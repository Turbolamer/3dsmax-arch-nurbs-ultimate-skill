-- MAIN-ONLY explicit one-use arm. No scene mutation; never auto-run on replay.
    -- Retain this exact struct AND detached expected fields independently of the registry.
(
    local registryKey = "__P3W_9c1a6734f22c576288390eb4e4983f323fa02f87e74f250841599711ce936113" as name
    local identity = "67ad0526bf0336c790e359ec4d771867c63e47786ff7c6f0d3c71f2ed7df628f"
    local binding = "67970658c8759f6813ed9a5f8f98996bf32b088a44727bd59990f044f2ce75df"
    local ownerNamespace = "P3A_F01"
    if globalVars.isGlobal registryKey do throw "P3_ARM_REFUSE|reserved global exists; never replace"
    local actualScale = units.SystemScale as double
    if units.SystemType != #millimeters or actualScale != 1.0d0 do throw "P3_ARM_REFUSE|unit pair mismatch"
    if not (actualScale > 0.0d0 and actualScale < 1.0d300 and actualScale == actualScale) do throw "P3_ARM_REFUSE|invalid unit scale"
    local c = 0.1d0 * actualScale
    local f = 1.0d0 / c
    if c != 0.1d0 or f != 10.0d0 do throw "P3_ARM_REFUSE|unit factors mismatch"
    if objects.count != 0 or selection.count != 0 do throw "P3_ARM_REFUSE|requires explicitly inspected empty scene"
    if maxFilePath != "" or maxFileName != "" do throw "P3_ARM_REFUSE|saved/loaded scene unsupported"
    local h = getHandleByAnim rootNode
    if h == undefined or (getAnimByHandle h) != rootNode do throw "P3_ARM_REFUSE|root reference not comparable"
    local environment = #(#(rootNode, h, classOf rootNode), (copy maxFilePath), (copy maxFileName), currentTime as integer, #(), subObjectLevel)
    local P3LocalLease
    struct P3LocalLease (values = #())
    local witness = P3LocalLease values:#("p3-session-registry-2", (copy identity), (copy binding), (copy ownerNamespace), "ARMED",
        (copy "FreshNonce20261104AuthenticF01_a987"), environment, undefined, undefined, getSaveRequired())
    -- globalVars.set does not declare new names (measured by main).
    -- registryKey is generated hex/ASCII, never caller-provided executable text.
    local declaredHere = false
    try
    (
        execute ("global " + (registryKey as string))
        declaredHere = true
        globalVars.set registryKey witness
        if (globalVars.get registryKey) != witness do throw "P3_ARM_INCOMPLETE|exact registry publication unavailable"
    )
    catch
    (
        local reason = getCurrentException()
        local cleanupStatus = "UNKNOWN"
        local cleanupError = ""
        try
        (
            if not (globalVars.isGlobal registryKey) then cleanupStatus = "ABSENT_ON_READBACK"
            else if declaredHere and (globalVars.get registryKey) == witness then
            (
                witness.values[5] = "POISONED"
                cleanupStatus = "POISONED_RETAINED_FOR_FORENSICS"
            )
            else cleanupStatus = "RETAINED_UNPROVEN_OR_REPLACED_GLOBAL"
        )
        catch
        (
            cleanupStatus = "REMOVAL_OR_READBACK_UNKNOWN"
            cleanupError = getCurrentException() as string
        )
        print ("P3_ARM_INCOMPLETE|key=" + (registryKey as string) + "|cleanup=" + cleanupStatus + "|cleanupError=" + cleanupError + "|original=" + (reason as string))
        throw
    )
    print ("P3_ARMED|" + identity)
    witness
)
