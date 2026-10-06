# 10 — Conflict Resolution: the precedence ladder and the conflict log

> **Purpose:** the single authoritative definition of the precedence rules `R1`–`R7`, the order they are
> applied in, the shape of a `conflicts_resolved.json` entry, and the discipline that decides what
> counts as a conflict at all. `references/08-input-rules.md` runs this ladder during extraction;
> `scripts/validate_specs.py` (P2c) checks the records it produces. Nobody invents a rule at the desk.
>
> **No 3ds Max.** Nothing in this file was read off a live probe and nothing here needs one. The only
> 3ds Max claim made anywhere is the units convention in `09-defaults.md` §9, which is flagged
> **UNVERIFIED / no live probe** there, as `07-spec-grammar.md` §11 requires.

---

## 1. Adoption status

`07-spec-grammar.md` §7.1 and `examples/conflicts_resolved.json` §`precedence_rules.note` both record
the rule ids and names as *proposed*, pending adoption by this file.

**This file adopts `R1`–`R7` verbatim, with the ids and names below unchanged.** Consequence: the
`rules_invoked` arrays in `examples/conflicts_resolved.json` (C-001 … C-005) are correct as written
and **the examples do not need regenerating**. The only artefact now stale is the `note` string
inside `examples/conflicts_resolved.json`, which still says `PENDING ADOPTION`; that string is
informational and is not validated by any invariant. Correcting it is a cosmetic edit to the example,
not a schema change.

**Renaming** a rule is safe — `rules_invoked` holds bare ids, never names, so a name may move without
touching a single conflict entry. **Re-numbering, adding or removing** a rule is a schema change:
see §8.

---

## 2. The ladder

Applied **in order, lowest id first. The first rule that discriminates between the competing sources
wins.**

| Id | Name | Statement (canonical — copy verbatim) |
|---|---|---|
| `R1` | `CODE-SUPREMACY` | A statutory, regulatory or code requirement outranks every user statement, including an explicit one. |
| `R2` | `SPECIFICITY` | Among competing user statements of the same class, the one that is more specific wins: a value tied to a named level, element or condition beats a bare global value. |
| `R3` | `QUANTITY-OVER-SUMMARY` | A stated total loses to the stated parts that produce it. Parts are measurements; totals are usually summaries. |
| `R4` | `BUILDABILITY` | A value that cannot be built — negative dimension, head above floor-to-floor, negative clearance, element outside its host — loses to any value that can be built. |
| `R5` | `MODULE-ALIGNMENT` | A value that preserves the stated dimensional module or grid outranks one that breaks it. |
| `R6` | `LATER-STATEMENT` | Same class, same specificity, and no rule above discriminates: the statement appearing later in the source wins. |
| `R7` | `DEFAULT-FILL` | **Not a conflict rule.** A documented default from `references/09-defaults.md` may fill a silence but may never decide a conflict. A default that appears in a `conflicts` entry is a bug. |

`R7` is **outside the ladder.** It is a silence-filler, not a tie-breaker. `G-14` forbids `R7` — or
any default-fill rule — in any `rules_invoked` array, and the validator enforces it.

### 2.1 Why this order is load-bearing

| Position | Consequence of the ordering |
|---|---|
| `R3` before `R4` | A stated total loses to its own parts **before** anyone asks whether those parts are buildable. It is the cheaper question and the one actually posed by the input: the brief already told you both numbers. C-001 is decided on `R3` and never needs a structural opinion. |
| `R4` before `R5` | Impossibility is checked before preference. A value that cannot exist cannot be rescued by being on-module. |
| `R5` before `R6` | Module preservation is a design judgement the user almost certainly intended; "whichever sentence came last" is not. `R6` only ever breaks a genuine tie. |
| `R6` last, always | There is always a decision. A deterministic pipeline may not leave a contradiction open, so the last resort is documented position, never an agent's taste. |

### 2.2 The ladder walk, in one place

```
competing sources S = {s1, s2, ...}
for rule in [R1, R2, R3, R4, R5, R6]:        # ascending, and R7 is never in this list
    W = [ s in S if rule discriminates(s, S) ]
    if W is non-empty and W is a strict subset of S:
        chosen   = W
        rejected = S \ W
        record rule in rules_invoked        # see §5.3 — every rule that discriminated is recorded
        break
```

Two consequences worth stating because they are easy to get wrong:

- **A rule that returns all of `S` has not discriminated.** "R1 does not apply because neither source
  is a code requirement" is not a discrimination, and must not appear in `rules_invoked`.
- **A rule that returns an empty set is not a discriminator either.** It means the rule cannot be
  evaluated (usually because the input lacks the class of evidence the rule needs). Walk on.

### 2.3 `rules_invoked` records the whole walk, not just the winner

Ascending ids of **every rule that discriminated**, which is why `examples/conflicts_resolved.json`
carries two ids on some entries:

| Entry | `rules_invoked` | Reading |
|---|---|---|
| C-001 | `["R3", "R2"]` | `R3` picks the two storey heights over the 800 total. `R2` then confirms those beat a bare global figure *for the same paths*, because each is tied to a named storey. Both discriminated; both recorded, ascending. |
| C-002 | `["R4", "R2"]` | `R4` vetoes head 380 outright (it cannot exist against a locked 400 floor-to-floor). `R2` then decides *which* of the two buildable statements in the same paragraph supplies the surviving value — the element-specific spandrel over the bare head figure. |
| C-003 | `["R5", "R3"]` | `R5` affirms the stated 450 module over the stated count of 7. `R3` independently rejects 7 as a summary quantity that disagrees with its own geometry (1800 does not divide by 7). |
| C-004 | `["R6"]` | Nothing above discriminates. Position in the brief breaks the tie. |
| C-005 | `["R2"]` | Element-specific beats global. Note that `R4` and `R5` are irrelevant here — both candidate thicknesses are buildable and neither touches the grid. |

**`R1` appears in none of C-001 … C-005, and that is correct.** None of those five contradictions
involves a statutory or regulatory requirement. An `R1`-free log is the normal result for a brief
with no code content; it is not an omission. See §3.1 for why inventing an `R1` is the single easiest
way to corrupt this file.

---

## 3. The rules in detail

Each rule below states what it resolves, which evidence class it privileges, how it fails, and its
worked case from `examples/conflicts_resolved.json`.

### 3.1 `R1` CODE-SUPREMACY

| | |
|---|---|
| **Resolves** | A user statement that directly contradicts a stated statutory, regulatory or code requirement. Also resolves a user statement that cannot be honoured because a code requirement forbids the thing asked for (a door swing into an escape route, a glazing area that breaches a control requirement). |
| **Privileges** | The requirement text itself. In this pipeline that means a requirement **the input states** — quoted by the user, cited in the brief, or transcribed from a drawing's code note. |
| **Never resolves by** | The agent's memory of a code. This is a hard constraint, not a style preference. |
| **Failure mode** | An agent remembers "egress widths must be 1.2 m" (or any other figure) and invokes `R1` to overrule an explicit user dimension. That is a fabricated citation wearing a rule id, and it is invisible in the log because `R1` *is* in the ladder. |
| **Mitigation** | `R1` may only be invoked when a `sources[]` entry carries the requirement as `ref` (e.g. `brief:code_note`, `drawing:general_notes`) with the requirement in `statement`. The `rejected[].why_lost` must name the requirement, not the rule. If no such `sources[]` entry exists, `R1` did not discriminate — walk to `R2`. |
| **Worked case** | **None in `pavilion-01`.** The brief contains no code content, so no `sources[]` entry can carry a requirement and `R1` cannot fire. This is the correct and expected outcome. If a later brief adds a code note, `R1` fires there. |

`09-defaults.md` marks certain rows **code-driven**. Those rows are *not* `R1` evidence: a default row
is this repo's convention, not a jurisdiction's law. Citing one under `R1` is the exact error above.

### 3.2 `R2` SPECIFICITY

| | |
|---|---|
| **Resolves** | Two statements of the **same class** where one is scoped and the other is not. Scoped means it names a level, an element, an orientation, a condition or a range. |
| **Privileges** | The narrowly-scoped statement. Scope is the discriminator; confidence, politeness, detail and length are not. |
| **Failure mode** | Over-application in both directions. (a) Treating one element's note as governing a whole system — "300 ground slab" read as "300 everywhere". (b) Treating a *derived* statement as more specific than the measurement it was derived from, i.e. laundering a summary through specificity. |
| **Mitigation** | The ladder already orders `R3` above `R2`, so (b) is caught when the summary is a *total*. When it is not a total, the test is explicit: `R2` requires the winner to name a scope the loser does not. If neither names a scope, `R2` did not discriminate. |
| **Worked case** | **C-005** — room schedule `250 slabs throughout` (bare global) against structural note `300 ground slab, 250 suspended` (two named elements). The note wins for `floor_plates[0]`, and its suspended-slab figure agrees with the schedule anyway, so the entry resolves to 30 / 25 and `resolved_paths` names both plates. C-005's own `resolution.statement` makes the honest observation that these two were never truly contradictory — the log exists to record that, not to hide it. |

### 3.3 `R3` QUANTITY-OVER-SUMMARY

| | |
|---|---|
| **Resolves** | A stated **total** that disagrees with the stated **parts** that produce it. Total: a height, an area, a count, a sum. Part: a per-storey, per-bay or per-element figure. |
| **Privileges** | Measurement over summary. Parts are things someone counted; totals are usually things someone rounded. |
| **Failure mode** | Two variants. (a) **Circularity**: the "parts" were themselves computed from the total, so neither is independent and the rule has no evidence to weigh — fall through to `R6`. (b) **False total**: a rounded or hedged statement ("roughly 8 m") treated as a precise measurement, which inverts the rule and makes the summary win. |
| **Mitigation** | Read the *epithet*. "roughly", "about", "approximately", "say", "order of" marks a summary and loses under `R3`; an exact figure with no qualifier is a measurement and can win. Variant (a) is real and common — if every "part" traces back to the total in the same sentence, `R3` did not discriminate. |
| **Worked case** | **C-001** — `roughly 8 m overall` (800) against the two stated storey heights (420 + 400). The parts win; `building.total_height_cm` becomes 820 and `origin: derived` with `derives_from` the two heights, so `G-32` makes a hand edit to the total impossible. **C-003** uses `R3` a second time, against a stated *count* of 7 bays. |

### 3.4 `R4` BUILDABILITY

| | |
|---|---|
| **Resolves** | A value that cannot exist in the geometry: negative dimension, opening head above its level's floor-to-floor, opening wider than its host bay, a core vertex outside the footprint, a clearance that comes out negative, a bay sum that does not reach the facade length. |
| **Privileges** | Feasibility over intention. A value that cannot be built loses to any value that can be built — including a value the user never stated, **provided that value is itself derived from a stated one.** |
| **Failure mode** | Three ways to abuse a veto. (a) Using it as a preference: "340 reads better than 380" is not buildability. (b) Using it to reject a value that is merely *unusual*. (c) Using it to invent a replacement — `R4` can only reject; whatever survives must be traceable to a `sources[]` entry or to a `derived` computation from one. |
| **Mitigation** | Every `R4` rejection must be expressible as an invariant id. `C-002` cites `G-26`; `C-003` cites `G-25`. If you cannot name the `G-` id that fails, you have not applied buildability — you have applied taste. |
| **Worked case** | **C-002** — a curtain-wall head at 380 plus the same paragraph's 60 cm spandrel is 440 against a floor-to-floor locked at 400 by C-001: the head would run 40 cm past the roof deck. `R4` rejects 380; `R2` selects the spandrel as the surviving figure; the head is rebuilt as 400 − 60 = 340, which is why `openings[11].head_cm` is `conflict` and not `derived`. |

### 3.5 `R5` MODULE-ALIGNMENT

| | |
|---|---|
| **Resolves** | A stated dimension that breaks a **stated** repeated module — bay grid, floor rhythm, mullion spacing, column line — when a competing value preserves it. |
| **Privileges** | The module. A repeated element is a design decision with cost, fabrication and rhythm consequences; a one-off deviation from it is usually an error in the brief. |
| **Failure mode** | Inventing a module in order to invoke the rule. The module must come from the input or from a value already locked in `dimensions.json`. "450 would be neater" is not a module. Second failure: applying `R5` to a genuinely non-orthogonal facade, where `07` §5.10 makes `bay_width_cm` a `given` value and there is no module left to preserve. |
| **Mitigation** | Name the module and its source in `resolution.statement`. C-003 does: "the stated 450 cm grid module is affirmed". |
| **Worked case** | **C-003** — "seven equal bays across the front" against an 1800 cm facade and a 450 cm grid. 1800 / 7 = 257.142857, a non-integer module that is not the stated 450; seven bays would put every mullion off a column line. The grid wins: 4 bays, and `facades[0].bay_count` / `bay_width_cm` become `derived` from `structure.x_bay_cm` so the count cannot drift back. |

### 3.6 `R6` LATER-STATEMENT

| | |
|---|---|
| **Resolves** | Same class, same specificity, both buildable, neither module-relevant, no code content: a genuine tie that a deterministic pipeline must still break. |
| **Privileges** | Position in the source. Nothing else. |
| **Failure mode** | Order defined by the agent rather than by the input — reading the aesthetic notes before the room schedule because that is how the text happened to land. The rule would then be non-reproducible: the same brief would resolve differently on a re-run. |
| **Mitigation** | "Later" means **later in the source as received**, and for a multi-sheet input, later in a fixed sheet order that the entry states in `detected_in`. Never later in the agent's own traversal. Every `R6` resolution must say in `resolution.statement` that `R1`–`R5` did not discriminate — this is a hard requirement of the log's honesty and `C-004` demonstrates it. |
| **Worked case** | **C-004** — room schedule `1200 parapet` against aesthetic notes `keep the parapet low, about 900`. Same class, same specificity, both inside the `roof.parapet_height_cm` range 60–150, neither touches the grid. 90 wins on position. The losing 120 is recorded as **outranked, not wrong**, and its `why_lost` says so — which is what makes the decision reversible at zero cost if the room schedule is later confirmed authoritative. |

### 3.7 `R7` DEFAULT-FILL — outside the ladder

| | |
|---|---|
| **Does** | Supply a value when the input is **silent**, from `09-defaults.md`, creating an `A-nnn` entry in `assumptions.json`. |
| **Does not** | Decide, break or influence a conflict. Ever. |
| **Mechanically** | `G-14`: *No `R7` appears in any `rules_invoked`.* Adding a new default-fill rule under a different id does not evade this — `G-14`'s prohibition is on the *behaviour*, and P2c checks the ladder, not the spelling. |
| **Borderline, resolved** | A default range may be cited as **corroboration** inside a `why_lost`, provided the deciding rule is a real ladder rule. C-001's rejected 800 cm says it is "below the office range carried in `09-defaults.md`" — and its `rules_invoked` is `["R3", "R2"]`, with no `R7`. That is legitimate: the range explains *why the brief's own arithmetic is implausible*, and `R3` is what decided it. Had `rules_invoked` been `["R7"]`, the entry would be a validation error. |
| **Worked case** | Not applicable by construction. The 22 defaults consumed by `pavilion-01` are all `A-nnn` in `examples/assumptions.json`, none of them appears in `conflicts_resolved.json`. |

---

## 4. When it is **not** a conflict

The most common way to corrupt this pipeline is to reach for the conflict log when the conflict log is
the wrong instrument. Silence, revision and consequence are not contradiction.

| Situation | Correct instrument | Why |
|---|---|---|
| The input says nothing about a key that the schema requires | **Assumption** `A-nnn` from `09-defaults.md` | Silence is not contradiction. `R7` fills it; it never decides anything. See §3.7. |
| The input says nothing and a default would be a guess | **Assumption** with `confidence: "low"`, or **escalate** (§6) | A low-confidence assumption and a question are both honest; a `medium` one is not. |
| Two sources state the **same** value | Nothing | An entry with two sources and one value is noise. `conflicts[]` may legitimately be empty. |
| The user **revises** a decision after the spec was locked | **Supersede**, not conflict: new file `status: "superseded"` on the old, new file declaring `"supersedes": "<old spec name>@<version>"` in `source` (`07` §3.1) | A revision is a change of intent over time; a conflict is two intents alive at once. Filing a revision as a conflict fabricates a contradiction the user never had. |
| A value is computed from a resolved one (`total_height_cm` from two heights; `bay_count` from `x_bay_cm`) | **`origin: "derived"`** with `derives_from`; recomputed by `G-32` | Consequence is not choice. C-001's and C-003's downstream effect is exactly this: the derived value can never drift from its inputs, so a future re-decision changes one input and the consequence follows. |
| A value is consistent but sits outside the range `07` declares for its key | **Assumption or conflict depending on origin** — but *not* a silent narrowing | `07` §12 forbids narrowing a declared range because the current project happens to sit inside it. If the user's value is genuinely out of range, that is a `R4`/`G-16` question with the user (§6), not a range edit. |
| Two statements differ about something the grammar has **no key for** | Do **not** invent a key | `07` §1 S-4 and §12: reserved files are reserved. Ask, or record it in the brief and drop it. |
| The contradiction cannot be resolved by `R1`–`R6` (e.g. two mutually exclusive design intents, no ordering information) | **Escalate** (§6), and leave `rules_invoked` empty only if the entry explicitly documents the unresolved state | `G-14` permits an empty `rules_invoked` **only** for an entry that documents an unresolved conflict. An empty array plus a chosen value is a validation error. |
| A code requirement is violated and the agent can only guess what the code says | **Escalate** (§6) | `R1` needs a stated requirement, not a remembered one (§3.1). |

---

## 5. The conflict record

### 5.1 Shape — the fields a validator can check

One entry per contradiction. Schema fixed by `07` §7.2; the right-hand column is what makes it
checkable rather than narrative.

| Field | Type | Req | Checkable as |
|---|---|---|---|
| `id` | string | yes | matches `^C-\d{3}$`, unique, ascending within the file — `G-11` |
| `title` | string | yes | non-empty; one line stating the contradiction |
| `detected_in` | string | yes | non-empty; names the paragraphs / sheets / cells, which is also what fixes "later" for `R6` |
| `invariant_violated_if_unresolved` | string | yes | a real `G-` id from `07` §9 — `G-14` |
| `sources[]` | array | yes | `≥ 2` entries, each `{ ref, statement, value, unit }`; `unit` is `cm`, `deg`, `m2`, `count` — `G-14` |
| `rules_invoked` | array | yes | bare ids, **ascending**, `≥ 1`, every id in `precedence_rules.rules`, **no `R7`** — `G-14` |
| `rule_names_as_proposed` | array | yes | human-readable mirror of `rules_invoked`, marked provisional; never read by the validator |
| `resolution.chosen_sources` | array | yes | non-empty; every `ref` appears in `sources[]` |
| `resolution.chosen_value` | any | yes | **deep-equal** to the value at `resulting_value_of` — `G-14` |
| `resolution.statement` | yes | yes | what was decided, and which rule decided it. For an `R6` entry it must also state that `R1`–`R5` did not discriminate |
| `resolution.resolved_paths` | array | yes | dotted paths in `dimensions.json`; coverage is tested **by prefix**, so `openings[11].head_cm` satisfies an origin recorded at `openings[11]` — `G-13` |
| `resolution.resulting_value_of` | string | yes | one primary path; the anchor for the `G-14` equality check |
| `resolution.downstream_effect` | string | yes | what visibly changes downstream |
| `rejected[]` | array | yes | `≥ 1` entry `{ ref, value, why_lost }`; `why_lost` must name the rule that beat it |
| `downstream_stages` | array | yes | non-empty; stage ids `P3`…`P9` |

Two shapes the validator enforces that are easy to get wrong:

- **`G-13` coverage is bidirectional by prefix, in both ledgers.** `assumptions.json.cross_references.conflict_sourced_paths`
  in the example lists `openings[11]` for `C-002` while the entry's `resolved_paths` names
  `openings[11].head_cm`. Both directions resolve.
- **A `C-` id may not appear under `assumptions`** (§6.2 of `07`). `assumptions.json` has exactly one
  ledger; `cross_references` is a reader's convenience, not a second ledger.

### 5.2 `precedence_rules` — the log is self-contained

`conflicts_resolved.json` carries the ladder it was decided with, copied in, so a reader never has to
open this file to know what `R3` meant:

| Key | Content |
|---|---|
| `note` | Adoption status; **must name the file that owns the definitions** — `references/10-conflict-resolution.md` |
| `evaluation_order` | `strict ladder, lowest id first; the first rule that discriminates between the competing sources wins` |
| `rules[]` | `{ id, name, statement }` ascending — `R1`…`R6`. **`R7` is not in this array** |
| `non_conflict_fallback` | the single object for `R7`, kept structurally separate so it cannot be walked by mistake |

Putting `R7` in a `non_conflict_fallback` object rather than in `rules[]` is the structural half of
`G-14`: a resolver that iterates `rules[]` cannot reach it.

### 5.3 `rules_invoked` convention

| Rule | Value |
|---|---|
| Form | **Bare ids only** — `"R3"`, never `"QUANTITY-OVER-SUMMARY"`. Renaming a rule therefore never invalidates an entry. |
| Order | Ascending by id. |
| Content | **Every rule that discriminated**, not only the winner (§2.3). |
| `R7` | **Forbidden.** A default that decided a conflict is a bug (§3.7, `G-14`). |
| Empty | Only for an entry that documents an unresolved conflict and is escalated (§6). An empty array alongside a `chosen_value` fails `G-14`. |
| Unknown id | A validation error — ids must exist in `precedence_rules.rules`. |

---

## 6. Escalation — what may not be decided alone

A subagent working the input stage **may** resolve a conflict by the ladder. It **may not** decide any
of the following alone, even when the ladder appears to have an answer. Escalation means a question
put to the user with the two candidate values, the rule that would decide, and the downstream cost —
not a delay, and not a silent choice.

### 6.1 Hard escalations

| # | Domain | Why it is not the agent's call | What to bring back |
|---|---|---|---|
| E1 | **Structural system and sizing** beyond a low-confidence proxy: framing material, load paths, foundations, anything load-bearing | A licensed structural engineer signs this. `A-004` (column section) and `A-007` (core wall thickness) exist in the example **as proxies** with `confidence: "low"` and `recheck_stage: "P3"` — that is the limit of what an agent may assume, and even those two are borderline. | The proxy value, its range, and what P3 must re-check. |
| E2 | **Life safety**: egress width, number of exits, travel distance, stair geometry, door swing and panic hardware, compartmentation, fire separation, fire ratings, sprinkler and alarm provision | Code-driven. `R1` cannot be used from memory (§3.1) and `09-defaults.md` marks these rows code-driven for exactly this reason. | The question, and an explicit statement that no figure has been assumed. |
| E3 | **Any area or cost figure that will be quoted to the user** — GFA, NFA, usable area, budget, rate | An invented number that reaches a client is a professional commitment, not a placeholder. `gross_floor_area_m2` and `net_floor_area_m2` are `derived` (`G-32`) and safe to state; `net_usable_area_m2` is `assumed` (`A-010`, `A-011`) and is **not** a quotable figure until confirmed. | Both numbers, labelled `derived` / `assumed`, with the assumption ids. |
| E4 | **Storey count, footprint, or plot boundary** | These set everything downstream and are the two most expensive things to change after modelling. | Both candidates and the downstream stages that rebuild. |
| E5 | **Façade composition** — whether an elevation is glazed, blank, or punched, and which bays | Design intent, not geometry. `A-016`…`A-022` show the agent adding openings to un-described elevations; that is a **rendering-quality decision** with a stated rationale, and it is one the user may reasonably reverse. | The added openings, their ids, and the alternative of leaving the elevation blank. |
| E6 | **Roof build-up**: form, drainage strategy, whether the roof is in scope at all | `roof.type` and `roof.deck_thickness_cm` are `given` in the example, but a wrong roof form invalidates massing, NURBS and materials. | The form options and their effect on `building.total_height_cm` / `overall_height_cm`. |
| E7 | **Client, authority or heritage constraints** — anything the user framed as a requirement imposed by someone else | The agent cannot verify them, and inventing one is worse than omitting it. | The question, unprompted by any default. |
| E8 | **Any conflict where `R6` would be the deciding rule on a code-adjacent value** — parapet height on an escape route, guard height, stair landing length | `R6` breaks ties by position alone. On a life-safety value, position is not a reason. | Both values, both sources, and an explicit note that the tie is unresolvable on principle. |
| E9 | **Site address, coordinates, or orientation reference axis** where the answer depends on a real site | `A-001` records 0° for a brief with no orientation; that is a modelling convenience, not a site fact, and it must never be reported as the site's true orientation. | Confirmation, or an explicit "orientation is a modelling convention" note in the delivery. |

### 6.2 What happens to the stage if something stays open

An open escalation is **not** a reason to lock the file. `G-4` makes a non-`locked` file an error for
any build and a warning for a lint, which is precisely the desired behaviour: S1 reports the open
question, `status` stays `draft`, and no downstream stage can consume a spec that is not settled.
Locking a file with an open escalation trades a visible question for an invisible defect.

---

## 7. Worked decision traces

Three of `pavilion-01`'s five entries, end to end. Values and ids are the committed ones.

### 7.1 C-001 — summary against parts (`R3`, then `R2`)

| Step | Content |
|---|---|
| **Detected** | Brief paragraph 2 says overall height is *roughly 8 m* (800 cm). Paragraph 3 gives ground storey floor-to-floor 420 and first floor 400. |
| **Class of dispute** | Stated total vs stated parts. Both are lengths in cm. |
| **Ladder** | `R1` — no requirement in the input → all of `S`, no discrimination. `R2` — both statements name scopes (a total; two named storeys), so specificity *could* discriminate; deferred, because `R3` is cheaper and comes first. `R3` — the two per-storey heights produce 820; the 800 total disagrees with its own parts and cannot be reached without altering a directly stated dimension. **Discriminates.** `R2` — retained as a second discriminator: each storey figure is tied to a named storey, the 800 is not. |
| **Chosen** | `sources: ["brief:para3"]` → `chosen_value: 820.0` |
| **Rejected** | `brief:para2` = 800. `why_lost`: a summary that cannot be satisfied without altering a directly stated dimension; honouring it would compress a storey to 380, below the 400 the brief itself states. The `09-defaults.md` office band is cited as corroboration only. |
| **Written** | `levels[0].height_cm` → `origin: conflict`, `origin_ref: C-001`; `levels[1].height_cm` likewise; `building.total_height_cm` → `origin: derived`, `derives_from` the two heights, `conflict_ref: C-001`. |
| **Downstream** | `G-18` (0 → 420 → 820) and `G-19` (820 = 420 + 400) both hold; `roof.deck_level_cm` derives to 820; `building.overall_height_cm` derives to 910 once `C-004` fixes the parapet. Because the total is `derived`, no later hand edit can put it out of step (this is C-001's own `downstream_effect`). |

### 7.2 C-002 — an opening that cannot exist (`R4`, then `R2`)

| Step | Content |
|---|---|
| **Detected** | Paragraph 4: the glazed bay runs to a head at 380 and keeps a 60 cm spandrel. Paragraph 3 locked level 1's floor-to-floor at 400 via C-001. |
| **Class of dispute** | Within one paragraph: head 380 and spandrel 60. Against the locked storey height. |
| **Ladder** | `R1` none. `R2` both statements name the same element, so specificity does not separate them yet. `R3` neither is a total. `R4` — 380 + 60 = 440 against a 400 floor-to-floor: the head would run 40 cm past the roof deck. `G-26` (`head_cm ≤ levels[].height_cm`) fails. **Vetoes 380.** `R2` — now decides what survives: the spandrel is element-specific, the head figure is bare, so the spandrel is the more specific statement. **Discriminates.** |
| **Chosen** | `sources: ["brief:para4", "brief:para3"]` → `chosen_value: 340.0` (= 400 − 60) |
| **Rejected** | `brief:para4` = 380, `why_lost`: contradicts the same paragraph's 60 cm spandrel; `BUILDABILITY` rejects it outright and the element-specific spandrel outranks the head figure under `SPECIFICITY`. Most likely a transcription of the ground-floor head of 400. |
| **Written** | `openings[11].head_cm` = 340, `origin: conflict`, `origin_ref: C-002`. Width stays 420 (a `curtain_wall` strictly narrower than its 450 bay, so `G-27` holds). |
| **Downstream** | The upper glazed bay is 340 cm tall, not 380; the P5 facade grid panel count on that bay changes. The entry's `downstream_effect` also carries the **residual asymmetry** the log exists to expose: the ground-floor glazed bay keeps the brief's own head of 400 against a 420 floor-to-floor, i.e. a 20 cm spandrel. That is buildable and was never in conflict, so it is carried forward as found rather than silently normalised to 60 — with an instruction to reopen `C-002` rather than edit `dimensions.json`, because `G-9`/`G-10` will block a hand edit to a conflict-sourced path. |

### 7.3 C-004 — a true tie, broken on position (`R6`)

| Step | Content |
|---|---|
| **Detected** | Room schedule: parapet 1200. Aesthetic notes: *keep the parapet low, about 900*. |
| **Class of dispute** | Two bare single values of the same class, same specificity. |
| **Ladder** | `R1` no requirement. `R2` neither names a scope — **no discrimination**. `R3` neither is a total — no. `R4` both buildable; 120 and 90 both sit inside the `roof.parapet_height_cm` range 60–150 — no. `R5` neither invokes the grid module — no. `R6` **discriminates on position**, and the entry's `detected_in` fixes the order: room schedule, then aesthetic notes. |
| **Chosen** | `sources: ["brief:aesthetic_notes"]` → `chosen_value: 90.0` |
| **Rejected** | `brief:room_schedule` = 120, `why_lost`: same class and specificity as the competing value, nothing above `R6` applies, it appears earlier in the brief. **Not rejected as wrong, only as outranked** — if the room schedule is confirmed authoritative the value reverts with no other change needed. |
| **Written** | `roof.parapet_height_cm` = 90, `origin: conflict`, `origin_ref: C-004`. |
| **Downstream** | `building.overall_height_cm` derives to 910 rather than 940 (`G-20`); the parapet instance in P6's assembly layer inherits the lower value. `C-001`'s `derived` total is unaffected, because the parapet sits above the deck. |
| **Honesty requirement met** | `resolution.statement` explicitly says "`R1` to `R5` do not discriminate here", which is the condition `R6` places on itself (§3.6). An `R6` entry that does not say this has not done the walk. |

---

## 8. Rule maintenance

`07` §12 governs, and for this file one distinction matters more than the rest:

| Change | Is it a schema change? | What must happen |
|---|---|---|
| **Rename** a rule, keeping its id | **No** | Update §3 of this file and the `name` / `rule_names_as_proposed` strings. `rules_invoked` holds bare ids, so no conflict entry changes. |
| **Restate** a rule's wording | **No**, if the meaning is unchanged | Keep the statement byte-identical in `07` §7.1 and in the example's `precedence_rules.rules` — they are copies of one definition. |
| **Re-order** the ladder | **Yes** | Existing entries may have been decided on the old order. Re-walk every conflict whose `rules_invoked` contains a rule that would now discriminate differently, and regenerate the example if any decision flips. |
| **Add** a rule, remove one, or re-number | **Yes** | `07` §12: *adding a rule to §7.1 is a schema change, not a documentation change.* Existing `conflicts_resolved.json` files decided without it may need re-deciding, and every `rules_invoked` array must be re-checked against the new ladder. Update `07` §7.1, this file, and `examples/conflicts_resolved.json` **in one change**. |
| **Give `R7` ladder behaviour** | **Forbidden** | It would make every existing conflict re-decidable and would break `G-14`'s meaning. A new silence-filler gets a new name and stays outside `rules[]`. |

Ids `R1`–`R7` are disjoint from the invariant namespace `G-1`…`G-33` defined in `07` §9, so the two
can be cited in the same sentence without ambiguity — `C-002` is decided by `R4` and checked by `G-26`.