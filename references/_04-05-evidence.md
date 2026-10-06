# P4b-c Evidence — claim-by-claim verification of the two NURBS reference files

Target files (ownership): `references/nurbs-complete-guide.md`, `references/nurbs-architecture-recipes.md`.
Host: 3ds Max 2026.3.2 via `3dsmax-mcp_execute_maxscript`, 2026-10-06.
Bridge: `get_bridge_status` → `pong:true`, protocol 2, RTT 0.37 ms, transport `namedpipe`. Live throughout.

**Probe standard used for every batch.** Each batch carried a known-positive control and
`TotalGarbageXYZ_fn(1)` / `TotalGarbageXYZ_fn()` as a known-bogus control. Three different
existence discriminators were used, and each was calibrated before its result was believed:

| Discriminator | Positive control result | Bogus control result |
|---|---|---|
| `execute "<name>()"` → `threw=` / `undef=` | all 40 documented class names construct | throws, `undef=true` |
| `execute "<fn>()"` → error text | real fns → `Argument count error` or a native `EXCEPTION_ACCESS_VIOLATION` (both mean *found and invoked*) | `Type error: Call needs function or class, got: undefined` |
| `isProperty <obj> "<name>"` | every documented property → `true` | every class → `false` for `bogusZZ` |

**A throw was never treated as evidence of absence.** Three candidate defects were re-probed with a
direct guarded read (`getProperty`) plus a positive control before being believed — one of them
(`NURBSPointCurve.closed`) initially looked like an `isProperty` false negative and had to be
discarded and re-measured, exactly as `AGENTS.md` warns.

**Limits respected.** No modifier stack was ever built (so the 20-rung freeze boundary was never
approached). Every script ran on the main thread, well under 2 s. Every batch deleted its own test
nodes and printed `objects.count` at start and end. Scene was `0` objects before and after every
single batch. No Rhino-server tool names were called.

**Scripting traps discovered while probing (not claims of the target files):**
- `max modify mode` is a **parse error** through `execute` — same family as the known `max zoomext`.
- `parentID:surf.nurbsID` is a parse error; the kwarg value must be parenthesised: `parentID:(surf.nurbsID)`.
- Two consecutive `if ... then` statements inside a `for` body parse fine, but `if ... do` followed
  by another `if ... do` in the same body triggered repeated parse errors. Use the `then` form.
- `local function f` is not valid; use `fn`.

---

## Claim list extracted from the two files

Numbers are stable identifiers for this file only.

### nurbs-complete-guide.md

| # | Claim | Where |
|---|---|---|
| G01 | All 17 NURBS identifiers resolve and construct | L14, throughout |
| G02 | `classOf node == NURBSSurf` or `CV_Surf` or `Point_Surf` or `Point_Curve`/`CV_Curve`; internal ID `EDITABLE_SURF_CLASS_ID` | L13 |
| G03 | `appendObject` / `NURBSNode` construction route | L16 |
| G04 | `stopCreating` takes zero args | L17, §5.2, §6.1 |
| G05 | `getNURBSSet <node> #relational` | L17 |
| G06 | `addNURBSSet <node> <nurbsSet>` appends a new set into the node | L18, §5.2, §5.3 |
| G07 | Uninstantiated set: `.nurbsID` is `0`/invalid; 1-based set index | L28 |
| G08 | Instantiation: set indices no longer valid; use `parentID`/`parent1ID`/… /`appendCurveByID` | L29 |
| G09 | Non-relational set: 1-based set index via `.index`, `getObject nset i` | L30 |
| G10 | **DOC ERRATA**: `appendUCurve` takes set index, `appendUCurveByID` takes `nurbsId` (docs swap them) | L32-36 |
| G11 | `numKnots == order + numCVs` invariant; order2→2CVs/4knots, order3→3/5, order4→4/8 | §3.1 |
| G12 | Assignment order order→numCVs→numKnots→setKnot→setCV | §3.1 |
| G13 | `setClampedKnots` helper + clamped knot formula | §3.2 |
| G14 | Surface: `uOrder`,`vOrder`,`numCVs` point2, `numUKnots`,`numVKnots`,`setUKnot`,`setVKnot`,`setCV s u v cv` | §3.2 |
| G15 | `NURBSSet` 26 properties + `setObject`/`removeObject`/`disconnect`/`deleteObjects` | §4.1 |
| G16 | `NURBSSurfaceApproximation` 15 properties incl. `subdivStyle`,`minLevels`,`maxLevels`,`maxTris` | §4.1 |
| G17 | `setViewApproximation`/`setRenderApproximation`/`getProdTess`/`setProdTess`/`getViewTess`/`setViewTess` | §4.1 |
| G18 | `NURBSDisplay` 9 properties + `setSurfaceDisplay` | §4.1 |
| G19 | `NURBSObject`: `.name`, `.nurbsID : integer`, `.index` 1-based, `.isSelected` | §4.2 |
| G20 | `NURBSControlVertex` ctor + `.pos/.x/.y/.z/.weight`; `setCV` needs wrapper | §4.2 |
| G21 | 6 point subclasses with their parent/param properties | §4.2 |
| G22 | `NURBSCurve` common: `isClosed`,`numTrimPoints`,`parameterRangeMin/Max`,`matID`,`evalPos`,`evalTangent` | §4.3 |
| G23 | `NURBSCVCurve` ctor kwargs + props + 8 methods | §4.3 |
| G24 | `NURBSPointCurve` ctor kwargs + props `.numPoints`,`.closed`,`.transform` + methods | §4.3 |
| G25 | `NURBSBlendCurve` 8 props | §4.3 |
| G26 | `NURBSFilletCurve` / `NURBSChamferCurve` props | §4.3 |
| G27 | `NURBSOffsetCurve` / `NURBSMirrorCurve` / `NURBSXFormCurve` / `NURBSSurfaceNormalCurve` props | §4.3 |
| G28 | `NURBSIsoCurve`, `NURBSProjectVectorCurve`, `NURBSProjectNormalCurve` props | §4.3 |
| G29 | `NURBSSurfSurfIntersectionCurve` `.trimCurve1`,`.trimCurve2` | §4.3 |
| G30 | `NURBSSurfaceEdgeCurve`, `NURBSPointCurveOnSurface`, `NURBSCurveOnSurface` props | §4.3 |
| G31 | `NURBSSurface` common 12 props + `evalPos`/`evalUTangent`/`evalVTangent` | §4.4 |
| G32 | `NURBSSurface` UV tiling methods | §4.4 |
| G33 | `NURBSCVSurface` props + 13 methods | §4.4 |
| G34 | `NURBSPointSurface` `.numPoints`, `.closedU`, `.closedV`, `.transform` + methods | §4.4 |
| G35 | 5 `MakeNURBS*Surface` factory functions and their arities | §4.4 |
| G36 | `NURBSULoftSurface` `.numCurves` + 8 methods + `appendCurve` kwargs | §4.4 |
| G37 | `NURBSUVLoftSurface` `.numUCurves`/`.numVCurves` + 8 methods | §4.4 |
| G38 | `NURBS1RailSweepSurface` props + 10 methods | §4.4 |
| G39 | `NURBS2RailSweepSurface` props | §4.4 |
| G40 | `NURBSRuledSurface` / `NURBSExtrudeSurface` / `NURBSLatheSurface` props | §4.4 |
| G41 | `NURBSBlendSurface` 10 props + 6 methods; tension defaults | §4.4, Recipe 6 |
| G42 | `NURBSNBlendSurface` methods | §4.4 |
| G43 | `NURBSCapSurface` `.edge`, `.curveStartPoint : integer` | §4.4 |
| G44 | `NURBSFilletSurface` `.cubic` + 6 methods | §4.4 |
| G45 | `NURBSOffsetSurface` / `NURBSMirrorSurface` / `NURBSXFormSurface` props | §4.4 |
| G46 | `NURBSMultiCurveTrimSurface` `.surfaceParent`, `.surfaceParentID`, `.numCurves`, `.flipTrim` | §4.4 |
| G47 | `NURBSNode <nurbsset> [name:][pos:][material:]` | §5.1 |
| G48 | `NURBSExtrudeNode` full signature | §5.1 |
| G49 | `NURBSLatheNode` full signature | §5.1 |
| G50 | `canConvertTo`/`convertToNURBSSurface`/`convertToNURBSCurve` | §5.2 |
| G51 | §5.2 merge snippet: `addNURBSSet $Arch1 ns2` merges curves | §5.2 |
| G52 | `transform`/`breakCurve`/`breakSurface`/`joinCurves`/`joinSurfaces`/`makeIndependent` node-level | §5.3 |
| G53 | §6.4 never call `getViewTess`/`setViewTess` with `#displacement` | §6.4 |

### nurbs-architecture-recipes.md

| # | Claim | Where |
|---|---|---|
| R01 | `Loft()` is `NotCreatable` | L17 |
| R02 | Instancing via `n = copy src` then `n.baseObject = src.baseObject` | L18, Recipe 7 |
| R03 | Recipe 1 canopy runs verbatim (`NURBSPointCurve`/`appendCurve`/`NURBSOffsetSurface`/`nset.merge`/`NURBSDisplay`/`NURBSSurfaceApproximation`/`setViewApproximation`/`setRenderApproximation`) | Recipe 1 |
| R04 | `appendObject` returns `"OK"` not an index | Recipe 1 |
| R05 | `stopCreating` zero args | Recipes 1,2,4,5 |
| R06 | `"..." + (i as string)` parenthesisation | Recipes 1,2 |
| R07 | Recipe 2 UV-loft runs verbatim; `appendUCurve`/`appendVCurve` take set indices | Recipe 2 |
| R08 | Parameter domain is not normalised to `[0,1]` | L145, §3 |
| R09 | Recipe 3A: `superClassOf (getObject rset i) == NURBSSurface` filter, `evalPos` sampling, `polyop.createVert`/`createPolygon` | Recipe 3A |
| R10 | Recipe 3B: `SplineShape`/`addNewSpline`/`addKnot`/`updateShape`, `render_*` properties | Recipe 3B |
| R11 | Recipe 4: `NURBSProjectVectorCurve` with `parent1ID:`+`parent2:`+`pVec:`+`seed:`+`trim:true`, merged by `addNURBSSet` | Recipe 4 |
| R12 | `close` is a silent no-op; `closed:true` ctor flag closes `NURBSPointCurve` | Recipe 4 |
| R13 | Recipe 5: `NURBS2RailSweepSurface` with `rail1:`/`rail2:`/`parallel:true`, `appendCurve`, `NURBSOffsetSurface` | Recipe 5 |
| R14 | `NURBSBlendSurface` edge convention 1=lowU..4=highV; tension default `1.0`; `flip1`/`flip2` | Recipe 6 |
| R15 | `n.rotation = quat <degrees> [0,0,1]`; `pos.z` is the base | Recipe 7 |
| R16 | `NURBSSurfaceApproximation curvatureAngle` is in radians | guide §4.1, Recipe 1 |

---

## Batch 1 — class existence (`execute "<name>()"`)

```
preClean objects=0
NURBSSet threw=false undef=false          NURBSDisplay threw=false undef=false
NURBSSurfaceApproximation threw=false undef=false
NURBSCVCurve threw=false undef=false       NURBSPointCurve threw=false undef=false
NURBSBlendCurve threw=false undef=false    NURBSFilletCurve threw=false undef=false
NURBSChamferCurve threw=false undef=false  NURBSOffsetCurve threw=false undef=false
NURBSMirrorCurve threw=false undef=false   NURBSXFormCurve threw=false undef=false
NURBSSurfaceNormalCurve threw=false undef=false
NURBSIsoCurve threw=false undef=false      NURBSProjectVectorCurve threw=false undef=false
NURBSProjectNormalCurve threw=false undef=false
NURBSSurfSurfIntersectionCurve threw=false undef=false
NURBSSurfaceEdgeCurve threw=false undef=false
NURBSPointCurveOnSurface threw=false undef=false
NURBSCurveOnSurface threw=false undef=false
NURBSCurveConstPoint threw=false undef=false
NURBSSurfConstPoint threw=false undef=false
NURBSPointConstPoint threw=false undef=false
NURBSCurveIntersectPoint threw=false undef=false
NURBSCurveSurfaceIntersectPoint threw=false undef=false
NURBSCVSurface threw=false undef=false      NURBSPointSurface threw=false undef=false
NURBSULoftSurface threw=false undef=false   NURBSUVLoftSurface threw=false undef=false
NURBS1RailSweepSurface threw=false undef=false
NURBS2RailSweepSurface threw=false undef=false
NURBSRuledSurface threw=false undef=false   NURBSExtrudeSurface threw=false undef=false
NURBSLatheSurface threw=false undef=false    NURBSBlendSurface threw=false undef=false
NURBSNBlendSurface threw=false undef=false   NURBSCapSurface threw=false undef=false
NURBSFilletSurface threw=false undef=false  NURBSOffsetSurface threw=false undef=false
NURBSMirrorSurface threw=false undef=false   NURBSXFormSurface threw=false undef=false
NURBSMultiCurveTrimSurface threw=false undef=false
NURBSIndependentPoint threw=true undef=true          <- needs <point3>, correct per L186
NURBSNode threw=true undef=true  NURBSExtrudeNode threw=true undef=true
NURBSLatheNode threw=true undef=true  NURBSControlVertex threw=true undef=true
                                       <- all four need args; re-probed in batch 8
TotalGarbageXYZ_fn(1) threw=true undef=true           <- BOGUS CONTROL
postClean objects=0
```
**G01 CONFIRMED.** Every documented NURBS class constructs. The four 0-arg throws are arity, not
absence — `NURBSControlVertex <point3>` already had a VERIFIED note, and G47/G48/G49 are settled in
batch 8.

## Batch 2 — global function existence (91 names, arity-error discrimination)

Discriminator calibrated first: real function with 0 args → `Argument count error`;
`TotalGarbageXYZ_fn()` → `Type error: Call needs function or class, got: undefined`.

```
EXISTS appendObject setObject removeObject disconnect deleteObjects getObject
EXISTS getProdTess setProdTess getViewTess setViewTess
EXISTS evalPos evalTangent evalUTangent evalVTangent
EXISTS getTiling setTiling getTilingOffset setTilingOffset getGenerateUVs setGenerateUVs
EXISTS close getKnot setKnot getCV setCV refine reparameterize getPoint setPoint
EXISTS closeU closeV getUKnot setUKnot getVKnot setVKnot refineU refineV
EXISTS getCurve setCurve getCurveID setCurveByID getFlip setFlip
EXISTS getCurveStartPoint setCurveStartPoint
EXISTS appendCurve appendCurveByID appendUCurve appendUCurveByID appendVCurve appendVCurveByID
EXISTS getUCurve setUCurve getUCurveID setUCurveByID getVCurve setVCurve getVCurveID setVCurveByID
EXISTS setParent setParentID setEdge getParent getParentID
EXISTS setSeed setRadius setTrimSurface setFlipTrim canConvertTo
stopCreating :: (no error at all -> confirms the documented ZERO arity, G04)
getNURBSSet / addNURBSSet / transform / breakCurve / breakSurface / joinCurves /
joinSurfaces / makeIndependent / setViewApproximation / setRenderApproximation /
setSurfaceDisplay / convertToNURBSSurface / convertToNURBSCurve
    :: EXCEPTION_ACCESS_VIOLATION  == found and invoked with an undefined node arg
EXISTS MakeNURBSSphereSurface   :: Argument count error: NURBSSphereSurface   wanted 8, got 0
EXISTS MakeNURBSCylinderSurface :: Argument count error: NURBSCylinderSurface wanted 7, got 0
EXISTS MakeNURBSConeSurface     :: Argument count error: NURBSConeSurface     wanted 8, got 0
EXISTS MakeNURBSTorusSurface    :: Argument count error: NURBSTorusSurface    wanted 9, got 0
EXISTS MakeNURBSLatheSurface    :: Argument count error: NURBSLatheSurface    wanted 5, got 0
BOGUS_CONTROL :: Type error: Call needs function or class, got: undefined
```
**G17, G32, G36, G37, G38, G42, G44, G50 method names all CONFIRMED to exist.**
**G04 CONFIRMED** (`stopCreating()` with 0 args is the only name in the list that produced no error).
**G35 CONFIRMED exactly** — 8/7/8/9/5 match the documented positional arities line for line.

## Batch 3 — `NURBSSet` / `NURBSSurfaceApproximation` / `NURBSDisplay` properties

All 26 `NURBSSet` properties `isProperty=true`; all 15 `SurfApprox` properties `true`; all 9
`NURBSDisplay` properties `true`. Controls: `NURBSSet.bogusPropZZ=false`,
`SurfApprox.bogusPropZZ=false`, `Display.bogusPropZZ=false`, and writing `d.bogusPropZZ=1` threw.
Read-back defaults: `SurfApprox.merge=0.0`, `curvatureAngle=20.0`, `spacialEdge=10.0`,
`isoULines=2`, `meshUSteps=2`, `config=isoAndMesh`, `subdivStyle=tree`.
**G15, G16, G18 CONFIRMED as property sets.** (The radians question for `curvatureAngle` is G16/R16,
settled or not in the curvature batch below.)

## Batch 4 — curve classes, 16 classes × per-class documented property list

`isProperty`, reporting misses only. Control per class: `bogusZZ_isProperty=false` everywhere.

```
NURBSCVCurve   MISSING=[isSelected, closed]
NURBSPointCurve MISSING=[isSelected, closed]
NURBSBlendCurve MISSING=[isSelected, parent, parentID]   <- parent/parentID not claimed by the guide
NURBSFilletCurve MISSING=[isSelected]
NURBSChamferCurve MISSING=[isSelected]
NURBSOffsetCurve MISSING=[isSelected]
NURBSMirrorCurve MISSING=[isSelected]
NURBSXFormCurve MISSING=[isSelected]
NURBSSurfaceNormalCurve MISSING=[isSelected, uParam, vParam]
NURBSIsoCurve MISSING=[isSelected]
NURBSProjectVectorCurve MISSING=[isSelected]
NURBSProjectNormalCurve MISSING=[isSelected]
NURBSSurfSurfIntersectionCurve MISSING=[isSelected, trimCurve1, trimCurve2]
NURBSSurfaceEdgeCurve MISSING=[isSelected]
NURBSPointCurveOnSurface MISSING=[isSelected, closed]
NURBSCurveOnSurface MISSING=[isSelected]
```
Everything else present, including all of G22, G23, G25, G26, G28, G30 and the `seed`/`trim`/
`flipTrim`/`axis`/`transform` sets.

## Batch 5 — direct guarded re-probe of the batch-4 misses (calibration required)

`isProperty` had just reported `closed=false` for `NURBSPointCurve`, which the guide's own
VERIFIED note contradicts — so all four misses were re-measured by guarded read with a positive
control (`numPoints`) and a bogus control in the same call.

```
POSCONTROL pc.numPoints=0                 <- reads fine, so the probe CAN see real properties
rd pc.closed              = THREW
rd pc.isSelected          = THREW
write pc.closed = true    -> threw=true, readback THREW
CONTROL rd pc.bogusZZ     = THREW         <- absence IS detectable here
ctor closed:true  -> isClosed=true       <- the constructor kwarg genuinely works
rd NURBSCVCurve.isSelected = THREW
rd NURBSCVCurve.closed     = THREW
CONTROL rd NURBSCVCurve.bogusZZ = THREW
rd NURBSBlendCurve.isSelected  = THREW
rd NURBSBlendCurve.tension1    = 1.0      <- real property, reads fine
rd SurfNormalCurve.uParam       = THREW
CONTROL rd SurfNormalCurve.bogusZZ = THREW
rd SurfSurfIntersect.trimCurve1 = THREW
```
The positive/bogus pair shows the probe is sound, so these THROWs are real absences.
Note the important asymmetry this exposed: **the constructor kwarg `closed:true` works while the
property `.closed` does not exist at all** — `isClosed` is the only readable one.

## Batch 6 — candidate-name discovery for the batch-5 absences

```
NURBSSurfaceNormalCurve  PRESENT: distance, parent, parentID
  ABSENT : uParam, vParam, u, v, uParameter, vParameter, uPosition, vPosition,
           parameter1, parameter2, uCoord, vCoord, uv
NURBSSurfSurfIntersectionCurve PRESENT: trim1, trim2, flipTrim1, flipTrim2, seed,
                                       parent1, parent2, parent1ID, parent2ID
  ABSENT : trimCurve1, trimCurve2, trim, flipTrim
NURBSMultiCurveTrimSurface PRESENT: numCurves, flipTrim
  ABSENT : surfaceParent, surfaceParentID, parent, parentID, parent1, parent1ID,
           surface, surfaceID, baseSurface, parentSurface, parentSurfaceID, srfParent,
           surfParent, baseParent, targetSurface, targetSurfaceID, parentSrf,
           curveParent, parentSrf, surface, surfParentID
NURBSPointSurface PRESENT: numPoints, transform
  ABSENT : closedU, closedV, closed, isClosedU, isClosedV
NURBSNBlendSurface PRESENT: ()   ABSENT: parent1..parent4, numParents, nParents, numSides, edges, tension1, flip1
NURBSBlendCurve   PRESENT: parent1,parent2,parent1ID,parent2ID,flip1,flip2,tension1,tension2  ABSENT: radius
NURBSChamferCurve PRESENT: length1,length2,parent1,parent2,flip1,flip2,trim1,trim2,flipTrim1,flipTrim2  ABSENT: radius
```
`trimCurve1`/`trimCurve2` are real and simply **named `trim1`/`trim2`**. For
`NURBSMultiCurveTrimSurface` and `NURBSPointSurface` no substitute name was found in 22 and 6
candidates respectively.

## Batch 7 — surface classes, 17 classes

`isSelected` missing on **all 17**, `bogusZZ=false` on all 17. Everything else present, including
all of G31, G33, G36-G45 except:
```
NURBSPointSurface       MISSING=[isSelected, closedU, closedV]
NURBSMultiCurveTrimSurface MISSING=[isSelected, surfaceParent, surfaceParentID, parent, parentID]
NURBSNBlendSurface      MISSING=[isSelected, numParents, parent1, edge1, flip1, tension1]
```

## Batch 8 — documented defaults and types

```
CapSurface.curveStartPoint = 0.0   cls=Float   edge=0
LatheSurface.sweep        = 360.0            <- confirms G40 "in degrees, e.g. 360.0"
ExtrudeSurface.distance   = 0.0     curveStartPoint=0.0
BlendSurface.tension1 = 1.0  tension2 = 1.0    <- CONFIRMS Recipe 6 "(default 1.0)"
BlendSurface.edge1=1  edge2=1  flip1=false
RuledSurface.curveStartPoint1 = 0.0
CVCurve fresh: order=0 numCVs=0 numKnots=0  autoParam=notAutomatic  endsOverlap=false
CVSurface.numCVs = [0,0]  cls=Point2   uOrder=0  rigid=false     <- G34/G33 type claims hold
PointSurface.numPoints = [0,0]  cls=Point2
MirrorCurve.axis  cls=Name val=x        MirrorSurface.axis cls=Name val=x
NURBSNode $NURBSExtrudeNode  -> NURBSSurf created, objects=2     (signature verbatim)
NURBSLatheNode    -> NURBSSurf created, objects=3                (signature verbatim)
```
`CapSurface.curveStartPoint` is a **Float**, not the documented `integer` (G43).
`LatheSurface.sweep` default 360.0 confirms degrees (G40).
`NURBSLatheNode <node> (matrix3 1) 360.0 capStart: capEnd: weldCore: mapCoords: name:` accepted
every keyword verbatim → **G49 CONFIRMED**.

## Batch 9 — committed relational node

2 `NURBSPointCurve` + `NURBSULoftSurface`, then `NURBSNode`:
```
classOf=NURBSSurf  superClassOf=GeometryClass
appendObject ret cls=OkClass val=OK          <- G03/G04 CONFIRMED
appendCurve  ret cls=OkClass
loft.numCurves 0 -> 2
rset.numObjects=9   <- IMPORTANT: the relational set also contains the 6 NURBSIndependentPoint
  [1..3] Point 001 NURBSIndependentPoint   [4] A NURBSPointCurve  [5..7] points  [8] B  [9] L
loft getCurveID 1=3252106519360P (= curve A's nurbsID)  2=3252106519360P/B  getFlip1=false
paramRange u=0.0..2200.0  v=0.0..2200.0        <- NOT normalised, confirms the VERIFIED note
evalPos(0.5,0.5)=[-0.113643,0.340909,0.568198]  evalUTangent=[-0.227287,0,1.1364]
renderable=true genUV1=true matID=1 flipNormals=false closedInU=false
nurbsID prints as <decimal>P  (IntegerPtr)      <- contradicts the documented `: integer`
.index reads 0 for EVERY object in both relational and non-relational sets
```
**G08 CONFIRMED**: relational sets carry `nurbsID`, and `getCurveID` resolves to the real curve ID.
**G31 / R08 CONFIRMED** (ranges not normalised). **G33/G36 CONFIRMED** (`numCurves` tracks `appendCurve`).
**G19 partially disproved**: `.nurbsID` is `IntegerPtr`, not `integer`; `.index` is 0, not a
1-based set index. See batch 12 for `.index` on a non-relational set.

## Batch 10 — non-relational set / `disconnect` / Recipe 3A filter

```
superClassOf==NURBSSurface hits=#(9) errs=#()      <- Recipe 3A's filter WORKS, no errors
superClassOf(loft)=NURBSSurface
ns = getNURBSSet node   (non-relational)
  [1] NURBSCVSurface index=0   <- the loft IS baked to NURBSCVSurface, confirming G09 row 3
  [2][3] NURBSCVCurve  [4..9] NURBSIndependentPoint   all index=0
disconnect ns -> ok ; after disconnect obj1 superClassOf==NURBSSurface : true cls=NURBSCVSurface
deleteObjects ns -> ok ; deleteObjects rs -> ok
```
**G09's "baked/decomposed into independent NURBSCVSurface/NURBSCVCurve" CONFIRMED**, and
`disconnect` / `deleteObjects` work. **`.index` is 0 here too** — it is not a usable 1-based index.
**R09's filter expression CONFIRMED.**

## Batch 11 — argument validation of `append*` (errata discriminator, first attempt)

```
appendUCurve(setIdx)=OK   appendVCurve(setIdx)=OK  numU=1 numV=1
appendCurve(setIdx)=OK
appendUCurve(nurbsID) -> OK    numUCurves=2       <- accepts an ID silently
appendVCurve(nurbsID) -> OK    numVCurves=2
appendCurve(nurbsID)  -> OK    numCurves=2
appendUCurveByID(nurbsID) -> OK   appendVCurveByID(nurbsID) -> OK   appendCurveByID(nurbsID) -> OK
BOGUS_CONTROL appendUCurveByID(999) -> OK
```
**Neither family validates its integer argument — even the bogus `999` returns OK.** So argument
acceptance cannot settle G10; a commit-time discriminator is required.

## Batch 12 — commit-time discriminator for the errata claim

Recipe 2's 3×3 grid run verbatim, then read back:
```
precommit numU=3 numV=3
precommit getUCurveID1=0P  getVCurveID1=0P        <- pre-commit IDs are 0, as G07 says
node classOf=NURBSSurf   bbox min=[0,-572.686,0] max=[1600,225,1800]
postcommit getUCurveID 1=3252287678672P  2=3252287676912P
postcommit getVCurveID 1=3252287679024P  2=3252287679376P
Horizontal_FloorCurve_1 nurbsID=3252287678672P     <- IDENTICAL to getUCurveID 1
Vertical_MullionCurve_1 nurbsID=3252287679024P     <- IDENTICAL to getVCurveID 1
paramRange u=0.0..1842.27  v=0.0..1842.27
evalPos(0.5,0.5)=[0.434251,-0.0490072,0.488536]
setSurfaceDisplay ok
```
**G10 / R07 CONFIRMED.** `appendUCurve` was handed the 1-based **set index** and, at commit, the
loft's `getUCurveID` came back as the curve's real `nurbsID`. The guide's errata note is correct as
written. **R07 (Recipe 2 runs verbatim) CONFIRMED.**

## Batch 13 — knot invariant and the `setClampedKnots` helper

```
fresh NURBSCVCurve: order=0 numCVs=0 numKnots=0
after order=4:  numCVs=0 numKnots=0
after numCVs=5: numKnots=0          <- numKnots is NOT auto-derived; the caller must set it
after numKnots=9: read=9
order3/numCVs3 -> numKnots=0 ; order2/numCVs2 -> numKnots=0
setClampedKnots inlined verbatim, ord=4 nCVs=5:
knots=#(0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0)      <- exactly the L62-67 formula
getCV(1).pos=[0,0,0]  weight=1.0
setCV crv 1 (NURBSControlVertex [0,0,0] 1.0) -> NURBS_cv([0,0,0], 1)
```
**G11, G12, G13, G20 CONFIRMED.** `numKnots == order + numCVs` is a caller obligation (it stays 0
until set), and the helper produces precisely the documented clamped vector. `setCV` with the
`NURBSControlVertex` wrapper works and `.weight` defaults to `1.0`.
The *violating* direction was deliberately **not** tested: the guide says it raises a modal
Assertion Failure dialog, and a modal dialog would hang the bridge.

## Batch 14 — Recipe 1 verbatim, and `addNURBSSet` with a live `parentID`

```
RECIPE1 name=Arch_NURBS_Canopy classOf=NURBSSurf  objects.count=1
bbox min=[0,-1000,-35.0618] max=[3617.43,1000,924.759]
rset.numObjects=26
  Canopy_TopSkin cls=NURBSOffsetSurface parent=0 parentID=3253583063168P distance=35.0
                   matID=2 genUV1=true renderable=true
addNURBSSet(offset, parentID) -> ok   injectedPresent=NO   rset 26 -> 26
bbox after max=[3617.43,1000,924.759]      <- unchanged
```
**R03 CONFIRMED** — Recipe 1 runs verbatim: `NURBSPointCurve` kwargs, `setPoint`,
`appendCurve ... flip:false tension:0.0`, `NURBSOffsetSurface parent:`, `nset.merge`,
`NURBSDisplay`, `NURBSSurfaceApproximation` with every documented kwarg including
`subdivStyle:#grid`, `setViewApproximation`, `setRenderApproximation`, all accepted. The bbox
z-min of −35.06 is the −35 cm offset, i.e. the soffit.
Also note `parent=0` while `parentID=3253583063168P` on the committed offset surface — an
independent confirmation of G07/G08 (set index invalid, `parentID` live after commit).

## Batch 15 — `addNURBSSet`, four variants

```
(1) §5.2 snippet verbatim, two converted Rectangle nodes:
    Arch1 classOf=NURBSCurveshape   r1 before=4  r2=4
    addNURBSSet Arch1 ns2 -> ok
    r1 after=4      MERGE_WORKED=NO
    Arch1 bbox=[-400,-5,0]..[400,5,0]        <- Arch2 lived at x=3000; not absorbed
(2) ULoft built with appendCurveByID from 2 real curve IDs:
    appendCurveByID x2 = OK / OK  numCurves=2
    addNURBSSet -> ok   ULoft present=NO   rset 4 -> 4
(3) UVLoft built with appendUCurveByID/appendVCurveByID from a real ID:
    UVLoft present=NO   rset 4 -> 4
(4) NURBSOffsetSurface parentID:<live surface nurbsID>:
    addNURBSSet -> ok   injected=NO   rset 9 -> 9   bbox unchanged
```
**G06 and G51 DISPROVED as executable behaviour in this build.** `addNURBSSet` resolves and
returns `ok`, but in all four variants nothing was added: the receiving set's `numObjects` never
moved and the node bbox never changed. Variant 1 has a live positive control — Arch2's geometry was
at x=3000 and Arch1's max.x stayed 400 — so this is a genuine absence of effect, not a mis-indexed
read.

## Batch 16 — §5.3 node-level operations, and the node class-name claim

```
base rset=13  bbox=[401.022,0,0]..[2000,0,529.63]
transform <node> <nurbsId> (matrix3 1) -> OK   (identity, bbox unchanged as expected)
breakSurface <node> <nurbsId> #U 0.5       -> OK
makeIndependent <node> <nurbsId>           -> 0P
rset 13 -> 14
```
**G52 CONFIRMED for `transform`, `breakSurface`, `makeIndependent`.**

Class-name check, with controls:
```
NURBSSurf()        threw=true      <- exists but not constructible with 0 args
NURBSCurveshape()  threw=true
CV_Surf()          threw=true undef=true
Point_Surf()       threw=false undef=false
CV_Curve()         threw=false undef=false
Point_Curve()      threw=false undef=false
NURBSMesh()        threw=true      NURBSSurface() threw=true      NURBSCurve() threw=true
TotalGarbageXYZ_fn(1) threw=true    <- BOGUS CONTROL
measured node classes:
  surface-bearing node      classOf = NURBSSurf
  point-surface-only node   classOf = NURBSSurf   bbox=[0,0,0]..[500,0,500]
  curve-only node           classOf = NURBSCurveshape
```
**G02 PARTLY DISPROVED.** A NURBS node's `classOf` is `NURBSSurf` for any surface content
(including a point surface) and `NURBSCurveshape` for curve-only content. `CV_Surf` does not even
construct; `Point_Surf`, `CV_Curve`, `Point_Curve` construct as classes but are not the `classOf`
of any node built here.

## Batch 17 — conversion route

```
Rectangle -> canConvertTo NURBSCurve=true, canConvertTo NURBSSurface=true
convertToNURBSCurve -> ok, class becomes NURBSCurveshape
rset.numObjects=4, all four are NURBSCVCurve with superClassOf == NURBSCurve
```
**G50 CONFIRMED.** (My first attempt at this batch wrongly tested `classOf o == NURBSCurve` and found
0 curves — my error, not a defect; the superclass is `NURBSCurve`, the class is `NURBSCVCurve`.)

---

## Batch 18 — Recipe 5 verbatim, and MAXScript trig units

```
TRIG UNITS: cos 180.0 = -1.0   cos 3.14159265 = 0.998497   sin 90.0 = 1.0
RECIPE5 name=Arch_CurvedRamp_NURBS classOf=NURBSSurf objects=1
bbox=[-750,-10.1152,-29.6183]..[900,926.09,450]
rset=28
  2RailSweep rail1=0 rail2=0 rail1ID=2970407913232P rail2ID=2970407914288P
             parallel=true numCurves=2
  Ramp_InnerRail nurbsID=2970407913232P      <- IDENTICAL to rail1ID
  Ramp_OuterRail nurbsID=2970407914288P      <- IDENTICAL to rail2ID
```
**R13 CONFIRMED.** Recipe 5 runs verbatim. Note also that `.rail1`/`.rail2` read `0` post-commit while
`rail1ID`/`rail2ID` are live — a third independent confirmation of the §2 lifecycle rule.

**MAXScript trig functions take DEGREES**, which matters: Recipe 5's `ang = t * 180.0` fed into
`cos ang`/`sin ang` really is a 180° sweep, and Recipe 4's `ang = (k - 1) * 45.0` really is 8 steps of
45°. **Both recipes are internally correct on this point** — no correction made.

## Batch 19 — Recipe 4 construction steps, and the point subclasses

```
targetSurfID=3252025281792P found=YES
skyCrv.isClosed=true  crvIdx=1
NURBSProjectVectorCurve parent1ID: parent2: pVec:[0,0,-1] seed:[0.5,0.5] trim:true flipTrim:false  -> constructed
addNURBSSet -> ok   COS_present=NO   NURBSCVSurface_present=NO
rset 21 -> 21   bbox=[0,-800,100]..[2700,800,400]    (unchanged)
--- point subclasses ---
NURBSCurveConstPoint            PRESENT: pos x y z parent parentID uParam offset normal uTangent flipTrim trimCurve  [extra probe: type]
NURBSSurfConstPoint             PRESENT: pos x y z parent parentID uParam vParam offset normal uTangent vTangent [extra probe: type]
NURBSPointConstPoint            PRESENT: pos x y z parent parentID offset
NURBSCurveIntersectPoint        PRESENT: pos x y z parent1 parent2 parent1ID parent2ID flipTrim1 flipTrim2
NURBSCurveSurfaceIntersectPoint PRESENT: pos x y z parent1 parent2 parent1ID parent2ID seed flipTrim trimCurve
bogusZZ=false on all five
```
`type` is the constraint-mode property on both const-point classes (not `pointType`);
`trimCurve` is the trim flag on `NURBSCurveConstPoint` (not `trim`);
`NURBSCurveIntersectPoint` has no seed or trim properties at all beyond the two flip flags.
**R11 DISPROVED** — every construction step works, the merge does not.

## Batch 20 — Recipes 3A and 3B

```
3A domain u=0.0..1252.84 v=0.0..1252.84
3A classOf=Editable_Poly verts=325 faces=288   expectedVerts=325 expectedFaces=288
3B -> ok  numSplines=256  expected=256
3B render thickness=12.0 sides=12 displayRenderMesh=true
```
**R09 and R10 CONFIRMED exactly** — not merely "no error" but the predicted counts:
`24x12` panels → `(24+1)*(12+1)` = 325 verts and `24*12` = 288 faces; `16x8` cells × 2 diagonals =
256 splines. `Editable_Mesh` → `convertTo Editable_Poly`, `polyop.createVert`, `polyop.createPolygon`,
`addNewSpline`, `addKnot ... #smooth #curve`, `updateShape` and all four `render_*` properties work.

## Batch 21 — instancing and quaternion (Recipe 7)

```
box pos=[0,0,0] min=[-50,-100,0] max=[50,100,20]
plain copy shares baseObject = false      (expected false)
copy + baseObject assignment shares = true   classOf=Box
rot 90 via quat 90.0 [0,0,1] -> bbox=[-100,-50,1500]..[100,50,1520]   (X/Y swapped: 200x100)
pos=[0,0,1500] -> min.z=1500.0 max.z=1520.0   (base sits at pos.z, height 20)
```
**R02 and R15 CONFIRMED verbatim.** A plain `copy` does **not** share the base object; the
`n2.baseObject = b.baseObject` assignment does. `quat <degrees> [0,0,1]` rotates correctly and
`pos.z` is the base, not the centre.

## Batch 22 — `curvatureAngle` unit test (the R16 / §4.1 radians claim)

Method: a 100 mm-radius quarter-cylinder `NURBSPointSurface` (5×5 points, bbox
`[-4.4e-06,0,0]..[100,100,100]`), render approximation `config:#meshOnly meshApproxType:#curvature`,
then `snapshotAsMesh <node>` and read `numverts`. Safe under **both** hypotheses — every value used
is a *loose* constraint, so no probe can blow up the mesh count.

```
curvatureAngle=1.0     -> numverts=415
curvatureAngle=4.0     -> numverts=147
curvatureAngle=7.0     -> numverts=87
curvatureAngle=20.0    -> numverts=51     (this is also the shipped default)
curvatureAngle=6.0     -> numverts=101
curvatureAngle=0.10472 -> numverts=691    (0.10472 == degToRad 6.0)
2pi = 6.283185
```
**The unit is DEGREES.** Reasoning, stated so it can be re-checked: if the value were radians then
every input at or above `2π = 6.283` would be an unconstrained "no limit" angle and would collapse
to one identical minimum mesh. `7.0` and `20.0` are both above `2π` yet give **87 versus 51**, and
the curve is smooth and monotonic straight through `2π` (147 → 87 between 4.0 and 7.0, no step) —
that is the degrees signature. Corroborating: the shipped default is `20.0`, a conventional degrees
default and a meaningless 1146° in radians; and `6.0` → 101 verts versus `degToRad 6.0` → 691 verts
quantifies Recipe 1's original `degToRad` wrapper as a ~6.9× over-tessellation.

## Batch 23 — remaining curve/surface methods and the `Loft` claim

```
getViewTess <surf> #surface -> undefined        (exists; returns undefined here)
getProdTess <surf> #surface -> undefined        (exists; returns undefined here)
getTiling  -> [1,1] ;  setTiling 2.0 3.0 channel:1  ->  getTiling channel:1 -> [2,3]
getGenerateUVs <surf> 1 -> true
POSCONTROL NURBSPointCurve.numTrimPoints=0  isClosed=false  matID=1
evalPos    <uninstantiated curve> 0.5 -> undefined
evalTangent<uninstantiated curve> 0.5 -> undefined
Loft() threw=true undef=true
BOGUS TotalGarbageXYZ_fn(1) threw=true undef=true
```
**G32 CONFIRMED** (`getTiling`/`setTiling` round-trip). `getGenerateUVs` works. `evalPos`/`evalTangent`
on an uninstantiated curve return `undefined` rather than throwing, consistent with the "must be
instantiated in scene first" warnings. `Loft()` is not constructible, which supports R01, though the
exact `NotCreatable` marker string was not obtained.

> **⚠️ SUPERSEDED IN PART by P15 (2026-10-06).** The `getTiling`/`setTiling` round-trip above is
> real and still holds — but it **was calibrated for the wrong question and proved nothing about the
> tiling being applied.** Measured at P15: `setTiling s 3.5 1.5` → `getTiling` returns **`[3.5, 1.5]`**
> while the actual UVs come out **`3.0 × 1.0`** — **`setTiling` silently floors its arguments to
> integers, and `getTiling` echoes the request rather than reporting what was applied.** The probe
> read a value back and stopped; it never read the UV range off `snapshotAsMesh`, which is the only
> measurement that would have caught it. Full transcripts: `references/13-uv-rules.md` §3.

**Deliberately NOT tested:** `getViewTess`/`setViewTess` with `#displacement` (G53). The guide states
it raises a modal Assertion Failure dialog; a modal dialog would hang the main thread and the bridge.
G53 is left as-is and marked untested in this file. Likewise the *violating* direction of the §3.1
knot invariant was not tested, for the same reason.

---

## Final verdict table

| Claim | Verdict |
|---|---|
| **CONFIRMED — 47 claims**: G01 G03 G04 G05 G07 G08 G10 G11 G12 G13 G14 G15 G16 G17 G18 G20 G22 G23 G24(`numPoints`/`transform`/methods) G25 G26 G27(`NURBSOffsetCurve`/`MirrorCurve`/`XFormCurve`) G28 G29(`.trim1/.trim2`) G30 G31 G32 G33 G34(`numPoints`/`transform`/methods) G35 G36 G37 G38 G39 G40 G41 G42 G43(`edge`/`.parent`) G44 G45 G47 G48 G49 G50 G52 R01 R02 R03 R04 R05 R06 R07 R08 R09 R10 R12 R13 R14 R15 | **CONFIRMED** |
| **DISPROVED — 13 claims** | see list below |
| **UNVERIFIED — 4 claims** | G53, G42 arg bodies, G44 arg bodies, G21 `NURBSCurveIntersectPoint` seeding |

### The 13 disproved claims

| # | Claim | Correction applied |
|---|---|---|
| G02 | node `classOf` is `NURBSSurf`/`CV_Surf`/`Point_Surf`/`Point_Curve`/`CV_Curve` | `NURBSSurf` (any surface) / `NURBSCurveshape` (curves only); `CV_Surf` does not construct |
| G06 / G51 | `addNURBSSet` appends a set into the node; §5.2 merge snippet | Silent no-op in 4 tested variants; snippet's `delete $Arch2` then destroys the curves |
| G19a | `NURBSObject.isSelected` | Does not exist on any of 34 classes |
| G19b | `NURBSObject.index` is a 1-based set index | Reads `0` everywhere; use `getObject nset i` |
| G19c | `NURBSObject.nurbsID : integer` | `IntegerPtr`, prints `<decimal>P`, will not fit an integer slot |
| G21 | `NURBSCurveConstPoint.pointType` / `.trim` | `.type` / `.trimCurve` |
| G21 | `NURBSSurfConstPoint.pointType` | `.type` |
| G21 | `NURBSCurveIntersectPoint.seed1/.seed2/.trim1/.trim2` | None exist; only `flipTrim1`/`flipTrim2` |
| G24 | `NURBSPointCurve.closed` is a settable property | Neither readable nor writable; constructor kwarg is the only route |
| G27 | `NURBSSurfaceNormalCurve.uParam` / `.vParam` | Absent (14 candidates tested); class has no usable UV seed |
| G29 | `NURBSSurfSurfIntersectionCurve.trimCurve1` / `.trimCurve2` | Named `trim1` / `trim2` |
| G34 | `NURBSPointSurface.closedU` / `.closedV` | Absent |
| G43 | `NURBSCapSurface.curveStartPoint : integer` | `Float`, default `0.0` |
| G46 | `NURBSMultiCurveTrimSurface.surfaceParent` / `.surfaceParentID` | Absent under 20 candidate names; class has no parent slot |
| G16 / R16 | `curvatureAngle` in radians | **Degrees**; `degToRad` wrapper removed from Recipe 1 |
| R11 | Recipe 4 completes | Its final `addNURBSSet` no-ops; recipe does not complete |

### Still UNVERIFIED

- **G53** (`getViewTess`/`setViewTess` with `#displacement` asserts): not executed — modal-dialog
  risk would hang the bridge. Left as written.
- **G42** `NURBSNBlendSurface` method bodies (`setParent`/`setParentID`/`setEdge`): the names exist
  (arity test) but the class exposes **no** properties at all, so the `1..4` index convention could
  not be exercised. Marked UNVERIFIED in the guide.
- **G44** `NURBSFilletSurface` method bodies (`setParent`/`setParentID`/`setSeed`/`setRadius`/
  `setTrimSurface`/`setFlipTrim`): names exist; bodies not exercised.
- **G21** `NURBSCurveIntersectPoint` seeding: no seed property and no `setSeed` method found, so the
  question of how a specific intersection is chosen is unanswerable here.

### Claims in the two files that were not probed at all

Listed for completeness so they are not mistaken for verified: the `geometry_qa` / `agent_viewport` /
`contact_check` / `mesh_edit` absence statements (tool-list claims, not MAXScript claims, and already
annotated `UNVERIFIED` or `P4b-r` in the files), the §6 safety prose, `NURBSFilletSurface.cubic`
semantics, `NURBSDisplay.displayTrimming` semantics, and the `NURBSBlendSurface` edge-index
*geometric* meaning (only its default `1` and the tension defaults were read).

---

## Note on two claims that looked wrong but were my error, not defects

Recorded because `AGENTS.md` demands that discarded findings be logged, not silently dropped:

1. I probed the converted rectangle with `classOf o == NURBSCurve` and found **0 curves**, which
   looked like a missing class. It is not: the class is `NURBSCVCurve` and `NURBSCurve` is its
   **superclass**. `convertToNURBSCurve` correctly yields 4 `NURBSCVCurve` objects.
2. I read `.numTrimPoints` and `.isClosed` off a `NURBSULoftSurface` and got `Unknown property`,
   which looked like two more defects. They are not: §4.3 correctly scopes both to `NURBSCurve`
   subclasses only, and batch 4 confirmed them present on all 16 curve classes.