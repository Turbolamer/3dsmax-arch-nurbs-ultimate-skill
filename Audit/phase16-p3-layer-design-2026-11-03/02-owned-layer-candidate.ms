-- PREPARED / UNEXECUTED DESIGN SCAFFOLD; NOT APPROVED TO RUN AS-IS.
-- It is too long for the preferred short-call discipline until reviewed/split.
-- Main-only, local controlled empty scene, NOT replay QA.
-- This can set saveRequired and change undo history. No save/reset/dirty clearing.
-- It creates at most one layer and one Box; it changes only those new entities.
-- Main must review all guards and explicitly approve a clean-to-dirty transition.
(
    local allowTemporaryLayerEdits = false -- deliberately fail closed; main may review/change
    local allowCleanToDirty = false -- deliberate second guard for a clean scene
    local allowOwnedNode = false -- optional reassignment leg requires separate review
    local nameA = "P3_LayerProbe_20261103_A_453E"
    local nameB = "P3_LayerProbe_20261103_B_453E"
    local l0 = undefined, r0 = undefined, h0 = undefined, rootH = undefined
    local rootRef = undefined, time0 = undefined, sub0 = undefined, dirty0 = undefined
    local state0 = undefined, deps0 = undefined
    local owned = undefined, rt = undefined, hrt = undefined, layerDeps = undefined
    local originalLock = undefined, originalName = undefined
    local giOriginal = undefined
    local n = undefined, nh = undefined, originalLayerRef = undefined
    local nodeDeps = undefined, baseDeps = undefined, nodeBase = undefined
    local failed = false, nodeRemoved = false, layerRemoved = false
    local layerConstructorAttempted = false, nodeConstructorAttempted = false
    local layerHandleCaptured = false, nodeHandleCaptured = false
    local stage = "preflight"

    fn p3ProbeRequire b message = (if b != true do throw message)
    fn p3ProbeSame a b =
    (
        if classOf a != classOf b then false
        else if classOf a == Array then
        (
            if a.count != b.count then false
            else (local eq = true; for i = 1 to a.count while eq do eq = p3ProbeSame a[i] b[i]; eq)
        )
        else a == b
    )
    fn p3ProbeSetSame a b =
    (
        if (classOf a != Array) or (classOf b != Array) then false
        else if a.count != b.count then false
        else
        (
            local eq = true
            local seenA = #(), seenB = #()
            for v in a while eq do
            (
                if (findItem seenA v) != 0 then eq = false else append seenA v
            )
            for v in b while eq do
            (
                if (findItem seenB v) != 0 then eq = false else append seenB v
            )
            for v in a while eq do if (findItem b v) == 0 do eq = false
            for v in b while eq do if (findItem a v) == 0 do eq = false
            eq
        )
    )
    fn p3ProbeScalar v =
    (
        case (classOf v) of
        (
            BooleanClass: #("bool", v)
            Integer: #("int", v)
            Integer64: #("int64", v)
            Float: (p3ProbeRequire (v == v and abs v < 1.0e38) "nonfinite Float"; #("float", v))
            Double: (p3ProbeRequire (v == v and abs v < 1.0d300) "nonfinite Double"; #("double", v))
            String: #("string", copy v)
            Name: #("name", v)
            Color:
            (
                local rgba = #(v.r, v.g, v.b, v.a)
                for component in rgba do p3ProbeRequire (component == component and abs component < 1.0e38) "nonfinite Color"
                #("color", rgba[1], rgba[2], rgba[3], rgba[4])
            )
            default: throw ("unsupported scalar class: " + ((classOf v) as string))
        )
    )
    fn p3ProbeState lyr =
    (
        p3ProbeRequire (isProperty lyr #name and isProperty lyr #lock and
            isProperty lyr #layerAsRefTarg and isProperty lyr #INodeGIProperties) "required layer reader missing"
        local names = getPropNames lyr
        p3ProbeRequire (classOf names == Array and names.count <= 64) "layer names unsupported"
        local required = #(#on, #lock, #current, #wireColor, #isGIExcluded, #name, #renderable,
            #inheritVisibility, #primaryVisibility, #secondaryVisibility, #receiveShadows, #castShadows,
            #applyAtmospherics, #renderOccluded, #isHidden, #isFrozen, #boxMode, #backfaceCull,
            #allEdges, #vertexTicks, #showTrajectory, #xray, #ignoreExtents, #showFrozenInGray,
            #showVertexColors, #vertexColorsShaded, #visibility, #imageMotionBlurMultiplier,
            #motionBlurOn, #motionBlur, #display, #INodeGIProperties, #layerAsRefTarg)
        p3ProbeRequire (p3ProbeSetSame names required) "layer property-set drift"
        local state = #()
        for p in names where p != #layerAsRefTarg and p != #INodeGIProperties do
            append state #(p, p3ProbeScalar (getProperty lyr p))
        local gi = getProperty lyr #INodeGIProperties
        p3ProbeRequire (gi != undefined) "GI interface unavailable"
        local gis = getPropNames gi
        p3ProbeRequire (classOf gis == Array and gis.count <= 64) "GI names unsupported"
        local requiredGI = #(#isGIExcluded, #isGIOccluder, #isGIReceiver, #isGIDiffuse,
            #isGISpecular, #GIUseGlobalMeshing, #GIMeshingEnabled, #nbGIRefineSteps,
            #nbGIRefineStepsDone, #GIMeshSize, #isGIExcludedFromRegather, #storeIllumToMesh,
            #GIByLayer, #GIRayMult, #GIUseAdaptiveSubdivision, #GIMinMeshSize,
            #GIInitialMeshSize, #GIContrastThreshold)
        p3ProbeRequire (p3ProbeSetSame gis requiredGI) "GI property-set drift"
        local giState = #()
        for p in gis do append giState #(p, p3ProbeScalar (getProperty gi p))
        local backing = getProperty lyr #layerAsRefTarg
        p3ProbeRequire (backing != undefined) "backing reference unavailable"
        local backingNames = getPropNames backing
        local requiredBacking = copy required
        append requiredBacking #degrade
        p3ProbeRequire (classOf backingNames == Array and backingNames.count <= 64 and
            p3ProbeSetSame backingNames requiredBacking) "backing property-set drift"
        local backingState = #()
        for p in backingNames where p != #layerAsRefTarg and p != #INodeGIProperties do
            append backingState #(p, p3ProbeScalar (getProperty backing p))
        local backingGI = getProperty backing #INodeGIProperties
        p3ProbeRequire (backingGI != undefined) "backing GI interface unavailable"
        local backingGINames = getPropNames backingGI
        p3ProbeRequire (classOf backingGINames == Array and backingGINames.count <= 64 and
            p3ProbeSetSame backingGINames requiredGI) "backing GI property-set drift"
        local backingGIState = #()
        for p in backingGINames do append backingGIState #(p, p3ProbeScalar (getProperty backingGI p))
        #(state, giState, backingState, backingGIState)
    )
    fn p3ProbeEnv =
    (
        p3ProbeRequire (rootRef != undefined and (getHandleByAnim rootRef) == rootH and
            (getAnimByHandle rootH) == rootRef and rootNode == rootRef) "root witness changed"
        p3ProbeRequire (maxFileName == "" and maxFilePath == "") "scene path changed"
        p3ProbeRequire (units.SystemType == #millimeters and units.SystemScale == 1.0) "units changed"
        p3ProbeRequire (currentTime == time0 and subObjectLevel == sub0 and selection.count == 0) "time/subobject/selection changed"
        local actual0 = LayerManager.getLayer 0
        p3ProbeRequire (actual0 != undefined and actual0.layerAsRefTarg == r0 and
            (getHandleByAnim r0) == h0 and (getAnimByHandle h0) == r0) "original layer identity changed"
        local cur = LayerManager.current
        p3ProbeRequire (cur != undefined and cur.layerAsRefTarg == r0) "current layer changed"
        p3ProbeRequire (p3ProbeSame state0 (p3ProbeState actual0)) "existing default layer state changed"
        p3ProbeRequire (actual0.getParent() == undefined and actual0.getNumChildren() == 0) "default hierarchy changed"
        local originalMembers = #()
        p3ProbeRequire (actual0.nodes &originalMembers) "default membership reader failed"
        p3ProbeRequire (classOf originalMembers == Array and actual0.getNumNodes() == originalMembers.count) "default membership inconsistent"
        local expectedOriginal = #()
        if n != undefined and isValidNode n and n.layer.layerAsRefTarg == r0 do append expectedOriginal n
        p3ProbeRequire (p3ProbeSetSame originalMembers expectedOriginal) "default layer foreign/ambiguous member"
        local expectedDeps = copy deps0
        if expectedOriginal.count == 1 do append expectedDeps n
        p3ProbeRequire (p3ProbeSetSame (refs.dependents r0) expectedDeps) "default backing dependents changed"
        local expectedCount = if owned == undefined or layerRemoved then 1 else 2
        p3ProbeRequire (LayerManager.count == expectedCount) "layer census changed"
        local expectedNodes = if n != undefined and isValidNode n then 1 else 0
        p3ProbeRequire (objects.count == expectedNodes) "node census changed"
        if expectedNodes == 1 do
        (
            local all = for obj in objects collect obj
            p3ProbeRequire (all.count == 1 and all[1] == n) "foreign node in census"
        )
        true
    )
    fn p3ProbeLayer =
    (
        p3ProbeRequire (owned != undefined and rt != undefined and hrt != undefined) "missing exact owned layer witness"
        p3ProbeRequire (p3ProbeSetSame layerDeps deps0) "unexpected/uncalibrated owned-layer dependents"
        p3ProbeRequire (owned.layerAsRefTarg == rt and (getHandleByAnim rt) == hrt and
            (getAnimByHandle hrt) == rt) "owned layer identity changed"
        local nm = copy owned.name
        p3ProbeRequire (nm == nameA or nm == nameB) "owned layer name unexpected"
        local located = LayerManager.getLayerFromName nm
        p3ProbeRequire (located != undefined and located.layerAsRefTarg == rt) "lookup is not the retained layer"
        p3ProbeRequire (not owned.current and owned.getParent() == undefined and owned.getNumChildren() == 0) "owned layer hierarchy/current changed"
        local members = #()
        p3ProbeRequire (owned.nodes &members) "owned layer membership reader failed"
        p3ProbeRequire (classOf members == Array and owned.getNumNodes() == members.count) "owned membership inconsistent"
        local expected = #()
        if n != undefined and isValidNode n and n.layer.layerAsRefTarg == rt do append expected n
        p3ProbeRequire (p3ProbeSetSame members expected) "foreign/ambiguous layer member"
        local depExpected = copy layerDeps
        if expected.count == 1 do append depExpected n
        p3ProbeRequire (p3ProbeSetSame (refs.dependents rt) depExpected) "owned layer dependencies changed"
        true
    )
    fn p3ProbeNode =
    (
        p3ProbeRequire (n != undefined and nh != undefined and isValidNode n) "exact node unavailable"
        p3ProbeRequire ((getHandleByAnim n) == nh and (getAnimByHandle nh) == n) "node handle mismatch"
        p3ProbeRequire ((n.parent == undefined or n.parent == rootRef) and n.children.count == 0) "node hierarchy changed"
        p3ProbeRequire (n.material == undefined and n.baseObject == nodeBase) "node material/base changed"
        p3ProbeRequire (p3ProbeSetSame (refs.dependents n) nodeDeps) "node dependents changed"
        p3ProbeRequire (p3ProbeSetSame (refs.dependents nodeBase) baseDeps) "base dependents changed"
        true
    )

    try
    (
        dirty0 = getSaveRequired()
        p3ProbeRequire allowTemporaryLayerEdits "temporary layer edits not explicitly enabled"
        p3ProbeRequire (dirty0 or allowCleanToDirty) "clean scene: explicit allowCleanToDirty required"
        p3ProbeRequire (objects.count == 0 and selection.count == 0) "requires empty scene and selection"
        p3ProbeRequire (maxFileName == "" and maxFilePath == "") "requires unnamed scene"
        p3ProbeRequire (units.SystemType == #millimeters and units.SystemScale == 1.0) "requires mm/1"
        p3ProbeRequire (LayerManager.count == 1) "requires only the default layer"
        rootRef = rootNode; rootH = getHandleByAnim rootRef
        time0 = currentTime; sub0 = subObjectLevel
        p3ProbeRequire (rootH != undefined and (getAnimByHandle rootH) == rootRef) "root not comparable"
        l0 = LayerManager.getLayer 0
        p3ProbeRequire (l0 != undefined and l0.name == "0") "default layer not available"
        r0 = l0.layerAsRefTarg; h0 = getHandleByAnim r0
        p3ProbeRequire (r0 != undefined and h0 != undefined and (getAnimByHandle h0) == r0) "default reference not comparable"
        local currentLayer = LayerManager.current
        p3ProbeRequire (currentLayer != undefined and currentLayer.layerAsRefTarg == r0) "default not current"
        p3ProbeRequire (l0.getParent() == undefined and l0.getNumChildren() == 0 and l0.getNumNodes() == 0) "unexpected default hierarchy/members"
        deps0 = refs.dependents r0
        p3ProbeRequire (classOf deps0 == Array and deps0.count == 2 and (findItem deps0 rootRef) > 0) "unexpected default backing dependents"
        local bogusThrow = false
        try (getProperty l0 #P3LayerBogus_453E) catch (bogusThrow = true)
        p3ProbeRequire (isProperty l0 #name and not (isProperty l0 #P3LayerBogus_453E) and bogusThrow) "real/bogus controls failed"
        local gi0 = l0.INodeGIProperties
        local bogusGIThrow = false, bogusBackingThrow = false
        try (getProperty gi0 #P3BogusGI_453E) catch (bogusGIThrow = true)
        try (getProperty r0 #P3BogusBacking_453E) catch (bogusBackingThrow = true)
        p3ProbeRequire (isProperty gi0 #isGIOccluder and not (isProperty gi0 #P3BogusGI_453E) and bogusGIThrow) "GI real/bogus controls failed"
        p3ProbeRequire (isProperty r0 #degrade and not (isProperty r0 #P3BogusBacking_453E) and bogusBackingThrow) "backing real/bogus controls failed"
        state0 = p3ProbeState l0
        p3ProbeRequire (p3ProbeSame state0 (p3ProbeState l0)) "default scalar snapshot unstable"
        p3ProbeRequire ((LayerManager.getLayerFromName nameA) == undefined and
            (LayerManager.getLayerFromName nameB) == undefined) "probe name collision"
        p3ProbeEnv()

        stage = "create-owned-layer"
        layerConstructorAttempted = true
        owned = LayerManager.newLayerFromName nameA
        p3ProbeRequire (owned != undefined) "layer constructor returned undefined"
        rt = owned.layerAsRefTarg; hrt = getHandleByAnim rt
        p3ProbeRequire (rt != undefined and hrt != undefined and (getAnimByHandle hrt) == rt) "owned backing identity unavailable"
        layerHandleCaptured = true
        originalLock = owned.lock; originalName = copy owned.name
        p3ProbeRequire (classOf originalLock == BooleanClass and originalName == nameA) "unusable owned-layer state"
        layerDeps = refs.dependents rt
        p3ProbeRequire (p3ProbeSetSame layerDeps deps0) "new-layer dependents differ from reviewed default dependents"
        p3ProbeEnv(); p3ProbeLayer()
        local eqLayers = l0 == owned
        local eqLayersReverse = owned == l0
        local eqRefs = r0 == rt
        local eqRefsReverse = rt == r0
        local eqHandles = h0 == hrt
        print ("P3_LAYER_ID|sameInterface=" + (eqLayers as string) + "|reverseInterface=" + (eqLayersReverse as string) +
            "|sameBacking=" + (eqRefs as string) + "|reverseBacking=" + (eqRefsReverse as string) + "|sameHandle=" + (eqHandles as string))
        p3ProbeRequire (not eqLayers and not eqLayersReverse and not eqRefs and not eqRefsReverse and not eqHandles) "distinct-layer negative control failed"
        p3ProbeRequire (owned == (LayerManager.getLayerFromName nameA) and
            owned.layerAsRefTarg == (LayerManager.getLayerFromName nameA).layerAsRefTarg) "same-layer positive control failed"
        local baseline = p3ProbeState owned
        p3ProbeRequire (p3ProbeSame baseline (p3ProbeState owned)) "owned layer clean snapshot unstable"

        stage = "owned-lock-edit"
        p3ProbeEnv(); p3ProbeLayer()
        owned.lock = not originalLock
        p3ProbeRequire (owned.lock != originalLock and not (p3ProbeSame baseline (p3ProbeState owned))) "lock edit not detected"
        owned.lock = originalLock
        p3ProbeRequire (owned.lock == originalLock and p3ProbeSame baseline (p3ProbeState owned)) "lock restore mismatch"
        print "P3_LAYER_LOCK|cleanEqual=true|changedDetected=true|restoredEqual=true"

        stage = "owned-nested-gi-edit"
        p3ProbeEnv(); p3ProbeLayer()
        local gi = owned.INodeGIProperties
        giOriginal = getProperty gi #isGIOccluder
        p3ProbeRequire (classOf giOriginal == BooleanClass) "owned GI boolean unavailable"
        setProperty gi #isGIOccluder (not giOriginal)
        p3ProbeRequire ((getProperty gi #isGIOccluder) != giOriginal and
            not (p3ProbeSame baseline (p3ProbeState owned))) "nested GI edit not detected"
        setProperty gi #isGIOccluder giOriginal
        p3ProbeRequire ((getProperty gi #isGIOccluder) == giOriginal and
            p3ProbeSame baseline (p3ProbeState owned)) "nested GI restore mismatch"
        print "P3_LAYER_GI|changedDetected=true|restoredEqual=true"

        stage = "owned-rename"
        p3ProbeEnv(); p3ProbeLayer()
        p3ProbeRequire (owned.setName nameB) "rename refused"
        p3ProbeLayer()
        p3ProbeRequire (owned.name == nameB and not (p3ProbeSame baseline (p3ProbeState owned)) and
            (getAnimByHandle hrt) == rt) "rename not detected or identity changed"
        p3ProbeRequire ((LayerManager.getLayerFromName nameA) == undefined) "old name unexpectedly occupied"
        p3ProbeRequire (owned.setName originalName) "name restore refused"
        p3ProbeRequire (p3ProbeSame baseline (p3ProbeState owned)) "name restore mismatch"
        print "P3_LAYER_RENAME|changedDetected=true|backingIdentityStable=true|restoredEqual=true"

        if allowOwnedNode then
        (
            stage = "create-owned-node"
            p3ProbeEnv(); p3ProbeLayer()
            nodeConstructorAttempted = true
            n = Box width:1.0 length:1.0 height:1.0
            nh = getHandleByAnim n
            p3ProbeRequire (isValidNode n and nh != undefined and (getAnimByHandle nh) == n) "new node identity unavailable"
            nodeHandleCaptured = true
            originalLayerRef = n.layer.layerAsRefTarg
            p3ProbeRequire (originalLayerRef == r0) "new node did not start on original layer"
            nodeBase = n.baseObject; nodeDeps = refs.dependents n; baseDeps = refs.dependents nodeBase
            p3ProbeRequire (classOf nodeDeps == Array and nodeDeps.count <= 1 and
                (nodeDeps.count == 0 or nodeDeps[1] == rootRef)) "unexpected node dependents"
            p3ProbeRequire (classOf baseDeps == Array and baseDeps.count == 1 and baseDeps[1] == n) "unexpected base dependents"
            p3ProbeEnv(); p3ProbeLayer(); p3ProbeNode()

            stage = "owned-node-reassignment"
            owned.addNode n
            p3ProbeEnv(); p3ProbeLayer(); p3ProbeNode()
            p3ProbeRequire (n.layer.layerAsRefTarg == rt and n.layer.layerAsRefTarg != originalLayerRef) "reassignment not detected"
            l0.addNode n
            p3ProbeEnv(); p3ProbeLayer(); p3ProbeNode()
            p3ProbeRequire (n.layer.layerAsRefTarg == originalLayerRef) "original node layer not restored"
            print "P3_LAYER_REASSIGN|changedDetected=true|originalReferenceRestored=true"
        )
        else print "P3_LAYER_REASSIGN|NOT_RUN|optional owned-node leg disabled"
        stage = "tests-complete"
    )
    catch (failed = true; print ("P3_LAYER_TEST_THROW|stage=" + stage + "|" + (getCurrentException() as string)))

    -- No name-based adoption or deletion. On ANY uncertainty leave exact residue.
    try
    (
        if n != undefined and isValidNode n do
        (
            p3ProbeEnv(); p3ProbeNode()
            p3ProbeRequire (owned != undefined and originalLayerRef == r0) "original layer unresolved"
            p3ProbeLayer()
            if n.layer.layerAsRefTarg != originalLayerRef do
            (
                p3ProbeRequire (n.layer.layerAsRefTarg == rt) "node assigned to foreign layer"
                l0.addNode n
                p3ProbeRequire (n.layer.layerAsRefTarg == originalLayerRef) "node layer restore failed"
            )
            p3ProbeEnv(); p3ProbeNode()
            delete n
            p3ProbeRequire (not isValidNode n and objects.count == 0) "exact node removal unverified"
            nodeRemoved = true
        )
    )
    catch (failed = true; print ("P3_LAYER_NODE_RESIDUE|handle=" + (nh as string) + "|" + (getCurrentException() as string)))

    try
    (
        if owned != undefined and not layerRemoved do
        (
            p3ProbeEnv(); p3ProbeLayer()
            p3ProbeRequire (objects.count == 0) "node remains; preserve layer"
            p3ProbeRequire (classOf originalLock == BooleanClass and originalName == nameA) "initial layer state unavailable"
            if owned.lock != originalLock do owned.lock = originalLock
            p3ProbeRequire (owned.lock == originalLock) "lock restore failed"
            if giOriginal != undefined do
            (
                local cleanupGI = owned.INodeGIProperties
                if (getProperty cleanupGI #isGIOccluder) != giOriginal do setProperty cleanupGI #isGIOccluder giOriginal
                p3ProbeRequire ((getProperty cleanupGI #isGIOccluder) == giOriginal) "GI restore failed"
            )
            if owned.name != originalName do
            (
                local occupant = LayerManager.getLayerFromName originalName
                p3ProbeRequire (occupant == undefined or occupant.layerAsRefTarg == rt) "original name occupied"
                p3ProbeRequire (owned.setName originalName) "name restore failed"
            )
            p3ProbeEnv(); p3ProbeLayer()
            p3ProbeRequire (owned.getNumNodes() == 0 and owned.getNumChildren() == 0 and not owned.current) "layer not empty/noncurrent"
            -- Name only transports the deletion request after exact identity and membership proof.
            p3ProbeRequire (LayerManager.deleteLayerByName originalName) "exactly resolved layer deletion failed"
            layerRemoved = true
            p3ProbeRequire (LayerManager.count == 1 and (LayerManager.getLayerFromName originalName) == undefined) "layer removal unverified"
        )
    )
    catch (failed = true; print ("P3_LAYER_LAYER_RESIDUE|handle=" + (hrt as string) + "|" + (getCurrentException() as string)))

    try
    (
        if state0 != undefined do
        (
            p3ProbeEnv()
            p3ProbeRequire (objects.count == 0 and LayerManager.count == 1) "final census not restored"
            p3ProbeRequire (p3ProbeSetSame (refs.dependents r0) deps0) "default backing dependencies changed"
        )
    )
    catch (failed = true; print ("P3_LAYER_FINAL_INCOMPLETE|" + (getCurrentException() as string)))
    if layerConstructorAttempted and not layerRemoved do
        print ("P3_LAYER_OWNED_RESIDUE_OR_UNKNOWN|kind=layer|refReturned=" + ((owned != undefined) as string) +
            "|handleCaptured=" + (layerHandleCaptured as string) + "|handle=" + (hrt as string))
    if nodeConstructorAttempted and not nodeRemoved do
        print ("P3_LAYER_OWNED_RESIDUE_OR_UNKNOWN|kind=node|refReturned=" + ((n != undefined) as string) +
            "|handleCaptured=" + (nodeHandleCaptured as string) + "|handle=" + (nh as string))
    print ("P3_LAYER_END|failed=" + (failed as string) + "|nodeRemoved=" + (nodeRemoved as string) +
        "|layerRemoved=" + (layerRemoved as string) + "|objects=" + (objects.count as string) +
        "|layers=" + (LayerManager.count as string) + "|nodeHandle=" + (nh as string) +
        "|layerHandle=" + (hrt as string) + "|dirtyBefore=" + (dirty0 as string) +
        "|dirtyAfter=" + ((getSaveRequired()) as string) + "|note=unknown-constructor-residue-possible")
)
