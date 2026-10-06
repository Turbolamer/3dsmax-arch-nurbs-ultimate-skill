# 09 — Architectural Defaults

> **Purpose:** the authoritative table of default values used whenever the input is silent — storey
> heights, slabs, roofs, walls, openings, guards, cores, facade modules, site elements and clearances.
> Every row states its key, value, acceptable range, unit, source basis and the `A-nnn` ledger slot it
> consumes when applied. `07-spec-grammar.md` owns the schema and the `G-*` invariants; this file owns
> the **values**. `10-conflict-resolution.md` owns `R1`–`R7`; `R7` (DEFAULT-FILL) points here.
>
> **No 3ds Max in §3.** No value in §3 was read off a live probe. The **only** place this file touches
> 3ds Max is §6, the unit-configuration requirement — which was **UNVERIFIED when P2 wrote it and was
> verified by live probe at P3** (`units.SystemType == #centimeters`, `SystemScale 1.0`). Everything here
> is convention and engineering judgement, and every code-driven row says so rather than inventing a
> citation.

---

## 1. What a default is, and what it is not

| A default **is** | A default **is not** |
|---|---|
| A recorded **assumption**. Every use creates an `A-nnn` entry in `assumptions.json` with a `reason` naming the silence it fills, a `confidence`, an `invalidated_by` and a `recheck_stage`. | A fact. It was never stated by the user, so it carries no authority over a later stated value. |
| A **range plus a chosen value**. The range is the convention; the number written into the spec is *this project's* choice out of that range, and `alternatives_considered` records why. | The midpoint, automatically. If a row lists 300–400, applying the default still requires a decision and a reason. |
| **Overridable by input**, always, with no argument needed. A stated value is `origin: "given"`. | A floor on what the user may ask for. A brief demanding 5 cm slabs does not get overridden by this file; it gets escalated (§5, `10` §6). |
| **Scoped to a project type.** Read the preset table in §4 — a retail podium and a pavilion do not share a storey height. | Universal. A default from the wrong preset is an error even when the value looks plausible. |
| **Named in the spec.** A default that cannot be traced to a row and an `A-nnn` id does not exist. | A licence to skip the ledger. G-9, G-10, G-12 and G-13 will block the file. |

**`R7` boundary.** A default fills a **silence**. It never decides a **conflict**. If a value is
merely absent, the instrument is `assumptions.json`; if two statements disagree, it is
`conflicts_resolved.json` and the `R1`–`R6` ladder decides. Putting a default in a conflict entry is
forbidden by **G-14**.

---

## 2. How to read a row, and how a row becomes an `A-nnn`

| Column | Meaning |
|---|---|
| **Row id** | `D-xx`, a **documentation anchor only**. It is not a ledger id and the validator never sees it. It exists so `08-input-rules.md`, the agent prompt and a reviewer can all cite the same row. |
| **Key** | The `dimensions.json` dotted path, in the `07` key vocabulary. Every length ends `_cm` (G-8); areas end `_m2`; angles `_deg`. A row with no `dimensions.json` key says so and is marked *reference only*. |
| **Default** | The value to write when the input is silent and the preset selects it. |
| **Range** | Acceptable range. Where `07` §5 declares a range for the key, **the `07` range is the binding one** and this column may only be narrower, never wider — see §2.1. |
| **Basis** | `convention` · `span-rule` · `geometry` (a consequence of other values) · `rendering` (a visual-quality decision, safe to change) · `code-driven — verify` · `engineering — proxy only`. |
| **Ledger id** | `A-nnn` — allocate the next free id in the project's ledger when the row is applied. Where `pavilion-01` already consumed a row, the concrete id is shown so the worked example reconciles. |

### 2.1 Two hard limits on these tables

1. **`07`'s declared range wins.** G-16 is the validator. This file's bands are soft and advisory; they
   exist so a human can sanity-check a choice, exactly as `07` §11 states. If a row's range leaves the
   `07` range, the value cannot be written — see the KNOWN LIMITATION in §3.1 for the one case that
   actually bites (industrial clear heights).
2. **`A-nnn` is allocated by the input stage, never by this file.** Ids are project-scoped, unique and
   ascending (G-11). A default row does not own an id; it *consumes* the next free one when applied,
   and §7 shows that allocation for `pavilion-01`.

---

## 3. Default tables

### 3.1 Storey heights (`levels[].height_cm`) — floor-to-floor, **not** clear height

G-16 hard bound: `250 … 600` cm (`07` §5.6).

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-SH-01 | `levels[].height_cm` — residential | 300 | 280–330 | cm | convention — floor-to-floor incl. structure | `A-nnn` |
| D-SH-02 | `levels[].height_cm` — office | 380 | 360–400 | cm | convention | `A-nnn` · `pavilion-01` used **400**, which is `given`-by-conflict (**C-001**) — see note ↓ |
| D-SH-03 | `levels[].height_cm` — lobby / atrium / double-height | 480 | 420–600 | cm | convention | `A-nnn` · `pavilion-01` ground floor declared 420 as `given`-by-conflict **C-001** |
| D-SH-04 | `levels[].height_cm` — retail | 450 | 400–550 | cm | convention | `A-nnn` |
| D-SH-05 | `levels[].height_cm` — assembly (auditorium, hall) | 550 | 500–600 | cm | convention | `A-nnn` |
| D-SH-06 | `levels[].height_cm` — parking | 280 | 250–320 | cm | convention; often driven by clear height for vehicles + services | `A-nnn` |
| D-SH-07 | `levels[].height_cm` — industrial / shed | 600 | 500–600 | cm | **see KNOWN LIMITATION below** | `A-nnn` |
| D-SH-08 | `levels[].height_cm` — plant / mechanical only | 300 | 250–400 | cm | convention | `A-nnn` |
| D-SH-09 | `levels[0].elevation_cm` when the brief is silent | 0.0 | any | cm | convention — finished ground level at Z 0 | `A-nnn` · `pavilion-01`: `given`, brief stated 0 |
| D-SH-10 | *reference only* — clear headroom = `height_cm` − the plate below | — | — | cm | geometry; computed downstream, **never entered by hand** (`07` §5.6) | — |

> **KNOWN LIMITATION — industrial clear height.** A shed with 7–10 m clear height cannot be written as
> one `levels[]` entry: G-16 caps `height_cm` at 600 cm. The pipeline has no mezzanine or two-tier
> storey representation. Do **not** narrow G-16 (`07` §12 forbids it) and do **not** fake a 600 cm
> storey on a 9 m shed. Raise it with the user (`10` §6 E4) and split into a working level plus a
> `riser_shaft` / `plant` level if the programme allows; otherwise S1 cannot complete and the file
> stays `draft` (G-4).

> ↓ **Note on `pavilion-01`.** Its two storey heights — 420 (ground) and 400 (first) — are **not
> defaults**. They came from the brief and are `origin: "conflict"` under **C-001**. The ground-floor
> 420 sits in D-SH-03's band, not D-SH-02's, which is why `07` §5.6 notes the office band 360–400 is
> advisory for this project. No row in this table was consumed for them.

### 3.2 Slab and beam depths by span

Structural. **Basis `engineering — proxy only`** for every row: a span/depth ratio is a starting point
for a massing model, never a design. `10` §6 E1 governs — see §5.

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-SD-01 | `floor_plates[].thickness_cm` — ground plate on grade | 30 | 25–40 | cm | engineering — proxy only | `A-nnn` · `pavilion-01`: **C-005** (30 chosen from the brief) |
| D-SD-02 | `floor_plates[].thickness_cm` — suspended plate, span ≤ 450 | 20 | 15–25 | cm | engineering — proxy only | `A-nnn` |
| D-SD-03 | `floor_plates[].thickness_cm` — suspended plate, span 450–600 | 22 | 18–25 | cm | engineering — proxy only | `A-nnn` · `pavilion-01`: **C-005** (25 chosen from the brief) |
| D-SD-04 | `floor_plates[].thickness_cm` — suspended plate, span 600–750 | 25 | 22–30 | cm | engineering — proxy only | `A-nnn` |
| D-SD-05 | `floor_plates[].thickness_cm` — suspended plate, span 750–900 | 30 | 26–35 | cm | engineering — proxy only | `A-nnn` |
| D-SD-06 | `floor_plates[].thickness_cm` — suspended plate, span > 900 | 38 | 30–45 | cm | engineering — proxy only; beyond this, deepen or add beams | `A-nnn` |
| D-SD-07 | *reference only* — downstand beam depth by span (span/18) | span/18 | span/12 – span/24 | cm | engineering — proxy only; no `dimensions.json` key today (see §3.4 note) | `A-nnn` |
| D-SD-08 | *reference only* — edge / spandrel beam upstand at slab | 0 | 0–40 | cm | convention — zero for a flush slab edge, upstand where the facade needs cover | `A-nnn` |
| D-SD-09 | *reference only* — void allowance at slab edges for services | 10 | 0–20 | cm | convention | `A-nnn` |

G-16 range for `floor_plates[].thickness_cm` is **15–45**; every row above sits inside it.

### 3.3 Ground-floor and roof build-ups

**These are layered constructions. `dimensions.json` has no key for a layered build-up** — it carries a
single `thickness_cm` per plate and per roof deck. The rows below are therefore *reference only*: they
explain what a single `thickness_cm` figure is standing in for. Do not invent a nested key (`07` §12).
> **CORRECTED (verified 2026-10-06):** this paragraph previously said the rows *"inform later stages that
> build the layers (**P6 assembly, P7 materials**)"*. **No stage builds these layers.** Assembly (P6)
> places components and tiles wall cells; it does not resolve a build-up stack, and **P7 materials was
> cancelled on 2026-10-05** — materials are assigned by hand. The rows are **documentation of intent
> for a human**, full stop.

| Row | Layer (bottom → top) | Nominal | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-GB-01 | Ground slab — sub-base / hardcore | 15 | 10–30 | cm | convention | `A-nnn` |
| D-GB-02 | Ground slab — blinding / lean concrete | 5 | 3–8 | cm | convention | `A-nnn` |
| D-GB-03 | Ground slab — structural slab | 30 | 25–40 | cm | engineering — proxy only | `A-nnn` |
| D-GB-04 | Ground slab — screed / levelling | 5 | 3–8 | cm | convention | `A-nnn` |
| D-GB-05 | Ground slab — finish (tile, timber, vinyl) | 1 | 0.5–3 | cm | convention; 0 where the slab is the finished floor | `A-nnn` |
| D-GB-06 | Suspended slab — soffit lining / acoustic ceiling void | 5 | 0–15 | cm | convention | `A-nnn` |
| D-GB-07 | Suspended slab — services zone (bulkhead to soffit) | 15 | 10–35 | cm | convention | `A-nnn` |
| D-RF-01 | Roof — structural deck | 30 | 20–40 | cm | engineering — proxy only | `A-nnn` · `pavilion-01`: `given` from brief |
| D-RF-02 | Roof — insulation | 12 | 6–25 | cm | convention; **varies by climate and by code** | `A-nnn` |
| D-RF-03 | Roof — screed to falls / tapered insulation | 8 | 5–20 | cm | convention; required where `roof.slope_deg > 0` | `A-nnn` |
| D-RF-04 | Roof — waterproofing membrane | 1 | 0.3–2 | cm | convention | `A-nnn` |
| D-RF-05 | Roof — ballast / paving / green roof | 10 | 0–40 | cm | convention; 0 for a membrane roof | `A-nnn` |
| D-RF-06 | Roof — total build-up above `roof.deck_level_cm` | — | — | cm | geometry: `deck_level_cm` is the **top** of the build-up (`07` §5.9) — never double-counted | — |

### 3.4 Parapet, coping and roof form

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-PC-01 | `roof.parapet_height_cm` | 100 | 90–120 | cm | convention; **code-driven where the roof edge is an escape route or a fall edge** — verify | `A-nnn` · `pavilion-01`: **C-004** (90 from the brief) |
| D-PC-02 | `roof.parapet_thickness_cm` | 30 | 20–40 | cm | convention | `A-nnn` · `pavilion-01`: **A-013** (30) |
| D-PC-03 | `roof.coping_overhang_cm` | 3 | 2–5 | cm | rendering — a flat-topped parapet reads as a slab in render; keep a drip edge | `A-nnn` · `pavilion-01`: **A-014** (3) |
| D-PC-04 | *reference only* — coping material thickness | 5 | 3–10 | cm | convention | `A-nnn` |
| D-PC-05 | `roof.type` — flat with parapet | `flat_parapet` | `flat_parapet` \| `flat_balustrade` | — | convention for a non-residential small building | `A-nnn` |
| D-PC-06 | `roof.slope_deg` — flat roof fall to internal drainage | 2 | 1–3 | deg | convention; **the minimum practical fall and a local code figure both matter** — verify | `A-nnn` · `pavilion-01`: **A-012** (2) |
| D-PC-07 | `roof.slope_deg` — pitched roof (shed / gable / hip) | 15 | 10–45 | deg | convention; form-driven, `07` §5.9 declares 0–15 for the `slope_deg` key, so a steeper form needs a `pitched_*` type and the pitch is expressed by the geometry, not by this key | `A-nnn` |
| D-PC-08 | `roof.drainage` | `internal_downpipe` | `internal_downpipe` \| `external_downpipe` \| `flat_roof_outlet` | — | convention; drives D-PC-06 | `A-nnn` · `pavilion-01`: **A-015** (internal) |
| D-PC-09 | *reference only* — downpipe diameter per 100 m² of roof | 12 | 10–16 | cm | engineering — proxy only; sizing by rainfall intensity, which is not known here | `A-nnn` |

G-16 ranges: `parapet_height_cm` 60–150, `parapet_thickness_cm` 15–45, `coping_overhang_cm` 0–10,
`slope_deg` 0–15, `deck_thickness_cm` 15–45. Every applicable row sits inside them.

### 3.5 Wall thicknesses

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-WA-01 | `core.wall_thickness_cm` — RC core | 25 | 20–40 | cm | engineering — proxy only | `A-nnn` · `pavilion-01`: **A-007** (25) |
| D-WA-02 | `core.wall_thickness_cm` — lightweight / framed core | 15 | 10–20 | cm | convention | `A-nnn` |
| D-WA-03 | *reference only* — internal partition, lightweight | 10 | 7.5–15 | cm | convention | `A-nnn` |
| D-WA-04 | *reference only* — internal partition, masonry | 15 | 10–20 | cm | convention | `A-nnn` |
| D-WA-05 | *reference only* — external wall, lightweight infill panel | 20 | 15–30 | cm | convention | `A-nnn` |
| D-WA-06 | *reference only* — external wall, masonry cavity | 35 | 25–45 | cm | convention; **cavity width and insulation thickness are code/climate driven** — verify | `A-nnn` |
| D-WA-07 | *reference only* — spandrel panel / opaque panel zone at floor level | 60 | 20–100 | cm | convention; the spandrel is a rendering and thermal decision | `A-nnn` · `pavilion-01`: 20 ground (**given**), 60 upper (**C-002**) |
| D-WA-08 | *reference only* — parapet upstand matching wall thickness | 30 | 20–40 | cm | convention | `A-nnn` |
| D-FW-01 | *reference only* — modelled thickness of an opaque facade wall band | 20 | 10–40 | cm | geometry — the band is a massing proxy; a real build-up is a curtain-wall system schedule | `A-nnn` · `pavilion-01`: **A-025** (20) |

> **On `D-FW-01`'s id.** The prefix is `FW`, not `WA`, because the value is not a wall in the
> structure sense: it is the band `massing.json` builds per `(facade, level)` so that P6 has a
> `facade_wall` to cut each opening in. It lives here, in §3.5, because it is a thickness; it
> keeps its own prefix because `components_registry.json`'s two P5 defaults (`D-CL-05`,
> `D-FM-10`) set the precedent of one row per *file* that carries an assumed value rather than
> one row per structural family.

### 3.6 Openings

G-16 per-type ranges are fixed by `07` §5.11 and are the binding constraint. The table supplies the
convention *inside* those ranges.

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-OP-01 | `openings[].type` `window` — `width_cm` | 150 | 60–420 | cm | convention | `A-nnn` · `pavilion-01`: 180 south, 150 elsewhere (**given** / **A-016**…**A-022**) |
| D-OP-02 | `openings[].type` `window` — `sill_cm` | 90 | 0–150 | cm | convention | `A-nnn` |
| D-OP-03 | `openings[].type` `window` — `head_cm` | 270 | 150–350 | cm | convention; standard sill + standard opening height | `A-nnn` |
| D-OP-04 | `openings[].type` `window` — opening height (`head_cm` − `sill_cm`) | 180 | 120–300 | cm | geometry — `07` §5.11: both `sill_cm` and `head_cm` are measured from **this level's finished floor** | — |
| D-OP-05 | `openings[].type` `door` — `width_cm` | 90 | 80–150 | cm | convention — service, WC, plant | `A-nnn` · `pavilion-01`: 110 (**given**) |
| D-OP-06 | `openings[].type` `door` — `head_cm` | 210 | 180–260 | cm | convention; **code-driven where the door is on an escape route** — verify | `A-nnn` · `pavilion-01`: 220 (**given**) |
| D-OP-07 | `openings[].type` `entrance` — `width_cm` | 180 | 120–300 | cm | convention; one per building (`07` §5.11) | `A-nnn` · `pavilion-01`: 200 (**given**) |
| D-OP-08 | `openings[].type` `entrance` — `head_cm` | 240 | 200–320 | cm | convention | `A-nnn` · `pavilion-01`: 260 (**given**) |
| D-OP-09 | *reference only* — maximum glazed width without a mullion (single pane / single light) | 120 | 100–150 | cm | convention; the commercial figure of ~150 is glass- and frame-dependent and the limit is a hardware question, not an aesthetic one | `A-nnn` |
| D-OP-10 | *reference only* — maximum glass pane area without a transom | 250×250 | 150×150 – 300×300 | cm | convention; 250×250 is the usual large-format limit | `A-nnn` |
| D-OP-11 | `openings[].type` `curtain_wall` — `width_cm` | `bay_width_cm` − 2 × pier | 100–600 | cm | geometry — must be **strictly less** than the host bay (G-27); the natural maximum is `bay − 2 × pier` | `A-nnn` · `pavilion-01`: 420 in a 450 bay (**given**) |
| D-OP-12 | *reference only* — curtain-wall pier / mullion width each side | 15 | 10–25 | cm | convention | `A-nnn` |
| D-OP-13 | *reference only* — curtain-wall spandrel zone (`sill_cm`) | 20 | 0–100 | cm | convention | `A-nnn` |
| D-OP-14 | *reference only* — stair headroom, clear, measured on the pitch line | 210 | 200–240 | cm | **code-driven — verify against the governing local code; do not treat as free.** At least the head height of a door, and often more on a pitch. | `A-nnn` |
| D-OP-15 | *reference only* — corridor / circulation soffit height | 240 | 210–270 | cm | convention; must exceed D-OP-14 + any beam or duct soffit | `A-nnn` |
| D-OP-16 | *reference only* — window head to the underside of the plate above | 30 | 20–60 | cm | convention — hiding head, services and deflection | `A-nnn` |

### 3.7 Guards, railings and balustrades

**Every row in this table is code-driven and varies materially by jurisdiction, by occupancy and by
the height of the drop below. They are recorded so the agent knows the order of magnitude and knows to
ask — not so it can answer.** `10` §6 E2 and E8 apply.

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-GU-01 | *reference only* — guard height, residential, low drop | 90 | 90–110 | cm | **code-driven — verify; a drop under a stated threshold is often treated differently from a greater one** | `A-nnn` |
| D-GU-02 | *reference only* — guard height, public / assembly / roof edge | 110 | 100–120 | cm | **code-driven — verify** | `A-nnn` |
| D-GU-03 | *reference only* — guard height, where a child could climb it | 110 | 100–130 | cm | **code-driven — verify; climbable-element provisions often raise the minimum** | `A-nnn` |
| D-GU-04 | *reference only* — balustrade height, internal stair / mezzanine floor edge | 100 | 90–110 | cm | **code-driven — verify** | `A-nnn` |
| D-GU-05 | *reference only* — max unguarded opening between balusters | 10 | 8–12 | cm | **code-driven — verify; a sphere-probe limit is the usual test** | `A-nnn` |
| D-GU-06 | *reference only* — handrail height above pitch line | 90 | 85–100 | cm | **code-driven — verify; a second lower rail is common where children are present** | `A-nnn` |
| D-GU-07 | *reference only* — guard/balustrade top rail member thickness | 5 | 3–8 | cm | rendering | `A-nnn` |

### 3.8 Core and circulation minimums

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-CR-01 | `core.type` | `lift_stair_wc` | `lift_stair_wc` \| `stair_only` \| `lift_only` \| `riser_shaft` | — | convention — the minimum that makes a multi-storey building with a stair servable | `A-nnn` · `pavilion-01`: **A-005** |
| D-CR-02 | *reference only* — lift car, small (8 persons) internal dimensions | 110×140 | 100×140 – 160×180 | cm | engineering — supplier dependent; a car is not authored by this pipeline | `A-nnn` |
| D-CR-03 | *reference only* — dog-leg stair, flight width (clear, per flight) | 110 | 100–140 | cm | convention | `A-nnn` |
| D-CR-04 | *reference only* — stair total width, dog-leg including the well | 220 | 200–280 | cm | geometry — two flights + well | `A-nnn` |
| D-CR-05 | *reference only* — stair riser / tread | 17 / 30 | riser 15–18, tread 28–32 | cm | **code-driven — verify; the governing rule is usually a riser+tread relationship, not either number alone** | `A-nnn` |
| D-CR-06 | *reference only* — stair landing depth, equal to the flight width | 110 | 100–140 | cm | convention | `A-nnn` |
| D-CR-07 | *reference only* — egress travel route clear width (corridor) | 120 | 100–180 | cm | **code-driven — verify; depends on occupant load and on whether the width may be measured between handrails or between walls** | escalate — see §5 |
| D-CR-08 | *reference only* — escape stair width | 120 | 100–200 | cm | **code-driven — verify; do not assume** | escalate — see §5 |
| D-CR-09 | *reference only* — corridor clear width, general circulation (non-escape) | 120 | 100–180 | cm | convention | `A-nnn` |
| D-CR-10 | *reference only* — corridor clear width, secondary / service | 90 | 75–120 | cm | convention | `A-nnn` |
| D-CR-11 | *reference only* — accessible WC footprint | 160×220 | 150×200 – 200×250 | cm | **code-driven — verify; door approach and turning space usually govern the enclosing room, not the WC itself** | escalate — see §5 |
| D-CR-12 | *reference only* — accessible turning circle | 150 | 120–150 | cm | **code-driven — verify** | escalate — see §5 |
| D-CR-13 | *reference only* — riser shaft footprint (small, per riser) | 60×25 | 50×25 – 100×40 | cm | convention | `A-nnn` |

### 3.9 Facade module and mullion spacing

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-FM-01 | `structure.x_bay_cm` / `y_bay_cm` — office / commercial | 450 | 360–900 | cm | convention; G-16 requires each bay in **300–1200** and `Σ x_bay_cm == site.footprint_width_cm` (G-24) | `A-nnn` · `pavilion-01`: 450 long axis (**given**), **[450, 450]** short axis (**A-003**) |
| D-FM-02 | `structure.x_bay_cm` / `y_bay_cm` — residential | 420 | 330–600 | cm | convention | `A-nnn` |
| D-FM-03 | `structure.x_bay_cm` / `y_bay_cm` — retail (wants a long frontage) | 750 | 600–1200 | cm | convention | `A-nnn` |
| D-FM-04 | `structure.x_bay_cm` / `y_bay_cm` — industrial / shed | 900 | 600–1200 | cm | convention; long clear spans, deep beams | `A-nnn` |
| D-FM-05 | `facades[].bay_width_cm` — derived from the structural grid | — | 300–1200 | cm | geometry — **derived, never a default.** `07` §5.10 and G-25/G-32 | — |
| D-FM-06 | `facades[].bay_width_cm` — a bay split at one intermediate mullion | `bay / 2` | — | cm | convention, only where the user asked for a finer facade rhythm than the grid; this is an **R5 MODULE-ALIGNMENT** matter, not a free default — see `10` §4 | `A-nnn` |
| D-FM-07 | *reference only* — vertical mullion spacing in a curtain wall | 120 | 100–150 | cm | convention; equals D-OP-09 | `A-nnn` |
| D-FM-08 | *reference only* — horizontal transom spacing, one per floor at the spandrel line | 1 per storey | — | count | convention | `A-nnn` |
| D-FM-09 | *reference only* — window spacing in a punched elevation, equal to the bay | bay | — | cm | convention; align openings to column lines, never to a module you invented | `A-nnn` |
| D-FM-10 | *reference only* — facade panel joint width | 2 | 1–4 | cm | rendering — a visible joint keeps adjacent panels from z-fighting in render | `A-nnn` |

### 3.10 Site and exterior elements

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-ST-01 | `site.setback_cm` | 300 | 300–3000 | cm | convention — room for paving, planting and a site pad; `07` §5.4 declares 0–3000 | `A-nnn` · `pavilion-01`: **A-002** (300) |
| D-ST-02 | `site.plot_rotation_deg` | 0.0 | −180…180 | deg | convention — axis-aligned is the honest default when no orientation is given | `A-nnn` · `pavilion-01`: **A-001** (0) |
| D-ST-03 | `site.plot_rotation_ref_axis` | `north` | `north` \| `true_north` \| `grid_north` | — | convention; **if the site matters, this must come from the user** (`10` §6 E9) | `A-nnn` |
| D-ST-04 | `site.ground_level_cm` | 0.0 | any | cm | convention — finished ground level at Z 0 | `A-nnn` |
| D-ST-05 | *reference only* — footpath / sidewalk width | 180 | 150–300 | cm | convention; a local minimum often governs | `A-nnn` |
| D-ST-06 | *reference only* — kerb height above the road | 12 | 12–15 | cm | convention | `A-nnn` |
| D-ST-07 | *reference only* — kerb width | 15 | 15–20 | cm | convention | `A-nnn` |
| D-ST-08 | *reference only* — road lane width | 325 | 300–350 | cm | convention; regional | `A-nnn` |
| D-ST-09 | *reference only* — accessible route clear width (site) | 120 | 90–180 | cm | **code-driven — verify; whether a passing place is required, and at what interval, is a local figure** | escalate — see §5 |
| D-ST-10 | *reference only* — ramp gradient | 1:20 | 1:12 – 1:20 | ratio | **code-driven — verify** | escalate — see §5 |
| D-ST-11 | *reference only* — ramp landings, level rest | 150 | 120–180 | cm | **code-driven — verify** | escalate — see §5 |
| D-ST-12 | *reference only* — soffit height over a footpath | 240 | 210–300 | cm | convention | `A-nnn` |
| D-ST-13 | *reference only* — ceiling height, habitable room (finished floor to finished ceiling) | 270 | 240–300 | cm | convention; regional and use-specific | `A-nnn` |
| D-ST-14 | *reference only* — ceiling height, service / back-of-house | 240 | 210–270 | cm | convention | `A-nnn` |
| D-ST-15 | *reference only* — exterior steps, riser / tread | 15 / 32 | 10–18 / 28–35 | cm | convention; **the rise/tread relationship is a code figure** — verify | `A-nnn` |

### 3.11 Clearances, tolerances and modelling conventions

| Row | Key | Default | Range | Unit | Basis | Ledger id |
|---|---|---|---|---|---|---|
| D-CL-01 | `tolerances.linear_cm` | 0.5 | 0.1–1.0 | cm | grammar — `07` §3.3, G-18, G-33. Fixed by the grammar; listed here so the value is not mistaken for a free choice | — |
| D-CL-02 | `tolerances.area_m2` | 0.05 | 0.01–0.5 | m² | grammar — `07` §3.3 | — |
| D-CL-03 | `tolerances.angle_deg` | 0.01 | 0.001–0.1 | deg | grammar — `07` §3.3 | — |
| D-CL-04 | *reference only* — minimum gap between two separate solids to avoid z-fighting | 0.5 | 0.2–2 | cm | rendering | `A-nnn` |
| D-CL-05 | *reference only* — minimum modelled thickness for a facade panel or reveal | 3 | 2–8 | cm | rendering; a paper-thin panel renders as a hole | `A-nnn` |
| D-CL-06 | *reference only* — chamfer on hard arrises (concrete, metal) | 1 | 0.3–2 | cm | rendering — a hard arris never catches light | `A-nnn` |
| D-CL-07 | *reference only* — shadow-catching ground pad half-extent beyond the footprint | 2000 | 1000–5000 | cm | rendering | `A-nnn` |
| D-CL-08 | *reference only* — eye level for an architectural viewpoint | 170 | 160–180 | cm | rendering | `A-nnn` |
| D-CL-09 | *reference only* — nominal overlap between adjacent solid cells of a tiled wall, as a fraction of cell depth | 0 | 0 – 0.25 | ratio | geometry — keeps a shared cell boundary from leaking light, and guarantees neighbouring cells interpenetrate rather than abutting on a float tolerance | — |
> **CORRECTED (verified 2026-10-06):** this row previously read *"overlap for a **boolean cut**, cutter
> depth vs host thickness — the cutter must pierce both faces of the host"*, with a default of `2 ×` and a
> range of `≥ 1.5 ×`. **There is no cutter and there is no boolean.** The `Boolean` modifier is unusable in
> this build; a wall with openings is built by **tiling it with solid cells** (`wall_cells[]` in
> `assembly.json`, decomposed along the run axis at each opening's `u` boundary then the `v` boundaries per
> column — `07` §8.5.8). So the quantity that matters is the overlap between *adjacent solid cells of one
> wall*, not the overshoot of a cutting solid through a host. The ratio is restated in those units above; the
> `A-nnn` ledger id is unchanged and still applies.
| D-CL-10 | *reference only* — minimum vertical separation between two facade openings to keep a legible band | 30 | 20–60 | cm | rendering | `A-nnn` |

**Regional variation, stated plainly.** D-GU-01…D-GU-06 (guard and handrail heights),
D-CR-05 / D-CR-07 / D-CR-08 / D-CR-11 / D-CR-12 (stair, egress, accessible), D-ST-06 / D-ST-09 / D-ST-10
/ D-ST-11 / D-ST-15 (kerb, accessible route, ramp, steps) and the insulation layer in D-RF-02 are
**jurisdiction-specific and cannot be responsibly generalised.** This file records the order of
magnitude so the agent knows what question to ask. It does not choose a jurisdiction, and it cites no
clause, because citing a clause from memory is exactly the failure that `10` §3.1 forbids under `R1`.

---

## 4. Project-type presets

A preset selects which defaults apply. Everything not selected is *not* defaulted — it is either asked
or left as an assumption with `confidence: "low"` and a stated `invalidated_by`.

| Preset | Storey heights | Slabs | Roof | Facade module | Openings | Site | Characteristic rows |
|---|---|---|---|---|---|---|---|
| **Small office / pavilion** | D-SH-02, D-SH-03 | D-SD-01, D-SD-02/03 | D-PC-01…05, D-PC-06, D-PC-08 | D-FM-01 (450) | D-OP-01…03, D-OP-07/08, D-OP-11 | D-ST-01…04 | `pavilion-01` is exactly this preset |
| **Retail podium** | D-SH-04 (retail) at ground, D-SH-02 above | D-SD-04/05 (longer spans) | D-PC-01, D-PC-05, D-PC-08 | D-FM-03 (750) | D-OP-11 curtain wall at ground, D-OP-01…03 above | D-ST-05, D-ST-09 | ceiling voids are the design driver; confirm the retail `use` before applying anything |
| **Residential slab** | D-SH-01 | D-SD-02/03 | D-PC-01, D-PC-05, D-PC-08 | D-FM-02 (420) | D-OP-01…03, D-OP-05/06, D-OP-14 | D-ST-01, D-ST-05 | **D-GU-01…04 apply** — code-driven, must be asked; core type and every `use` per storey must be asked |
| **Industrial shed** | D-SH-07 | D-SD-05/06, D-SD-07 | D-PC-05, D-PC-07 (pitched), D-PC-09 | D-FM-04 (900) | D-OP-05 (roller / service door), D-OP-16 | D-ST-01, D-ST-08 | **hits the KNOWN LIMITATION in §3.1** if clear height > 600 cm — escalate, do not fake it |
| **Pavilion / single-volume** | D-SH-03 (one storey, tall) | D-SD-01 | D-PC-05, D-PC-06 | D-FM-01 or a single wide bay | D-OP-11 curtain wall, D-OP-09 | D-ST-01…04 | also `10`'s worked case for `R7`; often no `structure` intent at all — ask before defaulting a grid |

| Rule | Detail |
|---|---|
| `small office` vs `pavilion` | Same defaults; the difference is one storey, not a different table. A pavilion with one 480 cm storey is D-SH-03 only. |
| Multi-typology projects | Apply per-storey uses, not per-project. `levels[].use` selects the row; a retail ground under offices takes D-SH-04 and D-SH-02. |
| A preset never widens authority | Selecting a preset does not upgrade a `low` confidence. `pavilion-01` is a full low-confidence project and is a correct, accurate file for what it is. |

---

## 5. Do-not-default list

An agent **must never invent** any of the following silently. Each is either a question for the user or
a hard `escalate` per `10` §6.

| # | Value | Why | Correct instrument |
|---|---|---|---|
| 1 | **Structural system** — material, framing type, load paths, foundations | Licensed engineer's scope. A wrong system invalidates massing, NURBS and every clearance. | Ask (`10` §6 E1). A *proxy* dimension with `confidence: "low"` and `recheck_stage: "P3"` is the limit — see the note below. |
| 2 | **Structural sizing** — member sizes, slab thickness beyond D-SD-01…06, reinforcement | Same. The span tables are starting points for a massing model, not a design. | Ask. `A-004` / `A-007` are the accepted shape of a proxy assumption. |
| 3 | **Fire rating, compartmentation, fire separation, sprinklers, alarms** | Life safety and code-driven; `R1` cannot be applied from memory. | Ask (`10` §6 E2). |
| 4 | **Egress** — exit count, widths, travel distance, stair provision, door swing, panic hardware, accessible egress | Life safety and code-driven. D-CR-07, D-CR-08, D-CR-11, D-CR-12 are marked escalate. | Ask (`10` §6 E2). |
| 5 | **Guard and handrail heights** — D-GU-01…06 | Code-driven, jurisdiction-specific, and conditional on occupancy and drop height. | Ask (`10` §6 E2, E8). |
| 6 | **Cost, rate, budget** | No key exists for it and a number that reaches a client is a commitment. | Ask (`10` §6 E3). Do not compute. |
| 7 | **Area figures to be quoted** — GFA, NFA, usable area | `gross_floor_area_m2` and `net_floor_area_m2` are `derived` (G-32) and safe to state as *derived*. `net_usable_area_m2` is `assumed` and is **not** quotable until confirmed. | State the label. Ask before quoting (`10` §6 E3). |
| 8 | **Site address, coordinates, true orientation, plot boundary** | A real-world fact the agent cannot verify. `A-001` records 0° as a *modelling convention*, not the site's true bearing. | Ask (`10` §6 E9, E4). |
| 9 | **Heritage / conservation constraints** | Imposed by an authority the agent cannot see. | Ask (`10` §6 E7). |
| 10 | **Client or authority requirements of any kind** | Same. | Ask (`10` §6 E7). |
| 11 | **Anything a licensed professional must sign off** | The general case that items 1–5 instantiate. | Ask, and say in the handoff that it needs sign-off. |

> **On item 1's proxy allowance.** `pavilion-01` defaults `structure.column_section_cm` to `[40, 40]`
> (**A-004**, `confidence: "low"`, `recheck_stage: "P3"`) and `core.wall_thickness_cm` to `25`
> (**A-007**, same). That is permitted because `dimensions.json` has no *optional* way to leave them
> unset and the schema is prismatic — not because structural sizing is an agent's call. The boundary:
> **a placeholder value with `confidence: "low"`, an `invalidated_by` that names an engineer, and a
> `recheck_stage` of P3 is acceptable; anything presented as a design value is not.** The *system*
> itself is never defaulted — `pavilion-01`'s `structure.system` is `given` because the brief stated it.

---

## 6. 3ds Max unit configuration — required, and now VERIFIED

> **Status change, P3 (2026-10-04).** This section was UNVERIFIED when P2 wrote it. A live probe has since
> run; the rows below now carry their evidence. The rule itself has not changed — only what we know.

| Statement | Status |
|---|---|
| This pipeline's spec unit is the **centimetre** (`07` §2), and the pipeline authors geometry in centimetres. | design decision, `07` §2 |
| The probed scene runs `units.SystemType == #centimeters` with `units.SystemScale == 1.0`, so a spec value in cm reaches Max **unchanged**. | ✅ **verified by live execution** — `units.SystemType` → `centimeters`, `units.SystemScale` → `1.0`, and `units.SystemType == #centimeters` is `true` while `#meters`, `#millimeters`, `#inches`, `#feet`, `#decimeters` are all `false` |
| 3ds Max's unit *display* setting changes how numbers are **labelled**, not the geometry. | ⚠️ still **unverified** for this installation — the probe read `SystemType`/`SystemScale`, not the display units |
| Therefore the spec states cm, and any script that ever writes geometry in another unit **must convert at the boundary**. | the rule this pipeline follows regardless |

**Reading the unit back.** `getProperty units #SystemType` **fails** in Max 2026 — read the members
directly: `units.SystemType`, `units.SystemScale`, `units.DisplayType`, `units.USType`, `units.MetricType`.
`units` is a struct, and `units.SystemRotation` does not exist.

**Operational rule — unchanged, and now confirmed satisfiable.** Two numbers must agree before any
geometry is built:

1. the spec's declared unit (`dimensions.json` → `units.length == "cm"`, G-5), and
2. the scene's system unit, read once and recorded.

If they disagree, **convert at the script boundary** — never by editing the spec. The spec is cm by
contract; the scene is whatever the user's file already is. Changing a user's existing `Units Setup`
silently is a modification they did not ask for. The P3 build confirms the agreement case end-to-end:
`build_spec.py` emits `Box(width:1800, …)` and the node measures 1800 cm, with **no conversion anywhere in
the builder**.

---

## 7. How a row becomes an `A-nnn` — worked, from `pavilion-01`

`A-nnn` allocation is in the order the defaults are applied, which is the order of §3, skipping rows
the brief already answered. This is the reconciliation with `examples/assumptions.json`:

| Row | Field path | Ledger id | Value | Why a default at all |
|---|---|---|---|---|
| D-SH-01, D-SH-03 | `levels[0].height_cm`, `levels[1].height_cm` | — | 420 / 400 | **Not defaults.** Stated by the brief; conflict-resolved by **C-001**. No row consumed. |
| D-FM-01 | `structure.y_bay_cm` | **A-003** | `[450, 450]` | Brief gives the 450 grid on the long elevation only. Short direction uses the same module. |
| D-SD-01 | `structure.column_section_cm` | **A-004** | `[40, 40]` | No column size given. `confidence: low`, `recheck_stage: P3` — the §5 proxy allowance. |
| D-CR-01 | `core.type` | **A-005** | `lift_stair_wc` | "A service core" without enumeration. |
| D-PC-01, D-PC-02 | `roof.parapet_height_cm`, `roof.parapet_thickness_cm` | **C-004**, **A-013** | 90 / 30 | Height was a conflict, not a silence; thickness was a silence. |
| D-PC-06, D-PC-08, D-PC-03 | `roof.slope_deg`, `roof.drainage`, `roof.coping_overhang_cm` | **A-012**, **A-015**, **A-014** | 2, `internal_downpipe`, 3 | Brief says "parapet roof" with no drainage. |
| D-ST-01, D-ST-02 | `site.setback_cm`, `site.plot_rotation_deg` | **A-002**, **A-001** | 300, 0.0 | No plot boundary, no orientation. |
| D-OP-01…03 | `openings[4]`, `[6]`, `[7]`, `[12]`…`[15]` | **A-016**…**A-022** | 150 × 90…270 | Brief describes the south elevation only. |

Read the shape: **7 of the 22 assumptions are openings on elevations the brief never described.** That
is the expected signature of a short brief, and every one of those entries carries a
`reason` that names the silence ("The brief describes the south elevation only") rather than restating
the value — which is what `07` §6.1 requires.

**Cross-check.** `A-004` [40, 40] sits inside G-16's optional `column_section_cm` range 20–80;
`A-003`'s bays are 450, inside G-16's 300–1200; `A-012` 2° inside `slope_deg` 0–15; `A-013` 30 and
`A-014` 3 inside 15–45 and 0–10; `A-002` 300 inside `setback_cm` 0–3000. Every default a project
consumes must land inside `07`'s declared range or it is not a default — it is a conflict or a question.