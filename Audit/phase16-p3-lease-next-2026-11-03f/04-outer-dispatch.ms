-- DISABLED TEMPLATE, NOT LIVE-EXECUTED. Main's exact independently reviewed
-- inline MCP request is the trust anchor, not another recursively held file.
-- It holds and hashes EITHER the approved arm-witness wrapper OR the approved
-- wall-guard wrapper before fileIn. No functions or global writes here.
(
    throw "P16_TEMPLATE_DISABLED: main must review a NEW inline request"
    local wrapperPath = "@@ABSOLUTE_PRIVATE_WRAPPER_PATH@@"
    local expectedHash = "@@REVIEWED_WRAPPER_SHA256@@"
    local wrapperRead = undefined
    local hasher = undefined
    local failure = undefined
    local cleanupProblem = ""
    local delegated = false
    local result = undefined
    try
    (
        if expectedHash.count != 64 do throw "P16_REFUSED|wrapper hash length"
        for i = 1 to expectedHash.count do
            if (findString "0123456789abcdef" (substring expectedHash i 1)) == undefined do throw "P16_REFUSED|wrapper hash format"
        local mode = dotNetClass "System.IO.FileMode"
        local access = dotNetClass "System.IO.FileAccess"
        local sharing = dotNetClass "System.IO.FileShare"
        wrapperRead = dotNetObject "System.IO.FileStream" wrapperPath mode.Open access.Read sharing.Read
        if wrapperRead.Length > 2097152 do throw "P16_REFUSED|wrapper too large"
        hasher = (dotNetClass "System.Security.Cryptography.SHA256").Create()
        wrapperRead.Position = 0
        local raw = hasher.ComputeHash wrapperRead
        if wrapperRead.Position != wrapperRead.Length do throw "P16_REFUSED|incomplete wrapper read"
        local actual = toLower (substituteString (((dotNetClass "System.BitConverter").ToString raw) as string) "-" "")
        if actual != expectedHash do throw "P16_REFUSED|wrapper hash mismatch"
        delegated = true
        result = fileIn wrapperPath quiet:true
    )
    catch (failure = getCurrentException())
    if wrapperRead != undefined do
    (
        try (wrapperRead.Close()) catch (cleanupProblem += ("wrapper close: " + (getCurrentException() as string) + " | "))
        try (wrapperRead.Dispose()) catch (cleanupProblem += ("wrapper dispose: " + (getCurrentException() as string) + " | "))
        try (if wrapperRead.CanRead do cleanupProblem += "wrapper remains readable | ") catch (cleanupProblem += ("wrapper readback: " + (getCurrentException() as string) + " | "))
    )
    if hasher != undefined do try (hasher.Dispose()) catch (cleanupProblem += ("hasher dispose: " + (getCurrentException() as string) + " | "))
    if failure != undefined do print ("P16_DISPATCH_ERROR|wrapperStarted=" + (delegated as string) + "|" + (failure as string))
    if cleanupProblem != "" do print ("P16_DISPATCH_RESOURCE_ERROR|" + cleanupProblem)
    if failure != undefined or cleanupProblem != "" do throw "P16_INCOMPLETE|stop and inspect only"
    result
)
