# P3 source review — publication-first independent pass, 2026-11-02e

**Status: snapshot-specific review, not P3 acceptance.** Prepared after reading the frozen coordinator
contract and clarifications. The latest steering requests publication helper/tests first; other modules
are still being authored and require main's later final pass. Only this new report is modified;
`Audit/_phase16-p3-contract-review-2026-11-02e.md` remains unchanged. No Max, installs, git writes,
source/test edits or fixture edits. Reproduction writes were confined to newly owned approved temp trees.

## 1. Publication verdict and exact evaluated bytes

```text
c43a9e8b4816fa50c26d36ee6eca14daeb6509805f250837e3859f5fe7200027 scripts/wall_surface_publish.py
718834b8474156fcb19e023154e0ea769402249811ff4a650b5d306a43241106 Audit/test_phase16_p3_publication.py
```

Both were read in full. An independent Windows repeat of
`python -B Audit/test_phase16_p3_publication.py -v` ran **39 tests / 0 failures / 0 errors / 0 skips**,
exit 0. Source/test hashes were identical before/after; the suite independently asserted unchanged
publisher and P2 input-fixture bytes. Test count alone is not the verdict: the actual helper and test
assertions were reviewed, with the additional focused controls below. The author report is evidence,
not an independent acceptance source.

### PUB-1 — confirmed boundary mismatch, caller gate required

`wall_surface_publish.py:27,203-219` admits **32 MiB per file**, not the frozen contract's **2 MiB
combined pair**. The author's size-bound tests intentionally prove that per-file behavior by replacing
the constant; they do not prove the production P3 pair ceiling.

**Independent reproduction:** the real helper successfully published two payloads of 1,048,577 bytes
each: total **2,097,154**, exceeding the contract pair ceiling **2,097,152**. Exact resulting bytes
were verified. This is a real public-helper acceptance boundary, not an inferred allocation estimate.

**Action:** either narrow the helper or explicitly keep it internal/lower-level and retain the CLI's
combined pre-publication gate. The evaluated coordinator snapshot has `sum(map(len, artifacts.values()))
> MAX_ARTIFACT_BYTES` with `MAX_ARTIFACT_BYTES=2*1024*1024`; this is the appropriate caller boundary,
but its integration must be independently tested on final settled bytes. Require combined-size exact
limit/limit+1 controls and assert the publisher is **not called** on refusal. Do not label helper-only
39-test success as proof of the pair ceiling. Empty bytes and CRLF test artifacts likewise validate
publication mechanics only; they are not syntactically valid produced wall artifacts.

### PUB-2 — no new bounded overwrite/partial-pair defect reproduced

The helper snapshots immutable `bytes`, closes names, stages a new sibling, records created-file
identities before writes, handles short writes, flushes/fsyncs, and checks exact membership, regular
single-link identities and byte/hash readback. Publication uses actual Windows `os.rename`, not
`os.replace` or two separate final-file moves. Existing outputs always refuse; cleanup is nonrecursive
and checks the whole recorded ownership set before unlinking. These observations support the stated
**controlled local single-writer / detectable-substitution** boundary, not arbitrary timing safety.

Two independent controls beyond the author's suite:

- **Late case-insensitive collision:** injected an ordinary file at `CASE-RUN` immediately before real
  Windows rename to `case-run`. Windows raised `WinError 183`; foreign collision bytes and the separate
  sentinel stayed identical; the owned staging directory was removed. This checks real filesystem
  name collision behavior rather than replacing rename with a mock failure.
- **Second cleanup unlink failure:** injected rename failure, allowed deletion of owned JSON, then
  failed deletion of owned MS. The helper raised an explicit original+cleanup `PublicationError` with
  `evidence_path`; no final output existed, exactly the owned MS residue remained, and a foreign binary
  sentinel was unchanged. Partial cleanup evidence is correctly not presented as a complete recovery
  pair. The experiment's own temporary owner later removed only its test tree.

### PUB-3 — retained limits, not repaired defects or waived guarantees

- Parent/stage/file checks are path-based checkpoints, not held handle-relative locks. In-place changes
  after verified readback and arbitrary substitutions between checks remain outside the advertised
  guarantee; do not expand the claim based on the tested injections.
- Ordinary drive-letter spelling is checked, **not actual local drive technology/backend**. A mapped
  network drive is not excluded merely by spelling. Main must admit a known controlled local output
  parent; helper alone does not prove that operational precondition.
- No fallible filesystem call follows the helper's confirmed rename; it never deletes published
  output. The CLI may independently read back afterward, but a post-commit refusal must preserve
  output/recovery evidence rather than imply nothing was published or retry by overwriting.
- Process interruption/uncertain commit, directory durability and malicious filesystem providers remain
  explicitly unsupported. `Exception` cleanup is not a power-loss or asynchronous-interruption promise.

## 2. Other-module observations: provisional, NOT final source review

All named modules appeared during the single initial capture; none is currently being polled. The
first console dump stopped on CP1251 encoding in the publisher, not on a source exception. A subsequent
single in-memory integration probe used freshly byte-hashed source, **no Max and no artifact publication**.
Runtime/coordinator hashes changed between captures, so observations are not a settled-tree assessment:

```text
43b030d156eab30dd93aeff5db12b91d3f0938a294d48dbed23734f4b2d11c6b scripts/wall_surface_inputs.py
305bd91ad8875683235072ee718c5b6251d6369f8ec43ec8e8b143f594b1e399 scripts/wall_surface_runtime.py (initial full capture)
8ec319c0cf0d838dac5207e3f022c46f114f0bd935d19105a2d286a7a9eb14dd scripts/wall_surface_runtime.py (later probe bytes)
2e9a63489c05497afbf5d00fc2686ac8bd76487fb50dd7a2a73f2c3d4409856b scripts/build_wall_surface.py (later probe bytes)
```

- The initial read showed subset/node-name disagreements between modules; the **later actual-module
  in-memory F01 probe did not reproduce those disagreements**: both used
  `single_standalone_straight_inner_wall`, metadata and emitted source named `ReviewF01__wall`, and
  `make_artifacts` returned without an exception. Do not report the earlier disagreement as current.
- Independently constructed F01 input yielded plan predictions 24/38/15 grid V/E/F, 12 kept polygons,
  36 active edges, 24 boundary edges, 87,000 cm2, 48/96 evaluated polygons/triangles and 2,610,000 cm3.
  This checks deterministic Python planning only, not provenance admission or actual Max geometry.
- Generated guard source separately compared **type**, **scale** and factors; expected mm/1 yielded
  explicit `actualType == #millimeters` and `actualScale == 1.0d0` checks. This source observation is
  **not execution** of either positive or equal-factor/different-pair negative in Max.
- Initial runtime catch walked `createdRefs` only. Because conversion can invalidate the old reference,
  independently prove retained/reacquired handle cleanup and residual reporting on a failure at that
  boundary; an invalid reference must not silently imply no residual exists. This remains a review
  target, not a new live claim.
- Initial input inventory copied only recognized domain JSON. Review whether contradictory preexisting
  produced manifests/scripts can be ignored by the snapshot adapter and hence appear missing to the
  validator; frozen contract requires contradictory outputs to refuse. **Not yet reproduced.**

## 3. Frozen-contract rubric for main's one final pass

The following gates are **NOT REVIEWED to completion** on final stable bytes, regardless of any author's
test result. Require byte-hash-stable source and independent target-specific controls, not broad test
counts or a manifest echo:

1. **Input snapshot:** exact raw bytes used by validator and emitter; inventory closure/duplicates,
   source membership/path/drift checks; original upstream/ledger eligibility, no input rewrites; safe
   empty-draft assembly exception only; existing contradictory output detection.
2. **Formula refusal:** all required reached/local/implicit-contour derived inputs have an actual
   recomputation oracle and dependency coverage; unknown required G-32/annotation incompleteness
   refuses. Demonstrate a clean positive and isolated unsupported formula, not a masked unrelated FAIL.
3. **Authority:** exact closed operational record bound to wall/source hashes and run/coordinates;
   source cannot be wall/authority self-attestation; distinguish human attestation from automated source
   semantic proof. Independent F01 source/sign review is mandatory; reversing both declaration and
   winding against unchanged physical source must not pass merely by matching one another.
4. **Units/numerics:** exact expected type/scale/factor comparisons before mutation and replay inspection;
   equal-factor different pairs must refuse. Bound source and mapped native Float32 error, nonzero
   thickness/cells, distinct stations; no snapping or accidental design-tolerance substitution.
5. **Ownership/replay:** exact node/base/modifier references and scene-local registry; copy tags/names,
   lost identity, modified user state, material/stack/controller/dependency changes refuse without
   mutation. Complete supported-state fingerprint must fail closed on unknown serialization. Bound
   work **before** unbounded graph/property/scene enumeration, not after allocation. Prove actual
   no-op replays, not a printed counter. Save/load/merge persistence remains unsupported.
6. **Mutation cleanup:** no prefix/name deletion, reset, hidden host or unrelated edits. Conversion
   identity and failed cleanup must expose precise residuals; new registry publication failure must
   not falsely imply complete rollback. Main checks actual bridge error/exception markers.
7. **Artifacts/integration:** exact schema/status/node/stack consistency, deterministic identity and
   independently checked script hash, combined 2 MiB pre-publication gate, final readback/recovery
   semantics, no canonical assembly deployment or installed-package update hidden inside the CLI.

**Next action:** main supplies one final settled-module review pass after authors stop. Publication
mechanics have the bounded independent evidence above; no P3/live/whole-method acceptance is inferred.

---

## 4. Requested final actual-source pass — 2026-11-03, provisional where bytes moved

This supersedes earlier open/current dispositions **only as explicitly stated below**; older exact-hash
evidence remains historical. Main's latest steering stops broad-suite repetition while the coordinator
recorder owns the settled run. Runtime and publisher changed between the initial capture and focused
controls, so this is **not a hash-stable whole-source acceptance**. No Max or source/test/fixture edits
were made by this reviewer. Only this report changed.

### Exact snapshots

Final focused reproductions used these exact bytes; the four executable hashes and contract were
identical before/after those controls and at the final read-back:

```text
4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f Audit/_phase16-p3-contract-2026-11-02e.md
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
03c9accba70648e677fdb837a436256186d2535f438e553910f38cc8725f8c59 scripts/wall_surface_inputs.py
5df101ab21f935d63f061c2f7d7c18659aba3e359970b6d3bb9516b873372ba2 scripts/wall_surface_runtime.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
```

Initial final-pass runtime was `da74c759170f4263f9467c137bf93bf291f3d251cc1cec67513034e74fe967cb`,
publisher `c43a9e8b...`. These are **not** the later focused snapshot. Final observed test hashes:

```text
1a4e77a6d4ceae9c8f0d7c69152400238bd04635b7252ff3dd2ca5f99c0a43a5 Audit/test_phase16_p3_builder.py
2ed71edc4935cce80c0b7ff835368249eecc9389e767aadf5f051423be97c3d2 Audit/test_phase16_p3_inputs.py
b3fa77a48aa538090641528341b338921aa7fd5bcf2f07bd0b1235cac2ba63b4 Audit/test_phase16_p3_runtime.py
7b62cb2117378c1cb81131c8e7df60eb5a61eeea3dda5051c47566d5ba9ba42d Audit/test_phase16_p3_publication.py
```

### FINAL-1 — BLOCKER reproduced: existing contradictory artifact files are ignored

`wall_surface_inputs.py` snapshots only `INPUT_NAMES` recognized domain JSON; the private validator
therefore cannot see original `wall_surface.json` or `wall_surface.ms`. The coordinator checks consumed
source paths but does not inventory those existing artifacts before accepting missing-output SKIPs.
This contradicts the frozen contract's **existing contradictory output is refused** rule.

**Isolated actual public-builder reproduction**, each calibrated by successful genuine F01 emission:

1. Copy the authentic F01 project and operational authority to an approved owned temp tree.
2. Add `project/wall_surface.json` containing
   `{"schema_version":"bogus","project":"FOREIGN","route":"legacy_cells_v1"}`.
3. Call actual `build(...)` to a disjoint new directory: **ACCEPTED/published**.
4. Remove only that owned injected file; add `project/wall_surface.ms` containing an explicitly
   contradictory `resetMaxFile #noPrompt` script, never executed. Actual builder again **ACCEPTED**.

Injected files remained byte-identical; the issue is **ignored contradiction**, not source overwrite or
execution. No fabricated assembly was used. Fix belongs to source owners: inventory and refuse/validate
existing route artifacts at the same project/pipeline boundary, bind that inventory to drift checks,
and add calibrated clean/contradictory/late-membership controls. Existing legacy-assembly refusal alone
does not close this manifest/script case. This finding is on coordinator `a2b05348...` + inputs
`03c9accb...`; no repair was reviewed here.

### FINAL-2 — earlier size mismatch repaired in the observed publisher; focused controls pass

Publisher `7868798b...` now checks **combined** `MAX_PAIR_BYTES=2 MiB` before hashing/staging; the older
32 MiB-per-file constant remains redundant defense. Independently verified the actual helper accepts
exactly **2,097,152** combined bytes and refuses **2,097,153**, with `mkdtemp` asserted **not called**
on the latter. This supersedes PUB-1 as a current helper defect; its earlier reproduction remains
historically true on `c43a9e8b...`. The publisher's final expanded author suite is **not rerun here**;
the coordinator's settled recorder must cover that repaired source/test pair.

The actual coordinator `make_artifacts` was independently exercised with the real runtime plus
controlled source padding: exact 2 MiB pair accepted, plus one byte refused. Both checks concern
artifact-byte admission, not geometry or replay. No oversize artifact was sent to Max.

### FINAL-3 — independently discriminated input/authority/output-chain controls

- Actual public F01 `build` emitted the two expected files, correct script SHA and offline/unverified
  status. Its actual generator-hash closure contained nine entries: coordinator, three helpers,
  validator, scene units, curve generator, legacy coverage helper, and frozen contract. No unrelated
  previously imported test module was credited as generator input.
- **Private same-byte snapshot:** instrumented actual validator load to inspect the private wall bytes,
  then changed the original wall after snapshot. Parsing stayed on the captured private bytes, but
  actual builder refused `input changed since snapshot: walls.json`; no output directory was created.
  This is the documented observed-drift model, not an immutable concurrent-writer lock.
- **Missing formula:** replaced the selected facade's individual origins by one valid-shape collapsed
  `derived` origin from `site.footprint_cm`, avoiding overlapping-origin masking. Actual public builder
  refused `required derived formula unavailable/failed ... facades[0]: no documented recomputation`.
  Restoring original bytes restored a successful build. No formula was invented or laundered to given.
- **Authority CWD:** authentic relative source token resolved from repo CWD; changing only CWD to the
  owned request directory refused the missing `Audit/...` source with no authority-directory fallback.
  Raw authority/source hashes, token and resolved path are retained separately. The CLI help text itself
  still does not state this CWD convention; add user-facing help/documentation before hand-off, as the
  frozen contract expressly requires. This documentation gap is not a source-hash bypass.
- **Physical source drift after actual rendering:** generated the actual script, then changed only an
  owned copy of the analytical authority source. Public build refused `observed input/code drift`;
  a mocked publisher was asserted **not called**. Changed input bytes were not overwritten.
- Authority remains explicitly a **human-authored attestation**, not semantic validation of arbitrary
  text. Independent F01 source/sign review and the paired winding+declaration negative remain main's
  physical acceptance work. Do not turn matching hashes/attested vectors into a physical-truth PASS.
- Unit source still separately checks type/scale/factors before inspection/mutation, so equal-factor
  pair equality alone cannot authorize it. Independent Python source guards are not a live mismatch
  test; actual MAXScript pair/factor negatives remain main-owned.

### FINAL-4 — runtime safe refusal is NOT replay support; P3.1 still blocked

Latest inspected runtime `5df101ab...` deliberately contains unconditional `INCOMPLETE_REPLAY` after
observed baseline equality; it cannot emit a successful no-op replay from that branch. Main separately
reported live `LayerPropertiesMixinInterface` anim-handle/reference enumeration failure. That report
is **main-provided evidence, not executed by this reviewer**. Keeping uncomparable layer/interface
state fail-closed is correct; skipping the field, treating pointer presence as equality or weakening
the fingerprint would not close acceptance.

The explicit-arm design now matches the coordinator clarification: wall source requires an already
armed structured lease, never auto-arms a missing registry, poisons failed creation attempts, retains
created references/handles for bounded cleanup, and requires main's external exact lease witness.
This is not save/load/merge durable ownership, nor proof of full metadata/dependency comparison.
Runtime's broader fingerprint and three successful no-op replays therefore remain **INCOMPLETE**;
the unconditional refusal must not be counted as a replay PASS or renamed idempotence.

### Verification disposition / stop point

- Independently ran builder suite **34 tests OK**, and a contemporaneous runtime source suite **40
  tests OK**. The latter preceded later runtime/test edits and is not evidence for the final hash pair.
- An initial capture-all-suite wrapper timed out without completed captured results; a separate broad
  input-suite attempt also timed out. Neither is credited as PASS. A direct authentic-F01 adapter
  control did complete successfully. No long-suite repeat is made after main's stop steering.
- Final focused controls above completed on identical before/after executable+contract hashes. All
  authored inputs/artifacts were in newly owned temp trees, removed only by their own temp owner;
  preexisting fixtures/sources remained unchanged by this reviewer.

**Main gate:** repair FINAL-1; retain repaired pair-size protection; finish/retain explicit runtime
INCOMPLETE rather than unsafe replay claims; then freeze authors and run the coordinator's settled
recorder plus actual published-artifact `fileIn`/independent measurements. No P3.1 acceptance, live
geometry PASS, installer approval or Phase 16 completion follows from this source review.

## 5. Independent existing-output regression delivered; narrow repair verified

Ownership was explicitly extended to the new
`Audit/test_phase16_p3_existing_output_review.py` only, in addition to this report.
The independent test is now frozen at:

```text
5d58f7bd742828e1731661b283edd3644d21b0bfba02f411e6b4594edfcf884e Audit/test_phase16_p3_existing_output_review.py
```

**Executed quick command:** `python -B Audit/test_phase16_p3_existing_output_review.py -q`:
**7 tests / 0 failures / 0 errors / 0 skips**, **6.878 s**, normal exit 0. These are seven actual
CLI calls: clean positive through the real late-generation hook; invalid JSON alone, MS alone,
contradictory pair, each initial and after the real script generator returned executable wall source.
Late controls require a marker containing the actual generated-script hash, not a mocked output echo.
Every negative checks exit 1/clean refusal, unchanged original and injected sentinel bytes, no new
output pair and no staging residue. Source/fixture hashes were identical before/after.

The test freezes unmodified Python source and authentic F01 **input** bytes into an approved owned
temp tree; source/authority text is never executed. No synthetic produced fixture is used. An initial
expanded 21-CLI matrix also passed all project/parent/pipeline boundary cases in 20.507 s. To keep the
requested default under 10 s, final test retains that wider matrix behind `--all-boundaries`; its
default is the seven project-local cases above. No broad review/suite has been reopened.

Actual source snapshot for both independent runs:

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12 scripts/wall_surface_inputs.py
f966cbdd9b582df90cad33bfa5b0d2acde44429ccad85fe410629261d474acf5 scripts/wall_surface_runtime.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
```

**Disposition update:** FINAL-1 is **repaired for these exact tested initial/late-presence cases** on
inputs `5c1e3134...`; do not carry the previous red reproduction forward as a current failure on that
hash. Its historical source/hash/results remain intact above. This narrow closure is not arbitrary
concurrent substitution protection, broader metadata/replay acceptance or a whole P3 acceptance.

**Remaining main gate categories:** (1) actual final artifact/arm `fileIn` and measured safe-refusal
behavior are main-owned, not proven by these offline tests; (2) layer/native-metadata/full replay stay
explicitly INCOMPLETE, never advertised as three successful no-op replays; (3) source/authority/unit
and publication protections must survive the coordinator's forthcoming settled recorder; (4) no
installation or full-phase acceptance. Main reported the arm catch compile failure and the owner's
bare-throw-only repair at runtime `f966cbdd...`; this review has not executed that repair in Max.
Test/report authoring is stopped here for the coordinator freeze. No future tests are claimed run.
