(
local s = Rectangle()
s.width = 40.0
s.length = 40.0
local sm = undefined
local cthrew = false
try (sm = Sweep()) catch (cthrew = true)
local athrew = false
if not cthrew then
(
    try (addModifier s sm) catch (athrew = true)
)
-- Use the .modifiers PROPERTY. The standalone "modifiers s" function form
-- fails with: Type error: Call needs function or class, got: undefined
local mods = 0
try (mods = s.modifiers.count) catch ()
local out = "ctor="
if cthrew then out += "THROWS" else out += "ok"
out += " attach="
if athrew then out += "THROWS" else out += "ok"
out += " mods=" + (mods as string)
if mods > 0 then
(
    local first = "?"
    try (first = s.modifiers[1].name) catch ()
    out += " first=" + first
)
-- delete s, the shape node (a bare Sweep() would NOT be deletable). Guarded so a
-- cleanup failure cannot swallow the result string this probe exists to return.
try (delete s) catch ()
out
)