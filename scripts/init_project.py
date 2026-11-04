#!/usr/bin/env python3
"""Scaffold a project workdir for the 3ds Max architectural/NURBS pipeline.

Creates ``<dir>/<project>/`` with fresh pipeline specs, or seeds them from an
examples directory, plus ``specs/recipes/``, ``specs/export/``, ``snippets/``
and a ``project.json`` manifest. Standard library only, no network.

WHY THIS SCRIPT CANNOT TOUCH 3DS MAX
------------------------------------
It writes JSON. It does not read, set or detect anything in 3ds Max, and it
records no plugin, renderer or scene fact. ``project.json`` names the *target*
application version from 07 section 11 (3ds Max 2026, a verified fact) and stops
there: **the renderer is detected at build time by P7 and stored in
``materials.json``, never assumed here** (07 section 4.2, PLAN section 4.2).
Scaffolding a renderer here would be exactly the "assumption creep" the repo
risk list forbids.

WHAT A FRESH SCAFFOLD ACTUALLY SATISFIES
----------------------------------------
Every emitted spec file is envelope-complete JSON with the six envelope keys in
order. A fresh project is deliberately incomplete and must not be built before
its draft inputs are authored and locked:

* ``dimensions.json`` is a small **internally consistent** single-storey bay, not
  a set of blanks. The footprint, grid, core, levels, roof and facades reconcile,
  so G-16..G-30 and G-32 all evaluate and pass. Its ``status`` is ``draft`` --
  that is the honest state of a project with no brief behind it -- so G-4 reports
  a WARN in lint mode and a FAIL under ``--build``.
* ``massing.json`` (P3), ``facade_grids.json`` and ``components_registry.json`` (P5)
  are **computed, not authored**, so the empty draft placeholders have no
  provenance. ``assembly.json`` is also an empty draft placeholder; the current
  builder computes legacy assembly only, not the selected poly route.
* ``nurbs.json`` (P4) is the exception: it is **hand-authored**. ``build_nurbs.py``
  reads it and emits the normalised spec plus the MAXScript; it refuses when the
  file is absent. The stub is still empty and ``draft``, and its ``source.reference``
  says so -- the distinction matters because there is no generator to go and run.
* ``walls.json`` is a separate draft domain spec selecting
  ``closed_inner_contour_shell_v2`` by default (or ``legacy_cells_v1`` /
  ``poly_surface_shell_v1`` via ``--wall-route``). Its closed v2 storey contour
  is consistent with dimensions.json levels and facades.
  A seeded historical example with no wall selector remains legacy.
* reserved files (P6..P9) carry the envelope plus the key list 07 section 4
  promises for them and are otherwise empty. Per 07 S-4 no builder reads them,
  so their body is reported SKIP rather than validated.
* ``assumptions.json`` carries the seven entries a scaffold genuinely needs: the
  documented 07 section 5 defaults that a human is most likely to forget are
  recorded as ``assumed`` so they become an ``A-nnn`` audit trail rather than a
  silent value.

SAFETY BOUNDARY
---------------
``--force`` does not migrate wall routes or authorize overwriting edited, locked,
seeded or otherwise unverified walls. Fresh scaffolds record a wall-content hash
for a later unmodified-draft check; older manifests without that hash fail closed.
Every used seed is parsed strictly before destination creation, including historical
no-wall seeds: duplicate keys, lossy/underflowed numbers and excessive nesting are
refused rather than normalized into apparently clean output. Valid no-selector
seeds retain their legacy route and existing source re-stamping behavior.
Preflight detects existing links and hardlinks. Each output is written through an
exclusively created sibling staging file and replaced only after path/state checks;
an ordinary staging/write/replace failure does not truncate that destination's old
bytes. Earlier completed replacements are not rolled back: the project as a whole
is NOT transactional. Parent-path swaps and hostile concurrent mutation are not
supported or proven safe. Do not run against a concurrently modified project.

Exit codes
----------
    0   every planned file written, or --dry-run completed
    1   an internal consistency check failed (the audit trail was not preserved)
    2   usage error, unreadable path, or a file that would be overwritten
        without --force

Usage
-----
    python scripts/init_project.py --project my_pavilion
    python scripts/init_project.py --project my_pavilion --dir path/to/workdir [--force]
    python scripts/init_project.py --project my_pavilion --from examples
    python scripts/init_project.py --project my_pavilion --dry-run
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import math
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional, Sequence

# --------------------------------------------------------------------------- #
# Constants declared by references/07-spec-grammar.md
# --------------------------------------------------------------------------- #

GENERATOR = "scripts/init_project.py"
GENERATOR_VERSION = "1.0"
SCHEMA_VERSION = "1.0"
TARGET_MAX_VERSION = "2026"  # 07 section 11, verified by live execution

_ID_RE = re.compile(r'"[AC]-\d{3}"')

ENVELOPE_ORDER = (
    "schema_version",
    "spec",
    "project",
    "units",
    "source",
    "status",
)

#: Defined and reserved project files. A fresh project scaffolds all of them;
#: a historical seed without walls.json stays legacy instead of inventing walls.
#: ``owner`` is recorded in the source reference of a reserved file.
INVENTORY: tuple[tuple[str, str, str], ...] = (
    ("dimensions.json", "P2a", "defined"),
    ("conflicts_resolved.json", "P2a", "defined"),
    ("assumptions.json", "P2a", "defined"),
    ("massing.json", "P3", "defined"),
    ("nurbs.json", "P4", "defined"),
    ("facade_grids.json", "P5", "defined"),
    ("components_registry.json", "P5", "defined"),
    ("walls.json", "Phase16-P2", "defined"),
    ("assembly.json", "P6", "defined"),
    ("materials.json", "P7", "reserved"),
    ("qa.json", "P8", "defined"),
    ("export.json", "P9", "reserved"),
)

#: Files required when seeding from the historical worked example. Its two
#: CSVs are not spec files and are rebuilt by scripts/facade_tables.py; a wall
#: file is copied separately only when the source actually contains one.
SEEDED_FROM_EXAMPLES: tuple[str, ...] = (
    "dimensions.json",
    "assumptions.json",
    "conflicts_resolved.json",
    "massing.json",
    "nurbs.json",
    "facade_grids.json",
    "components_registry.json",
    "assembly.json",
)

# Unlike the historical, required example files, walls.json is optional in a
# seed: its absence is the legacy route, not an invitation to invent a selector.
POLY_WALL_TECHNIQUE = "poly_surface_shell_v1"
LEGACY_WALL_TECHNIQUE = "legacy_cells_v1"
CLOSED_CONTOUR_SHELL_V2_TECHNIQUE = "closed_inner_contour_shell_v2"
WALL_TECHNIQUES = (CLOSED_CONTOUR_SHELL_V2_TECHNIQUE, LEGACY_WALL_TECHNIQUE, POLY_WALL_TECHNIQUE)
MAX_SAFE_JSON_INTEGER = (1 << 53) - 1
MAX_JSON_CONTAINER_DEPTH = 128
MAX_JSON_FLOAT_TOKEN_LENGTH = 1024

#: Reserved-file top-level keys, verbatim from the 07 section 4 table, with the
#: container 07 section 8 describes for each. The kind is NOT invented: "array" is
#: used where section 8 describes a list ("one entry per ..."), "object" where it
#: describes a map. ``renderer`` is an empty object on purpose -- 07 section 8.6
#: says "never assumed", and an empty object claims nothing about the renderer.
RESERVED_KEYS: dict[str, tuple[tuple[str, str], ...]] = {
    "massing.json": (
        ("tolerances", "tolerances"),
        ("origin_inputs", "array"),
        ("origins", "origins"),
        ("storeys", "array"),
        ("elements", "array"),
        ("site_pad", "object"),
        ("grouping", "array"),
    ),
    "facade_grids.json": (
        ("tolerances", "tolerances"),
        ("origin_inputs", "array"),
        ("origins", "origins"),
        ("facades", "array"),
        ("axes", "array"),
        ("panels", "array"),
        ("panel_types", "array"),
    ),
    "components_registry.json": (
        ("tolerances", "tolerances"),
        ("origin_inputs", "array"),
        ("origins", "origins"),
        ("components", "array"),
        ("families", "array"),
    ),
    "assembly.json": (
        ("tolerances", "tolerances"),
        ("origin_inputs", "array"),
        ("placements", "array"),
        ("cuts", "array"),
        ("scatters", "array"),
        ("layer_map", "object"),
    ),
    "materials.json": (
        ("tolerances", "tolerances"),
        ("origin_inputs", "array"),
        ("renderer", "object"),
        ("materials", "array"),
        ("uv_rules", "object"),
    ),
    "export.json": (
        ("tolerances", "tolerances"),
        ("origin_inputs", "array"),
        ("exports", "array"),
        ("tessellation", "object"),
        ("delivery", "object"),
    ),
}

#: 07 section 3.3. These are the arithmetic tolerances every equality check uses.
TOLERANCES: dict[str, float] = {"linear_cm": 0.5, "area_m2": 0.05, "angle_deg": 0.01}

#: 07 section 7.1 proposes R1..R7; ``references/10-conflict-resolution.md`` (P2b)
#: owns the canonical definitions and must adopt these verbatim or regenerate the
#: file. The scaffold carries the proposed set with the same pending-adoption note
#: as the worked example so nothing downstream silently treats them as final.
PRECEDENCE_RULES: tuple[tuple[str, str, str], ...] = (
    (
        "R1",
        "CODE-SUPREMACY",
        "A statutory, regulatory or code requirement outranks every user statement, "
        "including an explicit one.",
    ),
    (
        "R2",
        "SPECIFICITY",
        "Among competing user statements of the same class, the one that is more "
        "specific wins: a value tied to a named level, element or condition beats a "
        "bare global value.",
    ),
    (
        "R3",
        "QUANTITY-OVER-SUMMARY",
        "A stated total loses to the stated parts that produce it. Parts are "
        "measurements; totals are usually summaries.",
    ),
    (
        "R4",
        "BUILDABILITY",
        "A value that cannot be built - negative dimension, head above floor-to-floor, "
        "negative clearance, element outside its host - loses to any value that can be "
        "built.",
    ),
    (
        "R5",
        "MODULE-ALIGNMENT",
        "A value that preserves the stated dimensional module or grid outranks one "
        "that breaks it.",
    ),
    (
        "R6",
        "LATER-STATEMENT",
        "Same class, same specificity, and no rule above discriminates: the statement "
        "appearing later in the source wins.",
    ),
)

NON_CONFLICT_FALLBACK: tuple[str, str, str] = (
    "R7",
    "DEFAULT-FILL",
    "A documented default from references/09-defaults.md may fill a silence but may "
    "never decide a conflict. A default that appears in a conflicts entry is a bug.",
)

PENDING_ADOPTION_NOTE = (
    "PENDING ADOPTION. The rule ids and names below are PROPOSED in "
    "references/07-spec-grammar.md section 7.1 and must be adopted verbatim by "
    "references/10-conflict-resolution.md (P2b). If P2b renames or re-numbers any "
    "rule, the rules_invoked arrays in this file and every origin_ref chain in "
    "dimensions.json must be updated in the same change. A rules_invoked entry is "
    "always a bare rule id (R1..R7) so the name can move without touching this file."
)

# --------------------------------------------------------------------------- #
# The scaffold geometry. Documented defaults where 07 section 5 gives one, and a
# single square-ish bay where it does not -- chosen so every derived value
# recomputes and every range holds. This is a starting point, not a design.
# --------------------------------------------------------------------------- #

FOOTPRINT_CM: list[list[float]] = [[0.0, 0.0], [900.0, 0.0], [900.0, 600.0], [0.0, 600.0]]
FOOTPRINT_AREA_M2 = 54.0
X_BAY_CM = [450.0, 450.0]
Y_BAY_CM = [300.0, 300.0]
CORE_FOOTPRINT_CM: list[list[float]] = [[0.0, 300.0], [450.0, 300.0], [450.0, 600.0], [0.0, 600.0]]
CORE_AREA_M2 = 13.5
LEVEL_HEIGHT_CM = 400.0
PARAPET_HEIGHT_CM = 60.0

#: Scaffold assumptions. Each names the silence it fills, per 07 section 6.1, and
#: records ``confidence: low`` because that is the honest reading: every one of
#: these is a placeholder standing in for a brief nobody has read yet. All are the
#: documented 07 section 5 defaults, which is precisely why they belong in the
#: ledger instead of sitting in the spec as unlabelled values.
SCAFFOLD_ASSUMPTIONS: tuple[dict[str, Any], ...] = (
    {
        "field_path": "site.plot_rotation_deg",
        "value": 0.0,
        "reason": (
            "No brief has been captured, so there is no stated orientation and no north "
            "arrow to read. The scaffold models the building with its local X axis on world "
            "X and its local Y axis on world Y; 0 deg means the facade grid is axis-aligned "
            "and the south facade faces -Y."
        ),
        "invalidated_by": (
            "A brief with a north arrow, a stated true-north bearing, or a requirement that "
            "the entrance face a street at an angle."
        ),
        "recheck_stage": "P3",
        "downstream_stages": ["P3", "P4", "P5"],
    },
    {
        "field_path": "site.setback_cm",
        "value": 300.0,
        "reason": (
            "No plot boundary is supplied, so there is no edge to measure a clearance from. "
            "The 07 section 5 default is carried so a later stage has a site pad, paving and "
            "planting somewhere to live; the footprint itself is unaffected."
        ),
        "invalidated_by": (
            "A plot boundary, a boundary wall, or a planning constraint giving a different "
            "minimum distance."
        ),
        "recheck_stage": "P3",
        "downstream_stages": ["P3", "P6"],
    },
    {
        "field_path": "structure.column_section_cm",
        "value": [40.0, 40.0],
        "reason": (
            "No column size is stated anywhere in the input. The 07 section 5 default of a "
            "400 x 400 mm column is carried; it reads correctly against a 450 cm bay."
        ),
        "invalidated_by": (
            "A structural design, a load case, or a material change from steel to reinforced "
            "concrete."
        ),
        "recheck_stage": "P3",
        "downstream_stages": ["P3", "P6"],
    },
    {
        "field_path": "core.wall_thickness_cm",
        "value": 20.0,
        "reason": (
            "No core wall thickness is stated. The 07 section 5 default of 200 mm is carried, "
            "which suits a light framed core rather than the 250 mm a reinforced-concrete "
            "shear core would need."
        ),
        "invalidated_by": "A core type change, a supplier minimum, or a lightweight core.",
        "recheck_stage": "P3",
        "downstream_stages": ["P3", "P6"],
    },
    {
        "field_path": "roof.slope_deg",
        "value": 0.0,
        "reason": (
            "The input says nothing about drainage, so there is no fall to record. The 07 "
            "section 5 default is a flat deck; a pitch needs a drainage strategy first, and "
            "A-007 must be revisited with it."
        ),
        "invalidated_by": (
            "An external-gutter or flat-roof requirement, a local rainfall rule, or a stated "
            "drainage layout."
        ),
        "recheck_stage": "P3",
        "downstream_stages": ["P3", "P4", "P7"],
    },
    {
        "field_path": "roof.coping_overhang_cm",
        "value": 0.0,
        "reason": (
            "No coping detail exists in the input. The 07 section 5 default is a flush coping; "
            "a render needs an overhang to read the parapet as capped rather than as a wall."
        ),
        "invalidated_by": (
            "A specified coping profile, or a metal-cap rather than masonry-capping decision."
        ),
        "recheck_stage": "P3",
        "downstream_stages": ["P6", "P7"],
    },
    {
        "field_path": "roof.drainage",
        "value": "internal_downpipe",
        "reason": (
            "No drainage strategy is stated. The 07 section 5 default keeps rainwater out of "
            "the facade. Note it is not self-consistent with the 0 deg fall in A-005: a real "
            "project must set both together."
        ),
        "invalidated_by": (
            "A requirement for external downpipes, or a visible outlet requirement on the "
            "elevation."
        ),
        "recheck_stage": "P3",
        "downstream_stages": ["P3", "P6", "P7"],
    },
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def envelope(spec: str, project: str, kind: str, reference: str, status: str) -> dict[str, Any]:
    """The six envelope keys, in 07 section 3.1 order, and nothing after them.

    The order assertion is not decoration: 07 G-1 is about key order, and Python
    dicts preserve insertion order, so building the envelope in one place is the
    only way every scaffolded file gets it right.
    """
    doc: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "spec": spec,
        "project": project,
        "units": {"length": "cm", "angle": "deg"},
        "source": {"kind": kind, "reference": reference, "recorded_at": now_iso()},
        "status": status,
    }
    assert tuple(doc)[: len(ENVELOPE_ORDER)] == ENVELOPE_ORDER, doc.keys()
    return doc


def scaffold_reference(project: str, status: str) -> str:
    return (
        f"scaffold for project {project!r}; no user brief has been captured yet "
        f"({GENERATOR} {GENERATOR_VERSION}). Every value is a documented 07 section 5 "
        f"default or a single structural bay that keeps the derived values consistent. "
        f"Replace this text with the brief citation before status is set to {status!r}."
    )


def scaffold_dimensions(project: str) -> dict[str, Any]:
    """A single-storey bay that satisfies G-16..G-30 and G-32 as written."""
    doc: dict[str, Any] = envelope(
        "dimensions",
        project,
        "assumed",
        scaffold_reference(project, "locked"),
        "draft",
    )
    doc["tolerances"] = dict(TOLERANCES)
    doc["origins"] = {
        # building -- 07 section 5.3
        "building.typology": {"origin": "given"},
        "building.total_height_cm": {
            "origin": "derived",
            "derives_from": ["levels[0].elevation_cm", "levels[0].height_cm"],
        },
        "building.overall_height_cm": {
            "origin": "derived",
            "derives_from": ["building.total_height_cm", "roof.parapet_height_cm"],
        },
        "building.gross_floor_area_m2": {
            "origin": "derived",
            "derives_from": ["floor_plates[0].gross_area_m2"],
        },
        "building.net_floor_area_m2": {
            "origin": "derived",
            "derives_from": ["building.gross_floor_area_m2", "core.footprint_area_m2",
                             "core.spans_level_indices"],
        },
        # site -- 07 section 5.4
        "site.footprint_kind": {"origin": "given"},
        "site.footprint_cm": {"origin": "given"},
        "site.footprint_ccw": {"origin": "given"},
        "site.footprint_area_m2": {"origin": "derived", "derives_from": ["site.footprint_cm"]},
        "site.footprint_width_cm": {"origin": "derived", "derives_from": ["site.footprint_cm"]},
        "site.footprint_depth_cm": {"origin": "derived", "derives_from": ["site.footprint_cm"]},
        "site.ground_level_cm": {"origin": "given"},
        "site.plot_rotation_deg": {"origin": "assumed", "origin_ref": "A-001"},
        "site.plot_rotation_ref_axis": {"origin": "given"},
        "site.setback_cm": {"origin": "assumed", "origin_ref": "A-002"},
        # structure -- 07 section 5.5
        "structure.system": {"origin": "given"},
        "structure.grid_kind": {"origin": "given"},
        "structure.x_bay_cm": {"origin": "given"},
        "structure.y_bay_cm": {"origin": "given"},
        "structure.column_x_cm": {"origin": "derived", "derives_from": ["structure.x_bay_cm"]},
        "structure.column_y_cm": {"origin": "derived", "derives_from": ["structure.y_bay_cm"]},
        "structure.column_section_cm": {"origin": "assumed", "origin_ref": "A-003"},
        "structure.interior_column_count": {
            "origin": "derived",
            "derives_from": ["structure.column_x_cm", "structure.column_y_cm"],
        },
        # levels -- 07 section 5.6
        "levels[0].use": {"origin": "given"},
        "levels[0].elevation_cm": {"origin": "given"},
        "levels[0].height_cm": {"origin": "given"},
        # core -- 07 section 5.7
        "core.type": {"origin": "given"},
        "core.footprint_kind": {"origin": "given"},
        "core.footprint_cm": {"origin": "given"},
        "core.footprint_area_m2": {"origin": "derived", "derives_from": ["core.footprint_cm"]},
        "core.spans_level_indices": {"origin": "given"},
        "core.wall_thickness_cm": {"origin": "assumed", "origin_ref": "A-004"},
        # floor_plates -- 07 section 5.8
        "floor_plates[0].thickness_cm": {"origin": "given"},
        "floor_plates[0].gross_area_m2": {
            "origin": "derived",
            "derives_from": ["site.footprint_area_m2"],
        },
        "floor_plates[0].net_usable_area_m2": {"origin": "given"},
        # roof -- 07 section 5.9
        "roof.type": {"origin": "given"},
        "roof.deck_level_cm": {"origin": "derived", "derives_from": ["building.total_height_cm"]},
        "roof.deck_thickness_cm": {"origin": "given"},
        "roof.slope_deg": {"origin": "assumed", "origin_ref": "A-005"},
        "roof.parapet_height_cm": {"origin": "given"},
        "roof.parapet_thickness_cm": {"origin": "given"},
        "roof.coping_overhang_cm": {"origin": "assumed", "origin_ref": "A-006"},
        "roof.drainage": {"origin": "assumed", "origin_ref": "A-007"},
        # facades -- 07 section 5.10, collapsed per element (uniform derived origin)
        "facades[0]": {
            "origin": "derived",
            "derives_from": ["site.footprint_cm", "structure.x_bay_cm"],
        },
        "facades[1]": {
            "origin": "derived",
            "derives_from": ["site.footprint_cm", "structure.x_bay_cm"],
        },
        "facades[2]": {
            "origin": "derived",
            "derives_from": ["site.footprint_cm", "structure.y_bay_cm"],
        },
        "facades[3]": {
            "origin": "derived",
            "derives_from": ["site.footprint_cm", "structure.y_bay_cm"],
        },
        # openings -- 07 section 5.11, may be empty
        "openings": {"origin": "given"},
    }

    doc["building"] = {
        "id": "BLD-01",
        "name": project,
        "typology": "unspecified",
        "total_height_cm": LEVEL_HEIGHT_CM,
        "overall_height_cm": LEVEL_HEIGHT_CM + PARAPET_HEIGHT_CM,
        "gross_floor_area_m2": FOOTPRINT_AREA_M2,
        "net_floor_area_m2": FOOTPRINT_AREA_M2 - CORE_AREA_M2,
    }
    doc["site"] = {
        "id": "SITE-01",
        "footprint_kind": "polygon",
        "footprint_cm": [list(p) for p in FOOTPRINT_CM],
        "footprint_ccw": True,
        "footprint_area_m2": FOOTPRINT_AREA_M2,
        "footprint_width_cm": max(p[0] for p in FOOTPRINT_CM) - min(p[0] for p in FOOTPRINT_CM),
        "footprint_depth_cm": max(p[1] for p in FOOTPRINT_CM) - min(p[1] for p in FOOTPRINT_CM),
        "ground_level_cm": 0.0,
        "plot_rotation_deg": 0.0,
        "plot_rotation_ref_axis": "north",
        "setback_cm": 300.0,
    }
    doc["structure"] = {
        "id": "STR-01",
        "system": "unspecified",
        "grid_kind": "bay_spacing",
        "x_bay_cm": list(X_BAY_CM),
        "y_bay_cm": list(Y_BAY_CM),
        "column_x_cm": [450.0],
        "column_y_cm": [300.0],
        "column_section_cm": [40.0, 40.0],
        "interior_column_count": 1,
    }
    doc["levels"] = [
        {
            "index": 0,
            "id": "LVL-00",
            "use": "unspecified",
            "elevation_cm": 0.0,
            "height_cm": LEVEL_HEIGHT_CM,
        }
    ]
    doc["core"] = {
        "id": "CORE-01",
        "type": "service_core",
        "footprint_kind": "polygon",
        "footprint_cm": [list(p) for p in CORE_FOOTPRINT_CM],
        "footprint_area_m2": CORE_AREA_M2,
        "spans_level_indices": [0],
        "wall_thickness_cm": 20.0,
    }
    doc["floor_plates"] = [
        {
            "level_index": 0,
            "id": "FP-00",
            "thickness_cm": 30.0,
            "gross_area_m2": FOOTPRINT_AREA_M2,
            "net_usable_area_m2": FOOTPRINT_AREA_M2 - CORE_AREA_M2,
        }
    ]
    doc["roof"] = {
        "type": "flat_parapet",
        "deck_level_cm": LEVEL_HEIGHT_CM,
        "deck_thickness_cm": 30.0,
        "slope_deg": 0.0,
        "parapet_height_cm": PARAPET_HEIGHT_CM,
        "parapet_thickness_cm": 30.0,
        "coping_overhang_cm": 0.0,
        "drainage": "internal_downpipe",
    }
    # facades: N/S take x_bay_cm, E/W take y_bay_cm (07 section 5.10)
    depth = max(p[1] for p in FOOTPRINT_CM) - min(p[1] for p in FOOTPRINT_CM)
    width = max(p[0] for p in FOOTPRINT_CM) - min(p[0] for p in FOOTPRINT_CM)
    doc["facades"] = [
        {
            "id": "F-S",
            "name": "south",
            "direction_deg": 180.0,
            "start_corner_cm": [0.0, 0.0],
            "end_corner_cm": [width, 0.0],
            "length_cm": width,
            "bay_count": len(X_BAY_CM),
            "bay_width_cm": list(X_BAY_CM),
        },
        {
            "id": "F-N",
            "name": "north",
            "direction_deg": 0.0,
            "start_corner_cm": [0.0, depth],
            "end_corner_cm": [width, depth],
            "length_cm": width,
            "bay_count": len(X_BAY_CM),
            "bay_width_cm": list(X_BAY_CM),
        },
        {
            "id": "F-E",
            "name": "east",
            "direction_deg": 90.0,
            "start_corner_cm": [width, 0.0],
            "end_corner_cm": [width, depth],
            "length_cm": depth,
            "bay_count": len(Y_BAY_CM),
            "bay_width_cm": list(Y_BAY_CM),
        },
        {
            "id": "F-W",
            "name": "west",
            "direction_deg": 270.0,
            "start_corner_cm": [0.0, 0.0],
            "end_corner_cm": [0.0, depth],
            "length_cm": depth,
            "bay_count": len(Y_BAY_CM),
            "bay_width_cm": list(Y_BAY_CM),
        },
    ]
    doc["openings"] = []
    return doc


def scaffold_assumptions(project: str) -> dict[str, Any]:
    doc: dict[str, Any] = envelope(
        "assumptions",
        project,
        "assumed",
        "silences in an uncaptured brief; each entry names the silence it fills",
        "draft",
    )
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(SCAFFOLD_ASSUMPTIONS, start=1):
        entries.append(
            {
                "id": f"A-{index:03d}",
                "field_path": item["field_path"],
                "value": item["value"],
                "reason": item["reason"],
                "confidence": "low",
                "invalidated_by": item["invalidated_by"],
                "recheck_stage": item["recheck_stage"],
                "downstream_stages": list(item["downstream_stages"]),
            }
        )
    doc["assumptions"] = entries
    doc["cross_references"] = {
        "note": "Scaffold ledger. Non-assumption provenance is intentionally empty: there "
        "is no brief yet, so nothing is given and nothing is conflict-resolved. Conflict "
        "entries are written to conflicts_resolved.json, never here, and no id in this "
        "block may match a C- id.",
        "conflict_sourced_paths": [],
    }
    return doc


def scaffold_conflicts(project: str) -> dict[str, Any]:
    doc: dict[str, Any] = envelope(
        "conflicts_resolved",
        project,
        "assumed",
        "no input has been read, so no contradiction has been found; an empty conflicts "
        "array is a valid and meaningful result (07 section 7)",
        "draft",
    )
    doc["precedence_rules"] = {
        "note": PENDING_ADOPTION_NOTE,
        "evaluation_order": (
            "strict ladder, lowest id first; the first rule that discriminates between "
            "the competing sources wins"
        ),
        "rules": [
            {"id": rule_id, "name": name, "statement": statement}
            for rule_id, name, statement in PRECEDENCE_RULES
        ],
        "non_conflict_fallback": {
            "id": NON_CONFLICT_FALLBACK[0],
            "name": NON_CONFLICT_FALLBACK[1],
            "statement": NON_CONFLICT_FALLBACK[2],
        },
    }
    doc["conflicts"] = []
    return doc


def scaffold_massing(project: str) -> dict[str, Any]:
    """The P3 file. Structurally valid, deliberately empty.

    Unlike the reserved files this one is **computed, not authored**: it is written by
    ``scripts/build_spec.py --stage massing`` from a locked ``dimensions.json``. The stub
    exists so a fresh project lints clean and so the key order is visible, and it says so
    in ``source.reference`` -- hand-editing it produces a file no invariant can vouch for.
    """

    doc: dict[str, Any] = envelope(
        "massing",
        project,
        "derived",
        "empty stub written by init_project.py. massing.json is GENERATED by "
        "scripts/build_spec.py --stage massing from a locked dimensions.json; do not "
        "hand-edit it. Key order per references/07-spec-grammar.md section 8.1.",
        "draft",
    )
    doc["tolerances"] = dict(TOLERANCES)
    doc["origin_inputs"] = []
    doc["origins"] = {}
    doc["defaults"] = {}
    doc["storeys"] = []
    doc["elements"] = []
    doc["site_pad"] = {
        "ground_pad": None,
        "paving": None,
        "kerb": None,
        "layer": "00_SITE",
    }
    doc["grouping"] = []
    return doc


def scaffold_nurbs(project: str) -> dict[str, Any]:
    """The P4 file. Structurally valid, deliberately empty.

    Unlike ``massing.json`` and ``assembly.json``, ``nurbs.json`` is **hand-authored**.
    ``build_nurbs.py`` *consumes* it -- its own refusal message says so: "nurbs.json is
    hand-authored at P4 -- this stage reads it and emits the normalised spec plus the
    MAXScript, it does not compute the geometry." A stub that claimed the opposite
    would send an author looking for a generator that does not exist, and
    ``build_nurbs.py`` refuses outright when the file is absent.

    Three empty arrays, not a reserved key list: ``sections`` / ``surfaces`` /
    ``derivatives`` are real tables, and a promised skeleton of them would be a shape no
    invariant can vouch for. The 07 section 8.2 key order is still made visible here.

    Its ``status`` is ``draft``, which is what keeps G-41..G-49 honest: an empty
    array is still a leaf 07 section 5.2 asks for an ``origins`` entry for, so the
    stub cannot satisfy G-49 and 07 section 9.7 says a draft file is not evaluated.
    """

    doc: dict[str, Any] = envelope(
        "nurbs",
        project,
        "derived",
        "empty stub written by init_project.py. nurbs.json is hand-authored -- "
        "scripts/build_nurbs.py READS it and emits the normalised spec plus the "
        "MAXScript; it does not compute the geometry and refuses when this file is "
        "absent. Author it against references/07-spec-grammar.md section 8.2.",
        "draft",
    )
    doc["tolerances"] = dict(TOLERANCES)
    doc["origin_inputs"] = []
    doc["origins"] = {}
    doc["sections"] = []
    doc["surfaces"] = []
    doc["derivatives"] = []
    return doc


def scaffold_facade_grids(project: str) -> dict[str, Any]:
    """The P5 grid file. Structurally valid, deliberately empty.

    Same situation as ``massing.json`` one stage later: ``facade_grids.json`` is
    **computed, not authored** -- written by
    ``scripts/facade_tables.py --stage grids`` from a locked ``dimensions.json``
    and a locked ``massing.json``. The stub exists so a fresh project lints clean
    and so the 07 section 8.3 key order is visible, and it says so in
    ``source.reference``. Empty arrays, not a promised skeleton of them:
    ``facades`` / ``axes`` / ``panels`` / ``panel_types`` are real tables, and a
    skeleton of them would be a shape no invariant can vouch for.

    Its ``status`` is ``draft``, which is what keeps G-57..G-64 honest: an empty
    array is still a leaf 07 section 5.2 asks for an ``origins`` entry for, so the
    stub cannot satisfy G-64 and 07 section 9.7 says a draft file is not
    evaluated. It also cannot satisfy G-61 -- a facade with no panel is not a
    partition -- which is the rule that would otherwise fire on the stub alone.
    """

    doc: dict[str, Any] = envelope(
        "facade_grids",
        project,
        "derived",
        "empty stub written by init_project.py. facade_grids.json is GENERATED by "
        "scripts/facade_tables.py --stage grids from a locked dimensions.json and a locked "
        "massing.json; do not hand-edit it. Key order per references/07-spec-grammar.md "
        "section 8.3.",
        "draft",
    )
    doc["tolerances"] = dict(TOLERANCES)
    doc["origin_inputs"] = []
    doc["origins"] = {}
    doc["facades"] = []
    doc["axes"] = []
    doc["panels"] = []
    doc["panel_types"] = []
    return doc


def scaffold_components_registry(project: str) -> dict[str, Any]:
    """The P5 registry. Structurally valid, deliberately empty.

    Read by ``scripts/facade_tables.py --stage components`` and written by
    ``--stage all``; like the grid it is computed, not authored. ``defaults`` is an
    **empty object** on purpose. Its two keys -- ``panel_thickness_cm`` and
    ``joint_width_cm`` -- are the only values P5 assumes (09 ``D-CL-05`` and
    ``D-FM-10``), and each one needs a ledger entry before it can legally sit in a
    spec: G-10 pairs an ``assumed`` value with its ``origin_ref``. A stub that
    printed two numbers with no ledger entry would plant exactly the untraceable
    assumption the ledger exists to prevent, so it declares none and says where
    they come from.
    """

    doc: dict[str, Any] = envelope(
        "components_registry",
        project,
        "derived",
        "empty stub written by init_project.py. components_registry.json is GENERATED by "
        "scripts/facade_tables.py --stage components from an existing facade_grids.json; do not "
        "hand-edit it. Key order per references/07-spec-grammar.md section 8.4. The two assumed "
        "defaults (panel_thickness_cm, joint_width_cm, 09 D-CL-05 and D-FM-10) arrive with the "
        "builder and their assumptions.json ledger entries; a placeholder must not carry them "
        "without one.",
        "draft",
    )
    doc["tolerances"] = dict(TOLERANCES)
    doc["origin_inputs"] = []
    doc["origins"] = {}
    doc["defaults"] = {}
    doc["component_types"] = []
    doc["components"] = []
    doc["families"] = []
    return doc


def scaffold_walls(
    project: str,
    dimensions: dict[str, Any],
    wall_route: str = CLOSED_CONTOUR_SHELL_V2_TECHNIQUE,
) -> dict[str, Any]:
    """An explicitly selected wall-domain input, matching the chosen wall_route."""
    if wall_route == CLOSED_CONTOUR_SHELL_V2_TECHNIQUE:
        doc = envelope(
            "walls",
            project,
            "assumed",
            f"draft wall-domain scaffold from {GENERATOR}; storey boundary and facade "
            "segments match scaffold dimensions. Reference face is inner per Contract 20.",
            "draft",
        )
        doc["schema_version"] = "2.0"
        doc["tolerances"] = dict(dimensions["tolerances"])
        doc["origin_inputs"] = []
        doc["origins"] = {}
        doc["wall_technique"] = CLOSED_CONTOUR_SHELL_V2_TECHNIQUE
        doc["reference_face"] = "inner"
        doc["numeric_epsilon_cm"] = 0.001
        doc["numeric_unit_epsilon"] = 0.0001
        doc["storeys"] = [
            {
                "id": "storey_1",
                "name": "Ground Floor",
                "base_z_cm": 0.0,
                "top_z_cm": LEVEL_HEIGHT_CM,
                "wall_thickness_cm": 30.0,
                "reference_face": "inner",
                "vertices_cm": [list(p) for p in FOOTPRINT_CM],
                "segments": [
                    {
                        "id": "seg_south",
                        "start_vertex_index": 0,
                        "end_vertex_index": 1,
                        "facade_ref": "dimensions.json:facades:F-S",
                    },
                    {
                        "id": "seg_east",
                        "start_vertex_index": 1,
                        "end_vertex_index": 2,
                        "facade_ref": "dimensions.json:facades:F-E",
                    },
                    {
                        "id": "seg_north",
                        "start_vertex_index": 2,
                        "end_vertex_index": 3,
                        "facade_ref": "dimensions.json:facades:F-N",
                    },
                    {
                        "id": "seg_west",
                        "start_vertex_index": 3,
                        "end_vertex_index": 0,
                        "facade_ref": "dimensions.json:facades:F-W",
                    },
                ],
                "openings": [],
                "topology_budget": {
                    "max_grid_polygons": 128,
                    "max_base_active_polygons": 128,
                    "max_evaluated_triangles": 1024,
                },
            }
        ]
        return doc
    elif wall_route == POLY_WALL_TECHNIQUE:
        doc = envelope(
            "walls",
            project,
            "assumed",
            "draft wall-domain scaffold from init_project.py; no wall brief or geometry "
            "has been captured. The reference face and numerical epsilons remain pending.",
            "draft",
        )
        doc["schema_version"] = "1.0"
        doc["tolerances"] = dict(dimensions["tolerances"])
        doc["origin_inputs"] = []
        doc["origins"] = {}
        doc["wall_technique"] = POLY_WALL_TECHNIQUE
        doc["reference_face"] = None
        doc["numeric_epsilon_cm"] = None
        doc["numeric_unit_epsilon"] = None
        doc["blocks"] = []
        doc["wall_runs"] = []
        doc["openings"] = []
        doc["upper_returns"] = []
        return doc
    elif wall_route == LEGACY_WALL_TECHNIQUE:
        doc = envelope(
            "walls",
            project,
            "assumed",
            "draft legacy wall scaffold from init_project.py; legacy cells route selected.",
            "draft",
        )
        doc["schema_version"] = "1.0"
        doc["tolerances"] = dict(dimensions["tolerances"])
        doc["origin_inputs"] = []
        doc["origins"] = {}
        doc["wall_technique"] = LEGACY_WALL_TECHNIQUE
        doc["reference_face"] = None
        doc["numeric_epsilon_cm"] = None
        doc["numeric_unit_epsilon"] = None
        doc["blocks"] = []
        doc["wall_runs"] = []
        doc["openings"] = []
        doc["upper_returns"] = []
        return doc
    else:
        raise ValueError(f"unknown wall route {wall_route!r}; choices: {WALL_TECHNIQUES}")


def scaffold_assembly(
    project: str,
    wall_route: str = CLOSED_CONTOUR_SHELL_V2_TECHNIQUE,
) -> dict[str, Any]:
    """A draft assembly placeholder matching the selected wall route."""
    if wall_route == CLOSED_CONTOUR_SHELL_V2_TECHNIQUE:
        doc = envelope(
            "assembly",
            project,
            "derived",
            "empty v2 assembly placeholder written by init_project.py; not a produced assembly. "
            "Future assembly inputs include components_registry.json, world_table.csv, "
            "massing.json, dimensions.json and wall_surface.json.",
            "draft",
        )
        doc["tolerances"] = dict(TOLERANCES)
        doc["origin_inputs"] = []
        doc["origins"] = {}
        doc["defaults"] = {}
        doc["layer_map"] = {}
        doc["placements"] = []
        doc["scatter"] = []
        doc["wall_technique"] = CLOSED_CONTOUR_SHELL_V2_TECHNIQUE
        doc["wall_ref"] = "wall_surface.json"
        return doc
    elif wall_route == POLY_WALL_TECHNIQUE:
        doc = envelope(
            "assembly",
            project,
            "derived",
            "empty poly-route placeholder written by init_project.py; not a produced assembly. "
            "Future assembly inputs include components_registry.json, world_table.csv, "
            "massing.json, dimensions.json and wall_surface.json. The existing "
            "scripts/place_components.py supports closed_inner_contour_shell_v2 and legacy_cells_v1; "
            "poly_surface_shell_v1 is supported via scripts/build_wall_surface.py.",
            "draft",
        )
        doc["tolerances"] = dict(TOLERANCES)
        doc["origin_inputs"] = []
        doc["origins"] = {}
        doc["defaults"] = {}
        doc["layer_map"] = {}
        doc["placements"] = []
        doc["scatter"] = []
        doc["wall_technique"] = POLY_WALL_TECHNIQUE
        doc["wall_ref"] = "wall_surface.json"
        return doc
    elif wall_route == LEGACY_WALL_TECHNIQUE:
        doc = envelope(
            "assembly",
            project,
            "derived",
            "empty legacy assembly placeholder written by init_project.py; not a produced assembly. "
            "Legacy assembly inputs include components_registry.json, world_table.csv, "
            "massing.json and dimensions.json. Place components via scripts/place_components.py.",
            "draft",
        )
        doc["tolerances"] = dict(TOLERANCES)
        doc["origin_inputs"] = []
        doc["origins"] = {}
        doc["defaults"] = {}
        doc["layer_map"] = {}
        doc["placements"] = []
        doc["opening_cuts"] = []
        doc["wall_cells"] = []
        doc["scatter"] = []
        doc["wall_technique"] = LEGACY_WALL_TECHNIQUE
        return doc
    else:
        raise ValueError(f"unknown wall route {wall_route!r}; choices: {WALL_TECHNIQUES}")


def scaffold_qa(project: str) -> dict[str, Any]:
    """The P8 QA plan. Structurally valid draft QA plan under schema 1.1 compliant with G-87..G-90."""
    doc: dict[str, Any] = envelope(
        "qa",
        project,
        "assumed",
        f"draft QA plan scaffolded by {GENERATOR} for project {project!r}; author against "
        f"references/07-spec-grammar.md section 8.7.",
        "draft",
    )
    doc["schema_version"] = "1.1"
    doc["tolerances"] = {
        "linear_cm": 0.5,
        "area_m2": 0.05,
        "angle_deg": 0.01,
        "form": {
            "surface_deviation_cm": 0.5,
            "longitudinal_extent_cm": 0.5,
            "landmark_deviation_cm": 0.5,
        },
        "numerical": {
            "policy": "separate_bounds_v1",
            "solver_distance_cm": 0.001,
            "wire_length_cm": 0.0001,
            "wire_angle_deg": 0.001,
            "unit_factor_relative": 1e-06,
            "volume_roundoff_cm3": 0.01,
        },
        "volume": {
            "policy": "box_endpoint_propagation_v1",
            "endpoint_tolerance_ref": "tolerances.linear_cm",
        },
    }
    doc["origin_inputs"] = []
    doc["origins"] = {
        "profile": "assumed",
        "dependencies": "assumed",
        "scope": "assumed",
        "check_plan": "assumed",
        "sampling": "assumed",
        "limits": "assumed",
        "capture_plan": "assumed",
        "tolerances.form.surface_deviation_cm": "assumed",
        "tolerances.form.longitudinal_extent_cm": "assumed",
        "tolerances.form.landmark_deviation_cm": "assumed",
        "tolerances.numerical.solver_distance_cm": "assumed",
        "tolerances.numerical.wire_length_cm": "assumed",
        "tolerances.numerical.wire_angle_deg": "assumed",
        "tolerances.numerical.unit_factor_relative": "assumed",
        "tolerances.numerical.volume_roundoff_cm3": "assumed",
    }
    doc["profile"] = "form_precision_v1"
    doc["dependencies"] = [
        {
            "id": "DEP_DIMENSIONS",
            "format": "json",
            "file": "specs/pipeline/dimensions.json",
            "spec": "dimensions",
            "schema_version": "1.0",
        },
        {
            "id": "DEP_MASSING",
            "format": "json",
            "file": "specs/pipeline/massing.json",
            "spec": "massing",
            "schema_version": "1.0",
        },
        {
            "id": "DEP_NURBS",
            "format": "json",
            "file": "specs/pipeline/nurbs.json",
            "spec": "nurbs",
            "schema_version": "1.0",
        },
        {
            "id": "DEP_FACADE_GRIDS",
            "format": "json",
            "file": "specs/pipeline/facade_grids.json",
            "spec": "facade_grids",
            "schema_version": "1.0",
        },
        {
            "id": "DEP_COMPONENTS_REGISTRY",
            "format": "json",
            "file": "specs/pipeline/components_registry.json",
            "spec": "components_registry",
            "schema_version": "1.0",
        },
        {
            "id": "DEP_ASSEMBLY",
            "format": "json",
            "file": "specs/pipeline/assembly.json",
            "spec": "assembly",
            "schema_version": "1.0",
        },
    ]
    doc["scope"] = {
        "registry_ref": "dimensions.json:precision_targets",
        "targets": [
            {
                "id": "TGT_PROJECT",
                "kind": "project",
                "role": "project",
                "node_names": [],
            }
        ],
    }
    doc["check_plan"] = [
        {
            "id": "CHK_COVERAGE",
            "kind": "QA-V1-COVERAGE",
            "target_ref": "TGT_PROJECT",
            "tolerance_ref": "exact",
        }
    ]
    doc["sampling"] = {
        "policy": "domain_grid_v1",
        "version": "1",
        "grid_u": 5,
        "grid_v": 5,
        "landmarks_policy": "barrel_landmarks_v1",
        "selected_frame": 0,
    }
    doc["limits"] = {
        "max_rows_per_batch": 25,
        "max_targets": 50,
        "max_samples": 200,
        "max_calls": 50,
        "max_batch_seconds": 2.0,
        "max_total_seconds": 60.0,
        "max_solver_iterations": 100,
        "max_response_bytes": 1048576,
    }
    doc["capture_plan"] = []
    return doc


def scaffold_reserved(filename: str, project: str, owner: str) -> dict[str, Any]:
    spec = filename[: -len(".json")]
    doc: dict[str, Any] = envelope(
        spec,
        project,
        "assumed",
        f"reserved by references/07-spec-grammar.md section 4; owner stage {owner} has "
        f"not written this file. Its top-level keys are the promised shape only "
        f"(07 S-4) and no builder reads it yet.",
        "draft",
    )
    for key, kind in RESERVED_KEYS[filename]:
        if kind == "tolerances":
            doc[key] = dict(TOLERANCES)
        elif kind == "array":
            doc[key] = []
        else:
            doc[key] = {}
    return doc


def render_json(document: dict[str, Any]) -> str:
    """07 section 3.2: UTF-8, LF, exactly one trailing newline."""
    return json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


# --------------------------------------------------------------------------- #
# Plan
# --------------------------------------------------------------------------- #


class Plan:
    """The complete set of directories and files a run intends to write."""

    def __init__(self, root: Path, project: str, wall_route: str = CLOSED_CONTOUR_SHELL_V2_TECHNIQUE) -> None:
        self.root = root
        self.project = project
        self.wall_route = wall_route
        self.directories: list[Path] = [
            root,
            root / "specs",
            root / "specs" / "pipeline",
            root / "specs" / "recipes",
            root / "specs" / "export",
            root / "snippets",
        ]
        self.files: list[tuple[Path, str, str]] = []  # (path, kind, content)

    def add_file(self, path: Path, kind: str, content: str) -> None:
        self.files.append((path, kind, content))

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root.parent).as_posix()


def build_plan(
    project: str,
    root: Path,
    examples: Optional[Path],
    wall_route: str = CLOSED_CONTOUR_SHELL_V2_TECHNIQUE,
) -> Plan:
    if wall_route not in WALL_TECHNIQUES:
        raise ValueError(f"invalid wall route {wall_route!r}; choices: {WALL_TECHNIQUES}")
    plan = Plan(root, project, wall_route=wall_route)
    pipeline = root / "specs" / "pipeline"

    if examples is not None:
        source_walls = examples / "walls.json"
        source_has_walls = entry_present(source_walls)
        seed_texts = {
            filename: (examples / filename).read_text(encoding="utf-8")
            for filename in SEEDED_FROM_EXAMPLES
        }
        if source_has_walls:
            seed_texts["walls.json"] = source_walls.read_text(encoding="utf-8")
            validate_seed_projects(seed_texts)
        seed_documents: dict[str, dict[str, Any]] = {}
        for filename, _, _ in INVENTORY:
            if filename in SEEDED_FROM_EXAMPLES:
                document = rewrite_from_example(
                    seed_texts[filename], project,
                    preserve_source=source_has_walls,
                )
                seed_documents[filename] = document
                plan.add_file(pipeline / filename, "seeded from examples", render_json(document))
            elif filename == "walls.json" and source_has_walls:
                document = rewrite_from_example(
                    seed_texts["walls.json"], project,
                    preserve_source=True,
                )
                seed_documents[filename] = document
                plan.add_file(pipeline / filename, "seeded wall spec", render_json(document))
            elif filename == "qa.json":
                plan.add_file(
                    pipeline / filename,
                    "scaffold (draft QA plan)",
                    render_json(scaffold_qa(project)),
                )
        validate_seed_route(seed_documents.get("walls.json"), seed_documents["assembly.json"])
    else:
        dimensions = scaffold_dimensions(project)
        plan.add_file(
            pipeline / "dimensions.json",
            "scaffold",
            render_json(dimensions),
        )
        plan.add_file(
            pipeline / "assumptions.json",
            "scaffold",
            render_json(scaffold_assumptions(project)),
        )
        plan.add_file(
            pipeline / "conflicts_resolved.json",
            "scaffold",
            render_json(scaffold_conflicts(project)),
        )
        plan.add_file(
            pipeline / "massing.json",
            "stub (generated at build time by build_spec.py)",
            render_json(scaffold_massing(project)),
        )
        plan.add_file(
            pipeline / "nurbs.json",
            "stub (generated at build time by build_nurbs.py)",
            render_json(scaffold_nurbs(project)),
        )
        plan.add_file(
            pipeline / "facade_grids.json",
            "stub (generated at build time by facade_tables.py)",
            render_json(scaffold_facade_grids(project)),
        )
        plan.add_file(
            pipeline / "components_registry.json",
            "stub (generated at build time by facade_tables.py)",
            render_json(scaffold_components_registry(project)),
        )
        plan.add_file(
            pipeline / "walls.json",
            f"scaffold (draft {wall_route} wall domain)",
            render_json(scaffold_walls(project, dimensions, wall_route=wall_route)),
        )
        plan.add_file(
            pipeline / "assembly.json",
            f"stub (draft {wall_route} assembly; place via place_components.py)"
            if wall_route in (CLOSED_CONTOUR_SHELL_V2_TECHNIQUE, LEGACY_WALL_TECHNIQUE)
            else f"stub (draft {wall_route} assembly; build not implemented)",
            render_json(scaffold_assembly(project, wall_route=wall_route)),
        )
        plan.add_file(
            pipeline / "qa.json",
            "scaffold (draft QA plan)",
            render_json(scaffold_qa(project)),
        )
        for filename, owner, state in INVENTORY:
            if filename in ("assembly.json", "qa.json") or state != "reserved":
                continue
            plan.add_file(
                pipeline / filename,
                f"reserved ({owner})",
                render_json(scaffold_reserved(filename, project, owner)),
            )

    wall_hashes: dict[str, str] = {}
    if examples is None:
        for path, _, content in plan.files:
            if path == pipeline / "walls.json":
                wall_hashes[path.relative_to(root).as_posix()] = hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest()
    plan.add_file(
        root / "project.json",
        "manifest",
        render_json(build_manifest(project, root, [p for p, _, _ in plan.files], wall_hashes)),
    )
    return plan


def build_manifest(project: str, root: Path, files: Sequence[Path],
                   wall_hashes: dict[str, str]) -> dict[str, Any]:
    """The project manifest.

    Deliberately records only facts this script can justify: the project id, the
    schema revision, the generator, and the 3ds Max **target** version from 07
    section 11. It records no renderer, no plugin and no scene fact -- the renderer
    is detected at build time and stored in ``materials.json``.
    """
    manifest: dict[str, Any] = {
        "project": project,
        "schema_version": SCHEMA_VERSION,
        "created_at": now_iso(),
        "generator": GENERATOR,
        "generator_version": GENERATOR_VERSION,
        "grammar": "references/07-spec-grammar.md",
        "target": {
            "application": "3dsmax-mcp",
            "max_version": TARGET_MAX_VERSION,
            "length_unit": "cm",
            "angle_unit": "deg",
        },
        "notes": [
            "The renderer is NOT recorded here. 07 section 4 and PLAN section 4.2 require "
            "it to be detected at build time and stored in materials.json; assuming it at "
            "scaffold time is the assumption creep the repo risk list forbids.",
            "No plugin presence is recorded. Only a live probe establishes that, and the "
            "probe result belongs in a build artifact, not a manifest.",
            "specs/recipes/ and specs/export/ are created empty: 07 section 4 reserves "
            "recipe bodies to P4 and exports to P9.",
        ],
        # This list is necessary but not sufficient for --force. The separate
        # digest is recorded only for a fresh, unmodified wall scaffold.
        "files": sorted(
            [path.relative_to(root).as_posix() for path in files] + ["project.json"]
        ),
    }
    if wall_hashes:
        manifest["unmodified_wall_scaffold_sha256"] = dict(wall_hashes)
    return manifest


# --------------------------------------------------------------------------- #
# --from examples
# --------------------------------------------------------------------------- #


def collect_ids(document: Any) -> tuple[set[str], set[str]]:
    """Every ``A-nnn`` / ``C-nnn`` id and every ``origin_ref`` in a document."""
    text = json.dumps(document, ensure_ascii=False, sort_keys=True)
    ids: set[str] = set()
    refs: set[str] = set()
    for match in _ID_RE.finditer(text):
        ids.add(match.group(0))
    for entry in _iter_origin_entries(document):
        value = entry.get("origin_ref")
        if isinstance(value, str):
            refs.add(value)
    return ids, refs




def _iter_origin_entries(document: Any) -> list[dict[str, Any]]:
    origins = document.get("origins") if isinstance(document, dict) else None
    if not isinstance(origins, dict):
        return []
    return [obj for obj in origins.values() if isinstance(obj, dict)]


def parse_seed_json(text: str) -> Any:
    """Strictly parse every used seed/ownership document, regardless of wall route.

    Ambiguous historical files are intentionally refused, not silently repaired.
    Decimal round-trip equality is not a claim of exact binary representation.
    Unlike the validator parser, this copier also bounds floating-token magnitude.
    """
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_CONTAINER_DEPTH:
                raise ValueError(
                    f"JSON nesting exceeds the scaffold safety limit ({MAX_JSON_CONTAINER_DEPTH} containers)"
                )
        elif char in "]}":
            depth -= 1

    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON constant {value!r}")

    def finite_float(value: str) -> float:
        if len(value) > MAX_JSON_FLOAT_TOKEN_LENGTH:
            raise ValueError("JSON number exceeds the scaffold numeric token length limit")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"non-finite JSON number {value!r}")
        try:
            unchanged = Decimal(value) == Decimal(str(number))
        except InvalidOperation:
            unchanged = False
        if not unchanged:
            raise ValueError(f"JSON number {value!r} loses decimal precision when decoded")
        if abs(number) > MAX_SAFE_JSON_INTEGER:
            raise ValueError(f"JSON number {value!r} exceeds the exact integer safety range")
        return number

    def safe_integer(value: str) -> int:
        if len(value.lstrip("-")) > 16:
            raise ValueError("JSON integer exceeds the exact integer safety range")
        number = int(value)
        if abs(number) > MAX_SAFE_JSON_INTEGER:
            raise ValueError("JSON integer exceeds the exact integer safety range")
        return number

    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                shown = key if len(key) <= 100 else key[:100] + "..."
                raise ValueError(f"duplicate JSON object key {shown!r}")
            result[key] = value
        return result

    return json.loads(
        text, parse_constant=reject_constant, parse_float=finite_float,
        parse_int=safe_integer, object_pairs_hook=unique_pairs,
    )


def rewrite_from_example(
    text: str, project: str, *, preserve_source: bool = False,
) -> dict[str, Any]:
    """Re-stamp an example file onto a new project, preserving the audit trail.

    The project id is rewritten. For an explicit wall seed, ``preserve_source``
    keeps the complete original source object for *all* seeded specs. Historical
    no-wall seeds retain their existing source re-stamping behavior.
    Everything else is copied byte-for-byte in value terms -- in particular every
    ``A-nnn`` and ``C-nnn`` id and every ``origin_ref``, which *is* the audit
    trail. The caller asserts that after the rewrite.
    """
    document = parse_seed_json(text)
    if not isinstance(document, dict):
        raise ValueError("example spec is not a JSON object")
    before_ids, before_refs = collect_ids(document)
    document["project"] = project
    source = document.get("source")
    if isinstance(source, dict) and not preserve_source:
        # A `derived` file must keep naming the spec file it was computed from (07 G-6), so
        # the seeding note is appended to the original reference instead of replacing it.
        original = str(source.get("reference", "")).strip()
        note = (
            f"seeded from examples/ by {GENERATOR} for project {project!r}; the worked "
            "example pavilion-01 brief re-stamped onto this project id. Ledger ids "
            "(A-nnn / C-nnn) and every origin_ref are preserved verbatim; the audit trail "
            "now records this project."
        )
        if source.get("kind") == "derived" and original:
            source["reference"] = f"{original}. {note}"
        else:
            source["reference"] = note
        source["recorded_at"] = now_iso()
    after_ids, after_refs = collect_ids(document)
    if before_ids != after_ids or before_refs != after_refs:
        missing = sorted((before_ids | before_refs) - (after_ids | after_refs))
        raise ValueError(
            "the rewrite did not preserve the audit trail; lost " + ", ".join(missing)
        )
    return document


def validate_seed_projects(seed_texts: dict[str, str]) -> None:
    """Check each explicit-wall seed's original project before any rewrite.

    This is not a schema or provenance-content validation. Parsing every seeded
    document strictly also prevents duplicate project keys from being silently
    collapsed before comparing their identities.
    """
    identities: dict[str, str] = {}
    for filename, text in seed_texts.items():
        document = parse_seed_json(text)
        if not isinstance(document, dict):
            raise ValueError(f"seed {filename} is not a JSON object")
        project = document.get("project")
        if not isinstance(project, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", project):
            raise ValueError(f"seed {filename} has an invalid or missing project identity")
        identities[filename] = project
    if len(set(identities.values())) != 1:
        details = ", ".join(f"{name}={value!r}" for name, value in sorted(identities.items()))
        raise ValueError(f"seed project identities differ before re-stamping: {details}")


def validate_route_document(document: dict[str, Any], name: str) -> None:
    """Check the route document's envelope and wall table shape, not full G-93."""
    versions = ("1.0", "1.1", "2.0") if name == "walls" else ("1.0", "1.1")
    source = document.get("source")
    if (list(document)[:len(ENVELOPE_ORDER)] != list(ENVELOPE_ORDER)
            or document.get("spec") != name or document.get("schema_version") not in versions
            or not isinstance(document.get("project"), str) or not document["project"].strip()
            or document.get("units") != {"length": "cm", "angle": "deg"}
            or not isinstance(source, dict) or set(source) != {"kind", "reference", "recorded_at"}
            or source.get("kind") not in ("user_brief", "drawing", "image", "imported", "assumed", "derived")
            or not all(isinstance(source.get(key), str) and source[key].strip()
                       for key in ("reference", "recorded_at"))
            or document.get("status") not in ("draft", "locked", "superseded")):
        raise ValueError(f"{name}.json has an invalid route document envelope")
    if name == "walls":
        technique = document.get("wall_technique")
        if technique == CLOSED_CONTOUR_SHELL_V2_TECHNIQUE:
            if document.get("schema_version") != "2.0":
                raise ValueError(
                    f"closed_inner_contour_shell_v2 walls.json requires schema_version '2.0', "
                    f"found {document.get('schema_version')!r}"
                )
            keys = set(ENVELOPE_ORDER) | {"tolerances", "origin_inputs", "origins", "wall_technique",
                "reference_face", "numeric_epsilon_cm", "numeric_unit_epsilon", "storeys"}
            if (set(document) != keys or not isinstance(document["tolerances"], dict)
                    or set(document["tolerances"]) != {"linear_cm", "area_m2", "angle_deg"}
                    or not isinstance(document["origins"], dict)
                    or any(not isinstance(document[key], list) for key in ("origin_inputs", "storeys"))):
                raise ValueError("walls.json has an invalid route document shape")
        elif technique in (LEGACY_WALL_TECHNIQUE, POLY_WALL_TECHNIQUE):
            if document.get("schema_version") not in ("1.0", "1.1"):
                raise ValueError(
                    f"{technique} walls.json requires schema_version '1.0' or '1.1', "
                    f"found {document.get('schema_version')!r}"
                )
            keys = set(ENVELOPE_ORDER) | {"tolerances", "origin_inputs", "origins", "wall_technique",
                "reference_face", "numeric_epsilon_cm", "numeric_unit_epsilon", "blocks", "wall_runs",
                "openings", "upper_returns"}
            if (set(document) != keys or not isinstance(document["tolerances"], dict)
                    or set(document["tolerances"]) != {"linear_cm", "area_m2", "angle_deg"}
                    or not isinstance(document["origins"], dict)
                    or any(not isinstance(document[key], list) for key in
                           ("origin_inputs", "blocks", "wall_runs", "openings", "upper_returns"))):
                raise ValueError("walls.json has an invalid route document shape")
        else:
            raise ValueError(f"walls.json has invalid or missing wall_technique {technique!r}")


def validate_seed_route(walls: Optional[dict[str, Any]], assembly: Optional[dict[str, Any]]) -> None:
    """Validate the selected route and its echo before any destination is written."""
    selector = "wall_technique"
    wall_ref = "wall_ref"
    if walls is not None:
        validate_route_document(walls, "walls")
    if assembly is None:
        if walls is not None:
            route = walls.get(selector)
            if not isinstance(route, str) or route not in WALL_TECHNIQUES:
                raise ValueError(f"walls.json has invalid or missing wall_technique {route!r}")
        return
    validate_route_document(assembly, "assembly")
    if walls is None:
        if selector in assembly or wall_ref in assembly:
            raise ValueError("seed assembly declares a wall selector or wall_ref but walls.json is absent")
        return
    route = walls.get(selector)
    if not isinstance(route, str) or route not in WALL_TECHNIQUES:
        raise ValueError(f"seed walls.json has invalid or missing wall_technique {route!r}")
    placeholder = assembly.get("status") == "draft" and all(
        key not in assembly or assembly[key] in ({}, [])
        for key in ("origins", "defaults", "layer_map", "origin_inputs", "placements",
                    "opening_cuts", "wall_cells", "scatter")
    )
    if selector in assembly and assembly[selector] != route:
        raise ValueError("seed assembly wall_technique conflicts with walls.json")
    if not placeholder and assembly.get(selector) != route:
        raise ValueError("produced seed assembly must echo walls.json wall_technique")
    if route == LEGACY_WALL_TECHNIQUE:
        if wall_ref in assembly:
            raise ValueError("legacy seed assembly must not declare wall_ref")
        if not placeholder and any(not isinstance(assembly.get(key), list)
                                   for key in ("opening_cuts", "wall_cells")):
            raise ValueError("produced legacy seed assembly requires opening_cuts and wall_cells arrays")
    else:
        if wall_ref in assembly and assembly[wall_ref] != "wall_surface.json":
            raise ValueError(f"{route} seed assembly has an invalid wall_ref")
        if not placeholder and assembly.get(wall_ref) != "wall_surface.json":
            raise ValueError(f"produced {route} seed assembly must reference wall_surface.json")
        if "opening_cuts" in assembly or "wall_cells" in assembly:
            raise ValueError(f"{route} seed assembly must not declare legacy wall arrays")


def resolve_examples(candidate: Path, workdir: Path) -> Optional[Path]:
    """Find the examples directory: as given, then from the repo root, then CWD."""
    repo_root = Path(__file__).resolve().parent.parent
    for base in (Path.cwd(), workdir, repo_root):
        candidate_path = (base / candidate).resolve() if not candidate.is_absolute() else candidate
        if candidate_path.is_dir():
            return candidate_path
    return None


def entry_present(path: Path) -> bool:
    """Count broken links and other non-files as present, not as a missing route."""
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    return True


def is_link_or_reparse(info: Any) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def require_safe_path(path: Path, *, directory: bool) -> None:
    """Reject links present at inspection; concurrent path swaps remain unsafe."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if is_link_or_reparse(info):
        raise ValueError(f"unsafe symlink or reparse point: {path}")
    if directory and not stat.S_ISDIR(info.st_mode):
        raise ValueError(f"not a directory: {path}")
    if not directory and (not stat.S_ISREG(info.st_mode) or info.st_nlink > 1):
        raise ValueError(f"not a safe regular output file: {path}")


def check_seed_route_locations(examples: Path) -> None:
    """The seed reads one directory; never ignore an adjacent route declaration."""
    alternatives = [examples / "pipeline"]
    if examples.name.casefold() == "pipeline":
        alternatives.append(examples.parent)
    for alternate in alternatives:
        require_safe_path(alternate, directory=True)
    for directory in (examples, *alternatives):
        candidate = directory / "wall_surface.json"
        if entry_present(candidate):
            raise ValueError(f"{candidate} is a wall manifest; seed import does not copy or validate it")
    for name in ("walls.json", "assembly.json"):
        source = examples / name
        if entry_present(source):
            require_safe_path(source, directory=False)
        for alternate in alternatives:
            candidate = alternate / name
            if entry_present(candidate):
                raise ValueError(f"ambiguous seed route: {candidate} is outside the selected seed directory")


def check_destination(plan: Plan, workdir: Path, *, legacy_seed: bool) -> None:
    """Preflight every project-owned path and route before creating any directory."""
    for directory in (workdir.absolute(), *workdir.absolute().parents):
        require_safe_path(directory, directory=True)
    for directory in plan.directories:
        require_safe_path(directory, directory=True)
    for path, _, _ in plan.files:
        require_safe_path(path, directory=False)
    for name in ("walls.json", "assembly.json"):
        parent_route = plan.root / "specs" / name
        if entry_present(parent_route):
            raise ValueError(f"ambiguous destination route: {parent_route} would coexist with pipeline specs")
    for directory in (plan.root / "specs", plan.root / "specs" / "pipeline"):
        manifest = directory / "wall_surface.json"
        if entry_present(manifest):
            raise ValueError(f"{manifest} already exists; scaffolding would leave an unvalidated wall manifest")
    destination_walls = plan.root / "specs" / "pipeline" / "walls.json"
    if legacy_seed and entry_present(destination_walls):
        raise ValueError(f"{destination_walls} already exists; a legacy seed would leave a conflicting wall route")
    # --force is not permission to erase an invalid/ambiguous route selector.
    # Inspect existing declarations too, before writing any planned file.
    route_docs: dict[str, dict[str, Any]] = {}
    for name in ("walls.json", "assembly.json"):
        path = plan.root / "specs" / "pipeline" / name
        if entry_present(path):
            document = parse_seed_json(path.read_text(encoding="utf-8"))
            if not isinstance(document, dict):
                raise ValueError(f"existing {path} is not a JSON object")
            route_docs[name] = document
    if route_docs:
        validate_seed_route(route_docs.get("walls.json"), route_docs.get("assembly.json"))

    # A scaffold is not a migration tool. Outputs can exist outside the pipeline
    # directory, so even an apparently artifact-free route switch is refused.
    planned_docs = {
        path.name: parse_seed_json(content)
        for path, _, content in plan.files
        if path.parent == plan.root / "specs" / "pipeline"
        and path.name in ("walls.json", "assembly.json")
    }
    if route_docs:
        old_route = (route_docs["walls.json"]["wall_technique"] if "walls.json" in route_docs
                     else LEGACY_WALL_TECHNIQUE)
        new_route = (planned_docs["walls.json"]["wall_technique"] if "walls.json" in planned_docs
                     else LEGACY_WALL_TECHNIQUE)
        if old_route != new_route:
            raise ValueError(
                f"refusing wall route switch {old_route} -> {new_route}; "
                "existing scripts or manifests could become stale; preserve them and migrate separately"
            )
    # Even on the same route, rewriting specs alongside an existing output can
    # leave it stale. An orphan output is not evidence of its owning route.
    for directory in (plan.root, plan.root / "specs", plan.root / "specs" / "pipeline"):
        for name in ("assembly.ms", "wall_surface.ms", "wall_surface.json"):
            artifact = directory / name
            if entry_present(artifact):
                raise ValueError(
                    f"refusing to rewrite route specs beside existing output {artifact}; "
                    "preserve and review it separately"
                )


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #


def output_file_state(path: Path) -> Optional[tuple[int, ...]]:
    """Inspect without opening/following the output leaf; not a filesystem lock.

    Parent checks are repeated near commit, but a later hostile directory swap
    remains outside this single-owner command's guarantee.
    """
    for parent in path.absolute().parents:
        require_safe_path(parent, directory=True)
    require_safe_path(path, directory=False)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    return file_state(info)


def file_state(info: Any) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
            info.st_ctime_ns, info.st_mode, info.st_nlink)


def write_staged_file(path: Path, content: str, expected: Optional[tuple[int, ...]]) -> None:
    """Commit one complete file without opening the destination for truncation.

    mkstemp exclusively creates a regular sibling; all writes use its existing
    descriptor, not a second path open. A failed write/flush/fsync/replace leaves
    the old destination intact. No multi-file rollback or crash durability is
    promised. State checks detect observed changes, not hostile concurrent races.
    """
    if output_file_state(path) != expected:
        raise OSError(errno.EBUSY, "output changed since scaffold preflight", str(path))
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        try:
            stream = os.fdopen(descriptor, "w", encoding="utf-8", newline="\n")
        except BaseException:
            os.close(descriptor)
            raise
        with stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            staged_state = file_state(os.fstat(stream.fileno()))
        if output_file_state(path) != expected:
            raise OSError(errno.EBUSY, "output changed while staging scaffold", str(path))
        closed_state = output_file_state(temporary)
        # Windows can update timestamps only when the writer closes. Compare
        # identity/size/type/link-count here; destination changes use full state.
        if closed_state is None or any(closed_state[i] != staged_state[i] for i in (0, 1, 2, 5, 6)):
            raise OSError(errno.EBUSY, "staged scaffold file changed before replacement", str(temporary))
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError as exc:
            print(f"warning: could not remove owned staging file {temporary}: {exc}; preserve and inspect it",
                  file=sys.stderr)


def render_written_table(rows: Sequence[tuple[str, str]]) -> str:
    headers = ("STATUS", "PATH", "KIND")
    body = [row for row in rows]
    widths = [
        max(len(headers[i]), max((len(row[i]) for row in body), default=0))
        for i in range(len(headers))
    ]
    lines = [
        "  ".join(headers[i].ljust(widths[i]) for i in range(len(headers))).rstrip(),
        "  ".join("-" * widths[i] for i in range(len(headers))),
    ]
    for row in body:
        lines.append("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))).rstrip())
    return "\n".join(lines)


def existing_creations(root: Path) -> set[str]:
    """Files a previous run of this generator created, per project.json."""
    manifest = root / "project.json"
    if not manifest.is_file():
        return set()
    try:
        payload = parse_seed_json(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError):
        return set()
    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, list):
        return set()
    return {str(item) for item in files}


def require_unmodified_wall_scaffold(plan: Plan) -> None:
    """Allow --force on walls only for an intact, recorded fresh draft stub.

    Manifests from older versions or seeded projects do not provide this
    evidence. This content check is not an atomic lock against path changes.
    """
    path = plan.root / "specs" / "pipeline" / "walls.json"
    if not any(target == path for target, _, _ in plan.files) or not entry_present(path):
        return
    manifest = plan.root / "project.json"
    try:
        payload = parse_seed_json(manifest.read_text(encoding="utf-8"))
        content = path.read_bytes()
        current = parse_seed_json(content.decode("utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise ValueError(f"cannot verify existing wall scaffold: {exc}") from exc
    relative = path.relative_to(plan.root).as_posix()
    hashes = payload.get("unmodified_wall_scaffold_sha256") if isinstance(payload, dict) else None
    expected_hash = hashes.get(relative) if isinstance(hashes, dict) else None
    template = scaffold_walls(plan.project, {"tolerances": TOLERANCES}, wall_route=plan.wall_route)
    if isinstance(current, dict) and isinstance(current.get("source"), dict):
        template["source"]["recorded_at"] = current["source"].get("recorded_at")
    if (not isinstance(expected_hash, str) or
            hashlib.sha256(content).hexdigest() != expected_hash or current != template):
        raise ValueError(
            f"refusing to overwrite {path}: it is not an unchanged recorded fresh draft wall scaffold; "
            "preserve authored, locked, seeded, edited, or unverifiable walls"
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scaffold a project workdir for the 3ds Max architectural/NURBS pipeline "
            "(references/07-spec-grammar.md section 4 inventory)."
        ),
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project id; must match ^[a-z0-9][a-z0-9._-]*$ and becomes the 'project' "
        "envelope key in every spec file (07 section 3.1).",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="Workdir that will contain the project directory (default: CWD).",
    )
    parser.add_argument(
        "--from",
        dest="from_examples",
        type=Path,
        default=None,
        help="Seed specs/pipeline from an examples directory instead of scaffolding. "
        "With walls.json, source projects must agree and all seed provenance is preserved; "
        "historical no-wall example seeds retain their original re-stamping behavior. "
        "Every used seed must be strict JSON without duplicate keys or lossy numbers.",
    )
    parser.add_argument(
        "--wall-route",
        "--route",
        dest="wall_route",
        choices=WALL_TECHNIQUES,
        default=None,
        help=f"Wall modeling technique/route to scaffold (choices: {', '.join(WALL_TECHNIQUES)}; "
        f"default for fresh projects: {CLOSED_CONTOUR_SHELL_V2_TECHNIQUE}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite previously recorded paths subject to safety checks. An existing "
        "walls.json must be an unchanged, hash-recorded fresh draft scaffold; route "
        "switches and concurrent modification are not supported.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print the plan and write nothing.",
    )
    args = parser.parse_args(argv)

    # ---- validate user input before touching the filesystem ----
    if not re.match(r"^[a-z0-9][a-z0-9._-]*$", args.project):
        print(
            f"error: project id {args.project!r} must match ^[a-z0-9][a-z0-9._-]*$ "
            "(07 section 3.1: it is also the output name)",
            file=sys.stderr,
        )
        return 2

    workdir = args.dir
    if workdir.exists() and not workdir.is_dir():
        print(f"error: --dir {workdir} exists and is not a directory", file=sys.stderr)
        return 2

    root = workdir / args.project
    if root.exists() and not root.is_dir():
        print(f"error: {root} exists and is not a directory", file=sys.stderr)
        return 2

    examples: Optional[Path] = None
    if args.from_examples is not None:
        examples = resolve_examples(args.from_examples, workdir)
        if examples is None:
            print(
                f"error: --from {args.from_examples} is not a directory (looked in CWD, "
                "--dir and the skill root)",
                file=sys.stderr,
            )
            return 2
        for filename in SEEDED_FROM_EXAMPLES:
            if not (examples / filename).is_file():
                print(
                    f"error: {examples} does not contain {filename}; --from needs the "
                    "worked example directory",
                    file=sys.stderr,
                )
                return 2

    if args.wall_route is not None and args.wall_route not in WALL_TECHNIQUES:
        print(
            f"error: invalid --wall-route {args.wall_route!r}; choices are: {', '.join(WALL_TECHNIQUES)}",
            file=sys.stderr,
        )
        return 2

    if examples is not None:
        source_walls = examples / "walls.json"
        source_has_walls = entry_present(source_walls)
        seed_route = LEGACY_WALL_TECHNIQUE
        if source_has_walls:
            try:
                seed_doc = parse_seed_json(source_walls.read_text(encoding="utf-8"))
                seed_route = seed_doc.get("wall_technique")
            except Exception as exc:
                print(f"error: cannot read seed walls.json: {exc}", file=sys.stderr)
                return 2
        if args.wall_route is not None and args.wall_route != seed_route:
            print(
                f"error: explicit --wall-route {args.wall_route!r} conflicts with seed route {seed_route!r}; "
                "no silent fallback or route conversion on seeded projects",
                file=sys.stderr,
            )
            return 2
        wall_route = seed_route
    else:
        wall_route = args.wall_route if args.wall_route is not None else CLOSED_CONTOUR_SHELL_V2_TECHNIQUE

    try:
        if examples is not None:
            check_seed_route_locations(examples)
        plan = build_plan(args.project, root, examples, wall_route=wall_route)
        source_walls = examples / "walls.json" if examples is not None else None
        source_has_walls = source_walls is not None and entry_present(source_walls)
        check_destination(plan, workdir, legacy_seed=examples is not None and not source_has_walls)
        if args.force:
            require_unmodified_wall_scaffold(plan)
        output_states = {path: output_file_state(path) for path, _, _ in plan.files}
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(f"error: cannot prepare scaffold: {exc}", file=sys.stderr)
        return 2

    # ---- refuse to clobber ----
    created_before = existing_creations(root) if root.is_dir() else set()
    blocked: list[Path] = []
    for path, _, _ in plan.files:
        if not path.exists():
            continue
        relative = path.relative_to(root).as_posix()
        if not args.force:
            blocked.append(path)
        elif relative not in created_before:
            blocked.append(path)
    if blocked:
        print(
            "error: refusing to overwrite the following file(s). --force is limited to "
            "previously recorded paths and is subject to additional wall and route checks:",
            file=sys.stderr,
        )
        for path in blocked:
            print(f"  {path}", file=sys.stderr)
        return 2

    rows: list[tuple[str, str]] = []

    if args.dry_run:
        for directory in plan.directories:
            rows.append(("dir", plan.rel(directory), "would create" if not directory.is_dir() else "exists"))
        for path, kind, _ in plan.files:
            status = "exists" if path.exists() else "write"
            rows.append((status, plan.rel(path), kind))
        print(f"init_project  --  dry run, nothing written")
        print(f"project       {args.project}")
        print(f"root          {root}")
        if examples is not None:
            print(f"seeded from   {examples}")
        print()
        print(render_written_table(rows))
        print()
        print(f"{len(plan.files)} file(s), {len(plan.directories)} directory(ies) planned")
        return 0

    # ---- write ----
    try:
        for directory in plan.directories:
            directory.mkdir(parents=True, exist_ok=True)
        for path, kind, content in plan.files:
            write_staged_file(path, content, output_states[path])
            rows.append(("write", plan.rel(path), kind))
    except (OSError, ValueError) as exc:
        failed_path = getattr(exc, "filename", None)
        reason = getattr(exc, "strerror", None) or str(exc)
        print(
            f"error: writing failed at {failed_path or root}: {reason}. "
            "This file was not committed; prior completed replacements are left in place. "
            "The project is not a whole-project transaction; "
            "preserve and inspect them before deciding how to recover. "
            "A --force retry may be refused, especially if project.json was not written.",
            file=sys.stderr,
        )
        if rows:
            print("Completed file writes:", file=sys.stderr)
            for _, name, _ in rows:
                print(f"  {name}", file=sys.stderr)
        return 2

    print(f"init_project  --  {GENERATOR} {GENERATOR_VERSION}")
    print(f"project       {args.project}")
    print(f"root          {root}")
    if examples is not None:
        print(f"seeded from   {examples}")
    print()
    print(render_written_table(rows))
    print()
    print(f"{len(plan.files)} file(s) written")
    if examples is None:
        if wall_route == CLOSED_CONTOUR_SHELL_V2_TECHNIQUE:
            print(
                "next          author dimensions.json and walls.json (closed_inner_contour_shell_v2); "
                "the v2 wall builder emits wall_surface.ms and wall_surface.json"
            )
        elif wall_route == POLY_WALL_TECHNIQUE:
            print(
                "next          author dimensions.json and walls.json; the poly wall build and "
                "runtime QA are not implemented"
            )
        else:
            print(
                "next          edit specs/pipeline/dimensions.json and walls.json, then run "
                "legacy pipeline stages"
            )
    elif source_has_walls:
        print(
            "next          validate the seeded wall route; the poly wall build and "
            "runtime QA are not implemented"
        )
    else:
        print(
            "next          edit specs/pipeline/dimensions.json, then set status to 'locked' "
            "and run scripts/validate_specs.py --build"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
