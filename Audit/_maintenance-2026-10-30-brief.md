# Evidence brief — maintenance pass, 2026-10-30 (session 2)

Read this first. These are **measured or user-decided facts**; do not re-derive them, and do not
re-litigate them. Written by the orchestrator so concurrent subagents share one copy.

## 1. User decisions taken in the main thread this session (authoritative)

| # | Decision |
|---|---|
| U1 | **Option C+ on `references/_form-units-qa-design.md` is AUTHORISED.** Move the three contiguous blocks + the 2 DEAD sections into a new `Audit/FORM-QA-SESSION-LOG.md`. Two line-splices. |
| U2 | **Option D (§17, ≈ −60.5 KB) is NOT authorised.** §17 must stay byte-identical. §17.1 is cited by `scripts/qa_check.py:152`; §17.2–§17.7 are the schema its emitter implements. Do not touch §17 in any way. |
| U3 | **The 5 `semantic_hash == ""` files stay pending.** `scripts/build_nurbs.py`, `references/_form-units-qa-design.md`, `Audit/AGENT_BRIEF_form_precision.md`, `Audit/AGENT_PLAN_form_precision.md`, `Audit/CHECKPOINT-archive-2026-10-28.md`. Do not extract, stamp or "fix" them. |
| U4 | The 2026-10-30 errata block at the head of the FROZEN doc **stays**. You may APPEND a dated line to it; never rewrite or delete what is already there. |

## 2. Measured now, by the orchestrator (2026-10-30, HEAD `268abb4`)

- `references/_form-units-qa-design.md` = **273,208 bytes / 2,816 lines** in its CURRENT state.
- `Audit/_form-qa-citation-map.md` inventories **267,728 bytes** and its line numbers are
  **PRE-errata**. The errata insertion of 2026-10-30 added **+44 lines / +5,480 bytes**
  (267,728 + 5,480 = 273,208 ✔).
  ⚠️ **So every line number in the citation map — including the C+ block ranges
  `1160–1263`, `2240–2330`, `2674–2731` — must be shifted by +44, or better, resolved by
  section anchor / by matching the block's own heading text.** Cutting at the raw citation-map
  line numbers would slice 44 lines early and corrupt the file. This is the single most likely
  way to fail this task.
- Files that mention `_form-units-qa-design` by name (9): `agents/max-input.md`,
  `Audit/AGENT_PLAN_form_precision.md`, `Audit/AGENT_PLAN_poly_surface_shell.md`,
  `Audit/EVIDENCE_2026-10-27.md`, `Audit/_form-qa-citation-map.md`, `CHECKPOINT.md`,
  `references/07-spec-grammar.md`, `scripts/qa_check.py`, and the doc itself.
- `Audit/EVIDENCE_2026-10-27.md:175` reads `:2693` and is **frozen data — leave the file
  untouched**, exactly as the 2026-10-30 pass did. Its offset note changes again because of your
  cut; record the new offset in the doc's errata block (append-only) and in your report.

## 3. Packaging facts (already verified, do not re-check)

- The `.skill` archive at HEAD is **byte-identical to the working tree** (107 entries, 0 differ) and
  both installed copies (`~/.claude/skills/3dsmax-arch-nurbs-ultimate`,
  `~/.agents/skills/3dsmax-arch-nurbs-ultimate`) differ on **0** files.
- Both installed copies carry **5 stale extra files** that the repo moved to `Audit/` on 2026-10-28:
  `references/_drift-audit.md`, `references/_fix-a-notes.md`, `references/_fix-b-notes.md`,
  `references/_fix-c-notes.md`, `references/_fix-d-notes.md`. Cause: `install_skill.py` copies
  without pruning.
- `Audit/` is **not** packaged. Consequence of C+: the moved session-log content leaves the shipped
  skill. That is intended (it is NARRATIVE/DEAD material), **provided** none of the 13 live
  citations resolves into a moved block. Proving that is a gate — see §4.
- After any edit, the archive must be rebuilt: `python scripts/install_skill.py`.
  **The orchestrator runs this, not you.**

## 4. Gates for the C+ cut (all must be measured, not asserted)

1. **No live citation may point into moved content.** Enumerate the 13 live citations from
   `Audit/_form-qa-citation-map.md` and show, for each, that its target section anchor survives.
   If even one lands inside a block you were about to move — **STOP, move nothing, report it.**
2. **§17 byte-identical** (U2). Show the hash of the §17 span before and after.
3. **Errata block byte-identical** except for appended dated lines (U4).
4. **Byte reduction measured**, and the arithmetic must close:
   old 273,208 − moved = new size, and the moved bytes land in `Audit/FORM-QA-SESSION-LOG.md`
   (its size ≈ moved bytes + whatever header you add).
5. **`scripts/qa_check.py` still imports and runs** — it routes to this doc.
   `python -m py_compile scripts/*.py` exit 0, and the QA emitter path still resolves.
6. **`python scripts/validate_specs.py --dir examples` still PASS / FAIL 0.**
7. **`Audit/_form-qa-citation-map.md` updated** so its inventory sums to the NEW byte total and its
   line numbers are post-cut. State the new sum explicitly.
8. Every edit outside your declared file ownership must be listed in your report with a reason.

## 5. Repo conventions that bind you

- `CHECKPOINT.md` is **owned by the orchestrator**. Do not edit it. Report your facts instead.
- A `.ms`/CSV/doc is not done until measured — no claim without its own transcript.
- Never invoke `formattedPrint` through the Max bridge (irrelevant here unless you probe Max;
  you should not need Max at all for this pass).
- Give your scratch files their **own** directory and delete **only the files you created** —
  a shared scratch dir plus "delete the scratch dir" destroyed 6 orchestrator scripts on
  2026-10-30 (incident-log trap 11).
- Final report: **under 15 lines**, structured. Artifacts carry the detail, not the message.
