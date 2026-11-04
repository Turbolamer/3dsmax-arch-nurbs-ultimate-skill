-- PREPARED, UNEXECUTED. Main only: bounded read-only candidate, no node creation.
-- Neither this probe nor Autodesk documentation proves layer replay safety.
(
    local objectCountBefore = undefined
    local selectionCountBefore = undefined
    local dirtyBefore = undefined
    local timeBefore = undefined
    local layerCount = undefined
    local firstLayer = undefined
    local aliasLayer = undefined
    local firstTarget = undefined
    local aliasTarget = undefined
    local targetThrew = false
    local h = undefined
    local handleThrew = false
    local rootOK = false
    local bogusPresent = undefined
    local bogusThrew = false
    local layerPresent = undefined
    local outcome = "INCOMPLETE"
    try
    (
        objectCountBefore = objects.count
        selectionCountBefore = selection.count
        dirtyBefore = getSaveRequired()
        timeBefore = currentTime as integer
        layerCount = LayerManager.count
        if (classOf layerCount) != Integer or layerCount < 1 do throw "layer count unavailable"
        firstLayer = LayerManager.getLayer 0
        aliasLayer = LayerManager.getLayer 0
        if firstLayer == undefined or aliasLayer == undefined do throw "first layer unavailable"

        local nameOK = false
        try (nameOK = (isProperty firstLayer #name) and ((getProperty firstLayer #name) != undefined)) catch ()
        try (bogusPresent = isProperty firstLayer #P3LayerBogusXYZ) catch ()
        try (getProperty firstLayer #P3LayerBogusXYZ) catch (bogusThrew = true)
        try (layerPresent = isProperty firstLayer #layerAsRefTarg) catch ()
        try
        (
            firstTarget = firstLayer.layerAsRefTarg
            aliasTarget = aliasLayer.layerAsRefTarg
        )
        catch (targetThrew = true; print ("P3_LAYER_TARGET_ERROR|" + ((getCurrentException()) as string)))
        try
        (
            local rh = getHandleByAnim rootNode
            rootOK = (rh != undefined and (getAnimByHandle rh) == rootNode)
        ) catch ()
        if not targetThrew and firstTarget != undefined do
        (
            try (h = getHandleByAnim firstTarget) catch (handleThrew = true)
        )
        local aliasEqual = undefined
        local handleRoundtrip = undefined
        if not targetThrew and firstTarget != undefined and aliasTarget != undefined do
            try (aliasEqual = firstTarget == aliasTarget) catch ()
        if not handleThrew and h != undefined do
            try (handleRoundtrip = (getAnimByHandle h) == firstTarget) catch ()
        print ("P3_LAYER_TARGET|nameOK=" + (nameOK as string) + "|bogusPresent=" + (bogusPresent as string) +
            "|bogusThrew=" + (bogusThrew as string) + "|targetIsProperty=" + (layerPresent as string) +
            "|targetThrew=" + (targetThrew as string) + "|targetUndefined=" + ((firstTarget == undefined) as string) +
            "|targetClass=" + ((classOf firstTarget) as string) + "|aliasEqual=" + (aliasEqual as string) +
            "|rootControl=" + (rootOK as string) + "|handleThrew=" + (handleThrew as string) +
            "|handleUndefined=" + ((h == undefined) as string) + "|handleRoundtrip=" + (handleRoundtrip as string))

        -- A second pre-existing layer is a discrimination candidate, never an excuse to create one.
        if layerCount >= 2 then
        (
            local differentLayer = undefined
            local differentTarget = undefined
            local differentThrew = false
            local distinct = undefined
            try
            (
                differentLayer = LayerManager.getLayer 1
                differentTarget = differentLayer.layerAsRefTarg
                if firstTarget != undefined and differentTarget != undefined do distinct = (firstTarget != differentTarget)
            )
            catch (differentThrew = true; print ("P3_LAYER_DISTINCT_ERROR|" + ((getCurrentException()) as string)))
            print ("P3_LAYER_DISTINCT|threw=" + (differentThrew as string) +
                "|targetUndefined=" + ((differentTarget == undefined) as string) + "|distinct=" + (distinct as string))
        )
        else print "P3_LAYER_DISTINCT|INCOMPLETE|no second existing layer; no layer created"

        if nameOK and bogusPresent == false and bogusThrew and rootOK and not targetThrew and
            aliasEqual == true and not handleThrew and handleRoundtrip == true do
            outcome = "REPEAT_HANDLE_OBSERVED_ONLY"
    )
    catch (print ("P3_LAYER_READONLY_INCOMPLETE|" + ((getCurrentException()) as string)))
    local dirtyAfter = undefined
    local timeAfter = undefined
    try (dirtyAfter = getSaveRequired()) catch ()
    try (timeAfter = currentTime as integer) catch ()
    print ("P3_LAYER_READONLY_END|outcome=" + outcome + "|layers=" + (layerCount as string) +
        "|objectsBefore=" + (objectCountBefore as string) + "|objectsAfter=" + (objects.count as string) +
        "|selectionBefore=" + (selectionCountBefore as string) + "|selectionAfter=" + (selection.count as string) +
        "|dirtyBefore=" + (dirtyBefore as string) + "|dirtyAfter=" + (dirtyAfter as string) +
        "|timeBefore=" + (timeBefore as string) + "|timeAfter=" + (timeAfter as string))
)
