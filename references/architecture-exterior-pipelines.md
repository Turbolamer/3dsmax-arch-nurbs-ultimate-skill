# Architecture & Exterior Modeling Pipelines for `3dsmax-mcp`

> **Purpose:** End-to-end architectural and exterior production workflows — site and terrain,
> building massing, core and shell, curtain walls, classical and modern facades, roof systems,
> stairs and ramps, hardscape, landscaping, materials, lighting and geometric QA.
>
> **Routing corrected 2026-10-06.** This file was written against a **178-tool server that is not
> the one connected.** `curve_model`, `loft_mesh`, `draw_spline`, `geometry_qa`, `contact_check`,
> `scene_qa` and `agent_viewport` are **absent**, as are Forest Pack, tyFlow and railClone. Every
> step that prescribed one has been rerouted to a verified route and labelled with its evidence.
>
> **Authority.** `references/_closeout-evidence.md` is the evidence brief for this correction.
> `references/02-mcp-live-orchestration.md` §4 is the verified tool routing table; §3 is the list of
> tools that always fail. Where this file says **measured**, a transcript exists. Where it says
> **UNVERIFIED**, nothing was executed and the claim is a hypothesis that must be probed live.

---

## 1. Units, Coordinate Conventions & Scene Layer Organization

### 1.1 Units & Proportions Check

**Measured:** scene units in this build are **centimetres**, `units.SystemScale` 1.0 — a spec value
in cm reaches Max unchanged. Read `units.SystemType` **directly**; `getProperty units #SystemType`
**fails**.

**Authority for the numbers.** `references/09-defaults.md` is the single source for every
dimension default, and **every use of one is recorded as an `A-nnn` assumption, never as a fact.** A
convention's *default* is the value to use; a value merely *inside* its range is an invention. The
table below is a design quick-reference carried over from the original file; treat it as
**UNVERIFIED-from-source** unless `09` agrees, and prefer `09` when they differ.

| Element | Range | cm | `09-defaults.md` |
|---|---|---|---|
| Residential floor-to-floor | 280–330 | slab 20–30 | `D-SH-01`, default 300 |
| Commercial / lobby floor-to-floor | 360–600 | — | `D-SH-01` |
| Standard door | 90–100 w × 210–240 h | double 180–240 w × 240–300 h | — |
| Window sill (standard) | 80–90 | floor-to-ceiling glazing 0–15 | `D-OP-02`, default 90 |
| Window head | 240–270 | — | `D-OP-03`, default 270 |
| Parapet above roof finish | 90–120 | thickness 30–40 | `D-PC-01` / `D-PC-02` |
| Railing / balustrade | 105–110 | — | — |
| Stair riser / tread | 15–17.5 / 28–32 | 2R + T ≈ 62–64 | `D-CR-05`, default 17 / 30 |
| Road lane width | 300–350 | curb height 12–15, curb width 15–20 | — |

Two rules `09` states that this file's original phrasing lost:

- `sill_cm` and `head_cm` are measured from **that level's finished floor**, not from grade.
- The stair rule is usually a **riser+tread relationship, not either number alone — code-driven,
  verify.** Do not emit a stair from the range alone.

### 1.2 Layer organization — **the pipeline's layer stack is data, not a tool call**

> **This section is superseded in place.** The tool call it described does not work.
>
> `manage_layers(action="create", ...)` cannot move objects between layers: **layer assignment is
> impossible from this bridge — nine routes were executed, all failed**, and `manage_layers`' entire
> verified vocabulary is `{list, create, delete}`. Layer attribution is **data** that the user
> applies by hand in the Layer dialog (`agents/max-orchestrator.md` §5.3).
>
> **The ten-layer stack below is also not this repo's standard.** The canonical vocabulary is the
> **eight**-layer set in `references/11-layer-standard.md`: `00_SITE`, `01_SLABS`, `02_STRUCTURE`,
> `03_CORE`, `04_ROOF`, `05_FACADE`, `90_SCENE`, `99_DEBUG`. Use that one — the original list here
> is kept only so a reader who remembers it learns that it disagrees.

The original ten-layer stack, retained for reference:

1. `00_Site_Terrain` — topography, site boundary, water bodies, context buildings
2. `01_Structure_Core` — foundations, floor slabs, structural columns, shear walls, core shafts
3. `02_Facade_Envelope` — exterior walls, cladding panels, brick/stone masonry, NURBS shells
4. `03_Fenestration_Glazing` — window frames, curtain wall mullions, glass panes, doors, louvers
5. `04_Roof_Parapets` — roof slabs, pitched roofs, parapets, copings, skylights, MEP rooftop units
6. `05_Stairs_Ramps_Railings` — exterior steps, ramps, canopies, balconies, balustrades
7. `06_Hardscape_Roads` — roads, sidewalks, curbs, paving, retaining walls, bollards, fences
8. `07_Landscape_Scatter` — Forest Pack objects, hidden scatter source plants/rocks
9. `08_Props_Cosmos` — vehicles, street furniture, streetlights, people, signage
10. `09_Lights_Cameras` — sun/sky, HDRI dome, architectural facade lights, interior glow planes

What survives, and is worth keeping: the *grouping intent* — separate site, structure, envelope,
fenestration, roof, circulation, hardscape, planting, props, and lighting/camera. That is a sound way
to think about an exterior scene even when the layer assignment is manual. The naming convention
that goes with each node is enforced: `references/11-layer-standard.md` §N1–N4 and invariant `G-74`
(node names derived from their spec id, dashes replaced, unique across `placements[]`,
`opening_cuts[]`, `wall_cells[]` and `scatter[]`).

---

## 2. Core & Shell Construction (Walls, Slabs, Columns, Openings)

### 2.1 Footprint-Driven Extrusion & Sweeps

**Measured route.** A footprint is a MAXScript shape; solidity comes from an attachable modifier.

- **The shape:** `references/maxscript-splines-shapes.md` — `splineShape`, `addNewSpline`,
  `addKnot`, `close`, `updateShape`. The shape constructors (`rectangle`, `circle`, `arc`, …) were
  all constructed and read back at P4b-r. Two traps govern every shape script: **`bezierShape()` is
  unusable** (`updateShape` throws on it), and **`updateShape` throws if any spline in a
  multi-spline shape has only 2 knots** — give every spline ≥ 3 knots.
- **The solid:** `Extrude` and `Sweep` **construct but throw on a hand-written `addModifier`.** Use
  the typed tool **`3dsmax-mcp_add_modifier`**, which was executed and attaches them. The same
  applies to `Lathe`, `Surface`, `CrossSection`, `Conform`. `Bevel_Profile` is unusable either way.
  `Shell`, `Chamfer`, `Lattice`, `Uvwmap`, `Noisemodifier`, `Bend`, `Twist`, `Taper` attach fine
  with plain `addModifier`.
- **Wall thickness without a Shell modifier:** `applyOffset <shape> <float>` was measured to return
  `true`. Negative is left of the spline direction; open splines become closed outlines.

Verified `Extrude` parameters, all seven: `amount`, `segs` (default 1), `capStart`, `capEnd`,
`capType`, `mapCoords`, `matIDs`.

Verified `Shell` parameters — and **three of the six commonly cited do not exist**: `innerAmount`
(default 0.0), `outerAmount` (default 1.0) and `straightenCorners` (default false) exist;
**`segs`, `overrideEdgeMatID`, `edgeMatID` are `NO`.** Do not write them.

**Stack limit, measured:** ≤ 5 modifiers per `execute_maxscript` call; > 10 on one node is
forbidden. 20 on one node **froze Max permanently and cost a reboot.** Do not re-measure the ladder.

**Slabs.** Emit solids, do not extrude. `assembly.ms` emits one `Box` per row and contains **zero**
`addModifier` calls (`G-81`). Placement primitive: `Box(width:,length:,height:,pos:)` — geometry
centres on `pos.x/y` and **the base sits at `pos.z`**, which stays true after `copy`, after a
`baseObject` assignment and after rotation. To centre a box vertically write
`pos = [cx, cy, cz - height/2]`.

**UNVERIFIED-from-source:** `draw_spline` + `add_modifier` as a two-tool sequence (both tools
exist; that pairing is not something a transcript covers), and `add_offset` as a bridge tool name.

### 2.2 Openings in solid walls — **do not use a Boolean**

> **This subsection is superseded in place.** It prescribed `boolean_operation` with inline
> cutters. That route does not work here, and the failure is silent rather than loud.
>
> **Measured:** the **Boolean modifier cannot be made to cut in this build.** `Boolean()` throws,
> `BooleanMod()` carries Voxel Map's paramblock, and the bridge's `add_modifier` **attaches** one
> whose operand is never set — `verts=8 faces=12`, unchanged, for every `params` spelling. A
> previous build shipped **unpierced walls and reported success**, because its census counted its
> own iterations and read `cut_count = 16` against a scene with **zero** modifiers (`G-81`,
> `agents/max-assembly.md` AP-22).

**The verified route — build the wall out of solid cells and never cut it.** Emit one `Box` per
`wall_cells[]` row, each spanning the wall's full thickness:

1. For each host `facade_wall`, take **its own** `profile_cm` extent — not the opening's centre.
2. Cut at every opening's `u` boundary to get **columns**.
3. Inside each column, cut at the `v` boundaries of the openings covering it to get **rows**.
4. Emit in **ascending run interval, then ascending `v`**.
5. The spec keeps `u` facade-local (that is the frame the facade grid is written in); the world
   position along the run is `start_corner_cm + u`, converted once, here.

The opening is therefore passed through cleanly — which is what `G-83` asserts rather than assumes.
The old "cut depth ≥ 2× the wall thickness" advice is **moot**: there is no cutter.

Two invariants a rerun must reproduce: every `dimensions.json` opening has **exactly one** cut and
every cut exactly one opening — orphans fail in **both** directions (`G-77`); and per host,
`Σ cell volume == wall volume − openings volume` within tolerance (`G-82`, `G-83`).

**UNVERIFIED-from-source:** the original's `mesh_edit` route (`inset` / `bridge` / `extrude` to keep
100% quad topology and automatic Material IDs on window reveals). `inspect_mesh` and `mesh_edit` do
not appear in the verified routing table, and neither was executed here. It is plausible, it is not
measured — probe before relying on it.

---

## 3. Facade Systems & Architectural Styles

### 3.1 Modern Curtain Walls & High-Rise Towers

1. **Rectilinear / extruded-footprint towers — `railClone` is not installed.**
   `get_railclone_style_graph` is absent and `references/railclone.md` is **OBSOLETE, reference
   only.** The verified substitute is a MAXScript array describing base and segment runs plus a
   material-ID map, instantiated with `clone_objects` in `mode: "instance"`. Keep the array in a
   spec file so the layout stays parametric without the plugin.

   The original `A2S` / `L1S` walkthrough below describes a plugin that cannot run. What survives is
   the **bay module design**, which is good practice and independent of the tool: author one clean
   modular bay (e.g. `300` wide × `360` high) in the **XY plane**, height along local Y, with proper
   Multi/Sub-Object material IDs —

   | MatID | Element |
   |---|---|
   | 1 | Mullion / transom aluminium frame |
   | 2 | Clear vision glass |
   | 3 | Spandrel glass / opaque shadowbox panel |
   | 4 | Interior ceiling / slab edge strip |

   **Measured trap:** a 100 × 200 × 20 box rotated 90° about Z spans **X 200 / Y 100** — the long
   axis follows the rotation. The **in-out placement rule**: `n = copy src` then
   `n.baseObject = src.baseObject` produces a true reference instance; `setCopyMode` **does not
   exist** and a plain `copy` shares nothing. And **materials are per node, not per prototype** —
   0 of 10 instances inherited a material set on the prototype. `baseObject` sharing is a memory
   optimisation, not inheritance.

2. **Custom quad curtain walls without railClone.** The original route was
   `create_mesh` / `loft_mesh` + `mesh_edit`. **`loft_mesh` is absent** → use
   `NURBSULoftSurface` (below), or build the quad cage from a shape plus the attachable modifier set
   in §2.1. **UNVERIFIED-from-source:** the face-`inset` / negative-`extrude` batch that creates
   recessed panes and projecting mullions in one atomic pass — `create_mesh` and `mesh_edit` are
   not in the verified routing table.

3. **Freeform / double-curved / twisted facades → NURBS.** This route is **vindicated at P4b** and
   is the strongest content in the file. Build the master envelope with `NURBSULoftSurface`,
   `NURBSUVLoftSurface` or `NURBS2RailSweepSurface` (`references/nurbs-complete-guide.md`,
   `references/nurbs-architecture-recipes.md`). Sample the surface analytically via `evalPos surf
   u v` into a quad `Editable_Poly` curtain wall or structural diagrid
   (`snippets/nurbs_arch_library.ms` — loads cleanly, 12 functions, zero known bugs).
   **Correction, verified:** `NURBSProjectVectorCurve` **projects and does not cut**. Trim skylight
   openings with `references/12-nurbs-gotchas.md` §3.25–3.26 / `agents/max-nurbs.md` §6.7.5, not
   with the superseded recipe in `nurbs-architecture-recipes.md`.

### 3.2 Classical & Haussmann / Neoclassical Facades

The proportion stack — base / rusticated podium → piano nobile and pilaster order → entablature and
cornice → mansard / balustrade — is design guidance and survives unchanged.

- **Horizontal profiles (plinth, belt courses, sills, main cornice):** the original prescribed
  `curve_model` with a `sweep` output, an `up` vector, and cyma-recta / ogee `bezier` segments.
  **`curve_model` is absent and there is no measured equivalent** — see §2.1. The profile is a
  2D shape; the path is a second shape; solidity comes from the attachable modifier set.
  **`UNVERIFIED-from-source`:** whether a closed profile shape can be swept along a path shape
  through this bridge. **Do not assume the `up`-vector / twist semantics in the original carry
  over** — Max's `Sweep` takes a section shape and a spine *node*, and no transcript covers frame
  control here. Probe it.
- **Arched windows, vaults, colonnades:** the original offered `curve_model` (`arc` segment) or
  NURBS rational arcs. Use the **NURBS** form — vindicated at P4b. The `Arc` **shape** is also
  available and was measured, but note it stores its angles in **`from`** and **`to`**; there is no
  `from_angle` / `to_angle`.
- **Fluted columns with entis:** the original said `loft_mesh` with 4–5 circular cross-sections of
  varying radius. **`loft_mesh` is absent.** Two real routes, and **the modifier has a trap**:
  `Lathe` attaches only through `3dsmax-mcp_add_modifier`, and its axis property is **`axis`**, a
  **`matrix3`** — not `direction`, and not an integer enum. `degrees`, `segs` and `flipNormals`
  exist. The multi-section loft equivalent is `NURBSULoftSurface`.
- **Balustrades, dentils, corbels:** model one element, then array. `RailClone` L1S is gone;
  `clone_objects` in `mode: "instance"` replaces it, and MAXScript `lengthInterp` distribution is
  **measured and real** — but be precise: `lengthInterp` is *uniform by arc length*, which is what
  you want for evenly-spaced balusters. (`pathParam` is **inert**: it is type-checked and changes
  nothing. Choose `lengthInterp`/`lengthTangent` vs `pathInterp`/`pathTangent` instead.)

### 3.3 Contemporary Residential & Villa Exteriors

- **Timber slat screens with randomized rotation:** `add_data_channel` **exists and was executed** —
  `add_data_channel(name=..., operators=[{"type":"vertex_input"},{"type":"scale"}])`. Three
  corrections that matter: the operator key is **`type`**, not `name`; values are lowercased
  **snake_case** (`vertex_input`, not `DistToNode` or `FaceArea` — those do not exist); and the real
  vocabulary is 32 operators, with **no presets** (`list_dc_presets` returns `[]`). `RailClone` for
  the same effect is gone → `clone_objects` instance mode.
- **Chamfering hard concrete and metal edges so sunlight catches a specular highlight:** the class
  name in the original, `ChamferMod`, constructs but `classOf` reports **`Chamfer`**. Verified
  parameters: `amount` (1.0), `segments` (1), `tension` (1.0), `limitEffect` (false), `minAngle`
  (20.0). **`mitering` does not exist** — write `minAngle` instead.
- **Coping overhangs `2–4` as a drip edge on every parapet:** keep. A flat-topped parapet reads as a
  slab. Matches `D-PC-03` (default 3, range 2–5).

---

## 4. Roof Systems (Flat, Pitched, Hip/Gable, Vaulted & NURBS Shells)

1. **Flat commercial / modern villa roofs.** Never leave a bare flat face:
   - Perimeter parapet wall — `30–40` thick, `90–120` high (`D-PC-01` / `D-PC-02`).
   - **Metal coping cap** on the parapet, overhanging `2–3` each side with a slight inward slope.
     The original prescribed a `curve_model` sweep → **absent**; use §2.1's shape + attachable
     modifier route. **`UNVERIFIED-from-source`:** the folded drip profile as an extruded shape.
   - Inset roof surface with a material ID for membrane, gravel ballast or pavers, plus skylights,
     rooftop mechanical curbs and solar panels.
   - The original's `scatter_forest_pack` for roof gravel/pebbles → **absent plugin.** Substitute
     Chaos Scatter (§6) or `clone_objects` instance mode. **UNVERIFIED-from-source:** Chaos Scatter
     as a roof-gravel device; the verified Scatter parameter map is in
     `references/14-chaos-scatter.md`.
2. **Pitched, gable, hip and mansard roofs.** Build exact ridge, hip, valley and eave geometry so
   pitches meet at true ridgelines with no boolean slivers — **and there are no booleans here**
   (§2.2), which is an argument *for* doing it this way. The original's `create_mesh` with
   world-space vertex and face arrays is **UNVERIFIED-from-source** — `create_mesh` is not in the
   verified routing table. The mesh-modifier route (`Edit_Poly`, attachable) or `FFDs` (attachable)
   is the traceable option. Eave fascia, soffits and downspouts follow; gutters were a `curve_model`
   sweep → **absent**, use §2.1.
3. **Domed, barrel-vaulted, hyperbolic-paraboloid and freeform roofs.** NURBS is the route and it is
   **vindicated**: `MakeNURBSSphereSurface`, `NURBSLatheSurface`, `NURBSRuledSurface` for hyperbolic
   paraboloids, `NURBSULoftSurface` / `NURBSUVLoftSurface` for organic shells.
   **UNVERIFIED-from-source:** `NURBSOffsetSurface` for structural shell thickness. `NURBSOffset`
   did not appear in any transcript in this repo — **probe it before you plan a shell thickness on
   it.**

---

## 5. Site, Terrain, Roads & Hardscape

1. **Graded terrain and building-pad integration.** A building must never float above or clip
   through sloped terrain. Create a flat pad / plinth at `Z = 0.0` (or sidewalk level `Z = +15`),
   then grade away from the foundation:
   - Smooth berms and swales: `NURBSPointSurface` / `NURBSULoftSurface` — **vindicated**.
   - Or a subdivided plane sculpted by `Noisemodifier` — **attachable with plain `addModifier`**,
     and all six of its properties were verified: `seed`, `scale`, `fractal`, `roughness`,
     `iterations`, `strength`. **`strength` really is a point3.** `UNVERIFIED-from-source:` the
     original's `edit_vertices` with soft-selection `falloff` — no such transcript here.
2. **Roads, sidewalks, curbs.** Sweep a curb profile along a path — original numbers `15` high × `18`
   wide with a `2` chamfered top corner, and asphalt at `Z = -15` relative to the sidewalk at
   `Z = 0`, which is a sound detail. The original's `draw_spline` / `curve_model` path is **absent**;
   both the path and the profile are shapes (§2.1). **UNVERIFIED-from-source:** sweeping one shape
   along another through this bridge.

---

## 6. Landscaping and Asset Population — **both sections OBSOLETE**

> **Superseded in place, not deleted.** The surrounding architectural context still matters, so the
> *strategy* is kept. The *tools* and the *parameter blocks* are dead and are labelled as such
> rather than translated, because there is no verified mapping between them and Chaos Scatter's
> parameter set — inventing one would be exactly the failure this correction exists to remove.

### 6.1 Multi-Layer Vegetation — Forest Pack is **not installed**

`scatter_forest_pack` **always throws**; forestPack and forestLite are absent. The density /
`facing_mode` / scale-range block below is **forestPack-specific and does not transfer** — it is
retained only so a reader who remembers it learns not to reuse it.

**The strategy that survives**, and maps onto Chaos Scatter: layer plantings by role and density
rather than scattering one asset everywhere.

| Layer | Role | Forest Pack parameters — **DEAD, do not reuse** |
|---|---|---|
| 1 | Base lawn / cut grass | `density_units_x_cm: 80–120`, `scale_min: 80`, `scale_max: 120`, `facing_mode: 0` |
| 2 | Weeds, clover, wildflowers | `density_units_x_cm: 250–400`, `scale_min: 70`, `scale_max: 135` |
| 3 | Shrubs, ornamental grasses | lower density along beds; `facing_mode: 1` |
| 4 | Canopy trees | `density_units_x_cm: 1200–2500`, `facing_mode: 1`, `scale_min: 85`, `scale_max: 125` |

**Substitute — Chaos Scatter** (`references/14-chaos-scatter.md`):
`ChaosScatter()` constructs; **`CScatter` is `NotCreatable`**, so always construct
`ChaosScatter`. Wire `targetNodes` from the surface, `modelNodes` one per plant, `modelFrequencies`,
`instanceCountLimit`, scale and rotation ranges, `collisionAvoid`. Two names that will bite:

- **`distributionDesityPattern` is the real property name — the typo is in Max, not in your code.**
  The spec field is `distribution_density_pattern`; the builder emits the typo.
- **`seed` is `1 … 31337` and is *data*.** It comes from the spec (`G-78`). A run-time-generated seed
  makes the scatter irreproducible.

Post-scatter cleanup still applies, and the trap is real: **`delete <base>` does not delete its
instances.** Hide source meshes with `set_visibility` — that tool **is** verified — but collect and
delete instances explicitly by name, twice (`for o in objects do delete o` silently skips entries).

### 6.2 Populating exteriors with Chaos Cosmos — **no such tool here**

`cosmos_search` and `cosmos_import` are **not in the connected toolset**, and no `cosmos_*` family
appears in the evidence brief's absent-tool table — so this is **UNVERIFIED from this close-out, not
confirmed absent.** Probe `get_plugin_capabilities` before relying on either. Treat as **absent**
for planning purposes.

Nothing in the original's asset list survives as a route: the asset-search step, the PBR material
search, the HDRI sky search, and the ground-contact verification via `contact_check` all name tools
that are either absent or unverified here. The **intent** — acquire verified exterior assets, then
place and orient them and prove they touch the ground — is sound; see §8 for the ground-contact
measurement that replaces `contact_check`, and note the scope note in §7 about assets the pipeline
does not deliver.

---

## 7. Exterior Materials, UVW & Architectural Lighting

> **Scope note.** Materials and UVs were **cancelled** as pipeline stages. The deliverable is the
> model plus a hand-off; the user applies materials by hand (`agents/max-orchestrator.md` §5.2–5.3).
> Nothing here is an automated stage, and no material is delivered by the builders.

1. **Materials.** `assign_material` and `create_material_from_textures` are both in the verified
   routing table — but their **schemas advertise classes that are not installed**: Octane, VRay and
   `RS_Standard_Material`. Pass only `OpenPBR`, `PhysicalMaterial`, `Standard`, or a Corona class,
   and **always verify with `get_materials`.** For reference, `_CoronaPhysicalMtl` is the
   architectural material and has a **leading underscore** — `CoronaPhysicalMtl` is not a name in
   this build.
2. **UVW. — RESOLVED at P15, 2026-10-06, by live measurement.** Full transcripts and the class
   census are in **`references/13-uv-rules.md`**; the four facts that matter here:

   - The `Uvwmap` modifier attaches with plain `addModifier`; **all nine** of its parameters are
     verified: `maptype`, `length`, `width`, `height`, `utile`, `vtile`, `wtile`,
     `realWorldMapSize`, `mapChannel`. `mirrorU/V/W`, `offsetU/V/W`, `flip` and `tiling` throw.
   - **`maptype: 4` IS the Box mapping value** — the row that used to say UNVERIFIED. `maptype`
     reads `0` on a fresh `Uvwmap`; writing `4` persists across calls.
   - **`realWorldMapSize: true` makes one UV unit equal one centimetre.** Measured on three
     independently placed boxes: 4×6×2 cm → uv span `4.0 × 6.0`; 400×600×2 → `400.0 × 600.0`;
     300×150×20 → `300.0 × 150.0`. **For one tile per metre, set `utile` = `vtile` = `0.01`.** The
     map is object-relative, not world-aligned — fine for a repeated panel, wrong for a continuous
     texture run across neighbours.
   - **`generateUVs1` and `setTiling` are now measured, and `setTiling` is defective.** `generateUVs1`
     is a boolean **constructor keyword** and a property of the **committed surface sub-object**
     (unreadable on a `NURBSPoint`). `true` yields a **`0..1` normalised map regardless of the
     surface's size in cm**; `false` yields **no channel 1 at all**. `setTiling <surf> <u> <v>
     channel:1` works and returns `"OK"`, but **silently floors both arguments to integers** —
     `2.99 → 2`, `1.9 → 1`, `3.5 → 3`. A 350 cm wall therefore gets 3 tiles, not 3.5, and every
     real building has non-multiple-of-100 widths. **Use `Uvwmap` with `utile`/`vtile` for
     fractional tiling — measured working at `3.5 × 1.5` on a 350 × 150 cm surface.**
   - ⛔ **A modifier's `utile`/`vtile` written in the same `execute_maxscript` call that adds the
     modifier is silently discarded** — it reads back correctly in-call and reverts to `1.0` in the
     next call (8/8). `maptype` and `realWorldMapSize` are unaffected. Write in a **later call**,
     or force an evaluation (`snapshotAsMesh`) between the `addModifier` and the write (3/3).
   - **`Unwrap_UVW` constructs and attaches but is unusable through this bridge**: it changes
     nothing and every one of its methods throws when invoked. Unwrapping is a manual, in-the-UI
     operation.
   - **Reference instances inherit their prototype's modifier.** `addModifier` on the 29 `PROTO_*`
     nodes took the delivered chain from **0 to 165** UV-carrying nodes. The wall cells and massing
     are not instanced and need their own 74.
3. **Renderer detection — corrected.** The original said "always run `lighting_capabilities` first".
   **That tool is not in the verified routing table — treat it as UNVERIFIED.** Use
   **`get_plugin_capabilities`**, which is verified to report renderer and plugin presence.
   Measured: Max reports **`Arnold`** active while the user's production renderer is **Corona** —
   **never assume.** To switch, the setter needs an **instance, not the class**:
   `renderers.production = Corona` **throws**. Write `local c = Corona()` then assign `c` to both
   `renderers.production` and `renderers.current` — two independent slots, not aliases. **`Corona()`
   costs ~3.5 s cold: give it its own `execute_maxscript` call**, the one exemption to the ~2 s
   budget.
4. **Lighting design intent.** Blue-hour presentation, warm interior light behind glazing, grazing
   uplights on masonry and columns, and bollard / tree uplights at `2700–3200K` — the *intent* is
   sound and worth keeping. **UNVERIFIED:** `create_lights` as a tool name, and every kelvin figure
   (no transcript covers them). Probe before prescribing. There is no automated lighting stage: this
   is manual authoring by the user.

---

## 8. Mandatory Exterior QA Protocol Before Finishing

Never conclude an exterior modeling task without this loop. **`geometry_qa`, `contact_check`,
`scene_qa` and `agent_viewport` do not exist**, and the read-back below replaces all four. Every
number is **measured**; the tolerance comparisons are what make the loop a gate rather than a
ritual.

The read-back uses only `objects.count`, `node.min` and `node.max` — the three reads named in
`references/_closeout-evidence.md` §1 as the verified replacement. Report the nodes that carry the
design, **by name**, so a failure names a node rather than a number:

```maxscript
-- Census. One call, scene left clean; every read guarded.
local out = "objects.count=" + (objects.count as string)
for nm in #("Wall_North_F1", "Slab_F1", "Parapet_North") do (
    local nd = getNodeByName nm
    if nd != undefined do
        out += " | " + nm + " min=" + (nd.min as string) + " max=" + (nd.max as string)
)
print out
```

Two rules this shape of the loop exists to enforce: **guard every property read in its own
`try ( ) catch ( )`** — an unguarded read elsewhere aborts the whole probe — and put any cleanup
block **first**, not last. Scene-wide aggregation helpers are deliberately not used here: the only
aggregation route in the evidence brief is per-node, so anything more elaborate is unmeasured.

1. **Count and extents** — `execute_maxscript` reading `objects.count` and `node.min` / `node.max`,
   as above. `get_scene_snapshot` gives counts by class and a materials summary. **This replaces
   `geometry_qa` for integrity checking.** It will not tell you about inverted normals,
   non-manifold edges or degenerate faces — **those are UNVERIFIED here and there is no tool that
   reports them.** If they matter, inspect them by eye in a capture or write the check yourself in
   MAXScript; do not assume a clean count implies clean geometry.
2. **Physical grounding and interpenetration** — **this replaces `contact_check`**, and it is a
   subtraction, not a magic call: for each column, wall, railing, post or tree, read `node.min.z`
   and compare it against the ground `z` it must sit on, all in scene units (centimetres).
   **`min.z == ground_z`** is seated. A positive gap is floating in mid-air — a defect. A negative
   value is intentional seating for trees and posts, and a defect for a wall or a column. Assert
   the difference with a tolerance; never with `==`, and remember `pos.z` is the *base* of a `Box`.
3. **Scene hygiene** — **this replaces `scene_qa`.** There is no single call. Assemble it from
   `get_scene_info` (paginated listing with filters) and `get_scene_snapshot`: confirm descriptive
   architectural names following `references/11-layer-standard.md` N1–N4, confirm every node name is
   derived from its spec id with dashes replaced (`G-74`, unique across `placements[]`,
   `opening_cuts[]`, `wall_cells[]`, `scatter[]`), and check clean transforms via
   `analyze_node_orientation`. **Layer assignment cannot be checked here at all** — it is data the
   user applies by hand.
4. **Scatter determinism — `FpInterface`.** For a Chaos Scatter object, `FpInterface` is the **only**
   verified read-back: `getInstanceCount()`, `getModelCount()`, `getModelNode(i)`, and
   `saveConfiguration` / `loadConfiguration`. Snapshot, rebuild, and require the instance count to
   come back **identical**; if it does not, the seed is not being applied.
5. **Visual proof** — **this replaces `agent_viewport` and `set_viewport`.** The bridge's own
   captures are the route: `capture_viewport` for the current view, `capture_multi_view` for a
   stitched labeled grid of angles, `isolate_and_capture_selected` for per-object captures of a
   selection. Set the view by other means — the `agent_viewport(action="open")` /
   `set_viewport` pair in the original is **absent or UNVERIFIED**. The original's eye-level intent
   (eye at `Z = 165–180` for human eye level, plus a bird's-eye overview) is sound guidance; in
   centimetres that is `1650–1800`, and the original's figures were in centimetres only under a
   metres reading — **compute it, do not hard-code either.**

### 8.1 Anti-patterns — the traps this loop exists to catch

| Anti-pattern | Why it fails |
|---|---|
| Treating `objects.count` as proof of clean geometry | The count says nothing about normals, manifoldness or degenerate faces |
| Counting your own loop instead of the scene | The build that shipped **unpierced walls and reported success** did exactly this — `cut_count = 16` against a scene with zero modifiers (`G-81`) |
| Attaching a Boolean and calling it a cut | It attaches and does nothing. `verts=8 faces=12`, unchanged, for every `params` spelling |
| `setCopyMode` for instancing | **Does not exist.** `n = copy src` then `n.baseObject = src.baseObject` |
| `rotationZ` / `rotationX` / `rotationY` / `angle` / `matrix3` as a *value* | **Do not exist.** Use `n.rotation = quat <degrees> [0,0,1]` |
| Expecting a material on an instance | **Materials are per node.** 0 of 10 instances inherited a material set on the prototype |
| `renderers.current = Corona` | **Throws** — the setter needs `Corona()`, an instance |
| More than 5 modifiers per call | 20 on one node froze Max permanently and cost a reboot |
| `for o in objects do delete o` | Silently skips entries and leaves orphans. Collect names, delete by name, run twice |
| `"x" + value` | Throws. Write `(value as string)` |
| `try { } catch { }` | The brace form **is** a parse error. Use `try ( ) catch ( )` |