# Proposed static and controlled tests — not executed

These are test specifications/pseudocode only. They do not supply scene-capture
arrays, build an instrumented script, contact Max, or assert that MAXScript can
implement a callback. A future owner must implement/review tests separately. A
static test is not a live proof; only main may run any eventual live control.

## A. Static source and publication tests

Use a source-aware tokenizer or a parsed representation if one becomes available;
plain substring scans can be fooled by comments, strings, unreachable code and
shadowing. Never describe a lexical scan as a MAXScript compiler or execution.
Inject one fault at a time with a known-positive source and verify the targeted
assertion itself fails, not only an unrelated earlier guard.

1. **Real seam and ordering:** creation/readback of all faces and grid update →
   exactly one approved-observer call → neutral-ack validation → exact-reference
   and before/after preservation checks → pre-delete marker → first opening
   deletion. No earlier face deletion or Shell attachment. Reject deleted,
   duplicated, moved-after-delete, conditional-bypass or unreachable hook; also
   reject an observer failure that is swallowed or logged then continued.
2. **Argument provenance:** call's node argument is the local exact created
   node from the same attempt, post-conversion continuity check; never a name,
   handle lookup, copy, clone, reconstructed fixture or expected-data proxy.
   Observer must not receive expected points, face/cut IDs, cell slots, predicted
   counts/geometry or a synthesized mesh. A static use-def check must cover all
   aliases, not merely the literal call expression.
3. **Read-only observer subset:** accepted operations obtain actual base, counts,
   dead sets, `polyop.getVert`, `polyop.getFaceVerts`, measured transform/units,
   serialize and use the owned telemetry stream. Reject scene-node `create`, `copy`,
   `delete`, `convertTo`, `snapshot`, geometry `set`/`create`/`delete`, `update`,
   modifier, selection, time/unit/file/dirty setter, reset/save/undo, unknown
   helper, executable `eval`/`execute`/unreviewed `fileIn`, or mutable global
   overwrite. Whitelist actual reviewed calls; detecting none of a few forbidden
   spellings is not proof. Permit a writer to close/dispose **only its owned
   stream**, never a scene reference. Detached copies of scalar/point/array data
   are needed for comparison and are not scene-node copies.
4. **No payload self-echo:** taint/model the data flow from actual `polyop`
   getter returns through the observer serialization. The arrays must not be
   populated from `expectedPoints`, `cellSlots`, predicted faces/counts, prior
   file, caller-provided geometry or a constant F01 array. Test deliberately
   aliased and nested sources as well as direct textual names. Check the separate
   observed grid-face-ID → deletion-event → final active/dead-loop join, and
   refuse ambiguous or uncalibrated reindexing; predicted cut IDs cannot supply it.
5. **Hash DAG:** test frozen exact observer/generator/input bytes → generated
   actual S → `M.script.sha256=SHA256(S)` → B → actual capture C → E.
   Observer digest in approved seam/binding must match O; generator or observer
   byte change, new protocol/seam, swapped M/S/O, wrong namespace, source hash,
   units, authority, witness or attempt ID each refuses. No S self-hash or M
   self-hash, no mutual B/wrapper hash, no output hash embedded upstream; no new manifest fields without
   schema/contract decision. Corrupting a byte or changed line ending in *each*
   file must be detected by hashing original bytes, not JSON reserialization.
6. **Bounded serialization and CreateNew:** no replacement/append/truncation or
   evidence-file deletion; explicit finite/cap checks and correct UTF-8 framing,
   raw exact-byte digest and close/error propagation. A lexical reference to
   `CreateNew` alone is not an I/O proof. Isolate resource ownership and all
   early exits, including failed close and escaped exceptions.
7. **Oracle adapter contract:** input is actual raw grid with one-based active
   vertex array/loops, world coordinates and measured unit pair. Verify source
   analysis for `grid_raw` status/schema/units/four target comparisons and the
   current absence of grid-specific `issues`/header/authentication checks.
   Test a proposed external admission layer, not an imagined current one. On a
   private explicitly `synthetic_test` dictionary, validate missing/extra/dead
   slots, invalid/duplicate vertices or loops, reversed loops, nonfinite numbers,
   nonquad, mismatched unit type with equal factor, target/transform mismatch,
   grid `issues`, bad/stale binding, duplicate JSON keys and truncated bytes.
   A clean grid control must cause the intended named checks to run; each
   mutation must make its **own** intended check fail/refuse. Existing
   `EVALUATED_CAPTURE` remains INCOMPLETE with no native evaluated faces.
8. **Replay and no fabricated PASS:** a replay never calls the observer or opens
   the prior/new grid output, including when replay is refused. Synthetic data
   always has `kind=synthetic_test` and
   cannot be promoted by a capture label or passing result. Missing actual arrays,
   final capture, byte receipt, independently held witness, event sequence or
   accepted source authority yields INCOMPLETE; mismatch yields FAIL/refusal.
   No test alters an old evidence file to retrofit a result.

## B. Conceptual seam behavior / fault matrix

Implement a **host-neutral state-machine model** only as an offline unit test;
it can validate intended transitions but cannot prove actual MAXScript behavior.
Use spies for observer invocation, writer, exact-ref comparators, deletion and
cleanup; detached value copies for mutable arrays. Pseudocode:

```text
given pristine_grid and explicit independent_witness and approved_observer:
    run_model()
    assert called_once_with_exact_reference(pristine_grid)
    assert observer_only_read_actual_geometry()
    assert post_capture == pre_capture    # exact supported state, NOT initial empty scene
    assert receipt_verified_before_delete()  # no crash-durability claim
    assert opening_face_delete_invoked_only_after_all_guards()

for fault in each_fault_below:
    configure_fresh_model_and_neutral_positive_control()
    inject_only(fault)
    result = run_model()
    assert not accepted(result)
    assert not opening_face_delete_invoked()  # detected synchronous seam failures
    assert exact_nonowned_state_unchanged()
    assert error_and_cleanup_outcomes_preserved()
```

Faults: absent/wrong/replaced callback; equal-looking but distinct callback;
undefined/false/wrong-type return; exception before/during/after capture; zero,
two, reentrant or late callback; wrong exact node/base including same
name/handle/coordinates; stale/replaced lease/nonce/attempt ID; conversion
identity uncertainty; invalid/dead slots, wrong class, unexpected modifier,
over-cap counts, getter throw, unit type/scale/factor drift; changed geometry,
stack, exact node set, transform, selection, time, dirty or file state; unknown
pre/post comparison; existing telemetry destination; partial write, flush/hash/
close/readback failure, duplicate receipt; and raw bridge error/marker despite
transport success. For cleanup inject missing node, unprovable identity, foreign
dependent, unit drift, delete throw/unknown outcome and census/readback error;
require retained residual/unknown and never guess by name/handle.

Separate cases for failures *after* the builder resumed or for loss of transport/
crash: **do not assert deletion did not happen**. Assert that the model reports
unknown/incomplete and never claims rollback, acceptance or a safe retry.

## C. Main-only future calibration outline, NOT authorization

After runtime safety review and frozen source/contract approval, main may design
its own tiny controlled experiments with exact owned refs and read-only before/
after snapshots. Do not use pre-existing user geometry or this note as an
executable recipe.

- Demonstrate real callback creation, scope/lifetime, exact instance comparison,
  actual node/base passage, synchronous ordering and one-invocation semantics.
  Same callable/target positives; independently constructed equal-looking callable,
  node/base and wrong-global controls must discriminate. If Max cannot do so,
  report unsupported; do not fall back to a fake grid.
- On a tiny owned grid, compare the observer's actual coordinates/loops with an
  independently executed calibrated query, including translated **and** rotated
  controls; an intentionally double-transformed observation must fail. Check raw
  counts/slots and independently inspected world coordinates, not only area.
  Independently compare exact node/base, geometry, object transforms, scene
  census, selection, time and dirty flag immediately before/after observer.
- Test capture-file CreateNew, UTF-8, escaping/precision, hash/readback and
  failure behavior with already existing leaf bytes preserved. Never use user
  paths as negative controls. Capture full live error and resource outcome;
  an escaped ToolError is not a successful INCOMPLETE JSON envelope.
- After calibrated positive/negative semantics, only a new hash-frozen actual
  emitted F01 pair may be considered. Preserve before/after byte snapshots,
  exact live witness/target refs and raw wire; independently re-read the grid
  file, link it to the final capture from the *same* attempt, run the oracle and
  retain all remaining INCOMPLETE results. No further scope is accepted by this
  outline.
