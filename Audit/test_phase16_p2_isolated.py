#!/usr/bin/env python3
"""Offline, isolated regressions for the open Phase 16 P2 wall-input issues.

Run: python -B Audit/test_phase16_p2_isolated.py -v

These are *contract* tests, not expected-failure tests: they fail on an
unfixed validator and automatically pass when the behavior is corrected.
Every test calibrates its own clean synthetic control, then changes the exact
input under examination. All copied specs and CLI output live in a private
temporary directory; no Max, builder, installer or project file is touched.
An offline pass is not evidence of a generated or measured wall.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
VALIDATOR = ROOT / "scripts" / "validate_specs.py"
INIT = ROOT / "scripts" / "init_project.py"
POLY = "poly_surface_shell_v1"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, document: Any) -> None:
    path.write_bytes((json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False)
                      + "\n").encode("utf-8"))


def walls_declaration(dimensions: dict[str, Any]) -> dict[str, Any]:
    """A hypothetical, data-only fixture; no claim about the user's model.

    The test brief supplies the inner reference faces, directions, sizes and
    declared budget; none are inferred from compass names or live geometry.
    """
    budget = {"max_grid_polygons": 64, "max_base_active_polygons": 64,
              "max_evaluated_triangles": 512}

    def run(ident: str, facade: str, start: list[float], end: list[float],
            outward: list[float], base: float = 0.0, top: float = 420.0) -> dict:
        return {"id": ident, "block_id": "BLK-001",
                "contour_ref": f"dimensions.json:facades:{facade}",
                "start_cm": start, "end_cm": end, "outward": outward,
                "thickness_cm": 30.0, "base_z_cm": base, "top_z_cm": top,
                "topology_budget": dict(budget)}

    upper = run("RET-001", "F-W", [0.0, 0.0], [0.0, 900.0], [-1.0, 0.0],
                380.0, 420.0)
    upper["adjacent_run_ids"] = ["RUN-001", "RUN-002"]
    paths = ("wall_technique", "reference_face", "numeric_epsilon_cm",
             "numeric_unit_epsilon", "blocks[0]", "blocks[1]", "wall_runs[0]",
             "wall_runs[1]", "openings[0]", "openings[1]", "upper_returns[0]")
    return {
        "schema_version": "1.1", "spec": "walls", "project": dimensions["project"],
        "units": {"length": "cm", "angle": "deg"},
        "source": {"kind": "user_brief", "reference": "Synthetic offline brief: facade "
                   "segments F-S, F-N and F-W are wall inner faces; all values, directions "
                   "and budgets are test inputs.", "recorded_at": "2026-11-02T00:00:00Z"},
        "status": "locked", "tolerances": copy.deepcopy(dimensions["tolerances"]),
        "origin_inputs": ["facades[0]", "facades[1]", "facades[3]"],
        "origins": {path: {"origin": "given"} for path in paths},
        "wall_technique": POLY, "reference_face": "inner",
        "numeric_epsilon_cm": 0.001, "numeric_unit_epsilon": 0.000001,
        "blocks": [{"id": "BLK-001", "z_range_cm": [0.0, 420.0]},
                   {"id": "BLK-002", "z_range_cm": [420.0, 820.0]}],
        "wall_runs": [run("RUN-001", "F-S", [0.0, 0.0], [1800.0, 0.0], [0.0, -1.0]),
                      run("RUN-002", "F-N", [0.0, 900.0], [1800.0, 900.0], [0.0, 1.0])],
        "openings": [{"id": "OP-001", "wall_run_id": "RUN-001", "kind": "window",
                      "u_range_cm": [135.0, 315.0], "sill_cm": 90.0, "head_cm": 270.0},
                     {"id": "OP-002", "wall_run_id": "RUN-001", "kind": "door",
                      "u_range_cm": [575.0, 775.0], "sill_cm": 0.0, "head_cm": 260.0}],
        "upper_returns": [upper],
    }


def draft_assembly(example: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0", "spec": "assembly", "project": example["project"],
        "units": copy.deepcopy(example["units"]),
        "source": {"kind": "derived", "reference": "components_registry.json; synthetic "
                   "empty draft placeholder, not generated assembly output",
                   "recorded_at": "2026-11-02T00:00:00Z"},
        "status": "draft", "tolerances": copy.deepcopy(example["tolerances"]),
        "origin_inputs": [], "origins": {}, "defaults": {}, "layer_map": {},
        "placements": [], "opening_cuts": [], "wall_cells": [], "scatter": [],
    }


def synthetic_poly_assembly(example: dict[str, Any]) -> dict[str, Any]:
    document = copy.deepcopy(example)
    document["source"]["reference"] = ("components_registry.json and dimensions.json; "
                                      "synthetic test-only echo, not built or measured")
    for key in ("opening_cuts", "wall_cells"):
        document.pop(key)
        document["origins"] = {path: value for path, value in document["origins"].items()
                               if not path.startswith(key + "[") and path != key}
    document["wall_technique"] = POLY
    document["wall_ref"] = "wall_surface.json"
    return document


class Isolated(unittest.TestCase):
    def setUp(self) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        owner = tempfile.TemporaryDirectory(prefix="phase16-p2-isolated-", dir=parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.pipeline = self.temp / "project" / "pipeline"
        self.pipeline.parent.mkdir(parents=True)
        shutil.copytree(EXAMPLES, self.pipeline)
        (self.pipeline / "assembly.ms").unlink(missing_ok=True)
        self.dimensions = read_json(self.pipeline / "dimensions.json")
        self.original_assembly = read_json(self.pipeline / "assembly.json")
        self.walls = walls_declaration(self.dimensions)
        self.assembly = draft_assembly(self.original_assembly)
        self.save_walls()
        write_json(self.pipeline / "assembly.json", self.assembly)

    def save_walls(self) -> None:
        write_json(self.pipeline / "walls.json", self.walls)

    def command(self, script: Path, *args: object) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-B", str(script), *(str(arg) for arg in args)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        try:
            return subprocess.run(command, cwd=self.temp, env=env, text=True,
                                  encoding="utf-8", errors="replace", capture_output=True,
                                  timeout=120, check=False)
        except subprocess.TimeoutExpired as exc:
            self.fail(f"offline command timed out: {command!r}: {exc}")

    def validate(self, *args: object, target: tuple[object, object] | None = None
                 ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        selector = target or ("--dir", self.pipeline)
        process = self.command(VALIDATOR, *selector, "--json", *args)
        self.assertNotIn("Traceback", process.stderr, process.stderr)
        try:
            report = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"invalid validator JSON: {exc}; stdout={process.stdout[:2000]!r}; "
                      f"stderr={process.stderr!r}")
        self.assertIsInstance(report.get("findings"), list)
        internal = [row for row in report["findings"]
                    if "internal error" in str(row.get("detail", "")).lower()]
        self.assertFalse(internal, internal)
        return process, report

    @staticmethod
    def rows(report: dict, rule: str, severity: str | None = None) -> list[dict]:
        return [row for row in report["findings"] if row.get("rule") == rule
                and (severity is None or row.get("severity") == severity)]

    @staticmethod
    def failures(report: dict) -> list[dict]:
        return [row for row in report["findings"] if row.get("severity") == "FAIL"]

    def clean(self, *args: object, target: tuple[object, object] | None = None
              ) -> dict[str, Any]:
        result, report = self.validate(*args, target=target)
        self.assertEqual(result.returncode, 0, self.failures(report))
        self.assertEqual(report.get("exit_code"), 0, self.failures(report))
        self.assertFalse(self.failures(report))
        return report

    def positive(self, rule: str = "G-93", *, severity: str = "PASS") -> None:
        report = self.clean()
        self.assertTrue(self.rows(report, rule, severity), (rule, severity, self.rows(report, rule)))
        self.assertFalse(self.rows(report, rule, "FAIL"))

    def reject(self, rule: str, location: str, *, also: tuple[str, ...] = (),
               detail: str = "") -> dict:
        result, report = self.validate()
        bad = self.failures(report)
        self.assertFalse([row for row in bad if row.get("rule") not in (rule, *also)], bad)
        target = [row for row in self.rows(report, rule, "FAIL")
                  if location in str(row.get("location", "")) + " " + str(row.get("detail", ""))]
        if detail:
            target = [row for row in target if detail in str(row.get("detail", ""))]
        self.assertEqual(result.returncode, 1,
                         f"{rule} silently accepted {location}; target={self.rows(report, rule)}; "
                         f"all failures={bad}")
        self.assertEqual(report.get("exit_code"), 1, bad)
        self.assertTrue(target, f"missing {rule} FAIL at {location}: {bad}")
        return report

    def split_run_origins(self, index: int) -> None:
        """Split one valid element marker into exactly-one leaf markers."""
        base = f"wall_runs[{index}]"
        del self.walls["origins"][base]
        for key in self.walls["wall_runs"][index]:
            if key != "id":
                self.walls["origins"][f"{base}.{key}"] = {"origin": "given"}

    def assumption_control(self) -> None:
        self.split_run_origins(0)
        path = "wall_runs[0].thickness_cm"
        self.walls["origins"][path] = {"origin": "assumed", "origin_ref": "A-026"}
        ledger_path = self.pipeline / "assumptions.json"
        ledger = read_json(ledger_path)
        entry = copy.deepcopy(ledger["assumptions"][0])
        entry.update(id="A-026", field_path=f"walls.json:{path}", value=30.0,
                     reason="Synthetic fixture: assume this wall thickness.",
                     invalidated_by="A wall thickness from the test brief.")
        ledger["assumptions"].append(entry)
        write_json(ledger_path, ledger)
        self.save_walls()

    def conflict_control(self) -> None:
        self.split_run_origins(0)
        path = "wall_runs[0].thickness_cm"
        self.walls["origins"][path] = {"origin": "conflict", "origin_ref": "C-006"}
        ledger_path = self.pipeline / "conflicts_resolved.json"
        ledger = read_json(ledger_path)
        entry = copy.deepcopy(ledger["conflicts"][0])
        entry["id"] = "C-006"
        entry["resolution"]["resulting_value_of"] = f"walls.json:{path}"
        entry["resolution"]["resolved_paths"] = [f"walls.json:{path}"]
        entry["resolution"]["chosen_value"] = 30.0
        ledger["conflicts"].append(entry)
        write_json(ledger_path, ledger)
        self.save_walls()

    def derived_control(self) -> None:
        # Identical declared thicknesses; the second is given, so this is an
        # acyclic, value-consistent dependency rather than an arbitrary formula.
        self.split_run_origins(0)
        self.split_run_origins(1)
        a = "wall_runs[0].thickness_cm"
        b = "wall_runs[1].thickness_cm"
        self.assertEqual(self.walls["wall_runs"][0]["thickness_cm"],
                         self.walls["wall_runs"][1]["thickness_cm"])
        self.walls["origins"][a] = {"origin": "derived", "derives_from": [b]}
        self.save_walls()

    def produced_echo(self) -> None:
        # Static synthetic echo, deliberately not an S5 build or manifest.
        self.assembly = synthetic_poly_assembly(self.original_assembly)
        write_json(self.pipeline / "assembly.json", self.assembly)


class Provenance(Isolated):
    def test_assumption_id_must_match_owner_and_path(self) -> None:
        self.assumption_control()
        report = self.clean()
        self.assertTrue(self.rows(report, "G-13", "PASS"))
        self.assertTrue(self.rows(report, "G-93", "PASS"))
        # A-001 is a real, separately consumed dimensions.json assumption;
        # only the reference changes, not the valid wall-owned A-026 entry.
        self.walls["origins"]["wall_runs[0].thickness_cm"]["origin_ref"] = "A-001"
        self.save_walls()
        self.reject("G-13", "walls.json::wall_runs[0].thickness_cm", also=("G-93", "G-10"))

    def test_assumption_ledger_value_must_equal_wall_value(self) -> None:
        self.assumption_control()
        self.positive("G-13")
        path = self.pipeline / "assumptions.json"
        ledger = read_json(path)
        entry = next(item for item in ledger["assumptions"] if item["id"] == "A-026")
        entry["value"] = 31.0  # same id/owner/path, only the value differs
        write_json(path, ledger)
        self.reject("G-12", "walls.json:wall_runs[0].thickness_cm",
                    also=("G-93", "G-10", "G-13"))

    def test_unrelated_assumption_without_wall_claim_cannot_pass(self) -> None:
        # No second ledger entry: independently tests a wall for which *only*
        # an unrelated yet real A-001 is named, not a mismatched pair of IDs.
        self.split_run_origins(0)
        self.save_walls()
        self.positive("G-13")
        self.walls["origins"]["wall_runs[0].thickness_cm"] = {
            "origin": "assumed", "origin_ref": "A-001"}
        self.save_walls()
        self.reject("G-13", "walls.json::wall_runs[0].thickness_cm", also=("G-93", "G-10"))

    def test_unrelated_conflict_id_cannot_prove_wall_origin(self) -> None:
        self.split_run_origins(0)
        self.save_walls()
        self.positive()
        # Both fields carry an existing, unrelated dimension-owned conflict.
        # conflict_ref is set as well because the existing G-13 reads that field.
        self.walls["origins"]["wall_runs[0].thickness_cm"] = {
            "origin": "conflict", "origin_ref": "C-001", "conflict_ref": "C-001"}
        self.save_walls()
        self.reject("G-13", "walls.json::wall_runs[0].thickness_cm", also=("G-93", "G-10"))

    def test_conflict_id_must_match_owner_and_path(self) -> None:
        self.conflict_control()
        report = self.clean()
        self.assertTrue(self.rows(report, "G-13", "PASS"))
        self.assertTrue(self.rows(report, "G-93", "PASS"))
        self.walls["origins"]["wall_runs[0].thickness_cm"]["origin_ref"] = "C-001"
        self.save_walls()
        self.reject("G-10", "wall_runs[0].thickness_cm", also=("G-93", "G-13"))

    def test_conflict_chosen_value_must_match_wall_value(self) -> None:
        self.conflict_control()
        self.positive("G-13")
        path = self.pipeline / "conflicts_resolved.json"
        ledger = read_json(path)
        entry = next(item for item in ledger["conflicts"] if item["id"] == "C-006")
        entry["resolution"]["chosen_value"] = 31.0
        write_json(path, ledger)
        self.reject("G-12", "walls.json:wall_runs[0].thickness_cm",
                    also=("G-10", "G-13", "G-14", "G-93"))

    def test_self_dependency_rejected_by_g10(self) -> None:
        self.derived_control()
        self.positive("G-10")
        self.walls["origins"]["wall_runs[0].thickness_cm"]["derives_from"] = [
            "wall_runs[0].thickness_cm"]
        self.save_walls()
        self.reject("G-10", "wall_runs[0].thickness_cm", also=("G-93",))

    def test_two_node_cycle_rejected_by_g10(self) -> None:
        self.derived_control()
        self.positive("G-10")
        self.walls["origins"]["wall_runs[1].thickness_cm"] = {
            "origin": "derived", "derives_from": ["wall_runs[0].thickness_cm"]}
        self.save_walls()
        self.reject("G-10", "wall_runs[1].thickness_cm", also=("G-93",))

    def test_element_marker_cycle_detected(self) -> None:
        # Whole-object markers are allowed and each source resolves exactly;
        # the control is a one-way dependency to a given second element.
        self.walls["origins"]["wall_runs[0]"] = {
            "origin": "derived", "derives_from": ["wall_runs[1]"]}
        self.save_walls()
        self.positive("G-10")
        self.walls["origins"]["wall_runs[1]"] = {
            "origin": "derived", "derives_from": ["wall_runs[0]"]}
        self.save_walls()
        self.reject("G-10", "wall_runs[1]", also=("G-93",))

    def test_element_self_dependency_through_descendant_is_a_cycle(self) -> None:
        # Exact path comparison is insufficient: the descendant is covered by
        # the very same element origin. The neighbouring given element is the
        # acyclic control, also using an existing descendant path.
        self.walls["origins"]["wall_runs[0]"] = {
            "origin": "derived", "derives_from": ["wall_runs[1].thickness_cm"]}
        self.save_walls()
        self.positive("G-10")
        self.walls["origins"]["wall_runs[0]"]["derives_from"] = [
            "wall_runs[0].thickness_cm"]
        self.save_walls()
        self.reject("G-10", "wall_runs[0]", also=("G-93",))

    def test_derived_can_use_a_real_upstream_value(self) -> None:
        # Separate positive control for upstream (not another local origin).
        self.split_run_origins(0)
        path = "wall_runs[0].base_z_cm"
        self.walls["origins"][path] = {
            "origin": "derived", "derives_from": ["levels[0].elevation_cm"]}
        self.save_walls()
        # Establish which upstream fields actually exist; no target spelling is
        # inferred from the validator's internal code.
        self.assertEqual(self.dimensions["levels"][0]["elevation_cm"],
                         self.walls["wall_runs"][0]["base_z_cm"])
        self.positive("G-10")

    def test_origin_inputs_must_not_resolve_only_in_walls(self) -> None:
        self.walls["origin_inputs"] = ["facades[0].id"]
        self.save_walls()
        self.positive()
        self.walls["origin_inputs"] = ["wall_runs[0].thickness_cm"]
        self.save_walls()
        self.reject("G-93", "walls.json::origin_inputs", also=("G-31",))

    def test_origin_inputs_cannot_be_sourced_from_downstream_assembly(self) -> None:
        self.produced_echo()
        self.walls["origin_inputs"] = ["facades[0].id"]
        self.save_walls()
        self.positive()
        self.assertTrue(self.assembly["placements"])
        # This path exists in the downstream synthetic assembly, but not in a
        # declaration input. It is different from the self-file-only case.
        self.walls["origin_inputs"] = ["placements[0].id"]
        self.save_walls()
        self.reject("G-93", "walls.json::origin_inputs", also=("G-31",))


class ScopeAndGeometry(Isolated):
    def test_g97_does_not_pass_when_one_run_is_not_an_object(self) -> None:
        self.walls["status"] = "draft"
        self.save_walls()
        report = self.clean()
        self.assertTrue(self.rows(report, "G-97", "PASS"))
        self.walls["wall_runs"].append(None)
        self.save_walls()
        result, report = self.validate()
        self.assertEqual(result.returncode, 1, self.failures(report))
        self.assertTrue([r for r in self.rows(report, "G-93", "FAIL")
                         if "walls.json::wall_runs[2]" in r["location"]], self.failures(report))
        self.assertFalse([r for r in self.failures(report) if r["rule"] != "G-93"],
                         self.failures(report))
        self.assertFalse(self.rows(report, "G-97", "PASS"), self.rows(report, "G-97"))
        self.assertTrue(self.rows(report, "G-97", "SKIP") or self.rows(report, "G-97", "FAIL"),
                        self.rows(report, "G-97"))

    def test_g97_does_not_pass_when_returns_are_not_an_array(self) -> None:
        self.walls["status"] = "draft"
        self.save_walls()
        report = self.clean()
        self.assertTrue(self.rows(report, "G-97", "PASS"))
        self.walls["upper_returns"] = None
        # Do not let the removed element's origin cause an unrelated failure.
        self.walls["origins"].pop("upper_returns[0]")
        self.save_walls()
        result, report = self.validate()
        self.assertEqual(result.returncode, 1, self.failures(report))
        self.assertTrue([r for r in self.rows(report, "G-93", "FAIL")
                         if "walls.json::upper_returns" in r["location"]], self.failures(report))
        self.assertFalse([r for r in self.failures(report) if r["rule"] != "G-93"],
                         self.failures(report))
        self.assertFalse(self.rows(report, "G-97", "PASS"), self.rows(report, "G-97"))
        self.assertTrue(self.rows(report, "G-97", "SKIP") or self.rows(report, "G-97", "FAIL"),
                        self.rows(report, "G-97"))

    def test_envelope_failure_cannot_coexist_with_g93_pass(self) -> None:
        self.positive()
        original = copy.deepcopy(self.walls)
        cases = (("G-2", "spec", "not-walls"),
                 ("G-5", "units", {"length": "mm", "angle": "deg"}),
                 ("G-6", "source", {"kind": "user_brief", "reference": "",
                                      "recorded_at": "2026-11-02T00:00:00Z"}))
        for gate, key, bad in cases:
            with self.subTest(gate=gate):
                self.walls = copy.deepcopy(original)
                self.walls[key] = bad
                self.save_walls()
                _, report = self.validate()
                self.assertTrue([r for r in self.rows(report, gate, "FAIL")
                                 if r["location"] == "walls.json"], self.failures(report))
                self.assertFalse([r for r in self.failures(report) if r["rule"] != gate],
                                 self.failures(report))
                self.assertFalse(self.rows(report, "G-93", "PASS"), self.rows(report, "G-93"))
                self.assertTrue(self.rows(report, "G-93", "SKIP") or
                                self.rows(report, "G-93", "FAIL"), self.rows(report, "G-93"))

    def test_zero_outward_with_available_epsilon(self) -> None:
        self.positive()
        self.walls["wall_runs"][0]["outward"] = [0.0, 0.0]
        self.save_walls()
        self.reject("G-93", "walls.json::wall_runs[0].outward")

    def test_parallel_outward_with_available_epsilon(self) -> None:
        self.positive()
        self.walls["wall_runs"][0]["outward"] = [1.0, 0.0]
        self.save_walls()
        self.reject("G-93", "walls.json::wall_runs[0].outward")

    def test_opposite_unit_normal_is_only_a_syntactic_control(self) -> None:
        # The declaration has no independently machine-checkable outside/inside
        # oracle. Both signs meet the documented static unit/perpendicular
        # predicate; neither G-93 PASS establishes real outward direction.
        self.positive()
        self.walls["wall_runs"][0]["outward"] = [0.0, 1.0]
        self.save_walls()
        self.positive()

    def test_draft_zero_outward_with_unavailable_epsilon(self) -> None:
        self.walls["status"] = "draft"
        self.walls["numeric_unit_epsilon"] = None
        self.save_walls()
        self.positive("G-93", severity="SKIP")
        self.walls["wall_runs"][0]["outward"] = [0.0, 0.0]
        self.save_walls()
        self.reject("G-93", "walls.json::wall_runs[0].outward")

    def test_outward_cannot_hide_behind_excessive_unit_epsilon(self) -> None:
        self.positive()
        self.walls["numeric_unit_epsilon"] = 1.0
        self.walls["wall_runs"][0]["outward"] = [0.0, 0.0]
        self.save_walls()
        report = self.reject("G-93", "walls.json::numeric_unit_epsilon")
        # Once epsilon is invalid, an explicit zero remains invalid on its own;
        # merely rejecting the epsilon must not turn this into a valid vector.
        self.assertTrue([row for row in self.rows(report, "G-93", "FAIL")
                         if "walls.json::wall_runs[0].outward" in row["location"]],
                        self.rows(report, "G-93"))

    def test_dimensionless_epsilon_bound_without_vector_mutation(self) -> None:
        self.positive()
        self.walls["numeric_unit_epsilon"] = 1.0
        self.save_walls()
        self.reject("G-93", "walls.json::numeric_unit_epsilon")

    def test_linear_epsilon_must_be_numerical_not_a_building_scale(self) -> None:
        # The precise upper bound still needs a contract decision; this input is
        # 10^100 cm, not any plausible numerical or construction tolerance.
        self.positive()
        self.walls["numeric_epsilon_cm"] = 1e100
        self.save_walls()
        self.reject("G-93", "walls.json::numeric_epsilon_cm")

    def test_json_finite_float_overflow_is_not_an_accepted_wall_number(self) -> None:
        self.positive()
        path = self.pipeline / "walls.json"
        text = path.read_text(encoding="utf-8")
        before = '"numeric_epsilon_cm": 0.001'
        self.assertEqual(text.count(before), 1)
        # 1e999 is syntactically valid JSON, unlike NaN / Infinity literals.
        path.write_bytes(text.replace(before, '"numeric_epsilon_cm": 1e999').encode("utf-8"))
        result, report = self.validate()
        bad = self.failures(report)
        self.assertEqual(result.returncode, 1, bad)
        matched = [r for r in bad if r["rule"] in ("G-7", "G-93") and
                   "walls.json" in r["location"] and
                   (r["rule"] == "G-7" or "numeric_epsilon_cm" in r["location"])]
        self.assertTrue(matched, bad)
        self.assertFalse(self.rows(report, "G-93", "PASS"), self.rows(report, "G-93"))

    def test_json_overflow_cannot_hide_in_unreferenced_ledger_value(self) -> None:
        # The unit annotation is a legitimate JSON number, not a bare Infinity
        # token. It is not a wall field: rejecting only _wall_number is not a
        # strict loader. 0.0 is the calibrated finite control.
        ledger_path = self.pipeline / "assumptions.json"
        ledger = read_json(ledger_path)
        ledger["assumptions"][0]["alternatives_considered"][0]["value"] = 0.0
        write_json(ledger_path, ledger)
        self.positive()
        text = ledger_path.read_text(encoding="utf-8")
        needle = '"alternatives_considered": [\n        {\n          "value": 0.0'
        self.assertEqual(text.count(needle), 1)
        ledger_path.write_bytes(text.replace(needle, needle[:-3] + "1e999").encode("utf-8"))
        result, report = self.validate()
        self.assertEqual(result.returncode, 1, self.failures(report))
        self.assertTrue([r for r in self.rows(report, "G-7", "FAIL")
                         if "assumptions.json" in r["location"]], self.failures(report))

    def test_off_contour_reaches_g93_without_normal_error(self) -> None:
        self.positive()
        # Shift the entire run, leaving its tangent and unit normal unchanged.
        self.walls["wall_runs"][0]["start_cm"][1] = 0.501
        self.walls["wall_runs"][0]["end_cm"][1] = 0.501
        self.save_walls()
        self.reject("G-93", "walls.json::wall_runs[0].contour_ref")

    def test_opening_outside_run_reaches_g94_without_g93_failure(self) -> None:
        self.positive("G-94")
        self.walls["openings"][1]["u_range_cm"] = [575.0, 1801.0]
        self.save_walls()
        self.reject("G-94", "walls.json::openings[1].u_range_cm")


class RoutingAndCli(Isolated):
    def test_parent_pipeline_duplicate_visible_to_dir_and_file(self) -> None:
        self.produced_echo()
        for selector in (("--dir", self.pipeline.parent),
                         ("--file", self.pipeline / "walls.json")):
            with self.subTest(control=selector[0]):
                report = self.clean(target=selector)
                self.assertTrue(self.rows(report, "G-92", "PASS"), self.rows(report, "G-92"))
        write_json(self.pipeline.parent / "walls.json", self.walls)
        for selector in (("--dir", self.pipeline.parent),
                         ("--file", self.pipeline / "walls.json")):
            with self.subTest(duplicate=selector[0]):
                result, report = self.validate(target=selector)
                self.assertEqual(result.returncode, 1, self.failures(report))
                self.assertTrue(self.rows(report, "G-92", "FAIL"), self.rows(report, "G-92"))
                # G-1 can also fail because an unknown route cannot interpret
                # the produced assembly's route-specific top-level schema.
                self.assertFalse([r for r in self.failures(report)
                                  if r["rule"] not in ("G-92", "G-1")],
                                 self.failures(report))
                self.assertFalse(self.rows(report, "G-92", "PASS"), self.rows(report, "G-92"))

    def test_directory_named_walls_cannot_fall_back_to_legacy(self) -> None:
        (self.pipeline / "walls.json").unlink()
        write_json(self.pipeline / "assembly.json", self.original_assembly)
        report = self.clean()
        self.assertTrue(self.rows(report, "G-92", "PASS"), self.rows(report, "G-92"))
        (self.pipeline / "walls.json").mkdir()
        self.reject("G-92", "walls.json / assembly.json", also=("G-7", "G-1"))

    def test_dangling_walls_symlink_cannot_fall_back_to_legacy(self) -> None:
        (self.pipeline / "walls.json").unlink()
        write_json(self.pipeline / "assembly.json", self.original_assembly)
        report = self.clean()
        self.assertTrue(self.rows(report, "G-92", "PASS"), self.rows(report, "G-92"))
        try:
            (self.pipeline / "walls.json").symlink_to(self.temp / "nonexistent-target.json")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable on this host: {exc}")
        self.assertTrue((self.pipeline / "walls.json").is_symlink())
        self.reject("G-92", "walls.json / assembly.json", also=("G-7", "G-1"))

    def test_json_filtered_rule_exit_matches_unfiltered_process(self) -> None:
        self.produced_echo()
        control = self.clean()
        self.assertTrue(self.rows(control, "G-93", "PASS"), self.rows(control, "G-93"))
        self.assertTrue(self.rows(control, "G-92", "PASS"), self.rows(control, "G-92"))
        report = self.clean("--rule", "G-92")
        self.assertTrue(self.rows(report, "G-92", "PASS"))
        self.assertTrue(all(row.get("rule") == "G-92" for row in report["findings"]))
        self.walls["wall_runs"][0]["outward"] = [0.0, 0.0]
        self.save_walls()
        full = self.reject("G-93", "walls.json::wall_runs[0].outward")
        self.assertTrue(self.rows(full, "G-92", "SKIP"), self.rows(full, "G-92"))
        self.assertFalse(self.rows(full, "G-92", "PASS"), self.rows(full, "G-92"))
        result, filtered = self.validate("--rule", "G-92")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(filtered.get("rule_filter"), "G-92")
        self.assertTrue(all(row.get("rule") == "G-92" for row in filtered["findings"]))
        self.assertTrue(self.rows(filtered, "G-92", "SKIP"), self.rows(filtered, "G-92"))
        self.assertFalse(self.rows(filtered, "G-92", "PASS"), self.rows(filtered, "G-92"))
        self.assertEqual(self.rows(filtered, "G-92"), self.rows(full, "G-92"))
        self.assertFalse(self.failures(filtered), self.failures(filtered))
        self.assertEqual(filtered.get("exit_code"), result.returncode,
                         "JSON exit_code must match process exit even if the failure is filtered")

    def test_seed_duplicate_route_key_rejected_before_writing(self) -> None:
        self.produced_echo()
        self.positive()
        control = self.command(INIT, "--project", "seed-control", "--dir", self.temp,
                               "--from", self.pipeline)
        self.assertEqual(control.returncode, 0, control.stdout + control.stderr)
        seeded = read_json(self.temp / "seed-control" / "specs" / "pipeline" / "walls.json")
        self.assertEqual(seeded["wall_technique"], POLY)
        path = self.pipeline / "walls.json"
        text = path.read_text(encoding="utf-8")
        needle = f'"wall_technique": "{POLY}"'
        self.assertEqual(text.count(needle), 1)
        text = text.replace(needle, '"wall_technique": "legacy_cells_v1",\n  ' + needle)
        path.write_bytes(text.encode("utf-8"))
        result = self.command(INIT, "--project", "seed-duplicate", "--dir", self.temp,
                              "--from", self.pipeline)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("duplicate", (result.stdout + result.stderr).lower())
        self.assertFalse((self.temp / "seed-duplicate").exists(), "rejected seed wrote output")

    def test_seed_float_overflow_rejected_before_writing(self) -> None:
        self.produced_echo()
        self.positive()
        control = self.command(INIT, "--project", "seed-finite", "--dir", self.temp,
                               "--from", self.pipeline)
        self.assertEqual(control.returncode, 0, control.stdout + control.stderr)
        path = self.pipeline / "walls.json"
        text = path.read_text(encoding="utf-8")
        before = '"numeric_epsilon_cm": 0.001'
        self.assertEqual(text.count(before), 1)
        path.write_bytes(text.replace(before, '"numeric_epsilon_cm": 1e999').encode("utf-8"))
        result = self.command(INIT, "--project", "seed-overflow", "--dir", self.temp,
                              "--from", self.pipeline)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("non-finite", (result.stdout + result.stderr).lower())
        self.assertFalse((self.temp / "seed-overflow").exists(), "rejected seed wrote output")

    def test_duplicate_route_key_in_validator_reports_g7(self) -> None:
        self.produced_echo()
        report = self.clean()
        self.assertTrue(self.rows(report, "G-92", "PASS"))
        path = self.pipeline / "walls.json"
        text = path.read_text(encoding="utf-8")
        needle = f'"wall_technique": "{POLY}"'
        self.assertEqual(text.count(needle), 1)
        path.write_bytes(text.replace(needle, '"wall_technique": "legacy_cells_v1",\n  ' + needle)
                         .encode("utf-8"))
        self.reject("G-7", "walls.json", also=("G-92", "G-1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
