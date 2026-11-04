-- Main-only bounded calibration, not replay or wall acceptance.
-- One disposable exact node in a freshly inspected empty unnamed mm/1 scene.
-- VData11 custom support/value on that node only; no user scene edits.
(
    local n = undefined
    local orig = undefined
    local converted = undefined
    local h = undefined
    local didConstruct = false
    local cleanupOK = false
    local outcome = "INCOMPLETE"
    local report = "P3_VDATA11"
    local beforeDirty = getSaveRequired()
    local root = rootNode
    try
    (
        if objects.count != 0 or selection.count != 0 do throw "not an empty unselected scene"
        if maxFilePath != "" or maxFileName != "" do throw "named scene unsupported"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "unexpected units"
        n = Editable_Mesh()
        didConstruct = true
        orig = n
        h = getHandleByAnim n
        if not isValidNode n or h == undefined or (getAnimByHandle h) != n do throw "cannot bind created reference"
        if objects.count != 1 do throw "unexpected construction census"
        converted = convertTo n Editable_Poly
        if not isValidNode orig or not isValidNode converted do throw "uncertain conversion: leave candidates"
        if orig != converted or (getHandleByAnim converted) != h or (getAnimByHandle h) != orig do throw "conversion identity mismatch"
        n = orig
        local ids = #()
        for p in #([0,0,0], [10,0,0], [10,0,10], [0,0,10]) do
        (
            local id = polyop.createVert n p
            if classOf id != Integer or id < 1 or (findItem ids id) != 0 do throw "vertex ID incomplete"
            append ids id
        )
        local f = polyop.createPolygon n ids
        update n
        if classOf f != Integer or f < 1 or (polyop.getNumVerts n) != 4 or (polyop.getNumFaces n) != 1 do throw "quad setup incomplete"
        local base = n.baseObject
        local hit = isProperty n #name
        local miss = isProperty n #P3VDataBogusNameF9
        local missThrew = false
        try (getProperty n #P3VDataBogusNameF9) catch (missThrew = true)
        local wrongThrew = false
        try (polyop.getNumVDataChannels undefined) catch (wrongThrew = true)
        if hit != true or miss != false or not missThrew or not wrongThrew do throw "positive/miss/unknown control failed"
        local countA = polyop.getNumVDataChannels base
        local countB = polyop.getNumVDataChannels base
        if classOf countA != Integer or countA < 0 or countA > 10 or countA != countB do throw "unexpected initial channel domain"
        local v = polyop.getVert base ids[1]
        local frozen = #(v.x, v.y, v.z)
        polyop.setNumVDataChannels base 11 keep:true
        polyop.setVDataChannelSupport base 11 true
        local sel = #{}
        sel[ids[1]] = true
        polyop.setVDataValue base 11 sel 0.375
        local countC = polyop.getNumVDataChannels base
        local supported = polyop.getVDataChannelSupport base 11
        local first = polyop.getVDataValue base 11 ids[1]
        local repeatValue = polyop.getVDataValue base 11 ids[1]
        polyop.setVDataValue base 11 sel 0.625
        local second = polyop.getVDataValue base 11 ids[1]
        local after = polyop.getVert base ids[1]
        local untouched = after.x == frozen[1] and after.y == frozen[2] and after.z == frozen[3] and (polyop.getNumVerts base) == 4 and (polyop.getNumFaces base) == 1
        report += "|positive=" + (hit as string) + "|bogusAbsent=" + ((not miss) as string) + "|bogusThrows=" + (missThrew as string) + "|wrongTypeThrows=" + (wrongThrew as string)
        report += "|beforeChannels=" + (countA as string) + "|afterChannels=" + (countC as string) + "|supported=" + (supported as string)
        report += "|first=" + (first as string) + "|repeat=" + (repeatValue as string) + "|edited=" + (second as string) + "|geometryUnchanged=" + (untouched as string)
        if countC != 11 or supported != true or first != 0.375 or repeatValue != first or second != 0.625 or not untouched do throw "target readback did not discriminate"
        outcome = "BOUNDED_VDATA_OBSERVED_NOT_ACCEPTANCE"
    )
    catch (report += "|ERROR=" + ((getCurrentException()) as string))
    try
    (
        if didConstruct then
        (
            if n == undefined or orig == undefined or h == undefined or not isValidNode orig do throw "lost exact original node; no handle-only adoption"
            if n != orig or (getHandleByAnim orig) != h or (getAnimByHandle h) != orig do throw "exact node continuity uncertain"
            if converted != undefined and (not isValidNode converted or converted != orig) do throw "converted candidate not exact original"
            if rootNode != root or objects.count != 1 or selection.count != 0 do throw "environment/census changed"
            if orig.children.count != 0 or (orig.parent != undefined and orig.parent != rootNode) do throw "unexpected hierarchy"
            local users = for o in objects where o.baseObject == orig.baseObject collect o
            if users.count != 1 or users[1] != orig do throw "shared base or neighbor"
            delete orig
            if isValidNode orig or objects.count != 0 do throw "cleanup not confirmed"
        )
        else if objects.count != 0 do throw "constructor outcome/census ambiguous"
        cleanupOK = true
    )
    catch (report += "|CLEANUP_ERROR=" + ((getCurrentException()) as string))
    if not cleanupOK do outcome = "INCOMPLETE_RESIDUE_OR_IDENTITY"
    report += "|outcome=" + outcome + "|cleanup=" + (cleanupOK as string) + "|objects=" + (objects.count as string) + "|selection=" + (selection.count as string) + "|dirtyBefore=" + (beforeDirty as string) + "|dirtyAfter=" + ((getSaveRequired()) as string)
    report
)
