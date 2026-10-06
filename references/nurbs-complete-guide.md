# NURBS Modeling in 3ds Max — Complete MAXScript & MCP Agent Reference

> **Purpose:** Authoritative reference for creating, inspecting, modifying, trimming, and tessellating NURBS curves and surfaces in Autodesk 3ds Max (2023–2027) via `execute_maxscript` / `execute_python` within `3dsmax-mcp`.
> Read this file before authoring any `NURBSSet` or manipulating `Editable Surface` / `NURBS` scene nodes.

---

## 1. Architectural Overview: How 3ds Max NURBS Work

Unlike standard primitives (`Box`, `Sphere`) or `SplineShape` / `Editable_Poly` where you directly mutate the scene node, **3ds Max uses an indirect relational container architecture for NURBS**:

1. **Internal Representation vs. MAXScript Wrapper:**
   - Inside a 3ds Max scene, a NURBS object is a single scene node whose internal C++ class ID is `EDITABLE_SURF_CLASS_ID`. **CORRECTED (verified 2026-10-06):** the scene-node class is **`NURBSSurf`** when the node contains any surface, and **`NURBSCurveshape`** when it contains curves only. The class names previously listed here (`CV_Surf`, `Point_Surf`, `Point_Curve`, `CV_Curve`) are not the `classOf` of any NURBS node built from a `NURBSSet`; `CV_Surf()` does not even construct, while `Point_Surf()`, `CV_Curve()` and `Point_Curve()` construct as classes but never appear as a node's `classOf`. Measured: 5-rib `NURBSULoftSurface` node → `classOf` = `NURBSSurf`; `NURBSPointSurface`-only node → `classOf` = `NURBSSurf`; `NURBSPointCurve`-only node → `classOf` = `NURBSCurveshape`; `convertToNURBSCurve` of a `Rectangle` → `classOf` = `NURBSCurveshape`. Both classes have `superClassOf` = `GeometryClass`.
   - Inside that single scene node lives an entire **relational graph of sub-objects**: Points, Control Vertices (CVs), Independent Curves, Dependent Curves (fillets, blends, offsets, surface-edge curves, projected curves, iso curves), Independent Surfaces (`NURBSCVSurface`, `NURBSPointSurface`), and Dependent Surfaces (`NURBSULoftSurface`, `NURBSUVLoftSurface`, `NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface`, `NURBSExtrudeSurface`, `NURBSLatheSurface`, `NURBSFilletSurface`, `NURBSOffsetSurface`, `NURBSCapSurface`, `NURBSMultiCurveTrimSurface`, etc.).
2. **The `NURBSSet` Container:**
   - To create a NURBS object from scratch, you instantiate a `NURBSSet()`, append `NURBSObject` sub-objects to it via `appendObject <nurbsset> <nurbsobj>`, link dependent sub-objects to their parents using **1-based set indices**, and then instantiate the scene node with `NURBSNode <nurbsset> name:"..."`.
   - To inspect or modify an existing NURBS node in the scene, you always call `stopCreating` (zero arguments) first, and then extract a live relational set via `getNURBSSet <node> #relational`.
   - To append new dependent curves/surfaces to an **already existing** scene NURBS node, you create a secondary `NURBSSet()`, reference existing parents via their **`.nurbsID`** (`parentID`, `railID`, `appendCurveByID`, etc.), and merge the set into the node via `addNURBSSet <node> <newNurbsSet>`. **CORRECTED (verified 2026-10-06): `addNURBSSet` returns `ok` but is a silent no-op in Max 2026.3.2 — it does not merge.** See the note under §5.3; four independent variants were executed and none added anything.

---

## 2. CRITICAL RULE #1: Set Index (`index`) vs. `NURBSId` (`nurbsID`)

The #1 cause of broken scripts and C++ Assertion Failures in 3ds Max NURBS is confusing **Set Index** with **`NURBSId`**. Memorize this lifecycle rule:

> **CORRECTED (verified 2026-10-06): the id type.** This section was the one place that named a type **`NURBSId`** and described it as *"an opaque runtime integer"*. **There is no `NURBSId` class.** The type is **`IntegerPtr`**. It prints as `<decimal>P` (e.g. `3253572981568P`; `railID` reads `0P` on a committed 1-rail sweep). Two rules follow, and both are hard:
>
> - **Never parse it and never compare two of them.** It is an address, not a value.
> - **Never write a literal into a `parent1ID:` / `parent2ID:` slot.** A **string** there is a plain conversion error; a **synthetic integer** there is an `EXCEPTION_ACCESS_VIOLATION` that **kills the 3ds Max process**. Bind the id from a committed sub-object **in the same script that consumes it**.
>
> `NURBSId` is still used below as shorthand for *the concept* (the relational-link identifier), and in
> method signatures such as `appendCurveByID <uloft> <curve_nurbsID>` where Autodesk's own
> documentation uses it. Wherever a *type* is being asserted, it is `IntegerPtr`. **This file's own
> §4.2 entry for `.nurbsID` (~line 172) already stated `IntegerPtr` correctly** — the two agreed, and
> this note is only reconciling the earlier section with it.

| Lifecycle State | How Sub-Objects Are Identified | Properties / Methods to Use |
| :--- | :--- | :--- |
| **1. Uninstantiated `NURBSSet`** (Before calling `NURBSNode nset`) | **1-based Set Index** (`1, 2, 3...` in the order `appendObject` was called). `.nurbsID` is `0` / invalid. | `.parent`, `.parent1`, `.parent2`, `.rail`, `.rail1`, `.rail2`, `.surfaceParent`, `appendCurve`, `appendUCurve`, `appendVCurve`, `setParent`, `setCurve` |
| **2. Instantiated `NURBSSet` or Relational Set** (After `NURBSNode nset` OR returned by `getNURBSSet node #relational` OR after `addNURBSSet node nset`) | **Relational id** (`.nurbsID` property on each sub-object). **CORRECTED (verified 2026-10-06): this cell previously read "`NURBSId` … an opaque runtime integer assigned by 3ds Max" — the type is `IntegerPtr`, an address printing as `<decimal>P`, and it must be bound from a live committed sub-object, never written as a literal.** Set indices are **no longer valid** for linking! | `.parentID`, `.parent1ID`, `.parent2ID`, `.railID`, `.rail1ID`, `.rail2ID`, `.surfaceParentID`, `appendCurveByID`, `appendUCurveByID`, `appendVCurveByID`, `setParentID`, `setCurveByID`, `breakCurve`, `breakSurface`, `joinCurves`, `joinSurfaces`, `makeIndependent`, `transform` |
| **3. Non-relational `NURBSSet`** (Returned by `getNURBSSet node` *without* `#relational`, or after `disconnect nset`) | **1-based Set Index** (All dependent surfaces/curves are baked/decomposed into independent `NURBSCVSurface` / `NURBSCVCurve` objects; disconnected from the scene node). | `getObject nset i` (with the loop counter `i`) |
> **VERIFIED (2026-10-06):** the bake-to-independent half of row 3 is confirmed — `getNURBSSet node` (no `#relational`) returns the `NURBSULoftSurface` as a `NURBSCVSurface`, `disconnect <nset>` succeeds and leaves it that way, and `deleteObjects <nset>` frees it. **But `.index` is NOT a usable set index:** it read `0` on every object of both a relational and a non-relational set (16 object classes checked). Use `getObject nset i` driven by the loop counter, as Recipe 3A does.

> **DOC ERRATA WARNING (`NURBSUVLoftSurface`):**
> In Autodesk's official MAXScript documentation for `NURBSUVLoftSurface`, the descriptions of `appendUCurve` and `appendUCurveByID` are accidentally swapped in the text! In actual 3ds Max C++ implementation:
> - `appendUCurve <uvloft> <set_index>` takes the **1-based `NURBSSet` index** (use before `NURBSNode`).
> - `appendUCurveByID <uvloft> <nurbsID>` takes the **relational id** (an `IntegerPtr`; use on relational sets). **CORRECTED (verified 2026-10-06):** this errata block originally wrote the second parameter as a type named `NURBSId`; see the note at the head of §2 — the type is `IntegerPtr`.
> The same applies to `appendVCurve <uvloft> <set_index>` vs `appendVCurveByID <uvloft> <nurbsID>`.

---

## 3. CRITICAL RULE #2: The Mathematical Knot/Order/CV Invariant

The 3ds Max NURBS C++ SDK performs almost zero bounds checking before invoking the internal math kernel. Passing invalid knot counts or non-monotonic knot vectors triggers a modal C++ **Assertion Failure** dialog (`BLOCKED_BY_DIALOG` in MCP).

### 3.1 The Fundamental Equation
For **every** `NURBSCVCurve` and `NURBSCVSurface`, the following equation **MUST** hold strictly:

$$\text{numKnots} = \text{order} + \text{numCVs}$$

- **`order`** $= \text{degree} + 1$:
  - `order = 2` (Degree 1): Linear polyline/faceted surface (requires at least `2` CVs, `4` knots).
  - `order = 3` (Degree 2): Quadratic curve/surface (requires at least `3` CVs, `6` knots).
  - `order = 4` (Degree 3): **Standard Cubic NURBS** (G2 curvature continuous; requires at least `4` CVs, `8` knots).
- **Order of Property Assignment Matters!**
  Changing `.numCVs` or `.numKnots` wipes existing CV/knot arrays. Always set properties in this exact sequence:
  1. `c.order = 4`
  2. `c.numCVs = N`
  3. `c.numKnots = N + 4`
  4. Populate all knots (`1` to `numKnots`) via `setKnot`
  5. Populate all CVs (`1` to `numCVs`) via `setCV`

### 3.2 Clamped Knot Vector Formula (Endpoint Interpolation)
For an open curve or surface to touch its first and last CVs (standard CAD/architectural behavior), its knot vector must have **multiplicity = `order`** at both ends, and monotonically non-decreasing interior knots in $[0.0, 1.0]$:

- First `order` knots (`k = 1` to `order`): `0.0`
- Interior knots (`k = order + 1` to `numCVs`):
  $$\text{knot}[k] = \frac{k - \text{order}}{\text{numCVs} - \text{order} + 1.0}$$
- Last `order` knots (`k = numCVs + 1` to `numCVs + order`): `1.0`

```maxscript
-- Universal helper to configure a Clamped Knot Vector on any NURBSCVCurve:
fn setClampedKnots crv ord nCVs = (
    crv.order = ord
    crv.numCVs = nCVs
    crv.numKnots = ord + nCVs
    local numSpans = (nCVs - ord + 1) as float
    for k = 1 to ord do setKnot crv k 0.0
    for k = (ord + 1) to nCVs do (
        setKnot crv k ((k - ord) / numSpans)
    )
    for k = (nCVs + 1) to (ord + nCVs) do setKnot crv k 1.0
)
```

For a `NURBSCVSurface`, the exact same rule applies independently in **U** and **V**:
- `s.uOrder = uOrd; s.vOrder = vOrd`
- `s.numCVs = [nU, nV]`
- `s.numUKnots = uOrd + nU; s.numVKnots = vOrd + nV`
- Populate `setUKnot s k val` (`1` to `numUKnots`) and `setVKnot s k val` (`1` to `numVKnots`) before calling `setCV s u v cv`!

---

## 4. Complete Class Hierarchy & API Reference

### 4.1 Container & Associated Classes

#### `NURBSSet : Value`
Container for constructing or inspecting NURBS models.
- **Constructors:**
  - `NURBSSet [<prop>:<val>...]`
  - `getNURBSSet <node> [#relational]`
- **Properties:**
  - `.numObjects : integer` (read-only) — number of sub-objects in the set
  - `.count : integer` (read-only) — alias for `.numObjects`
  - `.display : NURBSDisplay` — viewport display flags
  - `.viewApproximation : NURBSSurfaceApproximation`
  - `.renderApproximation : NURBSSurfaceApproximation`
  - `.merge : float` — edge tessellation merge tolerance (prevents cracks between adjacent surfaces at render time; set to `0.05`–`0.5` for architectural shells)
  - Direct tessellation shortcuts on `NURBSSet`:
    - `.viewConfig`, `.renderConfig` (`#isoOnly`, `#isoAndMesh`, `#meshOnly`)
    - `.viewIsoULines`, `.viewIsoVLines`, `.renderIsoULines`, `.renderIsoVLines` (`integer`)
    - `.viewMeshUSteps`, `.viewMeshVSteps`, `.renderMeshUSteps`, `.renderMeshVSteps` (`integer`)
    - `.viewMeshApproxType`, `.renderMeshApproxType` (`#parametric`, `#spatial`, `#curvature`, `#regular`, `#spatialAndCurvature`)
    - `.viewSpacialEdge`, `.renderSpacialEdge` (`float`)
    - `.viewCurvatureAngle`, `.renderCurvatureAngle` (`float`, **in degrees** — see the correction under `NURBSSurfaceApproximation`)
    - `.viewCurvatureDistance`, `.renderCurvatureDistance` (`float`, % of bbox diagonal)
    - `.viewViewDependent`, `.renderViewDependent` (`boolean`)
- **Operators & Methods:**
  - `nset[i]` / `getObject <nurbsset> (<index> | <NURBSSelection>)` — 1-based retrieval
  - `appendObject <nurbsset> <nurbsobj>` — appends sub-object and returns the **string `"OK"`** (class `OkClass`), *not* an index. The new 1-based index is `<nurbsset>.numObjects`, read **after** the call.
  - `setObject <nurbsset> <index> <nurbsobj>` — replaces sub-object at 1-based index
  - `removeObject <nurbsset> <index>` — removes sub-object (renumbers higher indices down)
  - `disconnect <nurbsset>` — turns a live `#relational` set into an offline non-relational set
  - `deleteObjects <nurbsset>` — frees C++ memory held by the `NURBSSet`

> **CORRECTED (verified 2026-10-04):** `appendObject` does **not** return an index. Executed on Max 2026.3.2: `ret1 = OK cls = OkClass n = 1`. Any code of the form `local i = appendObject nset obj` or `append idxs (appendObject nset obj)` puts the string `"OK"` into an integer slot and fails. Write:
> ```maxscript
> appendObject nset uLoft
> local loftIdx = nset.numObjects   -- 1-based set index of uLoft
> ```

#### `NURBSSurfaceApproximation : Value`
Encapsulates tessellation settings for viewports or production rendering.
- **Constructor:** `NURBSSurfaceApproximation [<prop>:<val>...]`
- **Properties:**
  - `.config : #isoOnly | #isoAndMesh | #meshOnly`
  - `.isoULines : integer`, `.isoVLines : integer`
  - `.meshApproxType : #parametric | #spatial | #curvature | #regular | #spatialAndCurvature`
  - `.meshUSteps : integer`, `.meshVSteps : integer` (subdivisions per knot span in `#parametric` or total across surface in `#regular`)
  - `.spacialEdge : float` (% of bounding box diagonal unless `viewDependent:true`, then pixels)
  - `.curvatureAngle : float` (**in degrees**, e.g. `6.0`). **CORRECTED (verified 2026-10-06): this is DEGREES, not radians.** Measured on a 100 mm-radius quarter-cylinder `NURBSPointSurface` rendered with `meshApproxType:#curvature`: `curvatureAngle` `1.0` → 415 verts, `4.0` → 147, `7.0` → 87, `20.0` → 51, and `0.10472` (= `degToRad 6.0`) → 691. Under a radians reading every value at or above `2π` (6.283) would be an unconstrained "no limit" angle and would collapse to one identical minimum mesh — `7.0` and `20.0` do not (`87` vs `51`), and the curve is smooth and monotonic through `2π`, which is the degrees signature. The default value is also `20.0`, which is a sane degrees default and a meaningless `1146°` in radians. **Do not wrap this value in `degToRad`.**
  - `.curvatureDistance : float` (% of surface bounding box diagonal, e.g. `0.25`)
  - `.viewDependent : boolean`
  - `.merge : float` (seamless edge matching distance across sub-surfaces)
  - `.subdivStyle : #tree | #grid | #delaunay` (Advanced Surface Approximation; `#grid` is best for regular architectural quads, `#delaunay` for organic curvature)
  - `.minLevels : float`, `.maxLevels : float`, `.maxTris : integer`
- **Node Application Methods:**
  - `setViewApproximation <node> <NURBSSurfaceApproximation>`
  - `setRenderApproximation <node> <NURBSSurfaceApproximation>`
  - Per-surface tessellation methods: `getProdTess <surf> (#surface|#displacement|#curve)`, `setProdTess <surf> (#surface|#displacement|#curve) <approx>`, `getViewTess <surf> (#surface|#curve)`, `setViewTess <surf> (#surface|#curve) <approx>`.
  - **CRITICAL PITFALL:** Never call `getViewTess` or `setViewTess` with `#displacement`! Viewports do not support displacement tessellation and 3ds Max will immediately raise an Assertion Failure dialog.

#### `NURBSDisplay : Value`
Controls sub-object visibility on the NURBS node.
- **Constructor:** `NURBSDisplay [<prop>:<val>...]`
- **Properties (all `boolean`):**
  - `.displayCurves` — show/hide 3D curves in viewport (set `false` on finished architectural envelopes so construction curves don't clutter viewport captures!)
  - `.displaySurfaces` — show/hide surfaces
  - `.displayLattices`, `.displaySurfCVLattices`, `.displayCurveCVLattices`
  - `.displayDependents` — show/hide dependent objects
  - `.displayTrimming` — when `true`, trimmed regions are hidden (clipped); when `false`, full untrimmed surface is shown
  - `.degradeOnMove`, `.displayShadedLattice`
- **Node Application Method:** `setSurfaceDisplay <node> <NURBSDisplay>`

---

### 4.2 Base Class, Points & Control Vertices

#### `NURBSObject` (Abstract Base Class)
Inherited by all points, CVs, curves, and surfaces:
- `.name : string` — always give meaningful names (`"Footprint_South"`, `"Arch_Section_01"`, `"Canopy_Loft"`) for easy inspection!
- `.nurbsID : IntegerPtr` (read-only) — valid only after `NURBSNode` or `getNURBSSet #relational`. **CORRECTED (verified 2026-10-06):** the declared type is `IntegerPtr`, not `integer`; it prints as `<decimal>P` (e.g. `3252106519360P`) and **cannot be stored in an `Integer32` slot or an array of integers** — keep it in its own variable and pass it straight back into `parentID`/`appendCurveByID`.
- `.index : integer` (read-only) — reads `0` on every object in both relational and non-relational sets. **CORRECTED (verified 2026-10-06):** it is **not** the 1-based set index; use `getObject <nurbsset> <i>` with the loop counter instead.
- ~~`.isSelected : boolean`~~ — **DOES NOT EXIST (verified 2026-10-06).** A guarded `getProperty` read of `.isSelected` throws on all 16 curve classes and all 17 surface classes tested (34 classes), each with a working positive control in the same call. There is no sub-object selection flag on a NURBS sub-object in this build.

#### `NURBSControlVertex : NURBSObject`
Used by `NURBSCVCurve` and `NURBSCVSurface`.
- **Constructor:** `NURBSControlVertex <point3> [<weight_float>]` (default weight is `1.0`)
- **Properties:**
  - `.pos : point3` (in parent NURBS node's local coordinate system!)
  - `.x : float`, `.y : float`, `.z : float`
  - `.weight : float` (must be `> 0.0`; rational weight relative to neighboring CVs. For an exact $90^\circ$ circular arc with 3 CVs of order 3, the middle CV weight is $\cos(45^\circ) = \frac{\sqrt{2}}{2} \approx 0.70710678$).
- **VERIFIED (2026-10-04):** both `NURBSControlVertex <point3>` and `NURBSControlVertex <point3> <weight>` construct fine (weight defaults to `1.0`); a bare 3-element array coerces. The wrapper is **mandatory** in `setCV` — `setCV c 1 [0,0,0]` throws `Unable to convert: [0,0,0] to type: NURBSControlVertex`, so always write `setCV c 1 (NURBSControlVertex [0,0,0] 1.0)`. There is **no** `setWeight` / `getWeight` (both throw `No "SetWeight"/"GetWeight" function for <NURBSCVCurve>`); weight is settable only through the 2-argument constructor.

#### `NURBSPoint : NURBSObject` Subclasses
All points expose `.pos : point3`, `.x`, `.y`, `.z` (read/write on independent points, read-only on dependent points):
1. **`NURBSIndependentPoint <point3>`** — freestanding point or point inside `NURBSPointCurve` / `NURBSPointSurface`.
2. **`NURBSCurveConstPoint`** — point constrained to lie on a curve (`parent`/`parentID`, `uParam`, `type` (`#onCurve`/`#tangent`/`#normal`), `offset`, `normal`, `uTangent`, `trimCurve`, `flipTrim`).
   > **CORRECTED (verified 2026-10-06):** the constraint-mode property is **`.type`**, not `.pointType`, and the trim flag is **`.trimCurve`**, not `.trim`. Measured present: `pos x y z parent parentID uParam type offset normal uTangent trimCurve flipTrim`. `pointType` and `trim` are absent.
3. **`NURBSSurfConstPoint`** — point constrained to a surface (`parent`/`parentID`, `uParam`, `vParam`, `type`, `offset`, `uTangent`, `vTangent`, `normal`).
   > **CORRECTED (verified 2026-10-06):** as with the curve variant the property is **`.type`**, not `.pointType`. Measured present: `pos x y z parent parentID uParam vParam offset normal uTangent vTangent type`. `pointType` is absent.
4. **`NURBSPointConstPoint`** — point offset relative to another point (`parent`/`parentID`, `offset`).
5. **`NURBSCurveIntersectPoint`** — intersection of two curves (`parent1`/`parent1ID`, `parent2`/`parent2ID`, `flipTrim1`, `flipTrim2`).
   > **CORRECTED (verified 2026-10-06):** there are **no `seed1`, `seed2`, `trim1` or `trim2` properties** on this class. Measured present: `pos x y z parent1 parent2 parent1ID parent2ID flipTrim1 flipTrim2` and nothing else from the documented set — `seed1`, `seed2`, `seed`, `trim1`, `trim2`, `trimCurve` and `flipTrim` are all absent. **UNVERIFIED:** with no seed property the class has no measured way to steer which intersection is picked; there is no `setSeed`-style method either. Do not rely on a seed argument.
6. **`NURBSCurveSurfaceIntersectPoint`** — piercing point of a curve through a surface (`parent1` surface, `parent2` curve, `seed`, `trimCurve`, `flipTrim`).

---

### 4.3 NURBS Curve Classes (`NURBSCurve : NURBSObject`)

#### Common Properties & Methods on ALL `NURBSCurve` Subclasses
- `.isClosed : boolean` (read-only)
- `.numTrimPoints : integer` (read-only)
- `.parameterRangeMin : float`, `.parameterRangeMax : float` (read-only; **only valid after scene instantiation!**)
- `.matID : integer`
- `evalPos <nurbscurve> <u_param>` $\rightarrow$ returns `point3` in node-local space (must be instantiated in scene first).
- `evalTangent <nurbscurve> <u_param>` $\rightarrow$ returns tangent `point3` vector.

#### Independent Curves
1. **`NURBSCVCurve`**
   - Constructor: `NURBSCVCurve [name:<string>] [order:<int>] [numCVs:<int>] [numKnots:<int>] [closed:<bool>] [autoParam:#notAutomatic|#autoCentripetal|#autoUniform]`
   - Properties: `.order`, `.numKnots`, `.numCVs`, `.transform` (`matrix3`), `.endsOverlap` (read-only), `.autoParam`
   - Methods: `close <crv>`, `getKnot <crv> <i_1based>`, `setKnot <crv> <i_1based> <float>`, `getCV <crv> <i_1based>`, `setCV <crv> <i_1based> <NURBSControlVertex>`, `refine <crv> <u_param>`, `reparameterize <crv> (#centripetal | #uniform)`
   - **CORRECTED (verified 2026-10-04):** a `NURBSCVCurve` **cannot** be made topologically closed. `close <crv>` is a silent no-op — it returns `OK` (class `OkClass`) and does not mutate the curve. The constructor kwarg `closed:true` is silently ignored, `closed` and `isClosed` are not settable (both throw `Unknown property`), and `isClosed` always reads `false`. Do not rely on any of these to produce a closed CV curve.
2. **`NURBSPointCurve`** (Interpolates directly through points — easiest for architectural profiles/paths when exact knot math isn't needed!)
   - Constructor: `NURBSPointCurve [name:<string>] [numPoints:<int>] [closed:<bool>] [transform:<matrix3>]`
   - Properties: `.numPoints`, `.transform` (`.closed` does **not** exist — see the correction below)
   - Methods: `close <crv>`, `getPoint <crv> <i_1based>`, `setPoint <crv> <i_1based> (NURBSIndependentPoint <pt3>)`, `refine <crv> <u_param>`
   - **VERIFIED (2026-10-04):** `closed:true` in the constructor **does** work natively on `NURBSPointCurve` (`isClosed = true`). Prefer the constructor kwarg for any closed section or profile curve.
   - **CORRECTED (verified 2026-10-06):** the earlier note in this file also claimed `.closed` was a *settable property*. **It is not settable and not even readable.** `NURBSPointCurve().closed` throws on read and throws on write, with `numPoints` reading `0` as a positive control and `bogusZZ` throwing as the negative control in the same call. `.isClosed` is the only working flag, and it is read-only — set closure in the constructor, never afterwards.

#### Dependent 3D Curves
3. **`NURBSBlendCurve`** — smooth G2 curvature blend between endpoints of two curves:
   - `.parent1` / `.parent1ID`, `.parent2` / `.parent2ID`
   - `.flip1 : boolean`, `.flip2 : boolean` (`false` = start of curve, `true` = end of curve)
   - `.tension1 : float`, `.tension2 : float` (typically `1.0`)
4. **`NURBSFilletCurve`** — circular arc corner between two curves:
   - `.parent1` / `.parent1ID`, `.parent2` / `.parent2ID`, `.radius : float`
   - `.flip1`, `.flip2`, `.trim1`, `.trim2`, `.flipTrim1`, `.flipTrim2` (`boolean`)
5. **`NURBSChamferCurve`** — straight bevel corner between two curves:
   - `.parent1` / `.parent1ID`, `.parent2` / `.parent2ID`, `.length1 : float`, `.length2 : float`
   - `.flip1`, `.flip2`, `.trim1`, `.trim2`, `.flipTrim1`, `.flipTrim2` (`boolean`)
6. **`NURBSOffsetCurve`** — planar offset curve:
   - `.parent` / `.parentID`, `.distance : float`
7. **`NURBSMirrorCurve`** — mirrored curve across local axis:
   - `.parent` / `.parentID`, `.axis : #X | #Y | #Z | #XY | #XZ | #YZ`, `.transform : matrix3`, `.distance : float`
8. **`NURBSXFormCurve`** — transformed copy of a curve:
   - `.parent` / `.parentID`, `.transform : matrix3`
9. **`NURBSSurfaceNormalCurve`** — curve normal to a surface:
   - `.parent` / `.parentID`, `.distance : float`
   - **CORRECTED (verified 2026-10-06):** there are **no `uParam` / `vParam` properties**, so there is no documented way to place the sample point on the parent surface through this class. Measured present: `parent parentID distance` plus the `NURBSCurve` base properties. `uParam`, `vParam`, `u`, `v`, `uParameter`, `vParameter`, `uPosition`, `vPosition`, `parameter1`, `parameter2`, `uCoord`, `vCoord` and `uv` are all absent — 14 candidates, none matched. **UNVERIFIED:** whether `NURBSSurfaceNormalCurve` is constructible in a usable state at all without a UV seed. Prefer `NURBSSurfaceEdgeCurve` or `NURBSIsoCurve` (both verified) when you need a surface-derived curve.

#### Dependent Curves on Surface (COS — Used for Trimming & Facade Paneling)
10. **`NURBSIsoCurve`** — isoparametric U or V line on a surface:
    - `.parent` / `.parentID`, `.dir : #U | #V`, `.parameter : float` (within surface parameter range), `.trim : boolean`, `.flipTrim : boolean`, `.seed : point2`
11. **`NURBSProjectVectorCurve`** — projects a 3D curve onto a surface along vector `pVec`:
    - `.parent1` / `.parent1ID` (**Surface!**), `.parent2` / `.parent2ID` (**Curve!**)
    - `.pVec : point3` (projection direction, e.g. `[0, 1, 0]` for front facade projection or `[0, 0, -1]` for roof skylight projection)
    - `.trim : boolean`, `.flipTrim : boolean`, `.seed : point2` (UV hint on surface, e.g. `[0.5, 0.5]`)
12. **`NURBSProjectNormalCurve`** — projects a 3D curve along the surface's own normals:
    - `.parent1` / `.parent1ID` (**Surface**), `.parent2` / `.parent2ID` (**Curve**), `.trim : boolean`, `.flipTrim : boolean`, `.seed : point2`
13. **`NURBSSurfSurfIntersectionCurve`** — intersection curve of two surfaces (can trim one or both surfaces!):
   - `.parent1` / `.parent1ID`, `.parent2` / `.parent2ID`
   - `.trim1 : boolean`, `.trim2 : boolean`, `.flipTrim1 : boolean`, `.flipTrim2 : boolean`, `.seed : point2`
   - **CORRECTED (verified 2026-10-06):** the trim flags are named **`.trim1` / `.trim2`**, not `.trimCurve1` / `.trimCurve2` — `trimCurve1` and `trimCurve2` do not exist on this class. Measured present: `parent1 parent2 parent1ID parent2ID trim1 trim2 flipTrim1 flipTrim2 seed`. (Note the neighbouring `NURBSCurveSurfaceIntersectPoint` *does* use `trimCurve`; only the surface/surface intersection curve uses the short form.)
14. **`NURBSSurfaceEdgeCurve`** — extracts one of the 4 boundary edges of a surface as a usable curve:
    - `.parent` / `.parentID`, `.seed : point2` (e.g. `[0.0, 0.5]` for low-U edge, `[1.0, 0.5]` for high-U edge, `[0.5, 0.0]` for low-V edge, `[0.5, 1.0]` for high-V edge)
15. **`NURBSPointCurveOnSurface`** — point curve authored directly in surface `(U, V)` parameter space:
    - Inherits `NURBSPointCurve` (`numPoints`, `setPoint` where `.pos` is `[u, v, 0]`) + `.parent` / `.parentID`, `.trim : boolean`, `.flipTrim : boolean`
      > **CORRECTED (verified 2026-10-06):** this line previously listed **`closed`** among the inherited properties. It does not — `NURBSPointCurve.closed` **throws on read and on write**. `.isClosed` (read-only) is the only closure flag, and it is set **only** by the `closed:` constructor kwarg. **This file's own `NURBSPointCurve` entry above already carried this correction;** this note reconciles the subclass line with it.
16. **`NURBSCurveOnSurface`** — CV curve authored in surface `(U, V)` parameter space:
    - Inherits `NURBSCVCurve` + `.parent` / `.parentID`, `.trim : boolean`, `.flipTrim : boolean` (prefer `NURBSPointCurveOnSurface` or `NURBSProjectVectorCurve` in scripts).

---

### 4.4 NURBS Surface Classes (`NURBSSurface : NURBSObject`)

#### Common Properties & Methods on ALL `NURBSSurface` Subclasses
- `.renderable : boolean` (default `true`)
- `.flipNormals : boolean` — **always check and toggle `.flipNormals` if a viewport capture shows inverted faces, or if a `node.min` / `node.max` read-back in `execute_maxscript` disagrees with the prediction.** (There is no `geometry_qa` tool in this bridge — verified absent at P4b-r. Verify with `execute_maxscript` plus the bridge's own viewport/snapshot tools.)
- `.generateUVs1 : boolean`, `.generateUVs2 : boolean`
- `.matID : integer` — Material ID for Multi/Sub-Object architectural materials
- `.closedInU : boolean`, `.closedInV : boolean` (read-only)
- `.uParameterRangeMin : float`, `.uParameterRangeMax : float`, `.vParameterRangeMin : float`, `.vParameterRangeMax : float` (read-only; **valid only after `NURBSNode` instantiation!**)
   - **VERIFIED (2026-10-04):** these ranges are **not** normalised to `[0, 1]` — a surface may legitimately report e.g. `[0.0, 700.0]`. Never hard-code `[0, 1]` when sampling; read `Min`/`Max` first and interpolate between them.
- **Analytical Surface Evaluation Methods (only on instantiated relational/non-relational set):**
  - `evalPos <surf> <u_param> <v_param>` $\rightarrow$ `point3` (local space; transform by `node.objectTransform` for world space)
  - `evalUTangent <surf> <u_param> <v_param>` $\rightarrow$ `point3` vector along U
  - `evalVTangent <surf> <u_param> <v_param>` $\rightarrow$ `point3` vector along V
  - Surface unit normal at `(u, v)`: `normalize (cross (evalUTangent surf u v) (evalVTangent surf u v))` (invert if `surf.flipNormals == true`).
- **UV Mapping & Tiling Methods:**
  - `getTiling <surf> [channel:<int>]` / `setTiling <surf> <u_tile> <v_tile> [channel:<int>]`
  - `getTilingOffset <surf> [channel:<int>]` / `setTilingOffset <surf> <u_off> <v_off> [channel:<int>]`
  - `getGenerateUVs <surf> <channel_int>` / `setGenerateUVs <surf> <channel_int> <bool>`

#### Independent Surfaces
1. **`NURBSCVSurface`** — control lattice `[u, v]` surface with rational weights:
   - Properties: `.uOrder`, `.vOrder`, `.numUKnots`, `.numVKnots`, `.numCVs` (`point2`, e.g. `[4, 4]`), `.transform` (`matrix3`), `.rigid` (`boolean`), `.autoParam` (`#notAutomatic | #autoCentripetal | #autoUniform`), `.uEdgesOverlap`, `.vEdgesOverlap`
   - Methods: `closeU <srf>`, `closeV <srf>`, `getUKnot <srf> <u>`, `setUKnot <srf> <u> <val>`, `getVKnot <srf> <v>`, `setVKnot <srf> <v> <val>`, `getCV <srf> <u> <v>`, `setCV <srf> <u> <v> <NURBSControlVertex>`, `refineU <srf> <v_param>`, `refineV <srf> <u_param>`, `refine <srf> <u_param> <v_param>`, `reparameterize <srf> (#centripetal | #uniform)`
2. **`NURBSPointSurface`** — interpolates directly through a 2D grid `[u, v]` of 3D points:
   - Properties: `.numPoints : point2` (e.g. `[5, 5]`, minimum `[2, 2]`), `.transform : matrix3`
   - **CORRECTED (verified 2026-10-06):** there are **no `.closedU` / `.closedV` properties** on this class. Measured present: `numPoints`, `transform`. `closedU`, `closedV`, `closed`, `isClosedU` and `isClosedV` are all absent. Closure in U or V must come from the closed **curve** grid you build the point surface from, not from a flag on the surface. (The `closeU` / `closeV` *methods* listed below do exist — verified by arity test.)
   - Methods: `closeU <srf>`, `closeV <srf>`, `getPoint <srf> <u_idx> <v_idx>`, `setPoint <srf> <u_idx> <v_idx> (NURBSIndependentPoint <pt3>)`, `refineU <srf> <v_param>`, `refineV <srf> <u_param>`, `refine <srf> <u_param> <v_param>`
3. **Analytic `NURBSCVSurface` Factory Functions** (return a `NURBSCVSurface` to pass to `appendObject`):
   - `MakeNURBSSphereSurface <radius> <center_pt3> <north_pt3> <ref_pt3> <startU_rad> <endU_rad> <startV_rad> <endV_rad> [open:<bool>]`
     *(Note: `north_pt3` and `ref_pt3` must be perpendicular, e.g. `[0,0,1]` and `[0,-1,0]`; angles in radians!)*
   - `MakeNURBSCylinderSurface <radius> <height> <origin_pt3> <sym_axis_pt3> <ref_axis_pt3> <start_rad> <end_rad> [open:<bool>]`
   - `MakeNURBSConeSurface <radius1> <radius2> <height> <origin_pt3> <sym_axis_pt3> <ref_axis_pt3> <start_rad> <end_rad> [open:<bool>]`
   - `MakeNURBSTorusSurface <majorRad> <minorRad> <origin_pt3> <sym_axis_pt3> <ref_axis_pt3> <startU_rad> <endU_rad> <startV_rad> <endV_rad> [open:<bool>]`
   - `MakeNURBSLatheSurface <nurbsCurve> <origin_pt3> <north_pt3> <start_rad> <end_rad>`

#### Dependent (Relational) Surfaces — The Powerhouse of Architectural NURBS
4. **`NURBSULoftSurface`** — smooth loft across 2 or more cross-section curves along U:
   - Properties: `.numCurves : integer`
   - Methods:
     - `appendCurve <uloft> <curve_set_index> [flip:<bool>] [startPoint:<float>] [tension:<float>] [useTangent:<bool>] [flipTangent:<bool>]`
     - `appendCurveByID <uloft> <curve_nurbsID> [flip:<bool>] [startPoint:<float>] [tension:<float>] [useTangent:<bool>] [flipTangent:<bool>]`
     - `getCurve <uloft> <idx>`, `setCurve <uloft> <idx> <curve_set_index>`, `getCurveID <uloft> <idx>`, `setCurveByID <uloft> <idx> <curve_nurbsID>`
     - `getFlip <uloft> <idx>`, `setFlip <uloft> <idx> <bool>`
   - *Architectural Tip:* Keep all cross-section curves oriented in the same direction (`flip:false`) so the loft doesn't twist into a bow-tie!
5. **`NURBSUVLoftSurface`** — bi-directional Gordon/Coons network surface interpolated across U-curves and V-curves:
   - Properties: `.numUCurves : integer`, `.numVCurves : integer`
   - Methods:
     - `appendUCurve <uvloft> <curve_set_index>` / `appendUCurveByID <uvloft> <curve_nurbsID>`
     - `appendVCurve <uvloft> <curve_set_index>` / `appendVCurveByID <uvloft> <curve_nurbsID>`
     - `getUCurve`, `setUCurve`, `getUCurveID`, `setUCurveByID`, `getVCurve`, `setVCurve`, `getVCurveID`, `setVCurveByID`
   - *Critical Requirement:* Every U curve **must spatially intersect** every V curve in 3D space (within tight tolerance), and the first/last U and V curves should form the boundary perimeter!
6. **`NURBS1RailSweepSurface`** — sweeps 1 or more cross-section curves along 1 rail curve:
   - Properties: `.rail : integer` (set index), `.railID : IntegerPtr`, `.numCurves : integer`, `.parallel : boolean`, `.axisTM : matrix3`
     > **CORRECTED (verified 2026-10-06):** `.railID` was typed here as `: integer` and labelled `` `NURBSId` ``. It is an **`IntegerPtr`** — measured `0P` on a committed 1-rail sweep, i.e. the same `IntegerPtr` printing rule as `.nurbsID` (§4.2). Never parse it, never compare two, never write a literal.
   - Methods: `appendCurve <sweep> <curve_set_index> [flip:<bool>] [startPoint:<float>]`, `appendCurveByID <sweep> <curve_nurbsID> [...]`, `getCurve`, `setCurve`, `getCurveID`, `setCurveByID`, `getFlip`, `setFlip`, `getCurveStartPoint`, `setCurveStartPoint`
   - *Critical Requirement:* Cross-section curves must touch/intersect the rail curve!
7. **`NURBS2RailSweepSurface`** — sweeps 1 or more cross-section curves along 2 rail curves (scales/adapts section width as distance between rails varies!):
   - Properties: `.rail1 : integer`, `.rail2 : integer`, `.numCurves : integer`, `.parallel : boolean`, `.rail1ID : IntegerPtr`, `.rail2ID : IntegerPtr`
     > **CORRECTED (verified 2026-10-06):** `.rail1ID` / `.rail2ID` were typed here as `: integer`. Both are measured as **full `IntegerPtr` pointers**, each **equal to the `nurbsID` of its own rail curve**. They are therefore never 1-based set indices even though `.rail1` / `.rail2` are — same hazard as §2 row 2. Bind each from the committed rail curve's own `.nurbsID`.
   - Methods: `appendCurve <sweep2> <curve_set_index> [flip:<bool>] [startPoint:<float>]`, `appendCurveByID <sweep2> <curve_nurbsID> [...]`
8. **`NURBSRuledSurface`** — straight linear interpolation between 2 curves (ideal for ramps, soffits, window jambs, developable facade strips):
   - Properties: `.parent1` / `.parent1ID`, `.parent2` / `.parent2ID`, `.flip1 : boolean`, `.flip2 : boolean`, `.curveStartPoint1 : float`, `.curveStartPoint2 : float`
9. **`NURBSExtrudeSurface`** — linear extrusion of a curve along `axisTM` by `distance`:
   - Properties: `.parent` / `.parentID`, `.distance : float`, `.axisTM : matrix3` (extrudes along the Z-axis of `axisTM`, default identity = world/local +Z), `.curveStartPoint : float`
10. **`NURBSLatheSurface`** — surface of revolution from a profile curve:
    - Properties: `.parent` / `.parentID`, `.sweep : float` (in **degrees**, e.g. `360.0`), `.axisTM : matrix3` (rotates around the Z-axis of `axisTM`), `.curveStartPoint : float`
11. **`NURBSBlendSurface`** — smooth G1/G2 transition surface between two surface edges (or a surface edge and a curve):
    - Properties: `.parent1` / `.parent1ID`, `.parent2` / `.parent2ID`, `.edge1 : integer` (`1`=low U, `2`=high U, `3`=low V, `4`=high V), `.edge2 : integer` (`1..4`), `.flip1 : boolean`, `.flip2 : boolean`, `.tension1 : float`, `.tension2 : float`, `.curveStartPoint1 : float`, `.curveStartPoint2 : float`
    - Methods: `getParent`, `setParent`, `getParentID`, `setParentID`, `getEdge`, `setEdge`
12. **`NURBSNBlendSurface`** — multisided Coons patch filling a closed loop of 3 or 4 curves/surface edges (head-to-tail loop):
    - Methods: `setParent <nblend> <idx_1to4> <set_index>`, `setParentID <nblend> <idx_1to4> <nurbsID>`, `setEdge <nblend> <idx_1to4> <edge_1to4>`
    - **UNVERIFIED (not executed 2026-10-06):** the three method names are confirmed to exist by an arity test, but their bodies were **not** run, because this class exposes **no properties whatsoever** (`parent1..parent4`, `numParents`, `nParents`, `numSides`, `edges`, `tension1`, `flip1` all absent, with a working `bogusZZ=false` control), so there is no read-back to confirm a link was made. Treat the `1to4` index range as unconfirmed.
13. **`NURBSCapSurface`** — planar/curved cap closing a closed curve or closed surface edge (`edge: 1..4`):
   - Properties: `.parent` / `.parentID`, `.edge : integer` (`1..4` if parent is a surface), `.curveStartPoint : float` (measured default `0.0`)
   - **CORRECTED (verified 2026-10-06):** `.curveStartPoint` is a **`Float`**, not an `integer` — `classOf` reads `Float` and the default is `0.0`, matching `.curveStartPoint` on `NURBSExtrudeSurface` / `NURBSLatheSurface` / `NURBSRuledSurface` / `NURBSBlendSurface` (all four also measured `0.0`). Only `.edge` is an integer (default `0`).
14. **`NURBSFilletSurface`** — rolling-ball constant or cubic fillet between two intersecting/adjacent surfaces:
    - Properties: `.cubic : boolean`
    - Methods (`<idx>` is `1` or `2`):
      - `setParent <fillet> <idx> <set_index>` / `setParentID <fillet> <idx> <nurbsID>`
      - `setSeed <fillet> <idx> <uv_point2>`
      - `setRadius <fillet> <idx> <radius_float>` (`idx=1` start radius, `idx=2` end radius)
      - `setTrimSurface <fillet> <idx> <bool>`
      - `setFlipTrim <fillet> <idx> <bool>`
    - **UNVERIFIED (not executed 2026-10-06):** the six method names and `.cubic` are confirmed to exist by an arity/property test, but the method **bodies** were not run — no fillet was constructed and committed, so the `idx=1`/`idx=2` radius pairing and the seed convention rest on the documentation, not on measurement.
15. **`NURBSOffsetSurface`** — thickens/offsets a parent surface along its surface normals by `distance`:
    - Properties: `.parent` / `.parentID`, `.distance : float`
16. **`NURBSMirrorSurface`** — mirrors a parent surface inside the `NURBSSet`:
    - Properties: `.parent` / `.parentID`, `.axis : #X | #Y | #Z | #XY | #XZ | #YZ`, `.transform : matrix3`, `.distance : float`, `.flipNormals : boolean`
17. **`NURBSXFormSurface`** — transformed dependent copy of a parent surface:
    - Properties: `.parent` / `.parentID`, `.transform : matrix3`
18. **`NURBSMultiCurveTrimSurface`** — trims a parent surface using a loop of multiple curves:
   - Properties: `.numCurves : integer`, `.flipTrim : boolean`
   - **CORRECTED (verified 2026-10-06):** **there is no `surfaceParent` / `surfaceParentID` property, and no parent property of any name.** Measured present: `numCurves`, `flipTrim` (plus the `NURBSSurface` base properties). Absent after testing 20 candidates — `surfaceParent`, `surfaceParentID`, `parent`, `parentID`, `parent1`, `parent1ID`, `surface`, `surfaceID`, `baseSurface`, `parentSurface`, `parentSurfaceID`, `srfParent`, `surfParent`, `surfParentID`, `baseParent`, `targetSurface`, `targetSurfaceID`, `parentSrf`, `curveParent`, `parentSrf`. **UNVERIFIED:** with no parent slot, this class could not be given a parent surface by script at all, so **there is no verified way to build a multi-curve trim in this build.** `appendCurve` / `appendCurveByID` on it exist (arity-verified) but the surface to trim cannot be attached through any property. For facade opening layout use `NURBSProjectVectorCurve` (Recipe 4) or offset/loft strategies that do have a working parent slot.
   - Methods: `appendCurve <trimSurf> <curve_set_index>`, `appendCurveByID <trimSurf> <curve_nurbsID>`

---

## 5. Scene Node Creation, Conversion & Sub-Object Manipulation

### 5.1 Creating NURBS Nodes in the Scene
```maxscript
-- 1. General constructor from any NURBSSet:
node = NURBSNode <nurbsset> [name:<string>] [pos:<point3>] [material:<mtl>]
-- IMPORTANT: NURBSNode mutates <nurbsset> in-place so it becomes a live #relational set
-- with all .nurbsID properties populated!

-- 2. Shorthand NURBS Extrude from an existing Spline/Shape node:
extNode = NURBSExtrudeNode $FootprintSpline 400.0 capStart:true capEnd:true mapCoords:true name:"Wall_NURBS"

-- 3. Shorthand NURBS Lathe from an existing Spline/Shape node:
latheNode = NURBSLatheNode $ProfileSpline (matrix3 1) 360.0 capStart:false capEnd:false weldCore:true mapCoords:true name:"Dome_NURBS"
```

### 5.2 Converting Existing Primitives or Splines to NURBS
- **Primitives (`Box`, `Sphere`, `Cylinder`, `Cone`, `Torus`, `Tube`) $\rightarrow$ `NURBSSurface`:**
  ```maxscript
  if canConvertTo $MyCylinder NURBSSurface do convertToNURBSSurface $MyCylinder
  ```
- **`SplineShape` / `Line` / `Circle` / `Arc` / `Rectangle` $\rightarrow$ `NURBSCurve`:**
  ```maxscript
  if canConvertTo $MySpline NURBSCurve do convertToNURBSCurve $MySpline
  ```
- **Combining multiple converted NURBS curves/surfaces into one `NURBSSet`:**
  If you convert two splines `$Arch1` and `$Arch2` using `convertToNURBSCurve`, they are two separate scene nodes. To loft between them in a single `NURBSSet`:
  ```maxscript
  stopCreating                       -- zero arguments; see note below
  ns1 = getNURBSSet $Arch1          -- non-relational copy
  ns2 = getNURBSSet $Arch2          -- non-relational copy
  addNURBSSet $Arch1 ns2            -- DOES NOT WORK in 2026.3.2 -- see correction below
  delete $Arch2
  -- Now extract relational set from $Arch1 and add NURBSULoftSurface via appendCurveByID!
  ```
> **CORRECTED (verified 2026-10-04):** `stopCreating` takes **zero** arguments. `stopCreating <node>` throws `Argument count error: StopCreating wanted 0, got 1`, so the original per-node loop `stopCreating $Arch1; stopCreating $Arch2` is replaced by a single bare `stopCreating` — it is a global "finish whatever creation is pending" toggle, not a per-node query or setter.
>
> **CORRECTED (verified 2026-10-06): the merge in the snippet above does not happen.** Run verbatim on two `Rectangle`s converted with `convertToNURBSCurve`, `addNURBSSet $Arch1 ns2` **returned `ok` and changed nothing**: `$Arch1`'s relational set stayed at 4 objects and its bounding box stayed `[-400,-5,0]..[400,5,0]` even though `$Arch2` sat at `x = 3000` and would have extended it to `max.x ≈ 3300`. `$Arch2` was untouched and `delete $Arch2` then destroyed the curves. **Do not rely on `addNURBSSet` for merging.** Instead, rebuild the combined set in one pass before `NURBSNode`: put **all** the curves you need into a **single** `NURBSSet` with `appendObject`, then append the dependent surface with `appendCurve <surf> <set_index>` and instantiate once. That path is verified end-to-end by Recipes 1, 2 and 5.

### 5.3 Node-Level Operations on Instantiated NURBS Objects
Always call `stopCreating` (zero arguments — see Pitfall 1) and obtain `.nurbsID` via `getNURBSSet <node> #relational`:
- **`addNURBSSet <node> <nurbsSet>`** — **DOES NOT WORK in Max 2026.3.2 (verified 2026-10-06).** The name resolves (calling it with no arguments reaches native code and faults on the undefined node, so it is genuinely present), and it **returns `ok`**, but it **never adds anything**. Four variants were executed against a live node, all with working positive controls on the receiving set, and none produced any change in `numObjects` or in the node bounding box:
  1. the §5.2 snippet — a real `getNURBSSet $Arch2` set of curves into `$Arch1`;
  2. a `NURBSULoftSurface` built with `appendCurveByID` from two real curve `nurbsID`s;
  3. a `NURBSUVLoftSurface` built with `appendUCurveByID` / `appendVCurveByID` from a real `nurbsID`;
  4. a `NURBSOffsetSurface` with `parentID` set to a live surface's own `nurbsID`.

  Build everything in **one** `NURBSSet` before `NURBSNode` instead — that route is verified.
- **`transform <node> (<nurbsId> | #(<nurbsId1>, ...)) <matrix3>`** — transforms sub-objects in node-local space.
- **`breakCurve <node> <nurbsId> <u_param>`** — splits a curve into two curves at `u_param`.
- **`breakSurface <node> <nurbsId> (#U | #V) <u_or_v_param>`** — splits a surface into two surfaces along a U or V isoline.
- **`joinCurves <node> <nurbsId1> <nurbsId2> <tolerance_float> [flip1:<bool>] [flip2:<bool>]`** — joins two curves into one (blends across gap if distance `> tolerance`; set `tolerance` larger than gap to avoid loops).
- **`joinSurfaces <node> <nurbsId1> <nurbsId2> <edge1_1to4> <edge2_1to4> <tolerance_float>`** — joins two surfaces along specified edges (`1`=low U, `2`=high U, `3`=low V, `4`=high V).
- **`makeIndependent <node> <nurbsId>`** — bakes a dependent sub-object (e.g. `NURBSULoftSurface`, `NURBSBlendSurface`, `NURBSOffsetSurface`) into an independent `NURBSCVSurface` or `NURBSCVCurve` so its CVs can be directly sculpted!

---

## 6. Top 10 NURBS Pitfalls & Safety Rules for AI Agents

1. **Always Call `stopCreating` (No Arguments) Before `getNURBSSet`:**
   If 3ds Max is still in object creation mode, `getNURBSSet` returns an incomplete set. Always precede inspection/modification with a bare `stopCreating`. Passing a node throws `Argument count error: StopCreating wanted 0, got 1`.
2. **Never Mix `.parent` (Set Index) and `.parentID` (relational id, an `IntegerPtr` — see the note at the head of §2):**
   - Building a fresh `NURBSSet` before `NURBSNode` $\rightarrow$ use `.parent`, `.parent1`, `.rail`, `appendCurve`.
   - Modifying an existing node via `addNURBSSet` or `getNURBSSet #relational` $\rightarrow$ use `.parentID`, `.parent1ID`, `.railID`, `appendCurveByID`.
3. **Strict Knot Vector Invariant (`numKnots == order + numCVs`):**
   Violating this or leaving knots uninitialized (`setKnot`) causes immediate Assertion Failures or empty nodes. When in doubt, use `NURBSPointCurve` / `NURBSPointSurface` (which compute knots automatically) or use the `setClampedKnots` helper!
4. **Never Call `getViewTess` / `setViewTess` with `#displacement`:**
   Viewport tessellation only supports `#surface` and `#curve`. Passing `#displacement` triggers a C++ Assertion Failure dialog.
5. **Parameter Ranges (`uParameterRangeMin/Max`) Require Scene Instantiation:**
   Calling `evalPos`, `evalUTangent`, `evalVTangent`, or reading `.uParameterRangeMin` on an uninstantiated `NURBSSet` fails. Call `NURBSNode` first, then evaluate on the active relational set.
6. **Hide Construction Curves Before Final Capture/Delivery:**
   Curves inside a `NURBSSet` remain visible in the viewport by default. Set ` local d = NURBSDisplay displayCurves:false displaySurfaces:true displayTrimming:true; setSurfaceDisplay node d ` so the viewport shows clean architectural surfaces.
7. **Set `.merge` on Multi-Surface Shells:**
   When a NURBS model contains multiple joined or adjacent surfaces (e.g. a canopy with fillets/blends/caps), set `nset.merge = 0.1` (and on `NURBSSurfaceApproximation`) so production tessellation stitches shared boundary vertices without hairline cracks.
8. **Enable `generateUVs1 = true` on Every Renderable Surface:**
   Always set `surf.generateUVs1 = true` and `setTiling surf uTile vTile channel:1` so PBR materials with textures render properly without requiring a destructive `UVW Map` modifier.
   > **⚠️ MEASURED 2026-10-06 (P15) — `setTiling` is DEFECTIVE, do not use it for density.**
   > Full transcripts: `references/13-uv-rules.md`. Three corrections:
   > - `generateUVs1` is a **constructor keyword** and a property of the **committed surface
   >   sub-object**, not of a `NURBSPoint` (every UV property throws there).
   > - `true` produces a **`0..1` normalised map regardless of the surface's size in cm** — a
   >   600 cm and an 1800 cm surface both give span `1.0 x 1.0`. `false` produces **no channel 1**.
   > - **`setTiling <surf> <u> <v> channel:1` silently floors both arguments to integers.**
   >   `2.99 → 2`, `1.9 → 1`, `3.5 → 3`. So constant texel density is unachievable with it.
   >
   > **For world-scale tiling use `Uvwmap` on the node instead** — measured `3.5 x 1.5` on a
   > 350 × 150 cm surface, fractional values accepted:
   > ```maxscript
   > addModifier node (Uvwmap maptype:0)          -- one call
   > -- SEPARATE execute_maxscript call, or after a snapshotAsMesh:
   > node.modifiers[1].utile = 3.5
   > node.modifiers[1].vtile = 1.5
   > ```
   > ⛔ `utile`/`vtile` written in the **same** call that adds the modifier are silently discarded
   > (reads back in-call, reverts to `1.0` next call — 8/8). `maptype` and `realWorldMapSize` are
   > unaffected. This is why the snippet above is split.
9. **Free Memory on Temporary Non-Relational Sets:**
   If you call `ns = getNURBSSet node` (without `#relational`) in a loop to inspect CV data, call `deleteObjects ns` when finished to prevent native SDK memory leaks.
10. **One-Line Safe Execution in `execute_maxscript`:**
    Remember `3dsmax-mcp`'s `execute_maxscript` rules: avoid `\n` or `\t` inside string literals, use forward slashes in paths, keep statements separated by `;` or inside a clean `try (...) catch (getCurrentException() as string)` block, and verify the resulting geometry by reading back `node.min`, `node.max` and `objects.count` in a further `execute_maxscript` call, plus a capture from the bridge's own viewport/snapshot tools. (`geometry_qa` and `agent_viewport` do **not** exist in this bridge — verified absent at P4b-r.) For a NURBS surface, also spot-check `evalPos surf u v` at a few parameter pairs inside the surface's own reported `uParameterRangeMin/Max` / `vParameterRangeMin/Max`.
