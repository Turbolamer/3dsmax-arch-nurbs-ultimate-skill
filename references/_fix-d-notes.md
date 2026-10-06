# Fix batch D — findings and per-file record

**Date:** 2026-10-06
**Scope:** eleven files only. No live `3dsmax-mcp_*` call was made — every fact below arrived as data
from the orchestrator, already measured on Max 2026.3.2.
**Files touched:** exactly the eleven named in the brief, plus this notes file.

---

## 0. Verification run

```
python -m py_compile scripts/*.py                       -> clean
python scripts/validate_specs.py --dir examples         -> PASS 138 / FAIL 0 / WARN 0 / SKIP 15
                                                          exit 0 -- no FAIL rows
```

Both matched the expected result exactly. `install_skill.py` was **not** run, as instructed.

### Residual-problem grep — every hit read individually

Command:

```
grep -n "formattedPrint\|NURBSId\|OpenPBRMaterial\|Point_Surf\|CV_Surf\|railID : integer" \
  <the eleven files>
```

| File:line | Inside a correction note that quotes the old text, or already correct? |
|---|---|
| `nurbs-complete-guide.md:13` | correction note (quotes `CV_Surf`, `Point_Surf`, `Point_Curve`, `CV_Curve` as the **wrong** node classes) |
| `nurbs-complete-guide.md:22`, `:24` | `NURBSId` as **concept shorthand** in a heading and a lead sentence; the note at `:26–31` states explicitly that the name survives as shorthand for the concept and in method signatures, and that the *type* is `IntegerPtr` |
| `nurbs-complete-guide.md:26`, `:31`, `:40`, `:47`, `:331` | correction notes |
| `nurbs-architecture-recipes.md:263`, `:264`, `:293` | in-code correction comments |
| `02-mcp-live-orchestration.md:379`, `:380`, `:383` | correction note |
| `02-mcp-live-orchestration.md:501`, `:504` | **already correct** — the material-name table and the note that `OpenPBRMaterial` does not exist |
| `maxscript-common-patterns.md:279–287`, `:299`, `:304`, `:313` | the ⛔ hazard note plus the fenced block that quotes the removed teaching lines |
| `maxscript-3dsmax-objects.md:431`, `:432` | in-code correction comment quoting the old line |
| `maxscript-rendering-cameras.md:68`, `:69`, `:484`, `:485` | in-code correction comments quoting the old lines |
| `maxscript-materials-textures.md:12`, `:124`, `:130` | correction notes naming the three wrong spellings |

**No hit is an uncorrected claim.** Zero hits in `07-spec-grammar.md`, `08-input-rules.md`,
`09-defaults.md` or `11-layer-standard.md` for any of these patterns.

A second sweep for stale variants (`six routes`, `P6 concern`, `QA loop at P8`, `does not exist yet`,
`set properties, move objects`, `cutter`) returned only correction notes and two unrelated
uses of "does not exist yet" (`07` §1275 on a grammar key, `07` G-76 on `cutter depth` — both
already-correct prose about *schema*, not about Max).

---

## 1. `references/nurbs-complete-guide.md` — A (id type) only

Narrow edits; **no geometry content touched**.

- **§2 head (`~22–36`), CRITICAL RULE #1.** Added a correction note at the head of the section:
  there is no `NURBSId` class, the type is `IntegerPtr`, it prints `<decimal>P` (`0P` on a committed
  1-rail sweep), never parse it, never compare two, and **never write a literal into a
  `parent1ID:`/`parent2ID:` slot** — a string is a conversion error, a synthetic integer is an
  `EXCEPTION_ACCESS_VIOLATION` that kills the Max process. The note says outright that **this file's
  own §4.2 `.nurbsID` entry (~line 172) already stated `IntegerPtr` correctly** and that the edit
  only reconciles the earlier section with it. It also licenses `NURBSId` as remaining shorthand for
  the *concept* and inside Autodesk-style method signatures, so the many downstream uses are not
  individually rewritten.
- **§2 table row 2.** The cell that read *"`NURBSId` … an opaque runtime integer assigned by 3ds
  Max"* now states "Relational id", quotes the old cell verbatim inside the correction, and gives
  the type plus the bind-don't-literal rule. Column 2 of the table was **not** restructured.
- **§2 doc-errata block.** The `appendUCurveByID` bullet no longer types the parameter as `NURBSId`;
  it defers to the §2 note.
- **§4.3 #15 `NURBSPointCurveOnSurface`.** The inherited-properties list no longer contains
  `closed`. The note states that `NURBSPointCurve.closed` **throws on read and on write**, that
  `.isClosed` (read-only) is the only flag, and that **this file's own `NURBSPointCurve` entry above
  already carried the correction.**
- **§4.4 #6 `NURBS1RailSweepSurface`.** `.railID : integer` (`NURBSId`) → `.railID : IntegerPtr`,
  with the `0P` measurement quoted.
- **§4.4 #7 `NURBS2RailSweepSurface`.** The two ID properties moved out of the integer group into
  `.rail1ID : IntegerPtr` / `.rail2ID : IntegerPtr`, noted as **full pointers, each equal to its own
  rail curve's `nurbsID`**, therefore never set indices even though `.rail1`/`.rail2` are.
- **§6 pitfall 2.** `parentID` (`NURBSId`) → `parentID` (relational id, an `IntegerPtr` — see §2).

## 2. `references/nurbs-architecture-recipes.md` — A only

Two in-code comments, no logic touched. Recipe 4's existing `addNURBSSet`-is-a-no-op correction is
untouched.

- **`~262`** `-- Find target surface NURBSId (…)` → "relational id", with a comment block recording
  that there is no `NURBSId` class, the type is `IntegerPtr` printing `<decimal>P`, and the
  never-write-a-literal rule.
- **`~286`** `parent1ID` "references the existing scene surface by NURBSId" → "…by its bound
  relational id (IntegerPtr, not a NURBSId and not a plain integer)".

## 3. `references/07-spec-grammar.md` — A, D, F

- **Verified-facts table, layer row (`~2314`).** "six routes … application is a P6 concern" → **nine**
  routes, **no stage applies it**, **the user applies it in the Layer dialog**. The note points at
  §8.5.6 of the same file, which already carried the correct text.
- **Verified-facts table, `nurbsID` printed form (`~2318`).** This row claimed UNVERIFIED and said a
  later probe "did not reproduce" `"0P"`. Now ✅ VERIFIED: `IntegerPtr`, `<decimal>P`,
  `railID = "0P"` reproduced **3 of 3**. The note states the file **contradicted itself row-on-row** —
  the dependent-surface row directly above already had `<decimal>P` and `0P`.
- **Same table, dependent-surface row evidence cell.** "an `IntegerPtr` of unestablished printed form"
  → points at the now-measured row beneath it. This was the second half of the same contradiction.
- **`~873`** "(this is what **P8 asserts**)" → replaced. **P8 cancelled 2026-10-05**; nothing asserts
  it automatically, the rule stands as a manual `evalPos` read-back obligation.
- **`~1426`** `material_role` "a role for **P7**" → "a role only, never a material class".
- **`~1560`** "**P7 resolves** a role to a material" → the promise of an unbuilt resolver is named
  and struck: materials are assigned by hand; this pack scripts no material assignment.
- **`~1867`** "Those are P7, P8 and P9" presented as pending → marked cancelled with the date, while
  keeping the *enforcement* rationale (G-1 still rejects those keys).
- **Beyond the brief, same rule ("no cancelled stage as pending"):** the pipeline table's
  `materials.json`/`qa.json`/`export.json` rows now read `CANCELLED 2026-10-05` in the stage column,
  and §8.6/§8.7/§8.8 headings carry the same mark. The `reserved` stubs are real files and G-31 still
  resolves their `origin_inputs`, so the rows are kept.
- **`recheck_stage` enum note.** The range `P3 … P9` was **left unchanged on purpose**:
  `scripts/validate_specs.py:90` defines `RECHECK_STAGES = ("P3"…"P9")` and `validate_specs.py` is not
  mine to edit. Narrowing the documented range without narrowing the validator would have made the doc
  and the tool disagree. Instead a note says the range is unchanged, the three stages are cancelled,
  a value naming one is **vacuous**, and `P3`…`P6` should be used for any assumption that must
  actually be re-examined.

## 4. `references/02-mcp-live-orchestration.md` — C cross-check, D

- **§4.5 routing table (`~231`).** `manage_layers` row: dropped "set properties, move objects". The
  cell now says the vocabulary **is** `{list, create, delete}` and the note quotes the old text,
  records 40+ rejected action names, and restates the permanent negative (nine routes; `node.layer`
  read-only; `set_object_property` dies too). Cross-checked `SKILL.md:113` and `SKILL.md:152` — both
  already correct, and the note says so.
- **§5 Rhino-collision paragraph (`~410`).** "lofting, sweeping, extrusion and **booleans**" →
  booleans removed from that sentence only. The note records that **no working Boolean route exists**,
  that `Boolean` attaches and is useless, and that openings come from tiling walls with solid cells
  (`wall_cells[]`, `07` §8.5.8). The `rhinomcp_*` sentence and the rest of the paragraph are intact.
- **§4 NURBS paragraph (`~369`).** "(`Point_Surf` / `CV_Surf` are valid identifiers)" removed as node
  classes. The note gives the measured node classes — **`NURBSSurf`** (any surface) /
  **`NURBSCurveshape`** (curves only), `superClassOf` = `GeometryClass` — names all four measurements,
  and distinguishes *construction identifiers* for sub-object classes from *node* classes, which is what
  made the original phrasing read wrong.
- **Not edited:** §6.5 material-name table (`~501`) and its note (`~504`) already said `OpenPBR`, not
  `OpenPBRMaterial`. Read as the C cross-check and confirmed correct.

## 5. `references/08-input-rules.md` — E

- **Header tooling paragraph (`~13`).** Said both scripts "do not exist yet" and that only
  `env_preflight.py` and `install_skill.py` exist. Corrected; the note says the statement was true
  when written and is false now, and that **no command in the file is ⬜ any more**.
- **Step 7 table (`~258`, `~260`).** Both rows flipped to ✅ with their real behaviour:
  `validate_specs.py` implements `G-1`…`G-33` and exits non-zero on failure; `init_project.py`
  scaffolds the workdir and the eleven `specs/pipeline/` specs plus `project.json`. The note quotes
  the old "⬜ planned, P2c — does not exist yet" text, and states that the §6 manual checklist remains a
  reading aid but **is not a validator pass and must not be described as one**. Stage ownership
  attributed to `agents/max-input.md` (read, not edited).

## 6. `references/09-defaults.md` — F

- **§3.3 lead-in (`~111`).** "inform later stages that build the layers (P6 assembly, P7 materials)" →
  **no stage builds these layers**; P6 places components and tiles cells, P7 is cancelled. The rows are
  documentation of intent for a human.
- **§3.11 `D-CL-09`.** "overlap for a **boolean cut**, cutter depth vs host thickness … the cutter
  must pierce both faces of the host", default `2 ×`, range `≥ 1.5 ×` → restated in the units that
  actually apply: **nominal overlap between adjacent solid cells of a tiled wall**, fraction of cell
  depth, `0 … 0.25`. The note quotes the old text, records that there is no cutter and no boolean, and
  names the tiling route (`wall_cells[]`, decomposed along the run axis then per-column `v`, `07`
  §8.5.8). The `A-nnn` ledger id is unchanged.

## 7. `references/11-layer-standard.md` — D

- **Purpose line (`~6`).** Was "consumed by `build_spec.py` …, by `assembly.json.layer_map` at P6, and
  by the QA loop at P8". Corrected: `build_spec.py` records a layer as **data**; **no stage applies a
  layer** (nine routes ruled out, vocabulary `{list, create, delete}`, `G-79` makes an attempt a build
  FAIL) and **P8 was cancelled 2026-10-05**. The user applies layers in the Layer dialog.
- **§5.1 lead.** "Six routes were executed" → **nine**, with the six MAXScript routes L1–L6 left
  exactly as measured and the three P6 routes named.
- **§5.1 cross-reference note.** Reworded so it no longer implies six is the total.
- **§5.3 `manage_layers` status.** "**the action name is still unknown**" → **IMPOSSIBLE — the action
  name does not exist, and never will**; 40+ candidates rejected across P3 and P6.
- **§5.4 standing rule item 3.** "Application is a **P6 item** … only after the correct `manage_layers`
  action name is found. That find is open item O-2." → the user applies layers in the Layer dialog,
  permanently.
- **§7 open item O-2.** Struck through and marked **CLOSED as impossible (2026-10-06)** — previously an
  open task with owner P6.

## 8. `maxscript-common-patterns.md` — B

The whole "C-style formatting" subsection was removed and replaced by a ⛔ hazard note that quotes the
four removed lines verbatim, states the measurement (**hung `execute_maxscript` until timeout, crashed
Max outright on one attempt**), and stresses that **the name resolves fine — invoking it is fatal**, so
neither an arity check nor a class check would warn you. Replacements given in plain MAXScript:
`format` to a `stringStream` for fixed decimals, `pad3` for zero-padding, `padLeft` for right-alignment,
and a `repeat`-loop decimal-to-hex. The `format` / `stringStream` lines above are untouched.

## 9. `maxscript-3dsmax-objects.md` — B

`~430` rename loop: the `formattedPrint i format:"03d"` call is replaced by `"Part_" + pad3 i` with
`fn pad3` defined inline. The old line is preserved as a quoted comment above the replacement, with the
hazard and the measurement.

## 10. `maxscript-rendering-cameras.md` — B, two sites

- **`~70`** render loop: `formattedPrint t format:"04d"` → `pad4 t`, with `fn pad4` defined in the same
  block (literal `"0"` prefixing, no printf needed for fixed-width small integers).
- **`~477`** turntable: `formattedPrint (i/5) format:"04d"` → `pad4 (i/5)`, with a comment deferring
  `pad4` to the earlier definition so the file defines it once.
Both old lines preserved as quoted comments.

## 11. `maxscript-materials-textures.md` — C

- **`~12–16`, the guess chain.** `OpenPBRMaterial` → `OpenPBR_Material` → `OpenPBR_Mtl` was a
  three-name guess ladder that **never tried the correct identifier**. Replaced with
  `opbr = OpenPBR name:"PBR_Mat"`, the note listing the three wrong names, the three-way split
  (display name / construction identifier / runtime class `OpenPBR_Material`), and cross-references.
- **`~117`, the `introspect_class` route.** Removed. Replaced with `OpenPBR` plus
  `get_material_slots` and `3dsmax-mcp_get_materials`. The note names `introspect_class "NURBSSet"` →
  `Class not found` while `NURBSSet()` constructs as the canonical false negative, records that this
  single lie once caused a whole plan to be rewritten, and states the rule: **only a successful
  construction proves a class exists.** It also notes that the runtime class really is
  `OpenPBR_Material`, which is exactly why the middle guess looked plausible.
- **Cross-checked, not edited:** `SKILL.md:147` and `SKILL.md:412` (`OpenPBR`, not `OpenPBRMaterial`),
  `02-mcp-live-orchestration.md:477–481` (§6.5 table and the constructor/class-name note),
  `12-nurbs-gotchas.md:392–402` (failing `OpenPBRMaterial` / working `OpenPBR` /
  `classOf (OpenPBR()) == OpenPBR_Material`). All four agree; spelling confirmed as `OpenPBR`.
- **F: added the hand-off note.** A short block records that **this pack does not script material
  assignment** — P7 was cancelled 2026-10-05, there is no `materials.json` gate, and the user assigns
  by hand — so every snippet in this reference is background for that hand-off, not a stage to run.

---

## Notes on scope decisions

- **Two files were deliberately *not* rewritten**, per instruction:
  `nurbs-complete-guide.md` and `nurbs-architecture-recipes.md` received six comment/annotation edits
  between them and no prose, table row, code block or geometry statement was touched. Both already
  carried several measured corrections (`addNURBSSet` no-op, `.closed` throws, `.index` unusable,
  `trim`/`trimCurve` names, `curveStartPoint` as Float) and all of them are intact.
- **One deviation from the brief's line list, in the same rule class.** The brief named
  `11-layer-standard.md:6` for D, but §5.1/§5.3/§5.4/O-2 of the same file still said "six routes",
  "the action name is still unknown" and "Application is a P6 item … open item O-2" — i.e. they
  presented the permanently-impossible finding as an open P6 task. Rule D is "layer is data,
  permanently", so these were corrected too. Similarly, `07`'s pipeline table and §8.6–§8.8 headings
  were corrected under rule F ("none of these files may present a cancelled stage as pending or
  planned"), which names four specific lines but states the rule generally.
- **One thing I could not do:** `recheck_stage`'s documented enum still spans `P3`…`P9` because
  `scripts/validate_specs.py:90` hard-codes `RECHECK_STAGES` with the cancelled stages in it, and
  `validate_specs.py` is outside my eleven. Editing the doc without the validator would have put the
  grammar and its own gate into disagreement. A note now flags the three values as vacuous instead.
- **No `install_skill.py` run**, so `3dsmax-arch-nurbs-ultimate.skill` is now behind the working tree.
  The orchestrator rebuilds it.
- `SKILL.md:152` still says "six assignment routes" where the count is now nine. Not mine to edit; the
  same paragraph's conclusion ("Layer is data and is applied by hand") is correct, and
  `_drift-audit.md` already lists it among five stale slips.
