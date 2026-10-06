# 07 — Spec Grammar: the JSON contract for the whole pipeline

> **Purpose:** the single authoritative definition of every file in `specs/pipeline/*.json` — the
> envelope, the units, the key-by-key schema, the traceability rule, and the mechanically checkable
> invariants that `scripts/validate_specs.py` (P2c) must implement. Every later stage reads this file
> and writes against it; nobody invents a schema from scratch.
>
> **Defined at P2a:** `dimensions.json`, `conflicts_resolved.json`, `assumptions.json`.
> **Defined at P3:** `massing.json` (§8.1, with invariants `G-34`…`G-40` in §9.6).
> **Defined at P4, extended at P4b:** `nurbs.json` (§8.2, with invariants `G-41`…`G-56` in §9.7 —
> `G-50`…`G-54` are the dependent-surface block that arrived with the rail-sweep / blend / trim kinds;
> `G-55` / `G-56` were added when the blend tension and the relation parent slots were measured).
> **Defined at P5:** `facade_grids.json` (§8.3) and `components_registry.json` (§8.4, with
> invariants `G-57`…`G-70` in §9.8).
> **Reserved here, defined by their own stage:** `assembly.json`, `materials.json`, `qa.json`,
> `export.json`.
>
> **This document needs no 3ds Max.** Everything here is a data contract. It makes claims about
> 3ds Max in exactly one place — §11 — and everything in that section is taken from
> `CHECKPOINT.md` §"Verified facts" and is labelled with how it was established. No range, default or
> dimension in §2–§10 was read off a 3ds Max probe.

---

## 1. Standing rules

| # | Rule |
|---|---|
| S-1 | **A spec file is data, never prose.** No comments, no trailing commas, no `//`. If something cannot be expressed as a value, it does not belong in the schema. |
| S-2 | **Traceability, not narrative.** Every value that was invented or overridden carries an id (`A-nnn` / `C-nnn`) that the file which consumes it references. A value may not exist without knowing where it came from. |
| S-3 | **A stage may not reinterpret an existing key.** A key means what §5–§8 say it means. If a later stage needs different meaning, that is a breaking change: bump `schema_version` major and rewrite the key. |
| S-4 | **Reserved means reserved.** A reserved file has a key list here so downstream stages can plan, but until its owner stage writes it and marks it `defined`, no builder reads it and no example file exists for it. |
| S-5 | **Determinism over convenience.** The same locked specs must produce byte-identical builder output. No timestamps, no random seeds and no iteration-order-dependent values inside a spec file. |

---

## 2. Units — the authoritative statement

**All lengths are centimetres, all angles are degrees, all areas are square metres.**

3ds Max scene units are centimetres in this pipeline, so centimetres is the spec unit; nothing is
converted on the way in or out.

| Quantity | Unit | Suffix | Notes |
|---|---|---|---|
| Length | cm | `_cm` | **Mandatory suffix. There are no bare length keys.** |
| Angle | deg | `_deg` | Only for rotations and slopes. |
| Area | m² | `_m2` | Used for room/floor/plot areas only, never for a surface dimension. |
| Count | integer | `_count`, or bare plural noun | `bay_count`, `interior_column_count`. |
| Coordinate pair | cm | `_cm`, value is `[x, y]` or `[x, y, z]` | `start_corner_cm`, `footprint_cm`, `column_x_cm`. |
| Ratio / flag | — | none, or `_ratio` / `_ccw` | `plot_rotation_deg` is an angle and takes `_deg`. |

Enforced by invariant **G-8**. The suffix is a lint, not a comment: a key named `height`, `width`,
`depth`, `thickness`, `radius`, `offset`, `spacing`, `sill` or `head` without a unit suffix is a
validation error, not a style preference. A key that needs a unit but has no suffix gets one.

Angles are always degrees, never radians. `plot_rotation_deg: 0.0` means the building's local X axis
lies on world X. `direction_deg` is a compass bearing: `0` = faces north (+Y), `90` = east (+X),
`180` = south (−Y), `270` = west (−X).

**A direction is not a length.** `nurbs.json`'s `p_vec` carries no unit suffix because its magnitude
carries no meaning: its three components are centimetres in world space, but only the *direction*
is a value, so G-53 asks for a non-zero magnitude rather than a length range (§8.2.7). `seed` is
dimensionless for the same reason — it is a position in a surface's parameter domain, not a distance.

---

## 3. Common envelope and file hygiene

### 3.1 The six envelope keys — first, in this order

Every file in `specs/pipeline/` opens with exactly these keys, in this order, before anything else:

```json
{
  "schema_version": "1.0",
  "spec": "<file base name>",
  "project": "<project id>",
  "units": { "length": "cm", "angle": "deg" },
  "source": { "kind": "user_brief", "reference": "user conversation", "recorded_at": "ISO-8601" },
  "status": "locked"
}
```

| Key | Type | Req | Constraint | Meaning | Default |
|---|---|---|---|---|---|
| `schema_version` | string | yes | semver; the envelope uses `MAJOR.MINOR`, patch optional. The validator's supported major must equal the file's major | Schema revision this file was written against | — |
| `spec` | string | yes | must equal the file base name (`dimensions.json` → `"dimensions"`) | which schema this file follows | — |
| `project` | string | yes | `^[a-z0-9][a-z0-9._-]*$`, identical across all files in one project | project id, used as the output name | — |
| `units.length` | string | yes | must be `"cm"` | length unit | — |
| `units.angle` | string | yes | must be `"deg"` | angle unit | — |
| `source.kind` | string | yes | `user_brief` \| `drawing` \| `image` \| `imported` \| `assumed` \| `derived` | where the input came from. **`derived` (added at P3)** means the file was computed from another spec in the same project, and `source.reference` must then name that file | — |
| `source.reference` | string | yes | free text; cite the file/paragraph/message | what specifically was read | — |
| `source.recorded_at` | string | yes | ISO-8601 date-time | when the input was captured | — |
| `status` | string | yes | `draft` \| `locked` \| `superseded` | lifecycle state | `draft` |

**`schema_version` is semver and a validator rejects a major mismatch.** Minor and patch drift is
tolerated and reported as a warning; a major difference is an error. A builder that meets a major it
does not implement must stop rather than guess.

**`status` and the build gate.** `draft` means a file is still being written. `locked` means the
values are agreed and downstream stages may consume them. `superseded` means a newer revision
exists. **A builder must refuse to consume any file whose `status` is not `locked`** — it must say
which file and which status it found, not silently use a draft. This is the single gate that stops a
half-read brief from becoming geometry.

`status` transitions: `draft` → `locked` is one-way within a project. `locked` → `superseded`
requires the replacement file to exist and to declare `"supersedes": "<old spec name>@<version>"` in
its `source` block. Nothing in this grammar requires a builder to *write* `superseded`; only the input
stage does.

### 3.2 File hygiene

| Property | Rule | Invariant |
|---|---|---|
| Encoding | UTF-8, no BOM | G-7 |
| Line ending | LF (`\n`). No CRLF. | G-7 |
| Parsing | Strict JSON. No comments, no trailing commas, no single quotes, no NaN/Infinity. | G-7 |
| Trailing newline | Exactly one LF at end of file | G-7 |
| Trailing newline | Yes, exactly one | — |
| Key order | The six envelope keys first, in order. Within an object, order is not semantic **except** in `dimensions.json` where `origins` must precede the value tree it annotates. | G-1 |
| `recorded_at` | ISO-8601. The only clock value allowed anywhere in a spec. | G-6 |

### 3.3 Tolerance block

`dimensions.json` carries a seventh top-level key immediately after `status`:

```json
"tolerances": { "linear_cm": 0.5, "area_m2": 0.05, "angle_deg": 0.01 }
```

These are the **arithmetic tolerances** used by every equality check in §9 unless a rule names its
own. They exist because specs are hand-edited; they are not design tolerances. `linear_cm: 0.5` is
half a millimetre — small enough that a real inconsistency is caught, large enough that
`0.1 + 0.2 + 0.3` style float noise does not fail the build. A hand-edited spec that is off by more
than 0.5 cm is a bug, and the validator is right to reject it. Enforced by **G-33**.

---

## 4. The full pipeline inventory

Specs live in `specs/pipeline/`. `examples/` holds the worked example. Twelve files, seven of them
defined now.

| File | Owner | Purpose | Status | Top-level keys |
|---|---|---|---|---|
| `dimensions.json` | **P2a** | The locked dimensional contract: site, envelope, structure, core, plates, roof, facade grid, openings. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origins` `building` `site` `structure` `levels` `core` `floor_plates` `roof` `facades` `openings` |
| `conflicts_resolved.json` | **P2a** | Every contradiction found in the input, with the chosen resolution, the loser, the precedence rule invoked and the affected stages. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `precedence_rules` `conflicts` |
| `assumptions.json` | **P2a** | Every value the pipeline had to invent because the input was silent. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `assumptions` `cross_references` |
| `massing.json` | P3, extended **P6** | Slabs, columns, core walls, facade wall bands, roof deck, parapet and plinth as placeable Z-prisms, in world coordinates. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `origins` `defaults` `storeys` `elements` `site_pad` `grouping` |
| `nurbs.json` | **P4**, extended **P4b** | NURBS shells and their lattices: U-lofts, UV-loft networks, interpolating point grids, CV-cage grids, one- and two-rail sweeps, blends between surface edges and profiles projected onto a surface, plus the quad-panel and space-frame derivatives read off them. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `origins` `sections` `surfaces` `derivatives` |
| `facade_grids.json` | **P5** | Per-facade bay and opening axes, and the panelised partition those axes generate: one rectangle per grid cell, kinded, each naming the opening it realises and carrying the world centre P6 places it at. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `origins` `facades` `axes` `panels` `panel_types` |
| `components_registry.json` | **P5** | The parametric blocks that grid needs: one entry per distinct `(kind, width, height)` class of panel with an ordered parameter list, plus the family index P6 resolves a panel against. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `origins` `defaults` `component_types` `components` `families` |
| `assembly.json` | **P6** | The last derived file in the chain: where each component instance goes, which `facade_wall` each opening belongs to, the solid cells each of those walls is built from, and the Chaos Scatter setup — plus `layer_map`, which is **data only** and is never applied by a builder. | **defined** | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `origins` `defaults` `layer_map` `placements` `opening_cuts` `wall_cells` `scatter` |
| `materials.json` | P7 — **CANCELLED 2026-10-05** | Renderer selection and Corona PBR materials with slot maps and UV rules. **Not planned work** — materials are assigned by hand. | reserved | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `renderer` `materials` `uv_rules` |
| `qa.json` | P8 — **CANCELLED 2026-10-05** | Deterministic QA results, viewport captures, and the pass/fail verdict. **Not planned work** — no QA loop exists. | reserved | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `checks` `determinism` `captures` `verdict` |
| `export.json` | P9 — **CANCELLED 2026-10-05** | FBX / OBJ / USD export settings, tessellation, and instance preservation. **Not planned work** — no exporter exists. | reserved | `schema_version` `spec` `project` `units` `source` `status` `tolerances` `origin_inputs` `exports` `tessellation` `delivery` |
| `recipes/*.json` | P4 | Individual NURBS recipe bodies emitted as MAXScript. Not part of the pipeline chain. | reserved | `schema_version` `recipe` `source` `params` `script` |

> **CORRECTED (verified 2026-10-06):** the three rows above previously read just `P7`, `P8`, `P9` in the
> stage column. **All three stages were cancelled by user decision on 2026-10-05.** Their rows are
> retained — the `reserved` stubs are real files and G-31 still resolves their `origin_inputs` — but
> **they are not planned work and no builder emits them.** There is no `qa_check.py`,
> `capture_views.py` or `export_max.py` in `scripts/`, and this pack does not script material
> assignment at all. §8.6–§8.8 below document the reserved key sets only.

Every reserved file carries `origin_inputs` — the list of dotted paths in **defined** files it read.
That is what makes the chain auditable in the forward direction: given any later file you can see
exactly which locked values produced it. G-31 checks the references resolve.

---

## 5. `dimensions.json` — the dimensional contract

### 5.1 Top level

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `schema_version` | string | yes | — | see §3.1 | — | — |
| `spec` | string | yes | — | `== "dimensions"` | — | — |
| `project` | string | yes | — | — | — | — |
| `units` | object | yes | — | see §3.1 | — | — |
| `source` | object | yes | — | see §3.1 | — | — |
| `status` | string | yes | — | must be `locked` to build | — | — |
| `tolerances` | object | yes | — | §3.3 | arithmetic tolerances | — |
| `origins` | object | yes | — | §5.2 | traceability map | — |
| `building` | object | yes | — | §5.3 | building-level totals | — |
| `site` | object | yes | — | §5.4 | plot and footprint | — |
| `structure` | object | yes | — | §5.5 | structural grid | — |
| `levels` | array | yes | — | ≥ 1, §5.6 | storeys, bottom to top | — |
| `core` | object | yes | — | §5.7 | vertical service core | — |
| `floor_plates` | array | yes | — | §5.8 | one entry per level | — |
| `roof` | object | yes | — | §5.9 | roof build-up and parapet | — |
| `facades` | array | yes | — | ≥ 1, §5.10 | the four elevations | — |
| `openings` | array | yes | — | may be empty, §5.11 | doors, windows, glazed bays | — |

### 5.2 `origins` — the traceability map

`origins` is a **flat map from dotted path to provenance record**. It is deliberately not inline:
a builder reading `site.footprint_cm` gets a list of numbers, never a wrapper object, and the audit
question ("what did we make up?") is one `grep` over the map instead of a tree walk.

```json
"site.plot_rotation_deg":        { "origin": "assumed", "origin_ref": "A-001" },
"building.total_height_cm":      { "origin": "derived", "derives_from": ["levels[0].height_cm", "levels[1].height_cm"], "conflict_ref": "C-001" },
"facades[0]":                    { "origin": "derived", "derives_from": ["site.footprint_cm", "structure.x_bay_cm"] }
```

| Field | Type | Req | Constraint | Meaning | Default |
|---|---|---|---|---|---|
| `origin` | string | yes | `given` \| `assumed` \| `conflict` \| `derived` | provenance of the value | — |
| `origin_ref` | string | cond. | **required iff** `origin` ∈ {`assumed`,`conflict`}; **forbidden otherwise**. Must resolve in the ledger named by `origin` | `A-nnn` in `assumptions.json`, `C-nnn` in `conflicts_resolved.json` | — |
| `derives_from` | array of paths | cond. | required iff `origin == "derived"`; each path must resolve | inputs the value is computed from | — |
| `conflict_ref` | string | opt. | `C-nnn`, must resolve | set when a derived value's **inputs** were conflict-resolved. Informational; G-10 does not require it | — |

**Granularity.** An entry is required for every leaf in the value tree, **except** the six
envelope keys, everything under `tolerances`, and keys named `id`, `name`, `index` or ending in
`_index` / `_indices`. An **array is a leaf**: `site.footprint_cm` is one value with eight numbers in
it and takes one entry, not eight. An **array element may be collapsed to a single entry**
(e.g. `facades[0]`, `openings[4]`) **only when all of its leaves share one origin**. Where an element
mixes origins — `levels[]` mixes `given` / `conflict` / `assumed` — every leaf gets its own entry. No
leaf may be covered by more than one entry. That rule is checkable (G-9) and it means nothing in the
file escapes the audit.

`origin` semantics:

| `origin` | Meaning | Ledger |
|---|---|---|
| `given` | Stated in the input and accepted without alteration | none |
| `assumed` | The input was silent; the pipeline chose a value | `assumptions.json` |
| `conflict` | The input contradicted itself; a resolution was chosen | `conflicts_resolved.json` |
| `derived` | Computed from other values in this file | none — G-32 recomputes it |

**The hard invariant: a value may not be `assumed` or `conflict` without an `origin_ref`, and a
`derived` value may not be hand-edited.** This is the rule that makes the pipeline auditable: given
any number in any spec, there is exactly one place that says where it came from.

### 5.3 `building`

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | — | stable id | — |
| `name` | string | yes | — | — | display name | — |
| `typology` | string | yes | — | free text | building type | — |
| `total_height_cm` | number | yes | cm | > 250 | **derived** = `levels[-1].elevation_cm + levels[-1].height_cm` | — |
| `overall_height_cm` | number | yes | cm | > 250 | **derived** = `total_height_cm + roof.parapet_height_cm` | — |
| `gross_floor_area_m2` | number | yes | m² | > 0 | **derived** = Σ `floor_plates[].gross_area_m2` | — |
| `net_floor_area_m2` | number | yes | m² | > 0 | **derived** = `gross_floor_area_m2` − core area over `core.spans_level_indices` | — |

### 5.4 `site`

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | — | stable id | — |
| `footprint_kind` | string | yes | — | `polygon` \| `rectangle` | how to read `footprint_cm` | `polygon` |
| `footprint_cm` | array of `[x, y]` | yes | cm | ≥ 3 vertices, all distinct | building footprint, closed | — |
| `footprint_ccw` | bool | yes | — | — | declared winding; validator confirms it | — |
| `footprint_area_m2` | number | yes | m² | > 0 | **derived** from `footprint_cm` | — |
| `footprint_width_cm` | number | yes | cm | > 0 | **derived**, X extent | — |
| `footprint_depth_cm` | number | yes | cm | > 0 | **derived**, Y extent | — |
| `ground_level_cm` | number | yes | cm | any | finished site level, Z of the lowest floor | `0` |
| `plot_rotation_deg` | number | yes | deg | −180 … 180 | building rotation on the plot | `0` |
| `plot_rotation_ref_axis` | string | yes | — | `north` \| `true_north` \| `grid_north` | what `plot_rotation_deg` is measured from | `north` |
| `setback_cm` | number | opt | cm | 0 … 3000 | perimeter clearance to the plot edge | `300` |

`footprint_kind: "rectangle"` permits `footprint_cm` to be given as two corners instead of a closed
ring. Everything downstream — containment, area, facade closure — reads it as the same 4-vertex ring
counter-clockwise from the minimum corner. The example uses `polygon` explicitly; a rectangle is a
declaration, not a shortcut.

Plot rotation is a single number applied to the whole building, not per facade. If a brief describes
a non-orthogonal building, that belongs in `facade_grids.json`, and the building's own rotation is
still needed for the base transform.

### 5.5 `structure`

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | — | stable id | — |
| `system` | string | yes | — | free text | e.g. `steel_frame_with_rc_core` | — |
| `grid_kind` | string | yes | — | `bay_spacing` \| `explicit_lines` | whether `x_bay_cm` or explicit lines are authoritative | `bay_spacing` |
| `x_bay_cm` | array of number | yes | cm | each 300 … 1200 | structural bays along X; **Σ must equal `site.footprint_width_cm`** | — |
| `y_bay_cm` | array of number | yes | cm | each 300 … 1200 | structural bays along Y; **Σ must equal `site.footprint_depth_cm`** | — |
| `column_x_cm` | array of number | yes | cm | each > 0, inside the footprint | **derived** interior column lines | — |
| `column_y_cm` | array of number | yes | cm | each > 0, inside the footprint | **derived** interior column lines | — |
| `column_section_cm` | array `[sx, sy]` | opt | cm | each 20 … 80 | column plan size | `[40, 40]` |
| `interior_column_count` | integer | yes | — | ≥ 0 | **derived** = `len(column_x_cm) × len(column_y_cm)` | — |

With `grid_kind: "explicit_lines"` the two `column_*` arrays become **given** rather than derived and
carry every line including the perimeter ones; `x_bay_cm` / `y_bay_cm` then become derived as the
differences between consecutive lines. The two modes are mutually exclusive per axis and the
validator rejects a file that mixes them.

The sum-is-equal-to-the-footprint rule is what makes the grid a *structural* grid rather than a
suggestion: a column line may not fall outside the building and a bay may not overhang the plot.

### 5.6 `levels[]`

Ordered **bottom to top**. `index` is positional and must equal the array position.

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `index` | integer | yes | — | == array position | position | — |
| `id` | string | yes | — | — | stable id, `LVL-nn` | — |
| `use` | string | yes | — | free text | programme of this storey | — |
| `elevation_cm` | number | yes | cm | strictly increasing with `index` | finished floor level of this storey | — |
| `height_cm` | number | yes | cm | **250 … 600** | floor-to-floor of this storey | — |

The vertical model is a chain, and this is the single most important convention in the file:

```
levels[i].elevation_cm  =  levels[i-1].elevation_cm  +  levels[i-1].height_cm        (i ≥ 1)
levels[-1].elevation_cm + levels[-1].height_cm       =  roof deck level
```

`height_cm` is floor-to-floor, **not** clear height. Clear height is
`height_cm − floor_plates[i+1].thickness_cm` and is computed downstream, never entered by hand.

**Height ranges by use** — these are the defaults a human should sanity-check against, enforced as
soft bounds by `09-defaults.md` and hard bounds by G-16:

| Use | `height_cm` range | Basis |
|---|---|---|
| residential | 300 … 330 | floor-to-floor incl. structure |
| office | 360 … 400 | ditto |
| lobby / retail / double-height | 420 … 600 | ditto |
| the example (`small_office_pavilion`) | 250 … 600 | hard bound in G-16; the soft office band 360–400 is advisory and this project declares 420 / 400 |

The hard bound in G-16 is deliberately wider than any single use so that the validator does not
encode a building-type opinion. The per-use bands belong to `09-defaults.md`, which is a different
file with different authority.

### 5.7 `core`

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | — | stable id | — |
| `type` | string | yes | — | `lift_stair_wc` \| `stair_only` \| `lift_only` \| `riser_shaft` \| free text | what the core contains | — |
| `footprint_kind` | string | yes | — | `polygon` \| `rectangle` | as `site.footprint_kind` | `polygon` |
| `footprint_cm` | array of `[x, y]` | yes | cm | ≥ 3 vertices, simple ring | core outline in world coordinates | — |
| `footprint_area_m2` | number | yes | m² | > 0 | **derived** from `footprint_cm` | — |
| `spans_level_indices` | array of int | yes | — | must exist in `levels[]` | which storeys the core passes through | — |
| `wall_thickness_cm` | number | opt | cm | 15 … 40 | core wall thickness | `20` |

The core is expressed in **world coordinates**, not as an offset from a corner. That is deliberate: it
lets G-22 and G-23 test it against the footprint and the grid with plain arithmetic, and it means the
core is visible in the input stage rather than discovered during massing.

### 5.8 `floor_plates[]`

One entry per level, `level_index` in the same order as `levels[]`.

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `level_index` | integer | yes | — | exists in `levels[]` | which storey | — |
| `id` | string | yes | — | — | stable id, `FP-nn` | — |
| `thickness_cm` | number | yes | cm | 15 … 45 | structural plate thickness | — |
| `gross_area_m2` | number | yes | m² | > 0 | **derived** = `site.footprint_area_m2` (prismatic building) | — |
| `net_usable_area_m2` | number | opt | m² | 0 < x ≤ gross − core share | usable area after partitions | — |
| `usage` | string | opt | — | — | **omit when equal to the parent level's `use`** | parent's `use` |

`net_usable_area_m2` and gross-minus-core are two different numbers on purpose. Gross-minus-core
ignores internal partitions; usable area is what a client can actually put a desk in. When both are
present, G-28 requires `net_usable_area_m2 ≤ gross − core share`, never equality.

### 5.9 `roof`

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `type` | string | yes | — | `flat_parapet` \| `pitched_parapet` \| `pitched_eaves` \| `flat_balustrade` | roof form | — |
| `deck_level_cm` | number | yes | cm | > 0 | **derived** = `building.total_height_cm` | — |
| `deck_thickness_cm` | number | yes | cm | 15 … 45 | structural thickness **downward** from `deck_level_cm` | — |
| `slope_deg` | number | yes | deg | 0 … 15 | fall for drainage; sign is magnitude | `0` |
| `parapet_height_cm` | number | yes | cm | 60 … 150 | up from `deck_level_cm` | — |
| `parapet_thickness_cm` | number | yes | cm | 15 … 45 | parapet wall thickness | — |
| `coping_overhang_cm` | number | opt | cm | 0 … 10 | each side | `0` |
| `drainage` | string | opt | — | `internal_downpipe` \| `external_downpipe` \| `flat_roof_outlet` | — | `internal_downpipe` |

`deck_level_cm` is the **top** of the roof build-up. `deck_thickness_cm` hangs below it. Parapet
height rises above it. Those three together are the whole roof vertical model; there is no separate
"roof level" in `levels[]`, because the top storey's floor-to-floor already reaches the deck.

### 5.10 `facades[]`

One entry per elevation. `start_corner_cm` and `end_corner_cm` are **footprint vertices in world
coordinates**, and `position_cm` in an opening is measured along that direction from
`start_corner_cm`.

| Key | Type | Req | Units | Range | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | — | stable id, `F-[NSEW]` | — |
| `name` | string | yes | — | `north` \| `south` \| `east` \| `west` | which elevation | — |
| `direction_deg` | number | yes | deg | 0 … 360 | compass bearing the facade **faces** | — |
| `start_corner_cm` | `[x, y]` | yes | cm | must be a `site.footprint_cm` vertex | origin of the facade's 0 cm | — |
| `end_corner_cm` | `[x, y]` | yes | cm | must be a `site.footprint_cm` vertex | far end | — |
| `length_cm` | number | yes | cm | > 0 | **derived** = distance between the corners | — |
| `bay_count` | integer | yes | — | 1 … 60 | **derived** = `len(bay_width_cm)` | — |
| `bay_width_cm` | array of number | yes | cm | each 300 … 1200, **Σ == `length_cm`** | **derived** from the structural grid | — |

The order of `bay_width_cm` runs from `start_corner_cm` toward `end_corner_cm`. In the example the
east facade's `start_corner_cm` is `[1800, 0]` — its south corner — so bay 0 is the southern bay and
bay 1 the northern one. **Bay indices are positional and that position is meaningful**; a builder
must not sort or normalise them.

For a rectangular footprint, `bay_width_cm` is derived from `structure.x_bay_cm` on the north/south
elevations and `structure.y_bay_cm` on east/west. A non-orthogonal footprint means `bay_width_cm`
becomes `given` — which is exactly the case that would justify a conflict entry under
MODULE-ALIGNMENT.

### 5.11 `openings[]`

| Key | Type | Req | Units | Meaning | Default |
|---|---|---|---|---|---|
| `id` | string | yes | — | unique within the file, `OP-[G1n]` | — |
| `facade` | string | yes | — | must be a `facades[].id` | — |
| `level_index` | integer | yes | — | must exist in `levels[]` | — |
| `bay_index` | integer | yes | — | 0-based into that facade's `bay_width_cm` | — |
| `type` | string | yes | — | `window` \| `door` \| `entrance` \| `curtain_wall` | — |
| `position_cm` | number | yes | cm | centre of the opening along the facade, from `start_corner_cm` | — |
| `width_cm` | number | yes | cm | opening width | — |
| `sill_cm` | number | yes | cm | sill above **this level's** finished floor | — |
| `head_cm` | number | yes | cm | head above **this level's** finished floor | — |

Per-type ranges, all enforced by G-16:

| `type` | `width_cm` | `sill_cm` | `head_cm` | Extra |
|---|---|---|---|---|
| `window` | 60 … 420 | 0 … 150 | 150 … 350 | — |
| `door` | 80 … 150 | 0 | 180 … 260 | service, WC, plant |
| `entrance` | 120 … 300 | 0 | 200 … 320 | main entrance; one per building |
| `curtain_wall` | 100 … 600 | 0 … 30 | 250 … 450 | fills a structural bay; see below |

`sill_cm` and `head_cm` are **both measured from the same level's finished floor**, never from the
parapet and never from the slab. That is what makes G-26 (`head_cm ≤ levels[level].height_cm`) a
one-line check with no special cases.

A `curtain_wall` opening is the one case where the host is a whole bay: its `width_cm` is still
**strictly less** than the bay width (G-27), because the structural bay always keeps a pier or a
mullion at each edge. There is no zero-pier full-bay expression in this grammar. If a brief wants a
fully glazed bay, the correct answer is a `curtain_wall` at `bay_width − 2 × pier`, which is why
`420` in a `450` bay is the natural maximum.

An opening whose host wall is a core wall is a design error, not a schema error — the schema has no
way to know. The example avoids it by construction: the core sits in the south-east bay and that bay
carries a `curtain_wall` (a glazed stair frontage, deliberately) while the east elevation's bay 0 —
also core — carries no opening at all. This is recorded in `assumptions.json` A-016 so a later stage
does not "helpfully" add one.

---

## 6. `assumptions.json`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `schema_version` … `status` | — | yes | envelope, §3.1. `status` must be `locked` to build. |
| `assumptions` | array | yes | ≥ 1 entry, ordered by id |
| `cross_references` | object | yes | non-assumption provenance, for a reader who has only this file |

### 6.1 `assumptions[]`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `id` | string | yes | `A-001`, zero-padded, unique, ascending |
| `field_path` | string | yes | bare or **file-qualified** dotted path — §6.1.1; **unique within the file** |
| `value` | any | yes | the value assumed, **equal to what the spec holds** (G-12) |
| `reason` | string | yes | why this value, in terms of the silence it fills — not a restatement of the value |
| `confidence` | string | yes | `high` \| `medium` \| `low` |
| `invalidated_by` | string | yes | the specific fact that would make this wrong |
| `recheck_stage` | string | yes | the stage that must re-examine it: **`P3` … `P6`**. **NARROWED 2026-10-06 (P14): the range is now enforced, not merely advised.** `scripts/validate_specs.py` `RECHECK_STAGES` was `("P3"…"P9")` and is now `("P3","P4","P5","P6")`; a value naming `P7`/`P8`/`P9` **FAILs G-15**. Those three stages were cancelled by user decision on 2026-10-05, so naming one was vacuous — nothing re-checks at a stage that does not exist. P10…P13 are close-out and documentation passes, not re-examination points |
| `downstream_stages` | array | yes | stages whose output changes if it is wrong |
| `alternatives_considered` | array | opt | `[{ value, why_not }]` |

`confidence` is about **evidence, not importance**: `high` = a stated default or a direct consequence
of a given value; `medium` = a defensible convention with a real alternative; `low` = a guess that a
professional would immediately want to change. Every invented value in a first-pass project is
legitimately `low`, and a file full of `low` is not a defect — it is an accurate picture.

`reason` must name the **silence**, not the number. "The brief is silent on orientation" is a reason.
"A 3 m setback was chosen" is not; it repeats `value`.

#### 6.1.1 `field_path` has two accepted forms

| Form | Example | Resolves in |
|---|---|---|
| **bare** | `"facades[0].bay_width_cm"` | `dimensions.json` |
| **file-qualified** | `"components_registry.json:defaults.panel_thickness_cm"` | the named spec file |

A bare path is unchanged and is what all 22 existing `A-nnn` entries use. A file-qualified path is
`"<spec-name>:<dotted path>"`: the prefix before the first `:` must be a **known spec name** and
that file must be **present in the project**. An unknown name or an absent file is a FAIL that says
which of the two it was — `field_path names an unknown spec file` and `field_path names a spec file
that is not in this project` are different problems with different fixes, and collapsing them into
one message is how a typo becomes a mystery.

**Why the second form exists.** `dimensions.json` was the only file carrying `assumed` provenance
while P2 built the ledger, so the machinery resolved `field_path` there and was correct for the
time. **P5 is the first stage where a *derived* file legitimately holds an assumed value** — a
convention's declared default is not derivable by any formula, so the only honest options are to
record it as `assumed` or to invent a formula for it — and every stage after P5 will need this.

**Two rules a file-qualified path must not break.** **G-13's prefix coverage is a statement about
two paths inside one document**: a qualified path never covers, and is never covered by, a path in
another file, because "the element's leaves share one origin" is a claim about one file's value
tree. And **uniqueness of `field_path` within a ledger is tested on the qualified form**, so
`"defaults.panel_thickness_cm"` and `"components_registry.json:defaults.panel_thickness_cm"` are two
distinct claims and do not collide — while two entries naming the same qualified path are the
collision G-13 already catches.

Worked example, from the generated P5 files:

| Id | `field_path` | `value` | From |
|---|---|---|---|
| `A-023` | `"components_registry.json:defaults.panel_thickness_cm"` | `3.0` | `09-defaults.md` `D-CL-05` — the declared cladding/panel depth default |
| `A-024` | `"components_registry.json:defaults.joint_width_cm"` | `2.0` | `09-defaults.md` `D-FM-10` — the declared frame joint width default |

### 6.2 `cross_references`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `note` | string | yes | why this block exists |
| `conflict_sourced_paths` | array | yes | `{ path, conflict_ref }` for every path in `dimensions.json` whose origin is `conflict` |

This block exists so a reader of `assumptions.json` can see the full provenance picture without
opening a second file. It carries **no assumption ids** — it is explicitly not a second ledger, and
a `conflict_ref` appearing under `assumptions` would be a validation error.

---

## 7. `conflicts_resolved.json`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `schema_version` … `status` | — | yes | envelope, §3.1 |
| `precedence_rules` | object | yes | the ladder actually invoked, copied in so the log is self-contained |
| `conflicts` | array | yes | ≥ 0 entries; an empty array is a valid, meaningful result |

### 7.1 `precedence_rules`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `note` | string | yes | adoption status; **must name the file that owns the definitions** |
| `evaluation_order` | string | yes | how the ladder is walked |
| `rules[]` | array | yes | `{ id, name, statement }`, ascending by id |
| `non_conflict_fallback` | object | yes | the rule that may fill a silence but never decide a conflict |

> ⚠️ **The rule ids and names in the example file are PROPOSED and are not yet canonical.**
> `references/10-conflict-resolution.md` (P2b) owns the definitions. It must adopt `R1`–`R7` and the
> names below **verbatim**, or it must update `examples/conflicts_resolved.json` in the same change.
> A `rules_invoked` array always holds **bare ids** (`"R3"`), never names, so renaming a rule does not
> invalidate any conflict entry. If P2b changes the *set* of rules, `examples/` must be regenerated.

| Id | Proposed name | Statement |
|---|---|---|
| R1 | `CODE-SUPREMACY` | A statutory, regulatory or code requirement outranks every user statement, including an explicit one. |
| R2 | `SPECIFICITY` | Among competing user statements of the same class, the one that is more specific wins: a value tied to a named level, element or condition beats a bare global value. |
| R3 | `QUANTITY-OVER-SUMMARY` | A stated total loses to the stated parts that produce it. Parts are measurements; totals are usually summaries. |
| R4 | `BUILDABILITY` | A value that cannot be built — negative dimension, head above floor-to-floor, negative clearance, element outside its host — loses to any value that can be built. |
| R5 | `MODULE-ALIGNMENT` | A value that preserves the stated dimensional module or grid outranks one that breaks it. |
| R6 | `LATER-STATEMENT` | Same class, same specificity, no rule above discriminates: the statement appearing later in the source wins. |
| R7 | `DEFAULT-FILL` | **Not a conflict rule.** A documented default from `09-defaults.md` may fill a silence but may never decide a conflict. A default appearing in a `conflicts` entry is a bug. |

Evaluation is a **strict ladder, lowest id first**; the first rule that discriminates wins. That
ordering is load-bearing: R3 before R4 means a stated total loses to its own parts *before* anyone
asks whether the parts are buildable, which is the cheaper question and the one that is actually
asked of the input.

R6 exists because real briefs contradict themselves in ways no principle can resolve, and a
deterministic pipeline cannot leave a conflict unresolved. R6 is the honest last resort, and every
R6 resolution must say so in its own `statement` — an example does exactly that in C-004.

### 7.2 `conflicts[]`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `id` | string | yes | `C-001`, zero-padded, unique, ascending |
| `title` | string | yes | one line, the contradiction itself |
| `detected_in` | string | yes | which paragraphs of the input |
| `invariant_violated_if_unresolved` | string | yes | a `G-` id from §9 — ties the conflict to the mechanical check |
| `sources[]` | array | yes | ≥ 2 entries: `{ ref, statement, value, unit }` |
| `rules_invoked` | array | yes | bare rule ids, ascending; empty only if the entry documents an unresolved conflict |
| `rule_names_as_proposed` | array | yes | human-readable mirror of `rules_invoked`; marked as provisional |
| `resolution` | object | yes | below |
| `rejected[]` | array | yes | ≥ 1 entry: `{ ref, value, why_lost }` |
| `downstream_stages` | array | yes | stages whose output changes |

`resolution`:

| Key | Type | Req | Meaning |
|---|---|---|---|
| `chosen_sources` | array | yes | refs from `sources[]` |
| `chosen_value` | any | yes | the value that won |
| `statement` | string | yes | what was decided and why this rule |
| `resolved_paths` | array | yes | dotted paths in `dimensions.json` the decision writes to |
| `resulting_value_of` | string | yes | the single primary path |
| `downstream_effect` | string | yes | what visibly changes downstream — this is where the log earns its keep |

**Every loser is recorded, including the ones that were merely outranked.** "Rejected" does not mean
"wrong": C-004's losing parapet is a perfectly buildable 120 cm that simply lost on ordering, and
saying so is what lets someone reopen the decision without re-deriving the analysis. `why_lost` must
name the rule that beat it, not just express preference.

---

## 8. Reserved schemas

Not defined here — the owning stage completes each one. The key lists exist so no stage has to
invent a file shape from nothing, and so `dimensions.json` can be written with the consumers in mind.

### 8.1 `massing.json` (P3) — **defined**

> **What changed from the reserved sketch.** The reserved key list promised `extrusion_cm` and an
> `origin` per element. P3 replaces both: `extrusion_cm` becomes `z_range_cm` (a massing solid is
> always a prism in Z, and a two-number interval states that without a second axis field), and
> provenance moves to a file-level `origins` map identical to §5.2, so the traceability machinery
> that already works on `dimensions.json` works here unchanged. Nothing was ever written against
> the old names, so this is a definition, not a migration.

| Key | Purpose |
|---|---|
| `tolerances` | copied verbatim from `dimensions.json`. A builder may not widen them |
| `origin_inputs` | dotted paths in `dimensions.json` that this file read |
| `origins` | flat provenance map, same shape and rules as §5.2, covering this file's value tree |
| `defaults` | the values this file **assumes** rather than derives — P6's `facade_wall_thickness_cm` (09 `D-FW-01`, `A-025`). Every entry is `origin: assumed` with an `origin_ref`; there is no silent default |
| `storeys[]` | one entry per level: the storey volume plus the element ids that build it |
| `elements[]` | every placeable solid as a Z-prism: `id`, `kind`, `storey_index`, `profile_cm`, `profile_ccw`, `z_range_cm`, `layer` |
| `site_pad` | ground pad, paving and kerb — each a Z-prism on `00_SITE` |
| `grouping[]` | the assemblies that span storeys, with the dummy pivot each is parented to |

#### 8.1.1 The element solid

**Every massing element is a prism in Z:** a world-XY ring plus a Z interval. Anything that is not a
Z-prism is not massing — it is NURBS, and it belongs to P4. This is the constraint that makes the
whole file checkable and the emitted MAXScript trivial.

**A ring with a hole is not expressible here.** `profile_cm` must be a *simple* ring, so a hollow shape
— a parapet band, a light well, a courtyard wall — is decomposed into one prism per straight side rather
than given a hole list. A rectangular deck's parapet is therefore **four** `parapet` elements, not one.
This keeps the prism rule absolute; the alternative (a `holes[]` array) is a schema change that belongs to
whoever first needs a genuine void.

`elements[]`:

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^EL-\d{3}$`, unique, ascending | element id | — |
| `kind` | string | yes | — | `plinth` \| `slab` \| `column` \| `core_wall` \| `roof_deck` \| `parapet` \| `facade_wall` | what it is | — |
| `storey_index` | int or `null` | yes | — | `null`, or an index present in `storeys[]`; **never `null` for a `facade_wall`** | owning storey; `null` for site-wide and roof elements | — |
| `profile_cm` | array | yes | cm | ≥ 3 `[x, y]` vertices in **world** coordinates; no duplicate vertices; simple (non-self-intersecting) ring; CCW | horizontal outline | — |
| `profile_ccw` | bool | yes | — | `true` | declared winding, so G-21 has something to assert against | — |
| `z_range_cm` | array | yes | cm | `[z0, z1]` with `z1 > z0` | vertical extent | — |
| `layer` | string | yes | — | §8.1.4 vocabulary, and fixed per `kind` by §8.1.2 | target layer | — |

`defaults` — the values this file **assumes** rather than derives. It exists because a value
nothing dimensions must be *recorded*, not invented: the alternative is a silent default baked
into geometry, which is the P5 trap (`_p5-contract.md` §5.2). Every entry is
`origin: assumed` with an `origin_ref` naming an `A-nnn`, which is what makes it checkable.

| Key | Type | Req | Units | Range | Meaning |
|---|---|---|---|---|---|
| `facade_wall_thickness_cm` | float | yes | cm | 10–40 (09 `D-FW-01`) | modelled thickness of an opaque facade wall band — a massing proxy, **P6** |

`storeys[]`:

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `index` | int | yes | — | `== dimensions.levels[i].index` | storey index | — |
| `level_ref` | string | yes | — | an `id` in `dimensions.levels[]` | the level this storey was built from | — |
| `elevation_cm` | float | yes | cm | `== levels[i].elevation_cm`, tol 0.5 | floor level | — |
| `height_cm` | float | yes | cm | `== levels[i].height_cm`, tol 0.5 | floor to floor | — |
| `z_range_cm` | array | yes | cm | `[elevation_cm, elevation_cm + height_cm]`, tol 0.5 | the storey volume | — |
| `slab_ref` | string | yes | — | an `elements[].id` of kind `slab` | this storey's floor | — |
| `column_refs` | array | yes | — | ≥ 0 element ids, each of kind `column` | columns reaching this storey | — |
| `core_refs` | array | yes | — | ≥ 0 element ids, each of kind `core_wall` | core walls in this storey | — |

`site_pad` — three optional parts, each `{profile_cm, profile_ccw, z_range_cm}`, plus `layer`:

| Key | Type | Req | Meaning |
|---|---|---|---|
| `ground_pad` | object or `null` | yes | the pad the building sits on |
| `paving` | object or `null` | yes | hard landscaping |
| `kerb` | object or `null` | yes | the kerb line; `dimensions.json` has no kerb key, so this is `null` unless a later stage supplies one |
| `layer` | string | yes | always `00_SITE` |

`grouping[]` — the assemblies a `Dummy` will parent:

| Key | Type | Req | Meaning |
|---|---|---|---|
| `id` | string | yes | `^GRP-\d{3}$`, unique, ascending |
| `name` | string | yes | the dummy's node name in the scene |
| `kind` | string | yes | `site` \| `slabs` \| `columns` \| `core` \| `roof` \| `facade` — `facade` was reserved for P5/P6 and **P6 is that reservation being used**: it groups the `facade_wall` elements |
| `element_ids` | array | yes | ≥ 1 element ids. **Every element appears in exactly one group** |
| `parent_pivot_cm` | array | yes | `[x, y, z]`, equal to the group's bbox centre in XY and its minimum Z, tol 0.5 |
| `layer` | string | yes | `90_SCENE` — the dummy, never the payload |

#### 8.1.2 Kind → layer is fixed

A stage may not put a column on `05_FACADE`. The mapping is a table, not a preference, because
`assembly.json.layer_map` (P6) resolves against it.

| `kind` | layer |
|---|---|
| `plinth` | `00_SITE` |
| `slab` | `01_SLABS` |
| `column` | `02_STRUCTURE` |
| `core_wall` | `03_CORE` |
| `roof_deck` | `04_ROOF` |
| `parapet` | `04_ROOF` |
| `facade_wall` | `05_FACADE` |

#### 8.1.3 Why `layer` is data at P3

**Verified 2026-10-04: an object's layer cannot be assigned from MAXScript in Max 2026.** Six routes
were executed and all threw (`node.layer = "name"`, assignment from `LayerManager.getLayerFromName`,
`node.setLayer`, `node.setProperty #layer`, `LayerManager.setLayerNode`, `LayerManager.setLayer`); see
`CHECKPOINT.md` §"Scene units and placement semantics" for the transcripts. Layer *creation*
(`LayerManager.newLayerFromName`) and layer *reading* (`node.layer.name`) do work.

So `build_spec.py` emits **geometry only**, and the layer column is data that P6 applies through
`3dsmax-mcp_manage_layers`. This is recorded here so a later stage does not "fix" the builder by
adding layer code that cannot work.

#### 8.1.4 The layer vocabulary — closed

Eight names. Authoritative **here**; `11-layer-standard.md` documents the intent of each and must not
introduce a tenth without changing this table first.

| Layer | Holds |
|---|---|
| `00_SITE` | ground pad, paving, kerb, plinth, steps, ramps |
| `01_SLABS` | floor slabs and ground slabs |
| `02_STRUCTURE` | columns, beams, bracing |
| `03_CORE` | core walls, core slabs, stair and lift shafts |
| `04_ROOF` | roof deck, parapet, coping, upstands |
| `05_FACADE` | panels, glazing, mullions, transoms, spandrels, reveals, doors, and the modelled `facade_wall` band P6 cuts its openings in |
| `90_SCENE` | cameras, lights, dummies, helpers |
| `99_DEBUG` | QA probes, scatter sources, reference and wireframe geometry |

`90_SCENE` and `99_DEBUG` carry no massing payload at P3 except grouping dummies.

### 8.2 `nurbs.json` (P4, extended P4b) — **defined**

> **What changed from the reserved sketch.** The sketch promised five kinds (`rail_sweep`,
> `revolve`, `freeform`), per-surface `closed_u` / `closed_v`, a separate `relations` edge list for
> trim/blend/offset/project, and `sections` carrying "knot/degree parameters". **All of that was
> re-derived against the library that actually exists**, because at P4 it was a paragraph of
> intention, not a description of code. What survived is smaller:
>
> - **Four independent kinds, executed live on 2026-10-04:** `u_loft`, `uv_loft`, `point_grid`,
>   `cv_grid`. **Four dependent kinds, added at P4b on executed transcripts:** `rail_sweep`,
>   `two_rail_sweep`, `blend`, `trim`.
> - **`closed_u` / `closed_v` are gone.** No surface class in this build has a `closeU` or `closeV`
>   at all — `NURBSPointSurface().closeU` fails with `Unknown property: "closeU"`. Closure is a
>   property of the *section curves*, and the library takes it as one flag per loft
>   (`closed_sections`), not per curve.
> - **`relations` is gone, and the four relation kinds now live in `surfaces[]`.** At P4 the only
>   relation the *library* wraps is a parallel offset shell, and it is an argument of the loft
>   (`thickness_cm`), not an edge between two surfaces. Rail sweep, blend, project-vector and trim
>   were recorded at P4 as **not implemented**; that was a **false negative**, disproved by execution
>   at P4b — all four classes construct, commit inside a `NURBSNode`, evaluate, and expose their
>   relational properties *after* commit (§8.2.6). They are expressed as ordinary `surfaces[]`
>   entries with their own kind-specific keys (§8.2.7), **not** as edges in a second table: a
>   `blend` or a `trim` references its parents by id, which is an ordinary reference and was already
>   expressible. The `relations` table stays out.
> - **Knots are gone from the spec.** `setClampedKnots` / `setSurfaceClampedKnots` derive a clamped
>   uniform knot vector from `order` and the point count. A spec that declared knots would be
>   declaring something the builder overwrites. Only `u_order` / `v_order` survive.
>
> One primitive underlies all eight kinds: **an ordered list of point rows**. A `u_loft`'s rows are
> its sections; a grid's rows are its lattice; a **rail** and a **trim profile** are rows too. That
> is why there is a single `sections[]` table and no per-kind geometry syntax, and it is why the P4b
> extension introduces **no new primitive** — only new references to the one that already exists.

Envelope: `schema_version` · `spec` · `project` · `units` · `source` · `status` · `tolerances`
(copied verbatim from `dimensions.json`; a builder may not widen them) · `origin_inputs` ·
`origins` (per §5.2) · `sections` · `surfaces` · `derivatives`.

#### 8.2.1 `sections[]`

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^SEC-\d{3}$`, unique, ascending | identity | — |
| `points_cm` | array | yes | cm | ≥ 2 entries; each exactly 3 finite numbers | the row, in order | — |
| `name` | string | no | — | unique in file, no `-` | curve name inside the set | `Section_<n>` |

**There is deliberately no `closed` key here.** The library applies one `closed_sections` flag to
every curve of a loft (`createULoftShell closedSections:`), so a per-section flag would be a value
the builder cannot honour. Closure lives on the surface.

#### 8.2.2 `surfaces[]`

Common keys:

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^SUR-\d{3}$`, unique, ascending | identity | — |
| `name` | string | yes | — | unique in file, no `-` (rule N1 of `11`) | node name in the scene | — |
| `kind` | string | yes | — | §8.2.3 vocabulary | construction route | — |
| `layer` | string | no | — | `04_ROOF` \| `05_FACADE` | §8.1.4 vocabulary. Layer stays **data** — MAXScript cannot assign it (P3) | `04_ROOF` |
| `mat_id` | int | no | — | ≥ 1 | sub-material index | `1` |
| `hide_curves` | bool | no | — | — | hide the section curves in the viewport | `true` |
| `merge_tol_cm` | float | no | cm | ≥ 0 | `NURBSSet.merge` | `0.15` |
| `approximation` | object | no | — | §8.2.4 | view + render tessellation | see §8.2.4 |

Kind-specific keys — **exactly** the ones the kind needs, and no others (G-43):

| Kind | Required | Optional | Forbidden |
|---|---|---|---|
| `u_loft` | `section_ids` (≥ 2, ordered) | `closed_sections` (bool, `false`), `thickness_cm` (float) | `u_section_ids`, `v_section_ids`, `u_order`, `v_order`, `weights` |
| `uv_loft` | `u_section_ids` (≥ 1), `v_section_ids` (≥ 1) | — | `section_ids`, `closed_sections`, `thickness_cm`, `u_order`, `v_order`, `weights` |
| `point_grid` | `section_ids` (≥ 2, ordered as rows) | — | `u_section_ids`, `v_section_ids`, `closed_sections`, `thickness_cm`, `u_order`, `v_order`, `weights` |
| `cv_grid` | `section_ids` (≥ 2, ordered as rows) | `u_order` (2–5), `v_order` (2–5), `weights` (flat, ≤ `nU·nV`) | `u_section_ids`, `v_section_ids`, `closed_sections`, `thickness_cm` |
| `rail_sweep` | `rail_section_ids` (exactly 1), `section_ids` (≥ 2, ordered) | `parallel` (bool, `true`) | `u_section_ids`, `v_section_ids`, `closed_sections`, `thickness_cm`, `u_order`, `v_order`, `weights` |
| `two_rail_sweep` | `rail_section_ids` (exactly 2), `section_ids` (≥ 2, ordered) | `parallel` (bool, `true`) | `u_section_ids`, `v_section_ids`, `closed_sections`, `thickness_cm`, `u_order`, `v_order`, `weights` |
| `blend` | `parent1_ref`, `edge1`, `parent2_ref`, `edge2` | `tension1` (float, `0.0`), `tension2` (float, `0.0`) | `section_ids`, `rail_section_ids`, `surface_ref`, `trim_section_ids`, `p_vec`, `seed`, `flip_trim`, `parallel` |
| `trim` | `surface_ref`, `trim_section_ids` (≥ 1 closed profile), `p_vec` | `seed` (array, `[0.5, 0.5]`), `flip_trim` (bool, `false`) | `section_ids`, `rail_section_ids`, `parent1_ref`, `parent2_ref`, `edge1`, `edge2`, `tension1`, `tension2`, `parallel` |

The last four rows are the **P4b dependent kinds**; §8.2.7 gives their geometry, types, units and
defaults, and this table is their authority on presence and absence.

**Why the forbidden column is what it is.** The authoritative design names each dependent kind's
keys and nothing else, so the forbidden set follows from G-43's own wording — *a surface carries
exactly the keys its kind requires and none of the forbidden ones* — rather than from a second
decision. Every §8.2.2 key outside a kind's own Required/Optional pair is forbidden on it. Two
consequences worth stating: `thickness_cm` is **not** available on a dependent surface (the offset
shell is an argument of the loft, F6, not of these classes), and neither dependent kind takes
`closed_sections` (the library's closure flag belongs to the loft helpers only — a trim profile's
closure is a property of its own row, §8.2.8).

`thickness_cm` is the **offset shell** distance. `|thickness_cm| < 0.001` is a FAIL, not a rounding
detail: the library tests `(abs thickness) > 0.001` and *silently omits the offset surface*
otherwise, so a 0.0005 shell would be a spec that builds to nothing.

`weights` is one flat row-major array over the lattice (`row 1` left to right, then row 2), matching
the library's `(iv - 1) * nU + iu` indexing. Missing entries are `1.0`.

`rail_section_ids` and `trim_section_ids` reference `sections[]` ids **exactly as `section_ids`
already does** — same `^SEC-\d{3}$` form, same resolution rule, same "consumed at least once" rule
(G-44). A rail is a row of points, a trim profile is a row of points, and neither is a second
geometry syntax.

#### 8.2.3 Vocabulary

`kind` ∈ `u_loft` (sections lofted along U) · `uv_loft` (Gordon network from a U and a V family) ·
`point_grid` (a surface interpolating a rectangular lattice of points) · `cv_grid` (a B-spline
surface *controlled* by a rectangular CV lattice) · `rail_sweep` (cross-sections swept along **one**
rail) · `two_rail_sweep` (cross-sections swept along **two** rails, section width adapting to rail
separation) · `blend` (a G1/G2 transition between **two surface edges**) · `trim` (a closed profile
**projected onto a surface** along a vector; the `trim` kind **projects only and does not cut** —
§8.2.7).

**The list is closed.** A stage that needs a ninth kind adds it here first, with its keys, its
forbidden set and its invariant, per §12 — it does not extend the vocabulary inside a builder.

**Kinds are geometric.** None of the eight names a MAXScript class, plugin or tool; `rail_sweep` is
not `NURBS1RailSweepSurface`. §12's standing rule is the reason these names are correct, and §8.2.7
names the implementing class only as the builder's implementation detail.

**`point_grid` and `cv_grid` are not interchangeable**, and the difference is architectural, not
cosmetic:

| | `point_grid` | `cv_grid` |
|---|---|---|
| Surface passes through every lattice point | **yes** — it interpolates | **no** — interior CVs only pull the surface |
| Where the surface may lie | **outside** the lattice hull between points | **inside** the CV convex hull, always |
| Parameter domain | **chord-length**: measured live, `u=[0, 434.555]`, `v=[0, 307.439]` for a 400 × 300 cm lattice | normalised `[0, 1]` |
| Use when | the lattice *is* the design intent: a dome ring grid, a freeform soffit | the lattice is a control cage: a ruled blend of two profiles |

Measured on the worked example, both lattices nominally identical in footprint (600 × 450 cm) and
rising 60–90 cm, sampled off the same 8 × 6 and 4 × 2 divisions:

| | `point_grid` (SUR-002 canopy) | `cv_grid` (SUR-003 canopy cage) |
|---|---|---|
| Lattice peak | 510 cm | 480 cm |
| Node bbox max Z | **568.226 cm** — 58 cm *above* the lattice, between lattice points | **480 cm** — exactly the hull, never above |
| Sampled surface max Z | 515.998 cm (space frame on it) | **448.125 cm** — 32 cm *below* the lattice it was given |

Those four numbers are the whole argument, and they are measurements, not theory: an interpolating
surface **overshoots** the points you gave it, and a controlled surface **undershoots** them. QA must
therefore compare **evaluated** geometry against the lattice, never the lattice against itself.
> **CORRECTED (verified 2026-10-06):** this sentence previously ended *"(this is what **P8 asserts**)"*.
> **P8 was cancelled by user decision on 2026-10-05** — there is no automated QA stage and no
> `qa.json` gate. **Nothing asserts this automatically.** It remains a *rule this file states*: any
> check against a lattice is a human or agent read-back of `evalPos` against the expected bounds,
> not a pipeline gate. The four measured numbers above are the evidence; the obligation is manual.

**Domain is a per-kind fact, not a constant.** The table above gives the two grid domains; both sweep
kinds were measured at `[0,1]` on their committed surfaces, `u=[0,1] v=[0,1]`, exactly like `cv_grid`.
That is what makes `trim.seed` (§8.2.7) a domain-sensitive key — see §8.2.8.

#### 8.2.4 `approximation`

Maps `applyArchTessellation`. All optional; the defaults are the library's.

| Key | Type | Units | Default | Meaning |
|---|---|---|---|---|
| `view_steps_u` | int ≥ 1 | — | `6` | viewport U steps |
| `view_steps_v` | int ≥ 1 | — | `6` | viewport V steps |
| `render_edge_pct` | float | % | `4.0` | spatial-and-curvature edge threshold |
| `render_angle_deg` | float | ° | `6.0` | curvature angle |
| `merge_tol_cm` | float | cm | `0.15` | view approximation merge tolerance |

#### 8.2.5 `derivatives[]`

New scene geometry computed **from** a surface in this file. It is a separate table because a
derivative has a surface *reference*, and a reference is an edge — the thing §8.2's old sketch put
in `relations` and this schema keeps out of `surfaces[]`.

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^DRV-\d{3}$`, unique, ascending | identity | — |
| `kind` | string | yes | — | `quad_panels` \| `space_frame` | see below | — |
| `surface_ref` | string | yes | — | an id in `surfaces[]` | the surface to read | — |
| `name` | string | yes | — | unique in file, no `-` | output node name | — |
| `layer` | string | no | — | `04_ROOF` \| `05_FACADE` \| `99_DEBUG` | `99_DEBUG` marks a QA intermediate | `99_DEBUG` |
| `divisions_u` | int | yes | — | ≥ 1, exact | cells across U | — |
| `divisions_v` | int | yes | — | ≥ 1, exact | cells across V | — |
| `thickness_cm` | float | no | cm | ≥ 0, `space_frame` only | member thickness | `10.0` |
| `sub_steps` | int | no | — | ≥ 1, `space_frame` only | knots per member | `4` |

`quad_panels` samples the surface analytically into a quad-only mesh — a panelisation that needs no
boolean. `space_frame` lays a 3D diagrid over the surface as a renderable spline cage.

**A derivative reads the *design* surface: the first `NURBSSurface` sub-object of the referenced node.**
A `thickness_cm` shell appends its offset surface *after* the base loft, so on a shelled surface the
last `NURBSSurface` is the offset and the first is the soffit you actually panelised. Measured on
`SUR-001_Vault`: 52 sub-objects, base surface at 51, offset at 52; sampling the first gives panels
spanning `z 420 → 600.97` (the design surface) and sampling the last gives `441.043 → 625.94` (the
25 cm shell). The rule is in the builder, and `G-43` is not what enforces it — the builder's
resolution order is.

**Rail sweeps, blends and trims are in this schema as of P4b**, as `surfaces[]` kinds (§8.2.7) rather
than as derivative kinds — a derivative produces *new* geometry *from* a surface, while these produce
a surface *from* other surfaces and therefore live where a surface is declared. §8.2.6 carries the
recovered keyword map and §8.2.8 the emission and read-back constraints that decide what a spec is
allowed to say about them.

#### 8.2.6 Dependent surfaces — the recovered keyword map (evidence, not schema)

> **This subsection corrects a P4 false negative.** P4 probed 15 candidate
> property names on freshly constructed `NURBS1RailSweepSurface` / `NURBS2RailSweepSurface` /
> `NURBSBlendSurface` / `NURBSProjectVectorCurve` objects, got an error on **every** name, and
> concluded the classes were unimplemented. Two things were wrong, both established by execution at
> P4b: the probe read the objects **before they were committed**, and it used `o["name"]`, which is
> not valid dynamic property access in MAXScript and fails for *every* name including known-good
> ones (`o["renderable"]` → error, while `o.renderable` → `true`; `getProperty o #x` also fails). A
> uniform error across a heterogeneous name list is a **broken probe, not a uniform absence**.
> `references/nurbs-complete-guide.md` and `references/nurbs-architecture-recipes.md` were right all
> along, including the `parent1ID:` / `parent2:` recipe.
>
> The capability is real. All four construct → commit → evaluate, and their relational properties are
> readable **on the committed sub-object**. That evidence is what the P4b kinds are built on: §8.2.7
> is the schema those transcripts justify, and §8.2.8 is the list of things a spec may not encode
> because Max will not read them back.

**Recovered keyword map.** Existence of each name is proved by **type mismatch** (passing a string to
a name that exists errors on conversion; a name that does not exist is silently swallowed), values
by commit + read-back. It is **not** proved by construction: the constructor accepts *any* keyword —
`NURBS1RailSweepSurface totalBogusName: 1` constructs fine, with no error — so a successful
construction proves nothing at all about a keyword. Introspection is not a route either:
`inspect_plugin_class "NURBS1RailSweepSurface"` returns `Unknown class`, a second false negative of
the same family as `NURBSSet`, so every row below is an execution transcript and nothing else.

| Class | Keywords that exist | Transcript |
|---|---|---|
| `NURBS1RailSweepSurface` | `rail` `railID` `parallel` `numCurves` `axisTM` | 3-point rail, 3 sections, `rail:` + `parallel:` + one `appendCurve` per section → surface committed at index 14, `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[500,0,100]` = exact expected midpoint. Committed read-back: `rail=0 parallel=true numCurves=3`, with `railID` returning an `IntegerPtr` whose **printed form is UNVERIFIED** — see the correction under *Measurement caveats* below |
| `NURBS2RailSweepSurface` | `rail1` `rail1ID` `rail2` `rail2ID` `parallel` `numCurves` | two parallel rails 500 cm apart, 3 transverse sections, `rail1:` `rail2:` `parallel:` → `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[550,200,0]` = exact midpoint between the rails |
| `NURBSBlendSurface` | `parent1` `parent1ID` `parent2` `parent2ID` `edge1` `edge2` `tension1` `tension2` | two point surfaces + `parent1:` `parent2:` `edge1:` `edge2:` `tension1:` `tension2:` → **3** surfaces; read-back `parent1=0 parent2=0 edge1=1 edge2=1 tension1=1.0`; `evalPos(0.5,0.5)` = `[-50.0011,100,100]` |
| `NURBSOffsetSurface` | `parent` `parentID` `distance` | already verified at P4 — F6 `createULoftShell` PASS, 20 sub-objects: loft + offset surface |
| `NURBSProjectVectorCurve` | `parent1` `parent1ID` `parent2` `parent2ID` `pVec` `seed` `trim` `flipTrim` | plane + closed 5-point circle above it, `pVec:[0,0,-1] trim:true` → read-back `parent1=0 parent2=0 seed=[0.5,0.5] trim=true flipTrim=false`, **and a second surface appears in the set** (`surfaces=#(10,11)`) — but it is **not a trim result**: a second, structurally different profile spanning the whole vault width produced a byte-identical set (`nObj=7`, one surface, `Y 0…900`, `numCVs [9,4]`), and `trim:false` adds **no surface at all**. That second surface is an untrimmed `NURBSCVSurface` **copy of the parent** (§8.2.7) |

**The two rules that make the map usable.** Both are the generalisation of the commit rule §8.2.5
already states for `evalPos`, and both must survive into any builder written for these classes.

- **Commit before you read.** Relational properties are readable **only on the committed
  sub-object**. On a freshly constructed, unattached `NURBS1RailSweepSurface`, `rail` / `railID` /
  `parallel` / `numCurves` / `axisTM` / `parent*` / `distance` **all** fail; the same surface after
  `appendObject` + `NURBSNode` returns `rail=0 parallel=true numCurves=3`, with `railID` readable but of
  unestablished printed form (correction below). The commit is part of the measurement, not part of the
  build.
- **Verify the committed set, never the keyword.** An **invalid dependent surface is silently
  dropped** at commit — no error, no warning, it simply is not in the set. A sweep with no rail set
  gives `numObjects=7` and **no `NURBSSurface` at all**; the same sweep with `rail:` set gives
  `numObjects=14`, index 14 being the surface. So a builder cannot conclude success from a
  successful construction: it must assert that the committed set contains the **expected number of
  `NURBSSurface` sub-objects** and fail loudly otherwise, or emit geometry that silently lost its
  rail. This is the P4 lesson generalised — measure the output, do not trust the input — and it is
  the reason the schema extension carries a builder self-check.

**Measurement caveats.** Every one of these is a read-back transcript, so a future builder may not
assert the value it passed.

| Property | What was passed | What reads back |
|---|---|---|
| `parent:` · `rail:` · `rail1:` | the 1-based set index passed to the constructor | **`0`** — never the index |
| `railID` | an integer | **not the index** — an `IntegerPtr`, printed `<decimal>P` (`railID=0P` on a 1-rail sweep; `rail1ID` reads the full pointer on a 2-rail one). **Never parse or compare it** (correction below) |
| `pVec` | `[0,0,-1]` | **`[0,0,1]`** — the opposite sign. Do not assert `pVec` round-trips; assert `trim` / `seed` / `parent*` instead |

> **The `"0P"` question is CLOSED (2026-10-06), and it closes in favour of the ORIGINAL reading.**
> This note previously retracted the committed `railID = "0P"` as "not reproduced", on the grounds that
> `o.nurbsID` printed as a large decimal + `P`. **Both were the same format at different magnitudes.**
> Measured: the class is `IntegerPtr`, the form is `<decimal>P`, `railID` on a committed 1-rail sweep
> reads `0P` (3 reps of identical geometry, 3 readings of `0P`), and `rail1ID` / `rail2ID` on a
> committed 2-rail sweep read the **full** pointer and equal the rail curve's own `nurbsID`. The value
> also **changes between builds of identical geometry**, so it must never be persisted.
>
> **The format is known and still must not be asserted on.** What actually survives is unchanged and
> is the rule a builder depends on: it is an `IntegerPtr`, it is **not** the set index passed in, and
> a **synthetic literal in that slot hard-crashes Max** (below). Any value in a `rail*ID:` /
> `parent*ID:` position must be a variable bound from a committed sub-object, never a literal in any
> format — `G-56`. Transcript in `12-nurbs-gotchas.md` §3.29.
>
> ⚠️ **Also measured here: `getProperty <o> (<name> as name)` works on these plugin classes.** Only
> the `#name` literal form fails. Use the coerced-string form for any name you do not want to
> hard-code.

Both sweep types carry a **`[0,1]`-normalised domain**, unlike `point_grid`'s chord-length domain
(§8.2.3) — measured on the committed surfaces, not assumed from the class name.

**Which surface is "the" surface.** In a set of N surfaces the design surface is **not** always the
first: a **sweep** test needs the **first** (`NURBSSurface`, the §8.2.5 offset-shell trap), while a
**`NURBSBlendSurface` is the last**. So the §8.2.5 rule generalises rather than covering the case:
resolve by superclass **and** confirm the candidate carries the relational properties just set. Never
hardcode a literal index — sub-object indices are not knowable before the set is built (§9.7).

#### 8.2.7 The four dependent kinds — schema (P4b)

These are ordinary `surfaces[]` entries: every common key of §8.2.2 applies (`id`, `name`, `layer`,
`mat_id`, `hide_curves`, `merge_tol_cm`, `approximation`), and their kind-specific keys are the last
four rows of §8.2.2. **No new top-level key and no new primitive** — rails and trim profiles are
`sections[]` rows like everything else. What changes is that a surface may now *depend* on other
surfaces, which is why `parent1_ref` / `parent2_ref` / `surface_ref` are references to `SUR-nnn` ids
**declared earlier in the same file**, following the existing `derivatives[].surface_ref` convention.

The MAXScript each kind emits is fixed by the authoritative design and is recorded here as the
builder's obligation, not as a spec field:

| Kind | Emitted |
|---|---|
| `rail_sweep` | `NURBS1RailSweepSurface rail:<i> parallel:<b>`, then one `appendCurve` per cross-section |
| `two_rail_sweep` | `NURBS2RailSweepSurface rail1:<i> rail2:<j> parallel:<b>`, then one `appendCurve` per cross-section |
| `blend` | `NURBSBlendSurface parent1ID:<id1> edge1:<n> parent2ID:<id2> edge2:<n> tension1:<f> tension2:<f>` |
| `trim` | `NURBSProjectVectorCurve parent1ID:<id1> pVec:[…] seed:[…] trim:false flipTrim:<b>` |

**A dependent surface references its parents; it does not rebuild them.** `parent1_ref` /
`parent2_ref` / `surface_ref` resolve to the parent's **committed** surface. The builder binds that
surface's `nurbsID` immediately after the parent node is committed — the first `NURBSSurface` in the
parent's committed set, per §8.2.5 — and emits the **variable**, never the value:

```
local id1 = (getObject (getNURBSSet <parentNode> #relational) <i>).nurbsID
local id2 = (getObject (getNURBSSet <parentNode> #relational) <j>).nurbsID
NURBSBlendSurface parent1ID:id1 edge1:4 parent2ID:id2 edge2:4 tension1:0.0 tension2:0.0
```

The parent is **not** re-instantiated inside the relation's set. Measured (executed 2026-10-04): the
relation set then holds **one** sub-object, `evalPos` works, and the blend's bbox is identical to the
in-set re-instantiation at the same tension (`bbY = 450.0…900.0`, `bbZ = 420.0…600.97` at
`tension1:0.0 tension2:0.0`, `rd_p1id` reading back the parent's own id). The id-binding was executed
on `blend`; `trim`'s `surface_ref` uses the same binding through the `parent1ID` slot its own keyword
map declares (§8.2.6). Three consequences, all of them contract-level rather than implementation
detail:

- **A parent keeps its own node.** Nothing is consumed by being referenced, so there is no
  `consumed` bookkeeping, no rule forbidding reuse, and a `derivative` that names the same surface
  keeps working. A parent named by **two** relations is instantiated **once**, not three times.
- **A relation's set contains the relation and nothing else**, so `G-54`'s expectation for a relation
  is a small constant — `1` `NURBSSurface` for a sweep or a blend, `0` for a `trim` — instead of a
  count that includes its parents.
- **Lifetime caveat, one case measured, not a guarantee.** After the parent node was deleted the
  relation kept evaluating: `objects=1`, `rel nObj=1`, `evalPos(0.5,0.5)=[899.861,900,600.97]`, no
  crash and no change. Record it as "did not break in the one case measured".

**A `nurbsID` is a pointer, and a synthetic one crashes Max.** This is the reason the binding above is
mandatory rather than tidy. Measured (executed 2026-10-04):

```
parent1ID:"2276505581808P"   ->  ERROR: Unable to convert: "2276505581808P" to type: IntegerPtr
parent1ID:<bound variable>    ->  commits and evaluates correctly
parent1ID:12345              ->  EXCEPTION_ACCESS_VIOLATION
                                 -- Access violation, read of address 0x0000000000003089
```

The third line is a **hard crash of the 3ds Max process**, not a catchable MAXScript error, and it is
not recoverable from inside the script. So: **no literal in a `parent1ID:` / `parent2ID:` position,
ever** — the same rule as "no literal sub-object index", extended from an index to a pointer, and
enforced as `G-56`.

**`rail_sweep` — one rail, many cross-sections.** Cross-sections are swept along a single rail; the
rail is the spine and each cross-section is a row placed at its station along it.

| Key | Type | Card. | Units | Constraint | Default | Meaning |
|---|---|---|---|---|---|---|
| `rail_section_ids` | array of `SEC-nnn` | **exactly 1** | — | id resolves in `sections[]` | — | the rail |
| `section_ids` | array of `SEC-nnn` | ≥ 2, ordered | — | ids resolve; every cross-section row has the same point count as the other cross-sections (G-42) | — | the cross-sections, in station order |
| `parallel` | bool | 1 | — | — | `true` | passed straight through as `parallel` |

Verified: a 3-point rail and 3 sections with `rail:` + `parallel:` set → the surface commits at index
14, `u=[0,1] v=[0,1]`, and `evalPos(0.5,0.5)` = `[500,0,100]`, the exact expected midpoint. Read-back
`rail=0 parallel=true numCurves=3`, with the `railID` printed form **unestablished** (§8.2.6).
**What `parallel: false` means geometrically is not
established by any transcript** — only that `true` round-trips; see the escalation list below.

**`two_rail_sweep` — two rails.** Cross-sections are swept along two rails and the section width
adapts to the rail separation.

| Key | Type | Card. | Units | Constraint | Default | Meaning |
|---|---|---|---|---|---|---|
| `rail_section_ids` | array of `SEC-nnn` | **exactly 2**, ordered | — | both ids resolve; element 0 is rail 1, element 1 is rail 2 | — | the two rails |
| `section_ids` | array of `SEC-nnn` | ≥ 2, ordered | — | as `rail_sweep` | — | the cross-sections |
| `parallel` | bool | 1 | — | — | `true` | passed straight through as `parallel` |

Verified: two parallel rails 500 cm apart with 3 transverse sections → `u=[0,1] v=[0,1]` and
`evalPos(0.5,0.5)` = `[550,200,0]`, the exact midpoint between the rails. The ordering convention
(element 0 → `rail1`) is what makes a 2-element array unambiguous; no transcript read the two rails
back apart, because `rail1` also reads `0`.

**`blend` — a G1/G2 transition between two surface edges.** The surface spans the gap between the two
selected edges, with controlled tangent tension at each end.

| Key | Type | Card. | Units | Constraint | Default | Meaning |
|---|---|---|---|---|---|---|
| `parent1_ref` | string | 1 | — | `^SUR-\d{3}$`, resolves to a surface **declared earlier in this file** | — | first parent |
| `edge1` | int | 1 | — | `1..4` = low-U, high-U, low-V, high-V, **of parent 1** | — | which edge of parent 1 |
| `parent2_ref` | string | 1 | — | as `parent1_ref` | — | second parent |
| `edge2` | int | 1 | — | `1..4`, as `edge1`, **of parent 2** | — | which edge of parent 2 |
| `tension1` | float | 0 or 1 | — | `0.0 … 1.0` (G-55) | `0.0` | tangent continuity at edge 1 |
| `tension2` | float | 0 or 1 | — | `0.0 … 1.0` (G-55) | `0.0` | tangent continuity at edge 2 |

**`edge1` / `edge2` are two independent edge selections, not two ends of a shared seam.** The blend
spans the gap between them and **the parents need not touch** — nothing in this grammar asks for
adjacency and no transcript produced one. All 16 `edge1` × `edge2` combinations were built and
measured on a controlled pair of 200 cm patches (`P` planar at `z = 0`, `x/y 0…200`; `Q` rising to
`z = 200` at `x = 400`; `P`'s high-U and `Q`'s low-U both at `x = 200`; **executed 2026-10-04**). All
16 commit, and every `edge1` / `edge2` / `tension1` / `tension2` reads back **exactly as set**. Two of
the combinations are hazards that neither Max nor any check in §9 reports:

| Combination | Measured blend bbox | Failure |
|---|---|---|
| `edge1: 2` / `edge2: 1` — the pair that genuinely shares the seam, `P`'s high-U against `Q`'s low-U, both at `x = 200` | `200,0,0 … 200,200,0` | **Zero area.** No error, no warning, no surface worth having: there is no gap to span and the class does not check for one |
| `edge1: 3` / `edge2: 3` and `edge1: 4` / `edge2: 4` — both edges on the **same side of the same axis** | `0,−111.8,0 … 400,0,200` and `0,200,0 … 400,311.8,200` | Bulges outside **both** parents, up to **111 cm** on a 200 cm patch |

The controlled pair is what makes those two combinations degenerate: `P` and `Q` share the same
`y 0…200` extent, so edge `3` is the plane `y = 0` on both parents and edge `4` is `y = 200` on both.
On parents of **different** extent the same numbers select a genuine gap — `edge1: 4 edge2: 4` between
the example's vault (high-V at `y = 900`) and canopy (high-V at `y = 450`) is the `tension 0.0` soffit
measured below, not a bulge. The hazard is the two selected edges landing together, and the number
alone does not tell you which case you are in.

A reviewer choosing an edge pair owns both of these; `G-52` checks the range `1..4` and cannot see the
parents' geometry, because the parents' committed edges are not in the JSON. That is escalated in
§8.2.8 rather than asserted here as a check.

**`tension1` / `tension2` are optional, and the default `0.0` is the geometrically correct value.**
A tension of `0.0` is the **straight transition between the two selected edges**; a value above `0`
pushes the blend outward past **both** edges, and the overshoot grows with the tension. **Max does
not bound it** — which is why the schema does, at `0.0 … 1.0` (G-55). Measured on the worked
example's own geometry (vault high-V edge at `y = 900`, canopy high-V edge at `y = 450`; blend bbox
sampled on a 7 × 7 grid over the blend's **own** committed domain, not the node bbox, which also
contains the parents; **executed 2026-10-04**):

| `tension1` / `tension2` | blend bbox Y | blend bbox Z |
|---|---|---|
| `1.0 / 1.0` | 450 … **1195.64** | **369.758** … 600.97 |
| `0.5 / 0.5` | 450 … 995.514 | 401.084 … 600.97 |
| `0.0 / 0.0` | **450 … 900.0** | **420.0** … 600.97 |
| `1.0 / 0.0` | 450 … 1081.41 | 420.0 … 600.97 |

`0.0 / 0.0` fills **exactly** between the two selected edges — `Y 450…900`, `Z 420…600.97`, the vault
springing at 420 through the 600.97 crown — which is a soffit panel and is correct. `1.0 / 1.0` on
the same edge pair bulges **295.64 cm past the vault's own `y = 900`** and drops to `z = 369.758`,
i.e. 50 cm below the springing: that is the `SUR_006_CanopySoffit` defect, whose bbox reached
`y = 1518` against a 900 cm deep plan. The mixed row shows the two keys are independent — `1.0 / 0.0`
pushes the far end out and leaves the near end straight — so a spec that wants the straight transition
states neither.

**`trim` — a closed profile projected onto a surface, and nothing more.** A closed profile row is
projected along a vector onto a parent surface. **It does not cut.** The `trim` kind is
**projection-only**; cutting an aperture is not something this class does, and it needs a Boolean
modifier or a surface split, which is outside the NURBS stage.

| Key | Type | Card. | Units | Constraint | Default | Meaning |
|---|---|---|---|---|---|---|
| `surface_ref` | string | 1 | — | `^SUR-\d{3}$`, resolves to a surface **declared earlier in this file** | — | the surface projected onto |
| `trim_section_ids` | array of `SEC-nnn` | ≥ 1 | — | ids resolve; each row is a **closed** profile (§8.2.8) | — | the profiles to project |
| `p_vec` | array | 1 | cm components; a **direction**, magnitude meaningless | exactly 3 finite numbers, **non-zero magnitude** (G-53) | — | projection direction |
| `seed` | array | 0 or 1 | — | exactly 2 finite numbers, in the **parent surface's own** parameter domain (G-53) | `[0.5, 0.5]` | where the profile starts on the parent |
| `flip_trim` | bool | 0 or 1 | — | — | `false` | passed straight through as `flipTrim` |

**Why the emission writes `trim:false`.** `trim:true` does not trim. It adds an **untrimmed
`NURBSCVSurface` copy of the parent** into the relation's set. Proven on the worked example's vault
with two structurally different profiles — the narrow `SEC-023` (`x 750…1050`, `y 375…525`) and one
widened to span the whole vault (`x −200…1900`, `y 300…500`), which a real trim would have split into
two disjoint pieces — producing **byte-identical** output: `nObj=7`, one `NURBSCVSurface`,
`Y 0.0…900.0`, `Z 420.0…600.97`, `numCVs = [9,4]` (**executed 2026-10-04**; `numCVs` is itself
unexplained for a 5-rib loft and is recorded as unverified). `trim:false` adds **no surface at all**.
So the emitted MAXScript uses `trim:false`, which is the reason for the choice: the relation's node
then carries **no duplicate parent shell**, and its `G-54` census expectation is **0
`NURBSSurface`**. A `trim` node is the projected profile, not a cut parent.

Verified read-back on the committed relation: `parent1=0 parent2=0 seed=[0.5,0.5] trim=true
flipTrim=false`. `trim`, `seed` and `flipTrim` remain readable flags on the projected curve, and
**`flipTrim` only flips the flag** — `flipTrim:true` changed the read-back and nothing else. What
`flip_trim` would change *geometrically* is therefore still unestablished; see the escalation table
below.

`flip_trim`'s default `false` is observed, not assumed: it was not passed and read `false`.

**Worked snippet.** One `nurbs.json` fragment carrying all four kinds. Every id is consumed
(G-44), every parent is declared earlier, and the counts satisfy G-50:

```json
"sections": [
  { "id": "SEC-010", "name": "Rail_South",       "points_cm": [[0,0,0],    [600,0,0],    [1200,0,0]] },
  { "id": "SEC-011", "name": "Rail_North",       "points_cm": [[0,400,0],  [600,400,0],  [1200,400,0]] },
  { "id": "SEC-012", "name": "Ramp_Rib_0",       "points_cm": [[0,0,0],    [0,400,0]] },
  { "id": "SEC-013", "name": "Ramp_Rib_1",       "points_cm": [[600,0,0],  [600,400,0]] },
  { "id": "SEC-014", "name": "Ramp_Rib_2",       "points_cm": [[1200,0,0], [1200,400,0]] },
  { "id": "SEC-015", "name": "Rooflight_Profile", "points_cm": [[0,0,0], [200,0,0], [200,200,0], [0,200,0], [0,0,0]] }
],
"surfaces": [
  { "id": "SUR-010", "name": "Ramp_Sweep",
    "kind": "rail_sweep",
    "rail_section_ids": ["SEC-010"],
    "section_ids": ["SEC-012", "SEC-013", "SEC-014"] },
  { "id": "SUR-011", "name": "Ramp_Deck",
    "kind": "two_rail_sweep",
    "rail_section_ids": ["SEC-010", "SEC-011"],
    "section_ids": ["SEC-012", "SEC-013", "SEC-014"] },
  { "id": "SUR-012", "name": "Soffit_Transition",
    "kind": "blend",
    "parent1_ref": "SUR-001", "edge1": 4,
    "parent2_ref": "SUR-002", "edge2": 4 },
  { "id": "SUR-013", "name": "Rooflight_Projection",
    "kind": "trim",
    "surface_ref": "SUR-001",
    "trim_section_ids": ["SEC-015"],
    "p_vec": [0, 0, -1], "seed": [0.5, 0.5] }
]
```

Each rib starts on `Rail_South` and ends on `Rail_North`, so every cross-section meets both rails at
**zero** distance — the shape `G-51` exists to demand. Move one rib 20 cm off its rail and the same
spec is a FAIL at lint rather than a surface that vanishes at commit. `SEC-015` closes by repeating its
first point as its last — see §8.2.8 for why that is the only closure expression available.

`SUR-012` states **no** tension and `SUR-013` states **no** `flip_trim`, and that is the recommended
style: absent means `0.0`, `0.0` and `false` respectively, and `0.0` is the straight transition
between the two selected edges rather than an outward bulge. `seed` is stated explicitly because it is
domain-sensitive (§8.2.8 row 7) and its default is only correct against a `[0,1]` parent. Note also
what `SUR-013` says by not saying anything else: a `trim` is the projected profile `SEC-015` and
**not** an aperture in `SUR-001`.

#### 8.2.8 What a spec may not encode — emission and read-back constraints

Eight consequences of the P4b transcripts. Each one **removes** an expressive option from
`nurbs.json`; none of them is a style note.

| # | Constraint | Transcript | Consequence for a spec |
|---|---|---|---|
| 1 | **Commit before read.** Relational properties are readable only on the committed sub-object | unattached `NURBS1RailSweepSurface`: `rail`/`railID`/`parallel`/`numCurves`/`axisTM`/`parent*`/`distance` all error; after `appendObject` + `NURBSNode`: `rail=0 parallel=true numCurves=3`, `railID` readable but of unestablished printed form (§8.2.6) | A dependent surface's relations are unverifiable until the emitted `.ms` has run. No lint can check them — which is exactly why `G-50`…`G-53` are static and **`G-54` is a build-time census** |
| 2 | **An unmet relation is silently dropped** | sweep with no rail → `numObjects=7`, **no `NURBSSurface` at all**; same sweep with `rail:` → `numObjects=14`, surface at index 14 | No error, no warning, no surface. The build completes and the node appears, so only a **pre-flight** (`G-51`) and a **post-commit census** (`G-54`) can catch it |
| 3 | **Construction proves nothing** | `NURBS1RailSweepSurface totalBogusName: 1` constructs fine; only a type mismatch discriminates (`rail: "zzz"` errors, `totalBogusName: "zzz"` is swallowed) | The keyword set is fixed by §8.2.7, not discovered by the builder's return value. A silent keyword typo is invisible to every check except `G-54` |
| 4 | **Sub-object indices are not knowable** | a 5 × 3 `point_grid` yields 15 `NURBSPoint` sub-objects, *then* the surface (index 16) | §8.2.5's rule: bind each index to a variable immediately after its append (`local idx = nset.numObjects`) and use the variable. **No literal sub-object index in emitted MAXScript** — it is wrong the moment a `thickness_cm` shell inserts another surface. Extended from an index to a **pointer**: `parent1ID:"2276505581808P"` → `Unable to convert: … to type: IntegerPtr`, and `parent1ID:12345` → **`EXCEPTION_ACCESS_VIOLATION`, a hard process crash**. A parent slot takes a variable bound from a committed sub-object (§8.2.7), enforced as `G-56` |
| 5 | **Read-back ≠ what was passed** | `parent:`/`rail:`/`rail1:` → `0`; `railID` → **not the index** — an `IntegerPtr` printed `<decimal>P` (`0P` on a 1-rail sweep, a full pointer on a 2-rail one; **never parse or compare it**), `pVec [0,0,-1]` → `[0,0,1]` | QA asserts `trim` / `seed` / `parent*`, never a round-trip of those three. And no spec key exists to carry a read-back id, so nothing may be written in the expectation of reading it. The **exceptions** are the relational values that do round-trip: `edge1` / `edge2` / `tension1` / `tension2` read back exactly as set across all 16 edge combinations, and `seed` / `trim` / `flipTrim` read back as passed (§8.2.7) — assert those |
| 6 | **"The design surface" is positional** | a sweep or offset derivative reads the **first** `NURBSSurface`; a `NURBSBlendSurface` is the **last** | §8.2.5's first-surface rule generalises to *resolve by superclass and confirm the candidate carries the relational properties just set*. No spec may name an index, and no `blend` may be assumed to sit where a sweep does |
| 7 | **Sweep domain is `[0,1]`; `point_grid` is chord-length** | both sweeps: `u=[0,1] v=[0,1]`; point grid: `u=[0,434.555] v=[0,307.439]` | `trim.seed` is written in the **parent's own** domain, so `[0.5,0.5]` is correct against a `[0,1]` parent and meaningless against a chord-length one. *Inference, not transcript* — the only `seed` read-back ran on a plane |
| 8 | **`trim` projects; it does not cut** | `trim:true` adds an untrimmed `NURBSCVSurface` **copy of the parent** to the relation's set — a profile spanning the whole vault width, which a real trim would have split in two, gave a **byte-identical** result (`nObj=7`, one surface, `Y 0…900`, `numCVs [9,4]`). `trim:false` adds **no surface at all** | The `trim` kind is **projection only**, so there is no aperture, no opening cut and no way to express one: a cut needs a Boolean modifier or a surface split, outside the NURBS stage. The emitted MAXScript therefore uses **`trim:false`**, which is what keeps the relation's node free of a **duplicate parent shell** and makes its `G-54` expectation **0 `NURBSSurface`** |

**A rail or trim profile closes itself.** §8.2.1 forbids a `closed` key, and no dependent kind takes
`closed_sections`, so closure is expressed in the row itself: a profile is closed when its last point
repeats its first. That is the seam-willing route already exercised by the library's closed-curve path
(`makePointCurve`, P1-b bug 4). A rail is an open row — three points along a line in the snippet above.

**Gaps escalated at this revision, not filled by invention.** Each is genuinely unspecified; the rule
is *escalate, do not fake a value*, and a key or invariant that does not exist yet is added here
first per §12.

**Closed at P4b round 2 by executed transcripts, and therefore no longer gaps:** the `tension1` /
`tension2` range and default (now `0.0`, range `0.0 … 1.0`, G-55 — §8.2.7); the `edge1` / `edge2`
mapping, where all 16 combinations now build, measure and read back exactly as set (§8.2.7); and
"projected without cutting", which is no longer undecided because `trim` **never** cuts (§8.2.8 row 8).

| Gap | State | Escalation |
|---|---|---|
| `parallel: false` — what it does geometrically | **unspecified.** Only `true` round-trips; no transcript varies it | A project that needs `false` must probe it with a known-positive control before the key's meaning is documented here |
| `flip_trim: true` — what it does geometrically | **flag only.** Executed: `flipTrim:true` changed the read-back flag and nothing else, on one relation | The geometric effect, if any, is unestablished. A project that relies on it must measure a bbox difference before relying on it |
| The `edge1` / `edge2` geometric hazard — coincident edges give a zero-area surface, a same-axis same-side pair bulges outward (§8.2.7) | **not expressible as a `G-` row.** §9 predicates run over the JSON, and the parents' committed edges are not in the file; `G-52` can only police `1..4` | A real check needs the parents' geometry, i.e. 3ds Max, i.e. it belongs to `G-54`'s census rather than to a lint. Until then this is a reviewer's rule and it is stated as one |
| Trim-profile closure | **expressible, unchecked.** G-50 counts profiles (≥ 1) and does not test that a profile closes | A `closed` assertion belongs in a `G-` row, not in prose; it is not added here because the authoritative invariant list for this revision does not contain it |
| `parent2` for a `trim` | **unspecified.** The emission names only one parent, and the transcripts cannot tell `parent1` from `parent2` (both read `0`) | The builder must not guess. If a second parent surface is ever needed, a second key is added to §8.2.7 first (§12 step 1) |
| "Declared earlier" for `trim.surface_ref` | **convention, not invariant.** G-52 enforces it for `blend`'s parents; G-50 checks only that `trim` names a surface | A `G-` row covering `surface_ref` ordering belongs to the next revision of §9.7 |

### 8.3 `facade_grids.json` (P5) — **defined**

> **What changed from the reserved sketch.** The sketch promised `axes` as "named horizontal and
> vertical axis lines with offsets from the facade origin" and `panels` carrying
> `width_cm` / `height_cm` / `kind`. Four decisions changed the shape:
>
> - **Offsets live only on `axes[]`, and are never duplicated.** `facades[].bay_offsets_cm` and
>   `bay_centre_cm` are the two exceptions and they are **derived cumulative sums of `bay_width_cm`**,
>   not a second copy of anything: a duplicated offset is a second number to drift, and `G-32`
>   recomputes every derived value anyway. A panel states its rectangle in `u_min_cm` … `v_max_cm`
>   and names the axes that bracket it; it does not restate their positions.
> - **`axes[]` gained a mandatory `level_index`.** A facade's vertical division is **per storey** —
>   `LVL-00` is 420 cm high and `LVL-01` is 400 — so an axis with no storey is meaningless, and one
>   storey's `level_base` would be indistinguishable from another's. The sketch's flat axis list
>   could not have expressed that, which is why the axis list moved inside
>   `facades[].levels[].u_axis_ids` / `v_axis_ids` as well as existing on `axes[]`.
> - **`panel_types[]` is data, not a fixed enum**, so a project declares only the kinds it uses. The
>   sketch's reserved vocabulary of six names survives as the **ceiling**, and `G-63` holds every
>   declared kind inside it — the ceiling is a bound, not a checklist.
> - **`panels[]` carries `bay_index`, `opening_ref`, `host_ref`, `full_height` and `centre_cm`**, so a
>   panel is placeable without recomputing anything downstream. The sketch's `axis_u` / `axis_v`
>   pair became `u_axis_min` / `u_axis_max` / `v_axis_min` / `v_axis_max`, because a cell is
>   bracketed by *two* axes per family, not one.

| Key | Purpose |
|---|---|
| `tolerances` | copied verbatim from `dimensions.json`. A builder may not widen them |
| `origin_inputs` | dotted paths in `dimensions.json` and `massing.json` that this file read |
| `origins` | flat provenance map, same shape and rules as §5.2, covering this file's value tree |
| `facades[]` | one entry per facade: the run geometry, the derived bay offsets, and one `levels[]` grid per storey |
| `axes[]` | every horizontal and vertical division line, each with the one offset that defines it |
| `panels[]` | the partition — one rectangle per grid cell, kinded, with its world centre |
| `panel_types[]` | the panel kinds this project declared, with the flags and the role each carries |

`spec` is `"facade_grids"` and `source.kind` is `"derived"`, with `source.reference` naming
`dimensions.json`, `massing.json` and this file's builder in the style `massing.json` uses.

#### 8.3.1 `facades[]`

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | in `dimensions.facades[].id`; unique; ascending in `dimensions` order | facade identity | — |
| `name` | string | yes | — | `== dimensions.facades[].name`; no `-` | label | — |
| `direction_deg` | float | yes | deg | `== dimensions` exactly | **facing label — never a rotation** (§8.3.6) | — |
| `start_corner_cm` | array | yes | cm | `== dimensions`, 2 finite numbers | run start, world XY | — |
| `end_corner_cm` | array | yes | cm | `== dimensions`, 2 finite numbers | run end, world XY | — |
| `length_cm` | float | yes | cm | `== dimensions`, tol `linear_cm`; `> 0` | run length | — |
| `bay_count` | int | yes | — | `== dimensions`; `== len(bay_width_cm)` | bays on this run | — |
| `bay_width_cm` | array | yes | cm | `== dimensions`; each `300 … 1200`; every bay `> 0` | bay widths | — |
| `bay_offsets_cm` | array | yes | cm | length `bay_count + 1`; **derived** cumulative sum; `[0] == 0`; `[-1] == length_cm` tol | bay boundaries | — |
| `bay_centre_cm` | array | yes | cm | length `bay_count`; **derived** `bay_offsets_cm[i] + bay_width_cm[i] / 2` | bay midpoints | — |
| `run_angle_deg` | float | yes | deg | **derived** `atan2(end.y - start.y, end.x - start.x)` in `(-180, 180]`, tol `angle_deg` | the rotation every panel on this facade uses | — |
| `levels[]` | array | yes | — | one entry per gridded level, ascending `level_index` | per-level grid | — |

`facades[].levels[]`:

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `level_index` | int | yes | — | in `dimensions.levels[].index` | storey | — |
| `elevation_cm` | float | yes | cm | `== dimensions.levels[i].elevation_cm` tol | storey floor | — |
| `height_cm` | float | yes | cm | `== dimensions.levels[i].height_cm` tol | storey height | — |
| `u_axis_ids` | array | yes | — | all `u` axes of this facade at this level, ascending by offset; first offset `0`, last `length_cm` | the shared horizontal division | — |
| `v_axis_ids` | array | yes | — | **every** `v` axis at this facade and level, ordered by `(bay_index, offset)`; each bay's own slice ascends from `0` to `height_cm` | the per-bay vertical divisions | — |

`run_angle_deg` exists because `direction_deg` cannot be used. In the worked example `F-S` runs
`[0, 0] → [1800, 0]`, i.e. along **+X**, and carries `direction_deg = 180.0`; `F-N` runs
`[0, 900] → [1800, 900]`, also **+X**, and carries `direction_deg = 0.0`. Two facades with the same
run direction carry different facings, so any rotation derived from `direction_deg` is wrong for at
least one of them. `direction_deg` is copied verbatim and used for nothing else.

#### 8.3.2 `axes[]`

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^AX-\d{3}$`, unique, ascending | axis identity | — |
| `facade` | string | yes | — | an id in `facades[]` | owning facade | — |
| `level_index` | int | yes | — | a `levels[].level_index` of that facade | owning storey | — |
| `bay_index` | int or `null` | yes | — | **`null` for `family == "u"`**, a real bay index for `family == "v"` | a horizontal line runs the whole facade; a spandrel line belongs to one bay's elevation | — |
| `family` | string | yes | — | `u` \| `v` | along the run, or up the storey | — |
| `kind` | string | yes | — | `bay` \| `opening_edge` \| `level_base` \| `level_top` | what created it | — |
| `offset_cm` | float | yes | cm | `u`: `0 … length_cm` of its facade. `v`: `0 … height_cm` of its level | position | — |

**`offset_cm` is the only place a division position is stated.** `kind` records provenance rather
than geometry — a `bay` axis exists because of the structural grid, an `opening_edge` because of an
opening, a `level_base` / `level_top` because the storey has to be closed — and it is what lets a
reviewer see why a line is in the grid at all.

**Why `v` axes are per bay and `u` axes are not** — the correction that arrived after the first
generated grid was read. An earlier revision made the vertical division the **union of every
opening's sill and head across the whole facade at that level**, on the reasoning that a curtain
wall's transom lines run continuously. It does — but the consequence nobody measured is that the
union also imposes every bay's head line on **every other bay**. `OP-G-02`, an entrance with
`head_cm = 260`, therefore put a horizontal division at 260 across a facade whose windows run
`sill 90 → head 270`, and produced `PNL-024`: a `punched_window` of `180 × 10 cm` — a 10 cm ribbon
of glass 10 cm below a window head, because a different bay's door ended there.

Per-bay v axes fix it at the root: **an opening's own sill and head are its only vertical
divisions, so every opening is realised by exactly one panel**, and the partition stays exact
because each bay tiles its own rectangle. The cost is that transom lines are continuous *within* a
bay rather than across the run; that is the correct trade, and it is recorded here because the
superseded rule looked defensible and produced glass slivers. A **bay with no opening contributes
exactly its `level_base` and `level_top`** and is therefore one whole `blank` panel — the correct
reading of "no opening declared here", not an elevation divided by lines that belong to other bays.

#### 8.3.3 `panels[]`

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^PNL-\d{3}$`, unique, ascending | panel identity | — |
| `facade` | string | yes | — | an id in `facades[]` | owning facade | — |
| `level_index` | int | yes | — | a `levels[].level_index` of that facade | owning storey | — |
| `kind` | string | yes | — | in `panel_types[].kind` | what it is | — |
| `u_min_cm` / `u_max_cm` | float | yes | cm | `u_min < u_max`; both within `0 … length_cm` | run extent | — |
| `v_min_cm` / `v_max_cm` | float | yes | cm | `v_min < v_max`; both within `0 … height_cm` | storey extent, from the level floor | — |
| `width_cm` | float | yes | cm | **derived** `u_max - u_min` tol; `> 0` | panel width | — |
| `height_cm` | float | yes | cm | **derived** `v_max - v_min` tol; `> 0` | panel height | — |
| `u_axis_min` / `u_axis_max` | string | yes | — | two `axes[]` ids, `family == "u"`, same facade and level, `offset_min ≤ offset_max` | bracketing horizontal axes | — |
| `v_axis_min` / `v_axis_max` | string | yes | — | two `axes[]` ids, `family == "v"`, same facade and level | bracketing vertical axes | — |
| `bay_index` | int | yes | — | the bay whose range contains the `u` midpoint | which structural bay it sits in | — |
| `full_height` | bool | yes | — | **derived**: `true` iff `v_min_cm == 0` and `v_max_cm == height_cm` of its level | this panel spans its bay's whole storey height, so the v grid does not cut it | — |
| `opening_ref` | string or `null` | yes | — | `null`, or a `dimensions.openings[].id` with the same `facade`, `level_index`, `bay_index` | the opening this panel realises | — |
| `host_ref` | string or `null` | yes | — | `null`, or an `massing.elements[].id` | host solid to cut an opening into | — |
| `centre_cm` | array | yes | cm | 3 numbers; **derived** (§8.3.5 step 12) | world XYZ of the panel centre on the facade plane | — |
| `layer` | string | yes | — | always `05_FACADE` | target layer | — |

`layer` is **data** for the reason §8.1.3 gives: it is `05_FACADE` from §8.1.4's closed vocabulary, and
a later stage applies it. No builder in this pipeline emits layer code.

**`bay_index` on a panel is load-bearing, not decorative.** It selects which slice of
`facades[].levels[].v_axis_ids` the panel's `v_min_cm` / `v_max_cm` are measured against, it is the
tiling unit of `G-61`, and it is one third of the identity an `opening_ref` must match. A panel
whose `bay_index` disagreed with its `v` axes would look correct in isolation and break the
partition.

#### 8.3.4 `panel_types[]`

The vocabulary this file's panels may use. It is **data**, not a fixed enum, so a project declares
only the kinds it uses — while the six names below remain the **ceiling**, and `G-63` holds every
declared kind inside it.

| Key | Type | Req | Meaning |
|---|---|---|---|
| `kind` | string | yes | one of `vision`, `spandrel`, `mullion`, `transom`, `punched_window`, `blank` |
| `glazed` | bool | yes | the panel is a light-transmitting opening |
| `frame_member` | bool | yes | the panel is a structural frame element of the curtain wall |
| `material_role` | string | yes | `glazing` \| `opaque` \| `frame` — **a role only, never a material class** |
| `opening_types` | array | yes | the `dimensions.json` §5.11 `openings[].type` values this kind may host; `[]` when none |

`glazed`, `frame_member` and `material_role` are mutually constrained and `G-63` enforces it:
`glazed` ⇒ `material_role == "glazing"`; `frame_member` ⇒ `"frame"`; neither ⇒ `"opaque"`;
`opening_types` non-empty **iff** `glazed`.

| `kind` | `glazed` | `frame_member` | `material_role` | what it is |
|---|---|---|---|---|
| `vision` | yes | no | `glazing` | a bay glazed floor-to-near-head; hosts a `curtain_wall` opening |
| `punched_window` | yes | no | `glazing` | a discrete opening inside a bay, narrower than the bay; hosts `window`, `door`, `entrance` |
| `spandrel` | no | no | `opaque` | the opaque band **at floor level** (`09` `D-WA-07` calls it a *zone*, not a strip) |
| `transom` | no | yes | `frame` | the thin horizontal frame member **above** a `curtain_wall` opening |
| `mullion` | no | yes | `frame` | the vertical frame member flanking a `curtain_wall` opening |
| `blank` | no | no | `opaque` | opaque infill: a wall return beside a punched opening, a head band above a window, or a bay with no opening at all |

**Why step 8.5's width test is `== the opening width`, and why it is not a bug.** A `spandrel` fires
for any cell whose `v_max_cm` equals an opening's sill **and** whose width equals that opening's
width. When the bay's side cells happen to be exactly as wide as the opening — `F-E` bay 1 is
`150 + 150 + 150` for a 150 cm window — all three cells of the floor-level row qualify, so the
spandrel comes out as a **continuous band across the whole bay in three pieces**. When they are not —
`F-S` bay 0 is `135 + 180 + 135` — only the middle cell qualifies, and the 135 cm sides stay `blank`
for the full storey height: full-height piers with a spandrel under the window. Both are correct
elevations and both follow from the single rule; `09` `D-WA-07` is the authority for the band, and
the measured spandrel widths in the worked example are `150 cm` × 21 and `180 cm` × 5.

#### 8.3.5 The grid is a partition, and the derivation

Computed per `(facade, level, bay)` — with the single exception of the `u` axes, which belong to the
whole run. All comparisons that merge or test use `tolerances.linear_cm` (0.5). Every step is a
formula, so `G-32` can recompute the file.

1. **Copy** the facade's identity and run geometry from `dimensions.facades[]`. Compute
   `bay_offsets_cm` = `[0]` then the running sum of `bay_width_cm`; `bay_centre_cm[i]` =
   `bay_offsets_cm[i] + bay_width_cm[i] / 2`; `run_angle_deg` = `atan2(dy, dx)` normalised to
   `(-180, 180]` (`180.0` stays `180.0`, not `-180.0`).
2. **Per level**, collect `O` = every opening with this `facade` and `level_index`, grouped by
   `bay_index`, each group sorted by `id`. G-28 forbids two openings sharing
   `(facade, level_index, bay_index)`, so a group holds at most one opening — the builder must still
   handle a group of more than one by admitting every member's sill and head as axes.
3. **u axes — one set per facade at that level.** Start from `bay_offsets_cm`, each with
   `kind: "bay"` and `bay_index: null`. For every opening in `O`, add
   `o_u0 = position_cm - width_cm / 2` and `o_u1 = position_cm + width_cm / 2`, each
   `kind: "opening_edge"` and `bay_index: null`. Sort ascending and **merge any two within
   `linear_cm`**, keeping the smaller and dropping the other. G-27 already guarantees both land
   inside the bay.
4. **v axes — one set per `(bay, level)`.** For each bay `b` in `0 … bay_count - 1`, ascending:
   start from `0` (`kind: "level_base"`) and the level's `height_cm` (`kind: "level_top"`), both with
   `bay_index: b`; then add the `sill_cm` and `head_cm` of every opening in that bay's group
   (`kind: "opening_edge"`). Sort ascending and merge within `linear_cm`, then **assert** `[0] == 0`
   and `[-1] == height_cm` within tolerance. **A bay with no opening gets exactly two v axes, `0`
   and `height_cm`, and is therefore one whole `blank` panel.** That is the correct reading of "no
   opening declared here" — not an elevation divided by lines that belong to other bays.
5. **u cells** = consecutive pairs of u axes. **v cells** = consecutive pairs of the bay's own v
   axes. The tiling unit is `(facade, level, bay)`.
6. For each `(u_cell, v_cell)` of that bay, set `u_mid` / `v_mid` to the cell midpoints.
7. Find the opening `o` in that bay's group whose u-range **contains** `u_mid`. At most one can —
   G-27 forbids overlap. Call it a *hit* when it exists and `v_mid` lies within
   `[o.sill_cm, o.head_cm]` within tolerance. Because the bay's own sill and head are its v axes,
   a hit cell is **always** the opening's whole rectangle: there is no second cell inside the
   opening and no cell straddling its edge.
8. **Kind**, in this order — first match wins:
   1. hit, and `o.type == "curtain_wall"` → **`vision`**
   2. hit, any other `o.type` → **`punched_window`**
   3. the cell's u-range is **adjacent to** a `curtain_wall` opening's u-range on the same bay —
      that is, one of its two u boundaries equals the opening's corresponding boundary within
      `linear_cm` — and the cell's width is `≤ 2 × D-OP-12` (`30 cm`) → **`mullion`**, and this cell
      is **not** cut by the v grid: it is emitted once per `(facade, level, bay)` spanning
      `0 … height_cm`, `full_height: true`
   4. the cell's `v_min_cm` equals some `curtain_wall` opening's `head_cm` within tolerance and the
      cell's width equals that opening's width within tolerance → **`transom`**
   5. the cell's `v_max_cm` equals some opening's `sill_cm` within tolerance and the cell's width
      equals that opening's width within tolerance → **`spandrel`**
   6. otherwise → **`blank`**
9. **The 30 cm in rule 8.3 is the one threshold in this file and it is `derived`, not chosen**: it is
   `09-defaults.md` `D-OP-12`'s curtain-wall pier width (`15 cm`, range `10 … 25`) **doubled**, i.e.
   `D-OP-12` × 2. Record `derives_from` accordingly. If a project's pier exceeds it, the pier becomes
   `blank` — a wall return, which is the correct reading of a wide pier, and no default is violated.
10. **`opening_ref`** is the hit opening's id for a hit cell, else `null`. A `mullion` and a
    `transom` carry `null`: they are frame members *of* an opening, not the opening. **Exactly one
    panel carries any given opening's id** — rule 7 guarantees it, and `G-62` asserts it.
11. **Axes bracketing**: `u_axis_min` / `u_axis_max` are the axis ids whose offsets equal the cell's
    `u_min_cm` / `u_max_cm`. For a merged `mullion`, `v_axis_min` / `v_axis_max` are the bay's
    `level_base` and `level_top` axis ids, and `v_min_cm` / `v_max_cm` are `0` / `height_cm`.
12. **`centre_cm`** = `start_corner_cm + run_unit * u_mid` in XY, where
    `run_unit = ((end.x - start.x), (end.y - start.y)) / length_cm`; Z = `elevation_cm + v_mid`.
13. **`host_ref`** is `null` unless a `massing.json` element of kind `plinth` or `parapet` has a
    `profile_cm` lying on this facade line — the only two kinds whose outline can legitimately lie
    on a facade line without being the wall behind it. No element in the example qualifies, so
    `host_ref` is `null` throughout (§8.3.6).
14. **Ids**: `AX-nnn` ascending over `(facade order, level_index, family with `u` before `v`, bay —
    `null` first, offset)`; `PNL-nnn` ascending over
    `(facade order, level_index, bay_index, v_min_cm, u_min_cm)`.

**Why the whole partition is exact.** Per `(facade, level, bay)` the u cells tile the bay's width and
the bay's own v cells tile the storey height, and the bays tile the run — so Σ panel areas per
`(facade, level, bay)` equals `bay_width_cm × height_cm`, and per `(facade, level)` equals
`length_cm × height_cm`. A merged `mullion` replaces a stack of cells with one panel of the same
total area. `G-61` asserts both area sums, that no two panels overlap in their interiors, and that
every panel is inside its bay's rectangle. That is what makes this a partition rather than a pile of
rectangles.

**What the worked example is expected to yield** — a build-time expectation, not a gate. Cells are
`(axes − 1) × (axes − 1)` per family, and the v family is **per bay**. Worked by hand for `F-S` at
`LVL-00`, whose four openings are `OP-G-01` window `180 @ 225, sill 90 head 270`, `OP-G-02`
entrance `200 @ 675, sill 0 head 260`, `OP-G-03` window `180 @ 1125, sill 90 head 270` and
`OP-G-04` curtain_wall `420 @ 1575, sill 0 head 400`:

```
u axes  13 -> 12 u cells, shared by all four bays:
   0 135 315 450 | 575 775 900 | 1035 1215 1350 | 1365 1785 1800

bay 0  v axes 0 90 270 420  (4 -> 3 cells)  -> 3 x 3 =  9 panels
bay 1  v axes 0 260 420     (3 -> 2 cells)  -> 3 x 2 =  6 panels
bay 2  v axes 0 90 270 420  (4 -> 3 cells)  -> 3 x 3 =  9 panels
bay 3  v axes 0 400 420     (3 -> 2 cells); the two 15 cm curtain-wall piers merge into
                                                   full-height mullions -> vision + transom
                                                   + 2 mullions =              4 panels
                                                              F-S / LVL-00 total  28 panels

All 8 (facade, level) groups together ~ 110 ... 130 panels.  The exact count is whatever the
builder prints; no gate assumes it.
```

`bay 1` is the case that proves the per-bay rule: `OP-G-02`'s head at `260` divides **only bay 1**,
so the 180 × 180 window in `bay 0` stays one panel instead of becoming a 180 × 170 panel plus a
180 × 10 sliver.

#### 8.3.6 What this schema may not encode

- **No MAXScript class, modifier, plugin or MCP tool name.** `kind` is geometric: a `vision` panel is
  not any renderer's glass, and a `glazed_panel` component (§8.4.3) is not a material class either.
  §12's standing rule is the reason these names are correct.
- **`material_role` is a role, not a material class.** `glazing` / `opaque` / `frame` say what a panel
  *is*, nothing more. Nothing in this file may name a material class.
  > **CORRECTED (verified 2026-10-06):** this bullet previously ended *"P7 resolves a role to a
  > material."* **P7 was cancelled by user decision on 2026-10-05** — materials are assigned **by
  > hand** by the user, and this pack does not script material assignment. The role is therefore
  > carried as data for a human, and the sentence as written promised an unbuilt resolver.
- **A rotation is never derived from `dimensions.facades[].direction_deg`.** `F-S` and `F-N` both run
  along **+X** and carry `180` and `0` respectively, so `direction_deg` is a compass-facing label and
  any rotation taken from it is wrong for at least one of the two. `run_angle_deg` is the only
  rotation source in this file, and `G-57` forbids the other route by name.
- **The standing limitation: `massing.json` has no exterior envelope element at P5.** Its
  `elements[]` carries `slab`, `column`, `core_wall`, `roof_deck` and `parapet`, and the only
  perimeter geometry is the four parapet strips at `z 820 … 910`. So **every `host_ref` in the
  worked example is `null`** — there is no solid to cut an opening into, and a punched window in the
  grid is a glazed panel in a plane, not a hole. A project that needs a punched opening cut into an
  opaque wall adds a `facade_wall` kind to `massing.json` through §12 step 1 (P3's table to change);
  this file then resolves `host_ref` to that element's id and nothing else in the schema moves.
- **An axis's `bay_index` decides whether a division is shared or private, and it is required.** A
  `u` axis belongs to the whole run and carries `null`; a `v` axis belongs to one bay's elevation and
  carries a real index. §8.3.2 gives why, and the short form is that a shared v grid imposes every
  bay's head line on every other bay.
- **Revision 2, 2026-10-05 — corrected by measurement, not by preference.** The first generated grid
  was read and it carried `PNL-024`: a `punched_window` of **180 × 10 cm**, a 10 cm ribbon of glass
  sitting 10 cm below a window head. The cause was revision 1's facade-wide v grid: `OP-G-02`, an
  entrance in one bay with `head_cm = 260`, put a horizontal division at 260 through a window in a
  *different* bay running `sill 90 → head 270`. Revision 1 also stated rule 8.3 self-contradictorily
  (a cell had to be simultaneously outside every opening's u-range and inside a `curtain_wall`
  opening's u-range; the intended reading was **flanking**, which is what the first build produced),
  and its worked arithmetic multiplied axis *counts* instead of cell counts. All three are fixed
  here: the v grid is per bay, rule 8.3 says *adjacent to*, and §8.3.5 is worked in cells. **A rule
  in this section that has not survived being executed on a generated file is provisional**, which
  is why the corrections are recorded here rather than folded in silently.

### 8.4 `components_registry.json` (P5) — **defined**

> **What changed from the reserved sketch.** Two decisions, both about what an entry *is*:
>
> - **One entry per distinct `(kind, width, height)` class of panel — not one per panel.** The sketch
>   read as a catalogue of blocks with no stated cardinality; P5 fixes it at the class. This is the
>   entire reason the file exists: the grid is expected to hold **110-odd panels** and those resolve
>   to a **few dozen** blocks, so the registry is what turns a partition into instances. A registry
>   with one entry per panel would be a copy of `facade_grids.json` with worse ids.
> - **The dependency is one-way.** `components_registry.json` reads `facade_grids.json` and
>   `dimensions.json`; **a panel never names a component.** The join runs registry → grid, so there
>   is no cycle, `G-31` stays a single pass, and `G-68` can ask "does every panel have a block?" as a
>   total-join question rather than as a mutual-consistency puzzle. The sketch's `families` row —
>   "which components are interchangeable in one slot, and which are unique" — survives as the
>   resolution index, but *uniqueness is now mandatory* rather than a per-family choice:
>   `substitution` is the single value `size_matched`.

Envelope in G-1 order, then `tolerances` (copied from `dimensions.json`; a builder may not widen
them) · `origin_inputs` · `origins` (per §5.2) · `defaults` · `component_types` · `components` ·
`families`. `spec` is `"components_registry"`, `source.kind` is `"derived"`.

| Key | Purpose |
|---|---|
| `tolerances` | copied verbatim from `dimensions.json`. A builder may not widen them |
| `origin_inputs` | dotted paths in `facade_grids.json` and `dimensions.json` that this file read |
| `origins` | flat provenance map, same shape and rules as §5.2, covering this file's value tree |
| `defaults` | the two assumed numbers §8.4.1 exists to declare — and the only invented values in P5 |
| `component_types[]` | the component vocabulary, with the two flags `G-67` matches panel kinds against |
| `components[]` | one entry per distinct `(kind, width, height)` class of panel, with an ordered parameter list |
| `families[]` | the resolution index: every component serving one panel kind, and how a slot picks among them |

#### 8.4.1 `defaults` — the only two invented numbers in P5

| Key | Type | Req | Units | Range | Meaning | Provenance |
|---|---|---|---|---|---|---|
| `panel_thickness_cm` | float | yes | cm | `2 … 8` (`09` `D-CL-05`) | modelled depth of every facade panel block | **assumed**, `A-023` |
| `joint_width_cm` | float | yes | cm | `1 … 4` (`09` `D-FM-10`) | visible gap between adjacent panels; the world table carries it so P6 insets each panel by half | **assumed**, `A-024` |

**These two numbers are the only invented values in P5**, and both are **assumed** rather than
derived. They are not new: each already exists in `09-defaults.md` as a **reference-only convention
with a declared range** — `D-CL-05` for cladding/panel depth and `D-FM-10` for frame joint width —
so the pipeline is not inventing a number, it is *adopting* one inside a documented band and
recording the adoption in the ledger, as `A-023` and `A-024`. `assumed` means exactly what §5.2 says
it means: the input was silent and the pipeline chose.

**Everything else in both P5 files recomputes from `dimensions.json`.** That is a sharp bound, not a
description: an `assumed` or a `given` value anywhere else in `facade_grids.json` or
`components_registry.json` is a **defect**, and `G-64` fails it by name, because `dimensions.json`
and `massing.json` already resolved every provenance question those values could raise. A P5 file
that cannot say where a number came from is a number nobody chose.

#### 8.4.2 `component_types[]`

| Key | Type | Req | Meaning |
|---|---|---|---|
| `kind` | string | yes | one of `glazed_panel`, `opaque_panel`, `frame_member`, `entrance_door` |
| `glazed` | bool | yes | carries a light-transmitting infill |
| `frame_member` | bool | yes | is a structural frame element |

**A component `kind` is derived from the panel, never chosen.** A project's registry declares the
kinds it uses, and every component's kind is read off the panels it serves:

| panel `kind` | panel hosts a `door` / `entrance` opening | component `kind` |
|---|---|---|
| `vision`, `punched_window` | no | `glazed_panel` |
| `vision`, `punched_window` | yes | `entrance_door` |
| `spandrel`, `blank` | — | `opaque_panel` |
| `mullion`, `transom` | — | `frame_member` |

#### 8.4.3 `components[]`

One entry per **distinct `(kind, width, height)` class** of panel — not one per panel. This is the
whole point: the grid's 110-odd panels resolve to a few dozen blocks.

| Key | Type | Req | Units | Constraint | Meaning | Default |
|---|---|---|---|---|---|---|
| `id` | string | yes | — | `^CMP-\d{3}$`, unique, ascending | component identity | — |
| `name` | string | yes | — | unique in file; no `-` | node name in the scene | — |
| `kind` | string | yes | — | in `component_types[].kind` | what it is | — |
| `size_cm` | array | yes | cm | 3 numbers `> 0`; `[0] == width_cm`, `[1] == height_cm` of the panels it serves, `[2] == defaults.panel_thickness_cm` | block size | — |
| `parameters` | array | yes | — | the ordered list of **exactly** `width_cm`, `height_cm`, `thickness_cm`, `joint_width_cm`, in that order, each `{name, source, value, units}` | stable parameter order for a builder | — |
| `serves_panel_kinds` | array | yes | — | ≥ 1 entries, each a `panel_types[].kind` of `facade_grids.json`, flags compatible with `kind` (`G-67`) | which panels it fits | — |
| `variants` | array | yes | — | `^VAR-\d{3}$`, unique within the component; `overrides` non-empty with keys from the four parameter names | construction options | — |
| `layer` | string | yes | — | always `05_FACADE` | target layer | — |

`parameters[].source` ∈ `size_cm` (`width_cm`, `height_cm`) \| `defaults` (`thickness_cm`,
`joint_width_cm`) — so the four parameters resolve to two places and the order is fixed, which is
what lets a builder generate a stable parameter order without reading the array's contents to
decide what is what. `name` carries no `-` for rule N1's reason: a hyphen in a node name reads as
subtraction in emitted script (§8.2.2).

#### 8.4.4 `families[]`

A family is **the resolution index P6 needs**: every component serving one panel kind, so P6 picks the
member whose `size_cm` matches the slot.

| Key | Type | Req | Meaning |
|---|---|---|---|
| `id` | string | yes | `^FAM-\d{3}$`, unique, ascending |
| `name` | string | yes | hyphen-free |
| `panel_kinds` | array | yes | ≥ 1 `panel_types[].kind`; every declared kind belongs to exactly one family |
| `component_ids` | array | yes | ≥ 1; **every component appears in exactly one family** |
| `substitution` | string | yes | `size_matched` — the member whose `size_cm` matches within `linear_cm` is used |

Both partitions are exact: every declared panel kind in one family, every component in one family.
A family with a member for every `(kind, width, height)` class of the kinds it serves is what makes
the join in §8.4.5 total rather than best-effort.

#### 8.4.5 The join, and why it is total

P6 walks three steps, and each is a lookup rather than a search:

1. Take the panel's `kind`.
2. Resolve the **family** whose `panel_kinds` contains that kind. Exactly one family, by §8.4.4's
   partition.
3. Within it, take the **component** whose `size_cm` matches the panel's `width_cm` / `height_cm`
   within `tolerances.linear_cm`.

**`G-68` is what makes the join total**, and it is the reason the registry is not a nice-to-have: it
asserts that **every** panel in `facade_grids.json` has at least one component satisfying both the
size match and the `serves_panel_kinds` membership, and that all matching components belong to
**one** family. **When it breaks it names the first ten offending panel ids and the count** — because
"a panel size has no block" is the failure mode that otherwise produces a scene that is *quietly*
wrong: the partition is complete, every check on it passes, and one panel simply is not there. The
rule is cross-file, so it reports SKIP with its reason when `components_registry.json` is absent
rather than pretending the join held.

### 8.5 `assembly.json` (P6) — **defined**

The **last derived file** in the chain. It resolves `components_registry.json` +
`world_table.csv` + `massing.json` + `dimensions.json` into instructions a builder can
execute, and it is the only file that carries a `scatter` table. `scripts/place_components.py`
emits **both** `assembly.json` and `assembly.ms` from those four inputs, so the two artefacts
cannot describe different scenes.

This is the one file in the chain whose `source.reference` names a **non-JSON** input
(`world_table.csv`). That is not an exception to §3.1's derived-reference rule — the reference
still names three spec files, which is what `G-6` resolves — it is a statement about what
"derived" means here: a *table* produced by P5, not a spec.

#### 8.5.1 Top level

| Key | Type | Req | Notes |
|---|---|---|---|
| `schema_version` | string | yes | semver; major must match §2 |
| `spec` | string | yes | `== "assembly"` |
| `project` | string | yes | the same id as the other seven files (G-31) |
| `units` | string | yes | `cm` / `deg` |
| `source` | object | yes | `kind: "derived"`, naming all four inputs |
| `status` | string | yes | `draft` \| `locked` \| `superseded` |
| `tolerances` | object | yes | inherited **verbatim** from `dimensions.json` (G-33) |
| `origin_inputs` | array | yes | the dotted paths read in `dimensions.json`, `massing.json` and `components_registry.json`. `world_table.csv` contributes none — a placement's traceability to it is its own `source_row`, and G-72 asserts that join in **both** directions, which is a stronger claim than a path list |
| `origins` | object | yes | one entry per leaf, collapsed per row (§5.2). Every value is `derived`: this file computes nothing it did not read, so an `assumed` here would be a silent default |
| `defaults` | object | yes | §8.5.5 |
| `layer_map` | object | yes | §8.5.6 — **data only** |
| `placements[]` | array | yes | §8.5.2 |
| `opening_cuts[]` | array | yes | §8.5.3 |
| `wall_cells[]` | array | yes | §8.5.8 — **the solids the walls are built from** |
| `scatter[]` | array | yes | §8.5.4 |

#### 8.5.2 `placements[]` — one per `world_table.csv` data row

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^PLC-\d{3}$`, unique, ascending |
| `component_id` | string | yes | resolves to `components_registry.json` `components[].id` |
| `source_row` | int | yes | the **1-based data row** of `world_table.csv`, header excluded |
| `node_name` | string | yes | unique across all four tables; the id with dashes replaced (`11` §3.1 N1, N4) |
| `position_cm` | array | yes | `[x, y, z]`, **verbatim** from the CSV row |
| `rot_z_deg` | float | yes | the CSV `rot_z_deg`, which P5 proved equals `run_angle_deg = atan2(dy, dx)` — never `dimensions.facades[].direction_deg`. `F-S` and `F-N` both run along +X and carry `180` and `0` |
| `instance` | bool | yes | always `true` |
| `layer` | string | yes | the `layer_map` entry for the component's role |

`source_row` exists so the count can be asserted **in both directions** against the table,
which is what G-72 does. It is the one field in this schema that reaches back past the JSON.

#### 8.5.3 `opening_cuts[]` — one per `dimensions.json` opening

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^CUT-\d{3}$`, unique, ascending |
| `opening_id` | string | yes | resolves to `dimensions.json` `openings[].id` |
| `node_name` | string | yes | the **declared** cut's name (`CUT-001` → `CUT_001`), unique across all four tables (§8.5.2). Carried so the `G-74` name partition stays total. **No node is created for it** — the wall cells (§8.5.8) are the nodes; grep the emitted `assembly.ms` for `CUT_` and expect **0** |
| `host_ref` | string | yes | a **`facade_wall`** element id in `massing.json` — **never `null`** |
| `facade` | string | yes | the opening's facade |
| `level_index` | int | yes | the opening's level |
| `bay_index` | int | yes | the opening's bay |
| `u_range_cm` | array | yes | `[u0, u1]` **along the facade run**, `u0 < u1` |
| `v_range_cm` | array | yes | `[sill_cm, head_cm]` from the opening |
| `depth_cm` | float | yes | the **declared** penetration depth of the opening, ≥ the host wall thickness, within `linear_cm`. **Retained for traceability of the declared opening, not consumed as geometry** — nothing is cut to this depth, because nothing is cut: the wall is built as cells that pass clean through (§8.5.8) |
| `kind` | string | yes | `difference` — the only legal value |

**`host_ref` is never `null` here, and that is the whole reason P6 exists.** `massing.json`
has exactly one `facade_wall` per `(facades[i].id, levels[j].index)` pair (§9.6, G-38 clause
2), so the envelope is total and every one of the sixteen openings has a wall it is cut out
of in the data — the declaration the wall's cells are computed from (§8.5.8). A cut with a
null host is a hole in the envelope, not a legitimate absence, and the rule
that forbids it is G-76's first clause.

**`u_range_cm` and `v_range_cm` are both facade-local, and the frame is stated here because
it is the one genuinely new computation in P6.**

```
u0 = opening.position_cm − opening.width_cm / 2
u1 = opening.position_cm + opening.width_cm / 2
v  = [ opening.sill_cm, opening.head_cm ]
```

`position_cm` is already measured from the bay's own origin, so `u` needs no facade offset —
but the **host wall's band starts at `start_corner_cm`**, so the world position along the run
is `start_corner_cm + u`, and the builder converts once, when it writes the wall cells
(§8.5.8). `v` is measured **from the level base**, which is the same frame `facade_grids.json`
is written in: a host wall's own local `v` extent is `[0, level.height_cm]`, so a level-1
opening whose head is 270 cm sits inside its wall without the 420 cm elevation that the *world*
frame would demand. Keeping the spec in the grid's frame and doing the one conversion in the
builder is what stops the two frames mixing — which is how P5's glass-sliver defect happened.

#### 8.5.4 `scatter[]`

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^SCT-\d{3}$`, unique, ascending |
| `node_name` | string | yes | unique across all four tables (§8.5.2) |
| `target_ref` | string | yes | a `massing.json` element id — the surface instances land on |
| `model_refs` | array | yes | ≥ 1; a `components_registry.json` id **or** a `massing.json` element id |
| `seed` | int | yes | **1 … 31337**, inclusive at both ends |
| `instance_count_limit` | int | yes | > 0, and ≤ `defaults.instance_limit_guard` |
| `distribution_density_pattern` | number | yes | 0…1. **P0 recorded the typo `distributionDesityPattern` as the real MAXScript name — the spec uses the corrected spelling**, and the *builder* owns the translation |
| `scale_from` / `scale_to` | number | yes | `0 < scale_from ≤ scale_to`, unitless ratios |
| `rotation_from_deg` / `rotation_to_deg` | number | yes | `from ≤ to` |
| `collision_avoid` | bool | yes | defaults `true`; leaving it unset is how interpenetrating scatter ships |
| `layer` | string | yes | `99_DEBUG` for scatter sources |

**The seed is a fixed literal in the spec, never a draw.** That is the whole P0 determinism
claim in one sentence: a builder that generated a seed would make every rebuild a different
scene, and no amount of seed *recording* fixes that. `examples/assembly.json` ships exactly one
scatter row, targeting the **`roof_deck`** element id with a single `column` model, so the
136-panel scene is not disturbed. (`ground_pad` is not a `massing.json` element — it lives in
`site_pad` — so it cannot be a `target_ref`.)

#### 8.5.5 `defaults`

| Key | Value | Origin |
|---|---|---|
| `panel_joint_cm` | `2.0` | **derived from `components_registry.json:defaults.joint_width_cm`** (`A-024`). Not a new assumption — this is P5's value carried forward, and saying so is what keeps P6's assumed count at **one** (`A-025`, the wall thickness) |
| `instance_limit_guard` | `2000` | derived: a refusal threshold on total placements, so a corrupt CSV cannot ask Max for a million instances. Nothing geometric reads it |

A builder that re-invented `panel_joint_cm` instead of reading the registry would create a
second untracked copy of `A-024` and break the ledger bijection, which is the P5 trap.

#### 8.5.6 `layer_map` — data, and *only* data

`layer_map` is an object **keyed by layer name**, whose value is the list of *roles* that file
assigns to that layer:

```json
"layer_map": {
  "05_FACADE": ["entrance_door", "frame_member", "glazed_panel", "opaque_panel"],
  "99_DEBUG":   ["scatter_source"]
}
```

Keying by layer is deliberate: it lets G-75 say **every `layer_map` key is in the §8.1.4
vocabulary** with one comparison, and it makes a placement's layer decidable from the spec
alone — a component's role is read through its `component_id`, and exactly one layer may list
that role.

**No builder emits layer code.** This was measured, not assumed, and the result was a negative
(§11, `11-layer-standard.md` §5): `LayerManager` in Max 2026 exposes only `newLayerFromName`,
`getLayerFromName` and `getLayer`, and has no setter of any kind; `node.layer` throws
`Property is read-only: layer` for a string, an integer index and a `LayerProperties` mixin;
`3dsmax-mcp_manage_layers`' action vocabulary is exactly `{list, create, delete}`; and
`3dsmax-mcp_set_object_property` with `property=layer` emits the same read-only error while a
positive control on the same tool with `property=pos` succeeded. **Applying layers is a human
action in the Layer dialog.** `layer_map` is therefore a *record of intent*, and a builder that
tries to apply it is a build **FAIL** (G-79), not a silent no-op.

#### 8.5.7 What this schema may not encode

No `materials`, no `cameras`, no `lights`, no `export` keys in this schema. A row naming
any of them is a FAIL — which G-1 already delivers, because §4 does not declare those keys.
> **CORRECTED (verified 2026-10-06):** this paragraph previously read *"Those are P7, P8 and P9"*, which
> presented three pending stages. **All three were cancelled by user decision on 2026-10-05.**
> `materials.json`, `qa.json` and `export.json` exist only as **reserved stubs** and are **not planned
> work**; there is no `qa_check.py`, no `capture_views.py` and no `export_max.py` anywhere in the
> scripts directory. **The stage boundary is still enforced** — G-1 rejects those keys — but it is
> enforced because the pipeline does not do those things, not because a later stage will.

Every value here is a length in `cm`, an angle in `deg`, or a unitless ratio
(`scale_from` / `scale_to`). No class name, modifier, plugin or MCP tool appears anywhere in
this schema (§11, §12): a cut is `kind: "difference"`, not a Boolean modifier; a scatter is a
`scatter[]` row, not a `ChaosScatter`. **The builder owns the class names.**

#### 8.5.8 `wall_cells[]` — the solid tiling that replaced the Boolean modifier

`wall_cells[]` is one entry per **solid box the builder emits for a wall**, and it is the reason
this stage emits no modifier at all. Each entry is a rectangle in plan, a range in Z, and the
volume that rectangle × range encloses.

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^WAL-<HOST>-C<NN>$`, unique. `<HOST>` is the host element id (`EL-014`), `<NN>` a 2-digit cell index within that host |
| `node_name` | string | yes | **its own `id` with dashes replaced** — `WAL-EL-014-C01` → `WAL_EL_014_C01`. That derivation is exactly what `G-74` already demands of every name in this file (N1, N4) |
| `host_ref` | string | yes | the **`facade_wall`** element id this cell belongs to. Never `null`, for the same reason `opening_cuts[].host_ref` is never `null` (§8.5.3) |
| `plan_rect_cm` | array | yes | `[x0, y0, x1, y1]` in **world** coordinates, `x0 < x1`, `y0 < y1` |
| `z_range_cm` | array | yes | `[z0, z1]`, inside the host's own `z_range_cm` within `linear_cm` |
| `volume_cm3` | float | yes | `(x1−x0)·(y1−y0)·(z1−z0)`, and the **sum over a host** is what `G-82` asserts |

**The tiling is a column-row decomposition along the facade's run axis.** Cut at every opening's
`u` boundary, producing columns; then, inside each column, cut at the `v` boundaries of the
openings covering it, producing rows. Every boundary therefore comes from *some* opening edge, so
a column is either wholly inside one opening's `u` span or wholly outside it — which is what makes
the decomposition **exact**: no gap, no overlap, no remainder. Cells are emitted in a
**deterministic order — ascending run interval, then ascending `v`** — so the same locked inputs
give the same ids in the same sequence (S-5).

**The cross axis always takes the wall's own extent.** Every opening is passed clean through, and
that is now an asserted invariant (`G-83`) rather than an assumption: a tiling of solid cells
cannot express a partial-depth opening, so a cell that stops short of a face is a defect.

#### 8.5.8.1 Why this array **replaces** cutting

**The Boolean modifier cannot be made to cut anything in this build.** Measured against live
3ds Max 2026.3.2 on 2026-10-05, every probe batched with a bogus-name control that came back
`undefined`:

| Probe | Measured result |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs and `classOf` reads `BooleanMod`, but its paramblock is **Voxel Map's** — `voxelSize`, `toleranceFactor`, `bevelDistance`, `bevelDepth` — and `VoxelMap()` is itself `NotCreatable`. The name is shadowed in the class registry |
| `ProBoolean()` | constructs, but `superClassOf` is `GeometryClass`, not Modifier, and constructing one **leaves a node in the scene** (three orphans accumulated while probing) |
| the bridge's native `add_modifier` with `"Boolean"` | genuinely **attaches** — `node.modifiers` reads `#modifiers(Boolean:Boolean)` — and the **operand is never set**: `snapshotAsMesh` reports `verts=8 faces=12`, unchanged, for every `params` spelling tried |
| the committed modifier's own properties | `isProperty m #operation`, `#object`, `#boolobject` all **`false`**, and the control `#totalBogusProp` is also `false`, so these names genuinely do not exist |
| `getModifier 1 node` | **throws**. `node.modifiers[1]` works |

So the previous `assembly.ms` opened with `Boolean()`, **did nothing**, and its own `G-80`
census still reported success — see the `G-80` row. `wall_cells[]` is the replacement: the
opening is expressed as *absent material*, computed in the builder and emitted as ordinary
solids, which is a thing this build can be relied on to do. The class names in that table are
**prose about the builder**, not schema content — `wall_cells[]` itself is six geometric keys and
nothing else (§12).

For `pavilion-01` the array carries **52 cells over 8 hosts** — `EL-014` 11, `EL-015` 12,
`EL-016` 6, `EL-017` 7, `EL-018` / `EL-019` / `EL-020` / `EL-021` 4 each.

### 8.6 `materials.json` (P7 — **cancelled 2026-10-05, reserved stub only**)

> **CORRECTED (verified 2026-10-06):** this heading and the two below read as pending stages. They are
> not. Materials are assigned **by hand** by the user; this pack scripts no material assignment, so
> nothing reads or writes this file. The key set is documented for audit only.

| Key | Purpose |
|---|---|
| `origin_inputs` | paths read from `assembly.json` and `massing.json` |
| `renderer` | detected renderer and the one explicitly chosen, with the reason. Never assumed |
| `materials` | one entry per material: class identifier, slot map, parameters, target objects |
| `uv_rules` | mapping strategy per geometry class — NURBS-generated vs poly-modified |

### 8.7 `qa.json` (P8 — **cancelled 2026-10-05, reserved stub only**)

| Key | Purpose |
|---|---|
| `origin_inputs` | paths read from every upstream file |
| `checks` | one entry per deterministic check: `id`, `rule`, `expected`, `measured`, `tolerance`, `pass` |
| `determinism` | the scatter configuration save path and the instance count recorded on the previous build, for comparison |
| `captures` | viewport captures by architectural viewpoint |
| `verdict` | `pass` \| `fail` plus the failing check ids |

### 8.8 `export.json` (P9 — **cancelled 2026-10-05, reserved stub only**)

| Key | Purpose |
|---|---|
| `origin_inputs` | paths read from `qa.json` |
| `exports` | one entry per target: format, options, target node set, output path |
| `tessellation` | tessellation settings per geometry class, and the tolerance used |
| `delivery` | the delivery MAXScript's responsibilities and the delivery manifest |

---

## 9. Invariants

Every rule here is **mechanically checkable** from the files alone, with no 3ds Max and no rendering.
`scripts/validate_specs.py` (P2c) implements exactly this list; if a rule cannot be expressed as a
function over the parsed JSON, it does not belong here.

### 9.1 Envelope and hygiene

| Id | Title | Check |
|---|---|---|
| **G-1** | Envelope keys present, first, in order | The first six keys are exactly `schema_version`, `spec`, `project`, `units`, `source`, `status`, in that order. In `dimensions.json`, `tolerances` is seventh and `origins` precedes the value tree. |
| **G-2** | `spec` matches the filename | `spec` equals the file's base name without extension. |
| **G-3** | `schema_version` major is supported | Parses as semver. Major differs from the validator's supported major → error. Minor/patch differ → warning. |
| **G-4** | `status` is known, and only `locked` builds | `status` ∈ {`draft`, `locked`, `superseded`}. A non-`locked` file is an error for any build, a warning for a lint. |
| **G-5** | Units are cm and deg | `units.length == "cm"` and `units.angle == "deg"` on every file. |
| **G-6** | `source` is well formed | `source.kind` ∈ {`user_brief`, `drawing`, `image`, `imported`, `assumed`, `derived`}; `source.reference` non-empty; `source.recorded_at` parses as ISO-8601. `kind == "derived"` additionally requires `reference` to name a spec file that exists in the project |
| **G-7** | File hygiene | File is UTF-8 without BOM, contains no `\r`, ends with exactly one `\n`, and parses with a strict JSON reader that rejects comments, trailing commas and `NaN`/`Infinity`. |
| **G-8** | Unit suffix lint | Every key carrying a length ends `_cm`, every area ends `_m2`, every angle ends `_deg`. A key named `height`, `width`, `depth`, `thickness`, `radius`, `offset`, `spacing`, `sill`, `head`, `length`, `rise` or `run` **without** a unit suffix is an error. The envelope keys, everything under `tolerances`, and index/count keys (`*_index`, `*_indices`, `*_count`) are outside the rule — `units.length` names a unit, it is not a length. |

### 9.2 Traceability

| Id | Title | Check |
|---|---|---|
| **G-9** | `origins` covers the value tree, exactly once | Every leaf in the value tree has an `origins` entry, except the six envelope keys, everything under `tolerances`, and keys named `id`, `name`, `index` or ending in `_index` / `_indices`. Every `origins` key resolves to an existing path, and **no leaf may be covered by more than one entry**. An array-of-scalars — including a polygon ring — is one leaf, so `site.footprint_cm` is covered by one entry rather than eight. An array **element** may be collapsed to a single entry (e.g. `facades[0]`, `openings[4]`) when its leaves share one origin; where an element mixes origins — `levels[]` mixes `given` / `conflict` / `assumed` — every leaf gets its own entry. An entry on an excluded key (`building.name`) is legal and documents provenance, but is never required; an entry inside the envelope or `tolerances` is an error. |
| **G-10** | `origin` / `origin_ref` pairing | `origin` ∈ {`given`, `assumed`, `conflict`, `derived`}. `assumed` or `conflict` ⇒ `origin_ref` present, matches `^[AC]-\d{3}$`, and resolves in the ledger named by `origin`. `given` or `derived` ⇒ `origin_ref` absent or `null`. `derived` ⇒ `derives_from` non-empty and every path resolves. |
| **G-11** | Ledger ids are unique and well formed | Within each ledger file, `id` values are unique, match `^[AC]-\d{3}$`, and ascend. `A-` ids appear only in `assumptions.json`; `C-` ids only in `conflicts_resolved.json`. |
| **G-12** | Ledger entries match the spec | For every entry, `field_path` — **bare or file-qualified per §6.1.1** — resolves in the file it describes, and the entry's `value` equals that spec's value at that path (deep equality for arrays/objects). A qualified `<spec-name>` must be known **and** present in the project. |
| **G-13** | Ledger bijection | Every value with `origin` ∈ {`assumed`, `conflict`} is covered by at least one ledger entry; every entry names exactly one existing `field_path`, **bare or file-qualified per §6.1.1**, resolving in a file that exists in the project; `field_path` is unique within a ledger file, **tested on the qualified form**, so a bare path and a file-qualified one are distinct claims. A `resolved_path` may name a field inside an element whose origin is declared at element level — `openings[11].head_cm` satisfies an origin recorded as `openings[11]` — so coverage is tested by prefix in both directions, never by exact string equality. **Prefix coverage is per document**: a file-qualified path never covers, and is never covered by, a path in another file, because shared-origin coverage is a claim about one file's value tree. |
| **G-14** | Conflict entries are complete | Each has ≥ 2 `sources`, ≥ 1 `rejected`, non-empty `rules_invoked` whose ids exist in `precedence_rules`, a `resolution.chosen_value` equal to the value at `resolution.resulting_value_of`, and an `invariant_violated_if_unresolved` naming a real `G-` id. No `R7` appears in any `rules_invoked`. |
| **G-15** | Assumption entries are complete | Each has non-empty `reason`, `confidence` ∈ {`high`, `medium`, `low`}, non-empty `invalidated_by`, a `recheck_stage` in **`P3`…`P6`** (narrowed 2026-10-06 — `P7`…`P9` were cancelled and now FAIL), and a `field_path` — **bare or file-qualified per §6.1.1** — naming a spec that exists inside the project it belongs to. |

### 9.3 Dimensional geometry

| Id | Title | Check |
|---|---|---|
| **G-16** | Range compliance | Every numeric value lies within the range declared for its key in §5–§7. A key with no declared range is unbounded. |
| **G-17** | Levels ordered bottom to top | `levels` is non-empty; `levels[i].index == i`; `elevation_cm` strictly increases with `i`. |
| **G-18** | Level chaining | For `i ≥ 1`: `levels[i].elevation_cm == levels[i-1].elevation_cm + levels[i-1].height_cm`, **tolerance `tolerances.linear_cm` (0.5 cm)**. The tolerance covers float representation only — it is not permission to leave a storey height slightly wrong. |
| **G-19** | Total height equals the top of the chain | `building.total_height_cm == levels[-1].elevation_cm + levels[-1].height_cm`, tol 0.5 cm. |
| **G-20** | Overall height includes the parapet | `building.overall_height_cm == building.total_height_cm + roof.parapet_height_cm`, tol 0.5 cm. |
| **G-21** | Polygons are simple and winding is declared | Each `footprint_cm` / `core.footprint_cm` has ≥ 3 vertices, no duplicate vertices, no self-intersection, and its winding matches the sibling `*_ccw` flag. |
| **G-22** | Core is inside the building | Every `core.footprint_cm` vertex is inside **or on** the `site.footprint_cm` ring (point-in-polygon, boundary counts as inside), tol 0.5 cm. |
| **G-23** | Core sits on the structural grid | Every core vertex's X matches a cumulative `x_bay_cm` grid line and its Y matches a cumulative `y_bay_cm` line, tol 0.5 cm. A core may not cut a bay in half. |
| **G-24** | Grid spans the footprint | `Σ x_bay_cm == site.footprint_width_cm` and `Σ y_bay_cm == site.footprint_depth_cm`, tol 0.5 cm; every bay > 0; every `column_*` coordinate lies strictly inside the footprint. |
| **G-25** | Facades close | Each facade's `start_corner_cm` and `end_corner_cm` are footprint vertices; `length_cm` equals the distance between them; `bay_count == len(bay_width_cm)`; `Σ bay_width_cm == length_cm`, tol 0.5 cm; every bay > 0. |
| **G-26** | Openings are physically sane | `width_cm > 0`; `head_cm − sill_cm > 0`; `sill_cm ≥ 0`; **`head_cm ≤ levels[level_index].height_cm`**; `position_cm ≥ 0`. |
| **G-27** | Openings fit their host bay | `width_cm < bay_width_cm[level's bay]` **strictly**; and `bay_start ≤ position_cm − width_cm/2` and `position_cm + width_cm/2 ≤ bay_end`, tol 0.5 cm, where `bay_start` / `bay_end` are the cumulative bay offsets on that facade. |
| **G-28** | Openings do not collide or duplicate | `openings[].id` unique within the file; no two openings share the same `(facade, level_index, bay_index)`; every `facade` exists in `facades[].id`; every `level_index` exists in `levels[]`; every `bay_index < facades[].bay_count`; every `type` is in the §5.11 vocabulary. |
| **G-29** | Area arithmetic is consistent | `floor_plates[i].gross_area_m2 == site.footprint_area_m2` (prismatic building), tol 0.05 m²; `building.gross_floor_area_m2 == Σ floor_plates[].gross_area_m2`, tol 0.05 m²; `building.net_floor_area_m2 == gross − Σ_{i in core.spans_level_indices} core.footprint_area_m2`, tol 0.05 m²; `0 < net_usable_area_m2 ≤ gross − core share`. |
| **G-30** | Roof is consistent | `roof.deck_level_cm == building.total_height_cm`, tol 0.5 cm; every level in `core.spans_level_indices` exists in `levels[]`. |

### 9.4 Cross-file

| Id | Title | Check |
|---|---|---|
| **G-31** | Cross-file references resolve | Every id, dotted path and `component_ref` a file references exists in the file that declares it. Every `origin_inputs` path resolves in a **defined** file, and every ledger `field_path` — **bare or file-qualified per §6.1.1** — resolves in a file that exists in the project. |
| **G-32** | Derived values recompute | Every `origin: "derived"` value equals its documented formula recomputed from its `derives_from` inputs, at the tolerance for its unit. A derived value that disagrees is an error, never a warning — this is what stops a hand edit to `total_height_cm` from surviving. |
| **G-33** | Tolerances are declared | `tolerances` exists in `dimensions.json`, all three values are present and non-negative, and every arithmetic rule above uses them unless it names its own. |

### 9.5 Tolerance policy

- **Equality checks use `tolerances.linear_cm` (0.5 cm)**, `area_m2` (0.05 m²), `angle_deg` (0.01°).
- **Range checks are exact** — no tolerance. A value outside its range is out, not nearly in.
- **G-27's strict `<` on `width_cm` has no tolerance.** 420 cm in a 450 cm bay passes; 450 cm fails.
- **G-22 and G-23 use 0.5 cm** so that a value written as `449.9999` is not a violation.
- **A tolerance is never applied to a count.** `bay_count` is an integer and is compared exactly.

---

### 9.6 Massing — `massing.json` (P3)

All of these are functions over the two files with no 3ds Max. `G-34`…`G-40` extend the same
machinery as `G-9`…`G-33`; they add no new tolerance values.

| Id | Title | Check |
|---|---|---|
| **G-34** | Element identity | Every `elements[].id` matches `^EL-\d{3}$`, is unique and ascends. Every `grouping[].id` matches `^GRP-\d{3}$`, is unique and ascends |
| **G-35** | Element solidity | `profile_cm` has ≥ 3 vertices, no duplicate vertices, no repeated final vertex, is a simple ring, and its winding matches the sibling `profile_ccw`. `z_range_cm[1] > z_range_cm[0]`, both finite. `kind` is in the §8.1.1 vocabulary |
| **G-36** | Massing provenance | `origins` covers this file's value tree exactly once, using §5.2's exclusions (G-9 machinery). Every `origin` is `derived` — an element that is `given`, `assumed` or `conflict` is a defect, because `dimensions.json` already resolved all three — with a non-empty `derives_from` whose paths resolve in `dimensions.json` or in this file. `origin_inputs` paths all resolve in `dimensions.json`. **The derived-only clause is scoped to the value tree:** an entry under the `defaults` block may be `assumed` and must carry an `origin_ref` (09 `D-FW-01`, `A-025`), because nothing in `dimensions.json` dimensions a facade build-up — the same documented exception G-64 makes for `components_registry.json`'s `A-023` / `A-024`. Every geometry leaf is still `derived`, so the clause cannot be stretched to cover invented massing |
| **G-37** | Storey chain | `storeys[i].index == levels[i].index`, `level_ref` is that level's `id`, `elevation_cm` / `height_cm` equal the level's within `linear_cm`, and `z_range_cm == [elevation_cm, elevation_cm + height_cm]` within `linear_cm`. `slab_ref` names a `slab` element whose `storey_index == i`; every id in `column_refs` / `core_refs` exists and has `storey_index == i` |
| **G-38** | Element-to-dimension agreement | For each element: a `slab`'s `z_range_cm` equals `[level.elevation_cm − floor_plates[i].thickness_cm, level.elevation_cm]`; a `column`'s equals `[level.elevation_cm − slab thickness, level.elevation_cm + level.height_cm]`; a `core_wall`'s `profile_cm` equals `core.footprint_cm` **inset by `core.wall_thickness_cm`**; a `roof_deck`'s equals `[roof.deck_level_cm − roof.deck_thickness_cm, roof.deck_level_cm]` (the deck is the **top** of the build-up and its thickness hangs below it — §5.9); a `parapet`'s equals `[roof.deck_level_cm, roof.deck_level_cm + roof.parapet_height_cm]`, so the model's top equals `building.overall_height_cm` within `linear_cm`. All within `linear_cm`. Every `storey_index` is `null` or an index in `storeys[]`, and a level named by `core.spans_level_indices` has a `core_wall`. **A `facade_wall`'s `z_range_cm` equals `[level.elevation_cm, level.elevation_cm + level.height_cm]`** (full storey height, tol `linear_cm`), **and every `(facades[i].id, levels[j].index)` pair has exactly one `facade_wall`** whose band spans that facade's `length_cm` and whose `storey_index` is `j` — the band is recomputed from the run's two corners, the run's inward side and `defaults.facade_wall_thickness_cm`, so a wall is matched to its facade by geometry rather than by a key that would let the file agree with itself. **A missing wall is a FAIL, not a gap**: an opening cut whose `host_ref` resolves to nothing is a silent hole |
| **G-39** | Layer vocabulary | Every `layer` value is in §8.1.4, and every element's layer equals the fixed mapping for its `kind` (§8.1.2). `site_pad.layer == "00_SITE"` and every `grouping[].layer == "90_SCENE"` |
| **G-40** | Grouping completeness | Every `elements[].id` appears in **exactly one** `grouping[].element_ids`, and every id inside a group exists. `parent_pivot_cm` equals the group's element bbox centre in XY and its minimum Z, within `linear_cm` |

**A check that cannot be evaluated reports SKIP with its reason, never a silent PASS.** If
`massing.json` is absent while §4 still marks it reserved, that is an informational SKIP; once §4
says `defined`, absence is a FAIL.

**A `draft` massing file is not evaluated either.** `massing.json` is *computed*, so the stub
`init_project.py` writes is an empty placeholder with no provenance to check. `G-34`…`G-38` and `G-40`
therefore report SKIP with that reason while `status != "locked"`. **Corrected at P6:** this
sentence used to add "*`--allow-draft` forces them to run and they will then fail, which is the
point*", which was true only of a draft **with content**. `--allow-draft` is a **status** flag —
it turns a non-locked status into a SKIP, the way `G-4` already treats it — so an **untouched
scaffold stub** is not evaluated even under the flag, while a filled-in draft is. See §9.9 for the
rule in full and for the defect the old sentence caused (17 FAIL rows on a fresh scaffold).
`G-39` is satisfiable by the stub and keeps running.

---

### 9.7 NURBS — `nurbs.json` (P4, extended P4b)

Same machinery, no new tolerances. **`G-41`…`G-53` and `G-55` are predicates over one file; nothing needs
3ds Max.** `G-54` and `G-56` are the two exceptions and each says so itself: `G-54` observes a commit,
`G-56` observes the emitted script.

| Id | Title | Check |
|---|---|---|
| **G-41** | Identity and naming | `sections[].id` matches `^SEC-\d{3}$`, `surfaces[].id` `^SUR-\d{3}$`, `derivatives[].id` `^DRV-\d{3}$`; each set is unique and ascending. Every `name` (`sections[].name`, `surfaces[].name`, `derivatives[].name`) is unique in the file and contains no `-` (rule N1 — a hyphen in a node name reads as subtraction in emitted MAXScript) |
| **G-42** | Section shape and rectangularity | `points_cm` has ≥ 2 entries, each exactly 3 finite numbers, no duplicate consecutive point. Every section referenced by one surface has the **same point count** as every other section of that surface — mandatory for `point_grid` / `cv_grid` (a lattice is rectangular) and for `uv_loft` (a network needs matching families). A `rail_section_ids` / `trim_section_ids` entry is a profile of its own and is **not** compared against the cross-sections it travels with |
| **G-43** | Kind fits its keys | `kind` ∈ §8.2.3 — **eight values**. A surface carries exactly the keys its kind requires and none of the forbidden ones (§8.2.2). `layer`, when present, is in the surface's declared set. `mat_id ≥ 1`, `merge_tol_cm ≥ 0`, `approximation` keys are integers/floats within §8.2.4 |
| **G-44** | References resolve and nothing is orphaned | Every id in `section_ids`, `u_section_ids`, `v_section_ids`, `rail_section_ids`, `trim_section_ids`, `parent1_ref`, `parent2_ref`, `surface_ref` resolves within this file. Every section is consumed by **at least one** surface — an unused section is a defect, not a spare, and a rail is a section |
| **G-45** | Kind-specific cardinality | `u_loft`: ≥ 2 sections. `uv_loft`: ≥ 1 in each family, and not 1 in both. `point_grid` / `cv_grid`: ≥ 2 sections, each with ≥ 2 points |
| **G-46** | Order is meaningful, not clamped away | `u_order`, `v_order` are integers in 2–5 and **≤ the count they apply to** (`u_order ≤ points per row`, `v_order ≤ number of rows`). The library clamps with `amin`, so an out-of-range order is silently discarded — a spec that says 5 on a 4-point row would build something other than what it says |
| **G-47** | Thickness is meaningful | `thickness_cm` on a `u_loft` satisfies `\|thickness_cm\| ≥ 0.001`. Below that the library omits the offset surface and the build silently loses a shell. `derivatives[].thickness_cm ≥ 0` where present |
| **G-48** | Derivative fitness | `kind` ∈ {`quad_panels`, `space_frame`}; `divisions_u`, `divisions_v` are integers ≥ 1 (counts are exact — §9.5); `sub_steps ≥ 1` on `space_frame` and absent otherwise; `thickness_cm` on `space_frame` and absent otherwise |
| **G-49** | NURBS provenance | `origins` covers this file's value tree exactly once, using §5.2's exclusions. Every `origin` is `derived` — a `given`, `assumed` or `conflict` value here is a defect, because `dimensions.json` and `massing.json` already resolved all three — with a non-empty `derives_from` whose paths resolve in `dimensions.json`, `massing.json` or this file. `origin_inputs` paths all resolve in `dimensions.json` or `massing.json` |
| **G-50** | Dependent-surface arity | `rail_sweep`: `rail_section_ids` has **exactly 1** entry and `section_ids` ≥ 2. `two_rail_sweep`: `rail_section_ids` has **exactly 2** entries and `section_ids` ≥ 2. `blend`: `parent1_ref`, `edge1`, `parent2_ref`, `edge2` are all present. `trim`: `surface_ref` is present and `trim_section_ids` ≥ 1. **FAIL** — a relation with a missing operand is §8.2.8 row 2, and nothing else in the system reports it |
| **G-51** | Every cross-section meets its rail | For each `rail_sweep` / `two_rail_sweep`: every entry of `section_ids` intersects **every** entry of `rail_section_ids`, within `tolerances.linear_cm` (0.5 cm). **FAIL.** This is the pre-flight for the silent drop — Max **discards a sweep whose cross-sections never meet its rail, and reports no error and no warning**: the build completes, the node appears, and the surface is simply not in the set. It is the reason this stage exists |
| **G-52** | Blend parents resolve, and resolve **earlier** | `parent1_ref` / `parent2_ref` match `^SUR-\d{3}$` and name a `surfaces[].id` **declared earlier in the file** (ascending `SUR-` order); `edge1` / `edge2` are integers in `1..4` (§8.2.7's low-U / high-U / low-V / high-V). **FAIL** — a forward or dangling parent has no defined resolution order at emission time |
| **G-53** | Trim operands are well formed | `p_vec` is exactly 3 finite numbers with **non-zero magnitude**; `seed`, where present, is exactly 2 finite numbers; `flip_trim`, where present, is a boolean. **FAIL** — a zero `p_vec` declares a projection direction that does not exist, and no transcript shows Max rejecting one: the constructor accepts whatever it recognises without complaint (§8.2.8 row 3), so a bad operand can only be caught here or not at all |
| **G-54** | Emitted-surface census | A committed node contains **exactly** the number of `NURBSSurface` sub-objects the spec implies — for a `trim` that number is **0**, because the kind projects and does not cut (§8.2.8 row 8). **FAIL at build time; honest SKIP with its reason at lint time** — a static file cannot observe a commit, and a check that cannot be evaluated must never report a silent PASS (§9.6). The emitted `.ms` counts the surfaces after `NURBSNode` and throws on a mismatch |
| **G-55** | Blend tension range | `tension1` / `tension2`, where present, are floats in `0.0 … 1.0`. **FAIL** — Max neither rejects nor bounds a larger tension, and the overshoot grows with it: at `1.0 / 1.0` the worked example's blend reaches `y = 1195.64` against a parent edge at `y = 900`, 295.64 cm outside its own geometry, and drops 50 cm below the springing (§8.2.7) |
| **G-56** | No synthetic pointer in a relation parent slot | No `parent1ID:` / `parent2ID:` position in the emitted MAXScript holds a literal; every one is a variable bound from a committed sub-object (§8.2.7, §8.2.8 row 4). **FAIL at build** — a string there is an `IntegerPtr` conversion error, and a bare number is an `EXCEPTION_ACCESS_VIOLATION` that **kills the 3ds Max process**: not a catchable MAXScript error, not recoverable from inside the script, and the scene is left with orphans |

**G-54 is the load-bearing one.** P4 shipped a stage whose entire cost of a wrong decision was
invisible: a dependent surface that loses its rail produces a *successful build* and a node with no
surface in it. `G-51` is the cheap static pre-flight and `G-54` is the expensive truth, and neither
is optional — this is the P4 lesson generalised, **measure the output, do not trust the input**.

**`G-50`…`G-53` extend G-43, G-44 and G-45 rather than replacing them.** The kind vocabulary they police
is §8.2.3's eight; G-43's forbidden sets are what stop `thickness_cm` or `weights` appearing on a
dependent surface, and G-44's orphan rule now covers rails and trim profiles as well as loft sections.
`G-51` is the only new invariant that needs geometry rather than JSON shape, and it needs none beyond
`tolerances.linear_cm`, which §3.3 already declares. **`G-55` is the range G-16 could not supply** —
before §8.2.7 declared one, a tension was unbounded by construction — and **`G-56` is §8.2.8 row 4
written as a check**, the way row 4's index rule is enforced in the builder rather than by lint.

**A `draft` `nurbs.json` is not evaluated.** Same argument as §9.6: the file is computed from
`massing.json`, so the `init_project.py` stub has no provenance and `G-41`…`G-53` and `G-55` SKIP
with that reason while `status != "locked"`; `--allow-draft` evaluates a **draft with content** and
still SKIPs an **untouched scaffold stub** — see §9.9, which corrects the older wording of this
sentence in all three places.
`G-54` SKIPs at lint time regardless of status, for the structural reason above, and `G-56` SKIPs with
it because it reads the emitted `.ms`, which does not exist at lint time.

**Two live facts this section depends on**, both established 2026-10-04 and recorded in
`CHECKPOINT.md`: a surface is **not evaluable until it is committed** — before `appendObject` +
`NURBSNode` its parameter ranges read `0.0` and `evalPos` returns `undefined`, after commit they read
their real domain — and a `point_grid` contributes **one `NURBSPoint` sub-object per lattice point
before the surface**, so its surface index is `nU·nV + 1`, not `1`. The builder resolves the surface
by superclass for exactly this reason; the schema forbids an index because indices are not knowable
until the set is built.

**The same commit rule is what makes the dependent-surface keywords of §8.2.6 readable at all**, and it
carries the hazard `G-50`…`G-54` exist for: a dependent surface is dropped from the set **silently**,
so a build that merely completes is not proof that the relation resolved. A spec may therefore not
treat "the `.ms` ran" as acceptance — only the census may.

---

### 9.8 Facade grid and components — `facade_grids.json` + `components_registry.json` (P5)

Same machinery, no new tolerances. **`G-57`…`G-69` are predicates over the two parsed files (plus
`dimensions.json` / `massing.json` for the cross-file ones); nothing needs 3ds Max.** `G-70` is the
single exception and it says so itself: it observes two **emitted CSVs**, which do not exist at lint
time — `G-54`'s arrangement exactly. `G-63`, `G-67` and `G-68` are cross-file and report SKIP with a
reason when the registry is absent; `G-69` reports SKIP when every `variants` array is empty, because
a rule nothing exercises should say so rather than pass vacuously.

| Id | Title | Check |
|---|---|---|
| **G-57** | Facade agreement and run angle | Every `facades[].id` exists in `dimensions.facades[]`, in the same order, and `name` / `direction_deg` / `length_cm` / `bay_count` / `bay_width_cm` equal theirs within tolerance (`bay_count` exactly). `bay_offsets_cm` is the cumulative sum with `[-1] == length_cm`; `bay_centre_cm[i] == bay_offsets_cm[i] + bay_width_cm[i]/2`. **`run_angle_deg == atan2(end.y - start.y, end.x - start.x)` in `(-180, 180]` within `angle_deg`, and no value in the file may be derived from `direction_deg`** — `F-S` and `F-N` both run along +X and carry `180` and `0`, so `direction_deg` is a facing label. **FAIL** — the field that would be reached for is the one that is wrong |
| **G-58** | Axis integrity | `axes[].id` `^AX-\d{3}$`, unique, ascending. `family` ∈ {`u`,`v`}, `kind` ∈ {`bay`,`opening_edge`,`level_base`,`level_top`}, `offset_cm` within its bound, and **`bay_index` is `null` for every `u` axis and a real bay index for every `v` axis**. Within one `(facade, level_index, family, bay_index)` offsets are strictly ascending and separated by more than `linear_cm`. Every `facades[].levels[].u_axis_ids` / `v_axis_ids` entry exists with the matching facade, level and family, `u_axis_ids` ascends by offset with first offset `0` and last `length_cm`, and `v_axis_ids` is ordered by `(bay_index, offset)` with **each bay's slice** running `0 → height_cm` and a bay that has no opening contributing exactly its `level_base` and `level_top`. Every `bay_offsets_cm[i]` and every `level_base` / `level_top` has a matching axis. **FAIL** — a `v` axis with no bay, or a bay slice that does not close at `0` and `height_cm`, is a division nobody can place |
| **G-59** | Panel rectangle integrity | `id` `^PNL-\d{3}$`, unique, ascending. `u_min_cm < u_max_cm`, `v_min_cm < v_max_cm` (strict), `width_cm` / `height_cm` equal the differences within `linear_cm`. Bounds inside `[0, length_cm]` × `[0, height_cm]`. `bay_index` is the bay containing the `u` midpoint. `layer == "05_FACADE"`. `opening_ref` is `null` or an opening with the same `facade`, `level_index`, `bay_index`. `centre_cm` equals `start_corner_cm + run_unit * u_mid` and `elevation_cm + v_mid` within `linear_cm`. `host_ref` is `null` or a `massing.elements[].id`. **FAIL** — the rectangle and its centre are what P6 places; a wrong `centre_cm` moves a panel with every other check still green |
| **G-60** | Panel edges lie on axes | The four axis ids exist, carry the panel's facade, level and family, and their offsets equal `u_min_cm` / `u_max_cm` / `v_min_cm` / `v_max_cm` within `linear_cm`. **`full_height` is asserted against the extent, not against a kind**: it is `true` exactly when `v_min_cm == 0` and `v_max_cm == height_cm`. **FAIL** — this is what makes `axes[]` the single source of offsets (§8.3.2) rather than a second, drifting copy. The flag was briefly specified as "a merged mullion only", which the per-bay rule falsifies twice: a bay with **no** opening is one whole-height `blank` panel, so both a kind-based definition and any assertion in the reverse direction fail on it |
| **G-61** | Complete partition | Per `(facade, level_index, bay_index)`: Σ panel areas `== bay_width_cm[b] × height_cm` within `area_m2`; and per `(facade, level_index)` the same sum `== length_cm × height_cm` within `area_m2`; **no two panels on the same facade and level overlap in their interiors**; every panel lies inside its bay's rectangle; every panel's `u` range lies inside its bay's `[bay_offsets_cm[b], bay_offsets_cm[b+1]]`. Every `(facade, levels[].level_index)` has ≥ 1 panel. **FAIL** — this is what makes the grid a *partition* rather than a pile of rectangles, and it is the check that would catch a duplicated or a dropped panel. Both sums are needed: the per-bay one catches a panel that spilled across a bay line, the per-facade one catches a bay that lost its whole slice |
| **G-62** | One opening, one panel | Every `dimensions.openings[]` entry is referenced by **exactly one** panel, and that panel has the same `facade`, `level_index`, `bay_index`, a u-range equal to `[position_cm − width_cm/2, position_cm + width_cm/2]` within `linear_cm` and a v-range equal to `[sill_cm, head_cm]` within `linear_cm`, and a `kind` that lists the opening's `type` in its `panel_types[].opening_types`. **FAIL** — strictly one, never "one or more": a vertical division is per bay, so an opening's own sill and head are its only divisions and nothing can split it. The earlier "tiles" wording was written to accommodate a shared facade-wide v grid, and that grid produced a 180 × 10 cm glass sliver 10 cm below a window head because a different bay's entrance head crossed it (§8.3.2). Two panels for one opening is not a partition nicety, it is a ribbon of glass |
| **G-63** | Panel-kind vocabulary and layer | `panel_types[].kind` unique and inside the §8.3.4 ceiling of six. Every `panels[].kind` is declared. `material_role` is consistent with `glazed` / `frame_member`, and `opening_types` is non-empty iff `glazed`. Every declared kind is used by ≥ 1 panel and served by ≥ 1 `components_registry.json` component (cross-file; SKIP with a reason when the registry is absent). **FAIL** — the ceiling is what stops a project from quietly growing a second vocabulary |
| **G-64** | Grid provenance | `origins` covers this file's value tree exactly once using §5.2's exclusions (G-9 machinery, array-element collapse allowed). **Every `origin` is `derived` with a non-empty `derives_from` whose paths resolve in `dimensions.json`, `massing.json` or this file** — P5 invents nothing in this file, so an `assumed` or `given` value here is a defect. `origin_inputs` paths all resolve in `dimensions.json` or `massing.json`. **FAIL** — the two `assumed` numbers live in the registry's `defaults` and nowhere else (§8.4.1) |
| **G-65** | Component identity | `components[].id` `^CMP-\d{3}$`, unique, ascending; `name` unique in the file and hyphen-free; `kind` ∈ `component_types[].kind`; `families[].id` `^FAM-\d{3}$`, unique, ascending; `layer == "05_FACADE"`; **every component appears in exactly one `families[].component_ids` and every listed id exists**. **FAIL** — an unindexed component is invisible to P6's resolution step |
| **G-66** | Component parameters recompute | `defaults` carries exactly `panel_thickness_cm` and `joint_width_cm`, each inside its declared range. `components[].parameters` is the ordered list of exactly `width_cm`, `height_cm`, `thickness_cm`, `joint_width_cm` in that order; each `source` is `size_cm` or `defaults` as §8.4.3 states; each `value` equals the corresponding number within `linear_cm`. `size_cm == [width_cm, height_cm, panel_thickness_cm]` within `linear_cm`. **FAIL** — this is `G-32` applied to the registry's own arithmetic |
| **G-67** | Component fits the panel kinds it serves | `serves_panel_kinds` non-empty, every entry a declared `panel_types[].kind`, and flags compatible with `kind`: a `glazed_panel` serves only `glazed` kinds; an `opaque_panel` only kinds that are neither glazed nor frame; a `frame_member` only `frame_member` kinds; an `entrance_door` only glazed kinds that host a `door` or `entrance` opening. `size_cm[0..1]` equals some panel's `width_cm` / `height_cm` within `linear_cm` — a component that matches no panel exists for no reason. **FAIL**, cross-file |
| **G-68** | Every panel is placeable | **Every** panel in `facade_grids.json` has ≥ 1 component whose `size_cm[0..1]` matches within `linear_cm` and whose `serves_panel_kinds` contains the panel's `kind`, and all matching components belong to **one** family. **FAIL names the first ten offending panel ids and the count. This is the total-join invariant** — the reason the registry exists, and the one that fails loudly the day a panel size has no block. SKIP with a reason when the registry is absent |
| **G-69** | Variant discipline | `variants[]` entries match `^VAR-\d{3}$`, unique within their component, `overrides` is a non-empty object and every key is one of the four parameter names. **A registry whose `variants` arrays are all empty reports SKIP with that reason** — the rule is then unexercised, and saying so is better than a vacuous PASS |
| **G-70** | Emitted-table census | `facade_table.csv` and `world_table.csv` each carry **exactly** `len(panels)` data rows; every `panel_ref`, `component_ref` and `family_ref` resolves; every `rot_z_deg` equals its facade's `run_angle_deg` within `angle_deg`; `instance_id` equals `panel_ref` on every row. **FAIL at build time; honest SKIP with its reason at lint time** — a static file cannot observe an emitted CSV. The builder asserts all of it after writing and refuses on a mismatch |

**G-61 and G-68 are the two that a reader should care about, and they are a pair.**
`G-61` says the grid *covers* its facade — every cell accounted for, no overlap, no gap — and
`G-68` says every one of those panels has a block behind it. Either one alone leaves a quiet
failure: a partition can be complete and still have no geometry for one panel, and a registry can be
meticulous and still leave a bay unglazed. **Between them, a grid that does not cover its facade and
a panel with no block are both build failures instead of a scene that is quietly wrong.** Everything
else in this section is arithmetic; those two are the invariants that make the stage trustworthy.

**A `draft` `facade_grids.json` is not evaluated either.** Same argument as §9.6: the file is
computed, so the `init_project.py` stub has no provenance to check. `G-57`…`G-66` and `G-68`…`G-69`
therefore report SKIP with that reason while `status != "locked"`; `--allow-draft` evaluates a **draft
with content** and still SKIPs an **untouched scaffold stub** — see §9.9, which corrects the older
wording of this sentence in all three places. `G-70` SKIPs at lint time regardless of status, for the
structural reason above.

---

### 9.9 Assembly — `assembly.json` (P6)

Same machinery, no new tolerances. **`G-71`…`G-78` are predicates over the parsed JSON plus
`components_registry.json`, `world_table.csv`, `massing.json` and `dimensions.json`; nothing
needs 3ds Max.** `G-82` and `G-83` join them — the wall tiling is arithmetic over the same files.
`G-79`…`G-81` are the three exceptions and each says so itself: they observe
the **emitted `assembly.ms`**, which does not exist at lint time — `G-54` and `G-70`'s
arrangement exactly. Every geometry row names the tolerance it used (§9.5).

| Id | Title | Check |
|---|---|---|
| **G-71** | Every placement names a real component | `placements[].id` `^PLC-\d{3}$`, unique, ascending. Every `component_id` resolves to a `components_registry.json` `components[].id`. **FAIL** — a placement naming no component is an instruction with no geometry, and it is invisible until someone opens the scene |
| **G-72** | `placements[]` and the world table are equal **in both directions** | Every `source_row` is a real 1-based data row of `world_table.csv` (header excluded), every data row appears exactly once, no duplicate `source_row`, and the two counts agree. **FAIL** — both directions are needed: a *missing* row and an *extra* row are different defects, and a rule that only counted them would see the same number in both |
| **G-73** | Placement geometry **equals its table row** | Each `position_cm` equals its row's `x_cm` / `y_cm` / `z_cm` within `linear_cm`, each `rot_z_deg` equals its row's within `angle_deg`, and `instance` is `true`. **FAIL** — the builder has two ways to place a panel and only one is right. `rot_z_deg` is the run angle `atan2(dy, dx)` and **never** `dimensions.facades[].direction_deg`, which is a facing label carrying `180.0` and `0.0` for two facades that both run along +X |
| **G-74** | Node names are unique and identifier-safe | `node_name` is unique across `placements[]`, `opening_cuts[]`, `wall_cells[]` **and** `scatter[]`, matches `^[A-Za-z][A-Za-z0-9_]*$`, and is derived from its own `id` with dashes replaced. **FAIL** — `11` §3.1: N1 because `-` reads as subtraction in MAXScript, N4 because a descriptive name is a lookup table nobody versions, and uniqueness because a name that identifies two nodes identifies neither |
| **G-75** | Layers come from `layer_map` | Every `placements[].layer` / `scatter[].layer` is a `layer_map` **key**; the role (the component's `kind`, or `scatter_source`) is listed under exactly that one key; every `layer_map` key is in the §8.1.4 vocabulary and lists at least one role. **FAIL** — the layer column is read *from* the map and never written beside it, so the two cannot disagree. SKIP with a reason when the registry is absent, since the role is then undecidable |
| **G-76** | Every opening names a real `facade_wall` and lies inside it | `opening_cuts[].id` `^CUT-\d{3}$`, unique, ascending. Every `host_ref` **resolves to a `facade_wall`** element and is never `null`; the host's `storey_index` equals the cut's `level_index`; `u_range_cm` lies inside the **host's own** `u` extent within `linear_cm` — the host's plan corners projected onto the run unit from `start_corner_cm` — and `v_range_cm` inside the host's own local `[0, level.height_cm]` within `linear_cm`; `kind == "difference"`. **FAIL** — measuring the extent on the *host* rather than on the facade is what makes this a statement about the wall, and an opening off the end of its wall produces no cell and no material, while one with a null host has nothing to be tiled at all. **`depth_cm` is now traceability only:** the declared opening's depth is retained so the declaration can be audited against `facade_wall_thickness_cm`, but the tiling passes clean through the wall (§8.5.8), so the hazard that clause existed to avoid — a cutter depth landing on two coincident surfaces — no longer arises, and a `depth_cm` below the thickness no longer produces a partial-depth hole |
| **G-77** | One opening, one cut, **both directions** | Every `dimensions.json` `openings[]` entry has exactly one cut and every cut names exactly one real opening. Each cut's `u_range_cm` equals `[position_cm − width_cm/2, position_cm + width_cm/2]` of its opening within `linear_cm` and its `v_range_cm` equals `[sill_cm, head_cm]` within `linear_cm`. **FAIL** — strictly one, never "one or more": two cuts on one opening mean two `u` ranges were authored for one rectangle and only one of them is the opening |
| **G-78** | Scatter ranges and reference resolution | `id` `^SCT-\d{3}$`, unique. `seed` is an integer in **1…31337 inclusive**; `0 < scale_from ≤ scale_to`; `rotation_from_deg ≤ rotation_to_deg`; `distribution_density_pattern` in 0…1; `instance_count_limit` an integer > 0 **and** ≤ `defaults.instance_limit_guard`; `collision_avoid` a boolean; `model_refs` ≥ 1 and every ref resolves in `massing.json` **or** `components_registry.json`; `target_ref` resolves in `massing.json`. **FAIL** — the seed range is closed on purpose: a seed outside it is either P0's typo'd constant or an uninitialised draw, and both make a rebuild a different scene. SKIP with a reason when `massing.json` is absent |
| **G-79** | No layer assignment in the emitted MAXScript | The emitted `assembly.ms` contains no `node.layer`, no `LayerManager` setter, no `.setLayer(`, `setProperty #layer`, `.layerIndex` or `LayerProperties`, and no layer-assignment helper. **FAIL at build time; honest SKIP with its reason at lint time.** Layer is unreachable from this bridge by nine measured routes (§8.5.6), so a builder that tries is a build FAIL, not a silent no-op |
| **G-80** | Emitted census — and it must **observe the scene** | The emitted `.ms` **walks the scene** and counts what it finds: placed instances, prototypes and the `WAL_`-prefixed wall cells, then **throws** on any mismatch against the three tables and against `wall_cells[]`. **FAIL at build time; honest SKIP with its reason at lint time** — a static JSON file cannot observe a script it did not write. The builder is the single implementation and asserts it on the bytes it has just written. **The scene walk is itself a required needle, not an implementation detail:** the previous census counted iterations of its own loop and therefore reported `cut_count = 16` and passed while the scene held `objects.count` 208 and **zero modifiers anywhere** (`nodes carrying modifiers=0`, `max stack=0`). A counter cannot detect a failed attach, which is why this rule is about what the census looks *at* |
| **G-81** | **Zero modifiers** — the stage attaches none | `addModifier` **does not appear at all** in the emitted `assembly.ms`: not once, in any function, for any node. The emitted script additionally **asserts the hosts arrive with empty stacks** and throws if any host carries one. **FAIL at build time. Measured, not inferred:** on 2026-10-05 `Extrude` and `Bevel` threw on `addModifier`, five rungs were clean in 38 ms, ten in 28 ms, and **twenty froze Max on the main thread until the machine rebooted.** The ladder is why the ceiling is **zero** rather than small — and the Boolean modifier that used to require a ceiling cannot cut at all in this build (§8.5.8.1), so there is nothing left to bound. The exact breaking point between ten and twenty is not established and must never be re-measured |
| **G-82** | The cells tile each wall exactly — **the volume identity** | For every host, the sum of its cells' `volume_cm3` equals **the host's volume minus its openings' volume** (each opening taken at the wall's own thickness, because every opening is cut clean through) within `linear_cm²`. Cells must be non-degenerate and lie inside the host's `z_range_cm`. **FAIL** — a difference is either a **gap** (material that was never built) or an **overlap** (material counted twice), and both are wrong in opposite directions, so a count is not enough and an average is not a check. **This is the rule the Boolean route could never have satisfied:** a modifier that removes nothing leaves the volume untouched, so a "successful" cut build reads as a wall with every opening still filled. SKIP with its reason when `massing.json` declares no `facade_wall`, or when `wall_cells[]` is absent — a file without it predates the tiling |
| **G-83** | Every cell carries its wall's **full thickness** | Each cell's extent in the wall's thin axis equals the host wall's own extent in that axis, within `linear_cm`. **FAIL** — a tiling of solid cells cannot express a partial-depth opening, so a cell that stops short of a face is a **defect, not a style choice**, and the alternative it invites is a silent partial-depth hole: a reveal that is not a reveal. This is stated as an invariant rather than assumed because the cross axis is the one place where "carry the wall's own extent" could quietly become "carry most of it" |

**`G-72`, `G-73`, `G-76` and `G-77` are the four that make this stage a build rather than a
description.** `G-76` says every opening has a wall to be cut out of; `G-77` says there is
exactly one rectangle per opening and it is the opening's own arithmetic; `G-72` says the
placement table is the world table with nothing added or dropped; `G-73` says it is a *copy*
rather than a recomputation. Between them, a cut that silently misses its wall, an opening
with two competing rectangles, a dropped panel and a panel placed by a facing label instead of
a run angle are all build failures instead of a scene that is quietly wrong.

**A `draft` `assembly.json` is not evaluated either.** Same argument as §9.6/§9.7/§9.8: the
file is computed, so the `init_project.py` stub declares no placement, no cut, no cell, no scatter
and no provenance. `G-71`…`G-83` therefore report SKIP with that reason while
`status != "locked"`.

**One clarification of the flag, because four files disagreed about it.** `--allow-draft` is a
**status** flag, not a "force every geometric rule to run" flag — that is exactly how `G-4`
already treats it: it turns a non-locked status into a SKIP instead of a FAIL. So it does two
different things depending on what it finds:

- **A draft that has been filled in** is evaluated under `--allow-draft`. A computed file with
  content has real provenance to check, and the resulting FAILs are the feedback the flag's
  author asked for.
- **An untouched scaffold stub** is not evaluated even under `--allow-draft`. The question is
  decidable, not a matter of taste: `massing.json`, `nurbs.json`, `facade_grids.json`,
  `components_registry.json` and `assembly.json` all keep their content in **arrays** —
  `assembly.json`'s in `placements[]`, `opening_cuts[]`, `wall_cells[]` and `scatter[]` — so an
  entirely empty array tree plus an empty `origins` is exactly the placeholder
  `init_project.py` writes. Every rule in the set would then be reporting the *absence of
  content* — a statement about the scaffold, not about the draft — and a check that cannot be
  evaluated must report SKIP with its reason rather than a manufactured verdict.

That is what `G-36`, `G-49`, `G-57`, `G-64` and `G-66` were getting wrong, and a fresh
`scaffold` linted with **17 FAIL rows** because of it. Nothing about a `locked` file changed,
and `examples/` stays `FAIL 0 / WARN 0` with and without `--build`.

---

## 10. The worked example

`examples/dimensions.json`, `examples/conflicts_resolved.json` and `examples/assumptions.json` are one
coherent project: **`pavilion-01`, a two-storey small office / pavilion.** `examples/massing.json` (P3)
is the fourth file of that same project and must reconcile against the first three — G-37 and G-38
are cross-file checks, so a massing file that drifts from its dimensions file fails immediately.
`examples/nurbs.json` (P4) is the fifth: its `origin_inputs` point at `massing.json`, and G-49 fails
if a lattice drifts from the massing it was derived from. `examples/facade_grids.json` and
`examples/components_registry.json` (P5) join the same project — the sixth and seventh files, both
computed, the first from `dimensions.json` + `massing.json` and the second from the first, so **every
panel and component count quoted anywhere is read out of the generated files rather than asserted
here** — the region in §8.3.5 is a build-time expectation, and the exact totals are whatever the
builder prints and `G-70` reconciles against the emitted tables. `examples/assembly.json` (P6) is the
**eighth** file and the **last** of the derived chain: it is built from
`components_registry.json` + `world_table.csv` + `massing.json` + `dimensions.json`, which is why
`massing.json` had to gain a `facade_wall` element kind (§8.1) — it is the only thing an opening can
be cut out of. Its `placements[]` has **one row per `world_table.csv` data row** (`G-72`, both
directions), its `opening_cuts[]` has **one row per `dimensions.json` openings[] entry** (`G-77`, both
directions), and it is the first file whose `layer_map` is **data only** and never applied
(§8.5.6). Because it is the end of the chain, `build_spec.py --stage massing` is no longer the last
builder in the project: **`scripts/place_components.py --stage assembly` is.**

**The example carries all four dependent kinds, one each — this changed at stage P4b round 1.** An
earlier revision of this section said the example carried none of them; that is **stale** and the file
now contradicts it. Measured by reading `examples/nurbs.json` (`schema_version` 1.0, `surfaces[]` of 7):
`SUR-001` `u_loft`, `SUR-002` `point_grid`, `SUR-003` `cv_grid`, then **`SUR-004` `rail_sweep`**,
**`SUR-005` `two_rail_sweep`**, **`SUR-006` `blend`** and **`SUR-007` `trim`** — exactly **one
occurrence of each of the four dependent kinds**, plus the three independent ones above and three
derivatives (`DRV-001` `quad_panels`, `DRV-002` `space_frame`, `DRV-003` `quad_panels`). The kind the
example still lacks is **`uv_loft`**, which appears **zero** times. So `G-50`…`G-53` are now
**exercised** by the file rather than vacuously satisfied.

**But `SUR-007` `trim` cuts no aperture.** The `trim` kind is **projection-only** (§8.2.8 row 8): it
projects a profile onto its parent and, per the P4b transcript, `trim:true` adds an untrimmed
`NURBSCVSurface` **copy of the parent** rather than cutting it, and `trim:false` adds no surface at all.
`SUR_007_VaultApertureGuide` is named for what it is — a guide. **A skylight, an oculus or a wall opening
in a NURBS surface cannot be expressed by this stage**: it needs a **Boolean modifier or a surface
split**, outside the NURBS schema. So the example now demonstrates all four dependent kinds *as schemas*;
a real aperture remains outstanding, and the dependent-surface **acceptance test** — build, commit and
measure the four kinds through an emitted `.ms` — is still outstanding too, because `build_spec.py`
accepts `--stage massing` only. That gap is escalated here rather than hidden.

| Property | Value |
|---|---|
| Footprint | 1800 × 900 cm rectangle, axis-aligned, CCW from `[0, 0]` |
| Structure | 4 × 2 structural grid at 450 cm; 3 interior columns at 40 × 40 cm |
| Levels | 2 — `LVL-00` at 0 / 420 high, `LVL-01` at 420 / 400 high |
| Roof deck | 820 cm, flat with a 2° fall, 90 cm parapet → 910 cm overall |
| Core | 450 × 450 cm in the south-east structural bay, both storeys, `lift_stair_wc` |
| Areas | 162 m² gross per floor, 324 m² total; 283.5 m² net of core |
| Facades | 4 — south/north 1800 cm (4 bays), east/west 900 cm (2 bays) |
| Openings | 16 — 4 on each long elevation per storey, 2 on each short elevation, less the two bays that are core wall. Includes one full-height glazed bay, `OP-G-04` / `OP-1-04`, in the south-east bay in front of the stair |

| Ledger | Count | Ids |
|---|---|---|
| Assumptions | 24 | `A-001` … `A-024` — `A-023` / `A-024` are P5's two facade defaults (§8.4.1) |
| Conflicts | 5 | `C-001` … `C-005` |

The five conflicts are the interesting part and are worth reading in the example file:

| Id | The contradiction | Rule |
|---|---|---|
| C-001 | Brief says 800 cm overall but also gives 420 + 400 per storey (820). | R3, R2 |
| C-002 | Curtain-wall head at 380 cannot coexist with the locked 400 floor-to-floor and the brief's own 60 cm spandrel. | R4, R2 |
| C-003 | "Seven bays across the front" against an 1800 cm facade and a 450 cm grid — 1800/7 is not a module. | R5, R3 |
| C-004 | Room schedule says a 120 cm parapet, aesthetic notes say 90. Neither outranks the other; the tie is broken on order. | R6 |
| C-005 | Room schedule says "250 slabs throughout", structural note says "300 ground, 250 suspended". | R2 |

The examples satisfy **every rule in §9**; that is the acceptance test for P2c. The load-bearing
places they exercise are G-18 (the level chain 0 → 420 → 820), G-22/G-23 (the core sits inside the
footprint and on grid lines), G-27 (the 420 cm glazed opening inside a 450 cm bay, and nothing else
overhanging its bay), and G-29 (162 / 324 / 283.5 all reconciling).

Two things in the example are deliberately imperfect and are recorded rather than hidden: the ground
and upper curtain-wall bays have different spandrels (20 cm vs 60 cm), which C-002 explains; and
`net_usable_area_m2` is 138 m² rather than the 141.75 m² that gross-minus-core would give, which
A-010 and A-011 explain. Both are exactly the situations the ledgers exist for.

---

## 11. Relationship to 3ds Max

This grammar makes **no claim about 3ds Max**. It is a data contract and needs no probe. The only
3ds Max facts it depends on are recorded here, and each was established by live execution per
`CHECKPOINT.md` §"Verified facts" — none of it was re-derived at P2a:

| Fact this grammar relies on | Status | Provenance |
|---|---|---|
| 3ds Max 2026.3.2, `namedpipe` transport, protocol 2, `mainThread` | ✅ verified by live execution | `CHECKPOINT.md` §Environment; `02-mcp-live-orchestration.md` §1 |
| Lengths are authored in centimetres and handed to Max unchanged | ✅ **verified by live execution (P3).** `units.SystemType` = `centimeters`, `units.SystemScale` = `1.0`. A spec value in cm is the same number in Max | `CHECKPOINT.md` §"Scene units and placement semantics" |
| Per-type dimension ranges (§5.6, §5.11) | ⚠️ **Advisory, not verified.** Sourced from `architecture-exterior-pipelines.md` §1.1, which `00-audit-p1.md` §3 flags as VERIFY-only. These are conventions for a human to sanity-check, and `09-defaults.md` (P2b) owns their authoritative form. | repo document, not probed |
| Layer names in `massing.json` / `assembly.json` | ✅ the vocabulary is closed and declared in §8.1.4. **But an object's layer cannot be assigned from MAXScript in Max 2026** — **nine** routes executed and rejected, final. Layer is *data*, and **no stage applies it** — the **user** applies it in the Layer dialog | `CHECKPOINT.md` §"Design consequences of the layer finding"; `agents/max-assembly.md` §6.3 |
> **CORRECTED (verified 2026-10-06):** this row previously read *"six routes executed and rejected … application is a P6 concern"*. Both halves were stale. **Nine** routes are ruled out, and **P6 closed it as permanently impossible — no stage applies a layer.** §8.5.6 of this file already carried the correct text ("Applying layers is a human action in the Layer dialog"); this row now agrees with it.
| A massing element is a `Box(width:,length:,height:,pos:)`, X/Y-centred on `pos.xy` with its base at `pos.z` | ✅ verified by live execution — `Box width:100 length:200 height:300 pos:[1000,0,0]` → `min=[950,-100,0] max=[1050,100,300]` | P3 probe |
| A NURBS surface is evaluable only after it is committed to a `NURBSSet` + `NURBSNode`; a `point_grid` surface sits at sub-object index `nU·nV + 1`, not `1` | ✅ verified by live execution (P4) — before commit ranges read `0.0` and `evalPos` returns `undefined`; a 5 × 3 point grid yields 15 `NURBSPoint` sub-objects then the surface | P4 probe |
| A **dependent** surface (`rail_sweep`, `two_rail_sweep`, `blend`, `trim`) behaves the same way, with one addition: an invalid one is **silently dropped** at commit. Its relational properties are readable **only after** the commit, and they do not read back as passed: `parent:`/`rail:`/`rail1:` → `0`, `railID` → **not the index** — an `IntegerPtr` printed `<decimal>P` (`0P` on a 1-rail sweep, a full pointer on a 2-rail one — **never parse or compare it**), `pVec [0,0,-1]` → `[0,0,1]`. Both sweep kinds carry a `[0,1]`-normalised domain, and the design surface is the **first** `NURBSSurface` for a sweep but the **last** for a blend | ✅ verified by live execution (P4b) — committed `NURBS1RailSweepSurface` reads `rail=0 parallel=true numCurves=3` with `railID` an `IntegerPtr` of unestablished printed form, every name failing pre-commit; a sweep with no rail set commits `numObjects=7` with no `NURBSSurface` at all, with `rail:` set `numObjects=14` with the surface at index 14. Full keyword map in §8.2.6; the schema in §8.2.7; what a spec may not encode in §8.2.8 | P4b probe |
> **CORRECTED (verified 2026-10-06):** this cell's evidence clause read *"`railID` an `IntegerPtr` of unestablished printed form"*. The printed form **is** established — `<decimal>P`, `0P` on a 1-rail sweep. See the next row, which now carries the measured statement.
| The **printed string form** of a `nurbsID` / `*ID` (`railID`, `parent1ID`, `parent2ID`) | ✅ **VERIFIED (2026-10-06).** It is an **`IntegerPtr`** and prints as `<decimal>P` — e.g. `3253572981568P`, and `railID` reads **`0P`** on a committed 1-rail sweep. A synthetic integer literal in such a slot hard-crashes Max (`EXCEPTION_ACCESS_VIOLATION`); a string there is a conversion error. Never parse it, never compare two, always bind it from a committed sub-object in the same script (`G-56`) | P4b probe; re-measured 2026-10-06, `railID = "0P"` reproduced 3 of 3; `12-nurbs-gotchas.md` §3.16, §3.23 |
> **CORRECTED (verified 2026-10-06):** this row previously read *"⚠️ UNVERIFIED, and one earlier reading was wrong … a later controlled probe did not reproduce it"*. **The printed form was measured, and `railID = "0P"` reproduced 3 of 3.** This table contradicted itself row-on-row — the row directly above (the dependent-surface row) already stated `<decimal>P` and `0P` correctly — so the two rows are now reconciled onto the measured answer. "Never parse or compare it" survives; "the printed form is unknown" does not.

**Nothing in §2–§8 is validated against 3ds Max geometry, and it does not need to be.** The grammar
is deliberately upstream of the bridge. P3 is the first stage that touches Max, and its probes
confirmed only the three facts listed above — units, the `Box` placement primitive, and that layer
assignment is impossible from script. If a later probe contradicts something here, the correction
lands in `09-defaults.md` or `11-layer-standard.md`, not in this file — this file owns shapes and
rules, not defaults and not scene conventions.

---

## 12. How to extend this grammar

A stage that adds a spec file, or adds a key to an existing one, does all six of the following. Any
one of them alone is an incomplete change, and an incomplete change is how the pipeline grows two
schemas that disagree.

1. **Add the schema row.** A table in §5–§8 with key, type, required/optional, units, range, meaning,
   default. A key with no declared range is unbounded, and the validator will say so rather than
   guessing. If it carries a length, the key ends `_cm` (G-8) — no exceptions, no bare `height`.
2. **Add the invariant.** A `G-n` row in §9 stating a check that is a **function over the parsed
   JSON**. Not "the geometry should look right" — not "the core should be sensible". If you cannot
   write it as a predicate, it is not an invariant; put it in `09-defaults.md` instead.
3. **Add the validator rule.** `scripts/validate_specs.py` implements it in the same stage. An
   invariant that nothing checks is documentation, and documentation that claims to be a check is
   worse than no invariant at all.
4. **Decide the provenance.** Every new value gets an `origin`. If it can be invented, it needs an
   `assumptions.json` entry with a reason, a confidence, an invalidation and a recheck stage. If two
   sources can disagree, it needs a `conflicts_resolved.json` entry and a rule from §7.1. An assumed
   value in a derived file names its file in `field_path` (§6.1.1); a computed value names a formula
   and lands in G-32; nothing is left with a dangling `origin_ref`.
5. **Update the inventory table in §4** — owner stage, purpose, status, top-level keys. Flip
   `reserved` to `defined` only when the file, a schema table and an example all exist.
6. **Add the example.** A worked example is part of the definition, not an illustration of it. For a
   new reserved file, that means the owning stage ships `examples/<name>.json` and it passes every
   invariant. Without an example, the schema stays `reserved` regardless of how complete §5–§8 look.

### Rules for extending an existing key

- **A stage may not silently reinterpret an existing key.** If the new meaning differs, the key is
  renamed and the old one deprecated with a note, or `schema_version` major is bumped.
- **A stage may not narrow a declared range without a conflict entry.** Tightening
  `roof.parapet_height_cm` from 60–150 because the current project is 90 is a silent reinterpretation
  of every other project's spec. Change the range in §5 with a reason, or leave it.
- **A stage may not add a required key to a `locked` file without bumping the minor version** and
  re-emitting the file. Hand-editing a locked file to add a required key breaks every project that
  was built against the old shape.
- **Reserved key lists in §8 are a promise, not a sketch.** If a stage finds a key missing while
  writing its file, it adds the key here first and bumps the minor version. A stage that finds itself
  inventing a schema at implementation time has skipped this step, and the correct fix is upstream in
  this file, not in the stage's own code.
- **Adding a rule to §7.1 is a schema change**, not a documentation change: existing
  `conflicts_resolved.json` files that were decided without it may need re-deciding, and their
  `rules_invoked` arrays must be re-checked against the new ladder.

### What must not happen

- No spec file may contain a computed result that no invariant recomputes. If it cannot be
  recomputed from the same file, it belongs to a downstream file.
- No spec file may reference a class, tool, modifier or plugin name. Those belong to
  `02-mcp-live-orchestration.md` and `06-arch-modifiers.md`. A spec that names `ChaosScatter` is a
  spec that will be wrong the day the routing table changes. A **`kind`** is geometric for the same
  reason: `rail_sweep` is not `NURBS1RailSweepSurface`, and §8.2.7 names the implementing class only
  as the builder's obligation. Renaming a kind to match its class would break every project already
  written against the geometric name.
- No spec file may grow a field whose only consumer is a human reading it. If nothing reads it in
  code, it belongs in a comment — and there are no comments, so it belongs in the brief.