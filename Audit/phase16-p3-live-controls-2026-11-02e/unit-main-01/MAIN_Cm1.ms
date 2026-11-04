-- MAIN ONLY; audit unit refusal, NO ARM and NO unit/scene/global setters.
(
    local artifactPath = "D:\\Rhino\\3dsmax-arch-nurbs-ultimate-skill\\Audit\\phase16-p3-live-controls-2026-11-02e\\unit-main-01\\expected_cm1.ms"
    local registryKey = "__P3W_783d78b17eb01726ad5d99bc803f4a60214e62007a35053696efcb1e01747c06" as name
    if globalVars.isGlobal registryKey do throw "UNIT_CONTROL_ABORT|fresh namespace already present"
    if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "UNIT_CONTROL_ABORT|actual mm/1 required; NEVER change scene units"
    if objects.count > 64 do throw "UNIT_CONTROL_ABORT|bounded census exceeded"
    local beforeNodes = for n in objects collect #(n, getHandleByAnim n)
    local beforeSelection = selection as array
    local beforeType = units.SystemType
    local beforeScale = units.SystemScale
    local beforeDirty = getSaveRequired()
    local beforePath = maxFilePath
    local beforeFile = maxFileName
    local beforeTime = currentTime
    local beforeSubobject = subObjectLevel
    local threw = false
    local reason = ""
    try (fileIn artifactPath quiet:true) catch (threw = true; reason = getCurrentException() as string)
    print ("UNIT_CONTROL_RAW|case=expected_cm1|threw=" + (threw as string) + "|reason=" + reason)
    if not threw do throw "UNIT_CONTROL_FAIL|expected actual runtime exception"
    if (findString reason "stage=entry") == undefined or (findString reason "SystemType mismatch") == undefined do throw "UNIT_CONTROL_FAIL|wrong refusal stage/reason; NOT target unit guard"
    if (findString reason "P3_REFUSED|") == undefined do throw "UNIT_CONTROL_FAIL|not actual runtime refusal"
    if globalVars.isGlobal registryKey do throw "UNIT_CONTROL_FAIL|registry declared/published before refusal"
    local afterNodes = for n in objects collect #(n, getHandleByAnim n)
    if afterNodes.count != beforeNodes.count do throw "UNIT_CONTROL_FAIL|scene census mutation"
    for i = 1 to beforeNodes.count do
        (if beforeNodes[i][1] != afterNodes[i][1] or beforeNodes[i][2] != afterNodes[i][2] do throw "UNIT_CONTROL_FAIL|exact node identity changed")
    local afterSelection = selection as array
    if beforeSelection.count != afterSelection.count do throw "UNIT_CONTROL_FAIL|selection mutation"
    for i = 1 to beforeSelection.count do
        (if beforeSelection[i] != afterSelection[i] do throw "UNIT_CONTROL_FAIL|selection identity changed")
    if units.SystemType != beforeType or units.SystemScale != beforeScale or getSaveRequired() != beforeDirty or maxFilePath != beforePath or maxFileName != beforeFile or currentTime != beforeTime or subObjectLevel != beforeSubobject do throw "UNIT_CONTROL_FAIL|units or protected context changed"
    print "UNIT_CONTROL_TARGET_REFUSAL_UNCHANGED|case=expected_cm1|arm=NOT_USED|live_geometry=NOT_TESTED"
)
