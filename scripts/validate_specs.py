#!/usr/bin/env python3
"""Validate spec files against references/07-spec-grammar.md (invariants G-1..G-83).

Pure data validation. Standard library only. Never raises on bad input: one
malformed file becomes a FAIL row, never a traceback, and the run continues so
the report still names every other problem it can see.

WHY THIS SCRIPT CANNOT TOUCH 3DS MAX
------------------------------------
The grammar it implements is deliberately upstream of the bridge. A spec file is
data, and every invariant in 07 section 9 is "a function over the parsed JSON"
(07 section 9 preamble). This script therefore never imports a Max library, never
opens a named pipe and never claims anything about a renderer, a plugin or a
scene. The first stage that touches Max is P3, long after these files are frozen.
The one 3ds Max fact in 07 (section 11) is a target version string, and it is not
asserted here -- a spec file is valid whether or not Max is installed.

WHAT A FRESH SCAFFOLD FAILS ON
------------------------------
``scripts/init_project.py`` emits a spec tree that passes this validator. The
checks that legitimately cannot pass without a real brief are:

* nothing. The scaffold emits a small *internally consistent* single-bay
  building rather than empty placeholders, so G-16..G-30 all evaluate. If you
  blank out a geometric key, the matching rule reports SKIP with the reason, not
  a silent PASS.
* reserved files (P3..P9) are schema-checked only. Per 07 S-4 a reserved file's
  key list is a promise, not a specification, so its body is reported SKIP with
  that reason rather than validated against a schema that does not exist yet.
* ``massing.json`` is written by ``init_project.py`` as an **empty draft stub**
  (``status: "draft"``, empty ``origins`` / ``storeys`` / ``elements``), because it
  is *computed* by ``build_spec.py``. Per 07 section 9.6 a draft massing file is
  not evaluated: ``G-34``..``G-38`` and ``G-40`` report SKIP with that reason, and
  only ``G-39`` -- which the stub satisfies -- keeps running. ``--allow-draft``
  forces the skipped rules to run and they fail, which is the point.

Exit codes
----------
    0   no FAIL rows (WARN is allowed unless --warnings-as-errors)
    1   at least one FAIL row
    2   usage error or unreadable input path

Usage
-----
    python scripts/validate_specs.py                       # ./specs/pipeline
    python scripts/validate_specs.py --dir path/to/specs
    python scripts/validate_specs.py --file examples/dimensions.json
    python scripts/validate_specs.py --json
    python scripts/validate_specs.py --warnings-as-errors
    python scripts/validate_specs.py --rule G-18           # one invariant
    python scripts/validate_specs.py --build              # enforce the lock gate
    python scripts/validate_specs.py --allow-draft        # draft work in progress
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, NamedTuple, Optional, Sequence

# --------------------------------------------------------------------------- #
# Constants declared by references/07-spec-grammar.md
# --------------------------------------------------------------------------- #

SUPPORTED_SCHEMA_MAJOR = 1

ENVELOPE_ORDER: tuple[str, ...] = (
    "schema_version",
    "spec",
    "project",
    "units",
    "source",
    "status",
)

#: 07 section 3.1, widened at P3: ``derived`` means the file was computed from
#: another spec in the same project, so ``source.reference`` must then name that
#: file (G-6).
SOURCE_KINDS = ("user_brief", "drawing", "image", "imported", "assumed", "derived")
STATUSES = ("draft", "locked", "superseded")
ORIGIN_VALUES = ("given", "assumed", "conflict", "derived")
OPENING_TYPES = ("window", "door", "entrance", "curtain_wall")
CONFIDENCES = ("high", "medium", "low")
#: G-15 ``recheck_stage``. P7 (materials), P8 (QA) and P9 (export) were
#: CANCELLED by the user on 2026-10-05, so a value naming one is vacuous --
#: nothing re-checks at a stage that does not exist. P10-P13 are close-out and
#: documentation passes, not re-examination points for a spec assumption.
RECHECK_STAGES = ("P3", "P4", "P5", "P6")
NON_CONFLICT_FALLBACK_ID = "R7"

PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?$")
LEDGER_ID_RE = re.compile(r"^[AC]-\d{3}$")

#: 07 section 9.5 -- the tolerance fallback used when a spec declares none.
FALLBACK_LINEAR_CM = 0.5
FALLBACK_AREA_M2 = 0.05
FALLBACK_ANGLE_DEG = 0.01

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARN = "WARN"
STATUS_SKIP = "SKIP"

_SEVERITY_ORDER = (STATUS_FAIL, STATUS_WARN, STATUS_SKIP, STATUS_PASS)


# --------------------------------------------------------------------------- #
# G-8 unit-suffix lint configuration (documented, so the lint is not noise)
# --------------------------------------------------------------------------- #

#: The twelve key names 07 section 9.1 G-8 calls out by name and calls "an
#: error, not a style preference". Matched as whole tokens.
UNIT_LINT_HARD_TOKENS = frozenset(
    {
        "height",
        "width",
        "depth",
        "thickness",
        "radius",
        "offset",
        "spacing",
        "sill",
        "head",
        "length",
        "rise",
        "run",
    }
)

#: Heuristic extension. A key whose final token is one of these is length-looking
#: even though 07 does not name it. These are the compound forms the pipeline
#: actually uses (``structural_bay``, ``core_diameter``).
UNIT_LINT_HEURISTIC_TOKENS = frozenset(
    {
        "apron",
        "bay",
        "centre",
        "center",
        "clear",
        "cover",
        "diameter",
        "elevation",
        "grid",
        "inset",
        "line",
        "perimeter",
        "plane",
        "plate",
        "reveal",
        "span",
        "storey",
        "story",
    }
)

#: Suffixes that mean the key already declares its unit or its non-unit nature.
UNIT_LINT_UNIT_SUFFIXES = ("_cm", "_m2", "_deg", "_pct")
UNIT_LINT_NON_UNIT_SUFFIXES = (
    "_count",
    "_index",
    "_indices",
    "_id",
    "_ids",
    "_ref",
    "_refs",
    "_name",
    "_kind",
    "_type",
    "_path",
    "_state",
    "_stage",
    "_at",
    "_ratio",
    "_ccw",
)

#: Keys exempt from G-8 by name. Two groups: the envelope (07 says ``units.length``
#: names a unit, it is not a length) and the vocabulary words of 07 sections 6-7
#: that carry prose or enumeration rather than a dimension.
#:
#: ``full_height`` (P5) is the first entry here whose final token is a *hard*
#: length token: it is a bool that says the v grid does not cut the panel, so the
#: word names an extent that is deliberately **not** a dimension. The heuristic
#: would otherwise ask for a ``_cm`` suffix on a bool, which is the lint becoming
#: noise rather than a finding.
UNIT_LINT_EXEMPT_KEYS = frozenset(
    {
        "alternatives_considered",
        "assumption_ref",
        "assumptions",
        "at",
        "chosen_sources",
        "chosen_value",
        "confidence",
        "conflict_ref",
        "conflict_sourced_paths",
        "conflicts",
        "cross_references",
        "derives_from",
        "detected_in",
        "downstream_effect",
        "downstream_stages",
        "evaluation_order",
        "field_path",
        "full_height",
        "invalidated_by",
        "lang",
        "layer",
        "note",
        "non_conflict_fallback",
        "origin",
        "origin_ref",
        "origin_inputs",
        "origins",
        "path",
        "precedence_rules",
        "reason",
        "recheck_stage",
        "rejected",
        "rejected_ref",
        "replacement",
        "resolution",
        "resolved_paths",
        "resulting_value_of",
        "rule_names_as_proposed",
        "rules_invoked",
        "source",
        "stage",
        "statement",
        "supersedes",
        "tolerances",
        "title",
        "units",
        "url",
        "value",
        "why_lost",
        "why_not",
    }
)


# --------------------------------------------------------------------------- #
# massing.json vocabulary (G-34..G-40, 07 section 8.1 and 9.6)
#
# ``references/07-spec-grammar.md`` is the single source of truth for all three
# tables below; they are transcribed here once and never re-derived elsewhere in
# the script. ``references/11-layer-standard.md`` documents the intent of each
# layer and must not introduce a ninth name without changing 07 section 8.1.4
# first.
# --------------------------------------------------------------------------- #

#: 07 section 8.1.2 -- kind -> layer is a table, not a preference, because
#: ``assembly.json.layer_map`` (P6) resolves against it.
MASSING_KIND_LAYER: dict[str, str] = {
    "plinth": "00_SITE",
    "slab": "01_SLABS",
    "column": "02_STRUCTURE",
    "core_wall": "03_CORE",
    "roof_deck": "04_ROOF",
    "parapet": "04_ROOF",
    "facade_wall": "05_FACADE",
}

#: 07 section 8.1.1 element kinds. The vocabulary and the layer map are the same
#: names in 07, so the tuple is taken from the map rather than restated.
MASSING_ELEMENT_KINDS: tuple[str, ...] = tuple(MASSING_KIND_LAYER)

#: 09-defaults.md ``D-FW-01`` -- the assumed thickness of an opaque facade wall
#: band, carried in ``massing.json:defaults`` so G-38 can recompute the P6
#: ``facade_wall`` profile from the facade runs. Ledger entry ``A-025``.
MASSING_FACADE_WALL_THICKNESS_LEAF = "defaults.facade_wall_thickness_cm"
MASSING_FACADE_WALL_THICKNESS_LEDGER = "A-025"

#: G-36's derived-only clause is scoped to the **value tree**.  P6 is the first
#: stage to put an assumed value in a derived massing file -- the one key above
#: -- for exactly the reason P5 put two in ``components_registry.json``: nothing
#: in ``dimensions.json`` dimensions a facade build-up, so the value cannot be
#: derived and must not be presented as if it were.  So an entry under the
#: ``defaults`` block may be ``assumed`` and must carry its ``origin_ref`` (G-10
#: checks the pairing); **every geometry leaf is still ``derived``**, so the
#: exception cannot be stretched to cover invented massing.  This mirrors how
#: G-64 scopes the same clause for the registry (``A-023`` / ``A-024``).
MASSING_ASSUMED_PREFIX = "defaults."

#: 07 section 8.1.4 -- the layer vocabulary is closed at eight names.
MASSING_LAYERS: tuple[str, ...] = (
    "00_SITE",
    "01_SLABS",
    "02_STRUCTURE",
    "03_CORE",
    "04_ROOF",
    "05_FACADE",
    "90_SCENE",
    "99_DEBUG",
)

#: 07 section 8.1.1 fixes these two layer values by name: the site pad is
#: ground, and a grouping layer holds the dummy, never the payload.
MASSING_SITE_PAD_LAYER = "00_SITE"
MASSING_GROUPING_LAYER = "90_SCENE"

#: 07 section 8.1.1 -- the two id shapes in a massing file.
ELEMENT_ID_RE = re.compile(r"^EL-\d{3}$")
GROUPING_ID_RE = re.compile(r"^GRP-\d{3}$")
ELEMENT_ID_PATTERN = r"^EL-\d{3}$"
GROUPING_ID_PATTERN = r"^GRP-\d{3}$"


# --------------------------------------------------------------------------- #
# 07 section 8.3 / 8.4 -- the facade_grids.json and components_registry.json
# schemas
#
# Transcribed from references/_p5-contract.md sections 3 and 5, which is the
# authoritative design for P5. Every name below is geometric or a *role*; none
# of them names a MAXScript class, a modifier, a plugin or an MCP tool (07
# section 11), so ``material_role`` is ``glazing`` / ``opaque`` / ``frame`` and a
# component's ``kind`` is ``glazed_panel`` rather than a renderer class.
# --------------------------------------------------------------------------- #

#: 07 section 8.3.3 -- the two id shapes in a facade_grids file, and the two in a
#: components_registry file.
AXIS_ID_RE = re.compile(r"^AX-\d{3}$")
PANEL_ID_RE = re.compile(r"^PNL-\d{3}$")
AXIS_ID_PATTERN = r"^AX-\d{3}$"
PANEL_ID_PATTERN = r"^PNL-\d{3}$"
COMPONENT_ID_RE = re.compile(r"^CMP-\d{3}$")
FAMILY_ID_RE = re.compile(r"^FAM-\d{3}$")
VARIANT_ID_RE = re.compile(r"^VAR-\d{3}$")
COMPONENT_ID_PATTERN = r"^CMP-\d{3}$"
FAMILY_ID_PATTERN = r"^FAM-\d{3}$"
VARIANT_ID_PATTERN = r"^VAR-\d{3}$"

#: 07 section 8.3.3 -- an axis is either along the run or up the storey, and one
#: of four things created it.
FACADE_AXIS_FAMILIES: tuple[str, ...] = ("u", "v")
FACADE_AXIS_KINDS: tuple[str, ...] = ("bay", "opening_edge", "level_base", "level_top")

#: 07 section 8.3.5 -- the six reserved panel kinds, and the ceiling G-63 holds
#: every declared kind inside. The table is *data*, so a project declares only
#: the kinds it uses.
FACADE_PANEL_KINDS: tuple[str, ...] = (
    "vision",
    "spandrel",
    "mullion",
    "transom",
    "punched_window",
    "blank",
)
FACADE_PANEL_KIND_CEILING = 6

#: 07 section 8.3.5 -- ``material_role`` is a role for P7, never a material class.
FACADE_MATERIAL_ROLES: tuple[str, ...] = ("glazing", "opaque", "frame")

#: 07 section 8.4.3 -- the four component kinds.
COMPONENT_KINDS: tuple[str, ...] = (
    "glazed_panel",
    "opaque_panel",
    "frame_member",
    "entrance_door",
)

#: 07 section 8.5 -- the ordered parameter list every component carries, and the
#: block each name reads. A builder needs a *stable order*, so this is a
#: sequence and not a set.
COMPONENT_PARAMETER_ORDER: tuple[str, ...] = (
    "width_cm",
    "height_cm",
    "thickness_cm",
    "joint_width_cm",
)
COMPONENT_PARAMETER_SOURCES: dict[str, str] = {
    "width_cm": "size_cm",
    "height_cm": "size_cm",
    "thickness_cm": "defaults",
    "joint_width_cm": "defaults",
}

#: 07 section 8.5.2 -- ``defaults`` carries exactly these two, and they are the
#: only invented values in P5: both already exist in 09-defaults.md as
#: reference-only conventions with a declared range, so they are ``assumed`` with
#: a ledger entry (A-023 / A-024), never ``derived``.
COMPONENT_DEFAULT_KEYS: tuple[str, ...] = ("panel_thickness_cm", "joint_width_cm")
COMPONENT_DEFAULT_RANGES: dict[str, tuple[float, float]] = {
    "panel_thickness_cm": (2.0, 8.0),
    "joint_width_cm": (1.0, 4.0),
}

#: 07 section 8.3.4 / 8.4.4 -- both files target the facade layer. Layer is data
#: here: it is unassignable from MAXScript, so P6 applies it and no builder emits
#: layer code.
FACADE_SPEC_LAYER = "05_FACADE"

#: 07 section 8.5 -- a family's substitution rule, the only one declared.
COMPONENT_SUBSTITUTION = "size_matched"

#: 07 section 8.5.6 -- the opening types that turn a glazed panel into a door.
COMPONENT_DOOR_OPENING_TYPES: tuple[str, ...] = ("door", "entrance")

#: How many offending ids a single FAIL row names before the count takes over.
P5_ID_LIST_LIMIT = 10


# --------------------------------------------------------------------------- #
# 07 section 8.2 -- the nurbs.json schema
# --------------------------------------------------------------------------- #

#: 07 section 8.2.3 -- the four lattice construction routes, all executed live on
#: 2026-10-04. ``point_grid`` interpolates its lattice and ``cv_grid`` only
#: pulls, which is why they are separate kinds and not two spellings of one.
#:
#: The P4b schema extension (CHECKPOINT section "P4b schema extension", which is
#: the authoritative contract) adds four more: ``rail_sweep``,
#: ``two_rail_sweep``, ``blend`` and ``trim``. The standing rule is preserved --
#: every name here is geometric and none of them names a MAXScript class, a
#: plugin or a tool. All eight were executed live before the 2026-10-04 P4b
#: correction; see CHECKPOINT section "Rail sweeps, blends and trims".
NURBS_SURFACE_KINDS: tuple[str, ...] = (
    "u_loft",
    "uv_loft",
    "point_grid",
    "cv_grid",
    "rail_sweep",
    "two_rail_sweep",
    "blend",
    "trim",
)

#: The subset the library indexes as a lattice, ``(iv - 1) * nU + iu``. Only these
#: consume rows that must share a point count (G-42). A rail, a trim profile and
#: a blend parent are section rows too, but they are independent curves, not a
#: lattice stride -- a 3-point rail beside a 5-point cross-section is a correct
#: ``rail_sweep``, not a stride that lands on the wrong point.
NURBS_LATTICE_KINDS: tuple[str, ...] = ("u_loft", "uv_loft", "point_grid", "cv_grid")

#: The four kinds G-50..G-54 govern, and the only kinds for which those rules
#: register a row at all. A file that declares none of them is outside their
#: scope: see ``check_nurbs_rules``.
NURBS_P4B_KINDS: tuple[str, ...] = ("rail_sweep", "two_rail_sweep", "blend", "trim")

#: P4b -- a sweep's rails and a trim's profiles reuse the existing ``sections[]``
#: primitive (an ordered list of ``points_cm``), so they reference ``SEC-nnn``
#: ids under their own key names. ``section_ids`` keeps its existing meaning: the
#: swept cross-sections.
NURBS_RAIL_SECTION_KEY = "rail_section_ids"
NURBS_TRIM_SECTION_KEY = "trim_section_ids"

#: P4b -- how many rails each sweep kind takes, exactly (G-50). Both counts were
#: executed live: ``NURBS1RailSweepSurface`` takes one, ``NURBS2RailSweepSurface``
#: takes ``rail1`` and ``rail2``.
NURBS_RAIL_COUNTS: dict[str, int] = {"rail_sweep": 1, "two_rail_sweep": 2}

#: P4b -- a sweep needs at least two cross-sections to sweep between. Stated in
#: the P4b key table ("section_ids (>=2 cross-sections)"), so G-50 enforces it as
#: declared rather than as an invention.
NURBS_MIN_SWEEP_SECTIONS = 2

#: P4b -- ``edge1`` / ``edge2`` are 1..4 = low-U, high-U, low-V, high-V. The
#: verified transcripts used ``edge1: 1 edge2: 1`` and read back exactly.
NURBS_BLEND_EDGES: tuple[int, ...] = (1, 2, 3, 4)

#: 07 section 8.2.5 -- the two derivative kinds.
NURBS_DERIVATIVE_KINDS: tuple[str, ...] = ("quad_panels", "space_frame")

#: 07 section 8.2.2 -- a surface carries roof or facade geometry only.
NURBS_SURFACE_LAYERS: tuple[str, ...] = ("04_ROOF", "05_FACADE")

#: 07 section 8.2.5 -- a derivative may also be a QA intermediate.
NURBS_DERIVATIVE_LAYERS: tuple[str, ...] = ("04_ROOF", "05_FACADE", "99_DEBUG")

#: 07 section 8.2.2 -- the keys every surface may carry whatever its kind is.
#: Anything outside this set plus the kind's own required/optional keys is
#: forbidden, which is how a ``u_loft`` is stopped from declaring ``u_order``.
NURBS_SURFACE_COMMON_KEYS: tuple[str, ...] = (
    "layer",
    "mat_id",
    "hide_curves",
    "merge_tol_cm",
    "approximation",
)

#: 07 section 8.2.2 -- exactly the keys each kind needs, and nothing else.
#: The P4b rows are transcribed from the authoritative key table. ``parallel`` is
#: optional because the design gives it a default ("bool, default true"). The four
#: keys in NURBS_P4B_DEFAULTS are optional for the same reason and no other: they
#: are exactly the keys the BUILDER substitutes for. ``surface_ref`` /
#: ``trim_section_ids`` / ``p_vec`` stay required -- a projection with no surface,
#: no profile and no direction is not a projection, and no builder substitutes a
#: default for any of the three.
NURBS_KIND_REQUIRED: dict[str, tuple[str, ...]] = {
    "u_loft": ("section_ids",),
    "uv_loft": ("u_section_ids", "v_section_ids"),
    "point_grid": ("section_ids",),
    "cv_grid": ("section_ids",),
    "rail_sweep": ("rail_section_ids", "section_ids"),
    "two_rail_sweep": ("rail_section_ids", "section_ids"),
    "blend": ("parent1_ref", "edge1", "parent2_ref", "edge2"),
    "trim": ("surface_ref", "trim_section_ids", "p_vec"),
}

NURBS_KIND_OPTIONAL: dict[str, tuple[str, ...]] = {
    "u_loft": ("closed_sections", "thickness_cm"),
    "uv_loft": (),
    "point_grid": (),
    "cv_grid": ("u_order", "v_order", "weights"),
    "rail_sweep": ("parallel",),
    "two_rail_sweep": ("parallel",),
    "blend": ("tension1", "tension2"),
    "trim": ("seed", "flip_trim"),
}

#: The keys the builder substitutes when a spec omits them, and their values. These
#: are the documented defaults, and the only substitution this schema sanctions.
#:
#: ``tension1`` / ``tension2`` default to **0.0**, not the 1.0 the P4b key table
#: recorded. ``NURBSBlendSurface`` tension measures the deviation from a straight
#: transition between the two selected edges; 0.0 IS that straight transition, and
#: 1.0 is not a neutral value -- on the worked example it pushed the soffit 295.64 cm
#: past the vault's own 900 cm depth and 50 cm below the springing (D1). Max does
#: not bound that overshoot above, which is why G-55 bounds the input instead.
NURBS_P4B_DEFAULTS: dict[str, Any] = {
    "parallel": True,
    "tension1": 0.0,
    "tension2": 0.0,
    "seed": (0.5, 0.5),
    "flip_trim": False,
}

#: G-55 -- the range a blend tension is held to, compared exactly (no epsilon).
#: 0.0 is the straight transition between the two selected edges; above 0 the blend
#: is pushed outward past both parents and the overshoot grows with the tension.
NURBS_TENSION_MIN = 0.0
NURBS_TENSION_MAX = 1.0

#: G-56 -- the kinds whose committed node hands a ``nurbsID`` to a relation. A
#: relation names its parent through ``parent1ID:`` / ``parent2ID:``, read from the
#: parent's FIRST committed ``NURBSSurface`` (D3), so a parent must be a kind that
#: commits at least one. ``trim`` commits NONE: ``trim:false`` "produces no surface
#: at all", and ``trim:true`` does not cut -- it appends an untrimmed ``NURBSCVSurface``
#: COPY of the parent (D5). A parent with no surface has no id to bind, and the only
#: way to fill the slot is a literal, which D4 measured as a hard
#: ``EXCEPTION_ACCESS_VIOLATION`` crash of the Max process rather than an error.
NURBS_ID_BEARING_KINDS: tuple[str, ...] = (
    "u_loft",
    "uv_loft",
    "point_grid",
    "cv_grid",
    "rail_sweep",
    "two_rail_sweep",
    "blend",
)

#: 07 section 8.2.4 -- the approximation block maps applyArchTessellation.
NURBS_APPROX_KEYS: tuple[str, ...] = (
    "view_steps_u",
    "view_steps_v",
    "render_edge_pct",
    "render_angle_deg",
    "merge_tol_cm",
)

NURBS_APPROX_DEFAULTS: dict[str, float] = {
    "view_steps_u": 6.0,
    "view_steps_v": 6.0,
    "render_edge_pct": 4.0,
    "render_angle_deg": 6.0,
    "merge_tol_cm": 0.15,
}

NURBS_SURFACE_DEFAULTS: dict[str, Any] = {
    "layer": "04_ROOF",
    "mat_id": 1,
    "hide_curves": True,
    "merge_tol_cm": 0.15,
}

NURBS_DERIVATIVE_DEFAULTS: dict[str, Any] = {
    "layer": "99_DEBUG",
    "thickness_cm": 10.0,
    "sub_steps": 4,
}

#: 07 section 8.2 -- the three id shapes in a nurbs file.
SECTION_ID_RE = re.compile(r"^SEC-\d{3}$")
SURFACE_ID_RE = re.compile(r"^SUR-\d{3}$")
DERIVATIVE_ID_RE = re.compile(r"^DRV-\d{3}$")
SECTION_ID_PATTERN = r"^SEC-\d{3}$"
SURFACE_ID_PATTERN = r"^SUR-\d{3}$"
DERIVATIVE_ID_PATTERN = r"^DRV-\d{3}$"

#: 07 section 8.2.2 -- an order outside this range is not a degree choice.
NURBS_MIN_ORDER = 2
NURBS_MAX_ORDER = 5

#: 07 section 8.2.2 and G-47 -- ``createULoftShell`` tests ``abs thickness >
#: 0.001`` and *silently omits* the offset surface otherwise, so a thinner shell
#: is a spec that builds to nothing rather than a rounding detail.
NURBS_MIN_SHELL_THICKNESS_CM = 0.001


# --------------------------------------------------------------------------- #
# Section 4 inventory
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SpecDef:
    """One row of the 07 section 4 inventory table."""

    name: str
    owner: str
    state: str  # "defined" | "reserved"
    body_keys: tuple[str, ...]  # after the envelope, in declared order
    leaf_skip_top: frozenset = frozenset()
    has_origins: bool = False


SPEC_INVENTORY: tuple[SpecDef, ...] = (
    SpecDef(
        "dimensions",
        "P2a",
        "defined",
        (
            "tolerances",
            "origins",
            "building",
            "site",
            "structure",
            "levels",
            "core",
            "floor_plates",
            "roof",
            "facades",
            "openings",
        ),
        frozenset({"origins"}),
        has_origins=True,
    ),
    SpecDef(
        "conflicts_resolved",
        "P2a",
        "defined",
        ("precedence_rules", "conflicts"),
    ),
    SpecDef(
        "assumptions",
        "P2a",
        "defined",
        ("assumptions", "cross_references"),
    ),
    SpecDef(
        "massing",
        "P3",
        "defined",
        (
            "tolerances",
            "origin_inputs",
            "origins",
            "defaults",
            "storeys",
            "elements",
            "site_pad",
            "grouping",
        ),
        frozenset({"origins"}),
        has_origins=True,
    ),
    SpecDef(
        "nurbs",
        "P4",
        "defined",
        (
            "tolerances",
            "origin_inputs",
            "origins",
            "sections",
            "surfaces",
            "derivatives",
        ),
        frozenset({"origins"}),
        has_origins=True,
    ),
    SpecDef(
        "facade_grids",
        "P5",
        "defined",
        (
            "tolerances",
            "origin_inputs",
            "origins",
            "facades",
            "axes",
            "panels",
            "panel_types",
        ),
        frozenset({"origins"}),
        has_origins=True,
    ),
    SpecDef(
        "components_registry",
        "P5",
        "defined",
        (
            "tolerances",
            "origin_inputs",
            "origins",
            "defaults",
            "component_types",
            "components",
            "families",
        ),
        frozenset({"origins"}),
        has_origins=True,
    ),
    SpecDef(
        "assembly",
        "P6",
        "defined",
        (
            "tolerances",
            "origin_inputs",
            "origins",
            "defaults",
            "layer_map",
            "placements",
            "opening_cuts",
            "wall_cells",
            "scatter",
        ),
        frozenset({"origins"}),
        has_origins=True,
    ),
    SpecDef(
        "materials",
        "P7",
        "reserved",
        ("tolerances", "origin_inputs", "renderer", "materials", "uv_rules"),
    ),
    SpecDef(
        "qa",
        "P8",
        "reserved",
        (
            "tolerances",
            "origin_inputs",
            "checks",
            "determinism",
            "captures",
            "verdict",
        ),
    ),
    SpecDef(
        "export",
        "P9",
        "reserved",
        ("tolerances", "origin_inputs", "exports", "tessellation", "delivery"),
    ),
)

SPEC_BY_NAME = {spec.name: spec for spec in SPEC_INVENTORY}

RULE_TITLES: dict[str, str] = {
    "G-1": "envelope keys present, first, in order",
    "G-2": "spec matches filename",
    "G-3": "schema_version major is supported",
    "G-4": "status is known, and only locked builds",
    "G-5": "units are cm and deg",
    "G-6": "source is well formed",
    "G-7": "file hygiene",
    "G-8": "unit suffix lint",
    "G-9": "origins covers the value tree, exactly once",
    "G-10": "origin / origin_ref pairing",
    "G-11": "ledger ids are unique and well formed",
    "G-12": "ledger entries match the spec",
    "G-13": "ledger bijection",
    "G-14": "conflict entries are complete",
    "G-15": "assumption entries are complete",
    "G-16": "range compliance",
    "G-17": "levels ordered bottom to top",
    "G-18": "level chaining",
    "G-19": "total height equals the top of the chain",
    "G-20": "overall height includes the parapet",
    "G-21": "polygons are simple and winding is declared",
    "G-22": "core is inside the building",
    "G-23": "core sits on the structural grid",
    "G-24": "grid spans the footprint",
    "G-25": "facades close",
    "G-26": "openings are physically sane",
    "G-27": "openings fit their host bay",
    "G-28": "openings do not collide or duplicate",
    "G-29": "area arithmetic is consistent",
    "G-30": "roof is consistent",
    "G-31": "cross-file references resolve",
    "G-32": "derived values recompute",
    "G-33": "tolerances are declared",
    "G-34": "element identity",
    "G-35": "element solidity",
    "G-36": "massing provenance",
    "G-37": "storey chain",
    "G-38": "element-to-dimension agreement",
    "G-39": "layer vocabulary",
    "G-40": "grouping completeness",
    "G-41": "nurbs identity and naming",
    "G-42": "section shape and rectangularity",
    "G-43": "kind fits its keys",
    "G-44": "nurbs references resolve and nothing is orphaned",
    "G-45": "nurbs kind-specific cardinality",
    "G-46": "nurbs order is meaningful, not clamped away",
    "G-47": "nurbs thickness is meaningful",
    "G-48": "derivative fitness",
    "G-49": "nurbs provenance",
    "G-50": "P4b kind arity",
    "G-51": "a sweep's cross-sections reach its rails",
    "G-52": "blend parents are declared earlier, edges are 1..4",
    "G-53": "trim projection vector, seed and flip are well formed",
    "G-54": "emitted-surface census (build time, SKIP at lint time)",
    "G-55": "blend tension is a bounded float",
    "G-56": "a relation parent hands a real nurbsID, never a synthetic pointer",
    "G-57": "facade agreement and run angle",
    "G-58": "axis integrity",
    "G-59": "panel rectangle integrity",
    "G-60": "panel edges lie on axes",
    "G-61": "complete partition",
    "G-62": "one opening, one panel",
    "G-63": "panel-kind vocabulary and layer",
    "G-64": "grid provenance",
    "G-65": "component identity",
    "G-66": "component parameters recompute",
    "G-67": "component fits the panel kinds it serves",
    "G-68": "every panel is placeable",
    "G-69": "variant discipline",
    "G-70": "emitted-table census (build time, SKIP at lint time)",
    "G-71": "every placement names a real component",
    "G-72": "placements and world_table.csv rows are equal in both directions",
    "G-73": "placement geometry equals its table row",
    "G-74": "node names are unique and identifier-safe",
    "G-75": "layers come from layer_map, and layer_map keys are in the vocabulary",
    "G-76": "every cut is on a real facade_wall, inside it, and deep enough",
    "G-77": "one opening, one cut, in both directions",
    "G-78": "scatter ranges and reference resolution",
    "G-79": "no layer assignment in the emitted MAXScript (build time)",
    "G-80": "emitted census (build time, SKIP at lint time)",
    "G-81": "zero modifiers (build time)",
    "G-82": "cells tile each host exactly (volume identity)",
    "G-83": "every cell carries its wall's full thickness",
}

#: Rules that read more than one file. Reported grouped by severity, never by file.
#: G-36..G-38 qualify because they resolve massing provenance, the storey chain
#: and the element geometry against dimensions.json through the same loader.
#: G-58 qualifies from P5 because "a bay with no opening contributes exactly its
#: level_base and level_top" is read from dimensions.json openings[] -- the v
#: division is per bay, so which bays have no opening is not a fact this file can
#: decide on its own.
CROSS_FILE_RULES = (
    "G-9",
    "G-10",
    "G-11",
    "G-12",
    "G-13",
    "G-14",
    "G-15",
    "G-31",
    "G-32",
    "G-33",
    "G-36",
    "G-37",
    "G-38",
    "G-49",
    "G-58",
    "G-62",
    "G-63",
    "G-67",
    "G-68",
    "G-71",
    "G-72",
    "G-73",
    "G-75",
    "G-76",
    "G-77",
    "G-78",
)


# --------------------------------------------------------------------------- #
# G-16 range table (07 sections 5 and 5.11)
# --------------------------------------------------------------------------- #

# (path pattern, low, high, low_inclusive, high_inclusive, unit)
RangeRule = tuple[str, Optional[float], Optional[float], bool, bool, str]

RANGE_RULES: tuple[RangeRule, ...] = (
    ("building.total_height_cm", 250.0, None, False, True, "cm"),
    ("building.overall_height_cm", 250.0, None, False, True, "cm"),
    ("building.gross_floor_area_m2", 0.0, None, False, True, "m2"),
    ("building.net_floor_area_m2", 0.0, None, False, True, "m2"),
    ("site.footprint_area_m2", 0.0, None, False, True, "m2"),
    ("site.footprint_width_cm", 0.0, None, False, True, "cm"),
    ("site.footprint_depth_cm", 0.0, None, False, True, "cm"),
    ("site.plot_rotation_deg", -180.0, 180.0, True, True, "deg"),
    ("site.setback_cm", 0.0, 3000.0, True, True, "cm"),
    ("structure.x_bay_cm[]", 300.0, 1200.0, True, True, "cm"),
    ("structure.y_bay_cm[]", 300.0, 1200.0, True, True, "cm"),
    ("structure.column_x_cm[]", 0.0, None, False, True, "cm"),
    ("structure.column_y_cm[]", 0.0, None, False, True, "cm"),
    ("structure.column_section_cm[]", 20.0, 80.0, True, True, "cm"),
    ("structure.interior_column_count", 0.0, None, True, True, ""),
    ("levels[].height_cm", 250.0, 600.0, True, True, "cm"),
    ("core.footprint_area_m2", 0.0, None, False, True, "m2"),
    ("core.wall_thickness_cm", 15.0, 40.0, True, True, "cm"),
    ("floor_plates[].thickness_cm", 15.0, 45.0, True, True, "cm"),
    ("floor_plates[].gross_area_m2", 0.0, None, False, True, "m2"),
    ("floor_plates[].net_usable_area_m2", 0.0, None, False, True, "m2"),
    ("roof.deck_level_cm", 0.0, None, False, True, "cm"),
    ("roof.deck_thickness_cm", 15.0, 45.0, True, True, "cm"),
    ("roof.slope_deg", 0.0, 15.0, True, True, "deg"),
    ("roof.parapet_height_cm", 60.0, 150.0, True, True, "cm"),
    ("roof.parapet_thickness_cm", 15.0, 45.0, True, True, "cm"),
    ("roof.coping_overhang_cm", 0.0, 10.0, True, True, "cm"),
    ("facades[].direction_deg", 0.0, 360.0, True, True, "deg"),
    ("facades[].length_cm", 0.0, None, False, True, "cm"),
    ("facades[].bay_count", 1.0, 60.0, True, True, ""),
    ("facades[].bay_width_cm[]", 300.0, 1200.0, True, True, "cm"),
)

#: 07 section 5.11 per-type opening ranges, all inclusive.
OPENING_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "window": {"width_cm": (60.0, 420.0), "sill_cm": (0.0, 150.0), "head_cm": (150.0, 350.0)},
    "door": {"width_cm": (80.0, 150.0), "sill_cm": (0.0, 0.0), "head_cm": (180.0, 260.0)},
    "entrance": {"width_cm": (120.0, 300.0), "sill_cm": (0.0, 0.0), "head_cm": (200.0, 320.0)},
    "curtain_wall": {
        "width_cm": (100.0, 600.0),
        "sill_cm": (0.0, 30.0),
        "head_cm": (250.0, 450.0),
    },
}

#: 07 section 9.8 -- the G-16 ranges for the two P5 files, which are separate
#: tables because the paths are relative to *their* documents rather than to
#: dimensions.json. Everything 07 does not bound here stays unbounded, as the
#: contract says.
P5_RANGE_RULES: dict[str, tuple[RangeRule, ...]] = {
    "facade_grids": (
        ("facades[].bay_width_cm[]", 300.0, 1200.0, True, True, "cm"),
        ("facades[].length_cm", 0.0, None, False, True, "cm"),
        ("facades[].bay_offsets_cm[]", 0.0, None, True, True, "cm"),
        ("facades[].bay_centre_cm[]", 0.0, None, True, True, "cm"),
        # ``-180 < x <= 180`` and not the closed interval: the run angle is
        # normalised to that half-open range, so -180.0 is not a legal value and
        # 180.0 is (the contract is explicit that 180.0 stays 180.0).
        ("facades[].run_angle_deg", -180.0, 180.0, False, True, "deg"),
        ("axes[].offset_cm", 0.0, None, True, True, "cm"),
        ("panels[].width_cm", 0.0, None, False, True, "cm"),
        ("panels[].height_cm", 0.0, None, False, True, "cm"),
    ),
    "components_registry": (
        ("components[].size_cm[]", 0.0, None, False, True, "cm"),
        ("defaults.panel_thickness_cm", 2.0, 8.0, True, True, "cm"),
        ("defaults.joint_width_cm", 1.0, 4.0, True, True, "cm"),
    ),
}


# --------------------------------------------------------------------------- #
# Findings
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Finding:
    """One row of the report."""

    rule: str
    severity: str  # FAIL | WARN | SKIP | PASS
    location: str
    detail: str
    tolerance: str = ""

    @property
    def status(self) -> str:
        return self.severity


class Report:
    """Collects findings and applies the --warnings-as-errors promotion."""

    def __init__(self, warnings_as_errors: bool = False) -> None:
        self.findings: list[Finding] = []
        self.warnings_as_errors = warnings_as_errors

    def add(
        self,
        rule: str,
        severity: str,
        location: str,
        detail: str,
        tolerance: str = "",
    ) -> None:
        if severity == STATUS_WARN and self.warnings_as_errors:
            severity = STATUS_FAIL
            if detail:
                detail = f"{detail} (WARN promoted by --warnings-as-errors)"
        self.findings.append(Finding(rule, severity, location, detail, tolerance))

    def ok(self, rule: str, location: str, detail: str, tolerance: str = "") -> None:
        self.add(rule, STATUS_PASS, location, detail, tolerance)

    def fail(self, rule: str, location: str, detail: str, tolerance: str = "") -> None:
        self.add(rule, STATUS_FAIL, location, detail, tolerance)

    def warn(self, rule: str, location: str, detail: str, tolerance: str = "") -> None:
        self.add(rule, STATUS_WARN, location, detail, tolerance)

    def skip(self, rule: str, location: str, detail: str) -> None:
        self.add(rule, STATUS_SKIP, location, detail)

    def counts(self) -> dict[str, int]:
        return {
            status: sum(1 for f in self.findings if f.severity == status)
            for status in _SEVERITY_ORDER
        }


# --------------------------------------------------------------------------- #
# Path resolution: "levels[1].height_cm"
# --------------------------------------------------------------------------- #

_TOKEN_RE = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def split_path(path: str) -> list[Any]:
    """``"levels[1].height_cm"`` -> ``["levels", 1, "height_cm"]``."""
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


def path_of(tokens: Sequence[Any]) -> str:
    out = ""
    for token in tokens:
        if isinstance(token, int):
            out += f"[{token}]"
        elif out:
            out += "." + str(token)
        else:
            out = str(token)
    return out


def resolve(document: Any, path: str) -> tuple[bool, Any]:
    """Resolve a dotted path. Returns ``(found, value)``."""
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


def iter_pattern(document: Any, pattern: str) -> Iterable[tuple[str, Any]]:
    """Yield concrete ``(path, value)`` pairs for a ``[]`` wildcard pattern.

    ``"levels[].height_cm"`` becomes steps ``levels`` / wildcard / ``height_cm``
    and expands to ``levels[0].height_cm`` ... ``levels[n].height_cm``. A pattern
    with no wildcard yields exactly the one resolved path. A pattern that does not
    resolve yields nothing -- the caller reports the missing key separately, so a
    silent empty expansion never reads as a pass.
    """
    steps: list[tuple[str, bool]] = []
    for segment in pattern.replace("[]", "[*]").split("."):
        if segment.endswith("[*]"):
            steps.append((segment[:-3], True))
        else:
            steps.append((segment, False))

    def walk(node: Any, prefix: str, index: int) -> Iterable[tuple[str, Any]]:
        if index >= len(steps):
            if prefix:
                yield prefix, node
            return
        key, wildcard = steps[index]
        if not isinstance(node, dict) or key not in node:
            return
        child_path = f"{prefix}.{key}" if prefix else key
        child = node[key]
        if wildcard:
            # ``levels[].height_cm`` walks into every element of levels[].
            # ``structure.x_bay_cm[]`` is the same marker on a scalar array.
            if not isinstance(child, list):
                return
            for item_index, item in enumerate(child):
                yield from walk(item, f"{child_path}[{item_index}]", index + 1)
            return
        yield from walk(child, child_path, index + 1)

    yield from walk(document, "", 0)


def path_matches(pattern: str, path: str) -> bool:
    """True when a ``[]`` wildcard pattern names this concrete path."""
    pattern_tokens = pattern.replace("[]", "[0]").split(".")
    path_tokens = path.split(".")
    if len(pattern_tokens) != len(path_tokens):
        return False
    for pat, actual in zip(pattern_tokens, path_tokens):
        p_index, a_index = pat.find("["), actual.find("[")
        if p_index != a_index:
            return False
        if p_index >= 0:
            if pat[:p_index] != actual[:a_index]:
                return False
        elif pat != actual:
            return False
    return True


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #


def deep_equal(left: Any, right: Any) -> bool:
    """Structural equality; int/float compare numerically, bool strictly."""
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False
        return all(deep_equal(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False
        return all(deep_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 1e-9
    return left == right


def as_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def fmt_number(value: Any) -> str:
    number = as_number(value)
    if number is None:
        return json.dumps(value, sort_keys=True)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.4g}"


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def close(a: Optional[float], b: Optional[float], tol: float) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= tol + 1e-9


def parse_iso8601(text: str) -> bool:
    try:
        datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return False
    return "T" in text or " " in text


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def is_point(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) in (2, 3)
        and all(as_number(component) is not None for component in value)
    )


def ring_of(value: Any) -> list[list[float]]:
    return [[as_number(p[0]) or 0.0, as_number(p[1]) or 0.0] for p in value if is_point(p)]


def polygon_signed_area_cm2(ring: Sequence[Sequence[float]]) -> float:
    total = 0.0
    count = len(ring)
    for index in range(count):
        x1, y1 = ring[index]
        x2, y2 = ring[(index + 1) % count]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def polygon_area_m2(ring: Sequence[Sequence[float]]) -> float:
    return abs(polygon_signed_area_cm2(ring)) / 10000.0


def expand_footprint_ring(value: Any, kind: str) -> Optional[list[list[float]]]:
    """07 section 5.4: a rectangle may be two corners; read it as a 4-ring CCW."""
    ring = ring_of(value)
    if kind != "rectangle" or len(ring) != 2:
        return ring
    (x1, y1), (x2, y2) = ring
    xlo, xhi = min(x1, x2), max(x1, x2)
    ylo, yhi = min(y1, y2), max(y1, y2)
    return [[xlo, ylo], [xhi, ylo], [xhi, yhi], [xlo, yhi]]


def _orient(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a: Sequence[float], b: Sequence[float], p: Sequence[float], tol: float) -> bool:
    if abs(_orient(a, b, p)) > tol * max(1.0, abs(b[0] - a[0]) + abs(b[1] - a[1])):
        return False
    return (
        min(a[0], b[0]) - tol <= p[0] <= max(a[0], b[0]) + tol
        and min(a[1], b[1]) - tol <= p[1] <= max(a[1], b[1]) + tol
    )


def segments_cross(
    a1: Sequence[float], a2: Sequence[float], b1: Sequence[float], b2: Sequence[float], tol: float
) -> bool:
    d1 = _orient(b1, b2, a1)
    d2 = _orient(b1, b2, a2)
    d3 = _orient(a1, a2, b1)
    d4 = _orient(a1, a2, b2)
    if ((d1 > tol) != (d2 > tol)) or (d1 < -tol) != (d2 < -tol):
        if abs(d1) > tol and abs(d2) > tol and abs(d3) > tol and abs(d4) > tol:
            return True
    for point, seg_a, seg_b in (
        (a1, b1, b2),
        (a2, b1, b2),
        (b1, a1, a2),
        (b2, a1, a2),
    ):
        if _on_segment(seg_a, seg_b, point, tol):
            return True
    return False


def self_intersects(ring: Sequence[Sequence[float]], tol: float) -> Optional[int]:
    count = len(ring)
    for i in range(count):
        a1, a2 = ring[i], ring[(i + 1) % count]
        for j in range(i + 1, count):
            if j == i or (i == 0 and j == count - 1) or j == i + 1:
                continue
            b1, b2 = ring[j], ring[(j + 1) % count]
            if segments_cross(a1, a2, b1, b2, tol):
                return i, j  # type: ignore[return-value]
    return None


def point_in_ring(
    point: Sequence[float], ring: Sequence[Sequence[float]], tol: float, strict: bool
) -> bool:
    """Ray casting with an explicit boundary test (boundary == inside unless strict)."""
    x, y = point[0], point[1]
    count = len(ring)
    for index in range(count):
        a = ring[index]
        b = ring[(index + 1) % count]
        if _on_segment(a, b, (x, y), tol):
            return not strict
    inside = False
    for index in range(count):
        x1, y1 = ring[index]
        x2, y2 = ring[(index + 1) % count]
        if (y1 > y) != (y2 > y):
            t = (y - y1) / (y2 - y1) if (y2 - y1) != 0 else 0.0
            if x < x1 + t * (x2 - x1):
                inside = not inside
    return inside


def cumulative(bays: Sequence[Any]) -> list[float]:
    total = 0.0
    lines = [0.0]
    for bay in bays:
        width = as_number(bay)
        if width is None:
            continue
        total += width
        lines.append(total)
    return lines


def interior_lines(bays: Sequence[Any]) -> list[float]:
    lines = cumulative(bays)
    return lines[1:-1] if len(lines) > 2 else []


def distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.hypot((as_number(a[0]) or 0.0) - (as_number(b[0]) or 0.0),
                      (as_number(a[1]) or 0.0) - (as_number(b[1]) or 0.0))


# --------------------------------------------------------------------------- #
# Loaded document
# --------------------------------------------------------------------------- #


@dataclass
class LoadedFile:
    path: Path
    label: str
    spec: Optional[SpecDef] = None
    raw: bytes = b""
    text: str = ""
    doc: Any = None
    hygiene: list[tuple[str, str]] = field(default_factory=list)  # (severity, detail)
    fatal: Optional[str] = None
    recipe: bool = False

    @property
    def name(self) -> str:
        return self.spec.name if self.spec else self.path.stem

    @property
    def ok(self) -> bool:
        return self.fatal is None


def strict_json_loads(text: str) -> Any:
    """Strict reader: rejects NaN / Infinity / -Infinity (07 G-7)."""

    def _reject(name: str) -> Any:
        raise ValueError(f"JSON constant {name} is not allowed (07 G-7)")

    return json.loads(text, parse_constant=_reject)


def load_spec_file(path: Path, label: str) -> LoadedFile:
    record = LoadedFile(path=path, label=label)
    try:
        record.raw = path.read_bytes()
    except OSError as exc:
        record.fatal = f"cannot read file: {exc.strerror or exc}"
        return record

    if record.raw.startswith(b"\xef\xbb\xbf"):
        record.hygiene.append((STATUS_FAIL, "file starts with a UTF-8 BOM (07 G-7)"))
        record.raw = record.raw[3:]
    if b"\r" in record.raw:
        record.hygiene.append((STATUS_FAIL, "file contains CR; line endings must be LF (07 G-7)"))
    if not record.raw.endswith(b"\n"):
        record.hygiene.append((STATUS_FAIL, "file does not end with a newline (07 G-7)"))
    elif record.raw.endswith(b"\n\n"):
        record.hygiene.append((STATUS_FAIL, "file ends with more than one newline (07 G-7)"))

    try:
        record.text = record.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        record.fatal = f"file is not valid UTF-8: {exc}"
        return record

    try:
        record.doc = strict_json_loads(record.text)
    except json.JSONDecodeError as exc:
        record.fatal = f"strict JSON parse failed at line {exc.lineno} col {exc.colno}: {exc.msg}"
        return record
    except ValueError as exc:
        record.fatal = str(exc)
        return record

    record.spec = SPEC_BY_NAME.get(path.stem)
    return record


# --------------------------------------------------------------------------- #
# Session
# --------------------------------------------------------------------------- #


@dataclass
class Session:
    files: list[LoadedFile]
    build_gate: bool = False
    allow_draft: bool = False

    def by_name(self, name: str) -> Optional[LoadedFile]:
        for record in self.files:
            if record.ok and not record.recipe and record.name == name:
                return record
        return None

    @property
    def dimensions(self) -> Optional[LoadedFile]:
        return self.by_name("dimensions")

    @property
    def recipes_only(self) -> bool:
        return bool(self.files) and all(record.recipe for record in self.files)

    @property
    def assumptions(self) -> Optional[LoadedFile]:
        return self.by_name("assumptions")

    @property
    def conflicts(self) -> Optional[LoadedFile]:
        return self.by_name("conflicts_resolved")

    @property
    def massing(self) -> Optional[LoadedFile]:
        return self.by_name("massing")

    @property
    def nurbs(self) -> Optional[LoadedFile]:
        return self.by_name("nurbs")

    @property
    def facade_grids(self) -> Optional[LoadedFile]:
        return self.by_name("facade_grids")

    @property
    def components_registry(self) -> Optional[LoadedFile]:
        return self.by_name("components_registry")

    @property
    def assembly(self) -> Optional[LoadedFile]:
        return self.by_name("assembly")

    def csv_by_name(self, name: str) -> Optional[Path]:
        """The first sibling ``name`` next to any loaded spec file, or None.

        ``world_table.csv`` is not a spec file, so it never enters ``self.files``; G-72 and
        G-73 read it through this. The search is deliberately narrow -- the directory
        holding a loaded spec, then its ``pipeline/`` child -- because a rule that picked up
        an arbitrary CSV from anywhere on the tree would be a rule whose verdict depended on
        the working directory.
        """
        for record in self.files:
            if not record.ok:
                continue
            for candidate in (record.path.parent / name, record.path.parent / "pipeline" / name):
                if candidate.is_file():
                    return candidate
        return None

    def tolerances(self) -> tuple[float, float, float, str]:
        """Return ``(linear_cm, area_m2, angle_deg, source_label)``."""
        dim = self.dimensions
        if dim is not None and dim.ok and isinstance(dim.doc, dict):
            block = dim.doc.get("tolerances")
            if isinstance(block, dict):
                linear = as_number(block.get("linear_cm"))
                area = as_number(block.get("area_m2"))
                angle = as_number(block.get("angle_deg"))
                if linear is not None and area is not None and angle is not None:
                    return linear, area, angle, f"{dim.label} tolerances"
        return (
            FALLBACK_LINEAR_CM,
            FALLBACK_AREA_M2,
            FALLBACK_ANGLE_DEG,
            "07 section 9.5 fallback (dimensions.json absent)",
        )


# --------------------------------------------------------------------------- #
# Envelope and hygiene: G-1..G-8
# --------------------------------------------------------------------------- #


def check_file_hygiene(record: LoadedFile, report: Report) -> None:
    location = record.label
    if record.fatal is not None:
        report.fail("G-7", location, record.fatal)
        return
    if not record.hygiene:
        report.ok(
            "G-7",
            location,
            "UTF-8 no BOM, LF endings, one trailing newline, strict JSON",
        )
        return
    for severity, detail in record.hygiene:
        report.add("G-7", severity, location, detail)


def check_envelope(record: LoadedFile, session: Session, report: Report) -> bool:
    """G-1..G-6 and the 07 section 4 key inventory. Returns True when usable."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        report.fail("G-1", location, f"top level is {type(doc).__name__}, not an object")
        return False

    keys = list(doc.keys())
    head = keys[: len(ENVELOPE_ORDER)]
    if head != list(ENVELOPE_ORDER):
        missing = [k for k in ENVELOPE_ORDER if k not in head]
        report.fail(
            "G-1",
            location,
            "first six keys must be "
            + ", ".join(ENVELOPE_ORDER)
            + f"; found {head}"
            + (f"; missing {missing}" if missing else ""),
        )
    else:
        report.ok("G-1", location, "envelope keys first, in order")

    spec_def = record.spec
    if spec_def is not None:
        expected = list(ENVELOPE_ORDER) + list(spec_def.body_keys)
        absent = [k for k in expected if k not in doc]
        if absent:
            report.fail(
                "G-1",
                location,
                f"{spec_def.name} is missing declared top-level keys: {', '.join(absent)}",
            )
        extra = [k for k in keys if k not in expected]
        if extra:
            report.warn(
                "G-1",
                location,
                f"undeclared top-level keys not in 07 section 4: {', '.join(extra)}",
            )
        if record.path.stem == "dimensions":
            ordered = keys[:7]
            if len(ordered) >= 7 and ordered[6] != "tolerances":
                report.fail("G-1", location, "tolerances must be the seventh key in dimensions.json")
            if "origins" in keys:
                value_index = next(
                    (i for i, k in enumerate(keys) if k not in ENVELOPE_ORDER
                     and k not in ("tolerances", "origins")),
                    len(keys),
                )
                if keys.index("origins") > value_index:
                    report.fail(
                        "G-1",
                        location,
                        "origins must precede the value tree it annotates (07 G-1)",
                    )

    # G-1 / 07 section 3.1: the project id is also the output name, so its shape is
    # part of the envelope contract.
    project = doc.get("project")
    if not isinstance(project, str) or not PROJECT_ID_RE.match(project):
        report.fail(
            "G-1",
            location,
            f"project {project!r} must match 07 section 3.1 ^[a-z0-9][a-z0-9._-]*$",
        )

    # G-2
    declared = doc.get("spec")
    if declared != record.path.stem:
        report.fail(
            "G-2",
            location,
            f'spec is {declared!r}; file base name is {record.path.stem!r}',
        )
    else:
        report.ok("G-2", location, f'spec == "{record.path.stem}"')

    # G-3
    version = doc.get("schema_version")
    if not isinstance(version, str):
        report.fail("G-3", location, f"schema_version is {version!r}, expected a semver string")
    else:
        match = SEMVER_RE.match(version)
        if match is None:
            report.fail("G-3", location, f"schema_version {version!r} is not MAJOR.MINOR[.PATCH]")
        elif int(match.group(1)) != SUPPORTED_SCHEMA_MAJOR:
            report.fail(
                "G-3",
                location,
                f"schema major {match.group(1)}; validator implements major "
                f"{SUPPORTED_SCHEMA_MAJOR}; a builder must stop rather than guess",
            )
        elif int(match.group(2)) != 0 or (match.group(3) not in (None, "0")):
            report.warn(
                "G-3",
                location,
                f"schema_version {version}: minor/patch drift accepted, tolerated by 07 G-3",
            )
        else:
            report.ok("G-3", location, f"schema_version {version} supported")

    # G-4
    status = doc.get("status")
    if status not in STATUSES:
        report.fail(
            "G-4",
            location,
            f"status {status!r} is not one of {', '.join(STATUSES)}",
        )
    elif status == "locked":
        report.ok("G-4", location, "status=locked; downstream stages may consume it")
    elif session_allow_draft:
        report.skip("G-4", location, f"status={status}; allowed by --allow-draft")
    elif session_build_gate:
        report.fail(
            "G-4",
            location,
            f"status={status}; a builder must refuse to consume this file",
        )
    else:
        report.warn(
            "G-4",
            location,
            f"status={status}; lint mode tolerates it, build mode (--build) would fail",
        )

    # G-5
    units = doc.get("units")
    if not isinstance(units, dict):
        report.fail("G-5", location, f"units is {units!r}, expected an object")
    elif units.get("length") != "cm" or units.get("angle") != "deg":
        report.fail(
            "G-5",
            location,
            f"units.length={units.get('length')!r} units.angle={units.get('angle')!r};"
            ' expected "cm" and "deg"',
        )
    else:
        report.ok("G-5", location, "units are cm and deg")

    # G-6
    source = doc.get("source")
    if not isinstance(source, dict):
        report.fail("G-6", location, f"source is {source!r}, expected an object")
    else:
        problems: list[str] = []
        kind = source.get("kind")
        if kind not in SOURCE_KINDS:
            problems.append(f"kind {kind!r} not in {', '.join(SOURCE_KINDS)}")
        reference = source.get("reference")
        if not isinstance(reference, str) or not reference.strip():
            problems.append(f"reference {reference!r} is empty")
        recorded = source.get("recorded_at")
        if not isinstance(recorded, str) or not parse_iso8601(recorded):
            problems.append(f"recorded_at {recorded!r} is not an ISO-8601 date-time")
        # 07 section 3.1: kind == "derived" means the file was computed from
        # another spec in the same project, so the reference must name that file.
        derived_from = _derived_source_file(reference, session)
        if kind == "derived" and derived_from is None:
            problems.append(
                f"kind 'derived' requires reference {reference!r} to name a spec file "
                "that exists in the project"
            )
        if problems:
            report.fail("G-6", location, "; ".join(problems))
        elif derived_from is not None:
            report.ok(
                "G-6",
                location,
                f"source kind=derived, reference names {derived_from}, recorded_at parses",
            )
        else:
            report.ok("G-6", location, f"source kind={source['kind']}, recorded_at parses")

    return True


def _derived_source_file(reference: Any, session: Optional[Session]) -> Optional[str]:
    """Return the spec label ``reference`` names, when it names one in the project.

    ``source.reference`` is free text that cites the file it read, so the check
    is a filename scan rather than an equality test: the first ``*.json`` token
    in the text whose base name is a 07 section 4 inventory entry that the
    session actually loaded wins.
    """
    if not isinstance(reference, str) or session is None:
        return None
    for candidate in re.findall(r"[A-Za-z0-9_.-]+\.json", reference):
        stem = candidate[: -len(".json")]
        if stem not in SPEC_BY_NAME:
            continue
        loaded = session.by_name(stem)
        if loaded is not None:
            return loaded.label
    return None


# ``G-4`` needs the CLI flags. Module-level sentinels keep the check function
# signature pure while still honouring --build and --allow-draft; main() sets
# them before any check runs.
session_build_gate = False
session_allow_draft = False


# --------------------------------------------------------------------------- #
# G-8 unit suffix lint
# --------------------------------------------------------------------------- #


def check_unit_lint(record: LoadedFile, report: Report) -> None:
    location = record.label
    doc = record.doc
    hits: list[tuple[str, str]] = []

    def walk(node: Any, prefix: str, exempt_root: bool) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                child_path = f"{prefix}.{key}" if prefix else key
                if prefix == "" and key in ("units", "source"):
                    walk(child, child_path, True)
                    continue
                if exempt_root:
                    walk(child, child_path, True)
                    continue
                verdict = _lint_key(key)
                if verdict:
                    hits.append((child_path, verdict))
                walk(child, child_path, False)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{prefix}[{index}]", exempt_root)

    if isinstance(doc, dict):
        walk(
            {k: v for k, v in doc.items() if k not in ("units", "source", "tolerances")},
            "",
            False,
        )
        walk(doc.get("units", {}), "units", True)
        walk(doc.get("source", {}), "source", True)

    if not hits:
        report.ok(
            "G-8",
            location,
            f"every length-looking key carries a unit suffix "
            f"(hard tokens {len(UNIT_LINT_HARD_TOKENS)}, "
            f"heuristic {len(UNIT_LINT_HEURISTIC_TOKENS)}, "
            f"{len(UNIT_LINT_EXEMPT_KEYS)} exempt names)",
        )
        return
    for path, verdict in hits:
        report.warn("G-8", f"{location}::{path}", verdict)


def _lint_key(key: str) -> str:
    """Return a message when ``key`` looks like a dimension with no unit suffix.

    An ``origins`` entry is a dotted *path* into the document rather than a key name, and
    G-9 requires the entry to name a path that resolves -- so the file's spelling is not
    the builder's to choose. The lint is therefore about the leaf such a path names:
    ``facades[0].bay_width_cm`` is judged as ``bay_width_cm`` and
    ``panels[0].full_height`` as ``full_height``. A genuinely unit-less leaf is still
    caught; only the path prefix is discarded.
    """
    if "." in key:
        key = key.rsplit(".", 1)[-1]
    lowered = key.lower()
    if lowered in UNIT_LINT_EXEMPT_KEYS:
        return ""
    for suffix in UNIT_LINT_UNIT_SUFFIXES + UNIT_LINT_NON_UNIT_SUFFIXES:
        if lowered.endswith(suffix):
            return ""
    final = lowered.rsplit("_", 1)[-1]
    if final in UNIT_LINT_HARD_TOKENS:
        return (
            f"key {key!r} carries a length with no unit suffix; 07 G-8 names "
            f"{final!r} explicitly and calls it an error. Rename to {key}_{'{cm|m2}'}"
        )
    if final in UNIT_LINT_HEURISTIC_TOKENS:
        return (
            f"key {key!r} looks like a dimension (heuristic token {final!r}) but "
            "carries no unit suffix; add _cm, _m2 or _deg, or add it to the "
            "documented exempt list"
        )
    return ""


# --------------------------------------------------------------------------- #
# Leaf enumeration for G-9
# --------------------------------------------------------------------------- #


#: 07 G-9 excludes these key names from the required origin coverage.
ORIGIN_EXEMPT_KEYS = frozenset({"id", "name", "index"})
ORIGIN_EXEMPT_SUFFIXES = ("_index", "_indices")


def is_origin_exempt_key(key: str) -> bool:
    return key in ORIGIN_EXEMPT_KEYS or key.endswith(ORIGIN_EXEMPT_SUFFIXES)


#: Top-level keys whose whole subtree is outside the origins coverage rule.
COVERAGE_EXEMPT_TOP = frozenset(set(ENVELOPE_ORDER) | {"tolerances", "origins", "origin_inputs"})


def collect_leaves(document: Any, spec_def: SpecDef) -> list[str]:
    """Every leaf path required to carry an ``origins`` entry, in file order.

    07 G-9 granularity: an array of scalars -- including a polygon ring -- is one
    leaf and takes one entry. An array of objects is not a leaf: each element is
    descended into, and the element may be collapsed into a single entry (e.g.
    ``facades[0]``) only when one entry is written for it.
    """
    leaves: list[str] = []
    skip_top = COVERAGE_EXEMPT_TOP | set(spec_def.leaf_skip_top)

    def walk(node: Any, prefix: str) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                if prefix == "" and key in skip_top:
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
    """An entry covers a leaf when it names it or names its element."""
    if entry == leaf:
        return True
    if leaf.startswith(entry + "."):
        return True
    return False


# --------------------------------------------------------------------------- #
# Traceability: G-9..G-15, G-31, G-32
# --------------------------------------------------------------------------- #


def check_origins_coverage(record: LoadedFile, report: Report) -> None:
    """G-9. Every leaf covered exactly once; every entry resolves."""
    if not isinstance(record.doc, dict):
        return
    problems, leaves, entries = _check_origins_coverage(
        record.doc, record.spec, record.label, report, "G-9"
    )
    if problems == 0:
        report.ok(
            "G-9",
            record.label,
            f"{leaves} leaves, {entries} entries, exactly-one coverage",
        )


def _check_origins_coverage(
    doc: Any,
    spec_def: Optional[SpecDef],
    location: str,
    report: Report,
    rule: str,
) -> tuple[int, int, int]:
    """The 07 section 5.2 coverage rule itself, shared by G-9 and G-36.

    Returns ``(problems, leaf_count, entry_count)``. ``rule`` only names which
    invariant the rows belong to; the conditions are the ones 07 section 5.2
    states, so ``massing.json`` gets the same coverage ``dimensions.json`` gets.
    """
    origins = doc.get("origins")
    if not isinstance(origins, dict):
        report.fail(rule, location, "origins is missing or not an object")
        return 1, 0, 0

    problems = 0

    # entries may not sit inside the envelope or tolerances
    for entry in origins:
        head = entry.split(".")[0].split("[")[0]
        if head in ENVELOPE_ORDER:
            report.fail(
                rule,
                f"{location}::{entry}",
                f"an origins entry may not live inside the envelope (07 {rule})",
            )
            problems += 1
        elif head == "tolerances":
            report.fail(
                rule,
                f"{location}::{entry}",
                f"an origins entry may not live inside tolerances (07 {rule})",
            )
            problems += 1

    # every entry must resolve
    resolvable: list[str] = []
    for entry in sorted(origins):
        found, _ = resolve(doc, entry)
        if not found:
            report.fail(
                rule,
                f"{location}::{entry}",
                "origins key does not resolve to an existing path",
            )
            problems += 1
        else:
            resolvable.append(entry)

    leaves = collect_leaves(doc, spec_def) if spec_def else []
    leaf_set = set(leaves)

    coverage: dict[str, list[str]] = {}
    for entry in resolvable:
        covered = sorted(leaf for leaf in leaf_set if covers(entry, leaf))
        coverage[entry] = covered

    for leaf, entries in ((leaf, [e for e, cov in coverage.items() if leaf in cov]) for leaf in leaves):
        if not entries:
            report.fail(
                rule,
                f"{location}::{leaf}",
                "leaf has no origins entry; every leaf except the envelope, "
                "tolerances and id/name/index keys must be covered",
            )
            problems += 1
        elif len(entries) > 1:
            report.fail(
                rule,
                f"{location}::{leaf}",
                f"leaf is covered by {len(entries)} entries: {', '.join(entries)};"
                f" 07 {rule} forbids more than one",
            )
            problems += 1

    return problems, len(leaves), len(resolvable)


def check_origin_pairing(record: LoadedFile, session: Session, report: Report) -> None:
    """G-10. ``origin`` / ``origin_ref`` / ``derives_from`` pairing."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict) or not isinstance(doc.get("origins"), dict):
        return
    origins = doc["origins"]
    a_ids = _ledger_ids(session.assumptions, "assumptions", "A")
    c_ids = _ledger_ids(session.conflicts, "conflicts", "C")
    problems = 0
    derived_entries: list[tuple[str, dict]] = []

    for entry in sorted(origins):
        record_obj = origins[entry]
        if not isinstance(record_obj, dict):
            report.fail(
                "G-10",
                f"{location}::{entry}",
                f"origins entry is {type(record_obj).__name__}, expected an object",
            )
            problems += 1
            continue
        origin = record_obj.get("origin")
        origin_ref = record_obj.get("origin_ref")
        derives_from = record_obj.get("derives_from")
        found, _ = resolve(doc, entry)
        if not found:
            continue  # already reported by G-9

        if origin not in ORIGIN_VALUES:
            report.fail(
                "G-10",
                f"{location}::{entry}",
                f"origin {origin!r} is not one of {', '.join(ORIGIN_VALUES)}",
            )
            problems += 1
            continue

        if origin in ("assumed", "conflict"):
            if not isinstance(origin_ref, str):
                report.fail(
                    "G-10",
                    f"{location}::{entry}",
                    f"origin={origin} requires origin_ref; found {origin_ref!r}",
                )
                problems += 1
                continue
            if not LEDGER_ID_RE.match(origin_ref):
                report.fail(
                    "G-10",
                    f"{location}::{entry}",
                    f"origin_ref {origin_ref!r} does not match ^[AC]-\\d{{3}}$",
                )
                problems += 1
                continue
            if origin == "assumed" and origin_ref not in a_ids:
                report.fail(
                    "G-10",
                    f"{location}::{entry}",
                    f"origin_ref {origin_ref} does not resolve in assumptions.json",
                )
                problems += 1
            if origin == "conflict" and origin_ref not in c_ids:
                report.fail(
                    "G-10",
                    f"{location}::{entry}",
                    f"origin_ref {origin_ref} does not resolve in conflicts_resolved.json",
                )
                problems += 1
        elif origin_ref is not None:
            report.fail(
                "G-10",
                f"{location}::{entry}",
                f"origin={origin} forbids origin_ref; found {origin_ref!r}",
            )
            problems += 1

        if origin == "derived":
            derived_entries.append((entry, record_obj))
            if not isinstance(derives_from, list) or not derives_from:
                report.fail(
                    "G-10",
                    f"{location}::{entry}",
                    "origin=derived requires a non-empty derives_from",
                )
                problems += 1
            else:
                for source in derives_from:
                    ok, _ = resolve(doc, str(source))
                    if not ok:
                        report.fail(
                            "G-10",
                            f"{location}::{entry}",
                            f"derives_from path {source!r} does not resolve",
                        )
                        problems += 1
        elif derives_from is not None:
            report.fail(
                "G-10",
                f"{location}::{entry}",
                f"origin={origin} must not carry derives_from",
            )
            problems += 1

        conflict_ref = record_obj.get("conflict_ref")
        if conflict_ref is not None:
            if not isinstance(conflict_ref, str) or conflict_ref not in c_ids:
                report.fail(
                    "G-10",
                    f"{location}::{entry}",
                    f"conflict_ref {conflict_ref!r} does not resolve in "
                    "conflicts_resolved.json",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-10",
            location,
            f"{len(origins)} entries: origin/origin_ref pairing valid, "
            f"{len(derived_entries)} derived with resolving derives_from",
        )

    check_derived_recompute(record, session, derived_entries, report)


def _ledger_ids(record: Optional[LoadedFile], key: str, prefix: str) -> set[str]:
    if record is None or not record.ok or not isinstance(record.doc, dict):
        return set()
    entries = record.doc.get(key)
    if not isinstance(entries, list):
        return set()
    ids: set[str] = set()
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            ids.add(entry["id"])
    return {i for i in ids if i.startswith(prefix + "-")}


def check_derived_recompute(
    record: LoadedFile,
    session: Session,
    derived_entries: Sequence[tuple[str, dict]],
    report: Report,
) -> None:
    """G-32. Recompute every derived value from its documented formula."""
    location = record.label
    doc = record.doc
    linear, area, angle, _ = session.tolerances()
    problems = 0
    checked = 0

    for entry, record_obj in derived_entries:
        is_element = entry.endswith("]") and "." not in entry.split("[")[-1]
        if is_element:
            sub_ok = 0
            sub_skip: list[str] = []
            for formula in DERIVED_FORMULAS:
                head = formula.pattern.split("[", 1)[0]
                if not entry.startswith(head):
                    continue
                # facades[] .bay_count becomes facades[0].bay_count
                concrete = head + entry[len(head) :] + formula.pattern[len(head) :]
                expected = formula.fn(doc, entry, linear, area, angle)
                ok, actual = resolve(doc, concrete)
                if expected is None or not ok:
                    sub_skip.append(concrete)
                    continue
                sub_ok += 1
                tol, tol_number = formula.tolerance(linear, area, angle)
                if not _formula_equal(actual, expected, tol_number):
                    report.fail(
                        "G-32",
                        f"{location}::{concrete}",
                        f"{formula.label}: spec holds {_short(actual)} but recomputes "
                        f"{_short(expected)} (derived via element entry {entry})",
                        tol,
                    )
                    problems += 1
            checked += sub_ok
            if not sub_ok:
                # No documented formula matched this collapsed entry, so nothing was
                # recomputed for it. ``note`` stays unbound in that case and must not
                # be referenced -- this line is what keeps G-10 from raising
                # UnboundLocalError on a file that declares such an entry.
                continue
            note = f"{sub_ok} documented member(s) recomputed"
            if sub_skip:
                note += f"; {len(sub_skip)} collapsed member(s) have no formula: " + ", ".join(
                    sub_skip
                )
            if problems == 0:
                report.ok("G-32", f"{location}::{entry}", note)
            continue

        expected_values: list[tuple[str, Any, str, Optional[float]]] = []
        for formula in DERIVED_FORMULAS:
            if not path_matches(formula.pattern, entry):
                continue
            value = formula.fn(doc, entry, linear, area, angle)
            if value is not None:
                label, tol_number = formula.tolerance(linear, area, angle)
                expected_values.append((formula.label, value, label, tol_number))
        ok, actual = resolve(doc, entry)
        if not expected_values:
            report.skip(
                "G-32",
                f"{location}::{entry}",
                "no documented formula for this derived path in 07 sections 5-5.11; "
                "G-32 cannot recompute it and will not pretend to",
            )
            continue
        if not ok:
            continue
        checked += len(expected_values)
        for label, expected, tol, tol_number in expected_values:
            if not _formula_equal(actual, expected, tol_number):
                report.fail(
                    "G-32",
                    f"{location}::{entry}",
                    f"{label}: spec holds {_short(actual)} but recomputes {_short(expected)}",
                    tol,
                )
                problems += 1

    if checked and problems == 0:
        report.ok("G-32", location, f"{checked} derived values recomputed from their formulas")


def _short(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, default=str)
    return text if len(text) <= 90 else text[:87] + "..."


def _formula_equal(actual: Any, expected: Any, tol: Optional[float]) -> bool:
    """Compare a spec value against a recomputed one. ``tol`` None means exact."""
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if tol is None:
            return float(actual) == float(expected)
        return close(float(actual), float(expected), tol)
    return deep_equal(actual, expected)


# --------------------------------------------------------------------------- #
# G-32 formula registry
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class DerivedFormula:
    pattern: str
    label: str
    fn: Callable[[Any, str, float, float, float], Any]
    #: returns ``(label, numeric_tolerance)``; numeric None means exact comparison
    tolerance: Callable[[float, float, float], tuple[str, Optional[float]]]


def _tol_linear(linear: float, area: float, angle: float) -> tuple[str, Optional[float]]:
    return f"{linear} cm (tolerances.linear_cm)", linear


def _tol_area(linear: float, area: float, angle: float) -> tuple[str, Optional[float]]:
    return f"{area} m2 (tolerances.area_m2)", area


def _tol_exact(linear: float, area: float, angle: float) -> tuple[str, Optional[float]]:
    return "exact (07 section 9.5: a tolerance is never applied to a count)", None


def _numbers(values: Any) -> Optional[list[float]]:
    if not isinstance(values, list):
        return None
    out: list[float] = []
    for item in values:
        number = as_number(item)
        if number is None:
            return None
        out.append(number)
    return out


def _f_total_height(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    levels = doc.get("levels") if isinstance(doc, dict) else None
    if not isinstance(levels, list) or not levels:
        return None
    top = levels[-1]
    if not isinstance(top, dict):
        return None
    base = as_number(top.get("elevation_cm"))
    height = as_number(top.get("height_cm"))
    if base is None or height is None:
        return None
    return base + height


def _f_overall_height(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    building = doc.get("building") or {}
    roof = doc.get("roof") or {}
    total = as_number(building.get("total_height_cm"))
    parapet = as_number(roof.get("parapet_height_cm"))
    if total is None or parapet is None:
        return None
    return total + parapet


def _f_gross_area(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    plates = doc.get("floor_plates")
    if not isinstance(plates, list) or not plates:
        return None
    total = 0.0
    for plate in plates:
        value = as_number(plate.get("gross_area_m2")) if isinstance(plate, dict) else None
        if value is None:
            return None
        total += value
    return total


def _f_net_area(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    building = doc.get("building") or {}
    core = doc.get("core") or {}
    gross = as_number(building.get("gross_floor_area_m2"))
    core_area = as_number(core.get("footprint_area_m2"))
    spans = core.get("spans_level_indices")
    if gross is None or core_area is None or not isinstance(spans, list):
        return None
    return gross - core_area * len(spans)


def _f_footprint_area(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    site = doc.get("site") or {}
    kind = site.get("footprint_kind")
    ring = expand_footprint_ring(site.get("footprint_cm"), kind if isinstance(kind, str) else "")
    if not ring or len(ring) < 3:
        return None
    return polygon_area_m2(ring)


def _f_footprint_width(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    site = doc.get("site") or {}
    kind = site.get("footprint_kind")
    ring = expand_footprint_ring(site.get("footprint_cm"), kind if isinstance(kind, str) else "")
    if not ring:
        return None
    return max(p[0] for p in ring) - min(p[0] for p in ring)


def _f_footprint_depth(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    site = doc.get("site") or {}
    kind = site.get("footprint_kind")
    ring = expand_footprint_ring(site.get("footprint_cm"), kind if isinstance(kind, str) else "")
    if not ring:
        return None
    return max(p[1] for p in ring) - min(p[1] for p in ring)


def _f_column_x(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    structure = doc.get("structure") or {}
    bays = _numbers(structure.get("x_bay_cm"))
    if bays is None:
        return None
    return interior_lines(bays)


def _f_column_y(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    structure = doc.get("structure") or {}
    bays = _numbers(structure.get("y_bay_cm"))
    if bays is None:
        return None
    return interior_lines(bays)


def _f_interior_column_count(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    structure = doc.get("structure") or {}
    xs = _numbers(structure.get("column_x_cm"))
    ys = _numbers(structure.get("column_y_cm"))
    if xs is None or ys is None:
        return None
    return len(xs) * len(ys)


def _f_level_elevation(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    tokens = split_path(path)
    if len(tokens) < 3 or not isinstance(tokens[1], int):
        return None
    index = tokens[1]
    levels = doc.get("levels")
    if not isinstance(levels, list) or index <= 0 or index >= len(levels):
        return None
    previous = levels[index - 1]
    base = as_number(previous.get("elevation_cm")) if isinstance(previous, dict) else None
    height = as_number(previous.get("height_cm")) if isinstance(previous, dict) else None
    if base is None or height is None:
        return None
    return base + height


def _f_core_area(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    core = doc.get("core") or {}
    kind = core.get("footprint_kind")
    ring = expand_footprint_ring(core.get("footprint_cm"), kind if isinstance(kind, str) else "")
    if not ring or len(ring) < 3:
        return None
    return polygon_area_m2(ring)


def _f_plate_gross(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    site = doc.get("site") or {}
    return as_number(site.get("footprint_area_m2"))


def _f_deck_level(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    building = doc.get("building") or {}
    return as_number(building.get("total_height_cm"))


def _grid_bays_for(doc: Any, facade: dict) -> Optional[list[float]]:
    """07 section 5.10: N/S facades take x_bay_cm, E/W take y_bay_cm."""
    structure = doc.get("structure") or {}
    name = facade.get("name")
    if name in ("north", "south"):
        return _numbers(structure.get("x_bay_cm"))
    if name in ("east", "west"):
        return _numbers(structure.get("y_bay_cm"))
    return None


def _f_facade_length(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    tokens = split_path(path)
    facades = doc.get("facades")
    if len(tokens) < 3 or not isinstance(tokens[1], int) or not isinstance(facades, list):
        return None
    facade = facades[tokens[1]] if 0 <= tokens[1] < len(facades) else None
    if not isinstance(facade, dict):
        return None
    start, end = facade.get("start_corner_cm"), facade.get("end_corner_cm")
    if not is_point(start) or not is_point(end):
        return None
    return distance(start, end)


def _f_facade_bay_count(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    tokens = split_path(path)
    facades = doc.get("facades")
    if len(tokens) < 3 or not isinstance(tokens[1], int) or not isinstance(facades, list):
        return None
    facade = facades[tokens[1]] if 0 <= tokens[1] < len(facades) else None
    if not isinstance(facade, dict):
        return None
    bays = facade.get("bay_width_cm")
    if not isinstance(bays, list):
        return None
    return len(bays)


def _f_facade_bay_width(doc: Any, path: str, linear: float, area: float, angle: float) -> Any:
    tokens = split_path(path)
    facades = doc.get("facades")
    if len(tokens) < 3 or not isinstance(tokens[1], int) or not isinstance(facades, list):
        return None
    facade = facades[tokens[1]] if 0 <= tokens[1] < len(facades) else None
    if not isinstance(facade, dict):
        return None
    return _grid_bays_for(doc, facade)


DERIVED_FORMULAS: tuple[DerivedFormula, ...] = (
    DerivedFormula(
        "building.total_height_cm",
        "07 section 5.3: levels[-1].elevation_cm + levels[-1].height_cm",
        _f_total_height,
        _tol_linear,
    ),
    DerivedFormula(
        "building.overall_height_cm",
        "07 section 5.3: total_height_cm + roof.parapet_height_cm",
        _f_overall_height,
        _tol_linear,
    ),
    DerivedFormula(
        "building.gross_floor_area_m2",
        "07 section 5.3: sum of floor_plates[].gross_area_m2",
        _f_gross_area,
        _tol_area,
    ),
    DerivedFormula(
        "building.net_floor_area_m2",
        "07 section 5.3: gross - core.footprint_area_m2 over core.spans_level_indices",
        _f_net_area,
        _tol_area,
    ),
    DerivedFormula(
        "site.footprint_area_m2",
        "07 section 5.4: shoelace area of site.footprint_cm",
        _f_footprint_area,
        _tol_area,
    ),
    DerivedFormula(
        "site.footprint_width_cm",
        "07 section 5.4: X extent of site.footprint_cm",
        _f_footprint_width,
        _tol_linear,
    ),
    DerivedFormula(
        "site.footprint_depth_cm",
        "07 section 5.4: Y extent of site.footprint_cm",
        _f_footprint_depth,
        _tol_linear,
    ),
    DerivedFormula(
        "structure.column_x_cm",
        "07 section 5.5: interior lines of cumulative x_bay_cm",
        _f_column_x,
        _tol_linear,
    ),
    DerivedFormula(
        "structure.column_y_cm",
        "07 section 5.5: interior lines of cumulative y_bay_cm",
        _f_column_y,
        _tol_linear,
    ),
    DerivedFormula(
        "structure.interior_column_count",
        "07 section 5.5: len(column_x_cm) * len(column_y_cm)",
        _f_interior_column_count,
        _tol_exact,
    ),
    DerivedFormula(
        "levels[].elevation_cm",
        "07 section 5.6: previous elevation_cm + previous height_cm",
        _f_level_elevation,
        _tol_linear,
    ),
    DerivedFormula(
        "core.footprint_area_m2",
        "07 section 5.7: shoelace area of core.footprint_cm",
        _f_core_area,
        _tol_area,
    ),
    DerivedFormula(
        "floor_plates[].gross_area_m2",
        "07 section 5.8: site.footprint_area_m2 (prismatic building)",
        _f_plate_gross,
        _tol_area,
    ),
    DerivedFormula(
        "roof.deck_level_cm",
        "07 section 5.9: building.total_height_cm",
        _f_deck_level,
        _tol_linear,
    ),
    DerivedFormula(
        "facades[].length_cm",
        "07 section 5.10: distance between start_corner_cm and end_corner_cm",
        _f_facade_length,
        _tol_linear,
    ),
    DerivedFormula(
        "facades[].bay_count",
        "07 section 5.10: len(bay_width_cm)",
        _f_facade_bay_count,
        _tol_exact,
    ),
    DerivedFormula(
        "facades[].bay_width_cm",
        "07 section 5.10: structure.x_bay_cm (N/S) or structure.y_bay_cm (E/W)",
        _f_facade_bay_width,
        _tol_linear,
    ),
)


# --------------------------------------------------------------------------- #
# Ledger checks: G-11..G-15, G-13
# --------------------------------------------------------------------------- #


def _scan_id_sequence(
    entries: Sequence[Any],
    key: str,
    location: str,
    report: Report,
    rule: str,
    id_re: Any,
    id_pattern: str,
    prefix: Optional[str] = None,
) -> int:
    """Unique, well formed, ascending ids. Returns the problem count.

    One sequence rule, two callers: G-11 over the A-/C- ledgers and G-34 over the
    EL-/GRP- identities in ``massing.json``. ``prefix`` is the ledger-only rule
    that a letter-prefixed id may appear in one ledger and not another; pass
    ``None`` for a vocabulary that carries no such restriction.
    """
    problems = 0
    seen: set[str] = set()
    previous = ""
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            report.fail(rule, f"{location}::{key}[{index}]", f"{key}[{index}] is not an object")
            problems += 1
            continue
        ident = entry.get("id")
        if not isinstance(ident, str) or not id_re.match(ident):
            report.fail(
                rule,
                f"{location}::{key}[{index}].id",
                f"id {ident!r} does not match {id_pattern}",
            )
            problems += 1
            continue
        if prefix is not None and not ident.startswith(prefix + "-"):
            report.fail(
                rule,
                f"{location}::{key}[{index}].id",
                f"{prefix}- ids may appear only in the matching ledger; found {ident}",
            )
            problems += 1
        if ident in seen:
            report.fail(rule, f"{location}::{key}", f"duplicate id {ident}")
            problems += 1
        seen.add(ident)
        if previous and ident <= previous:
            report.fail(
                rule,
                f"{location}::{key}[{index}].id",
                f"ids must ascend: {previous} is followed by {ident}",
            )
            problems += 1
        previous = ident
    return problems


def check_ledger_ids(record: LoadedFile, key: str, prefix: str, report: Report) -> None:
    """G-11. Ids unique, well formed, ascending, and in the right file."""
    location = record.label
    entries = record.doc.get(key) if isinstance(record.doc, dict) else None
    if not isinstance(entries, list):
        report.fail("G-11", location, f"{key} is {entries!r}, expected an array")
        return
    if prefix == "A" and not entries:
        report.fail("G-11", location, "assumptions must hold at least one entry (07 section 6)")
        return
    problems = _scan_id_sequence(
        entries, key, location, report, "G-11", LEDGER_ID_RE, r"^[AC]-\d{3}$", prefix
    )
    if problems == 0:
        report.ok(
            "G-11",
            location,
            f"{len(entries)} {prefix}- ids, unique, well formed, ascending",
        )


class LedgerPath(NamedTuple):
    """Where a ledger ``field_path`` resolved.

    ``owner`` is the spec file that answered, ``label`` its label as the report prints it,
    ``found`` whether the sub-path resolved inside it, ``value`` what it resolved to, and
    ``reason`` why not when ``found`` is false -- an actionable FAIL reason, never a SKIP.
    """

    owner: str
    label: str
    found: bool
    value: Any
    reason: str


def resolve_ledger_path(field_path: Any, session: Session) -> LedgerPath:
    """Resolve a ledger ``field_path``, which may be **bare** or **file-qualified**.

    Two accepted forms, everywhere a ledger path is read:

    * **bare** -- ``"facades[0].bay_width_cm"``. Resolves in ``dimensions.json``. This is
      **byte-for-byte the behaviour that existed before qualification**: same document, same
      resolver, same tolerance-free dotted-path semantics, so all 22 ``A-nnn`` and 5 ``C-nnn``
      entries of the worked example resolve exactly as they did and the counts do not move.
    * **qualified** -- ``"<spec-name>:<dotted path>"``, e.g.
      ``"components_registry.json:defaults.panel_thickness_cm"``. Resolves in the named spec
      file among this session's loaded files.

    P2 built the ledger when ``dimensions.json`` was the only file carrying
    ``origin: assumed``, so a bare path was the whole grammar. **P5 is the first stage to put an
    assumed value in a derived file** -- ``components_registry.json``'s two ``defaults`` -- so
    qualification is a producer-side fact the ledger side had no way to express. Making those
    values ``derived`` would be a lie and dropping the entries would leave two dangling
    ``origin_ref``s, which is why the grammar moves rather than the data.

    ``<spec-name>`` must be a spec name in ``SPEC_BY_NAME`` **and** loaded in this session.
    Anything else -- an unknown name, a file not loaded, a sub-path that does not exist there --
    is a FAIL naming the reason. A SKIP is reserved for "the whole comparison is impossible",
    never for "I could not find the file you named".
    """
    if not isinstance(field_path, str):
        return LedgerPath(
            "", "", False, None,
            f"field_path is {field_path!r}; expected a dotted path, or "
            "'<spec-name>:<dotted path>' to name the file it lives in",
        )
    if not field_path.strip():
        return LedgerPath("", "", False, None, "field_path is empty")
    if ":" in field_path:
        stem, _, sub_path = field_path.partition(":")
        stem = stem.strip()
        sub_path = sub_path.strip()
        # The qualifier is spoken the way the rest of this script names a spec file -- as a
        # filename. ``_derived_source_file`` strips the ``.json`` before consulting
        # ``SPEC_BY_NAME``, so ``components_registry.json`` and ``components_registry`` are one
        # name here too, and the worked ledger writes the former.
        spec_name = stem[: -len(".json")] if stem.endswith(".json") else stem
        if spec_name not in SPEC_BY_NAME:
            return LedgerPath(
                "", "", False, None,
                f"field_path qualifier {stem!r} is not a 07 section 4 spec file name; a qualified "
                f"field_path reads '<spec-name>:<dotted path>' and the spec names are "
                f"{', '.join(sorted(SPEC_BY_NAME))}",
            )
        record = session.by_name(spec_name)
        if record is None or not isinstance(record.doc, dict):
            return LedgerPath(
                "", "", False, None,
                f"field_path names {stem!r}, which is not loaded in this run; a qualified "
                "field_path must name a spec file this project actually carries, or the ledger "
                "claims a value nothing in scope can vouch for",
            )
        if not sub_path:
            return LedgerPath(
                spec_name, record.label, False, None,
                f"field_path {field_path!r} names {stem!r} but no path inside it",
            )
        found, value = resolve(record.doc, sub_path)
        if not found:
            return LedgerPath(
                spec_name, record.label, False, None,
                f"path {sub_path!r} does not exist in {record.label}",
            )
        return LedgerPath(spec_name, record.label, True, value, "")

    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        return LedgerPath(
            "", "", False, None,
            f"bare field_path {field_path!r} resolves in dimensions.json, which is not loaded in "
            "this run",
        )
    found, value = resolve(dimensions.doc, field_path)
    if not found:
        return LedgerPath(
            dimensions.spec.name if dimensions.spec else "dimensions",
            dimensions.label,
            False,
            None,
            f"path {field_path!r} does not exist in {dimensions.label}",
        )
    return LedgerPath(
        dimensions.spec.name if dimensions.spec else "dimensions",
        dimensions.label,
        True,
        value,
        "",
    )


def check_ledger_matches_spec(
    record: LoadedFile, key: str, session: Session, report: Report
) -> None:
    """G-12. Ledger ``value`` equals the spec value at ``field_path``."""
    location = record.label
    entries = record.doc.get(key) if isinstance(record.doc, dict) else None
    if not isinstance(entries, list):
        return

    problems = 0
    in_dimensions = 0
    in_other = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        if key == "conflicts":
            # A conflict entry has no field_path; 07 section 7.2 puts the winning
            # value in resolution.chosen_value and names its home in
            # resolution.resulting_value_of.
            resolution = entry.get("resolution")
            if not isinstance(resolution, dict):
                continue  # G-14 reports the missing resolution block
            field_path = resolution.get("resulting_value_of")
            where = f"{location}::{entry.get('id', index)}"
        else:
            field_path = entry.get("field_path")
            where = f"{location}::{key}[{index}]"
        if not isinstance(field_path, str):
            report.fail(
                "G-12",
                where,
                f"field_path is {field_path!r}, expected a dotted path, or "
                "'<spec-name>:<dotted path>' to name the file it lives in",
            )
            problems += 1
            continue
        resolved = resolve_ledger_path(field_path, session)
        if not resolved.found:
            report.fail(
                "G-12",
                f"{location}::{field_path}",
                f"{resolved.reason}; a ledger field_path is either a bare dotted path in "
                f"dimensions.json or '<spec-name>:<dotted path>' naming a loaded spec file",
            )
            problems += 1
            continue
        if resolved.label == (session.dimensions.label if session.dimensions else None):
            in_dimensions += 1
        else:
            in_other += 1
        ledger_value = (
            entry.get("value") if key != "conflicts" else resolution.get("chosen_value")
        )
        if not deep_equal(ledger_value, resolved.value):
            report.fail(
                "G-12",
                f"{location}::{field_path}",
                f"ledger value {_short(ledger_value)} != the {resolved.label} value "
                f"{_short(resolved.value)}",
            )
            problems += 1
    if problems == 0:
        note = f"{len(entries)} ledger values equal the spec value at their field_path"
        if in_other:
            note += (
                f"; {in_dimensions} resolve bare in dimensions.json and {in_other} name their "
                "own file with a '<spec-name>:<dotted path>' qualifier"
            )
        report.ok("G-12", location, note)


def check_ledger_bijection(
    record: LoadedFile, key: str, origin_value: str, session: Session, report: Report
) -> None:
    """G-13. Every assumed/conflict value is covered; every entry is consumed.

    Coverage is tested by prefix in both directions, never by exact string
    equality (07 G-13): a ledger entry may name a field inside an element whose
    origin is recorded at element level, and a conflict's ``resolved_paths`` may
    name a consequence that carries no marker of its own.

    **And never across files.** Prefix coverage is a statement about two paths
    *inside one document*; ``defaults.panel_thickness_cm`` in
    ``components_registry.json`` and a bare path in ``dimensions.json`` are unrelated, and
    treating them as one prefix family could mask a real gap in both. So ``_prefix_cover``
    takes an owner on each side and requires them to be equal, which is a no-op for bare paths
    (every one of them resolves in dimensions.json) and a real constraint the moment an entry is
    qualified.
    """
    location = record.label
    entries = record.doc.get(key) if isinstance(record.doc, dict) else None
    if not isinstance(entries, list):
        return

    #: ``(owner spec name, origin path) -> the origins entry``, over every loaded project spec
    #: that carries an origins map -- not dimensions alone, because P5 put the first assumed
    #: value in a derived file and an origins entry nobody covers is exactly what this rule
    #: exists to name.
    owned_maps: list[tuple[str, str, dict]] = []
    for other in session.files:
        if not other.ok or other.recipe or other.spec is None:
            continue
        origins = other.doc.get("origins") if isinstance(other.doc, dict) else None
        if isinstance(origins, dict) and origins:
            owned_maps.append((other.spec.name, other.label, origins))
    if not owned_maps:
        report.skip(
            "G-13",
            location,
            "no loaded spec file carries an origins map, so there is no origin for an entry to "
            "cover and none to be consumed by; coverage cannot be tested",
        )
        return

    # ---- 1. the paths this ledger claims, with the id that claims each ----
    claims: list[tuple[str, str, str, str]] = []  # (owner, sub-path, field_path as written, id)
    used_paths: dict[str, str] = {}
    problems = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        ident = entry.get("id") if isinstance(entry.get("id"), str) else f"#{index}"
        if key == "conflicts":
            resolution = entry.get("resolution")
            paths = resolution.get("resolved_paths") if isinstance(resolution, dict) else None
            paths = [paths] if isinstance(paths, str) else paths
            if not isinstance(paths, list) or not paths:
                report.fail(
                    "G-13",
                    f"{location}::{ident}",
                    "every entry must name at least one existing path "
                    "(resolution.resolved_paths for a conflict)",
                )
                problems += 1
                continue
        else:
            paths = [entry.get("field_path")]
        for path in paths if isinstance(paths, list) else []:
            if not isinstance(path, str):
                problems += 1
                continue
            resolved = resolve_ledger_path(path, session)
            if not resolved.found:
                report.fail(
                    "G-13",
                    f"{location}::{ident}",
                    f"entry must name exactly one existing field_path; {resolved.reason}",
                )
                problems += 1
                continue
            # Uniqueness is tested on the path **as written**, qualifier and all, so a bare
            # claim and a qualified claim are distinct claims. Canonicalising instead would
            # call ``X`` and ``dimensions.json:X`` the same claim while the ledger means them
            # as two spellings of two provenance decisions.
            if key != "conflicts" and path in used_paths:
                report.fail(
                    "G-13",
                    f"{location}::{path}",
                    f"field_path is not unique within this ledger; also claimed by "
                    f"{used_paths[path]}",
                )
                problems += 1
            else:
                used_paths.setdefault(path, ident)
            sub_path = path.partition(":")[2].strip() if ":" in path else path
            claims.append((resolved.owner, sub_path, path, ident))

    # ---- 2. every value of this provenance must be covered ----
    owned: list[tuple[str, str, str, Any]] = []
    for owner, label, origins in owned_maps:
        for path, obj in origins.items():
            if isinstance(obj, dict) and obj.get("origin") == origin_value:
                owned.append((owner, path, label, obj.get("origin_ref" if origin_value == "assumed" else "conflict_ref")))
    marker = "origin_ref" if origin_value == "assumed" else "conflict_ref"
    noun = key[:-1] if key.endswith("s") else key
    for owner, path, label, ref in owned:
        covered = any(
            _prefix_cover(path, sub_path, owner, claim_owner) or claim_id == ref
            for claim_owner, sub_path, _raw, claim_id in claims
        )
        if not covered:
            report.fail(
                "G-13",
                f"{label}::{path}",
                f"origin={origin_value} but no {noun} entry names this path, an ancestor of it "
                f"inside the same file, or carries {marker}={ref!r}",
            )
            problems += 1

    # ---- 3. every entry must be consumed at least once ----
    consumed_ids: set[str] = set()
    for owner, _label, origins in owned_maps:
        for path, obj in origins.items():
            if not isinstance(obj, dict):
                continue
            for claim_owner, sub_path, _raw, claim_id in claims:
                if obj.get("origin_ref") == claim_id or obj.get("conflict_ref") == claim_id:
                    if _prefix_cover(path, sub_path, owner, claim_owner):
                        consumed_ids.add(claim_id)
                        break
    for claim_owner, sub_path, _raw, claim_id in claims:
        if claim_id in consumed_ids:
            continue
        if any(
            _prefix_cover(owner_path, sub_path, owner, claim_owner)
            for owner, owner_path, _label, _ref in owned
        ):
            consumed_ids.add(claim_id)
    unconsumed = sorted({claim_id for _, _, _, claim_id in claims} - consumed_ids)
    for claim_id in unconsumed:
        report.fail(
            "G-13",
            f"{location}::{claim_id}",
            "ledger entry is never consumed: no origins entry in any loaded spec file "
            f"references it by {marker}, and no {origin_value} value inside the same file "
            "resolves to one of its paths",
        )
        problems += 1

    if problems == 0:
        note = (
            f"{len(claims)} claim(s) over {len(owned)} {origin_value} origins, "
            f"{len(consumed_ids)}/{len({i for _, _, _, i in claims})} entries consumed; "
            "bijection holds both ways"
        )
        owners = sorted({owner for owner, _, _, _ in claims})
        if len(owners) > 1:
            note += f"; claims resolve across {len(owners)} file(s): {', '.join(owners)}"
        report.ok("G-13", location, note)


def _prefix_cover(
    origin_path: str, ledger_path: str, origin_owner: str, ledger_owner: str
) -> bool:
    """Coverage is tested by prefix in both directions (07 G-13), **within one file**.

    Two paths in different documents are not a prefix family: ``building.total_height_cm`` in
    ``dimensions.json`` and ``facades[0].length_cm`` in ``facade_grids.json`` share no prefix
    relation, and pretending they did could cover a gap in both. Requiring equal owners is a
    no-op for bare paths -- every bare ledger path resolves in dimensions.json, and so does every
    origins entry the rule compared before -- and becomes a real constraint as soon as a claim is
    qualified.
    """
    if origin_owner != ledger_owner:
        return False
    if origin_path == ledger_path:
        return True
    return origin_path.startswith(ledger_path + ".") or ledger_path.startswith(origin_path + ".")



def check_conflicts_complete(record: LoadedFile, session: Session, report: Report) -> None:
    """G-14. Conflict entry completeness."""
    location = record.label
    doc = record.doc if isinstance(record.doc, dict) else None
    conflicts = doc.get("conflicts") if doc else None
    rules_block = doc.get("precedence_rules") if doc else None
    dimensions = session.dimensions

    if not isinstance(rules_block, dict):
        report.fail("G-14", location, "precedence_rules is missing; the log is not self-contained")
        return
    rule_ids = {
        rule.get("id")
        for rule in rules_block.get("rules", [])
        if isinstance(rule, dict) and isinstance(rule.get("id"), str)
    }
    fallback = rules_block.get("non_conflict_fallback")
    if isinstance(fallback, dict) and isinstance(fallback.get("id"), str):
        rule_ids.add(fallback["id"])
    rules_sorted = [
        rule.get("id")
        for rule in rules_block.get("rules", [])
        if isinstance(rule, dict)
    ]
    if rules_sorted != sorted(rules_sorted):
        report.fail("G-14", location, "precedence_rules.rules must be ascending by id")
    for key in ("note", "evaluation_order", "rules", "non_conflict_fallback"):
        if key not in rules_block:
            report.fail("G-14", location, f"precedence_rules is missing {key!r}")

    if not isinstance(conflicts, list):
        report.fail("G-14", location, "conflicts is missing or not an array")
        return

    problems = 0
    for index, entry in enumerate(conflicts):
        where = f"{location}::conflicts[{index}]"
        if not isinstance(entry, dict):
            report.fail("G-14", where, "entry is not an object")
            problems += 1
            continue
        ident = entry.get("id", "?")
        where = f"{location}::{ident}"

        sources = entry.get("sources")
        if not isinstance(sources, list) or len(sources) < 2:
            report.fail("G-14", where, "needs at least 2 sources")
            problems += 1
        rejected = entry.get("rejected")
        if not isinstance(rejected, list) or not rejected:
            report.fail("G-14", where, "needs at least 1 rejected entry; every loser is recorded")
            problems += 1

        invoked = entry.get("rules_invoked")
        if not isinstance(invoked, list) or not invoked:
            report.fail(
                "G-14",
                where,
                "rules_invoked must be non-empty (an empty array only documents an "
                "unresolved conflict)",
            )
            problems += 1
        else:
            unknown = [r for r in invoked if r not in rule_ids]
            if unknown:
                report.fail(
                    "G-14",
                    where,
                    f"rules_invoked names rules absent from precedence_rules: {unknown}",
                )
                problems += 1
            if NON_CONFLICT_FALLBACK_ID in invoked:
                report.fail(
                    "G-14",
                    where,
                    f"{NON_CONFLICT_FALLBACK_ID} DEFAULT-FILL is not a conflict rule; "
                    "a default in a conflicts entry is a bug (07 section 7.1)",
                )
                problems += 1
            ascending = [str(r) for r in invoked]
            if ascending != sorted(ascending, key=_rule_sort_key):
                report.warn(
                    "G-14",
                    where,
                    f"rules_invoked {ascending} is not in ascending id order. 07 section 7.2 "
                    "says 'ascending' without saying whether that means id order or ladder "
                    "priority; the worked example uses decisive-rule-first order. Reported as "
                    "a warning because G-14's mechanical list does not require ordering.",
                )

        invariant = entry.get("invariant_violated_if_unresolved")
        if not isinstance(invariant, str) or invariant not in RULE_TITLES:
            report.fail(
                "G-14",
                where,
                f"invariant_violated_if_unresolved {invariant!r} is not a real G- id",
            )
            problems += 1

        resolution = entry.get("resolution")
        if not isinstance(resolution, dict):
            report.fail("G-14", where, "resolution must be an object")
            problems += 1
            continue
        for key in (
            "chosen_sources",
            "chosen_value",
            "statement",
            "resolved_paths",
            "resulting_value_of",
            "downstream_effect",
        ):
            if key not in resolution:
                report.fail("G-14", where, f"resolution is missing {key!r}")
                problems += 1
        for key in ("chosen_sources", "resolved_paths"):
            value = resolution.get(key)
            if not isinstance(value, list) or not value:
                report.fail("G-14", where, f"resolution.{key} must be a non-empty array")
                problems += 1

        if isinstance(sources, list):
            source_refs = {
                s.get("ref") for s in sources if isinstance(s, dict)
            }
            for item in rejected if isinstance(rejected, list) else []:
                if isinstance(item, dict) and item.get("ref") not in source_refs:
                    report.fail(
                        "G-14",
                        where,
                        f"rejected ref {item.get('ref')!r} is not one of this entry's sources",
                    )
                    problems += 1

        primary = resolution.get("resulting_value_of")
        if isinstance(primary, str) and dimensions is not None and dimensions.ok:
            found, actual = resolve(dimensions.doc, primary)
            if not found:
                report.fail(
                    "G-14",
                    where,
                    f"resolution.resulting_value_of {primary!r} does not resolve in "
                    "dimensions.json",
                )
                problems += 1
            elif not deep_equal(resolution.get("chosen_value"), actual):
                report.fail(
                    "G-14",
                    where,
                    f"resolution.chosen_value {_short(resolution.get('chosen_value'))} != "
                    f"value at {primary} {_short(actual)}",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-14",
            location,
            f"{len(conflicts)} conflict entries complete"
            + (" (empty conflicts array is a valid result)" if not conflicts else ""),
        )


def _rule_sort_key(rule_id: str) -> tuple[int, str]:
    digits = "".join(ch for ch in str(rule_id) if ch.isdigit())
    return (int(digits) if digits else 0, str(rule_id))


def check_assumptions_complete(record: LoadedFile, session: Session, report: Report) -> None:
    """G-15. Assumption entry completeness."""
    location = record.label
    doc = record.doc if isinstance(record.doc, dict) else None
    entries = doc.get("assumptions") if doc else None
    if not isinstance(entries, list):
        report.fail("G-15", location, "assumptions is missing or not an array")
        return
    if not entries:
        report.fail("G-15", location, "07 section 6 requires at least one assumption")
        return

    problems = 0
    project_ids = {
        r.label for r in session.files if r.ok and isinstance(r.doc, dict)
    }
    dimensions = session.dimensions
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            report.fail("G-15", location, f"assumptions[{index}] is not an object")
            problems += 1
            continue
        ident = entry.get("id", "?")
        where = f"{location}::{ident}"
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            report.fail("G-15", where, "reason must be non-empty and name the silence")
            problems += 1
        elif reason.strip().startswith("The brief is silent on"):
            pass
        if entry.get("confidence") not in CONFIDENCES:
            report.fail(
                "G-15",
                where,
                f"confidence {entry.get('confidence')!r} not in {', '.join(CONFIDENCES)}",
            )
            problems += 1
        invalidated = entry.get("invalidated_by")
        if not isinstance(invalidated, str) or not invalidated.strip():
            report.fail("G-15", where, "invalidated_by must name the fact that would break it")
            problems += 1
        stage = entry.get("recheck_stage")
        if stage not in RECHECK_STAGES:
            report.fail(
                "G-15",
                where,
                f"recheck_stage {stage!r} not in {', '.join(RECHECK_STAGES)}",
            )
            problems += 1
        downstream = entry.get("downstream_stages")
        if not isinstance(downstream, list):
            report.fail("G-15", where, "downstream_stages must be an array")
            problems += 1
        field_path = entry.get("field_path")
        if not isinstance(field_path, str):
            report.fail(
                "G-15", where, "field_path must be a dotted path, or "
                "'<spec-name>:<dotted path>' to name the file it lives in"
            )
            problems += 1
            continue
        resolved = resolve_ledger_path(field_path, session)
        if not resolved.found:
            report.fail(
                "G-15",
                where,
                f"field_path {field_path!r} is outside the project it belongs to "
                f"({resolved.reason})",
            )
            problems += 1
            continue
        owner = session.by_name(resolved.owner)
        owner_doc = owner.doc if owner is not None else None
        if isinstance(owner_doc, dict) and owner_doc.get("project") != doc.get("project"):
            report.fail(
                "G-15",
                where,
                f"project mismatch: {doc.get('project')!r} in assumptions vs "
                f"{owner_doc.get('project')!r} in {resolved.label}; a ledger may not "
                "cross project boundaries",
            )
            problems += 1

    cross = doc.get("cross_references")
    if not isinstance(cross, dict):
        report.fail("G-15", location, "cross_references must be an object")
        problems += 1
    else:
        if not isinstance(cross.get("note"), str) or not cross["note"].strip():
            report.fail("G-15", location, "cross_references.note must be non-empty")
            problems += 1
        listing = cross.get("conflict_sourced_paths")
        if not isinstance(listing, list):
            report.fail("G-15", location, "cross_references.conflict_sourced_paths must be an array")
            problems += 1
        else:
            for item in listing:
                if not isinstance(item, dict):
                    report.fail("G-15", location, "conflict_sourced_paths entries must be objects")
                    problems += 1
                    continue
                if not isinstance(item.get("path"), str) or not isinstance(
                    item.get("conflict_ref"), str
                ):
                    report.fail(
                        "G-15",
                        location,
                        "conflict_sourced_paths entries need { path, conflict_ref }",
                    )
                    problems += 1

    if problems == 0:
        report.ok("G-15", location, f"{len(entries)} assumption entries complete")


# --------------------------------------------------------------------------- #
# G-16 ranges
# --------------------------------------------------------------------------- #


def check_ranges(record: LoadedFile, report: Report) -> None:
    """G-16. Every numeric value within the range 07 declares for its key."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict) or record.spec is None or record.spec.name != "dimensions":
        p5_rules = P5_RANGE_RULES.get(record.spec.name) if record.spec is not None else None
        if p5_rules is not None:
            problems = 0
            checked = 0
            for pattern, low, high, low_inc, high_inc, unit in p5_rules:
                for path, value in iter_pattern(doc, pattern):
                    number = as_number(value)
                    if number is None:
                        report.fail(
                            "G-16", f"{location}::{path}", f"value {value!r} is not a number"
                        )
                        problems += 1
                        continue
                    checked += 1
                    bound = _range_text(low, high, low_inc, high_inc, unit)
                    if not _in_range(number, low, high, low_inc, high_inc):
                        report.fail(
                            "G-16",
                            f"{location}::{path}",
                            f"{fmt_number(value)}{unit} outside declared range {bound}",
                        )
                        problems += 1
            if problems == 0:
                report.ok(
                    "G-16",
                    location,
                    f"{checked} ranged values in range (range checks are exact)",
                )
            return
        if record.spec is not None and record.spec.state == "defined":
            report.skip(
                "G-16",
                location,
                "07 declares no numeric range for this file; a key with no declared "
                "range is unbounded",
            )
        return

    problems = 0
    checked = 0
    for pattern, low, high, low_inc, high_inc, unit in RANGE_RULES:
        for path, value in iter_pattern(doc, pattern):
            number = as_number(value)
            if number is None:
                report.fail("G-16", f"{location}::{path}", f"value {value!r} is not a number")
                problems += 1
                continue
            checked += 1
            bound = _range_text(low, high, low_inc, high_inc, unit)
            if not _in_range(number, low, high, low_inc, high_inc):
                report.fail(
                    "G-16",
                    f"{location}::{path}",
                    f"{fmt_number(value)}{unit} outside declared range {bound}",
                )
                problems += 1

    problems += _check_opening_ranges(doc, location, report)
    checked += len(doc.get("openings") or []) if isinstance(doc.get("openings"), list) else 0

    if problems == 0:
        report.ok("G-16", location, f"{checked} ranged values in range (range checks are exact)")


def _check_opening_ranges(doc: Any, location: str, report: Report) -> int:
    problems = 0
    openings = doc.get("openings")
    if not isinstance(openings, list):
        return 0
    for index, opening in enumerate(openings):
        if not isinstance(opening, dict):
            continue
        kind = opening.get("type")
        where = f"{location}::openings[{index}]"
        if kind not in OPENING_RANGES:
            continue  # vocabulary is G-28
        for key, (low, high) in OPENING_RANGES[kind].items():
            number = as_number(opening.get(key))
            if number is None:
                continue
            if not (low - 1e-9 <= number <= high + 1e-9):
                report.fail(
                    "G-16",
                    f"{where}.{key}",
                    f"{fmt_number(number)}cm outside the {kind} range "
                    f"{fmt_number(low)}..{fmt_number(high)} cm (07 section 5.11)",
                )
                problems += 1
    return problems


def _range_text(low: Any, high: Any, low_inc: bool, high_inc: bool, unit: str) -> str:
    left = f"{'>' if not low_inc else '>='}{fmt_number(low)}" if low is not None else ""
    right = f"{fmt_number(high)}{'<' if not high_inc else '<='}" if high is not None else ""
    parts = [p for p in (left, right) if p]
    return (" ".join(parts) or "unbounded") + (f" {unit}" if unit else "")


def _in_range(value: float, low: Optional[float], high: Optional[float], low_inc: bool, high_inc: bool) -> bool:
    if low is not None:
        if value < low - 1e-9 if low_inc else value <= low + 1e-9:
            return False
    if high is not None:
        if value > high + 1e-9 if high_inc else value >= high - 1e-9:
            return False
    return True


# --------------------------------------------------------------------------- #
# G-17..G-30 geometry
# --------------------------------------------------------------------------- #


def check_geometry(record: LoadedFile, session: Session, report: Report) -> None:
    """Dispatch the dimensional-geometry rules that need dimensions.json."""
    if not isinstance(record.doc, dict) or record.spec is None:
        return
    if record.spec.state != "defined":
        report.skip(
            "G-16..G-30",
            record.label,
            f"{record.spec.name} is reserved by 07 section 4 (owner {record.spec.owner}); "
            "its body has no schema yet, so no geometric rule applies",
        )
        return
    if record.spec.name != "dimensions":
        return

    doc = record.doc
    linear, area, angle, source = session.tolerances()
    tol_linear = f"{linear} cm ({source})"
    tol_area = f"{area} m2 ({source})"

    _g17_levels_ordered(record, session, report, linear)
    _g18_level_chain(record, report, linear, tol_linear)
    _g19_total_height(record, report, linear, tol_linear)
    _g20_overall_height(record, report, linear, tol_linear)
    _g21_polygons(record, session, report, linear, tol_linear)
    _g22_core_inside(record, report, linear, tol_linear)
    _g23_core_on_grid(record, report, linear, tol_linear)
    _g24_grid_spans(record, report, linear, tol_linear)
    _g25_facades_close(record, report, linear, tol_linear)
    _g26_openings_sane(record, report, tol_linear)
    _g27_openings_fit(record, report, linear, tol_linear)
    _g28_openings_unique(record, report)
    _g29_areas(record, report, area, tol_area)
    _g30_roof(record, report, linear, tol_linear)
    # angle_deg is declared (G-33) but 07 section 9.3 states no angle equality rule,
    # so nothing below consumes it. It is not applied to a length or an area.


def _levels(doc: Any) -> Optional[list[dict]]:
    levels = doc.get("levels")
    if not isinstance(levels, list):
        return None
    return [lv for lv in levels if isinstance(lv, dict)]


def _g17_levels_ordered(record: LoadedFile, session: Session, report: Report, linear: float) -> None:
    location = record.label
    levels = _levels(record.doc)
    if levels is None:
        report.fail("G-17", location, "levels is missing or not an array")
        return
    if not levels:
        report.fail("G-17", location, "levels must hold at least one storey")
        return
    problems = 0
    for position, level in enumerate(levels):
        if level.get("index") != position:
            report.fail(
                "G-17",
                f"{location}::levels[{position}].index",
                f"index is {level.get('index')!r}; index is positional and must equal "
                "the array position",
            )
            problems += 1
    for position in range(1, len(levels)):
        previous = as_number(levels[position - 1].get("elevation_cm"))
        current = as_number(levels[position].get("elevation_cm"))
        if previous is None or current is None:
            continue
        if current <= previous:
            report.fail(
                "G-17",
                f"{location}::levels[{position}].elevation_cm",
                f"elevation {fmt_number(current)} does not strictly increase over "
                f"{fmt_number(previous)}; levels run bottom to top",
            )
            problems += 1
    if problems == 0:
        report.ok("G-17", location, f"{len(levels)} levels ordered bottom to top")


def _g18_level_chain(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    levels = _levels(record.doc)
    if levels is None:
        report.fail("G-18", location, "levels is missing; the vertical chain cannot be built")
        return
    problems = 0
    for position in range(1, len(levels)):
        base = as_number(levels[position - 1].get("elevation_cm"))
        height = as_number(levels[position - 1].get("height_cm"))
        current = as_number(levels[position].get("elevation_cm"))
        if base is None or height is None or current is None:
            report.skip(
                "G-18",
                f"{location}::levels[{position}]",
                "elevation_cm or height_cm missing; the chain cannot be evaluated",
            )
            continue
        expected = base + height
        if not close(current, expected, linear):
            report.fail(
                "G-18",
                f"{location}::levels[{position}].elevation_cm",
                f"level chaining: levels[{position}].elevation_cm {fmt_number(current)} != "
                f"{fmt_number(base)} + {fmt_number(height)} = {fmt_number(expected)}",
                tol,
            )
            problems += 1
    if problems == 0 and len(levels) > 1:
        report.ok(
            "G-18",
            location,
            f"chain {len(levels) - 1} step(s) closed within {linear} cm",
        )
    elif problems == 0:
        report.ok("G-18", location, "single-storey project; the chain has no step to close")


def _g19_total_height(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    levels = _levels(record.doc)
    building = record.doc.get("building")
    if levels is None or not isinstance(building, dict):
        report.skip("G-19", location, "building or levels missing; nothing to compare")
        return
    total = as_number(building.get("total_height_cm"))
    base = as_number(levels[-1].get("elevation_cm"))
    height = as_number(levels[-1].get("height_cm"))
    if total is None or base is None or height is None:
        report.skip("G-19", location, "building.total_height_cm or the top level is missing")
        return
    expected = base + height
    if not close(total, expected, linear):
        report.fail(
            "G-19",
            f"{location}::building.total_height_cm",
            f"total height {fmt_number(total)} != levels[-1].elevation_cm "
            f"{fmt_number(base)} + levels[-1].height_cm {fmt_number(height)} = {fmt_number(expected)}",
            tol,
        )
        return
    report.ok(
        "G-19",
        location,
        f"total height {fmt_number(total)} cm is the top of the chain",
        tol,
    )


def _g20_overall_height(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    building = record.doc.get("building")
    roof = record.doc.get("roof")
    if not isinstance(building, dict) or not isinstance(roof, dict):
        report.skip("G-20", location, "building or roof missing; nothing to compare")
        return
    overall = as_number(building.get("overall_height_cm"))
    total = as_number(building.get("total_height_cm"))
    parapet = as_number(roof.get("parapet_height_cm"))
    if overall is None or total is None or parapet is None:
        report.skip("G-20", location, "overall_height_cm, total_height_cm or parapet missing")
        return
    expected = total + parapet
    if not close(overall, expected, linear):
        report.fail(
            "G-20",
            f"{location}::building.overall_height_cm",
            f"overall height {fmt_number(overall)} != total {fmt_number(total)} + parapet "
            f"{fmt_number(parapet)} = {fmt_number(expected)}",
            tol,
        )
        return
    report.ok("G-20", location, f"overall height includes the {fmt_number(parapet)} cm parapet", tol)


def _polygon_check(
    location: str,
    path: str,
    ring: Sequence[Sequence[float]],
    declared_ccw: Any,
    tol: str,
    report: Report,
    rule: str = "G-21",
) -> int:
    problems = 0
    if len(ring) < 3:
        report.fail(rule, f"{location}::{path}", f"polygon has {len(ring)} vertices, needs >= 3")
        return 1
    seen: set[tuple[float, float]] = set()
    for index, point in enumerate(ring):
        key = (round(point[0], 6), round(point[1], 6))
        if key in seen:
            report.fail(rule, f"{location}::{path}", f"duplicate vertex {list(key)} at index {index}")
            problems += 1
        seen.add(key)
    crossing = self_intersects(ring, tol_value(tol))
    if crossing is not None:
        report.fail(rule, f"{location}::{path}", f"ring self-intersects (edges {crossing})", tol)
        problems += 1
    signed = polygon_signed_area_cm2(ring)
    if abs(signed) < 1e-9:
        report.fail(rule, f"{location}::{path}", "polygon has zero area", tol)
        problems += 1
        return problems
    actual_ccw = signed > 0
    if declared_ccw is None:
        report.skip(
            rule,
            f"{location}::{path}",
            "no sibling *_ccw flag exists for this ring in 07 section 5.7, so the "
            f"declared winding cannot be confirmed; ring is "
            f"{'CCW' if actual_ccw else 'CW'}",
        )
    elif not isinstance(declared_ccw, bool):
        report.fail(rule, f"{location}::{path}", f"*_ccw flag is {declared_ccw!r}, expected a bool")
        problems += 1
    elif declared_ccw != actual_ccw:
        report.fail(
            rule,
            f"{location}::{path}",
            f"declared {'CCW' if declared_ccw else 'CW'} but the ring is "
            f"{'CCW' if actual_ccw else 'CW'} (signed area {fmt_number(signed / 10000)} m2)",
            tol,
        )
        problems += 1
    return problems


def tol_value(tol: str) -> float:
    try:
        return float(tol.split(" ", 1)[0])
    except (ValueError, IndexError):
        return FALLBACK_LINEAR_CM


def _g21_polygons(record: LoadedFile, session: Session, report: Report, linear: float, tol: str) -> None:
    location = record.label
    site = record.doc.get("site")
    core = record.doc.get("core")
    problems = 0
    if isinstance(site, dict):
        kind = site.get("footprint_kind")
        ring = expand_footprint_ring(site.get("footprint_cm"), kind if isinstance(kind, str) else "")
        if not ring:
            report.skip("G-21", location, "site.footprint_cm missing; no polygon to test")
        else:
            problems += _polygon_check(
                location, "site.footprint_cm", ring, site.get("footprint_ccw"), tol, report
            )
            if site.get("footprint_ccw") is not None:
                report.ok(
                    "G-21",
                    f"{location}::site.footprint_cm",
                    f"{len(ring)} distinct vertices, simple ring, winding matches "
                    "footprint_ccw",
                    tol,
                )
    if isinstance(core, dict):
        kind = core.get("footprint_kind")
        ring = expand_footprint_ring(core.get("footprint_cm"), kind if isinstance(kind, str) else "")
        if not ring:
            report.skip("G-21", location, "core.footprint_cm missing; no polygon to test")
        else:
            problems += _polygon_check(
                location, "core.footprint_cm", ring, core.get("footprint_ccw"), tol, report
            )


def _site_ring(doc: Any) -> Optional[list[list[float]]]:
    site = doc.get("site")
    if not isinstance(site, dict):
        return None
    kind = site.get("footprint_kind")
    ring = expand_footprint_ring(site.get("footprint_cm"), kind if isinstance(kind, str) else "")
    return ring if ring and len(ring) >= 3 else None


def _core_ring(doc: Any) -> Optional[list[list[float]]]:
    core = doc.get("core")
    if not isinstance(core, dict):
        return None
    kind = core.get("footprint_kind")
    ring = expand_footprint_ring(core.get("footprint_cm"), kind if isinstance(kind, str) else "")
    return ring if ring and len(ring) >= 3 else None


def _g22_core_inside(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    site_ring = _site_ring(record.doc)
    core_ring = _core_ring(record.doc)
    if site_ring is None or core_ring is None:
        report.skip("G-22", location, "site.footprint_cm or core.footprint_cm missing")
        return
    problems = 0
    for index, vertex in enumerate(core_ring):
        if not point_in_ring(vertex, site_ring, linear, strict=False):
            report.fail(
                "G-22",
                f"{location}::core.footprint_cm[{index}]",
                f"core vertex {fmt_number(vertex[0])},{fmt_number(vertex[1])} is outside "
                "site.footprint_cm (boundary counts as inside)",
                tol,
            )
            problems += 1
    if problems == 0:
        report.ok(
            "G-22",
            location,
            f"{len(core_ring)} core vertices inside or on the footprint ring",
            tol,
        )


def _g23_core_on_grid(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    doc = record.doc
    core_ring = _core_ring(doc)
    site_ring = _site_ring(doc)
    structure = doc.get("structure")
    if core_ring is None or not isinstance(structure, dict) or site_ring is None:
        report.skip("G-23", location, "core.footprint_cm, site.footprint_cm or structure missing")
        return
    x_bays = _numbers(structure.get("x_bay_cm"))
    y_bays = _numbers(structure.get("y_bay_cm"))
    if x_bays is None or y_bays is None:
        report.skip("G-23", location, "x_bay_cm or y_bay_cm missing")
        return
    kind = (doc.get("site") or {}).get("footprint_kind")
    if kind != "rectangle":
        x0 = min(p[0] for p in site_ring)
        y0 = min(p[1] for p in site_ring)
        if abs(x0) > linear or abs(y0) > linear:
            report.skip(
                "G-23",
                location,
                f"the grid origin for a non-rectangular footprint is undefined: the ring's "
                f"min corner is ({fmt_number(x0)},{fmt_number(y0)}), so cumulative bay "
                "offsets cannot be placed on it. 07 fixes the rule for axis-aligned rings "
                "only; add a footprint-level grid origin to close this.",
            )
            return
    x_lines = cumulative(x_bays)
    y_lines = cumulative(y_bays)
    problems = 0
    for index, vertex in enumerate(core_ring):
        if not _near_any(vertex[0], x_lines, linear):
            report.fail(
                "G-23",
                f"{location}::core.footprint_cm[{index}]",
                f"core X {fmt_number(vertex[0])} is not on a cumulative x_bay_cm grid line "
                f"{[fmt_number(v) for v in x_lines]}; a core may not cut a bay in half",
                tol,
            )
            problems += 1
        if not _near_any(vertex[1], y_lines, linear):
            report.fail(
                "G-23",
                f"{location}::core.footprint_cm[{index}]",
                f"core Y {fmt_number(vertex[1])} is not on a cumulative y_bay_cm grid line "
                f"{[fmt_number(v) for v in y_lines]}",
                tol,
            )
            problems += 1
    if problems == 0:
        report.ok(
            "G-23",
            location,
            f"all core vertices on grid lines "
            f"X{[fmt_number(v) for v in x_lines]} Y{[fmt_number(v) for v in y_lines]}",
            tol,
        )


def _near_any(value: float, candidates: Sequence[float], tol: float) -> bool:
    return any(abs(value - candidate) <= tol + 1e-9 for candidate in candidates)


def _g24_grid_spans(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    doc = record.doc
    structure = doc.get("structure")
    site_ring = _site_ring(doc)
    if not isinstance(structure, dict) or site_ring is None:
        report.skip("G-24", location, "structure or site.footprint_cm missing")
        return
    width = max(p[0] for p in site_ring) - min(p[0] for p in site_ring)
    depth = max(p[1] for p in site_ring) - min(p[1] for p in site_ring)
    problems = 0
    for axis, bays, extent in (
        ("x", _numbers(structure.get("x_bay_cm")), width),
        ("y", _numbers(structure.get("y_bay_cm")), depth),
    ):
        if bays is None:
            report.skip("G-24", location, f"{axis}_bay_cm missing")
            continue
        total = sum(bays)
        if not close(total, extent, linear):
            report.fail(
                "G-24",
                f"{location}::structure.{axis}_bay_cm",
                f"sum {fmt_number(total)} cm != site footprint "
                f"{'width' if axis == 'x' else 'depth'} {fmt_number(extent)} cm; the grid "
                "must span the footprint exactly",
                tol,
            )
            problems += 1
        for index, bay in enumerate(bays):
            if bay <= 0:
                report.fail(
                    "G-24",
                    f"{location}::structure.{axis}_bay_cm[{index}]",
                    f"bay {fmt_number(bay)} cm is not greater than zero",
                )
                problems += 1
        for key in ("column_x_cm", "column_y_cm"):
            values = _numbers(structure.get(key))
            if values is None:
                continue
            for index, coordinate in enumerate(values):
                point = [coordinate, min(p[1] for p in site_ring) + depth / 2.0] if key == "column_x_cm" else [
                    min(p[0] for p in site_ring) + width / 2.0,
                    coordinate,
                ]
                if not point_in_ring(point, site_ring, linear, strict=True):
                    report.fail(
                        "G-24",
                        f"{location}::structure.{key}[{index}]",
                        f"{fmt_number(coordinate)} is not strictly inside the footprint",
                        tol,
                    )
                    problems += 1
    if problems == 0:
        report.ok(
            "G-24",
            location,
            f"grid spans {fmt_number(width)} x {fmt_number(depth)} cm exactly, "
            "all bays positive, all column lines strictly inside",
            tol,
        )


def _facades(doc: Any) -> list[dict]:
    facades = doc.get("facades")
    if not isinstance(facades, list):
        return []
    return [f for f in facades if isinstance(f, dict)]


def _g25_facades_close(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    doc = record.doc
    facades = _facades(doc)
    site_ring = _site_ring(doc)
    if not facades or site_ring is None:
        report.skip("G-25", location, "facades or site.footprint_cm missing")
        return
    problems = 0
    for index, facade in enumerate(facades):
        where = f"{location}::facades[{index}]"
        start, end = facade.get("start_corner_cm"), facade.get("end_corner_cm")
        if not is_point(start) or not is_point(end):
            report.fail("G-25", where, "start_corner_cm / end_corner_cm missing or malformed")
            problems += 1
            continue
        for label, corner in (("start_corner_cm", start), ("end_corner_cm", end)):
            if not _on_ring(corner, site_ring, linear):
                report.fail(
                    "G-25",
                    f"{where}.{label}",
                    f"{fmt_number(corner[0])},{fmt_number(corner[1])} is not a "
                    "site.footprint_cm vertex",
                    tol,
                )
                problems += 1
        span = distance(start, end)
        declared_length = as_number(facade.get("length_cm"))
        if declared_length is None or not close(declared_length, span, linear):
            report.fail(
                "G-25",
                f"{where}.length_cm",
                f"length {fmt_number(declared_length)} != corner-to-corner distance "
                f"{fmt_number(span)}",
                tol,
            )
            problems += 1
        bays = facade.get("bay_width_cm")
        bay_numbers = _numbers(bays)
        if bay_numbers is None:
            report.fail("G-25", where, "bay_width_cm missing or not numeric")
            problems += 1
            continue
        if facade.get("bay_count") != len(bay_numbers):
            report.fail(
                "G-25",
                f"{where}.bay_count",
                f"bay_count {facade.get('bay_count')!r} != len(bay_width_cm) "
                f"{len(bay_numbers)}",
            )
            problems += 1
        total = sum(bay_numbers)
        if not close(total, span, linear):
            report.fail(
                "G-25",
                f"{where}.bay_width_cm",
                f"sum {fmt_number(total)} cm != facade length {fmt_number(span)} cm",
                tol,
            )
            problems += 1
        for bay_index, bay in enumerate(bay_numbers):
            if bay <= 0:
                report.fail(
                    "G-25",
                    f"{where}.bay_width_cm[{bay_index}]",
                    f"bay {fmt_number(bay)} cm is not greater than zero",
                )
                problems += 1
    if problems == 0:
        report.ok(
            "G-25",
            location,
            f"{len(facades)} facades close on footprint vertices; bay sums equal lengths",
            tol,
        )


def _on_ring(corner: Sequence[Any], ring: Sequence[Sequence[float]], tol: float) -> bool:
    point = [as_number(corner[0]) or 0.0, as_number(corner[1]) or 0.0]
    for index in range(len(ring)):
        if _on_segment(ring[index], ring[(index + 1) % len(ring)], point, tol):
            return True
    return False


def _openings(doc: Any) -> list[dict]:
    openings = doc.get("openings")
    if not isinstance(openings, list):
        return []
    return [o for o in openings if isinstance(o, dict)]


def _facade_by_id(doc: Any) -> dict[str, dict]:
    return {str(f.get("id")): f for f in _facades(doc)}


def _level_heights(doc: Any) -> dict[int, float]:
    heights: dict[int, float] = {}
    for position, level in enumerate(_levels(doc) or []):
        value = as_number(level.get("height_cm"))
        if value is not None:
            heights[position] = value
            if is_int(level.get("index")):
                heights[int(level["index"])] = value
    return heights


def _g26_openings_sane(record: LoadedFile, report: Report, tol: str) -> None:
    location = record.label
    doc = record.doc
    openings = _openings(doc)
    heights = _level_heights(doc)
    if not openings:
        report.skip("G-26", location, "openings is empty; nothing to test (07 section 5.11 allows it)")
        return
    problems = 0
    for index, opening in enumerate(openings):
        where = f"{location}::openings[{index}]"
        width = as_number(opening.get("width_cm"))
        sill = as_number(opening.get("sill_cm"))
        head = as_number(opening.get("head_cm"))
        position = as_number(opening.get("position_cm"))
        level_index = opening.get("level_index")
        if None in (width, sill, head, position):
            report.fail("G-26", where, "width_cm, sill_cm, head_cm or position_cm missing")
            problems += 1
            continue
        if width <= 0:
            report.fail("G-26", f"{where}.width_cm", f"width {fmt_number(width)} is not > 0")
            problems += 1
        if head - sill <= 0:
            report.fail(
                "G-26",
                where,
                f"head_cm - sill_cm = {fmt_number(head - sill)} is not > 0",
            )
            problems += 1
        if sill < 0:
            report.fail("G-26", f"{where}.sill_cm", f"sill {fmt_number(sill)} is < 0")
            problems += 1
        if position < 0:
            report.fail("G-26", f"{where}.position_cm", f"position {fmt_number(position)} is < 0")
            problems += 1
        floor_to_floor = heights.get(level_index) if is_int(level_index) else None
        if floor_to_floor is None:
            report.skip(
                "G-26",
                where,
                f"level_index {level_index!r} has no height_cm; head <= floor-to-floor "
                "cannot be evaluated",
            )
            continue
        if head > floor_to_floor + 1e-9:
            report.fail(
                "G-26",
                f"{where}.head_cm",
                f"head {fmt_number(head)} > levels[{level_index}].height_cm "
                f"{fmt_number(floor_to_floor)}",
                tol,
            )
            problems += 1
    if problems == 0:
        report.ok("G-26", location, f"{len(openings)} openings physically sane", tol)


def _g27_openings_fit(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    doc = record.doc
    openings = _openings(doc)
    facades = _facade_by_id(doc)
    if not openings:
        report.skip("G-27", location, "openings is empty; nothing to fit")
        return
    problems = 0
    exact = "exact (07 section 9.5: G-27's strict < on width_cm has no tolerance)"
    for index, opening in enumerate(openings):
        where = f"{location}::openings[{index}]"
        facade = facades.get(str(opening.get("facade")))
        if facade is None:
            continue  # G-28 reports the dangling facade ref
        bays = _numbers(facade.get("bay_width_cm"))
        bay_index = opening.get("bay_index")
        width = as_number(opening.get("width_cm"))
        position = as_number(opening.get("position_cm"))
        if bays is None or not is_int(bay_index) or width is None or position is None:
            report.skip(
                "G-27",
                where,
                "bay_width_cm, bay_index, width_cm or position_cm missing; fit cannot be evaluated",
            )
            continue
        if not 0 <= bay_index < len(bays):
            continue  # G-28 reports the out-of-range index
        host = bays[bay_index]
        if width >= host:
            report.fail(
                "G-27",
                f"{where}.width_cm",
                f"width {fmt_number(width)} is not strictly less than its host bay "
                f"{fmt_number(host)} cm; the structural bay always keeps a pier or mullion",
                exact,
            )
            problems += 1
        lines = cumulative(bays)
        bay_start, bay_end = lines[bay_index], lines[bay_index + 1]
        if position - width / 2.0 < bay_start - linear - 1e-9:
            report.fail(
                "G-27",
                f"{where}.position_cm",
                f"opening starts at {fmt_number(position - width / 2.0)} cm, before its bay "
                f"start {fmt_number(bay_start)} cm",
                tol,
            )
            problems += 1
        if position + width / 2.0 > bay_end + linear + 1e-9:
            report.fail(
                "G-27",
                f"{where}.position_cm",
                f"opening ends at {fmt_number(position + width / 2.0)} cm, past its bay end "
                f"{fmt_number(bay_end)} cm",
                tol,
            )
            problems += 1
    if problems == 0:
        report.ok(
            "G-27",
            location,
            f"{len(openings)} openings strictly inside their host bay",
            tol,
        )


def _g28_openings_unique(record: LoadedFile, report: Report) -> None:
    location = record.label
    doc = record.doc
    openings = _openings(doc)
    if not openings:
        report.skip("G-28", location, "openings is empty; nothing to collide")
        return
    facades = _facade_by_id(doc)
    level_indices = {level.get("index") for level in (_levels(doc) or [])}
    problems = 0
    seen_ids: dict[str, int] = {}
    slots: dict[tuple[Any, Any, Any], str] = {}
    for index, opening in enumerate(openings):
        where = f"{location}::openings[{index}]"
        ident = opening.get("id")
        if not isinstance(ident, str) or not ident.strip():
            report.fail("G-28", where, f"id {ident!r} is missing or empty")
            problems += 1
        elif ident in seen_ids:
            report.fail(
                "G-28",
                where,
                f"duplicate opening id {ident!r}; also at openings[{seen_ids[ident]}]",
            )
            problems += 1
        else:
            seen_ids[ident] = index
        slot = (opening.get("facade"), opening.get("level_index"), opening.get("bay_index"))
        if slot in slots:
            report.fail(
                "G-28",
                where,
                f"slot {slot} is already taken by {slots[slot]!r}; two openings may not "
                "share a (facade, level_index, bay_index)",
            )
            problems += 1
        else:
            slots[slot] = ident if isinstance(ident, str) else f"openings[{index}]"
        if str(opening.get("facade")) not in facades:
            report.fail(
                "G-28",
                f"{where}.facade",
                f"facade {opening.get('facade')!r} does not exist in facades[].id",
            )
            problems += 1
        if opening.get("level_index") not in level_indices:
            report.fail(
                "G-28",
                f"{where}.level_index",
                f"level_index {opening.get('level_index')!r} does not exist in levels[]",
            )
            problems += 1
        bay_index = opening.get("bay_index")
        facade = facades.get(str(opening.get("facade")))
        if facade is not None and is_int(bay_index):
            if not 0 <= bay_index < len(facade.get("bay_width_cm") or []):
                report.fail(
                    "G-28",
                    f"{where}.bay_index",
                    f"bay_index {bay_index} is outside the facade's bay_count "
                    f"{facade.get('bay_count')!r}",
                )
                problems += 1
        if opening.get("type") not in OPENING_TYPES:
            report.fail(
                "G-28",
                f"{where}.type",
                f"type {opening.get('type')!r} is not in "
                f"{', '.join(OPENING_TYPES)} (07 section 5.11)",
            )
            problems += 1
    if problems == 0:
        report.ok("G-28", location, f"{len(openings)} opening ids, slots and types valid")


def _core_share(doc: Any, level_index: Any) -> Optional[float]:
    core = doc.get("core")
    if not isinstance(core, dict):
        return None
    area = as_number(core.get("footprint_area_m2"))
    spans = core.get("spans_level_indices")
    if area is None or not isinstance(spans, list):
        return None
    return area if level_index in spans else 0.0


def _g29_areas(record: LoadedFile, report: Report, area: float, tol: str) -> None:
    location = record.label
    doc = record.doc
    building = doc.get("building")
    site = doc.get("site")
    plates = doc.get("floor_plates")
    if not isinstance(building, dict) or not isinstance(site, dict) or not isinstance(plates, list):
        report.skip("G-29", location, "building, site or floor_plates missing")
        return
    problems = 0
    footprint_area = as_number(site.get("footprint_area_m2"))
    if footprint_area is None:
        report.skip("G-29", location, "site.footprint_area_m2 missing")
        return
    total = 0.0
    for index, plate in enumerate(plates):
        if not isinstance(plate, dict):
            continue
        gross = as_number(plate.get("gross_area_m2"))
        if gross is None:
            report.skip("G-29", f"{location}::floor_plates[{index}]", "gross_area_m2 missing")
            continue
        total += gross
        if not close(gross, footprint_area, area):
            report.fail(
                "G-29",
                f"{location}::floor_plates[{index}].gross_area_m2",
                f"gross {fmt_number(gross)} m2 != site.footprint_area_m2 "
                f"{fmt_number(footprint_area)} m2 (prismatic building)",
                tol,
            )
            problems += 1
        usable = as_number(plate.get("net_usable_area_m2"))
        if usable is None:
            continue
        share = _core_share(doc, plate.get("level_index"))
        if share is None:
            report.skip(
                "G-29",
                f"{location}::floor_plates[{index}].net_usable_area_m2",
                "core.spans_level_indices or core.footprint_area_m2 missing; the core "
                "share is unknown",
            )
            continue
        ceiling = gross - share
        if not (usable > 0) or usable > ceiling + 1e-9:
            report.fail(
                "G-29",
                f"{location}::floor_plates[{index}].net_usable_area_m2",
                f"net usable {fmt_number(usable)} m2 must satisfy 0 < x <= gross "
                f"{fmt_number(gross)} - core share {fmt_number(share)} = {fmt_number(ceiling)} m2",
                tol,
            )
            problems += 1
    declared_gross = as_number(building.get("gross_floor_area_m2"))
    if declared_gross is None or not close(declared_gross, total, area):
        report.fail(
            "G-29",
            f"{location}::building.gross_floor_area_m2",
            f"declared {fmt_number(declared_gross)} m2 != sum of floor_plates gross "
            f"{fmt_number(total)} m2",
            tol,
        )
        problems += 1
    declared_net = as_number(building.get("net_floor_area_m2"))
    core = doc.get("core")
    core_area = as_number(core.get("footprint_area_m2")) if isinstance(core, dict) else None
    spans = core.get("spans_level_indices") if isinstance(core, dict) else None
    if (
        declared_net is not None
        and core_area is not None
        and isinstance(spans, list)
        and declared_gross is not None
    ):
        expected = declared_gross - core_area * len(spans)
        if not close(declared_net, expected, area):
            report.fail(
                "G-29",
                f"{location}::building.net_floor_area_m2",
                f"declared {fmt_number(declared_net)} m2 != gross {fmt_number(declared_gross)} "
                f"- core {fmt_number(core_area)} m2 x {len(spans)} level(s) = "
                f"{fmt_number(expected)} m2",
                tol,
            )
            problems += 1
    else:
        report.skip(
            "G-29",
            f"{location}::building.net_floor_area_m2",
            "gross, core area or core.spans_level_indices missing; the net reconciliation "
            "cannot be evaluated",
        )
    if problems == 0:
        report.ok(
            "G-29",
            location,
            f"areas reconcile: {fmt_number(declared_gross)} gross, "
            f"{fmt_number(declared_net)} net over {len(plates)} plate(s)",
            tol,
        )


def _g30_roof(record: LoadedFile, report: Report, linear: float, tol: str) -> None:
    location = record.label
    doc = record.doc
    roof = doc.get("roof")
    building = doc.get("building")
    core = doc.get("core")
    if not isinstance(roof, dict) or not isinstance(building, dict):
        report.skip("G-30", location, "roof or building missing")
        return
    problems = 0
    deck = as_number(roof.get("deck_level_cm"))
    total = as_number(building.get("total_height_cm"))
    if deck is None or total is None:
        report.skip("G-30", location, "deck_level_cm or total_height_cm missing")
    elif not close(deck, total, linear):
        report.fail(
            "G-30",
            f"{location}::roof.deck_level_cm",
            f"deck {fmt_number(deck)} != building.total_height_cm {fmt_number(total)}",
            tol,
        )
        problems += 1
    spans = core.get("spans_level_indices") if isinstance(core, dict) else None
    indices = {level.get("index") for level in (_levels(doc) or [])}
    if spans is None:
        report.skip("G-30", location, "core.spans_level_indices missing")
    else:
        for value in spans:
            if value not in indices:
                report.fail(
                    "G-30",
                    f"{location}::core.spans_level_indices",
                    f"level index {value!r} does not exist in levels[]",
                )
                problems += 1
    if problems == 0:
        report.ok("G-30", location, f"roof deck agrees with total height; core spans resolve", tol)


# --------------------------------------------------------------------------- #
# G-31 cross-file references
# --------------------------------------------------------------------------- #


def check_cross_file(session: Session, report: Report) -> None:
    """G-31. Every id, path and ref a file names exists in the file declaring it."""
    dimensions = session.dimensions
    assumptions = session.assumptions
    conflicts = session.conflicts
    missing_siblings = [
        name
        for name in ("dimensions", "assumptions", "conflicts_resolved")
        if session.by_name(name) is None
        or not isinstance(session.by_name(name).doc, dict)
    ]
    if missing_siblings:
        report.skip(
            "G-31",
            ", ".join(sorted({r.label for r in session.files if r.ok})) or "(none)",
            f"cannot run: sibling file(s) not loaded: {', '.join(missing_siblings)}",
        )
        return

    assert dimensions is not None and assumptions is not None and conflicts is not None
    problems = 0
    doc = dimensions.doc if isinstance(dimensions.doc, dict) else {}

    # dimensions -> itself
    for key in ("building", "site", "structure", "levels", "core", "floor_plates", "roof",
                "facades", "openings"):
        found, _ = resolve(doc, key)
        if not found:
            report.fail("G-31", f"{dimensions.label}::{key}", "declared top-level key missing")
            problems += 1

    # conflicts -> dimensions
    conflict_entries = conflicts.doc.get("conflicts") or []
    for index, entry in enumerate(conflict_entries):
        if not isinstance(entry, dict):
            continue
        resolution = entry.get("resolution")
        if not isinstance(resolution, dict):
            continue
        for path in resolution.get("resolved_paths") or []:
            found, _ = resolve(doc, str(path))
            if not found:
                report.fail(
                    "G-31",
                    f"{conflicts.label}::{entry.get('id')}.resolution.resolved_paths",
                    f"path {path!r} does not resolve in dimensions.json",
                )
                problems += 1

    # assumptions -> dimensions + conflicts
    c_ids = _ledger_ids(conflicts, "conflicts", "C")
    a_entries = assumptions.doc.get("assumptions") or []
    for entry in a_entries:
        if not isinstance(entry, dict):
            continue
        for path in [entry.get("field_path")]:
            resolved = resolve_ledger_path(path, session)
            if not resolved.found:
                report.fail(
                    "G-31",
                    f"{assumptions.label}::{entry.get('id')}.field_path",
                    f"{resolved.reason}; a ledger field_path is either a bare dotted path in "
                    f"dimensions.json or '<spec-name>:<dotted path>' naming a loaded spec file",
                )
                problems += 1
    cross = assumptions.doc.get("cross_references")
    if isinstance(cross, dict):
        for item in cross.get("conflict_sourced_paths") or []:
            if not isinstance(item, dict):
                continue
            found, _ = resolve(doc, str(item.get("path")))
            if not found:
                report.fail(
                    "G-31",
                    f"{assumptions.label}::cross_references.conflict_sourced_paths",
                    f"path {item.get('path')!r} does not resolve in dimensions.json",
                )
                problems += 1
            if item.get("conflict_ref") not in c_ids:
                report.fail(
                    "G-31",
                    f"{assumptions.label}::cross_references.conflict_sourced_paths",
                    f"conflict_ref {item.get('conflict_ref')!r} does not resolve in "
                    "conflicts_resolved.json",
                )
                problems += 1

    # origin_inputs -> a dotted path *inside* a defined file
    #
    # An entry is a path, not a filename: ``levels[0].height_cm``,
    # ``floor_plates`` (a bare array name) and ``storeys[1].slab_ref`` (a path
    # into the reading file itself, which 07 section 4 permits) all occur. So
    # the path is walked with the same resolver the ``derives_from`` machinery
    # uses, against each defined file's parsed content, and the rule is that it
    # resolves in at least one of them. Comparing the first token against the set
    # of file names -- as an earlier revision did -- can never succeed, because
    # no path's first token is a file name.
    defined_records = [
        record
        for record in session.files
        if record.ok
        and record.spec is not None
        and record.spec.state == "defined"
        and isinstance(record.doc, dict)
    ]
    defined_names = {record.spec.name for record in defined_records if record.spec}
    for record in session.files:
        if not record.ok or record.spec is None:
            continue
        inputs = record.doc.get("origin_inputs") if isinstance(record.doc, dict) else None
        if not isinstance(inputs, list):
            continue
        for item in inputs:
            text = str(item)
            hosts = [host for host in defined_records if resolve(host.doc, text)[0]]
            if hosts:
                continue
            head = text.split(".", 1)[0].split("[", 1)[0]
            if head not in defined_names:
                detail = (
                    f"path {text!r} is not in a defined file; a file may only "
                    f"read {', '.join(sorted(defined_names))}"
                )
            else:
                detail = (
                    f"path {text!r} does not resolve in any defined file; 07 G-31 "
                    f"checked {', '.join(sorted(defined_names))}"
                )
            report.fail("G-31", f"{record.label}::origin_inputs", detail)
            problems += 1

    # 07 section 3.1: project is "identical across all files in one project"
    ids = {
        r.label: r.doc.get("project")
        for r in session.files
        if r.ok and isinstance(r.doc, dict)
    }
    distinct = {value for value in ids.values() if isinstance(value, str)}
    if len(distinct) > 1:
        report.fail(
            "G-31",
            ", ".join(sorted(ids)),
            "project id differs across files in one project (07 section 3.1): "
            + ", ".join(f"{label}={value!r}" for label, value in sorted(ids.items())),
        )
        problems += 1

    if problems == 0:
        report.ok(
            "G-31",
            dimensions.label,
            "all cross-file ids and dotted paths resolve; one project id "
            f"({next(iter(distinct))!r}) across {len(ids)} file(s)",
        )


def check_tolerances_declared(session: Session, report: Report) -> None:
    """G-33."""
    dimensions = session.dimensions
    if dimensions is None:
        if session.recipes_only:
            report.skip(
                "G-33",
                "(no dimensions.json)",
                "this run targets a recipe template library, not a project; a template "
                "declares its own tolerances block or falls back to the 07 section 9.5 "
                "defaults, and neither is a defect",
            )
            return
        report.fail(
            "G-33",
            "(no dimensions.json)",
            "dimensions.json is missing; tolerances are undeclared and every arithmetic "
            "rule would fall back to the 07 section 9.5 defaults",
        )
        return
    if dimensions is not None and (not dimensions.ok or not isinstance(dimensions.doc, dict)):
        report.skip(
            "G-33",
            dimensions.label,
            "dimensions.json is unreadable or not an object; G-7/G-1 already reported it, "
            "so the tolerance block cannot be inspected",
        )
        return
    block = dimensions.doc.get("tolerances")
    if not isinstance(block, dict):
        report.fail("G-33", dimensions.label, "tolerances must exist in dimensions.json")
        return
    problems = 0
    for key in ("linear_cm", "area_m2", "angle_deg"):
        value = block.get(key)
        number = as_number(value)
        if number is None:
            report.fail("G-33", f"{dimensions.label}::tolerances.{key}", f"{value!r} is missing")
            problems += 1
        elif number < 0:
            report.fail(
                "G-33",
                f"{dimensions.label}::tolerances.{key}",
                f"{fmt_number(number)} is negative",
            )
            problems += 1
    if problems == 0:
        report.ok(
            "G-33",
            dimensions.label,
            f"linear {fmt_number(block['linear_cm'])} cm, area {fmt_number(block['area_m2'])} m2, "
            f"angle {fmt_number(block['angle_deg'])} deg declared",
        )


# --------------------------------------------------------------------------- #
# G-34..G-40 massing (07 section 9.6)
#
# Same machinery as G-9..G-33, no new tolerance values: the leaf walker and
# coverage test come from G-9, the ring/simple-polygon checker from G-21, the
# dotted-path resolver from G-32, the tolerance from the file under test
# (_own_linear_tolerance, not Session.tolerances(), which only knows
# dimensions.json), and the origin/derives_from vocabulary from G-10.
# --------------------------------------------------------------------------- #


def _own_linear_tolerance(
    record: LoadedFile,
    session: Session,
    report: Report,
    *,
    skip_rule: Optional[str] = None,
) -> tuple[Optional[float], str]:
    """``linear_cm`` from this file's own ``tolerances`` block (07 section 8.1).

    07 section 9.5 makes every geometry row name the tolerance it used, and
    section 8.1 gives ``massing.json`` its own copy of the block -- ``copied
    verbatim from dimensions.json``, so the number agrees while the file that
    supplied it does not. ``Session.tolerances()`` only ever reads
    dimensions.json, so a massing row that takes its tolerance from there names
    the wrong block even though the value is right. Read it from the record
    under test instead.

    With no usable block the caller picks the fallback. ``skip_rule`` names the
    rule that would rather report a SKIP than borrow a tolerance (G-40, which
    compares a pivot against a bbox centre and has nothing else to say); it gets
    ``(None, "")`` back and its row is already written. Any other caller keeps its
    shape, vocabulary and chain checks -- none of which need a tolerance -- and
    falls back to the 07 section 9.5 default with a label that says so.
    """
    doc = record.doc
    block = doc.get("tolerances") if isinstance(doc, dict) else None
    value = as_number(block.get("linear_cm")) if isinstance(block, dict) else None
    if value is not None:
        return value, f"{value} cm ({record.label} tolerances)"
    if skip_rule is not None:
        report.skip(
            skip_rule,
            record.label,
            f"{record.label} declares no tolerances.linear_cm; {skip_rule} compares a "
            "pivot and will not assume a tolerance",
        )
        return None, ""
    linear, _area, _angle, _source = session.tolerances()
    return linear, (
        f"{linear} cm (07 section 9.5 fallback: {record.label} declares no "
        "tolerances.linear_cm)"
    )


#: 07 section 9.6 -- the massing rules that need a *computed* file. A draft
#: ``massing.json`` is the empty stub ``init_project.py`` writes: no origins to
#: cover, no elements to test, no storey chain to chase. G-39 is deliberately
#: absent: the layer vocabulary is declared in the stub, so the stub satisfies it
#: and that rule keeps running.
MASSING_DRAFT_RULES: tuple[str, ...] = ("G-34", "G-35", "G-36", "G-37", "G-38", "G-40")


def _draft_status(record: LoadedFile) -> Optional[str]:
    """The non-locked ``status`` that makes this file a draft, else None.

    Only a *string* status counts. G-4 already FAILs a missing or unknown one,
    and a file whose envelope is broken should keep its geometric rows rather
    than have them quietly disappear behind a status that never parsed.
    """
    if not isinstance(record.doc, dict):
        return None
    status = record.doc.get("status")
    if isinstance(status, str) and status != "locked":
        return status
    return None


def _is_empty_placeholder(record: LoadedFile) -> bool:
    """True when a draft file is still the untouched scaffold stub.

    The documented draft rule (07 sections 9.6 / 9.7 / 9.8 / 9.9) is *a draft file is not
    evaluated*. The flag ``--allow-draft`` exists so that G-4 reports a non-locked status
    and moves on rather than failing a build in progress -- it is a **status** flag, not a
    "force every geometric rule to run" flag, which is exactly how G-4 already treats it.

    A draft that has been **filled in** is still evaluated under ``--allow-draft``: a
    computed file with content has real provenance to check, and that feedback is the
    point of the flag. A draft that declares *nothing at all* is different, and the
    distinction is decidable rather than a matter of taste. ``massing.json``,
    ``nurbs.json``, ``facade_grids.json``, ``components_registry.json`` and
    ``assembly.json`` are all *computed*; the stub ``init_project.py`` writes has empty
    value trees, so every leaf is an empty array or an empty object. G-36, G-49, G-57,
    G-64, G-66 and the assembly rules then fail on the **absence of content**, which says
    nothing about the draft and everything about the scaffold -- and a check that cannot be
    evaluated reports SKIP with its reason, never a manufactured verdict.

    The predicate is deliberately narrow and asks one question: **does this draft contain
    a single row?** These computed files keep all of their content in arrays -- `elements`,
    `surfaces`, `panels`, `components`, `placements`, `opening_cuts`, `scatter` -- so an
    entirely empty array tree plus an empty `origins` is exactly the untouched scaffold.
    One row anywhere makes the file a draft that must be evaluated, and nothing here
    touches a `locked` file.
    """
    doc = record.doc
    if not isinstance(doc, dict):
        return False
    origins = doc.get("origins")
    if not isinstance(origins, dict) or origins:
        return False

    def holds_content(value: Any, top: bool) -> bool:
        if isinstance(value, dict):
            return any(holds_content(child, False) for key, child in value.items()
                       if not (top and key in ("tolerances", "origin_inputs")))
        if isinstance(value, list):
            if value:
                return True
            return any(holds_content(item, False) for item in value)
        return False

    for key, value in doc.items():
        if key in ENVELOPE_ORDER:
            continue
        if holds_content(value, True):
            return False
    return True


def _draft_skip_reason(
    record: LoadedFile,
    rules: tuple[str, ...],
    session: Session,
    report: Report,
    section: str,
    because: str,
) -> bool:
    """Emit the draft SKIP row for every rule in ``rules``; True when it fired.

    One implementation so the five computed files cannot drift: the reason text is the same
    shape everywhere, and the ``--allow-draft`` carve-out for an *empty* placeholder lives
    here rather than in five copies.
    """
    status = _draft_status(record)
    if status is None:
        return False
    placeholder = _is_empty_placeholder(record)
    if session.allow_draft and not placeholder:
        return False
    extra = (
        " This stub is empty as well, so there is nothing to evaluate at all: it declares no "
        "origins and no value leaves, and every rule in the set would be reporting the absence "
        "of content rather than a defect. An untouched scaffold is a placeholder, not a draft "
        "with findings."
        if placeholder
        else ""
    )
    for rule in rules:
        report.skip(
            rule,
            record.label,
            f'status={status} is not "locked"; 07 section {section} does not evaluate a draft '
            f"file, because {because}.{extra} --allow-draft forces the rule to run on a draft "
            "that has content, where it will fail.",
        )
    return True


def check_massing_rules(record: LoadedFile, session: Session, report: Report) -> None:
    """07 section 9.6: every massing rule, guarded one at a time.

    A ``draft`` massing file is **not evaluated** (07 section 9.6). ``massing.json``
    is computed by ``build_spec.py``, never hand-authored, so the placeholder a
    fresh scaffold writes has no provenance to check: G-34..G-38 and G-40 report
    SKIP with that reason instead of failing an empty tree. ``--allow-draft``
    forces them to run, where they do fail -- which is the point of the flag.
    G-39 runs either way, because the stub declares layers and is already
    correct; ``--build`` still refuses the file at G-4.
    """
    if _draft_skip_reason(
        record,
        MASSING_DRAFT_RULES,
        session,
        report,
        "9.6",
        "massing.json is computed by build_spec.py and this placeholder declares no "
        "provenance to check",
    ):
        guard("G-39", record.label, report, _g39_layer_vocabulary, record)
        return

    linear, tol_linear = _own_linear_tolerance(record, session, report)
    guard("G-34", record.label, report, _g34_identity, record)
    guard("G-35", record.label, report, _g35_solidity, record, linear, tol_linear)
    guard("G-36", record.label, report, _g36_provenance, record, session)
    guard("G-37", record.label, report, _g37_storey_chain, record, session, linear, tol_linear)
    guard(
        "G-38",
        record.label,
        report,
        _g38_dimension_agreement,
        record,
        session,
        linear,
        tol_linear,
    )
    guard("G-39", record.label, report, _g39_layer_vocabulary, record)
    guard("G-40", record.label, report, _g40_grouping, record, session)


# ---- massing value readers (shape + finiteness, shared by G-35/G-38/G-40) ---- #


def _massing_ring(value: Any) -> Optional[list[list[float]]]:
    """A world-XY ring of finite ``[x, y]`` vertices, or None when malformed.

    ``ring_of`` coerces a bad component to 0.0, which would let a typo'd vertex
    pass a geometry test as the origin. 07 G-35 wants finite numbers, so this
    reader refuses instead of repairing.
    """
    if not isinstance(value, list) or not value:
        return None
    ring: list[list[float]] = []
    for point in value:
        if not isinstance(point, list) or len(point) != 2:
            return None
        x, y = as_number(point[0]), as_number(point[1])
        if x is None or y is None or not (math.isfinite(x) and math.isfinite(y)):
            return None
        ring.append([x, y])
    return ring


def _finite_pair(value: Any) -> Optional[tuple[float, float]]:
    """``[z0, z1]`` of finite numbers, or None."""
    if not isinstance(value, list) or len(value) != 2:
        return None
    first, second = as_number(value[0]), as_number(value[1])
    if first is None or second is None:
        return None
    if not (math.isfinite(first) and math.isfinite(second)):
        return None
    return first, second


def _finite_triple(value: Any) -> Optional[tuple[float, float, float]]:
    """``[x, y, z]`` of finite numbers, or None."""
    if not isinstance(value, list) or len(value) != 3:
        return None
    numbers = [as_number(item) for item in value]
    if any(item is None or not math.isfinite(item) for item in numbers):
        return None
    return (numbers[0], numbers[1], numbers[2])  # type: ignore[return-value]


def _elements_of(doc: Any) -> list[Any]:
    elements = doc.get("elements") if isinstance(doc, dict) else None
    return elements if isinstance(elements, list) else []


def _elements_by_id(doc: Any) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for element in _elements_of(doc):
        if isinstance(element, dict) and isinstance(element.get("id"), str):
            index.setdefault(element["id"], element)
    return index


# ---- G-34 element identity ------------------------------------------------ #


def _g34_identity(record: LoadedFile, report: Report) -> None:
    """G-34. EL-/GRP- ids well formed, unique and ascending."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    problems = 0
    for key, id_re, pattern in (
        ("elements", ELEMENT_ID_RE, ELEMENT_ID_PATTERN),
        ("grouping", GROUPING_ID_RE, GROUPING_ID_PATTERN),
    ):
        entries = doc.get(key)
        if not isinstance(entries, list):
            report.fail("G-34", f"{location}::{key}", f"{key} is {entries!r}, expected an array")
            problems += 1
            continue
        problems += _scan_id_sequence(entries, key, location, report, "G-34", id_re, pattern)
    if problems == 0:
        report.ok(
            "G-34",
            location,
            f"{len(doc['elements'])} element ids and {len(doc['grouping'])} group ids, "
            "unique, well formed, ascending",
        )


# ---- G-35 element solidity ------------------------------------------------- #


def _g35_solidity(record: LoadedFile, linear: float, tol: str, report: Report) -> None:
    """G-35. Every element is a simple CCW Z-prism with an ascending z_range_cm."""
    location = record.label
    doc = record.doc
    elements = _elements_of(doc)
    if not elements:
        report.skip(
            "G-35", location, "elements[] is missing or empty; there is no solid to test"
        )
        return
    problems = 0
    for index, element in enumerate(elements):
        where = f"{location}::elements[{index}]"
        if not isinstance(element, dict):
            report.fail("G-35", where, "element is not an object")
            problems += 1
            continue
        kind = element.get("kind")
        if kind not in MASSING_ELEMENT_KINDS:
            report.fail(
                "G-35",
                f"{where}.kind",
                f"kind {kind!r} is not one of {', '.join(MASSING_ELEMENT_KINDS)} "
                "(07 section 8.1.1)",
            )
            problems += 1

        ring = _massing_ring(element.get("profile_cm"))
        declared = element.get("profile_ccw")
        if ring is None:
            report.skip(
                "G-35",
                f"{where}.profile_cm",
                "profile_cm is not a ring of >= 1 finite [x, y] vertices; G-35 cannot "
                "test simplicity or winding",
            )
        else:
            if len(ring) >= 2 and _near_point(ring[0], ring[-1], linear):
                report.fail(
                    "G-35",
                    f"{where}.profile_cm",
                    "profile_cm repeats its first vertex as the last; 07 G-35 forbids "
                    "writing a closed ring twice",
                    tol,
                )
                problems += 1
            if isinstance(declared, bool):
                winding: Any = declared
            else:
                report.fail(
                    "G-35",
                    f"{where}.profile_ccw",
                    f"profile_ccw is {declared!r}; 07 section 8.1.1 makes it a required "
                    "bool, so the declared winding is unreadable",
                )
                problems += 1
                # Nothing is left to declare; hand the checker the measured winding
                # so it does not emit a SKIP row about a 07 section 5.7 sibling flag
                # that massing.json does not have.
                winding = polygon_signed_area_cm2(ring) > 0.0
            problems += _polygon_check(
                location,
                f"elements[{index}].profile_cm",
                ring,
                winding,
                tol,
                report,
                rule="G-35",
            )

        span = element.get("z_range_cm")
        pair = _finite_pair(span)
        if pair is None:
            report.fail(
                "G-35",
                f"{where}.z_range_cm",
                f"z_range_cm is {span!r}; 07 section 8.1.1 requires two finite numbers",
            )
            problems += 1
        elif not pair[1] > pair[0]:
            report.fail(
                "G-35",
                f"{where}.z_range_cm",
                f"z_range_cm [{fmt_number(pair[0])}, {fmt_number(pair[1])}] is not strictly "
                "ascending; 07 G-35 requires z_range_cm[1] > z_range_cm[0]",
                tol,
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-35",
            location,
            f"{len(elements)} element solids: profile simple and wound as declared, "
            "z_range_cm strictly ascending, every kind in the 07 section 8.1.1 vocabulary",
            tol,
        )


def _near_point(a: Sequence[float], b: Sequence[float], tol: float) -> bool:
    return abs(a[0] - b[0]) <= tol + 1e-9 and abs(a[1] - b[1]) <= tol + 1e-9


# ---- G-36 massing provenance ------------------------------------------------ #


def _g36_provenance(record: LoadedFile, session: Session, report: Report) -> None:
    """G-36. Origins coverage, provenance, and origin_inputs resolve.

    **The "every origin is derived" clause is scoped to the value tree.**  P6 is the
    first stage to put an assumed value in a derived *massing* file --
    ``defaults.facade_wall_thickness_cm`` (09 ``D-FW-01``, ``A-025``) -- because nothing
    in ``dimensions.json`` dimensions a facade build-up.  It is recorded as ``assumed``
    with its ledger ref, exactly as P5 recorded ``components_registry.json``'s two
    defaults (``A-023`` / ``A-024``), and G-64 scopes its identical clause for those two.
    The exception is the ``defaults`` block and nothing else: every geometry leaf --
    every ``elements[]``, ``storeys[]``, ``site_pad`` and ``grouping`` value -- is still
    required to be ``derived``, so the clause cannot be stretched to cover invented
    massing.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    problems, leaves, entries = _check_origins_coverage(
        doc, record.spec, location, report, "G-36"
    )
    origins = doc.get("origins")
    if not isinstance(origins, dict):
        return  # the coverage pass already reported the shape; there is nothing else to read
    derived = 0
    excused = 0
    for entry in sorted(origins):
        value = origins[entry]
        if not isinstance(value, dict):
            continue  # the coverage pass already reported the shape
        origin = value.get("origin")
        if origin != "derived":
            if (
                entry.startswith(MASSING_ASSUMED_PREFIX)
                and origin == "assumed"
                and isinstance(value.get("origin_ref"), str)
            ):
                excused += 1  # G-10 checks that the ref is well formed and resolves
                continue
            report.fail(
                "G-36",
                f"{location}::{entry}",
                f"origin {origin!r} is not 'derived'; a massing value that is given, assumed "
                "or conflict is a defect, because dimensions.json already resolved all "
                f"three (07 section 9.6). The only exception is the documented "
                f"{MASSING_ASSUMED_PREFIX}* block, which must be "
                f"origin=assumed with an origin_ref (currently {excused} such entry/entries)",
            )
            problems += 1
            continue
        derived += 1
        derives_from = value.get("derives_from")
        if not isinstance(derives_from, list) or not derives_from:
            report.fail(
                "G-36",
                f"{location}::{entry}",
                "origin=derived requires a non-empty derives_from",
            )
            problems += 1

    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        report.skip(
            "G-36",
            location,
            "dimensions.json is absent; derives_from and origin_inputs are cross-file, so "
            "G-36 will not assume an answer for them",
        )
        return

    traced = 0
    for entry in sorted(origins):
        value = origins[entry]
        if not isinstance(value, dict) or value.get("origin") != "derived":
            continue
        for source in value.get("derives_from") or []:
            text = str(source)
            if resolve(doc, text)[0] or resolve(dimensions.doc, text)[0]:
                traced += 1
            else:
                report.fail(
                    "G-36",
                    f"{location}::{entry}",
                    f"derives_from path {text!r} resolves neither in this file nor in "
                    f"{dimensions.label}",
                )
                problems += 1

    inputs = doc.get("origin_inputs")
    checked_inputs = 0
    for item in inputs if isinstance(inputs, list) else []:
        text = str(item)
        if resolve(dimensions.doc, text)[0]:
            checked_inputs += 1
        else:
            report.fail(
                "G-36",
                f"{location}::origin_inputs",
                f"path {text!r} does not resolve in {dimensions.label}; 07 G-36 requires "
                f"every origin_inputs path there, where a derives_from path may also name "
                f"this file",
            )
            problems += 1

    if problems == 0:
        note = (
            f"{leaves} leaves, {entries} entries, exactly-one coverage; all {derived} "
            f"derived with {traced} resolving derives_from paths; {checked_inputs} "
            f"origin_inputs paths resolve in {dimensions.label}"
        )
        if excused:
            note += (
                f". The all-derived clause is scoped to the value tree: {excused} assumed "
                f"entry(ies) under the {MASSING_ASSUMED_PREFIX}* block are the documented "
                f"defaults ({MASSING_FACADE_WALL_THICKNESS_LEDGER}), not invented geometry"
            )
        report.ok("G-36", location, note)


# ---- G-37 storey chain ----------------------------------------------------- #


def _g37_storey_chain(
    record: LoadedFile, session: Session, linear: float, tol: str, report: Report
) -> None:
    """G-37. Each storey chains to its level and owns only its own elements."""
    location = record.label
    doc = record.doc
    storeys = doc.get("storeys") if isinstance(doc, dict) else None
    if not isinstance(storeys, list):
        report.skip(
            "G-37", location, "storeys[] is missing or not an array; there is no chain to test"
        )
        return
    if not storeys:
        report.skip(
            "G-37", location, "storeys[] is empty; there is no storey chain to test"
        )
        return
    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        report.skip(
            "G-37",
            location,
            "dimensions.json is absent; G-37 chains massing storeys against levels[] and "
            "will not assume an answer",
        )
        return

    levels = _levels(dimensions.doc) or []
    elements = _elements_by_id(doc)
    problems = 0
    for index, storey in enumerate(storeys):
        where = f"{location}::storeys[{index}]"
        if not isinstance(storey, dict):
            report.fail("G-37", where, "storey is not an object")
            problems += 1
            continue
        level = levels[index] if index < len(levels) else None
        if level is None:
            report.fail(
                "G-37",
                where,
                f"no levels[{index}] exists in {dimensions.label}; the storey has no level "
                "to chain to",
            )
            problems += 1
            continue

        if storey.get("index") != level.get("index"):
            report.fail(
                "G-37",
                f"{where}.index",
                f"index {storey.get('index')!r} != levels[{index}].index "
                f"{level.get('index')!r}",
                tol,
            )
            problems += 1
        if storey.get("level_ref") != level.get("id"):
            report.fail(
                "G-37",
                f"{where}.level_ref",
                f"level_ref {storey.get('level_ref')!r} is not levels[{index}].id "
                f"{level.get('id')!r}",
                tol,
            )
            problems += 1

        elevation = as_number(storey.get("elevation_cm"))
        height = as_number(storey.get("height_cm"))
        missing: list[str] = []
        if elevation is None:
            missing.append("elevation_cm")
        if height is None:
            missing.append("height_cm")
        if missing:
            report.fail(
                "G-37",
                where,
                f"{', '.join(missing)} is not a number; the storey cannot be chained",
                tol,
            )
            problems += 1
            continue
        for key in ("elevation_cm", "height_cm"):
            expected = as_number(level.get(key))
            actual = as_number(storey.get(key))
            if expected is None:
                report.skip(
                    "G-37",
                    f"{where}.{key}",
                    f"levels[{index}].{key} is missing in {dimensions.label}; G-37 will "
                    "not assume an answer",
                )
                continue
            if not close(actual, expected, linear):
                report.fail(
                    "G-37",
                    f"{where}.{key}",
                    f"{fmt_number(actual)} cm != levels[{index}].{key} "
                    f"{fmt_number(expected)} cm",
                    tol,
                )
                problems += 1

        span = _finite_pair(storey.get("z_range_cm"))
        if span is None:
            report.fail(
                "G-37",
                f"{where}.z_range_cm",
                f"z_range_cm is {storey.get('z_range_cm')!r}; 07 section 8.1.1 requires "
                "two finite numbers",
                tol,
            )
            problems += 1
        elif not (
            close(span[0], elevation, linear) and close(span[1], elevation + height, linear)
        ):
            report.fail(
                "G-37",
                f"{where}.z_range_cm",
                f"[{fmt_number(span[0])}, {fmt_number(span[1])}] != "
                f"[{fmt_number(elevation)}, {fmt_number(elevation + height)}] from this "
                "storey's own elevation_cm + height_cm",
                tol,
            )
            problems += 1

        problems += _g37_slab_ref(storey, index, elements, where, tol, report)
        for key in ("column_refs", "core_refs"):
            refs = storey.get(key)
            if not isinstance(refs, list):
                report.fail(
                    "G-37",
                    f"{where}.{key}",
                    f"{key} is {refs!r}, expected an array of element ids",
                    tol,
                )
                problems += 1
                continue
            for ident in refs:
                element = elements.get(str(ident))
                if element is None:
                    report.fail(
                        "G-37",
                        f"{where}.{key}",
                        f"id {ident!r} does not exist in elements[]",
                        tol,
                    )
                    problems += 1
                elif element.get("storey_index") != index:
                    report.fail(
                        "G-37",
                        f"{where}.{key}",
                        f"element {ident!r} has storey_index "
                        f"{element.get('storey_index')!r}, not {index}",
                        tol,
                    )
                    problems += 1

    if problems == 0:
        report.ok(
            "G-37",
            location,
            f"{len(storeys)} storeys chain to levels[]: index, level_ref, elevation_cm, "
            "height_cm and z_range_cm agree, and every referenced element belongs to its "
            "own storey",
            tol,
        )


def _g37_slab_ref(
    storey: dict,
    index: int,
    elements: dict[str, dict],
    where: str,
    tol: str,
    report: Report,
) -> int:
    problems = 0
    ident = storey.get("slab_ref")
    element = elements.get(str(ident))
    if element is None:
        report.fail(
            "G-37",
            f"{where}.slab_ref",
            f"slab_ref {ident!r} does not exist in elements[]",
            tol,
        )
        return 1
    if element.get("kind") != "slab":
        report.fail(
            "G-37",
            f"{where}.slab_ref",
            f"slab_ref names element {ident!r} of kind {element.get('kind')!r}, not 'slab'",
            tol,
        )
        problems += 1
    if element.get("storey_index") != index:
        report.fail(
            "G-37",
            f"{where}.slab_ref",
            f"element {ident!r} has storey_index {element.get('storey_index')!r}, not {index}",
            tol,
        )
        problems += 1
    return problems


# ---- G-38 element-to-dimension agreement ------------------------------------ #


def _g38_dimension_agreement(
    record: LoadedFile, session: Session, linear: float, tol: str, report: Report
) -> None:
    """G-38. Every element solid is the prism dimensions.json implies."""
    location = record.label
    doc = record.doc
    elements = _elements_of(doc)
    if not elements:
        report.skip(
            "G-38", location, "elements[] is missing or empty; nothing to reconcile"
        )
        return
    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        report.skip(
            "G-38",
            location,
            "dimensions.json is absent; G-38 reconciles every element against levels[], "
            "floor_plates[], core and roof and will not assume an answer",
        )
        return

    dims = dimensions.doc
    levels = _levels(dims) or []
    plates = [p for p in (dims.get("floor_plates") or []) if isinstance(p, dict)]
    roof = dims.get("roof") if isinstance(dims.get("roof"), dict) else {}
    building = dims.get("building") if isinstance(dims.get("building"), dict) else {}
    storey_indices = {
        storey.get("index")
        for storey in (doc.get("storeys") or [])
        if isinstance(storey, dict)
    }
    problems = 0
    reconciled = 0
    model_top: Optional[float] = None

    for index, element in enumerate(elements):
        where = f"{location}::elements[{index}]"
        if not isinstance(element, dict):
            continue
        span = _finite_pair(element.get("z_range_cm"))
        if span is not None:
            model_top = span[1] if model_top is None else max(model_top, span[1])

        storey_index = element.get("storey_index")
        if storey_index is not None and storey_index not in storey_indices:
            report.fail(
                "G-38",
                f"{where}.storey_index",
                f"storey_index {storey_index!r} is not an index in storeys[]",
                tol,
            )
            problems += 1
            continue

        kind = element.get("kind")
        if kind == "core_wall":
            reconciled += 1
            problems += _g38_core_wall(element, dims, where, linear, tol, report)
            continue
        if kind == "roof_deck":
            reconciled += 1
            problems += _g38_from_key(
                element, roof, "deck_level_cm", "deck_thickness_cm", where, linear, tol,
                report, below=True,
            )
            continue
        if kind == "parapet":
            reconciled += 1
            problems += _g38_from_key(
                element, roof, "deck_level_cm", "parapet_height_cm", where, linear, tol,
                report, below=False,
            )
            continue
        if kind == "plinth":
            continue  # 07 section 9.6 states no dimensional rule for a plinth
        if kind == "facade_wall":
            reconciled += 1
            problems += _g38_facade_wall(element, dims, where, linear, tol, report)
            continue
        if kind not in ("slab", "column"):
            continue  # G-35 reports an unknown kind

        if not is_int(storey_index):
            report.skip(
                "G-38",
                where,
                f"storey_index is {storey_index!r}, so no level elevation applies and G-38 "
                f"cannot reconcile this {kind}",
            )
            continue
        level = levels[storey_index] if 0 <= storey_index < len(levels) else None
        if level is None:
            report.skip(
                "G-38",
                where,
                f"levels[{storey_index}] does not exist in {dimensions.label}; G-38 cannot "
                f"reconcile this {kind}",
            )
            continue
        plate = plates[storey_index] if 0 <= storey_index < len(plates) else None
        elevation = as_number(level.get("elevation_cm"))
        height = as_number(level.get("height_cm"))
        thickness = as_number(plate.get("thickness_cm")) if plate is not None else None
        if elevation is None or thickness is None or (kind == "column" and height is None):
            report.skip(
                "G-38",
                where,
                f"levels[{storey_index}].elevation_cm/height_cm or "
                f"floor_plates[{storey_index}].thickness_cm is missing in "
                f"{dimensions.label}; G-38 will not assume an answer",
            )
            continue
        expected = [elevation - thickness, elevation]
        why = (
            f"levels[{storey_index}].elevation_cm - "
            f"floor_plates[{storey_index}].thickness_cm .. elevation_cm"
        )
        if kind == "column":
            expected = [elevation - thickness, elevation + float(height or 0.0)]
            why = (
                f"levels[{storey_index}].elevation_cm - slab thickness .. "
                "elevation_cm + levels[].height_cm"
            )
        reconciled += 1
        problems += _expect_z(element, expected, why, linear, where, tol, report)

    # 07 section 9.6: because a parapet tops out at deck_level + parapet_height,
    # the model's top must equal building.overall_height_cm.
    overall = as_number(building.get("overall_height_cm"))
    if overall is None:
        report.skip(
            "G-38",
            location,
            f"building.overall_height_cm is missing in {dimensions.label}; the model top "
            "cannot be compared",
        )
    elif model_top is None:
        report.skip(
            "G-38",
            location,
            "no element carries a usable z_range_cm, so the model top is unevaluable",
        )
    elif not close(model_top, overall, linear):
        report.fail(
            "G-38",
            f"{location}::elements",
            f"model top {fmt_number(model_top)} cm != building.overall_height_cm "
            f"{fmt_number(overall)} cm",
            tol,
        )
        problems += 1

    # 07 section 9.6: a level named by core.spans_level_indices has a core_wall.
    core = dims.get("core") if isinstance(dims.get("core"), dict) else {}
    spans = core.get("spans_level_indices")
    if spans is None:
        report.skip(
            "G-38",
            location,
            f"core.spans_level_indices is missing in {dimensions.label}; the core coverage "
            "cannot be tested",
        )
    else:
        covered = {
            element.get("storey_index")
            for element in elements
            if isinstance(element, dict) and element.get("kind") == "core_wall"
        }
        for value in spans:
            if value not in covered:
                report.fail(
                    "G-38",
                    f"{location}::elements",
                    f"level index {value!r} is named by core.spans_level_indices but has no "
                    "core_wall element",
                    tol,
                )
                problems += 1

    # 07 section 9.6 (P6 amendment): every (facades[i].id, levels[j].index) pair
    # has exactly one facade_wall banding that facade's run.  The second half of
    # the G-38 amendment -- "a missing wall is a FAIL, not a gap" -- because an
    # opening cut whose host_ref resolves to nothing is a silent hole.
    walls, wall_reason, wall_failures = _g38_facade_wall_coverage(
        doc, dims, location, tol, report
    )
    if walls is None:
        report.skip("G-38", location, wall_reason)
    else:
        reconciled += walls
        problems += wall_failures

    if problems == 0:
        report.ok(
            "G-38",
            location,
            f"{reconciled} element solid(s) equal the prism dimensions.json implies; model "
            f"top {fmt_number(model_top)} cm == overall_height_cm; every level named by "
            "core.spans_level_indices has a core_wall; every (facade, level) pair has "
            "exactly one facade_wall banding its run",
            tol,
        )


def _g38_facade_wall(
    element: dict, dims: Any, where: str, linear: float, tol: str, report: Report
) -> int:
    """G-38, first P6 clause: a facade_wall spans the full storey height.

    07 section 8.1.1 makes ``storey_index`` mandatory for a ``facade_wall`` (never
    ``null``, unlike a site-wide or roof element), so a null one is a defect rather
    than an unevaluable comparison.
    """
    index = element.get("storey_index")
    if not is_int(index):
        report.fail(
            "G-38",
            f"{where}.storey_index",
            f"a facade_wall carries storey_index {index!r}; 07 section 8.1.1 requires the "
            "storey it belongs to, because G-38 reconciles its z_range_cm against that "
            "level",
            tol,
        )
        return 1
    levels = _levels(dims) or []
    level = levels[index] if 0 <= index < len(levels) else None
    if level is None:
        report.skip(
            "G-38",
            where,
            f"levels[{index}] does not exist in dimensions.json; G-38 cannot reconcile this "
            "facade_wall",
        )
        return 0
    elevation = as_number(level.get("elevation_cm"))
    height = as_number(level.get("height_cm"))
    if elevation is None or height is None:
        report.skip(
            "G-38",
            where,
            f"levels[{index}].elevation_cm or levels[{index}].height_cm is missing; G-38 "
            "will not assume a facade_wall's storey volume",
        )
        return 0
    return _expect_z(
        element,
        [elevation, elevation + height],
        f"levels[{index}].elevation_cm .. elevation_cm + levels[{index}].height_cm",
        linear,
        where,
        tol,
        report,
    )


def _g38_facade_wall_coverage(
    doc: Any, dims: Any, location: str, tol: str, report: Report
) -> tuple[Optional[int], str, int]:
    """G-38, second P6 clause: exactly one wall per (facade, level) pair.

    The band is recomputed from ``dimensions.json`` -- the run's two corners, the
    run's inward side and ``massing.json``'s own assumed thickness -- so the
    element is matched to its facade by geometry rather than by a key that would
    let the file agree with itself.  Returns ``(pairs_checked, "", failures)``, or
    ``(None, reason, 0)`` for an honest SKIP when the comparison is impossible.
    """
    facades = dims.get("facades")
    if not isinstance(facades, list) or not facades:
        return None, (
            "dimensions.json declares no facades[]; the facade_wall envelope cannot be "
            "tested"
        ), 0
    levels = _levels(dims) or []
    if not levels:
        return None, "dimensions.json declares no levels[]; the facade_wall z-range cannot be tested", 0
    block = doc.get("defaults") if isinstance(doc, dict) else None
    thickness = as_number(
        block.get("facade_wall_thickness_cm") if isinstance(block, dict) else None
    )
    if thickness is None or thickness <= 0.0:
        return None, (
            f"{MASSING_FACADE_WALL_THICKNESS_LEAF} is missing or not a positive number in "
            "massing.json; the facade_wall bands cannot be recomputed"
        ), 0
    site = dims.get("site") if isinstance(dims.get("site"), dict) else {}
    kind = site.get("footprint_kind")
    outline = expand_footprint_ring(
        site.get("footprint_cm"), kind if isinstance(kind, str) else ""
    )
    if not outline:
        return None, "site.footprint_cm is unusable; the inward side of a run is undecidable", 0
    toward = (
        (min(p[0] for p in outline) + max(p[0] for p in outline)) / 2.0,
        (min(p[1] for p in outline) + max(p[1] for p in outline)) / 2.0,
    )
    elements = _elements_of(doc)
    failures = 0
    for facade in facades:
        if not isinstance(facade, dict):
            continue
        band = _facade_wall_band(facade, thickness, toward)
        if band is None:
            return None, (
                f"facade {facade.get('id')!r} has no usable start/end corner; the inward band "
                "cannot be recomputed"
            ), 0
        for level in levels:
            index = level.get("index")
            matches = [
                str(element.get("id"))
                for element in elements
                if isinstance(element, dict)
                and element.get("kind") == "facade_wall"
                and element.get("storey_index") == index
                and _ring_is_rect(element.get("profile_cm"), band)
            ]
            if len(matches) != 1:
                facade_id = facade.get("id")
                report.fail(
                    "G-38",
                    f"{location}::elements",
                    f"({facade_id!r}, level {index!r}) has {len(matches)} facade_wall element(s) "
                    f"banding {band} and spanning its length_cm; G-38 requires exactly one, so "
                    "the envelope is total in both directions"
                    + (f" (found {matches})" if matches else ""),
                    tol,
                )
                failures += 1
    return len(facades) * len(levels), "", failures


def _facade_wall_band(
    facade: dict, thickness: float, toward: tuple[float, float]
) -> Optional[tuple[float, float, float, float]]:
    """``(xmin, ymin, xmax, ymax)`` of the facade run banded inward, or None.

    "Inward" is the offset side that faces the footprint centre, so the rule does
    not depend on the order ``dimensions.json`` happens to direct the run in: the
    four runs of a rectangle are not all wound the same way round the ring.
    """
    start = facade.get("start_corner_cm")
    end = facade.get("end_corner_cm")
    if not (
        isinstance(start, list) and len(start) == 2 and isinstance(end, list) and len(end) == 2
    ):
        return None
    sx, sy = as_number(start[0]), as_number(start[1])
    ex, ey = as_number(end[0]), as_number(end[1])
    if None in (sx, sy, ex, ey):
        return None
    dx, dy = float(ex) - sx, float(ey) - sy
    length = math.hypot(dx, dy)
    if length <= 0.0:
        return None
    nx, ny = -dy / length, dx / length
    mid = ((sx + float(ex)) / 2.0, (sy + float(ey)) / 2.0)
    if math.hypot(mid[0] + nx - toward[0], mid[1] + ny - toward[1]) > math.hypot(
        mid[0] - nx - toward[0], mid[1] - ny - toward[1]
    ):
        nx, ny = -nx, -ny
    corners = [
        (sx, sy),
        (float(ex), float(ey)),
        (sx + nx * thickness, sy + ny * thickness),
        (float(ex) + nx * thickness, float(ey) + ny * thickness),
    ]
    return (
        min(p[0] for p in corners),
        min(p[1] for p in corners),
        max(p[0] for p in corners),
        max(p[1] for p in corners),
    )


def _ring_is_rect(value: Any, rect: Sequence[float], linear: float = 0.5) -> bool:
    """True when ``value`` is a ring whose bounding rectangle is ``rect``.

    The bounding rectangle is the identity here because the band is required to be
    axis-aligned: the emitted builder refuses anything else (07 section 8.1.1), and a
    rotated band cannot be compared vertex-for-vertex against an axis-aligned one
    without inventing a correspondence.
    """
    ring = _massing_ring(value)
    if ring is None or len(ring) < 3:
        return False
    actual = (
        min(p[0] for p in ring),
        min(p[1] for p in ring),
        max(p[0] for p in ring),
        max(p[1] for p in ring),
    )
    return all(close(actual[i], rect[i], linear) for i in range(4))


def _expect_z(
    element: dict,
    expected: Sequence[float],
    why: str,
    linear: float,
    where: str,
    tol: str,
    report: Report,
) -> int:
    actual = _finite_pair(element.get("z_range_cm"))
    if actual is None:
        return 0  # G-35 already reported the malformed z_range_cm
    if all(close(actual[i], expected[i], linear) for i in (0, 1)):
        return 0
    report.fail(
        "G-38",
        f"{where}.z_range_cm",
        f"[{fmt_number(actual[0])}, {fmt_number(actual[1])}] != "
        f"[{fmt_number(expected[0])}, {fmt_number(expected[1])}] from {why}",
        tol,
    )
    return 1


def _g38_from_key(
    element: dict,
    block: dict,
    base_key: str,
    extent_key: str,
    where: str,
    linear: float,
    tol: str,
    report: Report,
    below: bool,
) -> int:
    """``[base, base + extent]`` when ``below`` is False, else ``[base - extent, base]``."""
    base = as_number(block.get(base_key))
    extent = as_number(block.get(extent_key))
    if base is None or extent is None:
        report.skip(
            "G-38",
            where,
            f"dimensions.json declares no {base_key}/{extent_key}; G-38 cannot reconcile "
            "this element",
        )
        return 0
    expected = [base - extent, base] if below else [base, base + extent]
    why = (
        f"{base_key} - {extent_key} .. {base_key}"
        if below
        else f"{base_key} .. {base_key} + {extent_key}"
    )
    return _expect_z(element, expected, why, linear, where, tol, report)


def _g38_core_wall(
    element: dict, dims: Any, where: str, linear: float, tol: str, report: Report
) -> int:
    core = dims.get("core") if isinstance(dims.get("core"), dict) else None
    if core is None:
        report.skip("G-38", where, "core is missing in dimensions.json; G-38 cannot inset it")
        return 0
    kind = core.get("footprint_kind")
    outline = expand_footprint_ring(
        core.get("footprint_cm"), kind if isinstance(kind, str) else ""
    )
    wall = as_number(core.get("wall_thickness_cm"))
    if not outline or len(outline) < 3 or wall is None:
        report.skip(
            "G-38",
            where,
            "core.footprint_cm or core.wall_thickness_cm is unusable in dimensions.json; "
            "G-38 cannot compute the inset outline",
        )
        return 0
    expected = _inset_ring(outline, wall)
    actual = _massing_ring(element.get("profile_cm"))
    if expected is None or actual is None:
        report.skip(
            "G-38",
            f"{where}.profile_cm",
            "the inset outline or this profile_cm is not a usable ring; G-38 cannot "
            "compare them",
        )
        return 0
    reason = _ring_difference(actual, expected, linear)
    if reason is None:
        return 0
    report.fail(
        "G-38",
        f"{where}.profile_cm",
        f"profile_cm is not core.footprint_cm inset by {fmt_number(wall)} cm: {reason}",
        tol,
    )
    return 1


def _edge_normal(a: Sequence[float], b: Sequence[float], inward: bool) -> Optional[tuple[float, float]]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length <= 0.0:
        return None
    # The left normal of a->b is (-dy, dx); on a CCW ring it points inward.
    nx, ny = -dy / length, dx / length
    return (nx, ny) if inward else (-nx, -ny)


def _inset_ring(ring: Sequence[Sequence[float]], distance: float) -> Optional[list[list[float]]]:
    """Miter-inset a ring by ``distance`` cm toward its interior.

    Exact for the convex rings 07 section 8.1.1 allows a ``core_wall`` to be; it
    is the point-offset a builder would emit, and 07 does not license a hole list
    or an offset curve for a massing prism.
    """
    count = len(ring)
    if count < 3:
        return None
    inward = polygon_signed_area_cm2(ring) > 0.0
    out: list[list[float]] = []
    for index in range(count):
        previous, vertex, following = ring[index - 1], ring[index], ring[(index + 1) % count]
        first = _edge_normal(previous, vertex, inward)
        second = _edge_normal(vertex, following, inward)
        if first is None or second is None:
            return None
        bisector = (first[0] + second[0], first[1] + second[1])
        length = math.hypot(*bisector)
        if length < 1e-9:
            out.append([vertex[0] + first[0] * distance, vertex[1] + first[1] * distance])
            continue
        bisector = (bisector[0] / length, bisector[1] / length)
        denominator = bisector[0] * first[0] + bisector[1] * first[1]
        scale = distance / denominator if abs(denominator) > 1e-9 else distance
        out.append([vertex[0] + bisector[0] * scale, vertex[1] + bisector[1] * scale])
    return out


def _ring_difference(
    actual: Sequence[Sequence[float]], expected: Sequence[Sequence[float]], linear: float
) -> Optional[str]:
    """None when the rings agree vertex-for-vertex within ``linear``, else why."""
    if len(actual) != len(expected):
        return f"{len(actual)} vertices != {len(expected)} vertices"
    remaining = list(expected)
    worst = 0.0
    for point in actual:
        nearest = min(remaining, key=lambda q: math.dist(point, q))
        worst = max(worst, math.dist(point, nearest))
        remaining.remove(nearest)
    if worst > linear + 1e-9:
        return f"nearest vertex is {fmt_number(worst)} cm away (limit {fmt_number(linear)} cm)"
    return None


# ---- G-39 layer vocabulary -------------------------------------------------- #


def _g39_layer_vocabulary(record: LoadedFile, report: Report) -> None:
    """G-39. Layers are in 07 section 8.1.4 and fixed per kind by 07 section 8.1.2."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    elements = _elements_of(doc)
    problems = 0
    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue
        layer = element.get("layer")
        where = f"{location}::elements[{index}].layer"
        if layer not in MASSING_LAYERS:
            report.fail(
                "G-39",
                where,
                f"layer {layer!r} is not in the 07 section 8.1.4 vocabulary "
                f"({', '.join(MASSING_LAYERS)})",
            )
            problems += 1
            continue
        expected = MASSING_KIND_LAYER.get(element.get("kind"))
        if expected is None:
            continue  # G-35 reports a kind outside the vocabulary
        if layer != expected:
            report.fail(
                "G-39",
                where,
                f"layer {layer!r} != {expected!r}; 07 section 8.1.2 fixes layer for kind "
                f"{element.get('kind')!r}",
            )
            problems += 1

    site_pad = doc.get("site_pad")
    if isinstance(site_pad, dict):
        layer = site_pad.get("layer")
        if layer != MASSING_SITE_PAD_LAYER:
            report.fail(
                "G-39",
                f"{location}::site_pad.layer",
                f"layer {layer!r} != {MASSING_SITE_PAD_LAYER!r}; 07 section 8.1.1 puts the "
                "ground pad, paving and kerb on the site layer",
            )
            problems += 1

    for index, group in enumerate(doc.get("grouping") or []):
        if not isinstance(group, dict):
            continue
        layer = group.get("layer")
        if layer != MASSING_GROUPING_LAYER:
            report.fail(
                "G-39",
                f"{location}::grouping[{index}].layer",
                f"layer {layer!r} != {MASSING_GROUPING_LAYER!r}; a grouping layer holds the "
                "dummy, never the payload (07 section 8.1.1)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-39",
            location,
            f"{len(elements)} elements on their 07 section 8.1.2 layers, site_pad on "
            f"{MASSING_SITE_PAD_LAYER}, every grouping dummy on {MASSING_GROUPING_LAYER}",
        )


# ---- G-40 grouping completeness -------------------------------------------- #


def _g40_grouping(record: LoadedFile, session: Session, report: Report) -> None:
    """G-40. Exactly one group per element, and a pivot that matches the payload."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    grouping = doc.get("grouping")
    elements = doc.get("elements")
    if not isinstance(grouping, list) or not isinstance(elements, list):
        report.skip(
            "G-40", location, "grouping[] or elements[] is missing; no pivot to check"
        )
        return
    linear, tol = _own_linear_tolerance(record, session, report, skip_rule="G-40")
    if linear is None:
        return

    index = _elements_by_id(doc)
    placements: dict[str, list[str]] = {}
    problems = 0
    for position, group in enumerate(grouping):
        where = f"{location}::grouping[{position}]"
        if not isinstance(group, dict):
            report.fail("G-40", where, "group is not an object")
            problems += 1
            continue
        ids = group.get("element_ids")
        if not isinstance(ids, list) or not ids:
            report.fail(
                "G-40",
                f"{where}.element_ids",
                f"element_ids is {ids!r}; 07 section 8.1.1 requires at least one element id",
                tol,
            )
            problems += 1
            continue
        members: list[dict] = []
        for ident in ids:
            key = str(ident)
            placements.setdefault(key, []).append(str(group.get("id")))
            element = index.get(key)
            if element is None:
                report.fail(
                    "G-40",
                    f"{where}.element_ids",
                    f"id {key!r} does not exist in elements[]",
                    tol,
                )
                problems += 1
            else:
                members.append(element)

        pivot = _finite_triple(group.get("parent_pivot_cm"))
        if pivot is None:
            report.fail(
                "G-40",
                f"{where}.parent_pivot_cm",
                f"parent_pivot_cm is {group.get('parent_pivot_cm')!r}; 07 section 8.1.1 "
                "requires three finite numbers",
                tol,
            )
            problems += 1
            continue
        expected = _group_pivot(members)
        if expected is None:
            report.skip(
                "G-40",
                f"{where}.parent_pivot_cm",
                "no member carries a usable profile_cm / z_range_cm, so the group bbox is "
                "unevaluable and G-40 will not assume a pivot",
            )
            continue
        if not all(close(pivot[i], expected[i], linear) for i in range(3)):
            report.fail(
                "G-40",
                f"{where}.parent_pivot_cm",
                f"[{fmt_number(pivot[0])}, {fmt_number(pivot[1])}, {fmt_number(pivot[2])}] "
                "!= the group's bbox centre in XY and its minimum Z "
                f"[{fmt_number(expected[0])}, {fmt_number(expected[1])}, "
                f"{fmt_number(expected[2])}]",
                tol,
            )
            problems += 1

    for ident, groups in sorted(placements.items()):
        if len(groups) > 1:
            report.fail(
                "G-40",
                f"{location}::grouping",
                f"element {ident} appears in {len(groups)} groups: {', '.join(groups)}; "
                "07 G-40 says exactly one",
                tol,
            )
            problems += 1
    for element in elements:
        ident = element.get("id") if isinstance(element, dict) else None
        if isinstance(ident, str) and ident not in placements:
            report.fail(
                "G-40",
                f"{location}::grouping",
                f"element {ident} appears in no group; 07 G-40 says every element appears "
                "in exactly one",
                tol,
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-40",
            location,
            f"{len(grouping)} groups cover {len(placements)} elements exactly once; every "
            "pivot_cm equals its group bbox centre in XY and its minimum Z",
            tol,
        )


def _group_pivot(members: Sequence[dict]) -> Optional[tuple[float, float, float]]:
    """bbox centre in XY and the minimum Z over a group's elements."""
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for element in members:
        ring = _massing_ring(element.get("profile_cm"))
        span = _finite_pair(element.get("z_range_cm"))
        if ring is None or span is None:
            return None
        xs.extend(point[0] for point in ring)
        ys.extend(point[1] for point in ring)
        zs.append(span[0])
    if not xs:
        return None
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, min(zs)


# --------------------------------------------------------------------------- #
# 07 section 9.7 -- G-41..G-49, the nurbs.json invariants
# --------------------------------------------------------------------------- #

#: 07 section 9.7 -- a ``draft`` nurbs file is not evaluated, and *every* rule in
#: the section skips. Unlike massing there is no rule that the empty placeholder
#: can already satisfy: a computed stub declares empty ``sections`` / ``surfaces``
#: / ``derivatives`` arrays, and G-49's coverage rule alone already fails it, since
#: an empty array is still a leaf 07 section 5.2 asks an ``origins`` entry for.
NURBS_DRAFT_RULES: tuple[str, ...] = (
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


def check_nurbs_rules(record: LoadedFile, session: Session, report: Report) -> None:
    """07 section 9.7: every nurbs rule, guarded one at a time.

    A ``draft`` nurbs file is **not evaluated**. ``nurbs.json`` is computed from
    ``massing.json`` by ``build_nurbs.py``, never hand-authored, so the placeholder
    a fresh scaffold writes declares no lattice, no surface and no provenance:
    G-41..G-54 report SKIP with that reason instead of failing an empty tree.
    ``--allow-draft`` forces them to run, where G-49 does fail -- which is the
    point of the flag. ``--build`` still refuses the file at G-4.

    No rule in the section names a tolerance, except G-51: every other check is
    an exact count or an exact range (07 section 9.5), so its rows carry no
    tolerance label rather than borrowing ``linear_cm`` for a decision 07 does not
    allow one to soften. G-51 measures a distance, so it reads this file's own
    ``tolerances.linear_cm`` and names it in its row, as every geometry row must
    (G-33).
    """
    if _draft_skip_reason(
        record,
        NURBS_DRAFT_RULES,
        session,
        report,
        "9.7",
        "nurbs.json is computed from massing.json by scripts/build_nurbs.py and this "
        "placeholder declares no lattice and no provenance to check",
    ):
        return

    guard("G-41", record.label, report, _g41_identity, record)
    guard("G-42", record.label, report, _g42_shape, record)
    guard("G-43", record.label, report, _g43_key_fitness, record)
    guard("G-44", record.label, report, _g44_references, record)
    guard("G-45", record.label, report, _g45_cardinality, record)
    guard("G-46", record.label, report, _g46_order, record)
    guard("G-47", record.label, report, _g47_thickness, record)
    guard("G-48", record.label, report, _g48_derivative, record)
    guard("G-49", record.label, report, _g49_provenance, record, session)

    # G-50..G-56 govern only the four P4b relational kinds, so they register a row
    # only when the file declares one of them. A file built from the four lattice
    # routes is outside their scope: there is no rail, no blend and no trim for any
    # of them to have an opinion about, and a rule that reports a verdict on
    # nothing is noise in the tally. This is also what keeps the counts honest --
    # a rule that cannot be evaluated emits no row rather than a manufactured PASS.
    # Within scope, G-54 always reports SKIP with its reason, because a static file
    # cannot observe a commit.
    if _uses_p4b_kind(record.doc):
        guard("G-50", record.label, report, _g50_arity, record)
        guard("G-51", record.label, report, _g51_rail_intersection, record, session)
        guard("G-52", record.label, report, _g52_blend_edges, record)
        guard("G-53", record.label, report, _g53_trim_inputs, record)
        guard("G-54", record.label, report, _g54_surface_census, record)
        guard("G-55", record.label, report, _g55_blend_tension, record)
        guard("G-56", record.label, report, _g56_parent_pointer, record)


# ---- shared nurbs readers -------------------------------------------------- #


def _nurbs_table(doc: Any, key: str) -> Optional[list[Any]]:
    """``sections`` / ``surfaces`` / ``derivatives`` when it is an array, else None."""
    value = doc.get(key) if isinstance(doc, dict) else None
    return value if isinstance(value, list) else None


def _nurbs_rows(sections: Sequence[Any]) -> dict[str, list[Any]]:
    """``section id -> points_cm`` for the sections whose ``points_cm`` is an array."""
    rows: dict[str, list[Any]] = {}
    for entry in sections:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            continue
        points = entry.get("points_cm")
        if isinstance(points, list):
            rows.setdefault(entry["id"], points)
    return rows


def _nurbs_refs(surface: Any) -> list[tuple[str, str]]:
    """``(key, ref)`` for every section reference a surface declares, in key order.

    The P4b key names are here for the same reason the original three are: a rail
    and a trim profile are the existing ``sections[]`` primitive, so an id under
    ``rail_section_ids`` or ``trim_section_ids`` is a consumed section like any
    other. Leaving them out would make G-44 report every one of them as an
    orphan -- a section the file uses and no rule acknowledges.
    """
    if not isinstance(surface, dict):
        return []
    refs: list[tuple[str, str]] = []
    for key in (
        "section_ids",
        "u_section_ids",
        "v_section_ids",
        NURBS_RAIL_SECTION_KEY,
        NURBS_TRIM_SECTION_KEY,
    ):
        values = surface.get(key)
        if not isinstance(values, list):
            continue
        refs.extend((key, str(item)) for item in values)
    return refs


def _nurbs_lattice(surface: Any, rows: dict[str, list[Any]]) -> list[list[Any]]:
    """The resolvable section rows of a surface, in declared order."""
    seen: set[str] = set()
    out: list[list[Any]] = []
    for _key, ref in _nurbs_refs(surface):
        if ref in seen or ref not in rows:
            continue
        seen.add(ref)
        out.append(rows[ref])
    return out


# ---- G-41 identity and naming ---------------------------------------------- #


def _g41_identity(record: LoadedFile, report: Report) -> None:
    """G-41. SEC-/SUR-/DRV- ids well formed, unique and ascending; names clean.

    Rule N1 of reference 11 is part of this rule, not a separate one: a ``-`` in a
    node name is pasted into emitted MAXScript and reads as subtraction, so a name
    is rejected here rather than at build time.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    problems = 0
    for key, id_re, pattern in (
        ("sections", SECTION_ID_RE, SECTION_ID_PATTERN),
        ("surfaces", SURFACE_ID_RE, SURFACE_ID_PATTERN),
        ("derivatives", DERIVATIVE_ID_RE, DERIVATIVE_ID_PATTERN),
    ):
        entries = doc.get(key)
        if not isinstance(entries, list):
            report.fail("G-41", f"{location}::{key}", f"{key} is {entries!r}, expected an array")
            problems += 1
            continue
        problems += _scan_id_sequence(entries, key, location, report, "G-41", id_re, pattern)

    used: dict[str, str] = {}
    for key in ("sections", "surfaces", "derivatives"):
        for index, entry in enumerate(_nurbs_table(doc, key) or []):
            if not isinstance(entry, dict) or "name" not in entry:
                continue
            where = f"{location}::{key}[{index}].name"
            value = entry.get("name")
            if not isinstance(value, str) or not value:
                report.fail("G-41", where, f"name is {value!r}; 07 section 8.2 makes it a non-empty string")
                problems += 1
                continue
            if "-" in value:
                report.fail(
                    "G-41",
                    where,
                    f"name {value!r} contains '-'; a hyphen in a node name reads as "
                    "subtraction in emitted MAXScript (11 rule N1)",
                )
                problems += 1
            owner = used.get(value)
            if owner is not None:
                report.fail(
                    "G-41",
                    where,
                    f"name {value!r} is already used by {owner}; every name is unique in the file",
                )
                problems += 1
            else:
                used[value] = f"{key}[{index}]"

    if problems == 0:
        sections = _nurbs_table(doc, "sections") or []
        surfaces = _nurbs_table(doc, "surfaces") or []
        derivatives = _nurbs_table(doc, "derivatives") or []
        report.ok(
            "G-41",
            location,
            f"{len(sections)} section, {len(surfaces)} surface and {len(derivatives)} "
            "derivative ids unique, well formed, ascending; every declared name unique "
            "and hyphen-free",
        )


# ---- G-42 section shape and rectangularity --------------------------------- #


def _g42_shape(record: LoadedFile, report: Report) -> None:
    """G-42. points_cm is >= 2 triples of finite numbers, and a surface's rows match.

    The rectangularity half is per surface, not per kind: ``u_loft``/``point_grid``
    rows come from ``section_ids``, a ``uv_loft`` network from two families, and
    every one of them is a lattice the library indexes by ``(iv - 1) * nU + iu``.
    A row count that disagrees is not a rounding detail, it is a stride that lands
    on the wrong point.

    The P4b kinds are excluded from the rectangularity half on purpose: their
    section rows are independent curves, not one lattice. A ``rail_sweep`` whose
    rail has 3 points and whose cross-sections have 5 is the correct shape, so
    the test would otherwise fire on a valid file. What a rail must satisfy is
    distance, not stride -- that is G-51's job -- and a ``blend`` names no
    section at all.
    """
    location = record.label
    doc = record.doc
    sections = _nurbs_table(doc, "sections")
    if sections is None:
        report.fail("G-42", f"{location}::sections", f"sections is {doc.get('sections')!r}, expected an array")
        return
    if not sections:
        report.skip("G-42", location, "sections[] is empty; there is no row to shape or match")
        return

    problems = 0
    for index, entry in enumerate(sections):
        where = f"{location}::sections[{index}]"
        if not isinstance(entry, dict):
            report.fail("G-42", where, "section is not an object")
            problems += 1
            continue
        points = entry.get("points_cm")
        if not isinstance(points, list) or len(points) < 2:
            report.fail(
                "G-42",
                f"{where}.points_cm",
                f"points_cm is {points!r}; 07 section 8.2.1 requires at least 2 entries",
            )
            problems += 1
            continue
        for position, point in enumerate(points):
            if _finite_triple(point) is None:
                report.fail(
                    "G-42",
                    f"{where}.points_cm[{position}]",
                    f"point is {point!r}; 07 section 8.2.1 requires exactly 3 finite numbers",
                )
                problems += 1
        for position in range(1, len(points)):
            if points[position - 1] == points[position]:
                report.fail(
                    "G-42",
                    f"{where}.points_cm",
                    f"points_cm repeats point {position - 1} as point {position}; a section "
                    "row has no duplicate consecutive point",
                )
                problems += 1

    rows = _nurbs_rows(sections)
    for index, surface in enumerate(_nurbs_table(doc, "surfaces") or []):
        if not isinstance(surface, dict) or surface.get("kind") not in NURBS_LATTICE_KINDS:
            continue
        refs = _nurbs_refs(surface)
        if not refs:
            continue
        if any(ref not in rows for _key, ref in refs):
            continue  # G-44 owns a reference that does not resolve
        sizes = sorted({len(rows[ref]) for _key, ref in refs})
        if len(sizes) > 1:
            report.fail(
                "G-42",
                f"{location}::surfaces[{index}]",
                f"consumes rows of {sizes} point(s); every section one surface names must "
                "have the same point count, because a lattice is rectangular and the "
                "library strides it by (iv - 1) * nU + iu (07 G-42)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-42",
            location,
            f"{len(sections)} row(s) of >= 2 finite triples with no duplicate consecutive "
            "point; every surface consumes rows of one point count",
        )


# ---- G-43 kind fits its keys ------------------------------------------------ #


def _g43_key_fitness(record: LoadedFile, report: Report) -> None:
    """G-43. A surface carries exactly the keys its kind requires, and valid values.

    07 section 8.2.2 draws a closed table per kind, so the fit is exact in both
    directions: a missing required key and a forbidden one are the same defect seen
    from opposite sides, and ``weights`` is checked against the lattice it indexes
    because a flat array longer than ``nU * nV`` names a point that does not exist.

    The four P4b kinds sit in the same two tables, so they are fitted here too: a
    ``rail_sweep`` that carries ``edge1`` is a row here, not a shrug. Their deeper
    shape -- how many rails, which edges, how close to the rail -- belongs to
    G-50..G-53 and is deliberately not re-decided here.
    """
    location = record.label
    doc = record.doc
    surfaces = _nurbs_table(doc, "surfaces")
    if surfaces is None:
        report.fail("G-43", f"{location}::surfaces", f"surfaces is {doc.get('surfaces')!r}, expected an array")
        return
    if not surfaces:
        report.skip("G-43", location, "surfaces[] is empty; there is no kind whose keys could fit")
        return

    rows = _nurbs_rows(_nurbs_table(doc, "sections") or [])
    problems = 0
    for index, surface in enumerate(surfaces):
        where = f"{location}::surfaces[{index}]"
        if not isinstance(surface, dict):
            report.fail("G-43", where, "surface is not an object")
            problems += 1
            continue
        kind = surface.get("kind")
        if kind not in NURBS_KIND_REQUIRED:
            report.fail(
                "G-43",
                f"{where}.kind",
                f"kind {kind!r} is not one of {', '.join(NURBS_SURFACE_KINDS)} (07 section 8.2.3)",
            )
            problems += 1
            continue
        allowed = (
            {"id", "name", "kind"}
            | set(NURBS_SURFACE_COMMON_KEYS)
            | set(NURBS_KIND_REQUIRED[kind])
            | set(NURBS_KIND_OPTIONAL[kind])
        )
        for key in sorted(set(surface) - allowed):
            report.fail(
                "G-43",
                f"{where}.{key}",
                f"a {kind} carries {key!r}, which 07 section 8.2.2 does not allow for that "
                f"kind (allowed: {sorted(allowed)})",
            )
            problems += 1
        for key in NURBS_KIND_REQUIRED[kind]:
            if key not in surface:
                report.fail("G-43", f"{where}.{key}", f"a {kind} requires {key!r}")
                problems += 1

        layer = surface.get("layer")
        if layer is not None and layer not in NURBS_SURFACE_LAYERS:
            report.fail(
                "G-43",
                f"{where}.layer",
                f"layer {layer!r} is not in {', '.join(NURBS_SURFACE_LAYERS)}; a surface "
                "carries roof or facade geometry only (07 section 8.2.2)",
            )
            problems += 1
        mat_id = surface.get("mat_id")
        if mat_id is not None and (not is_int(mat_id) or mat_id < 1):
            report.fail("G-43", f"{where}.mat_id", f"mat_id {mat_id!r} is not an integer >= 1")
            problems += 1
        merge_tol = as_number(surface.get("merge_tol_cm"))
        if "merge_tol_cm" in surface and (merge_tol is None or merge_tol < 0.0):
            report.fail(
                "G-43", f"{where}.merge_tol_cm", f"merge_tol_cm {surface.get('merge_tol_cm')!r} is not >= 0"
            )
            problems += 1
        for flag in ("hide_curves", "closed_sections", "parallel"):
            if flag in surface and not isinstance(surface.get(flag), bool):
                report.fail("G-43", f"{where}.{flag}", f"{flag} is {surface.get(flag)!r}, expected a bool")
                problems += 1
        # P4b declares no range for a blend tension, so only its shape is checked
        # here; inventing a range 07 does not state would reject a legal spec.
        for key in ("tension1", "tension2"):
            if key in surface and as_number(surface.get(key)) is None:
                report.fail("G-43", f"{where}.{key}", f"{key} {surface.get(key)!r} is not a number")
                problems += 1
        for key in ("u_order", "v_order"):
            if key in surface and not is_int(surface.get(key)):
                report.fail("G-43", f"{where}.{key}", f"{key} {surface.get(key)!r} is not an integer")
                problems += 1

        weights = surface.get("weights")
        if weights is not None:
            if not isinstance(weights, list) or any(as_number(item) is None for item in weights):
                report.fail("G-43", f"{where}.weights", f"weights {weights!r} is not a flat array of numbers")
                problems += 1
            else:
                lattice = sum(len(row) for row in _nurbs_lattice(surface, rows))
                if lattice and len(weights) > lattice:
                    report.fail(
                        "G-43",
                        f"{where}.weights",
                        f"weights has {len(weights)} entries for a lattice of {lattice}; weights "
                        "is one flat row-major array (07 section 8.2.2)",
                    )
                    problems += 1

        approximation = surface.get("approximation")
        if approximation is None:
            continue
        if not isinstance(approximation, dict):
            report.fail("G-43", f"{where}.approximation", f"approximation is {approximation!r}, expected an object")
            problems += 1
            continue
        for key in sorted(set(approximation) - set(NURBS_APPROX_KEYS)):
            report.fail(
                "G-43",
                f"{where}.approximation.{key}",
                f"approximation carries {key!r}, which 07 section 8.2.4 does not define "
                f"(defined: {list(NURBS_APPROX_KEYS)})",
            )
            problems += 1
        for key in ("view_steps_u", "view_steps_v"):
            steps = approximation.get(key)
            if key in approximation and (not is_int(steps) or steps < 1):
                report.fail(
                    "G-43",
                    f"{where}.approximation.{key}",
                    f"{key} {steps!r} is not an integer >= 1",
                )
                problems += 1
        for key in ("render_edge_pct", "render_angle_deg", "merge_tol_cm"):
            if key not in approximation:
                continue
            value = as_number(approximation.get(key))
            if value is None or (key == "merge_tol_cm" and value < 0.0):
                report.fail(
                    "G-43",
                    f"{where}.approximation.{key}",
                    f"{key} {approximation.get(key)!r} is outside its 07 section 8.2.4 range",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-43",
            location,
            f"{len(surfaces)} surface(s): every key fits its 07 section 8.2.2 kind, layers in "
            f"{', '.join(NURBS_SURFACE_LAYERS)}, mat_id >= 1, merge_tol_cm >= 0, "
            "approximation within section 8.2.4",
        )


# ---- G-44 references resolve, nothing is orphaned -------------------------- #


def _g44_references(record: LoadedFile, report: Report) -> None:
    """G-44. Every id a surface or derivative names resolves, and nothing is spare.

    The orphan half is the one that catches an edited file: dropping one entry from
    ``section_ids`` leaves the section itself perfectly well formed and no other
    rule in the file mentions it again.

    The P4b surface-to-surface refs resolve here for the same reason the rail and
    profile refs do: ``a blend``'s ``parent1_ref``/``parent2_ref`` and a ``trim``'s
    ``surface_ref`` are ids this file must contain, so "resolves somewhere in this
    file" is this rule's claim. G-52 adds the stricter one -- a blend parent must
    be declared *earlier*, because the builder emits it as a sub-object index that
    only exists once the earlier append has happened.
    """
    location = record.label
    doc = record.doc
    sections = _nurbs_table(doc, "sections")
    surfaces = _nurbs_table(doc, "surfaces")
    if sections is None or surfaces is None:
        report.fail(
            "G-44",
            location,
            f"sections is {doc.get('sections')!r} and surfaces is {doc.get('surfaces')!r}; "
            "both must be arrays for a reference to resolve",
        )
        return

    section_ids = {
        entry["id"] for entry in sections if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    surface_ids = {
        entry["id"] for entry in surfaces if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }

    problems = 0
    consumed: set[str] = set()
    for index, surface in enumerate(surfaces):
        for key, ref in _nurbs_refs(surface):
            if ref in section_ids:
                consumed.add(ref)
            else:
                report.fail(
                    "G-44",
                    f"{location}::surfaces[{index}].{key}",
                    f"names {ref!r}, which is not a sections[] id in this file",
                )
                problems += 1
    for index, derivative in enumerate(_nurbs_table(doc, "derivatives") or []):
        if not isinstance(derivative, dict):
            continue
        ref = derivative.get("surface_ref")
        if str(ref) not in surface_ids:
            report.fail(
                "G-44",
                f"{location}::derivatives[{index}].surface_ref",
                f"surface_ref {ref!r} is not a surfaces[] id in this file",
            )
            problems += 1
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            continue
        for key in ("parent1_ref", "parent2_ref", "surface_ref"):
            if key not in surface:
                continue
            ref = surface.get(key)
            if str(ref) not in surface_ids:
                report.fail(
                    "G-44",
                    f"{location}::surfaces[{index}].{key}",
                    f"{key} {ref!r} is not a surfaces[] id in this file",
                )
                problems += 1
    for index, entry in enumerate(sections):
        ident = entry.get("id") if isinstance(entry, dict) else None
        if isinstance(ident, str) and ident not in consumed:
            report.fail(
                "G-44",
                f"{location}::sections[{index}]",
                f"{ident} is consumed by no surface; an unused section is a defect, not a "
                "spare (07 G-44)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-44",
            location,
            f"{len(consumed)} of {len(section_ids)} section(s) consumed and every "
            "section/surface reference resolves within this file",
        )


# ---- G-45 kind-specific cardinality ---------------------------------------- #


def _g45_cardinality(record: LoadedFile, report: Report) -> None:
    """G-45. Each kind's minimum, with counts compared exactly (07 section 9.5)."""
    location = record.label
    doc = record.doc
    surfaces = _nurbs_table(doc, "surfaces")
    if surfaces is None:
        report.fail("G-45", f"{location}::surfaces", f"surfaces is {doc.get('surfaces')!r}, expected an array")
        return
    if not surfaces:
        report.skip("G-45", location, "surfaces[] is empty; no kind has a cardinality to test")
        return

    rows = _nurbs_rows(_nurbs_table(doc, "sections") or [])
    problems = 0
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            continue
        kind = surface.get("kind")
        where = f"{location}::surfaces[{index}]"
        if kind == "u_loft":
            refs = [ref for key, ref in _nurbs_refs(surface) if key == "section_ids"]
            if len(refs) < 2:
                report.fail("G-45", where, f"a u_loft names {len(refs)} section(s); 07 G-45 requires >= 2")
                problems += 1
        elif kind == "uv_loft":
            u_count = sum(1 for key, _ref in _nurbs_refs(surface) if key == "u_section_ids")
            v_count = sum(1 for key, _ref in _nurbs_refs(surface) if key == "v_section_ids")
            if u_count < 1 or v_count < 1:
                report.fail(
                    "G-45",
                    where,
                    f"a uv_loft names {u_count} U and {v_count} V section(s); each family needs "
                    ">= 1",
                )
                problems += 1
            elif u_count == 1 and v_count == 1:
                report.fail(
                    "G-45",
                    where,
                    "a uv_loft names one curve in each family; a Gordon network needs 1 and n, "
                    "not 1 and 1 (07 G-45)",
                )
                problems += 1
        elif kind in ("point_grid", "cv_grid"):
            refs = [ref for key, ref in _nurbs_refs(surface) if key == "section_ids"]
            if len(refs) < 2:
                report.fail(
                    "G-45",
                    where,
                    f"a {kind} names {len(refs)} row(s); a lattice needs >= 2 (07 G-45)",
                )
                problems += 1
            for ref in refs:
                points = rows.get(ref)
                if points is not None and len(points) < 2:
                    report.fail(
                        "G-45",
                        where,
                        f"{kind} row {ref} has {len(points)} point(s); a lattice row needs >= 2",
                    )
                    problems += 1

    if problems == 0:
        report.ok(
            "G-45",
            location,
            f"{len(surfaces)} surface(s) satisfy their kind's 07 G-45 cardinality, counts "
            "compared exactly",
        )


# ---- G-46 order is meaningful, not clamped away --------------------------- #


def _g46_order(record: LoadedFile, report: Report) -> None:
    """G-46. An order is a degree choice, so it must survive the library's ``amin``.

    Only ``cv_grid`` may declare an order (07 section 8.2.2), so only ``cv_grid`` is
    evaluated here: a forbidden key on another kind is already G-43's row, and the
    count an order applies to is only defined for a lattice.
    """
    location = record.label
    doc = record.doc
    surfaces = _nurbs_table(doc, "surfaces")
    if surfaces is None:
        report.fail("G-46", f"{location}::surfaces", f"surfaces is {doc.get('surfaces')!r}, expected an array")
        return
    grids = [s for s in surfaces if isinstance(s, dict) and s.get("kind") == "cv_grid"]
    if not grids:
        report.skip("G-46", location, "no cv_grid surface declares an order; 07 G-46 has nothing to compare")
        return

    rows = _nurbs_rows(_nurbs_table(doc, "sections") or [])
    problems = 0
    checked = 0
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict) or surface.get("kind") != "cv_grid":
            continue
        where = f"{location}::surfaces[{index}]"
        lattice = _nurbs_lattice(surface, rows)
        if not lattice:
            continue
        columns = min(len(row) for row in lattice)
        for key, limit in (("u_order", columns), ("v_order", len(lattice))):
            if key not in surface:
                continue
            checked += 1
            value = surface.get(key)
            what = "points per row" if key == "u_order" else "rows"
            if not is_int(value) or not NURBS_MIN_ORDER <= value <= NURBS_MAX_ORDER:
                report.fail(
                    "G-46",
                    f"{where}.{key}",
                    f"{key} {value!r} is not an integer in {NURBS_MIN_ORDER}..{NURBS_MAX_ORDER}",
                )
                problems += 1
            elif value > limit:
                report.fail(
                    "G-46",
                    f"{where}.{key}",
                    f"{key} {value} exceeds the {limit} it applies to ({what}); "
                    "makeCVSurfaceGrid clamps with amin, so the build would differ from "
                    "the spec (07 G-46)",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-46",
            location,
            f"{checked} declared order(s) on {len(grids)} cv_grid surface(s): integer in "
            f"{NURBS_MIN_ORDER}..{NURBS_MAX_ORDER} and no larger than the count it applies to",
        )


# ---- G-47 thickness is meaningful ----------------------------------------- #


def _g47_thickness(record: LoadedFile, report: Report) -> None:
    """G-47. A shell thick enough for the library to actually build one.

    ``createULoftShell`` tests ``abs thickness > 0.001`` and omits the offset surface
    otherwise *without reporting it*, so a thinner value is not a rounding detail: it
    is a spec that builds to something other than what it says.
    """
    location = record.label
    doc = record.doc
    problems = 0
    shells = 0
    for index, surface in enumerate(_nurbs_table(doc, "surfaces") or []):
        if not isinstance(surface, dict) or "thickness_cm" not in surface:
            continue
        shells += 1
        value = as_number(surface.get("thickness_cm"))
        if value is None:
            report.fail(
                "G-47",
                f"{location}::surfaces[{index}].thickness_cm",
                f"thickness_cm {surface.get('thickness_cm')!r} is not a number",
            )
            problems += 1
        elif surface.get("kind") == "u_loft" and abs(value) < NURBS_MIN_SHELL_THICKNESS_CM:
            report.fail(
                "G-47",
                f"{location}::surfaces[{index}].thickness_cm",
                f"|thickness_cm| {abs(value):g} cm is under {NURBS_MIN_SHELL_THICKNESS_CM}; "
                "createULoftShell omits the offset surface below that, so the shell would "
                "silently not exist (07 G-47)",
            )
            problems += 1
    members = 0
    for index, derivative in enumerate(_nurbs_table(doc, "derivatives") or []):
        if not isinstance(derivative, dict) or "thickness_cm" not in derivative:
            continue
        members += 1
        value = as_number(derivative.get("thickness_cm"))
        if value is None or value < 0.0:
            report.fail(
                "G-47",
                f"{location}::derivatives[{index}].thickness_cm",
                f"thickness_cm {derivative.get('thickness_cm')!r} is not a number >= 0",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-47",
            location,
            f"{shells} shell thickness(es) at or above |{NURBS_MIN_SHELL_THICKNESS_CM}| cm and "
            f"{members} derivative member thickness(es) >= 0",
        )


# ---- G-48 derivative fitness ----------------------------------------------- #


def _g48_derivative(record: LoadedFile, report: Report) -> None:
    """G-48. A derivative declares what its kind can build and nothing more.

    ``sub_steps`` and ``thickness_cm`` are ``space_frame`` only (07 section 8.2.5);
    on a ``quad_panels`` entry they are keys the builder has no argument to pass
    them to, so they are defects rather than ignored extras.
    """
    location = record.label
    doc = record.doc
    derivatives = _nurbs_table(doc, "derivatives")
    if derivatives is None:
        report.fail(
            "G-48",
            f"{location}::derivatives",
            f"derivatives is {doc.get('derivatives')!r}, expected an array",
        )
        return
    if not derivatives:
        report.skip("G-48", location, "derivatives[] is empty; there is no derivative to test")
        return

    problems = 0
    for index, derivative in enumerate(derivatives):
        where = f"{location}::derivatives[{index}]"
        if not isinstance(derivative, dict):
            report.fail("G-48", where, "derivative is not an object")
            problems += 1
            continue
        kind = derivative.get("kind")
        if kind not in NURBS_DERIVATIVE_KINDS:
            report.fail(
                "G-48",
                f"{where}.kind",
                f"kind {kind!r} is not one of {', '.join(NURBS_DERIVATIVE_KINDS)} (07 section 8.2.5)",
            )
            problems += 1
            continue
        for key in ("divisions_u", "divisions_v"):
            value = derivative.get(key)
            if not is_int(value) or value < 1:
                report.fail(
                    "G-48",
                    f"{where}.{key}",
                    f"{key} {value!r} is not an integer >= 1; a count is compared exactly "
                    "(07 section 9.5)",
                )
                problems += 1
        for key in ("sub_steps", "thickness_cm"):
            if kind == "space_frame":
                if key not in derivative:
                    continue
                value = derivative.get(key)
                ok = is_int(value) and value >= 1 if key == "sub_steps" else as_number(value) is not None
                if not ok:
                    report.fail(
                        "G-48",
                        f"{where}.{key}",
                        f"space_frame {key} {value!r} is not a {'integer >= 1' if key == 'sub_steps' else 'number'}",
                    )
                    problems += 1
            elif key in derivative:
                report.fail(
                    "G-48",
                    f"{where}.{key}",
                    f"a {kind} carries {key}; 07 section 8.2.5 makes that key space_frame only",
                )
                problems += 1
        layer = derivative.get("layer")
        if layer is not None and layer not in NURBS_DERIVATIVE_LAYERS:
            report.fail(
                "G-48",
                f"{where}.layer",
                f"layer {layer!r} is not in {', '.join(NURBS_DERIVATIVE_LAYERS)} (07 section 8.2.5)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-48",
            location,
            f"{len(derivatives)} derivative(s): kinds in "
            f"{', '.join(NURBS_DERIVATIVE_KINDS)}, divisions integer >= 1, and the "
            "space_frame-only keys present only on space_frame",
        )


# ---- G-49 nurbs provenance -------------------------------------------------- #


def _g49_provenance(record: LoadedFile, session: Session, report: Report) -> None:
    """G-49. Coverage, all-derived provenance, and cross-file resolution.

    The resolution half differs from G-36 on purpose and must not be copied from it:
    ``nurbs.json`` is computed *from* ``massing.json``, so a ``derives_from`` path or
    an ``origin_inputs`` entry may name ``dimensions.json`` **or** ``massing.json``.
    G-36 resolves in ``dimensions.json`` only, and the worked example is correct on
    both counts -- it names ``storeys[1].z_range_cm`` and ``elements[8].z_range_cm``,
    which exist only in ``massing.json``.

    Both hosts must be present before an unresolved path is called a defect: with one
    absent the answer is unknowable, not wrong, and 07 section 9.6's line applies --
    a check that cannot be evaluated reports SKIP with its reason.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    problems, leaves, entries = _check_origins_coverage(doc, record.spec, location, report, "G-49")
    origins = doc.get("origins")
    if not isinstance(origins, dict):
        return  # the coverage pass already reported the shape; there is nothing else to read

    derived = 0
    for entry in sorted(origins):
        value = origins[entry]
        if not isinstance(value, dict):
            continue  # the coverage pass already reported the shape
        if value.get("origin") != "derived":
            report.fail(
                "G-49",
                f"{location}::{entry}",
                f"origin {value.get('origin')!r} is not 'derived'; a nurbs value that is "
                "given, assumed or conflict is a defect, because dimensions.json and "
                "massing.json already resolved all three (07 section 9.7)",
            )
            problems += 1
            continue
        derived += 1
        derives_from = value.get("derives_from")
        if not isinstance(derives_from, list) or not derives_from:
            report.fail(
                "G-49", f"{location}::{entry}", "origin=derived requires a non-empty derives_from"
            )
            problems += 1

    hosts: list[tuple[str, Any]] = [
        (item.label, item.doc) for item in (session.dimensions, session.massing) if item is not None
    ]
    missing = [
        name
        for name, item in (("dimensions.json", session.dimensions), ("massing.json", session.massing))
        if item is None
    ]
    if not hosts:
        report.skip(
            "G-49",
            location,
            "coverage and all-derived provenance hold "
            f"({leaves} leaves, {entries} entries, {derived} derived), but derives_from and "
            "origin_inputs are cross-file and neither dimensions.json nor massing.json is "
            "present, so G-49 will not assume an answer for them",
        )
        return

    traced = 0
    for entry in sorted(origins):
        value = origins[entry]
        if not isinstance(value, dict) or value.get("origin") != "derived":
            continue
        for source in value.get("derives_from") or []:
            text = str(source)
            if resolve(doc, text)[0] or any(resolve(body, text)[0] for _label, body in hosts):
                traced += 1
            elif not missing:
                report.fail(
                    "G-49",
                    f"{location}::{entry}",
                    f"derives_from path {text!r} resolves in neither this file, "
                    f"dimensions.json nor massing.json",
                )
                problems += 1

    inputs = doc.get("origin_inputs")
    checked_inputs = 0
    for item in inputs if isinstance(inputs, list) else []:
        text = str(item)
        if any(resolve(body, text)[0] for _label, body in hosts):
            checked_inputs += 1
        elif not missing:
            report.fail(
                "G-49",
                f"{location}::origin_inputs",
                f"path {text!r} resolves in neither dimensions.json nor massing.json; "
                "07 G-49 allows both, which is what a file computed from massing.json needs",
            )
            problems += 1

    if problems == 0 and missing:
        report.skip(
            "G-49",
            location,
            f"coverage and all-derived provenance hold ({leaves} leaves, {entries} entries, "
            f"{derived} derived; {traced} derives_from and {checked_inputs} origin_inputs paths "
            f"resolve), but {', '.join(missing)} is absent, so a path that resolves nowhere "
            "here could not be separated from one that resolves in the file that is missing. "
            "A check that cannot be evaluated reports SKIP with its reason, never a silent PASS.",
        )
    elif problems == 0:
        report.ok(
            "G-49",
            location,
            f"{leaves} leaves, {entries} entries, exactly-one coverage; all {derived} derived "
            f"with {traced} resolving derives_from paths; {checked_inputs} origin_inputs paths "
            "resolve in dimensions.json or massing.json",
        )


# --------------------------------------------------------------------------- #
# 07 section 9.7 -- G-50..G-54, the P4b relational kinds
#
# rail_sweep, two_rail_sweep, blend and trim are the kinds that depend on another
# object rather than only on their own rows, which is what makes them lossy: an
# invalid dependent surface is SILENTLY DROPPED at commit. CHECKPOINT section
# "Rail sweeps, blends and trims" records the executed evidence -- a sweep with no
# rail set committed to numObjects=7 with no NURBSSurface at all, no error and no
# warning, while the same sweep with rail: set committed to numObjects=14 with
# the surface at index 14. G-51 is the pre-flight for exactly that drop.
# --------------------------------------------------------------------------- #


def _uses_p4b_kind(doc: Any) -> bool:
    """True when at least one surface declares one of the four P4b kinds."""
    for surface in _nurbs_table(doc, "surfaces") or []:
        if isinstance(surface, dict) and surface.get("kind") in NURBS_P4B_KINDS:
            return True
    return False


def _p4b_surfaces(doc: Any, kind: str) -> list[tuple[int, dict]]:
    """``(index, surface)`` for every surface of one P4b kind."""
    out: list[tuple[int, dict]] = []
    for index, surface in enumerate(_nurbs_table(doc, "surfaces") or []):
        if isinstance(surface, dict) and surface.get("kind") == kind:
            out.append((index, surface))
    return out


def _point_segment_distance(
    point: Sequence[float], a: Sequence[float], b: Sequence[float]
) -> float:
    """3D distance from ``point`` to the segment ``a``-``b``, endpoints included.

    The projection is clamped to the segment, so a point beyond an endpoint
    measures to that endpoint rather than to the infinite line. This is the
    building block G-51 needs and the reason it cannot be a point-to-vertex test:
    a rail is a polyline, and the closest point of a polyline to a cross-section
    is routinely in the interior of a segment, where a vertex-only test reports a
    distance larger than the real one and fires a FAIL on a correct spec.
    """
    px, py, pz = (as_number(v) or 0.0 for v in point[:3])
    ax, ay, az = (as_number(v) or 0.0 for v in a[:3])
    bx, by, bz = (as_number(v) or 0.0 for v in b[:3])
    dx, dy, dz = bx - ax, by - ay, bz - az
    length_sq = dx * dx + dy * dy + dz * dz
    if length_sq <= 0.0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2 + (pz - az) ** 2)
    t = ((px - ax) * dx + (py - ay) * dy + (pz - az) * dz) / length_sq
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return math.sqrt((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2 + (pz - (az + t * dz)) ** 2)


def _segments_distance(
    a1: Sequence[float],
    a2: Sequence[float],
    b1: Sequence[float],
    b2: Sequence[float],
) -> float:
    """Exact minimum distance between two 3D segments.

    The naive "minimum of the four endpoint-to-segment distances" is **wrong**, and
    wrong in exactly the case G-51 is about: when two segments cross, the closest
    pair is interior to *both* and that formula reports the distance to the nearest
    pair of endpoints instead of 0. It was caught here by a fixture whose
    cross-sections genuinely cross their rail -- a false FAIL, on a correct spec.

    ``f(t, s) = |a1 + t*d1 - b1 - s*d2|^2`` is convex on the unit square, so its
    minimum is either the interior critical point or on the boundary. Both are
    evaluated: the four boundary edges are the endpoint-to-segment distances, and
    the interior point comes from solving the two normal equations. When the
    segments are parallel the interior solution is degenerate and the boundary
    candidates already attain the minimum, so the determinant test skips it.
    """
    a1v = [as_number(v) or 0.0 for v in a1[:3]]
    a2v = [as_number(v) or 0.0 for v in a2[:3]]
    b1v = [as_number(v) or 0.0 for v in b1[:3]]
    b2v = [as_number(v) or 0.0 for v in b2[:3]]
    u = [a2v[i] - a1v[i] for i in range(3)]  # d1
    v = [b2v[i] - b1v[i] for i in range(3)]  # d2
    r = [a1v[i] - b1v[i] for i in range(3)]

    best = min(
        _point_segment_distance(a1, b1, b2),
        _point_segment_distance(a2, b1, b2),
        _point_segment_distance(b1, a1, a2),
        _point_segment_distance(b2, a1, a2),
    )

    aa = sum(c * c for c in u)
    bb = sum(u[i] * v[i] for i in range(3))
    cc = sum(c * c for c in v)
    if aa <= 0.0 or cc <= 0.0:
        return best  # a degenerate "segment" is a point; the boundary already covers it
    pp = sum(u[i] * r[i] for i in range(3))
    qq = sum(v[i] * r[i] for i in range(3))
    det = bb * bb - aa * cc
    if det == 0.0:
        return best  # parallel: a boundary pair already attains the minimum
    t = (pp * cc + bb * qq) / det
    s = (bb * pp - aa * qq) / det
    if 0.0 <= t <= 1.0 and 0.0 <= s <= 1.0:
        gap = math.sqrt(
            sum((r[i] + t * u[i] - s * v[i]) ** 2 for i in range(3))
        )
        if gap < best:
            best = gap
    return best


def _polylines_distance(
    left: Sequence[Sequence[float]], right: Sequence[Sequence[float]]
) -> Optional[float]:
    """Minimum distance between two open polylines of >= 2 points, else None.

    Both operands are consecutive runs of points, so neither is closed: the
    distance is over the ``n - 1`` segments each declares. A one-point operand has
    no segment and yields None rather than a made-up number.
    """
    if len(left) < 2 or len(right) < 2:
        return None
    best: Optional[float] = None
    for i in range(len(left) - 1):
        for j in range(len(right) - 1):
            gap = _segments_distance(left[i], left[i + 1], right[j], right[j + 1])
            if best is None or gap < best:
                best = gap
    return best


def _well_formed_row(points: Any) -> bool:
    """Every entry of a section row is a finite triple (G-42 owns the failure)."""
    return isinstance(points, list) and len(points) >= 2 and all(
        _finite_triple(point) is not None for point in points
    )


def _referenced_rows(
    surface: Any, key: str, rows: dict[str, list[Any]]
) -> tuple[list[str], list[str], Optional[str]]:
    """``(refs, resolved, blocker)`` for one reference key of one surface.

    ``blocker`` names the first id that is missing or malformed, so the caller can
    say *which* reference it declined to evaluate and leave the diagnosis to the
    rule that owns it: G-44 owns an id that does not resolve, G-42 owns a row that
    is not a row. Guessing at either here would turn one defect into two rows and
    report a distance for geometry that does not exist.
    """
    values = surface.get(key) if isinstance(surface, dict) else None
    if not isinstance(values, list):
        return [], [], f"{key} is {values!r}, expected an array"
    refs = [str(item) for item in values]
    resolved: list[str] = []
    for ref in refs:
        points = rows.get(ref)
        if points is None:
            return refs, [], f"{key} names {ref!r}, which is not a sections[] id in this file"
        if not _well_formed_row(points):
            return refs, [], f"{key} names {ref!r}, whose points_cm is not >= 2 finite triples"
        resolved.append(ref)
    return refs, resolved, None


# ---- G-50 P4b kind arity ---------------------------------------------------- #


def _g50_arity(record: LoadedFile, report: Report) -> None:
    """G-50. Exactly the references each P4b kind needs, and no fewer.

    The counts are exact, not minima, because the counts are the kind: one rail is
    a sweep along a rail, two is a sweep between rails, and the library picks the
    constructor from that count, so a ``two_rail_sweep`` carrying one rail is not a
    short sweep but a request the builder cannot answer.
    """
    location = record.label
    doc = record.doc
    problems = 0
    sweeps = checked_rails = checked_sections = 0
    for kind, want in NURBS_RAIL_COUNTS.items():
        for index, surface in _p4b_surfaces(doc, kind):
            where = f"{location}::surfaces[{index}]"
            sweeps += 1
            refs = surface.get(NURBS_RAIL_SECTION_KEY)
            if not isinstance(refs, list):
                report.fail(
                    "G-50",
                    f"{where}.{NURBS_RAIL_SECTION_KEY}",
                    f"{NURBS_RAIL_SECTION_KEY} is {refs!r}, expected an array of exactly {want} "
                    f"rail(s); a {kind} takes {want} (07 section 9.7 G-50)",
                )
                problems += 1
            else:
                checked_rails += len(refs)
                if len(refs) != want:
                    report.fail(
                        "G-50",
                        f"{where}.{NURBS_RAIL_SECTION_KEY}",
                        f"a {kind} names {len(refs)} rail(s) {refs}; it takes exactly {want}, and "
                        "the count selects the constructor that builds it (07 section 9.7 G-50)",
                    )
                    problems += 1
            sections = surface.get("section_ids")
            if not isinstance(sections, list) or len(sections) < NURBS_MIN_SWEEP_SECTIONS:
                report.fail(
                    "G-50",
                    f"{where}.section_ids",
                    f"a {kind} names {len(sections) if isinstance(sections, list) else 0} "
                    f"cross-section(s); the P4b key table requires >= {NURBS_MIN_SWEEP_SECTIONS} "
                    "to sweep between (07 section 9.7 G-50)",
                )
                problems += 1
            else:
                checked_sections += len(sections)

    blends = 0
    for index, surface in _p4b_surfaces(doc, "blend"):
        where = f"{location}::surfaces[{index}]"
        blends += 1
        for key in ("parent1_ref", "parent2_ref"):
            if key not in surface:
                continue  # G-43 already reported the key as absent, by name
            value = surface.get(key)
            if not isinstance(value, str) or not value:
                report.fail(
                    "G-50",
                    f"{where}.{key}",
                    f"{key} is {value!r}; a blend needs both parents named, and an empty or "
                    "non-string ref names no surface (07 section 9.7 G-50)",
                )
                problems += 1
        for key in ("edge1", "edge2"):
            if key not in surface:
                continue  # G-43 owns absence; G-52 owns the value
            if surface.get(key) is None:
                report.fail(
                    "G-50",
                    f"{where}.{key}",
                    f"{key} is None; a blend needs both edges, one on each parent "
                    "(07 section 9.7 G-50)",
                )
                problems += 1

    trims = 0
    for index, surface in _p4b_surfaces(doc, "trim"):
        where = f"{location}::surfaces[{index}]"
        trims += 1
        if "surface_ref" in surface:
            value = surface.get("surface_ref")
            if not isinstance(value, str) or not value:
                report.fail(
                    "G-50",
                    f"{where}.surface_ref",
                    f"surface_ref is {value!r}; a trim projects a profile onto a surface and "
                    "names none (07 section 9.7 G-50)",
                )
                problems += 1
        profiles = surface.get(NURBS_TRIM_SECTION_KEY)
        if not isinstance(profiles, list) or not profiles:
            report.fail(
                "G-50",
                f"{where}.{NURBS_TRIM_SECTION_KEY}",
                f"{NURBS_TRIM_SECTION_KEY} is {profiles!r}; a trim needs >= 1 closed profile to "
                "project, and none means there is nothing to project (07 section 9.7 G-50)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-50",
            location,
            f"{sweeps} sweep(s) with exactly {NURBS_RAIL_COUNTS['rail_sweep']} and "
            f"{NURBS_RAIL_COUNTS['two_rail_sweep']} rail(s) respectively and >= "
            f"{NURBS_MIN_SWEEP_SECTIONS} cross-sections ({checked_rails} rail ref(s), "
            f"{checked_sections} section ref(s)), {blends} blend(s) with both parents and both "
            f"edges, {trims} trim(s) with a surface and >= 1 profile; counts compared exactly",
        )


# ---- G-51 a sweep's cross-sections reach its rails --------------------------- #


def _g51_rail_intersection(record: LoadedFile, session: Session, report: Report) -> None:
    """G-51. Every cross-section of a sweep comes within ``linear_cm`` of EVERY rail.

    This is the pre-flight for the silent drop. An invalid dependent surface is
    discarded at commit with no error and no warning: the executed transcript in
    CHECKPOINT committed a sweep with no rail set to ``numObjects=7`` with no
    ``NURBSSurface`` in the set at all, while the same sweep with ``rail:`` set
    committed to ``numObjects=14`` with the surface present. A spec whose sections
    never reach their rail therefore ships geometry that quietly lost its rail and
    costs nothing to report.

    The distance is point-to-**segment** over the whole rail polyline and the whole
    section polyline, not point-to-vertex: the closest point of a polyline is
    routinely interior to a segment, so a vertex-only test overstates the gap and
    would FAIL a correct spec.

    **EVERY rail, not the closest one.** This used to take the minimum over a
    sweep's rails and compare that, while ``build_nurbs.py`` compared each
    cross-section against each rail separately -- so a cross-section that met one
    rail of a ``two_rail_sweep`` and missed the other passed lint here and failed
    the build, which is the one outcome a pre-flight cannot have. The rule's own
    text ("must intersect its rail(s)") and the builder's stricter reading are the
    ones kept: a sweep needs every cross-section to reach **every** rail, because a
    ``two_rail_sweep``'s cross-section spans between its two rails and a section
    that never reaches one of them is half the sweep. The change is deliberately in
    this direction -- the linter now FAILs strictly more than it did, never less.

    The tolerance is this file's own ``tolerances.linear_cm`` (07 section 8.1), not
    a number baked in here, and the row names it as every geometry row must
    (G-33).
    """
    location = record.label
    doc = record.doc
    rows = _nurbs_rows(_nurbs_table(doc, "sections") or [])
    sweeps = _p4b_surfaces(doc, "rail_sweep") + _p4b_surfaces(doc, "two_rail_sweep")
    if not sweeps:
        report.skip(
            "G-51",
            location,
            "no rail_sweep or two_rail_sweep surface; there is no cross-section whose reach "
            "to a rail could be measured",
        )
        return

    linear, tol_label = _own_linear_tolerance(record, session, report)
    if linear is None:
        report.skip(
            "G-51",
            location,
            f"{record.label} declares no usable tolerances.linear_cm and the session fallback "
            "was unavailable, so G-51 will not assume a distance to compare against",
        )
        return
    problems = 0
    judged = 0
    rails_seen: list[str] = []
    for index, surface in sweeps:
        where = f"{location}::surfaces[{index}]"
        kind = surface.get("kind")
        _rail_refs, rail_rows, rail_blocker = _referenced_rows(surface, NURBS_RAIL_SECTION_KEY, rows)
        _sec_refs, sec_rows, sec_blocker = _referenced_rows(surface, "section_ids", rows)
        blocker = rail_blocker or sec_blocker
        if blocker is not None:
            report.skip(
                "G-51",
                where,
                f"{blocker}; G-51 will not measure a distance against geometry it does not "
                "have, and the rule that owns that reference has already reported it by name",
            )
            continue
        rails_seen.extend(ref for ref in rail_rows if ref not in rails_seen)
        missed: list[tuple[float, str, str]] = []
        for sec_ref in sec_rows:
            judged += 1
            for rail_ref in rail_rows:
                gap = _polylines_distance(rows[sec_ref], rows[rail_ref])
                if gap is None:
                    continue  # a degenerate row has no segment to measure against
                if gap > linear:
                    missed.append((gap, sec_ref, rail_ref))
        rails_noun = "rail" if len(rail_rows) == 1 else "rails"
        for gap, sec_ref, rail_ref in missed:
            report.fail(
                "G-51",
                f"{where}.section_ids",
                f"cross-section {sec_ref} of a {kind} stays {gap:g} cm from rail {rail_ref} "
                f"of its {len(rail_rows)} {rails_noun} {', '.join(rail_rows)}, over the declared "
                "tolerance; every cross-section must reach EVERY rail, because an invalid "
                "dependent surface is SILENTLY DROPPED at commit with no error and no warning "
                "(CHECKPOINT 'Rail sweeps, blends and trims'), so this spec would build to a "
                f"set with no {kind} in it",
                tol_label,
            )
            problems += 1

    if problems == 0 and judged == 0:
        # Every sweep above declined to measure, so no distance was compared at all.
        # A check that could not be evaluated reports SKIP with its reason; a PASS here
        # would claim a verdict it never earned, which is the one outcome this rule
        # exists to make impossible.
        report.skip(
            "G-51",
            location,
            f"{len(sweeps)} sweep(s) declared, but no cross-section of any of them resolved to "
            "measurable geometry, so no distance was compared; each sweep's own row above names "
            "the reference that G-44 or G-42 owns",
        )
        return

    if problems == 0:
        report.ok(
            "G-51",
            location,
            f"{judged} cross-section(s) of {len(sweeps)} sweep(s) reach EVERY one of their "
            f"rail(s) {', '.join(rails_seen)}: every point-to-segment distance over both "
            "polylines is within the declared tolerance (the silent-drop pre-flight, "
            "07 section 9.7 G-51)",
            tol_label,
        )


# ---- G-52 blend parents and edges -------------------------------------------- #


def _g52_blend_edges(record: LoadedFile, report: Report) -> None:
    """G-52. A blend's parents are ``SUR-nnn`` ids declared *earlier*; edges are 1..4.

    "Earlier" is the whole point and is stricter than G-44's "resolves somewhere
    in this file". The builder emits the parent as a sub-object index captured
    immediately after the parent's own append, so a parent declared after the
    blend names an index that does not exist yet -- and the failure it produces is
    the silent kind G-51 exists to prevent.

    ``edge1``/``edge2`` are 1..4 = low-U, high-U, low-V, high-V. The range is
    compared exactly (07 section 9.5); the verified transcripts used
    ``edge1: 1 edge2: 1`` and read back exactly.
    """
    location = record.label
    doc = record.doc
    blends = _p4b_surfaces(doc, "blend")
    if not blends:
        report.skip(
            "G-52",
            location,
            "no blend surface; there is no parent to resolve and no edge to range-check",
        )
        return

    order: dict[str, int] = {}
    for index, surface in enumerate(_nurbs_table(doc, "surfaces") or []):
        if isinstance(surface, dict) and isinstance(surface.get("id"), str):
            order.setdefault(surface["id"], index)

    problems = 0
    resolved = 0
    for index, surface in blends:
        where = f"{location}::surfaces[{index}]"
        for key in ("parent1_ref", "parent2_ref"):
            if key not in surface:
                continue  # G-43 owns absence; G-50 owns an empty value
            value = surface.get(key)
            if not isinstance(value, str) or not value:
                continue  # G-50 already named the empty ref
            if not SURFACE_ID_RE.match(value):
                report.fail(
                    "G-52",
                    f"{where}.{key}",
                    f"{key} {value!r} is not a SUR-nnn id; a blend parent is another surface in "
                    "this file (07 section 9.7 G-52)",
                )
                problems += 1
                continue
            declared = order.get(value)
            if declared is None:
                report.fail(
                    "G-52",
                    f"{where}.{key}",
                    f"{key} {value!r} is not declared in surfaces[] of this file",
                )
                problems += 1
                continue
            if declared >= index:
                report.fail(
                    "G-52",
                    f"{where}.{key}",
                    f"{key} {value!r} is declared at surfaces[{declared}], at or after this "
                    f"blend at surfaces[{index}]; a blend parent must be declared earlier, "
                    "because the builder binds its sub-object index at the parent's append "
                    "(07 section 9.7 G-52)",
                )
                problems += 1
                continue
            resolved += 1
        for key in ("edge1", "edge2"):
            if key not in surface:
                continue  # G-43 owns absence
            value = surface.get(key)
            if not is_int(value) or value not in NURBS_BLEND_EDGES:
                report.fail(
                    "G-52",
                    f"{where}.{key}",
                    f"{key} {value!r} is not an integer in "
                    f"{NURBS_BLEND_EDGES[0]}..{NURBS_BLEND_EDGES[-1]} "
                    "(low-U, high-U, low-V, high-V), compared exactly (07 section 9.7 G-52)",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-52",
            location,
            f"{len(blends)} blend(s): {resolved} parent ref(s) are SUR-nnn ids declared earlier "
            f"in the file, and every edge is an integer in {NURBS_BLEND_EDGES[0]}.."
            f"{NURBS_BLEND_EDGES[-1]}",
        )


# ---- G-53 trim projection inputs -------------------------------------------- #


def _g53_trim_inputs(record: LoadedFile, report: Report) -> None:
    """G-53. ``p_vec`` is 3 numbers of non-zero magnitude, ``seed`` 2, ``flip_trim`` a bool.

    A ``p_vec`` of ``[0, 0, 0]`` is the one that matters: the constructor accepts
    any keyword and any value, so a zero vector constructs cleanly, commits, and
    projects nowhere -- which is why this is a FAIL here and not a warning.

    A key that is absent is G-43's row, not a second row here (the same division
    G-46 makes); this rule evaluates the shape and the value of the keys the
    schema says a ``trim`` carries.
    """
    location = record.label
    doc = record.doc
    trims = _p4b_surfaces(doc, "trim")
    if not trims:
        report.skip("G-53", location, "no trim surface; there is no p_vec, seed or flip_trim to check")
        return

    problems = 0
    for index, surface in trims:
        where = f"{location}::surfaces[{index}]"
        if "p_vec" in surface:
            vector = _finite_triple(surface.get("p_vec"))
            if vector is None:
                report.fail(
                    "G-53",
                    f"{where}.p_vec",
                    f"p_vec {surface.get('p_vec')!r} is not exactly 3 finite numbers; the "
                    "P4b projection direction is [x, y, z] (07 section 9.7 G-53)",
                )
                problems += 1
            elif math.sqrt(sum(component * component for component in vector)) == 0.0:
                report.fail(
                    "G-53",
                    f"{where}.p_vec",
                    "p_vec has zero magnitude; the constructor accepts it and commits it and "
                    "the profile is projected nowhere, which is a silent loss rather than a "
                    "refusal (07 section 9.7 G-53)",
                )
                problems += 1
        if "seed" in surface:
            pair = _finite_pair(surface.get("seed"))
            if pair is None:
                report.fail(
                    "G-53",
                    f"{where}.seed",
                    f"seed {surface.get('seed')!r} is not exactly 2 finite numbers; the seed is "
                    "a [u, v] point on the surface (07 section 9.7 G-53)",
                )
                problems += 1
        if "flip_trim" in surface and not isinstance(surface.get("flip_trim"), bool):
            report.fail(
                "G-53",
                f"{where}.flip_trim",
                f"flip_trim {surface.get('flip_trim')!r} is not a bool; MAXScript reads flipTrim "
                "as a bool, and a non-bool is either refused or quietly ignored "
                "(07 section 9.7 G-53)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-53",
            location,
            f"{len(trims)} trim(s): p_vec is 3 finite numbers of non-zero magnitude, seed is 2 "
            "finite numbers, flip_trim is a bool",
        )


# ---- G-54 emitted-surface census -- SKIP, never a silent PASS --------------- #


def _g54_surface_census(record: LoadedFile, report: Report) -> None:
    """G-54. The emitted-surface census. SKIP with its reason, by construction.

    G-54 asks whether a committed node holds exactly the number of ``NURBSSurface``
    sub-objects the spec implies. That number does not exist until ``NURBSNode``
    commits in 3ds Max, and a dependent surface that fails to commit is *silently
    dropped* rather than reported -- so the census is the only thing that can catch
    it, and the only thing that can run it is the emitted ``.ms``, which counts the
    sub-objects after the commit and throws on a mismatch.

    A JSON file cannot observe a commit. This rule therefore reports SKIP and says
    why, which is this repo's standing answer for a check that cannot be evaluated
    (07 section 9.6) and the reason G-54 is stated as "honest SKIP at lint time".
    Reporting PASS here would be the one dishonest outcome available: it would claim
    a verdict no static reader has earned, on exactly the rule that exists because
    P4 shipped a stage whose whole cost of a wrong decision was invisible.
    """
    report.skip(
        "G-54",
        record.label,
        "not evaluable at lint time. G-54 counts the NURBSSurface sub-objects of the "
        "committed node, and a commit happens only inside 3ds Max: the dependent surfaces "
        "this census exists to catch are silently dropped there, with no error and no "
        "warning, so nothing in this file can observe whether one survived. Enforced at "
        "build time instead, by the emitted .ms counting the sub-objects after NURBSNode "
        "and throwing on a mismatch. A check that cannot be evaluated reports SKIP with "
        "its reason, never a silent PASS.",
    )


# ---- G-55 blend tension is a bounded float ---------------------------------- #


def _g55_blend_tension(record: LoadedFile, report: Report) -> None:
    """G-55. ``tension1`` / ``tension2`` are floats in ``[0.0, 1.0]``. FAIL outside.

    **Why the range exists, because 1.0 is not a neutral default.**
    ``NURBSBlendSurface`` tension measures the deviation from a *straight transition
    between the two selected edges*. Measured on the worked example (D1, live 3ds Max
    2026.3.2, 2026-10-04):

    =============  ===================  =====================  ====================
    ``tension``    blend bbox Y          blend bbox Z           reading
    =============  ===================  =====================  ====================
    ``0.0 / 0.0``  ``450 .. 900.0``      ``420.0 .. 600.97``    exactly the gap
    ``0.5 / 0.5``  ``450 .. 995.514``    ``401.084 .. 600.97``  bulges 95 cm
    ``1.0 / 1.0``  ``450 .. 1195.64``    ``369.758 .. 600.97``  bulges **295.64 cm**
    =============  ===================  =====================  ====================

    The vault's own high-V edge is ``y = 900``; at ``1.0/1.0`` the blend reached
    ``y = 1195.64`` -- 295.64 cm past the parent, and 50 cm below the springing. At
    ``0.0/0.0`` it fills exactly between the two selected edges, which is what a
    soffit panel is.

    Max does **not** bound that overshoot above: the constructor accepts any value,
    reads it back exactly, and commits. So the bound has to be the schema's, which is
    what this rule is. A missing key is not a FAIL -- it resolves to the documented
    default ``0.0`` (NURBS_P4B_DEFAULTS) -- and a key that is present is compared
    exactly, with no epsilon (07 section 9.5).
    """
    location = record.label
    doc = record.doc
    blends = _p4b_surfaces(doc, "blend")
    if not blends:
        report.skip(
            "G-55",
            location,
            "no blend surface, so there is no tension to range-check; a missing tension on a "
            f"blend resolves to the documented default {NURBS_P4B_DEFAULTS['tension1']}",
        )
        return

    problems = 0
    judged = 0
    for index, surface in blends:
        where = f"{location}::surfaces[{index}]"
        for key in ("tension1", "tension2"):
            if key not in surface:
                continue
            judged += 1
            value = surface.get(key)
            number = as_number(value)
            if number is None or not math.isfinite(number):
                report.fail(
                    "G-55",
                    f"{where}.{key}",
                    f"{key} {value!r} is not a finite number; a blend tension is a float in "
                    f"[{NURBS_TENSION_MIN:g}, {NURBS_TENSION_MAX:g}], compared exactly "
                    "(07 section 9.7 G-55)",
                )
                problems += 1
            elif not NURBS_TENSION_MIN <= number <= NURBS_TENSION_MAX:
                report.fail(
                    "G-55",
                    f"{where}.{key}",
                    f"{key} {value!r} is outside [{NURBS_TENSION_MIN:g}, {NURBS_TENSION_MAX:g}]. "
                    f"{NURBS_TENSION_MIN:g} is the straight transition between the two selected "
                    "edges; above 0 the blend is pushed outward past BOTH parents and the "
                    "overshoot grows with the tension -- measured 295.64 cm past the parent, and "
                    "50 cm below the springing, at 1.0. 3ds Max does not bound that overshoot "
                    "above and reports nothing, so the schema is the only bound "
                    "(07 section 9.7 G-55)",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-55",
            location,
            f"{judged} declared tension value(s) across {len(blends)} blend(s) are within "
            f"[{NURBS_TENSION_MIN:g}, {NURBS_TENSION_MAX:g}], compared exactly; "
            f"{len(blends) * 2 - judged} omitted value(s) resolve to the documented default "
            f"{NURBS_P4B_DEFAULTS['tension1']} (D1)",
        )


# ---- G-56 a relation parent hands a real nurbsID ----------------------------- #


def _g56_parent_pointer(record: LoadedFile, report: Report) -> None:
    """G-56. A relation parent must be a node that actually hands over a ``nurbsID``.

    A ``parent1ID:`` / ``parent2ID:`` slot is a **pointer**, and D4 measured all three
    outcomes for the same keyword:

    * a string literal -> a clean ``Unable to convert ... to type: IntegerPtr`` error;
    * a value read from a committed sub-object -> the node commits and evaluates
      correctly (D3);
    * a synthetic number (``parent1ID:12345``) -> **``EXCEPTION_ACCESS_VIOLATION``**,
      a hard crash of the 3ds Max *process*, not a MAXScript error, not recoverable
      from inside the script.

    That third outcome is why this rule is what it is. No offline check can observe a
    process crash, so the check has to be upstream of it: the builder binds every
    ``*ID:`` slot from a committed sub-object
    (``local id_<parent> = mcpNurbsSurfID <parent> "<parent>"``), and the only spec-level
    way to break that is to name a parent whose committed node holds no
    ``NURBSSurface`` to read. ``trim`` is exactly that case -- ``trim:false``
    "produces no surface at all", and ``trim:true`` does not cut, it appends an
    untrimmed ``NURBSCVSurface`` **copy of the parent** (D5) -- so a ``trim`` parent
    would force a literal into the slot and crash Max. It is refused by name here.

    This is the lint half. The build half -- no literal in a ``parent1ID:`` /
    ``parent2ID:`` position in the emitted bytes -- lives in ``build_nurbs.py``'s
    ``verify_script``, which is the only place the emitted text exists.
    """
    location = record.label
    doc = record.doc
    order: dict[str, str] = {}
    for surface in _nurbs_table(doc, "surfaces") or []:
        if isinstance(surface, dict) and isinstance(surface.get("id"), str):
            order.setdefault(surface["id"], str(surface.get("kind")))

    problems = 0
    resolved = 0
    for index, surface in enumerate(_nurbs_table(doc, "surfaces") or []):
        if not isinstance(surface, dict) or surface.get("kind") not in NURBS_P4B_KINDS:
            continue
        where = f"{location}::surfaces[{index}]"
        for key in ("parent1_ref", "parent2_ref", "surface_ref"):
            if key not in surface:
                continue  # G-43 owns absence; G-50 owns an empty value
            value = surface.get(key)
            if not isinstance(value, str) or not value:
                continue  # G-50 already named the empty ref
            parent_kind = order.get(value)
            if parent_kind is None:
                continue  # G-44 / G-52 already named the unresolved id
            if parent_kind in NURBS_ID_BEARING_KINDS:
                resolved += 1
                continue
            report.fail(
                "G-56",
                f"{where}.{key}",
                f"{key} names {value}, whose kind is {parent_kind!r}. The builder names a "
                "relation parent by the `nurbsID` it reads from the parent's FIRST committed "
                f"NURBSSurface (D3), so the parent must be one of {list(NURBS_ID_BEARING_KINDS)}. "
                f"A {parent_kind} commits none -- `trim:false` produces no surface at all, and "
                "`trim:true` does not cut, it appends a copy of the parent (D5) -- so it has no "
                "id to bind. Filling that slot with a literal is not a warning: a synthetic "
                "`nurbsID` crashes 3ds Max with EXCEPTION_ACCESS_VIOLATION (D4), which no "
                "offline check can catch after the fact (07 section 9.7 G-56)",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-56",
            location,
            f"{resolved} relation parent ref(s) name a node that commits at least one "
            f"NURBSSurface, so each is bound from a committed sub-object and no "
            "`parent1ID:`/`parent2ID:` slot can hold a literal (D3, D4); the same rule is "
            "enforced against the emitted bytes by build_nurbs.py's verify_script",
        )


# --------------------------------------------------------------------------- #
# 07 section 9.8 -- G-57..G-70, the facade_grids.json and components_registry.json
# invariants
#
# Same machinery as G-34..G-56 and no new tolerance values: the id scanner is
# G-34's, the leaf walker and coverage test are G-9's, the area helper is G-21's,
# the dotted-path resolver is G-32's, the ``nearest`` half-open comparison is
# G-27's, and every geometry row names the tolerance it used (07 section 9.5).
# --------------------------------------------------------------------------- #


class P5Tolerances(NamedTuple):
    """The three 07 section 9.5 tolerances, each with the label its row prints."""

    linear: float
    area: float
    angle: float
    tol_linear: str
    tol_area: str
    tol_angle: str


def _p5_tolerances(record: LoadedFile, session: Session) -> P5Tolerances:
    """``linear_cm`` from this file's own block, ``area_m2`` / ``angle_deg`` from the session.

    Same reasoning as ``_own_linear_tolerance``: a geometry row must name the block its
    number came from, and 07 section 8.3 / 8.4 give these two files their own copy of the
    block, copied verbatim from ``dimensions.json``. ``area_m2`` and ``angle_deg`` keep the
    session label because that is the block they come from.
    """
    doc = record.doc
    block = doc.get("tolerances") if isinstance(doc, dict) else None
    linear = as_number(block.get("linear_cm")) if isinstance(block, dict) else None
    _session_linear, area, angle, source = session.tolerances()
    if linear is None:
        linear = _session_linear
        tol_linear = (
            f"{linear} cm (07 section 9.5 fallback: {record.label} declares no "
            "tolerances.linear_cm)"
        )
    else:
        tol_linear = f"{linear} cm ({record.label} tolerances)"
    return P5Tolerances(
        linear,
        area,
        angle,
        tol_linear,
        f"{area} m2 ({source})",
        f"{angle} deg ({source})",
    )


# ---- shared P5 readers ------------------------------------------------------ #


def _p5_array(doc: Any, key: str) -> Optional[list[Any]]:
    """``doc[key]`` when it is an array, else None. The shape error is the caller's row."""
    value = doc.get(key) if isinstance(doc, dict) else None
    return value if isinstance(value, list) else None


def _p5_rows(doc: Any, key: str) -> list[dict]:
    """The object rows of ``doc[key]``, in file order."""
    return [entry for entry in (_p5_array(doc, key) or []) if isinstance(entry, dict)]


def _p5_index(doc: Any, key: str) -> dict[str, dict]:
    """``id -> entry`` for an array of objects, first occurrence winning."""
    out: dict[str, dict] = {}
    for entry in _p5_rows(doc, key):
        if isinstance(entry.get("id"), str):
            out.setdefault(entry["id"], entry)
    return out


def _p5_facade_index(doc: Any) -> dict[str, dict]:
    return _p5_index(doc, "facades")


def _p5_panel_type_index(doc: Any) -> dict[str, dict]:
    """``kind -> panel_types[] entry``. The key is ``kind``, not ``id``."""
    out: dict[str, dict] = {}
    for entry in _p5_rows(doc, "panel_types"):
        if isinstance(entry.get("kind"), str):
            out.setdefault(entry["kind"], entry)
    return out


def _p5_level_index(doc: Any) -> dict[tuple[str, int], dict]:
    """``(facade id, level_index) -> that facade's entry for that level``."""
    out: dict[tuple[str, int], dict] = {}
    for facade in _p5_rows(doc, "facades"):
        ident = facade.get("id")
        if not isinstance(ident, str):
            continue
        for level in facade.get("levels") or []:
            if isinstance(level, dict) and is_int(level.get("level_index")):
                out.setdefault((ident, level["level_index"]), level)
    return out


def _p5_level_keys(doc: Any) -> list[tuple[str, int]]:
    """Every ``(facade id, level_index)`` a ``facades[]`` entry declares, in file order."""
    return list(_p5_level_index(doc))


def _p5_ids(values: Sequence[Any], limit: int = P5_ID_LIST_LIMIT) -> str:
    """``"AX-001, AX-002 (+4 more)"`` -- what a FAIL row names before the count takes over."""
    shown = [str(value) for value in values[:limit]]
    rest = len(values) - len(shown)
    if rest <= 0:
        return ", ".join(shown)
    return ", ".join(shown) + f" (+{rest} more)"


def _p5_run_angle_deg(facade: Any) -> Optional[float]:
    """``atan2(end.y - start.y, end.x - start.x)`` normalised to ``(-180, 180]``.

    ``atan2`` already returns that half-open range, so the only case the normalisation has
    to fix is exactly ``-180.0`` -- which is why the contract insists that ``180.0`` stays
    ``180.0`` and G-16 bounds the key as ``-180 < x <= 180``.
    """
    if not isinstance(facade, dict):
        return None
    start = _finite_pair(facade.get("start_corner_cm"))
    end = _finite_pair(facade.get("end_corner_cm"))
    if start is None or end is None:
        return None
    angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))
    if angle <= -180.0:
        angle += 360.0
    return angle


def _p5_run_unit(facade: Any) -> Optional[tuple[float, float]]:
    """``((end - start) / length_cm)`` in XY -- the unit vector a panel's centre walks."""
    if not isinstance(facade, dict):
        return None
    start = _finite_pair(facade.get("start_corner_cm"))
    end = _finite_pair(facade.get("end_corner_cm"))
    length = as_number(facade.get("length_cm"))
    if start is None or end is None or length is None or length <= 0.0:
        return None
    return ((end[0] - start[0]) / length, (end[1] - start[1]) / length)


def _p5_bay_index(bay_width_cm: Any, u_mid: float, linear: float) -> Optional[int]:
    """The bay whose half-open ``[offset, offset + width)`` contains ``u_mid``.

    Only the lower edge is read with the tolerance, so a midpoint sitting exactly on a bay
    boundary belongs to the *later* bay and can never match both.
    """
    widths = _numbers(bay_width_cm)
    if not widths:
        return None
    offsets = cumulative(widths)
    for index in range(len(widths)):
        if offsets[index] - linear <= u_mid < offsets[index + 1]:
            return index
    return None


def _p5_panel_rect(panel: Any) -> Optional[tuple[float, float, float, float]]:
    """``(u_min, u_max, v_min, v_max)`` of finite numbers, or None."""
    if not isinstance(panel, dict):
        return None
    numbers = [
        as_number(panel.get(key))
        for key in ("u_min_cm", "u_max_cm", "v_min_cm", "v_max_cm")
    ]
    if any(item is None or not math.isfinite(item) for item in numbers):
        return None
    return (numbers[0], numbers[1], numbers[2], numbers[3])  # type: ignore[return-value]


def _p5_panel_ring(rect: tuple[float, float, float, float]) -> list[list[float]]:
    """The panel rectangle as a 4-ring, so ``polygon_area_m2`` reads it unchanged."""
    u0, u1, v0, v1 = rect
    return [[u0, v0], [u1, v0], [u1, v1], [u0, v1]]


def _p5_bay_offsets(facade: Any) -> Optional[list[float]]:
    """``bay_offsets_cm``, recomputed as the cumulative sum of ``bay_width_cm``.

    Recomputed rather than read: ``bay_offsets_cm`` is itself a derived value (G-57 checks it
    against exactly this), and G-61 has to judge a panel against its bay's rectangle whether or
    not the declared boundaries agree. ``None`` when the widths are unreadable.
    """
    if not isinstance(facade, dict):
        return None
    widths = _numbers(facade.get("bay_width_cm"))
    if not widths:
        return None
    return cumulative(widths)


def _p5_bay_span(facade: Any, bay_index: Any) -> Optional[tuple[float, float]]:
    """``(bay_offsets_cm[b], bay_offsets_cm[b + 1])`` -- the bay's half-open extent."""
    offsets = _p5_bay_offsets(facade)
    if offsets is None or not is_int(bay_index) or not 0 <= bay_index < len(offsets) - 1:
        return None
    return offsets[bay_index], offsets[bay_index + 1]


def _p5_openings_by_bay(dimensions_doc: Any) -> dict[tuple[str, int, int], list[dict]]:
    """``(facade, level_index, bay_index) -> that bay's openings``, each group by id.

    The tiling unit of P5 is ``(facade, level, bay)`` because the vertical division is per bay:
    an opening's own sill and head are the only horizontal lines that cross it. G-28 forbids two
    openings sharing a key, so a group holds at most one -- but the builder admits every member
    and so does this reader.
    """
    out: dict[tuple[str, int, int], list[dict]] = {}
    if not isinstance(dimensions_doc, dict):
        return out
    for opening in _p5_rows(dimensions_doc, "openings"):
        facade = opening.get("facade")
        level = opening.get("level_index")
        bay = opening.get("bay_index")
        if not isinstance(facade, str) or not is_int(level) or not is_int(bay):
            continue
        out.setdefault((facade, level, bay), []).append(opening)
    for group in out.values():
        group.sort(key=lambda opening: str(opening.get("id")))
    return out


def _p5_component_families(doc: Any) -> dict[str, list[str]]:
    """``component id -> the family ids that list it``, built from ``families[]``."""
    out: dict[str, list[str]] = {}
    for family in _p5_rows(doc, "families"):
        ident = family.get("id")
        if not isinstance(ident, str):
            continue
        for ref in family.get("component_ids") or []:
            out.setdefault(str(ref), []).append(ident)
    return out


def _p5_cell(value: Any) -> Optional[float]:
    """A CSV cell as a number.

    ``as_number`` is deliberately strict about JSON types, and every cell of a parsed CSV
    row is a **string**, so a strict reader would report every row as non-numeric and turn
    the census into noise. ``q()`` already bounds the emitted decimals, so ``float()`` on the
    stripped cell is exact enough to compare against ``angle_deg``.
    """
    direct = as_number(value)
    if direct is not None:
        return direct
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _p5_missing_registry_row(
    rule: str, location: str, report: Report, what: str
) -> None:
    """The SKIP a cross-file P5 rule reports when the registry is absent.

    Not a helper for its own sake: ``G-63``, ``G-67`` and ``G-68`` all read
    ``components_registry.json``, and a rule that cannot be evaluated reports SKIP with its
    reason -- never a vacuous PASS.
    """
    report.skip(
        rule,
        location,
        f"components_registry.json is absent; {what} is cross-file, so {rule} cannot be "
        f"evaluated and will not report a PASS it did not earn. A check that cannot be "
        "evaluated reports SKIP with its reason (07 section 9.6)",
    )


# ---- G-57 facade agreement and run angle ------------------------------------- #


def _g57_facade_agreement(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-57. Facade agreement with ``dimensions.json``, and the run angle of the run.

    ``direction_deg`` is a **compass-facing label, not a rotation**, and this rule is
    separate because that is exactly the kind of field a later stage reaches for. ``F-S``
    runs ``[0,0] -> [1800,0]``, i.e. along **+X**, and carries ``direction_deg = 180.0``.
    ``F-N`` runs ``[0,900] -> [1800,900]``, also **+X**, and carries ``0.0``. Two facades
    with the *same* run direction therefore carry *different* ``direction_deg``, so any
    rotation derived from it is wrong for at least one of them -- and neither value is the
    rotation, because a +X run is ``0.0``.

    The rotation every panel on a facade uses is ``run_angle_deg =
    atan2(end.y - start.y, end.x - start.x)``, normalised to ``(-180, 180]`` and compared
    within ``angle_deg``. ``180.0`` stays ``180.0``; it is never folded to ``-180.0``.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        report.skip(
            "G-57",
            location,
            f"{dimensions.label if dimensions else 'dimensions.json'} is not loaded as a usable "
            "document; facade agreement, bay arithmetic and the run angle are all read from it, "
            "so G-57 will not assume an answer for a file it cannot read",
        )
        return

    grid = _p5_rows(doc, "facades")
    source_facades = _p5_rows(dimensions.doc, "facades")
    if _p5_array(doc, "facades") is None or _p5_array(dimensions.doc, "facades") is None:
        report.fail(
            "G-57",
            location,
            f"facades is {doc.get('facades')!r} here and "
            f"{dimensions.doc.get('facades')!r} in {dimensions.label}; both must be arrays "
            "(07 section 9.8 G-57)",
        )
        return

    problems = 0
    judged = 0
    grid_ids = [facade.get("id") for facade in grid]
    source_ids = [facade.get("id") for facade in source_facades]
    if grid_ids != source_ids:
        report.fail(
            "G-57",
            f"{location}::facades",
            f"facade ids differ from {dimensions.label} in identity or in order: here "
            f"{_p5_ids(grid_ids)}, there {_p5_ids(source_ids)}; 07 G-57 requires the same ids in "
            "the same order, so the grids and the dimensions cannot drift apart by position",
        )
        problems += 1

    by_id = {facade["id"]: facade for facade in source_facades if isinstance(facade.get("id"), str)}
    for index, facade in enumerate(grid):
        where = f"{location}::facades[{index}]"
        ident = facade.get("id")
        source = by_id.get(ident) if isinstance(ident, str) else None
        if source is None:
            continue  # the id/order row above already named this facade

        for key, tolerance in (("name", ""), ("direction_deg", "")):
            judged += 1
            if not deep_equal(facade.get(key), source.get(key)):
                report.fail(
                    "G-57",
                    f"{where}.{key}",
                    f"{key} is {facade.get(key)!r}; {dimensions.label} says "
                    f"{source.get(key)!r} and 07 G-57 requires equality"
                    + (
                        ". direction_deg is a facing label: it is copied, never recomputed, and "
                        "never used as a rotation"
                        if key == "direction_deg"
                        else ""
                    ),
                    tolerance,
                )
                problems += 1

        length = as_number(facade.get("length_cm"))
        judged += 1
        if length is None or not close(length, as_number(source.get("length_cm")), tols.linear):
            report.fail(
                "G-57",
                f"{where}.length_cm",
                f"length_cm is {fmt_number(facade.get('length_cm'))}; {dimensions.label} says "
                f"{fmt_number(source.get('length_cm'))}",
                tols.tol_linear,
            )
            problems += 1

        judged += 1
        if not is_int(facade.get("bay_count")) or facade.get("bay_count") != source.get("bay_count"):
            report.fail(
                "G-57",
                f"{where}.bay_count",
                f"bay_count is {facade.get('bay_count')!r}; {dimensions.label} says "
                f"{source.get('bay_count')!r} and a count is compared exactly "
                "(07 section 9.5)",
            )
            problems += 1

        widths = _numbers(facade.get("bay_width_cm"))
        source_widths = _numbers(source.get("bay_width_cm"))
        judged += 1
        if widths is None or source_widths is None:
            report.fail(
                "G-57",
                f"{where}.bay_width_cm",
                f"bay_width_cm is {facade.get('bay_width_cm')!r}; it must be an array of numbers "
                f"and {dimensions.label} holds {source.get('bay_width_cm')!r}",
            )
            problems += 1
            continue
        if len(widths) != len(source_widths) or any(
            not close(a, b, tols.linear) for a, b in zip(widths, source_widths)
        ):
            report.fail(
                "G-57",
                f"{where}.bay_width_cm",
                f"bay_width_cm is {_short(widths)}; {dimensions.label} says "
                f"{_short(source_widths)}",
                tols.tol_linear,
            )
            problems += 1

        expected_offsets = cumulative(widths)
        offsets = _numbers(facade.get("bay_offsets_cm"))
        judged += 1
        if offsets is None or len(offsets) != len(expected_offsets):
            report.fail(
                "G-57",
                f"{where}.bay_offsets_cm",
                f"bay_offsets_cm is {_short(facade.get('bay_offsets_cm'))}; the derived cumulative "
                f"sum of {len(widths)} bay(s) has {len(expected_offsets)} entries "
                f"{_short(expected_offsets)}",
                tols.tol_linear,
            )
            problems += 1
            continue
        for position, (actual, expected) in enumerate(zip(offsets, expected_offsets)):
            if not close(actual, expected, tols.linear):
                report.fail(
                    "G-57",
                    f"{where}.bay_offsets_cm[{position}]",
                    f"bay boundary {position} is {fmt_number(actual)} but the derived cumulative "
                    f"sum of bay_width_cm is {fmt_number(expected)}",
                    tols.tol_linear,
                )
                problems += 1
        if offsets[0] != 0.0:
            report.fail(
                "G-57",
                f"{where}.bay_offsets_cm[0]",
                f"the first bay boundary is {fmt_number(offsets[0])}; a cumulative sum starts at 0",
                tols.tol_linear,
            )
            problems += 1
        if length is not None and not close(offsets[-1], length, tols.linear):
            report.fail(
                "G-57",
                f"{where}.bay_offsets_cm[{len(offsets) - 1}]",
                f"the last bay boundary is {fmt_number(offsets[-1])} but length_cm is "
                f"{fmt_number(length)}; the bays must close the run",
                tols.tol_linear,
            )
            problems += 1

        expected_centres = [offset + width / 2 for offset, width in zip(expected_offsets, widths)]
        centres = _numbers(facade.get("bay_centre_cm"))
        judged += 1
        if centres is None or len(centres) != len(expected_centres) or any(
            not close(a, b, tols.linear) for a, b in zip(centres, expected_centres)
        ):
            report.fail(
                "G-57",
                f"{where}.bay_centre_cm",
                f"bay_centre_cm is {_short(facade.get('bay_centre_cm'))}; the derived "
                "bay_offsets_cm[i] + bay_width_cm[i] / 2 is "
                f"{_short([round(value, 6) for value in expected_centres])}",
                tols.tol_linear,
            )
            problems += 1

        expected_angle = _p5_run_angle_deg(facade)
        declared_angle = as_number(facade.get("run_angle_deg"))
        judged += 1
        if declared_angle is None or not close(declared_angle, expected_angle, tols.angle):
            report.fail(
                "G-57",
                f"{where}.run_angle_deg",
                f"run_angle_deg is {fmt_number(facade.get('run_angle_deg'))} but the derived "
                "atan2(end.y - start.y, end.x - start.x) is "
                f"{fmt_number(expected_angle) if expected_angle is not None else 'undefined'} "
                f"(direction_deg is {fmt_number(facade.get('direction_deg'))} and is NOT it: two "
                "facades that both run along +X carry 180.0 and 0.0, so direction_deg is a "
                "facing label)",
                tols.tol_angle,
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-57",
            location,
            f"{len(grid)} facade(s) agree with {dimensions.label} by id, order, name, "
            f"direction_deg, length_cm, bay_count and bay_width_cm; every bay_offsets_cm is the "
            f"cumulative sum, every bay_centre_cm is offsets[i] + width[i]/2, and every "
            f"run_angle_deg equals its derived atan2 in (-180, 180] ({judged} comparisons)",
        )


# ---- G-58 axis integrity ---------------------------------------------------- #


def _g58_axis_integrity(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-58. Axis ids, vocabulary, ``bay_index``, bounds, spacing, and the per-level lists.

    **The vertical division is per bay, and ``bay_index`` is what says so.** A ``u`` axis is a
    line across the whole run, so its ``bay_index`` is ``null``; a ``v`` axis is a spandrel or head
    line belonging to one bay's elevation, so it carries that bay's index. Uniqueness and ordering
    are therefore per ``(facade, level_index, family, bay_index)`` -- two bays may each hold an axis
    at ``head_cm = 270`` without colliding, and they must.

    The reason is measurement, not taste. A facade-wide v grid is the union of every opening's
    sill and head on that facade at that level, which imposes each bay's head line on **every other
    bay**: an entrance at ``head_cm = 260`` puts a horizontal division through a window running
    ``90 -> 270`` and yields a ``180 x 10 cm`` glass sliver ten centimetres below its head. Per-bay
    divisions make an opening's own sill and head its *only* horizontal lines, so no cell can
    straddle an opening edge and every opening is realised by exactly one panel (G-62).
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    axes = _p5_array(doc, "axes")
    if axes is None:
        report.fail("G-58", f"{location}::axes", f"axes is {doc.get('axes')!r}, expected an array")
        return

    problems = _scan_id_sequence(axes, "axes", location, report, "G-58", AXIS_ID_RE, AXIS_ID_PATTERN)
    axis_rows = _p5_rows(doc, "axes")
    axis_index = _p5_index(doc, "axes")
    facades = _p5_facade_index(doc)
    levels = _p5_level_index(doc)

    groups: dict[tuple[Any, Any, str, Any], list[tuple[str, float]]] = {}
    for index, axis in enumerate(axis_rows):
        where = f"{location}::axes[{index}]"
        family = axis.get("family")
        kind = axis.get("kind")
        ident = axis.get("id")
        if family not in FACADE_AXIS_FAMILIES:
            report.fail(
                "G-58",
                f"{where}.family",
                f"family {family!r} is not one of {', '.join(FACADE_AXIS_FAMILIES)}: an axis runs "
                "along the facade (u) or up one bay's storey (v) (07 section 8.3.3)",
            )
            problems += 1
            continue
        if kind not in FACADE_AXIS_KINDS:
            report.fail(
                "G-58",
                f"{where}.kind",
                f"kind {kind!r} is not one of {', '.join(FACADE_AXIS_KINDS)} (07 section 8.3.3)",
            )
            problems += 1
        offset = as_number(axis.get("offset_cm"))
        if offset is None:
            report.fail(
                "G-58",
                f"{where}.offset_cm",
                f"offset_cm is {axis.get('offset_cm')!r}; an axis carries exactly one number",
            )
            problems += 1
            continue

        facade_id = axis.get("facade")
        level_index = axis.get("level_index")
        facade = facades.get(facade_id) if isinstance(facade_id, str) else None
        level = levels.get((facade_id, level_index))
        if facade is None:
            report.fail(
                "G-58", f"{where}.facade", f"facade {facade_id!r} is not a facades[].id of this file"
            )
            problems += 1
            continue
        if level is None:
            report.fail(
                "G-58",
                f"{where}.level_index",
                f"level_index {level_index!r} is not a levels[].level_index of {facade_id!r}",
            )
            problems += 1
            continue

        bay_index = axis.get("bay_index", "__absent__")
        bay_count = facade.get("bay_count")
        if bay_index == "__absent__":
            report.fail(
                "G-58",
                f"{where}.bay_index",
                "bay_index is absent; it is a required key and it is what makes the vertical "
                "division per bay -- null for a u axis, a real bay index for a v axis "
                "(07 section 8.3.3)",
            )
            problems += 1
            bay_index = None
        elif family == "u":
            if bay_index is not None:
                report.fail(
                    "G-58",
                    f"{where}.bay_index",
                    f"bay_index is {bay_index!r} on a u axis; a horizontal line runs the whole "
                    "run, so its bay_index is null. A non-null value would make G-61 divide the "
                    "area sum by a bay that the line does not belong to",
                )
                problems += 1
        elif not is_int(bay_index) or not is_int(bay_count) or not 0 <= bay_index < bay_count:
            report.fail(
                "G-58",
                f"{where}.bay_index",
                f"bay_index is {bay_index!r} on a v axis of {facade_id!r}, whose bay_count is "
                f"{bay_count!r}; a v axis belongs to one of its bays, so bay_index is an integer "
                "in 0 .. bay_count - 1",
            )
            problems += 1
            bay_index = None

        span = as_number(facade.get("length_cm") if family == "u" else level.get("height_cm"))
        span_key = "length_cm" if family == "u" else "height_cm"
        if span is None:
            report.fail(
                "G-58",
                f"{where}.offset_cm",
                f"the {family} bound {span_key} of {facade_id!r} level {level_index!r} is not a "
                "number, so this axis cannot be range-checked",
            )
            problems += 1
        elif offset > span + tols.linear:
            report.fail(
                "G-58",
                f"{where}.offset_cm",
                f"offset_cm is {fmt_number(offset)} but a {family} axis of {facade_id!r} level "
                f"{level_index!r} spans 0 .. {fmt_number(span)} {span_key}",
                tols.tol_linear,
            )
            problems += 1
        groups.setdefault((facade_id, level_index, family, bay_index), []).append(
            (ident if isinstance(ident, str) else where, offset)
        )

    for key in sorted(groups, key=lambda item: (str(item[0]), str(item[1]), item[2], str(item[3]))):
        rows = sorted(groups[key], key=lambda row: row[1])
        for earlier, later in zip(rows, rows[1:]):
            if earlier[1] == later[1]:
                report.fail(
                    "G-58",
                    f"{location}::axes",
                    f"{earlier[0]} and {later[0]} share offset_cm {fmt_number(earlier[1])} on "
                    f"({key[0]!r}, level {key[1]!r}, family {key[2]!r}, bay {key[3]!r}); offsets must "
                    "strictly ascend, and two axes at one offset are the same line declared twice",
                    tols.tol_linear,
                )
                problems += 1
            elif close(earlier[1], later[1], tols.linear):
                report.fail(
                    "G-58",
                    f"{location}::axes",
                    f"{earlier[0]} at {fmt_number(earlier[1])} and {later[0]} at "
                    f"{fmt_number(later[1])} on ({key[0]!r}, level {key[1]!r}, family {key[2]!r}, "
                    f"bay {key[3]!r}) are separated by "
                    f"{fmt_number(abs(later[1] - earlier[1]))} cm, which is not more than "
                    f"linear_cm ({tols.linear} cm); two axes within tolerance are one axis, and the "
                    "cell between them is a zero-width rectangle",
                    tols.tol_linear,
                )
                problems += 1

    judged_lists = 0
    for facade_index, facade in enumerate(_p5_rows(doc, "facades")):
        facade_where = f"{location}::facades[{facade_index}]"
        facade_id = facade.get("id")
        length = as_number(facade.get("length_cm"))
        bay_count = facade.get("bay_count")
        for level_index, level in enumerate(
            [row for row in facade.get("levels") or [] if isinstance(row, dict)]
        ):
            level_where = f"{facade_where}.levels[{level_index}]"
            height = as_number(level.get("height_cm"))

            # ---- u_axis_ids: one set for the whole run, ascending by offset ----
            judged_lists += 1
            u_listed = level.get("u_axis_ids")
            u_offsets = _p5_axis_list_offsets(
                u_listed,
                axis_index,
                facade_id,
                level.get("level_index"),
                "u",
                level_where,
                "u_axis_ids",
                report,
                problems,
            )
            if u_offsets is not None:
                problems += _p5_axis_slice_bounds(
                    u_offsets, length, level_where, "u_axis_ids", "the run", report, tols
                )
                problems += _p5_axis_list_completeness(
                    u_offsets,
                    axis_rows,
                    facade_id,
                    level.get("level_index"),
                    "u",
                    level_where,
                    "u_axis_ids",
                    report,
                )

            # ---- v_axis_ids: every v axis, ordered by (bay_index, offset) ----
            judged_lists += 1
            v_listed = level.get("v_axis_ids")
            v_offsets = _p5_axis_list_offsets(
                v_listed,
                axis_index,
                facade_id,
                level.get("level_index"),
                "v",
                level_where,
                "v_axis_ids",
                report,
                problems,
            )
            if v_offsets is None:
                continue
            problems += _p5_axis_list_completeness(
                v_offsets,
                axis_rows,
                facade_id,
                level.get("level_index"),
                "v",
                level_where,
                "v_axis_ids",
                report,
            )
            for earlier, later in zip(v_offsets, v_offsets[1:]):
                if earlier[0] != later[0]:
                    in_order = earlier[0] < later[0]
                else:
                    in_order = later[1] > earlier[1] + tols.linear
                if not in_order:
                    report.fail(
                        "G-58",
                        f"{level_where}.v_axis_ids",
                        f"the list is not ordered by (bay_index, offset): {earlier[2]} at "
                        f"(bay {earlier[0]!r}, {fmt_number(earlier[1])}) is followed by {later[2]} "
                        f"at (bay {later[0]!r}, {fmt_number(later[1])}); bays ascend and each bay's "
                        "own slice ascends by offset",
                        tols.tol_linear,
                    )
                    problems += 1
            declared_bays = sorted({bay for bay, _offset, _id in v_offsets})
            if is_int(bay_count) and declared_bays != list(range(bay_count)):
                report.fail(
                    "G-58",
                    f"{level_where}.v_axis_ids",
                    f"the listed v axes cover bay {declared_bays} but {facade_id!r} declares "
                    f"bay_count {bay_count}, so the vertical division is missing "
                    f"{sorted(set(range(bay_count)) - set(declared_bays))}; the tiling unit is "
                    "(facade, level, bay) and an undeclared bay has no rectangle",
                )
                problems += 1
            for bay in declared_bays:
                problems += _p5_axis_slice_bounds(
                    [row for row in v_offsets if row[0] == bay],
                    height,
                    level_where,
                    "v_axis_ids",
                    f"bay {bay}",
                    report,
                    tols,
                )

        # ---- every bay_offsets_cm[i] has a u 'bay' axis ----
        offsets = _p5_bay_offsets(facade)
        if offsets is None:
            continue
        bay_axes = {
            (axis.get("level_index"), as_number(axis.get("offset_cm")))
            for axis in axis_rows
            if axis.get("kind") == "bay" and axis.get("facade") == facade_id
        }
        for level_index, level in enumerate(
            [row for row in facade.get("levels") or [] if isinstance(row, dict)]
        ):
            level_key = level.get("level_index")
            height = as_number(level.get("height_cm"))
            for offset in offsets:
                if (level_key, offset) not in bay_axes:
                    report.fail(
                        "G-58",
                        f"{facade_where}.bay_offsets_cm",
                        f"bay boundary {fmt_number(offset)} has no matching kind='bay' u axis on "
                        f"({facade_id!r}, level {level_key!r}); every bay boundary is a u axis, "
                        "which is what lets a panel name its edges and G-61 find its bay",
                        tols.tol_linear,
                    )
                    problems += 1

            # ---- every bay has its own level_base and level_top v axis ----
            for bay in range(bay_count) if is_int(bay_count) else []:
                for kind, expected in (("level_base", 0.0), ("level_top", height)):
                    found = any(
                        axis.get("kind") == kind
                        and axis.get("family") == "v"
                        and axis.get("facade") == facade_id
                        and axis.get("level_index") == level_key
                        and axis.get("bay_index") == bay
                        and (
                            expected is None
                            or close(as_number(axis.get("offset_cm")) or 0.0, expected, tols.linear)
                        )
                        for axis in axis_rows
                    )
                    if not found:
                        report.fail(
                            "G-58",
                            f"{facade_where}.levels[{level_index}]",
                            f"no kind={kind!r} v axis on ({facade_id!r}, level {level_key!r}, bay "
                            f"{bay})"
                            + (f" at offset {fmt_number(expected)}" if expected is not None else "")
                            + "; each bay carries its own storey floor and head line, because the "
                            "vertical division is per bay",
                            tols.tol_linear,
                        )
                        problems += 1

    # ---- a bay with no opening contributes exactly its level_base and level_top ----
    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        report.skip(
            "G-58",
            location,
            f"{dimensions.label if dimensions else 'dimensions.json'} is not loaded as a usable "
            "document, and 'a bay with no opening contributes exactly its level_base and "
            "level_top' is read from its openings[]; G-58 will not assume an answer for a file it "
            "cannot read",
        )
        return

    openings_by_bay = _p5_openings_by_bay(dimensions.doc)
    for facade_index, facade in enumerate(_p5_rows(doc, "facades")):
        facade_id = facade.get("id")
        bay_count = facade.get("bay_count")
        if not isinstance(facade_id, str) or not is_int(bay_count):
            continue
        facade_where = f"{location}::facades[{facade_index}]"
        for level_index, level in enumerate(
            [row for row in facade.get("levels") or [] if isinstance(row, dict)]
        ):
            level_key = level.get("level_index")
            for bay in range(bay_count):
                if (facade_id, level_key, bay) in openings_by_bay:
                    continue
                held = [
                    axis
                    for axis in axis_rows
                    if axis.get("family") == "v"
                    and axis.get("facade") == facade_id
                    and axis.get("level_index") == level_key
                    and axis.get("bay_index") == bay
                ]
                if len(held) == 2 and {axis.get("kind") for axis in held} == {
                    "level_base",
                    "level_top",
                }:
                    continue
                report.fail(
                    "G-58",
                    f"{facade_where}.levels[{level_index}]",
                    f"bay {bay} of {facade_id!r} at level {level_key!r} declares no opening in "
                    f"{dimensions.label}, so it contributes exactly its level_base and level_top "
                    f"and is one whole blank panel; this one holds {len(held)} v axis(es) "
                    f"({_p5_ids([str(axis.get('id')) for axis in held])}, kinds "
                    f"{sorted(str(axis.get('kind')) for axis in held)}). A division that belongs "
                    "to another bay's opening does not cross an unopened bay",
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-58",
            location,
            f"{len(axes)} axis(es) match {AXIS_ID_PATTERN}, unique and ascending, carry a known "
            f"family and kind and a bay_index that is null for u and a real bay for v, and sit "
            f"inside 0 .. length_cm / height_cm; offsets strictly ascend and are more than "
            f"{tols.linear} cm apart within every (facade, level_index, family, bay_index); "
            f"{judged_lists} u_axis_ids / v_axis_ids list(s) resolve with the matching facade, "
            "level and family, u ascends by offset from 0 to length_cm, v is ordered by "
            "(bay_index, offset) with each bay's slice running 0 -> height_cm and every "
            "unopened bay holding exactly its level_base and level_top",
        )


def _p5_axis_list_offsets(
    listed: Any,
    axis_index: dict[str, dict],
    facade_id: Any,
    level_index: Any,
    family: str,
    level_where: str,
    key: str,
    report: Report,
    problems: int,
) -> Optional[list[tuple[Any, float, str]]]:
    """``[(bay_index, offset_cm, axis id)]`` for a resolvable list, or None when unusable.

    Every entry must exist, carry the matching facade, level and family, and carry an offset.
    Returns the list in **declared order** -- the ordering itself is the caller's clause, so this
    reader deliberately does not sort.
    """
    if not isinstance(listed, list) or not listed:
        report.fail(
            "G-58",
            f"{level_where}.{key}",
            f"{key} is {listed!r}; it lists the ids that divide this "
            f"{'run' if family == 'u' else 'set of bays' if key == 'v_axis_ids' else 'storey'}",
        )
        return None
    out: list[tuple[Any, float, str]] = []
    for ref in listed:
        axis = axis_index.get(str(ref))
        if axis is None:
            report.fail(
                "G-58", f"{level_where}.{key}", f"{ref!r} is not an axes[].id of this file"
            )
            problems += 1
            continue
        if (
            axis.get("facade") != facade_id
            or axis.get("level_index") != level_index
            or axis.get("family") != family
        ):
            report.fail(
                "G-58",
                f"{level_where}.{key}",
                f"{ref} is ({axis.get('facade')!r}, level {axis.get('level_index')!r}, family "
                f"{axis.get('family')!r}) but this list is ({facade_id!r}, level "
                f"{level_index!r}, family {family!r})",
            )
            problems += 1
            continue
        offset = as_number(axis.get("offset_cm"))
        if offset is None:
            continue
        out.append((axis.get("bay_index"), offset, str(ref)))
    return out or None


def _p5_axis_slice_bounds(
    rows: Sequence[tuple[Any, float, str]],
    span: Optional[float],
    level_where: str,
    key: str,
    slice_name: str,
    report: Report,
    tols: P5Tolerances,
) -> int:
    """A slice must start at 0 and end at its span. Returns the problem count."""
    if not rows:
        return 0
    problems = 0
    if rows[0][1] != 0.0:
        report.fail(
            "G-58",
            f"{level_where}.{key}",
            f"the first axis of {slice_name} is {rows[0][2]} at {fmt_number(rows[0][1])}, not at 0; "
            "a division starts at 0, which is the run origin (u) or the storey floor (v)",
            tols.tol_linear,
        )
        problems += 1
    if span is not None and not close(rows[-1][1], span, tols.linear):
        report.fail(
            "G-58",
            f"{level_where}.{key}",
            f"the last axis of {slice_name} is {rows[-1][2]} at {fmt_number(rows[-1][1])} but its "
            f"full extent is {fmt_number(span)}; the division must reach the far edge or the far "
            "strip is unpanelled",
            tols.tol_linear,
        )
        problems += 1
    return problems


def _p5_axis_list_completeness(
    listed: Sequence[tuple[Any, float, str]],
    axis_rows: Sequence[dict],
    facade_id: Any,
    level_index: Any,
    family: str,
    level_where: str,
    key: str,
    report: Report,
) -> int:
    """The list must name **every** axis of that family, level and facade, and no other."""
    present = {row[2] for row in listed}
    actual = {
        str(axis.get("id"))
        for axis in axis_rows
        if axis.get("facade") == facade_id
        and axis.get("level_index") == level_index
        and axis.get("family") == family
    }
    missing = sorted(actual - present)
    if not missing:
        return 0
    report.fail(
        "G-58",
        f"{level_where}.{key}",
        f"{key} omits {_p5_ids(missing)}; it must list **every** {family} axis of this facade and "
        "level, because an axis the grid does not list is an axis no panel can bracket",
    )
    return len(missing)


# ---- G-59 panel rectangle integrity ----------------------------------------- #



def _g59_panel_rectangles(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-59. Panel ids, a strictly positive rectangle, derived size, bay, layer and centre."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    panels = _p5_array(doc, "panels")
    if panels is None:
        report.fail("G-59", f"{location}::panels", f"panels is {doc.get('panels')!r}, expected an array")
        return

    problems = _scan_id_sequence(panels, "panels", location, report, "G-59", PANEL_ID_RE, PANEL_ID_PATTERN)
    dimensions = session.dimensions
    facades = _p5_facade_index(doc)
    levels = _p5_level_index(doc)
    openings = _p5_index(dimensions.doc, "openings") if isinstance(dimensions and dimensions.doc, dict) else {}
    judged = 0

    for index, panel in enumerate(_p5_rows(doc, "panels")):
        where = f"{location}::panels[{index}]"
        ident = panel.get("id")
        label = f"{location}::{ident}" if isinstance(ident, str) else where
        key = (panel.get("facade"), panel.get("level_index"))
        facade = facades.get(key[0]) if isinstance(key[0], str) else None
        level = levels.get(key)
        if facade is None:
            report.fail(
                "G-59",
                f"{where}.facade",
                f"facade {key[0]!r} is not a facades[].id of this file",
            )
            problems += 1
            continue
        if level is None:
            report.fail(
                "G-59",
                f"{where}.level_index",
                f"level_index {key[1]!r} is not a levels[].level_index of {key[0]!r}",
            )
            problems += 1
            continue
        length = as_number(facade.get("length_cm"))
        height = as_number(level.get("height_cm"))
        elevation = as_number(level.get("elevation_cm"))

        rect = _p5_panel_rect(panel)
        if rect is None:
            report.fail(
                "G-59",
                where,
                f"u_min_cm / u_max_cm / v_min_cm / v_max_cm must be four finite numbers; found "
                f"{panel.get('u_min_cm')!r}, {panel.get('u_max_cm')!r}, {panel.get('v_min_cm')!r}, "
                f"{panel.get('v_max_cm')!r}",
            )
            problems += 1
            continue
        u0, u1, v0, v1 = rect
        judged += 1
        if not u0 < u1 or not v0 < v1:
            report.fail(
                "G-59",
                label,
                f"the rectangle is u {fmt_number(u0)} .. {fmt_number(u1)} and v "
                f"{fmt_number(v0)} .. {fmt_number(v1)}; both ranges must strictly ascend, or the "
                "panel has no area and contributes nothing to the partition",
                tols.tol_linear,
            )
            problems += 1
            continue
        if length is not None and (u0 < -tols.linear or u1 > length + tols.linear):
            report.fail(
                "G-59",
                label,
                f"u {fmt_number(u0)} .. {fmt_number(u1)} is outside 0 .. "
                f"{fmt_number(length)}, the run length of {key[0]!r}",
                tols.tol_linear,
            )
            problems += 1
        if height is not None and (v0 < -tols.linear or v1 > height + tols.linear):
            report.fail(
                "G-59",
                label,
                f"v {fmt_number(v0)} .. {fmt_number(v1)} is outside 0 .. "
                f"{fmt_number(height)}, the storey height of level {key[1]!r}",
                tols.tol_linear,
            )
            problems += 1

        width = as_number(panel.get("width_cm"))
        panel_height = as_number(panel.get("height_cm"))
        judged += 1
        if width is None or not close(width, u1 - u0, tols.linear):
            report.fail(
                "G-59",
                f"{location}::{ident}",
                f"width_cm is {fmt_number(panel.get('width_cm'))} but u_max_cm - u_min_cm is "
                f"{fmt_number(u1 - u0)}",
                tols.tol_linear,
            )
            problems += 1
        if panel_height is None or not close(panel_height, v1 - v0, tols.linear):
            report.fail(
                "G-59",
                f"{location}::{ident}",
                f"height_cm is {fmt_number(panel.get('height_cm'))} but v_max_cm - v_min_cm is "
                f"{fmt_number(v1 - v0)}",
                tols.tol_linear,
            )
            problems += 1

        u_mid = (u0 + u1) / 2.0
        expected_bay = _p5_bay_index(facade.get("bay_width_cm"), u_mid, tols.linear)
        judged += 1
        if expected_bay is None:
            report.fail(
                "G-59",
                f"{label}.bay_index",
                f"the u midpoint {fmt_number(u_mid)} lies in no bay of {key[0]!r} as declared by "
                "bay_width_cm",
                tols.tol_linear,
            )
            problems += 1
        elif panel.get("bay_index") != expected_bay:
            report.fail(
                "G-59",
                f"{label}.bay_index",
                f"bay_index is {panel.get('bay_index')!r} but the u midpoint {fmt_number(u_mid)} "
                f"lies in bay {expected_bay}",
                tols.tol_linear,
            )
            problems += 1

        judged += 1
        if panel.get("layer") != FACADE_SPEC_LAYER:
            report.fail(
                "G-59",
                f"{label}.layer",
                f"layer is {panel.get('layer')!r}; every facade panel carries "
                f"{FACADE_SPEC_LAYER!r}, and layer is data here because it cannot be assigned "
                "from MAXScript",
            )
            problems += 1

        opening_ref = panel.get("opening_ref")
        if opening_ref is not None:
            judged += 1
            opening = openings.get(str(opening_ref))
            if opening is None:
                report.fail(
                    "G-59",
                    f"{label}.opening_ref",
                    f"opening_ref {opening_ref!r} is null or a dimensions.openings[].id; "
                    f"{dimensions.label if dimensions else 'dimensions.json'} declares "
                    f"{len(openings)} of them and this one is not among them",
                )
                problems += 1
            elif (
                opening.get("facade") != panel.get("facade")
                or opening.get("level_index") != panel.get("level_index")
                or opening.get("bay_index") != panel.get("bay_index")
            ):
                report.fail(
                    "G-59",
                    f"{label}.opening_ref",
                    f"opening_ref {opening_ref} is ({opening.get('facade')!r}, level "
                    f"{opening.get('level_index')!r}, bay {opening.get('bay_index')!r}) but the "
                    f"panel is ({panel.get('facade')!r}, level {panel.get('level_index')!r}, bay "
                    f"{panel.get('bay_index')!r}); an opening is realised only by a panel on its "
                    "own facade, level and bay",
                )
                problems += 1

        centre = _finite_triple(panel.get("centre_cm"))
        start = _finite_pair(facade.get("start_corner_cm"))
        unit = _p5_run_unit(facade)
        judged += 1
        if centre is None or start is None or unit is None or elevation is None:
            report.fail(
                "G-59",
                f"{label}.centre_cm",
                f"centre_cm is {panel.get('centre_cm')!r}; the derived value needs three finite "
                "numbers here and finite start_corner_cm / end_corner_cm / length_cm and "
                "levels[].elevation_cm to derive them from",
            )
            problems += 1
        else:
            expected = [
                start[0] + unit[0] * u_mid,
                start[1] + unit[1] * u_mid,
                elevation + (v0 + v1) / 2.0,
            ]
            if not all(close(a, b, tols.linear) for a, b in zip(centre, expected)):
                report.fail(
                    "G-59",
                    f"{label}.centre_cm",
                    f"centre_cm is {_short(list(centre))} but start_corner_cm + run_unit * "
                    f"{fmt_number(u_mid)} and elevation_cm + v_mid recompute to "
                    f"{_short([round(value, 6) for value in expected])}",
                    tols.tol_linear,
                )
                problems += 1

    host_refs = [
        str(panel.get("host_ref"))
        for panel in _p5_rows(doc, "panels")
        if panel.get("host_ref") is not None
    ]
    if host_refs:
        massing = session.massing
        if massing is None or not isinstance(massing.doc, dict):
            report.skip(
                "G-59",
                f"{location}::panels",
                f"{len(host_refs)} panel(s) carry a host_ref that names a "
                f"{massing.label if massing else 'massing.json'} element, and that file is not "
                "loaded as a usable document; G-59 will not assume an answer for a file it "
                "cannot read",
            )
        else:
            element_ids = {element.get("id") for element in _p5_rows(massing.doc, "elements")}
            unresolvable = sorted({ref for ref in host_refs if ref not in element_ids})
            problems += len(unresolvable)
            for ref in unresolvable[:P5_ID_LIST_LIMIT]:
                report.fail(
                    "G-59",
                    f"{location}::panels",
                    f"host_ref {ref!r} is not a {massing.label} elements[].id",
                )

    if problems == 0:
        report.ok(
            "G-59",
            location,
            f"{len(panels)} panel(s) match {PANEL_ID_PATTERN}, unique and ascending; every "
            f"rectangle strictly ascends in u and v inside 0 .. length_cm x 0 .. height_cm, "
            f"width_cm and height_cm equal their differences, bay_index is the bay holding the u "
            f"midpoint, layer is {FACADE_SPEC_LAYER!r}, every opening_ref names an opening on "
            f"the same facade, level and bay, and every centre_cm recomputes from "
            f"start_corner_cm + run_unit * u_mid ({judged} comparisons)",
        )


# ---- G-60 panel edges lie on axes ------------------------------------------- #


def _g60_panel_edges(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-60. A panel's four edges are named axes, and ``full_height`` agrees with its v range."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    panels = _p5_rows(doc, "panels")
    axes = _p5_index(doc, "axes")
    levels = _p5_level_index(doc)

    problems = 0
    judged = 0
    for panel in panels:
        ident = panel.get("id")
        label = f"{location}::{ident}" if isinstance(ident, str) else f"{location}::panels"
        rect = _p5_panel_rect(panel)
        if rect is None:
            continue  # G-59 already named the shape
        level = levels.get((panel.get("facade"), panel.get("level_index")))
        if level is None:
            continue  # G-59 already named the level
        height = as_number(level.get("height_cm"))

        for key, family, edge in (
            ("u_axis_min", "u", "u_min_cm"),
            ("u_axis_max", "u", "u_max_cm"),
            ("v_axis_min", "v", "v_min_cm"),
            ("v_axis_max", "v", "v_max_cm"),
        ):
            judged += 1
            ref = panel.get(key)
            axis = axes.get(str(ref))
            if axis is None:
                report.fail(
                    "G-60",
                    f"{label}.{key}",
                    f"{ref!r} is not an axes[].id of this file; every panel edge lies on an axis, "
                    "because offsets live only in axes[]",
                )
                problems += 1
                continue
            if (
                axis.get("facade") != panel.get("facade")
                or axis.get("level_index") != panel.get("level_index")
                or axis.get("family") != family
            ):
                report.fail(
                    "G-60",
                    f"{label}.{key}",
                    f"{ref} is ({axis.get('facade')!r}, level {axis.get('level_index')!r}, family "
                    f"{axis.get('family')!r}) but the panel needs a {family!r} axis of "
                    f"({panel.get('facade')!r}, level {panel.get('level_index')!r})",
                )
                problems += 1
                continue
            offset = as_number(axis.get("offset_cm"))
            expected = rect[("u_min_cm", "u_max_cm", "v_min_cm", "v_max_cm").index(edge)]
            if offset is None or not close(offset, expected, tols.linear):
                report.fail(
                    "G-60",
                    f"{label}.{key}",
                    f"{ref} is at offset {fmt_number(offset)} but {edge} is "
                    f"{fmt_number(expected)}; a panel edge lies ON an axis",
                    tols.tol_linear,
                )
                problems += 1

        judged += 1
        u_min_axis = axes.get(str(panel.get("u_axis_min")))
        u_max_axis = axes.get(str(panel.get("u_axis_max")))
        low = as_number(u_min_axis.get("offset_cm")) if u_min_axis else None
        high = as_number(u_max_axis.get("offset_cm")) if u_max_axis else None
        if low is not None and high is not None and low > high:
            report.fail(
                "G-60",
                label,
                f"u_axis_min {panel.get('u_axis_min')!r} is at {fmt_number(low)} and u_axis_max "
                f"{panel.get('u_axis_max')!r} at {fmt_number(high)}; the bracket runs the other way",
                tols.tol_linear,
            )
            problems += 1

        full_height = panel.get("full_height")
        judged += 1
        if not isinstance(full_height, bool):
            report.fail(
                "G-60",
                f"{label}.full_height",
                f"full_height is {full_height!r}; it is a bool",
            )
            problems += 1
            continue
        v0, v1 = rect[2], rect[3]
        if full_height:
            if height is None or not close(v0, 0.0, tols.linear) or not close(v1, height, tols.linear):
                report.fail(
                    "G-60",
                    label,
                    f"full_height is true but the panel spans v {fmt_number(v0)} .. "
                    f"{fmt_number(v1)}; a full-height panel is not cut by the v grid and spans 0 "
                    f".. {fmt_number(height)}",
                    tols.tol_linear,
                )
                problems += 1
        elif height is not None and close(v0, 0.0, tols.linear) and close(v1, height, tols.linear):
            report.fail(
                "G-60",
                label,
                f"full_height is false yet the panel spans the whole storey (v 0 .. "
                f"{fmt_number(height)}); the flag and the extent contradict each other",
                tols.tol_linear,
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-60",
            location,
            f"all four edge axis ids of {len(panels)} panel(s) resolve, carry the panel's facade, "
            "level and family, and sit at u_min_cm / u_max_cm / v_min_cm / v_max_cm; u_axis_min "
            "brackets u_axis_max; full_height is true exactly for panels spanning 0 .. height_cm "
            f"({judged} comparisons)",
        )


# ---- G-61 complete partition ------------------------------------------------ #


def _g61_partition(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-61. The panels **partition** every bay of every level, and through them every level.

    Two area sums and three positional tests, because the tiling unit is ``(facade, level, bay)``
    and each catches something the others cannot:

    * per ``(facade, level, bay)``, Σ areas ``== bay_width_cm[b] x height_cm`` -- the unit that is
      actually tiled;
    * per ``(facade, level)``, the same sum ``== length_cm x height_cm`` -- catches a bay whose
      area happens to cancel out against its neighbour;
    * no two panels on one facade and level overlap in their interiors -- catches a duplicate
      balanced by a gap, which both area sums miss;
    * every panel inside its bay's rectangle, and its ``u`` range inside
      ``[bay_offsets_cm[b], bay_offsets_cm[b+1]]`` -- catches a panel in the right storey on the
      wrong structural bay, which is exactly what a facade-wide v grid produces.

    Overlap is judged on ``> linear_cm`` in **both** axes: two panels sharing an edge tile, they do
    not overlap, and two overlapping in only one axis are adjacent strips.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    panels = _p5_array(doc, "panels")
    if panels is None:
        report.fail(
            "G-61", f"{location}::panels", f"panels is {doc.get('panels')!r}, expected an array"
        )
        return

    facades = _p5_facade_index(doc)
    levels = _p5_level_index(doc)
    grouped: dict[tuple[str, int, int], list[tuple[str, tuple[float, float, float, float]]]] = {}
    for panel in _p5_rows(doc, "panels"):
        rect = _p5_panel_rect(panel)
        if rect is None:
            continue  # G-59 already named the shape
        facade_id = panel.get("facade")
        level_index = panel.get("level_index")
        bay_index = panel.get("bay_index")
        if not isinstance(facade_id, str) or not is_int(level_index) or not is_int(bay_index):
            continue  # G-59 already named the panel
        ident = panel.get("id")
        grouped.setdefault((facade_id, level_index, bay_index), []).append(
            (
                ident
                if isinstance(ident, str)
                else f"a panel of {facade_id} level {level_index} bay {bay_index}",
                rect,
            )
        )

    problems = 0
    judged_levels = 0
    judged_bays = 0
    for (facade_id, level_index) in _p5_level_keys(doc):
        facade = facades.get(facade_id)
        level = levels.get((facade_id, level_index))
        if facade is None or level is None:
            continue  # G-57/G-59 already named the facade or the level
        length = as_number(facade.get("length_cm"))
        height = as_number(level.get("height_cm"))
        bay_widths = _numbers(facade.get("bay_width_cm"))
        bay_offsets = _p5_bay_offsets(facade)
        bay_count = facade.get("bay_count")
        where = f"{location}::{facade_id}/level {level_index}"
        judged_levels += 1

        level_rows = [
            row
            for (facade_key, level_key, _bay), rows in grouped.items()
            if facade_key == facade_id and level_key == level_index
            for row in rows
        ]
        if not level_rows:
            report.fail(
                "G-61",
                where,
                f"the file declares a level on {facade_id!r} and carries no panel for it; a gridded "
                "level with no panel is a hole in the facade",
            )
            problems += 1
            continue
        if length is None or height is None:
            report.fail(
                "G-61",
                where,
                f"length_cm ({fmt_number(facade.get('length_cm'))}) or height_cm "
                f"({fmt_number(level.get('height_cm'))}) is not a number, so the rectangle the "
                "panels must tile is undefined",
            )
            problems += 1
            continue

        # ---- per (facade, level): the whole run ----
        expected_area = length * height / 10000.0
        total = sum(polygon_area_m2(_p5_panel_ring(rect)) for _ident, rect in level_rows)
        if not close(total, expected_area, tols.area):
            report.fail(
                "G-61",
                where,
                f"the {len(level_rows)} panel(s) on this facade and level sum to {total:.6g} m2 but "
                f"the facade rectangle is {fmt_number(length)} x {fmt_number(height)} cm = "
                f"{expected_area:.6g} m2; the grid must be a partition, so a duplicated or a "
                "dropped panel shows up here as an area that does not add up",
                tols.tol_area,
            )
            problems += 1

        # ---- per (facade, level, bay): the unit that is actually tiled ----
        for bay in range(bay_count) if is_int(bay_count) else []:
            judged_bays += 1
            rows = grouped.get((facade_id, level_index, bay), [])
            bay_where = f"{location}::{facade_id}/level {level_index}/bay {bay}"
            bay_width = as_number(bay_widths[bay]) if bay_widths and bay < len(bay_widths) else None
            if bay_width is None:
                report.fail(
                    "G-61",
                    bay_where,
                    f"bay_width_cm[{bay}] is {fmt_number(bay_widths[bay]) if bay_widths else None}; "
                    "the bay's rectangle is undefined, so there is nothing to tile",
                )
                problems += 1
                continue
            if not rows:
                report.fail(
                    "G-61",
                    bay_where,
                    f"no panel sits in bay {bay} of {facade_id!r} level {level_index}, so the "
                    f"{fmt_number(bay_width)} cm of structural bay is unpanelled",
                )
                problems += 1
                continue
            bay_area = bay_width * height / 10000.0
            bay_total = sum(polygon_area_m2(_p5_panel_ring(rect)) for _ident, rect in rows)
            if not close(bay_total, bay_area, tols.area):
                report.fail(
                    "G-61",
                    bay_where,
                    f"the {len(rows)} panel(s) in this bay sum to {bay_total:.6g} m2 but the bay "
                    f"rectangle is {fmt_number(bay_width)} x {fmt_number(height)} cm = "
                    f"{bay_area:.6g} m2; the tiling unit is (facade, level, bay), so a missing or "
                    "a duplicated cell shows up here even when the level total happens to balance",
                    tols.tol_area,
                )
                problems += 1

            span = (
                (bay_offsets[bay], bay_offsets[bay + 1])
                if bay_offsets and bay + 1 < len(bay_offsets)
                else None
            )
            for ident, (u0, u1, v0, v1) in rows:
                outside: list[str] = []
                if v0 < -tols.linear or v1 > height + tols.linear:
                    outside.append(f"v {fmt_number(v0)} .. {fmt_number(v1)} is outside 0 .. "
                                   f"{fmt_number(height)}")
                if span is not None and (
                    u0 < span[0] - tols.linear or u1 > span[1] + tols.linear
                ):
                    outside.append(
                        f"u {fmt_number(u0)} .. {fmt_number(u1)} is outside this bay's "
                        f"[{fmt_number(span[0])}, {fmt_number(span[1])}]"
                    )
                if not outside:
                    continue
                problems += 1
                report.fail(
                    "G-61",
                    f"{location}::{ident}",
                    f"panel {ident} claims bay {bay} of {facade_id!r} but " + "; ".join(outside)
                    + "; a panel sits inside its own bay's rectangle, whose u extent is that bay's "
                    f"share of [0, {fmt_number(length)}]",
                    tols.tol_linear,
                )

        # ---- no interior overlap on the same facade and level ----
        clashes: list[str] = []
        for first in range(len(level_rows)):
            ident_a, rect_a = level_rows[first]
            for ident_b, rect_b in level_rows[first + 1 :]:
                overlap_u = min(rect_a[1], rect_b[1]) - max(rect_a[0], rect_b[0])
                overlap_v = min(rect_a[3], rect_b[3]) - max(rect_a[2], rect_b[2])
                if overlap_u > tols.linear and overlap_v > tols.linear:
                    clashes.append(f"{ident_a}/{ident_b}")
        problems += len(clashes)
        for clash in clashes[:P5_ID_LIST_LIMIT]:
            report.fail(
                "G-61",
                where,
                f"panels {clash} overlap in their interiors by more than {tols.linear} cm in both "
                f"u and v; {len(clashes)} overlapping pair(s) in total on this facade and level, and "
                "a partition cannot double-cover a strip",
                tols.tol_linear,
            )

    if problems == 0:
        report.ok(
            "G-61",
            location,
            f"the panels partition the grid: panel areas sum to bay_width_cm[b] x height_cm within "
            f"area_m2 for each of the {judged_bays} declared (facade, level_index, bay_index) "
            f"group(s) and to length_cm x height_cm for each of the {judged_levels} "
            "(facade, level_index) group(s); no two panels on the same facade and level overlap in "
            "their interiors by more than linear_cm in both axes; and every panel lies inside its "
            "own bay's rectangle, with its u range inside "
            "[bay_offsets_cm[b], bay_offsets_cm[b + 1]]",
        )


# ---- G-62 one opening, one panel --------------------------------------------- #


def _g62_opening_reconciliation(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-62. Every opening is realised by **exactly one** panel, and that panel is its rectangle.

    **Strictly one, never "one or more".** The earlier wording of this rule was "tiles": an opening
    split by the v grid into several panels counted as correct. That was written to accommodate a
    facade-wide v grid, and the measurement killed the grid: a union of every opening's sill and
    head across the facade at that level imposes each bay's head line on **every other bay**, so an
    entrance with ``head_cm = 260`` put a horizontal division through a window running ``90 -> 270``
    and produced a ``180 x 10 cm`` ``punched_window`` -- a ten-centimetre ribbon of glass sitting
    ten centimetres below the window head it belongs to.

    The fix is at the root (07 section 8.3.3: ``bay_index`` on every axis, and the v division per
    bay), and this rule is the assertion that keeps it fixed: an opening's own sill and head are
    its *only* horizontal lines, so no cell can straddle an opening edge and two panels for one
    opening is not a partition nicety -- it is that same sliver.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    dimensions = session.dimensions
    if dimensions is None or not isinstance(dimensions.doc, dict):
        report.skip(
            "G-62",
            location,
            "dimensions.json is not loaded as a usable document; this rule reconciles the panels "
            "against its openings[], so it will not assume an answer for a file it cannot read",
        )
        return
    dimensions_label = dimensions.label
    panels = _p5_rows(doc, "panels")
    panel_types = _p5_panel_type_index(doc)

    referencing: dict[str, list[dict]] = {}
    for panel in panels:
        ref = panel.get("opening_ref")
        if isinstance(ref, str):
            referencing.setdefault(ref, []).append(panel)

    problems = 0
    judged = 0
    for index, opening in enumerate(_p5_rows(dimensions.doc, "openings")):
        ident = opening.get("id")
        if not isinstance(ident, str):
            continue
        where = f"{dimensions_label}::openings[{index}]"
        position = as_number(opening.get("position_cm"))
        width = as_number(opening.get("width_cm"))
        sill = as_number(opening.get("sill_cm"))
        head = as_number(opening.get("head_cm"))
        judged += 1
        if None in (position, width, sill, head):
            report.fail(
                "G-62",
                where,
                f"opening {ident} needs finite position_cm, width_cm, sill_cm and head_cm; found "
                f"{fmt_number(opening.get('position_cm'))}, {fmt_number(opening.get('width_cm'))}, "
                f"{fmt_number(opening.get('sill_cm'))}, {fmt_number(opening.get('head_cm'))}",
            )
            problems += 1
            continue

        owners = referencing.get(ident, [])
        if not owners:
            report.fail(
                "G-62",
                where,
                f"opening {ident} ({opening.get('facade')!r}, level "
                f"{opening.get('level_index')!r}, bay {opening.get('bay_index')!r}, "
                f"{opening.get('type')!r}) is referenced by no panel; every declared opening is "
                "realised by exactly one panel, and a panel with a null opening_ref is not it",
            )
            problems += 1
            continue

        for extra in owners[1:]:
            report.fail(
                "G-62",
                f"{location}::{extra.get('id')}",
                f"opening {ident} is referenced by {len(owners)} panels ({_p5_ids([str(owner.get('id')) for owner in owners])}); "
                "07 G-62 says exactly one. The vertical division is per bay, so an opening's own "
                "sill and head are its only horizontal lines and nothing can split it -- two panels "
                "for one opening is a ribbon of glass, which is what a facade-wide v grid produced",
            )
        problems += len(owners) - 1

        panel = owners[0]
        pid = str(panel.get("id"))
        label = f"{location}::{pid}"
        if (
            panel.get("facade") != opening.get("facade")
            or panel.get("level_index") != opening.get("level_index")
            or panel.get("bay_index") != opening.get("bay_index")
        ):
            report.fail(
                "G-62",
                f"{label}.opening_ref",
                f"panel {pid} realises {ident} but sits on ({panel.get('facade')!r}, level "
                f"{panel.get('level_index')!r}, bay {panel.get('bay_index')!r}) where the opening is "
                f"({opening.get('facade')!r}, level {opening.get('level_index')!r}, bay "
                f"{opening.get('bay_index')!r}); an opening is realised only by a panel on its own "
                "facade, level and bay",
            )
            problems += 1

        rect = _p5_panel_rect(panel)
        if rect is None:
            report.fail(
                "G-62",
                label,
                f"panel {pid} has no finite u_min_cm / u_max_cm / v_min_cm / v_max_cm, so it "
                f"cannot be the rectangle of {ident}",
            )
            problems += 1
            continue
        for edge, expected, meaning in (
            ("u_min_cm", position - width / 2, "position_cm - width_cm / 2"),
            ("u_max_cm", position + width / 2, "position_cm + width_cm / 2"),
            ("v_min_cm", sill, "sill_cm"),
            ("v_max_cm", head, "head_cm"),
        ):
            actual = rect[("u_min_cm", "u_max_cm", "v_min_cm", "v_max_cm").index(edge)]
            if close(actual, expected, tols.linear):
                continue
            report.fail(
                "G-62",
                label,
                f"{edge} is {fmt_number(actual)} but opening {ident} is {fmt_number(expected)} "
                f"({meaning}); the one panel that realises an opening is the opening's whole "
                "rectangle",
                tols.tol_linear,
            )
            problems += 1

        entry = panel_types.get(str(panel.get("kind")))
        opening_types = entry.get("opening_types") if isinstance(entry, dict) else None
        if not isinstance(opening_types, list) or opening.get("type") not in opening_types:
            report.fail(
                "G-62",
                label,
                f"panel {pid} has kind {panel.get('kind')!r}, whose opening_types "
                f"{_short(opening_types)} do not list the {opening.get('type')!r} opening {ident} "
                "hosts; a panel may only realise an opening its kind declares",
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-62",
            location,
            f"all {judged} openings in {dimensions_label} are referenced by **exactly one** panel, "
            "and that panel is on the opening's own facade, level and bay, spans exactly "
            "[position_cm - width_cm / 2, position_cm + width_cm / 2] in u and exactly "
            "[sill_cm, head_cm] in v within linear_cm, and carries a kind whose "
            "panel_types[].opening_types lists the opening type. Strictly one, never one or more: a "
            "per-bay vertical division means nothing can split an opening",
        )


# ---- G-63 panel-kind vocabulary and layer ----------------------------------- #



def _g63_panel_vocabulary(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-63. The panel-kind vocabulary: closed, declared, used, and served."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    entries = _p5_array(doc, "panel_types")
    panels = _p5_array(doc, "panels")
    if entries is None:
        report.fail(
            "G-63",
            f"{location}::panel_types",
            f"panel_types is {doc.get('panel_types')!r}, expected an array",
        )
        return
    if panels is None:
        report.fail(
            "G-63", f"{location}::panels", f"panels is {doc.get('panels')!r}, expected an array"
        )
        return

    problems = 0
    declared: dict[str, dict] = {}
    for index, entry in enumerate(_p5_rows(doc, "panel_types")):
        where = f"{location}::panel_types[{index}]"
        kind = entry.get("kind")
        if not isinstance(kind, str) or not kind:
            report.fail(
                "G-63",
                f"{where}.kind",
                f"kind is {kind!r}; panel_types[] declares the kinds a panel may take",
            )
            problems += 1
            continue
        if kind in declared:
            report.fail(
                "G-63",
                f"{where}.kind",
                f"kind {kind!r} is already declared; panel_types[].kind is unique",
            )
            problems += 1
            continue
        declared[kind] = entry

        glazed = entry.get("glazed")
        frame_member = entry.get("frame_member")
        if not isinstance(glazed, bool) or not isinstance(frame_member, bool):
            report.fail(
                "G-63",
                where,
                f"glazed is {glazed!r} and frame_member is {frame_member!r}; both are bools",
            )
            problems += 1
            continue
        role = entry.get("material_role")
        expected_role = "glazing" if glazed else ("frame" if frame_member else "opaque")
        if role not in FACADE_MATERIAL_ROLES:
            report.fail(
                "G-63",
                f"{where}.material_role",
                f"material_role is {role!r}; it is one of {', '.join(FACADE_MATERIAL_ROLES)} -- a "
                "role P7 resolves, never a material class and never a MAXScript or plugin name",
            )
            problems += 1
        elif role != expected_role:
            report.fail(
                "G-63",
                f"{where}.material_role",
                f"material_role is {role!r} but glazed={glazed} and frame_member={frame_member} "
                f"require {expected_role!r}",
            )
            problems += 1
        opening_types = entry.get("opening_types")
        if not isinstance(opening_types, list):
            report.fail(
                "G-63",
                f"{where}.opening_types",
                f"opening_types is {opening_types!r}, expected an array (empty when the kind hosts "
                "no opening)",
            )
            problems += 1
        elif bool(opening_types) != glazed:
            report.fail(
                "G-63",
                f"{where}.opening_types",
                f"opening_types holds {len(opening_types)} entry(ies) while glazed is {glazed}; a "
                "kind that hosts an opening is glazed and a kind that hosts none is not",
            )
            problems += 1

    if len(declared) > FACADE_PANEL_KIND_CEILING:
        report.fail(
            "G-63",
            f"{location}::panel_types",
            f"{len(declared)} distinct kind(s) are declared against a ceiling of "
            f"{FACADE_PANEL_KIND_CEILING} (07 section 8.3); the vocabulary is data, so a project "
            "declares the kinds it uses, but it may not grow past the reserved names",
        )
        problems += 1

    used: dict[str, int] = {}
    undeclared: list[str] = []
    for index, panel in enumerate(_p5_rows(doc, "panels")):
        kind = panel.get("kind")
        if not isinstance(kind, str):
            report.fail(
                "G-63",
                f"{location}::panels[{index}].kind",
                f"kind is {kind!r}; every panel names a declared panel_types[].kind",
            )
            problems += 1
            continue
        used[kind] = used.get(kind, 0) + 1
        if kind not in declared and kind not in undeclared:
            undeclared.append(kind)
    problems += len(undeclared)
    for kind in undeclared[:P5_ID_LIST_LIMIT]:
        report.fail(
            "G-63",
            f"{location}::panels",
            f"panels[].kind {kind!r} is not declared in panel_types[]; a kind nothing declares "
            f"cannot be resolved by a builder ({len(undeclared)} undeclared kind(s) in total)",
        )

    unused = [kind for kind in declared if kind not in used]
    problems += len(unused)
    for kind in unused[:P5_ID_LIST_LIMIT]:
        report.fail(
            "G-63",
            f"{location}::panel_types",
            f"declared kind {kind!r} is used by no panel; a declared kind with no panel is a "
            f"vocabulary entry with no referent ({len(unused)} unused kind(s) in total)",
        )

    registry = session.components_registry
    served_problems = 0
    if registry is None or not isinstance(registry.doc, dict):
        _p5_missing_registry_row(
            "G-63",
            f"{location}::panel_types",
            report,
            "whether a declared panel kind is served by a component",
        )
    else:
        served: dict[str, int] = {}
        for component in _p5_rows(registry.doc, "components"):
            for kind in component.get("serves_panel_kinds") or []:
                served[str(kind)] = served.get(str(kind), 0) + 1
        unserved = [kind for kind in declared if kind not in served]
        served_problems = len(unserved)
        for kind in unserved[:P5_ID_LIST_LIMIT]:
            report.fail(
                "G-63",
                f"{location}::panel_types",
                f"declared kind {kind!r} is served by no component in {registry.label}; a panel "
                "kind no block can realise has nowhere to go in P6 "
                f"({len(unserved)} unserved kind(s) in total)",
            )

    problems += served_problems
    if problems == 0:
        note = (
            f"{len(declared)} declared kind(s) inside the ceiling of {FACADE_PANEL_KIND_CEILING}, "
            f"all used by at least one of the {len(panels)} panel(s), every panel kind declared, "
            "material_role consistent with glazed / frame_member and opening_types non-empty "
            "exactly when glazed"
        )
        if registry is not None and isinstance(registry.doc, dict):
            note += ", and every declared kind served by at least one component"
        report.ok("G-63", location, note)


# ---- G-64 grid provenance ---------------------------------------------------- #


def _g64_grid_provenance(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-64. Origins coverage, and provenance that recomputes rather than asserts.

    **The "every origin is derived" clause is scoped to ``facade_grids.json``,** because P5
    invents nothing there: ``dimensions.json`` and ``massing.json`` have already resolved
    ``given``, ``assumed`` and ``conflict``. ``components_registry.json`` is the exception and
    the schema says so -- its ``defaults.panel_thickness_cm`` and ``defaults.joint_width_cm``
    are ``assumed`` with ledger entries ``A-023`` / ``A-024``, because both are reference-only
    conventions in ``09-defaults.md`` with a declared range and no source in the brief. So the
    clause runs on the grid file and is skipped, with that reason, on the registry.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    problems, leaves, entries = _check_origins_coverage(
        doc, record.spec, location, report, "G-64"
    )
    origins = doc.get("origins")
    if not isinstance(origins, dict):
        return  # the coverage pass already reported the shape

    all_derived = record.name == "facade_grids"
    derived = 0
    excused = 0
    for entry in sorted(origins):
        value = origins[entry]
        if not isinstance(value, dict):
            continue  # the coverage pass already reported the shape
        origin = value.get("origin")
        if origin not in ORIGIN_VALUES:
            report.fail(
                "G-64",
                f"{location}::{entry}",
                f"origin {origin!r} is not one of {', '.join(ORIGIN_VALUES)}; G-10 pairs the "
                "value with its ledger entry",
            )
            problems += 1
            continue
        if origin == "derived":
            derived += 1
            if not isinstance(value.get("derives_from"), list) or not value.get("derives_from"):
                report.fail(
                    "G-64",
                    f"{location}::{entry}",
                    "origin=derived requires a non-empty derives_from naming the paths this value "
                    "was computed from",
                )
                problems += 1
        elif all_derived:
            report.fail(
                "G-64",
                f"{location}::{entry}",
                f"origin is {origin!r}, not 'derived'; P5 invents nothing in facade_grids.json, "
                "because dimensions.json and massing.json already resolved given, assumed and "
                "conflict. This clause is scoped to facade_grids.json: in components_registry.json "
                "the two assumed defaults are the documented exception (A-023 / A-024)",
            )
            problems += 1
        else:
            excused += 1

    dimensions = session.dimensions
    massing = session.massing
    inputs = doc.get("origin_inputs")
    cross_documents = [
        other.doc
        for other in (dimensions, massing)
        if other is not None and isinstance(other.doc, dict)
    ]
    cross_names = ", ".join(
        other.label
        for other in (dimensions, massing)
        if other is not None and isinstance(other.doc, dict)
    )
    traced = 0
    for entry in sorted(origins):
        value = origins[entry]
        if not isinstance(value, dict) or value.get("origin") != "derived":
            continue
        for source in value.get("derives_from") or []:
            text = str(source)
            if resolve(doc, text)[0] or any(resolve(document, text)[0] for document in cross_documents):
                traced += 1
            else:
                report.fail(
                    "G-64",
                    f"{location}::{entry}",
                    f"derives_from path {text!r} resolves neither in this file nor in "
                    f"{cross_names or '(no sibling file is loaded)'}",
                )
                problems += 1

    checked_inputs = 0
    listed: list[str] = []
    for item in inputs if isinstance(inputs, list) else []:
        if not isinstance(item, str):
            report.fail(
                "G-64",
                f"{location}::origin_inputs",
                f"origin_inputs entry {item!r} is not a path string",
            )
            problems += 1
            continue
        listed.append(item)
    for text in listed:
        if any(resolve(document, text)[0] for document in cross_documents):
            checked_inputs += 1
        else:
            report.fail(
                "G-64",
                f"{location}::origin_inputs",
                f"path {text!r} resolves in neither {cross_names or '(no sibling file is loaded)'}; "
                "an origin input names a path this stage actually read",
            )
            problems += 1

    if problems == 0:
        note = (
            f"{leaves} leaves, {entries} entries, exactly-one coverage; {derived} derived with "
            f"{traced} resolving derives_from paths; {checked_inputs} origin_inputs path(s) resolve"
        )
        if all_derived:
            note += " in dimensions.json or massing.json, and every origin is derived"
        else:
            note += (
                " in dimensions.json or massing.json. The all-derived clause is scoped to "
                f"facade_grids.json: {excused} assumed entry(ies) here are the documented "
                "defaults (A-023 / A-024), not invented geometry"
            )
        report.ok("G-64", location, note)


# ---- G-65 component identity ------------------------------------------------- #


def _g65_component_identity(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-65. ``CMP-`` / ``FAM-`` identity, clean unique names, and the family partition."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    components = _p5_array(doc, "components")
    families = _p5_array(doc, "families")
    if components is None:
        report.fail(
            "G-65",
            f"{location}::components",
            f"components is {doc.get('components')!r}, expected an array",
        )
        components = []
    if families is None:
        report.fail(
            "G-65",
            f"{location}::families",
            f"families is {doc.get('families')!r}, expected an array",
        )
        families = []

    problems = _scan_id_sequence(
        components, "components", location, report, "G-65", COMPONENT_ID_RE, COMPONENT_ID_PATTERN
    )
    problems += _scan_id_sequence(
        families, "families", location, report, "G-65", FAMILY_ID_RE, FAMILY_ID_PATTERN
    )

    kinds = {
        entry["kind"] for entry in _p5_rows(doc, "component_types") if isinstance(entry.get("kind"), str)
    }
    names: dict[str, str] = {}
    for index, component in enumerate(_p5_rows(doc, "components")):
        where = f"{location}::components[{index}]"
        ident = component.get("id")
        label = f"{location}::{ident}" if isinstance(ident, str) else where
        name = component.get("name")
        if not isinstance(name, str) or not name:
            report.fail(
                "G-65",
                f"{where}.name",
                f"name is {name!r}; it is the node name P6 places, so it is a non-empty string",
            )
            problems += 1
        elif "-" in name:
            report.fail(
                "G-65",
                f"{where}.name",
                f"name {name!r} contains '-'; a hyphen in a node name reads as subtraction in "
                "emitted MAXScript (11 rule N1), so PNL-001 becomes node PNL_001",
            )
            problems += 1
        elif name in names:
            report.fail(
                "G-65",
                f"{where}.name",
                f"name {name!r} is already used by {names[name]}; two components sharing a node "
                "name would collide in the scene",
            )
            problems += 1
        elif isinstance(ident, str):
            names[name] = ident

        if component.get("kind") not in kinds:
            report.fail(
                "G-65",
                f"{label}.kind",
                f"kind is {component.get('kind')!r}; it is null or one of "
                f"{_p5_ids(sorted(kinds))} (07 section 8.4.3)",
            )
            problems += 1
        if component.get("layer") != FACADE_SPEC_LAYER:
            report.fail(
                "G-65",
                f"{label}.layer",
                f"layer is {component.get('layer')!r}; every facade component carries "
                f"{FACADE_SPEC_LAYER!r}",
            )
            problems += 1

    declared = {entry["id"] for entry in _p5_rows(doc, "components") if isinstance(entry.get("id"), str)}
    placements: dict[str, list[str]] = {}
    for index, family in enumerate(_p5_rows(doc, "families")):
        where = f"{location}::families[{index}]"
        ident = family.get("id")
        name = family.get("name")
        if not isinstance(name, str) or not name:
            report.fail(
                "G-65",
                f"{where}.name",
                f"name is {name!r}; a family name is a non-empty string",
            )
            problems += 1
        elif "-" in name:
            report.fail(
                "G-65",
                f"{where}.name",
                f"name {name!r} contains '-'; a hyphen in a node name reads as subtraction in "
                "emitted MAXScript (11 rule N1)",
            )
            problems += 1
        if family.get("substitution") != COMPONENT_SUBSTITUTION:
            report.fail(
                "G-65",
                f"{where}.substitution",
                f"substitution is {family.get('substitution')!r}; 07 section 8.5 declares exactly "
                f"{COMPONENT_SUBSTITUTION!r} -- the member whose size_cm matches within linear_cm "
                "is used, and any other rule needs a rule of its own",
            )
            problems += 1
        listed = family.get("component_ids")
        if not isinstance(listed, list) or not listed:
            report.fail(
                "G-65",
                f"{where}.component_ids",
                f"component_ids is {listed!r}; a family resolves at least one component",
            )
            problems += 1
            continue
        for ref in listed:
            text = str(ref)
            if text not in declared:
                report.fail(
                    "G-65",
                    f"{where}.component_ids",
                    f"{text!r} is not a components[].id of this file",
                )
                problems += 1
            if isinstance(ident, str):
                placements.setdefault(text, []).append(ident)

    orphans = sorted(
        ident
        for ident in declared
        if len(placements.get(ident, [])) == 0
    )
    problems += len(orphans)
    for ident in orphans[:P5_ID_LIST_LIMIT]:
        report.fail(
            "G-65",
            f"{location}::families",
            f"component {ident} appears in no family; a family is the resolution index P6 needs, "
            f"and an unlisted component has no slot to be picked from ({len(orphans)} in total)",
        )
    doubled = sorted(ident for ident, families_of in placements.items() if len(families_of) > 1)
    problems += len(doubled)
    for ident in doubled[:P5_ID_LIST_LIMIT]:
        report.fail(
            "G-65",
            f"{location}::families",
            f"component {ident} appears in {len(placements[ident])} families "
            f"({', '.join(placements[ident])}); 07 G-65 says exactly one, because P6 picks the "
            "member whose size matches and cannot choose between two families",
        )

    if problems == 0:
        report.ok(
            "G-65",
            location,
            f"{len(components)} component(s) match {COMPONENT_ID_PATTERN} and {len(families)} "
            f"famil(ies) match {FAMILY_ID_PATTERN}, each set unique and ascending; every name is "
            "unique in the file and hyphen-free; every kind is declared in component_types[]; every "
            "component appears in exactly one families[].component_ids and every listed id exists",
        )


# ---- G-66 component parameters recompute ------------------------------------ #


def _g66_component_parameters(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-66. G-32 applied to the registry's own arithmetic."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    defaults = doc.get("defaults")
    if not isinstance(defaults, dict):
        report.fail(
            "G-66",
            f"{location}::defaults",
            f"defaults is {defaults!r}, expected an object holding exactly "
            f"{', '.join(COMPONENT_DEFAULT_KEYS)}",
        )
        return

    problems = 0
    for key, (low, high) in COMPONENT_DEFAULT_RANGES.items():
        value = as_number(defaults.get(key))
        if value is None:
            report.fail(
                "G-66",
                f"{location}::defaults.{key}",
                f"{key} is {defaults.get(key)!r}; the block carries a number, because the world "
                "table repeats it so P6 can inset a panel without re-reading this file",
            )
            problems += 1
            continue
        if not _in_range(value, low, high, True, True):
            report.fail(
                "G-66",
                f"{location}::defaults.{key}",
                f"{key} is {fmt_number(value)} outside its declared range "
                f"{_range_text(low, high, True, True, 'cm')}; the value is assumed (A-023 / A-024) "
                "against a range 09-defaults.md already states, so it is bounded here too",
            )
            problems += 1
    extra = sorted(key for key in defaults if key not in COMPONENT_DEFAULT_KEYS)
    problems += len(extra)
    for key in extra[:P5_ID_LIST_LIMIT]:
        report.fail(
            "G-66",
            f"{location}::defaults",
            f"defaults carries {key!r}; the block holds exactly "
            f"{', '.join(COMPONENT_DEFAULT_KEYS)} and nothing else",
        )

    thickness = as_number(defaults.get("panel_thickness_cm"))
    joint = as_number(defaults.get("joint_width_cm"))
    judged = 0
    for index, component in enumerate(_p5_rows(doc, "components")):
        where = f"{location}::components[{index}]"
        ident = component.get("id")
        label = f"{location}::{ident}" if isinstance(ident, str) else where
        size = _numbers(component.get("size_cm"))
        if size is None or len(size) != 3:
            report.fail(
                "G-66",
                f"{where}.size_cm",
                f"size_cm is {component.get('size_cm')!r}; it is exactly three numbers -- "
                "[width_cm, height_cm, panel_thickness_cm]",
            )
            problems += 1
            continue
        width, height, size_thickness = size
        judged += 1
        if thickness is not None and not close(size_thickness, thickness, tols.linear):
            report.fail(
                "G-66",
                f"{label}.size_cm",
                f"size_cm[2] is {fmt_number(size_thickness)} but defaults.panel_thickness_cm is "
                f"{fmt_number(thickness)}; a block deeper than the facade plane would not sit on "
                "it",
                tols.tol_linear,
            )
            problems += 1

        parameters = component.get("parameters")
        if not isinstance(parameters, list):
            report.fail(
                "G-66",
                f"{where}.parameters",
                f"parameters is {parameters!r}, expected the ordered list "
                f"{', '.join(COMPONENT_PARAMETER_ORDER)}",
            )
            problems += 1
            continue
        names = [entry.get("name") if isinstance(entry, dict) else None for entry in parameters]
        judged += 1
        if names != list(COMPONENT_PARAMETER_ORDER):
            report.fail(
                "G-66",
                f"{where}.parameters",
                f"the parameter order is {_p5_ids([str(name) for name in names])}; a builder needs "
                f"the stable order {', '.join(COMPONENT_PARAMETER_ORDER)} and cannot sort a set",
            )
            problems += 1
            continue
        expected_values = {
            "width_cm": width,
            "height_cm": height,
            "thickness_cm": thickness,
            "joint_width_cm": joint,
        }
        for position, parameter in enumerate(parameters):
            name = str(parameter.get("name"))
            param_where = f"{where}.parameters[{position}]"
            judged += 1
            expected_source = COMPONENT_PARAMETER_SOURCES[name]
            if parameter.get("source") != expected_source:
                report.fail(
                    "G-66",
                    param_where,
                    f"{name} declares source {parameter.get('source')!r}; 07 section 8.4.4 has it "
                    f"read {expected_source!r}"
                    + (
                        " -- width and height are this block's own size_cm"
                        if expected_source == "size_cm"
                        else " -- the depth and the joint are the same two numbers for every "
                        "component, so they live in defaults"
                    ),
                )
                problems += 1
            value = as_number(parameter.get("value"))
            target = expected_values[name]
            if value is None or target is None or not close(value, target, tols.linear):
                report.fail(
                    "G-66",
                    param_where,
                    f"{name} value is {fmt_number(parameter.get('value'))} but recomputes to "
                    f"{fmt_number(target)}",
                    tols.tol_linear,
                )
                problems += 1

    if problems == 0:
        report.ok(
            "G-66",
            location,
            f"defaults carries exactly {', '.join(COMPONENT_DEFAULT_KEYS)}, each inside its "
            "declared range; every component's parameters are the ordered list "
            f"{', '.join(COMPONENT_PARAMETER_ORDER)} with each source reading the right block and "
            f"each value recomputing from size_cm or defaults ({judged} comparisons)",
        )


# ---- G-67 component fits the panel kinds it serves -------------------------- #


def _g67_component_fit(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-67. A component's flags match the kinds it claims to serve, and its size fits a panel."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    grids = session.facade_grids
    if grids is None or not isinstance(grids.doc, dict):
        report.skip(
            "G-67",
            location,
            f"facade_grids.json is absent; which panel kinds a component may serve, and whether "
            "its size matches a real panel, are both read from it, so G-67 will not assume an "
            "answer for a file it cannot read",
        )
        return

    panel_types = _p5_panel_type_index(grids.doc)
    component_types = {
        entry["kind"]: entry
        for entry in _p5_rows(doc, "component_types")
        if isinstance(entry.get("kind"), str)
    }
    panel_sizes: list[tuple[float, float]] = []
    for panel in _p5_rows(grids.doc, "panels"):
        width = as_number(panel.get("width_cm"))
        height = as_number(panel.get("height_cm"))
        if width is not None and height is not None:
            panel_sizes.append((width, height))

    problems = 0
    judged = 0
    for index, component in enumerate(_p5_rows(doc, "components")):
        where = f"{location}::components[{index}]"
        ident = component.get("id")
        label = f"{location}::{ident}" if isinstance(ident, str) else where
        kind = component.get("kind")
        served = component.get("serves_panel_kinds")
        if not isinstance(served, list) or not served:
            report.fail(
                "G-67",
                f"{where}.serves_panel_kinds",
                f"serves_panel_kinds is {served!r}; it names at least one "
                f"{grids.label} panel_types[].kind, or the component serves nothing",
            )
            problems += 1
            continue

        undeclared = [str(entry) for entry in served if str(entry) not in panel_types]
        problems += len(undeclared)
        for entry in undeclared[:P5_ID_LIST_LIMIT]:
            report.fail(
                "G-67",
                f"{label}.serves_panel_kinds",
                f"{entry!r} is not a {grids.label} panel_types[].kind",
            )

        flags = component_types.get(str(kind))
        if flags is None:
            continue  # G-65 already named the unknown kind
        glazed = bool(flags.get("glazed"))
        frame_member = bool(flags.get("frame_member"))

        def compatible(panel_kind: str) -> Optional[str]:
            """None when the pairing is allowed, else the reason it is not."""
            entry = panel_types.get(panel_kind)
            if entry is None:
                return None
            panel_glazed = bool(entry.get("glazed"))
            panel_frame = bool(entry.get("frame_member"))
            opening_types = entry.get("opening_types") or []
            hosts_door = any(value in COMPONENT_DOOR_OPENING_TYPES for value in opening_types)
            if kind == "glazed_panel" and not panel_glazed:
                return "a glazed_panel fills a glazed panel kind"
            if kind == "opaque_panel" and (panel_glazed or panel_frame):
                return "an opaque_panel fills a kind that is neither glazed nor a frame member"
            if kind == "frame_member" and not panel_frame:
                return "a frame_member fills a kind whose frame_member flag is true"
            if kind == "entrance_door":
                if not panel_glazed:
                    return "an entrance_door fills a glazed panel kind"
                if not hosts_door:
                    return (
                        "an entrance_door fills a glazed kind that hosts a door or entrance "
                        f"opening, and {panel_kind} declares opening_types "
                        f"{_short(list(opening_types))}"
                    )
            return None

        for entry in served:
            reason = compatible(str(entry))
            judged += 1
            if reason is not None:
                report.fail(
                    "G-67",
                    f"{label}.serves_panel_kinds",
                    f"a {kind!r} may not serve panel kind {str(entry)!r}: {reason}",
                )
                problems += 1

        size = _numbers(component.get("size_cm"))
        if size is None or len(size) < 2:
            continue  # G-66 already named the size
        judged += 1
        if not any(
            close(size[0], width, tols.linear) and close(size[1], height, tols.linear)
            for width, height in panel_sizes
        ):
            report.fail(
                "G-67",
                f"{label}.size_cm",
                f"size_cm is {fmt_number(size[0])} x {fmt_number(size[1])} cm and matches no "
                f"{grids.label} panel's width_cm x height_cm within linear_cm ({tols.linear} cm); "
                "a component that fits no panel exists for no reason",
                tols.tol_linear,
            )
            problems += 1

    if problems == 0:
        report.ok(
            "G-67",
            location,
            f"every component's serves_panel_kinds is non-empty, names declared "
            f"{grids.label} panel_types[] kinds, and pairs only with kinds its own flags allow; "
            f"every size_cm matches at least one panel's width_cm x height_cm within linear_cm "
            f"({judged} comparisons over {len(panel_sizes)} distinct panel size(s))",
        )


# ---- G-68 every panel is placeable ------------------------------------------- #


def _g68_panel_placeable(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-68. The total join: every panel has a block, and the block resolves to one family.

    This is the invariant the registry exists for, and it is the one that fails loudly the
    day a panel size has no block. It runs on ``facade_grids.json`` rather than on the
    registry because the obligation is every *panel's*: P6 iterates panels, not components.
    """
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    registry = session.components_registry
    if registry is None or not isinstance(registry.doc, dict):
        _p5_missing_registry_row(
            "G-68",
            location,
            report,
            "the total join from every panel to a component whose size matches and whose "
            "serves_panel_kinds lists the panel's kind",
        )
        return

    panels = _p5_array(doc, "panels")
    if panels is None:
        report.fail(
            "G-68", f"{location}::panels", f"panels is {doc.get('panels')!r}, expected an array"
        )
        return

    family_of = _p5_component_families(registry.doc)
    components = _p5_rows(registry.doc, "components")
    problems = 0
    split: list[str] = []
    placeable = 0
    unplaceable: list[str] = []
    for index, panel in enumerate(_p5_rows(doc, "panels")):
        ident = panel.get("id")
        label = f"{location}::{ident}" if isinstance(ident, str) else f"{location}::panels[{index}]"
        kind = str(panel.get("kind"))
        width = as_number(panel.get("width_cm"))
        height = as_number(panel.get("height_cm"))
        matches: list[str] = []
        for component in components:
            size = _numbers(component.get("size_cm")) or []
            served = [str(value) for value in component.get("serves_panel_kinds") or []]
            if len(size) < 2 or width is None or height is None:
                continue
            if kind not in served:
                continue
            if close(size[0], width, tols.linear) and close(size[1], height, tols.linear):
                matches.append(str(component.get("id")))
        if not matches:
            unplaceable.append(ident if isinstance(ident, str) else label)
            continue
        families = sorted({family for match in matches for family in family_of.get(match, [])})
        if len(families) != 1:
            if not families:
                split.append(f"{ident} ({len(matches)} matching component(s), none in any family)")
            else:
                split.append(
                    f"{ident} ({len(matches)} matching component(s) across {len(families)} "
                    f"families: {', '.join(families)})"
                )
            continue
        placeable += 1

    problems += len(split)
    for entry in split[:P5_ID_LIST_LIMIT]:
        report.fail(
            "G-68",
            f"{location}::panels",
            f"panel {entry} has matching component(s) that do not resolve inside one family; P6 "
            "picks the member whose size_cm matches, so the match must be unambiguous",
        )
    problems += len(unplaceable)
    if unplaceable:
        report.fail(
            "G-68",
            f"{location}::panels",
            f"{len(unplaceable)} panel(s) have no component whose size_cm matches and whose "
            f"serves_panel_kinds lists the panel's kind: {_p5_ids(unplaceable)}; a panel with no "
            "block cannot be placed, and this is the check that says so before P6 runs",
            tols.tol_linear,
        )

    if problems == 0:
        report.ok(
            "G-68",
            location,
            f"all {placeable} panel(s) match at least one {registry.label} component on both "
            f"width and height within linear_cm with the panel's kind in serves_panel_kinds, and "
            "every match resolves inside exactly one family",
        )


# ---- G-69 variant discipline ------------------------------------------------- #


def _g69_variant_discipline(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-69. Variant ids, uniqueness, and an overrides object keyed by a real parameter."""
    location = record.label
    doc = record.doc
    if not isinstance(doc, dict):
        return
    components = _p5_array(doc, "components")
    if components is None:
        report.fail(
            "G-65",
            f"{location}::components",
            f"components is {doc.get('components')!r}, expected an array",
        )
        return

    rows = _p5_rows(doc, "components")
    total = sum(len(row.get("variants") or []) for row in rows)
    if total == 0:
        report.skip(
            "G-69",
            location,
            f"every one of the {len(rows)} component(s) declares an empty variants array, so "
            "nothing about a variant can be checked; the generated registry declares none, and "
            "saying the rule is unexercised is better than a vacuous PASS (07 section 9.6)",
        )
        return

    problems = 0
    judged = 0
    for index, component in enumerate(rows):
        where = f"{location}::components[{index}]"
        ident = component.get("id")
        variants = component.get("variants")
        if not isinstance(variants, list):
            report.fail(
                "G-69",
                f"{where}.variants",
                f"variants is {variants!r}, expected an array (empty when the block has one form)",
            )
            problems += 1
            continue
        seen: set[str] = set()
        for position, variant in enumerate(variants):
            variant_where = f"{where}.variants[{position}]"
            if not isinstance(variant, dict):
                report.fail(
                    "G-69", variant_where, f"variants[{position}] is not an object"
                )
                problems += 1
                continue
            judged += 1
            vid = variant.get("id")
            if not isinstance(vid, str) or not VARIANT_ID_RE.match(vid):
                report.fail(
                    "G-69",
                    f"{variant_where}.id",
                    f"id is {vid!r}; it does not match {VARIANT_ID_PATTERN}",
                )
                problems += 1
            elif vid in seen:
                report.fail(
                    "G-69",
                    f"{variant_where}.id",
                    f"id {vid!r} appears more than once in component {ident!r}; a variant id is "
                    "unique within its component",
                )
                problems += 1
            else:
                seen.add(vid)
            overrides = variant.get("overrides")
            if not isinstance(overrides, dict) or not overrides:
                report.fail(
                    "G-69",
                    f"{variant_where}.overrides",
                    f"overrides is {overrides!r}; a variant exists to override something, so it is "
                    "a non-empty object",
                )
                problems += 1
                continue
            unknown = sorted(key for key in overrides if key not in COMPONENT_PARAMETER_ORDER)
            problems += len(unknown)
            for key in unknown[:P5_ID_LIST_LIMIT]:
                report.fail(
                    "G-69",
                    f"{variant_where}.overrides",
                    f"{key!r} is not one of {', '.join(COMPONENT_PARAMETER_ORDER)}; a variant may "
                    "only override a declared parameter, or the builder has no slot to write it to",
                )

    if problems == 0:
        report.ok(
            "G-69",
            location,
            f"{total} variant(s) across {len(rows)} component(s) match {VARIANT_ID_PATTERN} and "
            "are unique within their component, and every overrides object is non-empty and keyed "
            f"only by {', '.join(COMPONENT_PARAMETER_ORDER)} ({judged} variants checked)",
        )


# ---- G-70 emitted-table census -- the predicate the builder reuses ------------ #


def facade_table_census(
    grid_doc: Any,
    registry_doc: Any,
    facade_table_rows: Sequence[Any],
    world_table_rows: Sequence[Any],
    angle_deg: float = FALLBACK_ANGLE_DEG,
) -> list[str]:
    """The G-70 predicate, as a pure function of three parsed documents and two CSV row lists.

    **Signature contract for ``facade_tables.py``.** The builder imports *this* rather than
    re-implementing the rule, so the build-time assertion and the lint-time definition can
    never disagree:

    ==================  ==========================================================
    ``grid_doc``        the parsed ``facade_grids.json`` object, written or in hand
    ``registry_doc``    the parsed ``components_registry.json`` object
    ``facade_table_rows``  ``facade_table.csv`` data rows, already parsed, **header
                        excluded**, each a ``dict`` keyed by the 07 section 9.8
                        column names
    ``world_table_rows``   ``world_table.csv`` data rows, same shape
    ``angle_deg``       the project's ``tolerances.angle_deg``, compared as
                        ``<=`` against ``run_angle_deg``
    ==================  ==========================================================

    Returns the list of problem strings; an **empty list is a pass**. The builder raises on a
    non-empty list and refuses to write, which is what makes a miscount a failed build rather
    than a silent one. Nothing here reads a file, a clock or the scene.
    """
    problems: list[str] = []
    panels = grid_doc.get("panels") if isinstance(grid_doc, dict) else None
    if not isinstance(panels, list):
        return ["facade_grids.json declares no panels array, so the census has no denominator"]

    panel_ids = {
        panel["id"] for panel in panels if isinstance(panel, dict) and isinstance(panel.get("id"), str)
    }
    run_angles: dict[str, float] = {}
    if isinstance(grid_doc, dict):
        for facade in _p5_rows(grid_doc, "facades"):
            ident = facade.get("id")
            angle = _p5_run_angle_deg(facade)
            if isinstance(ident, str) and angle is not None:
                run_angles[ident] = angle
    components = {
        component["id"]
        for component in _p5_rows(registry_doc, "components")
        if isinstance(component.get("id"), str)
    }
    families = {
        family["id"] for family in _p5_rows(registry_doc, "families") if isinstance(family.get("id"), str)
    }

    def check_rows(rows: Sequence[Any], label: str) -> None:
        if len(rows) != len(panels):
            problems.append(
                f"{label}.csv holds {len(rows)} data row(s) but facade_grids.json declares "
                f"{len(panels)} panel(s); the tables are emitted by walking panels[], so a "
                "mismatch means a row was dropped or duplicated"
            )
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                problems.append(f"{label}.csv row {index} is not an object")
                continue
            for key, known, what in (
                ("panel_ref", panel_ids, "a facade_grids.json panels[].id"),
                ("panel_id", panel_ids, "a facade_grids.json panels[].id"),
            ):
                if key in row and str(row[key]) not in known:
                    problems.append(
                        f"{label}.csv row {index} {key}={row[key]!r} is not {what}"
                    )
            if "component_ref" in row and str(row["component_ref"]) not in components:
                problems.append(
                    f"{label}.csv row {index} component_ref={row['component_ref']!r} is not a "
                    "components_registry.json components[].id"
                )
            if "family_ref" in row and str(row["family_ref"]) not in families:
                problems.append(
                    f"{label}.csv row {index} family_ref={row['family_ref']!r} is not a "
                    "components_registry.json families[].id"
                )
            if "instance_id" in row and "panel_ref" in row and row["instance_id"] != row["panel_ref"]:
                problems.append(
                    f"{label}.csv row {index} instance_id={row['instance_id']!r} differs from "
                    f"panel_ref={row['panel_ref']!r}; one instance per panel is the property that "
                    "makes the row count checkable against len(panels) with no join"
                )

    check_rows(facade_table_rows, "facade_table")
    check_rows(world_table_rows, "world_table")

    for index, row in enumerate(world_table_rows):
        if not isinstance(row, dict) or "rot_z_deg" not in row:
            continue
        facade = row.get("facade")
        angle = run_angles.get(str(facade))
        value = _p5_cell(row["rot_z_deg"])
        if angle is None or value is None or not close(value, angle, angle_deg):
            problems.append(
                f"world_table.csv row {index} rot_z_deg={row['rot_z_deg']!r} does not equal "
                f"{facade!r}'s run_angle_deg "
                f"{fmt_number(angle) if angle is not None else '(unknown facade)'} within "
                f"{angle_deg} deg; rot_z_deg is the run angle and never direction_deg, which is "
                "a facing label carrying 180.0 and 0.0 for two facades that both run along +X"
            )

    return problems


def _g70_table_census(record: LoadedFile, report: Report) -> None:
    """G-70. The emitted-table census. SKIP with its reason, by construction.

    G-70 asks whether the two emitted CSVs carry exactly ``len(panels)`` rows, whether every
    ``panel_ref`` / ``component_ref`` / ``family_ref`` resolves, and whether every
    ``rot_z_deg`` is its facade's ``run_angle_deg``. None of that exists at lint time: the
    CSVs are produced by ``scripts/facade_tables.py`` from the very JSON being linted, and a
    static reader that cannot see them has no verdict to give. This is the table-shaped
    analogue of G-54 -- a build that merely completes is not proof that the tables are right,
    and the count is the cheapest place a mistake becomes visible.

    The predicate itself is not duplicated here: ``facade_table_census`` is the single
    implementation, and the builder asserts the same function after writing. Reporting PASS
    would be the one dishonest outcome available, so this reports SKIP and says why.
    """
    report.skip(
        "G-70",
        record.label,
        "not evaluable at lint time. G-70 is a census of facade_table.csv and world_table.csv, "
        "and a static JSON file cannot observe a CSV it did not write: the row count, the "
        "reference resolution and the rot_z_deg of every instance are all properties of the "
        "emitted tables, not of this document. Enforced at build time instead, by "
        "scripts/facade_tables.py asserting facade_table_census() -- the same function this "
        "module defines -- on the files it has just written, and refusing on a mismatch. A "
        "check that cannot be evaluated reports SKIP with its reason, never a silent PASS "
        "(07 section 9.6)",
    )


# ---- dispatch: facade_grids.json (G-57..G-64) --------------------------------- #

#: 07 section 9.8 -- a ``draft`` facade_grids file is **not evaluated**, and every rule in the
#: section skips while ``status != "locked"``. Same argument as 07 section 9.6 and 9.7: the
#: file is *computed* from ``dimensions.json`` and ``massing.json`` by
#: ``scripts/facade_tables.py``, so the placeholder a fresh scaffold writes declares no
#: facade, no axis, no panel and no provenance to check. ``--allow-draft`` forces them to run,
#: where they do fail -- which is the point of the flag. ``--build`` still refuses the file at
#: G-4.
FACADE_DRAFT_RULES: tuple[str, ...] = (
    "G-57",
    "G-58",
    "G-59",
    "G-60",
    "G-61",
    "G-62",
    "G-63",
    "G-64",
    "G-68",
    "G-70",
)


def check_facade_rules(record: LoadedFile, session: Session, report: Report) -> None:
    """07 section 9.8: the ``facade_grids.json`` rules, guarded one at a time."""
    if _draft_skip_reason(
        record,
        FACADE_DRAFT_RULES,
        session,
        report,
        "9.8",
        "the grid is computed from dimensions.json and massing.json by "
        "scripts/facade_tables.py and this placeholder declares no facade, no axis, no "
        "panel and no provenance to check",
    ):
        return

    tols = _p5_tolerances(record, session)
    guard("G-57", record.label, report, _g57_facade_agreement, record, session, tols)
    guard("G-58", record.label, report, _g58_axis_integrity, record, session, tols)
    guard("G-59", record.label, report, _g59_panel_rectangles, record, session, tols)
    guard("G-60", record.label, report, _g60_panel_edges, record, session, tols)
    guard("G-61", record.label, report, _g61_partition, record, session, tols)
    guard("G-62", record.label, report, _g62_opening_reconciliation, record, session, tols)
    guard("G-63", record.label, report, _g63_panel_vocabulary, record, session, tols)
    guard("G-64", record.label, report, _g64_grid_provenance, record, session, tols)
    guard("G-68", record.label, report, _g68_panel_placeable, record, session, tols)
    guard("G-70", record.label, report, _g70_table_census, record)


# ---- dispatch: components_registry.json (G-65..G-67, G-69) ------------------- #

#: 07 section 9.8 -- and the same draft discipline for the registry. ``G-68`` is absent on
#: purpose: it is a total-join invariant over *panels*, so it is dispatched from
#: ``facade_grids.json`` and reports its own SKIP-with-a-reason when the registry is absent.
COMPONENT_DRAFT_RULES: tuple[str, ...] = ("G-65", "G-66", "G-67", "G-69")


def check_component_rules(record: LoadedFile, session: Session, report: Report) -> None:
    """07 section 9.8: the ``components_registry.json`` rules, guarded one at a time."""
    if _draft_skip_reason(
        record,
        COMPONENT_DRAFT_RULES,
        session,
        report,
        "9.8",
        "the registry is derived from facade_grids.json by scripts/facade_tables.py and "
        "this placeholder declares no component, no family and no provenance to check",
    ):
        return

    tols = _p5_tolerances(record, session)
    guard("G-65", record.label, report, _g65_component_identity, record, session, tols)
    guard("G-66", record.label, report, _g66_component_parameters, record, session, tols)
    guard("G-67", record.label, report, _g67_component_fit, record, session, tols)
    guard("G-69", record.label, report, _g69_variant_discipline, record, session, tols)


# --------------------------------------------------------------------------- #
# 07 section 9.9 -- G-71..G-81, the assembly.json invariants
# --------------------------------------------------------------------------- #
#
# Same machinery as G-34..G-56 and G-57..G-70 and no new tolerance values: the
# leaf walker is G-9's, the dotted-path resolver is G-32's, the inward-band
# recomputation is G-38 clause 2's, and every geometry row names the tolerance it
# used (07 section 9.5).
#
# Three of the eleven observe the **emitted** `assembly.ms` and therefore cannot
# be evaluated from the JSON: G-79 (no layer statement in the script), G-80 (the
# census the script asserts) and G-81 (the modifier-stack bound).  They report an
# honest SKIP with their reason at lint time and are FAIL at build time, exactly as
# G-54 and G-70 do.  `scripts/place_components.py` is the single implementation of
# all three and asserts them on the bytes it has just written.
# --------------------------------------------------------------------------- #

#: 07 section 8.5 -- the three id shapes, and the one legal cut kind.
ASSEMBLY_PLACEMENT_ID_RE = re.compile(r"^PLC-\d{3}$")
ASSEMBLY_CUT_ID_RE = re.compile(r"^CUT-\d{3}$")
ASSEMBLY_SCATTER_ID_RE = re.compile(r"^SCT-\d{3}$")
ASSEMBLY_CUT_KINDS: tuple[str, ...] = ("difference",)

#: 07 section 8.5 -- the closed scatter seed range (P0 determinism).
ASSEMBLY_SEED_MIN = 1
ASSEMBLY_SEED_MAX = 31337

#: The measured modifier ladder of 2026-10-05, restated here so the build-time
#: text and this section cannot quote different numbers.
ASSEMBLY_MAX_MODIFIERS_PER_CALL = 5
ASSEMBLY_MAX_MODIFIERS_PER_NODE = 10

#: 11 section 3.1 N1 -- letters, digits and `_` only. Restated here rather than imported
#: from ``build_spec.py``: the linter reads no other module, and a shared constant that had
#: to be kept in step by hand is two copies of a rule that can disagree.
ASSEMBLY_NODE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

ASSEMBLY_WORLD_CSV = "world_table.csv"
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

#: 07 section 9.6 -- a `draft` assembly file is **not evaluated**, and every rule in
#: the section skips while `status != "locked"`, for the same argument as 9.6/9.7/9.8:
#: the file is *computed* by `scripts/place_components.py`, so the stub a fresh scaffold
#: writes declares no placement, no cut, no scatter and no provenance to check.
#: `--allow-draft` forces the rules to run on a draft that has content -- where they do
#: fail -- and on an untouched empty stub, where every rule would be reporting the
#: absence of content rather than a defect.  `--build` still refuses the file at G-4.
ASSEMBLY_DRAFT_RULES: tuple[str, ...] = (
    "G-71",
    "G-72",
    "G-73",
    "G-74",
    "G-75",
    "G-76",
    "G-77",
    "G-78",
    "G-79",
    "G-80",
    "G-81",
    "G-82",
    "G-83",
)


def check_assembly_rules(record: LoadedFile, session: Session, report: Report) -> None:
    """07 section 9.9: the ``assembly.json`` rules, guarded one at a time."""
    if _draft_skip_reason(
        record,
        ASSEMBLY_DRAFT_RULES,
        session,
        report,
        "9.9",
        "assembly.json is computed by scripts/place_components.py from a locked "
        "components_registry.json, world_table.csv, massing.json and dimensions.json and "
        "this placeholder declares no placement, no cut, no scatter and no provenance",
    ):
        return

    tols = _p5_tolerances(record, session)
    guard("G-71", record.label, report, _g71_component_resolution, record, session)
    guard("G-72", record.label, report, _g72_source_row_join, record, session)
    guard("G-73", record.label, report, _g73_placement_geometry, record, session, tols)
    guard("G-74", record.label, report, _g74_node_names, record)
    guard("G-75", record.label, report, _g75_layer_map, record, session)
    guard("G-76", record.label, report, _g76_cut_host, record, session, tols)
    guard("G-77", record.label, report, _g77_opening_bijection, record, session, tols)
    guard("G-78", record.label, report, _g78_scatter, record, session)
    guard("G-79", record.label, report, _g79_no_layer_code, record)
    guard("G-80", record.label, report, _g80_emitted_census, record)
    guard("G-81", record.label, report, _g81_bounded_stack, record)
    guard("G-82", record.label, report, _g82_wall_tiling_volume, record, session, tols)
    guard("G-83", record.label, report, _g83_wall_cell_thickness, record, session, tols)


# ---- shared assembly readers ------------------------------------------------- #


def _assembly_point(value: Any) -> bool:
    """``[x, y, z]`` with three finite numbers -- ``is_point`` is the 2D helper."""
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(as_number(item) is not None for item in value)
    )


def _assembly_rows(doc: Any, key: str) -> list[dict]:
    """The object rows of ``doc[key]``, in file order."""
    value = doc.get(key) if isinstance(doc, dict) else None
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, dict)]


def _assembly_index(doc: Any, key: str) -> dict[str, dict]:
    """``id -> entry`` for an array of objects, first occurrence winning."""
    out: dict[str, dict] = {}
    for entry in _assembly_rows(doc, key):
        ident = entry.get("id")
        if isinstance(ident, str):
            out.setdefault(ident, entry)
    return out


def _assembly_facade_index(dims: Any) -> dict[str, dict]:
    facades = dims.get("facades") if isinstance(dims, dict) else None
    out: dict[str, dict] = {}
    for facade in facades or []:
        if isinstance(facade, dict) and isinstance(facade.get("id"), str):
            out.setdefault(facade["id"], facade)
    return out


def _assembly_level_index(dims: Any) -> dict[int, dict]:
    levels = dims.get("levels") if isinstance(dims, dict) else None
    out: dict[int, dict] = {}
    for level in levels or []:
        if isinstance(level, dict) and is_int(level.get("index")):
            out.setdefault(level["index"], level)
    return out


def _read_sibling_csv(path: Path, columns: Sequence[str]) -> Optional[list[dict[str, str]]]:
    """The data rows of an emitted CSV next to the specs, or None when it is unusable.

    Only the shape G-72/G-73 depend on is checked -- header identity, LF, field count -- so
    that the *count* lives in one place. The census itself is the linter's; the CSV's
    producer is `scripts/facade_tables.py`.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if "\r" in text:
        return None
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != ",".join(columns):
        return None
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        fields = line.split(",")
        if len(fields) != len(columns):
            return None
        rows.append(dict(zip(columns, fields)))
    return rows


def _assembly_world_rows(
    record: LoadedFile, session: Session
) -> tuple[Optional[list[dict[str, str]]], str]:
    """``(rows, reason_when_none)`` -- the world table beside this spec, or why not."""
    path = session.csv_by_name(ASSEMBLY_WORLD_CSV)
    if path is None:
        return None, (
            f"{ASSEMBLY_WORLD_CSV} was not found beside {record.label}. G-72 and G-73 are "
            "statements about the join between assembly.json and that table, and a validator "
            "that cannot see the table has no verdict to give"
        )
    rows = _read_sibling_csv(path, ASSEMBLY_WORLD_COLUMNS)
    if rows is None:
        return None, (
            f"{path} is not a well-formed {ASSEMBLY_WORLD_CSV}: expected the header "
            f"{','.join(ASSEMBLY_WORLD_COLUMNS)}, LF endings and {len(ASSEMBLY_WORLD_COLUMNS)} "
            "fields per row (07 G-70). The join G-72 and G-73 assert cannot be read"
        )
    return rows, ""


def _assembly_component_kinds(session: Session) -> dict[str, str]:
    """``component_id -> kind`` from the registry, empty when the registry is absent."""
    registry = session.components_registry
    if registry is None or not registry.ok or not isinstance(registry.doc, dict):
        return {}
    out: dict[str, str] = {}
    for component in _p5_rows(registry.doc, "components"):
        ident = component.get("id")
        kind = component.get("kind")
        if isinstance(ident, str) and isinstance(kind, str):
            out.setdefault(ident, kind)
    return out


# ---- G-71 .. G-78 ------------------------------------------------------------- #


def _g71_component_resolution(
    record: LoadedFile, session: Session, report: Report
) -> None:
    """G-71. Every ``placements[].component_id`` resolves to a registry component.

    Also the row's identity checks, because an id that is malformed, duplicated or
    out of order cannot be resolved at all and would otherwise be skipped silently by
    every join in the section.
    """
    doc = record.doc
    location = record.label
    registry = session.components_registry
    if registry is None or not registry.ok or not isinstance(registry.doc, dict):
        report.skip(
            "G-71",
            location,
            f"cannot run: {REGISTRY_SPEC_NAME} is absent or unreadable, so a component_id has "
            "nothing to resolve against. A join that cannot be evaluated reports SKIP with its "
            "reason (07 section 9.6)",
        )
        return
    declared = {
        str(component.get("id"))
        for component in _p5_rows(registry.doc, "components")
        if isinstance(component.get("id"), str)
    }
    rows = _assembly_rows(doc, "placements")
    problems = 0
    seen: dict[str, str] = {}
    numbers: list[int] = []
    for entry in rows:
        ident = entry.get("id")
        where = f"{location}::placements[{entry.get('source_row', '?')}]"
        if not isinstance(ident, str) or not ASSEMBLY_PLACEMENT_ID_RE.match(ident):
            report.fail("G-71", where, f"id {ident!r} does not match ^PLC-\\d{{3}}$")
            problems += 1
        elif ident in seen:
            report.fail("G-71", where, f"id {ident!r} is already used by {seen[ident]}")
            problems += 1
        else:
            seen[ident] = where
            match = ASSEMBLY_PLACEMENT_ID_RE.match(ident)
            if match:
                numbers.append(int(ident.split("-")[1]))
        component_id = entry.get("component_id")
        if not isinstance(component_id, str) or component_id not in declared:
            report.fail(
                "G-71",
                where,
                f"component_id {component_id!r} does not resolve to a "
                f"{REGISTRY_SPEC_NAME} components[].id; a placement naming no component is an "
                "instruction with no geometry",
            )
            problems += 1
    if numbers and numbers != sorted(numbers):
        report.fail(
            "G-71",
            f"{location}::placements",
            "ids are not ascending; 07 section 8.5 requires them allocated in row order so the "
            "file is diffable against the table it came from",
        )
        problems += 1
    if problems == 0:
        report.ok(
            "G-71",
            location,
            f"{len(rows)} placements, every component_id resolves to a {REGISTRY_SPEC_NAME} "
            "component, ids unique and ascending",
        )


REGISTRY_SPEC_NAME = "components_registry.json"
MASSING_SPEC_NAME = "massing.json"
DIMENSIONS_SPEC_NAME = "dimensions.json"


def _g72_source_row_join(record: LoadedFile, session: Session, report: Report) -> None:
    """G-72. ``placements[]`` and the world table's data rows are equal **both ways**.

    The two directions are the whole point of carrying ``source_row``: a missing row and an
    extra row are different defects, and a rule that only counted them would see the same
    number in both.
    """
    location = record.label
    rows, reason = _assembly_world_rows(record, session)
    if rows is None:
        report.skip("G-72", location, reason)
        return
    declared = [entry.get("source_row") for entry in _assembly_rows(record.doc, "placements")]
    real = list(range(1, len(rows) + 1))
    problems = 0
    malformed = [
        value
        for value in declared
        if not is_int(value)
    ]
    if malformed:
        for value in malformed[:10]:
            report.fail(
                "G-72",
                location,
                f"a placement carries source_row {value!r}; 07 section 8.5 makes it the 1-based "
                "data row index of world_table.csv, header excluded",
            )
        problems += len(malformed)
    integers = [value for value in declared if is_int(value)]
    duplicates = sorted({value for value in integers if integers.count(value) > 1})
    if duplicates:
        for value in duplicates[:10]:
            report.fail(
                "G-72",
                location,
                f"source_row {value} is claimed by {integers.count(value)} placements; one table "
                "row is one placement",
            )
        problems += len(duplicates)
    missing = sorted(set(real) - set(integers))
    if missing:
        report.fail(
            "G-72",
            location,
            f"{len(missing)} world_table.csv data row(s) have no placement: "
            f"{_p5_ids(missing)}; a panel that is never placed is a gap nobody would see",
        )
        problems += 1
    extra = sorted(set(integers) - set(real))
    if extra:
        report.fail(
            "G-72",
            location,
            f"{len(extra)} source_row value(s) name no table row: {_p5_ids(extra)}",
        )
        problems += 1
    if problems == 0:
        report.ok(
            "G-72",
            location,
            f"{len(declared)} placements == {len(rows)} data rows, equal in both directions, no "
            "duplicate source_row",
        )


def _g73_placement_geometry(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-73. Each placement's geometry **equals its CSV row**.

    The rule exists because the builder has two ways to place a panel and only one is
    right: reading the emitted table, or recomputing the position from the facade grid.
    Recomputing reintroduces P5's measured bug -- ``rot_z_deg`` is the run angle
    ``atan2(dy, dx)``, never ``dimensions.facades[].direction_deg``, and ``F-S`` and
    ``F-N`` both run along +X while carrying 180 and 0.
    """
    location = record.label
    rows, reason = _assembly_world_rows(record, session)
    if rows is None:
        report.skip("G-73", location, reason)
        return
    problems = 0
    checked = 0
    for entry in _assembly_rows(record.doc, "placements"):
        index = entry.get("source_row")
        if not is_int(index) or not 1 <= index <= len(rows):
            continue
        row = rows[index - 1]
        where = f"{location}::{entry.get('id')}"
        checked += 1
        actual = entry.get("position_cm")
        if not _assembly_point(actual):
            report.fail(
                "G-73",
                where,
                f"position_cm {actual!r} is not a finite [x, y, z] in cm",
            )
            problems += 1
        else:
            expected = [
                _p5_cell(row["x_cm"]),
                _p5_cell(row["y_cm"]),
                _p5_cell(row["z_cm"]),
            ]
            for axis, label in enumerate(("x_cm", "y_cm", "z_cm")):
                value = expected[axis]
                if value is None or not close(actual[axis], value, tols.linear):
                    report.fail(
                        "G-73",
                        where,
                        f"position_cm[{axis}] {fmt_number(actual[axis])} != "
                        f"{ASSEMBLY_WORLD_CSV} row {index} {label}={row[label]!r} within "
                        f"{tols.tol_linear}. The builder must copy the table, never recompute "
                        "placement geometry",
                        tols.tol_linear,
                    )
                    problems += 1
        angle = _p5_cell(row["rot_z_deg"])
        if angle is None or not close(entry.get("rot_z_deg"), angle, tols.angle):
            report.fail(
                "G-73",
                where,
                f"rot_z_deg {entry.get('rot_z_deg')!r} != {ASSEMBLY_WORLD_CSV} row {index} "
                f"rot_z_deg={row['rot_z_deg']!r} within {tols.tol_angle}. rot_z_deg is the run "
                "angle and never direction_deg, which is a facing label carrying 180.0 and 0.0 "
                "for two facades that both run along +X",
                tols.tol_angle,
            )
            problems += 1
        if entry.get("instance") is not True:
            report.fail(
                "G-73",
                where,
                f"instance is {entry.get('instance')!r}; 07 section 8.5 makes it always true, "
                "because the whole stage is an instancing pass and a non-instance would have to "
                "be a 136th copy of the geometry",
            )
            problems += 1
    if problems == 0 and checked:
        report.ok(
            "G-73",
            location,
            f"{checked} placements equal their {ASSEMBLY_WORLD_CSV} row within "
            f"{tols.tol_linear} / {tols.tol_angle}",
            tols.tol_linear,
        )


def _g74_node_names(record: LoadedFile, report: Report) -> None:
    """G-74. ``node_name`` is unique across the four tables, and identifier-safe.

    Rule N1 of `11-layer-standard.md` is not cosmetic: a name is pasted into emitted
    MAXScript and into typed-tool arguments, and ``EL-001`` reads as ``EL - 001`` there.

    ``wall_cells`` joined this tuple at P6 and was MISSING at first -- the fourth time in
    this repo a rule failed to fire because the array it governs was added later (after
    P4b's "G-56 does not cover depth_cm shells", P5's "G-69 is vacuous" and P6's own
    builder-side G-74 gap). ``place_components.py`` has swept all four since; this linter
    had not. When a stage adds a new array, re-read every rule that enumerates the old
    ones -- and prove it with fault injection, because a rule that does not mention your
    new thing will not tell you.
    """
    doc = record.doc
    location = record.label
    claims: dict[str, str] = {}
    problems = 0
    for table in ("placements", "opening_cuts", "wall_cells", "scatter"):
        for entry in _assembly_rows(doc, table):
            where = f"{location}::{table}[{entry.get('id')}]"
            name = entry.get("node_name")
            if not isinstance(name, str) or not ASSEMBLY_NODE_NAME_RE.match(name):
                report.fail(
                    "G-74",
                    where,
                    f"node_name {name!r} is not MAXScript-identifier-safe. 11 section 3.1 N1 "
                    "requires letters, digits and `_` only, and gives the mapping PLC-001 -> "
                    "PLC_001",
                )
                problems += 1
                continue
            if name in claims:
                report.fail(
                    "G-74",
                    where,
                    f"node_name {name!r} is already claimed by {claims[name]}; a name that "
                    "identifies one node in the scene cannot identify two",
                )
                problems += 1
            else:
                claims[name] = f"{table}[{entry.get('id')}]"
            expected = str(entry.get("id")).replace("-", "_")
            if name != expected:
                report.fail(
                    "G-74",
                    where,
                    f"node_name {name!r} is not derived from its own id {entry.get('id')!r}. "
                    "11 section 3.1 N4 requires the name to be the id with dashes replaced, so "
                    f"it reads {expected!r}; a descriptive name is a lookup table nobody versions",
                )
                problems += 1
    if problems == 0:
        report.ok(
            "G-74",
            location,
            f"{len(claims)} node names, unique across placements / opening_cuts / wall_cells / "
            "scatter, all identifier-safe and id-derived",
        )


def _g75_layer_map(record: LoadedFile, session: Session, report: Report) -> None:
    """G-75. ``placements[].layer`` is the ``layer_map`` entry for its role, and every
    ``layer_map`` **key** is in the 07 section 8.1.4 vocabulary.

    ``layer_map`` is keyed by layer name precisely so this rule has one job rather than two:
    the keys are the vocabulary, and a placement's role -- read through its component -- must
    be listed under exactly one of them.
    """
    doc = record.doc
    location = record.label
    layer_map = doc.get("layer_map")
    problems = 0
    if not isinstance(layer_map, dict):
        report.fail(
            "G-75",
            f"{location}::layer_map",
            f"layer_map is {type(layer_map).__name__}, expected an object keyed by layer name",
        )
        layer_map = {}
    else:
        for layer in sorted(layer_map):
            if layer not in MASSING_LAYERS:
                report.fail(
                    "G-75",
                    f"{location}::layer_map.{layer}",
                    f"layer {layer!r} is not one of {', '.join(MASSING_LAYERS)}. 07 section 8.1.4 "
                    "closes the vocabulary at eight names and 11-layer-standard.md must not "
                    "introduce a ninth before changing that table",
                )
                problems += 1
            elif not isinstance(layer_map[layer], list) or not layer_map[layer]:
                report.fail(
                    "G-75",
                    f"{location}::layer_map.{layer}",
                    f"layer {layer!r} lists no role; a layer that holds nothing here is a claim "
                    "nobody can check",
                )
                problems += 1
    kinds = _assembly_component_kinds(session)
    if not kinds:
        report.skip(
            "G-75",
            location,
            f"cannot run the role join: {REGISTRY_SPEC_NAME} is absent or unreadable, so a "
            "placement's role is undecidable. The vocabulary half of the rule still ran and is "
            "reported above if it failed",
        )
        return
    for table, role_of in (
        ("placements", lambda entry: kinds.get(str(entry.get("component_id")))),
        ("scatter", lambda entry: "scatter_source"),
    ):
        for entry in _assembly_rows(doc, table):
            where = f"{location}::{table}[{entry.get('id')}]"
            layer = entry.get("layer")
            role = role_of(entry)
            if role is None:
                report.fail(
                    "G-75",
                    where,
                    f"component_id {entry.get('component_id')!r} is not in the registry index, so "
                    "its layer_map role is undecidable",
                )
                problems += 1
                continue
            if not isinstance(layer, str) or layer not in layer_map:
                report.fail(
                    "G-75",
                    where,
                    f"layer {layer!r} is not a layer_map key; the layer column is read from "
                    "layer_map and never written beside it",
                )
                problems += 1
            elif role not in layer_map[layer]:
                report.fail(
                    "G-75",
                    where,
                    f"role {role!r} is not listed under layer_map[{layer!r}] "
                    f"({layer_map[layer]!r}), so the layer column disagrees with the map it "
                    "claims to come from",
                )
                problems += 1
    for layer, roles in sorted(layer_map.items()):
        if not isinstance(roles, list):
            continue
        for role in roles:
            found = [name for name, entries in layer_map.items() if isinstance(entries, list)
                     and role in entries]
            if len(found) > 1:
                report.fail(
                    "G-75",
                    f"{location}::layer_map.{layer}",
                    f"role {role!r} is listed under {len(found)} layers ({', '.join(found)}); a "
                    "role's layer must be decidable from the spec alone",
                )
                problems += 1
    if problems == 0:
        report.ok(
            "G-75",
            location,
            f"layer_map carries {len(layer_map)} of the eight 07 section 8.1.4 layers and every "
            "placement and scatter row agrees with it",
        )


def _g76_cut_host(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-76. Every cut is on a real ``facade_wall``, inside its own extent, deep enough.

    "Inside its own extent" is measured on the **host**, not on the facade the host serves:
    the wall's own corners are projected onto the run unit to give its ``u`` extent, and its
    ``z_range_cm`` span gives its ``v`` extent. ``u_range_cm`` and ``v_range_cm`` are both
    facade-local -- 07 section 8.5 states the frame, and a level-1 opening whose head is
    270 cm is inside a wall running 420 -> 820 without any elevation being added.
    """
    doc = record.doc
    location = record.label
    massing = session.massing
    dims = session.dimensions
    missing = [
        name
        for name, loaded in (
            (MASSING_SPEC_NAME, massing),
            (DIMENSIONS_SPEC_NAME, dims),
        )
        if loaded is None or not loaded.ok or not isinstance(loaded.doc, dict)
    ]
    if missing:
        report.skip(
            "G-76",
            location,
            f"cannot run: {', '.join(missing)} not loaded, so host_ref cannot be resolved and "
            "the u / v / depth bounds cannot be recomputed",
        )
        return
    assert massing is not None and dims is not None
    elements = _elements_of(massing.doc)
    by_id = {
        str(element.get("id")): element for element in elements if isinstance(element, dict)
    }
    facades = _assembly_facade_index(dims.doc)
    levels = _assembly_level_index(dims.doc)
    block = massing.doc.get("defaults")
    thickness = as_number(
        block.get(MASSING_FACADE_WALL_THICKNESS_LEAF.split(".", 1)[1])
        if isinstance(block, dict)
        else None
    )
    cuts = _assembly_rows(doc, "opening_cuts")
    problems = 0
    checked = 0
    seen: dict[str, str] = {}
    numbers: list[int] = []
    for entry in cuts:
        ident = entry.get("id")
        where = f"{location}::opening_cuts[{ident}]"
        if not isinstance(ident, str) or not ASSEMBLY_CUT_ID_RE.match(ident):
            report.fail("G-76", where, f"id {ident!r} does not match ^CUT-\\d{{3}}$")
            problems += 1
        elif ident in seen:
            report.fail("G-76", where, f"id {ident!r} is already used by {seen[ident]}")
            problems += 1
        else:
            seen[ident] = where
            numbers.append(int(ident.split("-")[1]))
        host_ref = entry.get("host_ref")
        if not isinstance(host_ref, str) or not host_ref:
            report.fail(
                "G-76",
                where,
                f"host_ref is {host_ref!r}. 07 section 9.8 G-38 makes the facade_wall envelope "
                "total -- one wall per (facade, level) -- so a cut with no host is a hole in "
                "the envelope, not a legitimate null",
            )
            problems += 1
            continue
        host = by_id.get(host_ref)
        if host is None or host.get("kind") != "facade_wall":
            report.fail(
                "G-76",
                where,
                f"host_ref {host_ref!r} is not a {MASSING_SPEC_NAME} facade_wall element; only a "
                "facade_wall is opaque enough to be cut and only it carries a storey to cut in",
            )
            problems += 1
            continue
        facade = facades.get(str(entry.get("facade")))
        level = levels.get(entry.get("level_index")) or levels.get(
            inum(entry.get("level_index"))
        )
        if facade is None or level is None:
            report.fail(
                "G-76",
                where,
                f"names facade {entry.get('facade')!r} / level {entry.get('level_index')!r}, which "
                f"{DIMENSIONS_SPEC_NAME} does not declare",
            )
            problems += 1
            continue
        checked += 1
        if not is_int(host.get("storey_index")) or host.get("storey_index") != (
            entry.get("level_index")
        ):
            report.fail(
                "G-76",
                where,
                f"is on level {entry.get('level_index')!r} but its host {host_ref!r} serves "
                f"storey {host.get('storey_index')!r}; a cut through a wall belonging to another "
                "storey removes geometry the opening never asked for",
                tols.tol_linear,
            )
            problems += 1
        u_range = entry.get("u_range_cm")
        v_range = entry.get("v_range_cm")
        depth = as_number(entry.get("depth_cm"))
        if not (isinstance(u_range, list) and len(u_range) == 2) or not (
            isinstance(v_range, list) and len(v_range) == 2
        ):
            report.fail(
                "G-76",
                where,
                f"u_range_cm {u_range!r} / v_range_cm {v_range!r} must each be a two-number "
                "array",
            )
            problems += 1
            continue
        if None in (as_number(u_range[0]), as_number(u_range[1]), as_number(v_range[0]),
                    as_number(v_range[1]), depth):
            report.fail("G-76", where, "carries a non-numeric range or depth")
            problems += 1
            continue
        if not as_number(u_range[0]) < as_number(u_range[1]):
            report.fail(
                "G-76",
                where,
                f"u_range_cm {u_range!r} is not ascending; 07 section 8.5 requires u0 < u1",
            )
            problems += 1
        band = _facade_wall_band(facade, thickness or 0.0, _footprint_toward(dims.doc))
        host_u0, host_u1 = _facade_wall_u_extent(host, facade, band)
        if host_u0 is None or host_u1 is None:
            report.skip(
                "G-76",
                where,
                "the host's own u extent is undecidable from its profile_cm, so the u bound "
                "cannot be evaluated for this row",
            )
        else:
            for value, label in ((u_range[0], "u0"), (u_range[1], "u1")):
                number = as_number(value)
                if number is None or (number < host_u0 - tols.linear) or (
                    number > host_u1 + tols.linear
                ):
                    report.fail(
                        "G-76",
                        where,
                        f"{label} {fmt_number(number)} lies outside host {host_ref!r}'s own u "
                        f"extent [{fmt_number(host_u0)}, {fmt_number(host_u1)}] within "
                        f"{tols.tol_linear}. A cutter off the end of its wall removes nothing and "
                        "reports success",
                        tols.tol_linear,
                    )
                    problems += 1
        storey_height = as_number(level.get("height_cm"))
        for value, label in ((v_range[0], "v0"), (v_range[1], "v1")):
            number = as_number(value)
            if number is None:
                continue
            if number < -tols.linear or (
                storey_height is not None and number > storey_height + tols.linear
            ):
                report.fail(
                    "G-76",
                    where,
                    f"{label} {fmt_number(number)} lies outside the host's own local v extent "
                    f"[0, {fmt_number(storey_height)}] within {tols.tol_linear}. v is measured "
                    "from the level base, which is the frame the grid is written in",
                    tols.tol_linear,
                )
                problems += 1
        if thickness is None:
            report.skip(
                "G-76",
                where,
                f"{MASSING_SPEC_NAME} declares no positive {MASSING_FACADE_WALL_THICKNESS_LEAF}, "
                "so the depth bound cannot be evaluated for this row",
            )
        elif depth is None or depth < thickness - tols.linear:
            report.fail(
                "G-76",
                where,
                f"depth_cm {fmt_number(depth)} < {MASSING_FACADE_WALL_THICKNESS_LEAF} "
                f"{fmt_number(thickness)} within {tols.tol_linear}; a cutter shallower than the "
                "wall leaves the opening uncut with no error anywhere",
                tols.tol_linear,
            )
            problems += 1
        if entry.get("kind") not in ASSEMBLY_CUT_KINDS:
            report.fail(
                "G-76",
                where,
                f"kind {entry.get('kind')!r} is not one of {', '.join(ASSEMBLY_CUT_KINDS)}. A cut "
                "is named by its role, never by the modifier class that will implement it "
                "(07 sections 8.5 / 11 / 12)",
            )
            problems += 1
    if numbers and numbers != sorted(numbers):
        report.fail(
            "G-76",
            f"{location}::opening_cuts",
            "ids are not ascending",
        )
        problems += 1
    if problems == 0 and checked:
        report.ok(
            "G-76",
            location,
            f"{checked} cuts, every host_ref a facade_wall and every u / v / depth inside that "
            f"host's own extent within {tols.tol_linear}",
            tols.tol_linear,
        )


def _footprint_toward(dims: Any) -> tuple[float, float]:
    """The footprint centre, the reference every "inward" decision is measured against."""
    site = dims.get("site") if isinstance(dims, dict) else None
    ring = site.get("footprint_cm") if isinstance(site, dict) else None
    points = [p for p in ring or [] if isinstance(p, list) and len(p) == 2]
    if not points:
        return 0.0, 0.0
    xs = [as_number(p[0]) or 0.0 for p in points]
    ys = [as_number(p[1]) or 0.0 for p in points]
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0


def _facade_wall_u_extent(
    host: Any, facade: dict, band: Optional[tuple[float, float, float, float]]
) -> tuple[Optional[float], Optional[float]]:
    """The host wall's own ``u`` extent, facade-local, or ``(None, None)``.

    The wall's plan rectangle is projected onto the run unit measured from
    ``start_corner_cm``, so ``u = 0`` is the corner the grid's ``u`` is measured from and no
    offset is added by hand.
    """
    profile = host.get("profile_cm") if isinstance(host, dict) else None
    if not isinstance(profile, list) or len(profile) < 4:
        return None, None
    start = facade.get("start_corner_cm")
    end = facade.get("end_corner_cm")
    if not (isinstance(start, list) and len(start) == 2 and isinstance(end, list) and len(end) == 2):
        return None, None
    sx, sy = as_number(start[0]), as_number(start[1])
    ex, ey = as_number(end[0]), as_number(end[1])
    if None in (sx, sy, ex, ey):
        return None, None
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy)
    if length <= 0.0:
        return None, None
    ux, uy = dx / length, dy / length
    values: list[float] = []
    for point in profile:
        if not (isinstance(point, list) and len(point) == 2):
            return None, None
        px, py = as_number(point[0]), as_number(point[1])
        if px is None or py is None:
            return None, None
        values.append((px - sx) * ux + (py - sy) * uy)
    return min(values), max(values)


def _g77_opening_bijection(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-77. One opening, one cut -- and both directions fail.

    The arithmetic is checked too, because a cut with a plausible-looking ``u_range_cm`` that
    does not match its opening's own ``position_cm`` and ``width_cm`` is the exact defect
    G-62 was written to catch on the grid, one stage downstream.
    """
    doc = record.doc
    location = record.label
    dims = session.dimensions
    if dims is None or not dims.ok or not isinstance(dims.doc, dict):
        report.skip(
            "G-77",
            location,
            f"cannot run: {DIMENSIONS_SPEC_NAME} is absent or unreadable, so openings[] cannot be "
            "enumerated and the join cannot be decided in either direction",
        )
        return
    openings = {
        str(opening.get("id")): opening
        for opening in _p5_rows(dims.doc, "openings")
        if isinstance(opening.get("id"), str)
    }
    cuts = _assembly_rows(doc, "opening_cuts")
    counts: dict[str, int] = {}
    for cut in cuts:
        key = str(cut.get("opening_id"))
        counts[key] = counts.get(key, 0) + 1
    problems = 0
    for opening_id, count in sorted(counts.items()):
        if count != 1:
            report.fail(
                "G-77",
                location,
                f"opening {opening_id!r} has {count} cuts; exactly one, never 'one or more' -- a "
                "second cut on the same opening means two different u ranges were authored for "
                "one rectangle and only one of them is the opening",
            )
            problems += 1
    orphan_cuts = sorted(key for key in counts if key not in openings)
    for opening_id in orphan_cuts[:10]:
        report.fail(
            "G-77",
            location,
            f"a cut names opening {opening_id!r}, which {DIMENSIONS_SPEC_NAME} does not declare; "
            f"{len(orphan_cuts)} such cut(s)",
        )
        problems += 1
    missing = sorted(key for key in openings if key not in counts)
    if missing:
        report.fail(
            "G-77",
            location,
            f"{len(missing)} opening(s) have no cut at all: {_p5_ids(missing)}. An uncut opening is "
            "a blank wall with no error anywhere else in the chain",
        )
        problems += 1
    for cut in cuts:
        opening = openings.get(str(cut.get("opening_id")))
        if opening is None:
            continue
        where = f"{location}::{cut.get('id')}"
        position = as_number(opening.get("position_cm"))
        width = as_number(opening.get("width_cm"))
        u_range = cut.get("u_range_cm")
        if (
            position is not None
            and width is not None
            and isinstance(u_range, list)
            and len(u_range) == 2
        ):
            for index, expected in ((0, position - width / 2.0), (1, position + width / 2.0)):
                if not close(u_range[index], expected, tols.linear):
                    report.fail(
                        "G-77",
                        where,
                        f"u_range_cm[{index}] {fmt_number(as_number(u_range[index]))} != "
                        f"[position_cm - width_cm/2, position_cm + width_cm/2] "
                        f"[{fmt_number(expected)}] of opening {opening.get('id')!r} within "
                        f"{tols.tol_linear}",
                        tols.tol_linear,
                    )
                    problems += 1
        v_range = cut.get("v_range_cm")
        if isinstance(v_range, list) and len(v_range) == 2:
            for index, key in ((0, "sill_cm"), (1, "head_cm")):
                if not close(v_range[index], opening.get(key), tols.linear):
                    report.fail(
                        "G-77",
                        where,
                        f"v_range_cm[{index}] {fmt_number(as_number(v_range[index]))} != "
                        f"{key} {fmt_number(as_number(opening.get(key)))} of opening "
                        f"{opening.get('id')!r} within {tols.tol_linear}",
                        tols.tol_linear,
                    )
                    problems += 1
    if problems == 0:
        report.ok(
            "G-77",
            location,
            f"{len(cuts)} cuts for {len(openings)} openings, one to one in both directions, every "
            f"u and v recomputed from the opening within {tols.tol_linear}",
            tols.tol_linear,
        )


def _g78_scatter(record: LoadedFile, session: Session, report: Report) -> None:
    """G-78. Scatter ranges are ordered, the seed is in the closed range, refs resolve."""
    doc = record.doc
    location = record.label
    massing = session.massing
    registry = session.components_registry
    known_elements: set[str] = set()
    if massing is not None and massing.ok and isinstance(massing.doc, dict):
        known_elements = {
            str(element.get("id"))
            for element in _elements_of(massing.doc)
            if isinstance(element.get("id"), str)
        }
    known_components = set(_assembly_component_kinds(session))
    if not known_elements:
        report.skip(
            "G-78",
            location,
            f"cannot run: {MASSING_SPEC_NAME} is absent or unreadable, so target_ref and "
            "model_refs have nothing to resolve against",
        )
        return
    rows = _assembly_rows(doc, "scatter")
    problems = 0
    seen: set[str] = set()
    for entry in rows:
        ident = entry.get("id")
        where = f"{location}::scatter[{ident}]"
        if not isinstance(ident, str) or not ASSEMBLY_SCATTER_ID_RE.match(ident):
            report.fail("G-78", where, f"id {ident!r} does not match ^SCT-\\d{{3}}$")
            problems += 1
        elif ident in seen:
            report.fail("G-78", where, f"id {ident!r} is already used")
            problems += 1
        else:
            seen.add(ident)
        seed = entry.get("seed")
        if not is_int(seed) or not ASSEMBLY_SEED_MIN <= seed <= ASSEMBLY_SEED_MAX:
            report.fail(
                "G-78",
                where,
                f"seed {seed!r} is not an integer in {ASSEMBLY_SEED_MIN}..{ASSEMBLY_SEED_MAX}. The "
                "range is closed on purpose: a seed outside it is either the P0 typo'd constant "
                "or an uninitialised draw, and both make a rebuild a different scene",
            )
            problems += 1
        for low_key, high_key, low, high, note in (
            (
                "scale_from",
                "scale_to",
                as_number(entry.get("scale_from")),
                as_number(entry.get("scale_to")),
                "0 < scale_from <= scale_to",
            ),
            (
                "rotation_from_deg",
                "rotation_to_deg",
                as_number(entry.get("rotation_from_deg")),
                as_number(entry.get("rotation_to_deg")),
                "rotation_from_deg <= rotation_to_deg",
            ),
        ):
            if low is None or high is None or low > high or (low <= 0.0 and "scale" in low_key):
                report.fail(
                    "G-78",
                    where,
                    f"{low_key}={entry.get(low_key)!r} / {high_key}={entry.get(high_key)!r} "
                    f"violates {note}",
                )
                problems += 1
        limit = entry.get("instance_count_limit")
        if not is_int(limit) or limit <= 0:
            report.fail(
                "G-78",
                where,
                f"instance_count_limit {limit!r} is not an integer > 0; it is the ceiling the "
                "builder and Max both honour, so 0 would mean 'place nothing' and -1 'no ceiling'",
            )
            problems += 1
        guard_rail = as_number((doc.get("defaults") or {}).get("instance_limit_guard"))
        if guard_rail is not None and is_int(limit) and limit > guard_rail:
            report.fail(
                "G-78",
                where,
                f"instance_count_limit {limit} exceeds defaults.instance_limit_guard "
                f"{fmt_number(guard_rail)}; the guard exists so a corrupt row cannot ask Max "
                "for more instances than the project is allowed",
            )
            problems += 1
        density = as_number(entry.get("distribution_density_pattern"))
        if density is None or not 0.0 <= density <= 1.0:
            report.fail(
                "G-78",
                where,
                f"distribution_density_pattern {entry.get('distribution_density_pattern')!r} is "
                "not a number in 0..1",
            )
            problems += 1
        target = entry.get("target_ref")
        if target not in known_elements:
            report.fail(
                "G-78",
                where,
                f"target_ref {target!r} does not resolve to a {MASSING_SPEC_NAME} element id",
            )
            problems += 1
        models = entry.get("model_refs")
        if not isinstance(models, list) or not models:
            report.fail(
                "G-78",
                where,
                f"model_refs {models!r} is not an array with at least one entry; a scatter with "
                "no model places nothing and still reports success",
            )
            problems += 1
        else:
            for ref in models:
                if ref not in known_elements and ref not in known_components:
                    report.fail(
                        "G-78",
                        where,
                        f"model_ref {ref!r} resolves in neither {MASSING_SPEC_NAME} nor "
                        f"{REGISTRY_SPEC_NAME}",
                    )
                    problems += 1
        if not isinstance(entry.get("collision_avoid"), bool):
            report.fail(
                "G-78",
                where,
                f"collision_avoid {entry.get('collision_avoid')!r} is not a boolean; leaving it "
                "unset is how interpenetrating scatter ships",
            )
            problems += 1
    if problems == 0 and rows:
        report.ok(
            "G-78",
            location,
            f"{len(rows)} scatter row(s): seeds in {ASSEMBLY_SEED_MIN}..{ASSEMBLY_SEED_MAX}, "
            "ranges ordered, every target and model ref resolved",
        )


# ---- G-79 .. G-81: the emitted script, SKIP with a reason at lint time -------- #


def _g79_no_layer_code(record: LoadedFile, report: Report) -> None:
    """G-79. No layer-assignment statement in the emitted MAXScript. SKIP at lint time.

    Nine routes were ruled out by execution on 2026-10-05: ``LayerManager`` in this build
    exposes only ``newLayerFromName`` / ``getLayerFromName`` / ``getLayer`` and has no
    setter; ``node.layer`` throws ``Property is read-only: layer`` for a string, an integer
    index and a ``LayerProperties`` mixin; ``3dsmax-mcp_manage_layers``' action vocabulary
    is exactly ``{list, create, delete}``, calibrated by observing that ``create`` and
    ``delete`` return *distinct* argument errors; and ``3dsmax-mcp_set_object_property``
    with ``property=layer`` emits ``node.layer = <value>`` and dies the same way, while a
    positive control on the same tool with ``property=pos`` succeeded.

    So ``layer_map`` is **data**, and the rule is a build-time refusal: a builder that
    applies layers is a FAIL, not a silent no-op. A lint run has no emitted script to read,
    and reporting PASS here would be the one dishonest outcome available.
    """
    report.skip(
        "G-79",
        record.label,
        "not evaluable at lint time. G-79 is a property of the emitted assembly.ms, and a "
        "static JSON file cannot observe a script it did not write. Enforced at build time "
        "instead: scripts/place_components.py refuses to write a script containing node.layer, "
        "a LayerManager call other than newLayerFromName, .setLayer(, setProperty #layer, "
        ".layerIndex, LayerProperties or any of six other tokens. A check that cannot be "
        "evaluated reports SKIP with its reason, never a silent PASS (07 section 9.6)",
    )


def _g80_emitted_census(record: LoadedFile, report: Report) -> None:
    """G-80. The emitted census. SKIP with its reason, by construction.

    G-80 asks whether the emitted script counted what it placed, prototyped and committed and
    threw on a mismatch. None of that exists at lint time: ``assembly.ms`` is produced by
    ``scripts/place_components.py`` from the very JSON being linted, and a static reader that
    cannot see it has no verdict. This is the table-shaped analogue of G-54, and the reason
    P5's sliver defect could not ship.

    The predicate is not duplicated here: the builder asserts the same three counts on the
    script it has just written and refuses on a mismatch.
    """
    report.skip(
        "G-80",
        record.label,
        "not evaluable at lint time. G-80 is a census of the emitted assembly.ms -- placed "
        "instances, prototypes and committed cuts against the three tables -- and a static JSON "
        "file cannot observe a script it did not write. Enforced at build time instead, by "
        "scripts/place_components.py refusing to write a script whose census needles are absent "
        "and whose per-function addModifier counts it has itself chunked. A check that cannot "
        "be evaluated reports SKIP with its reason, never a silent PASS (07 section 9.6)",
    )


def _g81_bounded_stack(record: LoadedFile, report: Report) -> None:
    """G-81. No call adds more than five modifiers; no node's stack exceeds ten.

    Both numbers are **measured**, not inferred. On 2026-10-05 the bounded ladder was run
    deliberately on a clean empty scene: ``Extrude`` and ``Bevel`` throw on ``addModifier``
    (``mods=0``), five rungs are clean in 38 ms, ten are clean in 28 ms, and **twenty** froze
    Max on the main thread until the bridge stopped answering, Max had to be killed and the
    machine rebooted. The exact breaking point between ten and twenty is not established and
    must never be re-measured.

    So the rule is a build-time refusal with two halves, and a lint run has no script to
    read: SKIP with its reason, never a PASS.
    """
    report.skip(
        "G-81",
        record.label,
        "not evaluable at lint time. G-81 constrains the modifier stack of the emitted "
        "assembly.ms, and a static JSON file cannot observe a script it did not write. Enforced "
        "at build time instead, by scripts/place_components.py refusing to write a script that "
        "contains addModifier at all -- the stage emits ZERO modifiers, because openings are cut "
        "by tiling the wall with solid cells rather than by a Boolean modifier, which was measured "
        "unusable in this build (Boolean() throws, BooleanMod() carries Voxel Map's paramblock, and "
        "the native bridge attaches a Boolean whose operand is never set). Measured 2026-10-05: 20 "
        "rungs on one node froze Max until the machine rebooted, so zero is a construction rather "
        "than a tuning. A check that cannot be evaluated reports SKIP with its reason, never a "
        "silent PASS (07 section 9.6)",
    )


def _assembly_facade_walls(session: Session) -> dict[str, dict[str, Any]]:
    """``{element id: element}`` for every ``facade_wall`` in ``massing.json``, if loaded."""
    massing = session.by_name("massing")
    if massing is None or not isinstance(massing.doc, dict):
        return {}
    return {
        str(element.get("id")): element
        for element in (massing.doc.get("elements") or [])
        if isinstance(element, dict) and element.get("kind") == "facade_wall"
    }


def _wall_cells(record: LoadedFile, report: Report) -> list[dict[str, Any]]:
    rows = record.doc.get("wall_cells")
    if not isinstance(rows, list):
        report.skip(
            "G-82",
            record.label,
            "wall_cells[] is absent. It was added when wall tiling replaced the Boolean "
            "modifier; a file without it predates that change and cannot be checked",
        )
        return []
    return [row for row in rows if isinstance(row, dict)]


def _cell_geometry(
    cell: dict[str, Any], linear: float
) -> tuple[float, float, float, float, float, float] | None:
    plan = cell.get("plan_rect_cm")
    z_range = cell.get("z_range_cm")
    if not isinstance(plan, list) or len(plan) != 4:
        return None
    if not isinstance(z_range, list) or len(z_range) != 2:
        return None
    try:
        x0, y0, x1, y1 = (float(value) for value in plan)
        z0, z1 = (float(value) for value in z_range)
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(value) for value in (x0, y0, x1, y1, z0, z1)):
        return None
    return (min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1))


def _g82_wall_tiling_volume(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-82. The cells must tile each host exactly: cells == host minus openings.

    This is the rule that replaces "the boolean committed". A Boolean modifier that removed
    nothing left the wall's volume untouched and the build reported success -- measured
    2026-10-05, where the old census read ``cut_count=16`` with an empty modifier stack. A
    volume identity cannot be satisfied by a cut that did not happen, so it is the check
    that would have caught it.
    """
    linear = tols.linear
    cells = _wall_cells(record, report)
    if not cells:
        return
    walls = _assembly_facade_walls(session)
    if not walls:
        report.skip(
            "G-82",
            record.label,
            "massing.json declares no facade_wall element, so there is no host for a cell to "
            "tile and the volume identity is undecidable",
        )
        return

    cuts = record.doc.get("opening_cuts")
    cuts = [row for row in cuts if isinstance(row, dict)] if isinstance(cuts, list) else []
    by_host: dict[str, list[dict[str, Any]]] = {}
    for cell in cells:
        by_host.setdefault(str(cell.get("host_ref")), []).append(cell)

    bad = 0
    for host_id, host_cells in sorted(by_host.items()):
        wall = walls.get(host_id)
        if wall is None:
            report.fail(
                "G-82",
                record.label,
                f"wall_cells[] names host {host_id!r}, which massing.json does not declare as a "
                "facade_wall",
            )
            bad += 1
            continue
        ring = wall.get("profile_cm")
        z_range = wall.get("z_range_cm")
        if not isinstance(ring, list) or not ring or not isinstance(z_range, list):
            report.fail("G-82", record.label, f"facade_wall {host_id!r} has no usable geometry")
            bad += 1
            continue
        try:
            xs = [float(point[0]) for point in ring]
            ys = [float(point[1]) for point in ring]
            wz0, wz1 = float(z_range[0]), float(z_range[1])
        except (TypeError, ValueError, IndexError):
            report.fail("G-82", record.label, f"facade_wall {host_id!r} has non-numeric geometry")
            bad += 1
            continue
        wx0, wx1 = min(xs), max(xs)
        wy0, wy1 = min(ys), max(ys)
        wall_volume = (wx1 - wx0) * (wy1 - wy0) * abs(wz1 - wz0)
        thickness = min(wy1 - wy0, wx1 - wx0)

        cell_volume = 0.0
        for cell in host_cells:
            geometry = _cell_geometry(cell, linear)
            if geometry is None:
                report.fail(
                    "G-82",
                    record.label,
                    f"wall cell {cell.get('id')!r} is not four plan numbers plus a two-number z "
                    "range",
                )
                bad += 1
                continue
            x0, y0, z0, x1, y1, z1 = geometry
            if x1 - x0 <= 0 or y1 - y0 <= 0 or z1 - z0 <= 0:
                report.fail(
                    "G-82",
                    record.label,
                    f"wall cell {cell.get('id')!r} is degenerate: x[{x0}, {x1}] "
                    f"y[{y0}, {y1}] z[{z0}, {z1}]",
                )
                bad += 1
                continue
            cell_volume += (x1 - x0) * (y1 - y0) * (z1 - z0)
            if z0 < min(wz0, wz1) - linear or z1 > max(wz0, wz1) + linear:
                report.fail(
                    "G-82",
                    record.label,
                    f"wall cell {cell.get('id')!r} spans z [{z0}, {z1}], outside host "
                    f"{host_id!r}'s [{min(wz0, wz1)}, {max(wz0, wz1)}]",
                )
                bad += 1

        opening_volume = 0.0
        for cut in cuts:
            if str(cut.get("host_ref")) != host_id:
                continue
            u_range = cut.get("u_range_cm")
            v_range = cut.get("v_range_cm")
            if not isinstance(u_range, list) or not isinstance(v_range, list):
                continue
            if len(u_range) != 2 or len(v_range) != 2:
                continue
            try:
                run_length = abs(float(u_range[1]) - float(u_range[0]))
                v_length = abs(float(v_range[1]) - float(v_range[0]))
            except (TypeError, ValueError):
                continue
            # An opening is cut clean through, so its volume carries the wall's thickness.
            opening_volume += run_length * thickness * v_length

        expected = wall_volume - opening_volume
        if abs(cell_volume - expected) > linear * linear:
            report.fail(
                "G-82",
                record.label,
                f"host {host_id}: cells total {cell_volume:g} cm3 but wall {wall_volume:g} minus "
                f"openings {opening_volume:g} is {expected:g} cm3; a difference of "
                f"{cell_volume - expected:g} cm3 means the cells do not tile the wall -- a gap "
                "(unbuilt material) or an overlap (double-counted material)",
            )
            bad += 1

    if not bad:
        report.ok(
            "G-82",
            record.label,
            f"{len(cells)} cell(s) across {len(by_host)} host(s) tile wall-minus-openings exactly",
        )


def _g83_wall_cell_thickness(
    record: LoadedFile, session: Session, tols: P5Tolerances, report: Report
) -> None:
    """G-83. Every cell carries its wall's full thickness.

    A tiling of solid cells cannot express a partial-depth opening, so a cell that stops
    short of the wall's face is a defect rather than a style choice. Stated here because the
    alternative -- a silent partial-depth hole -- is exactly the class of near-miss this
    grammar exists to make a build failure.
    """
    linear = tols.linear
    cells = _wall_cells(record, report)
    if not cells:
        return
    walls = _assembly_facade_walls(session)
    if not walls:
        report.skip(
            "G-83",
            record.label,
            "massing.json declares no facade_wall element, so a cell's wall has no thickness to "
            "be measured against",
        )
        return

    by_host: dict[str, list[dict[str, Any]]] = {}
    for cell in cells:
        by_host.setdefault(str(cell.get("host_ref")), []).append(cell)

    bad = 0
    checked = 0
    for host_id, host_cells in sorted(by_host.items()):
        wall = walls.get(host_id)
        if wall is None:
            continue
        ring = wall.get("profile_cm")
        if not isinstance(ring, list) or not ring:
            continue
        try:
            xs = [float(point[0]) for point in ring]
            ys = [float(point[1]) for point in ring]
        except (TypeError, ValueError, IndexError):
            continue
        wx0, wx1 = min(xs), max(xs)
        wy0, wy1 = min(ys), max(ys)
        thin_is_y = (wy1 - wy0) <= (wx1 - wx0)
        for cell in host_cells:
            geometry = _cell_geometry(cell, linear)
            if geometry is None:
                continue
            x0, y0, _z0, x1, y1, _z1 = geometry
            checked += 1
            if thin_is_y:
                off = max(abs(y0 - wy0), abs(y1 - wy1))
            else:
                off = max(abs(x0 - wx0), abs(x1 - wx1))
            if off > linear:
                report.fail(
                    "G-83",
                    record.label,
                    f"wall cell {cell.get('id')!r} misses its host {host_id}'s full thickness by "
                    f"{off:g} cm. A tiling of solid cells cannot express a partial-depth "
                    "opening, so a cell must span the wall exactly",
                )
                bad += 1

    if not bad and checked:
        report.ok(
            "G-83",
            record.label,
            f"{checked} cell(s) each carry their wall's full thickness",
        )


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def guard(rule: str, location: str, report: Report, fn: Callable[..., None], *args: Any) -> None:
    """Run one check, converting an internal error into a FAIL row.

    ``07`` says a validation failure is a row, not a traceback. That also has to
    hold for a bug in this script: a malformed file, a surprising type or a
    zero-length array must never abort the run, and the remaining checks must
    still report what they can see.
    """
    try:
        fn(*args, report)
    except Exception as exc:  # noqa: BLE001 - a check must never propagate
        report.fail(
            rule,
            location,
            f"internal error in this validator while running {rule} "
            f"({RULE_TITLES.get(rule, '')}): {type(exc).__name__}: {exc}. The rule was not "
            "evaluated; fix the validator, do not trust the rest of its row.",
        )


def run_checks(session: Session, report: Report) -> None:
    for record in session.files:
        guard("G-7", record.label, report, check_file_hygiene, record)
        if record.fatal is not None:
            continue
        guard("G-1", record.label, report, check_envelope, record, session)
        guard("G-8", record.label, report, check_unit_lint, record)
        guard("G-16", record.label, report, check_ranges, record)
        guard("G-17", record.label, report, check_geometry, record, session)
        if record.spec is not None and record.spec.name == "dimensions":
            guard("G-9", record.label, report, check_origins_coverage, record)
            guard("G-10", record.label, report, check_origin_pairing, record, session)
        if record.spec is not None and record.spec.name == "massing":
            guard("G-34", record.label, report, check_massing_rules, record, session)
        if record.spec is not None and record.spec.name == "nurbs":
            guard("G-41", record.label, report, check_nurbs_rules, record, session)
        if record.spec is not None and record.spec.name == "facade_grids":
            guard("G-57", record.label, report, check_facade_rules, record, session)
        if record.spec is not None and record.spec.name == "components_registry":
            guard("G-65", record.label, report, check_component_rules, record, session)
        if record.spec is not None and record.spec.name == "assembly":
            guard("G-71", record.label, report, check_assembly_rules, record, session)

    assumptions = session.assumptions
    if assumptions is not None and assumptions.ok and isinstance(assumptions.doc, dict):
        guard("G-11", assumptions.label, report, check_ledger_ids, assumptions, "assumptions", "A")
        guard("G-12", assumptions.label, report, check_ledger_matches_spec, assumptions,
              "assumptions", session)
        guard("G-13", assumptions.label, report, check_ledger_bijection, assumptions,
              "assumptions", "assumed", session)
        guard("G-15", assumptions.label, report, check_assumptions_complete, assumptions, session)

    conflicts = session.conflicts
    if conflicts is not None and conflicts.ok and isinstance(conflicts.doc, dict):
        guard("G-11", conflicts.label, report, check_ledger_ids, conflicts, "conflicts", "C")
        guard("G-12", conflicts.label, report, check_ledger_matches_spec, conflicts,
              "conflicts", session)
        guard("G-13", conflicts.label, report, check_ledger_bijection, conflicts,
              "conflicts", "conflict", session)
        guard("G-14", conflicts.label, report, check_conflicts_complete, conflicts, session)

    guard("G-31", "(cross-file)", report, check_cross_file, session)
    guard("G-33", "(tolerances)", report, check_tolerances_declared, session)
    guard("G-1", "(inventory)", report, check_inventory, session)


def check_inventory(session: Session, report: Report) -> None:
    """Report which inventory files are present, missing or unreadable.

    A ``dimensions.json`` that is absent is a FAIL: without it nothing downstream
    can be built. 07 section 9.6 draws the same line for every file 07 section 4
    marks ``defined`` -- its absence is a FAIL, not an informational SKIP. A file
    still marked ``reserved`` stays an informational SKIP (07 S-4): no builder
    reads it, so its absence is not a defect. ``state`` and ``owner`` here are
    read from the inventory table above, which is this validator's transcription
    of section 4 -- the reference file is never opened at runtime.
    """
    for spec in SPEC_INVENTORY:
        if spec.name in {"dimensions", "assumptions", "conflicts_resolved"}:
            continue
        if session.by_name(spec.name) is not None:
            continue
        if session.recipes_only:
            report.skip(
                "G-1",
                f"{spec.name}.json",
                f"absent; this run targets a recipe template library (every loaded file is a "
                f"recipe), and a template is not a project, so {spec.name} is not expected",
            )
            continue
        if spec.state == "defined":
            report.fail(
                "G-1",
                f"{spec.name}.json",
                f"absent; 07 section 4 marks it {spec.state} (owner {spec.owner}), so a "
                "builder reads it and its absence is a FAIL, not a SKIP (07 section 9.6)",
            )
        else:
            report.skip(
                "G-1",
                f"{spec.name}.json",
                f"absent; 07 section 4 marks it {spec.state} (owner {spec.owner}), so no "
                "builder reads it yet",
            )


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def label_for(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def discover(directory: Path, report: Optional[Report] = None) -> list[Path]:
    """Collect the pipeline spec files in ``directory`` and its ``pipeline/`` child."""
    found: list[Path] = []
    search_dirs = [directory]
    pipeline = directory / "pipeline"
    if pipeline.is_dir():
        search_dirs.insert(0, pipeline)
    for search in search_dirs:
        for path in sorted(search.glob("*.json")):
            if path.is_file():
                found.append(path)
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in found:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def load_session(
    paths: Sequence[Path], root: Path, report: Report, require_dimensions: bool = True
) -> Session:
    records: list[LoadedFile] = []
    for path in paths:
        if path.stem not in SPEC_BY_NAME:
            record = LoadedFile(path=path, label=label_for(path, root), fatal=None)
            schema = path.parent.name if path.parent.name in SPEC_BY_NAME else None
            if schema is not None:
                loaded = load_spec_file(path, record.label)
                loaded.spec = SPEC_BY_NAME[schema]
                loaded.recipe = True
                records.append(loaded)
                continue
            records.append(record)
            continue
        records.append(load_spec_file(path, label_for(path, root)))
    if records and all(record.recipe for record in records):
        require_dimensions = False
    session = Session(files=records)
    if require_dimensions and session.dimensions is None:
        broken = next(
            (r for r in records if r.path.stem == "dimensions" and r.fatal), None
        )
        if broken is not None:
            report.fail(
                "G-1",
                broken.label,
                f"dimensions.json is unreadable ({broken.fatal}); every cross-file and "
                "geometry invariant is unevaluable and no builder may proceed",
            )
        else:
            report.fail(
                "G-1",
                str(root),
                "dimensions.json is not present; every cross-file and geometry invariant "
                "is unevaluable and no builder may proceed",
            )
    return session


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

HEADERS = ("RULE", "SEVERITY", "LOCATION", "TOLERANCE", "DETAIL")


def render_group(findings: Sequence[Finding]) -> str:
    rows = [
        (f.rule, f.severity, f.location, f.tolerance or "-", f.detail) for f in findings
    ]
    widths = [
        max(len(HEADERS[i]), max((len(row[i]) for row in rows), default=0))
        for i in range(len(HEADERS))
    ]
    lines = [
        "  ".join(HEADERS[i].ljust(widths[i]) for i in range(len(HEADERS))).rstrip(),
        "  ".join("-" * widths[i] for i in range(len(HEADERS))),
    ]
    for row in rows:
        lines.append("  ".join(row[i].ljust(widths[i]) for i in range(len(HEADERS))).rstrip())
    return "\n".join(lines)


def render_report(
    session: Session,
    report: Report,
    rule_filter: Optional[str],
    warnings_as_errors: bool,
) -> str:
    visible = [
        f
        for f in report.findings
        if rule_filter is None or f.rule == rule_filter
    ]
    counts = {status: sum(1 for f in visible if f.severity == status) for status in _SEVERITY_ORDER}
    linear, area, angle, source = session.tolerances()
    targets = [r.label for r in session.files if r.ok] or ["(none)"]

    lines = [
        "validate_specs  --  references/07-spec-grammar.md"
        f"  (supported schema major {SUPPORTED_SCHEMA_MAJOR})",
        "targets         " + ", ".join(targets),
        f"tolerances      linear {linear} cm | area {area} m2 | angle {angle} deg"
        f"   [source: {source}]",
        "                the run default, not the value of every row: a file that declares",
        "                its own tolerances block (07 section 8.1) is read from that file, so",
        "                every geometry row names the tolerance it used; range checks are",
        "                exact (07 section 9.5) and G-27's width<bay is a strict comparison",
    ]
    if rule_filter:
        lines.append(f"rule filter     {rule_filter}")
    if warnings_as_errors:
        lines.append("warnings        promoted to FAIL by --warnings-as-errors")
    lines.append("")

    order = list(_SEVERITY_ORDER)
    for severity in order:
        findings = [f for f in visible if f.severity == severity]
        if severity == STATUS_PASS and rule_filter is None:
            lines.append(f"PASS  {len(findings)}")
        else:
            lines.append(f"{severity}  {len(findings)}")
        if not findings:
            lines.append("  (none)")
        else:
            lines.append(render_group(findings))
        lines.append("")

    summary = (
        f"PASS {counts[STATUS_PASS]} / FAIL {counts[STATUS_FAIL]} "
        f"/ WARN {counts[STATUS_WARN]} / SKIP {counts[STATUS_SKIP]}"
    )
    lines.append(summary)
    if counts[STATUS_FAIL]:
        lines.append("exit 1 -- at least one FAIL row")
    else:
        lines.append("exit 0 -- no FAIL rows" + (" (WARN present)" if counts[STATUS_WARN] else ""))
    return "\n".join(lines)


def render_json(
    session: Session,
    report: Report,
    rule_filter: Optional[str],
    warnings_as_errors: bool,
    root: Path,
) -> str:
    linear, area, angle, source = session.tolerances()
    findings = [
        {
            "rule": f.rule,
            "title": RULE_TITLES.get(f.rule, ""),
            "severity": f.severity,
            "location": f.location,
            "path": f.location.split("::", 1)[1] if "::" in f.location else "",
            "tolerance": f.tolerance,
            "detail": f.detail,
            "cross_file": f.rule in CROSS_FILE_RULES,
        }
        for f in report.findings
        if rule_filter is None or f.rule == rule_filter
    ]
    payload = {
        "grammar": "references/07-spec-grammar.md",
        "schema_major_supported": SUPPORTED_SCHEMA_MAJOR,
        "rule_filter": rule_filter,
        "warnings_as_errors": warnings_as_errors,
        "build_gate": session.build_gate,
        "allow_draft": session.allow_draft,
        "targets": [r.label for r in session.files if r.ok],
        "unreadable": [
            {"file": r.label, "error": r.fatal} for r in session.files if not r.ok
        ],
        "tolerances": {
            "linear_cm": linear,
            "area_m2": area,
            "angle_deg": angle,
            "source": source,
        },
        "findings": findings,
        "summary": {
            status: sum(1 for f in findings if f["severity"] == status)
            for status in _SEVERITY_ORDER
        },
        "exit_code": 1
        if any(f["severity"] == STATUS_FAIL for f in findings)
        else 0,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main(argv: Optional[Sequence[str]] = None) -> int:
    global session_build_gate, session_allow_draft

    parser = argparse.ArgumentParser(
        description="Validate spec files against references/07-spec-grammar.md (G-1..G-83).",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("specs") / "pipeline",
        help="Directory holding the pipeline specs (default ./specs/pipeline).",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Validate one file; siblings are loaded from the same directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit the report as JSON instead of a table.",
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        dest="warnings_as_errors",
        help="Promote every WARN row (including the G-8 unit lint) to FAIL.",
    )
    parser.add_argument(
        "--rule",
        default=None,
        help="Run a single invariant, e.g. --rule G-18 (debugging aid).",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        dest="build_gate",
        help="Enforce the 07 G-4 lock gate: a non-locked file becomes FAIL.",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        dest="allow_draft",
        help="Draft work in progress: report a non-locked status and move on.",
    )
    args = parser.parse_args(argv)

    session_build_gate = args.build_gate
    session_allow_draft = args.allow_draft

    if args.rule is not None:
        rule = args.rule.strip().upper()
        if rule not in RULE_TITLES:
            known = ", ".join(RULE_TITLES)
            print(
                f"error: unknown rule {args.rule!r}. Known rules: {known}",
                file=sys.stderr,
            )
            return 2
        rule_filter: Optional[str] = rule
    else:
        rule_filter = None

    report = Report(warnings_as_errors=args.warnings_as_errors)

    if args.file is not None:
        target = args.file
        if not target.is_file():
            print(f"error: --file {target} does not exist or is not a file", file=sys.stderr)
            return 2
        root = target.parent
        siblings = discover(root)
        paths = [target] + [p for p in siblings if p.resolve() != target.resolve()]
        session = load_session(paths, root, report)
    else:
        root = args.dir
        if not root.is_dir():
            print(f"error: --dir {root} is not a directory", file=sys.stderr)
            return 2
        paths = discover(root)
        if not paths:
            print(
                f"error: no spec files found under {root}. Looked for the 07 section 4 "
                "inventory (*.json) in the directory and in its pipeline/ child.",
                file=sys.stderr,
            )
            return 2
        session = load_session(paths, root, report)

    session.build_gate = args.build_gate
    session.allow_draft = args.allow_draft

    ignored = [r.label for r in session.files if r.spec is None and r.fatal is None]
    if ignored:
        report.skip(
            "G-1",
            ", ".join(ignored),
            "not a file in the 07 section 4 inventory (e.g. project.json); ignored",
        )

    run_checks(session, report)

    if args.as_json:
        print(render_json(session, report, rule_filter, args.warnings_as_errors, root))
    else:
        print(render_report(session, report, rule_filter, args.warnings_as_errors))
    return 1 if report.counts()[STATUS_FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
