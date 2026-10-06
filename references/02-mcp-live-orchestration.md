# 02 — MCP Live Orchestration: VERIFIED Tool Inventory and Routing Rules

> **Purpose:** The authoritative routing table for this skill. An agent must be able to read this
> file and know exactly which MCP tool to call for a task — and, just as importantly, which tool
> NOT to call, and which tool is lying to it.
>
> **Every fact in this file was verified empirically against a live 3ds Max 2026 session through the
> `3dsmax-mcp` bridge.** Where a claim could not be verified, it is marked UNVERIFIED and must be
> probed at runtime, never assumed.
>
> **Standing rule of this file: MAXScript execution is the only ground truth about what exists.**
> Enumeration and introspection tools are hints. Section 6 explains why this file exists.

---

## 1. Bridge status (verified)

| Field | Verified value |
| :--- | :--- |
| Application | 3ds Max 2026.3.2 (Security Fix) |
| Transport | `namedpipe` |
| Protocol version | `2` |
| `safeMode` | `true` |
| `threadMode` | `mainThread` |
| Round-trip time | ~2.5 ms |
| Scene at verification | 0 objects, unsaved file |

Version read: `maxVersion()` returns an **array**; the major version is at **index 8**.
`get3dsMaxVersion()` and `getMaxVersion` do not exist (see section 8).

### 1.1 There is no TCP listener. Do not start one.

The legacy TCP MAXScript listener on `127.0.0.1:8765` is **NOT used and NOT required**.
`requestedTransport: "auto"` successfully negotiates `namedpipe` against the per-instance pipe the
native GUP bridge registers for the running Max process.

**Never instruct an agent (or a human) to start a MAXScript TCP listener before calling MCP tools.**
It is a no-op for correctness and adds a failure mode. If a call fails with
`ConnectionError ... 127.0.0.1:8765`, the problem is almost certainly a stale cached client module
or a restarted Max with a new PID — not a missing listener. The instance-pipe discovery path handles
the new PID; the fix for a stale cache is to restart the `3dsmax-mcp` MCP server.

### 1.2 Main-thread execution

`threadMode: mainThread` means every MAXScript evaluation runs on Max's main thread. Long scripts
block the UI and freeze the viewport. See routing rule 3.

---

## 2. Capability probe results (verified)

### 2.1 Renderers

`Default_Scanline_Renderer`, `VUE_File_Renderer`, `Quicksilver_Hardware_Renderer`,
`A360_Cloud_Rendering`, `Corona`, `ART_Renderer`, `Arnold`, `Missing_Renderer`.

Active renderer reported as `Arnold`. **The user's production renderer is Corona** — Corona is
present and constructible, so render targets that assume Corona or a path tracer will work.

Note the presence of `Missing_Renderer` in the enumeration — that entry is a plugin stub, not an
installable renderer. Do not select it.

### 2.2 Plugin availability

| Plugin | Available |
| :--- | :--- |
| forestPack | **false** |
| forestLite | **false** |
| tyFlow | **false** |
| railClone | **false** |
| phoenixFD | **false** |

Present/absent confirmed via `get_plugin_capabilities`. This single fact drives the HARD RULE below.

### 2.3 Registered class counts

| Superclass | Count |
| :--- | :--- |
| material | 77 |
| geometry | 136 |
| modifier | 160 |

These counts are **enumeration output**, not a usability list — see section 6.2.

### 2.4 Third-party classes observed present

- **Corona** — Corona materials plus `CoronaPatternMod`, `CoronaHairMod`, `CoronaFumeFXMod`,
  `CoronaDisplacementMod`, `CoronaCameraMod`.
- **Chaos** — `ChaosScatter`, `CScatter`, `CFractal`, `CDecal`, `CVolumeGrid`, `CProxy`,
  `CGaussianSplats`. `ChaosScatter()` constructs; `CScatter` is its **NotCreatable** base class —
  always construct `ChaosScatter`.
- **FbxMaxWrapper**.
- **USD** — Stage, `USDGeomObject`.
- **PhysX** — `PhysXShapeConvex`, MassFX `RBody`, `clothfx`, `mCloth`.
- **HSDS**.
- **OpenSubdiv**.

Chaos and PhysX being present is why they are the sanctioned substitutes for the absent plugins.

### 2.5 Materials constructible (verified by construction, not enumeration)

`OpenPBR` (class `OpenPBR_Material`), `PhysicalMaterial`, `Standard`, plus 16 Corona classes:
`CoronaPhysicalMtl`, `CoronaMtl` / `CoronaLegacyMtl`, `CoronaLayeredMtl`, `CoronaHairMtl`,
`CoronaFabricMtl`, `CoronaSkinMtl`, `CoronaToonMtl`, `CoronaVolumeMtl`, `CoronaPortalMtl`,
`CoronaShadowCatcherMtl`, `CoronaRaySwitchMtl`, `CoronaOutlineMtl`, `CoronaSlicerMtl`,
`CoronaScannedMtl`, `CoronaSelectMtl`, `CoronaLightMtl`.

**NOT available:** Arnold-specific materials, `VRayMtl`, Octane materials
(`octane_standard` / `octane_pbr` / `octane_universal`), `RS_Standard_Material`, `MaterialX`.
Note how these are named in the schemas of `assign_material` and `create_material_from_textures` —
the schemas advertise classes that are not installed. See section 6.1.

---

## 3. HARD RULE — tools that ALWAYS fail in this environment

Because ForestPack / tyFlow / RailClone / PhoenixFD are absent, every MCP tool in these groups
throws. **Agents must not call them, and must not fall back to "try it anyway."** There are
**15** such tools.

### 3.1 Forest Pack

- `scatter_forest_pack`

**Substitution:** Chaos Scatter (`ChaosScatter` geometry object, present per section 2.4) via
`execute_maxscript`, or Forest-free instancing via `clone_objects` with `mode: "instance"`, or
XRef for very large repeats. `ChaosScatter` is deterministic via `seed` (int 1..31337) and exposes
an FpInterface readback (`getInstanceCount()`, `getModelCount()`, `convertInstancesToGeometry(time)`,
`saveConfiguration` / `loadConfiguration`) — prefer it over guess-and-check.

### 3.2 tyFlow (all — 14 tools)

- `create_tyflow`
- `create_tyflow_preset`
- `add_tyflow_event`
- `add_tyflow_collision`
- `connect_tyflow_events`
- `modify_tyflow_operator`
- `remove_tyflow_element`
- `get_tyflow_info`
- `get_tyflow_particles`
- `get_tyflow_particle_count`
- `reset_tyflow_simulation`
- `set_tyflow_physx`
- `set_tyflow_shape`
- `list_tyflow_operator_types`

**Substitution:** PhysX (`PhysXShapeConvex`, MassFX `RBody`, `clothfx`, `mCloth` — all present) for
rigid-body and cloth, Chaos Scatter for distribution, and Max **standard particle systems** (legacy
emitter geometry objects `Spray` and `Snow`) for emitters. Note that `spray` / `snow` in that
inventory are legacy particle **emitters**, not tyFlow.

### 3.3 RailClone

- `get_railclone_style_graph`

**Substitution:** MAXScript arrays describing base + segment runs, material ID maps, and random
seed, then instantiate with `clone_objects` using `mode: "instance"` (instances keep memory flat
and preserve editability). Keep the array-driven layout in a spec file so it stays parametric
without RailClone.

### 3.4 PhoenixFD

There is no dedicated MCP tool surface for PhoenixFD in this skill. Any PhoenixFD intent must be
rejected and reported, not approximated.

### 3.5 Enforcement

Before reaching for a procedural/scatter/particle capability, check it against section 3. If it is
not listed in section 4's routing table and not in 3, it does not exist. Do not invent tool names —
the pre-existing skill shipped roughly 35 hallucinated tool names, and that is exactly the failure
mode this file exists to prevent. **Invented class names are equally fatal** — see section 6.

---

## 4. Verified working tool routing table

Only the tools below are confirmed callable in this environment.

### 4.1 Scene query

| Intent | Tools |
| :--- | :--- |
| One-shot situational overview | `get_session_context` |
| Counts by class, materials summary, roots | `get_scene_snapshot` |
| Paginated object listing with filters | `get_scene_info` |
| Current selection, full detail | `get_selection` |
| Current selection, compact | `get_selection_snapshot` |
| What changed since last snapshot | `get_scene_delta` |

**WARNING — several of these names belong to the Rhino server, not to 3ds Max.** `get_document_summary`
is a **Rhino** MCP tool and does not exist on `3dsmax-mcp`. Read section 5 before calling any tool
whose name you have not seen in this table.

### 4.2 Object creation

| Intent | Tools |
| :--- | :--- |
| Primitives | `create_object` — Box, Sphere, Cylinder, Cone, Torus, Teapot, GeoSphere, ChamferBox, ChamferCyl, Gengon, Prism, Pyramid, C-Ext, L-Ext, Capsule, OilTank, Spindle, Hedra, Tube, Spring, Damper, Hose, Plane, and others in the geometry inventory |
| Grid-based 2D floor plan from room definitions | `build_floor_plan` |
| Anything curved / NURBS | `execute_maxscript` — see `12-nurbs-gotchas.md` |

On `3dsmax-mcp`, `create_object` creates a **primitive** and takes no NURBS parameters. The Rhino
server exposes a different `create_object` with a type-specific `params` dict — calling the wrong one
produces a validation error, not a helpful message.

### 4.3 Object editing

| Intent | Tools |
| :--- | :--- |
| Move / rotate / scale | `transform_object` |
| Copy, instance, or reference | `clone_objects` |
| Delete | `delete_objects` |
| Set an object property | `set_object_property` |
| Rename many objects at once | `batch_rename_objects` |

There is no `modify_object` tool on this server. `set_object_property` is the property-write path;
it takes `name`, `property`, `value`.

### 4.4 Selection and visibility

| Intent | Tools |
| :--- | :--- |
| Select by names, pattern, class, or all | `select_objects` |
| Show / hide / freeze / unfreeze | `set_visibility` |

### 4.5 Organization

| Intent | Tools |
| :--- | :--- |
| Layers: create, delete, list — **that is the entire vocabulary** | `manage_layers` |
| Groups: create, ungroup, open, close, attach, detach | `manage_groups` |
| Named selection sets | `manage_selection_sets` |
| Parenting | `set_parent` |

> **CORRECTED (verified 2026-10-06):** the `manage_layers` row previously read *"create, delete, list,
> **set properties, move objects**"*. The two extras **do not work**: 40+ candidate action names were
> rejected with a uniform `Unknown layer action`, and the real vocabulary is exactly
> `{list, create, delete}`. `manage_layers` **cannot assign an object to a layer**, and neither can
> `set_object_property` — `node.layer` is read-only from MAXScript and **nine** assignment routes are
> ruled out in total. **Layer is data and the user applies it in the Layer dialog, permanently.**
> `SKILL.md` §1.4 (~line 113) and §2 (~line 152) already state the correct three actions and the
> negative; this row now agrees with them.

### 4.6 Modifiers

| Intent | Tools |
| :--- | :--- |
| Add | `add_modifier` |
| Remove by name | `remove_modifier` |
| Collapse stack | `collapse_modifier_stack` |
| Enable/disable in viewport/render | `set_modifier_state` |
| Read all properties of one modifier | `inspect_modifier_properties` |
| Deep-read object / modifier / base object / material | `inspect_properties` |
| Batch-set one property across many objects | `batch_modify` |
| Break a shared modifier into a unique copy | `make_modifier_unique` |
| Data Channel: inspect operator graph | `inspect_data_channel` |
| Data Channel: set operator properties | `set_data_channel_operator` |
| Data Channel: create with a full operator graph | `add_data_channel` |
| Data Channel: create with a MAXScript operator | `add_dc_script_operator` |
| Data Channel: list presets | `list_dc_presets` |
| Data Channel: load a preset onto an object | `load_dc_preset` |

There is no `set_modifier_property` tool. `add_modifier` takes a `params` string; for post-hoc edits
use `inspect_modifier_properties` to learn real parameter names, then `execute_maxscript` to write
them, or `batch_modify` for a single uniform property across many objects.

### 4.7 Materials and textures

| Intent | Tools |
| :--- | :--- |
| Create a material and assign it | `assign_material` |
| List materials in use | `get_materials` |
| Compact slot / property readback | `get_material_slots` |
| Set one material property | `set_material_property` |
| Set several at once | `set_material_properties` |
| Fill a Multi/Sub-Object slot | `set_sub_material` |
| Swap one material for another across the scene | `replace_material` |
| Swap several at once | `batch_replace_materials` |
| Build a wired PBR set from a texture folder | `create_material_from_textures` |
| Shell Material with Arnold + glTF slots | `create_shell_material` |
| Lay textures into Compact Material Editor slots | `palette_laydown` |
| Read a material / texture / modifier API surface | `introspect_osl` |
| Write an OSL shader and create an OSLMap | `write_osl_shader` |
| Create a texture map as a global variable | `create_texture_map` |
| Set properties on such a map | `set_texture_map_properties` |

`create_material_from_textures` and `palette_laydown` advertise Octane, VRay and `RS_Standard_Material`
class names in their schemas. **Those are not installed** (section 2.5). Pass only
`OpenPBR` / `PhysicalMaterial` / a Corona class, and always verify the result with `get_materials`.

### 4.8 Verification and introspection — HINTS, NOT TRUTH

These tools are useful for orientation and for reading *values off a live instance*. **They are
unreliable as evidence that a class exists or is constructible.** Section 6 documents the specific
failures. Read section 6 before quoting any of them as fact.

| Intent | Tools | Trust for existence claims |
| :--- | :--- | :--- |
| Complete API surface of a class (C++ SDK) | `introspect_class` | **NO** — see 6.1, 6.4 |
| Complete API surface of a live instance, with values | `introspect_instance` | no |
| Scan the DLL directory for registered classes | `discover_plugin_classes` | **NO** — incomplete, see 6.3 |
| Summarize a plugin's likely entry points | `discover_plugin_surface` | no |
| List classes by plugin name or superclass | `list_plugin_classes` | **NO** — same scan |
| Reflect one class via runtime scan + `showClass` | `inspect_plugin_class` | **NO** |
| Guessed creation notes | `inspect_plugin_constructor` | **NO** — `inferred: true`, see 6.2 |
| Plugin-aware readback of a live instance | `inspect_plugin_instance` | no |
| Version / renderers / plugins / class counts | `get_plugin_capabilities` | plugin/renderer presence: yes; class lists: no |
| Map which classes can reference which types | `map_class_relationships` | no |
| All scene instances of a class | `find_class_instances` | yes (scene-scoped) |
| Find objects by property, optionally by value | `find_objects_by_property` | yes (scene-scoped) |
| Sub-anim discovery for wiring | `introspect_track_view` | no |
| Track View tree of one object | `inspect_track_view` | no |
| Enumerate wireable parameters | `list_wireable_params` | no |
| Read existing wire connections | `get_wired_params` | yes (reads real scene state) |
| Create a wire with an expression | `wire_params` | yes |
| Remove a wire | `unwire_params` | yes |
| Reference graph, one direction | `get_dependencies` | yes |
| Full reference dependency walk | `walk_references` | yes |
| All instances sharing a base object | `get_instances` | yes |
| Recursive children | `get_hierarchy` | yes |
| Orientation, pivots, bboxes, local axes | `analyze_node_orientation` | yes |

`introspect_track_view` and `inspect_track_view` are two distinct tools with overlapping names.
Read carefully which one you are calling.

### 4.9 Animation and scene state

| Intent | Tools |
| :--- | :--- |
| Create/assign a controller on a sub-anim track | `assign_controller` |
| Add a controller variable or constraint target | `add_controller_target` |
| Change controller script or properties | `set_controller_props` |
| Read the controller on a track | `inspect_controller` |
| All State Sets with camera assignments | `get_state_sets` |
| Camera-assigned State Sets only | `get_camera_sequence` |
| Atmospheric and render effects | `get_effects` |
| Enable/disable an effect | `toggle_effect` |
| Delete an effect | `delete_effect` |

### 4.10 Capture and render

| Intent | Tools |
| :--- | :--- |
| Capture the current viewport | `capture_viewport` |
| Full-screen capture (only when explicitly enabled) | `capture_screen` |
| Multiple viewport angles stitched into one labeled grid | `capture_multi_view` |
| Isolated per-object captures of the selection | `isolate_and_capture_selected` |
| Render the scene | `render_scene` |

Capture before claiming success. A tool returning without error is not evidence the geometry is
correct.

### 4.11 Files

| Intent | Tools |
| :--- | :--- |
| Inspect an external .max without opening it | `inspect_max_file` |
| Read metadata from several .max files at once | `batch_file_info` |
| Merge objects from an external .max | `merge_from_file` |
| Search .max files for objects matching a pattern | `search_max_files` |

### 4.12 Escape hatch — REQUIRED for all NURBS work

| Intent | Tool |
| :--- | :--- |
| Anything not covered above | `execute_maxscript` |

NURBS in 3ds Max has **no typed MCP surface**. Every surface construction, every spline and shape
edit, and every read of undocumented class state goes through `execute_maxscript`. Read
`12-nurbs-gotchas.md` before writing any of it — the constraints there are severe and
non-obvious.

The entire NURBS API is real and verified working: `NURBSSet`, `NURBSCVCurve`, `NURBSPointCurve`,
`NURBSPointSurface`, `NURBSCVSurface`, `NURBSULoftSurface`, `NURBSUVLoftSurface`,
`NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface`, `NURBSOffsetSurface`,
`NURBSProjectVectorCurve`, `NURBSDisplay`, `NURBSSurfaceApproximation` — all resolve AND
construct. `NURBSNode nset` is the surface node. **CORRECTED (verified 2026-10-06):** this sentence previously
read *"`NURBSNode nset` is the surface node (`Point_Surf` / `CV_Surf` are valid identifiers)"*, which
wrongly implied `CV_Surf` / `Point_Surf` are node classes. They are **not** — `CV_Surf` does not even
construct, and neither is ever a node's `classOf`. A NURBS node's `classOf` is **`NURBSSurf`** (any
surface present) or **`NURBSCurveshape`** (curves only); both have `superClassOf` = `GeometryClass`.
`Point_Surf` and `CV_Curve` do exist as *construction identifiers* for sub-object classes, which is
what made the original phrasing read wrong. Measured: 5-rib `NURBSULoftSurface` → `NURBSSurf`;
`NURBSPointSurface`-only → `NURBSSurf`; `NURBSPointCurve`-only → `NURBSCurveshape`; `convertToNURBSCurve`
of a `Rectangle` → `NURBSCurveshape`.
**Do not report the NURBS API as unavailable.** That false conclusion was reached once already by
trusting `introspect_class` and it propagated into four documents.

---

## 5. Tool-name confusion hazard — Rhino-side names on a 3ds Max bridge

A second MCP server (**RhinoMCP**) is connected in the same session. Its tool names overlap
badly with 3ds Max ones. Calling a Rhino tool against 3ds Max returns a confusing error — a schema
complaint, a "not found", or an unrelated result — and an agent that does not check the server
prefix will frequently conclude **the 3ds Max bridge is broken**. It is not. The bridge is fine;
the tool belongs to the other server.

**Rule: all 3ds Max work goes through `3dsmax-mcp_*`. If a tool name is not in section 4, it is not
a 3ds Max tool.**

Full list of Rhino-side names present in the connected toolset — do not call these for Max tasks:

- `get_document_summary`
- `get_objects`
- `get_object_info`, `get_object_attributes`, `get_selected_objects_info`
- `create_object` — **same name as the 3ds Max tool, different schema**: the Rhino one takes a
  type-specific `params` dict and supports NURBS/SURFACE types; the Max one creates primitives with
  flat `pos` / `radius` / `height` arguments
- `create_objects`, `create_layer`, `create_planar_region`
- `analyze_objects`
- `section_profile`
- `boolean_union`, `boolean_difference`, `boolean_intersection`
- `measure_objects`
- `intersect_curves`
- `loft`, `pipe`, `sweep1`, `extrude_curve`
- `offset_curve`, `split_curve`, `project_curve`
- `capture_viewport` — **same name as the 3ds Max tool**; the Max one is `3dsmax-mcp_capture_viewport`
- `undo`, `redo`, `select_objects`, `modify_object`, `modify_objects`, `run_command`
- the entire `gh_*` family (`gh_build_graph`, `gh_add_component`, `gh_mutate_graph`,
  `gh_get_canvas_state`, `gh_capture_preview`, ...) — these drive **Grasshopper**, not Max

Note the two true name collisions on this bridge: **`create_object`** and **`capture_viewport`**.
Both servers export both names. Always qualify which server you are calling.

For Max lofting, sweeping and extrusion, use `execute_maxscript` (NURBS classes such as
`NURBSULoftSurface`) or the typed Max tools in 4.3/4.6 — never the `rhinomcp_*` equivalents.

> **CORRECTED (verified 2026-10-06): the Boolean half of this sentence was removed.** It previously read
> *"For Max lofting, sweeping, extrusion and **booleans**, use `execute_maxscript`"* and named no working
> route. **There is none in this build.** The `Boolean` modifier attaches and is useless; openings are made by
> **tiling the wall with solid cells** — decompose along the run axis at every opening's `u` boundary, then at
> the `v` boundaries covering each column, producing `wall_cells[]`. See `SKILL.md` §2 and
> `references/07-spec-grammar.md` §8.5.8.

---

## 6. Class-name and existence-check pitfalls — the strongest rule in this skill

A previous stage of this skill concluded that the 3ds Max NURBS API was fictional and wrote four
documents on that basis. **That conclusion was wrong and it was caused entirely by trusting the
introspection tools.** Everything in this section exists to make that failure impossible to repeat.

### 6.1 `introspect_class` "Class not found" is FALSE — the class can exist and construct

Verified counterexample:

- `introspect_class "NURBSSet"` returns **`Class not found: NURBSSet`**.
- `execute_maxscript` with `NURBSSet()` returns **`CREATED:NURBSSet`**.

The class exists, it constructs, it works. `introspect_class` simply did not resolve it through the
C++ SDK reflection path it uses. **Never use this tool alone — or with any other introspection tool
— to claim a class is absent.** At most it tells you the class is not *reflected*.

It also lies about parameters: `introspect_class "Rectangle"` reports `paramBlocks: []`, yet
`Rectangle()` really has `width` / `length` (default `25.0`, assignable). Reflection failure, not a
missing feature.

### 6.2 `inspect_plugin_constructor` output is a hypothesis, never a fact

It returns `inferred: true` alongside **guessed** `category` and `creatable` fields. This is
precisely how the `Loft` trap was set: `Loft` resolves as a class, so enumeration suggests it is
creatable, but `Loft()` throws **`Not creatable: Loft`**. The correct lofting class is
`NURBSULoftSurface`. A guessed `creatable: true` will lead you straight into that throw.

### 6.3 The DLL class scan is incomplete and inconsistent with MAXScript

The bridge's DLL enumeration listed **78 of 160 modifiers** — under half — and it omitted classes
that MAXScript can instantiate without difficulty. `discover_plugin_classes superclass=NURBS` returns
**0** because the superclass name is simply wrong; `NURBS` is not the right token. Neither the count
nor the zero is meaningful.

**Therefore: MAXScript execution is ground truth; enumeration is only a hint.** Treat
`discover_plugin_classes`, `list_plugin_classes`, `discover_plugin_surface`, `map_class_relationships`
and `get_plugin_capabilities` class lists as a **candidate list to confirm**, never as an inventory.
A class missing from every list in this section may still be fully usable.

### 6.4 `NURBSObject` is the ROOT class of the whole MAXScript hierarchy

`classOf undefined` returns `UndefinedClass`. But **`NURBSObject` is the root class of the entire
MAXScript hierarchy** — every MAXScript value descends from it. So seeing `NURBSObject` in a
`classOf` result, or in a `superClassOf` walk, does **NOT** mean you found a NURBS surface API.

What you want is a NURBS surface node, and the classes that actually mean a NURBS surface exist:
`classOf` of a node built from a NURBS set is **`NURBSSurf`**, and sub-objects report
`superClassOf` values of `NURBSSurface`, `NURBSCurve`, `NURBSPoint`. Those are the signals to look
for. `NURBSObject` on its own is a hierarchy artefact and carries no information.

Corollary: **a hierarchy walk that terminates at `NURBSObject` proves nothing about feature
availability.** Do not use it as evidence in either direction.

### 6.5 Material identifiers are internalNames, not display names

Use the internalName, never the class as shown in the Material Editor:

| Display name in the UI | Correct MAXScript / tool identifier |
| :--- | :--- |
| Corona Physical Material | `CoronaPhysicalMtl` |
| Physical Material | `PhysicalMaterial` |
| OpenPBR Material | **`OpenPBR`**, not `OpenPBRMaterial` |
| Standard Material | `Standard` |

`OpenPBRMaterial` does not exist. `OpenPBR` constructs an instance whose `classOf` is
`OpenPBR_Material` — the constructor name and the runtime class name differ. Expect this pattern.

### 6.6 The rule

**Only a successful MAXScript construction proves a class is usable.** Not enumeration, not
`introspect_class`, not `inspect_plugin_constructor`, not documentation, not this file. If a claim
in any document — including this one — is about class availability and has no construction behind
it, verify it with section 7 before acting on it.

---

## 7. How to verify a class exists

**Before anything else: every existence probe MUST include a known-bogus control in the same batch.**
Without it, a batch that returns `undefined` for everything is indistinguishable from a broken
bridge, a failed script, or a scope problem. `TotalGarbageXYZ123` correctly yields `undefined`; its
presence proves the probe actually executed.

Procedure:

1. **Resolve** the name with `execute "<name>"` — a bare `execute "NURBSSet"` tells you the name
   resolves; `execute "NURBSSet()"` goes further and constructs.
2. **Construct** it. A constructible class returns a live value; `classOf` of it tells you the real
   runtime class, which may differ from the constructor name (see 6.5).
3. **Include `TotalGarbageXYZ123`** as a control in the same `execute` batch and confirm it returns
   `undefined`. If the control returns something, your batch is wrong, not the class.
4. **Distinguish "not creatable" from "missing".** `Not creatable: Loft` means the class resolves
   but refuses construction — find the creatable sibling instead of declaring the API absent.
5. **Clean up.** Delete every probe object. Do not leave test nodes in the scene.

Reusable snippet:

```maxscript
(
  -- Always includes the bogus control. Always deletes what it builds.
  local names  = #("NURBSSet", "NURBSULoftSurface", "TotalGarbageXYZ123")
  local report = ""
  for n in names do (
    local res = undefined
    local verdict = "MISSING"
    try (
      res = execute (n + "()")          -- execute() does NOT see enclosing scope: string must be self-contained
      if res == undefined then verdict = "MISSING (resolved to undefined)"
      else (
        verdict = "CREATED:" + (classOf res) as string
        try ( delete res ) catch()      -- probe objects must not survive
      )
    ) catch ( verdict = (getCurrentException() as string) )
    report += n + " -> " + verdict + "\n"
  )
  report
)
```

`execute "<str>"` does **not** see variables from the enclosing scope — the string must be
self-contained. Passing `n + "()"` satisfies this because only the literal class name ends up inside
the string. Anything else (a variable, a path, a loop index) will silently see `undefined`.

If the control row is missing from the output, the probe did not run. Fix the probe; never interpret
the result.

---

## 8. MAXScript file / existence function gotchas (cross-reference)

These are the ones that cost the most time. They are listed here because they are environment- and
bridge-level, not NURBS-specific. **Full set with worked examples: `references/12-nurbs-gotchas.md`.**

| You will write | Does not exist — use | Detail |
| :--- | :--- | :--- |
| `fileExists p` | **`doesFileExist p`** | `fileExists` is not a function. |
| `executeFile p`, `runScript p` | **`fileIn p`** | Both alternatives are nonexistent; `fileIn` is the only way to run a script file. |
| `stopCreating node` | **`stopCreating`** | Takes **zero** arguments. `Argument count error: StopCreating wanted 0, got 1` otherwise. |
| `modifiers node` | **`node.modifiers`** | The function form does not work; the **property** form does. |
| `delete (Sweep())` | attach to a node, delete the node | Standalone modifiers cannot be deleted: `Sweep()` returns a non-node and `delete` throws `No "delete" function for sweep:Sweep`. |
| `maxVersion()[8]` | `maxVersion()` | `maxVersion()` returns an **array**; the major version is at index 8. `get3dsMaxVersion()` and `getMaxVersion` do not exist. |
| `fileExists`-style existence by enumeration | `execute` + construct | Class existence is not a file question — see section 7. |

One more, in the same family because it produces a baffling type error:

- **String precedence:** `("Section_" + i as string)` throws
  `Incompatible types: 1, and ": "`. Write `("Section_" + (i as string))` — parenthesise the cast.

---

## 9. Routing rules

1. **Prefer the typed tool over `execute_maxscript` whenever a typed tool exists.** Typed tools are
   validated, return structured data, and fail loudly. Reach for MAXScript only after confirming
   section 4 has nothing for the job.

2. **Use `execute_maxscript` ONLY for:** NURBS surface construction; shape and spline construction
   and editing; operations with no typed tool; reading undocumented class state; and **proving a
   class exists** (section 7).

3. **MAXScript execution is MAIN-THREAD** (`threadMode: mainThread`) — long scripts block the UI and
   the viewport stops responding. Keep scripts under ~2 s. Batch work into one script rather than
   issuing many small calls; do not run a per-vertex MAXScript loop over large meshes (build a
   Data Channel modifier or use `add_data_channel` instead).

4. **Every MAXScript snippet must be idempotent and must not leave test objects behind.** Delete
   what it creates unless the object is a deliverable. Use a unique prefix for probe objects and
   `try ... catch` cleanup so a mid-script failure does not leave debris in the scene. A probe that
   pollutes the scene poisons every later measurement.

5. **Class existence is established only by MAXScript construction, with a bogus control in the same
   batch.** `get_plugin_capabilities`, `introspect_class`, `discover_plugin_classes` and
   `inspect_plugin_constructor` are orientation hints and have all produced false negatives and
   false positives in this environment. See sections 6 and 7.

6. **Before calling any tool, confirm it is a `3dsmax-mcp_*` tool and that its name appears in
   section 4.** A schema error from an unrecognised name almost always means a Rhino-side tool, not
   a broken bridge. See section 5.

---

## 10. Quick decision procedure

1. Read the task. Classify it into a section 4 row.
2. If the row's tools include the need, and the name is in section 4, call the typed tool. Done.
3. If the need is NURBS/curve/shape, or if no row covers it, go to `execute_maxscript` and consult
   `12-nurbs-gotchas.md` first.
4. If the class you need is not in any list here, **probe it** (section 7) — do not conclude it is
   absent from an enumeration, and do not report the NURBS API as unavailable.
5. If you were about to call a scatter / particle / RailClone tool, stop — section 3 applies.
6. Verify the result with `capture_viewport`, `analyze_node_orientation`, or `inspect_properties`.
   Tool success is not geometric correctness.
7. Clean up any probe objects you created.