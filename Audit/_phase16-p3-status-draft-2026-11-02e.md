# Phase 16 P3.1 — end-session status / handoff DRAFT, 2026-11-02e

**Host date: 2026-11-03; filenames retain the session label `2026-11-02e`.**
**P3/P3.1 NOT ACCEPTED. P0/P1 and bounded OFFLINE P2 acceptance stand.** This is a
draft for main to finalize after Main03 and the settled recorder, not a gate decision
or a substitute for `CHECKPOINT.md`. Only this new file is authored in this task;
`PLAN.md`, `CHECKPOINT.md`, sources, tests and existing evidence remain untouched.

## Preservation and authority

- Pre-P3 preservation: `Audit/_phase16-p3-preservation-2026-11-02e.json`, verified
  531-file ZIP at `C:/Users/Turbolamer/AppData/Local/Temp/opencode/phase16-p3-preserved-2026-11-02e.zip`.
  Draft author's read-only comparison on 2026-11-03 found **531 present / 0 missing**;
  only three preexisting files differ: `CHECKPOINT.md`, `PLAN.md`,
  `Audit/_phase16-p3-design-2026-11-02.md` (dated documentation updates). The other
  528, including accepted P2 executables, prior fixtures/evidence and `.skill`, match.
  HEAD remains `7951e3f584be83e7655072a11bb193c1982128fe`. This interim comparison
  is not the forthcoming final recorder or a claim that the three docs are byte-identical.
- Preserve all new/old artifacts, failed attempts and raw diagnostics; do not overwrite
  Main01/Main02 or repair evidence in place. Their preserved comparison is recorded in
  `Audit/phase16-p3-main-build-2026-11-02e/Main02/main01-preservation-external.json`.
- Necessary Max work is explicitly user-authorized; **only main operates Max**, with
  fresh-state guards, short sequential calls and exact ownership/cleanup. Status is
  not authorization. No reset/save/AutoBackup access, installer/archive/global-copy
  update; materials/export remain excluded. Do not install the unfinished method.

## New implementation/artifact inventory — existence is not acceptance

| Area | Files / directories implemented or authored |
|---|---|
| Public offline CLI / input / runtime / publication | `scripts/build_wall_surface.py`, `scripts/wall_surface_inputs.py`, `scripts/wall_surface_runtime.py`, `scripts/wall_surface_publish.py` |
| Direct offline tests | `Audit/test_phase16_p3_{builder,inputs,runtime,publication,oracle,independent}.py`, `Audit/test_phase16_p3_existing_output_review.py` |
| Independent analytical oracle | `Audit/phase16_p3_oracle.py` (repo-only; not deployed poly QA) |
| Authentic F01 INPUT ONLY | `Audit/phase16-p3-f01-input-2026-11-02e/` (four locked domain inputs, separate authority and retained lint evidence; not a produced assembly) |
| Measurement / execution / probes | `Audit/phase16-p3-measurement-2026-11-02e/`, `Audit/phase16-p3-execution-2026-11-02e/`, `Audit/phase16-p3-runtime-probes-2026-11-02e/`, `Audit/phase16-p3-state-probes-2026-11-02e/`, `Audit/phase16-p3-live-controls-2026-11-02e/` |
| Actual offline publication preparation | `Audit/phase16-p3-main-build-2026-11-02e/prepare_main.py`; retained Main01/Main02 pairs, plans, arm/wrappers and hash records |
| Final recording support | `Audit/run_phase16_p3_settled.py` (recorder, not acceptance) |

Contract: `Audit/_phase16-p3-contract-2026-11-02e.md`. Subset is one complete
standalone straight inner-reference wall; no assembly deployment, corners/returns,
instances, local F08 mesh or full-building support is accepted.

## Evidence separation at draft cutoff

**Author/reviewer reports, not main's final stable-tree verdict:** module owners report
offline tests (inputs31, builder34, publication42, runtime42 after its latest helper-name
repair); oracle and independent suites have their own snapshot-specific reports.
Do not sum these or credit old-source runs to final bytes. The independent suite's
original protective direct-publisher test22 failed on the OLD helper, with source drift;
its same-test repeat on repaired settled bytes is **NOTRUN** here. Source review §4
independently passed repaired helper exact-2-MiB / +1 controls; that narrower result
does not replace the original protective repeat or main's final recording.
Source review §5 separately reports 7 actual CLI existing-output regression tests OK
on inputs `5c1e3134…`; its earlier ignored-contradictory-output finding is historical
for those tested initial/late-presence cases, not silently still open or universally solved.

**Main-executed evidence actually read:**

- Entry JSON `_phase16-p3-live-entry-2026-11-02e.json`: 0 objects/selection,
  unnamed scene, mm/1, initial saveRequired=false. Later temporary controls dirtied
  the scene; no flag clearing/reset/save is claimed. Obtain fresh state before resuming.
- Identity/native-unit/registry controls and `_phase16-p3-registry-probe-2026-11-02e.json`
  establish bounded API observations, not production replay. Initial runtime probes
  include real failures despite clean transport envelopes; inspect returned diagnostics.
- `phase16-p3-main-publication-test-2026-11-02e/execution.json`: main's stable
  repeat of the OLD publication suite (39 tests per checkpoint), not repaired42 evidence.
- `_phase16-p3-f01-main-authority-review-2026-11-02e.json`: main read actual G.1,
  Y=0/outward -Y, 400×300 cm/thickness30 and authentic openings. This is synthetic
  F01 physical-source authority review, not current geometry measurement.
- `_phase16-p3-measurement-calibration-2026-11-02e.json`: actual translated/rotated
  quad confirms snapshot world-space, cleanup objects_after=0. Full tiny-quad capture
  `_phase16-p3-measurement-smoke-capture-2026-11-02e.json` exists (3516 bytes;
  base4/4/1, evaluated8 vertices/12 triangles), **not F01**. Earlier parse/GetBytes/
  Integer64-envelope faults remain evidence. Isolated corrected writer produced the
  actual 41-byte `_phase16-p3-writer-calibration-2026-11-02e.json`; exact-path repeat
  refused with ToolError, not a successful normalized error envelope. Corrected full
  measurement-envelope rerun remains **NOTRUN** in this draft.
- Main02 has an authentic actual offline artifact pair, manifest status
  `produced_offline_unverified`; `_phase16-p3-main02-live-result-2026-11-02e.json`
  records **arm compile FAIL**, argumented throw in catch, objectsAfter=0. The geometry
  pair was **not fileIn-ed**. `_phase16-p3-unit-initial-failure-2026-11-02e.json`
  records the subsequent `freeze` read-only helper-name collision, objects=0: the
  intended unit negative did **not** reach its target guard and is not PASS.

## Blockers / next handoff

1. Runtime owner repaired catch rethrows and prefixed all emitted local helper names;
   latest reported runtime `bd582b45…` / tests `242bb0c4…`, offline42 OK. These are
   author claims pending main's new actual compile/live attempt, not evidence that
   immutable Main02 now works. Preserve both failed attempts; generate a new pair.
2. Layer `MixinInterface` is readable but anim-handle/reference conversion throws;
   generic baseline comparability remains blocked. Native/specified-normal metadata,
   controller/dependency completeness also remain unproven. **Safe successful NOOP
   is not implemented**: runtime deliberately refuses `INCOMPLETE_REPLAY` even after
   observed baseline equality. Do not drop fields or reinterpret refusal as replay PASS.
3. F01's actual offline pair is still **NOT GEOMETRY ACCEPTED**. Current emitted-source
   fileIn, independent direction/area/volume/topology/void/bounds/census/stack evidence,
   targeted unit/edit/collision/cleanup controls and three real successful no-op replays
   remain required. Historical P1 and tiny calibration geometry do not substitute.
4. Original **21 P2 skips remain**; future authentic integrated-poly/QA evidence is
   required, never fabricated echoes. F01 input lint's four downstream-inventory FAILs
   and its separate SKIPs are not whole-pipeline PASS or the same 21-event ledger.

## Main-only finalization slots — deliberately unfilled

| Final record / gate | Draft value |
|---|---|
| Main03 final exact pair/arm/wrapper hashes and source closure reviewed by main | **NOTRUN** — main to insert verified record |
| Main03 actual compile/fileIn, raw bridge errors, returned diagnostics and cleanup | **NOTRUN** — no predicted outcome |
| Corrected target-specific units controls / full measurement-envelope rerun | **NOTRUN** |
| Settled recorder exact command/output directory, per-suite counts/exits/qualifiers, drift and normal-exit marker | **NOTRUN** — main to insert actual results; recorder remains NOT_ASSESSED |
| Final preservation/HEAD/source/artifact hash assessment and fresh final scene state | **NOTRUN** — interim preservation comparison above is not final |
| P3.1 acceptance / installer readiness | **NOT ACCEPTED / NOT READY** |

Main owns updating these slots and publishing the final checkpoint/plan/handoff.
No Main03 or recorder result is inferred from files appearing during concurrent work.
