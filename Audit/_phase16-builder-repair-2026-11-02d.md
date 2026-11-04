# Bounded builder repair — 2026-11-02d

## Scope and verdict

Only `scripts/place_components.py`, this new report, and the new
`Audit/test_phase16_builder_repair_d.py` were authored. All preexisting builder
edits were retained. The independent review and its tests are read-only and
unchanged. No project fixture, Max scene, AutoBackup, installer, archive,
installed copy, validator source, grammar or CHECKPOINT was edited here.
All behavioral test writes use disposable approved OpenCode temp copies.

The three reproduced defects are repaired **within a recovered-exception and
deterministic substitution boundary**, not by claiming a transactional filesystem:

| Finding | Actual repair / refusal behavior |
|---|---|
| B-D1 recovered second-file replacement error | Both payloads and exact prior bytes are staged before either replacement. Already installed entries are restored from private staged backups; a newly created first entry is unlinked only after its identity is checked. OS errors become exit-1 refusals, not raw tracebacks. |
| B-D2 walls changed after the final route check | A commit guard captures input/output route bytes and absent route entries before that final check; the writer compares them before staging, each replacement and completion. The injected selector change refuses before output modification. The builder does not undo the injected wall edit. |
| B-D3 output parent changed after final check | The guard remembers lexical parent-directory `(st_dev, st_ino)` identities and rejects symlink/reparse/non-directory/change before the writer creates staging files. The injected victim directory is not overwritten. The builder does not undo the injected directory swap. |

`read_spec` now explicitly calls `strict_loads(..., reject_duplicate_keys=True)`
for actual consumed JSON on **all** routes, including historical no-selector
projects. Invalid UTF-8 and JSON parse recursion at that boundary receive
controlled refusals too. The `strict_loads` helper's default was deliberately not
changed; production caller behavior, not merely a direct helper test, is verified.
Rejecting previously last-value-wins duplicate JSON is an intentional compatibility
tightening for ambiguous invalid inputs. The earlier strict numeric policy is
unchanged; this is not a promise of uniform float-magnitude behavior with the
validator.

## Implementation map

- `scripts/place_components.py:966`: actual `read_spec` strict duplicate read.
- `:3015`: lexical directory identity capture and verification (no `resolve()`).
- `:3047`: `OutputCommitGuard`, created after the initial route gate and before
  in-memory construction; the captured input/output route bytes are not silently
  replaced by whatever is present after the last check.
- `:3099`: `write_output_pair`, all payload/backup staging before replacements,
  rollback of recovered exceptions, identity checks before rollback, exact-path
  cleanup only. The preexisting single-file `write_bytes` helper was retained for
  compatibility but is **not called by `main`** and provides no pair protection.
- `:3292`, `:3337`: main constructs the guard and uses the pair writer.
- `:3341`: main's final OS-error boundary emits controlled exit-1 diagnostics.

No broad deletes were introduced. Cleanup only targets exact `mkstemp` entries;
rollback of a previously absent output only unlinks the exact installed entry
after a matching identity check. The positive late-leaf-hardlink control still
succeeds by replacing that directory entry, never truncating the linked victim.

## Guarantees deliberately NOT claimed

This is **not crash atomicity, a two-file atomic transaction, directory durability,
or arbitrary hostile-concurrency protection**. There are no Windows directory/file
handle locks and no portable `dir_fd`-anchored commit. `lstat` / byte comparison /
later path use remain separate operations; a new swap within those smaller
intervals is not eliminated by another check. In particular, a swap after a
successful guard but inside `mkstemp`, file read, `replace`, rollback or cleanup
can evade this bounded model. A stronger contract requires a separate reviewed
Windows handle-based design, not relabeling these checks as pinning/locking.

An unrelated writer can also observe the brief JSON/MS mixed state between the
two replacements. Process death, power loss, asynchronous interruption, disk
failure during rollback or arbitrary third-party file modification can prevent
recovery. A failed rollback emits **`ROLLBACK INCOMPLETE`** and retains/names its
old-byte recovery file rather than claiming preservation. A late directory change
after the first installed file refuses further writes, rollback and cleanup into
the victim; the original parked directory may then contain a new first file and
the retained recovery staging. This limitation is tested explicitly. Cleanup
failure emits a warning with retained paths; it is not hidden as leak-free.

Therefore the calibrated preexisting-output preservation statement covers the
reproduced first/second replacement failure with working rollback and the injected
pre-write late substitutions. It does not claim all possible OS failures restore
everything. No P2/P3/live acceptance follows from these offline tests.

## Initial repair tests and source stability (before edge-case follow-up)

Production source edits initially stopped at builder SHA below. Earlier iterations are
preliminary, not silently aggregated as passes:

- Initial frozen independent run: all 14 behaviors passed on builder
  `4ec5518b...`, but teardown failed because validator changed
  `3675bd7f...` → `979056a3...`; exit 1, **preliminary**.
- A later 14-behavior independent run and two 11-behavior extra-suite runs passed
  their assertions but failed their builder drift guards when docstring edits and
  the newly requested duplicate-key fix landed. These are **preliminary**.
- An initial legacy-build run was stopped by the shell's 120-second execution
  timeout before completing; **not a suite result**. It was rerun with a
  600-second allowance, without changing the test.

Commands from the repository root:

```text
python -B Audit/test_phase16_builder_repair_d.py -v
python -B Audit/test_phase16_builder_review_d.py -v
python -B Audit/test_phase16_legacy_builder_extra.py -v
python -B Audit/test_phase16_legacy_build.py -v
python -B Audit/test_phase16_legacy_three_projects.py -v
```

| Final-source run | Outcome |
|---|---|
| New owned repair regressions | **11 tests OK**, 1.827 s, no SKIP/xfail; builder/units source guard passed |
| Existing independent review | **14 tests OK**, 84.890 s, no SKIP/xfail; source/fixture guards passed; all three formerly failing safety tests now pass |
| Existing extra builder | **11 tests OK**, 50.694 s, no SKIP/xfail; source/fixture guards passed |
| Existing legacy build | **10 tests OK**, 180.666 s, no SKIP/xfail; source guard passed |
| Existing three legacy projects | **2 tests OK**, 24.701 s; all three valid project JSON/MS outputs match actual pre-P2 bytes; source/fixture guards passed |

The owned suite independently checks: successful changed/no-op/missing/nested
output writes; first/second replacement errors; no-old-pair second replacement
failure; second payload `fsync` failure; route-byte substitution; verified input
change after first replacement; ordinary parent-directory replacement; explicit
rollback failure with retained old-byte backup; parent symlink swap after the
first replacement (no victim writes/cleanup); early raw `OSError` containment;
and 12 actual CLI duplicate-key negative cases (three consumed JSON files × four
flag combinations), calibrated with a successful no-selector CLI build and
valid output JSON/script sentinels. Each duplicate refusal preserves the output
tree and the deliberately mutated input bytes.

The three-project suite reports validator-level SKIPs (31 examples, 30 stepped
tower, 24 form precision). These are existing unavailable/runtime/optional checks,
not unittest skips or wall/P3 acceptance. No missing runtime check is promoted to
PASS. Supported-byte parity does not remove the prior documented intentional
REVIEW/unsupported/numeric tightening or the thick-wall legacy volume limitation.

Both owned Python files parse with `ast.parse` without bytecode creation.
`git diff --check -- scripts/place_components.py Audit/test_phase16_builder_repair_d.py`
exited 0 (only the existing LF/CRLF advisory). New untracked files are not covered
by Git's tracked diff whitespace check.

## Initial repair source hashes (superseded by follow-up below)

| File | SHA-256 |
|---|---|
| `scripts/place_components.py` | `7f8d4415aa9a95298f13b16d6b28e6c5e40feaed481564cfc841800f131b9cd4` |
| `scripts/validate_specs.py` | `979056a31a0733fc588fded0cb6f40f5d924b233508ebcc2b152a9e00bf6d1ed` |
| `scripts/wall_cell_coverage.py` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` |
| `scripts/scene_units.py` | `b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2` |
| `scripts/curve_gen.py` | `4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c` |
| New owned `Audit/test_phase16_builder_repair_d.py` | `07b190719b8df41034dc36d617ef1bc358b11ee1f995e2d16a575e5825479e18` |
| Read-only `Audit/test_phase16_builder_review_d.py` | `e280ccce84d700a3eacb2a8184da7950606cd80e74a02747716c3da61bf77e91` |
| Read-only `Audit/test_phase16_legacy_build.py` | `4493b3fcba24d7cbf7895a562128c392c469a9971c711aef78f8ecda9aace15c` |
| Read-only `Audit/test_phase16_legacy_builder_extra.py` | `4e976bd6e63bc8a1ab51576ff5dd4ac4c697096d3c6cbb9ded06915efad3adfc` |
| Read-only `Audit/test_phase16_legacy_three_projects.py` | `02bd8c5e5b97c0788174211cc269a4b1fbb8b43032ffad8135c720503d0156c7` |

Rehash/repeat for any later validator or builder change. The coordinator owns
CHECKPOINT and final settled-tree acceptance; this report does not update them.

## Read-only review follow-up — two concrete edge cases

The stopped `7f8d4415...` builder had two additional, independently reported
defects. They were reproduced **before** source edits using new ordinary failing
tests in the owned repair suite, not waived as expected failures:

1. With `alias/` a real directory, `--in output --out alias/../output` addresses
   the same output directory but `Path.absolute()` preserves `..` spelling. The
   old-byte guard did not recognize its own installed assembly as replaced. Both
   alias directions reproduced **four staging files and two replacements** (JSON
   installation plus rollback) before a false changed-input refusal. The final
   old output bytes survived, but this was not an acceptable pre-write refusal.
2. Injecting the first staging `fsync` failure plus the first staging `unlink`
   failure produced a refusal naming **only the unlink failure**. The original
   fsync cause and the exact private retained file path were absent. Since
   `_stage_output` had not returned, the outer writer had never registered that
   file and could not issue its usual cleanup warning. The initial report's
   blanket cleanup-diagnostic wording was incomplete for this path.

The expanded suite on `7f8d4415...` ran 13 tests and failed these new assertions
(three failure entries: two alias subtests and one combined-error test). The
original 11 tests still passed. This is actual red-before-green evidence.

### Narrow repairs and policy

- `_directory_identities` refuses any input/output directory argument containing
  a lexical `..` component **before staging or directory creation**. No `resolve()`
  normalization was added: resolving could hide traversal through links and make
  the existing lexical symlink/reparse checks misleading. This intentionally
  tightens path spelling compatibility; callers must provide paths without parent
  traversal. Canonically spelled same-directory input/output still succeeds.
- `_stage_output` now separately guards cleanup of its exact private entry. If
  that cleanup fails, a controlled `Refusal` includes the original staging cause,
  the cleanup cause, and **`retained staging file <exact path>`**. The original
  exception is also retained as `__cause__`. No retry, glob or broad cleanup was
  added. The unregistered file is deliberately left and named, not falsely
  reported as removed or leak-free. This error is reported in the refusal itself;
  the outer `finally` warning only covers paths it has actually registered.

Both regression cases preserve the exact preexisting assembly JSON/MS bytes.
The alias test calibrates `os.path.samefile` and successful canonical same-directory
writing, then tests both alias directions with **zero mkstemp calls and zero
replacement calls**. The staging test verifies that exactly one private payload
remains, that it contains the staged bytes, and that the diagnostic names its
exact path and both injected errors. It verifies only that precise recovered
failure combination, not arbitrary OS faults or arbitrary concurrent writers.

### Follow-up verification and final hashes

No scope beyond these two concrete cases was audited or changed. Independent
tests remain read-only. All follow-up tests use approved private temporary copies.

| Follow-up command | Result |
|---|---|
| `python -B Audit/test_phase16_builder_repair_d.py -v` | **13 tests OK**, 1.756 s, zero SKIP/xfail; frozen builder/units source guard passed |
| `python -B Audit/test_phase16_builder_review_d.py -v` | **14 tests OK**, 81.760 s, zero SKIP/xfail; frozen source/fixture guards passed; B-D1/B-D2/B-D3 remain passing |
| `python -B Audit/test_phase16_legacy_three_projects.py -v` | **2 tests OK**, 23.455 s; source/fixture guards passed; all three valid project JSON/MS outputs retain actual pre-P2 bytes; existing validator SKIPs remain 31/30/24, not PASS |

The earlier 10-test legacy and 11-test extra results above remain evidence for
their exact **old** builder/validator snapshots, not the new source. The coordinator's
final full gate must use the hashes below. Follow-up source/test/report edits have
stopped after recording these results. The report's byte hash is supplied in the
handoff rather than embedded in itself.

| Follow-up file | SHA-256 |
|---|---|
| `scripts/place_components.py` | `4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac` |
| `scripts/validate_specs.py` at follow-up snapshot | `616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f` |
| Owned `Audit/test_phase16_builder_repair_d.py` | `8b4f75052c1fa40f8277693e931fd833a982d69fe9584c38b1ce0ef7352c62de` |
| Read-only `Audit/test_phase16_builder_review_d.py` | `e280ccce84d700a3eacb2a8184da7950606cd80e74a02747716c3da61bf77e91` |

Units/oracle/curve helper hashes remain those in the initial table. Both owned
Python files parsed via `ast.parse` without bytecode; neither had trailing
whitespace. All previously stated crash/rollback/arbitrary-race limitations
remain unchanged. These two repairs are not directory pinning or a file lock.
