-- MAIN-ONLY explicit one-use arm. No scene mutation; never auto-run on replay.
-- fileIn returns the exact array witness; retain it OUTSIDE the emitted wall file.
(
    local registryKey = "__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7" as name
    local identity = "318b9572f72e461b32a024fb2d00ea45ac7903a8b63be8b4fc0e60ae785c225c"
    local binding = "2dce49b0d0e7d4f028a64e5baadeff5bbc6a4c73b8a60ff44da009628290cff7"
    local ownerNamespace = "P3E_F01"
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
    local environment = #(#(rootNode, h, classOf rootNode), maxFilePath, maxFileName, currentTime as integer, #(), subObjectLevel)
    local P3LocalLease
    struct P3LocalLease (values = #())
    local witness = P3LocalLease values:#("p3-session-registry-2", identity, binding, ownerNamespace, "ARMED",
        "2cc48325a94733a678a270ce8bd6bca99f7928ed15aba8da", environment, undefined, undefined, getSaveRequired())
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
        if declaredHere do try (globalVars.remove registryKey) catch ()
        print ("P3_ARM_INCOMPLETE|" + (reason as string))
        throw
    )
    print ("P3_ARMED|" + identity)
    witness
)
