(
    -- MODIFIED CALIBRATION, NOT canonical. NOT LIVE-VERIFIED. OPTIONAL ONLY.
    -- Existing accepted Loft API facts do not require routine repetition for P3.
    -- If unexpected construction returns a node, cleanup uses that exact local ref.
    local beforeCount = objects.count
    local beforeSelection = selection.count
    if beforeCount != 0 or beforeSelection != 0 do throw "P16P3E_REFUSE: expected empty unselected scene"
    if maxFilePath != "" or maxFileName != "" do throw "P16P3E_REFUSE: expected unnamed scene"
    if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "P16P3E_REFUSE: expected mm/1"
    local hit = undefined
    local hitThrew = false
    try (hit = execute "1+1") catch (hitThrew = true)
    local bogus = undefined
    local bogusThrew = false
    try (bogus = execute "TotalGarbageXYZ123") catch (bogusThrew = true)
    local controlsOk = (not hitThrew) and (hit == 2) and (bogus == undefined)
    if not controlsOk do throw "P16P3E_REFUSE: uncalibrated resolution probe"
    local id = undefined
    local resolveThrew = false
    try (id = execute "Loft") catch (resolveThrew = true)
    local resolved = (id != undefined)
    local threw = false
    local candidate = undefined
    local created = false
    if resolved do
    (
        try (candidate = id(); created = (candidate != undefined)) catch (threw = true)
    )
    -- CLEANUP FIRST: never lookup/delete by a name or prefix.
    local cleanupThrew = false
    local ownedAlive = false
    if candidate != undefined do
    (
        try (if isValidNode candidate do delete candidate) catch (cleanupThrew = true)
        try (ownedAlive = isValidNode candidate) catch (ownedAlive = true)
    )
    local censusOk = (objects.count == beforeCount) and (selection.count == beforeSelection)
    local out = "resolved=" + (resolved as string)
    if threw then out += " THROWS" else out += " NOTHROW"
    out += " created=" + (created as string)
    out += " modifiedCalibration=true controlsOk=" + (controlsOk as string) + " hitThrew=" + (hitThrew as string) + " bogusThrew=" + (bogusThrew as string) + " bogusUndefined=" + ((bogus == undefined) as string) + " resolveThrew=" + (resolveThrew as string)
    out += " cleanupThrew=" + (cleanupThrew as string) + " ownedAlive=" + (ownedAlive as string) + " censusOk=" + (censusOk as string)
    out
)
