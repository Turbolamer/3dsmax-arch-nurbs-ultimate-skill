# Phase 16 P3 — inherited evidence and authentic-fixture entry review

Date: 2026-11-02. **Read-only review except for this new report. No accepted P2 tests were rerun; no Max/MCP, installer, archive, installed-copy, AutoBackup or Git operation was performed.** Ownership is this file only. This report is a requirements/evidence review, not P3 implementation or acceptance.

## 1. Entry decision and inherited boundaries

**P2 stands ACCEPTED in its bounded offline scope.** The coordinator decision is in `CHECKPOINT.md:30-101`; the execution record is `Audit/_phase16-p2-verification-2026-11-02d.md:158-251`, independently reviewed in `Audit/_phase16-p2-final-evidence-review-2026-11-02d.md`. Those reports, not a new run by this reviewer, establish the accepted snapshot: 20 scripts executed, all exit 0, 85 recorded hashes unchanged, 21 original-harness skips and one independently exposed expected failure. Neither qualifier is a PASS. Do not reopen accepted P2 merely because produced/runtime evidence belongs to later work; changes to accepted source/contracts do require proportionate new verification.

Carry forward these distinctions:

- **Input eligibility is not source truth.** Strict JSON, ledger/path/value joins and scoped formula checks do not establish that supplied source content says what is claimed, that an arbitrary wall-local formula is correct, or that the chosen outward sign is physically right. Unknown reached upstream formulas remain incomplete/build-refused; unproved wall-local formulas remain explicitly scoped G-32 SKIP. Do not promote them by copying declarations into a manifest.
- **No new production wall geometry was accepted.** P1 F01 is a measured spike, not an integrated production emitter. P3 must define the supported subset and output contract, then execute and independently measure the emitted route. F02–F08 and later QA/integration are not inherited passes.
- **Filesystem guarantees are bounded.** P2's builder recovery protects named recovered I/O/substitution cases; it is not crash-atomic pair publication, an arbitrary-race proof or immutable locking. Scaffold staging is per file, not project rollback; historical non-wall `--force` overwrites remain. A new emitter must state its publication/recovery policy and preserve foreign/authored or conflicting output rather than assuming P2 solved every race.
- **Legacy stays real and separate.** The three historical projects retain tested offline emitter parity; invalid/lossy JSON and REVIEW/unsupported spatial coverage intentionally refuse. No-cut is NOT_APPLICABLE, not coverage PASS, and the old thick-wall volume heuristic is limited. Keep legacy cells, hidden-host Mechanism A and zero-modifier G-81 scoped to legacy; do not impose that stack or its representation limits on poly.
- **Operational authorization is separate from acceptance.** The latest user permission in `CHECKPOINT.md:6-25` supersedes the inherited blanket Max ban for the coordinator's necessary P3 work. A fresh read-only scene snapshot plus actual units/state is still required; the old zero-object snapshot proves neither present state nor units/path. This review's explicit no-Max assignment remains in force. Preserve user work, do not touch declined AutoBackup files, do not install unfinished methodology, and keep materials/export excluded.

The relevant standing driver rules remain: never hand-edit builder output or widen tolerances/drop data to silence a failure (`agents/max-orchestrator.md:165-176`); an emitted script is not done until `fileIn` and independent measurement (`:9-14,349-374`); QA is read-only emit → collect → assess, not a builder (`:376-415`). `AGENTS.md:172-179,248-265,288-326` additionally keeps live probes in the coordinator, calls short/bounded, modifier additions at most five per call, and forbids the measured `formattedPrint`/20-stack crash paths. Ownership must exceed a name prefix: a matching name alone does not prove a node was created by this emitter or is safe to replace.

## 2. What P3 itself must produce and prove

`Audit/AGENT_PLAN_poly_surface_shell.md:310-322,473-491` assigns P3 the S4w emitter `scripts/build_wall_surface.py`, its actual `wall_surface.json` and `wall_surface.ms`, pre-publication self-checks, a scene-unit mismatch refusal before mutation, safe owned-node replay, and **live** loading/measurement. `references/07-spec-grammar.md:2977-3012` is the accepted static/output boundary; the older design sketch's blanket description of every gate as static does not supersede it.

Required P3 evidence, distinct from later integration:

1. **Explicit supported locked inputs.** Consume `walls.json`, `dimensions.json` and the actually used provenance/upstream dependencies without inventing geometry, epsilons or source semantics. State/refuse unsupported cases. An empty draft downstream assembly or not-yet-emitted manifest must not become an impossible prerequisite for building otherwise valid locked wall input (`07-spec-grammar.md:3007-3011`).
2. **Actual generated pair, traceable to an actual run.** Retain invocation, source/input identity, generated bytes/hashes, self-check result and the exact absolute script path used for `fileIn`. This is recommended external provenance evidence, not a claim that the original harness authenticates generation or already defines these metadata fields. A fixture brief may be hypothetical if labeled as such; authenticity here means genuine production-builder execution, not inventing evidence about the user's building.
3. **Defined per-run/return manifest.** Declare the node mapping, reference inner face, outward displacement, expected stack, volume and bounds, plus expected topology and budgets. Report grid polygons, active base polygons and evaluated triangles separately, never substitute one for another or silently optimize. Doors touching the base change the exterior boundary; windows produce interior loops. Do not make expected values from the emitter count as independent observations.
4. **Independent live comparison.** Load the actual generated script, inspect actual scene nodes/stacks/geometry, compare physical dimensions/bounds/volume to independently derived expectations, and retain raw observations. Direction must be checked separately: P1 established that reversed winding can preserve volume. Unsupported enclosure/corner claims remain unproved rather than implied by per-wall closedness.
5. **Safety and replay controls.** No scene reset; reject scene-unit mismatch before mutation; refuse foreign/same-name collisions and preserve user-edited owned nodes under the defined ownership/fingerprint policy. A real second `fileIn` must be compared by node set and geometric state, not a loop count or self-reported replay counter. Build/measure/cleanup only owned test nodes under bounded coordinator calls, retaining evidence before cleanup. The full F07 fixture gate is still later work, not automatically discharged by this requirement list.

Expected script stack checks are route-specific: poly may intentionally use `addModifier`; the legacy emitter's absence of modifiers is not the new target. Do not put MAXScript implementation class names into domain input specs. Do not claim JSON lint has observed G-95/G-98/G-99/G-100; those remain separately scoped artifact/runtime obligations until actual appropriate evidence exists.

## 3. Exact original harness fixture contract and blind spots

Inspected source: `Audit/test_phase16_p2.py`, not a rerun. `poly_fixture()` at lines 166–189 accepts `--p2-fixture` as a project root, a `pipeline` container or the pipeline itself; resolution requires `dimensions.json` (lines 94–98). Each negative uses a private clone. Its positive guard requires:

- Existing `walls.json` and `assembly.json`, **both `status: locked`**, both selecting exactly `poly_surface_shell_v1`.
- Both `wall_cells` and `opening_cuts` **absent** from assembly, not present as empty arrays.
- Whole-pipeline lint exit 0 and an actual G-92 PASS. Dependencies must therefore resolve within the supplied self-consistent pipeline.

**This is not production authentication.** The guard does not run a wall builder or S5, require an existing/generated/validated `wall_surface.json`, inspect `wall_surface.ms` or `assembly.ms`, authenticate output hashes, or observe Max. The manifest-missing test even conditionally deletes the manifest only *if* it exists. Consequently a handcrafted locked echo can satisfy the shape guard while leaving the real obligations absent. Do not use that weakness to clear skips. Do not manually relabel the input adapter's draft assembly, strip legacy arrays from historical output and call it produced poly, or fabricate a manifest/request.

The genuine supplied pipeline must contain wall artifacts produced by S4w and an assembly produced by the implemented poly S5 route, with `wall_ref` exactly `wall_surface.json` (grammar §8.5.9/§9.11). Keep generated scripts and derivation evidence as well as JSON. A leftover legacy `assembly.ms` is not poly output even if the JSON was edited to pass the guard.

### The 20 produced-fixture skip events

| Events | Original assertion | Authentic evidence/fixture requirement |
|---:|---|---|
| 1 | `test_locked_poly_does_not_run_legacy_wall_rules`, lines 415–422 | The generated poly pipeline reports G-76/G-77/G-82/G-83 and G-81 as visible SKIP, never PASS/FAIL for legacy applicability. This alone does not prove no `WAL_` scene nodes exist. |
| 3 | `test_locked_poly_route_mismatch_fails_g92`, lines 454–463 | Starting from the real positive assembly, mutate its selector to legacy, unsupported and null; each must give G-92 FAIL and exit 1. |
| 2 | `test_locked_poly_rejects_legacy_tables`, lines 465–476 | Add `wall_cells: []` or `opening_cuts: []` to a copy of the real assembly; each must exit 1 with G-96 or G-1 FAIL. |
| 1 | `test_locked_poly_manifest_missing_is_explicitly_incomplete_or_fail`, lines 478–493 | Remove the genuinely generated manifest from a copy, run `--build`, require visible manifest-related FAIL/SKIP/INCOMPLETE, no manifest-related PASS and no G-96 PASS. Existing assertion permits exit 0 or 1: **passing this negative is not a complete production build verdict**. |
| 13 | `test_locked_wall_negative_mutations`, lines 495–580 | Run the existing mutations against the real positive produced pipeline, with the fixture features below. Each must exit 1 and hit its specified rule, without internal errors. The earlier draft adapter is input-only evidence, not a substitute. |

To avoid feature-dependent skips within the 13 mutations, order the real positive fixture deterministically so that:

- `wall_runs` has at least two real dict runs with distinct `id`; the first has `thickness_cm`, `base_z_cm`, `top_z_cm`, `block_id`, `contour_ref`, `outward` and `topology_budget.max_grid_polygons`.
- Top-level `numeric_epsilon_cm` exists. All three topology ceilings are valid and sufficient for the actual generated fixture, not merely schema-valid declarations.
- `openings` has at least two real dict entries; **the first two belong to the same run**, both have two-element `u_range_cm`, and the first has `sill_cm`/`head_cm`. They must be initially legal, non-overlapping and within that run. Later opening duplication is a deliberate negative, not something to pre-bake into the fixture.
- Existing input contract/provenance, contour joins, heights and budgets remain clean in the unmutated pipeline; unrelated baseline faults must not mask the intended negative.

Specified mutation targets are G-93 for duplicate run ID, zero thickness, collapsed height, missing block, invalid contour, zero outward, zero numeric epsilon, reversed opening interval, collapsed sill/head and missing opening run; G-97 for negative grid-polygon budget; G-94 for outside opening and overlapping first-two opening intervals. The source reads these exact fields; a one-run-only spike cannot clear the duplicate-run coverage, and a fixture with fewer than two openings on the same run cannot clear the overlap coverage.

## 4. The remaining QA skip is a different deliverable

`test_poly_qa_without_runtime_observations_is_incomplete` (`test_phase16_p2.py:424-452`) requires **both** `--p2-qa-project` and `--p2-qa-request`, with `--require-p2`:

- A real project root containing `specs/pipeline/qa.json` with `profile: poly_surface_shell_v1`.
- An existing valid matching request with the same profile and **non-empty** `expected_check_ids` and `observations`, emitted by the implemented QA workflow, not handwritten records invented to meet the guard.
- The harness intentionally supplies `{"records": []}` to `qa_check.py --assess`. It requires exit 1, a written `qa-results.json`, verdict not PASS and `summary.incomplete > 0`. A generic FAIL with incomplete count zero does not satisfy this test.

This is a missing-evidence negative; a real request lists observations to collect, not invented measured values. Satisfying it does **not** prove that runtime collection or positive poly QA passed. Full direction/solid/topology/units/replay evidence still needs actual independent collection and assessment.

## 5. P3 versus later integration — do not fake an all-green kickoff

The accepted plan explicitly distinguishes work: `PLAN.md:314-318` reconciles its gate-oriented table with the detailed numbering. In `Audit/AGENT_PLAN_poly_surface_shell.md`, **P3 is S4w emission/live measurement**, **P4 is route orchestration/S5 integration** (also mapped in the per-file table at lines 576–578), **P5 is poly QA**, and P6 is the full fixture/close-out set. Thus P3 alone must deliver the genuine wall-artifact foundation, but cannot honestly clear all 20 produced-pipeline skips while poly S5 still refuses, nor clear the QA skip before the real profile/request exists. Either retain those explicit NOT RUN boundaries until their owning stage, or obtain an explicit coordinated scope extension; do not silently turn output mocks into integration evidence.

When those authentic artifacts exist, the unchanged original harness can be run with `--require-p2 --p2-fixture <actual-produced-project-or-pipeline> --p2-qa-project <actual-qa-project-root> --p2-qa-request <actual-emitted-request> --fail-on-skip -v`. This is a **future gate template, not a command executed by this review**. Preserve its raw per-test output and report any remaining skips; an exit-0 shape check alone is not authentication or live acceptance.

`Audit/test_phase16_p2_cases.py:8-17,122-147,235-258,577-619` is deliberately synthetic contract coverage. Its draft baseline, configuration-only locked echo, input arithmetic and runtime SKIPs are valuable bounded controls, not candidates for relabeling as production. `Audit/test_phase16_input_fixture.py:26-43,46-60` likewise overrides the original fixture helper with a draft assembly and absent wall artifacts to exercise exactly 13 input mutations. Keep that evidence honest and separate.

**Disposition:** P3 may proceed under coordinator ownership and the latest explicit user authorization. Preserve the accepted P2 result and its limits. Require authentic emitted artifacts plus independent live P3 evidence; defer the original produced-assembly/QA skips to their real integration owners instead of laundering them with fabricated echoes. No P3 deliverable or new test/live PASS is asserted by this report.
