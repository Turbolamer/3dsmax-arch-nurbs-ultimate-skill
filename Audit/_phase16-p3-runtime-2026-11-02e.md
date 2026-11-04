# P3.1 runtime author report — 2026-11-02e

**Status: implemented offline; LIVE NOT RUN by this owner; replay explicitly
BLOCKED/INCOMPLETE, never reported NOOP.** Ownership is exactly `scripts/wall_surface_runtime.py`,
`Audit/test_phase16_p3_runtime.py`, this report, and
`Audit/phase16-p3-runtime-probes-2026-11-02e/`. No other files were modified.
No Max/MCP call, install/archive/global-copy update, save/reset/unit write occurred.

## Public API for the builder owner

```python
plan = build_plan(walls: dict, dimensions: dict)  # raises ValueError on refusal
script = generate_script(plan, identity, namespace, expected_units)
arm = generate_arm_script(plan, identity, namespace, expected_units, fresh_nonce)
```

- Inputs must already have passed the owner's locked-input/provenance/formula and
  direction-authority gates. These functions do not pretend that document shape
  proves source truth. `identity` is the **64 lowercase hex SHA-256** of the
  builder's canonical locked source/contract identity, not a free-form label.
- `namespace` is the decided ASCII token, 1–40 chars, beginning with a letter.
- `expected_units` is the closed four-field object `{system_type, system_scale,
  cm_per_unit, units_per_cm}`. Certified type spelling must be canonical lowercase;
  scale must be exactly representable by Max Float32; the computed double factor
  pair must agree exactly. Separate runtime type, scale and computed-factor checks
  run before constructor/registry inspection, and again before cleanup deletion.
  Invalid/nonfinite/mismatched same-factor pairs refuse. No units are written.
- Returned plan: `schema_version="p3-wall-runtime-plan-1"`, `project`,
  `wall_technique`, `subset`, `wall_run_id`, `contour_ref`, `start_cm`, `end_cm`,
  `base_z_cm`, `top_z_cm`, `thickness_cm`, `length_cm`, `height_cm`, declared
  `outward`, independently normalized `geometric_normal`, epsilons, canonical
  ordered `openings`, `declared_budgets`, `operational_caps`, `grid`, `predictions`.
- `grid={u_cm,v_cm,vertices_cm,cells}`. Each row-major cell has zero-based
  `u_index/v_index`, 1-based **vertex_slots**, `opening_id` string or null.
  Slots are NOT actual Max IDs. Shared cells reuse slots. Actual createVert and
  createPolygon IDs are separately recorded/validated and used for topology and
  one accumulated deleteFaces. No assumed `{2,7,9}` universal IDs.
- `predictions.label="offline_predictions_not_measurements"`; separate grid,
  active-base, boundary, evaluated polygon/triangle counts; cm² area, cm³ volume,
  cm bounds. Manifest writer can retain the whole plan or selected labelled data.
- Complete one-block/one-run exact facade endpoints, no returns/adjacency,
  internal-u/below-top disjoint rectangles; sill zero allowed. Exact shared
  stations are allowed; distinct near-stations refuse, never merge/snap. Absolute
  planning ceilings are 32 grid polygons/64 verts/256 tris/6 openings/one node/
  one Shell, with lower declared budgets still enforced.
- Script generation additionally admits only initial F01-sized execution
  (24 grid vertices/15 grid polygons/96 evaluated triangles/2 openings or less).
  Broader planning counts are not runtime calibrated. Float32 conversion is
  explicit and checked for coincident vertices, lost thickness, degenerate cells,
  overflow/underflow and error exceeding numeric_epsilon_cm. It is representation
  validation, not coordinate snapping or a promise of exact decimal storage.
- Deterministic script binding hashes identity + namespace + complete plan + units.
  The fresh reserved session-global key hashes namespace + actual source identity;
  existing invalid/caller registry values are not replaced on refusal.

## Runtime policy and honest limits

- One fileIn wrapper owns local helpers. Constructor is measured P1 route A:
  `Editable_Mesh`, `convertTo ... Editable_Poly`, actual returned vertex/face IDs,
  single deletion pass, single `Shell(inner=0,outer=thickness,segments=1)`.
- Main's new operational identity evidence
  `Audit/_phase16-p3-identity-probes-2026-11-02e.json` is incorporated: prefer the
  actual convertTo return, compare its original handle; exact getAnimByHandle
  fallback only. No name-based reacquisition/deletion. Historical invalidation
  warning is not generalized to every conversion. No requirement/clearing of
  getSaveRequired=false after temporary edits.
- Conservative first-create admission is **zero objects/zero selection/unnamed
  scene**; subsequent census exactly one original node. This is stricter than
  the reviewed <=64 scene-node ceiling and avoids claiming unrelated-scene state
  preservation not actually implemented. Saved/loaded scenes refuse. No durable
  save/load/merge/restart registry claim exists.
- Registry stores exact refs, original input identity, complete binding, root/
  path/time/selection state, full measured baseline and dirty flag. Identical
  replay compares but never creates/replaces/deletes the existing node. Colliding
  names/tags, altered identity, invalid refs, material assignment, parent/children,
  shared base object/census changes, unsupported keyed controllers, unsupported
  property serialization/reference graphs all refuse conservatively.
- Baseline source reads numeric arrays (not stringified points), poly verts/
  edges/faces/dead flags/flags/material IDs/smoothing/selections/map channels/
  VData/EData, evaluated triangle mesh, exact base/Shell/controller refs and graph,
  all enumerated properties, all Shell enabled states and properties, node flags/
  transforms/object offsets, layer state, user-prop buffer, ref dependencies.
  Any exception aborts baseline establishment/comparison. Graph/property ceilings
  bound inspection. This is a **candidate bounded baseline**, NOT a demonstrated
  universal scene edit detector; third-party hidden/native state, callbacks and
  concurrent mutation are outside the verified claim. Actual API behavior must
  be inspected in main before any supported-state safety claim.
- Failure cleanup touches only references created in that attempt, with exact
  captured handle fallback after conversion. Unresolved/remnant census returns
  `P3_INCOMPLETE_RESIDUAL`; no broad deletion, reset, undo or name recovery. Scene
  dirty flag is never cleared; no undo/crash atomicity is claimed.
- Read-back diagnostics: `P3_VERTEX_IDS`, `P3_FACE_IDS` + `P3_CUT_IDS`,
  `P3_BASE_READBACK`, `P3_CREATED` or `P3_NOOP`. These contain actual runtime
  returns/counts, not fake measurements. Independent geometry/topology/direction
  QA is still required; a print marker alone is not acceptance.

## Executed offline tests / probes still needed

Executed `python -B Audit/test_phase16_p3_runtime.py`: **40 tests, OK, no skips**
on the current source, including exact in-memory mesh disposal/arm/refusal tests.
They test offline data/source only. No live success is implied.

Main should inspect then sequentially fileIn these tiny one-temporary-node probes:

1. `Audit/phase16-p3-runtime-probes-2026-11-02e/01_registry_properties.ms`
   — handle roundtrips, actual property types, refs/dependents and name controls.
2. `.../02_poly_state.ms` — operational base flags/map/VData/EData APIs, controller
   predicate/key count and global lookup. Every uncertain call is isolated.
3. `.../03_registry_roundtrip.ms` — fresh unique registry publication/read-back/
   removal plus actual root/parent/class behavior; refuses preexisting key.
   Unlike probes 1/2 this intentionally tests a reserved temporary global; it
   removes only the global it just created and never replaces a caller value.

Names previously resolved by main prove names only; this owner did not infer
operational success from that resolution. Uncertain/broken probes must lead to
targeted source correction or refusal—not ignored fields or fabricated baseline.

## Final operational corrections — supersede earlier registry/NOOP descriptions

The independent runtime-design report was read when it appeared. Main approved
its explicit one-use arm protocol. **The wall file never auto-arms**, creates or
replaces a global. Missing/invalid registry always refuses. Main calls the added
`generate_arm_script(plan, identity, namespace, expected_units, fresh_nonce)`;
its fileIn result is the exact structured lease witness to retain externally.
The fresh nonce is 16..128 ASCII token characters. The sole generated safe global
name hashes namespace plus actual source identity. Arm refuses an existing name,
explicitly declares it before globalVars.set, and removes only its newly declared
name on arm failure. Main's separate calibrated struct alias/separate-value
identity evidence is used: the lease is a struct with detached `.values`, not
array equality used as identity. Protocol details and example are in
`phase16-p3-runtime-probes-2026-11-02e/04_arm_protocol.md`.

Lease transitions are ARMED -> BUILDING -> COMMITTED or POISONED. No implicit
recovery/re-arm exists. State writes occur only on authorized initial creation;
replay refusal performs no registry/scene write. **Even identical supported
baseline replay refuses `INCOMPLETE_REPLAY`: specified-normal/native custom
metadata completeness is unproven. There is no successful `P3_NOOP` branch.**
Clean initial construction, if the actual readers work, prints
`P3_CREATED_UNVERIFIED`; matching supported state prints
`P3_OBSERVED_BASELINE_EQUAL` then refuses. This deliberately blocks three accepted
no-op replays and P3.1 acceptance while still allowing main to independently
measure actual initial geometry/targeted refusals. No broad edit-safety claim.

Non-scene snapshotAsMesh buffers are explicitly deleted on success and in their
own guarded error cleanup. Evaluated readback now also includes normals, face
material/smoothing and edge visibility. Snapshot coordinates are used directly
(main independently reconfirmed world-coordinate semantics), not transformed twice.

Main supplied operational evidence in
`Audit/_phase16-p3-runtime-probe-results-2026-11-02e.json`: tiny probe 02 base flags,
face/map/VData/EData APIs ran successfully and static PRS numKeys=-1 is allowed.
Probe 01 initially threw because local `shell` shadowed the `Shell` constructor;
renamed to `shellMod` in runtime and probe. Probe 03 proved globalVars.set alone
does not declare a fresh name; explicit safe declaration/owned cleanup added.
Failures were not interpreted as API absences. Corrected probes require main
retest. Unknown layer/interface/paramblock handles intentionally refuse rather
than dropping those fields.

## Main's corrected probe 01 — operational target distinction, source frozen

Main supplied the corrected probe result, request
`376c60c3f32144bbb4cc1c87607e61bb`, elapsed **34.038 ms**. This owner did not
execute it. Normalized findings:

| Exact target | Actual class/readback | Operational handle/reference result |
|---|---|---|
| Wall node with Shell | `Editable_mesh`; base remains `Editable_Poly` | Handle roundtrip true; refs count 16; dependent `DummyClass` |
| Base object | `Editable_Poly` | Handle roundtrip true; refs count 2; dependents `#(DummyClass,DummyClass,DummyClass,Editable_mesh,DummyClass)` |
| Shell modifier | `Shell` | Handle roundtrip true; refs count 1; dependents `#(DummyClass,DummyClass,Editable_mesh,DummyClass)` |
| Transform PRS | position Point3, rotation Quat, scale Point3 | Handle roundtrip true; refs count 3; dependents `#(Editable_mesh,DummyClass)` |
| Layer | `MixinInterface` / `LayerProperties`; readable boolean/color/string properties | **getHandleByAnim and refs.getNumRefs throw conversion to MaxObject; refs.dependents returns undefined** |

Positive arithmetic and bogus-name controls discriminated as expected. Exact
temporary-node cleanup completed (`exactRefStillValid=false`). The evaluated
node/base class distinction is expected with the modifier, not corruption.

**Specific unresolved blocker, not a blanket API absence:** the layer interface
is not a MaxObject for those operational calls. Current generic `freeze` routes
the layer through `exactRef`, so current authentic initial creation is expected
to refuse during baseline acquisition and clean only its newly created node.
The generic dependency walk also encounters measured `DummyClass` targets whose
full comparable support has not yet been calibrated. No layer fields are dropped,
no unsupported target is treated equal, and no successful creation is claimed.

Runtime/tests/probe source is frozen after this finding, as main requested.
A future layer-specific typed-property/reference comparator needs its own
calibrated equality controls before replacing this refusal; generic handle
existence on node/base/Shell/PRS does not establish layer identity support.
Specified-normal/native metadata completeness and accepted NOOP remain blocked.

### Main's corrected probe 03 — declaration/publication operational

Main supplied request `31cfc87bb7474071852ef96ef72d08e4`, round-trip **4.007 ms**,
elapsed **4.032 ms**, `ok=true`, no error/warnings. Corrected explicit fresh
declaration then globalVars.set/readback ran: `published=true;sameArray=true`.
Root handle was `39P`, exact root roundtrip true. Unparented temporary node had
`parent == rootNode` false and `parent == undefined` true. Actual class names:
`BooleanClass`, `Double`, `UndefinedClass`. Exact temporary-node cleanup completed
(`exactRefStillValid=false`). This proves the tested declaration/publication and
root/parent/class forms only, not array identity against separately constructed
equal-valued arrays, complete arm/runtime support, or produced-output acceptance.
No retest or executable/probe change was made by this owner.

## Main02 authentic attempt — compile failure and bounded repair

Main reported authentic Main02 live attempt request
`b7b3f2e80a294df389a314c9cc2c1b52`, elapsed **8.609 ms**. Arm compilation failed:
`only throws without arguments are permitted in catch expressions`, at
`throw ("P3_ARM_INCOMPLETE|" + (reason as string))`. `objectsAfter=0`.
This is an actual emitted-source compile failure, **not an API absence or passing
wall execution**. Main reports failure preceded arm/global/scene mutation; exact
Main02 registry-symbol absence remains main's follow-up check, not presumed here.

As explicitly reassigned by main, changed only owned runtime/tests: all generated
catch bodies now print contextual diagnostics, perform the existing exact cleanup,
then use **bare `throw`** to preserve/rethrow the original exception. This includes
arm failure, exactRef/property readers, mesh-snapshot cleanup and outer runtime
failure. No guard was removed; unproven replay still refuses. No probe edit or live
call was made by this owner. A calibrated offline token/balanced-catch structural
test rejects both former `throw (message)` and `throw reason` forms in catches;
it is not a substitute for Max compilation.

Executed after repair: `python -B Audit/test_phase16_p3_runtime.py` — **41/41 OK,
no skips**. Source frozen for main's new authentic Main03 publication/live attempt:

```text
f966cbdd9b582df90cad33bfa5b0d2acde44429ccad85fe410629261d474acf5  scripts/wall_surface_runtime.py
afdf6de5535a5463c9838bcc4fad1bda1af37eaac3c365faadfd966251270878  Audit/test_phase16_p3_runtime.py
```

Layer-interface reference comparability, complete metadata and accepted NOOP
remain blocked. Repairing compile syntax is not P3.1 acceptance.

## Post-catch unit-control attempt — read-only helper-name collision

Main reported request `27f87b2fd27b4a3ab24099070b5e53a9`, elapsed **3.54 ms**:
the generated expected-cm/1 runtime failed **before the intended unit guard** with
`Cannot assign to read-only variable: freeze`, `objects=0`. The intended negative
unit control therefore did not pass; the actual failure is a MAXScript helper
name collision with its read-only built-in, not an API/class absence.

Targeted repair only: all **13 emitted local helper definitions and references**
now use a `p3` prefix (`p3FreezeState`, `p3RequireState`, `p3SameState`,
`p3ExactRef`, `p3ReadProperties`, etc.). Token-aware emission leaves strings,
comments, IDs, geometry, baseline operations and guards unchanged. Added an
offline structural test requiring every emitted helper name to be prefixed and
rejecting the original generic helper definitions. Main must compile-preflight
the actual corrected emitted file before its next authentic publication attempt;
this owner made no Max call or runtime-success claim.

Executed after this repair: `python -B Audit/test_phase16_p3_runtime.py` —
**42/42 OK, no skips**. New frozen hashes supersede those above:

```text
bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15  scripts/wall_surface_runtime.py
242bb0c4403068246c9e223f769ebed822dbea3931d0dce6052bfc63aee96c38  Audit/test_phase16_p3_runtime.py
```

Unverified layer/state completeness and unconditional safe replay refusal remain
unchanged. No P3.1 acceptance.

## Main03 authentic published fileIn — exact layer blocker confirmed; frozen

Main supplied actual approved/hash-verified held-artifact execution evidence:
`Audit/_phase16-p3-main03-live-result-2026-11-02e.json`, request
`59a61aaa30f84b129588d5ff5b7b063f`, elapsed **28.727 ms**. Reported raw outcome:

```text
P3_MAIN03_AUTHENTIC_ATTEMPT|armed=true|EXCEPTION=-- Runtime error: -- Unable to convert:<MixinInterface:LayerProperties>totype:MaxObject|leaseState=POISONED|witnessStill=true|objectsAfter=0
```

The authentic emitted pair was actually fileIn-ed after successful explicit arm;
the current exact layer-comparability baseline blocker is now **operationally
confirmed**, not merely predicted. The original external witness remained exact,
the failed attempt poisoned its lease, and post-cleanup census was zero. This is
failed construction/baseline evidence, **not an accepted wall, independent F01
measurement, successful NOOP or P3.1 acceptance**. No source/test/probe changes or
Max calls by this owner follow this finding. Frozen hashes above remain current.
Next work is calibrated layer-specific identity/typed readback plus native mesh
metadata completeness, not omission of unsupported state. Main owns the final
settled tests and NOT_ACCEPTED handoff.
