# max-orchestrator — the stage-by-stage driver: brief → locked specs → measured model in 3ds Max

> **Purpose:** this file is the **driver**, not a stage worker. It is the sequence an agent follows to
> take a user from *"here is my building brief"* to *"here is a measured model in Max that I can put
> materials on by hand"*. The five stage playbooks it routes to own the detail of their own stage; this
> file owns the order, the gates between stages, what to do when a stage fails, and what the user is
> actually handed at the end.
>
> **The one rule that governs everything here: MAXScript execution is the only ground truth.**
> Introspection tools lie (`introspect_class "NURBSSet"` → *Class not found*, and `NURBSSet()` then
> constructs fine). A stage that emits an artefact and never ran it has shipped nothing. **An emitted
> `.ms` is not done until `fileIn` has run it and its output has been measured** (`CHECKPOINT.md`
> §Incident log 2026-10-04, P3 and P4 — two for two). The table-shaped form: **an emitted CSV is not
> done until it has been placed in Max and counted** (P5).
>
> **Every number in this file is measured.** Ones I re-ran today are marked **[re-measured]**. Anything
> inferred is labelled **UNVERIFIED**. Anything I could not find is in §8, and I did not fix it.

---

## 1. Scope decision — read this first, it is the current truth

**P7 (Corona materials + UVs) and P9 (export) remain cancelled by user decision.** In contrast, the **S7 QA verification gate (`qa_check.py`) is active and verified.**
The deliverable is **a verified building model passed through the S7 QA gate that a human can put materials on by hand.**
`place_components.py` is the **last geometry builder (S5)**.

### In scope

| Stage | Playbook | Produces |
|---|---|---|
| **S1** input | `agents/max-input.md` | `dimensions.json`, `assumptions.json`, `conflicts_resolved.json`, all `locked` |
| **S2** massing | `agents/max-massing.md` | `massing.json` + `massing.ms` → **27** nodes |
| **S3** NURBS | `agents/max-nurbs.md` | `nurbs.json` (normalised) + `nurbs.ms` → **10** nodes (plus fixtures up to 37 nodes) |
| **S4** facade + registry | `agents/max-facade.md` · `agents/max-components.md` | `facade_grids.json`, `components_registry.json`, `facade_table.csv`, `world_table.csv` → 136 panels, 29 blocks |
| **S5** assembly (last geometry builder) | `agents/max-assembly.md` | `assembly.json` + `assembly.ms` → **244** nodes total (254 with NURBS), Mechanism A host hiding |
| **S7** QA verification gate | `agents/max-qa.md` | `qa.json` (`G-87`…`G-90`), query batches, oracle assessment → `qa-results.json` |
| **Hand-off** manual materials | §5 below | Corona material assignment by hand, layer mapping in UI |

### Out of scope — do not plan these, do not stub them

| Dropped | What it was | Why it is gone |
|---|---|---|
| **S6 / P7** Corona materials + UVs | `materials.json`, automated material assignment scripts | **User decision.** Materials are applied by hand. The renderer route is recorded in §5.4 |
| **S8 / P9** export | `export.json`, glTF / FBX / USD | **User decision.** The deliverable is a live 3ds Max scene |

`init_project.py` still writes `materials.json` and `export.json` as **reserved** stubs. They are placeholders in a scaffold, nothing more. `validate_specs.py` SKIPs them (`G-1` SKIPs on an absent reserved file), and no builder reads them. In contrast, `qa.json` is a defined spec file verified under `G-87`…`G-90`.

---

## 2. The pipeline at a glance

The pipeline workflow: **S1 → S2 → S3 → S4 → S5 (last builder) → S7 QA gate (`scripts/qa_check.py`) → Manual material assignment handoff**.
Numbers are the live gates actually executed in Max on `pavilion-01` (`CHECKPOINT.md` §Stage status), re-confirmed offline and live.

| Stage | Agent file | Builder command | Inputs that must exist | Outputs | The live gate — what "done" looks like |
|---|---|---|---|---|---|
| **S1** | `max-input.md` | `python scripts/init_project.py --project <id> --dir <workdir>` then `python scripts/validate_specs.py --dir <p>/specs/pipeline --build` | the user's brief | `dimensions.json` · `assumptions.json` · `conflicts_resolved.json` | **No Max call.** Offline only: `--build` exit 0, `FAIL 0`, every file `status: locked` **[re-measured]** |
| **S2** | `max-massing.md` | `python scripts/build_spec.py --stage massing --in <specs> --out <specs>` | `dimensions.json` (locked) | `massing.json`, `massing.ms` | `fileIn massing.ms` → **27 nodes = 22 `Box` + 5 `Dummy`**, identical `objects.count` over 3 runs, **9/9 bboxes 0.000000 cm** against a Python prediction |
| **S3** | `max-nurbs.md` | `python scripts/build_nurbs.py --in <specs> --out <specs>` | `nurbs.json` — **hand-authored or expanded via `expand_curves.py`** — plus `massing.json` / `dimensions.json` | `nurbs.json`, `nurbs.ms` | `fileIn nurbs.ms` → **10 nodes = 7 `SUR_` + 3 `DRV_`**, idempotent over 3 runs, every bbox measured, per-node `NURBSSurface` census matches |
| **S4** | `max-facade.md` · `max-components.md` | `python scripts/facade_tables.py --in <specs> --out <specs>` (default `--stage all`) | `dimensions.json` + `massing.json` | `facade_grids.json`, `components_registry.json`, `facade_table.csv`, `world_table.csv` | **No `.ms` to `fileIn`.** The gate is the consumer: 136 CSV rows read by MAXScript, 136 instances placed, `objects.count` == 136 + 29 = **165**, 5 bboxes **EXACT**, `baseObject` shared with a plain-`copy` control reporting `false` |
| **S5** | `max-assembly.md` | `python scripts/place_components.py --stage assembly --in <specs> --out <specs>` | **four** inputs: `dimensions.json`, `massing.json`, `components_registry.json`, `world_table.csv` | `assembly.json`, `assembly.ms` | **LAST geometry builder.** `fileIn massing.ms` then `fileIn assembly.ms` ×3 → `objects.count` == **244** = 27 + 136 + 29 + 52 (254 with NURBS), identical on runs 2 and 3, **0 modifiers**, Mechanism A host deactivation (`host_node.isHidden = true`), 52/52 cell bboxes exact, $B_{\text{total}}$ volume budget exact in $\text{cm}^3$ |
| **S7** | `max-qa.md` | `python scripts/qa_check.py --in <specs> --emit <run> --run-id <id>` then MCP collect then `python scripts/qa_check.py --in <specs> --request <req> --results <res> --out <run>` | all pipeline specs + live Max scene | `qa-request.json`, `qa-run-context.json`, `results.json`, `qa-results.json` | **QA verification gate.** 3-step loop: offline query emit → sequential MCP collection → offline assessment against tolerances. Evaluates 8 check families (`COVERAGE`, `CENSUS`, `NURBS-CENSUS`, `PLACEMENT`, `WALLS`, `FORM`, `STACK`, `REPLAY`). Exit 0 = PASS only |

### The two numbers that moved, and why they moved

| Stage | First measured | Now | What changed it |
|---|---|---|---|
| S2 | **18** nodes (P3: 13 elements + 4 grouping dummies + 1 site pad) | **27** | P6 added the **`facade_wall`** element kind: 8 hosts (4 facades × 2 levels) and a 5th grouping dummy. 13 + 8 = 21 elements |
| S3 | **6** nodes (P4: 3 surfaces + 3 derivatives) | **10** | P4b added the four relational kinds: `SUR_004`…`SUR_007`. 7 surfaces + 3 derivatives |

**Neither delta is a regression.** A reader who compares against P3/P4 numbers and sees 27 and 10 is
reading the current state, not a drift.

### The chain, in dependency order

```
brief
 └─ S1  dimensions.json ─┬─ assumptions.json ─┬─ conflicts_resolved.json      [hand-authored, locked]
                         │
                         ├─> S2  build_spec.py ────> massing.json + massing.ms ──> 27 nodes
                         │
                         ├─> S3  build_nurbs.py ───> nurbs.json  + nurbs.ms     ──> 10 nodes
                         │      (reads hand-authored or curve_gen expanded nurbs.json)
                         │
                         └─> S4  facade_tables.py > facade_grids.json
                                            └────> components_registry.json
                                                     facade_table.csv
                                                     world_table.csv         ──> 136 panels / 29 blocks
                                                              │
                            S2 massing.json ──────────────────-┤
                            S1 dimensions.json ────────────────┤
                                                              ▼
                               S5  place_components.py ─> assembly.json + assembly.ms ──> 244/254 nodes
                               [LAST GEOMETRY BUILDER]                  │
                                                                        ▼
                                                   S7  qa_check.py  (--emit -> MCP collect -> --assess)
                                                   [QA VERIFICATION GATE: coverage, census, form, walls]
                                                                        │
                                                                        ▼
                                                       Manual Material Assignment Hand-off
```

**Two facts about this graph that are not obvious:**

1. **`nurbs.json` is the one hand-authored derived file.** `build_nurbs.py` refuses when it is absent:
   *"nurbs.json is hand-authored at P4 — this stage reads it and emits the normalised spec plus the
   MAXScript, it does not compute the geometry."* **[re-measured]** `init_project.py` labels it
   "stub (generated at build time by `build_nurbs.py`)" in its dry-run plan, which is **wrong**. See §8.
2. **S5 needs `world_table.csv`, so S4 cannot be skipped or deferred** even though S5 consumes no panel
   geometry directly. It reads one placement per CSV data row (`G-72`).

---

## 3. Preflight — the mandatory first step

`scripts/env_preflight.py` **cannot talk to 3ds Max.** It is two-phase by design, and the two-phase part
is where people go wrong: a bare run exits **0** with everything **SKIP**, and that is not a pass.

### 3.1 The three-step dance

| Step | Command | What happens | What you must do |
|---|---|---|---|
| **1 · EMIT** | `python scripts/env_preflight.py` | Prints **seven** MAXScript probe bodies verbatim, then a table of **9 checks all `SKIP`**, then `PASS 0 / FAIL 0` and `skip 9`. **Exit 0** | Copy each probe body |
| **2 · CAPTURE** | `3dsmax-mcp_execute_maxscript` ×7 | Each body returns a string | Keep each returned string, keyed by the check name printed in emit mode. Separately capture `bridge` from `3dsmax-mcp_get_bridge_status` and `plugins_absent` from `3dsmax-mcp_get_plugin_capabilities` — those two have no MAXScript equivalent |
| **3 · SCORE** | `python scripts/env_preflight.py --results results.json` | Evaluates all 9. **Exit 1 on any FAIL.** Add `--json` for a machine-readable report | Read it. `PASS 9 / FAIL 0` is the gate |

`results.json` is a **flat JSON object**, check name → captured output. No wrapper, no nesting
(`load_results()` rejects anything that is not an object). The nine keys:

```
max_version   nurbset_present   loft_not_creatable   sweep_creatable   sweep_on_shape
quadpatch_creatable   materials   bridge   plugins_absent
```

`--transport namedpipe` overrides the `bridge` key without a results file.

### 3.2 What the preflight asserts, and the five absent plugins

| Check | Asserts | Note |
|---|---|---|
| `bridge` | transport is `namedpipe` | from `3dsmax-mcp_get_bridge_status`. **TCP `127.0.0.1:8765` is never used and never required** |
| `max_version` | `major=2026` — index **8** of the array `maxVersion()` returns | P7 evidence read `#(28000, 68, 0, 28, 3, 2, 30788, 2026, ".3.2 Security Fix")` |
| `nurbset_present` | `NURBSSet` resolves **and constructs** | Asserts **presence**. It was inverted once and briefly asserted the opposite, which would have failed on a healthy machine. Do **not** use `get #NURBSSet` — it returns `undefined` for real classes and made the probe pass vacuously |
| `loft_not_creatable` | `Loft()` throws *Not creatable* | `Loft` resolves; `Loft()` is not constructible. The real loft path is `NURBSULoftSurface` |
| `sweep_creatable` | `Sweep()` constructs | A standalone modifier is **not a scene node** and cannot be deleted. Never write `delete s` |
| `sweep_on_shape` | `addModifier (Rectangle()) (Sweep())` → `mods=1` | **Expect this to FAIL on the current build** — see §8 |
| `quadpatch_creatable` | `QuadPatch()` constructs | |
| `materials` | `OpenPBR` / `PhysicalMaterial` / `Standard` all construct | **By internalName.** `OpenPBRMaterial` does not exist |
| `plugins_absent` | `{"forestPack": false, "forestLite": false, "tyFlow": false, "railClone": false, "phoenixFD": false}` | **These five plugins are not installed.** Every tool that depends on them always throws |

**Never call**, because those five plugins are absent: `3dsmax-mcp_scatter_forest_pack`, all **14**
`3dsmax-mcp_tyflow_*` tools, `3dsmax-mcp_get_railclone_style_graph`. Substitutions: **Chaos Scatter** for
scatter (`ChaosScatter()` constructs; `CScatter` is the base and is `NotCreatable`), PhysX / Max
particles for physics, `3dsmax-mcp_clone_objects` instance mode for RailClone-style patterning.

### 3.3 Two more absences, so the whole picture is in one place

| Absent | Evidence | Consequence |
|---|---|---|
| The whole `mcg_*` family and `curve_model` | live toolset inspection, P4b-r | Max Creation Graph is **undrivable** from this bridge. The **MCG half** of `references/procedural-graphs.md` is moot; **its Data Channel half is live** (six real `*_dc_*` tools), so that file is split, not fenced |
| Layer **assignment** — any route | **nine** routes executed, P3 + P6 | `layer` is read-only from MAXScript; `manage_layers`' whole vocabulary is `{list, create, delete}`; `set_object_property` emits the same read-only assignment. **Layer is data, permanently.** See §5.3 |

---

## 4. Per-stage runbook

Conventions for all five stages:

- **`<p>` = the project's specs directory**, normally `<workdir>/<project>/specs/pipeline`.
- **Never hand-edit a builder output.** Every builder refuses to overwrite a file whose bytes differ
  from what it computes, naming the first differing key path. That refusal is the feature.
- **A non-zero exit is a stop.** Fix the input through the stage that owns it, or the builder through its
  owner. Never rename a key, widen `tolerances`, drop a leaf, or delete a row to silence a FAIL.
- **Offline gate after every stage:** `python scripts/validate_specs.py --dir <p> --build` **and** again
  with `--warnings-as-errors`. Both must exit 0. `SKIP` is reported separately from `PASS` and is **not**
  a pass — read each SKIP's stated reason.

### 4.0 The rehearsal, verified end to end **[re-measured]**

Before touching a real brief, prove the toolchain on the committed example. This is the fastest way to
find a broken environment, and it is the recipe §4.1–§4.5 assume:

```bash
python scripts/init_project.py --project rehearsal-01 --dir <tmp> --from examples
# --from examples writes 9 files. Delete the FOUR computed ones; keep nurbs.json (hand-authored):
rm <tmp>/rehearsal-01/specs/pipeline/{massing,facade_grids,components_registry,assembly}.json
python scripts/build_spec.py       --stage massing --in <p> --out <p>
python scripts/build_nurbs.py                    --in <p> --out <p>
python scripts/facade_tables.py                  --in <p> --out <p>
python scripts/place_components.py --stage assembly --in <p> --out <p>
python scripts/validate_specs.py --dir <p> --build      # -> PASS 138 / FAIL 0 / WARN 0 / SKIP 15, exit 0
```

Verified result: `massing.ms` → 22 `Box` + 27 node names, `nurbs.ms` → 10 node names,
`addModifier` count in `assembly.ms` → **0**, validator **PASS 138 / FAIL 0 / WARN 0 / SKIP 15**,
and the whole chain re-run a second time exits 0 with no refusal **[re-measured]**.

**Two traps in that recipe, both measured, both yours to know about:**

| Trap | Symptom | Cause | Action |
|---|---|---|---|
| `--from examples` does **not** copy the CSVs | `place_components.py` refuses: *"`world_table.csv` is missing. `assembly.json` resolves `world_table.csv` one placement per data row; emit it with `scripts/facade_tables.py --stage tables` first."* exit 1 | `--from examples` copies JSON only — **9 files, no `.csv`** | Run `facade_tables.py` first, which regenerates both CSVs |
| `--from examples` re-stamps `project` but not `source.reference` | `facade_tables.py` refuses: *"refusing to overwrite … the file on disk differs from what this build computes. First differing key path: `source.reference`"* | the seeded prose still names `pavilion-01`; the recomputation names the new id | **Delete the four computed files** before running the chain. Do **not** hand-edit them |

### 4.1 S1 — input

| | |
|---|---|
| **Playbook** | `agents/max-input.md` |
| **Commands** | `python scripts/init_project.py --project <id> --dir <workdir>` · `--dry-run` to plan · `--from examples` to seed · `--force` to overwrite files this generator created · `python scripts/validate_specs.py --dir <p> --build` |
| **Scaffold** | **12 files, 6 directories** **[re-measured]**. Three hand-authored (`dimensions`, `assumptions`, `conflicts_resolved`), four computed stubs, three **reserved** (P7/P8/P9), plus `project.json` |
| **Must exist first** | nothing |
| **Gate** | `--build` exit 0 · `FAIL 0` · all three files `status: locked` · no escalation unanswered. **No Max call at all** — S1 is forbidden the bridge |
| **Idempotency re-run** | N/A offline. Instead: a fresh `--from examples` scaffold must lint clean **[re-measured: PASS 136 / FAIL 0 / WARN 0]** |

**The one thing that stops everything downstream:** a `draft` file. Every builder refuses it by name:

```
error: refusing to build: <p>/dimensions.json has status 'draft', not 'locked'.
07 section 3.1: a builder must refuse to consume a draft or superseded file and must say which
file and which status it found.
```

`--allow-draft` exists for linting work in progress and will make `G-41`…`G-56` and `G-57`…`G-70`
**run and fail**. That is the point of the flag. Never use it on a deliverable.

### 4.2 S2 — massing

| | |
|---|---|
| **Playbook** | `agents/max-massing.md` |
| **Command** | `python scripts/build_spec.py --stage massing --in <p> --out <p>` (`[--json]`) |
| **Must exist first** | `dimensions.json`, locked |
| **Reads / writes** | reads `<p>/dimensions.json` · writes `<p>/massing.json`, `<p>/massing.ms` |
| **Stage selector** | `--stage massing` is the **only** value. Anything else → `error: unsupported stage 'X'. This builder supports: massing.` **exit 2** **[re-measured]** |
| **Self-check** | `G-34`…`G-40`, printed before the write: `self-check G-34..G-40 pass`. Builder also prints `model Z -30.0 .. 910.0 (building.overall_height_cm = 910.0)` **[re-measured]** |
| **Live gate** | `3dsmax-mcp_execute_maxscript` with `fileIn "<abs>/massing.ms"` — **absolute path**, one script per call, under ~2 s. Then: `objects.count` == **27**; run it twice more and assert the count and the node-name set are **identical**; `node.min` / `node.max` on a deterministic sample against `massing.json` within `tolerances.linear_cm` = **0.5 cm** |
| **Measured** | **27 nodes** = 22 `Box` + 5 `Dummy` · idempotent over 3 runs · **9/9 bboxes 0.000000 cm** · model Z `-30 … 910` == `overall_height_cm` **[P6 live gate]** |
| **Idempotency re-run** | `fileIn` it **three** times. Counts must read 27, 27, 27. **A second run that doubles the count is a FAIL, not a harmless repeat.** Then delete by name and assert `objects.count == 0` |

**The `node.pos` trap, which this stage is built around.** On a `Box`, geometry centres on `pos.xy` and
the **base sits at `pos.z`**. It stays true after `copy`, after `baseObject =` and after rotation. To
centre a box vertically, write `pos.z = cz − height/2`. Getting this wrong put **every P5 panel one full
height too high**, and the measurement is what caught it.

### 4.3 S3 — NURBS

| | |
|---|---|
| **Playbook** | `agents/max-nurbs.md` |
| **Command** | `python scripts/build_nurbs.py --in <p> --out <p>` (`[--json] [--build] [--allow-draft]`). **No `--stage` flag** — this builder has no stage selector |
| **Must exist first** | `<p>/nurbs.json`, **hand-authored and `locked`**. `massing.json` and `dimensions.json` are **optional**; absent, `G-49` degrades to a SKIP with a reason rather than a false PASS |
| **Self-check** | `G-41`…`G-56` — `16 pass, 0 skip, 0 fail` **[re-measured]** |
| **Live gate** | `fileIn "<abs>/nurbs.ms"` ×3 · `objects.count` == **10** and identical on runs 2 and 3 · every node's `node.min` / `node.max` measured against the spec within 0.5 cm · **per-node sub-object census** via `getNURBSSet node #relational` |
| **Measured** | **10 nodes** = `SUR_001`…`SUR_007` + `DRV_001`…`DRV_003` · idempotent over 3 runs · census: `SUR_001` 2 surfaces, `SUR_006` 1 (`NURBSBlendSurface`), `SUR_007` **0 surfaces / 2 curves** · `SUR_006_CanopySoffit` = `[0,450,420]..[1800,900,603.016]` · `DRV_001_VaultPanels` max z **600.97**, the design soffit, **not** the 25 cm shell |
| **Idempotency re-run** | 3 × `fileIn`, same count, same names, same bboxes |

**Two structural facts that a static check cannot see:**

1. **A surface is not evaluable until it is committed.** `appendObject` + `NURBSNode` are part of the
   *measurement*, not a detail. Relational properties (`rail`, `parent1`, `edge1`, `tension1`, `trim`,
   `seed`) read **only on the committed sub-object**; on a freshly constructed object **every name fails**.
2. **A derivative reads the FIRST `NURBSSurface`, never the last.** On a shelled surface the last is the
   offset shell — sampling it gave `z 441.043 … 625.94` instead of `420 … 600.97`, a **silent 25 cm
   error**. On a `blend` set the design surface is the **last**. Resolve by superclass, then confirm the
   sub-object carries the relational properties you just set.

**Hard safety rule:** `nurbs.ms` opens with
`if MCP_NURBS_Arch == undefined do fileIn "<ABSOLUTE PATH>/snippets/nurbs_arch_library.ms"` — the
library path is **baked in at build time**. If this repo moves, re-run `build_nurbs.py` or the emitted
script will `fileIn` nothing.

### 4.4 S4 — facade grid + component registry + tables

| | |
|---|---|
| **Playbooks** | `agents/max-facade.md` (S4a: grids + tables) · `agents/max-components.md` (S4b: registry) |
| **Command** | `python scripts/facade_tables.py --in <p> --out <p>` — default `--stage all`. Or `--stage grids` → `--stage components` → `--stage tables` in that order |
| **Must exist first** | `grids`: `dimensions.json` + `massing.json` · `components`: the **existing** `facade_grids.json` · `tables`: both JSONs |
| **Writes** | `facade_grids.json`, `components_registry.json`, `facade_table.csv`, `world_table.csv` |
| **Self-check** | `G-57`…`G-70`; `G-70` SKIPs in `--stage grids` and `--stage components` (*"this stage writes no CSV"*) and is asserted by reading the files back after `tables` |
| **Emits MAXScript?** | **No.** There is no `.ms` at this stage, so there is nothing to `fileIn` — §7 is the gate |
| **Measured** | 136 panels · 140 axes · 29 components · 6 families · panel kinds: `blank` 88, `spandrel` 26, `punched_window` 14, `mullion` 4, `vision` 2, `transom` 2 · every `(facade, level, bay)` area sum exact to 0.000000 m², zero interior overlap · 16/16 openings on **exactly one** panel · smallest panel 20 cm tall × 15 cm wide (a transom head band and a mullion pier — both legitimate) |

**Live gate for S4 — the table-shaped form.** Read `world_table.csv` **with MAXScript itself**, place, and
count:

| # | Step | Pass condition |
|---|---|---|
| 1 | Count data rows `N` from Python, not from the builder's log | `N == len(panels)`, computed independently |
| 2 | One `Box` prototype per distinct `component_ref`, sized from the CSV | `prototypes == 29` for `pavilion-01` |
| 3 | Place instances: `n = copy proto`, `n.baseObject = proto.baseObject`, `n.pos = […]`, `n.rotation = quat rot_z_deg [0,0,1]` | every node named `PNL_nnn` / `PLC_nnn` |
| 4 | Assert the count | `objects.count == prototypes + N` — measured **165** = 136 + 29 |
| 5 | Prove the instances are **reference** instances | the real instance reports `true`, **a deliberate plain `copy` in the same batch reports `false`**. A uniform `true` is a **broken probe** |
| 6 | Measure 5 nodes spanning **all four facades and both rotation classes**, against a prediction computed in Python | every axis exact — measured 5/5 **EXACT** |
| 7 | Delete everything, **two sweeps**, and assert | `objects.count == 0` |

**In the delivered pipeline this measurement is made inside S5's gate**, because `assembly.ms` places all
136 panels itself. The standalone S4 gate (165 nodes) is the P5-era transcript; the S5 gate
(244 nodes, §4.5) is the current one. Run S5's gate — do not run both and average them.

**The rotation field that will bite you.** `rot_z_deg` is the CSV's number and equals
`run_angle_deg = atan2(dy, dx)`. It is **not** `dimensions.facades[].direction_deg`, which is a compass
*facing label*: `F-S` and `F-N` both run along **+X** and carry `180.0` and `0.0`. Two of the example's
four facades are 180° wrong if you reach for the label. **`G-73` says the builder copies the table and
never recomputes placement geometry.**

### 4.5 S5 — assembly · the deliverable

| | |
|---|---|
| **Playbook** | `agents/max-assembly.md` |
| **Command** | `python scripts/place_components.py --stage assembly --in <p> --out <p>` (`[--json] [--build] [--allow-draft]`) |
| **Stage selector** | `--stage assembly` is the **only** value (and the default). Anything else → `error: unsupported stage 'X'. This builder supports: assembly.` **exit 2** **[re-measured]** |
| **Must exist first** | **FOUR** inputs — see the trap below |
| **Self-check** | `G-71`…`G-83` all pass **[re-measured]** |
| **Emitted script** | **1979 lines, 1 function, one call** `mcpAssemblyBuild_pavilion_01()` **[re-measured]** |
| **Live gate** | `fileIn massing.ms` **first** — `assembly.ms` throws `G-80: host EL_014 is absent; fileIn massing.ms before assembly.ms` for each of the 8 hosts. Then `fileIn assembly.ms` ×3 |

#### The four-input trap

`place_components.py` is the last builder in the chain and reads **four** files:

```
dimensions.json   massing.json   components_registry.json   world_table.csv
```

Copying only what `build_spec.py` writes gives you two of them, and the builder refuses:

```
error: refusing to build: <p>/dimensions.json is missing. assembly.json is the last derived file
in the chain and reads four inputs; a builder never invents an input (07 S-5).
```

**That refusal is correct.** When you build into a scratch directory, copy **all** of `*.json` **and**
`*.csv` — or, better, run the chain in §4.0 and let each builder produce its own inputs. exit 1.

#### The two `/tmp` directories

| Shell | Path |
|---|---|
| git-bash `/tmp` | `C:/Users/<user>/AppData/Local/Temp` (`%LOCALAPPDATA%\Temp`) — also what `tempfile.gettempdir()` returns **[re-measured]** |
| Python `os.path.realpath('/tmp')` | `D:\tmp` **[re-measured]** |

Writing a `.ms` to one and `fileIn`-ing the other produces **`can't open file`**, which reads exactly
like a build bug and is not one. **Resolve the absolute path in Python and hand that same string to
`fileIn`.** Always print the path you are about to `fileIn` before you call it.

#### The live gate, and the numbers a rerun must reproduce

| # | Step | Pass condition | Measured |
|---|---|---|---|
| 1 | Count the inputs **from Python** | `N` = CSV data rows 136 · `P` = placements 136 · `K` = opening cuts 16 · `W` = wall cells 52 · `C` = scatters 1 · `D` = distinct `component_id` 29 | 136 / 136 / 16 / 52 / 1 / 29 |
| 2 | `fileIn massing.ms` once, then `fileIn assembly.ms` **three times**, one call each | `objects.count` and the node-name set **identical** after runs 2 and 3 | 244, 244 |
| 3 | **Assert the count** | `massing + P + D + W`, read back — not assumed | **244** = 27 + 136 + 29 + 52 |
| 4 | Prove the instances are reference instances, **with a plain-`copy` control in the same batch** | sample `true`, control `false` | 5/5 `true`, control `false` |
| 5 | Measure 5 placed nodes against a **Python** prediction from CSV + registry | every axis ≤ 0.5 cm | worst **0.000000 cm** |
| 6 | **Measure every wall cell** bbox, and per host `Σ` cell volume vs `wall − Σ openings`; read `host.modifiers.count` for all 8 hosts | worst bbox **0**; worst volume **0 cm³**; every host stack **0** | 52/52 exact; **0.000000 cm³** on all 8 hosts (total wall **73 800 000 cm³**) |
| 7 | Verify the zero-modifier bound | `addModifier` count in the emitted source **0**, and **0** on every host | **0** and **0** |
| 8 | Delete everything, **two sweeps** | `objects.count == 0` | **0** |

**Idempotency re-run, and why it is the single most valuable check in this repo.** Every builder emits a
`fn`-wrapped builder that deletes its previous nodes by name and rebuilds, so a second run must be a
no-op. Run it **twice and assert the node count is identical**. This is not politeness:

- P3, P4, P4b and P6 each found a live-only defect **because** the file was actually `fileIn`-ed.
- P3's `massing.ms` failed on the **first** `fileIn`: `Compile error: no local declarations at top level`.
- P4's `nurbs.ms` ran, built 6 nodes, was idempotent, and was **still wrong** — a derivative read the
  offset shell instead of the design surface.
- P4b's first `nurbs.ms` would not compile at all: the generator emitted a Python-shaped
  `case kind of "u_loft":` dispatch that MAXScript rejects.

**Structural self-checks are necessary and not sufficient.** They prove the file is well-formed. Only
the interpreter proves it is loadable, and only measurement proves it is correct.

### 4.6 S7 QA verification gate (`agents/max-qa.md`, `scripts/qa_check.py`)

`place_components.py` (S5) is the **final geometry builder**. S7 does not create or modify geometry —
it is strictly a read-only verification gate executed across an offline/live 3-step loop:

```
  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
  │  qa_check.py    │  ==>  │  3ds Max (MCP)  │  ==>  │  qa_check.py    │
  │     --emit      │       │ execute queries │       │    --assess     │
  └─────────────────┘       └─────────────────┘       └─────────────────┘
   offline request +         sequential execution      strict wire parser +
   query batch scripts       captures to results.json  independent oracle
```

1. **Emit:**
   ```bash
   python scripts/qa_check.py --in <specs> --emit <run_dir> --run-id <run_id> [--calibration-cert <cert>]
   ```
   Reads and validates `qa.json` against `G-87`…`G-90`. Produces canonical `qa-request.json`, `qa-run-context.json`,
   and read-only query batches (`batch_001.ms`, etc.). Exit 0 = `READY/NOT_EVALUATED`.

2. **MCP Collect:**
   Feed each query batch file into 3ds Max sequentially via `3dsmax-mcp_execute_maxscript`. Max runs the queries,
   enforces `GUARD` unit assertions (`units.SystemType` / `units.SystemScale`), and buffers response lines between
   `START_BATCH` and `END_BATCH` sentinels. Save captured stdout strings into `<run_dir>/results.json`.

3. **Assess:**
   ```bash
   python scripts/qa_check.py --in <specs> --request <run_dir>/qa-request.json --results <run_dir>/results.json --out <run_dir>
   ```
   Parses wire output, checks completeness without zip truncation, and executes the independent analytical
   geometric oracle (`distance_to_arc`, `distance_to_barrel`) across 8 check families:
   - `QA-V1-COVERAGE`: all target solids and surfaces observed.
   - `QA-V1-CENSUS` & `QA-V1-NURBS-CENSUS`: element and surface counts match spec.
   - `QA-V1-PLACEMENT`: placed component positions match predicted coordinates.
   - `QA-V1-WALLS`: Mechanism A verified (`host_node.isHidden == true` prevents opening occlusion).
   - `QA-V1-FORM`: surface deviation evaluated against analytical mathematical formula.
   - `QA-V1-STACK`: zero-modifier invariant verified across all nodes.
   - `QA-V1-REPLAY`: idempotency across repeated runs.
   Emits `qa-results.json`. **Exit 0 on complete PASS only; exit 1 on FAIL/ERROR/INCOMPLETE.**

---

## 5. The hand-off — what the user receives, and how they material it

**This is the deliverable.** A human opens the scene and puts materials on it by hand.

### 5.1 The node census — 244, and every node accounted for

| Prefix | Count | What it is | Where it comes from |
|---|---|---|---|
| `EL_001`…`EL_021` + `SP_GROUND_PAD` | **22 `Box`** | massing: 8 `facade_wall` · 4 `column` · 4 `parapet` · 2 `slab` · 2 `core_wall` · 1 `roof_deck` · 1 site pad | `massing.ms` (S2) |
| `GRP_001`…`GRP_005` | **5 `Dummy`** | grouping parents | `massing.ms` (S2) |
| `PLC_001`…`PLC_136` | **136** | facade panel instances | `assembly.ms` (S5) |
| `PROTO_CMP_001`…`PROTO_CMP_029` | **29** | **one prototype per distinct component block** | `assembly.ms` (S5) |
| `WAL_EL_nnn_Cnn` | **52** | solid wall cells — the pierced walls, 11 + 12 + 7 + 6 + 4 + 4 + 4 + 4 over 8 hosts | `assembly.ms` (S5) |
| | **244** | **and `0` modifiers anywhere in the scene** | |

Also in the file as **declarations with no node**: `assembly.json.opening_cuts[]` (16 rows). Nothing is
cut, so no `CUT_` node exists. `assembly.json.scatter[]` (1 row) is also a declaration only — §5.5.

### 5.2 Material handles — and the one claim about them that is **false**

**Read this before telling the user anything about materials.** The obvious inference from the instance
route is wrong, and it was wrong in this pack until it was measured on 2026-10-05.

The instance route — and it is the only one, `setCopyMode` does not exist in this build:

```maxscript
local n = copy proto             -- a copy: its own base object
n.baseObject = proto.baseObject  -- now it REFERENCES the prototype's geometry
n.pos      = [x_cm, y_cm, z_cm]
n.rotation = quat rot_z_deg [0,0,1]
```

That gives **shared geometry**. It does **not** give **shared materials**:

| Measured 2026-10-05, on the built scene and again on a fresh 3-node test | Result |
|---|---|
| `instance.baseObject == prototype.baseObject` | `true` — the sharing is real |
| material set on the **prototype** → read on each instance | **`0` of 10 inherit**; all read `undefined` |
| material set on **each instance** | **10 of 10** set — per-node and independent |
| material set on an **instance** → read on the prototype | prototype unaffected — **no back-propagation** |
| `instance.baseObject.material = m` | **THREW** `Unknown property: "material" in Box` |
| negative control: the other 28 prototypes | **0** leaked — the probe discriminates |

**So the material pass is per-node: 136 `PLC_` + 29 `PROTO_` + 52 `WAL_` + 27 massing, or whatever
subset the user wants.** The 29 prototypes are still useful — as *named references* for sizing and for
`Component > Assign Material` by-component pick-lists — but **not** as one-click family handles.

`baseObject` sharing is a **memory optimisation, not an inheritance mechanism.** Never conclude "change
it once on the source and the copies follow" from "they share a mesh"; that inference is exactly what
went wrong here.

**Selecting a family, by hand:** a component id appears in `components_registry.json.families[].component_ids`
and on every CSV row for that component in the `component_ref` column of `world_table.csv`, so the
`PLC_` instances belonging to `CMP-nnn` can be listed from either source without clicking through Max.
To confirm the geometry link in Max, read `node.baseObject` on a prototype and on an instance — same
object.

**Three things to tell the user, because each is a trap:**

| Fact | Consequence |
|---|---|
| **The 29 prototypes are all created at `pos [0, 0, 0]`** — they sit stacked at the world origin, inside the building footprint, not at a scratch offset | Expect a 29-box cluster at the origin. **Do not delete them** — they are the only in-scene reference for each component's size |
| **`delete <prototype>` does not delete its instances** — measured at P5: after deleting all 29, all 136 instances survived unchanged | Deleting the prototypes is survivable; the instances keep their geometry and their own materials |
| **A node's sub-material / material-ID index is not reachable from MAXScript** in this build — `materialID`, `subMaterialID`, `matID`, `materialId` all throw, on a `Box` and on an `Edit_Poly`, with a bogus control throwing identically | Multi-material / per-face assignment is a **Material Editor** action, not a script one. `node.material = m` (whole-node) is the one assignment that works — 136 of them, one per node |

### 5.2b UVs — measured at P15, and they change the hand-off

**§5.2's headline is that material assignment is per-node. The opposite is true for UV modifiers**,
and the difference is the single most useful fact in this hand-off. Measured 2026-10-06 on the
delivered 244 nodes; full transcripts in **`references/13-uv-rules.md`**.

| Target | Nodes | Channel 1 today | What it takes |
|---|---|---|---|
| `PROTO_*` + `PLC_*` | **165** | **absent** | `addModifier` on the **29 prototypes only** |
| `EL_*` `SP_GROUND_PAD` `WAL_*` | **74** | **absent** | 74 individual modifiers — not instanced |
| `SUR_001`…`SUR_006` | 6 | **`0..1`**, present | scale it — see below |
| `DRV_*`, `SUR_007` | 4 | absent | manual in the UI |
| `GRP_*` `Dummy` | 5 | n/a | no mesh |

**A modifier on a prototype propagates to every node sharing its `baseObject`** — the opposite of
materials. Measured: `addModifier` on the 29 `PROTO_*` nodes took the chain from **0 to 165**
UV-carrying nodes. Confirmed with a 4-node controlled test (`SRC` + 3 `copy`/`baseObject`
instances, all four picked up channel 1) and with `baseObject` identity per family.

So **the UV pass on the panel system is 29 calls, not 165** — while the material pass is 165.
Same scene, two opposite propagation rules, both measured.

**For world-scale UVs, the working recipe** — `realWorldMapSize:true` makes **1 UV unit = 1 cm**,
verified on three independently placed boxes (4×6×2 → span `4.0 × 6.0`; 400×600×2 →
`400.0 × 600.0`; 300×150×20 → `300.0 × 150.0`). **One tile per metre ⇒ `utile` = `vtile` = `0.01`.**
On the delivered panels, `maptype:4` (Box) + `realWorldMapSize:true` returns uv span **exactly equal
to the node's cm extent** — `PLC_001` 135×3×90 → `135.0 × 90.0`; `WAL_EL_014_C01` 135×20×420 →
`135.0 × 420.0`.

⛔ **Two traps, both measured, both silent.**

| Trap | Consequence |
|---|---|
| **`utile`/`vtile` written in the SAME `execute_maxscript` call that adds the modifier are discarded.** It reads back correctly in-call and reverts to `1.0` next call — 8/8. `maptype` and `realWorldMapSize` are unaffected | The user sets the density, sees it read back, and gets 1.0. **Write in a separate call**, or force an evaluation (`snapshotAsMesh`) between the `addModifier` and the write (3/3) |
| **`setTiling` silently floors its arguments to integers, and `getTiling` echoes the request rather than the result** — `setTiling s 3.5 1.5` → `getTiling` reads `[3.5, 1.5]`, actual UVs `3.0 × 1.0` | Any surface whose width is not a multiple of the tile size gets the wrong density, silently. **Do not use `setTiling` for density** — `Uvwmap` with `utile`/`vtile` accepts fractions |

`generateUVs1:true`, which the NURBS builders emit, is now measured: a **`0..1` normalised map
regardless of the surface's cm size** (600 cm and 1800 cm surfaces both give span `1.0 × 1.0`).
Usable, but it is not world scale — so NURBS surfaces need the same `Uvwmap` pass as everything else.
**Whether to change the builders is a user decision**; it is not changed here, because UVs are a
hand-off step and `G-81`'s zero-modifier rule governs builder output.

`Unwrap_UVW` constructs and attaches but is **unusable through this bridge** — it changes nothing
and every one of its methods throws when invoked. Unwrapping is a manual, in-the-UI operation.

### 5.3 Layers — data the user applies, not code the pipeline runs

**Layer assignment is impossible from this bridge.** Nine routes were executed and all failed:
`node.layer = …` in three forms (all `Property is read-only: layer`), `LayerManager`'s missing setter,
`node.setLayer`, `node.setProperty #layer`, `3dsmax-mcp_manage_layers` object assignment (40+ candidate
action names, all `Unknown layer action`), and `3dsmax-mcp_set_object_property` with `property=layer`
(a positive control on the same tool with `property=pos` succeeded, so the tool works and `layer` is the
blocker). **This is final, not an open question.** `manage_layers`' whole vocabulary is
`{list, create, delete}`.

**Where the data is:**

| File | Key | What it tells the user |
|---|---|---|
| `massing.json` | `elements[].layer` · `site_pad.layer` · `grouping[].layer` | per-element target layer: `00_SITE`, `01_SLABS`, `02_STRUCTURE`, `03_CORE`, `04_ROOF` |
| `assembly.json` | `placements[].layer` · `layer_map` | `05_FACADE` on all 136 · `layer_map` maps `05_FACADE → {entrance_door, frame_member, glazed_panel, opaque_panel}` and `99_DEBUG → {scatter_source}` |
| `world_table.csv` | `layer` column | the same, one row per panel |
| `massing.json` · `grouping[].layer` | | `90_SCENE` |

The **closed eight-name vocabulary** (`references/07-spec-grammar.md` §8.1.4): `00_SITE`, `01_SLABS`,
`02_STRUCTURE`, `03_CORE`, `04_ROOF`, `05_FACADE`, `90_SCENE`, `99_DEBUG`. **`assembly.ms` contains no
layer statement at all** (`G-79`) — grepping it for `node.layer` or `LayerManager` returns 0 matches, and
that is a **build FAIL** if not.

**The user's action:** `3dsmax-mcp_manage_layers create` for the eight names (or the Layer dialog), then
select nodes by name prefix and assign. Suggested mapping by prefix: `EL_`/`SP_` → `massing.json`'s
per-element `layer`; `PLC_` → `05_FACADE`; `WAL_` → the `facade_wall` host's own layer
(`05_FACADE`); `GRP_` → `90_SCENE`; `SCT_` → `99_DEBUG`.

### 5.4 Rendering with Corona

The user's production renderer is **Corona**; Max reports **Arnold** as active. **Set it explicitly.**
`Arnold` is active and Corona is present — never assume.

**The setter needs an INSTANCE, not the class.** This is the trap:

```maxscript
renderers.current = Corona      -- THROWS: Unable to convert: Corona to type: Renderer
```

```maxscript
local c = Corona()              -- construct an INSTANCE  (~3.5 s cold, ~0.4 s warm)
renderers.production = c        -- OK, reads back Corona
renderers.current    = c        -- OK, reads back Corona -- both slots, not aliases
```

Two operational notes:

- **Call `Corona()` in its own `execute_maxscript` call.** At **~3.5 s cold** it blows the standing
  "one script per call, under ~2 s" budget, and the first call will read as a timeout if it shares a
  call with anything else. This call is the **one exemption** to the budget rule.
- `superClassOf Corona` is `MAXWrapper`, not `Renderer`. `isKindOf … Renderer` is **not** a valid
  membership test. `RendererClass.classes` is the only way to enumerate engines and it does list Corona.
- The bridge's own read at `capabilities.py:15` uses `classOf renderers.current`, which returns the class
  name as a `Name` — so it reads fine **and looks like the thing you can assign back. It is not.**

**Materials, for reference only.** P7 was cancelled, but if the user asks what to build with:
`_CoronaPhysicalMtl` is the architectural material and **has a leading underscore** — `CoronaPhysicalMtl`
is not a name in this build. 16 Corona classes exist, **15 construct**, and `CoronaPortalMtl` throws.
171 properties, camelCase, in `<slot>` / `<slot>Texmap` / `<slot>TexmapOn` / `<slot>MapAmount` quadruples.
Naming is **camelCase**, not snake_case. Enum modes (`metalnessMode`, `roughnessMode`, `iorMode`,
`alphaMode`, `normalFilteringMode`, `gBufferOverride`) read as **`Integer`** and their meaning is **not
discoverable from MAXScript**. A bogus property name **throws on both read and write** — unlike the NURBS
constructors, which silently swallow unknown keywords, so a typo here fails loudly. That is good.

### 5.5 The Chaos Scatter is a declaration, not geometry — and how to apply it

**`assembly.ms` emits no scatter node at all.** I grepped the 1979-line emitted script: zero occurrences
of `ChaosScatter`, `scatter` or `SCT_001`. `assembly.json.scatter[0]` is a **declaration**:

```
SCT-001 · node_name SCT_001 · target_ref EL_009 · model_refs ["EL-003"] · seed 26010
          instance_count_limit 60 · distribution_density_pattern 0.02
          scale 0.85→1.15 · rotation -180→180 deg · collision_avoid true · layer 99_DEBUG
```

The apply route is the library in `snippets/chaos_scatter.ms`, which is **`fileIn`-safe and creates
nothing on load** — every mutation lives inside a named function body:

```maxscript
fileIn @"<abs>/snippets/chaos_scatter.ms"
local cfg = MCPChaosScatter.config(seed:26010, instanceLimit:60, densityPattern:0.02,
                                   collisionAvoid:true, rotationFrom:-180.0, rotationTo:180.0)
MCPChaosScatter.create "SCT_001"
local r = MCPChaosScatter.apply (getNodeByName "SCT_001") cfg \
              targetNodes:#("EL_009") modelNames:#("EL_003")
MCPChaosScatter.census  (getNodeByName "SCT_001")   -- -> #(name, instances, models, modelOrderOK)
```

> **Applying the scatter changes the node count.** 244 is measured **before** it. The scatter adds one
> `ChaosScatter` node plus its instances. Measure and report both numbers; do not report 244 and then
> silently have 300 nodes. **Do not guess** whether the scatter belongs in the delivered model — see §8.

Two naming facts, both measured: `distributionDesityPattern` is the **real** MAXScript property name —
**the typo is in Max, not in the library**. The spec uses the corrected
`distribution_density_pattern`; the builder emits the typo. And `seed` is **1 … 31337** and is **data**,
never generated at run time, or the scatter is irreproducible.

**The 20-modifier freeze happened with no Chaos Scatter object in the scene at all** (§7), so the trigger
is the geometry-stack change itself. Scatter presence is **not** required for the hazard, and the hazard
is **not** scatter-specific.

### 5.6 One line to the user

> 254 nodes for the whole S1→S5 chain — or **244** if you stop after massing, which is what P6 measured:
> massing in `EL_`/`GRP_`, 136 facade panels as `PLC_` instances sharing 29 `PROTO_` prototypes' geometry,
> and 52 `WAL_` cells tiling each wall around its openings. **Materials are per node, not per prototype** —
> the panels share a mesh, not a material, so a material on a `PROTO_CMP_nnn` block does *not* reach its
> panels (§5.2, measured). Layers come from `massing.json` / `assembly.json` `layer_map` in the Layer
> dialog; nothing assigns them from script. Set Corona with `renderers.production = Corona()` — assign
> the instance, not the class.

---

## 6. Failure playbook

Every row is a real incident. Nothing here is hypothetical. Full transcripts: `CHECKPOINT.md`
§Incident log and §Bridge transport.

| Symptom | Cause | Action |
|---|---|---|
| `ConnectionError: Could not connect to 3ds Max on 127.0.0.1:8765` | **The MCP client caches the pipe name for the process lifetime.** `MaxClient.__init__` calls `discover_instance_pipes()` exactly once; a Max restart changes the PID, hence the pipe, and the client calls `CreateFileW` on the dead PID's pipe forever. **The error names TCP even when the pipe is what failed** | Two-line check: read `%LOCALAPPDATA%\3dsmax-mcp\instances\pid-<PID>.json`, then `CreateFileW` on each name — live is `open`, dead is `ERROR_FILE_NOT_FOUND`. Stale files are **never pruned**. **Max is usually fine.** Then **restart opencode** — restarting the Max client is not enough and killing the MCP server does not recover in-session |
| `execute_maxscript` **times out** | Either a recoverable hang or the 20-rung freeze. **A timeout is the only symptom of the freeze** | **Never conclude "the bridge is down" from a timeout.** Run a cheap `3dsmax-mcp_get_bridge_status` first. The scene may be alive and merely busy |
| Everything times out, then the bridge stops answering; Max needs killing | **20 modifiers on one node in one scripted call.** 10 rungs clean, 20 froze Max until the machine rebooted | Do **not** re-run the ladder — it is measured and the price is a reboot. Assemble stacks ≤ 5 per call; > 10 on one node is forbidden without asking the user |
| Response has `error: ""`, `success: true`, and `result` **beginning `__MCP_MS_ERR__:`** | **The bridge's error surface has two shapes.** Every aborted probe in the P7 pass returned `success: true` | **A caller that checks only `success` sees a false pass.** Check for the `__MCP_MS_ERR__` prefix on every result |
| `Compile error: no local declarations at top level: SP_GROUND_PAD` | **`local` at the top level of a `.ms` is a compile error** | The emitted script must wrap its whole body in one `fn` plus one call. Never hand-edit the emitted file — fix the builder |
| `Syntax error: at string, expected ( … In line: "u_loft":` | The generator emitted a Python-shaped `case kind of "u_loft":` dispatch. MAXScript `case` forbids string case-labels | Map the kind to an integer, keep the branch bodies. `verify_script` cannot catch this — only the compiler can |
| `Type error: Call needs function or class, got: undefined` from `if (getNodeByName "X") != undefined do (…)` | Context-dependent: the one-liner works inside `fileIn` and **throws inside a direct `try`/`catch`** | Explicit-local form only: `local prev_X = getNodeByName "X"` then `if prev_X != undefined do ( delete prev_X )` |
| An aborted probe leaves orphans; `objects.count` will not reach 0 | An unguarded property access threw and killed the script **before** the cleanup block. Four of the P7 probes aborted this way | **Put the cleanup block FIRST**, or keep a separate sweep call ready. Wrap every property probe in its own `try ( ) catch ( )` |
| `for o in objects do delete o` "works" and leaves 24 orphans | **It silently skips entries** | Collect names first, delete by name, and **run the sweep twice** — deleting a base does not delete its instances |
| Everything is one full height too high | **`node.pos` on a `Box` puts the base at `pos.z`.** It survives `copy`, `baseObject =` and rotation | `pos.z = cz − height/2`. This is how the P5 panels were wrong; the measurement caught it |
| `can't open file` on `fileIn`, right after a successful build | **The two `/tmp` directories.** git-bash `/tmp` is `%LOCALAPPDATA%\Temp`; Python's `os.path.realpath('/tmp')` is `D:\tmp` | Resolve the absolute path **in Python** and hand that same string to `fileIn`. Print it before you call |
| `refusing to build: … dimensions.json is missing … reads four inputs` | `place_components.py` needs four inputs and you copied two | Copy **all** of `*.json` **and** `*.csv`, or run the §4.0 chain. The refusal is correct — exit 1 |
| `refusing to overwrite … first differing key path: source.reference` | A generated file on disk differs from what the builder computes — usually a `--from examples` scaffold whose prose still names the old project | Delete the computed file and rebuild. **Never hand-edit a builder output** |
| A validator/budget harness prints `PASS` having made zero comparisons | Two harnesses did exactly this. One printed `VERDICT: PASS` after comparing `EL-014` against node names spelled `EL_014` — **zero comparisons happened** | **A verdict must require that the expected number of comparisons actually occurred.** Check the pair of spellings |
| Fault injection reports `0 of 8 fired` | The harness mutated a **builder output** and rebuilt, so the rebuild overwrote the mutation before any rule saw it | Call the predicates directly with a mutated **document**. Measured that way: 11/11 fire |
| A census passes against a scene where nothing was built | The census **counted its own loop iterations** instead of walking the scene. It read `cut_count = 16` against **zero** modifiers anywhere | A counter is unfalsifiable by the very failure it exists to catch. `G-80` now walks `objects`; `assembly.ms` throws `G-81` if any host carries a modifier |
| A Boolean modifier attaches and cuts nothing — **silently** | `Boolean()` throws; `BooleanMod()` carries **Voxel Map's** paramblock; the bridge's `add_modifier` **attaches** one whose operand is never set (`verts=8 faces=12`, unchanged, for every `params` spelling) | **Openings are cut by tiling walls with solid `WAL_` cells, not by a modifier.** A modifier that attaches and does nothing is worse than one that throws |
| A build refuses with `Unable to convert: OK to type: Integer` | `appendObject` returns the **string `"OK"`**, not an index | Index = `nset.numObjects` read **after** the call |
| `Argument count error: StopCreating wanted 0, got 1` | `stopCreating` takes **0** arguments | Bare `stopCreating` |
| `getModifier 1 node` throws | It does. `node.modifiers[1]` works | Use the property. The first `assembly.ms` used `getModifier` in its own idempotent stack reset, so the reset never ran |
| A probe tool reports a class does not exist, and it does | **`introspect_class "NURBSSet"` → *Class not found*, and `NURBSSet()` then constructs fine.** This false negative rewrote a whole plan. `discover_plugin_classes` listed 78 of 160 modifiers; `inspect_plugin_constructor` returns `inferred: true` guesses | Execution is the only ground truth. **Never test existence without a known-bogus control in the same batch** |
| A probe returns a uniform result across a heterogeneous name list | **A uniform `ERR` is a broken probe, not a uniform absence.** P4's list had no known-positive | Include a **known-positive** *and* a bogus name in every property probe. A bogus control proves absence; a positive proves the probe can detect presence |
| Everything on an NURBS relation reads `ERR` | Relational properties are readable **only on the committed sub-object**. Read them pre-commit and every name fails — this is what produced the false "rail sweeps are not implemented" conclusion | Build it, `appendObject`, `NURBSNode`, **then** read. Also: `o["name"]` is **not** valid dynamic property access — always `ERR` |
| `EXCEPTION_ACCESS_VIOLATION` reading address `0x3089`, Max dies | **A synthetic `nurbsID` in a `parent*ID:` slot is a process crash**, not a catchable error | Every `parent*ID:` must be a variable bound from a committed sub-object. `G-56` exists for this alone — it is the only rule here whose failure mode is a crash rather than wrong geometry |
| A surface's parameter domain is not `[0,1]` | `point_grid` is **chord-length**; `cv_grid` and both rail sweeps are `[0,1]` | Read the domain. `evalPos` on `[0,1]` by habit samples the wrong place |
| `NURBSPointCurve` node bbox does not match its own rectangle | A NURBS node's `min`/`max` is **not** the NURBS geometry — it is a node bound inflated by tessellation | Sample `evalPos` on the committed surface. Measured: a curve over `750…1050 × 375…525` reports node bbox `714.645…1080.17 × 286.503…617.732` |
| A Rhino tool errors when called against Max | A large set of names in the connected toolset belongs to the **Rhino** server | Never call `get_objects`, `analyze_objects`, `measure_objects`, `boolean_*`, `loft`, `sweep1`, `pipe`, `extrude_curve`, `section_profile`, `capture_viewport`, `get_document_summary`, `create_object`, or any `gh_*` against Max. **Do not conclude the bridge is down because one errored** |
| `mcg_*` or `curve_model` is missing | **They do not exist in this bridge.** Confirmed by live toolset inspection | Record the absence. Do not emulate Max Creation Graph by hand |

### 6.1 Two habits that prevent most of the table

1. **A timeout is not a diagnosis.** `3dsmax-mcp_get_bridge_status` is cheap. Run it before concluding
   anything about Max.
2. **A subagent's report is a claim.** Verify it yourself. One P1 batch reported "all 39 nonexistent
   tools removed"; an independent `grep` found 13 remaining occurrences. They turned out to be legitimate
   warnings — but that was only established by **checking**.

---

## 6.2 The improvement log — record findings when a session produces them

**You own this. Every stage agent inherits it by reading this section.**

A modelling session is where the pipeline meets a real building, and real buildings produce findings the
rehearsal could not. Without a place to put them, they die with the session and the next one rediscovers
them. So:

> **If a session produced a real finding, write it to `<project>/IMPROVEMENTS.md`. If it produced none,
> write nothing and create no file.**

**Format and field rules: `references/improvement-log.md`. Read it before writing the first entry.** It
is the single source of truth for the entry shape; this section owns only the trigger.

### The trigger — three categories, and nothing else

| # | Category | The test |
|---|---|---|
| 1 | **A measured value that is wrong** | a bbox off by more than `tolerances.linear_cm`, a count that disagrees with the spec, an idempotency violation |
| 2 | **Something the pipeline cannot express** | an element with no `kind`, a dimension with no key, a facade situation the grid will not decompose into. **The most valuable kind — it is a gap in the grammar, and grammar gaps only appear on real buildings** |
| 3 | **A spec value that is legal but wrong here** | inside its declared range, passes every `G-` rule, and is still the wrong number for this building |

### Three things that are NOT triggers

- **A routine run.** Chain built, every gate passed, numbers matched → write nothing.
- **Something already in `CHECKPOINT.md`** → link to the entry instead of restating it.
- **A suspicion you did not measure.** "The blend tension might be wrong" is not a finding. This repo
  shipped **four fabricated negatives**, each costing a stage; a log full of unmeasured suspicions is
  the same failure in a new file. **If you did not run it and read a number, it does not go in.** A
  genuinely worthwhile open question goes under §"Open questions" with the exact probe that would
  settle it.

**The honest test: would a competent architect arriving at this model tomorrow be worse off for not
knowing this?** If no, write nothing.

### The line that keeps this file from becoming a second `CHECKPOINT.md`

> **A log entry describes THIS PROJECT. A `CHECKPOINT.md` entry describes THE PACK.**

If the finding is *"the skill pack is wrong"* — a wrong default, a builder that invents a value, a
documented tool that does not exist — it belongs in `CHECKPOINT.md` §"Open bugs", gets fixed there, and
the log entry **cites** it. If the finding is about *this building* — a bay that needs a spandrel depth
the registry does not carry, a slab that lands on the wrong storey — it goes in the log.

An agent that finds a problem **writes an entry. It does not go editing `locked` JSON** because a note
disagreed with it. Specs change through their owner stage, through its own gate, with the conflict
logged in `conflicts_resolved.json`.

### `IMPROVEMENTS.md` is never scaffolded

`init_project.py` writes 12 files and 6 directories. That count stays correct — a pre-created empty
log would assert that a finding was recorded, which is a lie. Create the file by hand, with the header
from `references/improvement-log.md` §5, the first time there is something to put in it.

It lives in the **project root**, beside `project.json`, **not** in `specs/`. `specs/pipeline/` is the
locked, `G-`-linted contract; a free-text observation file sitting next to it invites an agent to "fix"
the contract to match a note. `validate_specs.py`'s `discover()` globs `*.json` only, so the log is
invisible to the linter **by design** — nothing in the pipeline may depend on a file whose presence is
optional.

### Every entry needs an owner and a severity

`references/improvement-log.md` §4 defines the eight required fields. Two of them are what make the
log worth reading six weeks later:

- **Severity** — `note` · `fix-before-S5` · `blocks-S5` · `blocks-delivery`. A finding with no severity
  is a complaint.
- **Proposed + owner** — the change **and which stage owns it**. Never "fix this". A finding whose fix
  would require a builder to invent a value is an **S1** finding by definition, because `S2`+ may not
  invent inputs.

And `Status: applied` is a **claim that the pipeline now produces a different, verified number** — it
needs the re-run gate output quoted in the **Measured** field. Editing a builder and logging `applied`
without re-running the gate asserts a verification that never happened, which is the exact failure
this repo keeps paying for. `rejected` with a reason is a first-class outcome: it tells the next
session the question was already asked.

### Tell the user at the end, in one line

When the log has entries, add to your hand-off (§5.6) a line like *"2 findings logged in
`IMPROVEMENTS.md` — one `blocks-S5` (bay 7 spandrel depth, owner S1)."* When it has none, **do not
mention it.** A log that is announced every session trains the user to ignore it.

---

## 7. Hard limits

Each row is a standing rule **with the evidence that produced it**. Reasoning and transcripts:
`CHECKPOINT.md` §"Verified facts", §Incident log, and `agents/max-assembly.md` §6.5. Do not re-derive
these; do not re-measure the ladder.

| Limit | Evidence |
|---|---|
| **≤ 5 modifiers per `execute_maxscript` call. > 10 on a single node is forbidden without asking the user.** | Deliberate bounded ladder, clean scene, one rung per call, 2026-10-05: 2 · 5 · 10 **clean** (~30 ms each, `modifiers.count` tracked the rung) · **20 → `execute_maxscript` timed out, then `get_scene_snapshot`, then the bridge stopped answering; Max killed, machine rebooted.** The exact break between 10 and 20 is **not established and must never be re-measured** |
| **One script per call, under ~2 s** | `execute_maxscript` runs on Max's **main thread**; a long script freezes the UI. **One exemption:** `Corona()` costs ~3.5 s cold and needs its own call |
| **Zero modifiers in this pipeline** | Not prudence — design. `assembly.ms` emits `addModifier` count **0** (`G-81`) and throws `G-81` if any host arrives with a non-empty stack. Openings are tiled cells. The ladder is *why* the ceiling is zero rather than merely small |
| **`local` at the top level of a `.ms` is a compile error** | `fileIn examples/massing.ms` → `Compile error: no local declarations at top level: SP_GROUND_PAD` |
| **`try { } catch { }` (brace form) is a parse error** | Use `try ( ) catch ( )`. Both observed 2026-10-04 |
| **`getCurrentException()` inside a `catch` throws itself** | Turns a catchable error into a script abort. This is what made two probes abort mid-way |
| **`global fn`, `local fn`, and a bare top-level `fn` all fail through `execute_maxscript`** | Parse errors. Inline the code instead. (`local function` is also not valid; `local fn` is valid *in a file*) |
| **`setCopyMode`, `rotationZ`, `rotationX`, `rotationY`, `matrix3`, `angle`, `findString` do not exist** | Calibrated sweep: `copy`, `Box`, `filterString`, `openFile`, `readLine`, `findItem`, `matchPattern`, `pi`, `quat` all resolve; `TotalGarbageXYZ_fn` does not. **Use `n = copy src` then `n.baseObject = src.baseObject`; `n.rotation = quat <degrees> [0,0,1]`; `substring s 1 n`** |
| **`fileExists` → `doesFileExist`; `executeFile` / `runScript` → `fileIn`; `modifiers <node>` (function) → `node.modifiers` (property)** | Each verified by execution |
| **`stopCreating` takes 0 arguments** | `Argument count error: StopCreating wanted 0, got 1` |
| **`getPropNames` does not exist**; `compile "…"` does not close over enclosing locals | Dead ends for API discovery. `getPropNames` **does** work on built-in materials (171 names on `_CoronaPhysicalMtl`) — the failure is specific to the NURBS plugin classes |
| **`o["name"]` is not valid dynamic property access** | Always `ERR`, even for a property that reads fine literally. `getProperty o ("radius" as name)` **is** valid on built-ins. `getProperty` takes a **Name**, never a String |
| **`Dummy boxSize:` needs a `point3`** | A float throws `Unable to convert: 100.0 to type: Point3`. `getChildren` does not exist; use `dummy.children` |
| **Scene units are centimetres, `units.SystemScale 1.0`** | `units.SystemType == #centimeters` → `true`, all other constants `false`. **No conversion happens at the boundary.** Read `units.SystemType` directly — `getProperty units #SystemType` fails |
| **A bare modifier is not a scene node** | `Sweep()` cannot be `delete`d. Attach it to a node and delete the node |
| **`delete <base>` does not delete its instances** | Measured: after `delete bx`, `Box002` survived. Same rule as dummies |
| **Layer is data, permanently** | Nine routes executed, all failed. See §5.3 |
| **Never call the absent-plugin group** | forestPack, forestLite, tyFlow, railClone, phoenixFD are not installed: `scatter_forest_pack`, all 14 `tyflow_*`, `get_railclone_style_graph` |
| **Never rewrite a reference on suspicion** | `references/nurbs-complete-guide.md` and `nurbs-architecture-recipes.md` were marked unverified and were **vindicated** at P4b. Verify claim by claim, then correct only what actually fails |

---

## 8. OPEN — orchestrator must fill

Nine items. **None of them is fixed here** — this file owns only itself. Each is a real defect or
ambiguity I measured and could not resolve without touching a file I do not own.

### Blocking — the delivered pipeline cannot be rehearsed from a clean scaffold as documented

| # | Finding | Evidence | Needs |
|---|---|---|---|
| **1** | **`init_project.py`'s `assembly.json` stub omits `wall_cells`**, so a fresh untouched scaffold FAILs the validator. `CHECKPOINT.md` §Next actions records *"Fresh scaffold, `--allow-draft` → **FAIL 0 / WARN 0**"* — that is **stale** | `python scripts/init_project.py --project demo-tower --dir …` then `validate_specs.py --dir …/specs/pipeline --allow-draft` → **`PASS 105 / FAIL 1 / WARN 0 / SKIP 72`**, exit 1. The single FAIL: `G-1  assembly.json — assembly is missing declared top-level keys: **wall_cells**`. The stub declares `placements`, `opening_cuts`, `scatter`, `layer_map`, `defaults` — but not `wall_cells` **[re-measured]** | Decide: add `wall_cells: []` to `scaffold_assembly()` in `scripts/init_project.py`, **or** teach `G-1` in `scripts/validate_specs.py` that an empty computed stub may omit computed arrays. Then correct the `CHECKPOINT.md` row either way |
| **2** | **`init_project.py`'s dry-run plan mislabels `nurbs.json`** as *"stub (generated at build time by `build_nurbs.py`)"*. It is **hand-authored**; `build_nurbs.py` refuses to run without it | `build_nurbs.py` → `error: refusing to build: nurbs.json not found … nurbs.json is hand-authored at P4 — this stage reads it and emits the normalised spec plus the MAXScript, it does not compute the geometry.` **[re-measured]** | Fix the plan string and the `next` hint in `scripts/init_project.py`. My §4.0 recipe deletes only the **four** computed files for exactly this reason — someone following the dry-run text will delete `nurbs.json` and hit this |

### Preflight — two probes contradict measured facts

| # | Finding | Evidence | Needs |
|---|---|---|---|
| **3** | **`env_preflight.py`'s `sweep_on_shape` check will FAIL on this build.** It expects `addModifier (Rectangle()) (Sweep())` → `mods=1`, but `Sweep` is one of the six classes measured to **construct and then throw** on `addModifier` (`mods=0`) | P4b-r "6 unattachable modifiers" (`Extrude` `Sweep` `Lathe` `Surface` `CrossSection` `Bevel_Profile`), re-confirmed at the P6 ladder rung 1–2 | Either invert the expectation to `mods=0` with the reason, or move `Sweep` to the typed-tool route the note already documents. Until then the preflight cannot reach `PASS 9/9` |
| **4** | **`env_preflight.py`'s `loft_not_creatable` probe body calls `getCurrentException()` inside a `catch`** — which `CHECKPOINT.md` records as *throwing itself* and turning a catchable error into a script abort | The emitted body is `catch (out += "THROWS " + (getCurrentException()))`. `CHECKPOINT.md` §"MAXScript gotchas" and `agents/max-*.md` AP-21 both forbid it | Replace with a flag: `local threw = false` / `catch ( threw = true )`, then append `"THROWS"` without `getCurrentException()`. Until then this probe may abort instead of returning its expected string |

### Drift — documentation that contradicts the code it describes

| # | Finding | Evidence | Needs |
|---|---|---|---|
| **5** | **`AGENTS.md` §"Known packaging gap" is stale.** It says `install_skill.py` `collect_files()` ships **only** `SKILL.md`, `references/`, `snippets/` and calls the fix "a P10 item". It ships `references`, `snippets`, `scripts/*.py`, `agents/*.md`, `specs/*.json`, `examples/*.{json,ms,csv}` **and** `SKILL.md` `PLAN.md` `CHECKPOINT.md` `AGENTS.md`. `CHECKPOINT.md` §Artifacts already records the gap as **closed at P4b-r** | `scripts/install_skill.py:22-31` — `TOP_LEVEL_FILES` and `PACKAGE_DIRS` **[re-measured]** | Correct `AGENTS.md`. The stale line tells a reader the preflight is missing from an installed copy, which is no longer true |
| **6** | **`agents/max-facade.md` §7 step 3 still instructs `setCopyMode #instance` and `rotationZ rot_z_deg`** — both measured **absent** at P5, and `agents/max-assembly.md` §6.1 / AP-3 / AP-4 already correct both. `agents/max-components.md` §7 does not name them, but still lists *"Copy/instance mode producing a shared `baseObject`"* and *"Rotating a node after creation"* as **UNVERIFIED** — both are **verified** at P5 and P6 | `agents/max-facade.md:316` · `agents/max-components.md` §7 UNVERIFIED table | Correct `max-facade.md:316` to `n = copy src` + `n.baseObject = src.baseObject` and `n.rotation = quat rot_z_deg [0,0,1]`. Drop the two UNVERIFIED rows from `max-components.md` §7 and point at the P5 transcripts |
| **7** | **`agents/max-assembly.md` §4 step 5 says prototypes are "parked at a scratch offset outside the footprint"**. The emitted script creates **all 29 at `pos [0, 0, 0]`** | `examples/assembly.ms:877` onward — `local PROTO_CMP_001 = Box width:150.0 length:3.0 height:180.0 pos:[0.0,0.0,0.0]`, and the same for every prototype **[re-measured]** | Correct the playbook, **or** change the builder to emit a real scratch offset. Either is defensible; today the doc and the artefact disagree, and §5.2 documents the artefact |

### Ambiguity — needs the user's decision, not a fix

| # | Question | Why it is open |
|---|---|---|
| **8** | **Is the Chaos Scatter part of the delivered model?** `assembly.ms` emits **zero** scatter geometry (zero occurrences of `ChaosScatter` / `scatter` / `SCT_001` in 1979 lines **[re-measured]**), while `assembly.json.scatter[]` carries one row and `agents/max-assembly.md` §7 gate row 8 requires reading `FpInterface.getInstanceCount()` back — which implies a scatter object existed at the gate. `CHECKPOINT.md` §P6 records `objects.count == 244`, which does **not** include a scatter node | Two coherent readings: (a) S5 declares the scatter and the **user** applies it by hand from `snippets/chaos_scatter.ms`, in which case 244 is the correct delivered count; (b) the gate applied it and 244 was measured before, in which case the delivered count is 244 **+ 1 scatter node + N instances** and §5.1's table is wrong. **I did not guess.** §5.5 states the apply route and warns that the count changes |
| **9** | **`validate_specs.py --help` says it validates against `G-1..G-40`**, but the implementation runs **138 rows across `G-1`…`G-83`** | `scripts/validate_specs.py` `ArgumentParser` description, verified against the live run (`PASS 138 / FAIL 0 / WARN 0 / SKIP 15`) **[re-measured]** |

### Also confirmed still stale, lower priority

**One** `§8.2.7` citation in `references/07-spec-grammar.md` is still wrong. The *"trim projects and does
not cut"* claim lives in **`§8.2.8` row 8**, and the P6 fix landed in two places but not the third:

| Line | Cites | Correct |
|---|---|---|
| 1263, 2248 | `§8.2.8 row 8` | ✅ already fixed |
| **2072** (`G-54` row) | **`§8.2.7`** | ❌ still wrong |

**`references/14-chaos-scatter.md`**'s `G-74` row (`line 183`) still reads *"`node_name` unique across
`placements[]`, `opening_cuts[]` and `scatter[]`"* and omits **`wall_cells[]`** — which `G-74` in
`validate_specs.py` and `place_components.py` now covers. This is the **third** instance in this repo of a
rule failing to fire because the array it governs was added later.

---

## 9. The standing guard, restated

This repo has shipped **fabricated negatives**, not omissions. Every one cost a stage. The guard is one
sentence:

> **MAXScript execution is the only ground truth. An unexecuted claim is a hypothesis. An "unresolved"
> label is not a finding. Nothing may be recorded as blocked, impossible or non-existent without a
> transcript showing the attempt and the exact error.**

And four corollaries that each caught a real defect:

| Guard | What it caught |
|---|---|
| **An emitted `.ms` is not done until `fileIn` has run it and its output has been measured against the spec's intent** | P3's compile error; P4's 25 cm shell error inside a passing build; P4b's uncompilable `case` dispatch; P6's unpierced walls |
| **Structural self-checks are necessary and not sufficient** | Nine `G-`-rules passed at P4 while the output was wrong in the one place no rule covered |
| **A default value is a claim about behaviour and needs the same transcript as any other claim** | `NURBSBlendSurface` tension hardcoded `1.0/1.0` → `SUR_006` reached `y = 1518` against a 900 cm plan. `0.0` is correct. The defect was a fabrication wearing a default's clothes |
| **A convention's default is the value to use; a value merely inside its range is an invention** | P5's builder chose `panel_thickness_cm = 4.0`. `D-CL-05` declares **3**, range `2…8`, so `4.0` survived every range check. Caught by reading the value against `09-defaults.md` |

**The last one is the cheapest test in this repo and it is not a gate.** Open the generated file and look
at a number. That caught the P5 grid defect (a 180 cm window cut into a 180 × 170 panel and a **10 cm
ribbon of glass**) while **every offline gate was green** — exact partition, all openings covered,
`FAIL 0`, byte-deterministic. No linter can catch a specification that is wrong.