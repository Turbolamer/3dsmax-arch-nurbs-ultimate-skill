-- fileIn only. Fresh reserved probe symbol; refuse if preexisting, never replace.
(
    local key = #__P3_RuntimeProbe_b2818628e9c542f099ac91c637f5ed21
    local owned = undefined
    local wrote = false
    local declared = false
    local out = ""
    try
    (
        if globalVars.isGlobal key do throw "probe key already exists; refusing"
        execute ("global " + (key as string))
        declared = true
        owned = Editable_Mesh()
        local payload = #("probe-only", owned, getHandleByAnim owned)
        globalVars.set key payload
        wrote = true
        out += "published=" + ((globalVars.isGlobal key) as string) + ";sameArray=" + (((globalVars.get key) == payload) as string) + "\n"
        out += "rootHandle=" + ((getHandleByAnim rootNode) as string) + ";rootRoundtrip=" + (((getAnimByHandle (getHandleByAnim rootNode)) == rootNode) as string) + "\n"
        out += "parents=" + (#(owned.parent == rootNode, owned.parent == undefined) as string) + "\n"
        out += "classBoolean=" + ((classOf true) as string) + ";classDouble=" + ((classOf 1.0d0) as string) + ";classUndefined=" + ((classOf undefined) as string) + "\n"
    )
    catch (out += "PROBE_ERROR " + (getCurrentException() as string) + "\n")
    if declared do try (globalVars.remove key) catch (out += "GLOBAL_CLEANUP_ERROR " + (getCurrentException() as string) + "\n")
    try (if isValidNode owned do delete owned) catch (out += "NODE_CLEANUP_ERROR " + (getCurrentException() as string) + "\n")
    print (out + "exactRefStillValid=" + ((isValidNode owned) as string))
)
