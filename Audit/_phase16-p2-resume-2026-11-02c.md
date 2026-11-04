# Phase 16 P2 — third-session handoff, 2026-11-02

**Status: P2 remains IN PROGRESS, not accepted.** The user asked to stop after the
subagents finish and continue in a fresh session. This note supersedes the status
in `Audit/_phase16-p2-resume-2026-11-02b.md`, not its historical evidence. Read
`AGENTS.md`, the top of `CHECKPOINT.md`, `PLAN.md` §4.0d, this note and then the
earlier handoffs/briefs as needed. Preserve every tracked, untracked and ignored
file; no reset, cleanup, checkout, commit, installer or broad deletion is implied.

## Non-negotiable boundaries

- P0/P1 stand. There is **no** P3 `build_wall_surface.py`, poly runtime QA,
  generated poly wall manifest/script or new live acceptance. `walls.json` under
  `specs/fixtures/poly-shell-input/` is synthetic **input only**, not a produced
  assembly or a user project. Do not invent a produced poly fixture to clear a
  skip. Do not start P3 before P2 is independently accepted.
- Outward sign cannot be inferred from a facade name, winding or volume. It needs
  a physically authoritative source for the inner/outside side and a **separate**
  direction gate independent of volume. F01–F08 and all subsequent independent
  offline/live QA gates remain required before declaring Phase 16 complete.
- No Max scene call or mutation occurred in this session. The **previous**
  read-only snapshot was 0 objects; it is not current evidence. Obtain a fresh
  read-only snapshot before any scene access, never reset or delete user data.
  The user explicitly declined copying `AutoBackup*.max`: do not touch/copy them
  or alter backup settings without new permission. Materials/export are out of scope.
- `.skill` and global installed copies were not rebuilt or installed. Read
  `scripts/install_skill.py` again before any eventual installation: every target
  rebuilds the archive, global targets overwrite and prune. A read-only comparison
  during this session found 6 differing shipped files, 2 new files and 0 prune
  candidates in **each** global copy, but edits continued afterward, so those
  numbers are only a snapshot and must be recalculated. The input fixture README
  is not currently packaged with its JSON. Do not install unfinished methodology.

## Independently observed in this session — NOT final acceptance

1. At starting validator SHA-256 `a99892acb1544ea8bb7fd5930a928164039a5e9f924bc0a8df5b4c63e755ee52`
   the four provenance defects were known open. The orchestrator repeated them
   against an **intermediate concurrently edited** validator: clean synthetic
   control had no FAIL and wall G-10/G-93 PASS; bad transitive G-31 ledger,
   invalid registry `derives_from`, registry→walls back-reference, and superseded
   massing behind NURBS each produced FAIL without wall G-10/G-93 PASS. This
   observation is not a final stable-tree test. The original example registry
   has a **real provenance cycle** (`components[0].size_cm` ↔ parameter origins),
   so registry negatives need a separately calibrated **acyclic** positive
   fixture, not a negative masked by that cycle. The fixture is not rewritten.
2. Independently reproduced a further fail-open in upstream strict JSON: a
   `dimensions.json` with duplicate `project` keys (wrong value first, correct
   value last) gave exit 0, dimensions G-7 PASS and walls G-93 PASS. On a later
   intermediate SHA `a64388ec34796fadd8e540d38f7f2e8973906a65d1cac924ec0bdd4ab66d1ee1`,
   the clean positive still passed and the duplicate gave G-7 FAIL / exit 1 /
   no wall G-93 PASS; this is preliminary. One duplicate-dimensions run emitted
   1573 downstream FAIL rows; inspect whether this noisy cascade still exists.
   Duplicate and nested keys, `--file`, `--rule`, overflow, lost precision,
   partial/draft data and derived-source paths still need a final stable audit.
3. Independently reproduced an unrelated existing `conflict_ref`: selecting
   `building.total_height_cm` and changing its upstream annotation from the
   conflict for its actual level-height inputs `C-001` to the unrelated parapet
   conflict `C-004` originally left no FAIL and wall G-10/G-93 PASS. On
   intermediate validator SHA `f49a6fa97f440511ed9e85fda33710888d969f84d6b532f37fe1817403ba805d`,
   clean passed and the mutation produced wall G-93 FAIL. Wall-local optional
   annotations may instead be explicitly unverified/SKIP; check tests and docs.
4. Independently reproduced G-82 **precision loss before the spatial oracle**:
   an exact decimal boundary `10000000000000001.9` is decoded by ordinary
   `json.loads` as `1.0000000000000002e16`; a 0.1 cm gap is thereby erased and
   the oracle and G-82 report PASS. A representable 1 cm gap was detected.
   Agents began adding fail-closed numeric parsing and huge-integer diagnostics.
   Verify on final bytes. An API handed an already-rounded Python float cannot
   recover its original JSON token; do not count an expected failure documenting
   that fact as PASS. Safe-decimal round-trip parsing is **not** a claim of exact
   binary representation or live Max precision. The old G-82 volume subcheck can
   still reject valid walls thicker than their length.
5. Orchestrator ran the newly written
   `python -B Audit/test_phase16_legacy_three_projects.py -v` on a stable
   **intermediate** snapshot (builder `c603ac1cb7435fea...`, validator
   `e4fdb9966867097a...`, oracle `455a83e7908200f3...`): 2 tests OK, no skips.
   For each of `examples`, `stepped-tower`, and
   `form-precision/specs/pipeline`, lint, `--warnings-as-errors` and `--build`
   were FAIL 0 / WARN 0; respective PASS/SKIP counts 140/31, 147/30, 155/24.
   Normal/`--build` emitters succeeded in temporary copies, bytes matched each
   other and pre-P2 `git show 6c0f27b` for both `assembly.json` and `.ms`, and
   original fixture hashes remained unchanged. Runtime/artifact rows, absent
   optional/legacy specs, range rules without bounds, absent variant/form/QA
   inputs and other applicability cases were SKIP, not proof. The sources were
   edited again afterward: **rerun on the settled final tree**.
6. Orchestrator ran `python -B Audit/test_phase16_input_fixture.py`: the original
   acceptance method's 13 wall-input mutations all ran, no skips, with a
   synthetic **draft** assembly and no `wall_surface` artifacts. This is input
   declaration evidence only; the validator was subsequently edited and the
   run is not a final stable-tree acceptance.
7. The independent scaffold audit identified explicit-wall seed provenance being
   restamped/lost, cross-project mismatches laundered by restamping, `--force`
   overwriting an authored wall and switching route while retaining old script,
   plus a demonstrable check-then-use hardlink substitution race and incorrect
   partial-write `--force` recovery advice. See
   `Audit/_phase16-scaffold-review-2026-11-02c.md` for the pre-fix evidence.
   `scripts/init_project.py` was being changed to address a bounded subset;
   **review actual final code and retest**. Existing no-selector legacy behavior
   and prior user data must be preserved. A previously existing race/partial
   pair-write problem is not solved merely by documenting or a passing happy path.
8. The original acceptance harness can accept a synthetic locked assembly echo
   as its supposed real fixture because its guard checks JSON shape rather than
   produced artifact provenance. Keep actual poly output tests visibly skipped;
   no synthetic echo is produced/live evidence. Five opening injections in the
   102-case suite reach G-93 rather than the advertised alternative G-94; inspect
   target rule and masking, not just aggregate green test counts.

## Subagent reports and remaining verification

Final reports, source hashes and open issues are recorded below after agents stop.
All reported tests must be associated with their exact source snapshot and are
not independent orchestration acceptance unless explicitly stated.

- **Scaffold author:** reports initializer `0ab74f3a949626b039153b463f372608ca5f3ddd6447dafd513cadacd465b852`;
  `Audit/test_phase16_scaffold_safety.py` 13 OK with validator `f49a6fa9...`,
  observation probe `SOURCE_DRIFT []`, isolated suite 34 OK. The main harness
  had 1 failure and 21 SKIP during concurrent edits/temporary syntax error; not
  a final run. Hardlink/path substitution after preflight and non-atomic writes
  remain. The scaffold audit markdown is historical **pre-fix** evidence, not
  an updated verdict. Safety tests SHA `b5a1c86490a1b34e04d086016bbae871dc239154fa7a6fffae361d8913ff35df`,
  observation probe SHA `a4854182222ac6a9aca8d183d40c723a49992b113c90d3fae2556b21546b4614`.
- **Strict upstream auditor:** last completed run used frozen validator
  `f49a6fa97f440511ed9e85fda33710888d969f84d6b532f37fe1817403ba805d`;
  duplicate keys in used upstream files/ledgers produced G-7 FAIL without wall
  G-93 PASS, but the final stability guard saw concurrent edits. The test's
  selective-parser counterfactual reproduces the old false PASS, but is not an
  execution of the prior actual file. Global strict parsing changes behavior of
  ambiguous historical legacy files; assess compatibility explicitly. Wrong
  `assembly.project` produced G-31 FAIL while wall G-93 PASS and G-92 SKIP;
  decide whether that scoped G-93 claim is appropriate. The latest shortened
  `Audit/test_phase16_strict_upstream.py` was **not run** by its author.
- **Grammar author:** changed only `PLAN.md` and `references/07-spec-grammar.md`
  and reports `git diff --check` plus isolated numeric/duplicate controls, not
  full regression. Validator/builder/init/oracle continued changing; reconcile
  grammar with their settled bytes before accepting anything.
- **Independent validator auditor:** 26 tests OK / 0 unittest skips on frozen
  validator `f49a6fa9...`, but process exit 1 due to detected source drift; this
  does **not** verify the current tree. Four mutations exercised, with separate
  acyclic controls for the two registry cases. See
  `Audit/_phase16-validator-independent-2026-11-02c.md`; formula/physical side
  and runtime remain unproven.
- **Validator author:** final reported validator SHA
  `ed9e64dd323441dd9cf67a4bc6ecb1da4040a8a71ebaa863c57e183976162356` and
  `Audit/test_phase16_p2_transitive_regression.py` SHA
  `abf88f939d0d03dcc71d2c40c1ce7e44ffc1889f556e5bb62fd332e6387f747a`.
  **Open blocker:** last new regression had 27 tests / 1 error: deeply nested
  JSON parses but produces an internal `RecursionError` in G-8; no fix begun.
  Prior snapshot `f49a6fa...` yielded dependencies 15 OK and coverage 37 OK;
  isolated had 1/34 failure due to numeric-bound behavior later changed, not
  retested. Legacy-build run overlapped edits and is invalid as final evidence.
  Author did not create `_phase16-provenance-fix-2026-11-02c.md`.
- **Legacy builder author:** reported builder SHA
  `8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8`;
  `Audit/test_phase16_legacy_builder_extra.py` 11 OK on validator `f49a6fa...`
  and oracle `80931375...`. It covers precision guards, both routes, sentinels
  and historical example bytes; these are agent-reported interim results.
  The 10-case legacy-build suite's stability guard failed due to concurrent
  validator/oracle edits; the 37-case coverage suite had no source drift guard.
  Repeat both independently. Strict integer bound and rejection of REVIEW or
  unsupported geometry are compatibility changes. Both old/new builder refused
  the tested no-opening project at an older G-9 self-check before the oracle.
  The output pair is still sequential and non-atomic. Author did not create
  `_phase16-builder-review-2026-11-02c.md`.
- **Spatial oracle auditor:** reports `Audit/test_phase16_legacy_coverage.py` 37
  OK, `Audit/test_phase16_spatial_independent.py` 16 tests OK with **1 expected
  failure**, and `Audit/test_phase16_legacy_build.py` 10 OK on a stable
  snapshot of builder `8fdedf46...`, oracle `d8d1e930...` and **previous**
  validator `f49a6fa9...`. Current validator is `ed9e64dd...`; therefore repeat
  all on the final tree. The expected failure documents direct API inability
  to recover pre-rounded floats, not passing proof. Large diagnostics now have
  exact hexadecimal representations according to that report. Details are in
  `Audit/_phase16-spatial-independent-2026-11-02c.md`.

**Orchestrator read-back after all subagents stopped:** all four Python sources
parsed with `ast.parse` (no bytecode); `git diff --check` exited 0 with only
Git's LF→CRLF warnings. The following byte SHA-256s were independently
re-read after all reports arrived; they are not evidence that behavior passed.
Recompute before resuming tests:

```text
scripts/init_project.py                 0ab74f3a949626b039153b463f372608ca5f3ddd6447dafd513cadacd465b852
scripts/place_components.py             8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8
scripts/validate_specs.py               ed9e64dd323441dd9cf67a4bc6ecb1da4040a8a71ebaa863c57e183976162356
scripts/wall_cell_coverage.py           d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e
PLAN.md                                 c947f386641ab4fa552b67dc22b91d9a68c9804e800d191ac99c23e877bd168b
references/07-spec-grammar.md           4c8cc45f1d8b63d0a0c074a98dbac2396dfa36cb9572436a873d1b1c1e6b09f4
```

## Next session sequence

1. Re-read this handoff and `git status --short --branch --untracked-files=all`,
   `git diff --check`, relevant tracked diffs and every untracked test/audit/helper.
   Treat all as user work. Ensure all agents and pending shell runs are stopped;
   hash the relevant sources and fixtures before and after final tests.
2. Finish independently checking the legacy builder first. Validate positive and
   negative explicit `walls.json` controls: locked versus draft/superseded,
   targeted G-93 failures, `--build --allow-draft`, same/separate `--out`, empty,
   matching and conflicting output route, and unchanged byte sentinels on every
   refusal. Check no-opening and near-tolerance/unsupported cases against the
   historical builder; REVIEW is never PASS. Pair output files are still
   potentially non-atomic on I/O failure or concurrent substitution unless an
   actual final fix and tests prove otherwise.
3. Reproduce all four handoff provenance mutations **with clean calibrated
   controls** including acyclic registry, owner/path/value and ledger, transitive
   dependency/acyclicity, strict JSON duplicate and precision/overflow/recursion,
   partial/units, `--file`/`--rule` and no false PASS. Check `conflict_ref` and
   G-32 formula scope. Re-test G-82 missing first cell/all host, equal-volume
   gaps+overlaps, REVIEW in lint versus `--build`, and numeric input handling.
4. On an immutable tree, run both original harnesses and **all new relevant**
   `Audit/test_phase16_*` tests with enough timeout, plus three projects in lint,
   warnings-as-errors and build. `Audit/test_phase16_scaffold_independent.py`
   began as an observation script asserting *pre-fix* outcomes; verify whether its
   author updated it before interpreting a failure. Analyze each SKIP and xfail;
   a runtime absence, unsupported case or untrusted source is not PASS. Run the
   input-only 13-case adapter separately and never present it as produced output.
5. Reconcile docs with actual final implementation and record settled hashes,
   tests, skips, compatibility changes, safety limits and explicit P2 verdict in
   `CHECKPOINT.md`. Only if P2 truly meets its gates proceed to P3 and the later
   phases, preserving independent physical-direction and live QA requirements.
