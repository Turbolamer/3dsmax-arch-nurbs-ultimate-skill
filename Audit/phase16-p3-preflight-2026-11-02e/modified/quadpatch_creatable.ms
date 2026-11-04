(
    -- MODIFIED CALIBRATION, NOT canonical. NOT LIVE-VERIFIED. OPTIONAL ONLY.
    -- One QuadPatch; cleanup cannot be skipped by a result/property formatting throw.
    local beforeCount = objects.count
    local beforeSelection = selection.count
    if beforeCount != 0 or beforeSelection != 0 do throw "P16P3E_REFUSE: expected empty unselected scene"
    if maxFilePath != "" or maxFileName != "" do throw "P16P3E_REFUSE: expected unnamed scene"
    if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "P16P3E_REFUSE: expected mm/1"
    local patchNode = undefined
    local workThrew = false
    local actualClass = undefined
    local actualSuperclass = undefined
    try
    (
        patchNode = QuadPatch name:"P16P3E_PATCH_6d04f9a2"
        actualClass = classOf patchNode
        actualSuperclass = superclassOf patchNode
    )
    catch (workThrew = true)
    -- CLEANUP FIRST, even when constructor result/property reads failed.
    local cleanupThrew = false
    local ownedAlive = false
    if patchNode != undefined do
    (
        try (if isValidNode patchNode do delete patchNode) catch (cleanupThrew = true)
        try (ownedAlive = isValidNode patchNode) catch (ownedAlive = true)
    )
    local censusOk = (objects.count == beforeCount) and (selection.count == beforeSelection)
    local out = "ERROR"
    if not workThrew and actualClass != undefined do out = "OK classOf=" + (actualClass as string) + " superclass=" + (actualSuperclass as string)
    out += " modifiedCalibration=true workThrew=" + (workThrew as string) + " cleanupThrew=" + (cleanupThrew as string) + " ownedAlive=" + (ownedAlive as string) + " censusOk=" + (censusOk as string)
    out
)
