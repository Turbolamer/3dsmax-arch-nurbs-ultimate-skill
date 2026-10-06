# `_fix-b-notes.md` — banners for `railclone.md`, `tyflow-graphs.md`, `procedural-graphs.md`

**Date:** 2026-10-06 · **Owner of this pass:** fix-b · **Files modified:** 4 (3 references + the
`SKILL.md` index region) · **Live tools called:** none (no bridge; all facts supplied as measured data)

Closes the three **HIGH (b)** drift rows at `references/_drift-audit.md:22`, `:23`, `:25`, `:26`
and the related `SKILL.md:473` row at `:24`.

---

## 1. `references/railclone.md` — full `curve-construction.md` convention applied

193 → **250** lines. Original body retained verbatim below a fence.

| Element | Content |
|---|---|
| Banner | `OBSOLETE.` railClone not installed, by direct reading of the live tool list. `3dsmax-mcp_get_railclone_style_graph` is the only railClone tool in the schema and fails unconditionally; `get_railclone_style` / `set_railclone_style` / `get_railclone_output` **do not resolve at all** |
| Version-claim correction | The original *"verified in 3ds Max 2027 with RailClone Pro 7.3.5"* line is called out as **wrong twice over** — target is **2026.3.2**, plugin absent |
| Pointer | `14-chaos-scatter.md` §4 + `nurbs-architecture-recipes.md` (routing row 1). States plainly: **no railClone equivalent in this build** |
| `## Why OBSOLETE rather than rewritten` | 3 on-evidence points: no verified content to preserve (every step calls a non-resolving tool or the absent `RailClone_Pro()` class); the subject is a missing tool not a missing feature; the central deliverable — editing the graph in place — has no counterpart, and translating the patterns to MAXScript arrays would be a new design, which the standing rule forbids |
| `## Routing table` | 7 rows: `get_railclone_style_graph` → **nothing equivalent**, use reference instancing; `set_railclone_style` → nothing (no guarded setter, no `style_token` locking); `get_railclone_output` → `execute_maxscript` on `node.min`/`max`/`objects.count` + `capture_viewport`; **A2S/L1S/`Offset` → `n = copy src` then `n.baseObject = src.baseObject`, `setCopyMode` absent and a plain `copy` shares nothing**; repeated multi-storey facade → `facade_tables.py` → `place_components.py` under `max-facade.md`/`max-assembly.md`; scatter → **`ChaosScatter` only** (forestPack absent too; `CScatter` is `NotCreatable`); `limit_matid` edge limiting → `setMaterialID` is native and still works, but no generator remains to limit |
| Fence | `---` + *"Everything below this line is the original file … Do not execute it. Do not cite it. Do not copy from it."* + `---`, then the original `# RailClone modeling` heading and body unchanged |

Verified substitutes were quoted from in-repo measured sources, not invented:
`14-chaos-scatter.md:123` (instance route), `:121` (Chaos Scatter), `nurbs-architecture-recipes.md:18`
(repeated-facade instancing), `maxscript-splines-shapes.md:230` (`setMaterialID` signature).

## 2. `references/tyflow-graphs.md` — same convention

56 → **107** lines. Original body retained verbatim below a fence.

- **Banner** names **all 14** `3dsmax-mcp_tyflow_*` tools explicitly, matching the corrected tally at
  `CHECKPOINT.md:1013` (**14, not 13**).
- **Pointer:** `14-chaos-scatter.md` §4 + `02-mcp-live-orchestration.md`. States plainly **there is no
  tyFlow equivalent**, and notes the specific reason the file cannot even be started: its first step
  is `get_tyflow_graph`, which does not exist.
- **Why obsolete:** 3 points — every step depends on the absent plugin; the subject is covered better
  by Chaos Scatter's measured parameter map; the "Physics gotchas" section is labelled *live-verified,
  tyFlow 2.05 / Max 2027*, a version pair this build does not have, so those numbers describe an
  absent plugin rather than a fact about this Max.
- **Routing table**, 8 rows, per the brief: distribution → `ChaosScatter` (`targetNodes` /
  `modelNodes` / `modelFrequencies` / `seed` / `instanceCountLimit`, `seed` 1…31337 and **data**);
  density patterning → same call; physics → **PhysX or Max particles**; animated motion → keyframed
  transforms + `assign_controller` / `add_controller_target` / `set_controller_props`; emitter shapes →
  native primitives; graph read-back → **nothing equivalent**; `create_tyflow_preset` → nothing
  equivalent; operator names → read live, because introspection tools lie.
- **Fence** as in `railclone.md`, worded for this file: *"a tool that is not in the connected bridge,
  against a plugin that is not installed."*

## 3. `references/procedural-graphs.md` — **split banner, not a whole-file fence**

62 → **95** lines. Deliberately *not* fenced: the Data Channel half is live.

- **Split banner at the top** with two explicit verdicts: **Data Channel half LIVE and usable**, with
  the six real tool names spelled out; **Max Creation Graph half DEAD**, with all twelve `mcg_*` names
  enumerated, plus `curve_model` absent. States **no substitute exists** for MCG.
- **Pointer** to `arch-modifiers-and-procedural-reference.md` (the other MCG document, which received
  its retraction at P4b-r and carries the real 32-operator vocabulary), and names the repo's actual
  graph substitute: `max-orchestrator.md` + `07-spec-grammar.md` driving
  `build_spec.py` → `build_nurbs.py` → `facade_tables.py` → `place_components.py` — *specs in, geometry
  out*, not a runtime graph.
- **Two invented Data Channel tool names fixed in place**, per the brief, so the surviving workflow is
  correct: `list_dc_operators` → replaced with the real vocabulary (`list_dc_presets` for installed
  presets, `inspect_data_channel` for live operator/property names, and an explicit statement that **no
  operator-catalogue tool exists**); `manage_data_channel_stack` → replaced with `set_data_channel_operator`
  for edits plus `add_data_channel` (`operators` / `order` / `display`) for stack entries, with an
  explicit statement that **no stack-management tool exists**. A dated `2026-10-06 correction` bullet
  records the substitution.
- **Inline OBSOLETE marker** added directly under the `## Max Creation Graph` heading, so a reader who
  lands mid-file cannot miss it. The MCG body itself is untouched.
- Version-labelled **"Max 2027"** statements inside the Data Channel half are flagged in the banner as
  **unverified against 2026.3.2, not disproven** — the repo's standing rule forbids rewriting on
  suspicion.

## 4. `SKILL.md` — index region only, lines 472–475

Not a git repository (`fatal: not a git repository`), so verification was by re-reading the region:
**489 lines before and after**, and the single `edit` call replaced exactly the four contiguous rows
`procedural-graphs.md`, `curve-construction.md`, `railclone.md`, `tyflow-graphs.md`. Nothing outside
that region was touched.

- The false claim on the `curve-construction.md` row — *"the same convention as
  `references/railclone.md` and `references/tyflow-graphs.md`"* — is now **true**, because those two
  files carry a top banner, a "read this instead" pointer and a fenced non-executable body. The row
  was reworded to state the convention as applied on 2026-10-06 and to record that it was **verified**
  by reading those files, and it now notes the one deliberate exception: **`procedural-graphs.md` does
  not follow the fence convention because it is half live.**
- The two rows below it, which already said OBSOLETE, were upgraded to describe what the files now
  actually contain (router + fence; no equivalent tool; named substitutes), so the index is internally
  consistent with the files.
- The `procedural-graphs.md` row was changed from **"Partially obsolete … ignore it"** — which told a
  reader to ignore half a file that is live — to the split verdict with the real six tool names.
- The forward claim in `curve-construction.md:6-7` ("Same convention as `references/railclone.md` and
  `references/tyflow-graphs.md`") is **now accurate and needs no change**; that file was not modified.

## 5. Could not do / left for the orchestrator

1. **`references/14-chaos-scatter.md:124`** still describes `references/procedural-graphs.md` as
   *"**OBSOLETE** (moot, not wrong)"*. That is now **imprecise** — the file is half live. Not owned by
   this pass; one-line correction recommended.
2. **`references/_drift-audit.md:22-26`** are the audit record of the very rows this pass closes. Left
   as a point-in-time record; the orchestrator may want to stamp them closed in `CHECKPOINT.md`.
3. **`references/curve-construction.md`** was read as the style model but not modified (not owned).
4. `install_skill.py` was **not** run, per instruction — the archive is the orchestrator's to rebuild.
5. **No live verification was performed**, as instructed. Every claim in the three banners is either
   (a) supplied measured data, or (b) quoted from an already-verified in-repo source, cited inline.