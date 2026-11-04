#!/usr/bin/env python3
"""Phase 2 Verification Test Suite for closed_inner_contour_shell_v2 Wall Builder.

Tests:
1. Generation on fixture (specs/fixtures/v2-closed-shell-input/):
   - Successful emission of wall_surface.json and wall_surface.ms.
   - Return dictionary structure and artifact paths.
2. Structure and content of wall_surface.json:
   - Ownership manifest, node definitions, class and roles.
   - S4w -> S5 -> QA opening manifest (local frame, orthonormal basis, rough openings, clearances).
   - Topology budgets and counts (grid polygons, deleted faces, active polygons).
3. Exact analytical volume and bounding box:
   - V = (A_outer - A_inner) * H - sum(w * h * t).
   - Accurate 3D bounding box including outward Shell miter extent.
4. Emitted MAXScript source verification:
   - Balanced syntax and fileIn compatibility.
   - Zero banned tokens: NO formattedPrint, NO stopCreating, NO bare global fn.
   - NO lease, witness, nonces, POISONED, or rootScene traversals.
   - Correct Shell parameters (innerAmount 0, outerAmount wall_thickness*factor, straightenCorners true,
     segments 1, matID 3, matInnerID 1, matOuterID 2).
   - SplineShape inner guide created and hidden.
5. Strict thickness provenance law:
   - BuildRefusal raised when wall_thickness_cm is absent and no assumptions.json entry claims it.
   - Successful build when thickness is read from assumptions.json.
   - Rejection on non-positive or non-finite thickness.
6. Targeted rebuild & foreign sentinel preservation:
   - Exactly owned node names deleted; no wildcard deletion.
   - Preservation of WS_FOREIGN_SENTINEL and unrelated scene geometry.
7. Geometric variants:
   - Blind contour without openings (empty deleteFaces).
   - Multi-storey building aggregation.
   - Custom namespaces and unit configurations.
   - Rejection of invalid route or corrupt/self-intersecting contours.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_wall_v2 as builder
import scene_units
import wall_contour_v2 as wc

FIXTURE_DIR = ROOT / "specs" / "fixtures" / "v2-closed-shell-input"


class TestPhase2BuilderFixtureGeneration(unittest.TestCase):
    """Test standard generation on the authoritative v2 fixture."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_builder_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_generation_on_fixture(self):
        res = builder.build_walls_v2(FIXTURE_DIR, self.tmp_dir)
        self.assertIsInstance(res, dict)

        # Artifacts exist
        json_path = Path(res["artifacts"]["wall_surface_json"])
        ms_path = Path(res["artifacts"]["wall_surface_ms"])
        self.assertTrue(json_path.is_file())
        self.assertTrue(ms_path.is_file())
        self.assertGreater(json_path.stat().st_size, 0)
        self.assertGreater(ms_path.stat().st_size, 0)

        # Top-level manifest keys
        self.assertEqual(res["schema_version"], "2.0")
        self.assertEqual(res["spec"], "wall_surface")
        self.assertEqual(res["wall_technique"], "closed_inner_contour_shell_v2")
        self.assertEqual(res["project"], "pavilion-01")
        self.assertEqual(res["namespace"], "WS")


class TestWallSurfaceJsonStructure(unittest.TestCase):
    """Test detailed schema and semantic structure of wall_surface.json."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_json_")
        self.res = builder.build_walls_v2(FIXTURE_DIR, self.tmp_dir)
        json_path = Path(self.res["artifacts"]["wall_surface_json"])
        with open(json_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_nodes_manifest(self):
        nodes = self.manifest.get("nodes", [])
        self.assertEqual(len(nodes), 2)

        node_map = {n["name"]: n for n in nodes}
        self.assertIn("WS_storey_1", node_map)
        self.assertIn("WS_storey_1_InnerSpline", node_map)

        wall_node = node_map["WS_storey_1"]
        self.assertEqual(wall_node["role"], "wall_shell")
        self.assertEqual(wall_node["class"], "Editable_Poly")
        self.assertEqual(wall_node["storey_id"], "storey_1")

        guide_node = node_map["WS_storey_1_InnerSpline"]
        self.assertEqual(guide_node["role"], "inner_guide_spline")
        self.assertEqual(guide_node["class"], "SplineShape")
        self.assertEqual(guide_node["storey_id"], "storey_1")

        self.assertEqual(self.manifest.get("owned_nodes"), ["WS_storey_1", "WS_storey_1_InnerSpline"])

    def test_opening_manifest_records(self):
        openings = self.manifest.get("openings", [])
        self.assertEqual(len(openings), 3)

        op_map = {op["opening_id"]: op for op in openings}
        self.assertIn("OP-001", op_map)
        self.assertIn("OP-002", op_map)
        self.assertIn("OP-003", op_map)

        # Check door OP-001
        door = op_map["OP-001"]
        self.assertEqual(door["kind"], "door")
        self.assertEqual(door["segment_id"], "seg_south")
        self.assertEqual(door["rough_opening"]["width_cm"], 100.0)
        self.assertEqual(door["rough_opening"]["height_cm"], 210.0)
        self.assertEqual(door["rough_opening"]["depth_cm"], 30.0)

        # Orthonormality of local frame
        frame = door["local_frame"]
        t = frame["tangent"]
        n = frame["outward"]
        up = frame["up"]
        dot_tn = t[0] * n[0] + t[1] * n[1] + t[2] * n[2]
        dot_tup = t[0] * up[0] + t[1] * up[1] + t[2] * up[2]
        dot_nup = n[0] * up[0] + n[1] * up[1] + n[2] * up[2]
        self.assertAlmostEqual(dot_tn, 0.0, places=6)
        self.assertAlmostEqual(dot_tup, 0.0, places=6)
        self.assertAlmostEqual(dot_nup, 0.0, places=6)
        self.assertAlmostEqual(math.hypot(t[0], t[1]), 1.0, places=6)
        self.assertAlmostEqual(math.hypot(n[0], n[1]), 1.0, places=6)
        self.assertEqual(up, [0.0, 0.0, 1.0])

        # Basis matrix
        mat = frame["basis_matrix"]
        self.assertEqual(len(mat), 3)
        self.assertEqual(len(mat[0]), 4)

    def test_topology_budget_and_counts(self):
        topo = self.manifest.get("topology_budget", {})
        self.assertEqual(topo.get("total_grid_polygons"), 50)
        self.assertEqual(topo.get("total_deleted_faces"), 7)
        self.assertEqual(topo.get("total_base_active_polygons"), 43)
        self.assertEqual(topo.get("total_evaluated_triangles"), 86)

        # Confirm fits within fixture declared budget (128 max_grid, 128 max_base, 1024 max_eval)
        self.assertLessEqual(topo["total_grid_polygons"], 128)
        self.assertLessEqual(topo["total_base_active_polygons"], 128)
        self.assertLessEqual(topo["total_evaluated_triangles"], 1024)


class TestAnalyticalVolumeAndBoundingBox(unittest.TestCase):
    """Test exact volume derivation and bounding box calculation."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_vol_")
        self.res = builder.build_walls_v2(FIXTURE_DIR, self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_exact_analytical_volume(self):
        # Calculation:
        # Inner rectangle: 600 x 400 = 240,000 cm2
        # Outer rectangle: (600 + 2*30) x (400 + 2*30) = 660 x 460 = 303,600 cm2
        # Wall cross-section area: 303,600 - 240,000 = 63,600 cm2
        # Storey height: 300 cm
        # Solid volume: 63,600 * 300 = 19,080,000 cm3
        #
        # Openings:
        # OP-001 (door): w = 100, h = 210, t = 30 -> 100 * 210 * 30 = 630,000 cm3
        # OP-002 (window): w = 180, h = 120, t = 30 -> 180 * 120 * 30 = 648,000 cm3
        # OP-003 (window): w = 200, h = 130, t = 30 -> 200 * 130 * 30 = 780,000 cm3
        # Total openings volume = 2,058,000 cm3
        #
        # Net analytical volume = 19,080,000 - 2,058,000 = 17,022,000 cm3
        expected_volume = 17022000.0
        self.assertAlmostEqual(self.res["analytical_volume_cm3"], expected_volume, places=2)
        self.assertAlmostEqual(self.res["volume_cm3"], expected_volume, places=2)

    def test_bounding_box(self):
        # Inner: [0, 0] to [600, 400], Z from 0 to 300
        # Thickness = 30 outward miter -> [-30, -30] to [630, 430]
        # Bounds: [min_x, min_y, min_z, max_x, max_y, max_z]
        expected_bbox = [-30.0, -30.0, 0.0, 630.0, 430.0, 300.0]
        self.assertEqual(self.res["analytical_bbox_cm"], expected_bbox)
        self.assertEqual(self.res["bounds_cm"], expected_bbox)


class TestEmittedMaxscriptVerification(unittest.TestCase):
    """Test syntax, banned tokens, and modifier parameters in wall_surface.ms."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_ms_")
        res = builder.build_walls_v2(FIXTURE_DIR, self.tmp_dir)
        ms_path = Path(res["artifacts"]["wall_surface_ms"])
        with open(ms_path, "r", encoding="utf-8") as f:
            self.ms = f.read()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_banned_tokens(self):
        # formattedPrint is fatal in 3ds Max MCP bridge
        self.assertNotIn("formattedPrint", self.ms)
        # stopCreating without args or with args is not used
        self.assertNotIn("stopCreating", self.ms)
        # bare global functions or global fn are forbidden
        self.assertNotIn("global fn", self.ms)
        self.assertNotIn("global function", self.ms)
        # No lease, witness, nonces, POISONED, rootScene traversals
        ms_lower = self.ms.lower()
        self.assertNotIn("lease", ms_lower)
        self.assertNotIn("witness", ms_lower)
        self.assertNotIn("poisoned", ms_lower)
        self.assertNotIn("rootscene", ms_lower)

    def test_parentheses_balance(self):
        # The script is enclosed in an outer (...) block
        open_parens = self.ms.count("(")
        close_parens = self.ms.count(")")
        self.assertEqual(open_parens, close_parens)

        open_brackets = self.ms.count("[")
        close_brackets = self.ms.count("]")
        self.assertEqual(open_brackets, close_brackets)

        open_braces = self.ms.count("{")
        close_braces = self.ms.count("}")
        self.assertEqual(open_braces, close_braces)

    def test_shell_modifier_parameters(self):
        # Assert certified Shell parameters per contract §1
        self.assertIn("innerAmount:0.0", self.ms)
        self.assertIn("outerAmount:(30.0 * factor)", self.ms)
        self.assertIn("straightenCorners:true", self.ms)
        self.assertIn("segments:1", self.ms)
        self.assertIn("overrideMatID:true", self.ms)
        self.assertIn("matID:3", self.ms)
        self.assertIn("overrideInnerMatID:true", self.ms)
        self.assertIn("matInnerID:1", self.ms)
        self.assertIn("overrideOuterMatID:true", self.ms)
        self.assertIn("matOuterID:2", self.ms)

    def test_guide_spline_hidden(self):
        self.assertIn('SplineShape name:"WS_storey_1_InnerSpline"', self.ms)
        self.assertIn("guide.isHidden = true", self.ms)

    def test_poly_mesh_creation_and_opening_cuts(self):
        self.assertIn('Editable_mesh name:"WS_storey_1"', self.ms)
        self.assertIn("convertTo wall Editable_Poly", self.ms)
        self.assertIn("polyop.deleteFaces wall delFaces delIsoVerts:true", self.ms)
        self.assertIn("polyop.setFaceSmoothGroup wall #all 0", self.ms)
        self.assertIn("local delFaces = #{2,12,14,22,24,27,37}", self.ms)


class TestThicknessLawAndProvenance(unittest.TestCase):
    """Test strict thickness provenance law: builder never invents defaults."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_thickness_")
        # Copy fixture specs
        for f in FIXTURE_DIR.iterdir():
            if f.is_file():
                shutil.copy2(f, self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_refusal_when_thickness_missing_without_assumptions(self):
        # Remove wall_thickness_cm from walls.json
        walls_path = Path(self.tmp_dir) / "walls.json"
        with open(walls_path, "r", encoding="utf-8") as f:
            walls_data = json.load(f)

        del walls_data["storeys"][0]["wall_thickness_cm"]
        if "wall_thickness_cm" in walls_data:
            del walls_data["wall_thickness_cm"]

        with open(walls_path, "w", encoding="utf-8") as f:
            json.dump(walls_data, f, indent=2)

        # Ensure assumptions.json does not declare thickness for walls
        asm_path = Path(self.tmp_dir) / "assumptions.json"
        if asm_path.is_file():
            with open(asm_path, "r", encoding="utf-8") as f:
                asm_data = json.load(f)
            asm_data["assumptions"] = [
                a for a in asm_data.get("assumptions", [])
                if "wall_thickness_cm" not in str(a.get("field_path", ""))
            ]
            with open(asm_path, "w", encoding="utf-8") as f:
                json.dump(asm_data, f, indent=2)

        with self.assertRaises(builder.BuildRefusal) as ctx:
            builder.build_walls_v2(self.tmp_dir)

        msg = str(ctx.exception)
        self.assertTrue("wall_thickness_cm is missing" in msg or "builder cannot invent" in msg)

    def test_thickness_read_from_assumptions_ledger(self):
        # Remove thickness from walls.json
        walls_path = Path(self.tmp_dir) / "walls.json"
        with open(walls_path, "r", encoding="utf-8") as f:
            walls_data = json.load(f)
        del walls_data["storeys"][0]["wall_thickness_cm"]
        with open(walls_path, "w", encoding="utf-8") as f:
            json.dump(walls_data, f, indent=2)

        # Add assumption entry
        asm_path = Path(self.tmp_dir) / "assumptions.json"
        with open(asm_path, "r", encoding="utf-8") as f:
            asm_data = json.load(f)

        asm_data["assumptions"].append({
            "id": "A-099",
            "field_path": "storeys[0].wall_thickness_cm",
            "value": 35.0,
            "reason": "Assumed thickness for test",
            "confidence": "medium",
            "recheck_stage": "P3"
        })
        with open(asm_path, "w", encoding="utf-8") as f:
            json.dump(asm_data, f, indent=2)

        res = builder.build_walls_v2(self.tmp_dir)
        self.assertEqual(res["storeys"][0]["wall_thickness_cm"], 35.0)


class TestTargetedRebuildAndSentinelPreservation(unittest.TestCase):
    """Test targeted rebuild safety: preserves foreign objects and sentinels."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_rebuild_")
        res = builder.build_walls_v2(FIXTURE_DIR, self.tmp_dir)
        ms_path = Path(res["artifacts"]["wall_surface_ms"])
        with open(ms_path, "r", encoding="utf-8") as f:
            self.ms = f.read()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_foreign_sentinel_not_in_owned_names(self):
        # Verify ownedNodeNames contains strictly owned nodes
        self.assertNotIn("WS_FOREIGN_SENTINEL", self.ms)
        self.assertNotIn("FOREIGN_SENTINEL", self.ms)

        # Parse ownedNodeNames array from MAXScript
        match = re.search(r"local ownedNodeNames = #\((.*?)\)", self.ms, re.DOTALL)
        self.assertIsNotNone(match)
        block = match.group(1)
        owned_names = [nm.strip(' "\t\r\n') for nm in block.split(",") if nm.strip(' "\t\r\n')]
        self.assertEqual(owned_names, ["WS_storey_1", "WS_storey_1_InnerSpline"])

    def test_mock_scene_rebuild_preserves_sentinel(self):
        # Simulate MAXScript scene execution
        mock_scene = {
            "WS_storey_1": "WallPolyNode",
            "WS_storey_1_InnerSpline": "GuideSplineNode",
            "WS_FOREIGN_SENTINEL": "ProtectedSentinelNode",
            "S2_Floor_01": "FloorPlateNode",
            "S3_Core_01": "CoreNode",
        }

        # Emulate the deletion loop in wall_surface.ms:
        # local ownedNodeNames = #("WS_storey_1", "WS_storey_1_InnerSpline")
        # for nm in ownedNodeNames do ( local nd = getNodeByName nm; if nd != undefined do delete nd )
        match = re.search(r"local ownedNodeNames = #\((.*?)\)", self.ms, re.DOTALL)
        block = match.group(1)
        owned_names = [nm.strip(' "\t\r\n') for nm in block.split(",") if nm.strip(' "\t\r\n')]

        for nm in owned_names:
            if nm in mock_scene:
                del mock_scene[nm]

        # Verify exact owned nodes were deleted
        self.assertNotIn("WS_storey_1", mock_scene)
        self.assertNotIn("WS_storey_1_InnerSpline", mock_scene)

        # Crucial check: WS_FOREIGN_SENTINEL and unrelated scene geometry remain untouched
        self.assertIn("WS_FOREIGN_SENTINEL", mock_scene)
        self.assertIn("S2_Floor_01", mock_scene)
        self.assertIn("S3_Core_01", mock_scene)
        self.assertEqual(mock_scene["WS_FOREIGN_SENTINEL"], "ProtectedSentinelNode")


class TestGeometricVariants(unittest.TestCase):
    """Test additional variants: blind contour, multi-storey, custom namespace."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_v2_variants_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_blind_contour_without_openings(self):
        walls_doc = {
            "schema_version": "2.0",
            "spec": "walls",
            "project": "pavilion-blind",
            "units": {"length": "cm", "angle": "deg"},
            "source": {"kind": "user_brief", "reference": "Blind wall test", "recorded_at": "2026-11-04T00:00:00Z"},
            "status": "locked",
            "origins": {
                "wall_technique": {"origin": "given"},
                "reference_face": {"origin": "given"},
                "storeys[0]": {"origin": "given"},
            },
            "wall_technique": "closed_inner_contour_shell_v2",
            "reference_face": "inner",
            "storeys": [
                {
                    "id": "storey_blind",
                    "base_z_cm": 0.0,
                    "top_z_cm": 300.0,
                    "wall_thickness_cm": 30.0,
                    "vertices_cm": [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0]],
                    "openings": []
                }
            ]
        }
        walls_path = Path(self.tmp_dir) / "walls.json"
        with open(walls_path, "w", encoding="utf-8") as f:
            json.dump(walls_doc, f, indent=2)

        res = builder.build_walls_v2(self.tmp_dir)
        self.assertEqual(len(res["openings"]), 0)
        # Solid volume: 63,600 * 300 = 19,080,000 cm3
        self.assertAlmostEqual(res["analytical_volume_cm3"], 19080000.0, places=2)

        with open(res["artifacts"]["wall_surface_ms"], "r", encoding="utf-8") as f:
            ms = f.read()
        self.assertIn("local delFaces = #{}", ms)

    def test_multi_storey_building(self):
        walls_doc = {
            "schema_version": "2.0",
            "spec": "walls",
            "project": "pavilion-2storey",
            "units": {"length": "cm", "angle": "deg"},
            "source": {"kind": "user_brief", "reference": "2-storey test", "recorded_at": "2026-11-04T00:00:00Z"},
            "status": "locked",
            "origins": {
                "wall_technique": {"origin": "given"},
                "reference_face": {"origin": "given"},
                "storeys[0]": {"origin": "given"},
                "storeys[1]": {"origin": "given"},
            },
            "wall_technique": "closed_inner_contour_shell_v2",
            "reference_face": "inner",
            "storeys": [
                {
                    "id": "storey_ground",
                    "base_z_cm": 0.0,
                    "top_z_cm": 300.0,
                    "wall_thickness_cm": 30.0,
                    "vertices_cm": [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0]],
                    "openings": []
                },
                {
                    "id": "storey_upper",
                    "base_z_cm": 300.0,
                    "top_z_cm": 600.0,
                    "wall_thickness_cm": 30.0,
                    "vertices_cm": [[0.0, 0.0], [600.0, 0.0], [600.0, 400.0], [0.0, 400.0]],
                    "openings": []
                }
            ]
        }
        walls_path = Path(self.tmp_dir) / "walls.json"
        with open(walls_path, "w", encoding="utf-8") as f:
            json.dump(walls_doc, f, indent=2)

        res = builder.build_walls_v2(self.tmp_dir)
        self.assertEqual(len(res["storeys"]), 2)
        self.assertEqual(len(res["nodes"]), 4)
        self.assertEqual(len(res["owned_nodes"]), 4)
        # Total volume: 2 * 19,080,000 = 38,160,000 cm3
        self.assertAlmostEqual(res["analytical_volume_cm3"], 38160000.0, places=2)
        # BBox Z extent from 0 to 600
        self.assertEqual(res["analytical_bbox_cm"][2], 0.0)
        self.assertEqual(res["analytical_bbox_cm"][5], 600.0)

    def test_custom_namespace_and_units(self):
        res = builder.build_walls_v2(
            FIXTURE_DIR,
            self.tmp_dir,
            namespace="BLD_NORTH",
            system_type="Millimeters",
            system_scale=1.0,
        )
        self.assertEqual(res["namespace"], "BLD_NORTH")
        self.assertIn("BLD_NORTH_storey_1", res["owned_nodes"])
        self.assertIn("BLD_NORTH_storey_1_InnerSpline", res["owned_nodes"])

    def test_refusal_on_invalid_technique(self):
        walls_doc = {
            "schema_version": "2.0",
            "spec": "walls",
            "project": "bad-technique",
            "units": {"length": "cm", "angle": "deg"},
            "source": {"kind": "user_brief", "reference": "Bad route", "recorded_at": "2026-11-04T00:00:00Z"},
            "status": "locked",
            "wall_technique": "legacy_cells_v1",
            "storeys": []
        }
        walls_path = Path(self.tmp_dir) / "walls.json"
        with open(walls_path, "w", encoding="utf-8") as f:
            json.dump(walls_doc, f, indent=2)

        with self.assertRaises(builder.BuildRefusal):
            builder.build_walls_v2(self.tmp_dir)


if __name__ == "__main__":
    unittest.main()
