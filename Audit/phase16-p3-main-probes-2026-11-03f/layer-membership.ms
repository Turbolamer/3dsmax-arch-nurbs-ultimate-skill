-- Main-only: one owned Box and one owned layer, no user-layer property changes.
-- A diagnostic membership control; not broad dependency/replay acceptance.
(
    local label = "P3F_Layer_6D930A"
    local text = "P3_LAYER_MEMBERSHIP"
    local baseLayer = undefined
    local baseRef = undefined
    local baseHandle = undefined
    local baseDeps = undefined
    local layer = undefined
    local target = undefined
    local targetHandle = undefined
    local n = undefined
    local nodeHandle = undefined
    local layerAttempt = false
    local nodeAttempt = false
    local nodeRemoved = false
    local layerRemoved = false
    local beforeDirty = getSaveRequired()
    local outcome = "INCOMPLETE"
    fn p3SetSame a b =
    (
        if a == undefined or b == undefined or a.count != b.count then false
        else (local yes = true; for x in a while yes do if (findItem b x) == 0 do yes = false; yes)
    )
    try
    (
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "scene not empty unnamed unselected"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "units mismatch"
        if LayerManager.count != 1 or (LayerManager.getLayerFromName label) != undefined do throw "unexpected layer state/name"
        baseLayer = LayerManager.getLayer 0
        baseRef = baseLayer.layerAsRefTarg
        baseHandle = getHandleByAnim baseRef
        if baseLayer.name != "0" or not baseLayer.current or (getAnimByHandle baseHandle) != baseRef do throw "default identity/current"
        baseDeps = refs.dependents baseRef
        if baseDeps == undefined or baseDeps.count > 8 or (refs.getNumRefs baseRef) != 0 do throw "default dependencies unsupported"
        local initialMembers = #()
        if not (baseLayer.nodes &initialMembers) or initialMembers.count != 0 do throw "default not empty"
        layerAttempt = true
        layer = LayerManager.newLayerFromName label
        if layer == undefined do throw "layer constructor failed"
        target = layer.layerAsRefTarg
        targetHandle = getHandleByAnim target
        if target == baseRef or (getAnimByHandle targetHandle) != target or not (p3SetSame (refs.dependents target) baseDeps) do throw "layer identity/dependencies unsupported"
        nodeAttempt = true
        n = Box width:1 length:1 height:1
        nodeHandle = getHandleByAnim n
        if not isValidNode n or (getAnimByHandle nodeHandle) != n or objects.count != 1 do throw "node identity/census"
        local beforeLayer = n.layer.layerAsRefTarg
        local defaultBefore = #(); local tempBefore = #()
        if not (baseLayer.nodes &defaultBefore) or not (layer.nodes &tempBefore) do throw "before membership unreadable"
        if beforeLayer != baseRef or defaultBefore.count != 1 or defaultBefore[1] != n or tempBefore.count != 0 do throw "unexpected original membership"
        layer.addNode n
        local movedRef = n.layer.layerAsRefTarg
        local defaultDuring = #(); local tempDuring = #()
        if not (baseLayer.nodes &defaultDuring) or not (layer.nodes &tempDuring) do throw "moved membership unreadable"
        if movedRef != target or movedRef == beforeLayer or defaultDuring.count != 0 or tempDuring.count != 1 or tempDuring[1] != n do throw "membership edit not observed"
        baseLayer.addNode n
        local finalRef = n.layer.layerAsRefTarg
        local defaultAfter = #(); local tempAfter = #()
        if not (baseLayer.nodes &defaultAfter) or not (layer.nodes &tempAfter) do throw "restored membership unreadable"
        if finalRef != beforeLayer or defaultAfter.count != 1 or defaultAfter[1] != n or tempAfter.count != 0 do throw "membership restore failed"
        text += "|beforeDefault=true|movedDifferent=true|memberMove=true|restoredExact=true|nodeHandle="+(nodeHandle as string)+"|layerHandle="+(targetHandle as string)
        outcome = "BOUNDED_MEMBERSHIP_OBSERVED_NOT_ACCEPTANCE"
    )
    catch (text += "|ERROR="+((getCurrentException()) as string))
    try
    (
        if nodeAttempt then
        (
            if n == undefined or nodeHandle == undefined or not isValidNode n do throw "node constructor/identity uncertain"
            if (getHandleByAnim n) != nodeHandle or (getAnimByHandle nodeHandle) != n or objects.count != 1 or selection.count != 0 do throw "node cleanup identity/census"
            if n.children.count != 0 or (n.parent != undefined and n.parent != rootNode) do throw "node hierarchy"
            local users = for o in objects where o.baseObject == n.baseObject collect o
            if users.count != 1 or users[1] != n do throw "shared base/neighbor"
            local nr = n.layer.layerAsRefTarg
            if nr != baseRef and nr != target do throw "node attached to unknown layer"
            delete n
            if isValidNode n or objects.count != 0 do throw "node cleanup unresolved"
            nodeRemoved = true
        )
        else if objects.count == 0 then nodeRemoved = true else throw "node construction ambiguous"
    )
    catch (text += "|NODE_CLEANUP_ERROR="+((getCurrentException()) as string))
    try
    (
        if layerAttempt then
        (
            if layer == undefined or target == undefined or targetHandle == undefined do throw "layer creation identity uncertain"
            if not nodeRemoved or objects.count != 0 or selection.count != 0 or LayerManager.count != 2 do throw "cleanup census"
            if layer.layerAsRefTarg != target or (getAnimByHandle targetHandle) != target do throw "layer target mismatch"
            if (LayerManager.getLayer 0).layerAsRefTarg != baseRef or (getAnimByHandle baseHandle) != baseRef do throw "default ref changed"
            if not (p3SetSame (refs.dependents baseRef) baseDeps) or not (p3SetSame (refs.dependents target) baseDeps) do throw "unexpected dependencies"
            local alias = LayerManager.getLayerFromName label
            local members = #()
            if alias == undefined or alias.layerAsRefTarg != target or layer.name != label do throw "name lookup not exact backing"
            if not (layer.nodes &members) or members.count != 0 or layer.current or layer.getParent() != undefined or layer.getNumChildren() != 0 do throw "layer not empty noncurrent unnested"
            if not (LayerManager.deleteLayerByName label) do throw "layer deletion refused"
            if LayerManager.count != 1 or (LayerManager.getLayerFromName label) != undefined do throw "layer deletion unresolved"
            layerRemoved = true
        )
        else if LayerManager.count == 1 then layerRemoved = true else throw "layer construction ambiguous"
    )
    catch (text += "|LAYER_CLEANUP_ERROR="+((getCurrentException()) as string))
    if not nodeRemoved or not layerRemoved do outcome = "INCOMPLETE_RESIDUE_OR_IDENTITY"
    text += "|outcome="+outcome+"|nodeCleanup="+(nodeRemoved as string)+"|layerCleanup="+(layerRemoved as string)+"|objects="+(objects.count as string)+"|selection="+(selection.count as string)+"|layers="+(LayerManager.count as string)+"|dirtyBefore="+(beforeDirty as string)+"|dirtyAfter="+((getSaveRequired()) as string)
    text
)
