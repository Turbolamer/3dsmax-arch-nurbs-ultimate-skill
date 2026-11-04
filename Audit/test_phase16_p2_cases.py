#!/usr/bin/env python3
"""Independent offline fault injection for the Phase 16 P2 *contract*.

    python -B Audit/test_phase16_p2_cases.py -v
    python -B Audit/test_phase16_p2_cases.py ConfigControls -v
    python -B Audit/test_phase16_p2_cases.py RuntimeBoundary -v

Only the standard library is required. Every invocation copies examples into
temporary directories and writes only there. The wall input is synthetic, not
an invented model of the user's pavilion. No Max, installer, future wall
builder, or emitted script is run. A PASS here is solely an offline result.

This test is intentionally NOT gated on P2 availability and does not import
the validator's private implementation. It may fail while P2 is in progress.
The baseline has a locked walls declaration and a genuinely unproduced draft
assembly; tests of an assembly echo use a separate synthetic, in-memory fixture,
never a manufactured wall_surface.json or a claim that S5 produced one.
"""

from __future__ import annotations

import copy
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
VALIDATOR = ROOT / "scripts" / "validate_specs.py"
ASSEMBLER = ROOT / "scripts" / "place_components.py"
POLY = "poly_surface_shell_v1"
LEGACY = "legacy_cells_v1"
RUNTIME_GATES = ("G-95", "G-98", "G-99", "G-100")
LEGACY_GATES = ("G-76", "G-77", "G-81", "G-82", "G-83")
CONFIG_GATES = ("G-93", "G-94", "G-97")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, doc: Any, *, allow_nan: bool = False) -> None:
    # NaN/Infinity are permitted here only for the deliberate G-7 injections.
    text = json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=allow_nan) + "\n"
    path.write_bytes(text.encode("utf-8"))


def walls_declaration(dimensions: dict[str, Any]) -> dict[str, Any]:
    """Data-only declaration from a *hypothetical test brief* + known facades.

    The declared epsilon and ceilings are test inputs, not experiment-derived
    defaults or measurements. The source independently declares the reference
    face; no inference is made from a compass name, direction_deg, or winding.
    Object-level origins are permitted by the established G-9 coverage style;
    scalar arrays such as start_cm take one entry, not one per coordinate.
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
    origins = {
        "wall_technique": {"origin": "given"},
        "reference_face": {"origin": "given"},
        "numeric_epsilon_cm": {"origin": "given"},
        "numeric_unit_epsilon": {"origin": "given"},
        "blocks[0]": {"origin": "given"},
        "blocks[1]": {"origin": "given"},
        "wall_runs[0]": {"origin": "given"},
        "wall_runs[1]": {"origin": "given"},
        "openings[0]": {"origin": "given"},
        "openings[1]": {"origin": "given"},
        "upper_returns[0]": {"origin": "given"},
    }
    return {
        "schema_version": "1.1",
        "spec": "walls",
        "project": dimensions["project"],
        "units": {"length": "cm", "angle": "deg"},
        "source": {"kind": "user_brief",
                   "reference": "Synthetic offline test brief: facade segments F-S, F-N and "
                                "F-W denote the wall inner reference faces. All wall sizes, "
                                "openings, direction vectors, budgets and epsilons are test inputs.",
                   "recorded_at": "2026-11-02T00:00:00Z"},
        "status": "locked",
        "tolerances": copy.deepcopy(dimensions["tolerances"]),
        "origin_inputs": ["facades[0]", "facades[1]", "facades[3]"],
        "origins": origins,
        "wall_technique": POLY,
        "reference_face": "inner",
        "numeric_epsilon_cm": 0.001,
        "numeric_unit_epsilon": 0.000001,
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
    """A scaffold-like placeholder, not a purported generated poly assembly."""
    return {
        "schema_version": "1.0", "spec": "assembly", "project": example["project"],
        "units": copy.deepcopy(example["units"]),
        "source": {"kind": "derived", "reference": "components_registry.json; "
                   "synthetic empty draft placeholder, not generated assembly output",
                   "recorded_at": "2026-11-02T00:00:00Z"},
        "status": "draft", "tolerances": copy.deepcopy(example["tolerances"]),
        "origin_inputs": [], "origins": {}, "defaults": {}, "layer_map": {},
        "placements": [], "opening_cuts": [], "wall_cells": [], "scatter": [],
    }


def synthetic_poly_assembly(example: dict[str, Any]) -> dict[str, Any]:
    """Configuration-only mock of an assembly echo, not a builder result."""
    doc = copy.deepcopy(example)
    doc["source"]["reference"] = ("components_registry.json and dimensions.json; synthetic "
                                  "test-only assembly echo, not built or measured")
    for key in ("opening_cuts", "wall_cells"):
        doc.pop(key)
        doc["origins"] = {path: value for path, value in doc["origins"].items()
                          if not path.startswith(key + "[") and path != key}
    doc["wall_technique"] = POLY
    doc["wall_ref"] = "wall_surface.json"
    return doc


class OfflineCase(unittest.TestCase):
    def setUp(self) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        temp_parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        owner = tempfile.TemporaryDirectory(prefix="phase16-p2-cases-", dir=temp_parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.pipeline = self.temp / "project" / "specs" / "pipeline"
        self.pipeline.parent.mkdir(parents=True)
        shutil.copytree(EXAMPLES, self.pipeline)
        # Prevent an old legacy assembly script from looking like poly output.
        (self.pipeline / "assembly.ms").unlink(missing_ok=True)
        self.dims = read_json(self.pipeline / "dimensions.json")
        self.original_assembly = read_json(self.pipeline / "assembly.json")
        self.walls = walls_declaration(self.dims)
        self.assembly = draft_assembly(self.original_assembly)
        self.persist()

    def persist(self) -> None:
        write_json(self.pipeline / "dimensions.json", self.dims)
        write_json(self.pipeline / "walls.json", self.walls)
        write_json(self.pipeline / "assembly.json", self.assembly)

    def mock_poly_assembly(self) -> None:
        self.assembly = synthetic_poly_assembly(self.original_assembly)
        write_json(self.pipeline / "assembly.json", self.assembly)

    def calibrate_mock_echo(self) -> None:
        # This is a static, synthetic configuration control, not an S5 output.
        with self.subTest(stage="unmutated synthetic assembly control"):
            result, report = self.validate()
            self.assertEqual(result.returncode, 0, self.findings(
                report, tuple(f"G-{i}" for i in range(1, 101)), "FAIL")[:12])
            self.assertTrue(self.findings(report, ("G-92",), "PASS"))
            self.assertFalse(self.findings(report, ("G-96",), "FAIL"))

    def run_script(self, script: Path, *args: object) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, "-B", str(script), *(str(a) for a in args)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        try:
            return subprocess.run(cmd, cwd=self.temp, env=env, text=True, encoding="utf-8",
                                  errors="replace", capture_output=True, timeout=120, check=False)
        except subprocess.TimeoutExpired as exc:
            self.fail(f"offline CLI timed out: {cmd!r}: {exc}")

    def validate(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = self.run_script(VALIDATOR, "--dir", self.pipeline, "--json", *args)
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"validator did not emit JSON: {exc}\n{result.stderr}\n{result.stdout[:2000]}")
        self.assertIsInstance(report.get("findings"), list)
        self.assertEqual(result.returncode, report.get("exit_code"), report.get("summary"))
        internal = [f for f in report["findings"]
                    if "internal error" in str(f.get("detail", "")).lower()]
        self.assertFalse(internal, f"validator crashed inside a guarded check: {internal}")
        return result, report

    @staticmethod
    def findings(report: dict, rules: tuple[str, ...], severity: str | None = None) -> list[dict]:
        return [f for f in report["findings"] if f.get("rule") in rules
                and (severity is None or f.get("severity") == severity)]

    def must_fail(self, rules: tuple[str, ...], location: str = "") -> None:
        result, report = self.validate()
        failures = self.findings(report, rules, "FAIL")
        if location:
            failures = [f for f in failures if location in (str(f.get("location", "")) +
                                                            str(f.get("detail", "")))]
        self.assertEqual(result.returncode, 1, f"mutation silently accepted: {report['summary']}")
        self.assertTrue(failures, f"expected {rules} FAIL at {location!r}; got "
                        f"{self.findings(report, rules)}; other failures: "
                        f"{self.findings(report, tuple(f'G-{i}' for i in range(1, 101)), 'FAIL')[:10]}")

    def config_clean(self) -> dict:
        result, report = self.validate()
        self.assertEqual(result.returncode, 0, f"locked declaration must lint; {report['summary']}; "
                         f"FAIL={self.findings(report, tuple(f'G-{i}' for i in range(1, 101)), 'FAIL')[:12]}")
        for rule in CONFIG_GATES:
            self.assertTrue(self.findings(report, (rule,), "PASS"), (rule, self.findings(report, (rule,))))
            self.assertFalse(self.findings(report, (rule,), "FAIL"), rule)
        return report


class ConfigControls(OfflineCase):
    def test_locked_declaration_lints_without_assembly_output(self) -> None:
        report = self.config_clean()
        self.assertEqual(read_json(self.pipeline / "walls.json")["status"], "locked")
        self.assertEqual(read_json(self.pipeline / "assembly.json")["status"], "draft")
        self.assertFalse((self.pipeline / "wall_surface.json").exists())
        self.assertFalse((self.pipeline / "wall_surface.ms").exists())
        # Incomplete echo is not required to PASS to authorize checking inputs.
        self.assertFalse(self.findings(report, ("G-92",), "FAIL"))

        # Independent arithmetic over the declaration only; not a mesh, volume
        # measurement, or assertion about any later built/live geometry.
        run = self.walls["wall_runs"][0]
        length = math.dist(run["start_cm"], run["end_cm"])
        height = run["top_z_cm"] - run["base_z_cm"]
        holes = sum((o["u_range_cm"][1] - o["u_range_cm"][0]) *
                    (o["head_cm"] - o["sill_cm"]) for o in self.walls["openings"]
                    if o["wall_run_id"] == run["id"])
        area = length * height - holes
        self.assertEqual((length, height, holes, area, area * run["thickness_cm"]),
                         (1800.0, 420.0, 84400.0, 671600.0, 20148000.0))
        self.assertEqual((len(self.walls["blocks"]), len(self.walls["wall_runs"]),
                          len(self.walls["openings"]), len(self.walls["upper_returns"])),
                         (2, 2, 2, 1))

    def test_config_positive_controls(self) -> None:
        # Fresh fixture per subtest, with one deliberate change each.
        scenarios: tuple[tuple[str, Callable[[dict], None]], ...] = (
            ("subsegment", lambda w: w["wall_runs"][0].__setitem__("start_cm", [100.0, 0.0])),
            ("touching_opening_edges", lambda w: w["openings"][1].__setitem__("u_range_cm", [315.0, 450.0])),
            ("two_openings_in_one_bay", lambda w: w["openings"][1].__setitem__("u_range_cm", [320.0, 440.0])),
            ("within_unit_epsilon", lambda w: w["wall_runs"][0].__setitem__("outward", [0.0000005, -1.0])),
            ("noncontiguous_unreferenced_ids", lambda w: w["blocks"][1].__setitem__("id", "BLK-019")),
            ("zero_topology_ceiling_is_a_declaration_not_measurement",
             lambda w: w["wall_runs"][0]["topology_budget"].__setitem__("max_grid_polygons", 0)),
        )
        for name, change in scenarios:
            with self.subTest(name=name):
                self.walls = walls_declaration(self.dims)
                change(self.walls)
                write_json(self.pipeline / "walls.json", self.walls)
                self.config_clean()

    def test_contour_offset_within_linear_design_tolerance(self) -> None:
        run = self.walls["wall_runs"][0]
        run["start_cm"][1] = run["end_cm"][1] = 0.25
        write_json(self.pipeline / "walls.json", self.walls)
        # 0.25 cm is inside 0.5 cm design tolerance, but far above 0.001 cm epsilon.
        self.config_clean()

    def test_historical_examples_legacy_is_unchanged(self) -> None:
        (self.pipeline / "walls.json").unlink()
        write_json(self.pipeline / "assembly.json", self.original_assembly)
        result, report = self.validate("--warnings-as-errors")
        self.assertEqual(result.returncode, 0, report["summary"])
        for rule in ("G-76", "G-77", "G-82", "G-83"):
            self.assertTrue(self.findings(report, (rule,), "PASS"), rule)
        self.assertTrue(self.findings(report, ("G-81",), "SKIP"))

    def test_other_historical_fixtures_remain_legacy(self) -> None:
        sources = {
            "stepped-tower": ROOT / "specs" / "fixtures" / "stepped-tower",
            "form-precision": ROOT / "specs" / "fixtures" / "form-precision" / "specs" / "pipeline",
        }
        for name, source in sources.items():
            with self.subTest(fixture=name):
                self.pipeline = self.temp / name
                shutil.copytree(source, self.pipeline)
                self.assertFalse((self.pipeline / "walls.json").exists())
                for args in (("--warnings-as-errors",), ("--build",)):
                    with self.subTest(mode=args):
                        result, report = self.validate(*args)
                        self.assertEqual(result.returncode, 0, report["summary"])
                        for rule in ("G-76", "G-77", "G-82", "G-83"):
                            self.assertTrue(self.findings(report, (rule,), "PASS"), rule)
                        self.assertTrue(self.findings(report, ("G-81",), "SKIP"))


# Mutation registry. Each mutation changes one input property in a fresh copy;
# ID gaps mean dangling references, not a fictional mandatory numeric sequence.
# Rules are pinned to the contract, allowing G-7 for invalid JSON constants and
# existing G-9/G-10/G-31 for the established generic provenance machinery.
Mutation = Callable[[OfflineCase], None]
CASES: list[tuple[str, Mutation, tuple[str, ...], str]] = []


def case(name: str, mutation: Mutation, *rules: str, location: str = "") -> None:
    CASES.append((name, mutation, rules, location))


def field(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(test: OfflineCase) -> None:
        obj: Any = test.walls
        for part in path[:-1]:
            obj = obj[part]
        obj[path[-1]] = value
        write_json(test.pipeline / "walls.json", test.walls,
                   allow_nan=isinstance(value, float) and not math.isfinite(value))
    return mutate


def drop(path: tuple[Any, ...]) -> Mutation:
    def mutate(test: OfflineCase) -> None:
        obj: Any = test.walls
        for part in path[:-1]:
            obj = obj[part]
        del obj[path[-1]]
        write_json(test.pipeline / "walls.json", test.walls)
    return mutate


for name, path, value in (
    ("selector_unknown", ("wall_technique",), "not_a_route"),
    ("selector_null", ("wall_technique",), None),
    ("selector_boolean", ("wall_technique",), True),
):
    case(name, field(path, value), "G-92")
case("selector_missing", drop(("wall_technique",)), "G-92")

for name, path, value in (
    ("contour_wrong_syntax", ("wall_runs", 0, "contour_ref"), "F-S"),
    ("contour_wrong_file", ("wall_runs", 0, "contour_ref"), "massing.json:facades:F-S"),
    ("contour_wrong_collection", ("wall_runs", 0, "contour_ref"), "dimensions.json:openings:OP-G-01"),
    ("contour_unknown_id", ("wall_runs", 0, "contour_ref"), "dimensions.json:facades:F-BOGUS"),
    ("contour_misaligned_side", ("wall_runs", 0, "contour_ref"), "dimensions.json:facades:F-N"),
    ("contour_off_line", ("wall_runs", 0, "end_cm"), [1800.0, 2.0]),
    ("contour_beyond_segment", ("wall_runs", 0, "end_cm"), [1801.0, 0.0]),
    ("reference_face_outer_unsupported", ("reference_face",), "outer"),
    ("reference_face_missing_value", ("reference_face",), None),
    ("run_id_duplicate", ("wall_runs", 1, "id"), "RUN-001"),
    ("return_run_id_duplicate", ("upper_returns", 0, "id"), "RUN-001"),
    ("block_id_duplicate", ("blocks", 1, "id"), "BLK-001"),
    ("opening_id_duplicate", ("openings", 1, "id"), "OP-001"),
    ("run_block_id_gap", ("wall_runs", 0, "block_id"), "BLK-099"),
    ("return_block_id_gap", ("upper_returns", 0, "block_id"), "BLK-099"),
    ("return_neighbour_id_gap", ("upper_returns", 0, "adjacent_run_ids"), ["RUN-001", "RUN-099"]),
    ("return_duplicate_neighbours", ("upper_returns", 0, "adjacent_run_ids"), ["RUN-001", "RUN-001"]),
    ("return_self_neighbour", ("upper_returns", 0, "adjacent_run_ids"), ["RUN-001", "RET-001"]),
    ("return_wrong_neighbour_count", ("upper_returns", 0, "adjacent_run_ids"), ["RUN-001"]),
    ("zero_length", ("wall_runs", 0, "end_cm"), [0.0, 0.0]),
    ("zero_thickness", ("wall_runs", 0, "thickness_cm"), 0.0),
    ("negative_thickness", ("wall_runs", 0, "thickness_cm"), -1.0),
    ("boolean_thickness", ("wall_runs", 0, "thickness_cm"), True),
    ("outward_zero", ("wall_runs", 0, "outward"), [0.0, 0.0]),
    ("outward_nonunit", ("wall_runs", 0, "outward"), [0.0, -2.0]),
    ("outward_nonperpendicular", ("wall_runs", 0, "outward"), [1.0, 0.0]),
    ("outward_exceeds_unit_epsilon", ("wall_runs", 0, "outward"), [0.001, -0.9999995]),
    ("outward_bad_arity", ("wall_runs", 0, "outward"), [0.0, -1.0, 0.0]),
    ("base_equals_top", ("wall_runs", 0, "top_z_cm"), 0.0),
    ("run_below_block", ("wall_runs", 0, "base_z_cm"), -1.0),
    ("run_above_block", ("wall_runs", 0, "top_z_cm"), 421.0),
    ("return_above_block", ("upper_returns", 0, "top_z_cm"), 421.0),
    ("block_reversed_levels", ("blocks", 0, "z_range_cm"), [420.0, 0.0]),
    ("linear_epsilon_zero", ("numeric_epsilon_cm",), 0.0),
    ("linear_epsilon_negative", ("numeric_epsilon_cm",), -0.1),
    ("unit_epsilon_zero", ("numeric_unit_epsilon",), 0.0),
    ("unit_epsilon_boolean", ("numeric_unit_epsilon",), True),
    ("tolerance_not_copied", ("tolerances", "linear_cm"), 0.6),
    ("area_tolerance_not_copied", ("tolerances", "area_m2"), 0.06),
    ("angle_tolerance_not_copied", ("tolerances", "angle_deg"), 0.02),
    ("tolerance_extra_key", ("tolerances", "numeric_epsilon_cm"), 0.001),
    ("unknown_wall_property", ("wall_runs", 0, "invented"), 1),
    ("unknown_root_property", ("invented",), 1),
):
    rules = ("G-93", "G-1") if name == "unknown_root_property" else ("G-93",)
    case(name, field(path, value), *rules)

for name, path, value in (
    ("opening_unknown_run", ("openings", 0, "wall_run_id"), "RUN-099"),
    ("opening_unknown_kind", ("openings", 0, "kind"), "entrance"),
    ("opening_negative_u", ("openings", 0, "u_range_cm"), [-1.0, 315.0]),
    ("opening_reversed_u", ("openings", 0, "u_range_cm"), [315.0, 135.0]),
    ("opening_zero_width", ("openings", 0, "u_range_cm"), [135.0, 135.0]),
    ("opening_past_end", ("openings", 1, "u_range_cm"), [575.0, 1801.0]),
    ("opening_negative_sill", ("openings", 0, "sill_cm"), -1.0),
    ("opening_head_at_sill", ("openings", 0, "head_cm"), 90.0),
    ("opening_head_above_wall", ("openings", 0, "head_cm"), 421.0),
    ("opening_overlap_u", ("openings", 1, "u_range_cm"), [300.0, 400.0]),
):
    case(name, field(path, value), "G-94", "G-93")

for name, path, value in (
    ("budget_negative", ("wall_runs", 0, "topology_budget", "max_grid_polygons"), -1),
    ("budget_noninteger", ("wall_runs", 0, "topology_budget", "max_base_active_polygons"), 2.5),
    ("budget_boolean", ("wall_runs", 0, "topology_budget", "max_evaluated_triangles"), True),
    ("budget_extra_key", ("wall_runs", 0, "topology_budget", "guessed_faces"), 1),
):
    case(name, field(path, value), "G-97")
case("budget_missing_key", drop(("wall_runs", 0, "topology_budget", "max_grid_polygons")), "G-97")
case("budget_missing_object", drop(("upper_returns", 0, "topology_budget")), "G-97", "G-93")
case("tolerance_missing_key", drop(("tolerances", "linear_cm")), "G-93", "G-33")
case("epsilon_missing", drop(("numeric_epsilon_cm",)), "G-93", "G-1")
case("missing_origin_coverage", drop(("origins", "wall_runs[0]")), "G-93", "G-9", location="walls.json")
case("duplicate_origin_coverage", field(("origins", "wall_runs[0].thickness_cm"), {"origin": "given"}), "G-93", "G-9", location="walls.json")
case("unresolved_origin_path", field(("origins", "missing.value"), {"origin": "given"}), "G-93", "G-9", location="walls.json")
case("assumed_without_ledger", field(("origins", "wall_runs[0]"), {"origin": "assumed", "origin_ref": "A-999"}), "G-93", "G-10", "G-13", location="walls.json")
case("derived_unresolvable", field(("origins", "wall_runs[0]"), {"origin": "derived", "derives_from": ["not_a_real.path"]}), "G-93", "G-10", "G-31", location="walls.json")
case("unresolved_origin_input", field(("origin_inputs",), ["does_not_exist[0].value"]), "G-93", "G-31", location="walls.json")
case("nan_thickness", field(("wall_runs", 0, "thickness_cm"), float("nan")), "G-7", location="walls.json")
case("infinite_epsilon", field(("numeric_epsilon_cm",), float("inf")), "G-7", location="walls.json")
case("nan_vector_coordinate", field(("wall_runs", 0, "outward", 0), float("nan")), "G-7", location="walls.json")


def duplicate_facade(test: OfflineCase) -> None:
    # One duplicate insertion; both original facade targets remain available.
    test.dims["facades"].append(copy.deepcopy(test.dims["facades"][0]))
    write_json(test.pipeline / "dimensions.json", test.dims)


def reversed_run(test: OfflineCase) -> None:
    # One geometric mutation: reverse the directed segment without making it zero-length.
    run = test.walls["wall_runs"][0]
    run["start_cm"], run["end_cm"] = run["end_cm"], run["start_cm"]
    write_json(test.pipeline / "walls.json", test.walls)


def outside_linear_tolerance(test: OfflineCase) -> None:
    run = test.walls["wall_runs"][0]
    run["start_cm"][1] = run["end_cm"][1] = 0.501
    write_json(test.pipeline / "walls.json", test.walls)


def missing_walls(test: OfflineCase) -> None:
    test.mock_poly_assembly()
    test.calibrate_mock_echo()
    (test.pipeline / "walls.json").unlink()


def unreadable_walls(test: OfflineCase) -> None:
    (test.pipeline / "walls.json").write_bytes(b'{"wall_technique": "poly_surface_shell_v1",\n')


def bad_nonempty_draft(test: OfflineCase) -> None:
    # Move the same malformed run to draft status, then inject the one fault.
    # Draft status itself is an intentional test precondition, not the fault.
    test.walls["status"] = "draft"
    write_json(test.pipeline / "walls.json", test.walls)
    result, report = test.validate()
    test.assertEqual(result.returncode, 0, report["summary"])
    test.walls["wall_runs"][0]["thickness_cm"] = 0
    write_json(test.pipeline / "walls.json", test.walls)


def overlapping_u_disjoint_v(test: OfflineCase) -> None:
    # Calibrate a valid declaration with disjoint vertical intervals first.
    test.walls["openings"][1]["head_cm"] = 80.0
    write_json(test.pipeline / "walls.json", test.walls)
    test.config_clean()
    # The single fault now overlaps only in plan u, not in vertical extent.
    test.walls["openings"][1]["u_range_cm"] = [135.0, 315.0]
    write_json(test.pipeline / "walls.json", test.walls)


def invalid_echo(test: OfflineCase, key: str, value: Any) -> None:
    test.mock_poly_assembly()
    test.calibrate_mock_echo()
    test.assembly[key] = value
    write_json(test.pipeline / "assembly.json", test.assembly)


def missing_echo(test: OfflineCase) -> None:
    test.mock_poly_assembly()
    test.calibrate_mock_echo()
    del test.assembly["wall_technique"]
    write_json(test.pipeline / "assembly.json", test.assembly)


def mixed_legacy_array(test: OfflineCase, key: str, value: list) -> None:
    test.mock_poly_assembly()
    test.calibrate_mock_echo()
    test.assembly[key] = value
    write_json(test.pipeline / "assembly.json", test.assembly)


def explicit_legacy_missing_array(test: OfflineCase, key: str) -> None:
    test.walls["wall_technique"] = LEGACY
    test.assembly = copy.deepcopy(test.original_assembly)
    test.assembly["wall_technique"] = LEGACY
    test.persist()
    # The precondition itself must be a functioning explicitly-selected legacy route.
    result, report = test.validate("--warnings-as-errors")
    test.assertEqual(result.returncode, 0, test.findings(
        report, tuple(f"G-{i}" for i in range(1, 101)), "FAIL")[:12])
    test.assertTrue(test.findings(report, ("G-92",), "PASS"))
    for rule in ("G-76", "G-77", "G-82", "G-83"):
        test.assertTrue(test.findings(report, (rule,), "PASS"), rule)
    del test.assembly[key]
    write_json(test.pipeline / "assembly.json", test.assembly)


case("duplicate_contour_target", duplicate_facade, "G-93")
case("contour_reversed_direction", reversed_run, "G-93")
case("contour_offset_outside_design_tolerance", outside_linear_tolerance, "G-93")
case("missing_walls_with_selector", missing_walls, "G-92")
case("unreadable_walls_document", unreadable_walls, "G-92", "G-7")
case("nonempty_draft_is_not_exempt_from_geometry_checks", bad_nonempty_draft, "G-93")
case("opening_overlapping_u_disjoint_v", overlapping_u_disjoint_v, "G-94")
case("assembly_selector_conflict", lambda t: invalid_echo(t, "wall_technique", LEGACY), "G-92")
case("assembly_selector_unknown", lambda t: invalid_echo(t, "wall_technique", "bogus"), "G-92")
case("assembly_selector_absent", missing_echo, "G-92")
case("assembly_wrong_manifest_ref", lambda t: invalid_echo(t, "wall_ref", "other.json"), "G-92")
for key in ("wall_cells", "opening_cuts"):
    case(f"poly_with_empty_{key}", lambda t, k=key: mixed_legacy_array(t, k, []), "G-96")
    case(f"poly_with_populated_{key}",
         lambda t, k=key: mixed_legacy_array(t, k, copy.deepcopy(t.original_assembly[k])), "G-96")
    case(f"explicit_legacy_missing_{key}",
         lambda t, k=key: explicit_legacy_missing_array(t, k), "G-96", "G-1")


class FaultInjection(OfflineCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Calibrate once for this validator run. A broken baseline cannot turn
        # unrelated FAILs into apparent fault detections. Still execute each
        # injection so an in-progress implementation gets useful diagnostics.
        control = cls("test_selector_unknown")
        control.setUp()
        cls.baseline_error = None
        try:
            control.config_clean()
        except AssertionError as exc:
            cls.baseline_error = str(exc)
        finally:
            control.doCleanups()


def make_test(mutation: Mutation, rules: tuple[str, ...], location: str) -> Callable:
    def test(self: FaultInjection) -> None:
        with self.subTest(stage="positive locked-input calibration"):
            self.assertIsNone(self.baseline_error, self.baseline_error)
        mutation(self)
        with self.subTest(stage="injected fault"):
            self.must_fail(rules, location)
    return test


for _name, _mutation, _rules, _location in CASES:
    _test = make_test(_mutation, _rules, _location)
    _test.__name__ = "test_" + _name
    setattr(FaultInjection, _test.__name__, _test)


class RuntimeBoundary(OfflineCase):
    def assert_skips(self, report: dict) -> None:
        for rule in RUNTIME_GATES:
            rows = self.findings(report, (rule,))
            self.assertTrue(rows, f"{rule} must be visible; absence is not evidence")
            self.assertTrue(any(row.get("severity") == "SKIP" for row in rows), (rule, rows))
            self.assertFalse(any(row.get("severity") == "PASS" for row in rows), (rule, rows))

    def test_missing_future_artifacts_are_skipped_not_passed(self) -> None:
        self.assertFalse((self.pipeline / "wall_surface.json").exists())
        self.assertFalse((self.pipeline / "wall_surface.ms").exists())
        _, report = self.validate()
        self.assert_skips(report)
        for rule in LEGACY_GATES:
            self.assertTrue(self.findings(report, (rule,), "SKIP"), (rule, self.findings(report, (rule,))))
            self.assertFalse(self.findings(report, (rule,), "PASS"), rule)

    def test_invalid_selector_never_selects_legacy(self) -> None:
        self.walls["wall_technique"] = "unknown"
        write_json(self.pipeline / "walls.json", self.walls)
        result, report = self.validate()
        self.assertEqual(result.returncode, 1, report["summary"])
        self.assertTrue(self.findings(report, ("G-92",), "FAIL"))
        self.assertFalse(self.findings(report, ("G-92",), "PASS"))
        for rule in LEGACY_GATES:
            self.assertFalse(self.findings(report, (rule,), "PASS"), (rule, self.findings(report, (rule,))))

    def test_synthetic_echo_is_not_live_evidence(self) -> None:
        self.mock_poly_assembly()
        result, report = self.validate()
        self.assertEqual(result.returncode, 0, report["summary"])
        self.assertTrue(self.findings(report, ("G-92",), "PASS"), self.findings(report, ("G-92",)))
        self.assertFalse(self.findings(report, ("G-96",), "FAIL"), self.findings(report, ("G-96",)))
        self.assert_skips(report)

    def test_draft_assembly_refused_by_build_gate(self) -> None:
        result, report = self.validate("--build")
        self.assertEqual(result.returncode, 1, report["summary"])
        self.assertTrue([row for row in self.findings(report, ("G-4",), "FAIL")
                         if "assembly.json" in str(row.get("location", ""))])
        self.assertTrue([row for row in self.findings(report, ("G-4",), "PASS")
                         if "walls.json" in str(row.get("location", ""))])
        self.assert_skips(report)

    def test_legacy_builder_refuses_poly_before_writing(self) -> None:
        out = self.temp / "unbuilt-output"
        result = self.run_script(ASSEMBLER, "--in", self.pipeline, "--out", out, "--json")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("poly", (result.stdout + result.stderr).lower())
        self.assertFalse((out / "assembly.json").exists())
        self.assertFalse((out / "assembly.ms").exists())

    def test_refused_poly_does_not_overwrite_existing_output(self) -> None:
        out = self.temp / "existing-output"
        out.mkdir()
        sentinels = {"assembly.json": b"existing json sentinel\n",
                     "assembly.ms": b"existing script sentinel\n"}
        for name, data in sentinels.items():
            (out / name).write_bytes(data)
        result = self.run_script(ASSEMBLER, "--in", self.pipeline, "--out", out, "--json")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("poly", (result.stdout + result.stderr).lower())
        for name, data in sentinels.items():
            self.assertEqual((out / name).read_bytes(), data, name)


if __name__ == "__main__":
    print(f"Phase16 P2 offline: {len(CASES)} isolated mutation cases; runtime SKIP is not PASS.",
          file=sys.stderr)
    unittest.main(verbosity=2)
