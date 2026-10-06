---
name: 3dsmax-arch-nurbs-ultimate
description: Spec-first architectural, exterior and NURBS modeling for Autodesk 3ds Max 2026 through the cl0nazepamm/3dsmax-mcp bridge, plus a hand-off for manual material assignment. Ships a stage-by-stage build pipeline that has been executed live against Max 2026.3.2 - massing, relational NURBS via NURBSSet/NURBSNode, a panelised facade grid, and reference-instanced assembly with tiled wall openings. States the verified tool inventory, the tools that always fail because forestPack/tyFlow/railClone are absent, Rhino-server tool-name collisions, and the measured MAXScript traps (Boolean unusable, six unattachable modifiers, the 20-modifier freeze, absent function names). Materials, automated QA and export are out of scope by user decision.
---

# 3ds Max MCP — Ultimate Architecture, Exteriors and NURBS Agent Skill

Master orchestrator for controlling Autodesk 3ds Max via [`cl0nazepamm/3dsmax-mcp`](https://github.com/cl0nazepamm/3dsmax-mcp), specialized for architectural modeling, exterior environments, parametric facades and mathematical NURBS surfaces.

Verified against 3ds Max **2026.3.2 (Security Fix)**, transport `namedpipe`, protocol 2, `safeMode: true`, `threadMode: mainThread`.

---

## 0. Current state and scope

**Read this before anything else. `CHECKPOINT.md` is the status board of record; this section is a summary of it, not a second source.**

### 0.1 What is built and measured

Stages **P0 → P6** are closed. Every one was executed against live Max, and every emitted artefact was `fileIn`-ed and measured — not merely self-checked offline. Headline numbers, all from the `CHECKPOINT.md` stage table:

| Delivered | Live gate, as measured |
| :--- | :--- |
| Spec grammar + input (S1), `G-1`…`G-33` | offline: `PASS 52 / FAIL 0 / WARN 0`; 54-case fault battery **54/54** |
| Layer standard + massing (S2), `G-34`…`G-40` | `fileIn examples/massing.ms` → **27** nodes (22 `Box` + 5 `Dummy`), idempotent over 3 runs, **9/9** bboxes exact to `0.000000 cm` |
| NURBS core + the four relational kinds (S3), `G-41`…`G-56` | `fileIn examples/nurbs.ms` → **10** nodes, idempotent over 3 runs, every node bbox measured |
| Facade grid + component registry (S4a/S4b), `G-57`…`G-70` | `world_table.csv` read **by MAXScript itself** → 136 rows → 136 panels placed, `objects.count` = **165 = 136 + 29** |
| Assembly + Chaos Scatter (S5), `G-71`…`G-83` | `fileIn examples/assembly.ms` → **244** nodes = 27 + 136 `PLC_` + 29 `PROTO_` + **52 `WAL_`**, idempotent, **0 modifiers**, wall-volume identity exact to **`0.000000 cm³`** on all 8 hosts |
| **Full S1→S5 chain, re-run end to end** | the three `.ms` in order → **254** nodes (the 244 above **plus the 10 NURBS nodes**, which P6's gate never loaded), idempotent over 3 calls, **0 modifiers**, 52/52 cell bboxes exact, **0 nodes off layer 0**, scene back to **0** |

> **Two node counts, both correct, different chains.** **244** is `massing.ms` + `assembly.ms`.
> **254** is the whole chain including `nurbs.ms`. Always say which one you mean.

Four measured facts about Max shaped the whole architecture, and every stage inherits them:

- **Scene units are centimetres, scale 1.0.** A spec value in cm reaches Max unchanged.
- **The Boolean modifier is unusable in this build.** It attaches and silently cuts nothing. Openings are cut by **tiling the wall with solid cells** instead (§2).
- **An object's layer cannot be assigned from script.** Nine routes ruled out with transcripts. Layer attribution is data the user applies by hand (§5).
- **Relational NURBS properties are readable only on a committed sub-object**, never on a freshly constructed one (§3).

### 0.2 What is deliberately out of scope

**P7 (Corona materials + UVs), P8 (QA loop) and P9 (export) are SKIPPED BY USER DECISION.** Not pending, not next, not partially built. Do not route a reader toward them, do not write stubs, do not name a script that would perform them. Consequences:

- **Materials are applied by hand.** The probes that had run before the cancellation are kept in `references/_p7-evidence.md` — real measurements that close the P0 renderer question and the P0 "16 Corona classes" question, and they are what §5.4 is built on.
- **There is no automated QA loop.** Verification is the per-stage live gate recorded in `CHECKPOINT.md`; §6.4 is the manual replacement. `qa.json` is a reserved spec file and is **absent**.
- **There is no export stage.** `export_max.py` was never written. This pack's output is a live Max scene.
- **P10 is reduced to a lite version:** this file plus `agents/max-orchestrator.md`.

The full stage-by-stage map, including every skipped row, is §4.

### 0.3 The deliverable

**A measured 3ds Max building model, plus a hand-off for manual material assignment.** A user opens the scene, assigns Corona materials to the `PROTO_` handles, applies `layer_map` in the Layer dialog, and renders. Nothing in this pack assigns a material for them.

Full hand-off detail: **`agents/max-orchestrator.md` §5**. Short version: §5 below.

---

## 1. Tool Routing

### 1.1 Ground truth hierarchy

1. **MAXScript execution is the only ground truth about what exists.** `execute_maxscript` constructs classes; introspection tools only hint.
2. Prefer a dedicated typed MCP tool over raw MAXScript **when that tool exists and fits the request**.
3. NURBS has **no** dedicated typed tools. All NURBS construction and inspection runs through `execute_maxscript`. This is a genuine limitation of the bridge, not a defect of the API.
4. Every tool name in this file appears without the MCP server prefix. `create_object` in a routing table means `3dsmax-mcp_create_object`. See section 1.3 before using that name.

### 1.2 Hard rule — tools that ALWAYS fail

forestPack, forestLite, tyFlow, railClone and phoenixFD are **absent** from this installation. The following tools exist in the schema but can never succeed. Never route to them; use the substitution instead.

| Never call | Substituting pipeline |
| :--- | :--- |
| `scatter_forest_pack` | **Chaos Scatter** via `execute_maxscript`: `ChaosScatter()` (superclass `geometry`, classID `[1672609897, 845042209]`). `CScatter` is its base class and is **NotCreatable** — always construct `ChaosScatter`. Wire `targetNodes` / `modelNodes` / `modelFrequencies` / `seed` / `instanceCountLimit`. Determinism hook: `saveConfiguration` / `loadConfiguration` / `getInstanceCount()` FpInterface functions. |
| `create_tyflow`, `create_tyflow_preset`, `add_tyflow_event`, `add_tyflow_collision`, `connect_tyflow_events`, `modify_tyflow_operator`, `remove_tyflow_element`, `get_tyflow_info`, `get_tyflow_particles`, `get_tyflow_particle_count`, `reset_tyflow_simulation`, `set_tyflow_physx`, `set_tyflow_shape`, `list_tyflow_operator_types` | Particle simulation has no typed path. Use Chaos Scatter with `surfaceRandomUseDensity`, `distributionDesityPattern` (the typo is the real property name), `distributionLimitCoordSpace`, `surfaceUvSpacingU/V` and `surfaceUvJitterU/V` for static distribution; use keyframed MAXScript transforms plus `assign_controller` / `add_controller_target` for animated motion. |
| `get_railclone_style_graph` | Modular facades, curtain walls, railings and fences: MAXScript array of source objects, then `clone_objects(names:[...], mode:"instance")`. For genuine per-bay variation use a **Data Channel** modifier (`add_data_channel`, `set_data_channel_operator`) or per-clone transforms via `transform_object`. |
| every `mcg_*` tool, and `curve_model` | **No such tool exists in the connected toolset** — verified by direct inspection, not inferred. Max Creation Graph is undrivable from this bridge. Use `Edit_Poly` / `polyop.*` and the parametric primitives. |

### 1.3 Hard rule — Rhino tool-name collisions

The connected toolset also exposes the **Rhino** MCP server. These names belong to **Rhino, not 3ds Max**:

`get_document_summary`, `get_objects`, `get_object_info`, `create_object` (different schema entirely), `analyze_objects`, `section_profile`, `boolean_union`, `boolean_difference`, `boolean_intersection`, `measure_objects`, `loft`, `pipe`, `sweep1`, `extrude_curve`, `offset_curve`, `intersect_curves`, `project_curve`, and every `gh_*` Grasshopper tool.

Calling one against Max returns a confusing error and makes it look as though the bridge is down. Prefix explicitly with `3dsmax-mcp_` when you mean Max.

Also not present, under any prefix: `geometry_qa`, `contact_check`, `scene_qa`, `agent_viewport`, `set_viewport`, `create_lights`, `inspect_lights`, `edit_lights`, `lighting_capabilities`. See §6 for what replaces them.

### 1.4 Verified tool inventory (routing table)

Only these tools are available. Anything not listed here does not exist.

| Group | Tools |
| :--- | :--- |
| **Scene read** | `get_bridge_status`, `get_session_context`, `get_scene_snapshot`, `get_scene_info`, `get_scene_delta`, `get_selection`, `get_selection_snapshot`, `watch_scene`, `learn_scene_patterns` |
| **Create** | `create_object`, `build_floor_plan` |
| **Edit** | `transform_object`, `clone_objects`, `delete_objects`, `batch_rename_objects`, `set_object_property`, `set_visibility`, `select_objects` |
| **Organize** | `manage_layers`, `manage_groups`, `manage_selection_sets`, `set_parent` |
| **Modifiers** | `add_modifier`, `remove_modifier`, `collapse_modifier_stack`, `set_modifier_state`, `inspect_modifier_properties`, `inspect_properties`, `inspect_object`, `inspect_track_view`, `batch_modify`, `make_modifier_unique`, `add_data_channel`, `set_data_channel_operator`, `inspect_data_channel`, `add_dc_script_operator`, `list_dc_presets`, `load_dc_preset` |
| **Materials** | `assign_material`, `get_materials`, `get_material_slots`, `set_material_property`, `set_material_properties`, `set_sub_material`, `replace_material`, `batch_replace_materials`, `create_material_from_textures`, `create_shell_material`, `palette_laydown`, `introspect_osl`, `write_osl_shader`, `create_texture_map`, `set_texture_map_properties` |
| **Verification / introspection** | `introspect_class`, `introspect_instance`, `get_plugin_capabilities`, `refresh_plugin_manifest`, `get_plugin_manifest`, `discover_plugin_classes`, `discover_plugin_surface`, `list_plugin_classes`, `inspect_plugin_class`, `inspect_plugin_constructor`, `inspect_plugin_instance`, `map_class_relationships`, `find_class_instances`, `find_objects_by_property`, `list_wireable_params`, `get_wired_params`, `wire_params`, `unwire_params`, `get_dependencies`, `walk_references`, `get_instances`, `get_hierarchy`, `analyze_node_orientation` |
| **Animation** | `assign_controller`, `add_controller_target`, `set_controller_props`, `inspect_controller`, `get_state_sets`, `get_camera_sequence` |
| **Effects** | `get_effects`, `toggle_effect`, `delete_effect` |
| **Capture** | `capture_viewport`, `capture_screen`, `capture_multi_view`, `isolate_and_capture_selected`, `render_scene` |
| **Files** | `inspect_max_file`, `batch_file_info`, `merge_from_file`, `search_max_files` |
| **Escape hatch** | `execute_maxscript` |

Three of these carry a **verified capability limit**, not a bug:

| Tool | Limit, as measured |
| :--- | :--- |
| `manage_layers` | The whole vocabulary is `list`, `create`, `delete`. 40+ candidate action names were rejected with a uniform `Unknown layer action`. **It cannot assign an object to a layer** |
| `add_modifier` | Of the 23 modifier classes that construct, **6 cannot be attached via MAXScript `addModifier`**: `Extrude` `Sweep` `Lathe` `Surface` `CrossSection` `Bevel_Profile`. This typed tool is the working route for 5 of them; `Bevel_Profile` fails through every route. `Boolean` attaches and is useless — §2 |
| `set_sub_material` | A node's sub-material index is not reachable from MAXScript at all (`materialID`, `subMaterialID`, `matID`, `materialId` all throw, with a control). Whole-material assignment is the only scripted route |

### 1.5 Core operational principles

- **Match the request.** Do not run `get_bridge_status` or `get_session_context` as a blind preamble; call them only when diagnosing a connection.
- **Sequential writes only.** Never issue mutating calls concurrently. Interleaved writes corrupt Max undo transactions and crash the bridge.
- **No guard tokens exist.** There is no token, freshness, or `STALE_*` protocol on this server. There is no progressive-dispatch indirection either — no toolset enumeration, no toolset descriptor, and no generic call wrapper. Call tools directly by name.
- **No multi-instance management API.** The bridge pins to the first connected Max instance, automatically, via named-pipe discovery. TCP `127.0.0.1:8765` is neither used nor required.
- **No dialog-inspection API.** If a call returns `BLOCKED_BY_DIALOG`, **never repeat it** — the first call is still blocked inside Max. Tell the user to dismiss the dialog in the UI, then re-read state with a read-only tool. If `USER_BUSY` comes back, Max holds an open interactive undo transaction: wait and retry read-only only.
- **A timeout is not a bridge outage.** Before concluding the bridge is down, run a cheap `get_bridge_status`. A recoverable hang still burns the whole call, and a `ConnectionError` naming TCP may be a cached dead pipe — §7.5.

---

## 2. Architecture and Exterior Decision Matrix

Pick the pipeline before creating geometry.

| Architectural Component | Correct pipeline | Read first |
| :--- | :--- | :--- |
| 2D footprints, site contours, profiles | Shape objects — `Rectangle`, `Line`, `NGon`, `Circle`, `Arc`, `Helix`, `Donut`, `Star`, `PipeObject`, `Text` — via `create_object` or `execute_maxscript` | `references/maxscript-splines-shapes.md` |
| Cornices, parapet copings, window frames, curbs, gutters, reveals | Shape profile plus the `Extrude` or `Sweep` modifier. Both throw on MAXScript `addModifier` — use `add_modifier` | `references/arch-modifiers-and-procedural-reference.md` |
| Columns, balusters, piers, tapered members, chimneys | `create_object` primitives, or shape profile plus `Lathe` (typed-tool route only), or Box plus taper/scale | `references/arch-modifiers-and-procedural-reference.md` |
| **Walls with punched window and door openings** | **Not a Boolean.** Build the wall as **solid cells** tiling wall-minus-openings: decompose along the run axis, cut at every opening's `u` boundary, then at the `v` boundaries covering each column. Every boundary comes from some opening edge, so the subdivision has no gap and no overlap | `agents/max-assembly.md`, `references/07-spec-grammar.md` §8.5.8 |
| Floor slabs, decks, prismatic massing | `create_object` primitives from a locked `massing.json`, emitted by `build_spec.py`. A `Box` is centred on `pos.x`/`pos.y` with its **base at `pos.z`** | `references/07-spec-grammar.md` §8.1, `agents/max-massing.md` |
| Pitched roofs, stairs, ramps, custom mullions | `create_object` plus Edit Poly, Extrude or other modifiers | `references/maxscript-mesh-poly-ops.md` |
| Modular multi-storey facades, curtain walls, railings, fences | MAXScript source array plus `clone_objects(mode:"instance")`. railClone is absent — see section 1.2 | `references/architecture-exterior-pipelines.md` |
| A **panelised facade grid** as spec-first geometry: bay and opening divisions, spandrels, mullions, transoms, and the placement table that drives it | **S4 — build the grid, do not hand-place it.** `scripts/facade_tables.py` derives `facade_grids.json` from `dimensions.json` (facades · levels · openings) and emits `facade_table.csv` + `world_table.csv`; `scripts/validate_specs.py` enforces `G-57`…`G-70`, where **`G-61` is a partition and `G-62` is exactly one panel per opening**. Place with `n = copy src` then `n.baseObject = src.baseObject` and `n.rotation = quat <deg> [0,0,1]` — `setCopyMode` and `rotationZ` **do not exist in this build** — and remember `node.pos` on a `Box` puts the **base** at `pos.z` | **`agents/max-facade.md`** (S4a) · `agents/max-components.md` (S4b) · `references/07-spec-grammar.md` §8.3 / §8.4 / §9.8 |
| A rotation for a panel on a facade run | **`run_angle_deg = atan2(end.y − start.y, end.x − start.x)`** — never `facades[].direction_deg`, which is a **compass facing label**: `F-S` and `F-N` both run along +X and carry `180.0` and `0.0`. `07` §8.3.1 carries this as a hard rule | `references/07-spec-grammar.md` §8.3.1, `agents/max-facade.md` §6.1 |
| Vegetation, lawns, gravel, scatter | **Chaos Scatter** via `execute_maxscript` — `ChaosScatter()`; `CScatter` is NotCreatable; set `seed` for determinism. Hide source geometry afterwards with `set_visibility` | `references/14-chaos-scatter.md` |
| Freeform and double-curved shells, canopies, diagrids, UV panelization, helical ramps, projected profiles on a surface | **NURBS via `execute_maxscript`** — `NURBSSet`, `NURBSULoftSurface`, `NURBSUVLoftSurface`, `NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface`, `NURBSOffsetSurface`, `NURBSProjectVectorCurve`, `getNURBSSet`, `evalPos`. This API is real and verified working | `references/12-nurbs-gotchas.md`, `references/nurbs-architecture-recipes.md` |
| The four **relational** forms as *specified geometry*: `rail_sweep`, `two_rail_sweep`, `blend`, `trim` | **Implemented and verified** — each constructs, commits inside a `NURBSNode`, evaluates, and exposes its full relational keyword set. These are spec kinds in the `nurbs.json` schema, not prose: `rail_sweep` · `two_rail_sweep` · `blend` · `trim` with `rail_section_ids` / `section_ids` / `parallel`, `parent1_ref` / `edge1` / `parent2_ref` / `edge2` / `tension1` / `tension2`, `surface_ref` / `trim_section_ids` / `p_vec` / `seed` / `flip_trim`. Build them through the **S3 stage contract**, not ad-hoc | **`agents/max-nurbs.md`** (S3), `references/07-spec-grammar.md` §8.2.7 / §8.2.8 / §9.7 (`G-50`…`G-56`), `references/12-nurbs-gotchas.md` §3.20–3.28 |
| A **skylight or aperture cut into** a NURBS surface | **Not this class, and not a Boolean modifier either.** `NURBSProjectVectorCurve trim:true` **projects** a closed profile and adds an untrimmed copy of the parent — it does not split and does not vary with the profile. Use a **surface split**, or build the wall by tiling | `references/12-nurbs-gotchas.md` §3.25–3.26, `agents/max-nurbs.md` §6.7.5 |
| Materials | **Corona.** The architectural class is **`_CoronaPhysicalMtl`** — with a leading underscore; `CoronaPhysicalMtl` is not a name in this build. 16 Corona classes are listed in `Material.classes`, **15 construct**, and `CoronaPortalMtl` throws. Fallbacks `OpenPBR`, `PhysicalMaterial`, `Standard` construct. No Arnold-specific, VRay, Octane or `RS_Standard_Material` classes exist. **Setting Corona is not optional and is not done by the bridge** — §5 | `references/maxscript-materials-textures.md`, `references/_p7-evidence.md` §2 |
| Renderer | **Set it explicitly.** Both `renderers.current` and `renderers.production` were `Arnold` in this installation and are **independent slots**. The bridge has **no** renderer tool | §5.4, `references/_p7-evidence.md` §1 |
| Kinetic, parametric or per-instance variation | Data Channel modifiers — `add_data_channel`, `set_data_channel_operator`, `add_dc_script_operator`, `list_dc_presets`, `load_dc_preset`. MCG tools do not exist. The tool's key is **`type`**, not `name`, and the real vocabulary is 32 snake_case operators; `DistToNode` and `FaceArea` are not among them | `references/arch-modifiers-and-procedural-reference.md` §2 |
| Trees, cars, street furniture, people, HDRIs, asset libraries | No Chaos Cosmos tooling is exposed. Author proxies with primitives or import `.max`/`.fbx` via `merge_from_file` / `search_max_files` | `references/architecture-exterior-pipelines.md` |
| Lighting | Create lights as scene nodes via `create_object` or `execute_maxscript`, then transform with `transform_object` and verify with `inspect_object` / `analyze_node_orientation`. No lighting toolset exists | `references/maxscript-rendering-cameras.md` |
| Putting geometry on a named layer | **No route.** `node.layer` is read-only from MAXScript (six assignment routes executed, all threw `Property is read-only: layer`); `LayerManager`'s setter is missing; `manage_layers` has no assignment action (40+ candidates rejected); `set_object_property` does not either. **Layer is data and is applied by hand** — §5.3 | `references/11-layer-standard.md`, `references/07-spec-grammar.md` §8.1.3 / §8.5.6 |

---

## 3. NURBS Protocol

3ds Max exposes no dedicated NURBS MCP tools. All NURBS work runs through `execute_maxscript` using the relational `NURBSSet` architecture. The API is real, complete and verified by live execution — earlier revisions of this skill wrongly claimed otherwise, and that claim must not return.

**The four relational classes — `NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface`, `NURBSProjectVectorCurve` — are implemented, verified geometry, not prose.** They are `surfaces[]` kinds in the `nurbs.json` schema (`rail_sweep`, `two_rail_sweep`, `blend`, `trim`), validated by `G-50`…`G-54`. **Route them to `agents/max-nurbs.md` and `references/07-spec-grammar.md` §8.2.7, not to prose.** Three properties of that route are worth knowing before you write any of it by hand:

- **Relational properties are readable only on the COMMITTED sub-object.** On a freshly constructed, unattached surface every relational name reads `ERR`, which looks exactly like "this class exposes no API". Build it, `appendObject`, `NURBSNode`, then read. This is the single most expensive trap in the repo — it once caused a whole stage to be deferred on a false negative.
- `NURBSBlendSurface` `tension1` / `tension2` default to **`0.0`**, the straight transition between the two selected edges. Above `0` the blend is pushed outward past **both** edges and the overshoot grows with the tension — at `1.0` the measured blend overshot its parent by 295 cm. A coincident edge pair gives a **zero-area surface**; a same-side pair bulges outside both parents. All three fail silently.
- A relation references its parents by **`nurbsID`**, which is an **`IntegerPtr`**. A string in a `parent*ID:` slot errors; a **synthetic integer crashes the 3ds Max process** (`EXCEPTION_ACCESS_VIOLATION`). Always bind it from a committed sub-object.

**Verify before you trust.** Before writing or debugging NURBS code, read `references/12-nurbs-gotchas.md`. It carries the verified class matrix, the open API questions, the measured relational-surface behaviour, and the control-test requirement for any existence probe.

### 3.1 The six Golden Rules

1. **Append ordinals, then `nurbsID` — and nothing else.**
   - *While building the set, before `NURBSNode nset`:* sub-objects are referenced by their **pre-commit append ordinal**, i.e. `nset.numObjects` read immediately after each `appendObject`. That is the value `parent:`, `parent1:`, `parent2:`, `rail:`, `rail1:`, `rail2:`, `appendCurve`, `appendUCurve` and `appendVCurve` take.
   - *After the node is committed:* a relation that must point at a surface in **another** node's set passes that surface's **`nurbsID`** in `parent1ID:` / `parent2ID:`. Bind it from the committed sub-object — `(getObject (getNURBSSet node #relational) <i>).nurbsID` — never write a literal. `nurbsID` is an `IntegerPtr`: a **string** errors (`Unable to convert: … to type: IntegerPtr`) and a **synthetic integer crashes the 3ds Max process** with `EXCEPTION_ACCESS_VIOLATION`, unrecoverably.
   - **Do not re-instantiate a relation's parents inside the relation's own set.** The parent keeps its own node; the relation's set then holds only the relation sub-object. Re-instantiation puts a parent named by two relations into the scene three times.
   - **Commit first.** `evalPos` and the relational keywords are **measured** unreadable before `NURBSNode` returns `undefined` / `ERR`; bind every `nurbsID` from a **committed** sub-object, immediately after that node commits.
   - **UNVERIFIED, do not build on it:** `appendCurveByID`, `appendUCurveByID`, `appendVCurveByID`, `setParent`, `setParentID`, `surfaceParent`, `surfaceParentID` and `addNURBSSet` have **no execution transcript**. They are unverified names, not a route. A cross-set **`rail1ID:` / `rail2ID:`** form is likewise unverified — a rail stays on the ordinal route.
2. **Strict knot invariant (`numKnots == order + numCVs`).**
   - Every `NURBSCVCurve`: `numKnots == order + numCVs`. Every `NURBSCVSurface`: `numUKnots == uOrder + numCVs.x`, `numVKnots == vOrder + numCVs.y`.
   - Set `.order`, then `.numCVs`, then `.numKnots`, then initialize **all** knots monotonically in `[0.0, 1.0]` (first `order` knots `0.0`, last `order` knots `1.0`) before `setCV`.
   - To pass a curve or surface directly through architectural points without manual knot math, use **`NURBSPointCurve`** or **`NURBSPointSurface`**.
3. **`appendObject` returns the string `"OK"`, not an index.** Read the index back from `nset.numObjects`. Using the return value raises `Unable to convert: OK to type: Integer`.
4. **`stopCreating` takes zero arguments.** `stopCreating node` raises `Argument count error`. Then read back with `local rset = getNURBSSet node #relational`.
5. **Analytical UV evaluation requires scene instantiation.** `uParameterRange`, `vParameterRange`, `evalPos`, `evalUTangent` and `evalVTangent` work only after the set is instantiated via `NURBSNode`. Multiply `evalPos surf u v` by `node.objectTransform`. Parameter ranges are **not** normalized to `[0,1]` — a measured surface returned `[0.0, 307.703]`. Use the measured range, not an assumed one.
6. **Display, tessellation and trimming.**
   - Hide internal construction curves: `setSurfaceDisplay node (NURBSDisplay displayCurves:false displaySurfaces:true displayDependents:true displayTrimming:true)`.
   - Set `nset.merge = 0.15`, and the same on `NURBSSurfaceApproximation`, to avoid render cracks between adjacent surfaces.
   - Always set `surf.generateUVs1 = true` **on the constructor**, and read it back on the **committed surface sub-object** — it throws on a `NURBSPoint`. It yields a **`0..1` normalised map regardless of the surface's size in cm**, and `generateUVs1:false` yields **no channel 1 at all**.
   - ⛔ **Do not use `setTiling` to set texel density.** It **silently floors both arguments to integers** (`2.99 → 2`, `3.5 → 3`), and **`getTiling` echoes the request, not the result** — after `setTiling s 3.5 1.5` it reads `[3.5, 1.5]` while the UVs are `3.0 × 1.0`. Use `addModifier node (Uvwmap maptype:0)` with `utile`/`vtile` for fractional tiling. See `references/13-uv-rules.md`.
   - Project a closed profile onto a surface with `NURBSProjectVectorCurve` (`parent1ID:<surfID>`, `parent2:<curveIdx>`, `pVec:[0,0,-1]`, `trim:false`, `flipTrim:false`). **`trim:true` does not cut** — it adds an untrimmed `NURBSCVSurface` copy of the parent to the relation's set, identically whatever the profile. Use a surface split for an aperture.
   - **UNVERIFIED:** the claim that `getViewTess` / `setViewTess` with `#displacement` triggers a C++ assertion dialog could not be reproduced. Treat it as unconfirmed. Avoid that call shape as a precaution, but do not cite it as verified behaviour.

### 3.2 `snippets/nurbs_arch_library.ms`

**No open bugs.** All twelve functions in `snippets/nurbs_arch_library.ms` were executed live (ten on 2026-10-04, plus `makePointSurfaceGrid` and `makeCVSurfaceGrid` at P4) and the library now has **zero known defects**. It loads and is usable as shipped.

Four bugs were found and fixed. Recorded here because the "three bugs, one unresolved" figure in earlier revisions of this skill was itself inherited from an unverified summary — two of them were the wrong diagnosis:

| # | Bug | Symptom | Fix |
| :--- | :--- | :--- | :--- |
| 1 | `appendObject` return value treated as an index | `Unable to convert: OK to type: Integer` | after `appendObject nset obj`, read `idx = nset.numObjects` |
| 2 | `stopCreating` called with an argument (4 call sites) | `Argument count error: StopCreating wanted 0, got 1` | drop the argument |
| 3 | ~~`NURBSControlVertex` does not construct~~ — **premise was false** | real error was `Unable to convert: [0,0,0] to type: NURBSControlVertex` | the class constructs; `setCV`/`setPoint` require the wrapper: `setCV crv i (NURBSControlVertex (pts[i] as point3) w)` |
| 4 | `close <crv>` is a **silent no-op** (found while fixing 3) | `closed:true` produced an open curve with no error; `isClosed` always reads false | `closed:true` seam-wills the CVs (first repeated last); `NURBSPointCurve closed:true` is the real closed path |

Also note: `Loft` resolves as a class name but `Loft()` throws `Not creatable: Loft`. The real lofting class is `NURBSULoftSurface`.

---

## 4. Stage map

Reconciled with the `CHECKPOINT.md` status board. **Where the two disagree, `CHECKPOINT.md` wins and this table is the bug.**

| Stage | Scope | Status | Verified by |
| :--- | :--- | :--- | :--- |
| P0 | Environment baseline | ✅ | `get_bridge_status`, `get_plugin_capabilities`, preflight `PASS 9/9`. Its NURBS conclusion was **wrong** and was corrected at P1 |
| P1 | Audit & salvage | ✅ | library executed live; the preflight inversion was tested |
| P1-b | Library bugfix | ✅ | all ten then-existing functions executed live 2026-10-04; 4 bugs fixed, one of which was a false premise |
| P2 | Spec grammar + input (S1) | ✅ | `PASS 52 / FAIL 0 / WARN 0`, clean under `--warnings-as-errors`; 54-case fault battery **54/54** |
| P3 | Layer standard + massing (S2) | ✅ | `fileIn examples/massing.ms` → 27 nodes, 3-run idempotent, 9/9 bboxes exact |
| P4 | NURBS core (S3) | ✅ | `fileIn examples/nurbs.ms` → 10 nodes, idempotent over 3 runs |
| P4b | NURBS remainder — the four relational kinds | ✅ | all four construct → commit → evaluate; this **overturned** P4's "not implemented" finding |
| P4b-r | Reference claim-by-claim pass | ✅ | both remaining reference files executed against live Max, controls in every batch |
| P5 | Facade grid + component registry (S4a/S4b) | ✅ | offline `PASS 120 / FAIL 0 / WARN 0 / SKIP 12`, fault injection **16/16**; live: 136 CSV rows read by MAXScript, 136 panels placed |
| P6 | Assembly + Chaos Scatter (S5) | ✅ | offline `PASS 138 / FAIL 0 / WARN 0 / SKIP 15`, fault injection **11/11** and **3/3**; live: 244 nodes, idempotent, **0 modifiers** |
| P7 | Corona materials + UVs (S6) | **SKIPPED BY USER DECISION** | not attempted as a stage. Probes run before the cancellation are recorded in `references/_p7-evidence.md` |
| P8 | QA loop (S7) | **SKIPPED BY USER DECISION** | not attempted. `qa.json` does not exist |
| P9 | Export (S8) | **SKIPPED BY USER DECISION** | not attempted. `export_max.py` was never written |
| P10 | Orchestrator + e2e | 🟡 reduced to a lite version | this `SKILL.md` + `agents/max-orchestrator.md` |

### 4.1 The stage contracts

Each stage has its own agent file carrying the contract, the procedure, a completion gate and anti-patterns. Route there rather than improvising.

| Stage | Contract |
| :--- | :--- |
| S1 — input → three locked spec files | `agents/max-input.md` |
| S2 — massing | `agents/max-massing.md` |
| S3 — NURBS, and the four relational kinds in particular | `agents/max-nurbs.md` |
| S4a — panelised facade grid | `agents/max-facade.md` |
| S4b — component registry | `agents/max-components.md` |
| S5 — assembly: instances, tiled walls, Chaos Scatter | `agents/max-assembly.md` |
| orchestration, hand-off and the live-gate discipline | **`agents/max-orchestrator.md`** |

---

## 5. Hand-off: materialising the model by hand

This is the deliverable. The user applies materials, layers and render settings themselves. **Short version — full detail in `agents/max-orchestrator.md` §5.**

### 5.1 The 29 `PROTO_` nodes are the component references — **not** family-wide material handles

`fileIn examples/assembly.ms` builds **244** nodes: 27 massing, 136 `PLC_` placed panels, 29 `PROTO_` prototypes, 52 `WAL_` wall cells. Each `PLC_` instance **shares its prototype's `baseObject`** — measured 136/136 at P5 and 5/5 at P6 with a corrected negative control.

> ### ⚠️ A material on a prototype does **NOT** reach its instances — measured 2026-10-05
>
> This was the pack's central hand-off claim and it was **wrong**. It is a property of *sharing*, not
> inheritance, and the two are not the same thing:
>
> | Step | Result |
> |---|---|
> | `baseObject` shared | `true` / `true` — confirmed on the built scene and on a fresh 3-node test |
> | material on the **prototype** | **`0` of its 10 instances inherit it**; all read `undefined` |
> | material on each **instance** | **10 of 10** set — per-node, independent |
> | material on the instance, then read the **prototype** | prototype keeps its own — **no back-propagation either** |
> | `node.baseObject.material = m` | **THREW** `Unknown property: "material" in Box` — the base object has no material slot |
> | control: the other 28 prototypes | **0** leaked the material, so the probe discriminates |
>
> **What this means for the hand-off:** the material pass is **29 prototypes + 136 instances, i.e.
> per-node work in the Material Editor** — or, far better, **one MultiMaterial on a prototype's
> instances is not the mechanism here at all.** The practical route is a MultiMaterial applied to the
> whole `PLC_` set, or assigning per instance. Note that **a node's sub-material index is not
> reachable from MAXScript** (§5.4), so selecting which slot a panel uses is a UI action.
>
> **The reusable lesson:** *shared `baseObject` is a memory optimisation, not an inheritance
> mechanism.* Never infer "change it once on the prototype" from "they share geometry".

### 5.2 Zero modifiers in the scene is deliberate, not a bug

Measured `0`. It is `G-81`, and it exists because of a measurement rather than a preference: the Boolean modifier attaches and **silently cuts nothing** in this build, so P6 rebuilt wall openings as solid cells. It also retires the 20-modifier freeze hazard by construction instead of by chunking. If you find modifiers on these nodes, something is wrong with the run, not with the model.

### 5.3 Layer assignment is a manual step

`assembly.json.layer_map` is a **record of intent**, linted against a closed eight-name vocabulary, and it is **never applied by a builder** — no route exists (§2, last row). The user applies it in the Layer dialog. Node naming is id-based (`EL-001` → `EL_001`, `WAL-EL-014-C01` → `WAL_EL_014_C01`), which is what makes that mapping mechanical. Rule `N2`: names are unique across the whole scene, not per layer.

### 5.4 Corona must be set explicitly — and needs an instance

```maxscript
local c = Corona()          -- construct an INSTANCE
renderers.production = c    -- OK
renderers.current    = c    -- OK
```

- `renderers.current = Corona` **throws** `Unable to convert: Corona to type: Renderer`. The bridge's own read at `capabilities.py:15` uses `classOf renderers.current`, which returns a `Name` and looks assignable. It is not.
- `renderers.current` and `renderers.production` are **independent slots**. Both read `Arnold` in this installation out of the box.
- `Corona()` costs **~3.5 s cold, ~0.4 s warm** — it initialises the renderer on construction. **Call it in its own `execute_maxscript` call** or the first call reads as a timeout.
- The architectural material class is **`_CoronaPhysicalMtl`**, 171 properties, camelCase, with slot groups `<slot>` / `<slot>Texmap` / `<slot>TexmapOn` / `<slot>MapAmount`. A bogus property name **throws** on both read and write, so a typo fails loudly rather than silently.
- `materials` is `undefined` in this build — there is no global material collection to enumerate, the same family as `layers`. `RendererClass.classes` and `Material.classes` are the working substitutes; `Material.classes.count` = 77.
- **Node sub-material IDs are not reachable from MAXScript** (four spellings, both a primitive and a modifier-class object, all throw, with a control). Whole-material assignment only.

---

## 6. What to do first

### 6.1 Read, in this order

1. **`CHECKPOINT.md`** — the status board, every verified fact, the open-bugs table and the incident log of false conclusions. Do not re-derive anything in it.
2. **`agents/max-orchestrator.md`** — how to drive the stages, run the live gate, and hand the model over.
3. The stage contract for whatever you are about to do (§4.1).

### 6.2 The only commands that exist

There is no build system, no test runner, no linter and no CI. These are the entire executable surface:

```bash
python scripts/env_preflight.py                          # emit MAXScript probes, all checks SKIP
python scripts/env_preflight.py --results results.json    # score captured results; exit 1 on any FAIL
python scripts/env_preflight.py --json                    # machine-readable report
python scripts/install_skill.py                          # build .skill + install to ~/.claude, ~/.agents
python scripts/init_project.py --project X --dir D       # scaffold a workdir, 11 spec files + project.json
python scripts/validate_specs.py --dir examples          # lint every spec against G-1..G-83
python scripts/build_spec.py --stage massing --in examples --out examples   # emits massing.json + massing.ms
python scripts/build_nurbs.py --in examples --out examples                 # emits nurbs.json + nurbs.ms
python scripts/facade_tables.py --in examples --out examples              # emits both P5 JSONs + both CSVs
python scripts/place_components.py --in examples --out examples           # emits assembly.json + assembly.ms
python -m py_compile scripts/*.py                        # the only "test" that exists
```

Three constraints on that list:

- **`build_spec.py` accepts `--stage massing` only** and exits non-zero for anything else.
- **`place_components.py` reads four inputs** — `components_registry.json`, `world_table.csv`, `massing.json`, `dimensions.json` — all of which must be `locked` unless `--allow-draft`. Copying only what `build_spec.py` writes makes it refuse with *"dimensions.json is missing … a builder never invents an input"*. That refusal is correct.
- **An emitted `.ms` is not done until it has been `fileIn`-ed and measured**, and an emitted **CSV** is not done until it has been placed in Max and counted. Self-checks prove a file is well-formed and prove nothing about whether MAXScript will load it.

### 6.3 Named in `PLAN.md` but NOT written — never reference these as if they run

`qa_check.py` · `capture_views.py` · `export_max.py` · `lint_script.py` · `check_skill_md.py` · any `materials`-building script. `materials.json` and `qa.json` are reserved spec files and are **absent**, so `G-1` SKIPs on them.

### 6.4 Verifying a stage without the QA loop

There is no automated QA stage, so verification is per-stage and manual. This is the loop that replaces it:

1. **Preflight.** Run `env_preflight.py` bare. It **prints** the MAXScript probe bodies; paste each into `execute_maxscript`, collect the returned strings, write a JSON file mapping check name → captured output, then re-run with `--results`. A bare invocation exits 0 with everything SKIP — that is not a pass, it is a non-run. It is two-phase by design and cannot talk to Max itself.
2. **Run the emitted script and count.** `fileIn examples/massing.ms`, `examples/nurbs.ms`, `examples/assembly.ms`. Every builder is `fn`-wrapped and idempotent — invoke it three times and confirm the node count and every bbox are identical.
3. **Measure against an independent prediction.** Read `node.min` / `node.max` and compare against a prediction recomputed in Python from the spec files. A verdict must require that the expected number of comparisons actually **happened** — one comparison harness in this repo printed `PASS` having made zero, because prediction keys used `EL-014` and node names use `EL_014`.
4. **Instance structure.** `get_hierarchy`, `get_instances`, and `baseObject` equality with a control that is a plain `copy` renamed so it falls **outside** the population being scanned.
5. **Naming and reference hygiene.** `get_dependencies`, `walk_references`, `get_wired_params`, `list_wireable_params`.
6. **Scatter determinism.** Snapshot with `saveConfiguration(filePath, reserved)`, restore with `loadConfiguration(filePath)`, read `getInstanceCount()` before and after. If the counts differ, the seed is not applied.
7. **Visual confirmation.** `capture_multi_view` for an overview sheet, `capture_viewport` for one framed view, `isolate_and_capture_selected` for a single element. Eye-level perspective at `165–180 cm` plus a three-quarter bird's-eye.
8. **Clean up in the same call that created the objects.** `for o in objects do delete o` **silently skips entries** — collect the names first, then delete by name, and run it twice, because deleting a base does not delete its instances.
9. **Render only on request.** `render_scene` produces a real image; do not start one unprompted.

### 6.5 The control rule — it is not optional

Any class- or property-existence claim must carry a **known-bogus control in the same batch**, and a **known-positive** too, because absence and detectability are different things:

```maxscript
for code in #("quat 45.0 [0,0,1]", "matrix3 1 0 0 0 1 0 0 0 1", "1+1", "TotalGarbageXYZ_fn(1)") do
(
    local v = undefined
    local threw = false
    try ( v = execute code ) catch ( threw = true )
    print (code + " => threw=" + (threw as string) + " undef=" + ((v == undefined) as string))
)
```

`1+1` must come back `undef=false` and the bogus name `threw=true`. Two traps make this necessary and both have cost real time:

- **`introspect_class "NURBSSet"` returns `Class not found: NURBSSet` and is wrong** — the class constructs fine. This false negative caused a full plan to be rewritten around a fabricated conclusion. `discover_plugin_classes` (listed 78 of 160 modifiers, with wrong superclass names) and `inspect_plugin_constructor` (`inferred: true` guesses) are equally unreliable.
- **`((execute code) as string)` reports a FALSE ABSENCE for any value that cannot be stringified** — `as string` on a `matrix3` throws, and the throw looks exactly like "the class does not exist". Compare against `undefined`, as above. A uniform result across a heterogeneous name list is a **broken probe**, not a uniform absence.

Corollary, in force since P4b: **do not rewrite an unverified reference on suspicion.** `references/nurbs-complete-guide.md` and `references/nurbs-architecture-recipes.md` were unverified, not disproven — keyword claims vindicated at P4b, geometry claims still unverified, and their absent-tool routing since corrected in place at the close-out (§8). The rule now governs their remaining geometry claims, not their tool tables. Rewriting on suspicion already happened once and was wrong.

---

## 7. `execute_maxscript` Safety and Verified MAXScript Gotchas

### 7.1 Escaping

`code` is JSON-unescaped once before MAXScript parses it. A `BAD_PARAM` parse error with no line number means escaping corruption.

- Always use forward slashes in file paths: `"C:/assets/tex/"`.
- Never put literal `\n` or `\t` inside MAXScript string literals.
- Prefer single-line `;`-separated statements, or a clean `try (...) catch (...)` block. **The brace form `try { } catch { }` is a parse error in this build** — use the parenthesised form.
- `execute "<str>"` does **not** see variables from the enclosing scope. A string form must be fully self-contained.
- **One script per call, under ~2 s.** It runs on Max's main thread, so a long script freezes the UI. `Corona()` (§5.4) is the measured exception and needs its own call.

### 7.2 Function names that do not exist

Measured with a calibrated sweep in which `copy`, `Box`, `filterString`, `openFile`, `readLine`, `findItem`, `matchPattern`, `pi` and `quat` all resolve and `TotalGarbageXYZ_fn` does not.

| You want | Do not write | Write instead |
| :--- | :--- | :--- |
| check a file exists | `fileExists` | `doesFileExist` |
| run a script file | `executeFile`, `runScript` | **`fileIn`** |
| end interactive creation | `stopCreating node` | `stopCreating` — **0 arguments** |
| read a node's modifiers | `modifiers <node>` (function), `getModifier 1 node` | `node.modifiers`, `node.modifiers[1]` |
| a copy-mode instance | `setCopyMode` | `n = copy src` then `n.baseObject = src.baseObject` |
| a Z rotation | `rotationZ` / `rotationX` / `rotationY`, `matrix3`, `angle` | `n.rotation = quat <degrees> [0,0,1]` |
| a substring test | `findString` | `substring s 1 n` |
| Max's version array | `get3dsMaxVersion()`, `getMaxVersion` | `maxVersion()` — an array, major at index 8 |

### 7.3 Gotchas that cost real time

| Trap | Detail |
| :--- | :--- |
| `((execute code) as string)` | `as string` **throws** on any value that cannot be stringified (e.g. a `matrix3`), which reads as a false absence. Compare against `undefined` (§6.5) |
| `"prefix" + numericValue` | Throws a type error and looks exactly like a broken tool. Wrap the number: `(value as string)`. Same trap as `("Section_" + i as string)` |
| The MCP error surface | A **failed** script returns `success: true` with `error: ""` and a `result` beginning `__MCP_MS_ERR__:`. Any probe or caller that checks only `success` sees a pass — check for the prefix |
| `getProperty` needs a **Name** | `getProperty o ("radius" as name)` works; the raw String throws and can kill the enclosing script. This works on **built-in** classes; `o["name"]` bracket access is never valid dynamic access |
| Standalone modifiers | `Sweep()` returns a non-node; `delete` on it fails with `No "delete" function for sweep:Sweep`. Attach the modifier to a node, then delete the node |
| `delete <base>` or `delete <dummy>` | Deletes only that node. **Instances and children survive** and must be deleted by name |
| `introspect_class` | ParamBlock reflection is wrong for shapes: it reports `Rectangle` with `paramBlocks: []`, yet `Rectangle()` does have `width` / `length` (default `25.0`, assignable) |
| `Box` placement | `Box width: length: height: pos:` centres geometry on `pos.x`/`pos.y` and puts its **base at `pos.z`**. True after `copy`, after `baseObject =` and after a rotation. To centre vertically write `pos = [cx, cy, cz − height/2]` |
| Material identifiers | InternalNames, not display names. `OpenPBR`, not `OpenPBRMaterial`. The Corona architectural class is `_CoronaPhysicalMtl` |
| Constructor keywords | Never use `()`: `Box width:100 length:200 height:300`, never `Box() width:100`. `width` is X, `length` is Y, `height` is Z |
| Class-name spellings | `ChamferMod` → **`Chamfer`**, `Symmetry` → **`symmetry`**, `Surface` → **`surface`**, `Conform` is a spacewarp (`ConformSpaceWarp`) and its 0-arg constructor throws; the modifier-class counterpart is `SpaceConform` |
| `Noise` vs `Noisemodifier` | `Noise` is a texture map; `Noisemodifier` is the modifier. `Normalmodifier` is the normal modifier |
| `PhysicalMaterial` vs `Physical` | `PhysicalMaterial` is the material class; `Physical` is the camera class |
| `snapshotAsMesh` | Returns a world-space `TriMesh`: read vertices `in coordsys world` without re-multiplying `node.objectTransform`, then `delete` the temporary TriMesh in memory |
| `units` | `getProperty units #SystemType` **fails** — read `units.SystemType` directly |

### 7.4 The modifier limit — a hard stop, and it cost a reboot

**Never add more than a handful of modifiers to one node in one scripted call.** This is measured, not inferred. A deliberate bounded ladder on a single `Box`:

| rungs on one `Box` | result |
| :--- | :--- |
| 2 · 5 · 10 | clean — every rung `threw=false`, `modifiers.count` tracked the rung, ~30 ms each |
| **20** | **`execute_maxscript` timed out, then `get_scene_snapshot` timed out, then the bridge stopped answering. Max had to be killed and the machine rebooted.** |

Two of the attachable-looking classes (`Extrude`, `Bevel`) throw on `addModifier`, so the ladder used `Shell` `Chamfer` `Lattice` `Edit_Poly` `Uvwmap` `TurboSmooth` `Noisemodifier` `Bend` `Twist` `Taper`. **No ChaosScatter object existed in the scene during the hang**, which *strengthens* rather than weakens the link: the callback fires from the geometry-stack change itself, so Chaos Scatter's presence is not required for the hazard.

**Standing rule:** build stacks incrementally, **≤ 5 modifiers per `execute_maxscript` call**, and treat **> 10 on a single node as forbidden** without asking the user first. **Do not re-run the 20-rung probe** — it has been measured and the answer cost a reboot. The shipped assembly sidesteps the whole hazard by emitting **zero** modifiers.

Also measured and not to be retried: `getCurrentException()` inside a `catch` (it throws itself) · `global fn` and a bare top-level `fn` both fail through `execute_maxscript`, so inline the code · `modPanel.setCommandPanelCurrentMode` (throws) · `modPanel.addModToSelection` (returns OK, adds nothing) · `max zoomext` (parse error).

### 7.5 Bridge transport — the error text names the wrong transport

A `ConnectionError: Could not connect to 3ds Max on 127.0.0.1:8765` does **not** mean the bridge is down. `MaxClient.__init__` calls `discover_instance_pipes()` exactly once and caches the winning name for the process lifetime; a Max restart changes the PID, hence the pipe name, and the client then calls `CreateFileW` on a dead pipe forever. The error names TCP because the TCP branches are where the raise sites are.

- **Standing rule: after any Max restart, expect to restart opencode.** Restarting Max alone is not a fix, and killing the MCP server does not recover it in-session.
- Diagnose with a two-line check rather than a guess: `%LOCALAPPDATA%\3dsmax-mcp\instances\pid-<PID>.json` lists every instance ever seen; `CreateFileW` on each name separates live (`open`) from dead. Stale files are **never** pruned.

---

## 8. Reference Library

Read the relevant file before authoring complex systems or unfamiliar MAXScript.

| File | Status and contents |
| :--- | :--- |
| `agents/max-orchestrator.md` | **Start here.** How to drive the stages, run the per-stage live gate, and the material hand-off (§5 detail). |
| `references/improvement-log.md` | **The format specification for `<project>/IMPROVEMENTS.md`** — the eight required fields, the severity and owner rules, the header, and two worked examples. **The instruction to write one is `agents/max-orchestrator.md` §6.2**, which every stage contract points back to; this file owns only the entry shape. The log is **never scaffolded**, and **most sessions write nothing** — a session with no findings creates no file. |
| `references/07-spec-grammar.md` | **The spec contract.** JSON envelope, cm/deg units, `_cm` suffix rule, the full spec-file inventory, and invariants `G-1`…`G-83` that `scripts/validate_specs.py` implements. Every builder consumes specs, not prose. |
| `references/08-input-rules.md` | Input intake contract: source trust hierarchy, the extraction procedure, units normalisation, the never-infer list, and a worked brief reconstructed into the committed example. |
| `references/09-defaults.md` | Architectural default tables used whenever input is silent. Every use is recorded as an `A-nnn` assumption, never as a fact. **A convention's default is the value to use; a value merely inside its range is an invention.** Includes a do-not-default list. |
| `references/10-conflict-resolution.md` | Precedence ladder `R1`…`R6`, first match wins, plus `R7 DEFAULT-FILL` which fills silence only and is forbidden in a conflict. Defines the conflict record shape. |
| `references/11-layer-standard.md` | The eight-layer vocabulary, node naming (N1–N4), dummy rules, hygiene checklist. **Layer is data** — see §5.3. |
| `references/01-architecture-aec-workflow.md` | S0→S8 stage map, spec chain, build gate, determinism, context budget. Note the stage list here runs ahead of what was built. |
| `references/12-nurbs-gotchas.md` | **The corrected NURBS reference.** Verified class matrix, relational workflow, `evalPos` measurements, the resolved `close`/`NURBSControlVertex` behaviour, and the control-test rule for existence probes. |
| `references/14-chaos-scatter.md` | The verified Chaos Scatter parameter map, the measured modifier-stack hazard, and the determinism hook. Read before building any scatter. |
| `agents/max-input.md` | S1 stage contract: inputs → three locked spec files, completion gate, escalation policy, anti-pattern guards. |
| `agents/max-massing.md` | S2 stage contract: inputs, per-kind Z rules, the live-Max step, completion gate, cleanup, escalation, anti-patterns. |
| `agents/max-nurbs.md` | **The S3 stage contract — the route for every NURBS build, and for the four relational kinds in particular.** Lock gate, procedure, the commit rule, the sub-object-index and `nurbsID` traps, the four dependent kinds with their keys, defaults and **measured** census counts, a 19-row completion gate, cleanup, escalation, 24 anti-patterns. |
| `agents/max-facade.md` | **The S4a stage contract — the route for a panelised facade grid.** Per-bay vertical divisions, why a rotation comes from the run vector and **never** from `facades[].direction_deg`, the "exactly one panel per opening" rule, `axes[].bay_index`, and the live gate that places the emitted table and counts it. 17-row completion gate, 17 anti-patterns. |
| `agents/max-components.md` | **The S4b stage contract — the route for the component registry.** One entry per distinct `(kind, width, height)` class rather than one per panel, the two assumed numbers and why there are only two, the ordered `parameters` list, and the total join a panel must satisfy. 13-row completion gate, 16 anti-patterns. |
| `agents/max-assembly.md` | **The S5 stage contract** — the route for placement, wall tiling and Chaos Scatter. Includes why it emits no modifiers and how the census walks the scene instead of counting its own bookkeeping. |
| `references/02-mcp-live-orchestration.md` | Authoritative routing detail: verified tool inventory, failing tools, introspection-tool failure modes. |
| `references/nurbs-complete-guide.md` | Full NURBS API: `NURBSSet`, `NURBSNode`, `getNURBSSet #relational`, index vs `NURBSId`, knot invariant, curve and surface classes, COS projection and trimming, `NURBSDisplay`. **Vindicated at P4b — do not rewrite on suspicion.** Its absent-tool mentions (`geometry_qa`, `agent_viewport`) were corrected in place at the close-out; nothing in it prescribes a tool missing from the live list. |
| `references/nurbs-architecture-recipes.md` | Wave canopies, Gordon-network facades, UV panelization, diagrid generation, skylight trimming, two-rail helical ramps, G2 blends. **Vindicated at P4b**, except its skylight-trimming recipe, which is superseded: `NURBSProjectVectorCurve` projects and does not cut — `12` §3.25–3.26 and `agents/max-nurbs.md` §6.7.5. **Its tool routing was corrected at the close-out** — the NURBS-vs-spline table is re-pointed off `curve_model` / `draw_spline` / `loft_mesh` / `inspect_curve` / railClone, so the file no longer prescribes an absent tool and is usable as written. The geometry recipes themselves remain unverified, not disproven. |
| `snippets/nurbs_arch_library.ms` | Reusable `MCP_NURBS_Arch` struct. Loads cleanly and prints `MCP_NURBS_Arch loaded`. **12 functions, zero known bugs** — all 12 executed live (§3.2). |
| `references/arch-modifiers-and-procedural-reference.md` | Exact class and parameter names, plus **the corrected route for the six unattachable modifiers** and the real 32-operator Data Channel vocabulary. Its MCG material is obsolete. |
| `references/architecture-exterior-pipelines.md` | Exterior production pipeline: dimensions, layer stack, core and shell, curtain walls, moldings, roofs, terrain, roads. Its Forest Pack, Chaos Cosmos and lighting-tool sections are obsolete — substitute Chaos Scatter. |
| `references/procedural-graphs.md` | **Split, not fenced — the file is half live.** Its **Data Channel half is LIVE**: the six real tools are `list_dc_presets`, `add_data_channel`, `inspect_data_channel`, `add_dc_script_operator`, `load_dc_preset`, `set_data_channel_operator` (the invented `list_dc_operators` / `manage_data_channel_stack` were corrected in place 2026-10-06). Its **Max Creation Graph half is OBSOLETE** — all 12 `mcg_*` tools and `curve_model` do not exist, and there is no substitute. Use `arch-modifiers-and-procedural-reference.md` for the real 32-operator vocabulary. |
| `references/curve-construction.md` | **OBSOLETE, with a router at the top and the original body fenced as non-executable** — the same convention, now applied to `references/railclone.md` and `references/tyflow-graphs.md` (both reworked to match on 2026-10-06, verified to carry a top banner, a "read this instead" pointer and a fenced non-executable body; `procedural-graphs.md` deliberately does **not** follow it, because it is half live). Written against a 178-tool server that is not the one connected: `curve_model`, `inspect_curve`, `edit_curve`, `draw_spline`, `loft_mesh` and `geometry_qa` are **absent**, by direct reading of the live tool list. Kept for reference only. **Read `references/maxscript-splines-shapes.md` instead** — the verified route for every curve and shape operation, executed claim-by-claim at P4b-r. |
| `references/railclone.md` | **OBSOLETE, with a router at the top and the original body fenced as non-executable.** railClone is not installed: `get_railclone_style_graph` exists in the schema and always fails, and `get_railclone_style` / `set_railclone_style` / `get_railclone_output` do not resolve at all. Its opening *"verified in 3ds Max 2027 with RailClone Pro 7.3.5"* claim was wrong twice over — target is 2026.3.2 and the plugin is absent. **No equivalent tool.** Repeated placement = reference instancing, `n = copy src` then `n.baseObject = src.baseObject` (`setCopyMode` does not exist); scattering = `ChaosScatter`. Kept for reference only. |
| `references/tyflow-graphs.md` | **OBSOLETE, with a router at the top and the original body fenced as non-executable.** tyFlow is not installed; all 14 `3dsmax-mcp_tyflow_*` tools always fail, so its agentic loop cannot even start (`get_tyflow_graph` does not exist). **No equivalent tool.** Substitute Chaos Scatter for distribution (`references/14-chaos-scatter.md` §4), PhysX / Max particles for physics, keyframed transforms plus controllers for animated motion. Kept for reference only. |
| `references/maxscript-splines-shapes.md` | Executed claim-by-claim at P4b-r, **largely vindicated**: all 11 shape ctors, all 15 render props, all 27 `splineOps`, all 14 path-interp functions. Ten dated corrections. |
| `references/maxscript-core-syntax.md` · `-common-patterns.md` · `-3dsmax-objects.md` · `-mesh-poly-ops.md` · `-splines-shapes.md` · `-materials-textures.md` · `-rendering-cameras.md` · `-animation-controllers.md` · `-scripted-plugins.md` · `-ui-rollouts.md` | The ten-file MAXScript reference set. Deduped at P4b-r and byte-identical since. `script_controller` guidance was removed — that tool does not exist. |
| `references/_p7-evidence.md` | **P7 probe transcripts, executed live 2026-10-05** — renderer detection and switching, the 16 Corona material classes and 15 that construct, all 171 `_CoronaPhysicalMtl` property names, the material-assignment negative, and what stays UNVERIFIED. P7 was cancelled, not completed. |
| `references/_p6-contract.md` · `_p6-revision-brief.md` | The S5 design contract and the revision that removed the Boolean modifier after it was measured unusable. |
| `references/_p5-contract.md` · `_p4b-remainder-evidence.md` | The S4 design contract, and the executed transcripts behind the P4b-r reference corrections. Read before editing the corrected references again. |
| `references/00-audit-p1.md` | The P1 audit: dedupe measurement, per-file verdicts, and the `curve-construction.md` rewrite brief. |
| `scripts/env_preflight.py` | Environment preflight probe harness, two-phase by design. Emit mode prints probe bodies, `--results FILE` evaluates captured output, exit 1 on any FAIL. Also accepts `bridge` and `plugins_absent` from the typed tools. |
| `scripts/validate_specs.py` | Spec validator implementing `G-1`…`G-83` — envelope and units, traceability and the ledgers, dimensional geometry, massing, NURBS, the facade grid and assembly. Stdlib only, exit 1 on any FAIL. `--dir`, `--file`, `--json`, `--rule`, `--warnings-as-errors`, `--build`, `--allow-draft`. A check that cannot be evaluated reports **SKIP with its reason**, never a silent PASS. |
| `scripts/init_project.py` | Scaffolds a workdir: 11 spec files under `specs/pipeline/`, plus `specs/recipes/`, `snippets/`, `project.json`. `--from examples` seeds a project while preserving every `A-nnn`/`C-nnn` audit id. |
| `scripts/facade_tables.py` | **S4 builder.** `dimensions.json` + `massing.json` → `facade_grids.json` → `components_registry.json` → `facade_table.csv` + `world_table.csv`. Self-checks `G-57`…`G-70` before writing, then reads the CSVs back for `G-70`. Byte-deterministic. `--stage grids\|components\|tables\|all`. |
| `scripts/build_spec.py` | **S2 builder**, `--stage massing` only. `--in --out [--json]`, lock gate, deterministic, emits `massing.json` + `massing.ms`, self-checks `G-34`…`G-40` before writing, refuses non-rectangular profiles by name. |
| `scripts/build_nurbs.py` | **S3 builder**: locked `nurbs.json` → normalised `nurbs.json` + `nurbs.ms`. Self-checks `G-41`…`G-56`. Refuses a literal sub-object index or a synthetic `nurbsID` — the latter is a process crash, not an error. |
| `scripts/place_components.py` | **S5 builder**, the project's last builder: `--in --out [--stage assembly] [--json] [--build] [--allow-draft]`. Reads four locked inputs, emits `assembly.json` + `assembly.ms`, self-checks `G-71`…`G-83` against the bytes on disk, and **emits no modifiers**. |
| `scripts/install_skill.py` | Builds the `.skill` archive and installs to `~/.claude/skills/` and `~/.agents/skills/`. `collect_files()` now ships `SKILL.md`, `PLAN.md`, `CHECKPOINT.md`, `AGENTS.md` plus `references/` (all), `snippets/` (all), `scripts/*.py`, `agents/*.md`, `specs/*.json` and `examples/*.{json,ms,csv}` — so `env_preflight.py` and the whole pipeline **are** in an installed copy. Verified at P4b-r at **53 files**, all previously-missing paths present, deterministic, no `__pycache__`/`.pyc`/`.skill`. Not re-verified since; later stages added files. **The checked-in `3dsmax-arch-nurbs-ultimate.skill` archive is stale** — it predates P2–P6. Rebuild with `python scripts/install_skill.py` before trusting it. |