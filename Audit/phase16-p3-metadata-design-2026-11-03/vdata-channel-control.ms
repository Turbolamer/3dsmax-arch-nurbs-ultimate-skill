-- PREPARED, UNEXECUTED. Main only; fileIn as one short call after fresh inspection.
-- No assumptions about user scene: refuses unless empty, unnamed and unselected.
-- One exact owned node, 4 vertices, 1 quad, 1 Shell; no registry/layer/material writes.
-- This is a VData-reader control only, not production replay or metadata acceptance.
(
    local owned = undefined
    local h = undefined
    local created = false
    local cleanupOK = false
    local outcome = "INCOMPLETE"
    local dirtyBefore = undefined
    local startCount = undefined
    local startSelection = undefined
    try
    (
        startCount = objects.count
        startSelection = selection.count
        dirtyBefore = getSaveRequired()
        if startCount != 0 or startSelection != 0 do throw "admission: nonempty scene/selection"
        if maxFilePath != "" or maxFileName != "" do throw "admission: named scene"

        owned = Editable_Mesh()
        created = true
        h = getHandleByAnim owned
        if h == undefined or not isValidNode owned do throw "owned node/handle unavailable"
        local converted = convertTo owned Editable_Poly
        if not isValidNode converted do throw "conversion did not return an exact node"
        if (getHandleByAnim converted) != h or (getAnimByHandle h) != converted do throw "conversion identity uncertain"
        owned = converted
        if objects.count != 1 do throw "unexpected node census"

        local ids = #()
        for p in #([0,0,0], [10,0,0], [10,0,10], [0,0,10]) do
        (
            local id = polyop.createVert owned p
            if (classOf id) != Integer or id < 1 or (findItem ids id) != 0 do throw "invalid/duplicate vertex ID"
            append ids id
        )
        if ids.count != 4 do throw "quad vertex setup incomplete"
        local faceID = polyop.createPolygon owned ids
        if (classOf faceID) != Integer or faceID < 1 do throw "quad face setup incomplete"
        update owned
        local faceLoop = polyop.getFaceVerts owned faceID
        if faceLoop.count != 4 do throw "quad face loop count mismatch"
        for i = 1 to 4 do if faceLoop[i] != ids[i] do throw "quad face loop mismatch"
        local shellMod = Shell innerAmount:0.0 outerAmount:1.0 segments:1
        addModifier owned shellMod
        update owned
        if owned.modifiers.count != 1 or owned.modifiers[1] != shellMod do throw "Shell identity mismatch"
        local base = owned.baseObject

        local realPresent = undefined
        local realValue = undefined
        local realThrew = false
        local bogusPresent = undefined
        local bogusThrew = false
        local wrongTypeThrew = false
        local wrongTypeValue = undefined
        try (realPresent = isProperty owned #name) catch ()
        try (realValue = getProperty owned #name) catch (realThrew = true)
        try (bogusPresent = isProperty owned #P3MetadataBogusXYZ) catch ()
        try (getProperty owned #P3MetadataBogusXYZ) catch (bogusThrew = true)
        try (wrongTypeValue = polyop.getNumVDataChannels undefined) catch (wrongTypeThrew = true)
        print ("P3_VDATA_UNKNOWN|classification=INCOMPLETE|realPresent=" + (realPresent as string) +
            "|realThrew=" + (realThrew as string) + "|realValueClass=" + ((classOf realValue) as string) +
            "|bogusPresent=" + (bogusPresent as string) + "|bogusThrew=" + (bogusThrew as string) +
            "|wrongTypeThrew=" + (wrongTypeThrew as string) +
            "|wrongTypeUndefined=" + ((wrongTypeValue == undefined) as string) +
            "|wrongTypeClass=" + ((classOf wrongTypeValue) as string))
        if realPresent != true or realThrew or (classOf realValue) != String or realValue != owned.name or
            bogusPresent != false or not bogusThrew or not wrongTypeThrew do
            throw "positive/bogus/unknown reader controls did not discriminate"

        local countA = polyop.getNumVDataChannels base
        local countB = polyop.getNumVDataChannels base
        if (classOf countA) != Integer or countA < 0 or countA > 10 do
            throw "unsupported initial VData channel count; no channel changed"
        if countA != countB do throw "clean VData count unstable"
        local oldVert = polyop.getVert base ids[1]
        local oldX = oldVert.x
        local oldY = oldVert.y
        local oldZ = oldVert.z
        local oldNV = polyop.getNumVerts base
        local oldNF = polyop.getNumFaces base
        print ("P3_VDATA_CLEAN|count=" + (countA as string) + "|repeatEqual=" + ((countA == countB) as string))

        -- Channel 11 is outside Autodesk's documented reserved VData channels 1..10.
        -- This intentionally changes only the newly created disposable base object.
        polyop.setNumVDataChannels base 11 keep:true
        polyop.setVDataChannelSupport base 11 true
        local picked = #{}
        picked[ids[1]] = true
        polyop.setVDataValue base 11 picked 0.375
        local countC = polyop.getNumVDataChannels base
        local supportC = polyop.getVDataChannelSupport base 11
        local first = polyop.getVDataValue base 11 ids[1]
        local repeatFirst = polyop.getVDataValue base 11 ids[1]
        polyop.setVDataValue base 11 picked 0.625
        local second = polyop.getVDataValue base 11 ids[1]
        local afterVert = polyop.getVert base ids[1]
        local vertexSame = (afterVert.x == oldX and afterVert.y == oldY and afterVert.z == oldZ)
        local countsSame = ((polyop.getNumVerts base) == oldNV and (polyop.getNumFaces base) == oldNF)
        local countDetected = (countC != countA)
        local valueStable = (first == repeatFirst)
        local valueDetected = (first != second)
        print ("P3_VDATA_EDIT|countAfter=" + (countC as string) + "|support=" + (supportC as string) +
            "|first=" + (first as string) + "|second=" + (second as string) +
            "|firstClass=" + ((classOf first) as string) + "|secondClass=" + ((classOf second) as string) +
            "|countDetected=" + (countDetected as string) + "|valueStable=" + (valueStable as string) +
            "|valueDetected=" + (valueDetected as string) + "|vertexSame=" + (vertexSame as string) +
            "|countsSame=" + (countsSame as string))
        if (classOf countC) != Integer or (classOf supportC) != BooleanClass or
            (classOf first) != Float or (classOf second) != Float or
            countC != 11 or supportC != true or first != 0.375 or second != 0.625 or
            not countDetected or not valueStable or not valueDetected or not vertexSame or not countsSame do
            throw "mutation/readback/control incomplete"
        outcome = "BOUNDED_READERS_OBSERVED_ONLY"
    )
    catch (print ("P3_VDATA_INCOMPLETE|" + ((getCurrentException()) as string)))

    -- Cleanup is exact-reference/handle only. Never search by name or touch neighbors.
    try
    (
        if created then
        (
            if owned == undefined or h == undefined do throw "cleanup missing exact node/handle"
            if not isValidNode owned do throw "cleanup lost exact node reference; no handle-only adoption"
            if (getHandleByAnim owned) != h or (getAnimByHandle h) != owned do throw "cleanup handle mismatch"
            if objects.count != 1 do throw "cleanup unexpected node census"
            if owned.children.count != 0 do throw "cleanup unexpected children"
            if owned.parent != undefined and owned.parent != rootNode do throw "cleanup unexpected parent"
            local users = for other in objects where other.baseObject == owned.baseObject collect other
            if users.count != 1 or users[1] != owned do throw "cleanup unexpected base sharing"
            delete owned
            if isValidNode owned do throw "cleanup exact node remains valid"
            if objects.count != 0 do throw "cleanup unresolved node/residual"
        )
        else
        (
            if startCount == undefined do throw "creation status/census unavailable"
            if objects.count != startCount do
            (
                throw "creation failed with unexpected census; no owner to delete"
            )
        )
        cleanupOK = true
    )
    catch (print ("P3_VDATA_CLEANUP_INCOMPLETE|" + ((getCurrentException()) as string)))
    if not cleanupOK do outcome = "INCOMPLETE_RESIDUE"
    local dirtyAfter = undefined
    try (dirtyAfter = getSaveRequired()) catch ()
    print ("P3_VDATA_END|outcome=" + outcome + "|created=" + (created as string) +
        "|cleanupOK=" + (cleanupOK as string) + "|objectsBefore=" + (startCount as string) +
        "|objectsAfter=" + (objects.count as string) + "|selectionBefore=" + (startSelection as string) +
        "|selectionAfter=" + (selection.count as string) + "|dirtyBefore=" + (dirtyBefore as string) +
        "|dirtyAfter=" + (dirtyAfter as string))
)
