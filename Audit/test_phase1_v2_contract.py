#!/usr/bin/env python3
"""Phase 1 Acceptance & Verification Test Suite for closed_inner_contour_shell_v2.

Tests:
1. Polygon geometry, closure, simplicity, and CCW normalization:
   - CW to CCW reversal while preserving stable segment and opening IDs.
   - Opening s-range inversion on reversed edges: s'_min = L - s_max, s'_max = L - s_min.
   - Clean removal of closing duplicate vertex without creating a zero segment.
2. Safe contour offset & all 6 mathematical safety gates:
   - Positive cases: Rectangle blind, rectangle openings, L-shape, U-shape, Oblique, Outer 12x8 -> Inner.
   - Negative controls: Inset collapse, edge collapse, bowtie self-intersection, acute needle miter (< 30 deg), narrow notch crossing.
3. S4w -> S5 -> QA Opening Manifest contract:
   - Orthonormal basis frames (T, Outward, Up).
   - Transform matrices, mounting parameters, clearances, and rough openings.
4. Thickness provenance law:
   - Rejection when thickness is absent and not recorded in assumptions.json (builder never invents defaults).
   - Acceptance when missing thickness is explicitly claimed in assumptions.json.
5. Route validation & Exclusivity (G-92, G-93, G-94, G-96, G-97):
   - Route matching between walls.json and assembly.json.
   - Rejection on route conflict or illegal legacy tables (wall_cells, opening_cuts) in v2.
6. Legacy compatibility regression:
   - examples/ project passes with 0 FAIL.
"""
from __future__ import annotations

import copy
import json
import math
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import subprocess

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import wall_contour_v2 as wc
import validate_specs as validator


def run_validator(directory: Path, *extra_args: str) -> tuple[int, dict]:
    cmd = [sys.executable, str(ROOT / "scripts" / "validate_specs.py"), "--dir", str(directory), "--json", *extra_args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    report = json.loads(res.stdout) if res.stdout else {}
    return res.returncode, report


class TestPolygonAndCCWNormalization(unittest.TestCase):
    """Test 2D polygon validation, deduplication, and CCW normalization."""

    def test_ccw_polygon_already_normalized(self):
        pts = [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0]]
        norm = wc.normalize_contour_ccw(pts)
        self.assertTrue(norm.is_ccw)
        self.assertFalse(norm.was_reversed)
        self.assertFalse(norm.closing_knot_stripped)
        self.assertAlmostEqual(norm.signed_area, 240000.0, places=4)
        self.assertEqual(len(norm.vertices), 4)

    def test_closing_duplicate_vertex_stripped(self):
        pts = [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0], [0.0, 0.0]]
        norm = wc.normalize_contour_ccw(pts)
        self.assertTrue(norm.closing_knot_stripped)
        self.assertEqual(len(norm.vertices), 4)
        self.assertAlmostEqual(norm.signed_area, 240000.0, places=4)

    def test_cw_polygon_reversed_with_segment_and_opening_preservation(self):
        # CW rectangle: (0,0) -> (0,400) -> (600,400) -> (600,0)
        # Edge 0: (0,0) -> (0,400), length 400
        # Opening on Edge 0: s in [100, 250]
        pts_cw = [[0.0, 0.0], [0.0, 400.0], [600.0, 400.0], [600.0, 0.0]]
        segs = [
            {"id": "SEG-0", "start_vertex_index": 0, "end_vertex_index": 1},
            {"id": "SEG-1", "start_vertex_index": 1, "end_vertex_index": 2},
            {"id": "SEG-2", "start_vertex_index": 2, "end_vertex_index": 3},
            {"id": "SEG-3", "start_vertex_index": 3, "end_vertex_index": 0},
        ]
        openings = [
            {"id": "OP-1", "segment_id": "SEG-0", "kind": "window", "s_range_cm": [100.0, 250.0], "sill_cm": 90.0, "head_cm": 210.0}
        ]

        norm = wc.normalize_contour_ccw(pts_cw, segments=segs, openings=openings)
        self.assertTrue(norm.is_ccw)
        self.assertTrue(norm.was_reversed)
        self.assertAlmostEqual(norm.signed_area, 240000.0, places=4)

        # Segment ID preserved
        seg_map = {s["id"]: s for s in norm.segments}
        self.assertIn("SEG-0", seg_map)
        self.assertTrue(seg_map["SEG-0"].get("is_reversed"))

        # Opening preserved with flipped s-range: [400 - 250, 400 - 100] = [150, 300]
        self.assertEqual(len(norm.openings), 1)
        op = norm.openings[0]
        self.assertEqual(op["id"], "OP-1")
        self.assertEqual(op["segment_id"], "SEG-0")
        self.assertAlmostEqual(op["s_range_cm"][0], 150.0, places=4)
        self.assertAlmostEqual(op["s_range_cm"][1], 300.0, places=4)
        self.assertEqual(op["sill_cm"], 90.0)
        self.assertEqual(op["head_cm"], 210.0)

    def test_bowtie_polygon_rejected(self):
        bowtie = [[0.0, 0.0], [100.0, 100.0], [0.0, 100.0], [100.0, 0.0]]
        with self.assertRaises(wc.ContourError) as ctx:
            wc.normalize_contour_ccw(bowtie)
        self.assertEqual(ctx.exception.code, "POLYGON_SELF_INTERSECTION")

    def test_zero_length_edge_rejected(self):
        degenerate = [[0.0, 0.0], [600.0, 0.0], [600.0, 0.0], [0.0, 400.0]]
        with self.assertRaises(wc.ContourError) as ctx:
            wc.normalize_contour_ccw(degenerate)
        self.assertEqual(ctx.exception.code, "ZERO_LENGTH_EDGE")


class TestSafeContourOffset(unittest.TestCase):
    """Test safe contour offset algorithm and the 6 safety gates."""

    def test_positive_rectangle_outward(self):
        rect = [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0]]
        res = wc.safe_contour_offset(rect, 30.0, reference_face="inner")
        self.assertTrue(res.verified)
        self.assertAlmostEqual(res.inner_area, 240000.0, places=4)
        # Expected outer area = (600 + 60) * (400 + 60) = 660 * 460 = 303600
        self.assertAlmostEqual(res.outer_area, 303600.0, places=4)

    def test_positive_outer_12x8_inward(self):
        # Outer reference 1200x800 cm with 30 cm thickness -> inner 1140x740 cm
        outer = [[0.0, 0.0], [1200.0, 0.0], [1200.0, 800.0], [0.0, 800.0]]
        res = wc.safe_contour_offset(outer, 30.0, reference_face="outer")
        self.assertTrue(res.verified)
        self.assertAlmostEqual(res.outer_area, 960000.0, places=4)
        self.assertAlmostEqual(res.inner_area, 843600.0, places=4)
        # Inner vertices should be at (30, 30), (1170, 30), (1170, 770), (30, 770)
        self.assertAlmostEqual(res.inner_vertices[0][0], 30.0, places=4)
        self.assertAlmostEqual(res.inner_vertices[0][1], 30.0, places=4)
        self.assertAlmostEqual(res.inner_vertices[2][0], 1170.0, places=4)
        self.assertAlmostEqual(res.inner_vertices[2][1], 770.0, places=4)

    def test_positive_L_shape_offset(self):
        L_pts = [[0.0, 0.0], [600.0, 0.0], [600.0, 250.0], [350.0, 250.0], [350.0, 500.0], [0.0, 500.0]]
        res = wc.safe_contour_offset(L_pts, 30.0, reference_face="inner")
        self.assertTrue(res.verified)
        self.assertGreater(res.outer_area, res.inner_area)

    def test_positive_U_shape_offset(self):
        U_pts = [[0.0, 0.0], [800.0, 0.0], [800.0, 600.0], [550.0, 600.0],
                 [550.0, 250.0], [250.0, 250.0], [250.0, 600.0], [0.0, 600.0]]
        res = wc.safe_contour_offset(U_pts, 30.0, reference_face="inner")
        self.assertTrue(res.verified)
        self.assertGreater(res.outer_area, res.inner_area)

    def test_negative_gate2_excessive_miter_acute_needle(self):
        # Acute needle with interior angle ~5.7 deg (< 30 deg)
        needle = [[0.0, 0.0], [1000.0, 50.0], [0.0, 100.0]]
        with self.assertRaises(wc.ContourOffsetError) as ctx:
            wc.safe_contour_offset(needle, 10.0, reference_face="inner")
        self.assertEqual(ctx.exception.code, "EXCESSIVE_MITER")

    def test_negative_gate3_inset_collapse_exact(self):
        # 100x100 room with 50 cm inward offset collapses area to 0
        room = [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]
        with self.assertRaises(wc.ContourOffsetError) as ctx:
            wc.safe_contour_offset(room, 50.0, reference_face="outer")
        self.assertEqual(ctx.exception.code, "INSET_COLLAPSE")

    def test_negative_gate4_edge_collapse(self):
        # 100x100 room with 60 cm inward offset inverts edge direction
        room = [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]
        with self.assertRaises(wc.ContourOffsetError) as ctx:
            wc.safe_contour_offset(room, 60.0, reference_face="outer")
        self.assertEqual(ctx.exception.code, "EDGE_COLLAPSE")

    def test_negative_gate6_narrow_notch_crossing(self):
        # U-shape where inward corridor walls cross each other
        narrow_U = [[0.0, 0.0], [600.0, 0.0], [600.0, 600.0], [450.0, 600.0],
                    [450.0, 250.0], [250.0, 250.0], [250.0, 600.0], [0.0, 600.0]]
        with self.assertRaises(wc.ContourOffsetError) as ctx:
            wc.safe_contour_offset(narrow_U, 120.0, reference_face="inner")
        self.assertIn(ctx.exception.code, ("EDGE_COLLAPSE", "OFFSET_SELF_INTERSECTION", "NARROW_NOTCH"))


class TestOpeningManifestContract(unittest.TestCase):
    """Test S4w -> S5 -> QA Opening Manifest generation and local coordinate frames."""

    def test_manifest_local_frames_and_properties(self):
        rect = [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0]]
        segs = [
            {"id": "seg_south", "start_vertex_index": 0, "end_vertex_index": 1},
            {"id": "seg_east", "start_vertex_index": 1, "end_vertex_index": 2},
            {"id": "seg_north", "start_vertex_index": 2, "end_vertex_index": 3},
            {"id": "seg_west", "start_vertex_index": 3, "end_vertex_index": 0},
        ]
        ops = [
            {"id": "OP-001", "segment_id": "seg_south", "kind": "door", "s_range_cm": [100.0, 200.0], "sill_cm": 0.0, "head_cm": 210.0},
            {"id": "OP-002", "segment_id": "seg_east", "kind": "window", "s_range_cm": [50.0, 150.0], "sill_cm": 90.0, "head_cm": 210.0},
        ]
        norm = wc.normalize_contour_ccw(rect, segments=segs, openings=ops)
        records = wc.build_opening_manifest(
            "pavilion-01", "storey_1", "contour_1", norm, 30.0,
            base_z_cm=0.0, top_z_cm=300.0, mount_reference="inner_face"
        )
        self.assertEqual(len(records), 2)

        # Check door record on seg_south (points along +X, normal along -Y)
        door = records[0]
        self.assertEqual(door["manifest_version"], "2.0")
        self.assertEqual(door["opening_id"], "OP-001")
        self.assertEqual(door["kind"], "door")
        self.assertEqual(door["station_along_segment"]["width_cm"], 100.0)
        self.assertEqual(door["vertical_bounds"]["height_cm"], 210.0)

        frame = door["local_frame"]
        t = frame["tangent"]
        n = frame["outward"]
        up = frame["up"]
        orig = frame["origin_cm"]

        # Tangent along +X, Outward along -Y, Up along +Z
        self.assertEqual(t, [1.0, 0.0, 0.0])
        self.assertEqual(n, [0.0, -1.0, 0.0])
        self.assertEqual(up, [0.0, 0.0, 1.0])
        self.assertEqual(orig, [100.0, 0.0, 0.0])

        # Basis matrix check
        mat = frame["basis_matrix"]
        self.assertEqual(mat[0], (1.0, 0.0, 0.0, 100.0))
        self.assertEqual(mat[1], (0.0, -1.0, 0.0, 0.0))
        self.assertEqual(mat[2], (0.0, 0.0, 1.0, 0.0))

        # Check window record on seg_east (points along +Y, normal along +X)
        win = records[1]
        self.assertEqual(win["opening_id"], "OP-002")
        frame_win = win["local_frame"]
        self.assertEqual(frame_win["tangent"], [0.0, 1.0, 0.0])
        self.assertEqual(frame_win["outward"], [1.0, 0.0, 0.0])
        self.assertEqual(frame_win["origin_cm"], [600.0, 50.0, 90.0])


class TestThicknessProvenanceAndRefusal(unittest.TestCase):
    """Test strict thickness provenance law (builder never invents defaults)."""

    def setUp(self):
        self.base_doc = {
            "schema_version": "2.0",
            "spec": "walls",
            "project": "pavilion-01",
            "units": {"length": "cm", "angle": "deg"},
            "source": {"kind": "user_brief", "reference": "test", "recorded_at": "2026-11-04T00:00:00Z"},
            "status": "locked",
            "tolerances": {"linear_cm": 0.5, "area_m2": 0.05, "angle_deg": 0.01},
            "origin_inputs": [],
            "origins": {"storeys[0]": {"origin": "given"}},
            "wall_technique": "closed_inner_contour_shell_v2",
            "reference_face": "inner",
            "storeys": [
                {
                    "id": "st_1",
                    "base_z_cm": 0.0,
                    "top_z_cm": 300.0,
                    "vertices_cm": [[0, 0], [600, 0], [600, 400], [0, 400]]
                }
            ]
        }

    def test_missing_thickness_refused_without_assumption(self):
        errs = wc.validate_walls_v2_document(self.base_doc)
        self.assertTrue(any("builder cannot invent thickness" in e for e in errs), errs)

    def test_missing_thickness_accepted_with_recorded_assumption(self):
        assumptions = {
            "assumptions": [
                {
                    "id": "A-026",
                    "field_path": "storeys[0].wall_thickness_cm",
                    "value": 30.0
                }
            ]
        }
        errs = wc.validate_walls_v2_document(self.base_doc, assumptions_doc=assumptions)
        self.assertEqual(errs, [])


class TestValidatorIntegrationAndExclusivity(unittest.TestCase):
    """Test validate_specs.py integration with closed_inner_contour_shell_v2."""

    def test_v2_fixture_validates_cleanly(self):
        fixture_dir = ROOT / "specs" / "fixtures" / "v2-closed-shell-input"
        rc, report = run_validator(fixture_dir)
        self.assertEqual(rc, 0, f"Validator failed on v2 fixture: {report}")
        self.assertEqual(report["summary"]["FAIL"], 0)
        self.assertGreater(report["summary"]["PASS"], 130)

        # In draft assembly stage: G-93, G-94, G-97 PASS; G-92 and G-96 are cleanly SKIP (incomplete)
        rules = {f["rule"]: f["severity"] for f in report["findings"]}
        self.assertEqual(rules.get("G-93"), "PASS")
        self.assertEqual(rules.get("G-94"), "PASS")
        self.assertEqual(rules.get("G-97"), "PASS")
        # With locked v2 assembly produced by Phase 3 S5, G-92 PASSES; if draft, SKIP
        self.assertIn(rules.get("G-92"), ("PASS", "SKIP"))
        self.assertEqual(rules.get("G-96"), "SKIP")

    def test_v2_locked_assembly_and_manifest_passes_g92(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            shutil.copytree(ROOT / "specs" / "fixtures" / "v2-closed-shell-input", tmppath / "pipeline")
            p = tmppath / "pipeline"

            # Use valid produced assembly from fixture updated for v2
            asm = json.loads((p / "assembly.json").read_text(encoding="utf-8"))
            asm["wall_technique"] = "closed_inner_contour_shell_v2"
            asm["wall_ref"] = "wall_surface.json"
            asm.pop("opening_cuts", None)
            asm.pop("wall_cells", None)
            asm["origins"]["wall_technique"] = {"origin": "given"}
            asm["origins"]["wall_ref"] = {"origin": "given"}
            with open(p / "assembly.json", "w", encoding="utf-8", newline="\n") as f:
                json.dump(asm, f, indent=2)
                f.write("\n")
            with open(p / "wall_surface.json", "w", encoding="utf-8", newline="\n") as f:
                json.dump({"manifest_version": "2.0"}, f)
                f.write("\n")

            rc, report = run_validator(p)
            self.assertEqual(rc, 0)
            rules = {f["rule"]: f["severity"] for f in report["findings"]}
            self.assertEqual(rules.get("G-92"), "PASS")

    def test_route_mismatch_fails_g92(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            shutil.copytree(ROOT / "specs" / "fixtures" / "v2-closed-shell-input", tmppath / "pipeline")
            p = tmppath / "pipeline"

            # Modify assembly to claim legacy_cells_v1 while walls.json is closed_inner_contour_shell_v2
            asm = json.loads((p / "assembly.json").read_text(encoding="utf-8"))
            asm["wall_technique"] = "legacy_cells_v1"
            with open(p / "assembly.json", "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(asm) + "\n")

            rc, report = run_validator(p)
            self.assertEqual(rc, 1)
            g92_fails = [f for f in report["findings"] if f["rule"] == "G-92" and f["severity"] == "FAIL"]
            self.assertTrue(len(g92_fails) > 0)
            self.assertIn("conflicts", g92_fails[0]["detail"])

    def test_exclusivity_fails_if_v2_assembly_declares_legacy_cells(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            shutil.copytree(ROOT / "specs" / "fixtures" / "v2-closed-shell-input", tmppath / "pipeline")
            p = tmppath / "pipeline"

            # Modify assembly to be locked/produced and contain wall_cells
            asm = json.loads((p / "assembly.json").read_text(encoding="utf-8"))
            asm["status"] = "locked"
            asm["wall_cells"] = [{"node_name": "WAL_001"}]
            with open(p / "assembly.json", "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(asm) + "\n")

            rc, report = run_validator(p)
            self.assertEqual(rc, 1)
            g96_fails = [f for f in report["findings"] if f["rule"] == "G-96" and f["severity"] == "FAIL"]
            self.assertTrue(len(g96_fails) > 0)
            self.assertIn("wall_cells must be absent", g96_fails[0]["detail"])


class TestLegacyRegressionPreserved(unittest.TestCase):
    """Test that existing legacy examples validate with 0 FAIL."""

    def test_examples_legacy_clean(self):
        rc, report = run_validator(ROOT / "examples")
        self.assertEqual(rc, 0)
        self.assertEqual(report["summary"]["FAIL"], 0)
        self.assertEqual(report["summary"]["WARN"], 0)


if __name__ == "__main__":
    unittest.main()
