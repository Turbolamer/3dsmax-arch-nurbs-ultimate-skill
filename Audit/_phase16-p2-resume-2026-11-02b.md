# Phase 16 P2 — second session handoff, 2026-11-02

**User requested a stop and continuation in a new session. P2 is in progress and is not accepted.**
This document supersedes the status in `Audit/_phase16-p2-handoff-2026-11-02.md`, not its historical
observations. Read `AGENTS.md`, the new top of `CHECKPOINT.md`, `PLAN.md` §4.0d and this file first;
then consult the previous handoff, implementation brief and integration audit when needed. All
current tracked modifications and untracked files are work to preserve; do not reset, clean, revert,
delete, overwrite, commit, or install them without understanding their ownership and consequences.

## Scope and safety

- The previous P0/P1 live facts stand. **The P3 `build_wall_surface.py` emitter, poly runtime QA,
  emitted poly wall manifest and actual poly wall acceptance remain absent.** `place_components.py`
  is still a legacy-only builder; never describe the poly route as operational or production-ready.
- The present wall contract covers only sourced straight facade runs with `reference_face=inner`,
  plus the declared return subset. It does not prove all building enclosures, seams, upper returns,
  arbitrary contours, or physical direction. `outward` being unit and perpendicular does **not**
  prove its sign points outside. Do not infer sign from a facade name; use authoritative source
  geometry/face evidence and a separate live direction gate, independent of volume.
- Last read-only Max snapshot in this session: **0 objects**. No scene mutation, reset, or live
  modeling was done. Before any future Max work, re-read the current scene and run the required
  preflight; the bare preflight is SKIP, not PASS. No deleting objects belonging to the user.
- User explicitly refused copying the discovered `AutoBackup*.max`; do not touch/copy them or
  change autoback settings without new permission. Ordinary Max autosaves may overwrite them.
- Materials, export and a layer-application policy change remain outside the task.

## What changed, and evidence already observed

The working tree adds the `walls.json` domain declaration, route-aware legacy handling, wall
provenance/geometry checks, and scaffold changes. The original synthetic cases discovered several
false PASS conditions. The new checks address direct ledger owner/path/value bindings, local
dependency cycles, eligibility of upstream paths, transitive ledger failures, malformed partial
data, envelope status, strict JSON float overflow/duplicate route keys, parent/`pipeline` route
ambiguity and the JSON versus process exit-code mismatch for `--rule`. `G-93` only describes
declaration checks and explicitly disclaims proof of the physical side and outward sign. A valid
derived reference does not by itself prove its formula; G-32 stays SKIP without a formula oracle.

### New independent audit: P2 provenance blockers, still open

The read-only audit tested `scripts/validate_specs.py` SHA-256
`a99892acb1544ea8bb7fd5930a928164039a5e9f924bc0a8df5b4c63e755ee52`. The following are the
**agent's executed in-memory reproductions**; the orchestrator subsequently repeated all four
and their clean control with the same gate outcomes. Each uses the unchanged fixture as a positive
control and mutates only the described field:

```python
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path('Audit').resolve()))
import scripts.validate_specs as v
from test_phase16_p2_isolated import walls_declaration, synthetic_poly_assembly

D = {p.stem: json.loads(p.read_text(encoding="utf-8"))
     for p in Path("examples").glob("*.json") if p.stem in v.SPEC_BY_NAME}
D["walls"] = walls_declaration(D["dimensions"])
D["assembly"] = synthetic_poly_assembly(D["assembly"])

def run(d):
    report = v.Report()
    session = v.Session([v.LoadedFile(Path(k + ".json"), k + ".json",
                                      spec=v.SPEC_BY_NAME[k], doc=value)
                         for k, value in sorted(d.items())])
    v.run_checks(session, report)
    return report
```

No filesystem mutation is needed. On `run(copy.deepcopy(D))` the agent observed
G-92/G-93/G-94/G-97 PASS and no FAIL. It then observed these distinct problems:

1. `d['walls']['origin_inputs']=['structure.x_bay_cm']` and
   `d['assumptions']['cross_references']['conflict_sourced_paths'][3]['conflict_ref']='C-999'`
   gave **G-31 FAIL**, but wall **G-10/G-93 PASS**. Original `C-003` is the positive control.
   Recheck whether wall provenance can depend on a failed cross-file ledger gate.
2. `d['walls']['origin_inputs']=['components[0].size_cm']` and
   `d['components_registry']['origins']['components[0].size_cm']['derives_from']=['NO_SUCH_FIELD']`
   gave **G-31/G-93 PASS and no FAIL**. The untouched reference is the positive control. The
   registry's own provenance is not fully validated by the current dispatch. **Orchestrator
   independently re-ran this exact mutation and the clean control:** both had 0 FAIL / wall
   G-93 PASS, confirming the false PASS on that snapshot.
3. With the same wall input, set
   `d['components_registry']['origin_inputs']=['wall_runs[0].thickness_cm']`: **G-31/G-93 PASS,
   no FAIL**, though an upstream registry now points backward to walls. Current G-31 searches
   broadly rather than enforcing this source's allowed upstream dependency direction.
4. Set `d['walls']['origin_inputs']=['sections[0].points_cm']` and
   `d['massing']['status']='superseded'`: ordinary lint reported **G-31/G-93 PASS, no FAIL**,
   despite the selected NURBS source depending on massing. `--build` separately rejects the
   non-locked massing; that does not repair the incorrect lint PASS. Original locked massing is
   the positive control.

Independently reproduce these before editing. Require transitive validation and acyclic directional
dependencies without accidentally claiming a formula or physical source has been proven; add
isolated positive/negative tests, preserve the historical legacy fixtures, and rerun final QA.
Do not close P2 until these are fixed or explicitly marked incomplete rather than PASS.

`references/07-spec-grammar.md` now records defensive wall epsilon ceilings of **0.01 cm** and
**0.001 dimensionless**, separately from design tolerances, and records the closed bare-path owner
mapping implemented in the validator; unknown/ambiguous `defaults` is unsupported. These are
limits, not inferred epsilon values. `PLAN.md` §4.0d reconciles its gate-oriented P4–P6 groupings
with P4 orchestration / P5 QA / P6 fixtures in `Audit/AGENT_PLAN_poly_surface_shell.md`.

`specs/fixtures/poly-shell-input/` now contains a **hypothetical input-only** locked wall
declaration and a README. An agent reports G-93/G-94/G-97 positive controls and 13 negative input
mutations passed when paired with a synthetic draft assembly in a temp copy of examples. The
orchestrator independently tested the input in memory: positive G-93/G-94/G-97 PASS; zero wall
thickness yielded G-93 FAIL, a negative ceiling G-97 FAIL, and overlapping openings G-94 FAIL,
each with one FAIL overall. The full 13-case claim has not been independently repeated. The fixture
contains **no** produced assembly or wall surface; never
pass it off as real poly output or force it into a harness requiring a locked produced assembly.
Packaging caveat: `collect_files()` currently includes JSON under `specs/`, but not this fixture's
`README.md` (the `specs` suffix filter is `.json` only). Any eventual package review must ensure the
synthetic-only provenance and limitations remain visible to installed users, or deliberately choose a
different packaging policy; no installation was run here.

The orchestrator independently reproduced that old G-82 accepted deleting `WAL-EL-014-C01`
(1,134,000 cm³ within the aggregate budget), removing all cells of host EL-014, and shifting a
cell such that gaps and overlaps compensate. The new **`scripts/wall_cell_coverage.py`** is called
by G-82 *in addition to*, not instead of, the old volume calculation. It uses exact rational 3D
partitioning, cut-host/opening joins and an explicit resource cap, and ignores stored volume fields
as spatial evidence. The orchestrator observed: original examples PASS; all three faults FAIL; a
0.1 cm gap produces WARN + SKIP in lint, FAIL in `--build` (no fabricated PASS). The orchestrator
independently observed **37 oracle/integration tests OK**, including SHA-preserved fixtures; repeat
them after all changes settle.
Known limitation: the old volume subcheck infers thickness as the smaller plan extent; walls
thicker than their length can fail even when spatial coverage passes. Do not silently remove the
old volume requirement; review and document this before broadening the legacy contract.

## Offline checks and outstanding safety finding

Most recent orchestrator-observed tests, on snapshots that may differ from the final tree because
agents were working concurrently:

| Command | Observed result | Boundary |
|---|---|---|
| `python -B Audit/test_phase16_p2.py --require-p2 -q` | 18 tests OK, **21 SKIP** | No locked poly assembly / real poly QA fixture. The formerly skipped missing-cell negative now passes as a negative control. SKIP is not PASS. |
| `python -B Audit/test_phase16_p2_cases.py -q` | 102 OK | Run before final G-82 integration; 91 fault injections do not alone prove each target gate. |
| `python -B Audit/test_phase16_p2_isolated.py -q` | 34 OK | Isolated target rules with positive controls; run before later builder edits. |
| `python -B Audit/test_phase16_p2_dependencies.py -q` | 15 OK | Includes transitive ledger, route scope, malformed `--file`, G-86 and project mismatch. |
| `python -B Audit/test_phase16_legacy_coverage.py -q` | 37 OK | Repeat on the final stable tree. |

Historical baselines before the latest edits were `examples` **140 PASS/31 SKIP**,
`specs/fixtures/stepped-tower` **147/30**, and
`specs/fixtures/form-precision/specs/pipeline` **155/24**, all FAIL 0. The form-precision project
root is **not** its pipeline directory; passing the root directly to `validate_specs --dir` fails
for lack of specs and is not evidence of a regression. Re-run final regression in lint,
`--warnings-as-errors` and `--build` modes. Do not count a SKIP as a successful measurement.

A separate audit reproduced a serious pre-fix bug in `place_components.py`: it could emit a
**locked** legacy assembly from an explicit legacy `walls.json` that was draft/superseded, had
incorrect inherited tolerances, an inverted block, or incomplete provenance; it could overwrite
existing `assembly.json`/`.ms` after accepting these. Separate output-directory selection could
reject an empty destination or accept a conflicting wall declaration with the same route. The
builder agent was asked to repair this and the independent agent to add
`Audit/test_phase16_legacy_build.py`. **Check their final reports, actual diffs and test results;
until independently verified this repair remains unaccepted.** Check every refusal leaves sentinels
byte-identical, including `--build --allow-draft`, and preserve historical no-selector builds.

The orchestrator's background `python -B Audit/test_phase16_legacy_build.py -q` ran **while the
builder and tests were being edited** and ended with 3 failures among 10 tests: a transient
`TypeError` from a changed `verify_snapshots` signature/call. The call was subsequently seen in
the source as `verify_snapshots(specs_dir, snapshots)`, but that is **not a retest**. Re-run the
entire test after all writes stop, and verify positive/negative controls; do not count this run as
PASS or assume the original fail-open is fixed because the transient mismatch changed.

A second orchestrator run of `Audit/test_phase16_legacy_build.py -q` executed 10 tests but failed
its final stability guard because `place_components.py` changed during the run. This is **not an
accepted PASS**. The independent builder-test agent subsequently reported **10 tests OK** on
stable snapshot hashes: builder `c603ac1cb7435feaa426596d064613b62d3e3927b24d6ff316628a5bc0f312b9`,
validator `a99892acb1544ea8bb7fd5930a928164039a5e9f924bc0a8df5b4c63e755ee52`. The orchestrator
measured the same hashes on the then-current files but did not independently repeat that run. The
agent reports byte-identical historical output versus `git show 6c0f27b`, explicit-legacy locked
controls, refusal of invalid/draft/superseded inputs, and unchanged output sentinels. A clean
explicit `--out` is presently refused without writing unless a byte-identical `walls.json` is
already present; the builder will not copy it. The builder-fix agent has now also reported
**10 builder tests OK, 37 coverage tests OK, and the first harness 18 OK / 21 SKIP** at the same
builder SHA. These reports have not been independently rerun by the orchestrator on the final tree.

**Compatibility decision still needed before acceptance:** `verify_spatial_coverage()` is called
for every legacy output, even historical no-selector projects and regardless of `--build`, and
refuses `REVIEW`, `FAIL` and `NOT_APPLICABLE`. The independent oracle returns NOT_APPLICABLE for
no-opening inputs and FAIL for unsupported geometry. Thus a project the historical builder used
to process may now be refused, even though the worked example is byte-identical. Investigate with
calibrated no-opening, near-tolerance and unsupported-geometry cases; preserve legacy behavior
without allowing SKIP/REVIEW to masquerade as a verified build. Do not loosen the boundary solely
to make a test pass. Builder input rechecks and safety guards also **do not make the two sequential
output-file writes atomic** under I/O failure or concurrent path substitution; keep that limitation
visible, protect existing user files, and decide scope before any change.

The repeated `python -B Audit/test_phase16_p2_isolated.py -q` completed **34 tests OK**, but it
does not cover the four newly identified provenance blockers. All subagent reports have now arrived;
repeat required tests independently on the settled tree.

## Next-session gates

1. `git status --short --branch`, `git diff --check`, review all changes including new untracked
   tests, optional fixture and new helper. No destructive cleanup. Check the final agent reports
   and hashes; do not assume their claims are current. Resolve any concurrent-edit artifacts.
2. Run **both original offline harnesses** and the new isolated, dependencies, spatial and legacy
   builder tests on the stable final tree; use sufficient time for the 102-case harness. Check
   every relevant positive/negative gate individually, particularly targeted rather than masked
   failures, no user-data overwrite on refusal, and all three legacy projects. A missing test
   fixture or runtime observation remains explicit SKIP/INCOMPLETE. Also test strict symlink and
   malformed JSON handling if supported; report any platform SKIP.
3. Independently review the final validator and builder for remaining fail-open provenance,
   partially validated data and route/output conflicts. Follow the latest independent audit and
   preserve its repros if any. Reconcile documentation with actual implementation, including
   exact epsilon bounds, owner mapping, G-82 REVIEW policy and limitations. Record results in
   `CHECKPOINT.md`. Accept P2 only when all *P2* controls pass and missing runtime evidence stays
   visible, not on the basis of successful unittest counts containing SKIPs.
4. **Only after P2 acceptance**, continue P3 and later phases according to the mapped plan.
   `Audit/_phase16-p3-design-2026-11-02.md` is a proposed narrow P3 design, not an implementation
   or acceptance; evaluate its restrictions as a proposal rather than as new user requirements.
   Any emitter must be fileIn-ed and independently measured,
   including direction, opening occupancy, units, collisions, ownership and safe replay. Never
   delete nodes just because they share a prefix; F01 live gate and F02–F08 remain required.
5. The archive and global installations were not updated. `scripts/install_skill.py` always
   rebuilds the existing archive; default install copies and prunes. A prior read-only dry
   comparison showed 0 prune candidates and five differing files per installation, but this is
   not a future safety guarantee. Inspect current effects and preserve unfamiliar user data
   before installation; do not copy or manipulate AutoBackup files.

## Preserved files

Tracked changes seen during this session: `CHECKPOINT.md`, `PLAN.md`,
`references/07-spec-grammar.md`, `scripts/init_project.py`, `scripts/place_components.py`, and
`scripts/validate_specs.py`. New/untracked files include the previous handoff and implementation
audit/brief, `scripts/wall_cell_coverage.py`, `Audit/test_phase16_p2.py`,
`Audit/test_phase16_p2_cases.py`, `Audit/test_phase16_p2_isolated.py`,
`Audit/test_phase16_p2_dependencies.py`, `Audit/test_phase16_legacy_coverage.py`,
`Audit/test_phase16_legacy_build.py`, the proposed P3 design, and
`specs/fixtures/poly-shell-input/` (a hypothetical input-only fixture, with no produced assembly).
Confirm actual final `git status`; the list is not a licence to remove or overwrite anything.
