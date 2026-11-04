(
    -- MODIFIED CALIBRATION, NOT a canonical env_preflight.py body. NOT LIVE-VERIFIED.
    -- OPTIONAL mutating measurement: one Box, zero modifiers, exact local-ref cleanup.
    -- Names are labels, NEVER lookup/deletion authority. Never clears dirty state.
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
    local __node = undefined
    local __probe_threw = false
    local __probe_error = ""
    local __measure_ok = false
    local __mn = undefined
    local __mx = undefined
    local __actual_name = ""
    try
    (
        __node = Box name:"P16P3E_UNIT_6d04f9a2" width:(10.0 * __f_unit) length:(20.0 * __f_unit) height:(30.0 * __f_unit) pos:([100.0,200.0,300.0] * __f_unit) widthsegs:1 lengthsegs:1 heightsegs:1
        __actual_name = __node.name
        __mn = __node.min
        __mx = __node.max
        -- Independent literal native-unit expectation for mm/1, not an echo of f.
        __measure_ok = (distance __mn [950.0,1900.0,3000.0] <= 0.0001)
        __measure_ok = __measure_ok and (distance __mx [1050.0,2100.0,3300.0] <= 0.0001)
        __measure_ok = __measure_ok and (__node.modifiers.count == 0)
    )
    catch (__probe_threw = true; __probe_error = getCurrentException())

    -- CLEANUP FIRST after guarded work; no property formatting may precede it.
    local __cleanup_threw = false
    local __cleanup_error = ""
    if __node != undefined do
    (
        try (if isValidNode __node do delete __node)
        catch (__cleanup_threw = true; __cleanup_error = getCurrentException())
    )
    local __alive = false
    if __node != undefined do
    (
        try (__alive = isValidNode __node) catch (__alive = true)
    )
    local __census_ok = (objects.count == __before_count) and (selection.count == __before_selection)
    local __units_ok = (units.SystemType == __before_type) and (units.SystemScale == __before_scale)
    local __file_ok = (maxFilePath == __before_path) and (maxFileName == __before_file)
    local __save_after = getSaveRequired()
    "MODIFIED_CALIBRATION|native_box_roundtrip|guard=ok|probeThrew=" + (__probe_threw as string) + "|measureOk=" + (__measure_ok as string) + "|cleanupThrew=" + (__cleanup_threw as string) + "|ownedAlive=" + (__alive as string) + "|censusOk=" + (__census_ok as string) + "|unitsOk=" + (__units_ok as string) + "|fileOk=" + (__file_ok as string) + "|saveBefore=" + (__before_save as string) + "|saveAfter=" + (__save_after as string) + "|actualName=" + __actual_name + "|minNative=" + (__mn as string) + "|maxNative=" + (__mx as string) + "|probeError=" + __probe_error + "|cleanupError=" + __cleanup_error
)
