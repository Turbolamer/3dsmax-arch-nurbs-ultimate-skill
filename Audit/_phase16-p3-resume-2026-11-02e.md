# Phase 16 P3.1 — handoff, 2026-11-02e (host 2026-11-03)

## Gate and immediate resume

**Main decision: P3/P3.1 NOT ACCEPTED.** P0/P1 and bounded OFFLINE P2 acceptance stand.
Four new production modules exist and have settled offline tests; no accepted current
wall, full F01 QA, clean NOOP, route deployment or independent poly QA profile exists.
Necessary Max permission remains explicit and valid; do not resurrect the inherited ban.
Use maximum disjoint delegation, but **only main performs live Max**, short sequential
calls with fresh guards and exact ownership. Do not bypass baseline, drop unknown state,
auto-rearm/erase the POISONED lease, reset/save/clear dirty state or access AutoBackup.
No installer/archive/global-copy update, commit/reset/checkout/clean; materials/export excluded.

Read `CHECKPOINT.md`, `AGENTS.md`, `PLAN.md` §4.0d and
`Audit/_phase16-p3-contract-2026-11-02e.md` first. This handoff supersedes the old 02d
"P3 not implemented" and the unfinished status draft, **not their historical evidence**.

## Main's settled OFFLINE result — not author counts or live acceptance

Coordinator decision and verification: [coordinator report](_phase16-p3-coordinator-verification-2026-11-02e.md).
Independent retained-evidence review: [final2 review](_phase16-p3-final-run-review-2026-11-02e.md).

Actual command recorded in `Audit/phase16-p3-final2-2026-11-02e/run.json`:
`C:/Python314/python.exe Audit/run_phase16_p3_settled.py --out Audit/phase16-p3-final2-2026-11-02e --unique-out`.
Per-suite subprocesses use `-B`; raw stdout/stderr, commands and hashes are retained.

| Actual suite suffix (`Audit/test_phase16_p3_*.py`) | Methods | Final raw result |
|---|---:|---|
| builder | 34 | OK / exit0 |
| existing_output_review | 7 | OK / exit0 |
| independent | 22 | OK / exit0 |
| inputs | 38 | OK / exit0 |
| oracle | 65 | OK / exit0 |
| publication | 42 | OK / exit0 |
| runtime | 42 | OK / exit0 |

**7/7 suites, 250 observed methods; no SKIP/xfail.** The 307-entry file maps in
`hashes-before.json`, `hashes-after.json`, `hashes-at-process-exit.json` are identical;
`snapshot-verdict.json` has no drift/baseline problems, `process-exit.json` normal_end=true.
HEAD unchanged: `7951e3f584be83e7655072a11bb193c1982128fe`. Four accepted P2 source hashes,
49 legacy fixture paths and `.skill` bytes remain unchanged. Recorder stays
`acceptance=NOT_ASSESSED`, `complete_phase16_or_p3=false`; zero exit is not runtime acceptance.
The first `Audit/phase16-p3-final-2026-11-02e/` stopped after 3/7 suites on status-draft
doc drift: retain it unchanged as historical failure, not the final stable result.

Final tested **new production** SHA-256 (read from FINAL2, not author reports):

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12 scripts/wall_surface_inputs.py
bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15 scripts/wall_surface_runtime.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
```

Repairs actually covered include combined <=2MiB publication before staging (original
independent protective test22 now OK) and initial/late existing project output refusal.
Runtime catch-argument and read-only `freeze` helper-name faults were repaired before
Main03; keep the previous raw failures, not a claim that old artifact bytes now compile.

## Authentic artifacts and actual live stop

Input-only F01: `Audit/phase16-p3-f01-input-2026-11-02e/`; authority source resolution
is **process-CWD-relative**, no fallback (run from repo root). Physical G.1 source was
independently reviewed; source hashes/geometry predictions are not measurements.
Oracle: `Audit/phase16_p3_oracle.py`; measurement tools are in
`Audit/phase16-p3-measurement-2026-11-02e/`, not deployed runtime poly QA.

**Historical F01 lock:** preserved `input-lock.json` records earlier contract SHA-256
`25a017893a2b42bfa5cd22539a6f8ff8e55d8a0dfc2ef4f92d10cc2c2b934aca`, not FINAL2's
`4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f`.
The other eight lock entries match; this is historical metadata, **not a current full
nine-file lock**. Do not rewrite it. Main03's actual manifest correctly binds the
tested current contract and all four tested sources; no misbound pair or run drift follows.

Main03 files remain in `Audit/phase16-p3-main-build-2026-11-02e/Main03/`:

```text
59aa9741db9a40a8c593623e898fa956a4d061781bc695d30b5306b0b3e6565b published/wall_surface.json
91274ffbb1cb9491c6b5fd511ceb238346f45434e56c2d6b467753a7cbdaaf28 published/wall_surface.ms
825707e3bec8ec3efa48b971a442bd2941379ea5b1121c1871572182aabb6a61 main_only_arm.ms
c09d122744cb2475fd8c5679e7797026b9a5e905a44e6e3a8fafddc23324597c held_pair_filein.ms
```

`Audit/_phase16-p3-main03-live-result-2026-11-02e.json`: actual reviewed/read-held
emitted wall loaded after explicit arm; baseline threw **LayerProperties MixinInterface
cannot convert to MaxObject**. Exact attempted node cleaned, objectsAfter=0, external
witness unchanged, lease retained **POISONED**. Registry key:
`__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7`.
`Audit/_phase16-p3-live-final-controls-2026-11-02e.json`: same authentic pair actually
refused spent/poisoned lease without implicit recovery, same witness/state and 0 nodes.
This is safe refusal, **not clean NOOP/idempotent success**. Three actual unit negatives
hit targeted guards unchanged; mutated equal-embedded-factor/type artifacts are negative
controls, not legitimate alternate-unit positive models. Final recorded state before
later probe: unnamed, mm/1, 0 objects/selection, saveRequired=true, lease POISONED.
Re-read actual state; never infer current cleanliness from this historical census.

### Post-FINAL2 evidence — not in the immutable tested manifest

Main subsequently fileIn-ed
`Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-single-node.ms`, which wrote
`Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-evidence.txt`.
The actual response and final snapshot are retained in
`Audit/_phase16-p3-post-test-layer-and-scene-2026-11-02e.json`.
Despite its original prepared-candidate header, the retained actual rows show self,
repeat and default-layer equality true in both directions; detached name/bool/float/
color property reads repeat equal; real/bogus property controls discriminate.
`getHandleByAnim` and refs-count still throw for MixinInterface, dependents undefined.
END records objects=0/cleanupOK=true/dirty=true. This helps a specialized reader but
**does not prove unique layer identity, different-layer discrimination, mutation detection
or full metadata/dependency equality**. Do not add this later file to frozen FINAL2 hashes.

## Next work — preserve fail-closed semantics

1. Main fresh read-only snapshot plus name/path/units/scale/dirty/selection, and read-only
   review of the exact retained lease/witness. No automatic rearm/removal/adoption by name.
2. Disjoint source/review/test ownership; main calibrates a specialized bounded layer
   readback/comparison policy using positive/negative controls. Resolve native/specified-
   normal metadata, controller descendants and permitted dependency graph before allowing
   replay; order cheap unsupported-state refusal before evaluated geometry. Missing readers
   stay unsupported, not an absent-value equality or a reason to omit required state.
3. Freeze new bytes and retest; use a **new** artifact run/explicitly reviewed lease protocol,
   never overwrite/retry Main01–03 in place. FileIn actual hash-checked output, capture real
   F01 and independently assess direction/area/volume/void/topology/bounds/census/stack.
4. Only after completeness is proved: three actual clean no-op replays and discriminating
   geometry/transform/material/stack/ownership/collision negatives preserving all edits and
   exact neighbors; failure cleanup with residual reporting. Current runtime deliberately
   refuses `INCOMPLETE_REPLAY`; do not remove that barrier merely to obtain green output.
5. Original **21 P2 skips remain**: authentic later pipeline/poly-QA evidence is needed,
   not synthetic echoes. F02–F05/F08, full F06/F07 and integration/QA/close-out are not done.

## Preservation / publication boundary

All pre-P3 531 inventoried files were preserved in the verified ZIP referenced by
`Audit/_phase16-p3-preservation-2026-11-02e.json`. Pre-final read-only comparison found
none missing and only three old docs changed (`PLAN.md`, `CHECKPOINT.md`, old P3 proposal);
other 528 and HEAD matched. Preserve all old/new artifacts and failure evidence.
**This handoff and current PLAN/proposal edits are post-FINAL2 publication**. Main must
record their separate before/after publication hashes; they were not silently tested by
FINAL2. Do not rewrite old manifests or change the preserved status draft. No installation.
