(
    -- MODIFIED CALIBRATION, NOT a canonical env_preflight.py body. NOT LIVE-VERIFIED.
    -- No scene/unit/file/selection/dirty-flag writes. Current entry guards only.
    local __before_count = objects.count
    local __before_selection = selection.count
    local __before_type = units.SystemType
    local __before_scale = units.SystemScale
    local __before_path = maxFilePath
    local __before_file = maxFileName
    local __before_save = getSaveRequired()
    if __before_count != 0 or __before_selection != 0 do throw "P16P3E_REFUSE: expected empty unselected scene"
    if __before_path != "" or __before_file != "" do throw "P16P3E_REFUSE: expected unnamed scene"
    if __before_type != #millimeters or __before_scale != 1.0 do throw "P16P3E_REFUSE: expected native millimeters scale 1"
    -- Unit setup verification and scale preamble (P16_P3E_modified_native_calibration)
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
    local __cm_decode = units.decodeValue "1cm"
    local __mm10_decode = units.decodeValue "10mm"
    local __mm1_decode = units.decodeValue "1mm"
    local __ok = (abs (__c_cm - 0.1) <= 0.000001) and (abs (__f_unit - 10.0) <= 0.000001)
    __ok = __ok and (abs (__cm_decode - 10.0) <= 0.000001)
    __ok = __ok and (abs (__mm10_decode - __cm_decode) <= 0.000001)
    __ok = __ok and (abs (__mm1_decode - 1.0) <= 0.000001)
    local __unchanged = (objects.count == __before_count) and (selection.count == __before_selection)
    __unchanged = __unchanged and (units.SystemType == __before_type) and (units.SystemScale == __before_scale)
    __unchanged = __unchanged and (maxFilePath == __before_path) and (maxFileName == __before_file)
    __unchanged = __unchanged and ((getSaveRequired()) == __before_save)
    "MODIFIED_CALIBRATION|native_units_readonly|guard=ok|unitOk=" + (__ok as string) + "|unchanged=" + (__unchanged as string) + "|SystemType=" + (__before_type as string) + " SystemScale=" + (__before_scale as string) + "|c_cm_per_scene=" + (__c_cm as string) + "|f_scene_per_cm=" + (__f_unit as string) + "|decode_1cm=" + (__cm_decode as string) + "|decode_10mm=" + (__mm10_decode as string) + "|decode_1mm=" + (__mm1_decode as string)
)
