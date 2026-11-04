# P3 independent measurement authoring — 2026-11-02e

Ownership kept to this NEW report and NEW `Audit/phase16-p3-measurement-2026-11-02e/`.
Read checkpoint/plan/AGENTS, main brief, decided P3.1 contract and P1 E-11..E-16.
No live Max call, install, git action or edit outside ownership was performed.

Entrypoint: `Audit/phase16-p3-measurement-2026-11-02e/measure.ms`; main supplies
`P3MeasurementTarget` exact reference and optional `P3MeasurementOutput` absolute
new evidence filename, then `fileIn`. `#final` requires Editable_Poly + one Shell;
optional `P3MeasurementStage=#grid` measures an actual earlier zero-modifier grid.
No generator or emitter data dependency exists. Full measured JSON is exclusively
created without overwrite, stream-hashed; small returned envelope contains identity
path/hash/count status. No output -> full JSON string for debugging.

Captures complete actual base vertices/faces/edges/dead slots, active V/E/F,
API opens and reconstructed boundary cycles/chi, world area/normals; Shell state;
evaluated world vertices/triangles, double signed volume/bounds; bounded scene
census and potential bbox-overlap occluders. In-memory TriMesh is deleted in the
same success/catch; no scene snapshot or conversion is performed. Actual identities
are captured, never inferred by prefix/name selection. No polygon count is invented.

**Unverified limits:** not Max-parser/live/API-verified; <2 s F01 capture is only an
estimate. .NET invariant serialization controls run before capture; main must
inspect actual runtime errors and resulting file. Grid after deletion is not
recoverable; optional earlier-stage capture is the only supported grid source.
Evaluated polygon count stays INCOMPLETE; full measured triangle mesh is supplied.
Overlap candidates are not a geometric occlusion gate. Target-only scene census
is sufficient to rule out another scene host, not arbitrary internal void errors.

`adapter.py` preserves measured arrays and explicitly converts scene units to cm;
it neither imports the generator nor manufactures missing grid/evaluated quads.
Coordinator supplies independent artifact/source binding. As currently read, oracle
polygon-stage branch requires evaluated `faces`; absent arrays must stay INCOMPLETE
unless oracle owner separately supports the measured-triangle-only contract.
See sibling README for schema/precision/cleanup/runtime/adapter details.

Offline author checks are recorded below; none are live geometry acceptance.

Executed: `python -B Audit/phase16-p3-measurement-2026-11-02e/test_offline.py`:
**7/7 OK**, adapter positive/negative joins, scale/index/nonfinite/missing-evidence
refusal, no invented grid/quads, input immutability; MAXScript delimiter-only
smoke and forbidden scene-operation text scan. These are not a MAXScript parser,
API/geometry/runtime proof. Synthetic test arrays are confined to this new test
module and are explicitly `synthetic_test`, never produced-output evidence.

## Coordinator correction — snapshot world-space, 2026-11-03

Main/source review flagged original `measure.ms` snapshot vertex multiplication by
`n.objectTransform`. Directly read installed
`C:/Users/Turbolamer/.agents/skills/3dsmax-arch-nurbs-ultimate/SKILL.md:440`:
**world-space TriMesh; read `in coordsys world`, no second objectTransform**.
Original code/README assumption was wrong. Corrected only owned measurement code
and README: snapshot reads now explicitly world-space with no multiplication;
base local vertices still transform exactly once. No historical evidence edited.

Added `calibrate_snapshot.ms` (read-only one-quad capture, main-supplied exact
translated/rotated node; no node creation/conversion/Shell) plus independent
`calibration.py`. Adapter recomputes base-local×matrix once and checks raw snapshot,
base-world channel and node bbox; refuses identity/nonrigid placement and explicitly
discriminates the original double-transform fault. Main must run actual calibration;
author performed no live Max call. TriMesh cleanup occurs in the same call.

Re-executed owned offline suite after correction: **13/13 OK** (same command).
Translation-only, rotation-only, combined positive controls pass; intentionally
double-transformed observations fail all three; identity/nonrigid/mirror refuse;
wrong local/base/bbox channels fail. cm adapter also preserves supplied nonidentity
world observations without applying the recorded matrix. These are synthetic
adapter/static regression tests only, not live calibration or acceptance.

## Actual calibration independently assessed, 2026-11-03

Executed `python -B Audit/phase16-p3-measurement-2026-11-02e/verify_actual_calibration.py`
on main's retained `Audit/_phase16-p3-measurement-calibration-2026-11-02e.json`
**`['capture']` actual observations**. Verdict **PASS**, all five checks true,
translation and rotation both exercised; measured world vertices/bbox agree with
`[100,200,300]` through `[100,210,310]` at epsilon `1e-4` scene units.
Deliberately multiplying the ACTUAL snapshot coordinates by its ACTUAL transform
again returns **FAIL**: `SNAPSHOT_ALREADY_WORLD=false` and
`SNAPSHOT_NOT_DOUBLE_TRANSFORMED=false`, independent base/bbox gates remain true.
This negative is an explicit offline data mutation, not another live test.

Exclusive new verdict file: sibling
`actual-calibration-verdict-2026-11-02e.json`; before/after main-source SHA both
`08bbbecabb573948d98a285b4b19a237a9dbd1480e182947253e43340c7af4ca`.
Main reports clean live cleanup (`objects_after=0`), no bridge errors/warnings,
elapsed 13.385 ms. This does not accept F01 or remaining measurement API calls.

## Main measurement parse smoke failure and correction, 2026-11-03

Main reports request `9b7fab2311f349898152632abf1ee786`, elapsed 36.973 ms,
RT 36.948 ms: bridge `ok=true/error=null/warnings=[]` but result is explicit
`P3_MEASUREMENT_SMOKE|EXCEPTION=-- Syntax error: at by, expected name`
at `local by =`, `objectsAfter=0`. No measurement file was captured.
This is a code parse defect, **not API absence**. Renamed both occurrences of
reserved `by` and corresponding cross-product references: polygon helper uses
`edgeBX/edgeBY/edgeBZ`, volume helper `vertexBX/vertexBY/vertexBZ`. Historical
failure evidence is preserved; only owned source/tests/report changed.
Added a comment/string-aware lexical guard against known reserved identifiers
in declaration/assignment slots, with by/on/off/to/from/at fault controls and a
legitimate `for i=1 to 4 by 1 do` control. Not a MAXScript parser; main must retest.
Re-executed owned offline suite after this correction: **15/15 OK**, including
reserved-name positive/negative controls. No live Max call by this author.

## Main geometry smoke reached writer; byte-array interop correction, 2026-11-03

Main reports request `c63c8c0dc6e94c31ad3df7f9c75393b1`, 16.585 ms: corrected
measurement parsed/reached geometry, returned INCOMPLETE `Unknown property:length
in #(123,34,115,...bytes)`, `output_created=false`, `cleanup_issues=[]`,
`objectsAfter=0`. No file was captured; exact output path remains free according
to main. `Encoding.GetBytes` default interop returns MAXScript Array, not byte[].
No new geometry/API success beyond that reported smoke is inferred.

Corrected only owned writer: GetByteCount scalar ceiling; exclusive CreateNew
FileStream + UTF8Encoding(false) StreamWriter; write/flush both; length equality;
rewind then SHA256(stream); close writer only AFTER hashing. Digest array uses
`.count` and a bounded 32-byte hex nibble loop, no `.Length`/byte[] re-marshalling.
Guarded hash/writer/stream cleanup. Added `calibrate_writer.ms` for main's optional
minimal Unicode/noBOM/exclusive-write/hash/second-call-nooverwrite calibration.
Writer APIs remain **UNVERIFIED** until main executes; no live call by author.
Owned offline suite after this correction: **16/16 OK**. The new static writer
regression asserts no GetBytes/bytes.Length/byte[] overload path and ordering
write → writer flush → file flush → rewind → hash → writer close, across both
full measurement and isolated calibrator. Static ordering is not interop proof.

## Third main smoke captured full file; Integer64 envelope defect, 2026-11-03

Main request `1d6e2a20552c47a29ee49cba9e5493e8`, tool 15.252 ms, capture 6 ms,
created `Audit/_phase16-p3-measurement-smoke-capture-2026-11-02e.json`, expected
SHA `81b69fc1de39a9fcd410b9158cac6d317030d2f2bcd10bde4cd32afdf12c364a`,
3516 bytes. Main reports base-active `[4,4,1]`, evaluated V=8/triangles=12,
scene=1/issues=0, exact-reference cleanup `objectsAfter=0`. This is bounded
measurement calibration only, **not F01 produced output or P3.1 acceptance**.
The earlier parse failure and prefile byte-array failure remain recorded above.

Compact envelope was **INVALID JSON**: its byte-length Integer64 was emitted
`3516L` by `as string`. Corrected all owned general Integer64 JSON serialization
and both writer byte-count envelopes using exact decimal suffix removal, with
sign/digit/leading-zero validation; no integer-to-double precision loss. Added
same-call +/-Integer64 controls and static/JSON regression including signed-64
extrema. Corrected envelope requires main's actual retest, not presumed PASS.

Executed owned offline suite: **17/17 OK**. Executed
`python -B Audit/phase16-p3-measurement-2026-11-02e/verify_smoke_and_freeze.py`:
independently parsed main's actual full capture, verified exact 3516 bytes/hash and
actual base/evaluated/census/issue counts above; source SHA before/after identical.
New frozen source manifest + bounded verdict:
`phase16-p3-measurement-2026-11-02e/final-source-hashes-and-smoke-2026-11-02e.json`.
Final `measure.ms` SHA-256:
`eee6d56ecb0d7c270494d55ba90f51ccb1032eb261defb7a2bf11baa8772d8f9`.
Final `calibrate_writer.ms` SHA-256:
`19ac6c76adc28a7663561c9d391db0a42876ba145ce2d3c88b8adf715e8b05cc`.
Runtime Integer64-envelope fix remains unverified; this report-only append does
not change the frozen source bytes. No live Max call by author.

## Frozen readiness / host catch-rule review, 2026-11-03

Main reports separate runtime Main02arm compile error: only argumentless throws
are permitted syntactically in catch expressions. Runtime owner handles its own
source; no measurement change is needed for that defect. Narrow comment/string-
aware catch-body scan found **no explicit throw** in all owned catch bodies:
`measure.ms` 7, `calibrate_snapshot.ms` 2, `calibrate_writer.ms` 4. This lexical
finding is not a guarantee that helper/property/.NET calls cannot throw.

All nine finalized owned source hashes still match the frozen manifest exactly;
no full-suite rerun, Max call or source modification occurred in this review.
Independent retained full-capture reread confirms area `10000`, signed volume
`100000.00000000001`, exact original SHA. Main's Integer64-envelope retest remains
**PENDING**. Prior parse / GetBytes marshalled-array / invalid-envelope defects
remain recorded, not erased. Bounded tiny-quad measurement calibration is not F01.
New readiness record: sibling `ready-status-2026-11-02e.json`.

## Actual corrected writer success / exact-path refusal, 2026-11-03

Main executed corrected `calibrate_writer.ms`: request
`8fe959bf429d470e948306f375c724e4`, elapsed 3.925 ms, parsed actual JSON envelope
`WRITTEN_NOT_VERIFIED`, 41 bytes/expected 41, SHA
`51eca5564e30fcc80979e30679fd1f05410d08ae59b76508183bf6b2a9b06b0a`.
File: `Audit/_phase16-p3-writer-calibration-2026-11-02e.json`. Main independently
verified bytes/hash/JSON and UTF-8 Unicode/escaped-newline content. This provides
actual bounded runtime evidence for the corrected writer Integer64 envelope;
it is not a full-measurement rerun or F01 output acceptance.

Same EXACT path repeat request `9b3b0a8cb7684b9ebeea528f25ab2fca`, 2.1 ms:
**tool ok=false, ToolError/.NET runtime exception file already exists**. Existing
41 bytes remain identical by main's independent reread. This is targeted
no-overwrite refusal, **not** a successful INCOMPLETE-JSON error envelope: the
catch wrapper did not normalize this exception. That limitation remains explicit.
Main alone may inspect/clear its own possibly retained `P3MeasurementOutput`.

Owned normalized transcription:
`phase16-p3-measurement-2026-11-02e/writer-calibration-main-transcription-2026-11-02e.json`.
Existing readiness/freeze records are preserved as prior-time status, not rewritten;
this section supersedes only pending isolated-writer-envelope calibration status.
No code change, full-suite rerun or Max call by this author; sources stay frozen.
Author independently reread the actual writer file offline: exact 41 bytes/SHA,
valid expected JSON, UTF-8 without BOM, actual parsed newline; source bytes stayed
identical. All nine frozen source hashes still match. New verification record:
`phase16-p3-measurement-2026-11-02e/writer-calibration-independent-read-2026-11-02e.json`.
