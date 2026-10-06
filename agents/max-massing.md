# max-massing — S2: locked `dimensions.json` → `massing.json` + geometry in 3ds Max

> **Purpose:** S2 is the second build stage of the **S0 → S5** pipeline and the **first stage that touches
> 3ds Max**. It reads the locked spec set S1 handed over, turns `dimensions.json` into a validator-clean
> `massing.json` — every placeable solid as a prism in Z — emits the MAXScript that builds it, runs that
> script, measures what came back, and cleans up. **S2 builds massing only.** S1 hands you a spec set;
> you hand S3 (`agents/max-nurbs.md`) a `massing.json` and a matching scene.
>
> **CORRECTED (2026-10-06):** the pipeline ran to S8 in earlier revisions of this file. **S6 (materials),
> S7 (QA) and S8 (export) were cancelled by explicit user decision on 2026-10-05.** S5 is the last
> stage; materials are applied **by hand** by the user.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage · Input | **S2** — the second build stage (`PLAN.md` §4 row P3) · `specs/pipeline/dimensions.json`, plus `assumptions.json` and `conflicts_resolved.json` |
| Output | `massing.json` (`07` §8.1) and the builder's `massing.ms`, then the nodes that script creates |
| Geometry produced | Site pad · plinth · one slab per storey · one column per grid intersection per storey · core walls per spanned storey · roof deck · parapet · one `Dummy` per group |
| 3ds Max calls | Exactly one: run the emitted script, read back, clean up (§7). **No probes** (§1.2) |
| Consumer · Precondition | S3 (`agents/max-nurbs.md`), and through it S4a/S4b → S5, which is **the last stage** · S1 complete and locked (`01` §4) |
| Blocked by | A `draft` `dimensions.json`. Full stop (§2.2) |
| Findings | See `agents/max-orchestrator.md` §6.2. If this session produced a real finding — a measured bbox outside `tolerances.linear_cm`, a building element no `kind` expresses, or a `dimensions.json` value that is legal but wrong for this building — record it in `<project>/IMPROVEMENTS.md`. **A session with no findings writes nothing and creates no file.** Format: `references/improvement-log.md` |

### 1.1 What S2 owns, and who owns what S2 defers

S2 builds exactly six `kind`s plus the site pad and the group dummies: `plinth`, `slab` (one per
storey), `column` (one per grid intersection per storey), `core_wall` (one per storey in
`core.spans_level_indices`), `roof_deck`, `parapet`; plus `site_pad` ground pad / paving / kerb and
one `Dummy` per `grouping[]`. Layers are fixed by `kind` (§6.3); `kerb` is `null` because
`dimensions.json` has no kerb key; the ground slab is a `slab`, not `site_pad` (`11` §1.2); and stair
and lift shafts are **not** massing elements at S2.

| **Never** built by S2 | Consumed by | Correct instrument |
|---|---|---|
| Facade panels, glazing, mullions, spandrels, reveals, doors | **S4a / S5** | `facade_grids.json`, `components_registry.json`, `assembly.json` |
| Openings cut into slabs or walls | **S5** | `assembly.json`'s `wall_cells[]`. S2 does **not** boolean the openings out of a slab — a slab is a slab. **CORRECTED (2026-10-06):** this cell used to name `assembly.json.cuts`, which is not the key. The Boolean modifier cannot be made to cut anything in this build, so S5 tiles each `facade_wall` into **solid cells** instead (`agents/max-assembly.md` §6.2.1) |
| Materials, renderer choice, UVs | **nobody — S6 was cancelled 2026-10-05** | **Applied by hand by the user**; the hand-off is `agents/max-orchestrator.md` §5. `materials.json` is a **reserved stub**, not a deliverable and not a gate |
| NURBS surfaces, lofts, sweeps, blends, curved roofs, stairs, ramps, lifts | **S3** | `nurbs.json`, `recipes/*.json` |
| Beams, bracing, trusses, foundations | **S3/S5, after an engineer** | No `kind` produces them at S2 (`11` O-4) |
| Layer **application** to objects | **nobody — permanently** | Layer is **data** (`07` §8.1.3) and cannot be applied from this bridge by **any** of the **nine** ruled-out routes. **The user applies it in the Layer dialog**; `agents/max-assembly.md` §6.3 owns the wording |
| Scatter, planting, cameras, lights, export | **S5 for the scatter declaration; nobody for the rest** | **CORRECTED (2026-10-06):** this cell used to read `assembly.json.scatters`, `qa.json.captures`, `export.json`. **`scatters` is the wrong key** — the schema key is **`scatter`**, singular, and it is a **declaration** the user applies by hand. `qa.json` and `export.json` belong to the **cancelled** S7/S8 and are reserved stubs only |

### 1.2 The one-MCP rule

**You may execute the emitted `massing.ms` and read state back. You may not probe.**

| Allowed | Forbidden |
|---|---|
| `3dsmax-mcp_execute_maxscript` running `massing.ms`, or a short read-back of `node.min` / `node.max` / `node.width` | Any exploratory probe of your own — a class-existence question, a trial-and-error call |
| `3dsmax-mcp_get_scene_info` to confirm the scene holds nothing else | Every tool in `01` §1.2 — the forestPack / `tyflow_*` / RailClone group, and the Rhino-server names (`get_objects`, `analyze_objects`, `measure_objects`, `boolean_*`, `loft`, `sweep1`, `pipe`, every `gh_*`) |
| `3dsmax-mcp_delete_objects` on what you created | **`geometry_qa`, `contact_check`, `scene_qa` do not exist.** A check naming one is a defect |
| `3dsmax-mcp_manage_layers` actions `list` and `create` — the eight names in `07` §8.1.4, nothing else | **`3dsmax-mcp_manage_layers` **object assignment** — the action name is not "unknown", it **does not exist**: the vocabulary is **exactly `{list, create, delete}`**, 40+ candidates rejected, and eight further routes are ruled out (**nine total**). **The user applies layers in the Layer dialog** (`agents/max-assembly.md` §6.3) |

Executing an already-verified emitted script is **not** a probe (`01` §6). A fact not in
`CHECKPOINT.md` §"Verified facts" is escalated for an orchestrator probe — never opened by S2.

---

## 2. Inputs and outputs

### 2.1 What you read

| Source | What you take from it |
|---|---|
| `specs/pipeline/dimensions.json` | **The contract you build from** — `building` `site` `structure` `levels` `core` `floor_plates` `roof` `tolerances` |
| `assumptions.json` · `conflicts_resolved.json` | Every entry with `recheck_stage: "P3"` — **you are the recheck stage** (§4 step 2). And which paths were conflict-resolved, so a surprising number is explained rather than "corrected" |
| `references/07-spec-grammar.md` | **§8.1** the schema in full · **§9.6** `G-34`…`G-40` · §3.1 the lock gate · §3.3 tolerances · §2 units |
| `references/11-layer-standard.md` | Vocabulary (§1) · `kind` → layer (§2) · **node naming** (§3) · dummy rules (§4) · the layer constraint (§5) · delivery checklist (§6) |
| `09-defaults.md` · `10-conflict-resolution.md` | `09` §5 do-not-default list — S2 **never fills** a dimension (§10) · `10` §6 the escalation ladder `E1`…`E9` |
| `CHECKPOINT.md` | §"Scene units and placement semantics — VERIFIED (P3, 2026-10-04)" and §"Design consequences of the layer finding" — **the transcript of record** for §7 |
| `references/01` · the two `scripts/` | The stage map and the builder contract (§5). Read their `--help`; never guess a flag |

> `09` §6 still carries the pre-P3 **UNVERIFIED** label on scene units. `CHECKPOINT.md` is the later,
> executed transcript — cite it and report the stale label (§12), never edit it.

### 2.2 What you own, and the lock gate

| Path | Action |
|---|---|
| `<project>/specs/pipeline/massing.json` | **Emitted by the builder**, verified by you. Never hand-written, never hand-edited (§6.3) |
| the builder's documented `massing.ms` output path | **Emitted by the builder.** Never hand-written, never hand-patched |

**You modify nothing else** — not `references/07`–`11`, not `agents/max-input.md`, not the two
`scripts/`, not `examples/`, not `CHECKPOINT.md`, not S1's three locked files.

> **A builder must refuse any spec file whose `status` is not `locked`, naming the file and the status
> it found** (`07` §3.1, `01` §4). Exit non-zero. Checked before anything else is read.

| Found | Action |
|---|---|
| `status: "draft"` or `"superseded"` | **Refuse**, and report that path and status verbatim. Never soften it with `--allow-draft` — that flag is for linting, not shipping. `superseded` means a newer revision exists, and consuming the old one silently is what this gate exists to stop |
| a ledger file not `locked`, or a `project` id that differs across the three files | **Refuse.** They are part of the same locked set, and `07` §3.1 requires the id identical — `massing.json` carries the same `project` |
| `schema_version` major you do not implement | **Stop.** Do not guess |

A `draft` upstream file is not your failure to fix, and not a reason to build "just the ready parts".

---

## 3. File ownership

One file, one owner, exclusive — `AGENTS.md`, `01` §7. Two P3 deliverables are being written **in
parallel by another author**: you own neither, may rely only on this contract and never on their
internals, and must never edit them.

| Parallel artifact | The contract you may rely on |
|---|---|
| `scripts/build_spec.py` | Exposes `--stage massing --in <dir> --out <dir> [--json]`; reads `<in>/dimensions.json`; writes `<out>/massing.json` and `<out>/massing.ms`; refuses non-`locked` input with non-zero exit; byte-identical output for byte-identical input (`01` §8) |
| `examples/massing.json` | The `pavilion-01` worked case. It must satisfy every invariant in `07` §9 including `G-34`…`G-40`, and reconcile against the three `pavilion-01` files on disk — `G-37` and `G-38` are cross-file checks, so a massing file that drifts fails immediately (`07` §10) |

When either looks wrong, do what S1 does: **write against the owning file, record the objection, move
on** (§12).

---

## 4. Procedure

Ordered and deterministic. Each step has a pass condition.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Verify the input is locked** | Read the six envelope keys of all three files. Apply §2.2 in full | All three `locked`, `project` agrees, `units.length == "cm"` |
| 2 | **Re-check every P3 assumption** | List every `assumptions.json` entry with `recheck_stage: "P3"`. Each is a **low-confidence proxy** for something a licensed professional owns — column section, core wall thickness, slab thickness | Every one named in your report. **None silently upgraded** — if one would change the geometry, that is an escalation (§10) |
| 3 | **Read `dimensions.json` into the massing model** | Read §2.1 once, in order. Take `tolerances` verbatim — a builder may not widen them. Storeys from `levels[]` + `floor_plates[]`; columns from `structure.column_x_cm` × `column_y_cm` × `column_section_cm`; core walls from `core.footprint_cm` inset by `core.wall_thickness_cm` over `core.spans_level_indices`; roof from `roof.deck_level_cm` / `deck_thickness_cm` / `parapet_*`; site from `site.footprint_cm` / `ground_level_cm` / `setback_cm`; groups per `07` §8.1.1 | Every value used is at a `07` §5 key path. **Every element's `origin` is `derived`** (`G-36`) — S1 already resolved `given` / `assumed` / `conflict` |
| 4 | **Classify each candidate against §6** | Every element must be a prism in Z on an axis-aligned rectangle | Every refusal recorded with the element's id and reason, and escalated (§10) |
| 5 | **Emit `massing.json` and `massing.ms`** | Run the builder (§5). **You do not hand-write either file.** Then read `massing.json` back from disk and verify it independently — recompute at least one `z_range_cm`, one `profile_cm`, one `parent_pivot_cm`, and the `G-40` group partition by hand | The file matches your hand computation at `tolerances.linear_cm`, and the element-id set matches what you derived |
| 6 | **Validate** | `python scripts/validate_specs.py --dir <specs_dir> --build` | Exit **0**. `G-34`…`G-40` all **PASS** — see §8 row 2 |
| 7 | **Run in 3ds Max** | §7. One script per call, under ~2 s | Returns without error; the scene holds the expected nodes |
| 8 | **Verify against the spec** | §8. Measure every element's node and compare to `massing.json` | Every element matches within `tolerances.linear_cm`; the scene contains nothing else |
| 9 | **Clean up, then report** | §9. Delete what you created in the same call, then return §12 | Only the massing nodes and their dummies remain, named per `11` §3.1; the report is under the §12 cap |

**Determinism.** The same locked spec must yield byte-identical `massing.json` and `massing.ms`
(`07` S-5, `01` §5). Three things break it, all defects to report rather than fix in the scene: a
timestamp other than `source.recorded_at`, a run-time default, and iteration-order dependence. Element
ids ascend in fixed order, so a rebuild yields the same node names (`11` N3).

---

## 5. The build commands

```
python scripts/build_spec.py --stage massing --in <specs_dir> --out <out_dir>
python scripts/build_spec.py --stage massing --in <specs_dir> --out <out_dir> --json
python scripts/validate_specs.py --dir <specs_dir> --build
```

The CLI contract is fixed in `01` §8 — do not vary it, and do not add a second entry point.

| Aspect | Contract |
|---|---|
| Reads | `<in>/dimensions.json` for `--stage massing` |
| Writes | `<out>/massing.json` and `<out>/massing.ms`. `--out` defaults to `--in`; `--json` gives a machine-readable report on stdout |
| Exit **0** | The lock gate passed **and** `G-34`…`G-40` pass |
| Exit **non-zero** | A refusal naming the reason — the file path and the `status` found, or the `G-` id that fired |
| Determinism | Byte-identical output for byte-identical input |
| Layer code | **None.** `massing.ms` is geometry only. Adding layer code is a defect, not an improvement — it cannot work (`07` §8.1.3) |

`--build` forces the lock gate to a **FAIL** instead of the lint **WARN** it is without the flag
(`CHECKPOINT.md` §P2) — always run it with `--build`. If a flag errors, run `--help` and use only what
it prints; never substitute `python -m py_compile` for a validator run. **A non-zero exit is a stop**:
fix the spec through S1 (§10) or the builder through its owner (§3). Never rename a key, widen
`tolerances`, drop a leaf, or delete a group to silence a `FAIL`.

---

## 6. Geometry rules

### 6.1 Every element is a Z-prism

> **Every massing element is a prism in Z: a world-XY ring plus a Z interval. Anything that is not a
> Z-prism is not massing — it is NURBS, and it belongs to S3** (`07` §8.1.1).

`profile_cm` is a **world**-XY ring, CCW, ≥ 3 vertices, no duplicate and no repeated final vertex —
`[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]` in the rectangular case. `z_range_cm` is `[z0, z1]` with `z1 > z0`,
both finite. `profile_ccw` is declared and `true`, so `G-35` has something to assert against.

### 6.2 The per-kind Z rule — `G-38`, quoted

| `kind` | What `G-38` fixes | Tolerance |
|---|---|---|
| `slab` | `z_range_cm == [level.elevation_cm − floor_plates[i].thickness_cm, level.elevation_cm]` — **the slab sits under its level** | `linear_cm` |
| `column` | `z_range_cm == [level.elevation_cm − slab thickness, level.elevation_cm + level.height_cm]` — **the column spans the storey** | `linear_cm` |
| `core_wall` | `profile_cm == core.footprint_cm` **inset by `core.wall_thickness_cm`** | `linear_cm` |
| `roof_deck` | `z_range_cm == [roof.deck_level_cm, roof.deck_level_cm + roof.deck_thickness_cm]` — **at the deck level** | `linear_cm` |
| `parapet` | `z_range_cm == [roof.deck_level_cm + roof.deck_thickness_cm, … + roof.parapet_height_cm]` — **on top of the deck** | `linear_cm` |

Also from `G-38`: every `storey_index` is `null` or an index in `storeys[]`, and **every level in
`core.spans_level_indices` must have a `core_wall`**.

> **Reported, not resolved.** `G-38` puts the roof deck at `[deck_level_cm, deck_level_cm +
> deck_thickness_cm]` while `07` §5.9 says `deck_thickness_cm` hangs **downward** from `deck_level_cm`.
> One is wrong and **S2 does not pick**: build to `G-38`, the invariant the validator implements, and
> record it in `OBJECTIONS` (§12) for the `07` owner. Editing the spec to suit either reading is a
> reinterpretation of a locked key (`07` S-3).

### 6.3 `layer` is data, and what is out of scope

`layer` is fixed per kind (`07` §8.1.2 — a table, not a preference, because `assembly.json.layer_map`
resolves against it): `plinth` → `00_SITE` · `slab` → `01_SLABS` · `column` → `02_STRUCTURE` ·
`core_wall` → `03_CORE` · `roof_deck` and `parapet` → `04_ROOF`. `site_pad.layer` is always `00_SITE`;
every `grouping[].layer` is `90_SCENE` — *"the dummy, never the payload"*. Enforced by **G-39**. The
only verified placement primitive is `Box(width:, length:, height:, pos:)` — axis-aligned — so **a
non-rectangular profile cannot be emitted**:

| Case | Verdict |
|---|---|
| A profile that is not a rectangle — L, T, U, chamfered, notched, any > 4 vertices | **Out of scope at S2.** The builder refuses it **by name**; escalate (§10). Never approximate it with a bounding rectangle: a wrong massing that validates is worse than a refusal |
| A rectangle **rotated** from world axes (`site.plot_rotation_deg ≠ 0`) | **Out of scope at S2.** `Box` has no rotation in the verified call shape, and rotating after creation is **UNVERIFIED**. Escalate |
| A footprint that changes with height — stepped, tapered, setback per storey | **Out of scope.** One `site.footprint_cm`, and `G-29` assumes a prismatic building. Escalate |
| A `plinth` | `dimensions.json` has **no plinth key.** Emit one only if the spec supplies the dimension; otherwise omit it and say so. An S2-invented plinth is an invented dimension |
| `site_pad.kerb` · a `grouping[].kind` of `facade` · a `core_wall` that does not span its whole storey | `kerb` is `null`, `facade` is reserved for S4–S5, neither creates geometry (`07` §8.1.1, `11` §1.6). `G-38` fixes the core wall's **profile**, not its Z: build it on the storey volume and record it in `origins` as derived from `levels[i]`; a partial-height core wall is a `07` §8.1.1 schema question — escalate |

**A refusal names the element and the reason.** "Cannot build: `core.footprint_cm` has 8 vertices; a
`core_wall` at S2 must be a rectangle" is a refusal. A silently approximated rectangle is a defect.
**Never hand-build, never hand-edit:** both files are **builder output**, and hand-editing either breaks
the audit trail `G-36` protects — an element whose geometry no longer matches the `derives_from` in
`origins` is a hand-edited derived value, in a file nobody is validating. Verify the builder by
**recomputing it from `dimensions.json`**: not by trusting it, not by repairing it.

---

## 7. The 3ds Max step

Only these facts are verified. Everything else is UNVERIFIED and needs an orchestrator probe.

| Fact | Status | Consequence |
|---|---|---|
| Scene units are **centimetres** with `units.SystemScale 1.0` (`units.SystemType` = `centimeters`) | ✅ verified 2026-10-04, known-bogus control in the same batch | **No conversion happens.** A spec value in cm is the same number in Max. Do not divide, multiply or round at the boundary |
| The script creates each element with `Box(width:, length:, height:, pos:)`. Geometry is **centred on `pos.xy`**, its **base sits at `pos.z`**, and `pos:` moves the geometry, not only the pivot | ✅ verified — `Box width:100 length:200 height:300 pos:[1000,0,0]` → `min=[950,-100,0] max=[1050,100,300]` | `pos:` = `[profile centre x, profile centre y, z_range_cm[0]]`; `width`/`length` = the profile's X/Y extent; `height` = `z_range_cm[1] − z_range_cm[0]` |
| A node is **named after its spec id**: `EL-001` → `EL_001`, `GRP-001` → `GRP_001`. Replace every `-` with `_`; nothing else changes | design decision, `11` §3.1, rules N1–N5 | Names are identifier-safe (`-` is also subtraction, so `EL-001` in an expression reads as `EL - 001`), unique, stable across rebuilds, derived deterministically. `grouping[].name` resolves to the group id; a descriptive label is an **S5 / hand-off** concern (**CORRECTED 2026-10-06:** this cell used to say "S5/S6"; **S6 was cancelled on 2026-10-05**) |
| Grouping uses `Dummy` + `node.parent = dummy`. `Dummy boxSize:` needs a **`point3`** — a float throws. `getChildren` **does not exist**; use the `dummy.children` property | ✅ verified 2026-10-04 | `parent_pivot_cm` is the dummy's pivot: the group's bbox centre in XY and its **minimum** Z, tol 0.5 (`11` D3) |
| **An object's layer cannot be assigned from MAXScript at all.** Six routes executed, all throw `Property is read-only: layer`. Layer *creation* and *reading* do work | ✅ verified 2026-10-04, six transcripts | **Layer stays data.** Nodes created at S2 sit wherever Max puts new geometry and that is expected — **not a defect, never "fixed" in the emitted script** |

**UNVERIFIED — do not build on these without an orchestrator probe:** rotating a node after creation;
any layer-assignment route outside the six rejected; per-layer colour or render flags (`11` O-7);
`massing.ms` on a scene that is not empty.

**How to run it.** `3dsmax-mcp_execute_maxscript` with `fileIn "<absolute path>"` — the default route.
Non-negotiable: **one script per call** and **under ~2 s** — `execute_maxscript` runs on Max's **main
thread** and a long script freezes the UI.

---

## 8. Verification — the completion gate

Check every row. **The validator covers the mechanical subset only**; rows 3, 6 and 7 are yours.

| # | Gate | Checked by |
|---|---|---|
| 1 | `python scripts/validate_specs.py --dir <specs_dir> --build` exits **0**, with `G-34`…`G-40` **all PASS** | the transcript of the final run |
| 2 | **A SKIP on any of `G-34`…`G-40` is not a pass.** A check that cannot be evaluated reports SKIP with its reason, never a silent PASS (`07` §9.6). A SKIP means the build is unproven — escalate it | you, reading the `--json` output |
| 3 | **Every element's node exists**, named per `11` §3.1 | you — `3dsmax-mcp_get_scene_info` |
| 4 | Every `origins` entry is `derived` with a non-empty `derives_from` resolving in `dimensions.json` or this file; every `origin_inputs` path resolves; `tolerances` equals `dimensions.json`'s, unwidened | **G-36**, **G-31** |
| 5 | Every element is in **exactly one** group, each `parent_pivot_cm` equals that group's bbox centre in XY and minimum Z, and every `layer` matches the `kind` → layer table, `site_pad.layer == "00_SITE"`, `grouping[].layer == "90_SCENE"` | **G-40**, **G-39**, `11` H11 |
| 6 | **Every element's measured bounding box matches `massing.json` within `tolerances.linear_cm`** | you — the measurement route below |
| 7 | **The scene contains nothing else** — no auto-named `Box01`, no orphan from a failed run, no probe, nothing on `99_DEBUG` that is not a named probe | you — `get_scene_info`, `11` H5/H6 |
| 8 | The script ran **without error**. An error that produced no node is a FAIL, not a partial pass | the call's return value |
| 9 | The eight layer names in `07` §8.1.4 exist, character for character | `3dsmax-mcp_manage_layers` `list` — **existence only.** **CORRECTED (2026-10-06):** this cell used to read "Assignment is S5's problem and the action name is unknown". **It is nobody's problem and the action name will never be found** — the vocabulary is exactly `{list, create, delete}`, and nine routes are ruled out in total. **The user applies layers in the Layer dialog** (`agents/max-assembly.md` §6.3) |
| 10 | Nothing was filled silently from `09`'s do-not-default list, and every P3-flagged `A-nnn` from §4 step 2 is named | you |
| 11 | A second run over the same locked spec produces the same node-name set | `11` H10 — two runs, compared. The determinism check, not an assumption |

**The measurement route.** Read the node back and compare against the spec — do not eyeball a viewport
and do not ask a tool whether the geometry "looks right". Read `node.min` / `node.max`, or equivalently
`node.width` / `node.length` / `node.height`; they agree because `Box` geometry is centred in X/Y and
based at `pos.z`. Compare X/Y against the `profile_cm` ring's extent and Z against `z_range_cm`, with
`abs(measured − expected) ≤ tolerances.linear_cm` — **0.5 cm, half a millimetre**. A larger mismatch is
a real inconsistency in the spec or the builder: report both figures and stop, and do not nudge the node
or widen the tolerance. For a group, read the dummy's `pos` against `parent_pivot_cm`.

---

## 9. Cleanup

Cleanup is part of the build, not a chore after it.

| # | Rule | Evidence |
|---|---|---|
| 1 | **Delete every test node in the same call that created it.** **If a call fails or is aborted, sweep** — do not assume nothing was created | An aborted probe leaves its objects behind; eight orphans accumulated and had to be swept |
| 2 | **Deleting a `Dummy` does not delete its children.** Delete the payload **explicitly**, then the dummy | `objects.count` fell by exactly 1 after deleting a dummy with one child |
| 3 | **The sweep is explicit** — `3dsmax-mcp_delete_objects` with spec-derived names, never "delete everything", and **compare `objects.count` before and after** — the count is the evidence | You are not the only tenant of that session; a blanket delete destroys the user's own work (`11` H12) |

Teardown order is always **payload first, then dummies**: a group deleted first leaves its elements
unparented on the correct layer, where they pass H1–H3 and still ship a wrong model (`11` §4.1). A bare
modifier is not a node and cannot be deleted. Cleanup never touches the massing itself — it stays.

---

## 10. Escalation policy

S2 escalates far more than it decides. The builder computes; it does not design.

| You may decide alone | Boundary |
|---|---|
| Which `07` §8.1 key an element's data belongs at; element id assignment and ordering | If a value does not fit a key, escalate — never invent one (`07` §12). Ids ascend, zero-padded, fixed order (§4) |
| Group composition | As long as every element is in **exactly one** group (**G-40**) |
| Which optional `07` §8.1 keys to populate | Omit rather than guess. An honest `null` beats an invented value |
| Storey bookkeeping from `levels[]`; creating the eight layers with `manage_layers` `create` | Arithmetic, never a judgement call. Creation is verified; **assignment is not, and is not yours** |

### 10.1 You must stop and ask

Any of these is escalated, always — using `10`'s ladder `E1`…`E9` and `01` §3's S2 row:

| Topic | Why | Goes to |
|---|---|---|
| **A missing or contradictory dimension** — a value `G-38` needs that `dimensions.json` does not hold, or two keys that disagree | S2 may not fill a dimension (§6.3) and may not hand-edit a locked file | **S1** |
| **A non-rectangular, rotated, or non-prismatic-in-Z footprint** (§6.3) | The builder refuses it by name; approximating it with a rectangle is a wrong model that validates, and `G-29` assumes prismatic | the user, via S1 |
| **An industrial clear height above the `G-16` cap of 600 cm** | `levels[].height_cm` is capped 250…600 by `G-16`, so the storey is not expressible. `CHECKPOINT.md` §P2 records this as a **KNOWN LIMITATION**: widen `07`'s range with the change recorded — **never narrow the range to fit, never fake the height** | **S1** — S2 never edits `07` |
| **Structural sizing** — column section, slab thickness beyond the documented defaults, core wall thickness, load paths, foundations | `09` §5 items 1–2: a licensed engineer's scope. A `low`-confidence proxy from S1 may be built; a better guess may not | the user (`E1`) |
| **A P3-flagged `A-nnn` that would change the geometry**, or **any fact not in `CHECKPOINT.md` §"Verified facts"** | You are the recheck stage (§4 step 2). §1.2: S2 escalates for an orchestrator probe, it does not open one | the user, naming the `A-nnn`; the orchestrator |

### 10.2 How to ask, and the draft path

A question list, not a paragraph — one line per question:

```
<dotted key path> — <the competing values with units> — <what each would change in the massing> — <your recommendation, if you have one>
```

If an escalation goes unanswered and the massing cannot be completed without it: **do not emit a partial
`massing.json` and call it done** — a file with a hole in it passes a casual read and fails S3. Do not
lock it over an unanswered question (`07` §3.1 makes `locked` a one-way promise). Report it as
`INCOMPLETE` with the value you would have used and what it costs. S2 does not inherit S1's draft.

---

## 11. Anti-patterns and incident guards

This repo has shipped **two fabricated negatives** (`CHECKPOINT.md` §"Incident log"). S2 runs against a
live session, so it is the stage most able to produce a confident-sounding negative about the
environment. The guard is unchanged: **nothing may be recorded as blocked, impossible, unbuildable,
non-existent or unsatisfiable without a transcript showing the attempt and the exact error.**

| Anti-pattern | Instead |
|---|---|
| Reinterpreting a key — reading `roof.deck_thickness_cm` downward because `07` §5.9 says so, against `G-38` | Build to the invariant the validator implements, report the discrepancy in one line (§6.2), move on |
| Inventing a default dimension — a plinth height, a kerb, a slab thickness, a column size | Escalate (§10.1). `09`'s do-not-default list is not a permission slip at S2 |
| Building geometry by hand in the viewport instead of from the spec | Run the builder. A `Box` drawn interactively has an auto-name, no `origins` entry and no audit trail |
| Adding layer code to the emitted script because the nodes land on the wrong layer | It cannot work — **nine routes ruled out**, final (`agents/max-assembly.md` §6.3). Layer is data; **no stage applies it** (**CORRECTED 2026-10-06:** this cell used to read "six routes executed, all threw. Layer is data; S5 applies it (§7)" — **S5 does not apply it either**) and **the user applies it in the Layer dialog** |
| Treating a **SKIP** as a **PASS** on any of `G-34`…`G-40` | A SKIP means the build is unproven. Escalate it and report it separately |
| Naming nodes interactively, or accepting Max auto-names (`Box01`, `Dummy001`) | The name is the spec id with `-` → `_`. An auto-name records creation order, not design |
| Approximating a non-rectangular profile with its bounding rectangle, or marking an element's `origin` as `given` / `assumed` / `conflict` | Refuse by name and escalate (§6.3). **Every S2 origin is `derived`** — S1 resolved the other three (`G-36`) |
| Naming `geometry_qa`, `contact_check` or `scene_qa`, or reporting a pass you did not run | **Those tools do not exist** — use the `execute_maxscript` read-back. And write `NOT RUN` and say why |

### 11.1 Context discipline

You are a worker with a small budget; the main thread is the scarce resource (`AGENTS.md`
§"Context budget", `01` §6). **Read `07` §8.1 and §9.6 once** and **`dimensions.json` once**, end to end
— never re-read 948 lines of grammar to settle one Z rule. **Compute, don't transcribe.** **One bridge
call per batch**: read-backs in one `execute_maxscript`, cleanup with the creating call. **Never
probe.** **No bulk dumps in the final message**; never read another agent's transcript.

---

## 12. Return contract

Return **exactly** this, **≤ 12 lines** — no file dumps, no JSON blobs, no transcript excerpts:

```
S2 <project id>
FILES: <path> (<n> lines) · <path> (<n> lines)
VALIDATOR: scripts/validate_specs.py --dir <specs_dir> --build -> exit <n>  (PASS <n> · FAIL <n> · WARN <n> · SKIP <n>)
G-34..G-40: <n> PASS / <n> SKIP — <for each SKIP, the reason the check could not be evaluated>
BUILDER: scripts/build_spec.py --stage massing -> exit <n> · <n> elements · <n> groups · <n> site_pad parts
LIVE: massing.ms ran in 3ds Max, no error · <n>/<n> nodes present · <n> nodes deleted in the sweep · scene otherwise empty
MEASURED: worst |measured − expected| across all elements = <n> cm (tolerance linear_cm = <n> cm) · layer names created via manage_layers = <n>, assignment not attempted (S5, action name unknown)
P3-RECHECK: <A-nnn ids> — <each named, or "none">
ESCALATED: <n> — <one line each: key path, the question, whether it is answered>
OBJECTIONS: <one line per defect in a file you do not own, naming file and line, or "none">
INCOMPLETE: <what you could not do, or "none">
```

Rules for the fields:

- **Line counts** are the real counts from disk. **The validator and builder lines are only valid with
  a transcript**: paste the exit code you observed; if you did not run one, write `NOT RUN` and say why
  on `INCOMPLETE`. **`SKIP` is reported separately from `PASS`**, never folded into it. **`MEASURED` is a
  number, not an adjective** — "matches" is not evidence; `0.0 cm worst deviation` is. If you measured
  nothing, say `NOT MEASURED`. **`P3-RECHECK` is never silently empty** — every `recheck_stage: "P3"`
  entry is named, because you are the recheck stage.
- **`OBJECTIONS`** is where the `G-38` / `07` §5.9 roof-thickness disagreement (§6.2), any
  `validate_specs.py` behaviour that contradicts `07` §9, and any stale UNVERIFIED label goes — one line
  each, naming the file. **`INCOMPLETE`** is where you say you could not finish; a field that hides a gap
  is worse than an admission.
