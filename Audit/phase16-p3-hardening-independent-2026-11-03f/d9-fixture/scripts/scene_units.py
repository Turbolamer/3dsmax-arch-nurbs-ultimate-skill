#!/usr/bin/env python3
"""Scene units translation and boundary factor utilities.

Provides certified 3ds Max SystemType mappings, scale factor calculations (c, f),
MAXScript unit verification preambles, and offline conversion helpers.

Canonical pipeline convention (G-5, G-8):
- All length dimensions in specs are canonical centimetres (ends with '_cm').
- Native 3ds Max scene units depend on units.SystemType and units.SystemScale.
- c = k * SystemScale (cm per scene unit)
- f = 1.0 / c (scene units per cm)
- Writing to scene: L_scene = L_cm * f = L_cm / c
- Reading from scene: L_cm = L_scene * c
"""

from __future__ import annotations

import math
from collections.abc import Sequence

#: Certified 3ds Max SystemType names mapped to centimetres per base unit (k).
SYSTEM_TYPE_FACTORS: dict[str, float] = {
    "centimeters": 1.0,
    "millimeters": 0.1,
    "meters": 100.0,
    "kilometers": 100000.0,
    "inches": 2.54,
    "feet": 30.48,
    "miles": 160934.4,
    "yards": 91.44,
}

#: Known non-dimensional keys that do not scale with length factors.
NON_DIMENSIONAL_KEYS: frozenset[str] = frozenset(
    {
        "angle_deg",
        "closed_sections",
        "count",
        "divisions_u",
        "divisions_v",
        "flip_trim",
        "hide_curves",
        "mat_id",
        "p_vec",
        "parallel",
        "render_angle_deg",
        "render_edge_pct",
        "rot_z_deg",
        "rotation_from_deg",
        "rotation_to_deg",
        "run_angle_deg",
        "scale_from",
        "scale_to",
        "seed",
        "slope_deg",
        "tension",
        "u_order",
        "v_order",
        "view_steps_u",
        "view_steps_v",
        "weight",
    }
)


def unit_factor(system_type: str, system_scale: float) -> tuple[float, float]:
    """Calculate (c, f) factors for a given 3ds Max SystemType and SystemScale.

    Parameters:
        system_type: Name of the 3ds Max units.SystemType (e.g. "centimeters", "#inches").
        system_scale: Value of units.SystemScale (positive finite number).

    Returns:
        tuple[float, float]:
            c: centimetres per native scene unit (c = k * system_scale).
            f: native scene units per centimetre (f = 1.0 / c).

    Raises:
        ValueError: If system_type is uncertified/unknown or system_scale is not a finite positive number.
    """
    if not isinstance(system_type, str):
        raise ValueError(f"uncertified or unknown SystemType: {system_type!r}")
    norm_type = system_type.strip()
    if norm_type.startswith("#"):
        norm_type = norm_type[1:].strip()
    norm_type = norm_type.lower()

    if norm_type not in SYSTEM_TYPE_FACTORS:
        raise ValueError(f"uncertified or unknown SystemType: {system_type!r}")

    if isinstance(system_scale, bool) or not isinstance(system_scale, (int, float)):
        raise ValueError(f"invalid system_scale: {system_scale!r}; must be finite positive number")
    if not math.isfinite(system_scale) or system_scale <= 0.0:
        raise ValueError(f"invalid system_scale: {system_scale!r}; must be finite positive number")

    k = SYSTEM_TYPE_FACTORS[norm_type]
    c = k * float(system_scale)
    f = 1.0 / c
    return (c, f)


def emit_unit_preamble(stage: str = "general", factor_var: str = "__f_unit") -> str:
    """Return MAXScript preamble code string validating scene units and defining factor_var."""
    lines = [
        f"    -- Unit setup verification and scale preamble ({stage})",
        "    local __sys_scale = units.SystemScale as float",
        "    if __sys_scale == undefined or __sys_scale <= 0.0 do (",
        '        throw ("Invalid units.SystemScale: " + (__sys_scale as string) + "; must be positive")',
        "    )",
        "    local __sys_type_raw = units.SystemType as string",
        "    local __sys_type_str = toLower (units.SystemType as string)",
        '    if (substring __sys_type_str 1 1) == "#" do __sys_type_str = substring __sys_type_str 2 -1',
        "    local __k_cm = case __sys_type_str of (",
        '        "centimeters": 1.0',
        '        "millimeters": 0.1',
        '        "meters": 100.0',
        '        "kilometers": 100000.0',
        '        "inches": 2.54',
        '        "feet": 30.48',
        '        "miles": 160934.4',
        '        "yards": 91.44',
        "        default: undefined",
        "    )",
        "    if __k_cm == undefined do (",
        '        throw ("Uncertified or unknown units.SystemType: " + (units.SystemType as string))',
        "    )",
        "    local __c_cm = __k_cm * __sys_scale",
        f"    local {factor_var} = 1.0 / __c_cm",
    ]
    return "\n".join(lines)


def scene_length_expr(val_cm: float, factor_var: str = "__f_unit") -> str:
    """Return MAXScript expression converting val_cm to scene units."""
    if isinstance(val_cm, bool) or not isinstance(val_cm, (int, float)):
        raise ValueError(f"invalid val_cm: {val_cm!r}; must be finite number")
    if not math.isfinite(val_cm):
        raise ValueError(f"invalid val_cm: {val_cm!r}; must be finite number")
    if val_cm == 0.0:
        return "0.0"
    return f"({val_cm:g} * {factor_var})"


def scene_point_expr(point_cm: Sequence[float], factor_var: str = "__f_unit") -> str:
    """Return MAXScript expression converting 3D point in cm to scene units."""
    if len(point_cm) != 3:
        raise ValueError(f"point_cm must have length 3, got {len(point_cm)}")
    for i, coord in enumerate(point_cm):
        if isinstance(coord, bool) or not isinstance(coord, (int, float)) or not math.isfinite(coord):
            raise ValueError(f"invalid coordinate at index {i}: {coord!r}; must be finite number")
    return f"([{point_cm[0]:g}, {point_cm[1]:g}, {point_cm[2]:g}] * {factor_var})"


def to_scene_length(val_cm: float, system_type: str, system_scale: float) -> float:
    """Convert canonical length (cm) to native scene units."""
    if isinstance(val_cm, bool) or not isinstance(val_cm, (int, float)):
        raise ValueError(f"invalid val_cm: {val_cm!r}; must be finite number")
    if not math.isfinite(val_cm):
        raise ValueError(f"invalid val_cm: {val_cm!r}; must be finite number")
    _, f = unit_factor(system_type, system_scale)
    return float(val_cm) * f


def to_canonical_length(val_scene: float, system_type: str, system_scale: float) -> float:
    """Convert native scene length to canonical cm."""
    if isinstance(val_scene, bool) or not isinstance(val_scene, (int, float)):
        raise ValueError(f"invalid val_scene: {val_scene!r}; must be finite number")
    if not math.isfinite(val_scene):
        raise ValueError(f"invalid val_scene: {val_scene!r}; must be finite number")
    c, _ = unit_factor(system_type, system_scale)
    return float(val_scene) * c


def to_scene_point(pt_cm: Sequence[float], system_type: str, system_scale: float) -> list[float]:
    """Convert 3D point in canonical cm to native scene units."""
    if len(pt_cm) != 3:
        raise ValueError(f"pt_cm must have length 3, got {len(pt_cm)}")
    for i, coord in enumerate(pt_cm):
        if isinstance(coord, bool) or not isinstance(coord, (int, float)) or not math.isfinite(coord):
            raise ValueError(f"invalid coordinate at index {i}: {coord!r}; must be finite number")
    _, f = unit_factor(system_type, system_scale)
    return [float(coord) * f for coord in pt_cm]


def to_canonical_point(pt_scene: Sequence[float], system_type: str, system_scale: float) -> list[float]:
    """Convert 3D point in native scene units to canonical cm."""
    if len(pt_scene) != 3:
        raise ValueError(f"pt_scene must have length 3, got {len(pt_scene)}")
    for i, coord in enumerate(pt_scene):
        if isinstance(coord, bool) or not isinstance(coord, (int, float)) or not math.isfinite(coord):
            raise ValueError(f"invalid coordinate at index {i}: {coord!r}; must be finite number")
    c, _ = unit_factor(system_type, system_scale)
    return [float(coord) * c for coord in pt_scene]


def to_canonical_area(
    area_scene: float,
    system_type: str,
    system_scale: float,
    unit: str = "cm2",
) -> float:
    """Convert scene area to canonical area (default cm2, or m2 if unit='m2')."""
    if isinstance(area_scene, bool) or not isinstance(area_scene, (int, float)):
        raise ValueError(f"invalid area_scene: {area_scene!r}; must be finite number")
    if not math.isfinite(area_scene):
        raise ValueError(f"invalid area_scene: {area_scene!r}; must be finite number")
    c, _ = unit_factor(system_type, system_scale)
    a_cm2 = float(area_scene) * (c ** 2)
    norm_unit = unit.strip().lower()
    if norm_unit in ("cm2", "cm^2", "centimeter2", "centimeters2"):
        return a_cm2
    elif norm_unit in ("m2", "m^2", "meter2", "meters2"):
        return a_cm2 / 10000.0
    else:
        raise ValueError(f"unknown canonical area unit: {unit!r}; expected 'cm2' or 'm2'")


def to_canonical_volume(vol_scene: float, system_type: str, system_scale: float) -> float:
    """Convert scene volume to canonical cm3 (V_scene * (c**3))."""
    if isinstance(vol_scene, bool) or not isinstance(vol_scene, (int, float)):
        raise ValueError(f"invalid vol_scene: {vol_scene!r}; must be finite number")
    if not math.isfinite(vol_scene):
        raise ValueError(f"invalid vol_scene: {vol_scene!r}; must be finite number")
    c, _ = unit_factor(system_type, system_scale)
    return float(vol_scene) * (c ** 3)


def is_dimensional_length_key(key: str) -> bool:
    """Return True if key represents a dimensional length (ends with '_cm' and not exempted)."""
    if not isinstance(key, str):
        return False
    if key in NON_DIMENSIONAL_KEYS:
        return False
    return key.endswith("_cm")


def is_nondimensional_key(key: str) -> bool:
    """Return True if key is in NON_DIMENSIONAL_KEYS or ends with non-dimensional suffix."""
    if not isinstance(key, str):
        return False
    if key in NON_DIMENSIONAL_KEYS:
        return True
    return key.endswith(
        (
            "_deg",
            "_m2",
            "_count",
            "_id",
            "_ref",
            "_refs",
            "_ids",
            "_pct",
            "_ratio",
            "_index",
            "_indices",
            "_kind",
            "_type",
            "_ccw",
        )
    )
