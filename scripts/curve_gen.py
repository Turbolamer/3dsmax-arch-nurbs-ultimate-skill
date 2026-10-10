"""scripts/curve_gen.py - Pure Python curve generation and chord bound library.

Form-precision Stage 05 pure curve generator library (microtasks 05.1 & 05.2).
Provides analytical discretization, coordinate quantization (q6), chord bounds,
and station count recommendation for circular arcs and elliptical arcs.

Import-only library; executing as __main__ exits with code 2.
"""

from __future__ import annotations

import math
import sys
from typing import Any

__all__ = [
    "validate_generator",
    "generator_points",
    "chord_bound",
    "suggest_count",
    "q6",
]

_ARC_ALLOWED_KEYS = frozenset(
    {"kind", "plane", "center_cm", "radius_cm", "from_deg", "to_deg", "count"}
)
_ELLIPSE_ALLOWED_KEYS = frozenset(
    {"kind", "plane", "center_cm", "semi_axes_cm", "from_deg", "to_deg", "count"}
)
_VALID_PLANES = frozenset({"XY", "XZ", "YZ"})


def _is_finite_number(val: Any) -> bool:
    """Return True if val is a finite int or float (excluding bool)."""
    return isinstance(val, (int, float)) and not isinstance(val, bool) and math.isfinite(val)


def q6(x: float) -> float:
    """Quantize coordinate to 6 decimal places with signed-zero normalization."""
    r = round(x, 6)
    return 0.0 if r == 0.0 else r


def validate_generator(gen: dict) -> tuple[bool, str]:
    """Validate a curve generator specification dict.

    Returns (True, "") on success or (False, reason) on validation failure.
    """
    if not isinstance(gen, dict):
        return False, f"generator must be a dict, got {type(gen).__name__}"

    if "kind" not in gen:
        return False, "missing required key 'kind'"
    kind = gen["kind"]
    if kind not in ("arc", "ellipse_arc"):
        return False, f"kind {kind!r} must be 'arc' or 'ellipse_arc'"

    gen_keys = set(gen.keys())
    if kind == "arc":
        allowed = _ARC_ALLOWED_KEYS
    else:
        allowed = _ELLIPSE_ALLOWED_KEYS

    missing = allowed - gen_keys
    if missing:
        return False, f"missing required keys for {kind}: {sorted(missing)}"

    extra = gen_keys - allowed
    if extra:
        return False, f"unlisted or forbidden keys for {kind}: {sorted(extra)}"

    plane = gen["plane"]
    if plane not in _VALID_PLANES:
        return False, f"plane {plane!r} must be 'XY', 'XZ', or 'YZ'"

    center_cm = gen["center_cm"]
    if not (
        isinstance(center_cm, list)
        and len(center_cm) == 3
        and all(_is_finite_number(c) for c in center_cm)
    ):
        return False, f"center_cm must be a list of 3 finite numbers, got {center_cm!r}"

    if kind == "arc":
        radius_cm = gen["radius_cm"]
        if not _is_finite_number(radius_cm):
            return False, f"radius_cm must be a finite number, got {radius_cm!r}"
        if radius_cm <= 0:
            return False, f"radius_cm must be > 0, got {radius_cm!r}"
    else:
        semi_axes_cm = gen["semi_axes_cm"]
        if not (
            isinstance(semi_axes_cm, list)
            and len(semi_axes_cm) == 2
            and all(_is_finite_number(a) and a > 0 for a in semi_axes_cm)
        ):
            return (
                False,
                f"semi_axes_cm must be a list of 2 finite numbers > 0, got {semi_axes_cm!r}",
            )

    from_deg = gen["from_deg"]
    if not _is_finite_number(from_deg):
        return False, f"from_deg must be a finite number, got {from_deg!r}"

    to_deg = gen["to_deg"]
    if not _is_finite_number(to_deg):
        return False, f"to_deg must be a finite number, got {to_deg!r}"

    count = gen["count"]
    if not (isinstance(count, int) and not isinstance(count, bool)):
        return False, f"count must be an integer (non-bool), got {count!r}"
    if not (2 <= count <= 500):
        return False, f"count must be in range 2..500, got {count!r}"

    delta = abs(to_deg - from_deg)
    if delta == 0 or abs(delta) < 1e-12:
        return False, "zero angular span (from_deg == to_deg)"
    if abs(delta - 360.0) < 1e-9 or delta > 360.0:
        return False, f"angular span {delta} deg closed or exceeds 360 deg (refused in core v1)"

    return True, ""


def generator_points(gen: dict) -> list[list[float]]:
    """Compute quantized 3D points [x, y, z] for a generator specification.

    Raises ValueError if generator is invalid or if adjacent duplicate points occur.
    """
    ok, reason = validate_generator(gen)
    if not ok:
        raise ValueError(reason)

    kind = gen["kind"]
    plane = gen["plane"]
    cx, cy, cz = gen["center_cm"]
    from_deg = gen["from_deg"]
    to_deg = gen["to_deg"]
    n = gen["count"]

    if kind == "arc":
        radius_cm = gen["radius_cm"]
    else:
        a, b = gen["semi_axes_cm"]

    t0 = math.radians(from_deg)
    t1 = math.radians(to_deg)

    points: list[list[float]] = []
    for i in range(n):
        ti = t0 + (t1 - t0) * i / (n - 1)
        c = math.cos(ti)
        s = math.sin(ti)

        if kind == "arc":
            u = radius_cm * c
            v = radius_cm * s
        else:
            u = a * c
            v = b * s

        if plane == "XY":
            pt = [q6(cx + u), q6(cy + v), q6(cz)]
        elif plane == "XZ":
            pt = [q6(cx + u), q6(cy), q6(cz + v)]
        elif plane == "YZ":
            pt = [q6(cx), q6(cy + u), q6(cz + v)]
        else:
            raise ValueError(f"unsupported plane {plane!r}")

        for coord in pt:
            if not math.isfinite(coord):
                raise ValueError(f"non-finite coordinate generated at point {i}: {pt}")

        if i > 0 and pt == points[i - 1]:
            raise ValueError(f"adjacent duplicate point at index {i}")

        points.append(pt)

    return points


def chord_bound(gen: dict, count: int | None = None) -> dict:
    """Compute conservative chord-to-arc sagitta bound and rounding perturbation budget.

    If count is provided, it overrides gen['count'] and must be in range 2..500.
    """
    if count is not None:
        if not (isinstance(count, int) and not isinstance(count, bool)):
            raise ValueError(f"count must be an integer, got {count!r}")
        if not (2 <= count <= 500):
            raise ValueError(f"count must be in range 2..500, got {count!r}")
        gen_to_check = dict(gen)
        gen_to_check["count"] = count
    else:
        gen_to_check = gen

    ok, reason = validate_generator(gen_to_check)
    if not ok:
        raise ValueError(reason)

    n = gen_to_check["count"]
    kind = gen_to_check["kind"]
    from_deg = gen_to_check["from_deg"]
    to_deg = gen_to_check["to_deg"]

    t0 = math.radians(from_deg)
    t1 = math.radians(to_deg)
    delta_rad = abs(t1 - t0) / (n - 1)

    endpoint_budget = math.sqrt(3) * 0.5e-6

    if kind == "arc":
        radius_cm = gen_to_check["radius_cm"]
        a_max = radius_cm
        if 0 < delta_rad <= math.pi:
            method = "circle_minor_sagitta_q6_v1"
            bound_val = radius_cm * (1.0 - math.cos(delta_rad / 2.0)) + endpoint_budget
        else:
            method = "ellipse_second_derivative_q6_v1"
            bound_val = a_max * (delta_rad**2) / 8.0 + endpoint_budget
    else:
        a, b = gen_to_check["semi_axes_cm"]
        a_max = max(a, b)
        method = "ellipse_second_derivative_q6_v1"
        bound_val = a_max * (delta_rad**2) / 8.0 + endpoint_budget

    return {
        "count": n,
        "delta_rad": delta_rad,
        "method": method,
        "chord_bound_cm": bound_val,
        "endpoint_rounding_budget_cm": endpoint_budget,
    }


def suggest_count(gen: dict, tol_cm: float) -> dict:
    """Find minimum station count in 2..500 satisfying tolerance tol_cm.

    Checks generator admissibility with count=n (including adjacent duplicate points).
    Returns recommendation dict with exhausted=False if satisfied, or exhausted=True.
    """
    if not _is_finite_number(tol_cm) or tol_cm <= 0:
        raise ValueError(f"tol_cm must be a finite number > 0, got {tol_cm!r}")

    if not isinstance(gen, dict):
        raise ValueError(f"generator must be a dict, got {type(gen).__name__}")

    gen_test = dict(gen)
    gen_test["count"] = 2
    ok, reason = validate_generator(gen_test)
    if not ok:
        raise ValueError(f"invalid generator: {reason}")

    for n in range(2, 501):
        gen_n = dict(gen)
        gen_n["count"] = n

        try:
            generator_points(gen_n)
        except ValueError:
            continue

        bound = chord_bound(gen_n)
        if bound["chord_bound_cm"] <= tol_cm:
            return {
                "count": n,
                "method": bound["method"],
                "chord_bound_cm": bound["chord_bound_cm"],
                "tol_cm": tol_cm,
                "exhausted": False,
            }

    return {
        "count": None,
        "method": None,
        "chord_bound_cm": None,
        "tol_cm": tol_cm,
        "exhausted": True,
        "error": f"tolerance {tol_cm} cm cannot be satisfied within count limit 500",
    }


if __name__ == "__main__":
    print(
        "Error: scripts/curve_gen.py is an import-only pure Python library.",
        file=sys.stderr,
    )
    sys.exit(2)
