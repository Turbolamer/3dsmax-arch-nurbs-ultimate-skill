(
local st = undefined
local ss = undefined
local out = ""
try ( st = units.SystemType as string ) catch ( st = "THREW" )
try ( ss = units.SystemScale as string ) catch ( ss = "THREW" )
out += "SystemType=" + st + " SystemScale=" + ss
out
)