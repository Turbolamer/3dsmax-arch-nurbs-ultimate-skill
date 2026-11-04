# Independent P3 measurement, prepared 2026-11-02e

**Prepared, not live-run or Max-parser-verified.** Only main may inspect/fileIn this
file. It imports no generator/runtime methods, consumes no predicted arrays and
does not modify a scene node, selection, controller, stack, units or document.
It allocates one temporary in-memory TriMesh and deletes it in success/catch.
Local functions live in the `fileIn` parenthesized scope, not bridge top-level `fn`.

## Entrypoint

Main supplies an already identity-proven **exact object reference**:

```maxscript
P3MeasurementTarget = <exact node reference proved by main>
P3MeasurementOutput = @"D:\Rhino\3dsmax-arch-nurbs-ultimate-skill\Audit\<NEW exact evidence filename>.json"
P3MeasurementStage = #final
fileIn @"D:\Rhino\3dsmax-arch-nurbs-ultimate-skill\Audit\phase16-p3-measurement-2026-11-02e\measure.ms"
```

The angle-bracket values above are documentation slots, not executable code.
No name/prefix lookup is present. Target must be valid, present in the bounded
census, base `Editable_Poly`, exactly one `Shell`. Optional `#grid` mode requires
zero modifiers, captures the *actual* undeleted grid, and does not build one.
The final script cannot recover historical predeletion grid evidence. Do not
disable Shell/delete faces or execute a predicted grid merely to fill this gap.
Only an actual earlier permitted construction stage can provide that evidence.

Optional output `undefined` returns full JSON; otherwise exclusively creates the
single exact filename via .NET `FileMode.CreateNew`/`FileShare.None`, writes UTF-8
without BOM, flushes and SHA-256-hashes the actual file stream. It never creates
directories, overwrites or deletes an evidence file. Existing output -> INCOMPLETE.
Partial I/O failure may leave **that exact new file**: envelope reports
`output_created=true`; preserve it as failed evidence, choose another fresh path.
Output path must be drive-qualified absolute; forward/backslashes are accepted
and normalized by `System.IO.Path.GetFullPath`. No UNC/relative output.

Success returns only `{status,path,sha256,bytes,base_active_counts,
evaluated_vertices,evaluated_triangles,scene_count,issue_count,elapsed_ms}`.
This is **CAPTURED_NOT_ACCEPTED**, never a geometry/replay acceptance verdict.
Read both the bridge error/marker and this envelope; transport success alone is
not runtime success. Errors return INCOMPLETE with cleanup and output status.

## Actual captured data

- Exact target node handle, anim handle, base anim handle, class and objectTransform;
  per-census same names, geometry overlap candidates and same-call census stability.
- Full base local/world vertices and active ordered face IDs/index arrays; actual
  edge IDs/endpoints/incident faces, raw/dead/nondead/face-referenced counts; no dead
  index renumbering. `active_counts` is referenced V, face-used E, nondead F.
- `getOpenEdges` API result separately from independently classified one-face
  boundary edges; ordered closed boundary vertex cycles and active Euler chi.
- API local normal/area separately from world-coordinate double-arithmetic
  triangulated polygon area and oriented normal. Base local coordinates apply the
  node's actual `objectTransform` exactly once. `snapshotAsMesh` vertices are
  already world-space: read `in coordsys world` with **no second transform**.
- Shell identity, enabled states, actual inner/outer/segments and enumerated
  properties (unsupported values/read failures explicitly INCOMPLETE).
- Final `snapshotAsMesh` actual vertices and ordered triangle face indexes in
  world space, normals/area, signed tetrahedral volume relative to actual first
  vertex (double scalar arithmetic), mesh bounds. **No scene snapshot, conversion,
  collapseStack or invented evaluated quads**. Evaluated polygon count is null /
  INCOMPLETE: no independently verified dedicated non-mutating polygon method.
- Bounded whole-scene census with classes, base identities, transform, hidden,
  renderable, visibility, modifier count, measured world bbox for each object.
  Overlap candidate list is conservative **bbox only**, not geometric aperture
  clearance. A target-only standalone scene proves no other scene host can occlude;
  any additional object needs independent review, not an implicit clearance PASS.
- Actual scene units pair and `units.decodeValue "1cm"` conversion. No unit setting.

Numerical serialization uses .NET invariant `G17`, with same-call positive double,
negative and escaped-string controls; no `formattedPrint`. Failure refuses capture.
Ceilings refuse, never silently cap: 64 scene nodes, 64 base vertices, 128 base
edges, 32 base polygons, 256 evaluated vertices/triangles, 128 modifier properties,
2 MiB file. No new MAX scene nodes; no evaluations of other objects to mesh.

**Time:** expected below 2 seconds only for admitted small F01/target-only scene;
that is an unmeasured estimate, not a guarantee. Main must inspect timing from its
first permitted capture before reuse. Expensive unrelated geometry/bbox evaluation
can exceed it despite count bounds. No live tool was called by this author.

## Oracle adapter

`adapter.py:oracle_capture(raw, evidence, grid_raw=None)` uses stdlib only and no
I/O. It scales the actual positions to cm using measured `scene_units_per_cm`,
retains one-based face/triangle indexes and leaves missing arrays absent. `evidence`
is a coordinator-authored binding record, with actual captured artifact SHA,
capture ID, project/run and verified source hashes; not copied from predictions.
The adapter does not authenticate history/handles/source bindings by itself.

The oracle's separate generic `adapt_capture` also works on raw stage arrays if
main explicitly supplies `cm_per_scene_unit=1/raw['units']['scene_units_per_cm']`
and `index_base=1`, but its evidence must likewise be supplied independently.
As read during authoring, `Audit/phase16_p3_oracle.py` additionally requires
evaluated `faces` for its polygon checks: this capture deliberately has only
measured triangles. Those polygon checks must remain **INCOMPLETE**, or the oracle
owner must implement a separately reviewed triangle-only acceptance branch. Never
derive/insert evaluated quads from the generator or treat two triangles as a
measured polygon count. Missing grid likewise remains INCOMPLETE.

Offline checks may validate lexical delimiters and adapter fault discrimination;
they cannot prove MAXScript parse/API/coordinate semantics, speed or geometry.
Historical P1 facts were read from `Audit/EVIDENCE_2026-10-27.md` E-11..E-16;
current measured bytes are not inferred from those historical expected counts.

## Nonidentity snapshot-coordinate calibration (added after authoring correction)

Main flagged the original snapshot read multiplying by `n.objectTransform`.
Installed `C:/Users/Turbolamer/.agents/skills/3dsmax-arch-nurbs-ultimate/SKILL.md:440`
explicitly states world-space TriMesh / no second transform. The original line and
this README's local-space assumption were wrong and are corrected in owned files;
no historical evidence is changed and no new live measurement is claimed.

`calibrate_snapshot.ms` is a separate **read-only** fileIn entrypoint. Main supplies
`P3MeasurementTarget` exact reference to its own zero-modifier Editable_Poly with
exactly one quad/four vertices and a nonidentity transform. It creates no node,
adds no Shell and performs no conversion. It captures two independent coordinate
channels: base local vertices × actual objectTransform **once**, and raw
`snapshotAsMesh` vertices read **in coordsys world without multiplication**. Also
captures actual triangle indexes and `nodeGetBoundingBox ... (matrix3 1)`.
Temporary TriMesh is deleted in the same success/catch. The small one-quad JSON
is returned directly for main to retain as wire evidence, not written to disk.

Main can create its own asymmetric XZ quad with local vertices
`[2,0,3], [13,0,3], [13,0,10], [2,0,10]` and run separately:

1. Translation-only `objectTransform` rows
   `[[1,0,0],[0,1,0],[0,0,1],[37,-19,11]]`.
2. Rotation-only +90° around Z, rows
   `[[0,1,0],[-1,0,0],[0,0,1],[0,0,0]]`.
3. Optional combined translation/rotation using rotation rows and `[37,-19,11]`.

These are suggested calibration inputs, not measured scene facts. Main owns the
creation/cleanup and may choose other nondegenerate rigid placements. Identity
F01 cannot test this fault; the calibrator refuses identity. No expected array is
read from any generator or supplied to the MAXScript capture.

`calibration.py:assess_snapshot_calibration(raw, epsilon_scene_units=1e-4)` checks
raw scalar local coordinates × raw matrix against **both** observed channels and
the separate node bbox, with order-independent one-to-one vertex matching. It
requires rigid proper rotation (no scale/shear/mirror), explicit one-based index
arrays and a placement that actually discriminates a double transform. It neither
corrects bad snapshot coordinates nor trusts any reported PASS. Keep translation
and rotation captures separately; result motion flags show which were exercised.
It cannot authenticate supplied capture provenance or replace main's live test.

Offline synthetic translation/rotation/combined controls must PASS; intentionally
double-transformed snapshots must FAIL for each motion. Local-space snapshots,
incorrect independent base channel/bbox and identity/nonrigid inputs also fail or
refuse. These controls test the calibration adapter, not 3ds Max behavior.

## Stream writer calibration (unverified until main runs)

Main's geometry smoke got through the corrected parser and geometry, but failed
before file creation because `Encoding.GetBytes` was marshalled to a MAXScript
Array and `.Length` is invalid. This was an author interop defect, not geometry
or an absent .NET capability. Corrected writer does not call `GetBytes` at all:
`encoding.GetByteCount json` bounds size, then `StreamWriter(FileStream,
UTF8Encoding(false)).Write json`, writer flush, stream flush, compare actual
stream length, rewind, `SHA256.ComputeHash stream`, then close writer/stream.
Digest is checked as a 32-element marshalled Array and converted to lowercase hex
by a bounded **32-byte** nibble loop; no byte-array round-trip overload or per-file
byte loop exists. Hash/writer/stream cleanup is guarded on errors.

`calibrate_writer.ms` isolates this exact writer flow without geometry. Main sets
`P3MeasurementOutput` to a fresh exact owned filename and fileIns it. It writes
the fixed Unicode JSON `{"calibration":"AéЖ","line":"one\\ntwo"}` with no added
newline, returns `WRITTEN_NOT_VERIFIED` plus path/hash/count/text; main should
independently check actual file bytes equal returned text encoded UTF-8 with no
BOM and SHA-256. A second invocation with the same path must refuse before write,
with the first file bytes/hash unchanged. This minimal calibration has not been
run by its author. Main can instead retest the full module directly; do not call
the untested writer path a PASS before actual output exists.

### Subsequent main smoke / Integer64 envelope correction

Main's third full tiny-quad smoke created actual full capture
`Audit/_phase16-p3-measurement-smoke-capture-2026-11-02e.json`; measured base
active `[4,4,1]`, evaluated 8 vertices/12 triangles, one scene node, zero issues;
main reports exact-reference cleanup back to zero objects. This is a bounded
calibration of measurement, **not F01 produced-wall acceptance**.

The full file was emitted, but the compact envelope was invalid JSON because
MAXScript `Integer64 as string` produced `3516L`. Corrected both the general
`jvalue Integer64` branch and file-length envelope paths: integer-only serializer
strips exactly a terminal L/l, validates decimal digits/sign/leading-zero rules,
and never converts exact large integers to double. Same-call positive/negative
Integer64 controls were added. `calibrate_writer.ms` uses the same approach.
The corrected envelope still needs main's actual retest; no retroactive envelope
PASS is claimed. Existing evidence remains untouched.
