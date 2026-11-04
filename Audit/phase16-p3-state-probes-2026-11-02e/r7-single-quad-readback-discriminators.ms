-- PREPARED / UNEXECUTED: reader calibration only, NOT emitted-file replay acceptance.
-- One owned node, four verts, one face, one Shell. No material/layer construction.
(
    local n = undefined
    local h = undefined
    fn report label result threw errorText =
        print ("P3_DISCRIM|" + label + "|result=" + (result as string) +
            "|threw=" + (threw as string) + "|error=" + errorText)
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
        for label in #("property-positive", "property-bogus", "vertex-detached-clean-and-edit",
            "face-material-id-clean-and-edit", "face-smoothing-clean-and-edit", "vertex-selection-clean-and-edit",
            "raw-user-buffer-clean-and-edit", "shell-amount-clean-and-edit", "exact-reference-clean-and-rename") do
        (
            local result = undefined
            local threw = false
            local errorText = ""
            try
            (
                result = case label of
                (
                    "property-positive": (isProperty n #name and (getProperty n #name) == n.name)
                    "property-bogus": getProperty n #P3BogusPropertyXYZ
                    "vertex-detached-clean-and-edit":
                    (
                        local v = polyop.getVert b ids[1]
                        local baseline = #(v.x, v.y, v.z)
                        local clean = polyop.getVert b ids[1]
                        local cleanEqual = baseline[1] == clean.x and baseline[2] == clean.y and baseline[3] == clean.z
                        polyop.setVert b ids[1] [0,0,1]
                        local edited = polyop.getVert b ids[1]
                        local changed = baseline[1] != edited.x or baseline[2] != edited.y or baseline[3] != edited.z
                        polyop.setVert b ids[1] [0,0,0]
                        #(cleanEqual, changed, baseline[3] == 0)
                    )
                    "face-material-id-clean-and-edit":
                    (
                        local before = polyop.getFaceMatID b fid
                        local clean = polyop.getFaceMatID b fid
                        polyop.setFaceMatID b fid (before+1)
                        local after = polyop.getFaceMatID b fid
                        polyop.setFaceMatID b fid before
                        #(before == clean, before != after)
                    )
                    "face-smoothing-clean-and-edit":
                    (
                        local before = polyop.getFaceSmoothGroup b fid
                        local clean = polyop.getFaceSmoothGroup b fid
                        local changed = if before == 1 then 2 else 1
                        polyop.setFaceSmoothGroup b fid changed
                        local after = polyop.getFaceSmoothGroup b fid
                        polyop.setFaceSmoothGroup b fid before
                        #(before == clean, before != after)
                    )
                    "vertex-selection-clean-and-edit":
                    (
                        local before = copy (polyop.getVertSelection b)
                        local clean = copy (polyop.getVertSelection b)
                        polyop.setVertSelection b #{1}
                        local after = copy (polyop.getVertSelection b)
                        polyop.setVertSelection b before
                        #(before == clean, before != after)
                    )
                    "raw-user-buffer-clean-and-edit":
                    (
                        local before = copy (getUserPropBuffer n)
                        local clean = copy (getUserPropBuffer n)
                        setUserProp n "P3ProbeOwner" "P3ProbeChanged"
                        local after = copy (getUserPropBuffer n)
                        setUserPropBuffer n before
                        #(before == clean, before != after)
                    )
                    "shell-amount-clean-and-edit":
                    (
                        local before = shellMod.outerAmount
                        local clean = shellMod.outerAmount
                        shellMod.outerAmount = before+1
                        local after = shellMod.outerAmount
                        shellMod.outerAmount = before
                        #(before == clean, before != after)
                    )
                    "exact-reference-clean-and-rename":
                    (
                        local before = copy n.name
                        local alias = getAnimByHandle h
                        local cleanEqual = alias == n
                        n.name = before + "_P3ProbeChanged"
                        local changed = n.name != before
                        local stillExact = (getAnimByHandle h) == n
                        n.name = before
                        #(cleanEqual, changed, stillExact)
                    )
                )
            )
            catch (threw = true; errorText = getCurrentException())
            report label result threw errorText
        )
    )
    catch (print ("P3_DISCRIM_OUTER_THROW|" + (getCurrentException())))
    try
    (
        if n != undefined and not isValidNode n and h != undefined do n = getAnimByHandle h
        if n != undefined and isValidNode n do
        (
            if h == undefined or (getHandleByAnim n) != h do throw "cleanup identity uncertain"
            delete n
        )
    )
    catch (print ("P3_DISCRIM_CLEANUP_INCOMPLETE|" + (getCurrentException())))
    print ("P3_DISCRIM_END|objects=" + (objects.count as string) + "|dirty=" + ((getSaveRequired()) as string))
)
