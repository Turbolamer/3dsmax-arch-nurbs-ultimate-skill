# P3.1 temporary pre-create guard — offline, not accepted

This report supersedes `REPORT.md` only for the current runtime revision; the
earlier report and test logs remain historical and unchanged. **P3.1 remains
NOT ACCEPTED. Do not install or run this unfinished method in Max.**

## Preservation and source changes

Before editing, `wall_surface_runtime.pre-precreate-gate.py.bin` was created with
exclusive write and verified as 58,691 bytes with SHA-256
`d9f470754639a78b3fe5478fde91e5c513d7834c9ba8ffecbcff990225b9b08a`.
Its new companion `pre-precreate-gate.sha256.txt` was also written exclusively.
This is separate from, and does not alter, the older pre-edit snapshot/evidence.

The emitted wall script now has an unconditional `INCOMPLETE_PRECREATE`
refusal in the ARMED creation branch after unit, lease and context/dirty-state
checks, before the BUILDING write, node construction or scene mutation. Its
reason names unproven independent witness, layer, controller/stack/dependencies,
cleanup and native metadata safety. The guard's catch classification is
`P3_INCOMPLETE_PRECREATE` when the diagnostic readback succeeds; diagnostic
uncertainty remains `P3_INCOMPLETE_RESIDUAL`. The unconditional replay refusal
and inspect-only BUILDING/POISONED refusal remain. The construction code is
retained but unreachable through that source path while the guard remains.

**This gate is a temporary refusal, not a fix or proof of safety.** A future
complete repair must explicitly remove it only after the witness, layer,
controller/stack/dependency, cleanup and metadata safety requirements are
independently verified and reviewed with genuine calibrated tests. No
provisional COMMITTED or NOOP was added.

## Frozen offline result

Command: `python -B Audit/phase16-p3-runtime-hardening-2026-11-03f/run_offline.py precreate`.
The recorder correctly exited **1**, because the unchanged existing suite failed.
`precreate-results.json` shows identical before/after hashes for runtime, both
test files, recorder and both preserved runtime snapshots. Final runtime SHA-256:
`3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf`.
Protective test SHA-256:
`19360d8f54ce667e692d2c30ce6be7ea28e5fad1a82d3b79d8fbd95195d7919d`.

* New/extended protective tests: **21/21 passed, no skips**. They pin the
  straight-line emitted guard and replay branch, check ordering against mutation,
  and include negative textual controls for removal, true-predicate bypass,
  preceding lease write and conditional wrapping. They also interpret a limited
  extracted status predicate in Python. These are source-level checks, **not** a
  MAXScript compiler/interpreter or actual Max fault injection.
* Unchanged `Audit/test_phase16_p3_runtime.py`: **42 run, 1 failure**, the same
  `test_cleanup_exact_current_attempt_refs_only` failure as before. It requires
  the removed `getAnimByHandle createdHandles[i]` source branch and also expects
  `delete exactNode`; no test was changed to conceal it. Raw output is in
  `precreate-2.stderr.log`. No extra failures were observed.
* Python AST parsing succeeded for the runtime, protective suite and recorder.
  It does not verify emitted MAXScript syntax or actual behavior.

No Max call, git command, installation, deletion, or modification outside the
assigned runtime and audit directory was performed in this continuation.
