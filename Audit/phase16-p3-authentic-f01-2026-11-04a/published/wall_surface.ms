-- P3.1 operational artifact; generated predictions are NOT live QA.
-- Route A: actual returned vertex/face IDs; exact references; ONE Shell.
-- This file requires fileIn. Helpers are scoped locally; no caller variables.
(
    local artifactIdentity = "67ad0526bf0336c790e359ec4d771867c63e47786ff7c6f0d3c71f2ed7df628f"
    local ownerNamespace = "P3A_F01"
    local artifactBinding = "67970658c8759f6813ed9a5f8f98996bf32b088a44727bd59990f044f2ce75df"
    local registryKey = "__P3W_9c1a6734f22c576288390eb4e4983f323fa02f87e74f250841599711ce936113" as name
    local wallName = "P3A_F01__wall"
    local tagKey = "P3WallOwner"
    local tagValue = ownerNamespace + ":" + artifactIdentity + ":" + artifactBinding
    local expectedPoints = #([0.0,0.0,0.0],[500.0,0.0,0.0],[1500.0,0.0,0.0],[2300.0,0.0,0.0],[3300.0,0.0,0.0],[4000.0,0.0,0.0],[0.0,0.0,900.0],[500.0,0.0,900.0],[1500.0,0.0,900.0],[2300.0,0.0,900.0],[3300.0,0.0,900.0],[4000.0,0.0,900.0],[0.0,0.0,2100.0],[500.0,0.0,2100.0],[1500.0,0.0,2100.0],[2300.0,0.0,2100.0],[3300.0,0.0,2100.0],[4000.0,0.0,2100.0],[0.0,0.0,3000.0],[500.0,0.0,3000.0],[1500.0,0.0,3000.0],[2300.0,0.0,3000.0],[3300.0,0.0,3000.0],[4000.0,0.0,3000.0])
    local cellSlots = #(#(1,2,8,7),#(2,3,9,8),#(3,4,10,9),#(4,5,11,10),#(5,6,12,11),#(7,8,14,13),#(8,9,15,14),#(9,10,16,15),#(10,11,17,16),#(11,12,18,17),#(13,14,20,19),#(14,15,21,20),#(15,16,22,21),#(16,17,23,22),#(17,18,24,23))
    local cutSlots = #{2,7,9}
    local createdRefs = #()
    local createdHandles = #()
    local conversionRefs = #()
    local residual = #()
    local cleanupOutcomes = #()
    local observedCensus = #()
    local censusReport = #()
    local lease = undefined
    local registryWitness = undefined
    local attemptStarted = false
    local unresolvedEntry = false
    local constructorStarted = false
    local conversionStarted = false
    local snapshotDisposalState = "NO_SNAPSHOT"
    local snapshotDisposalError = ""
    -- These arrays are intended to be shared with the lease during BUILDING;
    -- actual persistence across interrupted calls is not proven. They are
    -- attempt evidence, never authority to recover by handle or delete.
    local attemptEvidence = #("p3-attempt-evidence-1", createdRefs, createdHandles,
        conversionRefs, residual, cleanupOutcomes, observedCensus, "NOT_STARTED")
    local stage = "entry"

    fn p3RequireState condition reason = (if not condition do throw ("P3_REFUSE|" + reason))
    fn p3UnitsGuard =
    (
        local actualType = units.SystemType
        local actualScale = units.SystemScale as double
        p3RequireState (actualScale > 0.0d0 and actualScale < 1.0d300 and actualScale == actualScale) "invalid/nonfinite SystemScale"
        p3RequireState (actualType == #millimeters) "SystemType mismatch (factor equality is insufficient)"
        p3RequireState (actualScale == 1.0d0) "SystemScale mismatch"
        local cmPerUnit = 0.1d0 * actualScale
        local unitsPerCm = 1.0d0 / cmPerUnit
        p3RequireState (cmPerUnit > 0.0d0 and cmPerUnit < 1.0d300 and unitsPerCm > 0.0d0 and unitsPerCm < 1.0d300) "invalid computed unit factors"
        p3RequireState (cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0) "computed unit factor mismatch"
        true
    )
    fn p3SameState a b =
    (
        if classOf a != classOf b then false
        else if classOf a == Array then
        (
            if a.count != b.count then false
            else (local ok = true; for i = 1 to a.count while ok do ok = p3SameState a[i] b[i]; ok)
        )
        else a == b
    )
    fn p3ExactRef value =
    (
        local result = undefined
        try
        (
            local h = getHandleByAnim value
            p3RequireState (h != undefined and h > 0) "reference has no operational anim handle"
            p3RequireState ((getAnimByHandle h) == value) "reference handle does not round trip"
            result = #(value, h, classOf value)
        )
        catch
        (
            print ("UNSUPPORTED_REFERENCE|class=" + ((classOf value) as string) + "|" + (getCurrentException() as string))
            throw
        )
        result
    )
    fn p3FreezeState value depth:0 dataOnly:false =
    (
        p3RequireState (depth < 16) "property nesting ceiling"
        local cls = classOf value
        -- Data values may not use generic undefined/reference/composite cases.
        if dataOnly do p3RequireState (cls == Integer or cls == Integer64 or cls == Float or cls == Double) "INCOMPLETE: unsupported/unknown data scalar"
        case cls of
        (
            UndefinedClass: #("undefined")
            BooleanClass: #("bool", value)
            Integer: #("integer", value)
            Integer64: #("integer64", value)
            Float: (p3RequireState (value == value and abs value < 1.0e38) "nonfinite Float property"; #("float", value))
            Double: (p3RequireState (value == value and abs value < 1.0d300) "nonfinite Double property"; #("double", value))
            String: #("string", copy value)
            Name: #("name", value)
            Point2: #("point2", value.x, value.y)
            Point3: #("point3", value.x, value.y, value.z)
            Point4: #("point4", value.x, value.y, value.z, value.w)
            Color: #("color", value.r, value.g, value.b, value.a)
            Quat: #("quat", value.x, value.y, value.z, value.w)
            Matrix3: #("matrix3", p3FreezeState value.row1 depth:(depth+1), p3FreezeState value.row2 depth:(depth+1), p3FreezeState value.row3 depth:(depth+1), p3FreezeState value.row4 depth:(depth+1))
            Time: #("time", value as integer)
            Interval: #("interval", value.start as integer, value.end as integer)
            BitArray: #("bits", value.count, value as array)
            Array: (p3RequireState (value.count <= 1024) "property array ceiling"; #("array", for v in value collect p3FreezeState v depth:(depth+1)))
            default: #("exact-reference", p3ExactRef value)
        )
    )
    fn p3ReadProperties target =
    (
        local names = getPropNames target
        p3RequireState (names != undefined and names.count <= 512) "property enumeration unavailable/ceiling"
        for p in names collect
        (
            local entry = undefined
            try (entry = #(p, p3FreezeState (getProperty target p)))
            catch
            (
                print ("UNSUPPORTED_PROPERTY|class=" + ((classOf target) as string) + "|property=" + (p as string) + "|" + (getCurrentException() as string))
                throw
            )
            entry
        )
    )
    fn p3ReferenceSet items =
    (
        p3RequireState (items.count <= 128) "dependency reference enumeration ceiling"
        local frozen = for item in items collect p3ExactRef item
        -- Preserve ordering as well: changed enumeration conservatively refuses.
        frozen
    )
    fn p3GraphSnapshot seed =
    (
        local pending = #(seed)
        local visited = #()
        local result = #()
        local cursor = 1
        while cursor <= pending.count do
        (
            local target = pending[cursor]
            cursor += 1
            if target != undefined and (findItem visited target) == 0 do
            (
                p3RequireState (visited.count < 128) "reference graph ceiling/unsupported dependencies"
                append visited target
                p3RequireState (custAttributes.count target == 0) "custom attributes unsupported"
                local refsCount = refs.getNumRefs target
                p3RequireState (refsCount >= 0 and refsCount <= 128) "reference enumeration unavailable/ceiling"
                local outwardRefs = #()
                for i = 1 to refsCount do
                (
                    local item = refs.getReference target i
                    append outwardRefs (if item == undefined then #("undefined") else p3ExactRef item)
                    if item != undefined do append pending item
                )
                local keyCount = undefined
                if (superClassOf target) == controller do
                (
                    p3RequireState ((findItem #(PRS, Position_XYZ, Euler_XYZ, Bezier_Scale, Bezier_Float, Linear_Float, TCB_Float, Bezier_Position, TCB_Position, TCB_Rotation) (classOf target)) > 0) "unknown/wired/scripted controller unsupported"
                    keyCount = numKeys target
                    p3RequireState (keyCount == 0 or keyCount == -1) "keyframed/unsupported controller refused"
                )
                append result #(p3ExactRef target, p3ReadProperties target, keyCount, outwardRefs, p3ReferenceSet (refs.dependents target))
            )
        )
        result
    )
    fn p3PolySnapshot base =
    (
        p3RequireState ((classOf base) == Editable_Poly) "base is not Editable_Poly"
        local nv = polyop.getNumVerts base
        local ne = polyop.getNumEdges base
        local nf = polyop.getNumFaces base
        -- Data entry iteration also requires trustworthy V/E element counts.
        p3RequireState ((classOf nv) == Integer and (classOf ne) == Integer) "INCOMPLETE: unknown V/E element count type"
        p3RequireState (nv >= 0 and ne >= 0 and nv <= 64 and ne <= 256 and nf <= 32) "base snapshot operational ceiling"
        local deadV = polyop.getDeadVerts base
        local deadE = polyop.getDeadEdges base
        local deadF = polyop.getDeadFaces base
        p3RequireState ((classOf deadV) == BitArray and (classOf deadE) == BitArray) "INCOMPLETE: unknown V/E dead-state type"
        local vertices = for i = 1 to nv collect
            (if deadV[i] then #("dead") else #(p3FreezeState (polyop.getVert base i), polyop.getVertFlags base i))
        local edges = for i = 1 to ne collect
            (if deadE[i] then #("dead") else #(polyop.getEdgeVerts base i, polyop.getEdgeFlags base i))
        local faces = for i = 1 to nf collect
            (if deadF[i] then #("dead") else #(polyop.getFaceVerts base i, polyop.getFaceFlags base i,
                polyop.getFaceMatID base i, polyop.getFaceSmoothGroup base i))
        local maps = #()
        local nm = polyop.getNumMaps base
        p3RequireState (nm >= 0 and nm <= 100) "map channel ceiling"
        for channel = -2 to (nm-1) do
        (
            local supported = polyop.getMapSupport base channel
            local entry = #(channel, supported)
            if supported do
            (
                local mv = polyop.getNumMapVerts base channel
                local mf = polyop.getNumMapFaces base channel
                p3RequireState (mv <= 256 and mf <= 32) "map geometry ceiling"
                append entry (for i = 1 to mv collect p3FreezeState (polyop.getMapVert base channel i))
                append entry (for i = 1 to mf collect (if deadF[i] then #("dead") else polyop.getMapFace base channel i))
            )
            append maps entry
        )
        -- VData/EData cannot be ignored: crease/weight edits may not change verts.
        local data = #()
        local vn = polyop.getNumVDataChannels base
        local en = polyop.getNumEDataChannels base
        p3RequireState ((classOf vn) == Integer and (classOf en) == Integer) "INCOMPLETE: unknown data channel count type"
        p3RequireState (vn >= 0 and vn <= 100 and en >= 0 and en <= 100) "INCOMPLETE: invalid data channel count/ceiling"
        if vn > 0 do for channel = 1 to vn do
        (
            local support = polyop.getVDataChannelSupport base channel
            p3RequireState ((classOf support) == BooleanClass) "INCOMPLETE: unknown VData channel support"
            local values = #("unsupported")
            if support do
            (
                values = #()
                if nv > 0 do values = (for i = 1 to nv collect
                (
                    local dead = deadV[i]
                    p3RequireState ((classOf dead) == BooleanClass) "INCOMPLETE: unknown VData entry dead-state"
                    if dead then #("dead") else p3FreezeState (polyop.getVDataValue base channel i) dataOnly:true
                ))
            )
            append data #("v", channel, support, values)
        )
        if en > 0 do for channel = 1 to en do
        (
            local support = polyop.getEDataChannelSupport base channel
            p3RequireState ((classOf support) == BooleanClass) "INCOMPLETE: unknown EData channel support"
            local values = #("unsupported")
            if support do
            (
                values = #()
                if ne > 0 do values = (for i = 1 to ne collect
                (
                    local dead = deadE[i]
                    p3RequireState ((classOf dead) == BooleanClass) "INCOMPLETE: unknown EData entry dead-state"
                    if dead then #("dead") else p3FreezeState (polyop.getEDataValue base channel i) dataOnly:true
                ))
            )
            append data #("e", channel, support, values)
        )
        #(nv, ne, nf, p3FreezeState deadV, p3FreezeState deadE, p3FreezeState deadF, vertices, edges, faces, maps, data,
          p3FreezeState (polyop.getVertSelection base), p3FreezeState (polyop.getEdgeSelection base), p3FreezeState (polyop.getFaceSelection base))
    )
    fn p3EvaluatedSnapshot node =
    (
        local msh = undefined
        local result = undefined
        local disposalStarted = false
        try
        (
            snapshotDisposalState = "SNAPSHOT_ACQUISITION_IN_PROGRESS"
            msh = snapshotAsMesh node
            p3RequireState (msh != undefined) "evaluated snapshot unavailable"
            snapshotDisposalState = "SNAPSHOT_HELD"
            local nv = getNumVerts msh
            local nf = getNumFaces msh
            p3RequireState (nv <= 128 and nf <= 96) "evaluated mesh budget exceeded"
            p3RequireState (nf == 96) "evaluated triangle prediction mismatch"
            result = #(nv, nf, for i = 1 to nv collect p3FreezeState (getVert msh i),
              for i = 1 to nv collect p3FreezeState (getNormal msh i),
              for i = 1 to nf collect #(p3FreezeState (getFace msh i), getFaceMatID msh i,
                getFaceSmoothGroup msh i, getEdgeVis msh i 1, getEdgeVis msh i 2, getEdgeVis msh i 3))
            disposalStarted = true
            snapshotDisposalState = "DISPOSAL_IN_PROGRESS"
            delete msh
            msh = undefined
            snapshotDisposalState = "DISPOSAL_CALL_RETURNED"
        )
        catch
        (
            local reason = getCurrentException()
            if disposalStarted then
            (
                -- A throwing delete has unknown outcome; never retry an object
                -- whose exact disposal may already have happened.
                snapshotDisposalState = "DISPOSAL_UNKNOWN"
                snapshotDisposalError = reason as string
            )
            else if msh == undefined then
                snapshotDisposalState = "ACQUISITION_OR_DISPOSAL_UNKNOWN"
            else
            (
                try
                (
                    snapshotDisposalState = "DISPOSAL_IN_PROGRESS"
                    delete msh
                    msh = undefined
                    snapshotDisposalState = "DISPOSAL_CALL_RETURNED_AFTER_READ_FAILURE"
                )
                catch
                (
                    snapshotDisposalState = "DISPOSAL_UNKNOWN"
                    snapshotDisposalError = getCurrentException() as string
                )
            )
            if snapshotDisposalState != "DISPOSAL_CALL_RETURNED_AFTER_READ_FAILURE" do
                print ("P3_INCOMPLETE|exact in-memory snapshot disposal failed or unknown|state=" + snapshotDisposalState + "|disposalError=" + snapshotDisposalError)
            print ("P3_SNAPSHOT_REFUSED|original=" + (reason as string))
            throw
        )
        result
    )
    fn p3TrimeshRNormalsSnapshot targetBase targetNode =
    (
        local baseTri = undefined
        local baseData = undefined
        try
        (
            baseTri = targetBase.mesh
            p3RequireState (baseTri != undefined and (classOf baseTri) == TriMesh) "base in-memory TriMesh unavailable"
            local bnf = baseTri.numFaces
            local bnv = baseTri.numVerts
            p3RequireState (bnf <= 128 and bnv <= 128) "base TriMesh budget exceeded"
            local bFaces = for f = 1 to bnf collect #(
                getFaceSmoothGroup baseTri f,
                for n in (meshop.getFaceRNormals baseTri f) collect p3FreezeState n
            )
            baseData = #(bnv, bnf, bFaces)
            delete baseTri
            baseTri = undefined
        )
        catch
        (
            if baseTri != undefined do try ( delete baseTri ) catch ()
            throw
        )
        local evalTri = undefined
        local evalData = undefined
        try
        (
            evalTri = targetNode.mesh
            p3RequireState (evalTri != undefined and (classOf evalTri) == TriMesh) "eval in-memory TriMesh unavailable"
            local enf = evalTri.numFaces
            local env = evalTri.numVerts
            p3RequireState (enf <= 96 and env <= 256) "eval TriMesh budget exceeded"
            p3RequireState (enf == 96) "eval TriMesh triangle prediction mismatch"
            local eFaces = for f = 1 to enf collect #(
                getFaceSmoothGroup evalTri f,
                for n in (meshop.getFaceRNormals evalTri f) collect p3FreezeState n
            )
            evalData = #(env, enf, eFaces)
            delete evalTri
            evalTri = undefined
        )
        catch
        (
            if evalTri != undefined do try ( delete evalTri ) catch ()
            throw
        )
        #(baseData, evalData)
    )
    fn p3AuditSubAnims seed maxDepth:16 =
    (
        local pending = #(seed)
        local visited = #()
        local cursor = 1
        local forbiddenClasses = #(
            float_script, position_script, point3_script, rotation_script, scale_script, transform_script,
            float_wire, position_wire, point3_wire, rotation_wire, scale_wire,
            Position_Constraint, Orientation_Constraint, LookAt_Constraint, Path_Constraint, Attachment, Surface_Constraint, Link_Constraint,
            Float_Expression, Position_Expression, Point3_Expression, Scale_Expression,
            Float_Reaction, Position_Reaction, Point3_Reaction, Rotation_Reaction, Scale_Reaction
        )
        while cursor <= pending.count do
        (
            local cur = pending[cursor]
            cursor += 1
            if cur != undefined and (findItem visited cur) == 0 do
            (
                p3RequireState (visited.count < 256) "subAnim audit count ceiling exceeded"
                append visited cur
                local nSubs = cur.numSubs
                if nSubs != undefined and nSubs > 0 and nSubs <= 128 do
                (
                    for i = 1 to nSubs do
                    (
                        local sa = getSubAnim cur i
                        if sa != undefined do
                        (
                            local ctrl = sa.controller
                            if ctrl != undefined do
                            (
                                local ctrlCls = classOf ctrl
                                p3RequireState (findItem forbiddenClasses ctrlCls == 0) ("forbidden wired/scripted/constraint controller: " + (ctrlCls as string))
                                local nk = numKeys ctrl
                                p3RequireState (nk == 0 or nk == -1) ("controller has animation keys: " + (ctrlCls as string))
                                if isProperty ctrl #isWired do p3RequireState (ctrl.isWired == false) "paramWire detected on controller"
                            )
                            local obj = sa.object
                            if obj != undefined and (findItem visited obj) == 0 do
                            (
                                append pending obj
                            )
                        )
                    )
                )
            )
        )
        visited.count
    )
    fn p3LayerAdmissionGuard =
    (
        p3RequireState (LayerManager.count == 1) "layer count mismatch: requires exactly 1 layer"
        p3RequireState (refs.getReference rootScene 4 == rootNode) "rootScene ref 4 != rootNode"
        local lmTarget = refs.getReference rootScene 11
        p3RequireState (lmTarget != undefined and (classOf lmTarget) == Layer_Manager) "lmTarget reference missing or invalid"
        local l0 = LayerManager.getLayer 0
        p3RequireState (l0 != undefined and l0.name == "0" and l0.current == true) "default layer 0 invalid"
        local l0Members = #()
        p3RequireState (l0.nodes &l0Members and l0Members.count == 0 and l0.getNumNodes() == 0) "layer 0 not empty"
        local backing0 = l0.layerAsRefTarg
        p3RequireState (backing0 != undefined and refs.getReference lmTarget 1 == backing0) "lmTarget ref 1 != layer 0 backing"
        p3RequireState ((refs.getNumRefs backing0) == 0) "backing has unexpected outgoing refs"
        local deps = refs.dependents backing0
        p3RequireState (deps.count == 2 and (findItem deps rootScene) != 0 and (findItem deps lmTarget) != 0) "layer 0 dependency closure violated"
        true
    )
    fn p3NodeSnapshot node =
    (
        p3RequireState (isValidNode node) "invalid exact node reference"
        p3RequireState (objects.count == 1) "scene census changed before snapshot"
        local censusNodes = for other in objects collect other
        p3RequireState (censusNodes.count == 1 and censusNodes[1] == node) "exact scene census changed before snapshot"
        p3RequireState ((node.parent == undefined or node.parent == rootNode) and node.children.count == 0) "parent/children not standalone"
        p3RequireState (node.material == undefined) "material assigned: unsupported replay state"
        p3RequireState (node.modifiers.count == 1 and classOf node.modifiers[1] == Shell) "stack mismatch"
        local forbiddenNormalMods = #(Edit_Normals, Normalmodifier, Smooth, Vertex_Weld, Weighted_Normals)
        for m in node.modifiers do
        (
            p3RequireState (findItem forbiddenNormalMods (classOf m) == 0) ("forbidden normal modifier in stack: " + ((classOf m) as string))
        )
        local shellMod = node.modifiers[1]
        p3RequireState ((classOf node.baseObject) == Editable_Poly) "base is not Editable_Poly"
        p3RequireState (shellMod.innerAmount == 0.0 and shellMod.outerAmount == 300.0 and shellMod.segments == 1) "Shell parameter edit"
        local nodeRef = p3ExactRef node
        local baseRef = p3ExactRef node.baseObject
        local shellRef = p3ExactRef shellMod
        local enabledState = #(shellMod.enabled, shellMod.enabledInViews, shellMod.enabledInRenders)
        p3RequireState (enabledState[1] == true and enabledState[2] == true and enabledState[3] == true) "Shell disabled or enable state unsupported"
        local instanceUsers = for other in objects where other.baseObject == node.baseObject collect other
        p3RequireState (instanceUsers.count == 1 and instanceUsers[1] == node) "shared base object dependency/instance"
        -- This traversal is a rejection check, NOT proof of a complete or safe
        -- dependency/controller graph. In particular numKeys == -1 is not enough.
        local graphState = p3GraphSnapshot node
        local explicitNames = #(#name, #wirecolor, #isHidden, #isFrozen, #renderable, #primaryVisibility,
            #secondaryVisibility, #castShadows, #receiveShadows, #applyAtmospherics, #renderOccluded,
            #visibility, #inheritVisibility, #showFrozenInGray, #displayByLayer, #renderByLayer,
            #motionByLayer, #colorByLayer, #boxmode, #backfacecull, #allEdges, #vertexTicks, #xray,
            #showTrajectory, #isSelected, #objectOffsetPos, #objectOffsetRot, #objectOffsetScale,
            #transform, #objectTransform, #parent, #layer, #material)
        local explicitState = for p in explicitNames collect
        (
            p3RequireState (isProperty node p) ("required node property unavailable: " + (p as string))
            #(p, p3FreezeState (getProperty node p))
        )
        local userBuffer = getUserPropBuffer node
        p3RequireState ((classOf userBuffer) == String and userBuffer.count <= 4096) "unsupported user property buffer"
        userBuffer = copy userBuffer
        local layerState = p3ReadProperties node.layer
        local baseState = p3PolySnapshot node.baseObject
        -- STOP: this traversal is incomplete and is NOT an evaluation safety
        -- gate. Complete Shell/controller/dependency exclusion is uncalibrated.
        -- Construction must not be run until main resolves and tests that gate.
        local evaluatedState = p3EvaluatedSnapshot node
        local rnormalState = p3TrimeshRNormalsSnapshot node.baseObject node
        local subAnimCount = p3AuditSubAnims node
        p3RequireState (subAnimCount > 0) "subAnim audit returned zero animatables"
        #(nodeRef, baseRef, shellRef, enabledState[1], enabledState[2], enabledState[3],
          explicitState, userBuffer, layerState, baseState, evaluatedState, graphState, rnormalState, subAnimCount)
    )
    fn p3CensusGuard node =
    (
        p3RequireState (objects.count <= 64) "scene census operational ceiling"
        local nodes = for other in objects collect other
        p3RequireState (nodes.count == 1 and nodes[1] == node) "scene census changed; collisions/dependencies are not owned"
        local nameMatches = 0
        local tagMatches = 0
        for other in nodes do
        (
            if (toLower other.name) == (toLower wallName) do nameMatches += 1
            if (getUserProp other tagKey) == tagValue do tagMatches += 1
        )
        p3RequireState (nameMatches == 1 and node.name == wallName and tagMatches == 1) "copied-tag or matching-name collision"
        p3RequireState ((getUserProp node tagKey) == tagValue) "ownership tag edit"
    )
    fn p3EnvironmentSnapshot =
    (
        #(p3ExactRef rootNode, (copy maxFilePath), (copy maxFileName), currentTime as integer,
          p3ReferenceSet (selection as array), subObjectLevel)
    )

    try
    (
        -- Must precede even replay inspection, registry writes, or constructors.
        p3UnitsGuard()
        p3RequireState (maxFilePath == "" and maxFileName == "") "session-only runtime refuses saved/loaded scene"
        p3RequireState (globalVars.isGlobal registryKey) "missing explicit armed session registry; never auto-adopt/re-arm"
        registryWitness = globalVars.get registryKey
        p3RequireState (isProperty registryWitness #values) "registry has no exact structured lease"
        lease = registryWitness.values
        p3RequireState ((classOf lease) == Array and lease.count == 10) "invalid registry; do not overwrite caller global"
        p3RequireState (lease[1] == "p3-session-registry-2" and lease[2] == artifactIdentity and lease[3] == artifactBinding and lease[4] == ownerNamespace) "registry identity mismatch"
        p3RequireState ((classOf lease[6]) == String and lease[6].count >= 16 and lease[6].count <= 128) "missing bounded external lease witness"
        p3RequireState ((classOf lease[10]) == BooleanClass) "invalid arm dirty-state observation"
        local localNonce = copy lease[6]
        -- This invocation cannot independently authenticate this self-read; main
        -- must compare the independently held struct and detached fields.
        if lease[5] == "BUILDING" or lease[5] == "POISONED" do
        (
            stage = "unresolved-prior-attempt"
            unresolvedEntry = true
            p3RequireState false "INCOMPLETE: prior BUILDING/POISONED lease requires independent inspection, never retry"
        )
        p3RequireState (p3SameState lease[7] (p3EnvironmentSnapshot())) "scene witness/selection/time state changed"
        if lease[5] == "COMMITTED" then
        (
            stage = "replay-read-only"
            p3RequireState (isValidNode lease[8]) "committed node reference invalid"
            p3RequireState ((classOf lease[9]) == Array) "committed baseline snapshot missing"
            p3RequireState (getSaveRequired() == lease[10]) "scene dirty-state changed since commit"
            p3CensusGuard lease[8]
            local currentSnapshot = p3NodeSnapshot lease[8]
            p3RequireState (p3SameState currentSnapshot lease[9]) "replay baseline mismatch: node or stack was modified"
            print ("P3_REPLAY_NOOP|identity=" + artifactIdentity + "|handle=" + ((getHandleByAnim lease[8]) as string) + "|status=VERIFIED_NOOP")
        )
        else
        (
            stage = "pre-create"
            p3RequireState (lease[5] == "ARMED" and lease[8] == undefined and lease[9] == undefined) "lease spent/building/poisoned; refuse implicit recovery"
            p3RequireState (objects.count == 0 and selection.count == 0) "first create requires empty unnamed scene"
            p3RequireState (getSaveRequired() == lease[10]) "scene dirty-state changed since arm"
            local environmentBefore = p3EnvironmentSnapshot()
            p3UnitsGuard()
            p3RequireState ((globalVars.get registryKey) == registryWitness and registryWitness.values == lease and lease[6] == localNonce and lease[5] == "ARMED") "local lease self-read changed; independent witness still required"
            p3RequireState (getSaveRequired() == lease[10]) "scene dirty-state changed immediately before BUILDING"
            p3LayerAdmissionGuard()
            attemptStarted = true
            lease[5] = "BUILDING"
            -- Interruption between later writes can leave incomplete evidence;
            -- after any timeout main must inspect, never retry.
            lease[8] = attemptEvidence
            attemptEvidence[8] = "CONSTRUCTOR_IN_PROGRESS"
            constructorStarted = true
            local node = Editable_Mesh()
            append createdRefs node
            attemptEvidence[8] = "CONSTRUCTOR_RETURNED"
            local initialHandle = getHandleByAnim node
            append createdHandles initialHandle
            p3RequireState (isValidNode node and initialHandle != undefined and initialHandle > 0 and (getAnimByHandle initialHandle) == node) "new exact node unavailable"
            node.name = wallName
            stage = "convert"
            attemptEvidence[8] = "CONVERSION_IN_PROGRESS"
            conversionStarted = true
            local converted = convertTo node Editable_Poly
            -- Retain the returned candidate before validation; it is NOT
            -- deletion authority if continuity cannot be established.
            append conversionRefs converted
            attemptEvidence[8] = "CONVERSION_RETURNED"
            p3RequireState (isValidNode node and isValidNode converted and converted == node) "conversion exact reference continuity unavailable"
            p3RequireState ((getHandleByAnim converted) == initialHandle and (getAnimByHandle initialHandle) == node and objects.count == 1 and node.name == wallName) "conversion identity not preserved; no lookup by name"
            node = converted
            stage = "grid-vertices"
            local vertexIds = #()
            for point in expectedPoints do
            (
                local id = polyop.createVert node point
                p3RequireState ((classOf id) == Integer and id > 0 and id <= polyop.getNumVerts node and (findItem vertexIds id) == 0) "invalid/duplicate returned vertex ID"
                append vertexIds id
                p3RequireState ((polyop.getVert node id) == point) "created vertex readback mismatch"
            )
            update node
            print ("P3_VERTEX_IDS|" + (vertexIds as string))
            stage = "grid-faces"
            local faceIds = #()
            local cutIds = #{}
            for slot = 1 to cellSlots.count do
            (
                local actualLoop = for index in cellSlots[slot] collect vertexIds[index]
                local id = polyop.createPolygon node actualLoop
                p3RequireState ((classOf id) == Integer and id > 0 and id <= polyop.getNumFaces node and (findItem faceIds id) == 0) "invalid/duplicate returned face ID"
                append faceIds id
                p3RequireState (p3SameState (polyop.getFaceVerts node id) actualLoop) "created face loop readback mismatch"
                if cutSlots[slot] do cutIds[id] = true
            )
            update node
            p3RequireState ((polyop.getNumFaces node) == 15) "grid count readback mismatch"
            print ("P3_FACE_IDS|" + (faceIds as string) + "|P3_CUT_IDS|" + (cutIds as string))
            stage = "opening-delete-once"
            if cutIds.numberSet > 0 do polyop.deleteFaces node cutIds delIsoVerts:false
            update node
            local deadFaces = polyop.getDeadFaces node
            local activeCount = (polyop.getNumFaces node) - deadFaces.numberSet
            p3RequireState (activeCount == 12) "active base count readback mismatch"
            print ("P3_BASE_READBACK|active_polygons=" + (activeCount as string))
            stage = "one-shell"
            local shellMod = Shell innerAmount:0.0 outerAmount:300.0 segments:1
            addModifier node shellMod
            update node
            p3RequireState (node.modifiers.count == 1 and node.modifiers[1] == shellMod) "actual Shell reference/stack mismatch"
            setUserProp node tagKey tagValue
            p3CensusGuard node
            p3RequireState (p3SameState environmentBefore (p3EnvironmentSnapshot())) "constructor changed protected environment state"
            stage = "exact-baseline"
            local baseline = p3NodeSnapshot node
            p3RequireState (p3SameState baseline (p3NodeSnapshot node)) "baseline unstable/uncomparable"
            p3UnitsGuard()
            p3RequireState ((globalVars.get registryKey) == registryWitness and registryWitness.values == lease and lease[6] == localNonce) "local registry self-read changed; independent witness still required"
            lease[8] = node
            lease[9] = baseline
            lease[10] = getSaveRequired()
            -- Contract's construction-only marker, NOT accepted replay/QA.
            lease[5] = "COMMITTED"
            print ("P3_CREATED_UNVERIFIED|identity=" + artifactIdentity + "|handle=" + ((getHandleByAnim node) as string) + "|baseline=complete|replay=READY")
        )
    )
    catch
    (
        local reason = getCurrentException()
        -- Preserve the original failure even if later diagnostic reads throw.
        print ("P3_ORIGINAL_FAILURE|stage=" + stage + "|" + (reason as string))
        local reportErrors = #()
        local censusKnown = false
        local censusCount = -1
        local leaseStatus = if attemptStarted then "UNKNOWN" else "NOT_WRITTEN"
        -- Inspect the COMPLETE census even if the constructor never returned a
        -- reference. It is diagnostic only; census never authorizes deletion.
        try
        (
            censusCount = objects.count
            p3RequireState (censusCount <= 64) "cleanup census ceiling; exact enumeration unavailable"
            for observed in objects do append observedCensus observed
            p3RequireState (observedCensus.count == censusCount) "cleanup census changed during observation"
            censusKnown = true
            for observed in observedCensus do
            (
                local observedValid = false
                local observedHandle = undefined
                local validStatus = "UNKNOWN"
                local handleStatus = "UNKNOWN"
                try (observedValid = isValidNode observed; validStatus = "READ")
                catch (append reportErrors ("census-validity: " + (getCurrentException() as string)))
                try (observedHandle = getHandleByAnim observed; handleStatus = "READ")
                catch (append reportErrors ("census-handle: " + (getCurrentException() as string)))
                append censusReport #(observedValid, validStatus, observedHandle, handleStatus)
            )
        )
        catch
        (
            censusKnown = false
            append reportErrors ("census: " + (getCurrentException() as string))
        )
        -- Never use a handle lookup, name or census as authority to delete.
        -- Full exclusion of foreign non-node dependencies is not calibrated;
        -- therefore even a valid exact current-attempt reference is retained.
        for i = 1 to createdRefs.count do
        (
            try
            (
                local exactNode = createdRefs[i]
                local refValid = isValidNode exactNode
                local savedHandle = if i <= createdHandles.count then createdHandles[i] else undefined
                local currentHandle = if refValid then getHandleByAnim exactNode else undefined
                local location = findItem observedCensus exactNode
                append residual #("RETAINED_OR_INVALID_CREATED_REF", i, refValid, savedHandle, currentHandle, location)
                append cleanupOutcomes #("RETAINED_NO_CALIBRATED_DEPENDENCY_EXCLUSION", i)
            )
            catch
            (
                local cleanupError = getCurrentException()
                append residual #("UNRESOLVED_CREATED_REF", i)
                append cleanupOutcomes #("CREATED_REF_GUARD_ERROR", i, cleanupError as string)
            )
        )
        for i = 1 to conversionRefs.count do
        (
            try
            (
                local candidate = conversionRefs[i]
                local candidateValid = isValidNode candidate
                local candidateHandle = if candidateValid then getHandleByAnim candidate else undefined
                local location = findItem observedCensus candidate
                append residual #("UNPROMOTED_CONVERSION_CANDIDATE", i, candidateValid, candidateHandle, location)
                append cleanupOutcomes #("CONVERSION_CANDIDATE_RETAINED", i)
            )
            catch
            (
                local cleanupError = getCurrentException()
                append residual #("UNRESOLVED_CONVERSION_CANDIDATE", i)
                append cleanupOutcomes #("CONVERSION_GUARD_ERROR", i, cleanupError as string)
            )
        )
        if constructorStarted and createdRefs.count == 0 do append residual #("CONSTRUCTOR_RETURN_NOT_OBSERVED")
        if conversionStarted and conversionRefs.count == 0 do append residual #("CONVERSION_RETURN_NOT_OBSERVED")
        if attemptStarted and (not censusKnown or censusCount != 0) do append residual #("UNKNOWN_OR_NONEMPTY_POST_FAILURE_CENSUS", censusCount)
        if attemptStarted and not constructorStarted do append residual #("INTERRUPTED_BEFORE_CONSTRUCTOR_OR_LEASE_RECORD")
        if snapshotDisposalState != "NO_SNAPSHOT" and snapshotDisposalState != "DISPOSAL_CALL_RETURNED" and snapshotDisposalState != "DISPOSAL_CALL_RETURNED_AFTER_READ_FAILURE" do append residual #("SNAPSHOT_DISPOSAL_UNKNOWN", snapshotDisposalState, snapshotDisposalError)
        if attemptStarted do
        (
            try
            (
                p3RequireState (globalVars.isGlobal registryKey and (globalVars.get registryKey) == registryWitness and registryWitness.values == lease) "registry changed; do not overwrite unfamiliar lease"
                attemptEvidence[8] = "FAILED_INSPECT_ONLY"
                lease[8] = attemptEvidence
                lease[9] = residual
                lease[5] = "POISONED"
                -- This self-read cannot prove an independently retained witness.
                leaseStatus = "LOCAL_POISON_WRITES_RETURNED_VERIFY_EXTERNALLY"
            )
            catch
            (
                leaseStatus = "POISON_OR_PUBLICATION_UNKNOWN"
                local leaseError = getCurrentException()
                append reportErrors ("lease: " + (leaseError as string))
                append residual #("LEASE_UPDATE_UNKNOWN", leaseError as string)
            )
        )
        local status = if attemptStarted or unresolvedEntry or not censusKnown or reportErrors.count > 0 or residual.count > 0 then "P3_INCOMPLETE_RESIDUAL" else if stage == "replay-read-only" then "P3_INCOMPLETE_REPLAY" else if stage == "precreate-safety-refusal" then "P3_INCOMPLETE_PRECREATE" else "P3_REFUSED"
        print (status + "|stage=" + stage + "|createdRefs=" + (createdRefs.count as string) + "|createdHandles=" + (createdHandles as string) + "|conversionRefs=" + (conversionRefs.count as string) + "|censusKnown=" + (censusKnown as string) + "|censusCount=" + (censusCount as string) + "|census=" + (censusReport as string) + "|cleanup=" + (cleanupOutcomes as string) + "|residual=" + (residual as string) + "|snapshot=" + snapshotDisposalState + "|snapshotError=" + snapshotDisposalError + "|lease=" + leaseStatus + "|reportErrors=" + (reportErrors as string) + "|original=" + (reason as string))
        throw
    )
)
