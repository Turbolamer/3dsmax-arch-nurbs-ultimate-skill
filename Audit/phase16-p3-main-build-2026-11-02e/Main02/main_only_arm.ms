-- MAIN-ONLY explicit one-use arm. No scene mutation; never auto-run on replay.
-- fileIn returns the exact array witness; retain it OUTSIDE the emitted wall file.
(
    local registryKey = "__P3W_2c7cdd5ecb8f9046ded01f94d84fa5bfae1043af08c3b432983606723c27a1dc" as name
    local identity = "251506d6a0bed86ad861c10bb79aadfbcbce4c02bb88fd77f74d72200ef8544f"
    local binding = "4a4c5e8942f5852a94cffb2ec3712c04f436d33439d06b8a6d757faefc6ca7f4"
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
        "d2bd1e88567ad434253f671ed52fabe36597f47b330266e1", environment, undefined, undefined, getSaveRequired())
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
        throw ("P3_ARM_INCOMPLETE|" + (reason as string))
    )
    print ("P3_ARMED|" + identity)
    witness
)
