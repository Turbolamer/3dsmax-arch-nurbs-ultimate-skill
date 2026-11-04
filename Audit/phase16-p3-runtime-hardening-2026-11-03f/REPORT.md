# P3.1 runtime hardening — offline, not accepted

**Do not run this revision in Max.** P3.1 remains NOT ACCEPTED. The construction
path and the contract's construction-only `COMMITTED` marker remain present, but
the required complete pre-evaluation Shell/controller/dependency safety predicate
is not calibrated. Moving partial checks ahead of `snapshotAsMesh` does not make
them complete. Resolving that predicate and the main-owned witness protocol is
required before an independently reviewed live run; no `NOOP` was added.

## Preservation and frozen final run

Before editing, the exact 47,522 runtime bytes were exclusively saved to
`wall_surface_runtime.pre-edit.py.bin`, verified SHA-256
`bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15`,
matching the settled historical source hash. `pre-edit.sha256.txt` was also
created exclusively. The historical files and manifests were not edited.

The final run is `python -B Audit/phase16-p3-runtime-hardening-2026-11-03f/run_offline.py final2`;
its status is **exit 1**, not PASS. `final2-results.json` retains before/after
hashes for runtime, both test files, this run script, and the saved runtime: all
five were unchanged during that run. Latest runtime SHA-256:
`d9f470754639a78b3fe5478fde91e5c513d7834c9ba8ffecbcff990225b9b08a`.
Latest protective-test SHA-256:
`36885bad3d566065c8471a4cf8c7dcc6c452de9676e58c03e6cb4f776b83b327`.
Python `ast.parse` succeeded for runtime/test/recorder; it is not MAXScript
compilation. `final-results.json` and `final-*.log` are the earlier run on
different source/test bytes; retained, not a final-source result. A preliminary
17-test run also had one detector failure because a substring matched `==`;
the test was corrected before the frozen final run.

| Actual final run | Result | Scope |
|---|---|---|
| `test_protection.py` | 17/17, exit 0, no skips | Static source/order checks, several calibrated textual mutation controls, and a constrained Python interpreter for the **extracted** status-selection expression. No MAXScript parser/interpreter or Max execution. |
| Unchanged `Audit/test_phase16_p3_runtime.py` | 42 run, **1 FAIL**, exit 1 | `test_cleanup_exact_current_attempt_refs_only` requires the removed `getAnimByHandle createdHandles[i]` branch; it also expects `delete exactNode`. The suite was not edited or weakened. `final2-2.stderr.log` has the actual failure. |

## Implemented source-level changes

* Catch handling never reacquires a node by a handle or deletes a node. Exact
  created/returned candidate references and handles are recorded where available;
  unreturned constructors/conversions, invalid refs, guard errors, foreign/unknown
  census and residuals are reported as incomplete. Even a known exact attempt
  reference is **retained**, because foreign non-node dependency exclusion is
  uncalibrated. This is intentionally not automatic cleanup.
* Exact returned conversion candidate is recorded before continuity validation;
  continuation requires a still-valid original reference, same returned reference,
  and matching handle roundtrip. A number, name or census never supplies deletion
  authority. Current evidence does not prove all conversion behaviors.
* Outer error reports retain the original error, per-reference/census/lease
  diagnostics, snapshot disposal uncertainty, and an INCOMPLETE status after an
  attempt or unresolved lease. The census is bounded at 64 and captured even if
  a constructor returned no node. Diagnostic failures do not claim a clean result.
  A mesh delete returning is reported as a **call returning**, not independently
  proven disposal; a throwing delete is not retried.
* Arm failure removes only the exact struct it just published when still observed
  at the just-declared key, and checks global absence afterward; otherwise it
  retains/reports an unknown or replaced global. No removal of a pre-existing key
  is authorized. Arm/wall mutable strings and the user-property buffer are copied.
* First construction checks the arm's Boolean dirty state twice before BUILDING.
  BUILDING/POISONED entries are explicitly INCOMPLETE, inspect-only. Attempt
  evidence is installed before the constructor and populated immediately after
  each returned reference/handle/candidate; an interrupt between writes or before
  an append can still leave incomplete evidence. A timeout may leave even ARMED
  with no persistent record: **never retry based on that apparent state**.
* Required explicitly listed node properties now refuse if absent. Cheap census,
  exact refs, base/stack/enabled-state checks and a bounded graph read precede
  evaluated geometry. Graph enumeration is only a partial rejection check: it is
  not proof that Shell, controller descendants or dependencies are safe.
* Replay immediately refuses `INCOMPLETE_REPLAY`, without evaluating an edited
  stack. `COMMITTED` remains a construction-only marker under the main contract,
  not accepted replay or QA. A nonce copy and self-read checks detect only local
  observed changes, not an independently held identity.

## Open blockers / non-claims

1. **Independent witness continuity:** main must implement and calibrate a
   separately retained exact lease plus detached expected nonce, context, and
   transition evidence across the real lifecycle. The wall's self-read cannot
   establish that. Array aliasing/equality and persistence of the new attempt
   evidence across interruption are not verified. Lost witness, interruption,
   timeout and ambiguous callback are inspect-only; no adoption/rearm/retry.
2. **Pre-evaluation safety:** complete bounded supported Shell parameters,
   controller descendants/classes and permitted dependencies are unproven.
   The current construction path can still reach `snapshotAsMesh`; do not run it.
   Removing it or substituting provisional COMMITTED would require an explicit
   contract decision and genuine calibrated tests. The partial ordering change is
   not a fix for finding 6.
3. **Cleanup:** foreign dependency exclusion, deletion and exact survivor-set
   verification are unimplemented. Do not infer that a retained residual is safe
   to delete, that no object was affected by an interrupted API, or that cleanup
   happened. Exact references stored in memory and printed census handles are
   diagnostic, not authorization. Main must decide future controlled probes.
4. **Layer and metadata:** no layer comparator was invented; the known
   `LayerProperties` baseline problem and unproven native/specified-normal state
   remain. No supported replay baseline or material/metadata edit detection is
   claimed. Retain the unconditional replay refusal.
5. **No live evidence:** no Max call, MAXScript compilation, independent fault
   injection of Max branches, crash-atomicity, geometry, NOOP, or broader suite
   acceptance is claimed. No installer, archive, global-copy update or cleanup
   was performed. Main must freeze/review sources, rerun relevant tests, and
   perform any authorized Max work itself.
