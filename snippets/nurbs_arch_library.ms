-- ============================================================================
-- MCP_NURBS_Arch : Production MAXScript Library for Architectural NURBS in 3ds Max
-- Compatible with 3ds Max 2023-2027 and cl0nazepamm/3dsmax-mcp
-- ============================================================================

struct MCP_NURBS_Arch_Lib (

    -- 1. Configure a valid Clamped Knot Vector on a NURBSCVCurve
    -- Enforces the strict invariant: numKnots = order + numCVs
    fn setClampedKnots crv ord nCVs = (
        if nCVs < ord do throw ("NURBSCVCurve requires numCVs (" + (nCVs as string) + ") >= order (" + (ord as string) + ")")
        crv.order = ord
        crv.numCVs = nCVs
        crv.numKnots = ord + nCVs
        local numSpans = (nCVs - ord + 1) as float
        for k = 1 to ord do setKnot crv k 0.0
        for k = (ord + 1) to nCVs do (
            setKnot crv k ((k - ord) / numSpans)
        )
        for k = (nCVs + 1) to (ord + nCVs) do setKnot crv k 1.0
        crv
    ),

    -- 2. Configure valid Clamped Knot Vectors in U and V on a NURBSCVSurface
    fn setSurfaceClampedKnots surf uOrd vOrd nU nV = (
        if nU < uOrd or nV < vOrd do throw "NURBSCVSurface requires numCVs >= order in both U and V"
        surf.uOrder = uOrd
        surf.vOrder = vOrd
        surf.numCVs = [nU, nV]
        surf.numUKnots = uOrd + nU
        surf.numVKnots = vOrd + nV
        local uSpans = (nU - uOrd + 1) as float
        local vSpans = (nV - vOrd + 1) as float
        for k = 1 to uOrd do setUKnot surf k 0.0
        for k = (uOrd + 1) to nU do setUKnot surf k ((k - uOrd) / uSpans)
        for k = (nU + 1) to (uOrd + nU) do setUKnot surf k 1.0
        for k = 1 to vOrd do setVKnot surf k 0.0
        for k = (vOrd + 1) to nV do setVKnot surf k ((k - vOrd) / vSpans)
        for k = (nV + 1) to (vOrd + nV) do setVKnot surf k 1.0
        surf
    ),

    -- 3. Create a NURBSCVCurve from an array of Point3 and optional weights
    --
    -- CLOSURE LIMITATION (verified live 2026-10-04, Max 2026.3.2):
    -- NURBSCVCurve cannot be made topologically closed. `closed:true` in the
    -- constructor is silently ignored, there is no settable `closed`/`isClosed`
    -- property, and `close <crv>` returns the string "OK" without mutating the
    -- curve. isClosed therefore always reads false.
    -- `closed:true` is honoured SEAM-WILED instead: the first CV is repeated as
    -- the last one, so the curve starts and ends on the same point.
    -- For a genuinely closed curve use makePointCurve, whose `closed:true` works.
    fn makeCVCurve pts name:"MCP_CVCurve" order:4 closed:false weights:#() = (
        local work = for i = 1 to pts.count collect (pts[i] as point3)
        local nSrc = work.count
        if closed and nSrc > 2 do append work work[1]
        local nCVs = work.count
        local effOrder = amin #(order, nCVs)
        local crv = NURBSCVCurve name:name
        this.setClampedKnots crv effOrder nCVs
        for i = 1 to nCVs do (
            local w = 1.0
            if i <= weights.count then w = weights[i] as float
            else if (i > nSrc and weights.count > 0) then w = weights[1] as float
            setCV crv i (NURBSControlVertex work[i] w)
        )
        crv
    ),

    -- 4. Create a NURBSPointCurve from an array of Point3
    -- `closed:true` is native and reliable here (unlike NURBSCVCurve).
    fn makePointCurve pts name:"MCP_PointCurve" closed:false = (
        local crv = NURBSPointCurve name:name closed:closed numPoints:pts.count
        for i = 1 to pts.count do (
            setPoint crv i (NURBSIndependentPoint (pts[i] as point3))
        )
        crv
    ),

    -- 5. Apply clean architectural viewport & render tessellation to a NURBS scene node
    fn applyArchTessellation node hideCurves:true mergeTol:0.15 uSteps:6 vSteps:6 edgePct:4.0 angleDeg:6.0 = (
        stopCreating
        local disp = NURBSDisplay displayCurves:(not hideCurves) displaySurfaces:true displayDependents:true displayTrimming:true
        setSurfaceDisplay node disp
        local vApprox = NURBSSurfaceApproximation config:#meshOnly meshApproxType:#parametric meshUSteps:uSteps meshVSteps:vSteps merge:mergeTol
        -- CORRECTED (verified 2026-10-06): curvatureAngle is in DEGREES, not radians, so angleDeg
        -- is passed through unchanged; the previous (degToRad angleDeg) misread the unit.
        -- Unit evidence, on a quarter-cylinder NURBSPointSurface with meshApproxType:#curvature and
        -- a loose curvatureDistance: the mesh reaches its 25-vert floor at >= 40 degrees, while
        -- 1.5708 (pi/2 rad) sits in the DENSE region -- under a radians reading pi/2 would already
        -- be maximally coarse, which it is not. On that curvature-bound surface 6.0 gives 101 verts
        -- against 691 for 0.10472, i.e. ~6.9x.
        -- Honest scope of that figure: 6.9x is the cost where curvatureAngle is the BINDING
        -- constraint. On the shipped examples/spatialAndCurvature surfaces spacialEdge dominates and
        -- the whole chain's render mesh measures 49499 verts with the fix versus 51197 without, i.e.
        -- ~3%. The fix is correct because the unit was wrong, not because it buys 6.9x everywhere.
        local rApprox = NURBSSurfaceApproximation config:#meshOnly meshApproxType:#spatialAndCurvature spacialEdge:edgePct curvatureAngle:angleDeg curvatureDistance:0.2 merge:mergeTol subdivStyle:#grid
        setViewApproximation node vApprox
        setRenderApproximation node rApprox
        node
    ),

    -- 6. Build a complete U-Loft shell (with optional thickness offset) from an array of Point3 arrays
    fn createULoftShell sectionPointsList name:"Arch_NURBS_ULoft" thickness:0.0 closedSections:false hideCurves:true hasShell:undefined mergeTol:0.15 = (
        local nset = NURBSSet()
        local crvIndices = #()
        for i = 1 to sectionPointsList.count do (
            local pc = this.makePointCurve sectionPointsList[i] name:("Section_" + (i as string)) closed:closedSections
            appendObject nset pc
            append crvIndices nset.numObjects
        )
        local uLoft = NURBSULoftSurface name:(name + "_BaseSurf") renderable:true generateUVs1:true matID:1
        for idx in crvIndices do appendCurve uLoft idx flip:false
        appendObject nset uLoft
        local surfIdx = nset.numObjects

        local doOffset = false
        if hasShell != undefined then (
            if hasShell == true do doOffset = true
        ) else (
            if ((abs thickness) >= 0.001) do doOffset = true
        )
        if doOffset do (
            local offSurf = NURBSOffsetSurface name:(name + "_OffsetSurf") parent:surfIdx distance:thickness renderable:true generateUVs1:true matID:2
            appendObject nset offSurf
        )
        nset.merge = mergeTol
        local node = NURBSNode nset name:name
        this.applyArchTessellation node hideCurves:hideCurves mergeTol:mergeTol
        node
    ),

    -- 7. Build a UV-Loft (Gordon network) surface from intersecting U and V Point3 arrays
    fn createUVLoftNetwork uCurvesPts vCurvesPts name:"Arch_NURBS_UVLoft" hideCurves:true mergeTol:0.15 = (
        local nset = NURBSSet()
        local uIndices = #()
        local vIndices = #()
        for i = 1 to uCurvesPts.count do (
            local uc = this.makePointCurve uCurvesPts[i] name:("UCurve_" + (i as string)) closed:false
            appendObject nset uc
            append uIndices nset.numObjects
        )
        for j = 1 to vCurvesPts.count do (
            local vc = this.makePointCurve vCurvesPts[j] name:("VCurve_" + (j as string)) closed:false
            appendObject nset vc
            append vIndices nset.numObjects
        )
        local uvSurf = NURBSUVLoftSurface name:(name + "_Surf") renderable:true generateUVs1:true matID:1
        for uIdx in uIndices do appendUCurve uvSurf uIdx
        for vIdx in vIndices do appendVCurve uvSurf vIdx
        appendObject nset uvSurf
        nset.merge = mergeTol
        local node = NURBSNode nset name:name
        this.applyArchTessellation node hideCurves:hideCurves mergeTol:mergeTol
        node
    ),

    -- 8. Inspect an existing NURBS node and return a structured summary string of all sub-objects
    fn inspectNURBSSet node = (
        stopCreating
        local rset = getNURBSSet node #relational
        local ss = stringStream ""
        format "NODE:%|COUNT:%\n" node.name rset.numObjects to:ss
        for i = 1 to rset.numObjects do (
            local o = getObject rset i
            local cls = (classOf o) as string
            local scls = (superClassOf o) as string
            if scls == "NURBSSurface" then (
                format "IDX:%|ID:%|CLASS:%|SUPER:%|NAME:%|U:[%,%]|V:[%,%]|MATID:%|FLIP:%\n" \
                    i o.nurbsID cls scls o.name o.uParameterRangeMin o.uParameterRangeMax o.vParameterRangeMin o.vParameterRangeMax o.matID o.flipNormals to:ss
            ) else if scls == "NURBSCurve" then (
                format "IDX:%|ID:%|CLASS:%|SUPER:%|NAME:%|U:[%,%]|CLOSED:%\n" \
                    i o.nurbsID cls scls o.name o.parameterRangeMin o.parameterRangeMax o.isClosed to:ss
            ) else (
                format "IDX:%|ID:%|CLASS:%|SUPER:%|NAME:%\n" i o.nurbsID cls scls o.name to:ss
            )
        )
        ss as string
    ),

    -- 9. Analytically sample any NURBSSurface into a pure Quad Editable_Poly mesh
    fn sampleSurfaceToQuadPoly node surfSetIndex uDivs vDivs name:"" = (
        stopCreating
        local rset = getNURBSSet node #relational
        local surf = getObject rset surfSetIndex
        if superClassOf surf != NURBSSurface do throw ("Sub-object " + (surfSetIndex as string) + " is not a NURBSSurface")

        local uMin = surf.uParameterRangeMin; local uMax = surf.uParameterRangeMax
        local vMin = surf.vParameterRangeMin; local vMax = surf.vParameterRangeMax
        local tm = node.objectTransform
        local outName = if name != "" then name else (node.name + "_QuadPoly")

        local ep = Editable_Mesh name:outName
        convertTo ep Editable_Poly

        for iu = 0 to uDivs do (
            local u = uMin + (uMax - uMin) * (iu as float / uDivs)
            for iv = 0 to vDivs do (
                local v = vMin + (vMax - vMin) * (iv as float / vDivs)
                local p = (evalPos surf u v) * tm
                polyop.createVert ep p
            )
        )

        local stride = vDivs + 1
        for iu = 0 to (uDivs - 1) do (
            for iv = 0 to (vDivs - 1) do (
                local v1 = iu * stride + iv + 1
                local v2 = (iu + 1) * stride + iv + 1
                local v3 = (iu + 1) * stride + (iv + 1) + 1
                local v4 = iu * stride + (iv + 1) + 1
                if surf.flipNormals then (
                    polyop.createPolygon ep #(v1, v4, v3, v2)
                ) else (
                    polyop.createPolygon ep #(v1, v2, v3, v4)
                )
            )
        )
        update ep
        ep
    ),

    -- 10. Generate a 3D Diagrid renderable spline space-frame on any NURBSSurface
    fn createDiagridOnSurface node surfSetIndex uCells vCells thickness:10.0 subSteps:4 name:"" = (
        stopCreating
        local rset = getNURBSSet node #relational
        local surf = getObject rset surfSetIndex
        if superClassOf surf != NURBSSurface do throw ("Sub-object " + (surfSetIndex as string) + " is not a NURBSSurface")

        local uMin = surf.uParameterRangeMin; local uMax = surf.uParameterRangeMax
        local vMin = surf.vParameterRangeMin; local vMax = surf.vParameterRangeMax
        local tm = node.objectTransform
        local outName = if name != "" then name else (node.name + "_Diagrid")

        local shp = SplineShape name:outName
        for iu = 0 to (uCells - 1) do (
            for iv = 0 to (vCells - 1) do (
                local u0 = uMin + (uMax - uMin) * (iu as float / uCells)
                local u1 = uMin + (uMax - uMin) * ((iu + 1) as float / uCells)
                local v0 = vMin + (vMax - vMin) * (iv as float / vCells)
                local v1 = vMin + (vMax - vMin) * ((iv + 1) as float / vCells)

                local s1 = addNewSpline shp
                for k = 0 to subSteps do (
                    local t = k as float / subSteps
                    addKnot shp s1 #smooth #curve ((evalPos surf (u0 + (u1 - u0)*t) (v0 + (v1 - v0)*t)) * tm)
                )
                local s2 = addNewSpline shp
                for k = 0 to subSteps do (
                    local t = k as float / subSteps
                    addKnot shp s2 #smooth #curve ((evalPos surf (u0 + (u1 - u0)*t) (v1 + (v0 - v1)*t)) * tm)
                )
            )
        )
        updateShape shp
        shp.render_renderable = true
        shp.render_displayRenderMesh = true
        shp.render_thickness = thickness
        shp.render_sides = 12
        shp
    ),

    -- 11. Build a NURBSPointSurface from a rectangular grid of Point3 arrays
    --
    -- GRID CONVENTION (identical for F11 and F12):
    --   grid[iv][iu] -- iv = row index (1..nV), iu = column index (1..nU).
    --   Rows may have different lengths ONLY if nU is taken from the longest;
    --   callers must pass a rectangular grid, build_nurbs.py enforces this.
    --
    -- VERIFIED 2026-10-04, Max 2026.3.2:
    --   - `setPoint` on a SURFACE takes FOUR arguments: setPoint surf u v point.
    --     The three-argument form used for curves fails with
    --     "Argument count error: setPoint wanted 4, got 3".
    --   - `numPoints` on a NURBSPointSurface is a point2 (grid dimensions).
    --   - A surface is NOT evaluable until it is committed: before
    --     appendObject + NURBSNode, uParameterRangeMin/Max read 0.0 and
    --     evalPos returns undefined. After commit they read 0.0..1.0.
    fn makePointSurfaceGrid grid name:"MCP_PointSurf" matID:1 renderable:true generateUVs1:true hideCurves:true mergeTol:0.15 = (
        stopCreating
        if grid.count < 2 do throw ("makePointSurfaceGrid needs >= 2 rows, got " + (grid.count as string))
        local nV = grid.count
        local nU = grid[1].count
        for iv = 1 to nV do (
            if grid[iv].count != nU do throw ("makePointSurfaceGrid row " + (iv as string) + " has " + (grid[iv].count as string) + " points, expected " + (nU as string))
        )
        local ps = NURBSPointSurface name:(name + "_PointSurf") renderable:renderable generateUVs1:generateUVs1 matID:matID
        ps.numPoints = [nU, nV]
        for iv = 1 to nV do for iu = 1 to nU do setPoint ps iu iv (NURBSIndependentPoint (grid[iv][iu] as point3))
        local nset = NURBSSet()
        appendObject nset ps
        nset.merge = mergeTol
        local node = NURBSNode nset name:name
        this.applyArchTessellation node hideCurves:hideCurves mergeTol:mergeTol
        node
    ),

    -- 12. Build a NURBSCVSurface from a rectangular grid of Point3 arrays
    -- `weights` is a single flat row-major array; missing entries default to 1.0.
    fn makeCVSurfaceGrid grid name:"MCP_CVSurf" uOrder:3 vOrder:3 weights:#() matID:1 renderable:true generateUVs1:true hideCurves:true mergeTol:0.15 = (
        stopCreating
        if grid.count < 2 do throw ("makeCVSurfaceGrid needs >= 2 rows, got " + (grid.count as string))
        local nV = grid.count
        local nU = grid[1].count
        for iv = 1 to nV do (
            if grid[iv].count != nU do throw ("makeCVSurfaceGrid row " + (iv as string) + " has " + (grid[iv].count as string) + " points, expected " + (nU as string))
        )
        local uOrd = amin #(uOrder, nU)
        local vOrd = amin #(vOrder, nV)
        local cs = NURBSCVSurface name:(name + "_CVSurf") renderable:renderable generateUVs1:generateUVs1 matID:matID
        this.setSurfaceClampedKnots cs uOrd vOrd nU nV
        for iv = 1 to nV do for iu = 1 to nU do (
            local w = 1.0
            local flat = (iv - 1) * nU + iu
            if flat <= weights.count then w = weights[flat] as float
            setCV cs iu iv (NURBSControlVertex (grid[iv][iu] as point3) w)
        )
        local nset = NURBSSet()
        appendObject nset cs
        nset.merge = mergeTol
        local node = NURBSNode nset name:name
        this.applyArchTessellation node hideCurves:hideCurves mergeTol:mergeTol
        node
    )
)

global MCP_NURBS_Arch = MCP_NURBS_Arch_Lib()
"MCP_NURBS_Arch loaded"
