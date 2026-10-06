# The improvement log — how a modelling session records what it found

**This file is the format specification. `agents/max-orchestrator.md` §6.2 owns the instruction to
write it; this file owns what a correct entry looks like. If the two disagree, this file is right
about the format and the orchestrator is right about the trigger.**

---

## 1. What this log is for, and what it is not for

A modelling session is where the pipeline meets a real building. Real buildings produce defects the
rehearsal could not: a slab that lands on the wrong storey, a bay that needs a spandrel nobody
modelled, a component size that is legal in the registry and wrong on site. **Those findings are
otherwise lost the moment the session ends** — the model is built, the spec is locked, and nobody
writes down the thing that will bite the next time.

So: the log is a **hand-off from one session to the next**.

### It is NOT

| Not this | Why, and where that thing actually lives |
|---|---|
| A dump of everything the agent noticed | A log that records trivia is a log nobody reads. Only findings that change a decision or a number go in |
| A place to record verified facts about Max | `CHECKPOINT.md` §"Verified facts". A fact about Max's behaviour belongs there, with a transcript. **This log does not get to claim verified facts about the bridge** |
| A place to record pack defects | If the finding is *the skill pack is wrong*, it goes in `CHECKPOINT.md` §"Open bugs" and gets fixed. This log **links** to it; it does not restate it |
| An SLA, a report, or a summary of the session | Append-only, one entry per finding, newest at the bottom. No executive summary |
| Required output of a session | **See §3. Most sessions write nothing.** A session with no findings produces no file |

### The line that matters

> **A log entry describes THIS PROJECT. A `CHECKPOINT.md` entry describes THE PACK.**

Concretely: *"bay 7 needs a 300 mm spandrel and the registry only has a 150 mm one — project
`riverside-tower`, suggest a `CMP-nnn` variant"* is a log entry. *"the builder chose
`panel_thickness_cm = 4.0` when `D-CL-05` declares 3"* is a `CHECKPOINT.md` entry, because it is true
of every project.

---

## 2. Location and name

```
<project>/
├── project.json
├── IMPROVEMENTS.md        ← this file. Optional. Created by hand, never scaffolded.
└── specs/
    ├── pipeline/…
    └── recipes/…
```

Exactly this name, capitalised, in the **project root** — next to `project.json`, not inside `specs/`.

**Why it is not in `specs/`:** `specs/pipeline/` is the locked, machine-read, `G-`-linted contract. A
free-text observation file sitting next to the contract invites two failures — an agent "fixing" the
contract to match an observation, or the linter treating a note as a spec. `validate_specs.py`
`discover()` globs `*.json` only, so this file is invisible to the linter **by design**, and that is
the correct behaviour: nothing in the pipeline may depend on a file whose presence is optional.

**Why `init_project.py` does not scaffold it:** a scaffolded empty log is a lie — it asserts that a
finding was recorded. `init_project.py`'s `--dry-run` output lists 12 files and 6 directories; that
count stays correct.

---

## 3. When to write — the trigger, and the three things that are NOT triggers

**Write an entry when, during a modelling session, you find any of these:**

1. **A measured value that is wrong** — a bbox off by more than `tolerances.linear_cm`, a count that
   does not match the spec, an idempotency violation, a node at the wrong height.
2. **Something the pipeline could not express** — a building element with no `kind`, a dimension with
   no key, a facade situation the grid does not decompose into. This is the most valuable category:
   it is a **gap in the grammar**, and gaps are found only on real buildings.
3. **A spec value that is legal but wrong on site** — inside its declared range, passes every `G-`
   rule, and is nonetheless the wrong number for this building. The P5 grid defect was exactly this
   shape: `panel_thickness_cm = 4.0`, range `2…8`, **every check green**, wrong value.

### Do NOT write an entry for

- **A routine run.** The chain built, every gate passed, the numbers matched. Write nothing.
- **Something already in `CHECKPOINT.md`.** Link to the entry instead of restating it.
- **A suspicion you have not measured.** "The blend tension might be wrong" is not a finding. This
  repo has shipped fabricated negatives — four of them cost a stage each — and a log full of
  unmeasured suspicions is the same failure in a new file. **If you did not run it and read a number,
  it does not go in the log.** If it is genuinely worth chasing, put it in §"Open questions" with the
  exact probe that would settle it.
- **A style preference.** "I would name this differently" is not a defect in a pipeline whose naming
  rule is `11` N1 and `G-74`.

**The honest test:** *would a competent architect arriving at this model tomorrow be worse off for not
knowing this?* If no, write nothing.

---

## 4. Entry format

Append newest at the bottom. Ids are `IMP-nnn`, zero-padded, ascending, **never reused** — including
when an entry is rejected or superseded, because "what was tried and why it was dropped" is part of
the hand-off.

```markdown
### IMP-004 · bay 7 spandrel depth does not match the registry

- **Found:** 2026-10-06, S4a, project `riverside-tower`
- **Kind:** gap-in-grammar (category 2 above)
- **Severity:** blocks-S5 — the panel will place, but it will not cover the slab edge
- **Measured:** facade B, bay 07, level 03 — opening `v_range_cm` is `[1050, 2400]`, the
  slab edge sits at `z = 2400`. `components_registry.json` declares `CMP-014 spandrel` at
  `height_cm 150`. The gap is **750 mm** and no registry component covers it.
- **Evidence:** `facade_grids.json` row `FB-07`, `world_table.csv` rows 61–64, read against
  `massing.json` `EL-006` `z_range_cm`. No transcript needed — this is arithmetic on the specs.
- **Proposed:** a `CMP-nnn` variant at `height_cm 75` plus the existing one, or widen the
  `spandrel` height range in `09-defaults.md`. **Owner: S1** — it is a `dimensions.json` value,
  and S2+ may not invent it.
- **Status:** open — not fixed in this session; the geometry was left as built.

```

### Field rules

| Field | Required | Rule |
|---|---|---|
| Heading `### IMP-nnn · <title>` | yes | `IMP` + 3 digits, ascending, never reused. Title is one line, states the finding, not the area |
| **Found** | yes | ISO date, the stage (`S1`…`S5`), the project id. Not "today" |
| **Kind** | yes | which of the three trigger categories. Forces the writer to say *why* this is a finding |
| **Severity** | yes | one of `note` · `fix-before-S5` · `blocks-S5` · `blocks-delivery`. A finding with no severity is a complaint |
| **Measured** | yes | **the numbers**, with units. "Looks wrong" is not a measurement. Cite the file and row/key you read |
| **Evidence** | yes | where the numbers came from. For a spec-arithmetic finding, that is the file path and key. **If a Max transcript produced it, say so and note that it belongs in `CHECKPOINT.md` if the finding is about the pack** |
| **Proposed** | yes | the change **and which stage owns it**. Never "fix this" — name the owner. A finding whose fix would require a builder to invent a value is an S1 finding by definition |
| **Status** | yes | `open` · `applied` · `applied-partial` · `rejected` · `superseded-by IMP-nnn`. **`applied` requires the gate re-run and the number quoted.** Never mark `applied` because the edit was made |

### The `Status` rule is the one that matters

`applied` is a claim that the pipeline now produces a different, verified number. It needs the gate
output in the **Measured** line, updated. Editing a builder and logging `applied` without re-running
the gate is the single easiest way to make this file worse than useless — it would assert a
verification that never happened, which is exactly the failure mode this repo keeps paying for.

### Rejection is a first-class outcome

`rejected` with a reason is as useful as `applied`. "Suggested widening the parapet range; rejected —
`09-defaults.md` declares 90–120 and the building is at 95" tells the next session the question was
already asked. Do not delete entries.

---

## 5. Header

Created with the file. Keep it exactly this shape:

```markdown
# IMPROVEMENTS — <project id>

> Findings from modelling sessions on this project. Newest at the bottom; ids are never reused.
> Format: `references/improvement-log.md`. A session with no findings writes nothing.
> Verified facts about 3ds Max live in the skill's `CHECKPOINT.md`, not here — see §1.

## Open

<!-- IMP entries are appended under this heading while Status: open. -->
```

Move an entry under `## Closed` when its status leaves `open`. Do not delete it.

---

## 6. Worked example

Two entries, the second of which is the failure mode this format exists to prevent.

```markdown
### IMP-001 · plaza slab overlaps the ground pad by 40 mm

- **Found:** 2026-10-06, S2, project `riverside-tower`
- **Kind:** measured-wrong (category 1)
- **Severity:** fix-before-S5
- **Measured:** `massing.ms` node `SP_GROUND_PAD` measures `z 400…-300` against a
  `SP-001` slab at `z -300…0`. Overlap **40 mm** on the full 4200 × 3600 footprint.
  `tolerances.linear_cm` is 5.
- **Evidence:** `node.min` / `node.max` on both nodes in Max, after `fileIn massing.ms`.
- **Proposed:** raise `SP_GROUND_PAD` to `z 440…-300`, or lower its `thickness_cm` in
  `dimensions.json`. **Owner: S1** — `thickness_cm` is a `dimensions.json` key.
- **Status:** open — recorded during the session; the scene was left as built so the
  measurement stays reproducible.

### IMP-002 · material does not propagate to the panel instances

- **Found:** 2026-10-06, S5, project `riverside-tower`
- **Kind:** already-in-CHECKPOINT (see below)
- **Severity:** note
- **Measured:** assigning a material to `PROTO_CMP_014` — **0 of 10** `PLC_` instances
  inherited it. Assigning to each instance — 10 of 10 set. Negative control: the other 28
  prototypes leaked 0.
- **Evidence:** this is already a **pack-level verified fact**, not a project finding.
- **Proposed:** none. Recorded here only because it is the single most common wrong
  assumption at the hand-off, and the next session on this project will hit it.
- **Status:** open — informational. See `CHECKPOINT.md` §"P10-lite", the material table.
```

`IMP-002` is the boundary case. It was found at modelling time, it is about **this project**'s
hand-off, and it is **not** re-measured or re-stated as a new fact — it points at the transcript. If
it had been a new mechanism rather than a known one, it would have gone to `CHECKPOINT.md` first and
this entry would cite that.

---

## 7. What this file must never contain

- **A claim about 3ds Max that has no transcript.** This log is not `CHECKPOINT.md`. If the finding
  *is* about Max's behaviour, the transcript goes to `CHECKPOINT.md` and the log entry cites it.
- **A prediction presented as a measurement.** Write `suspected, not measured — the probe that would
  settle it is X` in §"Open questions", not in an entry.
- **Anything that would change a locked spec.** The log is an observation channel. The specs are
  changed by their owner stage, through its own gate, with the conflict logged in
  `conflicts_resolved.json`. An agent that finds a problem writes an entry; it does not go editing
  `locked` JSON because a note disagreed with it.
- **Secrets, paths outside the project, or user data.** It ships with the project.