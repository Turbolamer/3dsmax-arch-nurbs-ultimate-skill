(
    local out = "P3_MAIN03_AUTHENTIC_ATTEMPT"
    local registryKey = #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7
    local witness = undefined
    if objects.count != 0 or selection.count != 0 do throw "P3 Main03 requires fresh empty scene"
    if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "P3 Main03 native units drift"
    if maxFileName != "" or maxFilePath != "" do throw "P3 Main03 scene identity drift"
    if globalVars.isGlobal registryKey do throw "P3 Main03 arm key already occupied"
    try
    (
        witness = fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-main-build-2026-11-02e/Main03/main_only_arm.ms"
        if witness == undefined or (globalVars.get registryKey) != witness do throw "P3 Main03 external witness mismatch"
        out += "|armed=true"
        local result = fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-main-build-2026-11-02e/Main03/held_pair_filein.ms"
        out += "|fileInReturned=" + (result as string)
    )
    catch (out += "|EXCEPTION=" + (getCurrentException() as string))
    if witness != undefined do
    (
        try
        (
            out += "|leaseState=" + (witness.values[5] as string)
            out += "|witnessStill=" + (((globalVars.get registryKey) == witness) as string)
        )
        catch (out += "|witnessReadError=" + (getCurrentException() as string))
    )
    out += "|objectsAfter=" + (objects.count as string)
    -- Retain exact lease for diagnostics; no implicit recovery/re-arm/deletion.
    out
)
