-- Read-only calibration of a MAIN-CREATED translated/rotated one-quad node.
-- No scene creation/conversion/Shell; main supplies exact P3MeasurementTarget.
-- Returns small JSON for main to retain in its wire evidence. NOT LIVE-VERIFIED.
(
    global P3MeasurementTarget
    local meshValue = undefined
    local started = timeStamp()
    local answer = undefined
    local invariant = (dotNetClass "System.Globalization.CultureInfo").InvariantCulture
    local textClass = dotNetClass "System.String"

    fn quoteValue value =
    (
        local s = substituteString (value as string) "\\" "\\\\"
        s = substituteString s "\"" "\\\""
        s = substituteString s "\n" "\\n"
        s = substituteString s "\r" "\\r"
        s = substituteString s "\t" "\\t"
        "\"" + s + "\""
    )
    fn numberValue value =
    (
        local s = (textClass.Format invariant "{0:G17}" value) as string
        if (findString s "NaN") != undefined or (findString s "Infinity") != undefined do throw "Nonfinite calibration number"
        s
    )
    fn arrayValue rows =
    (
        local s = "["
        for i = 1 to rows.count do
        (
            if i > 1 do s += ","
            local row = rows[i]
            case (classOf row) of
            (
                Point3: s += "[" + (numberValue row.x) + "," + (numberValue row.y) + "," + (numberValue row.z) + "]"
                Array: s += arrayValue row
                Integer: s += row as string
                Float: s += numberValue row
                Double: s += numberValue row
                default: throw "Unsupported calibration array item"
            )
        )
        s + "]"
    )

    try
    (
        if (numberValue 1.2345678901234567d0) != "1.2345678901234567" do throw "Calibration precision control failed"
        local n = P3MeasurementTarget
        if n == undefined or not (isValidNode n) do throw "Exact valid P3MeasurementTarget required"
        if (getAnimByHandle (getHandleByAnim n)) != n do throw "Calibration target identity does not round trip"
        local base = n.baseObject
        if (classOf base) != Editable_Poly or n.modifiers.count != 0 do throw "Calibration requires unmodified Editable_Poly"
        if polyop.getNumVerts base != 4 or polyop.getNumFaces base != 1 do throw "Calibration requires exactly four base vertices and one polygon"
        local face = polyop.getFaceVerts base 1
        if face.count != 4 do throw "Calibration requires one actual quad"
        local tm = n.objectTransform
        if tm == (matrix3 1) do throw "Identity transform cannot calibrate the double-transform fault"
        local beforeNodes = for o in objects collect ((getHandleByAnim o) as string)
        if beforeNodes.count > 64 do throw "Calibration scene census exceeds 64"
        local localVertices = for i = 1 to 4 collect (polyop.getVert base i)
        -- Independent channel: raw base local coordinates transformed exactly ONCE.
        local baseWorld = for p in localVertices collect (p * tm)
        in coordsys world (meshValue = snapshotAsMesh n)
        if getNumVerts meshValue != 4 or getNumFaces meshValue != 2 do throw "Calibration snapshot is not four vertices/two triangles"
        -- Channel under test: already world-space snapshot, NO objectTransform.
        local observed = in coordsys world (for i = 1 to 4 collect (getVert meshValue i))
        local triangles = for i = 1 to 2 collect
        (
            local f = getFace meshValue i
            #(f.x as integer, f.y as integer, f.z as integer)
        )
        local bounds = nodeGetBoundingBox n (matrix3 1)
        delete meshValue; meshValue = undefined
        local afterNodes = for o in objects collect ((getHandleByAnim o) as string)
        if beforeNodes.count != afterNodes.count do throw "Calibration scene census changed"
        for h in beforeNodes do if (findItem afterNodes h) == 0 do throw "Calibration scene identities changed"
        answer = "{\"schema_version\":\"p3-snapshot-calibration-1\",\"status\":\"CAPTURED_NOT_ACCEPTED\",\"index_base\":1"
        answer += ",\"target_anim_handle\":" + (quoteValue ((getHandleByAnim n) as string)) + ",\"base_anim_handle\":" + (quoteValue ((getHandleByAnim base) as string))
        answer += ",\"base_vertices_local\":" + (arrayValue localVertices) + ",\"base_faces\":" + (arrayValue #(face))
        answer += ",\"object_transform\":" + (arrayValue #(tm.row1, tm.row2, tm.row3, tm.row4))
        answer += ",\"base_vertices_world_once\":" + (arrayValue baseWorld) + ",\"snapshot_vertices_world\":" + (arrayValue observed)
        answer += ",\"snapshot_triangles\":" + (arrayValue triangles) + ",\"node_bounds_world\":" + (arrayValue bounds)
        answer += ",\"scene_count\":" + (beforeNodes.count as string) + ",\"elapsed_ms\":" + ((timeStamp() - started) as string) + "}"
    )
    catch
    (
        local message = (getCurrentException()) as string
        local cleanup = true
        if meshValue != undefined do try (delete meshValue; meshValue = undefined) catch (cleanup = false)
        answer = "{\"status\":\"INCOMPLETE\",\"error\":" + (quoteValue message) + ",\"mesh_cleanup_ok\":" + (if cleanup then "true" else "false") + "}"
    )
    answer
)
