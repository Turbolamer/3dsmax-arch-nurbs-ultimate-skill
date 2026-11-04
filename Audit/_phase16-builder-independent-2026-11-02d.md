# Independent legacy builder review — 2026-11-02d

## Verdict and scope

**The calibrated explicit-wall input/refusal boundary passed on the snapshot below;
end-to-end write safety did not. Do not describe the entire builder audit as green
or use it alone to accept P2.** Three independently reproduced safety limits remain:
non-atomic JSON/MS pair commit, a final-check wall-route substitution window, and a
final-check parent-directory substitution window. Their new tests are ordinary
failing tests, not expected failures or skips. Whether an inherited concurrency
limit is an accepted boundary needs an explicit orchestrator/user decision; this
review does not silently waive it or authorize a source repair.

Exclusive authored files: this report and
`Audit/test_phase16_builder_review_d.py`. Production scripts, existing tests,
fixtures, scene, installer, archive and installed copies were not modified. All
test writes were to private copies under
`C:/Users/Turbolamer/AppData/Local/Temp/opencode`. No Max call, checkout or reset.
The synthetic wall declaration is **input only**, not produced poly output or a
physical direction oracle. The existing declaration's legacy selector is a route
control, not evidence that S5 consumes its wall-run sizes as the legacy geometry.

Read actual `scripts/place_components.py`, the spatial oracle, both existing
builder tests, the session brief/02c handoff, CHECKPOINT beginning and PLAN §4.0d.
A read-only graph query was only routing context; current source and executed
controls, not the older graph, determine the findings.

## Exact source snapshot

Final repeat: all five source hashes were unchanged for the full new 14-test
run; both existing suites also passed their own stability guards. The original
first 10-test run **was preliminary**: its frozen validator was `ed9e64dd...`, and
the teardown detected concurrent validator repair. That result was not accepted;
the complete 10-test suite was rerun after repair to the snapshot below.

| File | Byte SHA-256 |
|---|---|
| `scripts/place_components.py` | `8fdedf46fd3d955f3cb0f5a25e7652d74f0c83b3ac043f86a60d8ddf283b01b8` |
| `scripts/validate_specs.py` | `3675bd7f8d8ae16542a9f3a2d03eb4189447ab592080c1cf506e8cd80dba2ec1` |
| `scripts/wall_cell_coverage.py` | `d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e` |
| `scripts/scene_units.py` | `b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2` |
| `scripts/curve_gen.py` | `4e304cfe558988b9a4d285df57ea34668ec9352f68bb18a83bab10a63208b55c` |
| `Audit/test_phase16_legacy_build.py` | `4493b3fcba24d7cbf7895a562128c392c469a9971c711aef78f8ecda9aace15c` |
| `Audit/test_phase16_legacy_builder_extra.py` | `4e976bd6e63bc8a1ab51576ff5dd4ac4c697096d3c6cbb9ded06915efad3adfc` |
| `Audit/test_phase16_builder_review_d.py` | `e280ccce84d700a3eacb2a8184da7950606cd80e74a02747716c3da61bf77e91` |
| Input `specs/fixtures/poly-shell-input/walls.json` | `b9fe25a37d2948779ba8ca504447834346a3ed228c765c212b0c64d0412ecc93` |

The 14-file examples + input-wall fixture manifest was unchanged:
`0b51e0bb532b6d5daf33a995744e7ea7bbb567769d68310d7f07703349765efa`.
Manifest algorithm: map sorted repository-relative POSIX filenames to byte
SHA-256, then SHA-256 of `json.dumps(mapping, sort_keys=True).encode()`.

Historical source was obtained with **actual `git show`, no checkout**:

```text
git show 6c0f27b:scripts/place_components.py
  c0bda8dbff0beba6ff4f38cfb8535ea744e56024ffd81cf16cbfb9c926fa99af
git show 6c0f27b:scripts/scene_units.py
  b31e703f8364d08da78a3b3be8e0e4cfd315915d8748ee0698ef1f5d1443ceb2
```

Any later source change makes these results snapshot-specific, not final-tree
evidence. The orchestrator must rehash/rerun if validator repair continues.

## Commands and observed results

Run from `D:/Rhino/3dsmax-arch-nurbs-ultimate-skill`:

```bash
python -B Audit/test_phase16_legacy_build.py -v
python -B Audit/test_phase16_legacy_builder_extra.py -v
python -B Audit/test_phase16_builder_review_d.py -v
```

| Final repeat | Observed outcome | Time | Skips/xfails |
|---|---|---:|---|
| Existing legacy-build suite | 10 tests OK, exit 0; source guard passed | 198.330 s | 0/0 |
| Existing extra-builder suite | 11 tests OK, exit 0; source/fixture guards passed | 52.963 s | 0/0 |
| New independent suite | 14 tests: **11 OK, 3 FAIL**, exit 1; source/fixture guards passed | 90.600 s | 0/0 |

All three were independent shell processes with independent disposable snapshots;
no live source was patched into a test. The existing suites were inspected, not
weakened. New failures are listed below, not hidden in an aggregate green count.
Git history and symlinks were available, so no historical/link control was skipped.

The initial existing extra suite also ran 11 OK on `ed9e64dd...` before the
concurrent repair; that earlier result is superseded by the final repeat. The
new suite was executed twice against `3675bd7f...`, both times with the same
three failures and no source drift; after tightening the failure diagnostics, the
final repeat above is the artifact-of-record.

## Calibrated input/output boundary

New controls independently cover the following; existing suites provide
additional per-field/route and numeric cases rather than being trusted by count:

| Boundary | Positive calibration | Negative / observed behavior |
|---|---|---|
| Explicit `walls.json` status | Locked walls build in both same/separate output layouts | Draft and superseded refuse in **all four** modes: no flag, `--allow-draft`, `--build`, `--build --allow-draft`; matching wall bytes prevent output mismatch masking |
| Target G-93 | Full validator clean control has exit 0 and G-93 PASS; builder actually emits 136 placements / 16 cuts / 52 cells | Change only `blocks[0].z_range_cm` to `[420, 0]`: G-93 FAIL at `walls.json::blocks[0].z_range_cm`, no G-93 PASS; builder refuses with G-93 in same/separate layouts |
| Same `--out` with no old pair | Remove only copied `assembly.json/.ms`, keep locked explicit walls and upstream inputs | Builder produces only its declared assembly pair, no wall copying or poly outputs |
| Separate matching output | Identical regular locked walls already present; valid JSON sentinel + script sentinel can really build | Refusals below are not caused by malformed JSON sentinels |
| Separate empty output | Matching-output build passes first | Refuses missing pre-existing identical wall document and creates no files |
| Separate conflicting walls | Matching-output control passes first | Different geometry, project/status or route refuse without changing either input or output bytes (existing suite covers extra fields/routes) |
| Semantically equal wall JSON | Same decoded object on both sides | Different serialization is refused: policy is **byte identity**, not semantic identity |
| Explicit snapshot recheck | Unmodified control builds | Append valid whitespace to `dimensions.json` during rendering: final snapshot check refuses before writes and output pair stays byte-identical |
| Pre-existing output links | Same ordinary-directory control builds | Existing directory symlink is refused; existing suites also execute regular-file symlink/hardlink refusal controls |

For all deliberate refusal controls, entire disposable output trees (not just the
script) were compared byte-for-byte, including valid distinct JSON sentinels.
Same-directory cases cover input preservation as well. The deliberate mutation
hook itself changes its input file; only that explicitly injected change is
excluded from the mid-build input-preservation assertion. No `SKIP` is used as PASS.

Source path: `require_legacy_wall_route` (~646),
`verify_explicit_wall_inputs` (~736), `require_safe_output_route` (~693),
`verify_snapshots` (~883), and `main` (~3100–3158). The route gate precedes
geometry, explicit dependencies require locked status despite `--allow-draft`,
and the validator's actual PASS findings are required rather than treating
missing/unsupported findings as success. There are two input/output rechecks,
but no atomic claim can be inferred from check-then-use code.

## Actual historical compatibility, not a counterfactual

Every historical row below executes the untouched old builder and its old
`scene_units.py` from `git show 6c0f27b` against the same disposable inputs.
The current spatial oracle is applied independently to the old output.

| Copied no-selector legacy inputs | Actual historical builder | Current builder |
|---|---|---|
| Unmodified supported example | Success; same/separate output and ordinary/build modes | Success; assembly JSON/MS bytes equal historical bytes |
| All openings removed, matching obsolete opening-origin entries removed | Refuses older G-9 self-check: uncovered empty `opening_cuts` / `wall_cells` leaves | Same earlier self-check refusal; do **not** attribute this observed refusal to a new oracle regression |
| Host `EL-014` top raised by `0.000001`, `0.499999`, or exactly `0.5` cm | Succeeds and old summary advertises G-82 `pass` | Oracle is REVIEW; current builder refuses in normal and `--build --allow-draft` modes; sentinels unchanged |
| Host top raised by `0.500001` cm | Succeeds and old summary advertises G-82 `pass` | Oracle FAIL; refuses in both tested modes; sentinels unchanged |
| Nonrectangular host: insert `[900, 1]` into `EL-014.profile_cm` | Succeeds using the legacy bbox-style interpretation | Oracle FAIL unsupported geometry; current builder refuses, no silent fallback |

The existing extra suite also directly measures the no-opening oracle status
as `NOT_APPLICABLE`; current builder explicitly refuses every non-PASS oracle
status, but the real CLI reaches the older G-9 failure first in this fixture.
The delta-zero control is PASS and byte-identical, separating the new refusals
from a broken fixture or historical tool. Linear tolerance `0.5` cm is **not** an
allowed gap or endpoint error: every nonzero tested discrepancy is inconclusive
or failure, never PASS. This is a real, intentional compatibility tightening,
not proof of full historical compatibility or of live Max geometry.

Additional numeric compatibility is documented and tested by the existing extra
suite: lossy decimal decoding and integers beyond +/-`(2**53-1)` are refused,
including on no-selector legacy projects. Equivalent safe decimal spellings
retain historical output bytes. This is decimal round-trip guarding, not a claim
that binary floats or Max coordinates are mathematically exact.

## Open write / path safety findings — reproduced, uncorrected

### B-D1 — pair write is not atomic; second-file I/O failure leaves a mixed pair

`main` writes JSON then MAXScript at lines ~3157–3158. Each file gets a private
`mkstemp`, fsync and `os.replace`, but there is no pair transaction or rollback.
The new test injects `PermissionError` only when replacing `assembly.ms`, after
a separately successful calibrated build. Actual result:

- Nonzero process exit with an **uncaught traceback** (the `main` handler catches
  only `Refusal`, not the OS error).
- `assembly.json` has changed to bytes identical to the successful control.
- `assembly.ms` remains the old sentinel.
- No temporary-file leak in this injected failure.

`test_safety_second_file_io_failure_must_not_leave_partial_pair` consequently
**FAILS** the desired preservation assertion. First-file replacement failure is
a separate passing control: both original sentinels survive, no temp leak, but
it also returns a raw traceback. That passing control proves only first-file
failure preservation, not adequate I/O diagnostics or pair safety.

This pair limitation is **inherited**, not new evidence that the P2 input gates
regressed. Read-only AST extraction of the actual old source confirms the same
JSON-then-MS calls and only-`Refusal` exception handler. The current writer does
improve temp-name safety: historical code used a predictable PID suffix; current
code uses `mkstemp`. Per-file replacement does not solve pair atomicity. Crash
durability and all possible OS error points were not exhaustively simulated.

### B-D2 — route substitution after final successful check can commit mixed routes

`test_safety_final_wall_substitution_must_not_commit_mixed_route` wraps the
actual `require_safe_output_route` and, **after its second/final successful
return**, changes only the disposable output `walls.json` selector to poly.
Production logic is otherwise unchanged. Actual result: builder exit **0**,
output walls now `poly_surface_shell_v1`, generated assembly still
`legacy_cells_v1`. Its desired refusal assertion **FAILS**.

Earlier status/content rechecks work, as the mid-render input mutation control
demonstrates. They do not lock wall-file identity/content across final check and
commit. This is a deterministic timing injection modeling an attacker/concurrent
writer, not a claim that a naturally scheduled race was observed. No poly
geometry or output-provenance acceptance is implied.

### B-D3 — directory substitution after final check redirects both output writes

`test_safety_final_directory_substitution_must_not_overwrite_victim` validates
directory-symlink capability, lets the final route check finish, renames the
disposable output directory aside and replaces it with a symlink to another
private sentinel directory. Both victim `assembly.json` **and** `assembly.ms`
are overwritten; original parked script sentinel remains untouched. The victim
preservation assertion **FAILS**. Existing link guards reject the same link
when it is present before checking, which is the calibrated negative control.

`mkstemp(dir=path.parent)` and later path resolution still follow a substituted
parent directory. Per-file `os.replace` does not bind the parent identity.
This models a precisely timed path substitution; no real external/user file was
touched. There is no hostile-concurrency-safe directory/handle commit here.

### Important non-finding: late leaf hardlinks are not equivalent to parent swaps

A separate passing injection replaces only `assembly.ms` with a hardlink after
the final check. The writer replaces that directory entry; the protected
external private file keeps its sentinel and its link count returns to one.
Thus **this** test does not show arbitrary external-file truncation by a leaf
hardlink. Do not generalize the parent-directory failure to all leaf-link cases,
or claim the existing guards make the whole path operation race-safe.

## Remaining acceptance boundaries

- Three red new safety tests remain until fixed or explicitly dispositioned;
  no production editing was within this reviewer's ownership.
- This is offline input/build safety evidence, not full validator provenance
  review, P3 implementation, produced poly fixtures, or a live scene acceptance.
- Supported-example historical byte parity does not waive unsupported geometry,
  exact-coverage REVIEW, no-opening self-check limits, or the older thick-wall
  volume heuristic limitation recorded in the handoff.
- This report does not prove wall `outward` physical sign, actual JSON source
  truth, arbitrary concurrent writer protection, pair crash atomicity, or final
  repository acceptance. Rehash/rerun all relevant suites after any further edit.
