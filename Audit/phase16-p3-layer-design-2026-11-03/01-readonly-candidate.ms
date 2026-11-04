-- PREPARED, UNEXECUTED. Read-only; output is diagnostic, not a baseline.
-- Main only, in a freshly inspected scene. No files, globals, nodes or layers written.
(
    local out = "P3_LAYER_RO_CANDIDATE"
    local beforeDirty = undefined
    try
    (
        beforeDirty = getSaveRequired()
        out += "|objects=" + (objects.count as string) + "|selection=" + (selection.count as string)
        out += "|path=" + maxFilePath + "|file=" + maxFileName
        out += "|units=" + (units.SystemType as string) + "|scale=" + (units.SystemScale as string)
        out += "|time=" + (currentTime as string) + "|subobject=" + (subObjectLevel as string)
        out += "|dirtyBefore=" + (beforeDirty as string) + "|layerCount=" + (LayerManager.count as string)
        if LayerManager.count < 1 or LayerManager.count > 64 do throw "unsupported layer count"
        local lyr = LayerManager.getLayer 0
        if lyr == undefined do throw "layer 0 unavailable"
        local base = lyr.layerAsRefTarg
        local repeated = (LayerManager.getLayer 0).layerAsRefTarg
        local h = getHandleByAnim base
        local bogus = false
        try (getProperty lyr #P3LayerBogus_453E) catch (bogus = true)
        out += "|namePresent=" + ((isProperty lyr #name) as string)
        out += "|bogusPresent=" + ((isProperty lyr #P3LayerBogus_453E) as string)
        out += "|bogusThrew=" + (bogus as string)
        out += "|sameInterface=" + ((lyr == (LayerManager.getLayer 0)) as string)
        out += "|sameBacking=" + ((base == repeated) as string)
        out += "|handle=" + (h as string) + "|roundTrip=" + (((getAnimByHandle h) == base) as string)
        local props = getPropNames lyr
        local gi = getProperty lyr #INodeGIProperties
        local giProps = getPropNames gi
        local backProps = getPropNames base
        if props == undefined or giProps == undefined or backProps == undefined do throw "property names unavailable"
        if props.count > 64 or giProps.count > 64 or backProps.count > 64 do throw "property count ceiling"
        out += "|properties=" + (props.count as string) + "|giProperties=" + (giProps.count as string) + "|backingProperties=" + (backProps.count as string)
        for p in props where p != #layerAsRefTarg and p != #INodeGIProperties do
        (
            try (local v = getProperty lyr p; out += "|L." + (p as string) + ":" + ((classOf v) as string))
            catch (out += "|L_THROW." + (p as string) + ":" + (getCurrentException() as string))
        )
        for p in giProps do
        (
            try (local v = getProperty gi p; out += "|GI." + (p as string) + ":" + ((classOf v) as string))
            catch (out += "|GI_THROW." + (p as string) + ":" + (getCurrentException() as string))
        )
        for p in backProps where p != #layerAsRefTarg and p != #INodeGIProperties do
        (
            try (local v = getProperty base p; out += "|B." + (p as string) + ":" + ((classOf v) as string))
            catch (out += "|B_THROW." + (p as string) + ":" + (getCurrentException() as string))
        )
    )
    catch (out += "|OUTER_THROW=" + (getCurrentException() as string))
    try (out += "|dirtyAfter=" + ((getSaveRequired()) as string)) catch (out += "|DIRTY_UNREADABLE")
    out
)
