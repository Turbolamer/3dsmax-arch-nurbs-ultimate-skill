# P3.1 F01 measurement gaps — bounded read-only candidate

**Prepared offline; not executed or parsed in Max. P3.1 remains NOT ACCEPTED.**
This directory contains a candidate diagnostic, not an accepted poly-QA profile.
Only main may execute Max; its ordinary fresh-state and exact-reference guards,
lease protocol and source freeze remain mandatory. No existing artifact is changed.
Candidate `triangle_view_capture.ms` SHA-256 at author handoff:
`b15fb1d6b39a06921c4da7e21f744bb339b1f106680f0c840c69fbaa8c1d75c8`.
Main must recompute and review the actual bytes; a hash alone is not an approval.

## What is and is not observable

| Evidence | Current status and source |
|---|---|
| Existing one-quad smoke | Main's retained `Audit/_phase16-p3-measurement-smoke-capture-2026-11-02e.json` is an **actual tiny-quad control**, not the F01 output: `[4,4,1]` base, 8 evaluated vertices/12 triangles, native polygon count `null`. Its SHA-256 is `81b69fc1de39a9fcd410b9158cac6d317030d2f2bcd10bde4cd32afdf12c364a`. Its original envelope had a defect; do not silently upgrade that old run. |
| Historical P1 grid and 48 converted polygons | `Audit/EVIDENCE_2026-10-27.md` E-11–E-13 reports an earlier **different execution**, with grid 24/38/15 and evaluated 48 converted-poly faces/48 vertices, and 96 mesh triangles. E-13's path creates a scene snapshot and converts it to Editable_Poly. This is historical evidence, not measurement of a new emitted output; conversion-derived faces are not automatically native modifier-output MNMesh faces. |
| F01 analytical expectations | The actual input-only fixture and independently reviewed G.1 authority yield **predictions**: grid 24/38/15, base 24/36/12, 48 shell quads and 96 triangles, 87,000 cm² and 2,610,000 cm³. These are not measured arrays. The fixture itself is synthetic input, not a user's building. |
| Current emitted F01 | Main03's actual attempt failed baseline and removed its only node; retained raw result says objectsAfter=0 and lease **POISONED**. No current accepted F01 wall, full final capture, pre-delete grid capture, clean NOOP or live P3 acceptance exists. Do not erase, adopt or rearm Main03. |

The existing final `measure.ms` records final base polygon loops and evaluated
world-space **triangles**, not evaluated native polygon loops. Its `#grid` mode
only captures an actual, still-existing zero-modifier node; it cannot rewind a
completed build. Main03's emitted MAXScript is a **single synchronous `fileIn`**:
create vertices/faces, read back each `polyop.getFaceVerts`, print returned IDs,
delete the cut faces, add Shell, then perform baseline. The reads are emitter
self-checks; printed IDs/count do **not** contain the pre-deletion positions and
ordered loops required by the oracle. The failed attempt cleaned the node; its
retained result does not contain an independent earlier-grid capture. A later
final base, deleted slots, script source, predicted station arrays, or P1 run
cannot authenticate what existed during that specific earlier stage.

Without instrumenting/intercepting execution of the specific emitter, or a
separately reviewed debugger/breakpoint or execution-control mechanism proven not
to affect it, a separate post-`fileIn` read cannot capture the actual historical
pre-deletion stage. Such observation support is **not implemented or calibrated**
here. A rebuild (even from identical bytes), an ad-hoc grid, and a later `#grid`
reading are new observations, not recovery of Main03's grid. Whether a future
reviewed same-attempt observation fits the evidence contract is main's decision;
do not weaken the gate to count inferred or synthetic data.

## Candidate: explicit TriMesh-group evidence, not native polygon loops

`triangle_view_capture.ms` accepts `P3NextMeasurementTarget`, an exact live node
reference supplied and externally retained by main. It checks a target-only
scene, node/base/Shell anim-reference round trips, one Editable_Poly base and one
Shell. It makes one evaluated `snapshotAsMesh`, captures raw world-space vertices,
triangle indices, `getEdgeVis` flags, and the **per-triangle** results of
`meshop.getPolysUsingFace` with `ignoreVisEdges:false` and `threshhold:45.0`.
It also separately reads `getPolygonCount`, documented as counts **as if converted
to a mesh**; that is not a native polygon count. No expected polygon count or
predicted face is supplied to the query. A caller may compare the channels with
the old independent measurement only after proving same exact scene references.

Autodesk documents [`snapshotAsMesh` as an in-memory TriMesh including evaluated
modifiers](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-38562330-1435-4112-9265-DE965319A2F2),
[`meshop.getPolysUsingFace` as a grouping of faces sharing *invisible* edges whose
angle is below its threshold](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-EF78FA1A-A382-4BED-BA10-7C856A7551A5),
and [`getPolygonCount` as the face/vertex counts of a mesh conversion](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-D1D7EB56-A370-4B07-99B4-BC779FB87CAF).
[`polyop` operates on an Editable_Poly base or a node with that base](https://help.autodesk.com/view/MAXDEV/2026/ENU/?guid=GUID-B40F84EA-5F19-45B6-AA7C-0ADC77708BBE);
that statement alone does not establish access to evaluated modifier-output
native face loops. These are documentation leads, **not current live calibration**.

The offline `group_diagnostics.py` verifies that the returned per-triangle group
rows are a real partition, then derives single-cycle oriented boundaries only from
the actual supplied triangles; it refuses disconnected, branched, duplicate,
inconsistent or unsupported groups. Such loops are **derived triangle-group
boundaries**, never actual native polygon loops. They are not injected into
`evaluated.faces` or accepted by the original oracle. Face-edge flags are
recorded but the Python checker does not independently reimplement Max's angle
and visibility algorithm, so it cannot prove the group API correct. Equal group
counts or identical recovered rectangles can coexist with a different native
polygon representation. Even a diagnostic group count of 48, if observed, is
not evidence of 48 native evaluated polygons.

## Exact next-step instructions for main, conditional and sequential

1. Do **not** run this on the historical Main03 poisoned lease/node. First inspect
   the fresh actual scene, user state, selection, units, and lease/witness; stop on
   ambiguity. Review and hash the candidate against the bytes on disk immediately
   before execution. It introduces the global symbol `P3NextMeasurementTarget`;
   first verify the symbol is not in use and refuse to overwrite another value.
   Its output is returned over MCP, with no capture-file writes.
2. Independently review the candidate for safety and parser/API assumptions. In a
   controlled target-only scene, use **a separately main-owned temporary** tiny
   Editable_Poly quad + Shell, exact node/base/modifier references retained; their
   creation/deletion is a scene mutation **outside this read-only candidate** and
   only within main's current authorization. Compare candidate snapshot vertices/
   triangles with the previously tested independent measure script and directly
   re-read exact census, stack, geometry, transform, selection, time, dirty flag
   and file/units afterward. Use a translated/rotated control to catch double
   transforms. The candidate itself verifies only the explicitly recorded subset
   of those properties, not arbitrary scene immutability.
3. Run discriminating *separate* controls on main-owned data: an independently
   known visible-diagonal two-triangle patch versus an otherwise identical
   invisible-diagonal patch; an angled pair straddling the 45-degree threshold;
   a prevalidated, documented safe negative/control of main's choosing, plus a
   known positive seed. Do not feed out-of-range face IDs to native geometry APIs
   without a separately reviewed safety case.
   Use exact retained references, no filename/name/prefix authority; record raw
   wire, actual face IDs/edge flags and results. These checks require separate
   **main-authored** mutation/calibration code or an already available controlled
   test object; this directory does not create or mutate them. If raw groups fail
   partition consistency or behave differently than documented, stop and retain
   the evidence; don't treat a parser/API exception as proof an API is absent.
4. To invoke *once* after those preconditions are met, set the global to the
   externally retained exact node reference, then fileIn the reviewed file. The
   slot below is intentionally not executable until main substitutes its own
   existing node variable:

   ```maxscript
   P3NextMeasurementTarget = <main_exact_node_reference>
   fileIn "D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/Audit/phase16-p3-measurement-next-2026-11-03/triangle_view_capture.ms"
   ```

   Retain **the full bridge wire** and exact returned JSON string in new,
   exclusively owned evidence paths under main's own protocol. Do not substitute
   a name lookup or fabricate a return. Inspect bridge `ok/error`,
   `__MCP_MS_ERR__`, `status`, all exceptions and elapsed time; a transport
   success is not a capture. Explicitly clear only the input global value main
   itself supplied, after successful return, without touching registry witnesses.
   A failure or timeout: stop, inspect live state read-only, preserve any
   residual exact refs/resources, and do not blind-retry or clear dirty state.
5. Extract the unmodified returned JSON to a *new* file using main's evidence
   process. From repository root, evaluate without writing files:

   ```bash
   python -B Audit/phase16-p3-measurement-next-2026-11-03/group_diagnostics.py <extracted-capture.json>
   python -B Audit/phase16-p3-measurement-next-2026-11-03/group_diagnostics.py <extracted-capture.json> --measurement <existing-full-final-capture.json>
   ```

   Bracketed paths are placeholders for **new, actual** evidence, not files in
   this package. The optional comparison requires identical one-based indexed
   vertex/triangle arrays, reported node/base/Shell identity, transform and units; legitimate
   reindexing therefore refuses instead of being silently welded. Equal reported
   handles/bytes don't authenticate same session or prove no intervening edits;
   exact refs and binding still require main's observations.
   CLI exit 0 means diagnostics ran, and JSON **still says `INCOMPLETE`**.
6. An actual F01 use additionally requires a newly fixed, frozen and hash-bound
   real emitter result admitted by main, a genuinely live final target, current
   scene/reference/stack proof, separate full `measure.ms` capture, and independent
   source/artifact/evidence binding. The candidate's group data is supplemental;
   don't pass its derived loops to the oracle as actual faces. The original oracle's
   `check_independent_capture(...)` should continue to report `GRID_CAPTURE` and
   `EVALUATED_CAPTURE` INCOMPLETE without actual arrays. Triangle profile PASS
   is narrowly scoped geometry evidence, never full acceptance.

## Safety and boundedness

No scene node is deliberately created, modified, converted, renamed, selected,
hidden or deleted. Only the **exact local in-memory `snapshotAsMesh` value** is
deleted, on success and catch; it is never a scene node or the caller's target.
No file I/O, lookup-by-name, eval, undo, reset, save, layer/material/unit/lease
setter or `formattedPrint` is used. A `snapshotAsMesh` read nevertheless evaluates
the stack and may allocate memory or invoke callbacks; *query does not mean no
side effects*. Main must inspect exact cleanup on all paths. Exceptions raised
inside .NET serialization/cleanup can still escape; catch saves diagnostic before
cleanup and a native crash before return cannot be contained. The global symbol is
interpreter state. SaveRequired equality is checked, not cleared.

Target-only admission is intentional. Base counts have upper bounds 24/128/15;
evaluated mesh is admitted after snapshot allocation, <=64 vertices/96 triangles,
with <=96 group queries and bounded arrays. This cannot enforce a pre-evaluation
memory cap or hard two-second deadline; a heavy/plugin/foreign node can hang.
Use only small approved static test targets, not arbitrary scene geometry. String
construction/console transport and stack evaluation may still be costly; capture
can fail/truncate in transit. The candidate is not yet Max-parser tested, and
its per-face query, deletion, exact-handle and JSON behavior need live controls.

## Offline checks actually executed

```bash
python -B Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py
```

13 tests completed OK without SKIP as of this author's run. They exercise
synthetic two-quad/different-group controls, malformed/group/identity/unit/
orientation refusals, unmodified actual tiny-quad JSON and Main03 failure evidence,
an actual F01 **input/source prediction**, the existing oracle's explicitly
`synthetic_test` triangle-only and grid-only branches, and a lexical scene-operation
scan. They do not execute Max, prove parser correctness or verify a mesh-group API.
In the oracle synthetic control the triangle geometry profile can PASS, while
overall status and missing real evaluated polygons/grid remain INCOMPLETE. No
new live result, produced F01 fixture, true polygon loops, old artifact, P2 file,
package, installed copy or checkpoint is written by these tests.
