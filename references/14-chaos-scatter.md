# 14 — Chaos Scatter: the verified parameter map, the measured hazard, and how the hand-application works

> **CORRECTED (2026-10-06):** this file's title used to promise "the P8 determinism hook", and §5
> presented that hook as owned by a planned S7. **P8 (S7, automated QA) was cancelled by explicit user
> decision on 2026-10-05** — not deferred. There is no QA stage and no planned one, and
> `agents/max-qa.md` does not exist and is not planned. **The scatter is a declaration in
> `assembly.json.scatter[]`, and the user applies it by hand from `snippets/chaos_scatter.ms`. S5 does
> not build it and does not measure it.** The `FpInterface` read-backs in §5 remain **verified and
> useful** — they are what the hand-application route uses — but they gate nothing.

> **Authority.** This file documents what was **executed** against 3ds Max 2026 through the
> `cl0nazepamm/3dsmax-mcp` bridge, plus the parameter map recorded in `PLAN.md` §4.1 and the transcripts
> in `CHECKPOINT.md`. It **replaces** `references/railclone.md`: railClone is not installed, so its
> subject matter is unavailable, and Chaos Scatter is the only working scatter route in this
> installation.
>
> **Every 3ds Max tool in this file is written `3dsmax-mcp_*`.** A large set of names in the connected
> toolset belongs to the **Rhino** server and fails confusingly against Max (`AGENTS.md` §"MCP tool-name
> collisions") — never call those here.

---

## 1. What is verified, and what is not

| Fact | Status | Evidence |
|---|---|---|
| `ChaosScatter()` **constructs**. Superclass `geometry`, classID `[1672609897, 845042209]` | ✅ executed | `PLAN.md` §4.1; `CHECKPOINT.md` §"Chaos Scatter" |
| `CScatter` is its base class and is **NotCreatable** | ✅ executed | Always construct `ChaosScatter` |
| `seed` is an integer **1 … 31337** → **deterministic** | ✅ executed | Same seed, same scatter. This is what makes a hand-applied scatter reproducible — and why a run-time seed is a defect, not a default |
| `FpInterface` exposes `getInstanceCount()`, `getModelCount()`, `getModelNode(i)`, `update()`, `clear()`, `addModelNode(node)`, **`saveConfiguration(f)` / `loadConfiguration(f)`** | ✅ executed | `PLAN.md` §4.1; `CHECKPOINT.md` |
| The property is spelled **`distributionDesityPattern`** — **the typo is the real name** | ✅ executed | `SKILL.md`; `02` §2.4. The spec file uses the corrected spelling; **the builder emits the typo** |
| The parameter map in §2 | ✅ executed property by property | `PLAN.md` §4.1 |
| Chaos Scatter **sub-object wiring semantics** — e.g. profile binding, exactly what `addModelNode` does to an existing model list, edge-case behaviour of `distributionLimitCoordSpace` | ❌ **UNVERIFIED** | `CHECKPOINT.md` §"Unverified". **Escalate for an orchestrator probe; never assume** |

> **`introspect_class` returns false negatives.** `introspect_class "CScatter"`-style probing is not how
> any claim here was established, and it must never be used as proof (`AGENTS.md` §"The one rule that
> matters most"). A class-existence claim ships with its control result.

---

## 2. The verified parameter map

Three groups. Everything in this table was recorded from execution (`PLAN.md` §4.1, `CHECKPOINT.md`).

### 2.1 Core wiring — what a scatter needs before it produces anything

| Property | Type | Meaning | Trap |
|---|---|---|---|
| `targetNodes` | node[] | the surfaces instances land on | Bind from `assembly.json.scatter[].target_ref`, a `massing.json` element id |
| `modelNodes` | node[] | the source geometry scattered | Bind from `model_refs`, a `components_registry.json` id **or** a `massing.json` element id |
| `modelFrequencies` | float[] | **one probability per model**, in `modelNodes` order | Length must equal `modelNodes.count`. `getModelCount()` and `getModelNode(i)` are the read-back |
| `seed` | integer 1…31337 | **deterministic** | **Never generated at run time.** Data or it is not reproducible |
| `instanceCountLimit` | integer | cap on instances | `> 0`. Read it with `getInstanceCount()` |
| **`distributionDesityPattern`** | number 0…1 | pattern modulation of the density | **The typo is real.** `distributionDensityPattern` does not exist |
| `distributionLimitCoordSpace` | — | which coordinate space the limit is expressed in | enum mapping **UNVERIFIED** — read it back, do not guess |

### 2.2 Placement ranges

| Property | Type | Note |
|---|---|---|
| `translationFrom` / `translationTo` | point3 | the random offset window |
| `rotationFrom` / `rotationTo` | point3 | **degrees**. Maps to `rotation_from_deg` / `rotation_to_deg` in `assembly.json` |
| `scaleFrom` / `scaleTo` | point3 | **unitless ratios** (`07` §2). Maps to `scale_from` / `scale_to` |
| `scaleUniform` | boolean | one scale for all axes |
| `rotationNormalAlignment` | — | align to the target surface normal |
| `rotationLookAt*` | — | look-at rotation family |

### 2.3 Constraints

| Property | Type | Note |
|---|---|---|
| `collisionAvoid` | boolean | maps to `assembly.json`'s `collision_avoid`, default **`true`** |
| `collisionStrictness` | float | how hard it avoids overlap |
| `collisionAvoidancePriority` | integer | relative priority between models |
| `altitudeLimitationEnabled` / `…From` / `…To` | boolean / float | with falloff curves |
| `surfaceSlopeLimitEnabled` | boolean | reject slopes beyond the limit |
| `edgeTrimmingEnabled` | boolean | keep instances off the target's border |
| `densityMap` | texture | a map drives density instead of a uniform value |
| `surfaceUv*` | — | `surfaceUvSpacingU/V`, `surfaceUvJitterU/V`, `surfaceRandomUseDensity` |

`surfaceRandomUseDensity` + `distributionDesityPattern` + `surfaceUvSpacingU/V` are how SKILL.md routes
static particle-like distribution onto Chaos Scatter now that no particle tool exists (§4).

---

## 3. The modifier-stack hazard — MEASURED, and it cost a reboot

**This is the single most important operational fact in this file.** It was not inferred; it was
measured deliberately on a clean empty scene at P6, 2026-10-05, one rung per call.

| rungs on one `Box` | result |
|---|---|
| 1 · 2 | `Extrude` and `Bevel` **throw** on `addModifier` (`mods=0`) — the P4b-r "6 unattachable modifiers" finding, re-confirmed. **Not a hang** |
| 5 | clean, 38 ms total |
| 10 | clean, 28 ms total |
| **20** | **`3dsmax-mcp_execute_maxscript` timed out; `3dsmax-mcp_get_scene_snapshot` then timed out; `3dsmax-mcp_get_bridge_status` then aborted. Max froze on the main thread, was killed, and the machine rebooted.** |

### 3.1 The binding rules

1. **≤ 5 modifiers per `3dsmax-mcp_execute_maxscript` call.** Chunk every emitted script.
2. **> 10 modifiers on a single node is forbidden** without asking the user first. Past 10, cut in
   separate passes — collapse the stack, or one modifier per node.
3. **The exact breaking point between 10 and 20 is not established and must never be re-measured.**
4. **A timeout is the only symptom.** No exception, no dialog, no error code. `Extrude` / `Bevel` on
   `addModifier` return promptly; a 20-stack returns nothing at all and the request simply times out.
5. **Never assume a timeout means "the bridge is down."** The scene may be alive and merely busy. Verify
   with a cheap `3dsmax-mcp_get_bridge_status` before concluding anything. A recoverable hang still burns
   the tool call, so verification costs you a second call — cheaper than the conclusion.
6. **The P4b-r hedge is retired.** The hang was originally hedged because **no Chaos Scatter object
   existed in the scene** during the event. The deliberate ladder reproduced it **with no Chaos Scatter
   object in the scene at all**, so the trigger is the geometry-stack change itself, not the scatter.

### 3.2 Why this belongs in a Chaos Scatter reference

Because it is the trap you will hit while building a scatter: Chaos Scatter is a **geometry object with
its own sub-object stack**, and a scatter pipeline invites "one more modifier on the host, one more on
the model". The ladder did not involve Chaos Scatter at all. Read §3 as a property of Max from this
build, not as a property of Chaos Scatter.

---

## 4. Absent tools, and the substitutions that work

These plugins are **not installed** in this Max: **forestPack, forestLite, tyFlow, railClone,
phoenixFD**. The following tools therefore **fail unconditionally. Never call them.**

| Absent tool family | Why it fails | Substitution — verified |
|---|---|---|
| `3dsmax-mcp_scatter_forest_pack` | forestPack / forestLite absent | **`ChaosScatter`** via `3dsmax-mcp_execute_maxscript`, wired with `targetNodes` / `modelNodes` / `modelFrequencies` / `seed` / `instanceCountLimit` (§2). `3dsmax-mcp_add_dc_script_operator` and `3dsmax-mcp_add_data_channel` are the *procedural-geometry* route, not a scatter route |
| all **14** `3dsmax-mcp_tyflow_*` tools — `3dsmax-mcp_create_tyflow`, `3dsmax-mcp_create_tyflow_preset`, `3dsmax-mcp_add_tyflow_event`, `3dsmax-mcp_add_tyflow_collision`, `3dsmax-mcp_connect_tyflow_events`, `3dsmax-mcp_modify_tyflow_operator`, `3dsmax-mcp_remove_tyflow_element`, `3dsmax-mcp_get_tyflow_info`, `3dsmax-mcp_get_tyflow_particles`, `3dsmax-mcp_get_tyflow_particle_count`, `3dsmax-mcp_reset_tyflow_simulation`, `3dsmax-mcp_set_tyflow_physx`, `3dsmax-mcp_set_tyflow_shape`, `3dsmax-mcp_list_tyflow_operator_types` | tyFlow absent | **Physics / motion:** PhysX or Max particles. **Static distribution:** Chaos Scatter with `surfaceRandomUseDensity`, `distributionDesityPattern`, `distributionLimitCoordSpace`, `surfaceUvSpacingU/V`, `surfaceUvJitterU/V`. **Animated motion:** keyframed MAXScript transforms plus `3dsmax-mcp_assign_controller` / `3dsmax-mcp_add_controller_target` / `3dsmax-mcp_set_controller_props` |
| `3dsmax-mcp_get_railclone_style_graph` | railClone absent | **RailClone-style patterning:** `3dsmax-mcp_clone_objects` in instance mode, driven by a MAXScript array. The verified instance route is `n = copy src` then `n.baseObject = src.baseObject` — **`setCopyMode` does not exist** |
| the whole `mcg_*` family (`3dsmax-mcp_...mcg...`) | no Max Creation Graph tool in the connected toolset | **Nothing substitutes.** Max Creation Graph is undrivable from this bridge. `references/procedural-graphs.md` is **half obsolete** as of 2026-10-06 — its **Max Creation Graph half is moot and its Data Channel half is LIVE** (six real `*_dc_*` tools), so it does **not** carry the whole-file OBSOLETE router that `curve-construction.md`, `railclone.md` and `tyflow-graphs.md` do. For the real 32-operator Data Channel vocabulary read `references/arch-modifiers-and-procedural-reference.md` |
| `3dsmax-mcp_curve_model` | absent from the live toolset | **Substitute: MAXScript shapes** — `splineShape` / `updateShape` / `splineOps`, documented in `references/maxscript-splines-shapes.md`. `references/curve-construction.md` is **OBSOLETE** as of 2026-10-06 (written against this tool; router at the top, body fenced non-executable) |
| `geometry_qa` · `contact_check` · `scene_qa` | these names do not exist at all | The real read-backs are `3dsmax-mcp_execute_maxscript` plus `FpInterface` (§5) |

**Rethink, don't emulate.** If a scatter recipe reaches for one of these, that is a **missing tool, not
a missing feature**. Record the gap and route to the substitution above — never hand-build a
substitute that no instrument will verify.

---

## 5. `FpInterface` — the read-back the hand-application uses

`FpInterface` is the **only** verified read-back path onto a Chaos Scatter object.

> **CORRECTED (2026-10-06):** this heading used to read "the P8 determinism hook", and the text below
> described `saveConfiguration` / `loadConfiguration` as the **P8 QA determinism hook**. **P8 was
> cancelled on 2026-10-05.** Nothing in the pipeline calls these functions. They are documented here
> because they are the **verified** way to inspect a scatter **after the user has applied it by hand**
> from `snippets/chaos_scatter.ms`, and because §5.1's round trip is a legitimate **optional manual
> verification** the user may run. **It is not a stage, not a gate, and nothing in S5 asserts it.**

| Function | Returns | Use |
|---|---|---|
| `getInstanceCount()` | integer | the census number. Read it **before and after** any re-apply |
| `getModelCount()` | integer | must equal the spec's `model_refs.count` |
| `getModelNode(i)` | node | assert `getModelNode(i) == modelNodes[i]` for every `i` — this is how you prove the models bound in the declared order |
| `update()` | — | force a re-evaluation after a parameter change, instead of assuming the viewport did it |
| `clear()` | — | drop the current instance set before a re-apply |
| `addModelNode(node)` | — | the Fp-side way to add a model; **`UNVERIFIED`** — prefer binding `modelNodes` wholesale and assert with `getModelNode(i)` |
| **`saveConfiguration(f)`** | — | snapshot the whole scatter configuration to disk |
| **`loadConfiguration(f)`** | — | restore it |

### 5.1 The round trip — an optional manual verification, not a pipeline gate

> **REFRAMED (2026-10-06).** This protocol was written as the S7 QA determinism gate. **S7 was cancelled
> on 2026-10-05**, so there is no stage that runs it and nothing depends on its result. It is kept
> because it is a complete, self-contained way for the **user** to confirm by hand that a scatter they
> applied from `snippets/chaos_scatter.ms` is reproducible — which is the one question a declared-but-
> unbuilt scatter leaves open. `MCPChaosScatter.determinismRoundTrip` (snippet §"optional manual
> verification") performs steps 4–10 in **one** call.

```
1.  set seed (the spec's integer, never a generated one)
2.  bind targetNodes / modelNodes / modelFrequencies
3.  update()
4.  n1 = getInstanceCount()
5.  saveConfiguration(<temp file>)
6.  clear();  rebuild from the same spec;  update()
7.  n2 = getInstanceCount()
8.  loadConfiguration(<temp file>);  update()
9.  n3 = getInstanceCount()
10. assert n1 == n2 == n3   -- otherwise the scene is NOT reproducible
```

**This was the replacement for the nonexistent QA tools** `geometry_qa` / `contact_check` / `scene_qa`,
none of which exist. Those tools are still nonexistent — **but no QA stage exists either**, so this is
now a user-facing convenience rather than the answer to a missing capability. `agents/max-assembly.md`
§7 row 8 **no longer** runs steps 5 and 9: that gate asserts the scene contains **no** `ChaosScatter`
node at all, because S5 deliberately does not apply one. **The former claim that "the protocol itself
belongs to P8 (`agents/max-qa.md`, planned)" is retracted** — P8 is cancelled and that file will not
exist.

> **A timeout during this protocol is not a determinism failure.** Check §3.1 rule 5 before drawing a
> conclusion, and never read `n1 != n2` as "the seed is ignored" without a `3dsmax-mcp_get_bridge_status` first.

---

## 6. How this maps onto `assembly.json.scatter[]`

`assembly.json` (`07` §8.5) is the **only** file in the spec chain carrying a scatter table. Per `07`
§11 + §12 it names **no MAXScript class, modifier, plugin or MCP tool** — a scatter row's identity is
`kind: "scattered"`, and the class name belongs to whoever applies the row. **CORRECTED (2026-10-06):**
this used to say "the builder owns the class name"; **the builder emits no scatter at all**, so the
mapping below is the **hand-application** contract — `ChaosScatter` is named by `snippets/chaos_scatter.ms`
and by the user, never by a builder. The mapping:

| `assembly.json.scatter[]` | Type / constraint | `ChaosScatter` property | Notes |
|---|---|---|---|
| `id` | `^SCT-\d{3}$`, unique, ascending | — | id space. It is the **declaration row's** identity — **never a node name**, because no scatter node is created by the pipeline |
| `node_name` | unique across **all four** arrays — `placements[]`, `opening_cuts[]`, **`wall_cells[]`** and `scatter[]` (`G-74`) | — | **CORRECTED (2026-10-06):** this used to read "the scatter node's name". **No scatter node is ever created by S5** — `assembly.ms` contains zero occurrences of `ChaosScatter`, `scatter` or `SCT_001` **[measured 2026-10-06]**. The field is the **name to give the node when the user applies the scatter by hand**, derived from the declaration row's `id` with dashes replaced, hyphen-free (`11` N1) |
| `target_ref` | a `massing.json` element id | `targetNodes` | the surface instances land on |
| `model_refs` | array, **≥ 1**; a `components_registry.json` id **or** a `massing.json` element id | `modelNodes` + `modelFrequencies` | one frequency per model; `getModelCount()` must equal `.count` |
| **`seed`** | **integer 1 … 31337** | `seed` | **Deterministic (P0).** Linted by **`G-78`**. A generated seed is a build defect, not a default |
| `instance_count_limit` | int `> 0` | `instanceCountLimit` | read back with `getInstanceCount()` |
| `distribution_density_pattern` | number 0…1 | **`distributionDesityPattern`** | **Spec uses the corrected spelling; the builder emits the typo.** P0 recorded the typo as the real MAXScript name |
| `scale_from` / `scale_to` | numbers, `0 < from ≤ to` | `scaleFrom` / `scaleTo` | **unitless ratios** (`07` §2), not centimetres |
| `rotation_from_deg` / `rotation_to_deg` | numbers, `from ≤ to` | `rotationFrom` / `rotationTo` | **degrees** |
| `collision_avoid` | bool, defaults `true` | `collisionAvoid` (+ `collisionStrictness`, `collisionAvoidancePriority`) | |
| `layer` | `"99_DEBUG"` for scatter sources | — | **DATA ONLY.** `99_DEBUG` carries no scatter payload as a *layer fact*; the scatter object sits wherever Max puts new geometry, which is expected and never "fixed" in the emitted script |

### 6.1 The worked example

> **Why this row once read three arrays and not four.** It read `placements[]`, `opening_cuts[]` and
> `scatter[]`, omitting `wall_cells[]` — added later, when solid wall tiling replaced the Boolean
> modifier. That is the **third instance in this repo of a rule failing to fire because the array it
> governs was added after the rule was written** (`G-81`'s scene census and `G-74`'s uniqueness sweep
> are the same shape). `scripts/place_components.py` carries the fix **and the comment explaining
> it**, and its sweep does iterate all four:
> `for table in ("placements", "opening_cuts", "wall_cells", "scatter")`. **A cell is a real scene
> node, so it carries every obligation a placement does** — including uniqueness against every other
> table, because the census counts nodes by name and two nodes sharing one would make that count a
> lie. **When a new array is added to `assembly.json`, re-read every rule that iterates the arrays** —
> a rule that no longer names the new array does not warn you, it just passes.
>
> ⚠️ **The lint side has not caught up, and this row is the spec, not a measurement of it.**
> `scripts/validate_specs.py`'s `_g74_node_names` still iterates **only three** —
> `("placements", "opening_cuts", "scatter")` — and its own docstring says so ("unique across the
> three tables"). So `validate_specs.py` does **not** enforce what this row states; only the
> build-time self-check in `place_components.py` does. `07`'s `G-74` invariant (§9) also lists all
> four, so the spec and the builder agree and **the validator is the outlier**. Fixing that is a
> `scripts/` change and is recorded here rather than made in a reference file.

The `pavilion-01` example ships **exactly one** scatter row. It targets the **`roof_deck`** element id
(`ground_pad` is **not** a `massing.json` element — `site_pad` is a separate object) with a **single**
model, a `column` element, so the 136-panel facade scene is not disturbed. `layer: "99_DEBUG"`.

### 6.2 Layer attribution is impossible from this bridge — and that is final

Not a Chaos Scatter matter, but it lands on this file because scatter rows carry a `layer` key.

**Nine routes are ruled out and this is not an open question** (`references/_p6-contract.md` §1.1,
`CHECKPOINT.md` §"Design consequences of the layer finding (P3 decision, closed at P6)"):
`LayerManager` exposes only `newLayerFromName` / `getLayerFromName` / `getLayer` and **no setter**;
`node.layer = <string>`, `= <integer index>` and `= <LayerProperties mixin>` all throw
`Property is read-only: layer`; `3dsmax-mcp_manage_layers`' action vocabulary is **exactly
`{list, create, delete}`** (40+ candidates rejected, including `rename`, for which the tool's own schema
carries a parameter); `3dsmax-mcp_set_object_property` with `property=layer` emits the same read-only
assignment and dies — with a **positive control** (`property=pos`) succeeding in the same batch.

**Therefore:** `layer_map` is declared and linted as **data**, and **no builder emits layer code**
(`G-79`). A builder that tries to apply layers is a **build FAIL**, not a silent no-op. Layer
application is a human action in the Layer dialog. `3dsmax-mcp_manage_layers` `create` is permitted for
the eight `07` §8.1.4 names' existence check; nothing else about layers is permitted.

---

## 7. `snippets/chaos_scatter.ms` — the **hand-application** library

> **This is the route the user is told to use.** `assembly.json` declares the scatter in data; S5 emits
> no scatter geometry; the user applies it from this snippet after the model is delivered. That is why
> the snippet is packaged and why its contract matters — it is a **human tool**, not a pipeline step.

The snippet is a **library of functions**, not a scene-changing script:

- **`fileIn`-able and it creates nothing on load.** No bare `ChaosScatter()`, no bare `Box()`, no `delete`
  outside a function body. That is the contract — a snippet that mutates the scene at load cannot be
  `fileIn`-ed safely from an emitted `.ms`.
- Every mutation lives in a named function: `apply`, `applyConfigFile`, `census`, `snapshot`,
  `restore`, `rebuild`, `dispose`.
- Every property write is **defensive**: `isProperty` guards, then a `try ( ) catch ( )`, so an
  unbindable property in a future build is reported instead of aborting the whole call. A partially
  applied scatter is a finding, not a success.
- **Apply is idempotent and re-appliable.** `rebuild` clears the instance set and re-applies from the
  same config — the re-apply-after-rebuild path, which is what makes the §5.1 round trip possible
  **for the user, by hand**.
- `seed` is clamped into **1 … 31337** deterministically, and `seedFromName` derives one from a string
  so a hand-wired scatter is still reproducible. **Never a run-time random.**
- `distribution_density_pattern` is written as `distributionDesityPattern` — **the typo is the real
  property name**, and `isProperty` is checked against it.

Load it, then:

```maxscript
fileIn @"D:\Rhino\3dsmax-arch-nurbs-ultimate-skill\snippets\chaos_scatter.ms"
local cfg = MCPChaosScatter.config(seed:1234, instanceLimit:2000, densityPattern:0.6, collisionAvoid:true)
MCPChaosScatter.create "SCT_001"
MCPChaosScatter.apply (getNodeByName "SCT_001") cfg targetNodes:#(roofDeck) modelNames:#("EL_004")
MCPChaosScatter.census (getNodeByName "SCT_001")      -- (instances, models, indexOK)
```

---

## 8. MAXScript traps that apply here specifically

| Trap | Consequence | Do instead |
|---|---|---|
| The property is **`distributionDesityPattern`** | `distributionDensityPattern` silently does not bind | Emit the typo. Guard with `isProperty` |
| `CScatter` is **NotCreatable** | `CScatter()` throws | Always `ChaosScatter()` |
| `try { } catch { }` | **Parse error** in this dialect | `try ( ) catch ( )` |
| `getCurrentException()` inside a `catch` | Throws itself | Never call it |
| `("x" + i as string)` | Throws on precedence | `("x" + (i as string))` |
| `for o in objects do delete o` | **Silently skips entries** — 24 orphans at P5 | Collect names, delete by name, **run twice** |
| `stopCreating <node>` | Wrong arity → `Argument count error: StopCreating wanted 0` | `stopCreating` takes **0** args |
| `modifiers <node>` as a function | Does not work | Use the `node.modifiers` **property** |
| A standalone modifier | Not a node; **cannot be deleted** | Attach it to a node and delete the node |
| `fileExists` · `executeFile` · `runScript` | Absent names | `doesFileExist` · `fileIn` |
| `setCopyMode` · `rotationZ` / `rotationX` / `rotationY` · `matrix3` · `angle` · `findString` | Absent in this build | `copy` + `baseObject =` · `quat <deg> [0,0,1]` · `substring s 1 n` |
| `node.pos` on a `Box` | **Base** sits at `pos.z` (geometry centres on x/y) | `pos.z = cz − height/2` to centre |

---

## 9. Anti-patterns

| Anti-pattern | Instead |
|---|---|
| **AP-1 · Reaching for `3dsmax-mcp_scatter_forest_pack`** because a scatter recipe names it | forestPack is absent. `ChaosScatter()` via `3dsmax-mcp_execute_maxscript` (§2, §4) |
| **AP-2 · Reaching for any of the 14 `3dsmax-mcp_tyflow_*` tools** | tyFlow is absent. Chaos Scatter + `surfaceRandomUseDensity` for static distribution; PhysX / Max particles for physics; controllers for animated motion (§4) |
| **AP-3 · Reaching for `3dsmax-mcp_get_railclone_style_graph`** to pattern a facade | railClone is absent. `3dsmax-mcp_clone_objects` instance mode, or `copy` + `baseObject =` in a MAXScript array (§4) |
| **AP-4 · Reaching for `mcg_*` or `3dsmax-mcp_curve_model`** | Neither family exists in the connected toolset. Nothing substitutes. Record the gap; do not emulate |
| **AP-5 · Writing `distributionDensityPattern`** | The real name is **`distributionDesityPattern`**, typo included (§2.1) |
| **AP-6 · Constructing `CScatter`** | It is **NotCreatable**. Always `ChaosScatter()` |
| **AP-7 · Generating a `seed` at run time**, or leaving it at the default | `seed` is 1…31337 and is **data** in `assembly.json`. A generated seed fails `G-78` and makes the §5.1 comparison meaningless |
| **AP-8 · Adding modifiers to the scatter node or its models without counting them** | §3. 5 and 10 are clean; **20 froze Max permanently and cost a reboot.** ≤ 5 per call, > 10 per node forbidden, and the break point must never be re-measured |
| **AP-9 · Reading a timeout as "the bridge is down"** | §3.1 rule 5. `3dsmax-mcp_get_bridge_status` first. A recoverable hang burns the call but the scene is alive |
| **AP-10 · Naming `geometry_qa`, `contact_check` or `scene_qa`** as the verification | Those tools do not exist — **and no QA stage exists either** (P8 cancelled 2026-10-05). The read-back, once the user has applied the scatter by hand, is `FpInterface` + `getInstanceCount()` (§5) |
| **AP-11 · Asserting instance count against a number the spec never declared** | Record the number that came back. Only `instance_count_limit` is a declared bound, and it is a cap, not an expectation |
| **AP-12 · Emitting layer code for a scatter row** because it declares `layer: "99_DEBUG"`** | §6.2. Nine routes ruled out; layer is data and the build **FAILs** (`G-79`) |
| **AP-13 · `fileIn`-ing a snippet that mutates the scene on load** | `snippets/chaos_scatter.ms` creates nothing at file scope by contract (§7). A load-time mutation cannot be undone by a failed build |
| **AP-14 · Assuming `addModelNode` semantics** | **UNVERIFIED** (§1). Bind `modelNodes` wholesale and assert with `getModelNode(i)` |
| **AP-15 · Concluding a rebuild is non-deterministic from one `n1 != n2`** | Run the full §5.1 protocol, and check `3dsmax-mcp_get_bridge_status` for a hang before believing it |

---

## 10. Sources

| Source | What it contributes |
|---|---|
| `PLAN.md` §4.1 | The verified parameter map, the classIDs, the `FpInterface` surface, the determinism hook |
| `CHECKPOINT.md` §"Chaos Scatter" · §"Tooling that always fails — never call" · §"RESOLVED at P6 by deliberate bounded ladder" · §"Design consequences of the layer finding (P3 decision, closed at P6)" · §"Unverified — must be checked before use" | The transcripts of record |
| `references/_p6-contract.md` §1.1 · §1.2 · §3.4 | The layer negative, the measured hazard, the `scatter[]` schema |
| `references/02-mcp-live-orchestration.md` §2.4 | The `ChaosScatter` / `CScatter` routing entry and its substitutions |
| `SKILL.md` | The routing table row and the determinism recipe |
| `AGENTS.md` | The modifier-stack ladder, the absent MAXScript names, the instance route, the `node.pos` rule, the tool-name collisions |
| `snippets/chaos_scatter.ms` | The apply / re-apply / census / snapshot library |