/* build_nurbs.py | project form-precision | DO NOT EDIT */
fn mcpNurbsBuild_form_precision = (
    -- Unit setup verification and scale preamble (nurbs)
    local __sys_scale = units.SystemScale as float
    if __sys_scale == undefined or __sys_scale <= 0.0 do (
        throw ("Invalid units.SystemScale: " + (__sys_scale as string) + "; must be positive")
    )
    local __sys_type_raw = units.SystemType as string
    local __sys_type_str = toLower (units.SystemType as string)
    if (substring __sys_type_str 1 1) == "#" do __sys_type_str = substring __sys_type_str 2 -1
    local __k_cm = case __sys_type_str of (
        "centimeters": 1.0
        "millimeters": 0.1
        "meters": 100.0
        "kilometers": 100000.0
        "inches": 2.54
        "feet": 30.48
        "miles": 160934.4
        "yards": 91.44
        default: undefined
    )
    if __k_cm == undefined do (
        throw ("Uncertified or unknown units.SystemType: " + (units.SystemType as string))
    )
    local __c_cm = __k_cm * __sys_scale
    local __f_unit = 1.0 / __c_cm
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
    local SEC_001 = #(([0, 0, 420] * __f_unit),([1.92697, 0, 431.773] * __f_unit),([7.69963, 0, 443.495] * __f_unit),([17.2932, 0, 455.116] * __f_unit),([30.6668, 0, 466.587] * __f_unit),([47.7629, 0, 477.859] * __f_unit),([68.5084, 0, 488.883] * __f_unit),([92.8145, 0, 499.612] * __f_unit),([120.577, 0, 510] * __f_unit),([151.677, 0, 520.003] * __f_unit),([185.982, 0, 529.577] * __f_unit),([223.344, 0, 538.682] * __f_unit),([263.604, 0, 547.279] * __f_unit),([306.589, 0, 555.331] * __f_unit),([352.115, 0, 562.804] * __f_unit),([399.987, 0, 569.665] * __f_unit),([450, 0, 575.885] * __f_unit),([501.94, 0, 581.437] * __f_unit),([555.585, 0, 586.298] * __f_unit),([610.704, 0, 590.447] * __f_unit),([667.063, 0, 593.867] * __f_unit),([724.419, 0, 596.541] * __f_unit),([782.526, 0, 598.46] * __f_unit),([841.137, 0, 599.615] * __f_unit),([900, 0, 600] * __f_unit),([958.863, 0, 599.615] * __f_unit),([1017.47, 0, 598.46] * __f_unit),([1075.58, 0, 596.541] * __f_unit),([1132.94, 0, 593.867] * __f_unit),([1189.3, 0, 590.447] * __f_unit),([1244.42, 0, 586.298] * __f_unit),([1298.06, 0, 581.437] * __f_unit),([1350, 0, 575.885] * __f_unit),([1400.01, 0, 569.665] * __f_unit),([1447.89, 0, 562.804] * __f_unit),([1493.41, 0, 555.331] * __f_unit),([1536.4, 0, 547.279] * __f_unit),([1576.66, 0, 538.682] * __f_unit),([1614.02, 0, 529.577] * __f_unit),([1648.32, 0, 520.003] * __f_unit),([1679.42, 0, 510] * __f_unit),([1707.19, 0, 499.612] * __f_unit),([1731.49, 0, 488.883] * __f_unit),([1752.24, 0, 477.859] * __f_unit),([1769.33, 0, 466.587] * __f_unit),([1782.71, 0, 455.116] * __f_unit),([1792.3, 0, 443.495] * __f_unit),([1798.07, 0, 431.773] * __f_unit),([1800, 0, 420] * __f_unit))
    local SEC_002 = #(([0, 225, 420] * __f_unit),([1.92697, 225, 431.773] * __f_unit),([7.69963, 225, 443.495] * __f_unit),([17.2932, 225, 455.116] * __f_unit),([30.6668, 225, 466.587] * __f_unit),([47.7629, 225, 477.859] * __f_unit),([68.5084, 225, 488.883] * __f_unit),([92.8145, 225, 499.612] * __f_unit),([120.577, 225, 510] * __f_unit),([151.677, 225, 520.003] * __f_unit),([185.982, 225, 529.577] * __f_unit),([223.344, 225, 538.682] * __f_unit),([263.604, 225, 547.279] * __f_unit),([306.589, 225, 555.331] * __f_unit),([352.115, 225, 562.804] * __f_unit),([399.987, 225, 569.665] * __f_unit),([450, 225, 575.885] * __f_unit),([501.94, 225, 581.437] * __f_unit),([555.585, 225, 586.298] * __f_unit),([610.704, 225, 590.447] * __f_unit),([667.063, 225, 593.867] * __f_unit),([724.419, 225, 596.541] * __f_unit),([782.526, 225, 598.46] * __f_unit),([841.137, 225, 599.615] * __f_unit),([900, 225, 600] * __f_unit),([958.863, 225, 599.615] * __f_unit),([1017.47, 225, 598.46] * __f_unit),([1075.58, 225, 596.541] * __f_unit),([1132.94, 225, 593.867] * __f_unit),([1189.3, 225, 590.447] * __f_unit),([1244.42, 225, 586.298] * __f_unit),([1298.06, 225, 581.437] * __f_unit),([1350, 225, 575.885] * __f_unit),([1400.01, 225, 569.665] * __f_unit),([1447.89, 225, 562.804] * __f_unit),([1493.41, 225, 555.331] * __f_unit),([1536.4, 225, 547.279] * __f_unit),([1576.66, 225, 538.682] * __f_unit),([1614.02, 225, 529.577] * __f_unit),([1648.32, 225, 520.003] * __f_unit),([1679.42, 225, 510] * __f_unit),([1707.19, 225, 499.612] * __f_unit),([1731.49, 225, 488.883] * __f_unit),([1752.24, 225, 477.859] * __f_unit),([1769.33, 225, 466.587] * __f_unit),([1782.71, 225, 455.116] * __f_unit),([1792.3, 225, 443.495] * __f_unit),([1798.07, 225, 431.773] * __f_unit),([1800, 225, 420] * __f_unit))
    local SEC_003 = #(([0, 450, 420] * __f_unit),([1.92697, 450, 431.773] * __f_unit),([7.69963, 450, 443.495] * __f_unit),([17.2932, 450, 455.116] * __f_unit),([30.6668, 450, 466.587] * __f_unit),([47.7629, 450, 477.859] * __f_unit),([68.5084, 450, 488.883] * __f_unit),([92.8145, 450, 499.612] * __f_unit),([120.577, 450, 510] * __f_unit),([151.677, 450, 520.003] * __f_unit),([185.982, 450, 529.577] * __f_unit),([223.344, 450, 538.682] * __f_unit),([263.604, 450, 547.279] * __f_unit),([306.589, 450, 555.331] * __f_unit),([352.115, 450, 562.804] * __f_unit),([399.987, 450, 569.665] * __f_unit),([450, 450, 575.885] * __f_unit),([501.94, 450, 581.437] * __f_unit),([555.585, 450, 586.298] * __f_unit),([610.704, 450, 590.447] * __f_unit),([667.063, 450, 593.867] * __f_unit),([724.419, 450, 596.541] * __f_unit),([782.526, 450, 598.46] * __f_unit),([841.137, 450, 599.615] * __f_unit),([900, 450, 600] * __f_unit),([958.863, 450, 599.615] * __f_unit),([1017.47, 450, 598.46] * __f_unit),([1075.58, 450, 596.541] * __f_unit),([1132.94, 450, 593.867] * __f_unit),([1189.3, 450, 590.447] * __f_unit),([1244.42, 450, 586.298] * __f_unit),([1298.06, 450, 581.437] * __f_unit),([1350, 450, 575.885] * __f_unit),([1400.01, 450, 569.665] * __f_unit),([1447.89, 450, 562.804] * __f_unit),([1493.41, 450, 555.331] * __f_unit),([1536.4, 450, 547.279] * __f_unit),([1576.66, 450, 538.682] * __f_unit),([1614.02, 450, 529.577] * __f_unit),([1648.32, 450, 520.003] * __f_unit),([1679.42, 450, 510] * __f_unit),([1707.19, 450, 499.612] * __f_unit),([1731.49, 450, 488.883] * __f_unit),([1752.24, 450, 477.859] * __f_unit),([1769.33, 450, 466.587] * __f_unit),([1782.71, 450, 455.116] * __f_unit),([1792.3, 450, 443.495] * __f_unit),([1798.07, 450, 431.773] * __f_unit),([1800, 450, 420] * __f_unit))
    local SEC_004 = #(([0, 675, 420] * __f_unit),([1.92697, 675, 431.773] * __f_unit),([7.69963, 675, 443.495] * __f_unit),([17.2932, 675, 455.116] * __f_unit),([30.6668, 675, 466.587] * __f_unit),([47.7629, 675, 477.859] * __f_unit),([68.5084, 675, 488.883] * __f_unit),([92.8145, 675, 499.612] * __f_unit),([120.577, 675, 510] * __f_unit),([151.677, 675, 520.003] * __f_unit),([185.982, 675, 529.577] * __f_unit),([223.344, 675, 538.682] * __f_unit),([263.604, 675, 547.279] * __f_unit),([306.589, 675, 555.331] * __f_unit),([352.115, 675, 562.804] * __f_unit),([399.987, 675, 569.665] * __f_unit),([450, 675, 575.885] * __f_unit),([501.94, 675, 581.437] * __f_unit),([555.585, 675, 586.298] * __f_unit),([610.704, 675, 590.447] * __f_unit),([667.063, 675, 593.867] * __f_unit),([724.419, 675, 596.541] * __f_unit),([782.526, 675, 598.46] * __f_unit),([841.137, 675, 599.615] * __f_unit),([900, 675, 600] * __f_unit),([958.863, 675, 599.615] * __f_unit),([1017.47, 675, 598.46] * __f_unit),([1075.58, 675, 596.541] * __f_unit),([1132.94, 675, 593.867] * __f_unit),([1189.3, 675, 590.447] * __f_unit),([1244.42, 675, 586.298] * __f_unit),([1298.06, 675, 581.437] * __f_unit),([1350, 675, 575.885] * __f_unit),([1400.01, 675, 569.665] * __f_unit),([1447.89, 675, 562.804] * __f_unit),([1493.41, 675, 555.331] * __f_unit),([1536.4, 675, 547.279] * __f_unit),([1576.66, 675, 538.682] * __f_unit),([1614.02, 675, 529.577] * __f_unit),([1648.32, 675, 520.003] * __f_unit),([1679.42, 675, 510] * __f_unit),([1707.19, 675, 499.612] * __f_unit),([1731.49, 675, 488.883] * __f_unit),([1752.24, 675, 477.859] * __f_unit),([1769.33, 675, 466.587] * __f_unit),([1782.71, 675, 455.116] * __f_unit),([1792.3, 675, 443.495] * __f_unit),([1798.07, 675, 431.773] * __f_unit),([1800, 675, 420] * __f_unit))
    local SEC_005 = #(([0, 900, 420] * __f_unit),([1.92697, 900, 431.773] * __f_unit),([7.69963, 900, 443.495] * __f_unit),([17.2932, 900, 455.116] * __f_unit),([30.6668, 900, 466.587] * __f_unit),([47.7629, 900, 477.859] * __f_unit),([68.5084, 900, 488.883] * __f_unit),([92.8145, 900, 499.612] * __f_unit),([120.577, 900, 510] * __f_unit),([151.677, 900, 520.003] * __f_unit),([185.982, 900, 529.577] * __f_unit),([223.344, 900, 538.682] * __f_unit),([263.604, 900, 547.279] * __f_unit),([306.589, 900, 555.331] * __f_unit),([352.115, 900, 562.804] * __f_unit),([399.987, 900, 569.665] * __f_unit),([450, 900, 575.885] * __f_unit),([501.94, 900, 581.437] * __f_unit),([555.585, 900, 586.298] * __f_unit),([610.704, 900, 590.447] * __f_unit),([667.063, 900, 593.867] * __f_unit),([724.419, 900, 596.541] * __f_unit),([782.526, 900, 598.46] * __f_unit),([841.137, 900, 599.615] * __f_unit),([900, 900, 600] * __f_unit),([958.863, 900, 599.615] * __f_unit),([1017.47, 900, 598.46] * __f_unit),([1075.58, 900, 596.541] * __f_unit),([1132.94, 900, 593.867] * __f_unit),([1189.3, 900, 590.447] * __f_unit),([1244.42, 900, 586.298] * __f_unit),([1298.06, 900, 581.437] * __f_unit),([1350, 900, 575.885] * __f_unit),([1400.01, 900, 569.665] * __f_unit),([1447.89, 900, 562.804] * __f_unit),([1493.41, 900, 555.331] * __f_unit),([1536.4, 900, 547.279] * __f_unit),([1576.66, 900, 538.682] * __f_unit),([1614.02, 900, 529.577] * __f_unit),([1648.32, 900, 520.003] * __f_unit),([1679.42, 900, 510] * __f_unit),([1707.19, 900, 499.612] * __f_unit),([1731.49, 900, 488.883] * __f_unit),([1752.24, 900, 477.859] * __f_unit),([1769.33, 900, 466.587] * __f_unit),([1782.71, 900, 455.116] * __f_unit),([1792.3, 900, 443.495] * __f_unit),([1798.07, 900, 431.773] * __f_unit),([1800, 900, 420] * __f_unit))
    local SEC_006 = #(([0, 0, 420] * __f_unit),([150, 0, 420] * __f_unit),([300, 0, 420] * __f_unit),([450, 0, 420] * __f_unit),([600, 0, 420] * __f_unit))
    local SEC_007 = #(([0, 225, 420] * __f_unit),([150, 225, 487.5] * __f_unit),([300, 225, 510] * __f_unit),([450, 225, 487.5] * __f_unit),([600, 225, 420] * __f_unit))
    local SEC_008 = #(([0, 450, 420] * __f_unit),([150, 450, 420] * __f_unit),([300, 450, 420] * __f_unit),([450, 450, 420] * __f_unit),([600, 450, 420] * __f_unit))
    local SEC_009 = #(([0, 0, 420] * __f_unit),([150, 0, 420] * __f_unit),([300, 0, 420] * __f_unit),([450, 0, 420] * __f_unit),([600, 0, 420] * __f_unit))
    local SEC_010 = #(([0, 225, 420] * __f_unit),([150, 225, 465] * __f_unit),([300, 225, 480] * __f_unit),([450, 225, 465] * __f_unit),([600, 225, 420] * __f_unit))
    local SEC_011 = #(([0, 450, 420] * __f_unit),([150, 450, 420] * __f_unit),([300, 450, 420] * __f_unit),([450, 450, 420] * __f_unit),([600, 450, 420] * __f_unit))
    local SEC_012 = #(([675, 0, 300] * __f_unit),([675, 225, 300] * __f_unit),([675, 450, 300] * __f_unit))
    local SEC_013 = #(([450, 0, 260] * __f_unit),([562.5, 0, 290] * __f_unit),([675, 0, 300] * __f_unit),([787.5, 0, 290] * __f_unit),([900, 0, 260] * __f_unit))
    local SEC_014 = #(([450, 225, 260] * __f_unit),([562.5, 225, 290] * __f_unit),([675, 225, 300] * __f_unit),([787.5, 225, 290] * __f_unit),([900, 225, 260] * __f_unit))
    local SEC_015 = #(([450, 450, 260] * __f_unit),([562.5, 450, 290] * __f_unit),([675, 450, 300] * __f_unit),([787.5, 450, 290] * __f_unit),([900, 450, 260] * __f_unit))
    local SEC_016 = #(([0, 525, 30] * __f_unit),([450, 581.25, 30] * __f_unit),([900, 600, 30] * __f_unit),([1350, 581.25, 30] * __f_unit),([1800, 525, 30] * __f_unit))
    local SEC_017 = #(([0, 600, 30] * __f_unit),([450, 768.75, 30] * __f_unit),([900, 825, 30] * __f_unit),([1350, 768.75, 30] * __f_unit),([1800, 600, 30] * __f_unit))
    local SEC_018 = #(([0, 525, 30] * __f_unit),([0, 562.5, 30] * __f_unit),([0, 600, 30] * __f_unit))
    local SEC_019 = #(([450, 581.25, 30] * __f_unit),([450, 675, 30] * __f_unit),([450, 768.75, 30] * __f_unit))
    local SEC_020 = #(([900, 600, 30] * __f_unit),([900, 712.5, 30] * __f_unit),([900, 825, 30] * __f_unit))
    local SEC_021 = #(([1350, 581.25, 30] * __f_unit),([1350, 675, 30] * __f_unit),([1350, 768.75, 30] * __f_unit))
    local SEC_022 = #(([1800, 525, 30] * __f_unit),([1800, 562.5, 30] * __f_unit),([1800, 600, 30] * __f_unit))
    local SEC_023 = #(([750, 375, 700] * __f_unit),([1050, 375, 700] * __f_unit),([1050, 525, 700] * __f_unit),([750, 525, 700] * __f_unit))
    local SUR_001_Vault = MCP_NURBS_Arch.createULoftShell #(SEC_001,SEC_002,SEC_003,SEC_004,SEC_005) name:"SUR_001_Vault" thickness:(25 * __f_unit) hasShell:true closedSections:false hideCurves:true mergeTol:(0.15 * __f_unit)
    local set_SUR_001_Vault = getNURBSSet SUR_001_Vault #relational
    set_SUR_001_Vault.merge = (0.15 * __f_unit)
    MCP_NURBS_Arch.applyArchTessellation SUR_001_Vault hideCurves:true mergeTol:(0.15 * __f_unit) uSteps:12 vSteps:8 edgePct:3.0 angleDeg:4.0
    local id_SUR_001_Vault = mcpNurbsSurfID SUR_001_Vault "SUR_001_Vault"
    local SUR_002_Canopy = MCP_NURBS_Arch.makePointSurfaceGrid #(SEC_006,SEC_007,SEC_008) name:"SUR_002_Canopy" matID:2 hideCurves:true mergeTol:(0.15 * __f_unit)
    MCP_NURBS_Arch.applyArchTessellation SUR_002_Canopy hideCurves:true mergeTol:(0.2 * __f_unit) uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
    local id_SUR_002_Canopy = mcpNurbsSurfID SUR_002_Canopy "SUR_002_Canopy"
    local SUR_003_CanopyCage = MCP_NURBS_Arch.makeCVSurfaceGrid #(SEC_009,SEC_010,SEC_011) name:"SUR_003_CanopyCage" uOrder:3 vOrder:3 matID:3 hideCurves:true mergeTol:(0.15 * __f_unit)
    MCP_NURBS_Arch.applyArchTessellation SUR_003_CanopyCage hideCurves:true mergeTol:(0.15 * __f_unit) uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
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
    SUR_004_EntranceCanopy_Set.merge = (0.15 * __f_unit)
    local SUR_004_EntranceCanopy = NURBSNode SUR_004_EntranceCanopy_Set name:"SUR_004_EntranceCanopy"
    MCP_NURBS_Arch.applyArchTessellation SUR_004_EntranceCanopy hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_004_EntranceCanopy hideCurves:true mergeTol:(0.2 * __f_unit) uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
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
    SUR_005_NorthWalkway_Set.merge = (0.15 * __f_unit)
    local SUR_005_NorthWalkway = NURBSNode SUR_005_NorthWalkway_Set name:"SUR_005_NorthWalkway"
    MCP_NURBS_Arch.applyArchTessellation SUR_005_NorthWalkway hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_005_NorthWalkway hideCurves:true mergeTol:(0.15 * __f_unit) uSteps:10 vSteps:8 edgePct:4.0 angleDeg:5.0
    local census_SUR_005_NorthWalkway = mcpNurbsCensus SUR_005_NorthWalkway "SUR_005_NorthWalkway" 1
    local SUR_006_CanopySoffit_Set = NURBSSet()
    local SUR_006_CanopySoffit_rel = NURBSBlendSurface parent1ID:id_SUR_001_Vault edge1:4 parent2ID:id_SUR_002_Canopy edge2:4 tension1:0.0 tension2:0.0 renderable:true generateUVs1:true matID:6
    appendObject SUR_006_CanopySoffit_Set SUR_006_CanopySoffit_rel
    SUR_006_CanopySoffit_Set.merge = (0.15 * __f_unit)
    local SUR_006_CanopySoffit = NURBSNode SUR_006_CanopySoffit_Set name:"SUR_006_CanopySoffit"
    MCP_NURBS_Arch.applyArchTessellation SUR_006_CanopySoffit hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_006_CanopySoffit hideCurves:true mergeTol:(0.15 * __f_unit) uSteps:8 vSteps:6 edgePct:5.0 angleDeg:6.0
    local census_SUR_006_CanopySoffit = mcpNurbsCensus SUR_006_CanopySoffit "SUR_006_CanopySoffit" 1
    local SUR_007_VaultApertureGuide_Set = NURBSSet()
    local SUR_007_VaultApertureGuide_profile1 = 0
    local SUR_007_VaultApertureGuide_tr1 = MCP_NURBS_Arch.makePointCurve SEC_023 closed:true
    appendObject SUR_007_VaultApertureGuide_Set SUR_007_VaultApertureGuide_tr1
    SUR_007_VaultApertureGuide_profile1 = SUR_007_VaultApertureGuide_Set.numObjects
    local SUR_007_VaultApertureGuide_rel1 = NURBSProjectVectorCurve parent1ID:id_SUR_001_Vault parent2:SUR_007_VaultApertureGuide_profile1 pVec:[0.0,0.0,-1.0] seed:[0.5,0.5] trim:false flipTrim:false
    appendObject SUR_007_VaultApertureGuide_Set SUR_007_VaultApertureGuide_rel1
    SUR_007_VaultApertureGuide_Set.merge = (0.15 * __f_unit)
    local SUR_007_VaultApertureGuide = NURBSNode SUR_007_VaultApertureGuide_Set name:"SUR_007_VaultApertureGuide"
    MCP_NURBS_Arch.applyArchTessellation SUR_007_VaultApertureGuide hideCurves:true
    MCP_NURBS_Arch.applyArchTessellation SUR_007_VaultApertureGuide hideCurves:true mergeTol:(0.15 * __f_unit) uSteps:8 vSteps:6 edgePct:4.0 angleDeg:6.0
    local census_SUR_007_VaultApertureGuide = mcpNurbsCensus SUR_007_VaultApertureGuide "SUR_007_VaultApertureGuide" 0
    local idx_SUR_001_Vault = mcpNurbsSurfIndex SUR_001_Vault "SUR_001_Vault"
    local DRV_001_VaultPanels = MCP_NURBS_Arch.sampleSurfaceToQuadPoly SUR_001_Vault idx_SUR_001_Vault 8 2 name:"DRV_001_VaultPanels"
    DRV_001_VaultPanels.name = "DRV_001_VaultPanels"
    local idx_SUR_002_Canopy = mcpNurbsSurfIndex SUR_002_Canopy "SUR_002_Canopy"
    local DRV_002_CanopyFrame = MCP_NURBS_Arch.createDiagridOnSurface SUR_002_Canopy idx_SUR_002_Canopy 4 2 thickness:(12 * __f_unit) subSteps:6 name:"DRV_002_CanopyFrame"
    DRV_002_CanopyFrame.name = "DRV_002_CanopyFrame"
    local idx_SUR_003_CanopyCage = mcpNurbsSurfIndex SUR_003_CanopyCage "SUR_003_CanopyCage"
    local DRV_003_CagePanels = MCP_NURBS_Arch.sampleSurfaceToQuadPoly SUR_003_CanopyCage idx_SUR_003_CanopyCage 4 2 name:"DRV_003_CagePanels"
    DRV_003_CagePanels.name = "DRV_003_CagePanels"
    true
)
mcpNurbsBuild_form_precision()
