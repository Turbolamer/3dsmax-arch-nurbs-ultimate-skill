#!/usr/bin/env python3
"""Independent, offline tests of explicit legacy walls at the S5 build boundary.

Run from any directory: python -B Audit/test_phase16_legacy_build.py -v

The test copies examples and uses the synthetic, given-origin wall declaration
from test_phase16_p2_cases in private temporary directories. It is self-contained
apart from the standard library and project scripts/fixtures under test: it never
imports another test or the builder/validator implementation, runs Max, installs
anything, or writes to a project in the repository. Failures are contract
regressions, not xfails: P2 is in progress, so a test may expose an unfixed
fail-open builder. No result is evidence of a poly build or live Max geometry.
"""

from __future__ import annotations

import copy
import hashlib
import json
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
LEGACY = "legacy_cells_v1"
OLD_REVISION = "6c0f27b"  # P0/P1 baseline, before the current P2 edits
OUTPUTS = ("assembly.json", "assembly.ms")
SCRIPT_NAMES = ("place_components.py", "validate_specs.py", "scene_units.py", "curve_gen.py",
                "wall_cell_coverage.py")
BUILD_MODES = ((), ("--build",))
STATUS_MODES = ((), ("--build",), ("--build", "--allow-draft"))
SCRIPT_SENTINEL = b"-- AUDIT SENTINEL: existing script, do not overwrite\n"


def walls_declaration(dimensions: dict[str, Any]) -> dict[str, Any]:
    """Self-contained copy of the synthetic fixture in test_phase16_p2_cases.

    Only the caller's route changes to legacy. These values are a hypothetical
    brief, not claims about the user's building or produced poly geometry.
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
        "wall_technique": "poly_surface_shell_v1",
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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, doc: dict[str, Any]) -> None:
    path.write_bytes((json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
                     .encode("utf-8"))


def tree_bytes(path: Path) -> dict[str, tuple[str, bytes]]:
    """Snapshot all output entries, including link targets, not just two files."""
    if not path.exists():
        return {}
    result: dict[str, tuple[str, bytes]] = {}
    for item in sorted(path.rglob("*")):
        name = item.relative_to(path).as_posix()
        if item.is_symlink():
            result[name] = ("symlink", os.fsencode(os.readlink(item)))
        elif item.is_file():
            result[name] = ("file", item.read_bytes())
        elif item.is_dir():
            result[name] = ("directory", b"")
        else:
            raise AssertionError(f"unexpected output entry: {item}")
    return result


class LegacyBuildBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Freeze one source snapshot so concurrent edits cannot split a run.

        Each CLI still runs unmodified production source in a subprocess. At
        teardown report if the working tree changed; the temporary snapshot
        itself is the exact code exercised by every case.
        """
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        cls.source_owner = tempfile.TemporaryDirectory(prefix="phase16-legacy-source-", dir=parent)
        cls.addClassCleanup(cls.source_owner.cleanup)
        script_dir = Path(cls.source_owner.name) / "scripts"
        script_dir.mkdir()
        cls.source_hashes: dict[str, str] = {}
        for name in SCRIPT_NAMES:
            source = (ROOT / "scripts" / name).read_bytes()
            cls.source_hashes[name] = hashlib.sha256(source).hexdigest()
            (script_dir / name).write_bytes(source)
        print("Offline source snapshot: " + ", ".join(
            f"{name}={digest[:16]}" for name, digest in cls.source_hashes.items()), file=sys.stderr)
        cls.builder = script_dir / "place_components.py"
        cls.validator = script_dir / "validate_specs.py"

    @classmethod
    def tearDownClass(cls) -> None:
        drift = [name for name, expected in cls.source_hashes.items()
                 if not (ROOT / "scripts" / name).is_file() or
                 hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest() != expected]
        if drift:
            raise AssertionError(f"scripts changed during test; results apply only to the "
                                 f"temporary snapshot, please rerun: {drift}")

    def setUp(self) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        owner = tempfile.TemporaryDirectory(prefix="phase16-legacy-build-", dir=parent)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)
        self.sequence = 0

    def fresh(self, label: str) -> Path:
        self.sequence += 1
        path = self.temp / f"{self.sequence:03d}-{label}"
        path.mkdir()
        return path

    def project(self, *, explicit: bool = True) -> tuple[Path, dict[str, Any] | None]:
        pipeline = self.fresh("input") / "pipeline"
        shutil.copytree(EXAMPLES, pipeline)
        self.assertFalse((pipeline / "walls.json").exists(), "examples changed route")
        self.assertFalse((pipeline / "wall_surface.json").exists())
        self.assertFalse((pipeline / "wall_surface.ms").exists())
        assembly = read_json(pipeline / "assembly.json")
        self.assertNotIn("wall_technique", assembly)
        if not explicit:
            return pipeline, None
        walls = walls_declaration(read_json(pipeline / "dimensions.json"))
        walls["wall_technique"] = LEGACY
        self.assertEqual(walls["status"], "locked")
        self.assertTrue(all(entry == {"origin": "given"} for entry in walls["origins"].values()))
        assembly["wall_technique"] = LEGACY
        write_json(pipeline / "walls.json", walls)
        write_json(pipeline / "assembly.json", assembly)
        return pipeline, walls

    def command(self, script: Path, *args: object) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-B", str(script), *(str(arg) for arg in args)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        try:
            return subprocess.run(command, cwd=self.temp, env=env, text=True, encoding="utf-8",
                                  errors="replace", capture_output=True, timeout=120, check=False)
        except subprocess.TimeoutExpired as exc:
            self.fail(f"offline command timed out: {command!r}: {exc}")

    def build(self, pipeline: Path, out: Path, *flags: str,
              script: Path | None = None) -> subprocess.CompletedProcess[str]:
        return self.command(script or self.builder, "--in", pipeline, "--out", out, "--json", *flags)

    def validate(self, pipeline: Path, *flags: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = self.command(self.validator, "--dir", pipeline, "--json", *flags)
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"validator did not return JSON: {exc}; stderr={result.stderr!r}; "
                      f"stdout={result.stdout[:2000]!r}")
        self.assertEqual(result.returncode, report.get("exit_code"), report.get("summary"))
        self.assertIsInstance(report.get("findings"), list)
        internal = [r for r in report["findings"]
                    if "internal error" in str(r.get("detail", "")).lower()]
        self.assertFalse(internal, internal)
        return result, report

    @staticmethod
    def rows(report: dict, rule: str, severity: str) -> list[dict]:
        return [r for r in report["findings"] if r.get("rule") == rule
                and r.get("severity") == severity]

    def valid_control(self, pipeline: Path, *, explicit: bool = True, flags: tuple[str, ...] = ()) -> None:
        result, report = self.validate(pipeline, *flags)
        failures = [r for r in report["findings"] if r.get("severity") == "FAIL"]
        self.assertEqual(result.returncode, 0, failures)
        self.assertTrue(self.rows(report, "G-92", "PASS"), self.rows(report, "G-92", "SKIP"))
        if explicit:
            self.assertTrue(self.rows(report, "G-93", "PASS"), failures)
        for rule in ("G-76", "G-77", "G-82", "G-83"):
            self.assertTrue(self.rows(report, rule, "PASS"), (rule, failures))

    def output_with_sentinels(self, pipeline: Path, walls: dict[str, Any]) -> Path:
        """The JSON sentinel is *valid* route data, so it cannot mask the target fault.

        A distinctive serialization is still a sentinel: exact bytes, including
        spacing and trailing LF, must survive a refusal. The positive control
        proves this same wall/assembly/output layout can really build.
        """
        out = self.fresh("output")
        write_json(out / "walls.json", walls)
        assembly = read_json(pipeline / "assembly.json")
        sentinel = (json.dumps(assembly, ensure_ascii=False, separators=(", ", ": ")) + "\n").encode("utf-8")
        (out / "assembly.json").write_bytes(sentinel)
        (out / "assembly.ms").write_bytes(SCRIPT_SENTINEL)
        return out

    def assert_built(self, result: subprocess.CompletedProcess[str], out: Path) -> dict:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        try:
            summary = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"builder success without JSON summary: {exc}; {result.stdout!r}")
        self.assertEqual(summary.get("exit_code"), 0)
        self.assertEqual((summary.get("placements"), summary.get("opening_cuts")), (136, 16))
        assembly = read_json(out / "assembly.json")
        self.assertEqual((len(assembly["placements"]), len(assembly["opening_cuts"]),
                          len(assembly["wall_cells"])), (136, 16, 52))
        script = (out / "assembly.ms").read_bytes()
        self.assertIn(b"host_node.isHidden = true", script)
        self.assertNotIn(b"addModifier", script)
        return assembly

    def matched_output_control(self, pipeline: Path, walls: dict[str, Any],
                               flags: tuple[str, ...]) -> tuple[Path, dict]:
        out = self.output_with_sentinels(pipeline, walls)
        before = tree_bytes(out)
        result = self.build(pipeline, out, *flags)
        assembly = self.assert_built(result, out)
        self.assertEqual(assembly.get("wall_technique"), LEGACY)
        self.assertNotIn("wall_ref", assembly)
        self.assertNotEqual((out / "assembly.json").read_bytes(), before["assembly.json"][1])
        self.assertNotEqual((out / "assembly.ms").read_bytes(), SCRIPT_SENTINEL)
        self.assertEqual((out / "walls.json").read_bytes(), before["walls.json"][1])
        self.assertEqual(set(tree_bytes(out)), set(before), "builder wrote undeclared files")
        return out, assembly

    def assert_refused_untouched(self, pipeline: Path, out: Path, *flags: str) -> None:
        before = tree_bytes(out)
        self.assertIn("assembly.json", before)
        self.assertEqual(before["assembly.ms"], ("file", SCRIPT_SENTINEL))
        inputs_before = tree_bytes(pipeline)
        result = self.build(pipeline, out, *flags)
        after = tree_bytes(out)
        # Evaluate both the bytes and return code even on success/crash. Report
        # changed paths instead of dumping a 150KB generated assembly diff.
        changed = sorted(name for name in set(before) | set(after)
                         if before.get(name) != after.get(name))
        input_after = tree_bytes(pipeline)
        changed_input = sorted(name for name in set(inputs_before) | set(input_after)
                               if inputs_before.get(name) != input_after.get(name))
        self.assertFalse(changed or changed_input or result.returncode == 0,
                         f"invalid wall state: exit={result.returncode}; "
                         f"changed output={changed}; changed input={changed_input}; "
                         f"stderr={result.stderr[:1000]!r}")
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        message = (result.stdout + result.stderr).lower()
        self.assertTrue("wall" in message or "g-93" in message or "g-4" in message,
                        f"refusal did not identify the wall boundary: {message}")

    def test_historical_empty_out_matches_old_builder_when_git_available(self) -> None:
        pipeline, _ = self.project(explicit=False)
        self.valid_control(pipeline, explicit=False)
        out = self.fresh("historical-out")
        self.assertEqual(tree_bytes(out), {})
        result = self.build(pipeline, out)
        assembly = self.assert_built(result, out)
        self.assertNotIn("wall_technique", assembly)
        self.assertEqual(set(tree_bytes(out)), set(OUTPUTS))

        # Obtain BOTH the old builder and its unit helper from the same commit.
        # A missing Git executable/history is a skip of the comparison only;
        # the modern positive above has already actually built.
        old_dir = self.fresh("old-revision")
        for name in ("place_components.py", "scene_units.py"):
            try:
                git = subprocess.run(["git", "show", f"{OLD_REVISION}:scripts/{name}"], cwd=ROOT,
                                     capture_output=True, timeout=30, check=False)
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                self.skipTest(f"historical git show unavailable: {exc}")
            if git.returncode:
                self.skipTest(f"historical commit/file unavailable: {git.stderr.decode(errors='replace')}")
            (old_dir / name).write_bytes(git.stdout)
        old_out = self.fresh("historical-old-out")
        old = self.build(pipeline, old_out, script=old_dir / "place_components.py")
        self.assert_built(old, old_out)
        self.assertEqual(set(tree_bytes(old_out)), set(OUTPUTS))
        for name in OUTPUTS:
            self.assertEqual((out / name).read_bytes(), (old_out / name).read_bytes(), name)

    def test_explicit_legacy_locked_builds_with_matching_output_walls(self) -> None:
        for flags in STATUS_MODES:
            with self.subTest(mode=flags):
                pipeline, walls = self.project()
                assert walls is not None
                self.valid_control(pipeline, flags=flags)
                out, _ = self.matched_output_control(pipeline, walls, flags)
                # Validate the actual emitted assembly together with its real
                # upstream inputs, not just a hand-crafted echo or self-check.
                (pipeline / "assembly.json").write_bytes((out / "assembly.json").read_bytes())
                self.valid_control(pipeline, flags=flags)
                self.assertFalse((pipeline / "wall_surface.json").exists())
                self.assertFalse((out / "wall_surface.json").exists())
                self.assertFalse((out / "wall_surface.ms").exists())

    def test_empty_explicit_output_has_no_undocumented_side_effects(self) -> None:
        """Until a separate-out policy is approved, refusal must leave no files.

        Revisit this assertion if a safe separate-out contract is documented and
        approved. Do not silently create/copy walls.json: current S5 declares
        only assembly.json/.ms as output and a selector needs its wall document.
        """
        for flags in BUILD_MODES:
            with self.subTest(mode=flags):
                pipeline, walls = self.project()
                assert walls is not None
                self.valid_control(pipeline, flags=flags)
                self.matched_output_control(pipeline, walls, flags)
                out = self.fresh("empty-explicit-out")
                inputs_before = tree_bytes(pipeline)
                result = self.build(pipeline, out, *flags)
                self.assertEqual(tree_bytes(pipeline), inputs_before, "builder changed input")
                produced = tree_bytes(out)
                self.assertFalse(result.returncode == 0 or produced,
                                 f"empty output: exit={result.returncode}, files={sorted(produced)}; "
                                 "success requires a documented, approved safe contract")
                self.assertNotIn("Traceback", result.stderr)

    def test_nonlocked_walls_never_build_even_with_allow_draft(self) -> None:
        for status in ("draft", "superseded"):
            for flags in STATUS_MODES:
                with self.subTest(status=status, mode=flags):
                    pipeline, walls = self.project()
                    assert walls is not None
                    self.valid_control(pipeline)
                    self.matched_output_control(pipeline, walls, flags)
                    walls["status"] = status
                    write_json(pipeline / "walls.json", walls)
                    # Matching the non-locked declaration on both sides prevents
                    # a future mismatch guard from masking a missing status gate.
                    out = self.output_with_sentinels(pipeline, walls)
                    self.assert_refused_untouched(pipeline, out, *flags)

    def test_invalid_locked_wall_inputs_reach_target_g93(self) -> None:
        for label, mutate, target in WALL_FAULTS:
            for flags in BUILD_MODES:
                with self.subTest(fault=label, mode=flags):
                    pipeline, walls = self.project()
                    assert walls is not None
                    self.valid_control(pipeline, flags=flags)
                    mutate(walls)
                    write_json(pipeline / "walls.json", walls)
                    result, report = self.validate(pipeline, *flags)
                    bad = self.rows(report, "G-93", "FAIL")
                    self.assertEqual(result.returncode, 1, report.get("summary"))
                    self.assertTrue([r for r in bad if target in str(r.get("location", ""))], bad)
                    self.assertFalse(self.rows(report, "G-93", "PASS"), bad)
                    if label == "origin":
                        self.assertTrue([r for r in self.rows(report, "G-9", "FAIL")
                                         if "walls.json::wall_runs[0]" in str(r.get("location", ""))])

    def test_builder_refuses_each_invalid_locked_wall_input(self) -> None:
        for label, mutate, _target in WALL_FAULTS:
            for flags in BUILD_MODES:
                with self.subTest(fault=label, mode=flags):
                    pipeline, walls = self.project()
                    assert walls is not None
                    self.valid_control(pipeline, flags=flags)
                    self.matched_output_control(pipeline, walls, flags)
                    mutate(walls)
                    write_json(pipeline / "walls.json", walls)
                    # The output wall matches the bad input exactly; route matching
                    # cannot hide failure to validate the declaration itself.
                    out = self.output_with_sentinels(pipeline, walls)
                    self.assertEqual(read_json(out / "walls.json"), read_json(pipeline / "walls.json"))
                    self.assert_refused_untouched(pipeline, out, *flags)

    def test_conflicting_output_wall_document_is_not_just_same_selector(self) -> None:
        for label, mutate in OUTPUT_FAULTS:
            for flags in BUILD_MODES:
                with self.subTest(fault=label, mode=flags):
                    pipeline, walls = self.project()
                    assert walls is not None
                    self.valid_control(pipeline, flags=flags)
                    self.matched_output_control(pipeline, walls, flags)
                    other = copy.deepcopy(walls)
                    mutate(other)
                    self.assertEqual(other["wall_technique"], LEGACY)
                    self.assertNotEqual(other, walls)
                    if label == "other-geometry":
                        # Confirm the alternative geometry is individually valid:
                        # this is an identity disagreement, not an invalid shape.
                        try:
                            write_json(pipeline / "walls.json", other)
                            self.valid_control(pipeline, flags=flags)
                        finally:
                            write_json(pipeline / "walls.json", walls)
                    out = self.output_with_sentinels(pipeline, other)
                    self.assert_refused_untouched(pipeline, out, *flags)

    def test_ambiguous_output_route_and_poly_reference_are_refused(self) -> None:
        for label in ("duplicate-walls", "poly-manifest", "poly-ref"):
            for flags in BUILD_MODES:
                with self.subTest(fault=label, mode=flags):
                    pipeline, walls = self.project()
                    assert walls is not None
                    self.valid_control(pipeline, flags=flags)
                    self.matched_output_control(pipeline, walls, flags)
                    out = self.output_with_sentinels(pipeline, walls)
                    if label == "duplicate-walls":
                        (out / "pipeline").mkdir()
                        write_json(out / "pipeline" / "walls.json", walls)
                    elif label == "poly-manifest":
                        (out / "wall_surface.json").write_bytes(b'{"sentinel":"do not touch"}\n')
                    else:
                        assembly = read_json(out / "assembly.json")
                        assembly["wall_ref"] = "wall_surface.json"
                        write_json(out / "assembly.json", assembly)
                    self.assert_refused_untouched(pipeline, out, *flags)

    def check_linked_output(self, link_kind: str) -> None:
        pipeline, walls = self.project()
        assert walls is not None
        self.valid_control(pipeline)
        self.matched_output_control(pipeline, walls, ())
        out = self.output_with_sentinels(pipeline, walls)
        external = self.fresh("external") / "protected.ms"
        external.write_bytes(SCRIPT_SENTINEL)
        (out / "assembly.ms").unlink()
        try:
            if link_kind == "symlink":
                (out / "assembly.ms").symlink_to(external)
            else:
                os.link(external, out / "assembly.ms")
        except (OSError, NotImplementedError) as exc:
            # Platforms may not grant symlink privileges or hardlinks.
            self.skipTest(f"{link_kind} unavailable on this host: {exc}")
        before = tree_bytes(out)
        inputs_before = tree_bytes(pipeline)
        result = self.build(pipeline, out)
        self.assertEqual(tree_bytes(out), before, "linked output changed")
        self.assertEqual(external.read_bytes(), SCRIPT_SENTINEL, "link target changed")
        self.assertEqual(tree_bytes(pipeline), inputs_before)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_symlinked_output_cannot_modify_another_file(self) -> None:
        self.check_linked_output("symlink")

    def test_hardlinked_output_cannot_modify_another_file(self) -> None:
        self.check_linked_output("hardlink")


# Each operation changes exactly one field of an otherwise calibrated fixture.
WALL_FAULTS: tuple[tuple[str, Callable[[dict], None], str], ...] = (
    ("tolerances", lambda w: w["tolerances"].__setitem__("linear_cm", 0.6),
     "walls.json::tolerances"),
    ("reversed-block", lambda w: w["blocks"][0].__setitem__("z_range_cm", [420.0, 0.0]),
     "walls.json::blocks[0].z_range_cm"),
    ("origin", lambda w: w["origins"].pop("wall_runs[0]"), "walls.json::origins"),
)

OUTPUT_FAULTS: tuple[tuple[str, Callable[[dict], None]], ...] = (
    ("other-project", lambda w: w.__setitem__("project", "other-project")),
    ("draft", lambda w: w.__setitem__("status", "draft")),
    ("superseded", lambda w: w.__setitem__("status", "superseded")),
    # A different but still forward, on-contour run (and valid opening bounds).
    ("other-geometry", lambda w: w["wall_runs"][0].__setitem__("end_cm", [1700.0, 0.0])),
)


if __name__ == "__main__":
    unittest.main(verbosity=2)
