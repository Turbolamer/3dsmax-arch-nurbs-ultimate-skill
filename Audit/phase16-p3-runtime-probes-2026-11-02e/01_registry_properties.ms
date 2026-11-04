-- fileIn only. One exact temporary node; no registry/caller-global mutation.
(
    local owned = undefined
    local out = ""
    try
    (
        owned = Editable_Mesh()
        local originalHandle = getHandleByAnim owned
        local converted = convertTo owned Editable_Poly
        if isValidNode converted do owned = converted
        if not isValidNode owned do owned = getAnimByHandle originalHandle
        if not isValidNode owned or (getHandleByAnim owned) != originalHandle do throw "conversion identity unavailable"
        local shellMod = Shell innerAmount:0.0 outerAmount:1.0 segments:1
        addModifier owned shellMod
        out += "node=" + ((classOf owned) as string) + ";base=" + ((classOf owned.baseObject) as string) + "\n"
        for target in #(owned, owned.baseObject, shellMod, owned.layer, owned.transform.controller) do
        (
            out += "TARGET " + ((classOf target) as string) + "\n"
            try (out += "handleRoundTrip=" + (((getAnimByHandle (getHandleByAnim target)) == target) as string) + "\n") catch (out += "HANDLE_ERROR " + (getCurrentException() as string) + "\n")
            try (out += "numRefs=" + ((refs.getNumRefs target) as string) + "\n") catch (out += "REF_ERROR " + (getCurrentException() as string) + "\n")
            try (out += "dependents=" + ((for d in (refs.dependents target) collect classOf d) as string) + "\n") catch (out += "DEPENDENT_ERROR " + (getCurrentException() as string) + "\n")
            try (out += "properties=" + ((for p in (getPropNames target) collect #(p, classOf (getProperty target p))) as string) + "\n") catch (out += "PROPERTY_ERROR " + (getCurrentException() as string) + "\n")
        )
        for code in #("globalVars.isGlobal #P3TotallyUnboundProbeSymbol", "isController", "polyop.getMapSupport", "polyop.getNumMapFaces", "polyop.getNumVDataChannels", "polyop.getNumEDataChannels", "1+1", "P3BogusRuntimeAPI_20261102") do
        (
            local value = undefined
            local threw = false
            try (value = execute code) catch (threw = true)
            out += code + ":threw=" + (threw as string) + ";undef=" + ((value == undefined) as string) + ";class=" + ((classOf value) as string) + "\n"
        )
    )
    catch (out += "PROBE_ERROR " + (getCurrentException() as string) + "\n")
    try (if isValidNode owned do delete owned) catch (out += "CLEANUP_ERROR " + (getCurrentException() as string) + "\n")
    out += "exactRefStillValid=" + ((isValidNode owned) as string)
    print out
)
