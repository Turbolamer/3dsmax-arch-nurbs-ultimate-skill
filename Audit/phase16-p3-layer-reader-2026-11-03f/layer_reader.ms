-- CANDIDATE ONLY. Local helper definitions to paste INSIDE a fileIn wrapper.
-- Not run in Max. Every outcome remains INCOMPLETE; never use as replay authority.
-- Profiles are the exact observed 2026.3.2 getPropNames sets, not universal metadata.
local p3LayerInterfaceProfile = #(
    #(#on, #bool), #(#Lock, #bool), #(#current, #bool), #(#wireColor, #color),
    #(#isGIExcluded, #bool), #(#name, #string), #(#renderable, #bool),
    #(#inheritVisibility, #bool), #(#primaryVisibility, #bool),
    #(#secondaryVisibility, #bool), #(#receiveshadows, #bool), #(#castShadows, #bool),
    #(#applyAtmospherics, #bool), #(#renderOccluded, #bool), #(#ishidden, #bool),
    #(#isfrozen, #bool), #(#boxmode, #bool), #(#backfacecull, #bool),
    #(#alledges, #bool), #(#vertexTicks, #bool), #(#showTrajectory, #bool),
    #(#xray, #bool), #(#ignoreExtents, #bool), #(#showFrozenInGray, #bool),
    #(#showVertexColors, #bool), #(#vertexColorsShaded, #bool),
    #(#visibility, #float), #(#imageMotionBlurMultiplier, #float),
    #(#motionBlurOn, #bool), #(#motionblur, #name), #(#display, #name),
    #(#INodeGIProperties, #gi), #(#layerAsRefTarg, #backing)
)
local p3LayerBackingProfile = #(
    #(#on, #bool), #(#Lock, #bool), #(#current, #bool), #(#wireColor, #color),
    #(#isGIExcluded, #bool), #(#name, #string), #(#renderable, #bool),
    #(#inheritVisibility, #bool), #(#primaryVisibility, #bool),
    #(#secondaryVisibility, #bool), #(#receiveshadows, #bool), #(#castShadows, #bool),
    #(#applyAtmospherics, #bool), #(#renderOccluded, #bool), #(#ishidden, #bool),
    #(#isfrozen, #bool), #(#boxmode, #bool), #(#backfacecull, #bool),
    #(#alledges, #bool), #(#vertexTicks, #bool), #(#showTrajectory, #bool),
    #(#xray, #bool), #(#ignoreExtents, #bool), #(#showFrozenInGray, #bool),
    #(#showVertexColors, #bool), #(#vertexColorsShaded, #bool),
    #(#visibility, #float), #(#imageMotionBlurMultiplier, #float),
    #(#motionBlurOn, #bool), #(#motionblur, #name), #(#display, #name),
    #(#INodeGIProperties, #gi), #(#layerAsRefTarg, #backing), #(#degrade, #bool)
)
local p3LayerGIProfile = #(
    #(#isGIExcluded, #bool), #(#isGIOccluder, #bool), #(#isGIReceiver, #bool),
    #(#isGIDiffuse, #bool), #(#isGISpecular, #bool), #(#GIUseGlobalMeshing, #bool),
    #(#GIMeshingEnabled, #bool), #(#nbGIRefineSteps, #integer),
    #(#nbGIRefineStepsDone, #integer), #(#GIMeshSize, #float),
    #(#isGIExcludedFromRegather, #bool), #(#storeIllumToMesh, #bool),
    #(#GIByLayer, #bool), #(#GIRayMult, #float), #(#GIUseAdaptiveSubdivision, #bool),
    #(#GIMinMeshSize, #float), #(#GIInitialMeshSize, #float), #(#GIContrastThreshold, #float)
)

fn p3LayerRequire condition reason =
(
    if condition != true do throw ("P3_LAYER_INCOMPLETE|" + reason)
    true
)
fn p3LayerExactRef value =
(
    p3LayerRequire (value != undefined) "undefined exact reference"
    local h = getHandleByAnim value
    p3LayerRequire (h != undefined) "reference has no operational handle"
    local resolved = getAnimByHandle h
    p3LayerRequire (resolved == value and (getHandleByAnim resolved) == h) "reference/handle roundtrip failed"
    #(value, h, classOf value)
)
fn p3LayerFinite value =
(
    local cls = classOf value
    p3LayerRequire (cls == Float or cls == Integer) "unsupported numeric component type"
    p3LayerRequire (value == value and abs value < 1.0e38) "nonfinite/out-of-range numeric value"
    value
)
fn p3LayerDetach value kind =
(
    case kind of
    (
        #bool: (p3LayerRequire ((classOf value) == BooleanClass) "expected BooleanClass"; #("bool", value))
        #integer: (p3LayerRequire ((classOf value) == Integer) "expected Integer"; #("integer", value))
        #float: (p3LayerRequire ((classOf value) == Float) "expected Float"; #("float", (p3LayerFinite value)))
        #name: (p3LayerRequire ((classOf value) == Name) "expected Name"; #("name", value))
        #string: (p3LayerRequire ((classOf value) == String and value.count <= 4096) "expected bounded String"; #("string", copy value))
        #color:
        (
            p3LayerRequire ((classOf value) == Color) "expected Color"
            #("color", (p3LayerFinite value.r), (p3LayerFinite value.g), (p3LayerFinite value.b), (p3LayerFinite value.a))
        )
        default: (throw "P3_LAYER_INCOMPLETE|unsupported detached type")
    )
)
fn p3LayerCheckNames target profile =
(
    local names = getPropNames target
    p3LayerRequire ((classOf names) == Array and names.count == profile.count and names.count <= 34) "missing/extra/unreadable property enumeration"
    for p in names do
    (
        p3LayerRequire ((classOf p) == Name) "invalid property name type"
        local hits = 0
        for spec in profile do if spec[1] == p do hits += 1
        p3LayerRequire (hits == 1) "unknown property"
        local duplicates = 0
        for other in names do if other == p do duplicates += 1
        p3LayerRequire (duplicates == 1) "duplicate property"
    )
    for spec in profile do p3LayerRequire ((findItem names spec[1]) != 0) "expected property missing"
    true
)
fn p3LayerReadGI gi =
(
    p3LayerRequire ((classOf gi) == MixinInterface) "unexpected nested GI interface type"
    p3LayerCheckNames gi p3LayerGIProfile
    for spec in p3LayerGIProfile collect #(spec[1], p3LayerDetach (getProperty gi spec[1]) spec[2])
)
fn p3LayerReadProps target profile expectedBacking =
(
    p3LayerCheckNames target profile
    for spec in profile collect
    (
        local value = getProperty target spec[1]
        local detached = undefined
        if spec[2] == #gi then detached = #("gi", p3LayerReadGI value)
        else if spec[2] == #backing then
        (
            p3LayerRequire (value == expectedBacking) "property backing changed or substituted"
            -- Exact reference record ONLY. Do not recurse into the backing property.
            detached = #("backing", p3LayerExactRef value)
        )
        else detached = p3LayerDetach value spec[2]
        #(spec[1], detached)
    )
)
fn p3LayerTreeEqual a b depth:0 =
(
    p3LayerRequire (depth <= 12) "comparison nesting ceiling"
    if classOf a != classOf b then false
    else if classOf a == Array then
    (
        p3LayerRequire (a.count <= 64 and b.count <= 64) "comparison array ceiling"
        if a.count != b.count then false
        else (local ok = true; for i = 1 to a.count while ok do ok = p3LayerTreeEqual a[i] b[i] depth:(depth+1); ok)
    )
    else a == b
)
fn p3LayerReadOnce node expectedNode expectedBacking expectedRoot expectedManager =
(
    p3LayerRequire (isValidNode node and node == expectedNode) "node witness changed"
    p3LayerRequire (rootNode == expectedRoot) "root witness changed"
    p3LayerRequire (LayerManager.count == 1) "non-standalone layer census"
    p3LayerRequire (objects.count == 1) "non-standalone scene census"
    local sceneNodes = for other in objects collect other
    p3LayerRequire (sceneNodes.count == 1 and sceneNodes[1] == expectedNode) "scene node identity mismatch"
    local nodeRef = p3LayerExactRef node
    local rootRef = p3LayerExactRef expectedRoot
    local backingRef = p3LayerExactRef expectedBacking
    local managerRef = p3LayerExactRef expectedManager
    p3LayerRequire (((classOf expectedBacking) as string) == "Base_LayerBase_Layer") "unknown backing class"
    p3LayerRequire (expectedRoot != expectedManager and node != expectedManager and expectedBacking != expectedManager and node != expectedRoot and node != expectedBacking and expectedRoot != expectedBacking) "invalid dependency witnesses"
    local layer = node.layer
    p3LayerRequire ((classOf layer) == MixinInterface) "unknown node.layer interface type"
    local actualBacking = layer.layerAsRefTarg
    local actualBackingRef = p3LayerExactRef actualBacking
    p3LayerRequire (actualBacking == expectedBacking and p3LayerTreeEqual actualBackingRef backingRef) "node.layer backing ref/handle mismatch"
    local defaultLayer = LayerManager.getLayer 0
    p3LayerRequire (defaultLayer != undefined and defaultLayer.layerAsRefTarg == expectedBacking) "default layer backing mismatch"
    local parent = layer.getParent()
    local children = layer.getNumChildren()
    p3LayerRequire (parent == undefined and children == 0) "layer hierarchy unsupported"
    local members = #()
    p3LayerRequire (layer.nodes &members) "layer membership unavailable"
    p3LayerRequire ((classOf members) == Array and members.count == 1 and members[1] == expectedNode) "foreign/missing/duplicate layer member"
    local memberRef = p3LayerExactRef members[1]
    p3LayerRequire (p3LayerTreeEqual nodeRef memberRef) "member/node identity differs"
    p3LayerRequire ((refs.getNumRefs expectedBacking) == 0) "backing outgoing references unsupported"
    local deps = refs.dependents expectedBacking
    p3LayerRequire ((classOf deps) == Array and deps.count >= 2 and deps.count <= 3) "dependency count unsupported"
    local rootHits = 0
    local managerHits = 0
    local nodeHits = 0
    for dep in deps do
    (
        if dep == expectedRoot then rootHits += 1
        else if dep == expectedManager then managerHits += 1
        else if dep == expectedNode then nodeHits += 1
        else throw "P3_LAYER_INCOMPLETE|foreign dependency"
    )
    p3LayerRequire (rootHits == 1 and managerHits == 1 and nodeHits <= 1) "missing/duplicate dependency"
    local interfaceProps = p3LayerReadProps layer p3LayerInterfaceProfile expectedBacking
    local backingProps = p3LayerReadProps expectedBacking p3LayerBackingProfile expectedBacking
    -- The names are detached state only, NEVER a lookup or ownership authority.
    -- No recursion through layerAsRefTarg: its exact identity is recorded above.
    #(nodeRef, rootRef, backingRef, managerRef, #("parent", "undefined"),
      #("children", children), #("members", #(memberRef)),
      #("dependencies", rootRef, managerRef, nodeHits), interfaceProps, backingProps)
)
fn p3LayerSnapshot node expectedNode expectedBacking expectedRoot expectedManager =
(
    local output = #("P3_LAYER_SNAPSHOT_1", "INCOMPLETE", "READ_FAILED")
    try
    (
        local a = p3LayerReadOnce node expectedNode expectedBacking expectedRoot expectedManager
        local b = p3LayerReadOnce node expectedNode expectedBacking expectedRoot expectedManager
        p3LayerRequire (p3LayerTreeEqual a b) "observation changed during double read"
        output = #("P3_LAYER_SNAPSHOT_1", "INCOMPLETE", "PARTIAL_CAPTURE_ONLY", a)
    )
    catch
    (
        output = #("P3_LAYER_SNAPSHOT_1", "INCOMPLETE", "READ_FAILED", (getCurrentException() as string))
    )
    output
)
fn p3LayerValidateScalarRecord record kind =
(
    p3LayerRequire ((classOf record) == Array) "malformed detached value"
    if kind == #color then
    (
        p3LayerRequire (record.count == 5 and record[1] == "color") "malformed detached color"
        for index = 2 to 5 do p3LayerFinite record[index]
    )
    else
    (
        p3LayerRequire (record.count == 2) "malformed detached scalar"
        p3LayerRequire (p3LayerTreeEqual record (p3LayerDetach record[2] kind)) "bad scalar tag/type/value"
    )
    true
)
fn p3LayerValidateGIRecord entries =
(
    p3LayerRequire ((classOf entries) == Array and entries.count == p3LayerGIProfile.count) "malformed GI entries"
    for index = 1 to p3LayerGIProfile.count do
    (
        local entry = entries[index]
        local spec = p3LayerGIProfile[index]
        p3LayerRequire ((classOf entry) == Array and entry.count == 2 and entry[1] == spec[1]) "missing/reordered GI property"
        p3LayerValidateScalarRecord entry[2] spec[2]
    )
    true
)
fn p3LayerValidatePropRecords entries profile backingRef =
(
    p3LayerRequire ((classOf entries) == Array and entries.count == profile.count) "malformed property entries"
    for index = 1 to profile.count do
    (
        local entry = entries[index]
        local spec = profile[index]
        p3LayerRequire ((classOf entry) == Array and entry.count == 2 and entry[1] == spec[1]) "missing/reordered property"
        local value = entry[2]
        if spec[2] == #gi then
        (
            p3LayerRequire ((classOf value) == Array and value.count == 2 and value[1] == "gi") "malformed nested GI"
            p3LayerValidateGIRecord value[2]
        )
        else if spec[2] == #backing then
        (
            p3LayerRequire ((classOf value) == Array and value.count == 2 and value[1] == "backing") "malformed backing record"
            p3LayerRequire (p3LayerTreeEqual value[2] backingRef) "backing record mismatch"
        )
        else p3LayerValidateScalarRecord value spec[2]
    )
    true
)
fn p3LayerValidatePayload payload =
(
    p3LayerRequire ((classOf payload) == Array and payload.count == 10) "malformed partial payload"
    for index = 1 to 4 do
    (
        local recorded = payload[index]
        p3LayerRequire ((classOf recorded) == Array and recorded.count == 3) "malformed exact reference record"
        p3LayerRequire (p3LayerTreeEqual recorded (p3LayerExactRef recorded[1])) "stale exact reference record"
    )
    p3LayerRequire (isValidNode payload[1][1]) "node reference is no longer valid"
    p3LayerRequire (p3LayerTreeEqual payload[5] #("parent", "undefined")) "invalid parent record"
    p3LayerRequire (p3LayerTreeEqual payload[6] #("children", 0)) "invalid children record"
    p3LayerRequire ((classOf payload[7]) == Array and payload[7].count == 2 and payload[7][1] == "members") "malformed membership record"
    local memberRecords = payload[7][2]
    p3LayerRequire ((classOf memberRecords) == Array and memberRecords.count == 1) "malformed membership list"
    p3LayerRequire (p3LayerTreeEqual memberRecords[1] payload[1]) "member exact reference mismatch"
    local deps = payload[8]
    p3LayerRequire ((classOf deps) == Array and deps.count == 4 and deps[1] == "dependencies") "malformed dependency record"
    p3LayerRequire (p3LayerTreeEqual deps[2] payload[2] and p3LayerTreeEqual deps[3] payload[4]) "dependency witnesses differ"
    p3LayerRequire ((classOf deps[4]) == Integer and (deps[4] == 0 or deps[4] == 1)) "malformed member dependency count"
    p3LayerValidatePropRecords payload[9] p3LayerInterfaceProfile payload[3]
    p3LayerValidatePropRecords payload[10] p3LayerBackingProfile payload[3]
    true
)
fn p3LayerSame a b =
(
    local output = #("P3_LAYER_COMPARE_1", "INCOMPLETE", "UNCOMPARABLE")
    try
    (
        p3LayerRequire ((classOf a) == Array and (classOf b) == Array and a.count == 4 and b.count == 4) "malformed snapshots"
        p3LayerRequire (a[1] == "P3_LAYER_SNAPSHOT_1" and b[1] == "P3_LAYER_SNAPSHOT_1" and a[2] == "INCOMPLETE" and b[2] == "INCOMPLETE") "snapshot status invalid"
        p3LayerRequire (a[3] == "PARTIAL_CAPTURE_ONLY" and b[3] == "PARTIAL_CAPTURE_ONLY") "snapshot capture failed"
        p3LayerValidatePayload a[4]
        p3LayerValidatePayload b[4]
        local equal = p3LayerTreeEqual a[4] b[4]
        output = #("P3_LAYER_COMPARE_1", "INCOMPLETE", if equal then "OBSERVED_MATCH" else "OBSERVED_DIFFERENT")
    )
    catch (output = #("P3_LAYER_COMPARE_1", "INCOMPLETE", "UNCOMPARABLE"))
    output
)
