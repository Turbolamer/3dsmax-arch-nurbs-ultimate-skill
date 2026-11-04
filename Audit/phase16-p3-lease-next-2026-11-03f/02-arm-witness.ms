-- DISABLED TEMPLATE / NOT LIVE-EXECUTED / NOT AN AUTHORIZATION.
-- Main must independently review a new concrete copy; see README. This file
-- itself always throws before file access, global declaration or arm fileIn.
(
    throw "P16_TEMPLATE_DISABLED: review blockers and adapt a NEW private file"

    -- Candidate follows the deliberate stop. All @@...@@ tokens are invalid
    -- until replaced in a new copy. Names/hashes/paths must be validated by
    -- main before substitution, not evaluated as arbitrary source text.
    local registryKey = "@@REGISTRY_KEY@@" as name
    local witnessKey = "@@WITNESS_KEY@@" as name
    local anchorKey = "@@ANCHOR_KEY@@" as name
    -- A detached copy is a candidate only; live in-place alias calibration is
    -- required before reliance on these mutable MAXScript String values.
    local expectedIdentity = copy "@@IDENTITY@@"
    local expectedBinding = copy "@@BINDING@@"
    local expectedNamespace = copy "@@NAMESPACE@@"
    local expectedNonce = copy "@@NONCE@@"
    local armPath = "@@ARM_PATH@@"
    local expectedArmHash = "@@ARM_SHA256@@"
    local expectedDirty = @@INITIAL_DIRTY@@
    local expectedTime = @@INITIAL_TIME_INTEGER@@
    local expectedSub = @@INITIAL_SUBOBJECT_LEVEL@@

    local P16MainWitnessType
    struct P16MainWitnessType (anchorRef, leaseRef, valuesRef, envRef, rootRecordRef, selectionRef, rootRef, rootHandle, rootClass,
        pathValue, fileValue, timeValue, subValue, initialDirty)
    local P16MainAnchorType
    struct P16MainAnchorType (witnessRef, leaseRef, valuesRef, envRef, rootRecordRef, selectionRef, rootRef)

    local armRead = undefined
    local hasher = undefined
    local failure = undefined
    local cleanupProblem = ""
    local armStarted = false
    local heldLease = undefined
    local heldValues = undefined
    local heldEnv = undefined
    local heldRootRecord = undefined
    local heldSelection = undefined
    local heldWitness = undefined
    local heldAnchor = undefined
    try
    (
        if (globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7) do throw "P16_REFUSED|historical Main03 key unexpectedly present; preserve it"
        if registryKey == witnessKey or registryKey == anchorKey or witnessKey == anchorKey do throw "P16_REFUSED|reserved names collide"
        if (globalVars.isGlobal registryKey) or (globalVars.isGlobal witnessKey) or (globalVars.isGlobal anchorKey) do throw "P16_REFUSED|reserved name occupied"
        if objects.count != 0 or selection.count != 0 do throw "P16_REFUSED|not an empty controlled scene"
        if maxFilePath != "" or maxFileName != "" do throw "P16_REFUSED|scene not unnamed"
        if units.SystemType != #millimeters or (units.SystemScale as double) != 1.0d0 do throw "P16_REFUSED|native unit pair changed"
        if (getSaveRequired()) != expectedDirty or (currentTime as integer) != expectedTime or subObjectLevel != expectedSub do throw "P16_REFUSED|scene context changed"
        local savedRoot = rootNode
        local savedHandle = getHandleByAnim savedRoot
        if savedHandle == undefined or (getAnimByHandle savedHandle) != savedRoot do throw "P16_REFUSED|root identity unsupported"
        local savedClass = classOf savedRoot
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        armRead = dotNetObject "System.IO.FileStream" armPath mode.Open access.Read sharing.Read
        if armRead.Length > 2097152 do throw "P16_REFUSED|arm too large"
        hasher = (dotNetClass "System.Security.Cryptography.SHA256").Create()
        armRead.Position = 0
        local raw = hasher.ComputeHash armRead
        if armRead.Position != armRead.Length do throw "P16_REFUSED|incomplete arm hash"
        local actualHash = toLower (substituteString (((dotNetClass "System.BitConverter").ToString raw) as string) "-" "")
        if actualHash != expectedArmHash do throw "P16_REFUSED|arm hash mismatch"
        -- Recheck immediately before arm. Never make an arm call on a precheck fault.
        if (globalVars.isGlobal registryKey) or (globalVars.isGlobal witnessKey) or (globalVars.isGlobal anchorKey) do throw "P16_REFUSED|late reserved name collision"
        if rootNode != savedRoot or (getAnimByHandle savedHandle) != savedRoot or (classOf rootNode) != savedClass do throw "P16_REFUSED|late root drift"
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "P16_REFUSED|late scene drift"
        if units.SystemType != #millimeters or (units.SystemScale as double) != 1.0d0 or (getSaveRequired()) != expectedDirty or (currentTime as integer) != expectedTime or subObjectLevel != expectedSub do throw "P16_REFUSED|late context drift"
        armStarted = true
        heldLease = fileIn armPath quiet:true
        -- heldLease is the actual arm return, NOT a registry reacquisition.
        if heldLease == undefined or not (isProperty heldLease #values) do throw "P16_INCOMPLETE|arm returned no structured witness"
        heldValues = heldLease.values
        if (classOf heldValues) != Array or heldValues.count != 10 do throw "P16_INCOMPLETE|lease shape"
        if heldValues[1] != "p3-session-registry-2" or heldValues[2] != expectedIdentity or heldValues[3] != expectedBinding or heldValues[4] != expectedNamespace do throw "P16_INCOMPLETE|lease identity"
        if heldValues[5] != "ARMED" or heldValues[6] != expectedNonce or heldValues[8] != undefined or heldValues[9] != undefined or heldValues[10] != expectedDirty do throw "P16_INCOMPLETE|lease state/nonce/dirty"
        heldEnv = heldValues[7]
        if (classOf heldEnv) != Array or heldEnv.count != 6 do throw "P16_INCOMPLETE|lease environment shape"
        heldRootRecord = heldEnv[1]
        heldSelection = heldEnv[5]
        if (classOf heldRootRecord) != Array or heldRootRecord.count != 3 or (classOf heldSelection) != Array or heldSelection.count != 0 do throw "P16_INCOMPLETE|lease environment record shape"
        if heldRootRecord[1] != savedRoot or heldRootRecord[2] != savedHandle or heldRootRecord[3] != savedClass or heldEnv[2] != "" or heldEnv[3] != "" or heldEnv[4] != expectedTime or heldEnv[6] != expectedSub do throw "P16_INCOMPLETE|lease environment mismatch"
        if not (globalVars.isGlobal registryKey) or (globalVars.get registryKey) != heldLease do throw "P16_INCOMPLETE|arm registry differs from returned witness"
        if rootNode != savedRoot or (getAnimByHandle savedHandle) != savedRoot or (classOf rootNode) != savedClass do throw "P16_INCOMPLETE|arm changed root"
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "P16_INCOMPLETE|arm changed scene"
        if units.SystemType != #millimeters or (units.SystemScale as double) != 1.0d0 or (getSaveRequired()) != expectedDirty or (currentTime as integer) != expectedTime or subObjectLevel != expectedSub do throw "P16_INCOMPLETE|arm changed context"
        -- No registry-derived reassignment of heldLease/heldValues follows.
        heldWitness = P16MainWitnessType leaseRef:heldLease valuesRef:heldValues envRef:heldEnv rootRecordRef:heldRootRecord selectionRef:heldSelection rootRef:savedRoot rootHandle:savedHandle rootClass:savedClass pathValue:(copy maxFilePath) fileValue:(copy maxFileName) timeValue:expectedTime subValue:expectedSub initialDirty:expectedDirty
        heldAnchor = P16MainAnchorType witnessRef:heldWitness leaseRef:heldLease valuesRef:heldValues envRef:heldEnv rootRecordRef:heldRootRecord selectionRef:heldSelection rootRef:savedRoot
        heldWitness.anchorRef = heldAnchor
        if (globalVars.isGlobal witnessKey) or (globalVars.isGlobal anchorKey) do throw "P16_INCOMPLETE|late main witness name collision"
        execute ("global " + (witnessKey as string))
        globalVars.set witnessKey heldWitness
        if (globalVars.get witnessKey) != heldWitness do throw "P16_INCOMPLETE|main witness publication"
        execute ("global " + (anchorKey as string))
        globalVars.set anchorKey heldAnchor
        if (globalVars.get anchorKey) != heldAnchor or (globalVars.get witnessKey) != heldWitness do throw "P16_INCOMPLETE|main witness anchor publication"
        if heldAnchor.witnessRef != heldWitness or heldWitness.anchorRef != heldAnchor or heldAnchor.leaseRef != heldLease or heldAnchor.valuesRef != heldValues or heldAnchor.envRef != heldEnv or heldAnchor.rootRecordRef != heldRootRecord or heldAnchor.selectionRef != heldSelection or heldAnchor.rootRef != savedRoot do throw "P16_INCOMPLETE|anchor wiring drift"
        if (globalVars.get registryKey) != heldLease or heldLease.values != heldValues or heldValues[7] != heldEnv or heldEnv[1] != heldRootRecord or heldEnv[5] != heldSelection do throw "P16_INCOMPLETE|lease publication drift"
    )
    catch (failure = getCurrentException())

    if armRead != undefined do
    (
        try (armRead.Close()) catch (cleanupProblem += ("arm close: " + (getCurrentException() as string) + " | "))
        try (armRead.Dispose()) catch (cleanupProblem += ("arm dispose: " + (getCurrentException() as string) + " | "))
        try (if armRead.CanRead do cleanupProblem += "arm remains readable | ") catch (cleanupProblem += ("arm readback: " + (getCurrentException() as string) + " | "))
    )
    if hasher != undefined do try (hasher.Dispose()) catch (cleanupProblem += ("hash dispose: " + (getCurrentException() as string) + " | "))
    if cleanupProblem != "" do print ("P16_INCOMPLETE|arm resource cleanup|" + cleanupProblem)
    if failure != undefined do print ("P16_INCOMPLETE|armStarted=" + (armStarted as string) + "|" + (failure as string))
    if failure != undefined or cleanupProblem != "" do throw "P16_INCOMPLETE|stop, preserve globals and inspect only"
    -- This is merely publication of a candidate witness, not a wall/QA PASS.
    "P16_WITNESS_PUBLISHED_UNVERIFIED"
)
