(
-- Report the throw and the constructed value SEPARATELY, never folded into one
-- concatenated string. getCurrentException() does work inside a catch on this
-- build (measured 2026-10-05, 6 of 6 throw kinds; the old rule that it throws
-- itself was withdrawn as false), but its return value is exactly the kind of
-- thing that must not be string-concatenated into a probe result.
-- Resolve first, construct second, so "the class is absent" and "the class is
-- present but not creatable" cannot be confused for each other.
local out = ""
local id = undefined
try (id = execute "Loft") catch ()
local resolved = (id != undefined)
local threw = false
local created = false
if resolved then
(
    try (local o = id(); created = true) catch (threw = true)
)
out += "resolved=" + (resolved as string)
if threw then out += " THROWS" else out += " NOTHROW"
out += " created=" + (created as string)
out
)