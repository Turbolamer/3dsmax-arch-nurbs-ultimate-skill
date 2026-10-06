# Architectural & Exterior NURBS Recipes for 3ds Max MCP

> **Purpose:** Production-ready MAXScript workflows for complex architectural exteriors using NURBS in 3ds Max (2023–2027).
> Every recipe follows `3dsmax-mcp` safety rules: single-transaction `undo ... on ( )` blocks, clean display settings (`displayCurves:false`), UV generation (`generateUVs1:true`), and verification by reading the result back with `execute_maxscript` (`node.min`, `node.max`, `objects.count`, `evalPos surf u v`) and inspecting it with the bridge's own viewport/snapshot tools.
>
> **There is no `geometry_qa`, `contact_check` or `agent_viewport` tool in this bridge** — all three were verified absent by direct inspection of the live tool list at P4b-r. Nothing in this file depends on them.

---

## When to Choose NURBS vs. the MAXScript Spline / Poly Routes

> **Tool availability, verified by direct inspection of the live tool list at P4b-r:** `curve_model`, `loft_mesh` and `draw_spline` **do not exist** in this bridge. `RailClone` is not installed (railClone is absent — substitute Chaos Scatter / instance copies). `inspect_curve` and `edit_curve` are absent too: read and modify a node's splines with MAXScript instead. The left column below has been re-pointed accordingly.

| Architectural Element | Recommended Route | Why |
| :--- | :--- | :--- |
| Standard extruded walls, slabs, cornices, window frames | MAXScript `SplineShape` / `Line` / `Rectangle` + `addNewSpline` / `addKnot` / `updateShape` / `splineOps` — see `references/maxscript-splines-shapes.md` — extruded as **solid wall/slab cells**; or the NURBS route `NURBSExtrudeSurface` via `NURBSSet` + `NURBSNode` | Built from constructors that exist, and it needs no optional plugin. Note the **Boolean modifier cannot be made to cut in this build** (`G-81`) — build walls as solid tiles, not as booleans. Do not route this row through `curve_model` / `draw_spline` (absent), and note that `Extrude` and `Sweep` were measured to **construct and then throw on `addModifier`** in this installation. |
| Straight or single-axis quad lofts (columns, vases, tapered piers) | **`NURBSULoftSurface`** (relational NURBS loft — see Recipes 1 and 5) | The verified loft path. `Loft` *resolves* as a class name but `Loft()` is **`NotCreatable`** — verified distinction, do not call it. `loft_mesh` and `curve_model(output:{kind:"loft"})` are both absent. |
| Repeated modular facades, curtain walls, railings, roof tiles | Instance copies — `n = copy src` then `n.baseObject = src.baseObject`, or `3dsmax-mcp_clone_objects` in instance mode — driven from MAXScript arrays (Recipe 3A/3B geometry + a `for` loop placing instances) | `setCopyMode` does **not** exist; the `baseObject` assignment is the verified instance route. RailClone is not installed, so `get_railclone_style` / `set_railclone_style` / L1S / A2S generators are unavailable. |
| **Double-curved organic roofs, shells, canopies (Zaha Hadid / Calatrava / MAD style)** | **NURBS (`NURBSULoftSurface` / `NURBSUVLoftSurface` + `NURBSOffsetSurface`)** | True mathematical $G_2$ continuity, bidirectional U/V curve networks, analytical UV evaluation (`evalPos`), and exact normal offsets. |
| **Curved skylights, atriums, or facade openings cut into a double-curved shell** | **UNVERIFIED — no working script route in this build.** The documented route (`NURBSProjectVectorCurve` + `trim:true`, or `NURBSMultiCurveTrimSurface`) does not survive execution: `addNURBSSet` is a silent no-op (Recipe 4), and `NURBSMultiCurveTrimSurface` has no parent-surface property at all. Model the opening as a separate panel/soffit surface rather than a trim. | Boolean operations on thin double-curved polygon shells often pinch normals; NURBS parametric trimming keeps exact mathematical curvature — **but see the correction: neither trim route was executable on Max 2026.3.2.** |
| **Analytical Diagrid / Space Frame / Quad Glazing Panelization on freeform envelopes** | **NURBS (`evalPos` + `evalUTangent` + `evalVTangent` $\rightarrow$ `Editable_Poly` / `NURBSIsoCurve`)** | Evaluates exact mathematical $(u,v)$ coordinates and surface normals at any resolution without polygon subdivision artifacts. |
| **Helical / variable-width curved ramps, parking spirals, sweeping grand stairs** | **NURBS (`NURBS2RailSweepSurface` with `parallel:true`)** | Inner and outer rails independently control elevation, banking, and width scaling along the path. |
| **Smooth podium-to-tower transitions, mushroom columns merging into slabs** | **NURBS (`NURBSBlendSurface` / `NURBSFilletSurface`)** | True tangent/curvature matching (`tension1`, `tension2`) between two distinct surfaces. |
| **Tensile membranes, stadium roofs, ETFE facade cushions** | **NURBS (`NURBSNBlendSurface` / weighted `NURBSCVSurface`)** | 3- or 4-edge boundary Coons patches and rational CV weights naturally model catenary/pneumatic tension. |

---

## Recipe 1: Parametric Double-Curved Roof / Canopy Shell (`NURBSULoftSurface` + `NURBSOffsetSurface`)

Creates a sweeping wave canopy from cross-section `NURBSPointCurve` ribs, thickens it with a relational `NURBSOffsetSurface`, hides construction curves, configures adaptive curvature tessellation, and enables UV mapping.

```maxscript
undo "MCP_NURBS_WaveCanopy" on (
    local nset = NURBSSet()
    -- Define 4 wave cross-section curves along X (Y = span, Z = height)
    local xCoords = #(0.0, 1200.0, 2400.0, 3600.0)
    local zArch   = #(450.0, 750.0, 350.0, 650.0)
    local zEdges  = #(150.0, 320.0, 100.0, 280.0)
    local crvIndices = #()

    for i = 1 to xCoords.count do (
        local x = xCoords[i]
        local zMid = zArch[i]
        local zEdg = zEdges[i]
        local pc = NURBSPointCurve name:("Canopy_Rib_" + (i as string)) closed:false numPoints:5
        setPoint pc 1 (NURBSIndependentPoint [x, -1000.0, zEdg])
        setPoint pc 2 (NURBSIndependentPoint [x, -500.0, (zEdg + zMid) * 0.55])
        setPoint pc 3 (NURBSIndependentPoint [x,    0.0, zMid])
        setPoint pc 4 (NURBSIndependentPoint [x,  500.0, (zEdg + zMid) * 0.55])
        setPoint pc 5 (NURBSIndependentPoint [x, 1000.0, zEdg])
        appendObject nset pc
        append crvIndices nset.numObjects   -- appendObject returns "OK", not an index
    )

    -- Create primary U-Loft surface (Bottom soffit skin, MatID 1)
    local uLoft = NURBSULoftSurface name:"Canopy_BottomSkin" renderable:true generateUVs1:true matID:1
    for idx in crvIndices do (
        appendCurve uLoft idx flip:false tension:0.0
    )
    appendObject nset uLoft
    local botSurfIdx = nset.numObjects

    -- Create relational Offset surface for structural roof thickness (Top skin, MatID 2, +35 cm)
    local topSurf = NURBSOffsetSurface name:"Canopy_TopSkin" parent:botSurfIdx distance:35.0 renderable:true generateUVs1:true matID:2
    appendObject nset topSurf

    -- Configure seamless tessellation
    nset.merge = 0.2
    local node = NURBSNode nset name:"Arch_NURBS_Canopy" pos:[0,0,0]
    stopCreating

    -- Hide construction curves in viewport and set high-quality curvature approximation
    local disp = NURBSDisplay displayCurves:false displaySurfaces:true displayDependents:true displayTrimming:true
    setSurfaceDisplay node disp

    local vApprox = NURBSSurfaceApproximation config:#meshOnly meshApproxType:#parametric meshUSteps:6 meshVSteps:6 merge:0.2
    local rApprox = NURBSSurfaceApproximation config:#meshOnly meshApproxType:#spatialAndCurvature spacialEdge:5.0 curvatureAngle:6.0 curvatureDistance:0.2 merge:0.2 subdivStyle:#grid
    setViewApproximation node vApprox
    setRenderApproximation node rApprox
    node.name
)
```
> **CORRECTED (verified 2026-10-04):**
> - `appendObject` returns the **string `"OK"`** (class `OkClass`), never an index — `local botSurfIdx = appendObject nset uLoft` would bind `"OK"` to a slot later used as the integer `parent:` of `NURBSOffsetSurface`. Read `nset.numObjects` *after* the call to get the new 1-based set index.
> - `stopCreating` takes **zero** arguments. `stopCreating node` throws `Argument count error: StopCreating wanted 0, got 1`.
> - `+` binds tighter than `as`, so `("Canopy_Rib_" + i as string)` parses as `(("Canopy_Rib_" + i) as string)` and throws `Incompatible types: 1, and ": "`. Parenthesise the conversion: `("Canopy_Rib_" + (i as string))`.
> - **CORRECTED (verified 2026-10-06): `curvatureAngle` is in DEGREES, not radians** — the `degToRad` wrapper has been removed above. Measured on a curved test surface with `meshApproxType:#curvature`, the value `6.0` yields a moderate mesh while `degToRad 6.0` (0.10472) yields **691 versus 101 verts — a ~6.9× denser mesh than intended**, and the mesh does not collapse to a floor anywhere near `2π`. The default is `20.0`, a sane degrees default. Writing `degToRad <deg>` here makes the render mesh needlessly heavy; pass the degree number directly.
> - **VERIFIED (2026-10-06) as a whole:** this recipe was executed verbatim against Max 2026.3.2 and produced exactly one node, `Arch_NURBS_Canopy`, `classOf` = `NURBSSurf`, bounding box `[0,-1000,-35.0618]..[3617.43,1000,924.759]` (the −35 z-minimum is the `-30`-style soffit offset landing correctly). `Canopy_TopSkin` came back as a `NURBSOffsetSurface` with `parentID` populated, `distance` = 35.0, `matID` = 2, `generateUVs1` = true. Every kwarg on `NURBSDisplay`, `NURBSSurfaceApproximation` (including `subdivStyle:#grid`) and both approximation setters was accepted.

---

## Recipe 2: Bi-Directional Network Facade (`NURBSUVLoftSurface` — Gordon Surface)

When an architectural facade or atrium roof must conform to **both** horizontal floor-edge profiles (U-curves) **and** vertical architectural elevation profiles (V-curves), use `NURBSUVLoftSurface`.
**Crucial Rule:** Every U-curve must intersect every V-curve at matching $(x,y,z)$ grid points!

```maxscript
undo "MCP_NURBS_UVLoft_Facade" on (
    local nset = NURBSSet()
    -- Define a 3x3 grid of exact intersection points on a doubly-curved facade
    -- Rows (u = 1..3): Bottom (z=0), Mid (z=900), Top (z=1800)
    -- Cols (v = 1..3): Left (x=0), Center (x=800), Right (x=1600)
    local gridPts = #(
        #([0,   0, 0],    [800, -180,    0], [1600,   0,    0]),
        #([0, 120, 900],  [800, -320,  900], [1600, 150,  900]),
        #([0,   0, 1800], [800,  -80, 1800], [1600,   0, 1800])
    )

    local uCurveIndices = #()
    for u = 1 to 3 do (
        local uc = NURBSPointCurve name:("Horizontal_FloorCurve_" + (u as string)) closed:false numPoints:3
        for v = 1 to 3 do setPoint uc v (NURBSIndependentPoint gridPts[u][v])
        appendObject nset uc
        append uCurveIndices nset.numObjects   -- appendObject returns "OK", not an index
    )

    local vCurveIndices = #()
    for v = 1 to 3 do (
        local vc = NURBSPointCurve name:("Vertical_MullionCurve_" + (v as string)) closed:false numPoints:3
        for u = 1 to 3 do setPoint vc u (NURBSIndependentPoint gridPts[u][v])
        appendObject nset vc
        append vCurveIndices nset.numObjects   -- appendObject returns "OK", not an index
    )

    local uvSurf = NURBSUVLoftSurface name:"Facade_UVLoft_Skin" renderable:true generateUVs1:true matID:1
    for uIdx in uCurveIndices do appendUCurve uvSurf uIdx
    for vIdx in vCurveIndices do appendVCurve uvSurf vIdx
    appendObject nset uvSurf

    local node = NURBSNode nset name:"Facade_NURBS_UVEnvelope"
    stopCreating
    setSurfaceDisplay node (NURBSDisplay displayCurves:false displaySurfaces:true displayDependents:true)
    node.name
)
```
> **CORRECTED (verified 2026-10-04):** `append uCurveIndices (appendObject nset uc)` was broken twice over: `appendObject` returns the string `"OK"`, so the index array would have collected `"OK"`; and `"..." + u as string` threw `Incompatible types: 1, and ": "`. Both are corrected above — `appendObject nset uc` followed by `append uCurveIndices nset.numObjects`, and `("..." + (u as string))`. `stopCreating` also takes zero arguments.

---

## Recipe 3: Analytical UV Panelization & Diagrid Generation (`evalPos` / `evalUTangent` / `evalVTangent`)

One of the biggest advantages of NURBS in 3ds Max is that you can mathematically evaluate **any** point `evalPos surf u v` and its exact tangent frame (`evalUTangent`, `evalVTangent`) across the surface's parameter domain `[uMin..uMax, vMin..vMax]`.
This lets the AI agent generate:
1. **A 100% pure Quad `Editable_Poly` Curtain Wall Cage** (with Material ID 1 for glass panels and inset/extruded mullions via `polyop`, or `Data Channel`). *An MCP tool named `mesh_edit` is sometimes cited for this step — **UNVERIFIED**: it was not in the live tool list inspected at P4b-r, and no transcript in this repo shows a successful call. Use the MAXScript route.*
2. **A 3D Diagrid Structural Space Frame** (renderable splines or cylinders connecting diagonal UV cells).

> **VERIFIED (2026-10-04):** the parameter domain is **not** normalised to `[0, 1]` — a surface can report e.g. `[0.0, 700.0]`. Both recipes below therefore read `uParameterRangeMin/Max` and `vParameterRangeMin/Max` from the surface and interpolate; never hard-code `[0, 1]`.

### 3A. Sample Any NURBS Surface into a Pure Quad `Editable_Poly` Curtain Wall
```maxscript
undo "MCP_NURBS_To_QuadCurtainWall" on (
    local srcNode = $Arch_NURBS_Canopy
    stopCreating
    local rset = getNURBSSet srcNode #relational
    -- Find first NURBSSurface in the set
    local surf = undefined
    for i = 1 to rset.numObjects where (superClassOf (getObject rset i) == NURBSSurface) while surf == undefined do (
        surf = getObject rset i
    )
    if surf == undefined do throw "No NURBSSurface found in node"

    local uMin = surf.uParameterRangeMin
    local uMax = surf.uParameterRangeMax
    local vMin = surf.vParameterRangeMin
    local vMax = surf.vParameterRangeMax

    local uDivs = 24 -- number of panels along U
    local vDivs = 12 -- number of panels along V
    local tm = srcNode.objectTransform

    -- Create empty Editable_Poly for the panelized curtain wall
    local ep = Editable_Mesh name:(srcNode.name + "_QuadPanels")
    convertTo ep Editable_Poly

    -- 1. Create vertices on exact mathematical UV grid
    for iu = 0 to uDivs do (
        local u = uMin + (uMax - uMin) * (iu as float / uDivs)
        for iv = 0 to vDivs do (
            local v = vMin + (vMax - vMin) * (iv as float / vDivs)
            local worldPt = (evalPos surf u v) * tm
            polyop.createVert ep worldPt
        )
    )

    -- 2. Create quad faces (1-based vertex indexing)
    local stride = vDivs + 1
    for iu = 0 to (uDivs - 1) do (
        for iv = 0 to (vDivs - 1) do (
            local v1 = iu * stride + iv + 1
            local v2 = (iu + 1) * stride + iv + 1
            local v3 = (iu + 1) * stride + (iv + 1) + 1
            local v4 = iu * stride + (iv + 1) + 1
            polyop.createPolygon ep #(v1, v2, v3, v4)
        )
    )
    update ep
    ep.name
)
```
> **CORRECTED (verified 2026-10-04):** `stopCreating` takes **zero** arguments — `stopCreating srcNode` throws `Argument count error: StopCreating wanted 0, got 1`. Both 3A and 3B now call a bare `stopCreating` before `getNURBSSet srcNode #relational`.
> **Pro Tip for Curtain Wall Mullions:** Once `ep` (`Editable_Poly`) is created from the NURBS surface with exact quad panels, you can immediately work on all quad faces with MAXScript (`polyop.bevelFaces` / `Lattice` modifier / `Data Channel`) to inset them by the mullion width (e.g. `2.5 cm`), assign `matID = 1` (Frame) to the border strips and `matID = 2` (Glass) to the inner panels, and apply a `Shell` modifier. *An MCP tool named `mesh_edit` is sometimes cited here — **UNVERIFIED**, see the note in Recipe 3.*

### 3B. Generate a Structural Diagrid Lattice Directly on a NURBS Surface
```maxscript
undo "MCP_NURBS_Diagrid" on (
    local srcNode = $Arch_NURBS_Canopy
    stopCreating
    local rset = getNURBSSet srcNode #relational
    local surf = getObject rset 5 -- index of the target NURBSSurface in rset
    local uMin = surf.uParameterRangeMin; local uMax = surf.uParameterRangeMax
    local vMin = surf.vParameterRangeMin; local vMax = surf.vParameterRangeMax
    local tm = srcNode.objectTransform

    local uCells = 16; local vCells = 8
    local subSteps = 4 -- intermediate curve points per diagonal cell so struts hug curvature!

    local diagShape = SplineShape name:(srcNode.name + "_Diagrid")
    for iu = 0 to (uCells - 1) do (
        for iv = 0 to (vCells - 1) do (
            local u0 = uMin + (uMax - uMin) * (iu as float / uCells)
            local u1 = uMin + (uMax - uMin) * ((iu + 1) as float / uCells)
            local v0 = vMin + (vMax - vMin) * (iv as float / vCells)
            local v1 = vMin + (vMax - vMin) * ((iv + 1) as float / vCells)

            -- Diagonal 1: (u0, v0) -> (u1, v1)
            local s1 = addNewSpline diagShape
            for k = 0 to subSteps do (
                local t = k as float / subSteps
                local pt = (evalPos surf (u0 + (u1 - u0)*t) (v0 + (v1 - v0)*t)) * tm
                addKnot diagShape s1 #smooth #curve pt
            )
            -- Diagonal 2: (u0, v1) -> (u1, v0)
            local s2 = addNewSpline diagShape
            for k = 0 to subSteps do (
                local t = k as float / subSteps
                local pt = (evalPos surf (u0 + (u1 - u0)*t) (v1 + (v0 - v1)*t)) * tm
                addKnot diagShape s2 #smooth #curve pt
            )
        )
    )
    updateShape diagShape
    diagShape.render_renderable = true
    diagShape.render_displayRenderMesh = true
    diagShape.render_thickness = 12.0
    diagShape.render_sides = 12
    diagShape.name
)
```

---

## Recipe 4: Cutting Skylights, Atriums & Organic Windows via Projected Trim Curves (`NURBSProjectVectorCurve`)

Instead of destructive polygon booleans that ruin shading on curved roofs or facades, project a closed `NURBSCVCurve` or `NURBSPointCurve` onto the surface along a vector (`[0,0,-1]` for roof skylights, `[0,1,0]` for facade windows) with `trim:true`!

```maxscript
undo "MCP_NURBS_SkylightTrim" on (
    local node = $Arch_NURBS_Canopy
    stopCreating
    local rset = getNURBSSet node #relational

    -- Find target surface relational id (e.g., Canopy_BottomSkin)
    -- CORRECTED (verified 2026-10-06): this comment read "target surface NURBSId".
    -- There is no NURBSId class - the type is IntegerPtr, an address printing
    -- as <decimal>P. Keep it in its own variable; never parse or compare two,
    -- and never write a literal into parent1ID: (a synthetic integer there is
    -- an EXCEPTION_ACCESS_VIOLATION that kills Max). See nurbs-complete-guide.md
    -- §2.
    local targetSurfID = 0
    for i = 1 to rset.numObjects do (
        local o = getObject rset i
        if o.name == "Canopy_BottomSkin" do targetSurfID = o.nurbsID
    )
    if targetSurfID == 0 do throw "Target surface not found"

    -- Build a secondary NURBSSet containing a closed oval skylight curve above the canopy
    local trimSet = NURBSSet()
    local skyCrv = NURBSPointCurve name:"Skylight_CutProfile" closed:true numPoints:8
    local cx = 1800.0; local cy = 0.0; local rx = 450.0; local ry = 280.0; local zHigh = 1200.0
    for k = 1 to 8 do (
        local ang = (k - 1) * 45.0
        local px = cx + rx * (cos ang)
        local py = cy + ry * (sin ang)
        setPoint skyCrv k (NURBSIndependentPoint [px, py, zHigh])
    )
    -- close is a silent no-op (returns OK, does not mutate the curve);
    -- closed:true on the NURBSPointCurve constructor above already closes it
    appendObject trimSet skyCrv
    local crvIdx = trimSet.numObjects   -- appendObject returns "OK", not an index

    -- Add vector-projected curve on surface with trim:true
    -- NOTE: parent1ID references the existing scene surface by its bound
    --       relational id (IntegerPtr, not a NURBSId and not a plain integer);
    --       parent2 references skyCrv by its 1-based index in trimSet!
    local projCrv = NURBSProjectVectorCurve name:"Skylight_TrimCOS" \
        parent1ID:targetSurfID parent2:crvIdx \
        pVec:[0, 0, -1] seed:[0.5, 0.5] trim:true flipTrim:false
    appendObject trimSet projCrv

    -- Merge into the live scene node
    addNURBSSet node trimSet          -- NO-OP in 2026.3.2 -- see the correction below
    stopCreating
    setSurfaceDisplay node (NURBSDisplay displayCurves:false displaySurfaces:true displayDependents:true)
    "Skylight trimmed successfully"
)
```
> **CORRECTED (verified 2026-10-04):**
> - `close skyCrv` was removed. `close` returns the value `OK` (class `OkClass`) and does **not** mutate the curve — it is a silent no-op. `NURBSPointCurve closed:true` works natively (`isClosed = true`), so the constructor flag is the correct and sufficient way to close this profile.
> - `local crvIdx = appendObject trimSet skyCrv` bound the string `"OK"` to `parent2:`, which expects an integer set index. Fixed by reading `trimSet.numObjects` after the append.
> - `stopCreating` takes zero arguments (`Argument count error: StopCreating wanted 0, got 1`).
> - **CORRECTED (verified 2026-10-06): the recipe does NOT complete — `addNURBSSet` is a silent no-op in Max 2026.3.2, so the trim curve never reaches the node.** Executed against a live 4-rib canopy: every construction step above succeeded (`NURBSProjectVectorCurve` with `parent1ID:`, `parent2:`, `pVec:`, `seed:`, `trim:true`, `flipTrim:` all accepted; `skyCrv.isClosed` = `true`), and `addNURBSSet` returned `ok` — but the target node's relational set stayed at 21 objects, no `NURBSProjectVectorCurve` and no `NURBSCVSurface` appeared in it, and the bounding box was unchanged. The trailing `"Skylight trimmed successfully"` string is therefore misleading: nothing was trimmed. **Recipe 4 cannot be used as written in this build.** There is also no working parent slot on `NURBSMultiCurveTrimSurface` (see `nurbs-complete-guide.md` §4.4), so the alternative multi-curve route is unavailable too.
> **What does work for cutting an opening:** build the projected curve **inside the same `NURBSSet` as its parent surface**, before `NURBSNode`, using the set-index form rather than `addNURBSSet`. Note also that `NURBSProjectVectorCurve trim:true` does not perform a real trim in this build — it appends an untrimmed `NURBSCVSurface` copy of the parent, and `trim:false` appends no surface at all.
> **Note on `flipTrim`:** If projecting the curve keeps the inner skylight patch and hides the rest of the roof, simply toggle `projCrv.flipTrim = true` on the relational set!

---

## Recipe 5: Curved Helical Ramp / Sweeping Staircase (`NURBS2RailSweepSurface`)

A 2-Rail Sweep is ideal for curved pedestrian bridges, spiral museum ramps, or variable-width grand stairs where the inner and outer edges follow different radii or slopes:

```maxscript
undo "MCP_NURBS_2RailRamp" on (
    local nset = NURBSSet()
    local numSteps = 9
    local rInner = 400.0; local rOuter = 750.0; local totalHeight = 450.0

    local railInner = NURBSPointCurve name:"Ramp_InnerRail" closed:false numPoints:numSteps
    local railOuter = NURBSPointCurve name:"Ramp_OuterRail" closed:false numPoints:numSteps

    for i = 1 to numSteps do (
        local t = (i - 1) as float / (numSteps - 1)
        local ang = t * 180.0 -- 180-degree sweeping ramp
        local z = t * totalHeight
        -- Outer rail flares wider at the bottom landing (t=0)
        local rOutCur = rOuter + (1.0 - t) * 150.0
        setPoint railInner i (NURBSIndependentPoint [rInner * (cos ang), rInner * (sin ang), z])
        setPoint railOuter i (NURBSIndependentPoint [rOutCur * (cos ang), rOutCur * (sin ang), z])
    )
    appendObject nset railInner
    local r1Idx = nset.numObjects
    appendObject nset railOuter
    local r2Idx = nset.numObjects

    -- Start cross-section connecting railInner[1] to railOuter[1] at ang = 0
    local secStart = NURBSPointCurve name:"Ramp_Section_Start" closed:false numPoints:2
    setPoint secStart 1 (NURBSIndependentPoint [rInner, 0, 0])
    setPoint secStart 2 (NURBSIndependentPoint [rOuter + 150.0, 0, 0])
    appendObject nset secStart
    local s1Idx = nset.numObjects

    -- End cross-section connecting railInner[numSteps] to railOuter[numSteps] at ang = 180
    local secEnd = NURBSPointCurve name:"Ramp_Section_End" closed:false numPoints:2
    setPoint secEnd 1 (NURBSIndependentPoint [-rInner, 0, totalHeight])
    setPoint secEnd 2 (NURBSIndependentPoint [-rOuter, 0, totalHeight])
    appendObject nset secEnd
    local s2Idx = nset.numObjects

    local rampSurf = NURBS2RailSweepSurface name:"Ramp_DeckSurface" rail1:r1Idx rail2:r2Idx parallel:true renderable:true generateUVs1:true matID:1
    appendCurve rampSurf s1Idx flip:false
    appendCurve rampSurf s2Idx flip:false
    appendObject nset rampSurf
    local deckIdx = nset.numObjects

    -- Add structural slab thickness (-30 cm)
    local soffitSurf = NURBSOffsetSurface name:"Ramp_Soffit" parent:deckIdx distance:-30.0 renderable:true generateUVs1:true matID:2
    appendObject nset soffitSurf

    local node = NURBSNode nset name:"Arch_CurvedRamp_NURBS"
    stopCreating
    setSurfaceDisplay node (NURBSDisplay displayCurves:false displaySurfaces:true displayDependents:true)
    node.name
)
```
> **CORRECTED (verified 2026-10-04):** the five `local <name>Idx = appendObject nset <obj>` lines were all returning the string `"OK"`. `rail1:`/`rail2:` and the `NURBSOffsetSurface parent:` below them require **integer set indices**, so each append is now followed by `local <name>Idx = nset.numObjects`. `stopCreating` takes zero arguments.

---

## Recipe 6: Podium-to-Tower Smooth Transition (`NURBSBlendSurface` & `NURBSNBlendSurface`)

When a vertical tower facade smoothly flares into a horizontal podium canopy (like Zaha Hadid's Opus or Heydar Aliyev Center), connect their boundary edges using `NURBSBlendSurface`:

- **Edge Index Convention on `NURBSSurface`:**
  - `1` = Low U edge ($u = u_{\min}$)
  - `2` = High U edge ($u = u_{\max}$)
  - `3` = Low V edge ($v = v_{\min}$)
  - `4` = High V edge ($v = v_{\max}$)
- **Controlling Curvature:**
  - `tension1` and `tension2` (default `1.0`): increase (`1.5`–`2.5`) for a deeper tangent extension from the parent surface; decrease (`0.3`–`0.7`) for a tighter turn.
  - If the blend surface twists into a bow-tie, toggle `blendSurf.flip1 = not blendSurf.flip1` or `blendSurf.flip2 = not blendSurf.flip2`.

---

## Recipe 7: Extracting `NURBSIsoCurve` Profiles to Drive Louver Instancing

To place architectural timber/aluminum louvers along a NURBS surface:
1. Sample `N` isoparametric curves along U or V using `evalPos surf u v` and create a multi-spline `SplineShape` (or individual `SplineShape` rails).
2. Place the fins along those rails with the **verified** routes below. Note what is *not* available: `RailClone` is not installed (so `set_railclone_style`, L1S and A2S generators cannot be used), `setCopyMode` does not exist, and `Sweep` / `Extrude` were measured to **construct and then throw on `addModifier`** in this installation — a stack that includes them will not build.
   - **Instanced fins (verified):** create one fin, then loop the sample points — `n = copy <fin>; n.baseObject = <fin>.baseObject`, set `n.pos` and orient with `n.rotation = quat <degrees> [0,0,1]`. Remember `pos.z` is the **base** of a primitive.
   - **Curved/continuous fins:** a MAXScript modifier stack on the louver node, drawn from the attachable set only (`Bend`, `Twist`, `Taper`, `Chamfer`, `Shell`, `Lattice`, `Edit_Poly`), built incrementally at **≤ 5 modifiers per `execute_maxscript` call**.
   - *An MCP tool named `add_modifier` is sometimes cited for this step — **UNVERIFIED**: no transcript in this repo shows a successful call, so route through MAXScript `addModifier`.*
