-- CANDIDATE ONLY, NEVER LIVE-EXECUTED BY AUTHOR.
-- One local-only call: no scene/global/file writes and no delete. Calibration,
-- not a guard for a wall; Max syntax, equality semantics and duration unproven.
(
    local P16LocalLease
    struct P16LocalLease (values = #())

    local origValues = #("schema", "identity", "binding", "namespace", "ARMED", "abcDEF0123456789")
    local original = P16LocalLease values:origValues
    local alias = original
    local equalValues = #("schema", "identity", "binding", "namespace", "ARMED", "abcDEF0123456789")
    local equalOther = P16LocalLease values:equalValues
    local originalNonce = copy "abcDEF0123456789"
    local nonceSource = copy "abcDEF0123456789"
    local nonceDetached = copy nonceSource
    local changedNonce = "abcDEF012345678X"
    local rootBefore = rootNode
    local rootHandle = getHandleByAnim rootBefore
    local countBefore = objects.count
    local selectionBefore = selection.count
    local dirtyBefore = getSaveRequired()
    local pathBefore = copy maxFilePath
    local fileBefore = copy maxFileName
    local timeBefore = currentTime as integer
    local subBefore = subObjectLevel
    local unitsBefore = units.SystemType
    local scaleBefore = units.SystemScale as double

    local out = "P16_LOCAL_CALIBRATION_NOT_ACCEPTANCE"
    out += "|structAlias=" + ((alias == original) as string)
    out += "|structFreshUnequal=" + ((equalOther != original) as string)
    out += "|valuesAlias=" + ((original.values == origValues) as string)
    out += "|valuesFreshUnequal=" + ((equalValues != origValues) as string)
    out += "|nonceDifferentSameLength=" + ((changedNonce.count == originalNonce.count and changedNonce != originalNonce) as string)
    original.values[6] = changedNonce
    out += "|detachedExpectedUnchanged=" + ((originalNonce == "abcDEF0123456789" and original.values[6] != originalNonce) as string)
    -- Test the much stronger question: does in-place source mutation reach the
    -- purported copy? A throw is an unverified API, not a passing control.
    local nonceCopyError = undefined
    try (nonceSource[1] = "Z") catch (nonceCopyError = getCurrentException())
    if nonceCopyError != undefined then out += "|nonceCopyMutationError=" + (nonceCopyError as string)
    else out += "|nonceInPlaceSourceChanged=" + ((nonceSource == "ZbcDEF0123456789") as string) + "|nonceCopyStayed=" + ((nonceDetached == "abcDEF0123456789") as string)
    original.values = equalValues
    out += "|valuesReplacementSeen=" + ((original.values != origValues and original.values == equalValues) as string)
    out += "|realGlobal=" + ((globalVars.isGlobal #rootNode) as string)
    out += "|bogusGlobalAbsent=" + ((not (globalVars.isGlobal #P16_ABSOLUTELY_BOGUS_NEXT_20261103F_74EBC2)) as string)
    out += "|rootRoundtrip=" + ((rootHandle != undefined and (getAnimByHandle rootHandle) == rootBefore and rootBefore == rootNode) as string)
    out += "|sceneContextUnchanged=" + ((objects.count == countBefore and selection.count == selectionBefore and getSaveRequired() == dirtyBefore and maxFilePath == pathBefore and maxFileName == fileBefore and (currentTime as integer) == timeBefore and subObjectLevel == subBefore and units.SystemType == unitsBefore and (units.SystemScale as double) == scaleBefore) as string)
    out
)
