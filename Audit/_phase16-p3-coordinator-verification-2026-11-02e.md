# Phase 16 P3.1 — coordinator gate, 2026-11-02e session

Host date rolled to 2026-11-03; session artifacts retain the `02e` label.

## Decision

**P3.1 is NOT ACCEPTED; Phase 16 is not complete.** P0/P1 and bounded offline P2
acceptance stand. New bounded emitter modules, actual output pair, synthetic F01
inputs, independent oracle and tests exist. Offline behavior is verified on the
snapshot below. Actual emitted runtime fails its initial baseline safely; full
F01 scene geometry and clean three-run NOOP/edit safety have not been accepted.
Do not bypass the baseline, relabel a synthetic echo, or install this unfinished method.

## Frozen execution, not just author claims

Main executed:

```text
python -B Audit/run_phase16_p3_settled.py --out Audit/phase16-p3-final2-2026-11-02e --unique-out
```

| Suite | Actual methods | Raw outcome |
|---|---:|---|
| builder | 34 | OK |
| independent existing output | 7 | OK |
| independent public boundary | 22 | OK |
| inputs | 38 | OK |
| independent oracle | 65 | OK |
| publication | 42 | OK |
| runtime offline | 42 | OK |
| **Total** | **250 / 7 scripts** | **all exit0** |

Main read raw log summaries and protective assertion names, verified every stdout/
stderr hash against each result record, and independently compared before/after/
process-exit **307 identical fingerprint entries**. No per-suite/end drift,
baseline problems, missing suite or abnormal exit. The sole qualifier is an
independent JSON summary explicitly reporting skips0; no test SKIP or xfail was
observed. The 131 named independent events are not a separate coverage total.
Recorder `NOT_ASSESSED` is deliberate: it never grants acceptance from exit0.
Independent final evidence review concurs:
`Audit/_phase16-p3-final-run-review-2026-11-02e.md`.

Tested source hashes:

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12 scripts/wall_surface_inputs.py
bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15 scripts/wall_surface_runtime.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
```

The first final recorder directory is immutable historical failed evidence:
3/7 suites exited0, then the recorder stopped because a late status-draft document
appeared. Four suites were NOT_RUN there. Final2 is the complete settled repeat;
the failed run is not erased or quietly rebranded.

## Actual live gates and failures

- Fresh entry: empty unnamed scene, mm/1, saveRequired=false. Main alone operated
  Max sequentially. Native unit/parser and literal Box-bound controls passed with
  exact-reference cleanup. A translated+rotated quad proved snapshot world-space
  capture, preventing a masked double-transform bug. Tiny Shell-quad full capture
  actual bytes/hash gave base4/4/1, triangles12, area10000 and volume100000 native
  units; this is calibration, NOT F01 acceptance.
- Preserved/diagnosed live failures: explicit throw argument in catch, local
  Shell-shadowing, undeclared global publication, built-in `freeze` helper name,
  reserved `by`, marshalled byte-array `.Length`, Integer64 JSON `L`. Targeted
  repairs are covered offline and retested where evidence records say so. A
  transport `ok=true` was never taken as geometry PASS.
- Actual Main03 pair and arm/wrapper SHA-256 were independently checked, explicit
  lease armed, and authentic script loaded through read-held hash-checked files.
  Initial baseline threw **LayerProperties MixinInterface cannot convert to
  MaxObject**. Runtime cleaned its attempted exact node, final objects0; exact
  witness survived as POISONED. See `_phase16-p3-main03-live-result-2026-11-02e.json`.
- Actual repeat of the same pair refused spent/poisoned lease before recovery;
  same witness, same state, census0. This is a bounded refusal, not clean NOOP.
- Actual unit controls refused wrong type and separately labelled negative
  mutations of embedded type/factors with exact scene/context preserved. No
  current unit switch occurred. A legitimate alternate equal-factor unit scene
  was not demonstrated; mutated negatives are not positive unit models.
- Post-final2 layer probe separately showed default-layer equality and detached
  supported-property re-reads, with real/bogus controls. Handle/ref-count still
  throw. Distinct-layer identity and state-change discrimination remain unproven.
  Post-test evidence is not inserted into immutable final2 manifests.

## Retained limitations and next gate

1. A calibrated specialized LayerProperties identity/state reader is required;
   do not omit the layer to force initial success.
2. Complete supported native mesh metadata, specified normals, controllers and
   dependencies must be comparable or conservatively refused. Current generated
   replay deliberately refuses `INCOMPLETE_REPLAY`, even on equal known baseline.
3. After repair, create a fresh artifact/run and explicit one-use lease after a
   fresh scene read. No automatic re-arm of Main03's retained POISONED registry.
4. Execute authentic F01 and independently measure grid/active topology, physical
   direction, openings/through-void, bounds, thickness, area, volume and evaluated
   counts, then three actual clean NOOP replays and edit/collision controls.
   Capture still lacks evaluated polygon loops/count and historical grid unless
   separately observed: absent evidence remains INCOMPLETE.
5. Assembly integration, independent poly QA profile and broader F02–F05/F08
   gates remain later work. Original P2's 21 skips were not rerun/cleared here.
6. Publication has bounded Windows no-clobber new-directory commit and 2MiB pair
   ceiling; input/output snapshots detect observed drift under controlled local
   single-writer assumptions. No arbitrary-race, whole-system lock, crash durability
   or automatic recovery guarantee is claimed.
7. Preserved F01 `input-lock.json` contains an earlier contract hash; other eight
   entries match. This historical author lock is not silently upgraded to a current
   nine-file lock. Main03 manifest correctly binds the actual tested contract/modules.

## Preservation and operations

Verified pre-edit ZIP/inventory covers 531 preexisting files. Independent current
comparison found none missing: only CHECKPOINT, PLAN and the prior P3 design doc
changed; other528 bytes remain identical. Original P2 four source hashes, 49
example/fixture files, package SHA and HEAD are unchanged. HEAD remains
`7951e3f584be83e7655072a11bb193c1982128fe`.

No reset/save/AutoBackup access, git commit/reset/checkout/clean, material/export,
installer/archive/global-copy update occurred. Final scene is unnamed mm/1,
objects0/selection0, saveRequired=true from temporary operations. POISONED Main03
lease intentionally retained for diagnosis. User's necessary-Max permission remains
valid; it is not permission to erase unrelated data. Post-test documentation and
new evidence publication must be recorded separately from the immutable test run.
