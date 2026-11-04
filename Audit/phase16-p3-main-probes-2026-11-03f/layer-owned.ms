-- Main-only disposable layer comparator probe. Never touches the default layer.
-- Not emitted-wall execution, arbitrary metadata proof, or replay acceptance.
(
    local label = "P3F_Layer_8A71C1"
    local label2 = "P3F_Layer_8A71C1_Renamed"
    local out = "P3_LAYER_OWNED"
    local created = undefined
    local backing = undefined
    local createdHandle = undefined
    local attempted = false
    local removed = false
    local outcome = "INCOMPLETE"
    local root = rootNode
    local defaultLayer = undefined
    local defaultTarget = undefined
    local defaultSnapshot = undefined
    local defaultDeps = undefined
    local dirtyBefore = getSaveRequired()

    fn p3LayerSame a b =
    (
        if classOf a != classOf b then false
        else if classOf a == Array then
        (
            if a.count != b.count then false
            else (local ok = true; for i = 1 to a.count while ok do ok = p3LayerSame a[i] b[i]; ok)
        )
        else a == b
    )
    fn p3LayerDetach value =
    (
        case (classOf value) of
        (
            BooleanClass: #("bool", value)
            Integer: #("integer", value)
            Float: (if value != value or abs value >= 1.0e38 do throw "nonfinite float"; #("float",value))
            Name: #("name", value)
            String: #("string", copy value)
            Color: #("color", value.r, value.g, value.b, value.a)
            default: (throw ("unsupported layer scalar " + ((classOf value) as string)))
        )
    )
    fn p3LayerProps target nested:false =
    (
        local names = getPropNames target
        if names == undefined or names.count > 64 do throw "layer property enumeration unavailable/over limit"
        local result = #()
        for p in names do
        (
            local v = getProperty target p
            if not nested and p == #INodeGIProperties then
                append result #(p, p3LayerProps v nested:true)
            else if not nested and p == #layerAsRefTarg then
            (
                local h = getHandleByAnim v
                if h == undefined or (getAnimByHandle h) != v do throw "backing target handle unavailable"
                append result #(p, #("backing", v, h, classOf v))
            )
            else append result #(p, p3LayerDetach v)
        )
        result
    )
    fn p3LayerSnapshot layer =
    (
        local target = layer.layerAsRefTarg
        if target == undefined do throw "missing backing target"
        local h = getHandleByAnim target
        if h == undefined or (getAnimByHandle h) != target do throw "backing ref/handle mismatch"
        local parent = layer.getParent()
        local childCount = layer.getNumChildren()
        local nodes = #()
        if not (layer.nodes &nodes) do throw "layer membership unavailable"
        if parent != undefined or childCount != 0 or nodes.count != 0 do throw "only empty unnested layers supported"
        #(target, h, p3LayerProps layer, p3LayerProps target, parent, childCount, nodes.count)
    )
    fn p3LayerSameSet a b =
    (
        if a == undefined or b == undefined or a.count != b.count then false
        else (local ok = true; for value in a while ok do if (findItem b value) == 0 do ok = false; ok)
    )

    try
    (
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "scene admission failed"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "units mismatch"
        if LayerManager.count != 1 do throw "requires exactly pre-inspected sole default layer"
        if (LayerManager.getLayerFromName label) != undefined or (LayerManager.getLayerFromName label2) != undefined do throw "probe name already in use"
        defaultLayer = LayerManager.getLayer 0
        if defaultLayer == undefined or defaultLayer.name != "0" or not defaultLayer.current do throw "default/current layer mismatch"
        defaultTarget = defaultLayer.layerAsRefTarg
        defaultSnapshot = p3LayerSnapshot defaultLayer
        defaultDeps = refs.dependents defaultTarget
        if defaultDeps == undefined or defaultDeps.count > 8 or (refs.getNumRefs defaultTarget) != 0 do throw "default dependencies unsupported"
        attempted = true
        created = LayerManager.newLayerFromName label
        if created == undefined do throw "layer constructor returned undefined"
        backing = created.layerAsRefTarg
        createdHandle = getHandleByAnim backing
        if backing == undefined or createdHandle == undefined or (getAnimByHandle createdHandle) != backing do throw "owned target identity unavailable"
        local alias = LayerManager.getLayerFromName label
        if alias == undefined or alias.layerAsRefTarg != backing do throw "owned alias mismatch"
        local distinct = backing != defaultTarget and defaultTarget != backing
        local stable = created.layerAsRefTarg == backing and alias.layerAsRefTarg == backing
        if not distinct or not stable do throw "layer identity controls failed"
        local deps = refs.dependents backing
        if not (p3LayerSameSet deps defaultDeps) or (refs.getNumRefs backing) != 0 do throw "unknown owned-layer dependencies"
        local before = p3LayerSnapshot created
        local repeat = p3LayerSnapshot alias
        if not (p3LayerSame before repeat) do throw "clean snapshot unstable"
        local oldLock = created.lock
        created.lock = not oldLock
        local locked = p3LayerSnapshot created
        local lockDetected = not (p3LayerSame before locked)
        created.lock = oldLock
        if not lockDetected or not (p3LayerSame before (p3LayerSnapshot created)) do throw "lock edit or restoration not observed"
        local gi = created.INodeGIProperties
        local giOld = gi.isGISpecular
        gi.isGISpecular = not giOld
        local giChanged = p3LayerSnapshot created
        local giDetected = not (p3LayerSame before giChanged)
        gi.isGISpecular = giOld
        if not giDetected or not (p3LayerSame before (p3LayerSnapshot created)) do throw "GI edit or restoration not observed"
        local renamed = created.setName label2
        if renamed != true or created.name != label2 or created.layerAsRefTarg != backing do throw "rename not observed with stable identity"
        local renamedSnapshot = p3LayerSnapshot created
        local renameDetected = not (p3LayerSame before renamedSnapshot)
        local restored = created.setName label
        if not renameDetected or restored != true or created.name != label or not (p3LayerSame before (p3LayerSnapshot created)) do throw "rename/restoration failed"
        out += "|distinct=" + (distinct as string) + "|sameLayer=" + (stable as string) + "|snapshotRepeat=true|lockDetected=" + (lockDetected as string) + "|giDetected=" + (giDetected as string) + "|renameDetected=" + (renameDetected as string) + "|backingHandle=" + (createdHandle as string)
        outcome = "BOUNDED_LAYER_OBSERVED_NOT_ACCEPTANCE"
    )
    catch (out += "|ERROR=" + ((getCurrentException()) as string))

    try
    (
        if attempted then
        (
            if created == undefined or backing == undefined or createdHandle == undefined do throw "constructor outcome unknown; leave layer"
            if rootNode != root or objects.count != 0 or selection.count != 0 or LayerManager.count != 2 do throw "unexpected scene/census"
            if created.layerAsRefTarg != backing or (getAnimByHandle createdHandle) != backing or (getHandleByAnim backing) != createdHandle do throw "lost exact layer identity"
            if (LayerManager.getLayer 0).layerAsRefTarg != defaultTarget or not (p3LayerSame defaultSnapshot (p3LayerSnapshot (LayerManager.getLayer 0))) do throw "default layer changed"
            if not (p3LayerSameSet (refs.dependents defaultTarget) defaultDeps) or not (p3LayerSameSet (refs.dependents backing) defaultDeps) do throw "layer dependencies changed/unknown"
            if (refs.getNumRefs backing) != 0 do throw "unexpected owned layer references"
            local actualName = created.name
            if actualName != label and actualName != label2 do throw "unexpected owned layer name"
            local alias = LayerManager.getLayerFromName actualName
            if alias == undefined or alias.layerAsRefTarg != backing do throw "exact lookup mismatch; name alone not authority"
            local members = #()
            if not (created.nodes &members) or members.count != 0 or created.current or created.getParent() != undefined or created.getNumChildren() != 0 do throw "layer not empty/noncurrent/unnested"
            if not (LayerManager.deleteLayerByName actualName) do throw "owned empty layer delete refused"
            if LayerManager.count != 1 or (LayerManager.getLayerFromName actualName) != undefined do throw "layer deletion not confirmed"
            if (LayerManager.getLayer 0).layerAsRefTarg != defaultTarget or not (p3LayerSame defaultSnapshot (p3LayerSnapshot (LayerManager.getLayer 0))) do throw "post-delete default changed"
            removed = true
        )
        else removed = true
    )
    catch (out += "|CLEANUP_ERROR=" + ((getCurrentException()) as string))
    if not removed do outcome = "INCOMPLETE_RESIDUE_OR_IDENTITY"
    out += "|outcome=" + outcome + "|cleanup=" + (removed as string) + "|objects=" + (objects.count as string) + "|selection=" + (selection.count as string) + "|layers=" + (LayerManager.count as string) + "|dirtyBefore=" + (dirtyBefore as string) + "|dirtyAfter=" + ((getSaveRequired()) as string)
    out
)
