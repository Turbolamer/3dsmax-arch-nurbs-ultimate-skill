# P1 Audit — `references/` inventory, dedupe, and rewrite list

Status: closed. This file is the durable record of what P1 measured. Later stages should read it
instead of re-investigating. Every claim below is either (a) copied from the verified evidence
brief `p1-evidence.md`, or (b) a measurement repeated here with the command that produced it.

Standing rule inherited from the brief: **MAXScript execution is the only ground truth.**
Reflection tools lie (see section 5 of the brief).

---

## 1. Scope and method

Examined:

- All 20 files in `references/` (18 pre-existing + 2 written during this stage).
- `SKILL.md` (20,139 bytes).
- `snippets/nurbs_arch_library.ms` (10,738 bytes).
- `scripts/install_skill.py` (checked for the standalone-install argument only).

Method — findings are measured, not judged:

- **Dedupe** came from `diff <(tr -d '\r' < local) <(tr -d '\r' < shared) | wc -l`, i.e. byte
  comparison with CRLF normalised, not from reading the files. Re-run result is in section 2.
- **Fiction claims** came from the brief's "Tools that ALWAYS fail" list (14 tyFlow tools,
  `scatter_forest_pack`, `get_railclone_style_graph`) and from the absent-plugin list
  (forestPack, forestLite, tyFlow, railClone, phoenixFD), plus a name cross-check of every tool
  string appearing in each file against the connected `3dsmax-mcp_*` toolset.
- **"Real API" claims** are accepted only where the brief records an executed probe
  (`snippets/nurbs_arch_library.ms` loading and printing `MCP_NURBS_Arch loaded`, plus the NURBS
  relational transcript in brief section 2).
- **VERIFY** verdicts are deliberate. They mean "plausible, not yet probed claim-by-claim", and
  are *not* a polite synonym for "probably fine". An earlier stage used a weaker version of that
  judgement to declare the NURBS API fictional. That conclusion was wrong and is reversed.

A note on counts: the pre-existing set is 18 files, not 17. `references/02-mcp-live-orchestration.md`
and `references/12-nurbs-gotchas.md` were rewritten in this stage and are the two newest files;
the other 18 carry the original bundle timestamp.

---

## 2. Dedupe against `3dsmax-mcp-dev` — measured

Shared source: `C:\Users\Turbolamer\.agents\skills\3dsmax-mcp-dev\`. Note the shared files sit
**flat in the skill root**, not in a `references/` subdirectory. Nine of ours are byte-identical
after CRLF normalisation; the tenth differs.

| File | Diff lines (CRLF normalised) | Local bytes | Shared bytes |
|---|---|---|---|
| maxscript-3dsmax-objects.md | 0 | 15215 | 15679 |
| maxscript-animation-controllers.md | 16 | 16083 | 15887 |
| maxscript-common-patterns.md | 0 | 12907 | 13337 |
| maxscript-core-syntax.md | 0 | 13632 | 14110 |
| maxscript-materials-textures.md | 0 | 16580 | 17099 |
| maxscript-mesh-poly-ops.md | 0 | 14447 | 14890 |
| maxscript-rendering-cameras.md | 0 | 14178 | 14679 |
| maxscript-scripted-plugins.md | 0 | 14768 | 15237 |
| maxscript-splines-shapes.md | 0 | 13940 | 14386 |
| maxscript-ui-rollouts.md | 0 | 15685 | 16166 |

The per-file byte deltas in the 0-diff rows are exactly the CR count: the shared copies are
CRLF, ours are LF. That is the only difference and it is why `tr -d '\r'` is required before
diffing. Comparing without normalisation produces a false "every file differs" result.

**Size.** Measured total for the ten local files: **147,435 bytes = 144 KB** (shared total
151,470 bytes = 148 KB). The brief states 164 KB; that figure was not reproducible from
`stat`, and the discrepancy is not material to the decision — either number is "a sixth of the
reference payload". Use 144 KB when quoting measured size.

### The one delta, and why it matters

`maxscript-animation-controllers.md` is the only file with any content difference, and the delta
makes our copy strictly worse:

- Our copy has **11 extra lines** at lines 263–273 instructing the reader to *"prefer
  `script_controller`"*, describing binding maps and compilation/runtime/output-type error
  reporting.
- **`script_controller` does not exist in the connected server.** It is not in the toolset and it
  is not in the brief's verified tool list. The instruction sends readers to a tool that cannot
  be called.
- The remaining 2 diff lines are the ordering of `c.script = "sin(F * 3) * 25 + 50"` inside the
  code block — cosmetic.

Conclusion: our copy was edited to add a capability that does not exist, on top of a file that
was otherwise an exact duplicate. **If dedupe happens, take the shared version, not ours.**

### Recommendation: vendor, and fix the one file

Do **not** delete these ten files and point readers at the shared skill by path.

Reasoning:

- Against vendoring: 144 KB of exact duplication, and two copies drift silently — which is
  precisely the failure this audit caught. The shared copy is the better copy here.
- For vendoring: `scripts/install_skill.py` exists, so this skill is expected to install and run
  standalone on a machine that has no `3dsmax-mcp-dev`. A path reference to another skill's
  directory is a hard external dependency that a standalone install cannot satisfy, and it turns
  a documentation lookup into a filesystem probe that can fail silently at read time.
- The drift risk is manageable and is not currently being managed. It was found by accident in
  this stage. Vendoring plus one rule ("these ten are frozen copies of the shared skill; do not
  edit locally") removes the failure mode that produced this finding.
- The fix is one file, not ten: overwrite `maxscript-animation-controllers.md` with the shared
  version and drop the `script_controller` section.

Recommended action for a later stage, not executed here:

1. Replace the local `maxscript-animation-controllers.md` with the shared copy (drops the phantom
   `script_controller` guidance).
2. Record in the shared skill's own notes that these ten are vendored, so the next editor knows
   which side is authoritative.
3. Leave the other nine untouched. Re-run the section 2 diff as a regression check; it should
   report 0 lines for all ten afterwards.

---

## 3. Per-file verdict table

| File | Size | Verdict | Action needed |
|---|---|---|---|
| `nurbs-complete-guide.md` | 34 KB | VERIFY | **Do not rewrite.** NURBS API is real and verified working; the earlier "fiction" verdict was wrong and is reversed. Verify claim-by-claim against live Max. |
| `nurbs-architecture-recipes.md` | 19 KB | VERIFY | Same reversal. Recipes depend on the guide; verify each against the executed NURBS transcript. |
| `arch-modifiers-and-procedural-reference.md` | 7 KB | VERIFY | Contains MCG tool names that do not exist: `mcg_create_graph`, `mcg_apply_patch`, `mcg_get_context`, `mcg_list_graphs`. Data Channel modifier half is real and has tools. Strip or correct the MCG half. |
| `architecture-exterior-pipelines.md` | 15 KB | VERIFY | Heavily caveated. Names `scatter_forest_pack` and `cosmos_*` tools that do not exist, and recommends Forest Pack scatters when Chaos Scatter is the only working option. Its dimensional guidance (floor heights 300–420 cm, slab 25–30 cm, parapet 90–120 cm, curb 15 cm) is plausibly reusable — re-derive against the spec stage rather than trusting. |
| `curve-construction.md` | 6 KB | REWRITE | Written entirely against nonexistent `curve_model` / `inspect_curve` / `edit_curve`. Full rewrite brief in section 4. |
| `railclone.md` | 10 KB | OBSOLETE | RailClone is not installed; `get_railclone_style_graph` always fails. Substitute: MAXScript arrays plus `clone_objects` in instance mode. |
| `tyflow-graphs.md` | 7 KB | OBSOLETE | tyFlow is not installed; all 14 tyFlow tools always fail. No substitute needed — this is a capability the environment does not have. |
| `procedural-graphs.md` | 8 KB | VERIFY | Data Channel modifiers are real and have tools (`add_data_channel`, `set_data_channel_operator`, `inspect_data_channel`, `load_dc_preset`, `list_dc_presets`, `add_dc_script_operator`). The MCG half is not real: 12 `mcg_*` names found, none connected. |
| `maxscript-*.md` (10 files) | 144 KB | DEDUPE | See section 2. Only `maxscript-animation-controllers.md` has a delta, and ours is worse. |
| `02-mcp-live-orchestration.md` | 30 KB | KEEP AS-IS | Corrected during this stage. |
| `12-nurbs-gotchas.md` | 33 KB | KEEP AS-IS | Rewritten during this stage; carries the corrected NURBS headline. |

Verdict counts: 2 KEEP, 5 VERIFY, 1 REWRITE, 2 OBSOLETE, 10 DEDUPE (grouped).

Nothing is marked KEEP AS-IS among the pre-1980 files. That is expected: those files predate the
live probe that invalidated their central premise.

---

## 4. `curve-construction.md` rewrite brief

### 4.1 Why it must be rewritten

Every capability the file documents is fictional. Six references to three tool names that are not
in the connected toolset:

- `curve_model` (lines 3, 10, 26) — including a `preview` mode and a definition/parameters schema.
- `inspect_curve` (lines 5, 106) — including a `capture=true` return contract.
- `edit_curve` (lines 5, 112) — including a token-based preflight protocol.

There is no partial salvage. A patch that keeps the structure would keep the fiction, because the
file's whole shape (declarative model call, token preflight, capture-based inspect) describes a
tool family that was never connected. Rewrite from zero against the real surface below.

### 4.2 What the real capability is

**Shape creation.** Shapes are creatable through `create_object` and through
`execute_maxscript`. Verified shape constructors: `Rectangle`, `Circle`, `Ellipse`, `Arc`,
`Line`, `NGon`, `Star`, `Donut`, `Helix`, `Text`, `PipeObject`, `Half Round`, `Quarter Round`,
plus `Point Curve` and `CV Curve`.

Trap to document prominently: **`introspect_class "Rectangle"` reports `paramBlocks: []`, which is
wrong.** `Rectangle()` has `width` / `length`, default 25.0, both assignable. Reflection on shapes
is broken; construct and read instead. This is the same class of error that produced the false
"NURBS is fiction" conclusion, so it belongs in the rewritten file as a named trap.

**Spline editing.** The real path is the `SplineShape` interface: `addNewSpline`, `addKnot`,
`setKnot`, `updateShape`. Build a `SplineShape` on a node, mutate its knot arrays, then call
`updateShape` to push the edit into the shape's vertex array. There is no preview/capture token
step; the node is the transaction boundary.

**Modifier route.** The `Edit Spline` modifier is present in the modifier list and is the
higher-level alternative to hand-editing knot arrays.

**Surface modifiers on shapes.** `Sweep`, `Lathe`, `Extrude` — all three verified creatable, and
all three verified to apply to a `Rectangle`. All three are **rejected on geometry** such as a
`Box` with `Modifier is not appropriate`. That error string is the signal that a shape-only
modifier was pushed onto a geometry node; it is not a failure of the modifier itself.

### 4.3 Proposed section outline for the rewritten file

1. **Scope and the one-sentence rule** — shapes are made with `create_object` /
   `execute_maxscript`; there is no `curve_model`. Say this in line 1 so a reader who arrived from
   an old copy of this skill stops immediately.
2. **Shape constructor catalogue** — the 15 verified constructors as a table: name, key
   parameters, typical use. Include the `Rectangle` `width`/`length` default-25.0 note here.
3. **Reflection trap** — `introspect_class` on shapes returns empty `paramBlocks`. Construct and
   read. One short subsection, not a lecture; link to `12-nurbs-gotchas.md` for the general rule.
4. **Building a profile to sweep** — `SplineShape` walkthrough: `addNewSpline`, `addKnot`,
   `setKnot`, `updateShape`, with a complete runnable snippet. This is the file's core payload and
   should be the longest section.
5. **Knot editing reference** — `Edit Spline` modifier, and when to prefer it over direct knot
   arrays (interactive tweaking vs. scripted generation).
6. **Shape-to-surface modifiers** — `Sweep`, `Lathe`, `Extrude`. For each: verified behaviour on a
   shape, and the `Modifier is not appropriate` rejection on geometry.
7. **Arc-length and continuity notes** — only what is verified. Mark the rest UNVERIFIED inline.
8. **Failure modes table** — fictional tool name → real replacement. This doubles as the migration
   table for anyone who read the previous version.
9. **Verified / unverified ledger** — the explicit split required by 4.4.

### 4.4 Explicitly UNVERIFIED — needs a live probe before the file ships

- **Sweep's sub-object / profile-assignment parameter names.** `Sweep()` is confirmed creatable
  and confirmed to attach to a shape; the parameter names for assigning the profile curve and the
  orientation/banking controls were not read. Do not invent them. Probe by constructing, then
  reading the modifier's interface from a live instance.
- Whether `Lathe` and `Extrude` expose the same interface shape as `Sweep` or differ.
- `Point Curve` and `CV Curve` exact constructor keywords and parameter names — the class identity
  is established, the calling convention is not.
- `Edit Spline` parameter names, and whether it round-trips against direct `SplineShape` knot edits.
- Whether shape modifiers can be added *before* vs *after* the shape is assigned to a node, and
  whether ordering changes the result.
- Knot-array capacity behaviour on `addNewSpline` for large profiles.

Rule for the rewriting stage: anything in this list that is not probed gets written into the file
as UNVERIFIED with the probe named. It does not get a plausible value.

---

## 5. `SKILL.md` status

As inherited, `SKILL.md` (20,139 bytes) was unusable: its Architecture & Exterior Modeling
decision matrix routed to roughly **35 tool names that do not exist in the connected server**. An
agent following it would fail on the first call.

The corrected decision matrix is now at `SKILL.md` section 2, "Architecture & Exterior Modeling
Decision Matrix" (line 39), rewritten during this stage. That rewrite is what makes the skill
usable; this audit does not duplicate its content and does not restate its routing rules.

`SKILL.md` also remains scheduled for a full rewrite at **P10**, which owns `SKILL.md`, `AGENTS.md`,
`agents/max-orchestrator.md`, `scripts/lint_script.py`, `scripts/check_skill_md.py`, and the
updated `install_skill.py`. The P10 rewrite should treat this audit's verdict table as the
authoritative statement of which reference files may still be cited.

Tool-name hazard worth carrying forward: several names in the connected toolset belong to the
**Rhino** MCP server, not 3ds Max — `get_document_summary`, `get_objects`, `get_object_info`,
`create_object` (different schema), `analyze_objects`, `section_profile`, `boolean_union`,
`measure_objects`, and all `gh_*`. Note in particular that `create_object` exists in both servers
with incompatible schemas. P10's router must prefix-qualify.

---

## 6. Open questions for later stages

1. **Sweep profile-assignment and sub-object parameter names.** Route: **P5** (facade grid and
   component registry) or the stage that first needs a swept profile. Blocked on a live probe; do
   not guess.
2. ~~**`NURBSControlVertex` construction route.**~~ **RESOLVED in P1-b, and the premise was false.**
   The class constructs (`NURBSControlVertex <pt3> [<weight>]`). The real defect was that `setCV`
   rejects a bare point — `Unable to convert: [0,0,0] to type: NURBSControlVertex`. All four library
   bugs are fixed and every function executed; see `references/12-nurbs-gotchas.md` §2.
   A fourth bug was found there too: `close <crv>` returns `"OK"` without mutating, so
   `NURBSCVCurve` cannot be closed at all. Route for the remaining recipe verification: **P4**.
3. **QuadPatch control-point access.** Whether QuadPatch exposes an editable control-point
   interface usable from script, and under what class. Not in the brief's verified list. Route:
   **P4**.
4. **Pre-export tessellation path: `Disp Approx` vs `Tessellate`.** Which is correct for
   production export, and what tolerance settings each takes. Route: **P9** (export).
5. **Corona material parameter names beyond class existence.** The brief confirms 16 Corona
   classes are constructible but records no parameter names for any of them. Route: **P7**
   (Corona materials and UVs), which is explicitly tasked with verifying that each class
   constructs.
6. **ChaosScatter sub-object wiring semantics.** The parameter map in brief section 6 is complete
   at the property level, but the meaning of `scatteringSelection` values 66–68 and the correct
   sub-object selection workflow for `targetNodes` / `modelNodes` were not exercised. Route:
   **P6** (assembly + Chaos Scatter).
7. **Renderer mismatch.** The active renderer reports as `Arnold`; the user's production renderer
   is Corona. Renderer detect/set behaviour is unowned. Route: **P7**, with **P10** informed.
8. **Reusable dimensions in `architecture-exterior-pipelines.md`.** Floor heights 300–420 cm, slab
   25–30 cm, parapet 90–120 cm, curb 15 cm are plausible but unmeasured. Route: **P2** (spec
   grammar and input stage), which owns the dimension schema.

---

## 7. What this audit does not authorise

- No file other than this one was created, modified, or deleted by P1.
- The section 2 dedupe recommendation is a recommendation. The overwrite of
  `maxscript-animation-controllers.md` with the shared copy is **not** executed and belongs to a
  later stage, together with the regression re-diff described in section 2.
- No OBSOLETE file was deleted. `railclone.md` and `tyflow-graphs.md` describe capabilities the
  connected environment does not have; deleting them loses the record of why the capability is
  missing. Removal is a P10 call, and should be accompanied by whatever substitute guidance
  replaces them.
- No VERIFY verdict was upgraded or downgraded here. Upgrading one requires a live probe; the
  stage list in section 6 says which stage owns each probe.