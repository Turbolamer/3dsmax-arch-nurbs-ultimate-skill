#!/usr/bin/env python3
"""Bounded output-commit regressions; no crash/hostile-race guarantee is tested.

Run: python -B Audit/test_phase16_builder_repair_d.py -v
All writes and injected errors operate on owned approved-temp copies. The
independent builder-review test remains read-only and supplies CLI/old-byte parity.
"""
from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
NAMES = ("place_components.py", "scene_units.py")


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest() for name in NAMES}


def tree(path: Path) -> dict[str, bytes]:
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}


class BuilderRepairD(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/opencode"
        if os.name == "nt" and not approved.is_dir():
            raise RuntimeError(f"approved temp directory unavailable: {approved}")
        cls.parent = str(approved) if os.name == "nt" else None
        owner = tempfile.TemporaryDirectory(prefix="p16-builder-repair-d-source-", dir=cls.parent)
        cls.addClassCleanup(owner.cleanup)
        cls.source = Path(owner.name)
        cls.source_hashes = hashes()
        for name in NAMES:
            (cls.source / name).write_bytes((ROOT / "scripts" / name).read_bytes())
        sys.path.insert(0, str(cls.source))
        cls.addClassCleanup(lambda: sys.path.remove(str(cls.source)))
        import place_components as builder
        cls.builder = builder
        print("REPAIR_D_SOURCE " + repr(cls.source_hashes), file=sys.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        if hashes() != cls.source_hashes:
            raise AssertionError("PRELIMINARY: production source drift during frozen run")

    def setUp(self) -> None:
        owner = tempfile.TemporaryDirectory(prefix="p16-builder-repair-d-case-", dir=self.parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.specs, self.out = self.temp / "input", self.temp / "output"
        self.specs.mkdir()
        self.out.mkdir()
        self.old = {"assembly.json": b"old JSON sentinel\n", "assembly.ms": b"old script sentinel\n"}
        for name, data in self.old.items():
            (self.out / name).write_bytes(data)

    def guard(self):
        return self.builder.OutputCommitGuard(self.specs, self.out, {})

    def write(self, guard=None) -> None:
        self.builder.write_output_pair(self.out, "new JSON\n", "new script\n", guard or self.guard())

    def test_positive_existing_and_missing_pair_noop_and_nested_new_output(self) -> None:
        self.write()
        expected = {"assembly.json": b"new JSON\n", "assembly.ms": b"new script\n"}
        self.assertEqual(tree(self.out), expected)
        info = {p: p.stat().st_ino for p in self.out.iterdir()}
        self.write()
        self.assertEqual(tree(self.out), expected)
        self.assertEqual({p: p.stat().st_ino for p in self.out.iterdir()}, info)
        self.out = self.temp / "new" / "nested" / "output"
        self.write()
        self.assertEqual(tree(self.out), expected)

    def test_parent_traversal_alias_is_intentionally_refused_before_any_write(self) -> None:
        b = self.builder
        # Same-directory canonical spelling is a positive control, not a broken
        # fixture that happens to refuse the lexical-alias case for another cause.
        self.specs = self.out
        self.write()
        for name, data in self.old.items():
            (self.out / name).write_bytes(data)
        alias = self.temp / "alias"
        alias.mkdir()
        lexical = alias / ".." / "output"
        self.assertTrue(os.path.samefile(self.out, lexical))
        for alias_input in (False, True):
            with self.subTest(alias_input=alias_input):
                specs = lexical if alias_input else self.out
                out = self.out if alias_input else lexical
                before = tree(self.out)
                original_mkstemp, original_replace = b.tempfile.mkstemp, b.os.replace
                with patch.object(b.tempfile, "mkstemp", wraps=original_mkstemp) as stage:
                    with patch.object(b.os, "replace", wraps=original_replace) as replace:
                        with self.assertRaises(b.Refusal) as caught:
                            guard = b.OutputCommitGuard(specs, out, {})
                            b.write_output_pair(out, "new JSON\n", "new script\n", guard)
                print(f"REPAIR_D_ALIAS alias_input={alias_input} staging={stage.call_count} "
                      f"replacements={replace.call_count}; {caught.exception}", file=sys.stderr)
                self.assertEqual(stage.call_count, 0, "alias refusal must precede staging")
                self.assertEqual(replace.call_count, 0, "alias refusal must precede output replacement")
                self.assertIn("parent traversal", str(caught.exception))
                self.assertEqual(tree(self.out), before)

    def test_both_replace_failures_are_controlled_and_restore_exact_existing_bytes(self) -> None:
        b = self.builder
        for fail_name in self.old:
            with self.subTest(fail_name=fail_name):
                original = b.os.replace
                def replace(src, dst):
                    if Path(dst).name == fail_name:
                        raise PermissionError("INJECTED recovered replace " + fail_name)
                    return original(src, dst)
                with patch.object(b.os, "replace", side_effect=replace):
                    with self.assertRaisesRegex(b.Refusal, "INJECTED recovered replace") as caught:
                        self.write()
                self.assertIn("restored to their prior bytes", str(caught.exception))
                self.assertEqual(tree(self.out), self.old)

    def test_second_replace_failure_removes_only_newly_created_first_entry(self) -> None:
        b = self.builder
        for path in self.out.iterdir():
            path.unlink()
        original = b.os.replace
        def replace(src, dst):
            if Path(dst).name == "assembly.ms":
                raise PermissionError("INJECTED missing-pair second replace")
            return original(src, dst)
        with patch.object(b.os, "replace", side_effect=replace):
            with self.assertRaisesRegex(b.Refusal, "missing-pair second replace"):
                self.write()
        self.assertEqual(tree(self.out), {})

    def test_second_staging_fsync_failure_changes_no_outputs_and_leaks_no_temps(self) -> None:
        b = self.builder
        original = b.os.fsync
        calls = 0
        def fsync(fd):
            nonlocal calls
            calls += 1
            if calls == 3:  # first payload + backup succeeded; second payload fails
                raise OSError("INJECTED second payload fsync")
            return original(fd)
        with patch.object(b.os, "fsync", side_effect=fsync):
            with self.assertRaisesRegex(b.Refusal, "second payload fsync"):
                self.write()
        self.assertEqual(calls, 3)
        self.assertEqual(tree(self.out), self.old)

    def test_first_staging_fsync_and_unlink_failure_names_retained_path_and_both_errors(self) -> None:
        b = self.builder
        original_unlink = Path.unlink
        unlink_calls = 0
        def unlink(path, *args, **kwargs):
            nonlocal unlink_calls
            if path.name.startswith(".assembly.json.tmp."):
                unlink_calls += 1
                if unlink_calls == 1:
                    raise PermissionError("INJECTED first staging unlink")
            return original_unlink(path, *args, **kwargs)
        with patch.object(b.os, "fsync", side_effect=OSError("INJECTED first staging fsync")):
            with patch.object(Path, "unlink", new=unlink):
                with self.assertRaises(b.Refusal) as caught:
                    self.write()
        print("REPAIR_D_STAGING_CLEANUP " + str(caught.exception), file=sys.stderr)
        remaining = tree(self.out)
        retained = [name for name in remaining if name.startswith(".assembly.json.tmp.")]
        self.assertEqual(len(retained), 1)
        self.assertEqual(unlink_calls, 1)
        self.assertIn("INJECTED first staging fsync", str(caught.exception))
        self.assertIn("INJECTED first staging unlink", str(caught.exception))
        self.assertIn("retained staging file " + str(self.out / retained[0]), str(caught.exception))
        self.assertEqual(remaining[retained[0]], b"new JSON\n")
        self.assertEqual({name: remaining[name] for name in self.old}, self.old)
        self.assertEqual(set(remaining), set(self.old) | set(retained))

    def test_route_replacement_after_guard_capture_refuses_before_writing(self) -> None:
        (self.out / "walls.json").write_bytes(b"legacy route\n")
        guard = self.guard()
        (self.out / "walls.json").write_bytes(b"poly route\n")
        before = tree(self.out)
        with self.assertRaisesRegex(self.builder.Refusal, "changed during the build"):
            self.write(guard)
        self.assertEqual(tree(self.out), before)

    def test_input_replacement_during_commit_rolls_back_installed_output(self) -> None:
        b = self.builder
        source = self.specs / "dimensions.json"
        source.write_bytes(b"verified input\n")
        guard = b.OutputCommitGuard(self.specs, self.out, {source: source.read_bytes()})
        original = b.os.replace
        def replace(src, dst):
            result = original(src, dst)
            if Path(dst).name == "assembly.json":
                source.write_bytes(b"changed input\n")
            return result
        with patch.object(b.os, "replace", side_effect=replace):
            with self.assertRaisesRegex(b.Refusal, "changed during the build"):
                self.write(guard)
        self.assertEqual(tree(self.out), self.old)
        self.assertEqual(source.read_bytes(), b"changed input\n")

    def test_parent_replacement_with_ordinary_directory_refuses(self) -> None:
        guard = self.guard()
        parked = self.temp / "parked"
        self.out.rename(parked)
        self.out.mkdir()
        (self.out / "victim").write_bytes(b"must survive\n")
        before = tree(self.out)
        with self.assertRaisesRegex(self.builder.Refusal, "commit directory.*changed"):
            self.write(guard)
        self.assertEqual(tree(self.out), before)
        self.assertEqual(tree(parked), self.old)

    def test_rollback_failure_is_not_falsely_reported_as_preservation(self) -> None:
        b = self.builder
        original = b.os.replace
        json_calls = 0
        def replace(src, dst):
            nonlocal json_calls
            name = Path(dst).name
            if name == "assembly.ms":
                raise PermissionError("INJECTED second replace")
            if name == "assembly.json":
                json_calls += 1
                if json_calls == 2:
                    raise PermissionError("INJECTED rollback failure")
            return original(src, dst)
        with patch.object(b.os, "replace", side_effect=replace):
            with self.assertRaisesRegex(b.Refusal, "ROLLBACK INCOMPLETE") as caught:
                self.write()
        self.assertNotIn("restored to their prior bytes", str(caught.exception))
        self.assertIn("INJECTED rollback failure", str(caught.exception))
        remaining = tree(self.out)
        backups = [p for p in remaining if p.startswith(".assembly.json.tmp.")]
        self.assertEqual(len(backups), 1)
        self.assertEqual(remaining[backups[0]], self.old["assembly.json"])
        self.assertIn(str(self.out / backups[0]), str(caught.exception))
        self.assertEqual(remaining["assembly.json"], b"new JSON\n")
        self.assertEqual(remaining["assembly.ms"], self.old["assembly.ms"])

    def test_parent_swap_after_first_replace_does_not_redirect_rollback_or_cleanup(self) -> None:
        b = self.builder
        victim, parked = self.temp / "victim", self.temp / "parked"
        victim.mkdir()
        (victim / "assembly.json").write_bytes(b"victim JSON\n")
        (victim / "assembly.ms").write_bytes(b"victim script\n")
        before = tree(victim)
        probe = self.temp / "symlink-control"
        try:
            probe.symlink_to(victim, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        self.assertEqual((probe / "assembly.json").read_bytes(), before["assembly.json"])
        probe.unlink()
        original = b.os.replace
        calls = 0
        def replace(src, dst):
            nonlocal calls
            result = original(src, dst)
            calls += 1
            if calls == 1:
                self.out.rename(parked)
                self.out.symlink_to(victim, target_is_directory=True)
            return result
        stderr = io.StringIO()
        with patch.object(b.os, "replace", side_effect=replace):
            with redirect_stderr(stderr):
                with self.assertRaisesRegex(b.Refusal, "ROLLBACK INCOMPLETE") as caught:
                    self.write()
        self.assertEqual(calls, 1)
        self.assertNotIn("restored to their prior bytes", str(caught.exception))
        self.assertIn("private output staging cleanup incomplete", stderr.getvalue())
        self.assertEqual(tree(victim), before)
        recovery = tree(parked)
        self.assertEqual(recovery["assembly.json"], b"new JSON\n")
        self.assertEqual(recovery["assembly.ms"], self.old["assembly.ms"])
        self.assertTrue(any(name.startswith(".assembly.json.tmp.") and data == self.old["assembly.json"]
                            for name, data in recovery.items()))

    def test_raw_oserror_at_main_boundary_is_controlled(self) -> None:
        b = self.builder
        stderr = io.StringIO()
        with patch.object(b, "require_legacy_wall_route", side_effect=PermissionError("INJECTED early I/O")):
            with redirect_stderr(stderr):
                code = b.main(["--in", str(self.specs), "--out", str(self.out)])
        self.assertEqual(code, b.EXIT_REFUSAL)
        self.assertIn("INJECTED early I/O", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
        self.assertEqual(tree(self.out), self.old)

    def test_historical_duplicate_inputs_refuse_all_modes_and_preserve_sentinels(self) -> None:
        project = self.temp / "legacy" / "pipeline"
        shutil.copytree(ROOT / "examples", project)
        self.assertFalse((project / "walls.json").exists())
        # The new independent oracle imports are needed for the successful
        # calibration; duplicate cases must fail in the actual read_spec caller.
        for name in ("wall_cell_coverage.py", "curve_gen.py"):
            (self.source / name).write_bytes((ROOT / "scripts" / name).read_bytes())
        control = self.temp / "legacy-control"
        argv = [sys.executable, "-B", str(self.source / "place_components.py"),
                "--in", str(project), "--out", str(control), "--json"]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        good = subprocess.run(argv, cwd=self.temp, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=120, check=False)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(set(tree(control)), {"assembly.json", "assembly.ms"})
        # A valid JSON route sentinel is required so rejection is not masked by
        # the existing-output route gate before read_spec reaches the mutation.
        (self.out / "assembly.json").write_bytes((project / "assembly.json").read_bytes())
        before = tree(self.out)
        for name, token in (("dimensions.json", '"width_cm":'),
                            ("massing.json", '"height_cm":'),
                            ("components_registry.json", '"joint_width_cm":')):
            path = project / name
            original = path.read_bytes()
            text = original.decode("utf-8")
            self.assertIn(token, text)
            # Identical duplicate values still have ambiguous object keys and
            # must not be treated as a harmless last-value-wins case.
            start = text.index(token) + len(token)
            end = start
            while end < len(text) and text[end] not in ",}\n":
                end += 1
            value = text[start:end]
            mutated = text[:start] + value + ", " + token + value + text[end:]
            path.write_bytes(mutated.encode("utf-8"))
            try:
                for flags in ([], ["--allow-draft"], ["--build"], ["--build", "--allow-draft"]):
                    with self.subTest(name=name, flags=flags):
                        command = argv[:]
                        command[command.index(str(control))] = str(self.out)
                        result = subprocess.run([*command, *flags], cwd=self.temp, env=env,
                                                capture_output=True, text=True, encoding="utf-8",
                                                timeout=120, check=False)
                        self.assertEqual(result.returncode, self.builder.EXIT_REFUSAL, result.stderr)
                        self.assertIn("duplicate JSON object key", result.stderr)
                        self.assertIn(name, result.stderr)
                        self.assertNotIn("Traceback", result.stderr)
                        self.assertEqual(tree(self.out), before)
                        self.assertEqual(path.read_bytes(), mutated.encode("utf-8"))
            finally:
                path.write_bytes(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
