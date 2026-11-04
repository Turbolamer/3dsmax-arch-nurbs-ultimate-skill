-- Independent audit capture. Main alone may fileIn this file. NOT LIVE-VERIFIED.
-- Inputs: P3MeasurementTarget = exact node reference (never a name/prefix).
-- Optional: P3MeasurementOutput = absolute NEW evidence filename; default returns JSON.
-- Optional: P3MeasurementStage = #grid (zero modifiers) or #final (default, one Shell).
-- No dependency on a generator/runtime module, manifest or expected geometry.
(
    global P3MeasurementTarget
    global P3MeasurementOutput
    global P3MeasurementStage
    local started = timeStamp()
    local tmpMesh = undefined
    local outputStream = undefined
    local outputWriter = undefined
    local hashProvider = undefined
    local outputCreated = false
    local outputPath = undefined
    local result = undefined
    local issues = #()
    local invariant = undefined
    local textClass = undefined

    fn jquote value =
    (
        local s = value as string
        local r = "\""
        for i = 1 to s.count do
        (
            local c = substring s i 1
            case c of
            (
                "\"": r += "\\\""
                "\\": r += "\\\\"
                "\n": r += "\\n"
                "\r": r += "\\r"
                "\t": r += "\\t"
                default:
                (
                    local code = bit.charAsInt c
                    if code < 32 then
                    (
                        local digits = "0123456789abcdef"
                        r += "\\u00" + (substring digits ((floor (code / 16.0)) + 1) 1) + (substring digits ((mod code 16) + 1) 1)
                    )
                    else r += c
                )
            )
        )
        r + "\""
    )

    fn jnum value =
    (
        -- Invariant G17, not MAXScript's low-precision `as string`; never formattedPrint.
        local s = (textClass.Format invariant "{0:G17}" value) as string
        if (findString s "NaN") != undefined or (findString s "Infinity") != undefined do throw "Nonfinite measurement"
        s
    )

    fn jint value =
    (
        -- MAXScript Integer64 `as string` appends L; strip only that suffix.
        -- Keep every decimal digit, never coerce large exact integers to double.
        if (classOf value) != Integer and (classOf value) != Integer64 do throw "JSON integer requires Integer/Integer64"
        local s = value as string
        if s.count > 0 and (toLower (substring s s.count 1)) == "l" do s = substring s 1 (s.count - 1)
        if s.count == 0 do throw "Empty JSON integer"
        local firstDigit = if (substring s 1 1) == "-" then 2 else 1
        if firstDigit > s.count do throw "Missing JSON integer digits"
        for i = firstDigit to s.count do if (findString "0123456789" (substring s i 1)) == undefined do throw "Invalid JSON integer token"
        if s.count > firstDigit and (substring s firstDigit 1) == "0" do throw "Leading zero in JSON integer"
        s
    )

    fn jvalue value depth:0 =
    (
        if depth > 8 do throw "Measurement value nesting exceeds 8"
        if value == undefined then "null"
        else case (classOf value) of
        (
            String: jquote value
            Name: jquote (value as string)
            BooleanClass: (if value then "true" else "false")
            Integer: jint value
            Integer64: jint value
            Float: jnum value
            Double: jnum value
            Point3: ("[" + (jnum value.x) + "," + (jnum value.y) + "," + (jnum value.z) + "]")
            Point2: ("[" + (jnum value.x) + "," + (jnum value.y) + "]")
            Color: ("[" + (jnum value.r) + "," + (jnum value.g) + "," + (jnum value.b) + "]")
            Array:
            (
                if value.count > 1024 do throw "Measurement array exceeds 1024"
                local s = "["
                for i = 1 to value.count do (if i > 1 do s += ","; s += jvalue value[i] depth:(depth + 1))
                s + "]"
            )
            BitArray: (jvalue (value as array) depth:(depth + 1))
            default:
            (
                append issues ("Unsupported property class: " + ((classOf value) as string))
                "{\"status\":\"INCOMPLETE\",\"unsupported_class\":" + (jquote ((classOf value) as string)) + "}"
            )
        )
    )

    fn jid value = jquote ((getHandleByAnim value) as string)

    fn matrixRows tm = #(tm.row1, tm.row2, tm.row3, tm.row4)

    fn boxJson b = "{\"min\":" + (jvalue b[1]) + ",\"max\":" + (jvalue b[2]) + "}"

    fn normalAndArea vertices face =
    (
        local p = vertices[face[1]]
        local sx = 0.0d0; local sy = 0.0d0; local sz = 0.0d0
        for i = 2 to (face.count - 1) do
        (
            local q = vertices[face[i]]; local r = vertices[face[i+1]]
            local ax = (q.x as double) - (p.x as double)
            local ay = (q.y as double) - (p.y as double)
            local az = (q.z as double) - (p.z as double)
            local edgeBX = (r.x as double) - (p.x as double)
            local edgeBY = (r.y as double) - (p.y as double)
            local edgeBZ = (r.z as double) - (p.z as double)
            sx += ay*edgeBZ - az*edgeBY; sy += az*edgeBX - ax*edgeBZ; sz += ax*edgeBY - ay*edgeBX
        )
        local magnitude = sqrt (sx*sx + sy*sy + sz*sz)
        if magnitude == 0 then #(0.0d0, #(0.0d0, 0.0d0, 0.0d0))
        else #(magnitude / 2.0d0, #(sx/magnitude, sy/magnitude, sz/magnitude))
    )

    fn vertexBounds vertices =
    (
        if vertices.count == 0 do throw "Empty mesh vertices"
        local lo = copy vertices[1]; local hi = copy vertices[1]
        for p in vertices do
        (
            lo.x = amin lo.x p.x; lo.y = amin lo.y p.y; lo.z = amin lo.z p.z
            hi.x = amax hi.x p.x; hi.y = amax hi.y p.y; hi.z = amax hi.z p.z
        )
        #(lo, hi)
    )

    fn loopsFromEdges edgeRows =
    (
        -- Rows are actual [edge ID, endpoint A, endpoint B], not expected stations.
        local unused = for i = 1 to edgeRows.count collect i
        local cycles = #(); local ok = true
        while unused.count > 0 and ok do
        (
            local first = edgeRows[unused[1]]
            deleteItem unused 1
            local initial = first[2]; local current = first[3]
            local cycle = #(initial, current)
            local steps = 1
            while current != initial and ok do
            (
                local matches = #()
                for i = 1 to unused.count do
                (
                    local edge = edgeRows[unused[i]]
                    if edge[2] == current or edge[3] == current do append matches i
                )
                if matches.count != 1 then ok = false
                else
                (
                    local slot = matches[1]; local edge = edgeRows[unused[slot]]
                    deleteItem unused slot
                    current = if edge[2] == current then edge[3] else edge[2]
                    append cycle current
                    steps += 1
                    if steps > edgeRows.count + 1 do ok = false
                )
            )
            append cycles cycle
        )
        #(ok, cycles)
    )

    fn propertyJson obj prop =
    (
        local r = undefined
        try (r = jvalue (getProperty obj prop)) catch
        (
            r = "{\"status\":\"INCOMPLETE\",\"error\":" + (jquote ((getCurrentException()) as string)) + "}"
            append issues ((prop as string) + " property read incomplete")
        )
        r
    )

    try
    (
        invariant = (dotNetClass "System.Globalization.CultureInfo").InvariantCulture
        textClass = dotNetClass "System.String"
        -- Same-call serialization controls. This tests syntax/precision, not geometry.
        local precisionControl = jnum 1.2345678901234567d0
        if precisionControl != "1.2345678901234567" do throw "Invariant double precision control failed"
        if (jnum -0.125d0) != "-0.125" do throw "Invariant negative number control failed"
        if (jint (3516 as Integer64)) != "3516" do throw "Integer64 JSON suffix control failed"
        if (jint ((-3516) as Integer64)) != "-3516" do throw "Negative Integer64 JSON suffix control failed"
        if (jquote "a\n\"\\") != "\"a\\n\\\"\\\\\"" do throw "JSON string escaping control failed"
        if (jquote ((bit.intAsChar 1) as string)) != "\"\\u0001\"" do throw "JSON control-character escaping failed"

        local n = P3MeasurementTarget
        if n == undefined do throw "P3MeasurementTarget must be an exact node reference"
        if not (isValidNode n) do throw "Invalid P3MeasurementTarget"
        if (getAnimByHandle (getHandleByAnim n)) != n do throw "Target anim identity does not round trip"
        local stage = if P3MeasurementStage == undefined then #final else P3MeasurementStage
        if stage != #final and stage != #grid do throw "P3MeasurementStage must be #grid or #final"
        local base = n.baseObject
        if (classOf base) != Editable_Poly do throw "Target base is not Editable_Poly"
        if (getAnimByHandle (getHandleByAnim base)) != base do throw "Base anim identity does not round trip"
        local mods = n.modifiers.count
        if stage == #final then
        (
            if mods != 1 do throw "Final target must have exactly one modifier"
            if (classOf n.modifiers[1]) != Shell do throw "Final target's sole modifier is not Shell"
            if (getAnimByHandle (getHandleByAnim n.modifiers[1])) != n.modifiers[1] do throw "Shell anim identity does not round trip"
        )
        else if mods != 0 do throw "Grid stage target must have zero modifiers"

        local nodes = for o in objects collect o
        if nodes.count > 64 do throw "Scene census exceeds 64; refusing, never truncating"
        if findItem nodes n == 0 do throw "Exact target is absent from scene census"
        local beforeHandles = for o in nodes collect ((getHandleByAnim o) as string)
        local nv = polyop.getNumVerts base; local ne = polyop.getNumEdges base; local nf = polyop.getNumFaces base
        if nv > 64 or ne > 128 or nf > 32 do throw "Base exceeds capture ceiling (64 vertices/128 edges/32 polygons)"
        local dv = polyop.getDeadVerts base
        local de = polyop.getDeadEdges base
        local df = polyop.getDeadFaces base
        local baseLocal = for i = 1 to nv collect (polyop.getVert base i)
        local baseWorld = for p in baseLocal collect (p * n.objectTransform)
        local faceIds = #(); local faces = #(); local apiNormals = #(); local apiAreas = #()
        local normals = #(); local areas = #(); local used = #{}
        local baseArea = 0.0d0
        for f = 1 to nf where not df[f] do
        (
            local ids = polyop.getFaceVerts base f
            if ids.count > 32 do throw "Base polygon exceeds 32 vertices"
            append faceIds f; append faces ids
            for id in ids do used[id] = true
            append apiNormals (polyop.getFaceNormal base f)
            append apiAreas (polyop.getFaceArea base f)
            local measured = normalAndArea baseWorld ids
            append areas measured[1]; append normals measured[2]; baseArea += measured[1]
        )
        local edgeRows = #(); local boundaryRows = #(); local activeEdges = 0
        for e = 1 to ne where not de[e] do
        (
            local ev = (polyop.getVertsUsingEdge base #{e}) as array
            local ef = (polyop.getFacesUsingEdge base #{e}) as array
            local aliveFaces = for f in ef where not df[f] collect f
            append edgeRows #(e, ev, aliveFaces)
            if aliveFaces.count > 0 do activeEdges += 1
            if aliveFaces.count == 1 do
            (
                if ev.count != 2 do throw "Boundary edge has other than two endpoints"
                append boundaryRows #(e, ev[1], ev[2])
            )
        )
        local apiOpen = (polyop.getOpenEdges base) as array
        local loopResult = loopsFromEdges boundaryRows
        if not loopResult[1] do append issues "Boundary is not a disjoint union of simple cycles"
        local chiActive = used.numberSet - activeEdges + faces.count
        local baseJson = "{\"coordinate_space\":\"world\",\"index_base\":1,\"vertices\":" + (jvalue baseWorld)
        baseJson += ",\"vertices_local\":" + (jvalue baseLocal) + ",\"faces\":" + (jvalue faces) + ",\"face_ids\":" + (jvalue faceIds)
        baseJson += ",\"raw_counts\":" + (jvalue #(nv,ne,nf)) + ",\"dead_vertex_ids\":" + (jvalue dv) + ",\"dead_edge_ids\":" + (jvalue de) + ",\"dead_face_ids\":" + (jvalue df)
        baseJson += ",\"nondead_vertex_count\":" + ((nv - dv.numberSet) as string) + ",\"active_counts\":" + (jvalue #(used.numberSet,activeEdges,faces.count))
        baseJson += ",\"referenced_vertex_ids\":" + (jvalue used) + ",\"edges_id_vertices_faces\":" + (jvalue edgeRows)
        baseJson += ",\"open_edge_ids_api\":" + (jvalue apiOpen) + ",\"boundary_edges_id_endpoints\":" + (jvalue boundaryRows)
        baseJson += ",\"boundary_cycles_valid\":" + (jvalue loopResult[1]) + ",\"boundary_vertex_cycles_closed\":" + (jvalue loopResult[2])
        baseJson += ",\"boundary_component_count\":" + (if loopResult[1] then (loopResult[2].count as string) else "null")
        baseJson += ",\"chi_active\":" + (chiActive as string) + ",\"area_scene2\":" + (jnum baseArea)
        baseJson += ",\"face_area_scene2_world\":" + (jvalue areas) + ",\"face_normals_world\":" + (jvalue normals)
        baseJson += ",\"face_normals_api_local\":" + (jvalue apiNormals) + ",\"face_areas_api_local\":" + (jvalue apiAreas)
        baseJson += ",\"bounds\":" + (boxJson (vertexBounds baseWorld)) + "}"

        local evaluatedJson = "null"
        local evaluatedCount = 0; local evaluatedVerts = 0
        local signedVolume = undefined; local evaluatedBounds = undefined
        if stage == #final do
        (
            -- Standing verified rule: snapshotAsMesh is WORLD space already.
            -- Never multiply its vertices by objectTransform a second time.
            in coordsys world (tmpMesh = snapshotAsMesh n)
            evaluatedVerts = getNumVerts tmpMesh; evaluatedCount = getNumFaces tmpMesh
            if evaluatedCount > 256 or evaluatedVerts > 256 do throw "Evaluated capture exceeds 256 triangles/vertices; refusing, never truncating"
            local vertices = in coordsys world (for i = 1 to evaluatedVerts collect (getVert tmpMesh i))
            local triangles = #(); local triangleNormals = #(); local triangleAreas = #()
            local meshArea = 0.0d0; signedVolume = 0.0d0
            local origin = vertices[1]
            for f = 1 to evaluatedCount do
            (
                local f3 = getFace tmpMesh f
                local ids = #(f3.x as integer, f3.y as integer, f3.z as integer)
                append triangles ids
                local measured = normalAndArea vertices ids
                append triangleAreas measured[1]; append triangleNormals measured[2]; meshArea += measured[1]
                local a = vertices[ids[1]]; local b = vertices[ids[2]]; local c = vertices[ids[3]]
                local ax = (a.x as double)-(origin.x as double); local ay = (a.y as double)-(origin.y as double); local az = (a.z as double)-(origin.z as double)
                local vertexBX = (b.x as double)-(origin.x as double); local vertexBY = (b.y as double)-(origin.y as double); local vertexBZ = (b.z as double)-(origin.z as double)
                local cx = (c.x as double)-(origin.x as double); local cy = (c.y as double)-(origin.y as double); local cz = (c.z as double)-(origin.z as double)
                signedVolume += (ax*(vertexBY*cz-vertexBZ*cy) + ay*(vertexBZ*cx-vertexBX*cz) + az*(vertexBX*cy-vertexBY*cx)) / 6.0d0
            )
            evaluatedBounds = vertexBounds vertices
            evaluatedJson = "{\"coordinate_space\":\"world\",\"index_base\":1,\"vertices\":" + (jvalue vertices) + ",\"triangles\":" + (jvalue triangles)
            evaluatedJson += ",\"vertex_count\":" + (evaluatedVerts as string) + ",\"triangle_count\":" + (evaluatedCount as string)
            evaluatedJson += ",\"polygon_count\":null,\"polygon_count_status\":\"INCOMPLETE: no verified non-mutating dedicated polygon evaluator\""
            evaluatedJson += ",\"signed_volume_scene3\":" + (jnum signedVolume) + ",\"absolute_volume_scene3\":" + (jnum (abs signedVolume))
            evaluatedJson += ",\"volume_reference_world\":" + (jvalue origin) + ",\"surface_area_scene2\":" + (jnum meshArea)
            evaluatedJson += ",\"triangle_area_scene2\":" + (jvalue triangleAreas) + ",\"triangle_normals_world\":" + (jvalue triangleNormals)
            evaluatedJson += ",\"bounds\":" + (boxJson evaluatedBounds) + "}"
            delete tmpMesh
            tmpMesh = undefined
        )

        local stackJson = "["
        for mi = 1 to mods do
        (
            if mi > 1 do stackJson += ","
            local m = n.modifiers[mi]
            local props = getPropNames m
            if props.count > 128 do throw "Modifier property list exceeds 128"
            stackJson += "{\"index\":" + (mi as string) + ",\"anim_handle\":" + (jid m) + ",\"class\":" + (jquote ((classOf m) as string))
            stackJson += ",\"name\":" + (jquote m.name) + ",\"enabled\":" + (propertyJson m #enabled)
            stackJson += ",\"enabledInViews\":" + (propertyJson m #enabledInViews) + ",\"enabledInRenders\":" + (propertyJson m #enabledInRenders)
            stackJson += ",\"innerAmount\":" + (propertyJson m #innerAmount) + ",\"outerAmount\":" + (propertyJson m #outerAmount) + ",\"segments\":" + (propertyJson m #segments)
            stackJson += ",\"all_properties\":{"
            for pi = 1 to props.count do
            (
                if pi > 1 do stackJson += ","
                stackJson += (jquote (props[pi] as string)) + ":" + (propertyJson m props[pi])
            )
            stackJson += "}}"
        )
        stackJson += "]"

        local censusJson = "["; local overlapHandles = #(); local exactNameHandles = #()
        for ni = 1 to nodes.count do
        (
            local o = nodes[ni]
            if ni > 1 do censusJson += ","
            censusJson += "{\"anim_handle\":" + (jid o) + ",\"node_handle\":" + (jquote (o.handle as string)) + ",\"name\":" + (jquote o.name)
            censusJson += ",\"class\":" + (jquote ((classOf o) as string)) + ",\"base_class\":" + (jquote ((classOf o.baseObject) as string))
            censusJson += ",\"super_class\":" + (jquote ((superClassOf o) as string)) + ",\"base_anim_handle\":" + (jid o.baseObject)
            censusJson += ",\"is_target\":" + (jvalue (o == n)) + ",\"isHidden\":" + (propertyJson o #isHidden) + ",\"renderable\":" + (propertyJson o #renderable)
            censusJson += ",\"visibility\":" + (propertyJson o #visibility) + ",\"object_transform\":" + (jvalue (matrixRows o.objectTransform))
            censusJson += ",\"modifier_count\":" + (o.modifiers.count as string)
            if o.name == n.name do append exactNameHandles ((getHandleByAnim o) as string)
            try
            (
                local b = nodeGetBoundingBox o (matrix3 1)
                censusJson += ",\"bounds_world\":" + (boxJson b)
                if o != n and evaluatedBounds != undefined and (superClassOf o) == GeometryClass do
                (
                    local overlap = true
                    for axis = 1 to 3 do if b[1][axis] > evaluatedBounds[2][axis] or b[2][axis] < evaluatedBounds[1][axis] do overlap = false
                    if overlap do append overlapHandles ((getHandleByAnim o) as string)
                )
            )
            catch
            (
                censusJson += ",\"bounds_status\":\"INCOMPLETE\""
                append issues ("Census bbox failed: " + o.name)
            )
            censusJson += "}"
        )
        censusJson += "]"
        local afterNodes = for o in objects collect o
        local afterHandles = for o in afterNodes collect ((getHandleByAnim o) as string)
        if beforeHandles.count != afterHandles.count do throw "Scene census changed during measurement"
        for handle in beforeHandles do if findItem afterHandles handle == 0 do throw "Scene identities changed during measurement"
        if not (isValidNode n) or n != P3MeasurementTarget do throw "Target identity changed during measurement"

        local json = "{\"schema_version\":\"p3-independent-measurement-1\",\"status\":\"CAPTURED_NOT_ACCEPTED\",\"stage\":" + (jquote (stage as string))
        json += ",\"evidence_origin\":\"independent_read_only_scene_queries\",\"index_base\":1,\"length_unit\":\"scene_unit\""
        json += ",\"units\":{\"system_type\":" + (jquote (units.SystemType as string)) + ",\"system_scale\":" + (jnum units.SystemScale) + ",\"scene_units_per_cm\":" + (jnum (units.decodeValue "1cm")) + "}"
        json += ",\"target\":{\"name\":" + (jquote n.name) + ",\"node_handle\":" + (jquote (n.handle as string)) + ",\"anim_handle\":" + (jid n)
        json += ",\"base_anim_handle\":" + (jid base) + ",\"base_class\":" + (jquote ((classOf base) as string)) + ",\"object_transform\":" + (jvalue (matrixRows n.objectTransform)) + "}"
        if stage == #grid then json += ",\"grid\":" + baseJson
        else json += ",\"base\":" + baseJson + ",\"grid_status\":\"INCOMPLETE: predeletion stage not recoverable from final base; never reconstructed\",\"evaluated\":" + evaluatedJson
        json += ",\"stack\":" + stackJson + ",\"census\":" + censusJson + ",\"scene_count\":" + (nodes.count as string)
        json += ",\"same_exact_name_anim_handles\":" + (jvalue exactNameHandles) + ",\"other_overlapping_geometry_anim_handles\":" + (jvalue overlapHandles)
        json += ",\"occlusion_status\":\"BBox candidates only; not a geometric aperture-occlusion test. Standalone acceptance requires target-only scene.\""
        json += ",\"issues\":" + (jvalue issues) + ",\"elapsed_ms_before_io\":" + ((timeStamp() - started) as string) + "}"

        if P3MeasurementOutput == undefined then result = json
        else
        (
            if (classOf P3MeasurementOutput) != String do throw "P3MeasurementOutput must be an absolute filename string"
            outputPath = P3MeasurementOutput
            local pathApi = dotNetClass "System.IO.Path"
            if not (pathApi.IsPathRooted outputPath) do throw "Evidence output path must be absolute"
            if outputPath.count < 4 or (substring outputPath 2 1) != ":" or ((substring outputPath 3 1) != "\\" and (substring outputPath 3 1) != "/") do throw "Evidence output must be drive-qualified absolute"
            if (findString outputPath "\\\\") == 1 do throw "UNC output is outside the local evidence-file contract"
            outputPath = (pathApi.GetFullPath outputPath) as string
            local encoding = dotNetObject "System.Text.UTF8Encoding" false
            local expectedBytes = encoding.GetByteCount json
            if expectedBytes > 2097152 do throw "Evidence exceeds 2 MiB; refusing, never truncating"
            -- Exact one filename, atomic CreateNew, no overwrite, no directories/delete.
            outputStream = dotNetObject "System.IO.FileStream" outputPath ((dotNetClass "System.IO.FileMode").CreateNew) ((dotNetClass "System.IO.FileAccess").ReadWrite) ((dotNetClass "System.IO.FileShare").None)
            outputCreated = true
            outputWriter = dotNetObject "System.IO.StreamWriter" outputStream encoding
            outputWriter.Write json
            outputWriter.Flush()
            outputStream.Flush()
            local fileBytes = outputStream.Length
            if fileBytes != expectedBytes do throw "Evidence UTF-8 byte count differs after flush"
            outputStream.Position = 0
            hashProvider = (dotNetClass "System.Security.Cryptography.SHA256").Create()
            local digest = hashProvider.ComputeHash outputStream
            hashProvider.Dispose(); hashProvider = undefined
            -- Default .NET interop marshals byte[] to a MAXScript Array.
            -- Do not call .Length or pass it back to a byte[] overload.
            if (classOf digest) != Array or digest.count != 32 do throw "SHA-256 digest is not a 32-byte marshalled array"
            local digits = "0123456789abcdef"
            local hex = ""
            for byteValue in digest do
            (
                if byteValue < 0 or byteValue > 255 do throw "Invalid SHA-256 byte"
                hex += (substring digits ((floor (byteValue / 16.0)) + 1) 1) + (substring digits ((mod byteValue 16) + 1) 1)
            )
            -- Closing the writer closes its underlying stream; hash is already done.
            outputWriter.Close(); outputWriter = undefined
            outputStream = undefined
            result = "{\"status\":\"CAPTURED_NOT_ACCEPTED\",\"path\":" + (jquote outputPath) + ",\"sha256\":" + (jquote hex)
            result += ",\"bytes\":" + (jint fileBytes) + ",\"base_active_counts\":" + (jvalue #(used.numberSet,activeEdges,faces.count))
            result += ",\"evaluated_vertices\":" + (evaluatedVerts as string) + ",\"evaluated_triangles\":" + (evaluatedCount as string)
            result += ",\"scene_count\":" + (nodes.count as string) + ",\"issue_count\":" + (issues.count as string) + ",\"elapsed_ms\":" + ((timeStamp() - started) as string) + "}"
        )
    )
    catch
    (
        -- Cleanup first: never let an unguarded diagnostic retain the temporary mesh.
        local errorText = (getCurrentException()) as string
        local cleanupIssues = #()
        if tmpMesh != undefined do
        (
            try (delete tmpMesh; tmpMesh = undefined) catch (append cleanupIssues "TriMesh delete failed")
        )
        if hashProvider != undefined do
        (
            try (hashProvider.Dispose(); hashProvider = undefined) catch (append cleanupIssues "Hash provider dispose failed")
        )
        if outputWriter != undefined do
        (
            try (outputWriter.Close(); outputWriter = undefined) catch (append cleanupIssues "Evidence writer close failed")
        )
        if outputStream != undefined do
        (
            try (outputStream.Close(); outputStream = undefined) catch (append cleanupIssues "Evidence stream close failed")
        )
        result = "{\"status\":\"INCOMPLETE\",\"error\":" + (jquote errorText) + ",\"output_created\":" + (if outputCreated then "true" else "false")
        result += ",\"output_path\":" + (if outputPath == undefined then "null" else jquote outputPath) + ",\"cleanup_issues\":" + (jvalue cleanupIssues) + "}"
    )
    result
)
