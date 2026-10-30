# Dangling-reference register re-check — per-row verdicts, evidence, and fixes

**Date:** 2026-10-30
**Scope:** the `CHECKPOINT.md:880` register *"Dangling references still routing to bogus tools
internally"* and its six named `references/*.md` files, plus `references/procedural-graphs.md`
(checked for coherence, not registered).
**Method:** offline documentation sweep. **No 3ds Max and no MCP tool was called.** No file outside
the seven `references/*.md` and this artifact was touched.
**Authority used for the absent-tool inventory:** `AGENTS.md` §"Two absent tool families, confirmed"
and §"MCP tool-name collisions"; `references/00-audit-p1.md` §3 (per-file verdict table) and §4.1;
`references/02-mcp-live-orchestration.md` §3 (the 15 always-fail tools) and §4 (verified routing
table); `references/_closeout-evidence.md`; and the **live 117-tool `3dsmax-mcp` catalog**, read as
metadata only (§"Catalog-completeness sweep" below).

---

## 1. Headline

| | |
|---|---|
| Token occurrences scanned (7 files, extended inventory) | **178** |
| **NEGATION** — text says the tool is absent / never call it / gives the substitute | **154** |
| **FENCED** — inside a region the file itself declares non-executable | **24** |
| **LIVE ROUTE** — routes the reader to the tool as if it worked | **0 after fixing; 4 before** |
| Files edited | **3** (`architecture-exterior-pipelines.md`, `arch-modifiers-and-procedural-reference.md`, `nurbs-complete-guide.md`) |
| LIVE ROUTE fixes applied | **4** (one file had two) |
| Register rows that are **stale** (nothing was ever wrong, or already fixed) | **3 of 6** |
| Register rows that were **substantively correct** (a real live route existed) | **3 of 6** |
| Register's own citation `00-audit-p1.md §7` | **wrong** — §7 is *"What this audit does not authorise"* and lists no dangling references. The real source is **§3**, plus §4.1 for `curve-construction.md`'s tool names |

The orchestrator's preliminary scan was **wrong in both directions**. It called
`nurbs-complete-guide.md` clean (0 bogus tokens) — that file carried a live route on its
**purpose line**, the first thing any reader reads. And it called
`architecture-exterior-pipelines.md` "the only row worth real scrutiny" — that row had exactly one
defect, while `arch-modifiers-and-procedural-reference.md`, which the orchestrator's detector
cleared as "they are the negations, my detector was wrong", had **two**.

The cause is the same in all three cases and is the central methodological result of this sweep:
**an inventory-based token scan cannot find a dangling route to a tool that is not in the
inventory.** Two of the four defects (`execute_python`, `set_modifier_property`) name tools absent
from `AGENTS.md`'s absent-tool list entirely. They were found only by diffing every backticked
identifier in the files against the live catalog (§5).

---

## 2. Per-row verdict table

Verdicts: **CLOSED** = the row was already clean, nothing edited. **FIXED** = a real LIVE ROUTE
existed and was corrected in this sweep. **OPEN** = still defective (none).

| # | Register row | Token occurrences | NEG | FENCED | LIVE ROUTE (pre-fix) | Verdict | Evidence (`file:line`) |
|---|---|---|---|---|---|---|---|
| 1 | `nurbs-complete-guide.md` | 4 | 4 | 0 | **1** | **FIXED** | live route at `:3` (`execute_python` in the Purpose line, no caveat anywhere in the file). Other 3 hits are correct negations: `:281` *"There is no `geometry_qa` tool in this bridge — verified absent at P4b-r"*, `:474` *"`geometry_qa` and `agent_viewport` do **not** exist in this bridge"* |
| 2 | `nurbs-architecture-recipes.md` | 26 | 26 | 0 | 0 | **CLOSED — row is STALE** | `:6` banner (*"There is no `geometry_qa`, `contact_check` or `agent_viewport` tool in this bridge"*), `:12` (*"`curve_model`, `loft_mesh` and `draw_spline` **do not exist** … `RailClone` is not installed … `inspect_curve` and `edit_curve` are absent too"*), `:16`–`:18` (table `Why` column, each naming the absent tool *and* the substitute), `:144`/`:201` (`mesh_edit` marked **UNVERIFIED**, "not in the live tool list inspected at P4b-r"), `:397` (*"Note what is *not* available: `RailClone` is not installed … `setCopyMode` does not exist"*) |
| 3 | `arch-modifiers-and-procedural-reference.md` | 16 | 16 | 0 | **2** | **FIXED** | live routes at `:7` (Purpose line listing `set_modifier_property` as a real tool) and `:79` (imperative *"When calling `add_modifier(…)` or `set_modifier_property`, use …"*). The 13 `mcg_*`/`curve_model` hits are all correct negations: `:4`, `:10`, `:196` (heading *"… (`mcg_*`) — NOT AVAILABLE"*), `:200`–`:201`, `:205`, `:215` (*"do not fall back to `curve_model`"*), `:86` (*"that recommendation is withdrawn"*) |
| 4 | `architecture-exterior-pipelines.md` | 70 | 70 | 0 | **1** | **FIXED** | live route at `:122`–`:123` — *"`draw_spline` + `add_modifier` as a two-tool sequence (**both tools exist**; …)"*, contradicting the file's own `:8` banner (*"`draw_spline` … **absent**"*) and `_closeout-evidence.md:20`. All other 69 hits are negations: `:8`–`:9`, `:128` (`boolean_operation` *"That route does not work here"*), `:156` (`inspect_mesh`/`mesh_edit` *"do not appear in the verified routing table"*), `:165`–`:166`, `:185`, `:192`–`:195`, `:213`–`:214`, `:220`, `:225`, `:229`, `:241`, `:257`, `:261`, `:268`–`:270`, `:291`, `:294`, `:308`–`:310`, `:339`, `:345`–`:348`, `:396`, `:407`, `:416`, `:442`–`:467`, `:478`–`:479` |
| 5 | `curve-construction.md` | 29 | 20 | 9 | 0 | **CLOSED — row is STALE** | Fully guarded by the 2026-10-06 treatment `AGENTS.md` records. Head OBSOLETE banner `:3`–`:14` (*"`curve_model`, `inspect_curve`, `edit_curve`, `draw_spline`, `loft_mesh` and `geometry_qa` are **absent** … nothing below the divider is executable"*); routing table `:37`–`:45` headed **"Absent tool \| Verified route in this build"**; divider `:87`–`:93` (*"**Do not execute it. Do not cite it. Do not copy from it.**"*). The 9 FENCED hits are `:97`, `:98`, `:99`×2, `:104`, `:120`, `:194`, `:200`, `:206` — all below the divider, i.e. the retained original body |
| 6 | `maxscript-animation-controllers.md` | **0** | 0 | 0 | 0 | **CLOSED — row is STALE, and should never have been listed** | Zero occurrences of any absent tool name *or* absent MAXScript global (`setCopyMode`, `rotationZ/X/Y`, code-form `angle`, `formattedPrint`, `fileExists`, `executeFile`, `runScript`, `getModifier(`). `00-audit-p1.md` §3 groups this file under **DEDUPE** ("Only `maxscript-animation-controllers.md` has a delta, and ours is worse") — a duplication finding, **not** a dangling-tool finding. The register appears to have absorbed it by mistake |
| 7 | `procedural-graphs.md` *(not registered — coherence check)* | 33 | 18 | 15 | 0 | **CLOSED — coherent exactly as `AGENTS.md` describes** | Split, not fenced, and with **no** whole-file router: the Data Channel half (`:31`–`:48`) is live and its only absent-name hits (`:35`) are a dated retraction (*"**Neither `list_dc_operators` nor `manage_data_channel_stack` exists.**"*). The MCG half carries a **section-level** OBSOLETE router at `:52`–`:56` (*"this entire section is dead … nothing below this line is executable"*), which fences the 15 hits at `:53`, `:60`×5, `:61`×4, `:62`×2, `:70`, `:71`, `:94`. The head banner `:12`–`:19` names all twelve `mcg_*` tools as nonexistent. **No edit made** |

---

## 3. The four fixes

All four use the negation style the neighbouring lines already use; none adds a router, none
rewrites a section, none touches verified content.

### 3.1 `references/nurbs-complete-guide.md:3` — `execute_python`

```diff
-> **Purpose:** … via `execute_maxscript` / `execute_python` within `3dsmax-mcp`.
+> **Purpose:** … via `execute_maxscript` within `3dsmax-mcp`. (**There is no `execute_python`
+> tool in this bridge** — it is not in the connected tool list, and nothing in this repo ever
+> executed it. `execute_maxscript` is the only execution route.)
```
Why it is a defect: `execute_python` is **not** among the 117 registered `3dsmax-mcp` tools, and it
appears **exactly once in the entire repo** — here. It is in no evidence file, in no routing table,
and in no transcript. `02-mcp-live-orchestration.md` §3.5 states the rule this violates: *"If it is
not listed in section 4's routing table and not in 3, it does not exist. Do not invent tool
names."* The file's Purpose line therefore routed every reader to a nonexistent entry point, with no
caveat, in a file that has no tool-availability banner at all.

### 3.2 `references/arch-modifiers-and-procedural-reference.md:7` — `set_modifier_property`

```diff
-> **Purpose:** … for modifiers (`add_modifier`, `set_modifier_property`) and **Data Channel** …
+> **Purpose:** … for modifiers (`add_modifier`) and **Data Channel** (`add_data_channel`).
+> **There is no `set_modifier_property` tool** in the connected toolset —
+> `references/02-mcp-live-orchestration.md` §4.6 records the verified route instead:
+> `add_modifier` takes a `params` string, and post-hoc edits go through
+> `inspect_modifier_properties` to learn real parameter names, then `execute_maxscript` to write
+> them (or `batch_modify` for one uniform property across many objects).
```

### 3.3 `references/arch-modifiers-and-procedural-reference.md:79` — `set_modifier_property`

```diff
-When calling `add_modifier(name=..., modifier=..., params=...)` or `set_modifier_property`, use
-the class name and parameter names in the table below:
+When calling `add_modifier(name=..., modifier=..., params=...)` — **there is no
+`set_modifier_property` tool**, so post-hoc parameter edits go through
+`inspect_modifier_properties` + `execute_maxscript` (§4.6 of
+`references/02-mcp-live-orchestration.md`) — use the class name and parameter
+names in the table below:
```
Why these two are defects: `02-mcp-live-orchestration.md:264` already says, in terms,
*"There is no `set_modifier_property` tool."* The catalog confirms it is not registered. So this was
a **direct contradiction between two reference files**, and the imperative form at `:79`
("When calling … `set_modifier_property`") is the strongest kind of dangling route: an instruction,
not a mention. Substitutes quoted above are verbatim from `02-mcp-live-orchestration.md:264`–`266`,
not invented; both `inspect_modifier_properties` and `batch_modify` are confirmed present in the
catalog.
`:22` also names `set_modifier_property`, but **inside an explicit retraction quote** (*"The text
this note replaces read: …"* / *"The **'always' was wrong**"*) → classified **NEGATION**, left
untouched.

### 3.4 `references/architecture-exterior-pipelines.md:122`–`:123` — `draw_spline`

```diff
-**UNVERIFIED-from-source:** `draw_spline` + `add_modifier` as a two-tool sequence (both tools
-exist; that pairing is not something a transcript covers), and `add_offset` as a bridge tool name.
+**UNVERIFIED-from-source:** `draw_spline` + `add_modifier` as a two-tool sequence (**`draw_spline`
+is absent** — banner above, and `references/_closeout-evidence.md` records it absent — so only
+`add_modifier` exists and the pairing cannot be run at all), and `add_offset` as a bridge tool name.
```
Why it is a defect: not an imperative, but a **false availability assertion**. The same file's `:8`
banner says `draw_spline` is **absent**; `_closeout-evidence.md:20` records it **absent** with the
substitute `splineShape` / `Line` / `Rectangle`; the catalog confirms it is not registered. A reader
who arrived at `:122` without reading `:8` would plan a two-tool sequence whose first tool cannot be
called. The `UNVERIFIED-from-source:` label is retained (it still correctly governs `add_offset`).

---

## 4. Classifier control — and an honest recall figure

A classifier that reports 0 defects has produced a result, not evidence. Three controls were run.

### 4.1 `git show HEAD~N` is not available; `git show HEAD:` is

`git log` for this repo returns **exactly one commit** (`779b979 Initial commit`), so there is no
`HEAD~N` pre-fix revision to diff against. However, this sweep's edits are **uncommitted
working-tree changes**, which makes `git show HEAD:references/<file>` the genuine pre-fix revision.
The three edited files were exported to scratch and re-scanned with the identical classifier.

**Ground-truth recall: 2 of 4.**

| Pre-fix defect | Classifier verdict | |
|---|---|---|
| `arch-modifiers-and-procedural-reference.md:79` `set_modifier_property` | **CAUGHT** — *"unit routes to the tool with no denial, no substitute, no fence"* | ✅ |
| `nurbs-complete-guide.md:3` `execute_python` | **CAUGHT** — same reason | ✅ |
| `architecture-exterior-pipelines.md:122` `draw_spline` | **MISSED** — called NEGATION, *"denial/substitute in same unit: not, not something, unverified"* | ❌ |
| `arch-modifiers-and-procedural-reference.md:7` `set_modifier_property` | **MISSED** — called NEGATION, *"denial/substitute in same unit: no, the original, there is no"* | ❌ |

**Both misses have one root cause, and it is worth recording:** the classifier tests whether the
*unit* contains a denial, but not whether the denial is **about the same token**. At `:122` the
denial words belong to a different clause ("that pairing is **not** something a transcript covers")
and to a caveat label ("**UNVERIFIED**-from-source"), while the claim about `draw_spline` is
affirmative ("both tools **exist**"). At `:7` the blockquote block merges the Purpose line with the
*following* MCG retraction, so "**There is no** `mcg_*` tool" masked an un-denied
`set_modifier_property`. **Unit-level negation detection is not token-scoped.** Anything that relies
on it alone will under-report exactly the subtle cases, which is why §5 exists.

### 4.2 Two structural controls — routers stripped from retained pre-fix text

Both files keep their own pre-fix text verbatim, so stripping the router reconstructs the pre-fix
file without guessing. The classifier **must** fire, or it is broken.

| Control | Construction | Result |
|---|---|---|
| **CTRL_A** | `curve-construction.md` lines 95–EOF (its own *"original file, retained … exactly as it was written"*) with the `:87`–`:93` divider removed | **6 LIVE ROUTE / 9 hits.** Fires on `Use \`curve_model\` when a shape is easiest to describe as…`, `Use \`draw_spline\` for a quick explicit world-point outline`, `Use \`inspect_curve\` / \`edit_curve\` for precise edits`, `curve_model(action="preview", …)`, `Pass this definition and parameters to \`curve_model\`` |
| **CTRL_B** | `procedural-graphs.md` lines 57–EOF (the MCG half) with the `:52`–`:56` OBSOLETE router removed | **11 LIVE ROUTE / 14 hits.** Fires on `Discover and fork with \`mcg_get_context\`, \`mcg_list_graphs\`…`, `Iterate with \`mcg_apply_patch\`…`, `use \`mcg_apply_modifier\``, `\`mcg_list_graphs\` scope tokens are…` |

Together these prove the **24 FENCED verdicts are load-bearing, not a blanket pass**: the same 20
lines classify as LIVE ROUTE the moment their file's own dead-region declaration is removed. CTRL_B
also caught a real bug in an earlier pass of this sweep — at whole-paragraph granularity it reported
14/14 NEGATION on that text, because consecutive markdown list items with no blank line between them
form one block and a single "not" in *any* item masked *all* of them. The final classifier splits
blocks into list items for that reason.

### 4.3 Manual ±5-line re-read (the step-4 cross-check)

**Two hits called NEGATION:**

1. `nurbs-architecture-recipes.md:17` (families `curve_model`, `loft_mesh`, `` `Loft` ``, `Loft(`) —
   read as a full table row. The `Why` cell reads: *"The verified loft path. `Loft` *resolves* as a
   class name but `Loft()` is **`NotCreatable`** — verified distinction, do not call it. `loft_mesh`
   and `curve_model(output:{kind:"loft"})` are both absent."* Every one of the four tokens is
   denied **in its own cell**, and the row's `Recommended Route` cell names the substitute
   (`NURBSULoftSurface`). Confirmed **NEGATION**. The preceding `:12` banner independently denies
   the same three tools.
2. `procedural-graphs.md:35` (`list_dc_operators`, `manage_data_channel_stack`) — read `:30`–`:40`.
   The bullet is a dated retraction: *"**2026-10-06 correction.** The original said … **Neither
   `list_dc_operators` nor `manage_data_channel_stack` exists.** The real vocabulary is six tools:
   …"*, and the four bullets below it route only to catalog-present tools (`list_dc_presets`,
   `add_data_channel`, `inspect_data_channel`, `load_dc_preset`, `set_data_channel_operator`,
   `add_dc_script_operator` — all six confirmed present). Confirmed **NEGATION**, and this is the
   evidence that the **live** half of a split file is genuinely live.

**Two hits called LIVE ROUTE (pre-fix text, ±5 lines):**

1. `arch-modifiers-and-procedural-reference.md:79` — context `:74`–`:84`. The five lines above are
   the file's legend for its own `NO` / `UNVERIFIED` markers; the five below are the modifier table.
   Nothing in the window denies `set_modifier_property`, and the sentence is an **imperative**
   governing the whole table ("When calling … or `set_modifier_property`, use the class name and
   parameter names in the table below"). Confirmed **LIVE ROUTE**.
2. `nurbs-complete-guide.md:3` — context `:1`–`:8`. The window is the title, the Purpose line, the
   "Read this file before authoring any `NURBSSet`" line, a rule, and the §1 heading. There is **no
   banner, no caveat and no retraction anywhere in the window or the file**, and `execute_python` is
   offered as a co-equal entry point with the verified `execute_maxscript`. Confirmed **LIVE ROUTE**
   — and the most exposed of the four, because it is the file's first substantive sentence.

---

## 5. Catalog-completeness sweep — how the two invisible defects were found

`AGENTS.md`'s absent-tool inventory is authoritative for what it lists, but it is **not complete**:
it was assembled from the plugin families and the P1 audit, so it never contained `execute_python` or
`set_modifier_property`. A scan built from it reports those files clean.

So the inventory was re-derived from the connected catalog (read as metadata only — **no Max call**):
the `3dsmax-mcp` server registers **117 tools**. Every backticked `snake_case` identifier in the
seven files was extracted and diffed against that list:

| | |
|---|---|
| Unique backticked `snake_case` identifiers | **104** |
| Present in the 117-tool catalog | 24 |
| Not in the catalog | **80** |
| …of which parameter / property / JSON-field / operator names (not tools) | ~50 (`after_hash`, `blend_modes`, `control_point_1`, `curve_token`, `expected_hash`, `face_output`, `floor_height`, `graph_version`, `head_cm`, `knot_ids`, `north_pt3`, `operator_ops`, `operator_order`, `profile_cm`, `ref_pt3`, `rounded_rectangle`, `sill_cm`, `spline_type`, `start_angle`, `tangent_arc`, `to_angle`, `u_param`, `vertex_input`, `vertex_output`, `current_built_in_shape`, `convert_subobject`, `remove_interior_patches`, `model_token`, `expected_model`, `expected_view`, …) |
| …of which tool-shaped **and already guarded** | `add_offset` (`:124` UNVERIFIED), `agent_viewport`, `boolean_operation` (`:128` "does not work here"), `contact_check`, `cosmos_search`/`cosmos_import` (`:339` "not in the connected toolset"), `create_lights` (`:407` UNVERIFIED), `create_mesh`, `curve_model`, `draw_spline`, `edit_curve`, `edit_vertices` (`:291` UNVERIFIED), `geometry_qa`, `get_railclone_style`/`set_railclone_style`, `inspect_curve`, `inspect_mesh` (`:156`), `lighting_capabilities` (`:396` "not in the verified routing table"), `list_dc_operators`/`manage_data_channel_stack`, `loft_mesh`, all 12 `mcg_*`, `mesh_edit`, `scene_qa`, `set_viewport` (`:463`/`:467` "absent or UNVERIFIED") |
| …of which tool-shaped **and unguarded → the two hidden defects** | **`execute_python`** (`nurbs-complete-guide.md:3`), **`set_modifier_property`** (`arch-modifiers…:7`, `:79`) |

Two corrections to vocabulary that the register's wording invites, both established by this sweep:

* **`scatter_forest_pack`, all 14 `tyflow_*` tools and `get_railclone_style_graph` ARE registered in
  the catalog.** They are not "bogus tool names"; they are **real tool names over absent plugins**,
  which is why they *"always throw"* rather than failing to resolve. `AGENTS.md` and
  `02-mcp-live-orchestration.md` §3 both phrase this correctly; the register's word "bogus" does not,
  and the replacement wording in §7 avoids it.
* **`create_object` and `capture_viewport` are present on the Max server** and are legitimate in
  these files, despite also being Rhino-server names. They were not counted as defects.

---

## 6. What could not be settled offline

* **Whether `add_offset` exists.** `architecture-exterior-pipelines.md:124` marks it
  UNVERIFIED-from-source; it is **not** in the 117-tool catalog, which on `02-mcp…` §3.5's own rule
  means it does not exist. The line is already correctly caveated, so no edit was made — but its
  label is weaker than the catalog evidence now supports. Upgrading it to a plain negation is a
  one-line change the orchestrator may want, and it is **not** mine to make under this ownership.
* **`cosmos_search` / `cosmos_import`.** `:339`–`:341` says they are *"not in the connected toolset"*
  yet also *"UNVERIFIED from this close-out, not confirmed absent"*, and tells the reader to probe
  `get_plugin_capabilities`. The catalog settles it: **neither is registered**, so they are absent,
  full stop. The file's hedged wording is now over-cautious rather than wrong. Left untouched (not a
  LIVE ROUTE — it says "Treat as **absent** for planning purposes").
* **Whether any *unbackticked* absent-tool name survives.** The identifier sweep keyed on backticks,
  which is how these files name tools throughout. A bare-word mention would be missed. The
  regex inventory sweep (§2 token counts) does not depend on backticks and found nothing further, so
  the risk is low but not zero.
* **Nothing was verified against live Max, by instruction.** Every absence claim above rests on the
  catalog's tool registry plus the repo's own transcripts — not on a fresh probe. Under this repo's
  standard that makes the *negations* second-hand; it does not weaken the four fixes, each of which
  only restates an absence the repo had already recorded in a file this one contradicted.

---

## 7. Proposed replacement wording for the `CHECKPOINT.md` register

The register is at `CHECKPOINT.md:880`–`883`. It is **wrong in its citation, wrong in three of its
six rows, and right in three** — so it should be replaced, not annotated. Paste-ready:

```markdown
## Dangling references routing to absent tools — CLOSED 2026-10-30

The register previously at this heading listed six `references/*.md` files as "flagged in
`references/00-audit-p1.md` §7, not yet fixed (outside P1's file ownership)". Re-checked per row
with evidence in `Audit/_dangling-register-recheck.md`. Both halves of that sentence were wrong:
**§7 is "What this audit does not authorise" and lists no dangling references** (the real source is
§3's per-file verdict table, plus §4.1), and **three of the six rows were already clean.**

178 absent-tool / absent-global token occurrences across the seven relevant files now classify as
**154 NEGATION · 24 FENCED · 0 LIVE ROUTE.** Four real live routes were found and fixed; no OBSOLETE
router was added anywhere.

| Row | Verdict | Evidence |
|---|---|---|
| `nurbs-complete-guide.md` | **FIXED** — `:3` offered `execute_python` as a co-equal entry point with `execute_maxscript`; that tool is not in the 117-tool catalog and appears nowhere else in the repo | fixed in place with the file's own parenthetical-negation style |
| `nurbs-architecture-recipes.md` | **STALE — was already clean.** 26/26 hits are negations (`:6`, `:12` banners; `:16`–`:18` table `Why` column; `:144`/`:201` `mesh_edit` UNVERIFIED; `:397`) | — |
| `arch-modifiers-and-procedural-reference.md` | **FIXED** — `:7` and `:79` both routed to `set_modifier_property`, which `02-mcp-live-orchestration.md:264` already states does not exist. `:22` names it only inside a retraction quote → NEGATION | substitutes quoted verbatim from `02-mcp…:264`–`266` (`inspect_modifier_properties` + `execute_maxscript`, or `batch_modify`) |
| `architecture-exterior-pipelines.md` | **FIXED** — `:122` asserted "`draw_spline` + `add_modifier` … (both tools exist)", contradicting its own `:8` banner and `_closeout-evidence.md:20` | 69 other hits are negations |
| `curve-construction.md` | **STALE — closed 2026-10-06.** Head OBSOLETE banner `:3`–`:14`, "Absent tool → Verified route" table `:37`–`:45`, divider `:87`–`:93`. The 9 hits below the divider are FENCED by the file's own declaration | — |
| `maxscript-animation-controllers.md` | **STALE — never belonged in this register.** 0 hits. `00-audit-p1.md` §3 groups it under **DEDUPE**, not dangling tools | — |
| `procedural-graphs.md` *(not registered)* | **Coherent as `AGENTS.md` describes** — split, no whole-file router: live Data Channel half (`:31`–`:48`) + section-level OBSOLETE router `:52`–`:56` fencing all 15 MCG hits | no edit |

**Method note that matters more than the verdicts.** Two of the four defects were invisible to any
scan built from `AGENTS.md`'s absent-tool inventory, because `execute_python` and
`set_modifier_property` are not in it. They were found only by diffing every backticked identifier in
the seven files against the **live 117-tool catalog** (104 identifiers → 80 not registered → 2
tool-shaped and unguarded). Any future re-check must derive its inventory from the catalog, not from
a hand-maintained list. Two controls prove the classifier can fire: the retained pre-fix bodies of
`curve-construction.md` and `procedural-graphs.md` with their routers stripped yield **6 and 11 LIVE
ROUTE** hits respectively, and the true pre-fix revisions (`git show HEAD:`, since the fixes are
uncommitted) give a measured **2-of-4 recall** — unit-level negation detection is not token-scoped,
and both misses are documented in the artifact.

**Vocabulary correction.** `scatter_forest_pack`, all 14 `tyflow_*` tools and
`get_railclone_style_graph` **are registered** in the catalog. They are not bogus names; they are
real tools over absent plugins, which is why they always throw. Keep saying "absent plugin", not
"bogus tool".
```

---

## 8. Reproduction

Scratch directory (this sweep's own; nothing shared, nothing outside it deleted):
`C:\Users\Turbolamer\AppData\Local\Temp\opencode\dangling-recheck\`

| File | Role |
|---|---|
| `scan.py` | pass 1 — ±6-line window classifier (superseded; too generous) |
| `scan2.py` | **token inventory** — the absent-tool and absent-global regex list, extended with the catalog-derived names. Imported by every later pass |
| `scan3_sentences.py` | pass 2 — sentence-level (superseded; markdown wrapping lost denials on the next line) |
| `scan4_paragraph.py` | pass 3 — paragraph-level + declared-dead-region (FENCED) detector; 0 suspects |
| `scan5_assert_control.py` | pass 4 — affirmative-availability-assertion override; **this is what caught `:122`** |
| `scan6_final.py` | **pass 5 — FINAL classifier.** List-item granularity, token-scoped assertion override, FENCED regions, and the CTRL_A / CTRL_B controls |
| `scan7_queue.py` | pass 6 — manual-review queue: every hit whose unit contains an affirmative word, with a backward-only negation test (122 queued, 11 unique locations, all read by hand) |
| `control_prefix.py` + `prefix/*.md` | the §4.1 control: the three true pre-fix revisions from `git show HEAD:`, and the 2-of-4 recall measurement |
| `scan_raw.json`, `pass3.json`, `pass4.json`, `pass5.json`, `pass6_queue.json`, `suspects.json`, `control_prefix.json` | machine-readable outputs |
| `CTRL_A_curve-construction_prefix_body.md`, `CTRL_B_procedural-graphs_mcg_half.md` | generated control inputs (§4.2) |

```bash
python scan6_final.py        # per-file counts, LIVE ROUTE listing, both controls
python control_prefix.py     # recall against the true pre-fix revisions
python scan7_queue.py        # manual-review queue
```

Files changed by this sweep — three, all inside its ownership:

```
 references/arch-modifiers-and-procedural-reference.md | 8 +++++---
 references/architecture-exterior-pipelines.md         | 5 +++--
 references/nurbs-complete-guide.md                    | 2 +-
```
