(
local p = QuadPatch()
local out = "OK classOf=" + ((classOf p) as string) + " superclass=" + ((superclassOf p) as string)
delete p
out
)