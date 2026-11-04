(
    global P3MeasurementTarget
    if P3MeasurementTarget != undefined do throw "P3 measurement target global occupied"
    if objects.count != 0 do throw "P3 measurement calibration requires empty scene"
    local owned = undefined
    local out = "P3_MEASUREMENT_CALIBRATION"
    try
    (
        owned = Editable_Mesh()
        local handle = getHandleByAnim owned
        local converted = convertTo owned Editable_Poly
        if not isValidNode converted or getHandleByAnim converted != handle do throw "conversion exact identity unavailable"
        owned = converted
        local ids = for p in #([0,0,0],[10,0,0],[10,0,10],[0,0,10]) collect polyop.createVert owned p
        polyop.createPolygon owned ids
        update owned
        owned.rotation = quat 90 [0,0,1]
        owned.pos = [100,200,300]
        P3MeasurementTarget = owned
        out += "|capture=" + (fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-measurement-2026-11-02e/calibrate_snapshot.ms")
    )
    catch (out += "|EXCEPTION=" + (getCurrentException() as string))
    try (if isValidNode owned do delete owned) catch (out += "|CLEANUP_ERROR=" + (getCurrentException() as string))
    P3MeasurementTarget = undefined
    out += "|objectsAfter=" + (objects.count as string)
    out
)
