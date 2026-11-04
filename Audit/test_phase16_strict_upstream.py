#!/usr/bin/env python3
"""Read-only Phase 16 P2 duplicate-key audit; all test inputs are disposable.

Run: python -B Audit/test_phase16_strict_upstream.py

This is a diagnostic/contract regression: it exits 1 when a duplicate is
accepted for a wall dependency or its ledger, and 2 for an invalid control or
a changing source snapshot.  The wall is synthetic *input*, and the empty draft
assembly is not an output.  No builder, installer, or Max is invoked.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (ROOT / "scripts" / "validate_specs.py", ROOT / "scripts" / "curve_gen.py",
           ROOT / "scripts" / "wall_cell_coverage.py",
           ROOT / "specs" / "fixtures" / "poly-shell-input" / "walls.json")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_snapshot() -> dict[Path, bytes]:
    example_files = sorted(p for p in (ROOT / "examples").rglob("*") if p.is_file())
    result = {p: p.read_bytes() for p in (*SOURCES, *example_files)}
    for path in SOURCES[:3]:
        ast.parse(result[path], filename=str(path))
    return result


def rows(report: dict[str, Any], rule: str, location: str) -> list[dict[str, Any]]:
    return [f for f in report["findings"] if f["rule"] == rule and location in f["location"]]


def status(report: dict[str, Any], rule: str, location: str) -> str:
    return ",".join(sorted({f["severity"] for f in rows(report, rule, location)})) or "ABSENT"


def put_json(path: Path, value: Any) -> None:
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))


def replace_once(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise RuntimeError(f"fixture anchor occurs {text.count(before)} times: {before!r}")
    return text.replace(before, after, 1)


def case(prefix: str, key: str, bad: str, good: str) -> tuple[str, str, str, str]:
    """One unique object-local prefix and a key whose single good value is known."""
    anchor = prefix + f'"{key}": {good}'
    bad_only = prefix + f'"{key}": {bad}'
    bad_first = prefix + f'"{key}": {bad}, "{key}": {good}'
    bad_last = prefix + f'"{key}": {good}, "{key}": {bad}'
    return anchor, bad_only, bad_first, bad_last


def run(snapshot: dict[Path, bytes], temp: Path) -> int:
    source = snapshot[SOURCES[0]]
    baseline = subprocess.run(["git", "show", "HEAD:scripts/validate_specs.py"], cwd=ROOT,
                              capture_output=True, check=True).stdout
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, check=True).stdout.strip()
    ast.parse(baseline)
    print("current validator sha256=" + sha(source), flush=True)
    print("baseline HEAD=" + commit + " validator sha256=" + sha(baseline), flush=True)
    print("curve_gen sha256=" + sha(snapshot[SOURCES[1]]), flush=True)
    print("wall_cell_coverage sha256=" + sha(snapshot[SOURCES[2]]), flush=True)
    print("synthetic walls sha256=" + sha(snapshot[SOURCES[3]]), flush=True)
    example_files = sorted(p for p in snapshot if p.is_relative_to(ROOT / "examples"))
    tree_hash = sha("\n".join(str(p.relative_to(ROOT)) + "=" + sha(snapshot[p])
                              for p in example_files).encode("utf-8"))
    print("examples path+sha256 tree=" + tree_hash, flush=True)

    scripts = temp / "scripts"
    scripts.mkdir()
    (scripts / "validate_current.py").write_bytes(source)
    (scripts / "validate_baseline.py").write_bytes(baseline)
    # Counterfactual of THIS snapshot with only the pre-change duplicate-key
    # dispatch restored. This is not represented as the earlier live file.
    raw = source.decode("utf-8")
    try:
        selective = replace_once(raw,
                                 "def strict_json_loads(text: str) -> Any:",
                                 "def strict_json_loads(text: str, reject_duplicate_keys: bool = False) -> Any:")
        selective = replace_once(selective, "object_pairs_hook=_unique)",
                                 "object_pairs_hook=_unique if reject_duplicate_keys else None)")
        selective = replace_once(selective, "record.doc = strict_json_loads(record.text)",
                                 'record.doc = strict_json_loads(record.text, reject_duplicate_keys=path.stem in ("walls", "assembly"))')
    except RuntimeError:
        if ('reject_duplicate_keys=path.stem in ("walls", "assembly")' in raw
                and "object_pairs_hook=_unique if reject_duplicate_keys else None" in raw):
            selective = raw  # the actual selective implementation
        else:
            selective = None
    if selective is None:
        print("selective-dispatch counterfactual unavailable: parser implementation changed", flush=True)
    else:
        ast.parse(selective)
        print("selective-dispatch counterfactual sha256=" + sha(selective.encode("utf-8")), flush=True)
        (scripts / "validate_selective.py").write_bytes(selective.encode("utf-8"))
    for path in SOURCES[1:3]:
        (scripts / path.name).write_bytes(snapshot[path])
    base = temp / "base"
    base.mkdir()
    for path in example_files:
        dst = base / path.relative_to(ROOT / "examples")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(snapshot[path])
    dims = json.loads((base / "dimensions.json").read_bytes())
    example = json.loads((base / "assembly.json").read_bytes())
    walls = json.loads(snapshot[SOURCES[3]])
    assert walls["project"] == dims["project"]
    draft = {
        "schema_version": "1.0", "spec": "assembly", "project": example["project"],
        "units": example["units"],
        "source": {"kind": "derived", "reference": "components_registry.json; synthetic empty draft only",
                   "recorded_at": "2026-11-02T00:00:00Z"},
        "status": "draft", "tolerances": example["tolerances"], "origin_inputs": [],
        "origins": {}, "defaults": {}, "layer_map": {}, "placements": [], "opening_cuts": [],
        "wall_cells": [], "scatter": [],
    }
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    env.pop("PYTHONPATH", None)
    def work_case(label: str, name: str, mutation: tuple[str, str, str, str],
                  origin: str | None, version: str = "current", legacy: bool = False,
                  variant: int = 0, file_mode: bool = False) -> dict[str, Any]:
        identity = sha(repr((label, name, origin, version, legacy, variant, file_mode)).encode("utf-8"))
        target = temp / ("case-" + identity)
        shutil.copytree(base, target)
        if not legacy:
            wall = json.loads(snapshot[SOURCES[3]])
            if origin is not None:
                wall["origin_inputs"] = [origin]
            put_json(target / "walls.json", wall)
            put_json(target / "assembly.json", draft)
            (target / "assembly.ms").unlink(missing_ok=True)
            if origin == "components[0].size_cm":
                # Historical registry has size -> parameters -> size. Replace
                # only its six return edges to calibrate an acyclic synthetic
                # provenance control, without asserting a formula is correct.
                registry_path = target / "components_registry.json"
                registry = json.loads(registry_path.read_bytes())
                for index in (0, 1):
                    for key in ("source", "value", "units"):
                        entry = registry["origins"][f"components[0].parameters[{index}].{key}"]
                        assert entry["derives_from"] == ["components[0].size_cm"]
                        entry["derives_from"] = ["tolerances.linear_cm"]
                put_json(registry_path, registry)
        if variant:
            path = target / name
            text = path.read_bytes().decode("utf-8")
            path.write_bytes(replace_once(text, mutation[0], mutation[variant]).encode("utf-8"))
        script = scripts / {"current": "validate_current.py", "HEAD": "validate_baseline.py",
                            "selective": "validate_selective.py"}[version]
        selection = ["--file", str(target / "walls.json")] if file_mode else ["--dir", str(target)]
        process = subprocess.run([sys.executable, "-B", str(script), *selection, "--json"],
                                 cwd=temp, env=env, text=True, encoding="utf-8", errors="replace",
                                 capture_output=True, timeout=120, check=False)
        if process.stderr or process.returncode not in (0, 1):
            raise RuntimeError(f"{label}: validator exited {process.returncode}: {process.stderr}")
        report = json.loads(process.stdout)
        if report.get("exit_code") != process.returncode:
            raise RuntimeError(f"{label}: JSON/process exit mismatch")
        internal = [f for f in report["findings"] if "internal error" in f.get("detail", "").lower()]
        if internal:
            raise RuntimeError(f"{label}: validator internal errors: {internal}")
        g7 = status(report, "G-7", name)
        g93 = status(report, "G-93", "walls.json") if not legacy else "n/a"
        failures = [f for f in report["findings"] if f["severity"] == "FAIL"]
        fail_summary = ",".join(sorted({f['rule'] for f in failures})) or "none"
        print(f"{label}: exit={process.returncode} G-7[{name}]={g7} G-93[walls]={g93} "
              f"FAIL={len(failures)}({fail_summary})", flush=True)
        return report

    # Each prefix uniquely identifies the object whose key is duplicated.
    scenarios = [
        ("dimensions.project", "dimensions.json", case("  ", "project", '"other-project"', '"pavilion-01"'),
         "facades[0]"),
        ("dimensions.facade.end", "dimensions.json", case('"id": "F-S",\n      "name": "south",\n'
         '      "direction_deg": 180.0,\n      "start_corner_cm": [0.0, 0.0],\n      ',
         "end_corner_cm", "[1700.0, 0.0]", "[1800.0, 0.0]"), "facades[0]"),
        ("dimensions.facade.derives_from", "dimensions.json", case('"facades[0]": { "origin": "derived", ',
         "derives_from", '["NO_SUCH_FIELD"]',
         '["site.footprint_cm", "site.plot_rotation_deg", "structure.x_bay_cm"]'), "facades[0]"),
        ("dimensions.origin_ref", "dimensions.json", case('"site.plot_rotation_deg": { "origin": "assumed", ',
         "origin_ref", '"A-999"', '"A-001"'), "site.plot_rotation_deg"),
        ("assumptions.project", "assumptions.json", case("  ", "project", '"other-project"', '"pavilion-01"'),
         "site.plot_rotation_deg"),
        ("assumptions.value", "assumptions.json", case('"id": "A-001",\n'
         '      "field_path": "site.plot_rotation_deg",\n      ', "value", "1.0", "0.0"),
         "site.plot_rotation_deg"),
        ("assumptions.field_path", "assumptions.json", case('"id": "A-001",\n      ', "field_path",
         '"site.NO_SUCH_FIELD"', '"site.plot_rotation_deg"'), "site.plot_rotation_deg"),
        ("conflicts.chosen_value", "conflicts_resolved.json", case('"chosen_sources": ["brief:para3"],\n'
         '        ', "chosen_value", "9", "4"), "structure.x_bay_cm"),
        ("massing.project", "massing.json", case("  ", "project", '"other-project"', '"pavilion-01"'),
         "storeys[0].elevation_cm"),
        ("nurbs.project", "nurbs.json", case("  ", "project", '"other-project"', '"pavilion-01"'),
         "sections[0].points_cm"),
        ("registry.project", "components_registry.json", case("  ", "project", '"other-project"',
         '"pavilion-01"'), "components[0].size_cm"),
        ("walls.selector", "walls.json", case("  ", "wall_technique", '"not_a_route"',
         '"poly_surface_shell_v1"'), "facades[0]"),
        ("assembly.project", "assembly.json", case("  ", "project", '"other-project"', '"pavilion-01"'),
         "facades[0]"),
    ]
    errors: list[str] = []
    violations: list[str] = []
    negative_targets = {
        "dimensions.project": ("G-31", "dimensions.json"),
        "dimensions.facade.end": ("G-25", "dimensions.json::facades[0]"),
        "dimensions.facade.derives_from": ("G-10", "dimensions.json::facades[0]"),
        "dimensions.origin_ref": ("G-10", "dimensions.json::site.plot_rotation_deg"),
        "assumptions.project": ("G-31", "assumptions.json"),
        "assumptions.value": ("G-12", "assumptions.json::site.plot_rotation_deg"),
        "assumptions.field_path": ("G-12", "assumptions.json::site.NO_SUCH_FIELD"),
        "conflicts.chosen_value": ("G-12", "conflicts_resolved.json::facades[0].bay_count"),
        "massing.project": ("G-31", "massing.json"),
        "nurbs.project": ("G-31", "nurbs.json"),
        "registry.project": ("G-31", "components_registry.json"),
        "walls.selector": ("G-92", "walls.json / assembly.json"),
        "assembly.project": ("G-31", "assembly.json"),
    }
    # Four independent copies at a time reduce the risk that a concurrently
    # edited source changes before the final stability guard. No outputs or
    # input directories are shared between validators.
    pool = ThreadPoolExecutor(max_workers=4)
    futures: dict[tuple, Any] = {}

    def schedule(label: str, name: str, mutation: tuple[str, str, str, str],
                 origin: str | None, version: str = "current", legacy: bool = False,
                 variant: int = 0, file_mode: bool = False) -> None:
        key = (label, name, mutation, origin, version, legacy, variant, file_mode)
        if key in futures:
            raise RuntimeError("duplicate test identity " + label)
        futures[key] = pool.submit(work_case, *key)

    def run_case(label: str, name: str, mutation: tuple[str, str, str, str],
                 origin: str | None, version: str = "current", legacy: bool = False,
                 variant: int = 0, file_mode: bool = False) -> dict[str, Any]:
        return futures[(label, name, mutation, origin, version, legacy, variant, file_mode)].result()

    comparison_cases = {"dimensions.project", "dimensions.facade.end", "dimensions.facade.derives_from",
                        "assumptions.value", "assumptions.field_path"}
    for label, filename, mutation, origin in scenarios:
        for variant, suffix in ((0, "clean"), (1, "bad-only"), (2, "duplicate bad-first"),
                                (3, "duplicate bad-last")):
            schedule(label + " " + suffix, filename, mutation, origin, variant=variant)
        if selective is not None and label in comparison_cases:
            for variant, suffix in ((0, "clean"), (1, "bad-only"), (2, "duplicate bad-first"),
                                    (3, "duplicate bad-last")):
                schedule("selective " + label + " " + suffix, filename, mutation, origin,
                         version="selective", variant=variant)
    for label in ("dimensions.facade.end", "assumptions.value", "massing.project"):
        _, filename, mutation, origin = next(item for item in scenarios if item[0] == label)
        for variant, suffix in ((0, "clean"), (2, "duplicate bad-first"), (3, "duplicate bad-last")):
            schedule("--file walls " + label + " " + suffix, filename, mutation, origin,
                     variant=variant, file_mode=True)
    legacy_dimensions = scenarios[0][2]
    legacy_assumptions = scenarios[5][2]
    legacy_assembly = next(item[2] for item in scenarios if item[0] == "assembly.project")
    legacy_cases = (("legacy.dimensions", "dimensions.json", legacy_dimensions),
                    ("legacy.assumptions", "assumptions.json", legacy_assumptions),
                    ("legacy.assembly", "assembly.json", legacy_assembly))
    for label, filename, mutation in legacy_cases:
        for version in ("HEAD", "current"):
            schedule(label + " " + version + " clean", filename, mutation, None,
                     version=version, legacy=True)
            schedule(label + " " + version + " duplicate bad-first", filename, mutation, None,
                     version=version, legacy=True, variant=2)
    for label, filename, mutation, origin in scenarios:
        control = run_case(label + " clean", filename, mutation, origin)
        if control["exit_code"] or "PASS" not in status(control, "G-93", "walls.json"):
            errors.append(label + " positive control did not produce G-93 PASS with zero FAIL")
        bad = run_case(label + " bad-only", filename, mutation, origin, variant=1)
        gate, where = negative_targets[label]
        if not bad["exit_code"] or not any(f["severity"] == "FAIL" for f in rows(bad, gate, where)):
            errors.append(label + " single bad key did not produce target " + gate + " FAIL")
        if label not in ("assembly.project",) and "PASS" in status(bad, "G-93", "walls.json"):
            errors.append(label + " single invalid used source retained G-93 PASS")
        if label == "assembly.project" and status(bad, "G-92", "walls.json / assembly.json") != "SKIP":
            errors.append("assembly.project mismatched project did not SKIP G-92")
        for variant, name in ((2, "duplicate bad-first"), (3, "duplicate bad-last")):
            result = run_case(label + " " + name, filename, mutation, origin, variant=variant)
            # The explicit-wall contract requires a duplicate-key hygiene FAIL,
            # and a G-93 PASS must not survive a bad upstream/ledger document.
            hygiene = rows(result, "G-7", filename)
            wall_status = status(result, "G-93", "walls.json")
            if (not any(f["severity"] == "FAIL" and "duplicate" in f["detail"].lower() for f in hygiene)
                    or "PASS" in wall_status or wall_status == "ABSENT" or result["exit_code"] != 1):
                violations.append(label + " " + name)

    for label in ("dimensions.facade.end", "assumptions.value", "massing.project"):
        entry = next(item for item in scenarios if item[0] == label)
        _, filename, mutation, origin = entry
        for variant, suffix in ((0, "clean"), (2, "duplicate bad-first"), (3, "duplicate bad-last")):
            result = run_case("--file walls " + label + " " + suffix, filename, mutation, origin,
                              variant=variant, file_mode=True)
            wall_status = status(result, "G-93", "walls.json")
            if variant == 0 and (result["exit_code"] or wall_status != "PASS"):
                errors.append("--file walls " + label + " clean control failed")
            if variant and (result["exit_code"] != 1 or "FAIL" not in status(result, "G-7", filename)
                            or "PASS" in wall_status or wall_status == "ABSENT"):
                violations.append("--file walls " + label + " " + suffix)

    # Replay upstream/ledger cases with identical validator logic but restored
    # selective parser dispatch. Actual P2 false PASS, not a guessed effect.
    for label, filename, mutation, origin in scenarios:
        if selective is None or label not in comparison_cases:
            continue
        for variant, suffix in ((0, "clean"), (1, "bad-only"), (2, "duplicate bad-first"),
                                (3, "duplicate bad-last")):
            report = run_case("selective " + label + " " + suffix, filename, mutation, origin,
                              version="selective", variant=variant)
            if variant == 0 and (report["exit_code"] or status(report, "G-93", "walls.json") != "PASS"):
                errors.append("selective " + label + " clean control failed")
            if variant == 1:
                gate, where = negative_targets[label]
                if not any(f["severity"] == "FAIL" for f in rows(report, gate, where)):
                    errors.append("selective " + label + " target bad-only not detected")
            if variant == 2 and (report["exit_code"] != 0 or status(report, "G-93", "walls.json") != "PASS"):
                errors.append("selective " + label + " did not reproduce last-key-wins false PASS")

    # Historical clean/no-selector and exact identical ambiguous file on old and
    # new validators: distinguish an observed behavior change from acceptance.
    for label, name, mutation in legacy_cases:
        for version in ("HEAD", "current"):
            clean = run_case(label + " " + version + " clean", name, mutation, None,
                             version=version, legacy=True)
            if clean["exit_code"]:
                errors.append(label + " " + version + " legacy clean control failed")
            run_case(label + " " + version + " duplicate bad-first", name, mutation, None,
                     version=version, legacy=True, variant=2)

    pool.shutdown(wait=True)
    if errors:
        print("INVALID CONTROLS:", "; ".join(errors), flush=True)
    if violations:
        print("CONTRACT VIOLATIONS:", "; ".join(violations), flush=True)
    return 2 if errors else 1 if violations else 0


def main() -> int:
    first = read_snapshot()
    time.sleep(8)
    if first != read_snapshot():
        print("INCONCLUSIVE: scripts or synthetic input changed during preflight", file=sys.stderr)
        return 2
    approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
    parent = str(approved) if os.name == "nt" and approved.is_dir() else None
    with tempfile.TemporaryDirectory(prefix="phase16-strict-upstream-", dir=parent) as directory:
        code = run(first, Path(directory))
        final = read_snapshot()
        if first != final:
            for path in sorted(set(first) | set(final)):
                if first.get(path) != final.get(path):
                    print(f"CHANGED {path}: before={sha(first[path]) if path in first else 'absent'} "
                          f"after={sha(final[path]) if path in final else 'absent'}", file=sys.stderr)
            print("INCONCLUSIVE: tracked snapshot inputs changed during audit", file=sys.stderr)
            return 2
    print("Snapshot pre/post stable; only private temporary test inputs were written.", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
