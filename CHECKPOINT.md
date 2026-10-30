# CHECKPOINT — progress tracker

**This file is the source of truth for what is done, what is verified, and what is assumed.**
Update it at the end of every stage. Read it before starting new work.

Last updated: 2026-10-30 (**maintenance pass 3 — the §"Dangling references" register re-checked and
CLOSED, 4 live routes to absent tools fixed, graph drift from the C+ cut measured and recorded as an
accepted remainder; pass 2 the same day — C+ cut applied to the FROZEN form-QA doc, installer prune
added, 4 dangling/stale anchors repaired, archive rebuilt and re-measured; earlier still: maintenance
item 5 — deep semantic re-extraction of the knowledge graph. Previous entry 2026-10-28: general
cleanup, slimmed to current state, the full history 2026-10-04…2026-10-27 archived verbatim in
`Audit/CHECKPOINT-archive-2026-10-28.md`**). **The maintenance queue is now empty of authorised
work — next is P2 (`walls.json`).**

**Archive policy (2026-10-28).** This file carries only: the current phase, the stage-status
board, §"Verified facts" (the transcript of record — never trim it), the routing tables
(§"Tooling that always fails", §"Unverified", §"Dangling references"), the material-propagation
finding, the curated standing-traps log and the next-action queue. Everything older — closed-phase
progress logs, closed-stage sections, full incident transcripts, superseded "Resume here" sections
— lives in `Audit/CHECKPOINT-archive-<date>.md` (repo-only: `Audit/` is not packaged in the
`.skill` archive, so installed agents never pay context for history). When a phase closes, cut a
new archive file and leave the previous ones untouched — history is appended, never rewritten.
§-references that point into pre-2026-10-28 phase sections (§P2, §P12, §P13, §"P5 — the live
gate", §"P10-lite", §"P7 — what the cancelled probes proved", …) resolve **in the archive file**.

## 2026-10-30 — Maintenance pass 3: dangling-reference register CLOSED, graph drift recorded

**Trigger.** While answering "is the general cleanup finished?", the orchestrator measured the
§"Dangling references" register against the files it names and found **the register was the drift,
not the reference files** — 3 of its 6 rows were already clean and its citation (`00-audit-p1.md` §7)
points at a section that lists no dangling references at all. A subagent then re-checked all 7 files
with a catalog-derived inventory; verdict table, evidence and the four diffs are in the register
itself (replaced in place, marked **CLOSED**) and in `Audit/_dangling-register-recheck.md`.
**4 LIVE ROUTE defects fixed** in 3 files (`execute_python`, `set_modifier_property` ×2,
`draw_spline`), **0 OBSOLETE routers added**, plus one orchestrator edit upgrading `add_offset` from
UNVERIFIED to measured-absent. Regression: `py_compile` exit 0, `validate_specs --dir examples`
PASS 138 / FAIL 0 — the fixes are prose-only and touch no gate.

**The transferable lesson, recorded because it cost a near-miss.** The orchestrator's own crude
pre-scan found **2 of the 4** defects. It missed the other two because it searched for the
absent-tool names listed in `AGENTS.md` — and `execute_python` / `set_modifier_property` are not in
that list. **A hand-maintained inventory of wrong things cannot find a wrong thing nobody wrote
down.** The scan that worked diffed every backticked identifier in the files against the **live tool
catalog**. Same shape as the repo's standing rule on probes: a check calibrated only against what you
already suspected produces a result, not evidence.

**Graph drift caused by pass 2's C+ cut — measured, accepted as a remainder, do NOT hand-fix.**

| observation | measurement |
|---|---|
| new file unregistered | `Audit/FORM-QA-SESSION-LOG.md` is **absent from `graphify-out/manifest.json`** (120 rows, none is this file) |
| rows drifted from their AST stamp | **4** — `scripts/install_skill.py`, `CHECKPOINT.md`, `references/_form-units-qa-design.md` (pass 2/3 edits) and `Audit/AGENT_PLAN_poly_surface_shell.md` (**pre-existing**, from the 2026-10-30 re-anchor of `:385`, not from this pass) |
| nodes describing moved content | ≥1 — `Unresolved register U01-U22 [src=references/_form-units-qa-design.md loc=None]` is §13.3, which now lives in the session log. A `graphify query` can route an agent to a file that no longer holds the text |
| nodes naming moved sections **by number** | **0** — so a number-keyed scan cannot find the misattribution. It is by concept, not by section label |
| `.evidence-brief.md` | still states **2911 nodes / 7119 edges** (accurate), makes no pre-cut size claim, does not mention the session log — stale-ish but **not actively misleading**, unlike the version pass 2 replaced |

**Why it stays open:** re-stamping the 4 AST rows is deterministic and cheap, but registering and
semantically extracting the new `Audit/` doc needs the subagent extraction pipeline again (no LLM
backend runs headless here), and `Audit/` is not packaged in the `.skill`. Deferred on exactly the
logic of item 5's remainder — a future `graphify extract` picks all of it up. **Do not hand-stamp the
manifest** (see item 5's positive control: `ast_hash` must equal the stored md5 on 119/120 rows).
**Not blocking P2…P6.**

## 2026-10-30 — Maintenance pass 2: C+ cut applied, installer prune, anchors repaired (COMPLETE)

**User decisions taken this session, authoritative:** option **C+ authorised**; option **D NOT
authorised** (§17 must not move); the **5 pending `semantic_hash == ""` files stay pending**; the
2026-10-30 errata block stays **append-only**. Work was split across two concurrent subagents with
disjoint file ownership from a shared brief (`Audit/_maintenance-2026-10-30-brief.md`), then
**re-measured by the orchestrator** — every number below is an independent measurement, not a
subagent claim.

**C+ cut, measured.** `references/_form-units-qa-design.md` **273,208 → 253,557 B**
(2,815 → 2,632 lines). Moved **26,161 B / 293 lines / 5 blocks (11 sections)** into the new
`Audit/FORM-QA-SESSION-LOG.md` (**31,848 B**): §6.2 and §7.1 (both DEAD), §13.3+§13.4, §19.1+§19.2,
§24+§24.1–§24.4 (NARRATIVE). Each block was located **by heading text**, never by the citation map's
line numbers — those are pre-errata and off by **+44**. The arithmetic closes:
`273,208 − 26,161 + 2,542 (5 pointer stubs) + 2,948 (errata append) + 1,020 (orchestrator's UPDATE
paragraph) = 253,557`.

| gate | measurement |
|---|---|
| **§17 untouched (D refused)** | sha256 of the §17 span **`a26547404175afec`** before *and* after; §16 `4e7c6ec489bdff48` and §18 `1e1d58e4087932f9` also identical — a neighbour control, not just the target |
| body edits are only the splices | `difflib` over the post-errata tail: **exactly 5 change hunks**, each `moved section → stub` (§6.2, §7.1, §13.3–13.4, §19.1–19.2, §24–24.4), 0 other body edits |
| moved content really moved | 10/10 sub-section headings absent from the doc, present verbatim in the log |
| errata append-only | blockquote **42 → 78 lines**, first 42 byte-identical |
| doc is still the largest `.md` | **253,557** vs `references/07-spec-grammar.md` 237,187 — C+ did not dethrone it, exactly as the citation map predicted |
| regression | `py_compile scripts/*.py` exit **0**; `validate_specs.py --dir examples` **PASS 138 / FAIL 0 / WARN 0 / SKIP 23**; `qa_check.py` imports with all **6** route mentions intact |

**Four anchors repaired — only the URL inside `]( )`, no prose rewritten.** §1's `[§19.1]` and both
`[§24]` links now point at `../Audit/FORM-QA-SESSION-LOG.md#…`; the **pre-existing** `[§23.3]` slug
(stale since the 2026-10-10 heading rename, so *not* charged to the cut) was re-pointed at
`#233-consolidated-10-approved-a--approval-package-user-approved-2026-10-10`. A slug-resolving
validator over every non-http link in the doc: **10 anchors resolve, 0 dangling live links**. The 3
matches it still reports at `:76`, `:77`, `:81` are **quoted code spans inside the errata
blockquote**, not links. Recorded in the doc's errata as an appended dated paragraph, and
`Audit/_form-qa-citation-map.md`'s UNRESOLVED **7–8 are CLOSED**; **9 stays open** (the moved
blocks' own internal `CHECKPOINT.md:NNN` refs were never audited — low impact). Citation map
inventory re-cut from 93 rows / 267,728 B to **82 rows / 252,537 B**, its roll-up equal to the file
size at cut time.

**Installer prune — the defect found this session, now closed.** `install_skill.py` copied without
pruning, so files the repo moved to `Audit/` on 2026-10-28 kept living in both installed copies:
installed agents paid context for 5 stale files and could route to paths that no longer exist.
Added `prune_stale_files()` (`:70-97`, keep-set = `collect_files()`, walk scoped to `dest`,
`followlinks=False`, honours `SKIP_DIR_NAMES`, empty dirs removed bottom-up, `dest` itself kept),
`install_to_dir(..., prune=False)` (`:100-118`, loud per-file reporting), `prune=True` for the two
skill-owned global dirs (`:156`) and **`prune=False` for `--mcp-repo`** — that directory is shared
with the `3dsmax-mcp-dev` skill, so the installer does not own its siblings. Verified against a
synthetic tree first (stale incl. nested removed, current files hash-identical, empty dir removed,
non-empty kept, out-of-target sibling untouched, second run removes 0), then for real:
**both installs 5 stale → 0, 107 shipped files byte-identical, 0 extra**.

**Archive rebuilt and re-measured:** `3dsmax-arch-nurbs-ultimate.skill` **1,370,358 → 1,364,374 B**,
**107 entries, 0 differing from the working tree**, `Audit/` still not packaged. Consequence,
intended: the moved 26,161 B **leaves the shipped skill** — it is NARRATIVE/DEAD session log, and no
live citation resolves into it (checked before cutting, not after).

**Trap worth keeping — a subagent disagreement can be *your* span definition.** The C+ subagent
reported "errata 6,122 → 9,070 B, `startswith`-verified prefix". The orchestrator's first
independent check returned **False** (6,309 → 9,195) and looked like a U4 violation. It was not: the
check extracted the errata as "from `ERRATA (2026-10-30)` to the next `\n## `", which swallows the
following body prose, while the subagent had measured the blockquote only. Re-measured on blockquote
lines, append-only holds. **Before treating a mismatch with a subagent as a defect, confirm both
sides measured the same span** — the same shape as the repo's standing rule that a probe without a
calibrated control has produced a result, not evidence.

**Not done, by decision:** option D (§17, ≈60.5 KB — still available, still requires editing the
live citer `scripts/qa_check.py`); deep extraction of the 5 pending files. **Inherent remainder:**
editing `_form-units-qa-design.md`, `install_skill.py` and `_form-qa-citation-map.md` re-queues them
in `graphify-out/manifest.json`, per the same logic as item 5's "known remainder" — a future
`graphify extract` picks it up; do not hand-stamp.

## 2026-10-30 — Maintenance item 5: deep semantic re-extraction of the knowledge graph (COMPLETE)

**Scope, user-approved this session.** The **18** "live" documents that `graphify-out/manifest.json`
marked `semantic_hash == ""`, out of 23 pending. Deliberately **excluded and still pending (5)**:
`references/_form-units-qa-design.md` (FROZEN — item 6), `Audit/CHECKPOINT-archive-2026-10-28.md`
(verbatim history), `Audit/AGENT_PLAN_form_precision.md` and `Audit/AGENT_BRIEF_form_precision.md`
(closed phase), `scripts/build_nurbs.py` (AST layer already fresh from the 2026-10-28
`graphify update`). This is a **remainder, not a gap** — do not "fix" it without a user decision.

**Why the subagent pipeline and not the CLI.** No LLM backend exists in this environment
(`graphify provider list` → "No custom providers registered"; no API keys in env), so
`graphify extract --mode deep` cannot run headless. Route actually executed: 10 chunks → one
extraction subagent per chunk → `.graphify_chunk_NN.json` → `save_semantic_cache` (returned `int 18`,
cache 80 → 98 entries) → `build_merge` → `to_json(force=True)` → `GRAPHIFY_BACKEND=none
graphify cluster-only .` for deterministic community naming.

**Measured result — final gate, 31 independent checks re-run by the orchestrator, not taken from a
subagent report.** Fresh layer: **507 nodes / 1948 edges / 30 hyperedges**, 0 duplicate ids across
chunks, 0 duplicate `(source,target,relation,source_file)` triples, all 18 files ≥1 node (min 3).

| | before | after |
|---|---|---|
| nodes | 2814 | **2911** (+97) |
| edges | 5845 | **7119** (+1274) |
| hyperedges | 27 | **47** (+20) |
| communities | 225 | **166 — all named, 0 placeholders** |
| manifest pending `semantic_hash` | 23 | **5** (exactly the excluded set) |
| `_origin` nodes | ast 1721 / sem 1078 / untagged 15 | **ast 1647 / sem 1249 / untagged 15** |
| `_origin` edges | ast 4165 / sem 1069 / untagged 1885 | **ast 4165 / sem 2954 / untagged 0** |

`build_merge` reported **"Replaced 410 node(s) from re-extracted source file(s)"** and dropped
exactly **31** (30× `CHECKPOINT.md`, 1× `AGENTS.md`) — concepts that now live only in the excluded
`Audit/CHECKPOINT-archive-2026-10-28.md`. **Dangling edges: 0.** The 2 inbound edges the per-chunk
validator had flagged on chunk 01 came from files that are themselves re-extracted, so they collapsed.
The 15 still-untagged nodes are pre-existing external import stubs with an EMPTY `source_file`
(`dataclasses`, `pathlib`, `datetime`, `json`, `math`, …) — correctly left alone.

**Three defects found and repaired, each measured rather than inferred:**

1. **`.deep-pass-protocol.md` §5b is WRONG** where it claims the merge is additive and "drops
   nothing". `build_merge` does a per-tier REPLACE (`build.py:2546-2551`, source sets from
   `_tier_replacement_sources`, `build.py:2194-2257`), and `to_json(force=True)` **silently permits
   the shrink** because the missing-semantic guard lives inside `if not force`
   (`export.py:294-353`). Measured: 410 replaced, 31 dropped. Any future pass must diff the id sets
   BEFORE persisting, and must treat `force=True` as "I have already accounted for the loss".
2. **`build_merge` does not apply the `_origin` tag** from `build.py:68`
   (`item.setdefault("_origin", "ast" if _is_ast_tier(item) else "semantic")`) to chunk nodes — the
   merged graph came out with **522 untagged** nodes. `_origin` drives both `_is_ast_tier`
   (`build.py:45-53`) and that missing-semantic guard, so untagged nodes are invisible to both.
   Repaired with graphify's own rule; edges tagged to match the **measured** pre-existing convention
   (5845/5845 old edges carry `_origin`; same-tier endpoints → that tier, mixed-tier leans semantic
   94:8; hyperedges carry none in either graph).
3. **56 nodes + 44 edges carried `source_location` of the form `L279-300`**, which `_is_ast_tier`
   classifies as **AST tier** (measured: `_is_ast_tier({'source_location':'L279-300'})` → `True`,
   `'§4'` → `False`, `None` → `False`). That contradicts the extraction contract's own rule
   ("free-form section ref, not a line number") and it is what pulled `AGENTS.md`, `PLAN.md`,
   `Audit/_drift-audit.md` and `Audit/_fix-a-notes.md` into `new_ast_sources` during the merge
   (74 AST nodes dropped and re-issued — zero node loss, but the tier identity flipped). Normalised
   to `lines 279-300`: information kept, heuristic no longer tripped, **0 fresh items now mis-tier**.

**Node-id convention, settled.** `graphify.ids.make_id` (`ids.py:86-93`, `re.sub(r"_+","_")` at
`ids.py:82`) makes the canonical id for an underscore-stemmed file **single-underscore**
(`Audit/_fix-b-notes.md` → `audit_fix_b_notes_<entity>`), while the historical semantic tier used
double (`references__p5_contract_*`; 173 double-underscore ids graph-wide). `extraction-spec.md:61`
is self-contradictory here: its literal `{parent_dir}_{filename_stem}` rule yields double, the same
line demands matching the AST id. **Renaming toward double is the harmful direction** — the two
`source_location:'L1 title'` nodes keep those files in AST-tier replacement, so 22 existing AST nodes
would be dropped and not re-issued. Both forms were therefore left as-is; `_semantic_id_remap`
(`build.py:1159-1172`) never rewrites the drift anyway.

**Manifest stamped with graphify's own writer**, `save_manifest(kind="semantic", root=ROOT)` — not by
hand. Decisive code: `detect.py:2934-2940` (`sem_h` = current md5, `ast_hash` taken from `prev`
verbatim) and the `scan_corpus=None` seed loop at `detect.py:2874-2887` that preserves rows not in
`files`. Result: the 102 untouched rows byte-identical, `ast_hash` preserved on all 18. **Positive
control:** `_stat_and_hash()[2]` (the md5, third return value) equals the stored `ast_hash` on
**119/120** rows — the single mismatch is `CHECKPOINT.md`, edited after the AST run and intentionally
left stale so a future `graphify update` re-queues its AST tier. `.graphify_build_state.json`'s
`graph_size` / `graph_mtime_ns` were re-stamped from the patched file because `watch.py:1836` compares
them against the on-disk stat and fails closed → a stale stamp forces a full rebuild (they were
already stale from the merge: 2905870 recorded vs 3452538 on disk).

**Also refreshed, because it was actively misleading.** `graphify-out/.evidence-brief.md` claimed
"1,439 nodes / 3,719 edges / 88 communities / 24 hyperedges" and "There is no `qa_check.py` … that
runs" — both false, and load-bearing, since `AGENTS.md` routes every subagent through that file as
its first read. It now carries the measured figures, the full node/edge field census, the dated
deep-pass note and the 5-file remainder. `.vocab.txt` regenerated via graphify's own documented
generator (`graphify/skills/opencode/references/query.md:31-45`, reads `graph.json`, writes only
`.vocab.txt`): **1615 → 2636 tokens**. Both read-only helpers re-smoke-tested against the new graph
(`.edge_between.py "wall" "shell"` → real paths; `.traverse.py "qa walls shell" bfs 2500` → 365-node
subgraph). Previously-absent tokens `coordinates`, `formatting`, `invariant` are now present;
`bi`, `declare`, `installer`, `numknots` still absent; `qa`/`uv`/`bi` can never appear (the
generator's 3-character minimum).

**Known remainder, inherent not accidental.** The manifest stamp records each file's md5 at stamp
time, so **any edit made to one of the 18 after the pass re-queues it** — including this very
section, which was written after the stamp. The graph's 77 `CHECKPOINT.md` semantic nodes therefore
describe the file as it stood at extraction, not this paragraph. That is correct behaviour (a future
`graphify extract` detects the change and re-extracts); do not "repair" it by hand-stamping.

**Artifacts and rollback.** Protocol + chunk plan: `graphify-out/.deep-pass-protocol.md` (its
§"UNRESOLVED" is still honest reading) and `.deep-pass-chunks.json`. Intermediates kept:
`.graphify_chunk_01..10.json`, `.graphify_semantic_new.json`, `.graphify_extract.json` (patched
consistently with `graph.json`, so a re-run of the cluster step reproduces the repaired state).
Pre-merge backup: `graphify-out/.pre-deep-pass-backup/` (9 files); `cluster-only` additionally backed
up the curated graph to `graphify-out/2026-10-30/`. `graph.json` is written compact with
`ensure_ascii=True` — that is graphify's own byte-exact recipe (`export.py:492-494`); do not
"prettify" it.

---



**Scope of this phase (user-approved):** P0 + P1 only. P2…P6 are queued separately and are
**not** started. Planning document: `Audit/AGENT_PLAN_poly_surface_shell.md` (plan, §I holds the
closed decisions). Single source of truth for the facts below: **`Audit/EVIDENCE_2026-10-27.md`**
(E-1…E-16) — it is DATA, do not re-derive or rewrite it.

**Measured environment:** 3ds Max **2026.3.2**, transport `namedpipe`, protocol 2, `mainThread`.
Scene units `SystemType = "millimeters"`, `SystemScale = 1.0`, `units.decodeValue "1cm"` → **10.0**
(400 cm = 4000 units). The scene was **empty** at the start of the session and **`objects.count == 0`**
after every probe batch — temporary nodes were deleted in the same call that stopped using them
(E-15). No user scene was touched.

### P0 — refuted claims withdrawn (documentation only; no behaviour changed)

| # | Claim that was **FALSE** | Correction | Where |
|---|---|---|---|
| 1 | `getCurrentException()` inside a `catch` "throws itself" / "does not exist" | **It works** — 6 of 6 throw kinds returned a real message, with a non-throw control proving the catch was not entered; re-confirmed 2026-10-27 inside live `catch` blocks | `SKILL.md:458`, `agents/max-orchestrator.md:809,844`, `agents/max-assembly.md` (AP-21), `references/14-chaos-scatter.md:311`, `references/maxscript-splines-shapes.md:494`, `references/_p4b-remainder-evidence.md:70`, `scripts/build_nurbs.py:66-67` |
| 2 | `matrix3` "does not exist" | **It exists** — `matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]` → `classOf` `Matrix3`. It takes **4 args**; the old verdict came from calling it with 9 numbers → *arity* error misread as absence | `agents/max-orchestrator.md:812`, `references/14-chaos-scatter.md` (traps table), `agents/max-assembly.md` (header) |
| 3 | `findString` "does not exist" | **It works** — `findString "hello world" "o w"` → **5** (1-based); `"zz"` → `undefined`; `12345` → throws | `agents/max-orchestrator.md:812`, `references/14-chaos-scatter.md` (traps table) |
| 4 | "There is **no way** to assign an object to a layer from this bridge — nine routes ruled out, final, not an open question" | **REFUTED** — `ILayerProperties.addNode` **works**: `(LayerManager.getLayerFromName name).addNode node` (Phase 14 probe; E-7). What survives: **reading** `node.layer` is read-only, and the two bridge tools have no assignment route | `agents/max-assembly.md` §6.3, `agents/max-facade.md` §1.1, `agents/max-massing.md` §1.1/§4/§5, `references/11-layer-standard.md`, `agents/max-components.md` §1.1, `agents/max-nurbs.md` §1.1, `references/_p6-contract.md` §1.1 |
| 5 | "`tolerances.linear_cm: 0.5` is half a millimetre" | **0.5 cm = 5 mm**. It is a **technological tolerance**; the float epsilon is a separate and much smaller number (`|y| < 1e-3`, E-5) | `agents/max-input.md:298`, `agents/max-massing.md:273`, `references/08-input-rules.md:266`, `references/improvement-log.md:179,203` |
| 6 | "`Extrude` (and 5 more modifiers) do not attach" | It is a property of the **target geometry**, not of the modifier: on a **`SplineShape`** `Extrude` attaches (`threw=false`, `mods=1`); on a **`Box`** it still throws (E-1) | `references/arch-modifiers-and-procedural-reference.md`, `references/_p4b-remainder-evidence.md` §7.2 |
| 7 | "`Shell` has no segments control (`segs` → NO)" | **False negative** — the property is **`segments`**; `getProperty <shell> "segs"` throws, `"segments"` exists (E-2) | `references/arch-modifiers-and-procedural-reference.md` (Shell row), `references/_p4b-remainder-evidence.md` §8.2 |

**Still genuinely absent — do not re-open:** `setCopyMode`, `rotationZ` / `rotationX` / `rotationY`,
`angle`. Substitutes: `copy` + `baseObject =`; `quat <deg> [0,0,1]`; `substring s 1 n`.

**History was not rewritten.** Every correction above is a dated `SUPERSEDED` / `RETRACTED` /
`CORRECTED` marker **next to** the surviving historical sentence, per the standing rule in
`AGENTS.md`. The original wording stays readable as the record of what was believed and when it was
withdrawn.

**`scripts/build_nurbs.py` lint change:** the linter's rejection of `getCurrentException` was
**removed** (it was rejecting correct scripts). The brace form `try { } catch { }` remains the only
rejected shape. The file's own docstring no longer says the call "does not exist".

**`scripts/qa_check.py`:** an `--assess` alias was added for the S7 QA gate's second mode
(`--in … --request … --results … --out …`). It is **additive and non-breaking**: the original
flag triplet still works, `--assess` without the triplet exits 2, `--assess` together with `--emit`
exits 2 (mutually exclusive). All four modes verified.

### P1 — live spike F01: the wall-surface route is **MEASURED**, not derived

Fixture F01 (`Audit/AGENT_PLAN_poly_surface_shell.md` §G.1): a 400 × 300 cm wall on stations
u = [0, 50, 150, 230, 330, 400] cm and Z = [0, 90, 210, 300] cm, with faces **2, 7, 9** removed
as openings.

**Route A — `polyop.createPolygon` over a station grid — works.** The contour is built directly
from points (`polyop.createVert` × 24), the grid is built cell by cell (`polyop.createPolygon`
× 15), the openings are removed (`polyop.deleteFaces w #{2,7,9} delIsoVerts:false`), the thickness
is applied (`Shell innerAmount:0.0 outerAmount:300.0`). **`Extrude` is not required at any step.**
It stays an *alternative* way to obtain a contour for curvilinear cases.

| Stage | V | E | F | boundary | interior | boundary components | χ | area |
|---|---|---|---|---|---|---|---|---|
| base grid 5×3 | 24 | 38 | 15 | 16 | 22 | 1 | 1 | 1.2e7 mm² |
| after `deleteFaces #{2,7,9}` | 24 | 36 | 12 | 24 | 12 | **2** | **0** | **8.7e6 mm² = 87 000 cm²** |

The area matches the closed-form prediction exactly: `400×300 − 100×210 − 100×120 = 87 000 cm²`.

| After `Shell` | measured |
|---|---|
| modifiers | `mods=1`, `classOf=Shell`, `inner=0.0`, `outer=300.0`, `segments=1` |
| bbox | `min=[0,-300,0]`, `max=[4000,0,3000]` — thickness grows **outward**, along the face normal `[0,-1,0]` |
| polygons / vertices / triangles | **48 / 48 / 96** (12 interior + 12 exterior + 24 rim) |
| volume | **2.61e+09 mm³ = 2.61 m³** = `87 000 cm² × 30 cm` exactly |

**Face layout confirmed:** the centre of face 9 is `[2800, 0, 1500]` — exactly the window
(`u = 230…330`, `Z = 90…210`), so face numbering is **row-major**. The normal of face 1 is
`[0,-1,0]`.

**Negative controls — both fire (E-14):** a wall with the openings *not* removed measures
**3.6e+09 mm³** (vs 2.61e+09), so volume does distinguish "openings present". But a **reversed
winding** produces normal `[0,1,0]` and a bbox growing to **+Y** at the **same** volume 2.61e+09 mm³.
⇒ **Volume does not distinguish direction.** The outward/inward check must be a **separate,
independent gate** (normal and/or bbox) and cannot be replaced by a volume check.

**New MAXScript traps measured 2026-10-27 (E-13):**

| Trap | Measured | Do this |
|---|---|---|
| `snapshot <node>` on an Editable Poly + Shell | base object is **`Editable_mesh`**; `polyop.*` throws "EPoly operation on non-Editable Poly: Editable Mesh" | `convertTo (getNodeByName "<name>") Editable_Poly`, **then** `polyop.getNumFaces` → **48** |
| `collapseStack <node>` | base object becomes **`Editable_mesh`** | `getNumFaces` → **96** — that is **triangles, not polygons** |
| `polyop.getFacesUsingEdge` / `polyop.getVertsUsingEdge` | return a **BitArray**, not a Point3 | count set bits: `for i = 1 to q.count do ( if q[i] then c += 1 )` |
| `Editable_Mesh()` + `convertTo … Editable_Poly` | **invalidates the node reference** | re-fetch by name: `getNodeByName "<name>"` |
| `polyop.createVert` / `polyop.createPolygon` | return the new index (1-based, creation order) | indices are predictable, but **read the return value** |

`references/maxscript-mesh-poly-ops.md` was extended with a dated traps section covering all seven.

### Open / deliberately deferred (not failures)

- **Layer auto-application policy — DEFERRED.** The capability claim is refuted (above); **whether
  this skill's builders should apply layers automatically is an open policy decision** and is not
  settled in either direction (`Audit/AGENT_PLAN_poly_surface_shell.md` §I.4).
- **P2…P6 not started.** `walls.json` (the new domain spec file), `build_wall_surface.py` (the
  S4w stage) and the `poly_surface_shell_v1` QA profile are **planned, not present**.
- **The "S5 is the last geometry builder" invariant** still holds today — but it will need rewording
  when S4w exists (`agents/max-orchestrator.md:61,378`, `references/01-pipeline-workflow.md:58`,
  `SKILL.md`).
- **Committed and pushed:** `6c0f27b` → `origin/main` on 2026-10-28 (P0 + P1 plus the previously
  uncommitted Phases 13–15 work). This bullet replaces an earlier "nothing has been committed"
  note written before that commit.

## Status legend

| Mark | Meaning |
|---|---|
| ✅ | Done **and** verified by live execution |
| 🟡 | In progress |
| ⬜ | Not started |
| ⚠️ | Done but contains a known error — must be corrected |
| 🔴 | Blocked |

---

## Stage status

| Stage | Status | Verified by | Notes |
|---|---|---|---|
| **P0** Environment baseline | ✅ | `get_bridge_status`, `get_plugin_capabilities`, preflight PASS 9/9 | NURBS conclusion was wrong — corrected in P1 |
| **P1** Audit & salvage | ✅ | library executed live; preflight inversion tested | `SKILL.md` decision matrix rebuilt; 02 and 12 corrected; dedupe measured; `curve-construction.md` rewrite brief written |
| **P1-b** Library bugfix | ✅ | all 10 library functions executed live on 2026-10-04 | 4 bugs fixed. Bug 3's premise was **false** — resolved. Bug 4 found and fixed. |
| **P2** Spec grammar + input (S1) | ✅ | `validate_specs.py --dir examples` → **PASS 52 / FAIL 0 / WARN 0**, also clean under `--warnings-as-errors`; 54-case negative battery fires 54/54 | Offline stage, no 🔌 needed. `07`–`10`, `agents/max-input.md`, `init_project.py`, `validate_specs.py`, 3 example files |
| **P3** Layer standard + massing (S2) | ✅ | live run of `examples/massing.ms`: 18 nodes, **18/18 bboxes match `massing.json` within 0.5 cm**, model Z `-30…910` = `overall_height_cm`; validator `PASS 67 / FAIL 0 / WARN 0` | `07` §8.1 + `G-34`…`G-40`; `11`, `01`, `agents/max-massing.md`, `build_spec.py`, `examples/massing.json`; 2 live-only defects found |
| **P4** NURBS core (S3) | ✅ | live run of `examples/nurbs.ms`: **6 nodes, idempotent over 3 runs**, every measurement below taken from it; validator `PASS 84 / FAIL 0 / WARN 0` | `nurbs.json` **defined** (`07` §8.2 + `G-41`…`G-49`); `build_nurbs.py`; library grew to **12 functions, all 12 executed live**; 1 live-only defect found and fixed |
| **P4b** NURBS remainder | ✅ | round 1: all 4 relation classes construct → commit → evaluate; schema extension executed live. round 2 (2026-10-04): **both live defects found by controlled probe and fixed** — `SUR_006` overshoot traced to the tension default, parent duplication removed via `nurbsID` references; live run of `examples/nurbs.ms` → **10 nodes, idempotent over 3 runs**, every node bbox measured, `SUR_006` now `y 450…900`, `SUR_007` no longer duplicates the vault; validator `PASS 90 / FAIL 0 / WARN 0` | Rail sweep / blend / trim discovery **✅ — it overturned the P4 "not implemented" finding**. Schema defines `rail_sweep` `two_rail_sweep` `blend` `trim` + `G-50`…`G-56` |
| **P4b-r** Reference claim-by-claim pass | ✅ | **both remaining files executed against live Max 2026.3.2**, controls in every batch; transcripts in `references/_p4b-remainder-evidence.md` | `maxscript-splines-shapes.md` — **largely vindicated** (all 11 shape ctors, all 15 render props, all 27 `splineOps`, all 14 path-interp fns, every knot/segment method), **10 corrections**. `arch-modifiers-and-procedural-reference.md` — **substantially wrong**: 3 class names wrong, 6 of 23 modifiers unusable via the documented route, ~13 parameter names don't exist, the Data Channel operator vocabulary was wrong, and §3 routed to **two nonexistent MCP tools** (`mcg_*`, `curve_model`). `install_skill.py` packaging gap closed. **New hazard found: Chaos Scatter's `px_modifierClothing.ms` crashed Max.** |
| **P5** Facade + component registry (S4) | ✅ | offline: `validate_specs.py --dir examples` → **PASS 120 / FAIL 0 / WARN 0 / SKIP 12**, clean under `--warnings-as-errors` and `--build`; **16/16 fault-injection cases fire** across `G-57`…`G-70`; builder deterministic into two temp dirs byte-identical to the committed files. **live: `world_table.csv` read by MAXScript itself → 136 rows → 136 panels placed as reference instances, `objects.count` = 165 = 136 + 29 prototypes, 136/136 sharing their prototype's `baseObject`, 5 sample bboxes exactly equal to an independent prediction, scene back to 0** | `07` §8.3/§8.4/§9.8 define both files; `scripts/facade_tables.py`; `G-57`…`G-70`; `examples/{facade_grids,components_registry}.json` + both CSVs; `agents/max-facade.md`, `agents/max-components.md`. **136 panels · 140 axes · 29 components · 6 families**. Three defects found and fixed — see §"P5 — what this changed" |
| **P6** Assembly + Chaos Scatter (S5) | ✅ | **live gate executed and measured, twice.** `fileIn examples/massing.ms` → **27** nodes (22 `Box` + 5 `Dummy`), idempotent over 3 runs, 9/9 bboxes exact (**0.000000 cm**). `fileIn examples/assembly.ms` → **244** nodes = 27 + 136 `PLC_` + 29 `PROTO_` + **52 `WAL_`**, idempotent (244, 244), **0 modifiers in the scene**, every cell bbox exact and the **volume identity exact to 0.000000 cm³ on all 8 hosts**, measured in Max against an independently re-derived prediction; 5/5 instances share their prototype's `baseObject` with a corrected negative control returning `false`; scene back to **0** after two sweeps. Offline: `py_compile` exit 0, validator **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** clean under `--warnings-as-errors` and `--build`, all four artefacts byte-identical across two temp dirs, fault injection **11/11** in the builder and **3/3** in the linter | `facade_wall` kind added to `massing.json`; `assembly.json` **136 placements / 16 opening_cuts / 52 wall_cells / 1 scatter**; `assembly.ms` 1979 lines, **one function, zero modifiers**; `scripts/place_components.py`; `agents/max-assembly.md`; `references/14-chaos-scatter.md`; `snippets/chaos_scatter.ms`; `G-71`…`G-83`. **The Boolean modifier was measured unusable and the stage was rebuilt without it** — see §"The Boolean modifier is unusable in this build" |
| **P7** Corona materials + UVs (S6) | ⛔ **cancelled** | partial probes executed 2026-10-05 before the decision — transcripts in `references/_p7-evidence.md` | **User decision 2026-10-05**: materials are made by hand. The probes that did run closed P0's renderer question and are now the best material reference the pack has (§"P7 — what the cancelled probes proved") |
| **P8** QA loop (S7) | ⛔ **cancelled** | — | **User decision.** `qa_check.py` / `capture_views.py` do not exist and are not planned. Scatter determinism via `saveConfiguration` was never proven |
| **P9** Export (S8) | ⛔ **cancelled** | — | **User decision.** No FBX / OBJ / USD, no instance-preserving export |
| **P10-lite** Orchestrator + scope | ✅ | `agents/max-orchestrator.md` written; `SKILL.md` rewritten 245→462 lines; **live full-chain re-run: 254 nodes** (§"P10-lite — the live chain run"); `py_compile` exit 0; validator PASS 138; all 5 artefacts byte-identical across two temp dirs; fresh scaffold PASS 105 | **3 real defects fixed** in the process — `init_project.py` `assembly.json` stub omitted `wall_cells` (fresh scaffold FAILed G-1), the same file mislabelled `nurbs.json` as computed when it is hand-authored, and `place_components.py` carried four dead Boolean-era functions plus docstrings describing a Boolean design that no longer exists |

| **P14** Close-out (docs + lint, no live bridge) | ✅ | `RECHECK_STAGES` narrowed so the linter names P7/P8/P9 as cancelled; fault injection 5/5 negatives + 4/4 positives; `procedural-graphs.md` found to need the OBSOLETE router in **three** files, not one | Three open items from §"Resume here — after P13" closed; `CHECKPOINT.md`'s own duplicated bullet removed; chain re-measured **254 nodes** |
| **P15** UV / unwrap rules | ✅ | **live, Max 2026.3.2**, ~90 `execute_maxscript` batches. Chain re-loaded: **254 nodes, 0 modifiers**. `addModifier` on the **29** `PROTO_*` → **165** nodes gain channel 1 (from 0). `realWorldMapSize:true` = **1 UV unit = 1 cm**, verified on 3 boxes at independent positions. `setTiling` integer truncation reproduced on 3 independently-built surfaces. Same-call `utile` loss reproduced **8/8**; the `snapshotAsMesh` fix **3/3** | **The last item §"Resume here — after P14" listed as open.** New **`references/13-uv-rules.md`**. `architecture-exterior-pipelines.md` §7 and `nurbs-complete-guide.md` §8 both carried `setTiling` as advice — corrected. `_04-05-evidence.md`'s G32 "CONFIRMED" **downgraded**: the round-trip is real but was calibrated for the wrong question |
| **Phase 14 / Audit 001** Input Protocol & Live Probes | ✅ | **Live, Max 2026.3.2**. Probe A: `ILayerProperties.addNode` assigns nodes to layers (`threw=false layer=__probe_L_WALL`), overturning P3/P6 negative. Probe B: `baseObject` material sync from 29 `PROTO_*` to 136 `PLC_*` verified (`beforeSync=false afterSync=true`), ~5 ms, 0 modifiers. Input protocol: `references/08` §1.3, `agents/max-input.md` §4.2 & §6.4.1 | Visual & proportional deconstruction protocol; scale anchor binding; candidate proposal in escalations; `snippets/sync_proto_materials.ms` workflow |
| **Stages 01–13** Form-precision & staged-unit pipeline | ✅ | Gates 01–13 PASS; regression corpus at `specs/fixtures/form-precision/specs/pipeline` (validator **PASS 153 / FAIL 0**); plan and brief archived at `Audit/AGENT_PLAN_form_precision.md`, `Audit/AGENT_BRIEF_form_precision.md` (moved there from the repo root on 2026-10-28) | closed 2026-10-10; the measured-fact register is `references/_form-units-qa-design.md` |
| **Phase 15** Stepped massing, setback tiers & pilasters (Schema 1.1) | ✅ | `validate_specs.py --dir specs/fixtures/stepped-tower --warnings-as-errors` → **PASS 145 / FAIL 0 / WARN 0 / SKIP 22** (G-91); live Max 2026: `massing.ms` → **155 nodes** (`__f_unit = 10.0`), `assembly.ms` → **374 objects**, **0 modifiers** (G-81), idempotent, scene back to 0 | `Audit/AGENT_BRIEF_stepped_massing.md`; fixture `specs/fixtures/stepped-tower/` |
| **Phase 16** `poly_surface_shell_v1` — P0 + P1 | ✅ | live spike F01 in Max 2026.3.2, every measured number hit the oracle exactly (see the Phase 16 section above) | **P2…P6 queued, not started** — see §Next actions |

---

## Verified facts — safe to build on

Each of these was executed against the live bridge. Do not re-derive; do not doubt without a control.

### Environment
- 3ds Max **2026.3.2** (Security Fix). `maxVersion()` returns an array; major = index 8.
- Transport `namedpipe`, protocol 2, `mainThread`, `safeMode: true`, RTT ~2.5 ms.
- TCP `127.0.0.1:8765` **not used, not required**. Instance-pipe discovery is automatic
  (survived an OS reboot mid-session).
- **Absent plugins:** forestPack, forestLite, tyFlow, railClone, phoenixFD.
- **Present:** Corona, Chaos, Arnold, PhysX, FbxMaxWrapper, USD.
- Materials constructible: `OpenPBR`, `PhysicalMaterial`, `Standard`, + **16 Corona classes of
  which 15 construct** (`CoronaPortalMtl` throws). The architectural one is **`_CoronaPhysicalMtl`**,
  leading underscore. No Arnold-specific / VRay / Octane / `RS_Standard_Material` classes.
- **`materials` is `undefined`** in this build — no library collection to enumerate or count, the
  same family as `layers`. Measured 2026-10-05; see `_p7-evidence.md` §4.
- **Material propagation via `baseObject` — VERIFIED (Probe B, 2026-10-13):**
  Painting 136 `PLC_*` panels individually by hand is **not required**. Because all 136 `PLC_*` reference
  instances share their respective prototype's `baseObject`, running material sync:
  `for proto in objects where matchPattern proto.name pattern:"PROTO_*" and proto.material != undefined do ( for o in objects where o != proto and o.baseObject == proto.baseObject do o.material = proto.material )`
  propagates assigned materials from the 29 `PROTO_*` nodes to all 136 `PLC_*` instances in ~5 ms with
  0 modifiers (strict G-81 compliance). Measured live: `beforeSync=false afterSync=true`. See `snippets/sync_proto_materials.ms`.
- **Active renderer was `Arnold`; `renderers.current` and `renderers.production` are independent
  slots and BOTH were `Arnold`.** The set route, measured: `renderers.production = Corona()` —
  **instantiate, do not assign the class**; `renderers.production = Corona` throws
  `Unable to convert: Corona to type: Renderer`. `Corona()` costs ~3.5 s cold, ~0.4 s warm, so it
  needs its own `execute_maxscript` call. **The user's Max is now on Corona for both slots**, at
  their request. This closes PLAN §4.2 — the bridge has no renderer-setter tool at all.

### NURBS — the relational API is real ✅
- All 27 identifiers used by the library resolve; the surface classes **construct**.
- `getNURBSSet node #relational` → `NURBSSet` with `numObjects` sub-objects.
- `superClassOf` on sub-objects → `NURBSSurface` / `NURBSCurve` / `NURBSPoint`.
- `evalPos`, `evalUTangent` work. Parameter ranges are **not** normalized to [0,1].
- `snippets/nurbs_arch_library.ms` loads cleanly → `MCP_NURBS_Arch loaded`.
- `makeCVCurve` and `makePointCurve` return valid objects.
- `NURBSNode nset` → node whose `classOf` is `NURBSSurf`, shown in UI as "CV Surf".
- `Point_Surf` / `CV_Surf` **do** have MAXScript identifiers.
- `Loft` resolves but `Loft()` is `Not creatable` → the real path is `NURBSULoftSurface`.

### Scene units and placement semantics — VERIFIED (P3, 2026-10-04)
Every row below is an executed transcript, not an inference. Control probe in the same batch:
`TotalGarbageXYZ123` → `undefined`, `Box` / `Dummy` → resolve.

| Fact | Evidence |
|---|---|
| **Scene units are centimetres, scale 1.0** → a spec value in cm reaches Max unchanged | `units.SystemType` = `centimeters`; `units.SystemScale` = `1.0`; `units.SystemType == #centimeters` → `true` (all other unit constants `false`). **This closes the UNVERIFIED row in `07` §11.** |
| `units` is a struct whose members are `USType`, `USFrac`, `CustomName`, `CustomValue`, `CustomUnit`, `decodeValue`, `DisplayType`, `SystemType`, `formatValue`, `SystemScale`, `MetricType`. `getProperty units #SystemType` **fails** — read `units.SystemType` directly | `showProperties`-equivalent dump; `getProperty units #SystemType` → `no-such` |
| **`Box(width:,length:,height:,pos:)` is the deterministic placement primitive.** Geometry is centred on `pos.x`/`pos.y` and its **base sits at `pos.z`**. `pos:` moves the geometry, not only the pivot | `Box width:100 length:200 height:300 pos:[1000,0,0]` → `min=[950,-100,0] max=[1050,100,300]`. Identical result via `b.pos = [1000,0,0]`. Default `Box()` is 25³, `min=[-12.5,-12.5,0]` |
| ~~**An object's layer cannot be assigned from MAXScript in this build.**~~ **OVERTURNED 2026-10-13.** While `node.layer = ...` is read-only, **layer assignment works via `ILayerProperties.addNode`**: `local lyr = LayerManager.getLayerFromName name; if lyr == undefined do lyr = LayerManager.newLayerFromName name; lyr.addNode obj` | Probe A (2026-10-13): `threw=false layer=__probe_L_WALL` with controls `1+1` (`threw=false undef=false`) and `TotalGarbageXYZ_fn(1)` (`threw=true undef=true`). Prior probe tested only property setter on node |
| Layers **can** be created, read, and populated with nodes from MAXScript | `LayerManager.newLayerFromName "P3_X"` → ok; `LayerManager.getLayerFromName "P3_X"` → `LayerProperties` mixin; `lyr.addNode node` → node assigned to layer |
| **Layer enumeration is not available from MAXScript in this build.** The typed tool is the only route | `layers` as a value → `undefined`; `layers[1]` → *"No get function for undefined"*; `layers.count` → *"Unknown property count in undefined"*; `LayerManager.layers` → *"Unknown property Layers"*; `LayerManager.numLayers` / `.getCount()` → throw |
| `3dsmax-mcp_manage_layers` works for `list`, `create`, `delete` — **and those three are the whole vocabulary** (P6, 40+ candidates rejected with a uniform `Unknown layer action`; `create`/`delete` return distinct argument errors, so the probe discriminates). While the MCP tool lacks node assignment, **MAXScript assigns nodes via `lyr.addNode node`** | typed-tool batch + MAXScript `ILayerProperties.addNode` live probe (2026-10-13) |
| `node.parent = dummy` works; `getChildren` **does not exist** → use `dummy.children`. `Dummy boxSize:` needs a **`point3`**, a float throws *"Unable to convert: 100.0 to type: Point3"* | `b.parent = d` → `P3_DUMMY`; `getChildren d` → ERR; `d.children` → `#children($P3_CHILD) count=1` |
| **`delete <dummy>` does NOT delete its children** — the child survives and must be deleted explicitly | after `delete d`, `objects.count` decreased by exactly 1 |
| `try { } catch { }` **block** form is a parse error in this build → use the parenthesised `try ( ) catch ( )`. ~~`getCurrentException()` is unavailable~~ **WITHDRAWN 2026-10-05 — it works** (6/6 throw kinds, with a non-throw control), re-confirmed 2026-10-27 | both observed 2026-10-04; the exception half withdrawn 2026-10-05 |
| A failed/aborted probe **leaves its objects in the scene** — 8 orphans accumulated across aborted probes and had to be swept. Always delete test nodes in the same call | `objects.count` 8 → 0 after an explicit sweep |

### Emitted-MAXScript rules — VERIFIED (P3, 2026-10-04)
Found by executing `examples/massing.ms`, i.e. **not** findable by any offline check.

| Fact | Evidence |
|---|---|
| **`local` at the top level of a `.ms` file is a compile error.** An emitted script must wrap its whole body in one `fn` | `fileIn examples/massing.ms` → `Compile error: no local declarations at top level: SP_GROUND_PAD`. After wrapping in `fn mcpMassingBuild_<project> = ( … true )` plus one call, the file runs |
| **`if (getNodeByName "X") != undefined do (…)` is context-dependent and throws** when the node is absent, inside a direct `try`/`catch`. Use the explicit-local form: `local prev_X = getNodeByName "X"` then `if prev_X != undefined do ( delete prev_X )` | the one-liner → `Type error: Call needs function or class, got: undefined`; the explicit-local form ran clean for both the present and the absent case |
| `getNodeByName` works and returns the node (`$Box:EL_001 @ [900,450,-30]`); `delete <node>` works | live, 3 invocations |
| **A `fn`-wrapped builder is idempotent.** Three consecutive invocations in one session: `true`, `true`, `true`, always 18 nodes with identical names | live |
| **`node.min` / `node.max` is the measurement route** and returns exactly what the `Box` placement primitive promises | all 18 nodes measured; every axis within 0.5 cm of `massing.json`, most exact |

### Design consequences of the layer finding (P3 decision, OVERTURNED 2026-10-13)
`node.layer` is read-only from MAXScript, which originally led to the P3/P6 conclusion that layer
assignment was impossible from script and had to remain a spec-time declaration applied by hand in the Layer dialog.

**Probe A on 2026-10-13 overturned this negative:** while `node.layer = ...` throws `Property is read-only: layer`,
`ILayerProperties.addNode` (`(LayerManager.getLayerFromName name).addNode obj`) works cleanly
(`threw=false layer=__probe_L_WALL`, calibrated with controls `1+1` and bogus function). The earlier
investigation tested six property-setter routes on `node` and tool actions in `manage_layers`, but missed
the interface method on `LayerProperties`. Builders can now optionally assign nodes to layers directly
in emitted MAXScript.

### Chaos Scatter
- `ChaosScatter()` constructs. `CScatter` is the base and is **NotCreatable**.
- `seed` is 1..31337 → deterministic. Full parameter map in PLAN §4.1.
- `FpInterface` gives `getInstanceCount()` and `saveConfiguration`/`loadConfiguration` → the QA
  determinism hook.

### NURBS mutators are status-style — read state back, never trust the return value
- `appendObject nset obj` returns the **string `"OK"`** (class `OkClass`). Index = `nset.numObjects`
  read *after* the call.
- `close <crv>` also returns `"OK"` and **does not mutate**. `NURBSCVCurve` cannot be closed at all:
  `closed:true` kwarg ignored, no settable `closed`/`isClosed`, `isClosed` always reads false.
  `NURBSPointCurve closed:true` **does** work natively.
- There is **no `setWeight` and no `getWeight`**. Weight only via `NURBSControlVertex <pt3> <weight>`.
- `NURBSControlVertex` **constructs** — `<pt3>` or `<pt3>, <weight>`; prints as
  `NURBS_cv([x,y,z], weight)`. The real constraint: `setCV`/`setPoint` reject a bare point
  (`Unable to convert: [0,0,0] to type: NURBSControlVertex`) — the wrapper is mandatory.

### NURBS surfaces and grids — VERIFIED (P4, 2026-10-04)
Control probe in the same batch: `TotalGarbageXYZ123` → `undefined`; all 17 real identifiers resolve.
Every row is an executed transcript.

| Fact | Evidence |
|---|---|
| **All 17 NURBS identifiers resolve**, including `NURBS1RailSweepSurface`, `NURBS2RailSweepSurface`, `NURBSBlendSurface`, `NURBSProjectVectorCurve`, `NURBSPointSurface`, `NURBSCVSurface` | control-tested batch; every one **constructs** |
| **There is no `closeU`, `closeV` or `close` on any surface class.** This is a *verified negative*, not an omission: `NURBSPointSurface().closeU()` → `Unknown property: "closeU" in <NURBSPointSurface:…>` | deliberately uncaught so the message was returned. Resolves the P1-b "left unverified" item — the answer is **no such method** |
| **A surface is not evaluable until it is committed.** Before `appendObject` + `NURBSNode`: `uParameterRangeMin/Max` read `0.0` and `evalPos` returns `undefined`. After commit: real domain, and `evalPos` returns a point | `NURBSCVSurface` 3×3 grid: before → `u=[0,0]` / `evalPos` `undefined`; after → `u=[0,1]` / `evalPos` = `[100,100,0]` |
| **Sub-object indices are not knowable in advance — resolve by superclass.** A 5×3 `point_grid` yields **15 `NURBSPoint` sub-objects, then the surface** (index 16). The 5-rib `u_loft` in the worked example yields **52** sub-objects: base surface 51, offset shell 52 | live enumeration via `getNURBSSet node #relational`. This is why the emitted `.ms` never writes a literal index |
| **A derivative must read the FIRST surface, not the last.** On a shelled surface the last `NURBSSurface` is the offset shell. Measured: sampling the first gave panels `z 420 → 600.97`; sampling the last gave `441.043 → 625.94` — a silent 25 cm error | the live run caught this; see §Incident log |
| **`thickness_cm > 0` offsets OUTWARD along the normal.** 25 cm on the worked vault: base crown `600.97` → offset crown `625.94` | both surfaces evaluated at their own mid-parameter |
| **`point_grid` interpolates and overshoots; `cv_grid` is controlled and undershoots.** Canopy lattice peak 510 → node bbox **568.226**, sampled max 515.998. Canopy cage lattice peak 480 → node bbox **exactly 480** (convex hull — it can never exceed it), sampled max **448.125** | both surfaces built by the same builder in the same run |
| **Parameter domain differs by kind.** `point_grid` is **chord-length**: `u=[0, 434.555]`, `v=[0, 307.439]` for a 400 × 300 cm lattice. `cv_grid` is normalised `[0,1]` | measured on committed surfaces |
| **Curve knots are normalised to `[0,1]` by `setClampedKnots`** and are correct: order 3 / 6 CVs → `#(0,0,0,0.25,0.5,0.75,1,1,1)`; order 4 / 4 CVs → `#(0,0,0,0,1,1,1,1)`. But an **unattached** curve's `parameterRangeMin/Max` read `[0,0]` — the property is meaningless until the curve is in a set | resolves the P1-b "curve parameter-range normalisation" item |
| `setPoint` takes **4 arguments on a surface** (`setPoint surf u v point`) and 3 on a curve. `NURBSPointSurface.numPoints` is a **point2** (grid dimensions); `numRows`/`numCols`/`numCVs` do **not** exist on it | `Argument count error: setPoint wanted 4, got 3`; property sweep |
| `NURBSCVSurface` has `numCVs` (point2), `uOrder`, `vOrder`, `numUKnots`, `numVKnots`, `flipNormals`, `matID` — exactly what `setSurfaceClampedKnots` writes | property sweep; guard fires correctly (`NURBSCVSurface requires numCVs >= order`) |
| **`NURBSControlVertex.weight` is a real settable property** (read 0.5 → write 3.0 → read 3.0). **`NURBSIndependentPoint` has no `.weight` at all** and no `getWeight` | resolves the P1-b "direct `.weight`" item — it works on the CV, never on the point |
| **F9/F10 division arguments are positional**, not keywords: `sampleSurfaceToQuadPoly node idx uDivs vDivs`, `createDiagridOnSurface node idx uCells vCells`. Calling them with `uDivs:` fails | `Argument count error: … wanted 4, got 2` |
| `getPropNames` does **not** exist; `compile "…"` does **not** close over enclosing locals. Both are dead ends for API discovery | `getPropNames` ERR; `compile "o"` → `undefined` |
| **Introspection is useless for these classes**: `inspect_plugin_class "NURBS1RailSweepSurface"` → `Unknown class` | a second, independent false negative — same family as the P0 `NURBSSet` incident |
| ~~Rail sweep / blend / project expose **no** property or method this build resolves~~ — **FALSE. Corrected at P4b; see §"Rail sweeps, blends and trims".** The P4 probe read properties on **unattached** objects and every read failed; the same names read back correctly on the **committed** sub-object | executed 2026-10-04 — `NURBS1RailSweepSurface rail:1` before commit → no readable property; after `NURBSNode` commit → `rail=0 railID="0P" parallel=true numCurves=3` |

### Rail sweeps, blends and trims — VERIFIED WORKING (P4b, 2026-10-04)

**This section overturns the P4 finding that these classes were "not implemented".** They were never
unimplemented — the P4 probe read them in the wrong place. `references/nurbs-complete-guide.md` and
`references/nurbs-architecture-recipes.md` were **right**; `07` §8.2.5, `12-nurbs-gotchas.md` and
`agents/max-nurbs.md` were **wrong** and have been corrected.

All rows are executed transcripts. Control in the same batch: `TotalGarbageXYZ123` → `undefined`,
`(NURBS1RailSweepSurface()).totalBogusName` → `ERR`, `(.totalBogusName: "zzz")` on a constructor →
**silently ignored**.

| Fact | Evidence |
|---|---|
| **THE RULE: relational properties are readable only on the COMMITTED sub-object.** Read them on a freshly constructed, unattached surface and *every* name fails; read them on the same surface after `appendObject` + `NURBSNode` and they all read back | unattached `NURBS1RailSweepSurface`: `rail`/`railID`/`parallel`/`numCurves`/`axisTM`/`parent*`/`distance`/… **all ERR**. Committed: `rail=0 railID="0P" parallel=true numCurves=3` |
| **An invalid dependent surface is silently DROPPED at commit** — no error, no warning, it just is not in the set | a sweep with no rail set → `numObjects=7`, no `NURBSSurface` at all. Same sweep with `rail:` set → `numObjects=14`, index 14 is the surface |
| **`NURBS1RailSweepSurface` works end-to-end.** `rail:<set index> parallel:<bool>` + `appendCurve` per cross-section | 3-point rail, 3 sections → surface at index 14, `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[500,0,100]` = exact expected midpoint |
| **`NURBS2RailSweepSurface` works end-to-end.** `rail1:` `rail2:` `parallel:` | two parallel rails 500 cm apart, 3 transverse sections → `u=[0,1] v=[0,1]`, `evalPos(0.5,0.5)` = `[550,200,0]` = exact midpoint between the rails |
| **Both sweep types have a `[0,1]`-normalised domain**, unlike `point_grid`'s chord-length domain | measured on committed surfaces |
| **`NURBSBlendSurface` works end-to-end.** `parent1:` `parent2:` `edge1:` `edge2:` `tension1:` `tension2:` | two point surfaces + blend → **3** surfaces; blend readback `parent1=0 parent2=0 edge1=1 edge2=1 tension1=1.0`; `evalPos(0.5,0.5)` = `[-50.0011,100,100]` |
| **`NURBSProjectVectorCurve` works.** `parent1:`/`parent2:`/`pVec:`/`seed:`/`trim:`/`flipTrim:` | plane + closed 4-pt rectangle above it, `pVec:[0,0,-1]` → projected curve readback `parent1=0 parent2=0 seed=[0.5,0.5] trim=true flipTrim=false`. **The "a second surface appears in the set" note in this row is WRONG and was corrected at P4b round 2 — the second surface is the parent's own untrimmed `NURBSCVSurface` copy, not evidence of a trim. See §"Relation semantics, corrected".** |
| ⚠️ **`pVec` reads back with the OPPOSITE sign.** Set `[0,0,-1]`, read `[0,0,1]` | committed projected curve. Do not assert `pVec` round-trips; assert `trim`/`seed`/`parent*` instead |
| `parent:`/`rail:`/`rail1:` read back **`0`**, not the 1-based set index that was passed; `railID` reads a **`nurbsID` string** (`"0P"`), not an integer — **the `"0P"` format was NOT reproduced at P4b round 2 and is now listed as unverified; the pointer prints as a large decimal + `P`** | committed surfaces, both sweep types and the blend |
| **The constructor silently accepts ANY keyword.** `NURBS1RailSweepSurface totalBogusName: 1` constructs fine — bogus name is ignored, no error | so a successful construction proves **nothing** about a keyword |
| **The only keyword-existence discriminator is a type mismatch.** Pass a string to a name that exists and it errors on conversion; a name that does not exist is silently swallowed | the sweep-of-names probe: `rail railID parallel numCurves axisTM` error on `rail: "zzz"`, `rail1 parent distance tension1` did not |
| `o["name"]` bracket access is **not** valid dynamic property access → always `ERR`, even for a property that reads fine literally. `getProperty o #x` also fails. `execute` sees no enclosing locals | `o["renderable"]` → ERR while `o.renderable` → `true`. This bug produced an all-`ERR` probe that looked like "these classes expose nothing" |

**Recovered keyword map** (existence proved by type-mismatch, values proved by commit + read-back):

> **Correction at P4b round 2:** `NURBS1RailSweepSurface` has **`railID`**, not `rail1ID:`. The
> `rail1ID` spelling that appeared in the P4b round-2 work brief was wrong; it never reached the code
> and is not in the emitted output. Rails also remain **in-set ordinals**, not `*ID:` references —
> only *surface* parents use the id form (see below).

| Class | Keywords that exist |
|---|---|
| `NURBS1RailSweepSurface` | `rail` `railID` `parallel` `numCurves` `axisTM` |
| `NURBS2RailSweepSurface` | `rail1` `rail1ID` `rail2` `rail2ID` `parallel` `numCurves` |
| `NURBSBlendSurface` | `parent1` `parent1ID` `parent2` `parent2ID` `edge1` `edge2` `tension1` `tension2` |
| `NURBSOffsetSurface` | `parent` `parentID` `distance` (already verified in P4 via F6) |
| `NURBSProjectVectorCurve` | `parent1` `parent1ID` `parent2` `parent2ID` `pVec` `seed` `trim` `flipTrim` |

**Which surface is "the" surface.** In a set of N surfaces, the design surface is **not** always the
first: the sweep test needs the **first** (P4's shelled-offset trap), while `NURBSBlendSurface` is the
**last**. Never hardcode a literal index — resolve by superclass *and* check which one carries the
relational properties you just set.

### Relation semantics, corrected — VERIFIED (P4b round 2, 2026-10-04)

Everything below was measured by a controlled probe, not inferred. Two live defects were **found**
this way and fixed; the raw transcripts were handed to the implementation agents as data.

| Fact | Evidence |
|---|---|
| **`NURBSBlendSurface` tension `0.0` is the straight transition; `> 0` pushes the blend outward past BOTH edges.** Worked-example geometry (vault high-V edge `y=900`, canopy high-V edge `y=450`): `0.0/0.0` → `Y 450…900`, `Z 420…600.97` = correct soffit. `0.5/0.5` → `Y …995.5`, `Z 401.08`. `1.0/1.0` → `Y …1195.64`, `Z 369.758` = **295.64 cm outside its own geometry and 50 cm below the springing**. `1.0/0.0` → `Y …1081.41`, `Z 420` | 6 blends, one per row, blend bbox from a 7×7 `evalPos` grid over the blend's own committed domain — **not** the node bbox, which also contains the parents |
| **The `1.0` default was the whole `SUR_006` defect.** `SUR_006_CanopySoffit` reached `y = 1518` against a 900 cm deep plan because the builder hardcoded `tension1:1.0 tension2:1.0`. Fixed: default `0.0`, `G-55` bounds it to `[0.0, 1.0]` | before/after live runs; `SUR_006` now `min=[0,450,420] max=[1800,900,603.016]` |
| **A blend spans the gap between the two selected edges — the parents need not touch.** All 16 `edge1`×`edge2` combinations commit (`nObj=21`, `nSurf=3`) and all four properties read back exactly | controlled pair: planar `P` `x 0…200 z 0`, ramp `Q` `x 200…400` rising to `z 200`; the two share the `x = 200` edge |
| **A blend whose two edges are coincident yields a ZERO-AREA surface, silently** — no error, no warning. Measured `200,0,0 … 200,200,0` | `edge1:2 edge2:1` on the pair above (`P` high-U against `Q` low-U) |
| **A same-axis/same-side edge pair bulges outside both parents** — `3/3` and `4/4` gave `y −111.8` and `y …311.8` on a 200 cm patch | the 16-combination table |
| **`nurbsID` is an `IntegerPtr`, not a string.** `parent1ID:"…"` → `Unable to convert: "2276505581808P" to type: IntegerPtr` | committed surfaces |
| ⚠️ **A SYNTHETIC `nurbsID` CRASHES 3ds Max.** `parent1ID:12345` → `EXCEPTION_ACCESS_VIOLATION`, read of address `0x3089` — a hard process crash, not a catchable MAXScript error. Scene left with orphans | executed; Max survived only because the offending node was already built. Hence `G-56`: never emit a literal in a `parent*ID:` slot |
| **A relation's parents need NOT live in the relation's `NURBSSet`.** `parent1ID:`/`parent2ID:` referencing a surface committed in **another** node's set works: the relation set then holds **one** sub-object and the geometry is identical to the in-set re-instantiation | `nObj=1`, `bbY=450.0..900.0`, `bbZ=420.0..600.97`, `rd_p1id` = the pointer passed |
| **Deleting the parent node afterwards did not break the relation** — still evaluated, no crash. **One test, one outcome; not a guarantee** | `post-delete evalPos(0.5,0.5)=[899.861,900,600.97]` |
| **`NURBSProjectVectorCurve trim:true` does NOT cut.** It adds an untrimmed `NURBSCVSurface` **copy of the parent**. Proven with two structurally different profiles — one spanning the full vault width, which a real trim would have split in two — producing **byte-identical** output: `nObj=7`, one `NURBSCVSurface`, `Y 0…900`, `numCVs [9,4]`. `trim:false` adds **no** surface at all; `flipTrim` only flips a flag | 3 variants × 2 profiles. **Cutting an aperture needs a Boolean modifier or a surface split — not this class** |
| **Pre-commit append ordinals ≠ committed set indices.** `appendObject` returns the ordinal (1, 2, 3); after commit the same three objects sit at indices 10, 20, 21 of a 21-object set. `parent:`/`rail:`/`appendCurve` take the **ordinal**; `getObject rset i` takes the **committed** index | 3×3 + 3×3 + blend → 21 sub-objects enumerated. Filtering committed sub-objects with `k > <ordinal>` silently reads the wrong object — that mistake cost one probe here. **Filter by `classOf`** |
| **A NURBS node's `min`/`max` is not the NURBS geometry.** A closed `NURBSPointCurve` over a `750…1050 × 375…525` rectangle has node bbox `714.645…1080.17 × 286.503…617.732`. Sample `evalPos` | both profile curves measured |

**What this changed in the build.** `mcpNurbsAppendParent` is **gone**. Parents are referenced by
`nurbsID` bound from the committed sub-object (`mcpNurbsSurfID`, first surface — the P4 rule). Census
counts moved: `blend` **3 → 1**, `trim` **2 → 0**; `rail_sweep` / `two_rail_sweep` stay at **1**.
The example's `SUR_007_VaultSkylight` is renamed **`SUR_007_VaultApertureGuide`** because it never
opened a skylight. Measured after the fix: `SUR_001_Vault` keeps its own 2 surfaces, `SUR_006` holds
1 (`NURBSBlendSurface`), `SUR_007` holds 0 surfaces / 2 curves — **no duplicate parent shell anywhere
in the scene.**

### P4b round 2 — verified state, re-run in the main thread, not taken from a report

```
py_compile scripts/*.py                                        0
validate_specs.py --dir examples                                0   PASS 90 / FAIL 0 / WARN 0 / SKIP 12
  … --warnings-as-errors                                         0   PASS 90 / FAIL 0 / WARN 0 / SKIP 12
  … --build                                                      0
validate_specs.py --dir specs/recipes/nurbs --allow-draft        0   PASS 54 / FAIL 0
build_nurbs.py --in examples --out <tmp>                         0   self-check G-41..G-56 16 pass 0 skip 0 fail
build_nurbs.py x2 into two temp dirs                            0   md5 c708d2f2a1cce39040b002fa2690289c both == examples/nurbs.ms
fault injection  tension1:1.5                                    0   build exits 1 on G-55; linter FAIL
fault injection  relation naming a relation's own output        0   build exits 1 on G-50 + G-56; linter FAIL
verify_script    parent1ID:12345 / "…P" / unbound name          0   refused, in memory
fileIn examples/nurbs.ms (live Max)                             0   10 nodes; 2 further calls idempotent, identical bboxes
per-node relational census                                       0   SUR_001 2 surf · SUR_006 1 (blend) · SUR_007 0 surf / 2 curve
measured SUR_006_CanopySoffit                                    0   [0,450,420]..[1800,900,603.016]  (was ..[1800,1518,611.8])
measured DRV_001_VaultPanels                                     0   max z 600.97 -> still reads the FIRST surface, not the 25 cm shell
scene after the run                                              0   objects.count = 0
```

### P4b schema extension — authoritative design (decided by the orchestrator, 2026-10-04)

**This section is the contract for the four new `nurbs.json` kinds.** `07` documents it, `validate_specs.py`
lints it, `build_nurbs.py` emits it. Where an implementation seems to want a different key name, this
section wins — it exists so three files cannot drift.

**Standing rule preserved:** kinds stay **geometric** and never name a MAXScript class, plugin or tool.
The class that implements a kind is an implementation detail of the builder.

| kind | geometry it describes | new keys | MAXScript the builder emits |
|---|---|---|---|
| `rail_sweep` | one or more cross-sections swept along **one** rail | `rail_section_ids` (exactly 1), `section_ids` (≥2 cross-sections), `parallel` (bool, default `true`) | `NURBS1RailSweepSurface rail:<ordinal> parallel:<b>` then `appendCurve` per cross-section |
| `two_rail_sweep` | cross-sections swept along **two** rails; section width adapts to rail separation | `rail_section_ids` (**exactly 2**), `section_ids` (≥2), `parallel` | `NURBS2RailSweepSurface rail1:<ordinal> rail2:<ordinal> parallel:<b>` then `appendCurve` per cross-section |
| `blend` | a transition surface **spanning the gap between two surface edges**; the parents need not touch | `parent1_ref`, `edge1`, `parent2_ref`, `edge2`, `tension1` (**optional, `0.0`**), `tension2` (**optional, `0.0`**) | `NURBSBlendSurface parent1ID:<var> edge1:<n> parent2ID:<var> edge2:<n> tension1:<f> tension2:<f>` |
| `trim` | a closed profile **projected onto a surface** along a vector. **It does not cut** — `trim:true` only adds an untrimmed copy of the parent | `surface_ref`, `trim_section_ids` (≥1 closed profile), `p_vec` `[x,y,z]`, `seed` `[u,v]` (**optional, `[0.5,0.5]`**), `flip_trim` (bool, **optional, `false`**) | `NURBSProjectVectorCurve parent1ID:<var> parent2:<profile ordinal> pVec:[..] seed:[..] trim:false flipTrim:<b>` |

> **Round-2 amendments (2026-10-04), all measured — see §"Relation semantics, corrected":**
> surface parents are referenced by **`parent1ID:` / `parent2ID:`**, never re-instantiated inside the
> dependent set (that was the duplication defect); `tension1/tension2` default **`0.0`**, not `1.0`;
> `trim` emits **`trim:false`**. Rails stay **in-set ordinals** — they are curves, and only surface
> parents take the id form.

- **Rails and trim profiles reuse the existing `sections[]` primitive** — an ordered list of `points_cm`.
  No new primitive is introduced. `section_ids` / `rail_section_ids` / `trim_section_ids` all reference
  `SEC-nnn` ids exactly as `section_ids` already does.
- `surface_ref` / `parent1_ref` / `parent2_ref` reference `SUR-nnn` ids **declared earlier in the same
  file**, matching the existing `derivatives[].surface_ref` convention.
- `edge1` / `edge2` are integers `1..4` = low-U, high-U, low-V, high-V (the convention the verified
  transcripts used: `edge1: 1 edge2: 1` read back exactly).
- **No literal sub-object index may appear in emitted MAXScript.** Bind each index to a variable
  immediately after its append (`local secIdx = nset.numObjects`) and use the variable. A bare literal is
  wrong the moment a `thickness_cm` offset shell inserts another surface into the set.

New invariants, numbered after the existing `G-49`, documented in `07` §9.7 and linted by
`validate_specs.py`:

| id | rule | failure |
|---|---|---|
| **G-50** | arity: `rail_sweep` has exactly 1 rail, `two_rail_sweep` exactly 2, `blend` has both parents and both edges, `trim` has a surface and ≥1 profile | FAIL |
| **G-51** | **every cross-section of a rail sweep must intersect its rail(s)** within `tolerances.linear_cm`. This is the pre-flight for the silent drop: Max discards a sweep whose sections never meet the rail, and reports nothing | FAIL |
| **G-52** | `blend` parents resolve to `SUR-nnn` ids **declared earlier** in the file; `edge1`/`edge2` integers in `1..4` | FAIL |
| **G-53** | `trim`: `p_vec` is 3 numbers with non-zero magnitude, `seed` is 2 numbers, `flip_trim` is boolean | FAIL |
| **G-54** | **emitted-surface census.** A committed node must contain exactly the number of `NURBSSurface` sub-objects the spec implies. Enforced at *build* time by the emitted `.ms`, which counts them after `NURBSNode` and throws on mismatch. **Counts after P4b round 2:** `rail_sweep` 1 · `two_rail_sweep` 1 · `blend` **1** · `trim` **0** | FAIL at build; **honest SKIP with reason at lint time**, since a static file cannot observe a commit |
| **G-55** | `tension1` / `tension2`, where present, are floats in `0.0 … 1.0`. Max neither rejects nor bounds a larger tension and the overshoot grows with it — measured `295.64 cm` outside its own geometry at `1.0/1.0` | FAIL |
| **G-56** | no `parent1ID:` / `parent2ID:` position in the emitted MAXScript holds a **literal**; every one is a variable bound from a committed sub-object | FAIL at build — a string there is an `IntegerPtr` conversion error and a bare number is an **`EXCEPTION_ACCESS_VIOLATION` that kills 3ds Max**, not a catchable error |

**G-54 is the important one.** P4 shipped a stage whose entire cost of a wrong decision was invisible;
G-54 makes an unverifiable build fail loudly instead of shipping geometry that quietly lost a rail.
**G-56 is the one that protects Max itself** — it is the only rule in this repo whose failure mode is
a process crash rather than wrong geometry.

### Reference claim-by-claim pass — VERIFIED (P4b-r, 2026-10-04)

The two files P4b left open (`references/maxscript-splines-shapes.md` = the real name behind
`references/13`, and `references/arch-modifiers-and-procedural-reference.md` = behind `06`)
were **executed claim by claim against live Max 2026.3.2**, not rewritten on suspicion.
Full transcripts: **`references/_p4b-remainder-evidence.md`** — read it before touching either
file again. Both files are now corrected in place with dated notes.

**`maxscript-splines-shapes.md` came out largely vindicated.** All 11 shape constructors build
with every documented keyword reading back the right value; all 15 `render_*` properties exist
with the documented defaults; all **27** `splineOps` pass with a bogus control throwing; all
14 path-interpolation functions work; every knot/spline/segment method works with the
documented semantics, including `numSegments == numKnots` closed / `- 1` open. Ten corrections
were needed, the substantive ones being:

| Fact | Evidence |
|---|---|
| **`bezierShape()` is not usable.** It constructs and reports `class=SplineShape`, but `updateShape` on it throws `curve with insufficient knots` at **2, 3 and 4 knots**. The doc's "`-- same thing`" was wrong | three knot counts, same throw; a plain `splineShape()` with 2 knots updates fine |
| **A real `splineShape()` trap the file never mentioned:** `updateShape` throws if **any** spline in a multi-spline shape has only 2 knots. 3 knots per spline is fine | 3-knot + 2-knot → THROWS; 3-knot + 3-knot → OK |
| **`setKnotType … #bezierCorner` silently no-ops on knot 1** and works from knot 2. No error either way | `getKnotType` reads `corner` on knot 1, `bezierCorner` on knot 2. `#smooth`/`#bezier` work on knot 1 |
| **`getSegLengths` return shape is undocumented** — 5 values for a 2-segment spline: cumulative params, per-segment lengths, total | `#(0.657467, 0.342533, 134.36, 70.0, 204.36)`, total = `curveLength` |
| **The `pathParam` keyword is type-checked but INERT.** Default, `:true` and `:false` all return the identical point; `pathParam:#bogus` throws, proving the name is real. The doc's "`false`=length-based / `true`=vertex-based" is unsupported | `interpCurve3D` → `[100,0,0]` in all three cases; `lengthInterp` → `[100,0.199425,0]`, measurably different |
| **`delete <base>` does not delete its instances** — after `delete bx`, the instance survived. Same rule already recorded for dummies | `Box002` alive after `delete Box001` |
| `sin` takes **degrees** (`sin 90` = `1.0`), so the doc's `[i, sin(i)*50, 0]` snippet is correct as written | measured |
| `Arc` stores angles in `from` / `to`, not `from_angle` / `to_angle` — the doc's *code* was right, only a read-back reader would guess wrong | `from=0.0 to=180.0` |

**`arch-modifiers-and-procedural-reference.md` was substantially wrong**, and its errors were
of exactly the kind that survive review because they read as authoritative:

| Fact | Evidence |
|---|---|
| **All 23 classes construct** (bogus control throws) — but **6 cannot be attached via MAXScript `addModifier`**: `Extrude` `Sweep` `Lathe` `Surface` `CrossSection` `Bevel_Profile` all construct standalone and all make `addModifier` throw | two-stage probe isolating construct vs. attach; `Shell` succeeded as the positive in the same batch |
| **The typed MCP tool `3dsmax-mcp_add_modifier` IS the working route** for 5 of those 6. `Bevel_Profile` fails through every route: `Unable to convert: Bevel_Profile to type: Modifier` | typed calls executed on a live `Box001` |
| **Three class-name corrections:** `ChamferMod`→**`Chamfer`**, `Symmetry`→**`symmetry`**, `Surface`→**`surface`**. The documented names construct; `classOf` reports these | constructor sweep with `classOf` read-back |
| **`Conform` is a spacewarp-class object** — `classOf` = `ConformSpaceWarp`, and its 0-arg constructor **throws**. `SpaceConform` is the modifier-class counterpart | `Conform=THROW`, `SpaceConform=OK:SpaceConform` |
| **~13 documented parameter names do not exist.** `Shell`: `segs` `overrideEdgeMatID` `edgeMatID`. `Lattice`: **`Joint_Type` `Both` `Ignore_Hidden_Edges`** — i.e. exactly the three the mullion recipe depends on. `Chamfer`: `mitering`. `Lathe`: `direction`. `RetopologyComponent`: `numFaces` `autoEdge`. `Bend`: `Low` `High` | each list probed with a known-positive and a `totalBogusXYZ` negative in the same call, so the probe could detect both |
| **`Lathe`'s axis property is `axis` and it is a `matrix3`, not an integer enum** — the doc's "`direction` (`0`=X, `1`=Y, `2`=Z)" is wrong in both name and type | `matrix3 [1,0,0] [0,-1.6e-07,-1] [0,1,-1.6e-07] [0,0,0]` |
| **Fully correct, left untouched:** `Extrude` (all 7), `Uvwmap` (all 9), `Noisemodifier` (all 6 — `strength` really is a `point3`), `SliceModifier` (both), `sweep` (6 of 7), `symmetry` `axis`/`flip`, `Normalmodifier` `flip`/`unify` | measured values match the doc |
| `Sweep.PivotAlignment` reads **`-1`**, not the documented `0..8`; `symmetry.threshold` reads **`0.01`**, not `0.1`; `symmetry.slice`/`weld` are **integers** `1`, not booleans; the axis properties default to `2`, not `0` | measured |
| **The Data Channel operator vocabulary in the doc was wrong.** The real vocabulary is **32 snake_case operators**; the tool's key is **`type`**, not `name`. **`DistToNode` and `FaceArea` do not exist** — and the doc's first recipe uses `DistToNode`. `Position` is an attribute of `vertex_input`, not a graph node. `list_dc_presets` returns `[]` in this build | `add_data_channel` with a bogus operator returns the full vocabulary in its error text; a correct call built a 2-operator graph |
| **The "CRITICAL Max 2027 Rule" is UNVERIFIED and cannot be tested here.** It is scoped to Max 2027; this is 2026.3.2. The field the inspector exposes is `Internal`, not `operator_ops`, and `blend_modes` already read `#(1, 1)` with no manual intervention | `inspect_data_channel` response recorded in the evidence brief |
| **§3 routed to two tools that do not exist: the whole `mcg_*` family and `curve_model`.** Definitive, not inferred — verified by direct inspection of the live connected tool list. The doc twice recommends `curve_model` as the fallback for `Bevel_Profile`, which is itself unusable, so it recommended a nonexistent tool in place of a class that does not work | live toolset listing |
| **UNVERIFIED, deliberately not guessed:** the real `surface` / `CrossSection` parameter names (11 candidates each, all negative), the `FFD_*` control-point route (`control_point_1` → `NO`), `animateAll`, and the `current_built_in_shape` enum mapping | labelled in the file |

#### Probe methodology discovered here — cheap, calibrated, reusable

| Fact | Evidence |
|---|---|
| **`isProperty <obj> <name>` is a calibrated existence test for built-in classes** — `false` for a bogus name, `true` for two known-positives in the same call | the calibration batch that opened the pass |
| **`getProperty <obj> (<string> as name)` is a valid DYNAMIC read — and this NARROWS an existing CHECKPOINT row.** §"NURBS surfaces and grids" records *"`getProperty o #x` also fails"*; that is **true for the NURBS plugin classes and false for built-ins**. Likewise `o["name"]` returns `undefined` rather than throwing | `getProperty gTestArc #radius` → `40.0` |
| **`execute` DOES work.** Three apparent failures were `"string" + numericValue` type errors. Always write `(execute code) as string`. This matters because a *bogus* expression still throws, so `execute` is the correct way to sweep candidate names with a real negative control | `execute "1+1"` "failed" only because its result was concatenated raw |
| **A uniform `NO` across a heterogeneous list is a broken probe.** Every parameter list above carried a known-positive *and* `totalBogusXYZ` alongside the unknowns, so absence and detectability were separated in the same call | standing guard from the P4b incident, now applied to property probes |

#### Four constructs that do not work in this bridge — do not retry

| Construct | Result |
|---|---|
| ~~`getCurrentException()` inside a `catch`~~ **WITHDRAWN 2026-10-05 — see §"Incident log 2026-10-05 (P10-lite)". It works: 6 of 6 throw kinds and 4 of 4 in a second batch, with a non-throw control proving the catch was not entered spuriously.** The aborts these probes suffered were caused by *unguarded property access elsewhere in the script*, not by this |
| `global fn name args = (...)` | parse error. `local fn name args = (...)` is valid; **`local function` is not** |
| `modPanel.setCommandPanelCurrentMode #modify` | throws — no UI panel available through the bridge |
| `modPanel.addModToSelection (…)` | returns OK and **silently adds nothing** (`modifiers.count` unchanged). This is why the 6 unattachable modifiers have no MAXScript fallback |

#### NEW HAZARD — Chaos Scatter's clothing callback crashes Max under a heavy modifier stack

While a **20-modifier stack** was assembled on one `Box` in a single scripted call, **two**
modal dialogs appeared:

```
MAXScript Callback script Exception
-- Address: 0x725125d; nCode: 0x00000000C0000005
-- Desc: EXCEPTION_ACCESS_VIOLATION The thread tried to read from or write to a
        virtual address for which it does not have the appropriate access.
-- Read of Address: 0x0000000000000000
-- File name: C:\Program Files\Autodesk\3ds Max 2026\stdplug\tstdcripts\MassFX\px_modifierClothing.ms
-- Line number: 7
```

Observed: two dialogs; 20 modifiers on one node; **no ChaosScatter object existed in the
scene**; the bridge stayed responsive and the node deleted normally afterwards (scene back to
`objects.count = 0`). **INFERENCE, not isolated by experiment:** `px_modifierClothing.ms` is a
Chaos Scatter callback on geometry-stack changes and dereferenced a null pointer while the
stack was mutating.

**This is a P6 hazard.** Chaos Scatter is the user's only working scatter route (ForestPack is
absent) and the failure mode is a **hard process crash, not a wrong result**. Standing rule:
build modifier stacks incrementally; never assemble a stack of this size in one scripted call.

#### RESOLVED at P6 by deliberate bounded ladder — the cost was a reboot (2026-10-05)

PLAN §"Next actions" item 1 required this attribution to be settled rather than left as inference.
It **was** run, on a clean empty scene, one rung per call, `objects.count` reported at every rung so
a break would be attributable. The answer is worse than the P4b-r observation:

| rungs on one `Box` | result |
|---|---|
| 1 · 2 | `Extrude` and `Bevel` throw on `addModifier` (`mods=0`) — **the P4b-r "6 unattachable modifiers" finding, re-confirmed**, not a hang |
| 5 | clean — `Shell` `Chamfer` `Lattice` `Edit_Poly` `Uvwmap`, every rung `threw=false`, `mods` tracked the rung, 38 ms total |
| 10 | clean — + `TurboSmooth` `Noisemodifier` `Bend` `Twist` `Taper`, every rung `threw=false`, 28 ms total |
| **20** | **`execute_maxscript` timed out; `get_scene_snapshot` then timed out; `get_bridge_status` then aborted. Max was frozen on the main thread, had to be killed, and the machine was rebooted.** |

**What this establishes.** The failure is **not** an exception and **not** a dialog — it is a
permanent main-thread freeze, and a timeout is the only symptom. 10 rungs are demonstrably safe and
the break is between 10 and 20; the exact breaking point is **not** established and **must not be
re-measured**, because the price of the answer is a reboot.

**Attribution, now measured rather than inferred.** At P4b-r the link to stack size was an
inference, and it was hedged because *no ChaosScatter object existed in the scene* during the event.
That hedge is now **retired in the other direction**: the same hang occurred again with **no
ChaosScatter object in the scene at all**, so the trigger is the geometry-stack change itself and the
`px_modifierClothing.ms` callback is a Chaos Scatter callback that fires on any such change, not a
scatter-specific one. Chaos Scatter's presence in the scene is **not required** for the hazard.

**Standing rule, now measured and not merely prudent:** build stacks **≤ 5 modifiers per
`execute_maxscript` call**; treat **> 10 on a single node as forbidden** without asking the user
first. A timeout must never be reported as "the bridge is down" without a cheap `get_bridge_status`
— the scene may be alive and merely busy, and in this case it was neither alive nor recoverable.


### Bridge transport — the MCP client caches the pipe name (measured 2026-10-05, P6)
This cost a session restart and it is not discoverable from the tool error, so it is recorded here.

| Fact | Evidence |
|---|---|
| **A `ConnectionError: Could not connect to 3ds Max on 127.0.0.1:8765` does NOT mean the bridge is down.** In `3dsmax-mcp/src/max_client.py`, `MaxClient.__init__` calls `discover_instance_pipes()` **exactly once**, and only when `transport == "auto"` and `pipe_name` is still the default. The winning name is then cached for the process lifetime. A Max restart changes the PID, hence the pipe name, and the client keeps calling `CreateFileW` on the **dead** PID's pipe forever | `discover_instance_pipes` appears at **one** call site (`max_client.py:153`); every subsequent call uses `self.pipe_name` |
| **The error message names TCP even when the pipe is what failed.** `native_available` probes the cached pipe, gets `ERROR_PATH_NOT_FOUND`, returns `False`, and the command silently falls back to TCP — so a dead-pipe cache is reported as a TCP problem | the raise sites are the TCP branches (`max_client.py:443`, `:448`) and nothing in the message mentions the pipe |
| **Diagnosis is a two-line check, not a guess.** `%LOCALAPPDATA%\3dsmax-mcp\instances\pid-<PID>.json` lists every instance ever seen; `CreateFileW` on each name separates live (`open`) from dead (`ERROR_FILE_NOT_FOUND` / `PATH_NOT_FOUND`). Stale files are **never** pruned — two dead PIDs sat alongside the live one | `pid-17152.json` → `open`; `pid-25584` / `pid-27352` → `ERR2`; all three files still present |
| **Max itself was fine.** The native GUP bridge had already registered the new instance and its descriptor was written seconds after launch — only the client was stale | descriptor `pid-17152.json` mtime 21:42, Max pid 17152 |
| **Restarting the Max client is not enough, and killing the MCP server does not recover in-session.** The registered fix is to restart opencode so the server re-resolves. **A restart of Max alone is not a fix** — do not spend another cycle on it | `taskkill` on `3dsmax-mcp.exe` succeeded, the process did not come back, and the `3dsmax-mcp_*` tools left the toolset for the rest of the session |

**Standing rule: after any Max restart, expect to restart opencode.** And when a bridge call fails,
run the two-line pipe check **before** concluding anything about Max — the error text is about the
wrong transport.

### The Boolean modifier is unusable in this build — MEASURED (P6, 2026-10-05)
**The most consequential Max finding in the repo.** A wall cannot be cut with a Boolean
modifier here, and the failure is **silent** — the script runs, nothing is removed. Every row
has a known-bogus control in the same batch.

| Probe | Result |
|---|---|
| `Boolean()` | **throws** `Type error: Call needs function or class, got: undefined` |
| `BooleanMod()` | constructs, `classOf BooleanMod` — but the paramblock is **Voxel Map's**: `m[1]=SubAnim:voxelSize`, `m[2]=toleranceFactor`, `m[3]=bevelDistance`, `m[4]=bevelDepth`. `VoxelMap()` is itself `NotCreatable`. The Boolean name is **shadowed in the class registry** |
| `ProBoolean()` | constructs, but `superClassOf` is **`GeometryClass`** — a spacewarp-style *object*, not a Modifier. Constructing one **leaves a node in the scene** (3 orphans accumulated while probing) |
| native bridge `native:add_modifier` with `"Boolean"` | **attaches**: `node.modifiers` → `#modifiers(Boolean:Boolean)`. But the **operand is never set** — `snapshotAsMesh` reads `verts=8 faces=12`, unchanged, for `operation:1`, `object:NAME`, `object:"NAME"`, `boolobject:NAME` and every combination |
| the committed modifier | `isProperty` **false** for `#operation`, `#object`, `#boolobject`. Control `isProperty #totalBogusProp` is also false, so absence is *detected*, not assumed |
| `getModifier 1 node` | **throws** the same type error. `node.modifiers[1]` **works**. `node.modifiers` prints `#modifiers(Boolean:Boolean)` |

**Consequence, and the trap.** P4b-r measured that 16 of 23 modifiers attach with `addModifier`
and 6 more through the typed tool, recording that `Extrude`/`Bevel` throw. **Boolean was simply
never in that batch of 23.** The lesson is the count, not the class list: *a modifier being
absent from a verified set is not evidence it works.* Probe what you intend to use.

**How P6 coped.** Walls are built as **solid cells** tiling wall-minus-openings — a column-row
decomposition along the facade run axis, cut at every opening's `u` boundary and then at the `v`
boundaries of the openings covering each column. Because every boundary comes from some opening
edge, a column is wholly inside an opening's `u` span or wholly outside it, which makes the
subdivision exact with **no gap and no overlap**. `assembly.json` carries the cells in
`wall_cells[]` (52 for `pavilion-01`), so the gate measures the scene against a real table.
`G-82` asserts the volume identity and `G-83` asserts full wall thickness. **The stage now emits
zero modifiers**, which retires the 20-rung freeze hazard by construction rather than by
chunking.

### A census that counts its own bookkeeping cannot observe failure

The first `assembly.ms` opened with `Boolean()`, cut nothing, and its `G-80` census **passed**:

```maxscript
local committed = 0
for cut_pair in cut_pairs do ( ...; committed = committed + 1 )   -- counts attempts
if cut_count != 16 do ( throw ... )
```

The live run had `objects.count` correct at 208 and **every modifier stack empty**
(`nodes carrying modifiers=0`). A counter is unfalsifiable by the very failure it exists to
catch. The census now **walks the scene** and the walk is itself a required needle in the
builder's self-check.

### Two harnesses that reported success while testing nothing

Both were written by me on 2026-10-05, and both are recorded because the failure mode recurs.

| Harness | What it claimed | What was wrong |
|---|---|---|
| The fault-injection run | **0 of 8 fired** | It mutated `examples/assembly.json` and re-ran the builder. `assembly.json` is the builder's **output**, so every mutation was overwritten before any rule saw it. The rules must be exercised by calling the predicates with a mutated document — **11 of 11 fire that way** |
| The bbox comparison's verdict | `VERDICT: PASS` | It printed PASS having made **zero** comparisons: prediction keys used `EL-014`, node names use `EL_014`. A verdict must require that the expected number of comparisons actually *happened*, not merely that no failure was recorded |

A third, smaller one: the `baseObject` negative control was initially `copy PROTO_CMP_001`,
whose **name still starts with `PROTO_`** — so the control matched itself in the scan and
reported the one value that would have exonerated a broken probe. It now renames the control to
`CTRL_PLAIN_COPY` first. P5's "a uniform `true` is a broken probe" was right; it just needed the
control to be *outside* the population it scans.

### MAXScript gotchas
- `fileExists` does **not** exist → `doesFileExist`. `executeFile`/`runScript` do **not** exist
  → **`fileIn`**.
- `stopCreating` takes **0** arguments.
- `modifiers <node>` function form does not work → use the `node.modifiers` **property**.
- **`getModifier <i> <node>` THROWS** (`Type error: Call needs function or class, got:
  undefined`) → use **`node.modifiers[i]`**, which works and prints `#modifiers(Boolean:Boolean)`.
  The first `assembly.ms` used `getModifier` in its own idempotent stack reset, so that reset
  never ran.
- A standalone modifier (e.g. `Sweep()`) is not a node and cannot be `delete`d.
- `introspect_class` paramBlock reflection is wrong for shapes (`Rectangle` has `width`/`length`,
  default 25.0, despite reporting `paramBlocks: []`).
- Material identifiers are internalNames: `OpenPBR`, not `OpenPBRMaterial`.
- String concatenation precedence: `("x" + i as string)` throws — write `("x" + (i as string))`.
- **`"prefix" + numericValue` throws too** — the whole left-hand side is not enough; wrap the
  number: `(value as string)`. This masqueraded as "`execute` is broken" three times before it
  was identified.

---

## Tooling that always fails — never call

`scatter_forest_pack` · all 14 `tyflow_*` tools · `get_railclone_style_graph`
(reason: forestPack, forestLite, tyFlow, railClone, phoenixFD are all absent).

Substitutions: ChaosScatter for scatter; PhysX / Max particles for physics; instance copies via
`clone_objects` for RailClone-style patterning.

---

## Unverified — must be checked before use

- `references/nurbs-complete-guide.md` — substantially correct. **The four P1-b bugs are now
  corrected in it** (2026-10-04): `appendObject` index claim, 4× `stopCreating <node>`, the `close`
  method claims, `NURBSControlVertex` weight note. Everything else is still unverified — verify
  claim-by-claim, do NOT rewrite on suspicion.
- `references/nurbs-architecture-recipes.md` — same. 21 code sites corrected for the same four
  bugs. Still unverified beyond that.
- ~~`references/13` shape/spline ids~~ · ~~`references/06` modifier params~~ — **CLOSED at P4b-r.**
  The real files are `references/maxscript-splines-shapes.md` and
  `references/arch-modifiers-and-procedural-reference.md`; both have now been executed
  claim-by-claim against live Max and corrected in place. Transcripts in
  `references/_p4b-remainder-evidence.md`.
- **New at P4b-r, all labelled UNVERIFIED in the corrected files:** the real `surface` /
  `CrossSection` parameter names (11 candidates each, all negative) · the `FFD_*` control-point
  access route · `animateAll` · the `Sweep.current_built_in_shape` enum mapping · the Data Channel
  "Max 2027 Rule" (wrong field name, and scoped to a version this installation is not).
- ~~`procedural-graphs.md`~~ — **its subject matter is unavailable.** It documents the
  transactional `mcg_*` workflow; **no `mcg_*` tool exists in the connected toolset.** Marked
  OBSOLETE rather than deleted, consistent with `tyflow-graphs.md`.
- `tyflow-graphs.md` (moot — plugin absent) · `maxscript-*` (deduped at P4b-r; `script_controller`
  guidance removed) · `architecture-exterior-pipelines.md` · `curve-construction.md` (written
  against a nonexistent `curve_model` tool — the P4b-r pass confirmed `curve_model` is absent
  from the live toolset, so this file needs a rewrite, not a fix).
- **New at P4b round 2, all labelled UNVERIFIED in `references/12-nurbs-gotchas.md` §7.6.** ✅ **the
  first two are CLOSED at P12 — see §P12, and note the retraction was itself wrong:**
  ~~the printed string format of a `nurbsID` — P4b's `railID="0P"` reading was **not reproduced** and
  the pointer prints as a large decimal + `P`, so no format may be asserted~~ **→ `IntegerPtr`,
  printed `<decimal>P`; `"0P"` was real, `rail1ID` reads the full pointer** · ~~why a 5-rib loft's
  `trim:true` copy reports `numCVs [9,4]`~~ **→ the parent's own CV conversion, not the trim**.
  **Still UNVERIFIED:** whether a cross-set `rail1ID:`/`rail2ID:` form exists for *curve* rails (rails
  still use in-set ordinals; only surface parents use the id form) · relation lifetime after the
  parent node is deleted — one test, one outcome, not a guarantee.
- ChaosScatter sub-object wiring beyond the parameter map (e.g. profile binding semantics).
- Corona material parameter names beyond class existence.
- **New at P3, all labelled UNVERIFIED inside the documents themselves:**
  per-layer colour and render flags (`11-layer-standard.md` O-7) · `references/01`'s S8 MAXScript export
  call and Chaos Scatter wiring · `references/09` §6 still says the scene-unit convention is unproven,
  which `CHECKPOINT.md` has now closed — **fix that stale line before P7**.
- ~~`3dsmax-mcp_manage_layers`' object-assignment action name~~ — **CLOSED at P6 as a verified
  negative: no such action exists.** Nine routes ruled out; `layer` is read-only and the tool
  vocabulary is `{list, create, delete}`. See §Next actions and §"Design consequences of the layer
  finding".

---

## Dangling references routing to absent tools — CLOSED 2026-10-30

The register previously at this heading listed six `references/*.md` files as "flagged in
`references/00-audit-p1.md` §7, not yet fixed (outside P1's file ownership)". Re-checked per row,
evidence in `Audit/_dangling-register-recheck.md`. **Both halves of that sentence were wrong:** §7 is
"What this audit does not authorise" and lists no dangling references (the real source is §3's
per-file verdict table plus §4.1), and **three of the six rows were already clean.**

178 absent-tool / absent-global token occurrences across the seven relevant files now classify as
**154 NEGATION · 24 FENCED · 0 LIVE ROUTE**. Four real live routes were found and fixed; no OBSOLETE
router was added anywhere.

| Row | Verdict | Evidence |
|---|---|---|
| `nurbs-complete-guide.md` | **FIXED** — `:3` offered `execute_python` as a co-equal entry point with `execute_maxscript`; that tool is not in the catalog and appears nowhere else in the repo | fixed in place, the file's own parenthetical-negation style |
| `nurbs-architecture-recipes.md` | **STALE — was already clean.** 26/26 hits are negations (`:6`, `:12` banners; `:16`–`:18` table `Why` column; `:144`/`:201`; `:397`) | — |
| `arch-modifiers-and-procedural-reference.md` | **FIXED** — `:7` and `:79` both routed to `set_modifier_property`, which `02-mcp-live-orchestration.md:264` already states does not exist (`:22` names it only inside a retraction quote → NEGATION) | substitutes quoted from `02-mcp…:264`–`266`: `inspect_modifier_properties` + `execute_maxscript`, or `batch_modify` |
| `architecture-exterior-pipelines.md` | **FIXED** — `:122` asserted "`draw_spline` + `add_modifier` … (both tools exist)", contradicting its own `:8` banner and `_closeout-evidence.md:20` | the other 69 hits are negations. `add_offset` also **upgraded from UNVERIFIED to measured-absent** the same day |
| `curve-construction.md` | **STALE — closed 2026-10-06.** Head OBSOLETE banner `:3`–`:14`, "Absent tool → Verified route" table `:37`–`:45`, divider `:87`–`:93`; the 9 hits below it are FENCED by the file's own declaration | — |
| `maxscript-animation-controllers.md` | **STALE — never belonged in this register.** 0 hits; `00-audit-p1.md` §3 groups it under **DEDUPE**, not dangling tools | — |
| `procedural-graphs.md` *(not registered)* | **Coherent as `AGENTS.md` describes** — split, no whole-file router: live Data Channel half `:31`–`:48` + section-level OBSOLETE router `:52`–`:56` fencing all 15 MCG hits | no edit |

**Orchestrator's independent confirmation (live catalog, metadata only — no Max call).** An exact-name
probe returns **0** matches for `execute_python`, `set_modifier_property`, `draw_spline` and
`add_offset`, and **exact matches** for `execute_maxscript`, `add_modifier`, `set_object_property`,
`inspect_modifier_properties`, `batch_modify`, `add_data_channel`, `clone_objects` — so the probe
discriminates, and every substitute the fixes introduce is itself a real tool (a fix that routed to a
new absent name would have been the same defect twice). Note the near-misses the catalog contains:
`set_modifier_state`, `set_object_property`, `set_material_property` — which is exactly how a
`set_modifier_property` route survives a casual read.

**Method note that matters more than the verdicts.** Two of the four defects were invisible to any
scan built from `AGENTS.md`'s absent-tool inventory, because `execute_python` and
`set_modifier_property` are not in it — the orchestrator's own crude pre-scan missed **2 of 4** for
that reason. They were found only by diffing every backticked identifier in the seven files against
the **live tool catalog** (104 identifiers → 80 unregistered → 2 tool-shaped and unguarded).
**Any future re-check must derive its inventory from the catalog, not from a hand-maintained list.**
Two controls prove the classifier can fire: with the routers stripped from the files' own retained
pre-fix bodies it reports **6 and 11** LIVE ROUTE hits, which is what makes the 24 FENCED verdicts
load-bearing rather than convenient.

**Vocabulary correction.** `scatter_forest_pack`, all 14 `tyflow_*` and `get_railclone_style_graph`
**are registered tools** — real tools over absent plugins. They are not "bogus tool names" and must
not be listed as such; the correct statement is the one `AGENTS.md` already makes (never call them,
the plugins are absent).

**Still unsettled, deliberately not edited:** `cosmos_*` is hedged as UNVERIFIED in
`architecture-exterior-pipelines.md` though the catalog settles it as absent — outside a LIVE ROUTE
fix, so it stays recorded in the artifact rather than silently changed. The identifier sweep keyed on
backticks; a bare-word mention would slip through (a regex sweep found none).

---

## The hand-off's central claim was false — prototype material does **not** propagate

`SKILL.md` §5.1 and `agents/max-orchestrator.md` §5.2 both told the user that **one material on a
`PROTO_` prototype covers its whole family** of `PLC_` instances. That was never measured — it was
inferred from the instance route sharing a `baseObject`. Measured 2026-10-05, on the built scene and
again on a fresh 3-node test:

| Step | Result |
|---|---|
| `instance.baseObject == prototype.baseObject` | **`true`** — the sharing is real |
| material set on the **prototype**, read on each of its 10 instances | **`0` inherit**; all read `undefined` |
| material set on **each instance** | **10 of 10** set — per-node, independent |
| material set on an **instance**, read on the prototype | prototype unaffected — **no back-propagation** |
| `instance.baseObject.material = m` | **THREW** `Unknown property: "material" in Box` — a base object has no material slot |
| negative control: the other 28 prototypes | **0** leaked the material, so the probe discriminates |
| plain `copy` with **no** `baseObject` assignment | separate base object, as P6 recorded |

**Shared `baseObject` is a memory optimisation, not an inheritance mechanism.** The material pass is
**per node**: 136 `PLC_` + 29 `PROTO_` + 52 `WAL_` + 27 massing. The prototypes remain useful as named
size references, and `components_registry.json.families[]` plus the `component_ref` column of
`world_table.csv` still let you list a family's members without clicking through Max — but that is a
*data* convenience, not a propagation.

This is the **fourth** false conclusion caught by execution in this repo, and the first one that
shipped inside two documents at once. It is the same shape as the P4b-r parameter-name sweep and the
Boolean-modifier finding: an inference from a *neighbouring* fact, never tested. **Both documents were
corrected** (`SKILL.md` §5.1, `agents/max-orchestrator.md` §5.2 and its §5.6 one-liner).

**Update 2026-10-13 (Phase 14 / Audit 001 — Probe B):** While native automatic propagation across instances
does not occur on `proto.material = m`, a scripted sync pass matching shared `baseObject`
(`for proto in objects where matchPattern proto.name pattern:"PROTO_*" and proto.material != undefined do ( for o in objects where o != proto and o.baseObject == proto.baseObject do o.material = proto.material )`)
propagates materials from the 29 prototypes to all 136 instances in ~5 ms with 0 modifiers.
The user paints only the 29 `PROTO_*` nodes and runs `snippets/sync_proto_materials.ms`.

## Incident log — standing traps (curated 2026-10-28)

The full transcripts of every incident live in `Audit/CHECKPOINT-archive-2026-10-28.md` (the
§"Incident log …" sections, 2026-10-04…2026-10-13). This table is the distilled, still-binding
form; playbooks citing `CHECKPOINT.md §"Incident log"` mean **this section**. Every row was
measured, not inferred, and every row has hit / miss / bogus controls in the archived transcript.

| # | Trap (measured) | The rule it leaves behind |
|---|---|---|
| 1 | Introspection lies: `introspect_class "NURBSSet"` → "Class not found" while `NURBSSet()` constructs fine; `discover_plugin_classes` / `inspect_plugin_constructor` are also unreliable | MAXScript execution is the only ground truth; never test class existence without a known-bogus control in the same batch |
| 2 | A throw is **not** evidence of absence — four refuted negatives: `getCurrentException()` (works, 6/6), `matrix3` (exists; a 4-arg arity error was misread), `findString` (works, 1-based), the "dead pipe" (`FileStream` normalised `\\.\pipe\…` to `D:\pipe`; `CreateFileW` → OK) | Report the value and the throw separately; require hit / miss / bogus before believing any negative |
| 3 | A read-back that agrees with what you wrote is **not** a measurement: `getTiling` echoes the request; a modifier property written in the adding call reads back correctly while being discarded; `getNumMapVerts` on a node is meaningless | Measure through an independent channel: `snapshotAsMesh` + `meshop.getNumMapVerts`, the UV **range**, the bbox |
| 4 | **A 20-modifier stack on one node in one scripted call froze Max permanently — the machine was rebooted** (2 / 5 / 10 rungs were clean, ~30 ms each) | Build stacks incrementally, ≤ 5 modifiers per `execute_maxscript` call; > 10 on one node is forbidden without asking the user; do not re-run the 20-rung probe |
| 5 | `formattedPrint` hung `execute_maxscript` until timeout and crashed Max; the name resolves fine, so *invoking* it is what is fatal; `try`/`catch` does not contain it | Banned through this bridge; use plain `+` concatenation |
| 6 | **Volume does not distinguish a flipped wall** — reversed winding: normal `[0,1,0]`, bbox +Y, the **same** 2.61 m³ (E-14, Phase 16 / P1) | Outward/inward direction must be a separate, independent QA gate (`QA-V1-DIRECTION`), never a volume check |
| 7 | `snapshot` / `collapseStack` on Editable Poly + Shell return an **`Editable_mesh`** base: `polyop.*` throws; `convertTo` then **invalidates the node handle**; `getNumFaces` on the mesh counts **triangles** (96), not polygons (48) | `convertTo … Editable_Poly` → re-fetch `getNodeByName` → `polyop.getNumFaces` |
| 8 | `for o in objects do delete o` silently skips entries — 24 orphans survived it at P5 | Collect names first, delete by name, and run the sweep twice (deleting a base does not delete its instances) |
| 9 | Materials: a shared `baseObject` is a memory optimisation, **not** inheritance — a prototype material propagates to **0** of 10 instances; the pass is per node | Paint the 29 `PROTO_*` nodes and run the scripted sync (`snippets/sync_proto_materials.ms`, ~5 ms, 0 modifiers) — see the section above |
| 10 | Twice, an inference from a *neighbouring* fact shipped as fact in live documents (the prototype-material claim, in two documents at once; the Extrude-attaches claim) | A claim without its own transcript is UNVERIFIED; measure before routing a user to it |
| 11 | **A shared scratch dir plus "delete your scratch files before finishing" destroyed 6 orchestrator scripts** (2026-10-30): the evidence-brief subagent deleted the whole shared temp dir, not just its own files, and a concurrently running repair subagent lost `measure.py`/`measure2.py` the same way — it reported "something external deleted them" and could not explain it | Give each concurrent subagent its **own** scratch directory, and phrase cleanup as "delete only the files you created", never "delete the scratch dir" |
| 12 | `graphify`'s `to_json(force=True)` **silently permits a shrinking graph** — the missing-semantic guard lives inside `if not force` (`export.py:294-353`), and `build_merge` does a per-tier REPLACE, so a re-extraction that re-emits fewer ids than the tier held loses them with no error (2026-10-30: 410 replaced, 31 dropped) | Diff the id sets **before** persisting, confirm every dropped id has 0 inbound edges from out-of-scope files, and treat `force=True` as "I have already accounted for this loss" |

**Do not re-open without a calibrated probe** (hit, miss, bogus in one batch): `getCurrentException`,
`matrix3`, `findString`, the pipe-discovery "dead bridge" — all four were refuted negatives.
**Genuinely absent, re-confirmed 2026-10-27:** `setCopyMode`, `rotationZ` / `rotationX` /
`rotationY`, `angle`.

---

## Next actions

Queue for `poly_surface_shell_v1` — planning document `Audit/AGENT_PLAN_poly_surface_shell.md`
(§C holds the phase plan, §I the closed decisions); measured facts are E-1…E-16 in
`Audit/EVIDENCE_2026-10-27.md` (frozen data — do not re-derive):

1. **P2 — `walls.json` schema.** New §8.x in `references/07-spec-grammar.md` (plan §B.3), gates
   `G-92`…`G-100` in §9, a row in the §4 inventory, and the `scripts/init_project.py` records
   (`INVENTORY` / `SEEDED_FROM_EXAMPLES` / `RESERVED_KEYS`).
2. **P3 — `scripts/build_wall_surface.py` (S4w).** The emitter for the measured route A
   (`polyop.createVert` → `createPolygon` → `deleteFaces` → `Shell`), plus the grammar's step
   tables in §12. P1 proved `Extrude` is **not required** at any step.
3. **P4 — live acceptance + the QA profile `poly_surface_shell_v1`**, with **separate** volume and
   direction gates (`QA-V1-DIRECTION` — incident-log trap 6). When S4w exists, reword the "S5 is the
   last geometry builder" invariant (`agents/max-orchestrator.md:61,378`,
   `references/01-pipeline-workflow.md:58`, `SKILL.md`).
4. **QA-family repairs** (plan §F.2): REPLAY / STACK / WALLS / CENSUS families, the drift sweep,
   `tolerances.linear_cm` semantics, the `scene_units` import, `evalPos` gating.

Maintenance queue (optional, deferred — does not block P2…P6):

5. **Deep semantic re-extraction of the knowledge graph — DONE 2026-10-30.** Measured result and the
   three repaired defects are in the dated section above (2814 → **2911** nodes, 5845 → **7119**
   edges, 27 → **47** hyperedges, 225 → **166** communities all named, manifest pending 23 → **5**,
   0 dangling edges). Note that `graphify label` was **not** used and must not be: with no API key it
   sets `force_relabel=True` (`cli.py:2420`), which skips the curated-label reuse branch
   (`cli.py:2578`) and DISCARDS every curated name. Naming went through
   `GRAPHIFY_BACKEND=none graphify cluster-only .` — reuses `.graphify_labels.json` where the
   membership sig still applies, hub-fills the rest, fully deterministic. **Remainder: 5 files still
   pending by decision, not by oversight** — `references/_form-units-qa-design.md`,
   `Audit/CHECKPOINT-archive-2026-10-28.md`, `Audit/AGENT_PLAN_form_precision.md`,
   `Audit/AGENT_BRIEF_form_precision.md`, `scripts/build_nurbs.py`. Re-run recipe if ever needed:
   `graphify-out/.deep-pass-protocol.md` + `.deep-pass-chunks.json`. The protocol **already carries
   corrections 1–3 in place** — header `⚠️ CORRECTIONS APPLIED 2026-10-30`, §5b rewritten at
   `:295-296`, §5d at `:333`. An earlier revision of this queue entry said the protocol "as written
   still contains the false additive-merge claim in §5b"; that text was stale and is corrected here.
   **User decision 2026-10-30 (pass 2): the 5 stay pending — do not extract them.**
6. **Slim pass on `references/_form-units-qa-design.md` — C+ APPLIED 2026-10-30 (pass 2).** 267 KB
   when this entry was written, **253,557 B after the cut** — still the largest `.md` in the repo
   (`07-spec-grammar.md` is 237,187 B),
   FROZEN (user-approved 2026-10-10), still routed by `scripts/qa_check.py`,
   `references/07-spec-grammar.md` and `agents/max-input.md`. **The citation-map prerequisite is DONE**
   (2026-10-30): `Audit/_form-qa-citation-map.md` — 9 files touch the name, not 3 (`CHECKPOINT.md:158`
   is a 4th routing mention the old queue text missed); 13 live citations; 9 load-bearing sections; a
   93-row inventory whose byte column sums exactly to 267,728 (**re-cut by pass 2 to 82 rows /
   252,537 B; UNRESOLVED 7–8 CLOSED, 9 stays open**).
   **The finding that changes the task:** the split as originally scoped **cannot slim this file.**
   NARRATIVE is only 27,559 B (10.3%) against CITED 95,569 B and FACT-TABLE 141,208 B, so moving the
   narrative out leaves ~234.5 KB — still the largest doc. Recommended option **C+**: move three
   contiguous blocks (1160–1263, 2240–2330, 2674–2731) plus 2 DEAD sections to a new
   `Audit/FORM-QA-SESSION-LOG.md` = 26,161 B (9.8%) for two line-splices. Real reduction needs option
   **D** (§17, 60.5 KB) and is HIGH risk — §17.1 is cited by `qa_check.py:152` and §17.2–§17.7 are the
   schema its emitter implements, so D requires editing a live citer.
   It also catalogues **10 contradictions with current repo state (D1–D10)**. The most serious is D1:
   `:259` claims `qa_check.py` / `curve_gen.py` / `expand_curves.py` / `scene_units.py` do not exist
   and that `scripts/` holds 8 modules (it holds 12) — sitting **inside §5.2, which
   `07-spec-grammar.md:2541` cites**, and half-true (five other scripts really are absent), which is
   what makes it dangerous. D10 (`:1268` "All ten A-* rows remain OPEN", inside cited §14) is
   contradicted by `:150` and `:2747` of the same file; `:374` says "next free ID is G-84" against
   `validate_specs.py:867,915` (91 gates registered, max G-91).
   **RESOLVED 2026-10-30, user decision: errata only, no slimming.** A dated `ERRATA (2026-10-30)`
   blockquote was inserted at the head of the FROZEN doc — `git diff` = **44 additions / 0 deletions**,
   so the frozen body is byte-identical. It lists D1–D10 by **section anchor**, records the
   "confirmed still correct" set (so nobody re-litigates it during a future cut), and states why no
   cut was made. It follows the file's own 2026-10-28 notice convention: resolve by section name, and
   the block's line numbers refer to the frozen 2026-10-10 revision.
   ⚠️ **Side effect, measured and handled:** the insertion shifted every body line by **+44**
   (verified on two anchors — D10's text `1268` → `1312`, D5's `374` → `418`). Two files cited this
   doc by line number. The **live** planning doc `Audit/AGENT_PLAN_poly_surface_shell.md:385` was
   re-anchored to `§24.2 «Design review cases»` (drift-proof). `Audit/EVIDENCE_2026-10-27.md:175`
   still reads `:2693` and was **deliberately left untouched** — this file designates it frozen data
   (E-1…E-16, "do not re-derive or rewrite it"); when reading that pointer, add 44 or resolve by
   section name.
   **CLOSED for C+, still closed for D (user decision 2026-10-30, pass 2).** C+ was authorised and
   executed — measured result in the dated section above (−26,161 B moved to
   `Audit/FORM-QA-SESSION-LOG.md`, 5 splices, §16/§17/§18 byte-identical, 0 dangling live anchors).
   **D (§17, ≈ −60.5 KB) is NOT authorised**: §17.1 is cited by `scripts/qa_check.py:152` and
   §17.2–§17.7 are the schema its emitter implements, so D means editing a live citer. That saving
   is still available and still unauthorised — do not take it on your own initiative.

7. **Installer prune — DONE 2026-10-30 (pass 2), found and closed in the same session.**
   `install_skill.py` copied without pruning, so the 5 files the repo moved to `Audit/` on
   2026-10-28 (`references/_drift-audit.md`, `references/_fix-{a,b,c,d}-notes.md`) kept living in
   both installed copies: installed agents paid context for them and could route to paths that no
   longer exist in the repo. `prune_stale_files()` now converges each install on `collect_files()`,
   scoped to the target, loud about every removal, and **`prune=False` for `--mcp-repo`** because
   that directory is shared with the `3dsmax-mcp-dev` skill. Measured: both installs 5 stale → **0**,
   107 shipped files byte-identical, second run removes 0. Detail in the dated section above.

Standing rules: cancelled stages stay cancelled (P7 / P8 / P9 — user decision 2026-10-05; do not
stub, plan or route toward them). A future entry is a **new dated section**, never a rewrite of an
old one. When a phase closes, cut a new `Audit/CHECKPOINT-archive-<date>.md` and leave the previous
archives untouched.

---

## Archive

Everything older than the current phase — the closed-phase progress logs (Phase 04.3 through
Phase 15), the closed-stage sections (P2, P3, P4, P5), the `snippets/nurbs_arch_library.ms` bug
history, the Artifacts ledger, every incident-log transcript (2026-10-04…2026-10-13), the P10-lite /
P12–P15 close-out sections and the superseded "Resume here" sections — lives **verbatim** in
[`Audit/CHECKPOINT-archive-2026-10-28.md`](Audit/CHECKPOINT-archive-2026-10-28.md) (2341 lines,
repo-only, not shipped in the `.skill` archive). It is history, not instruction: read it for
provenance and transcripts, not for routing.
