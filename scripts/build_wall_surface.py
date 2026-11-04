#!/usr/bin/env python3
"""Bounded, offline-only P3.1 wall emitter; never executes Max or source text.

The input adapter validates one private byte snapshot; the runtime plans and emits
from those documents. This coordinator independently checks operational authority,
units, source/code hashes and publication boundaries. No draft/force modes exist.
Exit 0 means produced_offline_unverified, NOT accepted live geometry.

Integration: load_inputs(Path, namespace=..., system_type=..., system_scale=...)
-> mapping walls, dimensions, input_snapshots, input_hashes, input_sources;
verify_inputs_unchanged(snapshot). Hash keys are source basenames; source mapping
keys are source stems and values are original absolute paths.
Runtime: build_plan(walls, dimensions), generate_script(plan, identity, namespace,
expected_units), with expected_units keys system_type, system_scale, cm_per_unit,
units_per_cm. Publisher: publish_new_directory(Path, {name: bytes}) -> hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from types import ModuleType
from typing import Any, Mapping, Sequence

try:
    from .scene_units import SYSTEM_TYPE_FACTORS, unit_factor
    from .validate_specs import strict_json_loads
except ImportError:  # direct CLI invocation
    from scene_units import SYSTEM_TYPE_FACTORS, unit_factor
    from validate_specs import strict_json_loads


AUTHORITY_KEYS = frozenset({
    "schema_version", "project", "wall_run_id", "walls_sha256", "source_file",
    "source_sha256", "source_location", "inner_start_cm", "inner_end_cm",
    "base_z_cm", "top_z_cm", "outward",
})
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_ARTIFACT_BYTES = 2 * 1024 * 1024
REPOSITORY_ROOT = Path(__file__).absolute().parent.parent
CONTRACT_PATH = REPOSITORY_ROOT / "references" / "10-wall-generation-pipeline.md"
SUBSET = "single_standalone_straight_inner_wall"
ROUTE = "poly_surface_shell_v1"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_NAMESPACE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,39}\Z", re.ASCII)
_SCALE = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z", re.ASCII)
_RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?\Z", re.I | re.ASCII)


class BuildRefusal(ValueError):
    """A bounded request cannot be safely emitted/published."""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: Any) -> bytes:
    """Deterministic operational JSON; no timestamps or circular file hashes."""
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                           separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise BuildRefusal(f"non-JSON or non-finite artifact metadata: {exc}") from exc


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BuildRefusal(f"{label} must be a finite JSON number")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise BuildRefusal(f"{label} must be finite") from exc
    if not math.isfinite(number):
        raise BuildRefusal(f"{label} must be finite")
    return number


def _pair(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        raise BuildRefusal(f"{label} must be an array of exactly two finite numbers")
    return [_number(x, f"{label}[{i}]") for i, x in enumerate(value)]


def _text(value: Any, label: str) -> str:
    if (not isinstance(value, str) or not value or value != value.strip()
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise BuildRefusal(f"{label} must be a nonempty unambiguous string")
    return value


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise BuildRefusal(f"{label} must be lowercase SHA-256 (64 hex characters)")
    return value


def validate_namespace(value: str) -> str:
    if not isinstance(value, str) or _NAMESPACE.fullmatch(value) is None:
        raise BuildRefusal("namespace must match ASCII [A-Za-z][A-Za-z0-9_]{0,39}")
    return value


def expected_units(system_type: str, system_scale: str | int | float) -> dict[str, Any]:
    """Exact type spelling and strict JSON scale; never normalize an alias."""
    if not isinstance(system_type, str) or system_type not in SYSTEM_TYPE_FACTORS:
        raise BuildRefusal("system-type must be an exact certified lowercase SystemType")
    if isinstance(system_scale, str):
        if len(system_scale) > 1024 or _SCALE.fullmatch(system_scale) is None:
            raise BuildRefusal("system-scale must be one unambiguous positive JSON number")
        try:
            system_scale = strict_json_loads(system_scale)
        except (ValueError, RecursionError) as exc:
            raise BuildRefusal(f"invalid system-scale: {exc}") from exc
    scale = _number(system_scale, "system-scale")
    if scale <= 0:
        raise BuildRefusal("system-scale must be positive")
    try:
        c, factor = unit_factor(system_type, scale)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise BuildRefusal(f"invalid system-scale factor: {exc}") from exc
    if not all(math.isfinite(x) and x > 0 for x in (c, factor)):
        raise BuildRefusal("expected unit conversion must be finite and positive")
    return {"system_type": system_type, "system_scale": scale,
            "cm_per_unit": c, "units_per_cm": factor}


def _path_spelling(value: str | Path, label: str) -> Path:
    raw = _text(os.fspath(value), label)
    normalized = raw.replace("\\", "/")
    # The first release is local-only. UNC, device and extended-path aliases are
    # not silently converted into ostensibly ordinary local paths.
    if normalized.startswith("//"):
        raise BuildRefusal(f"{label}: network/device/extended paths are unsupported")
    drive = re.match(r"^[A-Za-z]:", normalized)
    if drive:
        if len(normalized) < 3 or normalized[2] != "/":
            raise BuildRefusal(f"{label}: drive-relative path is ambiguous")
        normalized = normalized[2:]
    for part in normalized.split("/"):
        if not part:
            continue
        if (part in (".", "..") or part.endswith((" ", "."))
                or any(c in part for c in ':<>"|?*') or _RESERVED.fullmatch(part)):
            raise BuildRefusal(f"{label}: ambiguous/traversing path component {part!r}")
    return Path(os.path.abspath(raw))


def safe_path(value: str | Path, label: str, *, exists: bool = True,
              directory: bool = False) -> Path:
    """Reject links/reparse points in the entire spelling, before resolution.

    This is an observed-state boundary, not a hostile-writer filesystem lock.
    """
    path = _path_spelling(value, label)
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            if ancestor != path:
                raise BuildRefusal(f"{label}: parent does not exist: {ancestor}")
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise BuildRefusal(f"{label}: links/junctions/reparse points are refused: {ancestor}")
        if ancestor != path and not stat.S_ISDIR(info.st_mode):
            raise BuildRefusal(f"{label}: parent is not a directory: {ancestor}")
    present = os.path.lexists(path)
    if exists and not present:
        raise BuildRefusal(f"{label}: path does not exist: {path}")
    if not exists and present:
        raise BuildRefusal(f"{label}: output must not exist: {path}")
    if exists:
        info = path.stat()
        wanted = stat.S_ISDIR if directory else stat.S_ISREG
        if not wanted(info.st_mode):
            raise BuildRefusal(f"{label}: expected {'directory' if directory else 'regular file'}: {path}")
        if not directory and info.st_nlink != 1:
            raise BuildRefusal(f"{label}: hard-linked source is refused: {path}")
    return path


def _read_bytes(path: Path, limit: int, label: str) -> bytes:
    safe_path(path, label)
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise BuildRefusal(f"{label}: exceeds {limit} byte ceiling")
    safe_path(path, label)
    return raw


def _json_bytes(raw: bytes, label: str) -> Any:
    if len(raw) > MAX_JSON_BYTES:
        raise BuildRefusal(f"{label}: JSON exceeds 2 MiB")
    try:
        return strict_json_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise BuildRefusal(f"{label}: strict JSON refused: {exc}") from exc


def check_authority(record: Any, walls: Mapping[str, Any], walls_hash: str) -> dict[str, Any]:
    """Closed attestation vs independent wall values; no tolerance/sign laundering."""
    if not isinstance(record, dict) or set(record) != AUTHORITY_KEYS:
        missing = AUTHORITY_KEYS - set(record) if isinstance(record, dict) else AUTHORITY_KEYS
        extra = set(record) - AUTHORITY_KEYS if isinstance(record, dict) else set()
        raise BuildRefusal(f"direction authority is closed: missing {sorted(missing)}, extra {sorted(extra)}")
    if record["schema_version"] != "p3-direction-authority-1":
        raise BuildRefusal("direction authority schema_version must be p3-direction-authority-1")
    for key in ("project", "wall_run_id", "source_file", "source_location"):
        _text(record[key], f"authority.{key}")
    for key in ("walls_sha256", "source_sha256"):
        _digest(record[key], f"authority.{key}")
    if record["walls_sha256"] != _digest(walls_hash, "actual walls hash"):
        raise BuildRefusal("direction authority walls_sha256 does not match exact wall bytes")
    if record["project"] != walls.get("project"):
        raise BuildRefusal("direction authority project conflicts with walls")
    runs = walls.get("wall_runs")
    if not isinstance(runs, list) or len(runs) != 1 or not isinstance(runs[0], dict):
        raise BuildRefusal("UNSUPPORTED_SCOPE: authority requires exactly one complete wall run")
    run = runs[0]
    if record["wall_run_id"] != run.get("id"):
        raise BuildRefusal("direction authority wall_run_id conflicts with walls")
    for authority_key, wall_key in (("inner_start_cm", "start_cm"),
                                    ("inner_end_cm", "end_cm"), ("outward", "outward")):
        attested = _pair(record[authority_key], f"authority.{authority_key}")
        declared = _pair(run.get(wall_key), f"wall.{wall_key}")
        if attested != declared:
            raise BuildRefusal(f"direction authority {authority_key} conflicts with independently read wall.{wall_key}")
    for key in ("base_z_cm", "top_z_cm"):
        if _number(record[key], f"authority.{key}") != _number(run.get(key), f"wall.{key}"):
            raise BuildRefusal(f"direction authority {key} conflicts with independently read wall.{key}")
    if _number(record["top_z_cm"], "authority.top_z_cm") <= _number(record["base_z_cm"], "authority.base_z_cm"):
        raise BuildRefusal("direction authority top_z_cm must exceed base_z_cm")
    return dict(record)


def load_authority(path: str | Path, walls: Mapping[str, Any], walls_hash: str
                   ) -> tuple[dict[str, Any], dict[str, str]]:
    authority_path = safe_path(path, "direction authority")
    raw = _read_bytes(authority_path, MAX_JSON_BYTES, "direction authority")
    authority = check_authority(_json_bytes(raw, "direction authority"), walls, walls_hash)
    source_path = authority_source_path(authority)
    source_raw = _read_bytes(source_path, MAX_SOURCE_BYTES, "direction source")
    if source_path == authority_path:
        raise BuildRefusal("direction authority cannot attest itself as its independent source")
    if sha256(source_raw) != authority["source_sha256"]:
        raise BuildRefusal("direction authority source_sha256 does not match actual source bytes")
    return authority, {str(authority_path): sha256(raw), str(source_path): sha256(source_raw)}


def authority_source_path(authority: Mapping[str, Any]) -> Path:
    """Relative source_file is based ONLY on process CWD, never searched.

    The raw token remains in the closed authority; the manifest separately records
    its resolved local path. For F01 invoke the CLI from the repository root.
    """
    return _path_spelling(authority["source_file"], "direction source")


def _member(value: Any, key: str) -> Any:
    return value.get(key) if isinstance(value, Mapping) else getattr(value, key, None)


def _hash_mapping(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise BuildRefusal(f"{label} must map actual absolute input paths to SHA-256")
    hashes: dict[str, str] = {}
    folded: set[str] = set()
    for key, digest in value.items():
        if not isinstance(key, str) or not Path(key).is_absolute():
            raise BuildRefusal(f"{label}: path must be absolute")
        path = safe_path(key, label)
        normalized = str(path)
        collision = normalized.casefold()
        if collision in folded:
            raise BuildRefusal(f"{label}: ambiguous duplicate path: {normalized}")
        folded.add(collision)
        hashes[normalized] = _digest(digest, label)
    return dict(sorted(hashes.items()))


def snapshot_hashes(snapshot: Any) -> dict[str, str]:
    """Bind adapter's parsed documents to its exact snapshotted source bytes."""
    hashes = _member(snapshot, "input_hashes")
    sources = _member(snapshot, "input_sources")
    snapshots = _member(snapshot, "input_snapshots")
    if not all(isinstance(value, Mapping) and value for value in (hashes, sources, snapshots)):
        raise BuildRefusal("input adapter must expose source paths, byte snapshots and hashes")
    if set(hashes) != set(snapshots) or set(hashes) != {name + ".json" for name in sources}:
        raise BuildRefusal("input adapter source/snapshot/hash membership disagrees")
    absolute = {}
    total = 0
    for stem, filename in sources.items():
        if not isinstance(stem, str) or not isinstance(filename, str):
            raise BuildRefusal("input source mapping must use string stems and paths")
        name = stem + ".json"
        if Path(filename).name != name:
            raise BuildRefusal("input source path/basename identity mismatch")
        raw = snapshots[name]
        if not isinstance(raw, bytes):
            raise BuildRefusal("input snapshot must contain raw bytes, not rewritten JSON")
        total += len(raw)
        if total > MAX_SOURCE_BYTES:
            raise BuildRefusal("total input snapshot exceeds 16 MiB")
        digest = _digest(hashes[name], "input snapshot hash")
        if sha256(raw) != digest:
            raise BuildRefusal(f"input snapshot byte/hash mismatch: {name}")
        parsed = _json_bytes(raw, name)
        if stem in ("walls", "dimensions") and canonical_json(parsed) != canonical_json(_member(snapshot, stem)):
            raise BuildRefusal(f"input snapshot differs from normalized source document: {name}")
        absolute[filename] = digest
    return _hash_mapping(absolute, "input hashes")


def verify_hashes(hashes: Mapping[str, str]) -> None:
    """Recheck original raw bytes under a controlled single-writer threat model."""
    total = 0
    for filename, digest in sorted(hashes.items()):
        path = safe_path(filename, "hashed input")
        limit = MAX_JSON_BYTES if path.suffix.lower() == ".json" else MAX_SOURCE_BYTES
        raw = _read_bytes(path, limit, "hashed input")
        total += len(raw)
        if total > MAX_SOURCE_BYTES:
            raise BuildRefusal("total consumed input/source bytes exceed 16 MiB")
        if sha256(raw) != digest:
            raise BuildRefusal(f"observed input/code drift: {filename}")


def _merge_hashes(*groups: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    spellings: dict[str, str] = {}
    for group in groups:
        for path, digest in group.items():
            folded = path.casefold()
            if folded in spellings and spellings[folded] != path:
                raise BuildRefusal(f"ambiguous source path spelling: {spellings[folded]} / {path}")
            spellings[folded] = path
            if path in result and result[path] != digest:
                raise BuildRefusal(f"conflicting source hashes: {path}")
            result[path] = digest
    return dict(sorted(result.items()))


def _overlaps(left: Path, right: Path) -> bool:
    a, b = str(left).casefold(), str(right).casefold()
    try:
        return os.path.commonpath((a, b)) in (a, b)
    except ValueError:  # disjoint local drives
        return False


def check_output_boundary(out_dir: str | Path, project_dir: Path,
                          input_paths: Sequence[str] = ()) -> Path:
    out = safe_path(out_dir, "output", exists=False)
    if _overlaps(out, project_dir):
        raise BuildRefusal("new output must be disjoint from the input project directory")
    for source in input_paths:
        if _overlaps(out, Path(source)):
            raise BuildRefusal(f"new output must not overlap a consumed source: {source}")
    return out


def _module(name: str) -> Any:
    return importlib.import_module(f"{__package__}.{name}" if __package__ else name)


def code_hashes(modules: Sequence[Any]) -> dict[str, str]:
    """Source identity includes coordinator, helpers, validator, units, contract.

    This follows the actual helper import closure, not unrelated modules a caller
    might previously have imported. Stdlib/interpreter bytes are
    not represented as an executable-environment reproducibility claim.
    """
    scripts = Path(__file__).absolute().parent
    paths = {Path(__file__).absolute(), CONTRACT_PATH}
    pending = [*modules, sys.modules.get(strict_json_loads.__module__),
               sys.modules.get(unit_factor.__module__)]
    seen: set[int] = set()
    while pending:
        module = pending.pop()
        if id(module) in seen:
            continue
        seen.add(id(module))
        filename = getattr(module, "__file__", None)
        if not filename:
            continue
        candidate = Path(filename).absolute()
        if candidate.suffix == ".py" and candidate.parent == scripts:
            paths.add(candidate)
            for value in vars(module).values():
                if isinstance(value, ModuleType):
                    pending.append(value)
                else:
                    # `from helper import function` still consumes helper bytes.
                    dependency = sys.modules.get(getattr(value, "__module__", ""))
                    if dependency is not None:
                        pending.append(dependency)
    return {str(path): sha256(_read_bytes(path, MAX_SOURCE_BYTES, "generator/contract source"))
            for path in sorted(paths, key=str)}


def check_input_paths(project: Path, adapter: Any) -> None:
    """Refuse reparse-based laundering before the adapter reads a private copy."""
    directories = [project]
    if project.name == "pipeline":
        directories.append(safe_path(project.parent, "input parent", directory=True))
    elif os.path.lexists(project / "pipeline"):
        directories.append(safe_path(project / "pipeline", "input pipeline", directory=True))
    names = getattr(adapter, "INPUT_NAMES", ())
    if not isinstance(names, (tuple, list, set, frozenset)):
        raise BuildRefusal("input adapter INPUT_NAMES must enumerate its bounded source inventory")
    for directory in directories:
        for stem in names:
            path = directory / (stem + ".json")
            if os.path.lexists(path):
                safe_path(path, "input source")


def _plan_metadata(plan: Any, namespace: str) -> tuple[dict[str, Any], list[str]]:
    predictions = _member(plan, "predictions")
    if not isinstance(predictions, Mapping) or not predictions:
        raise BuildRefusal("runtime plan must expose separately labelled predictions")
    predictions = dict(predictions)
    canonical_json(predictions)
    names = _member(plan, "node_names")
    if callable(names):
        names = names(namespace)
    if names is None:
        # Runtime's documented injective naming convention, not an invented
        # domain-spec node name. Kept explicit in the integration report.
        names = [namespace + "__wall"]
    if (not isinstance(names, (list, tuple)) or len(names) != 1
            or not isinstance(names[0], str)
            or not re.fullmatch(re.escape(namespace) + r"_[A-Za-z0-9_]{1,80}", names[0], re.ASCII)):
        raise BuildRefusal("runtime node_names must expose exactly one safe namespaced node")
    return predictions, list(names)


def geometric_outward(run: Mapping[str, Any]) -> list[float]:
    """Exact segment perpendicular, signed by the separately attested declaration."""
    start, end = _pair(run.get("start_cm"), "wall.start_cm"), _pair(run.get("end_cm"), "wall.end_cm")
    declared = _pair(run.get("outward"), "wall.outward")
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if not math.isfinite(length) or length <= 0:
        raise BuildRefusal("wall segment length must be finite and positive")
    normal = [-dy / length, dx / length]
    dot = normal[0] * declared[0] + normal[1] * declared[1]
    if not math.isfinite(dot) or dot == 0:
        raise BuildRefusal("attested declaration cannot select a geometric outward sign")
    return normal if dot > 0 else [-normal[0], -normal[1]]


def make_artifacts(*, walls: Mapping[str, Any], plan: Any, authority: dict[str, Any],
                   input_hashes: Mapping[str, str], generator_hashes: Mapping[str, str],
                   namespace: str, units: dict[str, Any], runtime: Any) -> dict[str, bytes]:
    """In-memory deterministic pair; output path and wall-clock time are excluded."""
    validate_namespace(namespace)
    if walls.get("wall_technique") != ROUTE or walls.get("status") != "locked":
        raise BuildRefusal("only the explicit locked poly wall route can be emitted")
    runs = walls.get("wall_runs")
    if not isinstance(runs, list) or len(runs) != 1:
        raise BuildRefusal("UNSUPPORTED_SCOPE: complete single-run wall required")
    run = runs[0]
    predictions, names = _plan_metadata(plan, namespace)
    subset = _member(plan, "subset") or SUBSET
    if subset != SUBSET:
        raise BuildRefusal("runtime plan subset conflicts with P3.1 contract")
    identity_record = {
        "schema_version": "p3-wall-surface-identity-1", "project": walls.get("project"),
        "route": ROUTE, "subset": SUBSET, "namespace": namespace,
        "input_hashes": dict(input_hashes), "generator_hashes": dict(generator_hashes),
        "direction_authority": authority, "expected_units": units,
        "authority_source_resolution": {"base": "process_current_working_directory",
                                         "raw_token": authority["source_file"],
                                         "resolved_path": str(authority_source_path(authority))},
    }
    identity = sha256(canonical_json(identity_record))
    generated = runtime.generate_script(plan, identity, namespace, units)
    if isinstance(generated, str):
        script = generated.encode("utf-8")
    elif isinstance(generated, bytes):
        script = generated
    else:
        raise BuildRefusal("runtime generate_script must return UTF-8 str or bytes")
    try:
        script_text = script.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BuildRefusal("runtime script is not UTF-8") from exc
    if (not script or b"\r" in script or script.startswith(b"\xef\xbb\xbf")
            or not script.endswith(b"\n") or identity not in script_text):
        raise BuildRefusal("runtime script must contain canonical identity and use UTF-8/LF/final newline")
    manifest = {
        "schema_version": "p3-wall-surface-1", "spec": "wall_surface",
        "status": "produced_offline_unverified", "project": walls.get("project"),
        "route": ROUTE, "subset": SUBSET, "identity": identity,
        "owner": {"namespace": namespace, "id": identity},
        "input_hashes": dict(input_hashes), "generator_hashes": dict(generator_hashes),
        "direction_authority": authority,
        "direction_evidence": {
            "kind": "human_authored_source_attestation",
            "automated_semantic_source_proof": False,
            "source_file_base": "process_current_working_directory",
            "source_file_token": authority["source_file"],
            "resolved_source_file": str(authority_source_path(authority)),
            "declared_outward": run.get("outward"),
            "geometric_outward": geometric_outward(run),
        },
        "expected_units": units, "node_names": names,
        "declared_stack": [{"class": "Shell", "inner_amount_scene": 0.0,
                            "outer_amount_scene": _number(run.get("thickness_cm"), "wall.thickness_cm") * units["units_per_cm"],
                            "segments": 1, "enabled": True}],
        "declared_budgets": {run["id"]: run["topology_budget"]},
        "operational_planning_ceilings": {
            "grid_polygons": 32, "grid_vertices": 64, "evaluated_triangles": 256,
            "openings": 6, "created_nodes": 1, "modifiers": 1,
        },
        "initial_execution_admission": {
            "fixture": "F01", "grid_vertices": 24, "grid_polygons": 15,
            "evaluated_triangles": 96, "openings": 2,
            "live_calibrated": False, "scene_census_ceiling": 64,
        },
        "predictions": {"status": "offline_predictions_not_live_measurements", "values": predictions},
        "script": {"file": "wall_surface.ms", "sha256": sha256(script)},
        "publication": {"policy": "new_directory_no_replace",
                        "threat_model": "controlled_local_single_writer_observed_drift_checks",
                        "crash_durability_claim": False},
        "acceptance": {"live_execution": "NOT_RUN", "runtime_qa": "INCOMPLETE"},
    }
    artifacts = {"wall_surface.json": canonical_json(manifest), "wall_surface.ms": script}
    if sum(map(len, artifacts.values())) > MAX_ARTIFACT_BYTES:
        raise BuildRefusal("artifact pair exceeds 2 MiB")
    return artifacts


def build(project_dir: str | Path, out_dir: str | Path, namespace: str,
          system_type: str, system_scale: str | int | float,
          direction_authority: str | Path) -> dict[str, str]:
    validate_namespace(namespace)
    units = expected_units(system_type, system_scale)
    project = safe_path(project_dir, "project", directory=True)
    out = check_output_boundary(out_dir, project)
    inputs = _module("wall_surface_inputs")
    runtime = _module("wall_surface_runtime")
    publisher = _module("wall_surface_publish")
    generator_hashes = code_hashes((inputs, runtime, publisher))
    check_input_paths(project, inputs)
    snapshot = inputs.load_inputs(project, namespace=namespace, system_type=system_type,
                                  system_scale=units["system_scale"])
    walls, dimensions = _member(snapshot, "walls"), _member(snapshot, "dimensions")
    if not isinstance(walls, dict) or not isinstance(dimensions, dict):
        raise BuildRefusal("input adapter must return normalized walls and dimensions objects")
    hashes = snapshot_hashes(snapshot)
    walls_paths = [path for path in hashes if Path(path).name == "walls.json"]
    if len(walls_paths) != 1:
        raise BuildRefusal("input adapter must lock exactly one walls.json byte source")
    authority, authority_hashes = load_authority(direction_authority, walls, hashes[walls_paths[0]])
    authority_path = safe_path(direction_authority, "direction authority")
    if any(Path(path) == Path(walls_paths[0]) for path in authority_hashes if path != str(authority_path)):
        raise BuildRefusal("wall declaration cannot serve as its own independent direction source")
    hashes = _merge_hashes(hashes, authority_hashes)
    out = check_output_boundary(out, project, tuple(_merge_hashes(hashes, generator_hashes)))
    verify_hashes(_merge_hashes(hashes, generator_hashes))
    plan = runtime.build_plan(walls, dimensions)
    artifacts = make_artifacts(walls=walls, plan=plan, authority=authority, input_hashes=hashes,
                               generator_hashes=generator_hashes, namespace=namespace,
                               units=units, runtime=runtime)
    # The adapter can additionally recheck its directory/snapshot identity. Hash
    # checks here remain mandatory and do not assert immutable-handle exclusion.
    result = inputs.verify_inputs_unchanged(snapshot)
    if result is False:
        raise BuildRefusal("input adapter reports observed input drift")
    verify_hashes(_merge_hashes(hashes, generator_hashes))
    check_output_boundary(out, project, tuple(_merge_hashes(hashes, generator_hashes)))
    expected = {name: sha256(raw) for name, raw in artifacts.items()}
    published = publisher.publish_new_directory(out, artifacts)
    if published != expected:
        raise BuildRefusal("publication returned unexpected hashes; retain output for recovery inspection")
    # Independently verify the exact published pair, without cleanup or overwrite.
    for name, digest in expected.items():
        if sha256(_read_bytes(out / name, MAX_ARTIFACT_BYTES, "published artifact")) != digest:
            raise BuildRefusal("published artifact drift; retain output for recovery inspection")
    return expected


class _UniqueArgument(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Any, option_string: str | None = None) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"duplicate operational argument: {option_string}")
        setattr(namespace, self.dest, values)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    result.add_argument("--in", dest="project_dir", required=True, action=_UniqueArgument)
    result.add_argument("--out", dest="out_dir", required=True, action=_UniqueArgument)
    result.add_argument("--namespace", required=True, action=_UniqueArgument)
    result.add_argument("--system-type", required=True, action=_UniqueArgument)
    result.add_argument("--system-scale", required=True, action=_UniqueArgument)
    result.add_argument("--direction-authority", required=True, action=_UniqueArgument)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        hashes = build(**vars(args))
    except (ValueError, OSError, ImportError, AttributeError, TypeError, KeyError, RuntimeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print("produced_offline_unverified: " + json.dumps(hashes, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
