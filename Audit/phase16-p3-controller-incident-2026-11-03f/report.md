# Controller probe incident — independent source/evidence analysis

**Verdict: INCOMPLETE_RESIDUE_OR_IDENTITY; stop scene mutation.** This is an
offline review, not another Max execution. The retained evidence supports a
candidate residue but does not retain an independently witnessed exact live
node/Shell pair across the `fileIn` boundary. Do not infer deletion authority
from the sole node, its name, recovered handles, or a post-hoc witness.

## Evidence and scope

All paths below are relative to the repository root. Source line numbers refer
to the preserved files, not to a proposed replacement.

* `Audit/phase16-p3-main-probes-2026-11-03f/controller-graph.ms` has SHA-256
  `85ff2e65de58b79b525fc9af19d2a30eb68a46c2e0e07ee9791553b7df51d372`.
  `controller-graph-parse-failure.json:5-8` records an actual syntax error,
  with zero nodes in its before/after checks. The diagnostic points to the
  `if ... do`/`else` form at source lines 150-151. No geometry or controller
  behavior follows from that failed candidate.
* `controller-graph-v2.ms` has SHA-256
  `4d5b064c7d98bc531644ed9990629d4a3621989fcae0546c2150b1b6e8f50aa7`.
  A local source comparison found exactly one changed line: `do` became `then`
  in that conditional. This is a parse repair, not a cleanup/ownership repair.
* `controller-graph-v2-residue.json:5-8` records an earlier empty precheck, then
  transport `ok=true` but script result `ERROR=... Mesh operation on non-mesh:
  Box`, `CLEANUP_ERROR=... lost exact Shell`, `cleanup=false`, one object and
  zero selected. The returned output contains no `|setup;...` marker. The later
  read-only inspection observed one `Box001`, node handle `2024P`, base `Box`,
  one Shell handle `2044P`; no parent or children were reported. A separate
  snapshot also reported one object and one Shell. Both are observations at
  those times, not a present-state guarantee.
* Hashes checked offline for the two result records are respectively
  `6adcd6bf6c99ba8ade73bb7d10c7c162af02a4f26a36c0ae90e7c772a28558ce`
  and `b95b20a7c6a0d793bbcae0c2d93c702baa73eca13c1c1f9037ed79d4e03b2867`.
  The runtime safety review is
  `Audit/phase16-p3-runtime-review-2026-11-03/review.md` (SHA-256
  `88baf03fd899d006b14652b9dfcdeb2481c470270448e1d91c9f0bbdcc600272`).
  `CHECKPOINT.md:6-21` also records the same stop condition. The
  existing graph contains no node for these incident source files, so it is
  not a substitute for the preserved primary records.

## Failure localization: proven and not proven

1. The v2 source initializes `n`, `h`, `shellMod` and `shellHandle` as locals;
   after admission its prescribed order is to construct the Box and verify its
   reference/handle and census (`controller-graph-v2.ms:4-9,63-70`). Its next
   statements construct Shell, call `addModifier n shellMod`, call `update n`,
   obtain the Shell handle, validate it, and only then append `|setup` (`:71-76`).
   There is no per-statement stage marker in this interval; the ordered source
   does not prove all of those statements ran to completion.
2. Cleanup reaches `lost exact Shell` only after the `made` branch and the
   preceding exact-node/handle, one-object and zero-selection guards at
   `:134-138` have not thrown. **At that cleanup check, the guard found
   `shellMod == undefined` OR `shellHandle == undefined`.** The combined guard
   does not say which. It does not establish that the original Shell reference
   was never held locally, nor that the Shell handle alone was missing.
3. The cleanup's own `delete n` at `:143` is after that throwing guard, so this
   source path did not reach that deletion. No successful cleanup follows from
   transport success. The later count and snapshot support a remaining scene
   object; they do not themselves identify it by uninterrupted reference.
4. Under the script's ordinary sequential control flow, with no intervening
   callback/invalidation affecting the local values, the missing setup marker
   plus the Shell cleanup guard make the Shell setup interval around `:71-74`
   the strongest source-localized candidate, before a complete non-undefined
   Shell pair and the setup marker. This is **not** proof of an exact source
   line, and the lack of markers does not strictly exclude a transient exception
   in an earlier evaluated identity-check expression whose later cleanup
   re-read succeeded. In particular,
   `update n` on the parametric Box at `:73` is a plausible suspect, because it
   precedes the handle assignment, but `addModifier` or another operation in
   that interval may have thrown or had partial side effects. A modifier
   observed later is consistent with attachment having occurred; it does not
   prove `addModifier` returned normally, or prove reference continuity.
   `Audit/CHECKPOINT-archive-2026-10-28.md:2164-2169` documents a similar error
   for **direct meshop reads**, not an independently measured `update` result;
   it cannot identify this exception's caller.
5. The script has no explicit code that carries either exact local outside the
   parenthesized `fileIn` scope. The surviving result is text, and no retained
   evidence shows a separate exact object witness from the construction
   invocation persisting across calls. Within that invocation, the node guards
   demonstrably reached the Shell guard; that is narrower than proving either
   reference remained available after the invocation. Do not claim an exact
   Shell witness or a captured Shell handle survived. Likewise, do not claim
   callbacks occurred, handle reuse occurred, or that a foreign object was
   actually deleted: none is established here.

`dirtyBefore=false` and `dirtyAfter=false` are recorded flag values, not proof
that no scene/undo-history change happened. `oldKey=false`, PID, path, name,
root/census, class and matching current handles are likewise not session UUIDs
or proof of provenance. The reported dependency list is useful diagnostic
evidence, not a calibrated exclusion of every external dependent.

## Contrast with prior bounded probes

* The VData probe (`vdata11.ms:20-29,73-85` and `vdata11-result.json:5-8`)
  retained the original node locally within one uninterrupted invocation,
  checked conversion identity and handle before exact-reference cleanup, and
  reported zero nodes afterward. Its successful bounded control does not
  supply a witness to this later attempt, prove cross-call retention, or prove
  complete dependency protection.
* The layer probes (`layer-owned.ms:94-107,134-153` and
  `layer-membership.ms:39-48,67-101`) retained their layer backing references
  within the same invocation and guarded name-based layer API calls by those
  references. Their respective results report cleanup and the default layer
  afterward. That narrow in-call evidence cannot authenticate a later node,
  and lookup-by-name was only used after an independent in-call identity check.
* The EData probe (`edata3-result.json:5-8`) demonstrates why a transport-level
  `ok=true` is not success; it logged an actual error, left its precise
  operation unlocalized, and reported its own exact-node cleanup. No result
  above establishes controller/dependency completeness, safe replay or P3.1
  acceptance.

## Minimum safe next step

Preserve the candidate and all evidence; **do not** automatically delete,
adopt, retag, rename, reset, save, clear the dirty flag, rearm, or retry a
scene-mutating probe. The existing user permission for necessary Max work
remains valid; this is an ownership/evidence stop, not a request for permission
again. Have the operator inspect the visible scene and independently decide
whether they can identify and remove the temporary candidate under their own
ownership standard; a name, handle or sole-node census alone must not be
presented to them as proof. If provenance remains uncertain, leave it intact
and keep mutating work blocked. After an operator resolves the residue, main
must obtain a fresh **read-only** scene/context/census observation before any
new admission; neither this report nor the old precheck guarantees the state.
Finding a genuinely pre-existing, independently retained exact reference would
need its own continuity and dependency review; making a new reference by
querying `2024P`, `2044P`, `Box001`, or the sole node is not such a witness.
The same query in the Max Listener/console or through the production runtime
does not turn a newly acquired reference into the original retained witness.

## Proposed replacement design — offline only, not approved or run

This is a design proposal, **not executable MAXScript or an instruction to
mutate the current scene**. First review it against the existing safety review
and validate its scoping/identity behavior; the residual scene remains a hard
stop. Prefer a single uninterrupted, main-owned harness that constructs,
probes and, if safe, tears down its own objects while its original exact
locals are still live. Do not assume a `fileIn` local survives a later bridge
call. A cross-call persistence scheme is an alternative only after separately
calibrating its lifecycle and keeping a genuinely independent original witness;
if that cannot be shown, leave cross-call recovery unsupported.

1. **Admission and independent witness:** On a fresh, operator-resolved scene,
   compare approved context, units, empty exact census, selection, layer state
   and dirty observation before any construction; unknowns refuse. Preallocate
   an outer owning frame with direct exact-reference slots and a distinct
   witnessed attempt ledger. Retain the ledger's original exact instance
   separately from any registry, together with detached expected nonce,
   context and state. A registry lookup, matching tag, or the ledger's own
   self-reported values is not an independent witness. Calibrate whether the
   proposed frame, assignment, reference comparison and any file boundary
   actually have these semantics before relying on them. Limit the model to a
   sequential trusted harness; do not promise malicious-script resistance or
   session/restart durability.
2. **Retain at each constructor return, before risky calls:** Set an attempt
   stage immediately **before** the Box constructor. Receive the constructor's
   returned node in the outer frame's exact `nodeRef` and immediately mirror
   that very reference into the independently witnessed ledger, before any
   handle lookup, formatting, update, modifier attachment or diagnostic read.
   Check both retained references against one another, then capture the node
   handle and cross-check round trips. Capture the exact base reference when
   safely readable. Repeat the pattern for Shell: mark constructor entry,
   retain its direct returned reference in `shellRef` and the witnessed ledger
   **before** querying its handle, attaching it, calling `update`, or reading
   the graph; then independently cross-check its handle before attachment.
   Keep handle numeric values as received, not parsed from printed text.
   Explicitly mark before/after attachment and every potentially throwing
   operation. Mark a step complete only after it returns and its result is
   retained. Do not substitute an unevaluated `Box` for an Editable Mesh or
   assume `update n` is appropriate; avoid that call unless a separately
   calibrated API actually requires it. Do not add mesh evaluation merely to
   bypass the error: graph/controller safety must be checked before evaluation.
3. **Acknowledge the irreducible gap:** Construction and subsequent reference
   capture are not a demonstrated atomic transaction. If a constructor creates
   something but throws, or interruption occurs after allocation and before
   either reference is retained/verified, report the stage and
   `INCOMPLETE_CONSTRUCTION_OR_IDENTITY`; do not search the scene to adopt a
   candidate. A timeout/crash/interruption is not proof the catch, cleanup or
   even the last emitted marker ran. Never automatically retry it. No global
   struct, nonce, handle or later census repairs lost original continuity.
4. **Stage-aware cleanup:** On an ordinary caught error, use only the
   construction-returned live references still held by the owning frame and
   independently witnessed ledger. Verify exact reference agreement, handle
   round trips, correct expected attachment stage, exact survivor census,
   unchanged approved units/context, parent/children, base-sharing and a
   bounded calibrated exclusion of unknown/foreign node **and non-node**
   dependents before deleting the exact new node. `refs.dependents` output
   alone is not yet such a proof. Handle never supplies a replacement when an
   exact reference is missing. Before Shell construction, do not demand a
   nonexistent Shell witness for an otherwise proven node cleanup; if Shell
   construction was attempted but its outcome is unknown, fail closed. A
   constructed but unattached Shell is a non-node; do not call node `delete`
   on it or silently assert its disposal. Define its lifecycle and any
   partial-attachment case explicitly; do not detach a modifier or delete a
   node merely to resolve an uncertain attachment. Unknown,
   unreadable or unexpected conditions, including any failed cleanup guard,
   remain INCOMPLETE with all original/cleanup errors and available evidence;
   never remove other attachments to make deletion possible.
5. **Postcheck and instrumentation:** After any permitted exact deletion,
   verify the original reference is invalid/absent, re-read the **full exact
   survivor set** and compare it to the captured pre-attempt set, and record
   every cleanup/disposal failure separately. A zero count is not proof against
   an unobserved wrong deletion or an unknown constructor side effect. Preserve
   the original error and the last attempted/completed stage in the returned
   result, not only the final marker or transport `ok`. Do not save/reset or
   clear the dirty flag to make the postcondition look clean.

Before any new live construction, independently review a concrete harness and
run offline structural/fault-injection controls for each boundary: before and
after node/Shell constructors, witness writes and handle reads, during/after
attachment and any optional evaluation, reader errors, missing/replaced
witness, wrong or equal-looking references, handle mismatch/unresolvable
handle, foreign dependents/instances, altered context, cleanup/readback errors
and interruption. Show the controls refuse *before deletion* and preserve
neighbor identities. Later main-only bounded live controls, on a freshly
admitted controlled scene, must calibrate actual reference/scope/dependency and
cleanup behavior; offline checks cannot prove Max execution. P3.1 remains NOT
ACCEPTED, and `INCOMPLETE_REPLAY` is not to be lifted by this incident review.

No Max calls, scene writes, git operations, installer runs, or modifications to
source files or previously recorded evidence were made during this review.
