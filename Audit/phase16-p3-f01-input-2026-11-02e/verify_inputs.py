#!/usr/bin/env python3
"""Recheck this INPUT ONLY fixture without Max or generated geometry.

Run from the repository root with python -B. The accepted P2 CLI is invoked
unchanged. Its four absent-downstream inventory FAILs are retained, not filtered
from the raw reports and not presented as an overall PASS.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
PROJECT = BASE / "project"
VALIDATOR = ROOT / "scripts/validate_specs.py"
EXPECTED_VALIDATOR_SHA256 = "616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f"
EXPECTED_PLAN_SHA256 = "37813bb8f6b8d2e445c69a0424d78997f80a3752303ccffebee802e1d84ee672"
EXPECTED_EVIDENCE_SHA256 = "2869308638ba8e87766617a572937a769eb325b0a0699075c64d2cb8452141ad"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def main() -> None:
    assert sha256(VALIDATOR) == EXPECTED_VALIDATOR_SHA256, "accepted P2 validator drift"
    plan = ROOT / "Audit/AGENT_PLAN_poly_surface_shell.md"
    evidence = ROOT / "Audit/EVIDENCE_2026-10-27.md"
    assert sha256(plan) == EXPECTED_PLAN_SHA256, "actual analytical plan drift"
    assert sha256(evidence) == EXPECTED_EVIDENCE_SHA256, "historical evidence drift"
    source_lines = plan.read_text(encoding="utf-8").splitlines()
    # This is a bounded read/check of the actual named analytical source, not
    # a semantic verifier for arbitrary source text or independent scene QA.
    for text in ("u = 0…400", "Y = 0", "Z = 0…300", "(0,−1,0)", "**30**"):
        assert text in source_lines[669], (670, text)
    for text in ("u = 50…150", "Z = 0…210", "u = 230…330", "Z = 90…210"):
        assert text in source_lines[670], (671, text)
    assert "[0, 50, 150, 230, 330, 400]" in source_lines[672]

    authority = load(BASE / "direction-authority.json")
    assert set(authority) == {
        "schema_version", "project", "wall_run_id", "walls_sha256", "source_file",
        "source_sha256", "source_location", "inner_start_cm", "inner_end_cm",
        "base_z_cm", "top_z_cm", "outward",
    }
    assert authority["schema_version"] == "p3-direction-authority-1"
    assert authority["source_file"] == "Audit/AGENT_PLAN_poly_surface_shell.md"
    assert authority["source_sha256"] == sha256(plan)
    assert authority["walls_sha256"] == sha256(PROJECT / "walls.json")
    walls = load(PROJECT / "walls.json")
    dim = load(PROJECT / "dimensions.json")
    run, = walls["wall_runs"]
    assert walls["project"] == dim["project"] == authority["project"] == "phase16-p3-f01"
    assert run["id"] == authority["wall_run_id"] == "RUN-F01"
    for key, run_key, expected in (
        ("inner_start_cm", "start_cm", [0, 0]),
        ("inner_end_cm", "end_cm", [400, 0]),
        ("base_z_cm", "base_z_cm", 0),
        ("top_z_cm", "top_z_cm", 300),
        ("outward", "outward", [0, -1]),
    ):
        assert authority[key] == run[run_key] == expected, (key, run_key)
    assert len(walls["blocks"]) == 1 and walls["upper_returns"] == []
    assert run["thickness_cm"] == 30
    assert run["contour_ref"] == "dimensions.json:facades:F-S"
    assert run["start_cm"] == dim["facades"][0]["start_corner_cm"]
    assert run["end_cm"] == dim["facades"][0]["end_corner_cm"]
    door, window = walls["openings"]
    assert (door["kind"], door["u_range_cm"], door["sill_cm"], door["head_cm"]) == ("door", [50, 150], 0, 210)
    assert (window["kind"], window["u_range_cm"], window["sill_cm"], window["head_cm"]) == ("window", [230, 330], 90, 210)
    us = sorted({0, 400, *(u for op in walls["openings"] for u in op["u_range_cm"])})
    vs = sorted({0, 300, *(v for op in walls["openings"] for v in (op["sill_cm"], op["head_cm"]))})
    assert us == [0, 50, 150, 230, 330, 400] and vs == [0, 90, 210, 300]
    area = 400 * 300 - sum((op["u_range_cm"][1] - op["u_range_cm"][0]) * (op["head_cm"] - op["sill_cm"]) for op in walls["openings"])
    assert area == 87000 and area * run["thickness_cm"] == 2610000
    face9_center = [(us[3] + us[4]) / 2, 0, (vs[1] + vs[2]) / 2]
    assert face9_center == [280, 0, 150]
    for name in ("assembly.json", "wall_surface.json", "wall_surface.ms", "massing.json", "nurbs.json", "facade_grids.json", "components_registry.json", "qa.json"):
        assert not (PROJECT / name).exists(), "input-only boundary violated: " + name

    seed_dimensions = ROOT / "examples/dimensions.json"
    seed_assumptions = ROOT / "examples/assumptions.json"
    seed_conflicts = ROOT / "examples/conflicts_resolved.json"
    for path, expected in (
        (seed_dimensions, "5f0f0108936457b08149d78790a2f2453edc3f95b8c8abddc550effab3e52f75"),
        (seed_assumptions, "1c8d8eb29b5c09d81229058d106a99a84da0d1c9f537c10e990aba938335b986"),
        (seed_conflicts, "6676c4f38c7b2bb40d44828af631fc2b41e20754819d9cbf339b099b63d6f5fc"),
    ):
        assert sha256(path) == expected, "real seed drift: " + str(path)
    assert dim["tolerances"] == walls["tolerances"] == load(seed_dimensions)["tolerances"]
    assert load(PROJECT / "conflicts_resolved.json")["precedence_rules"] == load(seed_conflicts)["precedence_rules"]
    protected = [VALIDATOR, plan, evidence, seed_dimensions, seed_assumptions,
                 seed_conflicts, ROOT / "references/07-spec-grammar.md",
                 ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md",
                 *sorted(PROJECT.glob("*.json")), BASE / "direction-authority.json",
                 BASE / "fixture-brief.md"]
    before = {p.relative_to(ROOT).as_posix(): sha256(p) for p in protected}
    commands = []
    for label, flags in (("lint", []), ("build", ["--build", "--warnings-as-errors"])):
        command = [sys.executable, "-B", str(VALIDATOR), "--dir", str(PROJECT), "--json", *flags]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        (BASE / (label + "-validator.json")).write_bytes(result.stdout.encode("utf-8"))
        (BASE / (label + "-validator-stderr.txt")).write_bytes(result.stderr.encode("utf-8"))
        report = json.loads(result.stdout)
        assert result.returncode == report["exit_code"] == 1
        assert not result.stderr
        assert report["summary"] == {"FAIL": 4, "WARN": 0, "SKIP": 23, "PASS": 62}
        failures = [row for row in report["findings"] if row["severity"] == "FAIL"]
        assert {(row["rule"], row["location"]) for row in failures} == {
            ("G-1", name + ".json") for name in ("massing", "nurbs", "facade_grids", "components_registry")
        }
        for rule in ("G-9", "G-10", "G-93", "G-94", "G-97"):
            assert any(row["rule"] == rule and row["location"] == "walls.json" and row["severity"] == "PASS" for row in report["findings"]), rule
        assert any(row["rule"] == "G-32" and row["severity"] == "PASS" and row["location"] == "dimensions.json" and "16 derived" in row["detail"] for row in report["findings"])
        for rule in ("G-92", "G-95", "G-96", "G-98", "G-99", "G-100"):
            rows = [row for row in report["findings"] if row["rule"] == rule]
            assert rows and all(row["severity"] == "SKIP" for row in rows), (rule, rows)
        commands.append({"label": label, "argv": command, "exit_code": result.returncode,
                         "summary": report["summary"], "failures": failures,
                         "skips": [row for row in report["findings"] if row["severity"] == "SKIP"]})
        print(label + ": PASS62 FAIL4 WARN0 SKIP23; only missing downstream inventory FAILs")
    after = {p.relative_to(ROOT).as_posix(): sha256(p) for p in protected}
    assert before == after, "protected source or input bytes changed during validation"
    locked_paths = [*sorted(PROJECT.glob("*.json")), BASE / "direction-authority.json",
                    BASE / "fixture-brief.md", plan, evidence,
                    ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md"]
    write(BASE / "input-lock.json", {
        "schema_version": "f01-input-lock-1",
        "status": "locked_input_only_not_produced_output",
        "project": "phase16-p3-f01",
        "path_base": "repository_root",
        "files_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in locked_paths},
        "direction_authority": (BASE / "direction-authority.json").relative_to(ROOT).as_posix(),
        "source_file": authority["source_file"],
        "source_sha256": authority["source_sha256"],
        "source_location": authority["source_location"],
        "not_a_builder_manifest": True,
    })
    write(BASE / "validation-record.json", {
        "status": "input_only_scoped_gates_pass_whole_pipeline_inventory_refused",
        "validator_sha256": EXPECTED_VALIDATOR_SHA256,
        "commands": commands,
        "protected_hashes_before": before,
        "protected_hashes_after": after,
        "source_location_checked": "Audit/AGENT_PLAN_poly_surface_shell.md lines 670-673",
        "predictions_not_measurements": {"u_stations_cm": us, "v_stations_cm": vs,
            "active_area_cm2": area, "thickness_product_cm3": area * run["thickness_cm"],
            "row_major_face9_center_cm": face9_center},
        "limitations": ["No overall validator PASS", "No emitted output or assembly",
            "No Max execution or live measurements", "No source-content semantic proof for arbitrary text",
            "No installation, packaging or git command"],
    })
    print("Actual plan values / exact direction-attestation shape+hashes / 16 documented formulas / stable bytes checked")


if __name__ == "__main__":
    main()
