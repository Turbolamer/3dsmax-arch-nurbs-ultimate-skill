-- OFFLINE DRAFT ONLY. Main-only after independent review and fresh admission.
-- The independent EData control design is in DESIGN.md; this file's C04/C05
-- readings depend on the target setter and are NOT a substitute for it.
-- One owned quad; no globals, modifiers, reset, save, named lookup, or deletion
-- by handle. A lack of a stage result or any exception is INCOMPLETE, not PASS.
(
    local log = "P3_EDATA_DIAG_V1"
    local stage = "INIT"
    local mainOK = false
    local cleanupOK = false
    local cleanupStatus = "NOT_STARTED"
    local constructionAttempted = false
    local conversionAttempted = false
    local deleteAttempted = false
    local admitted = false
    local orig = undefined
    local converted = undefined
    local ownedHandle = undefined
    local originalRoot = undefined
    local originalBase = undefined
    local base = undefined
    local initialDirty = undefined
    local initialLayerCount = undefined
    local ids = #()
    local edgePair = undefined
    local vertexBefore = undefined
    local face = undefined
    local vCount0 = undefined
    local vCount1 = undefined
    local eCount0 = undefined
    local eCount1 = undefined
    local supportV = undefined
    local supportV3 = undefined
    local supportE = undefined
    local vFirst = undefined
    local vRepeat = undefined
    local vEdited = undefined
    local eFirst = undefined
    local eRepeat = undefined
    local eEdited = undefined
    local eAltFirst = undefined
    local eAltEdited = undefined
    local altCount = -1
    local altUniform = false
    local wrongThrew = false
    local wrongMessage = ""
    local sawEFirst = false
    local sawERepeat = false
    local sawEEdited = false
    local targetError = ""
    local outcome = "INCOMPLETE"

    -- Outer catch guarantees a return path to cleanup on caught errors.
    -- Each relevant VData/EData API call below has its own stage/catch;
    -- unexpected validation exceptions are labeled and remain incomplete.
    try
    (
        stage = "S01_ADMISSION"
        try
        (
            initialDirty = getSaveRequired()
            originalRoot = rootNode
            initialLayerCount = LayerManager.count
            if objects.count != 0 or selection.count != 0 do throw "nonempty or selected scene"
            if maxFilePath != "" or maxFileName != "" do throw "named scene"
            if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "unit mismatch"
            if initialDirty != false or initialLayerCount != 1 do throw "dirty scene or layer count not one"
            admitted = true
            log += "|S01=OK"
        ) catch (log += "|S01=THROW:" + ((getCurrentException()) as string); throw "S01")

        stage = "S02_CONSTRUCT"
        constructionAttempted = true
        try (orig = Editable_Mesh(); log += "|S02=RETURNED")
        catch (log += "|S02=THROW:" + ((getCurrentException()) as string); throw "S02")

        stage = "S03_BIND"
        try
        (
            if orig == undefined or not isValidNode orig or objects.count != 1 do throw "constructor reference/census ambiguous"
            ownedHandle = getHandleByAnim orig
            if ownedHandle == undefined or (getAnimByHandle ownedHandle) != orig do throw "original handle roundtrip failed"
            if selection.count != 0 or rootNode != originalRoot do throw "selection or root changed"
            originalBase = orig.baseObject
            if originalBase == undefined do throw "original base missing"
            log += "|S03=OK"
        ) catch (log += "|S03=THROW:" + ((getCurrentException()) as string); throw "S03")

        stage = "S04_CONVERT"
        conversionAttempted = true
        try (converted = convertTo orig Editable_Poly; log += "|S04=RETURNED")
        catch (log += "|S04=THROW:" + ((getCurrentException()) as string); throw "S04")

        stage = "S05_CONVERSION_IDENTITY"
        try
        (
            if converted == undefined or not isValidNode converted or not isValidNode orig do throw "conversion candidate invalid"
            if converted != orig or (getHandleByAnim converted) != ownedHandle or (getAnimByHandle ownedHandle) != orig do throw "conversion identity uncertain"
            if objects.count != 1 or selection.count != 0 do throw "conversion census uncertain"
            base = orig.baseObject
            if base == undefined or (classOf base) != Editable_Poly do throw "converted base uncertain"
            log += "|S05=OK"
        ) catch (log += "|S05=THROW:" + ((getCurrentException()) as string); throw "S05")

        stage = "S06_VERTICES"
        try
        (
            for p in #([0,0,0], [10,0,0], [10,0,10], [0,0,10]) do
            (
                local vi = polyop.createVert orig p
                if classOf vi != Integer or vi < 1 or (findItem ids vi) != 0 do throw "vertex identity uncertain"
                append ids vi
            )
            log += "|S06=OK"
        ) catch (log += "|S06=THROW:" + ((getCurrentException()) as string); throw "S06")

        stage = "S07_FACE"
        try (face = polyop.createPolygon orig ids; if classOf face != Integer or face < 1 do throw "face identity uncertain"; log += "|S07=OK")
        catch (log += "|S07=THROW:" + ((getCurrentException()) as string); throw "S07")
        stage = "S08_UPDATE"
        try (update orig; log += "|S08=OK")
        catch (log += "|S08=THROW:" + ((getCurrentException()) as string); throw "S08")
        stage = "S09_TOPOLOGY"
        try
        (
            if (polyop.getNumVerts base) != 4 or (polyop.getNumEdges base) != 4 or (polyop.getNumFaces base) != 1 do throw "not a four-edge quad"
            edgePair = polyop.getEdgeVerts base 1
            vertexBefore = polyop.getVert base ids[1]
            if edgePair == undefined or edgePair.count != 2 or vertexBefore == undefined do throw "edge or vertex unreadable"
            log += "|S09=OK"
        ) catch (log += "|S09=THROW:" + ((getCurrentException()) as string); throw "S09")

        -- Calibrate a wrong-type error for the exact EData getter. The positive
        -- getter control is EData3's independent EditablePoly read at C04/C05.
        stage = "C01_WRONG_TYPE_GET_EDATA"
        try (polyop.getEDataValue undefined 3 1)
        catch (wrongThrew = true; wrongMessage = (getCurrentException()) as string)
        log += "|C01_wrongThrow=" + (wrongThrew as string) + "|C01_message=" + wrongMessage
        if not wrongThrew do throw "C01 wrong-type control did not throw"

        -- The retained VData11 probe is a separate historical observation;
        -- this is a fresh positive read on this node, with per-operation IDs.
        stage = "V01_GET_INITIAL_COUNT"
        try (vCount0 = polyop.getNumVDataChannels base; log += "|V01_count=" + (vCount0 as string))
        catch (log += "|V01=THROW:" + ((getCurrentException()) as string); throw "V01")
        if classOf vCount0 != Integer or vCount0 < 0 or vCount0 > 10 do throw "V01 unexpected channel domain; no shrink"
        stage = "V02_SET_COUNT"
        try (polyop.setNumVDataChannels base 11 keep:true; log += "|V02=OK")
        catch (log += "|V02=THROW:" + ((getCurrentException()) as string); throw "V02")
        stage = "V03_READ_COUNT"
        try (vCount1 = polyop.getNumVDataChannels base; log += "|V03_count=" + (vCount1 as string))
        catch (log += "|V03=THROW:" + ((getCurrentException()) as string); throw "V03")
        if vCount1 != 11 do throw "V03 count mismatch"
        stage = "V04_ENABLE_SUPPORT"
        try (polyop.setVDataChannelSupport base 11 true; log += "|V04=OK")
        catch (log += "|V04=THROW:" + ((getCurrentException()) as string); throw "V04")
        stage = "V05_READ_SUPPORT"
        try (supportV = polyop.getVDataChannelSupport base 11; log += "|V05_support=" + (supportV as string))
        catch (log += "|V05=THROW:" + ((getCurrentException()) as string); throw "V05")
        if supportV != true do throw "V05 support not true"
        local vertexBits = #{}
        vertexBits[ids[1]] = true
        stage = "V06_WRITE_FIRST"
        try (polyop.setVDataValue base 11 vertexBits 0.375; log += "|V06=OK")
        catch (log += "|V06=THROW:" + ((getCurrentException()) as string); throw "V06")
        stage = "V07_READ_FIRST"
        try (vFirst = polyop.getVDataValue base 11 ids[1]; log += "|V07_value=" + (vFirst as string))
        catch (log += "|V07=THROW:" + ((getCurrentException()) as string); throw "V07")
        stage = "V08_READ_REPEAT"
        try (vRepeat = polyop.getVDataValue base 11 ids[1]; log += "|V08_value=" + (vRepeat as string))
        catch (log += "|V08=THROW:" + ((getCurrentException()) as string); throw "V08")
        stage = "V09_WRITE_EDIT"
        try (polyop.setVDataValue base 11 vertexBits 0.625; log += "|V09=OK")
        catch (log += "|V09=THROW:" + ((getCurrentException()) as string); throw "V09")
        stage = "V10_READ_EDIT"
        try (vEdited = polyop.getVDataValue base 11 ids[1]; log += "|V10_value=" + (vEdited as string))
        catch (log += "|V10=THROW:" + ((getCurrentException()) as string); throw "V10")
        if vFirst != 0.375 or vRepeat != vFirst or vEdited != 0.625 do throw "VData positive failed"

        -- EData3 reproduction: VData11 is enabled, but VData3 is never enabled.
        -- Every count/support/write/read is logged before the next operation.
        stage = "E01_GET_INITIAL_COUNT"
        try (eCount0 = polyop.getNumEDataChannels base; log += "|E01_count=" + (eCount0 as string))
        catch (log += "|E01=THROW:" + ((getCurrentException()) as string); throw "E01")
        if classOf eCount0 != Integer or eCount0 < 0 or eCount0 > 2 do throw "E01 unexpected count; no shrink"
        stage = "E02_SET_COUNT"
        try (polyop.setNumEDataChannels base 3 keep:true; log += "|E02=OK")
        catch (log += "|E02=THROW:" + ((getCurrentException()) as string); throw "E02")
        stage = "E03_READ_COUNT"
        try (eCount1 = polyop.getNumEDataChannels base; log += "|E03_count=" + (eCount1 as string))
        catch (log += "|E03=THROW:" + ((getCurrentException()) as string); throw "E03")
        if eCount1 != 3 do throw "E03 count mismatch"
        stage = "E04_ENABLE_SUPPORT"
        try (polyop.setEDataChannelSupport base 3 true; log += "|E04=OK")
        catch (log += "|E04=THROW:" + ((getCurrentException()) as string); throw "E04")
        stage = "E05_READ_SUPPORT"
        try (supportE = polyop.getEDataChannelSupport base 3; log += "|E05_support=" + (supportE as string))
        catch (log += "|E05=THROW:" + ((getCurrentException()) as string); throw "E05")
        if supportE != true do throw "E05 support not true"
        stage = "E05B_READ_SUPPORT_REPEAT"
        try (supportE = polyop.getEDataChannelSupport base 3; log += "|E05B_support=" + (supportE as string))
        catch (log += "|E05B=THROW:" + ((getCurrentException()) as string); throw "E05B")
        if supportE != true do throw "E05B support changed"
        stage = "E06_READ_VDATA3_SUPPORT"
        try (supportV3 = polyop.getVDataChannelSupport base 3; log += "|E06_vdata3Support=" + (supportV3 as string))
        catch (log += "|E06=THROW:" + ((getCurrentException()) as string); throw "E06")
        if supportV3 != false do throw "E06 VData3 not independently unsupported; stop"

        -- Exact first write from edata3.ms. If it throws, STOP: do not enable
        -- VData3 or run an alternate write on this same contaminated attempt.
        stage = "E07_SET_FIRST"
        try (polyop.setEDataValue base 3 #{1} 0.375; log += "|E07=OK")
        catch (log += "|E07=THROW:" + ((getCurrentException()) as string); throw "E07")

        -- The target getter may throw even after the write. Record that error,
        -- then still try the separately documented selected-edge reader. Its
        -- output is a genuine read of data written by E07, not an invented value.
        stage = "E08_GET_FIRST"
        try (eFirst = polyop.getEDataValue base 3 1; sawEFirst = true; log += "|E08_value=" + (eFirst as string))
        catch (targetError = (getCurrentException()) as string; log += "|E08=THROW:" + targetError)
        stage = "C02_SELECT_EDGE"
        try (polyop.setEdgeSelection base #{1}; log += "|C02=OK")
        catch (log += "|C02=THROW:" + ((getCurrentException()) as string); throw "C02")
        stage = "C03_VERIFY_EDGE_SELECTION"
        try (if (polyop.getEdgeSelection base) != #{1} do throw "edge selection mismatch"; log += "|C03=OK")
        catch (log += "|C03=THROW:" + ((getCurrentException()) as string); throw "C03")
        stage = "C04_READ_EDGE_DATA_FIRST"
        try (eAltFirst = orig.getEdgeData 3 &altCount &altUniform; log += "|C04_value=" + (eAltFirst as string) + "|C04_count=" + (altCount as string) + "|C04_uniform=" + (altUniform as string))
        catch (log += "|C04=THROW:" + ((getCurrentException()) as string); throw "C04")
        if altCount != 1 or altUniform != true or eAltFirst != 0.375 do throw "C04 independent EData first read not calibrated"
        if not sawEFirst do throw "E08 getter failed, independent EData read succeeded"
        if eFirst != eAltFirst do throw "E08 getter and independent edge reader disagree"
        stage = "E09_GET_REPEAT"
        try (eRepeat = polyop.getEDataValue base 3 1; sawERepeat = true; log += "|E09_value=" + (eRepeat as string))
        catch (log += "|E09=THROW:" + ((getCurrentException()) as string); throw "E09")
        if eRepeat != eFirst do throw "E09 repeat mismatch"
        stage = "E10_SET_EDIT"
        try (polyop.setEDataValue base 3 #{1} 0.625; log += "|E10=OK")
        catch (log += "|E10=THROW:" + ((getCurrentException()) as string); throw "E10")
        stage = "E11_GET_EDIT"
        try (eEdited = polyop.getEDataValue base 3 1; sawEEdited = true; log += "|E11_value=" + (eEdited as string))
        catch (targetError = (getCurrentException()) as string; log += "|E11=THROW:" + targetError)
        stage = "C05_READ_EDGE_DATA_EDIT"
        try (altCount = -1; altUniform = false; eAltEdited = orig.getEdgeData 3 &altCount &altUniform; log += "|C05_value=" + (eAltEdited as string) + "|C05_count=" + (altCount as string) + "|C05_uniform=" + (altUniform as string))
        catch (log += "|C05=THROW:" + ((getCurrentException()) as string); throw "C05")
        if altCount != 1 or altUniform != true or eAltEdited != 0.625 do throw "C05 independent EData edit read not calibrated"
        if not sawEEdited or eEdited != eAltEdited do throw "E11 getter absent or mismatch"

        stage = "C06_GEOMETRY_UNCHANGED"
        try
        (
            local afterPair = polyop.getEdgeVerts base 1
            local afterVertex = polyop.getVert base ids[1]
            if (polyop.getNumVerts base) != 4 or (polyop.getNumEdges base) != 4 or (polyop.getNumFaces base) != 1 do throw "counts changed"
            if afterPair[1] != edgePair[1] or afterPair[2] != edgePair[2] do throw "edge endpoints changed"
            if afterVertex.x != vertexBefore.x or afterVertex.y != vertexBefore.y or afterVertex.z != vertexBefore.z do throw "vertex position changed"
            log += "|C06=OK"
        ) catch (log += "|C06=THROW:" + ((getCurrentException()) as string); throw "C06")
        mainOK = true
        outcome = "BOUNDED_OBSERVATION_NOT_ACCEPTANCE"
    )
    catch (log += "|MAIN_ERROR_AT=" + stage + ":" + ((getCurrentException()) as string))

    -- Delete only the original exact node, never a handle/name-reacquired one.
    -- If constructor/conversion may have returned an unknown candidate, if
    -- references/dependents cannot be classified, or if delete throws, leave
    -- all survivors alone and report residual/identity uncertainty. No retry.
    stage = "K01_CLEANUP"
    try
    (
        if not constructionAttempted then
        (
            if admitted and objects.count == 0 and selection.count == 0 then
            (
                cleanupOK = true
                cleanupStatus = "NO_CONSTRUCTION_ATTEMPT"
            )
            else cleanupStatus = "NOT_ADMITTED_NO_DELETE"
        )
        else
        (
            if orig == undefined or not isValidNode orig or ownedHandle == undefined do throw "original reference/handle unavailable"
            if (getHandleByAnim orig) != ownedHandle or (getAnimByHandle ownedHandle) != orig do throw "original reference continuity uncertain"
            if conversionAttempted and (converted == undefined or not isValidNode converted or converted != orig) do throw "conversion candidate unknown or different"
            if not conversionAttempted and orig.baseObject != originalBase do throw "original base continuity uncertain"
            if conversionAttempted and (base == undefined or orig.baseObject != base) do throw "converted base continuity uncertain"
            if rootNode != originalRoot or objects.count != 1 or selection.count != 0 do throw "root/census/selection uncertain"
            if maxFilePath != "" or maxFileName != "" or units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "scene path or units changed"
            if LayerManager.count != initialLayerCount or getSaveRequired() != initialDirty do throw "layer count or dirty observation changed; ownership context uncertain"
            if objects[1] != orig do throw "exact sole scene node differs"
            if orig.children.count != 0 or (orig.parent != undefined and orig.parent != rootNode) do throw "hierarchy uncertain"
            local users = for item in objects where item.baseObject == orig.baseObject collect item
            if users.count != 1 or users[1] != orig do throw "base shared or unreadable"
            -- refs.dependents may expose ordinary Max infrastructure. Node
            -- must have none; the base may depend on the exact original node
            -- alone. No undocumented infrastructure class is whitelisted.
            local nodeDependents = refs.dependents orig
            local baseDependents = refs.dependents orig.baseObject
            log += "|K01_nodeDeps=" + (nodeDependents.count as string) + "|K01_baseDeps=" + (baseDependents.count as string)
            if nodeDependents.count != 0 do throw "node dependents unclassified"
            for dep in baseDependents do (if dep != orig do throw "base dependent unclassified")
            deleteAttempted = true
            delete orig
            if isValidNode orig or objects.count != 0 or selection.count != 0 do throw "deletion verification uncertain"
            cleanupOK = true
            cleanupStatus = "EXACT_NODE_DELETED"
        )
    )
    catch
    (
        cleanupStatus = if deleteAttempted then "DELETE_OUTCOME_UNCERTAIN_NO_RETRY" else "RESIDUAL_OR_IDENTITY_UNCERTAIN_NO_DELETE"
        log += "|K01=THROW:" + ((getCurrentException()) as string)
    )
    if not cleanupOK do outcome = "INCOMPLETE_CLEANUP_OR_IDENTITY"
    if not mainOK and cleanupOK do outcome = "INCOMPLETE_PROBE"
    -- Residual identifiers are informational only, never deletion authority.
    try (log += "|RESID_originalRef=" + (orig as string)) catch (log += "|RESID_originalRef=UNREADABLE")
    try (log += "|RESID_originalValid=" + ((isValidNode orig) as string)) catch (log += "|RESID_originalValid=UNREADABLE")
    try (log += "|RESID_boundHandle=" + (ownedHandle as string)) catch (log += "|RESID_boundHandle=UNREADABLE")
    try (log += "|RESID_conversionRef=" + (converted as string)) catch (log += "|RESID_conversionRef=UNREADABLE")
    try (log += "|RESID_conversionValid=" + ((isValidNode converted) as string)) catch (log += "|RESID_conversionValid=UNREADABLE")
    try (if converted != undefined and isValidNode converted do log += "|RESID_conversionHandle=" + ((getHandleByAnim converted) as string)) catch (log += "|RESID_conversionHandle=UNREADABLE")
    -- Reporting itself is guarded: an unreadable or changed post-state cannot
    -- become PASS, and this code does not restore any changed state.
    try
    (
        local postObjects = objects.count
        local postSelection = selection.count
        local postDirty = getSaveRequired()
        local postLayers = LayerManager.count
        log += "|POST_objects=" + (postObjects as string) + "|POST_selection=" + (postSelection as string) + "|POST_dirty=" + (postDirty as string) + "|POST_layers=" + (postLayers as string)
        if admitted and (rootNode != originalRoot or maxFilePath != "" or maxFileName != "" or units.SystemType != #millimeters or units.SystemScale != 1.0 or postDirty != initialDirty or postLayers != initialLayerCount) do
        (
            log += "|POST_ENV_CHANGED=true"
            if cleanupOK do outcome = "INCOMPLETE_ENVIRONMENT_CHANGED"
        )
    )
    catch (cleanupOK = false; outcome = "INCOMPLETE_POSTSTATE"; log += "|POST=THROW:" + ((getCurrentException()) as string))
    log += "|mainOK=" + (mainOK as string) + "|cleanupOK=" + (cleanupOK as string) + "|cleanupStatus=" + cleanupStatus + "|dirtyBefore=" + (initialDirty as string) + "|outcome=" + outcome
    log
)
