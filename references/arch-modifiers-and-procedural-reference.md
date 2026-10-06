# Architectural Modifiers & Data Channel Reference for `3dsmax-mcp`

> **MCG removed 2026-10-04.** This file previously advertised a Max Creation Graph section.
> **There is no `mcg_*` tool in the connected toolset** — verified by direct inspection of the
> live tool list, not inferred. MCG cannot be driven from this bridge. See §3.

> **Purpose:** Exact MAXScript/MCP class names, parameter names, enum integers, and architectural recipes for modifiers (`add_modifier`, `set_modifier_property`) and **Data Channel** (`add_data_channel`).
>
> **2026-10-04 correction.** The original purpose line advertised a third subject,
> **Max Creation Graph (`mcg_*`)**. **No `mcg_*` tool and no `curve_model` tool exist in the
> connected MCP toolset** — verified by direct inspection of the live tool list, so this is
> definitive. §3 has been rewritten to say so. There is no MCG workflow to drive from this
> bridge.

---

## 1. Essential Architectural Modifiers Cheat Sheet

> ### 2026-10-04 — the original headline instruction was WRONG for 6 of 23 classes
>
> The text this note replaces read: *"When calling `add_modifier(name=..., modifier=...,
> params={...})` or `set_modifier_property`, always use the exact MAXScript class name
> … below."* The **"always" was wrong.** Measured against live 3ds Max 2026.3.2:
> MAXScript `addModifier <node> <Ctor>()` succeeds for **16** of the 23 classes and
> **throws** for `Extrude`, `Sweep`, `Lathe`, `surface`, `CrossSection`, `Bevel_Profile` —
> even though all six construct fine standalone. `modPanel.addModToSelection` is **not** a
> workaround: it returns `OK` and silently adds nothing (`modifiers.count` stays `0`).
>
> | class | MAXScript `addModifier` | typed `3dsmax-mcp_add_modifier` |
> | :--- | :--- | :--- |
> | `Extrude` | **THROWS** | works — `Added ExtrudeMod to Box001` (`classOf` = `Extrude`; "ExtrudeMod" is only the tool's display string) |
> | `Sweep` | **THROWS** | works — `Added Sweep to Box001` |
> | `Lathe` | **THROWS** | works — `Added Lathe to Box001` |
> | `surface` | **THROWS** | works — `Added Surface to Box001` |
> | `CrossSection` | **THROWS** | works — `Added CrossSection to Box001` |
> | `Bevel_Profile` | **THROWS** | **FAILS** — `Unable to convert: Bevel_Profile to type: Modifier` |
>
> **Rule as measured:** use `3dsmax-mcp_add_modifier`, not a hand-written MAXScript
> `addModifier`, for `Extrude` / `Sweep` / `Lathe` / `surface` / `CrossSection` / `Conform`.
> `Bevel_Profile` is unusable through either route in this build.
>
> ### How to read the table
>
> Use the exact class name and parameter names in the table below. Per-cell markers:
>
> - **`NO`** — that parameter name **does not exist** on that class. Probed with
>   `isProperty` together with a known-positive and a `totalBogusXYZ` negative control in the
>   same batch, so the negatives are calibrated rather than assumed. **No substitute name is
>   offered**, because none was established.
> - **`UNVERIFIED`** — the row is wrong or incomplete but the real name could not be
>   established. Not a guess. Do not invent a replacement.
> - Unmarked cells were not falsified. Absence of a marker means "not shown wrong by this
>   pass", **not** "exhaustively verified".

When calling `add_modifier(name=..., modifier=..., params=...)` or `set_modifier_property`, use
the class name and parameter names in the table below:

| Architectural Purpose | MAXScript Modifier Class | Key Parameters (`params`) & Notes |
| :--- | :--- | :--- |
| **Extrude 2D Footprint to Slab / Wall** | `Extrude` | `amount` (float), `segs` (int, default `1`), `capStart` (bool), `capEnd` (bool), `capType` (`0`=Morph, `1`=Grid — use `1` for clean subdivision!), `mapCoords` (bool), `matIDs` (bool) |
| **Sweep Profile Along Path** (Cornices, Gutters, Curbs, Mullions) | `Sweep` | **2026-10-04:** all of `current_built_in_shape`, `CustomShape`, `SmoothPath`, `SmoothSection`, `Banking`, `GenMatIDs` exist — **unchanged, verified correct**. One correction: `PivotAlignment` ~~(`0..8`)~~ **reads `-1`, not `0..8`** — the integer range in the original cell was never measured. The `current_built_in_shape` enum mapping (`0`=Angle … `9`=Wide Flange) is likewise **UNVERIFIED** — the property exists but its per-value meaning was not read back. `Sweep` also **throws** on `addModifier`; use `3dsmax-mcp_add_modifier`. |
| **Custom Profile Bevel** (Classical Moldings) | `Bevel_Profile` | **2026-10-04 — UNUSABLE in this build.** `Bevel_Profile` constructs standalone, but `addModifier` **throws** for it and `3dsmax-mcp_add_modifier` **fails**: `Unable to convert: Bevel_Profile to type: Modifier`. This cell previously recommended `curve_model(output:{kind:"sweep"})` as a script-free fallback — **that recommendation is withdrawn**: `curve_model` **is not in the connected MCP toolset** (direct inspection of the live tool list). No working route was found. Do not plan work that depends on this class. |
| **Wall / Roof Shell Thickness** | `Shell` | `innerAmount` (float), `outerAmount` (float), `straightenCorners` (bool — **critical** for architectural walls so mitered corners stay uniform thickness!). **2026-10-04 — 3 of 6 original parameters do not exist:** ~~`segs` (int)~~ → **`NO`**, ~~`overrideEdgeMatID` (bool)~~ → **`NO`**, ~~`edgeMatID` (int)~~ → **`NO`**. Measured defaults for the surviving three: `innerAmount=0.0`, `outerAmount=1.0`, `straightenCorners=false`. No substitute names established for the three lost parameters. |
| **Architectural Edge Bevel / Micro-Chamfer** | `ChamferMod` → **real class name `Chamfer`** | **2026-10-04 — class-name correction:** `ChamferMod` constructs, but `classOf` reports **`Chamfer`**. `amount` (float, e.g. `0.3–1.0 cm`), `segments` (int), `tension` (float — **default is `1.0`**, i.e. flat; `0.5` is not the default), `limitEffect` (bool), `minAngle` (float, e.g. `25.0` so curved surfaces aren't chamfered) all exist; measured `amount=1.0 segments=1 tension=1.0 limitEffect=false minAngle=20.0`. ~~`mitering` (`0`=Quad, `1`=Tri, `2`=Uniform, `3`=Radial, `4`=Patch — use `0` Quad!)~~ → **`NO` — does not exist.** Since that cell recommended `0` (Quad) as the architectural default, **that recommendation is withdrawn**; no substitute was established. Separately, the original example value `25.0` for `minAngle` is a deliberate override — the measured **default is `20.0`**, which the original cell did not state. |
| **Surface of Revolution** (Domes, Columns, Balusters) | `Lathe` | `degrees` (float, `360.0`), `weldCore` (bool, `true`), `flipNormals` (bool), `segs` (int, `32–64`) — these exist. **2026-10-04 — the axis parameter is wrong in two ways:** ~~`direction` (`0`=X, `1`=Y, `2`=Z)~~ → **`NO` — does not exist.** The real property is **`axis`**, and it is a **`matrix3`, not an integer enum** — measured `matrix3 [1,0,0] [0,-1.62921e-07,-1] [0,1,-1.62921e-07] [0,0,0]`. Any code that passed `direction:` to `params` was silently ineffective or erroring. `Lathe` also **throws** on `addModifier`; use `3dsmax-mcp_add_modifier`. |
| **Diagonal Strut / Mullion Frame from Cage** | `Lattice` | `Strut_Radius` (float, measured `2.0`), `Strut_Segments` (int, measured `1`), `Strut_Sides` (int, measured `4` — the "4 for rectangular mullions" note is confirmed) — these three exist. **2026-10-04 — 3 of 6 original parameters do not exist,** and they are exactly the load-bearing ones: ~~`Joint_Type` (`0`=Tetra, `1`=Octa, `2`=Icosa)~~ → **`NO`**, ~~`Both` (`0`=Joints only, `1`=Struts only, `2`=Both — use `1` for mullions!)~~ → **`NO`**, ~~`Ignore_Hidden_Edges` (bool, `true`)~~ → **`NO`**. **The mullion recipe in this row is therefore UNVERIFIED.** The original cell told the reader to set `Both` to `1` for mullions; **that step cannot be performed** and no replacement name was established. Build the frame from the three `Strut_*` properties only, and verify the result visually. |
| **Spline Cage to Patch Surface** | `CrossSection` + `surface` (`Surface` → **real class name `surface`**, lower case) | **2026-10-04 — real parameter names are UNVERIFIED; do not guess.** `surface`: `threshold` (measured `1.0`) and `steps` (measured `5`) **do exist**. ~~`flip` (bool)~~ → **`NO`**; ~~`remove_interior_patches` (bool)~~ → **`NO`**. Eight further candidates were also probed and all returned `NO` (`flipNormals`, `reverse`, `removeInteriorPatches`, `remIntPatches`, `deleteInterior`, `smooth`, `output`, `surfaceMethod`, `mapTile`), so **no substitute for `flip` / `remove_interior_patches` is known.** `CrossSection`: ~~`spline_type` (`0`=Linear, `1`=Smooth, `2`=Bezier)~~ → **`NO`**; `splineType`, `type` and `crossSectionType` also **`NO`**. `CrossSection` exists and attaches, but its spline-type property is **UNVERIFIED**. Both `surface` and `CrossSection` also **throw** on `addModifier`; use `3dsmax-mcp_add_modifier`. |
| **Bilateral / Radial Architectural Symmetry** | `Symmetry` → **real class name `symmetry`** (lower case) | **2026-10-04 — class-name correction:** `Symmetry` constructs, but `classOf` reports **`symmetry`**. `axis` (measured `0`) and `flip` (measured `false`) **exist and are correct as documented**. `slice` and `weld` also exist, but this cell listed them as booleans and that is **wrong**: both are **integers**, both measured `1`. Write `1`, not `true`. `threshold` (float) **exists but the documented value is wrong**: measured **`0.01`**, not `0.1`. Move `.mirror` gizmo via `execute_maxscript` if the symmetry plane is offset from pivot. |
| **Architectural Section / Floor Cut** | `SliceModifier` | `Slice_Type` (`0`=Refine, `1`=Split, `2`=Remove Top, `3`=Remove Bottom), `Cap` (bool). Transform `.Slice_Plane` gizmo for height/angle. |
| **Global Bending / Twisting Towers** | `Bend` / `Twist` / `Taper` | `Bend`: `BendAngle` (measured `0.0`), `BendDir` (`0.0`), `BendAxis`, `FromTo` (bool, measured `false`). `Twist`: `angle` (`0.0`), `bias` (`0.0`), `axis`. `Taper`: `amount` (`1.0`), `curve` (`0.0`), `primaryAxis`, `effectAxis`. **2026-10-04 — two corrections:** ~~`Low`~~, ~~`High`~~ → **both `NO` — neither exists as a property on `Bend`.** They are `FromTo`-gated UI fields, so with `FromTo=false` (the default) they are not addressable at all. And the axis properties are documented as `0..2` but **all default to `2`**, not `0` — measured `BendAxis=2`, `Twist.axis=2`, `Taper.primaryAxis=2`, `Taper.effectAxis=2`. A model authored assuming axis `0` is X-shaped will instead be deformed about Z. |
| **Free-Form Deformation Lattice** | `FFD_2x2x2` / `FFD_3x3x3` / `FFD_4x4x4` | All three construct; `FFD_3x3x3` was confirmed to attach. **2026-10-04 — the control-point access route is UNVERIFIED.** ~~Animate/move control points (`animateAll <ffdMod>`, then `.control_point_1 ...`) in `0.0..1.0` normalized lattice space!~~ `control_point_1` and `control_point_10` both return **`NO`** on the modifier, and **`animateAll` itself was never tested.** Neither the property name nor the call is established — **do not build a workflow on this, and do not guess a replacement name.** |
| **Conform Road / Path to Terrain** | `Conform` (spacewarp-class object) / `SpaceConform` (the modifier-class counterpart) | Projects vertices onto a target terrain mesh along a specified direction. **2026-10-04 — important distinction, previously not stated:** `Conform`'s **0-arg constructor THROWS.** It is not a broken install and not a typo — it is a **spacewarp-class** object, and `classOf` on the instance added by the typed tool reads **`ConformSpaceWarp`**. `SpaceConform` is the modifier-class counterpart; it constructs and is the one that attaches via `addModifier`. `3dsmax-mcp_add_modifier` also accepts `Conform`, returning `Added Conform Object`. So: use `SpaceConform` on the modifier stack, and treat `Conform` as a scene-object spacewarp that cannot be built with a bare constructor. |
| **Box / Real-World UVW Mapping** | `Uvwmap` | `maptype` (`0`=Planar, `1`=Cylindrical, `2`=Spherical, `3`=Shrink Wrap, `4`=Box, `5`=Face, `6`=XYZ to UVW), `length`, `width`, `height`, `utile`, `vtile`, `wtile`, `realWorldMapSize` (bool), `mapChannel` (int, `1`). |
| **Flip / Unify Normals** | `Normalmodifier` | `flip` (bool), `unify` (bool) — note class name is `Normalmodifier`, not `Normal`! **VERIFIED 2026-10-04:** both properties exist, measured `flip=false` and `unify=false` on a fresh `Box`. Attaches with `addModifier`. Correct as documented. |
| **Noise (Terrain / Water Ripple)** | `Noisemodifier` | `seed`, `scale`, `fractal` (bool), `roughness`, `iterations`, `strength` (`point3`, e.g. `[0, 0, 45]`) — note class name is `Noisemodifier` (`Noise` is a texture map!). |
| **Clean Quad Retopology** (Max 2021+) | `RetopologyComponent` | **2026-10-04 — only 1 of 3 original parameters exists.** `engineType` (int, measured `0`) is real. ~~`numFaces` (target quad count)~~ → **`NO`**; ~~`autoEdge` (bool)~~ → **`NO`**. Eight further candidates were probed and all returned `NO` (`targetQuadCount`, `quadCount`, `faces`, `edgeLength`, `autoEdges`, `symmetry`, `engine`, `retopologyType`), so **the target-count and auto-edge controls are UNVERIFIED — the "clean quad retopology" workflow as written cannot be driven.** The class itself constructs fine. Compute via `.ComputeRetopology()` (not re-verified this pass). |

---

## 2. Procedural Facades with Data Channel (`add_data_channel`)

Read `procedural-graphs.md` before building Data Channel stacks. Data Channel is non-destructive and ideal for:
1. **Sun-Responsive / Attractor-Driven Kinetic Facade Panels:**
   - Use an **Element** or **Face** input, remap with `scale` / `curve` / `clamp`, and output to `vertex_output` or a Face Material ID / UVW.
2. **Height-Driven Material ID Assignment on High-Rise Facades:**
   - Stack:
     1. `vertex_input` (Z component of the `Position` attribute — see the note below, `Position` is **not** an operator)
     2. `normalize` / `scale`
     3. `convert_subobject` (Vertices $\rightarrow$ Faces)
     4. `face_output` (`Material ID`) — assigns podium, mid-rise, and crown Material IDs by elevation.
3. **Curvature-Driven Weathering / Edge Wear Mask:**
   - Output `curvature` to Vertex Color or Map Channel 2 to drive dirt/moss shaders on exterior concrete and stone cornices.

### 2.1 2026-10-04 — the operator vocabulary in this section was WRONG

**Every operator name below was wrong, and two of them did not exist at all.** The original
text used Max UI *display* names; the tool requires **snake_case** identifiers. Values are
**lowercased**, so `{"type": "Position"}` fails with `Unknown operator type: position`.

**Also wrong: the operator key is `type`, not `name`.** Passing `name` yields
`Unknown operator type: .` (the value arrives empty).

**The complete real vocabulary — 32 operators, snake_case** (obtained by asking
`3dsmax-mcp_add_data_channel` for a nonexistent operator, which returns the full list):

```
clamp, color_elements, color_space, component_space, convert_subobject, curvature, curve,
decay, delta_mush, distort, edge_input, edge_output, expression_float, expression_point3,
face_input, face_output, geo_quantize, invert, maxscript, maxscript_process,
node_influence, normalize, point3_to_float, scale, smooth, tension_deform,
transform_elements, vector, velocity, vertex_input, vertex_output, xyz_space
```

**Name corrections, claim by claim:**

| original claim | verdict |
| :--- | :--- |
| `Vertex Input` | **`vertex_input`** |
| `Face Output` | **`face_output`** |
| `Vertex Output` | **`vertex_output`** |
| `Convert To SubObject Type` | **`convert_subobject`** |
| `Normalize` / `Scale` / `Curve` / `Clamp` | `normalize` / `scale` / `curve` / `clamp` — all exist |
| `Curvature` | `curvature` — exists |
| **`DistToNode`** | **NOT IN THE VOCABULARY. This claim was wrong.** No node-distance input operator exists in this build. |
| **`FaceArea`** | **NOT IN THE VOCABULARY. This claim was wrong.** Recipe 1 above depended on it and has been rewritten to stop naming it. |
| `Position` | **Not an operator at all** — it is an **attribute of `vertex_input`**, not a graph node. Recipe 2 above has been corrected accordingly. |

**Working call, executed:**

```
3dsmax-mcp_add_data_channel(name="DCTEST", operators=[{"type":"vertex_input"},{"type":"scale"}])
→ {"modifier": "Data Channel", "operators": 2, "order": "#(0, 1)", "object": "DCTEST"}
```

`3dsmax-mcp_inspect_data_channel` on the result:

```json
{"object":"DCTEST","display":true,"order":"#(0, 1)","blend_modes":"#(1, 1)",
 "operators":[{"index":1,"class":"Operator_VertexInput","enabled":true,"frozen":false,
               "input":"0","Internal":"1","xyz":"0"},
              {"index":2,"class":"Operator_Scale","enabled":true,"frozen":false,"scale":"1.0"}]}
```

Real Data Channel class names, for reference: `Operator_VertexInput`, `Operator_Scale`.

**`3dsmax-mcp_list_dc_presets` returns `[]`** in this build — there are no Data Channel
presets available. Do not plan around a preset lookup.

### 2.2 The "CRITICAL Max 2027 Rule" — RETRACTED as unverified

This section previously carried:

> **CRITICAL Max 2027 Rule:** explicitly set the first Input operator's `operator_ops` entry
> to `1` (Replace) or the graph stays unevaluated!

**Retracted. Three separate reasons, all measured:**

1. It **cannot be tested here.** The rule is scoped to **Max 2027**; this installation is
   **3ds Max 2026.3.2**.
2. The field name is **wrong.** The per-operator field the inspector exposes is named
   **`Internal`**, not `operator_ops`. (It read `1` in the executed graph above.)
3. **No manual intervention was needed.** The graph in §2.1 was built with nothing but the
   two operators, and `blend_modes` already read **`#(1, 1)`**. The claimed failure mode —
   a graph that "stays unevaluated" — did not occur.

The observation that survives, stated neutrally: the inspector reports a per-operator
`Internal` field, and `blend_modes` read `#(1, 1)` on a freshly built two-operator graph. Any
assertion that this field *must* be set by hand is **UNVERIFIED** and should not be relied on.

---

## 3. Custom Parametric Architecture with Max Creation Graph (`mcg_*`) — NOT AVAILABLE

> **2026-10-04 — this entire section is retracted. Its premise is false.**
>
> **There is no `mcg_*` tool in the connected MCP toolset.** None of `mcg_get_context`,
> `mcg_list_graphs`, `mcg_create_graph` or `mcg_apply_patch` is present. This was established
> by **direct inspection of the live tool list**, so it is definitive rather than inferred —
> this is not "not yet implemented", it is **not exposed by this bridge**.
>
> **`curve_model` is also not in the toolset.** The previous version of this section named it
> twice, and — worse — recommended it as the script-free fallback for `Bevel_Profile`, which §1
> shows is itself unusable. **The old text therefore recommended a nonexistent tool in place of
> a class that does not work.** Both problems are removed here rather than patched around.

### What this means in practice

When the user asks for a reusable **parametric architectural generator or modifier** — a
procedural louvered facade, a parametric stair generator, a perforated metal screen — **no MCG
workflow can be driven from this bridge.** Do not begin one. Do not plan around
`mcg_create_graph`, and do not fall back to `curve_model`.

The recipe previously listed here (parametric multi-storey shell from a ground spline, via
`QuadMesh from Extruded Points`, `ToTriMesh`, and `Mesh Extrude All Polygons`) is **kept only as
unverified architectural background.** It is **not** an executable recipe through this toolset,
and its inner node names and parameter names (`direction`, `segmentCount`,
`inset`, `depth`, `materialId`, the `Parameter: INode` / `Parameter: Single` / `Parameter:
Int32` ports) were **never executed and are not verified**. Note also that `direction` is the
name this document got wrong on the `Lathe` modifier (§1) — do not carry that assumption across
node types without measuring.

### Build it another way

For parametric architecture from this bridge, use the surfaces that *were* measured:

- MAXScript primitives and shapes, then modifiers from §1 — observing the `addModifier` /
  `3dsmax-mcp_add_modifier` split documented there.
- **Data Channel** (§2) for non-destructive per-vertex and per-face procedural drives.
- Direct `3dsmax-mcp_execute_maxscript` loops for repetition and instancing, generating
  parameters in the script rather than in a node graph.

That is a different architecture from MCG, and it is a limitation of the bridge, not a
substitute design to be preferred. If MCG is genuinely required, say so rather than
improvising around it.
