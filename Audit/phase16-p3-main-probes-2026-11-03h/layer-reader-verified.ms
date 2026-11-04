-- Verified Bounded Layer Reader with Authenticated rootScene and Layer_Manager Witnesses
-- Main-only execution; read-only calibration; no mutations.
(
    local out = "P3_VERIFIED_BOUNDED_LAYER_READER"
    local beforeRootNode = rootNode
    local beforeRootScene = rootScene
    local beforeTime = currentTime as integer
    local beforeSub = subObjectLevel
    local beforePath = copy maxFilePath
    local beforeName = copy maxFileName
    local beforeDirty = getSaveRequired()
    
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
    
    fn require cond msg = if not cond do throw ("ASSERTION_FAILED: " + msg)
    
    fn exactWitness target expectedHandle:undefined =
    (
        require (target != undefined) "witness target is undefined"
        require ((classOf target) != MixinInterface and (classOf target) != Interface) "cannot witness bare interface"
        local h = getHandleByAnim target
        require (h != undefined and h != 0) "invalid anim handle"
        if expectedHandle != undefined do require (h == expectedHandle) "handle mismatch"
        local round = getAnimByHandle h
        require (round == target) "roundtrip mismatch"
        #(target, h)
    )
    
    fn finiteFloat val =
    (
        require ((classOf val) == Float) "expected Float"
        require (val == val and abs val < 1.0e38) "nonfinite or out-of-range Float"
        val
    )
    
    fn colorComp val =
    (
        local cls = classOf val
        require (cls == Integer or cls == Float) "unsupported color component"
        if cls == Float do finiteFloat val
        val
    )
    
    fn detachScalar val kind =
    (
        case kind of
        (
            #bool: (require ((classOf val) == BooleanClass) "expected bool"; #("bool", val))
            #integer: (require ((classOf val) == Integer) "expected integer"; #("integer", val))
            #float: #("float", finiteFloat val)
            #name: (require ((classOf val) == Name) "expected Name"; #("name", val))
            #string:
            (
                require ((classOf val) == String and val.count <= 4096) "expected bounded String"
                #("string", copy val)
            )
            #color:
            (
                require ((classOf val) == Color) "expected Color"
                #("color", (colorComp val.r), (colorComp val.g), (colorComp val.b), (colorComp val.a))
            )
            default: throw ("unknown scalar kind: " + (kind as string))
        )
    )
    
    fn checkProfile target profile =
    (
        local names = getPropNames target
        require ((classOf names) == Array and names.count == profile.count and names.count <= 34) "property count mismatch"
        for spec in profile do
        (
            local pName = spec[1]
            require ((findItem names pName) != 0) ("missing property: " + (pName as string))
        )
        true
    )
    
    fn readGI giTarget =
    (
        require ((classOf giTarget) == MixinInterface) "GI interface missing or invalid"
        checkProfile giTarget p31GIProfile
        for spec in p31GIProfile collect #(spec[1], (detachScalar (getProperty giTarget spec[1]) spec[2]))
    )
    
    fn readProps target profile backingWitness =
    (
        checkProfile target profile
        for spec in profile collect
        (
            local pName = spec[1]
            local pKind = spec[2]
            local val = getProperty target pName
            local detached = undefined
            if pKind == #gi then (
                detached = #("gi", readGI val)
            ) else if pKind == #backing then (
                require (val != undefined and val == backingWitness[1]) "backing target mismatch"
                exactWitness val expectedHandle:backingWitness[2]
                detached = #("backing", backingWitness[2])
            ) else (
                detached = detachScalar val pKind
            )
            #(pName, detached)
        )
    )
    
    fn p31DetachedEqual a b depth:0 =
    (
        require (depth <= 16) "comparison recursion depth exceeded"
        if classOf a != classOf b then false
        else if classOf a == Array then
        (
            require (a.count <= 64 and b.count <= 64) "array length exceeded"
            if a.count != b.count then false
            else (
                local isEq = true
                for i = 1 to a.count while isEq do isEq = p31DetachedEqual a[i] b[i] depth:(depth + 1)
                isEq
            )
        )
        else a == b
    )
    
    try
    (
        -- Scene admission
        require (objects.count == 0 and selection.count == 0) "objects/selection not empty"
        require (beforePath == "" and beforeName == "") "scene must be unnamed"
        require (units.SystemType == #millimeters and units.SystemScale == 1.0) "units mismatch"
        require (beforeDirty == true) "dirty must be true"
        require (LayerManager.count == 1) "layer count mismatch"
        require (not (globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7)) "historical key present"
        
        -- Acquire and authenticate witnesses from independent system roots
        local rootNodeW = exactWitness beforeRootNode
        local rootSceneW = exactWitness beforeRootScene
        require (refs.getReference beforeRootScene 4 == beforeRootNode) "rootScene ref 4 != rootNode"
        local lmTarget = refs.getReference beforeRootScene 11
        local lmTargetW = exactWitness lmTarget
        
        local l0 = LayerManager.getLayer 0
        require (l0 != undefined and l0.name == "0" and l0.current == true) "layer 0 invalid"
        local l0Members = #()
        require (l0.nodes &l0Members and l0Members.count == 0 and l0.getNumNodes() == 0) "layer 0 has members"
        require (l0.getParent() == undefined and l0.getNumChildren() == 0) "layer 0 has hierarchy"
        
        local backing0 = l0.layerAsRefTarg
        require (refs.getReference lmTarget 1 == backing0) "lmTarget ref 1 != layer 0 backing"
        local backingW = exactWitness backing0
        
        out += "|witnessesAuthenticated=true"
        out += "|rootNodeH=" + (rootNodeW[2] as string)
        out += "|rootSceneH=" + (rootSceneW[2] as string)
        out += "|lmTargetH=" + (lmTargetW[2] as string)
        out += "|backingH=" + (backingW[2] as string)
        
        -- Dependency Closure Check on layer 0 backing
        require ((refs.getNumRefs backing0) == 0) "backing has unexpected outgoing refs"
        local deps = refs.dependents backing0
        require (deps.count == 2) "backing must have exactly 2 dependents"
        local rsHits = 0
        local lmHits = 0
        local foreignHits = 0
        for dep in deps do (
            if dep == rootSceneW[1] then rsHits += 1
            else if dep == lmTargetW[1] then lmHits += 1
            else foreignHits += 1
        )
        require (rsHits == 1 and lmHits == 1 and foreignHits == 0) "dependency mismatch on backing"
        out += "|depClosureOK=true"
        
        -- Read and verify 33 interface properties
        local iface1 = readProps l0 p31InterfaceProfile backingW
        local iface2 = readProps l0 p31InterfaceProfile backingW
        require (p31DetachedEqual iface1 iface2) "interface read not repeatable"
        out += "|ifaceCount=" + (iface1.count as string)
        out += "|ifaceRepeatable=true"
        
        -- Read and verify 34 backing properties (including degrade)
        local back1 = readProps backing0 p31BackingProfile backingW
        local back2 = readProps backing0 p31BackingProfile backingW
        require (p31DetachedEqual back1 back2) "backing read not repeatable"
        out += "|backingCount=" + (back1.count as string)
        out += "|backingRepeatable=true"
        
        -- Read and verify 18 nested GI properties
        local gi1 = readGI l0.INodeGIProperties
        local gi2 = readGI l0.INodeGIProperties
        require (p31DetachedEqual gi1 gi2) "GI read not repeatable"
        out += "|giCount=" + (gi1.count as string)
        out += "|giRepeatable=true"
        
        -- Negative control 1: Detached GI modification detected
        local giModified = readGI l0.INodeGIProperties
        local origVal = giModified[1][2][2]
        giModified[1][2][2] = not origVal
        require (not (p31DetachedEqual gi1 giModified)) "detached GI mutation undetected"
        out += "|detachedGIMutationDetected=true"
        
        -- Negative control 2: Detached degrade modification detected
        local backModified = readProps backing0 p31BackingProfile backingW
        local degIdx = 0
        for i = 1 to backModified.count do if backModified[i][1] == #degrade do degIdx = i
        require (degIdx > 0) "degrade property not found in backing"
        backModified[degIdx][2][2] = not backModified[degIdx][2][2]
        require (not (p31DetachedEqual back1 backModified)) "detached degrade mutation undetected"
        out += "|detachedDegradeMutationDetected=true"
        
        -- Negative control 3: Wrong backing witness refused
        local wrongBackingRefused = false
        try (readProps l0 p31InterfaceProfile #(rootNodeW[1], rootNodeW[2])) catch (wrongBackingRefused = true)
        require wrongBackingRefused "wrong backing witness was not refused"
        out += "|wrongBackingRefused=true"
        
        -- Negative control 4: Bogus property refused
        local bogusPropRefused = false
        try (readProps l0 #(#(#P3_BOGUS_TEST_PROPERTY, #bool)) backingW) catch (bogusPropRefused = true)
        require bogusPropRefused "bogus property was not refused"
        out += "|bogusPropRefused=true"
        
        -- Negative control 5: Undefined scalar refused
        local undefinedRefused = false
        try (detachScalar undefined #float) catch (undefinedRefused = true)
        require undefinedRefused "undefined float was not refused"
        out += "|undefinedScalarRefused=true"
        
        out += "|outcome=BOUNDED_LAYER_READER_PASS_INCOMPLETE_REPLAY"
    )
    catch (out += "|ERROR=" + ((getCurrentException()) as string) + "|outcome=INCOMPLETE")
    
    -- Postcheck: verify scene state untouched
    local postL0 = LayerManager.getLayer 0
    local postMembers = #()
    local postL0Backing = postL0.layerAsRefTarg
    local postBackingH = undefined
    try (postBackingH = getHandleByAnim postL0Backing) catch ()
    local postUnchanged = (
        objects.count == 0 and selection.count == 0 and \
        rootNode == beforeRootNode and rootScene == beforeRootScene and \
        maxFilePath == beforePath and maxFileName == beforeName and \
        getSaveRequired() == beforeDirty and \
        (currentTime as integer) == beforeTime and subObjectLevel == beforeSub and \
        units.SystemType == #millimeters and units.SystemScale == 1.0 and \
        LayerManager.count == 1 and (postL0.nodes &postMembers) and postMembers.count == 0 and \
        postL0.getNumNodes() == 0 and postL0Backing == backing0 and \
        postBackingH == backingW[2]
    )
    out += "|postContextUnchanged=" + (postUnchanged as string)
    out += "|dirtyAfter=" + ((getSaveRequired()) as string)
    out
)
