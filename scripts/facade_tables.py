#!/usr/bin/env python3
"""Stage `facade`: locked dimensions.json + massing.json -> facade_grids.json,
components_registry.json, facade_table.csv, world_table.csv.

The P5 stage. It writes the four artefacts `_p5-contract.md` sections 3 to 6
define and section 8 requires, in the shape invariants G-57..G-70 accept:

    <out>/facade_grids.json        spec `facade_grids`: envelopes, grids, panels
    <out>/components_registry.json  spec `components_registry`: size-class blocks
    <out>/facade_table.csv          one row per panel, geometry
    <out>/world_table.csv           one row per panel, the placeable instance

Usage
-----
    python scripts/facade_tables.py --in examples --out examples
    python scripts/facade_tables.py --in examples --out examples --stage grids
    python scripts/facade_tables.py --in examples --out examples --stage components
    python scripts/facade_tables.py --in examples --out examples --stage tables
    python scripts/facade_tables.py --in examples --out examples --json
    python scripts/facade_tables.py --in examples --allow-draft

Exit codes
----------
    0   built, G-57..G-70 passed on the emitted documents, and G-70 re-asserted by
        reading the two CSVs back off disk
    1   a refusal: the lock gate, a schema mismatch, a file on disk this build would
        overwrite, a failed self-check, or a G-70 read-back mismatch. The message
        names the file, the id, the key path and the rule that fired.
    2   usage error

DETERMINISM (07 S-5)
--------------------
The same locked input produces byte-identical output. Nothing here reads a clock,
a random source or an unordered container: `AX-nnn`, `PNL-nnn`, `CMP-nnn` and
`FAM-nnn` are allocated in a fixed order, every number goes through `q()` (6
decimals, negative zero normalised), `origins` is emitted in document order,
`origin_inputs` is a sorted set, and CSV floats go through the same `q()`-based
`num()` `build_nurbs.py` uses. Two runs into two empty directories produce four
identical files, or this script has a bug.

THE FOUR FILES ARE DERIVED IN ONE DIRECTION
-------------------------------------------
`dimensions.json` + `massing.json` -> `facade_grids.json` ->
`components_registry.json` -> the two CSVs. A panel never names a component
(contract section 5.1), so the join runs registry -> grid and there is no cycle:
`G-68` is one pass.

`direction_deg` IS NOT A ROTATION (G-57)
---------------------------------------
`dimensions.json` `F-S` runs `[0,0] -> [1800,0]` -- along +X -- and carries
`direction_deg = 180.0`, while `F-N` runs `[0,900] -> [1800,900]`, also along +X,
and carries `0.0`. `direction_deg` is a compass-facing label. The rotation every
panel on a facade uses is
`run_angle_deg = atan2(end.y - start.y, end.x - start.x)` normalised to
`(-180, 180]`, which is `0.0` for both of those facades and `90.0` for `F-E` and
`F-W`. `world_table.csv` carries `run_angle_deg` in `rot_z_deg`, and the
self-check refuses a rotation taken from `direction_deg`.

THE ONE THRESHOLD, AND WHY IT IS DERIVED (contract section 4 step 9)
--------------------------------------------------------------------
The `30 cm` in rule 8.3 is `09-defaults.md` `D-OP-12`'s curtain-wall pier width
(`15 cm`, range `10 ... 25`) doubled. It is not a chosen number. A project whose
pier exceeds it gets a `blank` there, which is the correct reading of a wide pier
and violates no default. The module constant is `PIER_MAX_CM`.

THE VERTICAL DIVISION IS PER BAY, NOT PER FACADE (contract section 3.3)
----------------------------------------------------------------------
`u` axes are one set per `(facade, level)` -- the bay offsets plus every opening
edge, `bay_index: null` -- because a horizontal division runs the whole run. `v`
axes are one set per `(bay, level)`: `0` and `height_cm` plus **the sill and head
of the openings in that bay**, `bay_index: b`. An earlier revision made the
vertical division the union of every opening's sill and head across the whole
facade, and it produced `PNL-024` -- a `punched_window` of **180 x 10 cm**, a
10 cm ribbon of glass 10 cm below a window head, because `OP-G-02` (an entrance in
bay 1, `head_cm = 260`) put a horizontal division at 260 across a facade whose
bay-0 windows run `90 -> 270`. The cost of the per-bay rule is that transom lines
are continuous *within* a bay rather than across the run; that is the correct
trade. The benefit is that an opening's own sill and head are its only vertical
divisions, so **every opening is realised by exactly one panel** and a panel's
height is bounded by its own opening rather than by a neighbour's door head.

ONE MULLION RULE, NO FLAG (contract section 4 step 8.3, revision 2)
--------------------------------------------------------------------
A cell whose u-range is **adjacent to** a `curtain_wall` opening's u-range on the
same bay -- one of its two u boundaries equals the opening's corresponding
boundary within `linear_cm` -- and whose width is `<= PIER_MAX_CM` is a `mullion`,
emitted once per `(facade, level, bay)` spanning `0 .. height_cm` with
`full_height: true`. One rule, one code path. Revision 1 demanded that the cell be
simultaneously outside and inside that u-range and carried a `MULLION_ABUTS_OPENING`
switch to choose between the two readings; the switch is gone, because a cell can
only be one thing and the flanking reading is the one that describes a pier.

THE PARTITION IS EXACT, AND G-61 IS THE PROOF
---------------------------------------------
Per `(facade, level, bay)` the u cells tile the bay's width and the bay's own v
cells tile the storey height, and the bays tile the run (contract section 4, "Why
the whole partition is exact"). `G-61` asserts both area sums, that no two panels
overlap in their interiors, and that every panel lies inside its bay's rectangle.
`G-62` is strictly **exactly one** panel per opening, whose u-range is the
opening's own and whose v-range is exactly `[sill_cm, head_cm]`: under the
per-bay rule nothing can split an opening, so "one or more" is not a tolerance
but a different -- and, for the revision-1 grid, wrong -- geometry.

PROVENANCE (G-64)
-----------------
P5 states two numbers and both live in `defaults`, not in the grid:
`panel_thickness_cm` (`09` `D-CL-05`, declared default `3`, range `2 ... 8`) and
`joint_width_cm` (`09` `D-FM-10`, declared default `2`, range `1 ... 4`). Each is
its convention's **declared default**, not a value merely inside its range: a
default is traceable to a written convention, an in-range choice is an invention,
and a number in a generated file that nobody can trace is the failure this repo
has been bitten by twice. They are carried as `assumed` with ledger refs `A-023`
and `A-024` because nothing in `dimensions.json` states a panel depth or a joint;
everything in `facade_grids.json` is `derived` with a resolving `derives_from`,
which is why that file holds no `assumed` value at all. A `layer` leaf is a
constant of this stage's schema, and its only in-file anchor is `spec`.

The registry's `size_cm` has no in-registry source -- the panel widths live in
`facade_grids.json` -- so its size-bearing leaves are anchored on each other and
cross-checked by `G-66`, which recomputes
`size_cm == [width_cm, height_cm, panel_thickness_cm]` and every
`parameters[].value` from it. That keeps every `derives_from` inside the file the
claim is made about.

WHAT THIS BUILDER REFUSES
-------------------------
* A `dimensions.json` or `massing.json` that is not `locked` (07 section 3.1).
  `--allow-draft` waives the gate, and then `G-57..G-70` run and fail.
* A schema major this builder does not implement (07 G-3), a `spec` that does not
  match the filename (G-2), a BOM, or non-strict JSON (G-7).
* **`facade_grids.json` already present in `--in` whose canonical bytes differ
  from what this build computes, naming the first differing key path.** A hand
  edit that a rebuild would silently destroy is exactly what `--from examples`
  exists to prevent, and the silent overwrite is the only way that failure
  reaches a user.
* A `G-64` violation: an `assumed` or a `given` value inside `facade_grids.json`.
* Any FAIL from `G-57..G-70` on the emitted documents, checked against the bytes
  about to be written rather than against the intention.
* A `G-70` read-back mismatch after the CSVs are on disk: row counts, ref
  resolution, `rot_z_deg == run_angle_deg`, `instance_id == panel_ref`.

LAYER IS DATA (07 section 8.1.3)
-------------------------------
Every panel and every component carries `layer: "05_FACADE"` and the CSVs carry
the same string in a `layer` column. Nothing in this file assigns a layer to
anything; an object's layer is not assignable from MAXScript in Max 2026, so a
later stage applies it and this one only records it.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Sequence

SUPPORTED_SCHEMA_MAJOR = 1
SUPPORTED_SCHEMA_MINORS: tuple[int, ...] = (0, 1)
SCHEMA_VERSION = "1.0"

STAGES: tuple[str, ...] = ("grids", "components", "tables", "all")

DIMENSIONS_NAME = "dimensions.json"
MASSING_NAME = "massing.json"
GRIDS_NAME = "facade_grids.json"
REGISTRY_NAME = "components_registry.json"
FACADE_CSV_NAME = "facade_table.csv"
WORLD_CSV_NAME = "world_table.csv"

FACADE_LAYER = "05_FACADE"

#: 09-defaults.md D-CL-05, the modelled depth of a facade panel block. Assumed
#: (A-023), because nothing in dimensions.json states a panel depth. The value is
#: D-CL-05's own declared default, not a value merely inside its range: a
#: convention's default is traceable, an in-range choice is an invention (P5
#: contract section 5.2 and 7.1).
PANEL_THICKNESS_CM = 3.0
PANEL_THICKNESS_RANGE_CM = (2.0, 8.0)
#: 09-defaults.md D-FM-10, the visible joint between adjacent panels. Assumed
#: (A-024); the world table carries it so a later stage can inset each panel by
#: half without re-reading the registry. D-FM-10's own declared default, on the
#: same reasoning as D-CL-05 above.
JOINT_WIDTH_CM = 2.0
JOINT_WIDTH_RANGE_CM = (1.0, 4.0)
PANEL_THICKNESS_LEDGER = "A-023"
JOINT_WIDTH_LEDGER = "A-024"

#: 09-defaults.md D-OP-12 (curtain-wall pier 15 cm, range 10 ... 25) x 2. The one
#: threshold in P5; contract section 4 step 9.
PIER_MAX_CM = 30.0

#: Contract section 4 step 13 -- which `massing.json` kinds may act as a panel's
#: `host_ref`, the solid an opening is punched into. Only an *exterior envelope*
#: band qualifies, and today those are the perimeter bands `plinth` and `parapet`.
#: `slab`, `column`, `core_wall` and `roof_deck` are excluded on purpose and not
#: because they fail the geometry: a floor plate's plan is the whole footprint, so
#: its south edge *is* the south facade line, and no amount of measuring separates
#: "a wall standing on this line" from "a slab whose outline happens to include it".
#: Only the kind says which. A project that needs a punched opening in an opaque
#: wall adds a `facade_wall` kind to `massing.json` through 07 section 12 step 1 --
#: P3's table to change -- and appends it here. The two perimeter bands that do
#: qualify are then excluded by the z test alone: they sit above the top storey,
#: so no panel's storey band overlaps them, which is why every `host_ref` in the
#: worked example is null.
HOST_ELIGIBLE_KINDS: tuple[str, ...] = ("plinth", "parapet")

AXIS_ID_RE = re.compile(r"^AX-\d{3}$")
PANEL_ID_RE = re.compile(r"^PNL-\d{3}$")
COMPONENT_ID_RE = re.compile(r"^CMP-\d{3}$")
FAMILY_ID_RE = re.compile(r"^FAM-\d{3}$")
VARIANT_ID_RE = re.compile(r"^VAR-\d{3}$")
PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
NODE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

#: Contract section 3.5. The six reserved names and the ceiling G-63 holds.
PANEL_KINDS: tuple[str, ...] = (
    "vision",
    "punched_window",
    "spandrel",
    "transom",
    "mullion",
    "blank",
)
#: kind -> (glazed, frame_member). G-63 holds the two flags and material_role in
#: step with each other.
PANEL_KIND_FLAGS: dict[str, tuple[bool, bool]] = {
    "vision": (True, False),
    "punched_window": (True, False),
    "spandrel": (False, False),
    "transom": (False, True),
    "mullion": (False, True),
    "blank": (False, False),
}
MATERIAL_ROLE: dict[str, str] = {
    "vision": "glazing",
    "punched_window": "glazing",
    "spandrel": "opaque",
    "transom": "frame",
    "mullion": "frame",
    "blank": "opaque",
}
MATERIAL_ROLES: tuple[str, ...] = ("glazing", "opaque", "frame")

AXIS_FAMILIES: tuple[str, ...] = ("u", "v")
AXIS_KINDS: tuple[str, ...] = ("bay", "opening_edge", "level_base", "level_top")

#: Contract section 5.3 and 5.6. The panel kind decides the component kind; the
#: `door` / `entrance` flag comes from the opening the panel realises, never from
#: a preference.
COMPONENT_KINDS: tuple[str, ...] = (
    "glazed_panel",
    "opaque_panel",
    "frame_member",
    "entrance_door",
)
COMPONENT_KIND_FLAGS: dict[str, tuple[bool, bool]] = {
    "glazed_panel": (True, False),
    "opaque_panel": (False, False),
    "frame_member": (False, True),
    "entrance_door": (True, False),
}
DOOR_TYPES: tuple[str, ...] = ("door", "entrance")

#: 07 section 9.1 G-9 -- keys outside the origins coverage rule. Copied from the
#: siblings so a P5 leaf is the same set of leaves a G-9 walk sees.
COVERAGE_EXEMPT_TOP = frozenset(
    {
        "schema_version",
        "spec",
        "project",
        "units",
        "source",
        "status",
        "tolerances",
        "origins",
        "origin_inputs",
    }
)
COVERAGE_EXEMPT_KEYS = frozenset({"id", "name", "index"})
COVERAGE_EXEMPT_SUFFIXES = ("_index", "_indices")

#: The ordered four-element parameter list, contract section 5.4.
PARAMETER_ORDER: tuple[tuple[str, str], ...] = (
    ("width_cm", "size_cm"),
    ("height_cm", "size_cm"),
    ("thickness_cm", "defaults"),
    ("joint_width_cm", "defaults"),
)

FACADE_CSV_COLUMNS: tuple[str, ...] = (
    "panel_id",
    "facade",
    "level_index",
    "bay_index",
    "kind",
    "component_kind",
    "opening_ref",
    "host_ref",
    "full_height",
    "u_min_cm",
    "u_max_cm",
    "v_min_cm",
    "v_max_cm",
    "width_cm",
    "height_cm",
    "centre_x_cm",
    "centre_y_cm",
    "centre_z_cm",
    "u_axis_min",
    "u_axis_max",
    "v_axis_min",
    "v_axis_max",
    "run_angle_deg",
)
WORLD_CSV_COLUMNS: tuple[str, ...] = (
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

RULES: tuple[str, ...] = tuple(f"G-{number}" for number in range(57, 71))

TOLERANCE_EPSILON = 1e-9

_TOKEN_RE = re.compile(r"([^.\[\]]+)|\[(\d+)\]")

EXIT_OK = 0
EXIT_REFUSAL = 1
EXIT_USAGE = 2


class Refusal(Exception):
    """A deliberate non-zero exit. The message names the file, id, key path or rule."""


class Checks:
    """One row per rule: pass, skip with a reason, or fail with a message."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def pass_(self, rule: str, message: str) -> None:
        self.rows.append((rule, "pass", message))

    def skip(self, rule: str, message: str) -> None:
        self.rows.append((rule, "skip", message))

    def fail(self, rule: str, message: str) -> None:
        self.rows.append((rule, "fail", message))

    def failures(self) -> list[str]:
        return [f"{rule}: {message}" for rule, status, message in self.rows if status == "fail"]

    def tally(self) -> dict[str, int]:
        counts = {"pass": 0, "skip": 0, "fail": 0}
        for _, status, _ in self.rows:
            counts[status] += 1
        return counts

    def by_rule(self) -> dict[str, str]:
        return {rule: status for rule, status, _ in self.rows}

    def skips(self) -> list[str]:
        return [f"{rule}: {message}" for rule, status, message in self.rows if status == "skip"]

    def replace(self, rule: str, status: str, message: str) -> None:
        """Overwrite a row once the fact it reported has actually been observed.

        G-70 is the only user: the self-check runs before the CSVs exist, so it
        reports SKIP naming that reason, and the read-back then turns the same row
        into a PASS carrying the counts it measured off disk. Leaving the SKIP in
        place would claim the rule is unevaluated when it has just been evaluated.
        """
        for position, (recorded, _status, _message) in enumerate(self.rows):
            if recorded == rule:
                self.rows[position] = (rule, status, message)
                return
        self.rows.append((rule, status, message))


# --------------------------------------------------------------------------- #
# Determinism and tolerance helpers -- the same ones build_nurbs.py uses
# --------------------------------------------------------------------------- #


def q(value: Any) -> float:
    """Round to 6 decimals and normalise -0.0, so the bytes never wobble."""
    number = float(value)
    rounded = round(number, 6)
    return 0.0 if rounded == 0.0 else rounded


def inum(value: Any) -> int:
    return int(round(float(value)))


def num(value: Any) -> str:
    """Float literal through q(): 1800 -> '1800.0', 1357.5 -> '1357.5'."""
    number = q(value)
    if float(number).is_integer():
        return f"{int(number)}.0"
    return repr(float(number))


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def parse_number(text: Any) -> float | None:
    """Read a number back out of a CSV field.

    ``as_float`` refuses a string on purpose -- a CSV column is text -- so the
    read-back needs its own parse, and it must reject anything that is not a
    number rather than guessing.
    """
    try:
        return float(str(text))
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None or not float(number).is_integer():
        return None
    return int(number)


def close(left: Any, right: Any, tolerance: float) -> bool:
    a = as_float(left)
    b = as_float(right)
    if a is None or b is None:
        return False
    return abs(a - b) <= tolerance + TOLERANCE_EPSILON


def in_range(value: Any, low: float, high: float, tolerance: float) -> bool:
    number = as_float(value)
    if number is None:
        return False
    return (
        low - tolerance - TOLERANCE_EPSILON <= number <= high + tolerance + TOLERANCE_EPSILON
    )


def node_name(spec_id: Any) -> str:
    """11 section 3.1 rule N1: a node name is the spec id with the dashes replaced.

    ``PNL-001`` -> ``PNL_001``, ``CMP-004`` -> ``CMP_004``. Every ``name`` either
    file carries goes through this one function, so the JSON name and the scene
    node name cannot disagree.
    """
    return str(spec_id).replace("-", "_")


def _tolerance(
    document: dict[str, Any], dimensions: dict[str, Any] | None, key: str, fallback: float
) -> tuple[float, str]:
    for label, candidate in (("this file's", document), ("dimensions.json's", dimensions)):
        block = candidate.get("tolerances") if isinstance(candidate, dict) else None
        value = as_float(block.get(key)) if isinstance(block, dict) else None
        if value is not None and value >= 0.0:
            return value, f"{label} tolerances.{key}"
    return fallback, (
        f"07 section 3.3's declared {fallback} (neither this file nor dimensions.json declares "
        f"tolerances.{key})"
    )


def linear_tolerance(
    document: dict[str, Any], dimensions: dict[str, Any] | None
) -> tuple[float, str]:
    """``tolerances.linear_cm`` for an arithmetic comparison, and where it came from.

    This file's own block wins, then ``dimensions.json``'s, then 07 section 3.3's
    declared 0.5 cm -- the same fallback order `build_nurbs.py` uses, so a P5
    boundary decision matches a P4b one.
    """
    return _tolerance(document, dimensions, "linear_cm", 0.5)


def angle_tolerance(
    document: dict[str, Any], dimensions: dict[str, Any] | None
) -> tuple[float, str]:
    return _tolerance(document, dimensions, "angle_deg", 0.01)


def area_tolerance(
    document: dict[str, Any], dimensions: dict[str, Any] | None
) -> tuple[float, str]:
    return _tolerance(document, dimensions, "area_m2", 0.05)


def split_path(path: str) -> list[Any]:
    tokens: list[Any] = []
    position = 0
    while position < len(path):
        match = _TOKEN_RE.match(path, position)
        if match is None:
            return []
        name, index = match.group(1), match.group(2)
        tokens.append(name if name is not None else int(index))
        position = match.end()
        if position < len(path) and path[position] == ".":
            position += 1
    return tokens


def resolve(document: Any, path: str) -> tuple[bool, Any]:
    """Resolve a dotted path against a parsed document. Mirrors the G-9 machinery."""
    tokens = split_path(path)
    if not tokens and path:
        return False, None
    node = document
    for token in tokens:
        if isinstance(token, int):
            if not isinstance(node, list) or not 0 <= token < len(node):
                return False, None
            node = node[token]
        else:
            if not isinstance(node, dict) or token not in node:
                return False, None
            node = node[token]
    return True, node


def is_origin_exempt_key(key: str) -> bool:
    return key in COVERAGE_EXEMPT_KEYS or key.endswith(COVERAGE_EXEMPT_SUFFIXES)


def collect_leaves(document: Any) -> list[str]:
    """Every leaf path that needs an ``origins`` entry, in file order.

    The same walk as G-9 and as both siblings: an array of scalars is one leaf, an
    array of objects is descended into, and the envelope, ``tolerances``,
    ``origins``, ``origin_inputs``, ``id`` / ``name`` / ``index`` and ``*_index``
    keys are outside the rule.
    """
    leaves: list[str] = []

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                if prefix == "" and key in COVERAGE_EXEMPT_TOP:
                    continue
                if is_origin_exempt_key(key):
                    continue
                walk(child, f"{prefix}.{key}" if prefix else key)
        elif isinstance(node, list):
            if not any(isinstance(item, dict) for item in node):
                if prefix:
                    leaves.append(prefix)
                return
            for index, item in enumerate(node):
                walk(item, f"{prefix}[{index}]")
        elif prefix:
            leaves.append(prefix)

    walk(document, "")
    return leaves


def covers(entry: str, leaf: str) -> bool:
    return entry == leaf or leaf.startswith(entry + ".")


def strict_loads(text: str) -> Any:
    def _reject(name: str) -> Any:
        raise ValueError(f"JSON constant {name} is not allowed (07 G-7)")

    return json.loads(text, parse_constant=_reject)


def _round_tree(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _round_tree(child) for key, child in node.items()}
    if isinstance(node, list):
        return [_round_tree(child) for child in node]
    if isinstance(node, bool) or node is None or isinstance(node, str):
        return node
    if isinstance(node, int):
        return node
    if isinstance(node, float):
        return q(node)
    return node


def serialize(document: dict[str, Any], name: str) -> str:
    try:
        body = json.dumps(_round_tree(document), indent=2, ensure_ascii=False, allow_nan=False)
    except ValueError as exc:
        raise Refusal(f"refusing to write: {name} is not strict JSON -- {exc} (07 G-7).") from exc
    return body + "\n"


def write_bytes(path: Path, text: str) -> None:
    data = text.encode("utf-8")
    if b"\r" in data:
        raise Refusal(f"refusing to write {path}: the payload contains CR (07 G-7).")
    if not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise Refusal(f"refusing to write {path}: it must end with exactly one LF (07 G-7).")
    if path.is_file():
        existing_bytes = path.read_bytes()
        if existing_bytes != data:
            raise Refusal(
                f"refusing to overwrite {path}: differing existing content on disk (08.4 / A-WRITE / M34). "
                "Resolve difference or remove file before rebuilding."
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_p = path.parent / f"{path.name}.tmp.{os.getpid()}"
    try:
        with open(tmp_p, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_p, path)
    finally:
        if tmp_p.exists():
            try:
                tmp_p.unlink()
            except OSError:
                pass


def first_difference(left: Any, right: Any, path: str = "") -> str | None:
    """First differing key path between two parsed trees, in a deterministic order.

    Dicts are walked in sorted key order and lists in index order, so two runs over
    the same pair of documents always name the same path. That is the whole point
    of the obligation: a refusal the caller can act on.
    """
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}" if path else key
            if key not in left:
                return f"{child} (absent on disk, present in this build)"
            if key not in right:
                return f"{child} (present on disk, absent in this build)"
            found = first_difference(left[key], right[key], child)
            if found is not None:
                return found
        return None
    if isinstance(left, list) and isinstance(right, list):
        for index in range(max(len(left), len(right))):
            child = f"{path}[{index}]"
            if index >= len(left):
                return f"{child} (absent on disk, present in this build)"
            if index >= len(right):
                return f"{child} (present on disk, absent in this build)"
            found = first_difference(left[index], right[index], child)
            if found is not None:
                return found
        return None
    if isinstance(left, bool) or isinstance(right, bool):
        return None if left == right else (path or "(root)")
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return None if q(left) == q(right) else (path or "(root)")
    return None if left == right else (path or "(root)")


# --------------------------------------------------------------------------- #
# Reading the locked inputs -- 07 section 3.1, G-2, G-3, G-7
# --------------------------------------------------------------------------- #


def read_spec(
    specs_dir: Path,
    name: str,
    allow_draft: bool,
    required_keys: Sequence[str] = (),
    expected_project: str | None = None,
) -> dict[str, Any]:
    """Never build from anything that is not ``locked`` (07 section 3.1)."""
    path = specs_dir / name
    if not path.is_file():
        raise Refusal(
            f"refusing to build: {name} not found in {specs_dir}. P5 reads the locked "
            "dimensional contract and the locked massing before it can place a single panel "
            "(07 section 3.1)."
        )
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise Refusal(
            f"refusing to build: {path} starts with a UTF-8 BOM (07 G-7). Strip it and lock "
            "the file again."
        )
    try:
        document = strict_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal(
            f"refusing to build: {path} is not strict JSON -- {exc}. A half-read brief must "
            "never become geometry (07 section 3.1)."
        ) from exc
    if not isinstance(document, dict):
        raise Refusal(
            f"refusing to build: {path} top level is {type(document).__name__}, not an object "
            "(07 section 3.1)."
        )

    status = document.get("status")
    if status != "locked" and not allow_draft:
        raise Refusal(
            f"refusing to build: {path} has status {status!r}, not 'locked'. 07 section 3.1: a "
            "builder must refuse to consume a draft or superseded file and must say which file "
            "and which status it found. Pass --allow-draft to build a draft anyway; G-57..G-70 "
            "will then run and fail."
        )

    version = document.get("schema_version")
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?$", str(version)) if isinstance(version, str) else None
    if (
        match is None
        or int(match.group(1)) != SUPPORTED_SCHEMA_MAJOR
        or int(match.group(2)) not in SUPPORTED_SCHEMA_MINORS
    ):
        raise Refusal(
            f"refusing to build: {path} declares schema_version {version!r}; this builder "
            f"implements major {SUPPORTED_SCHEMA_MAJOR} and supports versions 1.0 and 1.1 "
            "and must stop rather than guess (07 G-3)."
        )

    project = document.get("project")
    if not isinstance(project, str) or not PROJECT_ID_RE.match(project):
        raise Refusal(
            f"refusing to build: {path} project {project!r} does not match 07 section 3.1 "
            "^[a-z0-9][a-z0-9._-]*$."
        )
    if expected_project is not None and project != expected_project:
        raise Refusal(
            f"refusing to build: {path} project {project!r} does not match "
            f"expected project {expected_project!r} (cross-file consistency, 07 section 3.1)."
        )

    if document.get("spec") != path.stem:
        raise Refusal(
            f"refusing to build: {path} declares spec {document.get('spec')!r}, not "
            f"{path.stem!r} (07 G-2)."
        )

    units = document.get("units")
    if not isinstance(units, dict) or units.get("length") != "cm" or units.get("angle") != "deg":
        raise Refusal(
            f"refusing to build: {path} units {units!r} are not cm/deg (07 section 2, G-5)."
        )

    for key in required_keys:
        if key not in document:
            raise Refusal(
                f"refusing to build: {path} is missing {key!r}, which the contract section 4 "
                "derivation reads."
            )
    return document


def read_downstream(
    specs_dir: Path, name: str, expected_project: str | None = None
) -> dict[str, Any]:
    """Read a P5 file this stage consumes as an input rather than recomputing.

    ``--stage components`` reads ``facade_grids.json`` and ``--stage tables`` reads
    both P5 JSONs. They are this stage's own products, so their ``status`` is
    reported rather than enforced -- but a hand-edited grid must still parse
    strictly (G-7) and declare its own spec (G-2).
    """
    path = specs_dir / name
    if not path.is_file():
        raise Refusal(
            f"refusing to build: {name} not found in {specs_dir}. Run --stage all, or the "
            "earlier stage, first; --stage tables reads the file it is asked to tabulate rather "
            "than recomputing it."
        )
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise Refusal(f"refusing to build: {path} starts with a UTF-8 BOM (07 G-7).")
    try:
        document = strict_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal(f"refusing to build: {path} is not strict JSON -- {exc} (07 G-7).") from exc
    if not isinstance(document, dict):
        raise Refusal(f"refusing to build: {path} top level is not an object (07 section 3.1).")
    if document.get("spec") != path.stem:
        raise Refusal(
            f"refusing to build: {path} declares spec {document.get('spec')!r}, not "
            f"{path.stem!r} (07 G-2)."
        )
    version = document.get("schema_version")
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?$", str(version)) if isinstance(version, str) else None
    if (
        match is None
        or int(match.group(1)) != SUPPORTED_SCHEMA_MAJOR
        or int(match.group(2)) not in SUPPORTED_SCHEMA_MINORS
    ):
        raise Refusal(
            f"refusing to build: {path} declares schema_version {version!r}; this builder "
            f"implements major {SUPPORTED_SCHEMA_MAJOR} and supports versions 1.0 and 1.1 "
            "(07 G-3)."
        )

    project = document.get("project")
    if not isinstance(project, str) or not PROJECT_ID_RE.match(project):
        raise Refusal(
            f"refusing to build: {path} project {project!r} does not match 07 section 3.1 "
            "^[a-z0-9][a-z0-9._-]*$."
        )
    if expected_project is not None and project != expected_project:
        raise Refusal(
            f"refusing to build: {path} project {project!r} does not match "
            f"expected project {expected_project!r} (cross-file consistency, 07 section 3.1)."
        )

    units = document.get("units")
    if not isinstance(units, dict) or units.get("length") != "cm" or units.get("angle") != "deg":
        raise Refusal(
            f"refusing to build: {path} units {units!r} are not cm/deg (07 section 2, G-5)."
        )

    return document


def read_optional(specs_dir: Path, name: str) -> dict[str, Any] | None:
    path = specs_dir / name
    if not path.is_file():
        return None
    try:
        document = strict_loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return document if isinstance(document, dict) else None


# --------------------------------------------------------------------------- #
# Contract section 4 -- the derivation, step for step
# --------------------------------------------------------------------------- #


def run_angle_deg(start: Sequence[float], end: Sequence[float]) -> float:
    """``atan2(dy, dx)`` normalised to ``(-180, 180]``.

    ``180.0`` stays ``180.0`` and is not folded to ``-180.0``: the half-open
    interval is what G-57 states, and folding it would move a facade's rotation to
    the other side of the branch cut for no reason.
    """
    angle = math.degrees(
        math.atan2(float(end[1]) - float(start[1]), float(end[0]) - float(start[0]))
    )
    if angle <= -180.0:
        angle += 360.0
    if angle > 180.0:
        angle -= 360.0
    return q(angle)


def merge_offsets(values: Sequence[float], tolerance: float) -> list[float]:
    """Sort ascending and drop any value within ``tolerance`` of the one kept.

    The smaller is kept, so a merged grid never loses its low end and a cell never
    inverts. Contract section 4 step 3.
    """
    kept: list[float] = []
    for value in sorted(q(item) for item in values):
        if kept and value - kept[-1] <= tolerance + TOLERANCE_EPSILON:
            continue
        kept.append(value)
    return kept


def bay_of(u_mid: float, offsets: Sequence[float], count: int) -> int:
    """The bay whose ``[offset, offset + width)`` contains ``u_mid``.

    The last bay is closed at its far end, so a facade's own far corner lands in
    bay ``count - 1`` instead of off the end of the array.
    """
    for index in range(count):
        low = offsets[index]
        high = offsets[index + 1] if index + 1 < len(offsets) else float("inf")
        if low - TOLERANCE_EPSILON <= u_mid < high:
            return index
    return count - 1


def line_distance(point: Sequence[float], start: Sequence[float], end: Sequence[float]) -> float:
    """Distance from ``point`` to the infinite line through ``start`` and ``end``."""
    ax, ay = float(start[0]), float(start[1])
    bx, by = float(end[0]), float(end[1])
    dx, dy = bx - ax, by - ay
    denominator = math.hypot(dx, dy)
    if denominator <= 0.0:
        return math.dist((float(point[0]), float(point[1])), (ax, ay))
    return abs(dx * (ay - float(point[1])) - (ax - float(point[0])) * dy) / denominator


def classify_cell(
    openings: Sequence[dict[str, Any]],
    curtain: Sequence[dict[str, Any]],
    bay_index: int,
    u_mid: float,
    width: float,
    v_min: float,
    v_max: float,
    tolerance: float,
) -> tuple[str, dict[str, Any] | None]:
    """Contract section 4 step 8, first match wins. Rule 8.3 is decided per u cell.

    Returns the kind and the hit opening (``None`` for a frame member or an
    infill), so step 10 fills ``opening_ref`` without a second search. Rules 8.1
    and 8.2 both require a hit whose ``v_mid`` lies inside ``[sill, head]``; since
    sill and head are themselves v axes the hit's v-range also contains the cell's,
    so one test serves both rules.
    """
    v_mid = q((v_min + v_max) / 2.0)
    for opening in openings:
        if opening["bay_index"] != bay_index:
            continue
        if not (opening["u0"] - tolerance <= u_mid <= opening["u1"] + tolerance):
            continue
        if not (opening["sill"] - tolerance <= v_mid <= opening["head"] + tolerance):
            continue
        return ("vision" if opening["type"] == "curtain_wall" else "punched_window"), opening

    for opening in curtain:
        if close(v_min, opening["head"], tolerance) and close(
            width, q(opening["u1"] - opening["u0"]), tolerance
        ):
            return "transom", None

    for opening in openings:
        if close(v_max, opening["sill"], tolerance) and close(
            width, q(opening["u1"] - opening["u0"]), tolerance
        ):
            return "spandrel", None

    return "blank", None


class GridModel:
    """The grid builder's working state: documents, provenance notes, counters."""

    def __init__(self, dimensions: dict[str, Any], massing: dict[str, Any]) -> None:
        self.dimensions = dimensions
        self.massing = massing
        self.facades: list[dict[str, Any]] = []
        self.axes: list[dict[str, Any]] = []
        self.panels: list[dict[str, Any]] = []
        self.sources: dict[str, list[str]] = {}
        self.axis_index: dict[str, int] = {}
        self.kind_first_panel: dict[str, int] = {}
        self.axis_counter = 0
        self.panel_counter = 0
        self.hosts: list[str] = []
        self.openings_by_id: dict[str, str] = {
            str(opening.get("id")): str(opening.get("type"))
            for opening in (dimensions.get("openings") or [])
            if isinstance(opening, dict)
        }

    def opening_type(self, opening_id: str) -> str | None:
        """The `dimensions.openings[].type` behind an ``opening_ref``, or ``None``.

        Panel kinds hold an opening *id*, not a type, so the registry needs this
        lookup to decide `entrance_door` (contract section 5.6). It is the only
        place a panel kind reaches across to the brief.
        """
        return self.openings_by_id.get(opening_id)

    # -- provenance (G-64) ------------------------------------------------ #

    def note(self, leaf_path: str, inputs: Sequence[str]) -> None:
        self.sources[leaf_path] = [str(item) for item in inputs]

    # -- axis classification, contract section 4 steps 3 and 4 ------------- #

    @staticmethod
    def axis_kind(
        family: str,
        offset: float,
        bay_offsets: Sequence[float],
        openings: Sequence[dict[str, Any]],
        tolerance: float,
    ) -> str:
        if family == "u":
            if any(close(offset, bay, tolerance) for bay in bay_offsets):
                return "bay"
            return "opening_edge"
        if close(offset, 0.0, tolerance):
            return "level_base"
        for opening in openings:
            if close(offset, opening["sill"], tolerance) or close(offset, opening["head"], tolerance):
                return "opening_edge"
        return "level_top"

    @staticmethod
    def axis_inputs(
        family: str, kind: str, openings: Sequence[dict[str, Any]]
    ) -> list[str]:
        """Where an axis's offset came from, as paths that resolve upstream.

        A ``u`` axis is cut by the bay widths or by an opening's position and
        width; a ``v`` axis by the storey height or by the **sill and head of the
        openings in its own bay** -- and ``openings`` is that bay's group, because
        a v axis belongs to one bay (contract section 4 steps 3 and 4).
        """
        if family == "u":
            if kind == "bay":
                return ["facades"]
            keys = ("position_cm", "width_cm")
        else:
            if kind in ("level_base", "level_top"):
                return ["levels"]
            keys = ("sill_cm", "head_cm")
        paths: list[str] = []
        for opening in openings:
            for key in keys:
                paths.append(f"openings[{opening['index']}].{key}")
        return paths or ["levels"]

    # -- one axis --------------------------------------------------------- #

    def add_axis(
        self,
        facade_id: str,
        level_index: int,
        family: str,
        bay_index: int | None,
        kind: str,
        offset: float,
        inputs: Sequence[str],
    ) -> str:
        self.axis_counter += 1
        identifier = f"AX-{self.axis_counter:03d}"
        index = len(self.axes)
        self.axes.append(
            {
                "id": identifier,
                "facade": facade_id,
                "level_index": int(level_index),
                "bay_index": None if bay_index is None else int(bay_index),
                "family": family,
                "kind": kind,
                "offset_cm": q(offset),
            }
        )
        self.axis_index[identifier] = index
        self.note(f"axes[{index}].facade", ["facades"])
        # bay_index is a function of the family and of which openings are admitted:
        # null for a u axis (a horizontal line runs the whole run), the bay for a v
        # axis (a spandrel line belongs to one bay's elevation). Contract 3.3.
        self.note(f"axes[{index}].bay_index", [f"axes[{index}].family"] + list(inputs))
        self.note(f"axes[{index}].family", [f"axes[{index}].kind"])
        self.note(f"axes[{index}].kind", list(inputs))
        self.note(f"axes[{index}].offset_cm", list(inputs))
        return identifier

    # -- one panel, contract section 4 steps 10 to 14 --------------------- #

    def host_for(
        self,
        facade_start: Sequence[float],
        facade_end: Sequence[float],
        elevation: float,
        level_height: float,
        elements: Sequence[dict[str, Any]],
        tolerance: float,
    ) -> str | None:
        """Contract section 4 step 13: is a massing element on this facade line?

        Three executed conditions, on top of the kind test in
        :data:`HOST_ELIGIBLE_KINDS`: at least two vertices of the element's
        ``profile_cm`` lie on the facade's infinite line within ``linear_cm``; those
        vertices are the ends of a run *along* the line rather than a pair of
        unrelated corners; and the element's ``z_range_cm`` overlaps the storey band
        by more than ``linear_cm``. The four parapet bands of the worked example
        pass the first two and fail the third -- they sit above the top storey -- so
        every panel's ``host_ref`` is ``null``. That is a property of that massing,
        not a defect, and CHECKPOINT.md records it.
        """
        for element in elements:
            if not isinstance(element, dict):
                continue
            if str(element.get("kind")) not in HOST_ELIGIBLE_KINDS:
                continue
            profile = element.get("profile_cm")
            z_range = element.get("z_range_cm")
            if not isinstance(profile, list) or not isinstance(z_range, list) or len(z_range) != 2:
                continue
            vertices = [
                vertex
                for vertex in profile
                if isinstance(vertex, list) and len(vertex) == 2
            ]
            on_line = [
                vertex
                for vertex in vertices
                if line_distance(vertex, facade_start, facade_end) <= tolerance
            ]
            if len(on_line) < 2:
                continue
            # The two vertices on the line have to be the ends of a run *along* it,
            # not a pair of unrelated corners, so the run length is compared with
            # the element's own extent along the run direction.
            run = math.hypot(
                float(facade_end[0]) - float(facade_start[0]),
                float(facade_end[1]) - float(facade_start[1]),
            )
            unit_x = (float(facade_end[0]) - float(facade_start[0])) / run
            unit_y = (float(facade_end[1]) - float(facade_start[1])) / run
            along = [
                (float(vertex[0]) - float(facade_start[0])) * unit_x
                + (float(vertex[1]) - float(facade_start[1])) * unit_y
                for vertex in on_line
            ]
            if abs(max(along) - min(along)) <= tolerance:
                continue
            low = as_float(z_range[0])
            high = as_float(z_range[1])
            if low is None or high is None:
                continue
            overlap = min(high, elevation + level_height) - max(low, elevation)
            if overlap > tolerance:
                identifier = str(element.get("id"))
                if identifier not in self.hosts:
                    self.hosts.append(identifier)
                return identifier
        return None


def build_grids(dimensions: dict[str, Any], massing: dict[str, Any]) -> tuple[dict[str, Any], GridModel]:
    """Contract section 4 steps 1 to 14, as a literal numbered procedure.

    Returns ``(document, model)``. Every number is rounded through :func:`q` where
    it is computed, so the emitted bytes are stable; every leaf records the paths
    it came from, which :func:`build_grid_origins` turns into ``origins`` and G-64
    re-checks against ``dimensions.json``, ``massing.json`` and this file.
    """
    tolerance, tolerance_source = linear_tolerance(dimensions, None)
    model = GridModel(dimensions, massing)

    facade_entries = dimensions.get("facades")
    level_entries = dimensions.get("levels")
    opening_entries = dimensions.get("openings")
    if not isinstance(facade_entries, list) or not facade_entries:
        raise Refusal(
            "refusing to build: dimensions.json facades[] is missing or empty. Contract "
            "section 4 step 1 has nothing to copy."
        )
    if not isinstance(level_entries, list) or not level_entries:
        raise Refusal("refusing to build: dimensions.json levels[] is missing or empty.")
    if not isinstance(opening_entries, list):
        raise Refusal("refusing to build: dimensions.json openings[] is missing or not an array.")

    elements = massing.get("elements") if isinstance(massing.get("elements"), list) else []

    for facade_position, facade in enumerate(facade_entries):
        if not isinstance(facade, dict):
            raise Refusal(
                f"refusing to build: dimensions.json facades[{facade_position}] is not an object."
            )
        stem = f"facades[{facade_position}]"
        facade_id = str(facade.get("id"))
        for key in (
            "name",
            "direction_deg",
            "start_corner_cm",
            "end_corner_cm",
            "length_cm",
            "bay_count",
            "bay_width_cm",
        ):
            if key not in facade:
                raise Refusal(
                    f"refusing to build: dimensions.json {stem} is missing {key!r}; contract "
                    "section 3.2 requires it."
                )
        start = [as_float(item) for item in facade["start_corner_cm"]]
        end = [as_float(item) for item in facade["end_corner_cm"]]
        if len(start) != 2 or len(end) != 2 or any(
            item is None for item in start + end
        ):
            raise Refusal(
                f"refusing to build: {stem}.start_corner_cm and end_corner_cm must each hold two "
                "finite numbers."
            )
        bay_widths = [as_float(item) for item in facade["bay_width_cm"]]
        bay_count = as_int(facade["bay_count"])
        length = as_float(facade["length_cm"])
        if bay_count is None or bay_count < 1:
            raise Refusal(
                f"refusing to build: {stem}.bay_count {facade['bay_count']!r} is not an integer >= 1."
            )
        if len(bay_widths) != bay_count or any(width is None or width <= 0.0 for width in bay_widths):
            raise Refusal(
                f"refusing to build: {stem}.bay_width_cm must hold {bay_count} positive numbers "
                f"(found {len(bay_widths)})."
            )
        if length is None or length <= 0.0:
            raise Refusal(f"refusing to build: {stem}.length_cm {facade['length_cm']!r} is not > 0.")
        run_length = math.hypot(end[0] - start[0], end[1] - start[1])
        if not close(run_length, length, tolerance):
            raise Refusal(
                f"refusing to build: {stem} length_cm is {num(length)} but start_corner_cm -> "
                f"end_corner_cm measures {num(run_length)}; they differ by more than "
                f"{tolerance_source}. Every panel centre is computed from the run, so a wrong "
                "length puts every panel in the wrong place (G-57)."
            )

        # -- step 1: bay offsets, bay centres, run angle ------------------- #
        bay_offsets: list[float] = [0.0]
        for width in bay_widths:
            bay_offsets.append(q(bay_offsets[-1] + float(width)))
        if not close(bay_offsets[-1], length, tolerance):
            raise Refusal(
                f"refusing to build: {stem}.bay_width_cm sums to {num(bay_offsets[-1])} but "
                f"length_cm is {num(length)}; the bays do not tile the run."
            )
        bay_centre = [
            q(bay_offsets[index] + float(bay_widths[index]) / 2.0) for index in range(bay_count)
        ]
        angle = run_angle_deg(start, end)

        entry = {
            "id": facade_id,
            "name": str(facade["name"]),
            "direction_deg": q(facade["direction_deg"]),
            "start_corner_cm": [q(start[0]), q(start[1])],
            "end_corner_cm": [q(end[0]), q(end[1])],
            "length_cm": q(length),
            "bay_count": int(bay_count),
            "bay_width_cm": [q(float(width)) for width in bay_widths],
            "bay_offsets_cm": bay_offsets,
            "bay_centre_cm": bay_centre,
            "run_angle_deg": angle,
            "levels": [],
        }
        model.facades.append(entry)
        for key in (
            "direction_deg",
            "start_corner_cm",
            "end_corner_cm",
            "length_cm",
            "bay_count",
            "bay_width_cm",
        ):
            model.note(f"{stem}.{key}", [f"{stem}.{key}"])
        model.note(f"{stem}.bay_offsets_cm", [f"{stem}.bay_width_cm"])
        model.note(f"{stem}.bay_centre_cm", [f"{stem}.bay_offsets_cm", f"{stem}.bay_width_cm"])
        model.note(f"{stem}.run_angle_deg", [f"{stem}.start_corner_cm", f"{stem}.end_corner_cm"])

        unit = (
            (end[0] - start[0]) / float(length),
            (end[1] - start[1]) / float(length),
        )

        for level_position, level in enumerate(level_entries):
            if not isinstance(level, dict):
                continue
            level_index = as_int(level.get("index"))
            level_height = as_float(level.get("height_cm"))
            elevation = as_float(level.get("elevation_cm"))
            if level_index is None or level_height is None or elevation is None:
                raise Refusal(
                    f"refusing to build: dimensions.json levels[{level_position}] needs an integer "
                    "index, an elevation_cm and a height_cm."
                )
            if level_height <= 0.0:
                raise Refusal(
                    f"refusing to build: dimensions.json levels[{level_position}].height_cm is not "
                    "> 0; a storey with no height has no v grid."
                )

            # -- step 2: this (facade, level)'s openings, ordered ------------ #
            openings: list[dict[str, Any]] = []
            for opening_position, opening in enumerate(opening_entries):
                if not isinstance(opening, dict):
                    continue
                if str(opening.get("facade")) != facade_id:
                    continue
                if as_int(opening.get("level_index")) != level_index:
                    continue
                position = as_float(opening.get("position_cm"))
                width = as_float(opening.get("width_cm"))
                sill = as_float(opening.get("sill_cm"))
                head = as_float(opening.get("head_cm"))
                bay = as_int(opening.get("bay_index"))
                if None in (position, width, sill, head, bay):
                    raise Refusal(
                        f"refusing to build: dimensions.json openings[{opening_position}] is missing "
                        "position_cm, width_cm, sill_cm, head_cm or bay_index."
                    )
                openings.append(
                    {
                        "id": str(opening.get("id")),
                        "index": opening_position,
                        "type": str(opening.get("type")),
                        "bay_index": int(bay),
                        "u0": q(float(position) - float(width) / 2.0),
                        "u1": q(float(position) + float(width) / 2.0),
                        "sill": q(float(sill)),
                        "head": q(float(head)),
                    }
                )
            openings.sort(key=lambda item: (item["bay_index"], item["id"]))

            for opening in openings:
                opening_stem = f"openings[{opening['index']}]"
                if not in_range(opening["u0"], 0.0, float(length), tolerance) or not in_range(
                    opening["u1"], 0.0, float(length), tolerance
                ):
                    raise Refusal(
                        f"refusing to build: {opening_stem} ({opening['id']}) spans u "
                        f"{num(opening['u0'])}..{num(opening['u1'])} on a facade of {num(length)} cm; "
                        "G-27 keeps every opening inside its bay and its bay inside the run."
                    )
                if not in_range(
                    opening["sill"], 0.0, float(level_height), tolerance
                ) or not in_range(opening["head"], 0.0, float(level_height), tolerance):
                    raise Refusal(
                        f"refusing to build: {opening_stem} ({opening['id']}) has sill/head "
                        f"{num(opening['sill'])}/{num(opening['head'])} outside the storey band "
                        f"0..{num(level_height)}."
                    )

            # -- step 3: u axes, one set per (facade, level), bay_index null --- #
            u_offsets = merge_offsets(
                [float(value) for value in bay_offsets]
                + [float(opening["u0"]) for opening in openings]
                + [float(opening["u1"]) for opening in openings],
                tolerance,
            )
            for offset in bay_offsets:
                if not any(close(offset, kept, tolerance) for kept in u_offsets):
                    raise Refusal(
                        f"refusing to build: {facade_id} level {level_index}: bay boundary "
                        f"{num(offset)} was merged away by an opening edge, so the u grid no longer "
                        "carries every bay boundary and G-58 has nothing to match it against. "
                        "Widen the bay or narrow the offending opening."
                    )

            # -- step 4: v axes, one set per (bay, level) --------------------- #
            # The openings of this (facade, level) grouped by bay, each group in id
            # order. G-28 forbids two openings sharing (facade, level, bay), so a
            # group holds at most one entry -- the builder admits every member's
            # sill and head anyway, so a brief that breaks G-28 still produces a
            # grid and G-61 still decides whether that grid is a partition.
            by_bay: dict[int, list[dict[str, Any]]] = {index: [] for index in range(bay_count)}
            for opening in openings:
                opening_bay = int(opening["bay_index"])
                if opening_bay in by_bay:
                    by_bay[opening_bay].append(opening)
            v_by_bay: dict[int, list[float]] = {}
            for bay in range(bay_count):
                group = by_bay[bay]
                offsets = merge_offsets(
                    [0.0, float(level_height)]
                    + [float(opening["sill"]) for opening in group]
                    + [float(opening["head"]) for opening in group],
                    tolerance,
                )
                if (
                    not offsets
                    or not close(offsets[0], 0.0, tolerance)
                    or not close(offsets[-1], float(level_height), tolerance)
                ):
                    raise Refusal(
                        f"refusing to build: {facade_id} level {level_index} bay {bay}: the v grid "
                        f"runs {num(offsets[0]) if offsets else 'none'}.."
                        f"{num(offsets[-1]) if offsets else 'none'} but must start at 0 and end at "
                        f"the storey height {num(level_height)} (contract section 4 step 4)."
                    )
                v_by_bay[bay] = offsets

            # -- step 14, first half: AX ids ascending over u then v ----------- #
            axis_ids: dict[tuple[str, Any, float], str] = {}
            for offset in u_offsets:
                if not in_range(offset, 0.0, float(length), tolerance):
                    raise Refusal(
                        f"refusing to build: {facade_id} level {level_index}: a u axis offset "
                        f"{num(offset)} is outside 0..{num(length)}."
                    )
                kind = GridModel.axis_kind("u", offset, bay_offsets, openings, tolerance)
                axis_ids[("u", None, q(offset))] = model.add_axis(
                    facade_id,
                    int(level_index),
                    "u",
                    None,
                    kind,
                    offset,
                    GridModel.axis_inputs("u", kind, openings),
                )
            v_axis_ids: list[str] = []
            bay_v_axes: dict[int, tuple[str, str]] = {}
            for bay in range(bay_count):
                group = by_bay[bay]
                offsets = v_by_bay[bay]
                for offset in offsets:
                    if not in_range(offset, 0.0, float(level_height), tolerance):
                        raise Refusal(
                            f"refusing to build: {facade_id} level {level_index} bay {bay}: a v "
                            f"axis offset {num(offset)} is outside 0..{num(level_height)}."
                        )
                    kind = GridModel.axis_kind("v", offset, (), group, tolerance)
                    identifier = model.add_axis(
                        facade_id,
                        int(level_index),
                        "v",
                        bay,
                        kind,
                        offset,
                        GridModel.axis_inputs("v", kind, group),
                    )
                    axis_ids[("v", bay, q(offset))] = identifier
                    v_axis_ids.append(identifier)
                bay_v_axes[bay] = (
                    axis_ids[("v", bay, q(offsets[0]))],
                    axis_ids[("v", bay, q(offsets[-1]))],
                )

            level_entry = {
                "level_index": int(level_index),
                "elevation_cm": q(elevation),
                "height_cm": q(level_height),
                "u_axis_ids": [axis_ids[("u", None, q(offset))] for offset in u_offsets],
                "v_axis_ids": list(v_axis_ids),
            }
            entry["levels"].append(level_entry)
            level_stem = f"{stem}.levels[{len(entry['levels']) - 1}]"
            model.note(f"{level_stem}.elevation_cm", [f"levels[{level_position}].elevation_cm"])
            model.note(f"{level_stem}.height_cm", [f"levels[{level_position}].height_cm"])
            model.note(
                f"{level_stem}.u_axis_ids",
                [
                    f"axes[{model.axis_index[axis_ids[('u', None, q(offset))]]}].offset_cm"
                    for offset in u_offsets
                ],
            )
            # Every v axis at this facade and level, ordered by (bay_index, offset).
            # That is the order they were created in: bays ascend, and inside a bay
            # the offsets ascend, so no sort is needed and none may drift.
            model.note(
                f"{level_stem}.v_axis_ids",
                [
                    f"axes[{model.axis_index[reference]}].offset_cm"
                    for reference in v_axis_ids
                ]
                + [
                    f"axes[{model.axis_index[reference]}].bay_index"
                    for reference in v_axis_ids
                ],
            )

            # -- steps 5 to 12: cells, kinds and panels, per (facade, level, bay) #
            host = model.host_for(
                start, end, float(elevation), float(level_height), elements, tolerance
            )
            for bay in range(bay_count):
                # The tiling unit. The u cells still come from the facade-wide u
                # grid, but only this bay's slice of it, so every panel below takes
                # `bay_index` from the loop and never from a midpoint lookup.
                group = by_bay[bay]
                curtain = [opening for opening in group if opening["type"] == "curtain_wall"]
                v_offsets = v_by_bay[bay]
                v_base, v_top = bay_v_axes[bay]
                bay_low = float(bay_offsets[bay])
                bay_high = float(bay_offsets[bay + 1])
                first_u = next(
                    index
                    for index, offset in enumerate(u_offsets)
                    if close(offset, bay_low, tolerance)
                )
                last_u = next(
                    index
                    for index, offset in enumerate(u_offsets)
                    if close(offset, bay_high, tolerance)
                )

                for u_index in range(first_u, last_u):
                    u_min = u_offsets[u_index]
                    u_max = u_offsets[u_index + 1]
                    u_mid = q((u_min + u_max) / 2.0)
                    cell_width = q(u_max - u_min)

                    any_hit = False
                    for v_index in range(len(v_offsets) - 1):
                        v_mid = q((v_offsets[v_index] + v_offsets[v_index + 1]) / 2.0)
                        for opening in group:
                            if not opening["u0"] - tolerance <= u_mid <= opening["u1"] + tolerance:
                                continue
                            if not (
                                opening["sill"] - tolerance <= v_mid <= opening["head"] + tolerance
                            ):
                                continue
                            any_hit = True
                            break
                        if any_hit:
                            break

                    # -- rule 8.3: adjacent to a curtain-wall pier, not cut by v -- #
                    # One rule, one code path (contract section 4 step 8.3 as
                    # revised): the cell's own u-range touches the opening's
                    # corresponding u boundary and the cell is no wider than the
                    # derived pier threshold. Rules 8.1 and 8.2 come first, so a
                    # cell inside an opening is glass and never a frame member.
                    mullion_column = False
                    if not any_hit and cell_width <= PIER_MAX_CM + tolerance:
                        for opening in curtain:
                            # Adjacent means the two u-ranges *share a boundary*: the
                            # pier on the left ends where the opening starts, the pier
                            # on the right starts where the opening ends.
                            if close(u_max, opening["u0"], tolerance) or close(
                                u_min, opening["u1"], tolerance
                            ):
                                mullion_column = True
                                break

                    if mullion_column:
                        model.panels.append(
                            panel_entry(
                                model,
                                facade_position=facade_position,
                                facade_id=facade_id,
                                level_index=int(level_index),
                                level_position=level_position,
                                elevation=float(elevation),
                                level_height=float(level_height),
                                start=start,
                                unit=unit,
                                u_min=u_min,
                                u_max=u_max,
                                v_min=v_offsets[0],
                                v_max=v_offsets[-1],
                                u_axis_min=axis_ids[("u", None, q(u_min))],
                                u_axis_max=axis_ids[("u", None, q(u_max))],
                                v_axis_min=v_base,
                                v_axis_max=v_top,
                                bay_index=bay,
                                kind="mullion",
                                full_height=True,
                                opening=None,
                                host=host,
                                tolerance=tolerance,
                            )
                        )
                        continue

                    for v_index in range(len(v_offsets) - 1):
                        v_min = v_offsets[v_index]
                        v_max = v_offsets[v_index + 1]
                        kind, hit = classify_cell(
                            group,
                            curtain,
                            bay_index=bay,
                            u_mid=u_mid,
                            width=cell_width,
                            v_min=v_min,
                            v_max=v_max,
                            tolerance=tolerance,
                        )
                        model.panels.append(
                            panel_entry(
                                model,
                                facade_position=facade_position,
                                facade_id=facade_id,
                                level_index=int(level_index),
                                level_position=level_position,
                                elevation=float(elevation),
                                level_height=float(level_height),
                                start=start,
                                unit=unit,
                                u_min=u_min,
                                u_max=u_max,
                                v_min=v_min,
                                v_max=v_max,
                                u_axis_min=axis_ids[("u", None, q(u_min))],
                                u_axis_max=axis_ids[("u", None, q(u_max))],
                                v_axis_min=axis_ids[("v", bay, q(v_min))],
                                v_axis_max=axis_ids[("v", bay, q(v_max))],
                                bay_index=bay,
                                kind=kind,
                                # The flag is a statement about the extent, not about the
                                # kind: G-60 tests both directions, so it must equal
                                # "this panel's v-range is the whole storey band". True
                                # for a merged mullion, and equally for the single
                                # `blank` of a bay that declares no opening -- that
                                # bay contributes only level_base and level_top
                                # (contract section 4 step 4), so its one panel is not
                                # cut by its v grid. Contract section 3.4 still words
                                # `full_height` as "only a frame-member column", which
                                # cannot hold for an opening-less bay; the flag
                                # definition G-60 enforces is the one used here.
                                full_height=(
                                    close(v_min, 0.0, tolerance)
                                    and close(v_max, float(level_height), tolerance)
                                ),
                                opening=hit,
                                host=host,
                                tolerance=tolerance,
                            )
                        )

    panels = sort_and_number_panels(model)
    for position, panel in enumerate(panels):
        note_panel(model, position, panel)
    document = assemble_grids(model, dimensions, panels)
    return document, model


def note_panel(model: GridModel, position: int, panel: dict[str, Any]) -> None:
    """Record where each leaf of one panel came from, now that its id is fixed.

    ``@axis:`` expands to the ``axes[n].offset_cm`` of a bracketing axis and
    ``@self:`` to another leaf of the same panel; every other path is already a
    path in ``dimensions.json`` or ``massing.json``. G-64 resolves all of them.
    """
    stem = f"panels[{position}]"

    def expand(path: str) -> str:
        if path.startswith("@axis:"):
            reference = str(panel[path[len("@axis:"):]])
            return f"axes[{model.axis_index[reference]}].offset_cm"
        if path.startswith("@self:"):
            return f"{stem}.{path[len('@self:'):]}"
        return path

    for leaf, paths in panel["_inputs"].items():
        model.note(f"{stem}.{leaf}", [expand(path) for path in paths])


def panel_entry(
    model: GridModel,
    facade_position: int,
    facade_id: str,
    level_index: int,
    level_position: int,
    elevation: float,
    level_height: float,
    start: Sequence[float],
    unit: tuple[float, float],
    u_min: float,
    u_max: float,
    v_min: float,
    v_max: float,
    u_axis_min: str,
    u_axis_max: str,
    v_axis_min: str,
    v_axis_max: str,
    bay_index: int,
    kind: str,
    full_height: bool,
    opening: dict[str, Any] | None,
    host: str | None,
    tolerance: float,
) -> dict[str, Any]:
    """One panel: contract section 4 steps 10 to 12, plus its sort key and notes.

    ``u_mid`` and ``v_mid`` are the cell midpoints, and ``centre_cm`` is
    ``start_corner_cm + run_unit * u_mid`` in XY with ``Z = elevation_cm + v_mid``.
    A merged ``mullion`` keeps the cell's ``u_mid`` and uses the storey midpoint for
    ``v_mid``, because its ``v`` range is the whole storey.
    """
    u_mid = q((u_min + u_max) / 2.0)
    v_mid = q((v_min + v_max) / 2.0)
    centre = [
        q(float(start[0]) + unit[0] * u_mid),
        q(float(start[1]) + unit[1] * u_mid),
        q(elevation + v_mid),
    ]
    facade_stem = f"facades[{facade_position}]"
    level_stem = f"levels[{level_position}]"
    grid_inputs = [
        "@axis:u_axis_min",
        "@axis:u_axis_max",
        "@axis:v_axis_min",
        "@axis:v_axis_max",
    ]
    opening_inputs = (
        [
            f"openings[{opening['index']}].id",
            f"openings[{opening['index']}].facade",
            f"openings[{opening['index']}].level_index",
            f"openings[{opening['index']}].bay_index",
        ]
        if opening is not None
        else ["openings"]
    )
    inputs: dict[str, list[str]] = {
        "facade": ["facades"],
        "kind": list(grid_inputs) + ["openings", f"{level_stem}.height_cm"],
        "u_min_cm": ["@axis:u_axis_min"],
        "u_max_cm": ["@axis:u_axis_max"],
        "v_min_cm": ["@axis:v_axis_min"],
        "v_max_cm": ["@axis:v_axis_max"],
        "u_axis_min": ["@axis:u_axis_min"],
        "u_axis_max": ["@axis:u_axis_max"],
        "v_axis_min": ["@axis:v_axis_min"],
        "v_axis_max": ["@axis:v_axis_max"],
        "width_cm": ["@self:u_min_cm", "@self:u_max_cm"],
        "height_cm": ["@self:v_min_cm", "@self:v_max_cm"],
        "full_height": ["@self:v_min_cm", "@self:v_max_cm", f"{level_stem}.height_cm"],
        "opening_ref": opening_inputs,
        "host_ref": ["elements"],
        "centre_cm": [
            f"{facade_stem}.start_corner_cm",
            f"{facade_stem}.end_corner_cm",
            f"{facade_stem}.length_cm",
            f"{level_stem}.elevation_cm",
        ]
        + list(grid_inputs),
    }
    del tolerance, level_height
    return {
        "_facade_position": facade_position,
        "_inputs": inputs,
        "_level_position": level_position,
        "_level_index": level_index,
        "_facade": facade_id,
        "id": "",
        "facade": facade_id,
        "level_index": int(level_index),
        "kind": kind,
        "u_min_cm": q(u_min),
        "u_max_cm": q(u_max),
        "v_min_cm": q(v_min),
        "v_max_cm": q(v_max),
        "width_cm": q(u_max - u_min),
        "height_cm": q(v_max - v_min),
        "u_axis_min": u_axis_min,
        "u_axis_max": u_axis_max,
        "v_axis_min": v_axis_min,
        "v_axis_max": v_axis_max,
        "bay_index": int(bay_index),
        "full_height": bool(full_height),
        "opening_ref": opening["id"] if opening is not None else None,
        "host_ref": host,
        "centre_cm": centre,
        "layer": FACADE_LAYER,
    }


def sort_and_number_panels(model: GridModel) -> list[dict[str, Any]]:
    """Contract section 4 step 14: ``PNL-nnn`` ascending over facade order, level,
    ``bay_index``, ``v_min_cm``, ``u_min_cm``.

    Sorting before numbering is what makes the ids stable: the number is a rank, not
    a counter, so a rebuild that changes one panel's cell moves exactly one id.
    """
    ordered = sorted(
        model.panels,
        key=lambda panel: (
            panel["_facade_position"],
            panel["_level_index"],
            panel["bay_index"],
            panel["v_min_cm"],
            panel["u_min_cm"],
        ),
    )
    for position, panel in enumerate(ordered, start=1):
        panel["id"] = f"PNL-{position:03d}"
        model.kind_first_panel.setdefault(str(panel["kind"]), position - 1)
    return ordered


def build_grid_origins(document: dict[str, Any], model: GridModel, dimensions: dict[str, Any], massing: dict[str, Any]) -> dict[str, Any]:
    """One ``origins`` entry per leaf, in document order, all ``derived`` (G-64)."""
    origins: dict[str, Any] = {}
    for leaf in collect_leaves(document):
        if leaf in model.sources:
            origins[leaf] = {"origin": "derived", "derives_from": list(model.sources[leaf])}
            continue
        if leaf.endswith(".layer"):
            origins[leaf] = {
                "origin": "derived",
                "derives_from": ["spec"],
                "note": (
                    "the layer vocabulary is fixed by this stage's schema (07 section 8.1.3), so "
                    "the only in-file anchor is the file's own spec identity"
                ),
            }
            continue
        if leaf.endswith(".kind") and leaf.startswith("panel_types["):
            kind = resolve(document, leaf)[1]
            first = model.kind_first_panel.get(str(kind))
            if first is None:
                raise Refusal(
                    f"internal: panel_types declares {kind!r} but no panel uses it, so G-63 has "
                    "nothing to anchor it on."
                )
            origins[leaf] = {"origin": "derived", "derives_from": [f"panels[{first}].kind"]}
            continue
        raise Refusal(
            f"internal: leaf {leaf} has no provenance recorded; G-64 requires an origins entry "
            "for every leaf of facade_grids.json and every one of them is derived."
        )
    del dimensions, massing
    return origins


def origin_inputs_for(model: GridModel, dimensions: dict[str, Any], massing: dict[str, Any]) -> list[str]:
    """Sorted set of the paths this build read upstream.

    Only paths that resolve in ``dimensions.json`` or ``massing.json`` belong here:
    an in-file path is not an input, and G-64 checks that every entry resolves in
    one of the two.
    """
    inputs: set[str] = set()
    for paths in model.sources.values():
        for path in paths:
            if resolve(dimensions, path)[0] or resolve(massing, path)[0]:
                inputs.add(path)
    return sorted(inputs)


def assemble_grids(
    model: GridModel, dimensions: dict[str, Any], panels: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    """The emitted ``facade_grids.json``, envelope first in G-1 order."""
    massing = model.massing
    used_kinds: list[str] = []
    for panel in panels:
        if panel["kind"] not in used_kinds:
            used_kinds.append(panel["kind"])

    # panel_types: only the kinds this project's panels use, in the reserved order.
    panel_types: list[dict[str, Any]] = []
    hosted_types: dict[str, list[str]] = {kind: [] for kind in PANEL_KINDS}
    for panel in panels:
        if panel["opening_ref"] is None:
            continue
        opening_type = model.opening_type(str(panel["opening_ref"]))
        bucket = hosted_types[panel["kind"]]
        if opening_type not in bucket:
            bucket.append(opening_type)
    for kind in PANEL_KINDS:
        if kind not in used_kinds:
            continue
        glazed, frame_member = PANEL_KIND_FLAGS[kind]
        panel_types.append(
            {
                "kind": kind,
                "glazed": glazed,
                "frame_member": frame_member,
                "material_role": MATERIAL_ROLE[kind],
                "opening_types": sorted(hosted_types[kind]),
            }
        )
        first = model.kind_first_panel[kind]
        index = len(panel_types) - 1
        for key in ("glazed", "frame_member", "material_role"):
            model.note(f"panel_types[{index}].{key}", [f"panel_types[{index}].kind"])
        model.note(f"panel_types[{index}].opening_types", [f"panels[{first}].opening_ref"])
        del first

    document: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "spec": "facade_grids",
        "project": dimensions["project"],
        "units": {"length": "cm", "angle": "deg"},
        "source": {
            "kind": "derived",
            "reference": (
                f"{DIMENSIONS_NAME} and {MASSING_NAME} -- the locked dimensional contract and "
                "the locked massing for "
                f"{dimensions['project']}; every value in this file is computed from them by "
                "scripts/facade_tables.py --stage grids, per the numbered procedure in the P5 "
                "contract section 4"
            ),
            "recorded_at": (dimensions.get("source") or {}).get("recorded_at"),
        },
        "status": "locked",
        "tolerances": dict(dimensions["tolerances"]),
        "origin_inputs": [],
        "origins": {},
        "facades": [strip_private(facade) for facade in model.facades],
        "axes": model.axes,
        "panels": [strip_private(panel) for panel in panels],
        "panel_types": panel_types,
    }
    document["origins"] = build_grid_origins(document, model, dimensions, massing)
    document["origin_inputs"] = origin_inputs_for(model, dimensions, massing)
    return document


def strip_private(node: Any) -> Any:
    """Drop the ``_``-prefixed build-time keys before a document is emitted."""
    if isinstance(node, dict):
        return {key: strip_private(value) for key, value in node.items() if not key.startswith("_")}
    if isinstance(node, list):
        return [strip_private(item) for item in node]
    return node


# --------------------------------------------------------------------------- #
# Contract section 5 -- the components registry
# --------------------------------------------------------------------------- #


def component_kind_for(panel: dict[str, Any], opening_types: dict[str, str]) -> str:
    """Contract section 5.6: the panel kind decides, the opening only disambiguates.

    A ``vision`` or ``punched_window`` panel that realises a ``door`` or
    ``entrance`` opening becomes an ``entrance_door``; every other glazed panel is
    a ``glazed_panel``. Nothing here is a preference.
    """
    kind = str(panel["kind"])
    if kind in ("vision", "punched_window"):
        opening_type = opening_types.get(str(panel.get("opening_ref")))
        if opening_type in DOOR_TYPES:
            return "entrance_door"
        return "glazed_panel"
    if kind in ("spandrel", "blank"):
        return "opaque_panel"
    if kind in ("mullion", "transom"):
        return "frame_member"
    raise Refusal(
        f"refusing to build: panel {panel.get('id')!r} declares kind {kind!r}, which contract "
        f"section 5.6 does not map to a component kind (known: {list(PANEL_KINDS)})."
    )


def build_registry(
    grids: dict[str, Any], dimensions: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str], dict[str, str], dict[str, str]]:
    """``components_registry.json`` plus the panel -> (component, family) assignment.

    One component per distinct ``(kind, width, height)`` class of panel, where
    ``kind`` is the **component** kind and the panel kind is carried alongside it.
    The panel kind has to be part of the key, and that is forced rather than
    preferred: ``G-65`` requires every component to appear in exactly one family and
    contract section 5.5 makes one family per panel kind, so a component that
    served two panel kinds could satisfy neither. ``G-68`` still resolves, because
    a panel matches only components whose ``serves_panel_kinds`` contains its kind.

    ``variants`` is empty for every component: an option a registry declares with
    no declared overrides is a shape G-69 could not check, and the contract asks
    for ``[]``. G-69 therefore reports SKIP with that reason rather than a
    vacuous PASS.
    """
    panels = grids.get("panels") or []
    panel_types = grids.get("panel_types") or []
    declared = [str(entry.get("kind")) for entry in panel_types]
    for kind in declared:
        if kind not in PANEL_KINDS:
            raise Refusal(
                f"refusing to build: facade_grids.json declares panel kind {kind!r}, which is "
                f"outside the six reserved names {list(PANEL_KINDS)} (G-63)."
            )

    opening_types: dict[str, str] = {}
    for opening in dimensions.get("openings") or []:
        if isinstance(opening, dict):
            opening_types[str(opening.get("id"))] = str(opening.get("type"))

    thickness = PANEL_THICKNESS_CM
    joint = JOINT_WIDTH_CM
    notes: dict[str, list[str]] = {}

    classes: dict[tuple[str, str, float, float], None] = {}
    panel_component_kind: dict[str, str] = {}
    for panel in panels:
        kind = component_kind_for(panel, opening_types)
        panel_component_kind[str(panel["id"])] = kind
        classes[(kind, str(panel["kind"]), q(panel["width_cm"]), q(panel["height_cm"]))] = None

    ordered_keys = sorted(
        classes,
        key=lambda item: (COMPONENT_KINDS.index(item[0]), item[2], item[3], PANEL_KINDS.index(item[1])),
    )

    components: list[dict[str, Any]] = []
    index_of_class: dict[tuple[str, str, float, float], str] = {}
    for position, key in enumerate(ordered_keys, start=1):
        kind, panel_kind, width, height = key
        identifier = f"CMP-{position:03d}"
        index_of_class[key] = identifier
        glazed, frame_member = COMPONENT_KIND_FLAGS[kind]
        entry = {
            "id": identifier,
            "name": node_name(identifier),
            "kind": kind,
            "size_cm": [q(width), q(height), q(thickness)],
            "parameters": [
                {
                    "name": name,
                    "source": source,
                    "value": {
                        "width_cm": q(width),
                        "height_cm": q(height),
                        "thickness_cm": q(thickness),
                        "joint_width_cm": q(joint),
                    }[name],
                    "units": "cm",
                }
                for name, source in PARAMETER_ORDER
            ],
            "serves_panel_kinds": [panel_kind],
            "variants": [],
            "layer": FACADE_LAYER,
        }
        components.append(entry)
        stem = f"components[{position - 1}]"
        index = position - 1
        del glazed, frame_member
        for offset, (parameter_name, source) in enumerate(PARAMETER_ORDER):
            if source == "size_cm":
                anchor = f"{stem}.size_cm"
            else:
                anchor = "defaults"
            for key_name in ("name", "source", "value", "units"):
                notes[f"{stem}.parameters[{offset}].{key_name}"] = [anchor]
        notes[f"{stem}.variants"] = [f"{stem}.parameters"]
        notes[f"{stem}.size_cm"] = [f"{stem}.parameters", "defaults.panel_thickness_cm"]
        notes[f"{stem}.serves_panel_kinds"] = [f"{stem}.kind"]
        notes[f"{stem}.kind"] = [f"component_types[{index}].kind"]

    used_component_kinds = [kind for kind in COMPONENT_KINDS if any(entry["kind"] == kind for entry in components)]
    component_types: list[dict[str, Any]] = []
    for kind in used_component_kinds:
        glazed, frame_member = COMPONENT_KIND_FLAGS[kind]
        index = len(component_types)
        first = next(position for position, entry in enumerate(components) if entry["kind"] == kind)
        component_types.append({"kind": kind, "glazed": glazed, "frame_member": frame_member})
        for key in ("glazed", "frame_member"):
            notes[f"component_types[{index}].{key}"] = [f"component_types[{index}].kind"]
        notes[f"component_types[{index}].kind"] = [f"components[{first}].kind"]

    families: list[dict[str, Any]] = []
    family_of_panel_kind: dict[str, str] = {}
    for position, panel_kind in enumerate(
        [kind for kind in PANEL_KINDS if kind in declared], start=1
    ):
        identifier = f"FAM-{position:03d}"
        member = [
            entry["id"] for entry in components if panel_kind in entry["serves_panel_kinds"]
        ]
        if not member:
            raise Refusal(
                f"refusing to build: no component serves panel kind {panel_kind!r}, so a family "
                "for it would be empty and G-68 could not resolve any of its panels."
            )
        families.append(
            {
                "id": identifier,
                "name": node_name(identifier),
                "panel_kinds": [panel_kind],
                "component_ids": member,
                "substitution": "size_matched",
            }
        )
        family_of_panel_kind[panel_kind] = identifier
        stem = f"families[{position - 1}]"
        first_member = member.index(member[0])
        notes[f"{stem}.panel_kinds"] = [f"components[{first_member}].serves_panel_kinds"]
        notes[f"{stem}.component_ids"] = ["components"]
        notes[f"{stem}.substitution"] = ["tolerances.linear_cm"]

    assignment: dict[str, str] = {}
    component_family: dict[str, str] = {}
    for family in families:
        for component_id in family["component_ids"]:
            component_family[component_id] = family["id"]
    for panel in panels:
        panel_kind = str(panel["kind"])
        key = (
            panel_component_kind[str(panel["id"])],
            panel_kind,
            q(panel["width_cm"]),
            q(panel["height_cm"]),
        )
        identifier = index_of_class[key]
        assignment[str(panel["id"])] = identifier
    panel_family: dict[str, str] = {}
    for panel in panels:
        panel_family[str(panel["id"])] = component_family[assignment[str(panel["id"])]]

    document: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "spec": "components_registry",
        "project": grids["project"],
        "units": {"length": "cm", "angle": "deg"},
        "source": {
            "kind": "derived",
            "reference": (
                f"{GRIDS_NAME} -- the P5 panel grid this registry resolves, itself computed from "
                f"{DIMENSIONS_NAME} by scripts/facade_tables.py. The join runs registry -> grid, so "
                "no panel names a component and G-31 stays a single pass"
            ),
            "recorded_at": (grids.get("source") or {}).get("recorded_at"),
        },
        "status": "locked",
        "tolerances": dict(grids["tolerances"]),
        "origin_inputs": [],
        "origins": {},
        "defaults": {
            "panel_thickness_cm": q(thickness),
            "joint_width_cm": q(joint),
        },
        "component_types": component_types,
        "components": components,
        "families": families,
    }

    document["origins"] = build_registry_origins(document, notes, grids)
    document["origin_inputs"] = registry_origin_inputs(notes, dimensions)
    return document, panel_family, panel_component_kind, assignment


def build_registry_origins(
    document: dict[str, Any],
    notes: dict[str, list[str]],
    grids: dict[str, Any],
) -> dict[str, Any]:
    """One ``origins`` entry per leaf of the registry, in document order.

    The two ``assumed`` values are the only numbers P5 does not derive, and they
    live in ``defaults``, with their ledger refs: ``A-023`` for the panel thickness
    and ``A-024`` for the joint width (contract section 5.2). Each is its
    convention's declared default (``09`` ``D-CL-05`` = 3, ``D-FM-10`` = 2), not a
    value merely inside its range. Everything else is ``derived``. A ``layer`` leaf
    is a constant of this stage's schema and its only in-file anchor is ``spec``.
    """
    origins: dict[str, Any] = {}
    for leaf in collect_leaves(document):
        if leaf == "defaults.panel_thickness_cm":
            origins[leaf] = {"origin": "assumed", "origin_ref": PANEL_THICKNESS_LEDGER}
            continue
        if leaf == "defaults.joint_width_cm":
            origins[leaf] = {"origin": "assumed", "origin_ref": JOINT_WIDTH_LEDGER}
            continue
        if leaf in notes:
            origins[leaf] = {"origin": "derived", "derives_from": list(notes[leaf])}
            continue
        if leaf.endswith(".layer"):
            origins[leaf] = {"origin": "derived", "derives_from": ["spec"]}
            continue
        raise Refusal(
            f"internal: leaf {leaf} has no provenance recorded; every leaf of "
            "components_registry.json needs an origins entry and this builder records one."
        )
    return origins


def registry_origin_inputs(notes: dict[str, list[str]], dimensions: dict[str, Any]) -> list[str]:
    """Sorted upstream paths the registry read: the grid's tolerances and nothing else.

    The grid's panel widths are read through ``facade_grids.json``, whose paths are
    not resolvable in ``dimensions.json``, so they are not inputs here -- which is
    why the registry's size-bearing leaves are anchored inside the registry and
    cross-checked by G-66 instead.
    """
    inputs: set[str] = set()
    for paths in notes.values():
        for path in paths:
            if resolve(dimensions, path)[0]:
                inputs.add(path)
    inputs.add("tolerances.linear_cm")
    return sorted(inputs)


# --------------------------------------------------------------------------- #
# Contract section 6 -- the two CSVs
# --------------------------------------------------------------------------- #


def csv_field(value: Any) -> str:
    """One CSV field. No quoting, no commas, so anything else is a defect."""
    if isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, int):
        text = str(value)
    elif isinstance(value, float):
        text = num(value)
    elif value is None:
        text = ""
    else:
        text = str(value)
    if "," in text or '"' in text or "\n" in text:
        raise Refusal(
            f"refusing to write: CSV field {text!r} contains a comma, a quote or a newline. The "
            "contract section 6 CSVs carry no quoting, so a value that needs it cannot be emitted."
        )
    return text


def render_csv(columns: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Header row, then rows, LF endings, exactly one trailing newline."""
    lines = [",".join(columns)]
    for row in rows:
        if len(row) != len(columns):
            raise Refusal(
                f"refusing to write: a row has {len(row)} fields for {len(columns)} columns."
            )
        lines.append(",".join(csv_field(field) for field in row))
    return "\n".join(lines) + "\n"


def build_facade_rows(
    grids: dict[str, Any], panel_component_kind: dict[str, str]
) -> list[list[Any]]:
    panels = sorted(grids.get("panels") or [], key=lambda panel: str(panel["id"]))
    angle_of = {str(facade["id"]): facade["run_angle_deg"] for facade in grids.get("facades") or []}
    rows: list[list[Any]] = []
    for panel in panels:
        identifier = str(panel["id"])
        rows.append(
            [
                identifier,
                str(panel["facade"]),
                int(panel["level_index"]),
                int(panel["bay_index"]),
                str(panel["kind"]),
                panel_component_kind[identifier],
                panel["opening_ref"],
                panel["host_ref"],
                bool(panel["full_height"]),
                q(panel["u_min_cm"]),
                q(panel["u_max_cm"]),
                q(panel["v_min_cm"]),
                q(panel["v_max_cm"]),
                q(panel["width_cm"]),
                q(panel["height_cm"]),
                q(panel["centre_cm"][0]),
                q(panel["centre_cm"][1]),
                q(panel["centre_cm"][2]),
                str(panel["u_axis_min"]),
                str(panel["u_axis_max"]),
                str(panel["v_axis_min"]),
                str(panel["v_axis_max"]),
                q(angle_of[str(panel["facade"])]),
            ]
        )
    return rows


def build_world_rows(
    grids: dict[str, Any],
    registry: dict[str, Any],
    panel_component_kind: dict[str, str],
    panel_family: dict[str, str],
    assignment: dict[str, str],
) -> list[list[Any]]:
    panels = sorted(grids.get("panels") or [], key=lambda panel: str(panel["id"]))
    angle_of = {str(facade["id"]): facade["run_angle_deg"] for facade in grids.get("facades") or []}
    thickness = q(registry["defaults"]["panel_thickness_cm"])
    joint = q(registry["defaults"]["joint_width_cm"])
    rows: list[list[Any]] = []
    for panel in panels:
        identifier = str(panel["id"])
        rows.append(
            [
                identifier,
                assignment[identifier],
                panel_family[identifier],
                identifier,
                str(panel["facade"]),
                int(panel["level_index"]),
                str(panel["kind"]),
                panel_component_kind[identifier],
                q(panel["centre_cm"][0]),
                q(panel["centre_cm"][1]),
                q(panel["centre_cm"][2]),
                q(angle_of[str(panel["facade"])]),
                q(panel["width_cm"]),
                q(panel["height_cm"]),
                thickness,
                joint,
                FACADE_LAYER,
            ]
        )
    return rows


# --------------------------------------------------------------------------- #
# G-70 -- the emitted-table census, ONE implementation
# --------------------------------------------------------------------------- #


def _read_csv_rows(path: Path, columns: Sequence[str]) -> list[dict[str, str]]:
    """Parse an emitted CSV off disk into the row dicts the census takes.

    Only what ``facade_table_census`` reads is checked here -- header identity, LF
    endings, field count, and no quoting -- so that the *rule* lives in exactly one
    place. Re-implementing the count, the ref resolution or the rotation check on
    top of this would be the duplication revision 2 of the contract removed: two
    implementations of G-70 is one implementation plus one thing that drifts.
    """
    text = path.read_text(encoding="utf-8")
    if "\r" in text:
        raise Refusal(
            f"refusing to finish: {path} contains CR. The contract section 6 CSVs are LF only."
        )
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != ",".join(columns):
        raise Refusal(
            f"refusing to finish: {path} header is {lines[0]!r}, expected "
            f"{','.join(columns)!r} (G-70)."
        )
    rows: list[dict[str, str]] = []
    for number, line in enumerate(lines[1:], start=2):
        fields = line.split(",")
        if len(fields) != len(columns):
            raise Refusal(
                f"refusing to finish: {path} line {number} has {len(fields)} fields for "
                f"{len(columns)} columns (G-70)."
            )
        rows.append(dict(zip(columns, fields)))
    return rows


def assert_emitted_tables(
    facade_path: Path,
    world_path: Path,
    grids: dict[str, Any],
    registry: dict[str, Any],
) -> tuple[int, int]:
    """G-70, asserted against the bytes on disk, by ``validate_specs``' own predicate.

    ``scripts/validate_specs.py`` exports :func:`facade_table_census` -- the single
    definition of the rule, used at lint time by ``_g70_table_census``. This builder
    **imports it** and calls it after writing, so the build-time assertion and the
    lint-time definition cannot disagree. A non-empty problem list is a refusal.
    The returned pair is the two data-row counts, so the summary reports what was
    read rather than what was intended.

    If the import fails this raises, loudly. Re-implementing the rule here would
    hide a broken toolchain behind a passing build, which is the exact failure the
    contract's revision 2 note warns about.
    """
    sibling = str(Path(__file__).resolve().parent)
    if sibling not in sys.path:
        sys.path.insert(0, sibling)
    try:
        from validate_specs import facade_table_census  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - a broken toolchain, not a bad brief
        raise Refusal(
            "refusing to finish: scripts/validate_specs.py does not export "
            f"facade_table_census ({exc}). G-70 has exactly one implementation and this builder "
            "imports it rather than re-implementing the rule, so a missing export is a blocker, "
            "not something to work around. Put the sibling script on sys.path (or run from "
            "scripts/) and try again."
        ) from exc

    facade_rows = _read_csv_rows(facade_path, FACADE_CSV_COLUMNS)
    world_rows = _read_csv_rows(world_path, WORLD_CSV_COLUMNS)
    angle, angle_source = angle_tolerance(registry, None)
    problems = facade_table_census(grids, registry, facade_rows, world_rows, angle)
    if problems:
        raise Refusal(
            f"refusing to finish: G-70 fails on the emitted tables, {len(problems)} problem(s) "
            f"reported by validate_specs.facade_table_census (angle tolerance {angle_source}).\n  - "
            + "\n  - ".join(problems[:20])
        )
    return len(facade_rows), len(world_rows)


# --------------------------------------------------------------------------- #
# G-57..G-70, evaluated on the emitted documents
# --------------------------------------------------------------------------- #


def _ids_ascending(
    table: Sequence[dict[str, Any]],
    pattern: re.Pattern[str],
    rule: str,
    label: str,
    checks: Checks,
    key: str = "id",
) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    previous = ""
    for entry in table:
        ident = str(entry.get(key))
        if not pattern.match(ident):
            checks.fail(rule, f"{label} {key} {ident!r} does not match {pattern.pattern}")
        if ident in seen:
            checks.fail(rule, f"{label} {key} {ident!r} is not unique")
        if previous and ident <= previous:
            checks.fail(rule, f"{label} {key} {ident!r} does not ascend (previous is {previous})")
        seen.add(ident)
        ordered.append(ident)
        previous = ident
    return ordered


def self_check(
    grids: dict[str, Any] | None,
    registry: dict[str, Any] | None,
    dimensions: dict[str, Any] | None,
    massing: dict[str, Any] | None,
    want_csvs: bool,
) -> Checks:
    """Every rule G-57..G-70, as a pass / skip-with-reason / fail row.

    A rule that cannot be evaluated reports SKIP naming the reason -- never a
    silent PASS (07 section 9.6). ``grids is None`` means the stage is not
    producing a grid and the grid-side rules have nothing to look at; the same for
    the registry.
    """
    checks = Checks()
    tolerance, tolerance_source = linear_tolerance(grids or dimensions or {}, dimensions)
    angle, angle_source = angle_tolerance(grids or dimensions or {}, dimensions)
    area, area_source = area_tolerance(grids or dimensions or {}, dimensions)

    if grids is None:
        for rule in ("G-57", "G-58", "G-59", "G-60", "G-61", "G-62", "G-63", "G-64"):
            checks.skip(rule, "this stage does not produce facade_grids.json")
    else:
        _check_g57(grids, dimensions, tolerance, angle, angle_source, checks)
        _check_g58(grids, tolerance, tolerance_source, checks)
        _check_g59(grids, dimensions, massing, tolerance, tolerance_source, checks)
        _check_g60(grids, tolerance, checks)
        _check_g61(grids, area, area_source, checks)
        _check_g62(grids, dimensions, tolerance, tolerance_source, checks)
        _check_g63(grids, registry, checks)
        _check_g64(grids, dimensions, massing, checks)

    if registry is None:
        for rule in ("G-65", "G-66", "G-67", "G-68", "G-69"):
            checks.skip(rule, "this stage does not produce components_registry.json")
    else:
        _check_g65(registry, checks)
        _check_g66(registry, tolerance, tolerance_source, checks)
        _check_g67(registry, grids, tolerance, checks)
        _check_g68(registry, grids, tolerance, checks)
        _check_g69(registry, checks)

    if not want_csvs:
        checks.skip(
            "G-70",
            "this stage writes no CSV, so there is no emitted table to census; the census is "
            "asserted by reading the files back after they are written",
        )
    else:
        checks.skip(
            "G-70",
            "a static document cannot observe a CSV; this build asserts G-70 itself after writing, "
            "by reading both files back off disk",
        )
    return checks


def _check_g57(
    grids: dict[str, Any],
    dimensions: dict[str, Any] | None,
    tolerance: float,
    angle: float,
    angle_source: str,
    checks: Checks,
) -> None:
    """Facade agreement, bay arithmetic, and `direction_deg` never read as a rotation."""
    facades = grids.get("facades") or []
    upstream = (dimensions or {}).get("facades") or []
    if not isinstance(upstream, list) or len(upstream) != len(facades):
        checks.fail(
            "G-57",
            f"facades[] holds {len(facades)} entries but dimensions.facades[] holds "
            f"{len(upstream) if isinstance(upstream, list) else 'no array'}; the two must agree "
            "in the same order",
        )
        return
    for position, (entry, source) in enumerate(zip(facades, upstream)):
        ident = str(entry.get("id"))
        if ident != str(source.get("id")):
            checks.fail(
                "G-57",
                f"facades[{position}] is {ident!r} but dimensions.facades[{position}] is "
                f"{source.get('id')!r}; the ids must match in the same order",
            )
            continue
        if entry.get("name") != source.get("name"):
            checks.fail(
                "G-57",
                f"{ident} name {entry.get('name')!r} != dimensions {source.get('name')!r}",
            )
        if not close(entry.get("direction_deg"), source.get("direction_deg"), angle):
            checks.fail(
                "G-57",
                f"{ident} direction_deg {num(entry.get('direction_deg'))} != dimensions "
                f"{num(source.get('direction_deg'))}",
            )
        if not close(entry.get("length_cm"), source.get("length_cm"), tolerance):
            checks.fail(
                "G-57",
                f"{ident} length_cm {num(entry.get('length_cm'))} != dimensions "
                f"{num(source.get('length_cm'))} within {tolerance} cm",
            )
        if as_int(entry.get("bay_count")) != as_int(source.get("bay_count")):
            checks.fail(
                "G-57",
                f"{ident} bay_count {entry.get('bay_count')!r} != dimensions "
                f"{source.get('bay_count')!r}; the count is compared exactly",
            )
        widths = entry.get("bay_width_cm")
        upstream_widths = source.get("bay_width_cm")
        if widths != upstream_widths:
            checks.fail(
                "G-57", f"{ident} bay_width_cm {widths!r} != dimensions {upstream_widths!r}"
            )
        count = as_int(entry.get("bay_count"))
        if count is not None and isinstance(widths, list) and len(widths) != count:
            checks.fail(
                "G-57", f"{ident} bay_count is {count} but bay_width_cm holds {len(widths)} entries"
            )
        offsets = entry.get("bay_offsets_cm")
        if isinstance(offsets, list) and isinstance(widths, list):
            running = 0.0
            for index, width in enumerate(widths):
                running = q(running + as_float(width) or 0.0)
                if index >= len(offsets) or not close(offsets[index + 1] if index + 1 < len(offsets) else offsets[index], running, tolerance):
                    checks.fail(
                        "G-57",
                        f"{ident} bay_offsets_cm is not the cumulative sum of bay_width_cm at index "
                        f"{index}",
                    )
                    break
            if offsets and not close(offsets[0], 0.0, tolerance):
                checks.fail("G-57", f"{ident} bay_offsets_cm[0] is {num(offsets[0])}, not 0")
            if not close(offsets[-1] if offsets else 0.0, entry.get("length_cm"), tolerance):
                checks.fail(
                    "G-57",
                    f"{ident} bay_offsets_cm[-1] is {num(offsets[-1] if offsets else 0.0)}, not "
                    f"length_cm {num(entry.get('length_cm'))}",
                )
            centres = entry.get("bay_centre_cm")
            if isinstance(centres, list) and isinstance(widths, list):
                for index in range(min(len(centres), len(widths), len(offsets))):
                    expected = q((as_float(offsets[index]) or 0.0) + (as_float(widths[index]) or 0.0) / 2.0)
                    if not close(centres[index], expected, tolerance):
                        checks.fail(
                            "G-57",
                            f"{ident} bay_centre_cm[{index}] is {num(centres[index])}, not "
                            f"bay_offsets_cm[{index}] + bay_width_cm[{index}]/2 = {num(expected)}",
                        )
        start = entry.get("start_corner_cm")
        end = entry.get("end_corner_cm")
        if isinstance(start, list) and isinstance(end, list) and len(start) == 2 and len(end) == 2:
            expected = run_angle_deg(start, end)
            if not close(entry.get("run_angle_deg"), expected, angle):
                checks.fail(
                    "G-57",
                    f"{ident} run_angle_deg is {num(entry.get('run_angle_deg'))}, not "
                    f"atan2(end.y - start.y, end.x - start.x) = {num(expected)} within "
                    f"{angle_source}",
                )
            if not in_range(entry.get("run_angle_deg"), -180.0, 180.0, angle) and not close(
                entry.get("run_angle_deg"), 180.0, angle
            ):
                checks.fail(
                    "G-57",
                    f"{ident} run_angle_deg {num(entry.get('run_angle_deg'))} is outside (-180, 180]",
                )
            # The trap itself: two facades with the same run direction carry
            # different direction_deg, so a rotation read from it is wrong for one.
            if not close(entry.get("run_angle_deg"), entry.get("direction_deg"), angle) and close(
                entry.get("direction_deg"), 0.0, angle
            ) and not close(expected, 0.0, angle):
                checks.fail(
                    "G-57",
                    f"{ident} run_angle_deg equals direction_deg on a facade whose run does not "
                    "point that way",
                )
    if not any(rule == "G-57" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-57",
            f"{len(facades)} facades agree with dimensions.json in the same order; "
            "bay_offsets_cm is the cumulative sum, bay_centre_cm is offsets + width/2, and every "
            "run_angle_deg equals atan2(end - start) in (-180, 180] -- none of them is derived "
            "from direction_deg",
        )


def _check_g58(
    grids: dict[str, Any], tolerance: float, tolerance_source: str, checks: Checks
) -> None:
    axes = grids.get("axes") or []
    _ids_ascending(axes, AXIS_ID_RE, "G-58", "axes[]", checks)
    by_id: dict[str, dict[str, Any]] = {}
    for axis in axes:
        by_id[str(axis.get("id"))] = axis
        family = str(axis.get("family"))
        kind = str(axis.get("kind"))
        if family not in AXIS_FAMILIES:
            checks.fail("G-58", f"{axis.get('id')} family {family!r} is not u or v")
        if kind not in AXIS_KINDS:
            checks.fail("G-58", f"{axis.get('id')} kind {kind!r} is not one of {list(AXIS_KINDS)}")
        # Contract section 3.3. bay_index is a *required* key: null for a u axis, which
        # runs the whole facade, and a real bay for a v axis, which belongs to one bay's
        # elevation. A missing key is not null and is a defect, not a default.
        if "bay_index" not in axis:
            checks.fail(
                "G-58",
                f"{axis.get('id')} carries no bay_index. A u axis is null and a v axis names its "
                "bay (07 section 8.3.3, contract section 3.3).",
            )
        elif family == "u" and axis.get("bay_index") is not None:
            checks.fail(
                "G-58",
                f"{axis.get('id')} is a u axis with bay_index {axis.get('bay_index')!r}; a "
                "horizontal line runs the whole run, so it belongs to no single bay",
            )
        elif family == "v" and as_int(axis.get("bay_index")) is None:
            checks.fail(
                "G-58",
                f"{axis.get('id')} is a v axis with bay_index {axis.get('bay_index')!r}; a spandrel "
                "or storey line divides one bay's elevation, so it names a bay",
            )

    # Offsets must ascend inside (facade, level, family, bay_index) -- the group that
    # is actually tiled. Two bays sharing a level legitimately repeat an offset: bay 0's
    # storey base is not bay 1's.
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for axis in axes:
        key = (
            str(axis.get("facade")),
            axis.get("level_index"),
            str(axis.get("family")),
            axis.get("bay_index") if str(axis.get("family")) == "v" else None,
        )
        grouped.setdefault(key, []).append(axis)
    for key, family_axes in sorted(grouped.items(), key=lambda item: str(item)):
        ordered = sorted(family_axes, key=lambda axis: as_float(axis.get("offset_cm")) or 0.0)
        previous: float | None = None
        for axis in ordered:
            offset = as_float(axis.get("offset_cm"))
            if offset is None:
                checks.fail("G-58", f"{axis.get('id')} offset_cm is not a number")
                continue
            if previous is not None and offset - previous <= tolerance + TOLERANCE_EPSILON:
                checks.fail(
                    "G-58",
                    f"{key[0]} level {key[1]} {key[2]} bay {key[3]} axes are not separated by more "
                    f"than {tolerance} cm at {num(previous)} / {num(offset)} ({tolerance_source}); "
                    "two axes that close on each other make a cell of zero width",
                )
            previous = offset

    for facade in grids.get("facades") or []:
        ident = str(facade.get("id"))
        length = as_float(facade.get("length_cm")) or 0.0
        bay_count = as_int(facade.get("bay_count")) or 0
        for level in facade.get("levels") or []:
            level_index = level.get("level_index")
            height = as_float(level.get("height_cm")) or 0.0
            for family, key, bound in (
                ("u", "u_axis_ids", length),
                ("v", "v_axis_ids", height),
            ):
                identifiers = list(level.get(key) or [])
                if not identifiers:
                    checks.fail("G-58", f"{ident} level {level_index} {key} is empty")
                    continue
                rows: list[tuple[int, float]] = []
                for reference in identifiers:
                    axis = by_id.get(str(reference))
                    if axis is None:
                        checks.fail(
                            "G-58",
                            f"{ident} level {level_index} {key} names {reference!r}, which is not "
                            "an axis id",
                        )
                        continue
                    if str(axis.get("facade")) != ident or axis.get("level_index") != level_index:
                        checks.fail(
                            "G-58",
                            f"{reference} is {axis.get('facade')} level {axis.get('level_index')}, "
                            f"but {ident} level {level_index} lists it",
                        )
                    if str(axis.get("family")) != family:
                        checks.fail(
                            "G-58",
                            f"{reference} is family {axis.get('family')!r} and is listed in "
                            f"{ident} level {level_index} {key}",
                        )
                    offset = as_float(axis.get("offset_cm"))
                    if offset is None:
                        continue
                    if not in_range(offset, 0.0, bound, tolerance):
                        checks.fail(
                            "G-58",
                            f"{reference} offset {num(offset)} is outside 0..{num(bound)} for its "
                            f"{'run' if family == 'u' else 'storey'}",
                        )
                    bay = as_int(axis.get("bay_index"))
                    rows.append((0 if bay is None else bay, offset))

                if family == "u":
                    if rows != sorted(rows) or [offset for _bay, offset in rows] != sorted(
                        offset for _bay, offset in rows
                    ):
                        checks.fail("G-58", f"{ident} level {level_index} {key} does not ascend")
                    if not close(rows[0][1], 0.0, tolerance):
                        checks.fail(
                            "G-58",
                            f"{ident} level {level_index} {key} starts at {num(rows[0][1])}, not 0",
                        )
                    if not close(rows[-1][1], bound, tolerance):
                        checks.fail(
                            "G-58",
                            f"{ident} level {level_index} {key} ends at {num(rows[-1][1])}, not "
                            f"{num(bound)}",
                        )
                    continue

                # v_axis_ids is every v axis at this facade and level, ordered by
                # (bay_index, offset). Each bay's own slice must therefore run 0 ->
                # height_cm, and it is that slice -- not the whole list -- that has to
                # start at 0 and end at the storey height.
                if [(bay, offset) for bay, offset in rows] != sorted(rows):
                    checks.fail(
                        "G-58",
                        f"{ident} level {level_index} v_axis_ids is not ordered by "
                        "(bay_index, offset)",
                    )
                slices: dict[int, list[float]] = {}
                for bay, offset in rows:
                    slices.setdefault(bay, []).append(offset)
                for bay in range(bay_count):
                    offsets = slices.get(bay)
                    if not offsets:
                        checks.fail(
                            "G-58",
                            f"{ident} level {level_index} has no v axis at all for bay {bay}; "
                            "every bay contributes at least its storey base and storey top, and a "
                            "bay with no opening is one whole blank panel",
                        )
                        continue
                    if not close(offsets[0], 0.0, tolerance) or not close(
                        offsets[-1], bound, tolerance
                    ):
                        checks.fail(
                            "G-58",
                            f"{ident} level {level_index} bay {bay}: its v axes run "
                            f"{num(offsets[0])}..{num(offsets[-1])} but must run 0..{num(bound)}",
                        )
                    if len(offsets) == 2:
                        opening_edges = [
                            by_id[str(reference)].get("kind")
                            for reference in identifiers
                            if by_id.get(str(reference), {}).get("bay_index") == bay
                        ]
                        if "opening_edge" in opening_edges:
                            checks.fail(
                                "G-58",
                                f"{ident} level {level_index} bay {bay} declares an opening but "
                                "contributes only its storey base and top, so the opening's own "
                                "sill and head are not axes (G-62 then has nothing to realise)",
                            )

        present = {
            (
                str(axis.get("facade")),
                str(axis.get("family")),
                axis.get("bay_index"),
                q(as_float(axis.get("offset_cm")) or 0.0),
            )
            for axis in axes
        }
        for index, offset in enumerate(facade.get("bay_offsets_cm") or []):
            if (ident, "u", None, q(as_float(offset) or 0.0)) not in present:
                checks.fail(
                    "G-58",
                    f"{ident} bay_offsets_cm[{index}] = {num(offset)} has no matching u axis on this "
                    "facade",
                )
        for level in facade.get("levels") or []:
            level_index = level.get("level_index")
            height = as_float(level.get("height_cm")) or 0.0
            for bay in range(bay_count):
                for bound, kind in ((0.0, "level_base"), (height, "level_top")):
                    if (ident, "v", bay, q(bound)) not in present or not any(
                        str(axis.get("facade")) == ident
                        and str(axis.get("kind")) == kind
                        and axis.get("bay_index") == bay
                        and close(as_float(axis.get("offset_cm")) or 0.0, bound, tolerance)
                        for axis in axes
                    ):
                        checks.fail(
                            "G-58",
                            f"{ident} level {level_index} bay {bay} has no v axis at {num(bound)}; "
                            "the storey base and the storey top are both required",
                        )
    if not any(rule == "G-58" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-58",
            f"{len(axes)} axes: ids well formed, unique and ascending; family and kind inside "
            "their vocabularies; bay_index null on every u axis and a real bay on every v axis; "
            "offsets ascending and separated by more than linear_cm within each "
            "(facade, level, family, bay_index); u_axis_ids ascends 0 -> length_cm and "
            "v_axis_ids is ordered by (bay_index, offset) with each bay's slice running "
            "0 -> height_cm",
        )



def _check_g59(
    grids: dict[str, Any],
    dimensions: dict[str, Any] | None,
    massing: dict[str, Any] | None,
    tolerance: float,
    tolerance_source: str,
    checks: Checks,
) -> None:
    panels = grids.get("panels") or []
    _ids_ascending(panels, PANEL_ID_RE, "G-59", "panels[]", checks)
    openings = {
        str(entry.get("id")): entry for entry in (dimensions or {}).get("openings") or [] if isinstance(entry, dict)
    }
    element_ids = {
        str(entry.get("id")) for entry in (massing or {}).get("elements") or [] if isinstance(entry, dict)
    }
    declared = {str(entry.get("kind")) for entry in grids.get("panel_types") or []}
    facade_by_id = {str(entry.get("id")): entry for entry in grids.get("facades") or []}
    level_by_facade = {
        str(facade.get("id")): {level.get("level_index"): level for level in facade.get("levels") or []}
        for facade in grids.get("facades") or []
    }

    for panel in panels:
        ident = str(panel.get("id"))
        if str(panel.get("kind")) not in declared:
            checks.fail("G-59", f"{ident} kind {panel.get('kind')!r} is not in panel_types[]")
        if panel.get("layer") != FACADE_LAYER:
            checks.fail(
                "G-59", f"{ident} layer is {panel.get('layer')!r}, not {FACADE_LAYER!r}"
            )
        u_min = as_float(panel.get("u_min_cm"))
        u_max = as_float(panel.get("u_max_cm"))
        v_min = as_float(panel.get("v_min_cm"))
        v_max = as_float(panel.get("v_max_cm"))
        if None in (u_min, u_max, v_min, v_max):
            checks.fail("G-59", f"{ident} carries a non-numeric extent")
            continue
        if not (u_min < u_max):
            checks.fail("G-59", f"{ident} u_min_cm {num(u_min)} is not < u_max_cm {num(u_max)}")
        if not (v_min < v_max):
            checks.fail("G-59", f"{ident} v_min_cm {num(v_min)} is not < v_max_cm {num(v_max)}")
        if not close(panel.get("width_cm"), q(u_max - u_min), tolerance):
            checks.fail(
                "G-59",
                f"{ident} width_cm {num(panel.get('width_cm'))} != u_max_cm - u_min_cm = "
                f"{num(q(u_max - u_min))} within {tolerance} cm ({tolerance_source})",
            )
        if not close(panel.get("height_cm"), q(v_max - v_min), tolerance):
            checks.fail(
                "G-59",
                f"{ident} height_cm {num(panel.get('height_cm'))} != v_max_cm - v_min_cm = "
                f"{num(q(v_max - v_min))} within {tolerance} cm",
            )
        facade = facade_by_id.get(str(panel.get("facade")))
        if facade is None:
            checks.fail("G-59", f"{ident} facade {panel.get('facade')!r} is not declared")
            continue
        level = level_by_facade.get(str(panel.get("facade")), {}).get(panel.get("level_index"))
        if level is None:
            checks.fail(
                "G-59",
                f"{ident} level_index {panel.get('level_index')!r} is not a level of "
                f"{panel.get('facade')}",
            )
            continue
        length = as_float(facade.get("length_cm")) or 0.0
        height = as_float(level.get("height_cm")) or 0.0
        if not in_range(u_min, 0.0, length, tolerance) or not in_range(u_max, 0.0, length, tolerance):
            checks.fail(
                "G-59", f"{ident} u-range {num(u_min)}..{num(u_max)} is outside 0..{num(length)}"
            )
        if not in_range(v_min, 0.0, height, tolerance) or not in_range(v_max, 0.0, height, tolerance):
            checks.fail(
                "G-59", f"{ident} v-range {num(v_min)}..{num(v_max)} is outside 0..{num(height)}"
            )
        offsets = [as_float(value) or 0.0 for value in facade.get("bay_offsets_cm") or []]
        count = as_int(facade.get("bay_count")) or 0
        if offsets and count:
            u_mid = q((u_min + u_max) / 2.0)
            expected_bay = bay_of(u_mid, offsets, count)
            if as_int(panel.get("bay_index")) != expected_bay:
                checks.fail(
                    "G-59",
                    f"{ident} bay_index {panel.get('bay_index')!r} is not the bay containing the u "
                    f"midpoint {num(u_mid)} (expected {expected_bay})",
                )
        centre = panel.get("centre_cm")
        start = facade.get("start_corner_cm")
        end = facade.get("end_corner_cm")
        if isinstance(centre, list) and len(centre) == 3 and isinstance(start, list) and isinstance(end, list):
            u_mid = q((u_min + u_max) / 2.0)
            v_mid = q((v_min + v_max) / 2.0)
            run = math.hypot(end[0] - start[0], end[1] - start[1])
            expected = [
                q(float(start[0]) + (end[0] - start[0]) / run * u_mid),
                q(float(start[1]) + (end[1] - start[1]) / run * u_mid),
                q((as_float(level.get("elevation_cm")) or 0.0) + v_mid),
            ]
            for axis_name, got, want in zip("xyz", centre, expected):
                if not close(got, want, tolerance):
                    checks.fail(
                        "G-59",
                        f"{ident} centre_{axis_name} is {num(got)}, not {num(want)} within "
                        f"{tolerance} cm",
                    )
        else:
            checks.fail("G-59", f"{ident} centre_cm is not three numbers")
        reference = panel.get("opening_ref")
        if reference is not None:
            opening = openings.get(str(reference))
            if opening is None:
                checks.fail("G-59", f"{ident} opening_ref {reference!r} is not a dimensions opening")
            elif (
                str(opening.get("facade")) != str(panel.get("facade"))
                or as_int(opening.get("level_index")) != as_int(panel.get("level_index"))
                or as_int(opening.get("bay_index")) != as_int(panel.get("bay_index"))
            ):
                checks.fail(
                    "G-59",
                    f"{ident} opening_ref {reference} sits on another facade, level or bay",
                )
        host = panel.get("host_ref")
        if host is not None and str(host) not in element_ids:
            checks.fail("G-59", f"{ident} host_ref {host!r} is not a massing element id")
    if not any(rule == "G-59" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-59",
            f"{len(panels)} panels: ids well formed, unique and ascending; extents strictly "
            "increasing, inside their rectangle, and equal to width_cm / height_cm; bay_index is "
            "the bay holding the u midpoint; centre_cm recomputes from the run and the level; "
            "every layer is 05_FACADE",
        )


def _check_g60(grids: dict[str, Any], tolerance: float, checks: Checks) -> None:
    by_id = {str(axis.get("id")): axis for axis in grids.get("axes") or []}
    facade_by_id = {str(entry.get("id")): entry for entry in grids.get("facades") or []}
    level_height = {
        (str(facade.get("id")), level.get("level_index")): as_float(level.get("height_cm")) or 0.0
        for facade in grids.get("facades") or []
        for level in facade.get("levels") or []
    }
    for panel in grids.get("panels") or []:
        ident = str(panel.get("id"))
        for key, family, value in (
            ("u_axis_min", "u", panel.get("u_min_cm")),
            ("u_axis_max", "u", panel.get("u_max_cm")),
            ("v_axis_min", "v", panel.get("v_min_cm")),
            ("v_axis_max", "v", panel.get("v_max_cm")),
        ):
            axis = by_id.get(str(panel.get(key)))
            if axis is None:
                checks.fail("G-60", f"{ident} {key} names {panel.get(key)!r}, which is not an axis id")
                continue
            if str(axis.get("facade")) != str(panel.get("facade")) or axis.get("level_index") != panel.get("level_index"):
                checks.fail(
                    "G-60", f"{ident} {key} axis {axis.get('id')} is on another facade or level"
                )
            if str(axis.get("family")) != family:
                checks.fail("G-60", f"{ident} {key} axis {axis.get('id')} is not a {family} axis")
            if not close(axis.get("offset_cm"), value, tolerance):
                checks.fail(
                    "G-60",
                    f"{ident} {key} axis {axis.get('id')} sits at {num(axis.get('offset_cm'))}, not "
                    f"{num(value)}",
                )
        height = level_height.get((str(panel.get("facade")), panel.get("level_index")), 0.0)
        spans = close(panel.get("v_min_cm"), 0.0, tolerance) and close(
            panel.get("v_max_cm"), height, tolerance
        )
        if panel.get("full_height") and not spans:
            checks.fail(
                "G-60",
                f"{ident} is full_height but its v-range is {num(panel.get('v_min_cm'))}.."
                f"{num(panel.get('v_max_cm'))}, not 0..{num(height)}",
            )
        if not panel.get("full_height") and spans:
            checks.fail(
                "G-60",
                f"{ident} spans the whole storey without being full_height, so its v grid is cut "
                "for no declared reason",
            )
    if not any(rule == "G-60" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-60",
            f"{len(grids.get('panels') or [])} panels: all four axis ids resolve on the same "
            "facade, level and family and their offsets equal the panel's own extents; "
            "full_height agrees with the v-range",
        )


def _check_g61(grids: dict[str, Any], area: float, area_source: str, checks: Checks) -> None:
    facade_by_id = {str(entry.get("id")): entry for entry in grids.get("facades") or []}
    buckets: dict[tuple[str, Any], list[dict[str, Any]]] = {}
    for panel in grids.get("panels") or []:
        buckets.setdefault((str(panel.get("facade")), panel.get("level_index")), []).append(panel)
    level_height = {
        (str(facade.get("id")), level.get("level_index")): as_float(level.get("height_cm")) or 0.0
        for facade in grids.get("facades") or []
        for level in facade.get("levels") or []
    }
    declared_levels = {
        (str(facade.get("id")), level.get("level_index"))
        for facade in grids.get("facades") or []
        for level in facade.get("levels") or []
    }
    for key in sorted(declared_levels, key=lambda item: str(item)):
        panels = buckets.get(key, [])
        facade = facade_by_id.get(key[0])
        if facade is None:
            continue
        if not panels:
            checks.fail(
                "G-61",
                f"{key[0]} level {key[1]} has no panel; a gridded level with no panel is a hole",
            )
            continue
        length = as_float(facade.get("length_cm")) or 0.0
        height = level_height.get(key, 0.0)
        total = sum(
            ((as_float(panel.get("width_cm")) or 0.0) * (as_float(panel.get("height_cm")) or 0.0))
            for panel in panels
        )
        target = length * height
        if abs(total - target) / 10000.0 > area + TOLERANCE_EPSILON:
            checks.fail(
                "G-61",
                f"{key[0]} level {key[1]}: panel areas sum to {num(total / 10000.0)} m2 but the "
                f"facade rectangle is {num(target / 10000.0)} m2, outside {area} m2 "
                f"({area_source})",
            )
        for panel in panels:
            u_min = as_float(panel.get("u_min_cm")) or 0.0
            u_max = as_float(panel.get("u_max_cm")) or 0.0
            v_min = as_float(panel.get("v_min_cm")) or 0.0
            v_max = as_float(panel.get("v_max_cm")) or 0.0
            if u_min < -TOLERANCE_EPSILON or u_max > length + TOLERANCE_EPSILON:
                checks.fail("G-61", f"{panel.get('id')} leaves the facade rectangle in u")
            if v_min < -TOLERANCE_EPSILON or v_max > height + TOLERANCE_EPSILON:
                checks.fail("G-61", f"{panel.get('id')} leaves the facade rectangle in v")
        for first in range(len(panels)):
            for second in range(first + 1, len(panels)):
                a = panels[first]
                b = panels[second]
                du = min(as_float(a.get("u_max_cm")) or 0.0, as_float(b.get("u_max_cm")) or 0.0) - max(
                    as_float(a.get("u_min_cm")) or 0.0, as_float(b.get("u_min_cm")) or 0.0
                )
                dv = min(as_float(a.get("v_max_cm")) or 0.0, as_float(b.get("v_max_cm")) or 0.0) - max(
                    as_float(a.get("v_min_cm")) or 0.0, as_float(b.get("v_min_cm")) or 0.0
                )
                if du > TOLERANCE_EPSILON and dv > TOLERANCE_EPSILON:
                    checks.fail(
                        "G-61",
                        f"{a.get('id')} and {b.get('id')} overlap in their interiors by "
                        f"{num(du)} x {num(dv)} cm on {key[0]} level {key[1]}; the grid must be a "
                        "partition, not a pile of rectangles",
                    )
    if not any(rule == "G-61" and status == "fail" for rule, status, _ in checks.rows):
        total = len(buckets)
        checks.pass_(
            "G-61",
            f"{total} (facade, level) groups: panel areas sum to length_cm x height_cm within "
            f"{area} m2, no two panels overlap in their interiors, every panel is inside the "
            "rectangle, and every declared level carries at least one panel",
        )


def _check_g62(
    grids: dict[str, Any],
    dimensions: dict[str, Any] | None,
    tolerance: float,
    tolerance_source: str,
    checks: Checks,
) -> None:
    openings = (dimensions or {}).get("openings") or []
    declared_openings = {
        str(entry.get("id")) for entry in openings if isinstance(entry, dict)
    }
    by_opening: dict[str, list[dict[str, Any]]] = {}
    for panel in grids.get("panels") or []:
        reference = panel.get("opening_ref")
        if reference is not None:
            by_opening.setdefault(str(reference), []).append(panel)
    types = {str(entry.get("kind")): entry for entry in grids.get("panel_types") or []}
    judged = 0
    for opening in openings:
        if not isinstance(opening, dict):
            continue
        ident = str(opening.get("id"))
        panels = by_opening.get(ident, [])
        judged += 1
        # Strictly one. The vertical division is per bay, so an opening's own sill
        # and head are its only divisions and nothing can split it; the revision-1
        # wording ("at least one, and the panels tile the v-range") accepted a
        # facade-wide v grid, and that grid produced a 180 x 10 cm glass sliver 10 cm
        # below a window head because a different bay's entrance head crossed it.
        if not panels:
            checks.fail(
                "G-62",
                f"{ident} is referenced by no panel, so the grid has no geometry for a real "
                "opening",
            )
            continue
        if len(panels) > 1:
            checks.fail(
                "G-62",
                f"{ident} is referenced by {len(panels)} panels ("
                + ", ".join(str(panel.get("id")) for panel in panels[:10])
                + f"); exactly one is required. An opening is divided only by its own sill and "
                "head, so two panels for one opening is a ribbon of glass, not a partition nicety.",
            )
            continue
        u0 = q((as_float(opening.get("position_cm")) or 0.0) - (as_float(opening.get("width_cm")) or 0.0) / 2.0)
        u1 = q((as_float(opening.get("position_cm")) or 0.0) + (as_float(opening.get("width_cm")) or 0.0) / 2.0)
        sill = q(as_float(opening.get("sill_cm")) or 0.0)
        head = q(as_float(opening.get("head_cm")) or 0.0)
        opening_type = str(opening.get("type"))
        for panel in panels:
            if (
                str(panel.get("facade")) != str(opening.get("facade"))
                or as_int(panel.get("level_index")) != as_int(opening.get("level_index"))
                or as_int(panel.get("bay_index")) != as_int(opening.get("bay_index"))
            ):
                checks.fail(
                    "G-62",
                    f"{ident} is realised by {panel.get('id')} on another facade, level or bay",
                )
            if not (
                close(panel.get("u_min_cm"), u0, tolerance)
                and close(panel.get("u_max_cm"), u1, tolerance)
            ):
                checks.fail(
                    "G-62",
                    f"{ident} is realised by {panel.get('id')} whose u-range "
                    f"{num(panel.get('u_min_cm'))}..{num(panel.get('u_max_cm'))} is not "
                    f"[{num(u0)}, {num(u1)}] = position_cm +/- width_cm / 2 within "
                    f"{tolerance} cm ({tolerance_source})",
                )
            if not (
                close(panel.get("v_min_cm"), sill, tolerance)
                and close(panel.get("v_max_cm"), head, tolerance)
            ):
                checks.fail(
                    "G-62",
                    f"{ident} is realised by {panel.get('id')} whose v-range "
                    f"{num(panel.get('v_min_cm'))}..{num(panel.get('v_max_cm'))} is not "
                    f"[{num(sill)}, {num(head)}] = [sill_cm, head_cm] within {tolerance} cm "
                    f"({tolerance_source}). A panel taller or shorter than its own opening means "
                    "the v grid is cutting something it should not, or the opening is realised "
                    "by the wrong cell.",
                )
            declared = types.get(str(panel.get("kind")), {})
            if opening_type not in (declared.get("opening_types") or []):
                checks.fail(
                    "G-62",
                    f"{ident} ({opening_type}) is realised by {panel.get('id')} of kind "
                    f"{panel.get('kind')!r}, whose panel_types entry does not list {opening_type!r}",
                )
    # The reverse direction, which the "tiles" wording never needed because an
    # unreferenced opening was the only failure mode worth naming. An opening_ref that
    # names nothing is a panel pointing at geometry that does not exist; an id carried by
    # two panels is the same defect as a split, seen from the other side.
    for reference in sorted(by_opening):
        if reference not in declared_openings:
            checks.fail(
                "G-62",
                f"opening_ref {reference} is not a dimensions.json openings[].id; a panel that "
                "points at an opening the brief never declared is not realisable",
            )
    seen_by_panel: dict[str, str] = {}
    for panel in grids.get("panels") or []:
        reference = panel.get("opening_ref")
        if reference is None:
            continue
        ident = str(reference)
        if ident in seen_by_panel:
            checks.fail(
                "G-62",
                f"{ident} is referenced twice, by {seen_by_panel[ident]} and {panel.get('id')}",
            )
        else:
            seen_by_panel[ident] = str(panel.get("id"))
    if not any(rule == "G-62" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-62",
            f"{judged} openings, each referenced by exactly one panel on the same facade, level "
            "and bay, with u-range [position_cm - width_cm/2, position_cm + width_cm/2] and "
            "v-range [sill_cm, head_cm] within linear_cm, and no panel referencing an opening "
            "that does not exist or referencing one twice",
        )


def _check_g63(grids: dict[str, Any], registry: dict[str, Any] | None, checks: Checks) -> None:
    declared = grids.get("panel_types") or []
    seen: set[str] = set()
    used = {str(panel.get("kind")) for panel in grids.get("panels") or []}
    for entry in declared:
        kind = str(entry.get("kind"))
        if kind in seen:
            checks.fail("G-63", f"panel_types kind {kind!r} is declared twice")
        seen.add(kind)
        if kind not in PANEL_KINDS:
            checks.fail(
                "G-63",
                f"panel_types kind {kind!r} is outside the six reserved names {list(PANEL_KINDS)}",
            )
            continue
        glazed = entry.get("glazed")
        frame_member = entry.get("frame_member")
        role = str(entry.get("material_role"))
        if not isinstance(glazed, bool) or not isinstance(frame_member, bool):
            checks.fail("G-63", f"{kind} glazed / frame_member must both be bool")
            continue
        expected_role = "glazing" if glazed else ("frame" if frame_member else "opaque")
        if role != expected_role:
            checks.fail(
                "G-63",
                f"{kind} material_role is {role!r}; glazed={glazed} and frame_member={frame_member} "
                f"imply {expected_role!r}. A material_role is a role for a later stage, never a "
                "material class (contract section 0).",
            )
        if role not in MATERIAL_ROLES:
            checks.fail("G-63", f"{kind} material_role {role!r} is not one of {list(MATERIAL_ROLES)}")
        opening_types = entry.get("opening_types")
        if not isinstance(opening_types, list):
            checks.fail("G-63", f"{kind} opening_types is not an array")
            continue
        if bool(opening_types) != bool(glazed):
            checks.fail(
                "G-63",
                f"{kind} opening_types is {opening_types!r} but glazed is {glazed}; a non-empty "
                "opening_types list is exactly what glazed means",
            )
        if kind not in used:
            checks.fail("G-63", f"{kind} is declared but no panel uses it")
    for kind in sorted(used - seen):
        checks.fail("G-63", f"panels use kind {kind!r}, which panel_types does not declare")
    if registry is not None:
        served = {
            str(entry)
            for component in registry.get("components") or []
            for entry in component.get("serves_panel_kinds") or []
        }
        missing = sorted(used - served)
        if missing:
            checks.fail(
                "G-63",
                f"declared panel kind(s) {missing} are served by no component in "
                "components_registry.json",
            )
    if not any(rule == "G-63" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-63",
            f"{len(declared)} panel kinds, all inside the six reserved names, all used, flags and "
            "material_role in step, and each served by at least one component",
        )


def _check_g64(
    grids: dict[str, Any],
    dimensions: dict[str, Any] | None,
    massing: dict[str, Any] | None,
    checks: Checks,
) -> None:
    origins = grids.get("origins") if isinstance(grids.get("origins"), dict) else {}
    leaves = collect_leaves(grids)
    for leaf in leaves:
        holders = [entry for entry in origins if covers(entry, leaf)]
        if not holders:
            checks.fail("G-64", f"leaf {leaf} has no origins entry")
        elif len(holders) > 1:
            checks.fail("G-64", f"leaf {leaf} is covered by {len(holders)} origins entries: {holders}")
    for entry in sorted(origins):
        record = origins[entry]
        if not isinstance(record, dict):
            checks.fail("G-64", f"origins entry {entry} is not an object")
            continue
        if record.get("origin") != "derived":
            checks.fail(
                "G-64",
                f"origins entry {entry} is {record.get('origin')!r}; P5 invents nothing outside "
                "the registry's defaults, so an assumed or given value here is a defect",
            )
        derives = record.get("derives_from")
        if not isinstance(derives, list) or not derives:
            checks.fail("G-64", f"origins entry {entry} has no derives_from")
            continue
        for path in derives:
            if (
                not resolve(grids, path)[0]
                and not resolve(dimensions, path)[0]
                and not resolve(massing, path)[0]
            ):
                checks.fail(
                    "G-64",
                    f"origins entry {entry} derives from {path!r}, which resolves in neither "
                    "facade_grids.json, dimensions.json nor massing.json",
                )
    for entry in sorted(origins):
        if not any(covers(entry, leaf) for leaf in leaves):
            checks.fail("G-64", f"origins entry {entry} covers no leaf")
    for path in grids.get("origin_inputs") or []:
        if not resolve(dimensions, path)[0] and not resolve(massing, path)[0]:
            checks.fail(
                "G-64", f"origin_inputs path {path!r} resolves in neither dimensions.json nor massing.json"
            )
    if not any(rule == "G-64" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-64",
            f"{len(origins)} origins entries cover {len(leaves)} leaves exactly once; every one is "
            "derived with a resolving derives_from, and all "
            f"{len(grids.get('origin_inputs') or [])} origin_inputs paths resolve upstream",
        )


def _check_g65(registry: dict[str, Any], checks: Checks) -> None:
    components = registry.get("components") or []
    families = registry.get("families") or []
    component_ids = _ids_ascending(components, COMPONENT_ID_RE, "G-65", "components[]", checks)
    _ids_ascending(families, FAMILY_ID_RE, "G-65", "families[]", checks)
    component_types = {str(entry.get("kind")) for entry in registry.get("component_types") or []}
    names: dict[str, str] = {}
    for entry in components:
        ident = str(entry.get("id"))
        name = str(entry.get("name"))
        if "-" in name:
            checks.fail("G-65", f"{ident} name {name!r} contains '-'; a hyphen reads as subtraction (11 N1)")
        if not NODE_NAME_RE.match(name):
            checks.fail("G-65", f"{ident} name {name!r} is not an identifier-safe node name")
        if name in names:
            checks.fail("G-65", f"{ident} name {name!r} is already used by {names[name]}")
        names[name] = ident
        if str(entry.get("kind")) not in component_types:
            checks.fail(
                "G-65",
                f"{ident} kind {entry.get('kind')!r} is not in component_types[] "
                f"({sorted(component_types)})",
            )
        if entry.get("layer") != FACADE_LAYER:
            checks.fail("G-65", f"{ident} layer is {entry.get('layer')!r}, not {FACADE_LAYER!r}")
    listed: dict[str, str] = {}
    for family in families:
        members = family.get("component_ids") or []
        if not members:
            checks.fail("G-65", f"{family.get('id')} lists no component")
        for member in members:
            if str(member) not in component_ids:
                checks.fail(
                    "G-65", f"{family.get('id')} lists {member!r}, which is not a component id"
                )
            if str(member) in listed:
                checks.fail(
                    "G-65",
                    f"component {member} appears in {listed[str(member)]} and "
                    f"{family.get('id')}; G-65 wants exactly one family per component",
                )
            listed[str(member)] = str(family.get("id"))
        panel_kinds = family.get("panel_kinds") or []
        if not panel_kinds:
            checks.fail("G-65", f"{family.get('id')} lists no panel kind")
        if str(family.get("substitution")) != "size_matched":
            checks.fail(
                "G-65",
                f"{family.get('id')} substitution is {family.get('substitution')!r}, not "
                "'size_matched'",
            )
    for identifier in component_ids:
        if identifier not in listed:
            checks.fail("G-65", f"component {identifier} appears in no family")
    if not any(rule == "G-65" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-65",
            f"{len(components)} components and {len(families)} families: ids well formed, unique "
            "and ascending, names unique and hyphen-free, every component in exactly one family "
            f"and every family layer {FACADE_LAYER}",
        )


def _check_g66(
    registry: dict[str, Any], tolerance: float, tolerance_source: str, checks: Checks
) -> None:
    defaults = registry.get("defaults")
    if not isinstance(defaults, dict):
        checks.fail("G-66", "defaults is not an object")
        return
    if sorted(defaults) != ["joint_width_cm", "panel_thickness_cm"]:
        checks.fail(
            "G-66",
            f"defaults carries {sorted(defaults)}; it holds exactly panel_thickness_cm and "
            "joint_width_cm (contract section 5.2)",
        )
        return
    thickness = as_float(defaults.get("panel_thickness_cm"))
    joint = as_float(defaults.get("joint_width_cm"))
    if thickness is None or not PANEL_THICKNESS_RANGE_CM[0] <= thickness <= PANEL_THICKNESS_RANGE_CM[1]:
        checks.fail(
            "G-66",
            f"defaults.panel_thickness_cm {defaults.get('panel_thickness_cm')!r} is outside "
            f"{PANEL_THICKNESS_RANGE_CM} (09 D-CL-05)",
        )
    if joint is None or not JOINT_WIDTH_RANGE_CM[0] <= joint <= JOINT_WIDTH_RANGE_CM[1]:
        checks.fail(
            "G-66",
            f"defaults.joint_width_cm {defaults.get('joint_width_cm')!r} is outside "
            f"{JOINT_WIDTH_RANGE_CM} (09 D-FM-10)",
        )
    for entry in registry.get("components") or []:
        ident = str(entry.get("id"))
        size = entry.get("size_cm")
        if not isinstance(size, list) or len(size) != 3 or any(as_float(v) is None for v in size):
            checks.fail("G-66", f"{ident} size_cm is not three numbers")
            continue
        if any((as_float(v) or 0.0) <= 0.0 for v in size):
            checks.fail("G-66", f"{ident} size_cm holds a non-positive number")
        parameters = entry.get("parameters")
        if not isinstance(parameters, list) or len(parameters) != len(PARAMETER_ORDER):
            checks.fail(
                "G-66",
                f"{ident} parameters holds {len(parameters) if isinstance(parameters, list) else 'no'}"
                f" entries; the ordered list has exactly {len(PARAMETER_ORDER)}",
            )
            continue
        for offset, (expected_name, expected_source) in enumerate(PARAMETER_ORDER):
            parameter = parameters[offset]
            if str(parameter.get("name")) != expected_name:
                checks.fail(
                    "G-66",
                    f"{ident} parameters[{offset}] is {parameter.get('name')!r}, expected "
                    f"{expected_name!r} in that exact order",
                )
                continue
            if str(parameter.get("source")) != expected_source:
                checks.fail(
                    "G-66",
                    f"{ident} parameters[{offset}] source is {parameter.get('source')!r}, expected "
                    f"{expected_source!r}",
                )
            value = as_float(parameter.get("value"))
            if expected_source == "size_cm":
                target = as_float(size[0] if expected_name == "width_cm" else size[1])
            else:
                target = thickness if expected_name == "thickness_cm" else joint
            if value is None or target is None or not close(value, target, tolerance):
                checks.fail(
                    "G-66",
                    f"{ident} parameters[{offset}].value {parameter.get('value')!r} != "
                    f"{expected_source}.{expected_name} {num(target) if target is not None else '?'} "
                    f"within {tolerance} cm ({tolerance_source})",
                )
        if thickness is not None and not close(size[2], thickness, tolerance):
            checks.fail(
                "G-66",
                f"{ident} size_cm[2] is {num(size[2])}, not defaults.panel_thickness_cm "
                f"{num(thickness)}",
            )
    if not any(rule == "G-66" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-66",
            f"defaults holds exactly panel_thickness_cm {num(thickness)} and joint_width_cm "
            f"{num(joint)}, both inside their 09 ranges; every component's size_cm is "
            "[width, height, panel_thickness_cm] and its four parameters are in the declared order "
            "with recomputing values",
        )


def _check_g67(
    registry: dict[str, Any], grids: dict[str, Any] | None, tolerance: float, checks: Checks
) -> None:
    kinds = {str(entry.get("kind")): entry for entry in (grids or {}).get("panel_types") or []}
    panels = (grids or {}).get("panels") or []
    sizes_by_kind: dict[str, set[tuple[float, float]]] = {}
    for panel in panels:
        width = as_float(panel.get("width_cm"))
        height = as_float(panel.get("height_cm"))
        if width is None or height is None:
            continue
        sizes_by_kind.setdefault(str(panel.get("kind")), set()).add((q(width), q(height)))
    for entry in registry.get("components") or []:
        ident = str(entry.get("id"))
        kind = str(entry.get("kind"))
        serves = entry.get("serves_panel_kinds") or []
        if not serves:
            checks.fail("G-67", f"{ident} serves_panel_kinds is empty")
            continue
        glazed, frame_member = COMPONENT_KIND_FLAGS.get(kind, (False, False))
        for panel_kind in serves:
            declared = kinds.get(str(panel_kind))
            if declared is None:
                checks.fail(
                    "G-67",
                    f"{ident} serves {panel_kind!r}, which facade_grids.json does not declare as a "
                    "panel kind",
                )
                continue
            panel_glazed = bool(declared.get("glazed"))
            panel_frame = bool(declared.get("frame_member"))
            if kind == "glazed_panel" and not panel_glazed:
                checks.fail("G-67", f"{ident} is a glazed_panel but serves {panel_kind!r}")
            if kind == "opaque_panel" and (panel_glazed or panel_frame):
                checks.fail(
                    "G-67",
                    f"{ident} is an opaque_panel but serves {panel_kind!r}, which is "
                    + ("glazed" if panel_glazed else "a frame member"),
                )
            if kind == "frame_member" and not panel_frame:
                checks.fail("G-67", f"{ident} is a frame_member but serves {panel_kind!r}")
            if kind == "entrance_door" and not panel_glazed:
                checks.fail(
                    "G-67", f"{ident} is an entrance_door but serves {panel_kind!r}, which is not glazed"
                )
        size = entry.get("size_cm")
        if isinstance(size, list) and len(size) == 3:
            pair = (q(as_float(size[0]) or 0.0), q(as_float(size[1]) or 0.0))
            if not any(
                close(pair[0], width, tolerance) and close(pair[1], height, tolerance)
                for panel_kind in serves
                for width, height in sizes_by_kind.get(str(panel_kind), set())
            ):
                checks.fail(
                    "G-67",
                    f"{ident} size_cm {num(pair[0])} x {num(pair[1])} matches no panel of the kind(s) "
                    f"it serves; a block that fits nothing exists for no reason",
                )
    if not any(rule == "G-67" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-67",
            f"{len(registry.get('components') or [])} components: every serves_panel_kinds entry is "
            "a declared panel kind, the component kind's flags agree with every kind it serves, and "
            "every size_cm matches a real panel of those kinds",
        )


def _check_g68(
    registry: dict[str, Any], grids: dict[str, Any] | None, tolerance: float, checks: Checks
) -> None:
    panels = (grids or {}).get("panels") or []
    components = registry.get("components") or []
    families = registry.get("families") or []
    family_of = {
        str(member): str(family.get("id"))
        for family in families
        for member in family.get("component_ids") or []
    }
    offenders: list[str] = []
    for panel in panels:
        width = q(as_float(panel.get("width_cm")) or 0.0)
        height = q(as_float(panel.get("height_cm")) or 0.0)
        kind = str(panel.get("kind"))
        matched = [
            str(entry.get("id"))
            for entry in components
            if kind in (entry.get("serves_panel_kinds") or [])
            and isinstance(entry.get("size_cm"), list)
            and len(entry["size_cm"]) >= 2
            and close(entry["size_cm"][0], width, tolerance)
            and close(entry["size_cm"][1], height, tolerance)
        ]
        if not matched:
            offenders.append(str(panel.get("id")))
            continue
        homes = {family_of.get(identifier) for identifier in matched}
        if len(homes) != 1 or None in homes:
            offenders.append(f"{panel.get('id')} (families {sorted(str(h) for h in homes)})")
    if offenders:
        checks.fail(
            "G-68",
            f"{len(offenders)} panel(s) have no size-matched component in exactly one family; the "
            f"first ten are {offenders[:10]}",
        )
    else:
        checks.pass_(
            "G-68",
            f"every one of {len(panels)} panels resolves to at least one component whose size_cm "
            "matches within linear_cm, and all matching components sit in one family",
        )


def _check_g69(registry: dict[str, Any], checks: Checks) -> None:
    empty = 0
    for entry in registry.get("components") or []:
        variants = entry.get("variants")
        if not isinstance(variants, list):
            checks.fail("G-69", f"{entry.get('id')} variants is not an array")
            continue
        if not variants:
            empty += 1
            continue
        seen: set[str] = set()
        for variant in variants:
            ident = str(variant.get("id"))
            if not VARIANT_ID_RE.match(ident):
                checks.fail("G-69", f"{entry.get('id')} variant {ident!r} does not match ^VAR-\\d{{3}}$")
            if ident in seen:
                checks.fail("G-69", f"{entry.get('id')} variant {ident} is repeated")
            seen.add(ident)
            overrides = variant.get("overrides")
            if not isinstance(overrides, dict) or not overrides:
                checks.fail("G-69", f"{entry.get('id')} variant {ident} overrides is empty")
                continue
            for key in sorted(overrides):
                if key not in {name for name, _ in PARAMETER_ORDER}:
                    checks.fail(
                        "G-69",
                        f"{entry.get('id')} variant {ident} overrides {key!r}, which is not one of "
                        "the four parameter names",
                    )
    if empty:
        checks.skip(
            "G-69",
            f"every one of {empty} components declares variants: [], so the rule is unexercised. A "
            "registry with no construction options has nothing to check, and saying so beats a "
            "vacuous PASS."
        )
    elif not any(rule == "G-69" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_("G-69", "every declared variant is well formed and overrides a parameter")


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def guard_existing_grids(specs_dir: Path, computed_text: str, computed: dict[str, Any]) -> None:
    """Refuse to overwrite a ``facade_grids.json`` this build does not reproduce.

    The refusal names the **first differing key path**, in a deterministic walk, so
    the caller knows what to look at. A silent overwrite is the failure mode
    ``--from examples`` exists to prevent: a hand edit that a rebuild destroys is
    indistinguishable from an edit that never happened until the edit is gone.
    """
    path = specs_dir / GRIDS_NAME
    if not path.is_file():
        return
    existing_raw = path.read_bytes()
    try:
        existing = strict_loads(existing_raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal(
            f"refusing to build: {path} is not strict JSON -- {exc}. Fix or remove it; this build "
            "will not overwrite a file it cannot read (G-7)."
        ) from exc
    if not isinstance(existing, dict):
        raise Refusal(f"refusing to build: {path} top level is not an object.")
    if serialize(existing, GRIDS_NAME) == computed_text:
        return
    path_found = first_difference(existing, computed)
    if path_found is not None:
        raise Refusal(
            f"refusing to overwrite {path}: the file on disk differs from what this build "
            f"computes. First differing key path: {path_found}. The build reproduces its own "
            "output exactly, so a difference is a hand edit (or a different input) -- resolve it "
            "before rebuilding, or remove the file to accept the computed grid."
        )
    existing_lines = serialize(existing, GRIDS_NAME).split("\n")
    computed_lines = computed_text.split("\n")
    number = next(
        (
            index
            for index in range(max(len(existing_lines), len(computed_lines)))
            if (
                existing_lines[index] if index < len(existing_lines) else None
            )
            != (computed_lines[index] if index < len(computed_lines) else None)
        ),
        1,
    )
    raise Refusal(
        f"refusing to overwrite {path}: the two parse to the same value tree but their bytes "
        f"differ, first at line {number}. Re-emit the file with this builder (no --json, no "
        "reformatting) so the canonical bytes agree."
    )


def summarise(
    stage: str,
    grids: dict[str, Any] | None,
    registry: dict[str, Any] | None,
    checks: Checks,
    written: Sequence[Path],
    row_counts: dict[str, int],
    lock_gate: str,
) -> str:
    lines = [f"facade_tables.py --stage {stage}"]
    if grids is not None:
        panels = grids.get("panels") or []
        by_kind: dict[str, int] = {}
        for panel in panels:
            key = str(panel.get("kind"))
            by_kind[key] = by_kind.get(key, 0) + 1
        lines.append(
            f"  project   {grids['project']}  (read: {DIMENSIONS_NAME} + {MASSING_NAME}, "
            f"gate {lock_gate})"
        )
        lines.append(
            f"  facades   {len(grids.get('facades') or [])} runs, "
            f"{sum(len(f['levels']) for f in grids.get('facades') or [])} gridded levels in total"
        )
        lines.append(f"  axes      {len(grids.get('axes') or [])}")
        lines.append(
            f"  panels    {len(panels)}  "
            + ", ".join(f"{kind} {by_kind[kind]}" for kind in PANEL_KINDS if kind in by_kind)
        )
        lines.append(
            f"  kinds     {len(grids.get('panel_types') or [])} declared: "
            + ", ".join(str(entry.get("kind")) for entry in grids.get("panel_types") or [])
        )
    if registry is not None:
        components = registry.get("components") or []
        by_component_kind: dict[str, int] = {}
        for entry in components:
            key = str(entry.get("kind"))
            by_component_kind[key] = by_component_kind.get(key, 0) + 1
        lines.append(
            f"  blocks    {len(components)} distinct size classes  "
            + ", ".join(
                f"{kind} {by_component_kind[kind]}" for kind in COMPONENT_KINDS if kind in by_component_kind
            )
        )
        lines.append(
            f"  families  {len(registry.get('families') or [])} (one per panel kind, "
            "substitution size_matched)"
        )
        lines.append(
            f"  assumed   panel_thickness_cm {num(registry['defaults']['panel_thickness_cm'])} "
            f"({PANEL_THICKNESS_LEDGER}), joint_width_cm "
            f"{num(registry['defaults']['joint_width_cm'])} ({JOINT_WIDTH_LEDGER}) -- the only two "
            "numbers P5 does not derive, each its convention's declared default (09 D-CL-05, D-FM-10)"
        )
    for name in (FACADE_CSV_NAME, WORLD_CSV_NAME):
        if name in row_counts:
            lines.append(f"  {name} {row_counts[name]} data rows (one per panel)")
    tally = checks.tally()
    lines.append(f"  self-check G-57..G-70 {tally['pass']} pass, {tally['skip']} skip, {tally['fail']} fail")
    for skip in checks.skips():
        lines.append(f"    skip  {skip}")
    lines.append(
        f"  layer     data only -- the CSVs carry {FACADE_LAYER} in a layer column and nothing "
        "assigns a layer to anything (07 section 8.1.3)"
    )
    for path in written:
        lines.append(f"  wrote    {path}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build facade_grids.json, components_registry.json, facade_table.csv and "
            "world_table.csv from a locked dimensions.json and massing.json "
            "(07 sections 8.3, 8.4 and 9.8, invariants G-57..G-70)."
        )
    )
    parser.add_argument(
        "--stage", default="all", choices=list(STAGES), help="stage to build (default: all)"
    )
    parser.add_argument("--in", dest="in_dir", required=True, type=Path, help="specs directory to read")
    parser.add_argument(
        "--out", dest="out_dir", default=None, type=Path, help="output directory (default: --in)"
    )
    parser.add_argument("--json", dest="as_json", action="store_true", help="print a machine-readable summary")
    parser.add_argument(
        "--build",
        action="store_true",
        dest="build_gate",
        help="Enforce the 07 G-4 lock gate. This builder always enforces it; the flag exists so "
        "its CLI matches validate_specs.py.",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        dest="allow_draft",
        help="Draft work in progress: waive the lock gate. G-57..G-70 then run and fail, which is "
        "the point of the flag.",
    )
    args = parser.parse_args(argv)

    stage: str = args.stage
    specs_dir: Path = args.in_dir
    out_dir: Path = args.out_dir if args.out_dir is not None else specs_dir
    written: list[Path] = []
    row_counts: dict[str, int] = {}
    wants_grids = stage in ("grids", "all")
    wants_registry = stage in ("components", "all")
    wants_tables = stage in ("tables", "all")

    try:
        # Both root contracts are read on every stage, including --stage tables,
        # and the lock gate applies to both. The reason is G-64, not tidiness: a
        # `host_ref` leaf derives from `elements` in massing.json, so the rule
        # cannot resolve that path without the file, and a stage that skipped it
        # would report SKIP for the reason "we did not look".
        dimensions = read_spec(
            specs_dir,
            DIMENSIONS_NAME,
            args.allow_draft,
            ("tolerances", "facades", "levels", "openings", "site", "source"),
        )
        massing = read_spec(
            specs_dir,
            MASSING_NAME,
            args.allow_draft,
            ("elements",),
            expected_project=dimensions.get("project"),
        )

        grids: dict[str, Any] | None = None
        registry: dict[str, Any] | None = None

        if wants_grids:
            assert dimensions is not None and massing is not None
            grids, _model = build_grids(dimensions, massing)
            grids_text = serialize(grids, GRIDS_NAME)
            guard_existing_grids(specs_dir, grids_text, grids)
            grids = strict_loads(grids_text)  # check the bytes, not the intention

        check_grids = grids
        if wants_registry:
            if check_grids is None:
                check_grids = read_downstream(
                    specs_dir, GRIDS_NAME, expected_project=dimensions.get("project")
                )
            registry, panel_family, panel_component_kind, assignment = build_registry(
                check_grids, dimensions if dimensions is not None else {}
            )
            registry = strict_loads(serialize(registry, REGISTRY_NAME))
        else:
            panel_family = {}
            panel_component_kind = {}
            assignment = {}

        if wants_tables:
            table_grids = (
                check_grids
                if check_grids is not None
                else read_downstream(
                    specs_dir, GRIDS_NAME, expected_project=dimensions.get("project")
                )
            )
            table_registry = (
                registry
                if registry is not None
                else read_downstream(
                    specs_dir, REGISTRY_NAME, expected_project=dimensions.get("project")
                )
            )
            if panel_component_kind:
                table_kind = panel_component_kind
                table_family = panel_family
                table_assignment = assignment
            else:
                table_kind, table_family, table_assignment = resolve_assignment(table_grids, table_registry)

            checks = self_check(table_grids, table_registry, dimensions, massing, want_csvs=True)
            grids = table_grids if grids is None else grids
            missing = [rule for rule in RULES if rule not in checks.by_rule()]
            if missing:
                raise Refusal(
                    f"refusing to write: the self-check produced no row for {missing}. Every rule "
                    "in 07 section 9.8 reports pass, skip or fail; silence is not a result."
                )
            failures = checks.failures()
            if failures:
                raise Refusal(
                    "refusing to write: the self-check failed "
                    f"{len(failures)} invariant(s).\n  - " + "\n  - ".join(failures[:20])
                )

            facade_csv = render_csv(
                FACADE_CSV_COLUMNS, build_facade_rows(table_grids, table_kind)
            )
            world_csv = render_csv(
                WORLD_CSV_COLUMNS,
                build_world_rows(table_grids, table_registry, table_kind, table_family, table_assignment),
            )
            facade_path = out_dir / FACADE_CSV_NAME
            world_path = out_dir / WORLD_CSV_NAME
            to_write: list[tuple[Path, str]] = [(facade_path, facade_csv), (world_path, world_csv)]
            if wants_grids:
                assert grids is not None
                to_write.append((out_dir / GRIDS_NAME, serialize(grids, GRIDS_NAME)))
            if wants_registry:
                assert registry is not None
                to_write.append((out_dir / REGISTRY_NAME, serialize(registry, REGISTRY_NAME)))
            for target_path, payload in to_write:
                target_bytes = payload.encode("utf-8")
                if target_path.is_file() and target_path.read_bytes() != target_bytes:
                    raise Refusal(
                        f"refusing to overwrite {target_path}: differing existing content on disk (08.4 / A-WRITE / M34). "
                        "Resolve difference or remove file before rebuilding."
                    )
            write_bytes(facade_path, facade_csv)
            write_bytes(world_path, world_csv)
            written.extend([facade_path, world_path])
            # G-70 is asserted on the bytes that are now on disk, not on the
            # rows that were meant to be written, and by validate_specs' own
            # predicate rather than a second copy of the rule.
            facade_rows, world_rows = assert_emitted_tables(
                facade_path, world_path, table_grids, table_registry
            )
            row_counts[FACADE_CSV_NAME] = facade_rows
            row_counts[WORLD_CSV_NAME] = world_rows
            checks.replace(
                "G-70",
                "pass",
                f"read back off disk: {FACADE_CSV_NAME} and {WORLD_CSV_NAME} each carry "
                f"{facade_rows} data rows for {len(table_grids['panels'])} panels; every "
                "panel_ref, component_ref and family_ref resolves; every rot_z_deg equals its "
                "facade's run_angle_deg; instance_id equals panel_ref on every row",
            )
        else:
            checks = self_check(check_grids, registry, dimensions, massing, want_csvs=False)
            grids = check_grids if grids is None else grids
            missing = [rule for rule in RULES if rule not in checks.by_rule()]
            if missing:
                raise Refusal(
                    f"refusing to write: the self-check produced no row for {missing}. Every rule "
                    "in 07 section 9.8 reports pass, skip or fail; silence is not a result."
                )
            failures = checks.failures()
            if failures:
                raise Refusal(
                    "refusing to write: the self-check failed "
                    f"{len(failures)} invariant(s).\n  - " + "\n  - ".join(failures[:20])
                )
            to_write_non_tables: list[tuple[Path, str]] = []
            if wants_grids:
                assert grids is not None
                to_write_non_tables.append((out_dir / GRIDS_NAME, serialize(grids, GRIDS_NAME)))
            if wants_registry:
                assert registry is not None
                to_write_non_tables.append((out_dir / REGISTRY_NAME, serialize(registry, REGISTRY_NAME)))
            for target_path, payload in to_write_non_tables:
                target_bytes = payload.encode("utf-8")
                if target_path.is_file() and target_path.read_bytes() != target_bytes:
                    raise Refusal(
                        f"refusing to overwrite {target_path}: differing existing content on disk (08.4 / A-WRITE / M34). "
                        "Resolve difference or remove file before rebuilding."
                    )

        if wants_grids:
            assert grids is not None
            grids_path = out_dir / GRIDS_NAME
            write_bytes(grids_path, serialize(grids, GRIDS_NAME))
            written.append(grids_path)
        if wants_registry:
            assert registry is not None
            registry_path = out_dir / REGISTRY_NAME
            write_bytes(registry_path, serialize(registry, REGISTRY_NAME))
            written.append(registry_path)
    except Refusal as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSAL

    lock_gate = (
        "waived by --allow-draft"
        if dimensions is not None and dimensions.get("status") != "locked"
        else "enforced"
    )
    panels = (grids or {}).get("panels") or []
    by_kind: dict[str, int] = {}
    for panel in panels:
        key = str(panel.get("kind"))
        by_kind[key] = by_kind.get(key, 0) + 1

    if args.as_json:
        summary = {
            "builder": "scripts/facade_tables.py",
            "stage": stage,
            "project": (grids or registry or {}).get("project"),
            "spec": (grids or registry or {}).get("spec"),
            "read": [
                str(specs_dir / name)
                for name in (DIMENSIONS_NAME, MASSING_NAME)
                if (specs_dir / name).is_file()
            ],
            "wrote": [str(path) for path in written],
            "facade_count": len((grids or {}).get("facades") or []),
            "axis_count": len((grids or {}).get("axes") or []),
            "panel_count": len(panels),
            "panel_ids": [str(panel.get("id")) for panel in panels],
            "panels_by_kind": {kind: by_kind[kind] for kind in PANEL_KINDS if kind in by_kind},
            "panel_type_count": len((grids or {}).get("panel_types") or []),
            "component_count": len((registry or {}).get("components") or []),
            "component_ids": [str(entry.get("id")) for entry in (registry or {}).get("components") or []],
            "family_count": len((registry or {}).get("families") or []),
            "assumed_defaults": (
                {
                    "panel_thickness_cm": q(registry["defaults"]["panel_thickness_cm"]),
                    "joint_width_cm": q(registry["defaults"]["joint_width_cm"]),
                }
                if registry is not None
                else {}
            ),
            "csv_rows": row_counts,
            "partition": partition_report(grids) if grids is not None else {},
            "openings": opening_report(grids, dimensions) if grids is not None else {},
            "threshold_cm": {
                "pier_max": PIER_MAX_CM,
                "derives_from": "09-defaults.md D-OP-12 (15 cm, range 10..25) x 2",
                "mullion_rule": (
                    "adjacent to a curtain_wall opening's u-range on the same bay and "
                    "width <= pier_max, merged over that bay's whole storey height"
                ),
            },
            "layer_application": (
                f"data only; every panel and component carries layer {FACADE_LAYER} and no artefact "
                "assigns a layer to anything"
            ),
            "origin_inputs": len((grids or registry or {}).get("origin_inputs") or []),
            "origins": len((grids or registry or {}).get("origins") or {}),
            "self_check": checks.by_rule(),
            "self_check_tally": checks.tally(),
            "self_check_skips": checks.skips(),
            "g70_asserted_by_readback": bool(wants_tables),
            "lock_gate": lock_gate,
            "exit_code": EXIT_OK,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(summarise(stage, grids, registry, checks, written, row_counts, lock_gate))
    return EXIT_OK


def resolve_assignment(
    grids: dict[str, Any], registry: dict[str, Any]
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Panel -> component kind, panel -> family, panel -> component, read off disk.

    Only ``--stage tables`` needs this: it reads the two JSONs rather than
    recomputing them, so the CSV rows have to recover the same join the registry
    already states. A panel whose kind and size resolve to no component is a
    refusal, not a blank cell.
    """
    dimensions_like = {
        "openings": [],
    }
    del dimensions_like
    panel_component_kind: dict[str, str] = {}
    components = registry.get("components") or []
    tolerance, _source = linear_tolerance(grids, None)
    for panel in grids.get("panels") or []:
        kind = str(panel.get("kind"))
        width = q(as_float(panel.get("width_cm")) or 0.0)
        height = q(as_float(panel.get("height_cm")) or 0.0)
        matched = [
            str(entry.get("id"))
            for entry in components
            if kind in (entry.get("serves_panel_kinds") or [])
            and isinstance(entry.get("size_cm"), list)
            and len(entry["size_cm"]) >= 2
            and close(entry["size_cm"][0], width, tolerance)
            and close(entry["size_cm"][1], height, tolerance)
        ]
        if not matched:
            raise Refusal(
                f"refusing to build: panel {panel.get('id')!r} ({kind}, {num(width)} x "
                f"{num(height)}) resolves to no component in {REGISTRY_NAME} (G-68). Rebuild the "
                "registry, or the grid, rather than emitting a row that names no block."
            )
        if len(matched) > 1:
            raise Refusal(
                f"refusing to build: panel {panel.get('id')!r} resolves to {len(matched)} components "
                f"({matched}); G-68 requires all matching components to sit in one family"
            )
        panel_component_kind[str(panel.get("id"))] = str(
            next(
                entry.get("kind")
                for entry in components
                if str(entry.get("id")) in matched
            )
        )
    family_of = {
        str(member): str(family.get("id"))
        for family in registry.get("families") or []
        for member in family.get("component_ids") or []
    }
    assignment: dict[str, str] = {}
    panel_family: dict[str, str] = {}
    for panel in grids.get("panels") or []:
        identifier = str(panel.get("id"))
        kind = str(panel.get("kind"))
        width = q(as_float(panel.get("width_cm")) or 0.0)
        height = q(as_float(panel.get("height_cm")) or 0.0)
        component = next(
            str(entry.get("id"))
            for entry in components
            if kind in (entry.get("serves_panel_kinds") or [])
            and close(entry["size_cm"][0], width, tolerance)
            and close(entry["size_cm"][1], height, tolerance)
        )
        assignment[identifier] = component
        panel_family[identifier] = family_of.get(component, "")
    return panel_component_kind, panel_family, assignment


def partition_report(grids: dict[str, Any]) -> dict[str, Any]:
    """The G-61 numbers, reported rather than only asserted."""
    facade_by_id = {str(entry.get("id")): entry for entry in grids.get("facades") or []}
    height_of = {
        (str(facade.get("id")), level.get("level_index")): as_float(level.get("height_cm")) or 0.0
        for facade in grids.get("facades") or []
        for level in facade.get("levels") or []
    }
    buckets: dict[tuple[str, Any], list[dict[str, Any]]] = {}
    for panel in grids.get("panels") or []:
        buckets.setdefault((str(panel.get("facade")), panel.get("level_index")), []).append(panel)
    worst_overlap = 0.0
    groups: list[dict[str, Any]] = []
    for key in sorted(buckets, key=lambda item: str(item)):
        panels = buckets[key]
        facade = facade_by_id.get(key[0], {})
        length = as_float(facade.get("length_cm")) or 0.0
        height = height_of.get(key, 0.0)
        total = sum(
            (as_float(panel.get("width_cm")) or 0.0) * (as_float(panel.get("height_cm")) or 0.0)
            for panel in panels
        )
        for first in range(len(panels)):
            for second in range(first + 1, len(panels)):
                a, b = panels[first], panels[second]
                du = min(as_float(a.get("u_max_cm")) or 0.0, as_float(b.get("u_max_cm")) or 0.0) - max(
                    as_float(a.get("u_min_cm")) or 0.0, as_float(b.get("u_min_cm")) or 0.0
                )
                dv = min(as_float(a.get("v_max_cm")) or 0.0, as_float(b.get("v_max_cm")) or 0.0) - max(
                    as_float(a.get("v_min_cm")) or 0.0, as_float(b.get("v_min_cm")) or 0.0
                )
                if du > 0.0 and dv > 0.0:
                    worst_overlap = max(worst_overlap, du * dv)
        groups.append(
            {
                "facade": key[0],
                "level_index": key[1],
                "panel_count": len(panels),
                "sum_area_m2": q(total / 10000.0),
                "rect_area_m2": q(length * height / 10000.0),
                "delta_area_m2": q((total - length * height) / 10000.0),
            }
        )
    return {"groups": groups, "max_pairwise_overlap_cm2": q(worst_overlap)}


def opening_report(grids: dict[str, Any], dimensions: dict[str, Any] | None) -> dict[str, Any]:
    """Which openings are realised by one panel and which the v grid split."""
    by_opening: dict[str, list[dict[str, Any]]] = {}
    for panel in grids.get("panels") or []:
        reference = panel.get("opening_ref")
        if reference is not None:
            by_opening.setdefault(str(reference), []).append(panel)
    types = {
        str(entry.get("id")): str(entry.get("type"))
        for entry in (dimensions or {}).get("openings") or []
        if isinstance(entry, dict)
    }
    split: list[dict[str, Any]] = []
    single = 0
    for reference in sorted(by_opening):
        panels = sorted(
            by_opening[reference], key=lambda panel: as_float(panel.get("v_min_cm")) or 0.0
        )
        entry = {"opening": reference, "type": types.get(reference, "?"), "panel_count": len(panels)}
        if len(panels) > 1:
            split.append(entry)
        else:
            single += 1
    unreferenced = sorted(
        str(item.get("id"))
        for item in (dimensions or {}).get("openings") or []
        if isinstance(item, dict) and str(item.get("id")) not in by_opening
    )
    return {
        "openings_total": len((dimensions or {}).get("openings") or []),
        "single_panel": single,
        "split_by_v_grid": split,
        "unreferenced": unreferenced,
    }


if __name__ == "__main__":
    sys.exit(main())