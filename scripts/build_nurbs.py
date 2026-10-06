#!/usr/bin/env python3
"""Stage `nurbs`: locked nurbs.json -> normalised nurbs.json + nurbs.ms.

Mirrors `scripts/build_spec.py` (stage `massing`): the same envelope gate, the
same self-check-against-the-bytes discipline, the same determinism contract and
the same `--json` shape, applied to the one primitive 07 section 8.2 defines:

    <out>/nurbs.json   the spec re-emitted in canonical form, strict JSON,
                       UTF-8 no BOM, LF, exactly one final newline
    <out>/nurbs.ms     geometry only -- no layer code (07 section 8.1.3)

Usage
-----
    python scripts/build_nurbs.py --in <specs_dir> --out <out_dir> [--json]
    python scripts/build_nurbs.py --in examples --out examples
    python scripts/build_nurbs.py --in examples --allow-draft

Exit codes
----------
    0   built, and the self-check passed G-41..G-56 against the bytes on disk
    1   a refusal: the lock gate, a failed self-check, or an emitted script that
        would not run. The message names the file, the id and the rule.
    2   usage error

DETERMINISM (07 S-5)
--------------------
The same locked input produces byte-identical output. Nothing reads a clock, a
random source or an unordered container: node names come from spec ids, every
number goes through `q()` (6 decimals, negative zero normalised), integer
arguments go through `inum()`, `origins` is emitted in document order,
`origin_inputs` is a sorted set, and the one path that is not in the spec -- the
absolute path of the library -- is derived from `__file__`, which is fixed for a
checkout.

THE EMITTED MAXSCRIPT, AND WHY IT IS SHAPED THIS WAY
----------------------------------------------------
Everything below was established by execution against live 3ds Max 2026.3.2 on
2026-10-04 and is recorded in `CHECKPOINT.md`; a stage that emits `.ms` owns
these rules and must not "improve" on them:

* **One function.** `local` at the top level of a `fileIn`-ed script is a
  compile error (`no local declarations at top level`), so the whole body lives
  inside `fn mcpNurbsBuild_<project>` and the file ends with one call to it.
* **Explicit-local delete guards.** `if (getNodeByName "X") != undefined do (
  delete (getNodeByName "X") )` throws `Type error: Call needs function or
  class, got: undefined` when the node is absent, so every guard binds the
  lookup first. Derivatives are deleted before the surfaces they sample, so a
  second `fileIn` converges on the same scene and the same node count.
* **The library is loaded once.** `if MCP_NURBS_Arch == undefined do ( fileIn
  "<abs path>" )` -- a global comparison, not the broken one-liner form.
* **No literal sub-object index, ever.** A `point_grid` of nU x nV contributes
  nU*nV `NURBSPoint` sub-objects *before* the surface, so its index is
  `nU*nV + 1` (measured: a 5 x 3 lattice put the surface at 16), and a `cv_grid`
  puts it at 1. A five-rib `u_loft` measured 52 sub-objects with the base
  surface at 51 and the offset shell at 52. The counts are not knowable until
  the set is built, so one shared local helper resolves the surface by
  `superClassOf o == NURBSSurface`, takes the **first** match -- the design
  surface, since a `thickness_cm` shell appends its offset surface afterwards --
  and throws a named error when there is none. `verify_script` rejects the
  emitted script if a surface index appears as a literal.
* **F9 and F10 take their division arguments positionally** -- `surfSetIndex
  uDivs vDivs` and `surfSetIndex uCells vCells` are not keywords.
* **Integer arguments are emitted as integers.** `view_steps_*`, `divisions_*`,
  `sub_steps`, `u_order` and `v_order` drive `for` ranges, array strides and
  `polyop` indices, so they are never emitted as `8.0`.
* **`try ( ) catch ( )` is the only tolerated form**; `try { } catch { }` is a
  parse error and `getCurrentException()` does not exist.
* **`("x" + i as string)` throws**, hence `("x" + (i as string))` -- used by the
  library, not re-invented here.
* **Node names use `_`, never `-`**, because a hyphen reads as subtraction once
  the name is pasted into MAXScript (11 section 3.1 N1).
* **`merge_tol_cm` on a loft is applied after the fact.** F6 (`createULoftShell`)
  and F7 (`createUVLoftNetwork`) hardcode `nset.merge = 0.15` and take no merge
  keyword, so the script re-applies the spec value through `getNURBSSet` --
  the same route the library itself uses to read a set. Every surface then gets
  an explicit `applyArchTessellation` call carrying the `approximation` block,
  because the grid and loft functions only forward `hideCurves`.

THE FOUR DEPENDENT KINDS, AND WHAT G-54 IS FOR
---------------------------------------------
`CHECKPOINT.md` section "P4b schema extension" is the contract. `rail_sweep`,
`two_rail_sweep`, `blend` and `trim` are built here as **flat statements in the
one function**, with no new library function, because the four classes that
implement them take their arguments positionally and by index and are fully
executable as written.

| kind | keys it adds | what is emitted |
|---|---|---|
| `rail_sweep` | `rail_section_ids` (1), `section_ids` (>= 2), `parallel` (default `true`) | `NURBS1RailSweepSurface rail:<i> parallel:<b>`, one `appendCurve` per cross-section |
| `two_rail_sweep` | `rail_section_ids` (2), `section_ids` (>= 2), `parallel` | `NURBS2RailSweepSurface rail1:<i> rail2:<j> parallel:<b>`, one `appendCurve` per cross-section |
| `blend` | `parent1_ref`, `edge1`, `parent2_ref`, `edge2`, `tension1`, `tension2` (`0.0`) | `NURBSBlendSurface parent1ID:<var> edge1:<n> parent2ID:<var> edge2:<n> tension1:<f> tension2:<f>` |
| `trim` | `surface_ref`, `trim_section_ids` (>= 1 closed profile), `p_vec`, `seed` (`[0.5,0.5]`), `flip_trim` (`false`) | one `NURBSPointCurve` profile and one `NURBSProjectVectorCurve` per profile: `parent1ID:<var> parent2:<profile ordinal> pVec:[..] seed:[..] trim:false flipTrim:<b>` |

Four emission rules, all consequences of executed transcripts
(`_P4B_EVIDENCE.md`, live 3ds Max 2026.3.2, 2026-10-04):

* **Every sub-object index is bound to a variable the moment it is appended**
  (`rail1Index = <set>.numObjects`) and the variable is what the constructor
  receives. A literal is a defect here for the same reason it is one for F9/F10,
  and `verify_script` now refuses one after `rail:` / `rail1:` / `rail2:` /
  `parent1:` / `parent2:` as well as after F9/F10.
* **A rail stays an in-set ordinal; a surface parent becomes a `nurbsID`.**
  D3 measured that a relation's parent need not live inside the relation's own
  `NURBSSet`: built as its own node, its first committed `NURBSSurface` hands
  over a `nurbsID` that the constructor takes through `parent1ID:` /
  `parent2ID:`, the relation set then holds only the relation, and the parent's
  own node survives so a derivative on it keeps working. So the parent is **not**
  re-instantiated -- that duplication is why `SUR_001_Vault` used to appear three
  times in one scene -- and the emitted script binds
  `local id_<parent> = mcpNurbsSurfID <parent> "<parent>"` immediately after the
  parent's node is committed. `mcpNurbsSurfID` reads the **first**
  `NURBSSurface` in the parent's committed set (P4's "read the first surface"
  rule: a `thickness_cm > 0` appends its offset shell after the design surface)
  and throws a named error when there is none.
* **A rail is a curve, not a surface, so `rail:` is unchanged.** `rail1:` /
  `rail2:` name an index within the set being constructed and the P4b live run
  verified them there. Only the *surface* parents moved to `*ID:`. NOTE
  `NURBS1RailSweepSurface` has `railID`, **not** `rail1ID` (CHECKPOINT
  "Recovered keyword map"), so the `rail1ID:` spelling does not exist at all.
* **G-54 counts what the commit actually produced.** An invalid dependent
  surface is **dropped at commit with no error and no warning**, so a build that
  merely completes proves nothing. Every dependent node is counted after
  `NURBSNode` + `stopCreating` and the emitted script throws a named error
  naming the node, the expected count and the actual count. The expected counts
  are read off what the emission above actually appends, not off the P4b
  in-set-parent arrangement that D3 replaced:
  `rail_sweep` 1, `two_rail_sweep` 1 (their rails and cross-sections are all
  `NURBSPointCurve`s, and D6 measured that a point curve commits no surface),
  `blend` 1 (D3: "the relation set holds **one** sub-object"), `trim` **0**
  (D5: `trim:false` "produces no surface at all"; `trim:true` does not cut, it
  adds a `NURBSCVSurface` copy of the *parent*). The counts are
  **self-correcting**: if a count here is wrong, the first `fileIn` reports the
  actual number in the error and the number in `expected_census()` is what has
  to change. Treat the first live run of a dependent spec as the measurement,
  not as a formality.
  The census is scoped to the four dependent kinds, whose surface is the only
  one that can be lost this way, and scoping is also what keeps the emitted
  bytes of every pre-P4b spec identical.

TENSION IS 0.0, NOT 1.0 (D1)
---------------------------
`NURBSBlendSurface tension1/tension2` measure the deviation from a straight
transition between the two selected edges. On the worked example,
`tension 0.0/0.0` fills *exactly* the gap (`Y 450..900`, `Z 420..600.97`) while
`tension 1.0/1.0` pushes the same blend **295.64 cm past the vault's own
y = 900** and drops 50 cm below the springing. 1.0 is not a neutral default, and
Max does not bound the overshoot above, so the schema does -- that is G-55, and
it is why the fallback here is `0.0`.

WHAT THIS BUILDER REFUSES
-------------------------
* A spec value with no node in the emitted script. `verify_script` walks the
  document instead of trusting the emitter, exactly as `build_spec.py` does.
* A `point_grid` / `cv_grid` lattice that is not rectangular, because the
  library throws at runtime and a spec that builds nothing is a defect, not a
  warning.
* A `thickness_cm` under 0.001 on a `u_loft`: F6 tests `abs thickness > 0.001`
  and silently omits the offset surface, so the spec would build to nothing.
* **G-51**: a rail-sweep cross-section that never comes within
  `tolerances.linear_cm` of **every** rail, measured point-to-segment against the
  rail polyline. This is the pre-flight for the silent drop above, and it is the
  one check in this file that measures geometry rather than reading a key.
* A relation that names a surface declared **later** in the file (G-52), and a
  relation parent whose kind commits no `NURBSSurface` at all -- a `trim`, whose
  census is 0 -- because the builder would have no `nurbsID` to bind and would
  have to invent a pointer, and a synthetic pointer crashes Max with
  `EXCEPTION_ACCESS_VIOLATION` (D4). That is G-56, refused by name.
* A non-`locked` file (07 section 3.1). `--allow-draft` waives the gate, and
  then G-41..G-56 run and fail -- which is the point of the flag.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Sequence

SUPPORTED_SCHEMA_MAJOR = 1
SCHEMA_VERSION = "1.0"

UPSTREAM_NAME = "nurbs.json"
OUT_JSON_NAME = "nurbs.json"
OUT_MS_NAME = "nurbs.ms"
LIBRARY_RELATIVE = ("snippets", "nurbs_arch_library.ms")

SECTION_ID_RE = re.compile(r"^SEC-\d{3}$")
SURFACE_ID_RE = re.compile(r"^SUR-\d{3}$")
DERIVATIVE_ID_RE = re.compile(r"^DRV-\d{3}$")
PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
NODE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

SURFACE_KINDS: tuple[str, ...] = (
    "u_loft",
    "uv_loft",
    "point_grid",
    "cv_grid",
    "rail_sweep",
    "two_rail_sweep",
    "blend",
    "trim",
)
#: The four kinds whose surface is a *relation*. These are the only kinds whose
#: NURBSSurface sub-object can be dropped silently at commit (CHECKPOINT P4b),
#: so they are the only ones G-51 and G-54 apply to, and the only ones that get
#: parent/rail index plumbing in the emitted script.
DEPENDENT_KINDS: tuple[str, ...] = ("rail_sweep", "two_rail_sweep", "blend", "trim")
RAIL_SWEEP_KINDS: tuple[str, ...] = ("rail_sweep", "two_rail_sweep")
#: A relation parent is named by `nurbsID`, read from the FIRST `NURBSSurface` of
#: the parent's own committed node (D3) -- it is no longer re-instantiated inside
#: the dependent set. So the parent must be a kind this builder commits as a node
#: holding at least one `NURBSSurface`. Every kind here does; `trim` does NOT
#: (D5: `trim:false` "produces no surface at all", census 0), which is why it is
#: absent and is refused by name under G-50 and G-56. A `u_loft` parent binds its
#: BASE surface, not its offset shell: P4's rule is that the first `NURBSSurface`
#: in the set is the design surface, and the shell is appended after it.
RELATION_PARENT_KINDS: tuple[str, ...] = (
    "u_loft",
    "uv_loft",
    "point_grid",
    "cv_grid",
    "rail_sweep",
    "two_rail_sweep",
    "blend",
)
DERIVATIVE_KINDS: tuple[str, ...] = ("quad_panels", "space_frame")
SURFACE_LAYERS: tuple[str, ...] = ("04_ROOF", "05_FACADE")
DERIVATIVE_LAYERS: tuple[str, ...] = ("04_ROOF", "05_FACADE", "99_DEBUG")
SURFACE_COMMON_KEYS: tuple[str, ...] = (
    "layer",
    "mat_id",
    "hide_curves",
    "merge_tol_cm",
    "approximation",
)
KIND_REQUIRED: dict[str, tuple[str, ...]] = {
    "u_loft": ("section_ids",),
    "uv_loft": ("u_section_ids", "v_section_ids"),
    "point_grid": ("section_ids",),
    "cv_grid": ("section_ids",),
    "rail_sweep": ("rail_section_ids", "section_ids"),
    "two_rail_sweep": ("rail_section_ids", "section_ids"),
    "blend": ("parent1_ref", "edge1", "parent2_ref", "edge2"),
    "trim": ("surface_ref", "trim_section_ids", "p_vec"),
}
KIND_OPTIONAL: dict[str, tuple[str, ...]] = {
    "u_loft": ("closed_sections", "thickness_cm"),
    "uv_loft": (),
    "point_grid": (),
    "cv_grid": ("u_order", "v_order", "weights"),
    "rail_sweep": ("parallel",),
    "two_rail_sweep": ("parallel",),
    "blend": ("tension1", "tension2"),
    "trim": ("seed", "flip_trim"),
}
APPROX_KEYS: tuple[str, ...] = (
    "view_steps_u",
    "view_steps_v",
    "render_edge_pct",
    "render_angle_deg",
    "merge_tol_cm",
)
APPROX_DEFAULTS: dict[str, float] = {
    "view_steps_u": 6.0,
    "view_steps_v": 6.0,
    "render_edge_pct": 4.0,
    "render_angle_deg": 6.0,
    "merge_tol_cm": 0.15,
}
SURFACE_DEFAULTS: dict[str, Any] = {
    "layer": "04_ROOF",
    "mat_id": 1,
    "hide_curves": True,
    "merge_tol_cm": 0.15,
}
DERIVATIVE_DEFAULTS: dict[str, Any] = {"layer": "99_DEBUG", "thickness_cm": 10.0, "sub_steps": 4}
#: CHECKPOINT "P4b schema extension": parallel defaults to true, flip_trim to
#: false, and the project seed to the surface's own mid-parameter -- the value the
#: executed transcript passed and read back.
#:
#: The blend tensions default to **0.0**, not the 1.0 CHECKPOINT's P4b table
#: records. D1 measured both on the worked example: `0.0/0.0` fills exactly the
#: gap between the two selected edges (`Y 450..900`, `Z 420..600.97`), while
#: `1.0/1.0` bulges 295.64 cm past the vault's own `y = 900` and 50 cm below the
#: springing. Max does not bound that overshoot, so G-55 bounds the input.
PARALLEL_DEFAULT = True
TENSION_DEFAULTS: dict[str, float] = {"tension1": 0.0, "tension2": 0.0}
SEED_DEFAULT: tuple[float, float] = (0.5, 0.5)
FLIP_TRIM_DEFAULT = False
#: D5 -- `trim:true` does NOT cut. Two structurally different profiles produced
#: byte-identical output (one of which a real trim would have split in two), and
#: what `trim:true` adds to the set is an untrimmed `NURBSCVSurface` COPY of the
#: parent. `trim:false` produces no surface at all. So the builder emits false and
#: the `trim` census is 0; the kind is projection-only and cutting an aperture
#: needs a Boolean modifier, which is outside the NURBS stage.
TRIM_FLAG = False
#: G-55 -- the tension range the schema enforces, compared exactly (no epsilon).
TENSION_MIN = 0.0
TENSION_MAX = 1.0
#: edge1 / edge2 are 1..4 = low-U, high-U, low-V, high-V -- the convention the
#: executed transcripts used (`edge1: 1 edge2: 1` read back exactly).
EDGE_MIN = 1
EDGE_MAX = 4

SECTION_KEY_ORDER: tuple[str, ...] = ("id", "points_cm", "name")
SURFACE_KEY_ORDER: tuple[str, ...] = (
    "id",
    "name",
    "kind",
    "layer",
    "section_ids",
    "u_section_ids",
    "v_section_ids",
    "rail_section_ids",
    "trim_section_ids",
    "parent1_ref",
    "parent2_ref",
    "surface_ref",
    "edge1",
    "edge2",
    "tension1",
    "tension2",
    "p_vec",
    "seed",
    "flip_trim",
    "parallel",
    "closed_sections",
    "thickness_cm",
    "u_order",
    "v_order",
    "weights",
    "mat_id",
    "hide_curves",
    "merge_tol_cm",
    "approximation",
)
DERIVATIVE_KEY_ORDER: tuple[str, ...] = (
    "id",
    "kind",
    "surface_ref",
    "name",
    "layer",
    "divisions_u",
    "divisions_v",
    "thickness_cm",
    "sub_steps",
)
APPROX_KEY_ORDER: tuple[str, ...] = APPROX_KEYS

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

RULES: tuple[str, ...] = (
    "G-41",
    "G-42",
    "G-43",
    "G-44",
    "G-45",
    "G-46",
    "G-47",
    "G-48",
    "G-49",
    "G-50",
    "G-51",
    "G-52",
    "G-53",
    "G-54",
    "G-55",
    "G-56",
)

MIN_ORDER = 2
MAX_ORDER = 5
MIN_SHELL_THICKNESS_CM = 0.001
DRAFT_SKIP_REASON = (
    'status is not "locked"; 07 section 9.7 does not evaluate a draft nurbs.json, '
    "because the file is computed from massing.json and a placeholder declares no "
    "provenance to check. --allow-draft forces the rule to run, where it will fail."
)
#: The measured distance-comparison epsilon. build_spec.py uses the same one, so
#: a G-51 boundary decision matches a massing boundary decision.
TOLERANCE_EPSILON = 1e-9

_TOKEN_RE = re.compile(r"([^.\[\]]+)|\[(\d+)\]")

EXIT_OK = 0
EXIT_REFUSAL = 1
EXIT_USAGE = 2


class Refusal(Exception):
    """A deliberate non-zero exit. The message names the file, id or rule."""


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


def q(value: Any) -> float:
    """Round to 6 decimals and normalise -0.0, so the bytes never wobble."""
    number = float(value)
    rounded = round(number, 6)
    return 0.0 if rounded == 0.0 else rounded


def inum(value: Any) -> int:
    return int(round(float(value)))


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None or not float(number).is_integer():
        return None
    return int(number)


def is_point3(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(as_float(item) is not None and math.isfinite(as_float(item)) for item in value)
    )


def num(value: Any) -> str:
    """MAXScript float literal: 1800 -> '1800.0', 539.059 -> '539.059'."""
    number = q(value)
    if float(number).is_integer():
        return f"{int(number)}.0"
    return repr(float(number))


def node_name(spec_id: Any) -> str:
    """11 section 3.1 N1: the node name is the spec id with dashes replaced."""
    return str(spec_id).replace("-", "_")


# --------------------------------------------------------------------------- #
# Geometry and tolerance helpers (G-51)
# --------------------------------------------------------------------------- #


def linear_tolerance(
    document: dict[str, Any], dimensions: dict[str, Any] | None
) -> tuple[float, str]:
    """``tolerances.linear_cm`` for an arithmetic comparison, and where it came from.

    This file's own block wins, then ``dimensions.json``'s, then 07 section 3.3's
    declared 0.5 cm -- the same fallback order `build_spec.py` uses. The returned
    source string is what a PASS or FAIL message names, because a tolerance with
    no provenance is a number somebody guessed.
    """
    for label, candidate in (("this file's", document), ("dimensions.json's", dimensions)):
        block = candidate.get("tolerances") if isinstance(candidate, dict) else None
        value = as_float(block.get("linear_cm")) if isinstance(block, dict) else None
        if value is not None and value >= 0.0:
            return value, f"{label} tolerances.linear_cm"
    return 0.5, "07 section 3.3's declared 0.5 cm (neither this file nor dimensions.json declares one)"


def point_segment_distance(point: Sequence[float], start: Sequence[float], end: Sequence[float]) -> float:
    """Distance from a point to the *segment* start..end, not to either endpoint.

    A rail is a polyline of `points_cm`, so its segments matter. Measuring to the
    nearest vertex instead would call a section that passes through the middle of
    a 4 m rail "4000 cm away" and refuse a sweep Max builds perfectly.
    """
    ax, ay, az = (float(start[0]), float(start[1]), float(start[2]))
    bx, by, bz = (float(end[0]), float(end[1]), float(end[2]))
    dx, dy, dz = bx - ax, by - ay, bz - az
    length_squared = dx * dx + dy * dy + dz * dz
    px, py, pz = (float(point[0]), float(point[1]), float(point[2]))
    if length_squared <= 0.0:
        return math.dist((px, py, pz), (ax, ay, az))
    t = ((px - ax) * dx + (py - ay) * dy + (pz - az) * dz) / length_squared
    t = min(1.0, max(0.0, t))
    return math.dist((px, py, pz), (ax + t * dx, ay + t * dy, az + t * dz))


def polyline_distance(left: Any, right: Any) -> float:
    """Smallest point-to-segment distance between two open polylines."""
    best: float | None = None
    for point in left:
        for index in range(1, len(right)):
            distance = point_segment_distance(point, right[index - 1], right[index])
            if best is None or distance < best:
                best = distance
    return float("inf") if best is None else best


def expected_census(surface: dict[str, Any]) -> int:
    """How many `NURBSSurface` sub-objects the spec says this node must hold.

    Measured, not guessed. For the lattice routes: a `point_grid` of nU x nV
    contributes nU*nV `NURBSPoint` sub-objects *before* the surface, a `cv_grid`
    contributes the surface alone, and a shelled `u_loft` appends its offset
    after the base.

    For the four dependent kinds the count is read off what the emission
    actually appends to the node's own set (`_P4B_EVIDENCE.md`):

    * `rail_sweep` / `two_rail_sweep` **1** -- every rail and every cross-section
      is a `NURBSPointCurve`, and D6 measured that a point curve commits as
      points + curve with no surface, so only the sweep itself is one.
    * `blend` **1** -- D3, "the relation set holds **one** sub-object". The two
      parents are named by `nurbsID` from their own nodes and are not in this
      set at all.
    * `trim` **0** -- D5: `trim:false` "produces no surface at all"; `trim:true`
      does not cut, it adds a `NURBSCVSurface` copy of the *parent*.

    A `trim` count of 0 is a real expectation, not a missing one: the census
    helper still runs and asserts that nothing extra committed.
    """
    kind = surface.get("kind")
    if kind == "u_loft":
        thickness = as_float(surface.get("thickness_cm", 0.0)) or 0.0
        return 2 if abs(thickness) > MIN_SHELL_THICKNESS_CM else 1
    if kind in ("uv_loft", "point_grid", "cv_grid", "rail_sweep", "two_rail_sweep", "blend"):
        return 1
    if kind == "trim":
        return 0
    return -1


def build_fn_name(project: Any) -> str:
    return "mcpNurbsBuild_" + re.sub(r"[^A-Za-z0-9_]", "_", str(project))


def id_variable_for(node: str) -> str:
    """The local that holds a committed node's first-surface `nurbsID` (D3).

    One prefix, one helper, one purpose: `mcpNurbsSurfIndex` binds `idx_<node>` for
    the derivative path, `mcpNurbsSurfID` binds `id_<node>` for the relation-parent
    path, and the census binds `census_<node>`. G-56 checks that every `parent1ID:` /
    `parent2ID:` slot carries exactly one of these.
    """
    return f"id_{node}"


def library_path() -> str:
    resolved = Path(__file__).resolve().parent.parent.joinpath(*LIBRARY_RELATIVE)
    return resolved.as_posix()


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
    """Every leaf path that needs an ``origins`` entry, in file order."""
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


def _ordered(source: dict[str, Any], order: Sequence[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in order:
        if key in source:
            out[key] = source[key]
    for key in sorted(source):
        if key not in out:
            out[key] = source[key]
    return out


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


def normalise(document: dict[str, Any]) -> dict[str, Any]:
    """Canonical key order and canonical numbers, in place of a stable text dump."""
    out: dict[str, Any] = {}
    for key, value in document.items():
        if key == "sections" and isinstance(value, list):
            out[key] = [
                _ordered(_round_tree(item), SECTION_KEY_ORDER) if isinstance(item, dict) else item
                for item in value
            ]
        elif key == "surfaces" and isinstance(value, list):
            surfaces = []
            for item in value:
                if not isinstance(item, dict):
                    surfaces.append(item)
                    continue
                entry = _ordered(_round_tree(item), SURFACE_KEY_ORDER)
                approximation = entry.get("approximation")
                if isinstance(approximation, dict):
                    entry["approximation"] = _ordered(approximation, APPROX_KEY_ORDER)
                surfaces.append(entry)
            out[key] = surfaces
        elif key == "derivatives" and isinstance(value, list):
            out[key] = [
                _ordered(_round_tree(item), DERIVATIVE_KEY_ORDER) if isinstance(item, dict) else item
                for item in value
            ]
        elif key == "origin_inputs" and isinstance(value, list):
            out[key] = sorted({str(item) for item in value})
        else:
            out[key] = _round_tree(value)
    return out


def load_spec(specs_dir: Path, allow_draft: bool) -> dict[str, Any]:
    """07 section 3.1: never build from anything that is not `locked`."""
    path = specs_dir / UPSTREAM_NAME
    if not path.is_file():
        raise Refusal(
            f"refusing to build: {UPSTREAM_NAME} not found in {specs_dir}. nurbs.json is "
            "hand-authored at P4 -- this stage reads it and emits the normalised spec plus "
            "the MAXScript, it does not compute the geometry."
        )
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise Refusal(
            f"refusing to build: {path} starts with a UTF-8 BOM (07 G-7). Strip it and "
            "lock the file again."
        )
    try:
        document = strict_loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal(
            f"refusing to build: {path} is not strict JSON -- {exc}. A half-read spec must "
            "never become geometry (07 section 3.1)."
        ) from exc
    if not isinstance(document, dict):
        raise Refusal(
            f"refusing to build: {path} top level is {type(document).__name__}, not an object "
            "(07 section 3.1)."
        )

    status = document.get("status")
    if status != "locked":
        if not allow_draft:
            raise Refusal(
                f"refusing to build: {path} has status {status!r}, not 'locked'. 07 section "
                "3.1: a builder must refuse to consume a draft or superseded file and must "
                "say which file and which status it found. Pass --allow-draft to build a "
                "draft anyway; G-41..G-49 will then run and fail."
            )
        status = status

    version = document.get("schema_version")
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?$", str(version))
    if match is None or int(match.group(1)) != SUPPORTED_SCHEMA_MAJOR:
        raise Refusal(
            f"refusing to build: {path} declares schema_version {version!r}; this builder "
            f"implements major {SUPPORTED_SCHEMA_MAJOR} and must stop rather than guess "
            "(07 G-3)."
        )

    project = document.get("project")
    if not isinstance(project, str) or not PROJECT_ID_RE.match(project):
        raise Refusal(
            f"refusing to build: {path} project {project!r} does not match 07 section 3.1 "
            "^[a-z0-9][a-z0-9._-]*$."
        )

    if document.get("spec") != path.stem:
        raise Refusal(
            f"refusing to build: {path} declares spec {document.get('spec')!r}, not "
            f"{path.stem!r} (07 G-2)."
        )

    for key in ("sections", "surfaces", "derivatives"):
        if not isinstance(document.get(key), list):
            raise Refusal(
                f"refusing to build: {path} is missing {key!r} or it is not an array, which "
                f"07 section 8.2 requires."
            )
    if not document["surfaces"]:
        raise Refusal(
            f"refusing to build: {path} declares no surfaces. A nurbs spec with no surface "
            "emits no geometry, and a spec with no node is a hole nobody would notice."
        )
    return document


def surface_settings(surface: dict[str, Any]) -> dict[str, Any]:
    layer = surface.get("layer", SURFACE_DEFAULTS["layer"])
    mat_id = surface.get("mat_id", SURFACE_DEFAULTS["mat_id"])
    hide_curves = surface.get("hide_curves", SURFACE_DEFAULTS["hide_curves"])
    merge_tol = surface.get("merge_tol_cm", SURFACE_DEFAULTS["merge_tol_cm"])
    approximation = surface.get("approximation") if isinstance(surface.get("approximation"), dict) else {}
    resolved: dict[str, float] = {}
    for key in APPROX_KEYS:
        resolved[key] = float(approximation.get(key, APPROX_DEFAULTS[key]))
    return {
        "layer": layer,
        "mat_id": mat_id,
        "hide_curves": hide_curves,
        "merge_tol_cm": merge_tol,
        "approximation": resolved,
    }


def derivative_settings(derivative: dict[str, Any]) -> dict[str, Any]:
    return {
        "layer": derivative.get("layer", DERIVATIVE_DEFAULTS["layer"]),
        "thickness_cm": derivative.get("thickness_cm", DERIVATIVE_DEFAULTS["thickness_cm"]),
        "sub_steps": derivative.get("sub_steps", DERIVATIVE_DEFAULTS["sub_steps"]),
    }


def _ids(table: Sequence[dict[str, Any]], pattern: re.Pattern[str], rule: str, label: str, checks: Checks) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    previous = ""
    for entry in table:
        ident = str(entry.get("id"))
        if not pattern.match(ident):
            checks.fail(rule, f"{label} id {ident!r} does not match {pattern.pattern}")
        if ident in seen:
            checks.fail(rule, f"{label} id {ident!r} is not unique")
        if previous and ident <= previous:
            checks.fail(rule, f"{label} id {ident!r} does not ascend (previous is {previous})")
        seen.add(ident)
        ordered.append(ident)
        previous = ident
    return ordered


def ref_families(kind: str) -> tuple[tuple[str, ...], ...]:
    """Which of a surface's section keys must carry one consistent point count.

    G-42 was written for lattices and lofts, where every row of one family is
    either the same length or the build fails. A rail sweep adds a second family
    with a *different* shape on purpose -- a 900 cm rail and a 300 cm cross-section
    -- so rails are compared against each other, never against a cross-section,
    and a trim's closed profiles are only required to be closed.
    """
    if kind in ("u_loft", "point_grid", "cv_grid", "rail_sweep", "two_rail_sweep"):
        return (("section_ids",),)
    if kind == "uv_loft":
        return (("u_section_ids", "v_section_ids"),)
    return ()


def self_check(
    document: dict[str, Any],
    dimensions: dict[str, Any] | None,
    massing: dict[str, Any] | None,
    specs_dir: Path,
    allow_draft: bool,
) -> Checks:
    checks = Checks()
    sections = document.get("sections") if isinstance(document.get("sections"), list) else []
    surfaces = document.get("surfaces") if isinstance(document.get("surfaces"), list) else []
    derivatives = document.get("derivatives") if isinstance(document.get("derivatives"), list) else []
    points_by_id: dict[str, Any] = {}
    for entry in sections:
        if isinstance(entry, dict):
            points_by_id[str(entry.get("id"))] = entry.get("points_cm")

    # -- G-41 identity and naming ------------------------------------------- #
    section_ids = _ids(sections, SECTION_ID_RE, "G-41", "sections[]", checks)
    surface_ids = _ids(surfaces, SURFACE_ID_RE, "G-41", "surfaces[]", checks)
    derivative_ids = _ids(derivatives, DERIVATIVE_ID_RE, "G-41", "derivatives[]", checks)
    if not section_ids:
        checks.fail("G-41", "sections[] is empty; a surface needs rows to build from")
    names: dict[str, str] = {}
    for label, table in (("sections[]", sections), ("surfaces[]", surfaces), ("derivatives[]", derivatives)):
        for entry in table:
            if not isinstance(entry, dict):
                continue
            if "name" not in entry:
                continue
            value = entry.get("name")
            if not isinstance(value, str) or not value:
                checks.fail("G-41", f"{label} {entry.get('id')!r} has a name that is not a string")
                continue
            if "-" in value:
                checks.fail(
                    "G-41",
                    f"{label} {entry.get('id')!r} name {value!r} contains '-'; a hyphen in a "
                    "node name reads as subtraction in emitted MAXScript (11 rule N1)",
                )
            if value in names:
                checks.fail(
                    "G-41",
                    f"{label} {entry.get('id')!r} name {value!r} is already used by "
                    f"{names[value]}",
                )
            names[value] = f"{label} {entry.get('id')!r}"
    if not any(rule == "G-41" and status == "fail" for rule, status, _ in checks.rows):
        checks.pass_(
            "G-41",
            f"{len(sections)} sections, {len(surfaces)} surfaces, {len(derivatives)} derivatives: "
            "ids well formed, unique and ascending; every declared name unique and hyphen-free",
        )

    # -- G-42 section shape and rectangularity ----------------------------- #
    shape_problems = 0
    for entry in sections:
        ident = str(entry.get("id"))
        points = entry.get("points_cm")
        if not isinstance(points, list) or len(points) < 2:
            checks.fail("G-42", f"{ident} points_cm has {len(points or [])} entries; >= 2 required")
            shape_problems += 1
            continue
        for position, point in enumerate(points):
            if not is_point3(point):
                checks.fail(
                    "G-42",
                    f"{ident} points_cm[{position}] is not exactly three finite numbers: {point!r}",
                )
                shape_problems += 1
        for position in range(1, len(points)):
            if is_point3(points[position]) and points[position] == points[position - 1]:
                checks.fail(
                    "G-42",
                    f"{ident} repeats point {position - 1} as point {position}; a section row "
                    "has no duplicate consecutive point",
                )
                shape_problems += 1
    counts: dict[str, dict[int, list[str]]] = {}
    for surface in surfaces:
        kind = surface.get("kind")
        if kind not in SURFACE_KINDS:
            continue
        bucket = counts.setdefault(kind, {})
        for family in ref_families(kind):
            for key in family:
                for ref in surface.get(key) or []:
                    points = points_by_id.get(str(ref))
                    if not isinstance(points, list):
                        continue
                    bucket.setdefault(len(points), []).append(f"{surface.get('id')}->{ref}")
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        if kind not in SURFACE_KINDS:
            continue
        for family in ref_families(kind):
            refs = [ref for key in family for ref in (surface.get(key) or [])]
            sizes = {len(points_by_id[str(ref)]) for ref in refs if isinstance(points_by_id.get(str(ref)), list)}
            if len(sizes) > 1:
                checks.fail(
                    "G-42",
                    f"{ident} ({kind}) consumes sections with different point counts {sorted(sizes)}; "
                    "a lattice is rectangular and a loft family needs matching rows",
                )
                shape_problems += 1
    if shape_problems == 0:
        detail = "; ".join(
            f"{kind} rows of {sorted(bucket)} point(s)" for kind, bucket in counts.items()
        )
        checks.pass_(
            "G-42",
            f"{len(sections)} row(s) well formed, no duplicate consecutive point; "
            + (detail if detail else "no surface consumes a section"),
        )

    # -- G-43 kind fits its keys -------------------------------------------- #
    key_problems = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        if kind not in SURFACE_KINDS:
            checks.fail("G-43", f"{ident} kind {kind!r} is not in the vocabulary {SURFACE_KINDS}")
            key_problems += 1
            continue
        allowed = {"id", "name", "kind"} | set(SURFACE_COMMON_KEYS) | set(KIND_REQUIRED[kind]) | set(
            KIND_OPTIONAL[kind]
        )
        present = set(surface.keys())
        for key in sorted(present - allowed):
            checks.fail(
                "G-43",
                f"{ident} ({kind}) carries {key!r}, which 07 section 8.2.2 does not allow for "
                f"that kind (allowed: {sorted(allowed)})",
            )
            key_problems += 1
        for key in KIND_REQUIRED[kind]:
            if key not in surface:
                checks.fail("G-43", f"{ident} ({kind}) is missing the required key {key!r}")
                key_problems += 1
        layer = surface.get("layer")
        if layer is not None and layer not in SURFACE_LAYERS:
            checks.fail(
                "G-43",
                f"{ident} layer {layer!r} is not in {SURFACE_LAYERS}; a surface carries roof or "
                "facade geometry only (07 section 8.2.2)",
            )
            key_problems += 1
        mat_id = as_int(surface.get("mat_id", SURFACE_DEFAULTS["mat_id"]))
        if mat_id is None or mat_id < 1:
            checks.fail("G-43", f"{ident} mat_id {surface.get('mat_id')!r} is not an integer >= 1")
            key_problems += 1
        merge_tol = as_float(surface.get("merge_tol_cm", SURFACE_DEFAULTS["merge_tol_cm"]))
        if merge_tol is None or merge_tol < 0.0 or not math.isfinite(merge_tol):
            checks.fail("G-43", f"{ident} merge_tol_cm {surface.get('merge_tol_cm')!r} is not >= 0")
            key_problems += 1
        if surface.get("hide_curves") is not None and not isinstance(surface.get("hide_curves"), bool):
            checks.fail("G-43", f"{ident} hide_curves is not a bool")
            key_problems += 1
        if "closed_sections" in surface and not isinstance(surface.get("closed_sections"), bool):
            checks.fail("G-43", f"{ident} closed_sections is not a bool")
            key_problems += 1
        for key in ("u_order", "v_order"):
            if key in surface and as_int(surface.get(key)) is None:
                checks.fail("G-43", f"{ident} {key} {surface.get(key)!r} is not an integer")
                key_problems += 1
        weights = surface.get("weights")
        if weights is not None:
            if not isinstance(weights, list) or not all(as_float(w) is not None for w in weights):
                checks.fail("G-43", f"{ident} weights is not a flat array of numbers")
                key_problems += 1
            else:
                grid = surface.get("section_ids")
                if isinstance(grid, list) and len(grid) >= 1:
                    total = 0
                    for ref in grid:
                        points = points_by_id.get(str(ref))
                        total += len(points) if isinstance(points, list) else 0
                    if len(weights) > total:
                        checks.fail(
                            "G-43",
                            f"{ident} weights has {len(weights)} entries for a lattice of {total}; "
                            "weights is one flat row-major array (07 section 8.2.2)",
                        )
                        key_problems += 1
        approximation = surface.get("approximation")
        if approximation is not None:
            if not isinstance(approximation, dict):
                checks.fail("G-43", f"{ident} approximation is not an object")
                key_problems += 1
            else:
                for key in sorted(approximation):
                    if key not in APPROX_KEYS:
                        checks.fail(
                            "G-43",
                            f"{ident} approximation carries {key!r}, which 07 section 8.2.4 does "
                            f"not define (defined: {list(APPROX_KEYS)})",
                        )
                        key_problems += 1
                for key in ("view_steps_u", "view_steps_v"):
                    steps = as_int(approximation.get(key))
                    if key in approximation and (steps is None or steps < 1):
                        checks.fail(
                            "G-43",
                            f"{ident} approximation.{key} {approximation.get(key)!r} is not an "
                            "integer >= 1",
                        )
                        key_problems += 1
                for key in ("render_edge_pct", "render_angle_deg", "merge_tol_cm"):
                    if key in approximation:
                        value = as_float(approximation.get(key))
                        if value is None or not math.isfinite(value) or (key == "merge_tol_cm" and value < 0.0):
                            checks.fail(
                                "G-43",
                                f"{ident} approximation.{key} {approximation.get(key)!r} is outside "
                                "its 07 section 8.2.4 range",
                            )
                            key_problems += 1
    if key_problems == 0:
        checks.pass_(
            "G-43",
            f"{len(surfaces)} surfaces; every key fits its kind; layers in "
            f"{SURFACE_LAYERS}; mat_id >= 1; merge_tol_cm >= 0",
        )

    # -- G-44 references resolve, nothing is orphaned ---------------------- #
    ref_problems = 0
    consumed: set[str] = set()
    for surface in surfaces:
        ident = str(surface.get("id"))
        for key in ("section_ids", "u_section_ids", "v_section_ids", "rail_section_ids", "trim_section_ids"):
            refs = surface.get(key)
            if refs is None:
                continue
            if not isinstance(refs, list):
                checks.fail("G-44", f"{ident} {key} is not an array")
                ref_problems += 1
                continue
            for ref in refs:
                if str(ref) not in points_by_id:
                    checks.fail("G-44", f"{ident} {key} names {ref!r}, which is not a section id")
                    ref_problems += 1
                else:
                    consumed.add(str(ref))
        for key in ("parent1_ref", "parent2_ref", "surface_ref"):
            ref = surface.get(key)
            if ref is None:
                continue
            if str(ref) not in surface_ids:
                checks.fail(
                    "G-44",
                    f"{ident} {key} {ref!r} is not a surface id in this file",
                )
                ref_problems += 1
    for derivative in derivatives:
        ref = derivative.get("surface_ref")
        if str(ref) not in surface_ids:
            checks.fail(
                "G-44",
                f"{derivative.get('id')} surface_ref {ref!r} is not a surface id in this file",
            )
            ref_problems += 1
    for section_id in section_ids:
        if section_id not in consumed:
            checks.fail(
                "G-44",
                f"{section_id} is consumed by no surface; an unused section is a defect, not a "
                "spare (07 section 9.7)",
            )
            ref_problems += 1
    if ref_problems == 0:
        checks.pass_(
            "G-44",
            f"{len(consumed)} of {len(section_ids)} sections consumed, every reference resolves",
        )

    # -- G-45 kind-specific cardinality ------------------------------------ #
    card_problems = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        if kind not in SURFACE_KINDS:
            continue
        if kind == "u_loft":
            refs = list(surface.get("section_ids") or [])
            if len(refs) < 2:
                checks.fail("G-45", f"{ident} (u_loft) has {len(refs)} sections; >= 2 required")
                card_problems += 1
        elif kind == "uv_loft":
            u_refs = list(surface.get("u_section_ids") or [])
            v_refs = list(surface.get("v_section_ids") or [])
            if len(u_refs) < 1 or len(v_refs) < 1:
                checks.fail(
                    "G-45",
                    f"{ident} (uv_loft) has {len(u_refs)} U and {len(v_refs)} V sections; each "
                    "family needs >= 1",
                )
                card_problems += 1
            elif len(u_refs) == 1 and len(v_refs) == 1:
                checks.fail(
                    "G-45",
                    f"{ident} (uv_loft) has one curve in each family; a network needs 1 and n, "
                    "not 1 and 1",
                )
                card_problems += 1
        elif kind in ("point_grid", "cv_grid"):
            refs = list(surface.get("section_ids") or [])
            if len(refs) < 2:
                checks.fail(
                    "G-45", f"{ident} ({kind}) has {len(refs)} rows; a lattice needs >= 2"
                )
                card_problems += 1
            for ref in refs:
                points = points_by_id.get(str(ref))
                if isinstance(points, list) and len(points) < 2:
                    checks.fail(
                        "G-45",
                        f"{ident} ({kind}) row {ref} has {len(points)} point(s); a lattice row "
                        "needs >= 2",
                    )
                    card_problems += 1
    if card_problems == 0:
        checks.pass_("G-45", f"{len(surfaces)} surfaces satisfy their kind's cardinality")

    # -- G-46 order is meaningful, not clamped away ------------------------ #
    order_problems = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        if surface.get("kind") != "cv_grid":
            continue
        refs = list(surface.get("section_ids") or [])
        rows = len(refs)
        columns = max(
            [len(points_by_id[str(ref)]) for ref in refs if isinstance(points_by_id.get(str(ref)), list)]
            or [0]
        )
        for key, limit in (("u_order", columns), ("v_order", rows)):
            if key not in surface:
                continue
            value = as_int(surface.get(key))
            if value is None or not MIN_ORDER <= value <= MAX_ORDER:
                checks.fail(
                    "G-46",
                    f"{ident} {key} {surface.get(key)!r} is not an integer in {MIN_ORDER}..{MAX_ORDER}",
                )
                order_problems += 1
            elif value > limit:
                checks.fail(
                    "G-46",
                    f"{ident} {key} {value} exceeds the {limit} it applies to "
                    f"({'points per row' if key == 'u_order' else 'rows'}); the library clamps "
                    "with amin, so the build would differ from the spec",
                )
                order_problems += 1
    if order_problems == 0:
        checks.pass_(
            "G-46",
            "no cv_grid order is outside 2..5 or larger than the count it applies to"
            if any(s.get("kind") == "cv_grid" for s in surfaces)
            else "no cv_grid surface declares an order",
        )

    # -- G-47 thickness is meaningful --------------------------------------- #
    thickness_problems = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        if "thickness_cm" not in surface:
            continue
        value = as_float(surface.get("thickness_cm"))
        if value is None or not math.isfinite(value):
            checks.fail("G-47", f"{ident} thickness_cm {surface.get('thickness_cm')!r} is not a number")
            thickness_problems += 1
        elif surface.get("kind") == "u_loft" and abs(value) < MIN_SHELL_THICKNESS_CM:
            checks.fail(
                "G-47",
                f"{ident} thickness_cm {surface.get('thickness_cm')!r} is under "
                f"{MIN_SHELL_THICKNESS_CM}; createULoftShell omits the offset surface below that, "
                "so the shell would silently not exist",
            )
            thickness_problems += 1
    for derivative in derivatives:
        if "thickness_cm" not in derivative:
            continue
        value = as_float(derivative.get("thickness_cm"))
        if value is None or not math.isfinite(value) or value < 0.0:
            checks.fail(
                "G-47",
                f"{derivative.get('id')} thickness_cm {derivative.get('thickness_cm')!r} is not "
                "a number >= 0",
            )
            thickness_problems += 1
    if thickness_problems == 0:
        shells = [s for s in surfaces if "thickness_cm" in s]
        checks.pass_(
            "G-47",
            f"{len(shells)} shell thickness(es), all |t| >= {MIN_SHELL_THICKNESS_CM} cm; "
            "derivative thickness >= 0",
        )

    # -- G-48 derivative fitness -------------------------------------------- #
    derivative_problems = 0
    for derivative in derivatives:
        ident = str(derivative.get("id"))
        kind = derivative.get("kind")
        if kind not in DERIVATIVE_KINDS:
            checks.fail(
                "G-48", f"{ident} kind {kind!r} is not in {DERIVATIVE_KINDS}"
            )
            derivative_problems += 1
            continue
        for key in ("divisions_u", "divisions_v"):
            value = as_int(derivative.get(key))
            if value is None or value < 1:
                checks.fail(
                    "G-48",
                    f"{ident} {key} {derivative.get(key)!r} is not an integer >= 1; a count is "
                    "compared exactly (07 section 9.5)",
                )
                derivative_problems += 1
        if kind == "space_frame":
            sub_steps = as_int(derivative.get("sub_steps", DERIVATIVE_DEFAULTS["sub_steps"]))
            if sub_steps is None or sub_steps < 1:
                checks.fail(
                    "G-48", f"{ident} sub_steps {derivative.get('sub_steps')!r} is not an integer >= 1"
                )
                derivative_problems += 1
            as_float_ok = as_float(derivative.get("thickness_cm", DERIVATIVE_DEFAULTS["thickness_cm"]))
            if as_float_ok is None:
                checks.fail("G-48", f"{ident} thickness_cm is not a number")
                derivative_problems += 1
        else:
            if "sub_steps" in derivative:
                checks.fail(
                    "G-48",
                    f"{ident} ({kind}) carries sub_steps; 07 section 8.2.5 makes that key "
                    "space_frame only",
                )
                derivative_problems += 1
            if "thickness_cm" in derivative:
                checks.fail(
                    "G-48",
                    f"{ident} ({kind}) carries thickness_cm; 07 section 8.2.5 makes that key "
                    "space_frame only",
                )
                derivative_problems += 1
        layer = derivative.get("layer")
        if layer is not None and layer not in DERIVATIVE_LAYERS:
            checks.fail(
                "G-43",
                f"{ident} layer {layer!r} is not in {DERIVATIVE_LAYERS} (07 section 8.2.5)",
            )
            derivative_problems += 1
    if derivative_problems == 0:
        checks.pass_(
            "G-48",
            f"{len(derivatives)} derivative(s): kinds in {DERIVATIVE_KINDS}, divisions >= 1, "
            "space_frame-only keys only on space_frame",
        )

    # -- G-49 provenance ---------------------------------------------------- #
    origins = document.get("origins") if isinstance(document.get("origins"), dict) else {}
    leaves = collect_leaves(document)
    provenance_problems = 0
    for entry in sorted(origins):
        found, _ = resolve(document, entry)
        if not found:
            checks.fail("G-49", f"origins entry {entry} does not resolve in {OUT_JSON_NAME}")
            provenance_problems += 1
            continue
        record = origins[entry]
        if not isinstance(record, dict):
            checks.fail("G-49", f"origins entry {entry} is not an object")
            provenance_problems += 1
            continue
        if record.get("origin") != "derived":
            checks.fail(
                "G-49",
                f"{entry} has origin {record.get('origin')!r}; every nurbs origin is derived, "
                "because dimensions.json and massing.json already resolved given/assumed/conflict",
            )
            provenance_problems += 1
        derives_from = record.get("derives_from")
        if not isinstance(derives_from, list) or not derives_from:
            checks.fail("G-49", f"{entry} has no non-empty derives_from")
            provenance_problems += 1
    leaf_set = set(leaves)
    for leaf in leaves:
        holders = [entry for entry in origins if covers(entry, leaf)]
        if not holders:
            checks.fail("G-49", f"leaf {leaf} has no origins entry")
            provenance_problems += 1
        elif len(holders) > 1:
            checks.fail("G-49", f"leaf {leaf} is covered by {holders}")
            provenance_problems += 1
    for entry in origins:
        if entry not in leaf_set and not any(covers(entry, leaf) for leaf in leaf_set):
            checks.fail("G-49", f"origins entry {entry} covers no leaf")
            provenance_problems += 1
    hosts: list[tuple[str, dict[str, Any]]] = [("dimensions.json", dimensions), ("massing.json", massing)]
    hosts = [(name, doc) for name, doc in hosts if isinstance(doc, dict)]
    absent = [name for name, value in (("dimensions.json", dimensions), ("massing.json", massing)) if not isinstance(value, dict)]
    unresolved = 0
    traced = 0
    for entry in sorted(origins):
        record = origins.get(entry)
        if not isinstance(record, dict):
            continue
        for path in record.get("derives_from") or []:
            if resolve(document, str(path))[0] or any(
                resolve(doc, str(path))[0] for _, doc in hosts
            ):
                traced += 1
            else:
                unresolved += 1
                if not absent:
                    checks.fail(
                        "G-49",
                        f"{entry} derives_from {str(path)!r} resolves in neither {OUT_JSON_NAME}, "
                        "dimensions.json nor massing.json",
                    )
    unresolved_inputs = 0
    checked_inputs = 0
    for item in document.get("origin_inputs") or []:
        text = str(item)
        if any(resolve(doc, text)[0] for _, doc in hosts):
            checked_inputs += 1
        else:
            unresolved_inputs += 1
            if not absent:
                checks.fail(
                    "G-49",
                    f"origin_inputs path {text!r} resolves in neither dimensions.json nor "
                    "massing.json",
                )
    if provenance_problems == 0 and absent:
        checks.skip(
            "G-49",
            f"coverage and all-derived provenance hold ({len(leaves)} leaves, {len(origins)} "
            f"entries), but cross-file provenance is unproven: {', '.join(absent)} absent from "
            f"{specs_dir}, so {unresolved} derives_from and {unresolved_inputs} origin_inputs "
            "paths could not be resolved. A check that cannot be evaluated reports SKIP with "
            "its reason, never a silent PASS.",
        )
    elif provenance_problems == 0:
        checks.pass_(
            "G-49",
            f"{len(leaves)} leaves covered exactly once by {len(origins)} entries, all derived, "
            f"{traced} derives_from paths and {checked_inputs} origin_inputs paths resolve",
        )

    # -- G-50 relation arity, and a parent that can be rebuilt -------------- #
    # `seen_kinds` is the surface table as it is walked, i.e. only surfaces
    # DECLARED EARLIER. A relation names an earlier surface (G-52), which is why
    # the emitted script can bind the parent's sub-object index as it builds.
    seen_kinds: dict[str, str] = {}
    arity_problems = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        if kind not in DEPENDENT_KINDS:
            seen_kinds[ident] = str(kind)
            continue
        if kind in RAIL_SWEEP_KINDS:
            wanted = 1 if kind == "rail_sweep" else 2
            rails = surface.get("rail_section_ids")
            rails = rails if isinstance(rails, list) else []
            if len(rails) != wanted:
                checks.fail(
                    "G-50",
                    f"{ident} ({kind}) declares {len(rails)} rail(s) in rail_section_ids; "
                    f"{kind} is a sweep along exactly {wanted} rail(s), and each rail is a "
                    "SEC-nnn polyline",
                )
                arity_problems += 1
            cross = surface.get("section_ids")
            cross = cross if isinstance(cross, list) else []
            if len(cross) < 2:
                checks.fail(
                    "G-50",
                    f"{ident} ({kind}) declares {len(cross)} cross-section(s); a rail sweep "
                    "needs >= 2, because one curve sweeps to a ruled band and nothing else",
                )
                arity_problems += 1
        elif kind == "blend":
            for key in ("parent1_ref", "edge1", "parent2_ref", "edge2"):
                if key not in surface:
                    checks.fail(
                        "G-50",
                        f"{ident} (blend) is missing {key!r}; a blend is a transition between "
                        "TWO surface edges and needs both parents and both edge numbers",
                    )
                    arity_problems += 1
        elif kind == "trim":
            if "surface_ref" not in surface:
                checks.fail(
                    "G-50", f"{ident} (trim) is missing 'surface_ref'; there is nothing to project onto"
                )
                arity_problems += 1
            profiles = surface.get("trim_section_ids")
            profiles = profiles if isinstance(profiles, list) else []
            if not profiles:
                checks.fail(
                    "G-50",
                    f"{ident} (trim) declares {len(profiles)} profile(s) in trim_section_ids; a "
                    "projection needs >= 1 closed profile",
                )
                arity_problems += 1
            for ref in profiles:
                points = points_by_id.get(str(ref))
                if not isinstance(points, list) or len(points) < 3:
                    checks.fail(
                        "G-50",
                        f"{ident} (trim) profile {ref} needs >= 3 points; a closed profile with "
                        "fewer cannot enclose an area to project",
                    )
                    arity_problems += 1
                elif list(points[0]) == list(points[-1]):
                    checks.fail(
                        "G-50",
                        f"{ident} (trim) profile {ref} repeats its first point as its last, and "
                        "the builder passes closed:true, which NURBSPointCurve honours "
                        "natively; the seam would be written twice, giving the projected "
                        "curve a zero-length segment",
                    )
                    arity_problems += 1
        for key in ("parent1_ref", "parent2_ref", "surface_ref"):
            ref = surface.get(key)
            if not isinstance(ref, str) or ref not in seen_kinds:
                continue  # a missing id is G-43's; a later id is G-52's
            parent_kind = seen_kinds[ref]
            if parent_kind not in RELATION_PARENT_KINDS:
                checks.fail(
                    "G-50",
                    f"{ident} {key} names {ref}, whose kind is {parent_kind!r}. A relation names "
                    f"its parent by the `nurbsID` the parent hands over once its own node is "
                    f"committed (D3), so the parent must be a kind that commits at least one "
                    f"NURBSSurface -- {list(RELATION_PARENT_KINDS)}. A `trim` parent commits "
                    "none (D5), so it has no id to bind and the slot would have to be filled "
                    "with a synthetic pointer, which crashes Max (D4, G-56).",
                )
                arity_problems += 1
        seen_kinds[ident] = str(kind)
    if arity_problems == 0:
        relations = [s for s in surfaces if s.get("kind") in DEPENDENT_KINDS]
        if relations:
            detail = ", ".join(f"{s.get('id')}={s.get('kind')}" for s in relations)
            checks.pass_(
                "G-50",
                f"{len(relations)} relation surface(s) ({detail}): rail and cross-section counts "
                "exact, blend has two parents and two edges, trim has a surface and >= 1 closed "
                "profile, every parent a kind that commits a NURBSSurface to bind",
            )
        else:
            checks.pass_(
                "G-50",
                "no relation surface in this file; the four dependent kinds declare nothing to "
                "count, so their arity is vacuously exact",
            )

    # -- G-51 every cross-section must actually meet the rail --------------- #
    # Max drops a rail sweep whose sections never touch the rail, silently. This
    # is the pre-flight, and it is the only rule in this file that measures
    # geometry instead of reading a key.
    tolerance, tolerance_source = linear_tolerance(document, dimensions)
    sweeps = [s for s in surfaces if s.get("kind") in RAIL_SWEEP_KINDS]
    if not sweeps:
        checks.pass_(
            "G-51",
            "no rail_sweep / two_rail_sweep surface, so there is no cross-section that could "
            "miss its rail; the silent-drop failure this guards cannot occur in this file",
        )
    else:
        rail_problems = 0
        measured = 0
        for surface in sweeps:
            ident = str(surface.get("id"))
            rail_refs = [str(ref) for ref in (surface.get("rail_section_ids") or [])]
            cross_refs = [str(ref) for ref in (surface.get("section_ids") or [])]
            offenders: list[str] = []
            worst = (0.0, "", "")
            for cross in cross_refs:
                cross_points = points_by_id.get(cross)
                if not isinstance(cross_points, list):
                    continue
                measured += 1
                for rail in rail_refs:
                    rail_points = points_by_id.get(rail)
                    if not isinstance(rail_points, list):
                        continue
                    distance = polyline_distance(cross_points, rail_points)
                    if distance > tolerance + TOLERANCE_EPSILON:
                        offenders.append(f"{cross} misses {rail} by {q(distance)} cm")
                        if distance > worst[0]:
                            worst = (distance, cross, rail)
            if offenders:
                rail_problems += 1
                checks.fail(
                    "G-51",
                    f"{ident} ({surface.get('kind')}) has {len(offenders)} cross-section/rail "
                    f"pair(s) that never intersect; worst {worst[1]} misses {worst[2]} by "
                    f"{q(worst[0])} cm, against {q(tolerance)} cm from {tolerance_source}. 3ds Max "
                    "discards such a sweep at commit and reports nothing at all, so the build "
                    "would silently lose its rail.",
                )
        if rail_problems == 0:
            checks.pass_(
                "G-51",
                f"{measured} cross-section(s) across {len(sweeps)} rail sweep(s) each come "
                f"within {q(tolerance)} cm of every rail, measured point-to-segment against the "
                f"rail polyline ({tolerance_source})",
            )

    # -- G-52 a relation names a surface declared EARLIER, and an edge 1..4 --- #
    declared: dict[str, str] = {}
    relation_problems = 0
    edge_count = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        if kind not in DEPENDENT_KINDS:
            declared[ident] = str(kind)
            continue
        if kind == "blend":
            ref_keys = ("parent1_ref", "parent2_ref")
        elif kind == "trim":
            ref_keys = ("surface_ref",)
        else:
            ref_keys = ()
        for ref_key in ref_keys:
            ref = surface.get(ref_key)
            if isinstance(ref, str) and ref in declared:
                continue
            relation_problems += 1
            if not isinstance(ref, str):
                where = f"is {ref!r}, not a SUR-nnn id"
            elif ref == ident:
                where = (
                    f"is {ref!r}, which is this surface itself. A relation resolves against a "
                    "surface declared EARLIER; a surface cannot be its own parent, because the "
                    "emitted script has not created it when it would have to name it."
                )
            else:
                later = next(
                    (
                        f"surfaces[{index}]"
                        for index, other in enumerate(surfaces)
                        if str(other.get("id")) == ref
                    ),
                    "no entry at all",
                )
                where = (
                    f"is {ref!r}, which is declared LATER in {OUT_JSON_NAME} at {later}. The "
                    "emitted script creates nodes in document order and a NURBSSet index cannot "
                    "name a node that does not exist yet, so a relation must resolve against a "
                    "surface declared earlier"
                )
            checks.fail("G-52", f"{ident} ({kind}) {ref_key} {where}")
        for edge_key in ("edge1", "edge2"):
            if edge_key not in surface:
                continue
            edge_count += 1
            value = as_int(surface.get(edge_key))
            if value is None or not EDGE_MIN <= value <= EDGE_MAX:
                checks.fail(
                    "G-52",
                    f"{ident} (blend) {edge_key} {surface.get(edge_key)!r} is not an integer in "
                    f"{EDGE_MIN}..{EDGE_MAX}; the edges are low-U, high-U, low-V, high-V, and "
                    "Max reads the number positionally",
                )
                relation_problems += 1
        declared[ident] = str(kind)
    if relation_problems == 0:
        relations = [s for s in surfaces if s.get("kind") in DEPENDENT_KINDS]
        if relations:
            checks.pass_(
                "G-52",
                f"{len(relations)} relation surface(s): every parent resolves to a SUR-nnn "
                f"declared earlier in {OUT_JSON_NAME}, {edge_count} edge number(s) in "
                f"{EDGE_MIN}..{EDGE_MAX}",
            )
        else:
            checks.pass_(
                "G-52", "no blend and no trim, so there is no parent edge to resolve or range-check"
            )

    # -- G-53 the project vector, the seed and the flip are all real --------- #
    vector_problems = 0
    trims = [s for s in surfaces if s.get("kind") == "trim"]
    for surface in trims:
        ident = str(surface.get("id"))
        p_vec = surface.get("p_vec")
        if not is_point3(p_vec):
            checks.fail(
                "G-53",
                f"{ident} (trim) p_vec {p_vec!r} is not exactly three finite numbers",
            )
            vector_problems += 1
        elif all(float(value) == 0.0 for value in p_vec):
            checks.fail(
                "G-53",
                f"{ident} (trim) p_vec is the zero vector; a projection along nothing has no "
                "direction, and Max would take the profile wherever it happened to fall",
            )
            vector_problems += 1
        seed = surface.get("seed", list(SEED_DEFAULT))
        if (
            not isinstance(seed, list)
            or len(seed) != 2
            or any(as_float(value) is None or not math.isfinite(as_float(value)) for value in seed)
        ):
            checks.fail(
                "G-53",
                f"{ident} (trim) seed {seed!r} is not exactly two finite numbers; it is the "
                "[u,v] point on the parent the projection is seeded from",
            )
            vector_problems += 1
        flip_trim = surface.get("flip_trim", FLIP_TRIM_DEFAULT)
        if not isinstance(flip_trim, bool):
            checks.fail("G-53", f"{ident} (trim) flip_trim {flip_trim!r} is not a bool")
            vector_problems += 1
    if vector_problems == 0:
        if trims:
            checks.pass_(
                "G-53",
                f"{len(trims)} trim surface(s): p_vec is 3 numbers of non-zero magnitude, seed "
                f"is 2 numbers (default {list(SEED_DEFAULT)}), flip_trim is boolean "
                f"(default {str(FLIP_TRIM_DEFAULT).lower()})",
            )
        else:
            checks.pass_(
                "G-53",
                "no trim surface, so there is no p_vec, seed or flip_trim to range-check; "
                "NOTE pVec reads back with the OPPOSITE sign (CHECKPOINT P4b), so the builder "
                "asserts nothing about it after the commit",
            )

    # -- G-54 the emitted-surface census ------------------------------------- #
    # The count itself can only be read after NURBSNode, in 3ds Max, which is
    # where the check belongs; what is checkable here is that every dependent
    # node carries a census with the count this spec implies, and that the
    # implied count is a real number rather than a default. A `trim` implies 0
    # (D5) and 0 is a real expectation, so the refusal below is negative counts,
    # not zero counts.
    census_rows: list[str] = []
    census_problems = 0
    for surface in surfaces:
        if surface.get("kind") not in DEPENDENT_KINDS:
            continue
        ident = str(surface.get("id"))
        expected = expected_census(surface)
        if expected < 0:
            census_problems += 1
            checks.fail(
                "G-54",
                f"{ident} ({surface.get('kind')}) implies {expected} NURBSSurface sub-objects; "
                "the spec implies no count at all, so nothing can be compared after the commit",
            )
            continue
        census_rows.append(f"{ident}->{expected}")
    if census_problems == 0:
        if census_rows:
            checks.pass_(
                "G-54",
                f"{len(census_rows)} dependent node(s) carry a committed-surface census "
                f"({', '.join(census_rows)}). The count itself is read after NURBSNode in 3ds "
                "Max, where a mismatch throws a named error naming the node, the expected count "
                "and the actual count -- a static file cannot observe a commit, so the census "
                "runs at build time in the emitted .ms. A trim's 0 is an assertion, not an "
                "absence: `trim:false` must commit no surface at all (D5).",
            )
        else:
            checks.pass_(
                "G-54",
                "no dependent surface, and only a dependent surface can be dropped silently at "
                "commit, so this file's four lattice/loft nodes cannot lose a surface",
            )

    # -- G-55 blend tension is bounded ---------------------------------------- #
    # 1.0 is not a neutral default. D1 measured 295.64 cm of overshoot past the
    # parent at 1.0/1.0, and Max does not bound the overshoot above, so the range
    # is the schema's job, not Max's.
    tension_problems = 0
    tensions = 0
    for surface in surfaces:
        ident = str(surface.get("id"))
        for key in ("tension1", "tension2"):
            if key not in surface:
                continue
            tensions += 1
            value = as_float(surface.get(key))
            if value is None or not math.isfinite(value):
                checks.fail(
                    "G-55",
                    f"{ident} (blend) {key} {surface.get(key)!r} is not a finite number; the "
                    f"tension is a float in [{num(TENSION_MIN)},{num(TENSION_MAX)}]",
                )
                tension_problems += 1
            elif not TENSION_MIN <= value <= TENSION_MAX:
                checks.fail(
                    "G-55",
                    f"{ident} (blend) {key} {value!r} is outside "
                    f"[{num(TENSION_MIN)},{num(TENSION_MAX)}]. 0.0 is the straight transition "
                    "between the two selected edges; above 0 the blend is pushed outward past "
                    "both parents and the overshoot grows with the tension, unbounded by 3ds "
                    "Max (measured 295.64 cm past the parent at 1.0, and 50 cm below the "
                    "springing). Max accepts any value, so the schema is the only bound.",
                )
                tension_problems += 1
    if tension_problems == 0:
        blends = [s for s in surfaces if s.get("kind") == "blend"]
        if blends:
            checks.pass_(
                "G-55",
                f"{tensions} tension value(s) across {len(blends)} blend(s) are within "
                f"[{num(TENSION_MIN)},{num(TENSION_MAX)}]; an absent tension resolves to "
                f"{num(TENSION_DEFAULTS['tension1'])}, the straight transition (D1)",
            )
        else:
            checks.pass_(
                "G-55",
                "no blend surface, so there is no tension to range-check; an absent tension on "
                f"a blend would resolve to {num(TENSION_DEFAULTS['tension1'])}",
            )

    # -- G-56 a relation parent slot is bound, never a literal pointer -------- #
    # D4: `parent1ID:12345` is an EXCEPTION_ACCESS_VIOLATION -- a hard crash of
    # the Max process, not a MAXScript error, and nothing offline can catch it.
    # This rule prevents it by construction: every `*ID:` slot must name a local
    # that was bound from a committed sub-object, and a parent that has no
    # `nurbsID` to bind (a `trim`, census 0) is refused here rather than at run
    # time. `verify_script` enforces the same rule against the emitted bytes.
    pointer_problems = 0
    bound_parents: list[str] = []
    declared_order: dict[str, str] = {}
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        declared_order[ident] = str(kind)
        if kind not in DEPENDENT_KINDS:
            continue
        for key in ("parent1_ref", "parent2_ref", "surface_ref"):
            ref = surface.get(key)
            if not isinstance(ref, str) or ref not in declared_order:
                continue  # a missing id is G-43's; a later id is G-52's
            bound_parents.append(f"{ident}->{ref}")
            if expected_census({"kind": declared_order[ref]}) < 1:
                pointer_problems += 1
                checks.fail(
                    "G-56",
                    f"{ident} ({kind}) {key} names {ref}, whose kind is {declared_order[ref]!r} "
                    f"and whose committed node holds {expected_census({'kind': declared_order[ref]})} "
                    "NURBSSurface sub-object(s). The emitted `parent1ID:`/`parent2ID:` slot must "
                    "hold the `nurbsID` read from the parent's first committed NURBSSurface "
                    "(D3); a parent with no such surface has no id to bind, and a literal or "
                    "synthetic id in that slot crashes 3ds Max with EXCEPTION_ACCESS_VIOLATION "
                    "(D4). No offline check can catch that crash; refusing the parent here is "
                    "what prevents it.",
                )
    if pointer_problems == 0:
        if bound_parents:
            checks.pass_(
                "G-56",
                f"{len(bound_parents)} relation parent ref(s) ({', '.join(bound_parents)}) name a "
                "surface that commits at least one NURBSSurface, so each is bound by "
                "`local id_<node> = mcpNurbsSurfID <node> ...` and the emitted `parent1ID:`/"
                "`parent2ID:` slot carries a variable, never a literal (D3, D4); verified against "
                "the emitted bytes by verify_script",
            )
        else:
            checks.pass_(
                "G-56",
                "no relation names a parent in this file, so no `parent1ID:`/`parent2ID:` slot "
                "is emitted and there is no pointer that could be synthetic",
            )
    return checks


def section_literal(points: Any) -> str:
    rows = []
    for point in points:
        rows.append("[" + ",".join(num(value) for value in point) + "]")
    return "#(" + ",".join(rows) + ")"


def row_list(names: Sequence[str]) -> str:
    return "#(" + ",".join(names) + ")"


def tessellation_line(variable: str, settings: dict[str, Any]) -> str:
    approximation = settings["approximation"]
    return (
        f"MCP_NURBS_Arch.applyArchTessellation {variable} "
        f"hideCurves:{'true' if settings['hide_curves'] else 'false'} "
        f"mergeTol:{num(approximation['merge_tol_cm'])} "
        f"uSteps:{inum(approximation['view_steps_u'])} "
        f"vSteps:{inum(approximation['view_steps_v'])} "
        f"edgePct:{num(approximation['render_edge_pct'])} "
        f"angleDeg:{num(approximation['render_angle_deg'])}"
    )


def literal_bool(value: Any) -> str:
    return "true" if value else "false"


def number_array(values: Sequence[Any]) -> str:
    return "[" + ",".join(num(value) for value in values) + "]"


# --------------------------------------------------------------------------- #
# Emitters for the four dependent kinds
# --------------------------------------------------------------------------- #
#
# Everything here is flat statements inside the one function. No new library
# function is introduced, and no sub-object index is ever written as a literal:
# each is bound to a variable in the statement that appends it, because
# `appendObject` returns the string "OK" and the index is only knowable from
# `<set>.numObjects` afterwards (CHECKPOINT P4, bug 1).


def census_helper_lines() -> list[str]:
    """The G-54 census. Emitted only when a dependent surface exists."""
    return [
        "fn mcpNurbsCensus node label expected = (",
        "    -- G-54: an invalid dependent surface is DROPPED at commit with no error and no",
        "    -- warning, so a build that completes proves nothing. Count what the commit produced.",
        "    stopCreating",
        "    local rset = getNURBSSet node #relational",
        "    local found = 0",
        "    for i = 1 to rset.numObjects do (",
        "        local o = getObject rset i",
        "        if superClassOf o == NURBSSurface do ( found = found + 1 )",
        "    )",
        "    if found != expected do throw (\"build_nurbs G-54: node \" + label + \" committed \" + (found as string) + \" NURBSSurface sub-object(s) but the spec implies \" + (expected as string) + \"; 3ds Max drops an invalid dependent surface at commit without reporting it, so this build is not the geometry the spec asked for\")",
        "    found",
        ")",
    ]


def surf_id_helper_lines() -> list[str]:
    """Read the `nurbsID` a committed parent node hands to a relation (D3).

    A relation's parent does NOT have to live inside the relation's own
    `NURBSSet`: built as its own node, its surface hands over a `nurbsID` that the
    constructor takes through `parent1ID:` / `parent2ID:`, the relation set then
    holds only the relation (D3: "the relation set holds one sub-object"), and the
    parent keeps its own node -- so a derivative on that parent keeps working and
    a parent named by two relations is instantiated once instead of three times.

    The **first** `NURBSSurface` in the committed set is the design surface: a
    `thickness_cm > 0` appends its offset shell after it, which is P4's "read the
    first surface, never the last" rule. The id is never written as a literal --
    D4 measured `parent1ID:12345` as an `EXCEPTION_ACCESS_VIOLATION`, a hard
    crash of the Max process rather than a MAXScript error, so G-56 refuses one
    at build time instead.
    """
    return [
        "fn mcpNurbsSurfID node label = (",
        "    -- G-56 support: a `parent1ID:` / `parent2ID:` slot takes a live pointer, never a",
        "    -- literal. D4: a literal or synthetic id there is an EXCEPTION_ACCESS_VIOLATION,",
        "    -- a hard crash of the Max process, so the id is always read from a committed",
        "    -- sub-object. The FIRST NURBSSurface is the design surface; a thickness_cm > 0",
        "    -- appends its offset shell after it, so the last one would be the shell.",
        "    local rset = getNURBSSet node #relational",
        "    local found = undefined",
        "    for i = 1 to rset.numObjects do (",
        "        local o = getObject rset i",
        "        if superClassOf o == NURBSSurface do ( found = o.nurbsID; exit )",
        "    )",
        '    if found == undefined do throw ("build_nurbs: " + label + " carries no NURBSSurface sub-object, so it has no nurbsID for a relation parent to bind (G-56); a pointer cannot be invented")',
        "    found",
        ")",
    ]


def dependent_surface_lines(
    surface: dict[str, Any],
    variable: str,
    settings: dict[str, Any],
    section_variables: dict[str, str],
    parent_id_variables: dict[str, str],
) -> list[str]:
    """The whole node build for one of the four dependent kinds, as flat statements."""
    kind = surface.get("kind")
    set_variable = f"{variable}_Set"
    mat = inum(settings["mat_id"])
    lines = [f"local {set_variable} = NURBSSet()"]

    def append_curve(
        role: str, ref: Any, index: int, closed: bool, curve_local: str
    ) -> list[str]:
        section = section_variables[str(ref)]
        index_variable = f"{variable}_{role}{index}"
        return [
            f"local {index_variable} = 0",
            f"local {curve_local} = MCP_NURBS_Arch.makePointCurve {section} closed:{literal_bool(closed)}",
            f"appendObject {set_variable} {curve_local}",
            f"{index_variable} = {set_variable}.numObjects",
        ]

    if kind in RAIL_SWEEP_KINDS:
        rails = [str(ref) for ref in (surface.get("rail_section_ids") or [])]
        for index, ref in enumerate(rails, start=1):
            lines += append_curve("rail", ref, index, False, f"{variable}_pc{index}")
        cross_sections = [str(ref) for ref in (surface.get("section_ids") or [])]
        for index, ref in enumerate(cross_sections, start=1):
            lines += append_curve("sec", ref, index, False, f"{variable}_sc{index}")
        parallel = literal_bool(surface.get("parallel", PARALLEL_DEFAULT))
        # A rail is a CURVE that lives in this set, so `rail:` / `rail1:` / `rail2:`
        # stay in-set pre-commit ordinals -- verified working by the P4b live run.
        # Only the SURFACE parents moved to `*ID:` (D3).
        if kind == "rail_sweep":
            relation = (
                f"local {variable}_rel = NURBS1RailSweepSurface rail:{variable}_rail1 "
                f"parallel:{parallel} renderable:true generateUVs1:true matID:{mat}"
            )
        else:
            relation = (
                f"local {variable}_rel = NURBS2RailSweepSurface rail1:{variable}_rail1 "
                f"rail2:{variable}_rail2 parallel:{parallel} renderable:true generateUVs1:true "
                f"matID:{mat}"
            )
        lines.append(relation)
        for index in range(1, len(cross_sections) + 1):
            lines.append(f"appendCurve {variable}_rel {variable}_sec{index} flip:false")
    elif kind == "blend":
        parent1 = parent_id_variables[str(surface.get("parent1_ref"))]
        parent2 = parent_id_variables[str(surface.get("parent2_ref"))]
        lines.append(
            f"local {variable}_rel = NURBSBlendSurface parent1ID:{parent1} "
            f"edge1:{inum(surface.get('edge1'))} parent2ID:{parent2} "
            f"edge2:{inum(surface.get('edge2'))} "
            f"tension1:{num(surface.get('tension1', TENSION_DEFAULTS['tension1']))} "
            f"tension2:{num(surface.get('tension2', TENSION_DEFAULTS['tension2']))} "
            f"renderable:true generateUVs1:true matID:{mat}"
        )
    else:  # trim
        seed = surface.get("seed")
        seed = list(SEED_DEFAULT) if not isinstance(seed, list) else seed
        p_vec = number_array(surface.get("p_vec"))
        flip = literal_bool(surface.get("flip_trim", FLIP_TRIM_DEFAULT))
        parent1 = parent_id_variables[str(surface.get("surface_ref"))]
        for index, ref in enumerate([str(ref) for ref in (surface.get("trim_section_ids") or [])], start=1):
            section = section_variables[ref]
            index_variable = f"{variable}_profile{index}"
            # makePointCurve is F4, the one executed closed-profile path in this repo:
            # NURBSPointCurve closed:true numPoints:n + setPoint per point. D6 measured that
            # such a curve commits as points + curve and NO surface, so the profile costs
            # nothing in the G-54 census.
            lines += [
                f"local {index_variable} = 0",
                f"local {variable}_tr{index} = MCP_NURBS_Arch.makePointCurve {section} closed:true",
                f"appendObject {set_variable} {variable}_tr{index}",
                f"{index_variable} = {set_variable}.numObjects",
            ]
            # parent1ID is the SURFACE (bound from the parent's own node, D3); parent2 stays
            # the in-set pre-commit ordinal of the PROFILE CURVE, because the curve really is
            # in this set. Binding parent2 to the surface as well projects the surface onto
            # itself and silently yields no projected curve at all.
            # `trim:` is emitted FALSE on purpose (D5): trim:true does not cut, it adds an
            # untrimmed NURBSCVSurface COPY of the parent to this set.
            lines.append(
                f"local {variable}_rel{index} = NURBSProjectVectorCurve parent1ID:{parent1} "
                f"parent2:{index_variable} pVec:{p_vec} "
                f"seed:{number_array(seed)} trim:{literal_bool(TRIM_FLAG)} flipTrim:{flip}"
            )
            lines.append(f"appendObject {set_variable} {variable}_rel{index}")
    if kind != "trim":
        lines.append(f"appendObject {set_variable} {variable}_rel")
    lines.append(f"{set_variable}.merge = {num(settings['merge_tol_cm'])}")
    lines.append(f'local {variable} = NURBSNode {set_variable} name:"{variable}"')
    lines.append(
        f"MCP_NURBS_Arch.applyArchTessellation {variable} "
        f"hideCurves:{literal_bool(settings['hide_curves'])}"
    )
    return lines


def surf_id_line(variable: str) -> str:
    """The parent-ID binding, emitted the moment the parent's node is committed."""
    return f'local id_{variable} = mcpNurbsSurfID {variable} "{variable}"'


def census_line(variable: str, expected: int) -> str:
    return f'local census_{variable} = mcpNurbsCensus {variable} "{variable}" {inum(expected)}'


def render_ms(document: dict[str, Any], path_to_library: str) -> str:
    """Emit the whole build as one function, called once.

    The surface index handed to F9 and F10 is resolved by superclass at run time,
    never written as a literal: a ``point_grid`` of nU x nV contributes nU*nV
    ``NURBSPoint`` sub-objects before the surface (measured: a 5 x 3 lattice put
    it at index 16), and those counts are not knowable until the set is built.
    """
    project = document["project"]
    function = build_fn_name(project)
    sections = document.get("sections") or []
    surfaces = document.get("surfaces") or []
    derivatives = document.get("derivatives") or []

    surface_variables = [str(surface.get("name") or node_name(surface.get("id"))) for surface in surfaces]
    derivative_variables = [
        str(derivative.get("name") or node_name(derivative.get("id"))) for derivative in derivatives
    ]
    section_variables = {str(entry.get("id")): node_name(entry.get("id")) for entry in sections}

    #: A relation parent must be declared EARLIER (G-52) and must be a kind that
    #: commits at least one NURBSSurface (G-50/G-56), so the script can bind its
    #: `nurbsID` at the parent's own node and hand that variable to `parent1ID:`.
    #: A dangling or forward reference is refused by name here too, exactly as the
    #: self-check refuses it.
    #: ``parent_id_variables`` maps a parent SUR id to the local that holds its
    #: ``nurbsID``; ``parent_node_variables`` is the set of the NODE variables that
    #: must therefore carry a binding line, so the binding is emitted exactly once
    #: per parent node and immediately after that node is committed.
    declared: dict[str, dict[str, Any]] = {}
    parent_id_variables: dict[str, str] = {}
    for surface in surfaces:
        ident = str(surface.get("id"))
        kind = surface.get("kind")
        if kind in DEPENDENT_KINDS:
            for key in ("parent1_ref", "parent2_ref", "surface_ref"):
                ref = surface.get(key)
                if ref is None:
                    continue
                target = declared.get(str(ref))
                if target is None:
                    raise Refusal(
                        f"refusing to write {OUT_MS_NAME}: {ident} {key} names {ref!r}, which is "
                        "not a surface declared earlier in this file. A relation must resolve "
                        "against an earlier surface (G-52): the script creates nodes in document "
                        "order and reads the parent's nurbsID from the parent's own committed "
                        "node, which does not exist yet for a later surface."
                    )
                if target.get("kind") not in RELATION_PARENT_KINDS:
                    raise Refusal(
                        f"refusing to write {OUT_MS_NAME}: {ident} {key} names {ref!r}, whose "
                        f"kind is {target.get('kind')!r}. The relation names its parent by the "
                        f"`nurbsID` read from the parent's own committed node (D3), so the parent "
                        f"must be a kind that commits at least one NURBSSurface -- "
                        f"{list(RELATION_PARENT_KINDS)} (G-50). A parent with none would force a "
                        "literal into the parent slot, and a literal there crashes 3ds Max with "
                        "EXCEPTION_ACCESS_VIOLATION (D4, G-56)."
                    )
                parent_id_variables[str(ref)] = id_variable_for(
                    str(target.get("name") or node_name(target.get("id")))
                )
        declared[ident] = surface

    dependent_surfaces = [surface for surface in surfaces if surface.get("kind") in DEPENDENT_KINDS]
    parent_node_variables = {binding[len("id_"):] for binding in parent_id_variables.values()}

    body: list[str] = [
        f'if MCP_NURBS_Arch == undefined do ( fileIn "{path_to_library}" )',
        "fn mcpNurbsSurfIndex node label = (",
        "    local rset = getNURBSSet node #relational",
        "    local found = 0",
        "    for i = 1 to rset.numObjects do (",
        "        local o = getObject rset i",
        "        if superClassOf o == NURBSSurface do ( found = i; exit )",
        "    )",
        '    if found == 0 do throw ("build_nurbs: " + label + " carries no NURBSSurface sub-object; a surface index cannot be guessed")',
        "    found",
        ")",
    ]
    if dependent_surfaces:
        body += census_helper_lines()
    if parent_id_variables:
        body += surf_id_helper_lines()
    for variable in derivative_variables + surface_variables:
        body.append(f'local prev_{variable} = getNodeByName "{variable}"')
        body.append(f"if prev_{variable} != undefined do ( delete prev_{variable} )")
    for entry in sections:
        ident = str(entry.get("id"))
        body.append(f"local {section_variables[ident]} = {section_literal(entry.get('points_cm'))}")
    for surface, variable in zip(surfaces, surface_variables):
        kind = surface.get("kind")
        settings = surface_settings(surface)
        name_literal = f'name:"{variable}"'
        if kind == "u_loft":
            rows = [section_variables[str(ref)] for ref in surface.get("section_ids") or []]
            body.append(
                f"local {variable} = MCP_NURBS_Arch.createULoftShell {row_list(rows)} "
                f"{name_literal} thickness:{num(surface.get('thickness_cm', 0.0))} "
                f"closedSections:{'true' if surface.get('closed_sections') else 'false'} "
                f"hideCurves:{'true' if settings['hide_curves'] else 'false'}"
            )
        elif kind == "uv_loft":
            u_rows = [section_variables[str(ref)] for ref in surface.get("u_section_ids") or []]
            v_rows = [section_variables[str(ref)] for ref in surface.get("v_section_ids") or []]
            body.append(
                f"local {variable} = MCP_NURBS_Arch.createUVLoftNetwork {row_list(u_rows)} "
                f"{row_list(v_rows)} {name_literal} "
                f"hideCurves:{'true' if settings['hide_curves'] else 'false'}"
            )
        elif kind == "point_grid":
            rows = [section_variables[str(ref)] for ref in surface.get("section_ids") or []]
            body.append(
                f"local {variable} = MCP_NURBS_Arch.makePointSurfaceGrid {row_list(rows)} "
                f"{name_literal} matID:{inum(settings['mat_id'])} "
                f"hideCurves:{'true' if settings['hide_curves'] else 'false'} "
                f"mergeTol:{num(settings['merge_tol_cm'])}"
            )
        elif kind == "cv_grid":
            rows = [section_variables[str(ref)] for ref in surface.get("section_ids") or []]
            weights = surface.get("weights")
            weight_argument = (
                "weights:#(" + ",".join(num(value) for value in weights) + ") " if isinstance(weights, list) else ""
            )
            body.append(
                f"local {variable} = MCP_NURBS_Arch.makeCVSurfaceGrid {row_list(rows)} "
                f"{name_literal} uOrder:{inum(surface.get('u_order', 3))} "
                f"vOrder:{inum(surface.get('v_order', 3))} {weight_argument}"
                f"matID:{inum(settings['mat_id'])} "
                f"hideCurves:{'true' if settings['hide_curves'] else 'false'} "
                f"mergeTol:{num(settings['merge_tol_cm'])}"
            )
        elif kind in DEPENDENT_KINDS:
            body += dependent_surface_lines(surface, variable, settings, section_variables, parent_id_variables)
        else:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {surface.get('id')} kind {kind!r} is not in "
                f"{SURFACE_KINDS}; the self-check should have refused first."
            )
        if kind in ("u_loft", "uv_loft"):
            body.append(f"local set_{variable} = getNURBSSet {variable} #relational")
            body.append(f"set_{variable}.merge = {num(settings['merge_tol_cm'])}")
        body.append(tessellation_line(variable, settings))
        if kind in DEPENDENT_KINDS:
            body.append(census_line(variable, expected_census(surface)))
        if variable in parent_node_variables:
            # D3: bind the parent's pointer the moment its node is committed, so a relation
            # later in the file reads a live id and never re-instantiates the parent.
            body.append(surf_id_line(variable))

    resolved_indices: set[str] = set()
    for derivative, variable in zip(derivatives, derivative_variables):
        surface_id = str(derivative.get("surface_ref"))
        surface_variable = next(
            (str(surface.get("name") or node_name(surface.get("id"))) for surface in surfaces if str(surface.get("id")) == surface_id),
            None,
        )
        if surface_variable is None:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {derivative.get('id')} surface_ref "
                f"{surface_id!r} is not a surface in this file; the self-check should have "
                "refused first."
            )
        index_variable = f"idx_{surface_variable}"
        if index_variable not in resolved_indices:
            resolved_indices.add(index_variable)
            body.append(f'local {index_variable} = mcpNurbsSurfIndex {surface_variable} "{surface_variable}"')
        u_divisions = inum(derivative.get("divisions_u"))
        v_divisions = inum(derivative.get("divisions_v"))
        if derivative.get("kind") == "quad_panels":
            body.append(
                f"local {variable} = MCP_NURBS_Arch.sampleSurfaceToQuadPoly {surface_variable} "
                f"{index_variable} {u_divisions} {v_divisions} name:\"{variable}\""
            )
        else:
            body.append(
                f"local {variable} = MCP_NURBS_Arch.createDiagridOnSurface {surface_variable} "
                f"{index_variable} {u_divisions} {v_divisions} "
                f"thickness:{num(derivative_settings(derivative)['thickness_cm'])} "
                f"subSteps:{inum(derivative_settings(derivative)['sub_steps'])} name:\"{variable}\""
            )
        body.append(f'{variable}.name = "{variable}"')
    body.append("true")

    lines = [f"/* build_nurbs.py | project {project} | DO NOT EDIT */"]
    lines.append(f"fn {function} = (")
    lines.extend(f"    {line}" for line in body)
    lines.append(")")
    lines.append(f"{function}()")
    return "\n".join(lines) + "\n"


def verify_script(document: dict[str, Any], script: str, path_to_library: str) -> None:
    """The emitted script must build every node the spec declares.

    A spec value with no node is a hole nobody would notice until the scene was
    read back, so the script is checked against the document rather than trusted.
    """
    function = build_fn_name(document["project"])
    surfaces = document.get("surfaces") or []
    derivatives = document.get("derivatives") or []
    surface_variables = [str(surface.get("name") or node_name(surface.get("id"))) for surface in surfaces]
    derivative_variables = [
        str(derivative.get("name") or node_name(derivative.get("id"))) for derivative in derivatives
    ]
    for variable in surface_variables + derivative_variables:
        if f"local {variable} = " not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: no node is created for {variable}. Every "
                "surface and every derivative must exist in the scene."
            )
        if f'local prev_{variable} = getNodeByName "{variable}"' not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {variable} has no explicit-local delete "
                "guard, so a second fileIn would duplicate it."
            )
        if f"if prev_{variable} != undefined do ( delete prev_{variable} )" not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {variable} is looked up but never deleted, "
                "so a second fileIn would duplicate it."
            )

    if script.count("fn mcpNurbsSurfIndex node label = (") != 1:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: exactly one shared surface-index helper must be "
            "emitted, and it must be found once."
        )
    if "superClassOf o == NURBSSurface" not in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: the surface-index helper must resolve by "
            "superClassOf o == NURBSSurface; sub-object indices are not knowable until the "
            "NURBSSet is built."
        )
    if "if found == 0 do throw" not in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: the surface-index helper must throw a named "
            "error when the node carries no NURBSSurface."
        )
    for line in script.split("\n"):
        stripped = line.strip()
        for call in ("sampleSurfaceToQuadPoly", "createDiagridOnSurface"):
            if call not in stripped:
                continue
            tokens = stripped.split()
            position = next(
                index for index, token in enumerate(tokens) if token.split(".")[-1] == call
            )
            index_slot = tokens[position + 2] if len(tokens) > position + 2 else ""
            if not NODE_NAME_RE.match(index_slot):
                raise Refusal(
                    f"refusing to write {OUT_MS_NAME}: {call} receives the surface index "
                    f"positionally, and {index_slot!r} is not a resolved local. A literal index "
                    "would be wrong for a point_grid (nU*nV + 1) and for a loft with an offset "
                    "shell."
                )
        if "makePointSurfaceGrid" in stripped or "makeCVSurfaceGrid" in stripped:
            for keyword in ("uOrder:", "vOrder:"):
                if keyword in stripped and not re.search(rf"{keyword}\d+ ", stripped):
                    raise Refusal(
                        f"refusing to write {OUT_MS_NAME}: {stripped!r} has an order that is not "
                        "an integer literal; an order drives knot spans and must not arrive as "
                        "a float."
                    )

    for surface, variable in zip(surfaces, surface_variables):
        expected = tessellation_line(variable, surface_settings(surface))
        if expected not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {variable} has no line carrying its "
                f"approximation block ({expected}). The library functions forward only "
                "hideCurves, so the tessellation must be applied explicitly."
            )
        kind = surface.get("kind")
        if kind not in DEPENDENT_KINDS:
            continue
        census = census_line(variable, expected_census(surface))
        if census not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {variable} ({kind}) has no committed-surface "
                f"census ({census}). 3ds Max drops an invalid dependent surface at commit with "
                "no error and no warning, so a build without G-54 cannot tell a resolved relation "
                "from a lost one."
            )

    dependent = [s for s in surfaces if s.get("kind") in DEPENDENT_KINDS]
    if dependent and script.count("fn mcpNurbsCensus node label expected = (") != 1:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: {len(dependent)} dependent surface(s) exist, so "
            "exactly one G-54 census helper must be emitted, and it must be found once."
        )
    if dependent and "if found != expected do throw" not in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: the G-54 census helper must compare the counted "
            "surfaces against the expected number and throw a named error. A census that counts "
            "without comparing is a comment, not a check, and the silent drop it guards is "
            "invisible."
        )
    # One superclass test per helper that has to find a surface in a committed set:
    # the shared index helper (always), the census (dependent nodes) and the parent-id
    # helper (a relation parent). Counting by literal position would count the wrong objects.
    expected_superclass_tests = 1 + (1 if dependent else 0)
    if any(s.get("kind") in DEPENDENT_KINDS for s in surfaces) and any(
        s.get(key) is not None for s in surfaces for key in ("parent1_ref", "parent2_ref", "surface_ref")
    ):
        expected_superclass_tests += 1
    if script.count("superClassOf o == NURBSSurface") != expected_superclass_tests:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: the emitted script uses the superclass test "
            f"{script.count('superClassOf o == NURBSSurface')} time(s) where exactly "
            f"{expected_superclass_tests} helper(s) need it (index / census / parent-id). "
            "Sub-object indices are not knowable before the set is built, so a census that "
            "counts by literal position would count the wrong objects."
        )
    for kind, marker in (
        ("rail_sweep", "NURBS1RailSweepSurface rail:"),
        ("two_rail_sweep", "NURBS2RailSweepSurface rail1:"),
        ("blend", "NURBSBlendSurface parent1ID:"),
        ("trim", "NURBSProjectVectorCurve parent1ID:"),
    ):
        if any(s.get("kind") == kind for s in surfaces) and marker not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: a {kind} surface is declared, so the script "
                f"must construct its class with {marker!r}. The constructor accepts any keyword "
                "and silently swallows an unknown one, so a successful construction proves "
                "nothing about what was emitted."
            )

    # -- G-56, against the emitted bytes ------------------------------------- #
    # A relation parent slot takes a LIVE pointer. D4 measured three outcomes for the
    # same keyword: a string literal is a clean type error, a value read from a committed
    # sub-object commits and evaluates, and a synthetic number is
    # EXCEPTION_ACCESS_VIOLATION -- a hard crash of the 3ds Max process, not a
    # MAXScript error, and not recoverable from inside the script. Nothing offline
    # can observe a crash, so the rule is enforced by construction on the bytes.
    emitted_id_bindings = set(re.findall(r"local\s+(id_[A-Za-z][A-Za-z0-9_]*)\s*=\s*mcpNurbsSurfID", script))
    pointer_slots = 0
    for line in script.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue  # a MAXScript comment quotes the keyword; it does not pass one
        for keyword in ("parent1ID:", "parent2ID:"):
            for match in re.finditer(rf"\b{keyword}(\S*)", stripped):
                token = match.group(1)
                pointer_slots += 1
                if not NODE_NAME_RE.match(token):
                    raise Refusal(
                        f"refusing to write {OUT_MS_NAME}: {keyword} receives {token!r}, which is "
                        "not an identifier. A `nurbsID` is a POINTER: D4 measured "
                        "`parent1ID:12345` as an EXCEPTION_ACCESS_VIOLATION, a hard crash of the "
                        "3ds Max process that no offline check can catch afterwards (G-56). Bind "
                        "it with `local id_<parent> = mcpNurbsSurfID <parent> \"<parent>\"`."
                    )
                if token not in emitted_id_bindings:
                    raise Refusal(
                        f"refusing to write {OUT_MS_NAME}: {keyword} receives {token!r}, which is "
                        "not bound by mcpNurbsSurfID anywhere in this script. A relation parent "
                        "must be read from a committed sub-object; a name invented here would be "
                        "a synthetic pointer, and D4 measured that as an "
                        "EXCEPTION_ACCESS_VIOLATION in 3ds Max (G-56)."
                    )
    needs_id_helper = bool(
        [s for s in surfaces if s.get("kind") in DEPENDENT_KINDS]
    ) and bool(
        [
            s
            for s in surfaces
            if s.get("kind") in DEPENDENT_KINDS
            and any(s.get(key) is not None for key in ("parent1_ref", "parent2_ref", "surface_ref"))
        ]
    )
    if needs_id_helper and script.count("fn mcpNurbsSurfID node label = (") != 1:
        raise Refusal(
            "refusing to write {OUT_MS_NAME}: a relation names a parent by nurbsID (D3), so "
            "exactly one parent-id helper must be emitted, and it must be found once. Without "
            "it the parent would have to be re-instantiated inside the relation's own set, "
            "which is the duplication G-56's binding replaces."
        )
    if pointer_slots and "if found == undefined do throw" not in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: {pointer_slots} relation parent slot(s) are bound "
            "by variable, so the parent-id helper must throw a named error when the node carries "
            "no NURBSSurface. A helper that returned undefined would put undefined into a "
            "pointer slot, which is the crash D4 measured."
        )

    # No literal sub-object index may reach any of the relational constructors.
    # The counts are not knowable before the set is built: a point_grid contributes
    # nU*nV NURBSPoint sub-objects before its surface (measured: 5 x 3 -> index 16),
    # a shelled u_loft appends its offset after the base (measured: 51 and 52), and a
    # dependent surface's own position depends on how many parents precede it.
    for line in script.split("\n"):
        stripped = line.strip()
        for keyword in ("rail:", "rail1:", "rail2:", "parent1:", "parent2:"):
            for match in re.finditer(rf"\b{keyword}(\S*)", stripped):
                token = match.group(1)
                if not NODE_NAME_RE.match(token):
                    raise Refusal(
                        f"refusing to write {OUT_MS_NAME}: {keyword} receives {token!r}, which "
                        "is not a resolved local. appendObject returns the string \"OK\", so the "
                        "index is only knowable from <set>.numObjects read after the append; a "
                        "literal is wrong the moment a parent, an offset shell or another point "
                        "changes the count."
                    )

# Every local must be declared once per function: MAXScript rejects a
    # redefinition in the same scope, and the generated locals are derived from
    # node names, so two nodes differing only by a generated suffix would collide.
    # The emitted script nests helpers one level deep and never deeper, so the
    # innermost `fn` name is an exact scope key.
    declared_locals: dict[tuple[str, str], int] = {}
    scope = function
    for line in script.split("\n"):
        opening = re.match(r"^\s*fn\s+([A-Za-z][A-Za-z0-9_]*)\b", line)
        if opening:
            scope = opening.group(1)
            continue
        match = re.match(r"^\s*local\s+([A-Za-z][A-Za-z0-9_]*)\s*=", line)
        if match:
            key = (scope, match.group(1))
            declared_locals[key] = declared_locals.get(key, 0) + 1
    repeated = sorted(
        f"{name} in {owner}" for (owner, name), count in declared_locals.items() if count > 1
    )
    if repeated:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: {repeated} would be declared more than once in the "
            "same scope. MAXScript rejects a local redefinition, so two nodes whose names differ "
            "only by a generated suffix would fail at load, not at build."
        )

    if f'if MCP_NURBS_Arch == undefined do ( fileIn "{path_to_library}" )' not in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: the library must be fileIn-ed behind an "
            "already-loaded guard, or a second fileIn reloads it."
        )
    if "\\" in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: it contains a backslash; the library path must "
            "be emitted with forward slashes."
        )
    if "getCurrentException" in script or "catch {" in script or "try {" in script:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: it uses try/catch in a form MAXScript rejects "
            "(try ( ) catch ( ) is the only parenthesised form, and getCurrentException does "
            "not exist)."
        )
    emitted = set()
    for pattern in (r'\.name\s*=\s*"([^"]*)"', r"\bname\s*:\s*\"([^\"]*)\"", r'getNodeByName "([^"]*)"'):
        emitted.update(re.findall(pattern, script))
    expected_names = set(surface_variables) | set(derivative_variables)
    if not emitted:
        raise Refusal(f"refusing to write {OUT_MS_NAME}: it names no node at all.")
    for value in sorted(emitted):
        if value == path_to_library:
            continue
        if not NODE_NAME_RE.match(value):
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: name {value!r} is not MAXScript-"
                "identifier-safe. 11 rule N1 requires letters, digits and `_` only, and gives "
                "the mapping SUR-001 -> SUR_001."
            )
    named_nodes = {value for value in emitted if value != path_to_library}
    if named_nodes != expected_names:
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: the scene names it declares are "
            f"{sorted(named_nodes)}, but the spec declares {sorted(expected_names)}. Two nodes "
            "may not share one name, and no node may be invented."
        )
    forbidden = ("LayerManager", ".layer =", ".setLayer(", "setProperty #layer", "node.layer")
    for line in script.split("\n"):
        if any(token in line for token in forbidden):
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: it touches a layer ({line.strip()!r}). An "
                "object's layer cannot be assigned from MAXScript in Max 2026, so layer stays "
                "a data column (07 section 8.1.3) and P6 applies it."
            )
    verify_script_shape(document, script, function)


def verify_script_shape(document: dict[str, Any], script: str, function: str) -> None:
    """Structural test: the emitted file must be a runnable one-function script."""
    lines = script.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    header = f"/* build_nurbs.py | project {document['project']} | DO NOT EDIT */"

    def bad(reason: str) -> Refusal:
        return Refusal(
            f"refusing to write {OUT_MS_NAME}: {reason}. A local declaration at the top level "
            "of a fileIn-ed script is a compile error (verified 2026-10-04), so the whole body "
            "must live inside one fn that is called once."
        )

    if not lines or lines[0] != header:
        raise bad("it does not start with the header comment")
    fn_lines = [line for line in lines if line.startswith("fn ")]
    if len(fn_lines) != 1:
        raise bad(f"it holds {len(fn_lines)} top-level fn declarations, expected exactly one")
    if fn_lines[0] != f"fn {function} = (":
        raise bad(f"its fn declaration is {fn_lines[0]!r}, expected 'fn {function} = ('")
    if not NODE_NAME_RE.match(function):
        raise bad(f"its function name {function!r} is not MAXScript-identifier-safe")
    if lines[-1] != f"{function}()":
        raise bad(f"it ends with {lines[-1]!r}, expected the single call '{function}()'")
    if script.count(f"{function}()") != 1:
        raise bad(f"the function {function}() is called {script.count(f'{function}()')} times")
    body = lines[2:-2]
    if not body or body[-1].strip() != "true":
        raise bad("its function does not end with `true`, so a caller cannot assert on it")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("local ") and not line.startswith("    "):
            raise bad(f"it has a top-level `local`: {stripped!r}")
        if stripped and not line.startswith("    ") and line not in (
            header,
            f"fn {function} = (",
            ")",
            f"{function}()",
        ):
            raise bad(f"it has a top-level statement outside the fn: {stripped!r}")
    if lines[-2] != ")":
        raise bad("the fn body is not closed by a single ')' line before the call")
    if re.search(r"if\s*\(\s*getNodeByName", script):
        raise bad(
            "it uses the parenthesised one-liner delete guard `if (getNodeByName ...)`, which "
            "throws when the node does not exist; bind the lookup to a local first"
        )


def serialize(document: dict[str, Any]) -> str:
    try:
        body = json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False)
    except ValueError as exc:
        raise Refusal(
            f"refusing to write: {OUT_JSON_NAME} is not strict JSON -- {exc} (07 G-7)."
        ) from exc
    return body + "\n"


def write_bytes(path: Path, text: str) -> None:
    data = text.encode("utf-8")
    if b"\r" in data:
        raise Refusal(f"refusing to write {path}: the payload contains CR (07 G-7).")
    if not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise Refusal(f"refusing to write {path}: it must end with exactly one LF (07 G-7).")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def read_optional(specs_dir: Path, name: str) -> dict[str, Any] | None:
    path = specs_dir / name
    if not path.is_file():
        return None
    try:
        document = strict_loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return document if isinstance(document, dict) else None


def summarise(document: dict[str, Any], checks: Checks, path_to_library: str, json_path: Path, ms_path: Path, waived: bool) -> str:
    surfaces = document.get("surfaces") or []
    derivatives = document.get("derivatives") or []
    by_kind: dict[str, int] = {}
    for surface in surfaces:
        by_kind[surface.get("kind")] = by_kind.get(surface.get("kind"), 0) + 1
    lattice = []
    for surface in surfaces:
        if surface.get("kind") in ("point_grid", "cv_grid"):
            refs = [str(ref) for ref in surface.get("section_ids") or []]
            rows = len(refs)
            columns = 0
            for entry in document.get("sections") or []:
                if str(entry.get("id")) in refs and isinstance(entry.get("points_cm"), list):
                    columns = max(columns, len(entry["points_cm"]))
            lattice.append(f"{surface.get('id')} {rows}x{columns}")
    dependent = [s for s in surfaces if s.get("kind") in DEPENDENT_KINDS]
    census = ", ".join(
        f"{s.get('id')} expects {expected_census(s)}" for s in dependent
    )
    points = sum(len(entry.get("points_cm") or []) for entry in document.get("sections") or [])
    tally = checks.tally()
    lines = [
        "build_nurbs.py --stage nurbs",
        f"  project   {document['project']}  (read: {UPSTREAM_NAME}, status "
        f"{document.get('status')})",
        f"  sections  {len(document.get('sections') or [])} rows, {points} points",
        f"  surfaces  {len(surfaces)}  "
        + ", ".join(f"{kind} {by_kind[kind]}" for kind in SURFACE_KINDS if kind in by_kind)
        + (f"  lattices: {', '.join(lattice)}" if lattice else ""),
        f"  derivs    {len(derivatives)}  "
        + ", ".join(
            f"{kind} {sum(1 for d in derivatives if d.get('kind') == kind)}"
            for kind in DERIVATIVE_KINDS
            if any(d.get("kind") == kind for d in derivatives)
        ),
        f"  library   {path_to_library} (fileIn-ed only when MCP_NURBS_Arch is undefined)",
        f"  nodes     {len(surfaces)} surface + {len(derivatives)} derivative, each with an "
        "explicit-local delete guard; a surface, rail or parent index is resolved by superclass "
        "or bound to a variable, never written as a literal",
        "  G-54      "
        + str(len(dependent))
        + " dependent node(s) are censused in the emitted script after NURBSNode + stopCreating"
        + (
            ": " + census
            if census
            else " (none; only a dependent surface can be dropped silently at commit)"
        ),
        f"  layers    data only -- {OUT_MS_NAME} assigns no layer to any node (07 section 8.1.3)",
        f"  self-check G-41..G-56 {tally['pass']} pass, {tally['skip']} skip, {tally['fail']} fail",
    ]
    for skip in checks.skips():
        lines.append(f"    skip  {skip}")
    if waived:
        lines.append(f"  draft   --allow-draft waived the lock gate. {DRAFT_SKIP_REASON}")
    lines.append(f"  wrote    {json_path}")
    lines.append(f"  wrote    {ms_path}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build nurbs.json and nurbs.ms from a locked nurbs.json "
            "(07 section 8.2, invariants G-41..G-56)."
        )
    )
    parser.add_argument("--in", dest="in_dir", required=True, type=Path, help="specs directory to read")
    parser.add_argument("--out", dest="out_dir", default=None, type=Path, help="output directory (default: --in)")
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
        help="Draft work in progress: waive the lock gate. G-41..G-56 then run and fail, which is "
        "the point of the flag.",
    )
    args = parser.parse_args(argv)

    specs_dir: Path = args.in_dir
    out_dir: Path = args.out_dir if args.out_dir is not None else specs_dir
    path_to_library = library_path()

    try:
        document = normalise(load_spec(specs_dir, args.allow_draft))
        text = serialize(document)

        checked = strict_loads(text)
        dimensions = read_optional(specs_dir, "dimensions.json")
        massing = read_optional(specs_dir, "massing.json")
        checks = self_check(checked, dimensions, massing, specs_dir, args.allow_draft)
        missing_rules = [rule for rule in RULES if rule not in checks.by_rule()]
        if missing_rules:
            raise Refusal(
                f"refusing to write: the self-check produced no row for {missing_rules}. Every "
                "rule in 07 section 9.7 reports pass, skip or fail; silence is not a result."
            )
        failures = checks.failures()
        if failures:
            raise Refusal(
                "refusing to write: the self-check failed "
                f"{len(failures)} invariant(s).\n  - " + "\n  - ".join(failures[:20])
            )

        script = render_ms(checked, path_to_library)
        verify_script(checked, script, path_to_library)
        json_path = out_dir / OUT_JSON_NAME
        ms_path = out_dir / OUT_MS_NAME
        write_bytes(json_path, text)
        write_bytes(ms_path, script)
    except Refusal as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSAL

    surfaces = checked.get("surfaces") or []
    derivatives = checked.get("derivatives") or []
    by_kind: dict[str, int] = {}
    for surface in surfaces:
        by_kind[surface.get("kind")] = by_kind.get(surface.get("kind"), 0) + 1
    if args.as_json:
        summary = {
            "builder": "scripts/build_nurbs.py",
            "stage": "nurbs",
            "project": checked["project"],
            "spec": checked["spec"],
            "read": [str(specs_dir / UPSTREAM_NAME)],
            "wrote": [str(json_path), str(ms_path)],
            "section_count": len(checked.get("sections") or []),
            "point_count": sum(len(entry.get("points_cm") or []) for entry in checked.get("sections") or []),
            "surface_count": len(surfaces),
            "surface_ids": [surface["id"] for surface in surfaces],
            "surfaces_by_kind": {kind: by_kind[kind] for kind in SURFACE_KINDS if kind in by_kind},
            "derivative_count": len(derivatives),
            "derivative_ids": [derivative["id"] for derivative in derivatives],
            "node_names": [str(surface["name"]) for surface in surfaces]
            + [str(derivative["name"]) for derivative in derivatives],
            "library": path_to_library,
            "surface_index_strategy": "resolved by superClassOf o == NURBSSurface, first match (the design surface); no literal index is emitted for a surface, a rail or a parent",
            "dependent_surfaces": [
                {
                    "id": surface["id"],
                    "kind": surface["kind"],
                    "expected_nurbssurface_subobjects": expected_census(surface),
                }
                for surface in surfaces
                if surface.get("kind") in DEPENDENT_KINDS
            ],
            "emitted_surface_census": "G-54: every dependent node counts its NURBSSurface sub-objects after NURBSNode + stopCreating and throws a named error on a mismatch; the commit is observed in 3ds Max, not statically",
            "layer_application": "data only; nurbs.ms assigns no layer to any node",
            "origin_inputs": len(checked.get("origin_inputs") or []),
            "origins": len(checked.get("origins") or {}),
            "self_check": checks.by_rule(),
            "self_check_tally": checks.tally(),
            "self_check_skips": checks.skips(),
            "lock_gate": "waived by --allow-draft" if checked.get("status") != "locked" else "enforced",
            "exit_code": EXIT_OK,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(summarise(checked, checks, path_to_library, json_path, ms_path, checked.get("status") != "locked"))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())