# 01 — Architecture AEC workflow: the stage map, S0 → S5

> **Current live-access policy (2026-11-04):** temporary no-Max/read-only/offline-only stops and
> the old orchestrator-only probe rule are superseded. Authorized agents may use Max when needed
> for assigned work; the orchestrator coordinates **one live operator at a time**, short calls and
> sequential writes. Preserve unrelated scene content; never reset/save it or manipulate dirty
> state, and clean up only proven-owned temporary fixtures. Fatal stack, `formattedPrint` and
> synthetic `nurbsID` safeguards remain. See `agents/max-orchestrator.md` §1.1. This policy changes
> no acceptance gate; a new architecture under test is not thereby built or accepted. Older
> historical scope/evidence below stays historical; current S7 routing is `agents/max-qa.md`.

> **CORRECTED (2026-10-06):** this map ran to S8. **S6, S7 and S8 were cancelled by explicit user
> decision on 2026-10-05** — not deferred. The live chain is **S0 → S5**, and S5 hands the model over
> for **manual** material assignment. See §3 "The cancelled stages" for what was dropped and what
> replaced it. Rows for S6/S7/S8 are retained below, marked cancelled, so a reader can see what changed.

> **Purpose:** this is the pipeline-level map. It answers four questions and nothing else: *where am I,
> what may I read, what must I produce, and when must I stop and escalate.*
>
> **It does not define a schema, a procedure, or a default.** Per-stage detail lives in
> `agents/max-*.md` — one file per stage, each the sole owner of its own procedure. Per-file schema
> lives in [`07-spec-grammar.md`](07-spec-grammar.md) and nowhere else. This file is the map above both.
>
> **Every claim about 3ds Max here is quoted from `CHECKPOINT.md` §"Verified facts"** with its
> provenance. Anything not in that table is marked **UNVERIFIED** until a live probe records it.
> This document needs no 3ds Max to read or use.

---

## 1. Scope, and two tool-naming rules that bind every stage

### 1.1 What each document owns

| Question | Owner |
|---|---|
| What shape is `massing.json`? | `07` §8.1 — and only `07` |
| What are the steps of my stage? | `agents/max-<stage>.md` — and only that file |
| What may I read, and who owns it? | This file, §2 and §3 |
| Which MCP tool do I call, and is the environment the same as last week? | `02-mcp-live-orchestration.md` §4, and `CHECKPOINT.md` §"Verified facts" |
| Which tool always fails? | §1.2 below, and `02` §3 |

If this file and `agents/*.md` disagree about a procedure, the agent file wins and this file is a
defect — report it in one line, never edit it from a worker (§7).

### 1.2 The sixteen tools that always fail — never call, at any stage

forestPack, forestLite, tyFlow, railClone and phoenixFD are **absent** from this installation, so every
`3dsmax-mcp_*` tool below throws unconditionally:

| Count | Tools |
|---|---|
| 1 | `3dsmax-mcp_scatter_forest_pack` |
| 14 | `3dsmax-mcp_create_tyflow`, `_create_tyflow_preset`, `_add_tyflow_event`, `_add_tyflow_collision`, `_connect_tyflow_events`, `_modify_tyflow_operator`, `_remove_tyflow_element`, `_get_tyflow_info`, `_get_tyflow_particles`, `_get_tyflow_particle_count`, `_reset_tyflow_simulation`, `_set_tyflow_physx`, `_set_tyflow_shape`, `_list_tyflow_operator_types` |
| 1 | `3dsmax-mcp_get_railclone_style_graph` |

**The tyFlow group is 14, not 13 — resolved in favour of the names.** `CHECKPOINT.md`, `02` §3.2 and
`AGENTS.md` record a tally of **13**, which was wrong: it did not match the toolset. The connected
toolset exposes exactly **14** `tyflow_*` tools, the 14 enumerated in the row above, and since tyFlow is
an absent plugin **all 14 throw** — not 13. Evidence: the enumeration itself, read off the live
connected toolset; there is no 14th name in dispute, only a miscount of a list that was already
complete. Count the names, not the tally. Substitutions, from `CHECKPOINT.md`: Chaos Scatter via
`3dsmax-mcp_execute_maxscript`; Max particles for animation; `3dsmax-mcp_clone_objects` in
`mode: "instance"` for modular patterning.

**A second set of names must also never be called**, for a different reason: the connected toolset
also exposes the **Rhino** server, whose `get_document_summary`, `get_objects`, `get_object_info`,
`create_object` (different schema), `capture_viewport` (different signature), `analyze_objects`,
`section_profile`, `boolean_*`, `measure_objects`, `intersect_curves`, `loft`, `pipe`, `sweep1`,
`extrude_curve` and every `gh_*` fail confusingly against Max. One such error does not mean the
bridge is down. Every tool name in this file is prefixed `3dsmax-mcp_` for that reason.

---

## 2. The spec chain

Eleven pipeline files live in `specs/pipeline/` and are the only channel between stages: **no stage
reads prose, and no stage reads another stage's transcript.** "Reads" below names the locked upstream
*files*; `origin_inputs` carries the paths inside them and `G-31` checks they resolve. Row 12 is the
`07` §4 outlier: not part of this chain.

> **CORRECTED (2026-10-06):** rows 9, 10 and 11 name stages that **were cancelled on 2026-10-05** and
> have **no owner and no builder**. The three agent files they named — `agents/max-materials.md`,
> `agents/max-qa.md`, `agents/max-export.md` — **do not exist and are not planned**; do not go looking
> for them. `materials.json`, `qa.json` and `export.json` exist only as **reserved stubs**: they are
> **not** pending deliverables, **not** a gate, and nothing reads or writes them.

| # | File | Owner stage | Reads | Writes | Status in `07` §4 |
|---|---|---|---|---|---|
| 1 | `dimensions.json` | **S1** (`agents/max-input.md`) | the brief, drawings, images | the dimensional contract | **defined** |
| 2 | `conflicts_resolved.json` | **S1** | the same input | every contradiction + the rule that decided it | **defined** |
| 3 | `assumptions.json` | **S1** | the same input | every invented value, with reason and confidence | **defined** |
| 4 | `massing.json` | **S2** (`agents/max-massing.md`) | 1–3 | Z-prism elements, storeys, grouping, layer column | **defined** (`07` §8.1) |
| 5 | `nurbs.json` | **S3** (`agents/max-nurbs.md`) | 4, and 1 | surfaces, sections, relations, approximation | reserved |
| 6 | `facade_grids.json` | **S4a** (`agents/max-facade.md`) | 1 (`facades`, `openings`, `levels`) | axes, panels, panel types | reserved |
| 7 | `components_registry.json` | **S4b** (`agents/max-components.md`) | 6, 1 | parametric blocks, families | reserved |
| 8 | `assembly.json` | **S5** (`agents/max-assembly.md`) | 6, 7, 4 | placements, opening cuts, **wall cells**, the `scatter[]` **declaration**, layer_map | reserved |
| 9 | ~~`materials.json`~~ | **S6 — CANCELLED 2026-10-05** | ~~8, 4~~ | ~~renderer choice, materials, UV rules~~ | **cancelled · reserved stub only** |
| 10 | ~~`qa.json`~~ | **S7 — CANCELLED 2026-10-05** | ~~every upstream file~~ | ~~checks, determinism record, captures, verdict~~ | **cancelled · reserved stub only** |
| 11 | ~~`export.json`~~ | **S8 — CANCELLED 2026-10-05** | ~~10~~ | ~~exports, tessellation, delivery manifest~~ | **cancelled · reserved stub only** |
| 12 | `recipes/*.json` | **S3** (P4) | `nurbs.json` | one recipe body each: `params`, `script` | reserved |

Two facts about this table are load-bearing. **Row 4 is the first stage that touches 3ds Max** — rows
1–3 are deliberately Max-independent (archival record: CHECKPOINT archive §P2), and `07` §12.5 needs a file, a schema
table **and** an example before a row flips to `defined`; `examples/massing.json` is P3's outstanding
deliverable, so row 4 is schema-defined but not yet example-proven. **Row 10 has no upstream sibling:**
S7 is the only stage that reads *all* of the others, which is why it is the only stage that may assert
anything about the whole model.

> **CORRECTED (2026-10-06):** the last two clauses of that paragraph described the **cancelled** S7.
> It is retained verbatim because the structural observation is still true of the row as written — but
> **no stage reads all upstream files any more.** The only stage that used to assert anything about the
> whole model was the one that no longer exists, so **nothing in the live pipeline asserts a whole-model
> verdict**, and no `verdict` field gates any build.

A file marked `reserved` has no example and no builder. S-4 in `07` is a promise about shape, not a licence to read one (`07` §12). Row 12 sits outside the chain, so only S3 reads or writes it. **A row marked `cancelled` is stronger than `reserved`: it is not a promise to be filled later, and a builder that reads or writes one of those stubs is a defect.**

---

## 3. The stage contracts

Every stage below has the same six rows: `07` §4 names the files, `agents/max-<stage>.md` names the
procedure, this file names the boundary. Where a stage's agent file does not exist yet that is stated
— **do not fill the gap from this file.** The last entry in this section is **not** a stage contract:
it is the cancellation record for the three stages that used to follow S5.

### S0 — dispatch and environment (`agents/max-orchestrator.md`, P10)

| | |
|---|---|
| **reads** | `AGENTS.md`, `PLAN.md` §5–§7, `CHECKPOINT.md`, the user's request |
| **gate** | `python scripts/env_preflight.py` **exits 0**. It is two-phase and cannot reach Max itself: run it bare to print the probe bodies, paste each into `3dsmax-mcp_execute_maxscript`, then score with `--results`. Bare invocation exits 0 with everything SKIP — **a non-run, not a pass** |
| **deliverables** | a routing decision per stage, a delegation brief with an explicit file list and a done-criterion, and the escalation list |
| **must refuse when** | preflight was not run, or did not exit 0; the bridge is unavailable (`PLAN.md` §6.1 blocks every bridge stage); a stage is about to start without a named file owner |
| **escalate to** | the user — a missing bridge is a stop, not a retry |
| **tools** | `3dsmax-mcp_get_bridge_status`, `3dsmax-mcp_get_plugin_capabilities`, `3dsmax-mcp_execute_maxscript` (to run preflight bodies only). Never §1.2 |

### S0b — live capability probe (`agents/max-env.md`, P0/P1 — the verified inventory)

| | |
|---|---|
| **reads** | `CHECKPOINT.md` §"Verified facts", `02` §1–§3, the preflight results file |
| **gate** | **every class-existence claim ships with its control result in the same batch.** A probe that reports `NURBSSet` as resolving while `TotalGarbageXYZ123` also resolves is a broken probe, not a finding |
| **deliverables** | a verified inventory written to disk, and a re-assertion that the five absent plugins are still absent so a future install cannot silently invalidate the routing table |
| **must refuse when** | a class is recorded as blocked, nonexistent or non-constructable **without a transcript showing the attempt and the exact error**. Two of this project's worst mistakes were fabricated negatives, not omissions (`CHECKPOINT.md` §Incident log) |
| **escalate to** | nobody — S0b *is* the escalation path for every later bridge stage |
| **tools** | `3dsmax-mcp_get_bridge_status`, `3dsmax-mcp_get_plugin_capabilities`, `3dsmax-mcp_execute_maxscript`, `3dsmax-mcp_get_scene_snapshot`. Never §1.2 |

### S1 — input (`agents/max-input.md`, P2 — **exists**)

| | |
|---|---|
| **reads** | the brief; `07`, `08`, `09`, `10` read-only; `examples/` read-only |
| **gate** | `python scripts/validate_specs.py --dir specs/pipeline` exits 0, **and** `status` is `locked` on all three files |
| **deliverables** | `dimensions.json`, `conflicts_resolved.json`, `assumptions.json`, `project.json` |
| **must refuse when** | a file would be locked while an escalation is open (§4); a value on `09`'s do-not-default list would be filled silently; a brief needs a `07` key that does not exist — `07` §12 is the extension path and it is not S1's |
| **escalate to** | the user, as a question list; `references/10-conflict-resolution.md` §6.1 owns the hard list `E1`–`E9` |
| **tools** | The spec gate needs no Max. Necessary source-model inspection/calibration may be assigned under `agents/max-orchestrator.md` §1.1; no blind bridge preamble |

### S2 — massing (`agents/max-massing.md`, P3 — being written in parallel)

| | |
|---|---|
| **reads** | `dimensions.json`, `assumptions.json`, `conflicts_resolved.json`; `07` §8.1 for the schema |
| **gate** | `build_spec.py --stage massing` exits 0 — which means the lock gate (§4) **and** `G-34`…`G-40` (§9.6) |
| **deliverables** | `massing.json` plus `examples/massing.json`; the builder's `massing.ms`. Layer is a **data column**, never builder output |
| **must refuse when** | an element is not a prism in Z — anything curved belongs to S3; an element's `origin` is not `derived` (`G-36`: S1 already resolved `given`/`assumed`/`conflict`); the builder is asked to assign a layer in MAXScript — six routes were executed and all threw, so this is not a bug to fix |
| **escalate to** | S1 for a dimension change (never hand-edit a locked file); the user for structural sizing (`E1`) or a plot/footprint question (`E4`) |
| **tools** | **None in the Python builder**, which *emits* MAXScript. An authorized S2 worker may run the live gate and necessary calibrated probes in the designated operator slot (§6) |

### S3 — NURBS (`agents/max-nurbs.md`, P4 — bugfix, not rewrite)

| | |
|---|---|
| **reads** | `massing.json`, `dimensions.json`, `references/nurbs-complete-guide.md` and `references/nurbs-architecture-recipes.md` **as unverified input**, `snippets/nurbs_arch_library.ms` (zero known bugs as of P1-b) |
| **gate** | `nurbs.json` locked, `G-31` `origin_inputs` resolve, and every recipe executed live at least once — with its control |
| **deliverables** | `nurbs.json`, the emitted recipe MAXScript, the NURBS nodes |
| **must refuse when** | `nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` would be rewritten on suspicion (`PLAN.md` §6.6: unverified is not disproven); a class is called non-constructable without a transcript; a script would run long enough to freeze the UI — one script per call, under ~2 s; test nodes would be left in the scene |
| **escalate to** | the orchestrator for live-operator scheduling, not exclusive execution; necessary probes may be delegated (§6) |
| **tools** | `3dsmax-mcp_execute_maxscript` — **mandatory**, NURBS has no typed path; `3dsmax-mcp_get_scene_snapshot`, `3dsmax-mcp_analyze_node_orientation`, `3dsmax-mcp_capture_viewport` for read-back; `3dsmax-mcp_delete_objects` in the same call as the probe. `3dsmax-mcp_introspect_class` / `_instance` are **hints, never proof**. Never §1.2 |

### S4a — facade grid (`agents/max-facade.md`, P5)

| | |
|---|---|
| **reads** | `dimensions.json` (`facades`, `openings`, `levels`) |
| **gate** | `facade_grids.json` locked; `bay_index` positions preserved verbatim — indices are positional and meaningful and must not be sorted or normalised |
| **deliverables** | `facade_grids.json`, `facade_table.csv`, `world_table.csv` |
| **must refuse when** | a facade is closed over a footprint vertex that does not exist; a panel would be placed on an elevation S1 never described and recorded — that is `E5`, an escalation, not a default |
| **escalate to** | the user for façade composition (`E5`); S1 for a bay or opening change |
| **tools** | **None in `facade_tables.py`**, which is deterministic Python. An authorized worker may run its consumer gate and necessary calibrated probes under §6 |

### S4b — component registry (`agents/max-components.md`, P5)

| | |
|---|---|
| **reads** | `facade_grids.json`, `dimensions.json` |
| **gate** | `components_registry.json` locked, with `parameters` as an ordered list so the generated parameter order is stable |
| **deliverables** | `components_registry.json` — parametric blocks only, no placements |
| **must refuse when** | a block would name a modifier, a plugin or an MCP tool. **A spec file may not name a class, tool, modifier or plugin** (`07` §12); the block is data, the recipe is not |
| **escalate to** | S4a for a panel type that has no component; the user if a family is interchangeable when it should be unique |
| **tools** | None in the registry builder. The shared prototype gate and necessary calibrated probes may be assigned to an authorized worker under §6 |

### S5 — assembly (`agents/max-assembly.md`, P6)

| | |
|---|---|
| **reads** | `facade_grids.json`, `components_registry.json`, `massing.json` |
| **gate** | `assembly.json` locked; `layer_map` resolves against `07` §8.1.4. **Layer assignment is not a gate and never will be** — see the correction below |
| **deliverables** | `assembly.json` + `assembly.ms`, placements with `instance_mode`, `wall_cells[]` tiling each `facade_wall` around its openings, and the `scatter[]` rows as a **declaration** carrying an explicit integer `seed` |
| **must refuse when** | a scatter **declaration** arrives without a seed — `seed` is 1…31337, it is `G-78`'s subject, and it is what makes the scatter reproducible when the user applies it by hand; a builder emits layer code, which is verified impossible; any tool in §1.2 is called |
| **escalate to** | S4a/S4b for a placement that has no component. **Layer application escalates to the user, permanently** — there is no orchestrator action to find |
| **tools** | `3dsmax-mcp_clone_objects` (`mode: "instance"`), `3dsmax-mcp_execute_maxscript` (to run the emitted `assembly.ms`), `3dsmax-mcp_transform_object`, `3dsmax-mcp_manage_layers` (`list` / `create` only), `3dsmax-mcp_get_scene_snapshot`, `3dsmax-mcp_get_instances`. Never §1.2 |

> **CORRECTED (2026-10-06) — three rows above were wrong, all three measured.**
>
> **1 · The layer gate is closed as a permanent negative, not an open item.** This row used to require
> that "the `manage_layers` object-assignment action name has been found by execution — it is still
> unknown." **It will never be found.** `node.layer` is read-only from MAXScript and **nine** routes
> are ruled out: six MAXScript calls (`node.layer` as string, as integer index, as a `LayerProperties`
> mixin, plus `LayerManager`'s `newLayerFromName` / `getLayerFromName` / `getLayer`, which exposes **no
> setter at all**), the `manage_layers` tool vocabulary — which is **exactly `{list, create, delete}`**,
> 40+ candidates rejected — and `set_object_property` with `property=layer`, which dies on the same
> read-only assignment (with a `property=pos` positive control succeeding in the same batch).
> **Layer assignment is a spec-time declaration and a human action in the Layer dialog** (`G-79`).
> See `agents/max-assembly.md` §6.3, the file that owns the wording.
>
> **2 · S5 emits no `ChaosScatter` geometry.** The deliverables row used to promise "`ChaosScatter`
> setups". `assembly.json` carries **one `scatter[]` declaration row** — note the key is `scatter`,
> **singular** — and `assembly.ms` contains **zero** occurrences of `ChaosScatter`, `scatter` or
> `SCT_001` **[measured 2026-10-06]**. **The user applies the scatter by hand**, from
> `snippets/chaos_scatter.ms`. S5's job is to make every reference in the declaration resolve; it does
> not build it and it does not measure it. There is **no `FpInterface.getInstanceCount()` gate**, and
> asserting one would be a check of something the stage deliberately never created.
>
> **3 · There is no Boolean cut path.** The tools row used to route "boolean cuts" through
> `3dsmax-mcp_execute_maxscript`. **The Boolean modifier cannot be made to cut anything in this build**
> (measured 2026-10-05): `Boolean()` throws, `BooleanMod()` carries Voxel Map's paramblock, and the
> bridge's own `add_modifier` attaches a Boolean **whose operand is never set** — it reports success and
> the geometry is unchanged. In the accepted production architecture **`closed_inner_contour_shell_v2`**,
> continuous perimeter poly walls are generated at stage **S4w** (`references/10-wall-generation-pipeline.md`)
> with openings excised before applying 1 outward `Shell` modifier, while S5 mounts frames via the opening
> manifest and deactivates host walls via Mechanism A (`host_node.isHidden = true`). In the preserved legacy route
> **`legacy_cells_v1`**, S5 emits zero modifiers and builds each `facade_wall` out of solid cells
> (`wall_cells[]`, `G-81`/`G-82`/`G-83`). See `agents/max-assembly.md` §6.2.1.

### The cancelled stages — S6 (materials) & S8 (export); S7 QA restored

> **Materials (S6 / P7) and Export (S8 / P9) remain CANCELLED by explicit user decision on 2026-10-05.**
> **S7 QA verification gate is active and restored** per locked decision `L-QA` (`scripts/qa_check.py`, `qa.json`).

The stage contracts for materials and export were removed on 2026-10-06 and replaced by this notice:

| Stage | Was | Status | What replaced it |
|---|---|---|---|
| **S6 (P7) · materials + UVs** | `materials.json` locked with a `renderer` field; `assign_material`, `create_material_from_textures`, `palette_laydown`, `set_sub_material` wired per geometry class; UV rules | **CANCELLED.** The user applies materials by hand. The deliverable is the verified model plus a hand-off | **The hand-off.** `agents/max-orchestrator.md` §5 owns it. `material_role` stays a **role**, never a material class (`07` §8.3.6) |
| **S7 (P8) · automated QA** | Automated verification gate | **RESTORED & ACTIVE** per `L-QA`. Evaluates coverage, census, analytical oracle form precision, watertightness (`openEdges == 0`), wall host hiding, modifier stack, replay idempotency | `scripts/qa_check.py` + `qa.json` (`agents/max-qa.md`) |
| **S8 (P9) · export** | `export.json`, FBX / OBJ / USD, the delivery MAXScript and its manifest | **CANCELLED.** No export format was ever specified | **Nothing.** The user saves and exports from Max |

**What did not change.** Two things named in the cancelled contracts are still live, and confusing the
two is the trap this notice exists to close:

| Still live | Where |
|---|---|
| **Measurement.** Every stage still `fileIn`s its emitted `.ms` and measures what came back (§"An emitted `.ms` is not done until it has been `fileIn`-ed and measured") | `agents/max-orchestrator.md`, and each stage's §7 |
| **Determinism of the *builders*.** The same locked specs must still produce byte-identical builder output (§5) | `01` §5, `07` S-5 |

**What is gone:** the whole-model `verdict`, the captures, the FBX/OBJ/USD path, and the `saveConfiguration`
→ `clear` → rebuild → `loadConfiguration` → compare-`getInstanceCount()` round trip as a *pipeline gate*.
The round trip survives only as an **optional manual check the user may run after applying the scatter by
hand** — `references/14-chaos-scatter.md` §5.1 and `MCPChaosScatter.determinismRoundTrip` in
`snippets/chaos_scatter.ms`. It is **not** a stage and it gates nothing.

**The file `materials.json` still exists as a scaffolded stub, and `qa.json` / `export.json` with it.**
They are placeholders in `specs/pipeline/`. **A stub is not planned work and is not a gate** — do not
report one as outstanding, and do not write one.

---

## 4. The build gate — one `status` check, and it is load-bearing

**A builder must refuse any spec file whose `status` is not `locked`, naming the file and the status
it found.** Exit non-zero. Nothing else is required of it.

| Aspect | Rule | Source |
|---|---|---|
| Permitted values | `draft` \| `locked` \| `superseded`. `G-4` makes a non-`locked` file an error for any build and a warning for a lint; `validate_specs.py --build` forces it | `07` §3.1, §9.1 |
| Who may relax it | nobody at build time. `--allow-draft` downgrades the failure to a SKIP and exists for linting, not for shipping | archival record: CHECKPOINT archive §P2 |
| What a builder prints | the file path and the status found — `massing.json: status=draft`, never a generic failure | `07` §3.1 |

**Why this one gate is enough.** Everything upstream of it is already decided: `G-9`…`G-15` prove
every value's provenance, `G-31` proves the chain resolves, and `G-32` proves no derived value was
hand-edited. A locked file is therefore not "probably fine" — every number in it came from the input,
from a recorded assumption, from a recorded conflict, or from a formula that recomputes. The one
remaining risk is a stage that locked a file it had not finished, and `status` is the flag for that:
an unanswered question in S1 keeps `dimensions.json` at `draft`, and every builder from S2 stops at
this gate naming that file. That is the whole mechanism.

---

## 5. Determinism

`07` S-5: **the same locked specs must produce byte-identical builder output.** Three things break it.

| Forbidden inside a spec file | Why it breaks the build |
|---|---|
| A timestamp other than `source.recorded_at`, or any value the builder defaults at run time | the output then depends on when it ran, not on the spec |
| A random or build-time-generated seed | `ChaosScatter` `seed` is an integer 1…31337 and is **data** in `assembly.json`; a generated seed makes the scatter unreproducible |
| A value that depends on dict or set iteration order | key order in JSON is not semantic, so two files differing only in key order would build differently |

Two consequences. **The determinism round trip is no longer a pipeline gate** — S7, which owned it, was
cancelled on 2026-10-05 (see §3 "The cancelled stages"). It survives only as an **optional manual check
the user may run after applying the scatter by hand**: `references/14-chaos-scatter.md` §5.1 and
`MCPChaosScatter.determinismRoundTrip` in `snippets/chaos_scatter.ms`. What the rule above still buys
is the one thing that was never in doubt — **byte-identical builder output from byte-identical specs**,
which is what §4's lock gate and `07` S-5 rest on.

**S5 must not "fix" a scatter that looks random** — that is a missing seed in the spec, an S5 defect
to report, not to patch in the scene. This still holds even though S5 builds no scatter: the *declaration*
carries the seed, and a hand-applied scatter that comes out differently than expected is a missing seed
in the declaration, not a reason to edit the scene.

---

## 6. Context budget — who may touch the live session (`PLAN.md` §5, `AGENTS.md`)

The current policy in `agents/max-orchestrator.md` §1.1 supersedes the former main-only wording
in `PLAN.md` §5 and historical handoffs; do not rewrite those records as if the old restriction
never existed.

| Rule | Detail |
|---|---|
| One designated live operator | **Authorized agents may operate Max when needed**, including necessary probes. The orchestrator assigns one operator at a time; other agents make no overlapping Max calls. Writes are sequential on Max's single UI thread; offline workers may continue in parallel |
| Probe vs recipe execution | A **probe** asks "does this work?"; a recipe execution builds specified geometry. Either may be delegated in the operator slot. Keep short bounded calls, known-positive/bogus controls and raw scripts/results; a worker's summary alone proves neither |
| Preserve the existing scene | Inspect current state and exact fixture ownership before writes. Do not delete/reset/save unrelated content, alter the user's Units Setup or manipulate the dirty flag. Cleanup only proven-owned temporary objects; uncertain identity or timeout means inspect/report, never a broad sweep |
| Retain measured safeguards | Do not re-run the fatal stack ladder, invoke `formattedPrint`, or fabricate `nurbsID` values. ≤5 modifiers per call and >10-stack approval boundaries remain; permission does not accept unverified architecture |
| Subagent returns | a short structured summary **plus written artifacts on disk** — never an inline dump. The cap is **12 lines**, as in `agents/max-input.md` §9. Without the cap, delegation relocates the bloat instead of removing it |
| File ownership, no cross-transcript reads | one file, one owner, exclusive; a worker that finds a defect elsewhere records it in one line and moves on. A subagent never reads another agent's transcript — verified facts arrive as a written brief, re-derived never |
| Verify the claims | subagent summaries are claims. The P1 batch reported "all 39 nonexistent tools removed"; an independent `grep` found 13 remaining occurrences. Check, do not read the report |

---

## 7. Handoff contract

A stage hands over **an artifact, not a message.** The next stage reads the file; it does not read you.

| # | What every stage must leave behind | Why |
|---|---|---|
| 1 | Its spec file, `status: "locked"`, or a `draft` with the open question named | this is the handoff |
| 2 | A validator transcript — the real exit code, not a paraphrase | "PASS 52 / FAIL 0 / WARN 0" without a run is a claim, not evidence |
| 3 | The builder's output files at their documented paths, and any `origin_inputs` list resolving under `G-31` | the next stage and the user both read them; the chain stays auditable forward |
| 4 | Escalations, in the return summary, each with the value that would be used and what it costs | a `draft` file plus a silent escalation is the failure mode this repo is guarding against |
| 5 | A **`CHECKPOINT.md` update at the end of every stage** | status board, verified facts, open bugs, incident log. Read before starting work so nothing settled is re-derived |

A stage that cannot complete says so in its summary; an empty field that hides a gap is worse.

**When a worker sees a problem in a file it does not own:** write against the **owning** file, record
the objection in one line naming the file, and move on. Do not edit it, and do not edit your own
output to agree with it. Two files disagreeing is a defect to report; one file edited to hide the
disagreement is a defect nobody can find.

---

## 8. The builder CLI contract — decided, do not vary it

`scripts/build_spec.py` is the **single dispatcher entry point** for every stage builder. Later
stages extend `--stage`; they do not add a second entry point.

```
python scripts/build_spec.py --stage massing --in <specs_dir> --out <out_dir> [--json]
```

| Behaviour | Contract |
|---|---|
| Reads | `<in>/dimensions.json` for `--stage massing` |
| Lock gate | refuses any spec file whose `status` is not `locked`; **non-zero exit naming the file and the status found** (§4) |
| Writes | `<out>/massing.json` and `<out>/massing.ms` |
| `--out` | defaults to `--in` |
| `massing.json` | follows `07` §8.1 exactly, and satisfies `G-34`…`G-40` |
| `massing.ms` | the MAXScript that builds the massing geometry. **Geometry only** — no layer code, which is verified impossible from MAXScript (`07` §8.1.3) |
| `--json` | machine-readable report on stdout |
| Determinism | byte-identical output for byte-identical input (§5) |

---

## 9. Where 3ds Max actually enters

The Python/spec stages are data contracts. Live Max supplies necessary source inspection,
calibrated capability probes, emitted-script execution and read-only S7 collection. Each is run
by the designated authorized operator under §6; the orchestrator retains scheduling and acceptance.

### 9.1 Verified by live execution (P3, 2026-10-04, with a control in the same batch)

| Fact | Consequence for this pipeline |
|---|---|
| **Scene units are centimetres, scale 1.0** — `units.SystemType` = `centimeters`, `units.SystemScale` = `1.0` | a spec value in cm reaches Max unchanged. No conversion at any boundary. This closes the previously UNVERIFIED row in `07` §11 |
| **`Box(width:, length:, height:, pos:)` is the deterministic placement primitive** — geometry is centred on `pos.x`/`pos.y` and its **base sits at `pos.z`**; `pos:` moves the geometry, not only the pivot | this is why every massing element is a Z-prism with a declared `z_range_cm`, and why the emitted `massing.ms` is trivial |
| **An object's layer cannot be assigned from MAXScript** — six routes executed, all throw `Property is read-only: layer`. Layer *creation* and layer *reading* do work | layer travels as **data**: `massing.json` carries the layer per element, `07` §8.1.4 closes the vocabulary, and `assembly.json` carries `layer_map`. **Application is the user's action in the Layer dialog — permanently** (see the S5 correction in §3) |

Verified elsewhere in `CHECKPOINT.md` and load-bearing for the stages above: `ChaosScatter()`
constructs while its base `CScatter` is NotCreatable; `appendObject` returns the string `"OK"`, not an
index; `fileIn` is the file-include function (`fileExists` does not exist); `stopCreating` takes zero
arguments; `delete <dummy>` does **not** delete its children.

### 9.2 UNVERIFIED — do not build on these without a probe first

| Claim | Status |
|---|---|
| Everything in `references/nurbs-complete-guide.md` and `references/nurbs-architecture-recipes.md` beyond the four P1-b corrections | **UNVERIFIED.** Substantially correct; verify claim-by-claim, do not rewrite on suspicion |
| Corona material **parameter** names beyond class existence | **UNVERIFIED** |
| ChaosScatter sub-object wiring beyond the `PLAN.md` §4.1 parameter map | **UNVERIFIED** |
| `references/13` shape/spline ids · `references/06` modifier params · `procedural-graphs.md` | **UNVERIFIED** |
| ~~Anything about `manage_layers` object assignment~~ | **CLOSED 2026-10-06 — this is no longer UNKNOWN, it is a permanent negative.** The action name will never be found: the vocabulary is **exactly `{list, create, delete}`**, and eight further routes (six MAXScript calls, `LayerManager`'s missing setter, `set_object_property`) are ruled out — **nine in total**, with a `property=pos` positive control. Layer **enumeration** from MAXScript is **UNAVAILABLE**; the typed tool is the only route, and it still cannot assign |

An "unresolved" label is not a finding. Nothing may be recorded as blocked, impossible or
non-constructable without a transcript showing the attempt and the exact error.
