-- P16 OFFLINE-GENERATED: enum/hash/fileIn sharing needs main's live probe.
-- Ordinary local files only; no named pipes, no parent immutability claim.
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
    local manifestPath = "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-main-build-2026-11-02e/Main01/published/wall_surface.json"
    local scriptPath = "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-main-build-2026-11-02e/Main01/published/wall_surface.ms"
    local expectedManifest = "71c71bb66eb4f887863bc29b5e718340c22cb163fcb176d5c5299f6b9b0278f4"
    local expectedScript = "9df84585dadc25ba4e76e2d756cae8fee2714555f0e0f72d1f1643804fd9b37b"
    local manifestRead = undefined
    local scriptRead = undefined
    local hasher = undefined
    local result = undefined
    local failure = undefined
    local cleanupProblems = ""
    try
    (
        if not (p16ExpectedHash expectedManifest) do throw "P16 malformed manifest SHA-256; fileIn refused"
        if not (p16ExpectedHash expectedScript) do throw "P16 malformed script SHA-256; fileIn refused"
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        -- Both opens are ordinary FileMode.Open/FileAccess.Read/FileShare.Read.
        -- Enum overload syntax and fileIn's sharing are UNVERIFIED until probed.
        manifestRead = dotNetObject "System.IO.FileStream" manifestPath mode.Open access.Read sharing.Read
        scriptRead = dotNetObject "System.IO.FileStream" scriptPath mode.Open access.Read sharing.Read
        if (manifestRead.Length + scriptRead.Length) > 2097152 do throw "P16 pair exceeds 2 MiB; fileIn refused"
        hasher = (dotNetClass "System.Security.Cryptography.SHA256").Create()
        local actualManifest = p16Digest256 hasher manifestRead
        local actualScript = p16Digest256 hasher scriptRead
        if actualManifest != expectedManifest do throw ("P16 manifest SHA-256 mismatch; fileIn refused; actual=" + actualManifest)
        if actualScript != expectedScript do throw ("P16 script SHA-256 mismatch; fileIn refused; actual=" + actualScript)
        -- Do not close/reopen either held stream before the delegated script ends.
        -- The delegated AUTHENTIC script is the only possible scene mutator here.
        result = fileIn scriptPath quiet:true
    )
    catch (failure = getCurrentException())

    -- No finally construct assumed: both closes attempted after any caught error.
    local scriptCleanup = p16CloseRead scriptRead "script close"
    local manifestCleanup = p16CloseRead manifestRead "manifest close"
    if scriptCleanup != undefined do cleanupProblems += (scriptCleanup + " | ")
    if manifestCleanup != undefined do cleanupProblems += (manifestCleanup + " | ")
    if hasher != undefined do
    (
        try (hasher.Dispose())
        catch (cleanupProblems += ("SHA256 dispose: " + (getCurrentException()) + " | "))
    )
    if cleanupProblems != "" do
    (
        if failure == undefined then failure = ("P16 cleanup failure: " + cleanupProblems)
        else failure += (" | P16 cleanup failure: " + cleanupProblems)
    )
    -- Return the actual fileIn value, NOT a synthetic OK envelope.
    -- Re-throw captured original exception text after cleanup, never convert to OK.
    if failure != undefined do throw failure
    result
)
