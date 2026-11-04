#!/usr/bin/env python3
"""Isolated, synthetic lint regressions for P2 dependency and PASS scope.

Run: python -B Audit/test_phase16_p2_dependencies.py -v

Each negative test first calibrates its own positive control, then makes one
specific input mutation in a disposable copy of the existing examples. The
wall declaration and the empty draft assembly are test inputs, not output
from a builder. The historical assembly is used only as an unchanged legacy
fixture. No production wall manifest/script, builder, installer, or Max is
created or run. A SKIP is reported as such and is never counted as PASS.
"""
from __future__ import annotations

import copy
import sys
from typing import Any

if __package__:
    from .test_phase16_p2_isolated import Isolated, POLY, ROOT, read_json, write_json
else:
    from test_phase16_p2_isolated import Isolated, POLY, ROOT, read_json, write_json


LEGACY = "legacy_cells_v1"
FORM_DIMENSIONS = (ROOT / "specs" / "fixtures" / "form-precision" /
                   "specs" / "pipeline" / "dimensions.json")


class Dependencies(Isolated):
    def setUp(self) -> None:
        super().setUp()
        self.assertFalse((self.pipeline / "wall_surface.json").exists())
        self.assertFalse((self.pipeline / "wall_surface.ms").exists())

    def probe(self, label: str, scopes: dict[str, str | None], *,
              target: tuple[object, object] | None = None) -> tuple[Any, dict]:
        result, report = self.validate(target=target)
        self.assertEqual(result.returncode, report.get("exit_code"), report.get("summary"))
        outcomes = []
        for gate, location in scopes.items():
            rows = self.scoped(report, gate, location)
            statuses = ",".join(sorted({str(row.get("severity")) for row in rows})) or "ABSENT"
            outcomes.append(f"{gate}={statuses}")
        print(f"\n[{label}] exit={result.returncode} " + " ".join(outcomes),
              file=sys.stderr, flush=True)
        return result, report

    def scoped(self, report: dict, gate: str, location: str | None = None) -> list[dict]:
        return [row for row in self.rows(report, gate)
                if location is None or location in str(row.get("location", ""))]

    def assert_clean(self, result: Any, report: dict) -> None:
        self.assertEqual(result.returncode, 0, self.failures(report))
        self.assertFalse(self.failures(report))

    def assert_pass(self, report: dict, gate: str, location: str | None = None) -> None:
        rows = self.scoped(report, gate, location)
        self.assertTrue(any(row.get("severity") == "PASS" for row in rows), (gate, rows))
        self.assertFalse(any(row.get("severity") == "FAIL" for row in rows), (gate, rows))

    def assert_not_pass(self, report: dict, gate: str, location: str | None = None) -> None:
        rows = self.scoped(report, gate, location)
        self.assertTrue(any(row.get("severity") in ("FAIL", "SKIP") for row in rows),
                        f"{gate} must explicitly FAIL or SKIP, not be absent: {rows}")
        self.assertFalse(any(row.get("severity") == "PASS" for row in rows), (gate, rows))

    def assert_failure(self, result: Any, report: dict, gate: str,
                       location: str, detail: str = "") -> None:
        rows = self.scoped(report, gate, location)
        failures = [row for row in rows if row.get("severity") == "FAIL"
                    and detail.lower() in str(row.get("detail", "")).lower()]
        self.assertNotEqual(result.returncode, 0, self.failures(report))
        self.assertTrue(failures, f"expected {gate} FAIL at {location}, detail {detail!r}: {rows}")

    def source_control(self, kind: str) -> dict:
        """A real dimensions-owned scalar with the ledger ID used by examples."""
        if kind == "assumption":
            path, ident, filename, key = "site.plot_rotation_deg", "A-001", "assumptions.json", "assumptions"
            value = self.dimensions["site"]["plot_rotation_deg"]
        else:
            path, ident, filename, key = "roof.parapet_height_cm", "C-004", "conflicts_resolved.json", "conflicts"
            value = self.dimensions["roof"]["parapet_height_cm"]
        self.assertEqual(self.dimensions["origins"][path], {"origin":
                         "assumed" if kind == "assumption" else "conflict", "origin_ref": ident})
        ledger = read_json(self.pipeline / filename)
        self.assertEqual(ledger["status"], "locked")
        matches = [item for item in ledger[key] if item["id"] == ident]
        self.assertEqual(len(matches), 1)
        entry = matches[0]
        if kind == "assumption":
            self.assertEqual(entry["field_path"], path)
            self.assertEqual(entry["value"], value)
            self.assertTrue(entry["reason"].strip())
        else:
            resolution = entry["resolution"]
            self.assertEqual(resolution["resulting_value_of"], path)
            self.assertIn(path, resolution["resolved_paths"])
            self.assertEqual(resolution["chosen_value"], value)
            self.assertTrue(entry["rejected"])
        self.walls["origin_inputs"] = [path]
        self.save_walls()
        return ledger

    def checked_source_control(self, kind: str) -> dict:
        ledger = self.source_control(kind)
        filename = "assumptions.json" if kind == "assumption" else "conflicts_resolved.json"
        gate = "G-15" if kind == "assumption" else "G-14"
        result, report = self.probe(f"{kind} locked control",
                                    {"G-4": filename, gate: filename,
                                     "G-31": None, "G-93": "walls.json"})
        self.assert_clean(result, report)
        for rule, location in (("G-4", filename), (gate, filename), ("G-31", None),
                               ("G-93", "walls.json")):
            self.assert_pass(report, rule, location)
        return ledger

    def test_assumed_source_locked_positive(self) -> None:
        self.checked_source_control("assumption")

    def test_assumed_source_draft_ledger_never_passes_wall(self) -> None:
        ledger = self.checked_source_control("assumption")
        ledger["status"] = "draft"
        write_json(self.pipeline / "assumptions.json", ledger)
        result, report = self.probe("assumed source: draft ledger",
                                    {"G-4": "assumptions.json", "G-15": "assumptions.json",
                                     "G-93": "walls.json"})
        # No additional malformed entry: status is the only mutation.
        status_rows = self.scoped(report, "G-4", "assumptions.json")
        self.assertTrue(any(row.get("severity") in ("WARN", "SKIP", "FAIL")
                            for row in status_rows), status_rows)
        self.assertFalse(any(row.get("severity") == "PASS" for row in status_rows))
        self.assert_not_pass(report, "G-93", "walls.json")

    def test_assumed_source_empty_reason_fails_g15_and_blocks_wall(self) -> None:
        ledger = self.checked_source_control("assumption")
        self.assertEqual(ledger["assumptions"][0]["id"], "A-001")
        ledger["assumptions"][0]["reason"] = ""
        write_json(self.pipeline / "assumptions.json", ledger)
        result, report = self.probe("assumed source: empty reason",
                                    {"G-4": "assumptions.json", "G-15": "assumptions.json",
                                     "G-93": "walls.json"})
        self.assert_pass(report, "G-4", "assumptions.json")
        self.assert_failure(result, report, "G-15", "assumptions.json::A-001", "reason")
        self.assert_not_pass(report, "G-93", "walls.json")

    def test_conflict_source_locked_positive(self) -> None:
        self.checked_source_control("conflict")

    def test_conflict_source_draft_ledger_never_passes_wall(self) -> None:
        ledger = self.checked_source_control("conflict")
        ledger["status"] = "draft"
        write_json(self.pipeline / "conflicts_resolved.json", ledger)
        result, report = self.probe("conflict source: draft ledger",
                                    {"G-4": "conflicts_resolved.json",
                                     "G-14": "conflicts_resolved.json", "G-93": "walls.json"})
        status_rows = self.scoped(report, "G-4", "conflicts_resolved.json")
        self.assertTrue(any(row.get("severity") in ("WARN", "SKIP", "FAIL")
                            for row in status_rows), status_rows)
        self.assertFalse(any(row.get("severity") == "PASS" for row in status_rows))
        self.assert_not_pass(report, "G-93", "walls.json")

    def test_conflict_source_missing_rejection_fails_g14_and_blocks_wall(self) -> None:
        ledger = self.checked_source_control("conflict")
        entry = next(item for item in ledger["conflicts"] if item["id"] == "C-004")
        entry["rejected"] = []
        write_json(self.pipeline / "conflicts_resolved.json", ledger)
        result, report = self.probe("conflict source: missing rejection",
                                    {"G-4": "conflicts_resolved.json",
                                     "G-14": "conflicts_resolved.json", "G-93": "walls.json"})
        self.assert_pass(report, "G-4", "conflicts_resolved.json")
        self.assert_failure(result, report, "G-14", "conflicts_resolved.json::C-004", "rejected")
        self.assert_not_pass(report, "G-93", "walls.json")

    def legacy_route_control(self) -> None:
        # Use the shipped historical assembly itself; no mock poly output.
        (self.pipeline / "walls.json").unlink()
        self.assembly = copy.deepcopy(self.original_assembly)
        write_json(self.pipeline / "assembly.json", self.assembly)
        self.assertNotIn("wall_technique", self.assembly)
        result, report = self.probe("unchanged historical legacy route",
                                    {"G-31": None, "G-92": None})
        self.assert_clean(result, report)
        self.assert_pass(report, "G-31")
        self.assert_pass(report, "G-92")

    def test_historical_route_positive(self) -> None:
        self.legacy_route_control()

    def test_assembly_project_mismatch_fails_g31_and_blocks_g92(self) -> None:
        self.legacy_route_control()
        self.assembly["project"] = "other"
        write_json(self.pipeline / "assembly.json", self.assembly)
        result, report = self.probe("assembly project mismatch", {"G-31": None, "G-92": None})
        self.assert_failure(result, report, "G-31", "assembly.json", "project")
        self.assert_not_pass(report, "G-92")

    def form_control(self) -> None:
        fixture = read_json(FORM_DIMENSIONS)
        reference = copy.deepcopy(fixture["form_references"][0])
        self.assertEqual(reference["kind"], "semi_elliptical_barrel")
        self.assertGreater(reference["semi_axes_cm"][0], 0)
        self.dimensions["schema_version"] = "1.1"
        self.dimensions["form_references"] = [reference]
        self.dimensions["origins"]["form_references[0]"] = {"origin": "given"}
        self.walls["origin_inputs"] = ["form_references[0].semi_axes_cm"]
        write_json(self.pipeline / "dimensions.json", self.dimensions)
        self.save_walls()
        result, report = self.probe("well-formed upstream form reference",
                                    {"G-86": "dimensions.json", "G-93": "walls.json"})
        self.assert_clean(result, report)
        self.assert_pass(report, "G-86", "dimensions.json")
        self.assert_pass(report, "G-93", "walls.json")

    def test_upstream_form_reference_positive(self) -> None:
        self.form_control()

    def test_invalid_upstream_form_reference_fails_g86_and_blocks_wall(self) -> None:
        self.form_control()
        self.dimensions["form_references"][0]["semi_axes_cm"][0] = -1.0
        write_json(self.pipeline / "dimensions.json", self.dimensions)
        result, report = self.probe("invalid upstream form reference",
                                    {"G-86": "dimensions.json", "G-93": "walls.json"})
        self.assert_failure(result, report, "G-86", "dimensions.json::form_references[0].semi_axes_cm")
        self.assert_not_pass(report, "G-93", "walls.json")

    def route_control(self) -> None:
        # The only assembly here remains the empty draft placeholder; attaching
        # a selector is not a claim that S5 output or a manifest exists.
        self.assembly["wall_technique"] = POLY
        write_json(self.pipeline / "assembly.json", self.assembly)
        self.assertEqual(self.assembly["status"], "draft")
        self.assertEqual(self.assembly["placements"], [])
        self.assertFalse((self.pipeline / "wall_surface.json").exists())
        result, report = self.probe("matching draft route control",
                                    {"G-92": None, "G-93": "walls.json",
                                     "G-94": "walls.json", "G-97": "walls.json"})
        self.assert_clean(result, report)
        self.assert_not_pass(report, "G-92")  # a draft echo is not production evidence
        for gate in ("G-93", "G-94", "G-97"):
            self.assert_pass(report, gate, "walls.json")

    def test_matching_draft_route_positive_for_opening_and_budget_checks(self) -> None:
        self.route_control()

    def conflicting_route(self) -> tuple[Any, dict]:
        self.route_control()
        self.assembly["wall_technique"] = LEGACY
        write_json(self.pipeline / "assembly.json", self.assembly)
        result, report = self.probe("conflicting assembly route",
                                    {"G-92": None, "G-94": "walls.json", "G-97": "walls.json"})
        self.assert_failure(result, report, "G-92", "walls.json / assembly.json", "conflicts")
        return result, report

    def test_conflicting_route_blocks_g94_pass(self) -> None:
        _, report = self.conflicting_route()
        self.assert_not_pass(report, "G-94", "walls.json")

    def test_conflicting_route_blocks_g97_pass(self) -> None:
        _, report = self.conflicting_route()
        self.assert_not_pass(report, "G-97", "walls.json")

    def unlisted_file_control(self) -> None:
        self.target = self.pipeline / "unlisted_control.json"
        envelope_keys = ("schema_version", "spec", "project", "units", "source", "status")
        document = {key: copy.deepcopy(self.dimensions[key]) for key in envelope_keys}
        document["spec"] = self.target.stem
        write_json(self.target, document)
        result, report = self.probe("valid non-inventory --file",
                                    {"G-7": self.target.name}, target=("--file", self.target))
        # Unlisted project specs can have a G-1 FAIL independently of JSON
        # hygiene. Calibrate only G-7: neither G-1 nor its process exit proves
        # that G-7 detected the malformed negative. A clean control is fine too.
        unrelated = self.failures(report)
        if unrelated:
            print("  control: other FAILs " + ", ".join(
                f"{row.get('rule')}@{row.get('location')}" for row in unrelated),
                  file=sys.stderr, flush=True)
        self.assert_pass(report, "G-7", self.target.name)

    def test_valid_unlisted_file_positive(self) -> None:
        self.unlisted_file_control()

    def test_invalid_unlisted_file_never_reports_g7_pass(self) -> None:
        self.unlisted_file_control()
        self.target.write_bytes(b'{"control":\n')
        result, report = self.probe("invalid non-inventory --file",
                                    {"G-7": self.target.name}, target=("--file", self.target))
        self.assertNotEqual(result.returncode, 0, self.failures(report))
        self.assert_not_pass(report, "G-7", self.target.name)


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
