(
    global P3MeasurementTarget
    global P3MeasurementOutput
    global P3MeasurementStage
    if P3MeasurementTarget != undefined or P3MeasurementOutput != undefined or P3MeasurementStage != undefined do throw "P3 measurement globals occupied"
    if objects.count != 0 do throw "P3 measurement smoke requires empty scene"
    local owned = undefined
    local out = "P3_MEASUREMENT_SMOKE"
    try
    (
        owned = Editable_Mesh()
        local h = getHandleByAnim owned
        local converted = convertTo owned Editable_Poly
        if not isValidNode converted or getHandleByAnim converted != h do throw "conversion exact identity unavailable"
        owned = converted
        local ids = for p in #([0,0,0],[100,0,0],[100,0,100],[0,0,100]) collect polyop.createVert owned p
        polyop.createPolygon owned ids
        update owned
        addModifier owned (Shell innerAmount:0.0 outerAmount:10.0 segments:1)
        update owned
        P3MeasurementTarget = owned
        P3MeasurementOutput = "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/_phase16-p3-measurement-smoke-capture-2026-11-02e.json"
        P3MeasurementStage = #final
        out += "|capture=" + (fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-measurement-2026-11-02e/measure.ms")
    )
    catch (out += "|EXCEPTION=" + (getCurrentException() as string))
    try (if isValidNode owned do delete owned) catch (out += "|CLEANUP_ERROR=" + (getCurrentException() as string))
    P3MeasurementTarget = undefined
    P3MeasurementOutput = undefined
    P3MeasurementStage = undefined
    out += "|objectsAfter=" + (objects.count as string)
    out
)
