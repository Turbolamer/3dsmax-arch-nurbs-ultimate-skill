#!/usr/bin/env python3
"""Calibrated strict-import and bounded staged-write regressions; offline only.

Run: python -B Audit/test_phase16_scaffold_repair_d.py -v
Freezes initializer bytes and hashes fixtures; writes only to owned OpenCode temp.
No Max, installer, archive, user project or manufactured produced poly output.
No skip/xfail suppression. Whole-project rollback and hostile concurrency are not
claimed by passing these per-file refusal and sequential-commit controls.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/init_project.py"
SEED_NAMES = ("dimensions.json", "assumptions.json", "conflicts_resolved.json", "massing.json",
              "nurbs.json", "facade_grids.json", "components_registry.json", "assembly.json")
FIXTURES = (ROOT / "examples", ROOT / "specs/fixtures/stepped-tower",
            ROOT / "specs/fixtures/form-precision/specs/pipeline")


def tree(root):
    if not root.exists():
        return {}
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


class ScaffoldRepairD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        approved = Path(os.environ["LOCALAPPDATA"]) / "Temp/opencode"
        if not approved.is_dir():
            raise AssertionError(f"approved temporary parent unavailable: {approved}")
        cls.owner = tempfile.TemporaryDirectory(prefix="phase16-scaffold-repair-d-", dir=approved)
        cls.addClassCleanup(cls.owner.cleanup)
        cls.root = Path(cls.owner.name)
        paths = [SOURCE, *(p for root in FIXTURES for p in root.rglob("*") if p.is_file())]
        cls.snapshot = {p: p.read_bytes() for p in paths}
        cls.script = cls.root / "init_project.py"
        cls.script.write_bytes(cls.snapshot[SOURCE])
        ast.parse(cls.snapshot[SOURCE].decode("utf-8"))
        spec = importlib.util.spec_from_file_location("scaffold_repair_d", cls.script)
        cls.init = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.init)
        print("FROZEN_INIT_SHA256 " + hashlib.sha256(cls.snapshot[SOURCE]).hexdigest(), file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        drift = [p.relative_to(ROOT).as_posix() for p, data in cls.snapshot.items()
                 if not p.is_file() or p.read_bytes() != data]
        if drift:
            raise AssertionError("source/fixture changed; rerun after edits stop: " + repr(drift))

    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="case-", dir=self.root)
        self.addCleanup(self.owner.cleanup)
        self.temp = Path(self.owner.name)
        self.counter = 0

    def seed(self, fixture=FIXTURES[0]):
        self.counter += 1
        target = self.temp / f"seed-{self.counter}"
        for source, data in self.snapshot.items():
            if source.is_relative_to(fixture):
                p = target / source.relative_to(fixture)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
        return target

    def cli(self, project, seed=None, *flags):
        args = [sys.executable, "-B", str(self.script), "--project", project, "--dir", str(self.temp)]
        if seed is not None:
            args += ["--from", str(seed)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        env.pop("PYTHONPATH", None)
        result = subprocess.run([*args, *flags], cwd=self.temp, env=env, capture_output=True,
                                text=True, encoding="utf-8", timeout=90, check=False)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def positive(self, seed, name):
        result = self.cli(name, seed)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("wall_technique", json.loads((self.temp / name / "specs/pipeline/assembly.json").read_bytes()))
        self.assertFalse((self.temp / name / "specs/pipeline/walls.json").exists())

    def refused(self, result, project, before, reason):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(reason, result.stderr)
        self.assertEqual(tree(project), before)

    @staticmethod
    def numeric_probe(path, token):
        doc = json.loads(path.read_bytes())
        doc["synthetic_numeric_probe"] = "TOKEN"
        path.write_bytes((json.dumps(doc, indent=2).replace('"TOKEN"', token) + "\n").encode())

    def test_every_historical_dependency_rejects_root_and_nested_duplicate_before_creation(self):
        for filename in SEED_NAMES:
            seed = self.seed()
            self.positive(seed, f"control-{self.counter}")
            path = seed / filename
            original = path.read_bytes()
            for nested in (False, True):
                with self.subTest(filename=filename, nested=nested):
                    raw = original.decode()
                    if nested:
                        raw = raw.rstrip()[:-1] + ', "synthetic_nested": {"value": 1, "value": 2}}\n'
                    else:
                        # Wrong first / correct last reproduces erased ambiguity.
                        value = json.loads(original)["project"]
                        anchor = json.dumps("project") + ": " + json.dumps(value)
                        self.assertEqual(raw.count(anchor), 1)
                        raw = raw.replace(anchor, '"project": "wrong-source", ' + anchor, 1)
                    path.write_bytes(raw.encode())
                    before_seed = tree(seed)
                    name = f"bad-{self.counter}-{int(nested)}"
                    result = self.cli(name, seed)
                    self.refused(result, self.temp / name, {}, "duplicate JSON")
                    self.assertFalse((self.temp / name).exists())
                    self.assertEqual(tree(seed), before_seed)

    def test_every_historical_dependency_rejects_underflow_and_lossy_number_before_creation(self):
        for filename in SEED_NAMES:
            seed = self.seed()
            self.positive(seed, f"control-{self.counter}")
            path = seed / filename
            original = path.read_bytes()
            self.numeric_probe(path, "0.1")
            self.positive(seed, f"numeric-control-{self.counter}")
            for index, token in enumerate(("1e-400", "134.999999999999999", "10000000000000001.9")):
                with self.subTest(filename=filename, token=token):
                    path.write_bytes(original)
                    self.numeric_probe(path, token)
                    before_seed = tree(seed)
                    name = f"bad-{self.counter}-{index}"
                    result = self.cli(name, seed)
                    self.refused(result, self.temp / name, {}, "loses decimal precision")
                    self.assertFalse((self.temp / name).exists())
                    self.assertEqual(tree(seed), before_seed)

    def test_original_ground_level_underflow_cannot_be_restamped_into_clean_zero(self):
        seed = self.seed()
        self.positive(seed, "control")
        path = seed / "dimensions.json"
        raw = path.read_text(encoding="utf-8")
        anchor = '"ground_level_cm": 0.0'
        self.assertEqual(raw.count(anchor), 1)
        path.write_bytes(raw.replace(anchor, '"ground_level_cm": 1e-400', 1).encode())
        before = tree(seed)
        result = self.cli("refused", seed)
        self.refused(result, self.temp / "refused", {}, "loses decimal precision")
        self.assertFalse((self.temp / "refused").exists())
        self.assertEqual(tree(seed), before)

    def test_historical_other_strict_numeric_and_syntax_refusals(self):
        seed = self.seed()
        self.positive(seed, "control")
        path = seed / "dimensions.json"
        original = path.read_bytes()
        samples = (("NaN", "non-finite"), ("Infinity", "non-finite"), ("1e999", "non-finite"),
                   ("9007199254740992", "safety range"), ("9007199254740992.0", "safety range"),
                   ("1e20", "safety range"), ("1" * 5000, "safety range"),
                   ("0." + "1" * 1025, "token length limit"))
        for index, (token, reason) in enumerate(samples):
            with self.subTest(token=token[:30]):
                path.write_bytes(original)
                self.numeric_probe(path, token)
                before = tree(seed)
                name = f"refused-{index}"
                self.refused(self.cli(name, seed), self.temp / name, {}, reason)
                self.assertFalse((self.temp / name).exists())
                self.assertEqual(tree(seed), before)

    def test_refused_import_with_force_preserves_existing_project_and_source(self):
        seed = self.seed()
        self.positive(seed, "protected")
        project = self.temp / "protected"
        (project / "user-notes.txt").write_bytes(b"KEEP USER NOTES\n")
        path = seed / "dimensions.json"
        original = path.read_bytes()
        for token in ("1e-400", "134.999999999999999"):
            with self.subTest(token=token):
                path.write_bytes(original)
                self.numeric_probe(path, token)
                before_seed, before_project = tree(seed), tree(project)
                self.refused(self.cli("protected", seed, "--force"), project, before_project, "loses decimal precision")
                self.assertEqual(tree(seed), before_seed)
        path.write_bytes(original.decode().replace('"project": ', '"project": "wrong", "project": ', 1).encode())
        before_seed, before_project = tree(seed), tree(project)
        self.refused(self.cli("protected", seed, "--force"), project, before_project, "duplicate JSON")
        self.assertEqual(tree(seed), before_seed)

    def test_deep_json_every_used_dependency_and_manifest_controlled_refusal(self):
        for filename in SEED_NAMES:
            with self.subTest(filename=filename):
                seed = self.seed()
                self.positive(seed, f"control-{self.counter}")
                path = seed / filename
                doc = json.loads(path.read_bytes())
                doc["synthetic_deep_probe"] = "TOKEN"
                raw = json.dumps(doc).replace('"TOKEN"', "[" * 160 + "0" + "]" * 160) + "\n"
                path.write_bytes(raw.encode())
                before_seed = tree(seed)
                name = f"deep-{self.counter}"
                self.refused(self.cli(name, seed), self.temp / name, {}, "JSON nesting exceeds")
                self.assertFalse((self.temp / name).exists())
                self.assertEqual(tree(seed), before_seed)
        seed = self.seed()
        self.positive(seed, "manifest")
        project = self.temp / "manifest"
        (project / "project.json").write_bytes(("[" * 160 + "0" + "]" * 160 + "\n").encode())
        before = tree(project)
        self.refused(self.cli("manifest", seed, "--force"), project, before, "refusing to overwrite")

    def test_nesting_limit_counts_containers_not_quoted_or_escaped_brackets(self):
        valid = "[" * 128 + "0" + "]" * 128
        self.init.parse_seed_json(valid)
        with self.assertRaisesRegex(ValueError, "nesting exceeds"):
            self.init.parse_seed_json("[" + valid + "]")
        with self.assertRaisesRegex(ValueError, "nesting exceeds"):
            self.init.parse_seed_json("[" * 4000 + "0" + "]" * 4000)
        with self.assertRaises(json.JSONDecodeError):
            self.init.parse_seed_json('{"shallow": [1,]}')
        quoted = {"brackets": '[{]}"' * 300, "escape": '\\"' * 100}
        self.assertEqual(self.init.parse_seed_json(json.dumps(quoted)), quoted)

    def test_valid_three_legacy_fixtures_keep_values_and_selector_absence(self):
        for index, fixture in enumerate(FIXTURES):
            with self.subTest(fixture=fixture):
                seed = self.seed(fixture)
                before = tree(seed)
                name = f"legacy-{index}"
                self.positive(seed, name)
                out = self.temp / name / "specs/pipeline"
                for filename in SEED_NAMES:
                    original = json.loads((seed / filename).read_bytes())
                    copied = json.loads((out / filename).read_bytes())
                    expected = dict(original, project=name, source=copied["source"])
                    self.assertEqual(copied, expected, filename)
                    self.assertEqual(copied["source"]["kind"], original["source"]["kind"])
                self.assertEqual(tree(seed), before)
                self.assertFalse(list(out.glob("*.tmp")))

    def test_valid_shortest_decimal_tokens_are_not_banned_in_historical_seeds(self):
        seed = self.seed()
        self.positive(seed, "control")
        path = seed / "dimensions.json"
        original = path.read_bytes()
        for index, token in enumerate(("0.1", "0.1000", "1e-3", "5e-324", "9007199254740991")):
            with self.subTest(token=token):
                path.write_bytes(original)
                self.numeric_probe(path, token)
                before = tree(seed)
                name = f"numeric-{index}"
                self.positive(seed, name)
                copied = json.loads((self.temp / name / "specs/pipeline/dimensions.json").read_bytes())
                self.assertEqual(copied["synthetic_numeric_probe"], json.loads(token))
                self.assertEqual(tree(seed), before)

    def test_fresh_net_area_declares_core_span_formula_dependency(self):
        result = self.cli("fresh")
        self.assertEqual(result.returncode, 0, result.stderr)
        dims = json.loads((self.temp / "fresh/specs/pipeline/dimensions.json").read_bytes())
        self.assertEqual(set(dims["origins"]["building.net_floor_area_m2"]["derives_from"]),
                         {"building.gross_floor_area_m2", "core.footprint_area_m2", "core.spans_level_indices"})
        expected = dims["building"]["gross_floor_area_m2"] - (
            dims["core"]["footprint_area_m2"] * len(dims["core"]["spans_level_indices"]))
        self.assertEqual(dims["building"]["net_floor_area_m2"], expected)

    def direct_target(self):
        path = self.temp / "output.json"
        path.write_bytes(b"PREEXISTING VALID OUTPUT - KEEP\n")
        return path

    def test_staged_success_and_failed_partial_stage_preserve_existing_bytes(self):
        path = self.direct_target()
        before = path.read_bytes()
        real_fdopen = self.init.os.fdopen

        class PartialFailure:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                self.stream.__enter__()
                return self
            def __exit__(self, *args):
                return self.stream.__exit__(*args)
            def write(self, content):
                self.stream.write(content[:9])
                self.stream.flush()
                raise OSError(28, "injected full disk after partial stage")

        def open_partial(*args, **kwargs):
            return PartialFailure(real_fdopen(*args, **kwargs))

        state = self.init.output_file_state(path)
        with patch.object(self.init.os, "fdopen", open_partial), self.assertRaisesRegex(OSError, "partial stage"):
            self.init.write_staged_file(path, '{"complete":true}\n', state)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(set(tree(self.temp)), {path.name})
        self.init.write_staged_file(path, '{"complete":true}\n', state)
        self.assertEqual(path.read_bytes(), b'{"complete":true}\n')
        self.assertEqual(set(tree(self.temp)), {path.name})

    def test_failed_fsync_and_replace_do_not_truncate_destination(self):
        path = self.direct_target()
        before = path.read_bytes()
        for name in ("fsync", "replace"):
            with self.subTest(failure=name):
                state = self.init.output_file_state(path)
                with patch.object(self.init.os, name, side_effect=OSError(5, "injected " + name)):
                    with self.assertRaisesRegex(OSError, "injected"):
                        self.init.write_staged_file(path, '{"new":1}\n', state)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(set(tree(self.temp)), {path.name})

    def test_late_hardlink_substitution_is_refused_without_following_sentinel(self):
        path = self.direct_target()
        state = self.init.output_file_state(path)
        victim = self.temp / "victim.txt"
        victim.write_bytes(b"SEPARATE OWNED SENTINEL\n")
        path.unlink()
        # Failure to create a hardlink is a real platform test failure, not SKIP.
        os.link(victim, path)
        before = victim.read_bytes()
        with self.assertRaisesRegex(ValueError, "safe regular output"):
            self.init.write_staged_file(path, '{"new":1}\n', state)
        self.assertEqual(victim.read_bytes(), before)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(self.temp.glob("*.tmp")))

    def test_substitution_while_staging_is_checked_before_commit(self):
        path = self.direct_target()
        state = self.init.output_file_state(path)
        victim = self.temp / "victim.txt"
        victim.write_bytes(b"SEPARATE OWNED SENTINEL\n")
        real_fsync = self.init.os.fsync

        def substitute(descriptor):
            real_fsync(descriptor)
            path.unlink()
            os.link(victim, path)

        with patch.object(self.init.os, "fsync", substitute):
            with self.assertRaisesRegex(ValueError, "safe regular output"):
                self.init.write_staged_file(path, '{"new":1}\n', state)
        self.assertEqual(victim.read_bytes(), b"SEPARATE OWNED SENTINEL\n")
        self.assertEqual(path.read_bytes(), victim.read_bytes())
        self.assertEqual(set(tree(self.temp)), {path.name, victim.name})

    def test_first_project_commit_failure_preserves_all_existing_project_bytes(self):
        made = self.cli("project")
        self.assertEqual(made.returncode, 0, made.stderr)
        project = self.temp / "project"
        (project / "user-notes.txt").write_bytes(b"KEEP USER DATA\n")
        before = tree(project)
        error = io.StringIO()
        with patch.object(self.init.os, "fsync", side_effect=OSError(28, "injected disk full")), \
                redirect_stdout(io.StringIO()), redirect_stderr(error):
            status = self.init.main(["--project", "project", "--dir", str(self.temp), "--force"])
        self.assertEqual(status, 2)
        self.assertEqual(tree(project), before)
        self.assertIn("not committed", error.getvalue())

    def test_sequential_project_commit_failure_preserves_failed_file_but_not_rollback(self):
        made = self.cli("project")
        self.assertEqual(made.returncode, 0, made.stderr)
        project = self.temp / "project"
        first = project / "specs/pipeline/dimensions.json"
        second = project / "specs/pipeline/assumptions.json"
        # Non-wall recorded edits remain explicitly overwritable with --force.
        first.write_bytes(b"FIRST OLD USER SENTINEL\n")
        second.write_bytes(b"SECOND OLD USER SENTINEL\n")
        before = tree(project)
        real_replace = self.init.os.replace

        def fail_second(source, target):
            if Path(target) == second:
                raise PermissionError(13, "injected second commit failure", str(target))
            return real_replace(source, target)

        error = io.StringIO()
        with patch.object(self.init.os, "replace", fail_second), redirect_stdout(io.StringIO()), redirect_stderr(error):
            status = self.init.main(["--project", "project", "--dir", str(self.temp), "--force"])
        self.assertEqual(status, 2)
        self.assertNotEqual(first.read_bytes(), before["specs/pipeline/dimensions.json"])
        self.assertEqual(second.read_bytes(), before["specs/pipeline/assumptions.json"])
        after = tree(project)
        self.assertEqual({k: v for k, v in before.items() if k != "specs/pipeline/dimensions.json"},
                         {k: v for k, v in after.items() if k != "specs/pipeline/dimensions.json"})
        self.assertIn("prior completed replacements", error.getvalue())
        self.assertIn("not a whole-project transaction", error.getvalue())
        self.assertIn("preserve and inspect", error.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
