#!/usr/bin/env python3
"""Stage `assembly`: the locked P5/P3 inputs -> assembly.json + assembly.ms.

The two artefacts P6 owns, in the shape ``references/07-spec-grammar.md`` section 8.5
defines and invariants G-71..G-81 (section 9.9) accept::

    <out>/assembly.json   the spec, strict JSON, UTF-8 no BOM, LF, one final newline
    <out>/assembly.ms     geometry only -- no layer code (07 section 8.5, G-79)

Usage
-----
    python scripts/place_components.py --in <specs_dir> --out <out_dir>
                                       [--stage assembly] [--json] [--build] [--allow-draft]

Exit codes
----------
    0   built, and the self-check passed G-71..G-81 against the bytes on disk
    1   a refusal: the lock gate, a missing upstream file, a shape the builder cannot
        honour, or a self-check failure. The message names the file, the id and the rule.
    2   usage error

DETERMINISM (07 S-5)
--------------------
The same locked inputs must produce byte-identical output. Nothing here reads a clock
or a random source: ids are allocated in a fixed order, prototypes are emitted in sorted
``component_id`` order, every number goes through ``q()`` (6 decimals, negative zero
normalised), ``origins`` is emitted in document order and ``origin_inputs`` is a sorted
set. The only timestamp is ``source.recorded_at``, copied verbatim from
``dimensions.json`` -- 07 section 3.2 allows exactly that one. ``scatter[].seed`` is a
**fixed literal in the spec**, not a draw: that is the whole P0 determinism claim, and a
builder that generated it would make every rebuild a different scene.

WHAT THIS BUILDER READS
-----------------------
``components_registry.json`` (what a panel is), ``world_table.csv`` (where every instance
goes), ``massing.json`` (the envelope to cut) and ``dimensions.json`` (the openings and
the facade runs). All four must be ``locked`` unless ``--allow-draft``; ``--build``
refuses a draft outright, which is the P2/P3 convention. The *emitted*
``assembly.json`` is ``locked``, and ``--build`` re-checks that on the bytes on disk.

DECISIONS THIS BUILDER MAKES, AND WHY
--------------------------------------
* **The world table is copied, never recomputed.** ``placements[].position_cm`` and
  ``rot_z_deg`` are read verbatim off ``world_table.csv`` (G-73). P5 measured that this
  table's ``rot_z_deg`` is ``atan2(dy, dx)`` of the run, *not*
  ``dimensions.facades[].direction_deg`` -- ``F-S`` and ``F-N`` both run along +X and
  carry 180 and 0 -- so recomputing the rotation here would reintroduce that bug.

* **``u_range_cm`` is facade-local, and so is ``v_range_cm``.** Both are the frame
  ``facade_grids.json`` is written in: ``u`` from ``facades[].start_corner_cm``, ``v``
  from the level base. That is why ``v_range_cm`` is ``[sill_cm, head_cm]`` literally:
  the host wall's own local ``v`` extent is ``[0, level.height_cm]``, so a level-1
  opening whose head is 270 cm sits inside its wall without the 420 cm elevation the
  *world* frame would demand. The builder converts once, at the end, when it writes each
  cell's plan rectangle. Mixing the two frames is how P5's glass-sliver defect happened.

* **``host_ref`` is resolved geometrically, not by a key.** The ``(facade, level)`` ->
  ``facade_wall`` mapping is recomputed from the run's two corners, its inward side and
  ``massing.json``'s own assumed thickness, then matched against each ``facade_wall``
  element's plan rectangle -- the identical computation G-38 clause 2 performs. A key
  would let ``assembly.json`` agree with a ``massing.json`` that has drifted.

* **``depth_cm`` is the wall thickness plus one panel joint.** ``20 + 2 = 22 cm``. It was
  written for a cutter that stands proud of each wall face, and it is **no longer read by
  the emitted geometry** -- ``wall_cells[]`` tiles the wall with solids, so the cells span
  the wall's own thickness. ``depth_cm`` stays in ``assembly.json`` as the **declaration**
  of the opening, which is what ``opening_cuts[]`` is for. ``panel_joint_cm`` is P5's
  ``A-024`` carried forward, not a new assumption, which is what keeps P6's assumed count
  at one (``A-025``).

* **One prototype per distinct component, then instances.** The 136 placements resolve
  to **29** distinct ``component_id`` values, so 29 prototype boxes are created and every
  placement is a copy that shares its prototype's ``baseObject``. The route is the one
  executed live on 2026-10-05: ``n = copy proto`` then ``n.baseObject = proto.baseObject``.
  ``setCopyMode`` **does not exist** in this build.

* **Rotation is ``quat``.** ``n.rotation = quat <degrees> [0,0,1]``. ``rotationZ``,
  ``rotationX``, ``rotationY``, ``matrix3`` and ``angle`` **do not exist** (P5).

* **``node.pos`` on a ``Box`` puts the BASE at ``pos.z``.** Verified live, and still true
  after ``copy``, after ``baseObject =`` and after rotation. A panel centred at ``cz`` is
  written ``pos.z = cz - height/2``; the same correction applies to every wall cell.
  Getting this wrong put every P5 panel one full height too high.

* **No modifier is ever attached, so the 20-modifier freeze cannot be reached from here.**
  Executed live on 2026-10-05: five and ten modifiers on one node are clean, **twenty
  froze Max on the main thread until the machine rebooted**. The stage that emitted cut
  passes of five was the Boolean design, which was then measured unusable and replaced by
  wall tiling (see §"Wall tiling"). What survives is the *rule* for any later stage that
  does attach modifiers: build stacks incrementally, five per call, never more than ten on
  one node (G-81).

* **Re-run policy: delete-then-create, by spec-derived name, twice.** Every node name
  comes from a spec id, so before creating anything the function deletes any node already
  holding that name -- **twice**, because deleting a base object does not delete its
  instances. The delete list is collected and applied by name; ``for o in objects do
  delete o`` silently skips entries (measured at P5: 24 orphans left behind).

* **The host walls are neither deleted nor created.** They belong to ``massing.ms``, and
  ``assembly.ms`` throws naming the missing one if they are absent. It attaches nothing to
  them, so a second ``fileIn`` converges instead of doubling a stack. The hosts are
  checked for an empty modifier stack on the way through (G-81): a non-empty one means
  another stage left something behind, since this stage's own output is modifier-free.

* **No layer code, anywhere (G-79).** ``LayerManager`` in this build exposes only
  ``newLayerFromName`` / ``getLayerFromName`` / ``getLayer``, and ``node.layer`` throws
  ``Property is read-only: layer`` for a string, an index and a ``LayerProperties``. Nine
  routes were ruled out; layer application is a human action in the Layer dialog.
  ``layer_map`` stays **data**. A builder that emits a layer assignment is a build FAIL,
  not a silent no-op.

* **No bare literal sub-object index.** ``G-56``'s rule generalises: every index is
  bound to a variable in the statement before it is used, so a stack reorder cannot
  silently retarget a modifier.

* **The census throws (G-80).** After placing, the function counts what it created and
  throws on any mismatch against the table. A build that merely completes is not proof
  that the numbers are right, and the count is the cheapest place a mistake shows up.
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

try:
    from scripts.scene_units import emit_unit_preamble, scene_length_expr, scene_point_expr
except ImportError:
    from scene_units import emit_unit_preamble, scene_length_expr, scene_point_expr

# --------------------------------------------------------------------------- #
# Constants declared by references/07-spec-grammar.md and the P6 contract
# --------------------------------------------------------------------------- #

SUPPORTED_SCHEMA_MAJOR = 1
SUPPORTED_SCHEMA_MINORS: tuple[int, ...] = (0, 1)
SCHEMA_VERSION = "1.0"

STAGES: tuple[str, ...] = ("assembly",)
DEFAULT_STAGE = "assembly"

DIMENSIONS_NAME = "dimensions.json"
MASSING_NAME = "massing.json"
REGISTRY_NAME = "components_registry.json"
WORLD_CSV_NAME = "world_table.csv"
OUT_JSON_NAME = "assembly.json"
OUT_MS_NAME = "assembly.ms"

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
FACADE_LAYER = "05_FACADE"
SCATTER_LAYER = "99_DEBUG"

#: 07 section 9.9 G-81 -- the measured modifier-stack ladder (2026-10-05).
MAX_MODIFIERS_PER_CALL = 5
MAX_MODIFIERS_PER_NODE = 10

#: 07 section 8.5 -- the only legal cut kind.
CUT_KINDS: tuple[str, ...] = ("difference",)

#: 07 section 8.5 -- the scatter seed range, closed (P0 determinism).
SEED_MIN = 1
SEED_MAX = 31337

#: The one scatter row this example ships, fixed rather than generated. See the module
#: docstring: a seed the builder drew would be a different scene on every run.
SCATTER_ID = "SCT-001"
SCATTER_TARGET_KIND = "roof_deck"
SCATTER_MODEL_KIND = "column"
SCATTER_SEED = 26010
SCATTER_INSTANCE_LIMIT = 60
SCATTER_DENSITY = 0.02
SCATTER_SCALE_FROM = 0.85
SCATTER_SCALE_TO = 1.15
SCATTER_ROT_FROM_DEG = -180.0
SCATTER_ROT_TO_DEG = 180.0

#: 07 section 8.5 ``defaults`` -- a guard rail, not a dimension. 2000 is more than an
#: order of magnitude above the 136 this project places, so a corrupt CSV cannot ask Max
#: for a million instances. Nothing geometric reads it; it is a refusal threshold.
INSTANCE_LIMIT_GUARD = 2000

PLACEMENT_ID_RE = re.compile(r"^PLC-\d{3}$")
CUT_ID_RE = re.compile(r"^CUT-\d{3}$")
SCATTER_ID_RE = re.compile(r"^SCT-\d{3}$")
ELEMENT_ID_RE = re.compile(r"^EL-\d{3}$")
COMPONENT_ID_RE = re.compile(r"^CMP-\d{3}$")
PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

#: 11 section 3.1 N1 -- a node name is pasted into emitted MAXScript and into typed-tool
#: arguments, and ``-`` reads as subtraction there, so it is the id with underscores.
NODE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

#: The Boolean modifier's difference index (0 union, 1 difference, 2 intersect), retained
#: only as a record of the design that wall tiling replaced. It was **never measured live**
#: and nothing reads it: the emitted script attaches zero modifiers. See §"Wall tiling".
BOOLEAN_DIFFERENCE_OPERATION = 1

#: 07 section 3.1 / G-9 -- keys outside the origins coverage rule.
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

RULES: tuple[str, ...] = tuple(f"G-{number}" for number in range(71, 84))

#: The four upstream files, in the order ``source.reference`` names them, which is also
#: the order the lock gate checks them in so a refusal names the first problem.
UPSTREAM_NAMES: tuple[str, ...] = (
    DIMENSIONS_NAME,
    MASSING_NAME,
    REGISTRY_NAME,
    WORLD_CSV_NAME,
)

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


def inum(value: Any) -> int:
    return int(round(float(value)))


def num(value: Any) -> str:
    """MAXScript literal for a spec number: 1800 -> '1800.0', 1372.5 -> '1372.5'."""
    number = q(value)
    if float(number).is_integer():
        return f"{int(number)}.0"
    return repr(float(number))


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return None if math.isnan(number) or math.isinf(number) else number
    if isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
        return None if math.isnan(number) or math.isinf(number) else number
    return None


def close(left: Any, right: Any, tolerance: float) -> bool:
    a = as_float(left)
    b = as_float(right)
    if a is None or b is None:
        return False
    return abs(a - b) <= tolerance


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


def node_name(spec_id: Any) -> str:
    """11 section 3.1 N1: the node name is the spec id with dashes replaced.

    ``PLC-001`` -> ``PLC_001``, ``CUT-016`` -> ``CUT_016``. Every name in either artefact
    goes through this one function, so the JSON name and the scene node name cannot
    disagree.
    """
    return str(spec_id).replace("-", "_")


def prototype_name(component_id: Any) -> str:
    """The one prototype node a distinct ``component_id`` gets: ``PROTO_CMP_008``."""
    return "PROTO_" + node_name(component_id)


def host_variable(element_id: Any) -> str:
    """The driver's local for a host wall: ``host_EL_014``, an identifier, not the spec id.

    11 section 3.1 N1 again: ``EL-014`` reads as ``EL - 014`` in an expression, so the local
    and the ``getNodeByName`` argument are both the id with underscores.
    """
    return "host_" + node_name(element_id)


def build_fn_name(project: Any) -> str:
    return "mcpAssemblyBuild_" + re.sub(r"[^A-Za-z0-9_]", "_", str(project))


def cell_node_name(host_id: Any, index: int) -> str:
    """``WAL_EL_014_C07`` -- a wall solid cell's node name (07 G-74, N1 again).

    A cell is not an ``EL-``/``CUT-``/``PLC-`` entity: it is a *solid piece of a wall*,
    which is why it gets its own prefix. The prefix is also the census hook -- the emitted
    script counts ``WAL_`` nodes rather than counting its own loop iterations, which is the
    defect that let G-80 report 16 committed cuts while the scene held none.
    """
    return f"WAL_{node_name(host_id)}_C{index:02d}"


def cell_id(host_id: Any, index: int) -> str:
    """``WAL-EL-014-C07`` -- the spec id; dashes are the spec form, underscores the node form."""
    return f"WAL-{node_name(host_id).replace('_', '-')}-C{index:02d}"


# --------------------------------------------------------------------------- #
# Origins coverage (07 G-9 machinery, so the coverage walk exists in one place)
# --------------------------------------------------------------------------- #


def is_origin_exempt_key(key: str) -> bool:
    return key in COVERAGE_EXEMPT_KEYS or key.endswith(COVERAGE_EXEMPT_SUFFIXES)


def collect_leaves(document: Any) -> list[str]:
    """Every leaf path that needs an ``origins`` entry, in file order (07 G-9)."""
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


# --------------------------------------------------------------------------- #
# Reading the upstream files
# --------------------------------------------------------------------------- #

WORLD_COLUMNS: tuple[str, ...] = (
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


def read_spec(specs_dir: Path, name: str) -> dict[str, Any]:
    path = specs_dir / name
    if not path.is_file():
        raise Refusal(
            f"refusing to build: {path} is missing. {OUT_JSON_NAME} is the last derived file in "
            "the chain and reads four inputs; a builder never invents an input (07 S-5)."
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Refusal(f"refusing to build: cannot read {path}: {exc}") from exc
    try:
        document = strict_loads(text)
    except (ValueError, json.JSONDecodeError) as exc:
        raise Refusal(f"refusing to build: {path} is not strict JSON -- {exc} (07 G-7).") from exc
    if not isinstance(document, dict):
        raise Refusal(f"refusing to build: {path} top level is not an object (07 G-1).")

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

    units = document.get("units")
    if not isinstance(units, dict) or units.get("length") != "cm" or units.get("angle") != "deg":
        raise Refusal(
            f"refusing to build: {path} units {units!r} are not cm/deg (07 section 2, G-5)."
        )

    return document


def require_locked(document: dict[str, Any], label: str, allow_draft: bool, build_gate: bool) -> None:
    """The P2/P3 lock gate (07 G-4), applied to the *inputs*.

    ``assembly.json`` is this builder's output, so what a consumer reads is
    ``massing.json`` and the registry: a builder must refuse to consume a draft of
    either, exactly as ``build_spec.py`` refuses a draft ``dimensions.json``.
    """
    status = document.get("status")
    if status == "locked":
        return
    if build_gate:
        raise Refusal(
            f"refusing to build: {label} has status {status!r}. --build enforces the 07 G-4 lock "
            "gate and a builder may not consume a file that is still a draft."
        )
    if allow_draft:
        return
    raise Refusal(
        f"refusing to build: {label} has status {status!r}. Pass --allow-draft to build against "
        "a draft input, or --build to make this refusal unconditional."
    )


def read_world_table(specs_dir: Path) -> list[dict[str, str]]:
    """Parse ``world_table.csv`` into data rows. The header is checked, not assumed.

    ``source_row`` in ``assembly.json`` is the **1-based data row index**, header excluded,
    and G-72 asserts the join against exactly this list, so both readers must agree on what
    a row is.
    """
    path = specs_dir / WORLD_CSV_NAME
    if not path.is_file():
        raise Refusal(
            f"refusing to build: {path} is missing. {OUT_JSON_NAME} resolves "
            f"{WORLD_CSV_NAME} one placement per data row; emit it with "
            "scripts/facade_tables.py --stage tables first."
        )
    text = path.read_text(encoding="utf-8")
    if "\r" in text:
        raise Refusal(f"refusing to build: {path} contains CR. The emitted CSVs are LF only.")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != ",".join(WORLD_COLUMNS):
        raise Refusal(
            f"refusing to build: {path} header is {(lines[0] if lines else '')!r}, expected "
            f"{','.join(WORLD_COLUMNS)!r} (07 G-70)."
        )
    rows: list[dict[str, str]] = []
    for number, line in enumerate(lines[1:], start=1):
        fields = line.split(",")
        if len(fields) != len(WORLD_COLUMNS):
            raise Refusal(
                f"refusing to build: {path} data row {number} has {len(fields)} fields for "
                f"{len(WORLD_COLUMNS)} columns (07 G-70)."
            )
        rows.append(dict(zip(WORLD_COLUMNS, fields)))
    return rows


# --------------------------------------------------------------------------- #
# Geometry: facade runs, inward normals, and the facade_wall envelope
# --------------------------------------------------------------------------- #


def run_unit_deg(start: Sequence[float], end: Sequence[float]) -> tuple[float, float]:
    """``(unit_x, unit_y)`` along the run, and nothing else."""
    sx, sy = as_float(start[0]), as_float(start[1])
    ex, ey = as_float(end[0]), as_float(end[1])
    if None in (sx, sy, ex, ey):
        raise Refusal("refusing to build: a facade run carries a non-numeric corner.")
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy)
    if length <= 0.0:
        raise Refusal(
            "refusing to build: a facade run has zero length, so its run unit -- and therefore "
            "every u_range_cm on it -- is undecidable (07 G-57)."
        )
    return dx / length, dy / length


def run_angle_deg(start: Sequence[float], end: Sequence[float]) -> float:
    """``atan2(dy, dx)`` in ``(-180, 180]`` -- the P5 run angle, never a facing label."""
    ux, uy = run_unit_deg(start, end)
    angle = math.degrees(math.atan2(uy, ux))
    return angle if angle > -180.0 else 180.0


def footprint_centre(dimensions: dict[str, Any]) -> tuple[float, float]:
    site = dimensions.get("site")
    if not isinstance(site, dict):
        raise Refusal("refusing to build: dimensions.json declares no site{} block.")
    ring = site.get("footprint_cm")
    if not isinstance(ring, list) or len(ring) < 3:
        raise Refusal(
            "refusing to build: dimensions.json site.footprint_cm is unusable, so the inward "
            "side of every facade run -- and therefore the facade_wall envelope -- is undecidable "
            "(07 G-38)."
        )
    points = [point for point in ring if isinstance(point, list) and len(point) == 2]
    xs = [as_float(point[0]) for point in points]
    ys = [as_float(point[1]) for point in points]
    if len(points) != len(ring) or any(value is None for value in xs + ys):
        raise Refusal("refusing to build: site.footprint_cm carries a non-2D or non-numeric vertex.")
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0


def inward_unit(
    start: Sequence[float], end: Sequence[float], toward: tuple[float, float]
) -> tuple[float, float]:
    """The side of the run that faces the footprint centre.

    "Inward" is decided by comparing both candidate offsets against the centre rather than
    by a winding convention: the four runs of a rectangle are not all wound the same way
    round the ring, so a left-of-direction rule bands two of the four outward. This is
    the same reasoning G-38 clause 2 uses.
    """
    ux, uy = run_unit_deg(start, end)
    nx, ny = -uy, ux
    sx, sy = as_float(start[0]), as_float(start[1])
    ex, ey = as_float(end[0]), as_float(end[1])
    mid = (sx + ex) / 2.0, (sy + ey) / 2.0
    if math.hypot(mid[0] + nx - toward[0], mid[1] + ny - toward[1]) > math.hypot(
        mid[0] - nx - toward[0], mid[1] - ny - toward[1]
    ):
        nx, ny = -nx, -ny
    return nx, ny


def _ring_rect(ring: Any) -> tuple[float, float, float, float] | None:
    if not isinstance(ring, list) or len(ring) < 4:
        return None
    points = [point for point in ring if isinstance(point, list) and len(point) == 2]
    if len(points) != len(ring):
        return None
    xs = [as_float(point[0]) for point in points]
    ys = [as_float(point[1]) for point in points]
    if any(value is None for value in xs + ys):
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def facade_wall_index(
    massing: dict[str, Any], dimensions: dict[str, Any], toward: tuple[float, float]
) -> tuple[dict[tuple[str, int], dict], float]:
    """``(facade id, level_index) -> the one facade_wall element banding that run``.

    The match is geometric: the band is recomputed from the run's two corners, its inward
    side and ``massing.json``'s own assumed thickness, then compared with each
    ``facade_wall`` element's plan rectangle. Nothing here trusts a key, because a key
    would let ``assembly.json`` and a drifted ``massing.json`` agree with each other.
    """
    block = massing.get("defaults")
    thickness = as_float(block.get("facade_wall_thickness_cm")) if isinstance(block, dict) else None
    if thickness is None or thickness <= 0.0:
        raise Refusal(
            "refusing to build: massing.json declares no positive "
            "defaults.facade_wall_thickness_cm, so the envelope to cut is undecidable "
            "(07 G-38, ledger A-025)."
        )
    walls: dict[tuple[str, int], dict] = {}
    for facade in dimensions.get("facades") or []:
        if not isinstance(facade, dict):
            continue
        facade_id = facade.get("id")
        start = facade.get("start_corner_cm")
        end = facade.get("end_corner_cm")
        if (
            not isinstance(facade_id, str)
            or not isinstance(start, list)
            or not isinstance(end, list)
            or len(start) != 2
            or len(end) != 2
        ):
            continue
        sx, sy = as_float(start[0]), as_float(start[1])
        ex, ey = as_float(end[0]), as_float(end[1])
        if None in (sx, sy, ex, ey):
            continue
        nx, ny = inward_unit(start, end, toward)
        band = [
            (sx, sy),
            (ex, ey),
            (sx + nx * thickness, sy + ny * thickness),
            (ex + nx * thickness, ey + ny * thickness),
        ]
        rect = (
            min(point[0] for point in band),
            min(point[1] for point in band),
            max(point[0] for point in band),
            max(point[1] for point in band),
        )
        for element in massing.get("elements") or []:
            if not isinstance(element, dict) or element.get("kind") != "facade_wall":
                continue
            index = element.get("storey_index")
            if not isinstance(index, int) or isinstance(index, bool):
                continue
            actual = _ring_rect(element.get("profile_cm"))
            if actual is None or not all(
                close(actual[i], rect[i], 1e-6) for i in range(4)
            ):
                continue
            walls.setdefault((facade_id, index), element)
    return walls, thickness


def host_u_extent(
    element: dict[str, Any], start: Sequence[float], unit: tuple[float, float]
) -> tuple[float, float]:
    """The host wall's own ``u`` extent, in the facade-local frame G-76 measures against.

    ``u = 0`` sits at ``start_corner_cm``, so the band's own plan rectangle projects onto
    ``[0, length_cm]`` with no offset added by hand. Projecting the *element's* corners --
    rather than reading ``facades[].length_cm`` -- is what makes G-76 a statement about
    the host and not about the facade the host happens to serve.
    """
    ring = element.get("profile_cm")
    rect = _ring_rect(ring)
    if rect is None:
        raise Refusal(
            f"refusing to build: facade_wall {element.get('id')!r} has no usable profile_cm, so "
            "its u extent is undecidable and no cut on it can be placed."
        )
    sx, sy = as_float(start[0]), as_float(start[1])
    ux, uy = unit
    xs = (rect[0], rect[2])
    ys = (rect[1], rect[3])
    values = [
        (px - sx) * ux + (py - sy) * uy for px in xs for py in ys
    ]
    return min(values), max(values)


# --------------------------------------------------------------------------- #
# Wall tiling -- the replacement for a Boolean modifier
# --------------------------------------------------------------------------- #
#
# WHY THIS EXISTS.  The Boolean modifier is unusable in Max 2026.3.2 as installed here,
# measured 2026-10-05 against live Max with a bogus control in every batch:
#
#   * ``Boolean()``      -> ``Type error: Call needs function or class, got: undefined``
#   * ``BooleanMod()``   -> constructs, but its paramblock is **Voxel Map's**
#                           (``voxelSize``/``toleranceFactor``/``bevelDistance``): the
#                           Boolean name is shadowed in the class registry.  ``VoxelMap()``
#                           itself is NotCreatable, so there is no clean spelling.
#   * ``ProBoolean()``   -> constructs, but ``superClassOf`` is ``GeometryClass`` -- it is a
#                           *spacewarp-style object*, not a Modifier, and constructing one
#                           leaves a node in the scene.
#   * native bridge ``native:add_modifier`` with ``"Boolean"`` -> genuinely attaches
#                           (``#modifiers(Boolean:Boolean)``), **but the operand is never
#                           set**: ``snapshotAsMesh`` reports ``verts=8 faces=12``
#                           unchanged for every ``params`` spelling tried, and the committed
#                           modifier exposes neither ``operation`` nor ``object``.
#
# So a wall is built as **solid cells that tile it minus its openings**. Every cell is a
# ``Box`` -- the one primitive with a placement rule verified live at P3 -- so the stage
# needs no modifier at all and is immune to the measured 20-modifier freeze.
#
# The tiling is a column-row decomposition along the run axis: cut at every opening's
# ``u`` boundaries, and inside each resulting column cut at the ``v`` boundaries of the
# openings covering it. Because every boundary comes from some opening's edge, a column is
# either wholly inside an opening's ``u`` span or wholly outside it, which is what makes the
# subdivision exact with no overlap and no gap. ``G-82`` then checks that identity
# numerically instead of trusting it.

TILING_EPS = 1e-6


def _run_axis(unit: Sequence[float]) -> int:
    """0 when the facade runs along X, 1 when it runs along Y.

    ``07`` §8.5.3 restricts the frame to axis-aligned runs, so the unit is exactly one of
    ``(+-1, 0)`` / ``(0, +-1)``. A facade that runs diagonally has no axis-aligned tiling and
    is refused rather than silently snapped.
    """
    ux, uy = as_float(unit[0]), as_float(unit[1])
    if ux is None or uy is None:
        raise Refusal("refusing to build: a facade run unit is non-numeric.")
    if abs(abs(ux) - 1.0) <= TILING_EPS and abs(uy) <= TILING_EPS:
        return 0
    if abs(abs(uy) - 1.0) <= TILING_EPS and abs(ux) <= TILING_EPS:
        return 1
    raise Refusal(
        f"refusing to build: facade run unit ({ux}, {uy}) is not axis-aligned, so a wall "
        "cannot be tiled with Box primitives. Tiling is only defined for a run along X or Y."
    )


def opening_plan_rect(
    cut: dict[str, Any],
    facade: dict[str, Any],
    wall_rect: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """The opening's world plan rectangle, given the wall rectangle it sits in.

    ``u`` is facade-local, so it becomes a world interval only through the run unit and
    ``start_corner_cm``. The cross axis takes the **wall's** own extent: every opening is cut
    clean through the wall, which is what ``G-83`` asserts rather than assumes.
    """
    start = facade.get("start_corner_cm")
    end = facade.get("end_corner_cm")
    if not isinstance(start, list) or not isinstance(end, list):
        raise Refusal(f"refusing to build: facade {cut.get('facade')!r} has no run corners.")
    unit = run_unit_deg(start, end)
    axis = _run_axis(unit)
    origin = as_float(start[axis])
    u0, u1 = as_float(cut["u_range_cm"][0]), as_float(cut["u_range_cm"][1])
    if origin is None or u0 is None or u1 is None:
        raise Refusal(f"refusing to build: cut {cut.get('id')!r} carries a non-numeric u range.")
    step = unit[axis]
    r0 = min(origin + step * u0, origin + step * u1)
    r1 = max(origin + step * u0, origin + step * u1)
    if r1 - r0 <= TILING_EPS:
        raise Refusal(
            f"refusing to build: cut {cut.get('id')!r} has a zero-width u range "
            f"[{u0}, {u1}], so it removes no material and the tiling would be ambiguous."
        )
    if axis == 0:
        return (r0, wall_rect[1], r1, wall_rect[3])
    return (wall_rect[0], r0, wall_rect[2], r1)


def wall_cell_rects(
    host: dict[str, Any],
    cuts: Sequence[dict[str, Any]],
    facades: dict[str, dict[str, Any]],
    levels: Sequence[dict[str, Any]],
) -> list[tuple[tuple[float, float, float, float], tuple[float, float]]]:
    """``[(plan_rect, z_range), ...]`` -- the solid cells tiling one wall minus its openings.

    Cells come out in a deterministic order (ascending run interval, then ascending ``v``),
    so the emitted script and the committed ``assembly.json`` agree byte-for-byte.
    """
    wall_rect = _ring_rect(host.get("profile_cm"))
    if wall_rect is None:
        raise Refusal(
            f"refusing to build: facade_wall {host.get('id')!r} has no usable profile_cm, so "
            "it cannot be tiled."
        )
    z_lo, z_hi = as_float(host["z_range_cm"][0]), as_float(host["z_range_cm"][1])
    if z_lo is None or z_hi is None or z_hi - z_lo <= TILING_EPS:
        raise Refusal(f"refusing to build: facade_wall {host.get('id')!r} has a degenerate z_range.")

    holes: list[tuple[int, float, float, float, float]] = []
    axes: set[int] = set()
    for cut in cuts:
        facade = facades.get(str(cut.get("facade")))
        level_index = inum(cut.get("level_index"))
        if facade is None or not isinstance(level_index, int) or not (
            0 <= level_index < len(levels)
        ):
            raise Refusal(
                f"refusing to build: cut {cut.get('id')!r} names facade {cut.get('facade')!r} / "
                f"level {cut.get('level_index')!r}, which dimensions.json does not declare."
            )
        unit = run_unit_deg(facade["start_corner_cm"], facade["end_corner_cm"])
        axis = _run_axis(unit)
        axes.add(axis)
        plan = opening_plan_rect(cut, facade, wall_rect)
        elevation = as_float(levels[level_index].get("elevation_cm"))
        v0, v1 = as_float(cut["v_range_cm"][0]), as_float(cut["v_range_cm"][1])
        if elevation is None or v0 is None or v1 is None:
            raise Refusal(f"refusing to build: cut {cut.get('id')!r} has a non-numeric v range.")
        hz0, hz1 = elevation + v0, elevation + v1
        if hz0 < z_lo - TILING_EPS or hz1 > z_hi + TILING_EPS:
            raise Refusal(
                f"refusing to build: cut {cut.get('id')!r} spans z [{hz0}, {hz1}], outside host "
                f"{host.get('id')!r}'s [{z_lo}, {z_hi}]. A hole that leaves the wall has no "
                "meaning in a tiling."
            )
        if hz1 - hz0 <= TILING_EPS:
            raise Refusal(
                f"refusing to build: cut {cut.get('id')!r} has a zero-height v range, so it "
                "removes no material."
            )
        holes.append((axis, plan[0] if axis == 0 else plan[1],
                      plan[2] if axis == 0 else plan[3], hz0, hz1))

    if len(axes) > 1:
        raise Refusal(
            f"refusing to build: host {host.get('id')!r} carries openings on mixed run axes "
            f"{sorted(axes)}; one wall has exactly one run axis."
        )

    cross_lo = wall_rect[1] if (axes and 0 in axes) else wall_rect[0]
    cross_hi = wall_rect[3] if (axes and 0 in axes) else wall_rect[2]
    run_lo = wall_rect[0] if (axes and 0 in axes) else wall_rect[1]
    run_hi = wall_rect[2] if (axes and 0 in axes) else wall_rect[3]

    bounds = {run_lo, run_hi}
    for _, r0, r1, _, _ in holes:
        bounds.add(r0)
        bounds.add(r1)
    stations = sorted(bounds)

    cells: list[tuple[tuple[float, float, float, float], tuple[float, float]]] = []
    for index in range(len(stations) - 1):
        a, b = stations[index], stations[index + 1]
        if b - a <= TILING_EPS:
            continue
        middle = (a + b) / 2.0
        covering = [hole for hole in holes if hole[1] <= middle <= hole[2]]
        v_bounds = {z_lo, z_hi}
        for _, _, _, hz0, hz1 in covering:
            v_bounds.add(hz0)
            v_bounds.add(hz1)
        v_stations = sorted(
            value for value in v_bounds if z_lo - TILING_EPS <= value <= z_hi + TILING_EPS
        )
        for j in range(len(v_stations) - 1):
            c0, c1 = v_stations[j], v_stations[j + 1]
            if c1 - c0 <= TILING_EPS:
                continue
            v_middle = (c0 + c1) / 2.0
            if any(hz0 <= v_middle <= hz1 for _, _, _, hz0, hz1 in covering):
                continue
            if axes and 0 in axes:
                cells.append(((a, cross_lo, b, cross_hi), (c0, c1)))
            else:
                cells.append(((cross_lo, a, cross_hi, b), (c0, c1)))
    if not cells:
        raise Refusal(
            f"refusing to build: host {host.get('id')!r} tiled to zero cells, which means every "
            "point of the wall was claimed by an opening. A wall with no material is not a wall."
        )
    return cells


def build_wall_cells(
    cuts: Sequence[dict[str, Any]],
    massing: dict[str, Any],
    dimensions: dict[str, Any],
) -> list[dict[str, Any]]:
    """``wall_cells[]`` -- the solids that replace every Boolean modifier.

    One entry per cell, per host, in the deterministic order
    :func:`wall_cell_rects` produces. Each entry carries the geometry **and** the ``Box``
    literal's frame, because the gate measures nodes rather than trusting this file.
    """
    facades = {
        str(facade.get("id")): facade
        for facade in (dimensions.get("facades") or [])
        if isinstance(facade, dict)
    }
    levels = [item for item in (dimensions.get("levels") or []) if isinstance(item, dict)]
    hosts = {
        str(element.get("id")): element
        for element in (massing.get("elements") or [])
        if isinstance(element, dict) and element.get("kind") == "facade_wall"
    }
    by_host: dict[str, list[dict[str, Any]]] = {}
    for cut in cuts:
        by_host.setdefault(str(cut.get("host_ref")), []).append(cut)

    cells: list[dict[str, Any]] = []
    for host_id in sorted(by_host):
        host = hosts.get(host_id)
        if host is None:
            raise Refusal(
                f"refusing to build: cut host {host_id!r} is not a facade_wall in massing.json."
            )
        for index, (plan, z_range) in enumerate(
            wall_cell_rects(host, by_host[host_id], facades, levels), start=1
        ):
            cells.append(
                {
                    "id": cell_id(host_id, index),
                    "node_name": cell_node_name(host_id, index),
                    "host_ref": host_id,
                    "plan_rect_cm": [q(plan[0]), q(plan[1]), q(plan[2]), q(plan[3])],
                    "z_range_cm": [q(z_range[0]), q(z_range[1])],
                    "volume_cm3": q(
                        (plan[2] - plan[0]) * (plan[3] - plan[1]) * (z_range[1] - z_range[0])
                    ),
                }
            )
    return cells


# --------------------------------------------------------------------------- #
# The document
# --------------------------------------------------------------------------- #

Prototype = tuple[str, float, float, float]


def build_layer_map() -> dict[str, list[str]]:
    """``layer_map``: **data only**, keyed by layer name (07 section 8.1.4).

    Keying by layer is what lets G-75 say "every ``layer_map`` **key** is in the
    vocabulary" without a second indirection. Each value lists the *roles* the file
    assigns to that layer: the four ``components_registry.json`` kinds a placement can
    carry, and ``scatter_source`` for the scatter. A placement's own role is looked up
    through its ``component_id``, so the join is total and a new component kind with no
    layer_map entry is a FAIL rather than a silent ``0``.
    """
    return {
        FACADE_LAYER: ["entrance_door", "frame_member", "glazed_panel", "opaque_panel"],
        SCATTER_LAYER: ["scatter_source"],
    }


def component_index(registry: dict[str, Any]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for component in registry.get("components") or []:
        if isinstance(component, dict) and isinstance(component.get("id"), str):
            out.setdefault(component["id"], component)
    return out


def build_placements(
    world_rows: Sequence[dict[str, str]], registry: dict[str, Any]
) -> list[dict[str, Any]]:
    """One placement per ``world_table.csv`` data row, copied verbatim (G-73)."""
    components = component_index(registry)
    layer_map = build_layer_map()
    placements: list[dict[str, Any]] = []
    for source_row, row in enumerate(world_rows, start=1):
        component_id = row["component_ref"]
        component = components.get(component_id)
        if component is None:
            raise Refusal(
                f"refusing to build: {WORLD_CSV_NAME} data row {source_row} names "
                f"component_ref {component_id!r}, which {REGISTRY_NAME} does not declare (G-71)."
            )
        role = component.get("kind")
        if not isinstance(role, str):
            raise Refusal(
                f"refusing to build: {REGISTRY_NAME} component {component_id!r} declares no "
                "kind, so its layer_map role is undecidable (G-75)."
            )
        layer = layer_for_role(layer_map, role, component_id)
        placement_id = f"PLC-{source_row:03d}"
        placements.append(
            {
                "id": placement_id,
                "component_id": component_id,
                "source_row": source_row,
                "node_name": node_name(placement_id),
                "position_cm": [q(row["x_cm"]), q(row["y_cm"]), q(row["z_cm"])],
                "rot_z_deg": q(row["rot_z_deg"]),
                "instance": True,
                "layer": layer,
            }
        )
    return placements


def layer_for_role(layer_map: dict[str, list[str]], role: str, component_id: str) -> str:
    """The single layer that lists this role, or a refusal."""
    found = [layer for layer, roles in layer_map.items() if role in roles]
    if len(found) != 1:
        raise Refusal(
            f"refusing to build: role {role!r} (component {component_id!r}) is listed under "
            f"{len(found)} layer_map entries; G-75 requires exactly one, so a role's layer is "
            "decidable from the spec alone."
        )
    return found[0]


def build_opening_cuts(
    dimensions: dict[str, Any],
    massing: dict[str, Any],
    toward: tuple[float, float],
    joint_cm: float,
    thickness_cm: float,
) -> list[dict[str, Any]]:
    """One ``difference`` cut per ``dimensions.json`` opening, every one on a real wall.

    ``host_ref`` is never ``null`` here: the whole point of P6's ``facade_wall`` kind is
    that the envelope is total, so an opening with no wall to cut is a refusal rather than
    a skipped cut.
    """
    walls, _declared = facade_wall_index(massing, dimensions, toward)
    levels = {
        inum(level["index"]): level
        for level in dimensions.get("levels") or []
        if isinstance(level, dict) and isinstance(level.get("index"), int)
    }
    cuts: list[dict[str, Any]] = []
    for index, opening in enumerate(dimensions.get("openings") or [], start=1):
        if not isinstance(opening, dict):
            raise Refusal(
                f"refusing to build: dimensions.json openings[{index - 1}] is not an object."
            )
        facade_id = opening.get("facade")
        level_index = opening.get("level_index")
        position = as_float(opening.get("position_cm"))
        width = as_float(opening.get("width_cm"))
        sill = as_float(opening.get("sill_cm"))
        head = as_float(opening.get("head_cm"))
        if (
            not isinstance(facade_id, str)
            or not isinstance(level_index, int)
            or isinstance(level_index, bool)
            or position is None
            or width is None
            or sill is None
            or head is None
            or width <= 0.0
            or sill >= head
        ):
            raise Refusal(
                f"refusing to build: dimensions.json opening {opening.get('id')!r} lacks a finite "
                "position_cm / width_cm / sill_cm < head_cm, so no cutter can be sized from it "
                "(G-76)."
            )
        host = walls.get((facade_id, level_index))
        if host is None:
            raise Refusal(
                f"refusing to build: opening {opening.get('id')!r} sits on {facade_id!r} level "
                f"{level_index}, and massing.json declares no facade_wall banding that run at that "
                "level. The P6 envelope is total by construction (G-38 clause 2); a cut with a "
                "null host_ref is exactly what that clause exists to prevent (G-76)."
            )
        if level_index not in levels:
            raise Refusal(
                f"refusing to build: dimensions.json opening {opening.get('id')!r} names level "
                f"{level_index}, which levels[] does not declare (G-76)."
            )
        cut_id = f"CUT-{index:03d}"
        cuts.append(
            {
                "id": cut_id,
                "opening_id": str(opening.get("id")),
                "node_name": node_name(cut_id),
                "host_ref": str(host.get("id")),
                "facade": facade_id,
                "level_index": level_index,
                "bay_index": opening.get("bay_index"),
                "u_range_cm": [q(position - width / 2.0), q(position + width / 2.0)],
                "v_range_cm": [q(sill), q(head)],
                "depth_cm": q(thickness_cm + joint_cm),
                "kind": "difference",
            }
        )
    return cuts


def build_scatter(massing: dict[str, Any]) -> list[dict[str, Any]]:
    """The one scatter row this example ships.

    ``ground_pad`` is *not* a ``massing.json`` element -- it lives in ``site_pad`` -- so the
    target is the ``roof_deck`` element and the model a single ``column`` element, so the
    136-panel scene is not disturbed. Every number is a fixed literal in the spec: a builder
    that drew a seed or a density would make the scene unrepeatable, which is the P0
    determinism claim in one sentence.
    """
    elements = [e for e in massing.get("elements") or [] if isinstance(e, dict)]
    targets = [e for e in elements if e.get("kind") == SCATTER_TARGET_KIND]
    models = [e for e in elements if e.get("kind") == SCATTER_MODEL_KIND]
    if not targets:
        raise Refusal(
            f"refusing to build: massing.json declares no {SCATTER_TARGET_KIND!r} element for "
            "scatter[].target_ref to name (G-78)."
        )
    if not models:
        raise Refusal(
            f"refusing to build: massing.json declares no {SCATTER_MODEL_KIND!r} element for "
            "scatter[].model_refs to name (G-78)."
        )
    return [
        {
            "id": SCATTER_ID,
            "node_name": node_name(SCATTER_ID),
            "target_ref": str(targets[0].get("id")),
            "model_refs": [str(models[0].get("id"))],
            "seed": SCATTER_SEED,
            "instance_count_limit": SCATTER_INSTANCE_LIMIT,
            "distribution_density_pattern": SCATTER_DENSITY,
            "scale_from": SCATTER_SCALE_FROM,
            "scale_to": SCATTER_SCALE_TO,
            "rotation_from_deg": SCATTER_ROT_FROM_DEG,
            "rotation_to_deg": SCATTER_ROT_TO_DEG,
            "collision_avoid": True,
            "layer": SCATTER_LAYER,
        }
    ]


def build_defaults(registry: dict[str, Any]) -> dict[str, Any]:
    """``defaults``: one carried-forward P5 value and one refusal threshold.

    ``panel_joint_cm`` is ``components_registry.json:defaults.joint_width_cm`` -- ledger
    entry ``A-024``, P5's, carried forward. It is **not** a new assumption, which is
    exactly what keeps P6's assumed count at one (``A-025``, the wall thickness).
    """
    block = registry.get("defaults")
    joint = as_float(block.get("joint_width_cm")) if isinstance(block, dict) else None
    if joint is None or joint <= 0.0:
        raise Refusal(
            f"refusing to build: {REGISTRY_NAME}:defaults.joint_width_cm is missing or not a "
            "positive number, so assembly.json:defaults.panel_joint_cm would have to be "
            "invented. A-024 is that value's home and it must not be re-invented here."
        )
    return {"panel_joint_cm": q(joint), "instance_limit_guard": INSTANCE_LIMIT_GUARD}


def origin_inputs(
    dimensions: dict[str, Any], massing: dict[str, Any], registry: dict[str, Any]
) -> list[str]:
    """The dotted paths in the three JSON inputs this builder read (07 S-4).

    ``world_table.csv`` is not a JSON document and contributes no dotted path. A placement's
    traceability to it is its own ``source_row``, and G-72 asserts that join in **both**
    directions -- a stronger claim than a path list would be.
    """
    paths: set[str] = set()

    def collect(source: Any, prefix: str) -> None:
        if isinstance(source, dict):
            for key, child in source.items():
                collect(child, f"{prefix}.{key}" if prefix else key)
        elif isinstance(source, list):
            for index, item in enumerate(source):
                collect(item, f"{prefix}[{index}]")
        elif prefix:
            paths.add(prefix)

    for key in ("facades", "levels", "openings"):
        collect(dimensions.get(key), key)
    collect(dimensions.get("site"), "site")
    collect(massing.get("defaults"), "defaults")
    collect(massing.get("elements"), "elements")
    collect(registry.get("defaults"), "defaults")
    collect(registry.get("components"), "components")
    return sorted(paths)


def build_origins(document: dict[str, Any]) -> dict[str, Any]:
    """An ``origins`` entry per value-tree leaf, collapsed per row.

    One entry per *element* rather than per leaf is 07 G-9's documented array-element
    collapse, and it is what keeps the map at ~155 entries instead of ~2 000. Every value
    in this file is ``derived``: ``assembly.json`` computes nothing it did not read, so an
    ``assumed`` here would mean a silent default, which is the P5 trap. The cross-file
    provenance itself lives in ``origin_inputs`` and in the source ledger, exactly as P5
    did it.
    """
    origins: dict[str, Any] = {}

    def put(entry: str, derives: Sequence[str]) -> None:
        origins[entry] = {"origin": "derived", "derives_from": list(derives)}

    for layer in sorted(document["layer_map"]):
        put(f"layer_map.{layer}", [f"layer_map.{layer}"])
    put("defaults.panel_joint_cm", ["defaults.panel_joint_cm"])
    put("defaults.instance_limit_guard", ["defaults.instance_limit_guard"])
    for index in range(len(document["placements"])):
        put(
            f"placements[{index}]",
            [f"placements[{index}].source_row", f"placements[{index}].component_id"],
        )
    for index in range(len(document["opening_cuts"])):
        put(
            f"opening_cuts[{index}]",
            [f"opening_cuts[{index}].opening_id", f"opening_cuts[{index}].host_ref"],
        )
    # A cell is derived from the host wall AND from the opening it works around, so both
    # paths are named. Naming only the host would leave every coordinate uncovered in
    # substance while looking covered in form -- which is what G-9 exists to catch.
    for index in range(len(document["wall_cells"])):
        cell = document["wall_cells"][index]
        host_ref = str(cell["host_ref"])
        driving = [
            f"wall_cells[{index}].{leaf}"
            for leaf in ("plan_rect_cm", "z_range_cm")
        ]
        put(
            f"wall_cells[{index}]",
            driving + [f"massing.json elements[id={host_ref}].z_range_cm"],
        )
    for index in range(len(document["scatter"])):
        put(
            f"scatter[{index}]",
            [f"scatter[{index}].target_ref", f"scatter[{index}].model_refs"],
        )
    return origins


def build_assembly(
    dimensions: dict[str, Any],
    massing: dict[str, Any],
    registry: dict[str, Any],
    world_rows: Sequence[dict[str, str]],
) -> tuple[dict[str, Any], float]:
    """The whole ``assembly.json``, in 07 section 8.5's declared key order."""
    defaults = build_defaults(registry)
    joint = float(defaults["panel_joint_cm"])
    toward = footprint_centre(dimensions)
    walls, thickness = facade_wall_index(massing, dimensions, toward)
    if not walls:
        raise Refusal(
            "refusing to build: massing.json declares no facade_wall element at all, so no "
            "opening has an envelope to be cut from. P6's facade_wall kind is the reason this "
            "stage can exercise a cut path at all (G-76)."
        )
    source = dimensions.get("source")
    recorded_at = source.get("recorded_at") if isinstance(source, dict) else None
    if not isinstance(recorded_at, str) or not recorded_at:
        raise Refusal(
            "refusing to build: dimensions.json source.recorded_at is missing or not a string. "
            "07 section 3.2 allows exactly one timestamp in a derived file and it is copied "
            "verbatim from the input -- a builder never reads a clock."
        )
    tolerances = dimensions.get("tolerances")
    if not isinstance(tolerances, dict):
        raise Refusal(
            "refusing to build: dimensions.json declares no tolerances{} block, and 07 G-33 "
            "requires assembly.json to carry it verbatim."
        )
    project = dimensions.get("project")
    opening_cuts = build_opening_cuts(dimensions, massing, toward, joint, thickness)
    document: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "spec": "assembly",
        "project": project,
        "units": {"length": "cm", "angle": "deg"},
        "source": {
            "kind": "derived",
            "reference": (
                f"{REGISTRY_NAME} -- what each panel instance is; "
                f"{WORLD_CSV_NAME} -- where every instance goes, one data row per placements[] "
                f"entry; "
                f"{MASSING_NAME} -- the facade_wall envelope the openings are cut in; "
                f"{DIMENSIONS_NAME} -- the openings and the facade runs"
            ),
            "recorded_at": recorded_at,
        },
        "status": "locked",
        "tolerances": dict(tolerances),
        "origin_inputs": origin_inputs(dimensions, massing, registry),
        "origins": {},
        "defaults": defaults,
        "layer_map": build_layer_map(),
        "placements": build_placements(world_rows, registry),
        "opening_cuts": opening_cuts,
        "wall_cells": build_wall_cells(opening_cuts, massing, dimensions),
        "scatter": build_scatter(massing),
    }
    document["origins"] = build_origins(document)
    return document, thickness


# --------------------------------------------------------------------------- #
# The emitted MAXScript -- geometry only, no layer code
# --------------------------------------------------------------------------- #


def prototype_sizes(placements: Sequence[dict[str, Any]], registry: dict[str, Any]) -> list[Prototype]:
    """``(component_id, width_cm, height_cm, thickness_cm)`` per distinct component.

    Sorted by id, so the prototype creation order -- and therefore the file's bytes -- does
    not depend on which placement happened to introduce the component first.
    """
    sizes: dict[str, list[float]] = {}
    for component in registry.get("components") or []:
        if not isinstance(component, dict):
            continue
        ident = component.get("id")
        size = component.get("size_cm")
        if not isinstance(ident, str) or not isinstance(size, list) or len(size) != 3:
            continue
        values = [as_float(item) for item in size]
        if any(value is None or value <= 0.0 for value in values):
            continue
        sizes[ident] = [float(value) for value in values]
    wanted = {str(placement["component_id"]) for placement in placements}
    unknown = sorted(wanted - set(sizes))
    if unknown:
        raise Refusal(
            f"refusing to build: {REGISTRY_NAME} declares no usable size_cm for "
            f"{', '.join(unknown)}. Every placement needs a prototype box, and a component "
            "without a size has no geometry (G-71)."
        )
    return [
        (ident, sizes[ident][0], sizes[ident][1], sizes[ident][2]) for ident in sorted(wanted)
    ]


def prototype_dims(prototypes: Sequence[Prototype], component_id: str) -> tuple[float, float]:
    for ident, width, height, _thickness in prototypes:
        if ident == component_id:
            return width, height
    raise Refusal(f"refusing to emit: no prototype for component {component_id!r} (G-71).")


def render_ms(
    document: dict[str, Any],
    massing: dict[str, Any],
    dimensions: dict[str, Any],
    registry: dict[str, Any],
    wall_thickness_cm: float,
) -> str:
    """Emit the whole build as **one** driver function. No helper functions, no modifiers.

    Four verified behaviours shape this emitter (all measured 2026-10-05):

    * a ``local`` at the top level of a ``fileIn``-ed script is a **compile** error
      (``no local declarations at top level``), so every body lives inside an ``fn``;
    * the parenthesised one-liner delete guard
      ``if (getNodeByName "X") != undefined do ( delete (getNodeByName "X") )``
      **throws** when the node is absent, so every lookup is bound to a local first;
    * twenty modifiers on one node **froze Max until the machine rebooted**. This stage now
      emits **zero** modifiers, so the hazard is gone by construction rather than by
      chunking (G-81);
    * ``getModifier <i> <node>`` **throws** in this build; ``node.modifiers[i]`` works. The
      previous emitter used ``getModifier`` in its own idempotent stack reset, so that reset
      never ran.

    The census counts nodes **found in the scene**, never iterations of a loop that ran --
    the previous version counted its own bookkeeping and reported success with nothing in
    the scene.
    """
    project = document["project"]
    if not isinstance(project, str) or not PROJECT_ID_RE.match(project):
        raise Refusal(
            f"refusing to emit {OUT_MS_NAME}: project {project!r} does not match 07 section 3.1 "
            "^[a-z0-9][a-z0-9._-]*$, so the function name would not be safe."
        )
    function = build_fn_name(project)
    placements = document["placements"]
    cuts = document["opening_cuts"]
    cells = document["wall_cells"]
    prototypes = prototype_sizes(placements, registry)
    toward = footprint_centre(dimensions)
    facades = {
        str(facade["id"]): facade
        for facade in dimensions.get("facades") or []
        if isinstance(facade, dict) and isinstance(facade.get("id"), str)
    }
    levels = {
        inum(level["index"]): level
        for level in dimensions.get("levels") or []
        if isinstance(level, dict) and isinstance(level.get("index"), int)
    }
    hosts = sorted({str(cut["host_ref"]) for cut in cuts})
    known_elements = {
        str(element.get("id"))
        for element in massing.get("elements") or []
        if isinstance(element, dict)
    }
    for element_id in hosts:
        if element_id not in known_elements:
            raise Refusal(
                f"refusing to emit: opening_cuts name host {element_id!r}, which "
                f"{MASSING_NAME} does not declare (G-76)."
            )

    # Every node this run creates, in creation order. Deleted twice: deleting a base
    # object does not delete its instances.
    created = (
        [prototype_name(ident) for ident, _, _, _ in prototypes]
        + [str(placement["node_name"]) for placement in placements]
        + [str(cell["node_name"]) for cell in cells]
    )

    body: list[str] = []
    preamble = emit_unit_preamble(stage="assembly", factor_var="__f_unit")
    for line in preamble.splitlines():
        body.append(line[4:] if line.startswith("    ") else line)
    body.append(
        f"-- {OUT_JSON_NAME}: placements={len(placements)} cuts={len(cuts)} cells={len(cells)}"
    )
    body.append(f"-- prototypes={len(prototypes)} hosts={len(hosts)}")
    body.append("-- G-79: no statement below assigns a layer to a node; layer_map stays data.")
    body.append("-- delete-by-name, twice: deleting a base does not delete its instances.")
    for _run in (1, 2):
        for variable in created:
            body.append(f'local prev_{variable} = getNodeByName "{variable}"')
            body.append(f"if prev_{variable} != undefined do ( delete prev_{variable} )")

    body.append("-- prototypes: one box per distinct component_id, sized from the registry.")
    body.append("local proto_count = 0")
    for ident, width, height, thickness in prototypes:
        variable = prototype_name(ident)
        body.append(
            f"local {variable} = Box width:{scene_length_expr(width)} length:{scene_length_expr(thickness)} "
            f"height:{scene_length_expr(height)} pos:[0.0,0.0,0.0]"
        )
        body.append(f'{variable}.name = "{variable}"')
        body.append("proto_count = proto_count + 1")

    body.append("-- placements: copy, then share the baseObject (setCopyMode does not exist).")
    body.append("local placed_count = 0")
    for placement in placements:
        variable = str(placement["node_name"])
        proto = prototype_name(placement["component_id"])
        width, height = prototype_dims(prototypes, str(placement["component_id"]))
        del width  # only the height is needed here; the width rides on the prototype
        x, y, z = (as_float(value) for value in placement["position_cm"])
        if x is None or y is None or z is None:
            raise Refusal(
                f"refusing to emit: placement {placement.get('id')!r} has a non-numeric position_cm."
            )
        # node.pos on a Box puts the BASE at pos.z (verified), so centre the panel.
        pos = [q(x), q(y), q(z - height / 2.0)]
        body.append(f"local {variable} = copy {proto}")
        body.append(f"{variable}.baseObject = {proto}.baseObject")
        body.append(f'{variable}.name = "{variable}"')
        body.append(f"{variable}.pos = {scene_point_expr(pos)}")
        body.append(f"{variable}.rotation = quat {num(placement['rot_z_deg'])} [0,0,1]")
        body.append("placed_count = placed_count + 1")

    body.append(
        "-- wall cells: solids tiling each facade_wall minus its openings. No Boolean"
    )
    body.append(
        "-- modifier exists in this build (measured 2026-10-05), so the wall IS the cells."
    )
    body.append("local cell_count = 0")
    for cell in cells:
        variable = str(cell["node_name"])
        plan = cell["plan_rect_cm"]
        z0, z1 = as_float(cell["z_range_cm"][0]), as_float(cell["z_range_cm"][1])
        width = as_float(plan[2]) - as_float(plan[0])
        length = as_float(plan[3]) - as_float(plan[1])
        height = z1 - z0
        if None in (width, length, height, z0):
            raise Refusal(
                f"refusing to emit: wall cell {cell.get('id')!r} carries non-numeric geometry."
            )
        # node.pos on a Box puts the BASE at pos.z (verified P3), so centre the cell in Z.
        cx = as_float(plan[0]) + width / 2.0
        cy = as_float(plan[1]) + length / 2.0
        body.append(
            f"local {variable} = Box width:{scene_length_expr(width)} length:{scene_length_expr(length)} "
            f"height:{scene_length_expr(height)} pos:{scene_point_expr((cx, cy, z0))}"
        )
        body.append(f'{variable}.name = "{variable}"')
        body.append("cell_count = cell_count + 1")

    body.append("-- hosts come from massing.ms; refuse to run without them.")
    for element_id in hosts:
        variable = host_variable(element_id)
        body.append(f'local {variable} = getNodeByName "{node_name(element_id)}"')
        body.append(
            f"if {variable} == undefined do ( throw "
            f'"G-80: host {node_name(element_id)} is absent; fileIn massing.ms before assembly.ms" )'
        )
    if hosts:
        body.append(
            "local host_nodes = #(" + ", ".join(host_variable(item) for item in hosts) + ")"
        )
        body.append("-- Mechanism A (A-CORRECT): deactivate / hide host wall nodes so discrete cells")
        body.append("-- tile the facade and openings remain clear of solid host geometry.")
        body.append("for host_node in host_nodes do host_node.isHidden = true")

    body.append(
        "-- G-80: the emitted census. It counts nodes FOUND IN THE SCENE, not iterations of"
    )
    body.append(
        "-- a loop that ran: the previous version counted its own bookkeeping and reported 16"
    )
    body.append(
        "-- committed cuts while the scene held zero modifiers. A counter cannot observe a"
    )
    body.append("-- failed attach, so this one observes the scene.")
    body.append("local found_cells = 0")
    body.append("for scene_node in objects do")
    body.append("(")
    body.append('    if (substring scene_node.name 1 4) == "WAL_" do found_cells = found_cells + 1')
    body.append(")")
    body.append(
        f'if found_cells != {len(cells)} do ( throw "G-80: found " + (found_cells as string) + '
        f'" cell nodes named WAL_*; {OUT_JSON_NAME} wall_cells[] declares {len(cells)}" )'
    )
    body.append(
        f"if placed_count != {len(placements)} do ( throw \"G-80: placed \" + "
        f"(placed_count as string) + \" instances; {OUT_JSON_NAME} declares "
        f"{len(placements)} placements[]\" )"
    )
    body.append(
        f"if proto_count != {len(prototypes)} do ( throw \"G-80: built \" + "
        f"(proto_count as string) + f' prototypes; {OUT_JSON_NAME} resolves "
        f"{len(prototypes)} distinct component_id values' )"
    )
    body.append(
        "-- G-81: this stage emits ZERO modifiers, which is the only safe stack. The hosts"
    )
    body.append("-- must therefore arrive with an empty stack; a non-empty one means another")
    body.append("-- stage left something behind.")
    body.append("local stray_modifiers = 0")
    body.append("for host_node in host_nodes do stray_modifiers = stray_modifiers + host_node.modifiers.count")
    body.append(
        'if stray_modifiers != 0 do ( throw "G-81: hosts carry " + (stray_modifiers as string) + '
        '" modifier(s); assembly.ms attaches none, so their stacks must be empty" )'
    )
    body.append("true")

    lines_out = [
        f"/* place_components.py --stage assembly | project {project} | DO NOT EDIT */"
    ]
    # One function, no helpers. The stage used to emit four cut-pass functions because the
    # Boolean modifier had to be committed in bounded chunks; with tiling there is no
    # modifier to commit, so the passes are gone rather than left in as dead code.
    # NB: nothing may be declared at this level -- a top-level `local` in a fileIn-ed script
    # is a compile error (verified P3), which G-80 now checks for.
    lines_out.append(f"fn {function} = (")
    lines_out.extend(f"    {line}" for line in body)
    lines_out.append(")")
    lines_out.append(f"{function}()")
    return "\n".join(lines_out) + "\n"


# --------------------------------------------------------------------------- #
# Self-check: G-71..G-81 against the bytes that will be written
# --------------------------------------------------------------------------- #


def _fail(failures: list[str], rule: str, message: str) -> None:
    failures.append(f"{rule}: {message}")


def self_check(
    document: dict[str, Any],
    dimensions: dict[str, Any],
    massing: dict[str, Any],
    registry: dict[str, Any],
    world_rows: Sequence[dict[str, str]],
    script: str,
) -> list[str]:
    """Every one of G-71..G-81, run against the emitted document and script.

    The builder asserts the same predicates the linter asserts, on the bytes on disk, and
    refuses on any failure. That is the P5 device and it is the reason a sliver could not
    ship: a build that merely completes is not proof that the numbers are right.
    """
    failures: list[str] = []
    linear = as_number((document.get("tolerances") or {}).get("linear_cm")) or 0.5
    angle = as_number((document.get("tolerances") or {}).get("angle_deg")) or 0.01
    placements = document["placements"]
    cuts = document["opening_cuts"]
    cells = document["wall_cells"]
    scatter = document["scatter"]
    components = component_index(registry)
    elements = {
        str(element.get("id")): element
        for element in massing.get("elements") or []
        if isinstance(element, dict) and isinstance(element.get("id"), str)
    }
    openings = {
        str(opening.get("id")): opening
        for opening in dimensions.get("openings") or []
        if isinstance(opening, dict)
    }

    # ---- G-71 component resolution -------------------------------------------------
    for placement in placements:
        component_id = str(placement.get("component_id"))
        if component_id not in components:
            _fail(
                failures,
                "G-71",
                f"{placement.get('id')!r} names component_id {component_id!r}, which "
                f"{REGISTRY_NAME} does not declare",
            )

    # ---- G-72 the source_row join, both directions -------------------------------
    declared_rows = [p.get("source_row") for p in placements]
    if any(not isinstance(row, int) or isinstance(row, bool) for row in declared_rows):
        _fail(failures, "G-72", "a placement carries a non-integer source_row")
    real_rows = list(range(1, len(world_rows) + 1))
    if len(placements) != len(world_rows):
        _fail(
            failures,
            "G-72",
            f"{len(placements)} placements for {len(world_rows)} {WORLD_CSV_NAME} data rows",
        )
    duplicates = sorted({row for row in declared_rows if declared_rows.count(row) > 1})
    if duplicates:
        _fail(failures, "G-72", f"duplicate source_row values {duplicates[:10]}")
    missing = sorted(set(real_rows) - {row for row in declared_rows if isinstance(row, int)})
    if missing:
        _fail(failures, "G-72", f"source_row values with no placement: {missing[:10]}")
    extra = sorted(
        {row for row in declared_rows if isinstance(row, int)} - set(real_rows)
    )
    if extra:
        _fail(failures, "G-72", f"source_row values past the end of the table: {extra[:10]}")

    # ---- G-73 placement geometry equals its row ----------------------------------
    for placement in placements:
        row_index = placement.get("source_row")
        if not isinstance(row_index, int) or isinstance(row_index, bool):
            continue
        if not 1 <= row_index <= len(world_rows):
            continue
        row = world_rows[row_index - 1]
        expected = [as_float(row["x_cm"]), as_float(row["y_cm"]), as_float(row["z_cm"])]
        actual = placement.get("position_cm")
        if (
            not isinstance(actual, list)
            or len(actual) != 3
            or any(value is None for value in expected)
            or not all(close(actual[i], expected[i], linear) for i in range(3))
        ):
            _fail(
                failures,
                "G-73",
                f"{placement.get('id')!r} position_cm {actual!r} != {WORLD_CSV_NAME} row "
                f"{row_index} {[row['x_cm'], row['y_cm'], row['z_cm']]} within {linear} cm",
            )
        if not close(placement.get("rot_z_deg"), as_float(row["rot_z_deg"]), angle):
            _fail(
                failures,
                "G-73",
                f"{placement.get('id')!r} rot_z_deg {placement.get('rot_z_deg')!r} != row "
                f"{row_index} {row['rot_z_deg']!r} within {angle} deg",
            )
        if placement.get("instance") is not True:
            _fail(failures, "G-73", f"{placement.get('id')!r} instance is not true")

    # ---- G-74 node names: unique across the four tables, and identifier-safe -------
# `wall_cells` is in this list from P6's tiling change. It was MISSING at first, and the
# fault injection caught it: a duplicated or malformed cell name passed the self-check
# clean. A cell is a real scene node, so it carries exactly the obligations a placement
# does -- including uniqueness against every other table, because the census counts nodes
# by name and two nodes sharing one would make that count a lie.
    names: dict[str, str] = {}
    for table in ("placements", "opening_cuts", "wall_cells", "scatter"):
        for row in document[table]:
            name = row.get("node_name")
            if not isinstance(name, str) or not NODE_NAME_RE.match(name):
                _fail(
                    failures,
                    "G-74",
                    f"{table} row {row.get('id')!r} node_name {name!r} is not "
                    "MAXScript-identifier-safe (11 section 3.1 N1)",
                )
                continue
            if name in names:
                _fail(
                    failures,
                    "G-74",
                    f"node_name {name!r} is claimed by both {names[name]} and {table} "
                    f"{row.get('id')!r}",
                )
            names[name] = f"{table} {row.get('id')}"
            # The name must be its own id with dashes replaced -- 11 section 3.1 N4, since
            # a descriptive name is a lookup table nobody versions.
            own = str(row.get("id")).replace("-", "_")
            if own != name:
                _fail(
                    failures,
                    "G-74",
                    f"{table} row {row.get('id')!r} node_name {name!r} is not its own id with "
                    f"dashes replaced ({own!r})",
                )

    # ---- G-75 layers come from layer_map, and layer_map keys are in the vocabulary -
    layer_map = document.get("layer_map")
    if not isinstance(layer_map, dict):
        _fail(failures, "G-75", "layer_map is not an object")
        layer_map = {}
    for layer in sorted(layer_map):
        if layer not in LAYER_VOCABULARY:
            _fail(
                failures,
                "G-75",
                f"layer_map key {layer!r} is not one of {', '.join(LAYER_VOCABULARY)} "
                "(07 section 8.1.4)",
            )
    for placement in placements:
        component = components.get(str(placement.get("component_id")))
        role = component.get("kind") if isinstance(component, dict) else None
        layer = placement.get("layer")
        if layer not in layer_map:
            _fail(
                failures,
                "G-75",
                f"{placement.get('id')!r} layer {layer!r} is not a layer_map key",
            )
            continue
        if isinstance(role, str) and role not in layer_map[layer]:
            _fail(
                failures,
                "G-75",
                f"{placement.get('id')!r} role {role!r} is not listed under layer_map[{layer!r}]",
            )
    for row in scatter:
        layer = row.get("layer")
        if layer not in layer_map:
            _fail(failures, "G-75", f"{row.get('id')!r} layer {layer!r} is not a layer_map key")
        elif "scatter_source" not in layer_map[layer]:
            _fail(
                failures,
                "G-75",
                f"{row.get('id')!r} role scatter_source is not listed under "
                f"layer_map[{layer!r}]",
            )

    # ---- G-76 every cut is on a real facade_wall, inside it, and deep enough -------
    toward = footprint_centre(dimensions)
    thickness = as_float(
        (massing.get("defaults") or {}).get("facade_wall_thickness_cm")
    )
    facades = {
        str(facade["id"]): facade
        for facade in dimensions.get("facades") or []
        if isinstance(facade, dict) and isinstance(facade.get("id"), str)
    }
    levels = {
        inum(level["index"]): level
        for level in dimensions.get("levels") or []
        if isinstance(level, dict) and isinstance(level.get("index"), int)
    }
    for cut in cuts:
        host_id = cut.get("host_ref")
        if not isinstance(host_id, str) or not host_id:
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} host_ref is {host_id!r}; the P6 envelope is total, so it is "
                "never null",
            )
            continue
        host = elements.get(host_id)
        if host is None or host.get("kind") != "facade_wall":
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} host_ref {host_id!r} is not a massing facade_wall element",
            )
            continue
        facade = facades.get(str(cut.get("facade")))
        level = levels.get(inum(cut.get("level_index")))
        if facade is None or level is None:
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} names facade {cut.get('facade')!r} / level "
                f"{cut.get('level_index')!r}, which dimensions.json does not declare",
            )
            continue
        if host.get("storey_index") != inum(cut.get("level_index")):
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} is on level {cut.get('level_index')!r} but its host "
                f"{host_id!r} serves storey {host.get('storey_index')!r}",
            )
        u_range = cut.get("u_range_cm")
        v_range = cut.get("v_range_cm")
        depth = as_float(cut.get("depth_cm"))
        if (
            not isinstance(u_range, list)
            or len(u_range) != 2
            or not isinstance(v_range, list)
            or len(v_range) != 2
        ):
            _fail(failures, "G-76", f"{cut.get('id')!r} carries a malformed range")
            continue
        u0, u1 = as_float(u_range[0]), as_float(u_range[1])
        v0, v1 = as_float(v_range[0]), as_float(v_range[1])
        if None in (u0, u1, v0, v1, depth):
            _fail(failures, "G-76", f"{cut.get('id')!r} carries a non-numeric range or depth")
            continue
        if not u0 < u1:
            _fail(failures, "G-76", f"{cut.get('id')!r} u_range_cm is not ascending")
        host_u0, host_u1 = host_u_extent(
            host, facade["start_corner_cm"], run_unit_deg(
                facade["start_corner_cm"], facade["end_corner_cm"]
            )
        )
        if u0 < host_u0 - linear or u1 > host_u1 + linear:
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} u_range_cm [{u0}, {u1}] leaves host {host_id!r}'s own u "
                f"extent [{host_u0}, {host_u1}] by more than {linear} cm",
            )
        height = as_float(level.get("height_cm"))
        if height is not None and (v0 < -linear or v1 > height + linear):
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} v_range_cm [{v0}, {v1}] leaves the host's own local v extent "
                f"[0, {height}] by more than {linear} cm",
            )
        z_range = host.get("z_range_cm")
        span = (
            as_float(z_range[1]) - as_float(z_range[0])
            if isinstance(z_range, list) and len(z_range) == 2
            else None
        )
        if span is not None and (v1 - v0) > span + linear:
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} v span {v1 - v0} exceeds host {host_id!r}'s height {span}",
            )
        if thickness is not None and depth < thickness - linear:
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} depth_cm {depth} < facade_wall_thickness_cm {thickness}",
            )
        if cut.get("kind") not in CUT_KINDS:
            _fail(
                failures,
                "G-76",
                f"{cut.get('id')!r} kind {cut.get('kind')!r} is not one of {', '.join(CUT_KINDS)}",
            )

    # ---- G-77 one opening, one cut, in both directions ----------------------------
    seen_openings: dict[str, int] = {}
    for cut in cuts:
        opening_id = str(cut.get("opening_id"))
        seen_openings[opening_id] = seen_openings.get(opening_id, 0) + 1
    for opening_id, count in sorted(seen_openings.items()):
        if count != 1:
            _fail(failures, "G-77", f"opening {opening_id!r} has {count} cuts, expected exactly 1")
    for opening_id in sorted(openings):
        if opening_id not in seen_openings:
            _fail(failures, "G-77", f"opening {opening_id!r} has no cut")
    for cut in cuts:
        opening_id = str(cut.get("opening_id"))
        opening = openings.get(opening_id)
        if opening is None:
            _fail(
                failures,
                "G-77",
                f"{cut.get('id')!r} names opening {opening_id!r}, which dimensions.json does not "
                "declare",
            )
            continue
        position = as_float(opening.get("position_cm"))
        width = as_float(opening.get("width_cm"))
        u_range = cut.get("u_range_cm") or []
        if position is not None and width is not None and len(u_range) == 2:
            if not (
                close(u_range[0], position - width / 2.0, linear)
                and close(u_range[1], position + width / 2.0, linear)
            ):
                _fail(
                    failures,
                    "G-77",
                    f"{cut.get('id')!r} u_range_cm {u_range!r} is not "
                    f"[{position - width / 2.0}, {position + width / 2.0}] for {opening_id!r}",
                )
        v_range = cut.get("v_range_cm") or []
        if len(v_range) == 2 and not (
            close(v_range[0], opening.get("sill_cm"), linear)
            and close(v_range[1], opening.get("head_cm"), linear)
        ):
            _fail(
                failures,
                "G-77",
                f"{cut.get('id')!r} v_range_cm {v_range!r} is not "
                f"[sill_cm, head_cm] of {opening_id!r}",
            )

    # ---- G-78 scatter ranges and reference resolution -----------------------------
    for row in scatter:
        ident = str(row.get("id"))
        if not SCATTER_ID_RE.match(ident):
            _fail(failures, "G-78", f"scatter id {ident!r} is not ^SCT-\\d{{3}}$")
        seed = row.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool) or not SEED_MIN <= seed <= SEED_MAX:
            _fail(
                failures,
                "G-78",
                f"{ident} seed {seed!r} is not an integer in {SEED_MIN}..{SEED_MAX}",
            )
        low, high = as_float(row.get("scale_from")), as_float(row.get("scale_to"))
        if low is None or high is None or not 0.0 < low <= high:
            _fail(failures, "G-78", f"{ident} scale range {low!r}..{high!r} is not 0 < from <= to")
        rlow, rhigh = as_float(row.get("rotation_from_deg")), as_float(
            row.get("rotation_to_deg")
        )
        if rlow is None or rhigh is None or rlow > rhigh:
            _fail(
                failures,
                "G-78",
                f"{ident} rotation range {rlow!r}..{rhigh!r} is not from <= to",
            )
        limit = row.get("instance_count_limit")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            _fail(failures, "G-78", f"{ident} instance_count_limit {limit!r} is not > 0")
        density = as_float(row.get("distribution_density_pattern"))
        if density is None or not 0.0 <= density <= 1.0:
            _fail(
                failures,
                "G-78",
                f"{ident} distribution_density_pattern {density!r} is outside 0..1",
            )
        if row.get("target_ref") not in elements:
            _fail(
                failures,
                "G-78",
                f"{ident} target_ref {row.get('target_ref')!r} does not resolve in "
                f"{MASSING_NAME}",
            )
        models = row.get("model_refs")
        if not isinstance(models, list) or not models:
            _fail(failures, "G-78", f"{ident} model_refs is not a non-empty array")
        else:
            for ref in models:
                if ref not in elements and ref not in components:
                    _fail(
                        failures,
                        "G-78",
                        f"{ident} model_ref {ref!r} resolves in neither {MASSING_NAME} nor "
                        f"{REGISTRY_NAME}",
                    )

    # ---- 07 section 8.5 section 3.5: nothing from P7/P8/P9 may appear -------------
    forbidden_tables = ("materials", "cameras", "lights", "export", "exports")
    for key in forbidden_tables:
        if key in document:
            _fail(
                failures,
                "G-1",
                f"{OUT_JSON_NAME} declares {key!r}; 07 section 8.5 section 3.5 reserves "
                "materials, cameras, lights and export to P7, P8 and P9",
            )

    # ---- origins coverage (07 G-9 machinery, so the walk exists once) -------------
    leaves = collect_leaves(document)
    entries = document.get("origins")
    if not isinstance(entries, dict):
        _fail(failures, "G-9", "origins is not an object")
        entries = {}
    for leaf in leaves:
        hits = [entry for entry in entries if covers(entry, leaf)]
        if len(hits) != 1:
            _fail(
                failures,
                "G-9",
                f"leaf {leaf} is covered {len(hits)} time(s) by origins; 07 G-9 requires exactly "
                "one",
            )
    for entry in sorted(entries):
        if not any(covers(entry, leaf) for leaf in leaves):
            _fail(failures, "G-9", f"origins entry {entry} covers no leaf")

    # ---- G-79 no layer assignment in the emitted script --------------------------
    body = script.replace("LayerManager.newLayerFromName", "")
    if "LayerManager" in body:
        _fail(
            failures,
            "G-79",
            f"{OUT_MS_NAME} uses a LayerManager call other than newLayerFromName; the layer "
            "vocabulary is data at this stage",
        )
    layer_tokens = (
        ".layer =",
        ".setLayer(",
        "setProperty #layer",
        "node.layer",
        ".layerIndex",
        "LayerProperties",
        "assignToLayer",
        "setLayerByName",
        "layers.add",
    )
    for line in script.split("\n"):
        if any(token in line for token in layer_tokens):
            _fail(
                failures,
                "G-79",
                f"{OUT_MS_NAME} assigns a layer to a node ({line.strip()!r}). node.layer throws "
                "'Property is read-only: layer' in Max 2026 and manage_layers has no setter "
                "action, so layer application is a human action in the Layer dialog",
            )

    # ---- G-80 the emitted census must be present and match the table --------------
    for needle, why in (
        (f"if placed_count != {len(placements)} do", "placements"),
        (f"if found_cells != {len(cells)} do", "wall_cells"),
        ("if proto_count != ", "prototypes"),
        # The census must OBSERVE the scene. A counter that only tallies its own
        # bookkeeping passed the previous build with 16 "committed" cuts and an empty
        # stack, so the scene-walk is itself a required needle, not an implementation
        # detail.
        ('if (substring scene_node.name 1 4) == "WAL_"', "the scene walk that observes cells"),
        ("for scene_node in objects do", "the scene walk that observes cells"),
    ):
        if needle not in script:
            _fail(
                failures,
                "G-80",
                f"{OUT_MS_NAME} carries no emitted census for {why}; a build that completes is "
                "not proof the numbers are right",
            )

    # ---- G-81 bounded modifier stack ---------------------------------------------
    _check_stack_bounds(script, cuts, failures)

    # ---- G-82/G-83 the cells must tile the wall exactly ---------------------------
    _check_wall_tiling(document, massing, failures)

    # ---- the guards the emitted script must actually contain ---------------------
    _check_script_shape(document, script, failures)
    return failures


def as_number(value: Any) -> float | None:
    return as_float(value)


def _check_stack_bounds(script: str, cuts: Sequence[dict[str, Any]], failures: list[str]) -> None:
    """G-81, checked on the emitted text: this stage must attach **no** modifier at all.

    The rule used to be two ceilings -- five modifiers per call, ten per node -- because
    openings were cut with a Boolean modifier. Both are gone. Measured 2026-10-05 against
    live Max: ``Boolean()`` does not construct, ``BooleanMod()`` carries Voxel Map's
    paramblock, and the native bridge attaches a Boolean whose operand is never set, so the
    cut silently did nothing. A wall is now built as solid cells, so the honest form of the
    rule is the strong one: **zero**.

    The ladder result still stands as the reason the ceiling is zero rather than merely
    small: 5 and 10 rungs were clean and 20 froze Max until the machine rebooted.
    """
    del cuts  # no cut is committed to a stack any more
    total = script.count("addModifier")
    if total:
        first = next(line.strip() for line in script.split("\n") if "addModifier" in line)
        _fail(
            failures,
            "G-81",
            f"{OUT_MS_NAME} attaches {total} modifier(s) ({first!r}). Walls are built as solid "
            "cells, so this stage emits none: the Boolean modifier is unusable in this build "
            "and a modifier stack is the measured freeze hazard (20 rungs rebooted the machine)",
        )


def box_endpoint_budget_cm3(w: float, h: float, t: float, linear_cm: float) -> float:
    """Conservative per-solid physical volume uncertainty budget B cm³ (07 §13.1, §21.4).

    For extents w, h, t > 0 and linear tolerance e = linear_cm >= 0,
    extent uncertainty d = 2 * e.
    B = max((w+d)(h+d)(t+d) - wht, wht - max(w-d,0)max(h-d,0)max(t-d,0)).
    If e <= 0, B = 0.0.
    """
    if linear_cm <= 0.0:
        return 0.0
    d = 2.0 * linear_cm
    upper_diff = (w + d) * (h + d) * (t + d) - (w * h * t)
    lower_prod = max(w - d, 0.0) * max(h - d, 0.0) * max(t - d, 0.0)
    lower_diff = (w * h * t) - lower_prod
    return max(upper_diff, lower_diff)


def _check_wall_tiling(
    document: dict[str, Any], massing: dict[str, Any], failures: list[str]
) -> None:
    """G-82 and G-83: the cells must tile their wall exactly -- no gap, no overlap.

    **G-82 -- volume identity.** For every host, the cells' summed volume equals the host's
    own volume minus the volume of its openings. This is the check the Boolean route could
    never have satisfied: a modifier that removes nothing leaves the volume untouched, so a
    "successful" build would have read as a wall with every opening still filled.

    **G-83 -- every cell carries the wall's full thickness.** A tiling of solid cells cannot
    express a partial-depth opening, so a cell that does not span the wall is a defect, not
    a style choice.

    Both compare geometry. A rule that only counted entries would be satisfied by any list
    of the right length.
    """
    cells = document["wall_cells"]
    cuts = document["opening_cuts"]
    linear = as_number((document.get("tolerances") or {}).get("linear_cm")) or 0.5
    walls = {
        str(element.get("id")): element
        for element in (massing.get("elements") or [])
        if isinstance(element, dict) and element.get("kind") == "facade_wall"
    }
    by_host: dict[str, list[dict[str, Any]]] = {}
    for cell in cells:
        by_host.setdefault(str(cell.get("host_ref")), []).append(cell)

    for host_id, host_cells in sorted(by_host.items()):
        wall = walls.get(host_id)
        if wall is None:
            _fail(failures, "G-82", f"wall_cells[] names host {host_id!r}, which is not a facade_wall")
            continue
        ring = wall.get("profile_cm")
        if not isinstance(ring, list) or not ring:
            _fail(failures, "G-82", f"facade_wall {host_id!r} has no profile_cm")
            continue
        xs = [as_float(point[0]) for point in ring]
        ys = [as_float(point[1]) for point in ring]
        wz0, wz1 = as_float(wall["z_range_cm"][0]), as_float(wall["z_range_cm"][1])
        if any(value is None for value in xs + ys) or wz0 is None or wz1 is None:
            _fail(failures, "G-82", f"facade_wall {host_id!r} carries non-numeric geometry")
            continue
        wx0, wx1 = min(xs), max(xs)
        wy0, wy1 = min(ys), max(ys)
        thin_is_y = (wy1 - wy0) <= (wx1 - wx0)
        thickness = (wy1 - wy0) if thin_is_y else (wx1 - wx0)
        wall_volume = (wx1 - wx0) * (wy1 - wy0) * (wz1 - wz0)
        b_host = box_endpoint_budget_cm3(wx1 - wx0, wy1 - wy0, abs(wz1 - wz0), linear)

        cell_volume = 0.0
        b_cells = 0.0
        for cell in host_cells:
            plan = cell.get("plan_rect_cm") or []
            z_range = cell.get("z_range_cm") or []
            values = [as_float(value) for value in list(plan) + list(z_range)]
            if len(plan) != 4 or len(z_range) != 2 or any(value is None for value in values):
                _fail(
                    failures,
                    "G-82",
                    f"wall cell {cell.get('id')!r} is not four plan numbers plus a two-number "
                    "z range",
                )
                continue
            x0, y0, x1, y1, z0, z1 = values
            if x1 <= x0 or y1 <= y0 or z1 <= z0:
                _fail(
                    failures,
                    "G-82",
                    f"wall cell {cell.get('id')!r} is degenerate: x[{x0}, {x1}] "
                    f"y[{y0}, {y1}] z[{z0}, {z1}]",
                )
                continue
            cell_volume += (x1 - x0) * (y1 - y0) * (z1 - z0)
            b_cells += box_endpoint_budget_cm3(x1 - x0, y1 - y0, z1 - z0, linear)
            if z0 < wz0 - linear or z1 > wz1 + linear:
                _fail(
                    failures,
                    "G-82",
                    f"wall cell {cell.get('id')!r} spans z [{z0}, {z1}], outside host "
                    f"{host_id!r}'s [{wz0}, {wz1}]",
                )
            if thin_is_y:
                off = max(abs(y0 - wy0), abs(y1 - wy1))
            else:
                off = max(abs(x0 - wx0), abs(x1 - wx1))
            if off > linear:
                _fail(
                    failures,
                    "G-83",
                    f"wall cell {cell.get('id')!r} misses the wall's full thickness by "
                    f"{off} cm. A tiling of solid cells cannot express a partial-depth "
                    "opening, so a cell must span the wall exactly",
                )

        opening_volume = 0.0
        b_cuts = 0.0
        for cut in cuts:
            if str(cut.get("host_ref")) != host_id:
                continue
            u_range = cut.get("u_range_cm") or []
            v_range = cut.get("v_range_cm") or []
            if len(u_range) != 2 or len(v_range) != 2:
                continue
            u0, u1 = as_float(u_range[0]), as_float(u_range[1])
            v0, v1 = as_float(v_range[0]), as_float(v_range[1])
            if None in (u0, u1, v0, v1):
                continue
            # An opening is cut clean through, so its volume is run length x wall
            # thickness x v length. `u` is facade-local and this host's long axis is the
            # run axis, which G-76 already established for this host.
            opening_volume += abs(u1 - u0) * thickness * abs(v1 - v0)
            b_cuts += box_endpoint_budget_cm3(abs(u1 - u0), thickness, abs(v1 - v0), linear)

        expected = wall_volume - opening_volume
        vol_budget = b_host + b_cells + b_cuts
        if abs(cell_volume - expected) > vol_budget:
            _fail(
                failures,
                "G-82",
                f"host {host_id}: cells total {cell_volume} cm3 but wall {wall_volume} minus "
                f"openings {opening_volume} is {expected} cm3. A difference of "
                f"{cell_volume - expected} cm3 exceeds the volume budget of {vol_budget} cm3 "
                "and means the cells do not tile the wall -- either a "
                "gap (unbuilt material) or an overlap (double-counted material)",
            )


def _check_script_shape(document: dict[str, Any], script: str, failures: list[str]) -> None:
    """The structural obligations of 07 section 8.5's emitted script, checked as text.

    Verified by execution, not by inspection: a top-level ``local`` is a compile error, and
    the parenthesised one-liner delete guard throws when the node is absent. Neither can be
    caught by a MAXScript interpreter here, so both are refused in the bytes.
    """
    project = str(document["project"])
    function = build_fn_name(project)
    header = f"/* place_components.py --stage assembly | project {project} | DO NOT EDIT */"
    lines = script.split("\n")

    def bad(rule: str, reason: str) -> None:
        _fail(failures, rule, f"{OUT_MS_NAME}: {reason}")

    if not lines or lines[0] != header:
        bad("G-80", "it does not start with the emitted header comment")
    while lines and not lines[-1].strip():
        lines.pop()
    calls = script.count(f"\n{function}()")
    if calls != 1:
        bad(
            "G-80",
            f"the entry point {function}() is called {calls} times; a second fileIn must "
            "converge, not accumulate",
        )
    if lines[-1] != f"{function}()":
        bad("G-80", f"it ends with {lines[-1]!r}, expected the single call '{function}()'")
    if "units.SystemScale" not in script or "__f_unit" not in script:
        bad("G-80", "missing unit verification preamble or __f_unit factor")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("local ") and not line.startswith("    "):
            bad(
                "G-80",
                f"it has a top-level `local`: {stripped!r}. A local declaration at the top level "
                "of a fileIn-ed script is a compile error (verified 2026-10-05)",
            )
    if re.search(r"if\s*\(\s*getNodeByName", script):
        bad(
            "G-80",
            "it uses the parenthesised one-liner delete guard `if (getNodeByName ...)`, which "
            "throws when the node does not exist; bind the lookup to a local first",
        )
    if script.count("= getNodeByName ") != script.count("if prev_") + len(
        {str(cut["host_ref"]) for cut in document["opening_cuts"]}
    ):
        bad(
            "G-80",
            "a getNodeByName lookup is not followed by an explicit-local guard; the "
            "context-dependent one-liner throws when the node is absent",
        )
    # G-56's rule, generalised: no bare literal sub-object index.
    for pattern, why in (
        (r"\.subobjectLevel\s*=", "a subObjectLevel assignment"),
        (r"\.subObjectID\s*=\s*\d", "a subObjectID assignment"),
        (r"getModifier\s+\d+\s", "a bare literal modifier index"),
    ):
        if re.search(pattern, script):
            bad("G-81", f"it carries {why}; every index must be bound to a variable first (G-56)")
    # The instance route, exactly as measured on 2026-10-05.
    if "copy " not in script:
        bad("G-71", "it creates no instance by `copy`, so nothing is instanced")
    if ".baseObject = " not in script:
        bad("G-71", "no node shares a prototype's baseObject; `setCopyMode` does not exist")
    # The banned-name scan reads *code* lines only. A comment may legitimately name an
    # absent function -- several of these comments exist precisely to record why the
    # working substitute is used -- and a self-check that failed on its own documentation
    # would be a rule that cannot be honoured.
    code_lines = [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("--")
    ]
    for banned in ("setCopyMode", "rotationZ", "rotationX", "rotationY", "matrix3", "angle",
                   "findString", "filterString"):
        for line in code_lines:
            if banned in line:
                bad(
                    "G-71",
                    f"it uses {banned!r} on the code line {line!r}, which does not exist in this "
                    "build (P5)",
                )
    if not any(".rotation = quat " in line for line in code_lines):
        bad("G-71", "it sets no rotation; `quat <degrees> [0,0,1]` is the only route that works")


# --------------------------------------------------------------------------- #
# Serialisation
# --------------------------------------------------------------------------- #


def serialize(document: dict[str, Any]) -> str:
    try:
        body = json.dumps(_round_tree(document), indent=2, ensure_ascii=False, allow_nan=False)
    except ValueError as exc:  # NaN / Infinity
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


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def summarise(document: dict[str, Any], script: str) -> str:
    placements = document["placements"]
    cuts = document["opening_cuts"]
    scatter = document["scatter"]
    hosts: dict[str, int] = {}
    for cut in cuts:
        hosts[str(cut["host_ref"])] = hosts.get(str(cut["host_ref"]), 0) + 1
    prototypes = len({str(p["component_id"]) for p in placements})
    passes = len(
        [1 for start in range(0, len(cuts), MAX_MODIFIERS_PER_CALL)]
    ) or 1
    lines = [
        "place_components.py --stage assembly",
        f"  project    {document['project']}  (read: {', '.join(UPSTREAM_NAMES)})",
        f"  placements {len(placements)}  -> {prototypes} prototypes, one per distinct "
        "component_id",
        f"  cuts       {len(cuts)}  difference, over {len(hosts)} facade_wall hosts, in "
        f"{passes} pass(es) of <= {MAX_MODIFIERS_PER_CALL} (G-81)",
        f"  scatter    {len(scatter)} row(s): "
        + ", ".join(
            f"{row['id']} -> {row['target_ref']} seed {row['seed']} layer {row['layer']}"
            for row in scatter
        ),
        f"  defaults   panel_joint_cm {document['defaults']['panel_joint_cm']} "
        "(components_registry.json:defaults.joint_width_cm, A-024 carried forward), "
        f"instance_limit_guard {document['defaults']['instance_limit_guard']}",
        f"  layer_map  {len(document['layer_map'])} layers, data only; {OUT_MS_NAME} assigns no "
        "layer to any node (G-79)",
        f"  emitted    {len(script.splitlines())} lines, {len(function_names(script))} functions, "
        f"one call: {function_names(script)[-1]}()",
        f"  self-check {' '.join(RULES)} pass",
    ]
    return "\n".join(lines)


def function_names(script: str) -> list[str]:
    return [line.split(" ", 1)[1].split(" ", 1)[0] for line in script.split("\n") if line.startswith("fn ")]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build assembly.json and assembly.ms from a locked components_registry.json, "
            "world_table.csv, massing.json and dimensions.json "
            "(07 section 8.5, invariants G-71..G-81)."
        )
    )
    parser.add_argument(
        "--stage",
        default=DEFAULT_STAGE,
        help=f"stage to build; supported: {', '.join(STAGES)}",
    )
    parser.add_argument(
        "--in", dest="in_dir", required=True, type=Path, help="specs directory to read"
    )
    parser.add_argument(
        "--out",
        dest="out_dir",
        default=None,
        type=Path,
        help="output directory (default: --in)",
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="print a machine-readable summary"
    )
    parser.add_argument(
        "--build",
        dest="build_gate",
        action="store_true",
        help="enforce the 07 G-4 lock gate: refuse a non-locked input",
    )
    parser.add_argument(
        "--allow-draft",
        dest="allow_draft",
        action="store_true",
        help="build against a draft input, reporting it and moving on",
    )
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
        if not specs_dir.is_dir():
            raise Refusal(f"refusing to build: --in {specs_dir} is not a directory.")
        dimensions = read_spec(specs_dir, DIMENSIONS_NAME)
        massing = read_spec(specs_dir, MASSING_NAME)
        registry = read_spec(specs_dir, REGISTRY_NAME)
        for name, document in (
            (DIMENSIONS_NAME, dimensions),
            (MASSING_NAME, massing),
            (REGISTRY_NAME, registry),
        ):
            require_locked(document, name, args.allow_draft, args.build_gate)
        world_rows = read_world_table(specs_dir)

        document, thickness = build_assembly(dimensions, massing, registry, world_rows)
        if args.build_gate and document.get("status") != "locked":
            raise Refusal(
                f"refusing to write: the emitted {OUT_JSON_NAME} would carry status "
                f"{document.get('status')!r}, and --build enforces the 07 G-4 lock gate on what "
                "it writes as well as on what it reads."
            )
        text = serialize(document)

        # Check the bytes, not the intention: parse the exact payload again and run
        # G-71..G-81 against it before anything reaches the disk.
        checked = strict_loads(text)
        script = render_ms(checked, massing, dimensions, registry, thickness)
        failures = self_check(
            checked, dimensions, massing, registry, world_rows, script
        )
        if failures:
            raise Refusal(
                f"refusing to write: the self-check failed {len(failures)} invariant(s).\n  - "
                + "\n  - ".join(failures[:20])
            )

        json_path = out_dir / OUT_JSON_NAME
        ms_path = out_dir / OUT_MS_NAME
        for target_path, payload in ((json_path, text), (ms_path, script)):
            target_bytes = payload.encode("utf-8")
            if target_path.is_file() and target_path.read_bytes() != target_bytes:
                raise Refusal(
                    f"refusing to overwrite {target_path}: differing existing content on disk (08.4 / A-WRITE / M34). "
                    "Resolve difference or remove file before rebuilding."
                )
        write_bytes(json_path, text)
        write_bytes(ms_path, script)
    except Refusal as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REFUSAL

    if args.as_json:
        placements = checked["placements"]
        cuts = checked["opening_cuts"]
        hosts: dict[str, int] = {}
        for cut in cuts:
            hosts[str(cut["host_ref"])] = hosts.get(str(cut["host_ref"]), 0) + 1
        print(
            json.dumps(
                {
                    "builder": "scripts/place_components.py",
                    "stage": args.stage,
                    "project": checked["project"],
                    "spec": checked["spec"],
                    "read": [str(specs_dir / name) for name in UPSTREAM_NAMES],
                    "wrote": [str(json_path), str(ms_path)],
                    "placements": len(placements),
                    "opening_cuts": len(cuts),
                    "scatter": len(checked["scatter"]),
                    "prototypes": len({str(p["component_id"]) for p in placements}),
                    "cut_hosts": hosts,
                    "cut_passes": [
                        len(cuts[start : start + MAX_MODIFIERS_PER_CALL])
                        for start in range(0, len(cuts), MAX_MODIFIERS_PER_CALL)
                    ],
                    "max_modifiers_per_call": MAX_MODIFIERS_PER_CALL,
                    "max_modifiers_per_node": MAX_MODIFIERS_PER_NODE,
                    "layer_application": "data only; assembly.ms assigns no layer to any node",
                    "layer_map": checked["layer_map"],
                    "defaults": checked["defaults"],
                    "functions": function_names(script),
                    "emitted_lines": len(script.splitlines()),
                    "self_check": {rule: "pass" for rule in RULES},
                    "exit_code": EXIT_OK,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(summarise(checked, script))
        print(f"  wrote    {json_path}")
        print(f"  wrote    {ms_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())