# max-nurbs — S3: locked `nurbs.json` → `nurbs.json` + `nurbs.ms` + NURBS nodes in 3ds Max

> **Purpose:** S3 is the stage that builds **curved** geometry. It reads the locked spec set S2 handed
> over, writes `nurbs.json` (`07` §8.2 — surfaces, their section lattice, and their derivatives),
> emits the MAXScript that builds it, **executes that script in live 3ds Max**, measures what came
> back, and cleans up. **S3 builds NURBS surfaces and the derivatives computed from them.** Massing,
> facades and everything after are other stages' work. **CORRECTED (2026-10-06):** this used to read
> "Massing, facades, **materials** and everything after are other stages' work." **There is no materials
> stage — S6 was cancelled on 2026-10-05** and the user applies materials by hand after delivery.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage · Input | **S3** — the curved-geometry build stage (`01` §"S3", `PLAN.md` §4 row P4) · `specs/pipeline/massing.json` and `dimensions.json`, plus `assumptions.json` / `conflicts_resolved.json` |
| Output | `nurbs.json` (`07` §8.2) and the builder's `nurbs.ms`, then the nodes that script creates |
| Geometry produced | one NURBS node per `surfaces[]` entry · one node per `derivatives[]` entry (`quad_panels` mesh, `space_frame` spline cage) · **no dummies, no grouping** — grouping is S2's |
| 3ds Max calls | `3dsmax-mcp_execute_maxscript` — **mandatory**, and it is the **orchestrator's** call, not a subagent's (§4 steps 6–8). **No probes** (§1.2) |
| Consumer · Precondition | S4a/S4b → S5, which is **the last stage** · S2 complete and locked (`07` §9.6 `G-34`…`G-40` PASS) |
| Blocked by | A `nurbs.json` that is not `locked`. Full stop (§2.2) |
| Findings | See `agents/max-orchestrator.md` §6.2. If this session produced a real finding — a measured value outside `tolerances.linear_cm`, a surface or relation the `nurbs.json` kinds cannot describe, or a lattice value that is legal but wrong for this building — record it in `<project>/IMPROVEMENTS.md`. **A session with no findings writes nothing and creates no file.** Format: `references/improvement-log.md` |

### 1.1 What S3 owns, and what S3 defers

S3 builds exactly **eight** `kind`s and two `derivative` kinds: `u_loft`, `uv_loft`, `point_grid`,
`cv_grid`, `rail_sweep`, `two_rail_sweep`, `blend`, `trim`; `quad_panels`, `space_frame`. One primitive
underlies all eight: **an ordered list of point rows** (`sections[]`) — a loft's rows are its sections, a
grid's rows are its lattice, and a **rail and a trim profile are rows too**. That is why there is one
`sections[]` table, no per-kind geometry syntax, and no second `relations` table: a relation is an
ordinary `surfaces[]` entry that *refers* to other surfaces by id. The last four kinds arrived at P4b;
their keys and defaults are §6.7.

| **Never** built by S3 | Consumed by | Correct instrument |
|---|---|---|
| Massing solids, slabs, columns, core walls, plinths | **S2** | `massing.json`. A Z-prism is not NURBS |
| Rail sweeps, blends, trim, project-vector curves, any relation between two surfaces | **S3 — since P4b** | `rail_sweep`, `two_rail_sweep`, `blend`, `trim` are `surfaces[]` kinds in `07` §8.2.7, with keys in §6.7 and `G-50`…`G-54`. **These are S3's own work, not an escalation and not "not implemented"** — the four classes construct, commit, evaluate and expose their relational keyword sets |
| Surface closure as a per-surface flag (`closed_u` / `closed_v`) | **nobody** | No surface class in this build has `closeU`/`closeV` at all (`NURBSPointSurface().closeU` → `Unknown property`). Closure is `closed_sections`, one flag per loft |
| Knot vectors, `relations[]` edges | **nobody** | Knots are derived from `order` and count; `relations` is not in the schema. A spec that declared them would be declaring something the builder overwrites |
| Facade panels on a curved wall, glazing, mullions | **S4a / S5** | `facade_grids.json`, `components_registry.json`, `assembly.json` |
| Materials, renderers, UV authoring | **nobody — S6 was cancelled 2026-10-05** | **Applied by hand by the user**; the hand-off is `agents/max-orchestrator.md` §5. `materials.json` is a **reserved stub**, not a deliverable and not a gate. `mat_id` is a sub-material index, data only — and data nothing reads |
| Layer **application** to any node | **nobody — permanently** | **There is no way to assign an object to a layer from this bridge. Nine routes are ruled out and this is final, not an open question** (`agents/max-assembly.md` §6.3) — the six originally executed, `LayerManager`'s missing setter, `manage_layers`' vocabulary being **exactly `{list, create, delete}`**, and `set_object_property`. **Layer is data; the user applies it in the Layer dialog** |

### 1.2 The one-MCP rule

**You may execute the emitted `nurbs.ms` and read state back. You may not probe** — and at S3 the
boundary is stricter than at S2, because **the live execution belongs to the orchestrator**.

| Allowed | Forbidden |
|---|---|
| The orchestrator running `3dsmax-mcp_execute_maxscript` with `fileIn "<abs path>/nurbs.ms"`, then one read-back call | **Any exploratory probe of your own.** A fact not in `CHECKPOINT.md` §"Verified facts" is escalated for an orchestrator probe, never opened by S3 (`01` §"S3") |
| `3dsmax-mcp_get_scene_info` / `_get_scene_snapshot` to confirm the scene holds what the spec says | A second Max call from a subagent "just to check". Max is single-threaded; concurrent calls are how the session is corrupted |
| `3dsmax-mcp_delete_objects` on nodes you created, in the same call | Every tool in `01` §1.2 — the forestPack / `tyflow_*` / RailClone group and the Rhino-server names (`get_objects`, `loft`, `sweep1`, `pipe`, `analyze_objects`, every `gh_*`) |
| `3dsmax-mcp_capture_viewport` for a human-facing record, after measuring | `3dsmax-mcp_introspect_class` / `_introspect_instance` / `_inspect_plugin_class` as **proof**. They both fail on the NURBS surface classes (`Unknown class: NURBS1RailSweepSurface`). Introspection is a hint, never proof |

Executing an already-verified emitted script is **not** a probe (`01` §6).

> **One trap worth stating before you read anything:** a NURBS **dependent** surface's relational
> properties are populated only once the sub-object is **committed** inside a `NURBSNode`. Read them on
> a freshly constructed, unattached object and *every* name fails — including the four that do exist.
> That single pre-commit read is what produced the false "rail sweeps and blends are not implemented"
> finding this stage used to carry. The rule is in §6.7; the commit is part of the measurement.

---

## 2. Inputs and outputs

### 2.1 What you read

| Source | What you take from it |
|---|---|
| `specs/pipeline/massing.json` | **The contract you build from** — `storeys[].z_range_cm`, `elements[].z_range_cm`, `roof.deck_level_cm`, `site.footprint_*` |
| `dimensions.json` · `assumptions.json` · `conflicts_resolved.json` | `levels[]`, `structure.*_bay_cm`, `column_section_cm`, `floor_plates[].thickness_cm`, `roof.*` — and every `A-nnn` whose provenance touches a surface |
| `references/07-spec-grammar.md` | **§8.2** the schema in full · **§8.2.7** the four dependent kinds · **§8.2.8** what a spec may not encode · **§9.7** `G-41`…`G-54` · §3.1 the lock gate · §5.2 `origins` granularity · §2 units · §9.5 exact counts |
| `references/11-layer-standard.md` | §1 the eight layer names · §2 `kind` → layer · **§3.1 naming, N1–N5** · §6 the delivery checklist H1–H12 |
| `snippets/nurbs_arch_library.ms` | The 12 functions you may call. **Read it; do not patch it** (§3) |
| `scripts/build_nurbs.py` · `scripts/validate_specs.py` | The two CLIs. Read their `--help`; never guess a flag |
| `CHECKPOINT.md` | §"Verified facts" — **the transcript of record** for §6 and §7 |

### 2.2 What you own, and the lock gate

| Path | Action |
|---|---|
| `<project>/specs/pipeline/nurbs.json` | **Emitted by the builder.** Never hand-written, never hand-edited |
| the builder's `nurbs.ms` output path | **Emitted by the builder.** Never hand-written, never hand-patched |
| `specs/recipes/*.json` | **You own this directory** — four templates, §13. They are `draft`, they are read-only inputs to a build, and they are never consumed as a project's spec |

**You modify nothing else** — not `references/`, not the two `scripts/`, not `examples/`, not
`snippets/`, not the other `agents/`, not `CHECKPOINT.md`, not S2's locked files.

> **A builder must refuse any spec file whose `status` is not `locked`, naming the file and the status
> it found** (`07` §3.1). Exit non-zero. Checked before anything else is read.

| Found | Action |
|---|---|
| `status: "draft"` or `"superseded"` | **Refuse**, and report that path and status verbatim. `--allow-draft` is an **inspection** flag (§2.3) |
| `source.kind` is not `derived`, or `source.reference` does not name the `massing.json` this file was computed from | **Refuse.** `G-6` requires a `derived` source to name a spec file that exists in the project; a `nurbs.json` that did not come from a `massing.json` has no audit trail |
| `origin_inputs` paths that do not resolve in `dimensions.json` or `massing.json` | **Refuse.** `G-31` / `G-49` — this is a cross-file check and the file is computed from `massing.json`, so **both** hosts are legal targets (`G-36` resolves in `dimensions.json` only; `G-49` widens it) |
| `schema_version` major you do not implement | **Stop.** Do not guess |

A `draft` upstream file is not your failure to fix, and not a reason to build "just the ready parts".

### 2.3 What `--allow-draft` is for, and what it is not

| Flag | Effect | S3's use |
|---|---|---|
| `build_nurbs.py --allow-draft` | **Waives the lock gate** so the invariants *run*. It does not relax them | Inspecting a draft during authoring. The emitted file is **not a deliverable** |
| `validate_specs.py --allow-draft` | The same waiver, for linting | Reading `G-41`…`G-49` rows on work in progress |
| `build_nurbs.py --build` | Present for CLI symmetry with the validator. **This builder always enforces the gate** | You may pass it; it changes nothing |
| neither | The gate is enforced and a non-`locked` file exits non-zero | **Every real build** |

**`--allow-draft` will not produce a shippable file.** `G-49` is the rule that answers: a `nurbs.json`
is *computed* from `massing.json`, so a draft carries provenance that was never resolved against a
project. Forced to run, `G-49` fails on that; with the upstream project absent it honestly SKIPs
instead, naming what it could not evaluate. **Both outcomes mean the same thing: unproven.**

---

## 3. File ownership

| Artifact | The contract you may rely on |
|---|---|
| `scripts/build_nurbs.py` | Exposes `--in <dir> --out <dir> [--json] [--build] [--allow-draft]`; reads `<in>/nurbs.json`; writes `<out>/nurbs.json` and `<out>/nurbs.ms`; refuses non-`locked` input with non-zero exit; self-checks `G-41`…`G-54` **before writing**, and refuses to write a file for which the self-check produced no row at all. On a dependent surface it also emits the **`G-54` census** (§6.7) and refuses to write a `.ms` whose census counts by literal index |
| `scripts/validate_specs.py` | Flags `--dir --file --json --rule --warnings-as-errors --build --allow-draft` |
| `snippets/nurbs_arch_library.ms` | 12 functions, all 12 executed live 2026-10-04. **Zero open bugs.** It is not a rewrite target. Note the four dependent kinds need **no** library function — the builder emits their classes directly (§6.7.4) |
| `examples/nurbs.json` / `examples/nurbs.ms` | The `pavilion-01` worked case — the four measured numbers in §6.2 come from it. It contains **no dependent surface**, so `G-50`…`G-53` are *vacuously* satisfied there and `G-54` SKIPs. That is the honest state, not a pass |

**S3 owns `specs/recipes/`. Nothing else does** (`01` row 12: outside the chain, only S3 reads or
writes it).

> **Measured, and it constrains the recipes.** `validate_specs.py` resolves a record's schema from its
> **file stem**, not from its `spec` key (`load_session` → `SPEC_BY_NAME.get(path.stem)`), and `G-2`
> requires `spec` to *equal* the stem. A recipe is therefore **ignored** by the validator — reported
> as `G-1 SKIP … not a file in the 07 section 4 inventory … ignored` — and `build_nurbs.py` refuses it
> outright with `declares spec 'barrel-vault', not 'nurbs' (07 G-2)`. Instantiating a recipe means
> copying it to `<project>/specs/pipeline/nurbs.json` **and rewriting `spec` to `"nurbs"`** (§13.2).
> Do not "fix" this by renaming a recipe to `nurbs.json` in place; four files cannot share one name.

---

## 4. Procedure

Ordered and deterministic. Each step has a pass condition.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Verify the input is locked** | Read the six envelope keys of `massing.json` and of `nurbs.json`. Apply §2.2 in full | Both `locked`, `project` agrees, `units.length == "cm"` |
| 2 | **Read `massing.json` into the surface model** | Read §2.1 once, in order. Take `tolerances` **verbatim** — a builder may not widen them. A springing level from `storeys[1].z_range_cm[1]`; a plan extent from `site.footprint_*`; a bay from `structure.*_bay_cm`; a shell from `floor_plates[i].thickness_cm` | Every value used is a real key path. **Every `origins` entry is `derived`** (`G-49`) — S1 and S2 already resolved `given` / `assumed` / `conflict` |
| 3 | **Classify each candidate against §6** | Each surface is exactly one of the **eight** kinds in §6.1. Every section belongs to ≥ 1 surface (`G-44`) | Every refusal recorded with the surface id and reason, and escalated (§10). **A form that needs a rail sweep, a 2-rail sweep, a blend or a projected trim is S3's own work, not an escalation** — classify it, write the keys §6.7 states, and build it (§6.7) |
| 4 | **Emit `nurbs.json` and `nurbs.ms`** | Run the builder (§5). **You do not hand-write either file.** Then read `nurbs.json` back from disk and verify it independently — recompute one arc or one lattice Z by hand and compare | The file matches your hand computation at `tolerances.linear_cm`; the section set matches what you derived |
| 5 | **Validate** | `python scripts/validate_specs.py --dir <specs_dir> --build` | Exit **0**. `G-41`…`G-49` **PASS** or **SKIP with a stated reason** — see §8 row 2 |
| 6 | **Run in 3ds Max** | §7. One script per call, under ~2 s. **The orchestrator runs this, not a subagent** | Returns without error; the scene holds the expected nodes |
| 7 | **Measure** | §8. Node count, names, `node.min` / `node.max`, parameter domains, and the **evaluated** surface against the lattice | Every node present and named; the four numbers in §6.2 explained by what came back |
| 8 | **Clean up, then report** | §9. Delete what you created in the same call, then return §12 | Only the S3 nodes remain; the report is under the §12 cap |

**Determinism.** The same locked spec must yield byte-identical `nurbs.json` and `nurbs.ms`. Node names
are the spec `name` verbatim (they already satisfy N1 — the ids carry no `-` because the *names*
replace them), so a rebuild yields the same node-name set (`11` N3/H10).

---

## 5. The build commands

```
python scripts/build_nurbs.py --in <specs_dir> --out <out_dir>
python scripts/build_nurbs.py --in <specs_dir> --out <out_dir> --json
python scripts/validate_specs.py --dir <specs_dir> --build
```

| Aspect | Contract |
|---|---|
| Reads | exactly one file, `<in>/nurbs.json` — this builder has **no stage selector**, unlike `build_spec.py` — plus `dimensions.json` and `massing.json` **optional** — absent, they degrade `G-49` to a SKIP with a reason rather than a false PASS |
| Writes | `<out>/nurbs.json` and `<out>/nurbs.ms`. `--out` defaults to `--in`; `--json` gives a machine-readable report on stdout, including `surface_index_strategy` and the self-check tally |
| Exit **0** | The lock gate passed **and** the `G-41`…`G-54` self-check produced no failure |
| Exit **non-zero** | A refusal naming the reason — the file path and the `status` found, the `G-` id that fired, or the list of failed invariants |
| Determinism | Byte-identical output for byte-identical input |
| Layer code | **None.** `nurbs.ms` is geometry only. Adding layer code is a defect, not an improvement — it cannot work (§7) |
| Surface index | **No literal index is ever emitted.** The builder emits a resolver that walks `getNURBSSet node #relational` and takes the **first** object with `superClassOf o == NURBSSurface`, and **throws** naming the node if there is none. **It never filters by comparing an index against a pre-commit ordinal** — the two numbering schemes differ (§6.7.6) — and a dependent relation is matched by `classOf`, not by superclass alone (§6.4.1) |
| `G-54` census | Emitted **only when a dependent surface exists**, so every pre-P4b spec's bytes are unchanged. It counts the node's `NURBSSurface` sub-objects **after `NURBSNode` + `stopCreating`** and throws a named error naming the **node, the expected count and the actual count**. This is the one part of the build that cannot be verified offline — only the live run resolves it (§6.7) |

**A non-zero exit is a stop**: fix the spec through S2 (§10) or the builder through its owner (§3).
Never rename a key, widen `tolerances`, drop a leaf, delete a section, or lower an order to silence a
`FAIL`.

---

## 6. Geometry rules

### 6.1 The eight kinds — four independent, four dependent

| `kind` | Construction | Keys it carries | Right when |
|---|---|---|---|
| `u_loft` | `createULoftShell` (F6) — section rows lofted along U, optional parallel offset shell | `section_ids` (≥ 2, ordered) · optional `closed_sections`, `thickness_cm` | A **vault, a canopy shell, a swept roof**: a family of parallel profiles you can name one by one. The only kind that takes a shell |
| `uv_loft` | `createUVLoftNetwork` (F7) — a Gordon network from two crossing curve families | `u_section_ids` (≥ 1), `v_section_ids` (≥ 1) — **not 1 in both** (`G-45`) | A **doubly-curved** form whose curvature in U and V is decided independently: a funnel roof, a hypar canopy, a twisted soffit. The families must actually cross |
| `point_grid` | `makePointSurfaceGrid` (F11) | `section_ids` (≥ 2, ordered **as rows**) | **The lattice is the design intent** — a dome ring grid, a freeform plaster soffit, a point-sampled survey. The surface passes through every point you gave it |
| `cv_grid` | `makeCVSurfaceGrid` (F12) | `section_ids` (≥ 2, as rows) · optional `u_order`, `v_order` (2–5), `weights` | **The lattice is a control cage** — a ruled blend between two profiles, a form whose extremes must be bounded. The surface only *pulls* toward the interior points |
| `rail_sweep` | `NURBS1RailSweepSurface rail:<i> parallel:<b>`, then one `appendCurve` per cross-section (§6.7.4) | `rail_section_ids` (**exactly 1**) · `section_ids` (≥ 2, ordered) · optional `parallel` | A skin swept along **one** spine — a ramp soffit, a rolling roof, a canopy on a single curved rail. Every cross-section must meet the rail within `linear_cm` (`G-51`) |
| `two_rail_sweep` | `NURBS2RailSweepSurface rail1:<i> rail2:<j> parallel:<b>`, then one `appendCurve` per cross-section | `rail_section_ids` (**exactly 2**, ordered) · `section_ids` (≥ 2, ordered) · optional `parallel` | A skin between **two** rails — a bridge deck, a ridge canopy — where the section width adapts to the rail separation |
| `blend` | `NURBSBlendSurface parent1ID:<id> edge1:<n> parent2ID:<id> edge2:<n> tension1:<f> tension2:<f>` — the ids are bound from the committed parents (§6.7.4) | `parent1_ref` · `edge1` (`1..4`) · `parent2_ref` · `edge2` (`1..4`) · `tension1`, `tension2` | A G1/G2 transition between **two surface edges** — soffit into wall, shell into soffit. Both parents must be declared **earlier** in the file (`G-52`). `tension1`/`tension2` are **`0.0`** unless the spec states otherwise (§6.7.1) |
| `trim` | `NURBSProjectVectorCurve parent1ID:<id> parent2:<j> pVec:[…] seed:[…] trim:false flipTrim:<b>` | `surface_ref` · `trim_section_ids` (≥ 1 closed profile) · `p_vec` `[x,y,z]` · `seed` `[u,v]` · `flip_trim` | A closed profile row **projected onto a surface along a vector**. **Projection only — this class does not cut.** An aperture needs a Boolean modifier or a surface split, which is not this stage (§6.7.5) |

Both grid kinds take orders with `amin #(order, count)`: **an order larger than the count is silently
clamped.** That is why `G-46` fails the spec rather than letting the library quietly build something
else. `weights` is one flat row-major array, index `(iv − 1)·nU + iu`, missing entries `1.0`.
`grid[iv][iu]` for both: `iv` = row, `iu` = column.

**The dependent four differ in one structural way: a surface may now depend on other surfaces in the
same file.** `parent1_ref` / `parent2_ref` / `surface_ref` name `SUR-nnn` ids **declared earlier**,
following the `derivatives[].surface_ref` convention (`G-52`). Rails and trim profiles are ordinary
`sections[]` rows — **no new primitive, no second table**. `edge1` / `edge2` are `1..4` = low-U, high-U,
low-V, high-V.

**A relation references its parents by `nurbsID` and does NOT re-instantiate them.** The parent surface
is committed in **its own node**; the relation's set then holds only the relation sub-object (§6.7.4).
Re-instantiating the parent inside the dependent set — which is what the builder emitted before
2026-10-04 — puts a parent named by two relations into the scene **three times**, and a `trim:true`
relation copies the whole parent shell into its own node. `G-50` still refuses by name any parent whose
kind the builder cannot build uncommitted — that is `u_loft`, `uv_loft`, `point_grid`, `cv_grid`, and
nothing else. A `u_loft` parent is built as its base surface only; its `thickness_cm` shell is a
property of its own node and plays no part in an edge.

Both sweep kinds are measured at a `[0,1]` domain, like `cv_grid` and unlike a `point_grid` (§6.2).

> **The standing rule, unchanged by P4b: a spec never names a MAXScript class, plugin or tool.** All
> eight names above are **geometric**. The `Construction` column names the class or library function an
> agent may expect the builder to emit — it is evidence about the implementation, **never** a field you may
> write into `nurbs.json`. A builder that met `rail_sweep: "NURBS1RailSweepSurface"` would have to ignore
> it, which is the v2 failure mode (`07` §12, §13.1).

### 6.2 `point_grid` and `cv_grid` are not interchangeable — four measured numbers

Two canopies on the **same 600 × 450 cm footprint**, nominally identical in extent, sampled off the
same divisions. `examples/nurbs.json`: `SUR-002_Canopy` is a `point_grid`, `SUR-003_CanopyCage` is a
`cv_grid`.

| | `point_grid` (`SUR-002_Canopy`) | `cv_grid` (`SUR-003_CanopyCage`) |
|---|---|---|
| Lattice peak | **510 cm** | **480 cm** |
| Node bounding-box max Z | **568.226 cm** — 58 cm **above** the lattice, reached *between* lattice points | **480 cm** — exactly the convex hull; it can never exceed it |
| Sampled surface max Z | **515.998 cm** | **448.125 cm** — 32 cm **below** the lattice it was given |

> **These four numbers are the whole argument, and they are measurements, not theory.** An
> **interpolating** surface **overshoots** the points you gave it; a **controlled** surface
> **undershoots** them. The parameter domains differ too: `point_grid` is **chord-length** parametrised
> — measured `u = [0, 434.555]`, `v = [0, 307.439]` for a 400 × 300 cm lattice — while `cv_grid` is
> normalised `[0, 1]`. **Never assume `[0, 1]`.**

**The QA consequence, and it is not optional: any comparison of the surface against the lattice must
compare the *evaluated* surface, never the lattice against itself** (`07` §8.2.3). A check that samples
the lattice and compares it to the lattice passes a surface that is 58 cm out of position.
**CORRECTED (2026-10-06):** this sentence used to say "asserted by P8". **P8 (S7, automated QA) was
cancelled on 2026-10-05**, so no automated check asserts it. **The rule stands for whoever measures this
surface** — S3's own gate does — and it is the user's to apply if they measure it themselves.

### 6.3 The commit rule

**A surface is not evaluable until it has produced a `NURBSNode`.** Before commit — a surface
`appendObject`-ed to a `NURBSSet` but with no node — `uParameterRangeMin` / `Max` read `0.0` and
`evalPos` returns `undefined`. After commit they read their real domain. Both grid functions and both
loft functions commit for you; **a derivative you build by hand must commit too**, or it samples a
surface that returns `undefined` and you get a plausible-looking empty mesh.

**The commit rule covers `nurbsID`, not just the relational keywords and `evalPos`.** A `nurbsID` is
only obtainable from a **committed** sub-object — `parent1ID:` must be bound after the parent node
exists, never before it. Reading an id from an uncommitted surface is not a weaker read than reading
`rail`; there is simply nothing to read. The full order is in §6.7.4 and it is not rearrangeable:

> **build → `appendObject` → `NURBSNode` → read.** Everything you read — `evalPos`, the parameter
> domain, `rail` / `parent1` / `tension1` / `trim` / `seed`, **and `nurbsID`** — is read on the
> committed sub-object. Nothing before that line is readable, and nothing before it may be used as an
> argument to anything.

`appendObject` returns the string `"OK"`, **not an index.** If you need the index of what you just
appended, read `nset.numObjects` after the call.

### 6.4 The sub-object-index trap — resolve by superclass, never by a literal index

Indices are **not predictable**, and this is not a style preference:

| Surface | Measured sub-objects | Design surface index | Last index |
|---|---|---|---|
| a 5 × 3 `point_grid` | 15 `NURBSPoint`, **then** the surface | **16** | 16 |
| the 5-rib vault `SUR-001_Vault` (`thickness_cm: 25.0`) | **52** | **51** — the design soffit | **52** — the offset shell |

A `point_grid` contributes one `NURBSPoint` sub-object per lattice point **before** the surface, so
its index is `nU·nV + 1`. A `cv_grid` puts the surface at 1. A `u_loft` / `uv_loft` interleave curves
and surfaces. **A derivative must read the *first* `NURBSSurface`.** On a shelled surface the **last**
one is the offset, and sampling it is a **silent 25 cm error**: on `SUR-001_Vault`, sampling the first
gives panels spanning `z 420 → 600.97` and sampling the last gives `441.043 → 625.94`. **That rule holds
for the four independent kinds in §6.1 — and for a sweep, but not for a blend.** Read §6.4.1 before
applying it to any dependent surface.

```maxscript
-- the shape the builder emits; the only correct resolution
fn mcpNurbsSurfIndex node label = (
    local rset = getNURBSSet node #relational
    local found = 0
    for i = 1 to rset.numObjects do (
        local o = getObject rset i
        if superClassOf o == NURBSSurface do ( found = i; exit )
    )
    if found == 0 do throw ("build_nurbs: " + label + " carries no NURBSSurface sub-object; a surface index cannot be guessed")
    found
)
```

`MCP_NURBS_Arch.inspectNURBSSet node` (F8) prints every sub-object with its index, class, superclass
and parameter range — **the cheap way to see what a build actually contributed.**

#### 6.4.1 …but the design surface is not always the *first* one

Resolving by superclass settles *which class*; it does not settle *which member of that class*. In a set
of N `NURBSSurface` sub-objects, the design surface may be the **first** or the **last**, and the two cases
are silently wrong in opposite directions:

| Set | Where the design surface is | What "first match" costs you |
| :--- | :--- | :--- |
| a `u_loft` with `thickness_cm` — a `NURBSOffsetSurface` is appended **after** the base loft (§6.5) | **first** | Sampling the last samples the shell — a silent `thickness_cm` error, measured `z 420 → 600.97` against `441.043 → 625.94` |
| a `NURBS1RailSweepSurface` / `NURBS2RailSweepSurface` — the sweep is the surface the whole set was built to produce (§6.7) | **first** | — |
| a `NURBSBlendSurface` — it is built **on top of** two parent surfaces that are already in the set, and measured as **3** surfaces for two point surfaces plus the blend | **last** | First match returns a parent, so the derivative samples the wrong surface and every number is plausible |
| a `NURBSProjectVectorCurve` set — **corrected 2026-10-04.** Earlier revisions recorded "two surfaces where one was expected" and called it unmeasured. The second surface is the **parent's untrimmed `NURBSCVSurface` copy**, added by the relation; it is not a cut (§6.7.5) | **0 surfaces** under `trim:false` — the relation contributes a curve only | Anything that counted "2" as the expected trim shape was counting the parent's own shell |

So the rule has two halves and **both are required**:

1. **Resolve by `classOf o == <the dependent class>`** — never by a literal index (§6.4), and never by
   comparing an index against a pre-commit ordinal (§6.7.6).
2. **Confirm the resolved sub-object carries the relational properties you just set** — `parent` / `rail`
   / `rail1` / `parent1` / `parent2` / `tension1` / `trim`. Read them **after commit** (§6.7.4, §6.7.5).

Half 1 alone is not enough: in a blend set, three sub-objects share one superclass and are
indistinguishable by class. A resolver that cannot be shown to carry the properties it was given is not a
resolver, it is a coin toss that usually compiles.

### 6.5 The shell

`thickness_cm` is a **parallel offset distance on a `u_loft`**, and it is not decorative:

| Fact | Consequence |
|---|---|
| `\|thickness_cm\| < 0.001` ⇒ the offset surface is **silently omitted** | `G-47` FAILs the spec. A 0.0005 shell would be a spec that builds to nothing and reports success |
| A **positive** value offsets **outward along the normal** | Measured: base crown `600.97` → offset crown `625.94` for `thickness_cm: 25.0`. **A vault's shell is above its soffit, not below it.** Do not "correct" a positive value to negative to get an inner lining — that inverts the soffit you panelised |
| The offset is appended **after** the base loft | §6.4. The last `NURBSSurface` is the shell |
| The offset surface gets `matID:2`, the base `matID:1` | Two sub-materials on one node. **CORRECTED (2026-10-06):** this cell said "a single-material assumption at S6 is a defect"; **S6 was cancelled on 2026-10-05** and applies nothing. The `matID` split is still the correct **declaration** — the user assigns the two materials by hand, and a surface that silently collapses to one is worth reporting |

Arithmetic check for a new recipe, stated as arithmetic and not as measurement: the
`specs/recipes/barrel-vault.json` crown is `580.0` with `thickness_cm: 20.0`, so its shell crown is
`600.0` by the same rule. **The 20 cm figure is arithmetic; only `600.97 → 625.94` was measured.**

### 6.6 The other two library traps

| Trap | Rule |
|---|---|
| **`setPoint` arity** | **4 arguments on a surface** — `setPoint surf u v point`. **3 on a curve.** The three-argument form on a surface throws `Argument count error: setPoint wanted 4, got 3` |
| **Weight** | `NURBSIndependentPoint` has **no** `.weight` and no `getWeight`. `NURBSControlVertex` has a real settable `.weight` (read `0.5` → write `3.0` → read `3.0`). A `point_grid` therefore **cannot be weighted at all** — `weights` is `cv_grid`-only (§8.2.2) |
| **Division arguments are positional** | `sampleSurfaceToQuadPoly node idx uDivs vDivs` (F9) and `createDiagridOnSurface node idx uCells vCells` (F10) take the divisions **positionally**. Passing `uDivs:` as a keyword throws |
| **Order clamping** | `u_order` / `v_order` above the count is silently clamped by `amin`. `G-46` fails the spec instead, because a spec that says 5 on a 4-point row builds something other than what it says |
| **No surface closure method** | There is **no** `closeU`, `closeV` or `close` on a surface. `NURBSPointSurface().closeU` → `Unknown property: "closeU"`. Closure is `closed_sections`, one flag per loft |
| **Curve closure** | `makeCVCurve closed:true` is honoured **SEAM-WILLED** — the first CV is repeated as the last — because a `NURBSCVCurve` can never be topologically closed. `makePointCurve closed:true` is native and real. Both lofts build from **point** curves |

### 6.7 The four dependent kinds — `rail_sweep`, `two_rail_sweep`, `blend`, `trim`

`NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface` and `NURBSProjectVectorCurve`
**all construct, commit inside a `NURBSNode`, evaluate, and expose their relational property sets.**
They are available. The stage's older claim that they "expose no property or method this build resolves"
was a **false negative**, from two mistakes at once: the properties were read on *unattached* objects, and
the read used `o["rail"]`, which is not dynamic property access in MAXScript. The same names read back
immediately on the committed sub-object — `rail=0 railID="0P" parallel=true numCurves=3`
(`railID` is an `IntegerPtr` printed `<decimal>P`; `12-nurbs-gotchas.md` §3.29 settles the format
and still forbids asserting on it)
(`CHECKPOINT.md` §"Rail sweeps, blends and trims", and the 2026-10-04 incident-log entry).
The 2026-10-04 note that followed here — "the `"0P"` string form was not reproduced" — was **itself
a false negative** and was removed on 2026-10-06: both readings were `<decimal>P` at different
magnitudes. An `*ID` is an `IntegerPtr` (§6.7.5).

> **Specified, buildable, and yours.** `07` §8.2.7 defines all four kinds, §8.2.2 is the authority on
> which keys each one carries, and `G-50`…`G-54` govern them. A `nurbs.json` naming `rail_sweep`,
> `two_rail_sweep`, `blend` or `trim` with the keys below is **valid input** and `build_nurbs.py` emits
> it. **What remains unspecified is the meaning of a few individual keys — not the kinds.** That list is
> §10.1 and it is escalated, never invented.

#### 6.7.1 Keys and defaults — exactly as the authoritative design states them

| `kind` | geometry it describes | keys it adds | default |
|---|---|---|---|
| `rail_sweep` | one or more cross-sections swept along **one** rail | `rail_section_ids` (**exactly 1**) · `section_ids` (≥ 2) · `parallel` (bool) | `parallel` → `true` |
| `two_rail_sweep` | cross-sections swept along **two** rails; section width adapts to rail separation | `rail_section_ids` (**exactly 2**) · `section_ids` (≥ 2) · `parallel` (bool) | `parallel` → `true` |
| `blend` | G1/G2 transition between **two surface edges** | `parent1_ref` · `edge1` · `parent2_ref` · `edge2` · `tension1` · `tension2` | `tension1` / `tension2` → **`0.0`**, measured (§6.7.5). The **ceiling is still open** and is a design decision, not a measurement — so a spec that states a tension states it deliberately |
| `trim` | a closed profile **projected onto a surface** along a vector. **Not a cut** | `surface_ref` · `trim_section_ids` (≥ 1 closed profile) · `p_vec` `[x,y,z]` · `seed` `[u,v]` · `flip_trim` (bool) | `flip_trim` → `false` (an *observed* read-back, not an assumption). `p_vec` and `seed` have **no** spec-level default |

Structural facts that travel with the keys, all from the authoritative design:

- Rails and trim profiles **reuse the existing `sections[]` primitive** — an ordered list of
  `points_cm`. `section_ids`, `rail_section_ids` and `trim_section_ids` all reference `SEC-nnn` ids
  exactly as `section_ids` already does, with the same "consumed at least once" rule (`G-44`).
- `surface_ref` / `parent1_ref` / `parent2_ref` reference `SUR-nnn` ids **declared earlier in the same
  file**, matching the `derivatives[].surface_ref` convention. `G-52` enforces the ordering for `blend`.
- `edge1` / `edge2` are integers `1..4` = **low-U, high-U, low-V, high-V**, and the mapping is now
  **measured for all sixteen combinations**, not only `edge1: 1 edge2: 1` (§6.7.5). Two of the sixteen
  are unusable and fail silently: the **coincident** pair yields a zero-area surface, and a
  **same-axis / same-side** pair bulges outside both parents.
- A `trim` profile **closes itself**: `sections[]` has no `closed` key and no dependent kind takes
  `closed_sections`, so a profile is closed when its last point repeats its first. A rail is an open row.
- **No dependent kind takes `thickness_cm` or `closed_sections`** — the offset shell and the closure flag
  are arguments of the loft helpers, not of these classes. They are on `G-43`'s forbidden list.

> **Declare every dependent key explicitly, and rely on no default.** `07` §8.2.2 marks `tension1`,
> `tension2`, `seed` and `flip_trim` **required** on their kinds; `build_nurbs.py` treats all four as
> optional. A spec that **states all four explicitly satisfies both readings** — so state them.
> `seed` remains domain-sensitive: `[0.5, 0.5]` is only a mid-parameter against a `[0,1]` parent, and a
> chord-length parent would take a different value (§6.7.5).
>
> **`tension1` / `tension2` are a reported defect, not an implementation fallback.** The builder
> substitutes `1.0, 1.0`. That value is now measured to be **the opposite of neutral**: at `1.0 / 1.0`
> the worked blend reached `Y 450…1195.64` against a parent ending at `y = 900` — **295.64 cm past the
> vault** and 50 cm below its springing (§6.7.5). `0.0` is the straight transition. Report the
> divergence on `OBJECTIONS` (§12) every time you see it; a spec that omits the tensions and gets
> `1.0` has specified a soffit that leaves the building.

#### 6.7.2 The invariants, and what they mean for the build

| id | What it demands | Failure |
|---|---|---|
| **`G-50`** | **Arity.** `rail_sweep` has exactly **1** rail, `two_rail_sweep` exactly **2**, `blend` has both parents and both edges, `trim` has a surface and ≥ 1 profile. It also refuses by name a relation parent whose kind the builder cannot build on its own node — `u_loft`, `uv_loft`, `point_grid`, `cv_grid` only | FAIL |
| **`G-51`** | **Every cross-section meets every rail** within `tolerances.linear_cm`. This is the pre-flight for the silent drop: Max discards a sweep whose sections never meet its rail and **reports nothing** | FAIL |
| **`G-52`** | **`blend` parents resolve, and resolve earlier** — `parent1_ref` / `parent2_ref` match `^SUR-\d{3}$` and name a `surfaces[].id` declared earlier in the file; `edge1` / `edge2` are integers in `1..4` | FAIL |
| **`G-53`** | **`trim` operands are well formed** — `p_vec` is exactly 3 finite numbers of **non-zero magnitude**, `seed` exactly 2 numbers, `flip_trim` a bool | FAIL |
| **`G-54`** | **Emitted-surface census.** A committed node holds **exactly** the number of `NURBSSurface` sub-objects the spec implies. Enforced **at build time by the emitted `.ms`**, which counts them after `NURBSNode` and throws a named error. An **honest SKIP with its reason at lint time** — a static file cannot observe a commit | FAIL at build · SKIP at lint |

`G-50`…`G-53` **extend** `G-43`, `G-44` and `G-45` rather than replacing them: they police the same
kind vocabulary and the same reference resolution for the four relational kinds.

> **The first live run of a spec that uses these kinds is a measurement, not a formality.**
> An invalid dependent surface is **silently dropped at commit** — no error, no warning, it is simply not
> in the set — so a build that merely completes proves nothing. **The census is what turns that silent
> geometry loss into a build failure, and it is the most valuable single check in this stage.** The
> expected counts come from transcripts, not from the emitter, and they are **self-correcting by design**.
> They **changed on 2026-10-04**, when relations were shown to reference their parents by `nurbsID`
> instead of re-instantiating them (§6.7.4):
>
> | kind | expected `NURBSSurface` sub-objects | why |
> |---|---|---|
> | `rail_sweep` · `two_rail_sweep` | **1** | the sweep is the only surface in its own set |
> | `blend` | **1** | the relation only. Its **two** parents live in their **own** nodes and are referenced by `nurbsID` — measured `nObj=1`, one `NURBSBlendSurface`, bbox identical to the in-set arrangement |
> | `trim` | **0** | with `trim:false` the relation adds **no** surface at all: measured `nObj=6` — 4 × `NURBSPoint`, the `NURBSPointCurve`, and the `NURBSProjectVectorCurve` |
>
> **Two divergences you may legitimately measure, and neither is a reason to change the expectation.**
> A `blend` reporting **3** means the builder still re-instantiates the parents inside the dependent set
> — the pre-2026-10-04 arrangement, which puts the parent in the scene once per relation. A `trim`
> reporting **1** means the builder is still emitting `trim:true`, and that one surface is the parent's
> **untrimmed copy**, not a cut. Both are **`OBJECTIONS` for the builder's owner** (§12). **Never** widen
> the expectation to make a throw disappear.
>
> If a count is wrong, the first `fileIn` reports the **true** number in the throw, and that number is the
> one that has to change at source. **A first-run `G-54` throw is the feedback loop working, not a failure
> to hide.** Read the actual count out of the message, record it with the surface id, and report it on
> `OBJECTIONS` for the builder's owner (§12). **Never** suppress it, widen the census, delete the census
> call, hand-edit `nurbs.ms`, or rebuild until it passes — you do not own that file (§2.2, §3), and
> silencing a measurement is the exact failure mode `G-54` was written to prevent.

#### 6.7.3 The keyword sets, as proved by execution

Existence was proved by type mismatch; values by commit + read-back. Nothing here is inferred from a
constructor.

| Class | Keywords that exist | Measured result on the committed surface |
|---|---|---|
| `NURBS1RailSweepSurface` | `rail` `railID` `parallel` `numCurves` `axisTM` | 3-point rail + 3 sections → `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[500,0,100]` — the exact expected midpoint |
| `NURBS2RailSweepSurface` | `rail1` `rail1ID` `rail2` `rail2ID` `parallel` `numCurves` | two rails 500 cm apart + 3 transverse sections → `[0,1]` × `[0,1]`, `evalPos(0.5,0.5)` = `[550,200,0]` — the exact midpoint between the rails |
| `NURBSBlendSurface` | `parent1` `parent1ID` `parent2` `parent2ID` `edge1` `edge2` `tension1` `tension2` | two point surfaces + blend → **3** surfaces (the in-set arrangement); the blend read back `parent1=0 parent2=0 edge1=1 edge2=1 tension1=1.0`, `evalPos(0.5,0.5)` = `[-50.0011,100,100]`. Parents referenced by `nurbsID` from their own nodes → **1** surface, `edge1`/`edge2`/`tension1`/`tension2` all reading back exactly across **all sixteen** edge combinations |
| `NURBSProjectVectorCurve` | `parent1` `parent1ID` `parent2` `parent2ID` `pVec` `seed` `trim` `flipTrim` | plane + closed 5-point circle above it, `pVec:[0,0,-1] trim:true` → `seed=[0.5,0.5] trim=true flipTrim=false`. **Corrected 2026-10-04: the second surface is the parent's untrimmed copy and `trim:true` cuts nothing (§6.7.5)** |
| `NURBSOffsetSurface` | `parent` `parentID` `distance` | §6.5 — already in use by `createULoftShell` |

Both sweep types have a `[0,1]`-normalised domain, unlike a `point_grid`'s chord-length one (§6.2).
**This table is evidence, not schema.** The spec keys are §6.7.1, and a spec **never names a MAXScript
class, plugin or tool** — `rail_sweep` is not `NURBS1RailSweepSurface`, and the implementing class is an
implementation detail of the builder (`07` §12's standing rule).

#### 6.7.4 The procedure — parents first and committed, then the relation, then count

```maxscript
-- 1. PARENTS FIRST. Build the rail and every cross-section, append each, and NOTE the index.
--    `sectionPts` is the point-row primitive of §1.1; a "section" is one ordered row.
--    A rail and a trim profile are rows too -- there is no second primitive to learn.
local nset = NURBSSet()
appendObject nset (MCP_NURBS_Arch.makePointCurve #[[0,0,0],[0,0,500],[500,0,100]] name:"Rail" closed:false)
local railIdx = nset.numObjects                            -- appendObject returns "OK", NEVER an index
local secIdx = #()
for i = 1 to 3 do (
    appendObject nset (MCP_NURBS_Arch.makePointCurve sectionPts[i] name:("Sec_" + (i as string)))
    append secIdx nset.numObjects
)

-- 2. THE DEPENDENT SURFACE, carrying its parent keyword. Then its cross-sections.
local sweep = NURBS1RailSweepSurface name:"MySweep" rail:railIdx parallel:true
for s in secIdx do appendCurve sweep s

-- 3. COMMIT. Nothing before this line is readable or evaluable.
appendObject nset sweep
local node = NURBSNode nset name:"MySweep"
stopCreating                                               -- ZERO arguments

-- 4. READ STATE BACK ON THE COMMITTED SUB-OBJECT. This step is mandatory, not a nicety.
local rset = getNURBSSet node #relational
local nSurf = 0
for i = 1 to rset.numObjects do (
    local o = getObject rset i
    if superClassOf o == NURBSSurface do (
        nSurf += 1
        format "% rail=% railID=% parallel=% numCurves=% u=[%,%]\n" i o.rail o.railID o.parallel \
            o.numCurves o.uParameterRangeMin o.uParameterRangeMax
    )
)

-- 5. THE CENSUS IS THE TEST -- this is G-54, and it is what the builder emits. An invalid
--    dependent surface is DROPPED SILENTLY at commit: no error, no warning, it is simply not
--    in the set. Measured: the same sweep with no rail set gave numObjects=7 and NO NURBSSurface
--    at all; with rail: set, numObjects=14 and the surface at index 14.
--    Expected: 1 for a sweep, 1 for a blend, 0 for a trim (§6.7.2). A first-run mismatch is a
--    MEASUREMENT: report the actual count, do not silence it.
if nSurf != 1 do throw ("MySweep: expected 1 NURBSSurface sub-object, got " + (nSurf as string) + \
    " -- the dependent surface was dropped at commit; check rail:/parent* before believing the node")
node
```

The order is not a style preference and must not be rearranged: **parents → `appendObject` → note indices →
construct the dependent → `appendCurve` → `appendObject` → `NURBSNode` → `stopCreating` → read → census.**
Steps 1–3 may be condensed into a helper; step 4 may not, and **step 5 is the only thing standing between
you and a clean-looking node with no surface inside it.**

##### A relation references its parents; it does not own them

The sweep above builds its rail **in the same set** and names it by the pre-commit ordinal `railIdx`.
**A `blend` or a `trim` is different: its parents are surfaces that already have their own nodes**, so
they are named by `nurbsID`, and the relation's own set holds the relation and nothing else.

```maxscript
-- The parent is committed in its OWN node. Bind its id immediately after that commit (§6.3).
local pset = getNURBSSet parentNode #relational
local pid  = 0
for i = 1 to pset.numObjects do (
    local o = getObject pset i
    if classOf o == NURBSULoftSurface do ( pid = o.nurbsID; exit )   -- classOf, never index arithmetic (§6.7.6)
)
if pid == 0 do throw ("build_nurbs: " + parentNode.name + " exposes no surface to reference")

-- A fresh set containing ONLY the relation.
local rset = NURBSSet()
local bl = NURBSBlendSurface parent1ID:pid edge1:4 parent2ID:<qid> edge2:4 \
                           tension1:0.0 tension2:0.0      -- 0.0 is the straight transition (§6.7.5)
appendObject rset bl
local relNode = NURBSNode rset name:"MyBlend"
stopCreating
```

Three rules, each with a transcript behind it:

1. **Do not re-instantiate the parent inside the relation's set.** Measured: referencing the parent's
   `nurbsID` gives a relation set holding **one** sub-object with a bbox **identical** to the in-set
   arrangement. Re-instantiation puts a parent named by two relations into the scene **three times**.
2. **Never emit a literal in a `parent*ID:` slot.** `nurbsID` is an **`IntegerPtr`**. A string errors
   (`Unable to convert: "…" to type: IntegerPtr`); a **synthetic integer crashes the 3ds Max process**
   with `EXCEPTION_ACCESS_VIOLATION`, unrecoverably from inside the script. Always bind from a committed
   sub-object.
3. **A blend's `tension` is `0.0` unless the spec says otherwise, and its two edges must be neither
   coincident nor on the same side of the same axis** (§6.7.5).

This is why `G-54` counts surfaces rather than nodes — and why a relation node now holds **fewer**
surfaces than a node of any other kind, not more. A `blend` node holds **1**; a `trim` node with
`trim:false` holds **0** (§6.7.2).

#### 6.7.5 Read-back caveats — what does *not* round-trip, and what must not be encoded

| You pass | It reads back | Therefore |
|---|---|---|
| `rail:` / `rail1:` / `parent:` / `parent2:` — a 1-based **set index** | **`0`** | Never assert a parent index round-trips. Assert the sub-object exists and carries the property at all |
| `railID:` / `parent1ID:` / `parent2ID:` | an **`IntegerPtr`**, printed as a large decimal followed by `P` | It is an id, not a slot. Do not parse it, compare it, or **write a literal** — a synthetic one crashes Max (§6.7.4, §11 AP-19) |
| `pVec:[0,0,-1]` | `[0,0,1]` — **the opposite sign** | ⚠️ **Never assert `pVec` round-trips.** Assert `trim` / `seed` / `parent1` / `parent2` instead |
| `flipTrim:true` | `true` — and **no geometry moves** | It is a flag on the relation, not a cut direction |
| *any* keyword at all, including a bogus one | no error — **silently ignored** | A clean construction proves **nothing** about a keyword (§11 AP-16) |

Two probe rules follow, both paid for by the original false negative:

- The only keyword-existence discriminator is a **type mismatch**. A name that exists errors when handed
  a string (`rail: "zzz"`); a name that does not exist is swallowed whole.
- **Never probe with `o["rail"]`.** Bracket access is not dynamic property access in MAXScript and returns
  `ERR` for **every** name, known-good included; `getProperty o #x` fails identically. **A uniform result
  across a heterogeneous name list is a broken probe, not a uniform absence** — it must contain at least one
  known-positive name.

Three further constraints the transcripts impose on what a spec may say:

- **The design surface is not always the first one.** A sweep or an offset derivative reads the **first**
  `NURBSSurface`; a `NURBSBlendSurface` is the **last** (§6.4.1). No spec names an index at all, and no
  `blend` may be assumed to sit where a sweep does.
- **`seed` is written in the parent's own parameter domain.** `[0.5, 0.5]` is correct against a `[0,1]`
  parent and meaningless against a chord-length `point_grid`. *(An inference from the domains, not a
  transcript — the only `seed` read-back ran on a plane.)*

##### `trim` projects; it does not cut — corrected 2026-10-04

Earlier revisions of this contract recorded that the projection produced "a **second** surface where one
was expected" and read that as a trim. **It is not a trim.** The second surface is the **parent's
untrimmed `NURBSCVSurface` copy**, added by the relation.

| `trim` | committed set | surfaces contributed |
|---|---|---|
| `false` | `nObj=6` — 4 × `NURBSPoint`, the `NURBSPointCurve`, the `NURBSProjectVectorCurve` | **0** |
| `true` | `nObj=7` — the same plus one `NURBSCVSurface`, `bb=[0,0,420 .. 1800,900,600.97]`, i.e. the **parent's** extent | **1**, and it is a duplicate of the parent |

The test that settled it: the profile was widened to span the whole vault — `x −200…1900, y 300…500` —
which a real cut would split into two disjoint pieces. The result was **byte-identical** to the small
profile's: `nSurf=1`, one `NURBSCVSurface`, `Y 0…900`. It does not split, does not cut, and does not
vary with the profile.

**Emit `trim:false`, expect 0 surfaces (§6.7.2).** An aperture in a NURBS surface is **not something
this class does** — it needs a **Boolean modifier or a surface split**, outside the NURBS stage. A spec
that asks for a skylight opening through `trim` is asking for a capability that does not exist here;
escalate it rather than emitting a node that carries a second copy of the vault shell and calls it a
skylight.

##### A blend's `tension` is `0.0`, and its edge pair must be sane — measured

All sixteen `edge1` × `edge2` combinations were built on a controlled pair (two 3 × 3 point surfaces,
`x 0…200` and `x 200…400`, sharing the plane `x = 200`). **All sixteen committed** and every
`edge1` / `edge2` / `tension1` / `tension2` **read back exactly** — and three of the sixteen are
unusable, with no error raised:

| edge pair | result |
|---|---|
| **coincident** (`edge1:2 edge2:1` — `P`'s high-U against `Q`'s low-U) | `200,0,0 … 200,200,0` — a **zero-area surface, silently** |
| **same axis, same side** (`3/3`, `4/4`) | bulges outside **both** parents — up to **111 cm on a 200 cm patch** |
| everything else | a bridge between the two selected edges |

And the tension scale, measured on the worked vault / canopy pair (blend bbox sampled over the blend's
own committed domain, never the node bbox):

| tension | blend bbox Y | blend bbox Z | |
| :--- | :--- | :--- | :--- |
| `0.0 / 0.0` | **450 … 900.0** | **420.0 … 600.97** | the straight transition — a soffit panel filling exactly the gap between the two edges |
| `0.5 / 0.5` | 450 … 995.514 | 401.084 … 600.97 | already outside the vault's own `y = 900` |
| `1.0 / 1.0` | **450 … 1195.64** | **369.758 … 600.97** | **295.64 cm past the parent**, 50 cm below the springing |

`0.0` is the neutral value. **Above `0` the blend is pushed outward past *both* edges and the overshoot
grows with the tension — Max does not bound it**, which is why the schema has to (`G-16` currently finds
the tensions unbounded, and that is now a known defect rather than an open question). This is the
measured cause of the `SUR_006_CanopySoffit` bbox reaching `y = 1518` against a 900 cm deep plan.

#### 6.7.6 Filter committed sub-objects by `classOf` — never by index arithmetic

`getObject rset i` is **1-based over the committed set**. `parent:` / `rail:` / `appendCurve` take the
**pre-commit ordinal** that `nset.numObjects` returned immediately after `appendObject`. They are not
the same number and the gap is not small: two 3 × 3 point surfaces plus a blend append as ordinals
**1, 2, 3** and commit as **21** sub-objects, with the blend at committed index **21**.

| route | what the number means |
|---|---|
| `getObject rset i`, `rset[i]` | the **committed** 1-based index |
| `parent:` / `rail:` / `appendCurve` | the **pre-commit ordinal** from `nset.numObjects` |

`parent1:1 parent2:2` resolved to committed indices 10 and 20 and the blend committed correctly, so the
emitted `local x = nset.numObjects` pattern is **right**. What is broken is **filtering committed
sub-objects with `k > <pre-commit ordinal>`** — it silently reads the wrong object, and it cost one
probe.

```maxscript
for i = 1 to rset.numObjects do (
    local o = getObject rset i
    if (classOf o) == NURBSBlendSurface do ( /* this is the blend */ )
)
```

**Enumerate by `classOf`, or by `superClassOf` when you only care about surfaces.** Never by comparing
an index against an ordinal you noted at append time.

---

## 7. The 3ds Max step

**The orchestrator executes `nurbs.ms`. S3 does not.** These are the verified facts the step depends on.

| Fact | Status | Consequence |
|---|---|---|
| Scene units are **centimetres**, `units.SystemScale 1.0` | ✅ verified 2026-10-04, known-bogus control in the same batch | **No conversion.** A `points_cm` triple is the same number in Max. Do not scale at the boundary |
| `nurbs.ms` opens with `if MCP_NURBS_Arch == undefined do fileIn "<abs>/snippets/nurbs_arch_library.ms"`, wraps its whole body in one `fn mcpNurbsBuild_<project>`, and ends with a single call to it | ✅ executed | **Never hand-edit.** `local` at the top level of a `.ms` is a compile error, and the builder is already idempotent — a second run deletes the previous nodes by name and rebuilds |
| The emitted builder deletes any node with a matching spec `name` before creating it | ✅ executed | A rebuild is safe. A **partially failed** run is not — see §9 |
| One `NURBSNode` per surface, named the spec `name`; one node per derivative, re-named after creation (`quad_panels` returns an `Editable_Poly`, `space_frame` a `SplineShape`) | ✅ executed | Node names come from the spec, never from an auto-name (`11` N4) |
| **An object's layer cannot be assigned from MAXScript.** Six routes executed, all throw `Property is read-only: layer`. Layer creation and reading do work | ✅ verified, six transcripts. **CORRECTED (2026-10-06): three further routes were ruled out — nine in total** — and the action name is **not unknown, it does not exist** (`agents/max-assembly.md` §6.3) | **Layer stays data.** Nodes land where Max puts new geometry and that is expected — **not a defect, never "fixed" in the emitted script.** **No stage applies the layer; the user does, in the Layer dialog** (this cell used to say "S5 applies `assembly.json.layer_map`") |
| `getNURBSSet node #relational` + `getObject rset i` is the read route for sub-objects; `evalPos surf u v` is the read route for a point | ✅ executed | This is the measurement route (§8) |

**UNVERIFIED — do not build on these without an orchestrator probe:** `nurbs.ms` on a scene that is not
empty; `setPoint` on a committed surface; any surface-closure method; a `space_frame` cage on a
`cv_grid` whose domain is `[0, 1]` against a `point_grid` whose domain is chord-length; a **cross-set
`rail1ID:` / `rail2ID:`** form — the *parent* side has a transcript (§6.7.4), the rail side does not, so
a rail stays on the ordinal route.
**Do not build on these; do not assert them either.**

> **Two of the three items in that paragraph were closed by execution on 2026-10-06 and have moved
> out of the "unexplained" list** — the printed form of an `*ID` and the `numCVs` copy, both
> explained in `12-nurbs-gotchas.md` §3.29 and §3.30. The cross-set rail id is the only one left,
> and it is still a hypothesis. The line above has been kept as the record of what was once unknown.

**Verified, do not re-probe or escalate as missing:** the four dependent kinds of §6.7 — `rail_sweep`,
`two_rail_sweep`, `blend`, `trim` — construct, commit, evaluate, expose the keyword sets in §6.7.3, and
are **specified and buildable**. A relation node holds **fewer** `NURBSSurface` sub-objects than a node
of any other kind — **1** for a `blend`, **0** for a `trim` under `trim:false` — because the relation
references its parents by `nurbsID` instead of re-instantiating them (§6.7.4). What is still open is
§10.1 — a ceiling for the blend tension and a few individual key meanings, never the kinds.

**How to run it.** `3dsmax-mcp_execute_maxscript` with `fileIn "<absolute path>"` — the default route.
Non-negotiable: **one script per call** and **under ~2 s**. `execute_maxscript` runs on Max's **main
thread** and a long script freezes the UI.

---

## 8. Verification — the completion gate

Check every row. **The validator covers the mechanical subset only**; rows 3, 5, 6, 7, 8, 9, 13, 14, 15,
16, 17, 18 and 19 are yours.

| # | Gate | Checked by |
|---|---|---|
| 1 | `python scripts/validate_specs.py --dir <specs_dir> --build` exits **0**, with `G-41`…`G-54` **all PASS** | the transcript of the final run |
| 2 | **A SKIP on any of `G-41`…`G-54` is not a pass.** A check that cannot be evaluated reports SKIP with its reason, never a silent PASS (`07` §9.7). `G-46` legitimately SKIPs when no `cv_grid` declares an order; `G-48` when `derivatives[]` is empty; `G-49` when `dimensions.json` / `massing.json` is absent; `G-50`…`G-53` when the file has **no dependent surface**; and **`G-54` always SKIPs at lint time, by construction** — the census is observed in live Max, not in the file. Each SKIP is named and escalated | you, reading the `--json` output |
| 3 | **Every surface and derivative node exists**, named the spec `name`, and **the scene holds nothing else** | you — `3dsmax-mcp_get_scene_info` (`11` H5/H6) |
| 4 | Every `origins` entry is `derived` with a non-empty `derives_from` resolving in `massing.json`, `dimensions.json` **or this file**; every `origin_inputs` path resolves in `massing.json` or `dimensions.json`; `tolerances` equals `massing.json`'s, unwidened | **G-49**, **G-31** |
| 5 | Every section is consumed by **at least one** surface; every `section_ids` / `u_section_ids` / `v_section_ids` / `rail_section_ids` / `trim_section_ids` / `surface_ref` / `parent1_ref` / `parent2_ref` resolves inside the file, and every relation parent is **declared earlier** | **G-44**, **G-52** |
| 6 | **`node.min` / `node.max` compared to the spec**, within `tolerances.linear_cm` — and the comparison is against the **evaluated** surface, never the lattice (§6.2). The bbox is a **node** bound inflated by the node's own tessellation; pair it with an `evalPos` sample before calling the geometry correct (route table below) | you — the measurement route below |
| 7 | **The parameter domain is what the kind implies**: `point_grid` chord-length, `cv_grid` `[0, 1]`, **both sweeps `[0, 1]`** — read from `getNURBSSet node #relational`, never assumed | you — `inspectNURBSSet` / `uParameterRangeMin` |
| 8 | Every surface was resolved **by superclass** and then **confirmed to carry the relational properties just set** — never by a literal index, never by first match alone (§6.4, §6.4.1). On a shelled surface the derivative's numbers are the **design soffit's**, not the shell's; on a **blend** set the design surface is the **last**, not the first | you — compare against `surfaces[0].thickness_cm`, then read the resolved sub-object's properties |
| 9 | The script ran **without error**. An error that produced no node is a FAIL, not a partial pass | the call's return value |
| 10 | A second run over the same locked spec produces the same node-name set | `11` H10 — two runs, compared. The determinism check, not an assumption |
| 11 | **No probe node, no `99_DEBUG` orphan, nothing hand-placed in the viewport.** A `quad_panels` mesh on `99_DEBUG` is a *named* QA intermediate and is allowed; an unnamed one is not (`11` H5) | you — `get_scene_info` |
| 12 | Every `kind` you emitted is one `07` §8.2.3 defines, and every key it carries is one that kind allows — including the four dependent kinds' forbidden sets (§6.7.1) | **G-43**, **G-45** |
| 13 | **The committed set holds the number of `NURBSSurface` sub-objects you expected** — counted on `getNURBSSet node #relational`, never assumed from the constructor, and checked on **every** node. A dependent surface with an unset parent is **dropped silently at commit**: no error, no node, no surface (§6.7.4). Expected counts: **1** for a sweep, **1** for a `blend`, **0** for a `trim` under `trim:false` (§6.7.2). A `blend` reporting 3 or a `trim` reporting 1 is a **divergence to report on `OBJECTIONS`**, not an expectation to widen | you — the census in §6.7.4 step 5, which is `G-54` |
| 14 | **On every dependent surface, `G-50`…`G-53` PASS with a stated reason if they SKIP** — arity, cross-section-meets-rail within `tolerances.linear_cm`, parents declared earlier with `edge1`/`edge2` in `1..4`, and `p_vec` / `seed` / `flip_trim` well formed. A `blend`/`trim` parent is a kind the builder can build on its own node | the validator transcript, read row by row |
| 15 | **The first live run of a spec using a dependent kind was treated as a measurement.** If `G-54` threw, the **actual** count was read out of the message, recorded against the surface id, and reported on `OBJECTIONS` — **not** suppressed, **not** silenced by editing `nurbs.ms`, **not** retried until it passed (§6.7.2) | you — the throw's text plus your `OBJECTIONS` line |
| 16 | **Every `parent1ID:` / `parent2ID:` in the emitted script is bound from a committed sub-object, and there is no literal in any `parent*ID:` slot.** A literal is a **process crash**, not a MAXScript error (§6.7.4) | you — read the emitted `nurbs.ms` for the bind, and confirm no bare integer sits in an `*ID` position |
| 17 | **Every `blend` states `tension1` and `tension2` explicitly, and neither edge pair is coincident or same-side-same-axis.** `0.0` is the neutral value; above it the blend overshoots **both** edges by an unbounded amount, and a coincident pair is a zero-area surface — both silently (§6.7.5) | you — the spec, plus the blend's own sampled bbox against its two parents' extents |
| 18 | **Every `trim` emits `trim:false`, and no spec claims a cut.** The class projects; it does not cut. An aperture is a Boolean-modifier or surface-split job outside this stage (§6.7.5) | you — the emitted `.ms`, and the spec's intent |
| 19 | **Every committed sub-object was located by `classOf` / `superClassOf`, never by comparing an index to a pre-commit ordinal** (§6.7.6) | you — the resolvers in the emitted `.ms` |

**The measurement route.** Read the node back and compare against the spec — do not eyeball a
viewport and do not ask a tool whether the geometry "looks right".

```maxscript
-- one call, all of it: names, bbox, parameter domain, sub-object census, then the sweep
local out = ""
for n in objects where (superClassOf n) == GeometryClass do (
    out += n.name + " min=" + (n.min as string) + " max=" + (n.max as string) + "\n"
)
out
```

| Question | Route |
|---|---|
| Did the right nodes arrive? | `n.name` against `surfaces[].name` + `derivatives[].name`, and `objects.count` before and after |
| Where is the geometry? | `evalPos surf u v` on the **resolved** sub-object, `u`/`v` from its real domain. `node.min` / `node.max` is a **node** bound, inflated by the node's own tessellation — measured: a closed `NURBSPointCurve` over a `750…1050 × 375…525` rectangle reports `714.645…1080.17 × 286.503…617.732`. Legitimate for a QA tolerance comparison you have bounded another way (§6.2); **never** a measurement of the surface itself |
| What did the set actually contribute? | `MCP_NURBS_Arch.inspectNURBSSet node` (F8) — index, class, superclass, `U:[min,max]`, `V:[min,max]`, `MATID`, `FLIP` per sub-object |
| Where is a point **on** the surface? | `evalPos surf u v` on the **resolved** surface, `u`/`v` from its real domain — never `[0, 1]` by habit |
| **Did a dependent surface actually get built?** | the `G-54` census on `getNURBSSet node #relational` (§6.7.4 step 5), **plus** a read-back of the relational properties on the resolved sub-object — `rail` / `parallel`, `parent1` / `parent2` / `edge1` / `tension1`, `trim` / `seed` / `flipTrim`. Assert those, never a parent index or a `pVec` round-trip (§6.7.5) |
| Does it match the spec? | `abs(measured − expected) ≤ tolerances.linear_cm`. A larger mismatch is a real inconsistency in the spec or the builder: **report both figures and stop.** Do not nudge the node or widen the tolerance |

For a `point_grid`, expect the bounding box to exceed the lattice (§6.2) — that is not a defect, it is
the kind. For a `cv_grid`, expect it never to. **A QA check that cannot tell those two apart is not a
QA check.**

---

## 9. Cleanup

Cleanup is part of the build, not a chore after it.

| # | Rule | Evidence |
|---|---|---|
| 1 | **Delete every test node in the same call that created it.** If a call fails or is aborted, **sweep** — do not assume nothing was created | An aborted probe leaves its objects behind; eight orphans accumulated and had to be swept |
| 2 | **A failed build leaves a half-made set.** `nurbs.ms` deletes only nodes it is about to recreate; a surface that threw before its derivative was emitted leaves the surface behind. Sweep by spec-derived name, never by wildcard | the builder's own pre-delete is per-name and cannot know about a node it never reached |
| 3 | **The sweep is explicit** — `3dsmax-mcp_delete_objects` with spec-derived names, never "delete everything", and **compare `objects.count` before and after** — the count is the evidence | You are not the only tenant of that session; a blanket delete destroys the user's own work (`11` H12) |
| 4 | A **bare modifier is not a node and cannot be deleted** | A `Sweep()` or `TurboSmooth()` left unattached is unreachable to a node-delete |
| 5 | Cleanup never touches the S3 geometry — it stays. Only probes and superseded runs are removed | `11` §6 delivery checklist |
| 6 | **A `G-54` throw aborts the builder mid-file.** Later nodes were never created, so a failed dependent build leaves an **earlier** complete set plus a partial one. Sweep the whole S3 name set on the failure path, not only the node that threw | the builder's per-name pre-delete cannot reach a node it never got to (§9 row 2) |
| 7 | **`delete <node>` on a `NURBSNode` did not remove it from `objects` in the same call in one measured case.** Sweep backwards and **confirm the count**: `for i = objects.count to 1 by -1 do (delete objects[i])`, then assert `objects.count == 0` before finishing. A `NURBSNode` holding a **relation** is the case that matters — it may still be evaluating an id | a failed probe leaves orphans; a silently-surviving node does the same |

---

## 10. Escalation policy

S3 computes; it does not design, and it escalates anything it cannot build honestly.

| You may decide alone | Boundary |
|---|---|
| Which `07` §8.2 key a surface's data belongs at; surface and derivative id assignment and ordering | If a value does not fit a key, escalate — never invent one. Ids ascend, zero-padded, fixed order |
| Which of the eight kinds a described form is, and why | If two kinds are defensible and the choice changes the geometry by more than `linear_cm`, escalate with both readings |
| Optional keys — `mat_id`, `hide_curves`, `merge_tol_cm`, `approximation`, `closed_sections` | Omit rather than guess. An honest omission beats an invented value |
| The lattice's **row** order and point order within a row | Row-major is not free choice: `grid[iv][iu]`. Reversing it transposes the surface |

### 10.1 You must stop and ask

| Topic | Why | Goes to |
|---|---|---|
| **The meaning of an unspecified dependent key.** `parallel: false` and `flip_trim: true` — what they do geometrically. **Resolved since 2026-10-04 and no longer on this list:** the `tension1`/`tension2` **default** (now `0.0`, measured), the `edge1`/`edge2` **mapping** (all sixteen combinations measured), and whether a `trim` cuts (**it does not**). | These semantics are **deliberately unspecified** — only the `true`/`false` round-trips have transcripts for the two remaining keys. **The four kinds themselves are not on this list; their keys are in §6.7.1.** Never invent a value, a range or a mapping: `G-52` checks the edge *range*, not the mapping, so an invented mapping fails silently | **an orchestrator probe with a known-positive control**, then **`07`'s owner** records the meaning — a new key is added to §8.2.7 first, per §12 step 1 |
| **A ceiling for `tension1` / `tension2`.** The default is `0.0`; the overshoot above `0` is **unbounded by Max** and grows with the tension (§6.7.5) | A bound is a **design decision**, not a measurement — the transcripts establish the direction and the growth, not a safe number. `G-16` currently finds the tensions unbounded; that is a known defect, and picking the number is not S3's to do | **`07`'s owner**, with §10.2's format if it needs a transcript |
| ~~**The printed string form of an `*ID`.** **CLOSED 2026-10-06 by execution.** `IntegerPtr`, printed `<decimal>P`; `railID="0P"` on a committed 1-rail sweep **was real**, and `rail1ID` / `rail2ID` on a 2-rail sweep read the full pointer and equal the rail curve's own `nurbsID`. The value **changes between builds of identical geometry** — never persist one | **Still never assert a format** and never write a literal — that is a crash. The format being known changes nothing about what a spec may encode; a builder binds the id in the same script that consumes it (`G-56`). Transcript: `12-nurbs-gotchas.md` §3.29 | **closed — measured** |
| **A cross-set `rail1ID:` / `rail2ID:` form.** `parent1ID:` across sets has a transcript (§6.7.4); the rail side does not | A **hypothesis**. Rails are curves in the same set and use `rail:` by ordinal; do not switch to an id form without a transcript | **an orchestrator probe**, then **`07`'s owner** |
| **Deleting a parent node that a live relation still points at.** After the parent was deleted the relation **did not break — in the one case measured** (`evalPos(0.5,0.5)=[899.861,900,600.97]`, unchanged bbox) | **One test, one outcome, not a guarantee.** The relation set is not refilled by the parent's removal, so the id can dangle | **an orchestrator probe** before anything depends on it; until then, **keep parent nodes alive** |
| **A trim-profile closure assertion**, or a `G-` row for the `surface_ref` ordering convention | Both are expressible and unchecked: `G-50` counts profiles (≥ 1) without testing that one closes, and it checks only that a `trim` *names* a surface, while "declared earlier" is enforced for `blend` alone | **`07`'s owner.** A `closed` assertion belongs in a `G-` row, not in prose |
| **A form §8.2 still cannot express** — `revolve`, `freeform`, a surface from a swept profile, per-surface `closed_u` / `closed_v`, knot vectors, or any second geometry table such as `relations[]` | There is no `kind` for it, and §8.2.3's list of **eight** is closed. Writing one into `nurbs.json` is a `G-43` FAIL and a schema change | **S3's owner, then `07`'s owner** |
| **A relation parent whose kind the builder cannot build on its own node** — a parent that is itself `rail_sweep`, `two_rail_sweep`, `blend` or `trim` | `G-50` refuses it by name. Only `u_loft`, `uv_loft`, `point_grid`, `cv_grid` can be built uncommitted and committed as their own node | **`07`'s owner** (the build rule is the builder's, but the admissibility rule is the schema's) |
| **A missing or contradictory dimension** in `massing.json` / `dimensions.json` | S3 may not fill a dimension and may not hand-edit a locked file | **S2 / S1** |
| **Structural sizing** — shell thickness, diagrid member depth, cable pretension, node capacities | A licensed engineer's scope (`09` §5) | the user (`E1`) |
| **A `kind` whose measured result violates the design intent** — a canopy whose bounding box is 58 cm above its lattice when the brief says it shall not exceed | §6.2 is a property of the kind, not a bug. The fix is a different kind or a different lattice, and that is a design decision | the user, with the four numbers |
| **Any fact not in `CHECKPOINT.md` §"Verified facts"** | §1.2: S3 escalates for an orchestrator probe, it does not open one | the orchestrator |

### 10.2 How to record a request you cannot fulfil

An unimplemented capability is a **recorded request, never a fake**. One line each:

```
<what was asked> — <the class that exists> — <what is missing: a property or method name, not a class> — <what it would need before it could be specified>
```

Nothing may be recorded as blocked, impossible, unbuildable or non-existent without a transcript
showing the attempt and the exact error — and a **negative** needs the same discipline as a positive.
This repo has shipped fabricated negatives before (`CHECKPOINT.md` §"Incident log"); the guard is in
§11.

**§10.2 is for genuinely absent capability only.** The four dependent kinds of §6.7 are **specified and
buildable** — a rail sweep, a 2-rail sweep, a blend and a projected trim are **not** a §10.2 record.
Neither direction of that error is acceptable: calling them unimplemented is the false negative this
stage once shipped across three authoritative documents, and **inventing the meaning of an unspecified key
is the same failure wearing a different hat.** Both go on `ESCALATED` (§10.1). `revolve`, `freeform`,
per-surface closure and knot vectors **are** §10.2 material — and each still needs the transcript the
format above demands. **Cutting an aperture in a NURBS surface is §10.2 material too**: `trim` projects
and does not cut (§6.7.5), so a Boolean modifier or a surface split is what an opening needs, and that
is not a S3 instrument.

---

## 11. Anti-patterns and incident guards

| Anti-pattern | Instead |
|---|---|
| **AP-1 · Declaring a `kind` §8.2 does not define** — `revolve`, `freeform`, or any ninth name — because some class constructs | A constructing class is not a spec vocabulary. §6.1 is the closed list of **eight**; anything else is a `G-43` FAIL and an escalation (§10.1). The four dependent kinds are **in** the vocabulary (§6.7) — refusing them as "not implemented" is the false negative this stage once committed to three authoritative documents |
| **AP-2 · Trusting the emitted `nurbs.ms` because it looks right** | It is well-formed and self-checked, which proves **nothing** about whether Max will load it. The builder's self-check runs in Python. **Only `fileIn` in live Max is the ground truth**, and a `.ms` that has never been executed is an unproven file |
| **AP-3 · Hard-coding a surface index** — `16` for a 5 × 3 grid, `52` for a shelled vault | Resolve by `superClassOf o == NURBSSurface`, first match (§6.4). Indices depend on the kind *and* the section count |
| **AP-4 ·** Sampling the **last** `NURBSSurface` on a shelled surface | It is the offset. The error is exactly `thickness_cm` and it is silent |
| **AP-5 · Assuming a `[0, 1]` parameter domain** | `point_grid` is chord-length — measured `u = [0, 434.555]`, `v = [0, 307.439]`. Read the range |
| **AP-6 · Adding `closed_u` / `closed_v`, knots, or a `relations[]` table to `nurbs.json`** | No surface class has `closeU`/`closeV`; knots are derived from `order` and count. A relation is an ordinary `surfaces[]` entry with its own kind and keys (§6.7.1) — a `blend` or a `trim` references its parents by id — so there is still **no second edge table** to add |
| **AP-7 · Passing `uDivs:` / `vCells:` as keywords to F9 / F10** | They are **positional** |
| **AP-8 · Writing a `weights` array on a `point_grid`** | `NURBSIndependentPoint` has no weight. `weights` is `cv_grid`-only |
| **AP-9 · Setting `u_order` above the point count and letting `amin` clamp it** | `G-46` exists for this. A clamped order builds something other than what the spec says |
| **AP-10 · Adding layer code to `nurbs.ms` because the nodes land on the wrong layer** | It cannot work — **nine routes ruled out**, final (`agents/max-assembly.md` §6.3). Layer is data; **no stage applies it** (**CORRECTED 2026-10-06:** this cell used to read "six routes executed, all threw. Layer is data; S5 applies it") and **the user applies it in the Layer dialog** |
| **AP-11 · Comparing a lattice against itself and calling it QA** | §6.2. Compare the **evaluated** surface. A lattice-vs-lattice check passes a surface 58 cm out |
| **AP-12 · Naming `geometry_qa`, `contact_check` or `scene_qa`, or reporting a pass you did not run** | **Those tools do not exist** — use the `execute_maxscript` read-back. And write `NOT RUN` and say why |
| **AP-13 · Rewriting `references/nurbs-complete-guide.md` or `nurbs-architecture-recipes.md` on suspicion** | They are **unverified, not disproven.** Verify claim-by-claim against live Max, then correct only what actually fails. Rewriting on suspicion already happened once and was wrong (`AGENTS.md`) |
| **AP-14 · Declaring a capability missing on the strength of one property-read probe** | A single read that returns `ERR` across a heterogeneous name list is a **broken probe**, not a uniform absence — `o["rail"]` is not dynamic property access and `ERR`s on names that exist, and an unattached sub-object has no relational properties to read at all (§6.7). This exact probe once condemned four working classes across three authoritative documents. **Commit first, read second**; and a "no API exists" claim needs a known-positive control in the same batch, not only a bogus one (§1.2, §6.7.5) |
| **AP-15 · Relying on a dependency surface having been created just because construction returned no error** | An invalid dependent surface is **dropped silently at commit** — no error, no warning, and the constructor swallows even a bogus keyword without complaint — so a clean build proves the **node** exists, not the **surface**. Measured: `numObjects=7` and no `NURBSSurface` at all. The census is the only defence: count the committed `NURBSSurface` sub-objects and fail loudly when the number is wrong (`G-54`, §6.7.4 step 5, §8 row 13) |
| **AP-16 · Treating a successful construction as proof that a constructor keyword exists** | The constructor **silently accepts any keyword**, including a bogus one. The only discriminator is a **type mismatch**: pass a string and a real name errors, a fake one is swallowed (§6.7.5) |
| **AP-17 · Treating a first-run `G-54` throw as noise** — suppressing it, widening the census, deleting the census call, or rebuilding until it passes | It is the **measurement**, and the only one obtainable: the expected counts come from transcripts and are self-correcting by design (§6.7.2). Read the actual count out of the throw, record it against the surface id, report it on `OBJECTIONS` for the builder's owner, and let the count be corrected **at source**. Hand-editing `nurbs.ms` to make it pass is a defect — you do not own that file (§2.2, §3, §8 row 15) |
| **AP-18 · Filling an unspecified dependent key with a plausible value** — a "standard" `tension`, what `parallel: false` or `flip_trim: true` do, a second trim parent, or a new `relations[]` table | Those semantics are unspecified **on purpose** and the schema author left them that way (§10.1). Escalate; do not invent. `G-52` checks the edge *range*, not the mapping, so an invented value passes every gate and can only be caught in a live run. The tension **default** is no longer on this list — it is `0.0`, measured (§6.7.5); a **ceiling** for it is (§10.1) |
| **AP-19 · Writing a literal into a `parent*ID:` slot** — `parent1ID:12345` "because the id is just a number" | `nurbsID` is an **`IntegerPtr`**. A string errors on conversion; a **synthetic integer crashes the 3ds Max process** with `EXCEPTION_ACCESS_VIOLATION`, unrecoverably from inside the script. Bind it from a **committed** sub-object, immediately after the parent node commits (§6.3, §6.7.4) |
| **AP-20 · Re-instantiating a relation's parents inside the relation's set** | Parents are committed in **their own nodes** and referenced by `nurbsID`; measured, the relation's set then holds **one** sub-object with an identical bbox (§6.7.4). Re-instantiation puts a parent named by two relations into the scene **three times** — coincident shells that z-fight and double every QA count |
| **AP-21 · Treating `tension` as a neutral `1.0`, or an edge pair as always sane** | `0.0` is the straight transition; at `1.0` the worked blend overshot its parent by **295.64 cm**. A **coincident** edge pair yields a **zero-area surface** and a **same-side** pair bulges outside both parents — up to 111 cm on a 200 cm patch. All sixteen combinations commit and all four properties read back exactly, so **no read-back detects any of the three** (§6.7.5) |
| **AP-22 · Assuming `trim:true` cuts the surface** — or counting "a second surface appeared" as evidence that it does | It does not. `trim:true` adds the **parent's untrimmed `NURBSCVSurface` copy** to the relation's set; a profile spanning the full vault width produced output **byte-identical** to a small one. Emit `trim:false` and expect **0** surfaces. An aperture is a Boolean-modifier or surface-split job (§6.7.5) |
| **AP-23 · Filtering committed sub-objects by comparing an index to a pre-commit ordinal** | `parent:` / `rail:` / `appendCurve` take the **pre-commit** `nset.numObjects` ordinal; `getObject rset i` is a **committed** 1-based index. Two 3 × 3 point surfaces plus a blend append as 1, 2, 3 and commit as 21 sub-objects. `k > <ordinal>` silently reads the wrong object. Filter by **`classOf`** (§6.7.6) |
| **AP-24 · Quoting `node.min` / `node.max` as the NURBS geometry** | A node bbox is inflated by the node's own tessellation — a closed `NURBSPointCurve` over a `750…1050 × 375…525` rectangle reports `714.645…1080.17 × 286.503…617.732`. Sample **`evalPos`** (§8 route table) |

### 11.1 Context discipline

**Never probe** (`01` §6). **One bridge call per batch**: build in one, read back in one, delete in the
same call as the create. **Compute, don't transcribe** — verify the builder by recomputing an arc or a
lattice Z from `massing.json`, not by reading the emitted `.ms` back and nodding at it. **No bulk dumps
in the final message**; never read another agent's transcript. `07` §8.2 and §9.7 are read **once**.

---

## 12. Return contract

Return **exactly** this, **≤ 12 lines** — no file dumps, no JSON blobs, no transcript excerpts:

```
S3 <project id>
FILES: <path> (<n> lines) · <path> (<n> lines)
VALIDATOR: scripts/validate_specs.py --dir <specs_dir> --build -> exit <n>  (PASS <n> · FAIL <n> · WARN <n> · SKIP <n>)
G-41..G-54: <n> PASS / <n> SKIP — <for each SKIP, the reason the check could not be evaluated; G-54 always SKIPs at lint>
BUILDER: scripts/build_nurbs.py -> exit <n> · <n> sections / <n> surfaces (<by kind>) · <n> derivatives · surface index resolved by superclass, no literal index emitted
DEPENDENT: <n> dependent surface(s) (<kinds>) · G-50..G-53 <n> PASS / <n> FAIL · G-54 census <for each node: id -> expected, actual> · <"none in this spec" if there are none>
LIVE: nurbs.ms fileIn-ed in 3ds Max by the orchestrator, no error · <n>/<n> nodes present · <n> nodes deleted in the sweep · scene otherwise empty
MEASURED: worst |measured − expected| across all surfaces = <n> cm (tolerance linear_cm = <n> cm) · param domains <kind>=chord-length / [0,1] as expected · shell crown base <n> -> offset <n> for thickness_cm <n>
OBJECTIONS: <one line per defect in a file you do not own, naming file and line, or "none">
NOT-IMPLEMENTED: <n> — <one line each: what was asked, the class that exists, what is missing>
ESCALATED: <n> — <one line each: key path or form, the question, whether it is answered>
INCOMPLETE: <what you could not do, or "none">
```

Rules for the fields:

- **Line counts** are the real counts from disk. The validator and builder lines are only valid with a
  transcript: paste the exit code you observed; if you did not run one, write `NOT RUN` and say why on
  `INCOMPLETE`. **`SKIP` is reported separately from `PASS`**, never folded into it. **`MEASURED` is a
  number, not an adjective** — "matches" is not evidence; `0.0 cm worst deviation` is. If you measured
  nothing, say `NOT MEASURED`.
- **`DEPENDENT`** is not optional when the spec carries a dependent surface. **`G-54`'s actual count is a
  measurement and goes here** — if the first run threw, write the true number, not `NOT RUN`, and mirror
  it on `OBJECTIONS` (§6.7.2, AP-17). With no dependent surface, write `none in this spec`; that is the
  honest answer, not an omission.
- **`OBJECTIONS`** is where any `validate_specs.py` or `build_nurbs.py` behaviour that contradicts
  `07` §8.2 / §9.7 goes — including the §3 recipe-naming finding, the required/optional split on
  `tension1` / `tension2` / `seed` / `flip_trim`, **the builder's `1.0, 1.0` tension substitution against
  the measured `0.0` neutral** (§6.7.1), and **any census count that differs from §6.7.2 — a `blend`
  reporting 3 or a `trim` reporting 1** (§6.7.4). One line each, naming the file.
- **`NOT-IMPLEMENTED`** is for genuinely absent capability only, and it is never silently empty when
  something was requested that S3 cannot supply (§10.2). **The four dependent kinds are *not* an entry
  here** — `rail_sweep`, `two_rail_sweep`, `blend` and `trim` are specified and buildable (§6.7).
  **Cutting an aperture through `trim` *is* an entry** — the class projects and does not cut (§6.7.5).
  What belongs on **`ESCALATED`** is an unspecified key *meaning* — `parallel: false`,
  `flip_trim: true`, a tension **ceiling**, an `*ID` string format, a cross-set rail id, the lifetime of a
  relation after its parent is deleted (§10.1) — naming the key, the question, and whether a probe has
  answered it. **`INCOMPLETE`** is where you say you could not finish; a field that hides a gap is worse
  than an admission.

---

## 13. The recipe library — `specs/recipes/`

`01` row 12: `recipes/*.json` sits **outside** the S0 → S5 chain, and **only S3 reads or writes it.** Each
file is one real architectural situation a NURBS stage is asked for, in the **same schema as
`nurbs.json`** — envelope, `sections`, `surfaces`, `derivatives`, `origins`, `tolerances`.

| File | `project` | Situation | Kind / derivative |
|---|---|---|---|
| `barrel-vault.json` | `market-hall-01` | Semi-elliptical barrel vault over a 1200 × 600 rectangular plan: springing 400, rise 180, crown 580, 200 mm shell | `u_loft` + `thickness_cm` · `quad_panels` |
| `gordon-canopy.json` | `atrium-canopy-02` | Doubly-curved funnel canopy over a 900 × 900 court: three U curves at y 0/450/900, three V curves at x 0/450/900, corners 600, edge midpoints 450, centre 400 | `uv_loft` |
| `freeform-soffit.json` | `gallery-soffit-03` | Interpolating freeform plaster soffit over a 720 × 400 gallery ceiling, 3 × 5 lattice between 273 and 331 | `point_grid` |
| `diagrid-frame.json` | `diagrid-hall-04` | Hyperbolic-paraboloid entrance canopy over a 960 × 600 plaza, `z = 420 + 60·sx·sy`, saddle 360 → 480 | `point_grid` + `space_frame` |

**No recipe covers the four dependent kinds, and that is a recorded gap, not an oversight.** All four
templates are independent kinds, so `examples/nurbs.json` contains no `rail_sweep`,
`two_rail_sweep`, `blend` or `trim` surface: there `G-50`…`G-53` are *vacuously* satisfied and `G-54`
SKIPs. **Consequences you must plan for:**

- A dependent form has to be written into a project's `nurbs.json` from §6.7.1's keys and the worked
  fragment in `07` §8.2.7 — there is no template to instantiate.
- Do **not** copy an untested template into existence to fill the gap. A recipe is a template for a
  *tested* situation, and the first live run of a dependent spec is a measurement (§6.7.2), not a formality.
- `G-52` demands the parents are declared **earlier**, so a dependent recipe also needs the two or three
  independent surfaces it refers to, in one file, in order. Recipes that grew to eight kinds to express
  the real thing are the failure mode to avoid.

The gap goes on `ESCALATED` (§12) until S3's owner adds a tested dependent recipe.

### 13.1 What a recipe is, and is not

| Property | Value |
|---|---|
| `status` | **`draft`, always.** `locked` is a one-way promise about a project's agreed values; a template has none |
| `source.kind` | **`assumed`** — the numbers were chosen to demonstrate the kind, and no project input was read. `derived` would require `source.reference` to name a spec file that exists in the project (`G-6`), which a template cannot do |
| `spec` | **the recipe's own base name** (`07` §3.1 / `G-2`). It is *not* `"nurbs"`, and §3 explains what that costs |
| `origin_inputs` | **`[]`.** There is no upstream project to name |
| `origins` | Full coverage, every entry `derived` with a non-empty `derives_from` **naming this file's own paths** — the honest form for a template that read nothing |
| Numbers | Arithmetically consistent. A vault's springing, crown, rise and shell make sense together; the hypar is a real saddle; the soffit is asymmetric because a freeform soffit is |
| **Never** | an invented `formula` key. No such key exists in §8.2, and a builder that met one would have to ignore it — which is exactly the v2 failure mode |

### 13.2 Instantiating a recipe into a project

Verified sequence — the first two steps are not optional and both fail loudly without them:

```
copy specs/recipes/<recipe>.json  <project>/specs/pipeline/nurbs.json
# 1. rewrite "spec" to "nurbs"            -- else build_nurbs.py refuses: G-2
# 2. rewrite "project" to the real project id, and "status" to "draft" while in progress
# 3. replace every origin_inputs and derives_from path with real keys in massing.json / dimensions.json
# 4. python scripts/validate_specs.py --dir <project>/specs/pipeline --build
# 5. python scripts/build_nurbs.py --in <project>/specs/pipeline --out <project>/specs/pipeline
# 6. fileIn nurbs.ms in live Max (orchestrator), measure per section 8
```

| Validator result on a recipe, verbatim | What it means |
|---|---|
| `G-1 SKIP … not a file in the 07 section 4 inventory … ignored`, and `G-41`…`G-49` produce **no rows at all** | **Expected under the recipe's own name** — the schema is resolved from the stem (§3). It is *not* a pass; those nine rules were **not evaluated** |
| `G-46 SKIP … no cv_grid surface declares an order` | Correct. Three of the four recipes have no `cv_grid`; the rule has nothing to compare |
| `G-48 SKIP … derivatives[] is empty` | Correct for `gordon-canopy` and `freeform-soffit` |
| `G-49 SKIP … neither dimensions.json nor massing.json is present` | Correct, and honest: coverage held (`N` leaves, `N` entries, all derived), but the cross-file half is unproven. A template has no upstream project to resolve against |
| `G-1 FAIL … dimensions.json is not present` | An artefact of validating in an isolated directory, not a recipe defect. Only a real project satisfies it |