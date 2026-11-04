# Prepared main-only R4/R5/R7 candidate probes

**UNEXECUTED.** No API availability, timing, complete snapshot or replay acceptance
is asserted. Execute with `fileIn`, not as raw top-level function definitions.

1. `r4-r5-single-quad-readers.ms`: one temporary empty mesh converted to Poly,
   four vertices, one quad, one Shell; separately guarded candidate node properties,
   controller reads, dependency reads, topology/map/VData/EData reader calls.
2. `r7-single-quad-readback-discriminators.ms`: same tiny owned geometry; clean/read-
   changed controls for detached vertices, face IDs/smoothing, selection, user
   buffer, Shell amount and rename/exact reference. This is **reader calibration**,
   not three-run execution or acceptance of the emitted wall artifact.

Both refuse nonempty/named scenes, retain exact references/handles and attempt
exact cleanup after exceptions. No reset/save/material/layer construction, no
name-based deletion, no mutation of existing user nodes, no live calls by author.
Main must inspect every `threw` and cleanup/census line. A failed target reader is
not absence; positive `#name` and bogus-property controls must discriminate.
The intended size is below ~2 seconds, but timing is **not measured**. Stop after
any timeout/incomplete cleanup. Dirty/undo history restoration is not claimed.
R1 and conversion behavior are already recorded by main in the dated registry
and identity-probe JSONs; these scripts do not replace those records.
