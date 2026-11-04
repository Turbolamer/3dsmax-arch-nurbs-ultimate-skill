#!/usr/bin/env python3
"""Independent, offline Phase 16 spatial review; never writes repository fixtures.

Run from the repository root: python -B Audit/test_phase16_spatial_independent.py -v
One expected failure documents the direct API's inherent precision limitation;
it is NOT a passing requirement or evidence about the production parsers.
All CLI inputs and generated outputs are isolated under the approved temp root.
"""
from __future__ import annotations

import copy
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import wall_cell_coverage as coverage  # noqa: E402
import validate_specs as validator  # noqa: E402
import place_components as builder  # noqa: E402

INPUT_ROOTS = (ROOT / "examples", ROOT / "specs/fixtures/stepped-tower",
               ROOT / "specs/fixtures/form-precision")
SOURCES = (ROOT / "scripts/wall_cell_coverage.py", ROOT / "scripts/validate_specs.py",
           ROOT / "scripts/place_components.py", ROOT / "Audit/test_phase16_legacy_coverage.py",
           ROOT / "scripts/scene_units.py", ROOT / "scripts/curve_gen.py")
TEMP_PARENT = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"


def fingerprint(paths):
    files = (p for root in paths for p in ([root] if root.is_file() else root.rglob("*"))
             if p.is_file())
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def sample():
    """Independent exact 10 x 2 x 5 prism, opening x=2..4, z=1..3."""
    assembly = {"units": {"length": "cm"}, "opening_cuts": [
        {"id": "cut", "opening_id": "open", "host_ref": "host", "facade": "facade",
         "level_index": 0, "kind": "difference", "u_range_cm": [2, 4], "v_range_cm": [1, 3]}],
        "wall_cells": [
            {"id": "L", "host_ref": "host", "plan_rect_cm": [0, 0, 2, 2], "z_range_cm": [0, 5]},
            {"id": "S", "host_ref": "host", "plan_rect_cm": [2, 0, 4, 2], "z_range_cm": [0, 1]},
            {"id": "H", "host_ref": "host", "plan_rect_cm": [2, 0, 4, 2], "z_range_cm": [3, 5]},
            {"id": "R", "host_ref": "host", "plan_rect_cm": [4, 0, 10, 2], "z_range_cm": [0, 5]}]}
    massing = {"units": {"length": "cm"}, "elements": [
        {"id": "host", "kind": "facade_wall", "storey_index": 0,
         "profile_cm": [[0, 0], [10, 0], [10, 2], [0, 2]], "z_range_cm": [0, 5]}]}
    dims = {"units": {"length": "cm"}, "tolerances": {"linear_cm": 0.5},
            "facades": [{"id": "facade", "start_corner_cm": [0, 0], "end_corner_cm": [10, 0]}],
            "levels": [{"index": 0, "elevation_cm": 0, "height_cm": 5}],
            "openings": [{"id": "open", "facade": "facade", "level_index": 0,
                          "position_cm": 3, "width_cm": 2, "sill_cm": 1, "head_cm": 3}]}
    return assembly, massing, dims


def example():
    return tuple(json.loads((ROOT / "examples" / (n + ".json")).read_text(encoding="utf-8"))
                 for n in ("assembly", "massing", "dimensions"))


def volume(cell):
    x0, y0, x1, y1 = cell["plan_rect_cm"]
    z0, z1 = cell["z_range_cm"]
    return (x1 - x0) * (y1 - y0) * (z1 - z0)


def huge_sample():
    d = sample()
    s = 10**1600
    for p in d[1]["elements"][0]["profile_cm"]:
        p[0] *= s
        p[1] *= s
    d[1]["elements"][0]["z_range_cm"] = [0, 5*s]
    for c in d[0]["wall_cells"]:
        c["plan_rect_cm"] = [v*s for v in c["plan_rect_cm"]]
        c["z_range_cm"] = [v*s for v in c["z_range_cm"]]
    for k in ("start_corner_cm", "end_corner_cm"):
        d[2]["facades"][0][k] = [v*s for v in d[2]["facades"][0][k]]
    d[2]["levels"][0].update(elevation_cm=0, height_cm=5*s)
    d[2]["openings"][0].update(position_cm=3*s, width_cm=2*s, sill_cm=s, head_cm=3*s)
    d[0]["opening_cuts"][0].update(u_range_cm=[2*s, 4*s], v_range_cm=[s, 3*s])
    return d


def g82(docs, build=False):
    """G-82 through full run_checks; unrelated malformed synthetic metadata is not a PASS."""
    r = validator.Report()
    s = validator.load_session(validator.discover(ROOT / "examples"), ROOT / "examples", r)
    s.assembly.doc, s.massing.doc, s.dimensions.doc = docs
    s.build_gate = build
    validator.run_checks(s, r)
    return [(x.severity, x.detail) for x in r.findings if x.rule == "G-82"]


class IndependentSpatialReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = fingerprint(INPUT_ROOTS + SOURCES)

    @classmethod
    def tearDownClass(cls):
        after = fingerprint(INPUT_ROOTS + SOURCES)
        if after != cls.before:
            raise AssertionError("source or fixture drift: " + repr(sorted(
                p for p in cls.before.keys() | after.keys() if cls.before.get(p) != after.get(p))))

    def test_example_and_hand_calibrated_prism(self):
        for docs in (example(), sample()):
            before = copy.deepcopy(docs)
            result = coverage.check_wall_cell_coverage(*docs)
            self.assertEqual(result.status, "PASS", result.findings)
            self.assertTrue(result.ok)
            self.assertEqual(docs, before)
        for build in (False, True):
            self.assertEqual([v for v, _ in g82(example(), build)], ["PASS"])

    def test_missing_cell_entire_host_and_opening_bijection(self):
        for fault in ("cell", "all-host-cells", "host", "cuts-and-cells"):
            d = example()
            a, m, _ = d
            if fault == "cell":
                a["wall_cells"] = [c for c in a["wall_cells"] if c["id"] != "WAL-EL-014-C01"]
            if fault in ("all-host-cells", "cuts-and-cells"):
                a["wall_cells"] = [c for c in a["wall_cells"] if c["host_ref"] != "EL-014"]
            if fault == "host":
                m["elements"] = [e for e in m["elements"] if e["id"] != "EL-014"]
            if fault == "cuts-and-cells":
                a["opening_cuts"] = [c for c in a["opening_cuts"] if c["host_ref"] != "EL-014"]
            with self.subTest(fault=fault):
                result = coverage.check_wall_cell_coverage(*d)
                self.assertEqual(result.status, "FAIL", result.findings)
                for build in (False, True):
                    rows = g82(d, build)
                    self.assertIn("FAIL", [v for v, _ in rows], rows)
                    self.assertNotIn("PASS", [v for v, _ in rows], rows)

    def test_gap_and_overlap_preserve_volume_but_are_not_coverage(self):
        d = sample()
        before = sum(map(volume, d[0]["wall_cells"]))
        d[0]["wall_cells"].pop()
        for ident, a, b in (("extra1", 4, 8), ("extra2", 7, 9)):
            d[0]["wall_cells"].append({"id": ident, "host_ref": "host",
                "plan_rect_cm": [a, 0, b, 2], "z_range_cm": [0, 5]})
        self.assertEqual(sum(map(volume, d[0]["wall_cells"])), before)
        result = coverage.check_wall_cell_coverage(*d)
        self.assertEqual(result.status, "FAIL")
        self.assertEqual({x["code"]: x["volume_cm3"] for x in result.findings}, {"gap": 10, "overlap": 10})
        d = example()
        moved = next(c for c in d[0]["wall_cells"] if c["id"] == "WAL-EL-014-C04")
        old = volume(moved)
        moved["plan_rect_cm"][0] += 2
        moved["plan_rect_cm"][2] += 2
        self.assertEqual(volume(moved), old)
        rows = g82(d)
        self.assertEqual({v for v, _ in rows}, {"FAIL"}, rows)
        self.assertTrue(all(any("'code': '" + code + "'" in msg for _, msg in rows)
                            for code in ("gap", "overlap")), rows)

    def test_thresholds_and_builder_refusal(self):
        builder.verify_spatial_coverage(*sample())  # positive control
        for amount, expected in ((0.1, "REVIEW"), (0.5, "REVIEW"), (0.500001, "FAIL")):
            d = sample()
            d[0]["wall_cells"][0]["plan_rect_cm"][2] = 2 - amount
            with self.subTest(amount=amount):
                result = coverage.check_wall_cell_coverage(*d)
                self.assertEqual(result.status, expected, result.findings)
                self.assertFalse(result.ok)
                with self.assertRaises(builder.Refusal):
                    builder.verify_spatial_coverage(*d)
        d = example()
        c = next(c for c in d[0]["wall_cells"] if c["id"] == "WAL-EL-014-C01")
        c["plan_rect_cm"][2] = 134.9
        c["volume_cm3"] = volume(c)
        self.assertEqual([v for v, _ in g82(d)], ["WARN", "SKIP"])
        self.assertEqual([v for v, _ in g82(d, True)], ["FAIL"])

    def test_unsupported_no_openings_and_malformed_inputs(self):
        d = sample()
        d[0]["opening_cuts"] = []
        d[0]["wall_cells"] = []
        d[2]["openings"] = []
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "NOT_APPLICABLE")
        with self.assertRaisesRegex(builder.Refusal, "NOT_APPLICABLE"):
            builder.verify_spatial_coverage(*d)
        for fault in ("diagonal", "missing-units", "bool", "duplicate", "nan", "limit"):
            d = sample()
            kwargs = {}
            if fault == "diagonal": d[2]["facades"][0]["end_corner_cm"] = [10, 1]
            if fault == "missing-units": d[1].pop("units")
            if fault == "bool": d[0]["wall_cells"][0]["plan_rect_cm"][0] = True
            if fault == "duplicate": d[0]["wall_cells"].append(copy.deepcopy(d[0]["wall_cells"][0]))
            if fault == "nan": d[0]["wall_cells"][0]["plan_rect_cm"][0] = float("nan")
            if fault == "limit": kwargs = {"max_atoms": 1}
            with self.subTest(fault=fault):
                result = coverage.check_wall_cell_coverage(*d, **kwargs)
                self.assertEqual(result.status, "FAIL", result.findings)
                self.assertFalse(result.ok)
        # On a real complete assembly the unsupported cut-host profile is FAIL,
        # never an applicability SKIP or a combined PASS, in both modes.
        d = example()
        host = next(e for e in d[1]["elements"] if e["id"] == "EL-014")
        host["profile_cm"].insert(1, [900.0, 0.0])
        for build in (False, True):
            rows = g82(d, build)
            self.assertIn("FAIL", [v for v, _ in rows], rows)
            self.assertNotIn("PASS", [v for v, _ in rows], rows)

    def test_extreme_finite_float_is_json_safe(self):
        d = sample()
        d[0]["wall_cells"][-1]["plan_rect_cm"][2] = 1e308
        result = coverage.check_wall_cell_coverage(*d)
        self.assertEqual(result.status, "FAIL", result.findings)
        json.dumps(result.findings, allow_nan=False)
        self.assertTrue(any(isinstance(f.get("volume_cm3"), str) for f in result.findings))

    def test_huge_integer_consumers_fail_closed(self):
        d = huge_sample()
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "PASS")
        d[0]["wall_cells"].pop(0)
        with self.assertRaisesRegex(builder.Refusal, "coverage is FAIL"):
            builder.verify_spatial_coverage(*d)
        d[0]["status"] = "locked"
        d[0]["tolerances"] = {"linear_cm": 0.5}
        rows = g82(d)
        self.assertEqual([v for v, _ in rows], ["FAIL"], rows)
        self.assertNotIn("PASS", [v for v, _ in rows])

    def test_old_volume_shorter_plan_extent_is_not_hidden(self):
        d = sample()
        d[1]["elements"][0]["profile_cm"] = [[0, 0], [10, 0], [10, 20], [0, 20]]
        for cell in d[0]["wall_cells"]:
            cell["plan_rect_cm"][3] = 20
        d[0]["status"] = "locked"
        d[0]["tolerances"] = {"linear_cm": 0}
        d[2]["tolerances"]["linear_cm"] = 0
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "PASS")
        rows = g82(d)
        self.assertEqual([v for v, _ in rows], ["FAIL"], rows)
        self.assertIn("volume tolerance budget", rows[0][1])

    @unittest.expectedFailure
    def test_direct_api_cannot_recover_json_fraction_after_rounding(self):
        """Inherent API limitation: no oracle can recover a previously rounded float.

        The production parser must reject a lossy token before invoking G-82;
        passing decoded floats directly cannot preserve its original spelling.
        """
        d = sample()
        origin = 10**16
        for p in d[1]["elements"][0]["profile_cm"]: p[0] += origin
        for c in d[0]["wall_cells"]:
            c["plan_rect_cm"][0] += origin
            c["plan_rect_cm"][2] += origin
        for k in ("start_corner_cm", "end_corner_cm"):
            d[2]["facades"][0][k][0] += origin
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "PASS")
        d[0]["wall_cells"][0]["plan_rect_cm"][2] = "NUMERIC_TOKEN"
        raw = json.dumps(d).replace('"NUMERIC_TOKEN"', '10000000000000001.9')
        self.assertEqual(Decimal("10000000000000002") - Decimal("10000000000000001.9"), Decimal("0.1"))
        loaded = json.loads(raw)
        self.assertEqual(loaded[0]["wall_cells"][0]["plan_rect_cm"][2], origin + 2)
        # Control: an actually representable 1 cm gap is detected.
        control = copy.deepcopy(loaded)
        control[0]["wall_cells"][0]["plan_rect_cm"][2] = origin + 1
        self.assertEqual(coverage.check_wall_cell_coverage(*control).status, "FAIL")
        actual = coverage.check_wall_cell_coverage(*loaded)
        self.assertEqual(actual.status, "REVIEW")

    def test_huge_integer_diagnostic_returns_exact_structured_fail(self):
        """A giant discrepancy must remain classified and exactly representable."""
        d = huge_sample()
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "PASS")
        d[0]["wall_cells"].pop(0)
        result = coverage.check_wall_cell_coverage(*d)
        self.assertEqual(result.status, "FAIL", result.findings)
        finding = next(f for f in result.findings if f["code"] == "gap")
        self.assertEqual(finding["severity"], "ERROR")
        encoded = finding["volume_cm3"]
        self.assertTrue(encoded.startswith("exact_hex:"), encoded[:40])
        numerator, denominator = encoded.removeprefix("exact_hex:").split("/")
        self.assertEqual(Fraction(int(numerator, 16), int(denominator, 16)), 20 * 10**4800)
        json.dumps(result.findings, allow_nan=False)
        for kw in ({"max_atoms": 1}, {"max_work": 1}):
            limited = coverage.check_wall_cell_coverage(*d, **kw)
            self.assertEqual(limited.status, "FAIL")
            self.assertTrue(any("resource limit" in f["message"] for f in limited.findings))

    def test_huge_review_does_not_become_fail_or_pass(self):
        """Even an enormous but narrow discrepancy preserves REVIEW semantics."""
        d = huge_sample()
        # Scale the 1600-digit sample again, so its gap volume exceeds the
        # 4300-digit decimal conversion limit while the gap width is 1 cm.
        scale = 10**600
        for p in d[1]["elements"][0]["profile_cm"]:
            p[0] *= scale
            p[1] *= scale
        d[1]["elements"][0]["z_range_cm"] = [v*scale for v in d[1]["elements"][0]["z_range_cm"]]
        for c in d[0]["wall_cells"]:
            c["plan_rect_cm"] = [v*scale for v in c["plan_rect_cm"]]
            c["z_range_cm"] = [v*scale for v in c["z_range_cm"]]
        for k in ("start_corner_cm", "end_corner_cm"):
            d[2]["facades"][0][k] = [v*scale for v in d[2]["facades"][0][k]]
        d[2]["levels"][0]["height_cm"] *= scale
        op = d[2]["openings"][0]
        for k in ("position_cm", "width_cm", "sill_cm", "head_cm"): op[k] *= scale
        cut = d[0]["opening_cuts"][0]
        for k in ("u_range_cm", "v_range_cm"): cut[k] = [v*scale for v in cut[k]]
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "PASS")
        d[2]["tolerances"]["linear_cm"] = 1
        d[0]["wall_cells"][0]["plan_rect_cm"][2] -= 1
        result = coverage.check_wall_cell_coverage(*d)
        self.assertEqual(result.status, "REVIEW", result.findings)
        gap = next(f for f in result.findings if f["code"] == "gap")
        self.assertEqual((gap["severity"], gap["difference_cm"]), ("REVIEW", 1))
        n, de = gap["volume_cm3"].removeprefix("exact_hex:").split("/")
        self.assertEqual(Fraction(int(n, 16), int(de, 16)), 10 * 10**4400)
        self.assertFalse(result.ok)
        json.dumps(result.findings, allow_nan=False)

    def test_oversized_level_index_is_not_a_diagnostic_crash(self):
        """Direct callers can supply integer indices beyond the decimal print limit."""
        d = sample()
        index = 10**5000
        d[1]["elements"][0]["storey_index"] = index
        d[0]["opening_cuts"][0]["level_index"] = index
        d[2]["levels"][0]["index"] = index
        d[2]["openings"][0]["level_index"] = index
        self.assertEqual(coverage.check_wall_cell_coverage(*d).status, "PASS")
        mismatch = copy.deepcopy(d)
        mismatch[1]["elements"][0]["storey_index"] += 1
        result = coverage.check_wall_cell_coverage(*mismatch)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("differs from host storey", result.findings[0]["message"])
        duplicate = copy.deepcopy(d)
        duplicate[2]["levels"].append(copy.deepcopy(duplicate[2]["levels"][0]))
        result = coverage.check_wall_cell_coverage(*duplicate)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("duplicate index", result.findings[0]["message"])
        two_hosts = copy.deepcopy(d)
        cut = copy.deepcopy(two_hosts[0]["opening_cuts"][0])
        cut.update(id="cut2", opening_id="open2", host_ref="host2")
        two_hosts[0]["opening_cuts"].append(cut)
        result = coverage.check_wall_cell_coverage(*two_hosts)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("multiple cut hosts", result.findings[0]["message"])
        json.dumps(result.findings, allow_nan=False)


class OfflineCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = fingerprint(INPUT_ROOTS + SOURCES)

    @classmethod
    def tearDownClass(cls):
        after = fingerprint(INPUT_ROOTS + SOURCES)
        if after != cls.before:
            raise AssertionError("source or fixture drift: " + repr(sorted(
                p for p in cls.before.keys() | after.keys() if cls.before.get(p) != after.get(p))))

    def setUp(self):
        parent = str(TEMP_PARENT) if os.name == "nt" and TEMP_PARENT.is_dir() else None
        self.owner = tempfile.TemporaryDirectory(prefix="p16-independent-spatial-", dir=parent)
        self.addCleanup(self.owner.cleanup)
        self.tmp = Path(self.owner.name)
        self.project = self.tmp / "input"
        shutil.copytree(ROOT / "examples", self.project)

    def write_doc(self, name, doc):
        (self.project / (name + ".json")).write_text(json.dumps(doc, indent=2), encoding="utf-8")

    def command(self, *args):
        return subprocess.run([sys.executable, "-B", *map(str, args)], cwd=self.tmp,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))

    def lint(self, *flags):
        result = self.command(ROOT / "scripts/validate_specs.py", "--dir", self.project,
                              "--json", "--rule", "G-82", *flags)
        self.assertNotIn("Traceback", result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, report["exit_code"])
        return result, [(x["severity"], x["detail"]) for x in report["findings"] if x["rule"] == "G-82"]

    def test_actual_cli_positive_review_warnings_and_no_openings(self):
        for flags in ((), ("--build",)):
            result, rows = self.lint(*flags)
            self.assertEqual(result.returncode, 0)
            self.assertEqual([v for v, _ in rows], ["PASS"], rows)
        a, _, d = example()
        cell = next(c for c in a["wall_cells"] if c["id"] == "WAL-EL-014-C01")
        cell["plan_rect_cm"][2] = 134.9
        cell["volume_cm3"] = volume(cell)
        self.write_doc("assembly", a)
        for flags, expected in (((), ["WARN", "SKIP"]),
                                (("--warnings-as-errors",), ["FAIL", "SKIP"]),
                                (("--build",), ["FAIL"])):
            result, rows = self.lint(*flags)
            self.assertEqual([v for v, _ in rows], expected, rows)
            # The process status is global, even when --rule only displays G-82.
            if "FAIL" in expected:
                self.assertEqual(result.returncode, 1)
        a["opening_cuts"] = []
        a["wall_cells"] = []
        d["openings"] = []
        self.write_doc("assembly", a)
        self.write_doc("dimensions", d)
        for flags in ((), ("--build",)):
            result, rows = self.lint(*flags)
            self.assertIn("SKIP", [v for v, _ in rows], rows)
            self.assertNotIn("PASS", [v for v, _ in rows], rows)
            # Process exit is global, and other non-G-82 rules may independently fail.

    def test_missing_dependency_is_not_pass(self):
        (self.project / "massing.json").unlink()  # private copy only
        for flags in ((), ("--build",)):
            _, rows = self.lint(*flags)
            self.assertIn("SKIP", [v for v, _ in rows], rows)
            self.assertNotIn("PASS", [v for v, _ in rows], rows)

    def test_validator_cli_rejects_lossy_token_before_g82(self):
        """A lexical gap must be rejected before it can round away into a PASS."""
        result, rows = self.lint()
        self.assertEqual(result.returncode, 0)
        self.assertEqual([v for v, _ in rows], ["PASS"], rows)
        a, _, _ = example()
        target = next(c for c in a["wall_cells"] if c["id"] == "WAL-EL-014-C01")
        self.assertEqual(target["plan_rect_cm"][2], 135.0)
        target["plan_rect_cm"][2] = "NUMERIC_TOKEN"
        bad = "134.999999999999999"
        self.assertEqual(float(bad), 135.0)
        self.assertNotEqual(Decimal(bad), Decimal("135"))
        raw = json.dumps(a).replace('"NUMERIC_TOKEN"', bad)
        (self.project / "assembly.json").write_text(raw, encoding="utf-8")
        for flags in ((), ("--build",)):
            result = self.command(ROOT / "scripts/validate_specs.py", "--dir", self.project,
                                  "--json", "--rule", "G-82", *flags)
            self.assertNotIn("Traceback", result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual((result.returncode, report["exit_code"]), (1, 1))
            self.assertTrue(any(x["file"] == "assembly.json" and "precision" in x["error"]
                                for x in report["unreadable"]), report["unreadable"])
            rows = [x["severity"] for x in report["findings"] if x["rule"] == "G-82"]
            self.assertNotIn("PASS", rows)

    def test_builder_cli_rejects_lossy_token_before_output(self):
        """The same refusal applies at the legacy builder's input boundary."""
        for flags, label in (((), "lint-mode"), (("--build",), "build-mode")):
            out = self.tmp / label
            out.mkdir()
            positive = self.command(ROOT / "scripts/place_components.py", "--in", self.project,
                                    "--out", out, "--json", *flags)
            self.assertEqual(positive.returncode, 0, positive.stderr)
            # Existing valid outputs act as preservation sentinels; no byte can change.
            before = {p.name: p.read_bytes() for p in out.iterdir() if p.is_file()}
            dims = json.loads((ROOT / "examples/dimensions.json").read_text(encoding="utf-8"))
            old = dims["openings"][0]["position_cm"]
            bad = str(Decimal(str(old)) - Decimal("0.000000000000001"))
            self.assertEqual(float(bad), float(old))
            self.assertNotEqual(Decimal(bad), Decimal(str(old)))
            dims["openings"][0]["position_cm"] = "NUMERIC_TOKEN"
            raw = json.dumps(dims).replace('"NUMERIC_TOKEN"', bad)
            (self.project / "dimensions.json").write_text(raw, encoding="utf-8")
            result = self.command(ROOT / "scripts/place_components.py", "--in", self.project,
                                  "--out", out, "--json", *flags)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("precision", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual({p.name: p.read_bytes() for p in out.iterdir() if p.is_file()}, before)
            shutil.copyfile(ROOT / "examples/dimensions.json", self.project / "dimensions.json")

    def test_historical_builder_no_openings_and_unsupported_profile(self):
        old = self.tmp / "old"
        old.mkdir()
        for name in ("place_components.py", "scene_units.py"):
            try:
                got = subprocess.run(["git", "show", "6c0f27b:scripts/" + name],
                    cwd=Path(os.environ.get("PHASE16_HISTORY_ROOT", str(ROOT))),
                    capture_output=True, timeout=30, check=False)
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                self.skipTest("historical source unavailable: " + str(exc))
            if got.returncode:
                self.skipTest("historical source unavailable: " + got.stderr.decode(errors="replace"))
            (old / name).write_bytes(got.stdout)
        def build(script, label, flags=()):
            out = self.tmp / label
            out.mkdir()
            r = self.command(script, "--in", self.project, "--out", out, "--json", *flags)
            return r, out
        now = ROOT / "scripts/place_components.py"
        # Establish both builders actually run on the identical untouched input.
        old_ok, old_out = build(old / "place_components.py", "old-control")
        new_ok, new_out = build(now, "new-control")
        self.assertEqual((old_ok.returncode, new_ok.returncode), (0, 0), old_ok.stderr + new_ok.stderr)
        for name in ("assembly.json", "assembly.ms"):
            self.assertEqual((old_out / name).read_bytes(), (new_out / name).read_bytes())
        d = json.loads((self.project / "dimensions.json").read_text(encoding="utf-8"))
        d["openings"] = []
        self.write_doc("dimensions", d)
        for flags, label in (((), "normal"), (("--build",), "build")):
            prior, _ = build(old / "place_components.py", "old-no-" + label, flags)
            current, out = build(now, "new-no-" + label, flags)
            # Both hit the older G-9 empty-array provenance check before the new
            # oracle.  Do not mistake direct NOT_APPLICABLE refusal for a proven
            # new end-to-end compatibility regression.
            self.assertNotEqual(prior.returncode, 0, prior.stdout + prior.stderr)
            self.assertIn("G-9", prior.stderr)
            self.assertNotEqual(current.returncode, 0, current.stdout + current.stderr)
            self.assertIn("G-9", current.stderr)
            self.assertEqual(list(out.iterdir()), [])
        # A 0.0000004 cm opening edit is rounded by the legacy builder to six
        # decimals.  This reaches REVIEW only in the new independent gate.
        d = json.loads((ROOT / "examples/dimensions.json").read_text(encoding="utf-8"))
        d["openings"][0]["position_cm"] += 0.0000004
        self.write_doc("dimensions", d)
        for flags, label in (((), "normal"), (("--build",), "build")):
            prior, _ = build(old / "place_components.py", "old-rounding-" + label, flags)
            current, out = build(now, "new-rounding-" + label, flags)
            self.assertEqual(prior.returncode, 0, prior.stderr)
            self.assertNotEqual(current.returncode, 0, current.stdout + current.stderr)
            self.assertIn("REVIEW", current.stderr)
            self.assertEqual(list(out.iterdir()), [])
        # Restore input before the independent unsupported-profile comparison.
        shutil.copyfile(ROOT / "examples/dimensions.json", self.project / "dimensions.json")
        m = json.loads((self.project / "massing.json").read_text(encoding="utf-8"))
        host = next(e for e in m["elements"] if e["id"] == "EL-014")
        host["profile_cm"].insert(1, [900.0, 0.0])  # same rectangle, extra collinear vertex
        self.write_doc("massing", m)
        prior, _ = build(old / "place_components.py", "old-collinear")
        current, out = build(now, "new-collinear")
        self.assertEqual(prior.returncode, 0, prior.stderr)
        self.assertNotEqual(current.returncode, 0, current.stdout + current.stderr)
        self.assertIn("invalid_or_unsupported_geometry", current.stderr)
        self.assertEqual(list(out.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
