"""Offline utility tests only. These cannot prove MAXScript API or Windows locks."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from pair_filein import (
    HERE,
    MAX_PAIR_BYTES,
    inspect_pair,
    ms_literal,
    ordinary_path,
    render_lock_probe,
    render_wrapper,
    require_hash,
    write_new_owned,
)


class OfflineUtilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="offline-test-", dir=HERE))
        self.manifest = self.root / "pair.json"
        self.script = self.root / "pair.ms"
        self.manifest.write_bytes(b'{"control":true}\n')
        self.script.write_bytes(b"2+2\n")
        self.mhash = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.shash = hashlib.sha256(self.script.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        # Every file was created in this exact new test directory. No recursion.
        for path in self.root.iterdir():
            path.unlink()
        self.root.rmdir()

    def test_valid_pair_read_only(self) -> None:
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}
        result = inspect_pair(self.manifest, self.script, self.mhash, self.shash)
        self.assertEqual(result, (self.manifest.resolve(), self.script.resolve()))
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.root.iterdir()})

    def test_exact_hash_grammar(self) -> None:
        self.assertEqual(require_hash(self.shash), self.shash)
        for invalid in ("", "0" * 63, "0" * 65, "A" * 64, "g" * 64, "0" * 64 + "\n"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                require_hash(invalid)

    def test_changed_script_refused(self) -> None:
        self.script.write_bytes(b"3+3\n")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            inspect_pair(self.manifest, self.script, self.mhash, self.shash)

    def test_changed_manifest_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "mismatch"):
            inspect_pair(self.manifest, self.script, "0" * 64, self.shash)

    def test_pair_limit_refuses(self) -> None:
        self.script.write_bytes(b"x" * MAX_PAIR_BYTES)
        shash = hashlib.sha256(self.script.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, "ceiling"):
            inspect_pair(self.manifest, self.script, self.mhash, shash)

    def test_same_file_refuses(self) -> None:
        with self.assertRaisesRegex(ValueError, "distinct"):
            inspect_pair(self.script, self.script, self.shash, self.shash)

    def test_output_is_exclusive_and_confined(self) -> None:
        target = self.root / "wrapper.ms"
        write_new_owned(target, "first")
        with self.assertRaises(FileExistsError):
            write_new_owned(target, "second")
        self.assertEqual(target.read_bytes(), b"first")
        with self.assertRaisesRegex(ValueError, "delegated"):
            write_new_owned(HERE.parent / "should-never-be-created.ms", "never")

    def test_namedpipe_and_ads_refuse(self) -> None:
        for path in (r"\\.\pipe\test", r"\\server\share\test.ms", "D:/example.ms:stream"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                ordinary_path(path, exists=False)

    def test_quote_escaping(self) -> None:
        self.assertEqual(ms_literal('a\\b"c'), '"a\\\\b\\"c"')
        with self.assertRaises(ValueError):
            ms_literal("a\nb")

    def test_wrapper_static_flow_not_runtime_proof(self) -> None:
        wrapper = render_wrapper(self.manifest, self.script, self.mhash, self.shash)
        open_line = 'dotNetObject "System.IO.FileStream"'
        self.assertEqual(wrapper.count(open_line), 2)
        self.assertEqual(wrapper.count("mode.Open access.Read sharing.Read"), 2)
        self.assertIn("hasher.ComputeHash stream", wrapper)
        self.assertIn("local actualManifest = p16Digest256 hasher manifestRead", wrapper)
        self.assertIn("local actualScript = p16Digest256 hasher scriptRead", wrapper)
        filein = wrapper.index("result = fileIn scriptPath quiet:true")
        self.assertLess(wrapper.index("actualScript != expectedScript"), filein)
        self.assertLess(wrapper.index("actualManifest != expectedManifest"), filein)
        self.assertGreater(wrapper.index("local scriptCleanup = p16CloseRead"), filein)
        self.assertGreater(wrapper.index("local manifestCleanup = p16CloseRead"), filein)
        self.assertIn("if failure != undefined do throw failure\n    result", wrapper)
        for forbidden in ("formattedPrint", "saveMaxFile", "resetMaxFile", "FileMode.Create", "deleteFile", "setNode"):
            self.assertNotIn(forbidden, wrapper)

    def test_negative_controls_static_only(self) -> None:
        malformed = render_wrapper(
            self.manifest, self.script, self.mhash, "not-a-sha256", _malformed_control=True
        )
        self.assertLess(malformed.index("P16 malformed script SHA-256"), malformed.index("manifestRead = dotNetObject"))
        mismatch = render_wrapper(self.manifest, self.script, self.mhash, "0" * 64)
        self.assertIn('local expectedScript = "' + "0" * 64 + '"', mismatch)
        lock = render_lock_probe(self.script)
        self.assertIn("mode.Open access.Write sharing.ReadWrite", lock)
        self.assertEqual(lock.count("mode.Open access.Write sharing.ReadWrite"), 2)
        self.assertIn("writeOpenCalibrated = writePositive.CanWrite", lock)
        self.assertIn("mode.Open access.Read sharing.None", lock)
        self.assertNotIn(".Write(", lock)
        self.assertNotIn(".SetLength", lock)

    def test_cli_generates_and_repeated_output_refuses(self) -> None:
        target = self.root / "wrapper.ms"
        command = [
            sys.executable, "-B", str(HERE / "pair_filein.py"),
            "--manifest", str(self.manifest), "--script", str(self.script),
            "--manifest-sha256", self.mhash, "--script-sha256", self.shash,
            "--out", str(target),
        ]
        first = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = target.read_bytes()
        second = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(target.read_bytes(), before)

    def test_cli_mismatch_writes_nothing(self) -> None:
        target = self.root / "not-produced.ms"
        result = subprocess.run(
            [sys.executable, "-B", str(HERE / "pair_filein.py"),
             "--manifest", str(self.manifest), "--script", str(self.script),
             "--manifest-sha256", self.mhash, "--script-sha256", "0" * 64,
             "--out", str(target)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("mismatch", result.stderr)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
