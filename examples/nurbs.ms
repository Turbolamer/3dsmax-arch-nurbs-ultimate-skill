/* build_nurbs.py | project pavilion-01 | DO NOT EDIT */
fn mcpNurbsBuild_pavilion_01 = (
    if MCP_NURBS_Arch == undefined do ( fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/snippets/nurbs_arch_library.ms" )
    fn mcpNurbsSurfIndex node label = (
        local rset = getNURBSSet node #relational
        local found = 0
        for i = 1 to rset.numObjects do (
            local o = getObject rset i
            if superClassOf o == NURBSSurface do ( found = i; exit )
        )
        if found == 0 do throw ("build_nurbs: " + label + " carries no NURBSSurface sub-object; a surface index cannot be guessed")
        found
    )
    fn mcpNurbsCensus node label expected = (
        -- G-54: an invalid dependent surface is DROPPED at commit with no error and no
        -- warning, so a build that completes proves nothing. Count what the commit produced.
        stopCreating
        local rset = getNURBSSet node #relational
        local found = 0
        for i = 1 to rset.numObjects do (
            local o = getObject rset i
            if superClassOf o == NURBSSurface do ( found = found + 1 )
        )
        if found != expected do throw ("build_nurbs G-54: node " + label + " committed " + (found as string) + " NURBSSurface sub-object(s) but the spec implies " + (expected as string) + "; 3ds Max drops an invalid dependent surface at commit without reporting it, so this build is not the geometry the spec asked for")
        found
    )
    fn mcpNurbsSurfID node label = (
        -- G-56 support: a `parent1ID:` / `parent2ID:` slot takes a live pointer, never a
        -- literal. D4: a literal or synthetic id there is an EXCEPTION_ACCESS_VIOLATION,
        -- a hard crash of the Max process, so the id is always read from a committed
        -- sub-object. The FIRST NURBSSurface is the design surface; a thickness_cm > 0
        -- appends its offset shell after it, so the last one would be the shell.
        local rset = getNURBSSet node #relational
        local found = undefined
        for i = 1 to rset.numObjects do (
            local o = getObject rset i
            if superClassOf o == NURBSSurface do ( found = o.nurbsID; exit )
        )
        if found == undefined do throw ("build_nurbs: " + label + " carries no NURBSSurface sub-object, so it has no nurbsID for a relation parent to bind (G-56); a pointer cannot be invented")
        found
    )
    local prev_DRV_001_VaultPanels = getNodeByName "DRV_001_VaultPanels"
    if prev_DRV_001_VaultPanels != undefined do ( delete prev_DRV_001_VaultPanels )
    local prev_DRV_002_CanopyFrame = getNodeByName "DRV_002_CanopyFrame"
    if prev_DRV_002_CanopyFrame != undefined do ( delete prev_DRV_002_CanopyFrame )
    local prev_DRV_003_CagePanels = getNodeByName "DRV_003_CagePanels"
    if prev_DRV_003_CagePanels != undefined do ( delete prev_DRV_003_CagePanels )
    local prev_SUR_001_Vault = getNodeByName "SUR_001_Vault"
    if prev_SUR_001_Vault != undefined do ( delete prev_SUR_001_Vault )
    local prev_SUR_002_Canopy = getNodeByName "SUR_002_Canopy"
    if prev_SUR_002_Canopy != undefined do ( delete prev_SUR_002_Canopy )
    local prev_SUR_003_CanopyCage = getNodeByName "SUR_003_CanopyCage"
    if prev_SUR_003_CanopyCage != undefined do ( delete prev_SUR_003_CanopyCage )
    local prev_SUR_004_EntranceCanopy = getNodeByName "SUR_004_EntranceCanopy"
    if prev_SUR_004_EntranceCanopy != undefined do ( delete prev_SUR_004_EntranceCanopy )
    local prev_SUR_005_NorthWalkway = getNodeByName "SUR_005_NorthWalkway"
    if prev_SUR_005_NorthWalkway != undefined do ( delete prev_SUR_005_NorthWalkway )
    local prev_SUR_006_CanopySoffit = getNodeByName "SUR_006_CanopySoffit"
    if prev_SUR_006_CanopySoffit != undefined do ( delete prev_SUR_006_CanopySoffit )
    local prev_SUR_007_VaultApertureGuide = getNodeByName "SUR_007_VaultApertureGuide"
    if prev_SUR_007_VaultApertureGuide != undefined do ( delete prev_SUR_007_VaultApertureGuide )
    local SEC_001 = #([0.0,0.0,420.0],[225.0,0.0,539.059],[450.0,0.0,575.885],[675.0,0.0,594.284],[900.0,0.0,600.0],[1125.0,0.0,594.284],[1350.0,0.0,575.885],[1575.0,0.0,539.059],[1800.0,0.0,420.0])
    local SEC_002 = #([0.0,225.0,420.0],[225.0,225.0,539.059],[450.0,225.0,575.885],[675.0,225.0,594.284],[900.0,225.0,600.0],[1125.0,225.0,594.284],[1350.0,225.0,575.885],[1575.0,225.0,539.059],[1800.0,225.0,420.0])
    local SEC_003 = #([0.0,450.0,420.0],[225.0,450.0,539.059],[450.0,450.0,575.885],[675.0,450.0,594.284],[900.0,450.0,600.0],[1125.0,450.0,594.284],[1350.0,450.0,575.885],[1575.0,450.0,539.059],[1800.0,450.0,420.0])
    local SEC_004 = #([0.0,675.0,420.0],[225.0,675.0,539.059],[450.0,675.0,575.885],[675.0,675.0,594.284],[900.0,675.0,600.0],[1125.0,675.0,594.284],[1350.0,675.0,575.885],[1575.0,675.0,539.059],[1800.0,675.0,420.0])
    local SEC_005 = #([0.0,900.0,420.0],[225.0,900.0,539.059],[450.0,900.0,575.885],[675.0,900.0,594.284],[900.0,900.0,600.0],[1125.0,900.0,594.284],[1350.0,900.0,575.885],[1575.0,900.0,539.059],[1800.0,900.0,420.0])
    local SEC_006 = #([0.0,0.0,420.0],[150.0,0.0,420.0],[300.0,0.0,420.0],[450.0,0.0,420.0],[600.0,0.0,420.0])
    local SEC_007 = #([0.0,225.0,420.0],[150.0,225.0,487.5],[300.0,225.0,510.0],[450.0,225.0,487.5],[600.0,225.0,420.0])
    local SEC_008 = #([0.0,450.0,420.0],[150.0,450.0,420.0],[300.0,450.0,420.0],[450.0,450.0,420.0],[600.0,450.0,420.0])
    local SEC_009 = #([0.0,0.0,420.0],[150.0,0.0,420.0],[300.0,0.0,420.0],[450.0,0.0,420.0],[600.0,0.0,420.0])
    local SEC_010 = #([0.0,225.0,420.0],[150.0,225.0,465.0],[300.0,225.0,480.0],[450.0,225.0,465.0],[600.0,225.0,420.0])
    local SEC_011 = #([0.0,450.0,420.0],[150.0,450.0,420.0],[300.0,450.0,420.0],[450.0,450.0,420.0],[600.0,450.0,420.0])
    local SEC_012 = #([675.0,0.0,300.0],[675.0,225.0,300.0],[675.0,450.0,300.0])
    local SEC_013 = #([450.0,0.0,260.0],[562.5,0.0,290.0],[675.0,0.0,300.0],[787.5,0.0,290.0],[900.0,0.0,260.0])
    local SEC_014 = #([450.0,225.0,260.0],[562.5,225.0,290.0],[675.0,225.0,300.0],[787.5,225.0,290.0],[900.0,225.0,260.0])
    local SEC_015 = #([450.0,450.0,260.0],[562.5,450.0,290.0],[675.0,450.0,300.0],[787.5,450.0,290.0],[900.0,450.0,260.0])
    local SEC_016 = #([0.0,525.0,30.0],[450.0,581.25,30.0],[900.0,600.0,30.0],[1350.0,581.25,30.0],[1800.0,525.0,30.0])
    local SEC_017 = #([0.0,600.0,30.0],[450.0,768.75,30.0],[900.0,825.0,30.0],[1350.0,768.75,30.0],[1800.0,600.0,30.0])
    local SEC_018 = #([0.0,525.0,30.0],[0.0,562.5,30.0],[0.0,600.0,30.0])
    local SEC_019 = #([450.0,581.25,30.0],[450.0,675.0,30.0],[450.0,768.75,30.0])
    local SEC_020 = #([900.0,600.0,30.0],[900.0,712.5,30.0],[900.0,825.0,30.0])
    local SEC_021 = #([1350.0,581.25,30.0],[1350.0,675.0,30.0],[1350.0,768.75,30.0])
    local SEC_022 = #([1800.0,525.0,30.0],[1800.0,562.5,30.0],[1800.0,600.0,30.0])
    local SEC_023 = #([750.0,375.0,700.0],[1050.0,375.0,700.0],[1050.0,525.0,700.0],[750.0,525.0,700.0])
    local SUR_001_Vault = MCP_NURBS_Arch.createULoftShell #(SEC_001,SEC_002,SEC_003,SEC_004,SEC_005) name:"SUR_001_Vault" thickness:25.0 closedSections:false hideCurves:true
    local set_SUR_001_Vault = getNURBSSet SUR_001_Vault #relational
    set_SUR_001_Vault.merge = 0.15
    MCP_NURBS_Arch.applyArchTessellation SUR_001_Vault hideCurves:true mergeTol:0.15 uSteps:12 vSteps:8 edgePct:3.0 angleDeg:4.0
    local id_SUR_001_Vault = mcpNurbsSurfID SUR_001_Vault "SUR_001_Vault"
    local SUR_002_Canopy = MCP_NURBS_Arch.makePointSurfaceGrid #(SEC_006,SEC_007,SEC_008) name:"SUR_002_Canopy" matID:2 hideCurves:true mergeTol:0.15
    MCP_NURBS_Arch.applyArchTessellation SUR_002_Canopy hideCurves:true mergeTol:0.2 uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
    local id_SUR_002_Canopy = mcpNurbsSurfID SUR_002_Canopy "SUR_002_Canopy"
    local SUR_003_CanopyCage = MCP_NURBS_Arch.makeCVSurfaceGrid #(SEC_009,SEC_010,SEC_011) name:"SUR_003_CanopyCage" uOrder:3 vOrder:3 matID:3 hideCurves:true mergeTol:0.15
    MCP_NURBS_Arch.applyArchTessellation SUR_003_CanopyCage hideCurves:true mergeTol:0.15 uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
    local SUR_004_EntranceCanopy_Set = NURBSSet()
    local SUR_004_EntranceCanopy_rail1 = 0
    local SUR_004_EntranceCanopy_pc1 = MCP_NURBS_Arch.makePointCurve SEC_012 closed:false
    appendObject SUR_004_EntranceCanopy_Set SUR_004_EntranceCanopy_pc1
    SUR_004_EntranceCanopy_rail1 = SUR_004_EntranceCanopy_Set.numObjects
    local SUR_004_EntranceCanopy_sec1 = 0
    local SUR_004_EntranceCanopy_sc1 = MCP_NURBS_Arch.makePointCurve SEC_013 closed:false
    appendObject SUR_004_EntranceCanopy_Set SUR_004_EntranceCanopy_sc1
    SUR_004_EntranceCanopy_sec1 = SUR_004_EntranceCanopy_Set.numObjects
    local SUR_004_EntranceCanopy_sec2 = 0
    local SUR_004_EntranceCanopy_sc2 = MCP_NURBS_Arch.makePointCurve SEC_014 closed:false
    appendObject SUR_004_EntranceCanopy_Set SUR_004_EntranceCanopy_sc2
    SUR_004_EntranceCanopy_sec2 = SUR_004_EntranceCanopy_Set.numObjects
    local SUR_004_EntranceCanopy_sec3 = 0
    local SUR_004_EntranceCanopy_sc3 = MCP_NURBS_Arch.makePointCurve SEC_015 closed:false
    appendObject SUR_004_EntranceCanopy_Set SUR_004_EntranceCanopy_sc3
    SUR_004_EntranceCanopy_sec3 = SUR_004_EntranceCanopy_Set.numObjects
    local SUR_004_EntranceCanopy_rel = NURBS1RailSweepSurface rail:SUR_004_EntranceCanopy_rail1 parallel:true renderable:true generateUVs1:true matID:4
    appendCurve SUR_004_EntranceCanopy_rel SUR_004_EntranceCanopy_sec1 flip:false
    appendCurve SUR_004_EntranceCanopy_rel SUR_004_EntranceCanopy_sec2 flip:false
    appendCurve SUR_004_EntranceCanopy_rel SUR_004_EntranceCanopy_sec3 flip:false
    appendObject SUR_004_EntranceCanopy_Set SUR_004_EntranceCanopy_rel
    SUR_004_EntranceCanopy_Set.merge = 0.15
    local SUR_004_EntranceCanopy = NURBSNode SUR_004_EntranceCanopy_Set name:"SUR_004_EntranceCanopy"
    MCP_NURBS_Arch.applyArchTessellation SUR_004_EntranceCanopy hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_004_EntranceCanopy hideCurves:true mergeTol:0.2 uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
    local census_SUR_004_EntranceCanopy = mcpNurbsCensus SUR_004_EntranceCanopy "SUR_004_EntranceCanopy" 1
    local SUR_005_NorthWalkway_Set = NURBSSet()
    local SUR_005_NorthWalkway_rail1 = 0
    local SUR_005_NorthWalkway_pc1 = MCP_NURBS_Arch.makePointCurve SEC_016 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_pc1
    SUR_005_NorthWalkway_rail1 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_rail2 = 0
    local SUR_005_NorthWalkway_pc2 = MCP_NURBS_Arch.makePointCurve SEC_017 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_pc2
    SUR_005_NorthWalkway_rail2 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_sec1 = 0
    local SUR_005_NorthWalkway_sc1 = MCP_NURBS_Arch.makePointCurve SEC_018 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_sc1
    SUR_005_NorthWalkway_sec1 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_sec2 = 0
    local SUR_005_NorthWalkway_sc2 = MCP_NURBS_Arch.makePointCurve SEC_019 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_sc2
    SUR_005_NorthWalkway_sec2 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_sec3 = 0
    local SUR_005_NorthWalkway_sc3 = MCP_NURBS_Arch.makePointCurve SEC_020 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_sc3
    SUR_005_NorthWalkway_sec3 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_sec4 = 0
    local SUR_005_NorthWalkway_sc4 = MCP_NURBS_Arch.makePointCurve SEC_021 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_sc4
    SUR_005_NorthWalkway_sec4 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_sec5 = 0
    local SUR_005_NorthWalkway_sc5 = MCP_NURBS_Arch.makePointCurve SEC_022 closed:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_sc5
    SUR_005_NorthWalkway_sec5 = SUR_005_NorthWalkway_Set.numObjects
    local SUR_005_NorthWalkway_rel = NURBS2RailSweepSurface rail1:SUR_005_NorthWalkway_rail1 rail2:SUR_005_NorthWalkway_rail2 parallel:true renderable:true generateUVs1:true matID:5
    appendCurve SUR_005_NorthWalkway_rel SUR_005_NorthWalkway_sec1 flip:false
    appendCurve SUR_005_NorthWalkway_rel SUR_005_NorthWalkway_sec2 flip:false
    appendCurve SUR_005_NorthWalkway_rel SUR_005_NorthWalkway_sec3 flip:false
    appendCurve SUR_005_NorthWalkway_rel SUR_005_NorthWalkway_sec4 flip:false
    appendCurve SUR_005_NorthWalkway_rel SUR_005_NorthWalkway_sec5 flip:false
    appendObject SUR_005_NorthWalkway_Set SUR_005_NorthWalkway_rel
    SUR_005_NorthWalkway_Set.merge = 0.15
    local SUR_005_NorthWalkway = NURBSNode SUR_005_NorthWalkway_Set name:"SUR_005_NorthWalkway"
    MCP_NURBS_Arch.applyArchTessellation SUR_005_NorthWalkway hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_005_NorthWalkway hideCurves:true mergeTol:0.15 uSteps:10 vSteps:8 edgePct:4.0 angleDeg:5.0
    local census_SUR_005_NorthWalkway = mcpNurbsCensus SUR_005_NorthWalkway "SUR_005_NorthWalkway" 1
    local SUR_006_CanopySoffit_Set = NURBSSet()
    local SUR_006_CanopySoffit_rel = NURBSBlendSurface parent1ID:id_SUR_001_Vault edge1:4 parent2ID:id_SUR_002_Canopy edge2:4 tension1:0.0 tension2:0.0 renderable:true generateUVs1:true matID:6
    appendObject SUR_006_CanopySoffit_Set SUR_006_CanopySoffit_rel
    SUR_006_CanopySoffit_Set.merge = 0.15
    local SUR_006_CanopySoffit = NURBSNode SUR_006_CanopySoffit_Set name:"SUR_006_CanopySoffit"
    MCP_NURBS_Arch.applyArchTessellation SUR_006_CanopySoffit hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_006_CanopySoffit hideCurves:true mergeTol:0.15 uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
    local census_SUR_006_CanopySoffit = mcpNurbsCensus SUR_006_CanopySoffit "SUR_006_CanopySoffit" 1
    local SUR_007_VaultApertureGuide_Set = NURBSSet()
    local SUR_007_VaultApertureGuide_profile1 = 0
    local SUR_007_VaultApertureGuide_tr1 = MCP_NURBS_Arch.makePointCurve SEC_023 closed:true
    appendObject SUR_007_VaultApertureGuide_Set SUR_007_VaultApertureGuide_tr1
    SUR_007_VaultApertureGuide_profile1 = SUR_007_VaultApertureGuide_Set.numObjects
    local SUR_007_VaultApertureGuide_rel1 = NURBSProjectVectorCurve parent1ID:id_SUR_001_Vault parent2:SUR_007_VaultApertureGuide_profile1 pVec:[0.0,0.0,-1.0] seed:[0.5,0.5] trim:false flipTrim:false
    appendObject SUR_007_VaultApertureGuide_Set SUR_007_VaultApertureGuide_rel1
    SUR_007_VaultApertureGuide_Set.merge = 0.15
    local SUR_007_VaultApertureGuide = NURBSNode SUR_007_VaultApertureGuide_Set name:"SUR_007_VaultApertureGuide"
    MCP_NURBS_Arch.applyArchTessellation SUR_007_VaultApertureGuide hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_007_VaultApertureGuide hideCurves:true mergeTol:0.15 uSteps:8 vSteps:6 edgePct:4.0 angleDeg:6.0
    local census_SUR_007_VaultApertureGuide = mcpNurbsCensus SUR_007_VaultApertureGuide "SUR_007_VaultApertureGuide" 0
    local idx_SUR_001_Vault = mcpNurbsSurfIndex SUR_001_Vault "SUR_001_Vault"
    local DRV_001_VaultPanels = MCP_NURBS_Arch.sampleSurfaceToQuadPoly SUR_001_Vault idx_SUR_001_Vault 8 2 name:"DRV_001_VaultPanels"
    DRV_001_VaultPanels.name = "DRV_001_VaultPanels"
    local idx_SUR_002_Canopy = mcpNurbsSurfIndex SUR_002_Canopy "SUR_002_Canopy"
    local DRV_002_CanopyFrame = MCP_NURBS_Arch.createDiagridOnSurface SUR_002_Canopy idx_SUR_002_Canopy 4 2 thickness:12.0 subSteps:6 name:"DRV_002_CanopyFrame"
    DRV_002_CanopyFrame.name = "DRV_002_CanopyFrame"
    local idx_SUR_003_CanopyCage = mcpNurbsSurfIndex SUR_003_CanopyCage "SUR_003_CanopyCage"
    local DRV_003_CagePanels = MCP_NURBS_Arch.sampleSurfaceToQuadPoly SUR_003_CanopyCage idx_SUR_003_CanopyCage 4 2 name:"DRV_003_CagePanels"
    DRV_003_CagePanels.name = "DRV_003_CagePanels"
    true
)
mcpNurbsBuild_pavilion_01()
