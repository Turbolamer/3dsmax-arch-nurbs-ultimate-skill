# AGENT_BRIEF_stepped_massing.md — Stepped Massing, Setback Tiers & Tectonic Pilasters (Schema 1.1 Extension)

> **Mission:** Extend the `3dsmax-arch-nurbs-ultimate` pipeline under `schema_version: "1.1"` so that stages S1 (`dimensions.json`), S2 (`massing.json` / `build_spec.py`), S4 (`facade_grids.json` / `facade_tables.py`), S5 (`assembly.json` / `place_components.py`), and S7 (`qa_check.py`) natively build **stepped skyscrapers, podiums, and setback crowns** (e.g., Art Deco towers with `2800 -> 2400 -> 1600 -> 800 cm` tier setbacks) while keeping **100% backwards compatibility** with prismatic buildings (`examples/pavilion-01`).

---

## 0. Non-Negotiable Guardrails

1. **Follow `references/07-spec-grammar.md` §12 (All 6 Steps):**
   Every schema extension must simultaneously update: (1) schema tables in `07-spec-grammar.md`, (2) `G-*` invariants in `07` §9, (3) `scripts/validate_specs.py`, (4) `origins` provenance rules, (5) stage agent contracts (`agents/max-*.md`), and (6) verification fixtures.
2. **Zero regression on `examples/` (`pavilion-01`):**
   - `schema_version: "1.0"` files and `"1.1"` prismatic files without per-level footprints must behave **identically** to current behaviour.
   - `python scripts/validate_specs.py --dir examples --warnings-as-errors` must continue to exit `0` (`FAIL 0 / WARN 0`).
3. **Preserve S5 Mechanism A & Zero-Modifier Law (`G-81`):**
   - No Boolean modifiers. Stepped facade walls (`facade_wall`) are still tiled into solid `WAL_` boxes by `place_components.py` and hidden via `host_node.isHidden = true`.
4. **Preserve Native Scene Units Boundary (`scene_units.py`):**
   - All new geometry coordinates and lengths remain canonical `_cm` in JSON specs and scale via `c = k * s` (`f = 1/c`) in emitted MAXScript.

---

## 1. Architectural Design: How Stepped Massing Works Across S1 → S5

In a prismatic building (`pavilion-01`), every floor plate equals `site.footprint_cm`, and all 4 facades span the full height of the building at the same XY corners.

In a **stepped building** (podium + shaft + multi-tier setback crown):
1. **Per-Level Footprint Override (`floor_plates[].footprint_cm`):**
   A `floor_plates[]` entry in `dimensions.json` (under `schema_version: "1.1"`) may optionally declare its own `footprint_kind`, `footprint_cm`, `footprint_ccw`, `footprint_width_cm`, and `footprint_depth_cm`.
   - When **absent**, the plate inherits `site.footprint_cm` and `site.footprint_area_m2` (the existing prismatic rule).
   - When **present**, the plate's `footprint_cm` must be a valid CCW polygon contained **inside or on** the plate immediately below it (`level_index - 1`, or `site.footprint_cm` at `level_index == 0`) within `tolerances.linear_cm`, and its vertices must lie on structural grid lines (`x_bay_cm` / `y_bay_cm` cumulative offsets) or symmetric sub-modules.
2. **Level-Scoped Facade Runs (`facades[].spans_level_indices`):**
   In `dimensions.json`, a `facades[]` entry may optionally declare `spans_level_indices` (array of integer level indices, e.g. `[0, 1, 2]` for a podium facade, `[3..17]` for a shaft facade, `[18, 19]` for a setback crown tier facade).
   - When `spans_level_indices` is **absent**, the facade spans **all** `levels[]` (existing prismatic behaviour).
   - When `spans_level_indices` is **present**, `start_corner_cm` and `end_corner_cm` of that facade must be vertices of the `floor_plates[lvl].footprint_cm` (or `site.footprint_cm` if the plate has no override) for every `lvl` in `spans_level_indices`.
3. **Setback Roof Terraces / Ledges (`massing.json` `setback_deck` & `pilaster`):**
   - Where `floor_plates[i].footprint_cm` is smaller than `floor_plates[i-1].footprint_cm`, the exposed top band of storey `i-1` forms a stepped terrace/parapet ledge.
   - To keep the prism rule (`07` §8.1.1: simple rings only, no holes), `build_spec.py` emits each storey's `slab` using that storey's effective `footprint_cm`, emits `column` elements only for interior grid intersections that lie strictly inside that storey's effective `footprint_cm`, and emits `facade_wall` elements **only** for valid `(facade, level_index)` pairs where `level_index` is in `facade.spans_level_indices`.
   - Optional tectonic pilasters (`kind: "pilaster"` on layer `05_FACADE`) are emitted as vertical Z-prisms along facade bay boundaries or corner piers when declared.

---

## 2. Step-by-Step File Modifications Required

### Task 1: Update `references/07-spec-grammar.md`

1. **In §5.8 (`floor_plates[]`), add optional Schema 1.1 keys:**
   | Key | Type | Req | Units | Range | Meaning | Default |
   |---|---|---|---|---|---|---|
   | `footprint_kind` | string | opt (1.1) | — | `polygon` \| `rectangle` | present iff `footprint_cm` is present | — |
   | `footprint_cm` | array of `[x,y]` | opt (1.1) | cm | ≥ 3 vertices, simple CCW ring inside/on lower level footprint | stepped floor plate outline in world XY | inherits `site.footprint_cm` |
   | `footprint_ccw` | bool | opt (1.1) | — | `true` | required iff `footprint_cm` is present | — |
   | `footprint_width_cm` | number | opt (1.1) | cm | > 0 | **derived** X extent of `footprint_cm` (required iff `footprint_cm` present) | — |
   | `footprint_depth_cm` | number | opt (1.1) | cm | > 0 | **derived** Y extent of `footprint_cm` (required iff `footprint_cm` present) | — |

2. **In §5.10 (`facades[]`), add optional Schema 1.1 key:**
   | Key | Type | Req | Units | Range | Meaning | Default |
   |---|---|---|---|---|---|---|
   | `spans_level_indices` | array of int | opt (1.1) | — | non-empty, strictly ascending, each in `levels[].index` | storeys this facade elevation spans (for podium / shaft / setback tiers) | all `levels[].index` |
   - Update `name` constraint on `facades[]`: allow tier-qualified elevation names matching `^(north|south|east|west)(_[a-z0-9_]+)?$` (e.g. `north_podium`, `north_shaft`, `north_crown1`) when `schema_version == "1.1"`, while keeping `north|south|east|west` for `"1.0"`.
   - Update `id` constraint on `facades[]`: allow `^F-[NSEW](-[A-Z0-9]+)?$` (e.g. `F-N-POD`, `F-N-SHF`, `F-N-CR1`) under `"1.1"`.

3. **In §8.1.1 (`massing.json` `elements[]`) & §8.1.2:**
   - Add `"pilaster"` to the allowed `elements[].kind` vocabulary, mapped to layer `"05_FACADE"` in §8.1.2.
   - Clarify in **G-38**: a `slab` uses the effective footprint of its storey (`floor_plates[i].footprint_cm` if present, else `site.footprint_cm`). Every `(facades[i].id, level_index)` pair **where `level_index` is in `facades[i].spans_level_indices`** (defaulting to all levels when `spans_level_indices` is omitted) has exactly one `facade_wall`. Columns in storey `i` are generated only for `(column_x_cm, column_y_cm)` intersections strictly inside storey `i`'s effective footprint.

4. **In §9.3 (`dimensions.json` Invariants), update G-21, G-25, G-28, G-29, G-30 and add G-91:**
   - **G-21:** Also validates `floor_plates[].footprint_cm` and `footprint_ccw` whenever present.
   - **G-25:** If `facades[i].spans_level_indices` is absent, `start_corner_cm` and `end_corner_cm` must be vertices of `site.footprint_cm` (unchanged). If `spans_level_indices` is present (Schema 1.1), `start_corner_cm` and `end_corner_cm` must be vertices of the effective footprint of every level in `spans_level_indices`.
   - **G-28:** Additionally checks that `openings[].level_index` is contained in the target facade's `spans_level_indices` (when present).
   - **G-29:** If `floor_plates[i].footprint_cm` is absent, `gross_area_m2 == site.footprint_area_m2` (unchanged). If `floor_plates[i].footprint_cm` is present (Schema 1.1), `gross_area_m2` equals the polygon area of `floor_plates[i].footprint_cm` in $\text{m}^2$ ($\pm 0.05\text{ m}^2$).
   - **G-30:** Roof `parapet` elements in S2 follow the effective footprint of the top storey (`levels[-1]`).
   - **Add `G-91` (Stepped plate containment & co-presence, Schema 1.1):**
     - If any of `footprint_kind`, `footprint_cm`, `footprint_ccw`, `footprint_width_cm`, `footprint_depth_cm` is present on a `floor_plates[i]` entry, **all five** must be present (`schema_version` must be `"1.1"`).
     - Every vertex of `floor_plates[i].footprint_cm` must lie inside or on the effective footprint of `floor_plates[i-1]` (or `site.footprint_cm` for `i == 0`) within `tolerances.linear_cm` (monotonic setback containment).
     - Reports honest `SKIP` when no `floor_plates[]` entry declares `footprint_cm` and no `facades[]` entry declares `spans_level_indices`.

---

### Task 2: Update `scripts/validate_specs.py`

1. **Implement `G-91` and update `G-21`, `G-25`, `G-28`, `G-29`, `G-32`, `G-38`:**
   - Write helper `effective_plate_footprint(dim_doc, level_index)` which returns `floor_plates[level_index]["footprint_cm"]` if present, else `dim_doc["site"]["footprint_cm"]`.
   - Write helper `effective_facade_levels(dim_doc, facade_obj)` which returns `facade_obj["spans_level_indices"]` if present, else `[lvl["index"] for lvl in dim_doc["levels"]]`.
   - In **`G-25`**: verify `start_corner_cm` and `end_corner_cm` against `effective_plate_footprint(dim_doc, lvl_idx)` for each `lvl_idx` in `effective_facade_levels(dim_doc, facade_obj)`.
   - In **`G-28`**: verify `opening["level_index"] in effective_facade_levels(dim_doc, facade_map[opening["facade"]])`.
   - In **`G-29`** and **`G-32`**: compute expected `floor_plates[i].gross_area_m2` from `effective_plate_footprint(dim_doc, i)`. When `floor_plates[i].footprint_cm` is present, recompute `footprint_width_cm` and `footprint_depth_cm` in `G-32`.
   - In **`G-38`**:
     - Check each `slab` element's `profile_cm` against `effective_plate_footprint(dim_doc, storey_index)`.
     - Check `roof_deck` and `parapet` outlines against `effective_plate_footprint(dim_doc, top_level_index)`.
     - Check `facade_wall` bijection against the active set of `(facade.id, lvl_idx)` pairs where `lvl_idx in effective_facade_levels(dim_doc, facade)`.
     - Allow `pilaster` in `elements[].kind` on layer `05_FACADE`.
   - Register **`G-91`** in the validator rule table so `--rule G-91` works and clean 1.0/1.1 prismatic projects report `SKIP` (with reason `"No stepped floor_plates[].footprint_cm or facades[].spans_level_indices declared"`).

---

### Task 3: Update `scripts/build_spec.py` (S2 Massing Builder)

1. **Per-storey effective footprint:**
   - When building `slab` for storey `i`, read `fp = effective_plate_footprint(dim, i)`. Compute the bounding box and emit `Box` with `fp`'s XY centre and extents.
   - Update `origins["elements[k]"]` `derives_from` to point to `floor_plates[i].footprint_cm` when overridden, or `site.footprint_cm` when inherited.
2. **Column pruning on upper setbacks:**
   - For storey `i`, filter `(cx, cy)` from `column_x_cm × column_y_cm` so only columns whose `[cx - sx/2, cx + sx/2] × [cy - sy/2, cy + sy/2]` box lies strictly inside `effective_plate_footprint(dim, i)` are emitted for that storey.
3. **Scoped `facade_wall` generation:**
   - Iterate over `facade in dim["facades"]` and only over `lvl_idx in effective_facade_levels(dim, facade)` (instead of the Cartesian product of all facades × all levels).
4. **Roof deck & parapet on top tier:**
   - Build `roof_deck` and the 4 `parapet` strips from `effective_plate_footprint(dim, len(levels) - 1)` so the roof crown sits on the top setback tier (`800 × 800 cm` in an Art Deco tower) instead of floating at the `2800 × 2400 cm` base width.

---

### Task 4: Update `scripts/facade_tables.py` (S4a/S4b Grid & Component Builder)

1. **Respect `facades[].spans_level_indices`:**
   - When constructing `facades[].levels[]` in `facade_grids.json`, iterate only over `lvl_idx in effective_facade_levels(dim, facade)` rather than all levels in `dimensions.json`.
   - Ensure `G-57`…`G-70` self-checks in `facade_tables.py` validate `facades[].levels[]` against the facade's active `spans_level_indices`.

---

### Task 5: Verify Compatibility in `scripts/place_components.py` (S5) & `scripts/qa_check.py` (S7)

1. In `scripts/place_components.py`:
   - Confirm that host wall lookup for `opening_cuts[]` and `wall_cells[]` matches `(facade_id, level_index)` against the `facade_wall` elements emitted for that facade's `spans_level_indices`.
   - Confirm that Mechanism A (`host_node.isHidden = true`) hides all active `facade_wall` hosts across all stepped tiers.
2. In `scripts/qa_check.py`:
   - Confirm that `QA-V1-WALLS` and `G-82` ($B_{\text{total}}$ volume identity) evaluate per active `facade_wall` host without assuming `len(facades) * len(levels)` fixed hosts.

---

### Task 6: Add Stepped Tower Fixture & Run Verification Gate

1. Create a new test fixture `specs/fixtures/stepped-tower/` (or test script) exercising a 3-tier stepped massing model (`Podium 2800×2400` -> `Shaft 2400×2000` -> `Crown 1600×1600`) with `schema_version: "1.1"`, `floor_plates[].footprint_cm`, and `facades[].spans_level_indices`.
2. Run the full verification sequence:
   ```bash
   python -m py_compile scripts/*.py
   python scripts/validate_specs.py --dir examples --warnings-as-errors
   python scripts/validate_specs.py --dir specs/fixtures/form-precision --warnings-as-errors
   python scripts/validate_specs.py --dir specs/fixtures/stepped-tower --warnings-as-errors