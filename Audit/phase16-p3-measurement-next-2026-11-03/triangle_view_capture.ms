-- CANDIDATE ONLY: main alone may run; not Max-parser- or live-tested.
-- Read-only scene query of an exact externally supplied node reference.
-- The only deletion is the exact in-memory TriMesh returned by snapshotAsMesh.
-- Result describes meshop's angle/edge-visibility triangle groups, NOT native
-- evaluated Editable_Poly faces. No historical pre-deletion grid is recovered.
-- No output file is opened; main retains the complete bridge response externally.
(
    global P3NextMeasurementTarget
    local started = timeStamp()
    local meshValue = undefined
    local result = undefined
    local invariant = (dotNetClass "System.Globalization.CultureInfo").InvariantCulture
    local textClass = dotNetClass "System.String"

    fn quoted value =
    (
        local s = value as string
        local out = "\""
        for k = 1 to s.count do
        (
            local c = substring s k 1
            case c of
            (
                "\"": out += "\\\""
                "\\": out += "\\\\"
                "\n": out += "\\n"
                "\r": out += "\\r"
                "\t": out += "\\t"
                default:
                (
                    local codepoint = bit.charAsInt c
                    if codepoint < 32 then
                    (
                        local digits = "0123456789abcdef"
                        out += "\\u00" + (substring digits ((floor (codepoint / 16.0)) + 1) 1) + (substring digits ((mod codepoint 16) + 1) 1)
                    )
                    else out += c
                )
            )
        )
        out + "\""
    )
    fn numberValue value =
    (
        local s = (textClass.Format invariant "{0:G17}" value) as string
        if (findString s "NaN") != undefined or (findString s "Infinity") != undefined do throw "Nonfinite numeric value"
        s
    )
    fn arrayValue rows =
    (
        local s = "["
        for k = 1 to rows.count do
        (
            if k > 1 do s += ","
            local item = rows[k]
            case (classOf item) of
            (
                Point3: s += "[" + (numberValue item.x) + "," + (numberValue item.y) + "," + (numberValue item.z) + "]"
                Array: s += arrayValue item
                Integer: s += item as string
                Float: s += numberValue item
                Double: s += numberValue item
                BooleanClass: s += (if item then "true" else "false")
                default: throw "Unsupported capture array item"
            )
        )
        s + "]"
    )

    try
    (
        if (numberValue 1.2345678901234567d0) != "1.2345678901234567" do throw "Double serialization control failed"
        if (numberValue -0.125d0) != "-0.125" do throw "Negative serialization control failed"
        if (quoted "a\n\"\\") != "\"a\\n\\\"\\\\\"" do throw "String serialization control failed"
        local n = P3NextMeasurementTarget
        if n == undefined or not (isValidNode n) do throw "Exact valid target reference required"
        local nodeAnim = getHandleByAnim n
        if nodeAnim == undefined or (getAnimByHandle nodeAnim) != n do throw "Node reference does not round trip"
        if objects.count != 1 do throw "Target-only scene required"
        local censusBefore = for o in objects collect o
        if censusBefore.count != 1 or censusBefore[1] != n do throw "Exact target not the only scene node"
        local base = n.baseObject
        if (classOf base) != Editable_Poly do throw "Editable_Poly base required"
        local baseAnim = getHandleByAnim base
        if baseAnim == undefined or (getAnimByHandle baseAnim) != base do throw "Base reference does not round trip"
        if n.modifiers.count != 1 or (classOf n.modifiers[1]) != Shell do throw "Exactly one Shell required"
        local shellValue = n.modifiers[1]
        local shellAnim = getHandleByAnim shellValue
        if shellAnim == undefined or (getAnimByHandle shellAnim) != shellValue do throw "Shell reference does not round trip"
        local unitsType = units.SystemType
        local unitsScale = units.SystemScale
        local unitsPerCm = units.decodeValue "1cm"
        local tm = n.objectTransform
        local sceneTime = currentTime
        local filePathBefore = maxFilePath
        local fileNameBefore = maxFileName
        local dirtyBefore = getSaveRequired()
        local selectionBefore = for o in selection collect o
        local baseCounts = #(polyop.getNumVerts base, polyop.getNumEdges base, polyop.getNumFaces base)
        if baseCounts[1] < 1 or baseCounts[1] > 24 or baseCounts[2] > 128 or baseCounts[3] < 1 or baseCounts[3] > 15 do throw "F01 base ceiling exceeded"
        in coordsys world (meshValue = snapshotAsMesh n)
        local vertexCount = getNumVerts meshValue
        local triangleCount = getNumFaces meshValue
        if vertexCount < 1 or vertexCount > 64 or triangleCount < 1 or triangleCount > 96 do throw "Evaluated F01 ceiling exceeded"
        local vertices = in coordsys world (for k = 1 to vertexCount collect (getVert meshValue k))
        local triangles = #()
        local visibility = #()
        local faceGroups = #()
        for k = 1 to triangleCount do
        (
            local face = getFace meshValue k
            local tri = #(face.x as integer, face.y as integer, face.z as integer)
            for idx in tri do if idx < 1 or idx > vertexCount do throw "Triangle index out of range"
            append triangles tri
            append visibility #(getEdgeVis meshValue k 1, getEdgeVis meshValue k 2, getEdgeVis meshValue k 3)
            local seed = #{}
            seed[k] = true
            local members = (meshop.getPolysUsingFace meshValue seed ignoreVisEdges:false threshhold:45.0) as array
            if members.count < 1 or members.count > triangleCount or (findItem members k) == 0 do throw "Invalid group result"
            append faceGroups members
        )
        -- This documented query counts the result as if converted to a TriMesh,
        -- NOT native evaluated polygon faces. Kept as a separate raw channel.
        local meshEquivalentCounts = getPolygonCount n
        if (classOf meshEquivalentCounts) != Array or meshEquivalentCounts.count != 2 do throw "Node mesh-equivalent count unavailable"
        if (classOf meshEquivalentCounts[1]) != Integer or (classOf meshEquivalentCounts[2]) != Integer do throw "Node mesh-equivalent count is not integer"
        delete meshValue
        meshValue = undefined
        if not (isValidNode n) or n != P3NextMeasurementTarget do throw "Target reference changed during capture"
        if (getAnimByHandle nodeAnim) != n or n.baseObject != base or (getAnimByHandle baseAnim) != base do throw "Node/base identity changed"
        if n.modifiers.count != 1 or n.modifiers[1] != shellValue or (getAnimByHandle shellAnim) != shellValue do throw "Shell identity changed"
        if objects.count != 1 do throw "Scene census changed"
        local censusAfter = for o in objects collect o
        if censusAfter.count != 1 or censusAfter[1] != n do throw "Exact scene census changed"
        local selectionAfter = for o in selection collect o
        if selectionAfter.count != selectionBefore.count do throw "Selection count changed"
        for o in selectionBefore do if (findItem selectionAfter o) == 0 do throw "Selection identity changed"
        if n.objectTransform != tm or units.SystemType != unitsType or units.SystemScale != unitsScale or (units.decodeValue "1cm") != unitsPerCm do throw "Transform or units changed"
        if currentTime != sceneTime or maxFilePath != filePathBefore or maxFileName != fileNameBefore or getSaveRequired() != dirtyBefore do throw "Time/path/dirty state changed"
        if (polyop.getNumVerts base) != baseCounts[1] or (polyop.getNumEdges base) != baseCounts[2] or (polyop.getNumFaces base) != baseCounts[3] do throw "Base counts changed"
        result = "{\"schema_version\":\"p3-triangle-view-1\",\"status\":\"CAPTURED_NOT_ACCEPTED\",\"observation\":\"snapshot_triangle_groups_not_native_polygons\",\"index_base\":1,\"coordinate_space\":\"world\""
        result += ",\"target\":{\"node_handle\":" + (quoted (n.handle as string)) + ",\"anim_handle\":" + (quoted (nodeAnim as string)) + ",\"base_anim_handle\":" + (quoted (baseAnim as string)) + ",\"modifier_anim_handle\":" + (quoted (shellAnim as string)) + ",\"object_transform\":" + (arrayValue #(tm.row1, tm.row2, tm.row3, tm.row4)) + "}"
        result += ",\"units\":{\"system_type\":" + (quoted (unitsType as string)) + ",\"system_scale\":" + (numberValue unitsScale) + ",\"scene_units_per_cm\":" + (numberValue unitsPerCm) + "}"
        result += ",\"group_api\":\"meshop.getPolysUsingFace\",\"ignore_visible_edges\":false,\"threshold_degrees\":45,\"vertices\":" + (arrayValue vertices) + ",\"triangles\":" + (arrayValue triangles)
        result += ",\"triangle_edge_visibility\":" + (arrayValue visibility) + ",\"groups_for_each_triangle\":" + (arrayValue faceGroups) + ",\"mesh_equivalent_node_counts\":" + (arrayValue meshEquivalentCounts)
        result += ",\"native_evaluated_polygon_status\":\"INCOMPLETE\",\"historical_predelete_grid_status\":\"INCOMPLETE\",\"elapsed_ms\":" + ((timeStamp() - started) as string) + "}"
    )
    catch
    (
        -- Retain the original exception; attempt only exact temporary mesh cleanup.
        local failure = getCurrentException()
        local cleanupOK = true
        if meshValue != undefined do try (delete meshValue; meshValue = undefined) catch (cleanupOK = false)
        result = "{\"status\":\"INCOMPLETE\",\"error\":" + (quoted (failure as string)) + ",\"temporary_mesh_cleanup_ok\":" + (if cleanupOK then "true" else "false") + "}"
    )
    result
)
