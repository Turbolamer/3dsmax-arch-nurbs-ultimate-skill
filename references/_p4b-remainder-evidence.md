# Evidence brief — P4b remainder, claim-by-claim verification

**Status: executed transcripts. This file is DATA, not conclusions.**
Produced by the orchestrator against live 3ds Max **2026.3.2** via `3dsmax-mcp_execute_maxscript`
and the typed `3dsmax-mcp_*` tools. Bridge transport `namedpipe`, protocol 2, `safeMode: true`.

Environment: `references/maxscript-splines-shapes.md` and
`references/arch-modifiers-and-procedural-reference.md` are the two files to correct.
Nothing below is inferred unless it says INFERENCE.

---

## 0. The two methodological findings that made this cheap

### 0.1 `isProperty <obj> <name>` is a calibrated existence test for built-in classes

Calibration batch (same call, both controls present):

```
CAL_neg=false      -- isProperty circle "totalBogusXYZ"
CAL_pos=true       -- isProperty circle "render_thickness"
CAL_pos2=true      -- isProperty circle "steps"
```

### 0.2 `getProperty <obj> (<string> as name)` is a valid DYNAMIC read — and this
### contradicts an existing CHECKPOINT row

```
getProperty gTestArc #radius      -> 40.0
("steps" as name) coercion        -> OK
```

`references/CHECKPOINT.md` §"NURBS surfaces and grids" records
*"`getProperty o #x` also fails"*. That is **true for the NURBS plugin classes and false for
built-in classes**. Same for `o["name"]` bracket access, which returns `undefined` (does not
throw) rather than erroring. **Both rows need narrowing, not deletion.**

### 0.3 `execute` DOES work — three earlier "failures" were `"string" + number` type errors

`execute "1+1"` appears to fail when its result is concatenated with a string. It is not
`execute` that fails, it is `"prefix" + 2`. **Always wrap: `(execute code) as string`.**
This matters because a *bogus* expression still throws, so `execute` is the correct way to
test many candidate names in a loop with a real negative control.

### 0.4 Things that do NOT work in this bridge — do not retry

| Construct | Result |
|---|---|
| `getCurrentException()` inside a `catch` | itself throws; makes a catchable error escape as a script abort |
| `global fn name args = (...)` | parse error |
| `local function name args = (...)` | parse error. Use `local fn name args = (...)` |
| `modPanel.setCommandPanelCurrentMode #modify` | throws — no UI panel available |
| `modPanel.addModToSelection (...)` | returns OK but **silently adds nothing** (`modifiers.count` stays 0) |
| `isInstanceOf inst <an instance>` | "Call needs function or class, got: undefined" |

---

## 1. `maxscript-splines-shapes.md` — §1 shape constructors: **FULLY VINDICATED**

Every documented constructor was built **and its keywords were read back**. Not one error.

| constructor | read-back |
|---|---|
| `circle radius:50` | `radius=50.0` |
| `arc radius:40 from:0 to:180 pie:false reverse:false` | `radius=40.0 from=0.0 to=180.0 pie=false reverse=false` |
| `ellipse length:30 width:50` | `length=30.0 width=50.0` |
| `rectangle length:40 width:60 cornerRadius:5` | `length=40.0 width=60.0 cornerRadius=5.0` |
| `star radius1:25 radius2:12 points:6 distort:0 fillet1:0 fillet2:0` | `radius1=25.0 radius2=12.0 points=6 distort=0.0 fillet1=0.0 fillet2=0.0` |
| `ngon radius:30 nSides:8 scribe:0 circular:true corner_Radius:0` | `radius=30.0 nSides=8 scribe=0 circular=true corner_Radius=0.0` |
| `donut radius1:35 radius2:25` | `radius1=35.0 radius2=25.0` |
| `helix radius1:35 radius2:15 height:100 turns:3 bias:0 direction:0` | `radius1=35.0 radius2=15.0 height=100.0 turns=3.0 bias=0.0 direction=0` |
| `text font:"Arial" size:100 text:"Hello" kerning:0 leading:0 alignment:1` | `font=Arial size=100.0 text=Hello kerning=0.0 leading=0.0 alignment=1` |
| `section pos:[0,0,50] length:200 width:200` | `pos=[0,0,50] length=200.0 width=200.0` |
| `line()` | `class=line super=shape` |

`superClassOf circle` = `shape`, `classOf` = `Circle`.

**Note on `Arc`:** the property names are `from` / `to`, NOT `from_angle` / `to_angle`. The
document's *code* is right; only a reader trying to read the value back would guess wrong.

**`star.points` caveat is unnecessary:** both `star.points` and `star.baseobject.points` read
`6` on the node. The documented caution does no harm — just record that it was not reproducible.

### 1.1 Shared interpolation properties — **VINDICATED, exact defaults**

```
circle radius:50  ->  steps=6  optimize=true  adaptive=false
```

Matches the document's stated defaults character for character.

---

## 2. `maxscript-splines-shapes.md` — `bezierShape()` is **effectively unusable**

`bezierShape()` constructs and reports `class=SplineShape super=shape`. But **`updateShape`
on it throws**, at every knot count tried:

| knots tried | result |
|---|---|
| 2 × `#corner #line` | `updateShape: curve with insufficient knots, knots added: Editable Spline` |
| 3 × `#corner #line` | same throw; `numSplines` had become `2` |
| 4 × `#smooth #curve` | same throw |

`plain splineShape()` with 2 knots updates fine. The document says
`ss = bezierShape() -- same thing`. **It is not the same thing.**

### 2.1 A REAL `splineShape()` trap the document does not mention

`updateShape` throws `curve with insufficient knots` when **any spline in a multi-spline shape
has only 2 knots**:

| shape | result |
|---|---|
| 1 spline, 2 knots | OK |
| spline 1 = 3 knots, spline 2 = **2 knots** | **THROWS** |
| spline 1 = 3 knots, spline 2 = **3 knots** | OK |

**Give every spline ≥3 knots before `updateShape`.**

---

## 3. `maxscript-splines-shapes.md` — spline / knot / segment methods: **all verified**

Built on a 3-knot `#corner #line` L-shape `[0,0,0] → [100,0,0] → [100,100,0]`,
`curveLength` = `200.0`.

| claim | measured |
|---|---|
| `numSplines`, `numKnots <sh> <i>`, `numKnots <sh>`, `numSegments`, `isClosed` | all work |
| **`numSegments == numKnots` closed, `numKnots - 1` open** | **exactly true**: open 3 knots → 2 segments; `close` → 3 knots / 3 segments; `open` → 2 segments |
| `getKnotPoint` / `setKnotPoint` | `[100,50,0]` → set `[120,60,0]` → read `[120,60,0]` |
| `getKnotType` / `setKnotType` | `corner` → set `#smooth` → read `smooth` |
| `getInVec` / `setInVec` / `getOutVec` / `setOutVec` | after `setKnotType ... #bezier`, handles are **auto-computed non-zero** (`[20,10,6.667]`); setting `[-10,10,0]` / `[10,-10,0]` read back exactly. **Handles are absolute positions — confirmed** |
| `getSegmentType` / `setSegmentType` | work |
| `deleteSpline` | `numSplines` 2 → 1 |
| `setFirstSpline` | works (observable: the swapped spline becomes index 1) |
| `setFirstKnot` | works |
| `reverse` | works (knot 1 flipped from `[0,0,0]` to `[100,100,0]`) |
| `setKnotSelection` / `getKnotSelection` | `#(1)` |
| `setSplineSelection` / `getSplineSelection` | `#(1)` |
| `setSegSelection` / `getSegSelection` | `#(1)` |
| `setMaterialID` / `getMaterialID` | wrote `7`, read `7` |
| `subdivideSegment <sh> <i> <seg> 2` | knots 3 → 5 |
| `refineSegment <sh> <i> <seg> 0.5` | knots 5 → 6 |
| `resetShape` | `numSplines` → `0` |
| `addAndWeld <to> <from> 5.0` | OK |
| `weldSpline <sh> 5.0` | OK; **type-checked** — `weldSpline gA #bogus` THROWS |
| `applyOffset <sh> 10.0` | returns `true` |
| `measureOffset <sh> [50,50,0]` | `31.6228` (signed distance) |
| `animateVertex <sh> #all` | OK |
| `convertToSplineShape circle` | `class=SplineShape numSplines=1 nKnots=4` — **exactly the document's claim** |
| `createSplineFromPoints` fn from the doc | works; 37 knots, open and closed variants both fine |

### 3.1 CORRECTION — `setKnotType ... #bezierCorner` silently fails **on knot 1 only**

| target | result |
|---|---|
| knot 1 | call returns OK, `getKnotType` still reads **`corner`** — silent no-op |
| knot 2 | `getKnotType` reads **`bezierCorner`** — works |

`#smooth` and `#bezier` both work on knot 1. The first knot specifically rejects
`#bezierCorner` without an error.

### 3.2 CORRECTION — `getSegLengths` return shape is not what the signature implies

For a **2-segment** spline, `getSegLengths sh 1` returned **five** values:

```
#(0.657467, 0.342533, 134.36, 70.0, 204.36)
```

i.e. cumulative params, then per-segment lengths, then the total `204.36` — which matches
`curveLength sh 1` = `204.36`. The documented signature
`getSegLengths <shape> <spline_idx> [cum] [byVertex] [numArcSteps:100]` is accepted but the
**return shape is undocumented**. Never index it positionally.

### 3.3 CORRECTION — the `pathParam` keyword is TYPE-CHECKED but **INERT**

Same L-shape, `interpCurve3D sh 1 0.5`:

| call | result |
|---|---|
| `interpCurve3D sh 1 0.5` | `[100,0,0]` |
| `... pathParam:true` | `[100,0,0]` |
| `... pathParam:false` | `[100,0,0]` |
| `... pathParam:#bogus` | **THROWS** (so the keyword is real) |
| `pathInterp sh 1 0.5` | `[100,0,0]` — identical |
| `lengthInterp sh 1 0.5` | `[100,0.199425,0]` — **measurably different** |

The document's comment *"`pathParam:false` = length-based (uniform), `pathParam:true` =
vertex-based"* is **not supported**. The flag is accepted and validated and then changes
nothing. To get length-based evaluation use **`lengthInterp` / `lengthTangent`**; to get
path/vertex-based use **`pathInterp` / `pathTangent` / `interpCurve3D` / `tangentCurve3D`**.

### 3.4 Path interpolation — all 14 functions exist and work

`interpCurve3D` · `tangentCurve3D` (`[0.707107,0.707107,0]`, normalised) ·
`interpBezier3D` (`[50,0,0]`) · `tangentBezier3D` (`[1,0,0]`) ·
`findPathSegAndParam` (`[1,1]`, a point2 as documented) ·
`findLengthSegAndParam` (`[1,1]`) · `pathInterp` · `lengthInterp` · `pathTangent` ·
`lengthTangent` · `nearestPathParam` · `pathToLengthParam` · `lengthToPathParam` ·
`resetLengthInterp`.

Two values worth recording because they do **not** match naive expectation:
`nearestPathParam sh 1 [50,50,0]` returned **`0.25`**, although the nearest point on that L is
the corner at path param `0.5`. `pathToLengthParam 0.5` → `0.499997`,
`lengthToPathParam 0.5` → `0.500997`. **Do not assert exact values from these.**

---

## 4. `maxscript-splines-shapes.md` — rendering properties: **VINDICATED, all 15**

On `circle radius:50`:

```
render_renderable=false  render_displayRenderMesh=false  render_useViewportSettings=false
render_thickness=1.0     render_sides=12                   render_angle=0.0
render_rectangular=false render_length=6.0                render_width=2.0
render_angle2=0.0        render_viewport_thickness=1.0    render_viewport_sides=12
render_mapcoords=false   render_auto_smooth=true          render_threshold=40.0
totalBogusXYZ=NO
```

`addModifier c (Renderable_Spline())` works; `.modifiers[#Renderable_Spline]` then reads and
writes `renderable`, `thickness` (→3.0) and `sides` (→8). Note `render_viewport_sides`
**defaults to 12, not the 8 used in the doc's example** — the doc never claimed a default, so
this is not an error, but state the default if you state one.

---

## 5. `maxscript-splines-shapes.md` — `splineOps`: **all 27 VERIFIED**

Shape selected, `subobjectLevel = 1`, each called through `execute`:

```
startCreateLine=OK  startBreak=OK  startAttach=OK  attachMultiple=OK  startRefine=OK
weld=OK  startConnect=OK  startInsert=OK  makeFirst=OK  fuse=OK  reverse=OK  close=OK
delete=OK  divide=OK  detach=OK  explode=OK  startFillet=OK  startChamfer=OK
startOutline=OK  startTrim=OK  startExtend=OK  startUnion=OK  startSubtract=OK
intersect=OK  mirrorHoriz=OK  mirrorVert=OK  mirrorBoth=OK
startBogusXYZ=THROW        <-- negative control
```

Zero corrections needed.

---

## 6. `maxscript-splines-shapes.md` — misc patterns

| claim | measured |
|---|---|
| `sin` takes **degrees** | `sin 90` = `1.0`, `sin 0` = `0.0` — the doc's `[i, sin(i)*50, 0]` for `i = 0..360` is correct as written |
| `point pos:[10,20,30] size:5` | `pos=[10,20,30] size=5.0` |
| `instance <node>` + `.pos` + `.dir` | `pos=[50,0,0] dir=[0,0,1]`, both nodes stay valid |
| **`delete <base>` does not delete its instances** | after `delete bx`, the instance `Box002` survived. Same rule already recorded for dummies |

---

## 7. `arch-modifiers-and-procedural-reference.md` — §1 class table

### 7.1 All 23 classes construct (bogus control throws) — but 6 of them **cannot be
### attached via MAXScript `addModifier`**

Constructor sweep, control `TotalGarbageXYZ123` → `THROW`:

```
Extrude=OK:Extrude        Sweep=OK:sweep          Shell=OK:Shell
ChamferMod=OK:Chamfer     Lathe=OK:Lathe          Lattice=OK:Lattice
CrossSection=OK:CrossSection   Surface=OK:surface    Symmetry=OK:symmetry
SliceModifier=OK:SliceModifier  Bend=OK:Bend       Twist=OK:Twist
Taper=OK:Taper            FFD_2x2x2 / FFD_3x3x3 / FFD_4x4x4 = OK
SpaceConform=OK:SpaceConform    Uvwmap=OK:Uvwmap    Normalmodifier=OK:Normalmodifier
Noisemodifier=OK:Noisemodifier   RetopologyComponent=OK:RetopologyComponent
Bevel_Profile=OK:Bevel_Profile
Conform=THROW             <-- the ONLY class whose 0-arg constructor throws
TotalGarbageXYZ123=THROW  <-- negative control
```

**Three class-name corrections.** The document's names *construct*, but `classOf` reports a
different real name:

| doc name | real `classOf` |
|---|---|
| `ChamferMod` | **`Chamfer`** |
| `Symmetry` | **`symmetry`** (lower case) |
| `Surface` | **`surface`** (lower case) |

### 7.2 The document's central instruction is WRONG for 6 of 23 modifiers

The file says *"always use the exact MAXScript class name … below"* for
`add_modifier(name=, modifier=, params=)`. Measured: `addModifier <node> <ctor>()` succeeds for
16 and **throws for `Extrude`, `Sweep`, `Lathe`, `Surface`, `CrossSection`, `Bevel_Profile`**,
even though all six construct fine standalone. `modPanel.addModToSelection` is not a way
around it — it returns OK and adds nothing (§0.4).

**The typed MCP tool `3dsmax-mcp_add_modifier` DOES work for them.** Executed on a `Box001`:

| `modifier` argument | tool result |
|---|---|
| `Extrude` | `Added ExtrudeMod to Box001` (resulting `classOf` is `Extrude` — "ExtrudeMod" is only the tool's display string) |
| `Sweep` | `Added Sweep to Box001` |
| `Lathe` | `Added Lathe to Box001` |
| `Surface` | `Added Surface to Box001` |
| `CrossSection` | `Added CrossSection to Box001` |
| `Conform` | `Added Conform Object to Box001` → `classOf` = **`ConformSpaceWarp`** |
| `Bevel_Profile` | **FAILS**: `Unable to convert: Bevel_Profile to type: Modifier` |

So the rule is: **use `3dsmax-mcp_add_modifier`, not a hand-written MAXScript
`addModifier`, for `Extrude` / `Sweep` / `Lathe` / `Surface` / `CrossSection` / `Conform`.**
`Bevel_Profile` is unusable through either route in this build.

Note `Conform` is a **spacewarp-class** object (`ConformSpaceWarp`); the modifier-class
counterpart `SpaceConform` is the one that attaches with `addModifier`.

---

## 8. `arch-modifiers-and-procedural-reference.md` — §1 parameter names

Every list below was probed with `isProperty` **plus a known-positive and a `totalBogusXYZ`
negative in the same call**. `NO` = the name does not exist.

### 8.1 FULLY CORRECT — no change needed

| modifier | verified params |
|---|---|
| `Extrude` | `amount=0.0 segs=1 capStart=true capEnd=true capType=0 mapCoords=false matIDs=true` — all 7 exist, `segs` default 1 as documented |
| `Sweep` (`sweep`) | `current_built_in_shape CustomShape SmoothPath SmoothSection Banking GenMatIDs` all exist |
| `Uvwmap` | `maptype=0 length=210.732 width=210.732 height=111.155 utile=1.0 vtile=1.0 wtile=1.0 realWorldMapSize=false mapChannel=1` — all 9 |
| `Noisemodifier` | `seed=0 scale=100.0 fractal=false roughness=0.0 iterations=6.0 strength=[0,0,0]` — all 6, and **`strength` really is a point3**, as claimed |
| `SliceModifier` | `Slice_Type=0 Cap=false` — both |
| `symmetry` | `axis=0 flip=false` exist; `slice` and `weld` exist but are **integers** (`1`), not booleans |

### 8.2 PARTLY WRONG — correct these

| modifier | claim | measured |
|---|---|---|
| `Shell` | `innerAmount`, `outerAmount`, `segs`, `straightenCorners`, `overrideEdgeMatID`, `edgeMatID` | `innerAmount=0.0 outerAmount=1.0 straightenCorners=false` exist. **`segs`, `overrideEdgeMatID`, `edgeMatID` → `NO`. 3 of 6 wrong** |
| `Chamfer` | `amount`, `segments`, `tension`, `mitering`, `limitEffect`, `minAngle` | `amount=1.0 segments=1 tension=1.0 limitEffect=false minAngle=20.0` exist. **`mitering` → `NO`.** `tension` default is `1.0` (flat), `minAngle` default `20.0` |
| `Lattice` | `Strut_Radius`, `Strut_Segments`, `Strut_Sides`, `Joint_Type`, `Both`, `Ignore_Hidden_Edges` | `Strut_Radius=2.0 Strut_Segments=1 Strut_Sides=4` exist (`Strut_Sides` default 4 matches "4 for rectangular mullions"). **`Joint_Type`, `Both`, `Ignore_Hidden_Edges` → all `NO`. 3 of 6 wrong — and they are the load-bearing ones for the mullion recipe** |
| `Lathe` | `direction` (`0`=X, `1`=Y, `2`=Z) | **`direction` → `NO`.** The real property is **`axis`**, and it is a **`matrix3`**, not an integer enum: `matrix3 [1,0,0] [0,-1.62921e-07,-1] [0,1,-1.62921e-07] [0,0,0]`. `degrees=360.0 segs=16 flipNormals` all exist |
| `RetopologyComponent` | `numFaces`, `engineType`, `autoEdge` | **`engineType=0` exists. `numFaces` and `autoEdge` → `NO`.** 8 further candidates all `NO` (`targetQuadCount quadCount faces edgeLength autoEdges symmetry engine retopologyType`) |
| `Sweep` | "`PivotAlignment` (`0..8`)" | `PivotAlignment` exists but reads **`-1`**, not `0..8` |

### 8.3 NOT FOUND — record as UNVERIFIED, do not invent

| modifier | doc claims | status |
|---|---|---|
| `Surface` (`surface`) | `threshold`, `steps`, `flip`, `remove_interior_patches` | `threshold=1.0` and `steps=5` **exist**. `flip` and `remove_interior_patches` → `NO`. 8 further candidates all `NO` (`flipNormals reverse removeInteriorPatches remIntPatches deleteInterior smooth output surfaceMethod mapTile`). **The real names are UNVERIFIED** |
| `CrossSection` | `spline_type` (`0`=Linear, `1`=Smooth, `2`=Bezier) | `spline_type` → `NO`; `splineType type crossSectionType` also `NO`. Class exists and attaches. **Real names UNVERIFIED** |

### 8.4 `Bend` / `Twist` / `Taper` — correct, with two corrections

```
Bend : BendAngle=0.0 BendDir=0.0 BendAxis=2 FromTo=false      Low=NO  High=NO
Twist: angle=0.0 bias=0.0 axis=2
Taper: amount=1.0 curve=0.0 primaryAxis=2 effectAxis=2
```

`Low` / `High` do not exist as properties on `Bend` (they are `FromTo`-gated UI fields).
`BendAxis` / `axis` / `primaryAxis` / `effectAxis` default to **`2`**, not `0`.

### 8.5 `FFD_*` — the documented control-point claim is NOT reproducible

`FFD_3x3x3` attaches fine. `control_point_1` and `control_point_10` → **`NO`** on the modifier.
The document says *"Animate/move control points (`animateAll <ffdMod>`, then
`.control_point_1 ...`)"*. **UNVERIFIED — record as such.** (`animateAll` itself untested.)

---

## 9. `arch-modifiers-and-procedural-reference.md` — §2 Data Channel: **the operator
## vocabulary in the document is wrong**

`3dsmax-mcp_list_dc_presets` returns **`[]`** — there are no presets in this build.

Asking `3dsmax-mcp_add_data_channel` for a nonexistent operator returns the **complete real
vocabulary — 32 operators, snake_case**:

```
clamp, color_elements, color_space, component_space, convert_subobject, curvature, curve,
decay, delta_mush, distort, edge_input, edge_output, expression_float, expression_point3,
face_input, face_output, geo_quantize, invert, maxscript, maxscript_process,
node_influence, normalize, point3_to_float, scale, smooth, tension_deform,
transform_elements, vector, velocity, vertex_input, vertex_output, xyz_space
```

**Tool schema correction:** the operator key is **`type`**, not `name`. `name` yields
`Unknown operator type: .` Values are lowercased and must be snake_case
(`{"type": "Position"}` → `Unknown operator type: position`).

**Working call, executed:**
`3dsmax-mcp_add_data_channel(name="DCTEST", operators=[{"type":"vertex_input"},{"type":"scale"}])`
→ `{"modifier": "Data Channel", "operators": 2, "order": "#(0, 1)", "object": "DCTEST"}`

`3dsmax-mcp_inspect_data_channel` then returned:

```json
{"object":"DCTEST","display":true,"order":"#(0, 1)","blend_modes":"#(1, 1)",
 "operators":[{"index":1,"class":"Operator_VertexInput","enabled":true,"frozen":false,
               "input":"0","Internal":"1","xyz":"0"},
              {"index":2,"class":"Operator_Scale","enabled":true,"frozen":false,"scale":"1.0"}]}
```

### 9.1 Per-claim verdicts

| document claim | verdict |
|---|---|
| `Vertex Input` | name is **`vertex_input`** |
| `Face Output` | **`face_output`** |
| `Vertex Output` | **`vertex_output`** |
| `Convert To SubObject Type` | **`convert_subobject`** |
| `Normalize` / `Scale` / `Curve` / `Clamp` | `normalize` / `scale` / `curve` / `clamp` — all exist |
| `Curvature` | `curvature` exists |
| **`DistToNode`** | **NOT in the vocabulary. The claim is wrong** |
| **`FaceArea`** | **NOT in the vocabulary. The claim is wrong** |
| `Position` (as an operator) | not an operator; it is an attribute of `vertex_input`, not a graph node |
| **"CRITICAL Max 2027 Rule"** — set the first Input operator's `operator_ops` to `1` (Replace) or the graph stays unevaluated | **UNVERIFIED on 2026.3.2.** The graph built with **no** manual intervention and `blend_modes` already read `#(1, 1)`; the per-operator field the inspector exposes is named **`Internal`**, not `operator_ops`, and it read `1`. The rule is also scoped to "Max 2027" while this installation is 2026.3.2, so it **cannot be tested here**. Record as unverified and drop "CRITICAL" |

Real Data Channel class names, for reference: `Operator_VertexInput`, `Operator_Scale`.

---

## 10. `arch-modifiers-and-procedural-reference.md` — §3 MCG and `curve_model`: both
## routes to nonexistent tools

The connected MCP toolset contains **no `mcg_*` tool** — none of `mcg_get_context`,
`mcg_list_graphs`, `mcg_create_graph`, `mcg_apply_patch` is present. This is a **direct
inspection of the live tool list**, so it is definitive rather than inferred.

Likewise **`curve_model` is not in the toolset.** It is named twice in the document, including
as the recommended fallback for `Bevel_Profile` — which §7.2 shows is itself unusable. So the
document currently recommends a nonexistent tool *in place of* a class that does not work.

---

## 11. NEW HAZARD discovered during this work — Chaos Scatter + heavy modifier stacks
## CRASH 3ds Max

While a **20-modifier stack** was assembled on one `Box` primitive in a single
`execute_maxscript` call, **two** modal dialogs appeared:

```
MAXScript Callback script Exception
-- Known system exception
-- Address: 0x725125d; nCode: 0x00000000C0000005
-- Desc: EXCEPTION_ACCESS_VIOLATION The thread tried to read from or write to a
        virtual address for which it does not have the appropriate access.
-- Read of Address: 0x0000000000000000
-- File name: C:\Program Files\Autodesk\3ds Max 2026\stdplug\tstdcripts\MassFX\px_modifierClothing.ms
-- Line number: 7
```

Observed fact: two such dialogs; the scene held 20 modifiers on one node; **no ChaosScatter
object existed in the scene**; the bridge stayed responsive and the node was deleted normally
afterwards (scene back to `objects.count = 0`).

**INFERENCE (not measured):** `px_modifierClothing.ms` is a Chaos Scatter callback that hooks
geometry-stack changes, and it dereferenced a null pointer while the stack was mutating. The
attribution to "20 modifiers at once" is plausible but **not isolated by experiment.**

Either way this is a **P6 hazard worth writing down**: Chaos Scatter is the user's only
working scatter route, and the failure mode is a hard process crash, not a wrong result.
Practical rule: build modifier stacks incrementally, and never assemble a stack of this size
in one scripted call.

---

## 12. Instructions for the correcting agent

1. **Correct only what this brief marks wrong.** The same rule that let `nurbs-complete-guide.md` /
   `nurbs-architecture-recipes.md` survive P4b:
   these files are **unverified, not disproven**. Nothing here licenses a rewrite.
2. For each correction, keep the original text visible — add a dated correction note or strike
   the wrong value — so a reader who remembers the old claim finds out it was wrong.
3. Anything this brief could not settle must be labelled **UNVERIFIED**, never deleted and
   never guessed. Specifically UNVERIFIED: the real `Surface`/`CrossSection` parameter names,
   the FFD control-point access route, the Data Channel "Max 2027" rule, and `animateAll`.
4. Do **not** invent replacement names for the `NO` rows. `Lattice`'s `Both`/`Joint_Type` are
   load-bearing for the mullion recipe — if the real names are unknown, say the recipe is
   unverified rather than guessing.
5. The Chaos Scatter crash (§11) belongs in the **hazard** documentation, not in these two
   files.