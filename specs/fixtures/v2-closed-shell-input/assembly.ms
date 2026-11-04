fn mcpAssemblyBuild_pavilion_01 =
(
    -- Unit setup verification and scale preamble (assembly)
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
    -- assembly.json (v2): placements=3 prototypes=3
    -- G-79: no statement below assigns a layer to a node; layer_map stays data.
    -- delete-by-name, twice: deleting a base does not delete its instances.
    local prev_PROTO_DOOR_01_1 = getNodeByName "PROTO_DOOR_01_1"
    if prev_PROTO_DOOR_01_1 != undefined do ( delete prev_PROTO_DOOR_01_1 )
    local prev_PROTO_COMP_WINDOW_2 = getNodeByName "PROTO_COMP_WINDOW_2"
    if prev_PROTO_COMP_WINDOW_2 != undefined do ( delete prev_PROTO_COMP_WINDOW_2 )
    local prev_PROTO_COMP_WINDOW_3 = getNodeByName "PROTO_COMP_WINDOW_3"
    if prev_PROTO_COMP_WINDOW_3 != undefined do ( delete prev_PROTO_COMP_WINDOW_3 )
    local prev_PLC_001 = getNodeByName "PLC_001"
    if prev_PLC_001 != undefined do ( delete prev_PLC_001 )
    local prev_PLC_002 = getNodeByName "PLC_002"
    if prev_PLC_002 != undefined do ( delete prev_PLC_002 )
    local prev_PLC_003 = getNodeByName "PLC_003"
    if prev_PLC_003 != undefined do ( delete prev_PLC_003 )
    local prev_PROTO_DOOR_01_1 = getNodeByName "PROTO_DOOR_01_1"
    if prev_PROTO_DOOR_01_1 != undefined do ( delete prev_PROTO_DOOR_01_1 )
    local prev_PROTO_COMP_WINDOW_2 = getNodeByName "PROTO_COMP_WINDOW_2"
    if prev_PROTO_COMP_WINDOW_2 != undefined do ( delete prev_PROTO_COMP_WINDOW_2 )
    local prev_PROTO_COMP_WINDOW_3 = getNodeByName "PROTO_COMP_WINDOW_3"
    if prev_PROTO_COMP_WINDOW_3 != undefined do ( delete prev_PROTO_COMP_WINDOW_3 )
    local prev_PLC_001 = getNodeByName "PLC_001"
    if prev_PLC_001 != undefined do ( delete prev_PLC_001 )
    local prev_PLC_002 = getNodeByName "PLC_002"
    if prev_PLC_002 != undefined do ( delete prev_PLC_002 )
    local prev_PLC_003 = getNodeByName "PLC_003"
    if prev_PLC_003 != undefined do ( delete prev_PLC_003 )
    -- prototypes: one box per distinct component, sized from rough opening minus clearances.
    local PROTO_DOOR_01_1 = Box width:((98 * __f_unit)) length:((12 * __f_unit)) height:((209 * __f_unit)) pos:[0.0,0.0,0.0]
    PROTO_DOOR_01_1.name = "PROTO_DOOR_01_1"
    PROTO_DOOR_01_1.isHidden = true
    local PROTO_COMP_WINDOW_2 = Box width:((178 * __f_unit)) length:((12 * __f_unit)) height:((119 * __f_unit)) pos:[0.0,0.0,0.0]
    PROTO_COMP_WINDOW_2.name = "PROTO_COMP_WINDOW_2"
    PROTO_COMP_WINDOW_2.isHidden = true
    local PROTO_COMP_WINDOW_3 = Box width:((198 * __f_unit)) length:((12 * __f_unit)) height:((129 * __f_unit)) pos:[0.0,0.0,0.0]
    PROTO_COMP_WINDOW_3.name = "PROTO_COMP_WINDOW_3"
    PROTO_COMP_WINDOW_3.isHidden = true
    -- placements: copy from prototype, share baseObject, transform via orthonormal basis.
    local PLC_001 = copy PROTO_DOOR_01_1
    PLC_001.baseObject = PROTO_DOOR_01_1.baseObject
    PLC_001.name = "PLC_001"
    PLC_001.transform = matrix3 [1.0000000, 0.0000000, 0.0000000] [0.0000000, -1.0000000, 0.0000000] [0.0000000, 0.0000000, 1.0000000] ([150, -16, 0] * __f_unit)
    local PLC_002 = copy PROTO_COMP_WINDOW_2
    PLC_002.baseObject = PROTO_COMP_WINDOW_2.baseObject
    PLC_002.name = "PLC_002"
    PLC_002.transform = matrix3 [1.0000000, 0.0000000, 0.0000000] [0.0000000, -1.0000000, 0.0000000] [0.0000000, 0.0000000, 1.0000000] ([410, -16, 90] * __f_unit)
    local PLC_003 = copy PROTO_COMP_WINDOW_3
    PLC_003.baseObject = PROTO_COMP_WINDOW_3.baseObject
    PLC_003.name = "PLC_003"
    PLC_003.transform = matrix3 [0.0000000, 1.0000000, 0.0000000] [1.0000000, 0.0000000, 0.0000000] [0.0000000, 0.0000000, 1.0000000] ([616, 200, 110] * __f_unit)
    -- Mechanism A: host wall hiding (ensure any legacy facade_wall does not occlude openings)
    for host_name in #("EL_007", "EL_008", "EL_009", "EL_010") do (
        local host_nd = getNodeByName host_name
        if host_nd != undefined do host_nd.isHidden = true
    )
    -- Census assert: count placed instances
    local placed_found = 0
    if (getNodeByName "PLC_001") != undefined do placed_found = placed_found + 1
    if (getNodeByName "PLC_002") != undefined do placed_found = placed_found + 1
    if (getNodeByName "PLC_003") != undefined do placed_found = placed_found + 1
    if placed_found != 3 do (
        throw ("Census failure: expected 3 placed nodes, found " + (placed_found as string))
    )
    true
)
mcpAssemblyBuild_pavilion_01()
