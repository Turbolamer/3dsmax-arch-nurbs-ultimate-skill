# `_fix-a-notes.md` — correction pass A, 2026-10-06

Two files owned by this pass, one extra file created (this one). No script, spec, example or other
reference was touched. No `3dsmax-mcp_*` tool was called — no live bridge in this session; all facts
below were supplied as measured data from live Max 2026.3.2.

---

## 1. `snippets/nurbs_arch_library.ms` — the one executable defect in the pack

### The defect

`applyArchTessellation` (function §5, ~line 86) built its **render** approximation as:

```maxscript
curvatureAngle:(degToRad angleDeg)
```

`curvatureAngle` is specified in **degrees**. `angleDeg` is a degrees value (keyword default `6.0`),
so the `degToRad` wrapper did two wrong things at once:

1. it reinterpreted a degrees number as if it were already radians, and
2. it shrank the value by ~57×, which over-tessellates every render approximation the library has
   ever produced — silently, since the result still looks like a valid mesh.

### The change

`curvatureAngle:angleDeg` — the degrees number is passed through unchanged — plus an 8-line dated
notice above the statement carrying the unit, the reason, and the measured proof.

```
        -- CORRECTED (verified 2026-10-06): curvatureAngle is in DEGREES, not radians, so angleDeg
        -- is passed through unchanged; the previous (degToRad angleDeg) both misread the unit and
        -- over-tessellated. Measured on a quarter-cylinder NURBSPointSurface with
        -- meshApproxType:#curvature and a loose curvatureDistance: curvatureAngle 6.0 -> 101 verts,
        -- 0.10472 (= degToRad 6.0) -> 691 verts, i.e. ~6.9x too dense. The discriminating evidence:
        -- on a 90-degree arc the mesh reaches its 25-vert floor at >= 40 degrees, while 1.5708
        -- (pi/2 rad) sits in the DENSE region -- under a radians reading pi/2 would already be
        -- maximally coarse, which it is not.
        local rApprox = NURBSSurfaceApproximation config:#meshOnly meshApproxType:#spatialAndCurvature spacialEdge:edgePct curvatureAngle:angleDeg curvatureDistance:0.2 merge:mergeTol subdivStyle:#grid
```

Notes on the edit as written:

- The statement is still **one well-formed `NURBSSurfaceApproximation …` call** on one physical line.
  All nine keyword arguments are unchanged in name, order and value except `curvatureAngle`, which
  changed from `(degToRad angleDeg)` to `angleDeg`.
- The comment sits **inside** the `fn … = ( … )` body, between two `local` bindings, so it parses as
  a `--` comment in an ordinary statement position. Existing explanatory comments above the function
  were left alone; comment density in this file is normal and was not reduced anywhere.
- Backticks were deliberately **not** used in the `.ms` comment. Backtick is MAXScript's string
  escape character; inside a `--` comment it is inert, but a comment that needs the lexer's escape
  processing rules to be harmless is a comment that was not worth the risk in a shipped library. Plain
  text instead, matching the surrounding style.
- The other two bugs in this file recorded in `AGENTS.md` — `appendObject` used as an index, and
  `stopCreating` called with an argument — were **already fixed** in the working tree (functions §6 and
  §7 call bare `stopCreating`, and `local surfIdx = nset.numObjects` follows `appendObject`). No edit
  was needed or made for either. Bug 3 (`NURBSControlVertex`) is likewise already handled: §3 and §12
  wrap every control vertex in `NURBSControlVertex <pt> <weight>`.

---

## 2. `references/12-nurbs-gotchas.md`

### 2a. Section 5, "Boolean / solid ops" (~line 1065) — was false

**Before:** "`Boolean` geometry object and the `Boolean` modifier are available; this is the practical
route for cutting openings in slabs and walls", followed by a 10-line `Boolean()` + `addModifier` +
`boolMod.operand = b` snippet. That snippet cannot work, and — worse — it is the exact shape that made
the previous `assembly.ms` ship unpierced walls while its own census reported success.

**After:** the claim is replaced with the measured result, matched in wording and level of detail to
the two authoritative sources, which were read before editing:

- `references/07-spec-grammar.md` §8.5.8.1 (lines 1903–1926) — "Why this array **replaces** cutting"
- `agents/max-assembly.md` §6.2.1 (lines 231–251) — "Why there is no cut path here"

Both carry the same six-row probe table, and that table is reproduced here with its verdicts intact:

| Probe | Measured |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs, `classOf` reads `BooleanMod`, but its paramblock is **Voxel Map's** (`voxelSize`, `toleranceFactor`, `bevelDistance`, `bevelDepth`); `VoxelMap()` is itself `NotCreatable` |
| `ProBoolean()` | constructs, `superClassOf` is `GeometryClass` not Modifier, and constructing one **leaves a node in the scene** |
| bridge `add_modifier` with `"Boolean"` | genuinely **attaches** — `node.modifiers` reads `#modifiers(Boolean:Boolean)` — and the **operand is never set**: `snapshotAsMesh` reports `verts=8 faces=12`, unchanged, for every `params` spelling tried |
| `isProperty m #operation` / `#object` / `#boolobject` | all **`false`**, and the bogus control is also `false`, so those names genuinely do not exist |
| `getModifier 1 node` | **throws**; `node.modifiers[1]` works |

The bogus-name control is called out in the lead-in, because per §4 of this same file a class-existence
claim without one has produced no evidence at all.

Two consequences are stated, both taken from the sources rather than invented:

- **"A modifier that attaches and does nothing is worse than one that throws."** The previous
  `assembly.ms` shipped unpierced walls *and reported success*, because its census counted iterations
  of its own loop (`cut_count = 16`) against a scene with zero modifiers anywhere.
- **The working route is absent material, not a cutter.** There is no cutter object at all. The wall
  is built from solid cells that tile wall-minus-openings exactly — `wall_cells[]` in
  `assembly.json`, one `plan_rect_cm` + `z_range_cm` box per cell, cut at every opening's `u`
  boundary into columns then at the covering openings' `v` boundaries into rows. The stage emits no
  modifier at all (`G-81`) and the tiling is asserted as a **volume identity** (`G-82`/`G-83`) — the
  check a Boolean could never have satisfied, since a modifier that removes nothing leaves the volume
  untouched.

The old `maxscript` snippet was **deleted**, not left alongside. Unlike a prose claim, an executable
snippet that cannot work is an active hazard: it is copy-pasteable. This is the one place in the file
where the correction is a removal rather than a superseding notice, and it is deliberate — the
replacement carries its own dated measurement.

### 2b. "Tessellation for export" (~line 1081) — correct advice, wrong framing

**Before:** "NURBS patches must be tessellated before FBX / OBJ export; a patch that looks right in the
viewport will export as garbage or as nothing otherwise."

**After:** retitled **"Tessellation quality for viewport and render"** and reframed. The
`NURBSSurfaceApproximation` / `setViewApproximation` / `setRenderApproximation` advice is **kept
verbatim in substance**, as required — it is correct and it is the NURBS-native route. Only the export
framing is gone, replaced by a plain statement that **there is no export stage in this pack** — export
was cancelled by user decision on 2026-10-05 and no exporter exists.

One line was **added** while in this paragraph, tying the two halves of this pass together: a ⚠️
noting `curvatureAngle` is in degrees and that passing `degToRad` over-tessellates (~6.9× measured),
pointing at the fixed function. A reader who reaches `NURBSSurfaceApproximation` in this file should
not have to open the `.ms` to learn the unit.

The adjacent `> **UNVERIFIED.**` note was kept but de-exported: it still records that the
`Disp Approx` / `Tessellate` modifier-stack path is unverified for patches, which remains true; only
the pre-export rationale was dropped.

### 2c. Two further places that repeated the same false claim

A `grep` for `Boolean` over this file found the section above plus **two more spots** carrying the
disproven "Boolean modifier or a surface split" phrasing. Both would have left the file contradicting
its own correction, so both got the same narrow, dated treatment — operative clause unchanged, only
the unusable route named differently:

- **line ~758** (§3.25, "Cutting an aperture in a NURBS surface is not something this class does.")
  → now "**absent material or a surface split**".
- **planning rule 19** (~line 1151) → same substitution.

The `Boolean` on **line 979** is a different thing entirely — it is one name in a list of creatable
primitives (`Teapot, Plane, Bone, Boolean, ChamferBox, …`). Untouched.

### 2d. Planning rule 15 — `nurbsID` "string" was a self-contradiction

**Before:** "They read back `0`, a `nurbsID` string, or a sign-flipped vector (3.16, 3.17)."

**After:** "They read back `0`, an **`IntegerPtr`** (never a string — see 3.29), or a sign-flipped
vector (3.16, 3.17)."

The file already said the opposite in three places, which is what made the error unambiguous:

- rule 18, ~line 1150 — "`nurbsID` is an `IntegerPtr`; a string errors"
- §3.16 row, line 512 — "an **`IntegerPtr`**, printed as a large decimal followed by `P`"
- §3.29, line 837–854 — full measurement: `classOf` is `IntegerPtr`, printed form `<decimal>P`,
  e.g. `3253572981568P`; `railID = "0P"` was **real**; `rail1ID`/`rail2ID` equal the rail curve's own
  `nurbsID`; the value changes between builds of identical geometry, so **never persist one**

Only the type word was wrong, so only the type word changed. The pointer at 3.29 was added because
that section now carries the measurement; rule 15's own citation of (3.16, 3.17) is kept, since the
operational rule — *never round-trip-assert, assert on `evalPos` or the surface count* — is unchanged
and does not depend on the format.

Note this is the **second** recorded instance in this repo of a claim about a `nurbsID` being resolved
the wrong way, and it arrived via the same signature: a signature error or a difference from
expectation, read as evidence about the feature. `3.16`'s own 2026-10-06 note calls that family out.

### 2e. §7.6 items 1 and 2 — **already resolved, no edit needed**

Checked as instructed; both are already closed and were left exactly as they are:

| Item | Status in file |
|---|---|
| printed string form of an `*ID` | `~~struck~~` + **"RESOLVED 2026-10-06 — see 3.29"**, Pointer `3.29`, "What is open" = *— closed* |
| `numCVs = [9,4]` on the `trim:true` copy of a 5-rib loft | `~~struck~~` + **"RESOLVED 2026-10-06 — see 3.30"**, Pointer `3.30`, *— closed; **no rule may be written against it*** |

Both answers match what was supplied: item 1 is the `IntegerPtr` / `<decimal>P` format (§3.29), and
item 2 is the parent surface's own CV conversion — §3.30 measures it (two structurally different
profiles both give `[9,4]`; `u` tracks the parent's points-per-section **and** its curvature; `v` is
fixed at `4`) and the file correctly forbids writing a rule against it.

**This is the second contradiction removed rather than introduced**: editing rule 15 was mandatory
precisely because §3.29 already contradicted it.

### 2f. §7.4 heading — closed the last export contradiction

Retitled **"Correct tessellation path for patches — viewport / render, NOT export"** with a dated
notice recording that there is no export stage. Without this, §7.4 would have contradicted the new
statement 250 lines above it. Its trailing sentence "verify the export path end-to-end on one patch"
became "verify the viewport and render result end-to-end on one patch". The probe body above it was
**not** touched — whether `Tessellate` / `Disp_Approx` apply to patches is still a real open question
and is still labelled so.

---

## 3. Verification

```
$ python -m py_compile scripts/*.py && python scripts/validate_specs.py --dir examples 2>&1 | tail -3
PASS 138 / FAIL 0 / WARN 0 / SKIP 15
exit 0 -- no FAIL rows
```

**Matches the expected result exactly.** This is the load-bearing check, because a FAIL here would have
meant an edit reached something the specs depend on — this pass was docs plus one MAXScript line, and
neither `validate_specs.py` nor any builder reads either file.

Structural checks on the `.ms` edit, by eye (no MAXScript interpreter in this session):

- the `NURBSSurfaceApproximation` statement is still a single, well-formed call on one line;
- all nine keyword arguments unchanged in name, order and value except `curvatureAngle`;
- `angleDeg` is in scope — it is the function's own keyword argument (`angleDeg:6.0`, line 81);
- the 8 added lines are `--` comments inside the `fn` body between two `local` bindings;
- `degToRad` occurs **only inside the correction comment** (naming the removed form and the 0.10472
  measurement), never as an executable argument — it had exactly one use in the file and that use is
  gone;
- `angleDeg` is still passed nowhere else, so no other statement inherits the unit error;
- the `struct` closes and `global MCP_NURBS_Arch = MCP_NURBS_Arch_Lib()` is untouched;
- no comment was stripped anywhere in the file.

## 4. What was not done

- **No live Max verification.** No `3dsmax-mcp_*` tool was called, by instruction — there is no bridge
  in this session. The `.ms` edit is therefore verified **by inspection**, not by `fileIn`. Per
  `AGENTS.md`, "an emitted `.ms` is not done until it has been `fileIn`-ed and measured"; that gate
  belongs to whoever next has the bridge open. Nothing else in this pass depends on it — the change is
  a unit correction to one argument value, and both readings are known to construct.
- **`CHECKPOINT.md` was not updated.** The repo convention says to update it at the end of every
  stage, but it is outside this pass's ownership. The facts here (Boolean unusable, `curvatureAngle`
  in degrees) are already recorded in `AGENTS.md`, `07` §8.5.8.1 and `max-assembly.md` §6.2.1, so
  nothing is unrecorded — but a stage-owner should still add the pass to the incident log.
- **`references/07-spec-grammar.md` and `agents/max-assembly.md` were read, not modified.** They are
  the authoritative corrected text and are already right.
- **P7 materials / P8 QA / P9 export remain cancelled.** This pass only removed the *file's* claim
  that an export stage exists; it did not add, revive or stub anything.