# `_drift-audit.md` — documentation drift audit, 2026-10-06

**Method.** Read-only sweep of `references/*.md`, `agents/*.md`, `SKILL.md`, `PLAN.md`, `snippets/*.ms`,
`scripts/*.py`, `examples/*` against the 17 measured facts in `CHECKPOINT.md`. **No live bridge was
contacted; nothing in the repo was modified.** Every row below was read in place, not inferred from a
grep hit alone.

Severity: **HIGH** = would mislead a modelling session, cause a crash, or produce wrong geometry ·
**MED** = misleading · **LOW** = cosmetic.

Category key: **(b)** stale falsehood needing correction · **(a)** correctly stated, listed only where
the distinction is easy to get wrong · **(c)** legitimate warning about an absent tool — **correct, keep.**

---

## 1. HIGH

| file:line | what it says | fact | severity |
|---|---|---|---|
| `snippets/nurbs_arch_library.ms:86` | `NURBSSurfaceApproximation … curvatureAngle:(degToRad angleDeg)` inside `applyArchTessellation`, default `angleDeg:6.0` (line 81) | **1** — degrees, never `degToRad`. `0.10472` → **691** verts vs **101** for `6.0`: a ~6.9× over-tessellation of **every render approximation this library produces**. This is shipped executable code, not prose | **HIGH** (b) |
| `references/12-nurbs-gotchas.md:1065-1079` | *"**Boolean / solid ops.** `Boolean` geometry object and the `Boolean` modifier are available; this is the practical route for cutting openings in slabs and walls."* + snippet `local boolMod = Boolean()` / `boolMod.operand = b` | **11** — `Boolean()` **throws**; `BooleanMod()` carries Voxel Map's paramblock; the bridge's `add_modifier` attaches one whose operand is never set. `07` §8.5.8 and `max-assembly.md` §6.2.1 both carry the full correction — this file does not | **HIGH** (b) |
| `references/railclone.md:1-5` (whole file, 193 lines) | No banner, no fence. *"Use RailClone's graph to assemble the requested model. … The recipes below were **verified in 3ds Max 2027 with RailClone Pro 7.3.5**."* | **9** — railClone is **not installed**. Also a wrong-version claim (target is 2026.3.2) | **HIGH** (b) |
| `references/tyflow-graphs.md:1-3` (whole file, 56 lines) | No banner, no fence. *"Read this reference completely before building, inspecting, editing, or verifying tyFlow event graphs."* then an "agentic loop" | **9** — tyFlow absent; all 14 `tyflow_*` tools throw | **HIGH** (b) |
| `SKILL.md:473` | *"`references/curve-construction.md` … **the same convention as `references/railclone.md` and `references/tyflow-graphs.md`**"* — asserts those two files carry a top router and a fenced non-executable body | **9** — **both claims are false**; neither file has a router or a fence (verified: zero matches for `OBSOLETE` / `do not execute`). The index an agent reads vouches for a mitigation that does not exist | **HIGH** (b) |
| `references/procedural-graphs.md:9, 11` | *"Discover with **`list_dc_operators`** …"* · *"Edit with `set_data_channel_operator` and **`manage_data_channel_stack`**"* | **9** — neither tool exists in the connected toolset. Real vocabulary is 6 `*_dc_*` tools | **HIGH** (b) |
| `references/procedural-graphs.md:27-29, 37-38, 61` | 12 `mcg_*` names presented as **the workflow**: `mcg_get_context`, `mcg_list_graphs`, `mcg_inspect_graph`, `mcg_search_operators`, `mcg_create_graph`, `mcg_apply_patch`, `mcg_compile_graph`, `mcg_test_tool`, `mcg_restore_checkpoint`, `mcg_cleanup_workspace`, `mcg_reload_operators`, `mcg_apply_modifier` | **9** — the entire `mcg_*` family does not exist. `arch-modifiers-and-procedural-reference.md` §3 received a retraction banner at P4b-r; this file, the second MCG document, got none. `SKILL.md:472` calls it "partially obsolete" but the file gives a reader no router | **HIGH** (b) |
| `references/01-architecture-aec-workflow.md:187-196` | Full **S6 materials stage**: gate on `materials.json`; deliverables *"Corona PBR materials assigned"*; tools `assign_material`, `create_material_from_textures`, `palette_laydown`, `set_sub_material` … | **14** — P7 **cancelled** 2026-10-05; materials are applied **by hand**. Names `agents/max-materials.md`, which does not exist. §3's own preamble (line 97) promises absent agent files are *stated* — this one is not | **HIGH** (b) |
| `references/01-architecture-aec-workflow.md:198-207` | Full **S7 QA stage**: *"gate: `qa.json` carries a `verdict`"*, deliverables *"the determinism record, captures by architectural viewpoint"*, tools `capture_viewport`, `capture_multi_view`, `isolate_and_capture_selected` | **14** — P8 **cancelled**. `qa.json` is a reserved stub that is **absent**; there is no automated QA pass | **HIGH** (b) |
| `references/01-architecture-aec-workflow.md:209-218` | Full **S8 export stage**: *"deliverables: `export.json`, **FBX / OBJ / USD output**, the delivery MAXScript and its manifest"* | **14** — P9 **cancelled**. `export.json` absent, `export_max.py` never written | **HIGH** (b) |
| `references/14-chaos-scatter.md:1, 21, 134, 137, 165-167` | Title *"...and the **P8** determinism hook"* · *"This is what makes the **P8 QA hook** work"* · §5 *"`FpInterface` — the **P8** determinism hook"* · *"**This is the replacement for the nonexistent QA tools.** … **the protocol itself belongs to P8** (`agents/max-qa.md`, **planned**)"* | **14** — P8 cancelled; `agents/max-qa.md` does not exist and **is not planned**. This is the only remaining explicit promise of a planned QA stage outside `01` | **HIGH** (b) |
| `AGENTS.md:249-257` *(top-level instruction file, outside the named list — reported anyway)* | §"Known bugs in `snippets/nurbs_arch_library.ms`" — *"Three **open** defects"* … *"3. `NURBSControlVertex` **does not construct**; the `setCV` path fails silently. **Unresolved.**"* | **10** + `CHECKPOINT` P1-b (all four bugs **fixed**, 2026-10-04, all ten functions executed live; bug 3's premise was **false**). The shipped library already writes `(NURBSControlVertex …)` at lines 65 and 298. `PLAN.md:93-98` carries the correct STATUS banner; `AGENTS.md` does not | **HIGH** (b) |

---

## 2. MED

| file:line | what it says | fact | severity |
|---|---|---|---|
| `references/01-architecture-aec-workflow.md:181` | Gate: *"**and the `manage_layers` object-assignment action name has been found by execution** — it is still unknown (`CHECKPOINT.md`, open item for P6)"* (self-contradictory as written) | **12** — **CLOSED at P6** as a verified negative; vocabulary is exactly `{list, create, delete}` | MED (b) |
| `references/01-architecture-aec-workflow.md:182-183` | Deliverables *"`ChaosScatter` setups with an explicit integer `seed`"* · *"a scatter is **emitted** without a seed"* | **15** — `assembly.ms` emits **zero** scatter geometry; `scatter[]` is a declaration the user applies by hand | MED (b) |
| `references/01-architecture-aec-workflow.md:184-185` | *"escalate to … the orchestrator to **resolve the `manage_layers` action name**"* · tools *"`execute_maxscript` (**ChaosScatter, boolean cuts**)"*, `clone_objects (mode: "instance")` | **12**, **11**, **8**, **15** — layer is permanently data; Boolean cannot cut; `setCopyMode` is absent so `mode:"instance"` is not a verified instance route; no scatter is emitted | MED (b) |
| `references/01-architecture-aec-workflow.md:253-256` | *"**S7's determinism check** … it re-runs the build, reloads the saved scatter configuration and asserts an identical count"* | **14**, **15** — S7 cancelled; no scatter config exists on the delivered model | MED (b) |
| `references/01-architecture-aec-workflow.md:77-79, 85-87` | Spec-chain rows 9/10/11 name owners `agents/max-materials.md` / `max-qa.md` / `max-export.md`; *"Row 10 has no upstream sibling: S7 is the only stage that reads **all** of the others"* | **14** — three agent files that do not exist and are not planned | MED (b) |
| `references/02-mcp-live-orchestration.md:231` | Routing table: *"Layers: create, delete, list, **set properties, move objects**"* → `manage_layers` | **12** — 40+ candidate actions rejected with a uniform `Unknown layer action`. Both listed extras fail. `SKILL.md:113` states the correct three | MED (b) |
| `references/02-mcp-live-orchestration.md:410` | *"For Max lofting, sweeping, extrusion and **booleans**, use `execute_maxscript`"* | **11** — the Boolean half of this sentence has no working route in this build | MED (b) |
| `references/02-mcp-live-orchestration.md:369` | *"`NURBSNode nset` is the surface node (**`Point_Surf` / `CV_Surf`** are valid identifiers)"* | **4** — a node's `classOf` is `NURBSSurf` / `NURBSCurveshape`. The identifiers exist as classes, but the phrasing reads as a node class. `nurbs-complete-guide.md:13` and `PLAN.md:88-89` state it correctly | MED (b) |
| `references/07-spec-grammar.md:2318` | *"The **printed string form** of a `nurbsID` … ⚠️ **UNVERIFIED**, and one earlier reading was wrong … a later controlled probe **did not reproduce** it"* | **2** — **CLOSED at P12**: `IntegerPtr`, prints `<decimal>P`, `railID="0P"` reproduced **3/3**. The row immediately above (`:2316`) in the *same table* already states the correct answer, so the file contradicts itself row-on-row | MED (b) |
| `references/07-spec-grammar.md:2314` | *"an object's layer cannot be assigned … **six routes** executed and rejected … application is a **P6 concern**"* | **12** — **nine** routes; P6 **closed** it as permanently impossible. Application is the **user's** action in the Layer dialog | MED (b) |
| `references/07-spec-grammar.md:1426, 1560` · `agents/max-facade.md:294` · `agents/max-components.md:418` | *"`material_role` … a **role for P7**, never a material class"* · *"**P7 resolves** a role to a material"* | **14** — P7 cancelled; nothing resolves a role to a material | MED (b) |
| `references/07-spec-grammar.md:873` | *"QA must therefore compare **evaluated** geometry against the lattice … (this is what **P8 asserts**)"* | **14** — the rule is sound; its owner is a cancelled stage | MED (b) |
| `references/07-spec-grammar.md:1867` | *"No `materials`, no `cameras`, no `lights`, no `export`. Those are **P7, P8 and P9**."* | **14** — reads as three pending stages inside a prohibition list | MED (b) |
| `references/08-input-rules.md:258, 260` | *"`python scripts/validate_specs.py …` ⬜ **planned, P2c — does not exist yet**"* · *"`init_project.py` ⬜ planned, P2c … **Until it exists**, create the directory and copy the envelope by hand"* | Both scripts **exist and ship**; `AGENTS.md` lists both as executable; `max-input.md` is their stage owner. The paragraph directly below then tells S1 to run the manual checklist — the exact failure this table causes | MED (b) |
| `references/09-defaults.md:111` | *"they inform later stages that build the layers (**P6 assembly, P7 materials**)"* | **12**, **14** — no stage builds layers; P7 cancelled | MED (b) |
| `references/09-defaults.md:273` | `D-CL-09` *"reference only — **overlap for a boolean cut**, cutter depth vs host thickness"* · *"the cutter must pierce both faces of the host"* | **11** — there is no cutter; walls are solid `wall_cells[]` | MED (b) |
| `references/11-layer-standard.md:6` | *"consumed by … `assembly.json.layer_map` **at P6**, and by the **QA loop at P8**"* | **12**, **14** — layer_map is never applied by a stage; there is no QA loop | MED (b) |
| `references/12-nurbs-gotchas.md:1125-1127` | Planning rule 15: *"They read back `0`, a **`nurbsID` string**, or a sign-flipped vector"* | **2** — `nurbsID` is an `IntegerPtr`, not a string. Contradicts **its own** line 1136 and its own §3.29 closure at line 1382 | MED (b) |
| `references/nurbs-complete-guide.md:22, 24, 29, 36` | §"CRITICAL RULE #1" builds the whole id-vs-index distinction on a type named **`NURBSId`** — *"an opaque runtime **integer** assigned by 3ds Max"* | **2** — the class is `IntegerPtr`. **Its own line 172 corrects this**; the section header and rule table were not updated | MED (b) |
| `references/nurbs-complete-guide.md:318` | *"`NURBS1RailSweepSurface` — Properties: `.rail : integer`, **`.railID : integer`** (`NURBSId`)"* | **2** — `railID` reads `0P` on a committed 1-rail sweep, an `IntegerPtr` | MED (b) |
| `references/nurbs-complete-guide.md:322` | *"`.rail1 : integer`, **`.rail1ID : integer`**, **`.rail2ID : integer`**"* | **2** — P12 measured both as **full `IntegerPtr` pointers** equal to each rail curve's own `nurbsID` | MED (b) |
| `references/nurbs-complete-guide.md:259` | `NURBSPointCurveOnSurface` *"Inherits `NURBSPointCurve` (`numPoints`, **`closed`**, `setPoint` …)"* | **7** — `NURBSPointCurve.closed` throws on **read and write**; `.isClosed` (read-only) is the only flag. **Its own line 220 corrects this** | MED (b) |
| `references/maxscript-common-patterns.md:278-282` | A whole subsection teaching `formattedPrint` as "C-style formatting" | **3** — `formattedPrint` **hung `execute_maxscript` to timeout and crashed 3ds Max outright** on one attempt through this bridge. No warning anywhere in the file | MED (b) |
| `references/maxscript-3dsmax-objects.md:430` | `selection[i].name = "Part_" + (formattedPrint i format:"03d")` | **3** — same. Use plain `+` concatenation | MED (b) |
| `references/maxscript-rendering-cameras.md:70, 477` | `render to:bm outputfile:(@"...frame" + (formattedPrint t format:"04d") + ".png")` | **3** — same | MED (b) |
| `references/maxscript-materials-textures.md:12-16` | Guesses `OpenPBRMaterial` → `OpenPBR_Material` → `OpenPBR_Mtl`, *"Class spelling differs across Max builds; introspect/discover first"* — **the correct `OpenPBR` is never tried** | Measured (not in the 17, but contradicting `PLAN.md:135`, `SKILL.md:412`, `02:477-481`, `12-nurbs-gotchas.md:392-402`): the constructor is **`OpenPBR`**, and `OpenPBRMaterial` **does not exist**. `SKILL.md:147` cites this very file as its authority | MED (b) |
| `references/maxscript-materials-textures.md:117` | *"`-- introspect_class class_name:"OpenPBRMaterial" -- or discovered name`"* | Same. Also routes to `introspect_class`, which `02` §6.1 proves is a false-negative machine | MED (b) |
| `agents/max-facade.md:48, 433` | *"**`manage_layers` object assignment — six action names rejected, the real one unknown.** That is S5's problem"* · *"Layer is data; **S5 applies it** through `assembly.json.layer_map`"* | **12** — nine routes ruled out, permanently; the **user** applies it in the Layer dialog. `max-assembly.md` §6.3 has the correct text | MED (b) |
| `agents/max-components.md:48` | *"the real one unknown. S5's problem"* | **12** — as above | MED (b) |
| `agents/max-assembly.md:7, 43, 45` | *"Materials and renderer choice are **S6** (`materials.json`); QA, captures and the scatter determinism proof are **S7**; export is **S8**"* · `materials.json` · `export.json` | **14** — the same file's line 44 correctly says *"nobody — S6/S7/S8 were cancelled"*. Lines 7/43/45 are the uncorrected originals | MED (b) |
| `agents/max-massing.md:36, 40` | *"Materials, renderer choice, UVs · **S6** · `materials.json`"* · *"Scatter, planting, cameras, lights, export · **S5 / S7 / S8** · `assembly.json.scatters`, `qa.json.captures`, `export.json`"* | **14** — and `assembly.json.scatters` is the **wrong key**; the schema key is `scatter` (`07` §8.5.4) | MED (b) |
| `agents/max-facade.md:33` · `agents/max-components.md:34` · `agents/max-nurbs.md:40` | *"Materials, renderer choice, UV rules · **S6** · `materials.json`"* | **14** — cancelled stage presented as a live boundary | MED (b) |
| `references/14-chaos-scatter.md:183` | `node_name` → *"the **scatter node's** name; hyphen-free"* | **15** — no scatter node is ever created. This file is the scatter reference and carries **no** declared-not-built note (grep for `declared`/`by hand`/`not built` in it returns nothing) | MED (b) |
| `snippets/chaos_scatter.ms:20-22` | *"`rebuild` … That is what makes the **P8 determinism protocol** work: saveConfiguration → clear → rebuild → loadConfiguration → compare getInstanceCount()"* | **14** — P8 cancelled; `14-chaos-scatter.md` §5.1 is the same cancelled protocol | MED (b) |
| `references/12-nurbs-gotchas.md:1081-1084` | *"**Tessellation for export.** NURBS patches must be tessellated before **FBX / OBJ export**"* | **14** — there is no export stage. The `NURBSSurfaceApproximation` advice itself is fine | MED (b) |

---

## 3. LOW / cosmetic

| file:line | what it says | fact | severity |
|---|---|---|---|
| `references/nurbs-architecture-recipes.md:262, 286` | *"Find target surface **NURBSId**"* · *"parent1ID references the existing scene surface by **NURBSId**"* | **2** — same `NURBSId`-as-a-type slip as `nurbs-complete-guide.md`. Neither line ever tells an agent to write a literal, and the recipe is marked UNVERIFIED | LOW (b) |
| `references/00-audit-p1.md:257, 259, 267` | *"Route: **P9** (export)"*, *"Route: **P7**"* | **14** — historical P1 audit with dated rewrite briefs and its own stale-tool banners. It is a record of what was found then, not a routing instruction | LOW (c) |

---

## 4. Facts with **no** drift found — stated explicitly

| # | fact | verdict |
|---|---|---|
| 1 | `curvatureAngle` is degrees | `nurbs-complete-guide.md:141`, `nurbs-architecture-recipes.md:77,87` and the whole `_04-05-evidence.md` §Batch 22 are **correctly corrected** (the `degToRad` wrapper *was* removed from Recipe 1). `12-nurbs-gotchas.md:68` lists the property without a unit claim. **One** stale site: `snippets/nurbs_arch_library.ms:86` — see HIGH |
| 2 | `nurbsID` is `IntegerPtr`, `<decimal>P`, never a literal | `SKILL.md:164-172`, `build_nurbs.py` (`G-56` enforcement), `examples/nurbs.ms:28-39,164,176`, `12-nurbs-gotchas.md:1136` and `:1382`, `nurbs-complete-guide.md:172`, `07-spec-grammar.md:1066,1252,2316` are all **correct**. Six type-name slips remain — see MED |
| 3 | `formattedPrint` must never be called from this bridge | **No file warns about it anywhere.** 7 call sites in 4 files, none fenced — see MED |
| 4 | node `classOf` is `NURBSSurf` / `NURBSCurveshape` | `nurbs-complete-guide.md:13` is a **model** correction (names the four wrong ones and why). `12-nurbs-gotchas.md:72` and `PLAN.md:88-89` correctly separate "valid identifiers" from "node class". One slip: `02:369` |
| 5 | `addNURBSSet` is a silent no-op | **Fully corrected** in `nurbs-complete-guide.md:18,392,398,402-403` and `nurbs-architecture-recipes.md:20,294,304-305`, each with a dated execution transcript and the working single-set alternative. No merge snippet is presented as working anywhere. **No drift.** (`SKILL.md:175` lists it as UNVERIFIED — a weaker but not false statement) |
| 6 | property renames (`pointType`→`.type`, `trim`→`.trimCurve`, `trimCurve1/2`→`trim1/2`, `curveStartPoint` is Float) | `nurbs-complete-guide.md:189,191,255,338` all carry the corrections. The old names survive **only** in `_04-05-evidence.md:52,62,72,86` — a claim table whose own line 618-626 resolves every one. **No drift** |
| 7 | absent properties (`.isSelected`, `.index`, `closedU/closedV`, …) | `nurbs-complete-guide.md:31,173,174,291` corrected with class counts. **One slip**: `:259` inherits `closed` — see MED |
| 8 | `setCopyMode`, `rotationZ/X/Y`, `angle` absent; `copy`+`baseObject=`; `quat <deg> [0,0,1]` | Correct in `SKILL.md:141,395-396`, all four `agents/max-*.md`, `place_components.py:75-82,2248-2258` (which **bans** the strings), `examples/assembly.ms:964`, `architecture-exterior-pipelines.md:455-456`, `14-chaos-scatter.md:285`, `_p6-contract.md:284`. **No drift.** Only `01:185`'s `clone_objects(mode:"instance")` is unverified rather than false |
| 9 | `mcg_*` / `curve_model` / forestPack / forestLite / tyFlow / railClone / phoenixFD absent | Warnings are **correct everywhere** — `AGENTS.md:175,217`, `SKILL.md:78`, all `agents/max-*.md`, `02` §3, `curve-construction.md` (router present, body fenced — verified), `arch-modifiers-and-procedural-reference.md:4,10,62` (retraction present — verified), `procedural-graphs.md`, `railclone.md`, `tyflow-graphs.md` **(these three are the drift — see HIGH)** |
| 10 | `Loft()` NotCreatable · `NURBSControlVertex` needs a wrapper | Correct in `SKILL.md:200-203`, `max-orchestrator.md:141`, `max-nurbs.md:350`, `12-nurbs-gotchas.md:70-71,200,252-275,1102-1105`, `nurbs-complete-guide.md:176-183,213`, `nurbs-architecture-recipes.md:17`, `build_nurbs.py`, and `PLAN.md:91-98` (which keeps the old table **with** a STATUS banner — the right convention). **One drift**: `AGENTS.md:257` |
| 11 | Boolean unusable; walls are `wall_cells[]` | Correct in `SKILL.md:37,114,137,277`, `max-assembly.md` (whole §6.2.1 + AP-1 + AP-22), `07-spec-grammar.md:1876-1918,2183-2184`, `place_components.py` (Boolean-era functions deleted at P10-lite). **Two slips**: `12-nurbs-gotchas.md:1065-1079` (HIGH) and `09-defaults.md:273` |
| 12 | `node.layer` read-only; nine routes ruled out; layer is data | Correct in `SKILL.md:113,152,281`, `max-assembly.md:255-270,518`, `14-chaos-scatter.md:220-233`, `build_spec.py:1820`, `build_nurbs.py:2516`, `facade_tables.py:3687`, `examples/assembly.ms:5`. **Five stale slips** — see MED |
| 13 | units cm / scale 1.0 · base at `pos.z` | **No drift found anywhere.** Checked `SKILL.md:36,138,141,411`, `PLAN.md:244`, all four `agents/max-*.md`, `09-defaults.md:342-348`, `07-spec-grammar.md:39-41,2312,2315`, `architecture-exterior-pipelines.md:23-24,118`, `build_spec.py:1149`, `place_components.py:80-82,1433,1460`, `nurbs-architecture-recipes.md:391`. Every one states base-at-`pos.z` **and** the `cz − height/2` correction |
| 14 | no QA / export / scripted materials | Correct in `SKILL.md:43-47,223-225,334`, `AGENTS.md:38-54`, `max-orchestrator.md:23-24,40-44`, `PLAN.md:245-248`, `architecture-exterior-pipelines.md:355`. **Everywhere else drifts** — see HIGH + MED |
| 15 | scatter is declared in data only | Correct in `SKILL.md:141` (routing to Chaos Scatter generally), `max-orchestrator.md:507-540`, `max-assembly.md:30,44`, `examples/assembly.ms` (zero scatter nodes), `07-spec-grammar.md:1873-1874`, `PLACE_COMPONENTS`. **Three slips**: `01:182-183,185`, `14-chaos-scatter.md:183`, `snippets/chaos_scatter.ms:20-22` |
| 16 | `for o in objects do delete o` skips entries | Correct in `max-assembly.md:14` + AP-6, `max-components.md:348`, `AGENTS.md` §"Iterating". **No drift.** No file recommends the bare one-liner as a cleanup route |
| 17 | `getCurrentException()` **works** (withdrawn) | Correct in `AGENTS.md` §"getCurrentException()" — explicitly marked **WITHDRAWN 2026-10-05 as false**, with the 6/6 and 4/4 transcripts. `max-orchestrator.md` uses the separate-fields probe form. **No drift.** |

---

## 5. Clean files

Read end-to-end or swept term-by-term, with **nothing** to correct:

`SKILL.md` — except `:473` (HIGH) · `PLAN.md` · `AGENTS.md` — except `:249-257` (HIGH) ·
`agents/max-orchestrator.md` · `agents/max-input.md` · `references/curve-construction.md` (router present,
body fenced) · `references/arch-modifiers-and-procedural-reference.md` (retraction banner present) ·
`references/08-input-rules.md` — except `:258,260` · `references/10-conflict-resolution.md` ·
`references/improvement-log.md` · all six `_*-evidence.md` / `_*-contract.md` transcripts ·
`references/maxscript-core-syntax.md` (correctly records `sin` as degrees at `:68,457`) ·
`references/maxscript-splines-shapes.md` · `references/maxscript-animation-controllers.md` ·
`references/maxscript-mesh-poly-ops.md` · `references/maxscript-scripted-plugins.md` ·
`references/maxscript-ui-rollouts.md` · `references/nurbs-architecture-recipes.md` — except `:262,286` (LOW) ·
`references/09-defaults.md` — except `:111,273` · `references/11-layer-standard.md` — except `:6` ·
`references/07-spec-grammar.md` — except `:873,1426,1560,1867,2314,2318` ·
`references/02-mcp-live-orchestration.md` — except `:231,369,410` ·
`references/12-nurbs-gotchas.md` — except `:1065-1079,1081-1084,1125-1127` ·
`references/14-chaos-scatter.md` — except `:1,21,134,137,165-167,183` ·
**`scripts/*.py`** — all eight. `place_components.py:2258` actively **bans** `setCopyMode`/`rotationZ`/
`angle`; `build_spec.py:1820` and `build_nurbs.py:2516` refuse to emit layer code; no builder emits a
Boolean, a scatter node, `degToRad`, or `formattedPrint`.
**`examples/*`** — all 13 files. `assembly.ms:964` and `:1782` carry the correct `setCopyMode` / no-Boolean
notes; `nurbs.ms` binds every `parent1ID:` from a committed sub-object.

---

## 6. Suggested fix order

1. **`snippets/nurbs_arch_library.ms:86`** — delete `degToRad`. One character-class change, measurable
   ~6.9× mesh reduction, and it is the only *code* defect in the pack.
2. **`references/railclone.md`, `tyflow-graphs.md`, `procedural-graphs.md`** — apply the router-at-top +
   fenced-body convention that `curve-construction.md` already uses, then fix `SKILL.md:473`.
3. **`references/01-architecture-aec-workflow.md` §3 S6/S7/S8** — add the cancellation banner, or delete
   the three stage contracts. They name three agent files that do not exist.
4. **`references/12-nurbs-gotchas.md:1065-1079`** — replace the Boolean section with the `wall_cells[]`
   route; `07` §8.5.8 and `max-assembly.md` §6.2.1 already hold the text.
5. **`references/14-chaos-scatter.md` + `snippets/chaos_scatter.ms:20-22`** — drop "P8", state that the
   scatter is **declared, not built**.
6. **`AGENTS.md:249-257`** — replace the three "open defects" with the P1-b closure; keep the bug list only
   as a dated historical record the way `PLAN.md:93-98` does.
7. The MED layer rows (five sites) — replace "the real one unknown / S5 applies it" with the nine-route
   closure and "the user applies it".
8. The MED type-name slips (`nurbsID` as a string / `NURBSId` / `: integer`) — mechanical, six sites.
9. `formattedPrint`: add a one-line warning to the four `maxscript-*.md` files, or drop the seven sites.