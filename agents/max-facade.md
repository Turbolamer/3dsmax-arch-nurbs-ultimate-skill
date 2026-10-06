# max-facade — S4a: locked `dimensions.json` + `massing.json` → `facade_grids.json` + `facade_table.csv` + `world_table.csv`

> **Purpose:** S4a is the first stage that turns **openings** into **geometry**. It reads the locked
> spec set S1/S2 handed over, writes `facade_grids.json` (`07` §8.3 — a `u` division shared by the whole
> run and a **`v` division per bay**, and the panelised partition those axes generate), emits two
> placement tables, and — because a CSV nobody has placed is an unproven CSV — hands them to the live
> gate in §7 for a count and a measurement. **S4a builds the grid only.** Blocks, families and the
> size-matched join are S4b (`agents/max-components.md`); placements, cuts and layer application are S5.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage · Input | **S4a** (`PLAN.md` §4 row P5, `01` §3 "S4a") · `specs/pipeline/dimensions.json` (`facades`, `levels`, `openings`) **and** `massing.json` (`storeys`, `elements`), plus `assumptions.json` / `conflicts_resolved.json` |
| Output | `facade_grids.json` (`07` §8.3), then `facade_table.csv` and `world_table.csv` (schema and columns: contract §6) |
| Geometry produced | `axes[]` — one offset per division line · `panels[]` — one rectangle per grid cell, kinded · `panel_types[]` — the kinds this project declared. **No placements, no blocks, no MAXScript** |
| 3ds Max calls | Exactly one stage of them, and they are **the orchestrator's**: the §7 live gate. **No probes** (§1.2) |
| Consumer · Precondition | S4b (`agents/max-components.md`) → S5 `assembly.json` · S1 and S2 complete and locked |
| Blocked by | A `dimensions.json` or `massing.json` that is not `locked`. Full stop (§2.2) |
| Findings | See `agents/max-orchestrator.md` §6.2. If this session produced a real finding — a measured value outside `tolerances.linear_cm`, a facade situation the `v` division will not decompose into, or an `openings[]` value that is legal but wrong for this building — record it in `<project>/IMPROVEMENTS.md`. **A session with no findings writes nothing and creates no file.** Format: `references/improvement-log.md` |

### 1.1 What S4a owns, and what S4a defers

S4a owns **three keys' worth of arithmetic**: a per-`(facade, level)` division in `u` and `v`, one
rectangle per cell, and the kind each rectangle is. Everything downstream of that is another stage's.

| **Never** built by S4a | Consumed by | Correct instrument |
|---|---|---|
| Blocks, `families`, the size-matched join | **S4b** | `components_registry.json` (`07` §8.4) |
| Placements, transforms, opening **cuts** into host geometry, the scatter declaration, `layer_map` | **S5** | `assembly.json` (`07` §8.5). **CORRECTED (2026-10-06):** this cell said "scatters"; the schema key is **`scatter`**, singular, and it is a **declaration** only — S5 emits no scatter node and the **user applies it by hand** |
| Materials, renderer choice, UV rules | **nobody — S6 was cancelled 2026-10-05** | **Applied by hand by the user**; the hand-off is `agents/max-orchestrator.md` §5. `materials.json` is a **reserved stub**, not a deliverable and not a gate. `material_role` here is a **role**, never a material class (`07` §8.3.6) |
| Layer **application** to any node | **nobody — permanently** | **There is no way to assign an object to a layer from this bridge. Nine routes are ruled out and this is final, not an open question** (`agents/max-assembly.md` §6.3): `LayerManager` exposes only `newLayerFromName` / `getLayerFromName` / `getLayer` and **no setter**; `node.layer =` as string, integer index or `LayerProperties` mixin all throw `Property is read-only: layer`; `manage_layers`' action vocabulary is **exactly `{list, create, delete}`** (40+ candidates rejected); `set_object_property` with `property=layer` dies on the same read-only assignment, with a `property=pos` **positive control** succeeding in the same batch. **Layer is data** (`07` §8.1.3); no builder emits layer code (`G-79`); **the user applies it in the Layer dialog** |
| Curved facades, warped runs, a facade that is not one straight segment | **nobody at P5** | There is no `kind` for it (§6.1). Refuse by name and escalate (§10.1) |
| Reveal depths, glazing build-ups, panel sub-components | **nobody — S6/S7 were cancelled 2026-10-05** | A component's `variants` and `parameters` are where that **data** belongs (`07` §8.4.3) — but no stage reads it into geometry |

### 1.2 The one-MCP rule

**You may not touch the bridge.** S4a is arithmetic; the §7 gate belongs to the orchestrator, and the
rule is the same one S3 uses, tightened by one thing: this stage has **no emitted `.ms`**, so there is
nothing to `fileIn` — the consumer of the CSV is live Max itself, and it is the orchestrator who runs it.

| Allowed | Forbidden |
|---|---|
| `3dsmax-mcp_get_scene_info` / `_get_scene_snapshot` to confirm the scene is empty **before** the gate | **Any exploratory probe.** A fact not in `CHECKPOINT.md` §"Verified facts" is escalated for an orchestrator probe, never opened by S4a |
| `3dsmax-mcp_delete_objects` on gate nodes, in the same call | Every tool in `01` §1.2 — the absent-plugin group, and the Rhino-server name collisions enumerated in `AGENTS.md` §"MCP tool-name collisions" and `02` §5. Never call those against Max and never conclude the bridge is down because one errored |
| `3dsmax-mcp_manage_layers` actions `list` and `create` — the eight names in `07` §8.1.4, nothing else | **`3dsmax-mcp_manage_layers` **object assignment** — and it is not "unknown": the action **does not exist**. The vocabulary is **exactly `{list, create, delete}`**, 40+ candidates rejected including `rename`; with the eight MAXScript and tool routes that is **nine ruled out in total**. **This is nobody's problem to solve — the user applies layers in the Layer dialog** (`agents/max-assembly.md` §6.3) |
| `3dsmax-mcp_capture_viewport` for a human-facing record, after measuring | `3dsmax-mcp_introspect_class` / `_introspect_instance` / `_inspect_plugin_class` as **proof** — they lie (`AGENTS.md`, §"The one rule that matters most") |

> **`mcg_*` and `curve_model` do not exist in this bridge** (`AGENTS.md` §"Two absent tool families",
> confirmed against the live tool list at P4b-r). If a facade recipe reaches for either, that is a
> missing tool, not a missing feature — record it (§10.2), never emulate it by hand.

Executing the §7 gate on an already-computed CSV is **not** a probe (`01` §6).

---

## 2. Inputs and outputs

### 2.1 What you read

| Source | What you take from it |
|---|---|
| `specs/pipeline/dimensions.json` | **The contract you build from** — `facades[]` (`id` `name` `direction_deg` `start_corner_cm` `end_corner_cm` `length_cm` `bay_count` `bay_width_cm`) · `levels[]` (`index` `elevation_cm` `height_cm`) · `openings[]` (`id` `facade` `level_index` `bay_index` `type` `position_cm` `width_cm` `sill_cm` `head_cm`) · `tolerances` |
| `specs/pipeline/massing.json` | `storeys[]` and `elements[]` — read **only** to resolve `host_ref` (§6.6). At P5 the answer is `null` throughout: there is no exterior envelope element to cut an opening into (`07` §8.3.6) |
| `references/07-spec-grammar.md` | **§8.3** the schema in full · **§8.3.5** the derivation, all fourteen steps · **§8.3.6** what this file may not encode · **§9.8** `G-57`…`G-70` · §3.1 the lock gate · §5.2 `origins` granularity · §2 units · **§5.11** the `openings[].type` vocabulary · **§8.1.3** layer is data · §9.6 the SKIP discipline |
| `references/09-defaults.md` | `D-OP-12` (curtain-wall pier width, 15 cm, range 10…25) — the **only** threshold in this file, and it is `D-OP-12` × 2 (§6.4) · `D-WA-07` (the spandrel convention `spandrel` names) |
| `references/11-layer-standard.md` | §1.6 `05_FACADE` · §3.1 naming, **N1** (no `-` in a name) · §6 checklist H1–H12 |
| `references/01-architecture-aec-workflow.md` | §2 the spec chain, **row 6** · §3 the S4a row — its gate and its two refusal cases · §8 the CLI contract |
| `references/_p5-contract.md` | §2 the executed read of the example inputs · §3 schema · §4 derivation · §6 CSV columns · §9 the live gate. **The authority for this stage** — where an implementation wants a different key name, formula or id pattern, this file wins |
| `CHECKPOINT.md` | §"Scene units and placement semantics — VERIFIED (P3, 2026-10-04)" and §"Emitted-MAXScript rules" — the transcript of record for §7 · §"Reference claim-by-claim pass — VERIFIED (P4b-r, 2026-10-04)" for the delete/instance rule in §9 |

> **`direction_deg` is not a rotation.** The example is executed fact, not a reading: `F-S` runs
> `[0,0] → [1800,0]` and carries `direction_deg: 180.0`; `F-N` runs `[0,900] → [1800,900]`, also
> **+X**, and carries `0.0`; `F-W` runs `[0,0] → [0,900]` and carries `270.0` where its run angle is
> `90.0`. Two of the four facades are wrong by 180° if the facing label is used as a rotation. §6.1.

### 2.2 What you own, and the lock gate

| Path | Action |
|---|---|
| `<project>/specs/pipeline/facade_grids.json` | **Emitted by the builder.** Never hand-written, never hand-edited (§6.8) |
| `<project>/specs/pipeline/facade_table.csv` · `world_table.csv` | **Emitted by the builder.** Never hand-written, never hand-patched |

**You modify nothing else** — not `references/07`, not `scripts/`, not `examples/`, not
`agents/max-components.md`, not S1's or S2's locked files, not `CHECKPOINT.md`.

> **A builder must refuse any spec file whose `status` is not `locked`, naming the file and the status
> it found** (`07` §3.1). Exit non-zero, before anything else is read.

| Found | Action |
|---|---|
| `status: "draft"` or `"superseded"` on `dimensions.json` or `massing.json` | **Refuse**, and report that path and status verbatim. `--allow-draft` is an inspection flag for linting work in progress, never for a deliverable |
| a `facade_grids.json` already in `--in` whose bytes differ from what the builder computes, or a CSV whose row count is not `len(panels)` | **Refuse, naming the first differing key path** (contract §8 obligation 1). A hand edit the next rebuild would silently destroy is the failure mode `--from examples` exists to prevent |
| `schema_version` major you do not implement | **Stop.** Do not guess |
| an `A-nnn` in `assumptions.json` with `recheck_stage: "P5"` | Build it **and name every one in your report**. You are the recheck stage |

A `draft` upstream file is not your failure to fix, and not a reason to build "just the ready parts".

---

## 3. File ownership

| Artifact | The contract you may rely on |
|---|---|
| `scripts/facade_tables.py` | Exposes `--in <dir> --out <dir> [--stage grids\|components\|tables\|all] [--json] [--build] [--allow-draft]`; `--stage grids` writes `facade_grids.json` only; refuses non-`locked` input with a non-zero exit; self-checks `G-57`…`G-70` **on the emitted documents before writing** and refuses on any FAIL; after writing the CSVs asserts `G-70` by reading them back; byte-identical output for byte-identical input. **It emits no MAXScript** — hence §7 |
| `examples/facade_grids.json` · `facade_table.csv` · `world_table.csv` | The `pavilion-01` worked case, orchestrator-committed from the builder's output. **Not yours to edit.** They are the artefact you verify |
| `examples/assumptions.json` | Carries `A-023` / `A-024`, owned by the orchestrator. You verify them (§10) and never write them |
| `07` §8.3 / §8.4 / §9.8 | Agent A's tables and `G-57`…`G-70`. Cite by id; **do not edit** |

**A `G-` id you cannot evaluate is a SKIP with its reason, never a silent PASS** (`07` §9.6). At P5
that includes `G-70` (it observes an emitted CSV, which a static file cannot see) and `G-63`/`G-68`
when the registry is absent.

---

## 4. Procedure

Ordered and deterministic. Each step has a pass condition.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Verify the inputs are locked** | Read the six envelope keys of `dimensions.json` and `massing.json`, and of an existing `facade_grids.json` if one is present. Apply §2.2 in full | Both `locked`, `project` agrees, `units.length == "cm"` |
| 2 | **Re-check every P5 assumption** | List every `assumptions.json` entry with `recheck_stage: "P5"`. Each is a **low-confidence proxy** for something a licensed professional owns — here, a facade composition decision | Every one named in your report. **None silently upgraded.** If one would change the panelisation, that is an escalation (§10.1) |
| 3 | **Read the inputs into the grid model** | Read §2.1 once, in order. Take `tolerances` **verbatim** — a builder may not widen them. Collect `O` = openings per `(facade, level_index)`, **grouped by `bay_index`** and each group sorted by `id`. `G-28` forbids two openings sharing `(facade, level_index, bay_index)`, so a group holds at most one — handle a larger group anyway by admitting every member's sill and head as axes. **Preserve `bay_index` verbatim: indices are positional and meaningful, never sorted or normalised** (`01` §3, S4a gate) | Every value used is a real key path. **Every `origins` entry is `derived`** (`G-64`) — S1 and S2 already resolved `given` / `assumed` / `conflict` |
| 4 | **Per facade, compute the run geometry** | `bay_offsets_cm` = `[0]` + running sum of `bay_width_cm`; `bay_centre_cm[i]` = `offsets[i] + width[i]/2`; `run_angle_deg` = `atan2(end.y - start.y, end.x - start.x)` normalised to `(-180, 180]`, with `180.0` staying `180.0` | `offsets[-1] == length_cm` within `linear_cm`; `run_angle_deg` recomputed by hand for **all four** facades and matching. `direction_deg` copied verbatim and used for nothing |
| 5 | **Build the axes — `u` per facade at a level, `v` per bay** | **u**, one set per `(facade, level)`: `bay_offsets_cm` as `kind: "bay"`, plus `position_cm ± width_cm/2` as `opening_edge` for every opening in `O` — **all with `bay_index: null`**. **v**, one set per `(facade, level, bay)`, bays ascending: `0` as `level_base` and `height_cm` as `level_top`, plus the `sill_cm` and `head_cm` of **that bay's group only**, **all with `bay_index: b`**. Sort ascending, **merge any two within `linear_cm`**, keeping the smaller (§6.3) | `[-1] == length_cm` (u) / `height_cm` (each bay's slice) within tolerance; within one `(facade, level, family, bay_index)` offsets strictly ascending and **more than `linear_cm` apart**; every `u` axis has `bay_index: null` and every `v` axis a real bay index; **a bay with no opening contributes exactly its `level_base` and `level_top`** (`G-58`) |
| 6 | **Enumerate cells per `(facade, level, bay)` and test each against that bay's openings** | u cells and v cells = consecutive axis pairs, **of that bay's own v axes** — the tiling unit is `(facade, level, bay)`. Per cell: `u_mid`, `v_mid`, `bay_index` = the bay whose `[offset, offset+width)` contains `u_mid`. Then the hit test: the opening in **that bay's group** whose u-range contains `u_mid` **and** whose `[sill, head]` contains `v_mid`. At most one can — `G-27` forbids overlap | Every `(facade, level)` has ≥ 1 panel; Σ panel areas == `bay_width_cm[b] × height_cm` per `(facade, level, bay)` **and** `length_cm × height_cm` per `(facade, level)`; no two panels overlap in their interiors; every panel lies inside its bay's rectangle (`G-61`) |
| 7 | **Classify each cell, first match wins** | The six rules of `07` §8.3.5 step 8, in order — `vision` → `punched_window` → `mullion` → `transom` → `spandrel` → `blank` (§6.5). A qualifying pier cell is emitted **once per `(facade, level, bay)`** spanning `0 … height_cm` with `full_height: true`, not once per v-cell | A `full_height` panel has `v_min_cm == 0` and `v_max_cm == height_cm`, and its v-axis ids are **its own bay's** `level_base` and `level_top` (`G-60`). No `mullion` or `transom` carries an `opening_ref` |
| 8 | **Compute the remaining panel fields and the ids** | `width_cm`/`height_cm` from the rectangle · `u_axis_min`/`u_axis_max`/`v_axis_min`/`v_axis_max` by matching offsets · `bay_index` · `opening_ref` · `host_ref` (§6.6) · `centre_cm` = `start_corner_cm + run_unit × u_mid` in XY, Z = `elevation_cm + v_mid`, where `run_unit = (end - start)/length_cm` · `layer: "05_FACADE"` · ids `AX-nnn` over `(facade order, level_index, family with u before v, bay — null first — offset)` and `PNL-nnn` over `(facade order, level_index, bay_index, v_min_cm, u_min_cm)` | Every panel's four edges land on declared axes at matching offsets (`G-60`); **every opening is referenced by exactly one panel** whose rectangle equals the opening's (`G-62`, §6.2) |
| 9 | **Declare `panel_types[]`** | One entry per kind this project actually used, with `glazed`, `frame_member`, `material_role` and `opening_types`. `material_role` is `glazing` / `opaque` / `frame` — a **role**, never a material class | Flags mutually consistent; `opening_types` non-empty **iff** `glazed`; every declared kind used by ≥ 1 panel (`G-63`); inside the ceiling of six (`07` §8.3.4) |
| 10 | **Emit, then verify by recomputation** | Run the builder (§5). **You do not hand-write either file.** Read `facade_grids.json` back from disk and verify it **independently**: recompute one u-axis set, **one bay's** v-axis set, one `run_angle_deg`, one `centre_cm` and one panel's `kind` by hand from `dimensions.json` — and check one opening's **single** panel against its own `sill_cm` / `head_cm` | Hand computation matches the file at `tolerances.linear_cm`, and the axis/panel id sets match what you derived. **Do not verify the builder by reading its own output back and nodding at it** |
| 11 | **Derive the registry and the two CSVs, then validate** | `--stage components` and `--stage tables` (or `--stage all`). Then `python scripts/validate_specs.py --dir <specs_dir> --build`, and again with `--warnings-as-errors` | Exit **0** and `FAIL 0` in **both** modes. `G-57`…`G-70` PASS, or SKIP **with its stated reason** — see §8 row 2 |
| 12 | **Hand the tables to the live gate, clean up, report** | §7 then §9 then §12. **An emitted CSV is not done until it has been placed in Max and counted** — the table-shaped equivalent of P3/P4's `fileIn` + `node.min/max` | Every measured number recorded; `objects.count == 0` at the end; the report is under the §12 cap |

**Determinism.** The same locked inputs must yield byte-identical `facade_grids.json` and both CSVs
(`07` S-5, `01` §5). Four things break it, and all four are defects to report rather than fix in the
output: a timestamp other than `source.recorded_at`, a run-time default, iteration-order dependence
(dict or set order leaking into an id or a row order), and float formatting that leaves `-0.0` or
varies in width. Panel ids ascend in fixed order, so a rebuild yields the same ids (`11` N3).

---

## 5. The build commands

```
python scripts/facade_tables.py --in <specs_dir> --out <out_dir>
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --stage grids
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --stage components   # reads the existing grids file
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --stage tables       # reads both existing JSONs
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --json
python scripts/validate_specs.py --dir <specs_dir> --build [--warnings-as-errors]
```

Read the builder's `--help`; never guess a flag. `01` §8 fixes the shape and forbids a second entry point.

| Aspect | Contract |
|---|---|
| Reads | `<in>/dimensions.json` and `<in>/massing.json` for `--stage grids`; the **existing** `<in>/facade_grids.json` for `--stage components`; both JSONs for `--stage tables` |
| Writes | `<out>/facade_grids.json`, `<out>/components_registry.json` (S4b's, §12), `<out>/facade_table.csv`, `<out>/world_table.csv`. `--out` defaults to `--in`; `--json` gives a machine-readable report |
| Exit **0** | The lock gate passed **and** the `G-57`…`G-70` self-check produced no failure |
| Exit **non-zero** | A refusal naming the reason — the file path and the `status` found, the first differing key path, or the `G-` ids that fired |
| Determinism | Byte-identical output for byte-identical input |
| MAXScript | **None emitted.** There is no `.ms` at this stage, so there is nothing to `fileIn` — §7 is the gate instead |
| Layer code | **None.** Layer is data (`07` §8.1.3). Adding layer code is a defect, not an improvement — it cannot work (`CHECKPOINT.md`, P3, 2026-10-04) |
| CSV shape | Header row, one row per panel, sorted by `panel_id`, LF endings, no quoting, no value containing a comma; floats through the same 6-dp `q()` as `build_nurbs.py`; counts and indices plain integers (contract §6) |

**A non-zero exit is a stop**: fix the input through S1 (§10.1) or the builder through its owner (§3).
Never rename a key, widen `tolerances`, drop a leaf, re-sort `bay_index`, or delete a panel to silence a
`FAIL`.

---

## 6. The grid rules

### 6.1 `direction_deg` is a label; `run_angle_deg` is the rotation

**This is the single most important rule in the stage** and it is its own invariant (`G-57`), because it
is exactly the field a later stage will reach for.

| Facade | Run | `direction_deg` | `run_angle_deg` |
|---|---|---|---|
| `F-S` | `[0,0] → [1800,0]`, **+X** | `180.0` | `0.0` |
| `F-N` | `[0,900] → [1800,900]`, **+X** | `0.0` | `0.0` |
| `F-E` | `[1800,0] → [1800,900]`, **+Y** | `90.0` | `90.0` |
| `F-W` | `[0,0] → [0,900]`, **+Y** | `270.0` | `90.0` |

Two of the four carry a facing that differs from their run by 180°. `run_angle_deg` is the **only**
rotation source in this file, and `G-57` forbids the other route by name.

### 6.2 Exactly one panel per opening — strictly one

**An opening is realised by exactly one panel.** Its own `sill_cm` and `head_cm` are its only vertical
divisions (§6.3), so there is nothing that could split it. `G-62` asserts strictly that: every
`dimensions.openings[]` entry is referenced by **exactly one** panel, that panel shares its
`facade`, `level_index` and `bay_index`, its u-range equals
`[position_cm - width_cm/2, position_cm + width_cm/2]`, its v-range equals `[sill_cm, head_cm]`, and its
`kind` lists the opening's `type` in `panel_types[].opening_types`. **"Exactly one", never "one or
more"** — two panels for one opening is not a partition nicety, it is a ribbon of glass (§6.3).

The rule this replaced said "tiles", and it was written to accommodate a **facade-wide** v grid. That
grid is gone; see §6.3 for what it cost.

### 6.3 The vertical division is **per bay**, and the `u` division is not

| Family | Granularity | Contents |
|---|---|---|
| **`u`** | one set per `(facade, level)` | `bay_offsets_cm` as `kind: "bay"`, plus every opening's `position_cm ± width_cm/2` as `opening_edge`. **Every `u` axis carries `bay_index: null`** — a horizontal line runs the whole run |
| **`v`** | one set per `(facade, level, **bay**)` | `0` as `level_base` and `height_cm` as `level_top`, plus the `sill_cm` and `head_cm` of **the openings in that bay only**. Every `v` axis carries a real `bay_index` |

`facades[].levels[].v_axis_ids` therefore holds **every** v axis at that facade and level, ordered by
`(bay_index, offset)`, and **each bay's own slice runs `0 → height_cm`**. `G-58` enforces both halves,
including that a bay with no opening contributes exactly its `level_base` and `level_top`.

**Consequences, both of them required:**

- **A bay with no opening is one whole `blank` panel** — two v axes, one v-cell, the bay's full width and
  full storey height. That is the correct reading of "no opening declared here", not an elevation
  divided by lines that belong to other bays.
- **An opening is realised by exactly one panel**, because its own sill and head are the only divisions
  inside it (§6.2). The tiling unit is `(facade, level, bay)`.

**The cost, stated honestly:** transom lines are continuous **within a bay**, not across the run. That is
the correct trade and it is the whole trade.

#### 6.3.1 The sliver — the cautionary example, with its real numbers

This is not hypothetical. It is what the first generated grid produced, and it is the shape of defect
you must be able to recognise in your own output.

| | |
|---|---|
| What the superseded rule did | made the v axes the **union of every opening's sill and head across the whole facade at that level**, on the reasoning that a curtain wall's transom lines run continuously — which they do |
| What nobody measured before generating | the union also imposes **every bay's head line on every other bay** |
| The inputs | `OP-G-01` — `F-S`, `LVL-00`, bay 0, `window`, `position_cm 225.0`, `width_cm 180.0`, **`sill 90 → head 270`** · `OP-G-02` — bay 1, `entrance`, `width_cm 200.0`, **`head_cm 260`** |
| What happened | the 260 line ran across the whole facade, cutting bay 0's window into a `180 × 170` panel plus **`PNL-024`, a `punched_window` of `180 × 10 cm`** — a 10 cm ribbon of glass sitting 10 cm below a window head, because a *different bay's* door ended there |
| What per-bay v axes produce | bay 0's v axes are `0, 90, 270, 420`; `OP-G-01` stays **one `180 × 180` panel**. Bay 1's `260` divides **only bay 1** |

**The recognition rule.** A panel whose `height_cm` is a sliver — a few centimetres, or smaller than the
`joint_width_cm` P6 will inset it by — is not a design decision. Find which axis produced its `v` edge,
name the opening on the **other** bay that owns that offset, and you have found a shared v grid. Fix the
axis, never the panel: deleting the sliver by hand leaves the grid wrong and the next rebuild puts it
back.

### 6.4 The 30 cm pier threshold is derived, not chosen

Rule `mullion` requires a cell inside a curtain-wall opening's u-zone with width `≤ 30 cm`. That number
is `09` `D-OP-12`'s curtain-wall pier width (**15 cm**, range `10 … 25`) **doubled** — record it as
`D-OP-12 × 2` in `derives_from`. It is the only threshold in the file. If a project's pier exceeds it,
the pier reads as `blank` — a wall return, which is the correct reading of a wide pier, and **no default
is violated**. Do not widen the threshold to rescue a pier; escalate (§10.1).

### 6.5 The classification order, and what each kind carries

Because a hit cell is always the opening's whole rectangle (§6.3), rules 1 and 2 no longer test the
cell's v-range: a hit **is** `[sill_cm, head_cm]`.

| Order | Kind | Condition | `opening_ref` | Cut by the bay's v grid |
|---|---|---|---|---|
| 1 | `vision` | hit and `o.type == "curtain_wall"` | the opening | — it is the whole rectangle |
| 2 | `punched_window` | hit, any other `o.type` | the opening | — it is the whole rectangle |
| 3 | `mullion` | the cell's u-range is **adjacent to** a `curtain_wall` opening's u-range **on the same bay** — one of its two u boundaries equals the opening's corresponding boundary within `linear_cm` — and the cell's width `≤ 30 cm` (§6.4) | **`null`** | **no** — merged once per `(facade, level, bay)` over `0 … height_cm`, `full_height: true` |
| 4 | `transom` | `v_min_cm` equals a curtain-wall opening's `head_cm` **and** width equals that opening's width | **`null`** | yes |
| 5 | `spandrel` | `v_max_cm` equals some opening's `sill_cm` **and** width equals that opening's width | the opening | yes |
| 6 | `blank` | anything else — including **every cell of a bay with no opening** | `null` | yes |

First match wins, and the order is not yours to reorder: `mullion` and `transom` are frame members
**of** an opening, not the opening, which is why they carry `null`. **Rule 3 says "adjacent to", not
"inside".** The earlier wording required a cell to be simultaneously *outside* every opening's u-range
and *inside* a curtain-wall opening's u-range, which no pier cell can satisfy — a pier *flanks* the
opening it belongs to, it is not inside it. `adjacent to` is the single rule, and it is what produces the
two 15 cm mullions per level on `F-S`/`LVL-00`. A `mullion` cut by the bay's v grid, or carrying an
`opening_ref`, is a defect (`G-60`, `G-62`).

### 6.6 `host_ref` is `null` at P5, and that is a limitation

`host_ref` names the solid to cut a punched opening into. **`massing.json` has no exterior envelope
element at P5**: its `elements[]` carries `slab`, `column`, `core_wall`, `roof_deck` and `parapet`, and
the only perimeter geometry is four parapet strips at `z 820…910`. So **every `host_ref` in the worked
example is `null`** and a punched window in the grid is a glazed panel in a plane, not a hole
(`07` §8.3.6). A project that needs a real cut adds a `facade_wall` kind to `massing.json` through
`07` §12 step 1 — **P3's table, not yours** — and this file then resolves `host_ref` to that element's
id with no other key moving. Never invent a host.

The test for a host is narrow on purpose: an element of kind **`plinth` or `parapet`** whose
`profile_cm` lies on this facade line — the only two kinds whose outline can legitimately lie on a
facade line without being the wall behind it. No element in the example qualifies.

### 6.7 Panel `kind` is geometric; the file may name nothing else

No MAXScript class, modifier, plugin or MCP tool name may appear in `facade_grids.json` — not in a
`kind`, not in `source.reference` prose, not in an `origins` formula. A `vision` panel is not any
renderer's glass; `material_role` is a role, never a material class (`07` §8.3.6, §12).
**CORRECTED (2026-10-06):** this sentence used to say "a role P7 resolves"; **S6/P7 was cancelled on
2026-10-05** and resolves nothing — the role stays a role, and the **user** applies materials by hand.
Every panel carries `layer: "05_FACADE"` and **no builder in this pipeline emits layer code**.

### 6.8 The files are builder output

`facade_grids.json` and both CSVs are **emitted**. A hand edit breaks the audit trail `G-64` protects:
a panel whose rectangle no longer matches its `derives_from` is a hand-edited derived value in a file
nobody recomputes. **Verify the builder by recomputing it from `dimensions.json`** — not by trusting it,
not by repairing it.

---

## 7. The 3ds Max step — the live gate

**`facade_tables.py` emits no MAXScript, so there is no `fileIn` here. The consumer of the CSV is live
Max, and it is mandatory.** Contract §9 is the gate and the **orchestrator performs it** — the same
standing guard as P3/P4, table-shaped: **an emitted CSV is not done until it has been placed in Max and
counted.**

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Count the rows** | `N` = data rows of `world_table.csv`, from Python. Not from the builder's log | `N == len(panels)`, independently computed |
| 2 | **Build one prototype per distinct `component_ref`** | At a scratch position, sized `width_cm × height_cm × thickness_cm` from `world_table.csv`. The **verified placement primitive** is `Box(width:, length:, height:, pos:)` — geometry centred on `pos.xy`, base at `pos.z`, scene units cm, scale 1.0, so **no conversion happens** (`CHECKPOINT.md` §"Scene units and placement semantics", P3, 2026-10-04, control in the same batch). **`Box` is the gate's primitive, not a value any spec file may carry** (§6.7) | `prototypes == count(distinct component_ref)`; every prototype's name is the component `name`, hyphen-free (`11` N1) |
| 3 | **Place instances** | **Copy, then rebind the base object:** `n = copy proto` followed by `n.baseObject = proto.baseObject`. That is the measured route; **`setCopyMode` does not exist** in this build (`Type error: Call needs function or class, got: undefined`, re-measured 2026-10-05). Set the copy's transform to `(x_cm, y_cm, z_cm)` with **`n.rotation = quat rot_z_deg [0,0,1]`** — `rotationZ`/`rotationX`/`rotationY` likewise do not exist. **One script per call, under ~2 s** — `execute_maxscript` runs on Max's main thread and a long script freezes the UI | Every placed node named after `instance_id` (`PNL_001`, `-` → `_`) |
| 4 | **Assert the count** | `objects.count == prototypes + M` | Exact equality, read back — not assumed |
| 5 | **Prove the instances are real reference instances** | An instance shares its prototype's `baseObject`; a copy does not. **Control: one deliberate copy in the same batch must report `false`.** If the discriminator does not discriminate, that is the finding — not a pass | The instance check reports `true` for the real instance and `false` for the deliberate copy, **in the same call** |
| 6 | **Measure a deterministic sample of 5 placed nodes** | `node.min` / `node.max` on five placed nodes, compared against the facade-local rectangle transformed to world — computed **independently in Python** from the CSV, not read out of `facade_grids.json` | Every axis within `tolerances.linear_cm`. A larger mismatch is a real inconsistency: **report both figures and stop**, never nudge a node or widen the tolerance |
| 7 | **Delete everything and prove it** | §9, then assert `objects.count == 0` | Zero. Not "the gate objects are gone" — zero |
| 8 | **Record every measured number** | `N`, `prototypes`, `M`, the four assertions, and the worst deviation in step 6 | Written down. **If any of it cannot be executed, say so — an unmeasured table is an unverified table**, and the gate is `NOT RUN`, not `pass` |

**UNVERIFIED, and the gate is what settles it — treat a throw as a measurement, not a nuisance:**

| Claim | Status | What you do |
|---|---|---|
| **Rotating a node after creation** — `rot_z_deg` applied to a placed instance | **UNVERIFIED.** `CHECKPOINT.md` records no transcript; `max-massing.md` §7 lists it as UNVERIFIED too. The `Box` placement primitive has no rotation in its verified call shape | Apply it and record what came back. **A rotation that throws is a finding that goes in `CHECKPOINT.md` and on `ESCALATED` — it is not a reason to place unrotated boxes and call the gate passed.** This is the first live test of `run_angle_deg` |
| **Copy/instance mode producing a shared `baseObject`** | **UNVERIFIED.** No transcript for the discriminator in this repo; `CHECKPOINT.md` (P4b-r) records only the related fact that `delete <base>` does **not** delete its instances | Run the deliberate-copy control in the same batch. A uniform `true` across both is a **broken probe**, not a pass (`AGENTS.md`, §"The one rule that matters most") |
| `3dsmax-mcp_clone_objects` in `mode: "instance"` as an alternative to scripted copy mode | Not required — scripted copy mode is contract §9's route. Use it only as a second measurement, and record which route produced the nodes | A disagreement between the two routes is a finding |

**Never assemble a large node set in one call.** `execute_maxscript` is main-thread and single-scene;
place in batches, and delete each batch in the call that created it (§9). The Chaos Scatter clothing
callback crashed Max under a 20-modifier stack (`CHECKPOINT.md` §"NEW HAZARD", P4b-r) — this gate adds
no modifiers, and must stay that way.

---

## 8. Verification — the completion gate

Check every row. **The validator covers the mechanical subset only**; rows 3, 4, 6, 7, 12, 14, 15 and 16 are yours.

| # | Gate | Checked by |
|---|---|---|
| 1 | `python scripts/validate_specs.py --dir <specs_dir> --build` exits **0** with **`FAIL 0`**, and the same command with `--warnings-as-errors` also exits **0** with `FAIL 0` | the transcript of both runs. **Both modes, not one** |
| 2 | **`G-57`…`G-70` all PASS, or SKIP with a stated reason.** A SKIP is not a pass (`07` §9.6). `G-70` **always** SKIPs at lint time — it observes an emitted CSV; the builder asserts it instead, and §7 observes it for real. `G-63` / `G-68` SKIP with a reason when the registry is absent | you, reading the `--json` output row by row |
| 3 | **Every `G-57`…`G-70` was proved to fire by fault injection** on a **temp copy**, and the failure it produced is recorded | you — one injected defect per rule, on a copy, never on `examples/` |
| 4 | **Determinism proved by construction**: the same inputs built into **two temp dirs** are **byte-identical** to each other and to the committed artefacts | you — `diff`/hash both outputs, report the result |
| 5 | **`G-70` fires on both of its injections** — a dropped table row, and a `rot_z_deg` that disagrees with `run_angle_deg`. The builder refuses and names it | you, on a temp copy |
| 6 | Every `origins` entry is `derived` with a non-empty `derives_from` resolving in `dimensions.json`, `massing.json` **or this file**; every `origin_inputs` path resolves; `tolerances` equals `dimensions.json`'s, **unwidened** | **G-64**, **G-31** |
| 7 | `run_angle_deg` recomputed by hand for **all four** facades matches, and **no value anywhere in the file derives from `direction_deg`** | **G-57** — the field that would be reached for is the one that is wrong (§6.1) |
| 8 | Per `(facade, level, bay)`: Σ panel areas == `bay_width_cm[b] × height_cm` within `area_m2`; and per `(facade, level)` the same sum == `length_cm × height_cm`; no two panels overlap in their interiors; every panel lies inside **its own bay's** rectangle | **G-61** — the tiling unit is `(facade, level, bay)` (§6.3) |
| 9 | **Every `dimensions.openings[]` entry is referenced by exactly one panel**, whose rectangle equals the opening's — u-range `[position_cm - width_cm/2, position_cm + width_cm/2]`, v-range `[sill_cm, head_cm]` — and whose `kind` lists the opening's `type`. **Two panels for one opening is a FAIL, not a nicety** | **G-62** (§6.2) |
| 10 | **Every `u` axis has `bay_index: null` and every `v` axis a real bay index**; each bay's v slice runs `0 → height_cm`; a bay with no opening contributes **exactly** its `level_base` and `level_top` | **G-58** (§6.3) |
| 11 | Every panel's four edges land on declared axes at matching offsets; a `full_height` panel spans `0 … height_cm` and names **its own bay's** `level_base` / `level_top` axes | **G-60** |
| 12 | **No sliver**: no panel's `height_cm` is smaller than the joint P6 will inset it by, and every such panel's v edge traces to an opening **in its own bay**. A 10 cm ribbon under a window head is a shared v grid, not a design | you — §6.3.1's recognition rule. This is the defect the first generated grid actually shipped |
| 13 | **`layer == "05_FACADE"`** on every panel and every name is hyphen-free | **G-59**, `11` N1 |
| 14 | **The §7 gate ran, and every number is recorded**: `N`, `prototypes`, `M`, `objects.count == prototypes + M`, the instance-vs-copy discriminator with its `#copy` control, the worst deviation over the 5 measured nodes, and `objects.count == 0` at the end | you — the transcript. **"The CSV exists" is not this row.** An unmeasured table is `NOT MEASURED` |
| 15 | **No `host_ref` is non-null** unless a `massing.elements[]` entry of kind `plinth` or `parapet` has a `profile_cm` on that facade line, and every non-null one is reported as a change P3's table must make first | **G-59**, `07` §8.3.6 (§6.6) |
| 16 | Nothing was filled silently from `09`'s do-not-default list, and every P5-flagged `A-nnn` from §4 step 2 is named in the report | you |
| 17 | **No MAXScript class, modifier, plugin or MCP tool name appears anywhere in either emitted file or in `source.reference`**, and no layer code was emitted | you — grep the artefacts, read `source.reference` |

---

## 9. Cleanup

Cleanup is part of the build, not a chore after it.

| # | Rule | Evidence |
|---|---|---|
| 1 | **Delete every gate node in the same call that created it.** If a call fails or is aborted, **sweep** — do not assume nothing was created | A failed/aborted probe leaves its objects behind; eight orphans accumulated across aborted probes and had to be swept (`CHECKPOINT.md` §"Scene units and placement semantics", P3, 2026-10-04) |
| 2 | **Delete instances before prototypes.** `delete <base>` does **not** delete its instances — after `delete bx`, the instance survived | `CHECKPOINT.md` §"Reference claim-by-claim pass", P4b-r, 2026-10-04. Deleting prototypes first leaves a full set of orphans that look like a clean scene |
| 3 | **The sweep is explicit** — `3dsmax-mcp_delete_objects` with CSV-derived names, never "delete everything", and **compare `objects.count` before and after** — the count is the evidence | You are not the only tenant of that session; a blanket delete destroys the user's own work (`11` H12) |
| 4 | **Sweep backwards and confirm the count**: `for i = objects.count to 1 by -1 do ( delete objects[i] )`, then assert `objects.count == 0` before finishing | A delete that does not remove the node in the same call has been measured in this repo (`max-nurbs.md` §9 row 7) |
| 5 | Place and delete in **batches**, one script per call under ~2 s | `execute_maxscript` is main-thread; a long script freezes the UI (`01` §1.2, `AGENTS.md`) |
| 6 | A **bare modifier is not a node and cannot be deleted** | This gate adds no modifiers — keep it that way (§7) |
| 7 | Cleanup never touches the massing or NURBS geometry from S2/S3 — it stays. Only gate prototypes, instances and orphans are removed | `11` §6 delivery checklist |

---

## 10. Escalation policy

S4a computes; it does not design, and it escalates anything it cannot build honestly.

| You may decide alone | Boundary |
|---|---|
| Which `07` §8.3 key a piece of grid data belongs at; axis, panel and type id assignment and ordering | If a value does not fit a key, escalate — never invent one (`07` §12). Ids ascend, zero-padded, fixed order (§4 step 8) |
| Which of the six kinds a cell is, by the stated order | If two kinds are defensible **and the choice changes the panelisation**, escalate with both readings |
| Whether an axis pair within `linear_cm` merges | Merge, and record what merged. Never widen `linear_cm` to avoid the decision |
| Optional keys — omit rather than guess | An honest omission beats an invented value |

### 10.1 You must stop and ask

| Topic | Why | Goes to |
|---|---|---|
| **A non-rectangular, curved, or otherwise not-one-straight-segment facade run** — a run that is not the single segment `start_corner_cm → end_corner_cm`, or a facade closed over a footprint vertex that does not exist (`01` §3, S4a refusal case) | There is no `kind` for it: `run_angle_deg` is one angle for the whole run, and the grid is a rectangle partition in `(u, v)`. Approximating a curved run with a straight one is a wrong model that validates | the user, via S1 — facade composition is `E5` |
| **A project that needs a host wall to cut a punched opening into** | `massing.json` has **no exterior envelope element at P5**, so every `host_ref` is `null` and a punched window is a panel in a plane, not a hole. A `facade_wall` kind is a **`07` §12 step 1 change to a P3 table**, not a field you may fill (§6.6) | **S2's owner**, via `07`'s owner — S4a never edits `massing.json` |
| **A bay whose curtain-wall pier exceeds `2 × D-OP-12`** (i.e. wider than 30 cm) | It does **not** break the build: the pier reads as `blank`, a wall return, which is the correct reading of a wide pier and violates no default (§6.4). What it means is a **composition decision** — a 40 cm opaque strip where a frame member was expected | the user (`E5`), with the pier width and the reading you took. **Never widen the threshold** |
| **An `openings[].type` outside the §5.11 vocabulary** — anything but `window`, `door`, `entrance`, `curtain_wall` | `panel_types[].opening_types` and the whole classification hinge on the four names; a fifth type has no rule in §6.5 and would be classified as if it were `window`. `G-28` already constrains the input | **S1** — an input vocabulary change |
| **A panel would land on an elevation S1 never described and recorded** | `01` §3 lists this as a refusal: that is `E5`, an escalation, not a default. Inventing an elevation is inventing a design decision | the user, via S1 |
| **A transom line a client expects to run continuously across a whole elevation** | Per-bay v axes mean transoms are continuous **within a bay**, not across the run (§6.3). That is the accepted cost of the rule that stopped the 10 cm sliver, and a request to restore continuity is a request for the shared grid | the user (`E5`), with the sliver's numbers as the argument |
| **A missing or contradictory dimension** — a bay, an opening extent or a level height the derivation needs and `dimensions.json` does not hold, or two keys that disagree | S4a may not fill a dimension and may not hand-edit a locked file | **S1** |
| **Any fact not in `CHECKPOINT.md` §"Verified facts"** — including whether rotation after creation works (§7) | §1.2: S4a escalates for an orchestrator probe, it does not open one | the orchestrator |

### 10.2 How to ask

A question list, not a paragraph — one line per question:

```
<dotted key path> — <the competing values with units> — <what each would change in the panelisation> — <your recommendation, if you have one>
```

Nothing may be recorded as blocked, impossible, non-buildable or non-existent without a transcript showing
the attempt and the exact error. **A negative needs the same discipline as a positive** — this repo has
shipped fabricated negatives (`CHECKPOINT.md` §"Incident log"). "There is no way to panelise a curved
run at P5" is a claim about the **schema** and you can support it by naming §6.1; "MAXScript cannot do
X" is a claim about the **environment** and needs a transcript.

---

## 11. Anti-patterns and incident guards

This stage builds a table that will be placed in a live scene, and its failure modes are quiet: a
partition that covers its facade and is still wrong.

| Anti-pattern | Instead |
|---|---|
| **AP-1 · Deriving a panel's rotation from `direction_deg`** — or emitting `rot_z_deg` from it | `run_angle_deg = atan2(end.y - start.y, end.x - start.x)`, the only rotation source (`G-57`, §6.1). `F-S` and `F-W` each differ from their facing by 180° |
| **AP-2 · Sharing one v grid across the facade because curtain-wall transoms run continuously** — or, from the other side, assuming an opening needs **several** panels | The `v` division is **per bay** (§6.3). The shared-grid reasoning looks defensible and produced `PNL-024`: a `180 × 10 cm` `punched_window` sitting 10 cm below a window head, because `OP-G-02`'s entrance `head_cm = 260` crossed `OP-G-01`'s window running `90 → 270` in a **different bay**. **Exactly one panel per opening**, and a bay with no opening is one whole `blank` (`G-62`, §6.2, §6.3.1) |
| **AP-2b · Deleting a sliver panel instead of fixing the axis that made it** | Find the axis that produced the sliver's v edge and name the opening on the other bay that owns that offset. The panel is downstream of the axis; a hand-deleted panel leaves the grid wrong and the next rebuild puts it back (§6.3.1, §6.8) |
| **AP-3 · Duplicating axis offsets onto the facade entry or the panel** — restating `bay_offsets_cm`, or putting an offset on a panel beside its four axis ids | `offset_cm` on `axes[]` is the **only** place a division position is stated; `bay_offsets_cm` and `bay_centre_cm` are cumulative sums of `bay_width_cm`, nothing else. A second copy is a second number to drift (`G-58`, `G-60`) |
| **AP-4 · Classifying a pier by an invented thickness threshold** — "mullions are under 20 cm, so 20" | The threshold is `D-OP-12 × 2`, derived and recorded as such (§6.4). A pier wider than it is `blank` — a wall return — and that is not a defect to patch by widening the number |
| **AP-5 · Emitting layer code**, or a "fix" for the nodes landing on the wrong layer | It cannot work: **nine routes ruled out**, every one of them executed (`agents/max-assembly.md` §6.3) — `node.layer` is read-only, `LayerManager` has no setter, `manage_layers`' vocabulary is exactly `{list, create, delete}`, `set_object_property` dies on the same read-only write. **CORRECTED (2026-10-06):** this cell used to say "**S5 applies it** through `assembly.json.layer_map`" and "six routes". **S5 does not apply it either** — no stage does, and the action name will never be found. **Layer is data (`07` §8.1.3), no builder emits layer code (`G-79`), and the user applies it in the Layer dialog** |
| **AP-6 · Widening `tolerances`** — bumping `linear_cm` so a merge, a hit test or an area sum comes out clean | `tolerances` is copied **verbatim** from `dimensions.json`. `G-16`'s ranges and `G-32`'s recomputation are calibrated to it. A wider tolerance is a lie about the model, and it hides the axis pair 0.2 cm apart that made the ambiguity |
| **AP-7 · Hand-editing a generated JSON** so the next rebuild silently destroys the edit | Both files are builder output; a divergent rebuild is **refused, naming the first differing key path** (§2.2). Verify by recomputing from `dimensions.json` (§6.8) |
| **AP-8 · Treating "the CSV exists" as done** | The gate is §7: place the instances, count them, measure five of them, delete everything. This is the table-shaped equivalent of P3/P4's `fileIn` + `node.min/max`, and an unplaced table is an unverified table |
| **AP-9 · Putting a Max class, modifier, plugin or MCP tool name in a spec file** — `kind: "CoronaGlass"`, `material_role: "CoronaMultiMat"`, a tool name in `source.reference` | `kind` is geometric and `material_role` is a **role** (`glazing`/`opaque`/`frame`). §12's standing rule is why these names are correct (`07` §8.3.6, §6.7). **CORRECTED (2026-10-06):** this cell said "a role that P7 resolves"; **P7/S6 was cancelled on 2026-10-05** and no stage resolves it — the user assigns materials by hand |
| **AP-10 · Sorting, renumbering or normalising `bay_index`** — or deriving an opening's position from `bay_centre_cm` | `bay_index` is **positional and meaningful**, preserved verbatim (`01` §3). An opening's u-range is `position_cm ± width_cm/2`, measured from `start_corner_cm`; the bay centre is a separate derived array |
| **AP-11 · Letting the bay's v grid cut a `mullion`**, giving a `mullion` / `transom` an `opening_ref`, or reading rule 8.3 as "inside the opening's u-range" | A qualifying pier column is emitted **once per `(facade, level, bay)`**, `full_height: true`, `v_min == 0` / `v_max == height_cm`, bracketed by **that bay's** `level_base` and `level_top` axes. The condition is **adjacent to** the opening's u-range — a pier flanks its opening, it is not inside it (§6.5) |
| **AP-12 · Dropping a `level_base` or `level_top`** — or merging across a storey boundary — when sills coincide | Both are v axes and both must exist **for every bay**: each bay's slice runs `0 → height_cm` within tolerance, and a bay with no opening contributes **exactly** its two (`G-58`). A bay missing its top is not a closed rectangle, and `G-61` will fail with a number, not a reason |
| **AP-13 · Asserting a panel count and treating the builder's number as wrong** (or the reverse), or multiplying axis *counts* to get cells | **No gate assumes a count.** The gates are the two area sums, one panel per opening, the total join and the table census (`G-61`, `G-62`, `G-68`, `G-70`). Cells are `(axes - 1) × (axes - 1)` **per bay**: contract §4.1 works `F-S`/`LVL-00` by hand to **28 panels** (bay 0 → 9, bay 1 → 6, bay 2 → 9, bay 3 → 4 after the mullion merge) and puts the whole model at **≈ 110 … 130**. Record any prose/arithmetic disagreement as an objection rather than editing a panel to fit |
| **AP-14 · Reporting the gate as passed on the CSV alone**, or writing "matches" where a number belongs | `MEASURED` is a **number**: `N = …`, `prototypes = …`, `M = …`, worst deviation `… cm`. If the gate could not run, write `NOT MEASURED` and say why (§12) |
| **AP-15 · Naming `geometry_qa`, `contact_check` or `scene_qa`**, or routing the gate through them | **Those tools do not exist.** The gate is `3dsmax-mcp_execute_maxscript` plus a count and a `node.min`/`node.max` read-back |
| **AP-16 · Concluding the bridge is broken because one call errored** | A large set of names in the connected toolset belongs to the **Rhino** server and fails confusingly against Max (`AGENTS.md` §"MCP tool-name collisions"). Only `3dsmax-mcp_*` acts on Max. And **`mcg_*` and `curve_model` do not exist at all** — record that, do not emulate it |
| **AP-17 · Rewriting a reference or a sibling stage's contract on suspicion** | They are **unverified, not disproven**. Verify claim by claim, then correct only what actually fails (`AGENTS.md`, §"The one rule that matters most") |

### 11.1 Context discipline

You are a worker with a small budget; the main thread is the scarce resource (`AGENTS.md`
§"Context budget"). **Read `07` §8.3 and §9.8 once**, and `dimensions.json` once, end to end — never
re-read the grammar to settle one classification rule. **Compute, don't transcribe.** The whole stage is
arithmetic on ≤ 16 openings, so a hand recomputation of **one bay** — its v axes, its cells, its
openings' single panels — is enough to catch a wrong builder, and it is where the sliver of §6.3.1
either appears or does not.

---

## 12. Return contract

Return **exactly** this, **≤ 12 lines** — no file dumps, no JSON blobs, no transcript excerpts:

```
S4a <project id>
FILES: <path> (<n> lines) · <path> (<n> rows + header) · <path> (<n> rows + header)
VALIDATOR: scripts/validate_specs.py --dir <specs_dir> --build -> exit <n>  (PASS <n> · FAIL <n> · WARN <n> · SKIP <n>)
G-57..G-70: <n> PASS / <n> SKIP — <for each SKIP, the reason the check could not be evaluated; G-70 always SKIPs at lint>
BUILDER: scripts/facade_tables.py --stage all -> exit <n> · <n> facades / <n> axes / <n> panels (<by kind>) · <n> rows per CSV · run_angle_deg <F-S/F-N/F-E/F-W = …>
FAULTS: G-57..G-70 fault-injected on a temp copy — <n>/<n> fired as expected · G-70 on a dropped row: <fired?> · on a wrong rot_z_deg: <fired?>
DETERMINISM: two temp dirs byte-identical = <yes/no> · equal to the committed files = <yes/no>
LIVE: world_table.csv placed in 3ds Max by the orchestrator · N = <n> · prototypes = <n> · M = <n> · objects.count == prototypes + M = <yes/no> · instance shares baseObject = <true>, deliberate #copy = <false> · worst |measured - expected| over 5 nodes = <n> cm (tolerance linear_cm = <n> cm) · rotation applied = <yes / THREW: …>
CLEANUP: <n> instances deleted before <n> prototypes · objects.count after = <n> · scene otherwise as found
P5-RECHECK: <A-nnn ids> — <each named, or "none">
ESCALATED: <n> — <one line each: the topic, the question, whether it is answered>
OBJECTIONS: <one line per defect in a file you do not own, naming file and section, or "none">
INCOMPLETE: <what you could not do, or "none">
```

Rules for the fields:

- **Line and row counts** are the real counts from disk. The validator and builder lines are only valid
  with a transcript: paste the exit code you observed; if you did not run one, write `NOT RUN` and say
  why on `INCOMPLETE`. **`SKIP` is reported separately from `PASS`**, never folded into it.
  **`MEASURED` is a number, not an adjective** — "matches" is not evidence; `0.0 cm worst deviation` is.
  If you measured nothing, say `NOT MEASURED`.
- **`LIVE` is never optional and never inferred.** If the gate did not run, `LIVE: NOT RUN — <reason>`
  and the stage is `INCOMPLETE`. A rotation that threw is reported as a **measurement** in the same
  line, not as a warning elsewhere.
- **`P5-RECHECK` is never silently empty** — every `recheck_stage: "P5"` entry is named, because you are
  the recheck stage.
- **`OBJECTIONS`** is where a `validate_specs.py` or `facade_tables.py` behaviour that contradicts
  `07` §8.3 / §9.8 goes, and where the §10.1 `mullion`-reading question goes — one line each, naming the
  file and the section. **`INCOMPLETE`** is where you say what you could not finish; a field that hides a
  gap is worse than an admission.