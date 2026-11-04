# Bounded P3 live negative controls — MAIN ONLY

## CURRENT STEERING — units-only freeze (supersedes broad adapters below)

Main narrowed this hand-off after the current runtime adopted explicit ARMED lease
and unconditional `INCOMPLETE_REPLAY`. Broad adapters below target the earlier
registry layout: **DO NOT GENERATE/EXECUTE those broad variants against current
runtime; positive replay preconditions cannot be met.** They are preserved as
unexecuted prior work, not acceptance or current runnable advice.

Current runnable pre-registry unit-only controls are under `unit-main-02/`:
`MAIN_Cm1.ms`, `MAIN_TypeOnly.ms`, `MAIN_Factor.ms` (one main fileIn per call).
`unit-main-01/` is superseded by 02's corrected raw-exception expectation. None
requires arm, no registry/global is created, no scene units are changed. They use
actual authentic F01 plan and actual runtime source frozen in their index.
Main must hash-check scripts/index immediately before fileIn and review raw wire.
Actual current runtime prints `P3_REFUSED|stage=entry` then bare-rethrows original
`P3_REFUSE|...`; wrapper checks original exception, main checks printed entry stage.

- Cm1: real runtime generator with expected centimeters/1 vs actual millimeters/1.
- TypeOnly: **NEGATIVE MUTATED** expected type only, retaining mm/1 scale/factors;
  proves type guard precedes equal embedded factors, NOT legitimate cm/.1 pair.
- Factor: **NEGATIVE MUTATED** stored expected factor 11 with actual mm/1; named
  computed-factor refusal must occur before lease/registry checks or mutation.

Exact legitimate cm/.1 cannot be generated under exact Float32 SystemScale policy:
`.1` becomes `0.10000000149011612`. The actual generator's offline refusal is
recorded separately; do not claim a true equal-factor legitimate pair live test
against current mm/1. No near-equality policy is silently substituted.

Reproduce only if main requests a new frozen run:
`python -B Audit/phase16-p3-live-controls-2026-11-02e/prepare_unit_controls.py --out Audit/phase16-p3-live-controls-2026-11-02e/unit-main-NEW`.
New child output, new namespace per output and unchanged source-hash closure.
No Max calls or production edits were made. Current owner freezes after hand-off.

**Prepared offline, not live-executed.** These helpers never call Max/MCP. They do
not install anything, modify production/fixtures, approve artifacts, fake missing
positive evidence or recover user edits. Owning coordinator alone admits and
executes individual `fileIn` calls, checks their raw wire/console and decides PASS.
No new scene, reset/open/save/undo, unit setter, broad deletion or test loop in Max.

## 1. Preconditions and exact preparation

1. Finish actual authentic emitted F01 creation and independent source-bound
   geometry/stack/units/topology/void/census assessment. Run **three additional
   actual identical-byte no-op replays**, retaining exact reference/handle and raw
   evidence. No original file rewriting to insert instrumentation.
2. Main must own this synthetic wall and its registry. No unrelated scene content
   and no user/plugin interaction between bounded calls. Not an arbitrary-scene
   or persistence test. Keep original artifact pair immutable; hash both bytes
   immediately before every original `fileIn` in the controlled private directory.
3. Write a separate main positive admission JSON using
   `positive-admission.EXAMPLE.json` as the **non-admitted** schema example.
   Set real hashes/handle/evidence paths, `created`, `independent_geometry_accepted`,
   `same_synthetic_node_owned_by_main`, `no_live_interleaving` true and exactly
   `replay_results: ["P3_NOOP", "P3_NOOP", "P3_NOOP"]` only from actual evidence.
   This JSON is an explicit human attestation; the generator cannot certify wire
   provenance or semantic correctness. Do not fabricate one to make preparation run.
4. From repo root (substitute actual existing paths and a fresh <=20-char token):

   ```text
   python -B Audit/phase16-p3-live-controls-2026-11-02e/prepare_controls.py --artifact ACTUAL_PAIR_DIR --positive MAIN_POSITIVE.json --out Audit/phase16-p3-live-controls-2026-11-02e/prepared_MAIN01 --token P3Main01
   ```

   `--out` must be a new **direct child of this owned audit directory**; generation
   completes all exact runtime-template anchors in memory before creating it.
   Template drift or absent/invalid admission refuses; no polling or auto-repair.
   Actual original source/identity/hash are retained in `control-index.json`.

The adapter was offline-tested against actual runtime SHA
`5df101ab21f935d63f061c2f7d7c18659aba3e359970b6d3bb9516b873372ba2`.
Regenerate/retest after production changes. It deliberately does **not** import a
Max bridge. Creating test scripts is not execution or acceptance.

## 2. Original exact-byte replay controls

Main executes `bind.ms` once, then `clean_noop_after_bind_or_restore.ms`, checking
the actual `P3_NOOP|` marker plus no exceptions/state drift. Binding reads the
actual production registry's exact reference and the admitted handle; no name
lookup/adoption. The audit witness global is separate. If its existence changes
runtime dependency readback and the clean control refuses, stop: negative controls
are NOT RUN. Do not weaken the production baseline or patch its registry.

Then **one case per call**, never all cases in a single scripted loop:

| Original-file control | Synthetic changed state |
|---|---|
| `edit_transform.ms` | Position X +1 scene unit |
| `edit_geometry.ms` | Base vertex #1 X +1 scene unit |
| `edit_material.ms` | One temporary Standard assignment (no render/material workflow) |
| `edit_stackparams.ms` | Same exact Shell outer amount +1 |
| `edit_enabledstate.ms` | Shell `enabled` inversion |
| `edit_enabledviews.ms` | Shell `enabledInViews` inversion |
| `edit_enabledrenders.ms` | Shell `enabledInRenders` inversion |
| `edit_layer.ms` | Target's exact layer membership changed; no shared-layer flag writes |
| `edit_visibility.ms` | Node `isHidden` inversion |
| `edit_renderability.ms` | Node `renderable` inversion |
| `edit_parent.ms` | Exact new Point parent |
| `edit_userprops.ms` | Extra distinct user-property entry |
| `edit_duplicate_tag_copy.ms` | Exact cloned node with whole original owner buffer |
| `edit_related_prefix.ms` | Separate Box with related wall prefix |
| `edit_registry_loss.ms` | Present registry set to undefined |
| `edit_registry_removed.ms` | Registry global removed, no automatic re-arm |

The runtime under test is the **unaltered original `wall_surface.ms`** in every
one of these controls. The test captures independent before/after target geometry,
stack, material, transform, layer, hierarchy, user buffer, census, context and
registry witnesses. It demands actual runtime exception/refusal, not a printed
word or a transport success flag. It proves each injected changed state still
exists after refusal; it does not erase it to manufacture preservation.

Expected marker `CONTROL_REFUSAL_PRESERVED|case=...|restore=NOT_RUN` leaves the
synthetic edit in place. Main inspects the raw response and actual refusal stage;
clean target-specific cases must reach replay read-only, not an unrelated guard.
Parent/copy/prefix can conservatively fail census before target inspection.

### Explicit synthetic-only restoration — never user edits

Only after that verified marker may main choose a **separate call** to
`restore_own_synthetic.ms`. It uses exact saved values/references (not a closure,
name lookup or model regeneration), refuses any intervening edit, restores only
that own control and validates the full exact target/registry/context baseline.
Then `clean_noop_after_bind_or_restore.ms` must discriminate again. If a test or
restore assertion fails, stop and retain evidence/residue; no automatic restore.
This authorization exists only for main's own synthetic node, never user data.
Neither script clears saveRequired or assumes clean undo/dirty history restored.

**Layer adapter gap:** main supplies an explicitly owned empty test-layer exact
reference in global name `<control_key>_layer` before that case. Creating/deleting
layers is not generated here. Main must calibrate layer `addNode`/readback and
confirm the original layer is unchanged. Do not borrow a populated/user layer.
If no owned empty layer is available, mark this case INCOMPLETE. Restoration
returns the target to its original exact layer and leaves layer teardown to main.

## 3. Fresh negative-only artifact controls

After original controls, main tears down the positive synthetic wall by its exact
reference using its own explicit harness, checks empty census, and does not reset
or save the scene. The following each have a **fresh test namespace, new test
identity/binding and different SHA**. Their source declarations/authority remain
unchanged; no script+manifest pair is published as accepted production output.
`NEGATIVE_ONLY_*.ms` files are intentionally altered generated bytes for fault
injection. Their hashes are separately recorded and must never be substituted for
the original production SHA or fed to ordinary artifact acceptance.

Run corresponding `fresh_*.ms` file one at a time:

- `fresh_unit_cm_1.ms`: altered expected cm/1 against actual mm/1; type mismatch
  must refuse before constructor/registry mutation. No current unit change.
- `fresh_unit_cm_0p1_equal_factor.ms`: altered expected cm/0.1, same mathematical
  conversion factor as mm/1; exact pair must still refuse before mutation.
  Public `generate_script()` **currently refuses cm/0.1 offline** because .1 is
  not exactly Float32. The labelled Double-guard variant separately tests live
  pair discrimination; it is **not** an authentic public cm/0.1 artifact or proof
  that production can generate that pair. Report both facts, not a combined PASS.
- `fresh_corrupt_factor.ms`: original mm/1 pair but corrupted stored expected
  factor 11 instead of 10; computed-factor guard must refuse before mutation.
- `fresh_exact_name_collision.ms`: create exact-name foreign Box first, then
  first-run test artifact; must refuse and preserve exact Box state. Main later
  tears down exact retained reference; no delete by name/prefix.
- `fresh_api_create_failure.ms`: admits empty scene, creates real wall and three
  real vertices, then calls actual `polyop.createVert` with an invalid point.
  A separately retained Box is injected after admission solely to discriminate
  exact-reference cleanup from prefix sweeping. Actual runtime catch must remove
  its exact created wall only, leave the exact foreign Box intact, and publish no
  registry. Runtime may correctly label this `P3_INCOMPLETE_RESIDUAL` because foreign
  census remains; that label is NOT a general clean failure PASS. Check raw reason
  is the actual invalid-point API error at grid-vertices, not another early refusal.
  Main cleans its own sentinel separately by exact reference stored under the
  variant's `foreign_key` (entry `[1]`; handle `[2]`). No automatic teardown.
- `fresh_reverse_winding.ms`: actual **full** generated runtime with reversed
  actual face loops plus actual grid/base/evaluated captures. Same source values,
  declared outward, Shell amounts and budgets; only test identity/namespace and
  measured winding are altered. It must actually build/commit, not merely refuse.
  If any API/baseline refuses, this winding runtime gate is INCOMPLETE.

First-run collision sentinel uses `foreign_key` registry `[1]=exact node,[2]=handle`.
Winding retains the exact produced node in its fresh production-style registry
`[5]`. None of these namespaces can adopt the original wall. Main retains the
raw wire evidence, hashes and exact refs before any synthetic-only teardown.

### Reversed full runtime: independent assessment

Save actual console output as UTF-8 text (not a Python repr or surrounding wire
JSON). Capture parser requires all sequential arrays and refuses truncation.

```text
python -B Audit/phase16-p3-live-controls-2026-11-02e/check_winding_capture.py --controls Audit/phase16-p3-live-controls-2026-11-02e/prepared_MAIN01 --capture ACTUAL_REVERSED_CONSOLE.txt --walls Audit/phase16-p3-f01-input-2026-11-02e/project/walls.json --dimensions Audit/phase16-p3-f01-input-2026-11-02e/project/dimensions.json --authority Audit/phase16-p3-f01-input-2026-11-02e/direction-authority.json --reviewer MAIN_REVIEWER
```

The separate independent oracle reads the actual analytical F01 plan and checks
authority bytes/source sign without inferring outside from bad winding or volume.
The checker independently measures triangle volume, closed triangle topology,
actual reversed grid/base normals and signed displacement **[-30,0]**, not required
**[0,+30]** along physical outside. Expected scalar absolute volume is unchanged
2,610,000 cm³. `CONTROL_DISCRIMINATES` means physical-direction **FAIL** despite
equal scalar volume, not acceptance of the bad artifact. This narrow checker does
not fabricate evaluated quads; full independent evaluated-quad QA remains separate.

## 4. Wrong authority is offline only

```text
python -B Audit/phase16-p3-live-controls-2026-11-02e/check_wrong_authority.py --project Audit/phase16-p3-f01-input-2026-11-02e/project --authority Audit/phase16-p3-f01-input-2026-11-02e/direction-authority.json --out Audit/phase16-p3-live-controls-2026-11-02e/offline-authority_MAIN02
```

This runs actual public CLI clean emission first, then flips only the private
authority outward. Requires targeted authority refusal and no bad output, logs
actual commands/stdout/stderr and before/after source hashes. No Max execution.
The prepared wrong-authority JSON is similarly negative-only, not source repair.

## 5. Verified here and remaining main-only API assumptions

Executed offline `selftest_offline.py`: 6 tests OK, source/fixture hashes stable;
this only exercises real runtime **source generation**, adapters and parser, no
MaxScript syntax/runtime proof. Executed actual CLI clean/wrong authority pair:
`offline-authority-01/result.json`: targeted negative discriminates, no source drift.
Initial selftest path typo was corrected from missing fixture root to `/project`;
its earlier exception was not a functional PASS.

No live test was executed by this owner. Main must separately calibrate wrapper
MAXScript local functions, array freezing/reference identity, `getPropNames`
readability, transform controller getter, `globalVars.remove`, raw user-buffer
setter, Shell enable flags, Point/Standard/copy construction, exact layer move,
and non-scene mesh readback/lifetime in short calls before relying on each case.
Any unsupported read/parse, unexpected exception or >~2s call makes the relevant
case INCOMPLETE; no automatic re-run. Snapshot mesh values are non-scene values,
never convert them into scene nodes for convenience. Baseline equality is broad
bounded observed-state evidence, not a claim of universal plugin/edit history.
