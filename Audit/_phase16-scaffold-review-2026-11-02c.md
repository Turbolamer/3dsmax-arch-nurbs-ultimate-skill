# Phase 16 P2 — independent scaffold, route and test review

**Outcome: unresolved findings; not P2 acceptance.** This review did not use Max,
run the installer, or alter any existing project file. Reproductions use only
copies and sentinels in owned temporary directories. The independent probe is
`Audit/test_phase16_scaffold_independent.py`; it freezes the initializer,
validator and their imports into a private temp directory, prints SHA-256s and
reports source drift. Run `python -B Audit/test_phase16_scaffold_independent.py`
from the repository root. Its output is an observation, not an acceptance suite.

## Numbered unresolved blockers and decisions

1. **`--from` deletes a real upstream citation while leaving a `user_brief`
   claim.** In the probe, an otherwise clean synthetic input's
   `dimensions.source.reference` is set to `PRIVATE_SYNTHETIC_TEST_SOURCE_LINE_719`;
   input lint exits 0. `--from` exits 0, but the destination keeps
   `source.kind=user_brief` and replaces that citation with the assertion that
   a `pavilion-01` worked-example brief was re-stamped. The original citation is
   gone; output lint exits 0 and wall G-93 says PASS. Code:
   `scripts/init_project.py:1097-1104,1282-1315`. `preserve_source` protects only
   the walls and assembly, not their provenance dependencies. The replacement
   policy predates P2, but optional custom poly seeds extend its impact; a
   successful lint is not evidence of the original source. Preserve an accurate
   source trail rather than substituting an invented fixed brief.

2. **A seed combining mismatched projects is silently re-stamped into an
   apparently clean project.** Starting from the previous clean positive,
   change only the input wall's `project` from `pavilion-01` to
   `different-source-project`. Input lint exits 1, including explicit G-31
   project mismatch and wall provenance failures. `--from` exits 0 and rewrites
   all projects to `mixed-input`; output lint exits 0. This conceals the
   cross-project mismatch before users can review it.
   `scripts/init_project.py:1097-1120,1295-1300,1351-1392` checks route shape
   *after* replacing project IDs, not original cross-file identity. Decide and
   enforce safe seed preflight/preserved origin; do not conflate all errors with
   a rule that a seed must be production-ready.

3. **`--force` can destroy authored walls and switch routes while retaining
   stale legacy output.** Two controlled, distinct cases:
   - Create a fresh project, replace its generator-created draft walls with a
     valid-shaped, locked hypothetical authored wall (unique sentinel source,
     populated runs); `--force` exits 0, replaces it with empty `draft` walls,
     and removes the sentinel. This is an explicit force operation, not a
     no-force clobber; nevertheless path ownership in `project.json` does not
     prove current content is still generated. `init_project.py:1509-1521,
     1615-1662` trusts names only. This is a user-data-safety decision, not
     permission to remove or overwrite real projects during verification.
   - Seed a historical legacy project, add a copy of its existing legacy
     `assembly.ms`, then run fresh initialization with `--force`. The command
     exits 0, writes poly draft `walls.json` and `assembly.json`, but retains
     the legacy `assembly.ms` byte-identically (SHA-256
     `9865aea8677462a4957cf2d07ba4de48811bd233b90a5fd075d61e83d001528f`).
     JSON lint exits 0 with G-92/G-96 and runtime gates SKIP; that exit is not
     an output PASS. No existing artifacts should be deleted automatically:
     refuse/warn on route transition with conflicting artifacts, with explicit
     user-directed preservation/migration. Test other wall artifacts too.

4. **Path safety is check-then-use, and partial-write recovery advice is
   false.** `init_project.py:1420-1431,1455-1462` refuses an already-existing
   hardlink; the probe confirms exit 2 and an unchanged temporary sentinel.
   Under a controlled substitution *after* preflight but just before
   `Path.write_text` at line 1661, a hardlink to another owned temporary sentinel
   is installed; initializer exits 0 and overwrites that sentinel. This is a
   deterministic simulation of a concurrent path-swap, not evidence that a
   third party did so in a real project. Restrict this risk explicitly or use
   an appropriate race-safe filesystem design; the current checks do not prove
   the documented never-follow guarantee against concurrent changes.
   Separately, injected `PermissionError` while writing `nurbs.json` leaves
   earlier files but no last-written `project.json`; the emitted advice to
   rerun `--force` (lines 1663-1667) fails with exit 2 because no ownership
   manifest exists. Preserve the partial files and offer safe recovery rather
   than asserting that forced retry works. Both write-loop behaviors predate P2;
   their applicability to the new draft walls still needs an explicit decision.

5. **The `--p2-fixture` guard accepts a synthetic *locked* assembly mock as a
   purported real fixture.** `Audit/test_phase16_p2.py:166-189` checks JSON
   status, shape, lint exit and G-92 but does not establish a genuine produced
   assembly; `Audit/test_phase16_p2_cases.py:136-147` creates an explicitly
   synthetic, `locked` echo. The probe seeds that mock without any manifest,
   prints its literal `synthetic ... not built or measured` source, and calls
   only `poly_fixture()`: the guard returns successfully. This does **not**
   show the fixture or P2 is accepted and does not mean all later tests pass;
   it shows the guard cannot enforce its documented real-output prerequisite.
   G-92 PASS explicitly says it is only selector/echo agreement; G-96 and
   G-95/G-98/G-99/G-100 are SKIP. Require independently validated artifact
   provenance at the appropriate future output boundary or clearly label the
   guard as config-only and retain a separate unavailable real-output gate.
   Do not fabricate an assembly merely to remove skips.

6. **Mutation counts do not establish each promised target gate.**
   `Audit/test_phase16_p2_cases.py:214-223,402-415,561-567` accepts either G-93
   or G-94 for ten opening mutations. At the frozen validator SHA below, five
   (`unknown_run`, `unknown_kind`, `reversed_u`, `zero_width`, `head_at_sill`)
   show G-93 FAIL only and G-94 SKIP; two trigger both, and three G-94 only.
   Overall refusal is real, but those five do **not** independently test the
   G-94 predicate named in `references/07-spec-grammar.md:2709-2710`. Decide
   whether G-94 is deliberately dependency-SKIP or must own these failures,
   then test/report the exact intended status and location. Other multi-rule
   alternatives (`test_phase16_p2.py:474-476`, and cases registry) need similar
   masking review. This repeats the handoff's known limitation on a hash-frozen
   snapshot; it does not assert that accepting an invalid opening occurred.

7. **Synthetic-input packaging and phase-document routing need reconciliation.**
   The fixture contains only `walls.json`, whose own reference says synthetic;
   `README.md:1-22` additionally explains the locked input is not a produced
   assembly or runtime evidence. Read-only `collect_files()` returned the JSON
   only, not the README: `scripts/install_skill.py:25-31,40-58`. Its README
   reproduction commands also import `Audit/` tests, not packaged. Preserve
   synthetic-only interpretation and actionable context for installed users,
   or deliberately exclude/move the fixture; do not run installer as a test.
   `PLAN.md:286-302` maps its gate-based phases to the detailed plan, but its
   P6 row still names only docs/archive, not F01–F08 fixture execution; P2
   row links the older handoff rather than the superseding `...02b.md`.
   `PLAN.md:302` names the default installer without warning that it builds an
   existing archive and copies/prunes global installs (`install_skill.py:61-67,
   70-116,133-156`); recheck ownership/effects before any eventual operation.
   No delivery/installer permission is implied by this note.

## Evidence, skips and scope

- `python -B Audit/test_phase16_p2.py --require-p2 --fail-on-skip -v`:
  18 tests run, **21 skips** (two full locked-fixture tests, two array subtests,
  three mismatch subtests, 13 wall-mutation subtests without a real locked
  pipeline, and one missing real poly QA project/request), `unittest` displays
  `OK (skipped=21)` but strict wrapper exits **1** as intended. No skips are
  acceptance. Before the concurrent validator edits this run completed; its
  exact validator hash was not captured at that instant, so do not attribute it
  to a later snapshot. The known first-cell G-82 test ran rather than skipped.
- README's two literal Bash/Python input controls were independently executed:
  both exited 0, including three isolated G-93/G-94/G-97 negatives, and its
  adapter executed the 13 original input mutations with no skips. The adapter
  deliberately uses draft assembly and does not exercise real assembly, output,
  or live QA. The full baseline was concurrently changing; rerun on a stable
  tree if used for a release decision.
- Two runs of `Audit/test_phase16_p2_cases.py -q` occurred while another agent
  modified the validator. The first ended **102 tests / 59 failures**, including
  `IndentationError` at the then-current line 13371; an independent read-only
  AST check reproduced it at SHA-256
  `97e4672a2ede0380b7e228975b444406e21b8c5dc597e49fd9ab13f49e24692b`.
  A later AST read found the indentation corrected. A second run reported 102
  OK, but the validator changed from `1837813b...` to `a64388ec...` during
  that run. **Neither is a settled-tree result.** Rerun after all writes stop.
- The dedicated probe's final run froze validator
  `a64388ec34796fadd8e540d38f7f2e8973906a65d1cac924ec0bdd4ab66d1ee1`,
  produced the observations above, and reported `SOURCE_DRIFT []`. This hashes
  one script snapshot; it is not proof other agents have stopped editing.
  Earlier identical findings were also reproduced against
  `1837813b3c95b2e87354733d603b39ff635550afdf4a4d42786f5c4612651935`.
- `git diff --check` exited 0 with Git LF/CRLF warnings only. New files appeared
  during review from other agents; they are not this review's files and were
  not modified. Existing four transitive provenance blockers listed in the
  handoff were not independently re-evaluated by this scaffold review; consult
  the agent assigned to them. No Max observations, archive installation, fixture
  cleanup outside owned temp, or claim of P2/P3/live acceptance is made here.

## SHA-256 snapshot (bytes, not Git normalized content)

```text
f928d4108b576ebe8f2f02cfc7340ac2a6ca8d1dc2493ff061e37af251e30fae  AGENTS.md
f3d469ff7eaa75b57b76ef109486ff29f5a20035292950ad165632caddf3069d  CHECKPOINT.md
c403acbf5888cbedeea2fe3d84e3421de7bc494b1af3040711db8721ad9b78ba  PLAN.md
eed4af9e53e974447b5a751baaa8cb23b545e329871e2c56733bc61d1abdeca9  references/07-spec-grammar.md
333eec798749b31b2e854f71b3cc174ba2184c4b87a3979ab782e1abc128aff8  scripts/init_project.py
a64388ec34796fadd8e540d38f7f2e8973906a65d1cac924ec0bdd4ab66d1ee1  scripts/validate_specs.py
c603ac1cb7435feaa426596d064613b62d3e3927b24d6ff316628a5bc0f312b9  scripts/place_components.py
455a83e7908200f37892247ce524f16248aaf7b14c1d0ce76dc906ca90d771b9  scripts/wall_cell_coverage.py
4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c  scripts/curve_gen.py
40de710b9360db1c146feeabb9d8e5bf7f99528ae10577821f22d950014f2805  scripts/install_skill.py
5ef4ad0c829755e90024294d65f93d0c0ce4d9e36e08f55658d5f579f9d1d605  specs/fixtures/poly-shell-input/README.md
b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93  specs/fixtures/poly-shell-input/walls.json
e2664cd6c3f40a747ecd75e8e017cf43f686a0adba1c1c2a2f87834c4e2d0a8a  Audit/_phase16-p2-resume-2026-11-02b.md
4abd82aa2d0846234c1b63a29f6d2eea417ec658a81f4503e468654d5ae24b3e  Audit/test_phase16_p2.py
7a2ef2f21423b37d964bff7e42b321ac6d200c6e7cf398d8fdc30123f04f8518  Audit/test_phase16_p2_cases.py
bafbcb0e433d9375b2e8be2394f67a4a08b1a85c42f6f38c0e33b106dd9a669d  Audit/test_phase16_p2_isolated.py
da68532ea9e475d787faf22ab8cf86586a1ecbfb9b6dca446b9ff35bc1ef5b2c  Audit/test_phase16_p2_dependencies.py
50b97625085c1ffe38b8514a5c6fc45cbbf2b22827e1d8fbf109290cdbff651a  Audit/test_phase16_legacy_coverage.py
4493b3fcba24d7cbf7895a562128c392c469a9971c711aef78f8ecda9aace15c  Audit/test_phase16_legacy_build.py
853d8651f20deb59eec84bfc14e18b100adf2894c6d4934dbb8a30df2b7696fc  Audit/test_phase16_scaffold_independent.py
9865aea8677462a4957cf2d07ba4de48811bd233b90a5fd075d61e83d001528f  examples/assembly.ms
```
