# Development Plan — `3dsmax-arch-nurbs-ultimate-skill` (v3)

Architecture ported from `rhino-grasshopper-ultimate-skill` (S0→S7 staged pipeline, JSON spec
grammar, deterministic Python builders, one subagent per stage), adapted for **3ds Max 2026 / MAXScript**.

**v3 supersedes v2, which superseded v1.** v1 was written from documentation. v2 was written after
a P0 probe whose central conclusion turned out to be **wrong**. v3 is corrected and now records the
full evidence trail, including the false start, so the mistake is not repeated.

Progress is tracked in [`CHECKPOINT.md`](CHECKPOINT.md).

---

## 0. Verified environment baseline

| Property | Value | How verified |
|---|---|---|
| 3ds Max | 2026.3.2 (Security Fix) | `maxVersion()[8]` → `2026` |
| Transport | `namedpipe`, protocol 2 | `get_bridge_status` |
| Threading | `mainThread`, `safeMode: true` | `get_bridge_status` |
| Installed | Corona, Chaos, Arnold, PhysX, FbxMaxWrapper, USD | `get_plugin_capabilities` + class scans |
| **Absent** | forestPack, forestLite, tyFlow, railClone, phoenixFD | `get_plugin_capabilities` |

Preflight `scripts/env_preflight.py`: **PASS 9 / FAIL 0** against live data, with verified
fault discrimination (injected faults are caught and named; the `nurbset_present` check was
confirmed to invert correctly).

The TCP listener on `127.0.0.1:8765` is **not used and not required**. Instance-pipe discovery is
automatic and survived an OS reboot mid-session.

### 0.1 User's declared stack — a hard requirement

The user produces in **Corona** and uses **Chaos Scatter**. Both confirmed available and both are
promoted to first-class:

- **Corona** must be the default material target (P7). `get_plugin_capabilities` reported the
  active engine as `Arnold` at verification time, so the skill must **detect and set** the renderer
  per project rather than assume it.
- **ChaosScatter** is the **only** working scatter route, since ForestPack is absent (P6).

---

## 1. The NURBS API is real — v2's re-scoping was wrong

### 1.1 What v2 got wrong and why

v2 claimed the 34 KB `references/nurbs-complete-guide.md` was "fiction" and that P4 needed a
rewrite from scratch. **That was false.** The guide is substantially correct and the library works.

The error came from three compounding mistakes:

1. **`introspect_class "NURBSSet"` returned `Class not found`** and was believed — even though the
   skill's own rule says introspection is a hint, never proof.
2. **The P0 preflight probe tested the wrong thing.** It used `get #NURBSSet`, which returns
   `undefined` even for existing classes, and then guarded `NURBSSet()` behind
   `if id != undefined` — so the construction test **never executed** and the check passed vacuously.
3. **`discover_plugin_classes superclass=NURBS` returned 0** because the superclass name was wrong.

A control group (`TotalGarbageXYZ123` → `undefined`, `NURBSSet` → resolves) proved all 27
identifiers genuine. **Lesson recorded permanently: never test class existence without a
known-bogus control in the same batch.**

### 1.2 Verified NURBS capability (executed live)

Every identifier used by `snippets/nurbs_arch_library.ms` resolves, and all construct:

```
NURBSSet, NURBSCVCurve, NURBSPointCurve, NURBSPointSurface, NURBSCVSurface,
NURBSULoftSurface, NURBSUVLoftSurface, NURBS1RailSweepSurface, NURBS2RailSweepSurface,
NURBSBlendSurface, NURBSOffsetSurface, NURBSProjectVectorCurve,
NURBSDisplay, NURBSSurfaceApproximation        -> all CREATED
```

The relational architecture works end-to-end. Executed proof:

```
nset = NURBSSet(); appendObject nset <curve>; appendCurve us <idx>
node = NURBSNode nset name:"TestShell"        -> class NURBSSurf
getNURBSSet node #relational                   -> NURBSSet, numObjects = 11
superClassOf sub-objects                       -> NURBSSurface / NURBSCurve / NURBSPoint
evalPos surf 0.5 0.5                           -> [0.347105,-0.343283,0.130161]
evalUTangent surf 0.5 0.5                      -> [0.698954,-0.683764,0.000429974]
```

`snippets/nurbs_arch_library.ms` loads cleanly and prints `MCP_NURBS_Arch loaded`.
`makeCVCurve` and `makePointCurve` both return valid objects.

Also corrected: `Point_Surf` and `CV_Surf` **do** have MAXScript identifiers; a `NURBSNode`
reports `classOf` as `NURBSSurf` and appears in the UI as "CV Surf".

### 1.3 The three real bugs in `nurbs_arch_library.ms`

> **STATUS: closed in P1-b (2026-10-04).** All three below are fixed, a **fourth** bug was found and
> fixed alongside them (`close <crv>` is a silent no-op, so `closed:true` produced open geometry), and
> every one of the ten library functions was executed live. Bug 3's premise turned out to be **false**
> — `NURBSControlVertex` constructs; `setCV` merely requires a wrapper. The table below is kept as the
> original record. Current state and evidence: [`CHECKPOINT.md`](CHECKPOINT.md) and
> `references/12-nurbs-gotchas.md` §2.

These are genuine defects, found by executing the library. They were the entire planned code scope of
P4.

| # | Bug | Symptom | Fix |
|---|---|---|---|
| 1 | `appendObject` returns the **string `"OK"`**, not an index. The library does `append crvIndices (appendObject nset pc)`, then `appendCurve uLoft idx` | `Unable to convert: OK to type: Integer` | After `appendObject nset obj`, take the index as `nset.numObjects` |
| 2 | `stopCreating` takes **zero** arguments; the library calls `stopCreating node` (5 call sites) | `Argument count error: StopCreating wanted 0, got 1` | Drop the argument |
| 3 | `NURBSControlVertex` does not construct | silent failure in `makeCVCurve`'s `setCV` path | Determine the correct CV construction route; `makeCVCurve` currently succeeds so this needs isolating |

Verified workaround for bug 1 — the corrected pattern:

```maxscript
nset = NURBSSet()
idxs = #()
for i = 1 to sectionPointsList.count do (
    local pc = MCP_NURBS_Arch.makePointCurve sectionPointsList[i] name:("Sec" + (i as string)) closed:true
    appendObject nset pc
    append idxs nset.numObjects      -- NOT appendObject's return value
)
```

Note also a MAXScript precedence trap present in the library:
`name:("Section_" + i as string)` throws `Incompatible types: 1, and ": "`.
Write `name:("Section_" + (i as string))`.

### 1.4 Real MAXScript gotchas (verified)

| Trap | Detail |
|---|---|
| `fileExists` **does not exist** | Use `doesFileExist`. `executeFile` and `runScript` also do not exist — use **`fileIn`**. |
| `stopCreating` arity | Takes 0 arguments. |
| `modifiers <node>` function form | Does not work; use the `node.modifiers` **property**. |
| Standalone modifiers | `Sweep()` returns a non-node; `delete` on it fails. Attach to a node, delete the node. |
| `introspect_class` paramBlocks | Lies for shapes — reported `Rectangle` as having no params, but `width`/`length` exist (default 25.0). |
| `maxVersion()` | Returns an array; major version is index 8. `get3dsMaxVersion()` does not exist. |
| Material identifiers | InternalNames, not display names: `OpenPBR` (not `OpenPBRMaterial`). |
| `Loft` | Class resolves but `Loft()` is `Not creatable`. Use `NURBSULoftSurface` — the real path was there all along. |

### 1.5 Standing rule on truth

**MAXScript execution is the only ground truth.** `introspect_class` returned "Class not found" for
a class that demonstrably exists; `inspect_plugin_constructor` returns `inferred: true` guesses;
the DLL class scan is incomplete (78 of 160 modifiers) and disagrees with MAXScript. Always pair a
class-existence claim with a known-bogus control.

---

## 2. Fifteen MCP tools that always fail

Because forestPack / forestLite / tyFlow / railClone / phoenixFD are absent, these tools throw
unconditionally and must never be called: `scatter_forest_pack`, all **14** `tyflow_*` tools,
`get_railclone_style_graph`. Substitution table: `references/02-mcp-live-orchestration.md`.

Material classes available: `OpenPBR`, `PhysicalMaterial`, `Standard`, plus 16 Corona classes.
No Arnold-specific, VRay, Octane, or `RS_Standard_Material` classes.

**Two more tool families are absent, confirmed by direct inspection of the live connected tool
list at P4b-r (2026-10-04):** there is **no `mcg_*` tool** (so Max Creation Graph cannot be
driven from this bridge at all — `references/procedural-graphs.md` is moot) and **no
`curve_model`** (`references/curve-construction.md` is written against it and needs a rewrite,
not a fix). `references/arch-modifiers-and-procedural-reference.md` §3 was retracted for
recommending both.

---

## 3. Target layout

```
3dsmax-arch-nurbs-ultimate-skill/
├── SKILL.md                       # thin orchestrator: routing + stage table only
├── AGENTS.md                      # agent registry / sync map
├── PLAN.md                        # this file
├── CHECKPOINT.md                  # ★ progress tracker (source of truth for status)
├── agents/
│   ├── max-orchestrator.md        # S0 dispatch, stage sequencing, context budget
│   ├── max-env.md                 # S0b live capability probe → verified inventory
│   ├── max-input.md               # S1 drawings/images → dimensions/conflicts/assumptions
│   ├── max-massing.md             # S2 site pad, slabs, columns, core
│   ├── max-nurbs.md               # S3 NURBS sets, lofts, sweeps, blends, trims, panelization
│   ├── max-facade.md              # S4a facade grids, axes, floors, panelization
│   ├── max-components.md          # S4b component registry (parametric blocks)
│   ├── max-assembly.md            # S5 place instances, cut openings, Chaos Scatter
│   ├── max-materials.md           # S6 Corona PBR materials, UVs, glass
│   ├── max-qa.md                  # S7 deterministic QA + visual verification loop
│   └── max-export.md              # S8 FBX/OBJ/USD export + delivery MAXScript
├── references/
│   ├── 01-architecture-aec-workflow.md      # stage contracts, spec flow
│   ├── 02-mcp-live-orchestration.md         # ✅ VERIFIED tool inventory + routing (P0)
│   ├── 03-maxscript-in-3dsmax-rules.md      # escaping, dialogs, undo, coordsys, gotchas
│   ├── nurbs-complete-guide.md              # ⚠ EXISTS, substantially correct — VERIFY, do not rewrite
│                                           #   ⚠ no numeric prefix in the real filename
│   ├── nurbs-architecture-recipes.md        # ⚠ VERIFY every recipe against live Max
│   ├── 06-arch-modifiers.md                 # verified modifier classes/params
│                                           #   ⚠ REAL FILE: arch-modifiers-and-procedural-reference.md
│   ├── 07-spec-grammar.md                   # ★ JSON schema for all spec files
│   ├── 08-input-rules.md                    # ★ drawings/images → dimensions
│   ├── 09-defaults.md                       # ★ architectural default values
│   ├── 10-conflict-resolution.md            # ★ precedence + conflict log
│   ├── 11-layer-standard.md                 # naming/layer/hygiene rules
│   ├── 12-nurbs-gotchas.md                  # ⚠ NEEDS CORRECTION (P0 headline was wrong)
│   ├── 13-curve-spline-shapes.md            # shape/spline construction
│                                           #   ⚠ REAL FILE: maxscript-splines-shapes.md
│   ├── 14-chaos-scatter.md                  # ★ replaces railclone.md
│   ├── 15-procedural-graphs.md
│   ├── 16-corona-materials.md               # ★ Corona material matrix
│   ├── 17-export-formats.md
│   ├── improvement-log.md                # ✅ P11 — per-project log format spec
│   └── maxscript-*.md                       # reused generic refs (deduped in P1)
├── snippets/
│   ├── nurbs_arch_library.ms                # ★ WORKS — fix the 3 bugs (P1-b/P4)
│   ├── chaos_scatter.ms                     # ★ verified ChaosScatter wiring
│   └── max_*.ms
├── scripts/
│   ├── env_preflight.py       # ✅ DONE (P0, corrected in P1)
│   ├── init_project.py        # scaffold workdir + specs/
│   ├── validate_specs.py      # schema + range + cross-file validation
│   ├── build_spec.py          # dispatch stage builders
│   ├── build_nurbs.py         # emit MAXScript from NURBS specs
│   ├── facade_tables.py       # facade_grids.json → facade_table.csv / world_table.csv
│   ├── place_components.py    # placement + opening cuts + scatter wiring
│   ├── ~~qa_check.py~~        # ⛔ P8 cancelled 2026-10-05 — never written
│   ├── ~~capture_views.py~~   # ⛔ P8 cancelled 2026-10-05 — never written
│   ├── ~~export_max.py~~      # ⛔ P9 cancelled 2026-10-05 — never written
│   ├── ~~lint_script.py~~     # ⛔ never written
│   └── ~~check_skill_md.py~~  # ⛔ never written — dangling refs tracked in CHECKPOINT.md
├── specs/{pipeline,recipes}/*.json
└── examples/                  # worked example: one small building
```

---

## 4. Execution plan — one subagent per item

Sequential where artifacts are consumed downstream. 🔌 = requires the live Max bridge.

| # | Item | Subagent | Deliverables | Depends on |
|---|---|---|---|---|
| **P0** | ✅ Environment baseline + verified inventory | `general` | `02`, `12`, `env_preflight.py` — **done, NURBS conclusion since corrected** | — |
| **P1** | 🔍 Audit & salvage | `general` | **NURBS API verified real**; 3 library bugs catalogued; `env_preflight.py` `nurbset_present` fix ✅; **remaining**: decision-matrix correction, dedupe vs `3dsmax-mcp-dev`, `curve-construction.md` rewrite list | P0 |
| **P2** | ★ Spec grammar + input stage (S1) — ✅ **done** | `general` | `07`, `08`, `09`, `10`, `agents/max-input.md`, `examples/{dimensions,conflicts_resolved,assumptions}.json`, `scripts/{init_project,validate_specs}.py` | P1 |
| **P3** | Layer standard + massing (S2) — ✅ **done** | `general` | `11`, `01`, `agents/max-massing.md`, `examples/{massing.json,massing.ms}`, `scripts/build_spec.py`; `07` §8.1 defines `massing.json`, §9.6 adds `G-34`…`G-40`. Emitted `.ms` executed live: 18/18 bboxes within 0.5 cm | P2 |
| **P4** | ★ NURBS core — ✅ **done** (bugfix, not rewrite; library work closed in P1-b) | `general` | ✅ live verification of the P1-b "left unverified" list — all three resolved, one of them a **verified negative** (`closeU`/`closeV` do not exist); ✅ `nurbs.json` defined in `07` §8.2 **re-derived against the library**, `G-41`…`G-49` in §9.7; ✅ `scripts/build_nurbs.py`, `examples/{nurbs.json,nurbs.ms}` — **executed live, 6 nodes, idempotent**; ✅ `agents/max-nurbs.md`, `specs/recipes/nurbs/*.json`; ✅ library grew to 12 functions, all executed live. **Remaining → P4b:** `references/13`, `references/06`, rail-sweep/blend/trim discovery | P3 |
| **P4b** | NURBS remainder — ✅ **done** | `general` | ✅ **control-tested discovery of the rail-sweep / blend / trim API — DONE 2026-10-04, and it overturned P4's "not implemented" finding: all four relation classes construct, commit and evaluate.** `references/07` §8.2.6, `12-nurbs-gotchas.md`, `agents/max-nurbs.md` §6.7 corrected. ✅ **round 2:** both live defects found and fixed (tension default `1.0`→`0.0`; relation parents referenced by `parent1ID:` instead of re-instantiated). ✅ **round 2 — the reference pass:** `maxscript-splines-shapes.md` and `arch-modifiers-and-procedural-reference.md` (the real names behind `13`/`06`) executed claim-by-claim against live Max and corrected — the first largely vindicated, the second substantially wrong; `install_skill.py` packaging gap closed; `maxscript-*.md` deduped; tyFlow tally 13→14 | P4 |
| **P4b-r** | ✅ Reference claim-by-claim pass — **done 2026-10-04** | `general` | `references/_p4b-remainder-evidence.md` (transcripts) · `maxscript-splines-shapes.md` corrected (10 fixes; `bezierShape()` unusable; `pathParam` inert; multi-spline `updateShape` trap) · `arch-modifiers-and-procedural-reference.md` corrected (3 class names; 6 modifiers need `3dsmax-mcp_add_modifier`; ~13 parameter names do not exist; Data Channel vocabulary rebuilt on the real 32 snake_case operators; §3 retracted — no `mcg_*`, no `curve_model`) · `install_skill.py` `collect_files()` closed | P4b |
| **P5** | Facade grid + component registry (S4) — ✅ **done** | `general` | ✅ `07` §8.3/§8.4 **define** `facade_grids.json` + `components_registry.json`, §9.8 adds `G-57`…`G-70`; ✅ `scripts/facade_tables.py`; ✅ `examples/{facade_grids,components_registry}.json` + `{facade_table,world_table}.csv`; ✅ `agents/max-facade.md`, `agents/max-components.md`; ✅ `assumptions.json` gains `A-023`/`A-024`. **Gate: the tables were placed in live Max and counted** — 136 rows read by MAXScript, 136 reference instances, `objects.count` 165, five bboxes exact. 136 panels · 140 axes · 29 components. **The stage's own design contract is `references/_p5-contract.md` (revision 2).** Found and fixed: a shared facade-wide v grid produced a 180 × 10 cm glass sliver; `panel_thickness_cm` was an in-range invention; the ledger could not describe an `assumed` value outside `dimensions.json` | P4b-r |
| **P6** | ★ Assembly + Chaos Scatter (S5) | `general` | `agents/max-assembly.md`, `scripts/place_components.py`, opening-cut recipes, `snippets/chaos_scatter.ms`, `references/14-chaos-scatter.md`. **Both inherited facts are now measured:** the instance route is `copy` + `baseObject =` (`setCopyMode` is absent), a Z rotation is `quat <deg> [0,0,1]` (`rotationZ`/`matrix3`/`angle` are absent), and `node.pos` on a `Box` puts the **base** at `pos.z`. **The `manage_layers` open item is CLOSED as a verified negative** — no object-assignment action exists, so `layer_map` stays data permanently. **The Chaos Scatter hazard is CLOSED by measurement** — the 1/2/5/10 ladder is clean, 20 freezes Max permanently | P5 |
| **P7** | ~~★ Corona materials + UVs (S6)~~ ⛔ **CANCELLED by the user 2026-10-05 — not pending, not blocked** | — | **Do not start this stage.** Materials are made by hand. What survives is already written up in `CHECKPOINT.md` §"P7 — what the cancelled probes proved" and `references/_p7-evidence.md`: the **renderer set route** (which closed P0) and the Corona class census. The one genuinely missing piece is **UV rules for NURBS surfaces vs poly-modified geometry** — start there if a hand-materialed model ever needs unwrapping. **Note this row supersedes §4.2's "record the renderer choice in the spec so QA can assert it"**, which assumed a QA stage that no longer exists | — |
| **P8** | ~~QA loop (S7)~~ ⛔ **CANCELLED with P7, 2026-10-05** | — | **Do not start this stage.** `agents/max-qa.md`, `scripts/qa_check.py` and `scripts/capture_views.py` **do not exist and are not planned.** Any text implying a QA loop is now wrong — including §4.1's "determinism hook for P8 QA", which survives only as the `FpInterface` observation and is deferred to a stage that may never exist | — |
| **P9** | ~~Export (S8)~~ ⛔ **CANCELLED with P7, 2026-10-05** | — | **Do not start this stage.** `references/17-export-formats.md`, `scripts/export_max.py`, `agents/max-export.md` **do not exist and are not planned** | — |
| **P10** | Orchestrator, SKILL.md rewrite, install, end-to-end test — ✅ **delivered as P10-lite** | `general` | ✅ `SKILL.md`, `AGENTS.md`, `agents/max-orchestrator.md`, `install_skill.py`, 🔌 **full run measured 2026-10-05: input → massing → NURBS → facade → assembly, 254 nodes, 3-run idempotent, 0 modifiers, scene back to 0.** The P7→P9 leg of the original chain is **cancelled**, so the run ends at a Corona-ready model with a hand-materialing hand-off rather than a Corona render. ~~`scripts/{lint_script,check_skill_md}.py`~~ — **never written; P8/P9 were cancelled first and the names are not planned** | P6 |
| **P11** | Improvement log + close-out pass — ✅ **done 2026-10-06** | `general` | ✅ `references/improvement-log.md` (the **format spec**), `agents/max-orchestrator.md` §6.2 (the **trigger and ownership rule**), pointers into all six `agents/max-*.md` playbooks and a row in `SKILL.md` · ✅ `G-74` lint-side gap found and fixed (the linter never covered `wall_cells[]`; proved by fault injection) · ✅ `curve-construction.md` marked **OBSOLETE** with a router, `architecture-exterior-pipelines.md` corrected in place, tool-routing prose fixed in the two NURBS files **with their geometry untouched** · ✅ three stale rows and one stale `AGENTS.md` section corrected · ✅ two self-defeating `env_preflight.py` probes restructured. **No live bridge was available — nothing here is new evidence about Max.** Remaining open items and their reasons: `CHECKPOINT.md` §"Close-out pass, 2026-10-06" | P10 |

★ = direct answer to the user's stated priorities. 🔌 = requires the live bridge.

### 4.1 Chaos Scatter — verified parameter map (feeds P6)

`ChaosScatter()` constructs, superclass `geometry`, classID `[1672609897, 845042209]`.
`CScatter` is its base and is **NotCreatable** — always use `ChaosScatter`.

Core wiring: `targetNodes` (node[] surfaces) + `modelNodes` (node[] source) +
`modelFrequencies` (float[] per-model probability). Verification uses `instanceCountLimit`,
`distributionDesityPattern` (the typo is the real name), `distributionLimitCoordSpace`,
`seed` (1..31337, **deterministic**).

Placement: `translationFrom/To`, `rotationFrom/To`, `scaleFrom/To`, `scaleUniform`,
`rotationNormalAlignment`, `rotationLookAt*`.

Constraints: `collisionAvoid` + `collisionStrictness` + `collisionAvoidancePriority`,
`altitudeLimitationEnabled/From/To` + falloff curves, `surfaceSlopeLimitEnabled`,
`edgeTrimmingEnabled`, `densityMap`, `surfaceUv*`.

**Determinism hook.** `FpInterface` exposes `getInstanceCount()`, `getModelCount()`,
`getModelNode(i)`, `update()`, `clear()`, `addModelNode(node)`, and
**`saveConfiguration(filePath)` / `loadConfiguration(filePath)`**. Saving the scatter config and
asserting identical instance counts across a rebuild is the obvious way to replace the nonexistent
QA tools — **and that QA stage was cancelled on 2026-10-05.** The observation stands on its own; the
consumer does not exist yet. ⚠️ Note also the **2026-10-06 decision**: the scatter is **declared, not
geometry** (`assembly.ms` emits zero scatter nodes; the user applies it by hand from
`snippets/chaos_scatter.ms`), so `getInstanceCount()` has nothing to read back on the delivered
chain. `agents/max-assembly.md` §5 step 9 and §7 rows 8 and 17 still describe the applied reading —
that inconsistency is **open**, not resolved.

### 4.2 Renderer handling

Active engine reported as `Arnold` while the user's production renderer is Corona. The skill must
detect the engine, set Corona when Corona rendering is requested, and record the choice in
`CHECKPOINT.md`'s verified-facts table so it is not re-derived. Never hardcode an assumption.
**Superseded 2026-10-05:** the "so QA can assert it" clause named a stage that is cancelled; and the
measured result is better than an assertion would have been — **`renderers.production = Corona()`
works, `renderers.current = Corona` throws**, and the two slots are independent. Instantiate, do not
assign the class. `Corona()` costs ~3.5 s cold and needs its own tool call.

---

## 5. Context budget strategy

- Main thread only: planning, gate decisions, user interaction, final verification.
- Every execution item is delegated to a `general` subagent with an explicit file list, a
  done-criterion, and "do not read other agents' transcripts".
- Subagents read/write only the files they own.
- Results returned as short structured summaries + written artifacts, never inline dumps.
- **Only the orchestrator performs live Max probes.** Verified facts are handed to subagents as
  data. This keeps Max — single-threaded and hang-prone — under controlled access and stops probe
  results from being hallucinated second-hand. This rule is what produced the v2 error: a
  conclusion was carried forward without re-verification.
- **Every class-existence claim ships with its control result.**

---

## 6. Risks and gates

1. 🔌 Bridge unavailable → all 🔌 items blocked. *Gate: `env_preflight.py` before each 🔌 stage.*
2. **Carried-over false conclusion (RESOLVED, guard added).** v2's "NURBS is fiction" was wrong.
   Guard: control-tested class claims only; `env_preflight.py` asserts `nurbset_present`.
3. End-to-end test fails on geometry, not tooling → report, do not paper over.
4. Max hangs during a long 🔌 probe → keep probes under ~2 s, one script per call, always delete
   test nodes (a bare modifier cannot be deleted; attach it to a node and delete that).
5. Plugin assumption creep → preflight asserts the five absent plugins every run, so a future
   install cannot silently invalidate the routing table.
6. **Do not rewrite `nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` on suspicion.** They are
   unverified, not disproven. Verify each claim
   by execution, then correct only what fails. **Proven twice over:** at P4b their keyword claims
   were vindicated after three other files had claimed the capability was missing, and at P4b-r
   the same discipline produced the opposite verdict on `arch-modifiers-and-procedural-reference.md`
   — which really was substantially wrong. The rule is not "assume the docs are right" or "assume
   they are wrong". It is **measure, then correct only what fails**.
7. 🔌 **A heavy scripted modifier stack permanently freezes Max** (P6, 2026-10-05: the bounded ladder
   was run deliberately and **rung 20 hung the main thread so hard that Max had to be killed and the
   machine rebooted**. 5 and 10 are clean; the break is between 10 and 20 and must **not** be re-measured).
   Standing rule: **≤ 5 modifiers per `execute_maxscript` call, > 10 on one node forbidden without
   asking the user.** A timeout is the only symptom — never report it as "the bridge is down" without
   a cheap `get_bridge_status` first. Note the P4b-r hedge is retired: the hang reproduces with **no
   ChaosScatter object in the scene**, so the trigger is the stack change itself.

---

## 7. Done criteria

Retrospective, not prospective: P7/P8/P9 were **cancelled** (2026-10-05), so criteria 5 and 6 can no
longer be met and are marked as retired rather than silently left to fail.

1. ✅ `env_preflight.py` **runs** and exits 0. *Partly retired:* it is two-phase by design — the
   bare run prints the probe bodies and reports every check **SKIP**, which is correct behaviour and
   **is not a pass**. Reaching a full `PASS` needs captured results in a second call against a live
   bridge. Note that `sweep_on_shape` previously asserted `mods=1 first=Sweep` and therefore **could
   never pass on a healthy machine** — `Sweep` is one of the six classes that construct and then
   throw on `addModifier` in this build. The probe now asserts that measured behaviour, so a full
   pass is reachable.
2. ✅ **Every tool named in `SKILL.md` exists and was executed at least once** — the P4b-r / close-out
   passes removed the rest rather than leaving the criterion aspirational. A name may still appear in
   a reference file as a **warning** that it is absent; that is correct, not a violation.
3. ⛔ **NOT MET, and now unmeetable as written.** Every NURBS recipe in `nurbs-complete-guide.md` /
   `nurbs-architecture-recipes.md` built in live Max.
   Their **keyword claims were vindicated at P4b** and their tool-routing prose was corrected on
   2026-10-06 — but a full claim-by-claim pass was never run, because the close-out session had no
   `3dsmax-mcp_*` tool. This stays open rather than being marked done on a vindication.
4. ✅ `snippets/nurbs_arch_library.ms` has zero known bugs, proven by executing every function.
5. ⛔ **RETIRED 2026-10-05** — the run ends at a Corona-ready model with a hand-materialing
   hand-off, so "through a Corona render with a passing QA report" no longer describes the
   deliverable. The substitute that *was* measured is the P10-lite chain: **254 nodes**, 3-run
   idempotent, **0 modifiers**, 52/52 cell bboxes exact, per-host volume error **0.000000 cm³**,
   scene back to **0**.
6. ⛔ **RETIRED 2026-10-05** — `check_skill_md.py` was never written and is not planned. Dangling
   references are instead tracked as `CHECKPOINT.md` §"Dangling references still routing to bogus
   tools internally", and were resolved by correction, not by a script.
7. ✅ **The delivered artefact is executed, not merely emitted.** Every `.ms` was `fileIn`-ed and
   counted in live Max, and every CSV was placed and counted — an emitted file that nobody ran is
   not a deliverable, and a builder that self-checks its own output proves nothing about whether
   Max will load it.