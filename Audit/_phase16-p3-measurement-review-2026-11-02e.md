# P3 independent measurement-source review — 2026-11-02e

> **FINAL ADDENDUM below supersedes the old-source coordinate blocker.** Owner
> repaired the source during this review; current hash `c8f93cca…`. **GO for main's
> tiny actual `measure.ms` fileIn calibration**, not yet F01 acceptance. The initial
> review remains intact as historical evidence for the old `67e7294d…` bytes.

## Verdict and frozen source

**GO only for a tiny, coordinator-owned diagnostic calibration; NO-GO for actual
F01 measurement/acceptance with this source.** A translated one-quad control is
mandatory: identity-only calibration masks the definite coordinate-space defect
at line 268. No Max call, source edit, evidence-file write, or scene operation was
performed by this reviewer. The only new artifact owned here is this report.

Reviewed all **416 lines / 24,038 bytes** of
`Audit/phase16-p3-measurement-2026-11-02e/measure.ms`:

```text
SHA-256 67e7294df6b8d7b7e62495b6944d6ae2259501e05a75d7227015ac0ad22970b4
```

This verdict binds those exact bytes, not later owner repairs. Main must rehash
immediately before `fileIn`, inspect any changes, and bind the actually executed
hash to evidence. Source owner is separate; **do not change it under this review's
ownership**. Supporting README/adapter/offline tests and current coordinator brief
and bounded contract were read for context; their claims are not live evidence.

## Critical targeted source lines for main

| Lines in `measure.ms` | Finding / consequence |
|---|---|
| **185–208** | Exact node and base anim-reference round trips; accepts only `Editable_Poly`; `#final` requires exactly one Shell, `#grid` zero modifiers. Base ceilings 64V/128E/32F. No lookup by name. Does **not** itself enforce target-only scene, mm/1, Shell amounts/segments, identity transform, static controllers, or main's tighter initial F01 ceilings. Main must admit these independently. |
| **203–206** | Scene references collected before 64-node refusal; safe read, but enumeration itself is not capped in advance. Target-only calibration avoids arbitrary-scene cost. |
| **212–213** | Base-local vertices multiplied once by `n.objectTransform`: appropriate base-local-to-world operation under the stated convention. |
| **264–268** | `tmpMesh = snapshotAsMesh n`, then **`getVert tmpMesh i * n.objectTransform`**. Standing verified skill rule says `snapshotAsMesh` already yields WORLD-space TriMesh; line 268 therefore double-transforms evaluated coordinates. README lines 53–54 repeat the conflicting object-space assumption. This is a source defect relative to the accepted rule, not an API-absence finding. |
| **267, 271–292** | Counts refused above 256V/256T, but only **after** evaluation. Wrong evaluated coordinates feed world normals/bounds, volume origin, JSON and bbox-overlap candidates. Pure translation preserves area/volume, so checking only those will not detect the error. Empty evaluated mesh has no explicit lower bound; it falls into catch rather than valid capture. |
| **293–294; 404–406** | Only scene-like deletion operands are the **exact local `tmpMesh` reference**, once on success and catch retry if needed. No deletion of target, other scene nodes, names or prefixes. Actual TriMesh cleanup method/release remains runtime-unverified: repo has historical `free <TriMesh>` guidance as well as skill `delete` guidance. Do not infer successful release from static syntax; inspect calibration outcome/errors. |
| **297–315** | Shell properties and enabled states only read; no stack changes. Up to 128 properties, nested arrays depth 8/count 1024. Unknown/read-failed property explicitly adds INCOMPLETE issue. Arbitrary property getters can still be slow; a tiny known Shell is the calibration admission. |
| **318–354** | Census reads all admitted nodes and their bboxes; no clones/conversions. Before/after anim-handle set check proves census identity stability only, not whole-scene immutability or unchanged target geometry/materials/controllers/selection/dirty flag. Unrelated evaluated bboxes can be expensive. |
| **355–365** | Data is explicitly `CAPTURED_NOT_ACCEPTED`; units are measured, not set. Evaluated polygon count and missing historic grid remain INCOMPLETE. Bbox-only occlusion caveat is explicit. No oracle acceptance or synthetic reconstruction hidden here. |
| **367–396** | Output omitted -> returns JSON only. Supplied path -> exactly one drive-qualified normalized filename, UTF-8 bytes, 2 MiB refusal, `FileMode.CreateNew` + `FileAccess.ReadWrite` + `FileShare.None`, write/flush/hash actual stream/close. No overwriting/deleting existing evidence or directory creation in source. |
| **399–413** | Catch attempts exact TriMesh deletion and exact stream close, returns INCOMPLETE and whether new output was created. **Line 402 formats `getCurrentException()` before cleanup**, contrary to its “Cleanup first” comment; low ordinary risk because that API is verified working, but not strict cleanup-first exception robustness. A partial new file is deliberately retained, not removed. |

## Calibration-only admission and discriminating expectations

Main should use its already approved bounded temporary-node mechanism, retaining
the **exact created reference** for later cleanup; this measurement file does not
create or delete the calibration node itself. Set all three input globals
explicitly: exact `P3MeasurementTarget`, `P3MeasurementStage = #final`, and
**`P3MeasurementOutput = undefined`** for the first diagnostic call. Do not inherit
a stale output path or stage from the earlier invocation. One call/file at a time.

Use one static local-space XZ quad, outward -Y winding, e.g. native vertices
`[0,0,0], [100,0,0], [100,0,100], [0,0,100]`, one Shell with inner 0 / outer 20 /
segments 1, native mm/1. The **translated control** has a pure node translation
`[1000,2000,3000]`, no rotation/scale/object-offset surprises. Main may first run
identity for syntax/serialization diagnostics, but identity is insufficient.

Independent literal expected native WORLD bounds under the accepted snapshot rule:

| Measurement | Correct translated control | Predicted erroneous line-268 result |
|---|---|---|
| Base | min `[1000,2000,3000]`, max `[1100,2000,3100]` | Base unaffected; line 213 transforms once. |
| Evaluated Shell | min **`[1000,1980,3000]`**, max **`[1100,2000,3100]`** | min **`[2000,3980,6000]`**, max **`[2100,4000,6100]`** from a second translation. |

Compare **actual vertex positions/bounds and base/evaluated alignment**, not only
area or volume. The cube-equivalent volume is 200,000 native units³ = 200 cm³ in
mm/1 on either translated version, so a volume-only positive would be misleading.
The calibration is diagnostic evidence, not an actual produced F01 fixture.

If runtime coordinates disagree with the standing rule, record raw vertices,
actual transform and a known-good direct read in the same controlled experiment;
do not silently change the rule or accept the script. Any source repair must be
made by its owner, rehashed/reviewed, and the translated control repeated **before
actual F01 capture**. Identity F01 geometry cannot waive the known defect.

On every calibration outcome main must inspect bridge error/`__MCP_MS_ERR__`, the
returned JSON status/issues, cleanup diagnostics and separate fresh scene state.
Stop on timeout or uncertainty; no repeated blind call or broad node cleanup.
The script's `CAPTURED_NOT_ACCEPTED` envelope is never an acceptance verdict.

## Scene safety, temporary resources, and output authority

No malicious broad writes, generated code execution, save/reset, unit/material/
layer/selection setters, snapshot scene-node creation, `convertTo*`, clone/copy of
scene nodes, stack collapse, or modifier addition were found. `copy` at line 118
copies Point3 values only. `deleteItem` in boundary tracing changes local arrays,
not geometry. `snapshotAsMesh` at line 265 is the sole snapshot operation and
allocates a **temporary in-memory mesh**, not a scene snapshot node. Queries can
evaluate caches/controllers/plugins; static inspection does not prove they cannot
trigger arbitrary third-party callbacks. Global input-symbol declarations at
7–9 also mean this is not zero-change to the entire Max interpreter environment.

Cleanup ownership is appropriately narrow: `tmpMesh` starts undefined, has only
the direct `snapshotAsMesh` assignment, and is never assigned `n`, a name lookup,
or another scene reference. A pre-assignment native exception cannot be recovered
as an allocated resource the script never received. `delete tmpMesh` failures
should yield INCOMPLETE/cleanup issue, not a false positive. Hash-provider Dispose
at 388 has no separate catch/finally; an I/O/hash exception can retain a small
managed resource until GC, while outer catch still attempts stream close. No
resource/crash-atomicity guarantee follows from this source.

Exclusive output is **narrowly true for the caller's supplied path**, not an
allowlisted evidence-root sandbox. Lines 370–376 do not reject NTFS alternate
data-stream syntax, inspect reparse points, constrain an extension, or bind to a
private run directory. `CreateNew` prevents an ordinary existing-file overwrite;
it does not by itself establish path ownership or arbitrary-race safety. For a
later I/O calibration, main must choose a freshly inspected exact local JSON leaf
inside its private owned run directory, ordinary drive path, no ADS/reparse/device
path, and no concurrent writer. Failure may leave only that exact newly created
file; retain it as failed evidence and use a different approved leaf next time.
No need to test I/O during the first translated-coordinate diagnostic.

## Bounds and syntax/serialization risks

- Numeric mesh/scene ceilings and boundary-loop progress are explicit. Boundary
  tracing removes one unused edge per successful step and caps its steps; O(E²)
  work is tiny for a one-quad target. No unbounded procedural generation found.
- **Not a hard <2-second bound:** `snapshotAsMesh` happens before evaluated-count
  refusal, property getters and unrelated bboxes may be expensive, and the 2 MiB
  test occurs after string construction (and is absent in return-JSON mode).
  Names/property strings are not length-limited; depth/array limits are not a
  global serialization budget. Admit tiny target-only calibration, not arbitrary
  64-object scenes. `elapsed_ms` reports time; it is not cancellation/deadline.
- Operational **`formattedPrint` is absent**. The text occurs only in a comment.
  Serialization uses `.NET System.String.Format` invariant `G17` (49–54), with
  same-call positive double, negative, escaped-string and control-character checks
  (176–183). These are good fail-closed controls but require actual `fileIn` to
  verify overload binding/boxing/precision; Python tests cannot establish them.
- The `\n`, quote and backslash literals are in a disk `.ms` loaded with `fileIn`,
  not a long bridge-embedded script string. They are not automatically the known
  bridge unescaping failure. Use a simple forward-slash wrapper file path; actual
  escaping controls at 182–183 decide the operational result.
- Helper `fn` declarations are inside the parenthesized **fileIn** scope, not the
  known broken bare bridge top-level `fn` route. Actual MAXScript parse and lexical
  helper access still require calibration; delimiter balance is not a parser.
  Inspect any compiler diagnostic literally, including the loop-local `pi` at
  309–312 (same spelling as the numeric global) if reported; this review does not
  assert a compile failure or nonexistent API from that spelling alone.

## Executed offline checks and limits

A reviewer-authored Python in-memory lexical scan stripped comments/string
contents, checked balanced quotes/delimiters, then located operational tokens:
**only `snapshotAsMesh` at 265, only `delete tmpMesh` at 293 and 406**. No operational
`formattedPrint`, `convertTo`, `convertToMesh`, `convertToPoly`, `collapseStack`,
`addModifier`, `deleteModifier`, `getNodeByName`, `createFile`, `openFile`,
`deleteFile`, `makeDir`, `saveMaxFile`, `resetMaxFile`, `execute`, `fileIn`,
`shellLaunch`, or `DOSCommand`. Source bytes were identical before/after the scan;
SHA is above. No files were emitted by that checker. Its first shell-wrapped
invocation had a Python backslash-quoting SyntaxError before inspecting the source;
the corrected character-code scanner completed successfully. Neither run touched
Max or measurement source. Existing synthetic adapter tests were not promoted to
runtime evidence, and no native MAXScript parser was available here.

**Bottom line:** narrowly safe to attempt a tiny exact-reference, no-file-output
diagnostic calibration in main's controlled scene; **not fit for actual F01 world-
coordinate evidence until line 268's assumption is resolved and independently
recalibrated on a frozen reviewed source hash.**

## Final addendum — owner repair and executed main control

**Current final verdict: GO for a tiny actual `measure.ms` fileIn calibration in
main's controlled target-only scene**, with exact externally retained node
reference, explicit stage and **output undefined on the first call**. No Max call
or measurement-source change was made by this reviewer. F01 measurement/acceptance
remains gated on successful actual script calibration, serialization/cleanup
inspection and main's independent oracle. The initial specific double-transform
blocker is **repaired in source and corroborated by main's executed independent
snapshot control**; it is not an outstanding source defect in the current bytes.

### Final frozen hashes

```text
c8f93ccae10f2fc1f0c2b5aa0b8cc3dae0ebe6619518241785a05516c976e832  measure.ms
  24,123 bytes / 417 lines
814ea958cdc1fe91832e3332601adeade29f883a473dfc230a6ee9a8a1d41dac  calibrate_snapshot.ms
  5,228 bytes / 95 lines
63d93d7f82765f7186a5a81adbd88a90ddf1f3af8f6383acb2923681fa4e30cf  Audit/_phase16-p3-snapshot-space-probe-2026-11-02e.json
```

Both `.ms` paths above are under
`Audit/phase16-p3-measurement-2026-11-02e/`. Latest rehash matched the revised
measurement source. Main still rehashes immediately before execution.

### Exact verified delta, not a blanket trust in owner report

I re-read revised lines 250–314 and 350–417. An independent in-memory byte
reconstruction replaced current lines **264–269** with the five original lines;
the reconstructed file hashed **exactly** to the earlier full-reviewed
`67e7294d…` SHA. Therefore the only byte changes from that reviewed source are:

```maxscript
-- CURRENT lines 264–269
-- Standing verified rule: snapshotAsMesh is WORLD space already.
-- Never multiply its vertices by objectTransform a second time.
in coordsys world (tmpMesh = snapshotAsMesh n)
evaluatedVerts = getNumVerts tmpMesh; evaluatedCount = getNumFaces tmpMesh
if evaluatedCount > 256 or evaluatedVerts > 256 do throw "Evaluated capture exceeds 256 triangles/vertices; refusing, never truncating"
local vertices = in coordsys world (for i = 1 to evaluatedVerts collect (getVert tmpMesh i))
```

No second `objectTransform` remains in the evaluated path. Old line references
after 268 shift **+1** in the revised file: success exact-mesh cleanup **294–295**,
catch cleanup **405–407**, output dispatch **368–369**, exclusive file open **382**,
stream close **393**, catch diagnostics before cleanup **403**. Entry checks
**185–208** and base-local transform **212–213** are unchanged. The repeat
comment/string-stripped structural check passed with only `snapshotAsMesh` and
exact `delete tmpMesh` operands at revised lines **294/407**; forbidden broad-write
tokens remain absent. These are static safety checks, not live parse or timing.

### Main's executed evidence and what it does not prove

Read the actual separate evidence file cited above, not only the follow-up message.
Its raw wire has `ok=true`, empty warnings, `error=null`, **1.54 ms**, and:

```text
P3_SNAPSHOT_SPACE|meshMin=[95,190,300]|meshMax=[105,210,330]|nodeMin=[95,190,300]|nodeMax=[105,210,330]|worldMatch=true|after=0
```

This translated native Box control positively confirms raw `snapshotAsMesh`
vertices equal world bounds without multiplying by the transform, and main
recorded exact mesh/node cleanup with final census zero. **This is main-executed
evidence, not reviewer execution and not a run of `measure.ms`.** It resolves the
coordinate convention; it does not establish `.NET G17` overload binding, helper
function parse/scoping, whole measurement JSON, Shell property reads, evidence
file I/O or the revised script's own cleanup path.

Main can now run the small actual measurement script against an admitted one-quad
reference. For `#grid`, zero modifiers are required and evaluated TriMesh branch
is not exercised; for `#final`, exactly one small known Shell is required and the
temporary TriMesh path is exercised. Use the translated control for actual
evaluated coordinate/bounds checks; the independent expected bounds in the
historical review remain valid **correct-output expectations** for that proposed
one-quad geometry. Do not treat the erroneous column as a current prediction.
Inspect same-call precision/escape controls and every JSON issue/error before
proceeding to F01. No hard runtime deadline claim was added by this revision.

### Added `calibrate_snapshot.ms`: secondary safety check

Read all 95 lines. This optional file is also read-only with respect to scene
nodes: exact target input at **50–55**, four-vertex/one-quad/no-modifier admission,
nonidentity transform requirement **58–59**, census <=64 at **60–61**, base-local
once-transformed independent channel **62–64**, world snapshot and raw world reads
**65–68**, exactly 4V/2T refusal **66**, exact mesh-reference deletion **75**, catch
retry **91**. No scene creation/conversion/Shell modification, evidence file
writer, name/prefix lookup/deletion or `formattedPrint` call. All output is returned
JSON. It returns separate raw channels rather than internally asserting geometry
equality; main must compare actual vertices/bounds and retain raw wire. The error
path formats a diagnostic before cleanup (**89**) just like `measure.ms`; ordinary
API behavior is verified, but strict exception-first cleanup is not claimed.
Array serializer has no general recursive budget, but its input channels are
constrained fixed small arrays from the admitted one-quad target; do not broaden
its use to arbitrary arrays/scenes. No live run of this new file is claimed here.

### Preserved qualifications

All earlier ownership/resource/I/O qualifications still apply: exact temp-only
deletion is structurally correct but actual release is checked by the live run;
exclusive output uses caller path authority, not an evidence-root sandbox; set
output undefined initially; no scene-wide bitwise immutability or arbitrary
callback/time guarantee; no polygon/grid invention; CAPTURED_NOT_ACCEPTED remains
capture only. **Final answer to the requested immediate gate: GO, narrowly, for
main's tiny actual fileIn calibration on current `c8f93cca…` bytes.**
