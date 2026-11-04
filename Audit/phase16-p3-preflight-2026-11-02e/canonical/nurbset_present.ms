(
-- NOTE: do NOT use "get #NURBSSet" to test for this class. It returns
-- undefined even when the class exists, which makes the probe pass vacuously.
-- Resolve the identifier and construct it instead.
local id = undefined
try (id = execute "NURBSSet") catch ()
local made = "no-class"
if id != undefined then
(
    try (local o = id(); made = "CREATED:" + ((classOf o) as string))
    catch (made = "not-creatable")
)
made
)