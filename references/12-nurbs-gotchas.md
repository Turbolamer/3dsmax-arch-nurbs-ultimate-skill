# 12 — NURBS Gotchas in 3ds Max 2026 (verified by live execution)

> **Purpose:** the practical gotchas and caveats for writing *working* NURBS code in 3ds Max 2026
> through the `3dsmax-mcp` bridge. The NURBS API is real, complete, and scriptable.
>
> **All rows below were verified on 2026-10-04 against a live 3ds Max 2026 session through the
> `3dsmax-mcp` bridge** by executing MAXScript, not by reading SDK reflection. Anything not verified
> is marked UNVERIFIED and must be probed at runtime. See `02-mcp-live-orchestration.md` for tool
> routing rules.
>
> Environment: 3ds Max **2026.3.2 Security Fix**, transport `namedpipe`, protocol 2,
> `safeMode: true`, `threadMode: mainThread`.

---

## Correction notice

An earlier revision of this file claimed that `NURBSSet` did not exist and that only
`QuadPatch` / `Surface` / `Sweep` were usable. **That was wrong.** The claim came from trusting
`introspect_class "NURBSSet"` (which returns `Class not found`) and from a vacuous probe — a class
probe with no known-bogus control in the same batch, which produced a false negative. Executing
`snippets/nurbs_arch_library.ms` proved the whole NURBS API resolves, constructs, and evaluates. The
finding has been reversed; the introspection lesson is kept and promoted in section 5. What remains
open is small and specific: three bugs in our own library file, and five genuinely unresolved API
details listed in section 7.

**Second reversal, same day — and this one is the dangerous one.** An intermediate revision of this
file reported that `NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface` and
`NURBSProjectVectorCurve` "expose no API, they are not implemented", on the strength of a probe that
returned `ERR` for all 15 candidate property names it tried. **All four classes work end-to-end.**
They construct, commit inside a `NURBSNode`, evaluate, and expose their full relational property sets
(section 1.4; gotchas 3.14–3.19). Two independent faults produced the false negative and both are now
permanent rules here: the probe read the objects in a **pre-commit** state (3.14), and it used
`o["name"]` bracket syntax, which is not dynamic property access in MAXScript (3.18). A third fact
from the same probe is the most transferable of the three — an invalid dependent surface is
**silently dropped** at commit, so geometry that "ran" can be absent from the set (3.15).

**Third correction, later the same day — the one that shipped a defect.** The P4b write-up recorded
that `NURBSProjectVectorCurve trim:true` "works … **and a second surface appears in the set**". That
second sentence was read here, and in `agents/max-nurbs.md`, as evidence that the trim *does*
something to the surface. **It does not.** The second surface is an untrimmed `NURBSCVSurface`
**copy of the parent**, added by the relation; `trim:true` does not split, does not cut, and does not
vary with the profile. Corrected 2026-10-04 with two structurally different profiles whose output was
byte-identical — see 3.25, and the correction itself in 3.26. The generalisable lesson, same family
as 3.18: **the presence of an extra object in a set is not evidence of the operation you expected.**

---

## 1. NURBS capability — verified

### 1.1 Class matrix

| MAXScript id | Creatable | Verified behaviour |
| :--- | :--- | :--- |
| `NURBSSet` | YES | The relational container. `NURBSSet()` -> `NURBSSet`. Holds curves and surfaces; `numObjects` reads back. |
| `NURBSCVCurve` | YES | CV curve primitive. Used by `MCP_NURBS_Arch.makeCVCurve`. |
| `NURBSPointCurve` | YES | Point curve primitive. Used by `MCP_NURBS_Arch.makePointCurve`; both return valid objects. |
| `NURBSPointSurface` | YES | Constructs. |
| `NURBSCVSurface` | YES | Constructs. |
| `NURBSULoftSurface` | YES | **The real lofting class.** U-direction loft over appended curves. |
| `NURBSUVLoftSurface` | YES | Gordon-network loft: append U-curves and V-curves. |
| `NURBS1RailSweepSurface` | YES | **Works end-to-end.** `rail:<set index> parallel:<bool>` + one `appendCurve` per cross-section. Executed: 3-point rail + 3 sections -> surface at index 14, `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[500,0,100]`. Reads back `rail` `railID` `parallel` `numCurves` `axisTM` — **committed sub-object only** (3.14). |
| `NURBS2RailSweepSurface` | YES | **Works end-to-end.** `rail1:` `rail2:` `parallel:`. Executed: two parallel rails 500 cm apart + 3 transverse sections -> `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[550,200,0]`, the exact midpoint between the rails. Reads back `rail1` `rail1ID` `rail2` `rail2ID` `parallel` `numCurves`. |
| `NURBSBlendSurface` | YES | **Works end-to-end.** `parent1:` `parent2:` `edge1:` `edge2:` `tension1:` `tension2:`. Executed: two point surfaces + a blend -> 3 surfaces, readback `parent1=0 parent2=0 edge1=1 edge2=1 tension1=1.0`, `evalPos(0.5,0.5)` = `[-50.0011,100,100]`. It is the **LAST** surface in the set (3.19). **`tension1`/`tension2` are not neutral at `1.0` — `0.0` is the straight transition, and `1.0` overshoots both edges by an unbounded amount (3.20).** |
| `NURBSOffsetSurface` | YES | Offset surface; takes `parent:` / `parentID:` and `distance:` (verified earlier, P4, via F6). A dependent surface like the others — 3.14 applies, and 3.15's count-based guard applies to it too. |
| `NURBSProjectVectorCurve` | YES | **Works — as a projection, not a cut.** `parent1:` `parent2:` `pVec:` `seed:` `trim:` `flipTrim:`. Executed: a plane + a closed 5-point circle above it with `pVec:[0,0,-1] trim:true` -> readback `parent1=0 parent2=0 seed=[0.5,0.5] trim=true flipTrim=false`. **Corrected 2026-10-04: the "second surface" earlier revisions reported is the parent's untrimmed `NURBSCVSurface` copy, and `trim:true` does not trim — 3.25, 3.26.** `pVec` reads back sign-flipped (3.17). |
| `NURBSDisplay` | YES | Display control object, passed to `setSurfaceDisplay`. |
| `NURBSSurfaceApproximation` | YES | View/render approximation, passed to `setViewApproximation` / `setRenderApproximation`. Accepts `config:#meshOnly`, `meshApproxType:#parametric` / `#spatialAndCurvature`, `meshUSteps`, `meshVSteps`, `spacialEdge`, `curvatureAngle`, `curvatureDistance`, `merge`, `subdivStyle:#grid`. |
| `NURBSNode` | **NO — special syntax** | Not a constructor. Build with `NURBSNode nset name:"..."` (no parentheses). The resulting node's `classOf` is `NURBSSurf`; it shows in the UI as **"CV Surf"**. |
| `NURBSControlVertex` | **YES — corrected** | Constructs fine: `NURBSControlVertex <point3>` or `NURBSControlVertex <point3> <weight>`. A bare array also coerces. Earlier revisions of this file wrongly recorded it as non-constructable — that was **never executed**, only assumed. See section 2.3. |
| `Loft` | **NO** | Resolves as a class, but `Loft()` throws `Not creatable: Loft`. Use `NURBSULoftSurface`. |
| `Point_Surf`, `CV_Surf` | YES | **Valid MAXScript identifiers** (earlier revisions of this file wrongly called them non-scriptable). |
| `QuadPatch()` | YES | Instance class `quadPatch`. Freeform control-net surface. |
| `Surface()` | YES | Instance class `surface`. Surface primitive. |
| `Edit_Patch()` | YES | Modifier for patch sub-object editing. |

### 1.2 Executed proof of the relational workflow

Everything below ran and returned these values:

```
nset = NURBSSet()                          -> NURBSSet
appendObject nset <curve>                  -> returns the STRING "OK"   (NOT an index)
node = NURBSNode nset name:"TestShell"     -> classOf node == NURBSSurf
getNURBSSet node #relational               -> NURBSSet, numObjects = 11
superClassOf of sub-objects                -> NURBSSurface / NURBSCurve / NURBSPoint
evalPos surf 0.0 0.0                       -> [0, 0, 0]
evalPos surf 0.5 0.5                       -> [0.347105, -0.343283, 0.130161]
evalPos surf 1.0 1.0                       -> [0.698976, -0.683715, 0.260751]
evalUTangent surf 0.5 0.5                  -> [0.698954, -0.683764, 0.000429974]
uParameterRange / vParameterRange          -> [0.0, 307.703]
```

Two facts to internalise from that block:

1. **`appendObject` returns `"OK"`, a string.** Any code that feeds its return value into an integer
   slot breaks. This is bug 1 below.
2. **Parameter ranges are NOT normalised to [0, 1].** The measured range is `[0.0, 307.703]`. Do
   not assume `u = 0.5` means the middle of the surface. Always read `uParameterRangeMin` /
   `uParameterRangeMax` (and the V equivalents) off the sub-object and lerp inside those bounds.
   Sampling with hardcoded 0.0 / 0.5 / 1.0 will silently evaluate near a corner, not across the
   surface.

### 1.3 The canonical relational workflow

```maxscript
(
local nset = NURBSSet()
local pc   = MCP_NURBS_Arch.makePointCurve [[0,0,0],[100,0,0],[100,100,50]] name:"Sec1"
appendObject nset pc
local idx  = nset.numObjects                  -- NOT the return value of appendObject

local loft = NURBSULoftSurface name:"Shell" renderable:true generateUVs1:true matID:1
appendCurve loft idx flip:false
appendObject nset loft

local node = NURBSNode nset name:"TestShell"
local disp = NURBSDisplay displayCurves:false displaySurfaces:true displayDependents:true displayTrimming:true
setSurfaceDisplay node disp
node
)
```

`MCP_NURBS_Arch.makeCVCurve` and `.makePointCurve` both return valid objects, and the library file
loads cleanly and prints `MCP_NURBS_Arch loaded`.

### 1.4 Rail sweeps, blends and projected trims — executed proof

These are the **dependent** sub-objects: each one points at other members of the same set, and those
pointers are resolved only at commit. Executed 2026-10-04. Control in the same batch:
`TotalGarbageXYZ123` -> `undefined`; `(NURBS1RailSweepSurface()).totalBogusName` -> `ERR`;
`(.totalBogusName: "zzz")` -> silently ignored.

**Recovered keyword map** — existence proved by type mismatch (3.18), values by commit + read-back:

| Class | Keywords that exist |
| :--- | :--- |
| `NURBS1RailSweepSurface` | `rail` `railID` `parallel` `numCurves` `axisTM` |
| `NURBS2RailSweepSurface` | `rail1` `rail1ID` `rail2` `rail2ID` `parallel` `numCurves` |
| `NURBSBlendSurface` | `parent1` `parent1ID` `parent2` `parent2ID` `edge1` `edge2` `tension1` `tension2` |
| `NURBSOffsetSurface` | `parent` `parentID` `distance` (verified earlier, P4, via F6) |
| `NURBSProjectVectorCurve` | `parent1` `parent1ID` `parent2` `parent2ID` `pVec` `seed` `trim` `flipTrim` |

Transcripts:

```
NURBS1RailSweepSurface   3-point rail + 3 appended cross-sections
  -> numObjects = 14, index 14 is the surface
  -> u = [0,1]   v = [0,1]
  -> evalPos(0.5, 0.5) = [500,0,100]        -- the exact expected midpoint

NURBS2RailSweepSurface   two parallel rails 500 cm apart + 3 transverse sections
  -> u = [0,1]   v = [0,1]
  -> evalPos(0.5, 0.5) = [550,200,0]        -- the exact midpoint between the rails

NURBSBlendSurface        two point surfaces + blend
  -> 3 surfaces in the set; the blend is the LAST one
  -> readback: parent1=0 parent2=0 edge1=1 edge2=1 tension1=1.0
  -> evalPos(0.5, 0.5) = [-50.0011,100,100]

NURBSProjectVectorCurve  plane + closed 5-point circle above it, pVec:[0,0,-1], trim:true
  -> readback: parent1=0 parent2=0 seed=[0.5,0.5] trim=true flipTrim=false
  -> surfaces = #(10,11)                    -- CORRECTED 2026-10-04. That second surface is the
                                              -- PARENT's untrimmed NURBSCVSurface copy. It is NOT
                                              -- evidence of a cut. trim:true does not trim: 3.25, 3.26
```

Five facts to internalise:

1. **Both sweep types have a `[0,1]`-normalised domain**, unlike a `point_grid` surface, whose domain
   is chord-length. Read the parameter range before sampling either way — just do not expect the two
   situations to behave alike.
2. **`parent:` / `rail:` / `rail1:` do not read back the index you passed.** They read `0`, and an
   `*ID` keyword reads an **`IntegerPtr`** that prints as a large decimal followed by `P`. See 3.16
   and 3.23.
3. **An invalid dependent surface is silently dropped** — the sweep with no rail set committed
   `numObjects = 7` with no `NURBSSurface` at all, while the same sweep with `rail:` set committed
   `numObjects = 14`. See 3.15.
4. **Which surface is "the" surface depends on its position in the set**, not on its class: the sweep
   derivative test reads the **first** `NURBSSurface`, a `NURBSBlendSurface` is the **last**. See 3.19.
5. **A blend's `tension` is not a neutral `1.0`, and `trim:true` is not a trim.** Both were read as
   neutral defaults and both were wrong; `tension 1.0` overshot a 900 cm plan by 295 cm and `trim:true`
   cut nothing. See 3.20 and 3.25.

---

## 2. The three real bugs in `snippets/nurbs_arch_library.ms`

**The library loads successfully.** `makeCVCurve` and `makePointCurve` work and return valid
objects. This is a **bugfix job, not a rewrite job** — the API calls, class names and object model in
that file are correct.

**Status: all four bugs fixed and every one of the ten library functions was executed live on
2026-10-04 (Max 2026.3.2).** `snippets/nurbs_arch_library.ms` is now clean.

| # | Bug | Symptom (exact error) | Fix | State |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `appendObject` returns the string `"OK"`, not an index. The library did `append crvIndices (appendObject nset pc)` and then `appendCurve uLoft idx` | `Unable to convert: OK to type: Integer` | After `appendObject nset obj`, read the index from `nset.numObjects` | ✅ applied |
| 2 | `stopCreating` takes ZERO arguments; the library called `stopCreating node` — 4 call sites | `Argument count error: StopCreating wanted 0, got 1` | Drop the argument: `stopCreating` | ✅ applied |
| 3 | **Was wrongly recorded as "`NURBSControlVertex` does not construct."** It constructs fine. The real fault was that `setCV` does not auto-coerce a raw point | `Unable to convert: [0,0,0] to type: NURBSControlVertex` | `setCV crv i (NURBSControlVertex (pts[i] as point3) w)` — the wrapper is mandatory, the class is not | ✅ applied |
| 4 | `close <crv>` returns `"OK"` and does **not** mutate. `closed:true` in the `NURBSCVCurve` constructor is silently ignored, and `isClosed` is read-only | `makeCVCurve closed:true` returned an open curve, silently | `closed:true` is now honoured seam-wise (first CV repeated as last). `NURBSPointCurve closed:true` is native and reliable — prefer it for closed sections | ✅ applied |

### 2.1 Bug 1 — `appendObject` returns `"OK"`, not an index

**What the code did.** In `createULoftShell` (and the same pattern in `createUVLoftNetwork`) it
collected the return value of `appendObject` into an index list:

```maxscript
-- BROKEN
append crvIndices (appendObject nset pc)      -- crvIndices gets the string "OK"
...
appendCurve uLoft idx flip:false              -- idx is "OK"
```

**Why it happens.** `appendObject` is a status-style function: it returns the string `"OK"` on
success (executed: `ret1=OK cls=OkClass n=1`). The append itself worked; only the *return value* is
useless as an index. Every failure downstream is a type conversion, not a geometry failure.

**Fix — use `nset.numObjects` as the index of the object just appended:**

```maxscript
nset = NURBSSet()
idxs = #()
for i = 1 to sectionPointsList.count do (
    local pc = MCP_NURBS_Arch.makePointCurve sectionPointsList[i] name:("Sec" + (i as string)) closed:true
    appendObject nset pc
    append idxs nset.numObjects      -- NOT the return value of appendObject
)
```

Note the corrected name expression: `("Sec" + (i as string))`, with the parentheses — `+` binds
tighter than `as`, so `("Section_" + i as string)` is `(("Section_" + i) as string)` and throws
`Incompatible types: 1, and ": "`. All such sites in the library were corrected.

### 2.2 Bug 2 — `stopCreating` takes no arguments

**What the code did.** `stopCreating node` at the top of `applyArchTessellation`,
`inspectNURBSSet`, `sampleSurfaceToQuadPoly`, and `createDiagridOnSurface` — 4 call sites.

**Exact error:** `Argument count error: StopCreating wanted 0, got 1`

**Why it happens.** `stopCreating` is a global mode flag ("stop auto-creating further NURBS
sub-objects"). It takes no node reference — it is not a per-node operation.

**Fix.** Delete the argument at all four sites:

```maxscript
stopCreating
local rset = getNURBSSet node #relational
```

### 2.3 Bug 3 — `NURBSControlVertex` constructs; `setCV` just needs the wrapper

**The previous version of this section was a fabricated blocker.** It claimed
`NURBSControlVertex` "does not construct" and told readers to distrust `makeCVCurve` output. That
claim was never executed. Executed on 2026-10-04:

```
NURBSControlVertex [10,0,0]              -> NURBS_cv([10,0,0], 1)
NURBSControlVertex (point3 1 2 3)        -> NURBS_cv([1,2,3], 1)
NURBSControlVertex (point3 1 2 3) 0.5    -> NURBS_cv([1,2,3], 0.5)
setCV c 1 (NURBSControlVertex (point3 55 66 77) 0.5)  -> getCV c 1 = NURBS_cv([55,66,77], 0.5)
```

Arity is 1 or 2; the second argument is the weight and defaults to `1.0`. The value stringifies as
`NURBS_cv([x,y,z], weight)`.

**The actual defect** is that `setCV` and `setPoint` do not auto-coerce a bare point:

```maxscript
setCV   c 1 [0,0,0]    -- ERROR: Unable to convert: [0,0,0] to type: NURBSControlVertex
setPoint p 2 [7,8,9]   -- ERROR: Unable to convert: [7,8,9] to type: NURBSIndependentPoint
```

so the wrapper is mandatory. The library now writes `(NURBSControlVertex (pts[i] as point3) w)` and
`(NURBSIndependentPoint (pts[i] as point3))`; the `as point3` cast also makes array input from
JSON specs safe.

**Note:** there is **no `setWeight` and no `getWeight`** — `No "SetWeight" function for
<NURBSCVCurve>`. Weight is only settable through the two-argument `NURBSControlVertex` constructor.

### 2.4 Bug 4 — `NURBSCVCurve` cannot be closed, and `close` is a silent no-op

Executed 2026-10-04:

```
NURBSCVCurve closed:true      -> isClosed = false      -- kwarg silently ignored
crv.isClosed = true           -- Unknown property: "isClosed" in <NURBSCVCurve>
crv.closed  = true            -- Unknown property: "closed"  in <NURBSCVCurve>
close crv                     -> returns OkClass ("OK"); crv.isClosed still false
NURBSPointCurve closed:true   -> isClosed = true       -- control: this one works
```

So the original `if closed do close crv` inside `makeCVCurve` was a no-op that silently discarded the
requested closure — a `closed:true` call produced an open curve with no error. The same `close` call
existed in `makePointCurve`, where it was merely redundant (the constructor kwarg works).

**Fix applied.** `makeCVCurve` now materialises `closed:true` **seam-wise**: the first control vertex
is repeated as the last one, so the curve starts and ends on the same point. This is a documented
approximation, not topological closure — `isClosed` still reads false and always will. For a truly
closed curve use `makePointCurve` / `NURBSPointCurve`.

This is the same failure family as bug 1: **several NURBS mutators are status-style and return
`"OK"` instead of doing anything observable.** Never trust the return value of `appendObject` or
`close`; read state back with `getCV` / `isClosed` / `nset.numObjects` instead.

---

## 3. MAXScript surface gotchas (verified)

Each entry: the failing form, the working form, and the exact error text. All of these came out of
preflight probes that were themselves wrong on a first pass — the failure modes are real and
repeatable.

### 3.1 `fileExists` does not exist

| | |
| :--- | :--- |
| Failing | `fileExists "C:/x.ms"` -> undefined function |
| Working | `doesFileExist "C:/x.ms"` -> boolean |

### 3.2 `executeFile` / `runScript` do not exist

Use **`fileIn`** to run a script file.

| | |
| :--- | :--- |
| Failing | `executeFile "C:/x.ms"`, `runScript "C:/x.ms"` -> undefined function |
| Working | `fileIn "C:/x.ms"` |

This is the function to use to load `snippets/nurbs_arch_library.ms`.

### 3.3 `stopCreating` takes 0 arguments

See section 2.2. `Argument count error: StopCreating wanted 0, got 1`.

### 3.4 `modifiers <node>` function form does not work

Use the `node.modifiers` **property**.

| | |
| :--- | :--- |
| Failing | `modifiers r` -> `ERR: Type error: Call needs function or class, got: undefined` |
| Working | `r.modifiers.count` -> `1` |

Indexing yields the full instance name with its class prefix: `r.modifiers[1] as string` is
`"sweep:Sweep"`, **not** `"Sweep"`. Read the bare name with `r.modifiers[1].name` -> `"Sweep"`, and let
any string test tolerate the prefix.

### 3.5 Standalone modifiers cannot be deleted

Only scene nodes can be deleted. A bare modifier is not in the scene graph.

| | |
| :--- | :--- |
| Failing | `local s = Sweep(); delete s` -> `ERR: -- No "delete" function for sweep:Sweep` |
| Working | Do not delete it. To clean up, attach it to a throwaway node and delete the **node**: `local s = Rectangle(); addModifier s (Sweep()); delete s` |

### 3.6 `introspect_class` paramBlock reflection is wrong for shapes

| | |
| :--- | :--- |
| Misleading | `introspect_class "Rectangle"` returns `paramBlocks: []` and `interfaces: []` |
| Reality | `Rectangle()` exposes `width` / `length` (default `25.0`, assignable). Verified live: `r.width = 40.0`, then `r.width` -> `40.0` |

**Never conclude "this object has no parameters" from `introspect_class`.** Probe with MAXScript
assignment-and-readback instead, which is definitive.

### 3.7 `maxVersion()` returns an array; `get3dsMaxVersion()` does not exist

| | |
| :--- | :--- |
| Failing | `get3dsMaxVersion()` -> `ERR: -- Type error: Call needs function or class, got: undefined` |
| Failing | `getMaxVersion` -> also undefined |
| Working | `maxVersion()` -> `#(28000, 68, 0, 28, 3, 2, 30788, 2026, ".3.2 Security Fix")` |

The major version is **index 8** (1-based) = `2026`; element 9 is the patch string. Do not concatenate
the array as if it were a version string. This is the body used by the version probe in
`scripts/env_preflight.py`, verbatim:

```maxscript
(
local v = maxVersion()
"major=" + ((v[8]) as string) + " full=" + (v as string)
)
```

### 3.8 Material identifiers are internalNames, not display names

| | |
| :--- | :--- |
| Failing | `execute "OpenPBRMaterial"` -> absent |
| Working | `execute "OpenPBR"` -> constructs, `classOf (OpenPBR())` == `OpenPBR_Material` |

Three-way name split: display name `OpenPBR Material`, construction identifier `OpenPBR`, instance
class `OpenPBR_Material`. `PhysicalMaterial` and `Standard` happen to match across all three, which is
why the `OpenPBR` mismatch is easy to miss.

| Identifier | Result | Instance class |
| :--- | :--- | :--- |
| `OpenPBR` | ok | `OpenPBR_Material` |
| `PhysicalMaterial` | ok | `PhysicalMaterial` |
| `Standard` | ok | `Standardmaterial` |

Not constructible in this build: no Arnold-specific materials, no `VRayMtl`, no Octane, no
`RS_Standard_Material`. Sixteen Corona classes are constructible (CoronaPhysicalMtl, CoronaMtl /
CoronaLegacyMtl, CoronaLayeredMtl, CoronaHairMtl, CoronaFabricMtl, CoronaSkinMtl, CoronaToonMtl,
CoronaVolumeMtl, CoronaPortalMtl, CoronaShadowCatcherMtl, CoronaRaySwitchMtl, CoronaOutlineMtl,
CoronaSlicerMtl, CoronaScannedMtl, CoronaSelectMtl, CoronaLightMtl). The parameterised material tools
in `02-mcp-live-orchestration.md` section 4.7 take the internalName, so this bites the moment a script
hands a display name to `assign_material` or `palette_laydown`.

### 3.9 String precedence: `("x" + i as string)`

| | |
| :--- | :--- |
| Failing | `("Section_" + i as string)` -> `Incompatible types: 1, and ": "` |
| Working | `("Section_" + (i as string))` |

`as string` binds tighter than `+` without parentheses, so MAXScript tries to add an integer to the
format string. This appears in `snippets/nurbs_arch_library.ms` at every section-name construction
(lines 84, 107, 112) and must be fixed alongside bug 1.

### 3.10 `execute "<string>"` does not see the enclosing scope

`execute` compiles the string in a fresh global context. Local variables, `local` bindings and
closures from the calling script are **not** visible inside it. Any script you hand to
`3dsmax-mcp_execute_maxscript`, and any string you hand to `execute`, must be fully self-contained.
This is why every probe in this file declares its own locals inside its own parentheses.

### 3.11 Every class-existence probe needs a bogus control in the same batch

A class-existence probe MUST include a known-bogus identifier in the same batch.
`TotalGarbageXYZ123` correctly yields `undefined`. Without that control, a batch that returns all
`undefined` is indistinguishable from a batch that failed to run — which is precisely how the false
"NURBS API is fictional" conclusion was reached. See section 5.

### 3.12 CONFIRMED WORKING — do not re-investigate

`addModifier (Rectangle()) (Sweep())` succeeds via **all** of these forms. There is no `local`-related
pitfall; do not spend time on it again.

| Form | Live result |
| :--- | :--- |
| `s = Rectangle()` then `addModifier s (Sweep())` — no `local` | `s.modifiers.count` -> `1` |
| `local sh = Rectangle()` then `addModifier sh (Sweep())` | `sh.modifiers.count` -> `1` |
| `local r = Rectangle()` then `addModifier r (Sweep())` | `r.modifiers.count` -> `1` |
| `local sw = Sweep(); addModifier r sw` | `r.modifiers.count` -> `1` |

### 3.13 Chained property assignment after `addModifier` is invalid

You cannot append a property assignment to a function call; `addModifier` returns nothing, so there
is no lvalue to assign to.

| | |
| :--- | :--- |
| Failing | `addModifier s (Extrude()) amount = 50.0` -> `ERR:-- No ""="" function for (Global:addModifier CodeBlockLocal:s (Global:Extrude) CodeBlockLocal:amount)` |
| Working | `local ex = Extrude()` / `addModifier s ex` / `ex.amount = 50.0` -> `s.modifiers.count` is `1` |

Every recipe in this file binds the modifier to a variable first. There is no typed MCP tool that
writes modifier parameters post-application (see `02-mcp-live-orchestration.md` section 4.6), so the
two-step MAXScript form is the standard pattern here.

### 3.14 Dependent-surface properties are readable only on the COMMITTED sub-object

The most expensive gotcha in this file: it cost a whole architecture stage.

| | |
| :--- | :--- |
| Failing | `local o = NURBS1RailSweepSurface rail:1`, then `o.rail` / `o.railID` / `o.parallel` / `o.numCurves` / `o.axisTM` -> `ERR` on **every** name, including the four that do exist |
| Working | the same object after `appendObject nset o` + `NURBSNode nset`, read off the **committed sub-object**: `rail=0 railID="0P" parallel=true numCurves=3` |

**The commit is part of the measurement, not a detail of it.** Never probe a NURBS dependent
sub-object in a pre-commit state — build it, `appendObject`, `NURBSNode`, then read, exactly as in
section 1.3. P4 had already discovered this precise rule for `evalPos` ("a surface is not evaluable
until it is committed", section 1.2) and then failed to apply it one paragraph later. Worked
transcripts: section 1.4.

### 3.15 An invalid dependent surface is silently DROPPED at commit

No error, no warning — the sub-object simply is not in the set.

| | |
| :--- | :--- |
| Failing | sweep built with no rail set -> `numObjects = 7`, and **no `NURBSSurface` at all** |
| Working | the same sweep with `rail:` set -> `numObjects = 14`, index 14 is the surface |

So a script that ran to completion is **not** evidence that the surface exists, and neither is a
constructor that returned an object. Count the `NURBSSurface` sub-objects in the committed set and
fail loudly when the expected count is missing. Enumerate by superclass (section 1.2), never by
index:

```maxscript
(
-- node = the committed NURBSNode from section 1.3
local nset   = getNURBSSet node #relational
local nsurf  = 0
for i = 1 to nset.numObjects do
(
    if (superClassOf nset[i]) == NURBSSurface do nsurf += 1
)
nsurf          -- 0 means every dependent surface was dropped
)
```

### 3.16 `parent:` / `rail:` / `rail1:` do not read back the index you passed

| Passed | Reads back |
| :--- | :--- |
| `rail:` (1-based set index) | `0` |
| `rail1:` / `parent1:` / `parent2:` | `0` |
| `railID:` / `parent1ID:` / `parent2ID:` | an **`IntegerPtr`**, printed as a large decimal followed by `P` |

Measured on the committed sub-objects of both sweep types and of the blend. Never round-trip-assert on
these fields: they are pointers the set re-resolved, not the values you supplied. Assert on
**geometry** (`evalPos`) or on the surface **count** (3.15) — those are the values that decide whether
the shape is right.

> **Corrected 2026-10-04, then corrected AGAIN 2026-10-06 — the `"0P"` string form is real.**
> The 2026-10-04 note above retracted this file's own earlier `"0P"` reading as "not reproduced".
> **That retraction was wrong.** Both readings were the same thing: the value is an `IntegerPtr`
> printed as `<decimal>P`, and the two probes saw different *magnitudes* of the same format — see
> 3.29. The retraction has been removed because it was the **tenth** instance of this repo's
> signature error (a throw, or a difference from expectation, read as evidence about the feature) and
> the **second** one about an `nurbsID`. The operational rule is unchanged and is what 3.29
> actually settles: **never parse the string, never compare two of them, never write a literal** —
> for the reason in 3.16, which is not about the format at all.

### 3.17 `pVec` reads back with the OPPOSITE sign

Set `[0,0,-1]`, read `[0,0,1]`, on the committed projected curve. Do not assert that `pVec`
round-trips; assert `trim` / `seed` / `parent*` instead. This flip is specific to `pVec` — no other
keyword in the section 1.4 map was observed to invert.

### 3.18 A uniform result across a heterogeneous name list is a broken probe, not a uniform absence

This is the generalisable lesson, and it is why the four classes in section 1.4 were nearly written
off as unimplemented.

| | |
| :--- | :--- |
| Failing | `o["renderable"]` -> `ERR`, while `o.renderable` -> `true` |
| Also failing | `getProperty o #x` fails; `execute` inside a probe sees no enclosing locals (3.10) |

> **NARROWED 2026-10-06 (3.29).** The `getProperty` row is true only of the `#name` **literal**
> form. **`getProperty o ("name" as name)` works on these plugin classes** — measured on a
> committed `NURBS1RailSweepSurface`, where `getProperty surf "railID"` returned `0P` and the
> bogus name in the same sweep threw. It was already known to work on built-in classes
> (`CHECKPOINT.md`, P4b-r); it is now established for the NURBS family too. Use the coerced-string
> form for any name you do not want to hard-code.

`o["name"]` is **not** dynamic property access in MAXScript. A probe built on it returns `ERR` for
every name, including known-good ones — and it did, for all 15 candidates in the batch that produced
the false "not implemented" verdict. Never accept a probe result that is *uniform* across a
*heterogeneous* name list.

Three corollaries:

1. **A bogus control proves absence; a known-positive proves the probe can detect presence.** Every
   property-read probe needs both. Compare 3.11, which covers class-existence probes only. The P4
   probe had a bogus control and no positive, so the control alone did not save it.
2. **A successful construction proves nothing about a keyword.** The constructor silently accepts
   *any* name — `NURBS1RailSweepSurface totalBogusName: 1` constructs fine, bogus name ignored, no
   error.
3. **The only keyword-existence discriminator is a type mismatch.** Pass a string: a name that exists
   errors on conversion, a name that does not exist is swallowed. In the sweep-of-names probe,
   `rail railID parallel numCurves axisTM` errored on `rail: "zzz"` while `rail1 parent distance
   tension1` did not — and those non-erroring names are keywords of the *other* classes in the map
   (`rail1` -> `NURBS2RailSweepSurface`; `parent` / `distance` -> `NURBSOffsetSurface`). **Probe per
   class.**

### 3.19 Never hardcode a literal sub-object index — "the" surface depends on its position

| You are reading | Which `NURBSSurface` |
| :--- | :--- |
| a sweep derivative / panel sampling | the **FIRST** |
| a `NURBSBlendSurface` | the **LAST** |
| a shelled surface (base + offset) | the **first** — the last one is the offset shell |

The shelled-offset trap, measured: sampling the first surface gave panels `z 420 -> 600.97`;
sampling the last gave `441.043 -> 625.94` — a silent 25 cm error with no error raised anywhere.
Resolve by superclass *and* confirm that the surface you picked is the one carrying the relational
properties you just set (section 1.4). **Extended, not replaced, by 3.27** — a committed sub-object is
also enumerated by `classOf`, never by comparing its index against a pre-commit ordinal.

### 3.20 `NURBSBlendSurface` tension is not a neutral `1.0` — `0.0` is the straight transition

**`tension1` / `tension2` default to `0.0`, and `0.0` means "straight transition between the two
selected edges". Any value above `0` pushes the blend outward past *both* edges, and the overshoot
grows with the tension. Max does not bound it** — so a schema that leaves the tension unbounded is a
defect, not a neutral default.

Measured on the worked vault / canopy pair, 2026-10-04. Blend bbox from a 7 × 7 sample grid over the
blend's **own** committed domain (`uParameterRangeMin/Max`, `vParameterRangeMin/Max`, `evalPos`) —
**not** the node bbox, which also contains the two parents:

| edges | tension1/2 | blend bbox Y | blend bbox Z | read-back |
| :--- | :--- | :--- | :--- | :--- |
| `edge1:4 edge2:4` | `1.0 / 1.0` | **450 … 1195.64** | **369.758 … 600.97** | `e1=4 e2=4 t1=1.0 t2=1.0` |
| `edge1:4 edge2:4` | `0.5 / 0.5` | 450 … 995.514 | 401.084 … 600.97 | `e1=4 e2=4 t1=0.5 t2=0.5` |
| `edge1:4 edge2:4` | `0.0 / 0.0` | **450 … 900.0** | **420.0 … 600.97** | `e1=4 e2=4 t1=0.0 t2=0.0` |
| `edge1:4 edge2:4` | `1.0 / 0.0` | 450 … 1081.41 | 420.0 … 600.97 | `e1=4 e2=4 t1=1.0 t2=0.0` |
| `edge1:4 edge2:3` | `1.0 / 1.0` | **−72.222 … 972.222** | 364.105 … 600.97 | `e1=4 e2=3` |
| `edge1:3 edge2:4` | `1.0 / 1.0` | **−85.333 … 535.333** | 379.817 … 600.97 | `e1=3 e2=4` |

All six committed (`nObj=68`, three `NURBSSurface` sub-objects: two parents plus the blend).

**Reading.** The vault's high-V edge is `y = 900`; the canopy's high-V edge is `y = 450`. At
`tension 0.0 / 0.0` the blend fills **exactly** the gap between the two selected edges — `Y 450…900`,
`Z 420…600.97`, the vault springing at 420 through the 600.97 crown. That is a soffit panel and it is
correct. At `tension 1.0 / 1.0` the *same edge pair* bulges **295.64 cm past the vault's own
`y = 900`** and drops to `z = 369.758`, i.e. 50 cm below the springing. That is the
`SUR_006_CanopySoffit` defect: its node bbox reached `y = 1518` against a 900 cm deep plan.

| | |
| :--- | :--- |
| Failing | `tension1: 1.0 tension2: 1.0` read as "the default" — blend outside the building |
| Working | `tension1: 0.0 tension2: 0.0` — a straight soffit between the two edges |

### 3.21 A blend whose two edges are coincident is a **zero-area surface, silently**

No error, no warning, no drop — the sub-object commits, all four properties read back exactly as set,
and the surface has zero area.

Controlled pair, built 16 times in identical sets: `P` = 3 × 3 `NURBSPointSurface`, planar `z = 0`,
`x 0…200`, `y 0…200`; `Q` = 3 × 3 `NURBSPointSurface`, `x 200…400` rising to `z = 200` at `x = 400`,
`y 0…200`. `P`'s high-U edge is `x = 200` and `Q`'s low-U edge is also `x = 200` — the two **share** that
edge. Blend bbox per combination, 25-sample grid, `x,y,z`:

| | `edge2=1` | `edge2=2` | `edge2=3` | `edge2=4` |
| :--- | :--- | :--- | :--- | :--- |
| **`edge1=1`** | `−17.9,0,−28.1 … 200,200,0` | `0,0,0 … 400,200,213` | `−6.4,−37.6,0 … 400,200,200` | `−6.4,0,0 … 400,237.6,200` |
| **`edge1=2`** | **`200,0,0 … 200,200,0`** (zero area) | `200,0,0 … 419.4,200,203` | `200,−39.8,0 … 400,200,200` | `200,0,0 … 400,239.8,200` |
| **`edge1=3`** | `0,−28.1,−19.9 … 200,200,0` | `0,−39.8,0 … 400,200,217` | `0,−111.8,0 … 400,0,200` | `0,−1.2,0 … 400,201.2,200` |
| **`edge1=4`** | `0,0,−19.9 … 200,228.1,0` | `0,0,0 … 400,239.8,217` | `0,−1.2,0 … 400,201.2,200` | `0,200,0 … 400,311.8,200` |

Every one of the 16 committed (`nObj=21`, `nSurf=3`) and every `edge1` / `edge2` / `tension1` /
`tension2` **read back exactly as set**.

**Reading.**

- `edge1:2 edge2:1` — `P`'s **high-U** against `Q`'s **low-U**, the pair that is actually coincident —
  yields `200,0,0 … 200,200,0`: a **zero-area** surface, silently. (`edge1:2 edge2:2` is *not* the
  coincident pair; it produces a normal bulge.)
- A same-axis / same-side pair (`3/3`, `4/4`) yields a surface that bulges outside **both** parents —
  up to **111 cm on a 200 cm patch**.

**A blend is only sane when its two edges are neither coincident nor on the same side of the same
axis.** Neither failure is observable through any read-back: not through `evalPos` on a domain that
has collapsed, not through the property read-back, and not through the commit.

### 3.22 A blend spans the gap between the two selected edges — the parents need not touch

The `edge` convention is **low-U / high-U / low-V / high-V of that parent**: `1` low-U, `2` high-U,
`3` low-V, `4` high-V. The blend bridges the two selected edges; the parents are not required to meet,
and they do not have to be in the same `NURBSSet` (3.24).

In the worked example the two selected edges were `y = 450` and `y = 900` — a **450 cm gap**, with the
two parents disjoint in depth — and `tension 0.0 / 0.0` produced a panel spanning exactly `Y 450…900`.

### 3.23 `nurbsID` is an `IntegerPtr`, and a synthetic one **crashes 3ds Max**

| Passed as `parent1ID:` | Result |
| :--- | :--- |
| `"2276505581808P"` — a **string** | `ERROR: Unable to convert: "2276505581808P" to type: IntegerPtr` |
| the **raw value** read off a committed sub-object | the node commits and evaluates correctly (3.24) |
| `12345` — a **synthetic integer** | **`EXCEPTION_ACCESS_VIOLATION` — Access violation, read of address 0x0000000000003089** |

The third line is a **hard crash of the 3ds Max process**. It is not a MAXScript error and it is **not
recoverable from inside the script**. Max survived here only because the offending node had already
been built and the crash landed afterwards; the scene was left with orphans and needed a sweep.

| | |
| :--- | :--- |
| Failing | `NURBSBlendSurface parent1ID:12345 …` — an id you invented |
| Working | commit the parent node, then bind `local idX = (getObject (getNURBSSet parentNode #relational) <i>).nurbsID` and pass `parent1ID:idX` |

**Never emit a literal in a `parent*ID:` slot.** The same rule the P4b linter already applies to a
literal sub-object index applies here, with a worse failure mode.

> **RESOLVED 2026-10-06 — see 3.29.** The printed form is `<decimal>P` and the class is
> `IntegerPtr`; `railID = "0P"` was real. Still: **never parse it, never compare two of them,
> never write a literal** — for 3.16's reason, which is about what to assert, not about the format.

### 3.24 A relation's parents need **not** live in the relation's `NURBSSet`

`parent1ID:` / `parent2ID:` accept a surface committed in **another node's set**. Build the parents as
their own nodes, read each committed surface's `nurbsID`, and pass that raw value:

```maxscript
set = NURBSSet()
bl = NURBSBlendSurface parent1ID:<vaultID> edge1:4 parent2ID:<canopyID> edge2:4 \
                        tension1:0.0 tension2:0.0
appendObject set bl
node = NURBSNode set
```

Measured result — the relation set holds **one** sub-object, `evalPos` works, and the bbox is
**identical** to the in-set re-instantiation at the same tension:

```
node bb=[0,450,420]..[1800,900,603.016]
nObj=1
  1 NURBSSurface NURBSBlendSurface id=2276505582256P bbY=450.0..900.0 bbZ=420.0..600.97
     rd_p1=0 rd_p1id=2276505581808P
```

Blending a surface's `edge4` **with itself** (`parent1ID:` = `parent2ID:`) also commits: `bb=[0,900,420]
..[1800,900,603.588]`, `nObj=1`.

This is how the **duplicate-parent-geometry** defect is removed: re-instantiating a parent inside every
dependent set means a parent named by two relations exists three times in the scene.

> **Lifetime — one test, one outcome, not a guarantee.** After `delete` of the parent node the relation
> kept evaluating; no crash, no change:
>
> ```
> after parent delete: objects=1 ; rel nObj=1
> post-delete evalPos(0.5,0.5)=[899.861,900,600.97] rd_p1id=2559963908880P
> node bb now=[0,900,420]..[1800,900,603.588]
> ```
>
> Record that as *"did not break in the one case measured"*. **Do not** delete a parent node while a
> live relation still points at it on the strength of this one row.

### 3.25 `NURBSProjectVectorCurve trim:true` does **not** cut — it adds the parent back

Same vault (`thickness:0.0`), profile `SEC_023` (`x 750…1050`, `y 375…525`, `z 700`) projected with
`pVec [0,0,-1]`, `seed [0.5,0.5]`:

```
trim:true   -> nObj=7, set contains: NURBSCVSurface, 4x NURBSPoint, NURBSPointCurve, NURBSProjectVectorCurve
               NURBSCVSurface bb=[0,0,420 .. 1800,900,600.97]  dom u[0,1866.75] v[0,1866.75]
trim:false  -> nObj=6, no surface at all: 4x NURBSPoint, NURBSPointCurve, NURBSProjectVectorCurve
```

`flipTrim:true` changes only the read-back flag — it moves no geometry.

**The test that settles it.** To find out whether the surface is actually cut, widen the profile to
span the whole vault — `x −200…1900`, `y 300…500` — which a real trim would split into two disjoint
pieces:

```
PSPLIT nObj=7
  surf 1 NURBSCVSurface Y=0.0..900.0 Z=420.0..600.97 numCVs=[9,4]
nSurf=1
```

One piece, full `Y 0…900`, **byte-identical to the small profile's result**. So `trim:true` does not
split, does not cut, and does not vary with the profile: it adds a `NURBSCVSurface` **copy of the
parent**.

| | |
| :--- | :--- |
| Failing | `trim:true` believing an aperture is cut — the node now carries a duplicate of the parent shell |
| Working | `trim:false` — the relation contributes **0** `NURBSSurface` sub-objects |

**Cutting an aperture in a NURBS surface is not something this class does.** That needs **absent
material or a surface split**, which is outside the NURBS stage.

> **CORRECTED (verified 2026-10-06):** this read "a **Boolean modifier** or a surface split". The
> Boolean modifier is **unusable** in this build — it attaches and does nothing (section 5,
> "Boolean / solid ops"). The operative half — *not something this class does* — is unchanged.

> **RESOLVED 2026-10-06 — see 3.30.** `[9,4]` is the **parent's own** CV conversion: two different
> profiles give the same number, `u` follows the parent's points-per-section *and* its curvature, `v`
> is fixed at 4. It is not a finding about the trim and **nothing may be asserted on it**.

### 3.26 CORRECTION (2026-10-04) — "a second surface appears in the set" was read backwards

`CHECKPOINT.md`'s P4b row for `NURBSProjectVectorCurve` says it "works … **and a second surface appears
in the set**". **That second surface is the parent's `NURBSCVSurface` copy — not evidence of a trim.**
An earlier revision of this file repeated the inference in section 1.1 and section 1.4; both are
corrected in place above, and this entry dates the correction.

The generalisable form, and it belongs with 3.18: **an extra object appearing where you expected none
is not proof that the operation ran.** The test that would have caught it is cheap — run the operation
with two structurally different inputs and check whether the output differs. Here it did not: a profile
spanning the full vault width produced output identical to a small one. Re-running an operation with a
deliberately extreme input and looking for a *change* is the cheapest available probe against a silent
no-op.

### 3.27 Pre-commit append **ordinals** vs committed set **indices**

| Route | What the number means |
| :--- | :--- |
| `getObject rset i`, `rset[i]` | the **1-based index into the committed set** |
| `parent:` / `rail:` / `appendCurve` | the **pre-commit ordinal** returned by `nset.numObjects` immediately after `appendObject` |

They are not the same number, and the gap is not small. Two 3 × 3 point surfaces plus a blend:

```
nset = NURBSSet()
appendObject nset ps1   -> numObjects = 1
appendObject nset ps2   -> numObjects = 2
appendObject nset blend -> numObjects = 3
NURBSNode nset ->
  committed numObjects = 21
   1..9   NURBSPoint     (ps1's 9 points)
   10      NURBSSurface   NURBSPointSurface     <- ps1, appended first
   11..19  NURBSPoint    (ps2's 9 points)
   20      NURBSSurface   NURBSPointSurface     <- ps2, appended second
   21      NURBSSurface   NURBSBlendSurface     <- the blend
```

`parent1:1 parent2:2` resolved to committed indices 10 and 20 and the blend committed correctly, so the
emitted `local x = nset.numObjects` pattern is **correct**.

The broken thing is **filtering committed sub-objects by comparing against a pre-commit ordinal** —
`if k > <pre-commit ordinal>` silently reads the wrong object, with no error. That mistake cost one
probe. **Filter committed sub-objects by `classOf`, never by index arithmetic:**

```maxscript
for i = 1 to rset.numObjects do
(
    local o = getObject rset i
    if (classOf o) == NURBSBlendSurface do ( /* this is the blend */ )
)
```

**This extends 3.19 — it does not replace it.** 3.19 decides *which* surface is the design surface and
is still load-bearing; 3.27 adds how to *find* it without arithmetic.

### 3.28 Never measure a NURBS node's `min` / `max` and call it the NURBS geometry

A node's bounding box is inflated by the node's own tessellation. Measured: a **closed
`NURBSPointCurve`** over a `750…1050 × 375…525` control rectangle has node bbox
`714.645…1080.17 × 286.503…617.732` — inflated on all four sides.

| | |
| :--- | :--- |
| Failing | `node.min` / `node.max` quoted as the geometry's extent |
| Working | sample **`evalPos`** on the resolved sub-object over its real parameter domain |

`node.min` / `node.max` are legitimate for a **QA tolerance comparison against a node you have already
bounded another way** (§6.2's four numbers are exactly that kind of measurement). They are not a
measurement of the surface. Related: a closed `NURBSPointCurve` commits as its points **plus** the
curve and no surface (`nObj=5` for 4 points, `nObj=6` for 5 on an open one), so a point-curve row
contributes no `NURBSSurface` to the census at all.

### 3.29 `nurbsID` is an `IntegerPtr` printed as `<decimal>P` — measured 2026-10-06

This closes the item §7.6 carried open for two stages. All rows are committed-sub-object reads
(the 3.15 rule — pre-commit, every name in this section returns `ERR`), with a `matID` /
`numCurves` positive and `totalBogusXYZ` negative in the same batch.

| Fact | Evidence |
|---|---|
| **`classOf` is `IntegerPtr`.** The printed form is a large decimal with a literal `P` suffix | `3253572981568P` on five committed `NURBSPointCurve` sub-objects |
| **`railID` on a committed `NURBS1RailSweepSurface` really does read `0P`** — 3 reps of identical geometry, 3 readings of `0P`, with `rail = 0` | This is the value P4b recorded and the P4b round-2 pass failed to reproduce. **Both saw the same format at different magnitudes.** 3.16's retraction was itself a false negative |
| **`rail1ID` / `rail2ID` on a committed `NURBS2RailSweepSurface` read the full pointer, and it is the rail's own `nurbsID`** — `==` comparable, `rail1ID ≠ rail2ID ≠ nurbsID` | `rail1ID` matched the curve at committed index 4, `rail2ID` index 8 |
| The value **changes between builds of identical geometry** — 3 reps, 3 different pointers | **Never persist an `nurbsID`.** Bind it in the script that consumes it, which is what `G-56` already mandates |
| The two sweep classes have **disjoint vocabularies**: `rail` / `railID` throw on the 2-rail class, `rail1` / `rail2` throw on the 1-rail class | calibrated `getProperty` sweep |
| ⚠️ **`getProperty <o> (<name> as name)` works on these plugin classes.** 3.18's row *"`getProperty o #x` fails"* is true only of the `#name` literal form | `getProperty surf "railID"` → `0P`; the bogus name in the same sweep threw |
| ⚠️ **NEW TRAP — `appendCurve` takes an `Integer` ordinal, not the curve object.** Passing the object throws `Unable to convert: <NURBSPointCurve:0x…> to type: Integer` | First probe failed on exactly this; `appendCurve rel (set.numObjects)` succeeded immediately. It is a cousin of 3.27 — ordinals and indices, and the argument type is checked |

**The rule that survives is 3.16's, unchanged:** assert on `evalPos` or on the surface count, never
on the pointer. The format is now known and still must not be parsed, compared or written as a literal.

### 3.30 `numCVs [9,4]` on a trim copy is the PARENT's own CV conversion — measured 2026-10-06

The §7.6 observation "a 5-rib loft's `trim:true` copy reports `numCVs [9,4]`" is explained, and it
is **not** a trim artefact.

| Fact | Evidence |
|---|---|
| **The number belongs to the parent surface, not to the projected profile.** Two structurally different profiles over one vault — a 5-pt small rectangle and an 8-pt profile spanning the whole vault — both give `[9,4]` | 2 profiles × 1 parent |
| `u` tracks the parent's **points per section**: 9 points → `[9,4]`; 5, 6, 7 and 11 points → `[4,4]` | 7-case sweep, `p` and `r` varied independently |
| **`v` is fixed at `4` in every case**, including 2-section and 6-section parents | same sweep |
| `u` **also** depends on the parent's own curvature, not only its point count: scaling the vault's profile amplitude to `0.25` gives `[5,4]`, while `0.5` / `1.0` / `2.0` all give `[9,4]` | parent is 9 points in all four cases |
| The added object is a **`NURBSCVSurface`**, and its parent `NURBSULoftSurface` has **no** `numCVs` / `numPoints` / `uOrder` / `vOrder` / `numUKnots` / `numVKnots` — all throw | property sweep with a surface-class control |

**So the copy is Max's conversion of the parent into a CV surface, and `numCVs` reports that
conversion.** It is a function of the parent's geometry in a form this repo cannot predict, so
**no rule may be written against it.** `G-54`'s census counts sub-objects, not CVs, and is
unaffected. `trim:false` adds no surface at all (3.25), re-confirmed on this parent.

---

## 4. The introspection trap — read this before trusting any tool that claims a class is missing

This is the failure that produced the false headline. Three of the introspection tools report
negative or guessed results:

- **`introspect_class "NURBSSet"` returns `Class not found: NURBSSet` — and that is WRONG.** The
  class exists, constructs, and evaluates. Never use this tool alone to claim a class does not exist.
- **`discover_plugin_classes superclass=NURBS` returns 0.** The superclass name it expects is wrong.
  Do not rely on this call for the NURBS family.
- **`inspect_plugin_constructor` returns `inferred: true`** with guessed `category` / `creatable`
  fields. Treat as hypothesis, never as fact. This is how the `Loft` "creatable" trap was set.
- **The DLL class scan is incomplete:** it listed 78 of 160 modifiers and omitted classes MAXScript
  can instantiate.

Corollaries that still hold:

- **`NURBSObject` is the ROOT of the entire MAXScript hierarchy.** Every value descends from it, so
  seeing `NURBSObject` in a `classOf` result tells you nothing about a NURBS surface API.
- **Name resolution is not constructibility.** `Loft` resolves and is not creatable. Always attempt
  the construction.
- **A display name in the DLL scan is not a scriptable identifier** — but its *absence* there does not
  mean the class is unscriptable either. The scan is wrong in both directions.

**Standing rule: MAXScript execution is the only ground truth.**

### 4.1 The corrected detection recipe

1. Resolve via `execute "<name>"`.
2. Attempt construction.
3. **Always include a known-bogus control (`TotalGarbageXYZ123` -> `undefined`) in the same batch.**
   If the control does not come back `undefined`, the batch itself is broken and every result in it is
   void.
4. Remember `execute "<string>"` sees no enclosing scope (section 3.10) — keep each snippet
   self-contained.

Reusable, control-tested detector:

```maxscript
(
local function probe nm callExpr =
(
    local out = (nm as string) + " : "
    local ident = undefined
    try (ident = execute nm) catch (ident = undefined)
    if ident == undefined then
        out += "undefined\n"
    else
    (
        out += "resolves (" + (ident as string) + ") -> "
        try
        (
            local o = execute callExpr
            out += "CREATED, classOf = " + ((classOf o) as string)
            try (delete o) catch ()          -- only scene nodes delete cleanly; failures are fine
        )
        catch (out += "construct throws: " + (getCurrentException()))
    )
    out
)

-- name, then the actual call expression to try (some constructors need arguments)
local cases = #(
    #("NURBSSet",              "NURBSSet()"),
    #("NURBSULoftSurface",     "NURBSULoftSurface()"),
    #("NURBSPointCurve",       "NURBSPointCurve()"),
    #("NURBSControlVertex",    "NURBSControlVertex()"),
    #("TotalGarbageXYZ123",    "TotalGarbageXYZ123()")   -- CONTROL: must be undefined
)

local rep = ""
for c in cases do rep += probe c[1] c[2]
rep
)
```

Read the result as: every row before the control is trustworthy; if the control row is not
`undefined`, discard the whole batch and fix the snippet. A constructor that resolves but throws
`Not creatable` (like `Loft`) is recorded as **non-creatable** regardless of name resolution.

---

## 5. Surface modifiers on shapes

`Sweep()`, `Lathe()`, `Extrude()` construct and apply to **shape** objects only. Verified shape hosts:
`Line`, `NGon`, `Donut`, `PipeObject`, `Rectangle`, `Circle`, `Ellipse`, `Arc`, `Star`, `Helix`,
`Text`, `Half Round`, `Quarter Round`.

On geometry such as a `Box` they throw `Modifier is not appropriate`. Verified behaviour:

| Modifier | Instance class | Superclass | Applies to |
| :--- | :--- | :--- | :--- |
| `Sweep()` | `sweep` | `modifier` | shapes only — `addModifier (Rectangle()) (Sweep())` succeeds; on a Box: `Runtime error: Modifier is not appropriate: sweep:Sweep` |
| `Lathe()` | `lathe` | `modifier` | shapes only (verified on `Rectangle`) |
| `Extrude()` | `extrude` | `modifier` | shapes only (verified on `Rectangle`) |
| `QuadPatch()` | `quadPatch` | `GeometryClass` | constructs standalone |
| `Surface()` | `surface` | geometry | constructs standalone |
| `Edit_Patch()` | — | `modifier` | applies to patches |

Also listed as shapes but internal/utility: Point Curve, CV Curve, LinkLeaf, LinkComposite,
PolymorphicGeom, LinkBlockInstance.

DLL-scan geometry inventory, for orientation only (the scan is incomplete — see section 4): Box,
Sphere, Cylinder, Target, Quad Patch, Tri Patch, Torus, Morph, Tube, Cone, Hedra, Spray, Snow,
Teapot, Plane, Bone, Boolean, ChamferBox, ChamferCyl, OilTank, Spindle, Capsule, Gengon, Prism,
Pyramid, C-Ext, L-Ext, Spring, Damper, Hose, Editable Mesh, Editable Poly (internalName
`EditablePolyMesh`), Terrain, PointCloud, Body Object/Utility/Join/Cutter, PhysXShapeConvex, Biped
Object, Populate Skin, Flow, Seat, ControlContainer, Global Container, Apollo Param Container,
ChaosScatter, CFractal, CDecal, CVolumeGrid, CProxy, CGaussianSplats, USD Stage, USDGeomObject,
LinkLeaf, LinkComposite, PolymorphicGeom, LinkBlockInstance, FbxMaxWrapper, Point Surf, CV Surf,
NURBS Imported Objects. `ChaosScatter` constructs; `CScatter` is its base class and is **NotCreatable**
— always use `ChaosScatter`.

Note: `spray` / `snow` here are legacy particle **emitters** (geometry objects), **NOT** tyFlow. Do
not confuse them with the absent tyFlow plugin.

### 5.1 Recipes that work

**Extruded footprint (slab, wall, plinth).**

```maxscript
(
local s = Rectangle()
s.width = 400.0
s.length = 200.0
local ex = Extrude()
addModifier s ex
ex.amount = 50.0
s
)
```

**Swept surface along a rail.** Rail: a `Line` / `Arc` / `Helix` / `NGon` shape. Profile: a
`Rectangle` / `Circle` shape. Bind the modifier, apply, then read back through `.modifiers`.

```maxscript
(
local rail = Line([0,0,0], [0,0,300])
local prof = Rectangle()
prof.width = 40.0
prof.length = 40.0
local sw = Sweep()
addModifier rail sw
rail.modifiers.count        -- 1
rail.modifiers[1]           -- sweep:Sweep
rail.modifiers[1].name      -- "Sweep"
prof
)
```

> **UNVERIFIED.** The exact sub-object wiring parameter names for assigning the profile to `Sweep`
> were not verified. `Sweep` works on shapes and `addModifier rail sw` succeeds, but *how* the profile
> is bound (`.shapes`, `.CustomShape`, `.current_built_in_shape`, sub-object level, thresholds) must
> be introspected first — see section 7.2. Guessing a parameter name produces a silent no-op or a
> runtime error inside the modifier.
>
> A profile shape must be cleaned up by deleting the shape node itself; a bare modifier cannot be
> deleted (section 3.5).

`Sweep` has a built-in cross-section list (Angle, Bar, Channel, Cylinder, Half Round, Pipe, Quarter
Round, Tee, Tube, Wide Flange) that may cover simple architectural mouldings without a custom profile
— see `arch-modifiers-and-procedural-reference.md`.

**Revolved surface (domes, columns, balusters, canopies).**

```maxscript
(
local prof = Line([0,0,0], [0,0,120])
local lt = Lathe()
addModifier prof lt
lt.degrees = 360.0
prof
)
```

**Freeform control net.** `QuadPatch()` plus `Edit_Patch()`.

```maxscript
(
local p = QuadPatch()
addModifier p (Edit_Patch())
p
)
```

> **UNVERIFIED.** The control-point access API for `QuadPatch` in MAXScript was not verified. The
> constructor and modifier both apply, but the property names for reading and writing the control net
> are unknown — see section 7.3. For a freeform architectural shell, prefer the relational route in
> section 1.3, which is verified.

**Boolean / solid ops — the Boolean modifier is UNUSABLE in this build.** It is *not* the route for
cutting openings in slabs and walls. Measured 2026-10-05 against live 3ds Max 2026.3.2, every probe
batched with a bogus-name control that came back `undefined` (full table: `07` §8.5.8.1,
`agents/max-assembly.md` §6.2.1):

| Probe | Measured |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs, `classOf` reads `BooleanMod`, but its paramblock is **Voxel Map's** (`voxelSize`, `toleranceFactor`, `bevelDistance`, `bevelDepth`); `VoxelMap()` is itself `NotCreatable` |
| `ProBoolean()` | constructs, `superClassOf` is `GeometryClass` not Modifier, and constructing one **leaves a node in the scene** |
| the bridge's `add_modifier` with `"Boolean"` | genuinely **attaches** — `node.modifiers` reads `#modifiers(Boolean:Boolean)` — and the **operand is never set**: `snapshotAsMesh` reports `verts=8 faces=12`, unchanged, for every `params` spelling tried |
| `isProperty m #operation` / `#object` / `#boolobject` | all **`false`**, and the bogus control is also `false`, so those names genuinely do not exist |
| `getModifier 1 node` | **throws**; `node.modifiers[1]` works |

**A modifier that attaches and does nothing is worse than one that throws** — so the earlier
`assembly.ms` shipped unpierced walls and *reported success*, because its census counted iterations
of its own loop (`cut_count = 16`) against a scene with **zero** modifiers anywhere.

**The working route is to express the opening as absent material, not as a cutter.** There is no
cutter object at all: the wall is built from **solid cells that tile wall-minus-openings exactly** —
`wall_cells[]` in `assembly.json`, one rectangle in plan plus a `z_range_cm` per box, cut at every
opening's `u` boundary into columns and then at the covering openings' `v` boundaries into rows.
This stage emits **no modifier at all** (`G-81`), and the tiling is asserted as a volume identity
(`G-82`/`G-83`) — which is the check a Boolean could never have satisfied, since a modifier that
removes nothing leaves the volume untouched. See `07` §8.5.8.

**Tessellation quality for viewport and render.** NURBS patches are approximated, not tessellated by
an exporter, and **there is no export stage in this pack** — export was cancelled by user decision on
2026-10-05 and no exporter exists, so treat any pre-export advice below as a statement about what you
see and render. The NURBS-native controls are `NURBSSurfaceApproximation` wired via
`setViewApproximation` / `setRenderApproximation` (see section 1.3); `Disp Approx` / `Tessellate` are
the modifier-stack alternatives. ⚠️ `curvatureAngle` on `NURBSSurfaceApproximation` is in **degrees**
— passing `degToRad` over-tessellates (~6.9× measured); see `snippets/nurbs_arch_library.ms` §5.

> **UNVERIFIED.** Whether `Disp Approx` or `Tessellate` is the correct path for patches specifically
> was not verified — `Disp Approx` is display-only in some configurations, and a render-time
> approximation is not necessarily the one the viewport shows. See section 7.4.

---

## 6. Planning rules derived from this file

1. **The NURBS API is fully usable.** Plan lofts, blends, offsets, rail sweeps and relational
   shells directly. There is no rewrite of `nurbs-complete-guide.md` to do.
2. **Never read an index from `appendObject`.** It returns the string `"OK"`. Use `nset.numObjects`
   after the call.
3. **Never pass an argument to `stopCreating`.** It takes zero.
4. **Never trust a NURBS mutator's return value as proof of effect.** `appendObject` and `close` both
   return `"OK"` while `close` changes nothing at all. Read state back (`getCV`, `isClosed`,
   `nset.numObjects`).
5. **Always wrap points for `setCV` / `setPoint`.** `NURBSControlVertex` and `NURBSIndependentPoint`
   do construct, but the setters reject a bare point or array.
6. **There is no `setWeight` / `getWeight`.** Weight is set only via
   `NURBSControlVertex <pt> <weight>`.
7. **`NURBSCVCurve` cannot be closed.** `closed:true` is ignored, `isClosed` is read-only, `close` is
   a no-op. Use `NURBSPointCurve closed:true`, or accept seam-wise closure.
8. **Parameter ranges are not normalised.** Read `uParameterRangeMin` / `Max` before sampling.
9. **`NURBSNode` is special syntax** — `NURBSNode nset`, no parentheses. It displays as "CV Surf".
10. **Loft via `NURBSULoftSurface` / `NURBSUVLoftSurface`,** never `Loft` (resolves, not creatable).
11. **Shape first, then surface modifier.** Any recipe applying `Sweep` / `Lathe` / `Extrude` to
    geometry is broken by construction.
12. **Probe before you write the property name.** Every sub-object and control-point detail flagged
    UNVERIFIED in this file must be introspected first — and "introspected" means executed, per
    section 4. A claim recorded as "unresolved" without an execution transcript has been wrong here
    twice; treat every unexecuted claim as a hypothesis, not a blocker.
13. **Mind the surface syntax rules** in section 3: `.modifiers` property not function form; never
    `delete` a bare modifier; never chain a property assignment onto `addModifier`; `doesFileExist`
    not `fileExists`; `fileIn` not `executeFile`/`runScript`; `maxVersion()` is an array; material
    identifiers are internalNames; parenthesise `(i as string)`; `execute` sees no enclosing scope.
14. **Commit before you read, and count what you committed.** Relational properties on a dependent
    surface exist only after `appendObject` + `NURBSNode` (3.14), and a surface whose rail or parent
    is unresolved is **dropped silently** — so verify the committed set contains the expected number
    of `NURBSSurface` sub-objects instead of trusting the script to have run (3.15).
15. **Never round-trip-assert on `parent:` / `rail:` / `rail1:` / `railID:` / `pVec`.** They read back
    `0`, an **`IntegerPtr`** (never a string — see 3.29), or a sign-flipped vector (3.16, 3.17).
    Assert on `evalPos` or on the surface count.
16. **Never hardcode a sub-object index, and never trust a uniform property-probe result.** Which
    surface is the design surface depends on its position — a sweep reads the first, a blend is the
    last (3.19); and a probe that returns the same result for every candidate name is a broken probe
    (3.18). Find the sub-object by **`classOf`**, not by index arithmetic (3.27).
17. **A blend's neutral is `tension 0.0`, and its two edges must be neither coincident nor on the same
    side of the same axis.** `1.0` is not a neutral default — it overshot a 900 cm plan by 295 cm; a
    coincident pair gives a zero-area surface; a `3/3` or `4/4` pair bulges outside both parents. All
    three failures are silent (3.20, 3.21).
18. **Never emit a literal in a `parent*ID:` slot.** `nurbsID` is an `IntegerPtr`; a string errors and a
    synthetic integer **crashes the 3ds Max process**. Bind it from a committed sub-object (3.23).
19. **`trim:true` projects; it does not cut.** It adds an untrimmed copy of the parent to the relation's
    set. Emit `trim:false` and expect 0 surfaces. An aperture is **absent material or a surface
    split**, outside this class (3.25, 3.26).
    > **CORRECTED (verified 2026-10-06):** this read "a **Boolean modifier** or a surface split". The
    > Boolean modifier is **unusable** in this build (section 5, "Boolean / solid ops"); the measured
    > route is solid cells that tile wall-minus-openings. The operative half — *a surface split, not a
    > trim* — is unchanged.
20. **`parent:` / `rail:` / `appendCurve` take a pre-commit append ordinal; `getObject` takes a
    committed index.** The emitted `local x = nset.numObjects` pattern is correct — filtering committed
    sub-objects against a pre-commit ordinal is not (3.27).
21. **Sample `evalPos` to measure NURBS geometry — never `node.min` / `node.max`.** A node bbox is
    inflated by the node's own tessellation: a closed point curve over a `750…1050 × 375…525`
    rectangle reads `714.645…1080.17 × 286.503…617.732` (3.28).

---

## 7. Remaining open items for P4

Each item below is genuinely unresolved **as of 2026-10-04**. The exact
`3dsmax-mcp_execute_maxscript` probe to run is given; every snippet is self-contained and cleans up
after itself. Per section 4, include a known-bogus control wherever the result is a class-existence
claim, and never trust `introspect_class` — MAXScript execution is the fallback and the arbiter.

> **Closed since the previous revision of this file:**
> - ~~7.1 `NURBSControlVertex` construction route (bug 3)~~ → **RESOLVED and the claim was false.**
>   The class constructs; `setCV` simply requires the wrapper. Full executed transcript in
>   section 2.3.
> - ~~Bug 1 `appendObject` / Bug 2 `stopCreating`~~ → both fixed in
>   `snippets/nurbs_arch_library.ms`, and all four bugs re-verified by executing every one of the
>   ten library functions (section 2, "Status" row).
>
> **Still open for P4:** claim-by-claim verification of `references/nurbs-complete-guide.md` and
> `references/nurbs-architecture-recipes.md`. Both files still contain the *pre-fix* patterns that
> are now known to be wrong — `appendObject` used as an index, `stopCreating <node>`, `close <crv>`
> as a real close, `setCV` with a raw point. Those recipes are inherited from the library's original
> bugs, so they are expected to fail until corrected. Verify by execution; correct only what fails.

### 7.1 RESOLVED — `NURBSControlVertex` and the `setCV` path

The probe that closed it (retained because the recipe is reusable for any wrapper class):

```maxscript
(
local out = ""
local cands = #("NURBSControlVertex", "NURBS_CV", "CV", "ControlVertex",
                "NURBSIndependentPoint", "NURBSPoint", "Point")
for nm in cands do
(
    local made = "n/a"
    try
    (
        local o = execute (nm + "([0,0,0])")
        made = "CREATED, classOf = " + ((classOf o) as string)
        try (delete o) catch ()
    )
    catch (made = "throws: " + (getCurrentException()))
    out += nm + " : " + made + "\n"
)
out += "CONTROL TotalGarbageXYZ123 : " + ((try (execute "TotalGarbageXYZ123") catch ("throws: " + (getCurrentException()))) as string) + "\n"
out
)
```

Then, once a constructor is found, verify the real `setCV` path end-to-end on a curve and read back
whether the control net actually changed. **This exact probe returned `setCV ok` and
`getCV 1 = NURBS_cv([10,20,30], 1)` on 2026-10-04** — the "does not construct" claim was wrong:

```maxscript
(
local out = ""
local crv = NURBSCVCurve name:"CVProbe" closed:false
crv.order = 3; crv.numCVs = 4; crv.numKnots = 7
try
(
    setCV crv 1 (NURBSControlVertex [10,20,30] 1.0)
    out += "setCV ok\n"
)
catch (out += "setCV failed: " + (getCurrentException()) + "\n")
try (out += "getCV 1 = " + ((getCV crv 1) as string) + "\n") catch (out += "getCV unavailable\n")
try (setCV crv 2 [10,20,30]; out += "raw point accepted\n") catch (out += "raw point REJECTED: " + (getCurrentException()) + "\n")
out
)
```

The last line is the load-bearing check: the raw-point form is **rejected**, which is why the wrapper
is mandatory. Report both the `setCV` outcome *and* the read-back, never just the function's return
value.

### 7.2 Sweep modifier sub-object / profile-assignment parameter names

> Apply the modifier to a real node and delete the **node** at the end. A bare `Sweep()` must never be
> deleted (section 3.5) and the stack must be read through `.modifiers` (section 3.4).

```maxscript
(
local rail = Line([0,0,0], [0,0,300])
local sw   = Sweep()
addModifier rail sw
local out  = "stack=" + ((rail.modifiers.count) as string) + "\n"
for p in (getPropNames sw) do
(
    try (out += (p as string) + " = " + ((getProperty sw #p) as string) + "\n") catch ()
)
delete rail
out
)
```

Fallback — enumerate the modifier sub-anim tree:

```maxscript
(
local rail = Line([0,0,0], [0,0,300])
local sw   = Sweep()
addModifier rail sw
local out = ""
for i = 1 to (numSubs sw) do
(
    local sa = getSubAnimByIndex sw i
    out += "subAnim " + (i as string) + ": " + (sa.name as string) + "\n"
    try (for p in (getPropNames sa) do out += "    " + (p as string) + "\n") catch ()
)
delete rail
out
)
```

Third fallback, and the one that works even when SDK-side reflection is empty (section 3.6): reach
the modifier back off the node and read it directly.

```maxscript
(
local rail = Line([0,0,0], [0,0,300])
local sw   = Sweep()
addModifier rail sw
local m = rail.modifiers[1]
local out = "node.modifiers[1] = " + ((m) as string) + "\n"
for p in (getPropNames m) do
(
    try (out += "    " + (p as string) + "\n") catch ()
)
delete rail
out
)
```

### 7.3 `QuadPatch` control-point access API

```maxscript
(
local p = QuadPatch()
local out = "classOf = " + ((classOf p) as string) + "\n"
for prop in (getPropNames p) do
(
    try
    (
        local v = getProperty p #prop
        if (isArray v) then out += prop + " : array[" + ((v.count) as string) + "]\n"
        else out += prop + " : " + ((classOf v) as string) + "\n"
    )
    catch (out += prop + " : <inaccessible>\n")
)
out += "numSubs = " + ((numSubs p) as string) + "\n"
delete p
out
)
```

Also probe the `Edit_Patch` modifier for control-vertex property names, since refinement is the
architecturally useful path:

```maxscript
(
local p = QuadPatch()
local ep = Edit_Patch()
addModifier p ep
local out = ""
for prop in (getPropNames ep) do
(
    try (out += prop + " : " + ((classOf (getProperty ep #prop)) as string) + "\n")
    catch (out += prop + " : <inaccessible>\n")
)
delete p
out
)
```

### 7.4 Correct tessellation path for patches — viewport / render, NOT export

> **CORRECTED (verified 2026-10-06):** this item was titled "pre-export tessellation path". **There is
> no export stage in this pack** — export was cancelled by user decision on 2026-10-05 and no exporter
> exists. The probe below is still the right one; it asks whether the modifier-stack alternatives to
> `setViewApproximation` / `setRenderApproximation` apply to patches at all.

```maxscript
(
local p = QuadPatch()
local out = ""
out += "Tessellate creatable: "
try (local t = Tessellate(); addModifier p t; out += "yes\n") catch (out += "NO -> " + (getCurrentException()) + "\n")
out += "DispApprox creatable: "
try (local d = Disp_Approx(); addModifier p d; out += "yes\n") catch (out += "NO -> " + (getCurrentException()) + "\n")
delete p
out
)
```

If `Tessellate` / `Disp_Approx` do not resolve, do not fall back to the DLL scan for names — probe
candidate identifiers by construction with a bogus control (section 4.1). Then verify the viewport
and render result end-to-end on one patch before trusting it on a model.

### 7.5 Tri Patch / `Point_Surf` / `CV_Surf` creation paths — UNVERIFIED

`Point_Surf` and `CV_Surf` are valid identifiers; their *creation signatures and parameters* are
unverified, as is any Tri Patch identifier.

```maxscript
(
local out = ""
local cands = #("TriPatch", "Tri_Patch", "trPatch", "Point_Surf", "CV_Surf")
for nm in cands do
(
    local ident = "unresolved"
    try (local v = execute nm; if v == undefined then ident = "undefined" else ident = "resolves (" + (v as string) + ")") catch (ident = "resolve throws: " + (getCurrentException()))
    local made = "n/a"
    if ident != "undefined" and ident != "unresolved" do
    (
        try
        (
            local o = execute (nm + "()")
            made = "CREATED, classOf = " + ((classOf o) as string)
            try (delete o) catch ()
        )
        catch (made = "throws: " + (getCurrentException()))
    )
    out += nm + " : " + ident + " | " + made + "\n"
)
out += "CONTROL TotalGarbageXYZ123 : " + ((try (execute "TotalGarbageXYZ123") catch ("throws: " + (getCurrentException()))) as string) + "\n"
out
)
```

Any identifier that resolves but throws `Not creatable` is the `Loft` situation: record it as
non-creatable regardless of name resolution. `NURBSPointSurface` and `NURBSCVSurface` both construct
(section 1.1), so prefer them over `Point_Surf` / `CV_Surf` until the surface-creation signatures are
confirmed.
### 7.6 Open after the P4b round-2 relational probes (2026-10-04)

Each is genuinely unresolved. None may be filled in from a plausible guess — per section 4, that has
been the failure mode six times in this repo.

| Item | What is known | What is open | Pointer |
|---|---|---|---|
| ~~**The printed string form of an `*ID`**~~ | **RESOLVED 2026-10-06 — see 3.29.** `IntegerPtr`, prints `<decimal>P`. `railID="0P"` **was real**; the P4b round-2 "not reproduced" note was wrong in the opposite direction from P4b's own claim. `rail1ID`/`rail2ID` read the full pointer and equal the rail curve's own `nurbsID` | — closed | 3.29 |
| ~~**`numCVs = [9,4]`** on the `trim:true` copy of a **5-rib loft**~~ | **RESOLVED 2026-10-06 — see 3.30.** It is the **parent's own** CV conversion, not the profile and not the trim. Two structurally different profiles both give `[9,4]`; `u` tracks the parent's points-per-section *and* its curvature; `v` is fixed at 4 | — closed; **no rule may be written against it** | 3.30 |
| **A cross-set `rail1ID:` / `rail2ID:` form** | `parent1ID:` / `parent2ID:` referencing another node's set **works** (3.24) | Whether the **rail** side has the same form. A rail is a curve in the same set and uses `rail:` by ordinal; the id form for rails has **no** transcript | 3.24, 3.27 |
| **Lifetime of a relation after its parent node is deleted** | One case measured: no crash, no geometry change | Whether that holds generally. **One test, one outcome** — not a guarantee, and not a licence to delete a parent a live relation points at | 3.24 |
| **A sane ceiling for `tension1` / `tension2`** | `0.0` is the straight transition; overshoot above it is **unbounded** by Max and grows with tension (3.20) | The bound. A schema that leaves it unbounded is a defect, but the number is a design decision, not a measurement | 3.20 |
