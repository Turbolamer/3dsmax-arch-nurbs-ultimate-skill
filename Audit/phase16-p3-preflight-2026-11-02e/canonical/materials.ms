(
local out = ""
local names = #("OpenPBR", "PhysicalMaterial", "Standard")
for n in names do
(
    local id = undefined
    try (id = execute n) catch ()
    if id == undefined then
    (
        out += n + "=absent "
    )
    else
    (
        local made = "notcreatable"
        try (local mt = id(); made = "ok") catch (made = "notcreatable")
        out += n + "=" + made + " "
    )
)
out
)