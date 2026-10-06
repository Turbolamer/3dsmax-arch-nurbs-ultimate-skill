# AGENTS.md

Instruction file for agents working in `3dsmax-arch-nurbs-ultimate-skill`.
Read `CHECKPOINT.md` first — it is the live status board. Then `PLAN.md` for scope.

## What this repo is

A skill pack (markdown + MAXScript snippets + Python helpers) that teaches an agent to drive
**3ds Max 2026** through the `cl0nazepamm/3dsmax-mcp` bridge for architectural and NURBS modeling.
It is not an application: there is no build, no test runner, no linter, no CI.

**Do not invent commands.** The only executable things that exist today:

```bash
python scripts/env_preflight.py                      # emit MAXScript probes, all checks SKIP
python scripts/env_preflight.py --results r.json     # score captured results; exit 1 on any FAIL
python scripts/env_preflight.py --json               # machine-readable report
python scripts/install_skill.py                     # build .skill + install to ~/.claude, ~/.agents
python scripts/init_project.py --project X --dir D  # scaffold: 11 spec files under D/X/specs/pipeline + project.json
python scripts/validate_specs.py --dir examples     # lint every spec against G-1..G-83
python scripts/build_spec.py --stage massing --in examples --out examples   # emits massing.json + massing.ms
python scripts/build_nurbs.py --in examples --out examples                   # emits nurbs.ms
python scripts/facade_tables.py --in examples --out examples                # emits both P5 JSONs + both CSVs
python -m py_compile scripts/*.py                   # the only "test" that exists
```

`python scripts/place_components.py --in <p> --out <p>` # **S5, LAST builder** — placement + wall tiling + scatter declaration
```

`build_spec.py` accepts `--stage massing` only and exits non-zero for anything else.

**`place_components.py` is the project's last builder**, not a planned one — `PLAN.md` §3's layout
still listed it among unwritten files, and that was wrong. It reads **four** inputs and refuses with
*"`dimensions.json` is missing … a builder never invents an input"* if given less: `assembly.json`,
`components_registry.json`, `world_table.csv` and either `dimensions.json` or `massing.json`. It emits
`assembly.json` + `assembly.ms` and is **zero-modifier** by design (`G-81`).

**Not written and not planned — do not reference these as if they run:** `qa_check.py`,
`capture_views.py`, `export_max.py`, `lint_script.py`, `check_skill_md.py`, `materials.json`, `qa.json`,
`export.json`. P7/P8/P9 were **cancelled by the user on 2026-10-05**, not deferred.

**An emitted `.ms` is not done until it has been `fileIn`-ed and measured.** `build_spec.py` self-checks
`G-34`…`G-40` before writing, which proves the file is well-formed and proves nothing about whether
MAXScript will load it. See `CHECKPOINT.md` §Incident log, 2026-10-04. The same rule has a
table-shaped equivalent, and P5 is where it was executed: **an emitted CSV is not done until it has
been placed in Max and counted** — 136 rows read from `examples/world_table.csv` by MAXScript itself,
136 panels built as reference instances, `objects.count` asserted at 165, five bboxes measured against
an independent prediction. See `CHECKPOINT.md` §"P5 — the live gate". The full S1→S5 chain was run
the same way at P10-lite: **254 nodes**, idempotent over three calls, 0 modifiers, scene back to 0.

**Scope, 2026-10-05 — the user cancelled P7 (materials + UVs), P8 (QA) and P9 (export).** The
deliverable is the model plus a hand-off for materials made by hand. `materials.json` `qa.json` and
`export.json` are scaffolded as reserved stubs and **must not be treated as planned work**; there are
no `qa_check.py` / `capture_views.py` / `export_max.py` / `lint_script.py` / `check_skill_md.py`
anywhere. Read `agents/max-orchestrator.md` first — it is the driver for S1→S5 and owns the hand-off.

## Probe method that is now standard

Two constructs make claim-by-claim verification cheap enough to be worth doing, both calibrated with
a known-positive control in the same call (`CHECKPOINT.md` §"Reference claim-by-claim pass"):

```maxscript
isProperty <obj> <name>              -- existence;  false on a bogus name, true on a real one
getProperty <obj> ("<name>" as name) -- dynamic read-back value
execute "<expr>"                     -- works; a bogus expr throws, so it is the right way to
                                      --   sweep candidate names with a real negative control
```

`execute` is **not** broken — wrap its result: `("x" + execute code)` throws a type error and looks
exactly like a broken tool. Write `((execute code) as string)`.

⚠️ **`((execute code) as string)` reports a FALSE ABSENCE for any value that cannot be stringified.**
It is not a safe existence test on its own. The calibrated form at P5 compares against `undefined`
and carries two controls:

```maxscript
for code in #("quat 45.0 [0,0,1]", "matrix3 1 0 0 0 1 0 0 0 1", "1+1", "TotalGarbageXYZ_fn(1)") do
(
    local v = undefined
    local threw = false
    try ( v = execute code ) catch ( threw = true )
    print (code + " => threw=" + (threw as string) + " undef=" + ((v == undefined) as string))
)
```

`1+1` must come back `undef=false` and the bogus name `threw=true`. If a candidate reads as absent,
re-run it through **this** form before believing it — `as string` on a `matrix3` throws, and the
throw looks exactly like "the class does not exist".

Do not retry: `global fn`, `local fn` **and** a bare top-level `fn` all fail through
`execute_maxscript` — inline the code instead · `modPanel.setCommandPanelCurrentMode` (throws) ·
`modPanel.addModToSelection` (returns OK, adds nothing) · `max zoomext` (parse error).

⚠️ **`getCurrentException()` inside a `catch` DOES work** — the rule saying it "throws itself" was
**withdrawn on 2026-10-05 as false**. It returned a real message for 6 of 6 throw kinds, with a
non-throw control proving the catch was not entered. Use it to diagnose, and see the trap below for
what actually aborts a probe.

## ⚠️ A throw is NOT evidence of absence — four of this file's own rules were wrong for that reason

Re-measured 2026-10-05, each with a hit, a miss and a bogus control in the same batch:

| Recorded as | Actually | Proof |
|---|---|---|
| `findString` absent | **works** | `findString "hello world" "o w"` → **5** (1-based); `"zz"` → `undefined`; `12345` → THREW |
| `matrix3` absent | **exists** | `matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]` → `classOf` **`Matrix3`**. It takes **4 args**, and calling it with 9 numbers gives `Argument count error: Matrix3 wanted 4, got 9` — an arity error misread as absence |
| `getCurrentException()` throws itself | **works** | 6/6 kinds; control `try (1+1)` did not enter the catch |
| **the bridge is dead because the pipe would not open** | **the pipe was open the whole time** | 2026-10-06: `.NET FileStream.Open("\\\\.\\pipe\\3dsmax-mcp-pid-17152")` returns `OPEN FAIL`, because `FileStream` normalises the path against the current drive and tries `D:\pipe`. **`CreateFileW` via P/Invoke → `OK`**, and driving the server through its own stdio transport returns `pong: true`, RTT 1.6 ms |

**The fourth is the same failure as the other three, one layer out.** The first three were a probe that
could not detect a working feature; the fourth was a probe that could not reach a working feature. Both
manufacture an absence. **A probe you have not calibrated against a known-good case has produced no
evidence at all** — it has only produced a result.

Still genuinely absent, re-confirmed in the same batch: **`setCopyMode`**, **`rotationZ`** /
`rotationX` / `rotationY`, **`angle`**.

**The corrected existence probe** — report the value and the throw separately, and require all three
of hit / miss / bogus before believing anything:

```maxscript
local v = undefined
local threw = false
try ( v = execute code ) catch ( threw = true )
out += code + " threw=" + (threw as string) + " undef=" + ((v == undefined) as string) \
        + " cls=" + ((classOf v) as string)
```

A batch of only throws discriminates nothing. **What actually aborts a probe is an unguarded
property access elsewhere** — wrap every property read in its own `try ( ) catch ( )`, and put the
cleanup block **first**, not last.

| You want | Use | Note |
|---|---|---|
| a copy-mode instance | `n = copy src` then `n.baseObject = src.baseObject` | `setCopyMode` is absent; shares the base object, a plain `copy` does not |
| a Z rotation | `n.rotation = quat <degrees> [0,0,1]` | `rotationZ` is absent; 100×200×20 box at rot 90 spans X 200 / Y 100 |
| a substring test | `substring s 1 n` | `findString s sub` works and returns a 1-based index; either is fine |

⚠️ **`node.pos` on a `Box` is `(centre_x, centre_y, base_z)` — the base sits at `pos.z`** (the P3
rule), and it **stays true after `copy`, after a `baseObject` assignment and after a rotation**. To
centre a box vertically, write `pos = [cx, cy, cz − height/2]`. Getting this wrong put every P5 panel
one full height too high; the measurement caught it.

⚠️ **Iterating `for o in objects do delete o` silently skips entries** and left 24 orphans at P5.
Collect the names first, then delete by name: `for o in objects do append names o.name`, then
`for nm in names do ( local nd = getNodeByName nm; if nd != undefined do delete nd )`. Run it twice:
deleting a base does not delete its instances.

**⛔ NEVER add 20 modifiers to one node in one scripted call. This is MEASURED, not inferred, and
the failure mode is a permanent freeze that cost the user a reboot.** The bounded ladder was run
deliberately at P6 on 2026-10-05:

| rungs on one `Box` | result |
|---|---|
| 2 · 5 · 10 | clean — every rung `threw=false`, `modifiers.count` tracked the rung, ~30 ms each |
| **20** | **`execute_maxscript` timed out, then `get_scene_snapshot` timed out, then the bridge stopped answering entirely. Max had to be killed and the machine rebooted.** |

Two modifiers in that list (`Extrude`, `Bevel`) throw on `addModifier` — the P4b-r "6 unattachable
modifiers" finding again — so the ladder used the attachable set: `Shell` `Chamfer` `Lattice`
`Edit_Poly` `Uvwmap` `TurboSmooth` `Noisemodifier` `Bend` `Twist` `Taper`. Notably **no ChaosScatter
object existed in the scene during the hang**, which strengthens rather than weakens the link: the
callback fires from the geometry-stack change itself.

**Standing rule:** build stacks **incrementally, ≤ 5 modifiers per `execute_maxscript` call**, and
treat > 10 on a single node as forbidden without asking the user first. Do not re-run the 20-rung
probe — it has already been measured, and the answer cost a reboot.

**One more trap, measured in the same session:** a *recoverable* hang still burns the tool call.
`Extrude`/`Bevel` on `addModifier` return promptly; a 20-stack returns nothing at all and the
request just times out. Never assume a timeout means "the bridge is down" — the scene may be alive
and merely busy. Verify with a cheap `get_bridge_status` before concluding anything.

## Two absent tool families, confirmed

No `mcg_*` tool and no `curve_model` exist in the connected toolset (verified by inspecting the live
tool list, P4b-r). Max Creation Graph is undrivable from this bridge; the **Max Creation Graph half**
of `references/procedural-graphs.md` is moot — **its Data Channel half is live**, six real `*_dc_*`
tools, so the file is split rather than fenced and deliberately does *not* carry the whole-file
OBSOLETE router. `references/curve-construction.md` **is** now marked OBSOLETE with a router and its
body fenced non-executable (resolved 2026-10-06 — it was written against four absent tools and had no
verified content to preserve).

## The one rule that matters most

**MAXScript execution is the only ground truth. Introspection tools lie.**

`introspect_class "NURBSSet"` returns `Class not found: NURBSSet` — and `NURBSSet()` then
constructs fine. This false negative caused a full plan to be rewritten around a fabricated
conclusion. Also unreliable: `discover_plugin_classes` (wrong/incomplete superclass names, listed
78 of 160 modifiers), `inspect_plugin_constructor` (returns `inferred: true` guesses).

**Never test whether a class exists without a known-bogus control in the same batch:**

```maxscript
for n in #("TotalGarbageXYZ123", "NURBSSet") do (
    local id = undefined
    try (id = execute n) catch ()
    out += n + "=" + ((id == undefined) as string) + "\n"
)
```

If the bogus name is not `undefined`, your probe is broken.

Corollary: **do not rewrite `references/nurbs-complete-guide.md` or `nurbs-architecture-recipes.md`
on suspicion.** They are unverified, not disproven. Verify claim-by-claim against live Max, then
correct only what actually fails. Rewriting on suspicion already happened once and was wrong.

## MCP tool-name collisions

Only `3dsmax-mcp_*` tools act on 3ds Max. A large set of names in the connected toolset belongs to
the **Rhino** server and will fail confusingly against Max:

`get_document_summary` · `get_objects` · `get_object_info` · `create_object` *(different schema)* ·
`capture_viewport` *(different signature)* · `analyze_objects` · `section_profile` · `boolean_union` ·
`boolean_difference` · `boolean_intersection` · `measure_objects` · `intersect_curves` · `loft` ·
`pipe` · `sweep1` · `extrude_curve` · every `gh_*`

Never call these against Max. Do not conclude the bridge is down when one errors.

**Never call** (plugins absent — forestPack, forestLite, tyFlow, railClone, phoenixFD):
`scatter_forest_pack`, all 14 `tyflow_*` tools, `get_railclone_style_graph`.
Substitute Chaos Scatter (`ChaosScatter()` constructs; `CScatter` is NotCreatable), PhysX/Max
particles, and `clone_objects` instance mode.

## Running the preflight against live Max

`env_preflight.py` cannot talk to Max itself — it is two-phase by design.

1. Run it bare. It **prints** the MAXScript probe bodies.
2. Paste each into `3dsmax-mcp_execute_maxscript`, collect the returned strings.
3. Write a JSON file mapping check name → captured output, then run with `--results`.

Phase 3 also accepts `bridge` and `plugins_absent` from the typed tools
(`get_bridge_status`, `get_plugin_capabilities`) since those have no MAXScript equivalent.
Bare invocation exits 0 with everything SKIP — that is not a pass, it is a non-run.

`nurbset_present` asserts the NURBS API **exists** (it was inverted once and briefly asserted the
opposite, which would have failed on a healthy machine).

## `execute_maxscript` operating limits

Runs on Max's **main thread** — a long script freezes the UI. One script per call, under ~2 s.

- **Test nodes must be deleted.** A bare modifier (e.g. `Sweep()`) is not a scene node and cannot
  be deleted; attach it to a node and delete the node.
- Use `execute "<string>"` only for self-contained code — it does **not** see enclosing scope.
- Avoid nesting quotes. `("x" + i as string)` throws; write `("x" + (i as string))`.

Verified function-name traps: `doesFileExist` (not `fileExists`), `fileIn` (not `executeFile` /
`runScript`), `stopCreating` takes **0** args, and `modifiers <node>` as a *function* does not work
— use the `node.modifiers` *property*.

⛔ **Never call `formattedPrint` through this bridge.** It **hung `execute_maxscript` until
timeout and crashed 3ds Max outright** on one attempt (measured 2026-10-06). The name resolves
fine — `formattedPrint` reads back as a valid global — so *invoking* it is what is fatal, and a
`try`/`catch` does not contain it. **Use plain `+` concatenation.** For fixed-width small integers
a literal `"0"` prefix is enough.

`setViewApproximation` / `setRenderApproximation` take a **node**, not a NURBS sub-object —
passing a sub-object throws `Unable to convert: <NURBSPointSurface:…> to type: <node>`.

## `snippets/nurbs_arch_library.ms` — bug history, all CLOSED

The library **loads and works**. All three original defects were **fixed at P1-b on 2026-10-04**
(all ten functions executed live). Kept here as a dated record, not as open work:

1. ~~`appendObject` returns `"OK"`, not an index~~ — **FIXED.** Index = `nset.numObjects` after the call.
2. ~~`stopCreating node` — wrong arity~~ — **FIXED.** `stopCreating` takes **0** args.
3. ~~`NURBSControlVertex` does not construct~~ — **the premise was false; the class constructs
   fine.** The real constraint is that `setCV`/`setPoint` **reject a bare point** with
   `Unable to convert: [0,0,0] to type: NURBSControlVertex` — the wrapper is mandatory. The library
   writes `(NURBSControlVertex …)` correctly at lines 65 and 298.

**A fourth defect was found later, on 2026-10-06, and is also fixed:**
`applyArchTessellation` wrapped `curvatureAngle` in `degToRad`, but that property is in
**degrees**. It now passes `angleDeg` through unchanged. Scope of the saving is honestly ~3% on the
shipped surfaces (`spacialEdge` binds there); the 6.9× figure is specific to a curvature-bound
surface. The unit correction matters regardless — see `CHECKPOINT.md` §P13.

## Context budget — delegate by default

**The main chat thread is the scarcest resource in this repo. Treat it as a coordinator, not a worker.**

Delegate to a `general` subagent by default:

- authoring or rewriting **any** file under `references/`, `agents/`, `examples/`, `specs/`
- audits, reviews, dedupe analysis, per-file verdicts
- reading and summarising more than ~2 files at once
- bulk `grep`/scan sweeps, and verifying a claim across many files

Keep in the main thread, deliberately:

- planning, gate decisions, anything needing the user
- **live Max probes** (see below)
- final verification before declaring a stage done

Rules that make delegation actually save context:

1. **A subagent must return a short structured summary plus written artifacts — never an inline
   dump.** Without this rule delegation just relocates the bloat. Cap the final message
   (e.g. "under 12 lines: what changed, what you verified, what you could not do").
2. **Give each subagent explicit file ownership** and state "modify nothing else". Overlapping
   ownership causes conflicting rewrites of the same file.
3. **Run independent subagents in parallel, in one message.** Disjoint files → no coordination cost.
4. **Pass verified facts down as data.** Put them in a shared evidence brief file the subagent reads,
   rather than re-explaining them per prompt. Do not make subagents re-derive what you already
   executed — that wastes their budget and invites a second, hallucinated version of the facts.
5. **Verify subagent output yourself before trusting it.** Their summaries are claims. The one
   P1 batch reported "all 39 nonexistent tools removed"; an independent `grep` found 13 remaining
   occurrences, which turned out to be legitimate warnings — but that was only established by
   checking, not by reading the report.

**Live Max probes stay in the main thread, deliberately.** This conflicts with "delegate
everything", and the conflict is real: Max is single-threaded, hangs on long scripts, and
second-hand probe results get hallucinated (this exact failure produced the false "NURBSSet does
not exist" conclusion in the incident log). So: orchestrator probes, then hands the *result* to
subagents as data. Keep probe scripts short, batch unrelated checks into a single call, and clean up
scene objects in the same call rather than re-reading state later.

## Repo conventions

- **Update `CHECKPOINT.md` at the end of every stage.** It carries a status board, a
  verified-facts section, an open-bugs table, and an incident log of false conclusions. Read it
  before starting work so you do not re-derive something already settled.
- Verified facts go in `CHECKPOINT.md` labeled as executed. Unverified stays labeled unverified.
- Prefix 3ds Max MCP tools with `3dsmax-mcp_` when writing about them, to keep them distinct from
  the Rhino names.

## Packaging — the "known gap" is closed (P4b-r)

**The gap described in earlier revisions of this file no longer exists.** Do not repeat it.

`scripts/install_skill.py` `collect_files()` now ships, from `scripts/install_skill.py:22-31`:

| Source | What ships |
|---|---|
| `TOP_LEVEL_FILES` | `SKILL.md`, `PLAN.md`, `CHECKPOINT.md`, `AGENTS.md` |
| `references/` | all files |
| `snippets/` | all files |
| `scripts/` | `*.py` — **including `env_preflight.py`, the preflight gate** |
| `agents/` | `*.md` |
| `specs/` | `*.json` |
| `examples/` | `*.json`, `*.ms`, `*.csv` |

Skipped by `_is_packaged()`: `__pycache__`, `.pyc`/`.pyo`, `*.skill`, and any name
containing `test_`, `_test.`, `selftest`, `self_test`, `scratch` or `backup`.

So an installed copy at `~/.claude/skills/` or `~/.agents/skills/` carries its own
preflight, its own builders, the orchestrator playbooks and the example specs. Running
`python scripts/env_preflight.py` from an installed skill directory behaves exactly as
it does in the repo. The checked-in `3dsmax-arch-nurbs-ultimate.skill` archive is
**current** — rebuilt at P4b-r and verified byte-identical to the working tree on six
files.

**Rebuild after any edit** — the archive is a build product, not a source:

```bash
python scripts/install_skill.py    # builds 3dsmax-arch-nurbs-ultimate.skill,
                                   # installs to ~/.claude and ~/.agents
```

If you ever need to re-derive what ships, read `collect_files()` in
`scripts/install_skill.py`; that function is the source of truth, not this section.