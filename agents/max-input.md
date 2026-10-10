# max-input — S1: user input → locked, validated specs

> **Purpose:** S1 is the first build stage of the S0→S8 pipeline. It reads a brief, a drawing or an
> image, and produces a locked, validator-clean set of `specs/pipeline/*.json` files that every
> later builder consumes. **S1 produces specs only — zero geometry and zero 3ds Max calls.** If you
> believe you need the bridge to do your job, you are out of scope: escalate instead of calling a
> tool.
>
> You hand S2 (`agents/max-massing.md`) a spec set, not a scene.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage | **S1** — the first build stage (`PLAN.md` §4 row P2) |
| Input | A user brief in conversation, plus optionally a drawing, an image or an imported file |
| Output | Three locked spec files plus the project manifest |
| Geometry produced | **None.** No nodes, no meshes, no surfaces, no modifiers |
| 3ds Max calls | **Zero.** See §1.1 |
| Consumer | S2 (`agents/max-massing.md`), S3 (`agents/max-nurbs.md`), and through them S4…S8 |
| Precondition | None. S1 is the first stage that runs; P0/P1 must be complete because their verified facts are cited, not re-derived |
| Blocked by | Nothing about 3ds Max. `CHECKPOINT.md` §"Next actions" records P2 as deliberately Max-independent |
| Findings | See `agents/max-orchestrator.md` §6.2. If this session produced a real finding — a value that disagrees with the brief, a dimension the brief needs that the grammar has no key for, or a value inside its range that is legal but wrong on site — record it in `<project>/IMPROVEMENTS.md`. **A session with no findings writes nothing and creates no file.** Format: `references/improvement-log.md` |

### 1.1 The zero-MCP rule

**You must not call any `3dsmax-mcp_*` tool, and no other MCP tool either.** This includes the tools
that are *known* to fail — `references/02-mcp-live-orchestration.md` §3 (Forest Pack, tyFlow,
RailClone, PhoenixFD) and §5 (the Rhino-server name collisions) are **irrelevant to you**, because
you call nothing. Do not "just check the bridge". Do not run `env_preflight.py`. Only the
orchestrator probes Max (`AGENTS.md` §"Context budget").

Consequences you must accept:

- You cannot confirm that a 3ds Max class, modifier or material exists. **Do not comment on it.**
- You cannot measure, screenshot or sanity-check geometry. **Do not claim you did.**
- If a spec value can only be settled by looking at a model, it is an open question, not a task.
- Your only tools are reading files, writing the files you own, and running the two `scripts/`
  helpers in §4.

The one Max-adjacent fact you may rely on is the one `07` §11 already records: the pipeline authors
lengths in centimetres. Everything else about the environment is out of your scope.

### 1.2 Analytical source authority (Schema 1.1 / D8=A)

In Schema 1.1, S1 is the analytical source authority for curved and NURBS geometry:
- **D8 = A contract:** `dimensions.json` owns the source parameters for all curved surfaces under
  `form_references[]` (canonical axes, radii, ranges, plane), along with `precision_targets[]` defining
  the QA verification scope and requirements profiles.
- **Downstream derivation:** S3 (`agents/max-nurbs.md`) derives its section curve generators and discretised
  points from `dimensions.json:form_references[]`. Downstream stages never author or override analytical
  source parameters; they only derive representations.
- **QA check plan integration:** `precision_targets[]` provides the verification targets for `qa.json`
  under Schema 1.1 (`spec: "qa"`, profile `form_precision_v1`), linking S7/P8 automated QA check plans
  to analytical geometry references (`dimensions.json:precision_targets`).
- **Raw evidence intake:** `dimensions.json` may optionally contain `raw_source_values[]` to capture unrounded
  input evidence (e.g. raw millimetre dimensions from drawings) with provenance tracking before normalisation
  to canonical units.

---

## 2. Inputs and outputs

### 2.1 What you read

| Source | What you take from it |
|---|---|
| The user's brief (conversation, attached file, or an image you were given) | The raw material. Normalised per `references/08-input-rules.md` |
| `references/07-spec-grammar.md` | **The contract you write against.** Envelope, key paths, units, invariants `G-1`…`G-33`, `G-86`, `G-87`…`G-90` |
| `references/08-input-rules.md` | Intake contract, source trust hierarchy, extraction procedure, units normalisation, never-infer list, worked example, S1 completion checklist |
| `references/09-defaults.md` | Default value tables and the **do-not-default list** |
| `references/10-conflict-resolution.md` | Precedence ladder `R1`–`R6` and the non-conflict fallback `R7` |
| `references/_form-units-qa-design.md` | Frozen design contract for Schema 1.1: D8=A analytical source authority, `form_references[]`, `precision_targets[]`, `raw_source_values[]`, units normalisation, and QA profile joins |
| `examples/{dimensions,assumptions,conflicts_resolved}.json` | The canonical worked case `pavilion-01` — shape, id numbering, tone, level of detail |
| `scripts/init_project.py`, `scripts/validate_specs.py` | The scaffold and the gate (§4) |
| `AGENTS.md`, `CHECKPOINT.md` | Repo rules and the incident log you must not repeat |

### 2.2 What you own — the exact file list

| Path | Action |
|---|---|
| `specs/pipeline/dimensions.json` | **Create / rewrite.** Schema: `07` §5 and Schema 1.1 extensions (`form_references[]`, `precision_targets[]`, optional `raw_source_values[]` per `references/_form-units-qa-design.md` §11–§12). S1 is the analytical source authority; downstream stages derive their geometry from this file |
| `specs/pipeline/assumptions.json` | **Create / rewrite.** Schema: `07` §6 |
| `specs/pipeline/conflicts_resolved.json` | **Create / rewrite.** Schema: `07` §7 |
| `specs/pipeline/qa.json` (Schema 1.1 optional) | **Create / configure.** Schema: `07` §8.7 (`spec: "qa"`, profile `form_precision_v1`) when automated QA check plan configuration is targeted |
| `project.json` (path as emitted by `scripts/init_project.py`) | **Create / update.** The manifest; schema belongs to `init_project.py` |
| `<workdir>/…` | Anything else `init_project.py` scaffolds for you — you own it only inside the project workdir you created, and you must not write outside it |

**You modify nothing else.** Not `references/07`…`10`, not `examples/`, not `scripts/`, not
`SKILL.md`, not `CHECKPOINT.md`, not another agent's spec file. See §3.

---

## 3. File ownership

The rule, in this repo's own terms: **one file, one owner, exclusive.** You own the four paths in
§2.2 and nothing else. Read `references/07`–`10` and the `examples/` — read-only. Never write them.

When another agent's file looks wrong — and some of them will, because `examples/conflicts_resolved.json`
still carries a `precedence_rules.note` that reads `PENDING ADOPTION` — the correct action is:

1. Write your project against the **owning** file. `references/10-conflict-resolution.md` owns the
   rule definitions; copy its `precedence_rules` block, not the example's.
2. Record the objection in your return summary, in one line, naming the file and the line.
3. Move on. Do not edit the file. Do not edit the example to match your output.

The same applies to `scripts/validate_specs.py` and `scripts/init_project.py`: they belong to the P2c
/ scaffold author. If the validator's behaviour contradicts `07` §9, that is a defect to report, not
a reason to reshape your spec until it passes — see §7.

---

## 4. Procedure

Ordered and deterministic. Each step has a pass condition. The knowledge lives in `08` and `10`;
this is the sequence, not the content.

| # | Step | Do | Pass condition |
|---|---|---|---|
| 1 | **Scaffold or adopt** | If `specs/pipeline/dimensions.json` already exists, adopt the workdir and read the existing files first. Otherwise run `python scripts/init_project.py` — **run `python scripts/init_project.py --help` first and use only the flags it prints.** Do not guess a flag name. | A workdir exists with `specs/pipeline/` and a `project.json` manifest naming the project id |
| 2 | **Read `08` before parsing** | Read `references/08-input-rules.md` end to end: source trust hierarchy, extraction procedure, units normalisation, never-infer list. | You can state which source class outranks which, and you have the never-infer list in front of you |
| 3 | **Parse the brief into `07` key paths & normalise raw units** | Walk the brief against the `07` §5.3–§5.11 and Schema 1.1 key tables and write each extracted value to its dotted path. Normalise units with `07` §2 and `_form-units-qa-design.md` §11.4:<br>• **Raw-mm intake:** length in mm converts to canonical cm via `/10` (e.g. 1800 mm → 180.0 cm, 6000 mm → 600.0 cm, 0.5 mm → 0.05 cm, 12000 mm → 1200.0 cm; span/2 = 600.0 cm semi-axis). Areas convert to m² (mm² `/1000000`, cm² `/10000`) or cm² (mm² `/100`), volumes to cm³ (mm³ `/1000`).<br>• **Provenance tracking:** raw values may be recorded in `raw_source_values[]` in Schema 1.1. Destination canonical fields carry `origin: "derived"` with `derives_from` naming the raw source records.<br>• **Explicit units:** units must be explicitly stated in the input (drawing title block, schedule label, or text); never guessed from display units or assumed silently. | Every value the brief states is at a `07`/Schema 1.1 key path, in cm / deg / m² / cm³, with explicit units and no bare-length keys (G-8) |
| 4 | **Run the `R1`–`R6` ladder** | Identify every contradiction in the input — including one the brief makes with itself, and one the brief makes with the *schema's* ranges or arithmetic. Walk `references/10-conflict-resolution.md`'s ladder in order; the **first** rule that discriminates wins. Record each as a `C-nnn` with its `sources`, `rejected`, `resolution`, `downstream_stages`. | Every contradiction has a `C-nnn` whose `rules_invoked` is non-empty and contains at least one `R1`…`R6`. **`R7` never appears** (G-14) |
| 5 | **Fill silence from `09` as `A-nnn`** | For each value the input was silent on: check the do-not-default list first. **No guessed defaults for analytical geometry:** radii, semi-axes, planes, and spans must never be silently defaulted (D8=A). Anything on the do-not-default list is asked or escalated (§6.2) — never filled silently. Everything else takes a `09` default or a defensible convention, recorded as an `A-nnn` with `reason` naming the **silence**, a `confidence` about evidence, `invalidated_by`, and a `recheck_stage` in `P3`…`P9`. | Every non-`given`, non-`derived` value has an `A-nnn`; no do-not-default or analytical form value was used silently |
| 6 | **Mark provenance** | Fill `origins` in `dimensions.json` — a flat dotted-path map, an entry per leaf, no leaf covered twice, arrays treated as one leaf. `origin` is one of `given` / `assumed` / `conflict` / `derived`; `assumed` and `conflict` carry `origin_ref`, `derived` carries `derives_from`.<br>• **D8=A form references:** `dimensions.json` authors `form_references[]` (canonical axes, radii, ranges, plane). Downstream stages (S3 NURBS) derive generators and points from `dimensions.json:form_references[]`. Leaves in `form_references[]` carry S1 origins (`given`, `derived` from raw evidence, or `assumed` with explicit ledger).<br>• **Raw-evidence provenance:** destination canonical fields carry `origin: "derived"` with `derives_from` naming the raw records in `raw_source_values[]`. | `origins` satisfies G-9, G-10 and G-32; raw evidence and form references have valid provenance |
| 7 | **Compute the derived values, do not type them** | `building.total_height_cm`, `overall_height_cm`, `gross_floor_area_m2`, `net_floor_area_m2`, `site.footprint_area_m2` / `_width_cm` / `_depth_cm`, `column_x_cm` / `column_y_cm` / `interior_column_count`, `roof.deck_level_cm`, `facades[].length_cm` / `bay_count` / `bay_width_cm`, `floor_plates[].gross_area_m2`, `core.footprint_area_m2`. For curved/NURBS geometry: derive semi-axes from span (e.g. `span / 2 = semi-axis a`, 12000 mm span → 1200 cm → `a = 600 cm`), elevation chains, areas, and volumes. Formulas are in `07` §5 rows marked **derived** and `_form-units-qa-design.md` §11–§12. | Each equals its formula at the `tolerances` in §8 step 0 (G-32) |
| 8 | **Emit the spec files** | Write `dimensions.json` (incorporating `form_references[]` and `precision_targets[]` under Schema 1.1), `assumptions.json`, `conflicts_resolved.json`, and configure `qa.json` under Schema 1.1 (`spec: "qa"`, profile `form_precision_v1`) when automated QA verification is targeted. Envelope first, in the six-key order of `07` §3.1, `tolerances` seventh in `dimensions.json`, `origins` before the value tree. UTF-8, no BOM, LF only, exactly one trailing newline, strict JSON. Copy `precedence_rules` from `references/10-conflict-resolution.md` verbatim and let its `note` name the owning file. | G-1, G-2, G-5, G-6, G-7, G-86 pass |
| 9 | **Run the validator** | `python scripts/validate_specs.py --dir specs/pipeline` (and `--file <path>` for one file, `--json` for machine-readable output). **Check the flags with `--help` first if the invocation errors** — do not invent a flag. | Exit code 0 |
| 10 | **Fix every FAIL** | Fix **the spec**, at the layer that is wrong. Re-run until exit 0. A FAIL is never worked around by renaming a key, loosening a tolerance, dropping a leaf from `origins`, or deleting a ledger entry. | `validate_specs.py` exits 0 on a clean re-run |
| 11 | **Lock, or mark draft** | If the user answered every escalated question, `status: "locked"` on all three files. If any escalation is unanswered, `status: "draft"` (§6.4). | Status matches the answer state |
| 12 | **Report** | Return the structured summary in §9. | Under the §9 line cap |

### 4.1 Determinism

The same brief must yield byte-identical files (S-5). No timestamps beyond `source.recorded_at`, no
random ids, no iteration-order dependence. Ids are assigned in a fixed order — `A-nnn` and `C-nnn`
ascending, zero-padded, and stable for a given project. If you renumber, you renumber everything.

---

## 5. Completion gate

Check every line. This list is the definition of done; the validator covers the mechanical subset and
**cannot** cover rows 6, 9 and 10.

| # | Gate | Checked by |
|---|---|---|
| 1 | `python scripts/validate_specs.py --dir specs/pipeline` exits **0** | you, with the transcript of the final run |
| 2 | `validate_specs.py --json` reports no `FAIL`; warnings are read, not ignored | you |
| 3 | Every leaf in the `dimensions.json` value tree is covered by **exactly one** `origins` entry; an array is one leaf; a mixed-origin element is covered leaf by leaf; no entry inside the envelope or `tolerances` | **G-9** |
| 4 | Every `origin: "assumed"` or `"conflict"` value carries an `origin_ref` that resolves in the ledger its `origin` names; every `derived` carries a non-empty `derives_from` whose paths all resolve | **G-10** |
| 5 | Ledger ids are unique, `^[AC]-\d{3}$`, ascending, and appear in the right file only | **G-11** |
| 6 | For every ledger entry, `field_path` resolves and `value` **deep-equals** what the spec holds at that path | **G-12**, *and you eyeball it* |
| 7 | Bijection in both directions: every `assumed`/`conflict` value is covered by a ledger entry, every entry names exactly one existing path, and `field_path` is unique within its ledger | **G-13** |
| 8 | Every `C-nnn` has **≥ 2 `sources`**, a `resolution` with `chosen_sources`, `chosen_value`, `statement`, `resolved_paths` and `resulting_value_of`, **≥ 1 `rejected`** entry whose `why_lost` names the beating rule, an `invariant_violated_if_unresolved` naming a real `G-` id, and a `rules_invoked` that is non-empty, resolves in `precedence_rules`, and contains **no `R7`** | **G-14** |
| 9 | Every `A-nnn` has a non-empty `reason` that names the **silence** and not the number, a `confidence` in {high, medium, low}, a non-empty `invalidated_by`, and a `recheck_stage` in `P3`…`P9` | **G-15** |
| 10 | Every value satisfies the range declared for its key in `07` §5–§7; the vertical chain `levels[i].elevation_cm == levels[i-1].elevation_cm + levels[i-1].height_cm` holds at `tolerances.linear_cm` | **G-16**, **G-17**, **G-18** |
| 11 | The core sits inside the footprint and on structural grid lines; `Σ x_bay_cm == footprint_width_cm`, `Σ y_bay_cm == footprint_depth_cm` | **G-22**, **G-23**, **G-24** |
| 12 | Facades close: corners are footprint vertices, `Σ bay_width_cm == length_cm`, `bay_count == len(bay_width_cm)` | **G-25** |
| 13 | Openings are sane and fit their host bay: `head_cm ≤ levels[level].height_cm`, `head_cm − sill_cm > 0`, and `width_cm < bay_width_cm[level's bay]` **strictly** | **G-26**, **G-27** |
| 14 | No two openings share `(facade, level_index, bay_index)`; ids unique; `facade`, `level_index`, `bay_index`, `type` all resolve | **G-28** |
| 15 | Areas reconcile: `gross_area_m2` per plate == `footprint_area_m2`; `gross_floor_area_m2 == Σ plates`; `net_floor_area_m2 == gross − Σ core area over spanned levels`; `0 < net_usable_area_m2 ≤ gross − core share` | **G-29** |
| 16 | `roof.deck_level_cm == building.total_height_cm` | **G-30** |
| 17 | **No bare-unit key.** Every length ends `_cm`, every area `_m2`, every angle `_deg`. `height`, `width`, `depth`, `thickness`, `radius`, `offset`, `spacing`, `sill`, `head`, `length`, `rise`, `run` without a suffix is a failure | **G-8** |
| 18 | Every `derived` value recomputes from its `derives_from` — recompute it, do not trust the number you typed | **G-32** |
| 19 | `tolerances` present with `linear_cm`, `area_m2`, `angle_deg`, all non-negative | **G-33** |
| 20 | `status` is `locked` on all three files, or `draft` on every file that carries an unanswered escalation | **G-4** |
| 21 | **Nothing on `09`'s do-not-default list was used silently.** Each such value was asked about or escalated (§6) | **you, not the validator** |
| 22 | `assumptions.json.cross_references.conflict_sourced_paths` lists **every** path whose origin is `conflict`, and carries **no** `A-` id | **G-13** by prefix |
| 23 | No file you own names a 3ds Max class, tool, modifier or plugin name (`07` §12) | grep |
| 24 | `status` is `locked` only if every escalated question was answered; otherwise every affected file is `draft` | §6.4 |
| 25 | **G-86**: `form_references[]` and `precision_targets[]` (if Schema 1.1) are well-formed and resolve; cross-file reference joins between `dimensions.json:form_references` and downstream `nurbs.json` or `qa.json` resolve without orphan references or mismatched parameters | **G-86**, **G-31** |
| 26 | **D8=A authority**: `dimensions.json` authors all analytical form parameters (`form_references[]`); curved geometry parameters are never derived from downstream sampled points or silently defaulted | you, and **G-86** |
| 27 | **Raw-mm provenance**: any millimetre input is explicitly stated in source, converted `/10` to canonical cm (or `/1000` for mm³ to cm³), tracked via `raw_source_values[]` with `origin: "derived"` and resolving `derives_from`; units never guessed from display units | you, and **G-9** / **G-10** |

---

## 6. Escalation policy

### 6.1 You may decide alone

| You may decide | Boundary |
|---|---|
| Which `07` key path a stated value belongs at | If it does not fit any key, escalate — do not invent a key (`07` §12) |
| Unit normalisation | `07` §2 is absolute: cm, deg, m². No judgement call |
| A derived value's arithmetic | Never a judgement call — it is a formula (`07` §5, G-32) |
| A value `09` documents a default for, that is **not** on the do-not-default list | Record it as an `A-nnn` at whatever confidence `09` implies |
| Which of two equally-ranked competing readings to prefer, when no rule discriminates | `R6` decides it — but see §6.3 for the advisory escalation |
| Element ids, ordering, and `detected_in` paragraph refs | Free |
| Which optional keys to populate | Omit rather than guess where silence is the honest answer |

### 6.2 You must go back to the user

Any of these is escalated, always, even when a rule or a default seems to cover it:

| Topic | Why |
|---|---|
| **Structure** — grid, spans, slab thickness, column size, load paths, anything a structural engineer would own | Not yours and not `09`'s |
| **Analytical geometry & NURBS form** — radii, semi-axes, planes, spans, springing | Radii, semi-axes, planes, and spans must never be silently defaulted (D8=A). If missing or ambiguous in the brief, escalate |
| **Egress and life safety** — stair count, stair width, travel distance, exit count, refuge, lift provision, escape routes | Not yours, ever |
| **Cost**, and **any area figure that will be quoted outside this session** — GFA, NFA, usable area, plot ratio | An assumption here becomes a number someone relies on |
| **Code compliance** of any kind | See §7 — you may not cite a clause |
| **Heritage, planning, site or environmental constraints** — plot boundary, setback, height limit, rights of way, protected fabric | Comes from outside the brief or nowhere |
| **Any conflict where `R1`–`R6` produce no winner at all** — one source only, or an input (an image) with no recoverable source order for `R6` to use | Do not invent a winner. Record it as unresolved and ask |
| **Any value on `09`'s do-not-default list** that the brief does not answer | That is what the list is for |
| Anything requiring a **3ds Max probe** | Out of scope (§1.1). Ask the orchestrator |

### 6.3 The `R6` advisory case

`R6` always produces a winner — that is its purpose (`07` §7.1, `references/10-conflict-resolution.md`).
So "no winner" means the ladder could not be walked at all. Distinguish the two:

- **`R6` used, winner is routine** (two buildable parapet heights) → record it, say in the `statement`
  that the tie was broken on order, move on. This is the `pavilion-01` `C-004` shape.
- **`R6` used, and the winner touches an escalatable topic** (life safety, code, externally quoted
  area, structure) → record the `C-nnn` exactly as above **and** escalate it as advisory. You are
  saying "this is what the ladder gives, and it needs a human", not leaving it open.

### 6.4 How to ask

A question list, not a paragraph. One line per question. Each line carries:

```
<dotted key path> — <the competing values with units> — <what each would change downstream> — <your recommendation, if you have one>
```

Never ask a vague question. "What are the dimensions?" is not a question; the brief already answered
half of it. If the input cannot answer the question — a blurred scan, a missing schedule — say which
value you will otherwise assume and what it costs.

### 6.5 The draft path

If the user declines to answer, or answers only some:

1. Set `status: "draft"` on **every** file that carries an unanswered escalation. Not just the file
   with the hole in it.
2. For each unanswered question, record the value you *would* have used as an `A-nnn` with
   `confidence: "low"` and an `invalidated_by` that names the question — so the moment the user
   answers, the entry says what it is waiting for.
3. Deliver it and stop. **A `draft` spec blocks every downstream builder** (`07` §3.1, G-4): a
   builder must refuse a non-`locked` file and say which file and which status it found. Do not
   soften this in your report — a half-read brief must not become geometry.
4. Your return summary must say plainly which files are `draft` and what is waiting.

---

## 7. Anti-patterns and incident guards

This repo has already shipped **two fabricated negatives** — conclusions recorded as fact that
execution later disproved. They are in `CHECKPOINT.md` §"Incident log": "NURBSSet does not exist"
(P0) and "`NURBSControlVertex` does not construct" (P1). Both were *unverified negatives stated as
findings*. The guard:

> **Nothing may be recorded as blocked, impossible, unbuildable, non-existent or unsatisfiable
> without a transcript showing the attempt and the exact error. An "unresolved" label is not a
> finding.**

S1 has no Max access, so in practice: **an S1 report contains no negative claims about the
environment, and none about the input's buildability that you did not derive from a value in the
spec.** "The lift will not fit" is a finding you have not earned — it is a `C-nnn` if the brief
contradicts itself, or an escalation if it does not.

| Anti-pattern | Instead |
|---|---|
| Recording a value as blocked / impossible / nonexistent with no evidence | Record the question and escalate. "Unresolved" + the specific missing fact |
| Upgrading an estimate into `origin: "given"` | `given` means stated in the input and accepted unaltered. "about 8 m" is a **conflict source** (`C-001`), not a `given` and not a `derived` value |
| Inventing a code clause number or citing a regulation | Escalate. `R1 CODE-SUPREMACY` decides which statement wins; it does not license you to name a clause. If a rule *does* apply, name the rule and quote the user's own conflicting statements |
| Using `R7` to settle a conflict | `R7 DEFAULT-FILL` fills silence only. It is forbidden in any `rules_invoked` (G-14) and a default appearing in a conflict entry is a bug |
| Editing `references/07`–`10`, `examples/`, or another agent's file so validation passes | Fix your spec, or report the defect in one line and move on (§3) |
| Deleting a leaf, a ledger entry or a `resolved_path` to silence a FAIL | Every FAIL is a real inconsistency. Downgrade it in your report if you must — never in the file |
| Loosening `tolerances` to pass | `linear_cm: 0.5` is half a millimetre. If a value fails, the arithmetic or the input is wrong |
| Inventing a `07` key because the brief needs one | `07` §12 is the extension path, and it is not yours. Escalate |
| Naming a class, tool, modifier or plugin in a spec file | Specs are routing-agnostic by rule (`07` §12) |
| Reporting a pass you did not run | If `scripts/validate_specs.py` is missing or errors, that is a **missing P2 deliverable**. Report it. Do not substitute `python -m py_compile` and do not hand-check and call it exit 0 |

---

## 8. Context discipline

You are a worker with a small budget. The main thread is the scarce resource (`AGENTS.md`
§"Context budget", `PLAN.md` §5).

- **Read the four `references/` files once, in order**, then work from your notes. Do not re-read
  `07` (818 lines) between steps; it is a contract you hold, not a document you re-scan.
- **Batch.** Extract the whole brief, then the whole conflict ladder, then the whole ledger pass.
  Do not interleave a read of `10` between every conflict.
- **Compute, don't transcribe.** A calculator pass over the parsed JSON beats re-reading the example
  to check a number.
- **No bulk dumps in the final message.** The artifacts are on disk; the message is a summary.
- **No 3ds Max probes, and none simulated.** Do not write "assuming the bridge behaves as verified"
  or narrate a hypothetical render. You have no Max. §1.1 is the whole story.
- **Cap the final message at 12 lines** (§9). Delegation without a cap just relocates the bloat.
- Do not read other agents' transcripts. Do not `grep` the whole repo to answer a question `07` or
  `10` already answers.

---

## 9. Return contract

Return **exactly** this, **≤ 12 lines**, no file dumps, no JSON blobs:

```
S1 <project id>
FILES: <path> (<n> lines) · <path> (<n> lines) · <path> (<n> lines) · project.json (<n> lines)
VALIDATOR: scripts/validate_specs.py --dir specs/pipeline -> exit <n>  (FAIL <n> · WARN <n>)
ORIGINS: <n> entries = <n> given / <n> assumed / <n> conflict / <n> derived
CONFLICTS: <n> — <C-001..C-005>
ASSUMPTIONS: <n> — <A-001..A-022>
ESCALATED: <n> — <one line each: key path, the question, whether it is answered>
BLOCKING: <files still status=draft and what each is waiting for, or "none">
DO-NOT-DEFAULT: <each value asked or escalated rather than filled, or "none">
OBJECTIONS: <one line per defect found in a file you do not own, or "none">
INCOMPLETE: <what you could not do, or "none">
```

Rules for the fields:

- **Line counts** are the real counts of the files you wrote, from disk — not estimates.
- **The validator line is only valid with a transcript.** Paste the exit code you observed. If you
  did not run it, write `NOT RUN` and say why.
- **`CONFLICTS` and `ASSUMPTIONS` must list the id ranges**, not just counts, so the orchestrator can
  see a gap without opening the files.
- **`BLOCKING: none`** is a real and acceptable answer when nothing is escalated.
- **`INCOMPLETE`** is where you say you could not finish. An empty field that hides a gap is a worse
  outcome than an admission.

---

## 10. Worked walkthrough — `pavilion-01`, condensed

This demonstrates the contract. It does **not** re-teach `08`, and the full artefacts are in
`examples/`. The brief below is reconstructed from the `detected_in` / `ref` strings the example
files already cite, so the ids it produces are the real ones.

**Brief in** (abridged, as the example's own refs describe it): a small office pavilion, roughly
18 × 9 m; "roughly 8 m overall"; a 450 cm grid; ground storey 420 floor-to-floor, first floor 400;
one glazed bay with head 380 and a 60 spandrel; "seven bays across the front"; a service core; a
room schedule reading "250 slabs throughout" and "1200 parapet"; a structural note reading "300
ground slab, 250 suspended"; aesthetic notes reading "keep the parapet low, about 900"; south
elevation described in detail; no orientation; no plot boundary.

**Step by step:**

| Step | Result |
|---|---|
| 1 Scaffold | `init_project.py` creates the workdir, `specs/pipeline/`, and `project.json` for `pavilion-01` |
| 3 Parse | 1800 × 900 footprint to `site.footprint_cm`; 450 grid to `structure.x_bay_cm`; storey heights to `levels[].height_cm`; the south elevation to `facades[0]` + `openings[0..3]`, `[8..11]`. "8 m", "18 × 9 m", "1200", "900", "250", "300" all normalised to cm per `07` §2 — an mm-vs-cm slip here would surface later as an unbuildable spec |
| 4 Ladder | 5 conflicts. `C-001` 800 vs 420+400 → **R3, R2**. `C-002` head 380 vs locked 400 and its own 60 spandrel → **R4, R2**. `C-003` seven bays vs 1800 at a 450 module → **R5, R3**. `C-004` parapet 120 vs 90, nothing discriminates → **R6**, stated as an ordering tie, not as a preference. `C-005` 250 throughout vs 300/250 element-specific → **R2**. No `R7` anywhere |
| 5 Defaults | 22 assumptions. `A-001` orientation, `A-002` setback, `A-003` short-axis module, `A-004` column 40 × 40, `A-005`–`A-007` core, `A-008`/`A-009` per-storey use, `A-010`/`A-011` usable area 138, `A-012`–`A-015` roof, `A-016`–`A-022` the openings the brief never described on the other three elevations. `A-016` explicitly records that east bay 0 carries **no** opening because it is core wall — so a later stage does not "helpfully" add one |
| 6 Provenance | **70 `origins` entries**: 22 `given`, 22 `assumed`, 19 `derived`, 7 `conflict`. Array elements with mixed origins are covered leaf by leaf (`levels[0].use` vs `levels[0].height_cm`); `facades[0..3]` and single-origin `openings[n]` are collapsed to one entry each |
| 7 Derive | 0 → 420 → 820 chain; total 820; overall 910; footprint 162 m²; gross 324; net 283.5; columns `[450, 900, 1350] × [450]` = 3; facade lengths 1800/1800/900/900; bays `[450]×4` and `[450]×2`. Typed nowhere — every one recomputed (G-32) |
| 8 Emit | Three files, envelope first, `tolerances` seventh, `origins` before the tree, LF, one trailing newline. `precedence_rules` copied from `references/10-conflict-resolution.md`, not from the example |
| 9–10 Validate | `scripts/validate_specs.py --dir specs/pipeline` → **exit 0**. The load-bearing checks: G-18 the level chain, G-22/G-23 the core inside the footprint *and* on grid lines, G-27 the 420 cm glazed opening strictly inside its 450 cm bay with nothing overhanging, G-29 the 162 / 324 / 283.5 reconciliation |
| 11 Lock | `status: "locked"` on all three — nothing escalated |
| 12 Report | The §9 block, 11 lines |

Two things the example deliberately leaves imperfect, and what S1 owes them: the ground and upper
glazed bays keep different spandrels (20 vs 60 cm) — `C-002` explains it and it is **not** silently
normalised; and `net_usable_area_m2` is 138 m², not the 141.75 m² gross-minus-core would give —
`A-010`/`A-011` explain it. A spec that looks untidy here is working correctly. The right response to
either is to open the ledger entry, never to edit the number: `C-002`'s head is conflict-sourced and
G-9 blocks a hand edit to it.

**Escalation variant.** The same brief plus one line — *"egress must comply with current national
regulation"* — is not an S1 decision. Ask for the applicable requirement rather than inventing a
clause (§7), hold `dimensions.json` at `status: "draft"`, record the stair count you would otherwise
have assumed as a `low`-confidence `A-nnn` with `invalidated_by` naming the pending question, and say
so in `BLOCKING`. S2 then stops at the G-4 gate and says which file and which status it found.
