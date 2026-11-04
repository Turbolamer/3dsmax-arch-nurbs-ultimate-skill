(
    -- MODIFIED CALIBRATION, NOT canonical. NOT LIVE-VERIFIED. OPTIONAL ONLY.
    -- One Rectangle, one attach attempt, no broad or named cleanup.
    local beforeCount = objects.count
    local beforeSelection = selection.count
    if beforeCount != 0 or beforeSelection != 0 do throw "P16P3E_REFUSE: expected empty unselected scene"
    if maxFilePath != "" or maxFileName != "" do throw "P16P3E_REFUSE: expected unnamed scene"
    if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "P16P3E_REFUSE: expected mm/1"
    local shapeNode = undefined
    local sm = undefined
    local cthrew = false
    local athrew = false
    local attachAttempted = false
    local workThrew = false
    local mods = undefined
    local first = "?"
    try
    (
        shapeNode = Rectangle name:"P16P3E_SWEEP_6d04f9a2" width:40.0 length:40.0
        try (sm = Sweep()) catch (cthrew = true)
        if not cthrew do
        (
            attachAttempted = true
            try (addModifier shapeNode sm) catch (athrew = true)
        )
        mods = shapeNode.modifiers.count
        if mods > 0 do first = shapeNode.modifiers[1].name
    )
    catch (workThrew = true)
    -- CLEANUP FIRST, even when shape setup/property reads failed.
    local cleanupThrew = false
    local ownedAlive = false
    if shapeNode != undefined do
    (
        try (if isValidNode shapeNode do delete shapeNode) catch (cleanupThrew = true)
        try (ownedAlive = isValidNode shapeNode) catch (ownedAlive = true)
    )
    local censusOk = (objects.count == beforeCount) and (selection.count == beforeSelection)
    local out = "ctor="
    if cthrew then out += "THROWS" else out += "ok"
    out += " attach="
    if athrew then out += "THROWS" else if attachAttempted then out += "ok" else out += "NOT_ATTEMPTED"
    out += " mods=" + (mods as string)
    if mods != undefined and mods > 0 do out += " first=" + first
    out += " modifiedCalibration=true workThrew=" + (workThrew as string) + " cleanupThrew=" + (cleanupThrew as string) + " ownedAlive=" + (ownedAlive as string) + " censusOk=" + (censusOk as string)
    out
)
