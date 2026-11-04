"""Offline synthetic controls and immutable historical-data cross-checks only."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest


HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
sys.path.insert(0, str(AUDIT))
import phase16_p3_oracle as oracle
import test_phase16_p3_oracle as fixture

SPEC = importlib.util.spec_from_file_location("p3_next_group_diagnostics", HERE / "group_diagnostics.py")
diagnostics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnostics)


def synthetic_view():
    # Two disjoint, parallel square patches. These are MADE-UP unit-test inputs,
    # not F01, not an actual API observation, and not an emitted-wall fixture.
    return {
        "schema_version": "p3-triangle-view-1", "status": "CAPTURED_NOT_ACCEPTED",
        "observation": "snapshot_triangle_groups_not_native_polygons", "index_base": 1,
        "coordinate_space": "world", "target": {"node_handle": "test1", "anim_handle": "test2",
          "base_anim_handle": "test3", "modifier_anim_handle": "test4",
          "object_transform": [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]},
        "units": {"system_type": "millimeters", "system_scale": 1, "scene_units_per_cm": 10},
        "group_api": "meshop.getPolysUsingFace", "ignore_visible_edges": False,
        "threshold_degrees": 45,
        "vertices": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                     [3, 0, 0], [4, 0, 0], [4, 1, 0], [3, 1, 0]],
        "triangles": [[1, 2, 3], [1, 3, 4], [5, 6, 7], [5, 7, 8]],
        "triangle_edge_visibility": [[True, True, False], [False, True, True],
                                     [True, True, False], [False, True, True]],
        "groups_for_each_triangle": [[1, 2], [1, 2], [3, 4], [3, 4]],
        "mesh_equivalent_node_counts": [4, 8],
        "native_evaluated_polygon_status": "INCOMPLETE", "historical_predelete_grid_status": "INCOMPLETE"}


def fake_final(view):
    return {"schema_version": "p3-independent-measurement-1", "status": "CAPTURED_NOT_ACCEPTED",
            "stage": "final", "target": deepcopy(view["target"]), "units": deepcopy(view["units"]),
            "evaluated": {"coordinate_space": "world", "index_base": 1,
                          "vertices": deepcopy(view["vertices"]), "triangles": deepcopy(view["triangles"])},
            "stack": [{"class": "Shell", "anim_handle": view["target"]["modifier_anim_handle"]}],
            "issues": []}


class GroupDiagnostics(unittest.TestCase):
    def test_two_groups_and_derived_loops_are_not_polygon_acceptance(self):
        raw = synthetic_view()
        original = deepcopy(raw)
        result = diagnostics.diagnose(raw)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["visibility_angle_group_count_not_native_polygon_count"], 2)
        self.assertEqual([x["derived_boundary_vertex_ids"] for x in
                          result["derived_group_boundaries_not_native_polygon_loops"]],
                         [[1, 2, 3, 4], [5, 6, 7, 8]])
        self.assertEqual(raw, original)
        self.assertNotIn("faces", raw)

    def test_same_triangles_different_groups_distinguish_group_count_from_face_count(self):
        raw = synthetic_view()
        raw["groups_for_each_triangle"] = [[1], [2], [3], [4]]
        result = diagnostics.diagnose(raw)
        self.assertEqual(result["visibility_angle_group_count_not_native_polygon_count"], 4)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual([len(x["derived_boundary_vertex_ids"]) for x in
                          result["derived_group_boundaries_not_native_polygon_loops"]], [3, 3, 3, 3])

    def test_inconsistent_and_overlapping_group_membership_refuse(self):
        for rows in ([[1, 2], [2], [3, 4], [3, 4]], [[1, 2], [1, 2], [2, 3, 4], [2, 3, 4]],
                     [[1, 1], [1, 2], [3, 4], [3, 4]], [[2], [1, 2], [3, 4], [3, 4]]):
            raw = synthetic_view()
            raw["groups_for_each_triangle"] = rows
            with self.subTest(rows=rows), self.assertRaises(diagnostics.Incomplete):
                diagnostics.diagnose(raw)

    def test_disconnected_and_wrong_oriented_group_refuse(self):
        raw = synthetic_view()
        raw["groups_for_each_triangle"] = [[1, 2, 3, 4]] * 4
        with self.assertRaises(diagnostics.Incomplete):
            diagnostics.diagnose(raw)
        raw = synthetic_view()
        raw["triangles"][1] = [1, 4, 3]
        with self.assertRaises(diagnostics.Incomplete):
            diagnostics.diagnose(raw)

    def test_malformed_ceilings_indices_and_metadata_refuse(self):
        for mutator in (
            lambda r: r.update(index_base=True),
            lambda r: r["triangles"][0].__setitem__(0, True),
            lambda r: r["triangles"][0].__setitem__(0, 9),
            lambda r: r["triangles"][0].__setitem__(0, []),
            lambda r: r["vertices"][0].__setitem__(0, float("nan")),
            lambda r: r.update(ignore_visible_edges=True),
            lambda r: r.update(native_evaluated_polygon_status="PASS"),
            lambda r: r.update(groups_for_each_triangle=[]),
            lambda r: r["triangle_edge_visibility"][0].__setitem__(0, 1),
            lambda r: r["vertices"].extend([[0, 0, 0]] * 57),
        ):
            raw = synthetic_view()
            mutator(raw)
            with self.subTest(mutator=mutator), self.assertRaises(diagnostics.Incomplete):
                diagnostics.diagnose(raw)

    def test_two_channel_match_does_not_authenticate_and_mismatches_refuse(self):
        raw = synthetic_view()
        measurement = fake_final(raw)
        result = diagnostics.compare_measurement(raw, measurement)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertTrue(result["matched_reported_identity_units_and_indexed_arrays"])
        for key in ("node_handle", "anim_handle", "base_anim_handle", "object_transform"):
            bad = deepcopy(measurement)
            bad["target"][key] = "changed"
            with self.subTest(key=key), self.assertRaises(diagnostics.Incomplete):
                diagnostics.compare_measurement(raw, bad)
        for key in ("vertices", "triangles"):
            bad = deepcopy(measurement)
            bad["evaluated"][key][0][0] += 1
            with self.subTest(key=key), self.assertRaises(diagnostics.Incomplete):
                diagnostics.compare_measurement(raw, bad)
        bad = deepcopy(measurement)
        bad["units"]["system_type"] = "centimeters"
        with self.assertRaises(diagnostics.Incomplete):
            diagnostics.compare_measurement(raw, bad)
        bad = deepcopy(measurement)
        bad["stack"][0]["anim_handle"] = "other-modifier"
        with self.assertRaises(diagnostics.Incomplete):
            diagnostics.compare_measurement(raw, bad)
        for key, value in (("triangles", True), ("vertices", True)):
            bad = deepcopy(measurement)
            bad["evaluated"][key][0][0] = value
            with self.subTest(boolean_laundering=key), self.assertRaises(diagnostics.Incomplete):
                diagnostics.compare_measurement(raw, bad)
        bad = deepcopy(measurement)
        bad["target"]["object_transform"][0][0] = True
        with self.assertRaises(diagnostics.Incomplete):
            diagnostics.compare_measurement(raw, bad)

    def test_actual_calibration_data_is_not_f01_or_polygon_observation(self):
        path = AUDIT / "_phase16-p3-measurement-smoke-capture-2026-11-02e.json"
        data = path.read_bytes()
        self.assertEqual(sha256(data).hexdigest(), "81b69fc1de39a9fcd410b9158cac6d317030d2f2bcd10bde4cd32afdf12c364a")
        raw = json.loads(data)
        self.assertEqual((raw["base"]["active_counts"], raw["evaluated"]["vertex_count"],
                          raw["evaluated"]["triangle_count"]), ([4, 4, 1], 8, 12))
        self.assertIsNone(raw["evaluated"]["polygon_count"])
        self.assertNotIn("faces", raw["evaluated"])
        self.assertNotIn("grid", raw)
        self.assertEqual(path.read_bytes(), data)


class OracleBoundary(unittest.TestCase):
    def test_f01_actual_inputs_produce_analytical_prediction_only(self):
        source = AUDIT / "phase16-p3-f01-input-2026-11-02e"
        paths = [source / "project/walls.json", source / "project/dimensions.json",
                 source / "direction-authority.json", AUDIT / "AGENT_PLAN_poly_surface_shell.md"]
        blobs = [p.read_bytes() for p in paths]
        walls, dims, authority = [json.loads(b) for b in blobs[:3]]
        physical = oracle.physical_from_f01_authority(walls, dims, authority, walls_bytes=blobs[0],
                                                       source_bytes=blobs[3], reviewer="offline cross-check")
        predicted = oracle.predict(walls, dims, physical)
        self.assertEqual(predicted["status"], "PASS")
        p = predicted["prediction"]
        self.assertEqual(tuple(p["grid_topology"][k] for k in ("vertices", "edges", "faces")), (24, 38, 15))
        self.assertEqual(tuple(p["base_topology"][k] for k in ("vertices", "edges", "faces")), (24, 36, 12))
        self.assertEqual((p["shell_topology"]["faces"], p["evaluated_triangles"]), (48, 96))
        self.assertEqual((p["source_area_cm2"], p["volume_cm3"]), (87000, 2610000))
        self.assertEqual([path.read_bytes() for path in paths], blobs)

    def test_triangle_only_synthetic_control_stays_incomplete(self):
        walls, dims, physical = fixture.fixture()
        synthetic = fixture.manual_capture(walls, dims)
        raw, grid = fixture.full_measurement_capture(synthetic)
        predicted = oracle.predict(walls, dims, physical)
        checked = oracle.check_independent_capture(predicted, raw, synthetic["evidence"], expected_units=raw["units"])
        states = {c["check"]: c["status"] for c in checked["checks"]}
        self.assertEqual(checked["status"], "INCOMPLETE")
        self.assertEqual(states["GRID_CAPTURE"], "INCOMPLETE")
        self.assertEqual(states["EVALUATED_CAPTURE"], "INCOMPLETE")
        self.assertEqual(states["TRIANGLE_VOID_AND_SOLID_COVERAGE"], "PASS")
        self.assertEqual(checked["evidence_scope"], "synthetic_test")
        self.assertNotIn("evaluated_topology", checked["measured"])
        with_grid = oracle.check_independent_capture(predicted, raw, synthetic["evidence"], grid_raw=grid,
                                                    expected_units=raw["units"])
        self.assertEqual(with_grid["status"], "INCOMPLETE")
        self.assertEqual({c["check"]: c["status"] for c in with_grid["checks"]}["EVALUATED_CAPTURE"], "INCOMPLETE")
        self.assertEqual({c["check"]: c["status"] for c in with_grid["checks"]}["GRID_TOPOLOGY"], "PASS")

    def test_historical_main03_is_failure_not_current_grid_evidence(self):
        path = AUDIT / "_phase16-p3-main03-live-result-2026-11-02e.json"
        data = path.read_bytes()
        report = json.loads(data)
        self.assertEqual(report["verdict"], "FAILED_INITIAL_BASELINE_SAFE_CLEANUP_NOT_ACCEPTED")
        self.assertIn("objectsAfter=0", report["wire"]["result"])
        self.assertNotIn("P3_FACE_IDS|", report["wire"]["result"])
        self.assertIn("no independent final F01 wall measurement", report["interpretation"])
        self.assertEqual(path.read_bytes(), data)

    def test_emitted_output_is_monolithic_and_does_not_publish_grid_loops(self):
        path = AUDIT / "phase16-p3-main-build-2026-11-02e" / "Main03" / "published" / "wall_surface.ms"
        data = path.read_bytes()
        self.assertEqual(sha256(data).hexdigest(), "91274ffbb1cb9491c6b5fd511ceb238346f45434e56c2d6b467753a7cbdaaf28")
        text = data.decode("utf-8")
        self.assertLess(text.index('stage = "grid-faces"'), text.index('stage = "opening-delete-once"'))
        self.assertLess(text.index('stage = "opening-delete-once"'), text.index('stage = "one-shell"'))
        self.assertIn('print ("P3_FACE_IDS|"', text)
        self.assertIn("polyop.getFaceVerts node id", text)
        self.assertNotIn("P3NextMeasurementTarget", text)
        self.assertEqual(path.read_bytes(), data)


class StaticCandidate(unittest.TestCase):
    def test_delimiters_and_reserved_names_lexically_only(self):
        source = (HERE / "triangle_view_capture.ms").read_text(encoding="utf-8")
        source = re.sub(r'--[^\n]*|"(?:\\.|[^"\\])*"', ' ', source)
        stack = []
        pairs = {")": "(", "]": "[", "}": "{"}
        for char in source:
            if char in "([{":
                stack.append(char)
            elif char in ")]}" :
                self.assertTrue(stack)
                self.assertEqual(stack.pop(), pairs[char])
        self.assertFalse(stack)
        self.assertNotRegex(source, r"\b(?:local|global|fn|for)\s+(?:by|on|off|to|from|at)\b")

    def test_candidate_narrow_temp_ownership_and_read_only_tokens(self):
        source = (HERE / "triangle_view_capture.ms").read_text(encoding="utf-8")
        operational = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("--"))
        for forbidden in ("convertTo", "collapseStack", "getNodeByName", "addModifier", "delete n", "delete o",
                          "snapshot n", "saveMaxFile", "resetMaxFile", "formattedPrint", "setEdgeVis"):
            self.assertNotIn(forbidden, operational)
        self.assertEqual(operational.count("delete meshValue"), 2)
        self.assertIn("meshop.getPolysUsingFace meshValue", operational)
        self.assertIn("getEdgeVis meshValue", operational)
        self.assertIn("getVert meshValue", operational)
        self.assertNotIn("getVert meshValue k) *", operational)
        self.assertIn("#(polyop.getNumVerts base, polyop.getNumEdges base, polyop.getNumFaces base)", operational)


if __name__ == "__main__":
    unittest.main(verbosity=2)
