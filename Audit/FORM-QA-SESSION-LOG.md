# FORM-QA session log — content moved out of `references/_form-units-qa-design.md`

Created **2026-10-30** by the **option C+ cut** (maintenance item 6, user decision U1 in
`Audit/_maintenance-2026-10-30-brief.md` §1). This file is the destination named by
`Audit/_form-qa-citation-map.md` §"Proposed cut lines", option C+ = the three contiguous
gate blocks **plus** the two DEAD sections.

Source: `references/_form-units-qa-design.md`, FROZEN and user-approved 2026-10-10,
**273,208 B / 2,815 lines** at HEAD `268abb4` (immediately before this cut). The cut is
**move-only**: every block below is byte-identical to what was removed. Nothing here was
rewritten, re-classified or deleted.

**Why these five and no others.** All five are session/gate narrative or dead prose. None is
CITED or FACT-TABLE except §24.2, whose only two citers are already inside `Audit/`. The 13
live citations — `scripts/qa_check.py` (6), `references/07-spec-grammar.md` (2),
`agents/max-input.md` (4), plus `CHECKPOINT.md:158`'s file-level route — were each resolved
against the five spans before cutting, and none intersects one. **§17 was deliberately not
touched** (option D is not authorised, U2): §17.1 is cited by `scripts/qa_check.py:152` and
§17.2–§17.7 are the schema its emitter implements.

⚠️ **`Audit/` is not packaged** by `scripts/install_skill.py`. The content below therefore
left the shipped `.skill` on this cut. That is the intended outcome — it is NARRATIVE/DEAD
material — but it is also why no live citation may point here.

⚠️ **Line numbers below are the PRE-CUT offsets in the post-errata revision** (the revision
measured at 273,208 B). They are recorded for provenance only; this file has no further
drift risk, and the section headings are verbatim so they can be re-found by text.

---

## Provenance of each moved block

| block | sections moved | class | source lines | bytes | lines | sha256 of the moved bytes |
|---|---|---|---|---|---|---|
| `M1` | §6.2 `PROPOSED — NOT IMPLEMENTED` | DEAD | 351–373 | 1,659 | 23 | `fdbe21cfe5de337724f54e6fd42c1a8b` |
| `M2` | §7.1 `Proposed new files — none of them exists` | DEAD | 399–415 | 1,733 | 17 | `5ab40703c4a8f0b81062c3aeaeef187d` |
| `M3` | §13.3 `Unresolved register` + §13.4 `Microtask 02.1 local gate record` | NARRATIVE | 1204–1307 | 10,403 | 104 | `66d7f2ebf9ff2c63d36596f303a3bbf4` |
| `M4` | §19.1 `Current U-register with 02.1 history retained` + §19.2 `Local 02.2 gate` | NARRATIVE | 2284–2374 | 7,855 | 91 | `cac5920458f3ecf34f809ba974c9c485` |
| `M5` | §24 `Local 02.3 document gate record` + §24.1–§24.4 | NARRATIVE + 1 CITED (§24.2) | 2718–2775 | 4,511 | 58 | `ed9aee619086f3d5e3805fb699abc7e4` |
| **total** | 5 blocks / 11 sections | — | — | **26,161** | **293** | — |

Closing arithmetic, measured: **273,208 − 26,161 (moved) + 2,542 (five pointer stubs) + 2,948
(appended errata lines) = 252,537 B**, the new size of `references/_form-units-qa-design.md`.
The citation map's option-C+ estimate predicted **241,567 B** retained; the measured file is
**10,970 B larger**, and that difference reconciles to the byte: +5,480 (the errata block inserted
earlier on 2026-10-30, after the estimate was written) + 2,948 (the errata append quoted above)
+ 2,542 (the five pointer stubs) = 10,970. The estimate priced a bare removal and included
none of the three; all three were required.

---

## How to cite this file

Cite a moved section by its **verbatim heading text**, not by a line number — the same
convention `references/_form-units-qa-design.md` imposes on its own stale `CHECKPOINT.md:NNN`
references. `Audit/EVIDENCE_2026-10-27.md:175`'s line anchor `:2693` meant §24.2 `Design review
cases`; that file is frozen data and was left untouched, so the mapping is recorded here and in
the source doc's errata block instead. §24.2 is block **M5** below.

`Audit/AGENT_PLAN_poly_surface_shell.md:385` was already re-anchored to the section anchor
`§24.2 «Design review cases»` by the 2026-10-30 pass, so it survives this cut unedited.

---

## M1 · §6.2 `PROPOSED — NOT IMPLEMENTED` (DEAD)

> Moved verbatim from `references/_form-units-qa-design.md` lines 351–373 —
> **1,659 B / 23 lines**, sha256 `fdbe21cfe5de337724f54e6fd42c1a8b08db746bd07f36311b65efae716bd0ab`.
> Headings below are the source headings, unedited.

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


---

## M2 · §7.1 `Proposed new files — none of them exists` (DEAD)

> Moved verbatim from `references/_form-units-qa-design.md` lines 399–415 —
> **1,733 B / 17 lines**, sha256 `5ab40703c4a8f0b81062c3aeaeef187db44133fb2ca657caf74fa88a1b911eb9`.
> Headings below are the source headings, unedited.

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


---

## M3 · §13.3 + §13.4 — 02.1 unresolved register and local gate record (NARRATIVE)

> Moved verbatim from `references/_form-units-qa-design.md` lines 1204–1307 —
> **10,403 B / 104 lines**, sha256 `66d7f2ebf9ff2c63d36596f303a3bbf495117573abafb0e66d94a26435812713`.
> Headings below are the source headings, unedited.

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


---

## M4 · §19.1 + §19.2 — 02.2 U-register snapshot and local gate (NARRATIVE)

> Moved verbatim from `references/_form-units-qa-design.md` lines 2284–2374 —
> **7,855 B / 91 lines**, sha256 `cac5920458f3ecf34f809ba974c9c4851ad945e96dd201480175a0e8b531e5cb`.
> Headings below are the source headings, unedited.

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


---

## M5 · §24 + §24.1–§24.4 — local 02.3 document gate record (NARRATIVE, incl. CITED §24.2)

> Moved verbatim from `references/_form-units-qa-design.md` lines 2718–2775 —
> **4,511 B / 58 lines**, sha256 `ed9aee619086f3d5e3805fb699abc7e477d2b108f167d145cce6471fc3c62dbf`.
> Headings below are the source headings, unedited.

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


---
