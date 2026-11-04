/* build_spec.py --stage massing | project pavilion-01 | DO NOT EDIT */
fn mcpMassingBuild_pavilion_01 = (
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
    local prev_GRP_001 = getNodeByName "GRP_001"
    if prev_GRP_001 != undefined do ( delete prev_GRP_001 )
    local prev_GRP_002 = getNodeByName "GRP_002"
    if prev_GRP_002 != undefined do ( delete prev_GRP_002 )
    local prev_GRP_003 = getNodeByName "GRP_003"
    if prev_GRP_003 != undefined do ( delete prev_GRP_003 )
    local SP_GROUND_PAD = Box width:(860 * __f_unit) length:(660 * __f_unit) height:(30 * __f_unit) pos:([300, 200, -60] * __f_unit)
    SP_GROUND_PAD.name = "SP_GROUND_PAD"
    local EL_001 = Box width:(660 * __f_unit) length:(460 * __f_unit) height:(30 * __f_unit) pos:([300, 200, -30] * __f_unit)
    EL_001.name = "EL_001"
    local EL_002 = Box width:(660 * __f_unit) length:(460 * __f_unit) height:(30 * __f_unit) pos:([300, 200, 300] * __f_unit)
    EL_002.name = "EL_002"
    local EL_003 = Box width:(660 * __f_unit) length:(20 * __f_unit) height:(60 * __f_unit) pos:([300, -20, 330] * __f_unit)
    EL_003.name = "EL_003"
    local EL_004 = Box width:(20 * __f_unit) length:(420 * __f_unit) height:(60 * __f_unit) pos:([620, 200, 330] * __f_unit)
    EL_004.name = "EL_004"
    local EL_005 = Box width:(660 * __f_unit) length:(20 * __f_unit) height:(60 * __f_unit) pos:([300, 420, 330] * __f_unit)
    EL_005.name = "EL_005"
    local EL_006 = Box width:(20 * __f_unit) length:(420 * __f_unit) height:(60 * __f_unit) pos:([-20, 200, 330] * __f_unit)
    EL_006.name = "EL_006"
    local EL_007 = Box width:(660 * __f_unit) length:(20 * __f_unit) height:(330 * __f_unit) pos:([300, -20, 0] * __f_unit)
    EL_007.name = "EL_007"
    local EL_008 = Box width:(660 * __f_unit) length:(20 * __f_unit) height:(330 * __f_unit) pos:([300, 420, 0] * __f_unit)
    EL_008.name = "EL_008"
    local EL_009 = Box width:(20 * __f_unit) length:(460 * __f_unit) height:(330 * __f_unit) pos:([620, 200, 0] * __f_unit)
    EL_009.name = "EL_009"
    local EL_010 = Box width:(20 * __f_unit) length:(460 * __f_unit) height:(330 * __f_unit) pos:([-20, 200, 0] * __f_unit)
    EL_010.name = "EL_010"
    local GRP_001 = Dummy name:"GRP_001"
    GRP_001.pos = ([300, 200, -30] * __f_unit)
    EL_001.parent = GRP_001
    local GRP_002 = Dummy name:"GRP_002"
    GRP_002.pos = ([300, 200, 300] * __f_unit)
    EL_002.parent = GRP_002
    EL_003.parent = GRP_002
    EL_004.parent = GRP_002
    EL_005.parent = GRP_002
    EL_006.parent = GRP_002
    local GRP_003 = Dummy name:"GRP_003"
    GRP_003.pos = ([300, 200, 0] * __f_unit)
    EL_007.parent = GRP_003
    EL_008.parent = GRP_003
    EL_009.parent = GRP_003
    EL_010.parent = GRP_003
    true
)
mcpMassingBuild_pavilion_01()
