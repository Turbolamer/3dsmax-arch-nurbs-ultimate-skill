-- DISABLED INITIAL-ONLY TEMPLATE / NOT LIVE-EXECUTED / NOT AUTHORIZATION.
-- Main must separately authenticate THIS wrapper, the pair, and all literals.
-- It is deliberately disabled before any file access or wall fileIn.
(
    throw "P16_TEMPLATE_DISABLED: review blockers and adapt a NEW private file"

    local registryKey = "@@REGISTRY_KEY@@" as name
    local witnessKey = "@@WITNESS_KEY@@" as name
    local anchorKey = "@@ANCHOR_KEY@@" as name
    -- Candidate detached literals; require in-place copy/alias calibration.
    local expectedIdentity = copy "@@IDENTITY@@"
    local expectedBinding = copy "@@BINDING@@"
    local expectedNamespace = copy "@@NAMESPACE@@"
    local expectedNonce = copy "@@NONCE@@"
    local manifestPath = "@@MANIFEST_PATH@@"
    local scriptPath = "@@SCRIPT_PATH@@"
    local expectedManifestHash = "@@MANIFEST_SHA256@@"
    local expectedScriptHash = "@@SCRIPT_SHA256@@"
    local expectedDirty = @@INITIAL_DIRTY@@
    local expectedTime = @@INITIAL_TIME_INTEGER@@
    local expectedSub = @@INITIAL_SUBOBJECT_LEVEL@@
    -- Must be decided independently from the repaired generator's contract;
    -- current COMMITTED is NOT accepted as complete replay proof.
    local expectedProvisionalState = "@@REVIEWED_POST_PROVISIONAL_STATE@@"
    local expectedPostDirty = @@REVIEWED_POST_DIRTY@@

    -- Local helpers only: no bridge top-level fn declarations. Before use main
    -- must calibrate their Max syntax and behavior using disposable controls.
    fn p16PreGuard regKey witnessName anchorName identity binding ns nonce dirty tm sub =
    (
        if (globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7) do throw "P16_REFUSED|historical Main03 key present"
        if regKey == witnessName or regKey == anchorName or witnessName == anchorName do throw "P16_REFUSED|reserved names collide"
        if not (globalVars.isGlobal witnessName) or not (globalVars.isGlobal anchorName) do throw "P16_REFUSED|main witness or anchor missing"
        local w = globalVars.get witnessName
        local anchor = globalVars.get anchorName
        if w == undefined or anchor == undefined do throw "P16_REFUSED|main witness or anchor undefined"
        if not (isProperty w #anchorRef) or not (isProperty w #leaseRef) or not (isProperty w #valuesRef) or not (isProperty w #envRef) or not (isProperty w #rootRecordRef) or not (isProperty w #selectionRef) or not (isProperty w #rootRef) or not (isProperty w #rootHandle) or not (isProperty w #rootClass) or not (isProperty w #pathValue) or not (isProperty w #fileValue) or not (isProperty w #timeValue) or not (isProperty w #subValue) or not (isProperty w #initialDirty) do throw "P16_REFUSED|main witness shape"
        if not (isProperty anchor #witnessRef) or not (isProperty anchor #leaseRef) or not (isProperty anchor #valuesRef) or not (isProperty anchor #envRef) or not (isProperty anchor #rootRecordRef) or not (isProperty anchor #selectionRef) or not (isProperty anchor #rootRef) do throw "P16_REFUSED|anchor shape"
        if w.anchorRef != anchor or anchor.witnessRef != w do throw "P16_REFUSED|main witness or anchor replaced"
        if not (globalVars.isGlobal regKey) do throw "P16_REFUSED|registry missing"
        local lease = w.leaseRef
        local vals = w.valuesRef
        if lease == undefined or anchor.leaseRef != lease or (globalVars.get regKey) != lease do throw "P16_REFUSED|original lease mismatch"
        if not (isProperty lease #values) or anchor.valuesRef != vals or lease.values != vals do throw "P16_REFUSED|original values array mismatch"
        if anchor.rootRef != w.rootRef do throw "P16_REFUSED|original root anchor mismatch"
        if (classOf vals) != Array or vals.count != 10 do throw "P16_REFUSED|lease shape"
        if vals[1] != "p3-session-registry-2" or vals[2] != identity or vals[3] != binding or vals[4] != ns do throw "P16_REFUSED|identity or binding drift"
        if vals[5] != "ARMED" or vals[6] != nonce or vals[8] != undefined or vals[9] != undefined or vals[10] != dirty do throw "P16_REFUSED|state nonce or dirty drift"
        local env = vals[7]
        if env != w.envRef or env != anchor.envRef do throw "P16_REFUSED|original environment array mismatch"
        if (classOf env) != Array or env.count != 6 do throw "P16_REFUSED|lease environment shape"
        local rootRecord = env[1]
        if rootRecord != w.rootRecordRef or rootRecord != anchor.rootRecordRef or env[5] != w.selectionRef or env[5] != anchor.selectionRef do throw "P16_REFUSED|original environment component mismatch"
        if (classOf rootRecord) != Array or rootRecord.count != 3 do throw "P16_REFUSED|lease root record shape"
        if rootRecord[1] != w.rootRef or rootRecord[2] != w.rootHandle or rootRecord[3] != w.rootClass do throw "P16_REFUSED|lease root record drift"
        if env[2] != w.pathValue or env[3] != w.fileValue or env[4] != tm or env[6] != sub do throw "P16_REFUSED|lease context record drift"
        if (classOf env[5]) != Array or env[5].count != 0 do throw "P16_REFUSED|lease selection record drift"
        if w.pathValue != "" or w.fileValue != "" or w.timeValue != tm or w.subValue != sub or w.initialDirty != dirty do throw "P16_REFUSED|main witness context drift"
        if rootNode != w.rootRef or (classOf rootNode) != w.rootClass or (getHandleByAnim rootNode) != w.rootHandle or (getAnimByHandle w.rootHandle) != w.rootRef do throw "P16_REFUSED|current root mismatch"
        if maxFilePath != w.pathValue or maxFileName != w.fileValue or (currentTime as integer) != tm or subObjectLevel != sub do throw "P16_REFUSED|current scene context mismatch"
        if objects.count != 0 or selection.count != 0 or (getSaveRequired()) != dirty do throw "P16_REFUSED|current census selection or dirty changed"
        if units.SystemType != #millimeters or (units.SystemScale as double) != 1.0d0 do throw "P16_REFUSED|native units mismatch"
        -- Return exact local references; none are reacquired from registry.
        #(w, anchor, lease, vals, rootNode, w.rootHandle, w.rootClass)
    )
    fn p16Digest hasher stream =
    (
        stream.Position = 0
        local raw = hasher.ComputeHash stream
        if stream.Position != stream.Length do throw "P16_REFUSED|incomplete full-stream hash"
        toLower (substituteString (((dotNetClass "System.BitConverter").ToString raw) as string) "-" "")
    )
    local manifestRead = undefined
    local scriptRead = undefined
    local hasher = undefined
    local failure = undefined
    local postFailure = undefined
    local cleanupProblem = ""
    local delegated = false
    local retained = undefined
    local result = undefined
    try
    (
        if expectedProvisionalState == "" or expectedProvisionalState == "ARMED" or expectedProvisionalState == "BUILDING" or expectedProvisionalState == "COMMITTED" or expectedProvisionalState == "POISONED" or expectedProvisionalState == "@@REVIEWED_POST_PROVISIONAL_STATE@@" do throw "P16_REFUSED|provisional state contract not independently decided"
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        manifestRead = dotNetObject "System.IO.FileStream" manifestPath mode.Open access.Read sharing.Read
        scriptRead = dotNetObject "System.IO.FileStream" scriptPath mode.Open access.Read sharing.Read
        if (manifestRead.Length + scriptRead.Length) > 2097152 do throw "P16_REFUSED|pair exceeds 2 MiB"
        hasher = (dotNetClass "System.Security.Cryptography.SHA256").Create()
        if (p16Digest hasher manifestRead) != expectedManifestHash do throw "P16_REFUSED|manifest hash mismatch"
        if (p16Digest hasher scriptRead) != expectedScriptHash do throw "P16_REFUSED|script hash mismatch"
        -- Last gate in the SAME call, after both full byte hashes and directly
        -- before delegation. This guard itself must have been hash-verified.
        retained = p16PreGuard registryKey witnessKey anchorKey expectedIdentity expectedBinding expectedNamespace expectedNonce expectedDirty expectedTime expectedSub
        delegated = true
        result = fileIn scriptPath quiet:true
    )
    catch (failure = getCurrentException())

    -- Any return/throw after delegate start needs independent post-inspection.
    -- This checks continuity/immutable fields, not whether the wall is safe.
    if delegated do
    (
        try
        (
            local w = retained[1]
            local anchor = retained[2]
            local lease = retained[3]
            local vals = retained[4]
            local savedRoot = retained[5]
            local savedRootHandle = retained[6]
            local savedRootClass = retained[7]
            if (globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7) do throw "post historical Main03 key unexpectedly present"
            if not (globalVars.isGlobal witnessKey) or not (globalVars.isGlobal anchorKey) or not (globalVars.isGlobal registryKey) do throw "post missing global"
            if (globalVars.get witnessKey) != w or (globalVars.get anchorKey) != anchor or w.anchorRef != anchor or anchor.witnessRef != w do throw "post witness/anchor replacement"
            if (globalVars.get registryKey) != lease or w.leaseRef != lease or anchor.leaseRef != lease or w.valuesRef != vals or anchor.valuesRef != vals or lease.values != vals do throw "post lease/values replacement"
            if (classOf vals) != Array or vals.count != 10 do throw "post lease shape"
            if vals[1] != "p3-session-registry-2" or vals[2] != expectedIdentity or vals[3] != expectedBinding or vals[4] != expectedNamespace or vals[6] != expectedNonce do throw "post immutable lease field changed"
            local env = vals[7]
            if env != w.envRef or env != anchor.envRef or (classOf env) != Array or env.count != 6 do throw "post environment array changed"
            local rootRecord = env[1]
            if rootRecord != w.rootRecordRef or rootRecord != anchor.rootRecordRef or (classOf rootRecord) != Array or rootRecord.count != 3 do throw "post root record changed"
            if rootRecord[1] != savedRoot or rootRecord[2] != savedRootHandle or rootRecord[3] != savedRootClass do throw "post root record contents changed"
            if w.rootHandle != savedRootHandle or w.rootClass != savedRootClass do throw "post witness root fields changed"
            if env[2] != "" or env[3] != "" or w.pathValue != "" or w.fileValue != "" or env[4] != expectedTime or env[6] != expectedSub or w.timeValue != expectedTime or w.subValue != expectedSub or w.initialDirty != expectedDirty do throw "post environment contents changed"
            if env[5] != w.selectionRef or env[5] != anchor.selectionRef or (classOf env[5]) != Array or env[5].count != 0 do throw "post selection record changed"
            if rootNode != savedRoot or w.rootRef != savedRoot or anchor.rootRef != savedRoot or (classOf rootNode) != savedRootClass or (getHandleByAnim rootNode) != savedRootHandle or (getAnimByHandle savedRootHandle) != savedRoot do throw "post root mismatch"
            if maxFilePath != w.pathValue or maxFileName != w.fileValue or (currentTime as integer) != expectedTime or subObjectLevel != expectedSub or selection.count != 0 do throw "post protected scene context drift"
            if units.SystemType != #millimeters or (units.SystemScale as double) != 1.0d0 do throw "post unit drift"
            -- Initial creation only: a future repaired contract must define
            -- the provisional state and exact node field before adaptation.
            -- A matching label is not baseline/geometry/replay acceptance.
            if vals[5] != expectedProvisionalState do throw "post unauthorized state transition"
            if (getSaveRequired()) != expectedPostDirty or vals[10] != expectedPostDirty do throw "post dirty state mismatch"
            local postNode = vals[8]
            if postNode == undefined or not (isValidNode postNode) do throw "post exact node unavailable"
            local postObjects = objects as array
            if postObjects.count != 1 or postObjects[1] != postNode do throw "post exact census mismatch"
            local postHandle = getHandleByAnim postNode
            if postHandle == undefined or (getAnimByHandle postHandle) != postNode do throw "post node handle mismatch"
        )
        catch (postFailure = getCurrentException())
    )
    if scriptRead != undefined do
    (
        try (scriptRead.Close()) catch (cleanupProblem += ("script close: " + (getCurrentException() as string) + " | "))
        try (scriptRead.Dispose()) catch (cleanupProblem += ("script dispose: " + (getCurrentException() as string) + " | "))
        try (if scriptRead.CanRead do cleanupProblem += "script remains readable | ") catch (cleanupProblem += ("script readback: " + (getCurrentException() as string) + " | "))
    )
    if manifestRead != undefined do
    (
        try (manifestRead.Close()) catch (cleanupProblem += ("manifest close: " + (getCurrentException() as string) + " | "))
        try (manifestRead.Dispose()) catch (cleanupProblem += ("manifest dispose: " + (getCurrentException() as string) + " | "))
        try (if manifestRead.CanRead do cleanupProblem += "manifest remains readable | ") catch (cleanupProblem += ("manifest readback: " + (getCurrentException() as string) + " | "))
    )
    if hasher != undefined do try (hasher.Dispose()) catch (cleanupProblem += ("hasher dispose: " + (getCurrentException() as string) + " | "))
    if failure != undefined do print ("P16_DELEGATE_OR_GUARD_ERROR|delegated=" + (delegated as string) + "|" + (failure as string))
    if postFailure != undefined do print ("P16_POST_CHECK_ERROR|" + (postFailure as string))
    if cleanupProblem != "" do print ("P16_RESOURCE_ERROR|" + cleanupProblem)
    if failure != undefined or postFailure != undefined or cleanupProblem != "" do throw "P16_INCOMPLETE|stop and inspect only"
    -- Never infer NOOP, complete state, safe cleanup, or acceptance here.
    result
)
