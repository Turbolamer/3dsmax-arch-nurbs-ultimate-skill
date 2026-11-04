-- P16 OPTIONAL READ-LOCK API PROBE: UNEXECUTED. No file bytes are written.
(

    -- Definitions are inside this fileIn-loaded file, not a bridge fn call.
    fn p16ExpectedHash value =
    (
        if (classOf value) != String then return false
        if value.count != 64 then return false
        for i = 1 to value.count do
            if (findString "0123456789abcdef" (substring value i 1)) == undefined do return false
        true
    )
    fn p16Digest256 hasher stream =
    (
        stream.Position = 0
        local raw = hasher.ComputeHash stream
        local hex = ((dotNetClass "System.BitConverter").ToString raw) as string
        if stream.Position != stream.Length do throw "P16 incomplete full-stream SHA-256 read"
        toLower (substituteString hex "-" "")
    )
    fn p16CloseRead stream label =
    (
        local problem = undefined
        if stream != undefined do
        (
            try (stream.Close()) catch (problem = getCurrentException())
            if problem != undefined do
            (
                try (stream.Dispose(); problem = undefined)
                catch (problem = getCurrentException())
            )
            if problem == undefined do
            (
                try (if stream.CanRead do problem = "stream still reports CanRead=true")
                catch (problem = getCurrentException())
            )
        )
        if problem == undefined then undefined else (label + ": " + problem)
    )
    local path = "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-execution-2026-11-02e/control_pair.ms"
    local firstRead = undefined
    local compatibleRead = undefined
    local writeAttempt = undefined
    local afterClose = undefined
    local writePositive = undefined
    local failure = undefined
    local cleanupProblems = ""
    local deniedWriteMessage = undefined
    local compatibleReadPassed = false
    local firstClosed = false
    local compatibleClosed = false
    local reopened = false
    local writeOpenCalibrated = false
    try
    (
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        firstRead = dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.Read
        compatibleRead = dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.Read
        compatibleReadPassed = compatibleRead.CanRead
        -- Open an existing file only; do not call any write/resize operation.
        try (writeAttempt = dotNetObject "System.IO.FileStream" path mode.Open access.Write sharing.ReadWrite)
        catch (deniedWriteMessage = getCurrentException())
        if writeAttempt != undefined do throw "P16 probe FAIL: WRITE open unexpectedly succeeded"
        if deniedWriteMessage == undefined do throw "P16 probe FAIL: missing WRITE denial diagnostic"
    )
    catch (failure = getCurrentException())
    local extraCleanup = p16CloseRead writeAttempt "unexpected write handle close"
    local compatibleCleanup = p16CloseRead compatibleRead "compatible read close"
    local firstCleanup = p16CloseRead firstRead "first read close"
    if extraCleanup != undefined do cleanupProblems += (extraCleanup + " | ")
    if compatibleCleanup != undefined do cleanupProblems += (compatibleCleanup + " | ")
    if firstCleanup != undefined do cleanupProblems += (firstCleanup + " | ")
    if firstRead != undefined do try (firstClosed = not firstRead.CanRead) catch (failure = getCurrentException())
    if compatibleRead != undefined do try (compatibleClosed = not compatibleRead.CanRead) catch (failure = getCurrentException())
    -- Calibrate the EXACT attempted WRITE-open signature once held reads are closed.
    -- No write/resize is called; an earlier throw alone is not lock evidence.
    if failure == undefined and cleanupProblems == "" do
    (
        try
        (
            local mode = dotNetClass "System.IO.FileMode"
            local access = dotNetClass "System.IO.FileAccess"
            local sharing = dotNetClass "System.IO.FileShare"
            writePositive = dotNetObject "System.IO.FileStream" path mode.Open access.Write sharing.ReadWrite
            writeOpenCalibrated = writePositive.CanWrite
        )
        catch (failure = getCurrentException())
    )
    local writePositiveCleanup = p16CloseRead writePositive "calibrating write handle close"
    if writePositiveCleanup != undefined do cleanupProblems += (writePositiveCleanup + " | ")
    -- A plain sharing.Read reopen cannot prove closure (compatible reads coexist).
    -- CanRead=false observes closure; exclusive READ reopen also checks liveness.
    if failure == undefined and cleanupProblems == "" do
    (
        try
        (
            local mode = dotNetClass "System.IO.FileMode"
            local access = dotNetClass "System.IO.FileAccess"
            local sharing = dotNetClass "System.IO.FileShare"
            afterClose = dotNetObject "System.IO.FileStream" path mode.Open access.Read sharing.None
            reopened = afterClose.CanRead
        )
        catch (failure = getCurrentException())
    )
    local afterCleanup = p16CloseRead afterClose "liveness read close"
    if afterCleanup != undefined do cleanupProblems += (afterCleanup + " | ")
    if cleanupProblems != "" do
    (
        if failure == undefined then failure = cleanupProblems else failure += (" | " + cleanupProblems)
    )
    if failure != undefined do throw failure
    if not compatibleReadPassed or not firstClosed or not compatibleClosed or not writeOpenCalibrated or not reopened do throw "P16 probe FAIL: incomplete read/close/calibration/liveness observation"
    #("P16_LOCK_PROBE_OBSERVED", compatibleReadPassed, deniedWriteMessage, firstClosed, compatibleClosed, writeOpenCalibrated, reopened)
)
