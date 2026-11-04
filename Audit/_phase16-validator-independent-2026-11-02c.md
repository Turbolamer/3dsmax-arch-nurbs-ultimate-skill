# Phase 16 P2 — independent validator audit, 2026-11-02c

## Verdict and limits

**Not accepted.** The latest complete run of the corrected harness executed
26 tests OK on frozen validator `f49a...` / helper `d8d1...`, but the live
validator changed during that run to `ed9e...`; the harness exited **1** as
designed. A complete rerun against the eventual settled pair remains mandatory.
Earlier on `f49a...`, two harness assertions failed because `1e100` was
rejected by G-7 before G-93 could run: parser **masking**, not targeted G-93
evidence. The corrected harness targets G-93 with `10000.0` and records the
`1e100` case separately. None of this is P2 acceptance.

This is an offline static-input audit. The synthetic wall is `specs/fixtures/poly-shell-input/walls.json`;
the assembly echo is a modified copy of `examples/assembly.json`, not a produced poly
assembly. No Max, builder, installer, real project geometry or original fixture was
modified. `G-95/G-98/G-99/G-100` are **SKIP**, as is poly `G-96` without a real
manifest. No SKIP is counted as proof of a model, output, formula, or runtime safety.

## Reproduction and hash discipline

From the repo root:

```text
python -B Audit/test_phase16_validator_independent.py -q
python -B Audit/test_phase16_validator_independent.py FourHandoff -v
python -B Audit/test_phase16_validator_independent.py Ledger.test_derived_conflict_annotation_matches_its_actual_input -v
python -B Audit/test_phase16_validator_independent.py StrictJSON -v
```

Each run uses isolated temporary copies; it snapshots the three actual Python
dependencies, sets `PYTHONPATH` to that snapshot, hashes every snapshot before and
after each CLI call, prints each control/negative and its gate status, hashes the
workspace during calls, and hashes originals/fixtures at end. A changed workspace
does not alter a frozen execution, but causes the harness to exit 1: **do not
call the run a clean final-tree pass**. All assertions are contract tests, not
expected failures. The harness is independent of validator imports and of the
other test harnesses. Output includes `SOURCE_HASHES`, each `PROBE`, and
`SOURCE_HASH_CHANGES`; its `failures_first20` is explicitly capped, while assertions
inspect the full JSON.

| Run | Validator SHA-256 snapshot | Helper SHA-256 snapshot | Observation |
|---|---|---|---|
| Initial live CLI | `a99892acb1544ea8bb7fd5930a928164039a5e9f924bc0a8df5b4c63e755ee52` | `455a83e7908200f37892247ce524f16248aaf7b14c1d0ce76dc906ca90d771b9` | Changed mid-call to `9fe0b565284124b441309bef9e36ffe5077e81e06ecc47adc3883f191080cd50`; remaining calls guarded, suite invalidated. |
| Second live CLI | `9fe0b565284124b441309bef9e36ffe5077e81e06ecc47adc3883f191080cd50` | same | Before second change, bad conflict crossref and bad registry path still produced wall G-10/G-93 PASS; draft massing also yielded both PASS. Validator then changed to `89de5a8bcffe9465f9ef96163279ee08b2ac46c37b351b6e16e8132c8ce91f8e`; suite invalidated. |
| Full frozen snapshot | `e4fdb9966867097a454f1f3b17e63fc1bf6301571710afe5421fd18fad8e53eb` | same | 20 tests, **9 failing subtests**, including three duplicate-status acceptances, registry cyclic control and an overly strict harness requirement for a G-10 row; original source hashes unchanged. Harness expectation for missing G-10 was corrected to allow G-93 FAIL. |
| Frozen handoff controls | `61320d1d04cc15ac265309d1b73c7c8fffd77ef341dbfb7864ebab5715596d04` | same | 2 tests OK, but historical registry control cyclic; separately calibrated acyclic negatives target the actual bad path/direction. Workspace hashes unchanged. |
| Intermediate live edit | `97e4672a2ede0380b7e228975b444406e21b8c5dc597e49fd9ab13f49e24692b` | same | `IndentationError` line 13371, no behavior test possible. Transient edit, **not a claim about later source**. |
| Full frozen snapshot | `3ede42004d2e791ccce8b03699db7bfe0ab95c024afd8afd79c5c9290ed438cf` | same | 24 tests, 3 failing subtests: `status` duplicated in assumptions/dimensions/conflicts silently accepted. Live validator changed to `a64388ec34796fadd8e540d38f7f2e8973906a65d1cac924ec0bdd4ab66d1ee1`; result is snapshot-only. |
| Full frozen snapshot | `a64388ec34796fadd8e540d38f7f2e8973906a65d1cac924ec0bdd4ab66d1ee1` | same | **24 tests OK, no unittest skips; exit 0 and `SOURCE_HASH_CHANGES {}`.** This predates the later conflict-annotation test and later source edits. |
| Full frozen snapshot | `3e35eedc47ac3b545fe53267553cec0fddd47b21d5d971379746e23df3822c5e` | same | **25 tests OK**, but harness exit **1**: workspace validator changed to `716dbcca90fca1a81ee2d1346bb95ad41f092470055c19d59f41e675b68b899f` and helper changed to `3a3eea494be158ace9405c4549835132668ba8fed12da94ed65739bd0cb43f80`. Full final-tree rerun required. |
| Full frozen snapshot, earlier harness | `f49a6fa97f440511ed9e85fda33710888d969f84d6b532f37fe1817403ba805d` | `809313752bbd78b28c3843188499809809b53f951d4e616804a986f73b6fc23d` | 25 tests, **2 failed subtests**: finite `1e100` rejected by G-7 exact-integer bound before G-93 (not silently accepted). `SOURCE_HASH_CHANGES {}`; exit 1. The other tests completed. |
| Corrected `NumericAndPartial` selector | `f49a6fa97f440511ed9e85fda33710888d969f84d6b532f37fe1817403ba805d` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` | **4 tests OK**, exit 0 and `SOURCE_HASH_CHANGES {}`. `10000.0` reached G-93 FAIL; `1e100` recorded as parser-masked G-7 FAIL. This is a selector run, not a full-suite rerun. |
| Corrected full frozen snapshot | `f49a6fa97f440511ed9e85fda33710888d969f84d6b532f37fe1817403ba805d` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` | **26 tests OK, zero unittest skips**, but process exit **1** because the workspace validator changed during the run to `ed9e64dd323441dd9cf67a4bc6ecb1da4040a8a71ebaa863c57e183976162356`. Helper and fixture hashes stayed unchanged. The newer validator was not tested by this run. |

`scripts/curve_gen.py` remained `4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c`.
The full test run prints hashes for **all** `examples/` files and the input fixture;
in the last run their end hashes matched the start. In particular the wall input was
`b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93` and
`examples/components_registry.json` was `2318898ca6c6cba3c67659222214bd5ff0f054723867c6ee4a6bfa839f39eb76`.

## Four handoff mutations and masking

The following table describes the `a643...` / `3e35...` snapshots, **not** later
edits. Each case starts from a separately saved same-source control. `—` is no
wall G-10 row, not PASS or SKIP. G-31 `FAIL+SKIP` means separate rows.

| Selected `walls.origin_inputs`; one mutation | Control | Mutant | Interpretation |
|---|---|---|---|
| `structure.x_bay_cm`; assumptions cross-reference index 3 `C-003` → `C-999` | rc 0; G-31/G-10/G-93 PASS | rc 1; G-31 FAIL+SKIP, wall G-10 —, G-93 FAIL, G-92 SKIP | Bad ledger is detected directly by G-31; wall PASS is blocked, but G-93 is broad source-eligibility rejection, not a separately isolated graph calculation. |
| `components[0].size_cm`; registry `derives_from` → `NO_SUCH_FIELD` | rc 1, G-93 FAIL on existing cycle | rc 1, G-93 FAIL explicitly mentioning `NO_SUCH_FIELD` | **Control is not clean**; do not count return code as a discrimination. Separate acyclic control below. |
| same input; registry `origin_inputs` → `wall_runs[0].thickness_cm` | rc 1, G-93 FAIL on existing cycle | rc 1, G-93 FAIL explicitly naming backward path | **Control is not clean**; do not count return code as discrimination. Separate acyclic control below. |
| `sections[0].points_cm`; massing `locked` → `superseded` | rc 0; G-31/G-10/G-93 PASS | rc 1; G-31 SKIP, wall G-10 —, G-93 FAIL, G-92 SKIP | Detected transitive eligibility issue, via NURBS `origin_inputs` `elements[8].z_range_cm`. Independent draft mutation gave same statuses. |

The historical registry is **actually cyclic**, not merely suspected:
`examples/components_registry.json:110-115` says component 0 size derives from
`components[0].parameters`, while lines 117–151 say parameters 0/1's source,
value, and units derive from that same size. This is an existing input defect under
an acyclic provenance contract; blindly saying the old control is clean would be
wrong. The harness makes a *temporary synthetic acyclic control only*: redirect
those six edges to existing `tolerances.linear_cm` (not a claim of recomputation).
With this control the selected size path yields rc 0, wall G-10/G-93 PASS; then
each of the two one-field mutations yields rc 1, wall G-93 FAIL naming the actual
bad field, G-31 SKIP and no wall G-10 PASS. Both reach their targeted direction/path
predicate without the old cycle masking the result. The untouched historical fixture
is preserved. A policy decision is needed on legacy cyclic provenance rather than
silently labelling it acyclic.

## Other observations: targeted checks versus masking

The rows below are from the frozen `a643...` complete run; `3e35...` also
exercised them but its workspace changed. Scope is the stated mutations only:

* A wall-local 3-node chain yielded G-10/G-93 PASS, while self, 2-node, 3-node,
  and object-to-own-descendant cycles reached **G-10 FAIL** and G-93 FAIL. G-32
  for the chain was SKIP. Missing/malformed sources and metadata each reached
  the specific wall G-10 location, not merely an exit-code failure.
* Both valid named wall-ledger controls passed. Mutating an existing wrong ID,
  owner/path, primary value, claimed path, and duplicated assumption ID was
  refused with wall G-10 FAIL and G-93 FAIL. **Masking:** the G-10 detail often
  says ledger-wide `G-11..15 or G-31 ... incomplete`, following G-12/G-13/G-14
  failure; these are fail-closed integration checks, **not proof the inner
  `_wall_ledger_binding` path/value branch independently ran**. Direct G-12
  value mismatch, G-11 duplicate ID and G-13 path failures are observable.
* Duplicate source-owner files reached wall G-93 FAIL with an acyclic unique-owner
  control; unknown roots, malformed paths, `defaults`, local-only wall paths and
  qualified origin-input paths reached wall G-93 FAIL. G-31 sometimes also fails.
* JSON on `a643...`: duplicate wall selector and duplicate nested budget keys,
  duplicated `status` independently in assumptions/dimensions/conflicts, `1e999`,
  `-1e999`, `NaN`, `Infinity`, trailing-comma syntax, and an unreferenced ledger
  overflow all reached **G-7 FAIL on the actual file**. The preceding `3ede...`
  snapshot incorrectly accepted duplicate upstream status (rc 0/G-7 PASS/G-93
  PASS). A 400-digit integer thickness reached G-93 FAIL without traceback.
* Unit-epsilon and length-epsilon upper bounds `0.001` and `0.01` respectively
  passed at the boundary; zero, negative, boolean, just-over-bound and `10000.0`
  reached the exact G-93 field FAIL. On `f49a...`, `1e100` is instead rejected
  by G-7 before G-93; this is recorded as masked, not a targeted G-93 test.
  Units `mm` reached G-5 FAIL with wall G-93
  SKIP. A partial draft with null unit epsilon stayed G-93 SKIP; zero vector gave
  G-93 FAIL, malformed additional run gave G-97 SKIP, not PASS. Flipped normal
  sign was accepted by the **static** perpendicular/unit check, not proof of
  physical direction.
* Historical no-selector route control rc 0/G-92 PASS. Unknown/conflicting/
  missing echo and orphan reference reached G-92 FAIL; mixed empty poly
  `wall_cells` reached G-96 FAIL. Duplicate parent/pipeline walls reached G-92
  FAIL for **both** `--dir` and `--file`; a single symlink reached both G-7 and
  G-92 FAIL. Symlink creation worked on this host. `--rule G-92` hid a G-93 FAIL
  but process and JSON exit codes were both 1; visible G-92 was SKIP. Draft lint
  rc 0 was incomplete, while `--build` and `--warnings-as-errors` each produced
  G-4 FAIL.
* Extra annotation edge: on the separately captured `7ed0faa8bba4b20e77e3ae739a22adef509f1ff4daef12b56d55a6239fb5252a`, a wall-derived value citing a valid but unrelated C-001 was silently accepted (rc 0, wall G-10/G-93 PASS). The following stable `3e35...` snapshot reports both the actually matched C-006 control **and** unrelated C-001 as G-10/G-93 **SKIP**, rc 0. This is conservative/incomplete, not proof that the annotation was checked. It must not be represented as a clean fully validated declaration.

## Remaining risks / required rerun

1. Validator and helper were edited during the last run: repeat the complete harness
   and all orchestrator regression suites on the actual settled tree, inspect the
   printed hashes and require no changes. Compare new behavior, do not infer it.
2. Valid wall-local conflict annotations are currently left SKIP by the `3e35...`
   implementation; verify the eventual policy and tests. Exit 0 alone is not PASS.
3. Full formulas, correctness of actual source evidence and outside/inside direction
   were never measured. P3 builder, real output fixture, manifest and runtime QA
   remain absent; `G-32`, `G-95/G-98/G-99/G-100` SKIP where applicable.
4. The suite samples many but not all provenance graphs or geometry combinations;
   the G-82 spatial helper, legacy builder compatibility, output atomicity, original
   acceptance suite's real-output skips, package installation, and live Max gates are
   outside this audit. Do not turn a 25-test success into P2 acceptance.
