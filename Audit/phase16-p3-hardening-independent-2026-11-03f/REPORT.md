# Independent P3.1 runtime hardening review — 2026-11-03f

**Decision: BLOCK LIVE CONSTRUCTION. P3.1 is NOT ACCEPTED.** The requested
`d9f470…` revision removes a dangerous cleanup fallback, but does not implement
the approved failure-cleanup behavior, a reliable independent lease witness, or a
complete pre-evaluation safety gate. Its `STOP` is a comment: construction and
the incomplete evaluation path remain reachable in generated source. The later
`3a7a38…` revision adds a real source-level pre-create refusal, but it is a
temporary block, not evidence that the retained implementation is safe. No Max
call or MAXScript compilation/execution was performed in this review.

## Evidence and version boundary

* **Requested reviewed runtime A:** SHA-256
  `d9f470754639a78b3fe5478fde91e5c513d7834c9ba8ffecbcff990225b9b08a`, now
  independently hash-verified at
  `Audit/phase16-p3-runtime-hardening-2026-11-03f/wall_surface_runtime.pre-precreate-gate.py.bin`.
  All `A:<line>` citations below refer to that byte-exact snapshot.
* **Earlier baseline B:**
  `Audit/phase16-p3-runtime-hardening-2026-11-03f/wall_surface_runtime.pre-edit.py.bin`,
  SHA-256 `bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15`.
  Compared with A, the previous catch reacquired an invalid node by saved handle
  and could then delete it; it did not screen foreign non-node dependents.
* **Concurrent update C:** The working runtime was A on the first SHA check,
  then became SHA-256
  `3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf` before
  tests. The protective suite also changed during review. C's source differs by
  an unconditional pre-create guard, its diagnostic branch, and comments; see
  `scripts/wall_surface_runtime.py:853-871,1044` while those bytes remain
  unchanged. `PRECREATE-GATE-REPORT.md` is the owner's later version-specific
  report. This report does not silently attribute A's reachable path to C.
* Contract = `Audit/_phase16-p3-contract-2026-11-02e.md:28-33,39-48`; design =
  `Audit/_phase16-p3-runtime-design-2026-11-02e.md:79-83,200-221,230-255`;
  earlier independent review = `Audit/phase16-p3-runtime-review-2026-11-03/review.md`.
  The P3.1 **contract** was agreed, but P3.1 implementation/live acceptance was
  not. This distinction matters when describing the regression.

## Findings, in priority order

### 1. BLOCKER — A can construct and evaluate despite `STOP`

`A:853-869` checks state and proceeds to set BUILDING and construct
`Editable_Mesh()`. The comment at `A:793-795` is immediately followed by
`evaluatedSnapshot` at `A:796`, and `A:928-930` calls `nodeSnapshot` on first
construction. Bounded graph traversal before `snapshotAsMesh` is not an exhaustive
Shell/controller/dependency exclusion (`A:608-643,755-796`). Moreover, construction
calls `update node` after adding Shell (`A:920-923`) before those checks; whether
this triggers particular evaluation is unverified, so moving only
`snapshotAsMesh` would not prove no prior evaluation. These are static control-flow
facts, not a reproduced crash or a claim that every environment reaches the call.

**Recommendation:** Keep an executable unconditional refusal **before any lease
transition or scene construction**, not merely before `snapshotAsMesh`, until a
reviewed complete safety predicate and witness/cleanup controls exist. C's
`require false` at `:861-863` supplies this source-level block for its wall
creation branch; it does not prevent a separately executed arm script from
publishing a global, does not validate Max semantics, and must not be removed to
make a test pass. Freshly generated artifacts and prior already-emitted artifacts
must be identified by hash; a change to the emitter does not change old `.ms`
files. Resolve all blockers and test true evaluation ordering before live work.

### 2. HIGH / contract blocker — safer refusal, but no required cleanup

`A:977-1016` never deletes a current-attempt node or promotes an invalid reference
using a handle; it records and retains both originally created and conversion
candidate refs. Recording a returned conversion candidate before checking exact
continuity (`A:879-885`) is an improvement. Relative to B, avoiding deletion
based on a reacquired handle materially reduces the *source-level* chance of
deleting a substituted/foreign node when identity or dependencies are unknown.
It does not establish safe cleanup or prove what `convertTo` actually does.

However, the approved contract requires failure cleanup of exact newly created
references, verification of removal, and residual INCOMPLETE on failure
(`contract:33`); the design allows retain/INCOMPLETE when dependencies or identity
are unknown, not unconditional retention even when a safe case can be proven
(`design:232-252`). A deliberately implements **no automatic node cleanup at
all**, so a construction/baseline exception after node creation is expected by
source to leave a residual rather than satisfy the clean-success case. Do not
characterize this as implementing the contract. Nor is retaining every unknown
node equivalent to proving that no prior operation affected a foreign object.
Recorded Main03 cleanup happened under B, not A: it cannot be cited as A cleanup
evidence. Interruption before a constructor or conversion returns is unresolved,
not proof of an actual Max partial-constructor incident.

**Recommendation:** Under the existing contract, first calibrate a bounded,
allowlisted known-safe dependency graph and exact live-reference/handle
continuity; delete **only** the still-valid exact created reference when all
checks are proven and re-read exact survivor sets. Unknown identity/dependency,
unit drift, attachment, failed delete/readback or interruption => retain and
report INCOMPLETE; never use name, tag, census or a reacquired handle as deletion
authority. If maintainers instead want permanent manual-only cleanup, obtain an
explicit contract decision; do not present it as the approved automatic-cleanup
implementation. A test asserting handle-based reacquisition must not drive a
reintroduction of the unsafe fallback.

### 3. HIGH — independent witness and interruption/poison remain unproven

The wall self-reads `registryWitness` and nonce (`A:826-835`); later equality
checks compare against that same in-call read (`A:859,932`), not an externally
held original struct and detached expected nonce/context. A shape-compatible
replacement or a modified valid-length nonce is not independently authenticated
by this code. This is a source-level protocol gap under the stated local trusted
single-writer threat model, not a demonstrated hostile replacement. Actual Max
array/struct equality and cross-call lifetime remain uncalibrated.

`A:864-866` sets a **local** `attemptStarted` before writing BUILDING/evidence;
a timeout between those writes can leave an apparently ARMED lease and no
persistent attempt record. Constructor/convert can return before their refs are
appended (`A:869-883`). During successful publication `lease[8] = node` replaces
the attempt evidence before COMMITTED (`A:933-937`). On caught failure, census
and per-reference work occur before the best-effort POISON write
(`A:943-1039`); interruption, an unguarded diagnostic/append/print error, or
registry mismatch can leave BUILDING/ARMED or partially published evidence.
`LOCAL_POISON_WRITES_RETURNED_VERIFY_EXTERNALLY` is correctly qualified; it is
not independent proof. A failure in the post-COMMITTED diagnostic print would
also enter the catch while `attemptStarted` remains true, so outcome must not be
inferred from seeing a transient marker alone.

**Additional diagnostic issue:** the code validates units, lease shape, identity,
nonce and dirty-state type **before** setting `unresolvedEntry` for BUILDING or
POISONED (`A:824-841`). If one of those earlier checks fails and catch census
succeeds, the final status expression (`A:1042`) can select `P3_REFUSED`, even
when an uninspected previous lease is BUILDING/POISONED or its witness is lost.
The entry refusal is not a clean-history proof. `source-checks.json` models the
actual extracted expression with `attemptStarted=false`, `unresolvedEntry=false`,
known census and no diagnostic errors; it returns `P3_REFUSED`. That is an
offline predicate model, not an injected Max observation. The same ordering is
present in C before its temporary gate.

**Recommendation:** Main must own and check a genuinely independent retained
struct plus detached expected nonce/identity/context and state transition log
before/after every arm-following execution, across a calibrated uninterrupted
session. Classify missing/replaced/unreadable witness, every timeout, ambiguous
callback, interrupted catch, malformed lease or unexpected state as INCOMPLETE
at the harness boundary even if the wall prints `P3_REFUSED` or appears ARMED.
Never re-arm/retry/adopt based on the wall's registry self-read or counters.
Add fault-injection coverage at every write/capture/publication and catch boundary;
only main may subsequently calibrate short owned probes in Max.

### 4. MEDIUM-HIGH — `COMMITTED` semantics need an explicit decision

`A:933-938` can set `COMMITTED` after two **bounded** snapshots while explicitly
reporting replay metadata incomplete. A's and the hardening report's assertion
that this is the contract's construction-only marker is not established by the
reviewed coordinator contract, which requires actual comprehensive equality for
replay (`contract:30-31,43,48`). The prior runtime design expressly says no
COMMITTED if any full baseline check is incomplete (`design:214-217`). It is
correct that A refuses replay unconditionally before node inspection/evaluation
(`A:844-850`), so it does not emit a false `P3_NOOP` here; nevertheless the
name/meaning is ambiguous for consumers and contradicts the reviewed design.

**Recommendation:** Obtain a documented coordinator decision: either use a
distinct construction-only/provisional state, reserving COMMITTED for the full
gate, or explicitly revise the governing contract and all consumers. Never
equate `P3_CREATED_UNVERIFIED` or COMMITTED with accepted geometry or replay.
Keep replay unconditionally incomplete until all required categories are proven.

### 5. MEDIUM — diagnostics improved but remain best-effort

Compared with B, A captures conversion candidates earlier, protects the arm's
global removal by exact just-published struct and verifies absence when the call
returns (`A:441-474`), checks the arm dirty state twice, records bounded census
and per-reference errors, copies the user buffer and mutable context strings,
refuses missing required properties, and tracks snapshot disposal uncertainty
(`A:696-753,941-1044`). These are useful conservative changes. They are source
observations, not proven runtime semantics. The arm can still be interrupted
between declaration/publication/cleanup; a successful delete call is not an
independently verified mesh disposal; catch's raw reason print and some follow-on
operations are outside dedicated guards. Snapshot state is local, and output
may be truncated or lost on interrupted execution. The former live
`LayerProperties` baseline problem and complete native/specified-normal data
comparability are not resolved by these edits.

**Recommendation:** Treat every incomplete/error marker and raw bridge result,
including missing final output, as inspect-only. Calibrate layer backing identity,
nested properties, controller/stack/foreign dependency exclusion, native metadata
and disposal with hit/miss/bogus controls. Test diagnostic/poison failures and
verify expected exact scene/witness survivor sets. Never assert clean disposal,
clean lease or unchanged scene solely from a returned call, marker, or zero count.

## Independently executed offline tests

Both suites were read first: they import only local pure-Python planning/source
code and do not call Max or write user files. Every invocation used `python -B`;
only new files in this audit directory were written. Raw stdout/stderr, arguments,
exit codes and before/after hashes are retained in the files below. No existing
source/test was edited to mask a failure.

| Runtime/test version | Existing runtime suite | Existing protective suite | Evidence |
|---|---|---|---|
| A `d9f470…`, original test `36885b…`, byte-identical isolated mirror | **42 run; 1 FAIL**, exit 1 | **17 run; OK**, exit 0 | `d9-results.json`, `d9-runtime.stderr.log`, `d9-protection.stderr.log` |
| C `3a7a38…`, updated test `19360d…`, working tree | **42 run; 1 FAIL**, exit 1 | **21 run; OK**, exit 0 | `latest-results.json`, `latest-runtime.stderr.log`, `latest-protection.stderr.log` |

The precise failure for both is
`SourceTests.test_cleanup_exact_current_attempt_refs_only`
(`Audit/test_phase16_p3_runtime.py:363-369`): its first failure is the required
text `getAnimByHandle createdHandles[i]`; the next assertion also requires
`delete exactNode`. The first assertion was not reached past to execute the next;
static source review confirms the next string is absent too. The test's demand
for handle-based reacquisition is unsafe as deletion authority; its demand that
there be *some proven-safe cleanup path* reflects a real unimplemented contract
requirement. Preserve the failure until a reviewed contract-compliant repair and
protective behavioral tests exist, rather than weakening assertions solely to
turn the suite green.

For A, the runtime snapshot was saved by the source owner during the concurrent
edit. The original protective-test bytes were reconstructed **only inside this
new audit directory** from the newer test's additions and required to match the
original recorded SHA-256 `36885bad3d566065c8471a4cf8c7dcc6c452de9676e58c03e6cb4f776b83b327`
before writing/running. `d9-fixture-manifest.json` and `d9-results.json` show all
five copied inputs, their exact hashes, and stability; `prepare_d9.py` documents
the reconstruction. This is an isolated copy with identical test/source bytes,
not a rerun of the concurrently changing working file. The earlier direct run
against C with the old protective test is preserved separately as `results.json`;
it had 3 parser errors caused by that old test not understanding C's additional
status clause, and is **not** the frozen A result or the latest updated-test
result.

The source-level observations in `source-checks.json` independently inspect the
actual emitted A artifact and model only the extracted status predicate. These
checks and both protective suites do **not** parse/execute MAXScript, inject
Max faults, demonstrate the lease survives a timeout, or prove no foreign
deletion. No new scene or live observation is claimed. The existing historical
Main03 records are evidence of that older run only.

## Required handoff

1. Preserve the pre-create refusal in C and keep older A-generated artifacts out
   of Max. Recheck exact current hashes after all parallel writers stop.
2. Agree witness, transition/commit semantics and cleanup contract; implement
   independent identity checks, fail-closed interruption handling and safe exact
   cleanup with explicit survivor verification. Do not reinstate handle-only
   reacquisition to appease the legacy test.
3. Establish bounded pre-evaluation, layer, metadata, dependency and disposal
   controls, then add discriminating positive/negative and interruption tests.
   Repeat all relevant offline suites on a frozen tree and honestly retain
   failures; main alone decides and performs any subsequently authorized live
   probes. No install, QA acceptance, NOOP or rollback claim follows from this
   review.
