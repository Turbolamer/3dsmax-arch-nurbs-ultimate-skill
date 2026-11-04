-- NEGATIVE_MUTATED_stored_factor: AUDIT UNIT ONLY; fresh test identity; NOT accepted production pair.
-- P3.1 operational artifact; generated predictions are NOT live QA.
-- Route A: actual returned vertex/face IDs; exact references; ONE Shell.
-- This file requires fileIn. Helpers are scoped locally; no caller variables.
(
    local artifactIdentity = "edfe77ec5daf8de01dcd80fa1d5ed373c3a4383838e35606ef9f95fa65e173c2"
    local ownerNamespace = "P3Unit03_Factor"
    local artifactBinding = "1f852d549f31623342a296be540c310f533950b1c744bb25bc8811c64ee9a09d"
    local registryKey = "__P3W_cd2a8f7024233cf68dacb3d617052da23addf89746bb804b0e5c47adf430bdcf" as name
    local wallName = "P3Unit03_Factor__wall"
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
        p3RequireState (cmPerUnit == 0.1d0 and unitsPerCm == 11.0d0) "computed unit factor mismatch"
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
    fn p3FreezeState value depth:0 =
    (
        p3RequireState (depth < 16) "property nesting ceiling"
        local cls = classOf value
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
        p3RequireState (nv <= 64 and ne <= 256 and nf <= 32) "base snapshot operational ceiling"
        local deadV = polyop.getDeadVerts base
        local deadE = polyop.getDeadEdges base
        local deadF = polyop.getDeadFaces base
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
        p3RequireState (vn >= 0 and vn <= 100 and en >= 0 and en <= 100) "data channel ceiling"
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
        #(nv, ne, nf, p3FreezeState deadV, p3FreezeState deadE, p3FreezeState deadF, vertices, edges, faces, maps, data,
          p3FreezeState (polyop.getVertSelection base), p3FreezeState (polyop.getEdgeSelection base), p3FreezeState (polyop.getFaceSelection base))
    )
    fn p3EvaluatedSnapshot node =
    (
        local msh = undefined
        local result = undefined
        try
        (
            msh = snapshotAsMesh node
            local nv = getNumVerts msh
            local nf = getNumFaces msh
            p3RequireState (nv <= 128 and nf <= 96) "evaluated mesh budget exceeded"
            p3RequireState (nf == 96) "evaluated triangle prediction mismatch"
            result = #(nv, nf, for i = 1 to nv collect p3FreezeState (getVert msh i),
              for i = 1 to nv collect p3FreezeState (getNormal msh i),
              for i = 1 to nf collect #(p3FreezeState (getFace msh i), getFaceMatID msh i,
                getFaceSmoothGroup msh i, getEdgeVis msh i 1, getEdgeVis msh i 2, getEdgeVis msh i 3))
            delete msh
            msh = undefined
        )
        catch
        (
            local reason = getCurrentException()
            local disposed = true
            try (if msh != undefined do delete msh) catch (disposed = false)
            if not disposed do print "P3_INCOMPLETE|exact in-memory snapshot disposal failed"
            print ("P3_SNAPSHOT_REFUSED|" + (reason as string))
            throw
        )
        result
    )
    fn p3NodeSnapshot node =
    (
        p3RequireState (isValidNode node) "invalid exact node reference"
        p3RequireState ((node.parent == undefined or node.parent == rootNode) and node.children.count == 0) "parent/children not standalone"
        p3RequireState (node.material == undefined) "material assigned: unsupported replay state"
        p3RequireState (node.modifiers.count == 1 and classOf node.modifiers[1] == Shell) "stack mismatch"
        local shellMod = node.modifiers[1]
        p3RequireState (shellMod.innerAmount == 0.0 and shellMod.outerAmount == 300.0 and shellMod.segments == 1) "Shell parameter edit"
        local explicitNames = #(#name, #wirecolor, #isHidden, #isFrozen, #renderable, #primaryVisibility,
            #secondaryVisibility, #castShadows, #receiveShadows, #applyAtmospherics, #renderOccluded,
            #visibility, #inheritVisibility, #showFrozenInGray, #displayByLayer, #renderByLayer,
            #motionByLayer, #colorByLayer, #boxmode, #backfacecull, #allEdges, #vertexTicks, #xray,
            #showTrajectory, #isSelected, #objectOffsetPos, #objectOffsetRot, #objectOffsetScale,
            #transform, #objectTransform, #parent, #layer, #material)
        local explicitState = for p in explicitNames collect
            #(p, if isProperty node p then p3FreezeState (getProperty node p) else #("absent"))
        local instanceUsers = for other in objects where other.baseObject == node.baseObject collect other
        p3RequireState (instanceUsers.count == 1 and instanceUsers[1] == node) "shared base object dependency/instance"
        local userBuffer = getUserPropBuffer node
        p3RequireState (userBuffer.count <= 4096) "unsupported user property buffer size"
        #(p3ExactRef node, p3ExactRef node.baseObject, p3ExactRef shellMod,
          shellMod.enabled, shellMod.enabledInViews, shellMod.enabledInRenders,
          explicitState, userBuffer, p3ReadProperties node.layer,
          p3PolySnapshot node.baseObject, p3EvaluatedSnapshot node, p3GraphSnapshot node)
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
        #(p3ExactRef rootNode, maxFilePath, maxFileName, currentTime as integer,
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
        p3RequireState (p3SameState lease[7] (p3EnvironmentSnapshot())) "scene witness/selection/time state changed"
        if lease[5] == "COMMITTED" then
        (
            stage = "replay-read-only"
            local node = lease[8]
            p3RequireState (isValidNode node) "registry exact node invalid; no name-based recovery"
            p3CensusGuard node
            p3RequireState (p3SameState lease[9] (p3NodeSnapshot node)) "baseline changed or state not comparable"
            p3RequireState (getSaveRequired() == lease[10]) "scene dirty-state changed"
            p3UnitsGuard()
            -- Current bounded readers have NOT established completeness for
            -- specified normals and all native/custom mesh metadata. Comparing
            -- known fields is evidence, never permission to invent unchanged.
            print ("P3_OBSERVED_BASELINE_EQUAL|identity=" + artifactIdentity)
            p3RequireState false "INCOMPLETE_REPLAY: specified-normal/native-metadata comparison unverified; no safe NOOP claim"
        )
        else
        (
            stage = "pre-create"
            p3RequireState (lease[5] == "ARMED" and lease[8] == undefined and lease[9] == undefined) "lease spent/building/poisoned; refuse implicit recovery"
            p3RequireState (objects.count == 0 and selection.count == 0) "first create requires empty unnamed scene"
            local environmentBefore = p3EnvironmentSnapshot()
            p3UnitsGuard()
            -- Only an explicit fresh arm can authorize this state transition.
            lease[5] = "BUILDING"
            attemptStarted = true
            local node = Editable_Mesh()
            append createdRefs node
            local initialHandle = getHandleByAnim node
            p3RequireState (isValidNode node and initialHandle != undefined) "new exact node unavailable"
            append createdHandles initialHandle
            node.name = wallName
            stage = "convert"
            local converted = convertTo node Editable_Poly
            -- Current calibrated probe: returned node retains the original handle.
            -- Historical P1 invalidation is not assumed universally true or false.
            if isValidNode converted do node = converted
            -- Recover ONLY via our previously captured exact anim handle.
            if not isValidNode node do node = getAnimByHandle initialHandle
            p3RequireState (isValidNode node and (getHandleByAnim node) == initialHandle and objects.count == 1 and node.name == wallName) "conversion identity not preserved; no lookup by name"
            createdRefs[1] = node
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
            p3RequireState ((globalVars.get registryKey) == registryWitness) "external exact registry witness changed"
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
                    p3UnitsGuard()
                    p3RequireState (i <= createdHandles.count and (getHandleByAnim exactNode) == createdHandles[i]) "cleanup exact handle mismatch"
                    p3RequireState (objects.count == 1 and exactNode.children.count == 0 and (exactNode.parent == undefined or exactNode.parent == rootNode)) "cleanup foreign census/hierarchy; leave residue"
                    local baseUsers = for other in objects where other.baseObject == exactNode.baseObject collect other
                    p3RequireState (baseUsers.count == 1 and baseUsers[1] == exactNode) "cleanup shared base; leave residue"
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
        throw
    )
)
