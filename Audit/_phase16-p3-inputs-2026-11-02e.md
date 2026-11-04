# P3.1 input adapter — implementation evidence and API

## FINAL-1 source-review repair — 2026-11-03

Read the independent exact reproduction in
`Audit/_phase16-p3-source-review-2026-11-02e.md` §FINAL-1. The earlier helper
ignored original `wall_surface.json`/`.ms`, so its private snapshot manufactured
absence. Repaired **only** the owned input helper, input tests and this report.
Accepted P2 and all input fixtures remain immutable; CLI/runtime/publisher were
not edited. No previously generated artifact was imported or interpreted.

The initial bounded subset now refuses **any** existing `wall_surface.json` OR
`wall_surface.ms` at the accepted project/pipeline boundary, using `lstat` before
private snapshot staging. This includes regular files, directories, valid and
dangling links; content need not parse or prove a contradiction. Inspection errors
fail closed. `project_artifact_presence` is a new returned dict, absolute reserved
path → bool; every admitted entry is false. The inventory includes both the project
and pipeline paths even if `pipeline/` does not exist initially. Selecting a
`pipeline/` input instead checks its parent too.

`verify_inputs_unchanged` rechecks that presence inventory before source hash checks
and refuses observed late additions, including `.ms` and late-created pipeline
links. Because every preexisting artifact refuses admission, there is no admitted
present-artifact baseline whose later removal can be allowed as input reuse.
Removing only a test-injected artifact restores the originally absent state and
allows verification again. A complete add/remove between checks remains invisible
under the explicit single-writer **observed-drift**, not filesystem-lock model;
this limitation was not upgraded into a race-safety claim.

Executed targeted actual-source tests:

- `python -B Audit/test_phase16_p3_inputs.py ProjectArtifactPresenceTests -v`:
  **7 tests OK**, zero skips, 1.464 s, preservation drift empty.
- `python -B Audit/test_phase16_p3_inputs.py -q`: **38 tests OK**, zero skips,
  123.462 s, `ACCEPTED_SOURCE_AND_SEED_DRIFT []`.
- AST parsing of the two changed Python files passed without bytecode writes.

Controls copy authentic F01 inputs/authority to owned temp directories. Clean
actual public `build()` to a disjoint new run succeeds with exact pair hashes.
JSON alone, MS alone and both refuse before private staging; actual builder
publication is asserted uncalled. Parent/pipeline combinations cover regular
files/directories/links/dangling links. Late actual `make_artifacts` injection of
JSON/MS/pair refuses before publisher, preserving the entire old source/sentinel
tree plus the exact injected bytes. The malicious MS sentinel is **never executed**.
Tests delete only their exact injected entries inside their own disposable trees.

Repair tested bytes (supersede the earlier implementation hashes below):

```text
5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12 scripts/wall_surface_inputs.py
62e1309a96fc4e92b795e6fc5541435f08086d15a671597f955bc15bdab48f20 Audit/test_phase16_p3_inputs.py
```

No output overwrites, source/fixture edits outside ownership, Max, installation
or git operations occurred. This closes the locally tested input admission defect;
independent final review and P3/runtime acceptance remain main's responsibility.

## Outcome (offline only)

Implemented only `scripts/wall_surface_inputs.py`,
`Audit/test_phase16_p3_inputs.py` and this new report. Accepted P2 files, examples
and the new F01 owner's input fixture were not edited. No Max, installer, package
update, git command or synthetic produced assembly was used. CHECKPOINT updates
remain the coordinator's ownership. This is not P3 geometry/runtime acceptance.

Executed `python -B Audit/test_phase16_p3_inputs.py -q`: **31 tests, OK, 123.988 s,
zero skips/xfails**, `ACCEPTED_SOURCE_AND_SEED_DRIFT []`. The guard hashes the four
accepted P2 executables, every existing example file and all four F01 input JSONs.
An earlier 26-test run exposed one unallowed *empty draft assembly* SKIP signature;
that implementation mismatch was corrected, and the final complete run passed.
Final AST parsing also passed without bytecode writes. Tested bytes:

```text
03c9accba70648e677fdb837a436256186d2535f438e553910f38cc8725f8c59 scripts/wall_surface_inputs.py
2ed71edc4935cce80c0b7ff835368249eecc9389e767aadf5f051423be97c3d2 Audit/test_phase16_p3_inputs.py
```

## Exact chosen API

```python
from scripts.wall_surface_inputs import load_inputs, verify_inputs_unchanged, InputRefusal

inputs = load_inputs(project_dir, namespace="F01", system_type="millimeters", system_scale=1)
# Build in memory from inputs only; do not reopen original JSONs for emission.
verify_inputs_unchanged(inputs)  # immediately before publication; None or InputRefusal
# Equivalent: inputs["verify_inputs_unchanged"]()
```

`project_dir` is the actual spec directory or its immediate `pipeline/` parent;
the returned `project_dir` is canonical absolute. Required operational arguments
are keyword-only. Namespace is strict ASCII `[A-Za-z][A-Za-z0-9_]{0,39}`; units
are exact certified lowercase names, without `#`, trimming or aliases. Exact
type/scale pair is retained, so equal-factor different pairs do not collapse.
The adapter never sets scene units and does not prove their current live value.

The returned ordinary dict contains:

- `walls`, `dimensions`: detached parsed documents; no origin relabeling/rewrite.
- `project`, `namespace`, `expected_units`: `system_type`, `system_scale`,
  `cm_per_scene_unit`, `scene_units_per_cm`.
- `run`, `block`, sorted `openings`, `length_cm`, `height_cm`, `tangent`,
  `declared_outward`, exact-geometric `geometric_outward`, `u_stations_cm`,
  `v_stations_cm`. The original supplied vector is retained, not silently replaced.
- `input_snapshots`: filename → **raw bytes**, e.g. `walls.json` → bytes.
- `input_hashes`: same filename keys → SHA-256 of those original bytes.
- `input_sources`: spec stem → original canonical absolute path, e.g. `walls` → path.
- `validation_findings`: every accepted-validator finding, including raw failures.
- `excluded_inventory_findings`: specifically out-of-stage missing-input inventory
  failures that were not admission preconditions; they are not rewritten as PASS.
- `allowed_skips`: complete original SKIP findings, not runtime evidence.
- `verify_inputs_unchanged`: no-argument convenience closure as shown above.

Treat the returned dict and its snapshots/hashes as caller-owned immutable data
for one build; deliberately tampering with the dict is outside the local
single-writer execution model. Hash verification detects observed membership,
path, symlink and byte drift. It is **not** an immutable lock, arbitrary-race
protection or a guarantee against a change after the last check.

## Snapshot and admission behavior

Input families inspected at the accepted validator's parent/pipeline boundary:
dimensions, walls, assumptions, conflicts, plus present massing/NURBS/facade-grid/
component-registry inputs and assembly. Duplicate names, symlinks, non-files,
ambiguous boundary directories and malformed present inputs refuse. This is a
conservative closure: present optional upstreams are inspected/hashed too, rather
than ignoring malformed authored inputs. Unrelated reserved materials/export and
future QA outputs are not consumed. Arbitrary source-reference text paths are not
opened as if they were executable formulas; separate source authority belongs to
the orchestrator and must join its own source bytes/hashes to the publication lock.

Each JSON is read bounded to **2 MiB**, accumulated sources to **16 MiB**, then
copied byte-for-byte to a private temporary directory. The **accepted unchanged**
validator's strict parser, hygiene and semantic gates read only that directory.
Geometry normalization uses the parsed private snapshot, never reopened originals.
Afterward the original source mapping and hashes are checked again. No output
files or original input bytes are written. Private temporary snapshot writes and
cleanup are the only filesystem writes performed by this module.

The whole wall project must contain exactly one block and one linked run, no
returns, explicit poly route and inner reference face. There is no selected-wall
API. All wall origins must be `given` in this initial subset; derived or ledger-
sourced wall origins refuse rather than laundering into given. The referenced
contour itself is an implicit required provenance/formula root even if omitted
from `origin_inputs`. Known required formulas are recomputed through accepted
formula functions only; unknown collapsed/upstream or wall-local formulas refuse.
No eval/exec/custom formula interpreter was added.

Openings require `0 < lo < hi < L`, `0 <= sill < head < H`, strict u separation,
valid sole-run links and at most six openings. Exact shared stations are permitted;
distinct stations nearer than numeric epsilon refuse with no snapping. Empty
openings are admitted as input, without claiming a runtime topology special case.
Input normalization also limits planning to 64 vertices/32 quads. Final active/
evaluated geometry budgets and actual IDs/triangles remain the geometry gate.

Early numeric guards cover finite positive unit factors, Float32 station collapse,
mapped inner/outer vertex Float32 range and error, duplicate mapped vertex tuples,
thickness below epsilon and overflowing/non-positive derived area/volume. They do
**not** simulate MAXScript evaluation, Shell normals, topology, triangulation or
prove actual native-coordinate accuracy; geometry must independently check those.

## Authentic F01 result: not whole-pipeline PASS

The test copies `Audit/phase16-p3-f01-input-2026-11-02e/project/` to a private temp,
checks true u `[0,50,150,230,330,400]`, v `[0,90,210,300]`, raw snapshot equality,
and unchanged originals. Admission succeeds with those four locked input files.
`validation_findings` still contains **four FAILs**, exactly G-1 absent inventory
for massing, nurbs, facade_grids and components_registry. Only those exact missing
inventory findings are excluded from this standalone admission; a reached missing
NURBS dependency or malformed present used NURBS G-1 fails. This is not an overall
accepted-validator/pipeline PASS, and no future output was fabricated to obtain it.

## Exact non-refusing SKIP signatures

F01's **23** SKIP findings remain SKIP. The following are accepted only with the
specific rule/message checks in `_allowed_skip`, never as a whole-rule waiver:

| Rule(s) | Exact message (one row each except noted) |
|---|---|
|G-95/G-98/G-99/G-100 (4)|`JSON lint cannot verify emitted script, manifest or live Max; output/runtime gate pending` at `wall pipeline`|
|G-16 (3 F01 files)|`07 declares no numeric range for this file; a key with no declared range is unbounded`|
|G-21|`no sibling *_ccw flag exists for this ring in 07 section 5.7, so the declared winding cannot be confirmed; ring is CCW` (CW alternative also explicit; never wall direction proof)|
|G-26|`openings is empty; nothing to test (07 section 5.11 allows it)`|
|G-27|`openings is empty; nothing to fit`|
|G-28|`openings is empty; nothing to collide`|
|G-91|`No stepped floor_plates[].footprint_cm or facades[].spans_level_indices declared`|
|G-86|`schema_version 1.0; form_references/precision_targets not present` (or explicit `schema_version 1.1 without analytical form targets; form_references not present`)|
|G-92|`poly_surface_shell_v1 selected; assembly is absent or a draft placeholder, echo incomplete`|
|G-96|`assembly absent or empty draft; route exclusivity incomplete; output manifest wall_surface.json is missing`|
|G-87/G-88/G-89/G-90 (4)|`qa.json is absent; QA configuration has not been scaffolded or run`|
|G-1 assembly|`poly assembly output is not produced; G-92/G-96 remain incomplete, but it is not a wall-input precondition`|
|G-1 qa|`absent; earlier stage / legacy project before S7/P8 QA gate (07 S-4)`|
|G-1 materials|`absent; 07 section 4 marks it reserved (owner P7), so no builder reads it yet`|
|G-1 export|`absent; 07 section 4 marks it reserved (owner P9), so no builder reads it yet`|

Additional explicitly matched cases exercised by disposable seed-copy tests:

- G-54 and G-70: their **entire exact accepted-validator runtime/emitted-census
  messages**, stored verbatim in `_allowed_skip`; static JSON cannot measure the
  committed NURBS node or emitted facade CSVs. No such CSVs are secretly read from
  original paths in this input-only case.
- G-84/G-85: exact `no section declares generator; compatibility skip (generator optional)`.
- G-69: exact empty-variants message with only the declared integer component count
  variable; this is NOT_APPLICABLE, not a variant validation PASS.
- Empty draft assembly only: G-71…83 exact established section9.9 empty-placeholder
  signature; G-4 `status=draft; allowed by --allow-draft`; G-92
  `poly_surface_shell_v1 selected, but assembly.json envelope/hygiene or locked-status checks failed or are incomplete`.
  The last is allowed **only after zero envelope/hygiene FAILs and an actual empty
  draft have been established**, not for an arbitrary failed/partial assembly.
- A future nonempty statically exclusive poly assembly can expose exact G-96
  `static route mixing checks passed; output manifest wall_surface.json is missing, and full exclusivity awaits the P3 manifest contract (not an input-build precondition)`;
  no produced poly fixture was fabricated/tested here, and other unapproved output
  checks may conservatively refuse such an assembly.

Every other SKIP is a refusal. In particular unknown G-32 required recomputation,
draft input/provenance, unavailable required source or form-reference checks are
not waived. An injected missing analytical form check is tested to refuse.

## Test boundaries

31 tests include individually calibrated malformed JSON/hygiene/numeric tokens,
draft/superseded, selector/outer, unknown wall fields, whole-project multiplicity,
block/return/opening joins, touching/overlap/bounds, near-stations, missing/ cyclic
provenance, ledger-value/cross-reference faults, known and unknown formulas,
authentic conflicting legacy assembly, no future-output requirement, private-read
instrumentation, observed hash/membership drift, numeric storage and resource
limits, namespace/unit pairs, and validator-global restoration. The 16 MiB total
limit test lowers that constant as a targeted branch injection, not a claim that
an actual 16 MiB project was generated. No live geometry, direction authority,
publication/replay or adversarial filesystem race was tested by this module.
