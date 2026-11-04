# Phase 16 P2 — bounded scaffold repair, 2026-11-02d

## Outcome and exclusive ownership

**Reproduced historical JSON laundering is repaired. Bounded per-file I/O refusal no longer
truncates the destination. This is not whole-project atomicity or P2 acceptance.**

Edited only the newly authorized files:

1. `scripts/init_project.py`
2. `Audit/test_phase16_scaffold_safety.py`
3. New `Audit/test_phase16_scaffold_repair_d.py`
4. This report.

The previous review/observation tests and report remain byte-identical and historical. No fixture,
project, other source, Max scene, installer, archive or installed copy was edited. No Max call,
installer run or archive rebuild occurred. Temporary copies are under the approved OpenCode root.
Tests introduce no produced poly fixture or live evidence.

## Strict seed parsing repair

- Every used seed now goes through the **same strict initializer parser**, including all eight
  historical no-wall dependencies. Removed the route-conditioned permissive parsing switches.
  Duplicate keys at any object nesting level, non-finite constants, overflow, underflow and decimal
  tokens that change under `Decimal(token) == Decimal(str(float(token)))` are refused before any
  destination directory/file is created. It is intentional that ambiguous/rounded historical files
  accepted previously now **refuse**, rather than being normalized into apparently clean output.
- Integer tokens and floating-token magnitude remain bounded to `±(2^53−1)` for initialization.
  Floating tokens are limited to 1024 characters, before conversion. This is a copier safety policy,
  not a geometry tolerance or proof of exact binary representation. Valid shortest-decimal tokens
  (`0.1`, `0.1000`, `1e-3`, `5e-324`, safe integer endpoints) remain accepted.
- Added an iterative quote/escape-aware **128-container nesting guard including the root** before
  `json.loads`; no recursion-limit changes or suppression of arbitrary exceptions. 129/160/4000
  nested containers controlled-refuse. Shallow invalid syntax still raises JSONDecodeError.
  The depth boundary protects subsequent recursive JSON encoding/origin inspection. It does not
  claim safety for arbitrary cyclic Python objects supplied directly to unrelated functions.
- Ownership manifest parsing (`existing_creations`) now also uses the strict/depth-bounded parser;
  malformed/deep manifests produce no overwrite authorization, not an uncaught RecursionError.
- Explicit-wall identity/source-preservation and route checks are retained. Valid historical
  no-selector imports still have **no `walls.json`, no assembly selector/wall_ref**, identical domain
  values/ledger references, and the historical source re-stamping behavior. Original fixtures are
  read only and hashed; their bytes are unchanged.

### Numeric policy test correction (not suppression)

`test_explicit_seed_numeric_policy_and_documented_validator_difference` now declares separate
initializer and validator parser expectations. In particular:

| Token | Initializer | Validator parser | Scope |
|---|---|---|---|
| `9007199254740992` | refuse | refuse | Out-of-range integer token |
| `9007199254740992.0`, `1e20` | **refuse** | may accept, observed accepts | Documented caller-specific floating magnitude policy |
| `1e-400`, lossy decimals, NaN/Infinity/overflow | refuse | refuse | Ambiguous/lossy/nonfinite numeric decoding |

The initializer negative still executes for each refused token and asserts exit 2/no destination.
The old failure at the validator-comparator assertion is not hidden with skip/xfail or a broad catch.
Parser acceptance does not imply G-82 range/arithmetic or geometry acceptance.

### Small fresh-scaffold integration correction

An actual original-harness smoke check initially failed against the validator owner's newly stricter
G-32: `building.net_floor_area_m2` omitted `core.spans_level_indices` from its declared inputs.
Added that existing formula dependency to the initializer's fresh dimensions origin only; no values
or checked-in fixture origins changed. The independent repair test checks all three declared inputs
and recomputes `gross − core_area × core_level_count`. The original fresh-scaffold check then passed.
This failure is recorded, not counted as a passing run or bypassed by weakening the validator.

## Per-file staging and exact safety boundary

Replaced direct destination `Path.write_text` with `write_staged_file`:

1. Preflight snapshots each destination's no-follow `lstat` identity/size/timestamps/mode/link count.
2. Before writing, rechecks parents and destination state, refusing observed symlinks/reparse points,
   hardlinks, nonregular files and changed destination state.
3. `mkstemp` exclusively creates a regular sibling in the same directory. Content is written using
   that already-open descriptor (`fdopen`), not by reopening a named temp path. Flush and fsync finish
   before closing. The final destination is **never opened for truncation**.
4. Rechecks parents/destination state, plus staged leaf identity/size/type/link count; then uses
   `os.replace` for that one file. Windows can update timestamps on writer close, so staging identity
   comparison intentionally does not demand identical pre-close timestamps.
5. Cleans the owned staging path on ordinary failure/success. A cleanup failure is reported and must
   be inspected; it is not silently promoted to all-or-nothing recovery.

**Verified guarantees under bounded single-owner/recoverable I/O conditions:** injected partial
staging write, fsync failure, and replace failure preserve old bytes of the affected destination and
remove the normal owned temporary file. A first-file failure preserves the entire preexisting project.
Late hardlink substitution before staging or at the injected fsync boundary is refused with the
separate sentinel unchanged. No final-leaf target is followed for a truncating content write.

**Not promised / remaining boundaries:**

- Files still commit **sequentially**, manifest last. A later failure leaves earlier complete new
  files beside later old/missing files. No project-level rollback, multi-file transaction, pair
  atomicity, crash/power-loss durability or recovery auto-migration is claimed. Failure advice now
  states that the failed file was not committed and prior completed replacements remain.
- State checks are check-before-use, **not locks or directory-handle-relative hostile-concurrency
  protection**. A parent-directory swap, final race after the last inspection, or adversarial temp
  namespace modification is not proven safe. The command explicitly excludes concurrent mutation.
  Do not extrapolate the two bounded hardlink controls into hostile concurrency acceptance.
- `--force` retains historical path-based overwrite semantics for recorded **non-wall** files;
  authored non-wall content is not protected by the wall hash/template guard. Existing wall/route/
  stale-artifact refusal checks are retained. Initialization is not a universal source-provenance
  authenticator, full schema validator, content hash attestation or produced-output validator.
- Replacement may change filesystem metadata such as file identity/permissions inherited by the
  new staging file; preserving all ACLs/attributes and cross-filesystem/network semantics is not
  verified. Staging is same-directory specifically to avoid a normal cross-filesystem move.

## Regressions, final commands and source stability

Final immutable executable copy and retained logs/hashes:

```text
C:/Users/Turbolamer/AppData/Local/Temp/opencode/phase16-scaffold-repair-d-check-elsxbe9v/
  frozen/                 exact executable/test/fixture snapshot
  hashes-before.json      full byte SHA-256 manifest
  results.json            command results and source_drift: []
  repair.{stdout,stderr}
  safety.{stdout,stderr}
  original-scaffold.{stdout,stderr}
  isolated-seed.{stdout,stderr}
```

`-B`/`PYTHONDONTWRITEBYTECODE=1`; approved TEMP/TMP/TMPDIR; no fixture writes. Final results:

| Command | Result |
|---|---|
| `python -B Audit/test_phase16_scaffold_repair_d.py -v` | **16 OK**, 18.931 s; 0 skips/xfails |
| `python -B Audit/test_phase16_scaffold_safety.py -v` | **13 OK**, 35.232 s; 0 skips/xfails |
| `python -B Audit/test_phase16_p2.py --require-p2 LegacyRegression.test_from_examples_preserves_legacy_route PolyAcceptance.test_fresh_scaffold_declares_poly_and_stays_draft PolyAcceptance.test_invalid_or_missing_selector_does_not_fallback_to_legacy -v` | **3 OK**, 4.293 s; 0 skips/xfails |
| `python -B Audit/test_phase16_p2_isolated.py RoutingAndCli.test_seed_duplicate_route_key_rejected_before_writing RoutingAndCli.test_seed_float_overflow_rejected_before_writing -v` | **2 OK**, 3.257 s; 0 skips/xfails |

All **34 selected tests passed** and every captured source/test/fixture hash stayed unchanged over
that final batch. This is bounded repair evidence, not the final all-suite orchestration gate.
Builder/validator owners are active; main must independently rerun the full settled suite later.

New independent controls cover every one of the eight historical dependencies, with clean positive
imports first; root/nested duplicate-key negatives; underflow and two distinct lost-precision tokens;
source bytes unchanged; no destination created; invalid import with `--force` preserving a preexisting
project; actual original `ground_level_cm:1e-400` laundering case; huge numeric tokens; controlled deep
input/ownership refusal; valid near-smallest floating tokens; all three legacy fixture domain/value/
selector checks; partial write/fsync/replace failures; hardlink substitutions; no whole-project rollback.
Each dependency's added numeric probe has its own accepted `0.1` control before the rejected probes,
so unknown-property rejection is not mistaken for strict numeric decoding.

Initial development runs: 12 then 15 repair tests passed; earlier snapshot had the one actual fresh
G-32 failure described above. A prior frozen batch used validator `686724c8...` while repository
validator/transitive tests changed; it is **not** final settled-tree acceptance. Final batch used
`61605041...` with no observed drift. `git diff --check -- scripts/init_project.py
Audit/test_phase16_scaffold_safety.py` exited 0 (Git LF/CRLF warning only); owned Python AST parsing
and trailing-whitespace inspection passed without bytecode.

## Explicit supersession of unchanged historical observations

The independent historical files were intentionally **not edited**. They now retain red assertions
about behavior this repair removes; do not silently filter them out in the coordinator's all-suite run.
An actual diagnostic run against initializer `42401725...` observed:

- `Audit/test_phase16_scaffold_independent.py`: exit 1 at line 268. It expects a `Path.write_text`
  injected hardlink race to overwrite a sentinel. There is no destination `Path.write_text` call now,
  so that injection no longer runs. This is a **superseded injection location/unsafe expectation**,
  not proof of hostile-race safety. The later old `Path.write_text` partial failure block is not reached.
- `Audit/test_phase16_scaffold_review_d.py`: 6 methods, 3 assertion failures. Two are duplicate and
  underflow subtests at line 214 expecting successful laundering; actual exit is now **2** with the
  appropriate duplicate/precision diagnostic. The third expects its old `Path.write_text` mid-file
  injection to run and return 2; actual is 0 because staging bypasses that hook. Independent new
  descriptor-write/fsync/replace failure controls replace that obsolete injection mechanism.
- The other four historical method behaviors (non-wall force, parser policy distinction, pre-rounded
  direct API limitation, exact ten-opening gate attribution) continued to pass on that snapshot.
- Earlier `Audit/_phase16-scaffold-harness-review-2026-11-02d.md` remains a historical pre-repair
  verdict. Only its laundering/direct-write statements are superseded by this report; its original
  skip inventory, synthetic-vs-produced warnings, outstanding scope/compatibility issues and lack of
  Phase16/runtime acceptance are **not waived**.

These historical nonzero results require explicit disposition in final orchestration. Do not change
them here, weaken new refusal tests, or label their intentional supersession as an all-tests PASS.

## Exact final byte SHA-256s

```text
42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88  scripts/init_project.py
11b4d04a37e626771a29eda890cb9b7c83eff9f86b3042856c97cea526cfd302  Audit/test_phase16_scaffold_safety.py
4b393c7aef78a17d56198f9fd562e5305882d2a42bbb0a57e47ab2dae0142eba  Audit/test_phase16_scaffold_repair_d.py
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f  scripts/validate_specs.py (read-only final test snapshot)
7f8d4415aa9a95298f13b16d6b28e6c5e40feaed481564cfc841800f131b9cd4  scripts/place_components.py (read-only final test snapshot)
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e  scripts/wall_cell_coverage.py (read-only)
a4854182222ac6a9aca8d183d40c723a49992b113c90d3fae2556b21546b4614  Audit/test_phase16_scaffold_independent.py (unchanged historical)
5e4ace3af15226dfaa92e994ea43faace9c3b832ce7b188753e79f7f5ed96289  Audit/test_phase16_scaffold_review_d.py (unchanged historical)
```

**Edits stop after this bounded handoff.** No P3 work or P2/full-suite/live acceptance follows from
these repairs. Main retains responsibility for ongoing-source integration, explicit historical-test
supersession, grammar reconciliation and the independent final full-suite gate.

## Authorized runnable-test supersession — later 2026-11-02d addendum

**This addendum supersedes only the earlier instruction to keep the two runnable tests unchanged.**
The user explicitly granted new exclusive ownership of
`Audit/test_phase16_scaffold_independent.py`, `Audit/test_phase16_scaffold_review_d.py`, and append-only
ownership of this report. Production sources were stopped and were **not changed**. No other file
was edited, including fixtures, the original output/fixture guards, the sixteenth-test repair suite,
or the previous detailed review report. Earlier audit evidence and nonzero historical results above
are retained rather than deleted or relabelled as successful tests.

### Historical assertions retained as evidence, exact pre-supersession hashes

```text
a4854182222ac6a9aca8d183d40c723a49992b113c90d3fae2556b21546b4614  Audit/test_phase16_scaffold_independent.py
5e4ace3af15226dfaa92e994ea43faace9c3b832ce7b188753e79f7f5ed96289  Audit/test_phase16_scaffold_review_d.py
```

The old bytes remain in the earlier retained diagnostic snapshot
`C:/Users/Turbolamer/AppData/Local/Temp/opencode/phase16-scaffold-repair-d-final-7slg1w36/frozen/Audit/`.
Their recorded failures/tracebacks remain in that run directory and the report above. The precise
obsolete assertions were:

```python
# Old independent.py line 268: injected at Path.write_text, now unused by writer.
assert race_status == 0 and sentinel.read_bytes() != b"KEEP THIS SENTINEL\n"

# Old independent.py lines 293–295, behind the earlier failure:
# old Path.write_text PermissionError was expected to leave a new partial project.
assert first == 2 and not (partial / "project.json").exists() and second.returncode == 2
assert "preserve and inspect" in stderr.getvalue().lower()
assert "re-run with --force to continue" not in stderr.getvalue().lower()

# Old review_d.py lines 214–218, per duplicate/underflow subtest:
self.assertEqual(result.returncode, 0, result.stderr)
lint, cleaned = self.validate(copied)
self.assertEqual(lint.returncode, 0, cleaned["summary"])
self.assertEqual(read_json(copied / "dimensions.json")["site"]["ground_level_cm"], 0)

# Old review_d.py lines 237–243: Path.write_text hook itself truncated the target.
self.assertEqual(result, 2)
self.assertEqual(target.read_bytes(), b'{"synthetic_partial":')
self.assertIn("partially written", error.getvalue())
self.assertIn("preserve and inspect", error.getvalue())
```

Those were historical vulnerability observations, **not intended protective requirements**.
Keeping current tests green by reproducing the old unsafe behavior would be incorrect; skipping,
xfailing or suppressing them was not used. The positive single-owner legacy controls, real refusal
preservation, numeric-policy distinction, non-wall force boundary, pre-rounded API limitation and
exact opening-rule attribution remain required and runnable.

### Precise current replacements

- `test_historical_invalid_seed_refused_before_creation_without_source_changes` retains a clean
  legacy initializer+lint positive, then the same duplicate-project and actual `ground_level_cm`
  underflow mutations. Input G-7 must fail. Initialization must return **2**, identify the duplicate
  or precision error without traceback, create **no destination directory**, and leave every invalid
  source file's bytes unchanged for inspection. No rewritten output is manufactured and linted as
  purported repair evidence.
- `test_failed_descriptor_stage_preserves_old_file_after_earlier_commit` replaces the unused
  `Path.write_text` hook with the actual `os.fdopen` stream. A first output commits normally; the
  second staged descriptor writes and flushes **19 characters** before an injected OSError. It
  asserts exactly two descriptors reached and exactly one fault executed, exit **2**, failed target
  old bytes intact, earlier target changed to complete parseable draft JSON, every other project file
  byte-identical, and no owned `.tmp` left. It checks the explicit not-committed/prior-completed/
  not-whole-project-transaction/preserve-and-inspect guidance. It intentionally does **not** demand
  rollback of the earlier completed replacement.
- The independent script uses the same current descriptor mechanism, injecting **17 characters**
  into the second stage of an already-created disposable project. Its diagnostic output reports
  `descriptor_injections=1`, `failed_file_preserved=true`, `earlier_file_committed=true`, exit **2**.
  It asserts the same full other-file byte preservation and actual first-file commit. The old new-
  project/forced-retry observation is not misrepresented as having exercised this writer.
- `test_specific_hardlink_substitution_during_stage_is_refused` and the script's `HARDLINK_RACE`
  block now inject the link **at actual fsync of the first staged descriptor**, after successful
  preflight. They prove the injection ran exactly once; initializer returns **2**; the error names
  an unsafe regular output; the separate owned sentinel is unchanged; the linked target still reads
  sentinel bytes; no stage file remains. Review test also asserts every unrelated project file is
  unchanged. The target's namespace was changed by the test itself, not preserved by the initializer.
  These controls cover this timing only, **not arbitrary hostile-race or parent-swap safety**.
- No hardlink availability SKIP remains in the script: inability to execute that platform control is
  a real test failure. No fixed behavior was marked expectedFailure or xfail.
- The independent script imports the initializer from its **captured frozen source copy** for its
  in-process staging injections, instead of an earlier live import. Its final source/fixture drift
  report is now asserted rather than merely printed. This makes source drift a non-success requiring
  rerun, not a hidden qualifier. The synthetic fixture/output guard diagnostic is unchanged and still
  does **not** become a produced/live-output acceptance gate.

### Executed current-source rerun and hashes

Both owned tests ran directly from the repository against the stopped current production sources,
with all subprocess/test temporary directories rooted under approved OpenCode TEMP/TMP/TMPDIR.
Per-test scripts still freeze initializer/validator/oracle bytes for execution. Wrapper snapshots
covered all scripts, `Audit/test_phase16*.py`, examples and relevant fixtures before/after.

```text
C:/Users/Turbolamer/AppData/Local/Temp/opencode/phase16-scaffold-supersession-d-82jap94d/
  hashes-before.json
  results.json                 source_drift: []
  independent.stdout/.stderr
  review.stdout/.stderr
```

| Command | Actual result |
|---|---|
| `python -B Audit/test_phase16_scaffold_independent.py` | exit **0**, `SOURCE_DRIFT []`; actual hardlink injection count 1, exit 2, sentinel not overwritten; actual descriptor fault count 1, exit 2, failed file preserved/earlier committed |
| `python -B Audit/test_phase16_scaffold_review_d.py -v` | **7 tests OK**, 17.194 s; **zero skips/xfails**; drift guard passed |
| `git diff --check -- Audit/test_phase16_scaffold_independent.py Audit/test_phase16_scaffold_review_d.py` | exit 0 |
| Owned Python `ast.parse` and trailing-whitespace checks | passed without writing bytecode |

New test hashes and unchanged production-source hashes at completion:

```text
f4647da4b85ca467f98ac18033b849f5ad8a639d7b577f2e0b995f7630d87472  Audit/test_phase16_scaffold_independent.py
adebe35064ea408ec38403d63ec5b15159f87f2212c9793600f4bc843eb173b2  Audit/test_phase16_scaffold_review_d.py
42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88  scripts/init_project.py
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f  scripts/validate_specs.py
4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac  scripts/place_components.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e  scripts/wall_cell_coverage.py
```

**Supersession edits stop here.** The current runnable tests now encode protective fixed-behavior
requirements rather than obsolete vulnerability expectations. No blanket all-suite, output/runtime,
hostile-concurrency or P2 acceptance claim is made; independent final orchestration still owns it.
