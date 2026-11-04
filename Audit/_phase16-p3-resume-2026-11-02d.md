# Phase 16 — P2 accepted offline; P3 next session, 2026-11-02d

## Current decision and user steering

**P0/P1 stand. P2 is ACCEPTED in the bounded offline scope. P3 is NOT implemented.**
The user asked to stop here and begin P3 in a fresh session because context is full.
All agents have stopped; no pending shell or agent work remains.

The user's latest explicit permission (Russian, verbatim):

> Делай в Макс все что нужно, запрет унаследован случайно. Сейчас можно снять любые
> ограничения по этому поводу. Только давай в новой сессии, контекст уже забился

**The earlier blanket restriction/permission blocker on live Max work is withdrawn.**
Do not repeatedly request the same permission in the next session. Necessary P3 Max
work is now authorized, but was deliberately NOT started here at the user's request.
Use normal fresh-state, bounded-call, ownership, preservation and measured-QA safety;
this is not a reason to erase unrelated data, touch backups gratuitously, or waive
correctness. Materials/export remain outside the task; unfinished `.skill`/installed
copies must not be updated. No reset, scene write, save or AutoBackup access occurred.

## Read first

1. `AGENTS.md`, newest `CHECKPOINT.md`, `PLAN.md` §4.0d.
2. `Audit/_phase16-p2-verification-2026-11-02d.md` — coordinator execution/acceptance.
3. `Audit/_phase16-p2-final-evidence-review-2026-11-02d.md` — independent final review.
4. `Audit/_phase16-p3-design-2026-11-02.md` — **proposal**, not implemented/approved
   interface. Update its obsolete P2-blocked premise using this accepted evidence;
   do not treat its open contract decisions as already solved.
5. `Audit/AGENT_PLAN_poly_surface_shell.md` §§B/C/E/G/I and
   `Audit/EVIDENCE_2026-10-27.md` — preserve actual P1 facts, do not re-derive falsely.

## Exact accepted executable snapshot

```text
42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88 scripts/init_project.py
4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac scripts/place_components.py
616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f scripts/validate_specs.py
d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e scripts/wall_cell_coverage.py
```

HEAD `7951e3f584be83e7655072a11bb193c1982128fe` (`main`, ahead 5). Do not commit/reset/
checkout/clean without user intent. All original tracked/untracked changes remain.

### Final tests actually executed by coordinator after all edits stopped

`python -B Audit/run_phase16_settled.py --out Audit/phase16-p2-final-2026-11-02d`

- **20/20 scripts exit 0**, no per-suite/end source/fixture drift, HEAD unchanged.
- **85 hashes** identical before/after/normal exit and independent read-back.
- Both original harnesses ran: original 18 methods / **21 SKIP**, cases **102 OK**.
- Builder independent **14 OK**, builder repair **13 OK**, legacy build **10 OK**,
  extra **11 OK**, coverage **37 OK**, dependencies **15 OK**, isolated **34 OK**,
  transitive **48 OK**, validator independent **26 OK**, new CLI review **29 OK /
  156 calls**; scaffold repair/review/safety **16/7/13 OK**. Standalone scaffold
  and strict-upstream scripts exit 0 with their actual protective assertions inspected.
- Input-only adapter executes all **13 wall mutation subtests** with synthetic walls
  and an **empty draft assembly**. It is not produced output or live evidence.
- Spatial review **17 methods: 16 ordinary success + 1 xfail**, not 17 passing gates.
- Three actual legacy pipelines lint/strict/build FAIL 0/WARN 0, PASS/SKIP
  **140/31, 147/30, 155/24**. Current normal/build emitters actually ran offline;
  JSON/MS bytes match the actual executed `git show 6c0f27b` emitter for each project.

All raw logs/commands/execution manifests remain in the final run directory.
Supplement `Audit/phase16-p2-final-supplement-2026-11-02d/` retains:
- strict `--require-p2 --fail-on-skip` repeat: **exit 1**, 21 skips, no unittest failures;
- actual xfail traceback at the final REVIEW-vs-PASS assertion after controls;
- preservation check (172/172 files, 49 fixtures unchanged, archive unchanged);
- post-publication source/doc hashes, AST parse of 34 Python files.

### Not passes; do not fabricate output to remove skips

21 original skip events = 20 requiring real produced poly fixture (including 13
input mutations separately exercised) + 1 real poly QA/request. No P3 emitter,
`wall_surface.json/.ms`, authentic produced poly fixture or new live QA exists.
Shape-only fixture guard can accept a synthetic locked echo; never use it as proof.
The xfail documents already-rounded Python floats losing original JSON digits;
production strict-token refusal works independently. Finding-level legacy SKIPs
and exact alternative opening-rule attribution are fully inventoried in the reports.

## What was repaired, and retained boundaries

- Deep JSON now controlled-refuses beyond **128 containers** at validator G-7,
  not internal G-8 recursion. Strict used upstream/ledger duplicates and precision/
  overflow controls pass, including `--file`/`--rule` failure-exit handling.
- All four transitive faults have calibrated positives, including separately
  acyclic registry; unknown paths, backward graph edges, invalid ledger eligibility
  and superseded massing behind NURBS remove broad wall PASS.
- Known scalar formulas require declared input coverage. Used upstream unavailable
  formula -> wall SKIP in lint / build refusal. Given conflict annotations reject;
  unknown wall-local formulas remain G-32 SKIP. No generic algebra/source-truth oracle.
- G-82 detects old missing-cell/host and balanced gap/overlap failures. REVIEW is
  never spatial PASS; builder refuses REVIEW/FAIL/NOT_APPLICABLE. Conservative
  unsupported/numeric restrictions tighten historical acceptance. Thick-wall old
  volume heuristic remains limited; no-opening tested old CLI already refused G-9.
- Builder ordinary recovered replacement failures restore asserted bytes; named
  late route/parent swaps refuse; rollback failure explicitly retains recovery.
  **Not** crash-atomic pair commit, immutable handles or arbitrary-race protection.
- All used initializer seeds now strict-parse before output creation. Per-file
  descriptor staging preserves affected old file on bounded errors; earlier full
  commits may remain. **Not** whole-project rollback; recorded non-wall `--force`
  remains path-based historical overwrite behavior. Protective current observation
  tests supersede old unsafe expectations; old assertions/hashes remain in report.

## Scene and packaging

After P2 acceptance, before any other scene call, coordinator obtained a fresh
read-only snapshot: **0 objects / 0 roots**, no warning/error, namedpipe protocol 2.
Exact response: `Audit/_phase16-p3-entry-snapshot-2026-11-02d.json`, request
`e50cda63f4144409a76f7df89db97d1d`. No other scene access was made. This compact
snapshot says nothing about current scene path, unsaved status or units. It will
be stale next session: take a new read-only snapshot before work; do not assume mm/1.

Installer source/effects were read only. Every target rebuilds archive; globals
overwrite/prune. Then-current each global: 6 different + 2 additions + 0 prune.
Further docs changed: recompute effects immediately before any eventual authorized
installation. No installation of unfinished method. Archive SHA remains
`dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a`.

## Next-session sequence

1. Preserve and inspect current status/hashes; do not rerun old P2 investigations
   without evidence of drift. Current source P2 accepted; no need to manufacture
   a clean commit/tree. Publication docs changed **after** tests and are separately
   recorded; do not silently replace the immutable execution manifests.
2. P3 begins with a concrete bounded emitter/manifest/publication/ownership contract
   from proposal plus actual grammar. Delegate independent offline geometry/oracle,
   test and review tasks with explicit disjoint files; main alone operates Max.
3. Independent **physical** outward-side authority must be distinct from winding,
   volume and supplied vector. The analytical F01 plan explicitly specifies inner
   Y=0 / outward −Y; real projects need their own authoritative source. Never infer
   from compass label or volume. Do not silently alter the closed wall schema.
4. Clarify supported first subset, CLI/manifest, exact input lock/provenance and
   unknown-formula refusal, topology budgets and operational limits; no unsupported
   return/corner/local-division partial output disguised as complete walls.
5. Implement only after contract; actual emitted script must be `fileIn`-ed and
   independently measured. Fresh read-only scene state first, real unit preflight,
   short sequential bounded calls, inspect both bridge error marker and exceptions.
   Latest user permission permits necessary Max work; do not stop on the accidental
   inherited blanket ban. Preserve unrelated work and verify ownership/replay safety.
6. P3 is not accepted by file emission or historical P1 spike. F01 integrated output,
   direction independent of volume, real census/topology/units/replay/negative
   controls and later F01–F08/QA/coexistence gates remain required. Update CHECKPOINT.

Ready-to-paste continuation prompt:
`Audit/_phase16-p3-next-session-2026-11-02d-ru.md`.
