# max-components — S4b: locked `facade_grids.json` + `dimensions.json` → `components_registry.json`

> **Purpose:** S4b is the stage that turns a **partition** into **blocks**. It reads the locked grid S4a
> handed over, groups ~120 panels into a few dozen size classes, writes `components_registry.json`
> (`07` §8.4 — one entry per distinct `(kind, width, height)` class, with a stable parameter order, plus
> the family index P6 resolves a panel against), and emits the two placement tables its blocks are counted
> in. **S4b builds parametric blocks only.** The grid is S4a's; placements, cuts and layer application
> are S5.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage · Input | **S4b** (`PLAN.md` §4 row P5, `01` §3 "S4b") · `specs/pipeline/facade_grids.json` and `specs/pipeline/dimensions.json`, plus `assumptions.json` for the two `A-nnn` entries it declares |
| Output | `components_registry.json` (`07` §8.4), then `facade_table.csv` and `world_table.csv` (columns: contract §6) |
| Geometry produced | `component_types[]` · `components[]` — one block per distinct `(kind, width, height)` class · `families[]` — the resolution index. **No placements, no grid arithmetic, no MAXScript** |
| 3ds Max calls | One, and it is **the orchestrator's**: the prototype half of S4a's §7 gate, which this stage shares. **No probes** (§1.2) |
| Consumer · Precondition | S5 `assembly.json`, which resolves each panel to a block · S4a complete and locked (`07` §8.3, `G-57`…`G-64`) |
| Blocked by | A `facade_grids.json` that is not `locked`. Full stop (§2.2) |
| Findings | See `agents/max-orchestrator.md` §6.2. If this session produced a real finding — a measured value outside `tolerances.linear_cm`, a panel class the registry cannot carry, or a `(kind, width, height)` that is legal but wrong on site — record it in `<project>/IMPROVEMENTS.md`. **A session with no findings writes nothing and creates no file.** Format: `references/improvement-log.md` |

### 1.1 What S4b owns, and what S4b defers

S4b owns exactly four decisions: **how many blocks exist**, **what kind each one is**, **what its four
parameters are**, and **which family resolves a panel to it**. The cardinality is the whole point — the
grid is expected to hold 110–130 panels and those resolve to a few dozen blocks.

| **Never** built by S4b | Consumed by | Correct instrument |
|---|---|---|
| Axes, panels, panel kinds, the partition itself | **S4a** | `facade_grids.json` (`07` §8.3). A registry that recomputes the grid is a second source of truth |
| Placements, transforms, `instance_mode`, opening **cuts**, `layer_map` | **S5** | `assembly.json` (`07` §8.5). The registry is blocks; it places nothing |
| A material, a renderer, a UV rule | **nobody — S6 was cancelled 2026-10-05** | **Applied by hand by the user**; the hand-off is `agents/max-orchestrator.md` §5. `materials.json` is a **reserved stub**, not a deliverable and not a gate. `glazed_panel` is a **block**, not a glass (`07` §8.3.6) |
| Reveal depths, glazing build-ups, a frame profile | **nobody — S6/S7 were cancelled 2026-10-05** | A component's `parameters` and `variants` are where the **data** would live — S4b declares the four, nothing more, and no later stage reads them |
| Layer **application** to any node | **nobody — permanently** | **There is no way to assign an object to a layer from this bridge. Nine routes are ruled out and this is final, not an open question** (`agents/max-assembly.md` §6.3). Layer is **data** (`07` §8.1.3), no builder emits layer code (`G-79`), and **the user applies it in the Layer dialog** |
| A panel naming a component | **nobody** | The dependency is **one-way**: registry → grid. A reverse reference is a cycle and a `G-31` failure (§6.8) |

### 1.2 The one-MCP rule

**You may not touch the bridge.** S4b emits no MAXScript and no table of its own; the live gate is S4a's
§7 and the orchestrator performs it.

| Allowed | Forbidden |
|---|---|
| `3dsmax-mcp_get_scene_info` / `_get_scene_snapshot` to confirm the scene is empty **before** the gate | **Any exploratory probe.** A fact not in `CHECKPOINT.md` §"Verified facts" is escalated for an orchestrator probe, never opened by S4b |
| `3dsmax-mcp_delete_objects` on gate nodes, in the same call | Every tool in `01` §1.2 — the absent-plugin group, and the Rhino-server name collisions enumerated in `AGENTS.md` §"MCP tool-name collisions" and `02` §5 |
| `3dsmax-mcp_manage_layers` actions `list` and `create` — the eight names in `07` §8.1.4, nothing else | **`3dsmax-mcp_manage_layers` **object assignment** — and it is not "unknown": the action **does not exist**. The vocabulary is **exactly `{list, create, delete}`**, 40+ candidates rejected; with the eight MAXScript and tool routes that is **nine ruled out in total**. **Nobody solves this — the user applies layers in the Layer dialog** (`agents/max-assembly.md` §6.3) |
| `3dsmax-mcp_capture_viewport` for a human-facing record, after measuring | `3dsmax-mcp_introspect_class` / `_introspect_instance` / `_inspect_plugin_class` as **proof** — they lie (`AGENTS.md`, §"The one rule that matters most") |

> **`mcg_*` and `curve_model` do not exist in this bridge** (`AGENTS.md` §"Two absent tool families",
> confirmed at P4b-r). A registry that would need either is a missing **tool**, not a missing block kind
> — record it (§10.2), never hand-model it as if it were a `kind`.

Executing the shared gate on an already-computed CSV is **not** a probe (`01` §6).

---

## 2. Inputs and outputs

### 2.1 What you read

| Source | What you take from it |
|---|---|
| `specs/pipeline/facade_grids.json` | **The contract you build from** — `panels[]` (`id` `kind` `width_cm` `height_cm` `opening_ref`) and `panel_types[]` (`kind` `glazed` `frame_member` `opening_types`) — the only two arrays that matter here |
| `specs/pipeline/dimensions.json` | `tolerances` (copied **verbatim**) · `levels[]` and `facades[]` for cross-checking counts · `openings[].type`, to resolve the `door` / `entrance` question in the kind mapping (§6.3) |
| `references/07-spec-grammar.md` | **§8.4** the schema in full · **§8.4.1** `defaults` and why there are only two · **§8.4.2** the kind mapping · **§8.4.3** `components[]` · **§8.4.4** `families[]` · **§8.4.5** the join · **§9.8** `G-65`…`G-70` · §3.1 the lock gate · §5.2 `origins` granularity · §2 units |
| `references/09-defaults.md` | `D-CL-05` (modelled facade panel thickness, 3 cm, range `2 … 8`) and `D-FM-10` (panel joint width, 2 cm, range `1 … 4`) — the **only** two values S4b adopts, both *reference only* rows, both adopted inside their declared band (§6.1) |
| `references/11-layer-standard.md` | §1.6 `05_FACADE` · §3.1 naming, **N1** (no `-` in a name) · §6 checklist H1–H12 |
| `references/01-architecture-aec-workflow.md` | §2 the spec chain, **row 7** · §3 the S4b row — its gate (`parameters` as an ordered list) and its refusal case · §8 the CLI contract |
| `references/_p5-contract.md` | §5 the schema · §6 CSV columns · §7 `G-65`…`G-70` · §9 the live gate. **The authority for this stage** |
| `CHECKPOINT.md` | §"Scene units and placement semantics — VERIFIED (P3, 2026-10-04)" — the transcript of record for §7 · §"Reference claim-by-claim pass — VERIFIED (P4b-r, 2026-10-04)" for the delete/instance rule in §9 |

> **You do not read `massing.json`, `nurbs.json` or any sibling's transcript.** The chain is one-way and
> `origin_inputs` carries the paths (`07` §2, `01` §2). Reading prose is a stage bug.

### 2.2 What you own, and the lock gate

| Path | Action |
|---|---|
| `<project>/specs/pipeline/components_registry.json` | **Emitted by the builder.** Never hand-written, never hand-edited (§6.9) |
| `<project>/specs/pipeline/facade_table.csv` · `world_table.csv` | **Emitted by the builder**, and the registry's rows are in them. Never hand-patched |

**You modify nothing else** — not `references/07`, not `scripts/`, not `examples/`, not
`agents/max-facade.md`, not S4a's grid, not S1's or S2's locked files, not `CHECKPOINT.md`.
**`examples/assumptions.json` is the orchestrator's** — you verify `A-023` / `A-024` (§6.1) and never
write them.

> **A builder must refuse any spec file whose `status` is not `locked`, naming the file and the status
> it found** (`07` §3.1). Exit non-zero, before anything else is read.

| Found | Action |
|---|---|
| `status: "draft"` or `"superseded"` on `facade_grids.json` or `dimensions.json` | **Refuse**, and report that path and status verbatim. `--allow-draft` is an inspection flag, never for a deliverable |
| a `components_registry.json` already in `--in` whose bytes differ from what the builder computes | **Refuse, naming the first differing key path** (contract §8 obligation 1) |
| `assumptions.json` missing `A-023` / `A-024`, or carrying a `value` that differs from `defaults` | **Refuse.** The registry would carry an adopted number with no ledger entry behind it — `G-64`'s whole purpose. Report the mismatch; do not add the entry yourself |
| `schema_version` major you do not implement | **Stop.** Do not guess |
| a panel whose `(kind, width, height)` has no component | **Do not invent a component to fit.** `G-68` FAILs and names the offending ids; that is the rule working. Report it to S4a |

A `draft` upstream file is not your failure to fix, and not a reason to build "just the ready parts".

---

## 3. File ownership

| Artifact | The contract you may rely on |
|---|---|
| `scripts/facade_tables.py` | `--stage components` reads the **existing** `<in>/facade_grids.json` and writes `components_registry.json` only; `--stage tables` reads both JSONs and writes the two CSVs; self-checks `G-57`…`G-70` **on the emitted documents before writing** and refuses on any FAIL; after writing the CSVs asserts `G-70` by reading them back; byte-identical output for byte-identical input. **It emits no MAXScript** |
| `examples/components_registry.json` | The `pavilion-01` worked case, orchestrator-committed from the builder's output. **Not yours to edit** — it is the artefact you verify |
| `agents/max-facade.md` | S4a's contract. Its §7 gate is **shared**: the prototype half is S4b's obligation, the instance-and-measure half is S4a's |
| `07` §8.4 / §9.8 | Cite by id; **do not edit** |

**A `G-` id you cannot evaluate is a SKIP with its reason, never a silent PASS** (`07` §9.6). At P5 that
includes `G-69` when every `variants` array is empty, and `G-70` at lint time (it observes an emitted
CSV).

---

## 4. Procedure

Ordered and deterministic. Each step has a pass condition.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Verify the inputs are locked** | Read the six envelope keys of `facade_grids.json` and `dimensions.json`, and of an existing `components_registry.json` if present. Apply §2.2 in full | Both `locked`, `project` agrees, `units.length == "cm"` |
| 2 | **Read the grid into the class model** | Read §2.1 once, in order. Take `tolerances` **verbatim**. Count `panels[]`, group by the key triple `(kind, width_cm, height_cm)`, and record the group count. **Every `origins` entry is `derived` except the two in `defaults`** (`G-64`) | Group count < panel count, and **the groups are exhaustive and non-overlapping** — every panel lands in exactly one |
| 3 | **Derive each component's `kind` from the panel, never choose it** | Apply §6.3's mapping: `vision` / `punched_window` → `glazed_panel`, or `entrance_door` when the panel's `opening_ref` resolves to a `door` / `entrance` opening · `spandrel` / `blank` → `opaque_panel` · `mullion` / `transom` → `frame_member` | Every component's kind is the **output** of the table, and the `door` / `entrance` question is answered from `dimensions.openings[]`, never guessed from the panel kind |
| 4 | **Declare `defaults`, and only `defaults`** | The two adopted numbers: `panel_thickness_cm` inside `2 … 8` (`D-CL-05`), `joint_width_cm` inside `1 … 4` (`D-FM-10`). Verify `A-023` and `A-024` exist in `assumptions.json`, name these two paths, carry `recheck_stage: "P6"`, and equal the values here | Exactly two keys; both inside range; the ledger is a **bijection** — two assumed values, two entries, no third (§6.1) |
| 5 | **Build `components[]`** | Per group: `id` `CMP-nnn` ascending · `name` unique and hyphen-free · `kind` (step 3) · `size_cm` = `[width_cm, height_cm, panel_thickness_cm]` · the **ordered** `parameters` list of exactly `width_cm`, `height_cm`, `thickness_cm`, `joint_width_cm` in that order, each `{name, source, value, units}` with `source` ∈ `size_cm` \| `defaults` · `serves_panel_kinds` = every panel kind in the group, flags compatible · `variants: []` · `layer: "05_FACADE"` | `size_cm` recomputed by hand for one component matches; the parameter list is in the stated order, not merely a set (§6.4) |
| 6 | **Build `families[]`** | One family per **panel kind** (not per component kind): `FAM-nnn` ascending, `name` hyphen-free, `panel_kinds` = exactly the kinds it serves, `component_ids` = every component serving them, `substitution: "size_matched"`. **Both partitions are exact** — every declared panel kind in exactly one family, every component in exactly one family | No kind in two families, no component in two families, no component in none (`G-65`) |
| 7 | **Emit, then verify by recomputation** | `python scripts/facade_tables.py --in <dir> --out <dir> --stage components` (§5). **You do not hand-write the file.** Read it back from disk and recompute, independently: one `size_cm`, one `parameters` order and one family membership from `facade_grids.json` | Hand computation matches at `tolerances.linear_cm`; the component-id set matches the group set from step 2. **Do not verify the builder by reading its own output back and nodding at it** |
| 8 | **Prove the join is total, then emit the tables** | `--stage tables`. **On a temp copy, delete one component and re-run — the build must refuse** and `G-68` must name the offending panel ids and the count (§6.6). Then on the real directory: `validate_specs.py --dir <dir> --build`, and again with `--warnings-as-errors` | The deletion is refused (a registry that builds after losing a block is worse than one that fails). Both validator runs exit **0** with `FAIL 0` |
| 9 | **Hand the prototype census to the live gate, clean up, report** | §7, §9, §12. **An emitted CSV is not done until it has been placed in Max and counted** | `prototypes == count(distinct component_ref)`, each prototype measured against its `size_cm`, `objects.count == 0` at the end |

**Determinism.** The same locked inputs must yield byte-identical `components_registry.json` and both CSVs
(`07` S-5, `01` §5). Four things break it, all defects to report rather than fix in the output: a
timestamp other than `source.recorded_at`, a run-time default, **iteration-order dependence in the
component or family ids** (grouping through a `set` or a dict whose order leaks into the numbering), and
float formatting that leaves `-0.0`. `parameters` is an **ordered list**, so its order is part of the
contract and never sorted at write time.

---

## 5. The build commands

```
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --stage components
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --stage tables
python scripts/facade_tables.py --in <specs_dir> --out <out_dir> --stage all --json
python scripts/validate_specs.py --dir <specs_dir> --build [--warnings-as-errors]
```

Read the builder's `--help`; never guess a flag. `01` §8 fixes the shape and forbids a second entry point.

| Aspect | Contract |
|---|---|
| Reads | `--stage components`: the **existing** `<in>/facade_grids.json` plus `<in>/dimensions.json` · `--stage tables`: both existing JSONs |
| Writes | `<out>/components_registry.json`, `<out>/facade_table.csv`, `<out>/world_table.csv`. `--out` defaults to `--in`; `--json` gives a machine-readable report |
| Exit **0** | The lock gate passed **and** the `G-57`…`G-70` self-check produced no failure |
| Exit **non-zero** | A refusal naming the reason — the file path and the `status` found, the first differing key path, or the `G-` ids that fired |
| Determinism | Byte-identical output for byte-identical input |
| MAXScript | **None emitted.** §7's gate is the consumer, not a `.ms` |
| Layer code | **None.** Layer is data (`07` §8.1.3); adding layer code is a defect — it cannot work (`CHECKPOINT.md`, P3, 2026-10-04) |
| CSV rows that carry this stage | `component_kind`, `component_ref`, `family_ref`, `width_cm`, `height_cm`, `thickness_cm`, `joint_cm` — `instance_id == panel_ref` on every row, so the census needs no join (`G-70`) |

**A non-zero exit is a stop**: fix the grid through S4a (§10.1) or the builder through its owner (§3).
Never rename a key, widen `tolerances`, add a third `defaults` key, or delete a component to silence a
`FAIL`.

---

## 6. The registry rules

### 6.1 The two assumed numbers, and why there are exactly two

`defaults` carries **`panel_thickness_cm`** (`D-CL-05`, range `2 … 8`) and **`joint_width_cm`**
(`D-FM-10`, range `1 … 4`). They are the **only** invented values in P5, and both are `assumed`, never
`derived`.

| | `panel_thickness_cm` | `joint_width_cm` |
|---|---|---|
| Ledger entry | **`A-023`** | **`A-024`** |
| Convention it adopts | `09` `D-CL-05` — minimum modelled thickness for a facade panel or reveal | `09` `D-FM-10` — facade panel joint width |
| Range | `2 … 8` cm | `1 … 4` cm |
| `recheck_stage` | **`"P6"`** | **`"P6"`** |
| Why P6 | P6 is where a panel is placed and inset by half the joint | P6 is where a panel is inset by half the joint |

**Why only these two.** Every other value in `components_registry.json` recomputes from
`facade_grids.json` and `dimensions.json`, which in turn recompute from `dimensions.json`. The pipeline
resolved every provenance question those values could raise at S1/S2. So **an `assumed` or a `given`
value anywhere else in this file is a defect**, and `G-64` fails it by name. A registry that cannot say
where a number came from is a number nobody chose.

**These are adoptions, not inventions.** Each already exists in `09` as a *reference-only* convention
with a declared band, so the stage picks a value inside a documented range and records the pick.
**You may not add a third.** A third assumed value is an escalation (§10.1), never a quiet addition —
the ledger is meant to stay a **bijection**: two adopted values, two entries, one for one.

Verify, do not write: `assumptions.json` is the orchestrator's. Your obligation is to **check** that
`A-023` and `A-024` exist, name these two `field_path`s, carry `recheck_stage: "P6"`, and equal the values
in `defaults` — and to **refuse** if they do not.

### 6.2 One component per size class, not per panel

`components[]` holds **one entry per distinct `(kind, width_cm, height_cm)` class of panel.** The grid is
expected to carry **≈ 110 … 130 panels** — contract §4.1 works `F-S`/`LVL-00` to 28 and puts the whole
model in that band; those resolve to **a few dozen blocks**. That collapse *is* the
stage: a registry with one entry per panel would be a copy of `facade_grids.json` with worse ids, and it
would double the model in S5. Width and height are the class key because they are the slot P6 must fill;
thickness is uniform by construction, which is what makes one `panel_thickness_cm` sufficient.

### 6.3 A component's `kind` is derived from the panel, never chosen

| panel `kind` | panel hosts a `door` / `entrance` opening | component `kind` |
|---|---|---|
| `vision`, `punched_window` | no | `glazed_panel` |
| `vision`, `punched_window` | **yes** | `entrance_door` |
| `spandrel`, `blank` | — | `opaque_panel` |
| `mullion`, `transom` | — | `frame_member` |

The middle row is the one that gets decided by eye. Resolve it from `dimensions.openings[].type` through
the panel's `opening_ref`: **one `entrance` and one `door` exist in the worked example**, and both become
`entrance_door` components. Everything else is glazed. `G-67` then checks the flags agree:
a `glazed_panel` serves only glazed panel kinds, an `opaque_panel` only kinds that are neither glazed nor
frame, a `frame_member` only frame-member kinds, and an `entrance_door` only glazed kinds that host a
`door` or `entrance` opening.

### 6.4 `parameters` is an ordered list, and the order is the point

Every component carries exactly `width_cm`, `height_cm`, `thickness_cm`, `joint_width_cm`, **in that
order**, each `{name, source, value, units}`, with `source` ∈ `size_cm` for the first two and `defaults`
for the last two. The four resolve to two places and the order is fixed, which is what lets a builder
generate a **stable parameter order without reading the array's contents to decide what is what**
(`01` §3, S4b gate; `G-66`). A map, or a list that got sorted, destroys exactly that.

`size_cm` is `[width_cm, height_cm, panel_thickness_cm]` within `linear_cm` — the third number is the
adopted default, not a per-component choice.

### 6.5 `variants` is empty, and that is not a gap

`variants: []` on every component is a valid, complete registry. `G-69` checks the discipline *when*
variants exist (`^VAR-\d{3}$`, unique within the component, `overrides` non-empty and keyed only by the
four parameter names), and **reports SKIP with its reason when every array is empty** — a rule nothing
exercises should say so rather than pass vacuously. So an all-empty registry produces a named SKIP, and
that SKIP is the honest state. **Inventing a variant to make `G-69` produce a row is a defect.**

### 6.6 The join, and why it is total

P6 walks three steps, and each is a lookup rather than a search:

1. Take the panel's `kind`.
2. Resolve the **family** whose `panel_kinds` contains that kind — exactly one, by §6.7's partition.
3. Within it, take the **component** whose `size_cm` matches the panel's `width_cm` / `height_cm` within
   `tolerances.linear_cm`.

**`G-68` is what makes that total**, and it is why this file exists: every panel must have **at least one**
component satisfying both the size match and the `serves_panel_kinds` membership, and **all** matching
components must belong to **one** family. When it breaks it **names the first ten offending panel ids and
the count** — because "a panel size has no block" is the failure mode that otherwise produces a scene
that is *quietly* wrong: the partition is complete, every check on the partition passes, and one panel
simply is not there. It is cross-file, so it SKIPs with a reason when the registry is absent rather than
pretending the join held.

**The worked example, from the real numbers.** `OP-G-01` is a `window` on `F-S` at `LVL-00`, bay 0,
`position_cm 225.0`, `width_cm 180.0`, `sill_cm 90.0`, `head_cm 270.0`. Bay 0 runs `0 … 450`, so the
opening's u-range is `225 - 90 = 135` to `225 + 90 = 315`. **Bay 0's own v axes** are
`0, 90, 270, 420` — its `level_base`, this opening's sill and head, and its `level_top` — so **exactly
one** cell lies inside the opening: `u 135 … 315`, `v 90 … 270` → `width_cm 180.0`,
`height_cm 180.0`, `kind: "punched_window"`, `opening_ref: "OP-G-01"`. **Exactly one panel per opening**
(`G-62`) — which is why this class key is a whole window and never a fragment of one.

**Why that cell is a single panel** is S4a's per-bay v rule (`07` §8.3.5 steps 4–7, and
`agents/max-facade.md` §6.3): the vertical division is computed **per bay**, so bay 1's entrance
`OP-G-02` with `head_cm = 260` divides **only bay 1**. An earlier facade-wide v grid put a line at
`260` across the whole elevation and split this window into a `180 × 170` panel plus a `180 × 10 cm`
sliver sitting 10 cm below its own head. **Had that happened, this registry would now be carrying a
`("punched_window", 180.0, 10.0)` class that serves one accidental panel** — a class no other panel
joins, `G-67`'s inverse failure. A sliver in the grid is a sliver in the registry.

| Step | Resolution |
|---|---|
| Group key | `("punched_window", 180.0, 180.0)` |
| Component `kind` (§6.3) | the panel hosts a `window`, not a `door` / `entrance` → **`glazed_panel`** |
| `size_cm` | `[180.0, 180.0, <defaults.panel_thickness_cm>]` |
| `parameters` | `width_cm 180.0` (`size_cm`) · `height_cm 180.0` (`size_cm`) · `thickness_cm <A-023>` (`defaults`) · `joint_width_cm <A-024>` (`defaults`) — **in that order** |
| Family | the one whose `panel_kinds` contains `punched_window`; `substitution: "size_matched"` |
| `world_table.csv` row | `rot_z_deg` = `F-S`'s **`run_angle_deg` = 0.0**, never its `direction_deg` of `180.0` (`G-57`, `G-70`) |

Note the last row: `F-S` runs along **+X**, so the row's rotation is `0.0` while the facade's compass
facing reads `180.0`. A registry step that reached for the facing label would place the whole south
elevation rotated a half turn.

### 6.7 Both partitions are exact

Every declared panel kind belongs to **exactly one** family; every component appears in **exactly one**
`families[].component_ids`, and every listed id exists (`G-65`). An unindexed component is invisible to
P6's step 2 — the join fails with no message about the registry. `substitution` is the single value
`size_matched`; a family that declared any other policy would be promising an interchangeability no
stage can honour. **CORRECTED (2026-10-06):** this sentence used to say "an interchangeability S6b cannot
honour"; there is no S6b, and **S6 was cancelled on 2026-10-05**.

**The partitions do not depend on how the grid was divided**, only on which panels exist: a family is a
set of size classes per panel kind, whatever produced them. What S4a's per-bay rule changes is the
**membership** — a shared v grid produced sliver classes that no other panel joined, and a sliver class
is a family of one (AP-3).

### 6.8 The dependency is one-way

`components_registry.json` reads `facade_grids.json` and `dimensions.json`. **A panel never names a
component.** The join runs registry → grid, so there is no cycle, `G-31` stays a single pass, and `G-68`
can ask "does every panel have a block?" as a **total-join** question rather than as a
mutual-consistency puzzle. Adding `component_ref` to a panel would be a cross-file edit you do not own
and a schema change `07` §12 governs.

### 6.9 The file is builder output

`components_registry.json` is **emitted**. A hand edit breaks the audit trail `G-64` protects: a component
whose `size_cm` no longer matches the panels it serves is a hand-edited derived value in a file nobody
recomputes. **Verify the builder by recomputing it from `facade_grids.json`** — not by trusting it, not
by repairing it. And `kind` is geometric: `glazed_panel` is a block, not a material and not any renderer's
glass (`07` §8.3.6, §12).

---

## 7. The 3ds Max step — the live gate's prototype half

**`facade_tables.py` emits no MAXScript, so there is no `fileIn` here. The consumer of the registry is
live Max, and the gate is mandatory.** The gate is S4a's §7 and the orchestrator performs it; **this
stage's half is the prototype census**, because a registry that names blocks nobody ever measured is
exactly the quiet failure `G-68` exists to prevent.

> **An emitted CSV is not done until it has been placed in Max and counted.** That guard is the
> table-shaped equivalent of P3/P4's `fileIn` + `node.min/max`, and it is shared with S4a.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Count the classes, independently** | From Python, over `world_table.csv`: `P = count(distinct component_ref)`, and separately `count(distinct component_ref in components_registry.json)`. Also `N` = data rows, and `N == len(panels)` | The two counts of prototypes are **equal**, and each is far below `N`. A prototype count equal to the panel count means one block per panel (§6.2) |
| 2 | **Build one prototype per distinct `component_ref`** | At a scratch position, sized `width_cm × height_cm × thickness_cm` from the CSV. The **verified placement primitive** is `Box(width:, length:, height:, pos:)` — geometry centred on `pos.xy`, base at `pos.z`; scene units cm, `units.SystemScale 1.0`, so **no conversion happens** (`CHECKPOINT.md` §"Scene units and placement semantics — VERIFIED (P3, 2026-10-04)", control in the same batch). **`Box` is the gate's primitive, not a value any spec file may carry** (§6.9) | `P` prototypes, each named the component `name`, hyphen-free (`11` N1) |
| 3 | **Measure every prototype against its `size_cm`** | `node.min` / `node.max` on each prototype, compared against `size_cm` **computed independently in Python** from the CSV — allowing for the verified `Box` semantics (centred in X/Y, based at `pos.z`) | Every axis within `tolerances.linear_cm`. A larger mismatch is a real inconsistency: **report both figures and stop**, never nudge a node or widen the tolerance |
| 4 | **Then hand off to S4a's rows 3–8** | Instance placement from the first `M = min(N, 120)` rows, the instance-vs-copy discriminator with its deliberate `#copy` control, the 5-node sample, and the `objects.count == 0` assertion | See `agents/max-facade.md` §7. **A registry-only pass is not a gate pass** |
| 5 | **Record every measured number** | `P`, `N`, `M`, `prototypes == P`, the worst deviation over all `P` prototypes, and the outcome of step 4 | Written down. **If it cannot be executed, say so — an unmeasured registry is an unverified registry**, and the gate is `NOT RUN`, not `pass` |

**Two of these were UNVERIFIED when this table was written and are now MEASURED. The third is
genuinely not. A throw is a measurement, not a nuisance:**

| Claim | Status | What you do |
|---|---|---|
| **Rotating a node after creation** — the *mechanism* | **MEASURED** (P5/P6, re-confirmed 2026-10-05; `references/_closeout-evidence.md` §4). **`rotationZ` / `rotationX` / `rotationY` / `angle` do not exist** in this build. The route is the single statement `n.rotation = quat <degrees> [0,0,1]` | Write exactly that statement — on a prototype **and** on a placed instance. `rotationZ` anywhere in your script is a defect, not a style choice (`agents/max-assembly.md` §6.1, AP-4). Reproduce the discriminating measurement while you are there: a **100 × 200 × 20** box at rotation 90 must span **X 200 / Y 100**, read back with `node.min` / `node.max`. A node whose bbox is unchanged by the rotation means the angle never reached it — record that, do not measure unrotated blocks and call the gate passed |
| **Copy/instance mode producing a shared `baseObject`** | **MEASURED** (P5; `references/_closeout-evidence.md` §4). **`setCopyMode` does not exist** — `Type error: Call needs function or class, got: undefined`. The route is two statements: `n = copy src`, then `n.baseObject = src.baseObject`. Proven by a **discriminator**: a plain `copy` shares nothing, and after the assignment it does | Use those two statements, in that order (`agents/max-assembly.md` §6.1, AP-3). **Still run the deliberate plain-`copy` control in the same batch** — a uniform `true` across both is a **broken probe**, not a pass (`AGENTS.md`, §"The one rule that matters most"). And `delete <base>` does **not** delete its instances: collect names, delete by name, and run it **twice** (AP-6) |
| **`run_angle_deg` applied live, as `rot_z_deg` on this stage's panels | **UNVERIFIED, and it stays that way.** The mechanism above is measured; **this stage has never run the CSV's angle onto a placed node.** `max-massing.md` §7 and `max-facade.md` §7 still list it UNVERIFIED too, and no transcript in `CHECKPOINT.md` covers it | Apply it and record the result. **A rotation that throws is a finding for `CHECKPOINT.md` and `ESCALATED`** — not a reason to place unrotated boxes and call the gate passed. This is the first live test of `run_angle_deg` |
| `3dsmax-mcp_clone_objects` in `mode: "instance"` as an alternative route | Not required — scripted copy mode is contract §9's route. Use it only as a second measurement, and record which route produced the nodes | A disagreement between the two routes is a finding |
| `3dsmax-mcp_clone_objects` in `mode: "instance"` as an alternative route | Not required — scripted copy mode is contract §9's route. Use it only as a second measurement, and record which route produced the nodes | A disagreement between the two routes is a finding |

**Never assemble a large node set in one call.** `execute_maxscript` is main-thread; build prototypes in
batches and delete each batch in the call that created it (§9). This gate adds **no modifiers** — keep it
that way: the Chaos Scatter clothing callback crashed Max under a 20-modifier stack (`CHECKPOINT.md`
§"NEW HAZARD", P4b-r).

---

## 8. Verification — the completion gate

Check every row. **The validator covers the mechanical subset only**; rows 3, 4, 6, 8, 12 and 13 are yours.

| # | Gate | Checked by |
|---|---|---|
| 1 | `python scripts/validate_specs.py --dir <specs_dir> --build` exits **0** with **`FAIL 0`**, and the same command with `--warnings-as-errors` also exits **0** with `FAIL 0` | the transcript of both runs. **Both modes, not one** |
| 2 | **`G-65`…`G-70` all PASS, or SKIP with a stated reason.** A SKIP is not a pass (`07` §9.6). **`G-69` reports SKIP when every `variants` array is empty — that is the expected state and it is named, not hidden.** `G-70` always SKIPs at lint time; the builder asserts it after writing | you, reading the `--json` output row by row |
| 3 | **Each of `G-65`…`G-69` was proved to fire by fault injection** on a **temp copy**, and the failure it produced is recorded | you — one injected defect per rule, on a copy, never on `examples/` |
| 4 | **`G-68` proved total by subtraction**: on a temp registry, **delete one component**, re-run, and the build **refuses**, naming the first ten offending panel ids and the count | you. A build that succeeds after losing a block is worse than one that fails — this is the row that matters most |
| 5 | Every `origins` entry is `derived` with a non-empty `derives_from` resolving in `facade_grids.json`, `dimensions.json` **or this file**; every `origin_inputs` path resolves; `tolerances` equals `dimensions.json`'s, **unwidened**. **The only two `assumed` origins are `defaults.panel_thickness_cm` and `defaults.joint_width_cm`, and nothing else is `assumed` or `given`** | **G-64**, **G-31**, `07` §8.4.1 |
| 6 | **The ledger is a bijection for `A-023` / `A-024`**: both entries exist, name `defaults.panel_thickness_cm` / `defaults.joint_width_cm`, carry **`recheck_stage: "P6"`**, and their `value`s equal the file's; both inside `2 … 8` / `1 … 4`; **and there is no third adopted value** | you — and `examples/assumptions.json` is the orchestrator's; you verify, never edit |
| 7 | **Component count equals the `(kind, width, height)` group count** recomputed from `facade_grids.json`, and is **strictly fewer** than `len(panels)` | you — the collapse is the stage (§6.2) |
| 8 | Every component's `parameters` is the ordered list `width_cm`, `height_cm`, `thickness_cm`, `joint_width_cm` with the right `source` and matching `value`; `size_cm == [width_cm, height_cm, panel_thickness_cm]` | **G-66** (§6.4) |
| 9 | `serves_panel_kinds` is non-empty, every entry a declared panel kind, flags compatible with the component `kind`, and **`size_cm[0..1]` equals some panel's `width_cm` / `height_cm`** — no component that matches no panel | **G-67** (§6.3) |
| 10 | Every component appears in **exactly one** `families[].component_ids`; every declared panel kind in **exactly one** family; every `substitution` is `size_matched`; every `name` is unique and hyphen-free; every `layer` is `05_FACADE` | **G-65**, `07` §8.4.4, `11` N1 |
| 11 | **Every panel in `facade_grids.json` resolves**, and the resolution was walked by hand for at least one `vision`, one `punched_window`, one `opaque_panel` and one `frame_member` | **G-68** (§6.6) |
| 12 | **The §7 gate ran, and every number is recorded**: `P`, `N`, `M`, `prototypes == P`, the worst deviation over all `P` prototypes, and `objects.count == 0` at the end | you — the transcript. **"The registry exists" is not this row.** An unmeasured registry is `NOT MEASURED` |
| 13 | **No MAXScript class, modifier, plugin, MCP tool or material class appears anywhere in the emitted file or in `source.reference`** — `kind` is geometric, and no layer code was emitted | you — grep the artefact, read `source.reference` (§6.9, `07` §12) |

---

## 9. Cleanup

Cleanup is part of the build, not a chore after it.

| # | Rule | Evidence |
|---|---|---|
| 1 | **Delete every gate node in the same call that created it.** If a call fails or is aborted, **sweep** — do not assume nothing was created | A failed/aborted probe leaves its objects behind; eight orphans accumulated and had to be swept (`CHECKPOINT.md` §"Scene units and placement semantics", P3, 2026-10-04) |
| 2 | **Delete instances before prototypes.** `delete <base>` does **not** delete its instances — after `delete bx`, the instance survived | `CHECKPOINT.md` §"Reference claim-by-claim pass", P4b-r, 2026-10-04. Deleting prototypes first leaves a full set of orphans that look like a clean scene |
| 3 | **The sweep is explicit** — `3dsmax-mcp_delete_objects` with CSV-derived names, never "delete everything", and **compare `objects.count` before and after** — the count is the evidence | You are not the only tenant of that session; a blanket delete destroys the user's own work (`11` H12) |
| 4 | **Sweep backwards and confirm the count**: `for i = objects.count to 1 by -1 do ( delete objects[i] )`, then assert `objects.count == 0` before finishing | A delete that does not remove the node in the same call has been measured in this repo (`max-nurbs.md` §9 row 7) |
| 5 | Build prototypes in **batches**, one script per call under ~2 s | `execute_maxscript` is main-thread; a long script freezes the UI (`AGENTS.md`) |
| 6 | A **bare modifier is not a node and cannot be deleted** | This gate adds no modifiers — keep it that way (§7) |
| 7 | Cleanup never touches the S2/S3/S4a geometry — it stays. Only gate prototypes, instances and orphans are removed | `11` §6 delivery checklist |

---

## 10. Escalation policy

S4b resolves; it does not design, and it escalates anything it cannot build honestly.

| You may decide alone | Boundary |
|---|---|
| Which `07` §8.4 key a piece of block data belongs at; component, type and family id assignment and ordering | If a value does not fit a key, escalate — never invent one (`07` §12). Ids ascend, zero-padded, fixed order |
| The **grouping** of panels into size classes | Mechanical: group by `(kind, width_cm, height_cm)`. **Never** group by anything else — a class keyed on position or facade defeats the collapse |
| Which component `kind` a group maps to | By §6.3's table, and **only** by that table. If the `door` / `entrance` question cannot be answered from `dimensions.openings[]`, escalate |
| Which family a panel kind belongs to | Arithmetic: one family per declared panel kind. If two kinds genuinely need one family, that is expressible (`panel_kinds` is a list) — but **two families claiming one kind never is** |
| Optional keys — omit rather than guess. `variants` is the only one, and empty is complete | An invented variant is worse than none (§6.5) |

### 10.1 You must stop and ask

| Topic | Why | Goes to |
|---|---|---|
| **A third assumed value** — anything in `defaults`, in `parameters` or anywhere else that is not recomputable from `dimensions.json` | `defaults` holds exactly two, and both are adoptions inside a documented band (§6.1). `G-64` fails an `assumed` or `given` value anywhere else **by name**; the ledger's one-to-one shape is what makes that checkable | **`07`'s owner**, via a `07` §12 step 1 change, plus the orchestrator for the new ledger entry |
| **A panel type that has no component** | `G-68` FAILs and names the ids. **The honest response is to report it to S4a, not to add a component to fit** — a block with no panel is `G-67`'s failure in the other direction, and a block that exists only to silence the join is a lie about the model | **S4a** (`01` §3, S4b escalation row) |
| **A family that would need to be interchangeable when it should be unique**, or a `substitution` other than `size_matched` | `substitution` is the single value; a second policy promises an interchangeability P6 cannot honour | the user, via S4a |
| **A glass thickness, a frame profile depth, a reveal, or any build-up that is not the two adopted numbers** | Each is a licensed professional's decision and `09`'s do-not-default list covers them. The two adopted values exist because they are *rendering* conventions with declared ranges; a structural profile does not | the user (`E1`) |
| **A component kind that would have to name a material or a renderer** — "the glass", "Corona glass", a named shader | §12's standing rule: a spec file may not name a class, tool, modifier or plugin. `glazed_panel` is a block; the `material_role` stays a role the **user** applies by hand (**CORRECTED 2026-10-06:** this cell used to say "P7 resolves roles to materials"; **P7/S6 was cancelled on 2026-10-05**) | **`07`'s owner** |
| **A size class that groups panels whose `serves_panel_kinds` flags disagree** — one block that would have to be glazed and opaque at once | `G-67` FAILs it, and the correct fix is two components, not one with a loosened flag | **S4a**, with both groups named |
| **A `P6`-flagged `A-023` / `A-024` that would change the geometry** — a real joint width or panel depth from the client | You declare the adoption; P6 is the recheck stage. Report, do not re-pick (§6.1) | the user, naming the `A-nnn`; the orchestrator |
| **Any fact not in `CHECKPOINT.md` §"Verified facts"** — including whether rotation after creation works (§7) | §1.2: S4b escalates for an orchestrator probe, it does not open one | the orchestrator |

### 10.2 How to ask

A question list, not a paragraph — one line per question:

```
<dotted key path> — <the competing values with units> — <what each would change in the registry> — <your recommendation, if you have one>
```

Nothing may be recorded as blocked, impossible, non-buildable or non-existent without a transcript showing
the attempt and the exact error, and a **negative needs the same discipline as a positive** — this repo
has shipped fabricated negatives (`CHECKPOINT.md` §"Incident log"). "There is no class that does X" is a
claim about the **environment** and needs a transcript; "§8.3.6 forbids naming one" is a claim about the
**schema** and you can support it by naming the section.

---

## 11. Anti-patterns and incident guards

| Anti-pattern | Instead |
|---|---|
| **AP-1 · One component per panel** — a `CMP-` entry per `PNL-` | One entry per distinct `(kind, width_cm, height_cm)` class (§6.2). The grid is ≈ 110 … 130 panels and a few dozen blocks; a per-panel registry is a copy of `facade_grids.json` with worse ids, and it doubles the model in S5 |
| **AP-2 · Inventing a glass thickness, a frame depth or a reveal** | Exactly two adopted numbers exist, both inside a documented band and both in the ledger (§6.1). Everything else recomputes. A third assumed value is a `G-64` FAIL and an escalation |
| **AP-3 · A component that matches no panel** — and, in a grid built on a shared v grid, a **`("punched_window", 180.0, 10.0)` class serving exactly one accidental sliver panel** | `G-67` requires `size_cm[0..1]` to equal some panel's `width_cm` / `height_cm`. A block with no panel exists for no reason, and it inflates the prototype count the §7 gate measures. A single-member class is the fingerprint of a defect upstream — find the axis, not the block (§6.6) |
| **AP-4 · A component in two families, or a panel kind in two families** | Both partitions are exact (§6.7, `G-65`). An unindexed component is invisible to P6's step 2 — the join fails with nothing pointing at the registry |
| **AP-5 · `parameters` as an unordered map, or a list that got sorted** | The **order** `width_cm`, `height_cm`, `thickness_cm`, `joint_width_cm` is the contract: it is what lets a builder generate a stable parameter order without inspecting contents (`G-66`, §6.4) |
| **AP-6 · Treating `variants` as mandatory, or inventing one to make `G-69` produce a row** | `variants: []` is complete. `G-69` **SKIPs with its reason** when every array is empty, and that is the honest state (§6.5). A fabricated variant is a defect the rule was written to catch |
| **AP-7 · Putting a Corona class, a MAXScript class, a plugin or an MCP tool name in `kind`** | `kind` is geometric: `glazed_panel`, `opaque_panel`, `frame_member`, `entrance_door` (`07` §8.4.2, §12). A block is not a material. `mcg_*` and `curve_model` **do not exist** in this bridge (`AGENTS.md`) — record that, never emulate it as a kind |
| **AP-8 · Deciding the `door` / `entrance` question by eye** instead of resolving `opening_ref` into `dimensions.openings[].type` | §6.3's middle row is the whole mapping subtlety: the same panel kind becomes `glazed_panel` or `entrance_door` depending on what it hosts. One `entrance` and one `door` exist in the worked example |
| **AP-9 · A panel naming its component** — `component_ref` added to `facade_grids.json` | The dependency is **one-way** (§6.8). A reverse reference is a cycle, a `G-31` failure, and an edit to a file you do not own |
| **AP-10 · A `glazed_panel` serving opaque kinds, or an `opaque_panel` serving glazed ones** — flags loosened to make a group fit | `G-67` matches the flags. A block that would have to be two things is two components (§6.3), not one with a relaxed flag |
| **AP-11 · Widening `tolerances`,** or treating a near-miss `size_cm` match as a match to make the join close | `tolerances` is copied **verbatim** from `dimensions.json`; the match is within `linear_cm` or it is a real gap. `G-68`'s FAIL is the finding |
| **AP-12 · Reporting `G-68` as PASS when the registry was absent** | It is cross-file and **SKIPs with a reason** in that case. A SKIP is not a pass (`07` §9.6) — a grid with no registry has an unproven join, and S5 is where that surfaces |
| **AP-13 · Reporting the gate as passed on the registry alone** | §7: place the prototypes and instances, count them, measure, delete. **An emitted CSV is not done until it has been placed in Max and counted** — the table-shaped equivalent of P3/P4's `fileIn` + `node.min/max` |
| **AP-14 · Hand-editing a generated JSON** so the next rebuild silently destroys the edit | Both files are builder output; a divergent rebuild is **refused, naming the first differing key path** (§2.2). Verify by recomputing from `facade_grids.json` (§6.9) |
| **AP-15 · Naming `geometry_qa`, `contact_check` or `scene_qa`,** or concluding the bridge is broken because one call errored | **Those tools do not exist.** And a large set of names in the connected toolset belongs to the **Rhino** server — only `3dsmax-mcp_*` acts on Max (`AGENTS.md`) |
| **AP-16 · Rewriting a reference or a sibling stage's contract on suspicion** | They are **unverified, not disproven**. Verify claim by claim, then correct only what actually fails (`AGENTS.md`, §"The one rule that matters most") |

### 11.1 Context discipline

You are a worker with a small budget; the main thread is the scarce resource (`AGENTS.md`
§"Context budget"). **Read `07` §8.4 and §9.8 once**, and `facade_grids.json` once — you need
`panels[]` and `panel_types[]`, nothing else, and never the whole file four times. **Compute, don't
transcribe.** The verification that matters is a hand resolution of **four** components — one per kind —
plus one deleted-block rebuild. That is cheaper than reading the emitted registry back and nodding at it.

---

## 12. Return contract

Return **exactly** this, **≤ 12 lines** — no file dumps, no JSON blobs, no transcript excerpts:

```
S4b <project id>
FILES: <path> (<n> lines) · <path> (<n> rows + header) · <path> (<n> rows + header)
VALIDATOR: scripts/validate_specs.py --dir <specs_dir> --build -> exit <n>  (PASS <n> · FAIL <n> · WARN <n> · SKIP <n>)
G-65..G-70: <n> PASS / <n> SKIP — <for each SKIP, the reason; G-69 SKIPs when every variants array is empty; G-70 always SKIPs at lint>
BUILDER: scripts/facade_tables.py --stage components -> exit <n> · <n> panels in / <n> (kind,width,height) classes / <n> components (<by kind>) / <n> families · parameters order width,height,thickness,joint = stable
DEFAULTS: panel_thickness_cm = <n> cm (A-023, D-CL-05 range 2..8) · joint_width_cm = <n> cm (A-024, D-FM-10 range 1..4) · both recheck_stage P6 · ledger bijection holds = <yes/no> · third assumed value = none
FAULTS: G-65..G-69 fault-injected on a temp copy — <n>/<n> fired as expected · G-68 by deleting one component: build refused = <yes/no>, named <n> panel ids
LIVE: prototypes placed in 3ds Max by the orchestrator · P = <n> distinct component_ref == prototypes = <yes/no> · worst |measured - expected| over all P = <n> cm (tolerance linear_cm = <n> cm) · instances N = <n>, M = <n>, objects.count == prototypes + M = <yes/no> · rotation applied = <yes / THREW: …> · scene after = <n>
P6-RECHECK: A-023 A-024 — both named, values match defaults; either would change the geometry = <yes/no>
ESCALATED: <n> — <one line each: the topic, the question, whether it is answered>
OBJECTIONS: <one line per defect in a file you do not own, naming file and section, or "none">
INCOMPLETE: <what you could not do, or "none">
```

Rules for the fields:

- **Line and row counts** are the real counts from disk. The validator and builder lines are only valid
  with a transcript: paste the exit code you observed; if you did not run one, write `NOT RUN` and say
  why on `INCOMPLETE`. **`SKIP` is reported separately from `PASS`**, never folded into it.
  **Measurements are numbers, not adjectives** — "matches" is not evidence; `0.0 cm worst deviation` is.
  If you measured nothing, say `NOT MEASURED`.
- **`DEFAULTS` is never silently empty.** Both adopted values, both ledger ids, both ranges and the
  `recheck_stage` are named every time, because the bijection is the check.
- **`G-69`'s SKIP is reported, not folded into PASS** — an all-empty `variants` set is the expected state
  and saying so is the point.
- **`P6-RECHECK`** carries `A-023` / `A-024` because P6, not this stage, is the recheck stage for them.
- **`OBJECTIONS`** is where a `validate_specs.py` or `facade_tables.py` behaviour that contradicts
  `07` §8.4 / §9.8 goes — one line each, naming the file and the section. **`INCOMPLETE`** is where you
  say what you could not finish; a field that hides a gap is worse than an admission.