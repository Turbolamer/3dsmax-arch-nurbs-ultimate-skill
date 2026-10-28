# _fix-c notes — the P7/P8/P9 cancellation sweep

**Pass C, 2026-10-06.** Owner: eight files only, listed below. **No `3dsmax-mcp_*` tool was called and
no live bridge was touched** — every fact written into these edits was handed to the pass as data and
was **not** re-derived. `install_skill.py` was **not** run; the orchestrator rebuilds the archive.

## Files touched

| File | What changed |
|---|---|
| `references/01-architecture-aec-workflow.md` | Title retargeted S0→S5 + correction banner. §2 spec-chain rows 9–11 struck through and marked CANCELLED with a notice naming the three nonexistent agent files; the "row 10 has no upstream sibling" paragraph retained verbatim and immediately retracted. §3 S5's three bad rows rewritten (layer gate closed as a permanent negative · scatter declared-not-built · no Boolean cut path) with a dated notice per claim. The S6/S7/S8 six-row contracts replaced by a "The cancelled stages" section. §5's S7 determinism consequence rewritten. §9.1 and §9.2's layer rows closed. |
| `references/14-chaos-scatter.md` | Title and §5 heading dropped the P8 hook; correction banners added. §5.1 reframed as an optional manual verification, with the `agents/max-assembly.md §7 row 8 runs steps 5 and 9` claim retracted (it does not). §6 `node_name` row de-node-ified. §6 intro's "the builder owns the class name" corrected. §7 retitled the hand-application library. AP-10 corrected. |
| `snippets/chaos_scatter.ms` | Four comment blocks reframed: header gained "WHY YOU ARE LOADING THIS FILE" (declared, hand-applied, changes the node count) and "OPTIONAL MANUAL VERIFICATION"; `rebuild`, the section banner, `snapshot` and `determinismRoundTrip` comments de-P8'd. **No executable line was touched** — `/*` and `*/` counts are 10/10 before and after. |
| `agents/max-assembly.md` | §1's purpose paragraph corrected (it contradicted §1.1 row 44, which was already right). §1.1 rows 43/45/47 de-staged. §2.1's "S7 determinism hook", §2.2's "fails S6", §6.7's "those are S6, S7 and S8", and two anti-pattern/escalation seed cells corrected. Report template's "scatters" → "scatter declaration rows". |
| `agents/max-massing.md` | Purpose + consumer rows retargeted S0→S5. §1.1: `assembly.json.cuts` → `wall_cells[]`; materials row cancelled; layer row made permanent; scatter row's **`scatters` → `scatter`** with `qa.json`/`export.json` marked as cancelled stubs. §1.2, §7 row 9 and one anti-pattern row: layer "unknown / S5's problem" → permanent negative. |
| `agents/max-facade.md` | §1.1 rows: scatters → scatter declaration; materials cancelled; **layer row reuses `max-assembly.md` §6.3's wording verbatim**; reveals row cancelled. §1.2 forbidden cell, §6.7, AP-5 and AP-9 all corrected. |
| `agents/max-components.md` | §1.1 materials / reveals / layer rows corrected; §1.2 forbidden cell corrected; the stray "S6b" in §6 corrected; §10's "P7 resolves roles to materials" corrected. |
| `agents/max-nurbs.md` | Purpose line 7 ("facades, materials and everything after") corrected. Consumer row retargeted. §1.1 materials + layer rows corrected. §6.2's "asserted by P8", §6.4's `matID` row, the §7 verified-facts layer row and AP-10 corrected. §12's "S0→S8 chain" → "S0 → S5". |

## Beyond the brief — four extra fixes, and why

The brief listed specific line numbers; these four were **the same falsehood** as briefed ones and sat
inside files I already owned, so leaving them would have made the files self-contradicting. Each is
flagged in place with a dated correction.

| Location | Was | Why it had to go with the briefed fix |
|---|---|---|
| `agents/max-massing.md` §7 row 9 | "Assignment is S5's problem and the action name is unknown" | The brief's own §-51 rule says "any text saying *the real action name is unknown, that is S5's problem* is wrong on both counts". Same sentence, one screen further down |
| `agents/max-massing.md` anti-pattern table | "six routes executed, all threw. Layer is data; S5 applies it (§7)" | Same. Note this file already contradicted itself — §1.1 line 39 said the same thing |
| `agents/max-nurbs.md` §7 verified-facts row | "S5 applies `assembly.json.layer_map`" | Same, and it is the file's own transcript-of-record table |
| `agents/max-nurbs.md` AP-10 | "Layer is data; S5 applies it" | Same |

I did **not** widen further. In particular I left two stale-but-unrelated claims alone and am reporting
them instead:

- **`references/01` §2, "row 4" paragraph** still says "`examples/massing.json` is P3's outstanding
  deliverable, so row 4 is schema-defined but not yet example-proven." **`examples/massing.json`
  exists** (confirmed by listing `examples/`). This is a staleness bug in the same paragraph I edited,
  but it is not a cancellation fact and fixing it would have been an unverified inference about what P3
  did or did not close. **Orchestrator's call.**
- **`agents/max-components.md` §6** said "a family that declared any other policy would be promising an
  interchangeability S6b cannot honour." `S6b` is not a stage in any reading I could find — it looks like
  a typo for S6. I annotated it (there is no S6b, and S6 was cancelled) rather than guessing what the
  author meant.

## Verification actually performed

```
$ python -m py_compile scripts/*.py && python scripts/validate_specs.py --dir examples | tail -3
PASS 138 / FAIL 0 / WARN 0 / SKIP 15
exit 0 -- no FAIL rows
EXIT=0
```

Both commands run from the repo root; **exit 0, and the counts match the expected
`PASS 138 / FAIL 0 / WARN 0 / SKIP 15`** exactly. Nothing under `scripts/`, `examples/` or `specs/`
was touched, so this is a regression check, not a change in spec state.

The residual-term grep was then run over **all eight files**, and **every remaining hit was read by
hand** rather than assumed. All of them sit inside one of four shapes:

1. a struck-through spec-chain row marked `CANCELLED 2026-10-05`;
2. a `**CORRECTED (2026-10-06):**` notice that **quotes the old text in order to retract it** — this is
   the house style, and it is why the grep cannot be driven to zero;
3. the "The cancelled stages" table in `01` §3, whose middle column is deliberately *"was"*;
4. an explicit "these are reserved stubs, not planned work and not a gate".

`scatters` (plural) now appears **zero** times as a live key anywhere in the eight files. The only
occurrences are the two correction notices that name it as the wrong key
(`agents/max-massing.md` §1.1, `agents/max-facade.md` §1.1).

`snippets/chaos_scatter.ms` was checked structurally rather than semantically: **only comment text
changed**, and the block-comment delimiters still balance at 10 `/*` against 10 `*/`. I did not execute
MAXScript — **no bridge call was permitted in this pass**, so the snippet remains
`fileIn`-unverified after this edit. Its executable lines are byte-identical to the last run, so the
previous load result still stands; **a `fileIn` after this pass is cheap insurance, not a requirement.**

## Not done, deliberately

- `install_skill.py` not run — the `.skill` archive is a build product and the orchestrator owns it.
  **The archive is now stale with respect to all eight files** and must be rebuilt before shipping.
- No other file was modified. `agents/max-orchestrator.md` §5 (the hand-off) and `references/07` §4
  (where rows 9–11 are declared `reserved`) still describe the cancelled stages in their own terms.
  Both are outside this pass's ownership; **if `07` §4 still says `reserved` rather than `cancelled`
  for those rows, that file now disagrees with `01` §2** and one of the two is wrong.
- No live probe. Nothing here claims a new Max fact; every claim added is either given data or a
  pointer to the file that owns it.
