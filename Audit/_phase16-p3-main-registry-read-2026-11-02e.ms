(
    global P3ERegistryProbe
    local out = "P3_REGISTRY_READ"
    if P3ERegistryProbe == undefined then out += "|REFUSED_UNDEFINED"
    else if classOf P3ERegistryProbe != P3ERegistryProbeType then out += "|REFUSED_TYPE"
    else out += "|state=" + (P3ERegistryProbe.state as string)
    out
)
