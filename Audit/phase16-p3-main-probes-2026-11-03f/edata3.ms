-- Main-only EData3 single-node control; NOT production comparator or acceptance.
(
    local n = undefined
    local orig = undefined
    local conv = undefined
    local h = undefined
    local constructed = false
    local cleaned = false
    local outcome = "INCOMPLETE"
    local report = "P3_EDATA3"
    local beforeDirty = getSaveRequired()
    local root = rootNode
    try
    (
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "admission scene not empty unnamed unselected"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "units mismatch"
        n = Editable_Mesh()
        constructed = true
        orig = n
        h = getHandleByAnim n
        if not isValidNode n or h == undefined or (getAnimByHandle h) != n or objects.count != 1 do throw "bind failed"
        conv = convertTo n Editable_Poly
        if not isValidNode orig or not isValidNode conv or conv != orig or (getHandleByAnim conv) != h or (getAnimByHandle h) != orig do throw "conversion identity uncertain"
        local ids = #()
        for p in #([0,0,0], [10,0,0], [10,0,10], [0,0,10]) do
        (
            local id = polyop.createVert orig p
            if classOf id != Integer or id < 1 or (findItem ids id) != 0 do throw "vertex id uncertain"
            append ids id
        )
        local face = polyop.createPolygon orig ids
        update orig
        if classOf face != Integer or face < 1 do throw "face setup failed"
        local b = orig.baseObject
        local countE = polyop.getNumEdges b
        if (polyop.getNumVerts b) != 4 or (polyop.getNumFaces b) != 1 or countE != 4 do throw "quad topology wrong"
        local hit = isProperty orig #name
        local miss = isProperty orig #P3EDataBogusNameF9
        local missThrew = false
        try (getProperty orig #P3EDataBogusNameF9) catch (missThrew = true)
        local wrongThrew = false
        try (polyop.getNumEDataChannels undefined) catch (wrongThrew = true)
        if hit != true or miss != false or not missThrew or not wrongThrew do throw "positive/miss/unknown controls failed"
        local c1 = polyop.getNumEDataChannels b
        local c2 = polyop.getNumEDataChannels b
        if classOf c1 != Integer or c1 < 0 or c1 > 2 or c1 != c2 do throw "initial EData unsupported"
        local edge = polyop.getEdgeVerts b 1
        local edgeA = edge[1]; local edgeB = edge[2]
        polyop.setNumEDataChannels b 3 keep:true
        polyop.setEDataChannelSupport b 3 true
        polyop.setEDataValue b 3 #{1} 0.375
        local c3 = polyop.getNumEDataChannels b
        local support = polyop.getEDataChannelSupport b 3
        local v1 = polyop.getEDataValue b 3 1
        local v2 = polyop.getEDataValue b 3 1
        polyop.setEDataValue b 3 #{1} 0.625
        local v3 = polyop.getEDataValue b 3 1
        local edgeAfter = polyop.getEdgeVerts b 1
        local unchanged = edgeAfter[1] == edgeA and edgeAfter[2] == edgeB and (polyop.getNumVerts b) == 4 and (polyop.getNumFaces b) == 1 and (polyop.getNumEdges b) == countE
        report += "|positive="+(hit as string)+"|bogusAbsent="+((not miss) as string)+"|bogusThrows="+(missThrew as string)+"|wrongTypeThrows="+(wrongThrew as string)
        report += "|beforeChannels="+(c1 as string)+"|afterChannels="+(c3 as string)+"|supported="+(support as string)+"|first="+(v1 as string)+"|repeat="+(v2 as string)+"|edited="+(v3 as string)+"|edgeAndCountsUnchanged="+(unchanged as string)
        if c3 != 3 or support != true or v1 != 0.375 or v2 != v1 or v3 != 0.625 or not unchanged do throw "target readback mismatch"
        outcome = "BOUNDED_EDATA_OBSERVED_NOT_ACCEPTANCE"
    )
    catch (report += "|ERROR="+((getCurrentException()) as string))
    try
    (
        if constructed then
        (
            if orig == undefined or h == undefined or not isValidNode orig do throw "lost exact original"
            if n != orig or (getHandleByAnim orig) != h or (getAnimByHandle h) != orig do throw "original identity uncertain"
            if conv != undefined and (not isValidNode conv or conv != orig) do throw "converted candidate uncertain"
            if rootNode != root or objects.count != 1 or selection.count != 0 do throw "census/selection changed"
            if orig.children.count != 0 or (orig.parent != undefined and orig.parent != rootNode) do throw "hierarchy changed"
            local users = for o in objects where o.baseObject == orig.baseObject collect o
            if users.count != 1 or users[1] != orig do throw "base-sharing or neighbor"
            delete orig
            if isValidNode orig or objects.count != 0 do throw "cleanup unresolved"
        )
        else if objects.count != 0 do throw "constructor/census ambiguous"
        cleaned = true
    )
    catch (report += "|CLEANUP_ERROR="+((getCurrentException()) as string))
    if not cleaned do outcome = "INCOMPLETE_RESIDUE_OR_IDENTITY"
    report += "|outcome="+outcome+"|cleanup="+(cleaned as string)+"|objects="+(objects.count as string)+"|selection="+(selection.count as string)+"|dirtyBefore="+(beforeDirty as string)+"|dirtyAfter="+((getSaveRequired()) as string)
    report
)
