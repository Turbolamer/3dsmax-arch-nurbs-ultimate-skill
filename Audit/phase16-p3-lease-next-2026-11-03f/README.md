# P3.1 future lease: main-only continuation candidate

**DESIGN ONLY; NOT LIVE-EXECUTED; NOT AUTHORIZATION; P3.1 NOT ACCEPTED.** No
Max call was made by this author. This directory is new evidence, not a change
to the runtime or a fix of the other findings in
`Audit/phase16-p3-runtime-review-2026-11-03/review.md`. The operational
templates contain an unconditional stop before any arm or delegated `fileIn`;
unexpanded tokens may instead cause parse failure. Their MAXScript syntax and
all unmeasured semantics remain unverified.

## The distinction this protocol must preserve

Main03's actual earlier lease was POISONED. Main's later read-only entry observed
its key absent in a *subsequent* Max process. The reason for the transition is
unknown. Do not recreate, remove, readopt, re-arm, or retry that key; its
history is not a currently held witness. If it is now present, preserve it and
stop; if absent, preserve absence. Inspect afresh immediately before admission.

The independent **future** experiment requires a separately reviewed new
namespace and/or genuinely changed input/source identity, producing a new
registry key, not merely a new output directory or nonce. Independently
recalculate the actual emitted key from `__P3W_` + SHA-256 of
`namespace + ':' + identity`, verify it matches the frozen new emitted literals
and differs from Main03, and verify all new names are absent at admission. A new
key is an independent test, never recovery or evidence that Main03 is fixed.

The separately reserved **main witness** stores the exact arm-returned lease
instance and original `.values` array instance, plus the initial root reference,
root handle/class and context. A second separately reserved **anchor struct**
holds an independent reference to that exact witness instance, the original
lease/values/root references, and is itself cross-referenced by the witness.
Before *every* delegated wall `fileIn`, inside the same held-pair wrapper and
immediately after byte-hash verification, compare (1) the witness and anchor
against their linked instances, (2) the registry value against both retained
lease references, and (3) its `.values` against both retained array references;
never reacquire any of those originals from the registry.
Compare the lease's nonce, identity, binding, namespace, schema and expected
context against **detached copies of separate literals in the independently
hashed wrapper**, not merely fields copied from the lease. Their actual string
copy/alias behavior is a mandatory live calibration, not presumed from syntax.
The nonce/identity are immutable *external
expectations*, not inherently immutable MAXScript strings; the wrapper's
reviewed bytes and main's separately retained external record supply the
independence. Compare the original root, its native handle round-trip, path,
filename, time, subobject level, selection, census, native units and dirty state
as specified below. After a delegate, check continuity and an explicitly
reviewed provisional-state transition, exact single-node census and approved
post-dirty state. These do not establish that node as safely created or a full
baseline; a thrown delegate or any uncertainty becomes INCOMPLETE.

**Threat boundary.** This catches a replaced registry if either retained original
is intact, and catches a replaced main witness or anchor if the other is intact.
It does **not** create a protected root of trust: in-process globals and struct
fields are mutable. If both witness and anchor (or their retained fields) can be
rewritten consistently, or the wrapper/expected literals changed, a coherent
substitution can evade these checks. Equal nonce strings are not authority.
This is a trusted, sequential, single-writer operational control, not a defense
against malicious MAXScript, plugins, callbacks, or arbitrary concurrent UI.
Root, PID, path, time, count and handle are *not* a scene/session UUID. No
snapshot can prove a transient change-and-restore between reads did not occur.

## A credible cross-call lifecycle is conditional

The ~2 s MCP limit makes a single long, no-yield MAXScript local unrealistic for
arm + measurement + three replays. The proposed alternative is **one contiguous
main-owned orchestration**, not one continuously live local: main exclusively
owns all sequential calls and the Max UI, commits to no reset/new/open/load/
merge/restart/save, callbacks or unrelated writes during the entire experiment,
and externally records immutable ordered request/response evidence and the
reviewed hashes. The main witness and its anchor are first installed in the
**same** call that actually receives the arm's exact return. They persist
between calls; each guarded call must recheck both. Main must stop if that
single-writer/no-yield *operational discipline* cannot credibly be maintained.
This is not an automatic lock, event monitor, or proof that no unobserved
operation occurred. A lost response, timeout, exception, unexpected state,
failed hash/read/close, ambiguous callback or any interruption ends the attempt
as INCOMPLETE: inspect only; **no rearm, adoption, repair, cleanup or retry**.

The arm template also exposes an unavoidable gap: if arm creates a lease but
the same call fails before witness/anchor publication, the exact local may be
lost. Quarantine the new key and all evidence, do not run the wall, and do not
try to reconstruct the witness. The current generator's arm failure cleanup and
the wall runtime's partial-construction/cleanup behavior have separate open
findings. A hash proves selected bytes, not that they are safe. The candidate
cannot authorize their use until those findings receive independent repair and
review.

The **historical** Main03 arm attempted global removal in its exception handler;
it is not the new arm for this protocol. Main must inspect the frozen future
arm's actual catch path. This candidate's strict *retain and inspect* policy
does not authorize cleanup even of a just-declared key after an ambiguous arm
failure. An arm that still removes a global on that path is incompatible with
this conservative policy unless the policy is explicitly re-reviewed; do not
run it merely because a future emitter produced it. No conclusion about the
current concurrently edited source follows from this historical observation.

## Main's required order

1. First resolve the runtime review's **all** blocking findings, including
   layer/native metadata/controller/dependency comparability, pre-evaluation
   order, provisional/commit state, exact-reference cleanup and exception
   propagation. The current wall's `INCOMPLETE_REPLAY` barrier stays. Review and
   freeze the changed sources, independent tests, arm, generated pair and wrapper;
   no code in this directory modifies them. Obtain explicit admission of this
   *new* experiment, with fresh empty/unnamed controlled scene and unit pair.
2. Main reads fresh exact scene/context, old-key absence, process/session and
   *all* new-key absences, with positive/bogus lookup controls. Choose unique
   validated ASCII names `__P3MW_<64 lower-hex>` and `__P3MA_<64 lower-hex>`
   distinct from the wall registry and all existing names. Prepare a fresh nonce
   and immutable external identity/binding/namespace/nonce record. Hash and
   retain each newly generated arm, wrapper, manifest and script. Verify their
   exact parameters mutually agree; validate all substituted token spellings,
   paths and hashes independently before creating an executable reviewed copy.
3. **Before touching the future lease**, run the calibration matrix below on
   disjoint, disposable reserved names and locally constructed dummy structs.
   `01-local-calibration.ms` is a small one-call candidate, not cross-call proof.
   A cross-call experiment needs a separately reviewed setup/read/stop plan on
   unique scratch globals; it must hold its exact original references as this
   protocol does. No negative test is permitted to mutate a real/future lease.
   Return and record raw results, errors, elapsed time, pre/post exact census,
   selection, root/context, dirty state and every reserved-global observation.
4. Only if main independently approves all prior gates, adapt
   `02-arm-witness.ms` in a **new**, no-replace, separately reviewed file. In one
   short call it checks current state and all absences, hashes and holds the
   approved arm, calls it exactly once, receives its exact instance locally,
   verifies its contents, and publishes witness then anchor. Main must execute
   the reviewed wrapper through a separately reviewed held-file inline dispatch;
   `04-outer-dispatch.ms` is a disabled, unexecuted candidate for that boundary.
   Inspect raw return and both globals immediately, and record the result. A failure after the arm
   starts is INCOMPLETE even if census is zero; do not remove globals or retry.
   Any partial publication is retained as diagnostic evidence, not repaired.
5. For a future wall call, adapt `03-held-guarded-call.ms` into a new reviewed
   file. Its caller must independently hash and hold **the wrapper itself**
   immediately before executing it; checking the pair alone does not authenticate
   wrapper code. The wrapper holds both fresh ordinary files, hashes both,
   checks the original witness and state **after hashing and immediately before**
   the only `fileIn` of the wall, then checks continuity again even on an
   exception, closes/disposes resources, and reports uncertainty rather than
   treating any marker or transport `ok` as acceptance. Main compares the
   result against all markers and actual scene/lease/census, not just a final
   string. A repaired contract must separately specify the provisional state,
   its exact-node slot, and approved post-build dirty flag; placeholders do not
   define these. The present template admits an initial `ARMED` attempt only and
   does not support replay. It is deliberately disabled. The outer dispatch's
   actual inline bytes and expected hash must be independently reviewed and
   recorded; it is the trust root, not a recursively unverified `fileIn`.
6. A future replay needs a **new independently reviewed replay variant** applying
   exactly the same before/after witness checks on every call, plus complete
   supported baseline and exact node/census verification before evaluation. Do
   not change `ARMED` to `COMMITTED` in this candidate and assume safety. Only
   after all actual completeness gates are met may main attempt the three genuine
   no-op replays and negative controls; earlier P2 skips remain skips.

Ordinary local read-held files follow the existing controlled private-directory,
single-writer model; holding a read stream is not a universal file-system or
parent-directory race lock. Strictly bound input pair <=2 MiB and short calls;
no duration is promised. If one combined hash/guard/delegate call cannot be
bounded to ~2 s, stop rather than check in one call and execute unguarded in
another. No `formattedPrint`, wildcard/node-name deletion, reset, save, unit
write, global cleanup, or rearming is part of this design.

## Calibration and independent observations required from main

Do not count a no-error return as evidence. Prove each row's expected decision
and the guard's exact predicate, not just any generic failure. Use distinct
scratch names only. Each negative checks the exact original witness, lease,
values, root and complete unchanged scene/neighbors before and after; delegated
mutation sentinel must remain **zero**. Do not replace a real registry to test.

| Case | Expected observation |
|---|---|
| Original lease/witness/values alias; fresh registry + anchor; context same | Guard admits a *safe read-only sentinel*, across at least two distinct sequential MCP calls. Original references, nonce and context remain exact. |
| Fresh equal-payload struct replacing registry, and same struct with fresh equal-payload values array | Each refuses before sentinel. Confirm separately-constructed values differ by reference and alias remains equal; otherwise array-based guard is unsupported. |
| Missing registry; defined `undefined`; wrong type; wrong registry key | Each distinct case refuses, without treating `isGlobal=false` and `isGlobal=true,value=undefined` as equivalent evidence. Positive real-global and bogus-global controls run in each lookup calibration. |
| Replaced or missing main witness; replaced or missing anchor; wrong type; lease/values field changed in either witness alone | Refuse before sentinel. Check original objects retained separately; a missing anchor must not be recreated. Deliberately replacing **both** with coherent objects is an explicit unsupported/fail-open threat-model demonstration, never a safety PASS. |
| Correct-length but different nonce; altered schema/identity/binding/namespace; changed state or nonempty payload | Refuse the *specific* comparison, even with same instance and same length. Keep external frozen literal independent of mutable fields; verify expected nonce stays unchanged. |
| Changed root/reference/handle, path, time, selection, units, dirty bit, census, or unreadable property | Each refuses before sentinel. Use controlled dummy contexts only; do not reset/open/merge or alter the user's real scene to manufacture tests. Calibrate actual reader behavior separately. |
| Original returned witness lost, only registry remains; partial publish; callback/timeout/ambiguous return | INCOMPLETE, no retrieval/adoption, no automatic restore/rearm. An outside transcript with same printed values is not the exact reference. |
| Held arm/wrapper/manifest/script hash changed or read/close failed | No delegated call on pre-delegate faults. After any delegate start, any disposal/identity/read/close failure is INCOMPLETE; report original and cleanup errors. |

Local negative-injection runs can model a thrown delegate and changed globals in
disposable scratch fixtures; they do not prove production cleanup, class identity,
time limits, lifecycle notifications or Max crash atomicity. Cross-call tests
must demonstrate true separate bridge calls, not several `fileIn`s nested inside
one call. The original arrays/strings must be tested for alias semantics in live
Max. The external model below is not an interpreter for MAXScript.

## Files and offline checks

* `01-local-calibration.ms` — no intentional global/node/file writes; local
  struct/array controls and root/context readback, unexecuted in Max.
* `02-arm-witness.ms` — **disabled template** for one arm + witness publication;
  all placeholder values are invalid. No recovery/deletion code.
* `03-held-guarded-call.ms` — **disabled initial-only template** with direct
  pair hashing, in-wrapper external witness comparisons, after-check, and
  conservative error propagation. No replay, baseline, cleanup or acceptance claim.
* `04-outer-dispatch.ms` — **disabled inline-request template** for hashing and
  holding a selected wrapper; not an executable production dispatch as shipped.
* `test_witness_model.py` — independent Python model and source-shape checks;
  it exercises modeled faults, not actual MAXScript or 3ds Max.

Run offline from repo root: `python -B Audit/phase16-p3-lease-next-2026-11-03f/test_witness_model.py -v`.
An offline result covers only the Python tests and stated textual checks. It
cannot prove that any candidate parses, runs, is bounded, or is safe in Max.
