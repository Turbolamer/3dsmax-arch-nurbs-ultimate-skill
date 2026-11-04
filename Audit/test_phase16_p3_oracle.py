"""Protective, offline tests; synthetic captures are never called live evidence."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import math
import importlib.util
import unittest

import phase16_p3_oracle as oracle


PLAN = Path(__file__).with_name("AGENT_PLAN_poly_surface_shell.md")


def fixture():
    """Hand-authored F01 values from plan G.1, not any wall emitter/output."""
    dim = {"schema_version": "1.1", "spec": "dimensions", "project": "P3_ORACLE_F01",
           "status": "locked", "units": {"length": "cm", "angle": "deg"},
           "tolerances": {"linear_cm": 0.5, "area_m2": 0.01, "angle_deg": 0.1},
           "facades": [{"id": "F01_INNER", "start_corner_cm": [0, 0],
                        "end_corner_cm": [400, 0]}]}
    ops = [{"id": "DOOR", "wall_run_id": "RUN", "kind": "door", "u_range_cm": [50, 150],
            "sill_cm": 0, "head_cm": 210},
           {"id": "WINDOW", "wall_run_id": "RUN", "kind": "window", "u_range_cm": [230, 330],
            "sill_cm": 90, "head_cm": 210}]
    wall = {"schema_version": "1.1", "spec": "walls", "project": "P3_ORACLE_F01",
            "status": "locked", "units": {"length": "cm", "angle": "deg"},
            "tolerances": deepcopy(dim["tolerances"]), "wall_technique": "poly_surface_shell_v1",
            "reference_face": "inner", "numeric_epsilon_cm": 0.0001,
            "numeric_unit_epsilon": 0.00001, "blocks": [{"id": "BLOCK", "z_range_cm": [0, 300]}],
            "wall_runs": [{"id": "RUN", "block_id": "BLOCK", "contour_ref": "dimensions.json:facades:F01_INNER",
                           "start_cm": [0, 0], "end_cm": [400, 0], "outward": [0, -1],
                           "base_z_cm": 0, "top_z_cm": 300, "thickness_cm": 30,
                           "topology_budget": {"max_grid_polygons": 15, "max_base_active_polygons": 12,
                                               "max_evaluated_triangles": 96}}],
            "openings": ops, "upper_returns": []}
    # This physical record is deliberately not copied from wall_runs or openings.
    physical = {"project": "P3_ORACLE_F01", "wall_run_id": "RUN", "reference_face": "inner",
                "start_cm": [0, 0], "end_cm": [400, 0], "outward": [0, -1],
                "base_z_cm": 0, "top_z_cm": 300, "thickness_cm": 30,
                "openings": [{"id": "DOOR", "kind": "door", "u_range_cm": [50, 150], "sill_cm": 0, "head_cm": 210},
                             {"id": "WINDOW", "kind": "window", "u_range_cm": [230, 330], "sill_cm": 90, "head_cm": 210}],
                "evidence": {"locator": "Audit/AGENT_PLAN_poly_surface_shell.md#G.1",
                             "sha256": sha256(PLAN.read_bytes()).hexdigest(),
                             "reviewer": "independent-offline-oracle-author", "reviewed": True}}
    bind(wall, dim, physical)
    return wall, dim, physical


def bind(wall, dim, physical):
    physical["source_hashes"] = {"walls": oracle.source_digest(wall), "dimensions": oracle.source_digest(dim)}


def manual_capture(wall, dim):
    """Independent F01 mesh fixture; never consumes oracle predictions.

    Ordinary rectangular-grid arithmetic is used only to manufacture synthetic test
    observations. These tests prove checker discrimination, not a Max execution.
    """
    u = [0, 50, 150, 230, 330, 400]
    z = [0, 90, 210, 300]
    verts = [[x, 0, h] for h in z for x in u]
    grid = [[6*j+i, 6*j+i+1, 6*(j+1)+i+1, 6*(j+1)+i] for j in range(3) for i in range(5)]
    base = [f for i, f in enumerate(grid, 1) if i not in (2, 7, 9)]
    # Hard-coded boundary loops, independently traced around the door notch and
    # window void; no oracle topology, edge enumeration or returned IDs are used.
    loops = [[0, 1, 7, 13, 14, 8, 2, 3, 4, 5, 11, 17, 23, 22, 21, 20, 19, 18, 12, 6],
             [9, 15, 16, 10]]
    shell_verts = verts + [[x, -30, h] for x, _, h in verts]
    shell = [list(reversed(f)) for f in base] + [[i+24 for i in f] for f in base]
    shell += [[a, b, b+24, a+24] for loop in loops for a, b in zip(loop, loop[1:]+loop[:1])]
    tris = [[q[0], q[1], q[2]] for q in shell] + [[q[0], q[2], q[3]] for q in shell]
    return {"evidence": {"kind": "synthetic_test", "capture_id": "independent-hand-authored-F01",
                         "artifact_sha256": sha256(b"synthetic-not-an-emitted-artifact").hexdigest(),
                         "source_hashes": {"walls": oracle.source_digest(wall), "dimensions": oracle.source_digest(dim)},
                         "project": wall["project"], "wall_run_id": "RUN", "length_unit": "cm"},
            "grid": {"vertices_cm": verts, "faces": grid, "index_base": 0},
            "base": {"vertices_cm": deepcopy(verts), "faces": base, "index_base": 0},
            "evaluated": {"vertices_cm": shell_verts, "faces": shell, "triangles": tris, "index_base": 0}}


def full_measurement_capture(normalized):
    """Synthetic FULL measure.ms schema, not its short path/hash return envelope."""
    def stage(name):
        item = normalized[name]
        result = {"coordinate_space": "world", "index_base": 1,
                  "vertices": [[10*x for x in v] for v in item["vertices_cm"]]}
        for key in ("faces", "triangles"):
            if key in item:
                result[key] = [[i+1 for i in f] for f in item[key]]
        return result
    target = {"name": "synthetic-only", "anim_handle": "100", "node_handle": "10", "base_anim_handle": "200",
              "object_transform": [[1,0,0],[0,1,0],[0,0,1],[0,0,0]]}
    raw = {"schema_version": "p3-independent-measurement-1", "status": "CAPTURED_NOT_ACCEPTED",
           "stage": "final", "evidence_origin": "independent_read_only_scene_queries",
           "index_base": 1, "length_unit": "scene_unit",
           "units": {"system_type": "millimeters", "system_scale": 1, "scene_units_per_cm": 10},
           "target": target, "base": stage("base"), "evaluated": stage("evaluated"),
           "issues": [], "grid_status": "INCOMPLETE: predeletion not recoverable", "scene_count": 1}
    del raw["evaluated"]["faces"]
    raw["evaluated"]["polygon_count"] = None
    raw["evaluated"]["polygon_count_status"] = "INCOMPLETE: no verified non-mutating dedicated polygon evaluator"
    grid_raw = {"schema_version": raw["schema_version"], "status": "CAPTURED_NOT_ACCEPTED", "stage": "grid",
                "units": deepcopy(raw["units"]), "target": deepcopy(target), "grid": stage("grid"), "issues": []}
    return raw, grid_raw


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.w, self.d, self.a = fixture()
        self.m = manual_capture(self.w, self.d)

    def pred(self):
        return oracle.predict(self.w, self.d, self.a)

    def measured(self):
        return oracle.assess(self.w, self.d, self.a, self.m)

    def assertCheck(self, result, name, status):
        found = [c for c in result["checks"] if c["check"] == name]
        self.assertTrue(found, (name, result))
        self.assertEqual(found[-1]["status"], status, found)

    def test_actual_plan_exact_coordinates_and_outside(self):
        text = PLAN.read_text(encoding="utf-8")
        # Direct independent inspection of source is intentionally separate from
        # source_digest and provenance-path syntax. No arbitrary semantic parser.
        self.assertIn("u = 0…400`, `Y = 0`, `Z = 0…300`, наружу `(0,−1,0)`, толщина **30**", text)
        self.assertIn("Дверь: `u = 50…150`, `Z = 0…210`. Окно: `u = 230…330`, `Z = 90…210`.", text)
        self.assertIn("u = [0, 50, 150, 230, 330, 400]`, `Z = [0, 90, 210, 300]", text)
        self.assertTrue(oracle.verify_authority_source(self.a, PLAN.read_bytes(),
                        locator="Audit/AGENT_PLAN_poly_surface_shell.md#G.1"))

    def test_source_bytes_mismatch_is_refused(self):
        with self.assertRaises(oracle.OracleProblem) as exc:
            oracle.verify_authority_source(self.a, b"not the reviewed source", locator=self.a["evidence"]["locator"])
        self.assertEqual(exc.exception.status, "FAIL")

    def test_source_locator_mismatch_is_refused(self):
        with self.assertRaises(oracle.OracleProblem):
            oracle.verify_authority_source(self.a, PLAN.read_bytes(), locator="some-other-source")

    def test_f01_exact_analytical_reference(self):
        r = self.pred()
        self.assertEqual(r["status"], "PASS", r)
        p = r["prediction"]
        for name, numbers in (("grid_topology", (24, 38, 15)), ("base_topology", (24, 36, 12))):
            self.assertEqual(tuple(p[name][k] for k in ("vertices", "edges", "faces")), numbers)
        self.assertEqual(p["base_topology"]["boundary_edges"], 24)
        self.assertEqual(p["base_topology"]["boundary_components"], 2)
        self.assertEqual(p["base_topology"]["surface_components"], 1)
        self.assertEqual(p["base_topology"]["euler"], 0)
        self.assertEqual(p["removed_row_major_labels"], [2, 7, 9])
        self.assertEqual(p["source_area_cm2"], 87000)
        self.assertEqual(p["volume_cm3"], 2610000)
        self.assertEqual(p["shell_topology"]["faces"], 48)
        self.assertEqual(p["evaluated_triangles"], 96)
        self.assertEqual(p["shell_topology"]["boundary_edges"], 0)
        self.assertEqual(p["shell_topology"]["euler"], 0)
        self.assertEqual(p["bounds_cm"], {"min": [0, -30, 0], "max": [400, 0, 300]})

    def test_independent_f01_capture_pass(self):
        r = self.measured()
        self.assertEqual(r["status"], "PASS", [c for c in r["checks"] if c["status"] != "PASS"])
        self.assertEqual(r["measured"]["signed_volume_cm3"], 2610000)
        self.assertEqual(r["measured"]["source_area_cm2"], 87000)
        self.assertEqual(r["evidence_scope"], "synthetic_test")

    def test_reflected_same_positive_volume_fails_physical_direction(self):
        for v in self.m["evaluated"]["vertices_cm"]:
            v[1] = -v[1]
        # Reflection changes parity. Reverse each face/triangle so it is still a
        # valid outward closed shell with positive volume and no open edges.
        for key in ("faces", "triangles"):
            self.m["evaluated"][key] = [list(reversed(f)) for f in self.m["evaluated"][key]]
        r = self.measured()
        self.assertEqual(r["status"], "FAIL")
        self.assertCheck(r, "TRIANGLE_VOLUME", "PASS")
        self.assertCheck(r, "TRIANGLE_CLOSED_MANIFOLD", "PASS")
        self.assertCheck(r, "EVALUATED_PHYSICAL_DIRECTION", "FAIL")
        self.assertEqual(r["measured"]["signed_volume_cm3"], 2610000)

    def test_closed_equal_volume_wrong_opening_locations_fail(self):
        # Move both holes by X reflection, retaining thickness direction, bounds,
        # closed manifold and positive volume. Only spatial/source checks catch it.
        for name in ("base", "evaluated"):
            for v in self.m[name]["vertices_cm"]:
                v[0] = 400-v[0]
            for key in ("faces", "triangles"):
                if key in self.m[name]:
                    self.m[name][key] = [list(reversed(f)) for f in self.m[name][key]]
        r = self.measured()
        self.assertCheck(r, "TRIANGLE_CLOSED_MANIFOLD", "PASS")
        self.assertCheck(r, "TRIANGLE_VOLUME", "PASS")
        self.assertCheck(r, "EVALUATED_PHYSICAL_DIRECTION", "PASS")
        self.assertCheck(r, "EVALUATED_BOUNDS", "PASS")
        self.assertCheck(r, "TRIANGLE_CAPTURE", "FAIL")
        self.assertEqual(r["status"], "FAIL")

    def test_declared_and_mesh_wrong_same_sign_cannot_supply_physical_truth(self):
        self.w["wall_runs"][0]["outward"] = [0, 1]
        bind(self.w, self.d, self.a)
        r = self.pred()
        self.assertCheck(r, "SOURCE_PHYSICAL_DIRECTION", "FAIL")
        self.assertEqual(r["prediction"]["bounds_cm"]["min"][1], -30)

    def test_missing_authority_is_incomplete(self):
        self.assertEqual(oracle.predict(self.w, self.d, None)["status"], "INCOMPLETE")

    def test_missing_authority_source_binding_is_incomplete(self):
        del self.a["source_hashes"]
        self.assertEqual(self.pred()["status"], "INCOMPLETE")

    def test_unreviewed_authority_incomplete(self):
        self.a["evidence"]["reviewed"] = False
        self.assertEqual(self.pred()["status"], "INCOMPLETE")

    def test_stale_authority_binding_fails(self):
        self.w["wall_runs"][0]["outward"] = [0, 1]
        self.assertEqual(self.pred()["status"], "FAIL")

    def test_opening_source_mismatch_fails_despite_well_formed_wall(self):
        self.w["openings"][1]["u_range_cm"] = [220, 320]
        bind(self.w, self.d, self.a)
        r = self.pred()
        self.assertCheck(r, "SOURCE_OPENINGS", "FAIL")
        self.assertEqual(r["prediction"]["source_area_cm2"], 87000)

    def test_full_window_face_left_in_base_fails_coverage(self):
        self.m["base"]["faces"].append(self.m["grid"]["faces"][8])
        r = self.measured()
        self.assertCheck(r, "BASE_COVERAGE", "FAIL")
        self.assertCheck(r, "BASE_SOURCE_AREA", "FAIL")

    def test_equal_area_window_solid_swap_fails_coverage(self):
        # Put the window back and remove a different 100*120 quad. Same total
        # area is not source occupancy evidence. Grid cell column1,row1 is door;
        # choose an equal-area alternate by swapping a 100*90 bottom cell with
        # another bottom cell of identical width outside the opening.
        base = self.m["base"]["faces"]
        base.remove(self.m["grid"]["faces"][3])
        base.append(self.m["grid"]["faces"][1])
        r = self.measured()
        self.assertCheck(r, "BASE_SOURCE_AREA", "PASS")
        self.assertCheck(r, "BASE_COVERAGE", "FAIL")

    def test_reversed_base_winding_fails_normals(self):
        self.m["base"]["faces"] = [list(reversed(f)) for f in self.m["base"]["faces"]]
        r = self.measured()
        self.assertCheck(r, "BASE_COVERAGE", "PASS")
        self.assertCheck(r, "BASE_NORMALS", "FAIL")

    def test_one_flipped_triangle_fails_integrity(self):
        self.m["evaluated"]["triangles"][0].reverse()
        r = self.measured()
        self.assertCheck(r, "TRIANGLE_CLOSED_MANIFOLD", "FAIL")
        self.assertCheck(r, "TRIANGLE_NORMALS", "FAIL")

    def test_duplicate_triangles_fail_even_with_no_boundary_edges(self):
        self.m["evaluated"]["triangles"] *= 2
        r = self.measured()
        self.assertEqual(r["measured"]["triangle_topology"]["boundary_edges"], 0)
        self.assertCheck(r, "TRIANGLE_CLOSED_MANIFOLD", "FAIL")
        self.assertCheck(r, "TRIANGLE_VOID_AND_SOLID_COVERAGE", "FAIL")

    def test_triangle_hole_fails(self):
        self.m["evaluated"]["triangles"].pop()
        r = self.measured()
        self.assertCheck(r, "TRIANGLE_CLOSED_MANIFOLD", "FAIL")

    def test_solid_wall_no_holes_closed_is_not_sufficient(self):
        # Independent box with the same overall bounds: perfectly closed, no
        # opening voids, and no reliance on expected grid to generate its mesh.
        vs = [[0,0,0],[400,0,0],[400,0,300],[0,0,300],
              [0,-30,0],[400,-30,0],[400,-30,300],[0,-30,300]]
        fs = [[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
        ts = [t for q in fs for t in ([q[0],q[1],q[2]], [q[0],q[2],q[3]])]
        self.m["evaluated"].update(vertices_cm=vs, faces=fs, triangles=ts)
        r = self.measured()
        self.assertCheck(r, "TRIANGLE_CLOSED_MANIFOLD", "PASS")
        self.assertCheck(r, "TRIANGLE_VOLUME", "FAIL")
        self.assertEqual(r["status"], "FAIL")

    def test_predicted_budget_cannot_auto_increase(self):
        self.w["wall_runs"][0]["topology_budget"]["max_grid_polygons"] = 14
        bind(self.w, self.d, self.a)
        r = self.pred()
        self.assertCheck(r, "PREDICTED_MAX_GRID_POLYGONS", "FAIL")

    def test_actual_budget_checked_on_duplicate_geometry(self):
        self.m["grid"]["faces"].append(self.m["grid"]["faces"][0])
        self.m["evaluated"]["triangles"].append(self.m["evaluated"]["triangles"][0])
        r = self.measured()
        self.assertCheck(r, "ACTUAL_MAX_GRID_POLYGONS", "FAIL")
        self.assertCheck(r, "ACTUAL_MAX_EVALUATED_TRIANGLES", "FAIL")

    def test_missing_measurement_stage_is_incomplete(self):
        del self.m["grid"]
        self.assertEqual(self.measured()["status"], "INCOMPLETE")

    def test_missing_triangles_is_incomplete_not_echo_pass(self):
        del self.m["evaluated"]["triangles"]
        self.m["evaluated"]["reported_volume"] = 2610000
        self.assertEqual(self.measured()["status"], "INCOMPLETE")

    def test_missing_evaluated_polygons_is_incomplete(self):
        del self.m["evaluated"]["faces"]
        r = self.measured()
        self.assertEqual(r["status"], "INCOMPLETE")
        self.assertCheck(r, "EVALUATED_PHYSICAL_DIRECTION", "PASS")
        self.assertCheck(r, "TRIANGLE_VOLUME", "PASS")

    def test_missing_evidence_is_incomplete(self):
        del self.m["evidence"]
        self.assertEqual(self.measured()["status"], "INCOMPLETE")

    def test_bad_index_fails(self):
        self.m["base"]["faces"][0][0] = 999
        self.assertEqual(self.measured()["status"], "FAIL")

    def test_boolean_coordinate_refused(self):
        self.w["wall_runs"][0]["thickness_cm"] = True
        self.assertEqual(self.pred()["status"], "FAIL")

    def test_nan_coordinate_refused(self):
        self.w["wall_runs"][0]["thickness_cm"] = math.nan
        self.assertEqual(self.pred()["status"], "FAIL")

    def test_duplicate_actual_vertex_not_welded(self):
        self.m["base"]["vertices_cm"][0] = self.m["base"]["vertices_cm"][1][:]
        self.assertEqual(self.measured()["status"], "FAIL")

    def test_diagonal_alternative_is_valid(self):
        self.m["evaluated"]["triangles"] = [t for q in self.m["evaluated"]["faces"]
                                                     for t in ([q[0], q[1], q[3]], [q[1], q[2], q[3]])]
        self.assertEqual(self.measured()["status"], "PASS")

    def test_actual_indices_need_not_be_row_major(self):
        for name in ("grid", "base", "evaluated"):
            stage = self.m[name]
            n = len(stage["vertices_cm"])
            stage["vertices_cm"].reverse()
            for key in ("faces", "triangles"):
                if key in stage:
                    stage[key] = [[n-1-i for i in f] for f in reversed(stage[key])]
        self.assertEqual(self.measured()["status"], "PASS")

    def test_explicit_mm_adapter_one_based(self):
        raw = {"evidence": self.m["evidence"]}
        for name in ("grid", "base", "evaluated"):
            src = self.m[name]
            raw[name] = {"vertices": [[10*x for x in v] for v in src["vertices_cm"]],
                         "faces": [[i+1 for i in f] for f in src["faces"]]}
            if "triangles" in src:
                raw[name]["triangles"] = [[i+1 for i in f] for f in src["triangles"]]
        self.m = oracle.adapt_capture(raw, cm_per_scene_unit=0.1, index_base=1)
        self.assertEqual(self.measured()["status"], "PASS")

    def test_wrong_scale_fails(self):
        for stage in ("grid", "base", "evaluated"):
            self.m[stage]["vertices_cm"] = [[10*x for x in v] for v in self.m[stage]["vertices_cm"]]
        self.assertEqual(self.measured()["status"], "FAIL")

    def test_overlap_refused(self):
        self.w["openings"][1]["u_range_cm"] = [140, 240]
        self.assertEqual(self.pred()["status"], "FAIL")

    def test_top_touching_opening_incomplete(self):
        self.w["openings"][1]["head_cm"] = 300
        self.assertEqual(self.pred()["status"], "INCOMPLETE")

    def test_multiple_runs_incomplete_not_subset_extraction(self):
        self.w["wall_runs"].append(deepcopy(self.w["wall_runs"][0]))
        self.assertEqual(self.pred()["status"], "INCOMPLETE")

    def test_directed_facade_subsegment_checked(self):
        self.d["facades"][0]["end_corner_cm"] = [400, 50]
        bind(self.w, self.d, self.a)
        r = self.pred()
        self.assertCheck(r, "SOURCE_CONTOUR", "FAIL")

    def test_no_mutation_of_locked_sources_or_captures(self):
        before = deepcopy((self.w, self.d, self.a, self.m))
        self.measured()
        self.assertEqual((self.w, self.d, self.a, self.m), before)

    def test_vertex_pinch_not_just_open_edge_count(self):
        # Two separate tetrahedra sharing exactly one vertex ID have no boundary
        # edges but a disconnected link at that vertex: not a manifold.
        faces = [[0,2,1],[0,1,3],[1,2,3],[2,0,3],
                 [0,5,4],[0,4,6],[4,5,6],[5,0,6]]
        stats = oracle.topology(7, faces)
        self.assertEqual(stats["boundary_edges"], 0)
        self.assertGreater(stats["bad_vertex_links"], 0)

    def test_operational_limit_is_not_pass(self):
        r = oracle.predict(self.w, self.d, self.a, max_cells=14)
        self.assertEqual(r["status"], "INCOMPLETE")

    def test_translated_diagonal_wall_general_physical_frame(self):
        # Exact 3-4-5 rotation. Physical authority, wall and independently authored
        # capture are transformed separately; no prediction arrays are read.
        def xy(x, y):
            return [100 + 0.6*x - 0.8*y, -50 + 0.8*x + 0.6*y]
        for rec in (self.w["wall_runs"][0], self.a):
            rec["start_cm"] = xy(0, 0)
            rec["end_cm"] = xy(400, 0)
            rec["base_z_cm"], rec["top_z_cm"] = 20, 320
            rec["outward"] = [0.8, -0.6]
        self.w["blocks"][0]["z_range_cm"] = [20, 320]
        self.d["facades"][0]["start_corner_cm"] = xy(0, 0)
        self.d["facades"][0]["end_corner_cm"] = xy(400, 0)
        bind(self.w, self.d, self.a)
        for stage in ("grid", "base", "evaluated"):
            self.m[stage]["vertices_cm"] = [xy(x, y)+[z+20] for x, y, z in self.m[stage]["vertices_cm"]]
        self.m["evidence"]["source_hashes"] = deepcopy(self.a["source_hashes"])
        r = self.measured()
        self.assertEqual(r["status"], "PASS", [c for c in r["checks"] if c["status"] != "PASS"])
        self.assertAlmostEqual(r["measured"]["signed_volume_cm3"], 2610000)

    def test_door_alone_not_artificially_given_threshold(self):
        self.w["openings"] = self.w["openings"][:1]
        self.a["openings"] = self.a["openings"][:1]
        bind(self.w, self.d, self.a)
        p = self.pred()["prediction"]
        self.assertEqual(p["source_area_cm2"], 99000)
        self.assertEqual(p["base_topology"]["boundary_components"], 1)
        self.assertEqual(p["base_topology"]["euler"], 1)
        self.assertEqual(p["evaluated_triangles"], 44)

    def test_window_alone_has_two_boundary_components(self):
        self.w["openings"] = self.w["openings"][1:]
        self.a["openings"] = self.a["openings"][1:]
        bind(self.w, self.d, self.a)
        p = self.pred()["prediction"]
        self.assertEqual(p["source_area_cm2"], 108000)
        self.assertEqual(p["base_topology"]["boundary_components"], 2)
        self.assertEqual(p["base_topology"]["euler"], 0)
        self.assertEqual(p["evaluated_triangles"], 64)

    def test_no_openings_is_supported_not_missing_void_pass(self):
        self.w["openings"], self.a["openings"] = [], []
        bind(self.w, self.d, self.a)
        p = self.pred()["prediction"]
        self.assertEqual(p["volume_cm3"], 3600000)
        self.assertEqual(p["shell_topology"]["euler"], 2)
        self.assertEqual(p["evaluated_triangles"], 12)

    def test_touching_openings_incomplete(self):
        self.w["openings"][1]["u_range_cm"] = [150, 250]
        self.assertEqual(self.pred()["status"], "INCOMPLETE")

    def test_overflow_is_clean_failure_not_exception(self):
        self.w["wall_runs"][0]["start_cm"] = [-1e308, 0]
        self.w["wall_runs"][0]["end_cm"] = [1e308, 0]
        self.assertEqual(self.pred()["status"], "FAIL")

    def test_malformed_objects_fail_without_internal_exception(self):
        for mutate in (lambda: self.w.update(wall_runs=[None]),
                       lambda: self.d.update(facades=None),
                       lambda: self.w.update(blocks=None)):
            self.setUp()
            mutate()
            self.assertIn(self.pred()["status"], ("FAIL", "INCOMPLETE"))

    def test_missing_capture_binding_is_incomplete(self):
        del self.m["evidence"]["source_hashes"]
        self.assertEqual(self.measured()["status"], "INCOMPLETE")

    def test_capture_budget_bool_fails(self):
        self.w["wall_runs"][0]["topology_budget"]["max_grid_polygons"] = True
        bind(self.w, self.d, self.a)
        self.assertEqual(self.pred()["status"], "FAIL")

    def authority_record(self):
        import json
        self.wbytes = json.dumps(self.w, ensure_ascii=False).encode("utf-8")
        return {"schema_version": "p3-direction-authority-1", "project": self.w["project"],
                "wall_run_id": "RUN", "walls_sha256": sha256(self.wbytes).hexdigest(),
                "source_file": "Audit/AGENT_PLAN_poly_surface_shell.md",
                "source_sha256": sha256(PLAN.read_bytes()).hexdigest(), "source_location": "G.1",
                "inner_start_cm": [0, 0], "inner_end_cm": [400, 0], "base_z_cm": 0,
                "top_z_cm": 300, "outward": [0, -1]}

    def test_f01_closed_authority_adapter_reads_actual_plan(self):
        record = self.authority_record()
        self.a = oracle.physical_from_f01_authority(self.w, self.d, record,
                         walls_bytes=self.wbytes, source_bytes=PLAN.read_bytes(), reviewer="offline-test")
        self.assertEqual(self.measured()["status"], "PASS")

    def test_f01_authority_adapter_does_not_copy_wrong_wall_openings(self):
        self.w["openings"][1]["u_range_cm"] = [220, 340]
        record = self.authority_record()
        self.a = oracle.physical_from_f01_authority(self.w, self.d, record,
                         walls_bytes=self.wbytes, source_bytes=PLAN.read_bytes(), reviewer="offline-test")
        self.assertCheck(self.pred(), "SOURCE_OPENINGS", "FAIL")

    def test_f01_authority_adapter_refuses_opposite_physical_claim(self):
        record = self.authority_record()
        record["outward"] = [0, 1]
        with self.assertRaises(oracle.OracleProblem) as caught:
            oracle.physical_from_f01_authority(self.w, self.d, record,
                         walls_bytes=self.wbytes, source_bytes=PLAN.read_bytes(), reviewer="offline-test")
        self.assertEqual(caught.exception.status, "FAIL")

    def test_f01_authority_adapter_refuses_changed_actual_source(self):
        record = self.authority_record()
        with self.assertRaises(oracle.OracleProblem):
            oracle.physical_from_f01_authority(self.w, self.d, record,
                         walls_bytes=self.wbytes, source_bytes=b"different-source", reviewer="offline-test")

    def test_f01_literal_source_disagrees_even_with_matching_source_hash(self):
        record = self.authority_record()
        wrong_source = PLAN.read_bytes().replace("наружу `(0,−1,0)`".encode(), "наружу `(0,1,0)`".encode())
        record["source_sha256"] = sha256(wrong_source).hexdigest()
        with self.assertRaises(oracle.OracleProblem) as caught:
            oracle.physical_from_f01_authority(self.w, self.d, record,
                         walls_bytes=self.wbytes, source_bytes=wrong_source, reviewer="offline-test")
        self.assertEqual(caught.exception.status, "INCOMPLETE")

    def test_full_actual_schema_triangle_only_checks_run_but_incomplete(self):
        raw, _ = full_measurement_capture(self.m)
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"], expected_units=raw["units"])
        self.assertEqual(r["status"], "INCOMPLETE")
        self.assertCheck(r, "GRID_CAPTURE", "INCOMPLETE")
        self.assertCheck(r, "EVALUATED_CAPTURE", "INCOMPLETE")
        for name in ("EVALUATED_PHYSICAL_DIRECTION", "TRIANGLE_VOLUME", "TRIANGLE_VOID_AND_SOLID_COVERAGE",
                     "TRIANGLE_NORMALS", "BASE_SOURCE_AREA", "BASE_COVERAGE"):
            self.assertCheck(r, name, "PASS")
        self.assertEqual(r["profiles"]["evaluated_triangles"]["status"], "PASS")
        self.assertEqual(r["measured"]["signed_volume_cm3"], 2610000)
        self.assertEqual(r["measured"]["source_area_cm2"], 87000)
        self.assertNotIn("evaluated_topology", r["measured"])

    def test_existing_independent_adapter_is_compatible_with_core(self):
        adapter_path = Path(__file__).with_name("phase16-p3-measurement-2026-11-02e") / "adapter.py"
        spec = importlib.util.spec_from_file_location("independent_measurement_adapter", adapter_path)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        raw, grid = full_measurement_capture(self.m)
        normalized = adapter.oracle_capture(raw, self.m["evidence"], grid_raw=grid)
        r = oracle.check_measurements(self.pred(), normalized)
        self.assertEqual(r["status"], "INCOMPLETE")
        self.assertCheck(r, "GRID_TOPOLOGY", "PASS")
        self.assertCheck(r, "EVALUATED_CAPTURE", "INCOMPLETE")
        self.assertCheck(r, "TRIANGLE_VOID_AND_SOLID_COVERAGE", "PASS")
        self.assertEqual(r["profiles"]["evaluated_triangles"]["status"], "PASS")
        own_normalized = oracle.adapt_independent_measurement(raw, self.m["evidence"], grid_raw=grid)
        for name in ("grid", "base", "evaluated"):
            for key in ("vertices_cm", "index_base", "faces", "triangles"):
                self.assertEqual(own_normalized[name].get(key), normalized[name].get(key))

    def test_full_schema_equal_factor_different_unit_pair_fails(self):
        raw, _ = full_measurement_capture(self.m)
        expected = {"system_type": "centimeters", "system_scale": 0.1, "scene_units_per_cm": 10}
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"], expected_units=expected)
        self.assertCheck(r, "INDEPENDENT_CAPTURE_UNITS", "FAIL")
        self.assertCheck(r, "TRIANGLE_VOLUME", "PASS")
        self.assertEqual(r["status"], "FAIL")

    def test_full_schema_missing_expected_units_incomplete(self):
        raw, _ = full_measurement_capture(self.m)
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"])
        self.assertCheck(r, "INDEPENDENT_CAPTURE_UNITS", "INCOMPLETE")

    def test_full_schema_property_read_issues_not_dropped(self):
        raw, grid = full_measurement_capture(self.m)
        raw["issues"] = ["unsupported modifier property class"]
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"], expected_units=raw["units"])
        self.assertCheck(r, "INDEPENDENT_CAPTURE_ISSUES", "INCOMPLETE")
        self.assertCheck(r, "TRIANGLE_VOLUME", "PASS")

    def test_full_schema_does_not_transform_snapshot_again(self):
        raw, _ = full_measurement_capture(self.m)
        raw["target"]["object_transform"][3] = [370,-190,110]
        normalized = oracle.adapt_independent_measurement(raw, self.m["evidence"])
        self.assertEqual(normalized["evaluated"]["vertices_cm"], self.m["evaluated"]["vertices_cm"])
        self.assertEqual(normalized["base"]["vertices_cm"], self.m["base"]["vertices_cm"])

    def test_full_schema_grid_identity_mismatch_refused(self):
        raw, grid = full_measurement_capture(self.m)
        grid["target"]["anim_handle"] = "not-the-same-node"
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"], grid_raw=grid, expected_units=raw["units"])
        self.assertCheck(r, "INDEPENDENT_CAPTURE_ADAPTER", "FAIL")

    def test_full_schema_summary_echo_not_used(self):
        raw, _ = full_measurement_capture(self.m)
        raw["evaluated"]["absolute_volume_scene3"] = 2610000000
        raw["evaluated"]["signed_volume_scene3"] = 2610000000
        for v in raw["evaluated"]["vertices"]:
            v[1] = -v[1]
        raw["evaluated"]["triangles"] = [list(reversed(f)) for f in raw["evaluated"]["triangles"]]
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"], expected_units=raw["units"])
        self.assertCheck(r, "TRIANGLE_VOLUME", "PASS")
        self.assertCheck(r, "EVALUATED_PHYSICAL_DIRECTION", "FAIL")
        self.assertEqual(r["profiles"]["evaluated_triangles"]["status"], "FAIL")

    def test_full_schema_short_path_envelope_incomplete_not_pass(self):
        raw = {"status": "CAPTURED_NOT_ACCEPTED", "path": "a-file.json", "sha256": "0"*64,
               "base_active_counts": [24,36,12], "evaluated_triangles":96}
        r = oracle.check_independent_capture(self.pred(), raw, self.m["evidence"])
        self.assertCheck(r, "INDEPENDENT_CAPTURE_ADAPTER", "INCOMPLETE")
        self.assertNotEqual(r["status"], "PASS")

    def test_full_schema_does_not_mutate_capture(self):
        raw, grid = full_measurement_capture(self.m)
        before = deepcopy((raw, grid))
        oracle.check_independent_capture(self.pred(), raw, self.m["evidence"], grid_raw=grid, expected_units=raw["units"])
        self.assertEqual((raw, grid), before)


if __name__ == "__main__":
    unittest.main()
