/* build_spec.py --stage massing | project form-precision | DO NOT EDIT */
fn mcpMassingBuild_form_precision = (
    -- Unit setup verification and scale preamble (massing)
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
    try ( LayerManager.newLayerFromName "00_SITE" ) catch ( print "00_SITE already exists" )
    try ( LayerManager.newLayerFromName "01_SLABS" ) catch ( print "01_SLABS already exists" )
    try ( LayerManager.newLayerFromName "02_STRUCTURE" ) catch ( print "02_STRUCTURE already exists" )
    try ( LayerManager.newLayerFromName "03_CORE" ) catch ( print "03_CORE already exists" )
    try ( LayerManager.newLayerFromName "04_ROOF" ) catch ( print "04_ROOF already exists" )
    try ( LayerManager.newLayerFromName "05_FACADE" ) catch ( print "05_FACADE already exists" )
    try ( LayerManager.newLayerFromName "90_SCENE" ) catch ( print "90_SCENE already exists" )
    local prev_SP_GROUND_PAD = getNodeByName "SP_GROUND_PAD"
    if prev_SP_GROUND_PAD != undefined do ( delete prev_SP_GROUND_PAD )
    local prev_EL_001 = getNodeByName "EL_001"
    if prev_EL_001 != undefined do ( delete prev_EL_001 )
    local prev_EL_002 = getNodeByName "EL_002"
    if prev_EL_002 != undefined do ( delete prev_EL_002 )
    local prev_EL_003 = getNodeByName "EL_003"
    if prev_EL_003 != undefined do ( delete prev_EL_003 )
    local prev_EL_004 = getNodeByName "EL_004"
    if prev_EL_004 != undefined do ( delete prev_EL_004 )
    local prev_EL_005 = getNodeByName "EL_005"
    if prev_EL_005 != undefined do ( delete prev_EL_005 )
    local prev_EL_006 = getNodeByName "EL_006"
    if prev_EL_006 != undefined do ( delete prev_EL_006 )
    local prev_EL_007 = getNodeByName "EL_007"
    if prev_EL_007 != undefined do ( delete prev_EL_007 )
    local prev_EL_008 = getNodeByName "EL_008"
    if prev_EL_008 != undefined do ( delete prev_EL_008 )
    local prev_EL_009 = getNodeByName "EL_009"
    if prev_EL_009 != undefined do ( delete prev_EL_009 )
    local prev_EL_010 = getNodeByName "EL_010"
    if prev_EL_010 != undefined do ( delete prev_EL_010 )
    local prev_EL_011 = getNodeByName "EL_011"
    if prev_EL_011 != undefined do ( delete prev_EL_011 )
    local prev_EL_012 = getNodeByName "EL_012"
    if prev_EL_012 != undefined do ( delete prev_EL_012 )
    local prev_EL_013 = getNodeByName "EL_013"
    if prev_EL_013 != undefined do ( delete prev_EL_013 )
    local prev_EL_014 = getNodeByName "EL_014"
    if prev_EL_014 != undefined do ( delete prev_EL_014 )
    local prev_EL_015 = getNodeByName "EL_015"
    if prev_EL_015 != undefined do ( delete prev_EL_015 )
    local prev_EL_016 = getNodeByName "EL_016"
    if prev_EL_016 != undefined do ( delete prev_EL_016 )
    local prev_EL_017 = getNodeByName "EL_017"
    if prev_EL_017 != undefined do ( delete prev_EL_017 )
    local prev_EL_018 = getNodeByName "EL_018"
    if prev_EL_018 != undefined do ( delete prev_EL_018 )
    local prev_EL_019 = getNodeByName "EL_019"
    if prev_EL_019 != undefined do ( delete prev_EL_019 )
    local prev_EL_020 = getNodeByName "EL_020"
    if prev_EL_020 != undefined do ( delete prev_EL_020 )
    local prev_EL_021 = getNodeByName "EL_021"
    if prev_EL_021 != undefined do ( delete prev_EL_021 )
    local prev_GRP_001 = getNodeByName "GRP_001"
    if prev_GRP_001 != undefined do ( delete prev_GRP_001 )
    local prev_GRP_002 = getNodeByName "GRP_002"
    if prev_GRP_002 != undefined do ( delete prev_GRP_002 )
    local prev_GRP_003 = getNodeByName "GRP_003"
    if prev_GRP_003 != undefined do ( delete prev_GRP_003 )
    local prev_GRP_004 = getNodeByName "GRP_004"
    if prev_GRP_004 != undefined do ( delete prev_GRP_004 )
    local prev_GRP_005 = getNodeByName "GRP_005"
    if prev_GRP_005 != undefined do ( delete prev_GRP_005 )
    local SP_GROUND_PAD = Box width:(2400 * __f_unit) length:(1500 * __f_unit) height:(30 * __f_unit) pos:([900, 450, -30] * __f_unit)
    SP_GROUND_PAD.name = "SP_GROUND_PAD"
    local EL_001 = Box width:(1800 * __f_unit) length:(900 * __f_unit) height:(30 * __f_unit) pos:([900, 450, -30] * __f_unit)
    EL_001.name = "EL_001"
    local EL_002 = Box width:(1800 * __f_unit) length:(900 * __f_unit) height:(25 * __f_unit) pos:([900, 450, 395] * __f_unit)
    EL_002.name = "EL_002"
    local EL_003 = Box width:(40 * __f_unit) length:(40 * __f_unit) height:(450 * __f_unit) pos:([450, 450, -30] * __f_unit)
    EL_003.name = "EL_003"
    local EL_004 = Box width:(40 * __f_unit) length:(40 * __f_unit) height:(450 * __f_unit) pos:([900, 450, -30] * __f_unit)
    EL_004.name = "EL_004"
    local EL_005 = Box width:(40 * __f_unit) length:(40 * __f_unit) height:(425 * __f_unit) pos:([450, 450, 395] * __f_unit)
    EL_005.name = "EL_005"
    local EL_006 = Box width:(40 * __f_unit) length:(40 * __f_unit) height:(425 * __f_unit) pos:([900, 450, 395] * __f_unit)
    EL_006.name = "EL_006"
    local EL_007 = Box width:(400 * __f_unit) length:(400 * __f_unit) height:(420 * __f_unit) pos:([1575, 225, 0] * __f_unit)
    EL_007.name = "EL_007"
    local EL_008 = Box width:(400 * __f_unit) length:(400 * __f_unit) height:(400 * __f_unit) pos:([1575, 225, 420] * __f_unit)
    EL_008.name = "EL_008"
    local EL_009 = Box width:(1800 * __f_unit) length:(900 * __f_unit) height:(30 * __f_unit) pos:([900, 450, 790] * __f_unit)
    EL_009.name = "EL_009"
    local EL_010 = Box width:(1800 * __f_unit) length:(30 * __f_unit) height:(90 * __f_unit) pos:([900, 15, 820] * __f_unit)
    EL_010.name = "EL_010"
    local EL_011 = Box width:(30 * __f_unit) length:(840 * __f_unit) height:(90 * __f_unit) pos:([1785, 450, 820] * __f_unit)
    EL_011.name = "EL_011"
    local EL_012 = Box width:(1800 * __f_unit) length:(30 * __f_unit) height:(90 * __f_unit) pos:([900, 885, 820] * __f_unit)
    EL_012.name = "EL_012"
    local EL_013 = Box width:(30 * __f_unit) length:(840 * __f_unit) height:(90 * __f_unit) pos:([15, 450, 820] * __f_unit)
    EL_013.name = "EL_013"
    local EL_014 = Box width:(1800 * __f_unit) length:(20 * __f_unit) height:(420 * __f_unit) pos:([900, 10, 0] * __f_unit)
    EL_014.name = "EL_014"
    local EL_015 = Box width:(1800 * __f_unit) length:(20 * __f_unit) height:(400 * __f_unit) pos:([900, 10, 420] * __f_unit)
    EL_015.name = "EL_015"
    local EL_016 = Box width:(1800 * __f_unit) length:(20 * __f_unit) height:(420 * __f_unit) pos:([900, 890, 0] * __f_unit)
    EL_016.name = "EL_016"
    local EL_017 = Box width:(1800 * __f_unit) length:(20 * __f_unit) height:(400 * __f_unit) pos:([900, 890, 420] * __f_unit)
    EL_017.name = "EL_017"
    local EL_018 = Box width:(20 * __f_unit) length:(900 * __f_unit) height:(420 * __f_unit) pos:([1790, 450, 0] * __f_unit)
    EL_018.name = "EL_018"
    local EL_019 = Box width:(20 * __f_unit) length:(900 * __f_unit) height:(400 * __f_unit) pos:([1790, 450, 420] * __f_unit)
    EL_019.name = "EL_019"
    local EL_020 = Box width:(20 * __f_unit) length:(900 * __f_unit) height:(420 * __f_unit) pos:([10, 450, 0] * __f_unit)
    EL_020.name = "EL_020"
    local EL_021 = Box width:(20 * __f_unit) length:(900 * __f_unit) height:(400 * __f_unit) pos:([10, 450, 420] * __f_unit)
    EL_021.name = "EL_021"
    local GRP_001 = Dummy name:"GRP_001"
    GRP_001.pos = ([900, 450, -30] * __f_unit)
    EL_001.parent = GRP_001
    EL_002.parent = GRP_001
    local GRP_002 = Dummy name:"GRP_002"
    GRP_002.pos = ([675, 450, -30] * __f_unit)
    EL_003.parent = GRP_002
    EL_004.parent = GRP_002
    EL_005.parent = GRP_002
    EL_006.parent = GRP_002
    local GRP_003 = Dummy name:"GRP_003"
    GRP_003.pos = ([1575, 225, 0] * __f_unit)
    EL_007.parent = GRP_003
    EL_008.parent = GRP_003
    local GRP_004 = Dummy name:"GRP_004"
    GRP_004.pos = ([900, 450, 790] * __f_unit)
    EL_009.parent = GRP_004
    EL_010.parent = GRP_004
    EL_011.parent = GRP_004
    EL_012.parent = GRP_004
    EL_013.parent = GRP_004
    local GRP_005 = Dummy name:"GRP_005"
    GRP_005.pos = ([900, 450, 0] * __f_unit)
    EL_014.parent = GRP_005
    EL_015.parent = GRP_005
    EL_016.parent = GRP_005
    EL_017.parent = GRP_005
    EL_018.parent = GRP_005
    EL_019.parent = GRP_005
    EL_020.parent = GRP_005
    EL_021.parent = GRP_005
    true
)
mcpMassingBuild_form_precision()
