# Close-out evidence brief — 2026-10-06

**Read this before editing anything. Do not re-derive these facts and do not re-probe anything.**
Every row here was measured against live 3ds Max 2026.3.2, or is a direct reading of a checked-in
file. The transcripts are in `CHECKPOINT.md` §"Verified facts" and
`references/_p4b-remainder-evidence.md` / `references/_p7-evidence.md`.

**No `3dsmax-mcp_*` tool is available in the session that produced this brief.** Nothing below may be
extended by a new claim about Max's behaviour. If a task needs a fact that is not in this file, the
correct output is to record it as UNVERIFIED and leave it — not to infer it.

---

## 1. Tools that do not exist (verified by direct inspection of the live tool list, P4b-r)

| Name | Status | What to use instead |
|---|---|---|
| `curve_model` | **absent** | `references/maxscript-splines-shapes.md` + MAXScript `splineShape` / `updateShape` |
| `inspect_curve`, `edit_curve` | **absent** | read/modify the node's spline via MAXScript |
| `draw_spline` | **absent** | `splineShape` / `Line` / `Rectangle` constructors |
| `loft_mesh` | **absent** | `NURBSULoftSurface` (the NURBS route) or poly-modifier stack |
| `geometry_qa`, `contact_check`, `scene_qa` | **absent** | `execute_maxscript` reading `node.min` / `node.max` / `objects.count`; `FpInterface` for scatter |
| `agent_viewport` | **absent** | the bridge's own viewport/snapshot tools |
| the whole `mcg_*` family | **absent** | Max Creation Graph is **undrivable** from this bridge |
| `scatter_forest_pack` | **absent** (forestPack not installed) | Chaos Scatter |
| all 14 `tyflow_*` | **absent** (tyFlow not installed) | Chaos Scatter / PhysX / instance copies |
| `get_railclone_style_graph` | **absent** (railClone not installed) | `3dsmax-mcp_clone_objects` instance mode |

**ForestPack, forestLite, tyFlow, railClone and phoenixFD are not installed.** Present: Corona, Chaos,
Arnold, PhysX, FbxMaxWrapper, USD.

**Important distinction for this task:** a reference file *warning* that a tool is absent is CORRECT and
must be kept. A reference file that *prescribes* a call to an absent tool is WRONG and must be corrected.
`grep -l` for a name does not tell you which kind of mention it is — read the sentence.

## 2. References already settled — do not re-open

| File | Verdict | Where it is recorded |
|---|---|---|
| `references/procedural-graphs.md` | Data Channel content valid; **all `mcg_*` content is moot** | `SKILL.md:471` |
| `references/railclone.md` | **OBSOLETE**, reference only | `SKILL.md:473` |
| `references/tyflow-graphs.md` | **OBSOLETE**, reference only | `SKILL.md:474` |
| `references/maxscript-splines-shapes.md` | **largely VINDICATED** at P4b-r (10 corrections applied) | `CHECKPOINT.md` §"Reference claim-by-claim pass" |
| `references/arch-modifiers-and-procedural-reference.md` | **substantially wrong**, corrected in place | same section |
| `references/nurbs-complete-guide.md`, `references/nurbs-architecture-recipes.md` | keyword claims **vindicated** at P4b — do **not** rewrite geometry claims | `CHECKPOINT.md` §"Rail sweeps, blends and trims" |

## 3. Standing rule that governs every edit in this close-out

> **MAXScript execution is the only ground truth. An unexecuted claim is a hypothesis. An "unresolved"
> label is not a finding. Nothing may be recorded as blocked, impossible or non-existent without a
> transcript showing the attempt and the exact error.**

Corollary, the one that matters most for this task: **a tool name that appears in a reference file is
not evidence that the tool exists.** Four of these references were written against a 178-tool server
that is not the one connected. Route them to what is verified, or mark the file OBSOLETE — do not
leave a recipe that cannot be executed.

## 4. Verified geometry and API facts relevant to the open items

| Fact | Note |
|---|---|
| Scene units are **centimetres**, `units.SystemScale` 1.0 — a spec value in cm reaches Max unchanged | read `units.SystemType` directly; `getProperty units #SystemType` **fails** |
| `Box(width:,length:,height:,pos:)` is the placement primitive. Geometry centres on `pos.x/y` and the **base sits at `pos.z`** | true after `copy`, after `baseObject =` and after rotation |
| Instance route: `n = copy src` then `n.baseObject = src.baseObject`. **`setCopyMode` does not exist** | verified discriminator: plain `copy` shares nothing, after the assignment it does |
| Z rotation: `n.rotation = quat <degrees> [0,0,1]`. **`rotationZ`/`rotationX`/`rotationY`/`matrix3`/`angle` do not exist** | a 100×200×20 box at rot 90 spans X 200 / Y 100 |
| Substring test: `substring s 1 n` works. `findString` **also works** (the old "absent" note was wrong) | returns a 1-based index; `undefined` when absent |
| `getCurrentException()` inside a `catch` **DOES work** — 6 of 6 throw kinds, with a non-throw control. The old "throws itself" rule was **withdrawn 2026-10-05** | do not "fix" code for this |
| `try { } catch { }` brace form **is** a parse error. Use `try ( ) catch ( )` | |
| `delete <base>` does **not** delete its instances; same for dummies | |
| A bare modifier is not a scene node and cannot be deleted | |
| Layer assignment is impossible from this bridge. **Nine** routes executed, all failed. `manage_layers`' whole vocabulary is `{list, create, delete}` | layer attribution is **data**, permanently — the user applies it in the Layer dialog |
| The **Boolean modifier cannot be made to cut** in this build. Walls are built as solid `wall_cells[]` tiles, `assembly.ms` contains **zero** `addModifier` calls | `G-81` |
| `ChaosScatter()` constructs; `CScatter` is **NotCreatable**. `seed` is 1…31337 and is **data**. The real property name is **`distributionDesityPattern`** — the typo is in Max | `references/14-chaos-scatter.md` |
| ≤ 5 modifiers per `execute_maxscript` call; > 10 on one node forbidden. **20 froze Max permanently and cost a reboot. Do not re-measure the ladder.** | |
| `assembly.ms` emits **zero** scatter geometry. `assembly.json.scatter[]` (1 row) is a **declaration**. **Decision taken 2026-10-06: scenario A — the user applies it by hand from `snippets/chaos_scatter.ms`, and 254 is the delivered count** | |
| All **29** prototypes are emitted at `pos [0,0,0]` — stacked at the world origin, inside the footprint, not at a scratch offset | `examples/assembly.ms:877` onward |
| Materials are **per node**, not per prototype: 0 of 10 instances inherited a material set on the prototype. `baseObject` sharing is a memory optimisation, not inheritance | measured 2026-10-05 |
| `renderers.production = Corona()` — **instantiate, do not assign the class**. `renderers.current = Corona` throws. Both slots are independent; both are now Corona | `Corona()` costs ~3.5 s cold → needs its own call |

## 5. Files, not facts — state of the drift items

| Item | State on 2026-10-06 |
|---|---|
| `scripts/validate_specs.py --help` says `G-1..G-40` | **ALREADY FIXED** — `ArgumentParser` now reads `G-1..G-83` |
| `agents/max-facade.md:316` `setCopyMode` / `rotationZ` | **ALREADY FIXED** — reads `copy` + `baseObject =` + `quat <deg> [0,0,1]` |
| `agents/max-assembly.md` §4 step 5 "scratch offset" | **ALREADY FIXED** — now states `pos [0,0,0]`, measured |
| `scripts/init_project.py` `assembly.json` stub missing `wall_cells` | **ALREADY FIXED** — `scaffold_assembly()` writes `doc["wall_cells"] = []` |
| `3dsmax-arch-nurbs-ultimate.skill` archive stale | **ALREADY FIXED** — rebuilt; `collect_files()` ships `scripts/`, `agents/`, `specs/`, `examples/`, and the four top-level md files. Verified byte-identical to the working tree on 6 files |
| `AGENTS.md` §"Known packaging gap" | **STALE** — still claims `collect_files()` ships only `SKILL.md`/`references/`/`snippets/`. `scripts/install_skill.py:22-31` shows `TOP_LEVEL_FILES = ("SKILL.md","PLAN.md","CHECKPOINT.md","AGENTS.md")` and `PACKAGE_DIRS` covering `references snippets scripts agents specs examples` |
| `agents/max-components.md` §7 UNVERIFIED table | **STALE** — still lists "Rotating a node after creation" and "Copy/instance mode producing a shared `baseObject`" as UNVERIFIED. Both verified at P5/P6 (§4 above) |
| `references/07-spec-grammar.md:2072` (`G-54` row) | **STALE** — cites `§8.2.7` for the "trim projects and does not cut" claim; the correct citation is **`§8.2.8` row 8**. Lines 1263 and 2248 were already fixed |
| `references/14-chaos-scatter.md:183` (`G-74` row) | **STALE** — reads "unique across `placements[]`, `opening_cuts[]` and `scatter[]`", omitting **`wall_cells[]`**. `G-74` in both `validate_specs.py` and `place_components.py` covers all four |
| `scripts/env_preflight.py` `sweep_on_shape` check | **WRONG EXPECTATION** — expects `mods=1 first=Sweep`, but `Sweep` is one of the **six classes measured to construct and then throw** on `addModifier` (`Extrude Sweep Lathe Surface CrossSection Bevel_Profile`). Re-confirmed at the P6 ladder rung 1–2 |
| `scripts/env_preflight.py` `loft_not_creatable` probe body | **uses `getCurrentException()` inside a `catch`** (`line 227`), which this repo's own `agents/max-*.md` AP-21 forbids. Note the rule was withdrawn as *false* — but a flag-based body is still the safer form and the repo's playbooks demand it |
| `references/curve-construction.md` | **WRITTEN AGAINST ABSENT TOOLS** — `curve_model`, `inspect_curve`, `edit_curve`, `draw_spline`. 120 lines, no verified content |
| `references/architecture-exterior-pipelines.md` | **WRITTEN AGAINST ABSENT TOOLS** — `curve_model`, `loft_mesh`, `draw_spline`, `geometry_qa`, `contact_check`, `agent_viewport`. 186 lines. The architectural *dimensions* content (floor heights, stair risers, layer naming) is reusable |
| `references/nurbs-architecture-recipes.md` | routes to `curve_model`, `loft_mesh`, `draw_spline`, `geometry_qa`, `contact_check`, `agent_viewport` in the tool-routing prose. **The NURBS geometry recipes were VINDICATED at P4b — do not touch them** |
| `references/nurbs-complete-guide.md` | two incidental mentions of `geometry_qa` / `agent_viewport` in verification advice (lines ~262, ~420). Geometry content is verified — touch only the routing sentences |

## 6. What the validator and builders currently report

```
python -m py_compile scripts/*.py                              exit 0
python scripts/validate_specs.py --dir examples                PASS 138 / FAIL 0 / WARN 0 / SKIP 15
```

Any edit to `scripts/` must leave both of those true.
