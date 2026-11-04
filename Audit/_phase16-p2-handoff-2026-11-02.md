# Phase 16 P2 — interrupted-session hand-off, 2026-11-02

P2 is **in progress, uncommitted, not accepted**. The full live-state note is at the top of
`CHECKPOINT.md`. Read `AGENTS.md`, `CHECKPOINT.md`, `PLAN.md`, then the integration audit and
implementation brief before editing. `Audit/_phase16-p2-integration-audit.md` was already
untracked when this session started; preserve it.

## User decisions and safety

- User authorized Max work on the empty scene, but requested that this session stop and resume in
  a new session. Last read-only scene snapshot: 0 objects, unnamed, system units mm / scale 1.
  Never reset or remove user scene data. Confirm the current scene again before live work.
- `C:\Users\Turbolamer\Documents\3ds Max 2026\autoback` contained 10 `AutoBackup*.max` files.
  User explicitly chose **not to copy them**; do not modify them or change Max autoback settings
  without new permission. Files may naturally be overwritten by future Max autosaves.
- The `.skill` archive and installed copies have not been rebuilt or updated. The installer prunes
  its owned destinations; inspect its actual effects and protect unfamiliar files before running.
- Keep historical `legacy_cells_v1` working; the new poly builder and poly runtime QA are **absent**.
  New scaffold selects poly in draft; this is not a production-ready construction route. Materials
  and export remain outside the current task.

## Artifacts and current validation

Changed tracked files at hand-off: `CHECKPOINT.md`, `references/07-spec-grammar.md`,
`scripts/init_project.py`, `scripts/place_components.py`, `scripts/validate_specs.py`. New untracked
files: `Audit/_phase16-p2-implementation-brief.md`, this hand-off, the Russian prompt
`Audit/_phase16-p2-next-session-ru.md`, and independent harnesses
`Audit/test_phase16_p2.py`, `Audit/test_phase16_p2_cases.py`; the prior integration audit is also
untracked. Do not discard/overwrite these changes. Re-check `git status` and diffs on resume.

The orchestrator observed `python -B Audit/test_phase16_p2.py --require-p2 -v`: 18 tests, 22 skipped
subcases; no locked poly output fixture or poly QA evidence. `python -B Audit/test_phase16_p2_cases.py
-q` produced 102 tests OK (91 synthetic fault cases), **but ran while the validator was being edited**.
Re-run once changes settle. These tests miss independently reproduced fail-open conditions below.
`git diff --check` reported no errors at the time, only Windows LF/CRLF warnings. Historic baselines:
examples 138 PASS, stepped-tower 145 PASS, form-precision 153 PASS before P2; expect changed PASS/SKIP
counts after additive gates, but no regressions or unexplained FAIL.

Some agent-owned work was still finishing at the time this hand-off was written. Re-read the actual
tree and any later notes; do not assume a finding is fixed, or still unfixed, without a fresh control.
The validator author subsequently reported `numeric_unit_epsilon` capped at `1e-3`, poly G-96
SKIP until a validated manifest exists, and passing legacy plus synthetic fixture regressions.
That cap is not yet synchronized with the brief/grammar and the independent provenance audit
was not included in the author's acceptance report. Re-test after all concurrent work completes.
The independent test audit reported that 86/91 injections trip the intended rule, while five
opening cases only trip G-93 instead of their other listed gate. Several tests are masked by another
failure: notably contour off-line by a simultaneous outward-vector error, and negative opening
coordinates by G-93 when G-94 is disabled. NaN/Infinity tests exercise parser G-7 rather than a
valid JSON float-overflow case. The test positive for zero topology ceiling checks the current
declaration contract only; adjacency-by-ID does not prove geometric contact. Add isolated controls
before crediting these cases as proof of individual checks.

## Audit findings to reproduce, fix and negatively test

Independent read-only subagents reported these; some were demonstrated in-memory using the synthetic
fixture in `Audit/test_phase16_p2_cases.py`, but **the orchestrator has not re-run them after the
last validator edits**:

1. A wall origin marked `assumed`/`conflict` can point to an existing but unrelated ledger ID and
   pass. Require the ledger owner/path/value relationship, not merely existence of `A-001`/`C-001`.
2. `derives_from` self-reference and multi-node cycles can pass, and `origin_inputs` may resolve in
   walls itself instead of an upstream spec. Require bounded, traceable upstream joins and acyclicity
   with positive and negative controls; avoid breaking valid legacy projects.
3. A non-dict run can result in `G-93 FAIL` while `G-97` says PASS for only the other runs. Incomplete
   draft data with absent unit epsilon may fail to reject an explicitly zero normal. `G-93` can say
   PASS while a separately checked envelope field fails. Each PASS must cover its stated scope.
4. Seed import may silently take the last duplicated route key; investigate strict parsing and route
   consistency before writing. A JSON `1e999` was reported to parse to infinity, and a very large
   `numeric_epsilon_cm` was accepted. Test finite/overflow behavior and define any bounds explicitly;
   do not conflate numerical epsilon with construction tolerances.
5. Review route discovery for unreadable/symlink/non-file `walls.json` and duplicate specs in parent
   and `pipeline/`, including `--file`. Audit `--rule` output: reported JSON exit code may use filtered
   findings while the process exit code uses all findings. Confirm and repair without silently changing
   established CLI behavior.
6. `--allow-draft` and an empty draft poly assembly with legacy array keys were reported to pass;
   clarify intended input vs output gate and exercise both. G-96 was changed to SKIP for poly even if
   a synthetic manifest exists; do not infer a valid built route from a file existing.
7. `outward` is currently an explicit, supplied semantic direction. A unit perpendicular vector can
   still point inward. Only an authoritative contour/reference-face provenance or an independent
   geometry oracle can determine its sign; do not invent it from a compass label. Measure separately
   from volume in the future live gate.
8. Legacy G-82 tolerates a deleted `WAL-EL-014-C01` because 1,134,000 cm³ lies within its aggregate
   volume budget (~1,635,900 cm³). This is an existing QA limitation, not evidence of full coverage;
   the legacy test marks it SKIP. Decide and scope a safe independent coverage check.

Do not silently loosen user requirements to make tests pass. The implementation brief's current
facade-only straight-run subset cannot represent every valid upper return; keep such cases visibly
unsupported rather than claiming the full method is implemented. Reconcile the exact P4–P6 phase
numbering between `PLAN.md`, `CHECKPOINT.md` and `Audit/AGENT_PLAN_poly_surface_shell.md` before
executing future phases, preserving all acceptance gates.
