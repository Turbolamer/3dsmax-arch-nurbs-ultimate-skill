# Phase 16 P3.1 exact-current-attempt cleanup — offline reference model

**Status: INCOMPLETE; not accepted; no authorization for live use.** This is
an independent, deliberately conservative Python thought experiment, not the
wall emitter, a MAXScript harness, a production fix, a general scene-graph
algorithm, or evidence of Max semantics. Do not integrate or execute it in Max.
The current scene-residue/owner-stop instructions and the pre-create and replay
blocks remain in force. In particular, the model supplies no deletion authority
for the already-reported Box/Shell residue.

## Scope and oracle

The contract requires cleanup of *exact* newly created current-attempt nodes
where safety is proven, removal verification, and an INCOMPLETE/residual report
otherwise. The incident establishes that a handle acquired after an error, a
name, or a census does not reconstruct the lost original ref; the hardening
review identifies both the necessity of a safe positive case and the insufficiency
of unconditional retention. The lease candidate describes an independent
witness and explicit limitations, not a proven cross-call mechanism. This
model addresses only a synthetic single attempt; it does not change lease,
COMMITTED, arm, replay, evaluation or publication behavior.

The oracle is **explicitly closed-world**: `SyntheticScene` owns finite lists
of all modeled nodes, all modeled live non-nodes and all modeled directed edges.
The input `graph_complete=True` is an *assumption/certificate supplied by the
fixture*, never inferred from a node count, observed edge list, `refs.dependents`,
or Max. Unknown/false/unreadable completeness refuses. Identity comparisons use
Python `is`; edge endpoints are identity-keyed and multiplicities matter. For a
known-safe attempt, the exact graph is the retained pre-attempt graph plus
`(new_node, base, exact_new_base)` and, after completed attachment only,
`(new_node, modifier, exact_new_shell)`. No other edge, new node, live non-node,
shared base, child/parent, dependent, or reverse reference is admitted. The
whole exact pre-attempt survivor node/non-node sets and edges must match after
deletion. This is a narrower assumed fixture than the space of possible Max
graphs; it is **not** a proof of graph completeness or a generally valid
allowlist. The tests use both empty and nonempty synthetic baselines; the latter
only exercise preservation and do not change the contract's initial empty-scene
admission requirement.

## Witness, stage, and cleanup decisions

* Each synthetic constructor's **direct return** is assigned to the original
  owning-frame slot, then mirrored as the same exact object to a separately
  retained witness and anchor before the handle is read or a risky attachment
  is attempted. The separate calls intentionally expose failure/interruption
  gaps; they are not an atomic capture. Detached expectations for root,
  document and units are checked; node and Shell handle values must agree in
  all slots and round-trip **to the original ref**. A lookup result is never
  assigned as a replacement. Pre-Shell and pre-attachment checks re-read this
  synthetic scene before the next mutation.
* A caught failure after fully witnessed node/base creation but **before Shell
  construction is attempted** can clean that exact node without demanding a
  nonexistent Shell. A fault at constructor entry, during construction, after
  return but before all witness/handle/base slots are trustworthy, or with an
  unknown graph retains. In this intentionally strict model, the `:before`
  injection occurs after the attempted-stage marker: e.g. a failure at
  `shell_construct:before` is treated as unknown rather than inferring no call
  from the synthetic label. An allocation-before-return fault exposes the
  irreducible unowned-ref gap; later census/handle observations are diagnostic
  only.
* For a witnessed Shell whose attachment has **not been attempted**, default
  behavior retains both. A separate opt-in, fabricated `dispose_unattached_shell`
  primitive supplies an explicitly hypothetical *positive* lifecycle case;
  only after its verified effect and complete recheck can node deletion follow.
  This is **not** a claim that Max can or should dispose a standalone Shell in
  that manner. If attachment was attempted but did not return, retain even if a
  matching edge is or is not present. A completed attachment can be cleaned
  only under this model's synthetic exact-node deletion capability and all
  remaining guards. No attachment is detached to enable cleanup.
* With all guards satisfied, the fabricated deletion primitive receives the
  exact frame-held node, not a handle lookup. Its normal fixture behavior also
  invalidates its unique base and attached Shell; this too is an assumption,
  not a Max lifetime claim. Postchecks independently read original validity,
  node and non-node survivor **identities**, graph, witness and context; errors
  are retained alongside the initiating error. A successful operation return
  alone, a zero count, or a later diagnostic reference is not cleanup proof.
  Dirty state is observed and never cleared; the synthetic dirty transition is
  assumed, not a Max calibration.
* `INCOMPLETE_CLEANUP` may mean refusal *before* mutation or an error after a
  synthetic delete/disposal effect. Consult `attempted`, `completed`, `events`,
  `errors` and diagnostic survivors; it **does not** imply that every owned
  object still survives. A guard refusal before deletion retains all observed
  objects. A delete that throws, silently does nothing, deletes a neighbor, or
  deletes both neighbor and target cannot be called CLEANED. Any interruption,
  including during a delete or postcheck, is `INCOMPLETE_INTERRUPTED`, stops
  further reads and cannot be retried by the same harness. No cleanup or
  postcheck can be assumed to have run after a real timeout/crash.

The model assumes a trusted sequential single writer, a working fixture oracle,
immutable retained instance roots and no covert synchronized replacement of all
frame/witness/anchor copies. Those roots are Python object references, not
calibrated Max globals/structs; neither the candidate lease protocol nor this
model is a defense against hostile scripts, callbacks, shared mutable roots,
transient changes between reads or arbitrary concurrency. The synthetic graph
and disposal postulates are the central outstanding implementation/calibration
gaps, not facts that a future runtime may silently adopt.

## Executed tests and hashes

Executed from repository root on Python 3.14.4:

```text
python -B Audit/phase16-p3-cleanup-model-2026-11-03g/test_cleanup_model.py
Ran 32 tests in 0.014s
OK
```

Exit 0, **32 unittest methods**, no reported skip/xfail; table and subtests
inside methods exercise additional distinct faults. `test.stderr.log` contains
the exact method list and unittest output, `test.stdout.log` is empty, and
`test-result.json` records executable argv, exit and before/after SHA-256. The
two Python sources were parsed with `ast.parse` before that run; hashes matched
before and after. Earlier while developing the suite, a 30-method run had one
failure because a generic guard-interruption point also occurred during forward
checks; the distinct `cleanup:guard_begin` injection corrected the *test's*
target. The subsequent runs passed. That earlier failure was not a Max result.

The tests' independent expected stage table and concrete side-effect assertions
cover:

1. Positive exact deletion before Shell and after completed attachment, empty
   and nonempty baselines, plus the strictly conditional standalone-Shell
   disposal path. Every positive verifies exact survivor identities.
2. Constructor entry, allocation-before-return, frame/witness/anchor capture,
   handles, base, and both attachment boundaries; partial attachment is checked
   with and without the visible synthetic edge. Explicit stage table chooses
   CLEANED or retain without calculating expectations from the guard itself.
3. Same-handle node **and Shell** ref swaps with a correspondingly replaced
   handle lookup: each retains the original witness and both objects. Missing,
   invalid, changed or unresolvable refs/handles, replaced/wrong-type witness,
   anchor or frame, and wrong trace are distinct controls.
4. Root/path/time/dirty, selection, native unit type/scale/factor (including a
   different pair with equal factor), exact census and equal-count replacement;
   no readable failure is treated as equality. An initial wrong unit pair
   refuses before construction. Forward pre-Shell/pre-attachment checks have
   explicit before-next-mutation negative sentinels.
5. Known baseline and new foreign nodes, distinct non-node controllers and
   both dependency directions into node/base/Shell, plus shared bases,
   parent/child/extra edges, unknown graph certificate and every guard reader.
6. Unsupported/no-op/throw-before/throw-after hypothetical disposal, drift
   between disposal and recheck, throw/no-op/wrong-target/collateral deletion,
   each postcheck reader error, simultaneous errors and diagnostic failures.
   Original errors and observable survivors remain separately visible.
7. Interruptions before/after every synthetic construction/witness/handle/
   guard step, inside constructor/attachment effects, and at representative
   cleanup/disposal/delete/postcheck/diagnostic boundaries. `events[-1]` is the
   interrupt point; no cleanup on forward-path interruption and no retry are
   asserted. These are simulated, not real bridge timeouts.

SHA-256 of relevant bytes at this report's preparation:

| File | SHA-256 |
|---|---|
| `reference_model.py` | `901ec8467b31845ced61ad1e289bc9801a9a351d4c433d1da7dd68a5cfcbe3ac` |
| `test_cleanup_model.py` | `10fde1f2216e5aff0272ce72a345149a52f8375150eb743ca91d535e6392d729` |
| `test-result.json` | `31d0c0eed79c1b53477193d3cf8bd48ad12332cb76f8bcd4d3c07a9b76f1c761` |
| `test.stderr.log` | `56eb32f1cf737a660421483d47a730754a40f9e12b6aa8d87f133ad026b3c2b6` |
| `test.stdout.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `Audit/_phase16-p3-contract-2026-11-02e.md` | `4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f` |
| `Audit/phase16-p3-controller-incident-2026-11-03f/report.md` | `3c848df6dfca5f201ce0c358aab95d55ad5596a9cbd0f744725afc0441b055a3` |
| `Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md` | `144c7b04b31a169cf4f896848a8a5f627d65c2672ab2836c78b091e2bf3e2966` |
| `Audit/phase16-p3-lease-next-2026-11-03f/README.md` | `02a21e750a0b1afdf744d504750753f9c9ce97c507648d36e8c1a8e564c43a5d` |

No Max/MCP calls, git writes, installer/package/global operations, or edits to
existing files were made for this model. The output directory was created with
`os.mkdir` (refuses a pre-existing directory). Source/test hashes and the
pass are evidence only for these synthetic bytes, not acceptance of P3.1,
actual dependency exclusion, ownership continuity, safe Max cleanup or replay.
