-- OFFLINE TEXT ONLY: not parsed, executed, timed, installed, or integrated.
-- Insert these LOCAL definitions into a reviewed enclosing MAXScript scope only.
-- No successful result authorizes a baseline, construction, cleanup, or replay.
-- Witnesses are independently retained #(exactReference, capturedHandle) pairs.

local p31InterfaceProfile = #(
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
local p31BackingProfile = #(
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
local p31GIProfile = #(
    #(#isGIExcluded, #bool), #(#isGIOccluder, #bool), #(#isGIReceiver, #bool),
    #(#isGIDiffuse, #bool), #(#isGISpecular, #bool), #(#GIUseGlobalMeshing, #bool),
    #(#GIMeshingEnabled, #bool), #(#nbGIRefineSteps, #integer),
    #(#nbGIRefineStepsDone, #integer), #(#GIMeshSize, #float),
    #(#isGIExcludedFromRegather, #bool), #(#storeIllumToMesh, #bool),
    #(#GIByLayer, #bool), #(#GIRayMult, #float), #(#GIUseAdaptiveSubdivision, #bool),
    #(#GIMinMeshSize, #float), #(#GIInitialMeshSize, #float), #(#GIContrastThreshold, #float)
)

fn p31Require condition reason =
(
    if condition != true do throw ("P31_LAYER_INCOMPLETE|" + reason)
    true
)

-- This is the only helper using anim-handle APIs. MixinInterface is rejected
-- BEFORE either API call; callers pass actual nodes or retained backing targets.
fn p31ExactWitness witness =
(
    p31Require ((classOf witness) == Array and witness.count == 2) "bad witness shape"
    local value = witness[1]
    local h = witness[2]
    p31Require (value != undefined and h != undefined and h != 0) "null witness"
    p31Require ((classOf value) != MixinInterface) "mixin is not an anim target"
    p31Require ((getHandleByAnim value) == h) "captured handle changed"
    local resolved = getAnimByHandle h
    p31Require (resolved != undefined and resolved == value) "handle did not resolve to exact reference"
    p31Require ((getHandleByAnim resolved) == h) "resolved handle changed"
    true
)

fn p31FiniteFloat value =
(
    p31Require ((classOf value) == Float) "expected Float"
    p31Require (value == value and abs value < 1.0e38) "nonfinite or out-of-range Float"
    value
)

fn p31ColorComponent value =
(
    local cls = classOf value
    p31Require (cls == Integer or cls == Float) "unsupported color component"
    if cls == Float do p31FiniteFloat value
    value
)

fn p31Detach value kind =
(
    case kind of
    (
        #bool: (p31Require ((classOf value) == BooleanClass) "expected bool"; #("bool", value))
        #integer: (p31Require ((classOf value) == Integer) "expected integer"; #("integer", value))
        #float: #("float", (p31FiniteFloat value))
        #name: (p31Require ((classOf value) == Name) "expected Name"; #("name", value))
        #string:
        (
            p31Require ((classOf value) == String and value.count <= 4096) "expected bounded String"
            #("string", copy value)
        )
        #color:
        (
            p31Require ((classOf value) == Color) "expected Color"
            #("color", (p31ColorComponent value.r), (p31ColorComponent value.g),
                (p31ColorComponent value.b), (p31ColorComponent value.a))
        )
        default: throw "P31_LAYER_INCOMPLETE|unknown scalar kind"
    )
)

fn p31CheckProfile target profile =
(
    local names = getPropNames target
    p31Require ((classOf names) == Array and names.count == profile.count and names.count <= 34) "property enumeration unavailable or drifted"
    for p in names do
    (
        p31Require ((classOf p) == Name) "unknown property-name type"
        local hits = 0
        for spec in profile do if spec[1] == p do hits += 1
        p31Require (hits == 1) "unknown or ambiguous property"
        local duplicates = 0
        for other in names do if other == p do duplicates += 1
        p31Require (duplicates == 1) "duplicate property name"
    )
    for spec in profile do p31Require ((findItem names spec[1]) != 0) "required property missing"
    true
)

fn p31ReadGI gi =
(
    p31Require ((classOf gi) == MixinInterface) "GI interface missing or unknown"
    p31CheckProfile gi p31GIProfile
    for spec in p31GIProfile collect #(spec[1], (p31Detach (getProperty gi spec[1]) spec[2]))
)

fn p31ReadProperties target profile backingWitness =
(
    p31CheckProfile target profile
    for spec in profile collect
    (
        local value = getProperty target spec[1]
        local detached = undefined
        if spec[2] == #gi then detached = #("gi", p31ReadGI value)
        else if spec[2] == #backing then
        (
            p31Require (value != undefined and value == backingWitness[1]) "backing property mismatch"
            p31ExactWitness #(value, backingWitness[2])
            -- No recursion into layerAsRefTarg and no name-based identity.
            detached = #("same_exact_backing")
        )
        else detached = p31Detach value spec[2]
        #(spec[1], detached)
    )
)

-- Only unnested layers are admitted. A non-null parent or any child is not
-- silently omitted: it is an unsupported state and makes the whole read fail.
fn p31RequireNoHierarchy layer =
(
    local parent = layer.getParent()
    local childCount = layer.getNumChildren()
    p31Require (parent == undefined) "parent layer unsupported"
    p31Require ((classOf childCount) == Integer and childCount == 0) "child layers unsupported"
    true
)

-- max 16 independently retained member witnesses; subject must occur once.
-- Canonicalize the actual membership in caller-witness order, not Max's order.
fn p31ReadMembers layer nodeWitness backingWitness memberWitnesses =
(
    p31Require ((classOf memberWitnesses) == Array and memberWitnesses.count >= 1 and memberWitnesses.count <= 16) "member witness count unsupported"
    local subjectHits = 0
    for i = 1 to memberWitnesses.count do
    (
        local witness = memberWitnesses[i]
        p31ExactWitness witness
        p31Require (isValidNode witness[1]) "member is not a valid node"
        if witness[1] == nodeWitness[1] do subjectHits += 1
        if i > 1 do
            for j = 1 to (i - 1) do p31Require (memberWitnesses[j][1] != witness[1]) "duplicate member witness"
    )
    p31Require (subjectHits == 1) "subject absent or duplicate in witnesses"
    local reported = layer.getNumNodes()
    p31Require ((classOf reported) == Integer and reported == memberWitnesses.count and reported <= 16) "reported member count unsupported"
    local members = #()
    p31Require (layer.nodes &members) "membership call failed"
    p31Require ((classOf members) == Array and members.count == reported) "membership enumeration mismatch"
    local result = #()
    for witness in memberWitnesses do
    (
        local hits = 0
        for actualMember in members do if actualMember == witness[1] do hits += 1
        p31Require (hits == 1) "member missing, duplicate, or foreign"
        local memberLayer = witness[1].layer
        p31Require ((classOf memberLayer) == MixinInterface) "member layer interface unavailable"
        local memberBacking = memberLayer.layerAsRefTarg
        p31Require (memberBacking != undefined and memberBacking == backingWitness[1]) "member backing mismatch"
        p31ExactWitness #(memberBacking, backingWitness[2])
        append result witness[2]
    )
    p31Require ((layer.getNumNodes()) == reported) "membership changed during read"
    result
)

-- Allowed dependents are exactly the separately retained root and manager,
-- plus optional exact member nodes. Manager identity needs independent proof.
-- This is a conservative observed-shape guard, not full dependency coverage.
fn p31ReadDependencies backingWitness rootWitness managerWitness memberWitnesses =
(
    p31ExactWitness rootWitness
    p31ExactWitness managerWitness
    p31Require (rootNode == rootWitness[1]) "root witness changed"
    p31Require (rootWitness[1] != managerWitness[1] and rootWitness[1] != backingWitness[1] and managerWitness[1] != backingWitness[1]) "ambiguous dependency witnesses"
    for witness in memberWitnesses do
        p31Require (witness[1] != rootWitness[1] and witness[1] != managerWitness[1] and witness[1] != backingWitness[1]) "member overlaps dependency witness"
    p31Require ((refs.getNumRefs backingWitness[1]) == 0) "backing outgoing refs unsupported"
    local deps = refs.dependents backingWitness[1]
    p31Require ((classOf deps) == Array and deps.count >= 2 and deps.count <= (2 + memberWitnesses.count)) "unreadable or oversized dependents"
    local rootHits = 0
    local managerHits = 0
    local memberHits = for witness in memberWitnesses collect 0
    for dep in deps do
    (
        p31Require (dep != undefined) "null dependent"
        if dep == rootWitness[1] then rootHits += 1
        else if dep == managerWitness[1] then managerHits += 1
        else
        (
            local matched = 0
            for i = 1 to memberWitnesses.count do
                if dep == memberWitnesses[i][1] do (memberHits[i] += 1; matched += 1)
            p31Require (matched == 1) "foreign or ambiguous dependent"
        )
    )
    p31Require (rootHits == 1 and managerHits == 1) "missing or duplicate root/manager dependent"
    for hits in memberHits do p31Require (hits <= 1) "duplicate member dependent"
    #("deps", rootWitness[2], managerWitness[2], memberHits)
)

fn p31ReadOnce nodeWitness backingWitness rootWitness managerWitness memberWitnesses =
(
    p31ExactWitness nodeWitness
    p31ExactWitness backingWitness
    local node = nodeWitness[1]
    local backing = backingWitness[1]
    p31Require (isValidNode node) "node witness is not live"
    p31Require (((classOf backing) as string) == "Base_LayerBase_Layer") "unrecognized backing class"
    local layer = node.layer
    p31Require ((classOf layer) == MixinInterface) "node.layer is not a readable mixin"
    local actualBacking = layer.layerAsRefTarg
    p31Require (actualBacking != undefined and actualBacking == backing) "node.layer backing changed"
    p31ExactWitness #(actualBacking, backingWitness[2])
    p31RequireNoHierarchy layer
    local members = p31ReadMembers layer nodeWitness backingWitness memberWitnesses
    local dependencies = p31ReadDependencies backingWitness rootWitness managerWitness memberWitnesses
    local interfaceState = p31ReadProperties layer p31InterfaceProfile backingWitness
    local backingState = p31ReadProperties backing p31BackingProfile backingWitness
    p31RequireNoHierarchy layer
    -- All copied property values are detached. Handles are comparison data only;
    -- the caller must retain the exact references separately and never trust a
    -- handle or this partial record as ownership or lifecycle authority.
    #(nodeWitness[2], backingWitness[2], #("parent", "none"), #("children", 0),
        members, dependencies, interfaceState, backingState)
)

fn p31DetachedEqual a b depth:0 =
(
    p31Require (depth <= 12) "comparison depth exceeded"
    if classOf a != classOf b then false
    else if classOf a == Array then
    (
        p31Require (a.count <= 64 and b.count <= 64) "comparison array limit exceeded"
        if a.count != b.count then false
        else (local same = true; for i = 1 to a.count while same do same = p31DetachedEqual a[i] b[i] depth:(depth + 1); same)
    )
    else a == b
)

-- A repeatable partial observation is still INCOMPLETE, including when equal.
-- Getter/API throws, unknown/null values, handle failures and bounds all refuse.
fn p31ObserveTwice nodeWitness backingWitness rootWitness managerWitness memberWitnesses =
(
    local result = #("P31_LAYER_OBSERVATION_V1", "INCOMPLETE", "READ_FAILED")
    try
    (
        local a = p31ReadOnce nodeWitness backingWitness rootWitness managerWitness memberWitnesses
        local b = p31ReadOnce nodeWitness backingWitness rootWitness managerWitness memberWitnesses
        if p31DetachedEqual a b then
            result = #("P31_LAYER_OBSERVATION_V1", "INCOMPLETE", "PARTIAL_STABLE", a)
        else
            result = #("P31_LAYER_OBSERVATION_V1", "INCOMPLETE", "CHANGED_DURING_READ")
    )
    catch (result = #("P31_LAYER_OBSERVATION_V1", "INCOMPLETE", "READ_FAILED"))
    result
)
