# Phase 16 P2 grammar reconciliation — 2026-11-02d

## Verdict and scope

**P2 remains IN PROGRESS / NOT ACCEPTED; P3 remains QUEUED, not started.** This is a
bounded independent documentation/source review plus targeted offline controls, not final
behavioral acceptance, produced poly output or live geometry evidence. Concurrent validator
repair was authorized in another worker; all results below name the actual reviewed bytes.

Write ownership used: `PLAN.md`, `references/07-spec-grammar.md`, and this report only.
No source, fixture, CHECKPOINT, installer, archive, global copy, graph or Max scene was changed
by this reviewer. No other agent transcript was read. Existing edits and historical evidence
were preserved. No `02d` resume handoff existed at the final check, so PLAN now supersedes
the old `02b` link with `Audit/_phase16-p2-resume-2026-11-02c.md`, and links this review
separately. This report is the reviewer's last authored artifact; stop edits after it.

Read: the session 02d brief, handoff 02c, CHECKPOINT beginning, PLAN §4.0d, relevant grammar
sections, and actual validator/initializer/legacy builder/spatial oracle implementations.
The existing graph query was read-only and only a locator; it is not current-source proof.

## Changes to the owned documentation

- PLAN retains P0/P1 history, P2 NOT accepted, P3 queued and all later independent gates;
  it names strict-parser, G-32, G-82 and filesystem limitations without waiving them.
- Grammar §3.2 records shortest-decimal numeric equality, integer-vs-floating-token scope,
  caller-specific duplicate/numeric policies, and the validator's new 128-container input
  guard. It does not call `0.1` exactly binary-representable or infer lost source digits.
- New §8.5.10 distinguishes pre-write input refusal from failure/substitution during writes:
  separate explicit legacy output needs identical existing `walls.json`; per-file temporary
  replacement is not pair atomicity; scaffold writes are sequential and non-transactional.
- §8.9 records explicit seed source preservation and original-project checks, restricted
  `--force`, explicit legacy null/empty applicability, upstream conflict annotation scope,
  and the difference between transitive provenance and G-32 recomputation.
- §9.4 keeps the intended G-32 requirement unchanged and limits claims about implemented
  formula checks. G-82 wording retains refusal of REVIEW/FAIL/NOT_APPLICABLE and avoids
  inventing proof that every no-opening project once passed the historical builder.

## Independently executed controls

Commands: `git status --short`; read-only `graphify query "wall provenance G-32
numeric strict_json_loads G-82 coverage" --budget 1000`; inline `python -B - <<'PY'`
probes described below; `git diff --check -- PLAN.md references/07-spec-grammar.md`;
inline `python -B` SHA-256 reads. No install, archive rebuild or live call was run.

Two exploratory probes compiled captured source bytes into in-memory modules; each ended
`SOURCE_DRIFT []`. A final assertion-bearing `python -B` run imported the actual source,
hashed all five source/helper files, eight example JSON inputs, synthetic wall input and
both edited docs before and after, and ended **`SOURCE_OR_FIXTURE_DRIFT []`**, exit 0.
This proves only stability over those controls, not that all concurrent work has finished.

### Strict numeric / duplicate boundary

The final run directly called `validate_specs.strict_json_loads`,
`place_components.strict_loads` (default and `reject_duplicate_keys=True`),
`init_project.parse_seed_json(strict_route=True, strict_numeric=True)`, and its default
historical mode. ACCEPT below means parser acceptance only, not schema/geometry acceptance.

| Token/input | Validator | Builder default | Builder duplicate-strict | Init explicit-wall | Init historical default |
|---|---|---|---|---|---|
| `0.1`, `1.00`, `1e0` | ACCEPT | ACCEPT | ACCEPT | ACCEPT | ACCEPT |
| `1e-400` | ValueError | ValueError | ValueError | ValueError | ACCEPT (underflows) |
| `1e999` | ValueError | ValueError | ValueError | ValueError | ValueError |
| `10000000000000001.9` | ValueError | ValueError | ValueError | ValueError | ACCEPT (rounds) |
| `9007199254740992` | ValueError | ValueError | ValueError | ValueError | ACCEPT |
| `9007199254740992.0`, `1e20` | ACCEPT | ValueError | ValueError | ValueError | ACCEPT |
| `{"a":{"x":1,"x":2}}` | ValueError | ACCEPT | ValueError | ValueError | ACCEPT |

All outcomes were asserted, not inferred from documentation. Source read-back confirms the
CLI selects strict duplicate/numeric seed mode for all explicit-wall seeds; historical
seed assembly uses duplicate checking but not that numeric mode. Ordinary historical
builder `read_spec` uses its default duplicate-permissive path; route documents and explicit
input snapshots use duplicate-strict mode. The validator globally loads known specs strictly.
The initializer's default is not a global guarantee about every CLI-selected route document.

Nesting controls: validator parsing accepts 128 nested containers, refuses 129 and 800
with controlled ValueError, and accepts a string containing 800 bracket pairs. The nesting
guard is now present, but these parser controls **do not rerun the whole deep-JSON G-8
regression**. The previous handoff's open recursion incident remains historical evidence;
the orchestrator must judge the independent current regression, not a docs-only closure.

### G-32 upstream claim limits — concrete open findings

All controls use in-memory copies of the eight example JSON files, add the checked-in
synthetic input-only wall declaration, and replace assembly content with an **empty draft**:
`origin_inputs`, `origins`, `defaults`, `layer_map`, `placements`, `opening_cuts`,
`wall_cells`, `scatter` are empty. No locked assembly echo, manifest or poly output is used.
Wall route input is genuine synthetic test input, not claimed project/source evidence.

1. **Clean positive:** wall `origin_inputs = ["building.total_height_cm"]`.
   `run_checks` produces no FAIL, dimensions G-32 PASS (15 formulas), wall G-10/G-93 PASS.
2. **Dependency-list fidelity defect:** replace only that dimension origin with
   `{"origin":"derived","derives_from":["site.ground_level_cm"]}`. The value stays
   820; the optional original `conflict_ref` is absent in this mutation. Result: **no FAIL,
   dimensions G-32 PASS (15 formulas), wall G-10/G-93 PASS**. The fixed formula still reads
   the level-chain fields, not this declared dependency list. An acyclic resolving list is
   not proof of the inputs actually used by recomputation.
3. **Reached upstream formula unavailable:** wall `origin_inputs =
   ["site.ground_level_cm"]`; replace its upstream origin with
   `{"origin":"derived","derives_from":["levels[0].elevation_cm"]}`.
   Result: **no FAIL, G-32 SKIP at `dimensions.json::site.ground_level_cm`, wall G-10/G-93
   PASS**. The wall transitive gate does not require a formula PASS for each reached value.
4. **Wrong-value negative control:** from the clean case add 10 to
   `dimensions.building.total_height_cm`. Actual G-32 FAIL occurs at that exact path and
   wall G-93 has no PASS. Other dimensional/ledger failures also occur; this is a calibrated
   formula-negative control, not an assertion that G-32 was the only failing predicate.

The intended contract still requires correct documented computation from declared inputs.
These observations block any claim of **complete upstream derived-value verification**.
Whether the required P2 fix is dependency/formula repair or an explicit independently
approved scope decision belongs to the orchestrator; this review does not waive it.
Wall-local unknown formulas still report SKIP, and no new wall formula evaluator was added.

Minimal reproduction core (execute under `python -B` with the actual imports and hashes):

```python
from pathlib import Path
import copy
from scripts import validate_specs as v

docs = {p.stem: v.strict_json_loads(p.read_text(encoding="utf-8"))
        for p in Path("examples").glob("*.json") if p.stem in v.SPEC_BY_NAME}
docs["walls"] = v.strict_json_loads(Path(
    "specs/fixtures/poly-shell-input/walls.json").read_text(encoding="utf-8"))
a = docs["assembly"]
a["status"] = "draft"
a.update(origin_inputs=[], origins={}, defaults={}, layer_map={}, placements=[],
         opening_cuts=[], wall_cells=[], scatter=[])

def run(data):
    session = v.Session([v.LoadedFile(Path(n + ".json"), n + ".json",
                         spec=v.SPEC_BY_NAME[n], doc=d)
                         for n, d in sorted(data.items())])
    report = v.Report()
    v.run_checks(session, report)
    return report

docs["walls"]["origin_inputs"] = ["building.total_height_cm"]
positive = run(copy.deepcopy(docs))
wrong_dependencies = copy.deepcopy(docs)
wrong_dependencies["dimensions"]["origins"]["building.total_height_cm"] = {
    "origin": "derived", "derives_from": ["site.ground_level_cm"]}
dependency_result = run(wrong_dependencies)
missing_formula = copy.deepcopy(docs)
missing_formula["walls"]["origin_inputs"] = ["site.ground_level_cm"]
missing_formula["dimensions"]["origins"]["site.ground_level_cm"] = {
    "origin": "derived", "derives_from": ["levels[0].elevation_cm"]}
formula_result = run(missing_formula)
```

### G-82 caller behavior — direct controlled observations

Starting from copied example assembly/massing/dimensions:

| Control | Spatial oracle | Validator G-82 lint | Validator G-82 build | Builder spatial helper |
|---|---|---|---|---|
| Unchanged supported example | PASS | PASS | PASS | accepts |
| Increase `WAL-EL-014-C04.plan_rect_cm[0]` by 0.1 | REVIEW | WARN + SKIP | FAIL | refuses |
| Empty openings, cuts and cells | NOT_APPLICABLE | SKIP | SKIP | refuses |
| Shift first corner X of first cut's host profile by 1 | FAIL | FAIL | FAIL | refuses |

Oracle calls: `check_wall_cell_coverage(a, m, d)`. Validator calls isolate
`_g82_wall_tiling` with `_p5_tolerances` and `Session(build_gate=False/True)`; builder
calls use `verify_spatial_coverage(a, m, d)`. These assert the caller policy, **not**
whole-CLI success for synthetic empty inputs, old-builder compatibility or any live mesh.
Independent builder/scaffold/coverage/legacy regressions remain the owning reviewers' work.

## Outstanding decisions / blockers; do not normalize into PASS

1. **G-32 scope:** the two actual observations above remain implementation/contract gaps;
   source eligibility, ledgers and acyclicity do not prove formula completeness or fidelity.
2. **Strict JSON across boundaries:** historical builder duplicate acceptance and historical
   initializer lossy decoding remain gaps against strict file handling, despite preserving
   established legacy route behavior. Integer-valued floating spellings also have different
   bounds across loaders. Record compatibility and resolve policy; do not claim identical
   enforcement, relax strict JSON, or infer a global magnitude requirement was implemented.
3. **Legacy compatibility:** a no-cut oracle yields NOT_APPLICABLE, never coverage PASS;
   current builder helper refuses it in all modes. Unsupported geometry fails closed.
   The historical volume subcheck's shorter-plan-extent thickness limitation remains.
   Full no-opening CLI comparisons need clean positives and the actual historical builder.
4. **Filesystem safety:** source read-back confirms checks precede writes, source snapshots
   are rechecked only on explicit legacy, builder outputs are sequential replacements, and
   initializer uses sequential direct writes. No immutable handle/path transaction closes
   the post-check substitution window. This reviewer did not rerun destructive/race or I/O
   fault injection; historical failures are preserved, not falsely claimed repaired.
5. **Existing non-P2 prose inconsistency, left untouched:** §3.1 says canonical versions only,
   while §9.1 G-3 permits minor/patch lint warnings and actual `check_envelope` does warn
   (but build refuses). Also §9.2 G-15 still names P3..P6 while the source permits restored
   P8. A broader reconciliation must distinguish intended policy from measured lint behavior.
6. **Acceptance:** repeat required independent suites on final stable hashes, inspect all
   SKIP/xfail, and separately verify authoritative physical outward sign and later artifact/
   runtime gates. No docs edit proves P2, P3, source truth, live precision or poly QA.

## Exact byte SHA-256 snapshots

Starting owned documents (the previous user/agent modifications were retained):

```text
c947f386641ab4fa552b67dc22b91d9a68c9804e800d191ac99c23e877bd168b PLAN.md
4c8cc45f1d8b63d0a0c074a98dbac2396dfa36cb9572436a873d1b1c1e6b09f4 references/07-spec-grammar.md
```

Final docs and tested source snapshot (validator is newer than handoff 02c's `ed9e64dd...`):

```text
0d2a7aece519fc16b452ff204e03988f5315a6d6c270340d68b2acb51325b679 PLAN.md
12edf3fef4d6847a9d198f9904df8fdcbed828e9a1f9eb035aedfcf23770d6df references/07-spec-grammar.md
3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1 scripts/validate_specs.py
0ab74f3a949626b039153b463f372608ca5f3ddd6447dafd513cadacd465b852 scripts/init_project.py
8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8 scripts/place_components.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e scripts/wall_cell_coverage.py
4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c scripts/curve_gen.py
```

Fixtures read (unchanged during the final controls):

```text
45cae7a142762ea9c98761db20967542956844ad43404e94f0cbee0e63157a01 examples/assembly.json
1c8d8eb29b5c09d81229058d106a99a84da0d1c9f537c10e990aba938335b986 examples/assumptions.json
2318898ca6c6cba3c67659222214bd5ff0f054723867c6ee4a6bfa839f39eb76 examples/components_registry.json
6676c4f38c7b2bb40d44828af631fc2b41e20754819d9cbf339b099b63d6f5fc examples/conflicts_resolved.json
5f0f0108936457b08149d78790a2f2453edc3f95b8c8abddc550effab3e52f75 examples/dimensions.json
1571917cc6f7a7dff1d7cb3f45310019ba522c2ab145f0e16aeb388dc5ee8a76 examples/facade_grids.json
fabad688a7da0c9b16239ccee0c0f10d546002f26ee3c81122d89b143bfb6fa9 examples/massing.json
45354c71562177c2820912e4c2da6ea02373ba3f52bfa5032b6e2c8917953fd3 examples/nurbs.json
b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93 specs/fixtures/poly-shell-input/walls.json
```

Final owned-document `git diff --check` before writing this report exited 0 (Git's LF→CRLF
working-copy warnings only). Targeted behavior and stable hashes are the evidence above;
the new prose itself supplies no behavioral acceptance. No further edits by this reviewer.

## Coordinated follow-up — conservative file/strict-string nesting boundary

**Supersedes only the earlier nesting-review completion and final grammar hash above, not
their historical evidence or any other finding.** After the initial report, the coordinator
explicitly requested this bounded continuation and confirmed the validator author had stopped
at SHA-256 `3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1`.
The earlier report bytes before this follow-up were
`41abcec18f2d62bcd7654070a1ff68497bad6ec0acf18fb64dc0941b2a0aaf0a`.

Read `Audit/_phase16-validator-repair-2026-11-02d.md` and independently re-read the
actual scanner, strict decoder call and file error mapping. Grammar §3.2 and G-7 now
explicitly state:

- `MAX_JSON_CONTAINER_DEPTH = 128` is a **conservative input resource policy** for
  validator file loading and text passed to `strict_json_loads`, not a geometry tolerance.
- The iterative lexical scanner runs before strict JSON decoding, counts array/object
  nesting including the root, and tracks strings and escapes. Valid deeper JSON is refused
  even if a Python interpreter could decode it. The decoder/hooks still own malformed
  syntax, duplicate keys and numeric checks; this is not a second general JSON parser.
- Over-limit text raises `ValueError`; the file loader maps that to fatal input/G-7,
  rather than an internal G-8 `RecursionError`.
- Preconstructed `LoadedFile.doc`, direct walkers and other already-decoded Python
  objects bypass it. No cyclic-container, arbitrary-object-graph, unlimited-depth direct
  API or universal resource-safety guarantee is claimed. Independent initializer/builder
  loaders do not automatically inherit the scanner.

**New independent execution**, not merely the author's report:

```text
python -B Audit/test_phase16_p2_transitive_regression.py JsonDepth StrictNesting -v
exit 0; 8 tests OK; 0 skip/xfail; SOURCE_DRIFT []
```

This subset exercised the reproduced 4000-deep file failure against its clean 100-level
control; seven used upstream/ledger deep-input refusals with calibrated positives;
maximum accepted file depth through unit/leaf checks; 128/129 array, object and mixed
boundaries; quoted brackets and escapes; duplicate/lossy/overflow hooks at the nesting
limit; malformed shallow JSON; and an unexpected decoder-error sentinel. No monitored
source or historical example changed. This supplies bounded independent evidence for
the repaired file/string recursion defect; it does **not** certify preconstructed Python
object graphs, repeat all 36 tests, resolve the G-32 findings or accept P2.

Final read-back hashes for this follow-up:

```text
0d2a7aece519fc16b452ff204e03988f5315a6d6c270340d68b2acb51325b679 PLAN.md
19a6243bd5bc7b1f51af92f48425db63eb40806a89d5789be14f122c0d212b55 references/07-spec-grammar.md
3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1 scripts/validate_specs.py
4a3529fccf5df63c6b3e86c506e9db15bcb886084377fe0f411e71f31cfa7347 Audit/test_phase16_p2_transitive_regression.py
8a6a1adad58971bbdbc6a6340242a90a65bfb11668922e302912d52ff6776e98 Audit/_phase16-validator-repair-2026-11-02d.md
```

`git diff --check -- PLAN.md references/07-spec-grammar.md
Audit/_phase16-grammar-review-2026-11-02d.md` exited 0 before this final report append
(Git LF→CRLF warnings only). No 02d resume handoff existed, so PLAN's 02c handoff link
remains correct. PLAN was not edited in this follow-up; only the owned grammar and this
report were edited. P2 remains **NOT accepted**, P3 **queued**. No Max, source repair,
installer, archive or global-copy update. **Edits stop after this report follow-up.**

## Reopened bounded reconciliation — builder/scaffold repairs and active validator, 2026-11-02d

**Dated supersession, not erasure or acceptance.** The coordinator explicitly reopened only
PLAN, the grammar and append-only reporting here. This section supersedes earlier statements
as *current implementation descriptions* where the bounded repairs below apply; it does not
erase any original failure, source hash, test run, remaining limit or required final retest.
Report bytes immediately before this append had SHA-256
`dfc3f3b445041500f96acb78ac4cb2b7ced7105ac3b7d8f44b59ba10b7c56fe8`.

Read the new `Audit/_phase16-builder-repair-2026-11-02d.md` and
`Audit/_phase16-scaffold-repair-2026-11-02d.md`, the coordinator's verification note and
actual current source at the affected parser/caller/staging/rollback/G-32/annotation sites.
**No broad suite or behavioral probe ran in this reopening.** Repair-author test counts remain
their attributed evidence, not fresh tests by this reviewer. Exact final source verification,
stopped-source orchestration, and disposition of superseded observation assertions belong to
the coordinator. Validator work remains active; source read-back is provisional.

### Reconciled current descriptions

- **Production caller policy:** builder `read_spec` now explicitly selects duplicate-strict
  parsing on every route, including historical no-selector inputs. Its standalone helper's
  duplicate-permissive default remains, so the old direct-helper ACCEPT is historical evidence
  and no longer describes actual consumed JSON. Route and explicit snapshot reads are strict.
- **All initializer-used seeds/ownership text:** historical as well as explicit-wall seed text
  now has strict duplicate, finite/shortest-decimal, integer/all-float-magnitude and depth
  boundaries; the independent scanner limits arrays/objects to 128 containers including root.
  The grammar adds a production-caller policy table and retains the earlier permissive-policy
  paragraph beneath an explicit dated SUPERSEDED marker. Valid historical no-selector routing
  and source re-stamping remain distinct from refusal of ambiguous/rounded invalid input.
- **Numeric differences preserved:** validator floating spellings do not universally inherit its
  integer-token magnitude bound; builder integer-valued floats and all initializer float
  magnitudes have tighter caller policies. The unchanged oracle cannot recover pre-rounded
  input. No global exact-binary, uniform-loader or arbitrary Python object-graph claim is made.
- **Builder output pair:** production `write_output_pair` stages changed payloads and old bytes,
  repeats its route/input/lexical-directory guard, and attempts identity-checked rollback on
  recovered write/replacement errors. `ROLLBACK INCOMPLETE` and retained recovery paths remain
  explicit. This supersedes the unqualified pre-repair ordinary-second-replacement mixed-pair
  finding; it does not prove a two-file atomic transaction, universal recovery or crash safety.
- **Initializer destination:** descriptor-based per-file staging replaces direct final-leaf
  truncation. Bounded staging/write/fsync/replace failure preserves the affected destination;
  whole-project commits remain sequential, manifest last, with no rollback of earlier commits.
  Non-wall `--force` retains historical recorded-path overwrite semantics: authored non-wall
  content is not protected by the wall hash/template guard. Metadata/ACL fidelity is unproven.
- **No safety waiver:** repeated checks are not locks, handle-relative commits or resistance to
  arbitrary swaps inside staging/read/replace/rollback/cleanup. Observable mixed pair state,
  failed rollback, late parent substitution, cleanup failure, retained files and crash/power-loss
  exposure remain. The grammar retains pre-repair wording as marked history and states the
  narrower current recovered-error/deterministic-substitution boundary separately.
- **Active validator response:** source read-back shows dependency-coverage checks for supported
  documented G-32 formulas, reached upstream G-32 SKIP propagated as wall incompleteness/build
  refusal, and non-derived `conflict_ref` rejection in reached upstream/wall origins. The earlier
  exact-hash G-32 findings are preserved and dated as superseded current claims *pending final
  verification*, not closed by docs. Ancestor/intermediate dependency coverage is not execution
  tracing or arbitrary algebra; unsupported/collapsed origin/stage oracles are not invented.
  Valid wall-local derived annotations still remain unverified/SKIP. The intended G-32 and
  annotation contract is not weakened to accept missing coverage.

PLAN now links both bounded repair reports, preserves P2 **NOT accepted** and P3 **queued**,
and states the coordinator's final verification ownership. No 02d resume handoff existed at
this review, so the 02c handoff link remains. G-82 refusal, thick-wall compatibility boundaries,
synthetic-vs-produced warnings and all later physical-direction/artifact/runtime gates survive.

### Checks and observed byte hashes — NOT final source certification

`git diff --check -- PLAN.md references/07-spec-grammar.md
Audit/_phase16-grammar-review-2026-11-02d.md` exited 0 before this append (LF→CRLF
advisories only). A read-only `python -B` check asserted the P2/P3 status strings, existence
of the two report links, new caller-policy/rollback/supersession text, and printed SHA-256s;
it ran no source behavior or suites.

The builder changed **during** this documentation review: opening read-back was
`7f8d4415aa9a95298f13b16d6b28e6c5e40feaed481564cfc841800f131b9cd4`, later read-back
was `4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac`.
Its report also changed from `a0e7b2df...` to the full hash below. The reviewer read the
updated staging cleanup path and did not infer stability or reuse earlier behavior results.
The following are point-in-time observations at **2026-11-02T19:44:37.582873Z**, not
settled/final hashes for the coordinator's forthcoming run:

```text
9f69880641abcd2e3f4d897aa4ed90a16d60a16f1f94dce4ab9c74c41022e661 PLAN.md
d67959191f0358c53e9d297f3da6a074db302171ae20af711903cb449fd9ef0c references/07-spec-grammar.md
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f scripts/validate_specs.py
42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88 scripts/init_project.py
4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac scripts/place_components.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e scripts/wall_cell_coverage.py
d0cc0713a2f7439b9028266511aa1e3ad1c39988437d885d444bd887cad4d22e Audit/_phase16-builder-repair-2026-11-02d.md
4043238babded73b36c0e91dceb42f35dc4ef03d341bdfa35a35c7ec97c5f2a2 Audit/_phase16-scaffold-repair-2026-11-02d.md
```

Earlier doc hashes in this report remain historical. Only PLAN and grammar were edited and
this report appended; no source, tests, fixture, CHECKPOINT, installer, archive, global copy
or Max work was performed. **P2 NOT accepted; P3 queued. Stop docs after this report append.**

## Post-test status publication — coordinator accepted bounded OFFLINE P2, 2026-11-02d

**Current gate decision supersedes all earlier non-acceptance/ACTIVE/provisional status in this
report, not the dated evidence or retained limitations.** After independently executing the stable
all-suite run and obtaining the separate final evidence review, the coordinator explicitly
**ACCEPTED bounded OFFLINE P2 only** and authorized status publication in the same owned files.
P3 is ready for contract/implementation next, **NOT implemented**; no live authorization follows.

Read `Audit/_phase16-p2-final-evidence-review-2026-11-02d.md` in full, the final tables and exact
snapshot in `Audit/_phase16-p2-verification-2026-11-02d.md`, and the retained run's
`snapshot-verdict.json` / `hashes-before.json`. This publication does not independently re-adjudicate
or broaden the coordinator's decision. The independent review is SHA-256
`07a014d104daf4a9d2ac0c8e388dcd5be8cddb6c0a7c3e34e20acc901c0716d7` at read-back.
The report bytes before this final append were
`b2e902f72aeb1b8a93cb0cc66d6fd294adcecdd04bcdfd13fb6e58591b678122`.

### Published decision and final disposition

- PLAN §4.0d and grammar's current status identify acceptance on the exact executable hashes
  below, with direct links to final verification, independent review and execution snapshot.
  Historical interruption, reproduced failures and provisional repairs remain explicitly dated.
- G-32/annotation **reproduced cases are no longer open/ACTIVE on that accepted snapshot**:
  final review §3 records independently calibrated dependency failures without annotation masking,
  reached unknown-formula lint incompleteness/build refusal, and non-derived annotation rejection.
  The finite registry, ancestor/intermediate dependency closure and nonzero-base controls are
  verified only within their documented scope. Unsupported wall-local formulas still yield G-32
  SKIP; valid wall-local derived annotation linkage remains SKIP. No source truth, arbitrary algebra,
  execution-read tracing or physical outward-side verification is inferred from scoped PASS.
- The **21 original-harness skip events remain NOT RUN, not PASS**: 20 need authentic produced
  poly fixtures and one needs real poly QA. The input-only adapter separately executes 13 mutation
  branches with a draft assembly. Final review §2 is the exact inventory and disposition, not an
  aggregate claim that every future output/runtime predicate ran.
- The **one expected failure is excluded from protective passing evidence**: ordinary JSON parsing
  erased the decimal gap before the oracle received it; a pre-rounded object cannot recover source
  digits. Non-xfail calibrated controls and production text refusals are separate evidence.
- Bounded I/O acceptance covers the named recovered-error/deterministic-substitution cases with
  working restoration, not multi-file/crash atomicity, immutable locks, arbitrary-race protection
  or universal recovery. Scaffold affected-file preservation is not whole-project rollback;
  historical recorded non-wall `--force` overwrite remains. Retained recovery/cleanup limits survive.
- Actual old/current offline emitters match both generated files for the three supported projects;
  this is not universal legacy parity. Strict invalid/lossy JSON, REVIEW/unsupported coverage,
  caller numeric policies, byte-identical separate-wall output and lexical parent-traversal spelling
  refusal remain intentional restrictions; thick-wall volume false rejection remains. See final
  review §§3–6 and verification's final compatibility table; no restriction was silently waived.
- Produced poly manifest/script, poly QA/runtime observations, integrated/live geometry, source
  authority, physical direction, F02–F08 and the rest of Phase 16 remain outside this P2 acceptance.
  P3 contract/implementation is the next stage, not an existing emitter or permission to use Max,
  install/prune global copies or rebuild the archive.

### Execution snapshot versus publication hashes — kept separate

The immutable execution record is `Audit/phase16-p2-final-2026-11-02d/`, run from
`2026-11-02T19:46:47.384432+00:00` to `2026-11-02T20:07:54.859466+00:00`.
It records 20/20 scripts, all exit 0, no observed source/fixture drift and unchanged Git HEAD.
Its `acceptance: NOT_ASSESSED` correctly leaves the later gate decision to the coordinator;
the execution file was **not rewritten** to publish acceptance.

Accepted executable SHA-256s, taken from the verified run and final evidence (final source
unchanged verification remains coordinator-owned, not a new behavioral claim by this publisher):

```text
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f scripts/validate_specs.py
42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88 scripts/init_project.py
4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac scripts/place_components.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e scripts/wall_cell_coverage.py
```

**Documentation publication occurred after those tests.** Before publication, both document
hashes matched their execution-manifest entries; after publication they deliberately differ:

| Document | Before / immutable execution-manifest SHA-256 | After status publication SHA-256 |
|---|---|---|
| `PLAN.md` | `9f69880641abcd2e3f4d897aa4ed90a16d60a16f1f94dce4ab9c74c41022e661` | `952ee01680bc3c04d4bf850b8c5db512bebb5105e4dd8bd48def73124cef2e60` |
| `references/07-spec-grammar.md` | `d67959191f0358c53e9d297f3da6a074db302171ae20af711903cb449fd9ef0c` | `6c38d3363093822c968c59fbccdff47c097eb57a9a8353e3c79a2b5fe9954258` |

No behavioral suite ran on the newly published documents; no immutable execution manifest was
regenerated or altered to hide the publication difference. Read-only evidence checksum checks:

```text
089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72 hashes-before.json
089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72 hashes-after.json
089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72 hashes-at-process-exit.json
50ff5d713c5a593783fe8cd30fcbda81b902b60de6feaa912c2955742f9ffd97 snapshot-verdict.json
2d1901ada0f06ecc2da7afc4a35c33add0d7eab1dfa3924362c9eeab00a4cfa7 results.json
```

Only read-only publication checks ran: relevant reads/grep, `python -B` document/status/link
assertions and SHA-256 comparisons, plus `git diff --check -- PLAN.md
references/07-spec-grammar.md Audit/_phase16-grammar-review-2026-11-02d.md` (exit 0,
LF→CRLF advisories only, before this append). No broad suite, source/test/fixture/CHECKPOINT/
SKILL edit, Max, installer, installed-copy or archive action occurred. This append is the final
owned write. **Documentation/source-stop: docs edits stopped; source was never edited here.**
