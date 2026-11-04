#!/usr/bin/env python3
"""Independent current controls for the 2026-11-02d scaffold/harness review.

Run: python -B Audit/test_phase16_scaffold_review_d.py -v
All writes are to newly owned directories under the approved OpenCode temp root.
No Max, installer, archive, user project or produced-poly artifact is involved.
Protective strict-import/staging tests supersede recorded pre-repair assertions.
Other boundary/observation tests pin limitations, not blanket safety approval.
Sources are frozen and source/fixture drift causes a test error, never a skip.
"""
from __future__ import annotations

import copy
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
SOURCE_NAMES = ("init_project.py", "validate_specs.py", "wall_cell_coverage.py", "curve_gen.py")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()} if root.exists() else {}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, doc):
    path.write_bytes((json.dumps(doc, indent=2, allow_nan=False) + "\n").encode("utf-8"))


class ScaffoldReviewD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        approved = Path(os.environ["LOCALAPPDATA"]) / "Temp" / "opencode"
        if not approved.is_dir():
            raise AssertionError(f"approved temporary parent is unavailable: {approved}")
        cls.owner = tempfile.TemporaryDirectory(prefix="p16-scaffold-d-", dir=approved)
        cls.addClassCleanup(cls.owner.cleanup)
        cls.root = Path(cls.owner.name)
        cls.scripts = cls.root / "scripts"
        cls.scripts.mkdir()
        paths = [ROOT / "scripts" / name for name in SOURCE_NAMES]
        paths += [p for p in (ROOT / "examples").rglob("*") if p.is_file()]
        paths += [ROOT / "specs/fixtures/poly-shell-input/walls.json"]
        cls.snapshot = {p: p.read_bytes() for p in paths}
        for name in SOURCE_NAMES:
            (cls.scripts / name).write_bytes(cls.snapshot[ROOT / "scripts" / name])
        spec = importlib.util.spec_from_file_location("scaffold_review_d_init", cls.scripts / "init_project.py")
        cls.init = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.init)
        spec = importlib.util.spec_from_file_location("scaffold_review_d_coverage", cls.scripts / "wall_cell_coverage.py")
        cls.coverage = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.coverage
        spec.loader.exec_module(cls.coverage)
        print("REVIEW_D_SOURCE_SHA256 " + json.dumps({name: digest(cls.snapshot[ROOT / "scripts" / name])
              for name in SOURCE_NAMES}), file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        drift = [p.relative_to(ROOT).as_posix() for p, data in cls.snapshot.items()
                 if not p.is_file() or p.read_bytes() != data]
        if drift:
            raise AssertionError("sources/fixtures changed; rerun on settled tree: " + repr(drift))

    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="case-", dir=self.root)
        self.addCleanup(self.owner.cleanup)
        self.temp = Path(self.owner.name)

    def cli(self, script, *args):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        env.pop("PYTHONPATH", None)
        return subprocess.run([sys.executable, "-B", str(self.scripts / script), *map(str, args)],
                              cwd=self.temp, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=90, check=False)

    def fresh(self, name="fresh"):
        result = self.cli("init_project.py", "--project", name, "--dir", self.temp)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.temp / name

    def input_seed(self):
        seed = self.temp / "seed"
        seed.mkdir()
        for source, data in self.snapshot.items():
            if source.is_relative_to(ROOT / "examples"):
                target = seed / source.relative_to(ROOT / "examples")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        (seed / "walls.json").write_bytes(self.snapshot[ROOT / "specs/fixtures/poly-shell-input/walls.json"])
        save(seed / "assembly.json", self.init.scaffold_assembly("pavilion-01"))
        return seed

    def validate(self, seed):
        result = self.cli("validate_specs.py", "--dir", seed, "--json")
        self.assertNotIn("Traceback", result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, report["exit_code"])
        self.assertFalse([f for f in report["findings"] if "internal error" in f["detail"].lower()])
        return result, report

    def test_parser_policy_difference_is_not_an_initializer_silent_acceptance(self):
        # The old safety suite wrongly demands global parser policy parity.
        # Grammar 3.2 permits validator float tokens beyond its integer-token cap.
        code = "import validate_specs as v; print(v.strict_json_loads('{\"n\":9007199254740992.0}')[\"n\"])"
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONPATH", None)
        checked = subprocess.run([sys.executable, "-B", "-c", code], cwd=self.scripts,
                                 env=env, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(float(checked.stdout), 9007199254740992.0)
        seed = self.input_seed()
        good = self.cli("init_project.py", "--project", "control", "--dir", self.temp, "--from", seed)
        self.assertEqual(good.returncode, 0, good.stderr)
        path = seed / "dimensions.json"
        doc = read_json(path)
        doc["synthetic_numeric_probe"] = "TOKEN"
        path.write_bytes((json.dumps(doc, indent=2).replace('"TOKEN"', "9007199254740992.0") + "\n").encode())
        result = self.cli("init_project.py", "--project", "refused", "--dir", self.temp, "--from", seed)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("exact integer safety range", result.stderr)
        self.assertFalse((self.temp / "refused").exists())

    def test_ten_opening_faults_pin_g93_dependency_and_g94_attribution(self):
        seed = self.input_seed()
        result, report = self.validate(seed)
        self.assertEqual(result.returncode, 0, report["summary"])
        for rule in ("G-93", "G-94", "G-97"):
            self.assertTrue(any(f["rule"] == rule and f["severity"] == "PASS" for f in report["findings"]))
        original = read_json(seed / "walls.json")
        cases = (
            ("unknown-run", 0, "wall_run_id", "RUN-099", {"G-93"}),
            ("unknown-kind", 0, "kind", "entrance", {"G-93"}),
            ("negative-u", 0, "u_range_cm", [-1, 315], {"G-93", "G-94"}),
            ("reversed-u", 0, "u_range_cm", [315, 135], {"G-93"}),
            ("zero-width", 0, "u_range_cm", [135, 135], {"G-93"}),
            ("past-end", 1, "u_range_cm", [575, 1801], {"G-94"}),
            ("negative-sill", 0, "sill_cm", -1, {"G-93", "G-94"}),
            ("head-at-sill", 0, "head_cm", 90, {"G-93"}),
            ("head-above-wall", 0, "head_cm", 421, {"G-94"}),
            ("overlap-u", 1, "u_range_cm", [300, 400], {"G-94"}),
        )
        for name, index, key, value, expected in cases:
            with self.subTest(name=name):
                doc = copy.deepcopy(original)
                doc["openings"][index][key] = value
                save(seed / "walls.json", doc)
                result, report = self.validate(seed)
                self.assertEqual(result.returncode, 1)
                relevant = [f for f in report["findings"] if f["rule"] in ("G-93", "G-94")]
                self.assertEqual({f["rule"] for f in relevant if f["severity"] == "FAIL"}, expected)
                self.assertTrue(all("walls.json::openings[" in f["location"] for f in relevant if f["severity"] == "FAIL"))
                if "G-94" not in expected:
                    self.assertTrue(any(f["rule"] == "G-94" and f["severity"] == "SKIP" for f in relevant))
                    self.assertFalse(any(f["rule"] == "G-94" and f["severity"] == "PASS" for f in relevant))

    def test_nonwall_force_boundary_is_not_edited_wall_protection(self):
        project = self.fresh()
        dims = project / "specs/pipeline/dimensions.json"
        authored = read_json(dims)
        authored["status"] = "locked"
        authored["source"]["reference"] = "SYNTHETIC AUTHORED NONWALL SENTINEL"
        save(dims, authored)
        before = tree(project)
        refused = self.cli("init_project.py", "--project", project.name, "--dir", self.temp)
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(tree(project), before)
        forced = self.cli("init_project.py", "--project", project.name, "--dir", self.temp, "--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertNotEqual(dims.read_bytes(), before["specs/pipeline/dimensions.json"])
        self.assertEqual(read_json(dims)["status"], "draft")
        # This observes the historical documented path-based --force behavior,
        # not authorization to overwrite real authored dimensions.

    def test_historical_invalid_seed_refused_before_creation_without_source_changes(self):
        seed = self.input_seed()
        (seed / "walls.json").unlink()
        (seed / "assembly.json").write_bytes(self.snapshot[ROOT / "examples/assembly.json"])
        control = self.cli("init_project.py", "--project", "legacy-control", "--dir", self.temp, "--from", seed)
        self.assertEqual(control.returncode, 0, control.stderr)
        good, report = self.validate(self.temp / "legacy-control/specs/pipeline")
        self.assertEqual(good.returncode, 0, report["summary"])
        path = seed / "dimensions.json"
        original = path.read_text(encoding="utf-8")
        for kind, anchor, replacement in (
            ("duplicate", '"project": "pavilion-01"', '"project": "other-source", "project": "pavilion-01"'),
            ("underflow", '"ground_level_cm": 0.0', '"ground_level_cm": 1e-400'),
        ):
            with self.subTest(kind=kind):
                self.assertEqual(original.count(anchor), 1)
                path.write_bytes(original.replace(anchor, replacement, 1).encode("utf-8"))
                invalid, invalid_report = self.validate(seed)
                self.assertEqual(invalid.returncode, 1)
                self.assertTrue(any(f["rule"] == "G-7" and f["severity"] == "FAIL"
                                    and f["location"] == "dimensions.json" for f in invalid_report["findings"]))
                before_seed = tree(seed)
                result = self.cli("init_project.py", "--project", "legacy-" + kind,
                                  "--dir", self.temp, "--from", seed)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                reason = "duplicate JSON" if kind == "duplicate" else "loses decimal precision"
                self.assertIn(reason, result.stderr)
                self.assertFalse((self.temp / ("legacy-" + kind)).exists())
                self.assertEqual(tree(seed), before_seed)
        # Invalid source bytes must remain visible for inspection, never get
        # restamped into output whose later lint hides the original ambiguity.

    def test_failed_descriptor_stage_preserves_old_file_after_earlier_commit(self):
        project = self.fresh()
        earlier = project / "specs/pipeline/dimensions.json"
        target = project / "specs/pipeline/assumptions.json"
        earlier.write_bytes(b"FIRST OLD RECORDED CONTENT\n")
        target.write_bytes(b"SECOND OLD RECORDED CONTENT\n")
        before = tree(project)
        real_fdopen = self.init.os.fdopen
        opened = []
        injected = []

        class PartialFailure:
            def __init__(self, stream):
                self.stream = stream
            def __enter__(self):
                self.stream.__enter__()
                return self
            def __exit__(self, *args):
                return self.stream.__exit__(*args)
            def write(self, content):
                self.stream.write(content[:19])
                self.stream.flush()
                injected.append(19)
                raise OSError(28, "injected descriptor partial-write failure", str(target))

        def fail_second(descriptor, *args, **kwargs):
            stream = real_fdopen(descriptor, *args, **kwargs)
            opened.append(descriptor)
            return PartialFailure(stream) if len(opened) == 2 else stream

        error = io.StringIO()
        with patch.object(self.init.os, "fdopen", fail_second), redirect_stdout(io.StringIO()), redirect_stderr(error):
            result = self.init.main(["--project", project.name, "--dir", str(self.temp), "--force"])
        self.assertEqual(result, 2)
        self.assertEqual(len(opened), 2)
        self.assertEqual(injected, [19], "the actual descriptor stage must reach the fault")
        self.assertEqual(target.read_bytes(), before["specs/pipeline/assumptions.json"])
        self.assertNotEqual(earlier.read_bytes(), before["specs/pipeline/dimensions.json"])
        self.assertEqual(read_json(earlier)["status"], "draft")
        after = tree(project)
        self.assertEqual({k: v for k, v in before.items() if k != "specs/pipeline/dimensions.json"},
                         {k: v for k, v in after.items() if k != "specs/pipeline/dimensions.json"})
        self.assertFalse(list(project.rglob("*.tmp")))
        self.assertIn("not committed", error.getvalue())
        self.assertIn("prior completed replacements", error.getvalue())
        self.assertIn("not a whole-project transaction", error.getvalue())
        self.assertIn("preserve and inspect", error.getvalue())

    def test_specific_hardlink_substitution_during_stage_is_refused(self):
        project = self.fresh()
        target = project / "specs/pipeline/dimensions.json"
        sentinel = self.temp / "hardlink-sentinel"
        sentinel.write_bytes(b"SEPARATE OWNED SENTINEL\n")
        before = tree(project)
        real_fsync = self.init.os.fsync
        injected = []

        def substitute(descriptor):
            real_fsync(descriptor)
            self.assertFalse(injected, "must stop at the first staged file")
            target.unlink()
            os.link(sentinel, target)
            injected.append(str(target))

        error = io.StringIO()
        with patch.object(self.init.os, "fsync", substitute), redirect_stdout(io.StringIO()), redirect_stderr(error):
            result = self.init.main(["--project", project.name, "--dir", str(self.temp), "--force"])
        self.assertEqual(result, 2)
        self.assertEqual(len(injected), 1)
        self.assertEqual(sentinel.read_bytes(), b"SEPARATE OWNED SENTINEL\n")
        self.assertEqual(target.read_bytes(), sentinel.read_bytes())
        after = tree(project)
        self.assertEqual({k: v for k, v in before.items() if k != "specs/pipeline/dimensions.json"},
                         {k: v for k, v in after.items() if k != "specs/pipeline/dimensions.json"})
        self.assertIn("not a safe regular output file", error.getvalue())
        self.assertFalse(list(project.rglob("*.tmp")))
        # The test itself replaced the target entry. Only the separate sentinel
        # and untouched entries are preservation evidence, not all-race safety.

    def test_pre_rounded_api_boundary_without_expectedfailure_mask(self):
        # A separate non-xfail control avoids treating an earlier assertion in
        # the existing expectedFailure test as proof of its intended last failure.
        origin = 10**16
        a = {"units": {"length": "cm"}, "opening_cuts": [
            {"id": "cut", "opening_id": "o", "host_ref": "h", "facade": "f", "level_index": 0,
             "kind": "difference", "u_range_cm": [2, 4], "v_range_cm": [1, 3]}], "wall_cells": []}
        for ident, lo, hi, z0, z1 in (("L", 0, 2, 0, 5), ("S", 2, 4, 0, 1),
                                     ("H", 2, 4, 3, 5), ("R", 4, 10, 0, 5)):
            a["wall_cells"].append({"id": ident, "host_ref": "h", "plan_rect_cm": [origin+lo, 0, origin+hi, 2],
                                    "z_range_cm": [z0, z1]})
        m = {"units": {"length": "cm"}, "elements": [{"id": "h", "kind": "facade_wall", "storey_index": 0,
             "profile_cm": [[origin, 0], [origin+10, 0], [origin+10, 2], [origin, 2]], "z_range_cm": [0, 5]}]}
        d = {"units": {"length": "cm"}, "tolerances": {"linear_cm": 0.5},
             "facades": [{"id": "f", "start_corner_cm": [origin, 0], "end_corner_cm": [origin+10, 0]}],
             "levels": [{"index": 0, "elevation_cm": 0, "height_cm": 5}],
             "openings": [{"id": "o", "facade": "f", "level_index": 0, "position_cm": 3,
                           "width_cm": 2, "sill_cm": 1, "head_cm": 3}]}
        self.assertEqual(self.coverage.check_wall_cell_coverage(a, m, d).status, "PASS")
        a["wall_cells"][0]["plan_rect_cm"][2] = "TOKEN"
        loaded = json.loads(json.dumps([a, m, d]).replace('"TOKEN"', "10000000000000001.9"))
        self.assertEqual(loaded[0]["wall_cells"][0]["plan_rect_cm"][2], origin + 2)
        self.assertEqual(self.coverage.check_wall_cell_coverage(*loaded).status, "PASS")
        loaded[0]["wall_cells"][0]["plan_rect_cm"][2] = origin + 1
        control = self.coverage.check_wall_cell_coverage(*loaded)
        self.assertEqual(control.status, "FAIL", control.findings)
        self.assertTrue(any(f["code"] == "gap" for f in control.findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
