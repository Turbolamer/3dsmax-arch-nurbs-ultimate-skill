-- MAIN ONLY: bounded pre-registry unit refusal; no ARM, setters or scene edits.
(
    local p3ucResult = "UNIT_CONTROL_ERROR|no_result"
    try
    (
        local p3ucPath = "D:\\Rhino\\3dsmax-arch-nurbs-ultimate-skill\\Audit\\phase16-p3-live-controls-2026-11-02e\\unit-main-03\\NEGATIVE_MUTATED_type_only_same_factor.ms"
        local p3ucKey = "__P3W_957d2605b4f4d5af3a8f7e5de7fcd83c2659cc0e14be2dacb11855a8217886c3" as name
        if globalVars.isGlobal p3ucKey then p3ucResult = "UNIT_CONTROL_ABORT|fresh_registry_already_exists"
        else if units.SystemType != #millimeters or units.SystemScale != 1.0 then p3ucResult = "UNIT_CONTROL_ABORT|actual_mm_1_required_NEVER_change_units"
        else if objects.count > 64 then p3ucResult = "UNIT_CONTROL_ABORT|scene_census_ceiling"
        else
        (
            local p3ucNodes = for n in objects collect #(n, getHandleByAnim n)
            local p3ucSelection = selection as array
            local p3ucType = units.SystemType
            local p3ucScale = units.SystemScale
            local p3ucDirty = getSaveRequired()
            local p3ucFile = maxFileName
            local p3ucDir = maxFilePath
            local p3ucTime = currentTime
            local p3ucSubobject = subObjectLevel
            local p3ucThrew = false
            local p3ucReason = ""
            try (fileIn p3ucPath quiet:true) catch
                (p3ucThrew = true; p3ucReason = getCurrentException() as string)
            local p3ucAfterNodes = for n in objects collect #(n, getHandleByAnim n)
            local p3ucAfterSelection = selection as array
            local p3ucNodesEqual = p3ucNodes.count == p3ucAfterNodes.count
            if p3ucNodesEqual do for i = 1 to p3ucNodes.count do
                (if p3ucNodes[i][1] != p3ucAfterNodes[i][1] or p3ucNodes[i][2] != p3ucAfterNodes[i][2] do p3ucNodesEqual = false)
            local p3ucSelectionEqual = p3ucSelection.count == p3ucAfterSelection.count
            if p3ucSelectionEqual do for i = 1 to p3ucSelection.count do
                (if p3ucSelection[i] != p3ucAfterSelection[i] do p3ucSelectionEqual = false)
            local p3ucContextEqual = units.SystemType == p3ucType and units.SystemScale == p3ucScale and
                getSaveRequired() == p3ucDirty and maxFilePath == p3ucDir and maxFileName == p3ucFile and
                currentTime == p3ucTime and subObjectLevel == p3ucSubobject
            local p3ucRegistryAbsent = not globalVars.isGlobal p3ucKey
            local p3ucReasonMatches = (findString p3ucReason "SystemType mismatch") != undefined and
                ((findString p3ucReason "P3_REFUSE|") != undefined or (findString p3ucReason "P3_REFUSED|") != undefined)
            local p3ucProtectedEqual = p3ucNodesEqual and p3ucSelectionEqual and p3ucContextEqual and p3ucRegistryAbsent
            local p3ucStatus = if p3ucThrew and p3ucReasonMatches and p3ucProtectedEqual then
                "UNIT_CONTROL_TARGET_REFUSAL_UNCHANGED" else "UNIT_CONTROL_FAIL"
            local p3ucBriefReason = if p3ucReason.count > 900 then (substring p3ucReason 1 900) else p3ucReason
            p3ucResult = p3ucStatus + "|case=NEGATIVE_MUTATED_type_only_same_factor|threw=" + (p3ucThrew as string) +
                "|targetReason=" + (p3ucReasonMatches as string) + "|nodesExact=" + (p3ucNodesEqual as string) +
                "|selectionExact=" + (p3ucSelectionEqual as string) + "|contextEqual=" + (p3ucContextEqual as string) +
                "|registryAbsent=" + (p3ucRegistryAbsent as string) + "|units=" + ((units.SystemType) as string) +
                "/" + ((units.SystemScale) as string) + "|nodes=" + ((objects.count) as string) +
                "|dirty=" + ((getSaveRequired()) as string) + "|arm=NOT_USED|reason=" + p3ucBriefReason
        )
    )
    catch
    (
        local p3ucUnexpected = getCurrentException() as string
        if p3ucUnexpected.count > 900 do p3ucUnexpected = substring p3ucUnexpected 1 900
        p3ucResult = "UNIT_CONTROL_ERROR|case=NEGATIVE_MUTATED_type_only_same_factor|reason=" + p3ucUnexpected
    )
    p3ucResult
)
