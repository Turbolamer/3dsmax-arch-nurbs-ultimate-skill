# Phase 16 P2 — scaffold, G-82 and original harness independent review

## Outcome and scope

**Bounded scaffold repairs are verified; neither a blanket safety PASS nor P2 acceptance is established.**
The current observation script was updated after the historical audit. Its successful run is not
evidence that the two remaining unsafe write boundaries are fixed: it intentionally asserts that a
post-preflight hardlink substitution overwrites a sentinel, and that failed sequential writes leave
an incomplete project. The historical `...02c.md` audit is pre-fix evidence, not today's verdict.

The existing safety suite has **one reproducible failing expectation**, not an initializer refusal
failure: it expects the validator parser to reject `9007199254740992.0`, although that parser accepts
this floating token and the initializer deliberately refuses it. Do not call this suite green or
silently erase the failure. Parser policy parity is not the documented contract; strict JSON and
non-lossy decoding remain requirements. Explicit-wall seeds obey the stricter initializer policy.

Only these repository files were written by this reviewer:

- `Audit/test_phase16_scaffold_review_d.py` — six missing independent controls, 6 OK, zero skips/xfails.
- This report.

No source, existing test, fixture, user project, Max scene, installer, archive or installed copy was
modified. No Max call was made. Existing generated legacy scripts were inspected/copied only into
disposable test directories and never executed. New poly output, runtime QA and physical direction
remain unimplemented/unverified; P0/P1 historical evidence is not remeasured here.

## Commands, frozen runs and source stability

Commands below ran against an immutable copy of the scripts/tests/fixtures rooted at:

```text
C:/Users/Turbolamer/AppData/Local/Temp/opencode/phase16-scaffold-review-d-final-glm9djnb/frozen
```

Its parent retains stdout/stderr per command, `hashes-start.json`, `results.json`,
`baseline-skips.json`, `poly-static-skips.json`, `multi-rule-attribution.json`, and `xfail-trace.txt`.
These are diagnostic temporary files, not production artifacts or repository deliverables.
`TEMP`, `TMP`, `TMPDIR` pointed at the approved OpenCode temp parent; `PYTHONDONTWRITEBYTECODE=1`
and `-B` prevented repository bytecode writes. Historical comparisons in the spatial test used
read-only `git show 6c0f27b:scripts/{place_components.py,scene_units.py}` via `PHASE16_HISTORY_ROOT`.

| Command | Actual result | Interpretation |
|---|---|---|
| `python -B Audit/test_phase16_scaffold_review_d.py -v` | **6 OK**, 0 skip/xfail; exit 0 | Final owned-test rerun: 20.799 s; limitations are explicitly observation tests |
| `python -B Audit/test_phase16_scaffold_safety.py -v` | 13 run, **1 failure**, 0 skip; exit 1 | Numeric parser expectation mismatch below; remaining 12 methods successful |
| `python -B Audit/test_phase16_scaffold_independent.py` | exit 0, `SOURCE_DRIFT []` | Updated observation, including affirmative reproduction of race/partial writes |
| `python -B Audit/test_phase16_legacy_coverage.py -v` | **37 OK**, 0 skip/xfail; exit 0 | Offline spatial + validator integration controls |
| `python -B Audit/test_phase16_spatial_independent.py -v` | 17 run, **16 successful + 1 expected failure**, 0 skip; exit 0 | Expected failure is the pre-rounded API limit, not production parser acceptance |
| `python -B Audit/test_phase16_p2.py --require-p2 --fail-on-skip -v` | 18 methods, **21 skips**, no unittest failure; wrapper exit **1** | Strict incompleteness policy works; 21 is not a count of failed P2 input predicates |
| `python -B Audit/test_phase16_p2.py -v` | 18 methods, **12 class-gated skips**, exit 0 | P2 class disabled; not acceptance |
| `python -B Audit/test_phase16_p2_cases.py -v` | **102 OK**, 0 unittest skip/xfail; exit 0 | Includes 90 mutation methods plus 6 config and 6 runtime-boundary methods; underlying rule SKIPs remain |
| `python -B Audit/test_phase16_input_fixture.py` | 1 method / **13 input-only subtests**, 0 skip; exit 0 | Calls original wall-input mutation method using synthetic locked walls + genuinely draft assembly |

The first batch froze validator `ed9e64dd...`; its same safety mismatch and coverage results were
repeated on validator **`3675bd7f...`** after the recursion repair. The first batch saw repository
validator/test drift and is preliminary. The later batch's **executable sources, reviewed original
tests and input fixtures remained byte-stable**; unrelated reviewer tests/runner plus `PLAN.md` and
grammar changed concurrently. Therefore this is valid evidence for the named frozen executable
snapshot, **not an immutable full-tree/documentation acceptance run**. The final six-control owned
test also ran directly against current sources with no drift, then on the frozen copy.

Additional read-only checks: `graphify query "How do init_project safety, legacy G-82 coverage, and
Phase 16 offline harness skipped gates relate?"` used the existing graph only; graph output was
truncated/stale for current line numbers and was not used as behavioral evidence. Direct source
reads, AST assertion enumeration and actual subprocess results are authoritative here. No graph
rebuild was run. `git status --short --untracked-files=all` preserved all unfamiliar work.

## Every assertion in the scaffold observation script

Reviewed `Audit/test_phase16_scaffold_independent.py`, SHA `a4854182...`, not its historical
`853d8651...` pre-fix copy. All 18 assertions below were reached and passed on the frozen run.

| Line(s) | Assertion / dependency | Correct interpretation of a failure |
|---|---|---|
| 83 | Seed input validator exits 0 | Calibration failure: do not attribute later failures to scaffold copying; inspect full validator report |
| 89 | Explicit-wall seed initialization exits 0 | Positive import regression or unrelated input refusal; not proof of lost source until compared |
| 105 | Full `dimensions.source` equality | Current source-preservation requirement; failure would reopen upstream citation laundering |
| 113 | Mock is locked and explicitly labelled synthetic | Test's config-only precondition, **not** produced assembly evidence |
| 128 | Mock seed copy exits 0, no wall manifest copied | Route-shaped config import is allowed; does not authorize output acceptance |
| 196 | Mismatched source lint AND initialization both refuse | Calibration + current cross-project safety; any successful import would reopen laundering |
| 197 | Mismatch creates no project directory | Refusal must precede all destination writes |
| 201 | Historical no-wall seed initializes | Legacy positive precondition |
| 203 | Its assembly has no selector | Historical legacy route is preserved rather than silently selecting poly |
| 209 | Forced legacy→poly change refuses and whole file tree is unchanged | Current route safety requirement, not a pre-fix assertion |
| 218 | Existing legacy script hash remains identical | Existing user artifact preservation on refusal |
| 221 | Fresh authored-wall test project initializes | Positive setup, not an authored production project |
| 237 | Force refuses authored-wall replacement and whole tree is unchanged | Current wall-content protection; failure is an actual safety regression |
| 251 | Preexisting hardlink refuses, separate temp sentinel unchanged | Existing-link preflight works; **not** race resistance |
| 268 | Injected post-preflight hardlink substitution succeeds AND overwrites sentinel | **An unsafe limitation is being asserted.** A failure can mean improved protection, changed injection timing or unrelated failure; investigate rather than “fixing” the protection to satisfy this observation |
| 293 | Injected first write failure exits 2, manifest absent, forced retry exits 2 | Sequential partial-write limit remains. A future transactional recovery improvement can invalidate this expected observation |
| 294 | Failure advice says “preserve and inspect” | Correct bounded recovery guidance |
| 295 | It no longer promises “re-run with --force to continue” | Misleading old recovery advice is repaired |

Important non-asserted output in that script: `SEED_SOURCE.lint_exit`, all ten `OPENING` results,
`MOCK_LOCKED_ECHO.lint_exit`, `MAIN_FIXTURE_GUARD.mock_accepted`, and `SOURCE_DRIFT` are **printed**,
not asserted. It catches `poly_fixture()` assertion failures for diagnostic logging, so exit 0 alone
does not prove the guard accepted or rejected the mock. `SOURCE_DRIFT` does not change its exit.
It imports `init_project` before taking byte snapshots; the two monkeypatched in-process observations
therefore are not automatically frozen by its own subprocess-script copy. The outer immutable copy
used for this review removes that ambiguity. Its fixture files are not independently hash-guarded;
the outer snapshot and new test do guard source/fixture drift. It is not a comprehensive test runner.

## Scaffold fixes and remaining write/import boundaries

Verified current `scripts/init_project.py` behaviors:

- Explicit-wall seed `source` objects are preserved for **all nine** seeded specs, not only walls and
  assembly (`build_plan`, lines 1101–1139; `rewrite_from_example`, 1330–1370). Project IDs are
  deliberately restamped only after original source projects agree. No claim that source citation
  text is physically authentic is made by a copier.
- `validate_seed_projects` strictly parses every explicit-wall seed before destination creation and
  rejects missing/blank/invalid/different project IDs. Source conflicts with `--force` preserve the
  existing project/sentinels. This is identity/JSON preflight, **not full G-93/provenance validation**.
- Route changes, orphan/existing `assembly.ms`, `wall_surface.ms`, `wall_surface.json` at root,
  `specs/`, and `specs/pipeline/`, adjacent ambiguous route declarations, and edited/locked/seeded or
  unverifiable walls refuse before writing. An intact fresh draft wall needs both manifest path
  ownership and its recorded hash **and** template equality, ignoring only its original timestamp.
  Editing the wall and forging only the hash does not evade template checking.
- Historical no-wall `--from examples` remains selector-free legacy; source restamping remains its
  historical policy. Current full-tree safety controls and the observation confirm refused operations
  preserve existing bytes; they do not establish atomicity of successful operations.

**Remaining boundaries, with requirement interpretation:**

1. `require_safe_path` / `check_destination` reject links/hardlinks present at inspection, but the write
   loop opens by name later (`1786–1805`). Deterministic substitution produced exit 0 and overwritten
   temp sentinel. This is a real unsafe race, **not repaired by documentation**. The initializer's
   header and `--force` help explicitly exclude concurrent modifications. It is a documented,
   preexisting unsupported concurrency boundary, not proof an ordinary single-owner invocation
   violates current P2 declaration requirements. Any “never follow a substituted path” or hostile-
   concurrent-use safety requirement remains unmet; do not claim universal safety from the suite.
2. Files are sequential `write_text` truncating writes, manifest last; there is no transaction,
   rollback or all-files commit. Earlier files survive a failure and forced recovery may refuse.
   The new mid-file control shows an existing recorded `dimensions.json` can be truncated while all
   other files/old manifest remain unchanged. “Preserved” must not be read as old bytes restored.
   This is an actual unmet atomic-write guarantee if such a guarantee is demanded, but no atomic
   project-write implementation was part of the bounded P2 scaffold contract. Safe advice is fixed;
   filesystem atomicity is not. Use fresh/disposable destinations for verification.
3. Only walls have the new content-hash/template protection. `--force` still overwrites an edited or
   locked recorded **non-wall** `dimensions.json`; the new control proves no-force refuses unchanged,
   force succeeds and replaces the sentinel with draft scaffold content. This is authorized path-
   based historical `--force` behavior, not new protection for every authored input. Do not extend the
   wall safety claim to the rest of the project or treat this observation as permission to touch data.
4. Historical no-wall import does **not** use strict duplicate/numeric policy for all dependencies.
   New independently calibrated cases: duplicate `dimensions.project` and
   `site.ground_level_cm:1e-400` each fail input G-7, yet initializer exits 0 and rewritten output lints
   clean after the evidence is lost (duplicate collapsed / underflow becomes 0). This is a reproducible
   strict-JSON import gap, not a harmless proof that invalid inputs were validated. Grammar documents
   the legacy distinction, but documentation does not waive a universal strict-JSON boundary
   requirement. Explicit-wall imports do refuse these tokens. Main must decide historical import
   scope/compatibility explicitly; validating **only the rewritten output cannot repair this**.
5. Source entry paths other than route files are read as historical inputs, not authenticated files;
   route preflight is not a complete anti-substitution/authentication design. No source locks,
   immutable source snapshots or digital provenance attestations are provided by initialization.

### The existing scaffold safety failure

At `Audit/test_phase16_scaffold_safety.py:248`, subtest token `9007199254740992.0` fails
`assertEqual(self.validator_numeric(token), False)` because actual is `True`. The failure occurs
**before that subtest invokes the initializer**. Existing grammar §3.2 explicitly distinguishes
integer tokens (bounded), floating-token parser acceptance, and the initializer's extra magnitude
bound. `0.1` shortest-decimal round-trip acceptance is not exact binary representation.

The new independent control separately confirms (a) validator parser accepts this floating spelling,
(b) a clean explicit-wall seed initializes, and (c) injecting that token into a seeded dependency
refuses with exit 2 before any output exists. No production source was changed and the failing old
suite was not suppressed. Correcting the old test requires explicit per-caller policy expectations,
not removing numeric negative coverage. A uniform numeric magnitude policy remains a separate
contract/design decision; the report does not manufacture one.

## G-82 oracle review and exact skip/xfail interpretation

The oracle checks supported **axis-aligned rectangular cut hosts**, independent host/cell/cut/level/
facade geometry and a bijective dimensions-opening→cut join. It does not trust `volume_cm3`, compass
names or builder cell decomposition. It is **not** an envelope census, full schema validator, poly
validator, geometry generator or live-scene measurement. Alternative spatial partitions can pass
while a separate G-83 full-thickness rule rejects them.

- Missing first cell below the old aggregate budget, all cells of one cut host, missing host,
  deleting both cut+cells while keeping the opening, and balanced gap/overlap **FAIL**. No combined
  G-82 PASS survives. Both 37-case suite and independent 17-method review exercised these.
- Every input boundary is retained and compared as rational values after decoding; face-connected
  defect atoms are merged before width classification. Any nonzero defect remains visible. A narrow
  defect's smallest bounding span at/below linear tolerance gives **REVIEW**, never physical approval.
  Lint: WARN + SKIP; warnings-as-errors: FAIL + SKIP; `--build`: FAIL. Separate volume failures are
  retained even when spatial result passes/reviews. Unsupported/malformed/resource-limit cases fail
  closed; no sampling or partial PASS.
- No-opening/no-cut/no-cell gives **NOT_APPLICABLE**, not PASS. Validator emits SKIP when it reaches
  it, with other global findings still allowed to fail. Builder refuses NOT_APPLICABLE, REVIEW and
  FAIL in all modes. No “legacy compatibility” claim may hide this stronger acceptance policy.
- Direct tests support `10**1600` scale, exact large diagnostics (`exact_hex`), extreme floats and
  giant indices without diagnostic crashes. Production G-82's historical floating-volume half
  separately rejects numeric values above `2^53−1` across all three documents; direct helper
  capabilities do not imply those values are production-supported.
- The old volume half still infers thickness from the smaller plan extent. An independently correct
  wall thicker than its length can spatially PASS but combined G-82 FAIL. This is a retained historical
  representational defect/compatibility boundary, not concealed coverage success.
- A collinear fifth profile point and a `0.0000004 cm` opening shift are **real old-success/new-refusal
  comparisons**: historical builder accepts, current refuses unsupported geometry / REVIEW with no
  output. Exact “same legacy behavior” requirement in the implementation brief is therefore not met
  universally; supported three-project success is narrower evidence. No-opening comparison hits old
  G-9 in **both** builders, so it does **not** prove an end-to-end new no-opening regression.

**Only expected failure:** `test_direct_api_cannot_recover_json_fraction_after_rounding` has the whole
method decorated `expectedFailure`, which could mask an earlier failed control. This review captured
its actual traceback: final line 276 expects REVIEW but receives **PASS**, after the clean positive
and representable 1 cm gap controls succeeded. Raw token `10000000000000001.9` was already rounded by
ordinary `json.loads` to `10000000000000002`. No oracle can recover the original 0.1 cm gap. The new
owned non-xfail control explicitly asserts that API limitation plus the representable negative.
This is not a production parser PASS: existing CLI tests separately reject lossy tokens before G-82
and preserve builder output bytes. The xfail must remain excluded from passing requirements.

Conditional skips in spatial review: historical-source comparison skips only if Git/history is
unavailable (`489–492`). It **ran**, no such skip occurred. Coverage suite has no unittest skips or
expected failures; its internal G-82 SKIP assertions test incompleteness, not full coverage.

## Original harness skip inventory and masked alternatives

### `Audit/test_phase16_p2.py`

Default run disables all **12 PolyAcceptance methods** via class `skipUnless(require_p2)`; 18 methods
are discovered, six legacy methods run. With `--require-p2` enabled and no forged fixture, actual
**21 skips** consist of:

- 2 full methods: locked poly skips legacy wall rules; missing locked poly manifest handling.
- 2 array subtests: `wall_cells`, `opening_cuts` presence on a real locked assembly.
- 3 echo mismatch subtests: legacy, unsupported route, null.
- 13 locked wall mutation subtests: duplicate run, nonpositive thickness, reversed height, missing
  block, bad contour, zero outward, epsilon, budget, reversed/outside opening, sill/head, missing
  opening run, overlapping openings.
- 1 full real-poly-QA/request test: unavailable future profile and request, no observations invented.

The old known G-82 first-cell gap conditional skip at lines 260–262 **did not fire**: this test now
passes because spatial failure is detected. Other conditional field/fixture-shape skips inside the
13 mutations (lines 511–575: no run/two IDs/thickness/heights/block/contour/vector/epsilon/budget/
opening/range/sill-head/run-reference/second same-run opening/range) are dormant without a fixture;
they are missing coverage, never successful predicates, if reached in another invocation.

`poly_fixture()` verifies shape/status/route and lint only. The observation confirmed it accepts an
explicit **synthetic locked assembly echo without any wall manifest**. The guard does not meet its
docstring's “real produced fixture” guarantee; avoid supplying that mock to clear skips. G-92 PASS
only proves selector/echo agreement. G-96 stays SKIP for absent manifest. The missing-manifest test
even permits `--build` exit 0 or 1 if incompleteness is visible; it is **not** proof of build refusal.
The G-96 table-mixing test accepts G-96 **or G-1**; an aggregate success alone cannot name which gate
ran. Existing cases-suite specific G-96-only mocks test static exclusivity, not actual outputs.
The future QA test would submit empty results against a real request; even then it would test
incompleteness handling, not positive live QA.

Missing P3/runtime fixtures are legitimate future-stage absences, not permission to fabricate them.
They prevent claiming full original-harness/Phase16 acceptance, but are not automatically new P2
input implementation failures. `--fail-on-skip` correctly exits 1 by policy. The input-only adapter
separately reaches all 13 original mutation subtests with fresh calibration and no synthetic output.

### `Audit/test_phase16_p2_cases.py`

No unittest skip/xfail mechanism exists. All **102 methods ran**, including 90 generated mutation
methods. Baseline calibration is asserted separately, preventing a universally broken fixture from
looking like successful fault detection. But `must_fail(rules)` means **any one** of the named rules,
not every rule; locations are unconstrained unless a case supplies a `location` filter.

All alternative-rule cases were additionally executed with their actual target rows captured:

| Cases | Actual FAIL attribution / absent alternative |
|---|---|
| unknown root property; missing epsilon | G-1 + G-93 (also G-9); generic G-1 envelope PASS rows are not full schema PASS |
| unknown opening run/kind; reversed u; zero width; head at sill | **G-93 only; G-94 SKIP** (schema/join prerequisite failed) |
| negative opening u; negative sill | **G-93 + G-94** |
| past end; head above wall; overlapping u | **G-94 only; G-93 SKIP**, so no falsely complete wall declaration |
| missing budget object | G-93 + G-97 |
| missing tolerance key | **G-93 only**; G-33 PASS belongs to dimensions, not mutated walls |
| missing/duplicate/unresolved origin coverage | G-9 + G-93 |
| assumed without ledger | G-10 + G-13 + G-93 |
| unresolved derived origin | **G-10 + G-93**; G-31 alternative not exercised on walls |
| unresolved origin input | G-31 + G-93 |
| unreadable walls | G-7 + G-92 |
| either explicit-legacy array missing | G-1 + G-96, plus applicable G-77/G-82 failures |

Thus five advertised opening alternatives do not individually test G-94. This is deliberate
fail-closed prerequisite behavior in current code (`13975–14039`), not acceptance of invalid openings;
grammar's broad G-94 ownership wording should not be reported as independently executed for those
five. The owned test pins **exact** G-93/G-94 failure sets and opening locations, including no G-94
PASS when prerequisite checking skips it. The independent overlapping-u/disjoint-v case targets
G-94 alone, as do valid-schema end/head/overlap cases. Aggregate 102 green is not 102 G-94 proofs.

### Rule-level SKIPs inside otherwise successful harness tests

Complete baseline lint inventories are retained in `baseline-skips.json`. All three have FAIL=0,
WARN=0; `--build`/warnings-as-errors also succeeded inside original harness on the same snapshot.

| Fixture | PASS / SKIP | Complete SKIP rule inventory (multiplicity where relevant) |
|---|---|---|
| examples | 140 / 31 | G-95/98/99/100; absent-wall G-93/94/97; G-16 ×5 (assembly/assumptions/conflicts/massing/nurbs); G-79/80/81; G-69; G-21 core winding flag; G-91; G-70; G-54; G-84/85; G-86; G-87/88/89/90; G-1 ×4 (walls/materials/qa/export absent) |
| stepped-tower | 147 / 30 | Same as examples except G-91 executes/PASS; G-86 is absent analytical targets rather than schema 1.0 |
| form-precision | 155 / 24 | G-95/98/99/100; absent-wall G-93/94/97; G-16 ×6 (adds qa); G-79/80/81; G-69; G-21; G-91; G-70; G-54; G-1 ×3 (walls/materials/export absent). G-84…90 execute rather than SKIP |

Meanings: G-16 has no declared numeric range; G-69 no component variants; G-21 no sibling core
winding declaration; G-91 no stepped declarations; G-54 requires committed Max NURBS census;
G-70 requires emitted CSV census; G-79/80/81 require emitted script inspection; G-84/85 generator
absent; G-86 analytical references absent; G-87…90 QA absent; reserved materials/export remain
out of scope, not planned work. Output/runtime G-95/98/99/100 remain unavailable for all JSON lint.

Cases-suite clean **draft input**: FAIL 0 / WARN 1 / SKIP 40 / PASS 140. In addition to inherited
baseline applicability skips, G-71…83 all SKIP empty draft assembly, G-92 incomplete draft echo,
G-96 incomplete exclusivity/manifest; walls G-16 has no range. Clean **locked synthetic echo**:
FAIL 0 / WARN 0 / SKIP 33 / PASS 148; G-76/77/81/82/83 are explicitly legacy-only SKIPs,
G-79/80 remain artifact SKIPs, G-96 is missing-manifest SKIP. Runtime-boundary methods assert
G-95/98/99/100 SKIP and no PASS; this is a passing **honesty test**, not a passing runtime gate.
Malformed route, envelope, provenance, draft or prior gate failures add dependency SKIPs (notably
G-92/93/94/97) throughout fault cases. Wall-derived formulas without an oracle can be G-32 SKIP;
no synthetic provenance/source declaration proves actual source content, physical face, outward
sign, formula recomputation, emitted topology, replay or live unit behavior.

## SHA-256 evidence (bytes, not normalized Git content)

Executable snapshot used for the final run:

```text
0ab74f3a949626b039153b463f372608ca5f3ddd6447dafd513cadacd465b852  scripts/init_project.py
3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1  scripts/validate_specs.py
8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8  scripts/place_components.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e  scripts/wall_cell_coverage.py
4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c  scripts/curve_gen.py
b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2  scripts/scene_units.py
ce97925d20418c5fa6a1e69c1dacd34334f532dcd244501ec0649fb6c6d48501  scripts/qa_check.py
4abd82aa2d0846234c1b63a29f6d2eea417ec658a81f4503e468654d5ae24b3e  Audit/test_phase16_p2.py
7a2ef2f21423b37d964bff7e42b321ac6d200c6e7cf398d8fdc30123f04f8518  Audit/test_phase16_p2_cases.py
a4854182222ac6a9aca8d183d40c723a49992b113c90d3fae2556b21546b4614  Audit/test_phase16_scaffold_independent.py
b5a1c86490a1b34e04d086016bbae871dc239154fa7a6fffae361d8913ff35df  Audit/test_phase16_scaffold_safety.py
50b97625085c1ffe38b8514a5c6fc45cbbf2b22827e1d8fbf109290cdbff651a  Audit/test_phase16_legacy_coverage.py
44cecac2863a0397fbaccd1f685e75f74c55290a678d8b08032cbc682cc7cfe6  Audit/test_phase16_spatial_independent.py
d7885efbccfe359a079eb3de7fd36dc5b3d9dd3f809dbeadb98727d7e784707a  Audit/test_phase16_input_fixture.py
5e4ace3af15226dfaa92e994ea43faace9c3b832ce7b188753e79f7f5ed96289  Audit/test_phase16_scaffold_review_d.py
45cae7a142762ea9c98761db20967542956844ad43404e94f0cbee0e63157a01  examples/assembly.json
9865aea8677462a4957cf2d07ba4de48811bd233b90a5fd075d61e83d001528f  examples/assembly.ms
b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93  specs/fixtures/poly-shell-input/walls.json
```

Frozen docs at batch start were PLAN `c947f386...`, grammar `4c8cc45f...`; both changed during review.
Their latest text read explicitly says documentation is not acceptance and caller-specific limits
do not waive strict JSON/non-lossy decoding. This review does not claim frozen documentation parity.
Full starting fixture/source hashes are in the retained temp manifest. Rehash/retest on the final
settled tree before orchestration acceptance; do not promote any skipped or expected-failed gate.

**Final read-back caveat:** after the frozen batch completed, `scripts/place_components.py` changed
from the tested `8fdedf46...` to
`4ec5518b9eae472cf2e0817fc3ffe7c7b9658bba0ddfc9edd0a628f1764d68bb`. Builder-dependent
coverage/original-harness comparisons in this report therefore remain snapshot evidence requiring
the main thread's settled rerun. Initializer, validator and oracle still match the listed hashes;
the final direct current-source owned suite again ran **6 OK / zero skips/xfails** in 18.570 s.
Both owned files parsed/decoded, had no trailing whitespace, and the owned test hash remained
`5e4ace3a...`. Latest docs read-back: PLAN
`0d2a7aece519fc16b452ff204e03988f5315a6d6c270340d68b2acb51325b679`, grammar
`19a6243bd5bc7b1f51af92f48425db63eb40806a89d5789be14f122c0d212b55`; neither is an acceptance
artifact. No other file was edited by this reviewer.
