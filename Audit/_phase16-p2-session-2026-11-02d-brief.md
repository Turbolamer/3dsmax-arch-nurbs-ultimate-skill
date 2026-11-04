# Phase 16 P2 resumed verification — 2026-11-02d

User scope: preserve all current files and changes; finish independent legacy builder
and validator verification before accepting P2. P0/P1 stand. P3 is blocked until
genuine P2 acceptance. Read `_phase16-p2-resume-2026-11-02c.md`, `AGENTS.md`,
`CHECKPOINT.md` beginning and `PLAN.md` §4.0d. That handoff's tests are historical,
not final evidence. Main thread has read them; no new behavior is yet verified.

Required controls: open deep JSON G-8 RecursionError; four transitive provenance
mutations with separately clean acyclic positives; strict JSON at all used upstream
boundaries, precision/overflow; G-82 spatial coverage; refusal preserving existing
output bytes. Use disposable copies under approved OpenCode temp directory. No
changes to existing projects, AutoBackup files, archive or installed copies. No Max
tools in subagents. Main has made no scene call. Materials/export excluded.

Independent file ownership for this session:
- Validator repair: `scripts/validate_specs.py`,
  `Audit/test_phase16_p2_transitive_regression.py`,
  `Audit/_phase16-validator-repair-2026-11-02d.md` only.
- Builder independent review: `Audit/test_phase16_builder_review_d.py`,
  `Audit/_phase16-builder-independent-2026-11-02d.md` only.
- Validator independent review: `Audit/test_phase16_validator_review_d.py`,
  `Audit/_phase16-validator-independent-2026-11-02d.md` only.
- Scaffold/coverage/harness review: `Audit/test_phase16_scaffold_review_d.py`,
  `Audit/_phase16-scaffold-harness-review-2026-11-02d.md` only.
- Grammar reconciliation: `PLAN.md`, `references/07-spec-grammar.md`,
  `Audit/_phase16-grammar-review-2026-11-02d.md` only; preserve P2 unaccepted status.
- Coordinator: preservation manifests, `Audit/run_phase16_settled.py`, final run
  logs/reports, handoff and `CHECKPOINT.md`.
- Builder repair (opened after independent failures): `scripts/place_components.py`,
  `Audit/_phase16-builder-repair-2026-11-02d.md`, optional new
  `Audit/test_phase16_builder_repair_d.py` only; independent tests are read-only.
- Scaffold repair (opened after independent import failure): `scripts/init_project.py`,
  `Audit/test_phase16_scaffold_safety.py`, new
  `Audit/test_phase16_scaffold_repair_d.py`,
  `Audit/_phase16-scaffold-repair-2026-11-02d.md`. Correct stale per-caller numeric
  expectation without removing initializer negatives; independent observations
  remain unchanged until explicitly reviewed against the repaired implementation.

All other source is read-only to reviewers. Report concrete failures rather than
silently patching outside ownership. No transcript reading. Short final summary
(under 12 lines) plus written artifacts, commands and source hashes. If sources
change during tests, clearly mark preliminary; main reruns on the settled tree.
Do not represent synthetic input/assembly echoes as produced poly output. No
installer run or graph rebuild is authorized. Use patch tool for edits.

Later explicit ownership extensions: the scaffold owner may update
`Audit/test_phase16_scaffold_independent.py` and
`Audit/test_phase16_scaffold_review_d.py` to supersede obsolete laundering/direct
write observations with calibrated protective current tests. Historical hashes,
assertions and outcomes remain in the appended scaffold repair report. No skips
or weakened refusal assertions are authorized. Grammar owner reopened its same
files for the repaired strict import / staged write / formula boundaries.
