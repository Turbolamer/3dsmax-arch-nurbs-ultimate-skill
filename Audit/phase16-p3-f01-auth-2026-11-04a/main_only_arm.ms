-- MAIN-ONLY explicit one-use arm. No scene mutation; never auto-run on replay.
    -- Retain this exact struct AND detached expected fields independently of the registry.
(
    local registryKey = "__P3W_3175eb207d5faccb833ac364c3cd1e1eed699a0d60155752fd5fde2dfeddf641" as name
    local identity = "5805cec304792f3f9f457e553cf82d2fcffc9bf07d876e804144e5cf4449c320"
    local binding = "844a500e4bbaf0634c4bb830391c6dfe5fea3a6638da604adf077b47a39165a6"
    local ownerNamespace = "P3_F01_AUTH"
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
        (copy "FreshNonce20261104AuthenticF01_b123"), environment, undefined, undefined, getSaveRequired())
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
