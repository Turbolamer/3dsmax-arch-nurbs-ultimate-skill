# Phase 16 P2 validator recursion repair — 2026-11-02d

## Verdict and scope

**The reproduced file/strict-JSON nesting blocker is repaired on the hashes below.**
This is bounded offline validator evidence, not P2 acceptance, produced poly
output, a formula oracle, source truth, or physical-direction/live evidence.
Only `scripts/validate_specs.py`, `Audit/test_phase16_p2_transitive_regression.py`
and this report were edited. Existing source changes were preserved. No Max,
installer, archive/global-copy operation, project mutation or graph rebuild ran.
All disposable file inputs and additional run logs were placed under the approved
`C:\Users\Turbolamer\AppData\Local\Temp\opencode` directory.

## Reproduction before editing

Command: `python -B Audit/test_phase16_p2_transitive_regression.py JsonDepth -v`
on validator `ed9e64dd323441dd9cf67a4bc6ecb1da4040a8a71ebaa863c57e183976162356`.
Exit **1**, one test with a failing `depth=4000` subtest. The CLI itself returned
JSON, but `Isolated.validate()` rejected this row:

> G-8 FAIL, assumptions.json: internal error in this validator while running G-8
> (unit suffix lint): RecursionError: maximum recursion depth exceeded.

The 100-level control completed without failure. Python here is **3.14.4, Windows
AMD64, recursion limit 1000**. Successful `json.loads` is not a traversal-depth
guarantee: this decoder accepted the 4000-level input before G-8 failed.

## Narrow repair

- Added `MAX_JSON_CONTAINER_DEPTH = 128` and an iterative lexical nesting check
  at the beginning of `strict_json_loads`. Both arrays and objects count,
  including the root container. Quoted brackets, escaped quotes and escaped
  backslashes do not count. This takes linear time and constant extra space.
- Exceeding 128 raises an explicit `ValueError` with `JSON nesting exceeds the
  validator safety limit (128 containers; 07 G-7)`. The existing loader maps it
  to fatal input/G-7 before any recursive inspection. All existing callers of
  this strict function receive the same boundary.
- The lexical check is **not** a replacement JSON parser: malformed syntax,
  duplicate keys, finite numeric bounds and decimal round-trip checks remain
  with the existing decoder/hooks. No change to `guard`, recursion limits or
  broad exception handling was made; unexpected decoder `RuntimeError` still
  propagates from `strict_json_loads` in the calibrated control.
- Examined G-8's unit walker, G-9 `collect_leaves`, ledger `deep_equal`, and
  draft-content recursion. Their file-loaded JSON trees now have the bound.
  The transitive provenance graph expansion, cycle elimination and annotation
  search are already iterative; they were not rewritten. A **1020-edge/node
  synthetic provenance chain** (1020 origin nodes, beyond the default Python
  stack limit) passed acyclic checking and failed after adding a closing cycle.

## Regressions and calibration

The transitive suite grew from 27 to **36 tests**. Added coverage includes:

- Exact 128-container arrays, objects and mixed nesting accepted; 129 and 4000
  refused, with deep equality both positive and single-leaf mismatch controls.
- Brackets inside long strings and quote/backslash escape parity controls;
  malformed shallow JSON still produces `JSONDecodeError`.
- Duplicate keys, overflow and lossy decimal tokens at maximum accepted nesting
  still refused by their own existing hooks.
- Maximum-depth geometry/source tree reaches G-8, leaf enumeration and actual
  wall provenance safely. A longer-than-stack provenance graph remains iterative.
- Deep-input refusal independently calibrated against clean wall positives for
  **dimensions, assumptions, conflicts_resolved, massing, nurbs, facade_grids
  and components_registry**, selected with `--file walls.json`; no wall
  G-10/G-93 PASS or unreadable-file G-7/G-8 PASS survives those refusals.
- Existing four transitive fault regressions remain active with acyclic registry
  controls, along with numeric precision/overflow and `--file`/`--rule` tests.
- Added pre/post source/fixture SHA checking to the transitive suite; drift causes
  a test error rather than being presented as a PASS.

One initial new test's facade-grids positive was invalid because the historical
`openings[11]` origin overclaims C-002's head-only claim. The test now uses the
already-defined disposable calibration (split opening leaves and acyclic registry)
before testing that boundary. **The failed positive was not counted as a repair
pass, and no checked-in historical fixture was changed.**

## Executed final tests on stable source bytes

These four commands ran concurrently through a `python -B` subprocess wrapper;
all monitored inputs were SHA-256 checked before and after the complete run.
The test commands themselves and all stdout/stderr are retained in
`C:\Users\Turbolamer\AppData\Local\Temp\opencode\phase16-validator-d-sg8r5_7t\run.json`
and its per-suite `.stdout.txt`/`.stderr.txt` files.

| Exact command | Observed outcome |
|---|---|
| `python -B Audit/test_phase16_p2_transitive_regression.py -v` | exit 0; **36 tests OK**, 0 skip/xfail; `SOURCE_DRIFT []` |
| `python -B Audit/test_phase16_p2_isolated.py -q` | exit 0; **34 tests OK**, 0 skip/xfail |
| `python -B Audit/test_phase16_p2_dependencies.py -q` | exit 0; **15 tests OK**, 0 skip/xfail |
| `python -B Audit/test_phase16_strict_upstream.py` | exit 0; all strict audit controls accepted, no contract/control errors; snapshot pre/post stable |

Additional independent wrapper invocation:
`python -B Audit/test_phase16_legacy_coverage.py -q` — exit 0, **37 tests OK**,
0 skip/xfail; monitored source and examples `SOURCE_DRIFT []`. Its complete
result/hashes are in the same log directory's `coverage-run.json`.

Total unittest cases in those five commands: **122 OK**, no unittest skips or
expected failures. Validator finding-level SKIP is distinct and remains present
for inapplicable, incomplete, unsupported or live/output-only gates. The strict
audit additionally exercises duplicate-key and bad-only controls plus an expressly
labelled selective-parser counterfactual; that counterfactual is **not** a run of
the original historical validator file.

`ast.parse` of both edited Python files succeeded without bytecode creation.
`git diff --check -- scripts/validate_specs.py` exited 0 (Git LF-to-CRLF warning
only). Removing exactly this repair's inserted depth-check block and restoring
the original strict-parser docstring **in memory** reconstructed the exact
pre-edit validator SHA below; no preexisting change was reverted or lost.

## SHA-256 evidence

| File | Before repair | Final / all final tests |
|---|---|---|
| `scripts/validate_specs.py` | `ed9e64dd323441dd9cf67a4bc6ecb1da4040a8a71ebaa863c57e183976162356` | `3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1` |
| `Audit/test_phase16_p2_transitive_regression.py` | `abf88f939d0d03dcc71d2c40c1ce7e44ffc1889f556e5bb62fd332e6387f747a` | `4a3529fccf5df63c6b3e86c506e9db15bcb886084377fe0f411e71f31cfa7347` |

Unchanged before/after the final run:

| Dependency | SHA-256 |
|---|---|
| `scripts/curve_gen.py` | `4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c` |
| `scripts/wall_cell_coverage.py` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` |
| `scripts/init_project.py` | `0ab74f3a949626b039153b463f372608ca5f3ddd6447dafd513cadacd465b852` |
| `scripts/place_components.py` | `8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8` |
| `Audit/test_phase16_p2_isolated.py` | `bafbcb0e433d9375b2e8be2394f67a4a08b1a85c42f6f38c0e33b106dd9a669d` |
| `Audit/test_phase16_p2_dependencies.py` | `da68532ea9e475d787faf22ab8cf86586a1ecbfb9b6dca446b9ff35bc1ef5b2c` |
| `Audit/test_phase16_strict_upstream.py` | `dedec42cfbd64650363117ce866a4484300e261c01232558cc2fe10136ef3cb9` |
| `Audit/test_phase16_legacy_coverage.py` | `50b97625085c1ffe38b8514a5c6fc45cbbf2b22827e1d8fbf109290cdbff651a` |
| `Audit/test_phase16_spatial_independent.py` | `44cecac2863a0397fbaccd1f685e75f74c55290a678d8b08032cbc682cc7cfe6` |

Every `examples/` file was byte-hashed individually in the wrappers and unchanged.
The strict audit's Windows path+SHA example-tree digest was
`a5031d95f39f9538c5bce7ca80bcd5c893f94d00a1d4e79f59e27199ec30a9ab`.
The exact per-file manifests are in `run.json`/`coverage-run.json`, not a claim
that unrelated files or concurrently authored reports remained immutable.

## Limitations / hand-off

1. The 128-container bound is a **new conservative input resource policy**. Valid
   JSON deeper than that is deliberately refused even where a given interpreter
   could parse it. Reconcile this explicit policy in the grammar before release;
   documentation is outside this agent's write ownership. Normal legacy fixtures
   remain covered by the existing isolated/dependency/coverage tests; this report
   does not substitute for the concurrent builder and three-project audits.
2. Arbitrarily preconstructed Python `LoadedFile.doc`/direct walker calls bypass
   strict JSON by design; this change is **not** a general object-graph validator
   and does not make cyclic Python containers or unlimited-depth direct API
   objects safe. No process recursion-limit tuning or unbounded-resource guarantee
   is claimed. File-loaded JSON and strict-string callers are the repaired boundary.
3. The strict audit observed unreadable massing producing **150 downstream FAIL
   rows**, while unreadable dimensions now produced 11 in the explicit-wall test.
   These were not internal errors and no tested wall G-93 PASS survived, but the
   massing cascade remains diagnostic noise outside this narrow repair.
4. The same audit observed wrong `assembly.project` producing G-31 FAIL, G-92 SKIP
   and wall G-93 PASS: the latter is scoped to wall-input declarations, not a valid
   assembly/global PASS. Full command exit remains 1. This preexisting PASS-scope
   decision is not changed or independently accepted by this report.
5. Historical origin claims/cycles were preserved. Transitive checks prove only
   declared owner/path/value joins and graph acyclicity, not authored source
   authority, formula correctness, actual dependency reads, outward sign, emitted
   poly geometry or runtime measurements. An already-rounded Python float cannot
   recover its original JSON token.
6. P2 acceptance and original full harness reruns remain with the orchestrator;
   P3 is not started here. Other reviewers' independently reported blockers are
   not silently patched by this agent. **Edits stop after this report.**

## Authorized reopening: G-32 fidelity and conflict annotations

The orchestrator explicitly reopened the same three files after the preceding
source stop. **This section supersedes the prior stop hashes and test attribution
for the final source**, while preserving the depth-repair history above. Only
the same three owned files were edited; no documentation, independent test,
fixture, installer, archive, global copy or Max scene was changed.

### Reproduced before this follow-up

At stopped validator `3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1`,
inline `python -B` runs against the actual imports and clean synthetic controls
reproduced both observations from the grammar review:

- Wall selects `building.total_height_cm`; replacing that origin with only
  `derives_from=["site.ground_level_cm"]`, leaving the value 820 unchanged and
  omitting optional conflict_ref, produced zero FAIL, dimensions G-32 PASS (15
  recomputed values), and wall G-10/G-93 PASS.
- Wall selects `site.ground_level_cm`; changing its origin to derived from
  `levels[0].elevation_cm` produced exact-path upstream G-32 SKIP, but still zero
  FAIL and wall G-10/G-93 PASS.

The independent reviewer also supplied concrete non-derived annotations:
`conflict_ref=C-001` on given upstream `roof.deck_thickness_cm`, or on given wall
`wall_runs[0]`. Its report records both zero-FAIL false PASS outcomes on stable
`3675bd7f...` and `979056a3...`; this agent ran the independent selector after
repair, not a new claimed pre-fix execution of those two cases.

### Follow-up implementation and scope

1. **Supported scalar G-32 computations:** before crediting a recomputation,
   compare the numerical input paths of the existing formula with the declared
   `derives_from` coverage. A missing required input now fails at the actual
   G-32 derived path and suppresses that file's summary G-32 PASS. No new
   numerical formula was invented. Declared ancestor paths and documented
   derived intermediates are supported, rather than demanding one literal list.
   Coverage is not a guarantee of execution tracing or minimal/exact dependency
   sets: harmless additional declared sources are not rejected for being extra.
2. Historical total-height origins list all level heights rather than the top
   elevation and height. The helper expands the already-documented elevation
   chain to recognize this closure. **Only an exactly zero base elevation may
   be omitted**; a non-zero base must be covered by a declared source. Tests
   independently discriminate a missing source from an unrelated extra, direct
   intermediate sources from the historical list, and explicit ancestor inputs.
   The existing numerical total-height formula remains unchanged.
3. **Reached upstream G-32 SKIP:** carry exact-path skipped recomputations through
   the iterative provenance graph/cache. A wall that actually reaches such an
   upstream origin emits wall G-10 and G-93 SKIP, with no wall PASS, in lint.
   In `--build`, G-93 explicitly fails for unavailable recomputation, including
   `--build --allow-draft`. An unrelated/unreached upstream G-32 SKIP does not
   blanket-invalidate an independent wall input. A supported derived input that
   transitively reaches the skipped origin is likewise incomplete.
4. **Non-derived conflict annotations:** `conflict_ref` describes a derived
   value's conflict-resolved inputs. For reached upstream non-derived origins,
   reject that unsupported annotation rather than treating ID existence as bound
   linkage. For wall-local non-derived origins, reject it under G-10. Given and
   assumed controls without that annotation remain valid. Correct upstream
   derived annotations keep their owner/path/input linkage checks; wall-local
   derived annotations remain explicitly unverified/SKIP as before.
5. The larger-than-stack graph test was corrected to distinguish its two claims:
   the acyclic graph is traversed without recursion failure, but its synthetic
   derived pN values lack formulas, so wall G-93 is now **SKIP**, not PASS. Closing
   the graph into a cycle still fails the targeted provenance gate. This is an
   honest expected-outcome update, not newly invented recomputation.

**Important boundary:** this repair checks the existing supported **scalar
dimension formula** registry and propagates explicit reached G-32 SKIP findings.
It does not invent formula evaluators for every collapsed origin member or every
S1–S4 stage, nor upgrade G-36/G-49/G-64/G-66 into universal formula oracles.
The preexisting collapsed-element recomputation path is not redesigned here.
Consequently no claim of complete formula/dependency verification for arbitrary
collapsed or other-stage origins is made. Wall-local unknown formulas deliberately
remain their existing G-32 SKIP, not a recomputation PASS. These scope boundaries
must remain visible when judging P2; source truth, exact execution reads, physical
direction, produced poly output and live geometry remain unproved.

### Follow-up final tests — no monitored source/fixture drift

The final batch is retained at:
`C:\Users\Turbolamer\AppData\Local\Temp\opencode\phase16-validator-g32-d-lwneuwnq\run.json`.
The wrapper hashes **all `scripts/*.py`, all existing `Audit/test_phase16*.py`,
and every file in examples, stepped-tower, form-precision and poly-shell-input**
before/after (excluding bytecode caches). Result: **`SOURCE_DRIFT []`**. No source
or fixture changed over this run; no intermediate snapshot is presented as final.

| Exact command | Final observed result |
|---|---|
| `python -B Audit/test_phase16_p2_transitive_regression.py -v` | exit 0, **48 tests OK**, no unittest skips/xfails; own `SOURCE_DRIFT []` |
| `python -B Audit/test_phase16_p2_isolated.py -q` | exit 0, **34 tests OK**, no unittest skips/xfails |
| `python -B Audit/test_phase16_p2_dependencies.py -q` | exit 0, **15 tests OK**, no unittest skips/xfails |
| `python -B Audit/test_phase16_strict_upstream.py` | exit 0, no invalid controls/contract violations; strict snapshot stable |
| `python -B Audit/test_phase16_validator_review_d.py -q` | exit 0, **29 tests / 156 CLI calls**, zero failures/errors/skips/xfails; `SOURCE_DRIFT {}` and `OBSERVED_SOURCE_DRIFT {}` |
| `python -B Audit/test_phase16_legacy_three_projects.py -q` | exit 0, **2 tests OK**, no skips; all three legacy pipelines pass lint, warnings-as-errors and build; generated JSON/MS match actual pre-P2 baseline bytes |
| `python -B Audit/test_phase16_legacy_coverage.py -q` | exit 0, **37 tests OK**, no unittest skips/xfails |

Total unittest cases: **165 OK**, plus the strict-upstream audit. This is not a
count of every individual assertion/subtest. Runtime/inapplicable/incomplete
validator findings are still SKIP, not verified outputs. For each legacy project,
lint/strict/build finding counts stayed respectively **140 PASS / 31 SKIP**
(examples), **147 / 30** (stepped-tower), **155 / 24** (form-precision), always
zero FAIL/WARN. Original fixture bytes were unchanged, and normal/build emitter
outputs matched each other and the actual pre-P2 builder at commit `6c0f27b`.

An earlier focused follow-up run had six formula tests and the legacy suite pass
at validator `979056a3...`; it predates annotation repair and is not the final
test attribution. The independent four-selector post-repair run then passed
8 CLI calls at the final validator below with no drift, and the full independent
29-case run above supersedes that limited evidence.

### Follow-up SHA-256s and source stop

| Owned source | Reopening hash | Final tested hash |
|---|---|---|
| `scripts/validate_specs.py` | `3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1` | `616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f` |
| `Audit/test_phase16_p2_transitive_regression.py` | `4a3529fccf5df63c6b3e86c506e9db15bcb886084377fe0f411e71f31cfa7347` | `074d565348dc61dc1c4a6cd1c232c2133124c665c9d14b0aca148504dbeaba1f` |

Final batch dependencies unchanged **during that batch** (other owners had
authorized changes between the earlier depth-only batch and this follow-up):

```text
scripts/init_project.py 42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88
scripts/place_components.py 7f8d4415aa9a95298f13b16d6b28e6c5e40feaed481564cfc841800f131b9cd4
scripts/curve_gen.py 4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c
scripts/wall_cell_coverage.py d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e
Audit/test_phase16_validator_review_d.py f5b014b7dfe4195722deac147115cc17584fca704cf5d2d794c846f0a58a9198
```

The depth/resource, already-rounded float, diagnostic-cascade and filesystem
limitations previously recorded still stand. No docs were edited on reopening;
the grammar review remains historical evidence of its precisely named snapshot.
**Source edits are stopped after this authorized follow-up report. P2 acceptance
and any further scope decision remain with the orchestrator; P3 was not started.**
