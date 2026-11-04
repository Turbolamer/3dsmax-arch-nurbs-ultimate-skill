-- PREPARED / UNEXECUTED: main-only, fileIn, candidate R4/R5 API calibration.
-- Exactly one owned node, four vertices, one quad, one Shell; no materials/layers.
-- No runtime acceptance is implied by a reader resolving or this file parsing.
(
    local n = undefined
    local h = undefined
    fn report label value threw errorText =
    (
        local text = "<not-stringifiable>"
        try (text = value as string) catch ()
        print ("P3_STATE|" + label + "|threw=" + (threw as string) +
            "|undef=" + ((value == undefined) as string) + "|class=" +
            ((classOf value) as string) + "|value=" + text + "|error=" + errorText)
    )
    try
    (
        if objects.count != 0 or selection.count != 0 do throw "P3_PROBE_REFUSE|not empty"
        if maxFilePath != "" or maxFileName != "" do throw "P3_PROBE_REFUSE|named scene"
        n = Editable_Mesh()
        h = getHandleByAnim n
        local converted = convertTo n Editable_Poly
        if isValidNode converted do n = converted
        if not isValidNode n do n = getAnimByHandle h
        if not isValidNode n or (getHandleByAnim n) != h do throw "P3_PROBE_INCOMPLETE|conversion identity"
        local ids = #()
        for p in #([0,0,0], [10,0,0], [10,0,10], [0,0,10]) do append ids (polyop.createVert n p)
        local fid = polyop.createPolygon n ids
        update n
        local shellMod = Shell innerAmount:0.0 outerAmount:1.0 segments:1
        addModifier n shellMod
        update n
        local b = n.baseObject
        print ("P3_STATE_SETUP|nodeHandle=" + (h as string) + "|vertexIds=" +
            (ids as string) + "|faceId=" + (fid as string) + "|objects=" + (objects.count as string))

        -- Existence/read errors are separate for every candidate; #name is positive.
        for p in #(#name, #P3BogusPropertyXYZ, #wirecolor, #isHidden, #isFrozen,
            #renderable, #primaryVisibility, #secondaryVisibility, #castShadows,
            #receiveShadows, #visibility, #inheritVisibility, #displayByLayer,
            #renderByLayer, #isSelected, #pos, #rotation, #scale, #pivot,
            #objectOffsetPos, #objectOffsetRot, #objectOffsetScale, #transform,
            #objectTransform, #parent, #children, #layer, #material, #controller) do
        (
            local value = undefined
            local threw = false
            local errorText = ""
            local present = undefined
            try (present = isProperty n p) catch (errorText = getCurrentException())
            print ("P3_PROPERTY_PRESENT|" + (p as string) + "|present=" + (present as string) + "|error=" + errorText)
            try (value = getProperty n p) catch (threw = true; errorText = getCurrentException())
            report ("node." + (p as string)) value threw errorText
        )
        for target in #(#("base", b), #("shell", shellMod), #("layer", n.layer)) do
        (
            local value = undefined
            local threw = false
            local errorText = ""
            try (value = getPropNames target[2]) catch (threw = true; errorText = getCurrentException())
            report (target[1] + ".getPropNames") value threw errorText
            for p in #(#name, #P3BogusPropertyXYZ) do
            (
                value = undefined; threw = false; errorText = ""
                try (value = getProperty target[2] p) catch (threw = true; errorText = getCurrentException())
                report (target[1] + "." + (p as string)) value threw errorText
            )
        )

        local controllerValues = #()
        for label in #("node.controller", "position.controller", "rotation.controller",
            "scale.controller", "visibility.controller", "shell.outerAmount.controller",
            "node.refsCount", "base.refsCount", "shell.refsCount", "node.dependents",
            "base.dependents", "shell.dependents", "node.dependentNodes", "base.dependentNodes",
            "node.userBuffer", "node.material", "node.custAttributes", "base.custAttributes",
            "shell.custAttributes", "shell.enabled", "shell.enabledInViews", "shell.enabledInRenders") do
        (
            local value = undefined
            local threw = false
            local errorText = ""
            try
            (
                value = case label of
                (
                    "node.controller": n.controller
                    "position.controller": n.position.controller
                    "rotation.controller": n.rotation.controller
                    "scale.controller": n.scale.controller
                    "visibility.controller": getPropertyController n #visibility
                    "shell.outerAmount.controller": getPropertyController shellMod #outerAmount
                    "node.refsCount": refs.getNumRefs n
                    "base.refsCount": refs.getNumRefs b
                    "shell.refsCount": refs.getNumRefs shellMod
                    "node.dependents": refs.dependents n
                    "base.dependents": refs.dependents b
                    "shell.dependents": refs.dependents shellMod
                    "node.dependentNodes": refs.dependentNodes n
                    "base.dependentNodes": refs.dependentNodes b
                    "node.userBuffer": getUserPropBuffer n
                    "node.material": n.material
                    "node.custAttributes": custAttributes.count n
                    "base.custAttributes": custAttributes.count b
                    "shell.custAttributes": custAttributes.count shellMod
                    "shell.enabled": shellMod.enabled
                    "shell.enabledInViews": shellMod.enabledInViews
                    "shell.enabledInRenders": shellMod.enabledInRenders
                )
            )
            catch (threw = true; errorText = getCurrentException())
            report label value threw errorText
            if not threw and value != undefined and (findString label ".controller") != undefined do
                append controllerValues #(label, value)
        )
        for entry in controllerValues do
        (
            for label in #("numKeys", "properties", "dependents", "superClass") do
            (
                local value = undefined
                local threw = false
                local errorText = ""
                try
                (
                    value = case label of
                    (
                        "numKeys": numKeys entry[2]
                        "properties": getPropNames entry[2]
                        "dependents": refs.dependents entry[2]
                        "superClass": superClassOf entry[2]
                    )
                )
                catch (threw = true; errorText = getCurrentException())
                report (entry[1] + "." + label) value threw errorText
            )
        )

        for label in #("getNumVerts", "getNumEdges", "getNumFaces", "getDeadVerts", "getDeadEdges",
            "getDeadFaces", "getVert", "getVertFlags", "getEdgeVerts", "getEdgeFlags", "getFaceVerts",
            "getFaceFlags", "getFaceMatID", "getFaceSmoothGroup", "getVertSelection", "getEdgeSelection",
            "getFaceSelection", "getNumMaps", "getNumVDataChannels", "getNumEDataChannels") do
        (
            local value = undefined
            local threw = false
            local errorText = ""
            try
            (
                value = case label of
                (
                    "getNumVerts": polyop.getNumVerts b
                    "getNumEdges": polyop.getNumEdges b
                    "getNumFaces": polyop.getNumFaces b
                    "getDeadVerts": polyop.getDeadVerts b
                    "getDeadEdges": polyop.getDeadEdges b
                    "getDeadFaces": polyop.getDeadFaces b
                    "getVert": polyop.getVert b ids[1]
                    "getVertFlags": polyop.getVertFlags b ids[1]
                    "getEdgeVerts": polyop.getEdgeVerts b 1
                    "getEdgeFlags": polyop.getEdgeFlags b 1
                    "getFaceVerts": polyop.getFaceVerts b fid
                    "getFaceFlags": polyop.getFaceFlags b fid
                    "getFaceMatID": polyop.getFaceMatID b fid
                    "getFaceSmoothGroup": polyop.getFaceSmoothGroup b fid
                    "getVertSelection": polyop.getVertSelection b
                    "getEdgeSelection": polyop.getEdgeSelection b
                    "getFaceSelection": polyop.getFaceSelection b
                    "getNumMaps": polyop.getNumMaps b
                    "getNumVDataChannels": polyop.getNumVDataChannels b
                    "getNumEDataChannels": polyop.getNumEDataChannels b
                )
            )
            catch (threw = true; errorText = getCurrentException())
            report ("polyop." + label) value threw errorText
        )
        -- Only fixed candidate channels; this is not a claim of full map coverage.
        for channel in #(-2, -1, 0, 1, 2) do
        (
            for label in #("support", "verts", "faces") do
            (
                local value = undefined
                local threw = false
                local errorText = ""
                try
                (
                    value = case label of
                    (
                        "support": polyop.getMapSupport b channel
                        "verts": polyop.getNumMapVerts b channel
                        "faces": polyop.getNumMapFaces b channel
                    )
                )
                catch (threw = true; errorText = getCurrentException())
                report ("map." + (channel as string) + "." + label) value threw errorText
            )
        )
    )
    catch (print ("P3_STATE_SETUP_OR_OUTER_THROW|" + (getCurrentException())))
    -- Exact reference first; conversion recovery ONLY uses the captured handle.
    try
    (
        if n != undefined and not isValidNode n and h != undefined do n = getAnimByHandle h
        if n != undefined and isValidNode n do
        (
            if h == undefined or (getHandleByAnim n) != h do throw "cleanup identity uncertain"
            delete n
        )
    )
    catch (print ("P3_STATE_CLEANUP_INCOMPLETE|" + (getCurrentException())))
    print ("P3_STATE_END|objects=" + (objects.count as string) + "|dirty=" + ((getSaveRequired()) as string))
)
