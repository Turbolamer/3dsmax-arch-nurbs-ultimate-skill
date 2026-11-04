"""Offline controls for the independent legacy wall coverage oracle.

Run: python -B Audit/test_phase16_legacy_coverage.py -v
Fixtures are only read; all fault injections use in-memory copies.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from wall_cell_coverage import check_wall_cell_coverage  # noqa: E402
import validate_specs as validator  # noqa: E402


FIXTURES = {
    "examples": ROOT / "examples",
    "stepped-tower": ROOT / "specs" / "fixtures" / "stepped-tower",
    "form-precision": ROOT / "specs" / "fixtures" / "form-precision" / "specs" / "pipeline",
}


def load_fixture(path: Path) -> tuple[dict, dict, dict]:
    return tuple(json.loads((path / (name + ".json")).read_text(encoding="utf-8"))
                 for name in ("assembly", "massing", "dimensions"))


def synthetic(axis: str = "x", reverse: bool = False, elevation: float = 100.0) -> tuple[dict, dict, dict]:
    """Hand-specified prism: run 0..10, thickness 2, height 5, 2x2 opening.

    The world-space cell coordinates are independent of the production builder.
    The misleading names are intentional; only actual endpoints define direction.
    """
    if axis == "x":
        start, end = ([0, 0], [10, 0]) if not reverse else ([10, 0], [0, 0])
        profile = [[0, 0], [10, 0], [10, 2], [0, 2]]
    else:
        start, end = ([0, 0], [0, 10]) if not reverse else ([0, 10], [0, 0])
        profile = [[0, 0], [2, 0], [2, 10], [0, 10]]
    hole_lo, hole_hi = ((2, 4) if not reverse else (6, 8))

    def rect(a: float, b: float) -> list[float]:
        return [a, 0, b, 2] if axis == "x" else [0, a, 2, b]

    def cell(ident: str, a: float, b: float, lo: float, hi: float) -> dict:
        return {"id": ident, "host_ref": "opaque-host", "plan_rect_cm": rect(a, b),
                "z_range_cm": [elevation + lo, elevation + hi], "volume_cm3": -123456789}

    cells = [cell("left", 0, hole_lo, 0, 5),
             cell("sill", hole_lo, hole_hi, 0, 1),
             cell("head", hole_lo, hole_hi, 3, 5),
             cell("right", hole_hi, 10, 0, 5)]
    assembly = {"units": {"length": "cm"},
                "opening_cuts": [{"id": "cut", "opening_id": "opening", "host_ref": "opaque-host",
                                  "facade": "misleading-name", "level_index": 7,
                                  "u_range_cm": [2, 4], "v_range_cm": [1, 3], "kind": "difference"}],
                "wall_cells": cells}
    massing = {"units": {"length": "cm"},
               "elements": [{"id": "opaque-host", "kind": "facade_wall", "storey_index": 7,
                              "profile_cm": profile, "z_range_cm": [elevation, elevation + 5]}]}
    dimensions = {"units": {"length": "cm"}, "tolerances": {"linear_cm": 0.5},
                  "facades": [{"id": "misleading-name", "name": "not a compass direction",
                               "direction_deg": 999, "start_corner_cm": start, "end_corner_cm": end,
                               "spans_level_indices": [7]}],
                  "levels": [{"index": 7, "elevation_cm": elevation, "height_cm": 5}],
                  "openings": [{"id": "opening", "facade": "misleading-name", "level_index": 7,
                                "position_cm": 3, "width_cm": 2, "sill_cm": 1, "head_cm": 3}]}
    return assembly, massing, dimensions


def geometric_volume(cell: dict) -> float:
    x0, y0, x1, y1 = cell["plan_rect_cm"]
    z0, z1 = cell["z_range_cm"]
    return (x1 - x0) * (y1 - y0) * (z1 - z0)


def fixture_file_hashes() -> dict[str, str]:
    """Snapshot every source fixture file, including CSV, MS, and QA evidence."""
    roots = (FIXTURES["examples"], FIXTURES["stepped-tower"],
             ROOT / "specs" / "fixtures" / "form-precision")
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for root in roots for path in sorted(root.rglob("*")) if path.is_file()}


def validator_session(path: Path, *, build: bool = False):
    """Load real fixtures through the public validator; callers mutate only .doc."""
    report = validator.Report()
    session = validator.load_session(validator.discover(path), path, report)
    session.build_gate = build
    return session, report


def g82_rows(session, report):
    validator.run_checks(session, report)
    return [finding for finding in report.findings if finding.rule == "G-82"]


class LegacyCoverageTests(unittest.TestCase):
    def assert_code(self, result, code: str) -> dict:
        matches = [finding for finding in result.findings if finding["code"] == code]
        self.assertTrue(matches, (code, result))
        return matches[0]

    def test_three_baselines_pass_without_mutation(self):
        for name, path in FIXTURES.items():
            with self.subTest(name=name):
                docs = load_fixture(path)
                originals = copy.deepcopy(docs)
                result = check_wall_cell_coverage(*docs)
                self.assertEqual(result.status, "PASS", result.findings)
                self.assertTrue(result.ok)
                self.assertEqual(len(result.checked_hosts), {"examples": 8, "stepped-tower": 7,
                                                              "form-precision": 8}[name])
                self.assertEqual(docs, originals)

    def test_deleted_named_cell_is_fail_even_inside_old_volume_budget(self):
        assembly, massing, dimensions = load_fixture(FIXTURES["examples"])
        victim = next(c for c in assembly["wall_cells"] if c["id"] == "WAL-EL-014-C01")
        self.assertEqual(geometric_volume(victim), 1_134_000)
        assembly["wall_cells"].remove(victim)
        result = check_wall_cell_coverage(assembly, massing, dimensions)
        self.assertEqual(result.status, "FAIL")
        gap = self.assert_code(result, "gap")
        self.assertEqual(gap["host_ref"], "EL-014")
        self.assertEqual(gap["volume_cm3"], 1_134_000)

    def test_empty_host_cells_and_missing_host_both_fail(self):
        for fault in ("cells", "host", "both", "all_cells"):
            with self.subTest(fault=fault):
                assembly, massing, dimensions = load_fixture(FIXTURES["examples"])
                if fault in ("cells", "both"):
                    assembly["wall_cells"] = [c for c in assembly["wall_cells"] if c["host_ref"] != "EL-014"]
                if fault == "all_cells":
                    assembly["wall_cells"] = []
                if fault in ("host", "both"):
                    massing["elements"] = [e for e in massing["elements"] if e["id"] != "EL-014"]
                result = check_wall_cell_coverage(assembly, massing, dimensions)
                self.assertEqual(result.status, "FAIL", result.findings)
                self.assertTrue(any(f.get("host_ref") == "EL-014" and f["severity"] == "ERROR" for f in result.findings))

    def test_deleted_cut_and_host_cells_do_not_hide_openings(self):
        assembly, massing, dimensions = load_fixture(FIXTURES["examples"])
        assembly["opening_cuts"] = [c for c in assembly["opening_cuts"] if c["host_ref"] != "EL-014"]
        assembly["wall_cells"] = [c for c in assembly["wall_cells"] if c["host_ref"] != "EL-014"]
        result = check_wall_cell_coverage(assembly, massing, dimensions)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("missing cuts", self.assert_code(result, "invalid_input")["message"])

    def test_gap_and_overlap_with_exactly_balanced_volumes(self):
        docs = synthetic()
        assembly = docs[0]
        old = sum(map(geometric_volume, assembly["wall_cells"]))
        assembly["wall_cells"].pop()
        common = {"host_ref": "opaque-host", "z_range_cm": [100, 105], "volume_cm3": 0}
        assembly["wall_cells"].extend([
            {**common, "id": "extra-1", "plan_rect_cm": [4, 0, 8, 2]},
            {**common, "id": "extra-2", "plan_rect_cm": [7, 0, 9, 2]},
        ])
        self.assertEqual(sum(map(geometric_volume, assembly["wall_cells"])), old)
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL", result.findings)
        self.assertEqual(self.assert_code(result, "gap")["volume_cm3"], 10)
        self.assertEqual(self.assert_code(result, "overlap")["volume_cm3"], 10)

    def test_opening_filled_and_partial_thickness_are_detected_in_3d(self):
        docs = synthetic()
        docs[0]["wall_cells"].append({"id": "plug", "host_ref": "opaque-host",
                                       "plan_rect_cm": [2, 0, 4, 2],
                                       "z_range_cm": [101, 103], "volume_cm3": 0})
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(self.assert_code(result, "opening_filled")["cell_ids"], ["plug"])
        docs = synthetic()
        docs[0]["wall_cells"][-1]["plan_rect_cm"][3] = 1
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL")
        gap = self.assert_code(result, "gap")
        self.assertEqual(gap["bbox_cm"], [4, 1, 100, 10, 2, 105])

    def test_two_openings_that_only_touch_are_valid(self):
        docs = synthetic()
        second_cut = copy.deepcopy(docs[0]["opening_cuts"][0])
        second_cut.update(id="cut-2", opening_id="opening-2", u_range_cm=[4, 6])
        docs[0]["opening_cuts"].append(second_cut)
        second_opening = copy.deepcopy(docs[2]["openings"][0])
        second_opening.update(id="opening-2", position_cm=5)
        docs[2]["openings"].append(second_opening)
        right = docs[0]["wall_cells"].pop()
        docs[0]["wall_cells"].extend([
            {**right, "id": "sill-2", "plan_rect_cm": [4, 0, 6, 2], "z_range_cm": [100, 101]},
            {**right, "id": "head-2", "plan_rect_cm": [4, 0, 6, 2], "z_range_cm": [103, 105]},
            {**right, "id": "right-2", "plan_rect_cm": [6, 0, 10, 2]},
        ])
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "PASS", result.findings)
        self.assertEqual(result.findings, [])

    def test_overlapping_openings_are_detected_without_any_cells_in_the_overlap(self):
        docs = synthetic()
        second_cut = copy.deepcopy(docs[0]["opening_cuts"][0])
        second_cut.update(id="cut-2", opening_id="opening-2",
                          u_range_cm=[2.5, 3.5], v_range_cm=[1.5, 2.5])
        docs[0]["opening_cuts"].append(second_cut)
        second_opening = copy.deepcopy(docs[2]["openings"][0])
        second_opening.update(id="opening-2", position_cm=3, width_cm=1, sill_cm=1.5, head_cm=2.5)
        docs[2]["openings"].append(second_opening)
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL", result.findings)
        finding = self.assert_code(result, "overlapping_openings")
        self.assertEqual(finding["severity"], "ERROR")
        self.assertEqual(finding["cut_ids"], ["cut", "cut-2"])
        self.assertEqual(finding["cell_ids"], [])
        self.assertEqual(finding["bbox_cm"], [2.5, 0, 101.5, 3.5, 2, 102.5])
        self.assertEqual(finding["volume_cm3"], 2)
        self.assertEqual([f["code"] for f in result.findings], ["overlapping_openings"])

    def test_overlapping_openings_tolerance_is_review_or_fail_not_pass(self):
        cases = ((2.999999, 2.7499995, 0.499999, "REVIEW"),
                 (3.0, 2.75, 0.5, "REVIEW"),
                 (3.000001, 2.7500005, 0.500001, "FAIL"))
        for upper, centre, width, expected in cases:
            with self.subTest(width=width):
                docs = synthetic()
                second_cut = copy.deepcopy(docs[0]["opening_cuts"][0])
                second_cut.update(id="cut-2", opening_id="opening-2",
                                  u_range_cm=[2.5, upper], v_range_cm=[1.5, 2.5])
                docs[0]["opening_cuts"].append(second_cut)
                second_opening = copy.deepcopy(docs[2]["openings"][0])
                second_opening.update(id="opening-2", position_cm=centre, width_cm=width,
                                      sill_cm=1.5, head_cm=2.5)
                docs[2]["openings"].append(second_opening)
                result = check_wall_cell_coverage(*docs)
                self.assertEqual(result.status, expected, result.findings)
                finding = self.assert_code(result, "overlapping_openings")
                self.assertAlmostEqual(finding["difference_cm"], width)
                self.assertEqual(finding["cut_ids"], ["cut", "cut-2"])
                self.assertFalse(result.ok)

    def test_four_signed_directions_and_nonzero_level(self):
        for axis in ("x", "y"):
            for reverse in (False, True):
                with self.subTest(axis=axis, reverse=reverse):
                    docs = synthetic(axis, reverse, elevation=-37)
                    result = check_wall_cell_coverage(*docs)
                    self.assertEqual(result.status, "PASS", result.findings)
                    docs[0]["wall_cells"].pop(1)
                    result = check_wall_cell_coverage(*docs)
                    self.assertEqual(result.status, "FAIL")
                    self.assertEqual(self.assert_code(result, "gap")["volume_cm3"], 4)

    def test_translated_world_origins_for_all_directions(self):
        for axis in ("x", "y"):
            for reverse in (False, True):
                with self.subTest(axis=axis, reverse=reverse):
                    docs = synthetic(axis, reverse, elevation=1200)
                    for point in docs[1]["elements"][0]["profile_cm"]:
                        point[0] += 130
                        point[1] -= 70
                    for cell in docs[0]["wall_cells"]:
                        rect = cell["plan_rect_cm"]
                        rect[0] += 130
                        rect[2] += 130
                        rect[1] -= 70
                        rect[3] -= 70
                    for key in ("start_corner_cm", "end_corner_cm"):
                        point = docs[2]["facades"][0][key]
                        point[0] += 130
                        point[1] -= 70
                    result = check_wall_cell_coverage(*docs)
                    self.assertEqual(result.status, "PASS", result.findings)

    def test_alternative_cell_partition_and_forged_volume_fields(self):
        docs = synthetic()
        right = docs[0]["wall_cells"].pop()
        self.assertLess(right["volume_cm3"], 0)  # deliberately false on all cells
        # Spatial coverage alone accepts a different 3-D partition. G-83,
        # which enforces full thickness per cell, remains a separate gate.
        for ident, rect in (("right-a", [4, 0, 7, 1]), ("right-b", [4, 1, 7, 2]),
                            ("right-c", [7, 0, 10, 1]), ("right-d", [7, 1, 10, 2])):
            docs[0]["wall_cells"].append({**right, "id": ident, "plan_rect_cm": rect})
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "PASS", result.findings)

    def test_multiple_elevations_of_same_reversed_facade(self):
        first = synthetic("y", reverse=True, elevation=-37)
        second = synthetic("y", reverse=True, elevation=100)
        second[0]["opening_cuts"][0].update(id="cut-2", host_ref="host-2", opening_id="opening-2", level_index=8)
        for cell in second[0]["wall_cells"]:
            cell.update(id=cell["id"] + "-2", host_ref="host-2")
        second[1]["elements"][0].update(id="host-2", storey_index=8)
        second[2]["levels"][0]["index"] = 8
        second[2]["openings"][0].update(id="opening-2", level_index=8)
        first[2]["facades"][0]["spans_level_indices"] = [7, 8]
        first[0]["opening_cuts"].extend(second[0]["opening_cuts"])
        first[0]["wall_cells"].extend(second[0]["wall_cells"])
        first[1]["elements"].extend(second[1]["elements"])
        first[2]["levels"].extend(second[2]["levels"])
        first[2]["openings"].extend(second[2]["openings"])
        result = check_wall_cell_coverage(*first)
        self.assertEqual(result.status, "PASS", result.findings)
        self.assertEqual(len(result.checked_hosts), 2)
        first[2]["levels"][1]["elevation_cm"] = 0
        result = check_wall_cell_coverage(*first)
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(self.assert_code(result, "host_level_mismatch")["host_ref"], "host-2")

    def test_square_host_still_uses_facade_axis_not_thin_dimension(self):
        docs = synthetic("y", reverse=True)
        docs[1]["elements"][0]["profile_cm"] = [[0, 0], [10, 0], [10, 10], [0, 10]]
        for cell in docs[0]["wall_cells"]:
            cell["plan_rect_cm"][2] = 10
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "PASS", result.findings)

    def test_wrong_sign_or_wrong_level_cannot_pass(self):
        docs = synthetic("x", reverse=True)
        docs[2]["facades"][0]["start_corner_cm"], docs[2]["facades"][0]["end_corner_cm"] = (
            docs[2]["facades"][0]["end_corner_cm"], docs[2]["facades"][0]["start_corner_cm"])
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL", result.findings)
        self.assert_code(result, "opening_filled")
        docs = synthetic(elevation=100)
        docs[2]["levels"][0]["elevation_cm"] = 0
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL")
        self.assert_code(result, "host_level_mismatch")

    def test_threshold_calibration_is_review_not_silent_pass(self):
        for delta, expected in ((0.000001, "REVIEW"), (0.499999, "REVIEW"),
                                (0.5, "REVIEW"), (0.500001, "FAIL")):
            with self.subTest(delta=delta):
                docs = synthetic()
                docs[0]["wall_cells"][0]["plan_rect_cm"][2] = 2 - delta
                result = check_wall_cell_coverage(*docs)
                self.assertEqual(result.status, expected, result.findings)
                self.assertFalse(result.ok)
                gap = self.assert_code(result, "gap")
                self.assertAlmostEqual(gap["difference_cm"], delta)
                self.assertAlmostEqual(gap["volume_cm3"], delta * 10)
                self.assertEqual(gap["severity"], "REVIEW" if expected == "REVIEW" else "ERROR")
        docs = synthetic()
        self.assertEqual(check_wall_cell_coverage(*docs).status, "PASS")
        docs[2]["tolerances"]["linear_cm"] = 0
        docs[0]["wall_cells"][0]["plan_rect_cm"][2] = 1.999999
        self.assertEqual(check_wall_cell_coverage(*docs).status, "FAIL")

    def test_tolerance_never_grants_pass_to_long_thin_gap(self):
        docs = synthetic()
        # A 0.1-cm gap traverses the whole 2x5 cross section. It is reported,
        # not deemed acceptable just because its width is under linear_cm.
        docs[0]["wall_cells"][0]["plan_rect_cm"][2] = 1.9
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "REVIEW")
        self.assertEqual(self.assert_code(result, "gap")["bbox_cm"], [1.9, 0, 100, 2, 2, 105])

    def test_tolerance_calibration_for_overlap_and_filled_opening(self):
        for delta, expected in ((0.499999, "REVIEW"), (0.5, "REVIEW"), (0.500001, "FAIL")):
            for defect in ("overlap", "opening_filled"):
                with self.subTest(delta=delta, defect=defect):
                    docs = synthetic()
                    if defect == "overlap":
                        docs[0]["wall_cells"][-1]["plan_rect_cm"][0] = 4 - delta
                    else:
                        docs[0]["wall_cells"][1]["z_range_cm"][1] = 101 + delta
                    result = check_wall_cell_coverage(*docs)
                    self.assertEqual(result.status, expected, result.findings)
                    finding = self.assert_code(result, defect)
                    self.assertAlmostEqual(finding["difference_cm"], delta)
                    self.assertFalse(result.ok)

    def test_cells_outside_host_and_wrong_opening_are_detected(self):
        docs = synthetic()
        docs[0]["wall_cells"][-1]["plan_rect_cm"][2] = 11
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL")
        self.assert_code(result, "outside_host")
        docs = synthetic()
        docs[0]["opening_cuts"][0]["u_range_cm"] = [3, 5]
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL")
        self.assert_code(result, "cut_opening_mismatch")
        self.assert_code(result, "opening_filled")

    def test_small_cut_disagreement_is_visible_review(self):
        docs = synthetic()
        docs[2]["openings"][0]["position_cm"] += 0.1
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "REVIEW", result.findings)
        self.assert_code(result, "cut_opening_mismatch")

    def test_same_frame_cannot_be_claimed_by_two_hosts(self):
        docs = synthetic()
        second_cut = copy.deepcopy(docs[0]["opening_cuts"][0])
        second_cut.update(id="cut-2", opening_id="opening-2", host_ref="host-2")
        docs[0]["opening_cuts"].append(second_cut)
        second_opening = copy.deepcopy(docs[2]["openings"][0])
        second_opening["id"] = "opening-2"
        docs[2]["openings"].append(second_opening)
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("multiple cut hosts", self.assert_code(result, "invalid_input")["message"])

    def test_unsupported_and_ambiguous_inputs_fail_closed(self):
        mutations = {
            "diagonal facade": lambda a, m, d: d["facades"][0].update(end_corner_cm=[10, 1]),
            "nonrectangular host": lambda a, m, d: m["elements"][0]["profile_cm"].__setitem__(2, [9, 2]),
            "crossed host": lambda a, m, d: m["elements"][0].update(profile_cm=[[0, 0], [10, 2], [10, 0], [0, 2]]),
            "duplicate facade": lambda a, m, d: d["facades"].append(copy.deepcopy(d["facades"][0])),
            "unknown level": lambda a, m, d: d["levels"].clear(),
            "unknown host": lambda a, m, d: a["opening_cuts"][0].update(host_ref="missing"),
            "unknown cut opening": lambda a, m, d: a["opening_cuts"][0].update(opening_id="missing"),
            "nonfinite cell": lambda a, m, d: a["wall_cells"][0]["plan_rect_cm"].__setitem__(0, float("inf")),
            "bad tolerance": lambda a, m, d: d["tolerances"].update(linear_cm=float("nan")),
            "wrong units": lambda a, m, d: m["units"].update(length="mm"),
            "missing units": lambda a, m, d: a.pop("units"),
            "wrong route": lambda a, m, d: a.update(wall_technique="poly_surface_shell_v1"),
            "boolean level": lambda a, m, d: d["openings"][0].update(level_index=True),
            "missing cells array": lambda a, m, d: a.pop("wall_cells"),
            "wrong storey": lambda a, m, d: m["elements"][0].update(storey_index=3),
            "wrong facade face": lambda a, m, d: d["facades"][0].update(start_corner_cm=[0, 4], end_corner_cm=[10, 4]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                docs = synthetic()
                mutate(*docs)
                result = check_wall_cell_coverage(*docs)
                self.assertEqual(result.status, "FAIL", result.findings)
                self.assertFalse(result.ok)

    def test_resource_limit_is_fail_not_partial_pass(self):
        result = check_wall_cell_coverage(*synthetic(), max_atoms=1)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("resource limit", self.assert_code(result, "invalid_or_unsupported_geometry")["message"])

    def test_nonfinite_coordinates_fail_under_explicit_resource_limits(self):
        for value in (float("nan"), float("inf"), float("-inf"), json.loads("1e999")):
            with self.subTest(value=value):
                docs = synthetic()
                docs[0]["wall_cells"][0]["plan_rect_cm"][0] = value
                result = check_wall_cell_coverage(*docs, max_atoms=64, max_work=512)
                self.assertEqual(result.status, "FAIL")
                finding = self.assert_code(result, "invalid_or_unsupported_geometry")
                self.assertIn("finite JSON number", finding["message"])

    def test_huge_finite_coordinates_and_exact_resource_guard(self):
        # Keep the wall and every reference coherent after translating by 10**100;
        # integer coordinates avoid losing the 10-cm wall width to float rounding.
        docs = synthetic()
        origin = 10**100
        for point in docs[1]["elements"][0]["profile_cm"]:
            point[0] += origin
        for cell in docs[0]["wall_cells"]:
            cell["plan_rect_cm"][0] += origin
            cell["plan_rect_cm"][2] += origin
        for key in ("start_corner_cm", "end_corner_cm"):
            docs[2]["facades"][0][key][0] += origin
        positive = check_wall_cell_coverage(*docs, max_atoms=64, max_work=512)
        self.assertEqual(positive.status, "PASS", positive.findings)
        for limits in ({"max_atoms": 1, "max_work": 512}, {"max_atoms": 64, "max_work": 1}):
            with self.subTest(limits=limits):
                result = check_wall_cell_coverage(*docs, **limits)
                self.assertEqual(result.status, "FAIL", result.findings)
                self.assertIn("resource limit", self.assert_code(result, "invalid_or_unsupported_geometry")["message"])

    def test_huge_finite_float_reports_outside_without_nonfinite_findings(self):
        docs = synthetic()
        docs[0]["wall_cells"][-1]["plan_rect_cm"][2] = 1e308
        result = check_wall_cell_coverage(*docs, max_atoms=64, max_work=512)
        self.assertEqual(result.status, "FAIL", result.findings)
        finding = self.assert_code(result, "outside_host")
        self.assertEqual(finding["severity"], "ERROR")
        self.assertIsInstance(finding["volume_cm3"], str)  # too large for a finite float
        json.dumps(result.findings, allow_nan=False)
        limited = check_wall_cell_coverage(*docs, max_atoms=1, max_work=512)
        self.assertEqual(limited.status, "FAIL")
        self.assertIn("resource limit", self.assert_code(limited, "invalid_or_unsupported_geometry")["message"])

    def test_no_openings_means_not_applicable_not_pass(self):
        docs = synthetic()
        docs[0]["opening_cuts"] = []
        docs[0]["wall_cells"] = []
        docs[2]["openings"] = []
        result = check_wall_cell_coverage(*docs)
        self.assertEqual(result.status, "NOT_APPLICABLE")
        self.assertFalse(result.ok)


class ValidatorG82IntegrationTests(unittest.TestCase):
    """G-82 through full Report/run_checks, with in-memory mutations only."""

    @classmethod
    def setUpClass(cls):
        cls.source_hashes = fixture_file_hashes()

    @classmethod
    def tearDownClass(cls):
        current = fixture_file_hashes()
        if current != cls.source_hashes:
            changed = sorted(key for key in cls.source_hashes.keys() | current.keys()
                             if cls.source_hashes.get(key) != current.get(key))
            raise AssertionError(f"fixture files changed during validator tests: {changed}")

    def assert_g82(self, rows, severities, *, detail=None):
        self.assertEqual([row.severity for row in rows], severities,
                         [(row.severity, row.detail) for row in rows])
        self.assertTrue(all("internal error" not in row.detail.lower() for row in rows), rows)
        if detail is not None:
            self.assertTrue(any(detail in row.detail for row in rows), rows)

    def test_three_complete_baselines_pass_g82(self):
        for name, root in FIXTURES.items():
            for build in (False, True):
                with self.subTest(fixture=name, build=build):
                    session, report = validator_session(root, build=build)
                    rows = g82_rows(session, report)
                    self.assert_g82(rows, ["PASS"], detail="independent 3D coverage passed")
                    self.assertIn("volume identity", rows[0].detail)
                    self.assertFalse([f for f in report.findings if f.severity == "FAIL"],
                                     [(f.rule, f.detail) for f in report.findings if f.severity == "FAIL"])

    def test_deleted_known_cell_fails_g82_on_spatial_gap(self):
        session, report = validator_session(FIXTURES["examples"])
        cells = session.assembly.doc["wall_cells"]
        victim = next(c for c in cells if c["id"] == "WAL-EL-014-C01")
        self.assertEqual(geometric_volume(victim), 1_134_000)
        cells.remove(victim)
        rows = g82_rows(session, report)
        self.assert_g82(rows, ["FAIL"], detail="'code': 'gap'")
        self.assertIn("EL-014", rows[0].detail)
        self.assertIn("1134000.0", rows[0].detail)

    def test_all_cells_of_one_cut_host_missing_fails_g82(self):
        session, report = validator_session(FIXTURES["examples"])
        assembly = session.assembly.doc
        self.assertTrue(any(c["host_ref"] == "EL-014" for c in assembly["opening_cuts"]))
        self.assertTrue(any(c["host_ref"] == "EL-014" for c in assembly["wall_cells"]))
        assembly["wall_cells"] = [c for c in assembly["wall_cells"] if c["host_ref"] != "EL-014"]
        rows = g82_rows(session, report)
        self.assert_g82(rows, ["FAIL"], detail="no wall cells")
        self.assertIn("EL-014", rows[0].detail)

    def test_missing_host_element_fails_g82_without_spurious_pass(self):
        session, report = validator_session(FIXTURES["examples"])
        session.massing.doc["elements"] = [e for e in session.massing.doc["elements"] if e["id"] != "EL-014"]
        rows = g82_rows(session, report)
        self.assertTrue(any(row.severity == "FAIL" and "'code': 'missing_host'" in row.detail for row in rows), rows)
        self.assertNotIn("PASS", [row.severity for row in rows], rows)
        self.assertTrue(all("internal error" not in row.detail.lower() for row in rows), rows)

    def test_equal_volume_shift_produces_both_gap_and_overlap_g82_fail(self):
        session, report = validator_session(FIXTURES["examples"])
        cells = session.assembly.doc["wall_cells"]
        # Shift an existing full-height solid two cm to the right: [315,575]
        # -> [317,577]. The left edge is a gap, the right edge overlaps C05.
        moved = next(c for c in cells if c["id"] == "WAL-EL-014-C04")
        original_volume = geometric_volume(moved)
        self.assertEqual(moved["plan_rect_cm"], [315.0, 0.0, 575.0, 20.0])
        moved["plan_rect_cm"][0] += 2.0
        moved["plan_rect_cm"][2] += 2.0
        self.assertEqual(geometric_volume(moved), original_volume)
        self.assertEqual(moved["volume_cm3"], original_volume)
        rows = g82_rows(session, report)
        self.assertEqual({row.severity for row in rows}, {"FAIL"}, rows)
        self.assertTrue(all("internal error" not in row.detail.lower() for row in rows), rows)
        self.assertTrue(any("'code': 'gap'" in row.detail for row in rows), rows)
        self.assertTrue(any("'code': 'overlap'" in row.detail for row in rows), rows)
        self.assertTrue(all("spatial coverage" in row.detail for row in rows), rows)

    def test_narrow_gap_warn_skip_lint_and_fail_build(self):
        for build in (False, True):
            with self.subTest(build=build):
                session, report = validator_session(FIXTURES["examples"], build=build)
                cell = next(c for c in session.assembly.doc["wall_cells"] if c["id"] == "WAL-EL-014-C01")
                cell["plan_rect_cm"][2] = 134.9
                # Keep this metadata coherent so this fault isolates the geometry.
                cell["volume_cm3"] = geometric_volume(cell)
                rows = g82_rows(session, report)
                self.assert_g82(rows, ["FAIL"] if build else ["WARN", "SKIP"], detail="requires review")
                self.assertTrue(any("'code': 'gap'" in row.detail for row in rows), rows)
                self.assertTrue(any("0.1" in row.detail for row in rows), rows)
                self.assertNotIn("PASS", [row.severity for row in rows])
                if build:
                    self.assertIn("build refused", rows[0].detail)
                else:
                    self.assertIn("not accepted as coverage", rows[1].detail)

    def test_narrow_gap_promotes_warn_under_warnings_as_errors(self):
        session, _ = validator_session(FIXTURES["examples"])
        cell = next(c for c in session.assembly.doc["wall_cells"] if c["id"] == "WAL-EL-014-C01")
        cell["plan_rect_cm"][2] = 134.9
        cell["volume_cm3"] = geometric_volume(cell)
        report = validator.Report(warnings_as_errors=True)
        rows = g82_rows(session, report)
        self.assert_g82(rows, ["FAIL", "SKIP"], detail="WARN promoted by --warnings-as-errors")

    def test_unsupported_profile_fails_g82_without_spurious_pass(self):
        session, report = validator_session(FIXTURES["examples"])
        host = next(e for e in session.massing.doc["elements"] if e["id"] == "EL-014")
        # Keep the original rectangle's bounding box and hence the old volume;
        # only the inner contour shape is unsupported by the independent check.
        host["profile_cm"].insert(1, [900.0, 1.0])
        rows = g82_rows(session, report)
        self.assert_g82(rows, ["FAIL"], detail="invalid_or_unsupported_geometry")
        self.assertIn("four-corner rectangular profiles", rows[0].detail)

    def test_volume_failure_is_not_masked_by_spatial_pass(self):
        session, report = validator_session(FIXTURES["examples"])
        assembly, massing, dimensions = synthetic()
        assembly["status"] = "locked"
        assembly["tolerances"] = {"linear_cm": 0}
        dimensions["tolerances"]["linear_cm"] = 0
        # Host runs along X for 10 cm but is 20 cm thick in Y. The spatial
        # oracle uses facade orientation, while historical G-82 volume uses
        # the shorter dimension as thickness. At zero tolerance they disagree.
        massing["elements"][0]["profile_cm"] = [[0, 0], [10, 0], [10, 20], [0, 20]]
        for cell in assembly["wall_cells"]:
            cell["plan_rect_cm"][3] = 20
        self.assertEqual(check_wall_cell_coverage(assembly, massing, dimensions).status, "PASS")
        session.assembly.doc = assembly
        session.massing.doc = massing
        session.dimensions.doc = dimensions
        rows = g82_rows(session, report)
        self.assert_g82(rows, ["FAIL"], detail="volume tolerance budget")

    def test_empty_openings_and_cells_do_not_produce_g82_pass(self):
        session, report = validator_session(FIXTURES["examples"])
        session.assembly.doc["opening_cuts"] = []
        session.assembly.doc["wall_cells"] = []
        session.dimensions.doc["openings"] = []
        rows = g82_rows(session, report)
        self.assertIn("SKIP", [row.severity for row in rows], rows)
        self.assertNotIn("PASS", [row.severity for row in rows], rows)
        self.assertTrue(any("no evaluable" in row.detail or "not applicable" in row.detail for row in rows), rows)


if __name__ == "__main__":
    unittest.main()
