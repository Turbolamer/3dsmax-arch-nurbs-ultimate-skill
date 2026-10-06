# 08 — Input Rules: from a request to a locked `dimensions.json`

> **Purpose:** the intake contract, the source trust hierarchy, the deterministic extraction procedure,
> the explicit list of values that may never be inferred, a full worked reconstruction of `pavilion-01`
> from a deliberately messy brief, and the pre-flight checklist for declaring S1 done. The schema being
> written against is `07-spec-grammar.md`; the values used to fill silences are `09-defaults.md`; the
> ladder run in step 4 is `10-conflict-resolution.md`.
>
> **No 3ds Max.** This stage never touches the bridge. It emits JSON and runs a validator. The single
> 3ds Max concern it touches — the scene's unit scale — is delegated to `09-defaults.md` §6 and is
> labelled **UNVERIFIED — no live probe** there. `07` §11 records the same gap.
>
> **Tooling status, stated plainly.** `scripts/init_project.py` and `scripts/validate_specs.py` are P2c
> deliverables and **both exist and ship** in the skill pack, alongside `scripts/env_preflight.py` and
> `scripts/install_skill.py`.
> **CORRECTED (verified 2026-10-06):** this paragraph previously read *"do not exist yet. Only
> `scripts/env_preflight.py` and `scripts/install_skill.py` exist today"* — that was true when written
> and is false now. Every command below is marked either ✅ exists or ⬜ planned; after this correction
> **no command in this file is ⬜** and nothing here claims a script runs when it does not.

---

## 1. The intake contract

An input is acceptable if a human can hand it over. It is **not** acceptable merely because it looks
dimensional. What each input kind can and cannot establish is fixed:

| Input kind | Can establish | **Cannot** establish | Trust anchor |
|---|---|---|---|
| **Dimensioned drawing** (DWG/PDF/scan with dimensions, grid, level marks, schedules) | `origin: "given"` dimensions, the structural module, bay counts, level names, the core position, schedule values | Intent that is not drawn; anything the drawing delegates to notes elsewhere; structure hidden behind finishes | A dimension on the drawing is a measurement. Feeds `R2` against a scaled estimate from anywhere else. |
| **Written brief / request** (chat, email, a paragraph) | `origin: "given"` for everything it states numerically; project name, typology, intent | Anything it omits — and a brief omits a great deal | Feeds `R2` (specific beats global), `R3` (parts beat totals), `R6` (order of statements). |
| **Table / spreadsheet** (room schedule, door schedule, area schedule, rate sheet) | Precise per-row values: `width_cm`, `head_cm`, areas, counts | Spatial relationships between rows; which facade or bay a row belongs to | Feeds `R2`. A schedule row tied to a named element beats a bare global value — that is exactly C-005. |
| **Imported geometry** (`.max`, `.fbx`, `.obj`) | Existing measurable geometry: extents, bay widths, slab thicknesses as they *are* | Design intent, and the authoring unit — the file's numbers are in its own units until measured against something | Treat as a **quantity**, i.e. `R3` territory: what the geometry measures beats what a note claims about it. `source.kind: "imported"`. |
| **Image / render / screenshot** | Proportions, counts, composition, adjacency, material intent | **Any dimension.** There is no scale in a picture | **Estimates only.** Every one becomes an assumption with a `confidence`. See §1.1. |
| **Sketch / hand annotation / photo of a whiteboard** | Intent, adjacency, rough order of magnitude | Dimensions, module, ratios you did not measure | **Estimates only**, normally `confidence: "low"`. |

### 1.1 An image or a sketch yields estimates, never dimensions

> **The rule.** A value read off a picture is `origin: "assumed"` with an `A-nnn` entry. It is **never**
> promoted to `origin: "given"`. "Given" means *stated in the input as a dimension*. A photograph has no
> dimension in it, however confident the reader is.

Three ways this goes wrong, all of them common:

1. **Silent promotion.** The agent scales a window against a door it also scaled, and writes the result
   into the spec as `given`. Two assumptions now masquerade as one fact, and neither is in the ledger.
2. **Invented scale.** A perspective render is scaled using an assumed camera distance. The result is a
   number with no source at all — worse than no number, because it looks like data.
3. **Double-counted estimate.** An image gives a proportion, a brief gives an absolute, and the agent
   writes both without noticing they are the same fact measured twice.

| `confidence` for an image-derived value | Use when |
|---|---|
| `high` | Scaled against a dimension stated **in the same image** (a dimension string, a known door size, a scale bar). |
| `medium` | Scaled against a dimension stated **elsewhere in the same project**, e.g. a brief figure or an imported model. |
| `low` | Taken from a convention or a typical proportion (`09-defaults.md`) because nothing measurable existed. |

`assumptions[].reason` for an image estimate must name the **image** and the scale source: *"brief image
`sketch-01.png`, window width scaled against the 90 cm door in paragraph 8"* — never *"the window is
150 cm"*, which just restates the value (`07` §6.1).

### 1.2 Sibling inputs do not merge silently

If a drawing and a brief disagree, that is a **conflict** (`10`, `R1`–`R6`), not a merge. If a drawing
and an image disagree about the same wall, and neither is dimensioned, that is an assumption at best
and a question at worst. **Never average two sources.** Averaging destroys both the conflict log and the
module discipline, and it produces a value no source supports.

---

## 2. Source hierarchy

Ranked by **evidence class**, not by file format. The rank answers one question: *when two sources
disagree about the same key, which one starts ahead?*

| Rank | Evidence class | Typical inputs | Beats a lower rank because | Ladder rules it feeds |
|---|---|---|---|---|
| 1 | **Stated requirement** | a code or authority note the input itself quotes | it is not a preference | `R1` — **only when the requirement is in the input.** The agent's memory of a code never qualifies (`10` §3.1). |
| 2 | **Dimensioned measurement** | dimension strings on a drawing, a measured imported model, a scale bar | someone measured it | `R2` against a scaled estimate |
| 3 | **Stated numeric value** | a number in the brief, a schedule cell | it was written down | `R2` against a global; `R3` as a part; `R6` as a position |
| 4 | **Stated composition / intent** | "glazed on the south", "blank on the rear", "keep the parapet low" | it is a design decision, and no measurement contradicts it | `R6` when two intents tie; escalate under `10` §6 E5 |
| 5 | **Derived quantity** | a total that a source computed from its own parts | it is arithmetic, not evidence | `R3` always loses to its parts |
| 6 | **Scaled estimate from an image** | proportions from a render, a sketch, a photo | it is a measurement of a picture | `R2` loses; assumption with a confidence |
| 7 | **Convention** | a proportion, a typical size, a rule of thumb | it is a habit, not evidence | `R7` — **silence only, never a conflict** (`G-14`) |
| 8 | **Agent inference** | anything not in ranks 1–7 | **it is not a source.** | **It is never a source.** See §4. |

Two rules that keep this hierarchy honest:

- **Rank 1 requires the input.** A code requirement is only rank 1 when the input states it. An agent who
  recalls a clause does not thereby promote it — that is the failure mode `R1` is most often misused for.
- **Ranks are per key, not per document.** A drawing is rank 2 for the bay widths and rank 0 for the
  roof drainage, which nobody drew. Do not rank a whole file and then treat every key in it as if it
  inherited the rank.

---

## 3. The extraction procedure

Deterministic, in this order. Each step's output is the next step's input, and each step is a function
of what came before — no step depends on the agent's mood.

### Step 0 — Register the source

Write the envelope `source` block (`07` §3.1) before anything else:

| Key | From |
|---|---|
| `source.kind` | the input kind: `user_brief` \| `drawing` \| `image` \| `imported` \| `assumed` (G-6) |
| `source.reference` | the actual artefact: file name, sheet, message, node name — `"drawing A-201 levels, sheet 3, dim string 4500"` |
| `source.recorded_at` | ISO-8601, the only clock value allowed anywhere in a spec (G-6) |

A mixed input gets **several `source` blocks' worth of provenance inside the one block** — the
`reference` string names every artefact, and each `detected_in` in the conflict log and each
`assumptions[].reason` names the specific one.

### Step 1 — Segment the input into addressable refs

Every fact the pipeline keeps must be addressable, because every later stage cites it.

| Input kind | Ref form | Example |
|---|---|---|
| Written brief | `brief:paraN`, `brief:<section_name>` | `brief:para3`, `brief:room_schedule`, `brief:aesthetic_notes` |
| Drawing | `drawing:<sheet>:<element>` | `drawing:A-201:gridline-4`, `drawing:A-201:general-notes` |
| Table | `table:<sheet>!<cell-range>` | `table:door_schedule!B4:B28` |
| Image | `image:<file>#<region>` | `image:front-elevation.png#bay2` |
| Import | `imported:<file>@<node>` | `imported:existing-tower.fbx@Slab_L01` |

`examples/conflicts_resolved.json` uses `brief:para2`, `brief:para3`, `brief:para4`, `brief:para5`,
`brief:room_schedule`, `brief:aesthetic_notes`, `brief:structural_note` — the same convention.

### Step 2 — Normalise every value into `07` key paths and centimetres

Read the value as written, convert, and place it at the key path in `07` §5. **Never write a value that
is not at a declared key path.**

#### 3.1 Units normalisation

| As written | To cm | Worked |
|---|---|---|
| `450 mm` | × 0.1 | 45.0 |
| `45 cm`, `45.` | × 1 | 45.0 |
| `4.5 m`, `4,5 m` | × 100 | 450.0 |
| `0.45 km` | × 100 000 | 45 000.0 |
| `10 ft`, `10'` | × 30.48 | 304.8 |
| `9 in`, `9"` | × 2.54 | 22.86 |
| `9'-6"` compound | both parts, then add | 274.32 + 15.24 = **289.56** |
| `9 1/2"` fractional | decimal first, then × 2.54 | 9.5 → **24.13** |
| `4500` on a drawing whose title block says `mm` | read the title block first | 4500 mm → **450.0** |
| `roughly 8 m`, `about 900`, `≈`, `say 300` | no arithmetic — mark as a **summary** | see `10` §3.3: hedged figures lose under `R3` |
| a length in a picture | **do not convert** — estimate and record an assumption | `08` §1.1 |
| 3ds Max scene numbers | see below | `09` §6 |

**Store to 0.1 cm.** A conversion like `4.5 m → 450.0` is exact; `18.0 m → 1800.0` is exact. Do not
round to 3 decimal places and do not round away a real disagreement: if `4.5 m` and `4500 mm` differ,
that is a `R2`/`R3` question, not a rounding question.

> **3ds Max `systemUnit` / `UnitsSetup` is a display setting and does not change geometry** — but
> ⚠️ **this is UNVERIFIED for this installation; no probe has been run** (`07` §11, `09` §6). The
> operational rule does not depend on how the probe lands: **the spec states centimetres (G-5), and any
> script that would write geometry in another unit converts at the script boundary.** Never edit the
> spec to match a scene, and never silently change a user's `Units Setup`.

#### 3.2 Tolerance policy

| Quantity | Tolerance | Source | Note |
|---|---|---|---|
| Linear equality | **± 0.5 cm** | `tolerances.linear_cm`, G-18, G-33 | half a millimetre. Catches a real error; absorbs float noise. |
| Area equality | **± 0.05 m²** | `tolerances.area_m2` | |
| Angle equality | **± 0.01°** | `tolerances.angle_deg` | |
| **Range** checks | **exact, no tolerance** | `07` §9.5 | a value outside its range is out, not nearly in. |
| Counts | **exact, never a tolerance** | `07` §9.5 | `bay_count` is an integer. |
| `G-27` opening-vs-bay | **strict `<`, no tolerance** | `07` §9.5 | 420 cm in a 450 cm bay passes; 450 fails. |

The level chain is the one place the 0.5 cm tolerance is load-bearing, and it is arithmetic only:

```
levels[i].elevation_cm = levels[i-1].elevation_cm + levels[i-1].height_cm      (G-18, ±0.5 cm)
```

**When the brief gives elevations instead of storey heights**, derive the height:
`height_cm = elevation_cm − previous elevation_cm`, mark it `origin: "derived"`, and record
`derives_from`. Do **not** write the elevation as `given` and the height as `given` — the two must be
able to disagree, and G-18 exists to catch exactly that.

### Step 3 — Place values at `07` key paths

| Rule | Detail |
|---|---|
| Every length key ends `_cm`, areas `_m2`, angles `_deg` | G-8. `height`, `width`, `thickness`, `radius`, `spacing`, `sill`, `head`, `length` without a suffix are **errors**, not style. |
| Derived values are computed, never entered | `footprint_area_m2`, `footprint_width_cm`, `footprint_depth_cm`, `column_x_cm`, `column_y_cm`, `interior_column_count`, `levels[i].elevation_cm`, `core.footprint_area_m2`, `floor_plates[].gross_area_m2`, `building.total_height_cm`, `overall_height_cm`, `gross_floor_area_m2`, `net_floor_area_m2`, `roof.deck_level_cm`, `facades[].length_cm`, `bay_count`, `bay_width_cm`. G-32 recomputes all of them. |
| Declare the footprint kind explicitly | `footprint_kind: "polygon"` vs `"rectangle"` changes how `footprint_cm` reads downstream. `pavilion-01` says `"polygon"` even though the brief described a rectangle — a rectangle is a declaration, not a shortcut (`07` §5.4). |
| Declare winding | `footprint_ccw` is stated and the validator confirms it (G-21). |
| Grid sums must close | `Σ x_bay_cm == site.footprint_width_cm` and `Σ y_bay_cm == site.footprint_depth_cm` (G-24). A grid that does not reach the wall is a design error found at input time, cheaply. |
| Facades close | `bay_count == len(bay_width_cm)` and `Σ bay_width_cm == length_cm` (G-25). |
| Openings fit | `head_cm ≤ levels[level].height_cm` (G-26); `width_cm < bay_width` **strictly** (G-27). |
| One opening per `(facade, level_index, bay_index)` | G-28. |

### Step 4 — Find contradictions and run the ladder

Scan **across sources and within each source**. Contradictions hide inside a single paragraph far more
often than between two files.

1. List every competing statement about the same key. Each gets a `ref` from Step 1.
2. Walk `R1 → R6` in order. **The first rule that discriminates wins**; record every rule that
   discriminated, ascending (`10` §5.3).
3. `R7` is never in the walk. A value that is merely **absent** is a silence and goes to step 5.
4. Write one `C-nnn` entry per contradiction, with ≥ 2 `sources`, ≥ 1 `rejected` whose `why_lost` names
   the beating rule, and an `invariant_violated_if_unresolved` naming a real `G-` id.
5. Anything on the do-not-decide list (`10` §6) stops here and goes to the user.

**Detection heuristics that find real contradictions in messy briefs:**

| Heuristic | Found in `pavilion-01` |
|---|---|
| A hedged total vs exact parts | C-001: *"roughly 8 m overall"* vs 420 + 400 |
| Two figures in one paragraph that must sum to a third | C-002: head 380 + spandrel 60 against a locked 400 floor-to-floor |
| A count that does not divide the length it describes | C-003: seven bays in 1800 cm on a 450 module |
| The same key stated twice, in two sections | C-004: parapet 1200 vs 90 |
| A global value vs an element-specific one | C-005: "250 slabs throughout" vs "300 ground, 250 suspended" |
| Arithmetic against the schema: a sum that will not close, a head above floor-to-floor, an opening wider than its bay | C-003, C-002 — this is `R4` territory and the ladder walk catches it mechanically |

### Step 5 — Fill the silences from `09-defaults.md`

For every key `07` requires that the input did not supply:

1. Pick the project-type preset (`09` §4).
2. Find the row. Read its **default** and its **range**; choose a value and be able to say why.
3. Allocate the next free `A-nnn` and write the entry: `field_path`, `value` **equal to the spec's
   value** (G-12), a `reason` that **names the silence** (not the number), a `confidence`, an
   `invalidated_by`, a `recheck_stage` in `P3`…`P6`, and `downstream_stages`.
4. Set `origins[field_path] = { "origin": "assumed", "origin_ref": "A-nnn" }`.
5. If no row exists, or the row is marked **escalate**, **ask the user** instead. Never improvise.

Confidence is about **evidence** (`07` §6.1): `high` = a stated default or a direct consequence of a
given value; `medium` = a defensible convention with a real alternative; `low` = a guess a professional
would immediately change. **A first-pass project is legitimately full of `low`, and that is an accurate
picture, not a defect.**

### Step 6 — Emit the three files

| File | Content |
|---|---|
| `specs/pipeline/dimensions.json` | envelope, then `tolerances`, then **`origins` before the value tree** (G-1), then the tree. Every leaf covered exactly once (G-9). |
| `specs/pipeline/conflicts_resolved.json` | envelope, `precedence_rules` (the ladder copied in), `conflicts[]`. **May legitimately be empty.** |
| `specs/pipeline/assumptions.json` | envelope, `assumptions[]` ascending, `cross_references.conflict_sourced_paths`. |

Three traps that cost more time than anything else in this stage:

- **`origins` before the tree.** G-1. It reads backwards otherwise.
- **Array elements that mix origins get one entry per leaf.** `levels[]` in `pavilion-01` mixes `given`
  (`elevation_cm` at level 0) / `derived` (`elevation_cm` at level 1) / `conflict` (`height_cm`) /
  `assumed` (`use`), so each leaf carries its own entry — while `facades[0..3]` and the `given`
  openings collapse to one entry each because all their leaves share an origin (G-9).
- **`cross_references` carries no `A-` ids.** A `conflict_ref` under `assumptions` is a validation
  error (`07` §6.2). It is a reader's convenience, not a second ledger.

### Step 7 — Validate

| Command | Status |
|---|---|
| `python scripts/validate_specs.py specs/pipeline/` | ✅ **exists and ships** (`scripts/validate_specs.py`). It implements the `G-1`…`G-33` list in `07` §9 and exits non-zero on any failure. |
| `python scripts/env_preflight.py` | ✅ exists — but it probes 3ds Max and this stage has no Max dependency. Not part of S1. |
| `python scripts/init_project.py <project>` | ✅ **exists and ships** (`scripts/init_project.py`). It scaffolds the workdir and the eleven `specs/pipeline/` spec files plus `project.json`. |

> **CORRECTED (verified 2026-10-06):** both rows above previously read *"⬜ planned, P2c — does not exist
> yet"*, and the text beneath them told the reader to create the directory and copy the envelope by
> hand and to treat a manual checklist as S1's gate. **Both scripts exist and ship with the skill
> pack**, and `validate_specs.py` is the real gate. The manual checklist in §6 remains useful as a
> reading aid, but **it is not a substitute for the validator and must not be described as one.**
> Stage ownership of these two scripts is `agents/max-input.md`.

**S1's gate is `validate_specs.py`:** run it against `specs/pipeline/` and require exit 0.

### Step 8 — Report and hand off

Report, in this order: the three file paths; the count of assumptions and of conflicts; every conflict
with the rule that decided it; **every open escalation**; and anything the pipeline defaulted that a
client would be surprised by. Then hand to P3 — which must re-check every `A-nnn` whose
`recheck_stage` is `P3`.

---

## 4. Never infer what you have not been told

Each row below is a value an agent is tempted to produce because the schema needs it. For each: ask, or
name the default explicitly. **Silently inferring any of these is the failure this file exists to
prevent.**

| # | Value | Why it cannot be inferred | Ask, or default (named) |
|---|---|---|---|
| 1 | **Storey count** | It sets `levels[]`, and therefore every elevation, plate, opening count and the whole vertical model. One wrong storey rebuilds the project. | **Ask only.** No default exists. Escalate per `10` §6 E4. |
| 2 | **Structural system** | Material, framing type, load paths and foundations are a licensed engineer's scope. A wrong system invalidates massing, NURBS and every clearance. | **Ask only.** No default. `structure.system` in `pavilion-01` is `given` because the brief stated it. Proxy *dimensions* at `confidence: "low"` with `recheck_stage: "P3"` are the documented limit (`09` §5). |
| 3 | **Egress** — exit count, widths, travel distance, stair provision, door swing, accessible egress | Code-driven. `R1` cannot be applied from memory (`10` §3.1). | **Ask only.** `09` rows D-CR-07/08/11/12 are marked escalate for this reason. |
| 4 | **Fire rating, compartmentation, separation, sprinklers, alarms** | Life safety and code-driven. | **Ask only.** No default row exists for any of them, deliberately. |
| 5 | **Cost, rates, budget** | No key exists for cost in `07`, and a number that reaches a client is a professional commitment. | **Ask only.** Do not compute, do not estimate, do not present a currency figure. |
| 6 | **Area figures quoted to the user** | `gross_floor_area_m2` and `net_floor_area_m2` are `derived` (G-32) and safe to state *as derived*. `net_usable_area_m2` is `assumed` and is **not** a quotable figure until confirmed. | State the label. Ask before quoting anything from an assumption (`10` §6 E3). |
| 7 | **Façade composition** — glazed, punched or blank, and which bays | Design intent. `A-016`…`A-022` show the agent adding punched windows to elevations the brief never described; that is a rendering-quality decision with a stated rationale, and the user may reasonably reverse it. | **Ask**, or apply D-FM-09 at `confidence: "low"` and say so plainly in the report. Escalate under `10` §6 E5. |
| 8 | **Roof build-up** — form, layers, drainage | A wrong roof form invalidates massing, NURBS and materials, and `building.overall_height_cm` moves with it. | **Ask.** Where the brief says only "parapet roof", D-PC-05 gives `flat_parapet`, D-PC-06 gives 2°, D-PC-08 gives `internal_downpipe` — each as an `A-nnn`, never as fact. |
| 9 | **Client or authority constraints** | The agent cannot verify them, and inventing one is worse than omitting it. | **Ask only** (`10` §6 E7). Do-not-default list item 10. |
| 10 | **Site address, coordinates, true orientation, plot boundary** | A real-world fact the agent cannot see. | **Ask.** A rotation of 0° may be recorded as a *modelling convention* (`A-001`) and must never be reported as the site's true bearing (`10` §6 E9). |

---

## 5. Worked example — a messy brief becomes `pavilion-01`

The input below is deliberately messy: **5 contradictions** (C-001 … C-005) and **22 silences**
(A-001 … A-022). It is the brief that produced the three committed example files, and every id,
value and arithmetic below is theirs.

### 5.1 The brief, as received

```
Pavilion 01 — small office pavilion. Brief, 2026-10-04.

 1. Single building, roughly 18 m wide by 9 m deep, rectangle. Ground level at 0.
 2. Overall height roughly 8 m.
 3. Two storeys: ground storey floor-to-floor 420, first floor 400. Steel frame with an
    RC core. Structural grid at 450 across the long elevation.
 4. The south-east bay is a full-height glazed bay — it fronts the stair. Runs to a head
    at 380 and keeps a 60 spandrel band.
 5. Seven equal bays across the front.
 6. South ground floor: a 180 window in bay 1, a 200 double entrance door in bay 2, an
    180 window in bay 3, and the glazed bay in bay 4 at 420 wide, head 400.
 7. First floor south: three 180 windows, sill 90, head 270, in bays 1 to 3; bay 4 is
    the glazed bay as above.
 8. There is a service door on the back at bay 2, 110 wide, head 220.
 9. Parapet roof, 30 deck.
10. South is the street frontage; north is the back.
11. Room schedule: 250 slabs throughout, parapet 1200.
12. Aesthetic notes: keep the parapet low, about 900.
13. Structural note: 300 ground slab, 250 suspended.
```

Every opening in it is **centred in its bay** — that instruction is what makes the opening positions
`given` rather than assumed. Silence is heavy: there is no orientation beyond "south is the front", no
plot, no column size, no core content or position, no storey programme, no room schedule, no drainage
strategy, and four undescribed elevations.

### 5.2 Step 0–1 — register and segment

`source.kind: "user_brief"`, `source.reference: "user conversation 2026-10-04, brief 'pavilion-01 small
office pavilion'"`, `status: "draft"` until §7 passes.

Refs, in the order the brief states them — this order is what `R6` later depends on:

| Ref | Line | Carries |
|---|---|---|
| `brief:para1` | 1 | footprint 18 m × 9 m rectangle, ground level 0 |
| `brief:para2` | 2 | **summary** overall height ≈ 8 m |
| `brief:para3` | 3 | 420 / 400 storey heights, `steel_frame_with_rc_core`, 450 grid on the long elevation |
| `brief:para4` | 4 | glazed bay: head 380, spandrel 60 |
| `brief:para5` | 5 | **7** bays across the front |
| `brief:para6` | 6 | south ground: 180 window, 200 entrance, 180 window, 420 × 400 glazed bay |
| `brief:para7` | 7 | south upper: three 180 windows at 90/270, bays 1–3 |
| `brief:para8` | 8 | north service door, 110 wide, head 220, bay 2 |
| `brief:para9` | 9 | `flat_parapet`, deck 30 |
| `brief:para10` | 10 | which elevation is south → `plot_rotation_ref_axis: "north"` |
| `brief:room_schedule` | 11 | "250 slabs throughout", "parapet 1200" |
| `brief:aesthetic_notes` | 12 | "keep the parapet low, about 900" |
| `brief:structural_note` | 13 | "300 ground slab, 250 suspended" |

### 5.3 Step 2 — normalise

| As written | Key | Becomes | Note |
|---|---|---|---|
| 18 m wide, 9 m deep | `site.footprint_cm` | 1800 × 900, ring `[[0,0],[1800,0],[1800,900],[0,900]]`, `footprint_ccw: true` | rectangle → declared `footprint_kind: "polygon"` with an explicit ring |
| ground level at 0 | `site.ground_level_cm` | `0.0` | |
| roughly 8 m | — | **no number written** | hedged summary; `R3` territory, step 4 |
| 420 / 400 | `levels[].height_cm` | `420.0` / `400.0` | already cm |
| 450 grid | `structure.x_bay_cm` | `[450, 450, 450, 450]` | `Σ = 1800 == footprint_width_cm` (G-24) |
| 450 on the long elevation only | `structure.y_bay_cm` | **silence** → A-003 | |
| head 380, spandrel 60 | `openings[]` | **conflict** → C-002 | |
| 7 bays | — | **conflict** → C-003 | |
| 180, 200, 420 wide; 90/270, 260, 400 head | `openings[0..3]`, `[5]`, `[8..10]` | cm, centred on the bay centre | `given` |
| "slabs 250" / "250, 300 ground" | `floor_plates[].thickness_cm` | **conflict** → C-005 | |
| "parapet 1200" / "about 900" | `roof.parapet_height_cm` | **conflict** → C-004 | note 1200 mm → **120 cm**, not 1200 |

> The unit line that matters most in this brief is **`1200` in the room schedule**. It is millimetres and
> becomes `120.0` cm. Reading it as 1200 cm is a 12 m parapet — it would fail G-16's 60–150 range and
> send the pipeline looking for a conflict that does not exist. **Convert before you compare.**

### 5.4 Step 3 — place, and derive everything derived

Values as `given`: `building.name`, `building.typology`, `site.footprint_kind`, `site.footprint_cm`,
`site.footprint_ccw`, `site.ground_level_cm`, `site.plot_rotation_ref_axis`, `structure.system`,
`structure.grid_kind`, `levels[0].elevation_cm`, `core.footprint_kind`, `core.spans_level_indices`,
`roof.type`, `roof.deck_thickness_cm`, and the seven stated openings.

Derived, never entered — with the arithmetic shown because these are the load-bearing numbers:

| Derived key | Formula | Result |
|---|---|---|
| `site.footprint_area_m2` | 1800 × 900 | **162.0** |
| `site.footprint_width_cm` / `depth_cm` | X / Y extent | **1800.0** / **900.0** |
| `levels[1].elevation_cm` | 0 + 420 (G-18, ±0.5) | **420.0** |
| `building.total_height_cm` | `levels[1].elevation + levels[1].height` (G-19) | **820.0** |
| `core.footprint_area_m2` | 450 × 450 | **20.25** |
| `floor_plates[].gross_area_m2` | `site.footprint_area_m2` (G-29) | **162.0** each |
| `building.gross_floor_area_m2` | Σ plates | **324.0** |
| `building.net_floor_area_m2` | 324 − (20.25 × 2 levels spanned) (G-29) | **283.5** |
| `roof.deck_level_cm` | `building.total_height_cm` (G-30) | **820.0** |
| `building.overall_height_cm` | 820 + 90 parapet (G-20) | **910.0** |
| `structure.column_x_cm` / `column_y_cm` | interior grid lines | `[450, 900, 1350]` / `[450]` |
| `structure.interior_column_count` | 3 × 1 | **3** |
| `facades[].length_cm`, `bay_count`, `bay_width_cm` | from the footprint and the grid (G-25) | S/N 1800 & 4 × 450; E/W 900 & 2 × 450 |

Two structural placements fall out of the placement step and are worth naming because they are *choices*,
not derivations:

- **The core has no position in the brief.** It is snapped to the single south-east structural bay —
  `[[1350,0],[1800,0],[1800,450],[1350,450]]` — so that it occupies whole bays (G-23), sits against two
  external walls, and releases the rest of the plate as one open room. The brief does tie that bay to
  the stair in para 4, which corroborates the snap. Recorded as **A-006**, `confidence: medium`, with
  the real alternative named in `alternatives_considered`.
- **That core occupies two elevations' bays** — south bay 3 and east bay 0. Consequence: the east
  elevation's bay 0 is core wall and carries **no opening at all**, which is recorded in **A-016** so a
  later stage does not "helpfully" add one. The glazed bay `OP-G-04` / `OP-1-04` sits in front of the
  stair on purpose.

### 5.5 Step 4 — the ladder, five times

| Id | The contradiction | `rules_invoked` | Chosen | Rejected |
|---|---|---|---|---|
| **C-001** | `brief:para2` ≈ 8 m overall vs `brief:para3` 420 + 400 | `["R3","R2"]` | 820 — `building.total_height_cm` becomes **derived** | 800, a summary unsatisfiable without compressing a stated storey |
| **C-002** | `brief:para4` head 380 + spandrel 60 vs the 400 floor-to-floor locked by C-001 | `["R4","R2"]` | **340** = 400 − 60, written to `openings[11].head_cm` | 380 — 380 + 60 = 440, so the head would run 40 cm past the deck (`G-26`) |
| **C-003** | `brief:para5` seven bays vs 1800 cm on a 450 grid | `["R5","R3"]` | **4 bays** of 450; `structure.x_bay_cm`, `facades[0].bay_count`, `bay_width_cm` | 7 — 1800 / 7 = 257.14, not a module, off every column line |
| **C-004** | `brief:room_schedule` parapet 1200 vs `brief:aesthetic_notes` about 900 | `["R6"]` | **90** — `roof.parapet_height_cm` | 120, same class and specificity, earlier in the brief; **outranked, not wrong** |
| **C-005** | `brief:room_schedule` "250 throughout" vs `brief:structural_note` "300 ground, 250 suspended" | `["R2"]` | **30 ground / 25 suspended** | 25 applied to the ground plate — a global against an element-specific statement |

`R1` fires **nowhere** — the brief contains no code content, and a remembered clause cannot be `R1`
evidence. `R7` fires **nowhere** — nothing here is a silence.

**The one arithmetic failure the ladder caught without being asked.** C-002's residual: the ground-floor
glazed bay keeps the brief's own head of 400 against a 420 floor-to-floor, i.e. a **20 cm** spandrel,
while the upper bay resolves to a **60 cm** one. That asymmetry is buildable and was never in conflict,
so it is **carried forward as found**, and the entry says to reopen C-002 rather than edit the spec —
G-9/G-10 will block a hand edit to a conflict-sourced path anyway. This is the kind of thing a log
exists to make visible and a shortcut would have quietly normalised away.

### 5.6 Step 5 — the 22 silences

| `A-nnn` | Path | Value | The silence it names |
|---|---|---|---|
| A-001 | `site.plot_rotation_deg` | 0.0 | no orientation beyond "south is the front" |
| A-002 | `site.setback_cm` | 300.0 | no plot boundary |
| A-003 | `structure.y_bay_cm` | `[450, 450]` | 450 stated on the long elevation only |
| A-004 | `structure.column_section_cm` | `[40, 40]` | no column size — `low`, P3 proxy |
| A-005 | `core.type` | `lift_stair_wc` | "an RC core" without enumeration |
| A-006 | `core.footprint_cm` | SE bay ring | the core has no stated position |
| A-007 | `core.wall_thickness_cm` | 25.0 | no core wall thickness — `low`, P3 proxy |
| A-008 | `levels[0].use` | `office_open_plan` | no per-storey programme |
| A-009 | `levels[1].use` | `meeting_and_office` | no upper-floor programme |
| A-010 | `floor_plates[0].net_usable_area_m2` | 138.0 | no room schedule; 3.75 m² below gross-minus-core |
| A-011 | `floor_plates[1].net_usable_area_m2` | 138.0 | same, upper plate |
| A-012 | `roof.slope_deg` | 2.0 | "parapet roof" says nothing about falls |
| A-013 | `roof.parapet_thickness_cm` | 30.0 | no parapet thickness |
| A-014 | `roof.coping_overhang_cm` | 3.0 | no coping detail |
| A-015 | `roof.drainage` | `internal_downpipe` | no drainage strategy — and it is what makes A-012's 2° necessary |
| A-016 | `openings[4]` | 150 window, east | brief describes the south elevation only |
| A-017 | `openings[6]` | 150 window, north | ditto |
| A-018 | `openings[7]` | 150 window, west | ditto |
| A-019 | `openings[12]` | 150 window, north upper | upper north undescribed; on the service-door vertical |
| A-020 | `openings[13]` | 150 window, north upper | ditto |
| A-021 | `openings[14]` | 150 window, east upper | stacked on A-016 |
| A-022 | `openings[15]` | 150 window, west upper | stacked on A-018 |

**7 of the 22 are openings on elevations the brief never described** (A-016 … A-022, one per
undescribed `(elevation, level, bay)` slot, minus the core-wall bay which deliberately stays blank). That
is the expected signature of a short brief, and each entry's `reason` names the silence
— *"The brief describes the south elevation only"* — rather than restating the number, as `07` §6.1
requires. If the user prefers blank elevations, this is the set to reverse.

### 5.7 Step 6 — emit

| File | Result |
|---|---|
| `examples/dimensions.json` | 269 lines, 16 openings, 4 facades, 2 levels, 2 plates. `origins` has 70 entries covering every leaf once. |
| `examples/conflicts_resolved.json` | 5 conflicts; `precedence_rules.rules` holds R1–R6, with R7 in `non_conflict_fallback` so the ladder cannot reach it. |
| `examples/assumptions.json` | 22 assumptions + `cross_references.conflict_sourced_paths` listing the 7 conflict-sourced paths. |

`assumptions.json.cross_references.conflict_sourced_paths` is the reader's map of the seven paths whose
origin is `conflict`: the two `levels[].height_cm`, `openings[11]`, `structure.x_bay_cm`,
`roof.parapet_height_cm`, and the two `floor_plates[].thickness_cm`. Seven paths, five conflicts —
C-001 and C-005 each own two.

### 5.8 Step 7 — the checks that actually load-bear

| Invariant | Check | Value |
|---|---|---|
| G-18 | level chain | 0 + 420 = **420**, + 400 = **820** ✓ |
| G-19 | total height | `levels[1].elevation + levels[1].height` = 420 + 400 = **820** ✓ |
| G-20 | overall height | 820 + 90 = **910** ✓ |
| G-24 | grid spans footprint | Σ x = 4 × 450 = **1800**; Σ y = 2 × 450 = **900** ✓ |
| G-22 / G-23 | core inside, core on grid | vertices at x 1350/1800, y 0/450 — all grid lines, all inside ✓ |
| G-25 | facades close | 4 × 450 = 1800; 2 × 450 = 900 ✓ |
| G-26 | openings sane | worst case: `openings[3].head_cm` 400 ≤ 420 ✓; `openings[11].head_cm` 340 ≤ 400 ✓ |
| G-27 | openings fit their bay **strictly** | the 420 curtain wall in a 450 bay leaves a 15 cm pier each side ✓ |
| G-28 | no duplicate host | no two openings share `(facade, level_index, bay_index)`; the core-wall bay carries none ✓ |
| G-29 | areas | 162 / 324 / 283.5 all reconcile; `net_usable_area_m2` 138 ≤ 141.75 ✓ |
| G-33 | tolerances | `linear_cm` 0.5, `area_m2` 0.05, `angle_deg` 0.01 present ✓ |

The two imperfections in the example are **recorded, not hidden**: the 20 cm vs 60 cm spandrel asymmetry
(C-002's `downstream_effect`) and `net_usable_area_m2` at 138 rather than the 141.75 that
gross-minus-core gives (A-010, A-011). A worked example with no imperfections in it teaches the wrong
lesson.

---

## 6. S1 done checklist

Run before declaring the input stage complete. Anything unticked means `status` stays `draft` (G-4) and
no downstream stage may consume the file.

### 6.1 Source and provenance

- [ ] `source.kind` ∈ {`user_brief`, `drawing`, `image`, `imported`, `assumed`}; `source.reference` names the actual artefact; `source.recorded_at` is ISO-8601 (G-6).
- [ ] Every kept fact has an addressable ref (Step 1), and every ref in the ledgers points back to one.
- [ ] **No value from an image or sketch is `origin: "given"`.** Every such value has an `A-nnn` with a confidence and a scale source (G-9, G-10).
- [ ] No value was averaged from two disagreeing sources.

### 6.2 Units

- [ ] `units.length == "cm"`, `units.angle == "deg"` (G-5).
- [ ] Every conversion applied and stored to 0.1 cm; no millimetre value left unconverted.
- [ ] Every length key ends `_cm`, every area `_m2`, every angle `_deg` (G-8).
- [ ] The spec says cm; the scene's unit scale is **read and recorded**, and any script converts at the boundary rather than editing the spec (`09` §6).

### 6.3 Geometry arithmetic

- [ ] `levels` is bottom-to-top, `index == array position`, elevations strictly increase (G-17).
- [ ] The level chain closes at ±0.5 cm, and every derivation is `derived` with `derives_from` (G-18, G-32).
- [ ] `total_height_cm`, `overall_height_cm`, `gross_floor_area_m2`, `net_floor_area_m2` recompute exactly (G-19, G-20, G-29, G-32).
- [ ] Polygons are simple, non-duplicated, winding declared and confirmed (G-21).
- [ ] The core is inside the footprint and every core vertex sits on a grid line (G-22, G-23).
- [ ] `Σ x_bay_cm == footprint_width_cm` and `Σ y_bay_cm == footprint_depth_cm` (G-24).
- [ ] Facades close: `bay_count == len(bay_width_cm)`, `Σ == length_cm` (G-25).
- [ ] Every opening: `head_cm ≤ levels[].height_cm`, `sill_cm ≥ 0`, `width_cm` **strictly** less than its bay, inside the bay's cumulative span (G-26, G-27).
- [ ] No duplicate `(facade, level_index, bay_index)`; every `bay_index < bay_count` (G-28).
- [ ] Roof is consistent: `deck_level_cm == total_height_cm` (G-30).

### 6.4 Ledgers

- [ ] Every leaf in the value tree has exactly one `origins` entry; arrays are one leaf; mixed-origin elements are per-leaf (G-9).
- [ ] `given` and `derived` entries have **no** `origin_ref`; `assumed` and `conflict` have one that resolves (G-10).
- [ ] Ledger ids match `^[AC]-\d{3}$`, are unique and ascend; `A-` only in `assumptions.json`, `C-` only in `conflicts_resolved.json` (G-11).
- [ ] Every ledger entry's `value` equals the spec's value at `field_path` (G-12).
- [ ] Every `assumed` / `conflict` path is covered by exactly one entry and every entry names one existing path (G-13).
- [ ] Each conflict: ≥ 2 `sources`, ≥ 1 `rejected` naming the beating rule, `invariant_violated_if_unresolved` naming a real `G-`, `resolution.chosen_value` equal to the value at `resulting_value_of` (G-14).
- [ ] **No `R7` in any `rules_invoked`**; ids ascending; `rule_names_as_proposed` mirrors `rules_invoked` (G-14).
- [ ] Each assumption: `reason` naming the silence, `confidence` ∈ {high, medium, low}, `invalidated_by`, `recheck_stage` in `P3`…`P6` (G-15 — **narrowed 2026-10-06; `P7`…`P9` were cancelled and now FAIL**).
- [ ] `assumptions.json.cross_references` carries **no** `A-` ids.
- [ ] Every `origin_ref`, `conflict_ref` and `resolved_paths` entry resolves across the three files, and every `field_path` exists in `dimensions.json` (G-31).

### 6.5 Judgement

- [ ] Every item on the **never infer** list (§4) is either stated by the input or escalated — none was quietly produced.
- [ ] Every code-driven row used is recorded as code-driven, with **no invented clause number or citation** anywhere in the three files.
- [ ] Every default consumed names a row in `09-defaults.md`, and its value lands inside `07`'s declared range for that key.
- [ ] Every `R6` resolution states in its own `resolution.statement` that `R1`–`R5` did not discriminate.
- [ ] Every open escalation is listed to the user, and `status` is `draft` while one is open (G-4).
- [ ] The report distinguishes `derived` figures (quotable, G-32) from `assumed` figures (**not** quotable).
- [ ] `python -m py_compile scripts/*.py` — ✅ exists, and remains the only test in the repo until P2c lands.