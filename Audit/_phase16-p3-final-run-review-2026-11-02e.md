# Phase 16 P3.1 — independent final2 evidence review

Reviewed on host date **2026-11-03**; filenames retain the coordinator's `2026-11-02e` run identity.

## Verdict

**OFFLINE PASS BOUNDARY ONLY. P3 / P3.1 NOT ACCEPTED.** The settled final2 run supplies current, hash-stable evidence for the seven executed offline suites, including the previously failing combined publication limit and existing-output refusal controls. It does not overcome the actual Main03 initial-baseline failure, implement a successful clean no-op replay, supply the missing independent full F01 measurements, or accept route assembly/poly QA integration.

This is an independent review of retained evidence, not a new suite run. No Max, installer, archive/global-copy update, Git operation, fixture/source/test edit or rerun was performed. **Only this new report was written, after main explicitly announced final2 completion.** It was not present in the frozen run and must be recorded as separate post-test publication. Main's final post-publication manifest is a later responsibility, not supplied by this report.

## 1. Exact run and raw-log disposition

Reviewed directory: `Audit/phase16-p3-final2-2026-11-02e/`.

- Recorder argv in `run.json`: `C:\Python314\python.exe Audit/run_phase16_p3_settled.py --out Audit/phase16-p3-final2-2026-11-02e --unique-out`; Python **3.14.4**. Began `2026-11-02T21:29:19.444323+00:00`.
- `snapshot-verdict.json`: timestamp `2026-11-02T21:33:34.636801+00:00`, recorder exit **0**, **7 discovered / 7 executed**, no NOT_RUN/missing required suite/nonzero execution, `source_drift: []`, `baseline_problems: []`. Its `acceptance: NOT_ASSESSED` is intentional recorder non-decision, not stage acceptance.
- `process-exit.json`: `normal_end: true`, timestamp `2026-11-02T21:33:34.806997+00:00`, again empty drift/baseline lists. Recorded HEAD is unchanged: `7951e3f584be83e7655072a11bb193c1982128fe`.
- Independently read all seven actual stderr logs and nonempty stdout; read/decoded full raw independent hash/event lines rather than relying on truncated display. All **14** stdout/stderr byte lengths and SHA-256 values match `results.json`.

| Actual suite (`Audit/`) | Raw unittest methods | Raw disposition and scope |
|---|---:|---|
| `test_phase16_p3_builder.py` | 34 | `OK`, exit 0; CLI/coordinator/authority/path/identity/emission checks, including real offline generated pairs and deliberately fake seams. Not Max execution. |
| `test_phase16_p3_existing_output_review.py` | 7 | `OK`, exit 0; actual clean public CLI plus initial/late existing JSON/MS/pair refusals, preserved bytes, `EXISTING_OUTPUT_REVIEW_DRIFT []`. Recorder uses the **default project layout**; optional `--all-boundaries` 21-CLI matrix was not run here. |
| `test_phase16_p3_independent.py` | 22 | `OK`, exit 0; actual public emissions/refusals and direct runtime/publication controls. Raw source and fixture maps equal before/after. |
| `test_phase16_p3_inputs.py` | 38 | `OK`, exit 0; input closure, required formula/provenance gates, exact snapshot use, unsupported-subset and initial/late artifact presence refusals; stdout `ACCEPTED_SOURCE_AND_SEED_DRIFT []`. |
| `test_phase16_p3_oracle.py` | 65 | `OK`, exit 0; independent analytical/checker discrimination, including missing evidence returning INCOMPLETE and synthetic malformed geometry returning FAIL. Tests explicitly label manufactured capture arrays `synthetic_test`; these are not live observations. |
| `test_phase16_p3_publication.py` | 42 | `OK`, exit 0; real Windows new-directory/no-replace publication, I/O/substitution/cleanup and combined 2 MiB controls. One non-Windows refusal is an injected platform control, not a real Linux run. |
| `test_phase16_p3_runtime.py` | 42 | `OK`, exit 0; pure planning and emitted-source assertions. Explicit unproven-metadata/replay refusal is a protective offline success, not successful scene replay. |

The sum is **250 reported top-level unittest methods**, not 250 independently proved architecture/runtime requirements. No raw `... skipped`, expected-failure, unexpected-success, failure/error block or `OK (skipped=...)` appears in these logs. All seven end in `OK`.

**Exact qualifier disposition:** independent stderr line 34 is:

```text
INDEPENDENT_P3_RESULT {"tests": 22, "failures": 0, "errors": 0, "skips": 0, "events": 131, "drift": []}
```

The recorder's `QUALIFIERS_REQUIRE_REVIEW` is triggered by the literal `skips` metadata key. It is **not a skip/xfail event**. Raw source maps contain 18 entries and fixture maps 7, equal before/after; all 131 event strings start with `PASS`. Events include repeated positives/refusals and must not be added to method counts or used as a live-coverage total. The independent source entrypoint refuses missing production modules or actual skips; it did not silently bypass unavailable modules in this run.

The previously red direct publisher test 22 now runs normally: its source still requires an exception for **two 1,126,400-byte artifacts**, both individually below 2 MiB but **2,252,800 bytes combined**, after a real small positive publication. Raw final2 line 24 reports `...test_22_publisher_direct_total_two_mib_contract ... ok`; it is neither xfailed nor skipped. Test 21 separately reaches the public CLI combined-pair boundary. Existing-output review asserts actual rejection and preserved bytes, not successful vulnerability reproduction.

## 2. Stable tested bytes, docs and preservation

Independently decoded `hashes-before.json`, `hashes-after.json`, `hashes-at-process-exit.json`: **all three `files` maps are identical, 307 entries**. There are **306 FILE entries** plus one explicit `NOT_AVAILABLE` authority-directory-relative source candidate, `Audit/phase16-p3-f01-input-2026-11-02e/Audit/AGENT_PLAN_poly_surface_shell.md`. The real source is repository/CWD-relative and present; absence of that fallback candidate is not a missing required input or newly lost file.

Before post-test publication began, every recorded file hash also matched an independent current read. Stable scopes include **17 `scripts/*.py`, 27 Phase16 test files, the oracle/recorder, 49 legacy/example files, 14 actual F01 input/evidence files, package bytes and the frozen contracts/docs**. The frozen markdown scope has 40 files and the one unavailable `.md` candidate. This is code **and documentation** stability during final2, unlike the first run.

### Tested P3 executable SHA-256

| File | Exact final2 SHA-256 |
|---|---|
| `scripts/build_wall_surface.py` | `a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878` |
| `scripts/wall_surface_inputs.py` | `5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12` |
| `scripts/wall_surface_runtime.py` | `bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15` |
| `scripts/wall_surface_publish.py` | `7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b` |
| `Audit/phase16_p3_oracle.py` | `c08a2a7759ed945eaab646104b5d60297725c84e97f107807c80e4b9a16d988a` |
| `Audit/_phase16-p3-contract-2026-11-02e.md` | `4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f` |

All four accepted P2 source hashes still match both final2 and current bytes: initializer `42401725…`, legacy builder `4f9735ff…`, validator `61605041…`, coverage oracle `d8d1e930…` (full authoritative values remain in final2 `run.json:89–94`). Independently joined the accepted P2 final manifest: **all 49 example/fixture hashes match**. Package SHA-256 remains `dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a`.

Independently checked all **531** original paths from `Audit/_phase16-p3-preservation-2026-11-02e.json`: **0 absent**. At the completed-run review cutoff, **528 unchanged**, with only the dated documentation changes in `CHECKPOINT.md`, `PLAN.md`, `Audit/_phase16-p3-design-2026-11-02.md`; inspected their actual diffs against the preservation ZIP. These changes predate the settled snapshot; they are not during-final2 drift. The original ZIP exists, SHA-256 **`8d23916992ea8072530a8ee3cd7ea78dca3c11d669665c8eede527f3c344208b`** matches, and every original ZIP member's size/hash matches all **531** original records. Original preservation is not a claim that the three current docs remain byte-identical.

**Historical F01 lock qualification:** the intentionally preserved `input-lock.json` still records earlier contract SHA `25a017893a2b42bfa5cd22539a6f8ff8e55d8a0dfc2ef4f92d10cc2c2b934aca`, whereas final2 tests contract `4e53b474…`. The other eight lock entries, wall/source/authority included, match current bytes. The earlier fixture review's all-nine-match statement was true for its earlier snapshot, not this one. Treat the old fixture lock/validation record as historical author evidence; do not silently rewrite it or claim a fully current nine-file lock. **Main03's actual generated manifest correctly records the current tested contract and all four tested modules**, so this historical metadata mismatch does not show a misbound Main03 pair or during-run drift.

Final2 supersedes the *incomplete run result*, not the bytes of `Audit/phase16-p3-final-2026-11-02e/`: the first run stopped after 34/7/22 methods because a new status-draft document appeared. Its four NOT_RUN suites and failed recorder remain honest historical evidence; no source/test/fixture failure was fabricated or erased.

### Frozen evidence file SHA-256

| Final2 evidence | SHA-256 |
|---|---|
| `results.json` | `2369b63e65dcd4f253ba7ce07c7eb396ecbaa90fa0c42d8b4900c83ae1db74a2` |
| `hashes-before.json` | `a70b949d488fb92f4afd45a16f670b963ea056c35eb4d54115abbefcd66cd16a` |
| `hashes-after.json` | `a9986f5b505b4a861a739ad42279a205c82f9a2e4d3a27bbb98eed7748b64192` |
| `hashes-at-process-exit.json` | `287a93d4ac59b47e08bd592af900787ee0acf2185c3d647d9f50664ddc58b89f` |
| `snapshot-verdict.json` | `237c81051af007d6d71f075c90383389e671e67927bf33d5ec07920a00cde32b` |
| `process-exit.json` | `5b45eeb4e83e66c3ff6c24ad4b902d86deb190cbcdbf6adbdacfec505a616bcb` |

Whole snapshot file hashes differ because capture metadata differs; their decoded **file maps**, not whole JSON bytes, are equal.

## 3. Actual Main03 live result is a blocker, not transport PASS

Read `Audit/_phase16-p3-main03-live-result-2026-11-02e.json` and `Audit/_phase16-p3-live-final-controls-2026-11-02e.json` including their actual returned wire strings. Independently hashed retained Main03 files against the approval record:

```text
wall_surface.ms      91274ffbb1cb9491c6b5fd511ceb238346f45434e56c2d6b467753a7cbdaaf28
wall_surface.json    59aa9741db9a40a8c593623e898fa956a4d061781bc695d30b5306b0b3e6565b
main_only_arm.ms     825707e3bec8ec3efa48b971a442bd2941379ea5b1121c1871572182aabb6a61
held_pair_filein.ms  c09d122744cb2475fd8c5679e7797026b9a5e905a44e6e3a8fafddc23324597c
```

All four match. The actual manifest labels predictions `offline_predictions_not_live_measurements`, status `produced_offline_unverified`; its pre-execution `live_execution: NOT_RUN` is preserved historical artifact metadata, superseded for actual execution outcome by the separate failed live record, not edited in place.

Actual request `59a61aaa30f84b129588d5ff5b7b063f` returned transport `ok=true`, but the decisive result is:

```text
P3_MAIN03_AUTHENTIC_ATTEMPT|armed=true|EXCEPTION=-- Runtime error: -- Unable to convert: <MixinInterface:LayerProperties> to type: MaxObject|leaseState=POISONED|witnessStill=true|objectsAfter=0
```

Thus the authentic pair **was loaded and failed initial baseline**. The recorded exact-attempt cleanup leaves no accepted wall; the lease remains POISONED with its exact witness. A same-pair retry actually refuses `lease spent/building/poisoned`, preserving witness/state/census; this is a **safe refusal**, not any of the three required successful no-op replays. Current runtime source also explicitly refuses `INCOMPLETE_REPLAY` for unverified specified-normal/native-metadata comparison: fixing just layer serialization cannot be advertised as completing replay.

The retained final controls separately record three targeted unit refusals with exact census/selection/context unchanged: wrong expected type, deliberately mutated type-only equal embedded factors, and deliberately mutated stored factor. The mutated cases are negative artifacts, **not legitimate alternate-unit positive emitted models**. No accepted alternate-unit/scale F01 or broad edit-detection gate follows. Final retained read-only state is objects/selection **0**, mm/**1**, unnamed scene, **saveRequired=true**, Main03 lease **POISONED**. No dirty-flag clearing, reset/save or automatic lease removal/rearm should be inferred.

## 4. Missing evidence and retained risks

1. **Full authentic F01 measurement is missing.** Direction, preserved inner face, area/volume, topology, opening clearance, bounds, census and stack have not collectively passed against an actual accepted emitted wall. Historical P1, current predictions, synthetic oracle arrays and tiny-quad calibration do not supply this evidence.
2. **Capture contract remains incomplete.** The measurement tool retains actual evaluated triangles but no independently verified evaluated polygon loops/count; the oracle deliberately keeps corresponding checks INCOMPLETE. Actual predeletion grid observation must be captured at that stage; the final base cannot reconstruct it. A short path/hash envelope is not full measurement data. Tiny smoke capture status is `CAPTURED_NOT_ACCEPTED`, with grid/polygon evidence explicitly incomplete; it is not F01.
3. **Safety/replay remain unproved.** Full native metadata, specified normals, supported controllers/dependencies and layer identity/state comparison need calibrated readback and targeted user-edit/collision controls. The narrow initial session/empty-scene lease does not claim save/load/restart durability or arbitrary scene coexistence.
4. **Filesystem limits stay bounded.** Offline tests discriminate named recoverable I/O/substitution cases and enforce 2 MiB combined publication. They do not prove arbitrary adversarial-race safety, immutable path capabilities, crash durability or hostile filesystem behavior. Source attestation/hash binding is not generic semantic proof or an authentication signature.
5. **Original P2 suite was not rerun.** Its 21 produced-pipeline/QA skip events remain their accepted historical incompleteness, neither new passes nor test skips inside these seven P3 suites. Poly assembly/QA profile and F02–F05/F08 integration remain outside this P3.1 offline result. Hash-only helper/measurement/probe trees in final2 were **not executed by the recorder**.

## 5. Post-test observations/publication are separate

After final2 completed, main reported a tiny prepared layer comparison request **`ef137e31a3aa4f5283f0d01cca72a9d5`**, elapsed **5.766 ms**, failed=false, cleanup=true, objects=0, rows=55. Independently read the new `Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-evidence.txt` (SHA-256 **`25667329c80cfac7a608023e8c1969940ee277765f1527c14bd79842bfec4bcd`**, 6,084 bytes). This new file was **not in the frozen final2 map**; it is separate post-test evidence, not during-run drift. The timing/request metadata here is main-reported; the text independently supports the observed comparisons and cleanup line.

Actual rows show `LayerManager.getLayer(0)` is `MixinInterface`; self/repeat/default/reverse comparisons true; `getHandleByAnim`/reference-count conversion throws; `refs.dependents` returns undefined. Real name/bool/float/color properties are readable and detached repeat values compare equal, while the bogus property and absent `color` are discriminated. These are **bounded default-layer observations**, not unique identity, layer edit/replacement detection, full property comparison or a repaired live baseline. Do not call the earlier conversion failure class absence, or call this probe P3 acceptance.

At a later read during authorized post-test publication, only `CHECKPOINT.md` among the frozen entries had changed; executable/test/fixture/package hashes still matched. Main has announced further PLAN/design/handoff publication after the run. Those changes, this report and any new evidence belong in the **separate final post-publication manifest**; do not alter/relabel the immutable final2 maps or say the suites executed on later docs. Endpoint hashes cannot exclude unobserved change-and-revert or arbitrary concurrent races.

**Final disposition:** retain final2 as a reviewed **offline passing boundary** on the exact hashes above, retain Main03 as an actual failed live attempt with safe bounded cleanup, and keep **P3/P3.1 NOT ACCEPTED**. Resolve/calibrate the real baseline/metadata and complete independent F01 measurement/replay gates before a new acceptance claim. No installation or unfinished-method rollout is justified by this review.
