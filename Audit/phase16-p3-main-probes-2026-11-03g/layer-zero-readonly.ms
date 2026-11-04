-- Main-only read-only calibration of the empty existing default layer.
-- Does not construct, rename, modify, delete, reset or save anything.
-- A local partial read is never a complete layer baseline or replay gate.
(
    local result = "P3G_LAYER_ZERO_READONLY"
    local beforeRoot = rootNode
    local beforePath = copy maxFilePath
    local beforeName = copy maxFileName
    local beforeDirty = getSaveRequired()
    local beforeTime = currentTime as integer
    local beforeSub = subObjectLevel
    local original = undefined
    local handle = undefined
    try
    (
        if objects.count != 0 or selection.count != 0 or beforePath != "" or beforeName != "" do throw "scene admission changed"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 or beforeDirty != true do throw "unit/dirty admission changed"
        if LayerManager.count != 1 or (globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7) do throw "layer or historical key admission changed"
        local layer = LayerManager.getLayer 0
        local members = #()
        if layer.name != "0" or not layer.current or not (layer.nodes &members) or members.count != 0 or layer.getNumNodes() != 0 do throw "default layer admission changed"
        original = layer.layerAsRefTarg
        if original == undefined do throw "missing default backing reference"
        handle = getHandleByAnim original
        if handle == undefined or (getAnimByHandle handle) != original do throw "default backing handle mismatch"
        local names = getPropNames layer
        local backingNames = getPropNames original
        local giNames = getPropNames layer.INodeGIProperties
        if names == undefined or backingNames == undefined or giNames == undefined do throw "property list unavailable"
        if names.count != 33 or backingNames.count != 34 or giNames.count != 18 do throw "observed property profile counts changed"
        if (findItem backingNames #degrade) == 0 or (findItem names #degrade) != 0 do throw "backing-only degrade distinction not found"
        local target = layer.layerAsRefTarg
        local defaultAlias = LayerManager.getLayer 0
        if target != original or defaultAlias.layerAsRefTarg != original do throw "default identity changed during read"
        local deps = refs.dependents original
        local outCount = refs.getNumRefs original
        if (classOf deps) != Array or deps.count > 8 or outCount < 0 or outCount > 8 do throw "unbounded or unavailable dependency enumeration"
        result += "|backingClass=" + ((classOf original) as string) + "|backingHandle=" + (handle as string)
        result += "|sameBacking=true|interfaceCount=" + (names.count as string) + "|backingCount=" + (backingNames.count as string) + "|giCount=" + (giNames.count as string) + "|degradeBackingOnly=true"
        result += "|backingOutgoingCount=" + (outCount as string) + "|dependentCount=" + (deps.count as string)
        for i = 1 to deps.count do
        (
            local dep = deps[i]
            local depClass = classOf dep
            local depHandle = undefined
            local roundtrip = false
            local err = ""
            try (depHandle = getHandleByAnim dep; roundtrip = depHandle != undefined and (getAnimByHandle depHandle) == dep) catch (err = getCurrentException() as string)
            result += "|dep" + (i as string) + "=" + (depClass as string) + ";isRoot=" + ((dep == beforeRoot) as string) + ";handle=" + (depHandle as string) + ";roundtrip=" + (roundtrip as string) + ";error=" + err
        )
        result += "|outcome=PARTIAL_OBSERVATION_INCOMPLETE"
    )
    catch (result += "|ERROR=" + ((getCurrentException()) as string) + "|outcome=INCOMPLETE")
    try
    (
        local layer = LayerManager.getLayer 0
        local members = #()
        local afterBacking = layer.layerAsRefTarg
        local layerOK = (layer.nodes &members) and members.count == 0 and layer.getNumNodes() == 0
        local unchanged = rootNode == beforeRoot and maxFilePath == beforePath and maxFileName == beforeName and getSaveRequired() == beforeDirty and (currentTime as integer) == beforeTime and subObjectLevel == beforeSub and units.SystemType == #millimeters and units.SystemScale == 1.0 and objects.count == 0 and selection.count == 0 and LayerManager.count == 1 and layerOK and original != undefined and afterBacking == original and (getHandleByAnim original) == handle and (getAnimByHandle handle) == original
        result += "|postContextAndExactBackingUnchanged=" + (unchanged as string) + "|objectsAfter=" + (objects.count as string) + "|selectionAfter=" + (selection.count as string) + "|dirtyAfter=" + ((getSaveRequired()) as string)
    )
    catch (result += "|POSTCHECK_ERROR=" + ((getCurrentException()) as string))
    result
)
