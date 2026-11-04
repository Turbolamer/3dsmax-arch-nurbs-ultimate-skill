(
local s = Sweep()
-- No delete: a standalone modifier instance is not a scene node.
-- "delete s" fails with: No "delete" function for sweep:Sweep
"OK classOf=" + ((classOf s) as string) + " superclass=" + ((superclassOf s) as string)
)