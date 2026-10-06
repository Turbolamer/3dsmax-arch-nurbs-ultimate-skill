/*  ============================================================================
    snippets/chaos_scatter.ms
    Chaos Scatter wiring library for 3ds Max 2026 + cl0nazepamm/3dsmax-mcp

    CONTRACT (references/14-chaos-scatter.md section 7)
    ----------------------------------------------------
    * This file is a LIBRARY. It creates NOTHING at file scope: no bare
      ChaosScatter(), no bare Box(), no delete. Every mutation lives inside a
      named function body. fileIn-safe from an emitted .ms.
    * Every property write is guarded: `isProperty` first, then try/catch, so an
      unbindable property in a future build is REPORTED in the returned array
      rather than aborting the whole call. A partially applied scatter is a
      finding, not a success.
    * `distributionDesityPattern` is the REAL property name -- the typo is in
      Max, not in this file. The spec file assembly.json uses the corrected
      spelling `distribution_density_pattern`; the builder emits the typo.
    * `seed` is clamped to 1 .. 31337 and is NEVER generated at run time.
      `seedFromName` derives one from a string so a hand-wired scatter is still
      reproducible.
    * `rebuild` is the re-apply-after-rebuild path: clear() then apply() from the
      same config.

    WHY YOU ARE LOADING THIS FILE
    ----------------------------
    The scatter is a DECLARATION. assembly.json.scatter[] carries one row (the
    schema key is `scatter`, singular); place_components.py emits no ChaosScatter
    node at all -- assembly.ms contains zero occurrences of ChaosScatter, scatter
    or SCT_001 [measured 2026-10-06]. S5 builds the model, stops, and hands it
    over. YOU, the user, apply the scatter from this snippet, by hand, afterwards.
    Applying it ADDS NODES -- one ChaosScatter node plus its instances -- so
    report the delivered count (254) and the count after separately.
    See agents/max-orchestrator.md section 5 for the hand-off and
    agents/max-assembly.md section 6.6 for the schema.

    OPTIONAL MANUAL VERIFICATION (not a pipeline stage)
    ----------------------------------------------------
    The QA stage that used to own a determinism protocol -- P8 / S7 -- was
    CANCELLED by user decision on 2026-10-05. Nothing in the pipeline calls
    saveConfiguration, loadConfiguration or getInstanceCount. The
    determinismRoundTrip function below survives only as something YOU may run
    by hand, if you want to confirm the scatter you just applied is
    reproducible: saveConfiguration -> clear -> rebuild -> loadConfiguration ->
    compare getInstanceCount(). See 14-chaos-scatter.md section 5.1. It is a
    convenience for a human, and it gates nothing.

    HAZARD, MEASURED (do not re-run this ladder -- it cost a reboot)
    ---------------------------------------------------------------
    5 and 10 modifiers on one node are clean. 20 PERMANENTLY FROZE Max main
    thread: 3dsmax-mcp_execute_maxscript timed out, 3dsmax-mcp_get_scene_snapshot
    timed out, 3dsmax-mcp_get_bridge_status aborted, Max had to be killed and the
    machine rebooted.
    Binding rule: <= 5 modifiers per 3dsmax-mcp_execute_maxscript call; > 10 on a single
    node is forbidden without asking the user first; past 10, cut in separate
    passes. A timeout is the ONLY symptom -- never call it "the bridge is down"
    without a cheap 3dsmax-mcp_get_bridge_status first.

    LOADING
    -------
        fileIn @"<abs path>/snippets/chaos_scatter.ms"
    Idempotent by construction. If your session reports a duplicate struct
    definition on a second fileIn, run
        undefined MCPChaosScatter; undefined MCPChaosScatterLib;
    once and fileIn again.

    USAGE
    -----
        local cfg = MCPChaosScatter.config(seed:1234, instanceLimit:2000,
                                           densityPattern:0.6,
                                           collisionAvoid:true,
                                           rotationFrom:0.0, rotationTo:360.0)
        MCPChaosScatter.create "SCT_001"
        local r = MCPChaosScatter.apply (getNodeByName "SCT_001") cfg \
                      targetNodes:#("EL_019") modelNames:#("EL_004")
        MCPChaosScatter.census (getNodeByName "SCT_001")
        MCPChaosScatter.rebuild (getNodeByName "SCT_001") cfg \
                      targetNodes:#("EL_019") modelNames:#("EL_004")
        MCPChaosScatter.dispose (getNodeByName "SCT_001")

    RETURN SHAPES
    -------------
        apply     -> #(name, targetsBound, modelsBound, applied, skipped, inst)
        census    -> #(name, instances, models, modelOrderOK)
        rebuild   -> #(cleared, <apply result>)
        save      -> true / false
        restore   -> true / false
        snapshot  -> #(name, instances, path, saved)
        config    -> an MCPChaosScatterCfg instance
        seedFromName -> integer 1 .. 31337

    ABSENT TOOLS -- never call (14-chaos-scatter.md section 4)
    ---------------------------------------------------------
    3dsmax-mcp_scatter_forest_pack, all 14 3dsmax-mcp_tyflow_* tools and
    3dsmax-mcp_get_railclone_style_graph do
    not exist in this installation. Nothing here emulates them.
    ============================================================================ */

global MCPChaosScatter


/*  ---------------------------------------------------------------------------
    CONFIG CARRIER
    A plain struct so every field is named. assembly.json.scatter[] -> one of
    these. Fields are NOT a copy of the ChaosScatter surface: names here are
    the spec-side names, and apply() does the mapping.
    --------------------------------------------------------------------------- */
struct MCPChaosScatterCfg
(
    fn targetNames = #(),        -- massing element node names
    fn modelNames = #(),         -- component or massing element node names
    fn frequencies = #(),         -- one per model; length must match modelNames
    fn seed = 1,                 -- integer 1 .. 31337
    fn instanceCountLimit = 1000,
    fn densityPattern = 1.0,     -- -> distributionDesityPattern
    fn limitCoordSpace = 0,      -- -> distributionLimitCoordSpace (enum UNVERIFIED)
    fn scaleFrom = 1.0,          -- unitless ratio, may be a scalar or a point3
    fn scaleTo = 1.0,
    fn scaleUniform = true,
    fn rotationFrom = 0.0,       -- degrees, scalar or point3
    fn rotationTo = 0.0,
    fn translationFrom = 0.0,    -- cm, scalar or point3
    fn translationTo = 0.0,
    fn collisionAvoid = true,
    fn collisionStrictness = 1.0,
    fn collisionAvoidancePriority = 1,
    fn edgeTrimmingEnabled = false,
    fn surfaceSlopeLimitEnabled = false,
    fn surfaceRandomUseDensity = false
)


/*  ---------------------------------------------------------------------------
    LIBRARY
    --------------------------------------------------------------------------- */
struct MCPChaosScatterLib
(
    fn seedMin = 1,
    fn seedMax = 31337,

    /* ---- small helpers ---------------------------------------------------- */

    -- scalar -> point3, or pass a point3 through. undefined kills the write.
    fn vec3 v =
    (
        if v == undefined then undefined
        else if classOf v == Point3 then v
        else if (classOf v == Float) or (classOf v == Integer) then [v, v, v]
        else undefined
    ),

    -- deterministic clamp. NEVER a random number.
    fn clampSeed v =
    (
        local s = 0
        if classOf v == Integer then s = v
        else if classOf v == Float then s = (v as integer)
        if s < this.seedMin do s = this.seedMin
        if s > this.seedMax do s = this.seedMax
        s
    ),

    -- a reproducible seed from a name, so a hand-wired scatter is still
    -- deterministic. Arithmetic is kept under 2^31 on purpose: MAXScript
    -- Integer is signed 32-bit and `s * 33` at 6 digits would overflow.
    fn seedFromName nm =
    (
        local t = nm as string
        local s = 5381
        local i = 1
        while i <= t.count do
        (
            s = ((s % 100000) * 33 + (getChar t i)) % 100000
            i = i + 1
        )
        this.clampSeed (s % (this.seedMax - this.seedMin + 1) + this.seedMin)
    ),

    -- the explicit-local delete form. The context-dependent one-liner
    -- `if getNodeByName nm != undefined do delete nm` throws when absent.
    fn resolveNode nm =
    (
        local nd = undefined
        if nm != undefined do try ( nd = getNodeByName nm ) catch ( nd = undefined )
        nd
    ),

    fn resolveNodes nameList =
    (
        local out = #()
        if nameList != undefined do
        (
            for nm in nameList do
            (
                local nd = this.resolveNode nm
                if nd != undefined do append out nd
            )
        )
        out
    ),

    -- guarded property write. true only if the property exists AND was set.
    -- uses `try ( ) catch ( )` on purpose: `try { } catch { }` is a parse error.
    fn setProp obj propName value =
    (
        local p = propName as name
        local present = false
        local ok = false
        try ( present = isProperty obj p ) catch ( present = false )
        if present do
        (
            try ( setProperty obj p value; ok = true ) catch ( ok = false )
        )
        ok
    ),

    -- the only verified read-back path onto a Chaos Scatter object.
    fn interface sc =
    (
        local ifc = undefined
        if sc != undefined do
        (
            local p = "FpInterface" as name
            local present = false
            try ( present = isProperty sc p ) catch ( present = false )
            if present do try ( ifc = getProperty sc p ) catch ( ifc = undefined )
        )
        ifc
    ),

    -- force a re-evaluation rather than assuming the viewport did it.
    fn refresh ifc =
    (
        local did = false
        if ifc != undefined do try ( ifc.update(); did = true ) catch ( did = false )
        did
    ),

    fn instanceCount ifc =
    (
        local n = undefined
        if ifc != undefined do try ( n = ifc.getInstanceCount() ) catch ( n = undefined )
        n
    ),

    fn modelCount ifc =
    (
        local n = undefined
        if ifc != undefined do try ( n = ifc.getModelCount() ) catch ( n = undefined )
        n
    ),

    -- getModelNode(i) must be modelNodes[i] for every i, in order.
    fn modelOrderOK sc ifc =
    (
        local ok = false
        local cnt = this.modelCount ifc
        local bound = #()
        if (ifc != undefined) and (cnt != undefined) and (cnt > 0) do
        (
            local p = "modelNodes" as name
            local present = false
            try ( present = isProperty sc p ) catch ( present = false )
            if present do try ( bound = getProperty sc p ) catch ( bound = #() )
            if bound.count == cnt do
            (
                ok = true
                local i = 1
                while i <= cnt do
                (
                    local a = undefined
                    local b = undefined
                    try ( a = ifc.getModelNode i ) catch ( a = undefined )
                    try ( b = bound[i] ) catch ( b = undefined )
                    local same = false
                    if (a != undefined) and (b != undefined) do same = ((a as string) == (b as string))
                    if not same do ok = false
                    i = i + 1
                )
            )
        )
        ok
    ),

    /* ---- construction ------------------------------------------------------ */

    -- the ONLY ChaosScatter() call in this file, and it is inside a function.
    fn create nodeName =
    (
        if nodeName == undefined do throw "MCPChaosScatter.create: nodeName is required"
        local prev = this.resolveNode nodeName
        if prev != undefined do delete prev
        local sc = ChaosScatter()
        sc.name = nodeName
        sc
    ),

    -- deletes the scatter node by name, and says whether it went. Models and
    -- targets are NOT touched: they belong to other stages.
    fn dispose sc =
    (
        local nm = undefined
        if sc != undefined do try ( nm = sc.name ) catch ( nm = undefined )
        if nm == undefined then false
        else
        (
            local nd = getNodeByName nm
            if nd != undefined do delete nd
            ((getNodeByName nm) == undefined)
        )
    ),

    /* ---- configuration ----------------------------------------------------- */

    fn config seed:1 instanceLimit:1000 densityPattern:1.0 collisionAvoid:true \
                 targetNames:#() modelNames:#() frequencies:#() \
                 rotationFrom:0.0 rotationTo:0.0 scaleFrom:1.0 scaleTo:1.0 \
                 translationFrom:0.0 translationTo:0.0 scaleUniform:true \
                 limitCoordSpace:0 collisionStrictness:1.0 \
                 collisionAvoidancePriority:1 edgeTrimmingEnabled:false \
                 surfaceSlopeLimitEnabled:false surfaceRandomUseDensity:false =
    (
        local c = MCPChaosScatterCfg()
        c.targetNames = targetNames
        c.modelNames = modelNames
        c.frequencies = frequencies
        c.seed = this.clampSeed seed
        c.instanceCountLimit = instanceLimit
        c.densityPattern = densityPattern
        c.limitCoordSpace = limitCoordSpace
        c.scaleFrom = scaleFrom
        c.scaleTo = scaleTo
        c.scaleUniform = scaleUniform
        c.rotationFrom = rotationFrom
        c.rotationTo = rotationTo
        c.translationFrom = translationFrom
        c.translationTo = translationTo
        c.collisionAvoid = collisionAvoid
        c.collisionStrictness = collisionStrictness
        c.collisionAvoidancePriority = collisionAvoidancePriority
        c.edgeTrimmingEnabled = edgeTrimmingEnabled
        c.surfaceSlopeLimitEnabled = surfaceSlopeLimitEnabled
        c.surfaceRandomUseDensity = surfaceRandomUseDensity
        c
    ),

    -- adopt a whole assembly.json.scatter[] row verbatim, so the spec is the
    -- only place a seed or a density is written. Returns the cfg, or throws
    -- naming the row id.
    fn configFromScatterRow row =
    (
        if row == undefined do throw "MCPChaosScatter.configFromScatterRow: row is undefined"
        local rid = "?"
        local ok = true
        try ( rid = row.id ) catch ()
        local c = MCPChaosScatterCfg()

        try ( c.targetNames = for x in row.targetRefs collect x ) catch ( ok = false )
        if row.modelNames == undefined do try ( c.modelNames = for x in row.modelRefs collect x ) catch ( ok = false )
        try ( c.frequencies = row.frequencies as array ) catch ( c.frequencies = #() )
        try ( c.seed = this.clampSeed row.seed ) catch ( ok = false )
        try ( c.instanceCountLimit = row.instanceCountLimit ) catch ( ok = false )
        try ( c.densityPattern = row.distribution_density_pattern ) catch ( ok = false )
        try ( c.scaleFrom = row.scale_from ) catch ( ok = false )
        try ( c.scaleTo = row.scale_to ) catch ( ok = false )
        try ( c.rotationFrom = row.rotation_from_deg ) catch ( ok = false )
        try ( c.rotationTo = row.rotation_to_deg ) catch ( ok = false )
        if row.collision_avoid != undefined do
        (
            if classOf row.collision_avoid != Boolean then ok = false
            else c.collisionAvoid = row.collision_avoid
        )
        -- layer is DATA ONLY and is deliberately NOT read here. Layer cannot be
        -- assigned from this bridge through any of nine ruled-out routes.
        if not ok do throw ("MCPChaosScatter.configFromScatterRow: row " + rid + \
                            " is missing or mistyping a required assembly.json key")
        c
    ),

    /* ---- apply ------------------------------------------------------------- */

    -- The apply-and-re-apply workhorse. Idempotent: every value is written on
    -- every call, so calling it twice is identical to calling it once.
    fn apply sc cfg targetNodes:undefined modelNames:undefined =
    (
        if sc == undefined do throw "MCPChaosScatter.apply: scatter node is undefined"
        if cfg == undefined do throw ("MCPChaosScatter.apply: config is undefined for " + \
                                      (sc.name as string) + " -- build one with config()")

        local tgtNames = if targetNodes == undefined then cfg.targetNames else targetNodes
        local mdlNames = if modelNames == undefined then cfg.modelNames else modelNames

        local tgt = this.resolveNodes tgtNames
        local mdl = this.resolveNodes mdlNames

        if tgt.count == 0 do throw ("MCPChaosScatter.apply: no target resolved from " + (tgtNames as string))
        if mdl.count == 0 do throw ("MCPChaosScatter.apply: no model resolved from " + (mdlNames as string))

        -- one frequency per model; the spec's list wins when the lengths agree
        local frq = #()
        try ( frq = cfg.frequencies as array ) catch ( frq = #() )
        if frq.count != mdl.count do
        (
            frq = #()
            if mdl.count > 0 do
            (
                local i = 1
                while i <= mdl.count do
                (
                    append frq 1.0
                    i = i + 1
                )
            )
        )

        local applied = #()
        local skipped = #()

        if this.setProp sc "targetNodes" tgt do append applied "targetNodes"
        else append skipped "targetNodes=<not settable>"
        if this.setProp sc "modelNodes" mdl do append applied "modelNodes"
        else append skipped "modelNodes=<not settable>"
        if this.setProp sc "modelFrequencies" (frq as float array) do append applied "modelFrequencies"
        else append skipped "modelFrequencies=<not settable>"

        -- NOTE: distributionDesityPattern. The typo is the REAL name.
        local pairs = #(
            #("seed", this.clampSeed cfg.seed),
            #("instanceCountLimit", cfg.instanceCountLimit),
            #("distributionDesityPattern", cfg.densityPattern),
            #("distributionLimitCoordSpace", cfg.limitCoordSpace),
            #("scaleFrom", this.vec3 cfg.scaleFrom),
            #("scaleTo", this.vec3 cfg.scaleTo),
            #("scaleUniform", cfg.scaleUniform),
            #("rotationFrom", this.vec3 cfg.rotationFrom),
            #("rotationTo", this.vec3 cfg.rotationTo),
            #("translationFrom", this.vec3 cfg.translationFrom),
            #("translationTo", this.vec3 cfg.translationTo),
            #("collisionAvoid", cfg.collisionAvoid),
            #("collisionStrictness", cfg.collisionStrictness),
            #("collisionAvoidancePriority", cfg.collisionAvoidancePriority),
            #("edgeTrimmingEnabled", cfg.edgeTrimmingEnabled),
            #("surfaceSlopeLimitEnabled", cfg.surfaceSlopeLimitEnabled),
            #("surfaceRandomUseDensity", cfg.surfaceRandomUseDensity)
        )

        for pr in pairs do
        (
            local nm = pr[1]
            local val = pr[2]
            if val == undefined do append skipped (nm + "=<undefined>")
            else if this.setProp sc nm val do append applied nm
            else append skipped (nm + "=<not settable>")
        )

        local ifc = this.interface sc
        this.refresh ifc
        local nInst = this.instanceCount ifc

        #(sc.name, tgt.count, mdl.count, applied, skipped, nInst)
    ),

    -- re-apply-after-rebuild: clear the instance set, then apply from the same
    -- config. This is the path the optional manual verification in
    -- determinismRoundTrip drives. Nothing in the pipeline calls it.
    fn rebuild sc cfg targetNodes:undefined modelNames:undefined =
    (
        local ifc = this.interface sc
        local cleared = false
        if ifc != undefined do
        (
            try ( ifc.clear(); cleared = true ) catch ( cleared = false )
        )
        local res = undefined
        try ( res = this.apply sc cfg targetNodes:targetNodes modelNames:modelNames ) \
            catch ( res = #(if (sc == undefined) then "?" else sc.name, 0, 0, #(), #("apply threw"), undefined) )
        #(cleared, res)
    ),

    /* ---- census ------------------------------------------------------------ */

    -- #(name, instances, models, modelOrderOK). A SKIP-shaped result reports
    -- undefined for what it could not read; it never reports a guess.
    fn census sc =
    (
        if sc == undefined do throw "MCPChaosScatter.census: scatter node is undefined"
        local ifc = this.interface sc
        local nInst = this.instanceCount ifc
        local nMdl = this.modelCount ifc
        local ok = false
        if (nMdl != undefined) and (nMdl > 0) do ok = this.modelOrderOK sc ifc
        #(sc.name, nInst, nMdl, ok)
    ),

    /* ---- OPTIONAL MANUAL VERIFICATION (the former P8 determinism hook) -------
       P8 / S7 was CANCELLED by user decision on 2026-10-05. No stage runs any
       of this; it is here for the user, after applying the scatter by hand.
       See the file header and 14-chaos-scatter.md section 5.1. */

    -- saveConfiguration(f): snapshot the whole scatter configuration to disk.
    fn save sc filePath =
    (
        if sc == undefined do throw "MCPChaosScatter.save: scatter node is undefined"
        if filePath == undefined do throw "MCPChaosScatter.save: filePath is required"
        local ifc = this.interface sc
        if ifc == undefined do throw ("MCPChaosScatter.save: FpInterface unavailable on " + (sc.name as string))
        local ok = false
        try ( ifc.saveConfiguration filePath; ok = true ) catch ( ok = false )
        ok
    ),

    -- loadConfiguration(f): restore it. Returns the post-load instance count.
    fn restore sc filePath =
    (
        if sc == undefined do throw "MCPChaosScatter.restore: scatter node is undefined"
        if filePath == undefined do throw "MCPChaosScatter.restore: filePath is required"
        local ifc = this.interface sc
        if ifc == undefined do throw ("MCPChaosScatter.restore: FpInterface unavailable on " + (sc.name as string))
        local ok = false
        try ( ifc.loadConfiguration filePath; ok = true ) catch ( ok = false )
        this.refresh ifc
        #(ok, this.instanceCount ifc)
    ),

    -- snapshot = save + census in one call, because the optional manual
    -- verification below needs BOTH the file and the count from the same moment.
    fn snapshot sc filePath =
    (
        local c = this.census sc
        local saved = this.save sc filePath
        #(c[1], c[2], filePath, saved)
    ),

    -- ONE call that does the whole optional manual check: save, clear, re-apply,
    -- load, and report the three counts. #3 is the whole point of the function.
    -- OPTIONAL, and never automatic -- the QA stage that used to require this was
    -- cancelled on 2026-10-05. Run it by hand if you want to know whether the
    -- scatter you applied is reproducible.
    --   #(name, nBefore, nAfterClearRebuild, nAfterLoad, stable)
    -- If nBefore differs from nAfterLoad the scene is NOT reproducible, and the
    -- seed is not the reason. Check 3dsmax-mcp_get_bridge_status before it.
    fn determinismRoundTrip sc cfg filePath targetNodes:undefined modelNames:undefined =
    (
        local n1 = this.instanceCount (this.interface sc)
        local saved = this.save sc filePath
        this.rebuild sc cfg targetNodes:targetNodes modelNames:modelNames
        local n2 = this.instanceCount (this.interface sc)
        this.restore sc filePath
        local n3 = this.instanceCount (this.interface sc)
        local stable = false
        if (n1 != undefined) and (n2 != undefined) and (n3 != undefined) do
            stable = ((n1 == n2) and (n2 == n3))
        #(sc.name, n1, n2, n3, stable, saved)
    )
)


/*  ---------------------------------------------------------------------------
    FILE SCOPE -- INSTANTIATION ONLY
    No scene mutation above this line other than defining structs. There is no
    bare ChaosScatter(), no bare Box() and no delete at file scope, so a
    fileIn of this file cannot change a scene even if the rest of an emitted
    build fails.
    --------------------------------------------------------------------------- */

MCPChaosScatter = MCPChaosScatterLib()