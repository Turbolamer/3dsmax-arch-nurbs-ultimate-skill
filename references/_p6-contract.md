# P6 contract — `assembly.json`, the `facade_wall` extension, `place_components.py`

**This file is the authority for stage P6.** It exists because four files must not drift:
`references/07-spec-grammar.md` (§8.1 amendment, §8.5, §9.6 amendment, §9.9),
`scripts/validate_specs.py` (`G-38` amendment, `G-71`…`G-81`), `scripts/build_spec.py`,
`scripts/place_components.py`. Where an implementation wants a different key name, a different id
pattern or a different formula, **this file wins** — the same contract mechanism P5 used
(`references/_p5-contract.md`).

Decided by the orchestrator, 2026-10-05. Inputs read from `examples/dimensions.json`,
`examples/massing.json`, `examples/components_registry.json` and `examples/world_table.csv` of
project `pavilion-01`.

---

## 0. Standing rules that constrain this stage

| Rule | Consequence for P6 |
|---|---|
| `07` §11 + §12: **no spec file may name a MAXScript class, modifier, plugin or MCP tool** | `assembly.json` carries geometric and role names only. A cut is `kind: "difference"`, not `BooleanModifier`. A scatter is `kind: "scattered"`, not `ChaosScatter`. The *builder* owns the class names. |
| `07` §2 + G-8: centimetres, degrees, every length key ends `_cm` | `position_cm`, `u_range_cm`, `v_range_cm`, `depth_cm`, `wall_thickness_cm`, `scale_from`/`scale_to` are unitless ratios. `rot_z_deg` is an angle. |
| G-32 | Every generated placement and cut is `derived` with a `derives_from` naming a real path in `world_table.csv` / `dimensions.json`. |
| **P6 decision: `layer` stays data, permanently** | See §1.3. `layer_map` is declared and linted, and **no builder emits layer code**. |

---

## 1. The two P6 blockers, both now CLOSED by execution

Both were live probes run by the orchestrator in the main thread on 2026-10-05. Agents **must not**
re-run either; the transcripts are in `CHECKPOINT.md`.

### 1.1 Layer assignment — a verified negative, nine routes ruled out

There is **no way to assign an object to a layer from this bridge.** Not from MAXScript, not from
`3dsmax-mcp_manage_layers`, not from `3dsmax-mcp_set_object_property`.

- `LayerManager` in this build exposes **only** `newLayerFromName`, `getLayerFromName`, `getLayer`.
  It has **no setter of any kind** (verified with a bogus-name control in the same batch, which threw).
- `node.layer = <x>` throws `Property is read-only: layer` for a string, for an integer index, and for
  a `LayerProperties` mixin.
- `3dsmax-mcp_manage_layers`' action vocabulary is **exactly `{list, create, delete}`**. 40+
  candidates — including `rename`, for which the tool's own schema carries a parameter — all return a
  uniform `Unknown layer action: X`. The probe was calibrated by observing that `create` and `delete`
  return *distinct* argument errors (`name is required for create`), so the batch could tell a real
  action from a fake one.
- `3dsmax-mcp_set_object_property` with `property=layer` emits `node.layer = <value>` and dies with the
  same read-only error. A **positive control** on the same tool (`property=pos`) succeeded, so the tool
  works and `layer` is the blocker.

**Consequence, and it is final:** `assembly.json` declares `layer_map` as **data**, linted against the
closed vocabulary of `07` §8.1.4, and the emitted MAXScript **must not contain a layer-assignment
statement**. A builder that tries to apply layers is a build FAIL, not a silent no-op. Layer
application is a human action in the Layer dialog.

### 1.2 The modifier-stack hazard — MEASURED, and a timeout is its only symptom

The bounded ladder was run deliberately on a clean empty scene, one rung per call:

| rungs on one `Box` | result |
|---|---|
| 1 · 2 | `Extrude` and `Bevel` **throw** on `addModifier` (`mods=0`) — the P4b-r "6 unattachable modifiers" finding, re-confirmed. Not a hang. |
| 5 | clean, 38 ms total |
| 10 | clean, 28 ms total |
| **20** | **`execute_maxscript` timed out; `get_scene_snapshot` then timed out; `get_bridge_status` then aborted. Max froze on the main thread, was killed, and the machine rebooted.** |

**Binding rules on the emitted script:**

1. **≤ 5 modifiers per `execute_maxscript` call.** `place_components.py` must chunk.
2. **> 10 modifiers on a single node is forbidden.** A host wall with more than 10 cut boxes must be
   built in **separate passes** (collapse, or one cutter per node) — never as one 20-deep stack.
3. The exact breaking point between 10 and 20 is **not established and must never be re-measured.**

**Also note for §4:** a timeout does **not** mean the bridge is down. Verify with a cheap
`get_bridge_status` before drawing any conclusion.

---

## 2. The `host_ref` decision — a `facade_wall` kind is added to `massing.json`

**The problem.** `massing.json` has no exterior envelope: only `column`, `core_wall`, `parapet`,
`roof_deck`, `slab`. So `host_ref` is `null` for all 136 panels, and P6 — the stage that exists to cut
openings — has nothing to cut.

**The decision.** Add a **`facade_wall`** element kind through `07` §12 step 1 (P3's change table), with
a matching `G-38` clause. This re-opens one closed file deliberately, and the reason is recorded here
so it is not read as drift: a cut path that cannot be exercised is not worth building.

### 2.1 The new kind

| Property | Value | Note |
|---|---|---|
| `kind` | `facade_wall` | added to the `§8.1.1` enum |
| `layer` | `05_FACADE` | added to the `§8.1.2` fixed table |
| grouping kind | `facade` | already reserved in `§8.1` "reserved for P5/P6" — this is that reservation being used |
| `storey_index` | the storey it belongs to | never `null` |
| `profile_cm` | the facade run banded **inward** | see below |
| `z_range_cm` | `[level.elevation_cm, level.elevation_cm + level.height_cm]` | full storey height, tol `linear_cm` |

**Geometry: one prism per `(facade, level)`.** The band runs from `facades[i].start_corner_cm` to
`facades[i].end_corner_cm` and extends **inward** (toward the building interior) by
`facade_wall_thickness_cm`. Inward, not outward: the facade panel line sits on the corner, and a wall
banded outward would push the envelope past the panel plane. This mirrors the existing `parapet_bands`
helper's inside-the-outline reasoning.

**Count for the example: 4 facades × 2 levels = 8 `facade_wall` elements**, so `massing.json` goes from
**13 → 21** elements and the emitted `massing.ms` from **18 → 27** nodes.

> **Correction, 2026-10-05, after the first build.** Revision 1 of this line said `massing.ms` goes
> 18 → **26**. That was wrong, and the error was mine: `facade_wall` elements go into a grouping of
> kind `facade`, and `G-40` requires every element in exactly one group, so they add a **fifth
> `Dummy`** as well as eight `Box`es. 22 `Box` + 5 `Dummy` = **27**. The `Dummy` is the missing term in
> any node-count prediction here — recompute it rather than adding the element count.

### 2.2 `facade_wall_thickness_cm` — an ASSUMED value with a ledger entry

`dimensions.json` has no facade build-up, and inventing a silent default is the P5 trap. So:

1. `09-defaults.md` gains **one** row, in the same style as `D-CL-05` / `D-FM-10` which P5 established:

   | id | description | default | range | units | note | used by |
   |---|---|---|---|---|---|---|
   | `D-FW-01` | *reference only* — modelled thickness of an opaque facade wall band | 20 | 10–40 | cm | geometry — the band is a massing proxy; a real build-up is a curtain-wall system schedule | `A-nnn` · `pavilion-01`: **A-025** (20) |

2. `massing.json` gains a `defaults` block carrying `facade_wall_thickness_cm: 20.0`, declared
   **`assumed`**, **not** `derived` — `dimensions.json` does not dimension it, so `G-64`'s derived-only
   rule does not apply and must not be stretched to cover it.
3. `examples/assumptions.json` gains **`A-025`**, shaped exactly like `A-023`/`A-024`, with
   `field_path: "massing.json:defaults.facade_wall_thickness_cm"`, `value: 20.0`,
   `recheck_stage: "P6"`, `downstream_stages: ["P6", "P7"]`.

**This makes P6's inventory exactly one assumed value**, same as P5's was one of two. The invariant
`G-38` amendment below must therefore assert that **only** that one key is `assumed` in `massing.json`.

### 2.3 `G-38` amendment — additive only

Append to the existing `G-38` row, changing nothing already there:

> a `facade_wall`'s `z_range_cm` equals `[level.elevation_cm, level.elevation_cm + level.height_cm]`
> (full storey height, tol `linear_cm`), and **every `(facades[i].id, levels[j].index)` pair has exactly
> one `facade_wall`** whose band spans that facade's `length_cm` and whose `storey_index` is `j`.

The second clause is what makes the envelope total. A missing wall is a FAIL, not a gap.

---

## 3. `assembly.json` — the schema (`07` §8.5)

`assembly.json` is the **last derived file** in the chain. It resolves
`components_registry.json` + `world_table.csv` + `massing.json` + `dimensions.json` into instructions a
builder can execute, and it is the only file that carries a `scatter` table.

### 3.1 Top level

| Key | Type | Req | Notes |
|---|---|---|---|
| `schema_version` | string | yes | semver; major must match `07` §2 |
| `spec` | string | yes | `== "assembly"` |
| `project` | string | yes | same id as the other six files (G-31) |
| `units` | string | yes | `cm` / `deg` |
| `source` | object | yes | `kind: "derived"`, naming `components_registry.json`, `world_table.csv`, `massing.json`, `dimensions.json` |
| `status` | string | yes | `draft` \| `locked` \| `superseded` |
| `tolerances` | object | yes | inherited verbatim from `dimensions.json` (G-33) |
| `origin_inputs` | array | yes | declared, per P2/P3 convention |
| `origins` | object | yes | one entry per leaf |
| `defaults` | object | yes | `panel_joint_cm`, `instance_limit_guard` — §3.6 |
| `layer_map` | object | yes | **data only** — §1.3 |
| `placements[]` | array | yes | §3.2 |
| `opening_cuts[]` | array | yes | §3.3 |
| `scatter[]` | array | yes | §3.4 |

### 3.2 `placements[]` — one per `world_table.csv` data row

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^PLC-\d{3}$`, unique, ascending |
| `component_id` | string | yes | resolves to `components_registry.json` `components[].id` |
| `source_row` | int | yes | the 1-based data row of `world_table.csv`, ignoring the header |
| `node_name` | string | yes | unique, per `11-layer-standard.md` N1 |
| `position_cm` | array | yes | `[x, y, z]`, verbatim from the CSV row |
| `rot_z_deg` | float | yes | **the CSV `rot_z_deg`**, which P5 proved equals `run_angle_deg = atan2(dy, dx)` — never `dimensions.facades[].direction_deg` |
| `instance` | bool | yes | always `true` |
| `layer` | string | yes | must equal the `layer_map` entry for its role |

`source_row` exists so the count can be asserted in **both** directions against the CSV, which is what
`G-72` does.

### 3.3 `opening_cuts[]` — one per `dimensions.json` opening

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^CUT-\d{3}$`, unique, ascending |
| `opening_id` | string | yes | resolves to `dimensions.json` `openings[].id` |
| `host_ref` | string | yes | a `facade_wall` element id in `massing.json` — **never `null`** |
| `facade` | string | yes | the opening's facade |
| `level_index` | int | yes | the opening's level |
| `bay_index` | int | yes | the opening's bay |
| `u_range_cm` | array | yes | `[u0, u1]` **along the facade run**, `u0 < u1` |
| `v_range_cm` | array | yes | `[sill_cm, head_cm]` from the opening |
| `depth_cm` | float | yes | cutter depth ≥ the host wall thickness, plus `linear_cm` |
| `kind` | string | yes | `difference` — the only legal value |

**`u_range_cm` is the one genuinely new computation in P6**, and it must be derived, not guessed:

```
u0 = opening.position_cm − opening.width_cm / 2
u1 = opening.position_cm + opening.width_cm / 2
```

`position_cm` is already measured from the bay's own origin, so this needs no facade offset — but the
**host wall's profile starts at `start_corner_cm`**, so the cutter's world position along the run is
`start_corner_cm + u`. The builder converts; the spec keeps `u` facade-local, because that is the frame
P5's whole grid is written in and mixing frames is how the P5 sliver defect happened.

### 3.4 `scatter[]`

| Key | Type | Req | Notes |
|---|---|---|---|
| `id` | string | yes | `^SCT-\d{3}$`, unique, ascending |
| `node_name` | string | yes | unique scatter node name |
| `target_ref` | string | yes | a `massing.json` element id — the surface instances land on |
| `model_refs` | array | yes | ≥ 1; a `components_registry.json` id **or** a `massing.json` element id |
| `seed` | int | yes | **1 … 31337** — deterministic (P0) |
| `instance_count_limit` | int | yes | > 0 |
| `distribution_density_pattern` | number | yes | 0…1. **P0 recorded the typo `distributionDesityPattern` as the real MAXScript name — the spec uses the corrected spelling** |
| `scale_from` / `scale_to` | number | yes | `0 < scale_from ≤ scale_to` |
| `rotation_from_deg` / `rotation_to_deg` | number | yes | `from ≤ to` |
| `collision_avoid` | bool | yes | defaults `true` |
| `layer` | string | yes | `99_DEBUG` for scatter sources |

**The example ships exactly one scatter row**, targeting `ground_pad` is not a `massing.json` element
(`site_pad` is a separate object), so it targets the **`roof_deck`** element id with a single model —
a `column` element, so the 136-panel scene is not disturbed. `layer: "99_DEBUG"`.

### 3.5 Nothing else is allowed

No `materials`, no `cameras`, no `lights`, no `export`. Those are P7, P8 and P9. A row naming any of
them is a FAIL — this is how a stage boundary is enforced rather than merely described.

### 3.6 `defaults`

| Key | Value | Origin |
|---|---|---|
| `panel_joint_cm` | `2.0` | **derived from `components_registry.json:defaults.joint_width_cm`** (`A-024`). Not a new assumption — this is P5's value carried forward, and saying so keeps P6's assumed count at one. |
| `instance_limit_guard` | `2000` | derived: a guard rail on total placements, so a corrupt CSV cannot ask Max for a million instances. |

---

## 4. New invariants — `G-71` … `G-81`

Lint-time checks are `FAIL` where a static file can decide, and **honest `SKIP` with a reason** where
it cannot — the §9.6 rule, because a check that cannot be evaluated must never report a silent PASS.

| id | rule | failure |
|---|---|---|
| **G-71** | Every `placements[].component_id` resolves to `components_registry.json` `components[].id` | FAIL |
| **G-72** | **`placements[]` and `world_table.csv` data rows are equal in both directions.** Every `source_row` is a real row, every real row appears once, no duplicate `source_row` | FAIL |
| **G-73** | Each placement's `position_cm` and `rot_z_deg` **equal its CSV row** within `linear_cm` / `angle_deg`. The builder must copy the table, never recompute placement geometry | FAIL |
| **G-74** | `node_name` is unique across `placements[]`, `opening_cuts[]` and `scatter[]`, and matches `11-layer-standard.md` N1 | FAIL |
| **G-75** | Every `placements[].layer` equals the `layer_map` entry for its role; every `layer_map` key is in the `07` §8.1.4 vocabulary | FAIL |
| **G-76** | Every `opening_cuts[].host_ref` resolves to a `facade_wall` element; `u_range_cm` and `v_range_cm` lie inside the host's own extent within `linear_cm`; `depth_cm ≥ facade_wall_thickness_cm` | FAIL |
| **G-77** | Every `dimensions.json` opening has **exactly one** cut and every cut has exactly one opening — orphans fail in **both** directions | FAIL |
| **G-78** | `scatter[].seed` in 1…31337; `scale_from ≤ scale_to`; `rotation_from_deg ≤ rotation_to_deg`; `model_refs` ≥ 1 and all resolve; `instance_count_limit > 0` | FAIL |
| **G-79** | **No layer-assignment statement in the emitted MAXScript** (§1.3). The emitted file must contain no `node.layer`, no `LayerManager` setter and no layer-assignment helper | FAIL at build |
| **G-80** | **Emitted census.** After building, the emitted `.ms` counts placed instances, prototypes and committed cuts and throws on any mismatch against the table — the same device as `G-34`…`G-40` and `G-54`, and the reason P5's sliver defect could not ship | FAIL at build; **SKIP with reason at lint** |
| **G-81** | **Bounded stack.** No emitted script adds more than **5** modifiers in one call, and no single node's final stack exceeds **10** (§1.2). Multi-pass cutting is required past 10 cutters | FAIL at build |

---

## 5. `place_components.py` — CLI and obligations

```
python scripts/place_components.py --in <dir> --out <dir> [--stage assembly] [--json]
                                   [--build] [--allow-draft]
```

| Obligation | Detail |
|---|---|
| Lock gate | refuse a non-`locked` `assembly.json` unless `--allow-draft`; `--build` enforces it (the P2/P3 convention) |
| Deterministic | byte-identical output across runs and across two output directories |
| `fn`-wrapped, idempotent | one `fn mcpAssemblyBuild_<project>` + one call; re-running replaces, never duplicates (the P3 rule) |
| **No `local` at top level** | the P3 compile-error rule, `fn`-wrap the whole body |
| **Explicit-local delete form** | `local prev = getNodeByName "X"` then `if prev != undefined do ( delete prev )` — the context-dependent one-liner throws when the node is absent |
| **Instance route** | `n = copy proto` then `n.baseObject = proto.baseObject`. `setCopyMode` **does not exist** (P5) |
| **Rotation** | `n.rotation = quat <degrees> [0,0,1]`. `rotationZ`/`rotationX`/`rotationY`/`matrix3`/`angle` **do not exist** (P5) |
| **`node.pos` on a `Box`** | the **base** sits at `pos.z`. It stays true after `copy`, after `baseObject =` and after rotation. To centre, write `pos.z = cz − height/2` |
| **Cuts** | one `difference` Boolean per opening, chunked **≤ 5 modifiers per call** and **≤ 10 per node** (`G-81`). Past 10, cut in separate passes |
| **Delete by name, twice** | `for o in objects do append names o.name`, then delete by name; **run twice** — deleting a base does not delete its instances, and `for o in objects do delete o` silently skips entries |
| **Read relational properties only on committed sub-objects** | the P4b rule, not needed here but must not be violated if a NURBS surface is ever a cut host |
| **No literal surface index** | `G-56`'s rule generalises: bind every index to a variable immediately after its append |

---

## 6. `references/14-chaos-scatter.md` and `snippets/chaos_scatter.ms`

- The reference documents the **verified** parameter map from `PLAN.md` §4.1 plus the §1.2 hazard, and
  states plainly that `scatter_forest_pack` and all 14 `tyflow_*` tools are absent and must never be
  called.
- `snippets/chaos_scatter.ms` is a **library of functions**, not a scene-changing script:
  `mcpScatterApply <node> <config>` style helpers, so a caller can apply and, importantly,
  **re-apply after a rebuild**. It must be `fileIn`-able and must **create nothing on load**.
- `FpInterface` exposes `getInstanceCount()`, `update()`, `clear()`, `saveConfiguration(f)`,
  `loadConfiguration(f)` — this is the **P8 determinism hook** and `14` must name it as such.

---

## 7. The live gate — the orchestrator performs it, agents must not touch the bridge

The guard, restated: *an emitted `.ms` is not done until `fileIn` has run it and its output has been
measured against the spec's intent.* It has fired for MAXScript (P3, P4), for a table (P5) and is
armed here for both, since P6 ships **two** emitted artefacts.

| # | Gate | Pass condition |
|---|---|---|
| 1 | `build_spec.py --stage massing` | byte-identical to the committed `examples/massing.ms`; validator still `PASS 120+ / FAIL 0 / WARN 0` |
| 2 | `fileIn examples/massing.ms` | **27** nodes — 22 `Box` (21 elements + 1 `site_pad.ground_pad`) and **5** `Dummy` group parents, of which **8** `Box`es are `facade_wall` — idempotent over 3 runs, every new wall bbox measured against an independent Python prediction |
| 3 | `place_components.py` | byte-identical to the committed `examples/assembly.ms`; self-check `G-71`…`G-81` |
| 4 | `fileIn examples/assembly.ms` | **136** panels placed as instances sharing their prototype's `baseObject`, `objects.count` == 136 + prototypes, **8** walls cut with **16** cutters, sample bboxes exact, scene back to 0 |
| 5 | fault injection | ≥ 8 cases across `G-71`…`G-81`, each **proved to fire** |
| 6 | determinism | two temp dirs byte-identical |

---

## 8. Definitions of done for P6

1. `py_compile scripts/*.py` clean; `validate_specs.py --dir examples` → `FAIL 0 / WARN 0`, clean under
   `--warnings-as-errors` and `--build`.
2. `facade_wall` defined in `07` §8.1 + §9.6, emitted by `build_spec.py`, linted by `G-38`.
3. `assembly.json` defined in `07` §8.5, linted by `G-71`…`G-78`; `G-79`…`G-81` enforced at build.
4. `place_components.py` deterministic, `fn`-wrapped, idempotent, and **free of layer code**.
5. `examples/assembly.json` + `examples/assembly.ms` exist and pass **every** gate in §7.
6. `agents/max-assembly.md`, `references/14-chaos-scatter.md`, `snippets/chaos_scatter.ms` exist and
   route only to tools and classes that were **executed**.
7. `CHECKPOINT.md` updated.7. `CHECKPOINT.md` updated.

---

## P6-A result

Offline slice only. **No bridge tool was called** — no `execute_maxscript`, no `3dsmax-mcp_*`,
no MCP call of any kind. Everything below is Python + markdown.

| Fact | Value |
|---|---|
| `examples/massing.json` elements | **13 → 21** (8 × `facade_wall`, 4 facades × 2 levels) |
| `examples/massing.ms` nodes | **18 → 27** (22 `Box` + 5 `Dummy`) |
| `py_compile scripts/*.py` | exit 0 |
| `validate_specs.py --dir examples` | `PASS 120 / FAIL 0 / WARN 0 / SKIP 12` |
| `--warnings-as-errors` | `PASS 120 / FAIL 0 / WARN 0 / SKIP 12` |
| `--build` | `PASS 120 / FAIL 0 / WARN 0 / SKIP 12` |
| Determinism | byte-identical: `tmpA == tmpB == committed` for **both** `massing.json` and `massing.ms` |
| `G-38` fault injection | **3 of 3 fired** |

**⚠️ The node count is 27, not the 26 §2.1/§7 state.** §2.1 requires grouping kind `facade`
("this is that reservation being used"), and `G-40` requires every element to sit in exactly
one group — so the eight walls need a fifth grouping dummy. 14 `Box` + 4 `Dummy` = 18 became
22 `Box` + 5 `Dummy` = **27**. The contract's 18 → 26 counted the 8 new solids and omitted the
new dummy. §7's "26 nodes, **21** of them `facade_wall`" is doubly garbled (21 is the *element*
count; 8 are `facade_wall`). **The §7 gate-2 target of 26 is unreachable while §2.1 and G-40
both hold**, so the gate needs restating to 27. Everything else in §2.1 is met exactly.

### G-38 fault injection — all three caught, each by a named rule

| Mutation | Caught by |
|---|---|
| (a) delete `EL-021`, the last `facade_wall` | **G-38 clause 2** — `('F-W', level 1) has 0 facade_wall element(s) banding (0.0, 0.0, 20.0, 900.0)`. The deletion is a FAIL, not a gap |
| (b) `EL-014.z_range_cm` → `[0.0, 390.0]` | **G-38 clause 1** — `[0, 390] != [0, 420] from levels[0].elevation_cm .. elevation_cm + levels[0].height_cm` |
| (c) `EL-014.layer` → `04_ROOF` | **G-39** — `layer '04_ROOF' != '05_FACADE'; 07 section 8.1.2 fixes layer for kind 'facade_wall'`. G-38 does not own layers, so (c) is *expected* to land on G-39 |

(a) also raises 3 collateral `G-36` rows because the removed element is named by
`grouping[4]`'s `derives_from` — a hand mutation artefact, not a rule conflict. Mutants were
written to throwaway copies; `examples/` was never edited.

### Deviations from the file-ownership list — all forced, all reported

1. **`G-36` was scoped** (`validate_specs.py` + `07` §9.6). §2.2 mandates the value be `assumed`
   with an `origin_ref`; `G-36` hard-FAILed **any** non-`derived` massing origin, so §2.2 and
   `FAIL 0` were mutually exclusive. The clause is now scoped exactly the way `G-64` is for
   `components_registry.json` (`A-023` / `A-024`): an entry under `defaults.*` may be
   `assumed` + `origin_ref`, **every geometry leaf is still `derived`**. §2.2 says the value
   must not be `derived` and that `G-64`'s rule "must not be stretched to cover it"; the
   derived-only clause that actually fires here is `G-36`, the massing twin of `G-64`.
2. **`defaults` added to the `massing` `SpecDef.body_keys`** (`validate_specs.py` + `07` §4).
   Without it `G-1` WARNs "undeclared top-level keys" and `--warnings-as-errors` fails.
3. **`07` §8.1.1 `storey_index`, §8.1 key table, §8.1.1 `grouping[].kind`, §8.1.4, §4, and the
   `G-36` row** were touched alongside the two `G-38` clauses, because leaving them stating the
   old shape would contradict the change. `§8.5` / `§9.9` were **not** touched.
4. **Not done — needs one line from the orchestrator:** `init_project.py`'s `scaffold_massing()`
   still writes no `defaults` key, so a freshly scaffolded project now FAILs `G-1`
   ("missing declared top-level keys: defaults"). `init_project.py` was outside the ownership
   list. The fix is `doc["defaults"] = {}` after `doc["origins"] = {}`, mirroring
   `scaffold_components_registry`.

### Geometry emitted (all bands **inward**, flush with the corner line)

| Element | Facade / level | Plan rect | `z_range_cm` |
|---|---|---|---|
| `EL-014` / `EL-015` | F-S / 0, 1 | x 0…1800, y 0…20 | [0, 420] / [420, 820] |
| `EL-016` / `EL-017` | F-N / 0, 1 | x 0…1800, y 880…900 | [0, 420] / [420, 820] |
| `EL-018` / `EL-019` | F-E / 0, 1 | x 1780…1800, y 0…900 | [0, 420] / [420, 820] |
| `EL-020` / `EL-021` | F-W / 0, 1 | x 0…20, y 0…900 | [0, 420] / [420, 820] |

"Inward" is decided by comparing the two candidate offsets against the **site footprint
centre**, not by a winding convention: the four runs of a rectangle are not all wound the same
way round the ring (`F-S` runs with it, `F-N` against it), so a left-of-direction rule bands two
of the four outward. Corner squares therefore overlap between two bands — that is what G-38
clause 2 demands, since a mitred corner would shorten two of the four runs below `length_cm`.

## P6-C result

The **docs + snippet** slice of P6: the S5 stage contract, the Chaos Scatter reference, and the
apply/re-apply library. **No bridge tool was called** — no `execute_maxscript`, no `3dsmax-mcp_*`, no
MCP call of any kind. Nothing below was re-probed; every fact is the executed transcript §1.1 and
§1.2 already record.

| File | Lines | Content |
|---|---|---|
| `agents/max-assembly.md` | **515** | S5 stage contract: purpose, §1 one-MCP rule, §2 inputs/lock gate, §3 file ownership, §4 the 13-step procedure, §5 build commands, §6 assembly rules, §7 the live gate, §8 completion gate, §9 cleanup, §10 escalation, §11 anti-patterns, §12 return contract |
| `references/14-chaos-scatter.md` | **301** | Verified parameter map (§2, three groups), the measured hazard (§3), absent tools + substitutions (§4), `FpInterface` as the **P8** determinism hook (§5), the `assembly.json.scatter[]` mapping (§6), MAXScript traps (§8), anti-patterns (§9) |
| `snippets/chaos_scatter.ms` | **535** | `MCPChaosScatterCfg` + `MCPChaosScatterLib` — 20 functions: `config`, `configFromScatterRow`, `apply`, `rebuild`, `census`, `save`, `restore`, `snapshot`, `determinismRoundTrip`, `create`, `dispose`, `seedFromName`, `clampSeed`, `resolveNode(s)`, `setProp`, `interface` |

### Verification

| Check | Result |
|---|---|
| **`.ms` creates nothing at file scope** | **PASS.** Every `ChaosScatter()`, `Box()` and `delete` occurrence is inside a function body. The only `ChaosScatter()` call is in `fn create`; the only `delete`s are in `fn create` and `fn dispose`. File scope holds one `global`, two `struct` definitions and one `MCPChaosScatter = MCPChaosScatterLib()` instantiation |
| **`.ms` parens / brackets balanced** | **PASS.** Net depth **0** after comment- and string-stripping; zero unbalanced closers. All string concatenation is parenthesised (`("x" + (i as string))` form); every handler is `try ( ) catch ( )`, never the brace form |
| **Every 3ds Max tool prefixed `3dsmax-mcp_`** | **PASS** — 39 / 45 / 9 occurrences across the three files; zero bare `execute_maxscript`, `get_bridge_status`, `get_scene_snapshot`, `manage_layers`, `set_object_property`, `add_modifier`, `clone_objects`, `tyflow_*` anywhere. The un-prefixed names that remain are the **Rhino**-server collision list in §1.2, which is correct in that context |
| **No absent tool recommended** | **PASS.** Every mention of `scatter_forest_pack`, the 14 `tyflow_*`, `get_railclone_style_graph`, `mcg_*` and `curve_model` sits in a prohibition / substitution row. Zero in a recommended position. The `.ms` names them only inside a `never call` header comment |

### Counts

| Table | Rows |
|---|---|
| `max-assembly.md` §8 completion gate | **20** |
| `max-assembly.md` §11 anti-patterns | **21** (`AP-1`…`AP-21`) |
| `14-chaos-scatter.md` §9 anti-patterns | **15** (`AP-1`…`AP-15`) |

### The S5 procedure, as written

create prototypes → place instances → cut openings → wire scatter → census, over 13 pass-conditioned
steps. §4 step 6 places instances (`copy` + `baseObject =`, `quat <deg> [0,0,1]`), step 8 commits cuts
under the **≤ 5 per call / ≤ 10 per node** bound, step 9 wires the scatter, step 10 embeds the census
(`G-80`) in the emitted `.ms` so it throws on any mismatch.

### §8 gate rows carrying *measured* expectations

| Row | Measured expectation as written |
|---|---|
| 5 | **`objects.count == placements + prototypes`** — 136 + D for `pavilion-01`, exact equality, read back, not assumed |
| 6 | every sampled instance **shares its prototype's `baseObject`** = `true`, and the deliberate plain `copy` control = **`false`**, **in the same call**. A uniform `true` is declared a broken probe |
| 7 | **sample bboxes exact**: five nodes, worst `\|measured − expected\| ≤ linear_cm` (0.5 cm), the worst number written down |
| 8 | the **census** threw **0** times; `G-77` orphans **0** in **both** directions |
| 9 | 8 `facade_wall` hosts / 16 cutters for the worked case; `depth_cm ≥ facade_wall_thickness_cm` |
| 10 | `G-81` held: max stack observed ≤ **10**, max per call ≤ **5** |
| 19 | **`objects.count == 0`** after the gate and after **two** delete sweeps |

### Layer is final, and there is no layer code anywhere

`max-assembly.md` §6.3 reproduces all **nine** ruled-out routes with the error each one produced, states
the conclusion as **final, not an open question**, and §8 rows 11–12 make a layer statement in
`assembly.ms` a **build FAIL** (`G-79`) with the grep expectation spelled out (match count **0**). The
§1.2 forbidden list names `3dsmax-mcp_manage_layers` object assignment and
`3dsmax-mcp_set_object_property` with `property=layer` explicitly. `AP-7` repeats it. No
layer-assignment code appears in either markdown file or in the snippet — and the snippet's
`configFromScatterRow` carries an explicit comment saying `layer` is **deliberately not read**.

### Not done

1. **No live gate was run**, so no number in `max-assembly.md` §7 or §8 is claimed as measured — they are
   the *expectations* the orchestrator's gate must satisfy, per §6 of this contract ("agents must not
   touch the bridge"). §7 row 10 and §12 `INCOMPLETE` require `NOT RUN` to be reported rather than
   inferred.
2. **`G-71`…`G-81` were not fault-injected** — `validate_specs.py` and `place_components.py` do not carry
   those rules yet; that is the P6-B slice's obligation (§8 row 3 of `max-assembly.md` is where the ≥ 8
   cases get injected).
3. **Two facts remain UNVERIFIED and are labelled as such** in `max-assembly.md` §7: the *world bbox*
   after `quat` rotation against the run-angle prediction (the `quat` form itself is verified), and
   `3dsmax-mcp_clone_objects` in `mode: "instance"` agreeing with the scripted route. Also UNVERIFIED and
   labelled: Chaos Scatter sub-object wiring beyond the §2 parameter map (e.g. `addModelNode` semantics)
   and `distributionLimitCoordSpace`'s enum mapping.
4. **`references/14-chaos-scatter.md` does not claim to replace `references/railclone.md`** — it says it
   documents what supersedes railClone's *subject matter* (railClone is not installed). Deleting or
   editing `railclone.md` was not in this slice's ownership and is not done.
---

## P6-B result

Offline slice only. **No bridge tool was called** — no `execute_maxscript`, no `3dsmax-mcp_*`,
no MCP call of any kind. Everything below is Python + markdown.

| Fact | Value |
|---|---|
| `examples/assembly.json` | **136 `placements[]`**, **16 `opening_cuts[]`**, **1 `scatter[]`**, 157 `origins` entries, 1234 `origin_inputs`, `status: locked` |
| Distinct components / prototypes | 29 / 29 — one `PROTO_CMP_nnn` per distinct `component_id` |
| Cut hosts | **8** `facade_wall` elements, `EL-014`…`EL-021`; max **4** cutters on one wall |
| Cut passes emitted | **4** (`5, 5, 5, 1`), each a separate called function, max **5** `addModifier` per call |
| `assembly.ms` | 1784 lines, 5 functions, one entry call `mcpAssemblyBuild_pavilion_01()` |
| `py_compile scripts/*.py` | exit 0 |
| `validate_specs.py --dir examples` | `PASS 136 / FAIL 0 / WARN 0 / SKIP 15` |
| `--warnings-as-errors` | `PASS 136 / FAIL 0 / WARN 0 / SKIP 15` |
| `--build` | `PASS 136 / FAIL 0 / WARN 0 / SKIP 15` |
| Determinism | byte-identical: `tmpA == tmpB == committed` for **both** `assembly.json` and `assembly.ms` |
| Fault injection | **21 fired out of 21** across `G-71`…`G-81` |
| Scaffold (`init_project.py --project p6probe`, then `validate_specs --allow-draft`) | **FAIL 0** / WARN 0 (was FAIL 17) |

### Fault injection — every case fired, each by a named rule

| # | Mutation | Caught by |
|---|---|---|
| a | `placements[0].component_id = CMP-999` | **G-71** |
| b | `placements[4].source_row = 999` | **G-72** — *and* the reverse direction: `world_table.csv data row 5 has no placement` |
| c | `placements[5].source_row = 5` (duplicate) | **G-72** |
| d | `placements[2].position_cm[0]` shifted 10 cm | **G-73** |
| d2 | `placements[0].rot_z_deg = 180.0` (the facing label, not the run angle) | **G-73** |
| e | `opening_cuts[0].host_ref = EL-009` (a `roof_deck`) | **G-76** |
| e2 | `opening_cuts[1].host_ref = null` | **G-76** |
| f | `opening_cuts[2].u_range_cm = [2100, 2280]` | **G-76** — `u0 2100 lies outside host EL-014's own u extent [0, 1800]` |
| f2 | `opening_cuts[3].depth_cm = 4.0` | **G-76** — shallower than `facade_wall_thickness_cm` 20 |
| g | `opening_cuts[4].opening_id = OP-NOPE-99` | **G-77** |
| g2 | `opening_cuts[5].opening_id = OP-G-01` (duplicate) | **G-77** — *both* directions: 2 cuts on `OP-G-01`, `OP-G-05` orphaned |
| h | `scatter[0].seed = 0` | **G-78** |
| h2 | `scatter[0].node_name = PLC_001` | **G-74** |
| i | `placements[0].layer = 00_SITE` | **G-75** |
| j | `opening_cuts[0].kind = union` | **G-76** |
| k | `.layer = "05_FACADE"` injected into the emitted `.ms` | **G-79** (build-time refusal) |
| k2 | `LayerManager.setLayer 3 PLC_001` injected | **G-79** |
| l | 16 cutters forced onto one host | **G-81** — `host EL-014 would collect 16 cutters; the ceiling is 10 per node` |
| m | one function made to add 16 modifiers | **G-81** — `function 'mcpAssemblyBuild_pavilion_01_cutPass1' adds 12 modifiers in one call; the ceiling is 5` |
| n | the G-80 census removed from the `.ms` | **G-80** |
| o | `getModifier 1 host_node` (bare literal index) | **G-81** / G-56's rule |

All mutants were written to throwaway copies under `%TEMP%`; **no committed file was edited.**

### Decisions the contract left open, resolved here

1. **`layer_map` is keyed by LAYER name, not role.** §4's `G-75` says "*every `layer_map` **key**
   is in the §8.1.4 vocabulary*", which is only literally true if the keys are layer names. So the
   shape is `{"05_FACADE": [<four component kinds>], "99_DEBUG": ["scatter_source"]}` and a
   placement's role — read through its `component_id` — must be listed under exactly one key. That
   satisfies both halves of `G-75` with one comparison.
2. **`opening_cuts[].node_name` was added.** §3.3's table omits it, but §4's `G-74` counts node
   names "across `placements[]`, `opening_cuts[]` and `scatter[]`", and the cutter needs a scene
   identity for the idempotent delete-by-name pass. It is the id with `-` → `_` (`CUT-001` →
   `CUT_001`), so `N-4` holds like every other name.
3. **`v_range_cm` is level-local, which is what makes §3.3's `[sill_cm, head_cm]` consistent with
   `G-76`.** A level-1 opening has `head_cm = 270` while its host wall's `z_range_cm` is
   `[420, 820]`. So `G-76` measures `v` against **the host's own local `[0, level.height_cm]`**,
   and `u` against **the host's own corners projected onto the run unit** — both recomputed from
   the element, not read from `facades[].length_cm`, which is what makes the rule a statement
   about the wall being cut. Written up in `07` §8.5.3.
4. **`depth_cm = facade_wall_thickness_cm + panel_joint_cm` = 22.0.** One panel joint proud of each
   wall face, so the boolean never runs on two coincident surfaces. Both operands come from a locked
   spec, so the extra centimetre is derived rather than invented.
5. **`instance_limit_guard = 2000` and `scatter[].seed = 26010`** are fixed literals in the builder,
   with `seed` documented in `07` §8.5.4 as *never a draw* — that is the P0 determinism claim.
6. **One driver `fn` plus its cut passes, emitted in that order.** A MAXScript `fn` cannot see the
   driver's locals, so each pass takes its `#(hostNode, cutterNode)` pairs as a parameter and
   returns its committed count for the `G-80` census. Pass functions come **before** the driver
   because MAXScript executes top-level statements in order, and the entry call is last.
7. **`07` §10 was not touched.** The worked-example table does not yet mention
   `examples/assembly.json`; §10 is outside this slice's ownership.

### The 17-row scaffold defect — root cause and the fix

`G-36`, `G-49`, `G-57`, `G-64` and `G-66` all sat behind a guard reading
`if status is not None and not session.allow_draft`, so `--allow-draft` made them evaluate an
**empty** scaffold stub and fail on the absence of content. `G-4` never did that: `--allow-draft`
is a **status** flag there, turning a non-locked status into a SKIP. The fix is one shared
predicate pair, `_is_empty_placeholder()` / `_draft_skip_reason()` in `validate_specs.py`:

- a draft **with content** is still evaluated under `--allow-draft` (the flag's point);
- an **untouched** stub is not evaluated even under `--allow-draft`. The question is decidable:
  all five computed files keep their content in **arrays**, so an empty array tree plus an empty
  `origins` is exactly what `init_project.py` writes.

Verified in both directions: the fresh scaffold is `FAIL 0`, and a draft stub given one
deliberately bad `component_id` **does** FAIL under `--allow-draft` (`G-71`), so the carve-out
does not gut the flag. `--build` still refuses every draft at `G-4`. Nothing about a `locked`
file changed, and the five dispatchers now share one implementation instead of five copies.

### Deviations / things needing a decision

1. **`07` §9.6/§9.7/§9.8 still say "`--allow-draft` forces them to run and they will then
   fail".** That sentence is now true only for a draft *with content*, and this slice's
   ownership was §8.5 + §9.9 + the §4 row, so those three paragraphs were left alone. The
   corrected rule is written in full in the new **§9.9**, next to the place it is used. One edit
   to §9.6–§9.8 by the orchestrator would close it.
2. **`check_massing_rules` and its three siblings were edited** — only the draft-guard condition,
   in the four dispatchers, not the `G-34`…`G-40` rule bodies and not the `G-38` row. Without
   this, `G-36` (one of the five offenders) cannot be fixed at all.
3. **`assembly.json` is now `defined`** in `07` §4 and in `SPEC_INVENTORY`, and is in
   `SEEDED_FROM_EXAMPLES`, so `--from examples` carries it. `init_project.py` gained
   `scaffold_assembly()` (a real §8.5 stub, replacing the reserved skeleton) and its
   `INVENTORY` row moved `reserved` → `defined`, with the reserved loop skipping it explicitly.
4. **`Boolean().operation = 1` is the one emitted constant NOT measured live.** It is the MAXScript
   Boolean modifier's documented difference index (0 union, 1 difference, 2 intersect), and it is
   the value §7 gate 4 must confirm. It is a named module constant in `place_components.py` so it
   is one edit, not a search.
5. **`getModifier` / `deleteModifier` / `classOf` on the host's own stack are also unmeasured.**
   The idempotent host-stack reset uses them; the hosts arrive from `massing.ms` with **no**
   modifiers, so the evaluated-stack and base-stack indices coincide and the walk is unambiguous.
   Any failure surfaces as the `G-80` census mismatch rather than as a silent wrong scene.
6. **`install_skill.py` `collect_files()` still ships no `scripts/`** — `env_preflight.py`,
   `validate_specs.py` and now `place_components.py` are all absent from an installed copy. That is
   the known P10 packaging gap, unchanged.

---

## P6-D result — wall tiling replaces the Boolean modifier

`assembly.json` gained a top-level **`wall_cells[]`** array and `assembly.ms` now builds each
`facade_wall` from **solid `Box` cells** instead of cutting it. Nothing in this section is
inferred: every row below was executed against live 3ds Max 2026.3.2 on 2026-10-05.

### What changed, and the measured reason

**The Boolean modifier cannot be made to cut anything in this build.** Every probe was batched
with a bogus-name control that came back `undefined`, so the negatives discriminate:

| Probe | Measured result |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs, `classOf` reads `BooleanMod`, but its paramblock is **Voxel Map's** — `m[1]=voxelSize`, `m[2]=toleranceFactor`, `m[3]=bevelDistance`, `m[4]=bevelDepth`. `VoxelMap()` is itself `NotCreatable`: the name is shadowed in the class registry |
| `ProBoolean()` | constructs, but `superClassOf` is **`GeometryClass`**, not Modifier, and constructing one **leaves a node in the scene** — three orphans accumulated while probing |
| native bridge `add_modifier` with `"Boolean"` | genuinely **attaches**: `node.modifiers` reads `#modifiers(Boolean:Boolean)`, `classOf` `BooleanMod`. The **operand is never set** — `snapshotAsMesh` reports `verts=8 faces=12`, unchanged, for every `params` spelling tried (`operation:1`, `object:NAME`, `object:"NAME"`, `boolobject:NAME`, and combinations) |
| the committed modifier's own properties | `isProperty m #operation` → `false`, `#object` → `false`, `#boolobject` → `false`. The control `#totalBogusProp` is also `false`, so these names genuinely do not exist |
| `getModifier 1 node` | **throws**. `node.modifiers[1]` works and returns the modifier; `node.modifiers` prints `#modifiers(Boolean:Boolean)` |

So the previous `assembly.ms` opened with `Boolean()` and therefore **did nothing** — and its
own `G-80` census still reported success. That combination is the finding: a modifier that
*attaches and does nothing* is worse than one that throws, because it defeats a count-based
check.

### The old census could not observe failure

The old emitted census tallied **iterations of its own loop**:

```maxscript
local committed = 0
for cut_pair in cut_pairs do ( ... addModifier pair_host pair_mod; committed = committed + 1 )
committed
...
if cut_count != 16 do ( throw "G-80: ..." )
```

The live run read `cut_count = 16` and passed while `objects.count` was correct at **208** and
the modifier stacks were **all empty** (`nodes carrying modifiers=0`, `max stack=0`). **A counter
cannot detect a failed attach.** The new census **walks the scene**, and that walk is itself a
required needle rather than an implementation detail:

```maxscript
local found_cells = 0
for scene_node in objects do
(
    if (substring scene_node.name 1 4) == "WAL_" do found_cells = found_cells + 1
)
if found_cells != 52 do ( throw "G-80: found " + ... )
```

### The replacement, and the two new invariants

`wall_cells[]` — one entry per emitted solid: `id`, `node_name`, `host_ref`, `plan_rect_cm`,
`z_range_cm`, `volume_cm3`. `id` is `WAL-<HOST>-C<NN>`; `node_name` is that id with dashes
replaced (`WAL-EL-014-C01` / `WAL_EL_014_C01`), which is what `G-74` already demanded of every
name in the file. The tiling is a **column-row decomposition along the run axis** — cut at every
opening's `u` boundary, then inside each column at the `v` boundaries of the openings covering
it — so a column is wholly inside one opening's `u` span or wholly outside it, and the
decomposition is exact with no gap and no overlap. The cross axis always takes the wall's own
extent, and order is deterministic: ascending run interval, then ascending `v`. `pavilion-01`
carries **52 cells over 8 hosts** (`EL-014` 11, `EL-015` 12, `EL-016` 6, `EL-017` 7,
`EL-018` / `EL-019` / `EL-020` / `EL-021` 4 each).

| Id | Title | What it asserts |
|---|---|---|
| **`G-82`** | **The volume identity** | For every host, the cells' summed volume equals the host's volume **minus its openings' volume**, within `linear_cm²`. This is the rule the Boolean route could never have satisfied: a modifier that removes nothing leaves the volume untouched, so a "successful" build reads as a wall with every opening still filled |
| **`G-83`** | **Full thickness** | Every cell spans its wall's **full** thickness in the wall's thin axis. A tiling of solid cells cannot express a partial-depth opening, so a cell that stops short is a defect, not a style choice |

Both are enforced in **two** places, as the P5 device requires:
`scripts/validate_specs.py` (`_g82_wall_tiling_volume`, `_g83_wall_cell_thickness`) and
`scripts/place_components.py` (`_check_wall_tiling`).

**`G-81` changed shape.** It was a two-ceiling rule (≤ 5 modifiers per call, ≤ 10 per node,
cutters chunked into passes). It is now the **strong form**: the stage emits **zero** modifiers,
`addModifier` must not appear at all, and the emitted script additionally asserts that the hosts
arrive with **empty** stacks. The ladder result still stands as the reason the ceiling is zero
rather than small — 5 and 10 rungs clean, **20 froze Max until the machine rebooted**.

### The live gate — measured

| Check | Result |
|---|---|
| `fileIn examples/massing.ms` | **27** nodes = 22 `Box` + 5 `Dummy`; idempotent over 3 runs |
| 9 bboxes vs an independent Python prediction (8 walls + ground pad) | worst deviation **0.000000 cm** |
| `fileIn examples/assembly.ms` | **244** nodes = 27 + 136 `PLC_` + 29 `PROTO_` + 52 `WAL_`; no throw; idempotent over 3 runs |
| 52/52 cell bboxes measured in Max vs the spec | worst deviation **0.000000 cm** |
| volume identity per host, from **measured** bboxes vs an **independently re-derived** prediction | error **0.000000 cm³** on all 8 hosts; total wall **73 800 000 cm³** |
| instances sharing their prototype's `baseObject` | **5/5** |
| **negative control** — a plain `copy`, renamed `CTRL_PLAIN_COPY` so it does not match the `PROTO_` scan | shares → `false` |
| `objects.count` after two delete sweeps | **0** |

The massing nodes stay in the scene, so the count is additive: **244 = 27 massing + 136 + 29 +
52**. The wall cells are *additional* nodes alongside the host walls, not a replacement for them.

### Fault injection — and the gap it found

**11 of 11** cases fired in the builder and **3 of 3** in the linter, baseline clean.

**`G-74` had to be widened, and the reason is a pattern, not a one-off.** It did not cover
`wall_cells[]` when the tiling landed, so **two injected defects passed the self-check clean**: a
duplicated `node_name`, and a `node_name` not derived from its id. `_g74_node_names` now iterates
`("placements", "opening_cuts", "wall_cells", "scatter")` and also checks the derivation.
**This is the third time in this repo that a rule has failed to fire because the thing it governs
was added later.** A rule has to be re-checked against the file as it now stands, not against the
shape it was written for.

### Two harness lessons — both produced a wrong answer first

1. **The first fault-injection harness proved nothing.** It mutated `examples/assembly.json` and
   re-ran the builder, and reported **0 of 8 fired**. But `assembly.json` is the builder's
   **output**, so every mutation was overwritten before any rule saw it. The rules are exercised
   by calling the predicates directly with a mutated **document**. Do not repeat the first harness.
2. **The first live-gate harness printed a false PASS.** `VERDICT: PASS` was reported while
   **zero** comparisons had been made, because the prediction keys used dashes and the node names
   use underscores — every lookup missed, nothing failed, and "no failures recorded" was read as
   success. **A verdict must require that the expected number of comparisons actually happened**,
   not merely that no failure was recorded.

### Two collateral facts, recorded because they will recur

- **`ProBoolean()` creates a scene node.** Probing it polluted the scene (three orphans). Delete
  test nodes in the same call that created them, and note that some "modifiers" are really objects.
- **`assembly.json`'s key order is `placements`, `opening_cuts`, `wall_cells`, `scatter`**, and
  `07` §4 now declares it in that order.
