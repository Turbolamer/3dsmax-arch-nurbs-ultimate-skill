#!/usr/bin/env python3
"""Read-only admission adapter for the bounded P3.1 standalone wall emitter.

API: load_inputs(project_dir, *, namespace, system_type, system_scale) returns a
dict containing walls, dimensions, run, block, openings, stations and expected
units, plus raw input_snapshots/input_hashes/input_sources and validator findings.
Call verify_inputs_unchanged(result) immediately before publication. That is an
observed-drift check under a local single-writer model, NOT an immutable lock.
The dict's callable result['verify_inputs_unchanged']() is the same check.

All accepted-validator reads run against one private raw-byte snapshot. No JSON
rewrites, formula eval/exec, source writes, assembly production or Max access.
Direction authority, final geometry precision/topology, publication and replay
belong to the orchestrator/geometry module, not this adapter.
"""
from __future__ import annotations

import copy
import hashlib
import math
import os
import re
import struct
import tempfile
import threading
from pathlib import Path
from typing import Any

try:
    from . import scene_units, validate_specs as validator
except ImportError:  # sibling import by a directly executed builder
    import scene_units
    import validate_specs as validator


MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_OPENINGS = 6
INPUT_NAMES = frozenset((*validator.WALL_UPSTREAM_SPECS, "walls", "assumptions",
                         "conflicts_resolved", "assembly"))
PROJECT_ARTIFACT_NAMES = ("wall_surface.json", "wall_surface.ms")
NAMESPACE_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,39}\Z", re.ASCII)
_VALIDATOR_LOCK = threading.RLock()


class InputRefusal(ValueError):
    """Invalid, unsupported, incomplete or observably changed consumed input."""

def _refuse(message: str) -> None:
    raise InputRefusal(message)


def _artifact_presence(root: Path) -> dict[str, bool]:
    """Snapshot reserved output presence, including dirs and dangling links.

    Include the not-yet-created pipeline boundary too, so a late artifact there
    cannot disappear from inventory merely because the directory was absent at
    admission. No existing artifact is parsed/imported by this initial subset.
    """
    directories = (root, root.parent) if root.name == "pipeline" else (root, root / "pipeline")
    presence = {}
    for directory in directories:
        for name in PROJECT_ARTIFACT_NAMES:
            path = directory / name
            try:
                path.lstat()
            except FileNotFoundError:
                presence[str(path)] = False
            except OSError as exc:
                raise InputRefusal(f"cannot inspect project wall artifact {path}: {exc}") from exc
            else:
                presence[str(path)] = True
    return presence


def _require_no_project_artifacts(presence: dict[str, bool]) -> None:
    existing = [path for path, present in presence.items() if present]
    if existing:
        _refuse("existing project wall artifact unsupported; previous-output import is not supported: "
                + "; ".join(existing))


def _inventory(root: Path) -> dict[str, Path]:
    """Same parent/pipeline boundary as the accepted validator; no recursive scan."""
    directories = [root]
    if root.name == "pipeline":
        directories.append(root.parent)
    elif (root / "pipeline").exists():
        directories.append(root / "pipeline")
    found: dict[str, Path] = {}
    for directory in directories:
        if directory.is_symlink() or not directory.is_dir() or directory.resolve() != directory:
            _refuse(f"input directory must be a real directory: {directory}")
        for name in sorted(INPUT_NAMES):
            path = directory / (name + ".json")
            if not path.exists() and not path.is_symlink():
                continue
            if name in found:
                _refuse(f"ambiguous duplicate {name}.json at parent/pipeline boundary")
            if path.is_symlink() or not path.is_file() or path.resolve() != path:
                _refuse(f"input must be a regular non-symlink file: {path}")
            found[name] = path
    return found


def _read_bounded(path: Path) -> bytes:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_JSON_BYTES + 1)
    except OSError as exc:
        raise InputRefusal(f"cannot read input {path}: {exc}") from exc
    if len(raw) > MAX_JSON_BYTES:
        _refuse(f"JSON input exceeds 2 MiB: {path}")
    return raw


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _temporary_parent() -> str | None:
    approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
    return str(approved) if os.name == "nt" and approved.is_dir() else None


def _allowed_skip(finding: Any, session: Any) -> bool:
    """Exact reviewed non-input/NOT_APPLICABLE cases; no blanket rule waiver."""
    rule, detail = finding.rule, finding.detail
    if (rule in {"G-95", "G-98", "G-99", "G-100"}
            and finding.location == "wall pipeline"
            and detail == "JSON lint cannot verify emitted script, manifest or live Max; output/runtime gate pending"):
        return True
    if rule == "G-16" and detail == "07 declares no numeric range for this file; a key with no declared range is unbounded":
        return True
    if rule == "G-21" and detail in {
        "no sibling *_ccw flag exists for this ring in 07 section 5.7, so the declared winding cannot be confirmed; ring is CCW",
        "no sibling *_ccw flag exists for this ring in 07 section 5.7, so the declared winding cannot be confirmed; ring is CW",
    }:
        return True  # no wall sign claim is inferred from core winding
    if rule == "G-91" and detail == "No stepped floor_plates[].footprint_cm or facades[].spans_level_indices declared":
        return True
    if (rule, detail) in {
        ("G-26", "openings is empty; nothing to test (07 section 5.11 allows it)"),
        ("G-27", "openings is empty; nothing to fit"),
        ("G-28", "openings is empty; nothing to collide"),
    }:
        return True  # dimensions openings are independent of rough wall openings
    if rule == "G-86" and detail in {
        "schema_version 1.0; form_references/precision_targets not present",
        "schema_version 1.1 without analytical form targets; form_references not present",
    }:
        return True
    if rule in {"G-87", "G-88", "G-89", "G-90"} and detail == "qa.json is absent; QA configuration has not been scaffolded or run":
        return True
    if rule == "G-92" and detail == "poly_surface_shell_v1 selected; assembly is absent or a draft placeholder, echo incomplete":
        return True
    if rule == "G-96" and detail in {
        "assembly absent or empty draft; route exclusivity incomplete; output manifest wall_surface.json is missing",
        "static route mixing checks passed; output manifest wall_surface.json is missing, and full exclusivity awaits the P3 manifest contract (not an input-build precondition)",
    }:
        return True
    if rule == "G-1":
        if (finding.location, detail) in {
            ("assembly.json", "poly assembly output is not produced; G-92/G-96 remain incomplete, but it is not a wall-input precondition"),
            ("assembly.json", "poly_surface_shell_v1 assembly output is not produced; G-92/G-96 remain incomplete, but it is not a wall-input precondition"),
            ("assembly.json", "closed_inner_contour_shell_v2 assembly output is not produced; G-92/G-96 remain incomplete, but it is not a wall-input precondition"),
            ("qa.json", "absent; earlier stage / legacy project before S7/P8 QA gate (07 S-4)"),
            ("materials.json", "absent; 07 section 4 marks it reserved (owner P7), so no builder reads it yet"),
            ("export.json", "absent; 07 section 4 marks it reserved (owner P9), so no builder reads it yet"),
        }:
            return True
    # The following describe unused variant/generator declarations or a future
    # stage's emitted/runtime census. Exact signatures, never arbitrary SKIPs.
    if rule == "G-69" and re.fullmatch(
        r"every one of the \d+ component\(s\) declares an empty variants array, so nothing about a variant can be checked; the generated registry declares none, and saying the rule is unexercised is better than a vacuous PASS \(07 section 9\.6\)", detail):
        return True
    if rule in {"G-84", "G-85"} and detail == "no section declares generator; compatibility skip (generator optional)":
        return True
    if rule == "G-54" and detail == (
        "not evaluable at lint time. G-54 counts the NURBSSurface sub-objects of the "
        "committed node, and a commit happens only inside 3ds Max: the dependent surfaces "
        "this census exists to catch are silently dropped there, with no error and no "
        "warning, so nothing in this file can observe whether one survived. Enforced at "
        "build time instead, by the emitted .ms counting the sub-objects after NURBSNode "
        "and throwing on a mismatch. A check that cannot be evaluated reports SKIP with "
        "its reason, never a silent PASS."):
        return True
    if rule == "G-70" and detail == (
        "not evaluable at lint time. G-70 is a census of facade_table.csv and world_table.csv, "
        "and a static JSON file cannot observe a CSV it did not write: the row count, the "
        "reference resolution and the rot_z_deg of every instance are all properties of the "
        "emitted tables, not of this document. Enforced at build time instead, by "
        "scripts/facade_tables.py asserting facade_table_census() -- the same function this "
        "module defines -- on the files it has just written, and refusing on a mismatch. A "
        "check that cannot be evaluated reports SKIP with its reason, never a silent PASS "
        "(07 section 9.6)"):
        return True
    if session.assembly is not None and validator._empty_assembly_draft(session.assembly.doc):
        if (rule in validator.ASSEMBLY_DRAFT_RULES and finding.location == session.assembly.label
                and detail.startswith('status=draft is not "locked"; 07 section 9.9 does not evaluate a draft file, because ')
                and "This stub is empty as well" in detail
                and detail.endswith("where it will fail.")):
            return True
        if rule == "G-4" and finding.location == session.assembly.label and detail == "status=draft; allowed by --allow-draft":
            return True
        if rule == "G-92" and detail == "poly_surface_shell_v1 selected, but assembly.json envelope/hygiene or locked-status checks failed or are incomplete":
            return True  # empty draft G-4 is SKIP, never waived envelope FAIL
    return False


def _run_validator(session: Any, report: Any) -> None:
    # Accepted envelope checks use module globals, not only Session attributes.
    # Scope and restore those globals under a lock; do not alter accepted code.
    with _VALIDATOR_LOCK:
        previous = validator.session_build_gate, validator.session_allow_draft
        try:
            validator.session_build_gate = True
            # Only an actual empty assembly draft is allowed below. Required
            # source status is checked explicitly and cannot use this exception.
            validator.session_allow_draft = True
            session.build_gate = True
            session.allow_draft = False
            validator.run_checks(session, report)
        finally:
            validator.session_build_gate, validator.session_allow_draft = previous


def _require_pass(report: Any, record: Any, rules: tuple[str, ...]) -> None:
    for rule in rules:
        if not any(f.rule == rule and f.severity == "PASS" and f.location == record.label
                   for f in report.findings):
            _refuse(f"required input gate has no PASS: {rule} {record.label}")


def _required_formulas(session: Any, report: Any) -> None:
    """Use accepted formula functions only, including the implicit contour root.

    Transitive provenance validation stays in the accepted validator. This walk
    only prevents a reached derived input with *no recomputation* from admission.
    Other stage validators can check geometry but are not arbitrary formula VMs.
    """
    wall = session.walls
    contour, reason = validator._wall_contour(wall.doc["wall_runs"][0]["contour_ref"], session)
    if contour is None:
        _refuse(reason)
    index = session.dimensions.doc["facades"].index(contour)
    pending = [(session.dimensions, f"facades[{index}]")]
    upstream = validator._wall_upstream(wall, session, report)
    for source in wall.doc["origin_inputs"]:
        owner, reason = validator._wall_checked_source(source, wall, session, report)
        if owner is None:
            _refuse(f"required source provenance refused: {reason}")
        pending.append((owner, source))
    seen: set[tuple[str, str]] = set()
    while pending:
        record, path = pending.pop()
        if (record.name, path) in seen:
            continue
        seen.add((record.name, path))
        owner, reason = validator._wall_checked_source(path, wall, session, report)
        if owner is None or owner.name != record.name:
            _refuse(f"required source provenance refused: {record.name}::{path}: {reason}")
        origins = record.doc.get("origins", {})
        for entry, origin in origins.items():
            if not validator._wall_paths_overlap(path, entry) or origin.get("origin") != "derived":
                continue
            key = (record.name, "<formula>" + entry)
            if key in seen:
                continue
            seen.add(key)
            formula_report = validator.Report(warnings_as_errors=True)
            validator.check_derived_recompute(record, session, [(entry, origin)], formula_report)
            rows = formula_report.findings
            if (not any(f.severity == "PASS" for f in rows)
                    or any(f.severity != "PASS" for f in rows)):
                detail = "; ".join(f"{f.rule} {f.severity}: {f.detail}" for f in rows)
                _refuse(f"required derived formula unavailable/failed: {record.name}.json::{entry}: {detail or 'no documented recomputation'}")
            for source in origin["derives_from"]:
                if validator._wall_path(source, record.doc):
                    selected = record
                else:
                    allowed = validator.WALL_TRACE_UPSTREAM[record.name]
                    selected = validator._wall_source(source, [r for r in upstream if r.name in allowed])
                if selected is None:
                    _refuse(f"required formula input does not resolve: {record.name}::{source}")
                pending.append((selected, source))
        for source in record.doc.get("origin_inputs", []):
            allowed = validator.WALL_TRACE_UPSTREAM[record.name]
            selected = validator._wall_source(source, [r for r in upstream if r.name in allowed])
            if selected is None:
                _refuse(f"required stage input does not resolve: {record.name}::{source}")
            pending.append((selected, source))


def _stations(values: list[float], epsilon: float, axis: str) -> list[float]:
    stations = sorted(set(values))  # only exact equality, no rounding or snapping
    if any(hi - lo < epsilon for lo, hi in zip(stations, stations[1:])):
        _refuse(f"distinct {axis} stations are closer than numeric_epsilon_cm")
    return stations


def _f32(value: float, label: str) -> float:
    try:
        result = struct.unpack("<f", struct.pack("<f", value))[0]
    except (OverflowError, struct.error) as exc:
        raise InputRefusal(f"Max Float32 range exceeded: {label}") from exc
    if not math.isfinite(result):
        _refuse(f"Max Float32 range exceeded: {label}")
    return result


def _normalise(walls: dict, units: dict) -> dict:
    if len(walls["blocks"]) != 1 or len(walls["wall_runs"]) != 1 or walls["upper_returns"]:
        _refuse("bounded whole-project subset requires exactly one block, one wall run and upper_returns=[]")
    if any(value.get("origin") != "given" for value in walls["origins"].values()):
        _refuse("P3.1 requires given-only wall origins; wall-local derived/ledger oracles are not implemented")
    run, block = walls["wall_runs"][0], walls["blocks"][0]
    if run["block_id"] != block["id"]:
        _refuse("sole wall run must link the sole block")
    start, end = run["start_cm"], run["end_cm"]
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    height = run["top_z_cm"] - run["base_z_cm"]
    thickness = run["thickness_cm"]
    tangent = [dx / length, dy / length]
    normal = [-tangent[1], tangent[0]]
    if sum(a * b for a, b in zip(normal, run["outward"])) < 0:
        normal = [-value for value in normal]
    openings = sorted(copy.deepcopy(walls["openings"]), key=lambda item: (item["u_range_cm"], item["id"]))
    if len(openings) > MAX_OPENINGS:
        _refuse("bounded wall supports at most 6 openings")
    us, vs = [0.0, length], [0.0, height]
    previous_hi = None
    for op in openings:
        lo, hi = op["u_range_cm"]
        sill, head = op["sill_cm"], op["head_cm"]
        if op["wall_run_id"] != run["id"]:
            _refuse("every opening must link the sole wall run")
        if not 0 < lo < hi < length:
            _refuse("opening u requires strict 0 < lo < hi < run length")
        if not 0 <= sill < head < height:
            _refuse("opening v requires 0 <= sill < head < run height")
        if previous_hi is not None and lo <= previous_hi:
            _refuse("opening u intervals must be strictly disjoint; touching is unsupported")
        previous_hi = hi
        us.extend([lo, hi])
        vs.extend([sill, head])
    epsilon = walls["numeric_epsilon_cm"]
    if thickness < epsilon:
        _refuse("wall thickness is below numeric_epsilon_cm")
    u_stations = _stations(us, epsilon, "u")
    v_stations = _stations(vs, epsilon, "v")
    if len(u_stations) * len(v_stations) > 64 or (len(u_stations) - 1) * (len(v_stations) - 1) > 32:
        _refuse("bounded planning grid exceeds 64 vertices or 32 polygons")
    # Early, conservative storage checks only. Geometry must still check all
    # mapped vertices, shared IDs and final Shell evaluation independently.
    factor = units["scene_units_per_cm"]
    for axis, stations in (("u", u_stations), ("v", v_stations)):
        rounded = [_f32(value * factor, axis) for value in stations]
        if any(a >= b for a, b in zip(rounded, rounded[1:])):
            _refuse(f"Max Float32 collapses distinct {axis} stations")
    mapped_points: set[tuple[float, ...]] = set()
    for u in u_stations:
        for v in v_stations:
            for depth in (0.0, thickness):
                point = [start[0] + tangent[0] * u + normal[0] * depth,
                         start[1] + tangent[1] * u + normal[1] * depth,
                         run["base_z_cm"] + v]
                mapped = []
                for coordinate in point:
                    native = coordinate * factor
                    rounded = _f32(native, "mapped wall vertex")
                    error = abs(rounded / factor - coordinate)
                    if not math.isfinite(error) or error > epsilon:
                        _refuse("Max Float32 mapped vertex error exceeds numeric_epsilon_cm")
                    mapped.append(rounded)
                if tuple(mapped) in mapped_points:
                    _refuse("Max Float32 collapses distinct mapped wall vertices")
                mapped_points.add(tuple(mapped))
    for value in (length, height, thickness, length * height, length * height * thickness):
        if not math.isfinite(value) or value <= 0:
            _refuse("wall derived length/area/volume is non-finite or non-positive")
    return {"run": copy.deepcopy(run), "block": copy.deepcopy(block), "openings": openings,
            "length_cm": length, "height_cm": height, "tangent": tangent,
            "geometric_outward": normal, "declared_outward": copy.deepcopy(run["outward"]),
            "u_stations_cm": u_stations, "v_stations_cm": v_stations}


def verify_inputs_unchanged(inputs: dict[str, Any]) -> None:
    """Refuse observed source/membership/path drift; successful check returns None.

    Use immediately before publication. No immutable filesystem handle, race-free
    guarantee or protection from a concurrent change *after* this check is claimed.
    """
    root = Path(inputs["project_dir"])
    if root.resolve() != root or not root.is_dir() or root.is_symlink():
        _refuse("project directory changed since snapshot")
    presence = _artifact_presence(root)
    _require_no_project_artifacts(presence)
    if presence != inputs["project_artifact_presence"]:
        _refuse("project wall artifact presence changed since snapshot")
    current = _inventory(root)
    expected = inputs["input_sources"]
    if set(current) != set(expected) or any(str(current[name]) != expected[name] for name in current):
        _refuse("input source membership/path changed since snapshot")
    for name, path in current.items():
        if _digest(_read_bounded(path)) != inputs["input_hashes"][name + ".json"]:
            _refuse(f"input changed since snapshot: {name}.json")


def load_inputs(project_dir: str | Path, *, namespace: str, system_type: str,
                system_scale: float) -> dict[str, Any]:
    """Snapshot, validate and normalize the entire bounded wall declaration.

    project_dir is the actual spec directory or its immediate pipeline parent;
    canonical absolute path is returned. Expected scene units and namespace are
    mandatory operational parameters, never read from/invented in wall specs.
    May raise InputRefusal; creates/deletes only a private temporary snapshot.
    """
    if not isinstance(namespace, str) or not NAMESPACE_RE.fullmatch(namespace):
        _refuse("namespace must match ASCII [A-Za-z][A-Za-z0-9_]{0,39}")
    if not isinstance(system_type, str) or system_type not in scene_units.SYSTEM_TYPE_FACTORS:
        _refuse("system_type must be an exact certified lowercase type, without # or whitespace")
    try:
        c, factor = scene_units.unit_factor(system_type, system_scale)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise InputRefusal(f"invalid expected scene units: {exc}") from exc
    if not all(math.isfinite(x) and x > 0 for x in (c, factor)):
        _refuse("expected unit factors must be finite and positive")
    units = {"system_type": system_type, "system_scale": float(system_scale),
             "cm_per_scene_unit": c, "scene_units_per_cm": factor}
    try:
        root = Path(project_dir).resolve(strict=True)
    except (OSError, ValueError, TypeError) as exc:
        raise InputRefusal(f"invalid project directory: {exc}") from exc
    if not root.is_dir():
        _refuse("project_dir must be a directory, not a selected wall file")
    artifact_presence = _artifact_presence(root)
    _require_no_project_artifacts(artifact_presence)
    sources = _inventory(root)
    if not {"walls", "dimensions"}.issubset(sources):
        _refuse("walls.json and dimensions.json are required")
    snapshots = {}
    total = 0
    for name, path in sources.items():
        raw = _read_bounded(path)
        total += len(raw)
        if total > MAX_SOURCE_BYTES:
            _refuse("total consumed source exceeds 16 MiB")
        snapshots[name + ".json"] = raw
    result: dict[str, Any] = {
        "project_dir": str(root), "namespace": namespace, "expected_units": units,
        "input_snapshots": snapshots,
        "input_hashes": {name: _digest(raw) for name, raw in snapshots.items()},
        "input_sources": {name: str(path) for name, path in sources.items()},
        "project_artifact_presence": artifact_presence,
    }
    with tempfile.TemporaryDirectory(prefix="p3-wall-inputs-", dir=_temporary_parent()) as temporary:
        private = Path(temporary)
        for name, raw in snapshots.items():
            (private / name).write_bytes(raw)
        report = validator.Report(warnings_as_errors=True)
        session = validator.load_session(sorted(private.glob("*.json")), private, report)
        for record in session.files:
            if record.fatal or record.hygiene:
                _refuse(f"strict input parse/hygiene refused {record.label}: {record.fatal or record.hygiene}")
            if not isinstance(record.doc, dict):
                _refuse(f"input must be a JSON object: {record.label}")
            if record.name == "assembly" and validator._empty_assembly_draft(record.doc):
                continue
            if record.doc.get("status") != "locked":
                _refuse(f"required input must be locked: {record.label}")
        if session.walls.doc.get("wall_technique") != validator.POLY_WALL_ROUTE:
            _refuse("explicit poly_surface_shell_v1 selector required")
        if session.walls.doc.get("reference_face") != "inner":
            _refuse("only inner-reference walls are supported")
        _run_validator(session, report)
        # Inventory completeness describes the entire S1-S7 pipeline, not this
        # standalone emitter. Missing optional upstreams are permitted only if
        # all *reached* provenance/formula checks below still pass.
        missing_upstream = {name + ".json" for name in validator.WALL_UPSTREAM_SPECS
                            if name != "dimensions" and session.by_name(name) is None}
        excluded_inventory = [f for f in report.findings
                              if f.rule == "G-1" and f.severity == "FAIL"
                              and f.location in missing_upstream
                              and f.detail.startswith("absent; 07 section 4 marks it defined")]
        failures = [f for f in report.findings if f.severity in {"FAIL", "WARN"}
                    and not (f.rule == "G-1" and f.location in missing_upstream
                             and f.detail.startswith("absent; 07 section 4 marks it defined"))]
        if failures:
            _refuse("input validator refused: " + "; ".join(f"{f.rule} {f.location}: {f.detail}" for f in failures))
        _require_pass(report, session.walls, ("G-1", "G-2", "G-3", "G-4", "G-5", "G-6", "G-7", "G-9", "G-10", "G-93", "G-94", "G-97"))
        _require_pass(report, session.dimensions, ("G-1", "G-2", "G-3", "G-4", "G-5", "G-6", "G-7", "G-9", "G-10", "G-31"))
        _required_formulas(session, report)
        unapproved = [f for f in report.findings if f.severity == "SKIP" and not _allowed_skip(f, session)]
        if unapproved:
            _refuse("unverified input gate: " + "; ".join(f"{f.rule} {f.location}: {f.detail}" for f in unapproved))
        walls, dimensions = copy.deepcopy(session.walls.doc), copy.deepcopy(session.dimensions.doc)
        result.update(_normalise(walls, units))
        result.update({"project": walls["project"], "walls": walls, "dimensions": dimensions,
                       "validation_findings": [vars(f).copy() for f in report.findings],
                       "excluded_inventory_findings": [vars(f).copy() for f in excluded_inventory],
                       "allowed_skips": [vars(f).copy() for f in report.findings if f.severity == "SKIP"]})
    verify_inputs_unchanged(result)
    result["verify_inputs_unchanged"] = lambda: verify_inputs_unchanged(result)
    return result
