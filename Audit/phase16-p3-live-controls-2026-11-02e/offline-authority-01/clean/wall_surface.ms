-- P3.1 operational artifact; generated predictions are NOT live QA.
-- Route A: actual returned vertex/face IDs; exact references; ONE Shell.
-- This file requires fileIn. Helpers are scoped locally; no caller variables.
(
    local artifactIdentity = "0593393b04977adbf41d9eeab9e182cf56ba175b3b7d825ba30078a8f1e389a1"
    local ownerNamespace = "AuditAuthorityControl"
    local artifactBinding = "76128b7b0d061832bbcd4aac98398e83a6ce16f3b64a89be5a22f18f216113ca"
    local registryKey = "__P3W_26ab3ea59e09fea43ee92b9f15dcf11a318cdb97ed4a254635e770a9408fcf1e" as name
    local wallName = "AuditAuthorityControl__wall"
    local tagKey = "P3WallOwner"
    local tagValue = ownerNamespace + ":" + artifactIdentity + ":" + artifactBinding
    local expectedPoints = #([0.0,0.0,0.0],[500.0,0.0,0.0],[1500.0,0.0,0.0],[2300.0,0.0,0.0],[3300.0,0.0,0.0],[4000.0,0.0,0.0],[0.0,0.0,900.0],[500.0,0.0,900.0],[1500.0,0.0,900.0],[2300.0,0.0,900.0],[3300.0,0.0,900.0],[4000.0,0.0,900.0],[0.0,0.0,2100.0],[500.0,0.0,2100.0],[1500.0,0.0,2100.0],[2300.0,0.0,2100.0],[3300.0,0.0,2100.0],[4000.0,0.0,2100.0],[0.0,0.0,3000.0],[500.0,0.0,3000.0],[1500.0,0.0,3000.0],[2300.0,0.0,3000.0],[3300.0,0.0,3000.0],[4000.0,0.0,3000.0])
    local cellSlots = #(#(1,2,8,7),#(2,3,9,8),#(3,4,10,9),#(4,5,11,10),#(5,6,12,11),#(7,8,14,13),#(8,9,15,14),#(9,10,16,15),#(10,11,17,16),#(11,12,18,17),#(13,14,20,19),#(14,15,21,20),#(15,16,22,21),#(16,17,23,22),#(17,18,24,23))
    local cutSlots = #{2,7,9}
    local createdRefs = #()
    local createdHandles = #()
    local lease = undefined
    local registryWitness = undefined
    local attemptStarted = false
    local stage = "entry"

    fn require condition reason = (if not condition do throw ("P3_REFUSE|" + reason))
    fn unitsGuard =
    (
        local actualType = units.SystemType
        local actualScale = units.SystemScale as double
        require (actualScale > 0.0d0 and actualScale < 1.0d300 and actualScale == actualScale) "invalid/nonfinite SystemScale"
        require (actualType == #millimeters) "SystemType mismatch (factor equality is insufficient)"
        require (actualScale == 1.0d0) "SystemScale mismatch"
        local cmPerUnit = 0.1d0 * actualScale
        local unitsPerCm = 1.0d0 / cmPerUnit
        require (cmPerUnit > 0.0d0 and cmPerUnit < 1.0d300 and unitsPerCm > 0.0d0 and unitsPerCm < 1.0d300) "invalid computed unit factors"
        require (cmPerUnit == 0.1d0 and unitsPerCm == 10.0d0) "computed unit factor mismatch"
        true
    )
    fn same a b =
    (
        if classOf a != classOf b then false
        else if classOf a == Array then
        (
            if a.count != b.count then false
            else (local ok = true; for i = 1 to a.count while ok do ok = same a[i] b[i]; ok)
        )
        else a == b
    )
    fn exactRef value =
    (
        local result = undefined
        try
        (
            local h = getHandleByAnim value
            require (h != undefined and h > 0) "reference has no operational anim handle"
            require ((getAnimByHandle h) == value) "reference handle does not round trip"
            result = #(value, h, classOf value)
        )
        catch (throw ("UNSUPPORTED_REFERENCE|class=" + ((classOf value) as string) + "|" + (getCurrentException() as string)))
        result
    )
    fn freeze value depth:0 =
    (
        require (depth < 16) "property nesting ceiling"
        local cls = classOf value
        case cls of
        (
            UndefinedClass: #("undefined")
            BooleanClass: #("bool", value)
            Integer: #("integer", value)
            Integer64: #("integer64", value)
            Float: (require (value == value and abs value < 1.0e38) "nonfinite Float property"; #("float", value))
            Double: (require (value == value and abs value < 1.0d300) "nonfinite Double property"; #("double", value))
            String: #("string", copy value)
            Name: #("name", value)
            Point2: #("point2", value.x, value.y)
            Point3: #("point3", value.x, value.y, value.z)
            Point4: #("point4", value.x, value.y, value.z, value.w)
            Color: #("color", value.r, value.g, value.b, value.a)
            Quat: #("quat", value.x, value.y, value.z, value.w)
            Matrix3: #("matrix3", freeze value.row1 depth:(depth+1), freeze value.row2 depth:(depth+1), freeze value.row3 depth:(depth+1), freeze value.row4 depth:(depth+1))
            Time: #("time", value as integer)
            Interval: #("interval", value.start as integer, value.end as integer)
            BitArray: #("bits", value.count, value as array)
            Array: (require (value.count <= 1024) "property array ceiling"; #("array", for v in value collect freeze v depth:(depth+1)))
            default: #("exact-reference", exactRef value)
        )
    )
    fn properties target =
    (
        local names = getPropNames target
        require (names != undefined and names.count <= 512) "property enumeration unavailable/ceiling"
        for p in names collect
        (
            local entry = undefined
            try (entry = #(p, freeze (getProperty target p)))
            catch (throw ("UNSUPPORTED_PROPERTY|class=" + ((classOf target) as string) + "|property=" + (p as string) + "|" + (getCurrentException() as string)))
            entry
        )
    )
    fn referenceSet items =
    (
        require (items.count <= 128) "dependency reference enumeration ceiling"
        local frozen = for item in items collect exactRef item
        -- Preserve ordering as well: changed enumeration conservatively refuses.
        frozen
    )
    fn graphSnapshot seed =
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
                require (visited.count < 128) "reference graph ceiling/unsupported dependencies"
                append visited target
                require (custAttributes.count target == 0) "custom attributes unsupported"
                local refsCount = refs.getNumRefs target
                require (refsCount >= 0 and refsCount <= 128) "reference enumeration unavailable/ceiling"
                local outwardRefs = #()
                for i = 1 to refsCount do
                (
                    local item = refs.getReference target i
                    append outwardRefs (if item == undefined then #("undefined") else exactRef item)
                    if item != undefined do append pending item
                )
                local keyCount = undefined
                if (superClassOf target) == controller do
                (
                    require ((findItem #(PRS, Position_XYZ, Euler_XYZ, Bezier_Scale, Bezier_Float, Linear_Float, TCB_Float, Bezier_Position, TCB_Position, TCB_Rotation) (classOf target)) > 0) "unknown/wired/scripted controller unsupported"
                    keyCount = numKeys target
                    require (keyCount == 0 or keyCount == -1) "keyframed/unsupported controller refused"
                )
                append result #(exactRef target, properties target, keyCount, outwardRefs, referenceSet (refs.dependents target))
            )
        )
        result
    )
    fn polySnapshot base =
    (
        require ((classOf base) == Editable_Poly) "base is not Editable_Poly"
        local nv = polyop.getNumVerts base
        local ne = polyop.getNumEdges base
        local nf = polyop.getNumFaces base
        require (nv <= 64 and ne <= 256 and nf <= 32) "base snapshot operational ceiling"
        local deadV = polyop.getDeadVerts base
        local deadE = polyop.getDeadEdges base
        local deadF = polyop.getDeadFaces base
        local vertices = for i = 1 to nv collect
            (if deadV[i] then #("dead") else #(freeze (polyop.getVert base i), polyop.getVertFlags base i))
        local edges = for i = 1 to ne collect
            (if deadE[i] then #("dead") else #(polyop.getEdgeVerts base i, polyop.getEdgeFlags base i))
        local faces = for i = 1 to nf collect
            (if deadF[i] then #("dead") else #(polyop.getFaceVerts base i, polyop.getFaceFlags base i,
                polyop.getFaceMatID base i, polyop.getFaceSmoothGroup base i))
        local maps = #()
        local nm = polyop.getNumMaps base
        require (nm >= 0 and nm <= 100) "map channel ceiling"
        for channel = -2 to (nm-1) do
        (
            local supported = polyop.getMapSupport base channel
            local entry = #(channel, supported)
            if supported do
            (
                local mv = polyop.getNumMapVerts base channel
                local mf = polyop.getNumMapFaces base channel
                require (mv <= 256 and mf <= 32) "map geometry ceiling"
                append entry (for i = 1 to mv collect freeze (polyop.getMapVert base channel i))
                append entry (for i = 1 to mf collect (if deadF[i] then #("dead") else polyop.getMapFace base channel i))
            )
            append maps entry
        )
        -- VData/EData cannot be ignored: crease/weight edits may not change verts.
        local data = #()
        local vn = polyop.getNumVDataChannels base
        local en = polyop.getNumEDataChannels base
        require (vn >= 0 and vn <= 100 and en >= 0 and en <= 100) "data channel ceiling"
        for channel = 1 to vn do
        (
            local support = polyop.getVDataChannelSupport base channel
            append data #("v", channel, support, if support then (for i = 1 to nv collect (if deadV[i] then undefined else polyop.getVDataValue base channel i)) else undefined)
        )
        for channel = 1 to en do
        (
            local support = polyop.getEDataChannelSupport base channel
            append data #("e", channel, support, if support then (for i = 1 to ne collect (if deadE[i] then undefined else polyop.getEDataValue base channel i)) else undefined)
        )
        #(nv, ne, nf, freeze deadV, freeze deadE, freeze deadF, vertices, edges, faces, maps, data,
          freeze (polyop.getVertSelection base), freeze (polyop.getEdgeSelection base), freeze (polyop.getFaceSelection base))
    )
    fn evaluatedSnapshot node =
    (
        local msh = undefined
        local result = undefined
        try
        (
            msh = snapshotAsMesh node
            local nv = getNumVerts msh
            local nf = getNumFaces msh
            require (nv <= 128 and nf <= 96) "evaluated mesh budget exceeded"
            require (nf == 96) "evaluated triangle prediction mismatch"
            result = #(nv, nf, for i = 1 to nv collect freeze (getVert msh i),
              for i = 1 to nv collect freeze (getNormal msh i),
              for i = 1 to nf collect #(freeze (getFace msh i), getFaceMatID msh i,
                getFaceSmoothGroup msh i, getEdgeVis msh i 1, getEdgeVis msh i 2, getEdgeVis msh i 3))
            delete msh
            msh = undefined
        )
        catch
        (
            local reason = getCurrentException()
            local disposed = true
            try (if msh != undefined do delete msh) catch (disposed = false)
            require disposed "INCOMPLETE: exact in-memory snapshot disposal failed"
            throw reason
        )
        result
    )
    fn nodeSnapshot node =
    (
        require (isValidNode node) "invalid exact node reference"
        require ((node.parent == undefined or node.parent == rootNode) and node.children.count == 0) "parent/children not standalone"
        require (node.material == undefined) "material assigned: unsupported replay state"
        require (node.modifiers.count == 1 and classOf node.modifiers[1] == Shell) "stack mismatch"
        local shellMod = node.modifiers[1]
        require (shellMod.innerAmount == 0.0 and shellMod.outerAmount == 300.0 and shellMod.segments == 1) "Shell parameter edit"
        local explicitNames = #(#name, #wirecolor, #isHidden, #isFrozen, #renderable, #primaryVisibility,
            #secondaryVisibility, #castShadows, #receiveShadows, #applyAtmospherics, #renderOccluded,
            #visibility, #inheritVisibility, #showFrozenInGray, #displayByLayer, #renderByLayer,
            #motionByLayer, #colorByLayer, #boxmode, #backfacecull, #allEdges, #vertexTicks, #xray,
            #showTrajectory, #isSelected, #objectOffsetPos, #objectOffsetRot, #objectOffsetScale,
            #transform, #objectTransform, #parent, #layer, #material)
        local explicitState = for p in explicitNames collect
            #(p, if isProperty node p then freeze (getProperty node p) else #("absent"))
        local instanceUsers = for other in objects where other.baseObject == node.baseObject collect other
        require (instanceUsers.count == 1 and instanceUsers[1] == node) "shared base object dependency/instance"
        local userBuffer = getUserPropBuffer node
        require (userBuffer.count <= 4096) "unsupported user property buffer size"
        #(exactRef node, exactRef node.baseObject, exactRef shellMod,
          shellMod.enabled, shellMod.enabledInViews, shellMod.enabledInRenders,
          explicitState, userBuffer, properties node.layer,
          polySnapshot node.baseObject, evaluatedSnapshot node, graphSnapshot node)
    )
    fn censusGuard node =
    (
        require (objects.count <= 64) "scene census operational ceiling"
        local nodes = for other in objects collect other
        require (nodes.count == 1 and nodes[1] == node) "scene census changed; collisions/dependencies are not owned"
        local nameMatches = 0
        local tagMatches = 0
        for other in nodes do
        (
            if (toLower other.name) == (toLower wallName) do nameMatches += 1
            if (getUserProp other tagKey) == tagValue do tagMatches += 1
        )
        require (nameMatches == 1 and node.name == wallName and tagMatches == 1) "copied-tag or matching-name collision"
        require ((getUserProp node tagKey) == tagValue) "ownership tag edit"
    )
    fn environmentSnapshot =
    (
        #(exactRef rootNode, maxFilePath, maxFileName, currentTime as integer,
          referenceSet (selection as array), subObjectLevel)
    )

    try
    (
        -- Must precede even replay inspection, registry writes, or constructors.
        unitsGuard()
        require (maxFilePath == "" and maxFileName == "") "session-only runtime refuses saved/loaded scene"
        require (globalVars.isGlobal registryKey) "missing explicit armed session registry; never auto-adopt/re-arm"
        registryWitness = globalVars.get registryKey
        require (isProperty registryWitness #values) "registry has no exact structured lease"
        lease = registryWitness.values
        require ((classOf lease) == Array and lease.count == 10) "invalid registry; do not overwrite caller global"
        require (lease[1] == "p3-session-registry-2" and lease[2] == artifactIdentity and lease[3] == artifactBinding and lease[4] == ownerNamespace) "registry identity mismatch"
        require ((classOf lease[6]) == String and lease[6].count >= 16 and lease[6].count <= 128) "missing bounded external lease witness"
        require (same lease[7] (environmentSnapshot())) "scene witness/selection/time state changed"
        if lease[5] == "COMMITTED" then
        (
            stage = "replay-read-only"
            local node = lease[8]
            require (isValidNode node) "registry exact node invalid; no name-based recovery"
            censusGuard node
            require (same lease[9] (nodeSnapshot node)) "baseline changed or state not comparable"
            require (getSaveRequired() == lease[10]) "scene dirty-state changed"
            unitsGuard()
            -- Current bounded readers have NOT established completeness for
            -- specified normals and all native/custom mesh metadata. Comparing
            -- known fields is evidence, never permission to invent unchanged.
            print ("P3_OBSERVED_BASELINE_EQUAL|identity=" + artifactIdentity)
            require false "INCOMPLETE_REPLAY: specified-normal/native-metadata comparison unverified; no safe NOOP claim"
        )
        else
        (
            stage = "pre-create"
            require (lease[5] == "ARMED" and lease[8] == undefined and lease[9] == undefined) "lease spent/building/poisoned; refuse implicit recovery"
            require (objects.count == 0 and selection.count == 0) "first create requires empty unnamed scene"
            local environmentBefore = environmentSnapshot()
            unitsGuard()
            -- Only an explicit fresh arm can authorize this state transition.
            lease[5] = "BUILDING"
            attemptStarted = true
            local node = Editable_Mesh()
            append createdRefs node
            local initialHandle = getHandleByAnim node
            require (isValidNode node and initialHandle != undefined) "new exact node unavailable"
            append createdHandles initialHandle
            node.name = wallName
            stage = "convert"
            local converted = convertTo node Editable_Poly
            -- Current calibrated probe: returned node retains the original handle.
            -- Historical P1 invalidation is not assumed universally true or false.
            if isValidNode converted do node = converted
            -- Recover ONLY via our previously captured exact anim handle.
            if not isValidNode node do node = getAnimByHandle initialHandle
            require (isValidNode node and (getHandleByAnim node) == initialHandle and objects.count == 1 and node.name == wallName) "conversion identity not preserved; no lookup by name"
            createdRefs[1] = node
            stage = "grid-vertices"
            local vertexIds = #()
            for point in expectedPoints do
            (
                local id = polyop.createVert node point
                require ((classOf id) == Integer and id > 0 and id <= polyop.getNumVerts node and (findItem vertexIds id) == 0) "invalid/duplicate returned vertex ID"
                append vertexIds id
                require ((polyop.getVert node id) == point) "created vertex readback mismatch"
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
                require ((classOf id) == Integer and id > 0 and id <= polyop.getNumFaces node and (findItem faceIds id) == 0) "invalid/duplicate returned face ID"
                append faceIds id
                require (same (polyop.getFaceVerts node id) actualLoop) "created face loop readback mismatch"
                if cutSlots[slot] do cutIds[id] = true
            )
            update node
            require ((polyop.getNumFaces node) == 15) "grid count readback mismatch"
            print ("P3_FACE_IDS|" + (faceIds as string) + "|P3_CUT_IDS|" + (cutIds as string))
            stage = "opening-delete-once"
            if cutIds.numberSet > 0 do polyop.deleteFaces node cutIds delIsoVerts:false
            update node
            local deadFaces = polyop.getDeadFaces node
            local activeCount = (polyop.getNumFaces node) - deadFaces.numberSet
            require (activeCount == 12) "active base count readback mismatch"
            print ("P3_BASE_READBACK|active_polygons=" + (activeCount as string))
            stage = "one-shell"
            local shellMod = Shell innerAmount:0.0 outerAmount:300.0 segments:1
            addModifier node shellMod
            update node
            require (node.modifiers.count == 1 and node.modifiers[1] == shellMod) "actual Shell reference/stack mismatch"
            setUserProp node tagKey tagValue
            censusGuard node
            require (same environmentBefore (environmentSnapshot())) "constructor changed protected environment state"
            stage = "exact-baseline"
            local baseline = nodeSnapshot node
            require (same baseline (nodeSnapshot node)) "baseline unstable/uncomparable"
            unitsGuard()
            require ((globalVars.get registryKey) == registryWitness) "external exact registry witness changed"
            lease[8] = node
            lease[9] = baseline
            lease[10] = getSaveRequired()
            -- Last transition only after every read-back and baseline gate.
            lease[5] = "COMMITTED"
            print ("P3_CREATED_UNVERIFIED|identity=" + artifactIdentity + "|handle=" + ((getHandleByAnim node) as string) + "|baseline=bounded-readback|replay=INCOMPLETE_METADATA")
        )
    )
    catch
    (
        local reason = getCurrentException()
        local residual = #()
        -- No prefix/name enumeration, undo, registry replacement, or replay deletion.
        for i = 1 to createdRefs.count do
        (
            local exactNode = createdRefs[i]
            if not isValidNode exactNode and i <= createdHandles.count do
                try (exactNode = getAnimByHandle createdHandles[i]) catch ()
            try
            (
                if isValidNode exactNode do
                (
                    unitsGuard()
                    require (i <= createdHandles.count and (getHandleByAnim exactNode) == createdHandles[i]) "cleanup exact handle mismatch"
                    require (objects.count == 1 and exactNode.children.count == 0 and (exactNode.parent == undefined or exactNode.parent == rootNode)) "cleanup foreign census/hierarchy; leave residue"
                    local baseUsers = for other in objects where other.baseObject == exactNode.baseObject collect other
                    require (baseUsers.count == 1 and baseUsers[1] == exactNode) "cleanup shared base; leave residue"
                    delete exactNode
                )
            ) catch ()
            try (if isValidNode exactNode do append residual (getHandleByAnim exactNode)) catch (append residual "UNRESOLVED_EXACT_REFERENCE")
        )
        if createdRefs.count > 0 and objects.count != 0 and residual.count == 0 do append residual "UNRESOLVED_CONVERSION_OR_FOREIGN_CENSUS"
        if attemptStarted do
        (
            lease[5] = "POISONED"
            lease[8] = createdRefs
            lease[9] = residual
        )
        local status = if residual.count > 0 then "P3_INCOMPLETE_RESIDUAL" else "P3_REFUSED"
        print (status + "|stage=" + stage + "|residual=" + (residual as string) + "|" + (reason as string))
        throw (status + "|stage=" + stage + "|" + (reason as string))
    )
)
