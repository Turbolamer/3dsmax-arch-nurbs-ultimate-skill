-- OFFLINE DRAFT ONLY; independent review and fresh admission required.
-- Separate one-node attempt. Uses EditablePoly.setEdgeData/getEdgeData for an
-- independent edge-data read even if polyop.setEDataValue cannot write.
-- Channel-index equivalence to polyop channel 3 is NOT assumed or proven.
(
    local out = "P3_EDATA_ALTERNATE_V1"
    local stage = "INIT"
    local attempted = false
    local converting = false
    local deleting = false
    local admitted = false
    local orig = undefined
    local converted = undefined
    local h = undefined
    local base = undefined
    local beforeBase = undefined
    local beforeRoot = undefined
    local beforeDirty = undefined
    local beforeLayers = undefined
    local ids = #()
    local n = undefined
    local v = undefined
    local va = undefined
    local vb = undefined
    local ec = undefined
    local supported = undefined
    local selectedCount = -1
    local uniform = false
    local edgeFirst = undefined
    local edgeRepeat = undefined
    local edgeEdited = undefined
    local edge2Before = undefined
    local edge2After = undefined
    local targetFirst = undefined
    local targetEdited = undefined
    local targetFirstOK = false
    local targetEditedOK = false
    local wrong = false
    local dataOK = false
    local cleanupOK = false
    local cleanup = "NOT_STARTED"
    local result = "INCOMPLETE"
    try
    (
        stage = "A01_ADMISSION"
        try
        (
            beforeDirty = getSaveRequired(); beforeLayers = LayerManager.count; beforeRoot = rootNode
            if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "scene not empty unnamed unselected"
            if units.SystemType != #millimeters or units.SystemScale != 1.0 or beforeDirty != false or beforeLayers != 1 do throw "environment not admitted"
            admitted = true; out += "|A01=OK"
        ) catch (out += "|A01=THROW:" + ((getCurrentException()) as string); throw "A01")
        stage = "A02_CONSTRUCT"; attempted = true
        try (orig = Editable_Mesh(); out += "|A02=RETURNED")
        catch (out += "|A02=THROW:" + ((getCurrentException()) as string); throw "A02")
        stage = "A03_BIND"
        try
        (
            if orig == undefined or not isValidNode orig or objects.count != 1 do throw "constructor result uncertain"
            h = getHandleByAnim orig
            if h == undefined or (getAnimByHandle h) != orig or rootNode != beforeRoot or selection.count != 0 do throw "identity/census uncertain"
            beforeBase = orig.baseObject
            if beforeBase == undefined do throw "base unavailable"
            out += "|A03=OK"
        ) catch (out += "|A03=THROW:" + ((getCurrentException()) as string); throw "A03")
        stage = "A04_CONVERT"; converting = true
        try (converted = convertTo orig Editable_Poly; out += "|A04=RETURNED")
        catch (out += "|A04=THROW:" + ((getCurrentException()) as string); throw "A04")
        stage = "A05_CONVERSION_IDENTITY"
        try
        (
            if converted == undefined or not isValidNode converted or not isValidNode orig or converted != orig do throw "conversion reference uncertain"
            if (getHandleByAnim converted) != h or (getAnimByHandle h) != orig or objects.count != 1 or selection.count != 0 do throw "conversion continuity uncertain"
            base = orig.baseObject
            if base == undefined or (classOf base) != Editable_Poly do throw "converted base unavailable"
            out += "|A05=OK"
        ) catch (out += "|A05=THROW:" + ((getCurrentException()) as string); throw "A05")
        stage = "A06_VERTICES"
        try
        (
            for p in #([0,0,0], [10,0,0], [10,0,10], [0,0,10]) do
            (
                local vi = polyop.createVert orig p
                if classOf vi != Integer or vi < 1 or (findItem ids vi) != 0 do throw "vertex uncertain"
                append ids vi
            )
            out += "|A06=OK"
        ) catch (out += "|A06=THROW:" + ((getCurrentException()) as string); throw "A06")
        stage = "A07_FACE"
        try (local f = polyop.createPolygon orig ids; if classOf f != Integer or f < 1 do throw "face uncertain"; out += "|A07=OK")
        catch (out += "|A07=THROW:" + ((getCurrentException()) as string); throw "A07")
        stage = "A08_UPDATE"
        try (update orig; out += "|A08=OK")
        catch (out += "|A08=THROW:" + ((getCurrentException()) as string); throw "A08")
        stage = "A09_TOPOLOGY"
        try
        (
            if (polyop.getNumVerts base) != 4 or (polyop.getNumEdges base) != 4 or (polyop.getNumFaces base) != 1 do throw "not a quad"
            out += "|A09=OK"
        ) catch (out += "|A09=THROW:" + ((getCurrentException()) as string); throw "A09")

        stage = "N01_WRONG_TYPE_TARGET_GET"
        try (polyop.getEDataValue undefined 3 1)
        catch (wrong = true; out += "|N01=THROW:" + ((getCurrentException()) as string))
        if not wrong do throw "N01 wrong-type did not throw"
        stage = "V01_INITIAL_COUNT"
        try (n = polyop.getNumVDataChannels base; out += "|V01_count=" + (n as string))
        catch (out += "|V01=THROW:" + ((getCurrentException()) as string); throw "V01")
        if classOf n != Integer or n < 0 or n > 10 do throw "V01 unexpected domain; no shrink"
        stage = "V02_SET_COUNT"
        try (polyop.setNumVDataChannels base 11 keep:true; out += "|V02=OK")
        catch (out += "|V02=THROW:" + ((getCurrentException()) as string); throw "V02")
        stage = "V03_READ_COUNT"
        try (n = polyop.getNumVDataChannels base; out += "|V03_count=" + (n as string))
        catch (out += "|V03=THROW:" + ((getCurrentException()) as string); throw "V03")
        if n != 11 do throw "V03 count mismatch"
        stage = "V04_SET_SUPPORT"
        try (polyop.setVDataChannelSupport base 11 true; out += "|V04=OK")
        catch (out += "|V04=THROW:" + ((getCurrentException()) as string); throw "V04")
        stage = "V05_READ_SUPPORT"
        try (v = polyop.getVDataChannelSupport base 11; out += "|V05_support=" + (v as string))
        catch (out += "|V05=THROW:" + ((getCurrentException()) as string); throw "V05")
        if v != true do throw "V05 support mismatch"
        local vertexBits = #{}; vertexBits[ids[1]] = true
        stage = "V06_SET_FIRST"
        try (polyop.setVDataValue base 11 vertexBits 0.375; out += "|V06=OK")
        catch (out += "|V06=THROW:" + ((getCurrentException()) as string); throw "V06")
        stage = "V07_GET_FIRST"
        try (va = polyop.getVDataValue base 11 ids[1]; out += "|V07_value=" + (va as string))
        catch (out += "|V07=THROW:" + ((getCurrentException()) as string); throw "V07")
        stage = "V08_SET_EDIT"
        try (polyop.setVDataValue base 11 vertexBits 0.625; out += "|V08=OK")
        catch (out += "|V08=THROW:" + ((getCurrentException()) as string); throw "V08")
        stage = "V09_GET_EDIT"
        try (vb = polyop.getVDataValue base 11 ids[1]; out += "|V09_value=" + (vb as string))
        catch (out += "|V09=THROW:" + ((getCurrentException()) as string); throw "V09")
        if va != 0.375 or vb != 0.625 do throw "VData control failed"

        stage = "E01_INITIAL_COUNT"
        try (ec = polyop.getNumEDataChannels base; out += "|E01_count=" + (ec as string))
        catch (out += "|E01=THROW:" + ((getCurrentException()) as string); throw "E01")
        if classOf ec != Integer or ec < 0 or ec > 2 do throw "E01 unexpected domain; no shrink"
        stage = "E02_SET_COUNT"
        try (polyop.setNumEDataChannels base 3 keep:true; out += "|E02=OK")
        catch (out += "|E02=THROW:" + ((getCurrentException()) as string); throw "E02")
        stage = "E03_GET_COUNT"
        try (ec = polyop.getNumEDataChannels base; out += "|E03_count=" + (ec as string))
        catch (out += "|E03=THROW:" + ((getCurrentException()) as string); throw "E03")
        if ec != 3 do throw "E03 count mismatch"
        stage = "E04_SET_SUPPORT"
        try (polyop.setEDataChannelSupport base 3 true; out += "|E04=OK")
        catch (out += "|E04=THROW:" + ((getCurrentException()) as string); throw "E04")
        stage = "E05_GET_SUPPORT"
        try (supported = polyop.getEDataChannelSupport base 3; out += "|E05_support=" + (supported as string))
        catch (out += "|E05=THROW:" + ((getCurrentException()) as string); throw "E05")
        if supported != true do throw "E05 support mismatch"

        -- Calibrate that the separate reader can distinguish selected edges.
        stage = "C01_SELECT_EDGE2"
        try (polyop.setEdgeSelection base #{2}; out += "|C01=OK")
        catch (out += "|C01=THROW:" + ((getCurrentException()) as string); throw "C01")
        stage = "C02_VERIFY_EDGE2"
        try (if (polyop.getEdgeSelection base) != #{2} do throw "edge 2 selection mismatch"; out += "|C02=OK")
        catch (out += "|C02=THROW:" + ((getCurrentException()) as string); throw "C02")
        stage = "C03_GET_EDGE2_BEFORE"
        try (selectedCount = -1; uniform = false; edge2Before = orig.getEdgeData 3 &selectedCount &uniform; out += "|C03_value=" + (edge2Before as string) + "|C03_count=" + (selectedCount as string) + "|C03_uniform=" + (uniform as string))
        catch (out += "|C03=THROW:" + ((getCurrentException()) as string); throw "C03")
        if selectedCount != 1 or uniform != true or classOf edge2Before != Float do throw "C03 not a calibrated read"
        stage = "C04_SELECT_EDGE1"
        try (polyop.setEdgeSelection base #{1}; out += "|C04=OK")
        catch (out += "|C04=THROW:" + ((getCurrentException()) as string); throw "C04")
        stage = "C05_VERIFY_EDGE1"
        try (if (polyop.getEdgeSelection base) != #{1} do throw "edge 1 selection mismatch"; out += "|C05=OK")
        catch (out += "|C05=THROW:" + ((getCurrentException()) as string); throw "C05")
        stage = "C06_ALT_WRITE_FIRST"
        try (orig.setEdgeData 3 0.375; out += "|C06=OK")
        catch (out += "|C06=THROW:" + ((getCurrentException()) as string); throw "C06")
        stage = "C07_ALT_READ_FIRST"
        try (selectedCount = -1; uniform = false; edgeFirst = orig.getEdgeData 3 &selectedCount &uniform; out += "|C07_value=" + (edgeFirst as string) + "|C07_count=" + (selectedCount as string) + "|C07_uniform=" + (uniform as string))
        catch (out += "|C07=THROW:" + ((getCurrentException()) as string); throw "C07")
        if selectedCount != 1 or uniform != true or edgeFirst != 0.375 do throw "C07 alternate first read failed"
        stage = "C08_ALT_READ_REPEAT"
        try (selectedCount = -1; uniform = false; edgeRepeat = orig.getEdgeData 3 &selectedCount &uniform; out += "|C08_value=" + (edgeRepeat as string) + "|C08_count=" + (selectedCount as string) + "|C08_uniform=" + (uniform as string))
        catch (out += "|C08=THROW:" + ((getCurrentException()) as string); throw "C08")
        if selectedCount != 1 or uniform != true or edgeRepeat != edgeFirst do throw "C08 alternate repeat failed"
        stage = "T01_TARGET_GET_FIRST"
        try (targetFirst = polyop.getEDataValue base 3 1; targetFirstOK = true; out += "|T01_value=" + (targetFirst as string))
        catch (out += "|T01=THROW:" + ((getCurrentException()) as string))
        stage = "C09_ALT_WRITE_EDIT"
        try (orig.setEdgeData 3 0.625; out += "|C09=OK")
        catch (out += "|C09=THROW:" + ((getCurrentException()) as string); throw "C09")
        stage = "C10_ALT_READ_EDIT"
        try (selectedCount = -1; uniform = false; edgeEdited = orig.getEdgeData 3 &selectedCount &uniform; out += "|C10_value=" + (edgeEdited as string) + "|C10_count=" + (selectedCount as string) + "|C10_uniform=" + (uniform as string))
        catch (out += "|C10=THROW:" + ((getCurrentException()) as string); throw "C10")
        if selectedCount != 1 or uniform != true or edgeEdited != 0.625 do throw "C10 alternate edit read failed"
        stage = "T02_TARGET_GET_EDIT"
        try (targetEdited = polyop.getEDataValue base 3 1; targetEditedOK = true; out += "|T02_value=" + (targetEdited as string))
        catch (out += "|T02=THROW:" + ((getCurrentException()) as string))
        stage = "C11_SELECT_EDGE2"
        try (polyop.setEdgeSelection base #{2}; out += "|C11=OK")
        catch (out += "|C11=THROW:" + ((getCurrentException()) as string); throw "C11")
        stage = "C12_VERIFY_EDGE2"
        try (if (polyop.getEdgeSelection base) != #{2} do throw "edge 2 selection mismatch"; out += "|C12=OK")
        catch (out += "|C12=THROW:" + ((getCurrentException()) as string); throw "C12")
        stage = "C13_GET_EDGE2_AFTER"
        try (selectedCount = -1; uniform = false; edge2After = orig.getEdgeData 3 &selectedCount &uniform; out += "|C13_value=" + (edge2After as string) + "|C13_count=" + (selectedCount as string) + "|C13_uniform=" + (uniform as string))
        catch (out += "|C13=THROW:" + ((getCurrentException()) as string); throw "C13")
        if selectedCount != 1 or uniform != true or edge2After != edge2Before do throw "C13 unselected edge changed/ambiguous"
        -- Both alternate values are observed before assessing target errors.
        out += "|ALT_POSITIVE_CONTROL=OBSERVED"
        if not targetFirstOK or not targetEditedOK or targetFirst != edgeFirst or targetEdited != edgeEdited do throw "target getter or channel correspondence not established"
        dataOK = true; result = "BOUNDED_CROSSCHECK_NOT_ACCEPTANCE"
    ) catch (out += "|MAIN_ERROR_AT=" + stage + ":" + ((getCurrentException()) as string))

    stage = "K01_CLEANUP"
    try
    (
        if not attempted then
        (
            if admitted and objects.count == 0 and selection.count == 0 then (cleanupOK = true; cleanup = "NO_CONSTRUCTION_ATTEMPT")
            else cleanup = "NOT_ADMITTED_NO_DELETE"
        )
        else
        (
            if orig == undefined or not isValidNode orig or h == undefined do throw "original reference unavailable"
            if (getHandleByAnim orig) != h or (getAnimByHandle h) != orig do throw "original continuity uncertain"
            if converting and (converted == undefined or not isValidNode converted or converted != orig) do throw "conversion candidate unknown/different"
            if not converting and orig.baseObject != beforeBase do throw "initial base continuity uncertain"
            if converting and (base == undefined or orig.baseObject != base) do throw "converted base continuity uncertain"
            if rootNode != beforeRoot or objects.count != 1 or selection.count != 0 or objects[1] != orig do throw "scene/identity uncertain"
            if maxFilePath != "" or maxFileName != "" or units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "scene path or units changed"
            if LayerManager.count != beforeLayers or getSaveRequired() != beforeDirty do throw "layer count or dirty observation changed; ownership context uncertain"
            if orig.children.count != 0 or (orig.parent != undefined and orig.parent != rootNode) do throw "hierarchy uncertain"
            local users = for item in objects where item.baseObject == orig.baseObject collect item
            if users.count != 1 or users[1] != orig do throw "shared base or neighbor"
            local nodeDeps = refs.dependents orig
            local baseDeps = refs.dependents orig.baseObject
            out += "|K01_nodeDeps=" + (nodeDeps.count as string) + "|K01_baseDeps=" + (baseDeps.count as string)
            if nodeDeps.count != 0 do throw "node dependencies unclassified"
            for dep in baseDeps do (if dep != orig do throw "base dependency unclassified")
            deleting = true; delete orig
            if isValidNode orig or objects.count != 0 or selection.count != 0 do throw "delete verification uncertain"
            cleanupOK = true; cleanup = "EXACT_NODE_DELETED"
        )
    )
    catch
    (
        cleanup = if deleting then "DELETE_OUTCOME_UNCERTAIN_NO_RETRY" else "RESIDUAL_OR_IDENTITY_UNCERTAIN_NO_DELETE"
        out += "|K01=THROW:" + ((getCurrentException()) as string)
    )
    if not cleanupOK do result = "INCOMPLETE_CLEANUP_OR_IDENTITY"
    if not dataOK and cleanupOK do result = "INCOMPLETE_PROBE"
    try (out += "|RESID_originalRef=" + (orig as string)) catch (out += "|RESID_originalRef=UNREADABLE")
    try (out += "|RESID_originalValid=" + ((isValidNode orig) as string)) catch (out += "|RESID_originalValid=UNREADABLE")
    try (out += "|RESID_boundHandle=" + (h as string)) catch (out += "|RESID_boundHandle=UNREADABLE")
    try (out += "|RESID_conversionRef=" + (converted as string)) catch (out += "|RESID_conversionRef=UNREADABLE")
    try (out += "|RESID_conversionValid=" + ((isValidNode converted) as string)) catch (out += "|RESID_conversionValid=UNREADABLE")
    try (if converted != undefined and isValidNode converted do out += "|RESID_conversionHandle=" + ((getHandleByAnim converted) as string)) catch (out += "|RESID_conversionHandle=UNREADABLE")
    try
    (
        local postObjects = objects.count; local postSelection = selection.count
        local postDirty = getSaveRequired(); local postLayers = LayerManager.count
        out += "|POST_objects=" + (postObjects as string) + "|POST_selection=" + (postSelection as string) + "|POST_dirty=" + (postDirty as string) + "|POST_layers=" + (postLayers as string)
        if admitted and (rootNode != beforeRoot or maxFilePath != "" or maxFileName != "" or units.SystemType != #millimeters or units.SystemScale != 1.0 or postDirty != beforeDirty or postLayers != beforeLayers) do
        (
            out += "|POST_ENV_CHANGED=true"
            if cleanupOK do result = "INCOMPLETE_ENVIRONMENT_CHANGED"
        )
    ) catch (cleanupOK = false; result = "INCOMPLETE_POSTSTATE"; out += "|POST=THROW:" + ((getCurrentException()) as string))
    out += "|dataOK=" + (dataOK as string) + "|cleanupOK=" + (cleanupOK as string) + "|cleanup=" + cleanup + "|dirtyBefore=" + (beforeDirty as string) + "|outcome=" + result
    out
)
