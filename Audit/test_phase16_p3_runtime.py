"""Offline planning/source guards ONLY; this suite never connects to 3ds Max."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from wall_surface_runtime import build_plan, generate_script, generate_arm_script, OPERATIONAL_CAPS


def fixture():
    """Analytical F01 values, not a produced artifact or live observation."""
    dims = {"spec": "dimensions", "project": "p3-runtime-offline-test", "status": "locked",
            "units": {"length": "cm"}, "facades": [{"id": "F01", "start_corner_cm": [0, 0],
            "end_corner_cm": [400, 0], "length_cm": 400}]}
    walls = {"spec": "walls", "project": dims["project"], "status": "locked", "units": {"length": "cm"},
             "wall_technique": "poly_surface_shell_v1", "reference_face": "inner",
             "numeric_epsilon_cm": 0.001, "numeric_unit_epsilon": 0.000001,
             "blocks": [{"id": "B", "z_range_cm": [0, 300]}], "upper_returns": [],
             "wall_runs": [{"id": "W", "block_id": "B", "contour_ref": "dimensions.json:facades:F01",
                "start_cm": [0, 0], "end_cm": [400, 0], "outward": [0, -1],
                "thickness_cm": 30, "base_z_cm": 0, "top_z_cm": 300,
                "topology_budget": {"max_grid_polygons": 32, "max_base_active_polygons": 32,
                                    "max_evaluated_triangles": 256}}],
             "openings": [{"id": "D", "wall_run_id": "W", "kind": "door", "u_range_cm": [50, 150],
                           "sill_cm": 0, "head_cm": 210},
                          {"id": "O", "wall_run_id": "W", "kind": "window", "u_range_cm": [230, 330],
                           "sill_cm": 90, "head_cm": 210}]}
    return walls, dims


UNITS = {"system_type": "millimeters", "system_scale": 1.0,
         "cm_per_unit": 0.1, "units_per_cm": 10.0}
IDENTITY = hashlib.sha256(b"offline-test-only").hexdigest()


def explicit_throws_in_catches(source: str) -> list[str]:
    """Structural check, not a MAXScript compiler or proof of live behavior.

    Ignore quoted strings/comments, balance catch bodies and reject arguments
    following a throw token within them. Bare generated rethrows end their body.
    """
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|--[^\n]*|[A-Za-z_][A-Za-z_0-9]*|[^\s]', source)
    tokens = [t for t in tokens if not t.startswith('"') and not t.startswith("--")]
    failures = []
    for index, token in enumerate(tokens):
        if token.lower() != "catch" or index+1 >= len(tokens) or tokens[index+1] != "(":
            continue
        depth = 0
        for cursor in range(index+1, len(tokens)):
            current = tokens[cursor]
            if current == "(":
                depth += 1
            elif current == ")":
                depth -= 1
                if depth == 0:
                    break
            if current.lower() == "throw" and cursor+1 < len(tokens) and tokens[cursor+1] != ")":
                failures.append(" ".join(tokens[cursor:cursor+4]))
    return failures


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.walls, self.dims = fixture()

    def plan(self):
        return build_plan(self.walls, self.dims)

    def runrow(self):
        return self.walls["wall_runs"][0]

    def test_f01_station_grid(self):
        p = self.plan()
        self.assertEqual(p["grid"]["u_cm"], [0, 50, 150, 230, 330, 400])
        self.assertEqual(p["grid"]["v_cm"], [0, 90, 210, 300])
        self.assertEqual(len(p["grid"]["vertices_cm"]), 24)
        self.assertEqual([i+1 for i, c in enumerate(p["grid"]["cells"]) if c["opening_id"]], [2, 7, 9])

    def test_f01_predictions_are_labelled_not_measured(self):
        p = self.plan()["predictions"]
        expected = {"grid_vertices": 24, "grid_edges": 38, "grid_polygons": 15,
                    "base_active_polygons": 12, "base_active_edges": 36, "base_boundary_edges": 24,
                    "base_area_cm2": 87000, "evaluated_polygons": 48, "evaluated_triangles": 96,
                    "volume_cm3": 2610000, "bounds_cm": [[0, -30, 0], [400, 0, 300]]}
        for key, value in expected.items():
            self.assertEqual(p[key], value, key)
        self.assertEqual(p["label"], "offline_predictions_not_measurements")

    def test_pure_and_deterministic(self):
        before = deepcopy((self.walls, self.dims))
        self.assertEqual(self.plan(), self.plan())
        self.assertEqual(before, (self.walls, self.dims))

    def test_opening_order_does_not_change_geometry(self):
        before = self.plan()
        self.walls["openings"].reverse()
        self.assertEqual(before, self.plan())

    def test_shared_slots_not_duplicate_geometric_vertices(self):
        p = self.plan()
        left, right = p["grid"]["cells"][:2]
        self.assertEqual(set(left["vertex_slots"]) & set(right["vertex_slots"]), {2, 8})
        self.assertEqual(len({tuple(v) for v in p["grid"]["vertices_cm"]}), 24)

    def test_reversed_outward_changes_winding_not_volume(self):
        p = self.plan()
        self.runrow()["outward"] = [0, 1]
        q = self.plan()
        self.assertEqual(q["grid"]["cells"][0]["vertex_slots"], p["grid"]["cells"][0]["vertex_slots"][::-1])
        self.assertEqual(q["predictions"]["volume_cm3"], p["predictions"]["volume_cm3"])
        self.assertEqual(q["predictions"]["bounds_cm"], [[0, 0, 0], [400, 30, 300]])

    def test_near_unit_vector_not_used_as_skew_offset(self):
        self.runrow()["outward"] = [0.0000001, -0.9999999]
        p = self.plan()
        self.assertEqual(p["geometric_normal"], [0, -1])
        self.assertEqual(p["predictions"]["bounds_cm"], [[0, -30, 0], [400, 0, 300]])

    def test_analytic_diagonal_not_axis_assumed(self):
        self.runrow()["end_cm"] = [240, 320]
        self.runrow()["outward"] = [0.8, -0.6]
        self.dims["facades"][0]["end_corner_cm"] = [240, 320]
        p = self.plan()
        self.assertEqual(p["length_cm"], 400)
        self.assertEqual(p["grid"]["vertices_cm"][1], [30, 40, 0])

    def test_door_no_sill_strip(self):
        p = self.plan()
        self.assertEqual(p["grid"]["cells"][1]["opening_id"], "D")
        self.assertEqual(p["grid"]["v_cm"][0], 0)

    def test_unsupported_subset_refused(self):
        for key, value in (("blocks", self.walls["blocks"]*2), ("wall_runs", self.walls["wall_runs"]*2),
                           ("upper_returns", [{}]), ("reference_face", "outer"), ("wall_technique", "legacy_cells_v1"),
                           ("status", "draft")):
            with self.subTest(key=key):
                w, d = fixture()
                w[key] = value
                with self.assertRaises(ValueError):
                    build_plan(w, d)

    def test_invalid_vectors_refused(self):
        for vector in ([0, 0], [1, 0], [0, 2], [float("nan"), -1], [True, -1]):
            with self.subTest(vector=vector):
                self.runrow()["outward"] = vector
                with self.assertRaises(ValueError):
                    self.plan()

    def test_zero_or_invalid_dimension_refused(self):
        for value in (0, -1, float("inf"), True, 10**400):
            with self.subTest(value=str(value)[:20]):
                self.runrow()["thickness_cm"] = value
                with self.assertRaises(ValueError):
                    self.plan()

    def test_bad_opening_boundaries_refused(self):
        for span, sill, head in (([0, 150], 0, 210), ([50, 400], 0, 210), ([150, 50], 0, 210),
                                 ([50, 150], -1, 210), ([50, 150], 210, 210), ([50, 150], 0, 300)):
            with self.subTest(span=span, sill=sill, head=head):
                self.walls["openings"][0].update(u_range_cm=span, sill_cm=sill, head_cm=head)
                with self.assertRaises(ValueError):
                    self.plan()

    def test_touching_and_overlapping_openings_refused(self):
        for lo in (149, 150):
            self.walls["openings"][1]["u_range_cm"] = [lo, 330]
            with self.assertRaises(ValueError):
                self.plan()

    def test_near_stations_refused_not_snapped(self):
        self.walls["openings"][1]["head_cm"] = 210.0001
        with self.assertRaisesRegex(ValueError, "near-stations"):
            self.plan()

    def test_lower_declared_budget_honored(self):
        for key, count in (("max_grid_polygons", 14), ("max_base_active_polygons", 11),
                           ("max_evaluated_triangles", 95)):
            w, d = fixture()
            w["wall_runs"][0]["topology_budget"][key] = count
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                build_plan(w, d)

    def test_invalid_budget_not_bool(self):
        self.runrow()["topology_budget"]["max_grid_polygons"] = True
        with self.assertRaises(ValueError):
            self.plan()

    def test_caps_not_relaxed_by_declaration(self):
        self.runrow()["topology_budget"] = {key: 100000 for key in self.runrow()["topology_budget"]}
        self.walls["openings"][1]["head_cm"] = 220
        self.walls["openings"].append({"id": "O3", "wall_run_id": "W", "kind": "window",
                                      "u_range_cm": [350, 380], "sill_cm": 110, "head_cm": 230})
        with self.assertRaisesRegex(ValueError, "operational grid"):
            self.plan()

    def test_facade_conflict_refused(self):
        self.dims["facades"][0]["start_corner_cm"] = [1, 0]
        with self.assertRaisesRegex(ValueError, "endpoints"):
            self.plan()

    def test_duplicate_facade_identity_refused(self):
        self.dims["facades"] *= 2
        with self.assertRaises(ValueError):
            self.plan()

    def test_duplicate_opening_identity_and_foreign_run_refused(self):
        for key, value in (("id", "D"), ("wall_run_id", "unknown")):
            self.walls["openings"][1][key] = value
            with self.assertRaises(ValueError):
                self.plan()

    def test_absolute_caps_are_explicit(self):
        self.assertEqual(OPERATIONAL_CAPS, {"grid_polygons": 32, "grid_vertices": 64,
                         "evaluated_triangles": 256, "openings": 6, "nodes": 1, "modifiers": 1})


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.walls, self.dims = fixture()
        self.plan = build_plan(self.walls, self.dims)

    def emit(self, **kwargs):
        args = dict(plan=self.plan, identity=IDENTITY, namespace="P3RuntimeOffline", expected_units=UNITS)
        args.update(kwargs)
        return generate_script(**args)

    def test_deterministic_emission_and_no_input_writes(self):
        before = deepcopy(self.plan)
        self.assertEqual(self.emit(), self.emit())
        self.assertEqual(before, self.plan)

    def test_invalid_namespace_and_identity(self):
        for namespace in ("", "_bad", "x y", "x\";delete objects", "a"*41, "ä"):
            with self.subTest(namespace=namespace), self.assertRaises(ValueError):
                self.emit(namespace=namespace)
        for identity in ("", "F"*64, "a"*63, "a"*65):
            with self.subTest(identity=identity), self.assertRaises(ValueError):
                self.emit(identity=identity)

    def test_expected_units_closed_and_canonical(self):
        for change in ({"system_type": "#millimeters"}, {"system_type": "Millimeters"},
                       {"system_type": []},
                       {"system_scale": True}, {"system_scale": float("nan")},
                       {"system_scale": 0}, {"system_scale": 0.1},
                       {"cm_per_unit": 1}, {"units_per_cm": 1}, {"extra": 1}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.emit(expected_units={**UNITS, **change})

    def test_same_factor_different_pair_remains_distinct(self):
        alternate = {"system_type": "centimeters", "system_scale": 0.5,
                     "cm_per_unit": 0.5, "units_per_cm": 2}
        other = {"system_type": "millimeters", "system_scale": 5,
                 "cm_per_unit": 0.5, "units_per_cm": 2}
        a, b = self.emit(expected_units=alternate), self.emit(expected_units=other)
        self.assertNotEqual(a, b)
        self.assertIn("actualType == #centimeters", a)
        self.assertIn("actualScale == 0.5d0", a)
        self.assertIn("actualType == #millimeters", b)

    def test_float32_indistinguishable_world_vertices_refused(self):
        for w, d in ((self.walls, self.dims),):
            w["wall_runs"][0]["start_cm"] = [10**9, 0]
            w["wall_runs"][0]["end_cm"] = [10**9+400, 0]
            d["facades"][0]["start_corner_cm"] = [10**9, 0]
            d["facades"][0]["end_corner_cm"] = [10**9+400, 0]
            p = build_plan(w, d)
            with self.assertRaisesRegex(ValueError, "Float32"):
                self.emit(plan=p)

    def test_float32_indistinguishable_thickness_refused(self):
        self.walls["wall_runs"][0]["start_cm"] = [0, 10**9]
        self.walls["wall_runs"][0]["end_cm"] = [400, 10**9]
        self.walls["wall_runs"][0]["thickness_cm"] = 0.001
        self.dims["facades"][0].update(start_corner_cm=[0, 10**9], end_corner_cm=[400, 10**9])
        with self.assertRaisesRegex(ValueError, "Float32"):
            self.emit(plan=build_plan(self.walls, self.dims))

    def test_tampered_plan_predictions_or_cells_refuse(self):
        for field in ("predictions", "grid", "operational_caps"):
            p = deepcopy(self.plan)
            p[field] = {}
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.emit(plan=p)

    def test_units_guard_before_constructor_or_registry(self):
        source = self.emit()
        start = source.index("-- Must precede even replay inspection")
        self.assertLess(source.index("p3UnitsGuard()", start), source.index("globalVars.isGlobal registryKey", start))
        self.assertLess(source.index("p3UnitsGuard()", start), source.index("local node = Editable_Mesh()", start))
        self.assertIn("actualScale == actualScale", source)
        self.assertIn("cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0", source)

    def test_returned_ids_not_assumed_row_major_ids(self):
        source = self.emit()
        self.assertIn("local id = polyop.createVert node point", source)
        self.assertIn("vertexIds[index]", source)
        self.assertIn("local id = polyop.createPolygon node actualLoop", source)
        self.assertIn("cutIds[id] = true", source)
        self.assertEqual(source.count("polyop.deleteFaces node"), 1)
        self.assertIn("P3_VERTEX_IDS|", source)
        self.assertIn("P3_FACE_IDS|", source)
        self.assertIn("P3_BASE_READBACK|", source)

    def test_no_dangerous_operations_or_name_recovery(self):
        source = self.emit()
        for forbidden in ("getNodeByName", "resetMaxFile", "saveMaxFile", "setSaveRequired", "formattedPrint",
                          "delete objects", "delete $", "units.SystemType =", "units.SystemScale =",
                          "Extrude(", "Boolean(", "undo "):
            self.assertNotIn(forbidden, source)
        self.assertEqual(source.count("addModifier node shellMod"), 1)

    def test_registry_publication_only_after_baseline(self):
        source = self.emit()
        self.assertNotIn("globalVars.set", source)
        self.assertLess(source.index("baseline = p3NodeSnapshot node"), source.index('lease[5] = "COMMITTED"'))
        replay = source[source.index('stage = "replay-read-only"'):source.index('stage = "pre-create"')]
        for write in ("delete ", "setUserProp", "globalVars.set", "addModifier", "convertTo "):
            self.assertNotIn(write, replay)

    def test_missing_registry_refuses_not_auto_arms(self):
        source = self.emit()
        self.assertIn('p3RequireState (globalVars.isGlobal registryKey) "missing explicit armed session registry', source)
        self.assertIn('lease[5] == "ARMED"', source)
        self.assertIn('lease[5] = "POISONED"', source)
        self.assertNotIn('lease[5] = "ARMED"', source)

    def test_unproven_metadata_never_yields_noop_pass(self):
        source = self.emit()
        self.assertIn("P3_CREATED_UNVERIFIED|", source)
        self.assertIn("P3_REPLAY_NOOP|", source)
        self.assertIn("status=VERIFIED_NOOP", source)
        self.assertIn("p3SameState currentSnapshot lease[9]", source)

    def test_explicit_arm_and_struct_exact_witness(self):
        arm = generate_arm_script(self.plan, IDENTITY, "P3RuntimeOffline", UNITS,
                                  "FreshExplicitNonce0123456789")
        self.assertIn("if globalVars.isGlobal registryKey do throw", arm)
        self.assertIn("struct P3LocalLease", arm)
        self.assertIn("globalVars.set registryKey witness", arm)
        self.assertIn('execute ("global " + (registryKey as string))', arm)
        self.assertNotIn("delete ", arm)
        self.assertNotIn("Editable_Mesh", arm)
        self.assertLess(arm.index("unit pair mismatch"), arm.index("globalVars.set"))
        with self.assertRaises(ValueError):
            generate_arm_script(self.plan, IDENTITY, "P3RuntimeOffline", UNITS, "tiny")

    def test_full_baseline_guards_are_explicit(self):
        source = self.emit()
        for guard in ("p3PolySnapshot node.baseObject", "p3GraphSnapshot node", "p3ReadProperties node.layer", "getUserPropBuffer node",
                      "shellMod.enabledInViews", "shellMod.enabledInRenders", "#objectOffsetRot", "#material", "#parent",
                      "getAnimByHandle h", "refs.getNumRefs target", "refs.getReference target i", "refs.dependents target",
                      "polyop.getVDataValue", "polyop.getEDataValue", "polyop.getMapVert", "getFace msh i",
                      "numKeys target", "instanceUsers.count == 1", "copied-tag or matching-name collision"):
            self.assertIn(guard, source)

    def test_cleanup_exact_current_attempt_refs_only(self):
        source = self.emit()
        self.assertIn("for i = 1 to createdRefs.count", source)
        self.assertIn("exactNode = createdRefs[i]", source)
        self.assertIn("savedHandle = if i <= createdHandles.count then createdHandles[i]", source)
        self.assertIn("P3_INCOMPLETE_RESIDUAL", source)
        self.assertIn("local converted = convertTo node Editable_Poly", source)

    def test_no_stringified_geometry_fingerprint(self):
        source = self.emit()
        self.assertIn("p3FreezeState (polyop.getVert base i)", source)
        self.assertIn("p3FreezeState (getVert msh i)", source)
        self.assertNotIn("(node.transform as string)", source)

    def test_snapshot_memory_disposal_in_success_and_error(self):
        source = self.emit()
        reader = source[source.index("fn p3EvaluatedSnapshot node"):source.index("fn p3NodeSnapshot node")]
        self.assertGreaterEqual(reader.count("delete msh"), 2)
        self.assertIn("exact in-memory snapshot disposal failed", reader)

    def test_catches_only_bare_rethrow_not_explicit_arguments(self):
        arm = generate_arm_script(self.plan, IDENTITY, "P3RuntimeOffline", UNITS,
                                  "FreshExplicitNonce0123456789")
        self.assertEqual(explicit_throws_in_catches(self.emit()), [])
        self.assertEqual(explicit_throws_in_catches(arm), [])
        # Calibrate the structural detector on the actual previously failing forms.
        self.assertTrue(explicit_throws_in_catches('try (1) catch (throw ("diagnostic"))'))
        self.assertTrue(explicit_throws_in_catches('try (1) catch (throw reason)'))
        self.assertEqual(explicit_throws_in_catches('try (1) catch (print "throw reason"; throw)'), [])

    def test_all_emitted_helpers_are_p3_prefixed(self):
        source = self.emit()
        names = re.findall(r"\bfn\s+(\w+)", source)
        self.assertEqual(len(names), 16)
        self.assertTrue(all(name.startswith("p3") for name in names), names)
        self.assertIn("fn p3FreezeState value", source)
        self.assertNotRegex(source, r"\bfn\s+(?:freeze|require|same|properties|exactRef)\b")
        # Diagnostic text remains literal, rather than accidental token rewriting.
        self.assertIn("property enumeration unavailable/ceiling", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
