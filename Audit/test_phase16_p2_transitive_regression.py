#!/usr/bin/env python3
"""Targeted, offline Phase 16 wall-provenance regressions.

Run: python -B Audit/test_phase16_p2_transitive_regression.py -v

All data is hypothetical, in memory or in an isolated temporary project. The
registry control rewires ONE provenance declaration to actual grid inputs;
the checked-in examples are never edited. Passing does not prove the source,
the formula, the physical wall direction, or any produced/live geometry.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.validate_specs as validator

from test_phase16_p2_isolated import (
    EXAMPLES, Isolated, draft_assembly, synthetic_poly_assembly, walls_declaration, write_json,
)
from test_phase16_spatial_independent import g82, huge_sample, sample
import wall_cell_coverage as coverage


REGISTRY_PATH = "components[0].size_cm"
REGISTRY_INPUTS = ["panels[71].width_cm", "panels[71].height_cm",
                   "defaults.panel_thickness_cm"]
SOURCE_PATHS = [ROOT / "scripts" / name for name in
                ("validate_specs.py", "curve_gen.py", "wall_cell_coverage.py")]
SOURCE_PATHS += [Path(__file__).resolve(),
                 ROOT / "Audit" / "test_phase16_p2_isolated.py",
                 ROOT / "Audit" / "test_phase16_spatial_independent.py"]
SOURCE_PATHS += sorted(p for p in EXAMPLES.rglob("*") if p.is_file())
SOURCE_HASHES = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE_PATHS}


def tearDownModule():
    after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE_PATHS}
    changed = [str(p.relative_to(ROOT)) for p in SOURCE_HASHES if SOURCE_HASHES[p] != after[p]]
    print("SOURCE_DRIFT " + repr(changed), flush=True)
    for path in SOURCE_PATHS[:6]:
        print(str(path.relative_to(ROOT)) + " " + SOURCE_HASHES[path] + " -> " + after[path],
              flush=True)
    if changed:
        raise AssertionError("source/fixture drift invalidates this run: " + repr(changed))


def nested_json(depth, value="0", *, objects=False):
    prefix, suffix = ('{"probe":', '}') if objects else ('[', ']')
    return prefix * depth + value + suffix * depth


def calibrate_registry_inputs(dimensions: dict, registry: dict) -> None:
    """Correct two historical provenance declarations in this disposable input.

    C-002 claims only opening 11's head, not the rest of the opening. Splitting
    that collapsed origin avoids treating a partially covered element as sound.
    """
    origins = dimensions["origins"]
    conflict = origins.pop("openings[11]")
    assert conflict == {"origin": "conflict", "origin_ref": "C-002"}
    for leaf in validator.collect_leaves(dimensions, validator.SPEC_BY_NAME["dimensions"]):
        if leaf.startswith("openings[11]."):
            origins[leaf] = conflict if leaf == "openings[11].head_cm" else {"origin": "given"}
    registry["origins"][REGISTRY_PATH]["derives_from"] = REGISTRY_INPUTS[:]


def make_control(path: str, acyclic_registry: bool = False) -> dict:
    docs = {p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in EXAMPLES.glob("*.json") if p.stem in validator.SPEC_BY_NAME}
    docs["walls"] = walls_declaration(docs["dimensions"])
    docs["walls"]["origin_inputs"] = [path]
    docs["assembly"] = synthetic_poly_assembly(docs["assembly"])
    if acyclic_registry:
        component = docs["components_registry"]["components"][0]
        panel = docs["facade_grids"]["panels"][71]
        assert component["size_cm"] == [panel["width_cm"], panel["height_cm"],
                                        docs["components_registry"]["defaults"]["panel_thickness_cm"]]
        assert panel["kind"] in component["serves_panel_kinds"]
        calibrate_registry_inputs(docs["dimensions"], docs["components_registry"])
    return docs


def run(docs: dict, *, build: bool = False) -> validator.Report:
    session = validator.Session([
        validator.LoadedFile(Path(name + ".json"), name + ".json",
                             spec=validator.SPEC_BY_NAME[name], doc=value)
        for name, value in sorted(docs.items())
    ], build_gate=build)
    report = validator.Report()
    validator.run_checks(session, report)
    return report


class TransitiveProvenance(unittest.TestCase):
    def rows(self, report, gate, location=None, severity=None):
        return [f for f in report.findings if f.rule == gate
                and (location is None or location in f.location)
                and (severity is None or f.severity == severity)]

    def control(self, path, *, registry=False):
        docs = make_control(path, registry)
        report = run(docs)
        failures = [f for f in report.findings if f.severity == "FAIL"]
        self.assertFalse(failures, failures)
        for gate, where in (("G-31", "dimensions.json"), ("G-10", "walls.json"),
                            ("G-93", "walls.json")):
            self.assertTrue(self.rows(report, gate, where, "PASS"), (gate, report.findings))
        return docs

    def blocked(self, docs, message):
        report = run(docs)
        failures = self.rows(report, "G-93", "walls.json::origin_inputs", "FAIL")
        self.assertTrue(any(message in f.detail for f in failures), failures)
        self.assertFalse(self.rows(report, "G-10", "walls.json", "PASS"))
        self.assertFalse(self.rows(report, "G-93", "walls.json", "PASS"))
        self.assertFalse(self.rows(report, "G-31", severity="PASS"))
        self.assertFalse([f for f in report.findings if "internal error" in f.detail.lower()])
        return report

    def test_ledger_cross_reference_failure_cannot_pass_wall(self):
        docs = self.control("structure.x_bay_cm")
        item = docs["assumptions"]["cross_references"]["conflict_sourced_paths"][3]
        self.assertEqual(item["conflict_ref"], "C-003")
        item["conflict_ref"] = "C-999"
        report = self.blocked(docs, "structure.x_bay_cm")
        self.assertTrue(self.rows(report, "G-31", "assumptions.json::cross_references", "FAIL"))

    def test_invalid_registry_derived_path_is_not_masked_by_a_cycle(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        docs["components_registry"]["origins"][REGISTRY_PATH]["derives_from"] = ["NO_SUCH_FIELD"]
        report = self.blocked(docs, "NO_SUCH_FIELD")
        self.assertFalse(self.rows(report, "G-31", severity="FAIL"))
        self.assertTrue(self.rows(report, "G-31", "walls.json::origin_inputs", "SKIP"))

    def test_backward_registry_reference_is_not_masked_by_a_cycle(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        docs["components_registry"]["origin_inputs"] = ["wall_runs[0].thickness_cm"]
        report = self.blocked(docs, "components_registry.json upstream path 'wall_runs[0].thickness_cm'")
        self.assertFalse(self.rows(report, "G-31", severity="FAIL"))

    def test_superseded_massing_behind_nurbs_blocks_wall_in_lint(self):
        docs = self.control("sections[0].points_cm")
        docs["massing"]["status"] = "superseded"
        report = self.blocked(docs, "nurbs.json upstream path 'elements[8].z_range_cm'")
        self.assertTrue(self.rows(report, "G-4", "massing.json", "WARN"))

    def test_historical_registry_cycle_is_incomplete_not_pass(self):
        # The unmodified historical source is not a positive acyclic control.
        docs = self.control(REGISTRY_PATH, registry=True)
        original = make_control(REGISTRY_PATH)["components_registry"]["origins"][REGISTRY_PATH]
        docs["components_registry"]["origins"][REGISTRY_PATH] = original
        self.blocked(docs, "cyclic transitive provenance")

    def test_explicit_local_self_cycle_is_rejected(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        docs["components_registry"]["origins"][REGISTRY_PATH]["derives_from"] = [REGISTRY_PATH]
        self.blocked(docs, "cyclic transitive provenance")

    def test_explicit_local_two_entry_cycle_is_rejected(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        docs["components_registry"]["origins"][REGISTRY_PATH]["derives_from"] = ["components[0].parameters[0].value"]
        self.blocked(docs, "cyclic transitive provenance")

    def test_existing_but_unrelated_upstream_conflict_id_is_rejected(self):
        docs = self.control("structure.x_bay_cm")
        docs["dimensions"]["origins"]["structure.x_bay_cm"]["origin_ref"] = "C-004"
        report = self.blocked(docs, "C-004 does not cover dimensions.json::structure.x_bay_cm")
        self.assertFalse([f for f in report.findings if f.severity == "FAIL" and f.rule != "G-93"])

    def test_informational_conflict_ref_must_name_a_derived_input(self):
        docs = self.control("building.total_height_cm")
        origin = docs["dimensions"]["origins"]["building.total_height_cm"]
        self.assertEqual(origin["conflict_ref"], "C-001")
        self.assertEqual(origin["derives_from"], ["levels[0].height_cm", "levels[1].height_cm"])
        origin["conflict_ref"] = "C-004"
        report = self.blocked(docs, "conflict_ref C-004 is not bound")
        self.assertFalse([f for f in report.findings if f.severity == "FAIL" and f.rule != "G-93"])

    def test_existing_but_unrelated_registry_assumption_id_is_rejected(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        docs["components_registry"]["origins"]["defaults.panel_thickness_cm"]["origin_ref"] = "A-024"
        report = self.blocked(docs, "A-024 does not cover components_registry.json::defaults.panel_thickness_cm")
        self.assertFalse([f for f in report.findings if f.severity == "FAIL" and f.rule != "G-93"])

    def test_upstream_non_derived_annotation_does_not_claim_conflict_linkage(self):
        for path in ("roof.deck_thickness_cm", "site.plot_rotation_deg"):
            with self.subTest(path=path):
                docs = self.control(path)
                self.assertIn(docs["dimensions"]["origins"][path]["origin"], ("given", "assumed"))
                docs["dimensions"]["origins"][path]["conflict_ref"] = "C-001"
                report = self.blocked(docs, "conflict_ref annotates conflict-resolved derived inputs")
                self.assertFalse([f for f in report.findings if f.severity == "FAIL" and f.rule != "G-93"])

    def test_wall_given_annotation_does_not_claim_conflict_linkage(self):
        docs = self.control("structure.x_bay_cm")
        self.assertEqual(docs["walls"]["origins"]["wall_runs[0]"], {"origin": "given"})
        docs["walls"]["origins"]["wall_runs[0]"]["conflict_ref"] = "C-001"
        report = run(docs)
        self.assertTrue(self.rows(report, "G-10", "walls.json::wall_runs[0]", "FAIL"))
        for gate in ("G-10", "G-93"):
            self.assertFalse(self.rows(report, gate, "walls.json", "PASS"))

    def test_transitive_bad_ledger_value_is_rejected(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        entry = next(a for a in docs["assumptions"]["assumptions"] if a["id"] == "A-023")
        entry["value"] += 1.0
        report = self.blocked(docs, REGISTRY_PATH)
        self.assertTrue(self.rows(report, "G-12", "assumptions.json", "FAIL"))

    def test_missing_transitive_owner_is_rejected(self):
        docs = self.control("sections[0].points_cm")
        del docs["massing"]
        self.blocked(docs, "sections[0].points_cm")

    def test_transitive_malformed_reference_is_rejected(self):
        docs = self.control(REGISTRY_PATH, registry=True)
        docs["components_registry"]["origins"][REGISTRY_PATH]["derives_from"][0] = "panels[71]..width_cm"
        self.blocked(docs, "panels[71]..width_cm")

    def test_wall_derived_formula_and_physical_side_are_not_claimed(self):
        docs = self.control("structure.x_bay_cm")
        wall = docs["walls"]
        del wall["origins"]["wall_runs[0]"]
        for key in wall["wall_runs"][0]:
            if key != "id":
                wall["origins"][f"wall_runs[0].{key}"] = {"origin": "given"}
        wall["origins"]["wall_runs[0].thickness_cm"] = {
            "origin": "derived", "derives_from": ["structure.x_bay_cm"]}
        report = run(docs)
        self.assertFalse([f for f in report.findings if f.severity == "FAIL"])
        self.assertTrue(self.rows(report, "G-32", "walls.json::wall_runs[0].thickness_cm", "SKIP"))
        self.assertFalse(self.rows(report, "G-32", "walls.json", "PASS"))
        passes = self.rows(report, "G-93", "walls.json", "PASS")
        self.assertEqual(len(passes), 1)
        self.assertIn("outward sign and physical face require independent evidence", passes[0].detail)

    def test_wall_informational_conflict_ref_is_explicitly_unverified(self):
        docs = self.control("building.total_height_cm")
        wall = docs["walls"]
        del wall["origins"]["wall_runs[0]"]
        for key in wall["wall_runs"][0]:
            if key != "id":
                wall["origins"][f"wall_runs[0].{key}"] = {"origin": "given"}
        origin = {"origin": "derived", "derives_from": ["building.total_height_cm"]}
        wall["origins"]["wall_runs[0].thickness_cm"] = origin
        control = run(docs)
        self.assertFalse([f for f in control.findings if f.severity == "FAIL"])
        self.assertTrue(self.rows(control, "G-10", "walls.json", "PASS"))
        self.assertTrue(self.rows(control, "G-93", "walls.json", "PASS"))
        origin["conflict_ref"] = "C-001"
        result = run(docs)
        self.assertFalse([f for f in result.findings if f.severity == "FAIL"])
        self.assertTrue(self.rows(result, "G-10", "walls.json", "SKIP"))
        self.assertFalse(self.rows(result, "G-10", "walls.json", "PASS"))
        self.assertTrue(self.rows(result, "G-93", "walls.json", "SKIP"))
        self.assertFalse(self.rows(result, "G-93", "walls.json", "PASS"))

    def test_maximum_json_tree_depth_is_safe_when_reached_by_provenance(self):
        self.control("structure.x_bay_cm")
        docs = make_control("building.provenance_probe")
        # Root + building + the nested objects = the exact accepted limit.
        docs["dimensions"]["building"]["provenance_probe"] = validator.strict_json_loads(
            nested_json(validator.MAX_JSON_CONTAINER_DEPTH - 2, objects=True))
        docs["dimensions"]["origins"]["building.provenance_probe"] = {"origin": "given"}
        report = run(docs)
        self.assertFalse([f for f in report.findings if f.severity == "FAIL"], report.findings)
        self.assertTrue(self.rows(report, "G-10", "walls.json", "PASS"))
        self.assertTrue(self.rows(report, "G-93", "walls.json", "PASS"))

    def test_provenance_chain_longer_than_python_stack_is_iterative(self):
        docs = self.control("structure.x_bay_cm")
        count = sys.getrecursionlimit() + 20
        docs["dimensions"]["building"]["provenance_probe"] = {f"p{i}": 0 for i in range(count)}
        origins = docs["dimensions"]["origins"]
        for i in range(count):
            path = f"building.provenance_probe.p{i}"
            origins[path] = ({"origin": "derived", "derives_from": [f"building.provenance_probe.p{i + 1}"]}
                             if i < count - 1 else {"origin": "given"})
        docs["walls"]["origin_inputs"] = ["building.provenance_probe.p0"]
        report = run(docs)
        self.assertFalse([f for f in report.findings if f.severity == "FAIL"], report.findings)
        # Graph traversal is complete, but these synthetic pN derived values
        # have no formula oracle. Acyclicity alone is not wall provenance PASS.
        self.assertTrue(self.rows(report, "G-93", "walls.json", "SKIP"))
        self.assertFalse(self.rows(report, "G-93", "walls.json", "PASS"))
        origins[f"building.provenance_probe.p{count - 1}"] = {
            "origin": "derived", "derives_from": ["building.provenance_probe.p0"]}
        self.blocked(docs, "cyclic transitive provenance")


class FormulaFidelity(unittest.TestCase):
    rows = TransitiveProvenance.rows

    def control(self, path):
        docs = make_control(path)
        docs["assembly"] = draft_assembly(docs["assembly"])
        report = run(docs)
        self.assertFalse([f for f in report.findings if f.severity == "FAIL"], report.findings)
        self.assertTrue(self.rows(report, "G-10", "walls.json", "PASS"))
        self.assertTrue(self.rows(report, "G-93", "walls.json", "PASS"))
        return docs
    def test_wrong_total_height_dependencies_fail_g32_without_value_change(self):
        docs = self.control("building.total_height_cm")
        value = docs["dimensions"]["building"]["total_height_cm"]
        docs["dimensions"]["origins"]["building.total_height_cm"] = {
            "origin": "derived", "derives_from": ["site.ground_level_cm"]}
        report = run(docs)
        self.assertEqual(docs["dimensions"]["building"]["total_height_cm"], value)
        self.assertTrue(self.rows(report, "G-32", "dimensions.json::building.total_height_cm", "FAIL"))
        self.assertFalse(self.rows(report, "G-32", "dimensions.json", "PASS"))
        for gate in ("G-10", "G-93"):
            self.assertFalse(self.rows(report, gate, "walls.json", "PASS"))

    def test_supported_formula_input_coverage_is_not_value_coincidence(self):
        for path in ("building.overall_height_cm", "building.gross_floor_area_m2",
                     "building.net_floor_area_m2", "site.footprint_area_m2",
                     "site.footprint_width_cm", "site.footprint_depth_cm",
                     "structure.column_x_cm", "structure.column_y_cm",
                     "structure.interior_column_count", "levels[1].elevation_cm",
                     "core.footprint_area_m2", "floor_plates[0].gross_area_m2",
                     "roof.deck_level_cm"):
            with self.subTest(path=path):
                docs = self.control(path)
                docs["dimensions"]["origins"][path] = {
                    "origin": "derived", "derives_from": ["site.ground_level_cm"]}
                report = run(docs)
                self.assertTrue(self.rows(report, "G-32", "dimensions.json::" + path, "FAIL"))
                self.assertFalse(self.rows(report, "G-32", "dimensions.json", "PASS"))
                self.assertFalse(self.rows(report, "G-93", "walls.json", "PASS"))

    def test_total_height_direct_intermediates_and_declared_ancestors_are_valid(self):
        for sources in (["levels[1].elevation_cm", "levels[1].height_cm"], ["levels"]):
            with self.subTest(sources=sources):
                docs = self.control("building.total_height_cm")
                docs["dimensions"]["origins"]["building.total_height_cm"]["derives_from"] = sources
                report = run(docs)
                self.assertFalse([f for f in report.findings if f.severity == "FAIL"], report.findings)
                self.assertTrue(self.rows(report, "G-32", "dimensions.json", "PASS"))
                self.assertTrue(self.rows(report, "G-93", "walls.json", "PASS"))

    def test_missing_one_required_source_is_not_masked_by_an_unrelated_extra(self):
        docs = self.control("building.overall_height_cm")
        docs["dimensions"]["origins"]["building.overall_height_cm"]["derives_from"] = [
            "building.total_height_cm", "site.ground_level_cm"]
        report = run(docs)
        failures = self.rows(report, "G-32", "dimensions.json::building.overall_height_cm", "FAIL")
        self.assertTrue(any("roof.parapet_height_cm" in f.detail for f in failures), failures)
        self.assertFalse(self.rows(report, "G-93", "walls.json", "PASS"))

    def test_nonzero_height_base_cannot_be_omitted_from_height_closure(self):
        docs = self.control("building.total_height_cm")
        dim = docs["dimensions"]
        dim["levels"][0]["elevation_cm"] = 50
        sources = dim["origins"]["building.total_height_cm"]["derives_from"]
        self.assertEqual(validator._formula_missing_dependencies(dim, "building.total_height_cm", sources),
                         ["levels[0].elevation_cm"])
        self.assertEqual(validator._formula_missing_dependencies(dim, "building.total_height_cm",
                                                                 sources + ["levels[0].elevation_cm"]), [])

    def test_unknown_reached_formula_is_incomplete_in_lint_and_refused_in_build(self):
        docs = self.control("site.ground_level_cm")
        docs["dimensions"]["origins"]["site.ground_level_cm"] = {
            "origin": "derived", "derives_from": ["levels[0].elevation_cm"]}
        for build in (False, True):
            with self.subTest(build=build):
                report = run(docs, build=build)
                self.assertTrue(self.rows(report, "G-32", "dimensions.json::site.ground_level_cm", "SKIP"))
                self.assertTrue(self.rows(report, "G-10", "walls.json", "SKIP"))
                self.assertFalse(self.rows(report, "G-10", "walls.json", "PASS"))
                self.assertFalse(self.rows(report, "G-93", "walls.json", "PASS"))
                self.assertTrue(self.rows(report, "G-93", "walls.json", "FAIL" if build else "SKIP"))
                self.assertEqual(bool([f for f in report.findings if f.severity == "FAIL"]), build)

    def test_unreached_formula_skip_does_not_invalidate_an_independent_wall_input(self):
        docs = self.control("structure.x_bay_cm")
        docs["dimensions"]["origins"]["site.ground_level_cm"] = {
            "origin": "derived", "derives_from": ["levels[0].elevation_cm"]}
        report = run(docs)
        self.assertFalse([f for f in report.findings if f.severity == "FAIL"], report.findings)
        self.assertTrue(self.rows(report, "G-32", "dimensions.json::site.ground_level_cm", "SKIP"))
        self.assertTrue(self.rows(report, "G-93", "walls.json", "PASS"))

    def test_unknown_formula_is_propagated_through_a_supported_derived_value(self):
        docs = self.control("building.total_height_cm")
        docs["dimensions"]["origins"]["site.ground_level_cm"] = {
            "origin": "derived", "derives_from": ["levels[0].elevation_cm"]}
        docs["dimensions"]["origins"]["building.total_height_cm"]["derives_from"].append("site.ground_level_cm")
        report = run(docs)
        self.assertFalse([f for f in report.findings if f.severity == "FAIL"], report.findings)
        self.assertTrue(self.rows(report, "G-32", "dimensions.json", "PASS"))
        self.assertTrue(self.rows(report, "G-93", "walls.json", "SKIP"))
        self.assertFalse(self.rows(report, "G-93", "walls.json", "PASS"))


class CliTransitive(Isolated):
    def test_g32_dependency_failure_survives_file_and_rule_filter(self):
        self.walls["origin_inputs"] = ["building.total_height_cm"]
        self.save_walls()
        self.positive("G-93")
        self.dimensions["origins"]["building.total_height_cm"] = {
            "origin": "derived", "derives_from": ["site.ground_level_cm"]}
        write_json(self.pipeline / "dimensions.json", self.dimensions)
        result, report = self.validate("--rule", "G-32", target=("--file", self.pipeline / "walls.json"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["exit_code"], 1)
        self.assertTrue([r for r in self.rows(report, "G-32", "FAIL")
                         if "building.total_height_cm" in r["location"]])
        self.assertFalse(self.rows(report, "G-32", "PASS"))

    def test_unknown_reached_formula_lint_skip_and_build_refusal_are_honest(self):
        self.walls["origin_inputs"] = ["site.ground_level_cm"]
        self.save_walls()
        self.positive("G-93")
        self.dimensions["origins"]["site.ground_level_cm"] = {
            "origin": "derived", "derives_from": ["levels[0].elevation_cm"]}
        write_json(self.pipeline / "dimensions.json", self.dimensions)
        lint, report = self.validate()
        self.assertEqual(lint.returncode, 0, self.failures(report))
        for gate in ("G-10", "G-93"):
            self.assertTrue([r for r in self.rows(report, gate, "SKIP") if "walls.json" in r["location"]])
            self.assertFalse([r for r in self.rows(report, gate, "PASS") if "walls.json" in r["location"]])
        for flags in (("--build",), ("--build", "--allow-draft")):
            with self.subTest(flags=flags):
                result, built = self.validate(*flags, "--rule", "G-93",
                                              target=("--file", self.pipeline / "walls.json"))
                self.assertEqual(result.returncode, 1)
                self.assertEqual(built["exit_code"], 1)
                self.assertTrue([r for r in self.rows(built, "G-93", "FAIL")
                                 if "recomputation" in r["detail"]])
                self.assertFalse(self.rows(built, "G-93", "PASS"))

    def test_file_and_rule_filters_keep_full_failure_status(self):
        registry = json.loads((self.pipeline / "components_registry.json").read_text(encoding="utf-8"))
        calibrate_registry_inputs(self.dimensions, registry)
        write_json(self.pipeline / "dimensions.json", self.dimensions)
        self.walls["origin_inputs"] = [REGISTRY_PATH]
        self.save_walls()
        write_json(self.pipeline / "components_registry.json", registry)
        target = ("--file", self.pipeline / "walls.json")
        result, report = self.validate(target=target)
        self.assertEqual(result.returncode, 0, self.failures(report))
        self.assertTrue(self.rows(report, "G-10", "PASS"))
        self.assertTrue(self.rows(report, "G-93", "PASS"))
        registry["origins"][REGISTRY_PATH]["derives_from"] = ["NO_SUCH_FIELD"]
        write_json(self.pipeline / "components_registry.json", registry)
        for gate in ("G-10", "G-31", "G-93"):
            with self.subTest(rule=gate):
                process, filtered = self.validate("--rule", gate, target=target)
                self.assertEqual(process.returncode, 1)
                self.assertEqual(filtered["exit_code"], 1)
                self.assertFalse([r for r in self.rows(filtered, gate, "PASS")
                                  if "walls.json" in r["location"] or gate == "G-31"])
                if gate == "G-93":
                    self.assertTrue([r for r in self.rows(filtered, gate, "FAIL")
                                     if "NO_SUCH_FIELD" in r["detail"]])
                if gate == "G-31":
                    self.assertTrue([r for r in self.rows(filtered, gate, "SKIP")
                                     if "NO_SUCH_FIELD" in r["detail"]])


class DuplicateKeys(Isolated):
    def duplicate(self, filename, key, actual, earlier, *, selectors=False):
        self.positive("G-93")
        path = self.pipeline / filename
        text = path.read_text(encoding="utf-8")
        needle = json.dumps(key) + ": " + json.dumps(actual)
        self.assertEqual(text.count(needle), 1, needle)
        duplicate = json.dumps(key) + ": " + json.dumps(earlier) + ", " + needle
        path.write_bytes(text.replace(needle, duplicate, 1).encode("utf-8"))
        targets = [("--dir", self.pipeline)]
        if selectors:
            targets.append(("--file", self.pipeline / "walls.json"))
        for target in targets:
            with self.subTest(selector=target[0]):
                result, report = self.validate(target=target)
                self.assertEqual(result.returncode, 1, self.failures(report))
                self.assertEqual(report["exit_code"], 1)
                self.assertTrue([r for r in self.rows(report, "G-7", "FAIL")
                                 if filename in r["location"] and "duplicate JSON object key" in r["detail"]],
                                self.failures(report))
                self.assertFalse([r for r in self.rows(report, "G-7", "PASS")
                                  if filename in r["location"]])
                self.assertFalse([r for r in self.rows(report, "G-10", "PASS")
                                  if "walls.json" in r["location"]])
                self.assertFalse([r for r in self.rows(report, "G-93", "PASS")
                                  if "walls.json" in r["location"]])
                if filename == "dimensions.json":
                    self.assertLess(len(self.failures(report)), 25, self.failures(report))
                    self.assertTrue([r for r in self.rows(report, "G-64", "SKIP")
                                     if "facade_grids.json" in r["location"]])
                    self.assertFalse([r for r in self.rows(report, "G-64", "PASS")
                                      if "facade_grids.json" in r["location"]])
                    self.assertTrue(self.rows(report, "G-92", "SKIP"))

    def test_dimensions_duplicate_root_project(self):
        self.duplicate("dimensions.json", "project", self.dimensions["project"], "different-project", selectors=True)

    def test_dimensions_duplicate_nested_geometry(self):
        self.duplicate("dimensions.json", "setback_cm", self.dimensions["site"]["setback_cm"], 999)

    def test_assumptions_duplicate_nested_conflict_ref(self):
        self.duplicate("assumptions.json", "conflict_ref", "C-003", "C-999")

    def test_transitive_massing_duplicate_root_status(self):
        self.walls["origin_inputs"] = ["sections[0].points_cm"]
        self.save_walls()
        self.duplicate("massing.json", "status", "locked", "superseded")


class NumericBoundary(unittest.TestCase):
    def test_decimal_tokens_must_round_trip_and_stay_in_safe_range(self):
        for token in ("0.1", "0.30000000000000004", "1e3", "1.000", "9007199254740991", "1e100"):
            with self.subTest(valid=token):
                self.assertIsNotNone(validator.strict_json_loads(token))
        for token in ("10000000000000001.9", "0.10000000000000001", "1e-9999",
                      "9007199254740992", "1e9999", "9" * 5000, "9" * 5000 + ".0"):
            with self.subTest(invalid=token):
                with self.assertRaises(ValueError):
                    validator.strict_json_loads(token)

    def test_rounding_gap_is_refused_before_the_spatial_oracle(self):
        docs = sample()
        origin = 10**16
        for point in docs[1]["elements"][0]["profile_cm"]:
            point[0] += origin
        for cell in docs[0]["wall_cells"]:
            cell["plan_rect_cm"][0] += origin
            cell["plan_rect_cm"][2] += origin
        for key in ("start_corner_cm", "end_corner_cm"):
            docs[2]["facades"][0][key][0] += origin
        self.assertEqual(coverage.check_wall_cell_coverage(*docs).status, "PASS")
        docs[0]["wall_cells"][0]["plan_rect_cm"][2] = "NUMERIC_TOKEN"
        raw = json.dumps(docs).replace('"NUMERIC_TOKEN"', "10000000000000001.9")
        legacy = json.loads(raw)
        self.assertEqual(legacy[0]["wall_cells"][0]["plan_rect_cm"][2], origin + 2)
        self.assertEqual(coverage.check_wall_cell_coverage(*legacy).status, "PASS")
        with self.assertRaisesRegex(ValueError, "safety range|precision"):
            validator.strict_json_loads(raw)

    def test_huge_in_memory_g82_refuses_without_internal_error(self):
        normal = sample()
        normal[0]["status"] = "locked"
        normal[0]["tolerances"] = {"linear_cm": 0.5}
        self.assertEqual([severity for severity, _ in g82(normal)], ["PASS"])
        docs = huge_sample()
        docs[0]["status"] = "locked"
        docs[0]["tolerances"] = {"linear_cm": 0.5}
        docs[0]["wall_cells"].pop(0)
        rows = g82(docs)
        self.assertEqual([severity for severity, _ in rows], ["FAIL"], rows)
        self.assertIn("safe range", rows[0][1])
        self.assertNotIn("internal error", rows[0][1])


class NumericCli(Isolated):
    def numeric_case(self, token):
        # The private copy is converted back to the unchanged legacy route.
        (self.pipeline / "walls.json").unlink()
        assembly = copy.deepcopy(self.original_assembly)
        write_json(self.pipeline / "assembly.json", assembly)
        result, control = self.validate()
        self.assertEqual(result.returncode, 0, self.failures(control))
        self.assertTrue(self.rows(control, "G-82", "PASS"))
        assembly["wall_cells"][0]["plan_rect_cm"][2] = "NUMERIC_TOKEN"
        text = json.dumps(assembly, indent=2, ensure_ascii=False).replace('"NUMERIC_TOKEN"', token) + "\n"
        (self.pipeline / "assembly.json").write_bytes(text.encode("utf-8"))
        result, report = self.validate()
        self.assertEqual(result.returncode, 1, self.failures(report))
        self.assertTrue([r for r in self.rows(report, "G-7", "FAIL")
                         if "assembly.json" in r["location"]], self.failures(report))
        self.assertTrue(self.rows(report, "G-82", "SKIP"))
        self.assertFalse(self.rows(report, "G-82", "PASS"))
        filtered_result, filtered = self.validate("--rule", "G-82")
        self.assertEqual(filtered_result.returncode, 1)
        self.assertEqual(filtered["exit_code"], 1)
        self.assertTrue(self.rows(filtered, "G-82", "SKIP"))
        self.assertFalse(self.rows(filtered, "G-82", "PASS"))

    def test_unrecoverable_decimal_gap_never_reaches_g82_as_pass(self):
        self.numeric_case("10000000000000001.9")

    def test_enormous_integer_is_rejected_without_internal_error(self):
        self.numeric_case("9" * 5000)

    def test_enormous_float_token_is_rejected_with_bounded_error(self):
        self.numeric_case("9" * 5000 + ".0")


class JsonDepth(Isolated):
    def test_deep_json_reports_g7_not_traceback(self):
        path = self.pipeline / "assumptions.json"
        original = path.read_text(encoding="utf-8")
        self.assertTrue(original.endswith("}\n"))
        for depth in (100, 4000):
            with self.subTest(depth=depth):
                addition = ",\n  \"_nesting_probe\": " + "[" * depth + "0" + "]" * depth + "\n}\n"
                path.write_bytes((original[:-2] + addition).encode("utf-8"))
                result, report = self.validate()
                rows = [r for r in self.rows(report, "G-7") if "assumptions.json" in r["location"]]
                if depth == 100:
                    self.assertEqual(result.returncode, 0, self.failures(report))
                    self.assertTrue([r for r in rows if r["severity"] == "PASS"], rows)
                else:
                    self.assertEqual(result.returncode, 1)
                    self.assertTrue([r for r in rows if r["severity"] == "FAIL" and
                                     "nesting exceeds" in r["detail"]], rows)
                    self.assertFalse([r for r in self.rows(report, "G-93", "PASS")
                                      if "walls.json" in r["location"]])

    def test_boundary_applies_to_every_used_upstream_and_ledger(self):
        # Every negative starts from separately calibrated, unchanged input.
        for name, source in (("dimensions", "structure.x_bay_cm"),
                             ("assumptions", "site.plot_rotation_deg"),
                             ("conflicts_resolved", "structure.x_bay_cm"),
                             ("massing", "storeys[0].elevation_cm"),
                             ("nurbs", "sections[0].points_cm"),
                             ("facade_grids", "panels[71].width_cm"),
                             ("components_registry", REGISTRY_PATH)):
            with self.subTest(spec=name):
                docs = make_control(source, acyclic_registry=name in ("facade_grids", "components_registry"))
                for spec, doc in docs.items():
                    write_json(self.pipeline / (spec + ".json"), doc)
                self.positive("G-93")
                path = self.pipeline / (name + ".json")
                original = path.read_text(encoding="utf-8")
                addition = ',"_nesting_probe":' + nested_json(
                    validator.MAX_JSON_CONTAINER_DEPTH, objects=True) + "}\n"
                path.write_bytes((original[:-2] + addition).encode("utf-8"))
                result, report = self.validate(target=("--file", self.pipeline / "walls.json"))
                self.assertEqual(result.returncode, 1)
                self.assertTrue([r for r in self.rows(report, "G-7", "FAIL")
                                 if name + ".json" in r["location"] and
                                 "nesting exceeds" in r["detail"]], self.failures(report))
                self.assertFalse([r for gate in ("G-7", "G-8")
                                  for r in self.rows(report, gate, "PASS")
                                  if name + ".json" == r["location"]])
                self.assertFalse([r for gate in ("G-10", "G-93")
                                  for r in self.rows(report, gate, "PASS")
                                  if "walls.json" in r["location"]])

    def test_maximum_accepted_depth_reaches_unit_and_leaf_walkers(self):
        self.positive("G-93")
        path = self.pipeline / "dimensions.json"
        doc = copy.deepcopy(self.dimensions)
        raw = nested_json(validator.MAX_JSON_CONTAINER_DEPTH - 1, objects=True)
        doc["raw_source_values"] = validator.strict_json_loads(raw)
        doc["origins"]["raw_source_values"] = {"origin": "given"}
        write_json(path, doc)
        result, report = self.validate()
        self.assertEqual(result.returncode, 0, self.failures(report))
        for gate in ("G-7", "G-8", "G-9", "G-10", "G-93"):
            self.assertTrue(self.rows(report, gate, "PASS"), (gate, report))
        loaded = validator.load_spec_file(path, path.name)
        self.assertTrue(loaded.ok, loaded.fatal)
        self.assertTrue([p for p in validator.collect_leaves(loaded.doc, loaded.spec)
                         if p.startswith("raw_source_values.")])


class StrictNesting(unittest.TestCase):
    def test_exact_limit_counts_arrays_objects_and_mixed_containers(self):
        limit = validator.MAX_JSON_CONTAINER_DEPTH
        for objects in (False, True):
            with self.subTest(objects=objects):
                parsed = validator.strict_json_loads(nested_json(limit, objects=objects))
                self.assertTrue(validator.deep_equal(parsed, copy.deepcopy(parsed)))
                different = validator.strict_json_loads(nested_json(limit, "1", objects=objects))
                self.assertFalse(validator.deep_equal(parsed, different))
                for depth in (limit + 1, 4000):
                    with self.assertRaisesRegex(ValueError, "JSON nesting exceeds"):
                        validator.strict_json_loads(nested_json(depth, objects=objects))
        mixed = '[{"probe":' * (limit // 2) + "0" + '}]' * (limit // 2)
        self.assertIsNotNone(validator.strict_json_loads(mixed))
        with self.assertRaisesRegex(ValueError, "JSON nesting exceeds"):
            validator.strict_json_loads("[" + mixed + "]")

    def test_quoted_brackets_escaped_quotes_and_backslashes_are_not_containers(self):
        text = json.dumps({"probe": '[{]}"\\' * 4000, "escaped": '\\"[[]]{}'})
        self.assertEqual(validator.strict_json_loads(text), json.loads(text))
        # A quote after an even number of backslashes ends the string, so the
        # genuinely deep array following it must still be rejected.
        prefix = '{"probe":' + json.dumps("\\\\") + ',"deep":'
        with self.assertRaisesRegex(ValueError, "JSON nesting exceeds"):
            validator.strict_json_loads(prefix + nested_json(validator.MAX_JSON_CONTAINER_DEPTH) + "}")

    def test_nested_duplicate_and_lossy_number_checks_are_not_bypassed(self):
        wrappers = validator.MAX_JSON_CONTAINER_DEPTH - 1
        self.assertIsNotNone(validator.strict_json_loads(nested_json(wrappers, '{"key":0.1}')))
        for leaf, message in (('{"key":0,"key":1}', "duplicate JSON object key"),
                              ('{"key":1e9999}', "overflows"),
                              ('{"key":0.10000000000000001}', "precision")):
            with self.subTest(leaf=leaf), self.assertRaisesRegex(ValueError, message):
                validator.strict_json_loads(nested_json(wrappers, leaf))

    def test_malformed_shallow_json_is_still_rejected_by_the_real_parser(self):
        for raw in ('[}', '{"key":"unterminated}', '{"key":[0,]}', '][0]'):
            with self.subTest(raw=raw), self.assertRaises(json.JSONDecodeError):
                validator.strict_json_loads(raw)

    def test_unexpected_decoder_error_is_not_relabelled_as_bad_input(self):
        with patch.object(validator.json, "loads", side_effect=RuntimeError("decoder sentinel")):
            with self.assertRaisesRegex(RuntimeError, "decoder sentinel"):
                validator.strict_json_loads("{}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
