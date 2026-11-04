# P3.1 same-attempt grid observer — design for review, not implementation

**Status: DESIGN ONLY.** No observer, instrumented emitter, callback mechanism,
grid capture or live F01 result has been executed or fabricated here. This is not
permission to run Max and does not alter the decided contract. Only main may
perform live work. P3.1 remains **NOT ACCEPTED**. The observer is not a solution
to the existing runtime ownership, baseline, evaluation-safety, or replay gates.

## 1. The actual evidence gap

The contract (`Audit/_phase16-p3-contract-2026-11-02e.md`, especially §§Geometry,
Scene ownership and replay, and Acceptance boundaries) calls for the actual
emitted F01, returned vertex/face IDs and independent geometry checks. The
retained Main03 `published/wall_surface.ms` builds the entire grid, updates it,
prints IDs, deletes opening faces and adds Shell inside **one synchronous fileIn**.
The source in `scripts/wall_surface_runtime.py` has the equivalent
`grid-faces` → `opening-delete-once` ordering. Runtime hardening is being edited
concurrently; neither an intermediate source read nor this note is a frozen
verdict on its later bytes.

The existing independent `measure.ms` has a zero-modifier `#grid` mode, and
reads real `polyop.getVert`/`polyop.getFaceVerts`; however, its usual separately
invoked fileIn cannot reach the transient grid of a completed single fileIn.
The emitter's own `expectedPoints`, `cellSlots`, ID prints and per-face readbacks
are not an independent capture. Dead slots, final base arrays, rebuilding the
same recipe, a temporary fixture, P1's historical grid, and Main03's cleaned-up
failed attempt do not recover that grid. See
`Audit/phase16-p3-measurement-next-2026-11-03/README.md` §§1, 75–80.

Main03's failure/POISONED lease and later process/key discontinuity remain
historical evidence as recorded in `CHECKPOINT.md`; neither a surviving current
witness nor an earlier-grid capture can be inferred. A future F01 is a **new
attempt**. Its input may be the F01 analytical fixture, but a real capture must be
from the actual node built by the actual newly emitted artifact, not an invented
or synthetic output. Test-only arrays must be explicitly `synthetic_test`.

## 2. Recommendation: one explicit, synchronous observer seam

Subject to contract approval and calibrated support, add **one required seam to
the emitter itself for the instrumented F01 capture profile**, after the last grid-face creation/readback and `update`,
but before *any* `polyop.deleteFaces` or Shell operation. The seam invokes a
separately authored observer once, with the runtime's **exact current `node`
reference**. The observer independently obtains `node.baseObject`, reads the
actual poly vertices and ordered face loops, and returns only a neutral scalar
acknowledgement. It receives **no** expected positions, cells, cuts, face IDs,
predictions, arrays to echo or permission to change the node. Its only permitted
external side effect is the separately bounded, no-replace telemetry write in §6.

This is a *proposed call contract*, not an assertion about MAXScript closure,
callback, debugger, global or fileIn scope support. A future implementation
must establish how a reviewed callable and its exact reference pass across that
scope with main-only, positive/negative controls. If it cannot, **stop**: no
seam, no same-attempt independent grid capture, and no grid-based PASS. A
post-fileIn reader is not a substitute. No registration or listener is presumed
to intercept `polyop.deleteFaces` safely.

| Approach | Consequence |
|---|---|
| Inline capture in the emitter | Adds no callable identity handoff, but the emitter is also the measurer: auditing cannot assume self-readback is independent of its construction arrays. Its entire modified script and capture logic become trusted. |
| Explicit seam + separate observer, **recommended candidate** | Adds the call seam, callback/reference continuity, writer and their side effects to the trusted base. Independent code queries the supplied actual node, without being fed construction geometry; this is code independence, not independent process attestation. |
| External callback, listener, debugger or breakpoint on an unchanged script | Could in principle preserve the original script bytes, but safe interception, ordering, object identity, lifetime and noninterference are not established. No such capability is claimed here. |
| Separate post-fileIn grid reader or rebuilt fixture | Cannot see the earlier transient stage of the specific attempt; not acceptable as that stage's evidence. |

`measure.ms #grid` is a useful source of reader/serialization techniques, not a
drop-in callback: it expects global inputs and performs additional scene reads.
Making it callable, changing its globals or wrapping it must itself be reviewed,
hash-bound and calibrated. The above options have different trust boundaries;
none becomes independent merely because it lives in a different file.

Conceptual, deliberately non-executable pseudocode:

```text
before creation: validate capture-required mode, approved observer reference,
  independent lease witness/context, expected units, and new evidence destination;
  if any required item is missing or unprovable: refuse before scene mutation
...
build real vertices and faces with the emitted runtime's ordinary checked IDs
update real node
assert bounded runtime readbacks already required by the emitter
assert current observer reference == main's independently retained approved reference
capture_target = node                           # exact current live reference
assert attempt-owned node and base continuity
observer_before = bounded detached preservation snapshot at THIS instant
ack = call_approved_observer(capture_target)   # exactly once; synchronous
assert ack is exactly the designated neutral success scalar; otherwise fail
assert same callback reference and same exact capture_target and base references
assert preservation snapshot equals a fresh AFTER snapshot; otherwise fail
assert exactly one valid verified receipt from this invocation, no unresolved issue
record post-observer / pre-delete transition in the trusted attempt transcript
only now proceed to ordinary opening deletion and Shell work
```

The snapshot comparison covers the target's live/dead vertices, positions and
ordered loops, base and node references/handles, transform/object transform,
modifier list and identities, exact bounded node census, selection references,
time, units, file identity, save-required/dirty flag, and relevant pre-existing
state accessible under the separately approved runtime-preservation contract.
The comparison is between the instants **immediately before and after the
observer**, not between an initially clean empty scene and a builder that has
legitimately created a wall and made the scene dirty. Neither observer nor
harness restores or clears a changed dirty flag, selection, time or history to
make a test pass. Include other required scene/base metadata as its safe readers
become calibrated; unreadable required state is **INCOMPLETE**, not equal.
This bounded comparison cannot prove that no transient edit-and-revert or
unobserved plugin side effect occurred. Queries, file operations and callbacks
may allocate, evaluate or invoke plugin code: read-only *intent* is not proof.

The post-observer state guard is distinct from the capture: it may re-read actual
state but must never replace the observer's recorded arrays with emitter arrays.
It must be independently reviewed for side effects. If exact references or
callbacks cannot be compared safely, or pre-deletion ordering cannot be proved,
the observer protocol remains unsupported.

The observer's approved, independently retained invocation context may contain
the attempt ID, exact binding record and a single-use receipt channel; these are
not geometry and must not contain expected points, loops or cut IDs. The observer
receives the node as its only geometry input. The receipt channel returns the
write/readback outcome to the invoking seam without changing the neutral scalar
return or mutating the wall; its actual safe representation is unproven. It must
be a bounded exact-instance, one-shot channel, not a lookup of a copyable global
by name. If such a channel cannot be implemented and independently witnessed,
the design refuses rather than assuming one. The seam runs **only** in the
initial creation branch, not on no-op/replay; a replay must not invoke the
observer or create, rewrite or reuse grid telemetry.

The externally held context must also retain the exact node and base references
as actually received at the seam, and compare them with the original creation
and final-capture references within one calibrated, uninterrupted harness
lifetime. The reference is not independently obtained merely by reading it
back later from the runtime's own registry. Interpreter-state changes needed
to hold this context are not zero side effects; preserve pre-existing globals
and report any uncertain teardown, retaining owned diagnostics rather than
clearing a witness. If callback scope cannot deliver this witness without
unapproved global mutation, keep the evidence INCOMPLETE.

## 3. Observer contract and source independence

`observe(existing_node) -> NEUTRAL_OK` is a conceptual signature. Any other
return, wrong type, exception, truncated receipt, missing/duplicate invocation,
failed write/readback, changed or unknown identity/state, or unobservable result
must prevent normal entry into opening deletion. No catch may turn an observer
failure into a success. Geometry cleanup, if any, is the separately reviewed
runtime failure handler's responsibility (§7), not the observer's.
The concrete neutral value and exact type must be fixed by the protocol and
tested; no arbitrary truthy value, free-form string or implicit return is accepted.

Admission and capture, in order:

1. Require the exact received reference to be a valid existing node and the one
   current attempt-owned, independently witnessed live node. Check calibrated
   exact-reference equality, a node/anim-handle roundtrip as corroboration, exact
   base reference and roundtrip, target-only current census, `Editable_Poly` base,
   zero modifiers, and current expected type **and** scale **and** conversion
   factor. A name, tag, handle, equal mesh, count, root/PID or nonce alone never
   proves identity. Reference identity lives in the uninterrupted controlled
   harness; serialized handles are corroborating observations only.
2. Read actual vertex/edge/face counts and dead sets before allocating bounded
   arrays. Admit only positive, within F01 caps (at most **24** vertices,
   **15** faces; independently enforce the applicable declared budget; use a
   modest explicit edge/serialization cap). Refuse, never truncate. Count/cap
   readbacks are observations, not assumed F01 values. No expected grid topology
   or station values are arguments to this reader.
3. For a minimal lossless v1, require every vertex and face slot in `1..nv` and
   `1..nf` to be active, with no dead vertex/face slot; if this cannot be read or
   differs, refuse rather than silently renumber. Independently read all vertex
   coordinates using `polyop.getVert` on the exact actual base and all ordered
   loops using `polyop.getFaceVerts` for actual active face IDs. Reject unreadable,
   nonfinite, malformed, repeated/out-of-range face indices and non-quads; retain
   original order and the actual IDs. Read edge count/dead-edge observations as
   supplemental evidence, not a stand-in for loop arrays. The oracle derives
   topology from the arrays. Do not use the emitter's `vertexIds`, `faceIds`,
   `cellSlots`, expected stations or `cutIds` as the capture data.
4. Preserve the measured local coordinate array and detached actual transform;
   produce world coordinates by the existing measurement convention of applying
   the observed `objectTransform` **once** to base-local points. Read/record the
   actual measured unit triple; do not set units or infer type from the factor.
   Translation/rotation calibration is still required on the observer's actual
   reader and serialization path; the `snapshotAsMesh` world-space rule applies
   to evaluated TriMesh, **not** a second transform on these world arrays.
5. Write the bounded full observation and issue a receipt only after the exact
   stream's successful flush, hash, close and verified readback, as described in
   §6. No `snapshotAsMesh`, conversion, new scene node, geometry write, selection
   or time setter, modifier operation, update, reset, save, undo, dirty-flag
   setter, material/layer operation or recursive scene walk is needed. Callback
   invocation and telemetry are trusted additional execution, not invisible.

No unreviewed replacement of `P3MeasurementTarget` or other user global is
allowed. An existing global-slot approach would need explicit absent/occupied
guards, exact-value restoration/removal only for a slot owned by this attempt,
and separate tests of lifecycle and failure; absent those proofs it is not an
implementation option. Never clear a pre-existing symbol or lease.

## 4. Identity and hash binding without cycles

An independently audited in-process hook is still trusted code. The harness,
published emitted script, seam, observer, actual callback object, writer and
runtime API are part of the trusted computing base. Hashes identify bytes; they
do not prove that they ran, that a node was live, or that Max/plugins were benign.
The controlled-local, sequential, single-writer threat model excludes malicious
code substituting the observer or filesystem during a call; it makes no general
race-proof or forensic-attestation claim.

Proposed no-cycle binding chain, with **actual byte hashes**, not prediction
hashes:

1. Freeze/review all input/source/authority/contract and generator bytes, the
   separately authored observer `O`, and the seam/protocol version. Record
   `H(O) = SHA256(exact observer file bytes)`. Any future package design that
   embeds `H(O)` in the generated script must use this pre-existing digest;
   the observer must not embed the future script or manifest digest in its own
   source. Review observers loaded from any dependency closure, not a top-level
   stub alone.
2. Generate the **actual** new `wall_surface.ms` `S` with the one seam and a
   future contract-approved binding of protocol version and `H(O)`. Publish it
   through the builder, not by hand-patching a published script or silently
   wrapping it after publication. Compute `H(S)` from its exact bytes. The
   generated `wall_surface.json` `M` must bind `H(S)` in its existing `script`
   record, input/generator/authority identities and expected unit pair. A
    reviewed versioned manifest extension may additionally pin `H(O)` and the
    seam; this changes the published contract and cannot be assumed allowed by
    the present schema. Alternatively main may explicitly approve keeping the
    manifest unchanged. In **either** option, create a separate frozen
    pre-attempt binding record `B` containing `H(M)`, `H(S)`, `H(O)`, the exact
    seam/protocol version, generator closure and artifact identity.
    `M.script.sha256 == H(S)` and every `B` field must be independently
    verified. **Neither option is implemented.**
3. The main-only wrapper pins and independently rechecks `B`, `M`, `S`, `O`,
   harness and their exact byte hashes immediately before invocation, with the
   reviewed held-read/controlled path policy. It must establish that the
   approved **callable instance actually invoked** came from the reviewed
   observer bytes, retaining its exact reference separately and checking it at
   the seam. A function's self-reported digest, a name or an equivalent-looking
   replacement is insufficient. If that relationship cannot be demonstrated,
   refuse. Hold/check handles only to the extent calibrated; reading a hash and
   later fileIn by path is not a universal immutable-file guarantee.
4. A fresh, unique **attempt ID** identifies this one attempt; it is not a secret
   or proof of a Max session. Bind it to main's independent original exact lease
   witness, detached nonce/identity/context, exact created node/base references,
   artifact identity and this particular callback instance. Keep those exact
   references alive across observer and final capture. Never reacquire the
   witness from the registry and call it independent; a registry value or
   serialized nonce cannot authenticate itself. Enforce exactly one invocation
   of the approved callback on that exact node before deletion, with transcript
   events and post-call checks. Reject reentry, substitution, extra invocation,
   stale attempt ID, missing original witness or process/scene discontinuity.
5. `C`, the actual raw grid capture, can carry `H(B)`, `H(M)`, `H(S)`, `H(O)`, attempt
   ID, runtime identity and observed target metadata supplied through the
   verified context; these are linkage claims, not the geometry. Main compares
   them with independently held `B` and the full actual wire transcript.
   Compute `H(C)` from the exact emitted file bytes **outside C**. Finally a
   separately created evidence record `E` binds `H(B)`, `H(M)`, `H(S)`, `H(O)`,
   `H(C)`, exact harness/wrapper hashes, raw bridge-wire hash, actual final
   capture hash (if one exists), witnessed comparisons and outcomes. Do not put
   `H(E)` in E. Never retrofit an old immutable manifest/evidence record.

The acyclic dependency is `O → S → M → B → C → E` (with inputs/generator/contract
feeding S and M). Freeze and verify the wrapper independently too. If its code
embeds `H(B)`, then B must **not** embed `H(wrapper)`; E binds both afterward.
Alternatively supply wrapper and B identities through a separately held,
reviewed out-of-band context. Never arrange mutual byte-hash dependencies. The
script must not contain its own SHA or the manifest SHA; the
manifest must not contain its own SHA or the future capture SHA. Hash separately
the original UTF-8 bytes as stored, not reserialized JSON, locale-dependent
strings or a digest echoed by the same unverified source. A further semantic JSON
hash, such as the oracle's `source_digest`, is a **different** binding and must
not be represented as the raw source-file hash.

Instrumenting the runtime changes the script and, normally, generator and
manifest identity: this is a **new emitted artifact**, not proof that Main03 or
an uninstrumented later artifact was observed. Claim “actual emitted F01” only
for the exact new builder-produced published script whose bytes main fileIns;
declare observer instrumentation and its trusted-code delta. A separately
post-edited script is a diagnostic fork, not the original published pair. If the
contract instead requires byte-identical observation of the old no-seam script,
only a separately reviewed, proven nonintrusive execution-control mechanism
could meet it; none is established here. Do not infer one from API naming.

## 5. Raw grid schema and oracle compatibility

The observer's future file must provide at least the existing raw shape consumed
by `Audit/phase16_p3_oracle.py:adapt_independent_measurement` and
`Audit/phase16-p3-measurement-2026-11-02e/adapter.py:oracle_capture`. The
following is a **shape specification, not captured data**; `<...>` are
non-executable descriptions, not fixture values:

```text
{
  schema_version: "p3-independent-measurement-1",
  status: "CAPTURED_NOT_ACCEPTED", stage: "grid",
  evidence_origin: "independent_read_only_scene_queries",
  length_unit: "scene_unit", index_base: 1,
  units: {system_type: <observed>, system_scale: <observed>,
          scene_units_per_cm: <observed>},
  target: {name: <observed>, anim_handle: <observed>, node_handle: <observed>,
           base_anim_handle: <observed>, base_class: <observed>,
           object_transform: <observed four rows>},
  grid: {coordinate_space: "world", index_base: 1,
         vertices: <actual world xyz array ordered by actual vertex ID 1..nv>,
         vertices_local: <actual base-local xyz array ordered 1..nv>,
         faces: <actual ordered polyop face loops ordered by actual face ID 1..nf>,
         face_ids: <actual active face IDs>,
         raw_counts: <actual [nv,ne,nf]>,
         dead_vertex_ids: <actual>, dead_edge_ids: <actual>, dead_face_ids: <actual>},
  issues: [],
  observation_binding: <versioned attempt/artifact/observer linkage claims>
}
```

The optional fields and exact writer spelling require review against the actual
final measurement format, in particular handle string representations and the
complete `units` dictionary: the adapters require **dictionary equality**
between grid and final captures, and exact equality of `target.anim_handle`,
`node_handle`, `base_anim_handle` and `object_transform`. Preserve the original
raw data and byte digest; metadata cannot substitute for a retained live ref.
Do not silently add, drop or renumber elements to obtain a topology match. If
the dense-ID requirement fails, leave v1 INCOMPLETE; a later sparse-ID adapter
would need a transparent, validated bijective mapping and preserved raw IDs.

For an independently audited deletion transition, retain actual grid face IDs,
the runtime's actual deletion-ID/event readback as a separate operational log,
and the final active/dead face IDs plus node/base refs. Independently map the
observed pre-delete loops to authority openings and compare with final active
loops. ID stability/compaction across deletion must be calibrated; if IDs are
reindexed, use only a separately verified unambiguous correspondence, otherwise
leave that transition INCOMPLETE. Runtime `cutIds` are a useful cross-check, not
the source of the observer's grid loops or the independent opening oracle.

After independent authentication, the existing adapter divides each captured
world coordinate by the *observed* `scene_units_per_cm` once and passes
`grid.vertices_cm`, `grid.faces`, `index_base=1` to the checker. The independent
physical authority and `oracle.predict(...)` must still be established separately
from the emitter and its predictions. Use
`oracle.check_independent_capture(predicted, actual_final_raw, evidence,
grid_raw=actual_grid_raw, expected_units=independently_locked_triple)` only after
the linkage gate; `evidence` supplies actual artifact hash and semantic source
hashes, project/run, capture ID and `length_unit="cm"`. The adapter's matching
strings are **not** an authentication mechanism.

**Source-level acceptance gap:** `adapt_independent_measurement` checks the grid
schema/status/stage, unit dictionary and four reported target values, but does
not check `grid_raw.issues`, `evidence_origin`, byte hashes, attempt ID, actual
callback identity or stage timing. `check_independent_capture` checks
`issues`/headers on the *final* raw capture, not on the separate grid. Therefore
a grid with an unresolved `issues` entry can still reach a `GRID_*` geometry
check. A future independent admission checker must explicitly reject it, or
the oracle owner must separately amend and test the wrapper; do not silently
claim the current wrapper enforces these requirements. No existing oracle code
is modified in this design.

On complete array input the existing `check_measurements` emits separate
`GRID_INTEGRITY`, `GRID_TOPOLOGY`, `GRID_COVERAGE`, `GRID_NORMALS` and applicable
`ACTUAL_MAX_GRID_POLYGONS` checks; a successful stage does **not** necessarily
emit a `GRID_CAPTURE=PASS` item (`GRID_CAPTURE` is emitted on an exception).
`_cycle_key` treats cyclic/reversed loops as equal for coverage, while
`GRID_NORMALS` separately tests orientation; both matter. Even an authenticated
passing grid does **not** resolve missing evaluated native polygon loops,
physical-direction verification, stack/census/ownership, three clean replays,
or Phase 16's later QA gates. Missing evaluated faces remain
`EVALUATED_CAPTURE=INCOMPLETE` in the current oracle.

## 6. Telemetry file and honest results

Use a fresh, private, already inspected main-owned run directory and one ordinary
new absolute local file leaf; no reparse/ADS/device/UNC path or unapproved
directory. Open with a calibrated exclusive **CreateNew/no-replace** primitive,
never overwrite, replace, truncate, unlink or reuse any existing artifact. Check
destinations and directory identity before construction and again at write;
checks do not eliminate arbitrary filesystem races. Bound scalar/array/string
sizes and total UTF-8 bytes before the write. Emit deterministic UTF-8 without
BOM with explicitly versioned serialization, round-trip finite numeric precision
and well-formed JSON; capture actual values, no predicted serialization. The
hash definition is **SHA-256 of the exact bytes actually stored**, not of an
in-memory object, formatted display text, path or future normalized cm arrays.

The writer must flush its writer and stream, verify byte count, rewind and hash
the actual stream, close/dispose all owned resources, and obtain a verified
readback under the approved local-file policy before sending an exact one-time
receipt. Writer behavior, Max/.NET overloads, EOF/close semantics, float
round-trip, string escaping, integer-handle representation and time bounds all
require main-only calibration. Existing isolated writer evidence is helpful but
does not prove this new observer path. Do **not** use `formattedPrint`.
Flush/close/readback do not establish crash-atomicity or power-loss durability.
Main must independently open and hash the exact raw bytes after return, strictly
parse once (duplicate keys/nonfinite/invalid UTF-8 refuse), verify bounded size,
identity/linkage and issue-free content, and preserve raw MCP wire, receipt and
file separately. A compact receipt is not the grid; no `ok=true` alone is a PASS.

Any create/write/flush/hash/close/readback/serialization error is an observer
failure, including an existing destination. A partially created exact file is
retained as **partial/failed evidence**, never renamed over another, silently
deleted, read as a success, or retried under the same name. Record the original
exception and every close/dispose/readback outcome; a .NET error may escape the
bridge rather than return the desired JSON envelope (the old writer no-replace
control actually did). If creation outcome is unknown, report it unknown.
Main inspects bridge errors, `__MCP_MS_ERR__`, all status markers and cleanup
records. A timeout/crash/transport loss means INCOMPLETE, not no-op or proof that
the callback failed before deletion; do not blind-retry. Even a correct live
receipt can later fail main's independent byte/linkage verification; if the
builder already resumed, refuse **acceptance**, not falsely assert that deletion
was prevented or undone. A capture retained after a later build/baseline failure
is partial evidence from that attempt, never a completed wall or cross-attempt
grid/final pair. Likewise a raw grid file written successfully before a failed
post-observer preservation check retains its original bytes and capture label;
the separately recorded failure prevents admission. Do not rewrite the raw file
to hide either the successful write or the failed guard.

## 7. Failure and independent verification gates

- The observer never deletes a node or modifies geometry. A normal caught
  observer failure must stop before deletion, propagate to the separately
  reviewed runtime failure protocol and leave the telemetry outcome explicit.
  Cleanup may delete **only** the exact attempt-owned node if valid original
  reference/continuity, dependency exclusion, units and before/after exact
  census are established. A name, prefix, tag or reacquired handle alone is not
  deletion authority. If an ownership, dependency, deletion or readback check
  fails, leave/report residual references and INCOMPLETE; preserve original and
  cleanup errors. A native crash cannot guarantee cleanup.
- Check the independent external witness and detached fields before and after;
  poison/retain the exact failed lease per the approved runtime policy, never
  auto-rearm, adopt a replacement, clear a pre-existing global, or turn an
  uncertain cleanup into `P3_REFUSED`/clean. Building, timeout and process/scene
  discontinuity remain inspect-only. The current runtime's independent safety
  blockers listed in `Audit/phase16-p3-runtime-review-2026-11-03/review.md`
  must be resolved/calibrated separately; this design waives none.
- Offline tests in `STATIC-TESTS.md` should precede main-only tiny same-call
  API/identity/preservation calibration, then a newly frozen actual emitted F01.
  Static lexical/order checks are not MAXScript parser, execution, timing, or
  side-effect proof. No hard <2 s guarantee follows from element caps.
- An evidence join must additionally prove same attempt/node/base *in process*,
  observer invocation before delete, correct bound bytes and units, cleanly
  preserved observer state, complete telemetry and raw-wire outcomes. The
  current oracle can check geometry but cannot establish those facts itself.

## 8. Contract decision: is the pre-delete grid itself a gate?

The decided contract requires a deterministic global station grid, returned-ID
tracking and actual-emitter independent geometry checks, but its concise final
acceptance sentence does not expressly spell out an independently captured
pre-deletion grid as a separate named gate. The current independent oracle does:
it requires actual grid, base and evaluated polygon arrays for its overall PASS.
The measurement-next report treats the missing grid as INCOMPLETE. This is a
**decision for main/contract owner**, not an authorization to silently redefine
acceptance:

1. **Retain grid-stage acceptance (recommended unless contract owner decides
   otherwise):** require the same-attempt observer or a demonstrably equivalent
   nonintrusive mechanism. It tests the actual pre-delete tessellation, winding,
   station subdivision and actual grid budget, not merely final shape.
2. **Approve a narrower final-geometry profile:** only an explicit contract
   revision/review and separately versioned assessment may omit that stage; it
   must identify the lost pre-delete topology/winding and actual grid-budget
   coverage and must not claim the existing oracle's full PASS or old broader
   contract. Emitter printouts/predictions do not close the evidence gap.

Either decision still leaves evaluated polygon evidence and all unrelated P3.1
safety/replay gates outstanding. This design does not choose or implement a
waiver.

## 9. Work performed and references

Read the current contract, runtime template and retained actual Main03 emitted
script/wrapper, the earlier measurement scripts/adapter and measurement-next
report, the independent oracle and tests, runtime safety review, and checkpoint.
All conclusions here are source/design analysis or explicitly attributed past
main evidence. No Max call, install, source/test/old-evidence edit, new fixture,
or live measurement was made by this author. One **read-only `git status`** was
invoked inadvertently despite the requested no-git constraint; no git mutation
was performed. A shell hook printed a graphify message; this note does not claim
to know whether any pre-existing cache was touched. No commands were run to
restore or modify it.
