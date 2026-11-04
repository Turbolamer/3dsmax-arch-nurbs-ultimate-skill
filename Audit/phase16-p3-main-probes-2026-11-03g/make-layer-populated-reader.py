"""Emit a fresh, hash-bound populated-layer reader calibration wrapper.

The wrapper embeds the exact offline candidate bytes, creates one Box and one
temporary layer, retains exact returned references/handles immediately, runs the
candidate against that owned populated layer, then performs guarded exact cleanup
in the same invocation. It is an evidence probe, not production integration.
"""

from hashlib import sha256
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent / "phase16-p3-layer-reader-2026-11-03f" / "layer_reader_p31_offline.ms"
EXPECTED = "5b16d1d648a2cdefd9b98440ad4fb4ae1ca1a1c3dde0ecf47990dfe44a8ad4f2"
OUTPUT = HERE / "layer-populated-reader.ms"

PREFIX = """-- Main-only owned populated-layer reader calibration.
-- Candidate remains offline-only and this probe is not production integration.
-- Exact refs/handles are retained immediately after each constructor return.
(
"""

SUFFIX = r'''
    local out = "P31_POPULATED_READER"
    local label = "P3G_LayerReader_47B2C1"
    local rootWitness = undefined
    local defaultLayer = undefined
    local defaultBacking = undefined
    local defaultHandle = undefined
    local layer = undefined
    local layerBacking = undefined
    local layerHandle = undefined
    local node = undefined
    local nodeWitness = undefined
    local memberWitnesses = #()
    local managerWitness = undefined
    local managerHandle = undefined
    local nodeAttempt = false
    local layerAttempt = false
    local nodeRemoved = false
    local layerRemoved = false
    local readerError = ""
    local cleanupError = ""
    local dirtyBefore = undefined
    local defaultDeps = undefined
    local managerCount = 0
    local stage = "entry"

    fn p31SafeString value = (try ((value as string)) catch ("<STRING_ERROR>"))
    fn p31DescribeRefs deps =
    (
        local text = ""
        if deps == undefined then return "<UNDEFINED_DEPS>"
        for i = 1 to deps.count do
        (
            local dep = deps[i]
            local h = undefined
            local rt = false
            local e = ""
            try (h = getHandleByAnim dep; rt = h != undefined and (getAnimByHandle h) == dep) catch (e = getCurrentException() as string)
            text += "|dep" + (i as string) + "=" + ((classOf dep) as string) + ";h=" + (p31SafeString h) + ";rt=" + (rt as string) + ";err=" + e
        )
        text
    )

    try
    (
        stage = "admission"
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "P31_REFUSE|scene not empty unnamed unselected"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "P31_REFUSE|native units mismatch"
        if LayerManager.count != 1 or (LayerManager.getLayerFromName label) != undefined do throw "P31_REFUSE|layer admission mismatch"
        if globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7 do throw "P31_REFUSE|historical key present"
        dirtyBefore = getSaveRequired()
        rootWitness = #(rootScene, getHandleByAnim rootScene)
        if rootWitness[2] == undefined or (getAnimByHandle rootWitness[2]) != rootScene do throw "P31_REFUSE|rootScene witness unavailable"
        defaultLayer = LayerManager.getLayer 0
        defaultBacking = defaultLayer.layerAsRefTarg
        defaultHandle = getHandleByAnim defaultBacking
        if defaultHandle == undefined or (getAnimByHandle defaultHandle) != defaultBacking do throw "P31_REFUSE|default layer witness unavailable"
        defaultDeps = refs.dependents defaultBacking
        stage = "layer-constructor"
        layerAttempt = true
        layer = LayerManager.newLayerFromName label
        if layer == undefined do throw "P31_INCOMPLETE|layer constructor returned undefined"
        layerBacking = layer.layerAsRefTarg
        layerHandle = getHandleByAnim layerBacking
        if layerBacking == undefined or layerHandle == undefined or (getAnimByHandle layerHandle) != layerBacking do throw "P31_INCOMPLETE|layer backing witness unavailable"
        if layerBacking == defaultBacking do throw "P31_INCOMPLETE|layer backing not distinct"
        out += "|stage=layer-bound|layerHandle=" + (layerHandle as string) + "|defaultHandle=" + (defaultHandle as string)
        stage = "node-constructor"
        nodeAttempt = true
        node = Box width:1.0 length:1.0 height:1.0
        if node == undefined do throw "P31_INCOMPLETE|Box constructor returned undefined"
        local nodeHandle = getHandleByAnim node
        nodeWitness = #(node, nodeHandle)
        if nodeHandle == undefined or (getAnimByHandle nodeHandle) != node do throw "P31_INCOMPLETE|node witness unavailable"
        append memberWitnesses nodeWitness
        out += "|stage=node-bound|nodeHandle=" + (nodeHandle as string) + ";nodeClass=" + ((classOf node) as string) + ";baseClass=" + ((classOf node.baseObject) as string)
        stage = "membership-attach"
        layer.addNode node
        local memberCheck = #()
        if not (layer.nodes &memberCheck) or memberCheck.count != 1 or memberCheck[1] != node do throw "P31_INCOMPLETE|membership attach/readback failed"
        local beforeDeps = refs.dependents layerBacking
        out += "|stage=membership-bound|memberCount=" + (memberCheck.count as string) + "|dependentCount=" + (beforeDeps.count as string) + (p31DescribeRefs beforeDeps)
        for dep in beforeDeps do
            if ((classOf dep) as string) == "Layer_Manager" do
            (
                managerCount += 1
                if managerWitness == undefined do
                (
                    local mh = getHandleByAnim dep
                    if mh == undefined or (getAnimByHandle mh) != dep do throw "P31_INCOMPLETE|manager dependent witness unavailable"
                    managerWitness = #(dep, mh)
                    managerHandle = mh
                )
            )
        if managerCount != 1 or managerWitness == undefined do throw "P31_INCOMPLETE|expected one exact Layer_Manager dependent not found"
        out += "|stage=dependency-witnesses|managerHandle=" + (managerHandle as string) + "|managerClass=" + ((classOf managerWitness[1]) as string)
        stage = "candidate-read-once"
        local one = undefined
        try (one = p31ReadOnce nodeWitness #(layerBacking, layerHandle) rootWitness managerWitness memberWitnesses; out += "|readOnce=OK;payloadCount=" + (one.count as string)) catch (readerError = getCurrentException() as string; out += "|readOnce=ERROR;error=" + readerError)
        stage = "candidate-observe-twice"
        local twice = p31ObserveTwice nodeWitness #(layerBacking, layerHandle) rootWitness managerWitness memberWitnesses
        if (classOf twice) == Array and twice.count >= 3 then out += "|observeTwice=" + (twice[3] as string) else out += "|observeTwice=MALFORMED"
        if one != undefined then out += "|candidateStatus=INCOMPLETE_PARTIAL_ONLY" else out += "|candidateStatus=INCOMPLETE_READ_ERROR"
    )
    catch
    (
        if readerError == "" do readerError = getCurrentException() as string
        out += "|MAIN_ERROR|stage=" + stage + "|error=" + readerError
    )

    stage = "node-cleanup"
    if nodeAttempt and node != undefined do
    (
        try
        (
            if not (isValidNode node) or nodeWitness == undefined or (getHandleByAnim node) != nodeWitness[2] or (getAnimByHandle nodeWitness[2]) != node or objects.count != 1 or selection.count != 0 do throw "P31_CLEANUP_REFUSE|node identity/census"
            if node.parent != undefined or node.children.count != 0 do throw "P31_CLEANUP_REFUSE|node hierarchy"
            local users = for o in objects where o.baseObject == node.baseObject collect o
            if users.count != 1 or users[1] != node do throw "P31_CLEANUP_REFUSE|node base sharing"
            local attached = #()
            if not (layer.nodes &attached) or attached.count != 1 or attached[1] != node do throw "P31_CLEANUP_REFUSE|member identity"
            delete node
            if isValidNode node or objects.count != 0 do throw "P31_CLEANUP_REFUSE|exact node removal unverified"
            nodeRemoved = true
        )
        catch (cleanupError += ("node:" + (getCurrentException() as string) + "|"))
    )
    else if nodeAttempt do cleanupError += "node:CONSTRUCTOR_RETURN_NOT_OBSERVED|"

    stage = "layer-cleanup"
    if layerAttempt and layer != undefined do
    (
        try
        (
            if not nodeRemoved or layerBacking == undefined or layerHandle == undefined or layer.layerAsRefTarg != layerBacking or (getAnimByHandle layerHandle) != layerBacking or LayerManager.count != 2 or objects.count != 0 or selection.count != 0 do throw "P31_CLEANUP_REFUSE|layer identity/census"
            local remaining = #()
            if not (layer.nodes &remaining) or remaining.count != 0 or layer.current or layer.getParent() != undefined or layer.getNumChildren() != 0 do throw "P31_CLEANUP_REFUSE|layer not empty/noncurrent/unnested"
            local alias = LayerManager.getLayerFromName label
            if alias == undefined or alias.layerAsRefTarg != layerBacking do throw "P31_CLEANUP_REFUSE|layer alias backing mismatch"
            if not (LayerManager.deleteLayerByName label) do throw "P31_CLEANUP_REFUSE|layer delete refused"
            if LayerManager.count != 1 or (LayerManager.getLayerFromName label) != undefined or (getAnimByHandle defaultHandle) != defaultBacking or (LayerManager.getLayer 0).layerAsRefTarg != defaultBacking do throw "P31_CLEANUP_REFUSE|layer survivor/default mismatch"
            layerRemoved = true
        )
        catch (cleanupError += ("layer:" + (getCurrentException() as string) + "|"))
    )
    else if layerAttempt do cleanupError += "layer:CONSTRUCTOR_RETURN_NOT_OBSERVED|"

    try
    (
        out += "|cleanupNode=" + (nodeRemoved as string) + "|cleanupLayer=" + (layerRemoved as string) + "|cleanupError=" + cleanupError + "|objectsAfter=" + (objects.count as string) + "|selectionAfter=" + (selection.count as string) + "|layersAfter=" + (LayerManager.count as string) + "|dirtyBefore=" + (dirtyBefore as string) + "|dirtyAfter=" + ((getSaveRequired()) as string) + "|outcome=" + (if nodeRemoved and layerRemoved and cleanupError == "" then "INCOMPLETE_PARTIAL_READER_ONLY" else "INCOMPLETE_RESIDUAL_OR_IDENTITY")
    )
    catch (out += "|POSTCHECK_ERROR=" + ((getCurrentException()) as string))
    out
)
'''

raw = CANDIDATE.read_bytes()
actual = sha256(raw).hexdigest()
if actual != EXPECTED:
    raise SystemExit(f"candidate SHA-256 drift: {actual}")
text = raw.decode("utf-8", "strict")
if "\x00" in text or not text.endswith("\n"):
    raise SystemExit("candidate bytes invalid")
payload = (PREFIX + text + SUFFIX).encode("utf-8")
with OUTPUT.open("xb") as stream:
    stream.write(payload)
print("candidate_sha256=" + actual)
print("wrapper_sha256=" + sha256(payload).hexdigest())
print("wrapper_bytes=" + str(len(payload)))
