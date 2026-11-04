# Phase 16 P2 — final independent evidence review, 2026-11-02d

## Recommendation and scope

**Recommend coordinator acceptance of the bounded P2 offline declaration/validation stage on the exact snapshot below. No unresolved reproduced P2 blocker is evident in the reviewed final run.** This is not acceptance of Phase 16, a produced poly assembly, physical source truth, a safe arbitrary-concurrency filesystem transaction, or live geometry. The coordinator must explicitly record the stage decision; the existing NOT ACCEPTED status in `CHECKPOINT.md`/`PLAN.md` is not changed by this report.

The distinction is substantive: all four original transitive fail-open findings, the deep-JSON failure, the two newly identified formula-dependency/incompleteness findings, ordinary refusal preservation, and the three red independent builder safety controls have current final-snapshot evidence. The remaining produced-poly, manifest/runtime/QA and physical-direction requirements are still missing evidence, not PASS. Known bounded/inherited limitations below must accompany any P2 acceptance.

Read-only review inputs were the retained final results, raw stdout/stderr logs, snapshot manifests, current test assertions, `Audit/_phase16-p2-session-2026-11-02d-brief.md`, the superseding third-session handoff, the bounded implementation brief, `PLAN.md` §4.0d, the detailed plan's P2/P3 partition, and relevant grammar/repair-boundary documentation. No previous conversation transcript was used. No broad suite was rerun. Short Python commands only parsed logs/AST and compared byte hashes/Git HEAD. **Only this new report was written**; no Max, installer, archive, installed-copy or AutoBackup operation occurred.

## 1. Final-run identity and independent read-back

Evidence directory: `Audit/phase16-p2-final-2026-11-02d/`.

- Recorder command supplied by the coordinator: `python -B Audit/run_phase16_settled.py --out Audit/phase16-p2-final-2026-11-02d`.
- `environment.json`: Python 3.14.4, `C:\Python314\python.exe`; started `2026-11-02T19:46:47.384432+00:00`.
- `snapshot-verdict.json`: finished `2026-11-02T20:07:54.859466+00:00`; **20 expected / 20 executed scripts**, all exit 0, `source_drift: []`, `git_head_changed: false`, acceptance deliberately `NOT_ASSESSED`.
- `process-exit.json`: `normal_end: true`, `changed: []`.
- Independently decoded all three manifests: before, after and process-exit maps are identical, **85 entries** (13 scripts, 21 Audit test/recorder files, 13 examples, 36 fixture files, plus PLAN and grammar). Every mapped current file still matched during this review. Current HEAD matched the recorded `7951e3f584be83e7655072a11bb193c1982128fe`.
- All 20 current `Audit/test_phase16*.py` files are represented in `results.json`; no current matching suite was omitted. Raw logs corroborate the summarized test counts, skips and xfail.

This supports **no observed snapshot drift**, not an immutable-filesystem or change-and-revert proof. It is also not a preservation census of unrelated user files: those lie outside the recorder's explicit manifest scope.

### Exact reviewed source SHA-256

| File | SHA-256 |
|---|---|
| `scripts/validate_specs.py` | `616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f` |
| `scripts/place_components.py` | `4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac` |
| `scripts/init_project.py` | `42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88` |
| `scripts/wall_cell_coverage.py` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` |
| `PLAN.md` | `9f69880641abcd2e3f4d897aa4ed90a16d60a16f1f94dce4ab9c74c41022e661` |
| `references/07-spec-grammar.md` | `d67959191f0358c53e9d297f3da6a074db302171ae20af711903cb449fd9ef0c` |

Retained evidence checksums independently read during review:

```text
2d1901ada0f06ecc2da7afc4a35c33add0d7eab1dfa3924362c9eeab00a4cfa7  results.json
089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72  hashes-before.json
089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72  hashes-after.json
089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72  hashes-at-process-exit.json
50ff5d713c5a593783fe8cd30fcbda81b902b60de6feaa912c2955742f9ffd97  snapshot-verdict.json
```

## 2. Test-run inventory, not an aggregate acceptance count

All entries below exited 0. Counts are reported unittest methods, not independent requirements or geometry checks. Subtests and validator-level SKIPs must not be flattened into a total of passing checks.

| Final script (`Audit/`) | Reported result / qualifier |
|---|---|
| `test_phase16_builder_repair_d.py` | 13 methods, OK; no unittest skip/xfail |
| `test_phase16_builder_review_d.py` | 14 methods, OK; no unittest skip/xfail |
| `test_phase16_input_fixture.py` | 1 method / **13 input-only mutation subtests**, OK; no skip |
| `test_phase16_legacy_build.py` | 10 methods, OK; no unittest skip/xfail |
| `test_phase16_legacy_builder_extra.py` | 11 methods, OK; no unittest skip/xfail |
| `test_phase16_legacy_coverage.py` | 37 methods, OK; includes tests asserting REVIEW/SKIP/refusal, not their promotion to PASS |
| `test_phase16_legacy_three_projects.py` | 2 methods covering all three actual legacy pipelines, OK; validator SKIPs remain 31/30/24 |
| `test_phase16_p2.py --require-p2` | **18 methods run, 21 skip events**, no failures; explicitly incomplete |
| `test_phase16_p2_cases.py` | 102 methods, OK, including 91 mutation cases; synthetic configuration/input tests |
| `test_phase16_p2_dependencies.py` | 15 methods, OK; scoped declaration statuses, not global source proof |
| `test_phase16_p2_isolated.py` | 34 methods, OK; no unittest skip/xfail |
| `test_phase16_p2_transitive_regression.py` | 48 methods, OK; includes honest unknown-formula incompleteness/build refusal |
| `test_phase16_scaffold_independent.py` | Standalone observation/control script, exit 0; `SOURCE_DRIFT []`; not a unittest count |
| `test_phase16_scaffold_repair_d.py` | 16 methods, OK; no unittest skip/xfail |
| `test_phase16_scaffold_review_d.py` | 7 methods, OK; mixes protective assertions with explicitly limited observations |
| `test_phase16_scaffold_safety.py` | 13 methods, OK; no unittest skip/xfail |
| `test_phase16_spatial_independent.py` | **17 methods: 16 ordinary successes, 1 expected failure** |
| `test_phase16_strict_upstream.py` | Standalone calibrated probe, exit 0; current, actual HEAD and selective-parser counterfactual outputs are distinguished |
| `test_phase16_validator_independent.py` | 26 methods, OK; historical-cycle negatives require its separate acyclic controls |
| `test_phase16_validator_review_d.py` | 29 methods / **156 CLI calls**, zero failures/errors/skips/xfails; empty source-drift maps |

### Exact disposition of the original harness's 21 SKIPs

Raw evidence: `test_phase16_p2.stderr.log:14-38`; assertion definitions: `Audit/test_phase16_p2.py:415-580`.

| Skip events | Actual unavailable coverage | Disposition |
|---:|---|---|
| 13 | `test_locked_wall_negative_mutations`: IDs, thickness/heights, block/contour/outward/epsilon, budget, opening order/range/run/overlap | The original harness requires a real locked poly pipeline and therefore still skips. **The same 13 input mutation branches actually ran** via `test_phase16_input_fixture.py`, with an empty synthetic draft assembly and no wall artifacts; this supplies bounded P2 input coverage, not produced-output coverage. |
| 3 | Locked poly assembly selector mismatch: legacy, unknown, null | Produced-pipeline instances remain untested here. Synthetic echo/configuration negatives separately exercise the P2 selector gate; they are not real assemblies. |
| 2 | Locked poly assembly containing `wall_cells` or `opening_cuts` | Produced-pipeline instances remain untested here. Configuration tests exercise forbidden presence/route exclusivity independently, without certifying a manifest. |
| 1 | Locked poly must not run legacy wall rules | Real produced route remains unavailable; synthetic route-applicability controls are static only. |
| 1 | Missing produced wall manifest must remain explicitly incomplete/refused | Output contract remains P3 work. G-96 stays SKIP/incomplete without the manifest; no full exclusivity PASS is asserted. |
| 1 | Real poly QA request with missing runtime observations | Poly QA profile/request/runtime observations do not exist. Deferred runtime evidence, never replaced with invented records. |

Thus **20 skip events depend on the missing produced poly fixture; one depends on missing real poly QA**. It would be incorrect either to call these 21 passes or to make every one a P2 blocker despite the implementation brief's explicit input/output partition. P3/later integration must eventually exercise them against authentic produced/runtime evidence. The original fixture guard is only a shape/status/lint guard: the observation script demonstrably passes it a labeled synthetic locked echo. It is **not artifact-provenance authentication**, and this review does not use that echo as production evidence.

The 102-case harness accepts alternative rejecting rules in some cases, so its green count alone does not prove every advertised predicate. The current 7-method scaffold review pins all ten opening injections to their exact G-93/G-94 failure sets and locations: five are G-93-only, three G-94-only, two both; G-94 is visibly SKIP rather than PASS when dependent structural checks fail. This disposes of the attribution concern without changing a rejection into fictitious coverage.

### Exact disposition of the one expected failure

`Audit/test_phase16_spatial_independent.py:250-276` uses ordinary `json.loads` to turn `10000000000000001.9` into `10000000000000002`, erasing a 0.1 cm gap **before** the spatial oracle receives the object. The test's requested REVIEW cannot be reconstructed from that already-rounded float. Its expected failure is a documented API-information-loss boundary, **not a protective test pass**.

The non-xfail `test_pre_rounded_api_boundary_without_expectedfailure_mask` in `Audit/test_phase16_scaffold_review_d.py:304-330` independently asserts the actual facts: clean prism PASS, rounded value equals `origin+2`, rounded input still PASS, and a representable 1 cm gap FAIL with a gap finding. Production validator and builder CLI tests separately refuse the lossy token before G-82/output. These independent controls avoid relying on an xfail that could mask failure at an earlier assertion. No exact-binary or live-Max precision claim follows.

## 3. Former P2 blockers — final evidence disposition

### All four original provenance faults have calibrated final controls

Primary evidence is the **current** raw `test_phase16_validator_review_d.stdout.log` plus `FourTransitiveControls` at `Audit/test_phase16_validator_review_d.py:196-236`. Every control has exit 0, no FAIL, and wall G-10/G-93 PASS. Every mutation has exit 1, wall G-93 FAIL and **no wall G-10/G-93 PASS**.

| Original fault | Clean control / exact negative scope |
|---|---|
| Bad transitive ledger cross-reference | Selects `structure.x_bay_cm`; actual `C-003` conflict edge is changed to `C-999`. Target assumptions G-31 FAIL and wall rejection are checked. |
| Invalid registry `derives_from` | Separate synthetic **acyclic** registry control; mutation names `NO_SUCH_FIELD`. Directory and `--file` modes reject; an unrelated G-31 FAIL is expressly excluded as a masking reason. |
| Registry backward reference to walls | Separate synthetic **acyclic** registry control; registry `origin_inputs` becomes `wall_runs[0].thickness_cm`. Target rejection is not masked by an unrelated G-31 FAIL. |
| Superseded massing behind NURBS | Selects `sections[0].points_cm` with a locked positive; massing changes to `superseded` and separately `draft`. The reached `elements[8].z_range_cm` dependency blocks wall PASS. |

The older 26-method review still logs the actual historical registry cycle and consequently has failing original registry “control” cases. Those two alone are **not calibrated positive evidence**. Its separate `acyclic_registry_control` and both corresponding mutations pass the intended discrimination, as do the new CLI-only controls above. The checked-in historical registry was not rewritten to manufacture an acyclic historical source.

Additional final controls exercise wall/upstream ledger owner, path, value and unique-ID binding; local multi-entry/self cycles; unknown/ambiguous owner paths; missing upstreams; duplicate owner copies; annotation linkage; invalid envelope/draft partial data; and no false aggregate wall PASS. These are binding/eligibility checks, not proof that any supplied drawing/source text actually contains the claimed architectural value.

### G-32 dependency and incompleteness findings are no longer open in these controls

- A known correct `building.total_height_cm` positive is calibrated **with its optional conflict annotation removed from both controls**, so annotation failure cannot mask wrong dependencies. Changing only `derives_from` to the unrelated ground-level path makes G-32/wall sourcing fail, despite unchanged arithmetic value.
- The 48-method regression covers required dependency coverage for documented formulas, missing-one-source versus unrelated extras, recognized intermediates/ancestor paths, and the nonzero-base height-chain boundary. This is a finite documented formula registry, not a generic algebra evaluator or exact execution-read tracing.
- A reached upstream derived value without a formula oracle yields G-32 SKIP and wall G-10/G-93 SKIP in lint, **not wall PASS**. `--build`, including `--allow-draft` and `--file`/`--rule` controls, refuses unavailable reached recomputation. An unrelated/unreached formula SKIP need not invalidate an independent wall source.
- Wall-local derived formulas without an oracle **still have G-32 SKIP**. Scoped G-10/G-93 can validate their declared dependencies while leaving arithmetic unproved. A wall-local derived optional `conflict_ref` makes linkage explicitly SKIP; non-derived annotations are not credited as verified bindings. Opposite valid unit normals can both pass declaration checks, whose text explicitly disclaims physical outward-side proof.

These limitations are visible and contract-scoped, not a blanket “every derived value/source verified” claim.

### Strict JSON and recursion

Final CLI-only review exercises duplicate status/geometry/ledger keys in both orders across used dimensions, assumptions, conflicts, massing, NURBS, facade grids, registry and walls, including nested keys and `--file` mode. It requires target G-7 FAIL, nonzero exit, no same-file G-7 PASS and no wall G-10/G-93 PASS. `--rule` filtering retains the underlying failed exit rather than hiding it. The standalone strict-upstream probe corroborates current refusal; its selective-parser counterfactual is explicitly **not an execution of historical actual source**, while separate HEAD legacy comparisons do execute actual Git bytes.

Lossy decimal tokens, overflow/underflow, NaN/Infinity and huge integer tokens refuse before a rounded value can reach a G-82 PASS. The independent CLI review separately reaches the declared epsilon bounds without parser masking. Caller policies differ legitimately and are tested: e.g. validator float spelling `9007199254740992.0` can parse, whereas initializer refuses its magnitude; integer-token acceptance and downstream G-82 numeric limits are separate. “Strict” is not a claim that every caller has identical float magnitude/depth policy.

The prior internal G-8 RecursionError has final boundary coverage:

- Validator text limit is **128 array/object containers including root**, quote/escape-aware, before decoding. In the independent inserted-array case, root plus 127 arrays succeeds; root plus 128 arrays and depths 450/800/1200/4000 produce controlled G-7 failure, no internal error/traceback or wall PASS.
- Regression tests check exact limits for arrays, objects and mixed containers; quoted/escaped delimiters; nested duplicate/lossy checks at the boundary; malformed shallow syntax still handled by the real parser; unexpected decoder errors not mislabeled as input refusals.
- Maximum accepted depth reaches units/leaves/provenance walkers; every used upstream/ledger has a separate positive and over-limit negative. A provenance chain longer than Python's recursion limit is traversed without a recursion crash, remains incomplete without formula oracles, and its cyclic version rejects.
- Initializer seed/ownership parsing has its own depth controls. The legacy builder has **not** acquired a universal independent 128-container scanner. None of this guarantees arbitrary direct cyclic Python-object safety.

### G-82 coverage and intentional compatibility tightening

Final 37-method spatial integration and 17-method independent results exercise the original missing `WAL-EL-014-C01` (inside the old aggregate volume budget), entire missing host cells, missing host element/cut pairing, equal-volume gaps/overlaps, filled openings, partial thickness, directions/elevations, and supported alternative partitions. They explicitly require FAIL/no spatial PASS for the reproduced defects.

A 0.1 cm gap has **WARN + SKIP** in lint, **FAIL** in build; warnings-as-errors promotes the warning. Unsupported profiles fail closed, no-openings yields NOT_APPLICABLE/SKIP rather than coverage PASS, and resource limits do not yield partial PASS. The builder refuses REVIEW/FAIL/NOT_APPLICABLE rather than building on uncertainty. Tests compare actual old Git emitter behavior: some near-tolerance/unsupported historical cases previously emitted and now refuse. The tested no-opening emitter already refused at its old empty-leaf self-check. Three supported actual projects retain byte parity; this is **not universal historical acceptance parity**.

The older volume subcheck's shorter-plan-extent/thick-wall false rejection is deliberately visible: a valid spatial prism can PASS the spatial oracle yet FAIL the volume rule. This is an inherited conservative limitation, not a repaired general wall oracle or proof of live coverage. Direct pre-rounded-float limitations remain as disposed above.

## 4. Actual legacy emitter bytes and refusal preservation

`Audit/test_phase16_legacy_three_projects.py:88-144` does not compare a handcrafted echo to itself. It copies each actual source pipeline to private temporary directories, runs lint/`--warnings-as-errors`/`--build`, invokes the **current production emitter** in normal and build modes, compares both JSON and MS bytes, then lints the actually generated assembly in a temporary pipeline. A separate test loads the real pre-P2 `place_components.py` and its `scene_units.py` via `git show 6c0f27b`, **executes both old and current emitters**, and compares their generated `assembly.json` and `assembly.ms` byte-for-byte for **each** project. No Git-baseline comparison was skipped in the retained run.

| Actual pipeline | Lint / warnings-as-errors / build | Static PASS / SKIP per mode | Current normal/build output and actual old-emitter comparison |
|---|---|---|---|
| `examples` | Exit 0; FAIL 0, WARN 0 | 140 / 31 | Both generated files byte-identical |
| `specs/fixtures/stepped-tower` | Exit 0; FAIL 0, WARN 0 | 147 / 30 | Both generated files byte-identical |
| `specs/fixtures/form-precision/specs/pipeline` | Exit 0; FAIL 0, WARN 0 | 155 / 24 | Both generated files byte-identical |

The raw log records the successful assertion methods, not retained individual output files/hashes: private outputs are cleaned by the tests. The byte-equality conclusion is supported by inspected assertions and successful final logs, **not a claim that this reviewer independently rebuilt or rehashed deleted outputs**. Original fixture hashes remain unchanged in the final manifests. Validator SKIPs cover script/live census/stacks, missing optional wall/QA/reserved files, absent generator/form/variant cases and unbounded/no-applicable rules; they are not new runtime passes.

The 10-method legacy boundary, 11-method extra builder, and independent 14-method review have actual positive emission before negative controls. Sentinels include a **valid route JSON with deliberately distinctive serialization** plus an MS sentinel, avoiding a malformed-output refusal masking the input under test. Assertions compare full input/output trees, not just exit codes. Covered refusals include draft/superseded explicit walls in all four flag combinations; calibrated G-93 faults; poly route; invalid/ambiguous selectors; same versus separate output; empty/missing, matching, conflicting or merely semantically-equal-but-byte-different wall documents; mid-build input changes; and link/path guards. Explicit separate output must already contain byte-identical walls; the builder does not silently copy them.

The three independent previously red safety tests are unchanged protective tests and now **ordinary passes**, not expected failures: second-file replacement failure restores the original pair when rollback works; injected late wall substitution does not commit mixed-route outputs; injected late directory substitution does not overwrite the separate victim. Additional repair controls cover absent outputs, first/second staging/replacement faults, input change during commit, explicit rollback failure/retained recovery bytes, parent change after the first replacement, lexical `..` refusal before any staging, and a staging-cleanup failure naming both causes and the retained path.

## 5. Standalone observations now assert the repaired behavior

The authorized supersession is documented append-only in `Audit/_phase16-scaffold-repair-2026-11-02d.md`; the current scripts were inspected, not accepted solely by their exit code.

- `Audit/test_phase16_scaffold_independent.py:245-280` injects one hardlink substitution at the **actual first staged descriptor fsync**. It asserts the hook ran once, exit 2, unchanged separate sentinel, explicit unsafe-output diagnostic, and no remaining owned temp. Retained stdout confirms `injected_substitutions: 1`, `sentinel_overwritten: false`.
- Its lines 282-340 inject a **17-character partial descriptor write into the second stage**, require exactly two descriptor opens/one fault, exit 2, old failed-file bytes intact, earlier complete draft committed, every other entry unchanged, no temp, and accurate preserve/inspect/not-whole-project-transaction guidance. Stdout confirms `failed_file_preserved: true`, `earlier_file_committed: true`. This is intentionally **not project rollback**.
- The script now asserts its source/fixture drift check, imports the captured initializer for in-process faults, preserves explicit seed source metadata, and rejects project laundering, forced route switching and authored-wall overwrite. Its mock locked-echo/fixture-guard demonstration and opening lines remain observations, not produced-output authentication.
- `Audit/test_phase16_scaffold_review_d.py:192-300` replaces successful-laundering/obsolete direct-write expectations with clean calibrated legacy imports, target duplicate/underflow G-7 failures, initializer exit 2/no destination/source preservation, actual **19-character** second-stage failure preservation, and one actual fsync hardlink rejection. None was skipped or xfailed. Other methods intentionally pin inherited non-wall `--force` overwrite and sequential earlier-commit behavior, not protective PASS for those broader properties.

The 16-method scaffold repair and 13-method safety suites additionally cover all used historical seed dependencies, numeric/depth/ownership boundaries, explicit source identity preservation, stale-route/wall guards, force refusal sentinels, and ordinary affected-file I/O preservation. Previously unsafe observation assertions were not preserved merely to manufacture a green vulnerability reproduction; their historical hashes/assertions/results remain in the repair report.

## 6. Acceptance boundary and remaining work

### Not unwaived reproduced P2 blockers in this evidence

The required original provenance faults now discriminate on clean positives; known formula dependencies/incomplete reached sources no longer retain a false full wall PASS; the deep-text regression refuses predictably; lossy production text refuses before rounding; original G-82 gaps are detected; all three real supported legacy outputs match executed historical emitter bytes; ordinary input refusals and named recovered-write/substitution tests preserve the asserted bytes. The final recorder includes all current Phase 16 suites and no observed source/fixture drift. This fulfills the reviewed **bounded P2** acceptance partition rather than silently waiving those findings.

### Explicitly retained limitations — do not broaden the recommendation

1. **P3/runtime absent:** no poly emitter output/manifest, real poly QA observations, new live wall geometry, measured stack/topology/units/replay or F02–F08 acceptance is proved. Static G-95/98/99/100 and incomplete G-96 remain SKIP. P1's earlier F01 spike is not integrated production acceptance.
2. **Source/geometry semantics:** path/ledger eligibility is not source-content authentication. Supplied outward sign/inner face, arbitrary wall-local formulas and cross-section/enclosure truth need independent evidence; no new physical claim is accepted here.
3. **Bounded I/O only:** builder rollback is recovered-exception protection when restoration succeeds, not two-file atomicity. A mixed pair is briefly observable; crash, power loss, rollback failure or a later parent swap can leave recovery work. Scaffold commits sequentially without whole-project rollback. Neither uses immutable handle locks or closes arbitrary check/use race windows; successful named injections are not hostile-concurrency certification.
4. **Inherited force and compatibility:** explicit authored walls/routes receive guards, but recorded non-wall paths remain overwritable under historical `--force`. Strict invalid/lossy JSON refusals, REVIEW/unsupported coverage refusals, per-caller numeric policies, byte-identical separate-wall output requirement and parent-traversal spelling refusal are intentional documented restrictions, not universal backward compatibility. The thick-wall volume limitation remains.
5. **Status/operations:** coordinator alone records P2 acceptance and decides whether to begin P3. No installation/archive/global overwrite/prune or Max access is authorized by this report. A fresh read-only scene snapshot is still required before future Max access; declined AutoBackup operations and cancelled materials/export remain excluded.

**Final disposition:** accept only the tested offline P2 scope with these explicit qualifiers; carry produced/live/source-semantic and bounded-safety limitations forward as unresolved later evidence or inherited constraints, never relabel them PASS. Any future source/fixture/contract change invalidates the exact-snapshot association and requires a proportionate new verification gate.
