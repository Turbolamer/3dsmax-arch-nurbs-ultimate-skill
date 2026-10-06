#!/usr/bin/env python3
"""Stage `massing`: locked dimensions.json -> massing.json + massing.ms.

The only stage implemented so far. It writes the two artefacts P3 owns, in the
shape `references/07-spec-grammar.md` section 8.1 defines and invariants
G-34..G-40 (section 9.6) accept:

    <out>/massing.json   the spec, strict JSON, UTF-8 no BOM, LF, one final newline
    <out>/massing.ms     geometry only -- no layer code (07 section 8.1.3)

Usage
-----
    python scripts/build_spec.py --stage massing --in <specs_dir> --out <out_dir> [--json]

Exit codes
----------
    0   built, and the self-check passed G-34..G-40 against the bytes on disk
    1   a refusal: the lock gate, a non-rectangular profile, an unsupported
        stage, or a self-check failure. The message names the file, the
        element id and the rule that fired.
    2   usage error

DETERMINISM (07 S-5)
--------------------
The same locked input must produce byte-identical output. Nothing here reads a
clock, a random source or an unordered container: every id is allocated in a
fixed order, every number goes through `q()` (rounded to 6 decimals, negative
zero normalised), `origins` is emitted in document order, and `origin_inputs`
is a sorted set. The only timestamp in either artefact is `source.recorded_at`,
copied verbatim from `dimensions.json` (07 section 3.2 allows exactly that one).

DECISIONS THIS BUILDER MAKES, AND WHY
-------------------------------------
* **Roof vertical model.** 07 section 5.9 is explicit and G-38 now agrees with
  it: `deck_level_cm` is the **top** of the build-up and `deck_thickness_cm`
  hangs below it. So a `roof_deck` is
  `[deck_level_cm - deck_thickness_cm, deck_level_cm]` and a `parapet` is
  `[deck_level_cm, deck_level_cm + parapet_height_cm]`, which makes the top of
  the model equal `building.overall_height_cm`. The self-check asserts that
  equality, so the old reading cannot come back unnoticed.

* **A parapet is four elements, not one.** 07 section 8.1.1: `profile_cm` must
  be a simple ring, so a ring with a hole is not expressible and a hollow shape
  is decomposed into one prism per straight side. A rectangular deck therefore
  gets four `parapet` prisms -- one band per side, each `parapet_thickness_cm`
  wide, their outer faces flush with the deck edge, in the ring's own CCW side
  order (south, east, north, west) so the ids are stable. The four bands
  partition the annulus between the deck outline and the outline inset by the
  parapet thickness: no overlap, no gap.

* **No plinth.** `dimensions.json` has no plinth dimension: nothing gives a
  plinth height, a plinth thickness or a plinth profile. Every candidate Z range
  either duplicates an element that already exists (the ground slab occupies the
  only band between `site.ground_level_cm` and `levels[0].elevation_cm`) or
  invents a number. `plinth` stays in the `kind` vocabulary, unused. Inventing a
  dimension is not this stage's job (`09-defaults.md` section 5,
  `agents/max-massing.md` section 6.4).

* **The ground pad's thickness is the ground slab's thickness.** No key in
  `dimensions.json` describes how thick a pad is, so `site_pad.ground_pad` uses
  `floor_plates[0].thickness_cm` -- a real dimension with a real provenance --
  rather than a literal of its own. `paving` and `kerb` stay `null`: 07 section
  8.1.1 says `kerb` is null until a later stage supplies one, and `dimensions`
  has no paving key either.

* **Columns that fall in the core are skipped.** The structural grid defines
  `column_x_cm x column_y_cm`; a column whose plan rectangle overlaps
  `core.footprint_cm` would stand inside the shaft, so it is not emitted and the
  skip is counted in the summary.

* **Node names are identifiers, not ids.** `references/11-layer-standard.md`
  section 3.1 rule N1: a generated node name is pasted into emitted MAXScript and
  into typed-tool arguments, and `-` reads as subtraction there, so the node name
  is the spec id with every dash replaced by an underscore -- `EL-001` becomes
  `EL_001`, `GRP-001` becomes `GRP_001`, `SP_GROUND_PAD` is already safe. One
  function (`node_name`) produces the MAXScript local, the `.name` /
  `Dummy name:` value and `grouping[].name`, so the three cannot disagree, and the
  self-check refuses any emitted name that is not `^[A-Za-z][A-Za-z0-9_]*$`.

* **The emitted script is one function.** Verified by execution on 2026-10-04: a
  `local` declaration at the top level of a `fileIn`-ed script is a *compile*
  error (`no local declarations at top level`). The whole body is therefore
  wrapped in `fn mcpMassingBuild_<project>`, indented one level, returning `true`
  and called exactly once.

* **Re-run policy: delete-then-create, by spec-derived name.** Every name the run
  creates comes from a spec id, so before creating anything the function deletes
  any node already holding that name -- payload first, then the dummies that
  parent it, because deleting a Dummy does not delete its children. A second
  `fileIn` therefore converges on the same scene as the first instead of
  accumulating duplicates, and layer creation stays guarded by `try`/`catch`.

* **The delete guard is written in explicit-local form.** Executed live on
  2026-10-04: `if (getNodeByName "X") != undefined do ( delete (getNodeByName
  "X") )` throws `Type error: Call needs function or class, got: undefined` when
  the node does not exist, so it only appears to work inside `fileIn`. Each guard
  binds the lookup first -- `local prev_X = getNodeByName "X"` then
  `if prev_X != undefined do ( delete prev_X )` -- which works whether the node is
  present or absent. The self-check rejects the one-liner outright.

* **`site_pad` creates nodes.** Every non-null `site_pad` part is a prism on
  `00_SITE` and belongs in the scene, so `massing.ms` creates one `Box` per part
  ahead of the elements, in the order `ground_pad`, `paving`, `kerb`, named
  `SP_GROUND_PAD` / `SP_PAVING` / `SP_KERB` -- upper case and `_` separated,
  matching the rule that turns a spec id into a node name. A site-pad part is
  not an `elements[]` entry, so it has no `EL-nnn` id and no grouping dummy;
  G-40 partitions elements only. The layer column stays data: nothing in the
  script assigns a layer to a node (07 section 8.1.3).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Sequence

# --------------------------------------------------------------------------- #
# Constants declared by references/07-spec-grammar.md
# --------------------------------------------------------------------------- #

SUPPORTED_SCHEMA_MAJOR = 1
SCHEMA_VERSION = "1.0"

STAGES: tuple[str, ...] = ("massing",)
UPSTREAM_NAME = "dimensions.json"
OUT_JSON_NAME = "massing.json"
OUT_MS_NAME = "massing.ms"

#: 07 section 8.1.4 -- the layer vocabulary is closed.
LAYER_VOCABULARY: tuple[str, ...] = (
    "00_SITE",
    "01_SLABS",
    "02_STRUCTURE",
    "03_CORE",
    "04_ROOF",
    "05_FACADE",
    "90_SCENE",
    "99_DEBUG",
)
SITE_LAYER = "00_SITE"
SCENE_LAYER = "90_SCENE"

#: 07 section 8.1.2 -- kind -> layer is a table, not a preference.
KIND_LAYER: dict[str, str] = {
    "plinth": "00_SITE",
    "slab": "01_SLABS",
    "column": "02_STRUCTURE",
    "core_wall": "03_CORE",
    "roof_deck": "04_ROOF",
    "parapet": "04_ROOF",
    "facade_wall": "05_FACADE",
}
ELEMENT_KINDS: tuple[str, ...] = tuple(KIND_LAYER)

#: 07 section 8.1.1 -- the grouping vocabulary. ``facade`` was reserved for
#: P5/P6 and P6 is that reservation being used: the ``facade_wall`` elements of
#: the P6 change table are what makes the envelope total, so they need a group
#: of their own (G-40 puts every element in exactly one).
GROUP_KINDS: tuple[str, ...] = ("site", "slabs", "columns", "core", "roof", "facade")
GROUP_OF_KIND: dict[str, str] = {
    "plinth": "site",
    "slab": "slabs",
    "column": "columns",
    "core_wall": "core",
    "roof_deck": "roof",
    "parapet": "roof",
    "facade_wall": "facade",
}

#: 09-defaults.md ``D-FW-01`` -- *reference only*, the modelled thickness of an
#: opaque facade wall band. This is **assumed**, never derived: nothing in
#: ``dimensions.json`` dimensions a facade build-up, and inventing a silent
#: default is the P5 trap (references/_p5-contract.md section 5.2, which is why
#: ``A-023`` / ``A-024`` exist for the two P5 defaults). It carries a ledger
#: entry and lives in ``massing.json:defaults``, and G-36's derived-only clause
#: is scoped to leave that one block alone -- see ``_g36_provenance``.
FACADE_WALL_THICKNESS_CM = 20.0
FACADE_WALL_THICKNESS_RANGE_CM = (10.0, 40.0)
FACADE_WALL_THICKNESS_LEDGER = "A-025"
FACADE_WALL_THICKNESS_LEAF = "defaults.facade_wall_thickness_cm"

ELEMENT_ID_RE = re.compile(r"^EL-\d{3}$")
GROUP_ID_RE = re.compile(r"^GRP-\d{3}$")
PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

#: 11 section 3.1 N1 -- a generated node name is pasted into emitted MAXScript and
#: into typed-tool arguments, so it must be a bare identifier: ``EL-001`` becomes
#: ``EL_001`` because ``-`` reads as subtraction there.
NODE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

#: 07 section 8.1.1 -- ``site_pad`` parts, the order ``massing.ms`` emits them in,
#: and the node name each one gets (upper case, ``_`` separated, like a spec id
#: with its dashes turned into underscores).
SITE_PAD_PARTS: tuple[str, ...] = ("ground_pad", "paving", "kerb")
SITE_PAD_NODE: dict[str, str] = {
    "ground_pad": "SP_GROUND_PAD",
    "paving": "SP_PAVING",
    "kerb": "SP_KERB",
}

#: 07 section 9.1 G-9 -- keys outside the origins coverage rule.
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

_TOKEN_RE = re.compile(r"([^.\[\]]+)|\[(\d+)\]")

EXIT_OK = 0
EXIT_REFUSAL = 1
EXIT_USAGE = 2


class Refusal(Exception):
    """A deliberate non-zero exit. The message names the file, id or rule."""


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #


def q(value: Any) -> float:
    """Round to 6 decimals and normalise -0.0, so the bytes never wobble."""
    number = float(value)
    rounded = round(number, 6)
    return 0.0 if rounded == 0.0 else rounded


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def is_point(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(as_float(item) is not None for item in value)
    )


def num(value: Any) -> str:
    """MAXScript literal for a spec number: 1800 -> '1800.0', 1372.5 -> '1372.5'."""
    number = q(value)
    if float(number).is_integer():
        return f"{int(number)}.0"
    return repr(float(number))


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
    """Resolve a dotted path against a parsed document. Mirrors G-9 machinery."""
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
    return (
        key in COVERAGE_EXEMPT_KEYS or key.endswith(COVERAGE_EXEMPT_SUFFIXES)
    )


def collect_leaves(document: Any) -> list[str]:
    """Every leaf path that needs an ``origins`` entry, in file order.

    The same walk as G-9: an array of scalars (including a polygon ring) is one
    leaf; an array of objects is descended into; ``id`` / ``name`` / ``index`` /
    ``*_index`` / ``*_indices`` and the envelope, ``tolerances``, ``origins`` and
    ``origin_inputs`` blocks are outside the rule.
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


def expand_rect_ring(ring: Any, kind: Any) -> list[list[float]]:
    """07 section 5.4: a `rectangle` footprint may be two corners."""
    points = [
        [as_float(p[0]) or 0.0, as_float(p[1]) or 0.0]
        for p in (ring if isinstance(ring, list) else [])
        if is_point(p)
    ]
    if kind == "rectangle" and len(points) == 2:
        (x1, y1), (x2, y2) = points
        x0, x1 = min(x1, x2), max(x1, x2)
        y0, y1 = min(y1, y2), max(y1, y2)
        return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    return points


def signed_area_cm2(ring: Sequence[Sequence[float]]) -> float:
    total = 0.0
    count = len(ring)
    for index in range(count):
        x1, y1 = ring[index]
        x2, y2 = ring[(index + 1) % count]
        total += x1 * y2 - x2 * y1
    return total / 2.0


# --------------------------------------------------------------------------- #
# Rectangles -- the only profile shape this stage can emit
# --------------------------------------------------------------------------- #


Rect = tuple[float, float, float, float]


def rect_ring(rect: Rect) -> list[list[float]]:
    """CCW from the minimum corner (07 section 6.1 of agents/max-massing.md)."""
    x0, y0, x1, y1 = rect
    return [[q(x0), q(y0)], [q(x1), q(y0)], [q(x1), q(y1)], [q(x0), q(y1)]]


def group_bounds(elements: Sequence[dict[str, Any]]) -> tuple[float, float, float, float]:
    """``(xmin, xmax, ymin, ymax)`` over the plan of a group's elements.

    Every vertex is considered, so the result does not depend on where a ring
    happens to start.
    """
    xs: list[float] = []
    ys: list[float] = []
    for element in elements:
        for point in expand_rect_ring(element["profile_cm"], "polygon"):
            xs.append(q(point[0]))
            ys.append(q(point[1]))
    return (min(xs), max(xs), min(ys), max(ys))


def parapet_bands(rect: Rect, thickness: float) -> list[tuple[str, Rect]]:
    """07 section 8.1.1: a hollow shape is one prism per straight side.

    The four bands partition the annulus between the deck outline and the outline
    inset by ``thickness``: the two long bands span the full length and the two
    short bands fill between them, so no band overlaps another and none is left
    out. Returned in the ring's own CCW side order -- south, east, north, west --
    which is what makes the element ids stable across rebuilds.
    """
    x0, y0, x1, y1 = rect
    t = q(thickness)
    if t <= 0:
        raise Refusal(
            f"parapet_thickness_cm is {num(t)}; a parapet band needs a positive width."
        )
    if (x1 - x0) <= 2 * t or (y1 - y0) <= 2 * t:
        raise Refusal(
            f"roof.parapet_thickness_cm ({num(t)}) does not fit twice inside the deck "
            f"outline {rect}; four parapet bands cannot be placed."
        )
    return [
        ("south", (x0, y0, x1, q(y0 + t))),
        ("east", (q(x1 - t), q(y0 + t), x1, q(y1 - t))),
        ("north", (x0, q(y1 - t), x1, y1)),
        ("west", (x0, q(y0 + t), q(x0 + t), q(y1 - t))),
    ]


def inward_normal(
    start: Sequence[float], end: Sequence[float], toward: tuple[float, float]
) -> tuple[float, float]:
    """The unit normal of the run ``start``->``end`` that points **inward**.

    "Inward" is decided by ``toward`` -- the centre of the site footprint -- rather
    than by a winding convention. A facade run is directed by ``dimensions.json``
    in whatever order reads naturally, and the four runs of a rectangle are *not*
    all wound the same way round the ring (``F-S`` runs with it, ``F-N`` against
    it), so a left-of-direction rule would band two of the four outward. Comparing
    the two candidate offsets against the footprint centre is independent of where
    the ring starts and of which corner a run begins at.
    """
    dx = q(end[0]) - q(start[0])
    dy = q(end[1]) - q(start[1])
    length = math.hypot(dx, dy)
    if length <= 0.0:
        raise Refusal(
            f"a facade run whose start and end corner coincide ({num(dx)}, {num(dy)}) has no "
            "length; a facade_wall band cannot be placed on it."
        )
    nx, ny = -dy / length, dx / length
    mid = ((q(start[0]) + q(end[0])) / 2.0, (q(start[1]) + q(end[1])) / 2.0)
    plus = math.hypot(mid[0] + nx - toward[0], mid[1] + ny - toward[1])
    minus = math.hypot(mid[0] - nx - toward[0], mid[1] - ny - toward[1])
    return (nx, ny) if plus <= minus else (-nx, -ny)


def facade_wall_band(
    start: Any,
    end: Any,
    thickness: float,
    toward: tuple[float, float],
    facade_id: Any,
) -> Rect:
    """The facade run banded **inward** by ``thickness`` (P6 contract section 2.1).

    The band spans ``start_corner_cm``..``end_corner_cm`` and extends toward the
    building interior, so its face stays flush with the facade panel line on the
    corner. An outward band would push the envelope past the panel plane, which is
    the reason this mirrors ``parapet_bands``' inside-the-outline reasoning rather
    than a plain offset. Unlike the parapet -- four bands that must *partition* the
    annulus -- these bands span the full run length, so at a corner two of them
    overlap over a ``thickness`` square. That is what the contract asks for: G-38
    requires every wall to span its facade's ``length_cm``, and a mitred corner
    would shorten two of the four runs.
    """
    if not (is_point(start) and is_point(end)):
        raise Refusal(
            f"{facade_id}: start_corner_cm / end_corner_cm are {start!r} / {end!r}; a "
            "facade_wall band needs two [x, y] corners (07 section 5.10)."
        )
    t = q(thickness)
    if t <= 0:
        raise Refusal(
            f"{facade_id}: facade_wall_thickness_cm is {num(t)}; a facade wall band needs a "
            "positive width (09 D-FW-01 declares 10-40)."
        )
    sx = as_float(start[0]) or 0.0
    sy = as_float(start[1]) or 0.0
    ex = as_float(end[0]) or 0.0
    ey = as_float(end[1]) or 0.0
    nx, ny = inward_normal((sx, sy), (ex, ey), toward)
    corners = {
        (q(sx), q(sy)),
        (q(ex), q(ey)),
        (q(sx + nx * t), q(sy + ny * t)),
        (q(ex + nx * t), q(ey + ny * t)),
    }
    rect = (
        min(p[0] for p in corners),
        min(p[1] for p in corners),
        max(p[0] for p in corners),
        max(p[1] for p in corners),
    )
    if len(corners) != 4 or corners != {
        (rect[0], rect[1]),
        (rect[2], rect[1]),
        (rect[2], rect[3]),
        (rect[0], rect[3]),
    }:
        raise Refusal(
            f"{facade_id}: the band from {list(start)} to {list(end)} offset inward by "
            f"{num(t)} cm is not an axis-aligned rectangle. The only verified primitive at "
            "this stage is Box(width:,length:,height:,pos:), which cannot describe it; a "
            "rotated facade envelope belongs to P4 and is refused here (07 section 8.1.1)."
        )
    return rect


def rect_of(ring: Any, source_path: str, kind: Any, element_id: str) -> Rect:
    """Return the rectangle ``ring`` describes, or refuse by name.

    A profile that is not an axis-aligned rectangle is NOT approximated with its
    bounding box: that is a wrong massing that validates. It belongs to P4,
    where ``nurbs.json`` owns surfaces.
    """
    points = expand_rect_ring(ring, kind)
    detail = (
        f"{source_path} is not an axis-aligned rectangle "
        f"({len(points)} vertex/vertices: {points})"
    )
    if len(points) != 4 or not all(is_point(p) for p in points):
        raise Refusal(
            f"{element_id}: {detail}. 07 section 8.1.1 makes every massing profile a "
            "Z-prism on a rectangle, and the only verified 3ds Max primitive at this "
            "stage is Box(width:,length:,height:,pos:), which cannot describe it. "
            "A non-rectangular profile belongs to P4 (NURBS) and is refused here."
        )
    xs = sorted({q(p[0]) for p in points})
    ys = sorted({q(p[1]) for p in points})
    if len(xs) != 2 or len(ys) != 2:
        raise Refusal(
            f"{element_id}: {detail}. The four vertices are not the corners of one "
            "axis-aligned rectangle (X values {xs}, Y values {ys}). A non-rectangular "
            "profile belongs to P4 (NURBS) and is refused here."
        )
    x0, x1 = xs
    y0, y1 = ys
    corners = {(x0, y0), (x1, y0), (x1, y1), (x0, y1)}
    if {(q(p[0]), q(p[1])) for p in points} != corners:
        raise Refusal(
            f"{element_id}: {detail}. Duplicate or repeated vertices: a massing "
            "profile needs >= 3 distinct vertices and no repeated final vertex "
            "(G-35). A non-rectangular profile belongs to P4 (NURBS)."
        )
    return (x0, y0, x1, y1)


def inset(rect: Rect, amount: float) -> Rect:
    x0, y0, x1, y1 = rect
    return (q(x0 + amount), q(y0 + amount), q(x1 - amount), q(y1 - amount))


def grow(rect: Rect, amount: float) -> Rect:
    x0, y0, x1, y1 = rect
    return (q(x0 - amount), q(y0 - amount), q(x1 + amount), q(y1 + amount))


def overlaps(a: Rect, b: Rect) -> bool:
    """Positive-area intersection. Touching edges do not count as overlapping."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


# --------------------------------------------------------------------------- #
# Reading the locked input
# --------------------------------------------------------------------------- #


def strict_loads(text: str) -> Any:
    def _reject(name: str) -> Any:
        raise ValueError(f"JSON constant {name} is not allowed (07 G-7)")

    return json.loads(text, parse_constant=_reject)


def load_locked_dimensions(specs_dir: Path) -> dict[str, Any]:
    """07 section 3.1: never build from anything that is not `locked`."""
    path = specs_dir / UPSTREAM_NAME
    if not path.is_file():
        raise Refusal(
            f"refusing to build: {UPSTREAM_NAME} not found in {specs_dir}. A builder "
            "may not start without the locked dimensional contract (07 section 3.1)."
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
            f"refusing to build: {path} is not strict JSON -- {exc}. A half-read brief "
            "must never become geometry (07 section 3.1)."
        ) from exc
    if not isinstance(document, dict):
        raise Refusal(
            f"refusing to build: {path} top level is "
            f"{type(document).__name__}, not an object (07 section 3.1)."
        )

    status = document.get("status")
    if status != "locked":
        raise Refusal(
            f"refusing to build: {path} has status {status!r}, not 'locked'. 07 "
            "section 3.1: a builder must refuse to consume a draft or superseded "
            "file and must say which file and which status it found."
        )

    version = document.get("schema_version")
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?$", str(version))
    if match is None or int(match.group(1)) != SUPPORTED_SCHEMA_MAJOR:
        raise Refusal(
            f"refusing to build: {path} declares schema_version {version!r}; this "
            f"builder implements major {SUPPORTED_SCHEMA_MAJOR} and must stop rather "
            "than guess (07 G-3)."
        )

    project = document.get("project")
    if not isinstance(project, str) or not PROJECT_ID_RE.match(project):
        raise Refusal(
            f"refusing to build: {path} project {project!r} does not match "
            "07 section 3.1 ^[a-z0-9][a-z0-9._-]*$."
        )

    for key in ("tolerances", "site", "structure", "levels", "core", "floor_plates", "roof"):
        if key not in document:
            raise Refusal(f"refusing to build: {path} is missing {key!r}, which G-38 needs.")

    units = document.get("units")
    if not isinstance(units, dict) or units.get("length") != "cm" or units.get("angle") != "deg":
        raise Refusal(
            f"refusing to build: {path} units {units!r} are not cm/deg (07 section 2, G-5)."
        )
    return document


# --------------------------------------------------------------------------- #
# Building massing.json
# --------------------------------------------------------------------------- #


class Model:
    """The builder's working state: the document plus its provenance notes."""

    def __init__(self, dimensions: dict[str, Any]) -> None:
        self.dim = dimensions
        self.elements: list[dict[str, Any]] = []
        self.stores: list[dict[str, Any]] = []
        self.sources: dict[str, list[str]] = {}
        self.conflicts: dict[str, str] = {}
        self._element_counter = 0
        self._group_counter = 0
        self.skipped_columns: list[str] = []
        self.parapet_sides: list[tuple[str, str]] = []
        self.facade_walls: list[tuple[str, str, Any]] = []
        self._site_rect: Rect | None = None
        self._core_rect: Rect | None = None

    # -- provenance ------------------------------------------------------- #

    def note(self, leaf_path: str, inputs: Sequence[str]) -> None:
        """Record where one leaf came from (G-36) and any conflict behind it."""
        self.sources[leaf_path] = [str(item) for item in inputs]
        for item in inputs:
            ref = CONFLICT_BY_INPUT.get(str(item))
            if ref is not None:
                self.conflicts.setdefault(leaf_path, ref)

    def next_element_id(self) -> str:
        self._element_counter += 1
        return f"EL-{self._element_counter:03d}"

    def peek_element_id(self) -> str:
        """The id the next :meth:`next_element_id` will hand out."""
        return f"EL-{self._element_counter + 1:03d}"

    def next_group_id(self) -> str:
        self._group_counter += 1
        return f"GRP-{self._group_counter:03d}"

    # -- rectangles the elements share ------------------------------------ #

    def site_rect(self, element_id: str) -> Rect:
        if self._site_rect is None:
            site = self.dim["site"]
            self._site_rect = rect_of(
                site.get("footprint_cm"), "site.footprint_cm", site.get("footprint_kind"), element_id
            )
        return self._site_rect

    def core_rect(self, element_id: str) -> Rect:
        if self._core_rect is None:
            core = self.dim["core"]
            self._core_rect = rect_of(
                core.get("footprint_cm"), "core.footprint_cm", core.get("footprint_kind"), element_id
            )
        return self._core_rect


#: A derived value whose *inputs* were conflict-resolved says so (07 section 5.2).
CONFLICT_BY_INPUT: dict[str, str] = {
    "levels[0].height_cm": "C-001",
    "levels[1].height_cm": "C-001",
    "floor_plates[0].thickness_cm": "C-005",
    "floor_plates[1].thickness_cm": "C-005",
    "roof.parapet_height_cm": "C-004",
}


def build_massing(dimensions: dict[str, Any]) -> tuple[dict[str, Any], Model]:
    model = Model(dimensions)
    dim = dimensions
    site = dim["site"]
    structure = dim["structure"]
    levels = dim["levels"]
    core = dim["core"]
    plates = dim["floor_plates"]
    roof = dim["roof"]

    rotation = as_float(site.get("plot_rotation_deg")) or 0.0
    if abs(rotation) > 1e-9:
        raise Refusal(
            f"refusing to build: site.plot_rotation_deg is {rotation}, not 0. Box() has "
            "no rotation in the verified call shape, so a rotated footprint cannot be "
            "emitted at this stage (agents/max-massing.md 6.4)."
        )

    plate_by_level = {p.get("level_index"): p for p in plates if isinstance(p, dict)}

    # ---- slabs, one per storey (G-38) ----------------------------------- #
    for position, level in enumerate(levels):
        index = level.get("index")
        plate = plate_by_level.get(index)
        if plate is None:
            raise Refusal(
                f"refusing to build: levels[{position}] (index {index!r}) has no entry in "
                "floor_plates[], so G-38 has no slab thickness to place."
            )
        eid = model.next_element_id()
        rect = model.site_rect(eid)
        elevation = q(level["elevation_cm"])
        thickness = q(plate["thickness_cm"])
        model.elements.append(
            _element(
                eid,
                "slab",
                index,
                rect,
                [q(elevation - thickness), elevation],
            )
        )
        inputs = [f"levels[{position}].elevation_cm", f"floor_plates[{position}].thickness_cm",
                  "site.footprint_cm"]
        for key in ("kind", "profile_cm", "profile_ccw", "z_range_cm", "layer"):
            model.note(f"elements[{len(model.elements) - 1}].{key}", inputs)

    # ---- columns, one per grid intersection per storey (G-38) ---------- #
    column_x = [q(v) for v in structure.get("column_x_cm", [])]
    column_y = [q(v) for v in structure.get("column_y_cm", [])]
    section = structure.get("column_section_cm") or [40.0, 40.0]
    size_x = q(section[0])
    size_y = q(section[1])

    for position, level in enumerate(levels):
        index = level.get("index")
        plate = plate_by_level.get(index)
        if plate is None:
            raise Refusal(
                f"refusing to build: levels[{position}] (index {index!r}) has no entry in "
                "floor_plates[], so G-38 has no slab thickness to place a column."
            )
        elevation = q(level["elevation_cm"])
        thickness = q(plate["thickness_cm"])
        top = q(elevation + q(level["height_cm"]))
        for line_x in column_x:
            for line_y in column_y:
                eid = model.next_element_id()
                rect = (q(line_x - size_x / 2.0), q(line_y - size_y / 2.0),
                        q(line_x + size_x / 2.0), q(line_y + size_y / 2.0))
                if overlaps(rect, model.core_rect(eid)):
                    model.skipped_columns.append(
                        f"grid line ({num(line_x)},{num(line_y)}) on storey "
                        f"{index}: its {num(size_x)}x{num(size_y)} plan rectangle "
                        "overlaps core.footprint_cm"
                    )
                    model._element_counter -= 1  # keep ids dense; nothing was emitted
                    continue
                model.elements.append(
                    _element(eid, "column", index, rect, [q(elevation - thickness), top])
                )
                inputs = [
                    "structure.column_x_cm",
                    "structure.column_y_cm",
                    "structure.column_section_cm",
                    f"levels[{position}].elevation_cm",
                    f"levels[{position}].height_cm",
                    f"floor_plates[{position}].thickness_cm",
                ]
                for key in ("kind", "profile_cm", "profile_ccw", "z_range_cm", "layer"):
                    model.note(f"elements[{len(model.elements) - 1}].{key}", inputs)

    # ---- core walls, one per spanned storey (G-38 fixes the profile) --- #
    spans = core.get("spans_level_indices") or []
    for position, level in enumerate(levels):
        if level.get("index") not in spans:
            continue
        eid = model.next_element_id()
        wall_thickness = q(core.get("wall_thickness_cm", 20.0))
        rect = inset(model.core_rect(eid), wall_thickness)
        if rect[2] - rect[0] <= 0 or rect[3] - rect[1] <= 0:
            raise Refusal(
                f"{eid}: core.footprint_cm inset by core.wall_thickness_cm "
                f"({num(wall_thickness)}) leaves no plan area; a core_wall is not "
                "expressible."
            )
        elevation = q(level["elevation_cm"])
        top = q(elevation + q(level["height_cm"]))
        model.elements.append(_element(eid, "core_wall", level.get("index"), rect, [elevation, top]))
        inputs = [
            "core.footprint_cm",
            "core.wall_thickness_cm",
            "core.spans_level_indices",
            f"levels[{position}].elevation_cm",
            f"levels[{position}].height_cm",
        ]
        for key in ("kind", "profile_cm", "profile_ccw", "z_range_cm", "layer"):
            model.note(f"elements[{len(model.elements) - 1}].{key}", inputs)

    # ---- roof deck and the four parapet bands (G-38) -------------------- #
    deck_level = q(roof["deck_level_cm"])
    deck_thickness = q(roof["deck_thickness_cm"])
    parapet_height = q(roof["parapet_height_cm"])
    parapet_thickness = q(roof.get("parapet_thickness_cm", 20.0))

    # deck_level_cm is the TOP of the build-up; the thickness hangs below it.
    eid = model.next_element_id()
    model.elements.append(
        _element(
            eid,
            "roof_deck",
            None,
            model.site_rect(eid),
            [q(deck_level - deck_thickness), deck_level],
        )
    )
    inputs = ["roof.deck_level_cm", "roof.deck_thickness_cm", "site.footprint_cm"]
    for key in ("kind", "profile_cm", "profile_ccw", "z_range_cm", "layer"):
        model.note(f"elements[{len(model.elements) - 1}].{key}", inputs)

    # 07 section 8.1.1: one prism per straight side of the parapet band.
    for side, band in parapet_bands(model.site_rect(model.peek_element_id()), parapet_thickness):
        eid = model.next_element_id()
        model.elements.append(
            _element(eid, "parapet", None, band, [deck_level, q(deck_level + parapet_height)])
        )
        inputs = [
            "roof.deck_level_cm",
            "roof.parapet_height_cm",
            "roof.parapet_thickness_cm",
            "site.footprint_cm",
        ]
        for key in ("kind", "profile_cm", "profile_ccw", "z_range_cm", "layer"):
            model.note(f"elements[{len(model.elements) - 1}].{key}", inputs)
        model.parapet_sides.append((eid, side))

    # ---- facade wall bands, one per (facade, level) (G-38, P6) ----------- #
    # P3 emitted no exterior envelope, so `assembly.json`'s opening cuts had no
    # host to cut (P6 contract section 2). One prism per (facade, level): the run
    # from start_corner_cm to end_corner_cm, banded inward by the assumed
    # `defaults.facade_wall_thickness_cm`, over the full storey height.
    wall_thickness = q(FACADE_WALL_THICKNESS_CM)
    if not FACADE_WALL_THICKNESS_RANGE_CM[0] <= wall_thickness <= FACADE_WALL_THICKNESS_RANGE_CM[1]:
        raise Refusal(
            f"refusing to build: defaults.facade_wall_thickness_cm is {num(wall_thickness)}, "
            f"outside 09 D-FW-01's declared range "
            f"{num(FACADE_WALL_THICKNESS_RANGE_CM[0])}-{num(FACADE_WALL_THICKNESS_RANGE_CM[1])} "
            f"cm. A value outside the declared range is not a default ({FACADE_WALL_THICKNESS_LEDGER})."
        )
    site_rect = model.site_rect("(facade_walls)")
    toward = ((site_rect[0] + site_rect[2]) / 2.0, (site_rect[1] + site_rect[3]) / 2.0)
    facades = [f for f in (dim.get("facades") or []) if isinstance(f, dict)]
    if not facades:
        raise Refusal(
            "refusing to build: dimensions.json declares no facades[], so G-38 cannot place "
            "a facade_wall for any (facade, level) pair."
        )
    for f_position, facade in enumerate(facades):
        facade_id = facade.get("id", f"facades[{f_position}]")
        band = facade_wall_band(
            facade.get("start_corner_cm"),
            facade.get("end_corner_cm"),
            wall_thickness,
            toward,
            facade_id,
        )
        for position, level in enumerate(levels):
            eid = model.next_element_id()
            elevation = q(level["elevation_cm"])
            top = q(elevation + q(level["height_cm"]))
            model.elements.append(
                _element(eid, "facade_wall", level.get("index"), band, [elevation, top])
            )
            inputs = [
                f"facades[{f_position}].start_corner_cm",
                f"facades[{f_position}].end_corner_cm",
                f"facades[{f_position}].length_cm",
                f"levels[{position}].elevation_cm",
                f"levels[{position}].height_cm",
                FACADE_WALL_THICKNESS_LEAF,
            ]
            for key in ("kind", "profile_cm", "profile_ccw", "z_range_cm", "layer"):
                model.note(f"elements[{len(model.elements) - 1}].{key}", inputs)
            model.facade_walls.append((eid, str(facade_id), level.get("index")))

    # ---- storeys (07 section 8.1.1) ------------------------------------- #
    for position, level in enumerate(levels):
        index = level.get("index")
        elevation = q(level["elevation_cm"])
        height = q(level["height_cm"])
        slab_ref = next(
            e["id"] for e in model.elements
            if e["kind"] == "slab" and e["storey_index"] == index
        )
        column_refs = [
            e["id"] for e in model.elements
            if e["kind"] == "column" and e["storey_index"] == index
        ]
        core_refs = [
            e["id"] for e in model.elements
            if e["kind"] == "core_wall" and e["storey_index"] == index
        ]
        model.stores.append(
            {
                "index": index,
                "level_ref": level.get("id"),
                "elevation_cm": elevation,
                "height_cm": height,
                "z_range_cm": [elevation, q(elevation + height)],
                "slab_ref": slab_ref,
                "column_refs": column_refs,
                "core_refs": core_refs,
            }
        )
        stem = f"storeys[{position}]"
        model.note(f"{stem}.level_ref", [f"levels[{position}].id"])
        model.note(f"{stem}.elevation_cm", [f"levels[{position}].elevation_cm"])
        model.note(f"{stem}.height_cm", [f"levels[{position}].height_cm"])
        model.note(
            f"{stem}.z_range_cm",
            [f"levels[{position}].elevation_cm", f"levels[{position}].height_cm"],
        )
        slab_index = _index_of(model.elements, slab_ref)
        model.note(f"{stem}.slab_ref", [f"elements[{slab_index}].id"])
        model.note(
            f"{stem}.column_refs",
            ["structure.column_x_cm", "structure.column_y_cm", "structure.column_section_cm"],
        )
        model.note(f"{stem}.core_refs", ["core.footprint_cm", "core.spans_level_indices"])

    # ---- site pad (07 section 8.1.1) ------------------------------------ #
    pad_rect = grow(model.site_rect("site_pad.ground_pad"), q(site.get("setback_cm", 300.0)))
    ground_level = q(site["ground_level_cm"])
    pad_thickness = q(plate_by_level[0]["thickness_cm"])
    site_pad = {
        "ground_pad": {
            "profile_cm": rect_ring(pad_rect),
            "profile_ccw": True,
            "z_range_cm": [q(ground_level - pad_thickness), ground_level],
        },
        "paving": None,
        "kerb": None,
        "layer": SITE_LAYER,
    }
    model.note("site_pad.ground_pad.profile_cm", ["site.footprint_cm", "site.setback_cm"])
    model.note("site_pad.ground_pad.profile_ccw", ["site.footprint_cm", "site.footprint_ccw"])
    model.note(
        "site_pad.ground_pad.z_range_cm", ["site.ground_level_cm", "floor_plates[0].thickness_cm"]
    )
    model.note("site_pad.paving", ["site"])
    model.note("site_pad.kerb", ["site"])
    model.note("site_pad.layer", ["site"])

    # ---- grouping (07 section 8.1.1) ------------------------------------ #
    grouping: list[dict[str, Any]] = []
    for group_kind in GROUP_KINDS:
        members = [e for e in model.elements if GROUP_OF_KIND[e["kind"]] == group_kind]
        if not members:
            continue
        gid = model.next_group_id()
        x0, x1, y0, y1 = group_bounds(members)
        z0 = min(q(e["z_range_cm"][0]) for e in members)
        pivot = [q((x0 + x1) / 2.0), q((y0 + y1) / 2.0), z0]
        grouping.append(
            {
                "id": gid,
                "name": node_name(gid),
                "kind": group_kind,
                "element_ids": [e["id"] for e in members],
                "parent_pivot_cm": pivot,
                "layer": SCENE_LAYER,
            }
        )
        stem = f"grouping[{len(grouping) - 1}]"
        model.note(f"{stem}.kind", ["elements"])
        model.note(
            f"{stem}.element_ids",
            [f"elements[{_index_of(model.elements, e['id'])}].id" for e in members],
        )
        model.note(
            f"{stem}.parent_pivot_cm",
            [
                f"elements[{_index_of(model.elements, e['id'])}].{leaf}"
                for e in members
                for leaf in ("profile_cm", "z_range_cm")
            ],
        )
        model.note(f"{stem}.layer", ["elements"])

    # ---- envelope and provenance ---------------------------------------- #
    # origin_inputs is exactly the set of dimensions.json paths this build read,
    # which is what 07 G-36 requires them to resolve against. The other
    # derives_from targets are in-file ones, rooted at `elements`, plus the one
    # assumed `defaults` key -- none of which is a dimensions.json path, so
    # listing any of them here would be a G-36 FAIL.
    origin_inputs = sorted(
        {
            path
            for inputs in model.sources.values()
            for path in inputs
            if resolve(dim, path)[0]
        }
    )

    document: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "spec": "massing",
        "project": dim["project"],
        "units": {"length": "cm", "angle": "deg"},
        "source": {
            "kind": "derived",
            "reference": (
                f"{UPSTREAM_NAME} -- the locked dimensional contract for {dim['project']}; "
                "every value in this file is computed from it by "
                "scripts/build_spec.py --stage massing"
            ),
            "recorded_at": dim["source"]["recorded_at"],
        },
        "status": "locked",
        "tolerances": dict(dim["tolerances"]),
        "origin_inputs": origin_inputs,
        "origins": {},
        # 07 section 8.1: the one assumed value massing.json declares. It is
        # *assumed* and carries a ledger ref -- never `derived`, because nothing
        # in dimensions.json dimensions a facade build-up (09 D-FW-01, A-025).
        "defaults": {"facade_wall_thickness_cm": wall_thickness},
        "storeys": model.stores,
        "elements": model.elements,
        "site_pad": site_pad,
        "grouping": grouping,
    }

    document["origins"] = build_origins(document, model)
    return document, model


def _element(
    element_id: str,
    kind: str,
    storey_index: Any,
    rect: Rect,
    z_range: Sequence[float],
) -> dict[str, Any]:
    return {
        "id": element_id,
        "kind": kind,
        "storey_index": storey_index,
        "profile_cm": rect_ring(rect),
        "profile_ccw": True,
        "z_range_cm": [q(z_range[0]), q(z_range[1])],
        "layer": KIND_LAYER[kind],
    }


def _index_of(elements: Sequence[dict[str, Any]], element_id: str) -> int:
    for position, element in enumerate(elements):
        if element["id"] == element_id:
            return position
    raise Refusal(f"internal: element {element_id} is not in elements[]")


#: The assumed leaves this builder declares, and the ledger entry each one names.
#: ``A-023`` / ``A-024`` did the same for the two P5 defaults; the pair is the
#: precedent for why a value nothing dimensions must be recorded rather than
#: quietly invented (references/_p5-contract.md section 5.2).
ASSUMED_LEAVES: dict[str, str] = {
    FACADE_WALL_THICKNESS_LEAF: FACADE_WALL_THICKNESS_LEDGER,
}


def build_origins(document: dict[str, Any], model: Model) -> dict[str, Any]:
    """One entry per leaf, in document order: ``derived``, or ``assumed`` for
    the declared defaults block (G-36, with the documented exception below)."""
    origins: dict[str, Any] = {}
    for leaf in collect_leaves(document):
        ledger = ASSUMED_LEAVES.get(leaf)
        if ledger is not None:
            origins[leaf] = {"origin": "assumed", "origin_ref": ledger}
            continue
        inputs = model.sources.get(leaf)
        if inputs is None:
            raise Refusal(
                f"internal: leaf {leaf} has no provenance recorded; G-36 requires an "
                "origins entry for every leaf and this builder records one itself."
            )
        entry: dict[str, Any] = {"origin": "derived", "derives_from": list(inputs)}
        conflict_ref = model.conflicts.get(leaf)
        if conflict_ref is not None:
            entry["conflict_ref"] = conflict_ref
        origins[leaf] = entry
    return origins


# --------------------------------------------------------------------------- #
# The emitted MAXScript -- geometry only, no layer code
# --------------------------------------------------------------------------- #


def referenced_layers(document: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for element in document["elements"]:
        names.add(str(element["layer"]))
    site_pad = document.get("site_pad")
    if isinstance(site_pad, dict) and isinstance(site_pad.get("layer"), str):
        names.add(site_pad["layer"])
    for group in document.get("grouping", []):
        names.add(str(group["layer"]))
    return [name for name in LAYER_VOCABULARY if name in names]


def prism_box(profile: Any, z_range: Sequence[float]) -> tuple[str, str, str, str]:
    """``Box`` is X/Y-centred on ``pos.xy`` with its base at ``pos.z`` (verified)."""
    points = expand_rect_ring(profile, "polygon")
    x0 = min(q(p[0]) for p in points)
    x1 = max(q(p[0]) for p in points)
    y0 = min(q(p[1]) for p in points)
    y1 = max(q(p[1]) for p in points)
    z0, z1 = q(z_range[0]), q(z_range[1])
    pos = [(x0 + x1) / 2.0, (y0 + y1) / 2.0, z0]
    return (
        num(q(x1 - x0)),
        num(q(y1 - y0)),
        num(q(z1 - z0)),
        "[" + ",".join(num(v) for v in pos) + "]",
    )


def node_name(spec_id: Any) -> str:
    """11 section 3.1 N1: the node name is the spec id with dashes replaced.

    ``EL-001`` -> ``EL_001``, ``GRP-001`` -> ``GRP_001``. Nothing else changes, and
    the same function names the MAXScript local, the scene node and
    ``grouping[].name`` so the three can never disagree.
    """
    return str(spec_id).replace("-", "_")


def element_box(element: dict[str, Any]) -> tuple[str, str, str, str]:
    return prism_box(element["profile_cm"], element["z_range_cm"])


def site_pad_nodes(document: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Every non-null ``site_pad`` part, in the order the script must emit them."""
    site_pad = document.get("site_pad")
    if not isinstance(site_pad, dict):
        return []
    out: list[tuple[str, dict[str, Any]]] = []
    for part in SITE_PAD_PARTS:
        value = site_pad.get(part)
        if isinstance(value, dict):
            out.append((SITE_PAD_NODE[part], value))
    return out


def build_fn_name(project: Any) -> str:
    """The emitted function's name: ``mcpMassingBuild_<project>``, identifier-safe."""
    return "mcpMassingBuild_" + re.sub(r"[^A-Za-z0-9_]", "_", str(project))


def render_ms(document: dict[str, Any], layers: Sequence[str]) -> str:
    """Emit the whole build as one function, called once.

    **Verified by execution (2026-10-04):** a ``local`` declaration at the top
    level of a ``fileIn``-ed script is a *compile* error --
    ``no local declarations at top level``. The body therefore lives inside one
    ``fn``, which is also what makes a second ``fileIn`` safe: every name the run
    creates is spec-derived, so the run deletes its own previous nodes first and
    converges on the same scene instead of accumulating duplicates.
    """
    project = document["project"]
    function = build_fn_name(project)
    pad_nodes = [name for name, _ in site_pad_nodes(document)]
    payload = pad_nodes + [node_name(e["id"]) for e in document["elements"]]
    dummies = [node_name(g["id"]) for g in document["grouping"]]

    body: list[str] = []
    for name in layers:
        # newLayerFromName throws when the layer exists; the guard is the catch,
        # because a second LayerManager route would be the layer code 07 8.1.3
        # forbids.
        body.append(
            f'try ( LayerManager.newLayerFromName "{name}" ) '
            f'catch ( print "{name} already exists" )'
        )
    # Idempotent re-run, policy: delete-then-create by spec-derived name. Payload
    # first, then the dummies that parent it (09 section 9 rule 2: deleting a
    # Dummy does not delete its children, so the payload goes first).
    #
    # The guard is written in the explicit-local form, executed live on
    # 2026-10-04: the one-liner `if (getNodeByName "X") != undefined do ( delete
    # (getNodeByName "X") )` throws "Type error: Call needs function or class, got:
    # undefined" when the node is absent, so it only works by accident inside
    # fileIn. Binding the lookup to a local first works in both cases.
    for variable in payload + dummies:
        body.append(f'local prev_{variable} = getNodeByName "{variable}"')
        body.append(f"if prev_{variable} != undefined do ( delete prev_{variable} )")
    for pad_variable, part in site_pad_nodes(document):
        width, length, height, pos = prism_box(part["profile_cm"], part["z_range_cm"])
        body.append(
            f"local {pad_variable} = Box width:{width} length:{length} height:{height} pos:{pos}"
        )
        body.append(f'{pad_variable}.name = "{pad_variable}"')
    for element in document["elements"]:
        variable = node_name(element["id"])
        width, length, height, pos = element_box(element)
        body.append(
            f"local {variable} = Box width:{width} length:{length} height:{height} pos:{pos}"
        )
        body.append(f'{variable}.name = "{variable}"')
    for group in document["grouping"]:
        variable = node_name(group["id"])
        pivot = ",".join(num(v) for v in group["parent_pivot_cm"])
        body.append(f'local {variable} = Dummy name:"{variable}"')
        body.append(f"{variable}.pos = [{pivot}]")
        for element_id in group["element_ids"]:
            body.append(f"{node_name(element_id)}.parent = {variable}")
    body.append("true")

    lines = [f"/* build_spec.py --stage massing | project {project} | DO NOT EDIT */"]
    lines.append(f"fn {function} = (")
    lines.extend(f"    {line}" for line in body)
    lines.append(")")
    lines.append(f"{function}()")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Self-check: G-34..G-40 against the bytes that will be written
# --------------------------------------------------------------------------- #


def _fails(failures: list[str], rule: str, message: str) -> None:
    failures.append(f"{rule}: {message}")


def self_check(
    document: dict[str, Any], dimensions: dict[str, Any], specs_dir: Path | None = None
) -> list[str]:
    failures: list[str] = []
    tolerance = as_float((dimensions.get("tolerances") or {}).get("linear_cm")) or 0.5

    def close(a: Any, b: Any) -> bool:
        left, right = as_float(a), as_float(b)
        return left is not None and right is not None and abs(left - right) <= tolerance + 1e-9

    # -- G-6 source, with the P3 addition --------------------------------- #
    source = document.get("source") if isinstance(document.get("source"), dict) else {}
    if source.get("kind") == "derived":
        reference = source.get("reference")
        named = re.findall(r"[A-Za-z0-9._-]+\.json", str(reference or ""))
        if not named:
            _fails(
                failures,
                "G-6",
                "source.kind is 'derived' but source.reference names no spec file; it "
                "must name the file this one was computed from",
            )
        for name in named:
            if specs_dir is not None and not (specs_dir / name).is_file():
                _fails(
                    failures,
                    "G-6",
                    f"source.reference names {name}, which does not exist in "
                    f"{specs_dir}; a derived file must point at a spec in the project",
                )

    elements = document.get("elements") if isinstance(document.get("elements"), list) else []
    grouping = document.get("grouping") if isinstance(document.get("grouping"), list) else []
    stores = document.get("storeys") if isinstance(document.get("storeys"), list) else []
    by_id = {e.get("id"): e for e in elements if isinstance(e, dict)}

    # -- G-34 element identity -------------------------------------------- #
    seen: set[str] = set()
    previous = ""
    for element in elements:
        ident = str(element.get("id"))
        if not ELEMENT_ID_RE.match(ident):
            _fails(failures, "G-34", f"{ident} does not match ^EL-\\d{{3}}$")
        if ident in seen:
            _fails(failures, "G-34", f"{ident} is not unique")
        if previous and ident <= previous:
            _fails(failures, "G-34", f"{ident} does not ascend (previous is {previous})")
        seen.add(ident)
        previous = ident
    seen_groups: set[str] = set()
    previous = ""
    for group in grouping:
        ident = str(group.get("id"))
        if not GROUP_ID_RE.match(ident):
            _fails(failures, "G-34", f"{ident} does not match ^GRP-\\d{{3}}$")
        if ident in seen_groups:
            _fails(failures, "G-34", f"{ident} is not unique")
        if previous and ident <= previous:
            _fails(failures, "G-34", f"{ident} does not ascend (previous is {previous})")
        seen_groups.add(ident)
        previous = ident

    # -- G-35 element solidity -------------------------------------------- #
    for element in elements:
        ident = str(element.get("id"))
        profile = element.get("profile_cm")
        if not isinstance(profile, list) or len(profile) < 3:
            _fails(failures, "G-35", f"{ident} profile_cm has {len(profile or [])} vertices")
            continue
        points = expand_rect_ring(profile, "polygon")
        if len({(q(p[0]), q(p[1])) for p in points}) != len(points):
            _fails(failures, "G-35", f"{ident} profile_cm has duplicate vertices")
        if points and points[0] == points[-1]:
            _fails(failures, "G-35", f"{ident} profile_cm repeats its final vertex")
        area = signed_area_cm2(points)
        if abs(area) < 1e-9:
            _fails(failures, "G-35", f"{ident} profile_cm has zero area")
        elif element.get("profile_ccw") is not True or area <= 0.0:
            _fails(
                failures,
                "G-35",
                f"{ident} declares profile_ccw={element.get('profile_ccw')!r} but the "
                f"signed area is {area}",
            )
        z_range = element.get("z_range_cm")
        if not isinstance(z_range, list) or len(z_range) != 2:
            _fails(failures, "G-35", f"{ident} z_range_cm is not a two-number interval")
        else:
            z0, z1 = as_float(z_range[0]), as_float(z_range[1])
            if z0 is None or z1 is None or not math.isfinite(z0) or not math.isfinite(z1):
                _fails(failures, "G-35", f"{ident} z_range_cm is not finite")
            elif not z1 > z0:
                _fails(failures, "G-35", f"{ident} z_range_cm {z_range} is not z1 > z0")
        if element.get("kind") not in ELEMENT_KINDS:
            _fails(failures, "G-35", f"{ident} kind {element.get('kind')!r} is not in the vocabulary")

    # -- G-36 provenance --------------------------------------------------- #
    origins = document.get("origins") if isinstance(document.get("origins"), dict) else {}
    leaves = collect_leaves(document)
    leaf_set = set(leaves)
    for entry in sorted(origins):
        found, _ = resolve(document, entry)
        if not found:
            _fails(failures, "G-36", f"origins entry {entry} does not resolve in massing.json")
            continue
        record = origins[entry]
        if not isinstance(record, dict):
            _fails(failures, "G-36", f"origins entry {entry} is not an object")
            continue
        ledger = ASSUMED_LEAVES.get(entry)
        if record.get("origin") != "derived":
            # The documented exception, exactly as G-64 scopes it for
            # components_registry.json: a value nothing in dimensions.json
            # dimensions is `assumed` with a ledger ref, never `derived`.
            if ledger is not None and record.get("origin") == "assumed":
                if record.get("origin_ref") != ledger:
                    _fails(
                        failures,
                        "G-36",
                        f"{entry} is origin=assumed with origin_ref "
                        f"{record.get('origin_ref')!r}; the declared ledger entry is {ledger!r}",
                    )
                continue
            _fails(
                failures,
                "G-36",
                f"{entry} has origin {record.get('origin')!r}; every massing geometry origin is "
                f"derived, and the only exception is {sorted(ASSUMED_LEAVES)}",
            )
            continue
        derives_from = record.get("derives_from")
        if not isinstance(derives_from, list) or not derives_from:
            _fails(failures, "G-36", f"{entry} has no non-empty derives_from")
            continue
        for path in derives_from:
            if not resolve(dimensions, str(path))[0] and not resolve(document, str(path))[0]:
                _fails(
                    failures,
                    "G-36",
                    f"{entry} derives_from {path!r} resolves in neither dimensions.json "
                    "nor massing.json",
                )
    for leaf in leaves:
        holders = [e for e in origins if covers(e, leaf)]
        if not holders:
            _fails(failures, "G-36", f"leaf {leaf} has no origins entry")
        elif len(holders) > 1:
            _fails(failures, "G-36", f"leaf {leaf} is covered by {holders}")
    for entry in origins:
        if entry not in leaf_set and not any(covers(entry, leaf) for leaf in leaf_set):
            _fails(failures, "G-36", f"origins entry {entry} covers no leaf")
    for path in document.get("origin_inputs") or []:
        if not resolve(dimensions, str(path))[0]:
            _fails(failures, "G-36", f"origin_inputs path {path!r} does not resolve in dimensions.json")

    # -- G-37 storey chain ------------------------------------------------- #
    levels = dimensions.get("levels") or []
    storey_indices = {s.get("index") for s in stores}
    for position, store in enumerate(stores):
        if position >= len(levels):
            _fails(failures, "G-37", f"storeys[{position}] has no level to mirror")
            continue
        level = levels[position]
        if store.get("index") != level.get("index"):
            _fails(
                failures,
                "G-37",
                f"storeys[{position}].index is {store.get('index')!r}, not "
                f"levels[{position}].index {level.get('index')!r}",
            )
        if store.get("level_ref") != level.get("id"):
            _fails(failures, "G-37", f"storeys[{position}].level_ref is not levels[{position}].id")
        if not close(store.get("elevation_cm"), level.get("elevation_cm")):
            _fails(failures, "G-37", f"storeys[{position}].elevation_cm disagrees with the level")
        if not close(store.get("height_cm"), level.get("height_cm")):
            _fails(failures, "G-37", f"storeys[{position}].height_cm disagrees with the level")
        expected = [q(level["elevation_cm"]), q(level["elevation_cm"] + level["height_cm"])]
        z_range = store.get("z_range_cm") or []
        if len(z_range) != 2 or not close(z_range[0], expected[0]) or not close(z_range[1], expected[1]):
            _fails(failures, "G-37", f"storeys[{position}].z_range_cm is not the storey volume")
        index = store.get("index")
        slab = by_id.get(store.get("slab_ref"))
        if slab is None or slab.get("kind") != "slab" or slab.get("storey_index") != index:
            _fails(failures, "G-37", f"storeys[{position}].slab_ref is not a slab of this storey")
        for key, kind in (("column_refs", "column"), ("core_refs", "core_wall")):
            for ref in store.get(key) or []:
                target = by_id.get(ref)
                if target is None or target.get("kind") != kind or target.get("storey_index") != index:
                    _fails(
                        failures,
                        "G-37",
                        f"storeys[{position}].{key} names {ref}, which is not a {kind} "
                        f"of storey {index}",
                    )

    # -- G-38 element-to-dimension agreement ------------------------------ #
    plate_by_level = {p.get("level_index"): p for p in dimensions.get("floor_plates") or []}
    roof = dimensions.get("roof") or {}
    deck = q(roof.get("deck_level_cm", 0.0))
    deck_thickness = q(roof.get("deck_thickness_cm", 0.0))
    parapet_height = q(roof.get("parapet_height_cm", 0.0))
    parapet_thickness = q(roof.get("parapet_thickness_cm", 0.0))
    site_rect = rect_of(
        (dimensions.get("site") or {}).get("footprint_cm"),
        "site.footprint_cm",
        (dimensions.get("site") or {}).get("footprint_kind"),
        "(self-check)",
    )
    core_rect = rect_of(
        (dimensions.get("core") or {}).get("footprint_cm"),
        "core.footprint_cm",
        (dimensions.get("core") or {}).get("footprint_kind"),
        "(self-check)",
    )
    core_inset = inset(core_rect, q((dimensions.get("core") or {}).get("wall_thickness_cm", 20.0)))
    expected_bands = dict(parapet_bands(site_rect, parapet_thickness))

    for element in elements:
        ident = str(element.get("id"))
        kind = element.get("kind")
        index = element.get("storey_index")
        if index is not None and index not in storey_indices:
            _fails(failures, "G-38", f"{ident} storey_index {index!r} is not in storeys[]")
        z_range = [as_float(v) for v in (element.get("z_range_cm") or [])]
        level = None
        if index is not None:
            level = next((lv for lv in levels if lv.get("index") == index), None)
            if level is None:
                _fails(failures, "G-38", f"{ident} storey_index {index!r} is not a level index")
                continue
        thickness = q((plate_by_level.get(index) or {}).get("thickness_cm", 0.0))
        if kind == "slab":
            expected = [q(level["elevation_cm"] - thickness), q(level["elevation_cm"])]
        elif kind == "column":
            expected = [
                q(level["elevation_cm"] - thickness),
                q(level["elevation_cm"] + level["height_cm"]),
            ]
        elif kind == "roof_deck":
            expected = [q(deck - deck_thickness), deck]
        elif kind == "parapet":
            expected = [deck, q(deck + parapet_height)]
        elif kind == "core_wall":
            expected = [q(level["elevation_cm"]), q(level["elevation_cm"] + level["height_cm"])]
        elif kind == "facade_wall":
            # P6 clause: full storey height, tol linear_cm.
            expected = [q(level["elevation_cm"]), q(level["elevation_cm"] + level["height_cm"])]
        elif kind == "plinth":
            expected = None  # no plinth rule in G-38; nothing to recompute
        else:
            expected = None
        if expected is not None and len(z_range) == 2:
            if not close(z_range[0], expected[0]) or not close(z_range[1], expected[1]):
                _fails(
                    failures,
                    "G-38",
                    f"{ident} ({kind}) z_range_cm {element.get('z_range_cm')} != "
                    f"G-38's {[num(v) for v in expected]}",
                )
        profile = expand_rect_ring(element.get("profile_cm"), "polygon")
        if kind == "core_wall" and len(profile) == 4:
            if not all(close(a, b) for a, b in zip(
                [profile[0][0], profile[0][1], profile[2][0], profile[2][1]],
                [core_inset[0], core_inset[1], core_inset[2], core_inset[3]],
            )):
                _fails(
                    failures,
                    "G-38",
                    f"{ident} core_wall profile is not core.footprint_cm inset by "
                    "core.wall_thickness_cm",
                )

    # 07 section 8.1.1: the parapet of a rectangular deck is four bands, one per
    # straight side, and together they are the whole annulus.
    parapets = [e for e in elements if e.get("kind") == "parapet"]
    if parapets:
        if len(parapets) != len(expected_bands):
            _fails(
                failures,
                "G-38",
                f"{len(parapets)} parapet elements; a rectangular deck's parapet is "
                f"{len(expected_bands)} bands, one per straight side (07 section 8.1.1)",
            )
        seen_sides: list[str] = []
        for element in parapets:
            profile = expand_rect_ring(element.get("profile_cm"), "polygon")
            if len(profile) != 4:
                continue
            rect = (
                min(q(p[0]) for p in profile),
                min(q(p[1]) for p in profile),
                max(q(p[0]) for p in profile),
                max(q(p[1]) for p in profile),
            )
            match = [side for side, band in expected_bands.items() if all(close(a, b) for a, b in zip(rect, band))]
            if not match:
                _fails(
                    failures,
                    "G-38",
                    f"{element.get('id')} is a parapet band at {rect}, which is not one of "
                    f"the four deck-edge bands {[list(b) for b in expected_bands.values()]}",
                )
            else:
                seen_sides.append(match[0])
        if sorted(seen_sides) != sorted(expected_bands):
            _fails(
                failures,
                "G-38",
                f"parapet bands cover sides {sorted(seen_sides)}, expected "
                f"{sorted(expected_bands)}: the annulus is not partitioned exactly once",
            )

    # P6, second G-38 clause: every (facades[i].id, levels[j].index) pair has
    # exactly one facade_wall whose band spans that facade's length_cm. A missing
    # wall is a FAIL, not a gap -- an opening cut with no host is a silent hole.
    wall_thickness = as_float((document.get("defaults") or {}).get("facade_wall_thickness_cm"))
    dimension_facades = [f for f in (dimensions.get("facades") or []) if isinstance(f, dict)]
    toward = ((site_rect[0] + site_rect[2]) / 2.0, (site_rect[1] + site_rect[3]) / 2.0)
    if wall_thickness is None:
        _fails(
            failures,
            "G-38",
            f"{FACADE_WALL_THICKNESS_LEAF} is missing; the facade_wall bands cannot be "
            "checked against the facade runs",
        )
    elif not dimension_facades:
        _fails(failures, "G-38", "dimensions.json declares no facades[]; nothing to reconcile")
    else:
        for f_position, facade in enumerate(dimension_facades):
            facade_id = str(facade.get("id", f"facades[{f_position}]"))
            band = facade_wall_band(
                facade.get("start_corner_cm"),
                facade.get("end_corner_cm"),
                wall_thickness,
                toward,
                facade_id,
            )
            span = math.hypot(
                (as_float(facade.get("end_corner_cm")[0]) or 0.0)
                - (as_float(facade.get("start_corner_cm")[0]) or 0.0),
                (as_float(facade.get("end_corner_cm")[1]) or 0.0)
                - (as_float(facade.get("start_corner_cm")[1]) or 0.0),
            )
            declared = as_float(facade.get("length_cm"))
            if declared is not None and not close(span, declared):
                _fails(
                    failures,
                    "G-38",
                    f"facades[{f_position}] ({facade_id}) run is {num(span)} cm long but "
                    f"declares length_cm {num(declared)}; the band cannot span it",
                )
            for level in levels:
                index = level.get("index")
                matches = []
                for element in elements:
                    if element.get("kind") != "facade_wall" or element.get("storey_index") != index:
                        continue
                    profile = expand_rect_ring(element.get("profile_cm"), "polygon")
                    if len(profile) != 4:
                        continue
                    rect = (
                        min(q(p[0]) for p in profile),
                        min(q(p[1]) for p in profile),
                        max(q(p[0]) for p in profile),
                        max(q(p[1]) for p in profile),
                    )
                    if all(close(a, b) for a, b in zip(rect, band)):
                        matches.append(str(element.get("id")))
                if len(matches) != 1:
                    _fails(
                        failures,
                        "G-38",
                        f"({facade_id}, level {index!r}) has {len(matches)} facade_wall "
                        f"element(s) banding {list(band)}; G-38 requires exactly one, so the "
                        "envelope is total in both directions"
                        + (f" (found {matches})" if matches else ""),
                    )

    # The model's top must be building.overall_height_cm (G-38 + G-20), so the old
    # reading -- deck on top of its thickness, parapet above that -- cannot return.
    overall = as_float((dimensions.get("building") or {}).get("overall_height_cm"))
    tops: list[float | None] = []
    for element in elements:
        z_range = element.get("z_range_cm")
        if isinstance(z_range, list) and len(z_range) > 1:
            tops.append(as_float(z_range[1]))
    pad_tops = [
        as_float(part.get("z_range_cm", [None, None])[1])
        for _, part in site_pad_nodes(document)
    ]
    model_top = max([t for t in tops + pad_tops if t is not None] or [None])
    if overall is None:
        _fails(failures, "G-38", "building.overall_height_cm is missing; the model top cannot be checked")
    elif model_top is None:
        _fails(failures, "G-38", "no element carries a top Z; the model top cannot be checked")
    elif not close(model_top, overall):
        _fails(
            failures,
            "G-38",
            f"model top {num(model_top)} != building.overall_height_cm {num(overall)}; "
            "G-38 requires the parapet to run from roof.deck_level_cm to "
            "deck_level_cm + parapet_height_cm",
        )

    spans = (dimensions.get("core") or {}).get("spans_level_indices") or []
    for spanned in spans:
        if not any(
            e.get("kind") == "core_wall" and e.get("storey_index") == spanned for e in elements
        ):
            _fails(
                failures,
                "G-38",
                f"level {spanned} is named by core.spans_level_indices but has no core_wall",
            )

    # -- G-39 layer vocabulary --------------------------------------------- #
    site_pad = document.get("site_pad") if isinstance(document.get("site_pad"), dict) else {}
    if site_pad.get("layer") != SITE_LAYER:
        _fails(failures, "G-39", f"site_pad.layer is {site_pad.get('layer')!r}, not {SITE_LAYER!r}")
    for element in elements:
        layer = element.get("layer")
        if layer not in LAYER_VOCABULARY:
            _fails(failures, "G-39", f"{element.get('id')} layer {layer!r} is not in the vocabulary")
        elif layer != KIND_LAYER.get(str(element.get("kind"))):
            _fails(
                failures,
                "G-39",
                f"{element.get('id')} is a {element.get('kind')} on {layer!r}; 07 section "
                f"8.1.2 fixes that kind to {KIND_LAYER.get(str(element.get('kind')))}",
            )
    for group in grouping:
        if group.get("layer") != SCENE_LAYER:
            _fails(failures, "G-39", f"{group.get('id')} layer {group.get('layer')!r}, not {SCENE_LAYER!r}")
        if group.get("kind") not in GROUP_KINDS:
            _fails(failures, "G-39", f"{group.get('id')} kind {group.get('kind')!r} is not in the vocabulary")

    # -- G-40 grouping completeness ---------------------------------------- #
    owner: dict[str, str] = {}
    for group in grouping:
        members = group.get("element_ids")
        if not isinstance(members, list) or not members:
            _fails(failures, "G-40", f"{group.get('id')} has no element_ids; a group needs >= 1")
            continue
        for ref in members:
            if ref not in by_id:
                _fails(failures, "G-40", f"{group.get('id')} names {ref}, which is not an element")
            elif ref in owner:
                _fails(failures, "G-40", f"{ref} appears in two groups ({owner[ref]}, {group.get('id')})")
            else:
                owner[ref] = str(group.get("id"))
    for element in elements:
        if element.get("id") not in owner:
            _fails(failures, "G-40", f"{element.get('id')} is in no group")
    for group in grouping:
        members = [by_id[ref] for ref in group.get("element_ids") or [] if ref in by_id]
        if not members:
            continue
        x0, x1, y0, y1 = group_bounds(members)
        z0 = min(q(e["z_range_cm"][0]) for e in members)
        pivot = group.get("parent_pivot_cm") or []
        expected = [q((x0 + x1) / 2.0), q((y0 + y1) / 2.0), z0]
        if len(pivot) != 3 or not all(close(a, b) for a, b in zip(pivot, expected)):
            _fails(
                failures,
                "G-40",
                f"{group.get('id')} parent_pivot_cm {pivot} is not the group bbox centre "
                f"in XY and its minimum Z {[num(v) for v in expected]}",
            )
    return failures


# --------------------------------------------------------------------------- #
# Serialisation
# --------------------------------------------------------------------------- #


def serialize(document: dict[str, Any]) -> str:
    try:
        body = json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False)
    except ValueError as exc:  # NaN / Infinity
        raise Refusal(f"refusing to write: massing.json is not strict JSON -- {exc} (07 G-7).") from exc
    return body + "\n"


def write_bytes(path: Path, text: str) -> None:
    data = text.encode("utf-8")
    if b"\r" in data:
        raise Refusal(f"refusing to write {path}: the payload contains CR (07 G-7).")
    if not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise Refusal(f"refusing to write {path}: it must end with exactly one LF (07 G-7).")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def verify_script(document: dict[str, Any], script: str) -> None:
    """The emitted script must actually build every solid the spec declares.

    A spec value with no node is a hole nobody would notice until the scene was
    read back, so the script is checked against the document rather than trusted.
    """
    function = build_fn_name(document["project"])
    expected: list[str] = [name for name, _ in site_pad_nodes(document)]
    expected += [node_name(e["id"]) for e in document["elements"]]
    expected += [node_name(g["id"]) for g in document["grouping"]]
    for variable in expected:
        if f"local {variable} = " not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: no node is created for {variable}. Every "
                "site_pad part, element and group must exist in the scene."
            )
    for variable in expected:
        if f'local prev_{variable} = getNodeByName "{variable}"' not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {variable} has no explicit-local "
                "delete guard, so a second fileIn would duplicate it."
            )
        if f"if prev_{variable} != undefined do ( delete prev_{variable} )" not in script:
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: {variable} is looked up but never "
                "deleted, so a second fileIn would duplicate it."
            )
    verify_script_shape(document, script, function)
    # 11 section 3.1 N1: a node name is the spec id with every dash turned into an
    # underscore, because it is pasted into MAXScript and into typed-tool arguments
    # and `-` reads as subtraction there.
    emitted_names = re.findall(r"\.name\s*=\s*\"([^\"]*)\"", script) + re.findall(
        r"\bname\s*:\s*\"([^\"]*)\"", script
    )
    if not emitted_names:
        raise Refusal(f"refusing to write {OUT_MS_NAME}: it names no node at all.")
    for value in emitted_names:
        if not NODE_NAME_RE.match(value):
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: node name {value!r} is not "
                "MAXScript-identifier-safe. 11 section 3.1 N1 requires letters, digits and "
                "`_` only, and gives the mapping EL-001 -> EL_001."
            )
    if len(set(emitted_names)) != len(emitted_names):
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: two nodes share one name; a node name is "
            "derived from its spec id and ids are unique."
        )
    if "LayerManager" in script.replace("LayerManager.newLayerFromName", ""):
        raise Refusal(
            f"refusing to write {OUT_MS_NAME}: it uses a LayerManager call other than "
            "newLayerFromName. Layer is data at this stage (07 section 8.1.3)."
        )
    forbidden = (".layer =", ".setLayer(", "setProperty #layer", "node.layer")
    for line in script.split("\n"):
        if any(token in line for token in forbidden):
            raise Refusal(
                f"refusing to write {OUT_MS_NAME}: it assigns a layer to a node "
                f"({line.strip()!r}). An object's layer cannot be assigned from "
                "MAXScript in Max 2026, so layer stays a data column (07 section 8.1.3)."
            )


def verify_script_shape(document: dict[str, Any], script: str, function: str) -> None:
    """Structural test: the emitted file must be a runnable one-function script.

    Verified by execution (2026-10-04): ``local`` at the top level of a
    ``fileIn``-ed script is a compile error, so the whole body must sit inside an
    ``fn``. This checks the shape without a MAXScript interpreter.
    """
    lines = script.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    header = f"/* build_spec.py --stage massing | project {document['project']} | DO NOT EDIT */"

    def bad(reason: str) -> Refusal:
        return Refusal(
            f"refusing to write {OUT_MS_NAME}: {reason}. A local declaration at the top "
            "level of a fileIn-ed script is a compile error (verified 2026-10-04), so "
            "the whole body must live inside one fn that is called once."
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
    # Executed live 2026-10-04: the parenthesised one-liner guard throws
    # "Type error: Call needs function or class, got: undefined" when the node is
    # absent, and only survives by accident inside fileIn. Reject it outright.
    if re.search(r"if\s*\(\s*getNodeByName", script):
        raise bad(
            "it uses the parenthesised one-liner delete guard "
            "`if (getNodeByName ...)`, which throws when the node does not exist; "
            "bind the lookup to a local first"
        )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def summarise(
    document: dict[str, Any], dimensions: dict[str, Any], model: Model, layers: Sequence[str]
) -> str:
    elements = document["elements"]
    grouping = document["grouping"]
    by_kind: dict[str, int] = {}
    for element in elements:
        by_kind[element["kind"]] = by_kind.get(element["kind"], 0) + 1
    by_group: dict[str, int] = {}
    for group in grouping:
        by_group[group["kind"]] = by_group.get(group["kind"], 0) + len(group["element_ids"])
    site_pad = document["site_pad"]
    parts = [name for name in SITE_PAD_PARTS if site_pad.get(name) is not None]
    z_values = [value for element in elements for value in element["z_range_cm"]] + [
        value for _, part in site_pad_nodes(document) for value in part["z_range_cm"]
    ]
    model_min_z, model_top = min(z_values), max(z_values)
    overall = (dimensions.get("building") or {}).get("overall_height_cm")
    lines = [
        "build_spec.py --stage massing",
        f"  project   {document['project']}  (source: {UPSTREAM_NAME}, status locked)",
        f"  elements  {len(elements)}  "
        + ", ".join(f"{kind} {by_kind[kind]}" for kind in ELEMENT_KINDS if kind in by_kind),
        f"  groups    {len(grouping)}  "
        + ", ".join(f"{kind} {by_group[kind]}" for kind in GROUP_KINDS if kind in by_group),
        f"  site_pad  {len(parts)} part(s): "
        + ", ".join(f"{name} -> {SITE_PAD_NODE[name]}" for name in parts)
        + "; paving and kerb are null (dimensions.json has no key for either)",
        "  plinth    not emitted: dimensions.json declares no plinth dimension, and a "
        "plinth built from an invented one is an invented dimension",
        f"  columns   skipped {len(model.skipped_columns)} inside core.footprint_cm"
        + (": " + "; ".join(model.skipped_columns) if model.skipped_columns else ""),
        f"  parapet   {by_kind.get('parapet', 0)} bands, one per straight side "
        "(07 section 8.1.1: a ring with a hole is not expressible)",
        f"  model Z   {num(model_min_z)} .. {num(model_top)} "
        f"(building.overall_height_cm = {num(overall)})",
        f"  layers    {len(layers)} created: {', '.join(layers)} (data only; no node is "
        "assigned to a layer)",
        "  self-check G-34..G-40 pass",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build massing.json and massing.ms from a locked dimensions.json "
            "(07 section 8.1, invariants G-34..G-40)."
        )
    )
    parser.add_argument("--stage", required=True, help=f"stage to build; supported: {', '.join(STAGES)}")
    parser.add_argument("--in", dest="in_dir", required=True, type=Path, help="specs directory to read")
    parser.add_argument("--out", dest="out_dir", default=None, type=Path, help="output directory (default: --in)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="print a machine-readable summary")
    args = parser.parse_args(argv)

    if args.stage not in STAGES:
        print(
            f"error: unsupported stage {args.stage!r}. This builder supports: "
            f"{', '.join(STAGES)}.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    specs_dir: Path = args.in_dir
    out_dir: Path = args.out_dir if args.out_dir is not None else specs_dir

    try:
        dimensions = load_locked_dimensions(specs_dir)
        document, model = build_massing(dimensions)
        text = serialize(document)

        # Check the bytes, not the intention: parse the exact payload again and
        # run G-34..G-40 against it before anything reaches the disk.
        checked = strict_loads(text)
        failures = self_check(checked, dimensions, specs_dir)
        if failures:
            raise Refusal(
                "refusing to write: the self-check failed "
                f"{len(failures)} invariant(s).\n  - " + "\n  - ".join(failures[:20])
            )

        layers = referenced_layers(checked)
        script = render_ms(checked, layers)
        verify_script(checked, script)
        json_path = out_dir / OUT_JSON_NAME
        ms_path = out_dir / OUT_MS_NAME
        write_bytes(json_path, text)
        write_bytes(ms_path, script)
    except Refusal as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSAL

    elements = checked["elements"]
    grouping = checked["grouping"]
    site_pad = checked["site_pad"]
    parts = [name for name in SITE_PAD_PARTS if site_pad.get(name) is not None]
    by_kind: dict[str, int] = {}
    for element in elements:
        by_kind[element["kind"]] = by_kind.get(element["kind"], 0) + 1
    z_values = [
        value
        for element in elements
        for value in element["z_range_cm"]
    ] + [
        value
        for _, part in site_pad_nodes(checked)
        for value in part["z_range_cm"]
    ]
    model_min_z, model_top = min(z_values), max(z_values)
    overall = dimensions["building"]["overall_height_cm"]
    if args.as_json:
        summary = {
            "builder": "scripts/build_spec.py",
            "stage": args.stage,
            "project": checked["project"],
            "spec": checked["spec"],
            "read": [str(specs_dir / UPSTREAM_NAME)],
            "wrote": [str(json_path), str(ms_path)],
            "element_count": len(elements),
            "element_ids": [element["id"] for element in elements],
            "elements_by_kind": {kind: by_kind[kind] for kind in ELEMENT_KINDS if kind in by_kind},
            "parapet_bands": [
                {"id": element_id, "side": side}
                for element_id, side in model.parapet_sides
            ],
            "group_count": len(grouping),
            "group_ids": [group["id"] for group in grouping],
            "group_pivots_cm": {group["id"]: group["parent_pivot_cm"] for group in grouping},
            "site_pad_parts": parts,
            "site_pad_nodes": [name for name, _ in site_pad_nodes(checked)],
            "model_min_z_cm": q(model_min_z),
            "model_top_z_cm": q(model_top),
            "overall_height_cm": q(overall),
            "plinth": {
                "emitted": False,
                "reason": "dimensions.json declares no plinth dimension; a plinth needs one",
            },
            "columns_skipped_in_core": model.skipped_columns,
            "layers_created": layers,
            "layer_application": "data only; massing.ms assigns no layer to any node",
            "origin_inputs": len(checked["origin_inputs"]),
            "origins": len(checked["origins"]),
            "self_check": {f"G-{number}": "pass" for number in range(34, 41)},
            "exit_code": EXIT_OK,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(summarise(checked, dimensions, model, layers))
        print(f"  wrote    {json_path}")
        print(f"  wrote    {ms_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
