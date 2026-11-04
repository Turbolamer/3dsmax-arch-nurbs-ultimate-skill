#!/usr/bin/env python3
"""Independent offline P2 contract probes; no validator imports, Max, or installer.

Run from repository root: python -B Audit/test_phase16_validator_independent.py -v
Optional unittest selectors: ... FourHandoff -v, ... StrictJSON -v, etc.
Only temporary copies are mutated. The synthetic locked assembly is a route
echo, NOT builder output. Runtime SKIPs and formula SKIPs are not passes.
Every CLI call runs a frozen, hash-checked copy and monitors the live source.
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

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
WALL_INPUT = ROOT / "specs" / "fixtures" / "poly-shell-input" / "walls.json"
VALIDATOR = ROOT / "scripts" / "validate_specs.py"
DEPENDENCIES = [VALIDATOR, ROOT / "scripts" / "curve_gen.py",
                ROOT / "scripts" / "wall_cell_coverage.py"]
POLY = "poly_surface_shell_v1"
LEGACY = "legacy_cells_v1"
RUNTIME = ("G-95", "G-98", "G-99", "G-100")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    paths = sorted(p for p in EXAMPLES.rglob("*") if p.is_file())
    paths += [WALL_INPUT, *DEPENDENCIES]
    return {str(p.relative_to(ROOT)): digest(p) for p in paths}


START_HASHES = source_hashes()
print("SOURCE_HASHES " + json.dumps(START_HASHES, sort_keys=True), flush=True)
_approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
_parent = str(_approved) if os.name == "nt" and _approved.is_dir() else None
SNAPSHOT_OWNER = tempfile.TemporaryDirectory(prefix="phase16-validator-snapshot-", dir=_parent)
SNAPSHOT = Path(SNAPSHOT_OWNER.name) / "scripts"
SNAPSHOT.mkdir()
for _source in DEPENDENCIES:
    _bytes = _source.read_bytes()
    if hashlib.sha256(_bytes).hexdigest() != START_HASHES[str(_source.relative_to(ROOT))]:
        raise RuntimeError(f"source changed while snapshot was being captured: {_source}")
    (SNAPSHOT / _source.name).write_bytes(_bytes)
SNAPSHOT_VALIDATOR = SNAPSHOT / VALIDATOR.name


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, doc) -> None:
    path.write_bytes((json.dumps(doc, ensure_ascii=False, indent=2, allow_nan=False)
                      + "\n").encode("utf-8"))


class Probe(unittest.TestCase):
    def setUp(self) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        self.owner = tempfile.TemporaryDirectory(prefix="phase16-independent-", dir=parent)
        self.addCleanup(self.owner.cleanup)
        self.root = Path(self.owner.name) / "project"
        self.root.mkdir()
        self.pipeline = self.root / "pipeline"
        shutil.copytree(EXAMPLES, self.pipeline)
        # This is a copy in our owned temporary directory, not an original.
        (self.pipeline / "assembly.ms").unlink(missing_ok=True)
        self.walls = read(WALL_INPUT)
        self.original_assembly = read(self.pipeline / "assembly.json")
        self.assembly = copy.deepcopy(self.original_assembly)
        for key in ("wall_cells", "opening_cuts"):
            self.assembly.pop(key)
            self.assembly["origins"] = {p: v for p, v in self.assembly["origins"].items()
                                        if p != key and not p.startswith(key + "[")}
        self.assembly["wall_technique"] = POLY
        self.assembly["wall_ref"] = "wall_surface.json"
        self.assembly["source"]["reference"] = (
            "components_registry.json and dimensions.json; synthetic test echo, not built")
        self.save("walls", self.walls)
        self.save("assembly", self.assembly)

    def save(self, name: str, doc) -> None:
        write(self.pipeline / (name + ".json"), doc)

    @staticmethod
    def rows(report, rule: str, location: str | None = None):
        return [r for r in report["findings"] if r["rule"] == rule
                and (location is None or location in r["location"])]

    def statuses(self, report, rule: str, location: str | None = None) -> set[str]:
        return {r["severity"] for r in self.rows(report, rule, location)}

    def run_validator(self, label: str, *args: str, selector=None):
        before = {str(p.relative_to(ROOT)): digest(p) for p in DEPENDENCIES}
        expected = {str(p.relative_to(ROOT)): START_HASHES[str(p.relative_to(ROOT))]
                    for p in DEPENDENCIES}
        frozen = {str(p.relative_to(ROOT)): digest(SNAPSHOT / p.name) for p in DEPENDENCIES}
        self.assertEqual(frozen, expected, "frozen source copy changed; abort attribution")
        if before != expected:
            print("WORKSPACE_DIVERGED " + json.dumps({"snapshot": expected, "current": before}), flush=True)
        command = [sys.executable, "-B", str(SNAPSHOT_VALIDATOR),
                   *(selector or ("--dir", str(self.pipeline))), "--json", *args]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                   PYTHONPATH=str(SNAPSHOT.parent))
        result = subprocess.run(command, cwd=self.root, text=True, encoding="utf-8",
                                errors="replace", capture_output=True, timeout=120, env=env)
        after = {str(p.relative_to(ROOT)): digest(p) for p in DEPENDENCIES}
        if before != after:
            print("CODE_CHANGED " + json.dumps({"before": before, "after": after}), flush=True)
        self.assertEqual({str(p.relative_to(ROOT)): digest(SNAPSHOT / p.name) for p in DEPENDENCIES},
                         expected, "frozen source changed during invocation")
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"{label}: invalid CLI JSON, rc={result.returncode}; "
                      f"stdout={result.stdout[:500]!r}; stderr={result.stderr[:500]!r}")
        self.assertEqual(result.returncode, report["exit_code"], label)
        scopes = [("G-7", None), ("G-10", "walls.json"), ("G-31", None),
                  ("G-92", None), ("G-93", "walls.json"), ("G-94", "walls.json"),
                  ("G-96", None), ("G-97", "walls.json")]
        bits = [f"{rule}{'/wall' if loc else ''}=" +
                ",".join(sorted(self.statuses(report, rule, loc)))
                for rule, loc in scopes]
        failures = [f"{r['rule']}@{r['location']}:{r['detail']}"
                    for r in report["findings"] if r["severity"] == "FAIL"]
        preview = failures[:20]
        print(f"PROBE {self.id()} [{label}] rc={result.returncode} " + " ".join(bits) +
              f" failure_count={len(failures)} failures_first20=" +
              json.dumps(preview, ensure_ascii=True), flush=True)
        self.assertFalse([f for f in failures if "internal error" in f.lower()], failures)
        return result, report

    def clean(self, label="clean"):
        result, report = self.run_validator(label)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.statuses(report, "G-93", "walls.json"), {"PASS"})
        self.assertEqual(self.statuses(report, "G-10", "walls.json"), {"PASS"})
        return report

    def no_wall_pass(self, report, reason=""):
        for rule in ("G-10", "G-93"):
            status = self.statuses(report, rule, "walls.json")
            self.assertNotIn("PASS", status, f"{reason}: false {rule} wall PASS: {status}")
            if rule == "G-93":
                self.assertTrue(status & {"FAIL", "SKIP"}, f"{reason}: {rule} missing/incomplete: {status}")

    def acyclic_registry(self):
        """Synthetic cycle repair used ONLY to calibrate directed negatives.

        The historical component claims size -> parameters -> size. Replacing
        the six back edges with the existing tolerance input creates a graph
        control; it does not establish that any formula is correct.
        """
        doc = read(self.pipeline / "components_registry.json")
        for index in (0, 1):
            for key in ("source", "value", "units"):
                path = f"components[0].parameters[{index}].{key}"
                self.assertEqual(doc["origins"][path]["derives_from"], ["components[0].size_cm"])
                doc["origins"][path]["derives_from"] = ["tolerances.linear_cm"]
        self.save("components_registry", doc)

    def direct_failure(self, report, rule, location):
        matching = [r for r in self.rows(report, rule, location) if r["severity"] == "FAIL"]
        other = [r for r in report["findings"] if r["severity"] == "FAIL"]
        self.assertTrue(matching, f"TARGET NOT REACHED {rule}@{location}; other failures={other}")

    def split_run(self, index):
        prefix = f"wall_runs[{index}]"
        del self.walls["origins"][prefix]
        for key in self.walls["wall_runs"][index]:
            if key != "id":
                self.walls["origins"][f"{prefix}.{key}"] = {"origin": "given"}

    def put_wall_path(self, path):
        self.walls["origin_inputs"] = [path]
        self.save("walls", self.walls)


class FourHandoff(Probe):
    def test_four_mutations_have_separate_calibrated_controls(self):
        cases = (
            ("bad_transitive_conflict_crossref", "structure.x_bay_cm"),
            ("registry_bad_derived_path", "components[0].size_cm"),
            ("registry_backward_to_wall", "components[0].size_cm"),
            ("nurbs_superseded_massing", "sections[0].points_cm"),
        )
        for label, source in cases:
            with self.subTest(case=label):
                # Each clean control selects exactly the same source as its mutation.
                for name in ("assumptions", "components_registry", "massing"):
                    shutil.copyfile(EXAMPLES / (name + ".json"), self.pipeline / (name + ".json"))
                self.put_wall_path(source)
                result, report = self.run_validator(label + "_control")
                if label not in ("registry_bad_derived_path", "registry_backward_to_wall"):
                    self.assertEqual(result.returncode, 0)
                    self.assertEqual(self.statuses(report, "G-93", "walls.json"), {"PASS"})
                else:
                    # The original registry is cyclic. Log, rather than claim,
                    # a clean positive and still run each exact mutation.
                    print("HISTORICAL_REGISTRY_CONTROL " + str(result.returncode), flush=True)
                if label == "bad_transitive_conflict_crossref":
                    doc = read(self.pipeline / "assumptions.json")
                    self.assertEqual(doc["cross_references"]["conflict_sourced_paths"][3]["conflict_ref"], "C-003")
                    doc["cross_references"]["conflict_sourced_paths"][3]["conflict_ref"] = "C-999"
                    self.save("assumptions", doc)
                elif label == "registry_bad_derived_path":
                    doc = read(self.pipeline / "components_registry.json")
                    doc["origins"]["components[0].size_cm"]["derives_from"] = ["NO_SUCH_FIELD"]
                    self.save("components_registry", doc)
                elif label == "registry_backward_to_wall":
                    doc = read(self.pipeline / "components_registry.json")
                    doc["origin_inputs"] = ["wall_runs[0].thickness_cm"]
                    self.save("components_registry", doc)
                else:
                    doc = read(self.pipeline / "massing.json")
                    doc["status"] = "superseded"
                    self.save("massing", doc)
                _, report = self.run_validator(label)
                if label == "bad_transitive_conflict_crossref":
                    self.direct_failure(report, "G-31", "assumptions.json")
                if label == "registry_bad_derived_path":
                    self.assertTrue(any("NO_SUCH_FIELD" in r["detail"] and r["severity"] == "FAIL"
                                        for r in self.rows(report, "G-93", "walls.json::origin_inputs")))
                if label == "registry_backward_to_wall":
                    self.assertTrue(any("wall_runs[0].thickness_cm" in r["detail"] and r["severity"] == "FAIL"
                                        for r in self.rows(report, "G-93", "walls.json::origin_inputs")))
                self.no_wall_pass(report, label)

    def test_registry_mutations_against_an_acyclic_control(self):
        self.put_wall_path("components[0].size_cm")
        self.acyclic_registry()
        self.clean("acyclic_registry_control")
        pristine = read(self.pipeline / "components_registry.json")
        for label in ("registry_bad_derived_path_acyclic", "registry_backward_to_wall_acyclic"):
            with self.subTest(case=label):
                doc = copy.deepcopy(pristine)
                if label.startswith("registry_bad"):
                    doc["origins"]["components[0].size_cm"]["derives_from"] = ["NO_SUCH_FIELD"]
                else:
                    doc["origin_inputs"] = ["wall_runs[0].thickness_cm"]
                self.save("components_registry", doc)
                _, report = self.run_validator(label)
                self.direct_failure(report, "G-93", "walls.json::origin_inputs")
                expected = "NO_SUCH_FIELD" if label.startswith("registry_bad") else "wall_runs[0].thickness_cm"
                self.assertTrue(any(expected in r["detail"] for r in self.rows(report, "G-93", "walls.json::origin_inputs")))
                self.no_wall_pass(report, label)


class Ledger(Probe):
    def setup_ledger(self, kind):
        self.split_run(0)
        path = "wall_runs[0].thickness_cm"
        if kind == "assumed":
            doc = read(self.pipeline / "assumptions.json")
            entry = copy.deepcopy(doc["assumptions"][0])
            entry.update(id="A-026", field_path="walls.json:" + path, value=30.0,
                         reason="Synthetic assumed wall thickness", invalidated_by="test brief")
            doc["assumptions"].append(entry)
            name, ref = "assumptions", "A-026"
        else:
            doc = read(self.pipeline / "conflicts_resolved.json")
            entry = copy.deepcopy(doc["conflicts"][0])
            entry["id"] = "C-006"
            entry["resolution"].update(resulting_value_of="walls.json:" + path,
                                       resolved_paths=["walls.json:" + path], chosen_value=30.0)
            doc["conflicts"].append(entry)
            name, ref = "conflicts_resolved", "C-006"
        self.save(name, doc)
        self.walls["origins"][path] = {"origin": kind, "origin_ref": ref}
        self.save("walls", self.walls)
        self.clean(kind + "_ledger_control")
        return name, doc, path

    def test_assumed_owner_path_value_and_unique_id(self):
        name, original, path = self.setup_ledger("assumed")
        wall_original = copy.deepcopy(self.walls)
        for label in ("wrong_existing_id_owner", "wrong_value", "wrong_qualified_path", "duplicate_id"):
            with self.subTest(case=label):
                doc = copy.deepcopy(original)
                self.walls = copy.deepcopy(wall_original)
                if label == "wrong_existing_id_owner":
                    self.walls["origins"][path]["origin_ref"] = "A-001"
                elif label == "wrong_value":
                    doc["assumptions"][-1]["value"] = 31.0
                elif label == "wrong_qualified_path":
                    doc["assumptions"][-1]["field_path"] = "walls.json:wall_runs[1].thickness_cm"
                else:
                    doc["assumptions"].append(copy.deepcopy(doc["assumptions"][-1]))
                self.save(name, doc)
                self.save("walls", self.walls)
                _, report = self.run_validator(label)
                self.direct_failure(report, "G-10", "walls.json")
                self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))

    def test_conflict_owner_path_value_and_coverage(self):
        name, original, path = self.setup_ledger("conflict")
        wall_original = copy.deepcopy(self.walls)
        for label in ("wrong_existing_conflict_owner", "wrong_chosen_value", "wrong_primary", "wrong_claim"):
            with self.subTest(case=label):
                doc = copy.deepcopy(original)
                self.walls = copy.deepcopy(wall_original)
                resolution = doc["conflicts"][-1]["resolution"]
                if label == "wrong_existing_conflict_owner":
                    self.walls["origins"][path]["origin_ref"] = "C-001"
                elif label == "wrong_chosen_value":
                    resolution["chosen_value"] = 31.0
                elif label == "wrong_primary":
                    resolution["resulting_value_of"] = "walls.json:wall_runs[1].thickness_cm"
                else:
                    resolution["resolved_paths"] = ["walls.json:wall_runs[1].thickness_cm"]
                self.save(name, doc)
                self.save("walls", self.walls)
                _, report = self.run_validator(label)
                self.direct_failure(report, "G-10", "walls.json")
                self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))

    def test_derived_conflict_annotation_matches_its_actual_input(self):
        # C-006 is a properly bound wall conflict. The derived second thickness
        # has the same value and explicitly cites that local conflict input.
        _, _, conflict_source = self.setup_ledger("conflict")
        self.split_run(1)
        derived = "wall_runs[1].thickness_cm"
        self.walls["origins"][derived] = {"origin": "derived", "derives_from": [conflict_source],
                                          "conflict_ref": "C-006"}
        self.save("walls", self.walls)
        result, report = self.run_validator("derived_conflict_annotation_control")
        self.assertEqual(result.returncode, 0)
        control_status = self.statuses(report, "G-93", "walls.json")
        self.assertTrue(control_status == {"PASS"} or control_status == {"SKIP"}, control_status)
        if control_status == {"SKIP"}:
            print("INCOMPLETE: even matching annotation linkage remains SKIP", flush=True)
        self.assertEqual(self.statuses(report, "G-32", "walls.json"), {"SKIP"})
        # C-001 exists and is valid but does not resolve the derived input.
        self.walls["origins"][derived]["conflict_ref"] = "C-001"
        self.save("walls", self.walls)
        _, report = self.run_validator("derived_conflict_unrelated_annotation")
        self.assertNotIn("PASS", self.statuses(report, "G-10", "walls.json"),
                         "existing but unrelated conflict_ref claimed as checked")
        self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))


class DirectedGraph(Probe):
    def test_acyclic_three_hop_and_cycles(self):
        self.split_run(0)
        self.split_run(1)
        a, b, c = ("wall_runs[0].thickness_cm", "wall_runs[1].thickness_cm", "upper_returns[0]")
        self.walls["origins"][a] = {"origin": "derived", "derives_from": [b]}
        self.walls["origins"][b] = {"origin": "derived", "derives_from": [c + ".thickness_cm"]}
        self.save("walls", self.walls)
        report = self.clean("directed_acyclic_chain")
        self.assertEqual(self.statuses(report, "G-32", "walls.json"), {"SKIP"})
        base = copy.deepcopy(self.walls)
        for label in ("self", "two_node", "three_node", "element_descendant_self"):
            with self.subTest(case=label):
                self.walls = copy.deepcopy(base)
                if label == "self":
                    self.walls["origins"][a]["derives_from"] = [a]
                elif label == "two_node":
                    self.walls["origins"][b]["derives_from"] = [a]
                elif label == "three_node":
                    self.walls["origins"][c] = {"origin": "derived", "derives_from": [a]}
                else:
                    self.walls["origins"][c] = {"origin": "derived", "derives_from": [c + ".thickness_cm"]}
                self.save("walls", self.walls)
                _, report = self.run_validator(label)
                self.direct_failure(report, "G-10", "walls.json")
                self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))

    def test_bad_sources_metadata_and_missing_local_coverage(self):
        self.split_run(0)
        path = "wall_runs[0].thickness_cm"
        self.walls["origins"][path] = {"origin": "derived", "derives_from": ["wall_runs[1].thickness_cm"]}
        self.save("walls", self.walls)
        self.clean("local_derived_control")
        base = copy.deepcopy(self.walls)
        for source in ("NO_SUCH_FIELD", "wall_runs[1]..thickness_cm", "source.kind", "defaults.foo"):
            with self.subTest(source=source):
                self.walls = copy.deepcopy(base)
                self.walls["origins"][path]["derives_from"] = [source]
                self.save("walls", self.walls)
                _, report = self.run_validator("bad_derived_" + source)
                self.direct_failure(report, "G-10", "walls.json::" + path)
                self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))

    def test_transitive_nurbs_to_massing_draft(self):
        self.put_wall_path("sections[0].points_cm")
        self.clean("nurbs_locked_control")
        doc = read(self.pipeline / "massing.json")
        doc["status"] = "draft"
        self.save("massing", doc)
        _, report = self.run_validator("nurbs_transitive_massing_draft")
        self.no_wall_pass(report, "transitive draft")


class Ambiguity(Probe):
    def test_owner_mapping_rejects_local_only_unknown_and_malformed(self):
        self.put_wall_path("facades[0].id")
        self.clean("upstream_owner_control")
        for path in ("wall_runs[0].thickness_cm", "defaults.panel_thickness_cm", "facades[0]..id",
                     "dimensions.json:facades[0]", "facades[-1].id"):
            with self.subTest(path=path):
                self.put_wall_path(path)
                _, report = self.run_validator("bad_origin_input_" + path)
                self.direct_failure(report, "G-93", "walls.json::origin_inputs")

    def test_duplicate_owner_never_resolves_first_copy(self):
        self.put_wall_path("components[0].size_cm")
        self.acyclic_registry()
        self.clean("unique_registry_control")
        shutil.copyfile(self.pipeline / "components_registry.json", self.root / "components_registry.json")
        _, report = self.run_validator("duplicate_registry_owner", selector=("--dir", str(self.root)))
        self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))
        self.assertTrue(self.statuses(report, "G-93", "walls.json") & {"FAIL", "SKIP"})


class StrictJSON(Probe):
    def test_route_and_nested_duplicate_keys(self):
        self.clean("strict_wall_control")
        path = self.pipeline / "walls.json"
        original = path.read_text(encoding="utf-8")
        for old, replacement in ((f'"wall_technique": "{POLY}"',
                                  f'"wall_technique": "{LEGACY}", "wall_technique": "{POLY}"'),
                                 ('"max_grid_polygons": 64', '"max_grid_polygons": -1, "max_grid_polygons": 64')):
            with self.subTest(needle=old):
                self.assertIn(old, original)
                path.write_text(original.replace(old, replacement, 1), encoding="utf-8", newline="\n")
                _, report = self.run_validator("duplicate_" + old)
                self.direct_failure(report, "G-7", "walls.json")
                self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))

    def test_duplicate_ledger_and_dimension_keys_are_not_silent(self):
        # Duplicate JSON names are RFC 8259 SHOULD-unique, not its MUST; independently
        # test whether these provenance-bearing files are handled unambiguously.
        self.clean("duplicate_source_control")
        for name in ("assumptions", "dimensions", "conflicts_resolved"):
            with self.subTest(source=name):
                path = self.pipeline / (name + ".json")
                original = path.read_text(encoding="utf-8")
                needle = '"status": "locked"'
                self.assertEqual(original.count(needle), 1)
                path.write_bytes(original.replace(needle, '"status": "superseded", ' + needle, 1).encode("utf-8"))
                try:
                    _, report = self.run_validator("duplicate_status_" + name)
                    # Demand source G-7 itself, not a coincidental cross-file failure.
                    self.direct_failure(report, "G-7", name + ".json")
                finally:
                    path.write_bytes(original.encode("utf-8"))

    def test_overflow_nonstandard_constant_and_invalid_syntax(self):
        self.clean("numeric_json_control")
        path = self.pipeline / "walls.json"
        original = path.read_text(encoding="utf-8")
        needle = '"numeric_epsilon_cm": 0.001'
        self.assertEqual(original.count(needle), 1)
        for token in ("1e999", "-1e999", "NaN", "Infinity", "1.0,}"):
            with self.subTest(token=token):
                text = original.replace(needle, '"numeric_epsilon_cm": ' + token, 1)
                path.write_bytes(text.encode("utf-8"))
                _, report = self.run_validator("invalid_number_" + token)
                self.direct_failure(report, "G-7", "walls.json")
                self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))

    def test_unreferenced_ledger_float_overflow(self):
        self.clean("finite_ledger_control")
        path = self.pipeline / "assumptions.json"
        original = path.read_text(encoding="utf-8")
        needle = '"value": 15.0'
        self.assertEqual(original.count(needle), 1)
        path.write_bytes(original.replace(needle, '"value": 1e999', 1).encode("utf-8"))
        _, report = self.run_validator("unreferenced_ledger_overflow")
        self.direct_failure(report, "G-7", "assumptions.json")

    def test_out_of_range_integer_must_not_crash(self):
        self.clean("huge_integer_control")
        path = self.pipeline / "walls.json"
        original = path.read_text(encoding="utf-8")
        # Still under CPython's 4300 digit parsing limit but over float range.
        needle = '"thickness_cm": 30.0'
        self.assertIn(needle, original)
        path.write_bytes(original.replace(needle, '"thickness_cm": ' + "9" * 400, 1).encode("utf-8"))
        _, report = self.run_validator("huge_thickness_integer")
        self.assertTrue(any(r["severity"] == "FAIL" and r["rule"] in ("G-7", "G-93")
                            and "walls.json" in r["location"] for r in report["findings"]))
        self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))


class NumericAndPartial(Probe):
    def test_epsilon_boundaries_and_boolean(self):
        for key, maximum in (("numeric_epsilon_cm", 0.01), ("numeric_unit_epsilon", 0.001)):
            with self.subTest(key=key, control="boundary"):
                original = self.walls[key]
                self.walls[key] = maximum
                self.save("walls", self.walls)
                self.clean(key + "_boundary_control")
                # 10000.0 is enormous vs the wall bound but remains within the
                # loader's exact-integer ceiling; it targets G-93, not G-7.
                for value in (0, -1, True, maximum * 1.0001, 10000.0):
                    with self.subTest(value=value):
                        self.walls[key] = value
                        self.save("walls", self.walls)
                        _, report = self.run_validator(key + "_bad_" + str(value))
                        self.direct_failure(report, "G-93", "walls.json::" + key)
                        self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))
                self.walls[key] = original
                self.save("walls", self.walls)

    def test_extreme_finite_epsilon_rejection_records_parser_masking(self):
        self.clean("extreme_epsilon_control")
        for key in ("numeric_epsilon_cm", "numeric_unit_epsilon"):
            with self.subTest(key=key):
                old = self.walls[key]
                self.walls[key] = 1e100
                self.save("walls", self.walls)
                result, report = self.run_validator("extreme_" + key)
                self.assertEqual(result.returncode, 1)
                g93 = self.statuses(report, "G-93", "walls.json::" + key)
                g7 = self.statuses(report, "G-7", "walls.json")
                self.assertTrue("FAIL" in g93 or "FAIL" in g7, (g93, g7))
                if "FAIL" not in g93:
                    print("MASKED G-93 " + key + ": G-7 rejected the finite 1e100 before domain check", flush=True)
                self.walls[key] = old
                self.save("walls", self.walls)

    def test_partial_draft_zero_vector_and_budget_scope(self):
        self.walls["status"] = "draft"
        self.walls["numeric_unit_epsilon"] = None
        self.save("walls", self.walls)
        _, control = self.run_validator("partial_draft_control")
        self.assertEqual(self.statuses(control, "G-93", "walls.json"), {"SKIP"})
        self.walls["wall_runs"][0]["outward"] = [0, 0]
        self.save("walls", self.walls)
        _, report = self.run_validator("partial_draft_zero_vector")
        self.direct_failure(report, "G-93", "walls.json::wall_runs[0].outward")
        self.walls["wall_runs"][0]["outward"] = [0, -1]
        self.walls["wall_runs"].append(None)
        self.save("walls", self.walls)
        _, report = self.run_validator("partial_draft_malformed_run")
        self.direct_failure(report, "G-93", "walls.json::wall_runs[2]")
        self.assertNotIn("PASS", self.statuses(report, "G-97", "walls.json"))
        self.assertTrue(self.statuses(report, "G-97", "walls.json") & {"FAIL", "SKIP"})

    def test_envelope_fail_blocks_wall_pass_and_unit_vector_edge(self):
        self.clean("units_control")
        self.walls["units"]["length"] = "mm"
        self.save("walls", self.walls)
        _, report = self.run_validator("wall_wrong_units")
        self.direct_failure(report, "G-5", "walls.json")
        self.assertNotIn("PASS", self.statuses(report, "G-93", "walls.json"))
        self.walls["units"]["length"] = "cm"
        self.walls["wall_runs"][0]["outward"] = [1, 0]
        self.save("walls", self.walls)
        _, report = self.run_validator("parallel_normal")
        self.direct_failure(report, "G-93", "walls.json::wall_runs[0].outward")
        self.walls["wall_runs"][0]["outward"] = [0, 1]
        self.save("walls", self.walls)
        self.clean("opposite_sign_static_only_not_physical_proof")


class RoutingCLI(Probe):
    def test_runtime_is_skip_and_synthetic_echo_is_not_output(self):
        report = self.clean("synthetic_echo_control")
        for rule in RUNTIME:
            self.assertEqual(self.statuses(report, rule), {"SKIP"}, (rule, self.rows(report, rule)))
        self.assertEqual(self.statuses(report, "G-96"), {"SKIP"})
        self.assertFalse((self.pipeline / "wall_surface.json").exists())
        self.assertFalse((self.pipeline / "wall_surface.ms").exists())

    def test_historical_implicit_route_unchanged(self):
        (self.pipeline / "walls.json").unlink()
        self.save("assembly", self.original_assembly)
        result, report = self.run_validator("historical_no_selector_control")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.statuses(report, "G-92"), {"PASS"})
        for rule in RUNTIME:
            self.assertEqual(self.statuses(report, rule), {"SKIP"})

    def test_draft_and_warnings_exit_policy(self):
        self.walls["status"] = "draft"
        self.save("walls", self.walls)
        result, report = self.run_validator("draft_lint_control")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.statuses(report, "G-93", "walls.json"), {"SKIP"})
        for extra in (("--build",), ("--warnings-as-errors",)):
            with self.subTest(mode=extra):
                result, report = self.run_validator("draft_" + extra[0], *extra)
                self.assertEqual(result.returncode, 1)
                self.direct_failure(report, "G-4", "walls.json")

    def test_mismatched_selector_missing_echo_and_mixed_arrays(self):
        self.clean("route_control")
        baseline = copy.deepcopy(self.assembly)
        for label in ("unknown_selector", "conflicting_echo", "missing_echo", "mixed_empty_cells", "orphan_wall_ref"):
            with self.subTest(case=label):
                self.assembly = copy.deepcopy(baseline)
                self.walls = read(WALL_INPUT)
                if label == "unknown_selector":
                    self.walls["wall_technique"] = "unknown"
                elif label == "conflicting_echo":
                    self.assembly["wall_technique"] = LEGACY
                elif label == "missing_echo":
                    del self.assembly["wall_technique"]
                elif label == "mixed_empty_cells":
                    self.assembly["wall_cells"] = []
                else:
                    (self.pipeline / "walls.json").unlink()
                if label != "orphan_wall_ref":
                    self.save("walls", self.walls)
                self.save("assembly", self.assembly)
                _, report = self.run_validator(label)
                gate = "G-96" if label == "mixed_empty_cells" else "G-92"
                self.direct_failure(report, gate, "assembly.json")
                self.assertNotIn("PASS", self.statuses(report, gate))

    def test_duplicate_route_file_detected_by_dir_and_file(self):
        for selector in (("--dir", str(self.root)), ("--file", str(self.pipeline / "walls.json"))):
            with self.subTest(selector=selector[0]):
                result, report = self.run_validator("route_scope_control", selector=selector)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(self.statuses(report, "G-92"), {"PASS"})
        shutil.copyfile(self.pipeline / "walls.json", self.root / "walls.json")
        for selector in (("--dir", str(self.root)), ("--file", str(self.pipeline / "walls.json"))):
            with self.subTest(duplicate=selector[0]):
                _, report = self.run_validator("duplicate_route_scope", selector=selector)
                self.direct_failure(report, "G-92", "assembly.json")
                self.assertNotIn("PASS", self.statuses(report, "G-92"))

    def test_filtered_json_exit_code_includes_hidden_failure(self):
        self.clean("filtered_control")
        self.walls["wall_runs"][0]["thickness_cm"] = 0
        self.save("walls", self.walls)
        full_result, full = self.run_validator("unfiltered_bad_wall")
        self.direct_failure(full, "G-93", "walls.json::wall_runs[0].thickness_cm")
        filtered_result, filtered = self.run_validator("filtered_g92", "--rule", "G-92")
        self.assertEqual(full_result.returncode, filtered_result.returncode)
        self.assertEqual(filtered_result.returncode, 1)
        self.assertTrue(all(r["rule"] == "G-92" for r in filtered["findings"]))
        self.assertEqual(self.rows(full, "G-92"), self.rows(filtered, "G-92"))
        self.assertEqual(filtered["exit_code"], 1)

    def test_route_symlink_rejected_if_available(self):
        self.clean("route_regular_file_control")
        # A single live symlink tests the symlink rule itself; a duplicate route
        # could reject for ambiguity even if symlinks were improperly followed.
        external = self.root.parent / "wall-input.json"
        shutil.copyfile(self.pipeline / "walls.json", external)
        link = self.pipeline / "walls.json"
        link.unlink()
        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"host cannot create symlinks: {exc}")
        _, report = self.run_validator("route_symlink")
        self.direct_failure(report, "G-92", "assembly.json")
        self.direct_failure(report, "G-7", "walls.json")


def main():
    program = None
    try:
        program = unittest.main(verbosity=2, exit=False)
    finally:
        final = source_hashes()
        changed = {name: {"before": value, "after": final.get(name)}
                   for name, value in START_HASHES.items() if final.get(name) != value}
        changed.update({name: {"before": None, "after": value}
                        for name, value in final.items() if name not in START_HASHES})
        print("SOURCE_HASH_CHANGES " + json.dumps(changed, sort_keys=True), flush=True)
        if changed:
            print("WARNING: sources/fixtures changed; results apply only to frozen source snapshot, "
                  "not current workspace; re-run after edits settle", flush=True)
        SNAPSHOT_OWNER.cleanup()
    if changed or program is None or not program.result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
