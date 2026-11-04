-- fileIn only. One exact temporary node; each uncertain operational call isolated.
(
    local owned = undefined
    local out = ""
    try
    (
        owned = Editable_Mesh()
        local h = getHandleByAnim owned
        local converted = convertTo owned Editable_Poly
        if isValidNode converted do owned = converted
        if not isValidNode owned do owned = getAnimByHandle h
        if not isValidNode owned or (getHandleByAnim owned) != h do throw "identity unavailable"
        local ids = for point in #([0,0,0],[10,0,0],[10,0,10],[0,0,10]) collect polyop.createVert owned point
        local face = polyop.createPolygon owned ids
        local base = owned.baseObject
        try (out += "dead=" + (#(polyop.getDeadVerts base,polyop.getDeadEdges base,polyop.getDeadFaces base) as string) + "\n") catch (out += "DEAD_ERROR " + (getCurrentException() as string) + "\n")
        try (out += "flags=" + (#(polyop.getVertFlags base 1,polyop.getEdgeFlags base 1,polyop.getFaceFlags base face) as string) + "\n") catch (out += "FLAGS_ERROR " + (getCurrentException() as string) + "\n")
        try (out += "face=" + (#(polyop.getFaceVerts base face,polyop.getFaceMatID base face,polyop.getFaceSmoothGroup base face) as string) + "\n") catch (out += "FACE_ERROR " + (getCurrentException() as string) + "\n")
        try
        (
            out += "maps=" + ((polyop.getNumMaps base) as string) + "\n"
            for c = -2 to ((polyop.getNumMaps base)-1) do
            (
                local supported = polyop.getMapSupport base c
                out += "map " + (c as string) + " support=" + (supported as string)
                if supported do out += " verts=" + ((polyop.getNumMapVerts base c) as string) + " faces=" + ((polyop.getNumMapFaces base c) as string)
                out += "\n"
            )
        ) catch (out += "MAP_ERROR " + (getCurrentException() as string) + "\n")
        try (out += "vdata=" + ((polyop.getNumVDataChannels base) as string) + "\n") catch (out += "VDATA_ERROR " + (getCurrentException() as string) + "\n")
        try (out += "edata=" + ((polyop.getNumEDataChannels base) as string) + "\n") catch (out += "EDATA_ERROR " + (getCurrentException() as string) + "\n")
        try (out += "controller=" + ((isController owned.transform.controller) as string) + ";keys=" + ((numKeys owned.transform.controller) as string) + "\n") catch (out += "CONTROLLER_ERROR " + (getCurrentException() as string) + "\n")
        try (out += "globalMissing=" + ((globalVars.isGlobal #P3TotallyUnboundProbeSymbol) as string) + "\n") catch (out += "GLOBAL_ERROR " + (getCurrentException() as string) + "\n")
    )
    catch (out += "PROBE_ERROR " + (getCurrentException() as string) + "\n")
    try (if isValidNode owned do delete owned) catch (out += "CLEANUP_ERROR " + (getCurrentException() as string) + "\n")
    print (out + "exactRefStillValid=" + ((isValidNode owned) as string))
)
