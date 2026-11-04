-- PREPARED / UNEXECUTED. Main-only short read-only control; creates/changes nothing.
-- It requires two already-existing layers; an ordinary one-layer scene refuses.
(
    local out = "P3_LAYER_TWO_EXISTING"
    local before = undefined
    try
    (
        before = getSaveRequired()
        local count = LayerManager.count
        if count < 2 or count > 64 do throw "requires 2..64 existing layers"
        local a = LayerManager.getLayer 0
        local b = LayerManager.getLayer 1
        local again = LayerManager.getLayer 0
        if a == undefined or b == undefined or again == undefined do throw "layer read returned undefined"
        local ar = a.layerAsRefTarg
        local br = b.layerAsRefTarg
        local rr = again.layerAsRefTarg
        if ar == undefined or br == undefined or rr == undefined do throw "backing reference unavailable"
        local ah = getHandleByAnim ar
        local bh = getHandleByAnim br
        if ah == undefined or bh == undefined do throw "handle unavailable"
        local positive = (ar == rr and rr == ar and (getAnimByHandle ah) == ar)
        local negative = (ar != br and br != ar and ah != bh and (getAnimByHandle bh) == br)
        out += "|alias=" + (positive as string) + "|distinct=" + (negative as string)
        out += "|ifaceAlias=" + ((a == again) as string) + "|ifaceDistinct=" + ((a != b and b != a) as string)
        out += "|handles=" + (ah as string) + "," + (bh as string)
        out += "|objects=" + (objects.count as string) + "|selection=" + (selection.count as string)
    )
    catch (out += "|THREW=" + (getCurrentException() as string))
    try (out += "|dirtyBefore=" + (before as string) + "|dirtyAfter=" + ((getSaveRequired()) as string))
    catch (out += "|DIRTY_UNREADABLE")
    out
)
