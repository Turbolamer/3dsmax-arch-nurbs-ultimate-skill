#!/usr/bin/env python3
"""Independent CLI-only Phase 16 P2 review, 2026-11-02d.

All mutations are disposable; no validator/test imports and no builder/Max calls.
The locked wall is synthetic INPUT; assembly is an EMPTY DRAFT, never output.
Run: python -B Audit/test_phase16_validator_review_d.py -v
Unittest selectors are supported. Source drift makes the process exit 2 even
when the frozen-snapshot assertions succeeded. No expected failures or skips.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = tuple(ROOT / "scripts" / name for name in
                ("validate_specs.py", "wall_cell_coverage.py", "curve_gen.py"))
WALL = ROOT / "specs/fixtures/poly-shell-input/walls.json"
FIXTURES = tuple(sorted(p for p in (ROOT / "examples").rglob("*") if p.is_file())) + (WALL,)
CAPTURE = {p: p.read_bytes() for p in (*SOURCES, *FIXTURES)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hashes():
    return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in CAPTURE}


INITIAL = {str(p.relative_to(ROOT)): sha(data) for p, data in CAPTURE.items()}
APPROVED = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/opencode"
PARENT = str(APPROVED) if os.name == "nt" and APPROVED.is_dir() else None
OWNER = tempfile.TemporaryDirectory(prefix="phase16-validator-review-d-", dir=PARENT)
TEMP = Path(OWNER.name)
SCRIPTS = TEMP / "scripts"
SCRIPTS.mkdir()
for source in SOURCES:
    (SCRIPTS / source.name).write_bytes(CAPTURE[source])
OBSERVED_DRIFT = {}
CLI_COUNT = 0


def write(path, doc):
    path.write_bytes((json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode())


def read(path):
    return json.loads(path.read_bytes())


def rows(report, rule, location=""):
    return [r for r in report["findings"] if r["rule"] == rule and location in r["location"]]


def statuses(report, rule, location=""):
    return {r["severity"] for r in rows(report, rule, location)}


class Review(unittest.TestCase):
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="case-", dir=TEMP)
        self.addCleanup(self.owner.cleanup)
        self.project = Path(self.owner.name)
        self.pipeline = self.project / "pipeline"
        self.pipeline.mkdir()
        for path in FIXTURES[:-1]:
            dst = self.pipeline / path.relative_to(ROOT / "examples")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(CAPTURE[path])
        (self.pipeline / "assembly.ms").unlink(missing_ok=True)
        self.wall = json.loads(CAPTURE[WALL])
        example = self.doc("assembly")
        draft = {key: copy.deepcopy(example[key]) for key in
                 ("schema_version", "spec", "project", "units")}
        draft.update(source={"kind": "derived", "reference":
                             "components_registry.json; synthetic empty draft, NOT produced output",
                             "recorded_at": "2026-11-02T00:00:00Z"}, status="draft",
                     tolerances=copy.deepcopy(example["tolerances"]),
                     origin_inputs=[], origins={}, defaults={}, layer_map={},
                     placements=[], opening_cuts=[], wall_cells=[], scatter=[])
        self.save("assembly", draft)
        self.save_wall()

    def doc(self, name):
        return read(self.pipeline / (name + ".json"))

    def save(self, name, doc):
        write(self.pipeline / (name + ".json"), doc)

    def save_wall(self):
        self.save("walls", self.wall)

    def run_cli(self, label, *extra, mode="dir", path=None):
        global CLI_COUNT
        CLI_COUNT += 1
        for source in SOURCES:
            self.assertEqual(sha((SCRIPTS / source.name).read_bytes()), sha(CAPTURE[source]))
        changed = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in SOURCES
                   if p.read_bytes() != CAPTURE[p]}
        OBSERVED_DRIFT.update(changed)
        selection = ("--file", str(path or self.pipeline / "walls.json")) if mode == "file" else (
                     "--dir", str(path or self.pipeline))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        env.pop("PYTHONPATH", None)
        process = subprocess.run([sys.executable, "-B", str(SCRIPTS / "validate_specs.py"),
                                  *selection, "--json", *extra], cwd=TEMP, env=env,
                                 text=True, encoding="utf-8", errors="replace",
                                 capture_output=True, timeout=90)
        self.assertFalse(process.stderr, f"{label}: stderr={process.stderr[:1000]}")
        try:
            report = json.loads(process.stdout)
        except ValueError:
            self.fail(f"{label}: rc={process.returncode}, non-JSON stdout {process.stdout[:1000]!r}")
        self.assertEqual(process.returncode, report["exit_code"], label)
        self.assertIn(process.returncode, (0, 1), label)
        failures = [r for r in report["findings"] if r["severity"] == "FAIL"]
        scopes = (("G-7", ""), ("G-8", ""), ("G-10", "walls.json"), ("G-31", ""),
                  ("G-32", "walls.json"), ("G-82", ""), ("G-92", ""),
                  ("G-93", "walls.json"), ("G-94", "walls.json"), ("G-97", "walls.json"))
        print("PROBE " + label + " " + json.dumps({
            "exit": process.returncode,
            "status": {gate + ("/wall" if where else ""): sorted(statuses(report, gate, where))
                       for gate, where in scopes},
            "fail_count": len(failures),
            "first_failures": [{**r, "detail": r["detail"][:500]} for r in failures[:4]],
        }, ensure_ascii=True), flush=True)
        self.assertFalse([r for r in report["findings"] if "internal error" in r["detail"].lower()],
                         f"{label}: internal error instead of a calibrated refusal")
        return report

    def positive(self, label, **kwargs):
        report = self.run_cli(label, **kwargs)
        self.assertEqual(report["exit_code"], 0, report["summary"])
        self.assertFalse([r for r in report["findings"] if r["severity"] == "FAIL"])
        for gate in ("G-10", "G-93"):
            self.assertEqual(statuses(report, gate, "walls.json"), {"PASS"})
        for gate in ("G-95", "G-96", "G-98", "G-99", "G-100"):
            self.assertEqual(statuses(report, gate), {"SKIP"}, (gate, rows(report, gate)))
        for name in ("wall_surface.json", "wall_surface.ms"):
            self.assertFalse((self.pipeline / name).exists())
        return report

    def fail_at(self, report, rule, location, detail=""):
        matches = [r for r in rows(report, rule, location)
                   if r["severity"] == "FAIL" and detail in r["detail"]]
        self.assertTrue(matches, f"TARGET NOT REACHED {rule}@{location} containing {detail!r}")

    def blocked(self, label, detail="", rule="G-93", where="walls.json::origin_inputs", **kwargs):
        report = self.run_cli(label, **kwargs)
        self.assertEqual(report["exit_code"], 1)
        self.fail_at(report, rule, where, detail)
        for gate in ("G-10", "G-93"):
            self.assertNotIn("PASS", statuses(report, gate, "walls.json"), (label, gate))
        return report

    def select(self, path, registry=False):
        self.wall["origin_inputs"] = [path]
        self.save_wall()
        if registry:
            # Synthetic graph calibration, not formula or production evidence.
            # Replace size->parameters->size with actual size inputs; split the
            # historical partial opening conflict before traversing the panel.
            registry_doc = self.doc("components_registry")
            panel = self.doc("facade_grids")["panels"][71]
            self.assertEqual(registry_doc["components"][0]["size_cm"],
                             [panel["width_cm"], panel["height_cm"],
                              registry_doc["defaults"]["panel_thickness_cm"]])
            registry_doc["origins"]["components[0].size_cm"]["derives_from"] = [
                "panels[71].width_cm", "panels[71].height_cm", "defaults.panel_thickness_cm"]
            dimensions = self.doc("dimensions")
            original = dimensions["origins"].pop("openings[11]")
            self.assertEqual(original, {"origin": "conflict", "origin_ref": "C-002"})
            for key in dimensions["openings"][11]:
                if key != "id":
                    dimensions["origins"][f"openings[11].{key}"] = (
                        original if key == "head_cm" else {"origin": "given"})
            self.save("dimensions", dimensions)
            self.save("components_registry", registry_doc)

    def split_run(self, index):
        prefix = f"wall_runs[{index}]"
        self.wall["origins"].pop(prefix)
        for key in self.wall["wall_runs"][index]:
            if key != "id":
                self.wall["origins"][prefix + "." + key] = {"origin": "given"}


class FourTransitiveControls(Review):
    def test_bad_transitive_ledger(self):
        self.select("structure.x_bay_cm")
        self.positive("transitive-ledger/control")
        ledger = self.doc("assumptions")
        edge = ledger["cross_references"]["conflict_sourced_paths"][3]
        self.assertEqual(edge["conflict_ref"], "C-003")
        edge["conflict_ref"] = "C-999"
        self.save("assumptions", ledger)
        report = self.blocked("transitive-ledger/C-999", "structure.x_bay_cm")
        self.fail_at(report, "G-31", "assumptions.json::cross_references")

    def test_registry_bad_path_with_acyclic_positive(self):
        self.select("components[0].size_cm", registry=True)
        self.positive("registry-path/acyclic-control")
        doc = self.doc("components_registry")
        doc["origins"]["components[0].size_cm"]["derives_from"] = ["NO_SUCH_FIELD"]
        self.save("components_registry", doc)
        for mode in ("dir", "file"):
            with self.subTest(mode=mode):
                report = self.blocked("registry-path/" + mode, "NO_SUCH_FIELD", mode=mode)
                self.assertNotIn("FAIL", statuses(report, "G-31"), "unrelated G-31 masking")

    def test_registry_backward_reference_with_acyclic_positive(self):
        self.select("components[0].size_cm", registry=True)
        self.positive("registry-backward/acyclic-control")
        doc = self.doc("components_registry")
        doc["origin_inputs"] = ["wall_runs[0].thickness_cm"]
        self.save("components_registry", doc)
        report = self.blocked("registry-backward/wall", "wall_runs[0].thickness_cm")
        self.assertNotIn("FAIL", statuses(report, "G-31"), "unrelated G-31 masking")

    def test_superseded_massing_behind_nurbs(self):
        self.select("sections[0].points_cm")
        self.positive("nurbs-massing/locked-control")
        doc = self.doc("massing")
        for status in ("superseded", "draft"):
            with self.subTest(status=status):
                doc["status"] = status
                self.save("massing", doc)
                self.blocked("nurbs-massing/" + status, "elements[8].z_range_cm")


class ProvenanceScope(Review):
    def test_known_formula_must_bind_its_declared_inputs(self):
        self.select("building.total_height_cm")
        doc = self.doc("dimensions")
        # Remove the OPTIONAL annotation from BOTH controls so its own conflict
        # predicate cannot mask the independent declared-formula dependency gate.
        doc["origins"]["building.total_height_cm"].pop("conflict_ref")
        self.save("dimensions", doc)
        self.positive("formula-inputs/actual-height-input-control")
        doc["origins"]["building.total_height_cm"]["derives_from"] = ["site.ground_level_cm"]
        self.save("dimensions", doc)
        report = self.run_cli("formula-inputs/unrelated-ground-level")
        target = rows(report, "G-32", "dimensions.json::building.total_height_cm")
        self.assertTrue(any(r["severity"] in ("FAIL", "SKIP") for r in target),
                        "G-32 did not expose unrelated declared inputs for its known formula")
        self.assertFalse(any(r["severity"] == "PASS" for r in target))
        self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"),
                         "wall credited a source whose declared inputs do not bind its formula")

    def test_used_upstream_unknown_formula_is_incomplete_not_wall_pass(self):
        self.select("site.ground_level_cm")
        self.positive("upstream-unknown-formula/given-control")
        doc = self.doc("dimensions")
        self.assertEqual(doc["origins"]["site.ground_level_cm"], {"origin": "given"})
        doc["origins"]["site.ground_level_cm"] = {
            "origin": "derived", "derives_from": ["site.footprint_width_cm"]}
        self.save("dimensions", doc)
        report = self.run_cli("upstream-unknown-formula/derived-ground-level")
        self.assertEqual(statuses(report, "G-32", "dimensions.json::site.ground_level_cm"), {"SKIP"})
        for gate in ("G-10", "G-93"):
            self.assertNotIn("PASS", statuses(report, gate, "walls.json"),
                             "wall credited an upstream derived value with no checked formula")

    def test_known_upstream_formula_failure_blocks_wall_pass(self):
        self.select("building.total_height_cm")
        control = self.positive("known-formula/height-control")
        self.assertIn("PASS", statuses(control, "G-32", "dimensions.json"))
        doc = self.doc("dimensions")
        doc["building"]["total_height_cm"] += 5
        self.save("dimensions", doc)
        report = self.blocked("known-formula/incorrect-height", "building.total_height_cm")
        self.fail_at(report, "G-32", "dimensions.json::building.total_height_cm", "recomputes")

    def test_upstream_conflict_annotation_binding(self):
        self.select("building.total_height_cm")
        self.positive("conflict-annotation/C-001-control")
        dimensions = self.doc("dimensions")
        origin = dimensions["origins"]["building.total_height_cm"]
        self.assertEqual(origin["conflict_ref"], "C-001")
        origin["conflict_ref"] = "C-004"
        self.save("dimensions", dimensions)
        report = self.blocked("conflict-annotation/unrelated-C-004", "conflict_ref C-004 is not bound")
        self.assertEqual({r["rule"] for r in report["findings"] if r["severity"] == "FAIL"}, {"G-93"})

    def test_non_derived_upstream_annotation_is_not_claimed_as_bound(self):
        self.select("roof.deck_thickness_cm")
        self.positive("given-annotation/upstream-control")
        doc = self.doc("dimensions")
        self.assertEqual(doc["origins"]["roof.deck_thickness_cm"], {"origin": "given"})
        doc["origins"]["roof.deck_thickness_cm"]["conflict_ref"] = "C-001"
        self.save("dimensions", doc)
        report = self.run_cli("given-annotation/upstream-unrelated-C-001")
        # The optional annotation describes conflict-resolved derived inputs.
        # An annotation on a given value has no such input linkage to verify;
        # reject it or be explicitly incomplete, not a checked binding PASS.
        self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"),
                         "unrelated conflict_ref on a given upstream input was claimed as checked")

    def test_non_derived_wall_annotation_is_not_claimed_as_bound(self):
        self.positive("given-annotation/wall-control")
        self.wall["origins"]["wall_runs[0]"]["conflict_ref"] = "C-001"
        self.save_wall()
        report = self.run_cli("given-annotation/wall-unrelated-C-001")
        self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"),
                         "unrelated conflict_ref on a given wall value was claimed as checked")

    def test_existing_wrong_upstream_conflict_owner(self):
        self.select("structure.x_bay_cm")
        self.positive("conflict-owner/C-003-control")
        dimensions = self.doc("dimensions")
        dimensions["origins"]["structure.x_bay_cm"]["origin_ref"] = "C-004"
        self.save("dimensions", dimensions)
        report = self.blocked("conflict-owner/C-004", "C-004 does not cover dimensions.json::structure.x_bay_cm")
        self.assertEqual({r["rule"] for r in report["findings"] if r["severity"] == "FAIL"}, {"G-93"})

    def test_existing_wrong_registry_assumption_owner(self):
        self.select("components[0].size_cm", registry=True)
        self.positive("registry-assumption/A-023-control")
        doc = self.doc("components_registry")
        doc["origins"]["defaults.panel_thickness_cm"]["origin_ref"] = "A-024"
        self.save("components_registry", doc)
        report = self.blocked("registry-assumption/A-024", "A-024 does not cover")
        self.assertEqual({r["rule"] for r in report["findings"] if r["severity"] == "FAIL"}, {"G-93"})

    def test_used_ledger_value_mismatch(self):
        self.select("components[0].size_cm", registry=True)
        self.positive("registry-ledger-value/control")
        ledger = self.doc("assumptions")
        next(a for a in ledger["assumptions"] if a["id"] == "A-023")["value"] += 1
        self.save("assumptions", ledger)
        report = self.blocked("registry-ledger-value/mismatch", "components[0].size_cm")
        self.fail_at(report, "G-12", "assumptions.json")

    def test_local_cycle_and_unknown_formula_scope(self):
        self.split_run(0)
        key = "wall_runs[0].thickness_cm"
        self.wall["origins"][key] = {"origin": "derived", "derives_from": ["wall_runs[1].thickness_cm"]}
        self.save_wall()
        self.positive("local-derived/control")
        # Deliberately change a valid positive thickness without changing its
        # declared input: dependency validity is not formula recomputation.
        self.wall["wall_runs"][0]["thickness_cm"] = 31
        self.save_wall()
        report = self.positive("local-derived/no-formula-not-value-proof")
        self.assertEqual(statuses(report, "G-32", "walls.json::" + key), {"SKIP"})
        self.assertNotIn("PASS", statuses(report, "G-32", "walls.json"))
        self.wall["origins"][key]["derives_from"] = [key]
        self.save_wall()
        self.blocked("local-derived/self-cycle", "cyclic", rule="G-10", where="walls.json")

    def test_wall_optional_annotation_is_unverified_not_false_pass(self):
        self.select("building.total_height_cm")
        self.split_run(0)
        key = "wall_runs[0].thickness_cm"
        self.wall["origins"][key] = {"origin": "derived", "derives_from": ["building.total_height_cm"]}
        self.save_wall()
        self.positive("local-annotation/no-annotation-control")
        for ref in ("C-001", "C-004"):
            with self.subTest(ref=ref):
                self.wall["origins"][key]["conflict_ref"] = ref
                self.save_wall()
                report = self.run_cli("local-annotation/" + ref)
                self.assertEqual(report["exit_code"], 0)
                for gate in ("G-10", "G-93"):
                    self.assertEqual(statuses(report, gate, "walls.json"), {"SKIP"})

    def test_partial_draft_cannot_hide_zero_normal_or_malformed_budget_host(self):
        self.wall["status"] = "draft"
        self.wall["numeric_unit_epsilon"] = None
        self.save_wall()
        control = self.run_cli("partial-draft/control")
        self.assertEqual(control["exit_code"], 0)
        self.assertEqual(statuses(control, "G-93", "walls.json"), {"SKIP"})
        self.wall["wall_runs"][0]["outward"] = [0, 0]
        self.save_wall()
        bad = self.run_cli("partial-draft/zero-normal")
        self.fail_at(bad, "G-93", "walls.json::wall_runs[0].outward")
        self.assertNotIn("PASS", statuses(bad, "G-93", "walls.json"))
        self.wall["wall_runs"][0]["outward"] = [0, -1]
        self.wall["wall_runs"].append(None)
        self.save_wall()
        bad = self.run_cli("partial-draft/malformed-extra-run")
        self.fail_at(bad, "G-93", "walls.json::wall_runs[2]")
        self.assertEqual(statuses(bad, "G-97", "walls.json"), {"SKIP"})

    def test_unique_owner_and_forbidden_paths(self):
        self.select("facades[0].id")
        self.positive("source-owner/control")
        for path in ("wall_runs[0].thickness_cm", "facades[0]..id", "dimensions.json:facades[0]",
                     "defaults.panel_thickness_cm", "facades[-1].id"):
            with self.subTest(path=path):
                self.select(path)
                self.blocked("source-owner/" + path, path)
        self.select("facades[0].id")
        (self.project / "dimensions.json").write_bytes((self.pipeline / "dimensions.json").read_bytes())
        self.blocked("source-owner/duplicate-parent", "facades[0].id", path=self.project)

    def test_full_declaration_pass_does_not_claim_flipped_sign(self):
        self.positive("normal-sign/control")
        self.wall["wall_runs"][0]["outward"] = [0, 1]
        self.save_wall()
        report = self.positive("normal-sign/flipped-static-only")
        self.assertTrue(any("outward sign and physical face require independent evidence" in r["detail"]
                            for r in rows(report, "G-93", "walls.json")))


class WallLedgerScope(Review):
    def prepare_ledger(self, origin):
        self.split_run(0)
        key = "wall_runs[0].thickness_cm"
        if origin == "assumed":
            name, ref = "assumptions", "A-026"
            doc = self.doc(name)
            entry = copy.deepcopy(doc["assumptions"][0])
            entry.update(id=ref, field_path="walls.json:" + key, value=30.0,
                         reason="Synthetic input ledger control", invalidated_by="synthetic review brief")
            doc["assumptions"].append(entry)
        else:
            name, ref = "conflicts_resolved", "C-006"
            doc = self.doc(name)
            entry = copy.deepcopy(doc["conflicts"][0])
            entry["id"] = ref
            entry["resolution"].update(resulting_value_of="walls.json:" + key,
                                       resolved_paths=["walls.json:" + key], chosen_value=30.0)
            doc["conflicts"].append(entry)
        self.wall["origins"][key] = {"origin": origin, "origin_ref": ref}
        self.save(name, doc)
        self.save_wall()
        self.positive("wall-ledger/" + origin + "/bound-control")
        return name, doc, key

    def test_assumed_owner_path_value_and_uniqueness(self):
        name, clean_ledger, key = self.prepare_ledger("assumed")
        clean_wall = copy.deepcopy(self.wall)
        for fault in ("existing-other-id", "wrong-owner", "same-value-wrong-path", "wrong-value", "duplicate-id"):
            with self.subTest(fault=fault):
                doc = copy.deepcopy(clean_ledger)
                self.wall = copy.deepcopy(clean_wall)
                entry = doc["assumptions"][-1]
                if fault == "existing-other-id":
                    self.wall["origins"][key]["origin_ref"] = "A-001"
                elif fault == "wrong-owner":
                    # Equal value, different owner: no numeric mismatch mask.
                    entry["field_path"] = "dimensions.json:roof.deck_thickness_cm"
                elif fault == "same-value-wrong-path":
                    entry["field_path"] = "walls.json:wall_runs[1].thickness_cm"
                elif fault == "wrong-value":
                    entry["value"] = 31
                else:
                    doc["assumptions"].append(copy.deepcopy(entry))
                self.save(name, doc)
                self.save_wall()
                self.blocked("wall-ledger/assumed/" + fault, rule="G-10", where="walls.json::" + key)

    def test_conflict_owner_claim_and_value(self):
        name, clean_ledger, key = self.prepare_ledger("conflict")
        clean_wall = copy.deepcopy(self.wall)
        for fault in ("existing-other-id", "wrong-owner", "same-value-wrong-primary", "wrong-claim", "wrong-value"):
            with self.subTest(fault=fault):
                doc = copy.deepcopy(clean_ledger)
                self.wall = copy.deepcopy(clean_wall)
                entry = doc["conflicts"][-1]["resolution"]
                if fault == "existing-other-id":
                    self.wall["origins"][key]["origin_ref"] = "C-001"
                elif fault == "wrong-owner":
                    entry["resulting_value_of"] = "dimensions.json:roof.deck_thickness_cm"
                elif fault == "same-value-wrong-primary":
                    entry["resulting_value_of"] = "walls.json:wall_runs[1].thickness_cm"
                elif fault == "wrong-claim":
                    entry["resolved_paths"] = ["walls.json:wall_runs[1].thickness_cm"]
                else:
                    entry["chosen_value"] = 31
                self.save(name, doc)
                self.save_wall()
                self.blocked("wall-ledger/conflict/" + fault, rule="G-10", where="walls.json::" + key)


class StrictBoundaries(Review):
    def test_used_upstream_numeric_boundaries(self):
        self.select("site.plot_rotation_deg")
        self.positive("used-numeric/control")
        for name, needle in (("dimensions", '"plot_rotation_deg": 0.0'),
                             ("assumptions", '"value": 0.0')):
            with self.subTest(file=name):
                path = self.pipeline / (name + ".json")
                original = path.read_text(encoding="utf-8")
                self.assertIn(needle, original)
                for token in ("0.10000000000000001", "1e9999", "1e-9999"):
                    with self.subTest(token=token):
                        value = needle.rsplit(":", 1)[0] + ": " + token
                        path.write_bytes(original.replace(needle, value, 1).encode())
                        report = self.run_cli("used-numeric/" + name + "/" + token)
                        self.assertEqual(report["exit_code"], 1)
                        self.fail_at(report, "G-7", name + ".json")
                        self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"))
                path.write_bytes(original.encode())

    def test_lossy_numeric_cannot_false_pass_legacy_g82(self):
        (self.pipeline / "walls.json").unlink()
        original = CAPTURE[ROOT / "examples/assembly.json"]
        (self.pipeline / "assembly.json").write_bytes(original)
        control = self.run_cli("g82-precision/legacy-control")
        self.assertEqual(control["exit_code"], 0)
        self.assertEqual(statuses(control, "G-82", "assembly.json"), {"PASS"})
        doc = self.doc("assembly")
        doc["wall_cells"][0]["plan_rect_cm"][2] = "LOSSY_NUMBER_TOKEN"
        text = json.dumps(doc, indent=2) + "\n"
        self.assertEqual(text.count('"LOSSY_NUMBER_TOKEN"'), 1)
        for token in ("10000000000000001.9", "9" * 5000):
            with self.subTest(token=token[:60]):
                (self.pipeline / "assembly.json").write_bytes(text.replace('"LOSSY_NUMBER_TOKEN"', token).encode())
                for mode in ("dir", "file"):
                    kwargs = {"mode": mode}
                    if mode == "file":
                        kwargs["path"] = self.pipeline / "assembly.json"
                    report = self.run_cli("g82-precision/reject/" + mode, **kwargs)
                    self.assertEqual(report["exit_code"], 1)
                    self.fail_at(report, "G-7", "assembly.json")
                    self.assertEqual(statuses(report, "G-82"), {"SKIP"})
                    filtered = self.run_cli("g82-precision/filtered/" + mode,
                                            "--rule", "G-82", **kwargs)
                    self.assertEqual(filtered["exit_code"], 1)
                    self.assertEqual(statuses(filtered, "G-82"), {"SKIP"})

    def test_used_upstream_and_ledger_duplicates(self):
        cases = (("dimensions", "facades[0]"), ("assumptions", "site.plot_rotation_deg"),
                 ("conflicts_resolved", "structure.x_bay_cm"), ("massing", "sections[0].points_cm"),
                 ("nurbs", "sections[0].points_cm"), ("facade_grids", "panels[71].width_cm"),
                 ("components_registry", "components[0].size_cm"), ("walls", "facades[0]"))
        originals = {name: (self.pipeline / (name + ".json")).read_bytes() for name, _ in cases}
        for name, source in cases:
            with self.subTest(file=name):
                for key, data in originals.items():
                    (self.pipeline / (key + ".json")).write_bytes(data)
                self.wall = json.loads(originals["walls"])
                self.select(source, registry=name in ("components_registry", "facade_grids"))
                self.positive("duplicate/" + name + "/control")
                path = self.pipeline / (name + ".json")
                clean = path.read_text(encoding="utf-8")
                needle = '"status": "locked"'
                self.assertEqual(clean.count(needle), 1)
                for first in (True, False):
                    dup = ('"status": "superseded", ' + needle if first else
                           needle + ', "status": "superseded"')
                    path.write_bytes(clean.replace(needle, dup, 1).encode())
                    for mode in ("dir", "file"):
                        label = f"duplicate/{name}/bad-{'first' if first else 'last'}/{mode}"
                        report = self.run_cli(label, mode=mode)
                        self.assertEqual(report["exit_code"], 1)
                        self.fail_at(report, "G-7", name + ".json", "duplicate JSON object key")
                        self.assertNotIn("PASS", statuses(report, "G-7", name + ".json"))
                        for gate in ("G-10", "G-93"):
                            self.assertNotIn("PASS", statuses(report, gate, "walls.json"))

    def test_nested_duplicate_used_ledger_value(self):
        self.select("site.plot_rotation_deg")
        self.positive("duplicate-ledger-nested/control")
        path = self.pipeline / "assumptions.json"
        text = path.read_text(encoding="utf-8")
        needle = '"value": 0.0'
        self.assertIn(needle, text)
        path.write_bytes(text.replace(needle, '"value": 1.0, ' + needle, 1).encode())
        report = self.run_cli("duplicate-ledger-nested/value")
        self.fail_at(report, "G-7", "assumptions.json", "duplicate JSON object key")
        self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"))

    def test_precision_overflow_underflow_and_huge_integer(self):
        self.positive("numeric-loader/control")
        path = self.pipeline / "walls.json"
        pristine = path.read_text(encoding="utf-8")
        needle = '"numeric_epsilon_cm": 0.001'
        self.assertEqual(pristine.count(needle), 1)
        for token in ("10000000000000001.9", "0.10000000000000001", "1e-9999", "1e9999",
                      "-1e9999", "NaN", "Infinity", "9007199254740992", "9" * 5000):
            with self.subTest(token=token[:70]):
                path.write_bytes(pristine.replace(needle, '"numeric_epsilon_cm": ' + token, 1).encode())
                report = self.run_cli("numeric-loader/" + token[:60])
                self.assertEqual(report["exit_code"], 1)
                self.fail_at(report, "G-7", "walls.json")
                self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"))

    def test_domain_bounds_reached_without_parser_masking(self):
        for key, limit in (("numeric_epsilon_cm", 0.01), ("numeric_unit_epsilon", 0.001)):
            with self.subTest(key=key):
                old = self.wall[key]
                self.wall[key] = limit
                self.save_wall()
                self.positive("epsilon/" + key + "/boundary-control")
                for value in (0, -1, True, limit * 1.0001, 10000.0):
                    self.wall[key] = value
                    self.save_wall()
                    report = self.run_cli("epsilon/" + key + "/" + str(value))
                    self.assertEqual(report["exit_code"], 1)
                    self.fail_at(report, "G-93", "walls.json::" + key)
                    # G-10 is a provenance-only claim; invalid numerical
                    # geometry does not invalidate an otherwise checked join.
                    self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"))
                    self.assertNotIn("FAIL", statuses(report, "G-7"))
                self.wall[key] = old
                self.save_wall()

    def test_deep_json_never_reports_internal_g8_error(self):
        self.positive("json-depth/control")
        path = self.pipeline / "assumptions.json"
        original = path.read_text(encoding="utf-8")
        self.assertTrue(original.endswith("}\n"))
        for depth in (100, 127, 128, 450, 800, 1200, 4000):
            with self.subTest(depth=depth):
                text = original[:-2] + ',\n  "_nesting_probe": ' + '[' * depth + '0' + ']' * depth + '\n}\n'
                path.write_bytes(text.encode())
                report = self.run_cli("json-depth/" + str(depth))
                if depth == 100:
                    self.assertEqual(report["exit_code"], 0)
                    self.assertEqual(statuses(report, "G-7", "assumptions.json"), {"PASS"})
                elif report["exit_code"] == 1:
                    self.fail_at(report, "G-7", "assumptions.json", "nesting")
                    self.assertNotIn("PASS", statuses(report, "G-93", "walls.json"))
                else:
                    # Supporting intermediate nesting is allowed; no crash or
                    # internal G-8 failure is. Record acceptance, not a refusal.
                    self.assertEqual(statuses(report, "G-7", "assumptions.json"), {"PASS"})


class CliScope(Review):
    def test_file_rule_and_hidden_failure_exit(self):
        self.select("components[0].size_cm", registry=True)
        self.positive("file-rule/file-control", mode="file")
        doc = self.doc("components_registry")
        doc["origins"]["components[0].size_cm"]["derives_from"] = ["NO_SUCH_FIELD"]
        self.save("components_registry", doc)
        full = self.blocked("file-rule/unfiltered", "NO_SUCH_FIELD", mode="file")
        for gate in ("G-7", "G-10", "G-31", "G-92", "G-93"):
            with self.subTest(gate=gate):
                filtered = self.run_cli("file-rule/" + gate, "--rule", gate, mode="file")
                self.assertEqual(filtered["exit_code"], 1)
                self.assertTrue(all(r["rule"] == gate for r in filtered["findings"]))
                self.assertEqual(filtered["findings"], rows(full, gate))

    def test_duplicate_parent_route_in_file_mode(self):
        self.positive("file-route/unique-control", mode="file")
        (self.project / "walls.json").write_bytes((self.pipeline / "walls.json").read_bytes())
        for mode in ("dir", "file"):
            with self.subTest(mode=mode):
                report = self.run_cli("file-route/duplicate/" + mode, mode=mode,
                                      path=self.project if mode == "dir" else None)
                self.assertEqual(report["exit_code"], 1)
                self.fail_at(report, "G-92", "assembly.json")
                self.assertNotIn("PASS", statuses(report, "G-92"))


def main():
    print("SOURCE_HASHES " + json.dumps(INITIAL, sort_keys=True), flush=True)
    program = None
    try:
        program = unittest.main(verbosity=2, exit=False)
    finally:
        final = hashes()
        changed = {name: {"before": digest, "after": final.get(name)}
                   for name, digest in INITIAL.items() if final.get(name) != digest}
        print("SOURCE_DRIFT " + json.dumps(changed, sort_keys=True), flush=True)
        print("OBSERVED_SOURCE_DRIFT " + json.dumps(OBSERVED_DRIFT, sort_keys=True), flush=True)
        if program is not None:
            print("RUN_SUMMARY " + json.dumps({"tests": program.result.testsRun, "cli_calls": CLI_COUNT,
                  "failures": len(program.result.failures), "errors": len(program.result.errors),
                  "skips": len(program.result.skipped), "expected_failures": len(program.result.expectedFailures),
                  "harness_sha256": sha(Path(__file__).read_bytes())}), flush=True)
        OWNER.cleanup()
    if changed or OBSERVED_DRIFT:
        raise SystemExit(2)
    if program is None or not program.result.wasSuccessful() or program.result.skipped:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
