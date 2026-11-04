#!/usr/bin/env python3
"""Phase 4 Verification Test Suite: Comprehensive Test Pavilion & S7 QA Assessment Gate.

Tests:
1. Pipeline End-to-End:
   - Slabs & roof elevations: base slab top Z=0, roof slab bottom Z=300.
   - Zero rough opening occlusion across all doors and windows.
   - Mechanism A: host facade walls are hidden in emitted assembly.ms.
   - Placements: G-81 zero modifiers, clearance & reveal math.
2. Analytical Volume Oracle:
   - Rectangular 600x400x300, t=30, 3 openings: exactly 17.022 m³ (17,022,000,000 mm³ in scene units).
   - Rotated pavilion (30° and 45°): rotation invariance of analytical volume.
   - L-shaped contour: analytical oracle volume formula (A_outer - A_inner)*H - openings_volume.
   - U-shaped contour: analytical oracle volume formula.
   - Unit factor scaling (cm vs mm vs m).
3. S7 QA Assess Mode:
   - Clean PASS across all checks (QA-V1-SOLID, QA-V1-TOPOLOGY, QA-V1-SURFACE,
     QA-V1-APERTURE, QA-V1-PLACEMENT, QA-V1-CENSUS, QA-V1-COVERAGE).
4. Strict Negative Controls (each MUST produce QA FAIL):
   - Non-positive / negative signed volume -> FAIL QA-V1-SOLID.
   - Evaluated volume mismatch vs oracle > tolerance -> FAIL QA-V1-SOLID.
   - Open edges > 0 (non-watertight) -> FAIL QA-V1-SOLID.
   - Modifiers count != 1 or mod != Shell -> FAIL QA-V1-TOPOLOGY.
   - Base class != Editable_Poly -> FAIL QA-V1-TOPOLOGY.
   - Duplicate vertices at corners or seam valence != 2 -> FAIL QA-V1-TOPOLOGY.
   - Inner contour deviation > tolerance -> FAIL QA-V1-SURFACE.
   - Host facade wall visible (occlusion / Mechanism A breach) -> FAIL QA-V1-APERTURE.
   - Placement clearances violated, hidden placement, or modifiers attached -> FAIL QA-V1-PLACEMENT.
5. Validator Integration:
   - validate_specs.py reports 0 FAIL, 0 WARN on specs/fixtures/v2-closed-shell-input.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import qa_check
import wall_contour_v2

FIXTURE_DIR = ROOT / "specs" / "fixtures" / "v2-closed-shell-input"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_base_valid_records(req_doc: dict) -> list[dict]:
    """Build synthetic valid wire records matching all 12 observations in qa-request.json."""
    obs_map = {obs["check_id"]: obs["id"] for obs in req_doc["observations"]}

    return [
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_COVERAGE"],
            "check_id": "CHK_COVERAGE",
            "target_id": "TGT_PROJECT",
            "sample_id": "Sec0df9a3d922e9c1791b52d470cb71da082d92917475032a6d3bf653f4c3e32",
            "status": "OK",
            "exists": True,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_SOLID"],
            "check_id": "CHK_SOLID",
            "target_id": "WS_storey_1",
            "sample_id": "S5986dcbe78a502f0743490cc51280d95c7064fe5c233bc09255f825f03a64a1",
            "status": "OK",
            "exists": True,
            "vol": 17022000.0,
            "signedVol": 17022000.0,
            "openEdges": 0,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_TOPOLOGY"],
            "check_id": "CHK_TOPOLOGY",
            "target_id": "WS_storey_1",
            "sample_id": "S158b65594b1eb55a2fdec2ac65e0c92971ce1dcb3870fcdf873c18f97951f7a",
            "status": "OK",
            "exists": True,
            "modCount": 1,
            "mod1Cls": "Shell",
            "baseCls": "Editable_Poly",
            "vol": 17022000.0,
            "signedVol": 17022000.0,
            "openEdges": 0,
            "dupVerts": 0,
            "seamValenceErr": 0,
            "tJunctions": 0,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_SURFACE"],
            "check_id": "CHK_SURFACE",
            "target_id": "WS_storey_1",
            "sample_id": "S695aae7c83731cfe2741253686be339d7ab06aae51c15ba5fb00c710c5da17c",
            "status": "OK",
            "exists": True,
            "maxYDev": 0.0,
            "vol": 17022000.0,
            "signedVol": 17022000.0,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_APERTURE_01"],
            "check_id": "CHK_APERTURE_01",
            "target_id": "PLC_001",
            "sample_id": "Saa12beec3285285e5111900e94ba5c3eba65428551b7e475d366459e834cf94",
            "status": "OK",
            "exists": True,
            "modCount": 0,
            "host_visible": False,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_APERTURE_02"],
            "check_id": "CHK_APERTURE_02",
            "target_id": "PLC_002",
            "sample_id": "S114142fa7b0bf5a3d236478df80bd6b0eab15f303696c9e4c88dfa5c67f474b",
            "status": "OK",
            "exists": True,
            "modCount": 0,
            "host_visible": False,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_APERTURE_03"],
            "check_id": "CHK_APERTURE_03",
            "target_id": "PLC_003",
            "sample_id": "Sb729969f43a2db1eb2c61cb1672f91cd827da3632683e6cc9b9f704fcddf26f",
            "status": "OK",
            "exists": True,
            "modCount": 0,
            "host_visible": False,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_PLACEMENT_01"],
            "check_id": "CHK_PLACEMENT_01",
            "target_id": "PLC_001",
            "sample_id": "Sd6cb76baba856021c993da8ed1b937a42ee82d4dbd8c0e1700c52680aa88f4e",
            "status": "OK",
            "exists": True,
            "modCount": 0,
            "isHidden": False,
            "pos": [150.0, -16.0, 0.0],
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_PLACEMENT_02"],
            "check_id": "CHK_PLACEMENT_02",
            "target_id": "PLC_002",
            "sample_id": "S2428b1df7e9a1aeabeb37c04ac81188b31e8441de12aaacef2fc103f42007a3",
            "status": "OK",
            "exists": True,
            "modCount": 0,
            "isHidden": False,
            "pos": [410.0, -16.0, 90.0],
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_PLACEMENT_03"],
            "check_id": "CHK_PLACEMENT_03",
            "target_id": "PLC_003",
            "sample_id": "S4d3618dad063cb95485ef2d8cc146d7dc0c3d60d74b372302b6c01526f401f6",
            "status": "OK",
            "exists": True,
            "modCount": 0,
            "isHidden": False,
            "pos": [616.0, 200.0, 110.0],
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_CENSUS_EL1"],
            "check_id": "CHK_CENSUS_EL1",
            "target_id": "EL_001",
            "sample_id": "S8d4fdc410d784ec6024764fdec3fd50e78f7d9917fac5d8100ba05c72e5f124",
            "status": "OK",
            "exists": True,
        },
        {
            "kind": "ROW",
            "observation_id": obs_map["CHK_CENSUS_EL2"],
            "check_id": "CHK_CENSUS_EL2",
            "target_id": "EL_002",
            "sample_id": "Se79496a55f46d5b2cc24f99499efb22aa63519a1ab8becf8a9bac971705e365",
            "status": "OK",
            "exists": True,
        },
    ]


class Test1_PipelineEndToEnd(unittest.TestCase):
    """Test 1: Slabs & roof elevations, Mechanism A, and zero-modifier placements."""

    def test_slab_and_roof_elevations(self):
        massing = load_json(FIXTURE_DIR / "massing.json")
        elements = {el["id"]: el for el in massing["elements"]}

        # Base slab EL-001 sits at Z in [-30.0, 0.0] cm
        self.assertIn("EL-001", elements)
        el1 = elements["EL-001"]
        self.assertEqual(el1["kind"], "slab")
        self.assertEqual(el1["z_range_cm"], [-30.0, 0.0])

        # Roof deck EL-002 sits at Z in [300.0, 330.0] cm
        self.assertIn("EL-002", elements)
        el2 = elements["EL-002"]
        self.assertEqual(el2["kind"], "roof_deck")
        self.assertEqual(el2["z_range_cm"], [300.0, 330.0])

        # Footprints match envelope [-30, -30] to [630, 430]
        expected_profile = [[-30.0, -30.0], [630.0, -30.0], [630.0, 430.0], [-30.0, 430.0]]
        self.assertEqual(el1["profile_cm"], expected_profile)
        self.assertEqual(el2["profile_cm"], expected_profile)

    def test_zero_rough_opening_occlusion(self):
        ws = load_json(FIXTURE_DIR / "wall_surface.json")
        openings = ws.get("openings", [])
        self.assertEqual(len(openings), 3)

        # Base slab top is Z = 0.0 cm; Roof deck bottom is Z = 300.0 cm
        base_slab_top = 0.0
        roof_deck_bottom = 300.0

        for op in openings:
            op_id = op.get("opening_id") or op.get("id")
            vb = op.get("vertical_bounds", {})
            sill = float(vb.get("sill_z_cm", op.get("sill_cm", 0.0)))
            head = float(vb.get("head_z_cm", op.get("head_cm", 0.0)))

            # Sill must be at or above base slab top (flush with door sill at Z=0.0)
            self.assertGreaterEqual(
                sill,
                base_slab_top,
                f"Opening {op_id} sill {sill} is below base slab top {base_slab_top}",
            )

            # Head must be strictly below roof deck bottom (zero occlusion)
            self.assertLessEqual(
                head,
                roof_deck_bottom,
                f"Opening {op_id} head {head} collides with roof deck bottom {roof_deck_bottom}",
            )
            # Minimum clear headroom above opening
            head_clearance = roof_deck_bottom - head
            self.assertGreaterEqual(
                head_clearance,
                60.0,
                f"Opening {op_id} has insufficient clearance to roof deck: {head_clearance} cm",
            )

    def test_mechanism_a_host_walls_hidden(self):
        ms_text = (FIXTURE_DIR / "assembly.ms").read_text(encoding="utf-8")

        # Mechanism A hides host facade walls
        self.assertIn("host_nd.isHidden = true", ms_text)
        # Component prototypes are hidden
        self.assertIn("PROTO_DOOR_01_1.isHidden = true", ms_text)
        self.assertIn("PROTO_COMP_WINDOW_2.isHidden = true", ms_text)
        self.assertIn("PROTO_COMP_WINDOW_3.isHidden = true", ms_text)

    def test_g81_zero_modifiers_and_placements(self):
        ms_text = (FIXTURE_DIR / "assembly.ms").read_text(encoding="utf-8")
        asm = load_json(FIXTURE_DIR / "assembly.json")

        # G-81 zero modifiers
        self.assertNotIn("addModifier", ms_text)
        self.assertNotIn("formattedPrint", ms_text)

        # 3 placements
        placements = asm.get("placements", [])
        self.assertEqual(len(placements), 3)

        # Clearance and reveal math
        # OP-001 (door): rough 100x210, cl_sides=1.0, cl_top=1.0, cl_bottom=0.0 -> 98x12x209
        p1 = placements[0]
        self.assertEqual(p1["component_id"], "DOOR-01")
        self.assertEqual(p1["size_cm"], [98.0, 12.0, 209.0])
        self.assertEqual(p1["position_cm"], [150.0, -16.0, 0.0])

        # OP-002 (window): rough 180x120, cl_sides=1.0, cl_top=1.0, cl_bottom=1.0 -> 178x12x119
        p2 = placements[1]
        self.assertEqual(p2["component_id"], "COMP_WINDOW")
        self.assertEqual(p2["size_cm"], [178.0, 12.0, 119.0])
        self.assertEqual(p2["position_cm"], [410.0, -16.0, 90.0])

        # OP-003 (window): rough 200x130, cl_sides=1.0, cl_top=1.0, cl_bottom=1.0 -> 198x12x129
        p3 = placements[2]
        self.assertEqual(p3["component_id"], "COMP_WINDOW")
        self.assertEqual(p3["size_cm"], [198.0, 12.0, 129.0])
        self.assertEqual(p3["position_cm"], [616.0, 200.0, 110.0])


class Test2_AnalyticalVolumeOracle(unittest.TestCase):
    """Test 2: Analytical volume oracle across geometric variants and unit scaling."""

    def test_rectangular_volume_oracle(self):
        walls = load_json(FIXTURE_DIR / "walls.json")
        ws = load_json(FIXTURE_DIR / "wall_surface.json")
        asm = load_json(FIXTURE_DIR / "assumptions.json")

        v_cm3 = qa_check.compute_closed_contour_analytical_volume(walls, ws, asm)
        # Expected: (303600 - 240000) * 300 - (630000 + 648000 + 780000) = 17,022,000 cm³
        self.assertAlmostEqual(v_cm3, 17022000.0, places=2)
        v_m3 = v_cm3 / 1e6
        self.assertAlmostEqual(v_m3, 17.022, places=4)
        v_mm3 = v_cm3 * 1000.0
        self.assertAlmostEqual(v_mm3, 17022000000.0, places=0)

    def test_rotation_invariance(self):
        walls = load_json(FIXTURE_DIR / "walls.json")
        orig_pts = walls["storeys"][0]["vertices_cm"]

        for deg in (30.0, 45.0, 90.0):
            rad = math.radians(deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            rot_pts = [
                [p[0] * cos_a - p[1] * sin_a, p[0] * sin_a + p[1] * cos_a]
                for p in orig_pts
            ]
            w_copy = copy.deepcopy(walls)
            w_copy["storeys"][0]["vertices_cm"] = rot_pts

            v_rot = qa_check.compute_closed_contour_analytical_volume(w_copy)
            self.assertAlmostEqual(v_rot, 17022000.0, delta=0.01)

    def test_l_shaped_contour_volume(self):
        # L-shaped polygon: A_in = 180,000 cm², offset 30 -> A_out = 243,600 cm²
        l_pts = [
            (0.0, 0.0),
            (600.0, 0.0),
            (600.0, 200.0),
            (300.0, 200.0),
            (300.0, 400.0),
            (0.0, 400.0),
        ]
        norm = wall_contour_v2.normalize_contour_ccw(l_pts)
        res = wall_contour_v2.safe_contour_offset(norm.vertices, 30.0, reference_face="inner")

        def shoelace_area(pts):
            n = len(pts)
            a = 0.0
            for i in range(n):
                j = (i + 1) % n
                a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
            return abs(a) / 2.0

        a_in = shoelace_area(l_pts)
        a_out = shoelace_area(res.outer_vertices)
        self.assertAlmostEqual(a_in, 180000.0, places=2)
        self.assertAlmostEqual(a_out, 243600.0, places=2)

        h = 300.0
        v_solid = (a_out - a_in) * h
        # One opening 100x210x30 = 630,000 cm³
        v_open = 100.0 * 210.0 * 30.0
        expected_net_vol = v_solid - v_open

        doc = {
            "storeys": [
                {
                    "id": "storey_1",
                    "base_z_cm": 0.0,
                    "top_z_cm": 300.0,
                    "wall_thickness_cm": 30.0,
                    "vertices_cm": l_pts,
                    "openings": [
                        {
                            "id": "OP-001",
                            "s_range_cm": [100.0, 200.0],
                            "sill_cm": 0.0,
                            "head_cm": 210.0,
                        }
                    ],
                }
            ]
        }
        computed = qa_check.compute_closed_contour_analytical_volume(doc)
        self.assertAlmostEqual(computed, expected_net_vol, places=2)

    def test_u_shaped_contour_volume(self):
        u_pts = [
            (0.0, 0.0),
            (600.0, 0.0),
            (600.0, 400.0),
            (400.0, 400.0),
            (400.0, 200.0),
            (200.0, 200.0),
            (200.0, 400.0),
            (0.0, 400.0),
        ]
        norm = wall_contour_v2.normalize_contour_ccw(u_pts)
        res = wall_contour_v2.safe_contour_offset(norm.vertices, 30.0, reference_face="inner")

        def shoelace_area(pts):
            n = len(pts)
            a = 0.0
            for i in range(n):
                j = (i + 1) % n
                a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
            return abs(a) / 2.0

        a_in = shoelace_area(u_pts)
        a_out = shoelace_area(res.outer_vertices)
        self.assertAlmostEqual(a_in, 200000.0, places=2)
        self.assertAlmostEqual(a_out, 275600.0, places=2)

        h = 300.0
        v_solid = (a_out - a_in) * h
        v_open = 100.0 * 210.0 * 30.0
        expected_net_vol = v_solid - v_open

        doc = {
            "storeys": [
                {
                    "id": "storey_1",
                    "base_z_cm": 0.0,
                    "top_z_cm": 300.0,
                    "wall_thickness_cm": 30.0,
                    "vertices_cm": u_pts,
                    "openings": [
                        {
                            "id": "OP-001",
                            "s_range_cm": [100.0, 200.0],
                            "sill_cm": 0.0,
                            "head_cm": 210.0,
                        }
                    ],
                }
            ]
        }
        computed = qa_check.compute_closed_contour_analytical_volume(doc)
        self.assertAlmostEqual(computed, expected_net_vol, places=2)

    def test_unit_factor_scaling(self):
        v_cm3 = 17022000.0

        # Millimeters: f_unit = 10.0 -> f_vol = 1000.0
        f_vol_mm = 10.0 ** 3
        self.assertEqual(v_cm3 * f_vol_mm, 17022000000.0)

        # Meters: f_unit = 0.01 -> f_vol = 1e-6
        f_vol_m = 0.01 ** 3
        self.assertAlmostEqual(v_cm3 * f_vol_m, 17.022, places=6)

        # Centimeters: f_unit = 1.0 -> f_vol = 1.0
        f_vol_cm = 1.0 ** 3
        self.assertEqual(v_cm3 * f_vol_cm, 17022000.0)


class Test3_S7QACheckAssessMode(unittest.TestCase):
    """Test 3: S7 QA Assess Mode on valid captured responses."""

    def test_clean_pass_across_all_checks(self):
        req_path = FIXTURE_DIR / "runs" / "qa-001" / "qa-request.json"
        req_doc = load_json(req_path)
        valid_records = get_base_valid_records(req_doc)

        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            res_file = tpath / "results.json"
            with open(res_file, "w", encoding="utf-8") as f:
                json.dump({"records": valid_records}, f, indent=2)

            rc = qa_check.run_assess_mode(
                in_path=FIXTURE_DIR,
                request_path=req_path,
                results_path=res_file,
                out_dir=tpath,
                json_mode=True,
            )
            self.assertEqual(rc, 0)

            results_doc = load_json(tpath / "qa-results.json")
            self.assertEqual(results_doc["verdict"], "PASS")
            self.assertEqual(results_doc["summary"]["failed"], 0)
            self.assertEqual(results_doc["summary"]["passed"], 12)

            # Verify every check passed cleanly
            expected_checks = [
                "CHK_SOLID",
                "CHK_TOPOLOGY",
                "CHK_SURFACE",
                "CHK_APERTURE_01",
                "CHK_APERTURE_02",
                "CHK_APERTURE_03",
                "CHK_PLACEMENT_01",
                "CHK_PLACEMENT_02",
                "CHK_PLACEMENT_03",
                "CHK_CENSUS_EL1",
                "CHK_CENSUS_EL2",
                "CHK_COVERAGE",
            ]
            for c_id in expected_checks:
                c_data = results_doc["checks"].get(c_id)
                self.assertIsNotNone(c_data, f"Check {c_id} missing from results")
                self.assertEqual(c_data["status"], "PASS", f"Check {c_id} did not pass: {c_data.get('errors')}")


class Test4_StrictNegativeControls(unittest.TestCase):
    """Test 4: Strict negative controls - each MUST produce QA FAIL."""

    def setUp(self):
        self.req_path = FIXTURE_DIR / "runs" / "qa-001" / "qa-request.json"
        self.req_doc = load_json(self.req_path)

    def _run_with_mutated_records(self, mutator_fn) -> tuple[int, dict]:
        records = get_base_valid_records(self.req_doc)
        mutator_fn(records)
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            res_file = tpath / "results.json"
            with open(res_file, "w", encoding="utf-8") as f:
                json.dump({"records": records}, f, indent=2)

            rc = qa_check.run_assess_mode(
                in_path=FIXTURE_DIR,
                request_path=self.req_path,
                results_path=res_file,
                out_dir=tpath,
                json_mode=True,
            )
            results_doc = load_json(tpath / "qa-results.json")
            return rc, results_doc

    def test_fail_solid_non_positive_volume(self):
        def mutate(recs):
            recs[1]["vol"] = 0.0

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_SOLID"]["status"], "FAIL")
        self.assertTrue(any("non-positive" in e for e in doc["checks"]["CHK_SOLID"]["errors"]))

    def test_fail_solid_negative_signed_volume(self):
        def mutate(recs):
            recs[1]["signedVol"] = -17022000.0

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_SOLID"]["status"], "FAIL")
        self.assertTrue(any("non-positive" in e for e in doc["checks"]["CHK_SOLID"]["errors"]))

    def test_fail_solid_volume_mismatch_vs_oracle(self):
        def mutate(recs):
            # Volume deviates from oracle by 2,022,000 cm³ (tolerance is 50,000 cm³)
            recs[1]["vol"] = 15000000.0
            recs[1]["signedVol"] = 15000000.0

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_SOLID"]["status"], "FAIL")
        self.assertTrue(any("deviates from analytical oracle" in e for e in doc["checks"]["CHK_SOLID"]["errors"]))

    def test_fail_solid_open_edges_non_watertight(self):
        def mutate(recs):
            recs[1]["openEdges"] = 4

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_SOLID"]["status"], "FAIL")
        self.assertTrue(any("not watertight: open edges count is 4" in e for e in doc["checks"]["CHK_SOLID"]["errors"]))

    def test_fail_topology_modifier_stack_not_single_shell(self):
        def mutate(recs):
            recs[2]["modCount"] = 2
            recs[2]["mod1Cls"] = "Edit_Poly"

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_TOPOLOGY"]["status"], "FAIL")
        self.assertTrue(any("invalid modifier stack" in e for e in doc["checks"]["CHK_TOPOLOGY"]["errors"]))

    def test_fail_topology_base_class_not_editable_poly(self):
        def mutate(recs):
            recs[2]["baseCls"] = "Editable_Mesh"

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_TOPOLOGY"]["status"], "FAIL")
        self.assertTrue(any("is not Editable_Poly" in e for e in doc["checks"]["CHK_TOPOLOGY"]["errors"]))

    def test_fail_topology_duplicate_vertices_or_seam_valence(self):
        # Test duplicate vertices
        def mutate_dup(recs):
            recs[2]["dupVerts"] = 2

        rc, doc = self._run_with_mutated_records(mutate_dup)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_TOPOLOGY"]["status"], "FAIL")
        self.assertTrue(any("duplicate vertices" in e for e in doc["checks"]["CHK_TOPOLOGY"]["errors"]))

        # Test seam valence != 2
        def mutate_seam(recs):
            recs[2]["seamValenceErr"] = 1

        rc, doc = self._run_with_mutated_records(mutate_seam)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_TOPOLOGY"]["status"], "FAIL")
        self.assertTrue(any("seam edges with valence != 2" in e for e in doc["checks"]["CHK_TOPOLOGY"]["errors"]))

    def test_fail_surface_inner_contour_deviation(self):
        def mutate(recs):
            recs[3]["maxYDev"] = 0.12  # exceeds 0.05 cm tolerance

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_SURFACE"]["status"], "FAIL")
        self.assertTrue(any("inner face deviation" in e for e in doc["checks"]["CHK_SURFACE"]["errors"]))

    def test_fail_aperture_mechanism_a_breach_host_visible(self):
        def mutate(recs):
            # Aperture target observes host wall is visible
            recs[4]["host_visible"] = True

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_APERTURE_01"]["status"], "FAIL")
        self.assertTrue(any("Mechanism A breach" in e for e in doc["checks"]["CHK_APERTURE_01"]["errors"]))

    def test_fail_placement_modifiers_attached_g81_breach(self):
        def mutate(recs):
            # Placement node has a modifier attached (G-81 breach)
            recs[7]["modCount"] = 1

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_PLACEMENT_01"]["status"], "FAIL")
        self.assertTrue(any("G-81 zero-modifier rule" in e for e in doc["checks"]["CHK_PLACEMENT_01"]["errors"]))

    def test_fail_placement_hidden(self):
        def mutate(recs):
            # Placement node is marked isHidden=True
            recs[7]["isHidden"] = True

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_PLACEMENT_01"]["status"], "FAIL")
        self.assertTrue(any("Placement node PLC_001 is hidden" in e for e in doc["checks"]["CHK_PLACEMENT_01"]["errors"]))

    def test_fail_placement_position_deviation(self):
        def mutate(recs):
            # Position deviates by 10 cm (linear tolerance is 0.5 cm)
            recs[7]["pos"] = [160.0, -16.0, 0.0]

        rc, doc = self._run_with_mutated_records(mutate)
        self.assertEqual(rc, 1)
        self.assertEqual(doc["verdict"], "FAIL")
        self.assertEqual(doc["checks"]["CHK_PLACEMENT_01"]["status"], "FAIL")
        self.assertTrue(any("position deviation" in e for e in doc["checks"]["CHK_PLACEMENT_01"]["errors"]))


class Test5_FixtureValidatorIntegration(unittest.TestCase):
    """Test 5: Validator integration on specs/fixtures/v2-closed-shell-input."""

    def test_fixture_validation_zero_fail_zero_warn(self):
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "validate_specs.py"),
            "--dir",
            str(FIXTURE_DIR),
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Validator failed:\n{res.stderr}\n{res.stdout}")

        report = json.loads(res.stdout)
        summary = report.get("summary", {})
        self.assertEqual(summary.get("FAIL", 0), 0)
        self.assertEqual(summary.get("WARN", 0), 0)
        self.assertGreater(summary.get("PASS", 0), 100)


if __name__ == "__main__":
    unittest.main()
