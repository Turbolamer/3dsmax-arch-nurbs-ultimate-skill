(
    global P3ERegistryProbe
    global P3ERegistryProbeType
    if P3ERegistryProbe != undefined or P3ERegistryProbeType != undefined do throw "P3 probe globals already occupied"
    struct P3ERegistryProbeType (state = #armed, values = #())
    local witness = P3ERegistryProbeType values:#(1.0, 2.0)
    local equalValueOther = P3ERegistryProbeType values:#(1.0, 2.0)
    local out = "P3_REGISTRY_PROBE"
    try
    (
        P3ERegistryProbe = witness
        out += "|aliasEqual=" + ((P3ERegistryProbe == witness) as string)
        out += "|separateEqual=" + ((equalValueOther == witness) as string)
        for i = 1 to 3 do out += "|read" + (i as string) + "=" + (fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/_phase16-p3-main-registry-read-2026-11-02e.ms")
        out += "|witnessStill=" + ((P3ERegistryProbe == witness) as string)
        P3ERegistryProbe = undefined
        out += "|missing=" + (fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/_phase16-p3-main-registry-read-2026-11-02e.ms")
        P3ERegistryProbe = 123
        out += "|wrongType=" + (fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/_phase16-p3-main-registry-read-2026-11-02e.ms")
        local raw = [1.0, 2.0, 3.0]
        local detached = #(raw.x, raw.y, raw.z)
        raw.x = 99.0
        out += "|scalarDetached=" + ((detached[1] == 1.0 and raw.x == 99.0) as string)
    )
    catch (out += "|EXCEPTION=" + (getCurrentException() as string))
    P3ERegistryProbe = undefined
    P3ERegistryProbeType = undefined
    out += "|objects=" + (objects.count as string)
    out
)
