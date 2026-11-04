#!/usr/bin/env python3
"""Owned-temp regression tests for the bounded Windows new-directory publisher.

Run: python -B Audit/test_phase16_p3_publication.py -v
No source fixture is rewritten. No Max/installer access. Deliberate substitutions
and failure injection occur only below the test's newly owned temp directory.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/wall_surface_publish.py"
FIXTURE = ROOT / "specs/fixtures/poly-shell-input/walls.json"
spec = importlib.util.spec_from_file_location("p3_publication_under_test", SOURCE)
assert spec is not None and spec.loader is not None
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)
PAIR = {"wall_surface.json": b'{"test_only":true}\n', "wall_surface.ms": b"-- test only\r\n"}


def source_hashes() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE, FIXTURE)}


class StreamFault:
    def __init__(self, stream, operation: str) -> None:
        self.stream, self.operation = stream, operation

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def fileno(self):
        return self.stream.fileno()

    def write(self, payload):
        if self.operation == "write":
            raise OSError("injected write error")
        if self.operation == "partial-write":
            self.stream.write(payload[:3])
            raise OSError("injected partial write error")
        if self.operation == "zero-write":
            return 0
        if self.operation == "short-write":
            return self.stream.write(payload[:3])
        return self.stream.write(payload)

    def flush(self):
        if self.operation == "flush":
            raise OSError("injected flush error")
        return self.stream.flush()

    def read(self, size):
        if self.operation == "read":
            raise OSError("injected read error")
        result = self.stream.read(size)
        if self.operation == "read-corrupt" and result:
            return bytes([result[0] ^ 1]) + result[1:]
        return result


class PlatformRefusal(unittest.TestCase):
    def test_non_windows_fails_before_filesystem_access(self) -> None:
        with patch.object(pub.sys, "platform", "linux"), patch.object(pub, "_output_path") as prepare:
            with self.assertRaisesRegex(pub.PublicationError, "Windows-only"):
                pub.publish_new_directory(Path("never-written"), PAIR)
            prepare.assert_not_called()


@unittest.skipUnless(os.name == "nt", "real Windows no-replace rename required; no POSIX emulation")
class PublicationWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.approved = Path(os.environ["LOCALAPPDATA"]) / "Temp/opencode"
        if not cls.approved.is_dir():
            raise RuntimeError(f"approved temp location is unavailable: {cls.approved}")
        cls.hashes_before = source_hashes()
        print("PUBLICATION_SOURCE " + repr(cls.hashes_before), file=sys.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        if source_hashes() != cls.hashes_before:
            raise AssertionError("source/fixture bytes changed during publication test run")
        print("PUBLICATION_SOURCE_AND_FIXTURE_UNCHANGED", file=sys.stderr)

    def setUp(self) -> None:
        owner = tempfile.TemporaryDirectory(prefix="p16-p3-publication-", dir=self.approved)
        self.addCleanup(owner.cleanup)  # Only this newly owned test tree, never source data.
        self.root = Path(owner.name)
        self.parent = self.root / "parent"
        self.parent.mkdir()
        self.sentinel = self.parent / "sentinel.bin"
        self.sentinel.write_bytes(b"USER BYTES\x00\xff\n")
        self.old_sentinel = self.sentinel.read_bytes()
        self.output = self.parent / "new-run"

    def assert_preserved(self) -> None:
        self.assertEqual(self.sentinel.read_bytes(), self.old_sentinel)

    def assert_clean_failure(self) -> None:
        self.assertFalse(os.path.lexists(self.output))
        self.assertEqual({p.name for p in self.parent.iterdir()}, {"sentinel.bin"})
        self.assert_preserved()

    def inject_stream(self, name: str, operation: str):
        original = pub._open_binary
        mode = "rb" if operation.startswith("read") else "xb"

        def injected(path, actual_mode):
            if path.name == name and actual_mode == mode:
                return StreamFault(original(path, actual_mode), operation)
            return original(path, actual_mode)

        return patch.object(pub, "_open_binary", side_effect=injected)

    def stages(self, parent: Path | None = None) -> list[Path]:
        return list((parent or self.parent).glob(".wall-surface-stage-*"))

    def make_link(self, path: Path, target: Path, *, directory: bool) -> None:
        try:
            path.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            self.skipTest(f"Windows symlink privilege unavailable: {exc}")

    def make_junction(self, path: Path, target: Path) -> None:
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(path), str(target)],
            capture_output=True, text=True, check=False,
        )
        if completed.returncode:
            self.skipTest(f"junction creation unavailable: {completed.stdout} {completed.stderr}")
        self.assertTrue(path.is_junction())

    def test_exact_pair_hashes_and_no_extra_files(self) -> None:
        hashes = pub.publish_new_directory(self.output, PAIR)
        self.assertEqual(hashes, {n: hashlib.sha256(b).hexdigest() for n, b in PAIR.items()})
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, PAIR)
        self.assertEqual(self.stages(), [])
        self.assert_preserved()

    def test_deterministic_bytes_separate_new_outputs_input_dict_unchanged(self) -> None:
        supplied = dict(reversed(list(PAIR.items())))
        first = pub.publish_new_directory(self.output, supplied)
        second_out = self.parent / "other-new-run"
        second = pub.publish_new_directory(second_out, supplied)
        self.assertEqual(first, second)
        self.assertEqual(supplied, PAIR)
        for name in PAIR:
            self.assertEqual((self.output / name).read_bytes(), (second_out / name).read_bytes())

    def test_replay_identical_directory_always_refuses_preserving_identity_bytes(self) -> None:
        pub.publish_new_directory(self.output, PAIR)
        before = {p.name: (p.stat().st_ino, p.read_bytes()) for p in self.output.iterdir()}
        with self.assertRaisesRegex(pub.PublicationError, "already exists"):
            pub.publish_new_directory(self.output, PAIR)
        self.assertEqual(before, {p.name: (p.stat().st_ino, p.read_bytes()) for p in self.output.iterdir()})
        self.assertEqual(self.stages(), [])

    def test_existing_empty_directory_refuses(self) -> None:
        self.output.mkdir()
        inode = self.output.stat().st_ino
        with self.assertRaisesRegex(pub.PublicationError, "already exists"):
            pub.publish_new_directory(self.output, PAIR)
        self.assertEqual(self.output.stat().st_ino, inode)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_existing_file_refuses_bytes_unchanged(self) -> None:
        self.output.write_bytes(b"existing output FILE")
        with self.assertRaisesRegex(pub.PublicationError, "already exists"):
            pub.publish_new_directory(self.output, PAIR)
        self.assertEqual(self.output.read_bytes(), b"existing output FILE")
        self.assert_preserved()

    def test_existing_symlink_and_broken_symlink_refuse(self) -> None:
        for target in (self.sentinel, self.parent / "absent-target"):
            with self.subTest(target=target):
                self.make_link(self.output, target, directory=False)
                original_target = self.output.readlink()
                original_identity = self.output.lstat().st_ino
                try:
                    with self.assertRaisesRegex(pub.PublicationError, "already exists"):
                        pub.publish_new_directory(self.output, PAIR)
                    self.assertTrue(self.output.is_symlink())
                    self.assertEqual(self.output.readlink(), original_target)
                    self.assertEqual(self.output.lstat().st_ino, original_identity)
                finally:
                    self.output.unlink()
        self.assert_preserved()

    def test_existing_junction_refuses_without_target_mutation(self) -> None:
        victim = self.root / "victim"
        victim.mkdir()
        (victim / "saved").write_bytes(b"junction victim")
        self.make_junction(self.output, victim)
        try:
            with self.assertRaisesRegex(pub.PublicationError, "already exists"):
                pub.publish_new_directory(self.output, PAIR)
            self.assertEqual((victim / "saved").read_bytes(), b"junction victim")
            self.assertEqual({p.name for p in victim.iterdir()}, {"saved"})
        finally:
            self.output.rmdir()  # Remove only the test-created junction itself.

    def test_symlink_ancestor_refuses_before_stage(self) -> None:
        alias = self.root / "alias"
        self.make_link(alias, self.parent, directory=True)
        try:
            with self.assertRaisesRegex(pub.PublicationError, "link/reparse"):
                pub.publish_new_directory(alias / "new-run", PAIR)
            self.assert_clean_failure()
        finally:
            alias.unlink()

    def test_junction_ancestor_refuses_before_stage(self) -> None:
        alias = self.root / "alias"
        self.make_junction(alias, self.parent)
        try:
            with self.assertRaisesRegex(pub.PublicationError, "link/reparse"):
                pub.publish_new_directory(alias / "new-run", PAIR)
            self.assert_clean_failure()
        finally:
            alias.rmdir()

    def test_missing_parent_is_not_created(self) -> None:
        with self.assertRaises(pub.PublicationError):
            pub.publish_new_directory(self.root / "missing-parent" / "new-run", PAIR)
        self.assertFalse((self.root / "missing-parent").exists())
        self.assert_clean_failure()

    def test_closed_names_exact_bytes_and_size_bound(self) -> None:
        invalid = [None, {}, {"wall_surface.json": b"a"}, {**PAIR, "extra": b"b"},
                   {"../wall_surface.json": b"a", "wall_surface.ms": b"b"},
                   {"wall_surface.json": "text", "wall_surface.ms": b"b"},
                   {"wall_surface.json": bytearray(b"a"), "wall_surface.ms": b"b"}]
        with patch.object(pub, "MAX_ARTIFACT_BYTES", 2):
            invalid.append({"wall_surface.json": b"123", "wall_surface.ms": b""})
            for payload in invalid:
                with self.subTest(payload=repr(payload)[:100]):
                    with self.assertRaises(pub.PublicationError):
                        pub.publish_new_directory(self.output, payload)
                    self.assert_clean_failure()

    def test_zero_length_is_valid_bytes_not_geometry_acceptance(self) -> None:
        pair = {name: b"" for name in PAIR}
        self.assertEqual(pub.publish_new_directory(self.output, pair),
                         {name: hashlib.sha256(b"").hexdigest() for name in pair})

    def test_size_bound_is_inclusive_before_any_stage(self) -> None:
        pair = {"wall_surface.json": b"12", "wall_surface.ms": b"1"}
        with patch.object(pub, "MAX_ARTIFACT_BYTES", 2):
            pub.publish_new_directory(self.output, pair)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, pair)

    def test_combined_pair_exact_two_mib_publishes(self) -> None:
        self.assertEqual(pub.MAX_PAIR_BYTES, 2 * 1024 * 1024)
        for index, sizes in enumerate(((1024 * 1024, 1024 * 1024), (2 * 1024 * 1024, 0))):
            with self.subTest(sizes=sizes):
                output = self.parent / f"boundary-run-{index}"
                pair = {"wall_surface.json": b"j" * sizes[0], "wall_surface.ms": b"m" * sizes[1]}
                result = pub.publish_new_directory(output, pair)
                self.assertEqual(result, {name: hashlib.sha256(data).hexdigest() for name, data in pair.items()})
                self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, pair)
        self.assertEqual(self.stages(), [])
        self.assert_preserved()

    def test_combined_pair_two_mib_plus_one_refuses_before_path_or_stage(self) -> None:
        pair = {"wall_surface.json": b"j" * (1024 * 1024), "wall_surface.ms": b"m" * (1024 * 1024 + 1)}
        self.assertEqual(sum(map(len, pair.values())), 2 * 1024 * 1024 + 1)
        self.assertTrue(all(len(payload) < pub.MAX_ARTIFACT_BYTES for payload in pair.values()))
        with patch.object(pub, "_output_path") as prepare, patch.object(pub.tempfile, "mkdtemp") as stage:
            with self.assertRaisesRegex(pub.PublicationError, "combined artifact pair.*2097152"):
                pub.publish_new_directory(self.output, pair)
            prepare.assert_not_called()
            stage.assert_not_called()
        self.assert_clean_failure()

    def test_combined_pair_independent_regression_two_individually_under_limit_refuses(self) -> None:
        pair = {"wall_surface.json": b"j" * 1_126_400, "wall_surface.ms": b"m" * 1_126_400}
        self.assertEqual(sum(map(len, pair.values())), 2_252_800)
        self.assertTrue(all(len(payload) < pub.MAX_PAIR_BYTES < pub.MAX_ARTIFACT_BYTES for payload in pair.values()))
        with patch.object(pub, "_output_path") as prepare, patch.object(pub.tempfile, "mkdtemp") as stage:
            with self.assertRaisesRegex(pub.PublicationError, "combined artifact pair.*2097152"):
                pub.publish_new_directory(self.output, pair)
            prepare.assert_not_called()
            stage.assert_not_called()
        self.assert_clean_failure()

    def test_stage_is_a_new_sibling_on_parent_volume_before_commit(self) -> None:
        original = pub._rename_no_replace
        def inspected(stage, output):
            self.assertEqual(stage.parent, output.parent)
            self.assertNotEqual(stage, output)
            self.assertEqual(stage.stat().st_dev, output.parent.stat().st_dev)
            self.assertFalse(os.path.lexists(output))
            self.assertEqual({p.name: p.read_bytes() for p in stage.iterdir()}, PAIR)
            return original(stage, output)
        with patch.object(pub, "_rename_no_replace", side_effect=inspected):
            pub.publish_new_directory(self.output, PAIR)
        self.assertEqual(self.stages(), [])

    def test_alias_path_components_and_traversal_refuse(self) -> None:
        invalid = [self.parent / ".." / "run", self.parent / "run.", self.parent / "run ",
                   self.parent / "CON", self.parent / "NUL.txt", self.parent / "COM1.foo",
                   self.parent / "bad:stream", Path("C:drive-relative"), Path("\\\\server\\share\\run"),
                   Path("\\\\?\\C:\\run"), Path(self.parent.anchor)]
        for path in invalid:
            with self.subTest(path=path):
                with self.assertRaises(pub.PublicationError):
                    pub.publish_new_directory(path, PAIR)
                self.assert_clean_failure()
        with self.assertRaisesRegex(pub.PublicationError, "pathlib.Path"):
            pub.publish_new_directory(str(self.output), PAIR)

    def test_stage_create_failure_preserves_sentinel(self) -> None:
        with patch.object(pub.tempfile, "mkdtemp", side_effect=OSError("injected mkdir error")):
            with self.assertRaisesRegex(pub.PublicationError, "mkdir error"):
                pub.publish_new_directory(self.output, PAIR)
        self.assert_clean_failure()

    def test_pair_open_errors_clean_owned_stage(self) -> None:
        original = pub._open_binary
        for name in PAIR:
            with self.subTest(name=name):
                def fail(path, mode):
                    if path.name == name and mode == "xb":
                        raise OSError("injected exclusive-open error")
                    return original(path, mode)
                with patch.object(pub, "_open_binary", side_effect=fail):
                    with self.assertRaisesRegex(pub.PublicationError, "exclusive-open"):
                        pub.publish_new_directory(self.output, PAIR)
                self.assert_clean_failure()

    def test_pair_write_partial_zero_and_flush_errors_clean_owned_stage(self) -> None:
        for name in PAIR:
            for operation in ("write", "partial-write", "zero-write", "flush"):
                with self.subTest(name=name, operation=operation):
                    with self.inject_stream(name, operation):
                        with self.assertRaises(pub.PublicationError):
                            pub.publish_new_directory(self.output, PAIR)
                    self.assert_clean_failure()

    def test_short_writes_are_completed_for_both_files(self) -> None:
        with self.inject_stream("wall_surface.json", "short-write"), self.inject_stream("wall_surface.ms", "short-write"):
            pub.publish_new_directory(self.output, PAIR)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, PAIR)

    def test_fsync_both_files_errors_clean_owned_stage(self) -> None:
        original = pub.os.fsync
        for failing_index in (1, 2):
            with self.subTest(failing_index=failing_index):
                count = 0
                def fail(fd):
                    nonlocal count
                    count += 1
                    if count == failing_index:
                        raise OSError("injected fsync error")
                    return original(fd)
                with patch.object(pub.os, "fsync", side_effect=fail):
                    with self.assertRaisesRegex(pub.PublicationError, "fsync error"):
                        pub.publish_new_directory(self.output, PAIR)
                self.assert_clean_failure()

    def test_pair_read_and_hash_errors_clean_owned_stage(self) -> None:
        for name in PAIR:
            for operation in ("read", "read-corrupt"):
                with self.subTest(name=name, operation=operation):
                    with self.inject_stream(name, operation):
                        with self.assertRaises(pub.PublicationError):
                            pub.publish_new_directory(self.output, PAIR)
                    self.assert_clean_failure()

    def test_truncated_readback_refuses_and_cleans_owned_stage(self) -> None:
        original = pub._verify_pair
        def truncated(stage, identity, owned, artifacts, hashes):
            (stage / "wall_surface.ms").write_bytes(b"x")
            return original(stage, identity, owned, artifacts, hashes)
        with patch.object(pub, "_verify_pair", side_effect=truncated):
            with self.assertRaisesRegex(pub.PublicationError, "length mismatch"):
                pub.publish_new_directory(self.output, PAIR)
        self.assert_clean_failure()

    def test_rename_error_cleans_pair_and_no_published_output(self) -> None:
        with patch.object(pub, "_rename_no_replace", side_effect=OSError("injected rename error")):
            with self.assertRaisesRegex(pub.PublicationError, "rename error"):
                pub.publish_new_directory(self.output, PAIR)
        self.assert_clean_failure()

    def test_real_windows_rename_late_file_and_empty_directory_collisions(self) -> None:
        original = pub._rename_no_replace
        for kind in ("file", "directory"):
            with self.subTest(kind=kind):
                def collide(stage, output):
                    if kind == "file":
                        output.write_bytes(b"late user file")
                    else:
                        output.mkdir()
                    return original(stage, output)
                with patch.object(pub, "_rename_no_replace", side_effect=collide):
                    with self.assertRaises(pub.PublicationError):
                        pub.publish_new_directory(self.output, PAIR)
                self.assertEqual(self.stages(), [])
                if kind == "file":
                    self.assertEqual(self.output.read_bytes(), b"late user file")
                    self.output.unlink()
                else:
                    self.assertEqual(list(self.output.iterdir()), [])
                    self.output.rmdir()
                self.assert_preserved()

    def test_real_windows_rename_late_symlink_collision(self) -> None:
        probe = self.root / "probe-link"
        self.make_link(probe, self.sentinel, directory=False)
        probe.unlink()
        original = pub._rename_no_replace
        original_target = None
        def collide(stage, output):
            nonlocal original_target
            output.symlink_to(self.sentinel)
            original_target = output.readlink()
            return original(stage, output)
        with patch.object(pub, "_rename_no_replace", side_effect=collide):
            with self.assertRaises(pub.PublicationError):
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual(self.output.readlink(), original_target)
        self.output.unlink()
        self.assert_clean_failure()

    def test_real_windows_rename_late_junction_collision(self) -> None:
        victim = self.root / "victim"
        victim.mkdir()
        (victim / "saved").write_bytes(b"late junction victim")
        original = pub._rename_no_replace
        def collide(stage, output):
            self.make_junction(output, victim)
            return original(stage, output)
        try:
            with patch.object(pub, "_rename_no_replace", side_effect=collide):
                with self.assertRaises(pub.PublicationError):
                    pub.publish_new_directory(self.output, PAIR)
            self.assertEqual((victim / "saved").read_bytes(), b"late junction victim")
            self.assertEqual(self.stages(), [])
        finally:
            if self.output.is_junction():
                self.output.rmdir()

    def test_parent_identity_substitution_before_stage_refuses_without_writing(self) -> None:
        original = pub._check_ancestors
        moved = self.root / "moved-parent"
        fired = False
        def substituted(ancestors):
            nonlocal fired
            if not fired:
                fired = True
                self.parent.rename(moved)
                self.parent.mkdir()
                (self.parent / "replacement").write_bytes(b"replacement parent")
            return original(ancestors)
        with patch.object(pub, "_check_ancestors", side_effect=substituted):
            with self.assertRaisesRegex(pub.PublicationError, "ancestor identity changed"):
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual((moved / "sentinel.bin").read_bytes(), self.old_sentinel)
        self.assertEqual({p.name for p in self.parent.iterdir()}, {"replacement"})
        self.assertEqual(self.stages(moved), [])

    def test_parent_identity_substitution_before_publish_preserves_stage_evidence(self) -> None:
        original = pub._verify_pair
        moved = self.root / "moved-parent"
        def substituted(*args):
            original(*args)
            self.parent.rename(moved)
            self.parent.mkdir()
            (self.parent / "replacement").write_bytes(b"replacement parent")
        with patch.object(pub, "_verify_pair", side_effect=substituted):
            with self.assertRaisesRegex(pub.PublicationError, "preserved staging evidence") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertIsNotNone(caught.exception.evidence_path)
        self.assertEqual({p.name for p in self.parent.iterdir()}, {"replacement"})
        stage = self.stages(moved)[0]
        self.assertEqual({p.name: p.read_bytes() for p in stage.iterdir()}, PAIR)
        self.assertEqual((moved / "sentinel.bin").read_bytes(), self.old_sentinel)

    def test_stage_substitution_before_publish_does_not_delete_replacement(self) -> None:
        original = pub._verify_pair
        kept = self.root / "moved-stage"
        def substituted(stage, *args):
            original(stage, *args)
            stage.rename(kept)
            stage.mkdir()
            (stage / "user-evidence").write_bytes(b"DO NOT DELETE")
        with patch.object(pub, "_verify_pair", side_effect=substituted):
            with self.assertRaisesRegex(pub.PublicationError, "staging directory identity changed") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual((caught.exception.evidence_path / "user-evidence").read_bytes(), b"DO NOT DELETE")
        self.assertEqual({p.name: p.read_bytes() for p in kept.iterdir()}, PAIR)
        self.assertFalse(self.output.exists())

    def test_unexpected_stage_entry_preserved_no_recursive_cleanup(self) -> None:
        original = pub._verify_pair
        def unexpected(stage, *args):
            (stage / "unowned").write_bytes(b"UNOWNED KEEP")
            return original(stage, *args)
        with patch.object(pub, "_verify_pair", side_effect=unexpected):
            with self.assertRaisesRegex(pub.PublicationError, "unowned/missing staging entry") as caught:
                pub.publish_new_directory(self.output, PAIR)
        stage = caught.exception.evidence_path
        self.assertEqual((stage / "unowned").read_bytes(), b"UNOWNED KEEP")
        for name, content in PAIR.items():
            self.assertEqual((stage / name).read_bytes(), content)
        self.assert_preserved()

    def test_exclusive_create_collision_preserves_unowned_stage_file(self) -> None:
        original = pub._write_artifact
        def collide(path, content, owned):
            if path.name == "wall_surface.ms":
                path.write_bytes(b"UNOWNED FILE")
            return original(path, content, owned)
        with patch.object(pub, "_write_artifact", side_effect=collide):
            with self.assertRaisesRegex(pub.PublicationError, "preserved staging evidence") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual((caught.exception.evidence_path / "wall_surface.ms").read_bytes(), b"UNOWNED FILE")
        self.assertEqual((caught.exception.evidence_path / "wall_surface.json").read_bytes(), PAIR["wall_surface.json"])

    def test_file_identity_substitution_preserved_on_cleanup(self) -> None:
        original = pub._verify_pair
        kept = self.root / "kept-file"
        def substituted(stage, *args):
            path = stage / "wall_surface.ms"
            path.rename(kept)
            path.write_bytes(b"SUBSTITUTED FILE")
            return original(stage, *args)
        with patch.object(pub, "_verify_pair", side_effect=substituted):
            with self.assertRaisesRegex(pub.PublicationError, "staged file substituted; refusing cleanup") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual((caught.exception.evidence_path / "wall_surface.ms").read_bytes(), b"SUBSTITUTED FILE")
        self.assertEqual(kept.read_bytes(), PAIR["wall_surface.ms"])

    def test_file_identity_substitution_after_readback_refuses_publication(self) -> None:
        original = pub._verify_pair
        kept = self.root / "kept-file"
        def substituted(stage, *args):
            original(stage, *args)
            path = stage / "wall_surface.ms"
            path.rename(kept)
            path.write_bytes(b"LATE SUBSTITUTED FILE")
        with patch.object(pub, "_verify_pair", side_effect=substituted):
            with self.assertRaisesRegex(pub.PublicationError, "identity changed before publication") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual((caught.exception.evidence_path / "wall_surface.ms").read_bytes(), b"LATE SUBSTITUTED FILE")
        self.assertEqual(kept.read_bytes(), PAIR["wall_surface.ms"])
        self.assertFalse(self.output.exists())

    def test_staged_hardlink_refuses_and_cleanup_does_not_delete_evidence(self) -> None:
        original = pub._verify_pair
        kept = self.root / "kept-hardlink"
        def hardlinked(stage, *args):
            os.link(stage / "wall_surface.ms", kept)
            return original(stage, *args)
        with patch.object(pub, "_verify_pair", side_effect=hardlinked):
            with self.assertRaisesRegex(pub.PublicationError, "exactly one hard link") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual((caught.exception.evidence_path / "wall_surface.ms").read_bytes(), PAIR["wall_surface.ms"])
        self.assertEqual(kept.read_bytes(), PAIR["wall_surface.ms"])
        self.assertFalse(self.output.exists())

    def test_parent_replaced_with_junction_before_publish_preserves_victim(self) -> None:
        victim = self.root / "victim"
        victim.mkdir()
        (victim / "saved").write_bytes(b"JUNCTION SUBSTITUTE VICTIM")
        moved = self.root / "moved-parent"
        original = pub._verify_pair
        def substituted(*args):
            original(*args)
            self.parent.rename(moved)
            self.make_junction(self.parent, victim)
        try:
            with patch.object(pub, "_verify_pair", side_effect=substituted):
                with self.assertRaisesRegex(pub.PublicationError, "link/reparse.*cleanup refused/failed") as caught:
                    pub.publish_new_directory(self.output, PAIR)
            self.assertIsNotNone(caught.exception.evidence_path)
            self.assertEqual({p.name for p in victim.iterdir()}, {"saved"})
            self.assertEqual((victim / "saved").read_bytes(), b"JUNCTION SUBSTITUTE VICTIM")
            self.assertEqual({p.name: p.read_bytes() for p in self.stages(moved)[0].iterdir()}, PAIR)
        finally:
            if self.parent.is_junction():
                self.parent.rmdir()

    def test_cleanup_unlink_failure_explicit_diagnostic_retains_evidence(self) -> None:
        original = Path.unlink
        def failed(path, *args, **kwargs):
            if path.name == "wall_surface.json":
                raise OSError("injected cleanup unlink error")
            return original(path, *args, **kwargs)
        with patch.object(pub, "_rename_no_replace", side_effect=OSError("injected rename error")), patch.object(Path, "unlink", failed):
            with self.assertRaisesRegex(pub.PublicationError, "cleanup unlink error.*preserved staging evidence") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertEqual({p.name: p.read_bytes() for p in caught.exception.evidence_path.iterdir()}, PAIR)
        self.assertFalse(self.output.exists())
        self.assert_preserved()

    def test_cleanup_rmdir_failure_explicit_diagnostic_retains_empty_stage(self) -> None:
        original = Path.rmdir
        def failed(path):
            if path.name.startswith(".wall-surface-stage-"):
                raise OSError("injected cleanup rmdir error")
            return original(path)
        with patch.object(pub, "_rename_no_replace", side_effect=OSError("injected rename error")), patch.object(Path, "rmdir", failed):
            with self.assertRaisesRegex(pub.PublicationError, "cleanup rmdir error.*preserved staging evidence") as caught:
                pub.publish_new_directory(self.output, PAIR)
        self.assertTrue(caught.exception.evidence_path.is_dir())
        self.assertEqual(list(caught.exception.evidence_path.iterdir()), [])
        self.assertFalse(self.output.exists())
        self.assert_preserved()

    def test_commit_is_not_followed_by_readback_or_cleanup(self) -> None:
        original = pub._rename_no_replace
        committed = False
        def commit(stage, output):
            nonlocal committed
            original(stage, output)
            committed = True
        with patch.object(pub, "_rename_no_replace", side_effect=commit), patch.object(pub, "_cleanup_stage") as cleanup:
            result = pub.publish_new_directory(self.output, PAIR)
        self.assertTrue(committed)
        self.assertEqual(set(result), set(PAIR))
        cleanup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
