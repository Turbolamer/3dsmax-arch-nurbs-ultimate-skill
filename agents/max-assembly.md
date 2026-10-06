# max-assembly — S5: locked `assembly.json` → `assembly.ms` → placed instances, tiled walls, wired Chaos Scatter

> **Purpose:** S5 is the stage that stops writing numbers and starts **moving geometry**. It reads the
> last derived file in the chain — `assembly.json` (`07` §8.5) — resolves it against
> `components_registry.json`, `world_table.csv` and `massing.json`, emits `assembly.ms`, runs it in
> 3ds Max, **counts and measures what came back**, and tears the whole assembly down again. **S5 builds
> the assembly only, and S5 is the last stage of the pipeline.**
>
> **CORRECTED (2026-10-06):** the paragraph this replaces read "Materials and renderer choice are S6
> (`materials.json`); QA, captures and the scatter determinism proof are S7; export is S8." **S6, S7 and
> S8 were cancelled by explicit user decision on 2026-10-05** — not deferred. `materials.json`,
> `qa.json` and `export.json` are **reserved stubs that no stage reads or writes**, and
> `agents/max-materials.md`, `agents/max-qa.md` and `agents/max-export.md` **do not exist and are not
> planned**. **Materials are applied by hand by the user**; the deliverable is the model plus the
> hand-off at `agents/max-orchestrator.md` §5. This row of §1.1 below agrees; it is §1's own purpose
> paragraph that had drifted, and this notice is the correction.
>
> **S5 inherits four measured P5 findings and three measured P6 findings, and every one of them is a
> rule in this file, not a preference:** the instance route is `copy` + `baseObject` assignment
> (`setCopyMode` is absent), a Z rotation is `quat <deg> [0,0,1]` (`rotationZ` / `rotationX` /
> `rotationY` / `matrix3` / `angle` are absent), `node.pos` on a `Box` puts the **base** at `pos.z`,
> `for o in objects do delete o` silently skips entries, **layer assignment is impossible from
> this bridge** — nine routes ruled out, final, not an open question — and **the Boolean modifier
> cannot cut anything in this build**: `Boolean()` throws, `BooleanMod()` carries Voxel Map's
> paramblock, and the bridge's own `add_modifier` attaches a Boolean whose operand is never set
> (`07` §8.5.8.1, measured 2026-10-05). **So this stage emits zero modifiers and builds each
> `facade_wall` out of solid cells** (`wall_cells[]`), which is also why the stack hazard below has a
> ceiling of **zero** rather than a number.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage · Input | **S5** (`PLAN.md` §4 row P6, `01` §3 "S5") · `specs/pipeline/assembly.json` (`placements[]`, `opening_cuts[]`, `wall_cells[]`, `scatter[]`), resolved against `components_registry.json`, `world_table.csv` and `massing.json` (which carries the `facade_wall` hosts the cells tile), plus `assumptions.json` / `conflicts_resolved.json` |
| Output | `assembly.json` (`07` §8.5) and the builder's `assembly.ms`, then the nodes that script creates |
| Geometry produced | One prototype per distinct `component_id` · one **reference instance** per `placements[]` row · one solid `Box` cell per `wall_cells[]` row, which together are the pierced walls. **Zero modifiers. No cutters, no cut passes.** `scatter[]` is **declared, not built** — no `ChaosScatter` node is emitted; the user applies it (§6.6). **No materials, no cameras, no lights, no export** (contract §3.5) |
| 3ds Max calls | Exactly one stage of them, and they are **the orchestrator's**: the §7 live gate. **No probes** (§1.2) |
| Consumer · Precondition | **the hand-off** (`agents/max-orchestrator.md` §5) — materials are made by hand · S1, S2, S4a and S4b complete and locked. **S6/S7/S8 were cancelled 2026-10-05** |
| Blocked by | An `assembly.json` that is not `locked`. Full stop (§2.2) |
| Findings | See `agents/max-orchestrator.md` §6.2. If this session produced a real finding — a measured value outside `tolerances.linear_cm`, a placement or host the tables cannot express, or a registry component that is legal but wrong on this building — record it in `<project>/IMPROVEMENTS.md`. **A session with no findings writes nothing and creates no file.** Format: `references/improvement-log.md` |

### 1.1 What S5 owns, and what S5 defers

S5 owns exactly four tables and the geometry they generate: `placements[]`, `opening_cuts[]`,
`wall_cells[]` and `scatter[]`. Everything else in the assembly vocabulary belongs to another stage.

| **Never** built by S5 | Consumed by | Correct instrument |
|---|---|---|
| Materials, Corona / OpenPBR parameters, UV rules | **nobody — S6 was cancelled 2026-10-05** | **Applied by hand by the user.** The hand-off is `agents/max-orchestrator.md` §5. `material_role` in a spec is a **role**, never a material class (`07` §8.3.6) |
| Cameras, lights, render settings, captures, the determinism *report* | **nobody — S6/S7/S8 were cancelled 2026-10-05** | Materials are made **by hand**; the hand-off is `agents/max-orchestrator.md` §5. Applying and reading back the scatter is the **user's** action, via `snippets/chaos_scatter.ms` |
| File export, glTF, FBX, USD | **nobody — S8 was cancelled 2026-10-05** | **Nothing.** The user saves and exports from Max |
| Curved or NURBS hosts, swept reveals, mitred corners | **nobody at S5** | Only an axis-aligned `facade_wall` prism can be tiled into cells (§6.2). A NURBS host is a **`07` §12 step 1 change**, escalated (§10.1) |
| Reveal depths, glazing build-ups, sill nosings | **nobody — S6/S7 were cancelled 2026-10-05** | A component's `variants` / `parameters` (`07` §8.4.3) still carry the **data**, but no stage reads them into geometry |
| Layer **application** to any node | **nobody — permanently** | Layer is **data** and cannot be applied from this bridge at all (§6.3, `G-79`) |
| Physics-based particle simulation | **nobody — the plugin is absent** | Chaos Scatter for static distribution; PhysX / Max particles for motion; instance copies for RailClone-style patterning (`references/14-chaos-scatter.md` §4) |

### 1.2 The one-MCP rule

**You may not touch the bridge.** S5 is arithmetic plus one emitted script; the §7 gate belongs to the
orchestrator, exactly as in S2 and S4a.

| Allowed | Forbidden |
|---|---|
| `3dsmax-mcp_get_scene_snapshot` / `_get_scene_info` to confirm the scene is empty **before** the gate | **Any exploratory probe.** A fact not in `CHECKPOINT.md` §"Verified facts" is escalated for an orchestrator probe, never opened by S5 |
| **No modifier at all.** `assembly.ms` must contain zero occurrences of `addModifier` (`G-81`), so the attachable set in §6.4 is a routing fact for other stages, not a permission for this one | `Extrude`, `Bevel`, `Sweep`, `Lathe`, `Surface`, `CrossSection`, `Bevel_Profile` on `addModifier` — they **construct** and then **throw** (`mods=0`). `Bevel_Profile` is unusable through every route. **`Boolean` is worse: it attaches and does nothing** (§6.2, AP-22) |
| `3dsmax-mcp_delete_objects` on gate nodes, in the same call that created them | **The absent-plugin group** — `3dsmax-mcp_scatter_forest_pack`, all 14 `3dsmax-mcp_tyflow_*` tools, `3dsmax-mcp_get_railclone_style_graph` (`PLAN.md` §4, `CHECKPOINT.md`). forestPack, forestLite, tyFlow, railClone and phoenixFD are **not installed** |
| `3dsmax-mcp_manage_layers` actions `list` and `create` — the eight names in `07` §8.1.4, nothing else | **`3dsmax-mcp_manage_layers` object assignment, and `3dsmax-mcp_set_object_property` with `property=layer`.** Both are the read-only `layer` property. §6.3, `G-79` |
| `3dsmax-mcp_capture_viewport` for a human-facing record, **after** measuring | `3dsmax-mcp_introspect_class` / `_introspect_instance` / `_inspect_plugin_class` as **proof** — they lie (`AGENTS.md` §"The one rule that matters most") |
| `3dsmax-mcp_clone_objects` (`mode: "instance"`) as a second, independent instance measurement | The **Rhino** server names — `get_objects`, `analyze_objects`, `measure_objects`, `boolean_*`, `loft`, `sweep1`, `pipe`, `extrude_curve`, `section_profile`, `capture_viewport`, every `gh_*`. Never call them against Max, and never conclude the bridge is down because one errored |
| `3dsmax-mcp_get_instances` to corroborate the `baseObject` discriminator | `mcg_*` and `3dsmax-mcp_curve_model` — **they do not exist in this bridge at all.** Record the absence; never emulate Max Creation Graph by hand |

> Executing the §7 gate on an already-emitted `assembly.ms` is **not** a probe (`01` §6). Executing a
> probe *you wrote to find out whether something works* is a probe, and it is forbidden here.

---

## 2. Inputs and outputs

### 2.1 What you read

| Source | What you take from it |
|---|---|
| `specs/pipeline/assembly.json` | **The contract you build from** — `placements[]` (`id` `component_id` `source_row` `node_name` `position_cm` `rot_z_deg` `instance` `layer`) · `opening_cuts[]` (`id` `opening_id` `node_name` `host_ref` `facade` `level_index` `bay_index` `u_range_cm` `v_range_cm` `depth_cm` `kind` — the **declaration** the wall is pierced around) · `wall_cells[]` (`id` `node_name` `host_ref` `plan_rect_cm` `z_range_cm` `volume_cm3` — **the solids actually emitted**, `07` §8.5.8) · `scatter[]` (§6.6) · `layer_map` · `defaults` (`panel_joint_cm`, `instance_limit_guard`) · `tolerances` (inherited **verbatim** from `dimensions.json`, `G-33`) |
| `specs/pipeline/components_registry.json` | `components[].id`, `name`, `width_cm`, `height_cm`, `thickness_cm` — the **only** source of a prototype's dimensions. A `placement` never carries its own size |
| `specs/pipeline/world_table.csv` | The P5 table. `source_row` in `assembly.json` indexes its **1-based data rows**, header excluded. S5 reads it to **assert** (`G-72`, `G-73`), never to recompute a position |
| `specs/pipeline/massing.json` | `elements[]` of kind **`facade_wall`** — the only hosts a cell may belong to, and the source of every host's `profile_cm` / `z_range_cm`. `column` / `roof_deck` elements are the scatter `model_refs` and `target_ref`. Plus every `node_name` S5 must not collide with |
| `references/_p6-contract.md` | **The authority for this stage** — §1.1 the layer negative · §1.2 the measured stack hazard · §2 the `facade_wall` decision · **§3 the `assembly.json` schema** · §4 `G-71`…`G-81` · §5 the builder obligations · §7 the live gate, and the appended **§"P6-D result"** for the tiling that replaced cutting. Where an implementation wants a different key name, id pattern or formula, **this file wins** |
| `references/07-spec-grammar.md` | **§8.5** the schema in full — §8.5.8 is `wall_cells[]` · §9.9 `G-71`…`G-83` · §3.1 the lock gate · §2 units · **§11 + §12 the no-class-names rule** · §9.6 the SKIP discipline |
| `references/11-layer-standard.md` | §1 the eight layer names · §3.1 naming, **N1** (no `-` in a name) · §6 checklist H1–H12 |
| `references/14-chaos-scatter.md` | The verified parameter map · the §1.2 hazard · the absent-tool substitutions · `FpInterface` as the **hand-application** read-back (§6.6). **Not** a stage gate — S7 was cancelled 2026-10-05 |
| `snippets/chaos_scatter.ms` | The apply / re-apply / census / snapshot library. **`fileIn`-able, creates nothing on load** |
| `CHECKPOINT.md` | §"Design consequences of the layer finding (P3 decision, closed at P6)" · §"RESOLVED at P6 by deliberate bounded ladder" · §"Chaos Scatter" · §"Scene units and placement semantics — VERIFIED (P3)". **The transcript of record for §7** |

> **`rot_z_deg` is the CSV's number, verbatim.** P5 proved it equals `run_angle_deg = atan2(dy, dx)` and
> **not** `dimensions.facades[].direction_deg` — two of the example's four facades are wrong by 180° if
> the facing label is used. `G-73` says the builder **copies the table and never recomputes placement
> geometry**. A placement's `position_cm` is likewise copied byte-for-byte out of the row.

### 2.2 What you own, and the lock gate

| Path | Action |
|---|---|
| `<project>/specs/pipeline/assembly.json` | **Emitted by the builder.** Never hand-written, never hand-edited |
| `<project>/specs/pipeline/assembly.ms` | **Emitted by the builder.** Never hand-written, never hand-patched |

**You modify nothing else** — not `references/07`, not `references/14-chaos-scatter.md`, not
`snippets/chaos_scatter.ms`, not `scripts/`, not `examples/`, not `agents/max-facade.md`, not
`agents/max-massing.md`, not `CHECKPOINT.md`, not S1/S2/S4's locked files.

> **A builder must refuse any spec file whose `status` is not `locked`, naming the file and the status
> it found** (`07` §3.1). Exit non-zero, before anything else is read.

| Found | Action |
|---|---|
| `status: "draft"` or `"superseded"` on `assembly.json` or any of its three upstream files | **Refuse**, and report that path and status verbatim. `--allow-draft` is an inspection flag for linting work in progress, never for a deliverable. `--build` **enforces** the gate (the P2/P3 convention) |
| a `draft` upstream `world_table.csv`-derived file, or a `project` id that differs across the four files | **Refuse.** They are one locked set and `G-31` requires the id identical |
| an existing `assembly.json` in `--in` whose bytes differ from what the builder computes | **Refuse, naming the first differing key path.** A hand edit the next rebuild would silently destroy is the failure mode `--from examples` exists to prevent |
| `schema_version` major you do not implement | **Stop.** Do not guess |
| an `A-nnn` in `assumptions.json` with `recheck_stage: "P6"` | Build it **and name every one in your report**. You are the recheck stage |

A `draft` upstream file is not your failure to fix, and not a reason to build "just the ready parts".
**Do not emit a partial `assembly.json` and call it done** — a file with a hole in it passes a casual
read and is not a deliverable. **CORRECTED (2026-10-06):** this sentence used to read "…and fails S6";
**S6 was cancelled on 2026-10-05** and no stage reads the file afterwards. The failure it describes is
real and worse now, not milder: a partial `assembly.json` reaches the **user's** hands as the finished
model.

---

## 3. File ownership

| Artifact | The contract you may rely on |
|---|---|
| `scripts/place_components.py` | Exposes `--in <dir> --out <dir> [--stage assembly] [--json] [--build] [--allow-draft]`; reads `assembly.json` + `components_registry.json` + `world_table.csv` + `massing.json`; writes `assembly.json` and `assembly.ms`; refuses non-`locked` input with a non-zero exit; self-checks `G-71`…`G-83` **on the emitted documents before writing**; byte-identical output for byte-identical input; **emits no layer statement** (`G-79`) and **no modifier statement at all** (`G-81`) |
| `examples/assembly.json` · `examples/assembly.ms` | The `pavilion-01` worked case, orchestrator-committed from the builder's output. **Not yours to edit.** They are the artefact you verify |
| `examples/assumptions.json` | Carries `A-025` (`facade_wall_thickness_cm`, 20 cm) plus P5's `A-023` / `A-024`. Owned by the orchestrator; you verify them and never write them |
| `07` §8.5 / §9.9 · `11` §1–§6 | Another author's tables. Cite by id; **do not edit** |

**A `G-` id you cannot evaluate is a SKIP with its reason, never a silent PASS** (`07` §9.6). At P6
that includes `G-80` — it observes the **built scene**, which a static file cannot see, so it is asserted
by the emitted census and by §7 instead. `G-82` / `G-83` need no scene: they are arithmetic over
`wall_cells[]`, `opening_cuts[]` and the hosts in `massing.json`, and they are enforced in **two**
places — `scripts/validate_specs.py` and `scripts/place_components.py` — so they cannot both be
wrong in the same direction.

---

## 4. Procedure

Ordered and deterministic. Each step has a pass condition.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Verify the inputs are locked** | Read the envelope keys of `assembly.json`, `components_registry.json`, `massing.json` and the CSV header of `world_table.csv`. Apply §2.2 in full | All `locked`, `project` agrees across all four, `units.length == "cm"`, `units.angle == "deg"` |
| 2 | **Re-check every P6 assumption** | List every `assumptions.json` entry with `recheck_stage: "P6"`. At the worked example that is exactly **`A-025`** — the modelled facade-wall thickness, a *reference-only* proxy: the band is a massing proxy, a real build-up is a curtain-wall system schedule | Every one named in your report. **None silently upgraded.** If `A-025` would change a wall's thickness, escalate (§10.1) — it now sets every cell's thin-axis extent |
| 3 | **Read the four inputs into the assembly model** | Read §2.1 once, in order. Take `tolerances` **verbatim** — a builder may not widen them. Index `world_table.csv` by its 1-based data row. Bind every `component_id` and every `massing.json` element id to a prototype / host **once** | Every `placements[].component_id` resolves (**G-71**); `len(placements) ==` CSV data rows, in **both** directions (**G-72**); every `source_row` is a real row, every real row appears exactly once, no duplicate |
| 4 | **Verify each placement against its own row** | Compare `position_cm` and `rot_z_deg` to the CSV row it names | Within `linear_cm` / `angle_deg`. **The builder copies the table; it never recomputes a position or an angle** (**G-73**). A disagreement is a FAIL on the spec, not something to "fix" by recomputing |
| 5 | **Create the prototypes** | One `Box` per distinct `component_id`, sized `width_cm × height_cm × thickness_cm` from `components_registry.json`, **at `pos [0,0,0]` — measured 2026-10-05, all 29 prototypes sit on the world origin and none is parked at a scratch offset**. Name it after the component's `name`, hyphen-free (**N1**) | `prototypes == count(distinct component_id)`. Prototype and placement names are **disjoint** — a prototype named like a placement makes `G-72`'s count ambiguous |
| 6 | **Place the instances** | For each row: `n = copy proto`, then `n.baseObject = proto.baseObject`, then `n.position = [x,y,z]`, then `n.rotation = quat rot_z_deg [0,0,1]`. **`setCopyMode` does not exist**; the assignment is what makes it a *reference* instance. **≤ 5 placements per `3dsmax-mcp_execute_maxscript` call** is not needed — the placement bound is **call length** (one script per call, under ~2 s), not a modifier stack | Every node named `placements[].node_name`. Every instance's `baseObject ==` its prototype's, and a **deliberate plain `copy` in the same batch reports `false`** — a uniform `true` is a **broken probe**, not a pass |
| 7 | **Compute the wall cells from the host, not from the opening's centre** | For each host `facade_wall`, take its own `profile_cm` extent and decompose it into solid cells around that host's openings: cut at every opening's `u` boundary to get **columns**, then inside each column cut at the `v` boundaries of the openings covering it to get **rows**. Emit `wall_cells[]` in **ascending run interval, then ascending `v`**. The spec keeps `u` facade-local because that is the frame P5's whole grid is written in; the world position along the run is `start_corner_cm + u`, converted once, here | Every opening's `u_range_cm` lies inside the host wall's own run extent and its `v_range_cm` inside the host's own local `[0, level.height_cm]`, within `linear_cm` (**G-76**). Every `dimensions.json` opening has **exactly one** cut and every cut exactly one opening — orphans fail in **both** directions (**G-77**). Per host, `Σ cell volume ==` wall volume − openings volume within `linear_cm²`, and every cell spans the wall's full thickness (**`G-82`**, **`G-83`**) |
| 8 | **Emit the cells as ordinary solids — no modifiers, no cutters** | One `Box` per `wall_cells[]` row, positioned from its own `plan_rect_cm` / `z_range_cm`. **There is nothing to commit and nothing to chunk**: `assembly.ms` contains **zero** `addModifier` calls and creates no cutter node (`G-81`). Every opening is therefore passed clean through, which is the invariant `G-83` states rather than assumes | `addModifier` count in the emitted source **0**, grepped. The emitted script asserts the hosts arrive with **empty** stacks and throws if any host carries a modifier. Every cell node is named `wall_cells[].node_name` — the id with dashes replaced, which is `G-74`'s derivation rule again |
| 9 | **Validate the scatter declaration — do NOT build the scatter** | `scatter[]` is a **declaration**, not geometry. `place_components.py` emits **no** `ChaosScatter` node: `assembly.ms` contains zero occurrences of `ChaosScatter`, `scatter` or `SCT_001` in its 1979 lines **[measured 2026-10-06]**. **Decided 2026-10-06: the user applies the scatter by hand**, from `snippets/chaos_scatter.ms`. Validate instead: `seed` is the spec's integer, not a run-time value, and in 1…31337 (**G-78**) · `target_ref` and every `model_ref` resolve to a `massing.json` element id or a `components_registry.json` id, and nothing else · `instance_count_limit > 0` · `scale_from ≤ scale_to`, `rotation_from_deg ≤ rotation_to_deg` | The declarations are consistent and resolvable. **`getInstanceCount()` is NOT read at this stage — there is nothing to read it from.** The apply route, with its `FpInterface` census, is in `snippets/chaos_scatter.ms` and §6.6, and the user runs it after the model is delivered. **Applying it changes the node count: report 254 before, and the measured count after** |
| 10 | **Emit the census into the script, not beside it** | The emitted `.ms` **walks the scene** — `for scene_node in objects` — and counts what it finds: placed instances, prototypes and the `WAL_`-prefixed cell nodes, then **throws on any mismatch** against the tables (`G-80`). This is the same device as `G-34`…`G-40` and `G-54`, and it is the reason P5's sliver defect could not ship. **It must observe the scene, not its own bookkeeping:** the previous census counted its own loop iterations and reported `cut_count = 16` while the scene held **zero** modifiers | Re-running the emitted script is **idempotent**: same node-name set, no duplicates (§5, the P3 `fn`-wrap rule). The scene walk is itself asserted as a required needle, because a counter that cannot see the scene cannot detect a failed attach |
| 11 | **Emit, then verify by recomputation** | Run the builder (§5). **You do not hand-write either file.** Read `assembly.json` back from disk and verify **independently**: recompute one host's total cell volume from `massing.json`'s `profile_cm` / `z_range_cm` minus its openings, one placement's expected bbox from the CSV row + the registry dimensions, and the `G-74` name partition across all **four** tables by hand | Your hand computation matches the file at `tolerances.linear_cm`, and the id set matches what you derived. **Do not verify the builder by reading its own output back and nodding at it** |
| 12 | **Validate** | `python scripts/validate_specs.py --dir <specs_dir> --build`, then again with `--warnings-as-errors` | Exit **0** and `FAIL 0` in **both** modes. `G-71`…`G-78`, `G-82`, `G-83` PASS, or SKIP **with its stated reason** (§8 row 2) |
| 13 | **Hand the script to the live gate, clean up, report** | §7 then §9 then §12. **An emitted `.ms` is not done until `fileIn` has run it and its output has been measured** | Every measured number recorded; `objects.count == 0` at the end; the report is under the §12 cap |

**Determinism.** The same locked inputs must yield byte-identical `assembly.json` and `assembly.ms`
(`07` S-5, `01` §5). Four things break it, and all four are defects to report rather than fix in the
output: a timestamp other than `source.recorded_at`, a **run-time seed** instead of the spec's, a
run-time default, and iteration-order dependence (dict or set order leaking into an id or a row order).
Placement, cut and **cell** ids ascend in fixed order, and the cell order is **ascending run interval
then ascending `v`**, so a rebuild yields the same node names (**N3**).

---

## 5. The build commands

```
python scripts/place_components.py --in <specs_dir> --out <out_dir> --stage assembly
python scripts/place_components.py --in <specs_dir> --out <out_dir> [--json] [--build] [--allow-draft]
python scripts/validate_specs.py --dir <specs_dir> --build [--warnings-as-errors]
```

Read the builder's `--help`; never guess a flag. `01` §8 fixes the shape and forbids a second entry point.

| Aspect | Contract |
|---|---|
| Reads | `<in>/assembly.json` · `<in>/components_registry.json` · `<in>/world_table.csv` · `<in>/massing.json` |
| Writes | `<out>/assembly.json`, `<out>/assembly.ms`. `--out` defaults to `--in`; `--json` gives a machine-readable report |
| Exit **0** | The lock gate passed **and** the `G-71`…`G-83` self-check produced no failure |
| Exit **non-zero** | A refusal naming the reason — the file path and the `status` found, the first differing key path, or the `G-` ids that fired |
| Determinism | Byte-identical output for byte-identical input |
| MAXScript shape | One `fn mcpAssemblyBuild_<project>` and **one call** — re-running replaces, never duplicates (the P3 rule). **No `local` at top level.** The explicit-local delete form only: `local prev = getNodeByName "X"` then `if prev != undefined do ( delete prev )` — the context-dependent one-liner throws when the node is absent |
| Instance route | `n = copy proto` then `n.baseObject = proto.baseObject`. `setCopyMode` **does not exist** |
| Rotation | `n.rotation = quat <degrees> [0,0,1]`. `rotationZ` / `rotationX` / `rotationY` / `matrix3` / `angle` **do not exist** |
| **`node.pos` on a `Box`** | The **base** sits at `pos.z`; geometry centres on `pos.xy`. It stays true after `copy`, after `baseObject =` and after rotation. To centre a prototype, write `pos.z = cz − height/2` |
| **Modifier statements** | **None.** `addModifier` count in `assembly.ms` must be **0** (`G-81`), and the emitted script asserts the hosts arrive with empty stacks. Walls are cells, not cuts (§6.2) |
| Layer code | **None.** `assembly.ms` must contain no `node.layer`, no `LayerManager` setter and no layer-assignment helper (`G-79`). A builder that tries is a build **FAIL**, not a silent no-op |

**A non-zero exit is a stop**: fix the input through S1/S4b (§10.1) or the builder through its owner
(§3). Never rename a key, widen `tolerances`, drop a leaf, re-sort `source_row`, or delete a placement
to silence a `FAIL`.

---

## 6. The assembly rules

### 6.1 A placement is a **copy plus a shared base object**, not a "copy mode"

The verified instance route is two statements:

```maxscript
local n = copy proto            -- a copy: its own base object
n.baseObject = proto.baseObject -- now it REFERENCES proto's geometry
n.position  = [x_cm, y_cm, z_cm]
n.rotation  = quat rot_z_deg [0,0,1]
```

An instance **shares its prototype's `baseObject`**; a plain copy does not. **That is the whole
discriminator, and the gate must prove it discriminates** — a deliberate plain `copy` in the same batch
has to report `false`. A uniform `true` across both is a **broken probe**, not a pass
(`AGENTS.md` §"The one rule that matters most"). `setCopyMode` does not exist in this build; every
recipe that calls it is wrong.

### 6.2 Only a `facade_wall` prism can be tiled, and `u` is facade-local

| Field | Rule |
|---|---|
| `host_ref` | A `facade_wall` element id in `massing.json`. **Never `null`** — S4a emitted `null` for all 136 panels because no exterior envelope existed; the `facade_wall` kind (contract §2) is what gives S5 something to build a wall from. **Never invent a host** |
| `u_range_cm` | `[position_cm − width_cm/2, position_cm + width_cm/2]` in the opening's own frame. The **world** position along the run is `start_corner_cm + u`, because the host wall's profile starts at `start_corner_cm`. The spec keeps `u` facade-local; the builder converts once, when it writes the cells |
| `v_range_cm` | `[sill_cm, head_cm]` verbatim, level-local |
| `depth_cm` | **Traceability only.** Retained so the declared opening's depth stays auditable against `facade_wall_thickness_cm`. It is **not** consumed as geometry: nothing is cut to a depth, because nothing is cut. A tiling cannot express a partial-depth opening, so every cell carries the wall's **full** thickness (`G-83`) |
| `kind` | `difference`, the only legal value (contract §3.3, §3.5) |

The worked example has **8 `facade_wall` elements** (4 facades × 2 levels) and **16 openings**, tiled
into **52 cells**. "Inward" is already decided in `massing.json` — S5 does not re-decide it and must
not widen a band outward.

#### 6.2.1 Why there is no cut path here

**The Boolean modifier cannot be made to cut anything in this build.** Measured 2026-10-05 against
live 3ds Max 2026.3.2, every probe batched with a bogus-name control that came back `undefined`
(`07` §8.5.8.1 carries the table):

| Probe | Measured |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs, `classOf` reads `BooleanMod`, but its paramblock is **Voxel Map's** (`voxelSize`, `toleranceFactor`, `bevelDistance`, `bevelDepth`); `VoxelMap()` is itself `NotCreatable` |
| `ProBoolean()` | constructs, `superClassOf` is `GeometryClass` not Modifier, and constructing one **leaves a node in the scene** |
| bridge `add_modifier` with `"Boolean"` | **attaches** — `node.modifiers` reads `#modifiers(Boolean:Boolean)` — and the **operand is never set**: `snapshotAsMesh` reports `verts=8 faces=12`, unchanged, for every `params` spelling tried |
| `isProperty m #operation` / `#object` / `#boolobject` | all **`false`**, and the bogus control is also `false`, so those names genuinely do not exist |
| `getModifier 1 node` | **throws**; `node.modifiers[1]` works |

The consequence is worse than a throw. The previous `assembly.ms` opened with `Boolean()` and
**silently did nothing**, and its own `G-80` census still reported success — because that census
counted iterations of its own loop and read `cut_count = 16` against a scene with **zero**
modifiers anywhere. **A modifier that attaches and does nothing is worse than one that throws**, so
S5 emits no modifier at all and expresses an opening as *absent material*: solid cells that tile
wall-minus-openings exactly (`G-82`).

### 6.3 Layer is **data, permanently** — and there is no layer code in this stage

**There is no way to assign an object to a layer from this bridge. Nine routes are ruled out and this
is final, not an open question** (contract §1.1, `CHECKPOINT.md` §"Design consequences of the layer
finding (P3 decision, closed at P6)"):

| Route | Result |
|---|---|
| `LayerManager.newLayerFromName` / `getLayerFromName` / `getLayer` | The class exposes **no setter of any kind** (verified with a bogus-name control in the same batch, which threw) |
| `node.layer = <string>` · `= <integer index>` · `= <LayerProperties mixin>` | All three throw `Property is read-only: layer` |
| `3dsmax-mcp_manage_layers` object assignment | The action vocabulary is **exactly `{list, create, delete}`**. 40+ candidates — including `rename`, for which the tool's own schema carries a parameter — all return a uniform `Unknown layer action: X` |
| `3dsmax-mcp_set_object_property` with `property=layer` | Emits `node.layer = <value>` and dies with the same read-only error. A **positive control** on the same tool (`property=pos`) succeeded, so the tool works and `layer` is the blocker |

**What S5 therefore does:** declares `layer_map` as **data**, linted against the closed vocabulary of
`07` §8.1.4 (**eight** names: `00_SITE`, `01_SLABS`, `02_STRUCTURE`, `03_CORE`, `04_ROOF`, `05_FACADE`,
`90_SCENE`, `99_DEBUG`), asserts every `placements[].layer` equals its role's `layer_map` entry
(**`G-75`**) — and emits **no layer statement at all** (`G-79`). Layer application is a **human action in
the Layer dialog**. `3dsmax-mcp_manage_layers` `create` is permitted for the eight names' existence
check; nothing else about layers is permitted.

### 6.4 The attachable modifier set, and what throws

**S5 attaches none of these.** The table is kept as a routing fact, because the ladder that produced
it is the reason the stage's own ceiling is zero (§6.5) — and because a reader who needs a modifier
in another stage needs the attach list.

| Verdict | Names |
|---|---|
| **Usable via `3dsmax-mcp_add_modifier`** | `Shell` `Chamfer` `Lattice` `Edit_Poly` `Uvwmap` `TurboSmooth` `Noisemodifier` `Bend` `Twist` `Taper` — the set the P6 ladder used |
| **Construct but `addModifier` throws, `mods=0`** | `Extrude` `Bevel` `Sweep` `Lathe` `Surface` `CrossSection` |
| **Unusable through every route** | `Bevel_Profile` |
| **Attaches and does nothing** | the Boolean modifier (§6.2.1) |

A throw is not a nuisance to route around: **no `mods=0` and no error is a FAIL, not a partial pass.**
The last row is the worse case of the same statement — see AP-22.

### 6.5 The modifier-stack hazard — MEASURED, and why this stage's ceiling is zero

Run deliberately on a clean empty scene at P6, 2026-10-05, one rung per call:

| rungs on one `Box` | result |
|---|---|
| 1 · 2 | `Extrude` and `Bevel` **throw** on `addModifier` (`mods=0`) — the P4b-r "6 unattachable modifiers" finding, re-confirmed. **Not a hang** |
| 5 | clean, 38 ms total |
| 10 | clean, 28 ms total |
| **20** | **`3dsmax-mcp_execute_maxscript` timed out; `3dsmax-mcp_get_scene_snapshot` then timed out; `3dsmax-mcp_get_bridge_status` then aborted. Max froze on the main thread, was killed, and the machine rebooted.** |

**Binding rules, for S5 and for the gate:**

1. **S5 attaches zero modifiers** (`G-81`). There is nothing to chunk, nothing to pass and nothing to
   collapse — the rule used to be two ceilings (≤ 5 per call, ≤ 10 per node) and both are gone
   because the openings are no longer cuts.
2. **The ladder is why the ceiling is zero rather than merely small.** Five and ten rungs were clean;
   **twenty froze Max until the machine rebooted.**
3. The exact breaking point between 10 and 20 is **not established and must never be re-measured.**
4. **A timeout does not mean the bridge is down.** A recoverable hang still burns the call: verify with
   a cheap `3dsmax-mcp_get_bridge_status` before concluding anything.
5. The P4b-r hedge is **retired**: the hang reproduces with **no Chaos Scatter object in the scene at
   all**, so the trigger is the geometry-stack change itself.
6. **A stage that does need a stack** must chunk at ≤ 5 per call, treat > 10 on a single node as
   forbidden without asking the user first, and escalate above that (§10.1). S5 is not that stage.

### 6.6 `scatter[]` — one row, and S5 does not build it

**This stage declares the scatter and does not apply it. Decided 2026-10-06.** `place_components.py`
emits no `ChaosScatter` node: `assembly.ms` contains **zero** occurrences of `ChaosScatter`, `scatter`
or `SCT_001` **[measured 2026-10-06]**, and the delivered count is **254** without it. The earlier
gate rows in this file that required reading `FpInterface.getInstanceCount()` back were written
against a scatter that was never applied, and asserting them would have been a check of nothing.

`assembly.json.scatter[]` (contract §3.4) is the **only** file in the chain carrying a scatter table,
and it names **no class**: `kind` is `scattered` in the spec's vocabulary. It is the **recipe** the
user applies, and S5's job is to make sure every reference in it resolves. Mapping, and the typos
that come with it:

| `scatter[]` key | `ChaosScatter` property | Note |
|---|---|---|
| `seed` | `seed` | **1 … 31337**, deterministic. **Data, never run-time.** A generated seed makes the scatter unreproducible and fails `G-78` |
| `target_ref` | `targetNodes` (node[]) | a `massing.json` element id |
| `model_refs` | `modelNodes` (node[]) + `modelFrequencies` (float[]) | ≥ 1; a `components_registry.json` id **or** a `massing.json` element id. One frequency per model |
| `instance_count_limit` | `instanceCountLimit` | `> 0`. Read it back with `getInstanceCount()` |
| `distribution_density_pattern` | **`distributionDesityPattern`** | 0…1. **The typo is the real MAXScript name.** The spec uses the corrected spelling; the builder emits the typo |
| `scale_from` / `scale_to` | `scaleFrom` / `scaleTo` | unitless ratios, `0 < from ≤ to` |
| `rotation_from_deg` / `rotation_to_deg` | `rotationFrom` / `rotationTo` | degrees, `from ≤ to` |
| `collision_avoid` | `collisionAvoid` (+ `collisionStrictness`, `collisionAvoidancePriority`) | defaults `true` |

`ChaosScatter()` constructs; `CScatter` is its base and is **NotCreatable** — always construct
`ChaosScatter`. `FpInterface` gives `getInstanceCount()`, `getModelCount()`, `getModelNode(i)`,
`update()`, `clear()`, `addModelNode(node)` and **`saveConfiguration(f)` / `loadConfiguration(f)`** —
that pair is the **determinism hook**, available **once the user has applied the scatter**. Full map:
`references/14-chaos-scatter.md`; the apply route is `snippets/chaos_scatter.ms`
(`MCPChaosScatter.config` → `create` → `apply` → `census`), which is **`fileIn`-safe and creates
nothing on load**.

**Hand-off wording — say both numbers.** Applying the scatter adds one `ChaosScatter` node plus its
instances. Report **254** as the delivered count and, if the user applies it, the measured count
after. Never report 254 and then silently have 300 nodes.

`layer: "99_DEBUG"` on a scatter row is a declaration that **no builder applies** (§6.3). The scatter
object sits wherever Max puts new geometry, and that is expected — **not a defect, never "fixed" in the
emitted script.**

### 6.7 Nothing else is allowed

No `materials`, no `cameras`, no `lights`, no `export`. **CORRECTED (2026-10-06):** this row used to say
"Those are S6, S7 and S8" — **all three were cancelled by user decision on 2026-10-05**, so **nobody
builds them**. A row naming any of them is a FAIL — this is how a stage boundary is enforced rather than
merely described (contract §3.5), and the boundary is now the **edge of the pipeline**. Materials are
applied by hand, downstream of delivery.

---

## 7. The 3ds Max step — the live gate

**The orchestrator performs the gate.** The same standing guard as P3, P4 and P5: **an emitted `.ms` is
not done until `fileIn` has run it and its output has been measured.** Contract §7 is the authoritative
gate list; this is its worked shape.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Count the inputs** | From Python, not from the builder's log: `N` = CSV data rows; `P` = `len(placements)`; `K` = `len(opening_cuts)`; `W` = `len(wall_cells)`; `C` = `len(scatter)`; `D` = distinct `component_id` | `N == P` exactly, and `W` is the number the wall decomposition produces. These numbers are the whole census and every later row is checked against them |
| 2 | **Run it three times** | `fileIn "<abs>/massing.ms"` once, then `fileIn "<abs>/assembly.ms"` three times, in one call each | Idempotent: `objects.count` and the node-name set identical after runs 2 and 3. **A second run that doubles the count is a FAIL**, not a harmless repeat |
| 3 | **Assert the count** | `objects.count ==` massing nodes **+** `P` **+** `D` **+** `W` — the massing geometry stays (§9 rule 5), so the cell total is added to the previous `P + D` rather than replacing it | **Exact equality, read back — not assumed.** Record the count that actually came back. For `pavilion-01` the measured figure was **244** = 27 + 136 + 29 + 52 |
| 4 | **Prove the instances are reference instances** | For a deterministic sample of placements, read `n.baseObject` and compare with `proto.baseObject`. **Control: one deliberate plain `copy` in the same batch must report `false`** | Sample reports `true`, control reports `false`, **in the same call**. A uniform `true` is a **broken probe** |
| 5 | **Measure a deterministic sample of 5 placed nodes** | `node.min` / `node.max` on five placements, compared against the **registry dimensions placed at the CSV row's position and rotation**, computed **independently in Python** from `world_table.csv` + `components_registry.json` — not read out of `assembly.json` | Every axis within `tolerances.linear_cm` (0.5 cm). A larger mismatch is a real inconsistency: **report both figures and stop**; never nudge a node or widen a tolerance |
| 6 | **Measure the wall cells** | **Every** cell's `node.min` / `node.max` against its own `plan_rect_cm` / `z_range_cm`, and per host, `Σ` cell volume against `wall − Σ openings`. Then read `host.modifiers.count` for all 8 hosts | Worst bbox deviation **0**; worst volume deviation **0 cm³**; and every host's stack **0**. A host carrying a modifier means something re-introduced a cut (§6.5, AP-22) |
| 7 | **Verify the zero-modifier bound held** | Grep the emitted source for `addModifier`, and read `modifiers.count` on every host the script touched | Count **0** in the source and **0** on every host (`G-81`). A non-zero count is a build FAIL, not a note |
| 8 | **Confirm there is no scatter in the scene** | Walk the scene for any `ChaosScatter` node. **The expected result is none** — this stage declares the scatter and does not apply it (step 9, §6.6) | **`objects` contains zero `ChaosScatter` nodes, and `objects.count == 244`.** A scatter present here means the scene is not the delivered model. `FpInterface.getInstanceCount()` / `getModelCount()` / `saveConfiguration` / `loadConfiguration` are **NOT** part of this gate — they are reachable only after the user applies the scatter, and asserting them here would test something the stage deliberately does not build. **This is the eighth instance of the repo's pattern: a gate that checks its own loop.** The previous census counted its own iterations and read `cut_count = 16` against a scene with zero modifiers |
| 9 | **Delete everything and prove it** | §9, then assert `objects.count == 0` | **Zero.** Not "the gate objects are gone" — zero |
| 10 | **Record every measured number** | `N`, `P`, `K`, `W`, `C`, `D`, the count assertion, the discriminator + its control, the worst bbox deviation over the 5 measured nodes, the worst cell-bbox and per-host-volume deviations, the modifier count, the scatter counts | Written down. **If any of it cannot be executed, say so — an unmeasured assembly is an unverified assembly**, and the gate is `NOT RUN`, not `pass` |

**Never assemble in one call.** `3dsmax-mcp_execute_maxscript` runs on Max's **main thread**, one script per call,
under ~2 s; a long script freezes the UI. Place in batches and delete each batch in the call that
created it (§9). And a *recoverable* hang still burns the tool call: **`Extrude` / `Bevel` on
`addModifier` return promptly, a 20-stack returns nothing at all.** Never assume a timeout means "the
bridge is down" — the scene may be alive and merely busy (§6.5 rule 4).

**The gate has been run.** The numbers recorded in §8's *measured* column are the P6-D live gate of
2026-10-05, not expectations: `massing.ms` 27 nodes idempotent over 3 runs, 9 bboxes within
**0.000000 cm** of an independent Python prediction, `assembly.ms` **244** nodes with no throw and
idempotent over 3 runs, **52 of 52** cell bboxes within **0.000000 cm**, per-host volume identity
error **0.000000 cm³** on all 8 hosts (total wall **73 800 000 cm³**), 5 of 5 instances sharing their
prototype's `baseObject` with the plain-`copy` control reporting `false`, and `objects.count == 0`
after two delete sweeps. **Any rerun must reproduce these numbers or explain the difference.**

**UNVERIFIED, and S5 must not silently depend on it — escalate rather than assume:**

| Claim | Status | What you do |
|---|---|---|
| Rotating a placed instance with `n.rotation = quat <deg> [0,0,1]` and the resulting **world bbox** matching the run-angle prediction | The `quat` form **is verified** (100×200×20 box: rot 0 spans X 100 / Y 200, rot 90 spans X 200 / Y 100, `z_rotation` reads `90.0`). The *predicted bbox for a run of 90°* is the thing to confirm at the gate | Apply it and record what came back. A throw is a **measurement** that goes in `CHECKPOINT.md` and on `ESCALATED` — never a reason to place unrotated boxes and call the gate passed |
| `3dsmax-mcp_clone_objects` in `mode: "instance"` agreeing with the scripted route | Not required — the scripted route is the contract's. Use it only as a second measurement and **record which route produced the nodes** | A disagreement between the two routes is a **finding**, not something to average |
| Per-layer colour and render flags | **UNVERIFIED**, no probe (`11` O-7) | Not part of this stage. Do not build on it |

---

## 8. Verification — the completion gate

Check every row. **The validator covers the mechanical subset only**; rows 3, 4, 5, 6, 7, 10, 11, 12, 13,
14, 15 and 17 are yours. The *measured* column carries the numbers the P6-D live gate of 2026-10-05
actually returned for `pavilion-01` — a rerun must reproduce them or explain the difference.

| # | Gate | Measured expectation | Checked by |
|---|---|---|---|
| 1 | `python scripts/validate_specs.py --dir <specs_dir> --build` exits **0** with **`FAIL 0`**, and the same command with `--warnings-as-errors` also exits **0** with `FAIL 0` | two transcripts, **both modes, not one** | you |
| 2 | **`G-71`…`G-78`, `G-82` and `G-83` all PASS, or SKIP with a stated reason.** A SKIP is not a pass (`07` §9.6). **`G-80` always SKIPs at lint time** — it observes the built scene; the emitted census and row 4 assert it instead | `n PASS / n SKIP`, each SKIP with its reason | you, reading the `--json` output row by row |
| 3 | **Every `G-71`…`G-83` was proved to fire by fault injection** on a **temp copy**; ≥ 8 cases, each recorded. **Call the predicates directly with a mutated document — do not mutate a builder *output* and rebuild**, which proves nothing because the rebuild overwrites the mutation | the failure text each mutant produced. P6-D: **11 of 11** fired in the builder and **3 of 3** in the linter, baseline clean | you — never on `examples/` |
| 4 | **The emitted census ran and did not throw.** The `.ms` **walks the scene** and counts the instances, prototypes and `WAL_` cells it finds, then throws on any mismatch | throw count **0**; the counts it compared are written down | the transcript of the `fileIn` |
| 5 | **`objects.count == massing nodes + placements + prototypes + cells`** | `pavilion-01`: **244** = 27 + 136 + 29 + 52, read back, exact equality. **Not assumed** | read-back |
| 6 | **Every sampled instance shares its prototype's `baseObject``, and the deliberate plain `copy` control reports **`false`** | `true` / `false`, **in the same call**. Measured: **5 / 5** shared, control `false` | read-back |
| 7 | **Sample bboxes are exact.** Five placed nodes, `node.min` / `node.max`, against a Python prediction from the CSV row + registry dimensions | worst `\|measured − expected\|` ≤ `tolerances.linear_cm` (0.5 cm); **measured 0.000000 cm** | you |
| 8 | **`G-80` closes at the gate**: the census agreed in every direction — placements vs CSV rows, openings vs cuts, **cells found in the scene vs `wall_cells[]`** | all three agreed; `G-77` orphans **0** in **both** directions | the census transcript |
| 9 | **The wall is tiled, not cut**: every opening's `host_ref` is a `facade_wall` and `kind: "difference"`; per host `Σ cell volume ==` wall − openings (`G-82`); every cell spans the wall's full thickness (`G-83`); every cell bbox matches its own `plan_rect_cm` / `z_range_cm` | 8 hosts / 16 openings / **52 cells**. Measured: worst cell bbox deviation **0.000000 cm**, per-host volume error **0.000000 cm³** on all 8 (total wall 73 800 000 cm³) | `G-76`, `G-82`, `G-83`, §6.2 |
| 10 | **`G-81` held at build and at the gate**: `addModifier` appears **zero** times in the emitted source, and every host's `modifiers.count` reads **0** — the emitted script asserts the hosts arrive with empty stacks | modifier count **0** everywhere. The old two-ceiling form (≤ 5 per call, ≤ 10 per node) is **retired**, not tightened: there is nothing to bound | you — grep the emitted source, then every host's `modifiers.count` |
| 11 | **Layer: `G-79` held.** The emitted `assembly.ms` contains **no** `node.layer`, **no** `LayerManager` setter and **no** layer-assignment helper — grepped, not assumed | match count **0** | you — `G-79` |
| 12 | **`G-75` held**: every `placements[].layer` equals its role's `layer_map` entry, and every `layer_map` key is one of the **eight** `07` §8.1.4 names, character for character | 8 names, 0 invented | `G-75`, `11` §1 |
| 13 | **No Max class, modifier, plugin or MCP tool name appears anywhere in `assembly.json`** — not in a `kind`, not in `source.reference`, not in an `origins` formula. A cut is `kind: "difference"`, a scatter is `kind: "scattered"` | match count **0** | you — `07` §11 + §12 |
| 14 | **`G-73` held**: every placement's `position_cm` and `rot_z_deg` equals its CSV row within `linear_cm` / `angle_deg`, and **nothing anywhere in the file derives from `dimensions.facades[].direction_deg`** | 0 placements disagree; 0 `direction_deg` derivations | `G-73`, `G-57` |
| 15 | **`G-72` held in both directions**: every `source_row` is a real data row, every real row appears once, no duplicate `source_row` | 136 = 136, 0 duplicates | `G-72` |
| 16 | **`G-74` held**: `node_name` unique across `placements[]`, `opening_cuts[]`, `wall_cells[]` **and** `scatter[]`, derived from its own `id` with dashes replaced, matching **N1** (no `-`) | 0 collisions. **Check the derivation too** — a duplicated `node_name` and a name not derived from its id both slipped through when the tiling first landed | `G-74`, `11` N1 |
| 17 | **The scatter is declared and NOT built**: no `ChaosScatter` node exists in the scene, `objects.count == 244`, and every `scatter[]` declaration resolves and is in range. **The apply route is handed to the user**, with the note that it changes the node count | the two numbers, plus the resolution result for each declaration | `objects`, `scatter[]` |
| 18 | **Determinism proved by construction**: the same inputs built into **two temp dirs** are **byte-identical** to each other and to the committed artefacts | `tmpA == tmpB == committed`, both files | you — hash both outputs |
| 19 | **The scene was returned to 0.** `objects.count == 0` after the gate, after **two** delete sweeps | **0** | the count is the evidence |
| 20 | **Nothing was filled silently from `09`'s do-not-default list**, and every P6-flagged `A-nnn` from §4 step 2 is named | `A-025` named | you |

**The measurement route.** Read the node back and compare against the spec — do not eyeball a viewport
and do not ask a tool whether the geometry "looks right". `node.min` / `node.max`, or equivalently
`node.width` / `node.length` / `node.height`; they agree because `Box` geometry is centred in X/Y and
based at `pos.z`. With `abs(measured − expected) ≤ tolerances.linear_cm`. A larger mismatch is a real
inconsistency in the spec or the builder: report both figures and stop, and do not nudge the node or
widen the tolerance.

---

## 9. Cleanup

Cleanup is part of the build, not a chore after it. **This stage has an unusually long cleanup**,
because every instance is a separate node, every wall cell is a separate node, and the hosts are
shared massing geometry.

| # | Rule | Evidence |
|---|---|---|
| 1 | **Delete every gate node in the same call that created it.** If a call fails or is aborted, **sweep** — do not assume nothing was created | A failed/aborted call leaves its objects behind; orphans accumulated across aborted probes and had to be swept (`CHECKPOINT.md`) |
| 2 | **Delete instances before prototypes.** `delete <base>` does **not** delete its instances | Measured: after deleting a base, its instances survived (`CHECKPOINT.md`, P4b-r). Deleting prototypes first leaves a full set of orphans that look like a clean scene |
| 3 | **Collect names first, then delete by name — and run it twice.** `for o in objects do append names o.name`, then for each name `local nd = getNodeByName nm; if nd != undefined do delete nd` | **`for o in objects do delete o` silently skips entries**, and it left **24 orphans** at P5. Deleting a base does not delete its instances, so one pass is never enough |
| 4 | **The sweep is explicit** — `3dsmax-mcp_delete_objects` with spec-derived names, never "delete everything", and **compare `objects.count` before and after** | You are not the only tenant of that session; a blanket delete destroys the user's own work (`11` H12) |
| 5 | **Never delete a `facade_wall` host.** It is `massing.json` geometry and it **stays** — the cells are *additional* nodes alongside it, which is why the gate's count is `massing + placements + prototypes + cells` (244 for `pavilion-01`, of which 27 are massing) | `11` §6 delivery checklist. Deleting a host destroys massing |
| 6 | **Delete the `WAL_` cells as S5's own nodes** — by name, from `wall_cells[].node_name`, in the same call that created them | **There is nothing to undo on a host any more.** The old "remove the modifiers S5 added" step is gone precisely because S5 adds none: no modifier was attached, so none has to be detached, and a bare modifier is not a node and could not have been deleted anyway (the P4b rule) |
| 7 | **If the user applied the scatter before asking for cleanup, delete the `ChaosScatter` node before its model nodes** | A scatter referencing a deleted model leaves an orphan or a dead reference. **Normally there is no scatter to delete — S5 does not build one** (§6.6) |
| 8 | **Place and delete in batches**, one script per call under ~2 s | `3dsmax-mcp_execute_maxscript` is main-thread; a long script freezes the UI |
| 9 | **Cleanup never touches the massing or NURBS geometry from S2/S3** — only S5's prototypes, instances, wall cells, scatter nodes and orphans are removed | `11` §6 |

---

## 10. Escalation policy

S5 executes; it does not design, and it escalates anything it cannot build honestly.

| You may decide alone | Boundary |
|---|---|
| Which `07` §8.5 key a piece of assembly data belongs at; placement, cut, **cell** and scatter id assignment and ordering | If a value does not fit a key, escalate — **never invent one** (`07` §12). Ids ascend, zero-padded, fixed order (§4) |
| **Nothing about a modifier stack** — the stage attaches none, so there is no chunking to choose | The former "how do I chunk the cut passes" decision is **closed**: a ceiling of zero cannot be chunked (§6.5). A stage that needs a stack escalates instead |
| Which optional `assembly.json` keys to populate | Omit rather than guess. An honest omission beats an invented value |
| Whether two axis offsets within `linear_cm` are the same axis | Treat as same, and record it. **Never widen `linear_cm`** to avoid the decision |

### 10.1 You must stop and ask

| Topic | Why | Goes to |
|---|---|---|
| **A cut host that is not an axis-aligned `facade_wall` prism** — a NURBS surface, a swept or curved wall, a mitred corner | A column-row decomposition along a straight run is what the tiling assumes; the only verified primitive is `Box(width:, length:, height:, pos:)`, axis-aligned. A NURBS host is a `07` §12 step 1 change, and its relational properties may only be read on committed sub-objects (the P4b rule) | **S3's owner** via `07`'s owner — S5 never edits `massing.json` |
| **Any proposal to cut an opening with a modifier again** | The Boolean modifier cannot be made to cut in this build, and a modifier stack of 20 froze Max until the machine rebooted (§6.2.1, §6.5) | the **user**, with the evidence from §6.2.1. There is no variant of the cut path that is merely slow |
| **A non-rectangular or rotated component** in `components_registry.json` | The only verified placement primitive is `Box(width:, length:, height:, pos:)` — axis-aligned. A non-rectangular block is a different component class, and `Box` cannot express it | **S4b's owner** |
| **`A-025` would change the wall thickness** — the modelled facade-wall thickness is a *reference-only* proxy | A real build-up is a curtain-wall system schedule, and a licensed professional owns it. It now sets every cell's thin-axis extent (`G-83`), so it changes the whole tiling | the user (`E5`), with the host and the cells it would change |
| **A `seed` outside 1…31337**, or a project that wants a *random* seed | `seed` is **data** in `assembly.json`. A run-time or generated seed makes the scatter unreproducible when the user applies it by hand (§6.6) | **S1** — the input vocabulary, via `07`'s owner |
| **`placements.len() > defaults.instance_limit_guard`** (2000) | The guard exists so a corrupt CSV cannot ask Max for a million instances. Exceeding it is an input defect, not a reason to raise the guard | **S1** |
| **A request to apply layers** | It cannot work. Nine routes ruled out (§6.3). Layer is data and the user applies it in the Layer dialog | the **user** — report the negative with its nine routes; do not attempt it |
| **A missing or contradictory dimension** — a component size, a host profile, an opening extent — or two keys that disagree | S5 may not fill a dimension and may not hand-edit a locked file | **S1 / S4b** |
| **Any fact not in `CHECKPOINT.md` §"Verified facts"** — including scatter sub-object wiring beyond the parameter map, and per-layer flags | §1.2: S5 escalates for an orchestrator probe, it does not open one | the **orchestrator** |

### 10.2 How to ask

A question list, not a paragraph — one line per question:

```
<dotted key path> — <the competing values with units> — <what each would change in the assembly> — <your recommendation, if you have one>
```

**Nothing may be recorded as blocked, impossible, non-buildable or non-existent without a transcript
showing the attempt and the exact error.** A negative needs the same discipline as a positive — this repo
has shipped fabricated negatives (`CHECKPOINT.md` §"Incident log"), and one of them was a layer claim
that had to be *un*-retracted. "Layer assignment is impossible from this bridge" is now safe to say
because nine routes were executed and are recorded; the next negative you form must meet that bar.

---

## 11. Anti-patterns and incident guards

This stage runs against a live session, and it is the stage most able to produce a confident-sounding
statement about the environment. Four of the entries below cost a reboot, an incident-log entry, a
reboot and a silent no-op respectively.

| Anti-pattern | Instead |
|---|---|
| **AP-1 · Attaching modifiers to build the walls at all** — "it's just one more Boolean", "chunk it, five per call is fine" | **Zero.** This stage attaches **no** modifier: `addModifier` count in `assembly.ms` must be **0** (`G-81`). The walls are `wall_cells[]`, solid boxes. The old ceilings (≤ 5 per call, ≤ 10 per node) are **retired, not tightened** — 5 and 10 rungs were clean and **20 froze Max until the machine rebooted**, which is why the bound is zero rather than small (§6.5). **Do not re-run the ladder** — it is measured |
| **AP-2 · Concluding "the bridge is down" because a call timed out** | A timeout is the *only* symptom of the hang, and a recoverable hang still burns the call. Verify with a cheap `3dsmax-mcp_get_bridge_status` first (§6.5) |
| **AP-3 · Calling `setCopyMode #instance`** | It **does not exist** in this build. The instance route is `n = copy src` then `n.baseObject = src.baseObject` (§6.1) |
| **AP-4 · Calling `rotationZ` / `rotationX` / `rotationY` / `matrix3` / `angle` / `findString`** | None of them exist, measured with controls. Use `n.rotation = quat <degrees> [0,0,1]`, and `substring s 1 n` for a substring test |
| **AP-5 · Writing `pos = [cx, cy, cz]` and expecting a centred box** | On a `Box`, `node.pos` puts the **base** at `pos.z` (geometry centres on x/y). Still true after `copy`, after `baseObject =` and after rotation. Centre it with `pos.z = cz − height/2` — getting this wrong put every P5 panel one full height too high, and the measurement caught it |
| **AP-6 · `for o in objects do delete o`** | It **silently skips entries** — it left 24 orphans at P5. Collect names first, delete by name, and **run twice**: deleting a base does not delete its instances (§9 rule 3) |
| **AP-7 · Emitting layer code** — `node.layer = ...`, a `LayerManager` setter, a "fix" for nodes landing on the wrong layer | It cannot work. Nine routes executed, all failed; `3dsmax-mcp_manage_layers`' vocabulary is exactly `{list, create, delete}` and `3dsmax-mcp_set_object_property` emits the same read-only assignment. **Layer is data; the user applies it.** A layer statement in `assembly.ms` is a **build FAIL** (`G-79`, §6.3) |
| **AP-8 · Attaching `Extrude`, `Bevel`, `Sweep`, `Lathe`, `Surface`, `CrossSection` or `Bevel_Profile` and treating the throw as noise** | They construct and then `addModifier` **throws**, `mods=0` — the P4b-r "6 unattachable modifiers" finding. `Bevel_Profile` is unusable through every route. **A throw that produced no modifier is a FAIL, not a partial pass.** S5 needs none of them: the attachable set in §6.4 is a routing fact, and this stage's own bound is zero |
| **AP-9 · Calling `3dsmax-mcp_scatter_forest_pack`, any of the 14 `3dsmax-mcp_tyflow_*` tools, or `3dsmax-mcp_get_railclone_style_graph`** | Those plugins are **not installed**. Substitute Chaos Scatter for scatter, PhysX / Max particles for physics, instance copies for RailClone-style patterning (`references/14-chaos-scatter.md` §4) |
| **AP-10 · Calling `mcg_*` or `3dsmax-mcp_curve_model`, or reaching for `geometry_qa` / `contact_check` / `scene_qa`** | **None of them exist in this bridge.** Max Creation Graph is undrivable from here and the QA tools have no replacement by that name — the real read-back is `3dsmax-mcp_execute_maxscript` plus `FpInterface`. Record the absence; never emulate it by hand |
| **AP-11 · Emitting the typo-free `distributionDensityPattern`** | The real property name is **`distributionDesityPattern`**, typo included. The **spec** uses the corrected spelling `distribution_density_pattern`; the **builder** emits the typo. A spec that carries the typo breaks `07`'s no-class-names rule |
| **AP-12 · Generating a `seed` at run time**, or leaving it unset | `seed` is 1…31337 and is **data** in `assembly.json`. A generated seed fails `G-78` and makes the scatter unreproducible when the user applies it by hand — the optional manual check in `references/14-chaos-scatter.md` §5.1 would report it, if anyone ran it |
| **AP-13 · Recomputing a placement's position or angle from `dimensions.json`** | Copy the CSV row. `rot_z_deg` is the CSV's number and equals `run_angle_deg`, **not** `direction_deg` — two of the example's four facades are 180° wrong if the facing label is used (`G-73`, §2.1) |
| **AP-14 · Mixing frames: treating `u_range_cm` as a world offset** | `u` is **facade-local**; the world position along the run is `start_corner_cm + u`. Mixing frames is how the P5 sliver defect happened (§6.2) |
| **AP-15 · Asserting a placement count and calling the builder's number wrong** (or the reverse) | **No gate assumes a count.** The gates are the two-direction CSV equality, one cut per opening in both directions, the emitted census — which **walks the scene** — and the zero-modifier bound (`G-72`, `G-77`, `G-80`, `G-81`) |
| **AP-16 · Hand-editing a generated JSON** so the next rebuild silently destroys the edit | Both files are builder output; a divergent rebuild is **refused, naming the first differing key path** (§2.2). Verify by recomputing from the CSV and `massing.json` |
| **AP-17 · Treating "the `.ms` was written" as done** | The gate is §7: `fileIn` it three times, count it, prove the discriminator with its control, measure five nodes, **measure every cell's bbox and every host's volume identity**, confirm every host's modifier count is 0, read the scatter back, delete everything. **An unrun `.ms` is an unverified `.ms`** |
| **AP-18 · Calling the gate passed on a number you inferred**, or writing "matches" where a number belongs | `MEASURED` is a number: `objects.count == …`, worst deviation `… cm`, per-host volume error `… cm³`, `getInstanceCount() == …`. If the gate could not run, write `NOT MEASURED` and say why (§12) |
| **AP-19 · Concluding one Max error means the bridge is broken** | A large set of names in the connected toolset belongs to the **Rhino** server and fails confusingly against Max (`AGENTS.md` §"MCP tool-name collisions"). Only `3dsmax-mcp_*` acts on Max |
| **AP-20 · Rewriting a reference or a sibling stage's contract on suspicion** | They are **unverified, not disproven**. Verify claim by claim, then correct only what actually fails (`AGENTS.md`, §"The one rule that matters most") |
| **AP-21 · `try { } catch { }`** — the brace form | It is a **parse error** in this dialect. Use `try ( ) catch ( )`. Also: `("x" + i as string)` throws on precedence — write `("x" + (i as string))`; `getCurrentException()` throws inside a `catch`; `stopCreating` takes **0** args; `modifiers <node>` does not work as a *function* — use the `node.modifiers` property |
| **AP-22 · Cutting openings with the Boolean modifier, and trusting a census that counts its own loop** | The Boolean modifier **cannot be made to cut in this build**: `Boolean()` throws, `BooleanMod()` carries Voxel Map's paramblock, and the bridge's `add_modifier` **attaches** one whose operand is never set — `verts=8 faces=12`, unchanged, for every `params` spelling (§6.2.1). The previous build therefore shipped **unpierced walls and reported success**, because its `G-80` census counted its own iterations and read `cut_count = 16` against a scene with **zero** modifiers. Two rules answer it: build `wall_cells[]` (`G-82`, `G-83`) and make the census **observe the scene** (`G-80`). A modifier that attaches and does nothing is worse than one that throws |
| **AP-23 · Fault-injecting by mutating a builder's *output* and rebuilding** | It proves nothing: the rebuild overwrites the mutation before any rule sees it — the first P6-D harness reported **0 of 8 fired** for exactly that reason. Call the predicates directly with a mutated **document** (§8 row 3) |

### 11.1 Context discipline

You are a worker with a small budget; the main thread is the scarce resource (`AGENTS.md` §"Context
budget"). **Read `_p6-contract.md` once, `07` §8.5 + §9.9 once, and the four input files once**, end to
end — never re-read the contract to settle one key name. **Compute, don't transcribe.** The whole stage
is a join of four tables — 136 placements and **52 wall cells** over 16 openings — so hand-verifying
**one host's cell-volume identity** and **one placement's predicted bbox** is enough to catch a wrong
builder. **Never probe** (§1.2). **No bulk dumps in the final message**; never read another agent's
transcript.

---

## 12. Return contract

Return **exactly** this, **≤ 12 lines** — no file dumps, no JSON blobs, no transcript excerpts:

```
S5 <project id>
FILES: <path> (<n> lines) · <path> (<n> lines)
VALIDATOR: scripts/validate_specs.py --dir <specs_dir> --build -> exit <n>  (PASS <n> · FAIL <n> · WARN <n> · SKIP <n>)
G-71..G-83: <n> PASS / <n> SKIP — <for each SKIP, the reason; G-80 always SKIPs at lint>
BUILDER: scripts/place_components.py --stage assembly -> exit <n> · <n> placements / <n> prototypes / <n> wall cells over <n> hosts / <n> scatter declaration rows · addModifier emitted = <n> (must be 0, G-81) · host stacks max = <n> · layer statements emitted = 0
LIVE: assembly.ms fileIn x3 in 3ds Max, no error · objects.count == massing + placements + prototypes + cells = <n> = <yes/no> · instance shares baseObject = <true>, deliberate copy = <false> · cell bboxes vs spec worst = <n> cm · per-host volume error worst = <n> cm3 · host modifiers.count = <n> · scatter getModelCount = <n>, getInstanceCount = <n>, save/load count stable = <yes/no> · worst |measured - expected| over 5 nodes = <n> cm (tolerance linear_cm = <n> cm)
CENSUS: emitted census threw <n> times · scene walk found <n> WAL_ cells == wall_cells[] = <yes/no> · placements == CSV rows both directions = <yes/no> · cuts == openings both directions = <yes/no>
DETERMINISM: two temp dirs byte-identical = <yes/no> · equal to the committed files = <yes/no>
CLEANUP: <n> instances deleted before <n> prototypes · <n> cells deleted by name · two sweeps · objects.count after = <n> · massing (incl. <n> facade_wall hosts) untouched
P6-RECHECK: <A-nnn ids> — <each named, or "none">
ESCALATED: <n> — <one line each: the topic, the question, whether it is answered>
OBJECTIONS: <one line per defect in a file you do not own, naming file and section, or "none">
INCOMPLETE: <what you could not do, or "none">
```

Rules for the fields:

- **Line counts** are the real counts from disk. The validator and builder lines are only valid **with a
  transcript**: paste the exit code you observed; if you did not run one, write `NOT RUN` and say why on
  `INCOMPLETE`. **`SKIP` is reported separately from `PASS`**, never folded into it.
  **`MEASURED` is a number, not an adjective** — "matches" is not evidence; `0.0 cm worst deviation` is.
  If you measured nothing, say `NOT MEASURED`.
- **`LIVE` is never optional and never inferred.** If the gate did not run, `LIVE: NOT RUN — <reason>`
  and the stage is `INCOMPLETE`. A throw is reported as a **measurement** in the same line, not as a
  warning elsewhere.
- **`BUILDER`'s modifier and layer lines are gates, not notes.** `addModifier emitted = 0` and
  `layer statements emitted = 0`, or the build failed (`G-81`, `G-79`). There is no partial credit and
  no "I added it as a comment".
- **`P6-RECHECK` is never silently empty** — every `recheck_stage: "P6"` entry is named, because you are
  the recheck stage.
- **`OBJECTIONS`** is where a `validate_specs.py` or `place_components.py` behaviour that contradicts
  `_p6-contract.md` §3 / §4 goes, and where any proposal to reintroduce a modifier stack goes — one line
  each, naming the file and the section. **`INCOMPLETE`** is where you say what you could not finish; a
  field that hides a gap is worse than an admission.