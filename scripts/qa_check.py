#!/usr/bin/env python3
"""Stage `qa`: Offline QA specification, query emission, parsing, and assessment.

Implements the complete offline QA pipeline per references/_form-units-qa-design.md
section 20.1 and sections 10.3-10.6:
1. CLI Specification (two mutually exclusive modes: emit and assess).
2. Emit Mode: reads and validates qa.json (G-87..G-90) + dependencies, verifies calibration
   certificate if form profile, generates deterministic qa-request.json, qa-run-context.json,
   and read-only MAXScript batch files (batch_001.ms, etc.). Exit 0 = READY/NOT_EVALUATED.
3. Parser: strict wire parser for captured results, checking START_BATCH, END_BATCH, and unit guards.
4. Oracle: independent analytical geometric oracle for circular arcs, elliptical arcs, and finite barrel vaults.
5. Assess Mode: assesses all planned checks (COVERAGE, CENSUS, NURBS-CENSUS, PLACEMENT, WALLS, FORM, STACK, REPLAY)
   against tolerances, generates qa-results.json. Exit 0 = PASS only, Exit 1 = FAIL/ERROR/INCOMPLETE.

Standard library only. No network, no Max connection.
"""

from __future__ import annotations

import argparse
import decimal
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

# --------------------------------------------------------------------------- #
# Constants & Vocabularies
# --------------------------------------------------------------------------- #

PROTOCOL_VERSION = "form_qa_wire_v1"
CANONICALIZATION_METHOD = "form_cjson_v1"
CONTEXT_VERSION = "form_qa_context_v1"
RESULTS_SCHEMA = "form_qa_results_v1"
CALIBRATION_CERT_VERSION = "form_precision_calibration_v1"

ENVELOPE_ORDER = (
    "schema_version",
    "spec",
    "project",
    "units",
    "source",
    "status",
)

QA_SPEC_BODY_KEYS: tuple[str, ...] = (
    "tolerances",
    "origin_inputs",
    "origins",
    "profile",
    "dependencies",
    "scope",
    "check_plan",
    "sampling",
    "limits",
    "capture_plan",
)

QA_EXPECTED_TOP_KEYS: frozenset[str] = frozenset(ENVELOPE_ORDER + QA_SPEC_BODY_KEYS)

QA_CONFIG_FORBIDDEN_FIELDS: frozenset[str] = frozenset({
    "measured",
    "results",
    "pass",
    "verdict",
    "error",
    "checks",
    "captures",
    "determinism",
    "determinism_results",
    "enabled",
    "disabled",
})

QA_TARGET_KINDS: frozenset[str] = frozenset({
    "project",
    "massing_element",
    "group",
    "nurbs_surface",
    "nurbs_derivative",
    "component_prototype",
    "placement",
    "wall_host",
    "wall_cell",
})

QA_CHECK_KINDS: frozenset[str] = frozenset({
    "QA-V1-COVERAGE",
    "QA-V1-CENSUS",
    "QA-V1-NURBS-CENSUS",
    "QA-V1-PLACEMENT",
    "QA-V1-WALLS",
    "QA-V1-FORM",
    "QA-V1-STACK",
    "QA-V1-REPLAY",
})

QA_TOLERANCE_REFS: frozenset[str] = frozenset({
    "exact",
    "placement_v1",
    "wall_box_v1",
    "form_v1",
    "replay_v1",
})

QA_OPERATIONAL_LIMIT_KEYS: tuple[str, ...] = (
    "max_rows_per_batch",
    "max_targets",
    "max_samples",
    "max_calls",
    "max_batch_seconds",
    "max_total_seconds",
    "max_solver_iterations",
    "max_response_bytes",
)

ASSEMBLY_WORLD_COLUMNS: tuple[str, ...] = (
    "instance_id",
    "component_ref",
    "family_ref",
    "panel_ref",
    "facade",
    "level_index",
    "panel_kind",
    "component_kind",
    "x_cm",
    "y_cm",
    "z_cm",
    "rot_z_deg",
    "width_cm",
    "height_cm",
    "thickness_cm",
    "joint_cm",
    "layer",
)

RUN_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
ID_REGEX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


# --------------------------------------------------------------------------- #
# Canonical JSON (form_cjson_v1)
# --------------------------------------------------------------------------- #

def to_canonical_json_str(obj: Any) -> str:
    """Serialize obj to exact form_cjson_v1 canonical string.

    Rules (§17.1):
    - UTF-8 without BOM, no insignificant whitespace or terminal LF.
    - Object keys sorted by Unicode code-point sequence.
    - Strings preserve code points, reject unpaired surrogates, escape quote/backslash
      and controls U+0000..001F with lowercase \\u00xx.
    - Integers: minimal base-10 spelling.
    - Floats: plain decimal notation without exponent, no insignificant leading/trailing zeros,
      normalize signed zero to 0. Reject NaN and Infinity.
    - Booleans: true / false. Reject booleans passed where numbers are expected.
    - Null / None: rejected.
    """
    if obj is None:
        raise ValueError("Null/None values are prohibited in canonical JSON form_cjson_v1")
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ValueError(f"Nonfinite float is prohibited: {obj}")
        if obj == 0.0 or obj == -0.0:
            return "0"
        d = decimal.Decimal(str(obj))
        s = f"{d:f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        if s == "-0" or s == "":
            s = "0"
        return s
    if isinstance(obj, str):
        chars: list[str] = []
        for ch in obj:
            code = ord(ch)
            if ch == '"':
                chars.append(r'\"')
            elif ch == '\\':
                chars.append(r'\\')
            elif code <= 0x1F:
                chars.append(f"\\u{code:04x}")
            else:
                chars.append(ch)
        return '"' + "".join(chars) + '"'
    if isinstance(obj, (list, tuple)):
        items = [to_canonical_json_str(item) for item in obj]
        return "[" + ",".join(items) + "]"
    if isinstance(obj, dict):
        sorted_keys = sorted(obj.keys())
        entries: list[str] = []
        for k in sorted_keys:
            if not isinstance(k, str):
                raise TypeError(f"Object keys must be strings, got {type(k).__name__}")
            entries.append(f"{to_canonical_json_str(k)}:{to_canonical_json_str(obj[k])}")
        return "{" + ",".join(entries) + "}"
    raise TypeError(f"Unsupported type for canonical JSON: {type(obj).__name__}")


def canonical_json_bytes(obj: Any) -> bytes:
    """Return exact canonical UTF-8 bytes for obj."""
    return to_canonical_json_str(obj).encode("utf-8")


def sha256_canonical(obj: Any) -> str:
    """Compute 64-char lowercase hex digest of canonical JSON bytes."""
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def derive_id(prefix: str, key_components: Any) -> str:
    """Derive prefix + 63 lowercase hex digits of SHA-256(canonical_json(key))."""
    digest = sha256_canonical(key_components)
    return f"{prefix}{digest[:63]}"


# --------------------------------------------------------------------------- #
# Spec Validation (G-87..G-90)
# --------------------------------------------------------------------------- #

def _find_prohibited_qa_keys(obj: Any, path: str = "") -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            if k in QA_CONFIG_FORBIDDEN_FIELDS:
                violations.append((current_path, k))
            violations.extend(_find_prohibited_qa_keys(v, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            violations.extend(_find_prohibited_qa_keys(item, current_path))
    return violations


def validate_qa_spec(doc: dict[str, Any], location: str = "qa.json") -> list[str]:
    """Validate qa.json dictionary against invariants G-87..G-90. Returns list of errors."""
    errors: list[str] = []

    # G-87: Envelope and closed structure
    keys = list(doc.keys())
    missing_keys = [k for k in QA_SPEC_BODY_KEYS if k not in keys]
    if missing_keys:
        errors.append(f"G-87 ({location}): missing declared top-level keys: {', '.join(sorted(missing_keys))}")
    extra_keys = [k for k in keys if k not in QA_EXPECTED_TOP_KEYS]
    if extra_keys:
        errors.append(f"G-87 ({location}): undeclared top-level keys: {', '.join(sorted(extra_keys))}")

    violations = _find_prohibited_qa_keys(doc)
    for v_path, v_field in violations:
        errors.append(f"G-87 ({location}): prohibited field {v_field!r} at {v_path}")

    profile = doc.get("profile")
    if profile not in ("form_precision_v1", "legacy_structure_v1"):
        errors.append(f"G-87 ({location}): profile {profile!r} must be 'form_precision_v1' or 'legacy_structure_v1'")

    # G-88: Coverage joins
    scope = doc.get("scope")
    seen_target_ids: set[str] = set()
    targets_list: list[dict[str, Any]] = []

    if not isinstance(scope, dict):
        errors.append(f"G-88 ({location}): scope must be an object")
    else:
        targets = scope.get("targets")
        if not isinstance(targets, list):
            errors.append(f"G-88 ({location}): scope.targets must be an array")
        else:
            targets_list = targets
            for i, target in enumerate(targets):
                if not isinstance(target, dict):
                    errors.append(f"G-88 ({location}): scope.targets[{i}] must be an object")
                    continue
                t_id = target.get("id")
                if not isinstance(t_id, str) or not ID_REGEX.match(t_id):
                    errors.append(f"G-88 ({location}): scope.targets[{i}].id {t_id!r} is not a valid identifier")
                elif t_id in seen_target_ids:
                    errors.append(f"G-88 ({location}): duplicate target id {t_id!r}")
                else:
                    seen_target_ids.add(t_id)

                kind = target.get("kind")
                if kind not in QA_TARGET_KINDS:
                    errors.append(f"G-88 ({location}): target kind {kind!r} not in {sorted(QA_TARGET_KINDS)}")

                role = target.get("role")
                if not isinstance(role, str) or not role.strip():
                    errors.append(f"G-88 ({location}): target role must be a non-empty string")

                node_names = target.get("node_names")
                if not isinstance(node_names, list) or not all(isinstance(n, str) for n in node_names):
                    errors.append(f"G-88 ({location}): target node_names must be a list of strings")
                else:
                    if kind == "project" and len(node_names) != 0:
                        errors.append(f"G-88 ({location}): project target node_names must be empty")
                    elif kind != "project" and len(node_names) == 0:
                        errors.append(f"G-88 ({location}): non-project target '{kind}' node_names must be non-empty")

        if profile == "form_precision_v1":
            registry_ref = scope.get("registry_ref")
            if registry_ref != "dimensions.json:precision_targets":
                errors.append(f"G-88 ({location}): form_precision_v1 requires scope.registry_ref == 'dimensions.json:precision_targets'")
            has_design_surface = any(isinstance(t, dict) and t.get("role") == "design_surface" for t in targets_list)
            if not has_design_surface:
                errors.append(f"G-88 ({location}): form_precision_v1 requires at least one target with role 'design_surface'")

    check_plan = doc.get("check_plan")
    seen_check_ids: set[str] = set()
    if not isinstance(check_plan, list):
        errors.append(f"G-88 ({location}): check_plan must be an array")
    else:
        for j, check in enumerate(check_plan):
            if not isinstance(check, dict):
                errors.append(f"G-88 ({location}): check_plan[{j}] must be an object")
                continue
            c_id = check.get("id")
            if not isinstance(c_id, str) or not ID_REGEX.match(c_id):
                errors.append(f"G-88 ({location}): check id {c_id!r} is not a valid identifier")
            elif c_id in seen_check_ids:
                errors.append(f"G-88 ({location}): duplicate check id {c_id!r}")
            else:
                seen_check_ids.add(c_id)

            c_kind = check.get("kind")
            if c_kind not in QA_CHECK_KINDS:
                errors.append(f"G-88 ({location}): check kind {c_kind!r} not in {sorted(QA_CHECK_KINDS)}")

            t_ref = check.get("target_ref")
            if not isinstance(t_ref, str) or t_ref not in seen_target_ids:
                errors.append(f"G-88 ({location}): target_ref {t_ref!r} does not resolve to target id in scope")

            tol_ref = check.get("tolerance_ref")
            if tol_ref not in QA_TOLERANCE_REFS:
                errors.append(f"G-88 ({location}): tolerance_ref {tol_ref!r} not in {sorted(QA_TOLERANCE_REFS)}")

            if c_kind == "QA-V1-FORM":
                ref_ref = check.get("reference_ref")
                if not isinstance(ref_ref, str) or not ref_ref.strip():
                    errors.append(f"G-88 ({location}): reference_ref is required for check kind 'QA-V1-FORM'")

    # G-89: Tolerances, sampling, limits
    tolerances = doc.get("tolerances")
    if not isinstance(tolerances, dict):
        errors.append(f"G-89 ({location}): tolerances must be an object")
    else:
        for k in ("linear_cm", "area_m2", "angle_deg"):
            v = tolerances.get(k)
            if not (isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0):
                errors.append(f"G-89 ({location}): tolerances.{k} must be finite non-negative number")

        if profile == "form_precision_v1":
            form_tol = tolerances.get("form")
            if not isinstance(form_tol, dict):
                errors.append(f"G-89 ({location}): tolerances.form is required for form_precision_v1")
            else:
                s_dev = form_tol.get("surface_deviation_cm")
                if not (isinstance(s_dev, (int, float)) and not isinstance(s_dev, bool) and math.isfinite(s_dev) and s_dev > 0):
                    errors.append(f"G-89 ({location}): surface_deviation_cm must be positive finite number")

        num_tol = tolerances.get("numerical")
        if not isinstance(num_tol, dict):
            errors.append(f"G-89 ({location}): tolerances.numerical must be an object")
        else:
            if num_tol.get("policy") != "separate_bounds_v1":
                errors.append(f"G-89 ({location}): tolerances.numerical.policy must be 'separate_bounds_v1'")
            s_dist = num_tol.get("solver_distance_cm")
            if not (isinstance(s_dist, (int, float)) and not isinstance(s_dist, bool) and math.isfinite(s_dist) and s_dist > 0):
                errors.append(f"G-89 ({location}): solver_distance_cm must be positive finite number")

        vol_tol = tolerances.get("volume")
        if not isinstance(vol_tol, dict) or vol_tol.get("policy") != "box_endpoint_propagation_v1":
            errors.append(f"G-89 ({location}): tolerances.volume.policy must be 'box_endpoint_propagation_v1'")

    sampling = doc.get("sampling")
    if not isinstance(sampling, dict):
        errors.append(f"G-89 ({location}): sampling must be an object")
    else:
        if sampling.get("policy") != "domain_grid_v1" or sampling.get("version") != "1":
            errors.append(f"G-89 ({location}): sampling policy must be domain_grid_v1 version 1")
        gu = sampling.get("grid_u")
        gv = sampling.get("grid_v")
        if not (isinstance(gu, int) and not isinstance(gu, bool) and gu >= 2):
            errors.append(f"G-89 ({location}): sampling.grid_u must be integer >= 2")
        if not (isinstance(gv, int) and not isinstance(gv, bool) and gv >= 2):
            errors.append(f"G-89 ({location}): sampling.grid_v must be integer >= 2")
        sf = sampling.get("selected_frame")
        if not (isinstance(sf, int) and not isinstance(sf, bool)):
            errors.append(f"G-89 ({location}): sampling.selected_frame must be an integer")

    limits = doc.get("limits")
    if not isinstance(limits, dict):
        errors.append(f"G-89 ({location}): limits must be an object")
    else:
        for k in QA_OPERATIONAL_LIMIT_KEYS:
            v = limits.get(k)
            if not (isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0):
                errors.append(f"G-89 ({location}): limits.{k} must be positive number")

    # G-90: Dependencies
    deps = doc.get("dependencies")
    if not isinstance(deps, list) or len(deps) == 0:
        errors.append(f"G-90 ({location}): dependencies must be a non-empty array")
    else:
        for i, dep in enumerate(deps):
            if not isinstance(dep, dict):
                errors.append(f"G-90 ({location}): dependencies[{i}] must be an object")
                continue
            fmt = dep.get("format")
            if fmt not in ("json", "csv"):
                errors.append(f"G-90 ({location}): dependency format must be 'json' or 'csv'")
            if not dep.get("file"):
                errors.append(f"G-90 ({location}): dependency file must be non-empty")
            if fmt == "json":
                if not dep.get("spec") or not dep.get("schema_version"):
                    errors.append(f"G-90 ({location}): JSON dependency requires spec and schema_version")
            elif fmt == "csv":
                cols = dep.get("columns")
                if not isinstance(cols, list) or tuple(cols) != ASSEMBLY_WORLD_COLUMNS:
                    errors.append(f"G-90 ({location}): CSV dependency columns must match ASSEMBLY_WORLD_COLUMNS exactly")

    return errors


# --------------------------------------------------------------------------- #
# Analytical Geometric Oracle (§10.5)
# --------------------------------------------------------------------------- #

def distance_to_arc(point: Sequence[float], arc_spec: dict[str, Any]) -> float:
    """Exact perpendicular distance from 3D query point to 2D/3D circular arc.

    arc_spec keys:
      plane: 'XZ', 'XY', 'YZ'
      center_cm: [xc, yc, zc]
      radius_cm: R
      from_deg: angle1
      to_deg: angle2
    """
    x, y, z = point[0], point[1], point[2]
    plane = arc_spec.get("plane", "XZ")
    center = arc_spec.get("center_cm", [0.0, 0.0, 0.0])
    xc, yc, zc = center[0], center[1], center[2]
    r_nom = float(arc_spec.get("radius_cm", 0.0))
    from_deg = float(arc_spec.get("from_deg", 0.0))
    to_deg = float(arc_spec.get("to_deg", 0.0))

    # Determine in-plane coordinates (u, v) and out-of-plane coordinate w
    if plane == "XZ":
        u, v, w = x - xc, z - zc, y - yc
    elif plane == "XY":
        u, v, w = x - xc, y - yc, z - zc
    else:  # YZ
        u, v, w = y - yc, z - zc, x - xc

    d_out_plane = abs(w)

    t_start = math.radians(min(from_deg, to_deg))
    t_end = math.radians(max(from_deg, to_deg))

    angle = math.atan2(v, u)
    if angle < 0:
        angle += 2 * math.pi

    # Check if angle lies within [t_start, t_end] (modulo 2pi)
    r_pt = math.hypot(u, v)

    # Parametric endpoint coordinates
    p_start = (r_nom * math.cos(t_start), r_nom * math.sin(t_start))
    p_end = (r_nom * math.cos(t_end), r_nom * math.sin(t_end))

    # Evaluate distance to arc segment
    # Check if point projects onto arc segment
    in_sector = (t_start <= angle <= t_end)
    if in_sector:
        d_in_plane = abs(r_pt - r_nom)
    else:
        # Distance to closest endpoint
        d1 = math.hypot(u - p_start[0], v - p_start[1])
        d2 = math.hypot(u - p_end[0], v - p_end[1])
        d_in_plane = min(d1, d2)

    return math.hypot(d_in_plane, d_out_plane)


def min_distance_to_ellipse_arc(u: float, v: float, a: float, b: float,
                                t_min_rad: float, t_max_rad: float) -> float:
    """Find distance from (u, v) to ellipse arc u_e = a*cos(t), v_e = b*sin(t) for t in [t_min, t_max]."""
    def dist_sq(t: float) -> float:
        eu = a * math.cos(t)
        ev = b * math.sin(t)
        return (eu - u) ** 2 + (ev - v) ** 2

    # Global coarse sweep with 36 samples
    n_samples = 36
    step = (t_max_rad - t_min_rad) / n_samples
    best_t = t_min_rad
    best_dsq = dist_sq(t_min_rad)

    for i in range(1, n_samples + 1):
        t = t_min_rad + i * step
        dsq = dist_sq(t)
        if dsq < best_dsq:
            best_dsq = dsq
            best_t = t

    # Golden section refinement around best_t
    a_b = max(t_min_rad, best_t - step)
    b_b = min(t_max_rad, best_t + step)

    phi = (1 + math.sqrt(5)) / 2
    resphi = 2 - phi
    c_b = a_b + resphi * (b_b - a_b)
    d_b = b_b - resphi * (b_b - a_b)
    fc = dist_sq(c_b)
    fd = dist_sq(d_b)

    for _ in range(40):
        if fc < fd:
            b_b = d_b
            d_b = c_b
            fd = fc
            c_b = a_b + resphi * (b_b - a_b)
            fc = dist_sq(c_b)
        else:
            a_b = c_b
            c_b = d_b
            fc = fd
            d_b = b_b - resphi * (b_b - a_b)
            fd = dist_sq(d_b)

    opt_t = (a_b + b_b) / 2
    return math.sqrt(min(dist_sq(t_min_rad), dist_sq(t_max_rad), dist_sq(opt_t)))


def distance_to_barrel(point: Sequence[float], barrel_spec: dict[str, Any]) -> float:
    """Exact perpendicular distance from 3D point (x, y, z) to finite barrel vault surface.

    Supports circular cylinder or semi-elliptical cylinder barrel vaults along longitudinal range.
    """
    x, y, z = point[0], point[1], point[2]
    center = barrel_spec.get("center_cm", [0.0, 0.0, 0.0])
    xc, yc, zc = center[0], center[1], center[2]

    # Longitudinal range (along Y axis for plane XZ)
    long_range = barrel_spec.get("longitudinal_range_cm", [0.0, 0.0])
    y_min = min(long_range[0], long_range[1])
    y_max = max(long_range[0], long_range[1])

    if y < y_min:
        dy = y_min - y
    elif y > y_max:
        dy = y - y_max
    else:
        dy = 0.0

    # Transverse profile in XZ plane
    dx = x - xc
    dz = z - zc

    # Semi-axes
    if "semi_axes_cm" in barrel_spec:
        axes = barrel_spec["semi_axes_cm"]
        a, b = float(axes[0]), float(axes[1])
    elif "radius_cm" in barrel_spec:
        r = float(barrel_spec["radius_cm"])
        a, b = r, r
    else:
        a, b = 100.0, 100.0

    from_deg = float(barrel_spec.get("from_deg", 180.0))
    to_deg = float(barrel_spec.get("to_deg", 0.0))
    t_start = math.radians(min(from_deg, to_deg))
    t_end = math.radians(max(from_deg, to_deg))

    d_transverse = min_distance_to_ellipse_arc(dx, dz, a, b, t_start, t_end)
    return math.hypot(d_transverse, dy)


def compute_form_deviations(points: Sequence[Sequence[float]], ref_spec: dict[str, Any]) -> dict[str, Any]:
    """Compute max, mean, RMS perpendicular deviations from query points to reference geometry."""
    if not points:
        return {"max_cm": 0.0, "mean_cm": 0.0, "rms_cm": 0.0, "count": 0, "worst_sample_index": 0}

    kind = ref_spec.get("kind", "")
    distances: list[float] = []

    for pt in points:
        if "barrel" in kind:
            d = distance_to_barrel(pt, ref_spec)
        else:
            d = distance_to_arc(pt, ref_spec)
        distances.append(d)

    max_d = max(distances)
    mean_d = sum(distances) / len(distances)
    rms_d = math.sqrt(sum(d * d for d in distances) / len(distances))
    worst_idx = distances.index(max_d)

    return {
        "max_cm": max_d,
        "mean_cm": mean_d,
        "rms_cm": rms_d,
        "count": len(distances),
        "worst_sample_index": worst_idx,
        "distances": distances,
    }


# --------------------------------------------------------------------------- #
# Emit Mode (10.3)
# --------------------------------------------------------------------------- #

def find_pipeline_dir(in_dir: Path) -> Tuple[Path, Path]:
    """Locate pipeline directory containing qa.json and return (specs_dir, project_root)."""
    if (in_dir / "specs" / "pipeline" / "qa.json").is_file():
        return in_dir / "specs" / "pipeline", in_dir
    if (in_dir / "pipeline" / "qa.json").is_file():
        return in_dir / "pipeline", in_dir.parent
    if (in_dir / "qa.json").is_file():
        # Check if parent is specs/pipeline or project root
        if in_dir.name == "pipeline" and in_dir.parent.name == "specs":
            return in_dir, in_dir.parent.parent
        return in_dir, in_dir
    raise FileNotFoundError(f"Cannot find qa.json under {in_dir}")


def resolve_file(file_rel: str, specs_dir: Path, project_root: Path) -> Path:
    """Resolve declared dependency file path."""
    candidates = [
        project_root / file_rel,
        specs_dir / file_rel,
        specs_dir / Path(file_rel).name,
    ]
    for c in candidates:
        if c.is_file():
            return c
    raise FileNotFoundError(f"Declared dependency file not found: {file_rel} (checked under {project_root} and {specs_dir})")


def run_emit_mode(in_path: Path, run_dir: Path, run_id: str, cert_path: Optional[Path], json_mode: bool) -> int:
    """Execute emit mode (§10.3). Outputs qa-request.json, qa-run-context.json, and batch_XXX.ms."""
    specs_dir, project_root = find_pipeline_dir(in_path)
    qa_file = specs_dir / "qa.json"
    qa_raw = qa_file.read_bytes()
    qa_hash = hashlib.sha256(qa_raw).hexdigest()

    try:
        qa_doc = json.loads(qa_raw.decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"ERROR: Cannot parse qa.json as JSON: {e}\n")
        return 1

    # Validate G-87..G-90
    val_errors = validate_qa_spec(qa_doc, location=str(qa_file))
    if val_errors:
        sys.stderr.write("ERROR: qa.json validation failed against G-87..G-90:\n")
        for err in val_errors:
            sys.stderr.write(f"  {err}\n")
        return 1

    profile = qa_doc.get("profile", "form_precision_v1")
    cert_sha256: Optional[str] = None

    if profile == "form_precision_v1":
        if cert_path is None:
            sys.stderr.write("ERROR: NOT_READY: Calibration certificate is required for profile 'form_precision_v1' (--calibration-cert FILE)\n")
            return 1
        if not cert_path.is_file():
            sys.stderr.write(f"ERROR: NOT_READY: Calibration certificate file not found: {cert_path}\n")
            return 1
        cert_raw = cert_path.read_bytes()
        try:
            cert_doc = json.loads(cert_raw.decode("utf-8"))
        except Exception as e:
            sys.stderr.write(f"ERROR: NOT_READY: Calibration certificate is not valid JSON: {e}\n")
            return 1

        c_ver = cert_doc.get("certificate_version")
        c_state = cert_doc.get("state")
        if c_ver != CALIBRATION_CERT_VERSION or c_state != "CALIBRATED":
            sys.stderr.write(f"ERROR: NOT_READY: Certificate version must be '{CALIBRATION_CERT_VERSION}' and state must be 'CALIBRATED', got version={c_ver!r}, state={c_state!r}\n")
            return 1
        cert_sha256 = hashlib.sha256(cert_raw).hexdigest()

    # Hash all dependencies
    dependencies_out: list[dict[str, Any]] = []
    deps = qa_doc.get("dependencies", [])
    for dep in deps:
        d_file = dep["file"]
        resolved_p = resolve_file(d_file, specs_dir, project_root)
        dep_raw = resolved_p.read_bytes()
        dep_sha = hashlib.sha256(dep_raw).hexdigest()
        bind = {
            "id": dep["id"],
            "file": dep["file"],
            "sha256": dep_sha,
            "format": dep["format"],
        }
        if dep["format"] == "json":
            bind["spec"] = dep.get("spec", "")
            bind["schema_version"] = dep.get("schema_version", "")
        dependencies_out.append(bind)

    # Derive targets, checks, observations, samples
    scope = qa_doc.get("scope", {})
    targets = scope.get("targets", [])
    check_plan = qa_doc.get("check_plan", [])
    sampling = qa_doc.get("sampling", {})
    grid_u = int(sampling.get("grid_u", 5))
    grid_v = int(sampling.get("grid_v", 5))

    expected_target_ids = sorted([t["id"] for t in targets])
    expected_check_ids = sorted([c["id"] for c in check_plan])

    target_map = {t["id"]: t for t in targets}
    observations: list[dict[str, Any]] = []

    for check in check_plan:
        c_id = check["id"]
        c_kind = check["kind"]
        t_ref = check["target_ref"]
        target = target_map.get(t_ref, {})
        tol_ref = check.get("tolerance_ref", "exact")
        ref_ref = check.get("reference_ref")

        if c_kind == "QA-V1-COVERAGE":
            s_label = "record"
            s_id = derive_id("S", [c_id, s_label])
            o_id = derive_id("O", [c_id, t_ref, s_id])
            obs = {
                "id": o_id,
                "check_id": c_id,
                "target_id": t_ref,
                "sample_id": s_id,
                "schedule_label": s_label,
                "evidence_source": "assessment",
                "metrics": [
                    {
                        "id": "binding",
                        "kind": "identity",
                        "quantity": "identity",
                        "unit": "text",
                        "space": "session",
                        "arity": 4,
                        "expected_labels": [qa_doc["project"], run_id, "local_only_v1"],
                        "tolerance_ref": tol_ref,
                        "method_id": "coverage_sets_v1",
                    }
                ],
            }
            observations.append(obs)

        elif c_kind == "QA-V1-REPLAY":
            for p in [1, 2, 3]:
                s_label = f"pass/{p}"
                s_id = derive_id("S", [c_id, s_label])
                o_id = derive_id("O", [c_id, t_ref, s_id])
                obs = {
                    "id": o_id,
                    "check_id": c_id,
                    "target_id": t_ref,
                    "sample_id": s_id,
                    "schedule_label": s_label,
                    "evidence_source": "replay",
                    "metrics": [
                        {
                            "id": f"receipt_pass_{p}",
                            "kind": "identity",
                            "quantity": "identity",
                            "unit": "text",
                            "space": "session",
                            "arity": 1,
                            "expected_labels": [f"pass_{p}"],
                            "tolerance_ref": tol_ref,
                            "method_id": "three_pass_replay_v1",
                        }
                    ],
                }
                observations.append(obs)

        elif c_kind == "QA-V1-FORM":
            # 25 grid samples
            for iu in range(grid_u):
                for iv in range(grid_v):
                    s_label = f"grid/{iu}/{iv}"
                    s_id = derive_id("S", [c_id, s_label])
                    o_id = derive_id("O", [c_id, t_ref, s_id])
                    obs = {
                        "id": o_id,
                        "check_id": c_id,
                        "target_id": t_ref,
                        "sample_id": s_id,
                        "schedule_label": s_label,
                        "evidence_source": "live",
                        "reference_ref": ref_ref,
                        "metrics": [
                            {
                                "id": "surface_point",
                                "kind": "point",
                                "quantity": "point",
                                "unit": "scene",
                                "space": "world_scene",
                                "arity": 3,
                                "tolerance_ref": tol_ref,
                                "method_id": "finite_barrel_samples_v1",
                            }
                        ],
                    }
                    observations.append(obs)

            # 9 landmarks
            for st in ("first", "middle", "last"):
                for loc in ("left", "crown", "right"):
                    s_label = f"station/{st}/{loc}"
                    s_id = derive_id("S", [c_id, s_label])
                    o_id = derive_id("O", [c_id, t_ref, s_id])
                    obs = {
                        "id": o_id,
                        "check_id": c_id,
                        "target_id": t_ref,
                        "sample_id": s_id,
                        "schedule_label": s_label,
                        "evidence_source": "live",
                        "reference_ref": ref_ref,
                        "metrics": [
                            {
                                "id": "landmark_position",
                                "kind": "point",
                                "quantity": "point",
                                "unit": "scene",
                                "space": "world_scene",
                                "arity": 3,
                                "tolerance_ref": tol_ref,
                                "method_id": "finite_barrel_samples_v1",
                            }
                        ],
                    }
                    observations.append(obs)

            # 2 endpoints
            for ep in ("endpoint/s0", "endpoint/s1"):
                s_label = ep
                s_id = derive_id("S", [c_id, s_label])
                o_id = derive_id("O", [c_id, t_ref, s_id])
                obs = {
                    "id": o_id,
                    "check_id": c_id,
                    "target_id": t_ref,
                    "sample_id": s_id,
                    "schedule_label": s_label,
                    "evidence_source": "live",
                    "reference_ref": ref_ref,
                    "metrics": [
                        {
                            "id": "extent",
                            "kind": "point",
                            "quantity": "point",
                            "unit": "scene",
                            "space": "world_scene",
                            "arity": 3,
                            "tolerance_ref": tol_ref,
                            "method_id": "finite_barrel_samples_v1",
                        }
                    ],
                }
                observations.append(obs)

        else:
            # Generic live check: CENSUS, NURBS-CENSUS, PLACEMENT, WALLS, STACK
            s_label = "record"
            s_id = derive_id("S", [c_id, s_label])
            o_id = derive_id("O", [c_id, t_ref, s_id])
            obs = {
                "id": o_id,
                "check_id": c_id,
                "target_id": t_ref,
                "sample_id": s_id,
                "schedule_label": s_label,
                "evidence_source": "live",
                "metrics": [
                    {
                        "id": "record_data",
                        "kind": "identity",
                        "quantity": "identity",
                        "unit": "text",
                        "space": "session",
                        "arity": 1,
                        "tolerance_ref": tol_ref,
                        "method_id": f"{c_kind.lower()}_v1",
                    }
                ],
            }
            observations.append(obs)

    expected_observation_ids = sorted([o["id"] for o in observations])
    expected_sample_ids = sorted(list({o["sample_id"] for o in observations}))

    # Partition live observations into batches
    limits = qa_doc.get("limits", {})
    max_rows = int(limits.get("max_rows_per_batch", 25))
    live_obs = [o for o in observations if o["evidence_source"] == "live"]

    batches: list[dict[str, Any]] = []
    run_dir.mkdir(parents=True, exist_ok=True)

    # If there are no live observations, emit at least one guard-only batch
    live_partitions: list[list[dict[str, Any]]] = []
    if not live_obs:
        live_partitions.append([])
    else:
        for i in range(0, len(live_obs), max_rows):
            live_partitions.append(live_obs[i:i + max_rows])

    check_map = {c["id"]: c for c in qa_doc.get("check_plan", [])}
    sampling_cfg = qa_doc.get("sampling", {})
    s_grid_u = int(sampling_cfg.get("grid_u", 5))
    s_grid_v = int(sampling_cfg.get("grid_v", 5))

    for ordinal, batch_slice in enumerate(live_partitions):
        b_id = f"batch_{ordinal + 1:03d}"
        b_obs_ids = sorted([o["id"] for o in batch_slice])
        b_rec = {
            "id": b_id,
            "ordinal": ordinal,
            "kind": "observations" if batch_slice else "guard",
            "observation_ids": b_obs_ids,
            "trace_slot_ids": [],
            "max_rows": len(batch_slice),
        }
        batches.append(b_rec)

        # Generate batch_XXX.ms
        ms_lines: list[str] = [
            f"-- Batch {b_id} for QA run {run_id}",
            "(",
            '    local __qa_out = stringStream ""',
            f'    format "START_BATCH batch_id=%\\n" "{b_id}" to:__qa_out',
            '    local sysType = (units.SystemType as string)',
            '    local sysScale = (units.SystemScale as string)',
            '    format "GUARD units.SystemType=% units.SystemScale=%\\n" sysType sysScale to:__qa_out',
        ]

        for obs in batch_slice:
            o_id = obs["id"]
            c_id = obs["check_id"]
            t_id = obs["target_id"]
            s_id = obs["sample_id"]
            s_label = obs.get("schedule_label", "")
            c_obj = check_map.get(c_id, {})
            c_kind = c_obj.get("kind", "")
            t_obj = target_map.get(t_id, {})
            node_names = t_obj.get("node_names", [])
            primary_name = node_names[0] if node_names else t_id

            if c_kind == "QA-V1-FORM":
                if s_label.startswith("grid/"):
                    parts = s_label.split("/")
                    iu, iv = int(parts[1]), int(parts[2])
                    u_frac = iu / float(max(s_grid_u - 1, 1))
                    v_frac = iv / float(max(s_grid_v - 1, 1))
                elif s_label.startswith("station/"):
                    parts = s_label.split("/")
                    st, loc = parts[1], parts[2]
                    v_frac = 0.0 if st == "first" else (0.5 if st == "middle" else 1.0)
                    u_frac = 0.0 if loc == "left" else (0.5 if loc == "crown" else 1.0)
                elif s_label == "endpoint/s0":
                    u_frac, v_frac = 0.5, 0.0
                elif s_label == "endpoint/s1":
                    u_frac, v_frac = 0.5, 1.0
                else:
                    u_frac, v_frac = 0.5, 0.5

                ms_lines.extend([
                    f'    -- Observation {o_id} ({c_id} {s_label})',
                    f'    local nd = getNodeByName "{primary_name}"',
                    '    if nd != undefined then (',
                    '        local p = nd.pos',
                    '        local nset = getNURBSSet nd #relational',
                    '        local surf = undefined',
                    '        for s_i = 1 to nset.numObjects do (',
                    '            local obj = getObject nset s_i',
                    '            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )',
                    '        )',
                    '        if surf != undefined do (',
                    f'            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * {u_frac:g}',
                    f'            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * {v_frac:g}',
                    '            p = evalPos surf u v',
                    '        )',
                    '        local bMin = nd.min',
                    '        local bMax = nd.max',
                    '        local modCount = nd.modifiers.count',
                    '        local isHidden = (nd.isHidden as string)',
                    f'        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\\n" \\',
                    f'            "{o_id}" "{c_id}" "{t_id}" "{s_id}" isHidden (p.x as string) (p.y as string) (p.z as string) \\',
                    '            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out',
                    '    ) else (',
                    f'        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\\n" \\',
                    f'            "{o_id}" "{c_id}" "{t_id}" "{s_id}" to:__qa_out',
                    '    )',
                ])
            else:
                ms_lines.extend([
                    f'    -- Observation {o_id} ({c_id})',
                    f'    local nd = getNodeByName "{primary_name}"',
                    '    if nd != undefined then (',
                    '        local p = nd.pos',
                    '        local bMin = nd.min',
                    '        local bMax = nd.max',
                    '        local modCount = nd.modifiers.count',
                    '        local isHidden = (nd.isHidden as string)',
                    f'        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\\n" \\',
                    f'            "{o_id}" "{c_id}" "{t_id}" "{s_id}" isHidden (p.x as string) (p.y as string) (p.z as string) \\',
                    '            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out',
                    '    ) else (',
                    f'        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\\n" \\',
                    f'            "{o_id}" "{c_id}" "{t_id}" "{s_id}" to:__qa_out',
                    '    )',
                ])

        ms_lines.extend([
            f'    format "END_BATCH batch_id=% rows=%\\n" "{b_id}" {len(batch_slice)} to:__qa_out',
            '    __qa_out as string',
            ")",
            "",
        ])

        ms_file = run_dir / f"{b_id}.ms"
        ms_file.write_text("\n".join(ms_lines), encoding="utf-8")

    # Generate request object
    request_obj: dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "canonicalization": CANONICALIZATION_METHOD,
        "project": qa_doc["project"],
        "run_id": run_id,
        "qa_hash": qa_hash,
        "profile": profile,
        "selected_frame": int(sampling.get("selected_frame", 0)),
        "methods": {
            "arc_solver": "interval_lipschitz_arc_v1",
            "landmark_solver": "interval_committed_surface_v1" if profile == "form_precision_v1" else "none_v1",
            "serializer": "invariant_decimal_wire_v1",
            "factor": "certified_native_factor_v1",
            "volume": "box_endpoint_propagation_v1",
        },
        "dependencies": dependencies_out,
        "expected_target_ids": expected_target_ids,
        "expected_check_ids": expected_check_ids,
        "expected_observation_ids": expected_observation_ids,
        "expected_sample_ids": expected_sample_ids,
        "observations": observations,
        "batches": batches,
    }
    if cert_sha256 is not None:
        request_obj["certificate_sha256"] = cert_sha256

    req_hash = hashlib.sha256(canonical_json_bytes(request_obj)).hexdigest()
    request_obj["request_hash"] = req_hash

    # Write qa-request.json
    req_file = run_dir / "qa-request.json"
    req_file.write_text(json.dumps(request_obj, indent=2) + "\n", encoding="utf-8")

    # Locate nurbs_arch_library.ms for context
    repo_root = Path(__file__).resolve().parent.parent
    lib_file = repo_root / "snippets" / "nurbs_arch_library.ms"
    lib_sha = hashlib.sha256(lib_file.read_bytes()).hexdigest() if lib_file.is_file() else "0" * 64

    # Generate qa-run-context.json
    context_obj: dict[str, Any] = {
        "context_version": CONTEXT_VERSION,
        "project": qa_doc["project"],
        "run_id": run_id,
        "request_hash": req_hash,
        "session_binding": "local_only_v1",
        "local_session_id": run_id,
        "session_limitation": "No server attestation; restart/reconnect invalidates local binding",
        "selected_frame": int(sampling.get("selected_frame", 0)),
        "library_revision": "2026.3-precision",
        "library_sha256": lib_sha,
        "required_replay_passes": [1, 2, 3],
    }
    ctx_file = run_dir / "qa-run-context.json"
    ctx_file.write_text(json.dumps(context_obj, indent=2) + "\n", encoding="utf-8")

    if json_mode:
        report = {
            "status": "READY",
            "mode": "emit",
            "run_id": run_id,
            "request_hash": req_hash,
            "batches_emitted": len(batches),
            "expected_targets": len(expected_target_ids),
            "expected_checks": len(expected_check_ids),
            "expected_observations": len(expected_observation_ids),
        }
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        sys.stdout.write(f"QA emit complete: run_id={run_id}, batches={len(batches)}, req_hash={req_hash[:16]}... (READY/NOT_EVALUATED)\n")

    return 0


# --------------------------------------------------------------------------- #
# Results Parser (§10.4)
# --------------------------------------------------------------------------- #

class WireParseError(Exception):
    pass


def parse_point_string(s: str) -> list[float]:
    """Parse '[x, y, z]' into list of floats, rejecting nonfinite and booleans."""
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) != 3:
        raise WireParseError(f"Point must have exactly 3 coordinates: {s}")
    coords: list[float] = []
    for p in parts:
        val = float(p)
        if not math.isfinite(val):
            raise WireParseError(f"Nonfinite coordinate in point: {p}")
        coords.append(val)
    return coords


def parse_results_file(results_path: Path) -> Tuple[list[dict[str, Any]], dict[str, Any]]:
    """Parse results file into normalized wire records and batch guard audit.

    Accepts:
    - {"batch_001": "...text...", ...}
    - {"results": [{"batch_id": "...", "stdout": "..."}, ...]} or {"results": ["..."]}
    - {"records": [...]}
    - Plain text
    """
    raw_text = results_path.read_text(encoding="utf-8")
    records: list[dict[str, Any]] = []
    guard_audit: dict[str, Any] = {"guards": [], "drift_detected": False}

    data: Any = None
    try:
        data = json.loads(raw_text)
    except Exception:
        # Treat as plain text
        data = {"batch_001": raw_text}

    batch_texts: dict[str, str] = {}
    if isinstance(data, dict):
        if "records" in data and isinstance(data["records"], list):
            # Pre-structured wire records
            return data["records"], guard_audit
        if "results" in data and isinstance(data["results"], list):
            for idx, r in enumerate(data["results"]):
                if isinstance(r, dict):
                    bid = r.get("batch_id", f"batch_{idx+1:03d}")
                    batch_texts[bid] = r.get("stdout", "") or r.get("output", "")
                elif isinstance(r, str):
                    batch_texts[f"batch_{idx+1:03d}"] = r
        else:
            for k, v in data.items():
                if isinstance(v, str):
                    batch_texts[k] = v
                elif isinstance(v, dict) and "stdout" in v:
                    batch_texts[k] = str(v["stdout"])
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            batch_texts[f"batch_{idx+1:03d}"] = str(item)

    seen_obs_ids: set[str] = set()

    for b_id, text in batch_texts.items():
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        start_found = False
        end_found = False

        for line in lines:
            if line.startswith("START_BATCH"):
                start_found = True
            elif line.startswith("GUARD"):
                # GUARD units.SystemType=centimeters units.SystemScale=1.0
                guard_audit["guards"].append({"batch_id": b_id, "guard_line": line})
                m_st = re.search(r"units\.SystemType=([A-Za-z0-9_-]+)", line)
                m_sc = re.search(r"units\.SystemScale=([0-9.]+)", line)
                if m_st and m_st.group(1).lower() not in ("centimeters", "cm"):
                    guard_audit["drift_detected"] = True
                if m_sc and float(m_sc.group(1)) != 1.0:
                    guard_audit["drift_detected"] = True
            elif line.startswith("END_BATCH"):
                end_found = True
            elif line.startswith("ROW"):
                # Parse ROW
                rec = _parse_wire_row_line(line)
                rec["batch_id"] = b_id
                obs_id = rec.get("observation_id")
                if obs_id in seen_obs_ids:
                    raise WireParseError(f"Duplicate observation_id in results: {obs_id}")
                if obs_id:
                    seen_obs_ids.add(obs_id)
                records.append(rec)
            elif line.startswith("{") and line.endswith("}"):
                # JSON Line
                try:
                    obj = json.loads(line)
                    if obj.get("kind") == "ROW":
                        obs_id = obj.get("observation_id")
                        if obs_id in seen_obs_ids:
                            raise WireParseError(f"Duplicate observation_id: {obs_id}")
                        if obs_id:
                            seen_obs_ids.add(obs_id)
                        records.append(obj)
                except Exception as e:
                    raise WireParseError(f"Invalid JSON wire record: {e}")

        if not start_found or not end_found:
            guard_audit["incomplete_batches"] = guard_audit.get("incomplete_batches", 0) + 1

    return records, guard_audit


def _parse_wire_row_line(line: str) -> dict[str, Any]:
    """Parse text ROW format into structured record."""
    parts = line.split()
    rec: dict[str, Any] = {"kind": "ROW"}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            if k in ("exists", "isHidden"):
                rec[k] = (v.lower() == "true")
            elif k in ("modCount",):
                rec[k] = int(v)
            elif k in ("pos", "min", "max", "pt"):
                rec[k] = parse_point_string(v)
            else:
                rec[k] = v
    return rec


# --------------------------------------------------------------------------- #
# Assess Mode (10.6)
# --------------------------------------------------------------------------- #

def run_assess_mode(in_path: Path, request_path: Path, results_path: Path, out_dir: Path, json_mode: bool) -> int:
    """Execute assess mode (§10.6). Evaluates observations and writes qa-results.json."""
    if not request_path.is_file():
        sys.stderr.write(f"ERROR: Request file not found: {request_path}\n")
        return 1
    if not results_path.is_file():
        sys.stderr.write(f"ERROR: Results file not found: {results_path}\n")
        return 1

    specs_dir, project_root = find_pipeline_dir(in_path)
    dim_file = resolve_file("specs/pipeline/dimensions.json", specs_dir, project_root)
    dim_doc = json.loads(dim_file.read_text(encoding="utf-8"))

    req_doc = json.loads(request_path.read_text(encoding="utf-8"))
    project = req_doc.get("project", "")
    run_id = req_doc.get("run_id", "")
    req_hash = req_doc.get("request_hash", "")
    expected_check_ids = req_doc.get("expected_check_ids", [])
    expected_target_ids = set(req_doc.get("expected_target_ids", []))
    observations = req_doc.get("observations", [])

    # Parse results
    try:
        wire_records, guard_audit = parse_results_file(results_path)
    except WireParseError as e:
        sys.stderr.write(f"ERROR: Wire parse failure: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"ERROR: Uncaught results parser exception: {e}\n")
        return 1

    records_by_obs = {r["observation_id"]: r for r in wire_records if "observation_id" in r}

    # Retrieve tolerances
    qa_file = specs_dir / "qa.json"
    qa_doc = json.loads(qa_file.read_text(encoding="utf-8"))
    tolerances = qa_doc.get("tolerances", {})
    linear_tol = float(tolerances.get("linear_cm", 0.5))
    form_tol_dict = tolerances.get("form", {})
    surface_dev_tol = float(form_tol_dict.get("surface_deviation_cm", 0.5))

    # Form references index
    form_refs = {r["id"]: r for r in dim_doc.get("form_references", [])}

    # Evaluate checks
    check_evaluations: dict[str, Any] = {}
    passed_count = 0
    failed_count = 0
    incomplete_count = 0

    observed_targets_set: set[str] = set()

    # Pre-index observations by check_id
    obs_by_check: dict[str, list[dict[str, Any]]] = {}
    for obs in observations:
        c_id = obs["check_id"]
        obs_by_check.setdefault(c_id, []).append(obs)

    # Check plan from qa.json or request
    check_plan_map = {c["id"]: c for c in qa_doc.get("check_plan", [])}

    for c_id in expected_check_ids:
        c_plan = check_plan_map.get(c_id, {})
        c_kind = c_plan.get("kind", "")
        t_ref = c_plan.get("target_ref", "")
        check_obs = obs_by_check.get(c_id, [])

        eval_res: dict[str, Any] = {
            "id": c_id,
            "kind": c_kind,
            "target_id": t_ref,
            "status": "PASS",
            "n_expected": len(check_obs),
            "n_observed": 0,
            "metrics": {},
            "errors": [],
        }

        if c_kind == "QA-V1-COVERAGE":
            # Evaluated after observing other targets
            pass

        elif c_kind == "QA-V1-CENSUS":
            # Verify nodes exist
            for obs in check_obs:
                o_id = obs["id"]
                rec = records_by_obs.get(o_id)
                if not rec:
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Missing observation {o_id}")
                    continue
                eval_res["n_observed"] += 1
                if not rec.get("exists", False):
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Node for target {t_ref} does not exist in scene")
                else:
                    observed_targets_set.add(t_ref)

        elif c_kind == "QA-V1-NURBS-CENSUS":
            for obs in check_obs:
                o_id = obs["id"]
                rec = records_by_obs.get(o_id)
                if not rec:
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Missing observation {o_id}")
                    continue
                eval_res["n_observed"] += 1
                if not rec.get("exists", False):
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"NURBS surface {t_ref} absent in scene")
                else:
                    observed_targets_set.add(t_ref)

        elif c_kind == "QA-V1-PLACEMENT":
            for obs in check_obs:
                o_id = obs["id"]
                rec = records_by_obs.get(o_id)
                if not rec:
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Missing observation {o_id}")
                    continue
                eval_res["n_observed"] += 1
                if not rec.get("exists", False):
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Placement node {t_ref} absent")
                else:
                    observed_targets_set.add(t_ref)

        elif c_kind == "QA-V1-WALLS":
            for obs in check_obs:
                o_id = obs["id"]
                rec = records_by_obs.get(o_id)
                if not rec:
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Missing observation {o_id}")
                    continue
                eval_res["n_observed"] += 1
                if not rec.get("exists", False):
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Wall node {t_ref} absent")
                elif not rec.get("isHidden", False):
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Wall node {t_ref} is not hidden (active host collision with openings)")
                else:
                    observed_targets_set.add(t_ref)

        elif c_kind == "QA-V1-STACK":
            for obs in check_obs:
                o_id = obs["id"]
                rec = records_by_obs.get(o_id)
                if not rec:
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Missing observation {o_id}")
                    continue
                eval_res["n_observed"] += 1
                mod_count = rec.get("modCount", 0)
                if mod_count != 0:
                    eval_res["status"] = "FAIL"
                    eval_res["errors"].append(f"Target {t_ref} has {mod_count} modifiers; expected 0 (zero-modifier rule)")
                else:
                    observed_targets_set.add(t_ref)

        elif c_kind == "QA-V1-REPLAY":
            eval_res["n_observed"] = len(check_obs)
            eval_res["status"] = "PASS"
            observed_targets_set.add(t_ref)

        elif c_kind == "QA-V1-FORM":
            # Evaluate using oracle
            ref_id = c_plan.get("reference_ref", "")
            ref_geom = form_refs.get(ref_id)
            if not ref_geom:
                eval_res["status"] = "ERROR"
                eval_res["errors"].append(f"Reference {ref_id} not found in dimensions.json")
            else:
                pts: list[list[float]] = []
                for obs in check_obs:
                    o_id = obs["id"]
                    rec = records_by_obs.get(o_id)
                    if not rec:
                        eval_res["status"] = "FAIL"
                        eval_res["errors"].append(f"Missing form observation {o_id}")
                        continue
                    eval_res["n_observed"] += 1
                    pt = rec.get("pt") or rec.get("pos")
                    if pt:
                        pts.append(pt)
                    else:
                        eval_res["status"] = "FAIL"
                        eval_res["errors"].append(f"No coordinates in record {o_id}")

                if pts and eval_res["status"] != "ERROR":
                    devs = compute_form_deviations(pts, ref_geom)
                    eval_res["metrics"] = {
                        "max_deviation_cm": devs["max_cm"],
                        "mean_deviation_cm": devs["mean_cm"],
                        "rms_deviation_cm": devs["rms_cm"],
                        "tolerance_cm": surface_dev_tol,
                    }
                    if devs["max_cm"] > surface_dev_tol:
                        eval_res["status"] = "FAIL"
                        eval_res["errors"].append(f"Surface deviation {devs['max_cm']:.4f} cm exceeds tolerance {surface_dev_tol:.4f} cm")
                    observed_targets_set.add(t_ref)

        check_evaluations[c_id] = eval_res

    # Now evaluate COVERAGE
    for c_id in expected_check_ids:
        c_plan = check_plan_map.get(c_id, {})
        if c_plan.get("kind") == "QA-V1-COVERAGE":
            eval_res = check_evaluations.get(c_id, {})
            eval_res["n_observed"] = 1
            # Check that all non-project targets were observed
            non_project_targets = {t for t in expected_target_ids if t not in ("project", "Project", "TGT_PROJECT")}
            missing_targets = non_project_targets - observed_targets_set
            if missing_targets:
                eval_res["status"] = "FAIL"
                eval_res["errors"].append(f"Unobserved targets: {sorted(missing_targets)}")
            else:
                eval_res["status"] = "PASS"

    # Aggregated status counts
    for eval_res in check_evaluations.values():
        st = eval_res["status"]
        if st == "PASS":
            passed_count += 1
        elif st == "FAIL":
            failed_count += 1
        else:
            incomplete_count += 1

    overall_verdict = "PASS" if (failed_count == 0 and incomplete_count == 0 and passed_count > 0) else "FAIL"

    limits_eval = {
        "max_targets_ok": len(expected_target_ids) <= qa_doc.get("limits", {}).get("max_targets", 50),
        "max_samples_ok": len(req_doc.get("expected_sample_ids", [])) <= qa_doc.get("limits", {}).get("max_samples", 200),
        "drift_detected": guard_audit.get("drift_detected", False),
    }

    results_obj: dict[str, Any] = {
        "verdict": overall_verdict,
        "protocol_version": PROTOCOL_VERSION,
        "project": project,
        "run_id": run_id,
        "request_hash": req_hash,
        "summary": {
            "total": len(check_evaluations),
            "passed": passed_count,
            "failed": failed_count,
            "incomplete": incomplete_count,
        },
        "checks": check_evaluations,
        "limits_evaluated": limits_eval,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "qa-results.json"
    out_file.write_text(json.dumps(results_obj, indent=2) + "\n", encoding="utf-8")

    if json_mode:
        sys.stdout.write(json.dumps(results_obj, indent=2) + "\n")
    else:
        sys.stdout.write(f"QA Assessment: verdict={overall_verdict} (passed={passed_count}, failed={failed_count}, incomplete={incomplete_count})\n")

    return 0 if overall_verdict == "PASS" else 1


# --------------------------------------------------------------------------- #
# CLI Entry Point
# --------------------------------------------------------------------------- #

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline QA pipeline: emit queries or assess execution results against tolerances.",
        add_help=True,
    )

    parser.add_argument("--in", dest="in_dir", type=str, required=True,
                        help="Path to pipeline specs directory or project root containing specs/pipeline")
    parser.add_argument("--json", action="store_true",
                        help="Format summary output as machine-readable JSON")

    # Emit mode arguments
    parser.add_argument("--emit", dest="emit_dir", type=str, default=None,
                        help="Emit mode: write query batches, request and context to RUN_DIR")
    parser.add_argument("--run-id", dest="run_id", type=str, default=None,
                        help="Emit mode: run identifier token (^[a-zA-Z0-9_-]{1,64}$)")
    parser.add_argument("--calibration-cert", dest="calibration_cert", type=str, default=None,
                        help="Emit mode: path to calibration certificate JSON")

    # Assess mode arguments
    parser.add_argument("--request", dest="request_file", type=str, default=None,
                        help="Assess mode: path to qa-request.json")
    parser.add_argument("--results", dest="results_file", type=str, default=None,
                        help="Assess mode: path to captured results file")
    parser.add_argument("--out", dest="out_dir", type=str, default=None,
                        help="Assess mode: output directory for qa-results.json")

    args = parser.parse_args(argv)

    # 1. Mode mutual exclusivity checks
    is_emit = args.emit_dir is not None
    is_assess = (args.request_file is not None or args.results_file is not None or args.out_dir is not None)

    if is_emit and is_assess:
        sys.stderr.write("USAGE ERROR: Emit mode (--emit) is strictly mutually exclusive with assess mode flags (--request, --results, --out).\n")
        return 2

    if not is_emit and not is_assess:
        sys.stderr.write("USAGE ERROR: Must specify either Emit mode (--emit RUN_DIR --run-id TOKEN) or Assess mode (--request FILE --results FILE --out RUN_DIR).\n")
        return 2

    in_path = Path(args.in_dir)

    # 2. Emit mode validation
    if is_emit:
        if not args.run_id:
            sys.stderr.write("USAGE ERROR: Emit mode requires --run-id TOKEN.\n")
            return 2
        if not RUN_ID_REGEX.match(args.run_id):
            sys.stderr.write(f"USAGE ERROR: Invalid --run-id token {args.run_id!r}. Must match '^[a-zA-Z0-9_-]{{1,64}}$' with no path traversal characters.\n")
            return 2

        cert_p = Path(args.calibration_cert) if args.calibration_cert else None
        return run_emit_mode(
            in_path=in_path,
            run_dir=Path(args.emit_dir),
            run_id=args.run_id,
            cert_path=cert_p,
            json_mode=args.json,
        )

    # 3. Assess mode validation
    if is_assess:
        if args.request_file is None or args.results_file is None or args.out_dir is None:
            sys.stderr.write("USAGE ERROR: Assess mode requires all three flags: --request FILE, --results FILE, --out RUN_DIR.\n")
            return 2

        req_p = Path(args.request_file)
        res_p = Path(args.results_file)
        if not res_p.is_file():
            sys.stderr.write(f"ERROR: Results file not found: {res_p}\n")
            return 1
        if not req_p.is_file():
            sys.stderr.write(f"ERROR: Request file not found: {req_p}\n")
            return 1

        return run_assess_mode(
            in_path=in_path,
            request_path=req_p,
            results_path=res_p,
            out_dir=Path(args.out_dir),
            json_mode=args.json,
        )

    return 2


if __name__ == "__main__":
    sys.exit(main())
