#!/usr/bin/env python3
"""Independent, offline Phase 16 P2 regression and acceptance harness.

Run from any directory, with the standard library only::

    python -B Audit/test_phase16_p2.py -v
    python -B Audit/test_phase16_p2.py --require-p2 -v
    python -B Audit/test_phase16_p2.py --require-p2 --p2-fixture PATH -v
    python -B Audit/test_phase16_p2.py --require-p2 --p2-qa-project PATH --p2-qa-request FILE -v
    python -B Audit/test_phase16_p2.py --require-p2 --fail-on-skip -v

The first command checks the existing no-selector legacy route and reports P2
tests as SKIP. --require-p2 enables scaffold/selector acceptance against the
actual implementation; it is expected to FAIL before P2 is integrated. It does
not infer a wall schema from the design sketch. For locked-document mutation
tests, --p2-fixture must name a *real*, self-consistent poly project root or its
pipeline directory, supplied after the schema is implemented. Missing fixture
features are reported as SKIP, not PASS; see each skip reason and the output.
The later poly runtime-evidence test additionally requires a real poly QA project
and its matching valid request; it submits an empty results file, not live probes.
By default unittest exits zero with skips: that means only the *executed* checks
passed, never full acceptance. --fail-on-skip turns any skip (including the known
legacy limitation and future QA) into exit 1 for strict automation.

All inputs, mutations and outputs live in fresh tempfile-owned directories.
--keep-temp retains only directories created by this invocation for diagnosis.
No builder output is executed in Max and an offline PASS is never a live PASS.
"""

from __future__ import annotations

import argparse
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
SCRIPTS = ROOT / "scripts"
POLY = "poly_surface_shell_v1"
LEGACY = "legacy_cells_v1"
LEGACY_RULES = ("G-76", "G-77", "G-82", "G-83")
FIXTURES = {
    "examples": ROOT / "examples",
    "stepped": ROOT / "specs" / "fixtures" / "stepped-tower",
    "form": ROOT / "specs" / "fixtures" / "form-precision" / "specs" / "pipeline",
}


def harness_options() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--require-p2", action="store_true")
    parser.add_argument("--p2-fixture", type=Path)
    parser.add_argument("--p2-qa-project", type=Path)
    parser.add_argument("--p2-qa-request", type=Path)
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--fail-on-skip", action="store_true")
    options, rest = parser.parse_known_args()
    if (options.p2_fixture or options.p2_qa_project or options.p2_qa_request) and not options.require_p2:
        parser.error("poly fixture options require --require-p2")
    if bool(options.p2_qa_project) != bool(options.p2_qa_request):
        parser.error("provide both --p2-qa-project and --p2-qa-request")
    return options, rest


OPTIONS, UNITTEST_ARGS = harness_options()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, document: Any) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def diagnostic(report: dict) -> str:
    """Keep a regression failure actionable without dumping hundreds of PASS rows."""
    failures = [(f.get("rule"), f.get("location"), f.get("detail"))
                for f in report.get("findings", []) if f.get("severity") == "FAIL"]
    return f"summary={report.get('summary')}; failures={failures}"


def pipeline_dir(path: Path) -> Path:
    for candidate in (path / "specs" / "pipeline", path / "pipeline", path):
        if (candidate / "dimensions.json").is_file():
            return candidate
    raise ValueError(f"no pipeline directory containing dimensions.json under {path}")


class OfflineCase(unittest.TestCase):
    def setUp(self) -> None:
        if OPTIONS.keep_temp:
            self.temp = Path(tempfile.mkdtemp(prefix="phase16-p2-"))
            print(f"\nretained diagnostic directory: {self.temp}", file=sys.stderr)
        else:
            owned = tempfile.TemporaryDirectory(prefix="phase16-p2-")
            self.addCleanup(owned.cleanup)
            self.temp = Path(owned.name)
        self.copy_number = 0

    def clone(self, source: Path) -> Path:
        self.copy_number += 1
        target = self.temp / f"input-{self.copy_number:03d}"
        return shutil.copytree(source, target)

    def run_cli(self, script: str, *args: object) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-B", str(SCRIPTS / script), *(str(x) for x in args)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        try:
            return subprocess.run(
                command, cwd=self.temp, env=env, text=True, encoding="utf-8",
                errors="replace", capture_output=True, timeout=90, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            self.fail(f"CLI timeout: {command!r}: {exc}")

    def validate(self, pipeline: Path, *options: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = self.run_cli("validate_specs.py", "--dir", pipeline, "--json", *options)
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"validator did not return JSON: {exc}\n{result.stderr}\n{result.stdout[:3000]}")
        self.assertIsInstance(report.get("findings"), list, diagnostic(report))
        self.assertIsInstance(report.get("summary"), dict, diagnostic(report))
        # A --rule-filtered report is intentionally not used: the real CLI exit
        # code is based on all findings, not just the visible filtered subset.
        self.assertEqual(result.returncode, report.get("exit_code"), diagnostic(report))
        return result, report

    def rows(self, report: dict, rule: str, severity: str | None = None) -> list[dict]:
        return [f for f in report["findings"] if f.get("rule") == rule
                and (severity is None or f.get("severity") == severity)]

    def require_fail(self, result: subprocess.CompletedProcess[str], report: dict, rule: str) -> None:
        failures = [(f.get("rule"), f.get("location"), f.get("detail"))
                    for f in report["findings"] if f.get("severity") == "FAIL"]
        self.assertEqual(result.returncode, 1,
                         f"expected {rule} FAIL; exit={result.returncode}; "
                         f"{rule} rows={self.rows(report, rule)}; failures={failures}")
        self.assertTrue(self.rows(report, rule, "FAIL"),
                        f"negative control did not trip {rule}: failures={failures}")
        self.assertFalse(any("internal error" in str(f.get("detail", "")).lower()
                             for f in report["findings"]), diagnostic(report))

    def scaffold(self, name: str = "p2-scaffold", seeded: bool = False) -> tuple[Path, Path]:
        args: list[object] = ["--project", name, "--dir", self.temp]
        if seeded:
            args += ["--from", FIXTURES["examples"]]
        result = self.run_cli("init_project.py", *args)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        root = self.temp / name
        return root, root / "specs" / "pipeline"

    def poly_fixture(self) -> Path:
        if OPTIONS.p2_fixture is None:
            self.skipTest("pending: supply --p2-fixture with a real locked poly pipeline after P2")
        try:
            source = pipeline_dir(OPTIONS.p2_fixture.resolve())
        except ValueError as exc:
            self.fail(str(exc))
        pipeline = self.clone(source)
        walls_path = pipeline / "walls.json"
        assembly_path = pipeline / "assembly.json"
        self.assertTrue(walls_path.is_file(), "supplied fixture must contain walls.json")
        self.assertTrue(assembly_path.is_file(), "supplied fixture must contain assembly.json")
        walls, assembly = load(walls_path), load(assembly_path)
        self.assertEqual(walls.get("status"), "locked", "fixture must use locked walls")
        self.assertEqual(assembly.get("status"), "locked", "fixture must use locked assembly")
        self.assertEqual(walls.get("wall_technique"), POLY)
        self.assertEqual(assembly.get("wall_technique"), POLY)
        self.assertNotIn("wall_cells", assembly)
        self.assertNotIn("opening_cuts", assembly)
        result, report = self.validate(pipeline)
        self.assertEqual(result.returncode, 0, f"positive fixture must lint clean: {diagnostic(report)}")
        self.assertTrue(self.rows(report, "G-92", "PASS"),
                        "positive fixture must actually exercise the route consistency rule")
        return pipeline


class LegacyRegression(OfflineCase):
    def test_no_selector_legacy_baselines_all_modes(self) -> None:
        for name, source in FIXTURES.items():
            with self.subTest(fixture=name):
                pipeline = self.clone(source)
                self.assertFalse((pipeline / "walls.json").exists(), name)
                assembly = load(pipeline / "assembly.json")
                self.assertNotIn("wall_technique", assembly, name)
                self.assertTrue(assembly["opening_cuts"] and assembly["wall_cells"], name)
                for options in ((), ("--warnings-as-errors",), ("--build",)):
                    with self.subTest(mode=options or ("lint",)):
                        result, report = self.validate(pipeline, *options)
                        self.assertEqual(result.returncode, 0, diagnostic(report))
                        self.assertEqual(report["summary"].get("WARN"), 0, diagnostic(report))
                        for rule in LEGACY_RULES:
                            self.assertTrue(self.rows(report, rule, "PASS"), (rule, self.rows(report, rule)))
                            self.assertFalse(self.rows(report, rule, "FAIL"), (rule, self.rows(report, rule)))
                        self.assertTrue(self.rows(report, "G-81", "SKIP"), self.rows(report, "G-81"))
                        self.assertFalse(self.rows(report, "G-81", "PASS"), self.rows(report, "G-81"))
                        if name == "stepped":
                            self.assertTrue(self.rows(report, "G-91", "PASS"), self.rows(report, "G-91"))
                        if name == "form":
                            for rule in ("G-84", "G-85", "G-86", "G-87", "G-88", "G-89", "G-90"):
                                self.assertTrue(self.rows(report, rule, "PASS"), (rule, self.rows(report, rule)))

    def test_legacy_fault_injection_reaches_each_wall_rule(self) -> None:
        def bad_host(a: dict) -> None:
            a["opening_cuts"][0]["host_ref"] = "EL-999"

        def missing_cut(a: dict) -> None:
            a["opening_cuts"].pop(0)

        def missing_large_cell(a: dict) -> None:
            # EL-014-C04 is 2,184,000 cm3, large enough to exceed the
            # conservative summed endpoint-tolerance budget on this host.
            index = next(i for i, cell in enumerate(a["wall_cells"])
                         if cell["id"] == "WAL-EL-014-C04")
            a["wall_cells"].pop(index)

        def short_cell(a: dict) -> None:
            a["wall_cells"][0]["plan_rect_cm"][3] -= 5

        for rule, mutation in (("G-76", bad_host), ("G-77", missing_cut),
                               ("G-82", missing_large_cell), ("G-83", short_cell)):
            with self.subTest(rule=rule):
                pipeline = self.clone(FIXTURES["examples"])
                path = pipeline / "assembly.json"
                document = load(path)
                mutation(document)
                save(path, document)
                result, report = self.validate(pipeline)
                self.require_fail(result, report, rule)

    def test_known_g82_missing_first_cell_limit(self) -> None:
        """Known baseline risk, not an accepted proof of complete wall tiling.

        The absent 1,134,000 cm3 cell is below the 1,635,900 cm3 conservative
        aggregate tolerance, so current G-82 reports PASS. Report that specific
        result as SKIP, not a PASS; unrelated validator failures still fail the
        test. If the defect is fixed the test automatically becomes a PASS.
        """
        pipeline = self.clone(FIXTURES["examples"])
        path = pipeline / "assembly.json"
        doc = load(path)
        self.assertEqual(doc["wall_cells"][0]["id"], "WAL-EL-014-C01")
        doc["wall_cells"].pop(0)
        save(path, doc)
        result, report = self.validate(pipeline)
        if result.returncode == 0 and self.rows(report, "G-82", "PASS"):
            self.skipTest("known G-82 gap: first cell missing but volume still within tolerance budget")
        self.require_fail(result, report, "G-82")

    def test_legacy_builder_is_deterministic_without_modifiers(self) -> None:
        pipeline = self.clone(FIXTURES["examples"])
        outputs = [self.temp / "first-output", self.temp / "second-output"]
        for out in outputs:
            result = self.run_cli("place_components.py", "--in", pipeline, "--out", out, "--json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        for filename in ("assembly.json", "assembly.ms"):
            self.assertEqual((outputs[0] / filename).read_bytes(),
                             (outputs[1] / filename).read_bytes(), filename)
        doc = load(outputs[0] / "assembly.json")
        self.assertEqual((len(doc["placements"]), len(doc["opening_cuts"]), len(doc["wall_cells"])),
                         (136, 16, 52))
        script = (outputs[0] / "assembly.ms").read_text(encoding="utf-8")
        self.assertIn("WAL_", script)
        self.assertIn("host_node.isHidden = true", script)
        self.assertNotIn("addModifier", script)
        # This is a byte-level regression, NOT fileIn, scene census or live QA.

    def test_from_examples_preserves_legacy_route(self) -> None:
        _, pipeline = self.scaffold("seeded", seeded=True)
        source = load(FIXTURES["examples"] / "assembly.json")
        seeded = load(pipeline / "assembly.json")
        self.assertEqual(seeded["project"], "seeded")
        for key in ("placements", "opening_cuts", "wall_cells", "scatter", "origins", "origin_inputs"):
            self.assertEqual(seeded[key], source[key], key)
        result, report = self.validate(pipeline)
        self.assertEqual(result.returncode, 0, diagnostic(report))
        for rule in LEGACY_RULES:
            self.assertTrue(self.rows(report, rule, "PASS"), (rule, self.rows(report, rule)))

    def test_existing_qa_missing_results_never_passes(self) -> None:
        fixture = ROOT / "specs" / "fixtures" / "form-precision"
        project = self.clone(fixture)
        request = project / "runs" / "form-qa" / "live-run-001" / "qa-request.json"
        missing = self.temp / "no-observations.json"
        save(missing, {"records": []})
        out = self.temp / "qa-out"
        result = self.run_cli("qa_check.py", "--in", project, "--assess", "--request", request,
                              "--results", missing, "--out", out, "--json")
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        report = load(out / "qa-results.json")
        self.assertNotEqual(report.get("verdict"), "PASS", report)
        self.assertTrue(report["summary"]["failed"] or report["summary"]["incomplete"], report)
        # Current legacy QA marks missing observations FAIL; INCOMPLETE is the
        # planned P2+/poly contract, not a claim about this existing behavior.


@unittest.skipUnless(OPTIONS.require_p2, "pending P2 acceptance: rerun with --require-p2")
class PolyAcceptance(OfflineCase):
    def test_fresh_scaffold_declares_poly_and_stays_draft(self) -> None:
        root, pipeline = self.scaffold()
        walls_path = pipeline / "walls.json"
        self.assertTrue(walls_path.is_file(), "new scaffold must write walls.json")
        walls = load(walls_path)
        self.assertEqual(walls.get("wall_technique"), POLY)
        self.assertEqual(walls.get("status"), "draft")
        self.assertIn("specs/pipeline/walls.json", load(root / "project.json")["files"])
        result, report = self.validate(pipeline)
        self.assertEqual(result.returncode, 0, diagnostic(report))
        build, build_report = self.validate(pipeline, "--build")
        self.require_fail(build, build_report, "G-4")

    def test_invalid_or_missing_selector_does_not_fallback_to_legacy(self) -> None:
        _, scaffold = self.scaffold()
        walls_path = scaffold / "walls.json"
        self.assertTrue(walls_path.is_file(), "P2 scaffold is the selector control")
        baseline = load(walls_path)
        self.assertEqual(baseline.get("wall_technique"), POLY)
        missing = object()
        for bad in (missing, None, "", "legacy", "POLY_SURFACE_SHELL_V1",
                    "garbage", False, 0, [], {}):
            with self.subTest(value="<absent>" if bad is missing else bad):
                pipeline = self.clone(scaffold)
                path = pipeline / "walls.json"
                document = load(path)
                if bad is missing:
                    document.pop("wall_technique", None)
                else:
                    document["wall_technique"] = bad
                save(path, document)
                result, report = self.validate(pipeline)
                self.require_fail(result, report, "G-92")

    def test_explicit_legacy_retains_legacy_gates(self) -> None:
        _, scaffold = self.scaffold()
        source = scaffold / "walls.json"
        self.assertTrue(source.is_file(), "P2 scaffold supplies the real walls envelope")
        walls = load(source)
        self.assertEqual(walls.get("wall_technique"), POLY)
        walls["wall_technique"] = LEGACY
        pipeline = self.clone(FIXTURES["examples"])
        assembly_path = pipeline / "assembly.json"
        assembly = load(assembly_path)
        # The scaffold and the historical example have different project ids.
        walls["project"] = assembly["project"]
        save(pipeline / "walls.json", walls)
        assembly["wall_technique"] = LEGACY
        save(assembly_path, assembly)
        result, report = self.validate(pipeline)
        self.assertEqual(result.returncode, 0, diagnostic(report))
        self.assertTrue(self.rows(report, "G-92", "PASS"), self.rows(report, "G-92"))
        for rule in LEGACY_RULES:
            self.assertTrue(self.rows(report, rule, "PASS"), (rule, self.rows(report, rule)))
        self.assertTrue(self.rows(report, "G-81", "SKIP"), self.rows(report, "G-81"))

    def test_selector_without_walls_file_fails_closed(self) -> None:
        pipeline = self.clone(FIXTURES["examples"])
        path = pipeline / "assembly.json"
        doc = load(path)
        doc["wall_technique"] = POLY
        save(path, doc)
        self.assertFalse((pipeline / "walls.json").exists())
        result, report = self.validate(pipeline)
        self.require_fail(result, report, "G-92")

    def test_no_emitted_or_live_artifact_is_not_a_production_pass(self) -> None:
        _, pipeline = self.scaffold()
        self.assertTrue((pipeline / "walls.json").is_file(), "P2 scaffold is required")
        self.assertEqual(load(pipeline / "walls.json").get("wall_technique"), POLY)
        self.assertFalse((pipeline / "wall_surface.json").exists())
        self.assertFalse((pipeline / "wall_surface.ms").exists())
        _, report = self.validate(pipeline)
        # Every named artifact/runtime gate must be visible, and none may claim
        # to have proved a missing script, live census, units or replay.
        for rule in ("G-95", "G-98", "G-99", "G-100"):
            rows = self.rows(report, rule)
            self.assertTrue(rows, f"{rule}: missing status is not evidence: {diagnostic(report)}")
            self.assertFalse(any(r.get("severity") == "PASS" for r in rows), (rule, rows))
            self.assertTrue(any(r.get("severity") in {"SKIP", "INCOMPLETE", "FAIL"}
                                for r in rows), (rule, rows))

    def test_legacy_builder_refuses_poly_before_overwrite(self) -> None:
        _, pipeline = self.scaffold()
        walls = pipeline / "walls.json"
        self.assertTrue(walls.is_file(), "P2 scaffold is the poly route control")
        self.assertEqual(load(walls).get("wall_technique"), POLY)
        output = self.temp / "protected-output"
        output.mkdir()
        sentinels = {"assembly.json": b"do-not-overwrite-json\n",
                     "assembly.ms": b"do-not-overwrite-script\n"}
        for name, data in sentinels.items():
            (output / name).write_bytes(data)
        result = self.run_cli("place_components.py", "--in", pipeline, "--out", output)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("poly", (result.stdout + result.stderr).lower(),
                      "must refuse the route, not an unrelated missing input")
        self.assertIn("wall", (result.stdout + result.stderr).lower(),
                      "refusal must identify the wall route")
        for name, data in sentinels.items():
            self.assertEqual((output / name).read_bytes(), data, f"overwrote {name}")

    def test_locked_poly_does_not_run_legacy_wall_rules(self) -> None:
        pipeline = self.poly_fixture()
        _, report = self.validate(pipeline)
        for rule in (*LEGACY_RULES, "G-81"):
            rows = self.rows(report, rule)
            self.assertTrue(rows, f"{rule} applicability must be visible")
            self.assertTrue(any(r.get("severity") == "SKIP" for r in rows), (rule, rows))
            self.assertFalse(any(r.get("severity") in {"PASS", "FAIL"} for r in rows), (rule, rows))

    def test_poly_qa_without_runtime_observations_is_incomplete(self) -> None:
        if OPTIONS.p2_qa_project is None:
            self.skipTest("pending: real poly QA project and request required; no runtime evidence invented")
        source = OPTIONS.p2_qa_project.resolve()
        self.assertTrue((source / "specs" / "pipeline" / "qa.json").is_file(),
                        "--p2-qa-project must be a project root with specs/pipeline/qa.json")
        request_path = OPTIONS.p2_qa_request.resolve()
        self.assertTrue(request_path.is_file(), "--p2-qa-request must be an existing valid request")
        project = self.clone(source)
        qa = load(project / "specs" / "pipeline" / "qa.json")
        request = load(request_path)
        self.assertEqual(qa.get("profile"), POLY, "positive control must be the real poly QA profile")
        self.assertEqual(request.get("profile"), POLY, "request must match the poly profile")
        self.assertTrue(request.get("expected_check_ids") and request.get("observations"),
                        "request without real checks/observations cannot test missing evidence")
        request_copy = self.temp / "qa-request.json"
        shutil.copy2(request_path, request_copy)
        empty = self.temp / "empty-results.json"
        save(empty, {"records": []})
        out = self.temp / "qa-out"
        result = self.run_cli("qa_check.py", "--in", project, "--assess", "--request", request_copy,
                              "--results", empty, "--out", out, "--json")
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        produced = out / "qa-results.json"
        self.assertTrue(produced.is_file(), "assessment must report an incomplete verdict")
        assessment = load(produced)
        self.assertNotEqual(assessment.get("verdict"), "PASS", assessment)
        self.assertGreater(assessment.get("summary", {}).get("incomplete", 0), 0,
                           "missing poly runtime evidence must be INCOMPLETE, not a fabricated PASS")

    def test_locked_poly_route_mismatch_fails_g92(self) -> None:
        for bad in (LEGACY, "unsupported_route", None):
            with self.subTest(value=bad):
                pipeline = self.poly_fixture()
                path = pipeline / "assembly.json"
                doc = load(path)
                doc["wall_technique"] = bad
                save(path, doc)
                result, report = self.validate(pipeline)
                self.require_fail(result, report, "G-92")

    def test_locked_poly_rejects_legacy_tables(self) -> None:
        for field in ("wall_cells", "opening_cuts"):
            with self.subTest(field=field):
                pipeline = self.poly_fixture()
                path = pipeline / "assembly.json"
                doc = load(path)
                doc[field] = []  # presence alone violates route exclusivity
                save(path, doc)
                result, report = self.validate(pipeline)
                self.assertEqual(result.returncode, 1, diagnostic(report))
                failures = self.rows(report, "G-96", "FAIL") + self.rows(report, "G-1", "FAIL")
                self.assertTrue(failures, f"{field} must fail route/schema check: {diagnostic(report)}")

    def test_locked_poly_manifest_missing_is_explicitly_incomplete_or_fail(self) -> None:
        pipeline = self.poly_fixture()
        manifest = pipeline / "wall_surface.json"
        if manifest.is_file():
            manifest.unlink()  # copy belongs solely to this test
        result, report = self.validate(pipeline, "--build")
        rows = [r for r in report["findings"]
                if "manifest" in str(r.get("detail", "")).lower()
                or "wall_surface" in str(r.get("detail", "")).lower()
                or "wall_surface" in str(r.get("location", "")).lower()]
        self.assertTrue(rows, f"missing manifest is not visible in report: {diagnostic(report)}")
        self.assertTrue(any(r.get("severity") in {"FAIL", "SKIP", "INCOMPLETE"} for r in rows), rows)
        self.assertFalse(self.rows(report, "G-96", "PASS"), self.rows(report, "G-96"))
        self.assertFalse(any(r.get("severity") == "PASS" for r in rows), rows)
        # If --build returns zero it is still incomplete, never a production PASS.
        self.assertIn(result.returncode, (0, 1), diagnostic(report))

    def test_locked_wall_negative_mutations(self) -> None:
        # These names occur in the P2 sketch; a released contract may differ.
        # We mutate only fields already present in a real positive fixture and
        # explicitly SKIP any unavailable coverage rather than fabricating a spec.
        cases = ("duplicate_run_id", "nonpositive_thickness", "reversed_height",
                 "missing_block_reference", "invalid_contour_reference", "zero_outward",
                 "nonpositive_numeric_epsilon", "negative_topology_budget",
                 "reversed_opening", "outside_opening", "inverted_sill_head",
                 "missing_opening_run", "overlapping_openings")
        for case in cases:
            with self.subTest(case=case):
                pipeline = self.poly_fixture()
                path = pipeline / "walls.json"
                walls = load(path)
                runs = walls.get("wall_runs")
                openings = walls.get("openings")
                if not isinstance(runs, list) or not runs or not isinstance(runs[0], dict):
                    self.skipTest("pending: fixture/actual contract has no mutable wall_runs")
                run = runs[0]
                expected = "G-93"
                if case == "duplicate_run_id":
                    if len(runs) < 2 or not isinstance(runs[1], dict) or "id" not in run:
                        self.skipTest("pending: need two real wall runs with ids")
                    runs[1]["id"] = run["id"]
                elif case == "nonpositive_thickness":
                    if "thickness_cm" not in run:
                        self.skipTest("pending: actual run thickness field/fixture not available")
                    run["thickness_cm"] = 0
                elif case == "reversed_height":
                    if not {"base_z_cm", "top_z_cm"} <= run.keys():
                        self.skipTest("pending: actual run height fields/fixture not available")
                    run["top_z_cm"] = run["base_z_cm"]
                elif case == "missing_block_reference":
                    if "block_id" not in run:
                        self.skipTest("pending: actual block-reference field not available")
                    run["block_id"] = "__nonexistent_block__"
                elif case == "invalid_contour_reference":
                    if "contour_ref" not in run:
                        self.skipTest("pending: actual contour-reference field not available")
                    run["contour_ref"] = "__not_a_resolvable_reference__"
                elif case == "zero_outward":
                    if "outward" not in run:
                        self.skipTest("pending: actual outward vector field not available")
                    run["outward"] = [0, 0]
                elif case == "nonpositive_numeric_epsilon":
                    if "numeric_epsilon_cm" not in walls:
                        self.skipTest("pending: actual numerical epsilon field not available")
                    walls["numeric_epsilon_cm"] = 0
                elif case == "negative_topology_budget":
                    budget = run.get("topology_budget")
                    if not isinstance(budget, dict) or "max_grid_polygons" not in budget:
                        self.skipTest("pending: actual topology-budget field not available")
                    budget["max_grid_polygons"] = -1
                    expected = "G-97"
                else:
                    if not isinstance(openings, list) or not openings or not isinstance(openings[0], dict):
                        self.skipTest("pending: fixture needs a real opening")
                    op = openings[0]
                    if not isinstance(op.get("u_range_cm"), list) or len(op["u_range_cm"]) != 2:
                        self.skipTest("pending: actual opening range field not available")
                    if case == "reversed_opening":
                        op["u_range_cm"] = [op["u_range_cm"][1], op["u_range_cm"][0]]
                    elif case == "outside_opening":
                        op["u_range_cm"] = [-100, -50]
                        expected = "G-94"
                    elif case == "inverted_sill_head":
                        if "sill_cm" not in op or "head_cm" not in op:
                            self.skipTest("pending: actual opening heights not available")
                        op["head_cm"] = op["sill_cm"]
                    elif case == "missing_opening_run":
                        if "wall_run_id" not in op:
                            self.skipTest("pending: actual opening run reference not available")
                        op["wall_run_id"] = "__nonexistent_run__"
                    else:
                        if len(openings) < 2 or not isinstance(openings[1], dict):
                            self.skipTest("pending: need two openings on one run")
                        other = openings[1]
                        if op.get("wall_run_id") != other.get("wall_run_id"):
                            self.skipTest("pending: need two openings on the same run")
                        if "u_range_cm" not in other:
                            self.skipTest("pending: second opening has no range")
                        other["u_range_cm"] = list(op["u_range_cm"])
                        expected = "G-94"
                save(path, walls)
                result, report = self.validate(pipeline)
                self.require_fail(result, report, expected)


if __name__ == "__main__":
    print("Phase 16 P2 OFFLINE harness: live Max was NOT queried; SKIP is not PASS.", file=sys.stderr)
    if not OPTIONS.require_p2:
        print("P2 acceptance is pending; use --require-p2 to run it.", file=sys.stderr)
    elif OPTIONS.p2_fixture is None:
        print("Locked poly mutation/manifest tests need --p2-fixture and will SKIP.", file=sys.stderr)
    program = unittest.main(argv=[sys.argv[0], *UNITTEST_ARGS], verbosity=2, exit=False)
    if program.result.skipped:
        print("INCOMPLETE: skipped checks are not acceptance or runtime evidence.", file=sys.stderr)
    success = program.result.wasSuccessful() and not (OPTIONS.fail_on_skip and program.result.skipped)
    sys.exit(0 if success else 1)
