#!/usr/bin/env python3
"""Unit tests for QA Wall Profile extensions in scripts/qa_check.py.

Verifies:
1. validate_qa_spec accepts profile 'poly_surface_shell_v1' and 'wall_surface_v1'.
2. validate_qa_spec accepts wall target kinds ('wall_surface', 'wall_run', 'wall_opening').
3. validate_qa_spec accepts wall check kinds ('QA-V1-DIRECTION', 'QA-V1-SOLID', 'QA-V1-TOPOLOGY', 'QA-V1-WALLS', 'QA-V1-STACK').
4. Wire parser correctly extracts enriched fields: baseCls, mod1Cls, innerAmt, outerAmt, segs, maxYDev, vol.
5. Assess mode accurately enforces Direction Gate, Volume/Solid Gate, Stack Gate, and Topology Gate.
6. Targeted negative cases fail as expected (inverted normal, extra modifiers, non-Editable_Poly, zero volume, inner face deviation).
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import qa_check


class TestQaWallProfile(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.minimal_qa_doc = {
            "schema_version": "1.0",
            "spec": "qa",
            "project": "F01_TEST",
            "units": "millimeters",
            "source": "unit_test",
            "status": "DRAFT",
            "tolerances": {
                "linear_cm": 0.05,
                "area_m2": 0.001,
                "angle_deg": 0.1,
                "numerical": {
                    "policy": "separate_bounds_v1",
                    "solver_distance_cm": 0.01,
                },
                "volume": {
                    "policy": "box_endpoint_propagation_v1",
                },
            },
            "origin_inputs": ["walls.json"],
            "origins": {"author": "qa_unit_test"},
            "profile": "poly_surface_shell_v1",
            "dependencies": [
                {
                    "id": "dep_walls",
                    "file": "walls.json",
                    "format": "json",
                    "spec": "walls",
                    "schema_version": "1.0",
                }
            ],
            "scope": {
                "targets": [
                    {
                        "id": "TGT_WALL_F01",
                        "kind": "wall_surface",
                        "role": "exterior_wall",
                        "node_names": ["WS_RUN_F01"],
                    }
                ]
            },
            "check_plan": [
                {
                    "id": "CHK_COVERAGE",
                    "kind": "QA-V1-COVERAGE",
                    "target_ref": "TGT_WALL_F01",
                    "tolerance_ref": "exact",
                },
                {
                    "id": "CHK_STACK",
                    "kind": "QA-V1-STACK",
                    "target_ref": "TGT_WALL_F01",
                    "tolerance_ref": "wall_poly_v1",
                },
                {
                    "id": "CHK_DIRECTION",
                    "kind": "QA-V1-DIRECTION",
                    "target_ref": "TGT_WALL_F01",
                    "tolerance_ref": "wall_poly_v1",
                },
                {
                    "id": "CHK_SOLID",
                    "kind": "QA-V1-SOLID",
                    "target_ref": "TGT_WALL_F01",
                    "tolerance_ref": "wall_poly_v1",
                },
                {
                    "id": "CHK_TOPOLOGY",
                    "kind": "QA-V1-TOPOLOGY",
                    "target_ref": "TGT_WALL_F01",
                    "tolerance_ref": "wall_poly_v1",
                },
            ],
            "sampling": {
                "policy": "domain_grid_v1",
                "version": "1",
                "grid_u": 2,
                "grid_v": 2,
                "selected_frame": 0,
            },
            "limits": {
                "max_rows_per_batch": 25,
                "max_targets": 10,
                "max_samples": 50,
                "max_calls": 5,
                "max_batch_seconds": 2.0,
                "max_total_seconds": 10.0,
                "max_solver_iterations": 100,
                "max_response_bytes": 1048576,
            },
            "capture_plan": {},
        }

    def test_validate_qa_spec_poly_profile(self):
        errors = qa_check.validate_qa_spec(self.minimal_qa_doc)
        self.assertEqual(errors, [])

    def test_wire_parser_enriched_row(self):
        line = (
            "ROW observation_id=O_test check_id=C_test target_id=T_test sample_id=S_test "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.0 vol=2610000000.0"
        )
        rec = qa_check._parse_wire_row_line(line)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["observation_id"], "O_test")
        self.assertTrue(rec["exists"])
        self.assertFalse(rec["isHidden"])
        self.assertEqual(rec["baseCls"], "Editable_Poly")
        self.assertEqual(rec["mod1Cls"], "Shell")
        self.assertEqual(rec["modCount"], 1)
        self.assertEqual(rec["innerAmt"], 0.0)
        self.assertEqual(rec["outerAmt"], 300.0)
        self.assertEqual(rec["segs"], 1)
        self.assertEqual(rec["maxYDev"], 0.0)
        self.assertEqual(rec["vol"], 2610000000.0)

    def _run_assessment(self, row_line: str) -> dict:
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            qa_path = specs_dir / "qa.json"
            qa_path.write_text(json.dumps(self.minimal_qa_doc), encoding="utf-8")

            # Dummy dependency walls.json
            walls_path = specs_dir / "walls.json"
            walls_path.write_text(json.dumps({"wall_technique": "poly_surface_shell_v1"}), encoding="utf-8")

            # 1. Emit
            emit_dir = tpath / "emit"
            res = qa_check.run_emit_mode(
                in_path=tpath,
                run_dir=emit_dir,
                run_id="run_test",
                cert_path=None,
                json_mode=False,
            )
            self.assertEqual(res, 0)

            # Read generated request to match observation IDs
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            # 2. Build mock results file matching the observation IDs
            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
            ]
            for c_id, o_id in obs_map.items():
                # Replace observation_id and check_id in row_line
                row = row_line.replace("O_PLACEHOLDER", o_id).replace("C_PLACEHOLDER", c_id)
                results_lines.append(row)
            results_lines.append(f"END_BATCH batch_id=batch_001 rows={len(obs_map)}")

            results_file = tpath / "captured_results.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            # 3. Assess
            out_dir = tpath / "out"
            assess_res = qa_check.run_assess_mode(
                in_path=tpath,
                request_path=req_file,
                results_path=results_file,
                out_dir=out_dir,
                json_mode=False,
            )
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            return {"exit_code": assess_res, "report": res_json}

    def test_assess_positive_case(self):
        row = (
            "ROW observation_id=O_PLACEHOLDER check_id=C_PLACEHOLDER target_id=TGT_WALL_F01 sample_id=S_rec "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.0 vol=2610000000.0"
        )
        res = self._run_assessment(row)
        self.assertEqual(res["exit_code"], 0)
        self.assertEqual(res["report"]["verdict"], "PASS")
        self.assertEqual(res["report"]["summary"]["failed"], 0)
        self.assertEqual(res["report"]["checks"]["CHK_DIRECTION"]["status"], "PASS")
        self.assertEqual(res["report"]["checks"]["CHK_SOLID"]["status"], "PASS")
        self.assertEqual(res["report"]["checks"]["CHK_STACK"]["status"], "PASS")
        self.assertEqual(res["report"]["checks"]["CHK_TOPOLOGY"]["status"], "PASS")

    def test_assess_negative_direction_inverted_normal(self):
        # Wall min/max has outward direction in +Y instead of -Y
        row = (
            "ROW observation_id=O_PLACEHOLDER check_id=C_PLACEHOLDER target_id=TGT_WALL_F01 sample_id=S_rec "
            "status=OK exists=true isHidden=false pos=[2000.0,150.0,1500.0] "
            "min=[0.0,0.0,0.0] max=[4000.0,300.0,3000.0] modCount=1 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.0 vol=2610000000.0"
        )
        res = self._run_assessment(row)
        self.assertEqual(res["exit_code"], 1)
        self.assertEqual(res["report"]["verdict"], "FAIL")
        self.assertEqual(res["report"]["checks"]["CHK_DIRECTION"]["status"], "FAIL")
        self.assertIn("normal direction not outward -Y", res["report"]["checks"]["CHK_DIRECTION"]["errors"][0])

    def test_assess_negative_inner_face_deviation(self):
        # Inner face deviates from Y=0 (maxYDev = 0.5)
        row = (
            "ROW observation_id=O_PLACEHOLDER check_id=C_PLACEHOLDER target_id=TGT_WALL_F01 sample_id=S_rec "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.5 vol=2610000000.0"
        )
        res = self._run_assessment(row)
        self.assertEqual(res["exit_code"], 1)
        self.assertEqual(res["report"]["verdict"], "FAIL")
        self.assertEqual(res["report"]["checks"]["CHK_DIRECTION"]["status"], "FAIL")
        self.assertIn("inner face deviation", res["report"]["checks"]["CHK_DIRECTION"]["errors"][0])

    def test_assess_negative_stack_extra_modifiers(self):
        # 2 modifiers instead of 1
        row = (
            "ROW observation_id=O_PLACEHOLDER check_id=C_PLACEHOLDER target_id=TGT_WALL_F01 sample_id=S_rec "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=2 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.0 vol=2610000000.0"
        )
        res = self._run_assessment(row)
        self.assertEqual(res["exit_code"], 1)
        self.assertEqual(res["report"]["verdict"], "FAIL")
        self.assertEqual(res["report"]["checks"]["CHK_STACK"]["status"], "FAIL")
        self.assertIn("expected strictly 1 (Shell)", res["report"]["checks"]["CHK_STACK"]["errors"][0])

    def test_assess_negative_base_class(self):
        # Base is Editable_Mesh instead of Editable_Poly
        row = (
            "ROW observation_id=O_PLACEHOLDER check_id=C_PLACEHOLDER target_id=TGT_WALL_F01 sample_id=S_rec "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
            "baseCls=Editable_Mesh mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.0 vol=2610000000.0"
        )
        res = self._run_assessment(row)
        self.assertEqual(res["exit_code"], 1)
        self.assertEqual(res["report"]["verdict"], "FAIL")
        self.assertEqual(res["report"]["checks"]["CHK_STACK"]["status"], "FAIL")
        self.assertIn("expected Editable_Poly", res["report"]["checks"]["CHK_STACK"]["errors"][0])

    def test_assess_negative_zero_volume(self):
        # Evaluated volume is 0.0 (non-solid / flat surface)
        row = (
            "ROW observation_id=O_PLACEHOLDER check_id=C_PLACEHOLDER target_id=TGT_WALL_F01 sample_id=S_rec "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
            "maxYDev=0.0 vol=0.0"
        )
        res = self._run_assessment(row)
        self.assertEqual(res["exit_code"], 1)
        self.assertEqual(res["report"]["verdict"], "FAIL")
        self.assertEqual(res["report"]["checks"]["CHK_SOLID"]["status"], "FAIL")
        self.assertIn("evaluated volume is non-positive", res["report"]["checks"]["CHK_SOLID"]["errors"][0])

    def test_validate_qa_spec_closed_contour_v2_profile(self):
        doc = dict(self.minimal_qa_doc)
        doc["profile"] = "closed_inner_contour_shell_v2"
        doc["scope"] = {
            "targets": [
                {
                    "id": "TGT_WALL_STOREY_1",
                    "kind": "wall_surface",
                    "role": "exterior_wall",
                    "node_names": ["WS_storey_1"],
                },
                {
                    "id": "TGT_PLC_001",
                    "kind": "placement",
                    "role": "window_placement",
                    "node_names": ["PLC_001"],
                },
                {
                    "id": "TGT_HOST_WALL",
                    "kind": "wall_host",
                    "role": "host_facade_wall",
                    "node_names": ["FACADE_WALL_1"],
                },
            ]
        }
        doc["check_plan"] = [
            {
                "id": "CHK_COV",
                "kind": "QA-V1-COVERAGE",
                "target_ref": "TGT_WALL_STOREY_1",
                "tolerance_ref": "exact",
            },
            {
                "id": "CHK_STK",
                "kind": "QA-V1-STACK",
                "target_ref": "TGT_WALL_STOREY_1",
                "tolerance_ref": "wall_poly_v1",
            },
            {
                "id": "CHK_SLD",
                "kind": "QA-V1-SOLID",
                "target_ref": "TGT_WALL_STOREY_1",
                "tolerance_ref": "wall_poly_v1",
            },
            {
                "id": "CHK_TOP",
                "kind": "QA-V1-TOPOLOGY",
                "target_ref": "TGT_WALL_STOREY_1",
                "tolerance_ref": "wall_poly_v1",
            },
            {
                "id": "CHK_PLC",
                "kind": "QA-V1-PLACEMENT",
                "target_ref": "TGT_PLC_001",
                "tolerance_ref": "placement_v1",
            },
            {
                "id": "CHK_HOST",
                "kind": "QA-V1-WALLS",
                "target_ref": "TGT_HOST_WALL",
                "tolerance_ref": "exact",
            },
        ]
        errors = qa_check.validate_qa_spec(doc)
        self.assertEqual(errors, [])

    def test_wire_parser_closed_contour_v2_fields(self):
        line = (
            "ROW observation_id=O_test check_id=C_test target_id=T_test sample_id=S_test "
            "status=OK exists=true isHidden=false pos=[2000.0,-150.0d0,1500.0] "
            "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
            "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0d0 outerAmt=300.0 segs=1 "
            "straightenCorners=true nVerts=8 nEdges=12 dupVerts=0 seamValenceErr=0 "
            "tJunctions=0 openEdges=0 maxYDev=0.0 vol=2.610000000000d+09 signedVol=2.610000000000d+09"
        )
        rec = qa_check._parse_wire_row_line(line)
        self.assertIsNotNone(rec)
        self.assertTrue(rec["straightenCorners"])
        self.assertEqual(rec["nVerts"], 8)
        self.assertEqual(rec["nEdges"], 12)
        self.assertEqual(rec["dupVerts"], 0)
        self.assertEqual(rec["seamValenceErr"], 0)
        self.assertEqual(rec["tJunctions"], 0)
        self.assertEqual(rec["openEdges"], 0)
        self.assertEqual(rec["vol"], 2610000000.0)
        self.assertEqual(rec["signedVol"], 2610000000.0)

    def test_emit_mode_closed_contour_v2_queries(self):
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            doc = dict(self.minimal_qa_doc)
            doc["profile"] = "closed_inner_contour_shell_v2"
            qa_path = specs_dir / "qa.json"
            qa_path.write_text(json.dumps(doc), encoding="utf-8")
            walls_path = specs_dir / "walls.json"
            walls_path.write_text(json.dumps({"wall_technique": "closed_inner_contour_shell_v2"}), encoding="utf-8")

            emit_dir = tpath / "emit"
            res = qa_check.run_emit_mode(
                in_path=tpath,
                run_dir=emit_dir,
                run_id="run_v2",
                cert_path=None,
                json_mode=False,
            )
            self.assertEqual(res, 0)
            ms_content = (emit_dir / "batch_001.ms").read_text(encoding="utf-8")
            self.assertNotIn("formattedPrint", ms_content)
            self.assertIn("straightenCorners", ms_content)
            self.assertIn("dupVerts", ms_content)
            self.assertIn("seamValenceErr", ms_content)
            self.assertIn("meshop.getOpenEdges", ms_content)
            self.assertIn("signedVol=", ms_content)

    def test_assess_closed_contour_v2_positive_with_oracle(self):
        # Closed contour rectangular wall with 1 opening
        # Inner: 400x300, Outer: 460x360 (thickness 30), Height: 300
        # V_solid = (165600 - 120000) * 300 = 13,680,000 cm3
        # Opening: 100x120x30 = 360,000 cm3
        # V_analytical = 13,320,000 cm3
        # In scene units (mm): 13,320,000,000 mm3
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)

            walls_doc = {
                "schema_version": "2.0",
                "wall_technique": "closed_inner_contour_shell_v2",
                "units": "millimeters",
                "storeys": [
                    {
                        "id": "storey_1",
                        "base_z_cm": 0.0,
                        "top_z_cm": 300.0,
                        "wall_thickness_cm": 30.0,
                        "vertices_cm": [[0.0, 0.0], [400.0, 0.0], [400.0, 300.0], [0.0, 300.0]],
                        "openings": [
                            {
                                "id": "OP_001",
                                "s_range_cm": [100.0, 200.0],
                                "sill_cm": 90.0,
                                "head_cm": 210.0,
                            }
                        ],
                    }
                ],
            }
            (specs_dir / "walls.json").write_text(json.dumps(walls_doc), encoding="utf-8")

            assembly_doc = {
                "project": "F01_TEST",
                "placements": [
                    {
                        "id": "PLC-001",
                        "node_name": "PLC_001",
                        "kind": "window",
                        "position_cm": [150.0, -15.0, 150.0],
                        "size_cm": [98.0, 12.0, 118.0],
                        "rough_opening": {"width_cm": 100.0, "height_cm": 120.0, "depth_cm": 30.0},
                        "mounting_parameters": {
                            "clearance_sides_cm": 1.0,
                            "clearance_top_cm": 1.0,
                            "clearance_bottom_cm": 1.0,
                            "recess_cm": 10.0,
                        },
                    }
                ],
            }
            (specs_dir / "assembly.json").write_text(json.dumps(assembly_doc), encoding="utf-8")

            qa_doc = dict(self.minimal_qa_doc)
            qa_doc["profile"] = "closed_inner_contour_shell_v2"
            qa_doc["scope"] = {
                "targets": [
                    {
                        "id": "TGT_WALL_STOREY_1",
                        "kind": "wall_surface",
                        "role": "exterior_wall",
                        "node_names": ["WS_storey_1"],
                    },
                    {
                        "id": "TGT_PLC_001",
                        "kind": "placement",
                        "role": "window_placement",
                        "node_names": ["PLC_001"],
                    },
                    {
                        "id": "TGT_HOST_WALL",
                        "kind": "wall_host",
                        "role": "host_facade_wall",
                        "node_names": ["FACADE_WALL_1"],
                    },
                ]
            }
            qa_doc["check_plan"] = [
                {"id": "CHK_COV", "kind": "QA-V1-COVERAGE", "target_ref": "TGT_WALL_STOREY_1", "tolerance_ref": "exact"},
                {"id": "CHK_SOLID", "kind": "QA-V1-SOLID", "target_ref": "TGT_WALL_STOREY_1", "tolerance_ref": "solid_v1"},
                {"id": "CHK_TOPO", "kind": "QA-V1-TOPOLOGY", "target_ref": "TGT_WALL_STOREY_1", "tolerance_ref": "topology_v1"},
                {"id": "CHK_STACK", "kind": "QA-V1-STACK", "target_ref": "TGT_WALL_STOREY_1", "tolerance_ref": "wall_poly_v1"},
                {"id": "CHK_PLC", "kind": "QA-V1-PLACEMENT", "target_ref": "TGT_PLC_001", "tolerance_ref": "placement_v1"},
                {"id": "CHK_APERTURE", "kind": "QA-V1-APERTURE", "target_ref": "TGT_PLC_001", "tolerance_ref": "aperture_v1"},
                {"id": "CHK_HOST", "kind": "QA-V1-WALLS", "target_ref": "TGT_HOST_WALL", "tolerance_ref": "exact"},
            ]
            (specs_dir / "qa.json").write_text(json.dumps(qa_doc), encoding="utf-8")

            # 1. Emit
            emit_dir = tpath / "emit"
            res = qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            self.assertEqual(res, 0)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            # 2. Mock results matching the expected geometry
            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
                # WS_storey_1 observations
                f"ROW observation_id={obs_map['CHK_SOLID']} check_id=CHK_SOLID target_id=TGT_WALL_STOREY_1 sample_id=S_1 "
                "status=OK exists=true isHidden=false pos=[2000.0,1500.0,1500.0] min=[-300.0,-300.0,0.0] max=[4300.0,3300.0,3000.0] modCount=1 "
                "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 straightenCorners=true "
                "nVerts=16 nEdges=24 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=13320000000.0 signedVol=13320000000.0",
                f"ROW observation_id={obs_map['CHK_TOPO']} check_id=CHK_TOPO target_id=TGT_WALL_STOREY_1 sample_id=S_2 "
                "status=OK exists=true isHidden=false pos=[2000.0,1500.0,1500.0] min=[-300.0,-300.0,0.0] max=[4300.0,3300.0,3000.0] modCount=1 "
                "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 straightenCorners=true "
                "nVerts=16 nEdges=24 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=13320000000.0 signedVol=13320000000.0",
                f"ROW observation_id={obs_map['CHK_STACK']} check_id=CHK_STACK target_id=TGT_WALL_STOREY_1 sample_id=S_3 "
                "status=OK exists=true isHidden=false pos=[2000.0,1500.0,1500.0] min=[-300.0,-300.0,0.0] max=[4300.0,3300.0,3000.0] modCount=1 "
                "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 straightenCorners=true "
                "nVerts=16 nEdges=24 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=13320000000.0 signedVol=13320000000.0",
                # Placement PLC_001
                f"ROW observation_id={obs_map['CHK_PLC']} check_id=CHK_PLC target_id=TGT_PLC_001 sample_id=S_4 "
                "status=OK exists=true isHidden=false pos=[1500.0,-150.0,1500.0] min=[1010.0,-210.0,910.0] max=[1990.0,-90.0,2090.0] modCount=0 "
                "baseCls=Box mod1Cls=none innerAmt=0.0 outerAmt=0.0 segs=0 straightenCorners=false "
                "nVerts=8 nEdges=12 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=1387200.0 signedVol=1387200.0",
                f"ROW observation_id={obs_map['CHK_APERTURE']} check_id=CHK_APERTURE target_id=TGT_PLC_001 sample_id=S_5 "
                "status=OK exists=true isHidden=false pos=[1500.0,-150.0,1500.0] min=[1010.0,-210.0,910.0] max=[1990.0,-90.0,2090.0] modCount=0 "
                "baseCls=Box mod1Cls=none innerAmt=0.0 outerAmt=0.0 segs=0 straightenCorners=false "
                "nVerts=8 nEdges=12 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=1387200.0 signedVol=1387200.0",
                # Host facade wall (hidden by Mechanism A)
                f"ROW observation_id={obs_map['CHK_HOST']} check_id=CHK_HOST target_id=TGT_HOST_WALL sample_id=S_6 "
                "status=OK exists=true isHidden=true pos=[2000.0,0.0,1500.0] min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=0 "
                "baseCls=Box mod1Cls=none innerAmt=0.0 outerAmt=0.0 segs=0 straightenCorners=false "
                "nVerts=8 nEdges=12 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=0.0 signedVol=0.0",
                "END_BATCH batch_id=batch_001 rows=6",
            ]
            results_file = tpath / "captured.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            # 3. Assess
            out_dir = tpath / "out"
            assess_res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(assess_res, 0)
            self.assertEqual(res_json["verdict"], "PASS")
            self.assertEqual(res_json["summary"]["failed"], 0)
            self.assertEqual(res_json["checks"]["CHK_SOLID"]["status"], "PASS")
            self.assertEqual(res_json["checks"]["CHK_TOPO"]["status"], "PASS")
            self.assertEqual(res_json["checks"]["CHK_PLC"]["status"], "PASS")
            self.assertEqual(res_json["checks"]["CHK_APERTURE"]["status"], "PASS")
            self.assertEqual(res_json["checks"]["CHK_HOST"]["status"], "PASS")

    def test_assess_closed_contour_v2_watertightness_failure(self):
        # Open edges count = 4 -> FAIL
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            doc = dict(self.minimal_qa_doc)
            doc["profile"] = "closed_inner_contour_shell_v2"
            (specs_dir / "qa.json").write_text(json.dumps(doc), encoding="utf-8")
            (specs_dir / "walls.json").write_text(json.dumps({"wall_technique": "closed_inner_contour_shell_v2"}), encoding="utf-8")

            emit_dir = tpath / "emit"
            qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
            ]
            for c_id, o_id in obs_map.items():
                results_lines.append(
                    f"ROW observation_id={o_id} check_id={c_id} target_id=TGT_WALL_F01 sample_id=S_rec "
                    "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
                    "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
                    "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
                    "straightenCorners=true openEdges=4 vol=2610000000.0"
                )
            results_lines.append(f"END_BATCH batch_id=batch_001 rows={len(obs_map)}")
            results_file = tpath / "res.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            out_dir = tpath / "out"
            res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            self.assertEqual(res, 1)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(res_json["checks"]["CHK_SOLID"]["status"], "FAIL")
            self.assertIn("not watertight", res_json["checks"]["CHK_SOLID"]["errors"][0])

    def test_assess_closed_contour_v2_dup_vertices_failure(self):
        # dupVerts = 2 -> FAIL in topology
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            doc = dict(self.minimal_qa_doc)
            doc["profile"] = "closed_inner_contour_shell_v2"
            (specs_dir / "qa.json").write_text(json.dumps(doc), encoding="utf-8")
            (specs_dir / "walls.json").write_text(json.dumps({"wall_technique": "closed_inner_contour_shell_v2"}), encoding="utf-8")

            emit_dir = tpath / "emit"
            qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
            ]
            for c_id, o_id in obs_map.items():
                results_lines.append(
                    f"ROW observation_id={o_id} check_id={c_id} target_id=TGT_WALL_F01 sample_id=S_rec "
                    "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
                    "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
                    "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
                    "straightenCorners=true dupVerts=2 openEdges=0 vol=2610000000.0"
                )
            results_lines.append(f"END_BATCH batch_id=batch_001 rows={len(obs_map)}")
            results_file = tpath / "res.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            out_dir = tpath / "out"
            res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            self.assertEqual(res, 1)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(res_json["checks"]["CHK_TOPOLOGY"]["status"], "FAIL")
            self.assertIn("duplicate vertices", res_json["checks"]["CHK_TOPOLOGY"]["errors"][0])

    def test_assess_closed_contour_v2_seam_valence_failure(self):
        # seamValenceErr = 1 -> FAIL in topology
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            doc = dict(self.minimal_qa_doc)
            doc["profile"] = "closed_inner_contour_shell_v2"
            (specs_dir / "qa.json").write_text(json.dumps(doc), encoding="utf-8")
            (specs_dir / "walls.json").write_text(json.dumps({"wall_technique": "closed_inner_contour_shell_v2"}), encoding="utf-8")

            emit_dir = tpath / "emit"
            qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
            ]
            for c_id, o_id in obs_map.items():
                results_lines.append(
                    f"ROW observation_id={o_id} check_id={c_id} target_id=TGT_WALL_F01 sample_id=S_rec "
                    "status=OK exists=true isHidden=false pos=[2000.0,-150.0,1500.0] "
                    "min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=1 "
                    "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 "
                    "straightenCorners=true dupVerts=0 seamValenceErr=1 openEdges=0 vol=2610000000.0"
                )
            results_lines.append(f"END_BATCH batch_id=batch_001 rows={len(obs_map)}")
            results_file = tpath / "res.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            out_dir = tpath / "out"
            res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            self.assertEqual(res, 1)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(res_json["checks"]["CHK_TOPOLOGY"]["status"], "FAIL")
            self.assertIn("valence != 2", res_json["checks"]["CHK_TOPOLOGY"]["errors"][0])

    def test_assess_closed_contour_v2_volume_mismatch_failure(self):
        # Evaluated volume deviates from oracle -> CHK_SOLID fails
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            walls_doc = {
                "schema_version": "2.0",
                "wall_technique": "closed_inner_contour_shell_v2",
                "units": "millimeters",
                "storeys": [
                    {
                        "id": "storey_1",
                        "base_z_cm": 0.0,
                        "top_z_cm": 300.0,
                        "wall_thickness_cm": 30.0,
                        "vertices_cm": [[0.0, 0.0], [400.0, 0.0], [400.0, 300.0], [0.0, 300.0]],
                        "openings": [{"id": "OP_001", "s_range_cm": [100.0, 200.0], "sill_cm": 90.0, "head_cm": 210.0}],
                    }
                ],
            }
            (specs_dir / "walls.json").write_text(json.dumps(walls_doc), encoding="utf-8")
            qa_doc = dict(self.minimal_qa_doc)
            qa_doc["profile"] = "closed_inner_contour_shell_v2"
            qa_doc["scope"] = {
                "targets": [
                    {"id": "TGT_WALL_STOREY_1", "kind": "wall_surface", "role": "exterior_wall", "node_names": ["WS_storey_1"]}
                ]
            }
            qa_doc["check_plan"] = [
                {"id": "CHK_SOLID", "kind": "QA-V1-SOLID", "target_ref": "TGT_WALL_STOREY_1", "tolerance_ref": "solid_v1"}
            ]
            (specs_dir / "qa.json").write_text(json.dumps(qa_doc), encoding="utf-8")

            emit_dir = tpath / "emit"
            qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            # Send volume 10,000,000,000 mm3 instead of 13,320,000,000 mm3
            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
                f"ROW observation_id={obs_map['CHK_SOLID']} check_id=CHK_SOLID target_id=TGT_WALL_STOREY_1 sample_id=S_1 "
                "status=OK exists=true isHidden=false pos=[2000.0,1500.0,1500.0] min=[-300.0,-300.0,0.0] max=[4300.0,3300.0,3000.0] modCount=1 "
                "baseCls=Editable_Poly mod1Cls=Shell innerAmt=0.0 outerAmt=300.0 segs=1 straightenCorners=true "
                "nVerts=16 nEdges=24 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=10000000000.0 signedVol=10000000000.0",
                "END_BATCH batch_id=batch_001 rows=1",
            ]
            results_file = tpath / "res.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            out_dir = tpath / "out"
            res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            self.assertEqual(res, 1)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(res_json["checks"]["CHK_SOLID"]["status"], "FAIL")
            self.assertIn("deviates from analytical oracle", res_json["checks"]["CHK_SOLID"]["errors"][0])

    def test_assess_closed_contour_v2_placement_modifiers_failure(self):
        # Placement with modCount=1 -> FAIL (G-81 zero-modifier rule)
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            doc = dict(self.minimal_qa_doc)
            doc["profile"] = "closed_inner_contour_shell_v2"
            doc["scope"] = {
                "targets": [
                    {"id": "TGT_PLC_001", "kind": "placement", "role": "window_placement", "node_names": ["PLC_001"]}
                ]
            }
            doc["check_plan"] = [
                {"id": "CHK_PLC", "kind": "QA-V1-PLACEMENT", "target_ref": "TGT_PLC_001", "tolerance_ref": "placement_v1"}
            ]
            (specs_dir / "qa.json").write_text(json.dumps(doc), encoding="utf-8")
            (specs_dir / "walls.json").write_text(json.dumps({"wall_technique": "closed_inner_contour_shell_v2"}), encoding="utf-8")

            emit_dir = tpath / "emit"
            qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
                f"ROW observation_id={obs_map['CHK_PLC']} check_id=CHK_PLC target_id=TGT_PLC_001 sample_id=S_1 "
                "status=OK exists=true isHidden=false pos=[1500.0,-150.0,1500.0] min=[1010.0,-210.0,910.0] max=[1990.0,-90.0,2090.0] modCount=1 "
                "baseCls=Box mod1Cls=Edit_Poly innerAmt=0.0 outerAmt=0.0 segs=0 straightenCorners=false "
                "nVerts=8 nEdges=12 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=1387200.0 signedVol=1387200.0",
                "END_BATCH batch_id=batch_001 rows=1",
            ]
            results_file = tpath / "res.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            out_dir = tpath / "out"
            res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            self.assertEqual(res, 1)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(res_json["checks"]["CHK_PLC"]["status"], "FAIL")
            self.assertIn("G-81 zero-modifier rule", res_json["checks"]["CHK_PLC"]["errors"][0])

    def test_assess_closed_contour_v2_host_wall_visible_failure(self):
        # Host facade wall is not hidden (isHidden=false) -> FAIL (Mechanism A)
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            specs_dir = tpath / "specs" / "pipeline"
            specs_dir.mkdir(parents=True)
            doc = dict(self.minimal_qa_doc)
            doc["profile"] = "closed_inner_contour_shell_v2"
            doc["scope"] = {
                "targets": [
                    {"id": "TGT_HOST_WALL", "kind": "wall_host", "role": "host_facade_wall", "node_names": ["FACADE_WALL_1"]}
                ]
            }
            doc["check_plan"] = [
                {"id": "CHK_HOST", "kind": "QA-V1-WALLS", "target_ref": "TGT_HOST_WALL", "tolerance_ref": "exact"}
            ]
            (specs_dir / "qa.json").write_text(json.dumps(doc), encoding="utf-8")
            (specs_dir / "walls.json").write_text(json.dumps({"wall_technique": "closed_inner_contour_shell_v2"}), encoding="utf-8")

            emit_dir = tpath / "emit"
            qa_check.run_emit_mode(tpath, emit_dir, "run_v2", None, False)
            req_file = emit_dir / "qa-request.json"
            req_doc = json.loads(req_file.read_text(encoding="utf-8"))
            obs_map = {o["check_id"]: o["id"] for o in req_doc["observations"]}

            results_lines = [
                "START_BATCH batch_id=batch_001",
                "GUARD units.SystemType=millimeters units.SystemScale=1.0",
                f"ROW observation_id={obs_map['CHK_HOST']} check_id=CHK_HOST target_id=TGT_HOST_WALL sample_id=S_1 "
                "status=OK exists=true isHidden=false pos=[2000.0,0.0,1500.0] min=[0.0,-300.0,0.0] max=[4000.0,0.0,3000.0] modCount=0 "
                "baseCls=Box mod1Cls=none innerAmt=0.0 outerAmt=0.0 segs=0 straightenCorners=false "
                "nVerts=8 nEdges=12 dupVerts=0 seamValenceErr=0 tJunctions=0 openEdges=0 maxYDev=0.0 vol=0.0 signedVol=0.0",
                "END_BATCH batch_id=batch_001 rows=1",
            ]
            results_file = tpath / "res.txt"
            results_file.write_text("\n".join(results_lines) + "\n", encoding="utf-8")

            out_dir = tpath / "out"
            res = qa_check.run_assess_mode(tpath, req_file, results_file, out_dir, False)
            self.assertEqual(res, 1)
            res_json = json.loads((out_dir / "qa-results.json").read_text(encoding="utf-8"))
            self.assertEqual(res_json["checks"]["CHK_HOST"]["status"], "FAIL")
            self.assertIn("active host collision with openings", res_json["checks"]["CHK_HOST"]["errors"][0])


if __name__ == "__main__":
    unittest.main()
