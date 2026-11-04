"""Build one exclusive offline wrapper for a partial read-only Max calibration.

The wrapper can parse and exercise pure/profile helpers on the existing empty
default layer. It deliberately does not call p31ReadOnce or p31ObserveTwice,
does not claim a member-node result, and never supplies adopted dependencies as
identity authority. Execution must be separately admitted and assessed by main.
"""

from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent / "phase16-p3-layer-reader-2026-11-03f" / "layer_reader_p31_offline.ms"
EXPECTED = "5b16d1d648a2cdefd9b98440ad4fb4ae1ca1a1c3dde0ecf47990dfe44a8ad4f2"
OUTPUT = HERE / "layer-empty-observer.ms"

prefix = r'''-- Main-only read-only partial calibration; NOT a baseline or replay authorization.
(
'''
suffix = r'''
    local out = "P31_EMPTY_LOCAL_OBSERVER"
    local root0 = rootNode
    local path0 = copy maxFilePath
    local name0 = copy maxFileName
    local dirty0 = getSaveRequired()
    local time0 = currentTime as integer
    local sub0 = subObjectLevel
    local backing0 = undefined
    local backingHandle0 = undefined
    try
    (
        if objects.count != 0 or selection.count != 0 or path0 != "" or name0 != "" do throw "admission scene mismatch"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 or dirty0 != true do throw "admission units or dirty changed"
        if LayerManager.count != 1 or (globalVars.isGlobal #__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7) do throw "admission layer/key mismatch"
        local layer = LayerManager.getLayer 0
        local members = #()
        if layer.name != "0" or not layer.current or not (layer.nodes &members) or members.count != 0 or layer.getNumNodes() != 0 do throw "admission default membership mismatch"
        backing0 = layer.layerAsRefTarg
        backingHandle0 = getHandleByAnim backing0
        if backingHandle0 == undefined or (getAnimByHandle backingHandle0) != backing0 do throw "backing identity unavailable"
        local backingWitness = #(backing0, backingHandle0)
        out += "|stage=layer-interface"
        local a = p31ReadProperties layer p31InterfaceProfile backingWitness
        local b = p31ReadProperties layer p31InterfaceProfile backingWitness
        out += "|interfaceCount=" + (a.count as string) + ";repeatEqual=" + ((p31DetachedEqual a b) as string)
        out += "|stage=backing"
        local c = p31ReadProperties backing0 p31BackingProfile backingWitness
        local d = p31ReadProperties backing0 p31BackingProfile backingWitness
        out += "|backingCount=" + (c.count as string) + ";repeatEqual=" + ((p31DetachedEqual c d) as string)
        out += "|stage=nested-gi"
        local gi = p31ReadGI layer.INodeGIProperties
        out += "|giCount=" + (gi.count as string)
        out += "|stage=detached-edits"
        local giSecond = p31ReadGI layer.INodeGIProperties
        local oldGi = giSecond[1][2][2]
        giSecond[1][2][2] = not oldGi
        out += "|detachedGIEditDetected=" + ((not (p31DetachedEqual gi giSecond)) as string)
        local copied = p31ReadProperties backing0 p31BackingProfile backingWitness
        local degradeIndex = 0
        for i = 1 to copied.count do if copied[i][1] == #degrade do degradeIndex = i
        if degradeIndex == 0 do throw "backing degrade record absent"
        copied[degradeIndex][2][2] = not copied[degradeIndex][2][2]
        out += "|detachedDegradeEditDetected=" + ((not (p31DetachedEqual c copied)) as string)
        local wrongBackingRef = false
        try (p31ReadProperties layer p31InterfaceProfile #(root0, getHandleByAnim root0)) catch (wrongBackingRef = true)
        local bogusField = false
        try (p31ReadProperties layer #(#(#P31_BOGUS_8817, #bool)) backingWitness) catch (bogusField = true)
        local missingValue = false
        try (p31Detach undefined #float) catch (missingValue = true)
        out += "|wrongBackingRefRefused=" + (wrongBackingRef as string) + "|bogusProfileRefused=" + (bogusField as string) + "|undefinedFloatRefused=" + (missingValue as string)
        out += "|status=INCOMPLETE_PARTIAL_ONLY"
    )
    catch (out += "|ERROR=" + ((getCurrentException()) as string) + "|status=INCOMPLETE")
    try
    (
        local l = LayerManager.getLayer 0
        local m = #()
        local unchanged = objects.count == 0 and selection.count == 0 and rootNode == root0 and maxFilePath == path0 and maxFileName == name0 and getSaveRequired() == dirty0 and (currentTime as integer) == time0 and subObjectLevel == sub0 and units.SystemType == #millimeters and units.SystemScale == 1.0 and LayerManager.count == 1 and (l.nodes &m) and m.count == 0 and l.getNumNodes() == 0 and backing0 != undefined and l.layerAsRefTarg == backing0 and (getHandleByAnim backing0) == backingHandle0 and (getAnimByHandle backingHandle0) == backing0
        out += "|postContextAndBackingUnchanged=" + (unchanged as string) + "|dirty=" + ((getSaveRequired()) as string)
    )
    catch (out += "|POSTCHECK_ERROR=" + ((getCurrentException()) as string))
    out
)
'''

raw = CANDIDATE.read_bytes()
if sha256(raw).hexdigest() != EXPECTED:
    raise SystemExit("candidate SHA-256 drift; refusing to generate")
text = raw.decode("utf-8", "strict")
if "\x00" in text or not text.endswith("\n"):
    raise SystemExit("invalid candidate bytes")
source = (prefix + text + suffix).encode("utf-8")
with OUTPUT.open("xb") as stream:
    stream.write(source)
print("wrapper_sha256=" + sha256(source).hexdigest())
print("candidate_sha256=" + EXPECTED)
print("bytes=" + str(len(source)))
