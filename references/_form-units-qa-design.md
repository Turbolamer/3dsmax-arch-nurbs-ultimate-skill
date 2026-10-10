# Form precision, native Max units and automatic QA — design proposals & decision register

**Status: FROZEN — approved by user on 2026-10-10; all 10 A-* decisions APPROVED; Gate 02 PASS.**
Date: 2026-10-09. Repository: `D:/Rhino/3dsmax-arch-nurbs-ultimate-skill`.
Owning authority: `AGENT_PLAN_form_precision.md` (the root plan). This file is that plan's English
decision register, derived from it. Where this file and the root plan disagree, the root plan wins
until a phase-02 freeze record says otherwise (`plan §1`).

> **Nothing in this file is a shipped contract.** Every row below is either a decision the user has
> already taken (section 3), a fact recorded in this repository's evidence (section 5), or a
> *proposal awaiting approval*. The design only becomes binding at the **phase 02 freeze plus
> explicit user approval**, recorded in section 4's approval package. Until then: no `.py` file may
> be created for any item in section 6's second table, no new invariant ID may be consumed, no
> tolerance may be chosen, and no unit factor may be implemented. `L-SESSION` forbids even the
> Max calls and builders that would normally precede a freeze (`plan §2`).

---

## 1. Purpose and how to read this file

The root plan is a **Russian planning document** that is never shipped (`plan §1`). This file is the
English artifact that a later executing agent reads instead. It exists to answer four questions
fast, without re-deriving anything:

1. **What is already decided?** — sections 2 and 3.
2. **What is not decided, and who decides it?** — section 4.
3. **What do we actually know, and how do we know it?** — section 5, three separated registers.
4. **What exists today versus what is only proposed?** — sections 6, 7, 8.

Microtask **02.1** adds the **PROPOSED** schema/compatibility/tolerance details in §§11–13;
§13.4 is its local design-only gate. The ten approvals in §4 remain OPEN.
Microtask **02.2** continues in [§14](#14-proposed-022-policy-and-navigation)–§19: exact recommended
policies, runtime artifact inventories and named calibration gates. [§19.1](#191-current-u-register-with-021-history-retained)
retains the 02.2 U-register snapshot.
Microtask **02.3** completes the design register in [§20](#20-proposed-future-cli-and-contextual-inventory-integration)–[§24](#24-local-023-document-gate-record):
CLI syntax, stage-aware contextual inventory, atomic publication & wall representation, fixture/recipe locations,
consolidated dispositions for U20–U22, the consolidated 10 APPROVED A-* approvals in [§23.3](#233-consolidated-10-open-a--approval-package-for-phase-024),
and the local document gate record in [§24](#24-local-023-document-gate-record).

**Provenance markers used throughout.** Every factual claim carries one:

| Marker | Meaning |
|---|---|
| `CHECKPOINT.md:<line>` | executed live against 3ds Max, transcript retained in this repo |
| `AGENTS.md:<line>` | recorded repo convention distilled from an executed transcript |
| `file:line` | read out of current source; true of the source text, proves nothing about Max |
| `plan §N` | stated by the root plan; inherited, not independently re-derived here |
| `PROPOSED` | the plan's recommendation or this file's restatement of it; **not approved** |

**The words `VERIFIED` are reserved.** They may only appear next to something in the
`HISTORICAL-MEASURED` register. A source-observed fact is *true of the source* and an unverified
item is *unknown*; neither is measured. Conflating those three is the exact failure this repo has
already paid for once (`CHECKPOINT.md:1058`).

**Minimal mandatory reference for the whole programme** (`plan §1`): a finished semi-elliptical
cylindrical barrel vault plus references to the arc/ellipse_arc of its own cross-sections. A
structural check of the legacy model is a *separate* deliverable and does not substitute for the
analytic form check.

---

## 2. Authority order

Reproduced from `plan §1`. Priority 1 wins. This table exists so that a later agent does not
re-ask a question the user has already answered, and does not treat a planning document as a
specification.

| Priority | Document / decision | How it is used |
|---|---|---|
| 1 | The user's current explicit decision and the confirmed locks, embedded in full in `plan §2` | Defines scope. Three main decisions are already closed; no temporary decision file is needed |
| 2 | The root plan; after FREEZE, this approved shipped English file | The frozen English contract supersedes the Russian root plan for execution. Only the user changes scope |
| 3 | Dated CHECKPOINT/AGENTS transcripts with their controls | The basis for a technical fact **only** in the measured context in which it was measured |
| 4 | Current source, especially `main()`, loaders and checks | The basis for claims about existing CLI/behaviour. **Not** proof that a Max API works |
| 5 | `AGENT_BRIEF_form_precision.md`, active playbooks, PLAN/SKILL | Applied only in the part the override table below does not cancel. Old contradictions must not be silently bypassed |
| 6 | Optional temporary decision/audit artifacts | Author's supporting evidence. Not a prerequisite for execution and not a new live certification |

### 2.1 Old restriction → new binding meaning

The override table from `plan §1`. **These are settled. Re-asking any of them is a defect in the
asking, not a legitimate question.**

| Old restriction | New binding meaning | What survives |
|---|---|---|
| Brief §1/§7 phase 6/§10: P8 and `qa.json` are forbidden | P8/S7 is restored; `qa.json` is a plan, the report is separate | P7/P9 stay cancelled; QA creates no materials, no UVs, no export |
| Brief §4/§5: scene cm/1 only, numbers without rescaling | Specs are cm; the Max boundary is aware of `SystemType` and `SystemScale` | The user's real scene settings are preserved |
| D8 open, choose A or B | **D8 = A**: source parameters live in `dimensions.json` | Derived-only G-49 remains for NURBS. Option B is not to be implemented |
| D1 forbids any edit to `build_spec` / `build_nurbs` | The generator does not become a builder primitive; edits to the dimensional sinks are nonetheless necessary | Only the owner, and only a separate permission, for the enumerated emitter/library files |
| Phase 6 is exclusively manual probes | A minimal analytic reference is **required** by the mandatory QA | The general intent DSL stays design-only |
| P8-a…g in the cornice phase | Rename to MOULD-a…g | That is **not** a P8 QA phase |
| "All builders are protected against overwrite" | An observable source/doc discrepancy; the protection must be designed and tested | One cannot rely on a common protection that does not exist |
| The old brief's priority "if it diverges, ask" | The confirmed overrides above are not to be re-asked | New decisions about schema/tolerances/corrections do require the gate |

The dated 2026-10-05 cancellation of P8 remains history (`CHECKPOINT.md` P7/P8/P9 rows). Only an
authorised phase changes active routing. A future CHECKPOINT entry written during planning does
**not** mean "implementation done", "measured", or "P8 accepted" (`plan §1`).

Future shipped references, agent playbooks, scripts/comments/help text and CHECKPOINT updates are
written **in English**. The root plan itself stays Russian (`plan §1`).

---

## 3. Locked decisions — CLOSED, do not re-ask

Verbatim from `plan §2`. Each of these is a user decision already taken. Re-asking any of them
violates the authority table in section 2.

| Lock | Already decided — do not ask again |
|---|---|
| **L-UNIT** | Canonical lengths are **cm** and keys carry the `_cm` suffix. Explicit **mm** input is normalised offline. Max receives **native** values |
| **L-QA** | **P8 is automatic.** `qa.json` is a *locked configuration / check plan*. Raw evidence and `qa-results.json` are separate artefacts |
| **L-D8** | `dimensions.json` owns the **source** parameters. Generator and points are **derived**. The QA reference is **independent of the points** |
| **L-SESSION** | Right now, this plan only: **no** Max calls, builders, git mutation, checkpoint edits or installation |
| **L-SCOPE** | Source-brief phases 5 and 8 need a separate "yes"; 7 is design-only; the general intent language is design-only |
| **L-HISTORY** | The existing `examples/` and the old `barrel-vault.json` stay **byte-identical** |
| **L-SAFETY** | Assembly `G-81` is modifier-free. Other stacks: **≤5 additions per call**, **>10 per node only after asking**, **20 never** |

### 3.1 The unit factor, as a proposal to be frozen

`L-UNIT` fixes the *canonical* side. The *boundary* side is still to be frozen, and the following is
the plan's proposal, not an approved contract (`plan §6.2`):

Let `k` be the number of centimetres in one base `SystemType` unit and `s = units.SystemScale`.
Then `c = k·s` cm per scene unit and `f = 1/c`.

- write: `L_scene = L_cm / c`, `point_scene = point_cm / c`
- readback: `L_cm = L_scene · c`
- area readback: `A_m2 = A_scene² · c² / 10000`
- volume readback: `V_cm³ = V_scene³ · c³` — powers apply per quantity type
- never converted: degrees, counts, weights, ratios, normalised schedules, knots, percentages

Candidate `k` values (mathematical, `plan §6.2`): mm 0.1 · cm 1 · m 100 · km 100000 · inch 2.54 ·
foot 30.48 · yard 91.44 · mile 160934.4. **The exact runtime enum spellings are future probes.**
`c`, `f` and `s` must be finite and positive; missing, zero, NaN or unknown data must **never** fall
back to cm. A change of the system tuple between stages or inside batches invalidates the build/run.

Candidate mathematical constants are **not** evidence that the runtime enum for kilometre exists.

---

## 4. Unapproved decision register

**Owner for every row below is the user. Status: APPROVED for all 10 decisions (User approved 2026-10-10 at Gate 02).** These decisions were
formally approved by the user as a unified package. The plan states a recommendation for each; a recommendation is a starting point for a
conversation, not a decision.

> **HARD RULE — a recommendation is not a decision. No default may be invented in order to start
> coding. All ten are asked as one package in phase 02.4, then STOP.**
> If a later patch finds itself needing one of these values and no approval record exists, the
> correct action is to write the exact question into the design register and stop — not to choose
> the recommended value (`plan §5`, opening paragraph).

| ID | Recommendation in the root plan | Exact question the user must approve | Owner | Status |
|---|---|---|---|---|
| **A-VERSION** | Explicitly support **1.0** and **1.1**; new references / generator / QA config ship as 1.1; exact-spelling proposal in [§11.1](#111-proposed-version-and-per-file-compatibility-matrix) | Which minor versions and patch spellings are supported; mixed-file compatibility; unknown-version refusal; owner migration | user | **APPROVED** (User approved 2026-10-10) |
| **A-TOL** | Separate **arithmetic**, **form** and **numerical** budgets; proposed leaves in §12.4 and comparator/volume policy in [§13.1](#131-proposed-dimensional-budgets-and-boundary-comparator) | Physical form threshold, cm³ propagation, numerical calibration, zero policy and boundary comparator; no value is approved by 02.1 | user | **APPROVED** (User approved 2026-10-10) |
| **A-FIELDS** | Constrained v1: [§11.2–§11.4](#112-envelope-leaf-table) and [§12](#12-proposed-form-generator-and-qa-leaf-inventory) supply exact proposed fields/joins/origins | Names, types, units, containers, kind-specific keys, target kinds and provenance exemptions; §13.3 lists pending 02.2/02.3 choices | user | **APPROVED** (User approved 2026-10-10) |
| **A-CLOSED** | An explicit 360° and shell-equality policy | Whether a closed consumer is permitted at all; the exact seam; the minimum distinct point count; the 0.001 cm equality rule | user | **APPROVED** (User approved 2026-10-10) |
| **A-EXAMPLE** | A new coherent fixture under `specs/fixtures/form-precision/`, with the recipe in a separate file | Where the QA example lives under the §12 grammar, without editing the old `examples/` | user | **APPROVED** (User approved 2026-10-10) |
| **A-WRITE** | Draft-only expansion; transaction/ownership rules for computed outputs | The refusal/replacement rules and the journal for an unfinished JSON+MS pair | user | **APPROVED** (User approved 2026-10-10) |
| **A-OWNERS** | The sequential patch scopes of `plan §8`–`§10` | Permission for the narrow edits to existing emitters, library, validator, scaffold and future docs | user | **APPROVED** (User approved 2026-10-10) |
| **A-LIVE** | Isolated, explicitly authorised rehearsal scenes | Permission for probes, the unit matrix, replay and named cleanup; production stays read-only QA | user | **APPROVED** (User approved 2026-10-10) |
| **A-CORRECT** | On a confirmed defect, a separate stage-owner patch | A dimension-correct `G-82` and the representation of the full wall host, rather than an exemption from QA | user | **APPROVED** (User approved 2026-10-10) |
| **A-REGEN** | Historical `examples/` stay separate from new adaptive examples | Whether to regenerate only an owner-driven copy in a newly approved location | user | **APPROVED** (User approved 2026-10-10) |

Two consequences of the table, both from `plan §2`:

- The design-only notes on intent / per-level footprints / mouldings **grant no permission** to
  implement them.
- Archive rebuild and global installation are **two different** future permissions, both requested
  only after measured gates pass. Creating a branch, committing or pushing is not part of this
  programme and happens only on a separate explicit user request.

---

## 5. Evidence classification

Three registers. They must never be merged, and the words `VERIFIED` belong only to the first.

### 5.1 `HISTORICAL-MEASURED`

Facts executed live against 3ds Max 2026, with a dated transcript and controls retained in
`CHECKPOINT.md`. **Each row states what it does and does not prove** — the scope limit is the
important half.

| Claim | Where recorded | What it proves / does not prove |
|---|---|---|
| `Box(width:,length:,height:,pos:)` is the placement primitive; geometry is centred on `pos.x`/`pos.y` and the **base sits at `pos.z`**; `pos:` moves geometry, not only the pivot | `CHECKPOINT.md:112`, `AGENTS.md:139` | Proves the P3 placement convention in a cm/1 scene. Does **not** prove it survives a different `SystemType`; the base-at-Z behaviour persists through `copy`, `baseObject` assignment and rotation |
| A surface is not evaluable until it is **committed**: `evalPos` returns `undefined` and the parameter range reads `0.0` before `appendObject` + `NURBSNode` | `CHECKPOINT.md:171` | Proves that a commit step is mandatory before any `evalPos`-based QA. Says nothing about sub-object selection *after* commit |
| Relational properties (`rail`, `railID`, `parent*`, `distance`, …) are readable only on the committed sub-object; on a fresh unattached surface every name fails | `CHECKPOINT.md:199` | Proves the commit rule for relations. Does not prove anything about a different relation class |
| `point_grid` interpolates and **overshoots** (lattice peak 510 → node bbox 568.226); `cv_grid` is controlled and **undershoots** (480 → bbox exactly 480, sampled max 448.125) | `CHECKPOINT.md:175`, `CHECKPOINT.md:704` | Proves the difference is architectural, on these two surfaces. **A node bounding box does not prove surface shape** — the sampled grid is what measured it |
| Parameter domain differs by kind: `point_grid` is **chord-length** (`u=[0,434.555]` for a 400 cm lattice); `cv_grid` is normalised `[0,1]` | `CHECKPOINT.md:176` | Proves the domain is kind-dependent and **not** a universal length contract. Proves nothing about an ellipse angle or a crown position |
| Curve knots are normalised to `[0,1]` by `setClampedKnots`; an unattached curve's `parameterRangeMin/Max` read `[0,0]` | `CHECKPOINT.md:177` | Proves knots are dimensionless fractions. An unattached curve's range property is meaningless |
| `parent:`/`rail:` read back **`0`**, not the 1-based index passed; `railID` reads a `nurbsID`; `nurbsID` is an `IntegerPtr`, not a string | `CHECKPOINT.md:207`, `CHECKPOINT.md:244` | Proves the read-back mismatch that `G-56` exists to prevent. The printed `"0P"` form was itself **not reproduced** |
| A **synthetic `nurbsID` crashes 3ds Max** — `parent1ID:12345` → `EXCEPTION_ACCESS_VIOLATION`, not a catchable error | `CHECKPOINT.md:245` | Proves a hard process crash, hence `G-56`: never emit a literal in a `parent*ID:` slot. It is a crash, so no `try`/`catch` contains it |
| A relation's parents need not live in the relation's `NURBSSet`; cross-set `parent1ID:` references work and give identical geometry | `CHECKPOINT.md:246` | Proves cross-set reference works. Says nothing about a *curve*-rail cross-set form, which remains unverified |
| `NURBSBlendSurface` tension `0.0` is the straight transition; larger tension pushes the blend past **both** edges (`1.0/1.0` → 295.64 cm outside its own geometry, 50 cm below springing). Max neither rejects nor bounds it | `CHECKPOINT.md:239` | Proves tension must stay in `0.0…1.0` and that the overshoot grows with it. This is the defect behind the `0.0` default |
| A NURBS node's `min`/`max` is **not** the NURBS geometry: a closed `NURBSPointCurve` over a `750…1050 × 375…525` rectangle has node bbox `714.645…1080.17 × 286.503…617.732` | `CHECKPOINT.md:250` | Proves node bbox must never be used as a shape measurement. Directly relevant to every form check |
| `setCopyMode` **does not exist**; the instance route is `n = copy src` then `n.baseObject = src.baseObject`. Measured discriminator on the same node: a plain `copy` shares nothing (`false`), after the assignment it does (`true`) | `CHECKPOINT.md:858` | Proves absence of `setCopyMode` against a calibrated sweep with a bogus-name control. Also proves a plain copy is **not** an instance |
| `rotationZ`/`rotationX`/`rotationY`/`angle` do not exist; the route is `n.rotation = quat <deg> [0,0,1]`. Geometry check: a 100×200×20 box spans X 200 / Y 100 at rot 90 | `CHECKPOINT.md:859` | Proves the rotation route in cm/1. Does not prove anything about rotation under a non-1 scale |
| A **20-modifier** stack on one `Box` in one scripted call froze Max permanently; the bridge stopped answering; Max was killed and the machine rebooted. 1·2·5·10 rungs were clean (~28–38 ms); the break is between 10 and 20 and **must not be re-measured** | `CHECKPOINT.md:418`, `CHECKPOINT.md:393` | Proves the ladder result and the exact price. The **exact** breaking point is *not* established |
| The Boolean modifier is unusable in this build; the assembly stage was rebuilt without it | `CHECKPOINT.md:464` | Proves a Boolean-based route cannot satisfy the wall checks. This is why `G-82` is a volume identity and not "the boolean committed" |
| The bridge is **not** dead when `FileStream.Open` returns `OPEN FAIL`: `FileStream` normalises `\\.\pipe\...` against the current drive and tries `D:\pipe`. `CreateFileW` via P/Invoke returns **OK**, and the server answers `pong: true` at RTT 1.6 ms | `CHECKPOINT.md:2061`, `CHECKPOINT.md:2068`, `CHECKPOINT.md:2039` | Proves the "dead pipe" conclusion was an artefact of the probe. Separately, a `ConnectionError` on port 8765 is explained by the client **caching** the pipe name after a Max restart (`CHECKPOINT.md:454`, `CHECKPOINT.md:456`) |
| Live P5 gate: `world_table.csv` read by MAXScript itself → **136 rows**, 136 panels as reference instances, `objects.count` = **165** = 136 + 29 prototypes, 136/136 sharing their prototype's `baseObject`, 5 bboxes exactly equal to an independent prediction, scene back to 0 | `CHECKPOINT.md:58`, `CHECKPOINT.md:824` | Proves the CSV → instance path end to end in cm/1. Does **not** prove determinism of scatter, or any other unit tuple |
| Live P6 gate: `massing.ms` → **27** nodes, idempotent over 3 runs, 9/9 bboxes exact (0.000000 cm); `assembly.ms` → **244** nodes = 27 + 136 `PLC_` + 29 `PROTO_` + 52 `WAL_`, **0 modifiers**, volume identity exact to 0.000000 cm³ on all 8 hosts, scene back to 0 after two sweeps | `CHECKPOINT.md:59` | Proves the assembly stage as built. Historical exact-zero measurements here do **not** prove the phase-11 visibility fix |
| Full chain re-run: **254 nodes = 27 massing + 10 NURBS + 217 assembly additions**; idempotent over three calls, 0 modifiers. The **244** massing/assembly nodes contain 239 `Box` + 5 `Dummy`; 136 `PLC_` + 29 `PROTO_` + 52 `WAL_` are already included in those 239 boxes | `CHECKPOINT.md:63`, `CHECKPOINT.md:1146–1150` | Proves the S1→S5 chain in cm/1. Historical P6's **244** excludes the 10 NURBS nodes. An arbitrary project must get its expected set from contracts, not from these constants (`plan §3`) |
| Historical validator baseline: **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** | `CHECKPOINT.md:59`, `CHECKPOINT.md:1144` | A historical baseline. **Not** a future acceptance total and **not** a count of G rules (`plan §3`) |
| `realWorldMapSize:true` = **1 UV unit = 1 cm**, verified on 3 boxes at independent positions | `CHECKPOINT.md:66` | Proves the UV scale in that run only. Materials and UV are out of scope by user decision |
| Transport `namedpipe`, protocol 2, `mainThread`, `safeMode: true` | `CHECKPOINT.md:76` | Proves the negotiated transport at that time. The stage-aware inventory API shape is **not** this |

**Corrections to this repository's own earlier claims.** These were false negatives produced by
probes that could not detect a working feature. They are listed so that nobody re-asserts the
absence.

| Recorded as absent | Actually | Proof |
|---|---|---|
| `getCurrentException()` throws itself / is unavailable | **It works.** 6 of 6 throw kinds returned a real message, repeated 4/4 in a second batch, with a non-throw control proving the catch was not entered | `CHECKPOINT.md:1067`, `CHECKPOINT.md:388` |
| `findString` does not exist | **It works.** `findString "hello world" "o w"` → **5** (1-based); a real miss returns `undefined`; a non-string argument **throws** | `CHECKPOINT.md:1068` |
| `matrix3` does not exist | **It exists.** `matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]` → `classOf` **`Matrix3`**. It takes **4** arguments; the earlier verdict came from calling it with 9 numbers — an arity error misread as absence | `CHECKPOINT.md:1069`, `CHECKPOINT.md:1073` |
| The bridge is dead because the pipe would not open | **The pipe was open the whole time.** `.NET FileStream` normalises the path against the current drive; `CreateFileW` returns OK and the server answers `pong: true` | `CHECKPOINT.md:2068`, `AGENTS.md` §"four false negatives" |

A batch of only throws discriminates nothing. The governing rule is in `AGENTS.md`: *a probe not
calibrated against a known-good case has produced no evidence at all — it has produced a result.*
Still genuinely absent, re-confirmed with the same calibration: `setCopyMode`, `rotationZ`,
`rotationX`, `rotationY`, `angle` (`CHECKPOINT.md:858`, `CHECKPOINT.md:859`), no `mcg_*` tool and
no `curve_model` in the connected toolset (`AGENTS.md:175`).

### 5.2 `SOURCE-OBSERVED`

Read out of current source. **True of the source text. Proves nothing about Max runtime behaviour**,
and does not by itself prove that a builder was ever run.

| Claim | Where | Notes |
|---|---|---|
| `build_spec.render_ms` writes `Box width:{width} length:{length} height:{height} pos:{pos}` straight from the canonical cm figures — no unit conversion anywhere in the emitter | `scripts/build_spec.py:1237`, `scripts/build_spec.py:1244` | Emitters write **raw cm** |
| `place_components.render_ms` does the same for prototype and wall cells: `Box width:{num(width)} length:{num(thickness)}` | `scripts/place_components.py:1415`, `scripts/place_components.py:1465` | Raw cm |
| `nurbs_arch_library.ms` carries **raw physical defaults**: `applyArchTessellation … mergeTol:0.15`, `createULoftShell … thickness:0.0`, `makePointSurfaceGrid … mergeTol:0.15`, `makeCVSurfaceGrid … mergeTol:0.15`, `createDiagridOnSurface … thickness:10.0` | `snippets/nurbs_arch_library.ms:81`, `:104`, `:218`, `:272`, `:293` | These are cm, unconditionally, whatever the scene unit is |
| `createULoftShell` tests `if (abs thickness) > 0.001 do (…append the offset surface…)` — a **strict** `>` | `snippets/nurbs_arch_library.ms:116` | The library drops the offset shell at exactly 0.001 |
| `build_nurbs` mirrors that with a strict `>`: `return 2 if abs(thickness) > MIN_SHELL_THICKNESS_CM else 1`, `MIN_SHELL_THICKNESS_CM = 0.001` | `scripts/build_nurbs.py:568`, `scripts/build_nurbs.py:390` | Census and geometry agree with each other, both strict |
| **`G-47` admits equality.** Both the validator and the builder self-check only complain `elif abs(value) < NURBS_MIN_SHELL_THICKNESS_CM` — so exactly 0.001 passes the lint while the emitter produces no offset surface | `scripts/validate_specs.py:604`, `scripts/validate_specs.py:6725`, `scripts/build_nurbs.py:1234` | **Source-observed contradiction** between the lint threshold and the emitter threshold. The equality policy is an open decision, not a settled fact |
| **`G-82` compares cm³ against a cm²-shaped threshold.** The cell total is a volume in cm³ and the expected value is a volume in cm³, but the test is `abs(cell_volume - expected) > linear * linear` where `linear` is a length tolerance in cm | `scripts/validate_specs.py:12078`, `scripts/place_components.py:2175` | The units on the right-hand side are cm². A dimension-correct cm³ policy is an open decision |
| The same `G-82` body therefore can be satisfied by gaps and overlaps that cancel in total; the per-cell occupancy checks are separate rows | `scripts/place_components.py:2067` | Volume identity is not occupancy. Both are mandatory |
| Builders validate the schema **major only**: `re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?$", …)` and refuse only when the major differs | `scripts/build_spec.py:618`, `scripts/build_spec.py:619`, `scripts/build_nurbs.py:767` | Minor and patch are not checked by builders |
| `validate_specs.py` `G-3` does the same and additionally **WARNs** on any nonzero minor or patch: `elif int(match.group(2)) != 0 or (match.group(3) not in (None, "0")): report.warn(...)` | `scripts/validate_specs.py:1598`, `scripts/validate_specs.py:1604`, `scripts/validate_specs.py:1609` | Consequence: `1.1` is **not** currently a warnings-as-errors-clean known-supported version. That is what an open version decision has to resolve |
| Writers hardcode `SCHEMA_VERSION = "1.0"` | `scripts/build_spec.py:126`, `scripts/build_nurbs.py:183`, `scripts/facade_tables.py:161`, `scripts/place_components.py:136`, `scripts/init_project.py:79` | A writer cannot silently emit 1.1 without a code change |
| `place_components.py` reads **four** inputs: `UPSTREAM_NAMES = (DIMENSIONS_NAME, MASSING_NAME, REGISTRY_NAME, WORLD_CSV_NAME)` and refuses with `refusing to build: {path} is missing…` | `scripts/place_components.py:228`, `scripts/place_components.py:424`, `scripts/place_components.py:473` | The four are `dimensions.json`, `massing.json`, `components_registry.json`, `world_table.csv` |
| `assembly.json` is an **output**, not an input: `OUT_JSON_NAME = "assembly.json"` and the module docstring lists it under "Build" | `scripts/place_components.py:144`, `scripts/place_components.py:2` | The old `AGENTS.md` description is wrong on this point and needs a narrow correction in a future doc phase (`plan §4.1`) |
| `init_project.INVENTORY` lists `materials.json` (P7), `qa.json` (P8) and `export.json` (P9) as **reserved**; `SEEDED_FROM_EXAMPLES` carries 8 JSONs and no CSV | `scripts/init_project.py:96`, `scripts/init_project.py:115` | The three reserved files are stubs. P7/P8/P9 were cancelled on 2026-10-05; P8 is restored by the root plan, P7/P9 are not |
| `init_project.RESERVED_KEYS["qa.json"]` currently carries `("checks", "array")` — a **result-ish** legacy key set | `scripts/init_project.py:131`, `scripts/init_project.py:172` | The root plan requires that a QA config carry no result fields; a legacy stub is not mechanically renamed |
| Last registered invariant is **`G-83`** ("every cell carries its wall's full thickness"); the dispatch list ends `G-80, G-81, G-82, G-83` | `scripts/validate_specs.py:851`, `scripts/validate_specs.py:10782` | The next free ID is **G-84** |
| `RECHECK_STAGES = ("P3","P4","P5","P6")` — P7/P8/P9 are named as cancelled | `scripts/validate_specs.py:94` | A future P8 recheck must be added without reviving P7/P9 |
| No `qa_check.py`, `curve_gen.py`, `expand_curves.py`, `scene_units.py`, `capture_views.py`, `export_max.py`, `build_mouldings.py`, `lint_script.py` or `check_skill_md.py` exists. `scripts/` contains exactly 8 modules | `scripts/` listing | Section 6's second table lists what is only proposed |
| There is no build, test or lint runner in this repository | `AGENTS.md` §"What this repo is" | Do not invent `pytest`, `npm test`, or QA/capture/export scripts as if they ran |
| The emitted `assembly.ms` contains **zero modifiers** and asserts `stray_modifiers != 0 do throw "G-81: …"` inside Max | `scripts/place_components.py:1514`, `scripts/place_components.py:1521` | The zero-modifier property is enforced at run time, not only at build time |

### 5.3 `UNVERIFIED`

Not known. **No probe is invented here** — the settling probes belong to plan phase 03, each with a
known-good control and a known-bogus control in the same batch (`plan §10` phase 03, gate 03).
A batch of only throws discriminates nothing.

| Unknown | What is needed to settle it | Where it is planned |
|---|---|---|
| Exact runtime spellings of every `SystemType` enum, and which are supported at all | A units-enum probe with direct field reads, working and bogus control in each batch | `plan §10` 03.3 |
| Behaviour of a unit scale **other than 1** (mm/10, cm/2 and friends) — seed mapping, both merges, setter echo is not sufficient | A native-unit fixture measuring physical shape and merges, not just a setter read-back | `plan §10` 03.3, 03.6 |
| Exact wire escaping, scalar precision and locale behaviour for MAXScript results | A serializer/locale probe with fractions, negatives, large coordinates, counts and a malformed control | `plan §10` 03.4 |
| The exact protocol enums a QA request/report must use | A protocol calibration probe; a list in a planning document does not make an enum a fact | `plan §10` 03.4 |
| Seed semantics: whether a domain coordinate is a length and how it maps under a non-1 scale | A commit/domain/world-transform/seed control fixture including translated, rotated, parented and non-uniform cases; a local-vs-world error must be detectable | `plan §10` 03.5 |
| Mesh-volume and open-edge APIs for a signed-volume / watertight route (needed only if a bbox-volume assumption cannot be confirmed) | A box/mesh volume route probe with open and inverted controls; a new name must not be declared measured from introspection | `plan §10` 03.8 |
| Whether `render_edge_pct` / `spacialEdge` and `curvatureDistance` are lengths at all — their names must not be read as cm | A semantic probe of percent / `viewDependent` properties | `plan §10` 03.6 |
| Whether the library's first-call merge/approximation defaults actually reach the geometry, as opposed to only echoing a setter | A probe comparing **initial** values against the resulting geometry; a setter-only proof is rejected | `plan §10` 03.6 |
| A library revision guard mechanism, beyond `MCP_NURBS_Arch != undefined` | A tested reload/capability check probe | `plan §10` 03.7 |
| Whether the shape of a stage-aware inventory API exists in any form | Requires an approved gate context first; the CLI shape is a mandatory freeze, not a flag to guess | `plan §4.2`, `plan §10` 02.3 |
| `references/nurbs-complete-guide.md` and `nurbs-architecture-recipes.md` beyond their corrected bugs | Claim-by-claim execution. **Do not rewrite on suspicion** — that already happened once and was wrong | `AGENTS.md` §"the one rule that matters most" |

---

## 6. Current executable surface

### 6.1 `CURRENT` — eight scripts, read from their own `main()`

Every row here is `file:line`-anchored. `--out` defaults to `--in` in all builders. `<p>` is an
absolute pipeline directory. Common flags: `-h/--help`.

| Script | Flags actually accepted | Required inputs | Outputs | Exit codes | Schema-version behaviour |
|---|---|---|---|---|---|
| `env_preflight.py` | `[--results FILE] [--transport TEXT] [--json]` (`scripts/env_preflight.py:726`) | none; `--results` supplies captured outputs | a report; bare mode prints probe bodies and **all checks SKIP**, exit 0 — that is a non-run, not a pass | 1 on a failed check, else 0 (`scripts/env_preflight.py:749`, `:797`) | n/a |
| `build_spec.py` | `--stage TEXT --in DIR [--out DIR] [--json]` (`scripts/build_spec.py:1944`) | locked `dimensions.json` | `massing.json` + `massing.ms` | 0 / 1 refusal / 2 usage (`scripts/build_spec.py:224`) | `STAGES = ("massing",)` (`scripts/build_spec.py:128`); any other stage exits **2**; major-only check (`scripts/build_spec.py:618`) |
| `build_nurbs.py` | `--in DIR [--out DIR] [--json] [--build] [--allow-draft]` (`scripts/build_nurbs.py:2675`) | hand-authored `nurbs.json` | normalised `nurbs.json` + `nurbs.ms` | 0 / 1 / 2 (`scripts/build_nurbs.py:402`) | major-only (`scripts/build_nurbs.py:767`); **no `--stage`** |
| `facade_tables.py` | `[--stage grids/components/tables/all] --in DIR [--out DIR] [--json] [--build] [--allow-draft]` (`scripts/facade_tables.py:3702`) | `dimensions.json` + `massing.json` | `facade_grids.json`, `components_registry.json`, both CSVs | 0 / 1 / 2 (`scripts/facade_tables.py:343`) | `STAGES` at `:163`; writes `SCHEMA_VERSION = "1.0"` (`:161`) |
| `place_components.py` | `[--stage TEXT] --in DIR [--out DIR] [--json] [--build] [--allow-draft]` (`scripts/place_components.py:2348`) | **four**: `dimensions.json`, `massing.json`, `components_registry.json`, `world_table.csv` (`:228`) | `assembly.json` + `assembly.ms` | 0 / 1 / 2 (`scripts/place_components.py:235`) | `STAGES = ("assembly",)` (`:138`); here `--build` overrides `--allow-draft` (`:450`, `:455`) |
| `validate_specs.py` | `[--dir DIR] [--file FILE] [--json] [--warnings-as-errors] [--rule TEXT] [--build] [--allow-draft]` (`scripts/validate_specs.py:12497`) | default `./specs/pipeline`; `--file` loads siblings | a report; `--rule` filters display, not the overall exit | report-driven (`--warnings-as-errors` promotes WARN) | `G-3`: FAIL on major mismatch, **WARN** on nonzero minor/patch (`scripts/validate_specs.py:1598`, `:1609`) |
| `init_project.py` | `--project ID [--dir DIR] [--from DIR] [--force] [--dry-run]` (`scripts/init_project.py:1171`) | none | fresh: 11 specs + a manifest; seeded: 8 JSONs + a manifest, **no CSV, no reserved files** (`:115`) | 0 / refusal | writes `SCHEMA_VERSION = "1.0"` (`:79`) |
| `install_skill.py` | `[--target archive/global/all] [--mcp-repo DIR]` (`scripts/install_skill.py:93`) | none | the `.skill` archive always; `global`/`all` install to both home directories | 0 / error | n/a |

`build_spec.py` accepts no `--build`, `--allow-draft`, `--force` or units flag. `--build` and
`--allow-draft` on `build_nurbs.py` and `facade_tables.py` are **compatibility flags** — the lock
gate is always enforced (`scripts/build_nurbs.py:2679`).

### 6.2 `PROPOSED — NOT IMPLEMENTED`

**None of the following exists.** Naming is provisional until the section-4 approvals are recorded.
Do not write a `.py` file, do not add a flag, do not add a doc route for any of them.

| Proposed item | Status |
|---|---|
| `scripts/curve_gen.py` — import-only stdlib math library | does not exist; naming provisional |
| `scripts/expand_curves.py` — authoring CLI (expand / check / suggest) | does not exist; naming provisional |
| `scripts/qa_check.py` — offline emit + offline assess | does not exist; naming provisional |
| `scripts/scene_units.py` — shared unit-factor emission helpers, **no live connection** | does not exist; naming provisional |
| `agents/max-qa.md` — the S7 collect contract | does not exist; naming provisional |
| `env_preflight --require-complete` — strict gate for captured mode | does not exist; naming provisional |
| A stage-aware inventory API | no approved API or CLI shape exists; guessing a flag is forbidden |
| `scripts/build_mouldings.py`, `references/_form-rings-design.md`, `_form-intent-probes.md`, `_form-per-level-footprint.md`, `_form-mouldings-design.md` | optional phases 14–16, each behind its own approval; **not** part of core |
| `specs/fixtures/form-precision/`, `specs/recipes/nurbs/barrel-vault-generated.json` | proposed placements, not approved |

The validator stays **static**: it must not grow `--results`, a Python connection, geometry evidence,
or a nonexistent `--stage qa`. An emitted `.ms` is not done until it has been `fileIn`-ed and
measured; an emitted CSV is not done until it has been placed in Max and counted (`AGENTS.md`).

---

## 7. Ownership map for future patches

From `plan §8`. **This table is an allocation, not a mass licence.** Each patch row is one coherent
patch followed by STOP/gate; each patch gets its own exact subset. Symbols listed as existing were
read out of source during phase 01.2; **re-read the actual symbols before editing.**

| File | Existing symbols / entry point | Narrow future work | Owning phase |
|---|---|---|---|
| `scripts/validate_specs.py` | `RULE_TITLES:768`, `CROSS_FILE_RULES:861`, `SpecDef:613`, `SPEC_INVENTORY:624`, `run_checks:12195` | **central ID allocation**; dispatch of new static predicates | 04.1 / 06.1 / 10.1 |
| `scripts/validate_specs.py` | `check_envelope:1512`, `check_inventory:12241`, `RECHECK_STAGES:94`, `G-1`/`G-3`/`G-15`/`G-31` | explicit versions; contextual QA presence; a P8 recheck that does not revive P7/P9 | 04.1 |
| `scripts/validate_specs.py` | `check_nurbs_rules:6031`, `_g42_shape:6219`, `_g49_provenance:6849` | generator/reference joins; equal counts restricted to lattices; D8-derived preservation | 06.1 |
| `scripts/validate_specs.py` | `_g82_wall_tiling_volume:11965`, `check_assembly_rules:10786` | dimension-correct volume policy and the visible-host declaration, only under an approved correction | 11.3 |
| `scripts/init_project.py` | `INVENTORY:96`, `RESERVED_KEYS:131`, `SEEDED_FROM_EXAMPLES:115`, envelope, `build_plan:945`, `build_manifest:1013` | draft QA config for fresh **and** seeded; canonical-vs-observed target; proposed `scaffold_qa` | 10.2 |
| `scripts/env_preflight.py` | `SCRIPT_*`, `CheckSpec`/`build_checks`, `ResultsRunner`/`evaluate`/`main:722` | read-only unit capture; a strict complete gate. **No new transport** | 07.2 |
| `scripts/build_spec.py` | `load_locked_dimensions:582`, `Model:650`, `build_massing:718`, `rect_of:516`, `prism_box:1148`, `element_box:1175` | canonical arithmetic. The `rect_of` limitation is preserved until an optional mesh phase | 08.1 |
| `scripts/build_spec.py` | `render_ms:1197`, `verify_script:1767`, `verify_script_shape:1830`, `write_bytes:1757` | length-sink conversion, unit preamble/receipt, approved write transaction | 08.1 / 08.4 |
| `scripts/build_nurbs.py` | `load_spec:728`, `normalise:695`, `section_literal:1839`, `tessellation_line:1850`, `dependent_surface_lines:1937` | version/metadata checks; points/merges/thickness conversion **without generator math** | 09.3 / 09.5 |
| `scripts/build_nurbs.py` | `expected_census:542`, `MIN_SHELL_THICKNESS_CM:390`, `self_check:863`, `render_ms:2049`, `verify_script:2240` | shell equality in cm; library revision/reload guard; first-call defaults | 09.2 / 09.4 |
| `scripts/build_nurbs.py` | `main:2668`, `write_bytes:2587`, `serialize:2577`, `strict_loads:663` | the 09.6 JSON+MS guarded transaction and recovery; a same-path draft input keeps its bytes | 09.6 |
| `snippets/nurbs_arch_library.ms` | `applyArchTessellation:81`, `createULoftShell:104`, `createUVLoftNetwork:128`, `makePointSurfaceGrid:272`, `makeCVSurfaceGrid:293` | scene-native optional arguments and initial propagation; **no double conversion** | 09.1 / 09.2 |
| `snippets/nurbs_arch_library.ms` | `sampleSurfaceToQuadPoly:176`, `createDiagridOnSurface:218`, `makePointCurve:72`, `makeCVCurve:53` | native evaluated geometry; dimensional default resolution. **Knots and weights unchanged** | 09.1 / 09.3 |
| `scripts/facade_tables.py` | `read_spec:667`, `read_downstream:736`, `build_grids:1081`, `build_registry:1872`, `render_csv:2136`, `guard_existing_grids:3572` | consistent envelope compatibility. **Canonical tables are not scaled**; no geometry conversion here | 08.2 |
| `scripts/place_components.py` | `UPSTREAM_NAMES:228`, `main:2340`, `build_placements:951`, `build_opening_cuts:1001`, `build_wall_cells:869`, `build_assembly:1221`, `prototype_sizes:1290` | the real four inputs made explicit; canonical computation; a narrow approved wall contract | 08.3 / 11.4 |
| `scripts/place_components.py` | `render_ms:1328`, `_check_script_shape:2186`, `_check_wall_tiling:2064`, `write_bytes` | boundary lengths, no modifiers, cm³ policy, receipt/write safety | 08.3 / 08.4 / 11.3 |

### 7.1 Proposed new files — none of them exists

| Proposed file | Proposed symbols | Narrow future work | Owning phase |
|---|---|---|---|
| `scripts/scene_units.py` | `unit_factor`, `scene_length_expr`, `scene_point_expr`, `emit_unit_preamble` | shared **emission text** and dimensional classification; no live connection | 07.1 |
| `scripts/curve_gen.py` | `generator_points`, `validate_generator`, `chord_bound`, `suggest_count` | pure stdlib math with a documented bound; the sampled diagnostic stays separate | 05.1 / 05.2 |
| `scripts/expand_curves.py` | `main`, `read_draft`, `expand`, `check`, `suggest` | authoring CLI, provenance, guarded draft output | 05.3 / 05.4 |
| `scripts/qa_check.py` | `main`, `emit_request`, `parse_capture`, `assess`, `resolve_reference`, `distance_to_arc` | two offline modes, a strict denominator, an independent oracle, reports | 10.3–10.6 |
| `references/_form-units-qa-design.md` | **this file** | the full freeze: fields, API ownership, G IDs | 01.3 (now) |
| `references/_form-generators-evidence.md` | future executed transcripts | shape/units/serialization/domain/receipt certification; may be split | 12.3 / 13.3 |
| `agents/max-qa.md` | the S7 contract | emit → sequential MCP collect → assess; read-only delivery | 10.7 |
| `specs/recipes/nurbs/barrel-vault-generated.json` | draft template | template `spec` = filename stem; instantiate a coherent project before building | 06.3 |
| `specs/fixtures/form-precision/` | a coherent defined QA example | the §12 example; placement subject to approval; no runtime reports in shipped specs | 06.4 |

Do not create dozens of empty helper modules. A shared QA helper is admissible only after the
ownership map itself is changed.

### 7.2 Invariant ID allocation

**The next free invariant ID is `G-84`.** It is allocated **centrally and sequentially, never by
parallel authors.** `PROPOSED` allocation only:

| ID | Subject |
|---|---|
| `G-84` | generator schema |
| `G-85` | expansion |
| `G-86` | reference / join |
| `G-87` | QA config |
| `G-88` | coverage joins |
| `G-89` | tolerances / schedule |
| `G-90` | dependencies / provenance |

`G-42`, `G-49`, `G-3`, `G-15` and `G-31` are **extended by meaning, not duplicated**. Optional
rings/mouldings get their IDs only after their block is approved. The runtime QA-V1 registry is a
**separate** registry: the static validator never observes Max and never assigns a live PASS.

---

## 8. Dimensional-sink checklist for future patch review

Run this list against **every** patch that touches an emitter or the library. Audit source locations
are given; re-read the actual symbols before editing.

- `build_spec.render_ms`: `Box` `width`/`length`/`height` and `pos` (`scripts/build_spec.py:1237`);
  `grouping.parent_pivot_cm`; a `Dummy`'s physical size **only** under an approved explicit contract.
- `build_nurbs.section_literal`: **every** point3 (`scripts/build_nurbs.py:1839`).
- `build_nurbs.dependent_surface_lines`: `set.merge` and the rail/trim points, through one shared
  boundary (`scripts/build_nurbs.py:1937`).
- `build_nurbs.render_ms`: `u_loft` thickness, grid merge, post-commit merge, `space_frame`
  thickness (`scripts/build_nurbs.py:2049`).
- `build_nurbs.tessellation_line`: `merge_tol_cm` (`scripts/build_nurbs.py:1850`).
- `createULoftShell` / `createUVLoftNetwork`: the **initial** `set.merge` and the initial
  `applyArchTessellation` settings, not only the later application
  (`snippets/nurbs_arch_library.ms:104`, `:128`).
- `makePointSurfaceGrid` / `makeCVSurfaceGrid`: the nested approximation receives an **explicit**
  merge (`snippets/nurbs_arch_library.ms:272`, `:293`).
- `createDiagridOnSurface`: thickness is physical (`snippets/nurbs_arch_library.ms:218`).
- `place_components.render_ms`: `PROTO` box sizes, `PLC` position after the canonical base-Z
  arithmetic, `WAL` box sizes and base positions (`scripts/place_components.py:1328`).

**Not length sinks.** These must not be scaled by a dimensional patch, and scaling them is a defect:

> Derived/derivative evaluated points · knot fractions · `p_vec` direction · seed domain coordinates
> · tension · rotations · `SCATTER_DENSITY` · counts · densities · unitless ratios.

`q` / `_round_tree` / `num` / `prototype_sizes` / the CSV builders / `self_check` stay canonical.
**No recursive conversion and no unrelated defaults cleanup** rides along with a dimensional patch.

---

## 9. Fault-injection obligations

The condensed matrix from `plan §11`. Mutations happen only in owned temporary copies and evidence
fixtures. Each row carries a known-good control and an exact observed message, exit code or check ID.

**Two rules, both mandatory:**

1. **At least two independent bad mutations per new G predicate.** One bad case is not a test.
2. **Never quote a refusal string before it has been observed.** The table below states *policy
   expectation*. The real transcript is filled in **after** execution, by the owner who ran it.
   Fabricating expected wording is itself a fault.

| ID | Mutation / case | Mandatory expectation (policy, not observed text) | Owning phase |
|---|---|---|---|
| M01 | missing/unknown `SystemType`; scale 0 / NaN / negative | refusal **before** any mutation | 07 / 08 |
| M02 | correct mm but ignored `SystemScale`; wrong `c`/`f` | physical measurement failure | 12 |
| M03 | same system tuple, changed display labels | geometry unchanged; metadata alone never changes a verdict | 03 / 12 |
| M04 | units changed between stages/batches; stale receipt | INVALID / INCOMPLETE run, no partial PASS | 07 / 10 |
| M05 | a cm² threshold used for cm³; an area power used for volume | dimensional-policy rejection | 10 / 11 |
| M06 | tolerance 0 then a hidden `or .5`; arithmetic reused as form | illegal fallback / policy rejected | 04 / 10 |
| M07 | shell 0, and below / equal / above 0.001 cm, in native m and mm | census and geometry consistent with the **frozen** rule | 09 / 12 |
| M08 | missing initial merge/default forwarding; only a late setter | a seam/approximation negative detects the physical effect | 09 |
| M09 | count 1, count `true`, wrong plane, radius ≤ 0 | `G-84` fails with an exact reason | 05 / 06 |
| M10 | angle delta 0 or > 360; wrong kind-specific radius keys | `G-84` fails | 05 / 06 |
| M11 | full-360 with count 2 or 3; rounded adjacent duplicate or zero chord | degeneracy refused, no division by zero | 05 |
| M12 | a point shifted by 1 cm; stored count mismatch | `G-85` fails | 06 |
| M13 | generator **and** points changed, dimensions reference fixed | `G-86` reference-join fails | 06 |
| M14 | unequal lattice counts; independently valid sweep counts | the first fails `G-42`, the second stays valid | 06 |
| M15 | a new feature declared as 1.0; an unsupported future version | version/feature refusal; a known 1.1 does not WARN | 04 |
| M16 | missing/mismatched origin or reference; circular authority | `G-86` / `G-90` fail | 04 / 10 |
| M17 | a required check removed/disabled; no analytic targets | `G-88`/profile fails — structure must not masquerade as form | 10 |
| M18 | legacy result fields inside the config; wrong key or container | `G-87` fails; an empty scaffold is not a PASS | 10 |
| M19 | bad physical tolerance or sample bounds; bad dependency | `G-89` / `G-90` fail | 10 |
| M20 | a P8 recheck against P7/P9 rechecks | P8 accepted, P7/P9 rejected | 10 |
| M21 | zero observations/compares; a missing, extra or duplicated sample | exact ID-denominator failure, no zip truncation | 10 |
| M22 | equal counts but substituted IDs; a duplicate node name | identity/coverage ERROR, never a nearest-name join | 10 / 12 |
| M23 | `success=true` plus a sentinel or error; timeout or missing END | batch ERROR / INCOMPLETE | 10 / 12 |
| M24 | undefined `evalPos`, non-finite, bool-as-numeric, a defaulted zero | explicit error, never a zero vector | 10 |
| M25 | wrong project, hash, request, run, frame or session | binding failure | 10 |
| M26 | double world transform, double normalisation, double derivative scaling | wrong-space / physical measurement failure | 09 / 12 |
| M27 | a pick offset instead of the design base; domain `[0,1]` assumed | role/domain failure and an observed form error | 12 |
| M28 | wrong half-ellipse, wrong infinite span, an oracle derived from the same points | finite reference/span/control failure | 10 / 12 |
| M29 | one sample above tolerance while the mean is low; solver exhausted | FAIL / INCOMPLETE — never a mean-based PASS | 10 |
| M30 | missing, moved or rotated panel; an ordinary copy | actual census/placement/`baseObject` failure | 12 |
| M31 | wall gaps and overlaps that cancel in volume; insufficient thickness | occupancy and full-thickness FAIL even when the totals match | 11 / 12 |
| M32 | a full visible host fills the opening while the cell table is correct | required WALLS FAIL; after the approved host correction, PASS | 11 |
| M33 | a foreign node or name collision; arbitrary cleanup | safe refusal and a foreign report; the fixture node survives | 03 / 12 |
| M34 | a differing output destination; a JSON+MS write interrupted, including the NURBS same-path draft input | refusal/recovery; the input and the prior complete pair stay intact | 05 / 08 / 09.6 |
| M35 | a stale library definition is loaded; an unsupported capability | the tested revision guard refuses or reloads the approved route | 09 |
| M36 | a fake replay or a scatter PASS derived from a single count snapshot | required replay is incomplete; optional scatter makes no determinism claim | 10 / 12 |
| M37 | an optional moulding with an open/inverted mesh or an invalid corner | MOULD topology/volume failure — **only if phase 16 is enabled**; not core | 16 |

---

## 10. Open questions that block phase 02

**Historical phase-01 question list:** 02.1 addresses paths/volume grammar; 02.2's §§14–19 address
wire/closed/shell/frame policies and define calibration gates. Current dispositions are in §19.1;
inventory/ownership/location questions remain 02.3. No A-* approval or phase-02 PASS is implied.

A later agent must **not guess** any of these. Each one either becomes an approval in section 4 or a
frozen field in phase 02. If a patch needs one and no record exists, the patch stops.

1. **Exact wire escaping, scalar precision and locale** for MAXScript results carried into a QA
   request. Without it, a hash cannot be reproduced.
2. **The exact protocol enums** a request, run-context, receipt or report must carry.
3. **Hash inclusion and exclusion rules** — precisely which bytes go into a hash and which are
   explicitly excluded. A script cannot know the SHA-256 of its own bytes without a contract.
4. **Cross-file path grammar** — how a dependency path is written, resolved and constrained to stay
   inside the project. A file-qualified reference resolver is **not** an existing legacy mechanism.
5. **The closed-360 consumer** — whether a full-circle row is permitted at all, the exact seam, the
   minimum distinct point count, and the 0.001 cm equality rule.
6. **The shell equality policy** — the source-observed contradiction between the emitter's strict `>`
   and `G-47`'s admitting `<` (`scripts/build_nurbs.py:568` vs `scripts/validate_specs.py:6725`).
7. **The frame field name and its units** in the request, and in every batch.
8. **The volume cm³ budget form** — the source-observed cm³-against-cm² comparison in `G-82`
   (`scripts/validate_specs.py:12078`) needs a dimension-correct replacement.
9. **Whether massing's `rect_of` limitation survives to a mesh phase.** Today the emitter is
   `Box`-only and refuses what it cannot describe (`scripts/build_spec.py:510`).
10. **The shape of the contextual stage-aware inventory API.** No approved API or CLI exists; the
    flag must not be guessed.

Two further items are design-only and grant no permission: the general intent/per-level footprint
programme, and mouldings.

---

## Provenance of the phase-01 text

Written as microtask **01.3**, whose scope was this file and nothing else. Its only sources were
`AGENT_PLAN_form_precision.md` (sections 1, 2, 3, 5, 6, 8, 9, 10-phase-01, 11, 14), `AGENTS.md`,
and read-only inspection of `scripts/*.py` and `snippets/nurbs_arch_library.ms` for the
`SOURCE-OBSERVED` rows. **No script was executed, no builder or validator was run, no Max or MCP
call was made, no git operation was performed, and no other file was modified.**

`source-observed` in the root plan is not automatically a shipped contract here: the row asserting
that `0.5 cm` was mislabelled as "half millimetre" (`plan §3`) was **not locatable** in
`CHECKPOINT.md` or `AGENTS.md` during phase 01.2, and no source line supports it. `0.5 cm` is
declared as the linear tolerance (`CHECKPOINT.md:566`); the "5 mm" reading is plain arithmetic, not
a document claim. It is therefore recorded here as `plan §3`, not as source-observed.

---

## 11. PROPOSED compatibility, envelope and provenance — 02.1

**Navigation:** §11.1 versions → §11.2 envelope → §11.3 joins/origins → §11.4 raw input;
§12 leaf inventory → §13 budgets, pending choices and local gate.
This is **one design-only proposal**, requiring **A-VERSION, A-FIELDS and A-TOL** as applicable.
Continuation of design work is not acceptance of any A-* row. All ten remain **OPEN**.
The phase-02 FREEZE requires 02.2, 02.3 and explicit approval **02.4**; code is still prohibited.

Table conventions throughout §§11–13:

- Every normative choice below is **PROPOSED**. Status `P-V`, `P-F`, `P-T` means respectively
  **PROPOSED / A-VERSION**, **PROPOSED / A-FIELDS**, **PROPOSED / A-TOL**; combinations require
  all named approvals. `PENDING Uxx` additionally blocks freeze; it is not an executable value.
- `R/—` = required, no default; `C/—` = required under the stated condition, otherwise forbidden;
  `O/absent` = optional, no implicit value. `draft`/empty scaffold recommendations are expressly
  draft authoring choices, not accepted build inputs. Missing and null are different: null is
  forbidden on all listed leaves. Unknown keys in the **new** objects are refused.
- `number` means finite JSON number **excluding bool**; `integer` means a JSON integer token,
  not a bool, decimal or exponent token (`2.0`/`2e0` are not count integers). Arrays of scalars or
  coordinates count as **one leaf family**, following legacy G-9;
  tables state their exact item types and arities. Object/array-of-object containers are specified
  separately and do not add scalar leaf families. `[]`/`{path}` are documentation notation only.
- Origins: `E` envelope exemption; `V` enumerated vocabulary/policy exemption; `I` identity/index
  exemption; `S1` source given/assumed/conflict with ledger where required, or a recomputable
  conversion from raw evidence; `D` derived with resolvable inputs; `Q` QA-owner physical/operational choice,
  given if explicitly supplied, assumed with an A-nnn ledger otherwise. Exemption is **not** a
  fake derived formula. Numeric operational choices are never exempt just because called policy.
- Consumer names describe **future responsibilities**, not implemented scripts. Existing source
  behaviour is identified separately below. All paths in tables are relative to their named file.

### 11.1 PROPOSED version and per-file compatibility matrix

**PROPOSED / A-VERSION:** accept exactly the two strings **`"1.0"` and `"1.1"`**. Recommend
**refusing patch spellings**, including `1.0.0` and `1.1.0`, rather than treating them as aliases;
also refuse `01.1`, whitespace, `1.2`, `1.1.1`, `2.0` and nonstrings. This exact-spelling choice
needs user approval: current grammar allows optional patches, and no present code enforces this
proposal. An owner may explicitly migrate a patch-spelled file after review; a reader never rewrites it.

| File / interface | PROPOSED 1.0 | PROPOSED 1.1 | Compatibility / gate (A-VERSION + A-FIELDS) |
|---|---|---|---|
| `dimensions.json` | Existing value tree / tolerances / origins | Existing tree plus optional `form_references`, `precision_targets`, `raw_source_values` | Presence of any new key under 1.0 FAILs, even if empty; form profile requires populated locked references/targets |
| `nurbs.json` | Existing sections with explicit `points_cm` | Same primitive plus optional generator/reference/station metadata | New keys under 1.0 FAIL; legacy point-only sections remain valid under either version |
| `massing.json`, `facade_grids.json`, `components_registry.json`, `assembly.json` | Existing per-file grammar | Same geometry grammar; compatible metadata preservation | 1.1 alone grants no new primitive, formula, modifier or field |
| `conflicts_resolved.json`, `assumptions.json` | Existing ledgers | Existing ledgers; approved qualified paths can name 1.1 fields and QA | Legacy bare ledger paths still mean dimensions; proposed P8 recheck extension needs future owner implementation |
| `qa.json` | Historical reserved/result-ish stub only | Defined configuration in §12.4–§12.8 | A 1.0 stub is not an executable QA plan; 1.1 config is not a results migration |
| `materials.json`, `export.json` | Historical reserved stubs | Envelope-readable reserved stubs only | No revived P7/P9 work; not required core build/QA dependencies |
| `world_table.csv` | Existing header/data contract | Identical CSV contract | No JSON version/envelope; explicit CSV dependency binds its JSON producers and joins |

**PROPOSED mixed-project positive:** dimensions 1.1 + NURBS 1.1 + massing/registry/assembly 1.0
+ QA 1.1 is compatible if each individual file passes its own grammar, units, project, status and
dependency version joins. Geometry entirely 1.0 + defined QA 1.1 can run a structural profile;
it cannot acquire analytical authority by relabelling QA. A **known 1.1 is not WARN** (including
warnings-as-errors). Unknown required versions are refusal, not tolerated drift.

**SOURCE-OBSERVED distinction:** `check_envelope` at `validate_specs.py:1590–1612` checks the major,
then WARNs on minor/patch drift. Builders' major-only checks and hardcoded 1.0 writers are recorded
in §5.2. None constitutes an exact-version implementation or support certificate for 1.1.

**PROPOSED writer rule:** same-document normalisation/expansion preserves the exact accepted
`schema_version`, `spec`, `project`, `units`, `source` and `status`, plus applicable origins and
generator/join metadata. It cannot downgrade 1.1 to 1.0, silently strip new metadata, restamp
`recorded_at` or auto-lock a draft. A newly computed *different* spec owns its appropriate
`source.kind=derived`/`source.reference`; it does not blindly copy an upstream source block.
Only the explicit document owner may migrate version/lifecycle/source metadata after comparison;
publication/transaction permissions remain **A-WRITE/A-OWNERS, pending 02.3**. Unsupported
metadata is a refusal or an owner migration question, never silent loss.

**PROPOSED stage policy:** missing legacy QA at S1–S5 / old examples gives QA **NOT_EVALUATED**
and the relevant unavailable static QA predicate **SKIP**, not a global mandatory failure.
P8 needs a **defined 1.1, locked, populated and structurally valid** configuration; missing,
reserved, empty, draft or superseded QA blocks assessment. Fresh and seeded scaffolds both need
an explicitly authored **draft config without a verdict**, with missing analytical-authority
tasks; neither earns a model verdict. A filled draft may undergo static structure review only.
Do not mechanically rename legacy `checks`/`captures`/`verdict` stubs into a plan or invent refs from
copied points. Run results stay outside pipeline discovery. Contextual inventory mechanism is U20.

### 11.2 Envelope leaf table

Containers: each spec is an object; first six keys remain, in order, `schema_version`, `spec`,
`project`, `units`, `source`, `status`. `units` remains an object with `length` and `angle`;
`source` remains an object with `kind`, `reference`, `recorded_at`, and the existing optional
`supersedes` only when a lifecycle replacement calls for it (`07-spec-grammar.md:107–110`).
No source URI/type/hash replacement is introduced. Existing unrelated metadata is not deleted by
this design; extending accepted metadata needs its own owner review.

| Path | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `schema_version` | string | R/— | — | Exact 1.0 or 1.1; §11.1 feature gates | Every loader/writer | E | P-V |
| `spec` | string | R/— | — | Exact JSON filename stem; no path | Loader/inventory | E | P-F |
| `project` | string | R/— | — | `^[a-z0-9][a-z0-9._-]*$`; identical across project inputs | Every loader/join | E | P-F |
| `units.length` | string | R/— | unit label | Exact `cm`; not display/system units | Canonical readers | E | P-F |
| `units.angle` | string | R/— | unit label | Exact `deg` | Canonical readers | E | P-F |
| `source.kind` | string | R/— | — | `user_brief`, `drawing`, `image`, `imported`, `assumed`, `derived` | Input/provenance | E | P-F |
| `source.reference` | string | R/— | — | Nonempty free text citing artifact/message; derived cites existing input spec file(s); not a resolver/hash | Input/provenance | E | P-F |
| `source.recorded_at` | string | R/— | ISO-8601 datetime | Preserve captured datetime; only spec clock; no generated run clocks here | Input/writer | E | P-F |
| `source.supersedes` | string | C/— | — | Replacement only; existing `<old spec name>@<version>` spelling; explicit owner lifecycle, not automatic version change | Lifecycle owner | E | P-V/F |
| `status` | string | R/—; scaffold proposes `draft` | — | `draft`, `locked`, `superseded`; build/P8 requires locked; absence never auto-locks | Stage gates | E | P-F |

### 11.3 PROPOSED path, identity and origin grammar

**A-FIELDS proposal; no resolver is claimed implemented.** Keep three distinct grammars:

1. **Local provenance/value path:** a nonempty dotted sequence of member names matching
   `[A-Za-z_][A-Za-z0-9_]*`, each followed by zero or more indices `[0]` or `[1-9][0-9]*`.
   Dots separate members, not indices: `sections[0].generator.semi_axes_cm` is valid;
   `sections.[0]`, negative/leading-zero indices, `[]`, wildcards, quoted keys, expressions and
   trailing dots are invalid. Every member/index must actually exist. Numeric-array provenance
   covers the array leaf as a whole, not separate x/y/z entries. An object-element origin may
   collapse its descendants only if all nonexempt leaves share that origin; overlapping coverage
   is forbidden. Origins **map keys remain local**. No change to legacy granularity is implied.
2. **Qualified provenance/value path:** `<known-spec-filename>.json:<local-path>` with exactly
   one colon, e.g. `dimensions.json:form_references[0].semi_axes_cm`. The named spec must be
   present in this project. Use this for **all new cross-file `derives_from` and ledger targets**.
   No drive/path/URI prefix, JSON Pointer, `::` or semantic-ID substitution. The bare ledger
   `field_path` still means `dimensions.json` per grammar §6.1.1. Existing bare `derives_from`
   and `origin_inputs` keep their existing file-specific allowed upstream hosts; they are not
   retrospectively interpreted as this new resolver. New same-file derives_from may be local;
   qualification removes cross-file ambiguity. Resolve cycles as failure; no downstream
   points→reference or QA→dimensions dependency is permitted as geometry authority.
3. **Source-ID selector (not a provenance path):** `<known-spec-filename>.json:<collection>:<id>`
   with exactly two colons. Collection is a single enumerated top-level array name; ID is an
   exact unique string in that array, never an index or a node pattern. Proposed new ID pattern
   `^[A-Za-z][A-Za-z0-9_-]{0,63}$`; existing source IDs retain their existing per-file patterns.
   `nurbs.json:surfaces:SUR-001` selects data, not a Max pointer. A `form_reference_ref`/
   `reference_ref` is instead the exact bare ID in this project's `dimensions.form_references`;
   a `target_ref` is the exact ID in `qa.scope.targets`. No fallback on name, nearest geometry,
   reordered array position, same-looking ID in another collection or wildcard is allowed.
   The one named-member exception, `massing.json:site_pad:<part>`, is specified in §12.3;
   its final token is a fixed part name, **not an invented site-pad ID**.

**PROPOSED dependency file paths:** nonempty project-root-relative POSIX paths; each segment
`[A-Za-z0-9_-][A-Za-z0-9._-]*`; reject empty / `.` / `..` segments, backslashes, absolute/drive/
UNC paths, colon, percent escapes and glob characters. Resolve through the filesystem and require
the result (including symlink/junction resolution) to stay inside the explicit project root.
Core JSON dependencies live at `specs/pipeline/<known-spec-filename>.json`; CSV at
`specs/pipeline/world_table.csv`. Alternative draft locations need 02.3 identity approval.
The filename qualifier in a provenance path is an inventory key, **not** an arbitrary file path.

Containers: `origins` is an object `{local_path: record}`; record has exactly the allowed leaves
below. `derives_from` is a nonempty array of strings. `origin_inputs` is an array of distinct
sorted **legacy bare dotted paths**, including in QA; it is compatibility metadata, never
dependency/hash authority. QA requires explicit JSON dependencies for new qualified inputs.

| Path | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `origin_inputs` | array of strings | R/— in downstream/QA; draft proposes `[]` | — | Actual legacy upstream paths; QA paths resolve in ≥1 declared defined JSON dependency; never CSV/hash input | Static compatibility review | Provenance metadata | P-F |
| `origins.{path}.origin` | string | R/— per record | — | `given`, `assumed`, `conflict`, `derived`; NURBS numeric leaves must be derived | Origin checker | Provenance metadata | P-F |
| `origins.{path}.origin_ref` | string | C/— | — | Required iff assumed/conflict; `A-[0-9]{3}` or `C-[0-9]{3}` respectively, existing ledger/value/path match; otherwise forbidden | Ledger pairing | Provenance metadata | P-F |
| `origins.{path}.derives_from` | array of strings | C/— | — | Required iff derived; ≥1 distinct actual local/qualified path; forbidden otherwise; no cycles | Recompute/join checker | Provenance metadata | P-F |
| `origins.{path}.conflict_ref` | string | O/absent | — | Existing `C-[0-9]{3}`; informational inherited conflict; not a replacement for origin_ref | Ledger trace | Provenance metadata | P-F |

**PROPOSED scoped exemptions:** envelope, origin metadata and existing id/name/index exemptions
remain. In the new tables `V` explicitly exempts kind, plane, role, requirement/profile IDs,
method/version IDs, structural collection/key names, units/dimension labels, fixed header/axis
vocabularies and capture attachment mode. Source/target selectors are structural joins validated
by existence and compatibility, not fake numeric derivations. Numeric `count`, station, angles,
coordinates, axes/radii, raw values, physical thresholds, sampling counts/frame, and operational
limits require origins. Empty arrays express absence, not numeric evidence.

**PROPOSED narrow QA exception:** legacy G-9 forbids origins inside `tolerances`
(`validate_specs.py:1901–1916`). Retain that for all 1.0 files and unchanged geometry tolerances.
For **defined QA 1.1 only**, extend coverage to numeric tolerance leaves in §12.4: arithmetic
copies are D, physical form choices Q, numerical bounds D from an approved calibration input or
Q with explicit ledger. QA policy-string leaves are V. This exception needs A-FIELDS/A-TOL and
future predicate changes; current validator cannot be claimed to accept it. Collapsing a mixed
QA tolerance object under one origin is invalid. Ordinary tolerance-copy rules are not weakened.
The D option for calibration budgets is **not a ready provenance route** until U18/U19 inventory
the exact approved calibration input and its qualified constant paths. Until then, the design
states an obligation, not a fictional dependency file. A Q bound still needs an explicit
QA-owner decision backed by calibration, with ledger if inferred; unsupported numbers cannot
be legitimised merely by writing origin=assumed. Raw evidence `value`/`unit` are deliberate
dimensional-registry exceptions to suffix lint, not authority to put mm inside an `_cm` leaf.

### 11.4 PROPOSED raw-input evidence and dimensional registry

Introduce **only in dimensions 1.1** `raw_source_values`: optional array of objects; each has
exactly `id`, `target_path`, `value`, `unit`, `source_reference`. S1 owns creation and preservation;
builders/expansion/QA read it. It is source evidence, not a replacement `source` envelope or a new
assumption ledger. Every converted field has exactly one selected raw record; the raw value is
kept **unrounded**, the canonical destination carries the conversion origin. If evidence records
conflict, S1 must resolve them with the existing ledger before conversion is authoritative.

| Path (dimensions) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `raw_source_values[].id` | string | R/— | — | New ID grammar §11.3; unique within evidence array | S1/evidence join | I | P-F |
| `raw_source_values[].target_path` | string | R/— | — | Actual local dimensions scalar/coordinate-array leaf registered below; no envelope/raw/QA target, unique selected destination | Normaliser/recompute | Structural join exemption | P-F |
| `raw_source_values[].value` | number or numeric array | R/— | As `unit` | Finite nonbool; same scalar/array shape as destination; no q6 on evidence; range checked after normalisation | S1 normaliser | Given raw evidence; inferred unit needs ledger | P-F |
| `raw_source_values[].unit` | string | R/— | unit label | Explicit `mm`, `cm`, `mm2`, `cm2`, `m2`, `mm3`, `cm3`, `deg`, `unitless`; must match registered quantity | Dimensional registry | Given source label; never guessed from display | P-F |
| `raw_source_values[].source_reference` | string | R/— | — | Nonempty document/sheet/dimension/message locator; original evidence retained | S1 audit | Given evidence | P-F |

**PROPOSED registry, exact for new 02.1 numeric fields:** form-reference `center_cm`, `radius_cm`,
`semi_axes_cm`, `longitudinal_range_cm`, section `station_cm`, generator center/radii/axes,
section `points_cm`, QA `linear_cm`, `surface_deviation_cm`, `longitudinal_extent_cm`,
`landmark_deviation_cm`, `solver_distance_cm`, `wire_length_cm` are lengths (cm).
`from_deg`, `to_deg`, `angle_deg`, `wire_angle_deg` are degrees; counts/frame/limits with count units are integers;
`unit_factor_relative` is dimensionless; `area_m2` is area (m²);
`volume_roundoff_cm3` is volume (cm³); time budgets are seconds and response cap bytes.
Only **source-owned dimensions destinations**, including existing registered dimensions fields,
may be targeted by raw evidence. Derived generator/points/QA fields are consumers, not alternative
raw-input destinations. New `construction_count` is unitless; it is not scaled.
This enumerated registry is extended explicitly for existing fields in future grammar work;
suffix guessing or recursive conversion of every number is prohibited.

**DESIGN known answers, not executed checks:** 1800 mm ÷ 10 = **180 cm**; 0.5 mm ÷ 10 =
**0.05 cm**, not 0.5 cm; 20000 mm = 2000 cm. Example raw record: ID `RAW-rise`,
target_path `form_references[0].semi_axes_cm`, value `[6000,1800]`, unit `mm`,
source_reference `drawing A-201, explicit semi-span/rise dimensions`; canonical array `[600,180]`.
Origin on `form_references[0].semi_axes_cm`: derived, derives_from
`raw_source_values[0].value` and `raw_source_values[0].unit`; conversion rule is registered
length-mm→cm division by 10, not arbitrary formula text. Unit is accepted as given only if explicit.
An inferred unit requires its own assumed origin and A-nnn ledger; an unresolved unit conflict
blocks normalisation. Already-canonical `_cm` output is never divided again.

Registry conversions: length mm→cm `/10`; area mm²→cm² `/100`, mm²→m² `/1000000`,
cm²→m² `/10000`; volume mm³→cm³ `/1000`; identity for the declared canonical unit;
angles/unitless values unchanged. Vector/matrix-shaped coordinate arrays convert **all declared
length components** and preserve shape. q6 applies to canonical geometry, not raw evidence or a
runtime unit factor. The plan's proposed raw 12000/1800/4000 mm span/rise/springing case becomes
1200/180/400 cm; span is not silently reinterpreted as semi-axis (a=600 follows span/2).

---

## 12. PROPOSED form, generator and QA leaf inventory

All choices in this section require **A-FIELDS**, plus A-VERSION/A-TOL where indicated. No API
name, arbitrary source formula, measured result or authority inferred from sampled points lives
in these objects. This section inventories every proposed leaf family **within 02.1**; pending
02.2/02.3 semantics are enumerated in §13.3, not supplied as plausible defaults.

### 12.1 dimensions: reference and precision-target leaves

Containers: `form_references` and `precision_targets` are optional arrays of objects in 1.1;
for the form profile both are required and nonempty. Each object is closed to its per-kind key
set. New `construction_count` is an explicit **PROPOSED source-owned authoring parameter** for
arc/ellipse section discretisation, not a geometric radius or a QA accuracy certificate. It is
needed so generator.count has an upstream origin rather than an invented G-49 exemption.

| Path (dimensions) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `form_references[].id` | string | R/— | — | §11.3 new ID grammar, unique in references | Expansion/QA joins | I | P-F |
| `form_references[].kind` | string | R/— | — | Exactly `arc`, `ellipse_arc`, `semi_elliptical_barrel` | Oracle/expansion | V | P-F |
| `form_references[].plane` | string | R/— | — | XY/XZ/YZ for arcs; barrel XZ only | Frame mapping | V | P-F |
| `form_references[].center_cm` | array of 3 numbers | R/— | cm | Finite world center; barrel center.y exactly 0; §12.2 frame rule | Oracle/expansion | S1 | P-F |
| `form_references[].radius_cm` | number | C/— | cm | >0; arc only | Circle oracle/expansion | S1 | P-F |
| `form_references[].semi_axes_cm` | array of 2 numbers | C/— | cm | Both >0; `[a,b]` along e1/e2; ellipse_arc or barrel only | Ellipse oracle/expansion | S1 | P-F |
| `form_references[].from_deg` | number | R/— | deg | Finite; 0<abs(to−from)≤360; barrel 0 or 180 with opposite endpoint | Oracle/expansion | S1 | P-F; closed U01 |
| `form_references[].to_deg` | number | R/— | deg | Finite; oriented unwrapped interval, no modulo rewrite; barrel 180 or 0 | Oracle/expansion | S1 | P-F; closed U01 |
| `form_references[].longitudinal_range_cm` | array of 2 numbers | C/— | cm | Barrel only, world Y endpoints `[s0,s1]`, s1>s0 | Finite-span oracle | S1 | P-F |
| `form_references[].construction_count` | integer | C/— | count | Arc/ellipse only; nonbool 2..500; closed/degen rules still apply | Generator.count source | S1 operational authoring choice | P-F; U01 |
| `precision_targets[].id` | string | R/— | — | §11.3 new ID grammar, unique in targets; equals corresponding QA scope ID | Required-registry coverage | I | P-F |
| `precision_targets[].source_ref` | string | R/— | — | Source-ID selector §11.3; v1 analytical target must select `nurbs.json:surfaces:<id>` | S1→NURBS→QA join | Structural join exemption | P-F |
| `precision_targets[].reference_ref` | string | R/— | — | Exact existing form-reference ID; v1 surface target is barrel; arcs remain section references | Independent oracle join | Structural join exemption | P-F |
| `precision_targets[].role` | string | R/— | — | Exact `design_surface`; never offset shell/copy/derived mesh | Surface-role resolver | V | P-F; U16 |
| `precision_targets[].requirement_profile` | string | R/— | — | Exact `form_precision_v1`; no structural downgrade | Mandatory QA inference | V | P-F |

**PROPOSED per-kind allowed/forbidden keys (A-FIELDS):**

| Object kind | Exact allowed required keys | Forbidden keys |
|---|---|---|
| Reference `arc` | id, kind, plane, center_cm, radius_cm, from_deg, to_deg, construction_count | semi_axes_cm, longitudinal_range_cm and every unlisted key |
| Reference `ellipse_arc` | id, kind, plane, center_cm, semi_axes_cm, from_deg, to_deg, construction_count | radius_cm, longitudinal_range_cm and every unlisted key |
| Reference `semi_elliptical_barrel` | id, kind, plane, center_cm, semi_axes_cm, from_deg, to_deg, longitudinal_range_cm | radius_cm, construction_count, span/rise aliases, rotation/axis/formula fields and every unlisted key |
| Generator `arc` | kind, plane, center_cm, radius_cm, from_deg, to_deg, count | semi_axes_cm, longitudinal_range_cm, id, construction_count and every unlisted key |
| Generator `ellipse_arc` | kind, plane, center_cm, semi_axes_cm, from_deg, to_deg, count | radius_cm, longitudinal_range_cm, id, construction_count and every unlisted key |

The barrel is an independent finite surface reference, **not a generator kind**. Its sectional
arc/ellipse references must have the same transverse center/axes/angles at the stated station.
For equal barrel semi-axes an `arc` section reference may use radius=a=b; otherwise an
`ellipse_arc` is required. No missing radius/axis is filled from the other kind.

### 12.2 PROPOSED frames, section joins and generation

The frame table is fixed vocabulary, not user numeric origins and not a guessed cross product:

| Plane | e1 | e2 | Station/orthogonal coordinate | Positive orientation |
|---|---|---|---|---|
| XY | +X | +Y | Z | t=0 at +X, t=90° at +Y |
| XZ | +X | +Z | Y | t=0 at +X, t=90° at +Z |
| YZ | +Y | +Z | X | t=0 at +Y, t=90° at +Z |

**PROPOSED barrel v1:** XZ transverse profile, +Y longitudinal direction, center `[cx,0,cz]`,
world endpoint range `[s0,s1]`; no center-Y offset is added. Points on the ideal barrel are
`[cx+a cos(t), s, cz+b sin(t)]`, s∈[s0,s1], t between **0↔180 degrees**, upper half in
either traversal order. Span=2a, rise=b, springing=cz are derived meanings, not stored aliases.
No arbitrary rotation, taper, lower half or XY/YZ barrel is in this proposal.

For an arc/ellipse section, station_cm is the world orthogonal coordinate from the frame table;
it must **equal** that component of the source reference's center. The generator copies this
world center unchanged. Station does not add a translation to it. For a barrel's referenced
surface all its participating transverse profile sections join XZ arc/ellipse references, share
cx/cz/axes/oriented endpoints, and have s0≤station≤s1; first/last profile stations equal s0/s1.
Transverse profile sections are ordered by strictly increasing world station (+Y); at least two
distinct stations are required. Consumer-specific longitudinal/rail curves are checked separately.
Rail rows/UV longitudinal curves keep their separate legacy meanings; no blanket semicircle
rule is applied to them. Geometry reference values match exactly after canonicalisation;
legacy arithmetic 0.5 cm cannot legitimise a shifted generator. Derived station source can be
the qualified reference center array; fixed component selection comes from this frame policy.

Containers: existing `sections` is an array of objects, retaining `id`, optional `name` and
`points_cm`. Add optional `generator` object (closed per kind), `form_reference_ref` and
`station_cm`; **the three new keys must appear together**. For an expansion input draft,
points_cm may be absent only in the authoring input, not in build/QA-ready NURBS. This does not
introduce a generator primitive to the builder or a per-section `closed` flag.

| Path (nurbs) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `sections[].id` | string | R/— | — | Preserve existing `SEC-[0-9]{3}`, unique/ascending | Section/surface joins | I | P-F |
| `sections[].name` | string | O/legacy naming | — | Preserve existing unique/no-dash curve-name rule; no new name default | NURBS builder | Existing name exemption | P-F |
| `sections[].form_reference_ref` | string | C/— | — | Exact arc/ellipse ID in dimensions; not barrel, source points or node name | Expansion/static join | Structural join exemption | P-F |
| `sections[].station_cm` | number | C/— | cm | Equals reference center's orthogonal component; barrel profile station within world range | Expansion/extent check | D from qualified reference center | P-F |
| `sections[].generator.kind` | string | C/— | — | `arc` or `ellipse_arc`, equals source kind | Expansion/static join | V, plus exact join | P-F |
| `sections[].generator.plane` | string | C/— | — | XY/XZ/YZ, equals source plane | Frame mapping | V, plus exact join | P-F |
| `sections[].generator.center_cm` | array of 3 numbers | C/— | cm | Finite; exactly source world center, no station double-add | Expansion/static join | D from dimensions reference | P-F |
| `sections[].generator.radius_cm` | number | C/— | cm | Arc only, >0, exactly source radius | Expansion/static join | D from dimensions reference | P-F |
| `sections[].generator.semi_axes_cm` | array of 2 numbers | C/— | cm | Ellipse only, both >0, exactly source axes | Expansion/static join | D from dimensions reference | P-F |
| `sections[].generator.from_deg` | number | C/— | deg | Finite, exact source endpoint; valid oriented delta | Expansion/static join | D from dimensions reference | P-F; U01 |
| `sections[].generator.to_deg` | number | C/— | deg | Finite, exact source endpoint; valid oriented delta | Expansion/static join | D from dimensions reference | P-F; U01 |
| `sections[].generator.count` | integer | C/— | count | Nonbool 2..500, exactly source construction_count; no silent suggestion adoption | Expansion/static join | D from dimensions construction_count | P-F; U01 |
| `sections[].points_cm` | array of arrays of 3 numbers | R/— at builder gate | cm | Generated n rows = count, finite nonbool; legacy ≥2 rows; q6/recompute/duplicate rules below | **Only builder geometric primitive** | D from local generator, or existing legacy derivation | P-F/T |

**PROPOSED exact generation:** t0=from_deg·π/180, t1=to_deg·π/180;
ti=t0+(t1−t0)·i/(n−1), i=0..n−1; Pi=C+a cos(ti)e1+b sin(ti)e2, with a=b=radius for
arc. Both endpoints included. Source geometry remains in dimensions; no points→kind→points
cycle can establish authority. Recompute independently from those parameters, not stored points.

Canonical coordinate output uses **q6(x)=round(x,6)**, nearest with ties-to-even as a mathematical
proposal; normalise either signed zero to JSON `0`. Reject NaN/Infinity, bool numeric values and
duplicate JSON keys; use strict UTF-8 JSON, not permissive NaN tokens. Six fractional decimal
places are a precision policy, not a required textual padding. Adjacent q6-equal points/zero
chords fail; overflow/nonfinite intermediate arithmetic fails. Full-360 count 2 is degenerate;
count 3 is not rescued by repeated endpoints. **No closed-360 consumer is accepted before U01 /
A-CLOSED**, so this text does not freeze a seam policy. Shell equality is likewise U02.
Expansion consistency ≤**0.001 cm** is a separately named PROPOSED consistency budget; it
does not certify a surface or relax the exact generator/reference parameter join. G-42 equal
counts remains limited to lattice/loft consumers; independently valid sweep sections may differ.

### 12.3 QA containers, profiles, scope and known checks

Defined `qa.json` 1.1 remains an object with the envelope, then exactly these proposed keys:
`tolerances`, `origin_inputs`, `origins`, `profile`, `dependencies`, `scope`, `check_plan`,
`sampling`, `limits`, `capture_plan`. **All are required containers/leaves**, even if an explicitly
draft scaffold uses empty arrays/maps. `tolerances` contains flat arithmetic leaves plus objects
`form`, `numerical`, `volume`; profile is a string; dependencies/check_plan/capture_plan are
arrays of objects; scope is an object with `targets` array and conditional registry_ref;
sampling/limits are objects. No open-ended nested settings or extension bags are proposed.

**PROPOSED configuration prohibition:** reject `measured`, `results`, `pass`, `verdict`, `error`,
`checks`, `captures`, `determinism`, `determinism_results`, `enabled`, `disabled` as object fields
anywhere in the new config value tree. Exact closed key sets also reject alternate result/disable
spellings. This does not ban words within free-text source/ledger evidence. There is no
check-disable boolean, nullable check or optional required-family flag.

**PROPOSED profiles:** `form_precision_v1` requires ≥1 analytical registry target and all its
inferred mandatory families. `legacy_structure_v1` permits structural measurement without
invented references, explicitly reporting **FORM NOT SPECIFIED**, never form_precision PASS.
No automatic profile downgrade. Existing locked analytical precision targets cannot be deleted
or omitted from dependencies/scope/check_plan to clear failure. A changed registry is an explicit
S1/QA-owner scope-change decision with retained prior binding (U21), not a QA workaround.

**PROPOSED target kinds / source collections:**

| Scope kind | Exact allowed source selector | Role vocabulary | Expected node expansion |
|---|---|---|---|
| `project` | `project` omitted source_ref, uses envelope identity | `project` | Empty names only; run-wide coverage/replay |
| `massing_element` | `massing.json:elements:<id>` excluding facade_wall, or `massing.json:site_pad:<part>` named-member selector | `delivered_solid` | Existing massing name mapping |
| `group` | `massing.json:grouping:<id>` | `group_parent` | Existing dummy mapping |
| `nurbs_surface` | `nurbs.json:surfaces:<id>` | `design_surface` | Existing surface name; committed subobject resolver U16 |
| `nurbs_derivative` | `nurbs.json:derivatives:<id>` | `derived_geometry` | Existing derivative name mapping; never analytical oracle |
| `component_prototype` | `components_registry.json:components:<id>` | `prototype` | Existing PROTO mapping |
| `placement` | `assembly.json:placements:<id>` | `instance` | Existing PLC mapping |
| `wall_host` | `massing.json:elements:<id>` whose kind is facade_wall | `wall_host` | Host mapping, active/reference representation pending A-CORRECT/U21 |
| `wall_cell` | `assembly.json:wall_cells:<id>` | `delivered_solid` | Existing WAL mapping |

The **sole source-selector exception** to §11.3's array rule is `massing.json:site_pad:<part>`:
part is exactly `ground_pad`, `paving` or `kerb`; require that named member to be a non-null
geometry object. Legacy site_pad has **no id** (`examples/massing.json:2184–2212`); never
fabricate one. The existing source name map is respectively `SP_GROUND_PAD`, `SP_PAVING`,
`SP_KERB` (`build_spec.py:198–202`). No scatter target/core
determinism claim, curve API string, mesh topology assumption or unnamed whole-scene scan is
added here. Known source class names belong in future measured evidence, not the config.

**PROPOSED known check vocabulary and joins:**

| kind | Allowed target kinds | Required reference / tolerance |
|---|---|---|
| `QA-V1-COVERAGE` | project | No reference; `exact` |
| `QA-V1-CENSUS` | Every non-project kind | No reference; `exact` |
| `QA-V1-NURBS-CENSUS` | nurbs_surface | No reference; `exact` |
| `QA-V1-PLACEMENT` | massing_element, group, component_prototype, placement, wall_cell | No reference; `placement_v1` bundle |
| `QA-V1-WALLS` | wall_host | No reference; `wall_box_v1` bundle |
| `QA-V1-FORM` | nurbs_surface with required registry entry | Registry barrel reference; `form_v1` bundle |
| `QA-V1-STACK` | placement, wall_cell, component_prototype | No reference; `exact` |
| `QA-V1-REPLAY` | project | No reference; `replay_v1` bundle; separate authorised rehearsal evidence |

These are **proposed runtime families**, not new static G allocations. QA inference derives the
mandatory set independently of configured rows: coverage/replay for project, census for every
owned target, NURBS census for every surface, placement for applicable modeled/placed objects,
walls for every applicable facade host, stack for scoped assembly outputs, form for every locked
precision target. One row per `(kind,target_ref)`; exact IDs/sets must agree. Removing a required
row yields missing-required failure, never a smaller successful denominator. Blend/trim design
role selection stays U16; no first/last-surface shortcut is approved. Existing historical trim
surface contribution zero remains relevant, not grounds for a phantom form target.
Exactly one project target is required. Every applicable emitted owned node must be represented
by one scope target; the same facade_wall cannot also be a massing_element target. Ancillary
roles within a NURBS node are resolved under its one surface target, not duplicated node rows.
The expected scope is inferred from source dependencies independently of scope.targets; deleting
a nonanalytical owned target cannot clear a missing census/placement obligation either.

### 12.4 QA tolerance leaves

No unconditional default is proposed for physical project values. `linear_cm`, `area_m2`,
`angle_deg` are copies of dimensions arithmetic tolerances; the added objects keep separate
quantity/consumer responsibilities. `form` is required for form profile and forbidden for
structure profile. `numerical`/`volume` are required in a complete QA plan, with the exact pending
calibration questions below; empty draft is not an executable contract.

| Path (qa) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `tolerances.linear_cm` | number | R/— | cm | ≥0, exact dimensions arithmetic copy; never surface threshold | Structural arithmetic | D from dimensions tolerances | P-F/T |
| `tolerances.area_m2` | number | R/— | m² | ≥0, exact dimensions arithmetic copy | Area arithmetic | D from dimensions tolerances | P-F/T |
| `tolerances.angle_deg` | number | R/— | deg | ≥0, exact dimensions arithmetic copy | Rotation arithmetic | D from dimensions tolerances | P-F/T |
| `tolerances.form.surface_deviation_cm` | number | C/— | cm | >0; recommendation **0.5 only as NEW physical choice**, never arithmetic inheritance | Max sampled nearest-distance gate | Q | P-F/T |
| `tolerances.form.longitudinal_extent_cm` | number | C/— | cm | ≥0, independent declared extent tolerance; zero meaningful; no default .5 | Finite-span extent gate | Q | P-F/T |
| `tolerances.form.landmark_deviation_cm` | number | C/— | cm | ≥0, independent declared landmark-position tolerance; zero meaningful | Required landmarks | Q | P-F/T |
| `tolerances.numerical.policy` | string | R/— | — | Exact proposed `separate_bounds_v1`; never geometric widening | Interval assessor | V | P-F/T |
| `tolerances.numerical.solver_distance_cm` | number | R/— | cm | >0, certified nearest-distance bracket width budget; value unresolved | Bounded oracle | D/Q with evidence | P-F/T; PENDING U03 |
| `tolerances.numerical.wire_length_cm` | number | R/— | cm | ≥0 certified serialization/readback length uncertainty; value unresolved | Evidence interval conversion | D/Q with evidence | P-F/T; PENDING U04 |
| `tolerances.numerical.wire_angle_deg` | number | R/— | deg | ≥0 certified serialization/readback angular uncertainty; not a length/factor budget | Rotation evidence interval | D/Q with evidence | P-F/T; PENDING U04 |
| `tolerances.numerical.unit_factor_relative` | number | R/— | ratio | ≥0 certified factor relative-error bound; magnitude-aware propagation; value unresolved | Native→cm interval | D/Q with evidence | P-F/T; PENDING U05 |
| `tolerances.numerical.volume_roundoff_cm3` | number | R/— | cm³ | ≥0 certified aggregate arithmetic/readback uncertainty; value unresolved | Volume numeric interval | D/Q with evidence | P-F/T; PENDING U06 |
| `tolerances.volume.policy` | string | R/— | — | Exact proposed `box_endpoint_propagation_v1`; no cm² threshold | Wall volume budget | V | P-F/T |
| `tolerances.volume.endpoint_tolerance_ref` | string | R/— | cm by referent | Exact local path `tolerances.linear_cm`; e is copied endpoint comparison budget, not solver noise | Box propagation §13.1 | Structural join exemption | P-F/T |

`placement_v1` = linear_cm + angle_deg (counts/links exact); `wall_box_v1` = linear_cm plus
volume propagation, exact occupancy/topology; `form_v1` = the three form leaves plus separate
numerical bounds; `replay_v1` = exact identity/count sets and relevant quantity tolerances;
`exact` = exact counts/IDs/links, not a hidden zero→default length tolerance. Bundles are closed
policy vocabulary, not untyped arbitrary paths; their field definitions still require approval.

### 12.5 QA dependencies — JSON and CSV are discriminated

`dependencies` is a nonempty array of closed objects with unique id/file. Common leaves id,
format and file; **format=json** adds exactly spec/schema_version; **format=csv** adds exactly
producer, columns, join and foreign_keys. `producer` and `join` are closed objects;
`foreign_keys` is an array of closed objects. JSON items forbid all CSV-only keys; CSV items
forbid spec/schema_version at item root. CSV's producer is JSON metadata, never a CSV envelope.
Actual SHA-256 is computed in emit/request, **not** a configurable dependency leaf.

**PROPOSED P8 core dependency set:** explicitly declare dimensions, massing, nurbs,
facade_grids, components_registry and assembly JSONs plus world_table.csv, even if an applicable
geometry array is empty. Declare assumptions/conflicts_resolved JSONs whenever an origin/ledger
join uses them. Source/form/scope/provenance resolution may only read these declared actual
inputs; discovering a missing dependency never silently fills the list. Removing a core input
cannot shrink expected model scope. Additional calibration-input binding is U18/U19, not a
fictional implemented JSON spec. P7/P9 stubs are not part of this mandatory set.

| Path (qa) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `dependencies[].id` | string | R/— | — | §11.3 new ID grammar; unique dependency ID | Request binding | I | P-F |
| `dependencies[].format` | string | R/— | — | Exactly `json` or `csv` discriminator | Dependency reader | V | P-F |
| `dependencies[].file` | string | R/— | — | Safe project-relative actual path §11.3; unique file; no guessed sibling | Dependency reader/hash input | Structural join exemption | P-F |
| `dependencies[].spec` | string | C/— | — | JSON only; actual envelope spec equals stem | JSON compatibility | Structural join exemption | P-F/V |
| `dependencies[].schema_version` | string | C/— | — | JSON only; exact accepted actual file version, not desired target | JSON compatibility | Structural join exemption | P-V/F |
| `dependencies[].producer.file` | string | C/— | — | CSV only; exact declared JSON dependency file for components_registry | CSV producer binding | Structural join exemption | P-F |
| `dependencies[].producer.spec` | string | C/— | — | CSV only; exact `components_registry`, actual JSON envelope | CSV producer binding | Structural join exemption | P-F |
| `dependencies[].producer.schema_version` | string | C/— | — | CSV only; actual producer version 1.0/1.1, equals its JSON dependency | CSV producer binding | Structural join exemption | P-V/F |
| `dependencies[].columns` | array of strings | C/— | labels with declared units | CSV only; exactly the ordered 17 WORLD_CSV_COLUMNS below; duplicates/extras fail | Strict CSV reader | V | P-F |
| `dependencies[].join.consumer_file` | string | C/— | — | CSV only; actual declared JSON dependency `specs/pipeline/assembly.json` | Placement/table bijection | Structural join exemption | P-F |
| `dependencies[].join.collection` | string | C/— | — | CSV only; exact `placements` | Placement/table bijection | V | P-F |
| `dependencies[].join.row_key` | string | C/— | — | CSV only; exact `source_row` in placement | Row bijection | V | P-F |
| `dependencies[].join.row_base` | integer | C/— | row index | CSV only; exactly 1, header excluded; fixed indexing rule, not measured count | Row bijection | I fixed protocol constant | P-F |
| `dependencies[].join.identity_column` | string | C/— | — | CSV only; exact `instance_id`, unique across data rows; not PLC id equality | CSV identity coverage | V | P-F |
| `dependencies[].foreign_keys[].csv_column` | string | C/— | — | CSV only; required columns/join tuples below | Referential integrity | V | P-F |
| `dependencies[].foreign_keys[].json_file` | string | C/— | — | CSV only; actual declared JSON dependency file | Referential integrity | Structural join exemption | P-F |
| `dependencies[].foreign_keys[].collection` | string | C/— | — | CSV only; exact array in named JSON file | Referential integrity | V | P-F |
| `dependencies[].foreign_keys[].key` | string | C/— | — | CSV only; exact `id`; unique actual ID values | Referential integrity | V | P-F |

**PROPOSED narrow CSV v1:** only `specs/pipeline/world_table.csv` is accepted as a CSV dependency
here. `facade_table.csv` retains its historical grammar but is not an invented QA authority;
adding a second CSV contract requires explicit design approval. Source-observed header is
`facade_tables.py:317–335`, independently read from `examples/world_table.csv`:
`instance_id, component_ref, family_ref, panel_ref, facade, level_index, panel_kind,
component_kind, x_cm, y_cm, z_cm, rot_z_deg, width_cm, height_cm, thickness_cm, joint_cm, layer`.
No header renaming, unit rescaling or q6 rewrite during QA reading.

Required foreign-key tuple set (paths below are project-relative):
`component_ref → specs/pipeline/components_registry.json / components / id`;
`family_ref → specs/pipeline/components_registry.json / families / id`;
`panel_ref → specs/pipeline/facade_grids.json / panels / id`;
`instance_id → specs/pipeline/facade_grids.json / panels / id`.
Each join tuple occurs exactly once; duplicate or missing tuples fail. Producer/grid/assembly
JSON dependencies are mandatory when this CSV dependency is used. Placement `source_row`
is a 1-based data-row bijection in **both directions**, not `instance_id==PLC-id`; actual
placement.component_id must equal the joined CSV component_ref. Every dependency has matching
project/cm-deg identity and locked status when required by P8. Declared producer relationship
does not by itself attest an executed build; receipt binding remains U19.

### 12.6 QA scope and check-plan leaves

`scope.targets` is a nonempty array of closed target objects with the leaves below; registry_ref
is required for form profile, absent for structure profile with no analytical registry. node_names
is an array of exact expected names expanded offline from existing mapping functions and then
independently checked against source IDs. No user wildcard or arbitrary node-name retargeting.
`check_plan` is a nonempty array of closed check objects; tolerance_ref is a bundle ID in §12.4.

| Path (qa) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `profile` | string | R/— | — | Exactly form_precision_v1 or legacy_structure_v1; §12.3 obligations | Required-family inference | V | P-F |
| `scope.registry_ref` | string | C/— | — | Form only: exact qualified path `dimensions.json:precision_targets`, locked/nonempty | Required analytical registry | Structural join exemption | P-F; U21 |
| `scope.targets[].id` | string | R/— | — | Unique §11.3 ID; analytic IDs equal precision_targets IDs | Scope/check join | I | P-F |
| `scope.targets[].kind` | string | R/— | — | Closed §12.3 target-kind set | Target resolver | V | P-F |
| `scope.targets[].source_ref` | string | C/— | — | Every kind except project; exact source selector/collection/ID | Source→name resolver | Structural join exemption | P-F |
| `scope.targets[].role` | string | R/— | — | Exact compatible kind/role pair §12.3; analytical design_surface only | Owned-role resolver | V | P-F; U16/U21 |
| `scope.targets[].node_names` | array of strings | R/— | — | Exact derived expected set, no wildcards/duplicates; project only `[]`; nonproject ≥1 | Census/ownership | D from source naming leaves; V for project empty set | P-F |
| `scope.targets[].reference_ref` | string | C/— | — | Analytical target only; matches S1 registry barrel reference; absent otherwise | Independent form oracle | Structural join exemption | P-F |
| `check_plan[].id` | string | R/— | — | Unique §11.3 ID; deterministic required-ID derivation awaits 02.2 wire/report design | Coverage/check identity | I | P-F; U18 |
| `check_plan[].kind` | string | R/— | — | Closed eight-family vocabulary §12.3, never unknown/disable | Family dispatch | V | P-F |
| `check_plan[].target_ref` | string | R/— | — | Exact scope ID, kind-compatible; uniqueness of (kind,target) | Coverage join | Structural join exemption | P-F |
| `check_plan[].reference_ref` | string | C/— | — | FORM only, equals target/registry reference; otherwise forbidden | Independent oracle join | Structural join exemption | P-F |
| `check_plan[].tolerance_ref` | string | R/— | — | Exact family-compatible bundle: exact/placement_v1/wall_box_v1/form_v1/replay_v1 | Dimensional comparator | V | P-F/T |

### 12.7 QA sampling and operational-limit leaves

`sampling` contains exactly the proposed leaves below; `limits` likewise. No value in an
operational-limit slot is frozen by this table. A proposed **5×5** baseline schedule is a plan
recommendation; counts and policies still need A-FIELDS, their method needs 02.2. Landmark and
resolver/receipt questions cannot be discharged by sampling more uniformly.

| Path (qa) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `sampling.policy` | string | R/— | — | Exact proposed `domain_grid_v1`, committed actual domain endpoints | Sample scheduler | V | P-F |
| `sampling.version` | string | R/— | — | Exact proposed `1`; policy revision, not schema version | Request schedule binding | V | P-F |
| `sampling.grid_u` | integer | R/—; propose 5, not default | count | Nonbool ≥2, includes both domain endpoints; bounded by limits.max_samples | Scheduler | Q operational choice with ledger if inferred | P-F |
| `sampling.grid_v` | integer | R/—; propose 5, not default | count | Nonbool ≥2, includes both domain endpoints; bounded by limits.max_samples | Scheduler | Q operational choice with ledger if inferred | P-F |
| `sampling.landmarks_policy` | string | R/— | — | Form: proposed barrel_landmarks_v1; structure: none_v1; precise matching pending | Critical coverage | V | P-F; PENDING U15 |
| `sampling.selected_frame` | integer | R/— | frame | Finite nonbool integer incl. negative; no default/current-frame fallback; live frame/tick route pending | Receipt/batch stability | Q owner-selected frame | P-F; PENDING U17 |
| `limits.max_rows_per_batch` | integer | R/— | rows | Nonbool >0; 25 evalPos rows is a trial recommendation only, not certified capacity | Batching | Q/D from approved calibration | P-F; PENDING U07 |
| `limits.max_targets` | integer | R/— | targets | Nonbool >0; exceed → refusal, never truncate scope | Request cap | Q/D | P-F; PENDING U08 |
| `limits.max_samples` | integer | R/— | samples/run | Nonbool >0; includes grid+all landmarks, no dropped samples | Schedule cap | Q/D | P-F; PENDING U09 |
| `limits.max_calls` | integer | R/— | MCP calls/run | Nonbool >0; complete planned collection must fit | Batch-plan cap | Q/D | P-F; PENDING U10 |
| `limits.max_batch_seconds` | number | R/— | s/call | >0; main-thread bounded work, value needs controlled time probe | Batch safety | Q/D | P-F; PENDING U11 |
| `limits.max_total_seconds` | number | R/— | s/run | >0; exceed/exhaustion → INCOMPLETE, not partial PASS | Collection bound | Q/D | P-F; PENDING U12 |
| `limits.max_solver_iterations` | integer | R/— | refinements/sample | Nonbool >0; exact refinement definition pending U03 | Bounded nearest solver | Q/D | P-F; PENDING U13 |
| `limits.max_response_bytes` | integer | R/— | bytes/response | Nonbool >0; parser/truncation capacity needs calibration; no silently clipped rows | Wire completeness | Q/D | P-F; PENDING U14 |

Grid fractions for proposed n=5 are `{0,.25,.5,.75,1}`; other approved counts use
i/(n−1), not angle fractions. Domain endpoints are read after commit. Required barrel landmarks
are first/middle/last longitudinal station springings/crown plus longitudinal endpoint coverage;
**their live UV selection/matching is U15**, not an assumption that mid-UV is the crown.
All limits are operational counts/time/bytes, never geometric tolerance. A complete config cannot
contain the symbolic Uxx labels or nulls: these are **design placeholders only**, blocking freeze.

### 12.8 Optional capture-plan item leaves

`capture_plan` is a required array, **empty allowed**. Each nonempty item is a closed object with
exactly these leaves. Captures are optional attachments, not quantitative check rows or a way to
meet mandatory coverage. No camera, renderer, selection-isolation or scene-mutation request is
added; the collector uses an approved viewport capture route in future 02.2/02.3 protocol work.

| Path (qa) | Type | Required / default | Units | Range / consumer constraints | Consumer | Origin | Status |
|---|---|---|---|---|---|---|---|
| `capture_plan[].id` | string | R/— per item | — | Unique §11.3 ID | Attachment identity | I | P-F |
| `capture_plan[].kind` | string | R/— per item | — | Exact proposed `current_viewport`; no render request | Read-only collector | V | P-F |
| `capture_plan[].target_refs` | array of strings | R/— per item | — | ≥1 distinct existing scope IDs; labels attachment relevance, does not isolate/select | Attachment→scope join | Structural join exemption | P-F |

---

## 13. PROPOSED tolerances, unresolved choices and microtask 02.1 local gate

### 13.1 PROPOSED dimensional budgets and boundary comparator

**A-TOL proposal, not a freeze:** distinguish (1) arithmetic consistency of canonical data,
(2) physical form/extent/landmark allowances, (3) numerical uncertainty in solver/wire/factor/
volume arithmetic. Preserve dimensions' original arithmetic values and the QA owner's original
physical thresholds verbatim in future requests/results. Never widen a geometric tolerance to
hide discretisation, sparse coverage, solver exhaustion, native-unit rounding or collection error.

Existing example arithmetic **0.5 cm / 0.05 m² / 0.01°** is historical source data, not an
automatically inherited physical form contract. **0.5 cm = 5 mm**; recommendation of
**surface_deviation_cm=0.5** here is solely a **NEW proposed physical choice** needing explicit
user approval. Extent/landmark tolerances are separate owner choices, no invented numeric defaults.
Expansion's **0.001 cm** is a proposed stored-points consistency check, not a form allowance or
a settled shell cutoff. Reject negative/nonfinite/bool tolerances; an explicitly permitted **zero
stays zero**, never `value or default`. Surface tolerance is proposed >0; other listed ≥0 budgets
retain meaningful exact-zero semantics with intervals.

**PROPOSED Box volume policy, derived from plan §7:** use only an independently confirmed
axis-aligned solid Box assumption; rotated bbox product is not physical volume. Given expected
positive extents w,h,t cm and an endpoint comparison allowance e cm taken from the declared
linear arithmetic tolerance, each extent uncertainty is d=2e cm. The conservative per-solid
physical budget B cm³ is the maximum of:

- upper product difference `(w+d)(h+d)(t+d) − wht`;
- lower product difference `wht − max(w−d,0)max(h−d,0)max(t−d,0)`.

This has volume units by multiplication of **three lengths**; it is **not linear_cm squared**.
e=0 yields B=0, no fallback. Expected extents come from locked independent source formulas,
not measured erroneous bbox values selected to enlarge B. For the signed wall identity
ΣVcells − Vhost + ΣVopenings, sum participating **per-solid absolute budgets once each** by the
triangle inequality; coefficients of magnitude one justify that sum even for correlated endpoint
errors. Avoid duplicate solids/openings and separately prove occupancy, no overlaps/gaps and
full thickness. This large conservative allowance can conceal small holes in a volume total;
mandatory per-cell/interval occupancy checks prevent calling that alone a wall PASS.

Separate `volume_roundoff_cm3` bounds numerical evaluation/readback, not physical B; it affects
the observed volume-error interval only. Other rotated/mesh/open-edge volume methods require
calibration and a separate approved policy (plan 03.8), **not** a guessed bbox fallback. Replacing
current G-82 requires A-CORRECT plus owner code permission after design approval; none is granted.

**PROPOSED interval comparator:** for the relevant nonnegative physical error, compute a
certified `[lower,upper]` after quantity-correct numerical propagation. If **upper≤tolerance**,
PASS for that check; if **lower>tolerance**, FAIL; otherwise **INCOMPLETE**. Original tolerance
is never modified. Exact boundary equality on a singleton interval passes; uncertain straddling
never does. Mandatory form gate is **maximum** sampled deviation; mean/RMS are report summaries
only and cannot compensate for one failing sample. Missing required samples/API resolution gives
INCOMPLETE/ERROR, never an empty max of zero. Sampled conformance is not a global surface proof.

### 13.2 PROPOSED mathematical bounds, with calibration still open

For a curve segment parameter span Δt radians, the candidate vector linear-interpolation bound
is `max(a,b)·Δt²/8` cm since ||C″||≤max(a,b). Rounded endpoint coordinate uncertainty q6 gives
`sqrt(3)·0.5·10^-6 cm`; add that endpoint contribution to the corresponding chord bound.
This is a curve→associated-chord bound, not a NURBS interpolation/Hausdorff certificate; exact
minor-circle sagitta and sampled estimates must be named separately. Policy numeric constants
here are mathematical derivation, not configurable guessed origins. U01 and U03 must settle
closed segments, solver termination and bound prerequisites in 02.2.

Wire/factor/solver/volume numerical budgets must bound the **actual** method and magnitude range.
No concrete live enum, transport formatting precision, solver iteration count or 25-row capacity
is certified by this patch. The following register has operational/numeric placeholders **only
in design**; they cannot be copied into a ready config or treated as final executable contracts.

### 13.3 Unresolved register — 22 explicit question groups

**02.1 history; current dispositions are §19.1.** All **ten A-* approvals in §4 remain OPEN**.
At the end of 02.1, **22 unresolved leaf/consumer-contract
question groups U01–U22** remain for 02.2/02.3 (19 for 02.2, 3 for 02.3). These counts are not
22 invented nullable fields; future report/wire/CLI leaf inventories are not authored by 02.1.
Physical project input slots with explicit owner choice (extent/landmark tolerance, frame value,
construction_count) have **no default**; this is a proposed input obligation, not a silently
selected number. User may reject any proposed schema choice at 02.4.

| ID | Exact remaining question / affected leaves or contract | Next microtask | Approval dependency |
|---|---|---|---|
| U01 | Which closed consumer, seam duplicate, minimum distinct vertices and segment-bound prerequisites make delta=360/count valid? | 02.2 | A-CLOSED/FIELDS |
| U02 | At shell abs(thickness)=0.001 cm is shell present? Align library, census and validator without choosing now | 02.2 | A-CLOSED |
| U03 | Which finite nearest-distance algorithm, proof/termination rule and numeric solver_distance_cm bound apply to every oriented finite arc? | 02.2 | A-TOL/FIELDS |
| U04 | What certified wire_length_cm and wire_angle_deg bounds follow from locale/escaping/scalar serialization and supported quantity magnitudes? | 02.2 | A-TOL/LIVE |
| U05 | What unit_factor_relative bound/precision and magnitude propagation are certified, without q6 factors? | 02.2 | A-TOL/LIVE |
| U06 | What volume_roundoff_cm3 bound is justified per aggregate/method and scale, separate from physical endpoint propagation? | 02.2 | A-TOL/LIVE |
| U07 | What max_rows_per_batch is safe? Is initial 25 evalPos rows viable with transforms/guards/serialization? | 02.2 | A-FIELDS/LIVE |
| U08 | Which numeric max_targets is an explicit operational cap without truncating mandatory scope? | 02.2 | A-FIELDS |
| U09 | Which numeric max_samples accounts for grid and required landmark samples? | 02.2 | A-FIELDS |
| U10 | Which numeric max_calls covers all required batch/control/metadata calls? | 02.2 | A-FIELDS |
| U11 | Which numeric max_batch_seconds keeps bounded main-thread work safe in calibrated scenes? | 02.2 | A-FIELDS/LIVE |
| U12 | Which numeric max_total_seconds defines exhaustion without partial PASS? | 02.2 | A-FIELDS |
| U13 | Which numeric max_solver_iterations and refinement-unit definition guarantee bounded termination? | 02.2 | A-FIELDS/TOL |
| U14 | Which numeric max_response_bytes and truncation/receipt rule guarantee a complete wire response? | 02.2 | A-FIELDS/LIVE |
| U15 | How are springings/crown/first-middle-last stations actually matched in UV, with stable sample IDs and endpoint coverage? | 02.2 | A-FIELDS/LIVE |
| U16 | Which role/census/domain/relation evidence identifies design_surface, especially blend/trim/shell, without first/last heuristics? | 02.2 | A-FIELDS/LIVE |
| U17 | How is selected_frame (integer frames) read, converted to native ticks and checked unchanged in receipts/batches? | 02.2 | A-FIELDS/LIVE |
| U18 | Exact request/report/wire containers/leaves, required-ID derivation, enums, escaping, hash inclusion/exclusion and uncertainty evidence links? | 02.2 | A-FIELDS/TOL |
| U19 | Exact run/session/build-receipt leaves, library revision guard, build binding and replay receipts without a fictional server token? | 02.2 | A-FIELDS/LIVE |
| U20 | What contextual inventory API/CLI lets earlier legacy stages SKIP QA while P8 requires defined locked config? | 02.3 | A-FIELDS/OWNERS |
| U21 | Exact owner migration/atomic publication and prior-registry scope-change binding; wall-host representation/correction ownership? | 02.3 | A-WRITE/OWNERS/CORRECT |
| U22 | Exact fixture/recipe/adaptive-regeneration location and explicit future CLI ownership, keeping historical examples byte-identical? | 02.3 | A-EXAMPLE/REGEN/OWNERS |

### 13.4 Microtask 02.1 local gate record — design review only

**ID 02.1; DRAFT / NOT FROZEN; no phase-02 PASS, no implementation claim.** This local record
states design coverage and review cases, not observed validator messages or a live certification.

- **Exclusive write ownership:** `references/_form-units-qa-design.md` only. The user authorized
  continuation of design work; approval decisions remain open. This patch proposes,
  **does not approve** A-VERSION/A-FIELDS/A-TOL. Root plan §§1–6, 9–11 governs; PLAN is historical
  scope and CHECKPOINT historical measured status. No CHECKPOINT update is authorised.
- **Leaf diff:** §11.2 envelope **10**, §11.3 origin metadata **5**, §11.4 raw evidence **5**,
  §12.1 references/targets **15**, §12.2 sections/generator **13**, §12.4 tolerances **14**,
  §12.5 dependencies **18**, §12.6 profile/scope/checks **13**, §12.7 sampling/limits **14**,
  §12.8 capture **3**: **110 leaf families**. All ten leaf tables have the eight columns
  path/type/required-default/units/range-consumer constraints/consumer/origin/status. Containers,
  scalar-array items, forbidden alternatives and the source-selector exception are explicit.
  This is a scoped inventory, not 110 wholly new keys: **21 reused leaf families** (10 envelope,
  5 origin metadata, 3 existing section leaves, 3 arithmetic tolerances) and **89 added families**;
  the tables explicitly propose changed consumer/coverage constraints on reused interfaces too.
- **Unresolved:** all ten A-* rows OPEN, plus U01–U22 above; numeric calibration/operational
  slots U03–U14 remain without chosen values. Further request/report/receipt/CLI leaves are
  explicitly 02.2/02.3 inventory work, not hidden missing entries in a purported frozen schema.
- **Narrow historical correction:** §5.1's full-chain row had double-counted PLC/PROTO/WAL
  subsets already inside 239 boxes. CHECKPOINT:1146–1150 unequivocally gives 27+10+217=254,
  with 239 Box+5 Dummy=244 excluding NURBS. P6's distinct 244 row is retained.

**DESIGN cases only — NOT EXECUTED validator checks:**

| Case | Independent input / expected policy outcome | Why this is not execution evidence |
|---|---|---|
| Positive V1 | Existing 1.0 geometry without new keys and no QA at S1–S5 → legacy QA NOT_EVALUATED/static SKIP | Proposed compatibility, no validator run |
| Positive V2 | 1.1 dimensions/NURBS + 1.0 assembly/registry + locked QA 1.1, exact per-file dependency versions → compatible, no 1.1 WARN | Schema join design, no assessment |
| Positive D1 | JSON dependency file/spec/version equals actual envelope; source_ref `nurbs.json:surfaces:SUR-001` resolves unique existing surface | Design resolver case, no implemented new resolver |
| Positive D2 | CSV header exact; producer JSON version matches; source_row 1 maps first data row; foreign-key IDs resolve; every row used once | Design bijection case, not a CSV placement/count gate |
| Known answer MM1 | Explicit raw 1800 mm → 180 cm; explicit raw .5 mm → .05 cm; conversion origins name raw value and unit | Mathematical known answers, no normaliser execution |
| Invalid R1 | Section joins ellipse reference `[600,180]`, but generator and regenerated points both use `[600,185]` → reference-join failure even if point recompute succeeds | Independent upstream-authority mutation, policy outcome only |
| Invalid O1 | Claimed derived generator axes name `dimensions.json:form_references[99].semi_axes_cm` absent in actual dimensions → unresolved provenance failure, not default radius | Independent missing-origin path, policy outcome only |
| Invalid O2 | Generator axes derive from local points_cm while points derive from generator → circular-authority failure | Independent cycle case, not merely the missing-index defect |
| Invalid V3 | New generator key under 1.0 or schema string 1.1.0 → refusal under proposed exact-version policy | Requires A-VERSION; no current-source refusal claimed |
| Invalid Q1 | Remove locked analytical target/check or insert disable/result leaf → missing-required/config failure, not a smaller PASS set | Required-registry/config policy, no assessor run |
| Boundary T1 | tol=.5 cm: [lower,upper]=[.5,.5] passes; [.5001,.5002] fails; [.4999,.5001] incomplete; low mean cannot override max | Comparator DESIGN cases, .5 not approved physical input |

Read-only review for this patch covers saved document bytes, all table-column counts/leaf-family
totals, decision statuses and ownership against the starting git status. The starting tree had
exactly three untracked additions: root `AGENT_BRIEF_form_precision.md`, root
`AGENT_PLAN_form_precision.md`, and this design. Read-only git diff/status plus unchanged root
file hashes check for tracked changes or scope drift; untracked design needs no-index diff,
since ordinary git diff omits it. These are document checks, not builder/validator/Max tests.

Actual read-only review results: saved UTF-8 bytes have no BOM, LF line endings and one final LF;
ten leaf tables have row counts **10/5/5/15/13/14/18/13/14/3 = 110**, all rows eight columns and
PROPOSED status; **10 OPEN approvals**, **22 U groups**, header **DRAFT / NOT FROZEN**.
Reversing only the declared preamble/navigation/register/history edits in memory reconstructs
the starting 502-line design blob **b32c55b3f0eed54f55c2f6de22be0a9fe21d8bf6** exactly (the
original lacked a final LF; the saved design now has one). Tracked git diff is empty; no-index
diff/check covers this untracked design. Root input blobs remain unchanged:
`AGENT_BRIEF_form_precision.md` **ca5827af3cc896be67ada861a82dd7a666446ad1**;
`AGENT_PLAN_form_precision.md` **4aaf640f0c670a6c8bd0e3d877c77b93dd3fcacb**.
These hashes bind source documents, not executed geometry. Document inspection uses an inline
read-only `python -B` counter/hash check, no imports of project scripts or cache/artifact writes;
`rg` was unavailable, so its attempted count checks supplied no evidence. No validator was run.

**02.1 hand-off, retained as history: next was 02.2 design-only patch**, only after its own explicit scope authorisation, to settle the
closed/shell/solver/landmark/wire/report/receipt questions. Then 02.3 completes inventory/CLI/
ownership/location policy. **Approval 02.4 is required** before any FREEZE or code. No fresh or
seeded config, fixture, run artifact, install, commit, Max probe or CHECKPOINT change is produced
by 02.1.

---

## 14. PROPOSED 02.2 policy and navigation

**02.2 / PROPOSED ONLY.** This extension recommends exact data/decision policies for U01–U19;
runtime success, API spellings and certified precision remain evidence gates. It is neither FREEZE
nor phase-02 PASS. All ten A-* rows remain **OPEN**, including A-LIVE. “продолжай” authorized
continuation of design, not approval. No change to §§11–12 schemas is implicit: §14.2 lists the
few exact refinements; reusable runtime records in §17 reference existing leaves rather than
creating another geometry/config schema. U20–U22 and publication/migration remain 02.3.

**Navigation:** §14.1 closed/shell → §15 independent math → §16 live selection/space/IDs →
§17 request/context/receipt/wire/raw/report inventories → §18 calibration/bounds → §19 register/gate.
The table conventions and origins in §11 apply. Additional origin `M` means immutable captured
measurement, `H` means independently computed hash/assessment, and `R` means supplied receipt
binding. None is an alternative source of geometrical intent.

### 14.1 Closed 360 and shell: exact recommendations

**U01 / A-CLOSED + A-FIELDS:** recommend **refuse abs(to_deg−from_deg)=360 in core v1** for
references used as generated sections and for generators, regardless of count. Open finite arcs
require `0<abs(delta)<360`; the barrel keeps §12.2's exact upper-half endpoints. No supported
closed consumer is proposed in 02.2. Therefore no new seam flag, count convention or closed API
claim is added. A future explicit closed-consumer approval must return to design and specify one
seam, count **including** its repeated endpoint, ≥3 distinct rounded vertices (thus count≥4),
adjacent duplicate rejection including the cyclic adjacency of distinct vertices, and source/API
compatibility. That is an extension gate, not today's executable exception.

Source compatibility explains the refusal, rather than implying API absence: the source library
has native `makePointCurve(...closed:true)` but CV closure is seam-welded, not topological
(`nurbs_arch_library.ms:45–77`); the loft accepts `closedSections` internally (`:104–109`), while
dependent sweeps emit open rail/section curves and trim emits closed profiles
(`build_nurbs.py:1962–1968,2004–2014`). A generated repeated-seam circle cannot simply be fed to
all these consumers. Their source text is not new live evidence. **Design controls:** full-circle
count 2 and count 3 both refuse under core policy; an open arc whose q6 endpoints or successive
points round equal also refuses. Even future closure cannot rescue count 2/3: they provide fewer
than three distinct vertices when count includes the repeated seam.

**U02 / A-CLOSED:** decide once in canonical cm: thickness=0 → `shell_present=false`;
`0<abs(thickness_cm)<0.001` → refusal; **abs(thickness_cm)≥0.001 → true**, including equality
and either sign. Only a finite nonbool input is considered. Census, validator, emitter and library
must receive this same decision. The future library takes an explicit presence decision plus
scene-native signed distance; it must not re-decide with `abs(native)>0.001`. At equality the
recommended u_loft surface census is two, at zero one. Initial forwarding/sign/actual geometry
are **C03-SHELL (03.6)** evidence obligations, not executed findings here.

### 14.2 Refinements of the saved 02.1 proposal

These are explicit recommended restrictions on the existing tables, not duplicated schemas:

- §12.7 `grid_u=grid_v=5` exactly for `domain_grid_v1` in this v1 profile; no configurable alternate
  grid accepted under the same policy ID. Fractions remain `{0,.25,.5,.75,1}`.
- §12.6 check IDs are generated by §16.3, not free choices merely matching a safe regex.
- §12.4 numerical leaves are required in a **ready** config and must exactly equal the selected
  certificate's bounds. No Q/assumed entry can manufacture a certification. A draft can omit the
  five not-yet-bound numeric leaves while retaining `numerical.policy=separate_bounds_v1` and
  explicitly remain NOT_READY; never null or Uxx in executable input. Its ready grammar is unchanged.
- §12.5 calibration artifacts are **not** extra JSON specs with invented envelopes. The certificate
  is a separate §17.7 run input supplied at emit; QA derived origins cite its immutable digest and
  §17.7 paths through the certificate binding, not the §11.3 known-spec resolver. This narrowly
  defined evidence-input namespace is `calibration:<sha256>:<local-path>`; it cannot resolve shape
  values or other provenance. Ready QA numeric origins name the selected certificate paths.
- §12.7 operational caps are all explicitly QA-owner supplied, no defaults; §18.2 freezes their
  selection/validation algorithm. Local time guards are additional limits, not precision budgets.

## 15. PROPOSED independent analytic algorithms

### 15.1 Oriented finite arc, interval branch/refine and exhaustion

**U03 / A-TOL + A-FIELDS:** assessor derives its own reference from locked dimensions, never
`generator_points`, emitted points, a NURBS fit or implicit ellipse residual. Convert input degrees
to radians once. Preserve signed unwrapped `delta=to−from`; reject zero/out-of-policy span. For
nearest distance use `l=min(t0,t1), r=max(t0,t1)` without modulo; traversal order is retained for
endpoint IDs. A crossing such as 350→370 is the small crossing; 350→10 is the distinct reverse
340° arc. No shortest-arc rewrite. Endpoints C(t0), C(t1) are always explicit candidates.

For transverse point p and C(t)=(a cos t,b sin t), `a_max=max(a,b)` bounds ||C′||.
On closed interval I=[l,r], m=(l+r)/2, h=(r−l)/2:
`lower(I)=max(0,d(p,C(m))−a_max*h)`; upper is the minimum of **evaluated distances at both
endpoints and midpoint**, accumulated globally. For full 3D arc distance include the fixed
orthogonal-coordinate difference in d; the derivative bound is unchanged. All calculations are
enclosed with outward numerical bounds under §18.1: use d_mid.lower and upper a_max*h for
lower, and d_eval.upper for upper. A nominal floating estimate alone is not a certified bound.

Algorithm: initialise root and endpoint/midpoint evaluations; maintain a queue of live intervals
with bounds and a deterministic path (`root`, then `0`/`1` per bisection). Global L=min live lowers,
U=min all evaluated uppers. Remove an interval only when its lower>U; equality is retained.
Select the least `(lower,l,r,path)` lexicographically, bisect at m, evaluate each child's midpoint,
reuse endpoint evaluations, and replace that interval by the two children. **One iteration = one
such replacement**, not one distance evaluation. Count root evaluation separately; duplicate
parameter evaluations are cached by exact interval path/endpoint identity. Guards run before each
refinement. At most max_solver_iterations replacements per sample; nonfinite/overflow is ERROR.

Terminate successfully only when `U−L≤solver_distance_cm`, yielding `[L,U]`, best evaluated
parameter/point and complete trace bounds. Independently propagate wire/factor/position uncertainty
by distance's 1-Lipschitz property. Report both the nominal solver bracket and final error interval;
use §13.1's upper≤T / lower>T / otherwise INCOMPLETE. If the bracket meets its width budget but
straddles T, comparator remains INCOMPLETE. Iteration/time exhaustion, unsplittable floating
interval, missing evaluation or unavailable arithmetic enclosure → **INCOMPLETE**, even when a
best estimate looks small. A proved FAIL may be reported as a diagnostic but cannot certify a
complete exhausted run. Trace replay by the assessor checks all pruning and final bounds.

### 15.2 Finite barrel and independent controls

For world-cm P=(x,y,z), transverse p=(x−cx,z−cz), independently solve the upper finite arc;
`d_span=max(s0−y,0,y−s1)` and **D=sqrt(d_arc²+d_span²)**. Squaring/sqrt use outward enclosures.
This formula requires §12.2's orthonormal world XZ/+Y frame; actual node transforms do not rotate
the reference. Arc and longitudinal nearest minimisers are independent in a Cartesian product.
Station/landmark/extent checks remain separate, so a shorter surface on the correct infinite
cylinder cannot pass merely by having zero interior distance.

**Independent policy controls, not executed tests:** full-circle mathematical control (solver
test domain only, not accepted generator) radius R gives ||p||−R in absolute value; at the center
distance R. For the finite upper semicircle, p=(0,R+h), h≥0 gives crown distance h. For a=600,
b=180 and p=(0,185), all candidates have z≤180 and the crown yields exactly 5 cm. For P at the
ideal crown but y=s1+7, finite barrel distance is exactly 7 cm, not zero; at y=s0/s1 it is zero.
Reverse 180→0 must give the same nearest bracket as 0→180 but reverse endpoint labels. For
an arc 0→90, p=(-R,0) has finite endpoint distance sqrt(2)R, not the zero of the infinite circle.
These constants come from independent geometry; no call to generation is a control oracle.

### 15.3 Chords and minimum count: distinct claims

For n endpoint-inclusive samples, `Δ=abs(t1−t0)/(n−1)` radians. **Circle minor sagitta** is
`R*(1−cos(Δ/2))` for `0<Δ≤π` only; it bounds curve-to-associated-chord distance for that minor
segment. For Δ>π do not use it as a minor sagitta. The **conservative interpolation bound**
`a_max*Δ²/8` follows ||C″||≤a_max and applies to any finite segment here; add
`sqrt(3)*0.5e−6 cm` for q6 endpoint perturbation (convex interpolation of endpoint errors cannot
exceed that norm bound). Use outward arithmetic enclosure for the bound evaluation too.
Sampled chord estimates are diagnostics, not proofs. None of these is a NURBS interpolation
bound or an inverse Hausdorff bound.

Suggestion evaluates n=2..500 in ascending order, first applying §14.1 admissibility and rounded
adjacent/nonadjacent duplicate guards, then the named bound. Choose the first with certified
upper≤the explicitly supplied positive tol_cm. Circle uses `circle_minor_sagitta_q6_v1` only
when its segment prerequisite holds, otherwise `ellipse_second_derivative_q6_v1` (a=b allowed).
No qualifying n → refusal/no recommendation; do not choose 500 and claim success. Count remains
an owner-adopted construction input, not an implicit change to dimensions. Full-circle count2/3
controls refuse before evaluating suggestions. Tiny open arcs with rounded zero chords refuse.

## 16. PROPOSED committed targets, landmarks and stable identity

### 16.1 Design-surface resolver: kind, census and relation together

**U16:** resolve exact owned node names, requiring unique actual nodes and committed sets. Census
enumerates **all** actual subobjects; curves/points are recorded but never sent to surface evalPos.
Expected surfaces follow kind and §14.1 shell decision. This source-based class-role map is a
recommendation, not new runtime evidence; **C03-ROLE (03.5/03.7)** must calibrate its read-back
mechanisms with correct base, offset and wrong-role controls before supporting a kind.

| Source kind | Recommended surface census / design role | Required discriminator; unsupported outcome |
|---|---|---|
| u_loft | 1 base, plus 1 offset iff canonical shell_present | Base U-loft class and section relation identities; offset class/parent resolves base and signed native distance. Never select first/last alone |
| uv_loft | 1 Gordon-network design surface | Surface kind, U/V section relation sets, committed nonempty actual domains |
| point_grid / cv_grid | 1 design surface | Corresponding point/CV surface kind, lattice cardinalities and committed domains; points ancillary |
| rail_sweep / two_rail_sweep | 1 sweep design surface | Correct sweep class, rail identities and section sequence; read-back index 0 alone proves nothing |
| blend | 1 blend design surface | Actual parent IDs resolve the exact committed design surfaces of both source parents, edges/tensions agree; never copied parent selection |
| trim | 0 surfaces under current emitted trim:false | Record projection/profile curves, no phantom design surface. A declared analytical target here is unsupported ERROR, not dropped |

Class identifiers are an emitter/certificate mapping, not config strings. Compare native relation
handles by actual committed objects within this session; do not synthesise `nurbsID` literals or
persist printed pointers as authority. Hash fingerprints may bind their local captured labels only.
Unexpected census, unresolvable parent, duplicate candidate or wrong known role → ERROR. Missing
domain/read route or uncertified relation mechanism → INCOMPLETE. Neither shrinks required scope.
Derivative nodes are separate census/geometry targets and cannot substitute for design_surface.
Only kinds with complete C03-ROLE **and** landmark capability may be analytical delivery targets.
Analytical target applicability requires a nontrim supported design surface, not a validator
exception for an unresolvable kind. Nonanalytical trim still gets node and zero-surface census.

### 16.2 Domain grid, required landmarks, actual-space contract

Read actual U=[u0,u1], V=[v0,v1] **after commit**; require finite strict increasing endpoints.
Grid point `(i,j)` uses `u=u0+(u1−u0)i/4`, `v=v0+(v1−v0)j/4`, i,j=0..4. Endpoints are included;
u/v are native parameter coordinates, neither lengths nor ellipse angles. Report domain intervals
and sample UV values. Empty/unknown domains refuse evaluation; do not substitute [0,1].

For each barrel target, required **additional** samples are nine fixed world reference points:
left springing/crown/right springing at stations s0, (s0+s1)/2, s1; plus **two independent**
`longitudinal_endpoint/start` and `/end` samples located at the corresponding crown anchors.
Thus **25+9+2=36 required sample identities per analytical target**. Co-located endpoint/crown
points may reuse an evaluation, but retain two obligations and comparison IDs; never erase one
by coordinate deduplication. Left/right are world x=cx−a/cx+a, crown=[cx,s,cz+b]; traversal
direction does not rename left/right. Endpoint rows also compare y against s0/s1; all three station
groups compare their own y and XYZ position. Form-distance and landmark-position tolerances
remain distinct. Interior grid rows cannot replace critical station/extent obligations.

**U15 independent bounded localization recommendation:** minimise ||S_world_cm(u,v)−Q|| over
the entire actual committed surface domain for each fixed landmark Q. Use a read-only captured
committed representation and an independent interval evaluator of that representation, or a
calibrated equivalent enclosure route, never generator sections or assumed mid-UV. On rectangle
I with midpoint (um,vm), require proved actual-surface derivative bounds Lu,Lv in cm/parameter;
lower=max(0,d_mid.lower−Lu*half_u−Lv*half_v), upper from evaluated corners/midpoint. Branch on
the axis with larger bound contribution (U on ties), choose rectangle by (lower,u0,v0,u1,v1,path),
reuse shared evaluations, and apply §15.1 pruning/width/exhaustion rules. One replacement is one
solver iteration. The **analytic ellipse a_max is never a NURBS derivative bound**.

The independent evaluator must enclose actual rational/relational geometry and transforms; knot
breaks/denominator positivity and parent relations must be accounted for. **C03-LANDMARK (03.5)**
must establish the concrete Max read-only representation/evaluation/derivative-bound API route
with crown/springing, nonmid-UV, wrong surface and translated/rotated/parented/nonuniform controls.
No such API is asserted available here. If no bounded route exists, return to design with evidence;
the target stays INCOMPLETE and cannot obtain form PASS from a denser grid.

Return an actually evalPos-evaluated best UV, its world point, minimisation bracket, point
enclosure and replayable subdivision trace. The nearest UV need not be unique; choose the
lexicographically smallest evaluated `(u,v)` on equal upper bounds. This is a bounded nearest
landmark candidate, **not** a claim of unique crown parameter. Position-to-Q and station/extent
errors are independently bounded from its measured point. Include every internal evaluation in
operation/time guards and trace count; exhaustion is INCOMPLETE, not an omitted landmark.

**Exact space contract:** surface evalPos is treated as `local_scene` only after C03-SPACE proves
it. Collector applies **node.objectTransform once**, including parent/pivot effects, obtaining
`world_scene`; no additional node.transform/parent transform. Assessor multiplies declared
length coordinates by c **once** to `world_cm`. Bbox endpoints already `world_scene` get no
objectTransform. Derivative-generated evaluated vertices are native values, not canonical cm
inputs. Directions, parameter domains, degrees, indices and knots are not blanket-scaled.
For nonuniform objectTransform, committed local derivative bounds are pushed through a proved
matrix norm bound before localization; otherwise INCOMPLETE. Reference stays the world-cm intent.

### 16.3 Mandatory ID generation and denominator

**U18:** use unambiguous semantic-key arrays encoded by §17.1 canonical bytes. ID is prefix
plus the first **63 lowercase hex digits** of SHA-256(key): T/C/S/O/B respectively for derived
target/check/sample/observation/batch. Detect collisions by retaining full keys/full digests and
refuse, never suffix-renumber. Analytical target IDs retain locked precision_targets IDs;
project target ID is `Project`; other target keys are `[kind,source_ref,role]` and source ownership
expansion is independent of qa.scope. Existing node naming maps stay the authority for names.

Check key `[family,target_id]`; sample key `[check_id,schedule_label]`; observation key
`[check_id,target_id,sample_id]`. For non-sampled checks sample label is `record` (one aggregate
record containing its exact typed metric/identity sets). Grid label `grid/i/j` with decimal i,j;
landmarks `station/first|middle|last/left|crown|right`; endpoint labels as §16.2. Replay uses
`stage/<stage>/pass/1|2|3`; the one project replay check compares all applicable stage/pass records.
Batch key `[ordinal,ordered_observation_ids,ordered_trace_slot_ids]`; ordinal is zero-based over the deterministic sorted
planned partition. Full source names and metric tags are retained, not inferred from truncated IDs.
Trace slot ID uses prefix `X` and the same 63-hex rule on `[sample_id,"localization",slot_index]`,
slot_index=0..K with K=max_solver_iterations; slot0 is initialization, slot k>0 one replacement.
Actual evaluation IDs use prefix `E` on `[sample_id,"localization",slot_index,eval_index]`, with
eval_index=0..4 at slot0 and 0..9 at later slots (a conservative five/ten evaluation upper per
initialization/two child rectangles). Unused cached/terminated evaluations are explicit unused,
not missing. Offline arc-solver evaluations use E key `[sample_id,"arc",slot_index,eval_index]`,
initial eval_index=0..2 and later 0..1. These bounded slots are independent of actual UV paths.
Source/analytic reserved ID collisions, including Project, are refusal. Exact node names cannot
become identifiers by undocumented sanitization. Receipt/replay FileBind IDs derive from
`[stage,pass_index,sha256]` with prefix `R`; response IDs use prefix `D` on `[run_id,batch_id]`.

Mandatory families are independently inferred exactly as §12.3; configured `(kind,target)` pairs
and generated IDs must be a bijection with that inference. Infer every applicable node/host/stack,
not only analytical ones. Project coverage and replay are nonempty aggregate observations even
when another family has no applicable objects; inapplicable families are documented outside the
mandatory set, not zero-count PASS. For **each applicable mandatory check**, exact expected,
observed and compared observation/sample/metric-identity sets agree and
**N_expected=N_observed=N_compared>0**. Equality of counts alone is insufficient. Unknown,
duplicate, extra, substituted or missing IDs → ERROR/INCOMPLETE and no run PASS. Match keyed
records, never zip arrays, nearest names, default zeros or silent missing-field defaults.
Optional captures have a separate NOT_RUN/ATTACHED/ERROR inventory; they do not enter those
denominators. Optional scatter is absent from core families and carries no determinism claim.

## 17. PROPOSED runtime artifacts, canonical hashing and wire grammar

**U18/U19 / A-FIELDS + A-TOL + A-LIVE:** the following are closed runtime artifact schemas,
**not pipeline specs** and not implemented files. Each table row is one leaf family using §11's
array convention. Unknown keys/nulls refuse. Object containers and references below reuse one
record definition; they do not duplicate the §§11–12 config/reference schema. All rows in §17
are PROPOSED even without a repeated status column. `R` means required/no default, `C` means
required only in the stated variant/otherwise forbidden, `O` optional/absent. All scalar numbers
are finite/nonbool; integer-token policy remains §11. SHA means 64 lowercase hex digits.

### 17.1 Canonical bytes, inclusion/exclusion and deterministic partition

**Exact proposed canonical JSON method `form_cjson_v1`:** UTF-8 without BOM, no insignificant
whitespace or terminal LF, object keys sorted by their Unicode code-point sequence; arrays in
the orders explicitly defined below. Strings preserve code points (no Unicode normalization),
reject unpaired surrogates, escape quote/backslash and controls U+0000..001F using lowercase
`\u00xx`; do not escape slash/non-ASCII. Integers use minimal base-10 spelling. For other numbers
parse original JSON tokens as exact decimal, remove insignificant leading/trailing zeros, use
plain decimal notation without exponent, normalize either signed zero to `0`; exact decimal
value is preserved, no q6 on hashes/factors. Nonfinite/bool-as-number and duplicate keys refuse.
Decimal arithmetic/enclosures, not a binary-float stringify roundtrip, prepare hashed numbers.
Very large decimal expansions count against caps and refuse before allocation when out of range.
JSON booleans are permitted only on named boolean leaves, not numeric ones.

- **Raw file SHA-256** covers exact input bytes including line endings/BOM/whitespace. The request
  binds qa.json and every declared input by raw hash, even when semantically identical JSON would
  canonicalize equally. CSV is hashed unchanged; its exact schema/joins remain §12.5.
- **request_hash** covers canonical bytes of the whole request object (§17.3), without a wrapper
  or self-hash field. Includes run_id, project, qa_hash, every dependency descriptor/hash,
  resolved reference snapshots, required IDs/metrics/schedule/batches/frame/tolerances/methods,
  certificate and prior receipts/replay bindings. Excludes only things not in its closed schema:
  timestamps, random/nonces, runtime snapshots/session/native handles, output paths, response
  bytes, generated batch script hashes and request_hash itself. No extra exclusion list.
- Reference snapshots/config fragments are **deep exact copies** of the approved §§11–12
  leaves after strict loading, not reconstructed from generated geometry. Sort dependencies by
  file, references by id, targets/checks/samples/observations by id, foreign-key tuples by their
  complete tuple, receipt refs by their dereferenced (stage,pass_index,sha256), metric descriptors by id. Preserve coordinate
  order, section traversal, CSV header, and sequence-sensitive relation arrays. Sort set arrays
  lexicographically; duplicates refuse. Batch records stay ordinal order.
- Infer complete observation rows, sort by observation ID, partition consecutively into the
  **largest prefix** meeting selected row limit and certified worst-case response/work bounds;
  ties never reorder. Each row has a certificate-bound cost/size upper, including nested metric
  sets and guards. A row too large for one batch refuses before emit; no splitting hidden inside
  a row. Adaptive landmark evaluations use preplanned refinement slots with stable trace paths;
  all potential slot batches count toward call/time caps, unused slots explicitly close as unused
  trace records, never pretend missing required observations. Final landmark rows are still required.
  Collection order is guard-only baseline batch, then sorted NURBS-CENSUS observation batches
  (including committed-representation binding), initialization and K possible localization slots in sample-ID order,
  then sorted final observation partitions. Each localization replacement can emit one TRACE with
  ≤10 new/cached evaluation slots; no unbounded loop hidden in a row. Analytic arc refinements run
  offline in assess and consume no MCP calls. Guard-only batches have zero data rows but complete
  START/END and explicit kind=guard; they are not zero-observation mandatory checks. Guard cost
  is the full scoped census/transform set, accounted in **every** batch. Batch order respects these
  fixed dependency phases, then IDs; there is no runtime-dependent re-partitioning.
- Batch source is deterministic from request_hash + batch plan + explicit local_session_id from
  bound receipts + approved emitter template. It echoes that local label, never a server token.
  Its SHA is over **exact UTF-8 script bytes** (LF, one final LF). Context adds these hashes after
  request hashing; source embeds request_hash/run_id/batch_id but **not its own or context hash**.
  Collector records invocation-script SHA independently. Context hash covers all its canonical
  bytes without a self-hash field. This is acyclic: inputs→request→scripts→context→capture→report.
- Receipt, calibration certificate, raw capture and report SHA cover exact saved artifact bytes;
  semantic fingerprints (units/frame/census/transforms) cover their canonical record bytes.
  Raw response SHA is separately over exact response bytes, **not** extracted text or normalized
  JSON. Hashes prove byte binding, not server attestation or execution by themselves.

Same approved inputs/certificate/prior receipts/template/caps and run_id yield identical request,
scripts and context. Run-id grammar is `^[a-z0-9][a-z0-9_-]{0,63}$`, user supplied; no slash/dot,
timestamp generation or random token. A local run-directory collision refuses rather than
overwriting. Read-only reproduction in memory for comparison is allowed; new execution needs a
new locally unused run ID. Artifact placement recommendation remains §5.5 outside pipeline;
atomic publication/ownership implementation is U21, not done here.

### 17.2 Shared closed records: binding, guards, metrics and evidence links

Container aliases (reuse by embedding, never copy leaf definitions): `FileBind` = object;
`Guard` has units/frame plus scoped census/transforms arrays; `Metric` discriminates numeric,
identity, surface, point, trace and error records. `EvidenceRef` points to one immutable response
and parsed line; `Interval` is a two-number array `[lower,upper]`, ordered and finite. Names and
runtime handles are strings, never executable expressions. Namespace/key compatibility checks
still apply to free runtime labels; error text can contain arbitrary escaped Unicode.
Closed embedding map: request `inputs/receipt_refs/replay_refs` = FileBind arrays;
context `certificate` = FileBind, `receipt_refs/replay_refs/scripts` = FileBind arrays;
receipt `inputs` = FileBind array, `script/library` = FileBind objects, `guard_before/guard_after`
= Guard; wire START/END `guard` = Guard, ROW `metrics` = Metric array, TRACE `metric` = Metric;
raw `request/context/certificate` = FileBind, `geometry_artifacts` = FileBind array,
`parsed_records` = array of `{record,evidence}`
where record reuses wire and evidence reuses EvidenceRef, `optional_attachments[].artifact`
= FileBind iff ATTACHED; report `inputs/receipts/replays/raw_artifacts` = FileBind arrays,
`certificate` = FileBind, `guards` = Guard array in batch START/END order,
`checks[].samples[].evidence` = EvidenceRef array, `optional` reuses optional_attachments records;
certificate `evidence` = FileBind array. No alias adds an unlisted scalar leaf or extension bag.
Report `tolerances/sampling/limits` copy the exact request/§12 objects, and `methods` copies
request.methods; originals are preserved, not only the tolerance of the worst sample. All these
containers are required; arrays can be empty only where their explicit variant permits absence.
receipt shell_decisions is required (empty on non-S3); report guards/foreign_nodes/optional are
required arrays, geometry_artifacts is required empty-or-populated according to analytical scope.

| Shared path | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| FileBind.id | string | R/— | — | Unique stable artifact/dependency identity | Binder | I |
| FileBind.file | string | R/— | — | §11.3 safe relative actual path | Binder | I |
| FileBind.sha256 | string | R/— | bytes digest | SHA of whole raw file | Binder | H |
| FileBind.format | enum | R/— | — | json,csv,ms,raw,certificate,receipt | Reader | V |
| FileBind.spec | string | C/— | — | JSON pipeline spec only; exact envelope identity | Reader | D |
| FileBind.schema_version | string | C/— | — | JSON pipeline spec only; exact 1.0/1.1 | Reader | D |
| Guard.units.system_type | string | R/— | runtime enum | Exact captured label mapped by certificate, not guessed | Unit guard | M |
| Guard.units.system_scale | number | R/— | native ratio | >0, within certificate domain | Unit guard | M |
| Guard.units.cm_per_scene | number | R/— | cm/scene | >0; k*s independently recomputed | Conversion | H/M |
| Guard.units.scene_per_cm | number | R/— | scene/cm | >0; 1/c independently recomputed | Conversion | H/M |
| Guard.units.display_type | string | R/— | metadata | Captured label, never conversion authority | Audit | M |
| Guard.frame.index | integer | R/— | frames | Exact selected_frame, signed integer | Frame guard | M |
| Guard.frame.ticks | integer | R/— | ticks | index*ticks_per_frame, exact | Frame guard | M |
| Guard.frame.ticks_per_frame | integer | R/— | ticks/frame | >0; actual captured rate identity | Frame guard | M |
| Guard.census[].target_id | string | R/— | — | Exact scoped target | Census guard | I |
| Guard.census[].node_names | array strings | R/— | — | Sorted actual exact names; duplicate names ERROR | Census guard | M |
| Guard.census[].node_handles | array strings | R/— | session-local | Bijection to names; not cross-session stable | Census guard | M |
| Guard.census[].subobject_keys | array strings | R/— | session-local | Sorted committed keys; [] for non-NURBS | Census guard | M |
| Guard.transforms[].node_name | string | R/— | — | One per scoped node | Transform guard | M |
| Guard.transforms[].object_transform | array numbers | R/— | mixed | Exactly 12 row-major values: 3 basis rows dimensionless, translation row scene length | Space guard | M |
| Guard.transforms[].parent_handle | string | R/— | session-local | Actual parent handle or exact reserved `NO_PARENT` | Space guard | M |
| Guard.fingerprints.units | string | R/— | digest | SHA canonical units minus display_type | Drift guard | H |
| Guard.fingerprints.frame | string | R/— | digest | SHA canonical frame record | Drift guard | H |
| Guard.fingerprints.census | string | R/— | digest | SHA canonical scoped census | Drift guard | H |
| Guard.fingerprints.transforms | string | R/— | digest | SHA canonical scoped transforms | Drift guard | H |
| Metric.id | string | R/— | — | Exact planned metric key; unique within observation | Metric matching | I |
| Metric.kind | enum | R/— | — | numeric,identity,surface,point,trace,error | Parser | V |
| Metric.quantity | enum | R/— | dimension tag | scalar,length,angle,area,volume,count,identity,domain,transform,point,trace,error | Dimensional dispatch | V |
| Metric.unit | enum | R/— | label | unitless,scene,scene2,scene3,deg,count,param,session,text | Dimensional dispatch | V |
| Metric.space | enum | R/— | space | none,local_scene,world_scene,parameter,session | Space validation | V |
| Metric.values | array numbers | C/— | by quantity/unit | numeric only; arity fixed in planned metric, all finite/nonbool | Assessor | M |
| Metric.labels | array strings | C/— | — | identity only; sorted exact identity set or order per descriptor | Identity checks | M |
| Metric.links | array strings | C/— | session-local | identity only; exact pairing keys, no fabricated pointer | Relation/instance checks | M |
| Metric.subobject_key | string | C/— | session-local | surface/point/trace only; resolved committed object | Surface binder | M |
| Metric.class_label | string | C/— | runtime label | surface only; certified kind-role map | Resolver | M |
| Metric.superclass_label | string | C/— | runtime label | surface only; certified surface discriminator | Resolver | M |
| Metric.role | enum | C/— | — | surface only: design_surface,offset_surface,ancillary | Resolver | H/M |
| Metric.domain_uv | array numbers | C/— | param | surface only; exactly [u0,u1,v0,v1], strict endpoints | Schedule | M |
| Metric.relation_keys | array strings | C/— | session-local | surface only; exact descriptor-ordered parent/rail/section bindings | Resolver | M |
| Metric.geometry_artifact_sha256 | string | C/— | digest | surface only; actual committed representation raw FileBind needed for bounded localization | Independent evaluator | H/M |
| Metric.uv | array numbers | C/— | param | point only; exactly [u,v], within committed domain | Point binding | M |
| Metric.xyz | array numbers | C/— | scene length | point only; exactly 3, world_scene after one transform | Oracle | M |
| Metric.trace_path | string | C/— | — | trace only; root or binary path, exact planned slot | Bounded localization | I |
| Metric.rectangle_uv | array numbers | C/— | param | trace only; 4 endpoints, contained partition rectangle | Trace replay | M |
| Metric.derivative_bounds | array numbers | C/— | cm/param | trace only; [Lu,Lv], ≥0, certified actual surface enclosure | Trace replay | H/M |
| Metric.distance_bounds | array numbers | C/— | cm | trace only; [L,U], 0≤L≤U, independently recomputed | Trace replay | H |
| Metric.trace_state | enum | C/— | — | trace only: split,pruned,terminal,unused | Trace completeness | H |
| Metric.evaluation_ids | array strings | C/— | — | trace only; exact planned E slots, including explicit unused slots | Trace completeness | H/I |
| Metric.evaluation_uv | array of numeric arrays | C/— | param | trace only; actual evaluation [u,v] in ID order, no unused rows | Trace replay | M |
| Metric.evaluation_xyz | array of numeric arrays | C/— | scene length | trace only; actual world_scene [x,y,z] same actual ID order | Trace replay | M |
| Metric.unused_evaluation_ids | array strings | C/— | — | trace only; partitions evaluation_ids with actual evaluations, no overlaps | Trace completeness | H |
| Metric.rectangle_path | string | C/— | — | trace only; root or binary path, actual queue selection, not slot number | Trace replay | H |
| Metric.geometry_artifact_sha256_trace | string | C/— | digest | trace only; same immutable representation binding as surface metric | Trace replay | H/M |
| Metric.actual_eval_used_ids | array strings | C/— | — | trace only; exact ID order for evaluation_uv/xyz, complement of unused IDs | Trace replay | H/I |
| Metric.error_code | enum | C/— | — | error only: API,UNDEFINED,NONFINITE,ROLE,DRIFT,BINDING,EXHAUSTED,WIRE | Error dispatch | M/H |
| Metric.error_text | string | C/— | text | error only; exact nonempty caught message, escaped | Error audit | M |
| EvidenceRef.response_id | string | R/— | — | Exact immutable raw response identity | Provenance | I |
| EvidenceRef.response_sha256 | string | R/— | digest | Raw response bytes SHA | Provenance | H |
| EvidenceRef.batch_id | string | R/— | — | Planned batch ID | Provenance | I |
| EvidenceRef.line_index | integer | R/— | line index | ≥0, includes START as line 0 | Provenance | H |
| EvidenceRef.observation_id | string | R/— | — | Exact planned observation | Provenance | I |
| EvidenceRef.metric_id | string | R/— | — | Exact metric in that observation | Provenance | I |

Surface geometry_artifact_sha256 is required only for analytical/localization targets, forbidden
otherwise; a complete surface census must not invent a snapshot artifact for an unsupported kind.
TRACE on unused replacement slots retains its evaluation/unused ID sets and trace_state=unused;
rectangle_path/rectangle_uv/derivative_bounds/distance_bounds/representation hash are forbidden
when unused, required otherwise. TRACE evaluations are typed Metric arrays, not wire-delivered
assessment conclusions: actual evalPos points are independently re-enclosed from captured
representation in the assessor. A single Metric stores the selected parent rectangle and slot
evaluation points; children's bounds are recomputed, not accepted as unexplained proof text.

Metric tuples are checked against **planned** arities/dimensions: length scene/world_scene or
scene/none for intrinsic dimensions/thickness,
area scene2/none, volume scene3/none, angle deg/none, count count/none, scalar unitless/none,
point scene/world_scene, surface domain/param/parameter, identity session/session, trace cm data
under quantity trace/unit param/space parameter (its named bounds explicitly cm), error text/none.
Transform numeric descriptor has mixed components declared individually by Guard rule; it is
never length-scaled as a whole. New quantity/method/metric tags require design revision, no generic
unknown numeric bag. Runtime class labels are evidence strings, not invented protocol enums.
Required node classes/parents/visibility/renderability/modifiers/baseObject identity and wall solid
occupancy descriptors appear as exact named Metric descriptors in the request, inferred from
§12.3; the `numeric`/`identity` variants cover their scalar/set measurements, not missing schemas.

**Exact metric descriptor generation:** safe metric tags are a literal listed below, optionally
`<tag>_` plus the first 48 hex digits of SHA(key) when a source key is needed. Retain full key in
`expected_labels` for identity records or source selector in the request target; collision refuses.
Units/space/arity follow the closed tuples above. No optional generic result bag is permitted.

| Family | Required descriptors per inferred observation; independent expected data |
|---|---|
| COVERAGE | `binding` identity labels [project,run_id,request_hash,local_session_id]; `batches` identity sorted batch IDs; `observations`/`samples` identity exact non-COVERAGE required sets. Assessor derives these from actual complete raw records/validated replay, then adds the one COVERAGE comparison; no self-count recursion or Max build log |
| CENSUS | `names`,`classes`,`parents` identity records for exact target nodes; key each class/parent pair by node name. `node_count` count token, arity1. Runtime labels must map to the certified source-kind classes; no expected class fabricated from introspection |
| NURBS-CENSUS | `surface_count` count arity1, including exact0 for trim; `subobjects` identity class/role/relations tuples for every committed key; `design` surface record only if census>0, `offset` surface record iff shell_present. Any other point/curve is ancillary and enumerated |
| PLACEMENT | Per node: `bbox` length/world_scene arity6 [xmin,ymin,zmin,xmax,ymax,zmax], `base_pos` length/world_scene arity3, `dimensions` length/none arity3, `rotation` angle/none arity3, `parent` identity. Placement additionally `base_object` identity paired with actual prototype; expected base-Z/rotation/dimensions from independent source/CSV joins. Groups require pivot/parent but no invented solid bbox/dimensions |
| WALLS | Per host/cell/opening: `bbox` as above, `visibility`,`renderability`,`solid_class` identity labels, `volume` scene3/none arity1 on certified solid route; `thickness` scene/none arity1. `occupancy` identity labels key actual solid intervals and independently recomputed cell/opening partition; gap/overlap/active host comparisons remain separate, not labels supplied from JSON |
| FORM | Each required grid/landmark/endpoint: `surface_point` point/world_scene arity3; landmark adds `landmark_position` point comparison to Q and `station` length/world_scene arity1; endpoints add `extent` length/world_scene arity1 against s0/s1. Min-distance is assessor-derived from surface_point and independent barrel oracle, not Max distance text |
| STACK | `modifiers` identity ordered actual class labels per owned node plus `modifier_count` count/none arity1, expected0 on assembly ownership only |
| REPLAY | Per stage/pass: `receipt` identity immutable receipt hash+actual invocation-response hash; `names`,`classes`,`parents` identity sets; per applicable node bbox/dimensions/base_object/stack descriptors as above. Three real pass-specific observations, no single count surrogate |

Count/visibility readings are explicit: count values must be nonbool integer tokens even inside
numeric arrays; identity visibility/renderability labels are exactly `true`/`false` **strings**.
Parent/baseObject pairs use canonical JSON string pairs, not ambiguous colon concatenation.
`expected_labels` for actual-runtime class mappings come from certificate-bound source-kind
mapping; relation count/order/semantic expected source handles are independently resolved in
this session. Missing mapping remains C03-ROLE gate, no default ClassName field in config.
For measured bbox/intervals, `occupancy` key labels encode canonical measured endpoint tuples
and comparisons use quantity-correct intervals, not string equality on rounded numbers. The
WALLS volume identity is assessor arithmetic from actual volumes; only confirmed axis-aligned
solid Box permits bbox product. Foreign visible intersecting solids are listed in `foreign_nodes`
and force owner-review INCOMPLETE for global opening claims, never auto-hidden or deleted.

### 17.3 Request and run context inventories

Request object has the leaves below plus `inputs`, `receipt_refs`, `replay_refs` arrays of FileBind;
`dependencies` exact §12.5 descriptors (including CSV producer/joins);
`references` exact §12.1 reference copies; `targets`, `checks` exact §12.6 inferred target/check
copies; `tolerances`, `sampling`, `limits` exact §12.4/§12.7 copies. No envelope/source timestamp
is synthesized. `observations` is an array with nested `metrics` descriptors; `batches` an array.
Context embeds certificate FileBind, receipt/replay FileBind arrays and script FileBind array.
Observation source is discriminated: `live` requires a wire ROW, `replay` requires the matching
immutable prior pass receipt + raw snapshot, `assessment` is the single COVERAGE observation
computed from these two sources. Only live observations are partitioned into collection batches;
the union over live batch IDs must equal the live expected subset exactly. Replay/assessment
still have mandatory O/S identities and metric comparisons, but are not fabricated Max ROWs.
Report replay EvidenceRefs resolve the original invocation/snapshot raw batch/line IDs, whose
FileBinds must be present; COVERAGE evidence lists all actual source rows. Missing original raw
provenance makes replay INCOMPLETE even if the receipt's node list looks correct.
Required family-method policy IDs are exactly `coverage_sets_v1`, `owned_census_v1`,
`committed_census_v1`, `source_placement_v1`, `box_wall_occupancy_v1`, `finite_barrel_samples_v1`,
`assembly_stack_v1`, `three_pass_replay_v1`, in the §12.3 family order. Certificate descriptor
bindings provide evidenced concrete implementation routes for these fixed policies; an unknown
method is refusal, not plugin dispatch. Enum policy vocabulary does not depend on Max.

| Path (request) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| protocol_version | string | R/— | — | Exact `form_qa_wire_v1` | All runtime readers | V |
| canonicalization | string | R/— | — | Exact form_cjson_v1 | Hashing | V |
| project | string | R/— | — | Exact QA/project identity | Binder | D |
| run_id | string | R/— | — | §17.1 safe supplied token | Local run binder | Q/I |
| qa_hash | string | R/— | digest | SHA exact locked qa.json bytes | Config binding | H |
| profile | string | R/— | — | Exact approved §12.3 profile | Inference | D |
| selected_frame | integer | R/— | frame | Exact QA sampling value | Batch guard | D |
| certificate_sha256 | string | R/— | digest | Approved selected §17.7 certificate raw hash | Precision binding | H |
| emitter_template_sha256 | string | R/— | digest | Approved template bytes, not generated source | Script binding | H |
| methods.arc_solver | string | R/— | — | interval_lipschitz_arc_v1 | Oracle | V |
| methods.landmark_solver | string | R/— | — | interval_committed_surface_v1; structure uses none_v1 | Landmark route | V |
| methods.serializer | string | R/— | — | invariant_decimal_wire_v1, only with certificate | Wire decoder | V |
| methods.factor | string | R/— | — | certified_native_factor_v1 | Converter | V |
| methods.volume | string | R/— | — | box_endpoint_propagation_v1 | Volume gate | V |
| expected_target_ids | array strings | R/— | — | Sorted inferred set, >0 | Coverage | H |
| expected_check_ids | array strings | R/— | — | Sorted independently inferred set, >0 | Coverage | H |
| expected_observation_ids | array strings | R/— | — | Sorted planned set, >0 | Coverage | H |
| expected_sample_ids | array strings | R/— | — | Sorted grid/landmark/replay/record set, >0 | Coverage | H |
| observations[].id | string | R/— | — | O key digest §16.3 | Parser | H/I |
| observations[].check_id | string | R/— | — | Required inferred C ID | Parser | H/I |
| observations[].target_id | string | R/— | — | Exact inferred target ID | Parser | H/I |
| observations[].sample_id | string | R/— | — | S key digest §16.3, including record | Parser | H/I |
| observations[].schedule_label | string | R/— | — | Exact §16.3 label | Scheduler | H |
| observations[].evidence_source | enum | R/— | — | live,replay,assessment; family-compatible variant above | Source binding | V/H |
| observations[].reference_ref | string | C/— | — | FORM only, independent registry reference | Oracle | D |
| observations[].reference_point_cm | array numbers | C/— | world cm | Landmark only; exact 3 source-derived coordinates | Localization | D |
| observations[].metrics[].id | string | R/— | — | Safe deterministic tag from family mapping | Metric matching | H/I |
| observations[].metrics[].kind | enum | R/— | — | Exact Metric variant §17.2 | Parser | V |
| observations[].metrics[].quantity | enum | R/— | dimension | Exact §17.2 tuple | Parser | V |
| observations[].metrics[].unit | enum | R/— | unit | Exact §17.2 tuple | Parser | V |
| observations[].metrics[].space | enum | R/— | space | Exact §17.2 tuple | Parser | V |
| observations[].metrics[].arity | integer | R/— | items | ≥1 for numeric,point; exact typed variant width, zero only explicitly empty identity set | Parser | H |
| observations[].metrics[].expected_labels | array strings | C/— | — | Identity only; exact inferred set/ordered sequence | Identity comparator | H |
| observations[].metrics[].expected_values | array numbers | C/— | canonical by quantity | Numeric/point only; exact independently inferred arity | Numeric comparator | H/D |
| observations[].metrics[].tolerance_ref | string | R/— | by referent | Compatible bundle §12.4, no arbitrary widening | Comparator | D/V |
| observations[].metrics[].method_id | string | R/— | — | Exact certified family-method ID | Assessor | V |
| batches[].id | string | R/— | — | B key digest §16.3 | Collector | H/I |
| batches[].ordinal | integer | R/— | batch index | Contiguous 0..b−1 | Collector | H |
| batches[].kind | enum | R/— | — | guard,trace,observations; fixed dependency order §17.1 | Collector | V/H |
| batches[].observation_ids | array strings | R/— | — | Sorted live partition, [] only guard/trace; full live union exact | Collector | H |
| batches[].trace_slot_ids | array strings | R/— | — | Explicit bounded localization slots, [] for ordinary batch | Collector | H |
| batches[].max_rows | integer | R/— | rows | Exact expected row/slot count, fits cap | Completeness | H |

No request live runtime snapshot is used to make emit deterministic; committed domains/UVs are
observed and expanded by the fixed grid policy in collection. Batch work costs account for that
fixed expansion. Context is deterministic **local expectation**, not a live assertion:

| Path (context) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| context_version | string | R/— | — | Exact form_qa_context_v1 | Binder | V |
| project | string | R/— | — | Request identity | Binder | D |
| run_id | string | R/— | — | Request token | Binder | D |
| request_hash | string | R/— | digest | Canonical request SHA | Binder | H |
| session_binding | string | R/— | — | Exact local_only_v1 | Scope of evidence | V |
| local_session_id | string | R/— | — | User-supplied safe token, same grammar as run_id | Session comparison | Q/I |
| session_limitation | string | R/— | — | Exact `No server attestation; restart/reconnect invalidates local binding` | Report limitation | V |
| selected_frame | integer | R/— | frame | Request value | Frame guard | D |
| library_revision | string | R/— | — | Approved expected revision string, nonempty | Guard | R/D |
| library_sha256 | string | R/— | digest | Actual approved library file bytes | Guard | H |
| library_guard_certificate_sha256 | string | R/— | digest | Certificate with tested C03-LIBRARY guard | Guard | H |
| required_replay_passes | array integers | R/— | pass indices | Exactly [1,2,3] | Replay | V |

If local_session_id is unavailable, stale, or reused after known restart/reconnect, STOP missing
binding. It is a collector-maintained continuity assertion, not a bridge token/credential. The
same request/run/certificate/explicit local session inputs produce identical context; no clock or
random fields. Stage receipt unit/frame tuple supplies expected runtime context, not emit guesses.
Scope guard comparison uses the union of latest complete **stage-owned** snapshots for the
current production build pass, including S5's whole final scoped snapshot. Earlier S2/S3 receipts
bind their own stage outputs/inputs; later expected additions are not drift against a partial
earlier census. For read-only QA, every batch compares the same complete final-scope baseline;
handles/parent relations may not change within that local session. Replay pass baselines are
separate; compare semantic IDs across passes, never carry one pass's handles into another.
Build guard_before/after census may differ by the independently expected owned stage changes;
their **unit/frame** tuple must agree. Read-only QA permits no census/transform change at all.

### 17.4 Stage receipts, library-first guards and three real replays

Receipt object embeds `inputs`/`script`/`library` FileBind (inputs array), `guard_before` and
`guard_after` Guard, plus `nodes` array below. Creation is by the stage owner/collector at an
**actually observed** authorized invocation, never reconstructed by read-only QA from specs.
`build_run_id` may differ from QA run_id but must join context's immutable receipt refs and same
local session/frame/units/owned identities. Missing binding in form profile is **STOP**, not a
receipt fabricated retroactively. Measurement-only legacy_structure_v1 reports its absent build
binding explicitly and cannot claim executed spec-build, replay or form delivery PASS.

| Path (receipt) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| receipt_version | string | R/— | — | Exact form_stage_receipt_v1 | Receipt reader | V |
| project | string | R/— | — | Exact built project | Binder | R |
| build_run_id | string | R/— | — | Safe supplied build token | Binder | R |
| local_session_id | string | R/— | local continuity | Context binding, no server token | Binder | R |
| stage | enum | R/— | — | S2,S3,S5; S4 artifacts are inputs, not fictitious live stage | Replay/receipt | V/R |
| pass_index | integer | R/— | pass | 1..3 rehearsal; exactly 0 for separately executed production build | Replay | R |
| selected_frame | integer | R/— | frames | Exact observed authorized frame | Guard | R/M |
| invocation_response_sha256 | string | R/— | digest | Raw actual tool response bytes | Execution provenance | H |
| invocation_script_sha256 | string | R/— | digest | Independently computed bytes actually sent/fileIn-ed | Execution provenance | H |
| library_revision | string | R/— | — | Tested observed active revision, not just defined global | Guard | M |
| guard_certificate_sha256 | string | R/— | digest | Tested library/receipt mechanism certificate | Guard | H |
| shell_decisions[].source_ref | string | R/— per S3 item | — | Every applicable u_loft source selector, unique | Census | D |
| shell_decisions[].thickness_cm | number | R/— per item | cm | Exact source signed thickness | Census | D |
| shell_decisions[].shell_present | boolean | R/— per item | — | Exact §14.1 canonical decision | Census/library | D |
| nodes[].target_id | string | R/— | — | Actual owned target identity | Census | R/M |
| nodes[].node_name | string | R/— | — | Exact actually enumerated name | Census | M |
| nodes[].node_handle | string | R/— | session-local | Exact observed handle | Binding | M |
| nodes[].class_label | string | R/— | runtime label | Actual measured class | Census | M |
| nodes[].parent_handle | string | R/— | session-local | Actual handle or NO_PARENT | Placement | M |
| nodes[].base_object_key | string | R/— | session-local | Actual read-back base identity, certified route | Instance binding | M |
| executed_owned_names | array strings | R/— | — | Sorted independently enumerated post-invocation names, nonempty | Receipt completeness | M |
| status | enum | R/— | — | COMPLETE,ERROR,INCOMPLETE; COMPLETE only with all guards/END | Receipt consumer | H |

**Library guard FIRST:** before any model delete/create/layer mutation, inspect unit/frame and
owned-name collisions, expected library bytes/revision and a **tested** active capability marker.
`MCP_NURBS_Arch != undefined` is insufficient. C03-LIBRARY (03.7) must prove valid fresh load,
stale definitions with same global name, mismatched file/revision, failed reload and collision
controls; calibrated authorized build may reload approved bytes then re-check before mutation.
Production QA only checks; never reloads/rebuilds to make evidence green. File hash computed
offline binds invoked file bytes; active-definition identity needs the tested marker route, not
fictitious transport introspection. No tested guard/capability route → STOP binding incomplete.

**Replay:** three distinct real S2→S3→S5 executions in an approved rehearsal, each with its own
invocation raw response, stage receipt, independently enumerated snapshot and quantity/identity
comparisons. Each pass records actual nodes after that pass; do not duplicate one response three
times. Cross-pass handles may legitimately change; compare semantic owned identities and
quantities, plus within-pass baseObject links. Inputs/script/library/frame/unit identity must match
across passes. Prior rehearsal refs in production QA are valid only for the identical approved
input/script/library/certificate contract; no production mutation is authorized by replay inference.
Without valid three-pass evidence the required replay check is INCOMPLETE. Foreign nodes are
reported separately and never renamed/deleted/rescaled; collisions refuse before build mutation.

### 17.5 Wire records, START/END and immutable capture

**Exact wire grammar:** UTF-8 JSON Lines; one complete `form_cjson_v1` JSON object per line,
each followed by LF, no BOM/CR/blank lines/comments/preamble/suffix. Line 0 is START; then
exactly expected ROW/TRACE records in planned order; final line END. No nested serialized
JSON blobs as strings. Explicit canonical identity-key strings in Metric.labels remain allowed;
their decoded array arity is validated under the planned descriptor. Strings use §17.1 escaping;
enums case-sensitive, no aliases. ROW's `metrics`
array embeds §17.2 Metric, sorted by metric id; error variant never masquerades as numeric zero.
START/END embed Guard snapshots of the whole scoped target set. Top-level kinds are
START,ROW,TRACE,END only. TRACE holds one Metric trace plus its planned slot identity.
For lexical numbers accept only the canonical decimal forms in §17.1 (no exponent, plus sign,
leading-zero integer, trailing fractional zero or negative zero). Strings must roundtrip to the
same canonical escaped bytes; field order must equal canonical sorted-key order. Collection
grammar is deliberately stricter than general JSON input. Numeric type/arity and integral count
constraints apply after parsing, independently of token spelling. Error text uses the same escaping.

| Path (wire record) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| kind | enum | R/— | — | START,ROW,TRACE,END | Parser | V |
| protocol_version | string | R/— | — | form_qa_wire_v1, every record | Parser | V |
| project | string | R/— | — | Exact request project | Binding | D |
| run_id | string | R/— | — | Exact request run ID | Binding | D |
| request_hash | string | R/— | digest | Exact canonical request hash | Binding | H/D |
| batch_id | string | R/— | — | Exact planned B ID | Binding | D |
| local_session_id | string | R/— | — | Expected local continuity label, not server attestation | Binding | D/M |
| expected_rows | integer | C/— | rows | START/END only; exact planned count including trace slots | Completeness | D |
| observed_rows | integer | C/— | rows | END only; actual count excluding START/END | Completeness | M |
| observed_observation_ids | array strings | C/— | — | END only; exact sorted complete ROW IDs | Completeness | M |
| observed_trace_slot_ids | array strings | C/— | — | END only; exact planned slots including explicit unused | Completeness | M |
| status | enum | C/— | — | END only: COMPLETE,ERROR,INCOMPLETE | Completeness | M/H |
| observation_id | string | C/— | — | ROW only; exact expected O ID | Identity matching | D |
| check_id | string | C/— | — | ROW only; exact expected C ID | Identity matching | D |
| target_id | string | C/— | — | ROW only; exact expected target | Identity matching | D |
| sample_id | string | C/— | — | ROW only; exact expected S ID | Identity matching | D |
| trace_slot_id | string | C/— | — | TRACE only; exact bounded planned slot | Trace replay | D |

Before START and immediately before END, collector measures unit tuple, frame/ticks, whole scoped
census and objectTransform fingerprints; guarded reads also bracket each target evaluation.
START/END/unit/frame/census/transform drift anywhere invalidates the **entire run**, retained raw,
report INCOMPLETE with DRIFT reason (malformed/forged bindings ERROR). Display-only changes are
recorded but excluded from conversion fingerprint. No script asserts continuous observation
between calls; local sequential continuity is the explicit limitation. Unknown runtime enum refuses
through certificate validation; wire policy enums themselves are fixed here, not future guesses.

**Scalar production MUST CALIBRATE 03.4:** recommend a .NET invariant-culture decimal/roundtrip
serializer for the **actual runtime scalar type** with direct sign/magnitude/locale controls and
explicit JSON escaping, preserving enough digits under a measured bound. The concrete callable
Max/.NET conversion and format precision are deliberately not asserted. Do not call
`formattedPrint` (known fatal route), rely on locale `as string`, or q6 a unit factor. If chosen
route cannot produce this grammar and bounds, return to design; no certified response exists yet.

Raw capture object embeds request/context/certificate FileBind, `responses` array with exact
tool envelope preservation, normalized parsed records array, and optional attachment FileBind.
Normalization is an additional artifact, never replacement evidence. Envelopes are opaque raw
bytes with exact tool input/output—including success/error/result/metadata fields—retained;
do not project only known envelope keys and lose unknown tool data. Capture format below is
closed around that byte payload. `base64` is RFC4648 standard padded encoding, no whitespace.

| Path (raw capture) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| capture_version | string | R/— | — | form_qa_capture_v1 | Capture reader | V |
| project | string | R/— | — | Request project | Binder | D |
| run_id | string | R/— | — | Request token | Binder | D |
| request_hash | string | R/— | digest | Canonical request | Binder | H |
| context_hash | string | R/— | digest | Canonical context | Binder | H |
| local_session_id | string | R/— | — | Observed collector continuity label | Binder | M |
| responses[].id | string | R/— | — | Unique exact response ID tied to batch | Provenance | I |
| responses[].batch_id | string | R/— | — | Planned B ID | Binder | I |
| responses[].tool_name | string | R/— | — | Exact 3dsmax-mcp_execute_maxscript for quantitative collection | Tool audit | M |
| responses[].tool_input_base64 | string | R/— | raw bytes | Complete actual input envelope bytes | Invocation audit | M |
| responses[].response_base64 | string | C/— | raw bytes | Required if response received; complete raw envelope bytes, not just result string; absent on no-response timeout | Immutable audit | M |
| responses[].response_sha256 | string | C/— | digest | Required iff response bytes present; SHA decoded raw bytes, never hash invented timeout response | Immutable audit | H |
| responses[].response_byte_count | integer | C/— | bytes | Required iff response bytes present; exact decoded length >0; cap violation retained/error | Completeness | H |
| responses[].script_sha256 | string | R/— | digest | Exact actual script bytes match context FileBind | Invocation audit | H |
| responses[].started_at | string | R/— | UTC ISO-8601 | Collector timestamp; raw only, never request | Timing audit | M |
| responses[].elapsed_seconds | number | R/— | s | ≥0 monotonic duration, within caps or explicit exhaustion | Operational guard | M |
| responses[].tool_success | boolean | C/— | — | Exact envelope field if present; absence recorded, never defaults true | Error check | M |
| responses[].transport_status | enum | R/— | — | RETURNED,TIMEOUT,DISCONNECTED,TRUNCATED | Error check | M |
| responses[].error_text | string | C/— | text | Required for detected error, exact source text | Error audit | M |
| responses[].wire_text_sha256 | string | C/— | digest | Exact decoded result text UTF-8, if extractable; separate from envelope SHA | Parser provenance | H |
| responses[].parsed_status | enum | R/— | — | COMPLETE,ERROR,INCOMPLETE | Completeness | H |
| foreign_nodes[].node_name | string | R/— | — | Exact observed foreign name, outside scoped ownership | Scope audit | M |
| foreign_nodes[].node_handle | string | R/— | session-local | Exact observed handle, never cleanup authority | Scope audit | M |
| foreign_nodes[].visible_intersection | enum | R/— | — | YES,NO,UNKNOWN based on certified read-only route | Wall scope limitation | M/H |
| optional_attachments[].capture_id | string | R/— | — | Exact configured optional ID | Attachment join | I |
| optional_attachments[].status | enum | R/— | — | ATTACHED,NOT_RUN,ERROR | Attachment report | H/M |
| optional_attachments[].reason | string | C/— | text | Required if NOT_RUN/ERROR | Attachment report | M |

`parsed_records` reuses the entire wire schema, with response_id/line_index supplied by
EvidenceRef, not edited rows. Optional attachment artifact bindings use FileBind when ATTACHED.
At future collect, actual raw-byte access must be calibrated by **C03-RAW (03.4/03.7)**; if tool
only exposes an already-decoded object, do not hash a reserialization as “raw response bytes”.
Retain that object with explicit limitation but core raw-byte binding is INCOMPLETE until the
approved collector route can capture exact bytes. No Python pipe/TCP client or new transport is
proposed. Byte hashes are honest local capture, not invented bridge-signed envelopes.

Inspect the **whole** envelope/text for tool errors and `__MCP_MS_ERR__`, even when success:true.
Timeout/disconnect/truncation/missing END → INCOMPLETE; explicit exception/error/sentinel,
invalid grammar/quantity/space/identity/bool/nonfinite → ERROR. A malformed END is not COMPLETE.
Never edit raw to repair a response or retry into the same batch identity; revised collection gets
a fresh run ID. Parse caps before unbounded allocation. Nested arrays must have exact arity;
missing length/coordinate/label is never zero, `undefined` never [0,0,0].

### 17.6 Assessment report inventory

Report embeds input/receipt/replay/certificate/raw FileBind arrays, actual START/END Guard
snapshots, `checks` array, `optional` attachment statuses and EvidenceRef arrays. Report-level
`foreign_nodes` copies the raw inventory. Every check has sorted `samples` (record/replay labels
included); the FORM variant has `form_summary` and
coverage arrays. Interval arrays are lower/upper numerical enclosures, not pairs of best guesses.
Original physical tolerances and copied request methods are retained unchanged.

| Path (report) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| report_schema | string | R/— | — | form_qa_results_v1 | Report reader | V |
| protocol_version | string | R/— | — | form_qa_wire_v1 | Report reader | D |
| project | string | R/— | — | Request identity | Binder | D |
| run_id | string | R/— | — | Request token | Binder | D |
| local_session_id | string | R/— | — | Context/capture agree | Binder | M/D |
| session_limitation | string | R/— | — | Exact context limitation, preserved | Handoff | D |
| request_hash | string | R/— | digest | Canonical request SHA | Binder | H |
| context_hash | string | R/— | digest | Canonical context SHA | Binder | H |
| qa_hash | string | R/— | digest | Exact current locked QA bytes match request | Binder | H |
| raw_hash | string | R/— | digest | Exact immutable whole capture artifact bytes | Binder | H |
| profile | string | R/— | — | Approved unchanged profile | Aggregator | D |
| selected_frame | integer | R/— | frames | Request and all guards agree | Aggregator | M/D |
| binding_status | enum | R/— | — | COMPLETE,MISSING,INVALID | Receipt binding | H |
| status | enum | R/— | — | PASS,FAIL,ERROR,INCOMPLETE | Handoff | H |
| form_claim | enum | R/— | — | sampled_conformance or FORM NOT SPECIFIED | Handoff | V/H |
| limitations | array strings | R/— | text | Includes sampling, local binding and unsupported/inapplicable methods | Handoff | H |
| expected_check_ids | array strings | R/— | — | Independently inferred sorted set | Coverage | H |
| observed_check_ids | array strings | R/— | — | Actual parsed sorted set | Coverage | H |
| compared_check_ids | array strings | R/— | — | Actually compared sorted set | Coverage | H |
| checks[].id | string | R/— | — | Exact required C ID | Coverage | I |
| checks[].family | string | R/— | — | Exact §12.3 family | Comparator | D |
| checks[].target_id | string | R/— | — | Exact required target | Comparator | D |
| checks[].method_id | string | R/— | — | Exact certified selected method | Comparator | D |
| checks[].status | enum | R/— | — | PASS,FAIL,ERROR,INCOMPLETE | Aggregator | H |
| checks[].reason_codes | array strings | R/— | — | Closed Metric error codes plus COVERAGE,TOLERANCE,NOT_BOUND | Handoff | H |
| checks[].n_expected | integer | R/— | comparisons | Inferred >0 for applicable mandatory check | Coverage | H |
| checks[].n_observed | integer | R/— | comparisons | Actual count, ≥0 | Coverage | H |
| checks[].n_compared | integer | R/— | comparisons | Actual count, ≥0; no invented comparison | Coverage | H |
| checks[].expected_ids | array strings | R/— | — | Exact sorted canonical JSON string keys [observation_id,sample_id,metric_id] | Coverage | H |
| checks[].observed_ids | array strings | R/— | — | Actual same triple keys, duplicate diagnostic retained raw | Coverage | H |
| checks[].compared_ids | array strings | R/— | — | Actually compared same triple keys | Coverage | H |
| checks[].tolerance_ref | string | R/— | — | Exact unchanged §12.4 bundle | Comparator | D |
| checks[].samples[].sample_id | string | R/— | — | Exact required S ID | Provenance | I |
| checks[].samples[].observation_id | string | R/— | — | Exact required O ID | Provenance | I |
| checks[].samples[].metric_id | string | R/— | — | Exact planned metric | Provenance | I |
| checks[].samples[].expected_values | array numbers | C/— | canonical by quantity | Numeric/point comparisons, exact arity | Comparator | D/H |
| checks[].samples[].observed_values | array numbers | C/— | canonical by quantity | Actual converted nominal values, finite/exact arity | Comparator | M/H |
| checks[].samples[].expected_labels | array strings | C/— | — | Identity comparison only | Comparator | H |
| checks[].samples[].observed_labels | array strings | C/— | — | Identity comparison only | Comparator | M |
| checks[].samples[].error_interval | array numbers | C/— | canonical by quantity | Numeric/point only; [L,U], 0≤L≤U | Comparator | H |
| checks[].samples[].tolerance | number | C/— | same as error | Numeric/point only; exact original approved tolerance | Comparator | D |
| checks[].samples[].unit | enum | R/— | label | cm,deg,m2,cm2,cm3,count,unitless,session | Dimensional audit | H/V |
| checks[].samples[].status | enum | R/— | — | PASS,FAIL,ERROR,INCOMPLETE | Aggregator | H |
| checks[].samples[].solver_bracket_cm | array numbers | C/— | cm | FORM/localization only; nominal certified [L,U] | Uncertainty audit | H |
| checks[].samples[].solver_iterations | integer | C/— | replacements | Solver rows only; ≥0, actual count | Exhaustion audit | H |
| checks[].samples[].solver_trace_sha256 | string | C/— | digest | Solver rows only; immutable replayable full trace bytes | Bound audit | H |
| checks[].samples[].numerical_components | array numbers | C/— | same as error | Numeric only; [wire,factor,arithmetic,solver] bounds, explicit zeros only if certified | Uncertainty audit | H |
| checks[].form_summary.max_cm | array numbers | C/— | cm | FORM only; [max Li,max Ui] over required distance samples | Max gate | H |
| checks[].form_summary.mean_cm | array numbers | C/— | cm | FORM only; [sum Li/N,sum Ui/N], outward | Summary only | H |
| checks[].form_summary.rms_cm | array numbers | C/— | cm | FORM only; [sqrt(sum Li²/N),sqrt(sum Ui²/N)], outward | Summary only | H |
| checks[].form_summary.worst_sample_id | string | C/— | — | FORM only; largest upper, tie lexicographic ID | Handoff | H |
| checks[].form_summary.claim | string | C/— | — | FORM only; exact sampled_conformance | Handoff | V |
| checks[].form_summary.coverage_grid_ids | array strings | C/— | — | FORM only; exact 25 required IDs | Coverage | H |
| checks[].form_summary.coverage_landmark_ids | array strings | C/— | — | FORM only; exact nine station IDs | Coverage | H |
| checks[].form_summary.coverage_endpoint_ids | array strings | C/— | — | FORM only; exact two endpoint IDs | Coverage | H |

For missing evidence, omit unavailable numeric C fields and keep ERROR/INCOMPLETE plus reason
and expected identities; never manufacture zero summaries. FORM summaries require all 36
distance samples; missing samples forbid a “complete” max. Landmark/extent position errors are
additional metrics, not mixed into a mean distance with incompatible units. Global status precedence:
ERROR for malformed/binding/identity failures; otherwise INCOMPLETE for drift/missing/exhaustion;
otherwise FAIL if any required comparison fails; PASS only with every mandatory check complete
and passing. Retain all diagnostic FAILs even when overall ERROR/INCOMPLETE wins. Optional
NOT_RUN is separate. Structure-only reports always say **FORM NOT SPECIFIED**; measurement-only
structure evidence with missing build/replay binding cannot be advertised as a delivery PASS.

### 17.7 Evidence-bound calibration certificate inventory

Proposed separate **non-spec** certificate object, selected explicitly by local emit input context
(future CLI wiring is U20/U22, not guessed now). `methods`, `domains`, `bounds`, `controls` are
closed objects/arrays below; `evidence` array uses FileBind. Certificate bytes bind transcripts,
runtime/route revisions and numerical proof obligations; it does not grant A-LIVE or A-TOL.
Certificate `surface_maps/descriptors` are required arrays with exact leaves below, sorted by
(source_kind,role) and descriptor id; proof/control bindings must cover every supported entry.

| Path (certificate) | Type | Required/default | Units | Range/constraint | Consumer | Origin |
|---|---|---|---|---|---|---|
| certificate_version | string | R/— | — | form_precision_calibration_v1 | Certificate reader | V |
| id | string | R/— | — | Safe unique evidence certificate ID | Binder | I |
| state | enum | R/— | — | CALIBRATED,UNSUPPORTED; only first usable | Ready gate | H |
| owner_gate | string | R/— | — | Exact approved phase03 gate record locator | Authorization trace | R |
| runtime_version | string | R/— | — | Actual Max/runtime version, nonempty | Domain guard | M |
| library_revision | string | R/— | — | Exact tested active revision | Guard | M |
| library_sha256 | string | R/— | digest | Exact tested source bytes | Guard | H |
| collector_revision_sha256 | string | R/— | digest | Actual tested collector/serializer source bytes | Capture guard | H |
| methods.serializer | string | R/— | — | invariant_decimal_wire_v1 plus evidenced route | Wire | V/H |
| methods.scalar_route | string | R/— | text | Exact tested callable/type/format/locale recipe, never config source code | Emitter calibration | M |
| methods.factor_route | string | R/— | text | Exact tested positive unit read/serialization/enclosure route | Units | M |
| methods.frame_route | string | R/— | text | Exact tested frame↔ticks/read-back route | Frame guard | M |
| methods.surface_route | string | R/— | text | Exact tested commit/class/relations/domain/world route | Resolver | M |
| methods.landmark_route | string | R/— | text | Exact tested read-only independent bounded representation route; UNSUPPORTED explicit | Landmark | M |
| methods.library_guard_route | string | R/— | text | Exact tested stale/reload/capability/receipt mechanism | Guard | M |
| methods.raw_capture_route | string | R/— | text | Exact actual byte-capture route, not object reserialization | Capture | M |
| methods.volume_route | string | R/— | text | Tested Box assumptions or separately approved mesh mechanism | Volume | M |
| methods.arithmetic_proof_sha256 | string | R/— | digest | Immutable outward arithmetic/transcendental enclosure proof+controls | Solver bounds | H |
| domains.unit_types[].runtime_enum | string | R/— | runtime enum | Actual probed exact spelling, unique | Unit mapper | M |
| domains.unit_types[].cm_per_base | number | R/— | cm/base | Exact mathematical constant after actual enum mapping | Unit mapper | H/M |
| domains.system_scale_range | array numbers | R/— | ratio | 2 finite positive endpoints; certified domain only | Guard | H/M |
| domains.max_abs_world_scene | number | R/— | scene length | >0; actual proven magnitude ceiling | Wire/space guard | H/M |
| domains.max_abs_local_scene | number | R/— | scene length | >0; actual local evalPos and representation control-point ceiling | Transform proof | H/M |
| domains.max_object_basis_norm | number | R/— | ratio | >0; proved matrix operator-norm ceiling, includes parent/nonuniform scale | Transform proof | H/M |
| domains.max_object_translation_scene | number | R/— | scene length | >0; measured/proved translation magnitude ceiling | Transform proof | H/M |
| domains.max_abs_parameter | number | R/— | param | >0; actual domain/evaluation magnitude ceiling, not length | Localization proof | H/M |
| domains.max_abs_world_cm | number | R/— | cm | >0; coordinate ceiling including transforms | Numerical guard | H/M |
| domains.max_abs_angle_deg | number | R/— | deg | >0; captured angle domain | Angular guard | H/M |
| domains.max_abs_volume_cm3 | number | R/— | cm³ | >0; aggregate ceiling, not geometry allowance | Numeric guard | H/M |
| domains.max_aggregate_terms | integer | R/— | terms | >0; actual sum/product enclosure scope | Volume guard | H/M |
| domains.surface_kinds | array strings | R/— | — | Tested supported kind-role/landmark set; never inferred all | Resolver gate | H/M |
| surface_maps[].source_kind | string | R/— | — | Exact §16.1 tested source kind; unique (kind,role) | Resolver | V/H |
| surface_maps[].class_label | string | R/— | runtime label | Exact executed read-back class, not introspection guess | Resolver | M |
| surface_maps[].superclass_label | string | R/— | runtime label | Exact executed superclass discriminator | Resolver | M |
| surface_maps[].role | enum | R/— | — | design_surface,offset_surface,ancillary | Resolver | V/H |
| surface_maps[].relation_slots | array strings | R/— | — | Actual tested property-slot labels in documented order; [] only if no relations | Relation guard | M |
| descriptors[].id | string | R/— | — | Exact unique policy family+metric/work class ID | Certificate scope | I |
| descriptors[].family | string | R/— | — | Eight §12.3 families or exact guard/localization work class | Method scope | V |
| descriptors[].method_id | string | R/— | — | Fixed family policy IDs §17.3; guard=runtime_fingerprints_v1, localization=interval_committed_surface_v1 | Assessor/batcher | V |
| descriptors[].route | string | R/— | text | Exact tested read-only mechanism and source revision locator, evidence-bound | Runtime route | M |
| domains.ticks_per_frame | integer | R/— | ticks/frame | >0; exact tested frame-rate domain | Frame guard | M |
| bounds.solver_distance_cm | number | R/— | cm | >0 approved solver bracket target; no certified guarantee of completion under cap | Solver stop | Q/H |
| bounds.wire_length_cm | number | R/— | cm | ≥0 proved route+domain serialization/world capture bound | Converter | H |
| bounds.wire_angle_deg | number | R/— | deg | ≥0 proved angular serialization bound | Converter | H |
| bounds.unit_factor_relative | number | R/— | ratio | 0≤rho<1 proved factor error bound | Converter | H |
| bounds.volume_roundoff_cm3 | number | R/— | cm³ | ≥0 proved aggregate arithmetic/read-back bound | Volume interval | H |
| bounds.solver_arithmetic_cm | number | R/— | cm | ≥0 enclosures for distances/trig/bound evaluation in domain | Solver interval | H |
| bounds.landmark_arithmetic_cm | number | R/— | cm | ≥0 actual-surface localization enclosure contribution | Localization | H |
| bounds.max_rows_per_batch | integer | R/— | rows | >0 tested operational envelope, not blanket 25 claim | Batcher | H/M |
| bounds.max_batch_seconds | number | R/— | s | >0 calibrated bounded-work ceiling, below 2 s and stop-growth near 1 s | Collector | H/M |
| bounds.max_response_bytes | integer | R/— | bytes | >0 tested complete-capture envelope limit | Parser | H/M |
| bounds.row_cost_seconds | array numbers | R/— | s/descriptor | >0 per named descriptor class; order in control descriptors | Batcher | H/M |
| bounds.row_size_bytes | array integers | R/— | bytes/descriptor | >0 per same class, worst-case guards/escaping/trace included | Batcher | H/M |
| controls[].id | string | R/— | — | Unique named calibration control | Certification | I |
| controls[].gate_id | string | R/— | — | C03-* gate in §18.1 | Certification | V |
| controls[].descriptor_ids | array strings | R/— | — | Exact certified family metric/work descriptors, aligns cost arrays | Batcher | H |
| controls[].evidence_sha256 | string | R/— | digest | Actual immutable transcript/raw FileBind digest | Certification | H |
| controls[].result | enum | R/— | — | HIT,MISS,BOGUS_REJECTED,BOUND_CONFIRMED,UNSUPPORTED | Certification | M/H |
| controls[].interpretation | string | R/— | text | Actual measured result and bounded-domain/proof limit | Review | H |

No invented numeric values populate this certificate during 02.2. A finite set of observed errors
alone cannot certify a supremum: the mathematical/type-rounding enclosure proof and measured
route/type/locale/magnitude controls must agree. Missing proof, raw transcript, authorization,
supported enum/kind, bound or tested guard → certificate unusable; emit/assess refuse readiness.
Per gate, require at least one HIT, one MISS (or correct bounded negative) and one
BOGUS_REJECTED control; BOUND_CONFIRMED additionally requires the referenced proof, not just
setter readback. Costs/sizes are indexed by the sorted union of distinct controls.descriptor_ids;
both arrays have that exact arity. Every scheduled descriptor needs a bound; arbitrary free
interpretation text cannot introduce an unlisted numeric parameter.

## 18. PROPOSED numerical certification and operational bounds

### 18.1 Freeze method first; bind evidence afterwards — no circular prerequisite

**U03–U06/U15–U19:** 02.4 can approve the **exact schemas, algorithms, refusal rules and gate
ownership** without asserting live precision values. No requirement to obtain a live certificate
before approving design or authorizing phase03. After A-LIVE, the phase03 coordinator owns
calibration transcripts and certificate authoring; the user/QA numerical-policy owner explicitly
reviews the evidence-bound values at **C03-CERT**. This later binding gate may choose only
measured/proved values within the frozen methods; any new field, algorithm, consumer or tolerance
change returns to design approval. A method failure is UNSUPPORTED, not a convenient replacement
default. 02.4 FREEZE is a contract approval; C03-CERT is a bounded-domain parameter binding,
**not** an unrecorded scope/physical-tolerance approval. No ready config/implementation use of
certified parameters before this gate. Phase02 still cannot PASS before 02.3/02.4.

| Calibration gate | Exact evidence obligation / owner gate | Absence/failure disposition |
|---|---|---|
| C03-UNITS (03.3) | Exact enums, positive scales, system vs display, c/f physical boxes; known hit/miss/bogus; bounded scale domain | Unknown/custom enum or uncertified scale refuses, never cm fallback |
| C03-WIRE (03.4) | Actual scalar type, invariant locale route, escaping, decimal canonical parse, fraction/sign/large-coordinate/count/NaN/bool/malformed controls, complete START/END | No scalar precision claimed; ERROR grammar or NOT_READY certificate |
| C03-RAW (03.4/03.7) | Actual raw response/input bytes, whole envelope, timing and timeout/sentinel preservation; positive and missing-END controls | No raw-byte access → INCOMPLETE binding, no reserialization substitution |
| C03-SPACE/FRAME (03.5) | Committed domain, local/world evalPos, exactly one objectTransform, parents/pivots/nonuniform transform; ticks_per_frame and negative/positive integer frame controls | Unknown space/frame API → INCOMPLETE, no current-frame/mid-UV assumption |
| C03-ROLE/LANDMARK (03.5) | §16 kind-role census/relations + independently bounded actual-surface localization/trace replay; offset/wrong-role/nonmid-UV controls | Unsupported kind stays required ERROR/INCOMPLETE, no dropped target |
| C03-SHELL (03.6) | Zero/below/equal/above ±.001 cm native mm/m; first-call presence/distance/census; merge/approximation geometry | Equality policy remains recommendation; failed forwarding returns to owner |
| C03-LIBRARY (03.7) | Fresh/stale same-name definitions, bytes/revision/capability marker, reload failure/name collision, stage receipt invocation binding before mutation | No tested guard/receipt → STOP, production QA never repairs |
| C03-NUMERIC (03.4/03.8 + offline proof) | Scalar/factor/transform/distance/trig/sqrt/product/sum outward enclosures, magnitude ceilings, term bounds and solver controls independent of generator | Empirical maximum alone is not a bound; missing proof refuses |
| C03-WORK (03.4/03.5) | Bounded complete descriptors, guard/serialization/trace work and response sizes; grow only below ~1 s, one call below 2 s; no modifier ladders | Unsafe/unknown descriptor cannot be scheduled; no automatic larger call |
| C03-CERT (after required 03 gates) | Coordinator writes actual immutable certificate, user/QA numerical owner approves domain/values/proofs; record digest and evidence locators | No binding record → NOT_READY/refusal, even if A-* design is approved |

Combined table labels abbreviate independently recorded controls: C03-SPACE and C03-FRAME;
C03-ROLE and C03-LANDMARK. Certificate gate_id uses the individual name. No combined row lets
one control stand in for the other. C03-CERT requires all applicable individual gate records.

**Exact certification method:** determine actual scalar representation/type and operation rounding
model with controlled reads, not introspection alone. Establish analytic worst-case enclosures for
conversion/serialization over the declared magnitude/scale/transform domain; demonstrate the
chosen route with known-answer and malformed controls. For offline math use rational interval
arithmetic with outward decimal rounding and rigorous sin/cos/sqrt enclosures (range-reduced
Taylor with bounded remainder, rational π enclosure and sqrt bracketing); plain stdlib sin/cos
nominals may seed upper candidates but cannot supply an undocumented ulp certificate. The proof
artifact fixes precision and range-reduction scheme; C03-NUMERIC binds it before use. No precision
digits, ulp count or Max factor format is fabricated in this design. If finite approved precision
cannot enclose the supported domain within the selected width, INCOMPLETE, not tolerance inflation.

All ready numerical QA leaves equal `bounds.<same_name>` of selected certificate exactly.
`solver_distance_cm` is an explicit approved computational bracket target, not empirical NURBS
accuracy; completion still depends on operation caps. `wire_length_cm` is a certified **world-cm
Euclidean point/endpoint error** over the declared route/transform domain, not an undocumented
per-component error. `wire_angle_deg` bounds angle capture. Factor rho=`unit_factor_relative`
requires 0≤rho<1 and a proof bounding relative deviation of captured c from true c. Use
`c_true∈[c_hat/(1+rho),c_hat/(1−rho)]`; propagate by interval multiplication per length, squared
for area (then /10000 to m²), cubed for volume. Magnitude-dependent errors are not replaced by
a constant cm fudge. Factor proof accounts k*s and reciprocal emission/readback; never q6 c/f.

For surface/world capture, the certificate says which transform/point rounding is already covered
by wire_length_cm, so it is counted **once**, not once per matrix element plus again per point.
Distance's Lipschitz positional error expands solver [L,U] to
`[max(0,L−e_pos),U+e_pos]` with arithmetic enclosure; reference decimal/trig enclosure is explicit
in solver arithmetic, not an unbounded “exact” double. Box extents from two measured endpoints
carry twice endpoint numerical uncertainty; product/aggregate intervals carry c powers and
volume_roundoff once per the certified aggregate/method domain. Physical volume budget remains
§13.1's B, unchanged. `solver_arithmetic_cm`/`landmark_arithmetic_cm` are certificate enclosure
components used internally and reported, not additional physical allowances or QA schema leaves.
All domain ceilings are enforced on **intermediates**, transforms and sums too; exceed → refusal
or INCOMPLETE with actual magnitude, never extending a certificate by extrapolation.

### 18.2 User-selected operation caps: exact policy, no hidden defaults

**U07–U14:** recommend all eight existing §12.7 caps be **explicit QA-owner inputs**, finite,
positive, nonbool with the stated integer/scalar types and recorded Q origins. No automatic value
is selected when absent (including “25”, “2 seconds”, “500 iterations” or a transport default).
Numeric cap choices are not unanswered schema design: the frozen input rule is that the owner
supplies them and readiness refuses if absent. Selection is exact:

| Existing leaf | Selection/validation and exhaustion policy |
|---|---|
| max_rows_per_batch | Owner value must be ≤certificate row ceiling. Partition largest sorted prefix fitting rows **and** sum of certified descriptor work/size plus batch guard overhead. Never auto-clamp a too-large owner value |
| max_targets | Count independent inferred nonproject targets + exactly one project target. Over owner cap → pre-emit refusal; no scope truncation |
| max_samples | Count final sample identities Nfinal plus all potential localization eval slots (11*(5+10K) per form target) plus offline arc eval slots (36*(3+2K) per form target), K=max_solver_iterations. Do not assume co-located reuse to reduce this upper. Over cap → refusal; final comparison denominator uses required final IDs/metrics only; unused internal slots reported separately |
| max_calls | Count every planned quantitative batch, metadata/guard-only call, trace-slot call and configured optional capture call; replay refs are prior runs, not invented current calls. Planned upper >cap → refusal; collector counts actual calls and stops before exceeding |
| max_batch_seconds | Owner value must be <2 s and ≤certificate work ceiling; certified planned work upper must fit. Collector measures elapsed and checks internal progress clock between bounded operations. Overrun stops new calls and run INCOMPLETE; timeout does not prove bridge absence |
| max_total_seconds | Owner value >0; sum certified planned call uppers must fit before emit. Monotonic time from start of first call through final call includes inter-call delays; exceed → INCOMPLETE, preserve completed raw |
| max_solver_iterations | Owner integer bounds §15/§16 rectangle replacements **per sample per solver**. Every adaptive slot/evaluation implied by this cap is accounted before emit; exhaustion INCOMPLETE. No hidden extra iterations to force PASS |
| max_response_bytes | Owner integer must be ≤certificate actual capture ceiling. Worst-case whole envelope+escaped wire/guards/trace for each planned batch must fit. Never clip raw or split lost rows retrospectively; actual oversize/truncation INCOMPLETE |

Guard overhead has its own certified descriptor cost/size, not omitted from the sum; certificate
control descriptor ordering associates cost/size arrays to exact work classes bijectively.
If the upper work/size model or timestamp route is uncalibrated, NOT_READY. No real-time preemption
is promised for Max's main-thread call: cooperative checks plus bounded certified work are the
method; a timeout preserves uncertainty. Time ceilings never imply numerical accuracy. Expensive
localization can legitimately refuse under caps: revise approved batching/caps after evidence,
not omit landmarks. Numerical interval width can remain too large under valid operational caps:
report INCOMPLETE, preserve physical threshold, ask the owner about numerical method/work limits.

## 19. PROPOSED dispositions and 02.2 local document gate

### 19.1 Current U-register with 02.1 history retained

§13.3's 22 pending groups are retained as dated 02.1 history; rows below are the current pointers.
**R = recommended design settled**, **C = exact method/schema settled with explicitly named
calibration gate**. Neither means approved/implemented/measured. All A-* approvals stay OPEN.

| ID | 02.2 disposition | Current policy / remaining evidence gate | Next owner |
|---|---|---|---|
| U01 | R | §14.1 core refuses full360; no closed consumer/API claim | User A-CLOSED/FIELDS at 02.4 |
| U02 | R | §14.1 zero absent, below refuses, equality present; canonical decision forwarded | User A-CLOSED; later C03-SHELL |
| U03 | C | §15 exact finite oriented interval solver/bracket/exhaustion; §18 arithmetic proof + certificate binds selected width | C03-NUMERIC/CERT |
| U04 | C | §17 wire grammar exact; actual invariant serializer/raw bytes and certified wire bounds | C03-WIRE/RAW/NUMERIC/CERT |
| U05 | C | §18 c/f relative enclosure, no q6; exact enum/scales and proof-domain values not guessed | C03-UNITS/NUMERIC/CERT |
| U06 | C | §§13/18 physical cm³ vs numeric aggregate enclosure separated | C03-NUMERIC/CERT; 03.8 if mesh route needed |
| U07 | C | §18 explicit row cap, deterministic work-aware partition; 25 not certified | C03-WORK/CERT plus QA owner cap |
| U08 | R | §18 explicit max_targets, inferred count, absence/exceed refuses | QA owner |
| U09 | R | §§16/18 exact 36 form identities + other required records; explicit cap | QA owner |
| U10 | R | §18 all planned call upper including guards/trace/captures, explicit cap | QA owner |
| U11 | C | §18 explicit <2s and certified work limit, measured overrun invalidates | C03-WORK/CERT plus QA owner cap |
| U12 | R | §18 explicit total cap, exact monotonic interval, no partial PASS | QA owner |
| U13 | R | §§15/16 one replacement per iteration, explicit per-sample limit | QA owner; solver arithmetic C03-NUMERIC |
| U14 | C | §§17/18 full raw-envelope size, explicit cap, no truncation; measured capture route | C03-RAW/WORK/CERT |
| U15 | C | §16 actual-domain grid + independent bounded landmark localization; never midUV assumption | C03-SPACE/LANDMARK/CERT |
| U16 | C | §16 kind-role census/relations, trim0 unsupported form target; ambiguity ERROR | C03-ROLE/CERT |
| U17 | C | §17 explicit signed frame, ticks=index*ticks_per_frame, drift guards | C03-FRAME/CERT |
| U18 | C | §§16–18 exact ID/enums/hash/wire/report inventory; serializer/arithmetic/raw mechanisms need evidence | C03-WIRE/RAW/NUMERIC/CERT |
| U19 | C | §17 local-only session/actual receipt/library-first/three real replays; no token or retrospective receipt | C03-LIBRARY/RAW/CERT, phase12 replay |
| U20 | PENDING 02.3 | Contextual inventory API + exact calibration-input CLI integration (§17.7), no guessed flag | 02.3 |
| U21 | PENDING 02.3 | Atomic publication/ownership/migration/prior registry/wall representation | 02.3 |
| U22 | PENDING 02.3 | Fixture/recipe/adaptive regen locations and explicit future CLI owners | 02.3 |

Totals: **7 R + 12 C = all 19 groups assigned exact proposals or named evidence gates**;
**3 pending groups remain for 02.3**. No truly unanswered **02.2 design choice** remains; ready
numeric values are intentionally selected by QA owner or evidence-bound C03-CERT, not unspecified
defaults. The exact user questions are still §4's OPEN approval package (including “approve core
full360 refusal and shell equality-present?”); U20–U22 add their explicit §13.3 questions at 02.3.
If user rejects a recommendation, reopen that named group; continuation never closes an A-* row.

### 19.2 Local 02.2 gate — saved document checks, not execution evidence

**02.2 design coverage reviewed / DRAFT / NOT FROZEN. No phase-02 PASS.** Exclusive write
ownership was `references/_form-units-qa-design.md` only; root plan §§5.3–5.5/6.2/7/9–11/13
and saved 1240-line design were read. Source reads of build_nurbs census/dependent emission and
library closure/loft identify source compatibility only. Existing §§1–13 history is retained with
status/navigation pointers, §13.3 marked historical, and §13.4 authorization wording narrowly
corrected. No schemas outside this file, G allocations or implementation are changed.

**Design review cases (NOT executed validators/Max evidence):**

| Case | Exact proposed outcome |
|---|---|
| Closed count2/count3; future count4 seam not approved | All full360 refuse in core; no assumption of native closure support |
| Shell 0 / ±.000999 / ±.001 / ±.001001 cm | Absent / refusal / present / present, same canonical decision at every consumer |
| Reverse upper ellipse, crown185 vs180; y beyond end by7 | Independent bounded distance5/span7 controls; no midUV/vertical-only shortcut |
| Solver width/exhaustion; one max above tolerance | Exhaustion INCOMPLETE; max FAIL cannot be offset by low mean/RMS |
| Grid25 but missing middle crown or endpoint ID | Required 36-identity coverage incomplete, no denominator shrink |
| success:true + sentinel; missing END; bool/undefined XYZ | ERROR / INCOMPLETE / ERROR, raw envelope retained |
| Same count but substituted ID, wrong unit/space, unknown runtime enum | Identity/quantity ERROR; uncertified enum readiness refusal |
| Changed frame/unit/census/transform between batches | Whole run INCOMPLETE/DRIFT; no partial PASS or foreign mutation |
| Receipt absent; stale library; one snapshot repeated three times | STOP binding / tested guard refusal / replay INCOMPLETE |
| Certificate absent; .5cm physical threshold not approved | NOT_READY and approval still OPEN; no fabricated precision/default |

Starting saved design: **121781 bytes / 1240 lines**, SHA-256
`e8fabdb5c536cf336c6f2421969de6df4a597e051ca31cf08d3e170f0270791c`.
Starting read-only git status: exactly the same three untracked files named in §13.4.
All other **219 non-.git files** have sorted `(relative path,SHA256)` inventory aggregate
`49a0f3f972b9735dee9b054061472b6cf85b6bdf24a7cd9df5058244e655ccf9`
(hash of Python repr of the sorted pair list encoded UTF-8). This supplies an actual ownership
baseline; saved-byte/leaf-count/status/diff checks below must be recorded after patch inspection.

**Actual read-only document gate:** inspected saved snapshot **221414 bytes / 2296 lines**, UTF-8
without BOM, CR count0, one final LF. The ten original tables still total **110** families;
eight new tables total **62+42+12+22+17+27+55+59=296**; combined **406**, all rows have exactly
the prescribed 8 original / 7 runtime columns (runtime status is explicitly PROPOSED in §17).
Current register counted **7 R / 12 C / 3 pending02.3**, all **10 approvals OPEN**. In-memory
reversal of only the declared §§1/10/13 pointer/authorization edits reconstructs the original
**121781-byte/1240-line** SHA-256 above exactly; no unrelated §§1–13 rewriting. Read-only
diff inspected those hunks and the appended extension; tracked diff/check empty, no-index
inspection covers this untracked file. All 219 other file digests still match the ownership
baseline, and git status still lists exactly the three pre-existing untracked paths. Inspection
used inline read-only Python (no project imports/cache writes), file reads and git read-only diff.
Initial shell-quoting/console-encoding inspection attempts failed; only the corrected hash/diff
and table checks count as evidence. Final gate-record edits and saved bytes are re-read before
handoff; this record does not attempt to hash itself or certify any policy case as execution.

**Next: 02.3 only on its own authorization**, then 02.4 approval/question STOP and complete
FREEZE. Live calibration, code, builders, validators, installation, git mutation and CHECKPOINT
editing were not authorized or executed by 02.2. This local document gate cannot approve A-*.

---

## 20. PROPOSED future CLI and contextual inventory integration

Covers **U20** and root plan §4.2.

### 20.1 Core CLI syntax contracts

The table below specifies the exact interfaces, arguments, mutual exclusivity constraints, exit
codes, and data flow for future CLI tools and modifications.

| Script | Interface / Subcommand | Required arguments | Optional flags | Exit codes | Mode & constraints |
|---|---|---|---|---|---|
| `curve_gen.py` | Import-only library | None (no CLI entry point) | None | n/a | Pure stdlib math; functions: `generator_points`, `validate_generator`, `chord_bound`, `suggest_count`. Calling as `__main__` raises error or prints usage |
| `expand_curves.py` | Expansion mode | `--project-dir DIR`, `--in FILE`, `--out FILE` | `[--json]` | 0 / 1 / 2 | Draft expansion; `--in` and `--out` are files; `--project-dir` is coherent root; differing existing `--out` refuses (exit 1); non-in-place; no guessed siblings |
| `expand_curves.py` | Verification mode | `--project-dir DIR`, `--in FILE`, `--check` | `[--json]` | 0 / 1 / 2 | Read-only check; verifies stored `points_cm` match generator & analytical ref; mismatch or missing dependency exits 1; no files written |
| `expand_curves.py` | Suggestion mode | `--project-dir DIR`, `--in FILE`, `--suggest-count`, `--section-id ID`, `--tol-cm X` | `[--json]` | 0 / 1 / 2 | Read-only suggestion for section `ID`; `X` finite > 0; returns count + method + bound; range 2..500; exhausted bounds exit 1; no Max interpolation guarantee |
| `qa_check.py` | Emit mode | `--in DIR`, `--emit RUN_DIR`, `--run-id TOKEN` | `[--calibration-cert FILE]`, `[--json]` | 0 / 1 / 2 | Offline emit; outputs deterministic `qa-request.json`, context & query batches; exit 0 = READY/NOT_EVALUATED, NOT model PASS; incompatible with assess flags |
| `qa_check.py` | Assess mode | `--in DIR`, `--request FILE`, `--results FILE`, `--out RUN_DIR` | `[--json]` | 0 / 1 / 2 | Offline assess; reads measurements, outputs `qa-results.json`; exit 0 = complete PASS only; 1 = FAIL/ERROR/INCOMPLETE; requires all three file flags |
| `env_preflight.py` | Strict gate mode | `--results FILE`, `--require-complete` | `[--transport TEXT]`, `[--json]` | 0 / 1 / 2 | Strict captured mode; exits 1 on any mandatory check SKIP, missing result or malformed output; bare mode without results remains exit 0 (all checks SKIP) |
| `init_project.py` | Scaffold mode | `--project ID` | `[--dir DIR]`, `[--from DIR]`, `[--force]`, `[--dry-run]` | 0 / 1 | Fresh mode creates 11 specs + manifest with draft `qa.json` (status=draft, no verdict); seeded creates 8 JSONs + draft QA, no CSV, no analytical authority |
| `validate_specs.py` | Static check mode | `[--dir DIR]` | `[--file FILE]`, `[--json]`, `[--warnings-as-errors]`, `[--rule TEXT]`, `[--build]`, `[--allow-draft]` | report exit | Purely static; validates envelopes, joins, G-1..G-90; no Max connection, no `--results`, no geometry inspection, no `--stage qa` |

**Operational rules for CLI tools:**
1. **Mode mutual exclusivity:**
   - In `expand_curves.py`: `--out`, `--check`, and `--suggest-count` are strictly mutually exclusive. Providing more than one or none exits 2.
   - In `qa_check.py`: `--emit` is strictly mutually exclusive with `--request`, `--results`, and `--out`. Mixing emit and assess flags exits 2. Missing results in assess mode never falls back to emit mode.
2. **Path and directory semantics:**
   - `--project-dir DIR` must be an absolute path or resolve to an existing coherent project directory containing `specs/pipeline/` and `project.json`.
   - `--in` and `--out` in `expand_curves.py` are file paths, not directory paths. Draft `--in` outside pipeline is allowed only via approved project identity.
   - Dependency paths inside specs are relative to the project root and must resolve strictly within the project directory tree. Any absent or mismatched dependency causes an immediate refusal (exit 1), never a guessed sibling or default.
3. **Exit code contract:**
   - Exit 0: requested operation completed successfully or check passed cleanly.
   - Exit 1: semantic refusal (data validation failure, count mismatch, dependency error, locked overwrite attempt, chord bound exhaustion, incomplete preflight, or QA check failure).
   - Exit 2: CLI usage error (missing mandatory options, unrecognized arguments, mutually exclusive flag collision).
   - Standard output messages and JSON output payloads never override or mask a non-zero exit code.
4. **Run token validation:**
   - In `qa_check.py`, `--run-id TOKEN` is provided by the calling agent or user script. It must match `^[a-zA-Z0-9_-]{1,64}$` to prevent path traversal. It is a local run identifier, not a server security token or cryptographic credential.
   - The emitted `qa-request.json` payload is strictly deterministic and free of system clocks, random nonces, or environment-dependent pointers. The accompanying `qa-run-context.json` links the request hash with the local run identifier.

### 20.2 Contextual inventory and stage awareness across S1..S7/P8

The pipeline spans stages S1 through S7 (with historical milestone P8 representing the automatic QA
gate). The handling of `qa.json` across stages is strictly contextual and governed by clear lifecycle
rules, without inventing ad-hoc validator flags.

| Stage | Primary pipeline outputs | QA status | Validator G-rule behavior |
|---|---|---|---|
| S1: Dimensions | `dimensions.json` | NOT_EVALUATED / static SKIP | Validates envelope, `form_references[]`, `precision_targets[]`. QA rules G-87..G-90 evaluate to SKIP |
| S2: Massing | `massing.json`, `massing.ms` | NOT_EVALUATED / static SKIP | Validates elements, site pad, grouping. QA rules evaluate to SKIP |
| S3: NURBS | `nurbs.json`, `nurbs.ms` | NOT_EVALUATED / static SKIP | Validates curves, generator joins, surfaces. QA rules evaluate to SKIP |
| S4: Facade | `facade_grids.json`, `components_registry.json`, CSVs | NOT_EVALUATED / static SKIP | Validates panels, prototypes, tables. QA rules evaluate to SKIP |
| S5: Assembly | `assembly.json`, `assembly.ms` | NOT_EVALUATED / static SKIP | Validates placements, wall cells, zero modifiers. QA rules evaluate to SKIP |
| S6: Rehearsal | Assembly smoke & scene measurement | NOT_EVALUATED / static SKIP | Optional execution smoke; static validator rules evaluate to SKIP |
| S7 / P8: QA Gate | `qa.json` (config), `qa-request.json`, `qa-results.json` | Evaluated / mandatory PASS | `validate_specs.py --dir <p> --build` at P8 enforces that `qa.json` is present, locked, valid schema 1.1, and fully configured. Draft, empty, or superseded QA refuses delivery (exit 1) |

**Contextual inventory rules:**
1. **Early stage independence:** Stages S1 through S5 do not require a locked, evaluated `qa.json`. A fresh scaffold created by `init_project.py` contains a draft `qa.json` with `status: "draft"`. In earlier stages, static linting passes with SKIP on QA-specific rules.
2. **P8 gate enforcement:** Delivery of the complete architectural model requires passing the P8 recheck. At P8, `qa.json` must be locked (`status: "locked"`), profile set to `form_precision_v1` (or explicitly approved `legacy_structure_v1`), with all required dependencies, targets, check plans, and operational limits fully populated. A draft or missing `qa.json` at P8 produces exit 1.
3. **Recheck scope preservation:** P8 is restored as an automatic gate without reviving cancelled stages P7 (materials) or P9 (export). Recheck stage lists must not re-introduce P7 or P9.
4. **No guessed CLI flags:** The validator detects whether a project is undergoing a P8 gate check through standard configuration or explicit `--build` mode targeting a pipeline with locked assets, not by inventing speculative CLI flags.

### 20.3 Calibration certificate CLI binding (§17.7, U20)

Per §17.7 and §18.1, empirical Max measurements and numerical evaluations require an evidence-bound
calibration certificate. The CLI binding for this requirement is explicit:

| CLI flag | Target schema | State requirement | Failure behavior |
|---|---|---|---|
| `--calibration-cert FILE` | `form_precision_calibration_v1` per §17.7 | Must have `state: "CALIBRATED"` and valid SHA-256 digests | If omitted in form profile, missing, unparseable, or state is `UNSUPPORTED`, `--emit` exits 1 with `NOT_READY` |

**Binding requirements:**
1. When `qa_check.py --emit` is invoked with `profile: "form_precision_v1"`, `--calibration-cert FILE` is mandatory.
2. The referenced file is verified before generating `qa-request.json`:
   - `certificate_version` must equal `"form_precision_calibration_v1"`.
   - `state` must be `"CALIBRATED"`.
   - `library_sha256` must match the SHA-256 digest of the active `nurbs_arch_library.ms`.
   - `methods.arithmetic_proof_sha256` must resolve to an immutable numerical enclosure proof.
   - All required runtime descriptor classes, work bounds, and unit types must be fully populated.
3. The certificate digest is embedded into `qa-request.json:calibration_cert_sha256`.
4. If the certificate is missing or invalid, `--emit` terminates with exit code 1, emitting an error explaining that numerical certification has not been completed. No hardcoded or guessed default bounds are substituted.

---

## 21. PROPOSED atomic publication, write transactions, ownership and wall representation

Covers **U21**, root plan §8, §11 (M31, M32, M34), and approvals **A-WRITE**, **A-OWNERS**, **A-CORRECT**.

### 21.1 Dual-file JSON+MS transactions and atomic publication (A-WRITE)

Every pipeline builder generates a tightly coupled dual-file artifact:
- `build_spec.py` -> `massing.json` + `massing.ms`
- `build_nurbs.py` -> `nurbs.json` + `nurbs.ms`
- `facade_tables.py` -> `facade_grids.json`, `components_registry.json`, `world_table.csv`, `components_table.csv`
- `place_components.py` -> `assembly.json` + `assembly.ms`

If a process is interrupted, killed, or throws an exception midway through writing, leaving one file
updated while the other is absent or stale produces a fatal synchronization defect.

| State | On-disk representation | Invariant verified | Failure action |
|---|---|---|---|
| 1. In-memory validation | Source models in memory | Schema invariants, G-rules, self-checks, receipt hashes verified | Abort before touching disk; no filesystem mutation |
| 2. Staged write | `<target>.tmp.<token>` | Both files completely written, flushed, closed; byte counts verified | Remove `.tmp.*` files; prior target files untouched |
| 3. Journal record | `.transaction.journal` | Transaction ID, timestamp, target file paths, staging paths logged as `STAGED` | Roll back staging files if journal write fails |
| 4. Atomic publication | Atomic rename / replace | Both staging files atomically replace target paths; journal updated to `COMMITTED` | If interrupted, journal recovery detects partial publish and restores previous pair |

**Atomic transaction protocol:**
1. **Staged generation:** Builders write output bytes to temporary staging files (e.g. `massing.json.tmp.<token>` and `massing.ms.tmp.<token>`) in the same filesystem directory to guarantee atomic rename capability.
2. **Self-check pre-condition:** No staging file is moved to the target path until all internal data structures, geometry predicates, and shape checks (e.g. `G-34`..`G-40`, `_check_script_shape`) have verified cleanly in memory.
3. **Atomic rename:** Target files are replaced via atomic filesystem operations (`os.replace` on POSIX/Windows). On Windows, if a target file is locked, the staging files are preserved and the transaction aborts with an explicit error.
4. **Journal and recovery:** The pipeline directory maintains a transaction journal. On builder startup, if an incomplete transaction from a crashed run is detected, the builder recovers the previous complete pair or halts with exit 1, refusing to operate on a corrupted directory.

### 21.2 Mitigation of M34 fault-injection and input draft preservation (A-WRITE)

Scenario **M34** in the fault-injection matrix addresses interrupted generation and differing output
handling, particularly when `--in` and `--out` share the same directory (as in `build_nurbs.py`):

1. **Input draft preservation:**
   - In `build_nurbs.py`, the input `nurbs.json` is authored as a draft spec (often containing generator definitions without discrete points).
   - The builder must read and parse the complete input file into memory before opening any write streams.
   - If `--in` and `--out` point to the same file (`--in . --out .`), the builder must NEVER truncate or write directly into the input file.
   - The original input draft is preserved intact in memory. If generation, normalization, or script rendering fails, the on-disk input file remains completely unaltered.
2. **Differing output refusal:**
   - If `--out` specifies an existing file path that already contains valid content differing from the freshly computed output, and overwrite is not explicitly forced, the builder refuses with exit 1.
   - This prevents accidental clobbering of hand-authored drafts or parallel stage outputs.
3. **Recovery:**
   - If a failure occurs during step 4 of the transaction, the journal enables full rollback to the pre-transaction state.
   - Incomplete file pairs (`.json` without `.ms` or vice versa) are detected by `validate_specs.py` and refused.

### 21.3 Stage ownership and analytical target immutability (A-OWNERS)

Stage boundaries enforce clear file ownership. No tool may cross ownership boundaries to modify
upstream files or circumvent validation.

| Stage | Owned spec files | Owned script / data files | Prohibited cross-file mutations |
|---|---|---|---|
| S1: Dimensions | `dimensions.json` | None | May not mutate massing or NURBS specs; owns analytical references & precision targets |
| S2: Massing | `massing.json` | `massing.ms` | Read-only access to `dimensions.json`; may not mutate NURBS or facade specs |
| S3: NURBS | `nurbs.json` | `nurbs.ms` | Read-only access to `dimensions.json`; may not mutate massing or assembly |
| S4: Facade | `facade_grids.json`, `components_registry.json` | `world_table.csv`, `components_table.csv` | Read-only access to dimensions & massing; may not alter placement outputs |
| S5: Assembly | `assembly.json` | `assembly.ms` | Read-only access to all four upstreams; may not mutate dimensions, massing, registry, or CSV |
| S7 / P8: QA | `qa.json` (config) | `qa-request.json`, `qa-results.json` | Strictly read-only access to all pipeline specs; may not modify upstream geometry or targets |

**Analytical target immutability:**
- If a QA check fails for an analytical target declared in `dimensions.json:precision_targets`, the QA agent and toolchain are **strictly prohibited** from deleting, disabling, or modifying the target in `dimensions.json` or `qa.json` to force a pass.
- Modifying an analytical target or removing a precision requirement is a project scope change that can only be authorized by the S1 design owner and user, recorded in the project assumptions/conflicts ledger.

### 21.4 Visible active solid wall representation and host occupancy (A-CORRECT, M31/M32)

In the legacy pipeline, `massing.json` created solid boxes for facade walls (`elements[]` with kind
`facade_wall`), while `place_components.py` generated discrete wall cells (`WAL_` nodes) tiling around
window and door openings. In 3ds Max, this resulted in a severe visual and geometric collision: the
original solid host wall remained active and visible in the scene, physically occupying the opening
volume and penetrating through the window/door panels (`PLC_` nodes).

**Visible active geometry contract:**
1. **Delivered solid geometry:** The QA check `QA-V1-WALLS` inspects **delivered visible active solid geometry** in the scene. A wall cannot be claimed to have openings if solid mass continues to render within the opening boundaries.
2. **Assembly host resolution options (A-CORRECT):**
   When `assembly.ms` executes, the host wall must be resolved using one of three explicit mechanisms:
   - **Mechanism A (Deactivation / Layer Isolation):** `assembly.ms` explicitly sets the host wall node to hidden or moves it to a dedicated non-rendering reference layer (e.g. `hide (getNodeByName "WALL_HOST_01")`), leaving only the discrete tiled `WAL_` cells and `PLC_` components visible.
   - **Mechanism B (Replacement):** `assembly.ms` explicitly deletes or suppresses the host box node, fully substituting it with the tiled `WAL_` solid cell meshes.
   - **Mechanism C (Emitted Opening Subtractions):** `massing.ms` or `assembly.ms` emits geometry with actual openings pre-cut or subtracted without unusable Boolean modifiers.
   Hiding or deactivation cannot merely be declared in a JSON attribute; it must be an executed operation in the emitted `assembly.ms`.
3. **Dimension-correct volume invariant (`G-82`):**
   - The legacy `G-82` formulation compared volume in cm³ against a cm²-shaped threshold (`abs(vol - expected) > linear * linear`), which is dimensional nonsense.
   - The corrected `G-82` invariant compares volume using a dimension-correct volume tolerance:
     $$\left| \sum V_{\text{cell}} - V_{\text{host}} \right| \le \text{tolerance\_cm3}$$
     where $\text{tolerance\_cm3}$ is derived from certified boundary propagation or explicitly configured in §12.4.
4. **Occupancy verification beyond volume equality (M31):**
   - Volume equality alone is insufficient: overlapping cells combined with void gaps can accidentally produce the correct total volume while failing spatial occupancy.
   - `QA-V1-WALLS` requires per-cell interval occupancy: every cell must span its wall's full thickness (`G-83`), have zero overlaps with neighboring cells, have zero gaps along the tiling interval, and leave opening apertures completely free of solid geometry.
   - Any foreign node or host mass intersecting an opening aperture produces an immediate QA FAIL (M32).

---

## 22. PROPOSED fixture, recipe and adaptive regeneration locations

Covers **U22**, root plan §8, §10 (Phase 13), and approvals **A-EXAMPLE**, **A-REGEN**, **A-OWNERS**.

### 22.1 Directory layout and role separation

To preserve historical test baselines while enabling verified adaptive pipeline fixtures, files are
strictly organized into three distinct locations:

| Directory path | Contents & schema versions | Mutability & regeneration policy | Historical hash binding |
|---|---|---|---|
| `examples/` | Historical benchmark project (136 panels, 27 massing, 10 NURBS, 244/254 nodes); schema 1.0; legacy cm/1 `.ms` scripts | **STRICTLY IMMUTABLE (L-HISTORY)**; no regeneration, no unit preambles, no edits; preserved byte-for-byte | All file SHA-256 digests pinned; verified unchanged across all phases |
| `specs/recipes/` | Generative templates (e.g. `specs/recipes/nurbs/barrel-vault-generated.json`); schema 1.1; standalone recipe specs | Mutable authoring source; updated by stage owners; instantiated into projects, never executed directly | Template SHA-256 tracked; spec name equals filename stem |
| `specs/fixtures/form-precision/` | Dedicated coherent adaptive fixture project; schema 1.1; complete specs + receipts + locked QA config | Generated & updated exclusively by deterministic builders; validated and certified live before check-in | Curated fixture; checked in with reproducible build receipts and test records |

### 22.2 Dedicated fixture directory: `specs/fixtures/form-precision/`

The fixture directory `specs/fixtures/form-precision/` serves as the primary integration and QA testbed
for all new form precision, unit conversion, and automatic QA capabilities:

1. **Directory structure:**
   ```
   specs/fixtures/form-precision/
   ├── project.json
   └── specs/
       └── pipeline/
           ├── dimensions.json          # Schema 1.1: form_references[], precision_targets[]
           ├── massing.json             # Schema 1.0/1.1: site_pad, elements[], grouping[]
           ├── nurbs.json               # Schema 1.1: sections[].generator, points_cm, surfaces
           ├── facade_grids.json        # Schema 1.0: panel grids
           ├── components_registry.json # Schema 1.0: prototype definitions
           ├── world_table.csv          # 136 panel placements
           ├── components_table.csv     # Prototype dimensions
           ├── assembly.json            # Schema 1.0: placements, wall cells
           └── qa.json                  # Schema 1.1: locked QA plan (form_precision_v1)
   ```
2. **Coherence contract:**
   - Follows all Grammar §12 rules: consistent `project` envelope identifier across all files, matching unit declarations (`cm`, `deg`), and complete foreign-key joins.
   - `dimensions.json` contains the analytical semi-elliptical barrel vault reference (`form_references[0]`) and declares an analytical target with `role: "design_surface"`.
   - `nurbs.json` derives its generator sections from `dimensions.json` and carries discrete points matching the generator recomputation within 0.001 cm.
   - `qa.json` is fully configured and locked, targeting the analytical surface with sampling grid, required landmarks, and operational bounds.
3. **Exclusion of runtime reports:**
   - The fixture directory contains **only design specifications and configuration**.
   - Runtime execution artifacts (`qa-request.json`, `qa-measurements.json`, `qa-results.json`) are written to `<project>/runs/form-qa/<run-id>/` outside `specs/pipeline/` and are never committed into the fixture spec tree.

### 22.3 Recipe templates: `specs/recipes/`

1. **Template contract:**
   - Recipes provide authoring starting points for specific geometric assemblies (e.g. `specs/recipes/nurbs/barrel-vault-generated.json`).
   - The `spec` property in the envelope must match the filename stem (e.g. `barrel-vault-generated.json` has `spec: "nurbs"`).
   - Recipes contain complete generator schemas but may omit derived points until expanded, or contain complete standalone examples.
   - Recipes are validated independently using `validate_specs.py --file <path>`.
2. **Instantiation:**
   - A recipe is instantiated into a target project using `init_project.py` or authoring tools.
   - A recipe is never directly built in-place as a project pipeline.

### 22.4 Historical `examples/` preservation (L-HISTORY)

1. **Immutability guarantee:**
   - Under lock `L-HISTORY` (plan §2), files in `examples/` must remain **byte-identical**.
   - The historical MAXScript files (`examples/massing.ms`, `examples/nurbs.ms`, `examples/assembly.ms`) represent verified cm/1-only milestones (P5 gate, P6 gate).
   - They must NOT be updated with scene unit preambles, build receipts, or stage receipts.
   - Active documentation will clearly document `examples/` as historical cm/1-only benchmarks.

### 22.5 Adaptive script regeneration and certification policy (A-REGEN)

When new adaptive scripts reflecting the unit conversion architecture, stage receipts, and corrected
wall representations need to be certified:

1. **Owner-driven generation:**
   - Generated `.ms` scripts are NEVER hand-edited.
   - Stage owners execute the deterministic builders:
     - `python scripts/build_spec.py --stage massing --in specs/fixtures/form-precision/specs/pipeline --out specs/fixtures/form-precision/specs/pipeline`
     - `python scripts/build_nurbs.py --in specs/fixtures/form-precision/specs/pipeline --out specs/fixtures/form-precision/specs/pipeline`
     - `python scripts/place_components.py --in specs/fixtures/form-precision/specs/pipeline --out specs/fixtures/form-precision/specs/pipeline`
2. **Static validation gate:**
   - Emitted scripts and JSON files are validated using `python scripts/validate_specs.py --dir specs/fixtures/form-precision/specs/pipeline --build --warnings-as-errors`.
3. **Live rehearsal certification:**
   - In an authorized rehearsal scene (under `A-LIVE`), the emitted scripts are executed via `fileIn`.
   - The resulting scene is measured: object counts, node names, bounding boxes, base-Z alignment, modifier count (0 for assembly), and volume.
   - Only when live measurements match expected analytical tolerances is the generated fixture certified.

---

## 23. PROPOSED dispositions for U20–U22 and consolidated 02.3 U-register

Covers the completion of the 22 unresolved design groups and consolidates the 10 OPEN A-* approvals.

### 23.1 Dispositions for U20, U21, U22

The remaining three unresolved groups from §13.3 and §19.1 are resolved into explicit proposed
policies:

1. **U20: CLI syntax, stage awareness, and calibration certificate binding:**
   - **Disposition: `R` (Recommended policy settled).**
   - Interface contracts for `curve_gen.py`, `expand_curves.py`, `qa_check.py`, `env_preflight.py`, `init_project.py`, and `validate_specs.py` are frozen in §20.1.
   - Contextual inventory lifecycle across S1..S7/P8 settled in §20.2: early stages skip QA; P8 enforces locked, valid `qa.json` without ad-hoc CLI flags.
   - Calibration certificate CLI binding `--calibration-cert FILE` settled in §20.3 per §17.7.
   - Next owners: CLI/validator authors in phases 04, 07, 10; user approval `A-FIELDS`/`A-OWNERS` at 02.4.
2. **U21: Atomic publication, ownership, and active wall representation:**
   - **Disposition: `R` (Recommended policy settled).**
   - Dual-file JSON+MS staged transaction protocol, atomic rename, and journal recovery settled in §21.1.
   - M34 fault-injection mitigation, draft preservation on same-path `--in`/`--out`, and differing output refusal settled in §21.2.
   - Stage file ownership and analytical target immutability settled in §21.3.
   - Active visible solid wall representation contract, opening clearance, and dimension-correct cm³ `G-82` volume policy settled in §21.4.
   - Next owners: Stage builders and assembly author in phases 08, 09, 11; user approval `A-WRITE`/`A-OWNERS`/`A-CORRECT` at 02.4.
3. **U22: Fixture locations, recipe templates, and regeneration policy:**
   - **Disposition: `R` (Recommended policy settled).**
   - Dedicated fixture directory `specs/fixtures/form-precision/` established in §22.1 and §22.2.
   - Recipe template directory `specs/recipes/` established in §22.1 and §22.3.
   - Byte-identical preservation of historical `examples/` under lock `L-HISTORY` reaffirmed in §22.4.
   - Deterministic, builder-driven regeneration and live certification policy settled in §22.5.
   - Next owners: Fixture author and documentation author in phases 06, 13; user approval `A-EXAMPLE`/`A-REGEN`/`A-OWNERS` at 02.4.

### 23.2 Consolidated 22-group U-Register (U01–U22)

All 22 question groups originating in §13.3 are now formally addressed. None remain pending.
**R = recommended design settled; C = exact method/schema settled with explicitly named calibration gate.**

| ID | 02.3 disposition | Current policy / remaining evidence gate | Next owner |
|---|---|---|---|
| U01 | R | §14.1 core refuses full360; no closed consumer/API claim | User A-CLOSED/FIELDS at 02.4 |
| U02 | R | §14.1 zero absent, below refuses, equality present; canonical decision forwarded | User A-CLOSED; later C03-SHELL |
| U03 | C | §15 exact finite oriented interval solver/bracket/exhaustion; §18 arithmetic proof + certificate binds selected width | C03-NUMERIC/CERT |
| U04 | C | §17 wire grammar exact; actual invariant serializer/raw bytes and certified wire bounds | C03-WIRE/RAW/NUMERIC/CERT |
| U05 | C | §18 c/f relative enclosure, no q6; exact enum/scales and proof-domain values not guessed | C03-UNITS/NUMERIC/CERT |
| U06 | C | §§13/18 physical cm³ vs numeric aggregate enclosure separated | C03-NUMERIC/CERT; 03.8 if mesh route needed |
| U07 | C | §18 explicit row cap, deterministic work-aware partition; 25 not certified | C03-WORK/CERT plus QA owner cap |
| U08 | R | §18 explicit max_targets, inferred count, absence/exceed refuses | QA owner |
| U09 | R | §§16/18 exact 36 form identities + other required records; explicit cap | QA owner |
| U10 | R | §18 all planned call upper including guards/trace/captures, explicit cap | QA owner |
| U11 | C | §18 explicit <2s and certified work limit, measured overrun invalidates | C03-WORK/CERT plus QA owner cap |
| U12 | R | §18 explicit total cap, exact monotonic interval, no partial PASS | QA owner |
| U13 | R | §§15/16 one replacement per iteration, explicit per-sample limit | QA owner; solver arithmetic C03-NUMERIC |
| U14 | C | §§17/18 full raw-envelope size, explicit cap, no truncation; measured capture route | C03-RAW/WORK/CERT |
| U15 | C | §16 actual-domain grid + independent bounded landmark localization; never midUV assumption | C03-SPACE/LANDMARK/CERT |
| U16 | C | §16 kind-role census/relations, trim0 unsupported form target; ambiguity ERROR | C03-ROLE/CERT |
| U17 | C | §17 explicit signed frame, ticks=index*ticks_per_frame, drift guards | C03-FRAME/CERT |
| U18 | C | §§16–18 exact ID/enums/hash/wire/report inventory; serializer/arithmetic/raw mechanisms need evidence | C03-WIRE/RAW/NUMERIC/CERT |
| U19 | C | §17 local-only session/actual receipt/library-first/three real replays; no token or retrospective receipt | C03-LIBRARY/RAW/CERT, phase12 replay |
| U20 | R | §20 CLI syntax contracts, contextual stage inventory S1..S7/P8, calibration certificate CLI binding | CLI/validator authors in phases 04/07/10; user A-FIELDS/OWNERS at 02.4 |
| U21 | R | §21 Dual-file atomic transactions, M34 mitigation, draft preservation, ownership & visible wall contract | Stage builders in phases 08/09/11; user A-WRITE/OWNERS/CORRECT at 02.4 |
| U22 | R | §22 Dedicated fixture `specs/fixtures/form-precision/`, `specs/recipes/`, byte-identical `examples/`, regen policy | Fixture/doc authors in phases 06/13; user A-EXAMPLE/REGEN/OWNERS at 02.4 |

**Register summary:**
- **10 R (Recommended policies settled)**: U01, U02, U08, U09, U10, U12, U13, U20, U21, U22.
- **12 C (Calibration-bound methods settled)**: U03, U04, U05, U06, U07, U11, U14, U15, U16, U17, U18, U19.
- **0 Pending**: All 22 question groups are formally resolved into either proposed policies or explicit calibration gates.

<a id="233-consolidated-10-open-a--approval-package-for-phase-024"></a>
### 23.3 Consolidated 10 APPROVED A-* approval package (User approved 2026-10-10)

All ten user decisions from §4 are **APPROVED** (User approved 2026-10-10 at Gate 02). They are consolidated below with their defining design
sections, recording user approval as a single package:

| ID | Root plan recommendation | Defining design sections | Exact consolidated question for user approval | Owner | Status |
|---|---|---|---|---|---|
| **A-VERSION** | Support 1.0 and 1.1 explicitly; new references, generators, and QA configs ship as 1.1; reject unknown versions | §11.1, §20.1 | Do you approve supporting schema versions 1.0 and 1.1 explicitly, requiring 1.1 for new form references and QA configs, while refusing unknown minor/patch versions without warning bypass? | user | **APPROVED** (User approved 2026-10-10) |
| **A-TOL** | Separate arithmetic, form, and numerical budgets; physical form threshold 0.5 cm; dimension-correct cm³ volume | §12.4, §13.1, §18, §21.4 | Do you approve separating arithmetic, form (0.5 cm), and numerical uncertainty budgets, using dimension-correct cm³ volume tolerances, and enforcing the boundary comparator? | user | **APPROVED** (User approved 2026-10-10) |
| **A-FIELDS** | Constrained v1 schemas: exact leaf inventories for envelope, origins, references, generator, tolerances, QA, and CLI | §11, §12, §16, §17, §20 | Do you approve the exact leaf inventories, container definitions, provenance origins, target roles, CLI interfaces, and calibration bindings across §§11–12, §§16–17, and §20? | user | **APPROVED** (User approved 2026-10-10) |
| **A-CLOSED** | Refuse 360° closed curves in core; enforce shell presence at exact 0.001 cm equality | §14.1 | Do you approve refusing 360° closed curves in core generator processing, and treating shell thickness equal to 0.001 cm as present across library, census, and validator? | user | **APPROVED** (User approved 2026-10-10) |
| **A-EXAMPLE** | Dedicated fixture in `specs/fixtures/form-precision/`; recipes in `specs/recipes/`; historical `examples/` immutable | §22.1–§22.4 | Do you approve creating the dedicated fixture project under `specs/fixtures/form-precision/` and recipe templates in `specs/recipes/`, while keeping historical `examples/` strictly byte-identical? | user | **APPROVED** (User approved 2026-10-10) |
| **A-WRITE** | Atomic staged publication; journal recovery; draft preservation on same-path `--in`/`--out`; refusal on differing output | §21.1, §21.2 | Do you approve the dual-file staged write transaction protocol, journal recovery, draft preservation on same-path expansion, and refusal when differing output exists? | user | **APPROVED** (User approved 2026-10-10) |
| **A-OWNERS** | Sequential patch scopes per plan §§8–10; strict stage file ownership; analytical target immutability | §21.3, plan §§8–10 | Do you approve the sequential patch scopes and stage file ownership rules, prohibiting tools from modifying upstream specifications or analytical targets to clear failures? | user | **APPROVED** (User approved 2026-10-10) |
| **A-LIVE** | Explicitly authorized rehearsal scenes for live Max probes, unit matrix, and replay; production stays read-only | §18.1, plan §10 | Do you grant permission for bounded live calibration probes, unit scale matrix tests, and replay rehearsals in isolated temporary scenes, keeping production scenes read-only? | user | **APPROVED** (User approved 2026-10-10) |
| **A-CORRECT** | Corrected active visible host wall representation; opening clearance; dimension-correct cm³ `G-82` | §21.4 | Do you approve resolving the visible solid host wall defect in Max assembly (via deactivation, replacement, or subtraction) so openings remain clear, with dimension-correct cm³ volume validation? | user | **APPROVED** (User approved 2026-10-10) |
| **A-REGEN** | Builder-driven regeneration and live rehearsal certification for new adaptive scripts; no hand-editing | §22.5 | Do you approve the policy that new adaptive example scripts are generated strictly by deterministic builders, validated, executed live, and certified before publication? | user | **APPROVED** (User approved 2026-10-10) |

---

## 24. Local 02.3 document gate record

**Microtask 02.3 design review completed / DRAFT / NOT FROZEN. No phase-02 PASS.**

This gate records read-only verification of the design document edits completed under microtask 02.3.
No code, builders, validators, test scripts, specs, or examples were executed or modified. No live Max
probes were run, and git state was not mutated.

### 24.1 Scope of edits and write ownership

- **Exclusive write ownership:** `references/_form-units-qa-design.md` only.
- **Added content:** Sections 20 through 24 appended; title status and navigation links in §1 updated.
  - §20: Proposed future CLI contracts, stage-aware contextual inventory lifecycle S1..S7/P8, and calibration certificate CLI binding.
  - §21: Dual-file atomic publication transactions, M34 fault-injection mitigation, draft preservation, stage ownership, and visible active solid wall representation.
  - §22: Dedicated fixture directory `specs/fixtures/form-precision/`, recipe templates in `specs/recipes/`, historical `examples/` preservation, and adaptive regeneration policy.
  - §23: Final dispositions for U20–U22 (all 22 U-groups now resolved: 10 R, 12 C, 0 pending) and consolidated 10 OPEN A-* approvals for Phase 02.4.
  - §24: Local 02.3 document gate record and read-only verification summary.

### 24.2 Design review cases (NOT executed code/evidence)

| Case | Exact proposed outcome |
|---|---|
| `expand_curves.py --check` on mismatched generator/points | Exits 1 with verification refusal; no files written |
| `expand_curves.py` with differing existing `--out` | Exits 1 with refusal; input draft and existing output preserved untouched |
| `expand_curves.py --suggest-count` with exhausted budget (>500) | Exits 1 with chord bound exhaustion notice; no count returned |
| `qa_check.py --emit` without `--calibration-cert` under form profile | Exits 1 with NOT_READY; no request or query batches emitted |
| `qa_check.py --emit` mixed with `--results` | Exits 2 with usage error; emit and assess modes are mutually exclusive |
| `qa_check.py --assess` with missing results file | Exits 1 with error; never falls back to emit mode |
| `env_preflight.py --results` with SKIP check under `--require-complete` | Exits 1 with preflight incomplete refusal |
| Interrupted build midway through dual-file write | Journal detects incomplete pair; rolls back to prior complete state |
| Same-path expansion in `build_nurbs.py` with generation failure | Input draft `nurbs.json` remains completely unmodified on disk |
| Visible solid host wall remaining in opening after assembly | QA check `QA-V1-WALLS` fails; host must be deactivated, replaced, or pre-cut |
| Volume identity check with cancelling cell gaps and overlaps | Total volume may match, but per-cell interval occupancy and zero-overlap checks fail |
| Attempt to edit `dimensions.json:precision_targets` to pass QA | Refused by ownership rules; requires S1 design authority and user approval |

### 24.3 Read-only document verification results

Verification performed via inline read-only Python scripts:
1. **File encoding & line endings:** UTF-8 encoded without BOM. Line endings are strictly LF (`\n`), zero CR (`\r`) characters present. Exactly one terminating LF at end of file.
2. **Table column consistency:** All tables throughout the entire document (historical §§1–19 plus new §§20–24) have strictly consistent column counts for every row. Zero column count mismatches across all tables.
3. **Table counts and metrics:**
   - Previous table count (02.2): 46 tables.
   - Newly added tables in 02.3: 9 tables (§20: 3, §21: 2, §22: 1, §23: 2, §24: 1).
   - Total table count: 55 tables.
4. **U-Register status:** All 22 U-groups resolved (10 Recommended, 12 Calibration-bound, 0 Pending).
5. **Approval register status:** All 10 A-* approvals remain **OPEN** awaiting user review in Phase 02.4.
6. **Filesystem and git status:** `git status --porcelain` confirms no files other than `references/_form-units-qa-design.md` were touched by this task.

### 24.4 Hand-off to Microtask 02.4

Microtask 02.3 is complete. The design register is comprehensive, fully cross-referenced, and ready for
Phase 02.4:
- The user will be presented with the consolidated 10 A-* approval package in §23.3.
- Upon user approval of the package, the design will transition from DRAFT to FROZEN.
- Coding, builders, validators, calibration probes, and installation remain prohibited until Phase 02.4 approval is recorded.

---

## 25. Gate 02 Freeze and Acceptance Record

**Gate 02 Status: PASS.**
**Document Contract Status: FROZEN.**
**Date of Acceptance: 2026-10-10.**

### 25.1 Explicit user approval record

On 2026-10-10, the user granted explicit, unanimous approval for all ten architectural and policy
decisions comprising the consolidated approval package (§4 and §23.3). This formal acceptance satisfies
the Phase 02.4 gate requirement, transitions this specification from DRAFT to FROZEN, and closes Gate 02
with status **PASS**.

| ID | Decision name | Defining sections | User decision (2026-10-10) | Resulting binding policy |
|---|---|---|---|---|
| **A-VERSION** | Supported schema versions & compatibility | §11.1, §20.1 | **APPROVED** | Versions 1.0 and 1.1 supported explicitly; 1.1 required for new form references & QA configs; unknown versions refused without bypass. |
| **A-TOL** | Uncertainty budgets & volume comparator | §12.4, §13.1, §18, §21.4 | **APPROVED** | Arithmetic, form (0.5 cm), and numerical budgets separated; dimension-correct cm³ volume tolerances; boundary comparator enforced. |
| **A-FIELDS** | Constrained v1 leaf schemas & CLI grammar | §11, §12, §16, §17, §20 | **APPROVED** | Exact leaf inventories, container definitions, provenance origins, target roles, CLI interfaces, and calibration bindings binding as specified. |
| **A-CLOSED** | Closed curve & shell presence policy | §14.1 | **APPROVED** | 360° closed curves refused in core generator; shell thickness equal to 0.001 cm treated as present across library, census, and validator. |
| **A-EXAMPLE** | Dedicated fixture location & recipes | §22.1–§22.4 | **APPROVED** | Dedicated fixture project under `specs/fixtures/form-precision/`; recipes in `specs/recipes/`; historical `examples/` strictly byte-identical under `L-HISTORY`. |
| **A-WRITE** | Dual-file atomic staged write transactions | §21.1, §21.2 | **APPROVED** | Dual-file staged write transaction protocol, journal recovery, draft preservation on same-path expansion, and refusal when differing output exists. |
| **A-OWNERS** | Sequential patch scopes & stage ownership | §21.3, plan §§8–10 | **APPROVED** | Sequential patch scopes and stage file ownership binding; tools prohibited from modifying upstream specs or analytical targets to clear failures. |
| **A-LIVE** | Authorized rehearsal scenes & read-only prod | §18.1, plan §10 | **APPROVED** | Permission granted for bounded live calibration probes, unit scale matrix tests, and replay rehearsals in isolated temporary scenes; production scenes stay read-only. |
| **A-CORRECT** | Solid host wall representation & clearance | §21.4 | **APPROVED** | Active visible solid host wall defect in Max assembly resolved (deactivation, replacement, or subtraction) keeping openings clear; dimension-correct cm³ volume validation. |
| **A-REGEN** | Deterministic adaptive example regeneration | §22.5 | **APPROVED** | New adaptive example scripts generated strictly by deterministic builders, validated, executed live, and certified before publication; no manual script editing. |

### 25.2 State of the contract

1. **Contract is FROZEN:** The specification contained in this document (`references/_form-units-qa-design.md`) is now the authoritative, binding English contract governing form precision, native Max units, and automatic QA implementation.
2. **Authority:** Per §2 (Authority order), this frozen English contract supersedes preliminary planning proposals.
3. **Locks preserved:** All foundational constraints (`L-UNIT`, `L-QA`, `L-D8`, `L-HISTORY`, `L-SAFETY`) remain in full effect.
4. **Implementation gates unlocked:** The freeze of Gate 02 authorizes proceeding to the next sequential execution phase.

### 25.3 Next execution phase: Phase 03 (Calibration after A-LIVE)

With `A-LIVE` approved by the user, the project advances to **Phase 03**:
- Execution of bounded, live calibration probes against isolated rehearsal scenes in 3ds Max 2026.
- Verification of the unit matrix (`k`, `s`, `c`, `f` runtime behaviors).
- Numerical brackets, wire representations, and library replay certification.
- Calibration certificates emitted for binding into subsequent builder and QA phases.
