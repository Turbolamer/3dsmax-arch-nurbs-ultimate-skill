-- PREPARED / UNEXECUTED. Main-only fileIn. ONE exact owned Box; no layer edits.
-- Full evidence goes to the explicit new file below; stdout is compact.
-- Equality within default layer does NOT prove unique layer identity.
(
    local evidencePath = "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-evidence.txt"
    local evidence = undefined
    local n = undefined
    local h = undefined
    local rows = 0
    local failed = false
    local cleanupOK = true
    fn record stream label value threw errorText =
    (
        local valueText = "<unstringifiable>"
        try (valueText = value as string) catch ()
        print (label + "|threw=" + (threw as string) + "|undef=" +
            ((value == undefined) as string) + "|type=" + ((classOf value) as string) +
            "|value=" + valueText + "|error=" + errorText) to:stream
    )
    fn detach value =
    (
        case (classOf value) of
        (
            String: #("string", copy value)
            Name: #("name", value)
            BooleanClass: #("bool", value)
            Integer: #("int", value)
            Float: #("float", value)
            Double: #("double", value)
            Color: #("color", value.r, value.g, value.b, value.a)
            Point3: #("point3", value.x, value.y, value.z)
            UndefinedClass: #("undefined")
            default: #("UNSUPPORTED_NOT_BASELINE", (classOf value) as string)
        )
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
    try
    (
        if objects.count != 0 or selection.count != 0 do throw "refuse: nonempty scene"
        if maxFilePath != "" or maxFileName != "" do throw "refuse: named scene"
        if doesFileExist evidencePath do throw "refuse: evidence file already exists"
        evidence = createFile evidencePath
        if evidence == undefined do throw "evidence file unavailable"
        print "PREPARED_CANDIDATE_PROBE; default-layer equality only; no layer mutation" to:evidence
        n = Box width:1.0 length:1.0 height:1.0
        h = getHandleByAnim n
        local layerA = n.layer
        local layerB = n.layer
        local layer0 = undefined
        local value = undefined
        local threw = false
        local errorText = ""
        try (layer0 = LayerManager.getLayer 0) catch (threw = true; errorText = getCurrentException())
        record evidence "LayerManager.getLayer(0)" layer0 threw errorText
        rows += 1
        for label in #("layer.self", "node.layer.repeat", "layer.vs.default", "layer.default.reverse",
            "layer.class", "default.class", "layer.getPropNames", "layer.animHandle",
            "layer.refsCount", "layer.dependents") do
        (
            value = undefined; threw = false; errorText = ""
            try
            (
                value = case label of
                (
                    "layer.self": layerA == layerA
                    "node.layer.repeat": layerA == layerB
                    "layer.vs.default": layerA == layer0
                    "layer.default.reverse": layer0 == layerA
                    "layer.class": classOf layerA
                    "default.class": classOf layer0
                    "layer.getPropNames": getPropNames layerA
                    "layer.animHandle": getHandleByAnim layerA
                    "layer.refsCount": refs.getNumRefs layerA
                    "layer.dependents": refs.dependents layerA
                )
            )
            catch (threw = true; errorText = getCurrentException())
            record evidence label value threw errorText
            rows += 1
        )
        -- Required real/bogus control plus fixed candidate layer-state fields.
        -- Missing/unknown fields are evidence, never accepted unchanged baseline.
        for p in #(#name, #P3BogusLayerPropertyXYZ, #on, #lock, #renderable, #isHidden,
            #isFrozen, #visibility, #wirecolor, #color) do
        (
            value = undefined; threw = false; errorText = ""
            local present = undefined
            local presenceThrew = false
            try (present = isProperty layerA p) catch (presenceThrew = true; errorText = getCurrentException())
            record evidence ("isProperty." + (p as string)) present presenceThrew errorText
            rows += 1
            errorText = ""
            try (value = getProperty layerA p) catch (threw = true; errorText = getCurrentException())
            record evidence ("getProperty." + (p as string)) value threw errorText
            rows += 1
            if not threw do
            (
                local detached = detach value
                local again = undefined
                local readThrew = false
                local readError = ""
                try (again = detach (getProperty layerA p)) catch (readThrew = true; readError = getCurrentException())
                record evidence ("detached." + (p as string)) detached false "scalar-copy construction; no layer edit"
                record evidence ("repeatDetached." + (p as string)) again readThrew readError
                rows += 2
                if not readThrew do
                (
                    record evidence ("typedDetachedEqual." + (p as string)) (same detached again) false "not a uniqueness or edit-detection proof"
                    rows += 1
                )
            )
        )
    )
    catch
    (
        failed = true
        if evidence != undefined do print ("OUTER_THROW|" + (getCurrentException())) to:evidence
    )
    try
    (
        if n != undefined and isValidNode n do
        (
            if h == undefined or (getHandleByAnim n) != h do throw "exact cleanup handle mismatch"
            delete n
        )
    )
    catch
    (
        cleanupOK = false
        if evidence != undefined do print ("CLEANUP_INCOMPLETE|" + (getCurrentException())) to:evidence
    )
    if evidence != undefined do
    (
        print ("END|objects=" + (objects.count as string) + "|cleanupOK=" +
            (cleanupOK as string) + "|dirty=" + ((getSaveRequired()) as string)) to:evidence
        close evidence
    )
    print ("P3_LAYER_PROBE|failed=" + (failed as string) + "|cleanup=" + (cleanupOK as string) +
        "|objects=" + (objects.count as string) + "|rows=" + (rows as string) +
        "|evidence=Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-evidence.txt")
)
