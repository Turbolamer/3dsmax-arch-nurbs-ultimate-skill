#!/usr/bin/env python3
"""Scaffold a project workdir for the 3ds Max architectural/NURBS pipeline.

Creates ``<dir>/<project>/`` holding ``specs/pipeline/*.json`` for every file in
the 07 section 4 inventory, plus ``specs/recipes/``, ``specs/export/``,
``snippets/`` and a ``project.json`` manifest. Standard library only, no network.

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
Every emitted spec file is valid, envelope-complete JSON with the six envelope
keys in order and every key from 07 section 4 present, so a fresh project passes
``scripts/validate_specs.py``:

* ``dimensions.json`` is a small **internally consistent** single-storey bay, not
  a set of blanks. The footprint, grid, core, levels, roof and facades reconcile,
  so G-16..G-30 and G-32 all evaluate and pass. Its ``status`` is ``draft`` --
  that is the honest state of a project with no brief behind it -- so G-4 reports
  a WARN in lint mode and a FAIL under ``--build``. That is the only non-PASS row
  a clean scaffold produces.
* ``massing.json`` (P3), ``facade_grids.json`` and ``components_registry.json`` (P5)
  and ``assembly.json`` (P6) are **computed, not authored**, so what this script
  writes for them is an empty placeholder with no provenance and a
  ``source.reference`` that says so. Their status is ``draft``, which is why their
  stage invariants (G-34..G-40, G-57..G-70, G-71..G-83) report SKIP with a reason
  instead of failing an empty tree.
* ``nurbs.json`` (P4) is the exception: it is **hand-authored**. ``build_nurbs.py``
  reads it and emits the normalised spec plus the MAXScript; it refuses when the
  file is absent. The stub is still empty and ``draft``, and its ``source.reference``
  says so -- the distinction matters because there is no generator to go and run.
* reserved files (P6..P9) carry the envelope plus the key list 07 section 4
  promises for them and are otherwise empty. Per 07 S-4 no builder reads them,
  so their body is reported SKIP rather than validated.
* ``assumptions.json`` carries the seven entries a scaffold genuinely needs: the
  documented 07 section 5 defaults that a human is most likely to forget are
  recorded as ``assumed`` so they become an ``A-nnn`` audit trail rather than a
  silent value.

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
import json
import re
import sys
from datetime import datetime, timezone
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

#: The 07 section 4 inventory, in declared order. Everything is scaffolded so a
#: later stage never has to invent a file shape; ``owner`` is recorded in the
#: source reference of a reserved file so the reader knows who completes it.
INVENTORY: tuple[tuple[str, str, str], ...] = (
    ("dimensions.json", "P2a", "defined"),
    ("conflicts_resolved.json", "P2a", "defined"),
    ("assumptions.json", "P2a", "defined"),
    ("massing.json", "P3", "defined"),
    ("nurbs.json", "P4", "defined"),
    ("facade_grids.json", "P5", "defined"),
    ("components_registry.json", "P5", "defined"),
    ("assembly.json", "P6", "defined"),
    ("materials.json", "P7", "reserved"),
    ("qa.json", "P8", "defined"),
    ("export.json", "P9", "reserved"),
)

#: Files ``--from examples`` copies. Every one of them is ``defined`` in 07 section 4, so a
#: project seeded from the worked example must carry them all -- a missing ``defined`` file is a
#: FAIL, not a SKIP (07 section 9.6). ``massing.json`` joined this list at P3, ``nurbs.json`` at
#: P4, and the P5 pair at P5. Their two CSVs are *not* spec files and are never seeded: they are
#: rebuilt from the two JSONs by ``scripts/facade_tables.py --stage tables``.
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
            "derives_from": ["building.gross_floor_area_m2", "core.footprint_area_m2"],
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


def scaffold_assembly(project: str) -> dict[str, Any]:
    """The P6 file. Structurally valid, deliberately empty.

    The same situation as ``massing.json`` two stages later: ``assembly.json`` is
    **computed, not authored** -- written by ``scripts/place_components.py --stage
    assembly`` from a locked ``components_registry.json``, ``world_table.csv``,
    ``massing.json`` and ``dimensions.json``. The stub exists so a fresh project lints
    clean and so the 07 section 8.5 key order is visible, and it says so in
    ``source.reference``.

    Empty arrays, not the reserved skeleton's promised keys: ``placements`` /
    ``opening_cuts`` / ``wall_cells`` / ``scatter`` are real tables and a skeleton of them
    would be a shape no invariant can vouch for. ``wall_cells`` is here because P6 moved
    opening cuts off the Boolean modifier -- it was measured unusable -- and onto tiling the
    wall with solid cells; a stub written before that move omits the key and FAILs G-1.
    ``layer_map`` is an **empty object** on purpose -- it is the only place a layer is ever
    declared (07 section 8.5, G-79), so a stub that printed layer names would be claiming a
    layer assignment the bridge cannot perform.

    Its ``status`` is ``draft``, which is what keeps G-71..G-78 honest: an empty array is
    still a leaf 07 section 5.2 asks for an ``origins`` entry for, so the stub cannot
    satisfy the origins coverage rule, and 07 section 9.9 says a draft file is not
    evaluated.
    """

    doc: dict[str, Any] = envelope(
        "assembly",
        project,
        "derived",
        "empty stub written by init_project.py. assembly.json is GENERATED by "
        "scripts/place_components.py --stage assembly from a locked components_registry.json, "
        "world_table.csv, massing.json and dimensions.json; do not hand-edit it. Key order "
        "per references/07-spec-grammar.md section 8.5. defaults.panel_joint_cm arrives with "
        "the builder from the registry's A-024 and defaults.instance_limit_guard is a refusal "
        "threshold, so a placeholder declares neither.",
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
    return doc


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
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- #
# Plan
# --------------------------------------------------------------------------- #


class Plan:
    """The complete set of directories and files a run intends to write."""

    def __init__(self, root: Path, project: str) -> None:
        self.root = root
        self.project = project
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


def build_plan(project: str, root: Path, examples: Optional[Path]) -> Plan:
    plan = Plan(root, project)
    pipeline = root / "specs" / "pipeline"

    if examples is not None:
        for filename, _, _ in INVENTORY:
            if filename in SEEDED_FROM_EXAMPLES:
                source = examples / filename
                document = rewrite_from_example(source.read_text(encoding="utf-8"), project)
                plan.add_file(pipeline / filename, "seeded from examples", render_json(document))
            elif filename == "qa.json":
                plan.add_file(
                    pipeline / filename,
                    "scaffold (draft QA plan)",
                    render_json(scaffold_qa(project)),
                )
    else:
        plan.add_file(
            pipeline / "dimensions.json",
            "scaffold",
            render_json(scaffold_dimensions(project)),
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
            pipeline / "assembly.json",
            "stub (generated at build time by place_components.py)",
            render_json(scaffold_assembly(project)),
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

    plan.add_file(
        root / "project.json",
        "manifest",
        render_json(build_manifest(project, root, [p for p, _, _ in plan.files])),
    )
    return plan


def build_manifest(project: str, root: Path, files: Sequence[Path]) -> dict[str, Any]:
    """The project manifest.

    Deliberately records only facts this script can justify: the project id, the
    schema revision, the generator, and the 3ds Max **target** version from 07
    section 11. It records no renderer, no plugin and no scene fact -- the renderer
    is detected at build time and stored in ``materials.json``.
    """
    return {
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
        # Every file this generator created, project.json included. It is the
        # ownership record: --force overwrites exactly these paths and nothing
        # else, so a hand-written file that happens to share a name is refused.
        "files": sorted(
            [path.relative_to(root).as_posix() for path in files] + ["project.json"]
        ),
    }


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


def rewrite_from_example(text: str, project: str) -> dict[str, Any]:
    """Re-stamp an example file onto a new project, preserving the audit trail.

    Rewritten: ``project``, ``source.reference`` and ``source.recorded_at``.
    Everything else is copied byte-for-byte in value terms -- in particular every
    ``A-nnn`` and ``C-nnn`` id and every ``origin_ref``, which *is* the audit
    trail. The caller asserts that after the rewrite.
    """
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("example spec is not a JSON object")
    before_ids, before_refs = collect_ids(document)
    document["project"] = project
    source = document.get("source")
    if isinstance(source, dict):
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


def resolve_examples(candidate: Path, workdir: Path) -> Optional[Path]:
    """Find the examples directory: as given, then from the repo root, then CWD."""
    repo_root = Path(__file__).resolve().parent.parent
    for base in (Path.cwd(), workdir, repo_root):
        candidate_path = (base / candidate).resolve() if not candidate.is_absolute() else candidate
        if candidate_path.is_dir():
            return candidate_path
    return None


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #


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
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, list):
        return set()
    return {str(item) for item in files}


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
        "Ledger ids and origin_refs are preserved; project/source are re-stamped.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files a previous run of this generator created. Files this "
        "generator did not create are never touched, even with --force.",
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
    if not workdir.exists():
        try:
            workdir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"error: cannot create --dir {workdir}: {exc.strerror or exc}", file=sys.stderr)
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

    plan = build_plan(args.project, root, examples)

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
            "error: refusing to overwrite the following file(s). Re-run with --force only "
            "if this generator created them (it will not touch a file it did not create, "
            "and will not overwrite anything at all without --force):",
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
            path.write_text(content, encoding="utf-8", newline="\n")
            rows.append(("write", plan.rel(path), kind))
    except OSError as exc:
        print(
            f"error: writing failed at {exc.filename}: {exc.strerror or exc}. "
            "Files already written are left in place; re-run with --force to continue.",
            file=sys.stderr,
        )
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
    print(
        "next          edit specs/pipeline/dimensions.json, then set status to 'locked' "
        "and run scripts/validate_specs.py --build"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())