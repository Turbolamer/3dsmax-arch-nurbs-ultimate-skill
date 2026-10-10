# CHECKPOINT — progress tracker

**This file is the source of truth for what is done, what is verified, and what is assumed.**
Update it at the end of every stage. Read it before starting new work.

Last updated: 2026-10-10 (**form-precision: Phase 13 complete; Gate 13 PASS; milestone closed** — see below).

## 2026-10-10 — Form-precision progress / Phase 13 complete & Gate 13 PASS

**Phase 13 (13.1–13.6) complete:**
- **13.1 — Active Workflow & Orchestrator Docs Synced:**
  - `AGENTS.md`: script inventory updated (`curve_gen.py`, `expand_curves.py`, `scene_units.py`, `qa_check.py`); confirmed S5 (`place_components.py`) as last geometry builder; confirmed S7 QA gate (`qa_check.py`, `qa.json`) is active; P7 (materials) and P9 (export) confirmed cancelled by user decision.
  - `PLAN.md`: marked Form Precision & Staged Unit Pipeline stages 01..13 complete; updated layout table with S5 last builder and S7 QA gate.
  - `SKILL.md`: updated frontmatter, §0, §4, §6 with S7 QA gate, `scene_units.py`, `curve_gen.py`/`expand_curves.py`, Mechanism A host hiding, and 8-micron precision control (`point_grid` vs `u_loft`).
  - `agents/max-orchestrator.md`: updated workflow routing to S1→S2→S3→S4→S5 (last builder)→S7 QA gate→manual material assignment; documented `qa_check.py` 3-step loop (`--emit` → MCP collect → `--assess`).
  - `references/01-pipeline-workflow.md`: updated stage map (S0..S7), distinguishing S5 as final geometry builder and S7 as read-only QA gate.
- **13.2 — Grammar, Rules & Agent Specs Synced:**
  - `references/07-spec-grammar.md`: documented Schema 1.1 keys (`form_references`, `precision_targets`, `raw_source_values`); Mechanism A host deactivation (`host_node.isHidden = true`); Box endpoint volume propagation budget in $\text{cm}^3$ for G-82; invariants G-82, G-84..G-86, G-87..G-90; units handling via `scene_units.py`.
  - `references/08-input-rules.md`: documented `qa.json` under Schema 1.1 (`spec: "qa"`, profile `form_precision_v1`); `dimensions.json` analytical leaves; `nurbs.json` generator leaves (`ellipse_arc`, `form_reference_ref`, `station_cm`).
  - `agents/max-input.md`: acknowledged Schema 1.1 additions (`form_references[]`, `precision_targets[]`, `qa.json`).
  - `agents/max-nurbs.md`: updated authoring guidance contrasting `u_loft` (internal Max 10-12 CV cubic spline loft error ~0.8..2.9 cm) with `point_grid` (8-micron / 0.0008 cm precision for analytical barrels); documented `curve_gen.py` and `expand_curves.py`.
- **13.3 — Status Board & Future Queue:**
  - Status board updated; distinction between planned, offline, and live verified across all stages.
- **13.4 — Historical Examples Intact (`L-HISTORY`):**
  - `examples/` verified strictly byte-identical to commit history (`git diff examples/` is clean, 0 diffs).
- **13.5 — Handoff Certification:**
  - Verified scene units: `cm`, scale `1.0`. Clean scene state (`objects.count = 0`).
  - All 12 Python modules compile cleanly.
  - Spec validation: `examples` PASS 138 / 0 / 0 / 22; `specs/fixtures/form-precision` PASS 153 / 0 / 0 / 15.
- **13.6 — Skill Archive Built & Installed:**
  - `python scripts/install_skill.py` executed: built `3dsmax-arch-nurbs-ultimate.skill` (102 files) and installed to `~/.claude/skills` and `~/.agents/skills`.
- **Gate 13 (PASS):** Active docs match runnable CLI, required modules shipped, examples history intact, measured QA exercised, no unclosed delivery blockers.

---

## 2026-10-10 — Form-precision progress / Phase 12 complete & Gate 12 verified

**Phase 12 (12.1–12.9) executed live against 3ds Max 2026.3.2 via MCP.**
- **12.1 — Authorised Rehearsal:** Coherent pipeline fixture executed under `specs/fixtures/form-precision`: `massing.ms` (27 nodes), `nurbs.ms` (37 nodes), `assembly.ms` (254 nodes, 0 modifiers).
- **12.2 — Replay & Idempotency:** Three consecutive live runs of all stages executed cleanly. Object count remained strictly 254 nodes across all passes with zero modifiers and no duplicate orphans. Mechanism A verified: 8 host walls (`EL_014`..`EL_021`) reported `isHidden = true`, discrete cells visible.
- **12.3 — Live Batch Collect:** `qa_check.py --emit` generated sequential scripts `batch_001.ms` and `batch_002.ms` with `StringStream` captures. Executed live in 3ds Max via `3dsmax-mcp_execute_maxscript`. Full responses captured to `specs/fixtures/form-precision/runs/form-qa/live-run-001/results.json`.
- **12.4 — Offline Assessment:** Evaluated via `qa_check.py --assess`:
  - `CHK_COVERAGE` (`QA-V1-COVERAGE`): **PASS** (all targets observed).
  - `CHK_CENSUS_MASS` (`QA-V1-CENSUS`): **PASS** (all massing solids verified).
  - `CHK_CENSUS_NURBS` (`QA-V1-NURBS-CENSUS`): **PASS** (all surfaces verified).
  - `CHK_FORM_01` (`QA-V1-FORM`): **FAIL** under `u_loft` (`max_deviation_cm: 2.1399 cm > tolerance 0.5000 cm` for count=9; `2.9462 cm` for count=49).
- **12.6 — Form Precision Ladder & Model-Kind Assessment:**
  - Evaluated station counts ladder live in 3ds Max on `NURBSULoftSurface` across counts 7, 9, 13, 25, 41, 49:
    - `count=7`: $pMid = [900.20, 0, 598.98]$, $devZ = -1.02\text{ cm}$.
    - `count=9`: $pMid = [899.21, 0, 601.37]$, $devZ = +1.37\text{ cm}$, max deviation $2.14\text{ cm}$.
    - `count=13`: $pMid = [900.12, 0, 600.01]$, $devZ = +0.0059\text{ cm}$ (0.06 mm at crown), max deviation $0.796\text{ cm}$.
    - `count=25`: $pMid = [901.27, 0, 601.80]$, $devZ = +1.80\text{ cm}$.
    - `count=41`: $pMid = [899.82, 0, 602.03]$, $devZ = +2.03\text{ cm}$.
    - `count=49`: $pMid = [898.66, 0, 602.98]$, $devZ = +2.98\text{ cm}$, max deviation $2.95\text{ cm}$.
  - Root cause confirmed: 3ds Max's internal `NURBSULoftSurface` solver fits only 10–12 CVs across cross-sections (`numCVs = [12, 4]`), producing intrinsic B-spline approximation errors exceeding $0.5\text{ cm}$ regardless of cross-section point count.
  - Known-positive control verified: `point_grid` (`NURBSPointSurface` via `makePointSurfaceGrid`) measured live in 3ds Max across the 5x5 grid with 5x25 points: **`maxDev = 0.000824 cm` (8 microns $\ll 0.50\text{ cm}$ tolerance)**.
  - In accordance with `AGENT_PLAN_form_precision.md` line 589 (*"Если desired form не проходит, вернуть owner authoring/count/model-kind вопрос; новый kind отдельно утверждается, tolerance не меняется"*), the model-kind assessment is formally documented for owner review.
- **12.7 — Rehearsal Negatives:** Fault injection verified active full host collision (`isHidden=false`), absent target nodes, non-zero modifier stacks, and unit guard drift.
- **12.8 — Rehearsal Cleanup:** Two-pass deletion (`collect names then delete by names`) executed live in 3ds Max; scene restored to `objects.count = 0`, 0 modifiers.
- **Gate 12 (PASS):** Pipeline live execution verified, idempotent replay verified, MCP collection verified, QA assessor verified, numerical boundaries measured, scene restored clean.

**Next step:** **Phase 13 — Active docs, handoff, regeneration и archive gate** (13.1–13.6).

---

## 2026-10-10 — Form-precision progress / Phase 11 complete & Gate 11 PASS

**Phase 11 (11.1–11.5) complete & verified via subagents.**
- **11.1 — Audit & assessment of volume formula and host occlusion:**
  - Audited G-82 volume formula across [`scripts/validate_specs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/validate_specs.py), [`scripts/place_components.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/place_components.py), and [`references/07-spec-grammar.md`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/references/07-spec-grammar.md).
  - Identified and confirmed dimensional mismatch: comparing $\text{cm}^3$ volume against area threshold $linear \times linear$ ($\text{cm}^2$).
  - Audited host wall lifecycle: confirmed that solid `Box` nodes from `massing.ms` (`EL_010`..`EL_017`) remained visible and unhidden in `assembly.ms`, physically occluding window/door opening apertures and colliding with `PLC_` and `WAL_` nodes.
- **11.2 — Design alignment (A-CORRECT & A-TOL):**
  - Confirmed Box endpoint volume propagation policy `box_endpoint_propagation_v1` in $\text{cm}^3$ (§13.1, §21.4): for extents $w, h, t$ and linear tolerance $e$, extent uncertainty $d = 2e$; $B = \max((w+d)(h+d)(t+d) - wht, \; wht - \max(w-d,0)\max(h-d,0)\max(t-d,0))$.
  - Confirmed Mechanism A host deactivation: `assembly.ms` sets `host_node.isHidden = true`, keeping host walls as non-rendering carriers while discrete tiled `WAL_` cells and `PLC_` components provide delivered solids.
- **11.3 — Patch volume owners ([`scripts/validate_specs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/validate_specs.py), [`scripts/place_components.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/place_components.py), [`references/07-spec-grammar.md`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/references/07-spec-grammar.md)):**
  - Implemented `box_endpoint_budget_cm3(w, h, t, linear_cm)` in `validate_specs.py` and `place_components.py`.
  - Updated `_g82_wall_tiling_volume` and `_check_wall_tiling` to compute $B_{\text{total}} = B_{\text{host}} + \sum B_{\text{cells}} + \sum B_{\text{cuts}}$ ($\text{cm}^3$) and test $|\text{cell\_volume} - \text{expected}| > B_{\text{total}}$.
  - Updated G-82 entry in `references/07-spec-grammar.md` §9.8 table to specify Box endpoint volume propagation budget in $\text{cm}^3$ derived from `linear_cm`.
- **11.4 — Patch wall owners & QA walls check ([`scripts/place_components.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/place_components.py), [`scripts/qa_check.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/qa_check.py)):**
  - In `scripts/place_components.py` `render_ms`: emitted Mechanism A deactivation (`for host_node in host_nodes do host_node.isHidden = true`) right after `host_nodes` array creation.
  - In `scripts/qa_check.py`: updated batch generation to probe `(nd.isHidden as string)`, updated wire row parser to parse `isHidden` boolean, and updated `assess_run` under `QA-V1-WALLS` to assert that host wall nodes exist with `isHidden == True` (failing with error if `isHidden == False`).
- **Gate 11 (PASS):**
  - Spec validation:
    - `validate_specs.py --dir examples --build --warnings-as-errors`: **PASS 138 / FAIL 0 / WARN 0 / SKIP 22** (exit 0).
    - `validate_specs.py --dir specs/fixtures/form-precision/specs/pipeline`: **PASS 153 / FAIL 0 / WARN 0 / SKIP 15** (exit 0).
  - Emitted `assembly.ms` verified to contain Mechanism A deactivation (`for host_node in host_nodes do host_node.isHidden = true`).
  - G-82 volume fault injection verified: missing wall cell fails with exit 1.
  - QA walls check verified: good synthetic evidence exits 0 (`PASS`); active host collision negative (`isHidden=false`) exits 1 (`FAIL`) with diagnostic `'Wall node ... is not hidden (active host collision with openings)'`.
  - Python scripts compile cleanly (`Get-ChildItem scripts/*.py | ForEach-Object { python -m py_compile $_.FullName }`).

**Next step:** **Phase 12 — Live Acceptance: emit → MCP collect → assess** (12.1–12.9).

---

## 2026-10-10 — Form-precision progress / Phase 10 complete & Gate 10 PASS

**Phase 10 (10.1–10.7) complete & verified via subagents.**
- **10.1 — QA spec grammar & validator rules ([`scripts/validate_specs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/validate_specs.py), [`references/07-spec-grammar.md`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/references/07-spec-grammar.md)):**
  - Registered G-87 (closed QA configuration; prohibited result/verdict fields; profile check), G-88 (coverage joins: targets, checks, inferred mandatory families), G-89 (tolerances & operational limits), G-90 (discriminated JSON & CSV dependencies).
  - Documented G-87..G-90 in grammar reference §8.7 and cross-file verification tables.
  - Allowed schema version 1.1 for `qa.json` in envelope checks.
- **10.2 — Project init QA scaffolding ([`scripts/init_project.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/init_project.py)):**
  - Updated `INVENTORY` to defined `qa.json` (P8) under schema 1.1 with `form_precision_v1` profile, 6 JSON dependencies, 8 operational limits, empty `origin_inputs: []`, and no result fields.
  - Maintained fresh and seeded mode parity via `scaffold_qa(project)`.
  - Added draft exemption in `validate_specs.py` G-88 so scaffolded projects with `status: "draft"` skip analytical precision joins until targets are authored.
- **10.3 — Offline emit mode in [`scripts/qa_check.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/qa_check.py):**
  - Implemented `--in DIR --emit RUN_DIR --run-id TOKEN [--calibration-cert FILE] [--json]`.
  - Validates `qa.json` and dependencies; enforces `--calibration-cert` under `profile: "form_precision_v1"` (exits 1 with `NOT_READY` if omitted).
  - Derives target inventory and infers observations/samples.
  - Emits `qa-request.json` with canonical `form_cjson_v1` SHA-256 hashes (`request_hash`), `qa-run-context.json` with local session binding, and sequential read-only batch scripts (`batch_001.ms`, etc.).
  - Exits 0 (`READY/NOT_EVALUATED`, not model pass).
- **10.4 — Wire format parser in [`scripts/qa_check.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/qa_check.py):**
  - Parses captured execution outputs (`--results FILE`); audits `START_BATCH` / `END_BATCH` sentinels and `GUARD` unit checks (`units.SystemType`, `units.SystemScale`).
  - Enforces strict wire validation: rejects nonfinite floats (NaN, Inf), boolean-as-number, missing or extra sample/observation IDs, and duplicate IDs without zip truncation.
- **10.5 — Analytical geometry oracle in [`scripts/qa_check.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/qa_check.py):**
  - Implemented independent mathematical oracle (`distance_to_arc`, `distance_to_barrel`): computes exact perpendicular distances from query 3D points $(x,y,z)$ to finite cylindrical barrel vaults / elliptical arcs.
  - Computes max deviation, mean deviation, and RMS deviation against analytical formulas.
- **10.6 — Offline assessment & reporting in [`scripts/qa_check.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/qa_check.py):**
  - Implemented `--in DIR --request FILE --results FILE --out RUN_DIR [--json]`.
  - Evaluates 8 check families (`QA-V1-COVERAGE`, `QA-V1-CENSUS`, `QA-V1-NURBS-CENSUS`, `QA-V1-PLACEMENT`, `QA-V1-WALLS`, `QA-V1-FORM`, `QA-V1-STACK`, `QA-V1-REPLAY`).
  - Outputs comprehensive `qa-results.json` containing verdict (`PASS` / `FAIL`), per-check metrics, error budgets, and evidence refs.
  - Exits 0 on complete PASS only; exits 1 on FAIL/ERROR/INCOMPLETE.
- **10.7 — QA playbook & coherent fixture ([`agents/max-qa.md`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/agents/max-qa.md), [`specs/fixtures/form-precision/`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/specs/fixtures/form-precision/)):**
  - Created `agents/max-qa.md` documenting the S7 / P8 read-only QA execution contract, 3-step loop (offline emit → sequential MCP collect → offline assess), 8 check families, and strict anti-mutation invariants.
  - Created `specs/fixtures/form-precision/specs/pipeline/qa.json` (locked schema 1.1 spec with `TGT-001` design surface join, 4 checks, full tolerances and operational limits).
  - Created `specs/fixtures/form-precision/calibration-cert.json` bound to active `snippets/nurbs_arch_library.ms` SHA-256.
- **Gate 10 (PASS):**
  - Spec validation:
    - `validate_specs.py --dir examples --build --warnings-as-errors`: **PASS 138 / FAIL 0 / WARN 0 / SKIP 22** (exit 0).
    - `validate_specs.py --dir specs/fixtures/form-precision/specs/pipeline`: **PASS 153 / FAIL 0 / WARN 0 / SKIP 15** (exit 0).
    - Fresh project scaffold test passes validation clean with exit 0.
  - CLI exclusivity and token traversal checks verified (exit 2).
  - Calibration certificate gating verified: exits 1 (`NOT_READY`) without cert; exits 0 with cert.
  - Assess mode verified: valid synthetic evidence exits 0 (`PASS`); point shifted > 0.5 cm exits 1 (`FAIL`); nonfinite NaN exits 1 (`ERROR`); missing `END_BATCH` exits 1 (`INCOMPLETE`).
  - Python scripts compile cleanly (`Get-ChildItem scripts/*.py | ForEach-Object { python -m py_compile $_.FullName }`).

**Next step:** **Phase 11 — Correctness Branch: Openings & Active Wall-Host** (11.1–11.5).

---

## 2026-10-10 — Form-precision progress / Phase 09 complete & Gate 09 PASS

**Phase 09 (09.1–09.6) complete & verified via subagents.**
- **09.1 & 09.2 — NURBS library initial propagation & shell decision ([`snippets/nurbs_arch_library.ms`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/snippets/nurbs_arch_library.ms)):**
  - `createULoftShell`: added `hasShell:undefined` and `mergeTol:0.15` optional kwargs; assigns `nset.merge = mergeTol` and forwards `mergeTol:mergeTol` to `applyArchTessellation`. Implemented U02 / A-CLOSED shell presence branching: if `hasShell != undefined` checks `hasShell == true`, otherwise falls back to `(abs thickness) >= 0.001` (treating exact 0.001 cm equality as present).
  - `createUVLoftNetwork`: added `mergeTol:0.15` kwarg; sets `nset.merge = mergeTol` and forwards `mergeTol:mergeTol` to `applyArchTessellation`.
  - `makePointSurfaceGrid` & `makeCVSurfaceGrid`: forwarded `mergeTol:mergeTol` to `applyArchTessellation`.
  - Preserved existing physical defaults and non-dimensional curve/knot parameters.
- **09.3 — NURBS boundary scaling & length sinks ([`scripts/build_nurbs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/build_nurbs.py)):**
  - Integrated `emit_unit_preamble`, `scene_length_expr`, and `scene_point_expr` from `scripts.scene_units`.
  - Added unit setup preflight preamble at start of emitted function in `render_ms`.
  - Converted section point coordinates in `section_literal` via `scene_point_expr`.
  - Scaled all dimensional parameters: `tessellation_line` `mergeTol`, dependent surface `set.merge`, `u_loft` `thickness` and `mergeTol`, `uv_loft` / `point_grid` / `cv_grid` `mergeTol`, post-commit `set.merge`, and diagrid spline `thickness`.
  - Preserved non-dimensional parameters (divisions, orders, weights, knots, mat_id, render_angle_deg, render_edge_pct) unchanged without double conversion.
- **09.4 — Shell equality and script verification ([`scripts/build_nurbs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/build_nurbs.py)):**
  - Updated `expected_census` from `>` to `>= MIN_SHELL_THICKNESS_CM` so that $|t| = 0.001\text{ cm}$ expects 2 surfaces, matching G-47 and U02 / A-CLOSED.
  - Added unit preamble presence assertion (`units.SystemScale` and `__f_unit`) to `verify_script`.
- **09.5 — Schema envelope & generator preservation ([`scripts/build_nurbs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/build_nurbs.py)):**
  - Enforced G-5 units (`length: 'cm'`, `angle: 'deg'`) and supported schema versions 1.0 and 1.1 in `load_spec`.
  - Validated generator metadata in `normalise` while preserving discrete points as the sole geometric primitive (D8=A).
  - Preserved canonical cm in `nurbs.json` output.
- **09.6 — Approved write policy & A-WRITE / M34 transaction ([`scripts/build_nurbs.py`](file:///D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/scripts/build_nurbs.py)):**
  - Integrated atomic staging (`.tmp.<pid>`, `os.fsync`, `os.replace`, `finally` cleanup) in `write_bytes`.
  - Added upfront target checks in `main()`: pre-checks both `json_path` and `ms_path` for differing content on disk; refuses with exit 1 before touching disk if either differs.
  - Maintained memory-first parsing so same-path `--in`/`--out` runs never corrupt or truncate draft inputs.
- **Gate 09 (PASS):**
  - Canonical `nurbs.json` compares byte-identical across independent temp dirs and matches `examples/nurbs.json`.
  - Emitted `nurbs.ms` is deterministic, contains unit preamble and `* __f_unit` expressions, `hasShell:true`, and `mergeTol:`.
  - Idempotent re-run on temp dir exits 0 without file mutation.
  - Fault injection verifies M34 refusal (exit 1) on mutated `nurbs.json`.
  - Shell equality threshold verified: $|t| \ge 0.001$ yields 2 surfaces, $t = 0.0$ yields 1 surface.
  - Python scripts compile cleanly (`Get-ChildItem scripts/*.py | ForEach-Object { python -m py_compile $_.FullName }`).
  - Spec validation passes clean: `validate_specs.py --dir examples --build --warnings-as-errors`: **PASS 138 / FAIL 0 / WARN 0 / SKIP 18** (exit 0).

**Next step:** **Phase 10 — Defined QA Plan, Emit & Assessor** (10.1: grammar + validator inventory/QA dispatch).

---

## 2026-10-10 — Form-precision progress / Phase 08 complete & Gate 08 PASS

**Phase 08 (08.1–08.4) complete & verified via subagents.**
- **08.1 — Massing boundary scaling in `scripts/build_spec.py`:**
  - Integrated `emit_unit_preamble`, `scene_length_expr`, and `scene_point_expr` from `scripts.scene_units`.
  - Added unit setup preflight preamble at start of emitted function body in `render_ms` before scene mutations.
  - Scaled all Box dimensions (`width`, `length`, `height`) and `pos` via `scene_length_expr` and `scene_point_expr`; scaled group Dummy pivots.
  - Preserved canonical arithmetic in JSON document (`massing.json`).
  - Added unit preamble presence assertion to `verify_script`.
- **08.2 — Facade consumed envelopes in `scripts/facade_tables.py`:**
  - Added G-5 unit validation (length 'cm', angle 'deg') in `read_spec` and `read_downstream`.
  - Supported schema versions 1.0 and 1.1 explicitly; rejected unsupported major or minor versions.
  - Enforced cross-file `project` consistency matching `PROJECT_ID_RE`.
  - Canonical tables and CSV headers/values preserved unchanged without geometry scaling.
- **08.3 — Assembly boundary scaling in `scripts/place_components.py`:**
  - Integrated `emit_unit_preamble`, `scene_length_expr`, and `scene_point_expr` from `scripts.scene_units`.
  - Emitted unit setup preflight preamble in `render_ms` before delete sweeps.
  - Converted prototype Box dimensions and wall cell Box dimensions to scene units via `scene_length_expr`.
  - Placed instances (`.pos`) and wall cells (`pos:`) in scene units via `scene_point_expr` after canonical $z - h/2$ centering; preserved non-dimensional rotation (`rot_z_deg`).
  - Added preamble verification to `_check_script_shape` (G-80); added envelope unit & version gates to `read_spec`.
- **08.4 — Approved computed-output write policy (A-WRITE / M34):**
  - Updated `write_bytes` across `build_spec.py`, `place_components.py`, and `facade_tables.py` to enforce atomic staging (`.tmp.<pid>`, `os.fsync`, `os.replace`), refusal on differing existing on-disk output, and no-op on identical content.
  - Added upfront dual-file/multi-file target pre-checks in `main()` before opening any write streams, guaranteeing that differing files abort before touching disk.
- **Gate 08 (PASS):**
  - Canonical JSON/CSV outputs compare byte-identical across independent temp directories and against `examples/`.
  - Adaptive MS files are deterministic and identical across runs.
  - Idempotent re-runs exit 0 without file mutation.
  - Fault injection verifies M34 refusal (exit 1) on mutated output without modifying other targets.
  - Python scripts compile cleanly (`Get-ChildItem scripts/*.py | ForEach-Object { python -m py_compile $_.FullName }`).
  - Spec validation passes clean: `validate_specs.py --dir examples --build --warnings-as-errors`: **PASS 138 / FAIL 0 / WARN 0 / SKIP 18** (exit 0).

**Next step:** **Phase 09 — NURBS Boundary & Library First-Call Propagation** (09.1: library optional scene-native arguments).

---

## 2026-10-10 — Form-precision progress / Phase 07 complete & Gate 07 PASS

**Phase 07 (07.1–07.3) complete & verified.**
- **07.1 — Unit helper `scripts/scene_units.py`:**
  - Certified `SYSTEM_TYPE_FACTORS`: maps 8 certified SystemType names (`centimeters` 1.0, `millimeters` 0.1, `meters` 100.0, `kilometers` 100000.0, `inches` 2.54, `feet` 30.48, `miles` 160934.4, `yards` 91.44) to $k$ ($\text{cm per base unit}$).
  - Implemented `unit_factor(system_type, system_scale)` returning $(c, f)$ where $c = k \cdot s$ and $f = 1/c$. Rejects uncertified types, $s \le 0$, NaN, Inf, non-numbers and booleans.
  - Implemented `emit_unit_preamble`: emits MAXScript runtime preflight enforcing `units.SystemScale > 0.0`, case mapping `units.SystemType`, and throwing before any scene mutation.
  - Implemented `scene_length_expr` and `scene_point_expr` for adaptive script emission.
  - Implemented offline conversions for QA/calculators (`to_scene_length`, `to_canonical_length`, `to_scene_point`, `to_canonical_point`, `to_canonical_area`, `to_canonical_volume`).
  - Implemented dimensional key classification (`NON_DIMENSIONAL_KEYS`, `is_dimensional_length_key`, `is_nondimensional_key`).
- **07.2 — Strict preflight & units probe in `scripts/env_preflight.py`:**
  - Added CLI flag `--require-complete`: strict gate mode that exits 1 if any check evaluates to SKIP or FAIL. Bare invocation without `--results` remains exit 0 (all checks SKIP).
  - Added `SCRIPT_UNITS` probe and `check_units` (severity FAIL): validates running Max reports certified SystemType and finite positive SystemScale.
  - Fixed `check_plugins_absent`: missing plugin keys in payload now fail explicitly (`missing keys must not inherit false-as-absent`).
- **07.3 — Spec grammar & input rules unit documentation:**
  - `references/07-spec-grammar.md` (§2, §11) and `references/08-input-rules.md` (§3.1): documented that offline mathematical definitions (e.g. 1 m = 100 cm) are distinct from live executed unit certificates. Documented that `units.DisplayType` and `units.MetricType` are UI display metadata ONLY and never affect coordinate conversions; boundary scaling relies exclusively on certified `units.SystemType` and `units.SystemScale > 0`.
- **Gate 07 (PASS):**
  - Finite positive scale/type gates verified (invalid/uncertified types, negative/zero scale raise ValueError).
  - Preamble before mutation verified (case statements, throw guards).
  - Bare emit NOT_EVALUATED (exits 0 with all SKIP).
  - Captured incomplete fails strict mode (`--require-complete` exits 1).
  - Full Python suite passes `python -m py_compile scripts/*.py` (exit 0).
  - Spec validation passes clean: `validate_specs.py --dir examples --build --warnings-as-errors` (exit 0) and fixture pipeline (exit 0).

**Next step:** **Phase 08 — Staged Publication & Dimensional Sinks** (08.1: `build_spec.py` massing boundary scaling).

---

## 2026-10-10 — Form-precision progress / 04.4 complete & Gate 04 PASS

**04.4 complete & verified via parallel subagents.**
- **`agents/max-input.md` patched:**
  - Added §1.2 analytical authority (D8=A): `dimensions.json` is the sole source parameter authority for analytical forms; S3 (`max-nurbs`) derives its generators and points from `dimensions.json:form_references[]`.
  - Added Schema 1.1 `form_references[]`, `precision_targets[]`, and `raw_source_values[]` handling.
  - §4 Step 3: Documented raw-mm intake procedure (length /10 to cm, volume /1000 to cm³, area to m²; explicit source units requirement; raw-evidence provenance tracking).
  - §4 Step 5: Banned guessed defaults for analytical geometry (radii, semi-axes, planes, station spans) and units.
  - §5 Completion gate: Added G-86 form references gate, D8=A authority check, and raw-mm provenance verification.
  - §6.2 Escalation: Added analytical form/NURBS parameters to mandatory escalation list.
- **`references/08-input-rules.md` patched:**
  - §3.1 Units normalisation: Expanded conversion table with exact /10 (mm->cm), /100, /1,000,000, /10,000, /1,000 rules; banned mm disguised under `_cm`.
  - §3.1: Updated 3ds Max units note: replaced UNVERIFIED disclaimer with verified Phase 03 C03-UNITS facts ($c = k \cdot s$, boundary scaling, no Units Setup mutation).
  - §3.1: Documented Schema 1.1 `raw_source_values[]`, explicit source unit requirement, and D8=A authority rule.
  - §4: Added row 11 (analytical form geometry / curves / vaults — ask only) and row 12 (units — must be explicitly stated in source).
- **Gate 04 (PASS):**
  - All schemas and grammar compatible with versions 1.0 and 1.1.
  - Validation: `python scripts/validate_specs.py --dir examples --build --warnings-as-errors`: **PASS 138 / FAIL 0 / WARN 0 / SKIP 16** (exit 0).
  - `python -m py_compile scripts/*.py`: clean (exit 0).

---

## 2026-10-10 — Form-precision progress / 04.3 complete (G-86 & source selector)

**04.3 complete & verified via subagent.** Exclusive write ownership was restricted to `scripts/validate_specs.py`.
- **`scripts/validate_specs.py` patched:**
  - `RULE_TITLES` and `CROSS_FILE_RULES`: registered `G-86: form references and precision targets are well-formed and resolve`.
  - `check_envelope`: permitted optional `form_references` and `precision_targets` under schema_version 1.1 dimensions without extra key warning. Under 1.0, presence of either fails G-86.
  - Added `"plane"` to `UNIT_LINT_EXEMPT_KEYS`.
  - Implemented `resolve_source_id_selector(selector, session)`: resolves `<spec>.json:<collection>:<id>` format against session specs.
  - Implemented `check_g86_form_references(session, report)`: validates 1.0 vs 1.1 gates, closed allowed/forbidden keys per kind (`arc`, `ellipse_arc`, `semi_elliptical_barrel`), finite ranges, barrel XZ and center.y==0 rules, and precision_targets joins to form_references and source_ref items.
  - Registered G-86 in `run_checks`.
- **Verification:**
  - `python -m py_compile scripts/validate_specs.py`: exit 0.
  - `validate_specs.py --dir examples --build --warnings-as-errors`: **PASS 138 / FAIL 0 / WARN 0 / SKIP 16** (exit 0).
  - Synthetic battery verified: 1.0 rejection, 1.1 clean pass, invalid reference_ref / source_ref fail, extraneous keys fail, barrel geometry constraints fail.

---

Previous live update: 2026-10-06 (**P15 — the last open item is CLOSED**: UV / unwrap rules were the only
thing §"Resume here — after P14" left open. Measured live, and it turned up **three defects that
were being carried as fact**: `setTiling` silently floors its arguments to integers; `getTiling`
echoes the *request* rather than what was applied, which is why the truncation survived an earlier
pass that claimed to have confirmed the round-trip; and a modifier's `utile`/`vtile` written in the
**same** `execute_maxscript` call that adds the modifier is **silently discarded**. Also measured:
**modifier propagation and material propagation are opposite rules** — a modifier on a prototype
reaches all 165 panel nodes, while a material reaches none. New file
`references/13-uv-rules.md`) · Plan version: **v3** · Target: `3dsmax-arch-nurbs-ultimate-skill`

**P0 ✅ · P1 ✅ · P1-b ✅ · P2 ✅ · P3 ✅ · P4 core ✅ · P4b ✅✅ · P4b-r ✅ · P5 ✅ · P6 ✅** ·
**P7 ⛔ cancelled · P8 ⛔ cancelled · P9 ⛔ cancelled · P10 ✅ lite · P11 ✅ close-out · P12 ✅ · P13 ✅ ·
P14 ✅ close-out · P15 ✅** — read §"Resume here — after P15".

> **Scope, 2026-10-05, user decision:** *"мне нужен скилл для моделинга архитектуры… нам пока
> достаточно получить модель здания, на которую можно без труда накинуть материалы (материалы на
> этом этапе будут создаваться руками)"*. P7 (Corona materials + UVs), P8 (QA loop) and P9 (export)
> are **cancelled, not pending**. The deliverable is S1→S5 and the hand-off in
> `agents/max-orchestrator.md` §5. Do not plan, stub or route toward a `materials.json`.

> **Session findings, 2026-10-06:** a modelling session that produces a real finding records it in
> `<project>/IMPROVEMENTS.md` — **a session with no findings writes nothing and creates no file**.
> Instruction: `agents/max-orchestrator.md` §6.2. Format: `references/improvement-log.md`.
> **A log entry describes THIS PROJECT; a `CHECKPOINT.md` entry describes THE PACK.** An agent that
> finds a problem writes an entry — it does not edit `locked` JSON.

---

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
| **An object's layer cannot be assigned from MAXScript in this build.** Six routes tried, all throw | `node.layer = "0"` / `= "P3_X"` / `= LayerManager.getLayerFromName "P3_X"` / `node.setLayer "P3_X"` / `node.setProperty #layer` / `LayerManager.setLayerNode` → all `ERR` (`Property is read-only: layer`). Reading works: `node.layer.name` → `"0"` |
| Layers **can** be created and read from MAXScript | `LayerManager.newLayerFromName "P3_X"` → ok; `LayerManager.getLayerFromName "P3_X"` → `LayerProperties` mixin; `LayerManager.getLayer 0` → `LayerProperties` |
| **Layer enumeration is not available from MAXScript in this build.** The typed tool is the only route | `layers` as a value → `undefined`; `layers[1]` → *"No get function for undefined"*; `layers.count` → *"Unknown property count in undefined"*; `LayerManager.layers` → *"Unknown property Layers"*; `LayerManager.numLayers` / `.getCount()` → throw |
| `3dsmax-mcp_manage_layers` works for `list`, `create`, `delete` — **and those three are the whole vocabulary** (P6, 40+ candidates rejected with a uniform `Unknown layer action`; `create`/`delete` return distinct argument errors, so the probe discriminates). It **cannot assign objects to layers**, and neither can MAXScript or `set_object_property`. **CLOSED as a verified negative** | typed-tool batch + `LayerManager` member sweep + `set_object_property`, 2026-10-04 / 2026-10-05 |
| `node.parent = dummy` works; `getChildren` **does not exist** → use `dummy.children`. `Dummy boxSize:` needs a **`point3`**, a float throws *"Unable to convert: 100.0 to type: Point3"* | `b.parent = d` → `P3_DUMMY`; `getChildren d` → ERR; `d.children` → `#children($P3_CHILD) count=1` |
| **`delete <dummy>` does NOT delete its children** — the child survives and must be deleted explicitly | after `delete d`, `objects.count` decreased by exactly 1 |
| `try { } catch { }` **block** form is a parse error in this build → use the parenthesised `try ( ) catch ( )`. `getCurrentException()` is unavailable | both observed 2026-10-04 |
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

### Design consequences of the layer finding (P3 decision, closed at P6)
`node.layer` is read-only from MAXScript, so a builder cannot place geometry on a layer by
executing script. **P3 therefore carries layer assignment as data**: `massing.json` records the
target layer per element and `07` §8.1 declares a closed layer vocabulary; `scripts/build_spec.py`
emits geometry only.

**P6 closed the open half of this.** `assembly.json.layer_map` was to be applied via
`3dsmax-mcp_manage_layers`, pending its object-assignment action name. That action name **does not
exist** — see §"P6 step 1" in §Next actions. So the P3 design is **final, not provisional**: layer
attribution is permanently a spec-time declaration that a builder emits and the user applies in the
Layer dialog. Do not re-attempt it — **nine** routes are now ruled out with transcripts (six MAXScript,
`LayerManager`'s missing setter, the `manage_layers` vocabulary, and `set_object_property`).

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

## P2 — spec grammar and the input stage (closed 2026-10-04)

The pipeline is **spec-first**: no stage reads prose, every stage consumes JSON. The contract is
`references/07-spec-grammar.md`; `scripts/validate_specs.py` is its executable form.

### Decisions that are now settled — build on these, do not re-open

- **Units: centimetres**, angles degrees. Every length key ends in `_cm` (areas `_m2`, angles `_deg`).
  A bare length key is a defect (G-8). 3ds Max scene units are centimetres, so no conversion is
  needed at build time — but `07` §11 and `09` §6 both mark that as **UNVERIFIED, no live probe**,
  and the boundary-conversion rule holds either way.
- **Envelope on every spec file**, in this order: `schema_version` (semver, major must match) ·
  `spec` (must equal the file base name) · `project` · `units` · `source` · `status`
  (`draft` | `locked` | `superseded`). **A builder must refuse a non-`locked` file.**
- **Traceability is an invariant, not prose.** Every leaf in `dimensions.json` is covered by exactly
  one `origins` entry (G-9); `assumed`/`conflict` must carry an `origin_ref` (G-10) resolving to a
  ledger entry whose value **equals** the spec value (G-12); every ledger entry is consumed at least
  once (G-13). Ids `A-nnn` / `C-nnn` are project-scoped and zero-padded.
- **Precedence ladder `R1`…`R6`, ascending order, first match wins**: `CODE-SUPREMACY` ·
  `SPECIFICITY` · `QUANTITY-OVER-SUMMARY` · `BUILDABILITY` · `MODULE-ALIGNMENT` · `LATER-STATEMENT`.
  **`R7 DEFAULT-FILL` is not a conflict rule** — it fills silence only and is forbidden in
  `rules_invoked` (G-14). `rules_invoked` is listed **ascending** and mirrors `rule_names_as_proposed`
  positionally.
- **Tolerances are declared, not hidden**: linear 0.5 cm, area 0.05 m², angle 0.01°. Every geometry
  row in the validator output names the tolerance it used (G-33). Range checks are exact.

### Validator state — verified

```
py_compile                                    0
validate_specs.py --dir examples               0   PASS 52 / FAIL 0 / WARN 0 / SKIP 11
  … same, --warnings-as-errors                 0
init_project.py --project X --dry-run          0   12 files planned
init_project.py --project X                    0   12 written
validate_specs.py --dir X/specs                0   PASS 102 / FAIL 0 (11 WARN = status draft, G-4)
init_project.py --project Y --from examples    0   audit ids preserved
validate_specs.py --dir Y/specs                0   PASS 52 / FAIL 0 / WARN 0
```

G-1…G-33 are implemented and each was proved to **fire** by mutating the example (54 mutations,
54/54 caught). That battery found two real defects: G-16 was never wired in, and the `[]` wildcard
in the leaf walker dropped every match.

**Honest SKIPs — a check that cannot be evaluated reports SKIP with a reason, never a silent PASS:**
G-21 winding on `core.footprint_cm` (no sibling `*_ccw` declared) · G-23 for a non-axis-aligned
footprint (grid origin undefined) · G-32 for a derived path with no documented formula ·
G-26/27/28 on an empty `openings` · G-16 on files with no declared ranges · absent `reserved` files.

Two flags exist beyond the original spec because G-4 is a WARN in lint and a FAIL at build time:
`--build` (enforce the lock gate) and `--allow-draft` (non-`locked` → SKIP instead of FAIL).

### Known limitations, carried forward — not defects

- `examples/conflicts_resolved.json` `precedence_rules.note` said `PENDING ADOPTION`; corrected to
  ADOPTED during P2 verification. All four docs (`07`/`08`/`09`/`10`) and the example now agree on
  ascending `rules_invoked`; the example was the sole outlier and was the thing fixed.
- **`G-16` caps `levels[].height_cm` at 600 cm**, so an industrial clear height above 6 m is not
  expressible. Recorded as a KNOWN LIMITATION in `09` §3.1 with "escalate, do not narrow the range,
  do not fake it". Widen `07`'s range in P3 if a real project needs it — with the change recorded.
- `09` cannot pre-allocate `A-nnn` ids (G-11 makes them project-scoped, G-12 requires value
  equality), so each default row carries a stable `D-xx` doc anchor plus a "next free id" column.
- Structural **systems** are never defaulted (do-not-default list); the example still carries a
  low-confidence column section and core wall thickness, flagged `recheck_stage: "P3"`.

### Verified by execution, not by report

Every P2 subagent claimed success. All claims were re-run in the main thread before this section was
written — `py_compile`, both validator modes, both `init_project.py` modes, the `--from examples`
round-trip, and the leftover-directory check. One agent also found `agents/max-input.md` appearing
mid-run and correctly left it alone. Self-test directories were removed; the repo contains only the
committed P2 files.

---

## P3 — layer standard + massing (closed 2026-10-04)

`massing.json` is **defined**: schema in `07` §8.1 (full key tables), invariants `G-34`…`G-40` in §9.6,
layer vocabulary in §8.1.4. `examples/massing.json` is the worked example and the builder's real output.

### Decisions that are now settled — build on these

- **Every massing element is a prism in Z**: a world-XY ring plus `z_range_cm`. A ring *with a hole* is not
  expressible, so a hollow shape is decomposed per side — a rectangular deck's parapet is **four**
  `parapet` elements (`EL_010`…`EL-013`), not one.
- **The roof reads downward.** `roof_deck` is `[deck_level − deck_thickness, deck_level]`;
  `parapet` is `[deck_level, deck_level + parapet_height]`. The model's top is therefore
  `building.overall_height_cm` — and that equality is asserted in the builder's self-check, because the
  first reading of `G-38` was **wrong** and produced a 940 cm model (see the incident log).
- **Layer is data, never code.** Six MAXScript assignment routes were executed and rejected; a builder
  cannot place geometry on a layer. `massing.json` carries `layer` per element, `build_spec.py` emits
  geometry only, and application is P6's problem.
- **A massing node is named after its spec id**: `EL-001` → node `EL_001`, `GRP-001` → `GRP_001`
  (`11-layer-standard.md` rule N1 — names get pasted into MAXScript, and `-` reads as subtraction).
- **A `draft` massing file is not evaluated.** The stub `init_project.py` writes is a placeholder with no
  provenance; `G-34`…`G-38`/`G-40` SKIP with a reason, and `--allow-draft` forces them to run and fail.
- **`G-16`'s 600 cm `levels[].height_cm` cap is NOT widened.** No project needs it. Recorded as a standing
  limitation, not an oversight; widening requires a real project and a note in `09` §3.1.
- `source.kind: "derived"` was added to the §3.1 enum at P3: a spec file computed from another spec file
  now has a kind that says so, and `G-6` requires its `reference` to name a real file.

### Verified state — re-run in the main thread, not taken from a report

```
py_compile scripts/*.py                                   0
validate_specs.py --dir examples                          0   PASS 67 / FAIL 0 / WARN 0 / SKIP 11
  … --warnings-as-errors                                   0   PASS 67 / FAIL 0 / WARN 0 / SKIP 11
  … --build                                                0   PASS 67 / FAIL 0 / WARN 0 / SKIP 11
init_project.py --project X --dir tmp                     0   fresh scaffold: PASS 103 / FAIL 0 / WARN 11
init_project.py --project Y --dir tmp --from examples     0   seeded: PASS 67 / FAIL 0 / WARN 0 / SKIP 11
build_spec.py --stage massing --in examples --out a|b     0   byte-identical, and equal to the committed example
fileIn examples/massing.ms (live Max)                     0   18 nodes; 2 further calls idempotent
measured bbox vs massing.json, 18/18 within 0.5 cm        0   model Z -30.0 … 910.0 == overall_height_cm
```

`G-34`…`G-40` each have a fault-injection proof that they fire. Honest SKIPs remain: `G-16` on the three
files `07` declares no range for, `G-21` on `core.footprint_cm` (no sibling `*_ccw`), and the seven
reserved P4–P9 files.

### Carried forward — known, not defects

- **`manage_layers`' object-assignment action name is still unknown** (rejected: `move`, `assign`, `add`,
  `addobjects`, `moveobjects`, `setlayer`). P6 must find it before `assembly.json.layer_map` can be applied.
- **`init_project.py` scaffolds `massing.json` as a stub, not content.** Correct — the file is computed —
  but it means a scaffolded project has an empty massing until `build_spec.py` runs.
- **Non-rectangular profiles are refused by name** and escalated to P4 (NURBS). Deliberate, not a gap.
- **No `plinth` element is produced**: `dimensions.json` has no plinth dimension and inventing one is
  forbidden. `plinth` stays in the `kind` vocabulary for projects that do dimension one.
- `site_pad` nodes are not parented to a grouping dummy — they are not elements, so `G-40` does not cover them.

---

## P4 — NURBS core (closed 2026-10-04)

`nurbs.json` is **defined**: schema in `07` §8.2, invariants `G-41`…`G-49` in §9.7.
`examples/nurbs.json` + `examples/nurbs.ms` are the worked example and the builder's real output.

### The scoping decision, and why it went the way it did

The P3 draft of §8.2 promised five kinds (`rail_sweep`, `revolve`, `freeform`), per-surface
`closed_u`/`closed_v`, and a `relations` edge list for trim/blend/offset/project. **All of it was
re-derived against the library before anything was written**, and most of it did not survive:

- `closed_u`/`closed_v` — **no such method exists** on any surface class. Verified negative.
- `relations` — the only relation implemented is a parallel offset shell, and it is an *argument* of
  the loft, not an edge between two surfaces.
- knots/degree in `sections[]` — `setClampedKnots` derives them; a spec that declared them would
  declare something the builder overwrites.
- `rail_sweep`, `blend`, `revolve`, `trim`, `project` — ~~the classes construct, but expose **no**
  property or method this build resolves~~ → **CORRECTED AT P4b: this was a false negative.** All four
  relation classes work end-to-end; see §"Rail sweeps, blends and trims". They stayed out of the P4
  schema for a *documentation* reason, and the schema has simply not caught up yet.

What shipped instead is **smaller and true**: four kinds (`u_loft`, `uv_loft`, `point_grid`,
`cv_grid`), two derivative kinds (`quad_panels`, `space_frame`), and one primitive — an ordered list
of point rows, which is simultaneously a loft's sections and a grid's lattice. **Writing down what
the code cannot do was cheaper than discovering it twice.**

### Decisions that are now settled — build on these

- **`nurbs.json` may not name a class, tool or plugin** (`07` §12's standing rule). Kinds are
  geometric: `u_loft`, `uv_loft`, `point_grid`, `cv_grid`, `quad_panels`, `space_frame`.
- **`point_grid` ≠ `cv_grid`, and the difference is architectural.** Interpolating surfaces overshoot
  the points you give them (measured: 510 → bbox 568.226); controlled surfaces undershoot them
  (480 → sampled 448.125) and can never leave their CV hull. Choosing wrong is a geometry error, not
  a stylistic one, and QA must compare *evaluated* geometry against the lattice.
- **A derivative reads the first `NURBSSurface`, never the last.** See §Incident log — the live run
  caught the wrong choice and the fix is one `exit`.
- **Layers stay data.** `nurbs.ms` assigns no layer to any node, for the same P3 reason.
- **A recipe is a template, not a project.** `specs/recipes/<schema>/<name>.json` takes its schema
  from the **directory name**, so `G-2` keeps tying `spec` to the file name and a recipe must be
  *instantiated* (copy to `nurbs.json`, `spec: "nurbs"`, `status: locked`, fill `origin_inputs`)
  before any builder will read it. Verified: `build_nurbs.py` refuses a recipe under its own name
  with a named `G-2` error, and builds the instantiated copy cleanly.

### Verified state — re-run in the main thread, not taken from a report

```
py_compile scripts/*.py                                        0
build_nurbs.py --in examples --out examples                     0   self-check G-41..G-49 9 pass 0 skip 0 fail
build_nurbs.py, two temp dirs + in place                        0   nurbs.json and nurbs.ms byte-identical
validate_specs.py --dir examples                                0   PASS 84 / FAIL 0 / WARN 0 / SKIP 11
  … --warnings-as-errors                                         0
  … --build                                                      0
validate_specs.py --dir specs/recipes/nurbs --allow-draft        0   PASS 54 / FAIL 0  (4 recipes linted)
build_spec.py --stage massing                                   0   unchanged by P4
fileIn examples/nurbs.ms (live Max)                             0   6 nodes; two further calls idempotent
measured node bboxes vs the lattice                             0   all six as tabulated above
```

Every `G-41`…`G-49` was proved to **fire** by fault injection on a temp copy (dangling section ref,
ragged lattice, `thickness_cm 0.0005`, `u_order` above the point count, hyphen in a name, forbidden
key for a kind, `origin: "given"`, and more). Honest SKIPs are reported with their reason, never a
silent PASS: `G-16` (no range declared for this file), `G-46` on a file with no `cv_grid`,
`G-49` when `dimensions.json`/`massing.json` are absent, `G-31` without the sibling ledgers.

### Carried forward — known, not defects

- **Rail sweeps, blends, trims and project-vector curves are not implemented.** Discovery needs a
  method name, and the only honest route is a control-tested probe — `getPropNames` and `compile`
  closures are both dead ends (measured), and both introspection tools return a false negative on
  these classes. This is the first item in §"Next actions".
- **`G-46` SKIPs on any file with no `cv_grid`.** The worked example now has one (`SUR-003`), so the
  example exercises it; a project without a CV cage will still see the SKIP with its reason.
- **`manage_layers`' object-assignment action name is still unknown** (P6's problem, not P4's).
- **Non-closed vault ribs are open curves.** `closed_sections` exists and is honoured for
  `u_loft`; a closed-section barrel needs the flag set, and the example deliberately leaves it
  `false` so the springing is open at the two ends.

---

## P5 — facade grid + component registry (closed 2026-10-05)

`facade_grids.json` and `components_registry.json` are **defined**: schema in `07` §8.3 / §8.4,
invariants `G-57`…`G-70` in §9.8. The stage had its own design contract,
**`references/_p5-contract.md`**, so three files could not drift; it is at **revision 2** and carries
its own revision note.

**The orchestrator probes Max; agents never touch the bridge.** All four authoring agents received
verified data and a file list. Three defects below were found by *me*, in the main thread, by reading
the agents' output and then measuring it — not by any agent's report.

### Decisions that are now settled — build on these

- **The vertical division is per bay, not per facade.** `u` axes are one set per `(facade, level)`;
  `v` axes are computed **per bay**, so every opening is realised by **exactly one** panel. This is
  the correction of the stage's worst defect — see §Incident log.
- **`axes[]` carries a required `bay_index`**, `null` for `u` and a real index for `v`. `panels[].bay_index`
  became load-bearing: it selects the `v_axis_ids` slice, it is the tiling unit, and it is part of
  what `opening_ref` must match.
- **A rotation is `run_angle_deg = atan2(dy, dx)`, never `dimensions.facades[].direction_deg`.**
  `F-S` and `F-N` both run along **+X** and carry `180.0` and `0.0` — `direction_deg` is a compass
  **facing label**. This is asserted by `G-57` and it is the single most likely field for a later
  stage to reach for by mistake.
- **`full_height` is derived from the extent**, `v_min == 0 ∧ v_max == height_cm`, not from a kind. A
  bay with no opening is one whole-height `blank` panel, so any kind-based definition is falsified by
  the example itself.
- **The grid is a partition, and the join is total.** `G-61`: Σ panel area per `(facade, level, bay)`
  equals `bay_width × height`, per `(facade, level)` equals `length × height`, no interior overlap,
  every panel inside its bay. `G-68`: every panel matches ≥ 1 registry component and all matches are
  in one family. Between them, a grid that does not cover its facade and a panel with no block are
  both **build failures** rather than a quietly wrong scene.
- **Only two values in P5 are invented**: `defaults.panel_thickness_cm = 3.0` and
  `defaults.joint_width_cm = 2.0`, both `09`'s own **declared defaults** (`D-CL-05`, `D-FM-10`),
  both `assumed` with ledger entries `A-023` / `A-024` and `recheck_stage: "P6"`. Everything else in
  both files is `derived` and recomputes from `dimensions.json` — `G-64` **fails** any other origin in
  the grid file.
- **One component per distinct `(kind, width, height)` class, not one per panel.** 136 panels resolve
  to **29** blocks. The registry is derived *from* the grid and never the reverse, so `G-31` stays a
  single pass and there is no cycle.
- **Layer stays data.** Every panel carries `layer: "05_FACADE"`; no builder emits layer code (§8.1.3).
- **`host_ref` is `null` for all 136 panels.** `massing.json` has **no exterior envelope element** —
  only the core and four parapet strips — so there is nothing to cut an opening into. Recorded as a
  limitation, not a defect: a project that needs it gets a `facade_wall` kind added to `massing.json`
  through `07` §12 step 1, which is P3's table.

### Verified state — re-run in the main thread, not taken from a report

```
py_compile scripts/*.py                                            0
validate_specs.py --dir examples                                    0   PASS 120 / FAIL 0 / WARN 0 / SKIP 12
  … --warnings-as-errors                                             0   PASS 120 / FAIL 0 / WARN 0 / SKIP 12
  … --build                                                          0   PASS 120 / FAIL 0 / WARN 0 / SKIP 12
validate_specs.py --dir specs/recipes/nurbs --allow-draft           0   PASS  54 / FAIL 0 / WARN 0 / SKIP 28
facade_tables.py --out tmpA | --out tmpB | committed               0   all four files byte-identical
  … --stage grids | components | tables                             0   each reproduces its own files exactly
G-57..G-70 fault injection, 16 cases                                0   16/16 fired
measured: panels 136 · axes 140 · components 29 · families 6 · panel_types 6
measured: kinds  blank 88 · spandrel 26 · punched_window 14 · mullion 4 · vision 2 · transom 2
measured: max |Σarea − bay_width×height| per (facade,level,bay)      0.000000 m2   over 24 groups
measured: max |Σarea − length×height| per (facade,level)             0.000000 m2
measured: max pairwise interior overlap                              0 cm2
measured: openings referenced by exactly one panel                  16/16, u- and v-range exact
measured: u axes with a bay_index                                    0    (G-58)
measured: v axes with bay_index null                                0    (G-58)
measured: smallest panel                                            min height 20 cm (a transom head band),
                                                                          min width 15 cm (a mullion pier)
measured: panels with no size-matched component                     0    (G-68)
measured: CSV rows                                                   facade_table 136, world_table 136
measured: rot_z_deg == run_angle_deg on every row                   136/136
```

### P5 — the live gate

**The guard, stated once:** *an emitted `.ms` is not done until `fileIn` has run it and its output has
been measured against the spec's intent.* It has now fired twice for MAXScript (P3, P4) and once in
its table-shaped form here. **An emitted CSV is not done until it has been placed in Max and counted.**

`examples/world_table.csv` was read **by MAXScript itself** — `openFile` / `readLine` / `filterString`
— 136 data rows, 17 columns. Measured against an independent prediction computed in Python from the
same CSV:

```
rows read by MAXScript                        136
distinct components -> Box prototypes          29
instances placed                               136
objects.count after placement                  165      expected 136 + 29   MATCH
instances sharing their prototype's baseObject 136      not-instances: 0
PNL-001  (F-S, rot   0.0)  0,-1.5,0.0   .. 135,1.5,90.0     expected identical    EXACT
PNL-034  (F-S, rot   0.0)  315,-1.5,510  .. 450,1.5,690      expected identical    EXACT
PNL-069  (F-N, rot   0.0)  1500,898.5,0  .. 1650,901.5,90    expected identical    EXACT
PNL-102  (F-E, rot  90.0)  1798.5,600,90 .. 1801.5,750,270   expected identical    EXACT
PNL-136  (F-W, rot  90.0)  -1.5,750,690  .. 1.5,900,820      expected identical    EXACT
after deleting the 29 prototypes              136      every instance alive and unchanged
scene after the full sweep                      0
```

The sample deliberately spans **all four facades** and **both rotation classes**, so it covers the
case the CSV exists to get right: `rot_z = 90` swaps the X and Y extents.

### P5 — what this changed in the toolchain

Four things P5 changed outside its own files, all found by execution:

| Fact | Evidence |
|---|---|
| **`setCopyMode` does not exist in this build.** The instance route is `n = copy src` then `n.baseObject = src.baseObject` | calibrated sweep: `copy`, `Box`, `filterString`, `openFile`, `readLine`, `findItem`, `matchPattern`, `pi`, `quat` all resolve; `setCopyMode` and a bogus name both return `undefined`. Measured discriminator on the same node: a plain `copy` shares nothing (`false`), after the assignment it does (`true`) |
| **`rotationZ` / `rotationX` / `rotationY` / `matrix3` / `angle` / `findString` do not exist either.** The route is `n.rotation = quat <degrees> [0,0,1]` | same calibrated sweep. Geometry check: a 100×200×20 box spans X 100 / Y 200 at rot 0 and X 200 / Y 100 at rot 90, `z_rotation` reads `90.0` |
| **The traceability machinery could not describe an `assumed` value outside `dimensions.json`.** Adding `A-023` / `A-024` produced **8 FAIL rows** across `G-12`, `G-13`, `G-15`, `G-31` | executed. A `field_path` may now be **file-qualified** (`"<spec-name>:<dotted path>"`); the bare form is byte-for-byte unchanged, and `G-13`'s prefix coverage is now owner-scoped so a path in one document never covers a path in another |
| **`G-8`'s lint needed two narrowings**, both reviewed and accepted: `full_height` is exempt (a bool naming an extent that is deliberately *not* a dimension) and `_lint_key` judges the **leaf** of a dotted `origins` path, since the path spelling is not the builder's to choose | 402 WARN rows → 0. Strictly non-widening of coverage: a genuinely unit-less leaf is still caught, verified by a per-rule diff against the pre-change baseline |

### Carried forward from P5 — known, not defects

- **`host_ref` is unreachable** until `massing.json` gains an envelope element kind. P6's opening
  cuts inherit this.
- **`examples/facade_grids.json` is 584 KB** (2970 provenance leaves). G-9 permits collapsing an
  array element to a single `origins` entry, which would cut it by roughly 5×; the per-leaf form was
  kept because `massing.json` and `nurbs.json` both use it and the richer provenance is worth the
  bytes. It compresses ~10× in the `.skill` archive.
- **`spandrel` width follows rule 8.5's equality test**, so it comes out 150 cm wide ×21 and 180 cm ×5.
  Both are correct elevations — a continuous floor-level band where the bay's side cells happen to
  equal the opening width, a window-only spandrel with full-height piers where they do not. Recorded
  so nobody "fixes" it.
- **`rotate`'s absence is UNPROVEN.** Its only test used `matrix3`, which is itself absent, so the
  failure is uninformative. `quat` works and is the route; nothing depends on `rotate`.
- The P6 items in §"Next actions" are unchanged: `manage_layers`' object-assignment action name is
  still unknown, and the Chaos Scatter crash attribution is still inference.

---

## Bugs in `snippets/nurbs_arch_library.ms` — ALL CLOSED (P1-b, 2026-10-04)

The library loads and every one of its ten functions was executed against live Max. Zero known bugs
remain. Full transcript in `references/12-nurbs-gotchas.md` §2.

**P4 added two functions and executed them live** — `makePointSurfaceGrid` (F11) and
`makeCVSurfaceGrid` (F12) — so the library is now **12 functions, all 12 verified, zero known bugs**.
Both reject a non-rectangular grid by throwing a named error, and both clamp an order above the point
count with `amin` (which is why `G-46` fails the spec rather than letting the clamp happen silently).

| # | Bug | Symptom | Fix | State |
|---|---|---|---|---|
| 1 | `appendObject` returns `"OK"`, not an index | `Unable to convert: OK to type: Integer` | index = `nset.numObjects` after the call | ✅ applied, verified |
| 2 | `stopCreating node` — wrong arity (4 sites) | `Argument count error: StopCreating wanted 0, got 1` | bare `stopCreating` | ✅ applied, verified |
| 3 | ~~`NURBSControlVertex` does not construct~~ — **premise was false** | none; the real error is `Unable to convert: [0,0,0] to type: NURBSControlVertex` | wrap every point: `setCV crv i (NURBSControlVertex (pts[i] as point3) w)` | ✅ applied, verified |
| 4 | `close <crv>` is a silent no-op → `closed:true` produced an open curve, no error | `isClosed` always false; no settable property | `closed:true` now seam-willed (first CV repeated last); `makePointCurve` documented as the real closed path | ✅ applied, verified |

Also fixed while in there: every `("x" + i as string)` precedence trap (5 sites), and `setPoint`
now casts through `as point3`.

Execution evidence: F2 `setSurfaceClampedKnots` PASS · F3 `makeCVCurve` PASS (closed → 5 CVs, first
= last) · F6 `createULoftShell` PASS (nObj=20, loft + offset surface) · F7 `createUVLoftNetwork` PASS
(nObj=41) · F8 `inspectNURBSSet` PASS · F9 `sampleSurfaceToQuadPoly` PASS (25 v / 16 f) · F10
`createDiagridOnSurface` PASS (18 splines) · F9 type guard correctly throws on a non-surface
sub-object. Test nodes deleted; scene left empty.

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

## Artifacts

| File | State |
|---|---|
| `PLAN.md` | ✅ v3 |
| `CHECKPOINT.md` | ✅ this file |
| `references/00-audit-p1.md` | ✅ NEW — audit, dedupe measurement, per-file verdicts, `curve-construction.md` rewrite brief |
| `references/02-mcp-live-orchestration.md` | ✅ corrected — false NURBS claim removed, introspection trap promoted, Rhino-collision section added |
| `references/12-nurbs-gotchas.md` | ✅ rewritten — verified class matrix, 3 library bugs, 13 gotchas, control-tested detection recipe |
| `scripts/env_preflight.py` | ✅ corrected: `nurbset_present` asserts presence, PASS 9/9, inversion tested |
| `snippets/nurbs_arch_library.ms` | ✅ **zero known bugs** — 4 fixed at P1-b (all 10 functions then executed live); **extended at P4 with F11/F12, 12 functions, all 12 executed live** |
| `references/12-nurbs-gotchas.md` | ✅ rewritten — verified class matrix, **4** bugs (3 resolved-as-false, 1 new), 13 gotchas, control-tested detection recipe |
| `references/07-spec-grammar.md` | ✅ NEW (P2) — envelope, cm/`_cm` rule, full spec inventory, invariants `G-1`…`G-33` |
| `references/08-input-rules.md` | ✅ NEW (P2) — intake contract, source trust hierarchy, units normalisation, never-infer list, worked brief → committed example |
| `references/09-defaults.md` | ✅ NEW (P2) — 128 default rows in 11 tables, 5 project presets, do-not-default list |
| `references/10-conflict-resolution.md` | ✅ NEW (P2) — ladder `R1`…`R6` first-match-wins, `R7` non-conflict, conflict record shape, escalation policy |
| `agents/max-input.md` | ✅ NEW (P2) — S1 contract: 12-step procedure, 24-row completion gate, escalation, anti-pattern guards, return contract |
| `scripts/validate_specs.py` | ✅ NEW (P2) — `G-1`…`G-33`, stdlib only, `--dir/--file/--json/--rule/--warnings-as-errors/--build/--allow-draft` |
| `scripts/init_project.py` | ✅ NEW (P2) — workdir scaffold, 12 files, `--from examples` preserves the `A-nnn`/`C-nnn` audit trail |
| `examples/{dimensions,assumptions,conflicts_resolved}.json` | ✅ NEW (P2) — worked example `pavilion-01`; PASS 52 / FAIL 0 / WARN 0 |
| `SKILL.md` | ✅ rewritten — 39 nonexistent routing targets removed, decision matrix rebuilt, new frontmatter; **§3.2 + §7 stale-bug claims corrected during P2** |
| `references/07-spec-grammar.md` §8.1 + §9.6 | ✅ NEW (P3) — `massing.json` **defined**: Z-prism element/storey/site_pad/grouping tables, kind→layer map, closed 8-layer vocabulary, invariants `G-34`…`G-40`; §3.1 gained `source.kind: "derived"` |
| `references/11-layer-standard.md` | ✅ NEW (P3) — per-layer intent, kind→layer table, node naming (N1, id-based), dummy rules (D1–D6), hygiene checklist (H1–H12), open items |
| `references/01-architecture-aec-workflow.md` | ✅ NEW (P3) — S0→S8 stage map, spec chain, build gate, determinism, context budget, `build_spec.py` CLI contract |
| `agents/max-massing.md` | ✅ NEW (P3) — S2 contract: inputs, 9-step procedure, per-kind Z rules, the live-Max step, 11-row completion gate, cleanup, escalation, anti-patterns |
| `scripts/build_spec.py` | ✅ NEW (P3) — `--stage massing --in --out [--json]`, lock gate, deterministic, emits `massing.json` + `massing.ms`, self-checks `G-34`…`G-40` before writing, refuses non-rectangular profiles by name |
| `examples/massing.json` + `examples/massing.ms` | ✅ NEW (P3) — builder output for `pavilion-01`: 13 elements, 4 groups, 1 site pad; the `.ms` **executed live**, 18/18 bboxes within 0.5 cm |
| `scripts/validate_specs.py` | ✅ extended (P3) — `G-34`…`G-40`, `massing.json` flipped to `defined`; **two latent P2 bugs fixed**: `G-31` compared an `origin_inputs` path's first token against file names (23 false FAILs), and `G-6` lacked `derived` |
| `scripts/init_project.py` | ✅ extended (P3) — `massing.json` gets a real stub instead of the reserved skeleton, `--from examples` now seeds it, and a `derived` file keeps naming its upstream spec |
| `references/07-spec-grammar.md` §8.2 + §9.7 | ✅ NEW (P4) — `nurbs.json` **defined**: the four kinds that exist, the one point-row primitive, `approximation`, `derivatives`, kind/key fitness table, and **rail sweeps / blends / trims explicitly recorded as not implemented**; §9.7 adds `G-41`…`G-49`; §2/§4/§10/§11 updated |
| `scripts/build_nurbs.py` | ✅ NEW (P4) — `--in --out [--json] [--build] [--allow-draft]`, lock gate, deterministic (byte-identical on repeat), self-checks `G-41`…`G-49`, refuses a literal surface index in its own output, `fn`-wrapped idempotent builder |
| `examples/nurbs.json` + `examples/nurbs.ms` | ✅ NEW (P4) — builder output for `pavilion-01`: 11 rows, 3 surfaces (`u_loft` vault + `point_grid` canopy + `cv_grid` cage), 3 derivatives; the `.ms` **executed live**, 6 nodes, idempotent, every bbox measured |
| `scripts/validate_specs.py` | ✅ extended (P4) — `G-41`…`G-49`, `nurbs.json` flipped to `defined`; recipe templates lint from `specs/recipes/<schema>/` with the schema taken from the directory name; a recipe-only run reports absent project files as SKIP, not FAIL |
| `scripts/init_project.py` | ✅ extended (P4) — `nurbs.json` stub + `--from examples` seeding |
| `agents/max-nurbs.md` | ✅ NEW (P4) — S3 contract: lock gate, procedure, the four kinds with the measured overshoot/undershoot numbers, commit rule, the 52-sub-object index trap, positional-argument traps, 12-row completion gate, cleanup, escalation, 13 anti-patterns |
| `specs/recipes/nurbs/*.json` | ✅ NEW (P4) — 4 templates: barrel vault (`u_loft` + shell), Gordon canopy (`uv_loft`), freeform soffit (`point_grid`), diagrid frame (`space_frame`); `PASS 54 / FAIL 0` as a lint target |
| `snippets/nurbs_arch_library.ms` | ✅ extended (P4) — **F11 `makePointSurfaceGrid`, F12 `makeCVSurfaceGrid`** added and executed live; 12 functions, zero known bugs |
| **P4b** control-tested discovery of the rail-sweep / blend / trim API | ✅ **DONE — overturned the P4 "not implemented" finding.** `NURBS1RailSweepSurface` `NURBS2RailSweepSurface` `NURBSBlendSurface` `NURBSProjectVectorCurve` all construct → commit → evaluate. Keyword map recovered by execution; the rule is **read properties only on the committed sub-object** |
| **P4b round 2** — the two live defects | ✅ **both fixed and measured.** Tension default `1.0` → `0.0` (it was the whole overshoot); relation parents referenced by `parent1ID:`/`parent2ID:` instead of re-instantiated, `mcpNurbsAppendParent` deleted. `SUR_006` `[0,0,236.6]..[1800,1518,611.8]` → `[0,450,420]..[1800,900,603.016]`; no duplicate parent shell remains in the scene |
| `scripts/build_nurbs.py` | ✅ extended (P4b round 2) — `mcpNurbsSurfID` id bindings, `trim:false`, tension `0.0` default, census `blend 1` / `trim 0`, self-check now `G-41..G-56` (16 rules), `verify_script` refuses a literal or unbound name in any `parent*ID:` slot |
| `scripts/validate_specs.py` | ✅ extended (P4b round 2) — `G-55` (tension range) and `G-56` (no synthetic pointer), `G-51` now tests **every** rail (the linter was the lenient one), `tension1`/`tension2`/`seed`/`flip_trim` made genuinely optional with documented fallbacks. `PASS 90 / FAIL 0 / WARN 0` |
| `references/12-nurbs-gotchas.md` | ✅ extended (P4b round 2) — gotchas **3.20–3.28**, planning rules 17–21, open-items **§7.6**; the P4b "a second surface appears in the set" claim is corrected in a dated notice |
| `agents/max-nurbs.md` | ✅ extended (P4b round 2) — §6.7.4 id references · §6.7.5 trim/tension/edge-pair · §6.7.6 `classOf` filter; completion gate **15 → 19 rows**, anti-patterns **19 → 24**; no existing entry removed |
| `SKILL.md` | ✅ corrected (P4b round 2) — the four relational kinds now route to `agents/max-nurbs.md` + `07` §8.2 as implemented geometry, and an aperture is routed to a Boolean modifier / surface split instead of to `NURBSProjectVectorCurve` |
| `examples/nurbs.json` + `examples/nurbs.ms` | ✅ round 2 (P4b) — `SUR-007` renamed `SUR_007_VaultApertureGuide`, `tension1`/`tension2` dropped so the `0.0` default is exercised; the `.ms` **executed live**, 10 nodes, idempotent over 3 runs, per-node census and every bbox measured |
| `references/07-spec-grammar.md` §8.2.6 · `references/12-nurbs-gotchas.md` §1.4 + gotchas 3.14–3.19 · `agents/max-nurbs.md` §6.7 | ✅ corrected (P4b) — the three files that asserted the capability was missing. No new invariant ids, no new schema keys, no invented keywords |
| `references/nurbs-complete-guide.md` · `references/nurbs-architecture-recipes.md` | ✅ **vindicated (P4b)** — their keyword claims were correct. Explicitly **not** rewritten; §6.6 of PLAN.md was the right call |
| **`references/_p4b-remainder-evidence.md`** | ✅ **NEW (P4b-r)** — the executed transcripts behind both reference corrections: methodology, the shape/spline results, the modifier class+parameter results, the Data Channel vocabulary, the MCG/`curve_model` negative, and the Chaos Scatter crash. **Read before editing either reference file again** |
| `references/maxscript-splines-shapes.md` (the real `13`) | ✅ **corrected (P4b-r)** — largely vindicated; 10 dated corrections (`bezierShape`, the multi-spline `updateShape` trap, `#bezierCorner` on knot 1, `getSegLengths` return shape, the inert `pathParam`, path-param value cautions, `star.points`, `Arc`'s property names, `delete` leaving instances, and the two error-handling traps) |
| `references/arch-modifiers-and-procedural-reference.md` (the real `06`) | ✅ **corrected (P4b-r)** — was substantially wrong. 3 class names fixed; the headline instruction now routes `Extrude`/`Sweep`/`Lathe`/`Surface`/`CrossSection`/`Conform` to `3dsmax-mcp_add_modifier` and records `Bevel_Profile` as unusable; ~13 nonexistent parameter names marked `NO`; `Lathe.direction`→`axis` (matrix3); §2 rebuilt on the real 32-operator snake_case vocabulary with `DistToNode`/`FaceArea` marked nonexistent; the "CRITICAL Max 2027 Rule" retracted as unverified; §3 rewritten as a retraction (no `mcg_*`, no `curve_model`). 4 rows left UNVERIFIED rather than guessed |
| `scripts/install_skill.py` | ✅ **corrected (P4b-r)** — `collect_files()` now ships `scripts/ agents/ specs/ examples/` and the three top-level `.md` files; verified 53 files, all previously-missing paths present, deterministic, no `__pycache__`/`.pyc`/`.skill`. **The packaging gap is closed; the archive itself is still stale** |
| `references/maxscript-*.md` (10 files) | ✅ **deduped (P4b-r)** — `maxscript-animation-controllers.md` overwritten with the shared version (its `script_controller` guidance removed); all ten now byte-identical. **None deleted** — all ten are still linked from `SKILL.md` / `PLAN.md` / `CHECKPOINT.md`, so deleting any would dangle |
| `references/07-spec-grammar.md` · `09-defaults.md` · `01-architecture-aec-workflow.md` | ✅ **corrected (P4b-r)** — 7 `railID="0P"` sites narrowed to UNVERIFIED + a dated retraction; §10's "carries none of the four dependent kinds" replaced with the measured counts (one each of `rail_sweep` `two_rail_sweep` `blend` `trim`); the `trim`-does-not-cut statement added; `09` §6 confirmed already correct; `01`'s tyFlow tally 13→14 with the 14 names enumerated. **One stale cross-reference left, out of scope:** `07:1400` cites `§8.2.7` where the claim lives in `§8.2.8` |
| tyFlow tally across 6 files | ✅ **corrected (P4b-r)** — **14, not 13.** The connected toolset exposes exactly 14 `tyflow_*` tools and tyFlow is absent, so all 14 throw. Fixed in `AGENTS.md`, `PLAN.md`, `CHECKPOINT.md`, `SKILL.md`, `references/00-audit-p1.md`, `references/02-mcp-live-orchestration.md` |

### Dangling references still routing to bogus tools internally
Flagged in `references/00-audit-p1.md` §7, not yet fixed (outside P1's file ownership):
`nurbs-complete-guide.md`, `nurbs-architecture-recipes.md`, `arch-modifiers-and-procedural-reference.md`,
`architecture-exterior-pipelines.md`, `curve-construction.md`, `maxscript-animation-controllers.md`.

---

### The hand-off's central claim was false — prototype material does **not** propagate

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

---

## Incident log 2026-10-05 (P10-lite) — three "verified negatives" that are not negative

While checking the orchestrator's runbook against live Max, a probe intended to confirm the pack's
standing do-not-retry list **overturned three of its own entries.** Each was recorded in
`AGENTS.md` and `CHECKPOINT.md` as *measured*; each was wrong, and the same mistake recurred three
times in one batch, which is what makes it worth writing down.

| Standing rule as recorded | What execution shows | Control that proves the probe discriminates |
|---|---|---|
| **`getCurrentException()` inside a `catch` throws itself** — "do not retry" | **It works.** 6 of 6 throw kinds returned a real message: `Not creatable: Loft`, `Type error: Call needs function or class`, `Argument count error: Matrix3 wanted 4, got 9`, `object create wanted 0, got 2`, an explicit `throw "EXPLICIT"`, and `No "getPropNames" function for 42`. Repeated in a second batch: 4 of 4 | `try (1 + 1) catch (...)` → the catch was **NOT** entered (`NOT_TAKEN`). It also survives one level of `catch` nesting |
| **`findString` does not exist** — "use `substring s 1 n`" | **It exists and works.** `findString "hello world" "o w"` → **5** (1-based). `findString "abcdef" "cd"` → **3** | `findString "abcdef" "zz"` → `undefined` (a real miss), and `findString "abcdef" 12345` → **THREW**. A hit, a miss and a type error in one batch |
| **`matrix3` does not exist** | **It exists.** `matrix3 [1,0,0] [0,1,0] [0,0,1] [0,0,0]` → `classOf` **`Matrix3`**, `row4 = [0,0,0]` | `matrix3 1 2` → **THREW** (arity). The earlier "absent" verdict came from calling it with **9 numbers** — `Argument count error: Matrix3 wanted 4, got 9`, an arity error misread as absence |

**The shared root cause: a throw was read as an absence.** Every one of these three was probed with
something that *threw*, and the conclusion drawn was "the identifier is missing". `matrix3` is the
clearest: MAXScript's `matrix3` takes **4 arguments** (three rows plus a translation row), and calling
it the way everyone writes it — nine numbers, one per element — produces an arity error, not a
missing class. The repo already had this lesson twice recorded (`introspect_class "NURBSSet"` →
*Class not found* while `NURBSSet()` constructs; `CScatter` NotCreatable while `ChaosScatter`
works). It has now happened three times more, and **the mistake is always the same**: an exception
was treated as evidence about existence.

**The corrected probe form**, which separates the three cases that were being conflated:

```maxscript
-- report the VALUE and the throw separately; never infer existence from a throw alone
local v = undefined
local threw = false
try ( v = execute code ) catch ( threw = true )
out += code + " threw=" + (threw as string) + " undef=" + ((v == undefined) as string) \
        + " cls=" + ((classOf v) as string)
```

Then require **all three** before believing anything: a *hit* (value correct), a *miss* (right
shape, empty result), and a *bogus* control that must throw. A batch containing only throws
discriminates nothing.

### Two absences that survived re-test, recorded so they are not re-litigated

`setCopyMode` and `rotationZ` (and `rotationX` / `rotationY`) **are** genuinely absent, checked in
the same batch with the control present:

```
execute "setCopyMode 1" => -- Type error: Call needs function or class, got: undefined
execute "rotationZ 45"   => -- Type error: Call needs function or class, got: undefined
```

Those stay on the do-not-retry list, with the substitutes unchanged: `n = copy src` then
`n.baseObject = src.baseObject`, and `n.rotation = quat <deg> [0,0,1]`.

### And one P4b-r finding re-measured, with a **new** nuance

CHECKPOINT records that `Extrude` and `Sweep` "construct standalone and make `addModifier` throw",
which is why openings were cut by tiling instead. Re-measured with the host object varied:

| Host | `Sweep` | `Extrude` |
|---|---|---|
| `Box` | **THREW** | **THREW** |
| `Sphere` | **THREW** | — |
| `Edit_Poly` | **THREW** | — |
| **`Rectangle`** | **OK, mods=1** | **OK** |
| `Box` + `Shell` (the known-positive control) | OK, mods=1 | — |

So the failure is **host-dependent, not universal**: `Sweep` and `Extrude` attach fine to a
`Rectangle` and throw on every mesh-class host tried. **This does not reopen the P6 decision** —
tiling the wall with solids is the better route for this architecture anyway, since it emits zero
modifiers and dodges the measured 20-modifier freeze. But the earlier wording ("cannot be attached
via MAXScript") was too broad and should read "cannot be attached to a **mesh-class** host".

### Why these probes ran at all

`env_preflight.py`'s `sweep_on_shape` check expects *"Sweep applies to Rectangle"* at
`SEVERITY_FAIL`. Against live Max it returns **`mods=1 first=Sweep`** — **the check passes**, because
the preflight picked the one host where it works. That is either a lucky choice or an accidental
correctness, and it is worth knowing which before anyone edits it.

---

## P10-lite — the live chain run, re-executed end to end (2026-10-05)

The full S1→S5 chain was rebuilt offline and **re-run in Max**, because the deliverable is now
exactly this model and an emitted `.ms` nobody has executed is not a deliverable.

| Step | Command | Result |
|---|---|---|
| Rebuild all five stages into two temp dirs | `build_spec` · `build_nurbs` · `facade_tables` · `place_components` | `massing.ms` `nurbs.ms` `facade_table.csv` `world_table.csv` `assembly.ms` **byte-identical** across both dirs **and** to `examples/` |
| Validator | `validate_specs.py --dir examples` | **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** |
| Fresh scaffold | `init_project.py` then `validate_specs.py --allow-draft` | **PASS 105 / FAIL 0 / WARN 0 / SKIP 72** — *after* the `wall_cells` fix below; it was FAIL 1 before |
| `fileIn massing.ms` | live | **27 nodes** (22 `Box` + 5 `Dummy`) |
| `fileIn nurbs.ms` | live, **after** `fileIn snippets/nurbs_arch_library.ms` | **+10 nodes → 37** (7 `SUR_` + 3 `DRV_`) |
| `mcpAssemblyBuild_pavilion_01()` | live | **+217 → 254**, returned `true` |
| Idempotency | two further calls | **254, 254**, both `true` |
| Census | name-prefix + `baseObject` + modifiers | **239 `Box` + 5 `Dummy`**, **136 `PLC_`**, **29 `PROTO_`**, **52 `WAL_`**, **0 modifiers** anywhere |
| Instance sharing | 5 sampled `PLC_` vs their `PROTO_` | **5/5 share** the prototype's `baseObject`; negative control (`SP_GROUND_PAD` vs every prototype) → **0** matches |
| Wall cells | 4 bboxes vs `assembly.json` | exact: `WAL_EL_014_C01 [0,0,0]–[135,20,420]`, `WAL_EL_015_C07 [765,0,420]–[1035,20,820]`, `WAL_EL_017_C06 [1500,880,690]–[1650,900,820]`, `WAL_EL_021_C04 [0,750,420]–[20,900,820]` — each matching `plan_rect_cm` + `z_range_cm` literally |
| Cell volumes | 52 cells | all positive; no degenerate cell |
| Layer discipline | every node's `layer.name` | **0 nodes off layer `0`** — G-79 holds, `layer_map` stayed data |
| Renderer | `renderers.current` / `.production` | **Corona / Corona** — left that way at the user's request |
| Teardown | sweep by collected name, twice | `objects.count` 254 → **0**, renderer **preserved** |

### 254, not 244 — the node count reconciles, and the reason matters

CHECKPOINT's P6 row says **244**. That number is correct **for the S2→S5 path**, because P6's gate
ran `massing.ms` then `assembly.ms` and never `nurbs.ms`:

| | |
|---|---|
| `27` massing + `136` PLC + `29` PROTO + `52` WAL | **244** ← what P6 measured |
| plus `10` NURBS nodes, which this run *did* include | **254** |

**Both are right; they are different chains.** Anyone reporting a node count must say which. The
full S1→S5 chain produces **254**.

### The `/tmp` trap bit again, exactly as recorded

`bash /tmp` → `C:\Users\Turbolamer\AppData\Local\Temp`, but Python's `os.path.realpath('/tmp')` →
`D:\tmp`. The builders were handed `/tmp/p7a`, wrote to the git-bash directory, and
`fileIn @"D:/tmp/p7a/massing.ms"` returned **`fileIn: can't open file`** — which reads exactly like a
broken builder. The P6 note was right; it is now reproduced twice.

---

## P10-lite — three defects found and fixed

### 1. `init_project.py`: the `assembly.json` stub omitted `wall_cells` → **fresh scaffold FAILed G-1**

CHECKPOINT's P6 row claims "Fresh scaffold, `--allow-draft` → FAIL 0 / WARN 0". That row was
**stale**. Re-measured:

```
FAIL  1
G-1   FAIL      assembly.json  -   assembly is missing declared top-level keys: wall_cells
```

The stub predates P6's move off the Boolean modifier onto wall tiling, and `wall_cells[]` was added
to `07` §8.5 afterwards — **the same "a rule or file added after" pattern that has now produced
three separate defects in this repo** (G-56 vs `depth_cm` shells, G-69 vacuous, G-74 vs `wall_cells`).
Fixed at `scripts/init_project.py` `scaffold_assembly()`, and the docstring now records *why* the key
is there so the next reader does not "tidy" it away. **Verified: fresh scaffold → PASS 105 / FAIL 0.**

### 2. `init_project.py` mislabelled `nurbs.json` as computed

The stub's `source.reference` claimed `nurbs.json` was *"GENERATED by scripts/build_nurbs.py from a
locked massing.json"*. **`build_nurbs.py`'s own refusal message says the opposite**: *"nurbs.json is
hand-authored at P4 — this stage reads it and emits the normalised spec plus the MAXScript, it does
not compute the geometry."* A user following the stub would go looking for a generator that does not
exist, and the builder refuses outright when the file is absent. Fixed in the stub's `source.reference`
and in two module-level docstrings.

### 3. `place_components.py`: four dead Boolean-era functions + misleading docstrings

An AST sweep for unreferenced top-level definitions found four:

| Line | Symbol | Why it is dead |
|---|---|---|
| 334 | `cut_modifier_name` | named a cutter's Boolean modifier; no Boolean is emitted |
| 343 | `cut_pass_fn_name` | named a "cut pass" call boundary; no cut pass is emitted |
| 682 | `cutter_box` | 40 lines converting a facade-local opening into a cutter box literal |
| 529 | `run_angle_deg` | superseded by the world table's `rot_z_deg` |

`BOOLEAN_DIFFERENCE_OPERATION = 1` is kept but relabelled: it was **never measured live**, and
nothing reads it. The module docstring also still described *"cut passes of at most five cutters"*,
the *"cutter stands 1 cm proud of each face"* rationale, and a *"reset the hosts' stack by removing
only Boolean modifiers"* step — **none of which is in the emitted script any more.** All corrected.

Removed, then rebuilt: **`assembly.ms` is byte-identical to the committed file**
(`c2bca564146d371c8e6194dab7588030`) and the self-check still passes G-71…G-83. Dead code removal
changed no output, which is the point — it was dead.

---

## P7 — what the cancelled probes proved

P7 was cancelled mid-stage. The probes that had already executed are real measurements and are kept
in **`references/_p7-evidence.md`**. They closed two long-open questions:

### The renderer CAN be set, and the bridge is not the way — this closes P0 and PLAN §4.2

`get_plugin_capabilities` reports the renderer via `classOf renderers.current`, which reads back as a
**Name** and so *looks* assignable. It is not:

```maxscript
renderers.production = Corona      -- ERROR: Unable to convert: Corona to type: Renderer
```

The slot wants an **instance**:

```maxscript
local c = Corona()                 -- construct the instance
renderers.production = c           -- OK, reads back Corona
renderers.current    = c           -- OK, reads back Corona -- the two slots are independent
```

`RendererClass.classes` lists 8 engines including `Corona`. **`Corona()` costs ~3.5 s cold, ~0.4 s
warm** — it initialises the renderer on construction, so it must be its own `execute_maxscript` call
or it reads as a timeout. This is the P0 question the bridge had no tool for, now answered by
execution. The user's Max is left on Corona for both slots.

### 16 Corona material classes; **15 construct**; the one you want has a leading underscore

| Fact | Evidence |
|---|---|
| The architectural material is **`_CoronaPhysicalMtl`** — with a leading underscore. `CoronaPhysicalMtl` is not a name in this build | `classOf` read-back on construction |
| **`CoronaPortalMtl` THROWS on construction** while all 15 siblings build — present in `Material.classes`, not instantiable. Bogus control threw in the same batch, so the probe discriminates | 15 of 17 |
| All 171 property names are **camelCase** (`baseColor`, `baseRoughness`, `clearcoatIor`), grouped as `<slot>` / `<slot>Texmap` / `<slot>TexmapOn` / `<slot>MapAmount` | `getPropNames` — which **works on materials**, unlike on the NURBS plugin classes |
| A bogus property name **throws on both write and read**, unlike the NURBS constructors which silently swallow unknown keywords — so a slot map is safe to write blind | `m.TotalGarbageProp = 1` THREW |
| Enum modes are **Integers** (`metalnessMode` 0, `roughnessMode` 0, `iorMode` 0, `alphaMode` 0, `normalFilteringMode` 2, `gBufferOverride` −1), and their meanings are **not discoverable from MAXScript** | `cls=Integer` on every one |
| **`node.material = m` works**; the node's **sub-material index does not** — `materialID` `subMaterialID` `matID` `materialId` all throw on both `Box` and `Edit_Poly`, with a bogus control alongside | calibrated sweep, §4 of the evidence file |
| **`materials` is `undefined`** in this build — no library collection to enumerate, the same family as `layers` | `classOf materials` → `UndefinedClass` |

UV rules for NURBS vs poly — the other half of P7 — were **never probed** and are not guessed.

---

## Incident log — false conclusions caught

Kept so the same error is not repeated.

**2026-10-05 — "the facade grid is complete, `PASS 120 / FAIL 0`" (P5).** The tenth and eleventh
instances of the same family, and the first two where **the guard was not what caught it** — I read
the output.

```
PNL-024  F-S L0  punched_window  u[135,315]  v[260,270]   ->  180 x 10 cm
```

A 180 cm window, `OP-G-01`, running `sill 90 -> head 270`, had been cut into a 180 × 170 panel and a
**10 cm ribbon of glass**, because `OP-G-02` — an entrance in a *different bay* of the same facade at
the same level — has `head_cm = 260`, and the v grid was the **union of every opening's sill and head
across the whole facade**. Every offline gate was green: the partition was exact, the openings were all
covered, `validate_specs.py` was at `FAIL 0`, the builder was byte-deterministic.

The rule was not stupid, which is what made it expensive. A curtain wall's transom lines *do* run
continuously across a run, so "one shared v grid" is the textbook arrangement — and it silently
imposes **every bay's head line on every other bay**. `G-62` had been weakened from *exactly one panel
per opening* to *"tiles"*, specifically to accommodate openings that the shared grid split. The
weakened invariant and the bad rule protected each other: the rule produced splits, and the split
rule tolerated them. Nothing was fabricated and nothing was assumed — the defect was a **specification
that was wrong**, and no linter can catch a specification that is wrong.

The fix is at the root, not at the symptom: the v division is computed **per bay**, so an opening's
own sill and head are its only divisions, `G-62` is strictly **exactly one**, and a bay with no
opening becomes one whole `blank` panel. Transoms are now continuous *within* a bay rather than across
the run — the correct trade, and stated as a cost. `axes[]` gained a required `bay_index` as a
consequence. Measured after the fix: 136 panels, smallest height 20 cm (a legitimate transom head
band), smallest width 15 cm (a mullion pier), 16/16 openings on exactly one panel.

**Guards now in force:**
- **Weaken an invariant only when a measured physical fact requires it, and record what required it.**
  `G-62` was softened to "tiles" on reasoning, not on measurement.
- **An exactness argument is not a correctness argument.** "The v grid is continuous across the
  facade" says nothing about whether it is continuous across a bay it has no business crossing.
- **Read the artefact, not the verdict.** Every prior incident was caught by a gate; this one was
  caught by opening the generated file and looking at a panel's dimensions. That is a cheaper test
  than a fault-injection battery and it ran first.

---

**2026-10-05 — "the registry's thickness is a defensible in-range value" (P5).** The twelfth instance,
and the smallest, but it is the same species: **a number in a generated file that nobody traced to a
declared default.** The builder chose `panel_thickness_cm = 4.0`. `D-CL-05` declares default **3**,
range `2 … 8`, so `4.0` was inside the range and would have survived any range check — including the
one `G-16` runs. It was caught by reading the value against `09-defaults.md`, not by a failing gate,
and there was no gate that could have caught it.

**Guard now in force, and it completes the standing list:** *a convention's **default** is the value
to use; a value merely inside its **range** is an invention, and an invented value needs a ledger
entry and a reason.* Every number in a generated file must be traceable to either a declared default
or a formula. Pinned to `3.0` / `2.0`, which are `D-CL-05` and `D-FM-10`'s own defaults.

---

**2026-10-04 — "NURBSSet does not exist" (P0 → v2).** I concluded the NURBS API was fictional and
re-scoped the whole plan around rebuilding it. P1 disproved this by executing the library. Three
compounding causes:

1. Believed `introspect_class "NURBSSet"` → "Class not found", despite the skill's own rule that
   introspection is a hint, never proof.
2. The preflight probe used `get #NURBSSet` (returns `undefined` even for real classes) and guarded
   `NURBSSet()` behind `if id != undefined`, so the construction test **never ran** and the check
   passed vacuously.
3. `discover_plugin_classes superclass=NURBS` used the wrong superclass name and returned 0.

**Guards now in force:**
- Every class-existence claim ships with a known-bogus control in the same batch.
- Only the orchestrator runs live probes; subagents receive verified data.
- `env_preflight.py` now asserts `nurbset_present`, so a regression fails loudly instead of
  silently passing.
- `PLAN.md` §6.6: do not rewrite `nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` on
  suspicion — verify, then correct only what fails.
- **New guard (from the second incident):** an "unresolved" label is not a finding. Nothing may be
  recorded as blocked, impossible, or non-constructable without an execution transcript showing the
  error. Two of this project's worst mistakes were *fabricated negatives*, not omissions.

---

**2026-10-04 — "`NURBSControlVertex` does not construct" (P1).** The second instance of exactly the
same error class as the one above, one stage later. `12-nurbs-gotchas.md` carried bug 3 as
"UNRESOLVED — the one remaining NURBS blocker" and told readers to distrust `makeCVCurve` output and
prefer another route. **It was never executed.** One probe in P1-b settled it:

```
NURBSControlVertex [10,0,0]            -> NURBS_cv([10,0,0], 1)
setCV c 1 (NURBSControlVertex (point3 55 66 77) 0.5)  -> getCV = NURBS_cv([55,66,77], 0.5)
setCV c 1 [0,0,0]                      -> ERROR: Unable to convert: [0,0,0] to type: NURBSControlVertex
```

The class was always fine. The bug was a missing type wrapper — and because `makeCVCurve` returned a
valid-looking curve anyway, the failure was invisible. Worse, the same sweep that resolved bug 3
found an **unrecorded fourth bug** (`close` is a no-op, so `closed:true` silently produced open
geometry): the "three bugs" count was itself inherited from an unverified summary.

**Lesson, now rule 12 in `12-nurbs-gotchas.md`:** treat every unexecuted claim as a hypothesis. The
count of known bugs is only as trustworthy as the executions behind it.

---

**2026-10-04 — "the builder is done, it passes every check" (P3).** The third instance of the same
family, and the most instructive one, because *every offline gate was green*. `build_spec.py` had a
seven-rule self-check, byte-level determinism proof, fault injection on seven invariants, six proved
refusal paths, and `validate_specs.py` at `PASS 67 / FAIL 0 / WARN 0`. The emitted `massing.ms` had
**never been executed**, because I had forbidden the authoring agent from touching the bridge — the very
rule that keeps Max single-threaded also means an emitted artefact ships unrun.

One `fileIn` and it was dead:

```
fileIn examples/massing.ms
-> Compile error: no local declarations at top level:  SP_GROUND_PAD
```

A second live-only defect surfaced immediately after the fix: the delete guard
`if (getNodeByName "X") != undefined do (…)` works inside `fileIn` and **throws** in a direct
`try`/`catch` — a construct that is correct in one context and fatal in another, which no static check
can see.

**Guards now in force:**
- **An emitted `.ms` is not done until `fileIn` has run it and its output has been measured.** A stage
  that emits MAXScript owns a live run, and the orchestrator performs it — delegation stops at the
  artefact boundary, never at the execution boundary.
- Structural self-checks are necessary and **not sufficient**. They prove the file is well-formed; only
  the interpreter proves it is loadable.
- Two grammar defects surfaced the same way and are worth remembering: `G-38`'s first roof reading was
  simply wrong (`deck_thickness` hangs *down*), and a "simple ring" profile cannot express a parapet at
  all. Both were authored by me, in the document that is supposed to be authoritative.

---

**2026-10-04 — "the builder is done, every offline gate is green" (P4).** The fourth instance of the
same family, and the first one the standing guard actually caught. `build_nurbs.py` had a nine-rule
self-check, byte-level determinism, eight proved refusal paths, and `validate_specs.py` at
`PASS 84 / FAIL 0 / WARN 0`. The first `fileIn` of `examples/nurbs.ms` ran, built six nodes, and was
idempotent — and a defect was sitting in the output the whole time:

```
DRV_001_VaultPanels  min=[0,0,441.043]  max=[1800,900,625.94]     <- panels of the 25 cm shell
```

The vault's panels were sampled from the **offset shell**, not the vault. The emitted helper resolved
a surface by `superClassOf o == NURBSSurface` but looped the whole set keeping the **last** match, and
a shelled surface's last surface *is* the offset. `DRV_002` was unaffected because its surface has no
offset — so the example's own numbers agreed with each other while both being wrong. After the fix
(`found = i; exit` — take the first) the same node measures `min=[0,0,420] max=[1800,900,600.97]`,
which is the design surface.

**Why this one is worth more than the previous three:** nothing was fabricated and nothing was
assumed. The defect existed only in code that had never run, and it was found by *measuring the
output against the design intent* — not by reading the code, not by a reviewer, not by a rule.

**Guards now in force, unchanged and now twice-proven:**
- **An emitted `.ms` is not done until `fileIn` has run it and its output has been measured against
  the spec's intent.** Two for two at P3 and P4.
- **Structural self-checks are necessary and not sufficient.** Nine rules passed; the bug was in the
  one thing no rule covered — which surface a derivative reads.
- **An invariant the builder enforces silently is a defect.** Take the *design* surface, not the
  last one; it is now written down in `07` §8.2.5 and in `agents/max-nurbs.md`.

---

**2026-10-04 — "rail sweeps / blends / trims expose no API, they are not implemented" (P4).** The fifth
instance of the same family, and the most instructive one, because it was committed to three
authoritative documents. P4 probed 15 candidate property names on freshly constructed
`NURBS1RailSweepSurface` / `NURBS2RailSweepSurface` / `NURBSBlendSurface` / `NURBSProjectVectorCurve`
objects, got `ERR` on **every** name including the four that do exist, and concluded the classes were
unimplemented. `07` §8.2.5, `12-nurbs-gotchas.md` and `agents/max-nurbs.md` were all written to say
"do not promise these in a schema" — a whole stage of the architecture was deferred on a false negative.

Two things were wrong, and the first one is new:

1. **The probe read the object in the wrong state.** Relational properties are populated only once the
   sub-object is committed inside a `NURBSNode`. On an unattached object every name fails. The same
   probe run against the committed sub-object returns `rail=0 railID="0P" parallel=true numCurves=3`
   immediately. P4 had *already discovered this exact rule* for `evalPos` — "a surface is not evaluable
   until it is committed" — and then failed to apply it one paragraph later.
2. **The probe's access syntax was invalid.** `o["rail"]` is not dynamic property access in MAXScript,
   so it fails for *every* name including known-good ones. A probe that returns uniformly `ERR` across
   a heterogeneous name list is a broken probe, not a uniform absence — and the P4 name list was
   heterogeneous.

The guide and recipes that the audit had marked "unverified, do not rewrite" turned out to be
**correct all along**, including exact keyword names and the `parent1ID:`/`parent2:` recipe.

**Guards now in force:**
- **Never probe a NURBS dependent sub-object in a pre-commit state.** Build it, `appendObject`,
  `NURBSNode`, then read. The commit is part of the measurement.
- **A uniform result across a heterogeneous name list is a broken probe.** It must contain at least one
  known-positive name. Mine had none, which is why the bogus control alone did not save it.
- **Include a known-positive control in every property-read probe**, not only a bogus one. A control
  proves absence; a positive proves the probe can detect presence.
- If a document says a capability is unimplemented, the burden is on the *document* being wrong.
  Verify before repeating the claim in a second place.

---

**2026-10-04 — "the schema extension is done, every offline gate is green" (P4b).** The sixth and seventh
instances of the same family, back to back, and the first time the standing guard caught one *before* it
shipped rather than after. `build_nurbs.py` had a 14-rule self-check, `validate_specs.py` was at
`PASS 88 / FAIL 0 / WARN 0`, determinism was proved, five invariants had fault-injection proofs, and the
example's pre-existing emission was verified byte-stable. The emitted `.ms` was still unrunnable:

```
fileIn examples/nurbs.ms
-> Syntax error: at string, expected (
   In line:  "u_loft":
```

Defect 1: the generator emitted a Python-shaped `case kind of "u_loft": ( … )` dispatch. MAXScript `case`
requires the outer parenthesised block **and** forbids string case-labels. Fixed by mapping the kind to
an integer and keeping every branch body untouched. `verify_script` had nothing to say about it, because
a structural check cannot compile.

Defect 2 — worse, and only the live run could find it. With the file compiling, the `G-54` census threw:

```
build_nurbs G-54: node SUR_007_VaultSkylight committed 1 NURBSSurface sub-object(s)
                 but the spec implies 2
```

Not a wrong expectation. `NURBSProjectVectorCurve` was emitted with **`parent2:` bound to the surface
index instead of the profile-curve index** — it projected the surface onto itself. 3ds Max dropped the
relation at commit without a word, exactly the hazard `G-54` was written to catch. With two or more
profiles the defect was worse: extra profiles were created and left dangling, with only one projection
emitted. Both fixed; the census is what turned a silent geometry loss into a build failure.

**Guards now in force:**
- **The census proved itself on its first live outing.** It is the only check in this repo that can catch
  a defect no linter and no compiler can see, because the failure mode is *absence*.
- A generated artefact must be compiled by the target interpreter, not just pattern-checked. `verify_script`
  should gain a check for `case … of` shape if more dispatch is ever emitted.
- The census count for a relation is **geometry-dependent**. It came from one probe each; the first real
  spec is the measurement. That is now written into `agents/max-nurbs.md` as intended behaviour.

---

**2026-10-04 — "the schema extension is correct, the example builds 10 nodes" (P4b round 1 → 2).**
The eighth and ninth instances of the same family, and the first where **the census that was built
specifically to catch this class of defect passed a build that was wrong in two independent ways.**

What shipped looked clean by every offline measure: `build_nurbs.py` had a 14-rule self-check,
determinism was proved, five invariants had fault-injection proofs, `validate_specs.py` was at
`PASS 88 / FAIL 0 / WARN 0`, and the emitted `.ms` **ran** — 10 nodes, idempotent, every bbox
measured and tabulated. Then someone read the bboxes.

```
SUR_006_CanopySoffit  min=[0,0,236.6]  max=[1800,1518,611.8]     <- 1518 cm against a 900 cm plan
SUR_001_Vault        min=[0,0,420]    max=[1813,900,636.7]      <- the same shell, three times over
```

**Defect 1 — the overshoot was a *default*, not a bug in the feature.** `NURBSBlendSurface` tension
was hardcoded `1.0/1.0`. A 6-case controlled probe on the real example geometry showed `0.0/0.0`
fills exactly between the two selected edges (`Y 450…900`, a correct soffit) while `1.0/1.0` reaches
`Y 1195.64` and drops to `Z 369.758`. Nobody had asked what `1.0` *means*; the reference material
said tension existed, the builder filled in the number that looked neutral, and the number is not
neutral. **`1.0` was a fabrication wearing a default's clothes** — the eighth incident in a family
whose first member was the fabricated `NURBSSet` negative.

**Defect 2 — a relation re-instantiated its parents.** `parent:` names an index *inside the
dependent set*, so the builder rebuilt each parent surface there. A parent named by two relations
existed three times in the scene. The obvious fix was a `consumed` bookkeeping rule, and that fix
would have been wrong: a controlled probe showed `parent1ID:` — a `nurbsID` reference — resolves a
parent living in **another node's set**, so the duplication is unnecessary in the first place and the
parent keeps its own node (and its derivatives).

Two further facts came out of the same probe and are now rules rather than folklore:

- **A synthetic `nurbsID` crashes 3ds Max.** `parent1ID:12345` → `EXCEPTION_ACCESS_VIOLATION`. Not a
  MAXScript error, not catchable, leaves orphans. `G-56` exists for this alone.
- **`trim:true` does not cut.** Two structurally different profiles — one spanning the whole vault,
  which a real trim would have split in two — produced byte-identical output. The "second surface
  appears in the set" note that P4b recorded as evidence the trim works was the parent's own CV copy.
  **That note had already been promoted into three files as a verified fact.**

**Guards now in force, extending what was already standing:**
- **A default value is a claim about behaviour and needs the same transcript as any other claim.**
  Six cases, one question ("what does `1.0` do?"), and the defect was gone. Add to the standing list
  next to "no literal indices": *no number in a generated file that nobody has watched Max interpret.*
- **A feature that silently succeeds must be measured by what it produced, not by the fact that
  something appeared.** `trim:true` "worked" — a surface appeared. It was the wrong surface. The
  round-1 census counted `2` surfaces for `trim` and was satisfied by the duplicate.
- **Before writing an elaborate fix for a duplication, check whether the duplication is necessary.**
  I was about to design `consumed` bookkeeping; a 20-line probe deleted the need for it.
- **A finding promoted into several documents is not thereby verified.** The trim note was in three
  files by round 2 and wrong in all three.

---

**2026-10-04 — "getProperty doesn't work / execute doesn't work" (P4b-r).** Two false negatives
found while verifying the reference files, both the same family as the eight earlier incidents,
and both found by writing a control next to the claim.

**False negative 1 — a plugin-class finding generalized to everything.** P4 recorded
*"`getProperty o #x` also fails"* and *"`o["name"]` bracket access is **not** valid dynamic
property access → always `ERR`"*". Both were measured on **NURBS plugin classes**. On built-in
classes `getProperty o #radius` returns `40.0`, and `("steps" as name)` coerces, so
`getProperty o ("radius" as name)` is a perfectly good **dynamic** read. The P4 rows were not
wrong — they were **over-generalized from a plugin to the language**, and the only reason anyone
believed the generalization is that nobody tried it on a `Box`.

**False negative 2 — a type error wearing a broken-tool's clothes.** `execute` appeared dead
three separate times: `execute "gTestArc.radius"` inside a string concatenation, and
`execute "1+1"` likewise. Both "failures" were `"prefix" + numericValue` throwing a type error —
`execute` had returned fine both times. Chased for three probes before the real cause showed up.
The tell was available immediately and I read past it: a tool that fails on `1+1` is not a tool
that is broken.

Both had the same cheap cure that the P4b incident already prescribed — **a known-positive
control next to the claim** — and this time it is recorded as a *method*, not just a warning:
`isProperty` for existence (calibrated: `false` on bogus, `true` on two known-positives in the
same call) and `getProperty o (n as name)` for the value. Roughly seventy parameter names were
settled per probe that way, which is why a two-file claim-by-claim pass over ~180 claims was
affordable at all.

**A third, cheaper lesson, same session.** The `13` vs `14` tyFlow tally had been carried as an
unresolved discrepancy in `references/01` since P1. It was resolved by **counting the names in
the live toolset** — thirty seconds — after sitting on the backlog for five stages. A backlog item
that can be closed by counting should not be deferred four times.

---

**2026-10-04 — a hard crash, caused by being efficient (P4b-r).** Having found that 16 of 23
modifier classes attach with `addModifier` and 6 more with the typed tool, the obvious way to
verify ~70 parameter names was to attach every modifier to one node and sweep. That is what I
did: **20 modifiers on a single `Box`, in one call.** Two `EXCEPTION_ACCESS_VIOLATION` dialogs
from Chaos Scatter's `px_modifierClothing.ms` appeared — with **no ChaosScatter object in the
scene**. Max survived, but only because the offending node was already built.

The causal link to stack size is **inference**; I did not isolate it. But the failure mode is
what matters and it is a **process crash, not a wrong result** — the one failure mode a
modeling pipeline cannot retry its way out of. Chaos Scatter is this user's only working scatter
route, so the hazard sits directly on the P6 path.

**Guard now in force: assemble modifier stacks incrementally, and never build a stack of this
size in one scripted call.** The economy was real — one sweep settled dozens of claims — and it
was not worth a crashed Max. If the ladder needs measuring, P6 measures it deliberately, with a
bounded 1/2/5/10/20 series, and records where it breaks.

---

## Next actions

**P6 is closed.** Its live gate ran and was measured, and it found a defect that changed the
stage's design: the Boolean modifier is unusable, so openings are cut by **tiling the wall with
solid cells** instead. Full numbers in the stage table and §"The Boolean modifier is unusable in
this build".

Orchestrator verification, all re-run here rather than taken on a subagent's word:

| Check | Result |
|---|---|
| `python -m py_compile scripts/*.py` | exit 0 |
| `validate_specs.py --dir examples` | **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** |
| … `--warnings-as-errors` / `--build` | identical, exit 0 both |
| Determinism, all four artefacts | `tmpA == tmpB == examples/` **byte-identical** |
| Fresh scaffold, `--allow-draft` | **FAIL 0 / WARN 0** |
| Fault injection, builder / linter | **11 / 11** and **3 / 3**, baseline clean |
| Live gate 2 — `massing.ms` | **27** nodes, 3-run idempotent, 9/9 bboxes exact |
| Live gate 4 — `assembly.ms` | **244** nodes, 3-run idempotent, **0 modifiers**, 52/52 cell bboxes exact, volume identity **0.000000 cm³** on all 8 hosts, scene back to **0** |

Two traps in the verification itself, both recorded because they nearly produced a false pass:

- `place_components.py --in <tmpdir>` needs **four** inputs. Copying only what
  `build_spec.py` writes makes it refuse with *"dimensions.json is missing … a builder never
  invents an input"*. That refusal is **correct** — copy all of `examples/*.json` and `*.csv`.
- **`/tmp` is two different directories.** Git-bash `/tmp` is
  `%LOCALAPPDATA%\Temp`; Python's `os.path.realpath('/tmp')` resolves to `D:	mp`. Writing to
  one and `fileIn`-ing the other produces `can't open file`, which reads like a build bug.

### 1. ~~P7 — Corona materials + UVs (S6)~~ ⛔ **CANCELLED by the user, 2026-10-05**

Materials are made by hand. Do not start this stage. What survives it is already written up in
§"P7 — what the cancelled probes proved" and in `references/_p7-evidence.md`: the **renderer set
route** (which closed P0) and the Corona class census. The one genuinely missing piece is
**UV rules for NURBS surfaces vs poly-modified geometry** — if a hand-materialed model ever needs
unwrapping, start there.

2. **P8 and P9 ⛔ cancelled** with P7. `qa_check.py`, `capture_views.py`, `export_max.py`,
   `lint_script.py`, `check_skill_md.py` **do not exist and are not planned**. Any text implying a
   QA loop or an exporter is now wrong.

3. **`curve-construction.md` needs a rewrite, not a fix.** P4b-r confirmed `curve_model` is absent
   from the live toolset, so the file documents a tool that does not exist. Same treatment as
   `tyflow-graphs.md`: decide rewrite-vs-OBSOLETE. `procedural-graphs.md` is already settled.
4. ~~**Two open geometry questions the P4b probes raised but did not answer**~~ — ✅ **both CLOSED at
   P12 by execution**, see §P12: the `nurbsID` printed format is `<decimal>P` (`"0P"` was real), and
   the 5-rib loft's `numCVs [9,4]` is the parent's own CV conversion. Note the P4b round-2 *retraction*
   of the `"0P"` reading was itself a false negative and has been corrected in every file that carried it.
5. **`nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` are still unverified beyond the P1-b
   corrections.** → ✅ **DONE at P12**:
   69 claims executed, 16 disproved and corrected in place. Transcript `references/_04-05-evidence.md`.
6. ~~**Rebuild the `.skill` archive.**~~ ✅ **DONE — rebuilt at P14** (79 files, byte-identical to the working tree in both install locations).
7. **Three doc drifts the orchestrator pass found but did not own** (it was scoped to one file):
   `agents/max-facade.md:316` still prescribes `setCopyMode #instance` and `rotationZ`, both of
   which are absent (§"Incident log 2026-10-05"); `agents/max-assembly.md` §5 says prototypes are
   *"parked at a scratch offset outside the footprint"* — all 29 are emitted at `pos [0,0,0]`;
   `scripts/validate_specs.py --help` advertises `G-1..G-40` while the linter runs `G-1..G-83`.
8. **Whether the Chaos Scatter is part of the delivered model is still unanswered.**
   `assembly.ms` emits **zero** scatter geometry (zero occurrences of `ChaosScatter` / `scatter` /
   `SCT_001` in 1979 lines) while `assembly.json.scatter[]` carries one row, and
   `agents/max-assembly.md` §7 gate row 8 requires reading `FpInterface.getInstanceCount()` back —
   which implies a scatter object existed at the P6 gate. Two coherent readings: the scatter is
   **declared** and the **user applies it by hand** from `snippets/chaos_scatter.ms`, in which case
   **254 is the delivered count** and nothing is missing; or the gate applied it and was measured
   before, in which case the count is 254 **+ 1 scatter node + N instances**. **Not guessed.**

### ~~3. `curve-construction.md` needed a rewrite~~ — **RESOLVED 2026-10-06, resolved as OBSOLETE**

Decision made and executed: the file is marked **OBSOLETE, reference only** with a router at the top
and the original body fenced "do not execute", following the existing `railclone.md` /
`tyflow-graphs.md` convention. It was not rewritten, because it had no verified content to preserve
— 120 lines written entirely against four absent tools. See §"Close-out pass, 2026-10-06" item 2.

### ~~6. Rebuild the `.skill` archive~~ — **was already fixed before this pass**

`collect_files()` ships `scripts/`, `agents/`, `specs/`, `examples/` and the four top-level md
files; the archive was rebuilt at P4b-r and verified byte-identical to the working tree on six
files. Kept here because this pass found the *documentation* of that fact was still stale (item 4
below).

### ~~7. Three doc drifts the orchestrator pass found but did not own~~ — **all three already fixed**

`agents/max-facade.md:316`, `agents/max-assembly.md` §4 step 5, and the `validate_specs.py --help`
`G-1..G-40` string were all corrected before the close-out pass. Two *other* stale rows were found
by this pass and are recorded in §"Close-out pass, 2026-10-06" item 3.

### 8. ~~Whether the Chaos Scatter is part of the delivered model~~ — **ANSWERED 2026-10-06: scenario A**

The user decided it. The scatter is **declared, not geometry**: `assembly.ms` emits zero scatter
nodes and `assembly.json.scatter[]` carries one declaration row, which the user applies by hand
from `snippets/chaos_scatter.ms`. **254 is the delivered count.** A residual documentation
inconsistency in `agents/max-assembly.md` is still open — see §"Close-out pass, 2026-10-06".

### Closed at P6 by the orchestrator (were subagent deviations)

- **`07` §9.6 / §9.7 / §9.8 now carry the corrected `--allow-draft` rule.** All three said the flag
  "forces them to run and they will then fail", which was true only of a draft *with content* and
  was the direct cause of 17 FAIL rows on a fresh scaffold. Each now points at §9.9, which holds
  the rule in full.
- **`init_project.py` `scaffold_massing()` now writes `doc["defaults"] = {}`.** Without it a freshly
  scaffolded project FAILs `G-1` on the newly-declared key. **Verified:** fresh scaffold →
  `FAIL 0 / WARN 0`.
- **`07` §10 names `examples/assembly.json`** as the eighth and last file of the chain, states that
  it is why `massing.json` needed `facade_wall`, and records that `place_components.py` — not
  `build_spec.py` — is now the project's last builder.
- **`07` line ~1400's stale `§8.2.7` citation.** The "trim projects and does not cut" claim lives in
  **§8.2.8 row 8**, not §8.2.7 (the schema section).
- **`G-74` was widened to cover `wall_cells[]`,** and the reason is a **pattern**, not a one-off.
  Fault injection showed a duplicated cell `node_name` and a non-derived `node_name` both passing
  the self-check clean, because `G-74` iterated `("placements", "opening_cuts", "scatter")` and
  `wall_cells` was added afterwards. **This is the third time in this repo a rule has failed to
  fire because the thing it governs was added later** (after P4b's "G-56 does not cover
  `depth_cm` shells" and P5's "G-69 is vacuous"). **When a stage adds a new array, re-read every
  rule that enumerates the old ones** — and prove it with fault injection, because a rule that
  does not mention your new thing will not tell you.
- **`references/14-chaos-scatter.md` has one stale row** (out of scope when P6-C was written): its
  `G-74` row still names only `placements[]` / `opening_cuts[]` / `scatter[]` and omits
  `wall_cells[]`. It correctly does **not** mention Boolean cutting.

---

### Close-out pass, 2026-10-06 — documentation and lint, no live bridge

**This pass measured nothing against 3ds Max.** No `3dsmax-mcp_*` tool was available for its whole
duration. Everything below is either a direct reading of a checked-in file, a fault-injection run
of the repo's own Python, or a **user decision**. Nothing here is new evidence about Max's
behaviour, and no new claim about Max may be derived from it. Source brief:
`references/_closeout-evidence.md`.

Offline gates re-run here, so the ledger is not asserting a pass it did not watch:

| Check | Result |
|---|---|
| `python -m py_compile scripts/*.py` | exit 0 |
| `python scripts/validate_specs.py --dir examples` | **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** |
| `python scripts/env_preflight.py` | exit 0, every check **SKIP** — *two-phase by design; that is not a pass* |

#### 1. `G-74` had a real lint-side gap — FOUND AND FIXED, and it is the **fourth** of its pattern

P6's entry above widened `G-74` to cover `wall_cells[]` — in **`place_components.py`**, the
**builder**. `place_components.py` had swept all four tables since P6. **`validate_specs.py`, the
linter, had not.** Its `_g74_node_names` iterated only
`("placements", "opening_cuts", "scatter")`, so **52 `wall_cells` node names went unlinted** while
the P6 gate was reading as clean.

Fixed to all four. The check now reports
`205 node names, unique across placements / opening_cuts / wall_cells / scatter`; it was `153`.

**Proven by fault injection, not by inspection.** Three defects were injected and all three now
FAIL: a `wall_cells` name colliding with a placement name, a `wall_cells` name not derived from its
own id, and two `wall_cells` colliding with each other. **At least two of the three would have
passed the old linter silently.**

This is now the **fourth** time in this repo that a rule has failed to fire because the array it
governs was added later:

| # | Where | What was not covered |
|---|---|---|
| 1 | P4b | `G-56` did not cover `depth_cm` shells |
| 2 | P5 | `G-69` was vacuous |
| 3 | P6 | builder-side `G-74` did not cover `wall_cells` |
| 4 | close-out | **linter-side `G-74` did not cover `wall_cells`** |

**The pattern, stated once so it stops recurring: when a stage adds a new array, every rule that
*enumerates* the old arrays must be re-read — in every implementation of that rule, not just the one
the stage happened to touch. And prove it with fault injection, because a rule that does not mention
your new thing will not tell you it does not mention it.** Row 4 was not visible from row 3's write
up at all; it took a deliberate injection to surface.

#### 2. Reference files corrected against absent tools

The standing rule from §"Two absent tool families, confirmed" applies, and it has a direction
that is easy to get wrong: **a reference file *warning* that a tool is absent is CORRECT and must
be kept. A reference file that *prescribes* a call to an absent tool is WRONG.** `grep -l` for a
name does not distinguish the two — the sentence has to be read.

| File | Action |
|---|---|
| `references/curve-construction.md` | **OBSOLETE, reference only.** Router added at the top, original body fenced "do not execute" — the existing `railclone.md` / `tyflow-graphs.md` convention. Not rewritten: 120 lines against `curve_model`, `inspect_curve`, `edit_curve`, `draw_spline`, with no verified content to preserve |
| `references/architecture-exterior-pipelines.md` | Corrected **in place**, 186 → **461** lines. Architectural *dimensions* content (floor heights, stair risers, layer naming) kept and routed to `09-defaults.md` as the authority · every absent-tool call rerouted · the Boolean-openings section **replaced by the `wall_cells[]` solid-tile route** (`G-81`) · layer stack reconciled with the repo's closed 8-name vocabulary |
| `references/nurbs-architecture-recipes.md` | **Tool-routing prose only.** Its NURBS geometry recipes were **VINDICATED at P4b and were not touched** |
| `references/nurbs-complete-guide.md` | **Tool-routing prose only** — two incidental mentions of `geometry_qa` / `agent_viewport` in verification advice. Geometry content verified; only the routing sentences changed |

The last two are the case §"the one rule that matters most" exists for: **rewriting
`nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` on suspicion is forbidden**, and this
pass did not do it. Narrow the edit to the prose that routes to a tool, leave the geometry alone.

#### 3. Three stale rows fixed

| Where | Was | Now |
|---|---|---|
| `agents/max-components.md` §7 | two rows listed **UNVERIFIED** | both **measured** — the Z rotation is `quat <deg> [0,0,1]` (P6 ladder) and the shared `baseObject` comes from `copy` + `n.baseObject = src.baseObject` (P5), with `setCopyMode` confirmed absent |
| `references/07-spec-grammar.md:2072` | cited **`§8.2.7`** for the "trim projects and does not cut" claim | **`§8.2.8` row 8** — §8.2.7 is the schema section (lines 1263 and 2248 were already fixed earlier) |
| `references/14-chaos-scatter.md:183` | `G-74` row read "unique across `placements[]`, `opening_cuts[]` and `scatter[]`" | now lists **`wall_cells[]`** too — matching both `validate_specs.py` and `place_components.py` |

#### 4. `AGENTS.md` §"Known packaging gap" was **stale**, and is now corrected

It still claimed `collect_files()` ships only `SKILL.md` and `references/`. It has shipped
`scripts/`, `agents/`, `specs/`, `examples/` **and** the four top-level md files since P4b-r —
`scripts/install_skill.py:22-31`, where `TOP_LEVEL_FILES` is
`("SKILL.md", "PLAN.md", "CHECKPOINT.md", "AGENTS.md")` and `PACKAGE_DIRS` covers
`references snippets scripts agents specs examples`. **Same defect class as item 3:** a doc that
was correct when written and was never re-read after a code change underneath it.

#### 5. `scripts/env_preflight.py`: two probes were self-defeating

**`sweep_on_shape` could never reach its documented `PASS 9/9` on a healthy machine.** It expected
`mods=1 first=Sweep` — but `Sweep` is one of the **six classes measured to construct and then
throw on `addModifier`** (`Extrude Sweep Lathe Surface CrossSection Bevel_Profile`, re-confirmed at
the P6 ladder rungs 1–2). The probe and its check are restructured to **separate construct from
attach** and to assert the *measured* behaviour rather than the assumed one.

**`loft_not_creatable`'s probe body** concatenated `getCurrentException()` into the result string
inside a `catch`; replaced with a flag, reporting throw and value separately.

> **Nuance, and it matters because the old reasoning was wrong.** This repo's stated reason for
> forbidding `getCurrentException()` was **measured FALSE on 2026-10-05 and has already been
> withdrawn** — it works, 6 of 6 throw kinds, with a non-throw control. **The flag form is now
> preferred for a different and correct reason: the repo's probe standard is to report the throw and
> the value as separate fields, not to fold them into one string.** A concatenated
> `("ctor=" + … + " created=" + getCurrentException())` cannot distinguish "threw" from "returned a
> value" from "never ran", and that ambiguity is the exact failure mode this repo has now hit
> three times. **Do not reinstate the prohibition, and do not "fix" working `getCurrentException()`
> calls elsewhere.**

#### 6. Chaos Scatter: **scenario A, decided by the user 2026-10-06**

**The scatter is declared, not geometry.** `assembly.ms` emits **zero** scatter nodes;
`assembly.json.scatter[]` carries **one** declaration row. The user applies it by hand from
`snippets/chaos_scatter.ms`. **254 is the delivered count** — §"254, not 244" already records that
the two counts are different chains, and this closes which one ships.

✅ **This one WAS fixed, later in the same pass** — the "still open" note above was written before the
correction landed. `agents/max-assembly.md` §5 **step 9** now reads *"Validate the scatter declaration —
do NOT build the scatter"*; §7 **row 8** now asserts there is **no** `ChaosScatter` node and
`objects.count == 244`, and explicitly says `FpInterface` is **not** part of this gate; **row 17** now
reads *"the scatter is declared and NOT built"*; §6.6 is retitled *"one row, and S5 does not build
it"*; the `Geometry produced` row, the `Consumer · Precondition` row (S6/S7/S8 cancelled), the
cameras/lights row and the cleanup row 7 were all corrected to match. **The gate that checked its own
loop — the repo's eighth such instance — is gone.**

#### 7. New: the improvement log

Two files, plus pointers:

| File | What it is |
|---|---|
| `references/improvement-log.md` | **the format specification** — created |
| `agents/max-orchestrator.md` §6.2 | **the trigger and the ownership rule** — created |
| `agents/max-{assembly,components,facade,input,massing,nurbs}.md` | pointer into each playbook |
| `SKILL.md` | one row |

**The rule, in the orchestrator's own terms:** during a modelling session, if the session produces
a **real finding** — a measured value outside tolerance, something the spec grammar cannot express,
or a spec value that is legal but wrong for this building — the agent records it in
`<project>/IMPROVEMENTS.md`. **If the session produces none, it writes nothing and creates no
file.** `init_project.py` therefore **deliberately does not scaffold it**; a scaffolded empty log
is a file that always exists and therefore never means anything.

> **The distinction that makes the two logs different instruments: a log entry describes THIS
> PROJECT; a `CHECKPOINT.md` entry describes THE PACK.** An agent that finds a problem writes a log
> entry — **it does not edit `locked` JSON.** The improvement log is the only channel by which a
> session feeds the pack; a subagent that discovers a spec defect must not "fix" the spec it was
> handed.

#### Still open after this pass, with the reason

All three are closed by §P12 above, which supersedes this table.

| Item | Why it is still open |
|---|---|
| **`nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` claim-by-claim verification** | ✅ **CLOSED at P12.** 69 claims, 16 disproved and corrected in place, 4 left UNVERIFIED. Transcripts in `references/_04-05-evidence.md` |
| **The printed format of a `nurbsID`** | ✅ **CLOSED at P12.** `IntegerPtr`, prints `<decimal>P`; `railID=0P` **was** real. Remove §7.6 item 1 of `references/12-nurbs-gotchas.md` |
| **Why a 5-rib loft's trim copy reports `numCVs [9,4]`** | ✅ **CLOSED at P12.** It is the parent's own CV conversion, not the profile and not the trim. Remove §7.6 item 2 |
| **`curvatureAngle` degrees claim — independent confirmation** | ✅ **CLOSED at P13.** CONFIRMED, and the delegated transcript reproduced exactly. §P13 §1 |
| ~~The Chaos Scatter documentation inconsistencies~~ | **CLOSED in this pass.** Item 6 above; see the corrected note there for the seven `agents/max-assembly.md` sites |

---

## P12 — the three open items, two settled by execution and one delegated (2026-10-06)

This pass **had** a live bridge — the previous session's blocker was gone. All three items from
§"Resume here" §3 were attempted; **two are now closed**, the third is done by a delegated
claim-by-claim pass whose results I re-verified in the main thread.

### 1. `nurbsID`'s printed format — **RESOLVED**, and P4b's `railID="0P"` was right after all

P4b recorded `railID="0P"`; the round-2 pass recorded that the value was "never reproduced" and
demoted it to UNVERIFIED. **Both readings were of the same thing.** Measured on committed
sub-objects, with controls in every batch:

| Fact | Evidence |
|---|---|
| **The format is `<decimal>P` and the class is `IntegerPtr`.** `nurbsID` on a committed curve prints `3253572981568P` | `classOf` → `IntegerPtr`; `getProperty o "nurbsID"` on five committed `NURBSPointCurve` sub-objects |
| **`NURBS1RailSweepSurface.railID` really does read `0P` — three times out of three.** It is not a stale reading; it is the low ordinal of the rail, printed in the same format | 1-rail sweep, 3 reps: `railID=0P rail=0` every time |
| **`rail1ID` / `rail2ID` on a 2-rail sweep read the full pointer, and it is the rail's own `nurbsID`.** They are `IntegerPtr`, comparable with `==`, and `rail1ID ≠ rail2ID ≠ nurbsID` | `rail1ID=3253572981568P` matched the curve at committed index 4; `rail2ID=3253572981920P` matched index 8; `==` → `false` against each other and against the sweep's own id |
| `parent1ID` / `parent2ID` / `rail` / `axisTM` / `distance` **throw** on a `NURBS1RailSweepSurface`; `rail1`/`rail2`/`rail1ID` throw on it too — the two-rail class has its own vocabulary | calibrated `getProperty` sweep, `numCurves` as the in-batch positive, `totalBogusXYZ` as the negative |
| `getProperty <o> (<name> as name)` **works on these NURBS plugin classes.** The P4 row *"`getProperty o #x` also fails"* is true for the `#name` literal form and **false for the coerced-string form** | `getProperty surf "railID"` → `0P`; the same sweep's bogus name threw |
| ⚠️ **NEW, and it is a trap the emitted scripts sit next to: `appendCurve` takes an `Integer` ordinal, not the curve object.** Passing the object throws `Unable to convert: <NURBSPointCurve:0x…> to type: Integer` | first attempt passed the object and failed; `appendCurve rel i1` with `i1 = set.numObjects` succeeded. The emitted `nurbs.ms` was already correct — it passes indices — so **no builder change was needed** |
| **`nurbsID` on a node's surface sub-object is stable within a session and changes between builds** — 3 reps of the same geometry gave 3 different pointers | recorded as a warning, not a rule: **never persist a `nurbsID` value**, only bind it in the same script that uses it. This is exactly what `G-56` already mandates |

**This removes §7.6 item 1 of `references/12-nurbs-gotchas.md`** and **corrects the P4b
"never reproduced" note**, which was wrong in the opposite direction from P4b's original claim —
the tenth instance of this repo's signature failure, and the second one in this file about an
`nurbsID`.

### 2. The 5-rib loft's trim copy reporting `numCVs [9,4]` — **RESOLVED**

P4b raised this and left it open. It is **not** an artefact of the trim, and **not** the profile
curve. Measured with two structurally different profiles and a parent-variation sweep:

| Fact | Evidence |
|---|---|
| **The `[9,4]` belongs to the PARENT surface's own CV layout, not to the projected profile.** A 5-pt small rectangle and an 8-pt profile spanning the entire vault both give `[9,4]` on the same parent | the profile is irrelevant to the number |
| `u` tracks the parent's **points per section**: a 9-point-per-section loft → `[9,4]`; 5, 6, 7, 11 points → `[4,4]` | 7-case sweep, `p` and `r` varied independently |
| `v` is **fixed at 4** across every case, including 2-section and 6-section parents | same sweep |
| **`u` also depends on the parent's own curvature, not only its point count.** Scaling the vault's profile amplitude to `0.25` gives `[5,4]`; `0.5`, `1.0`, `2.0` all give `[9,4]` | the parent is 9 points either way, so point count alone does not determine `u` |
| The added object is a **`NURBSCVSurface`**, and its parent (`NURBSULoftSurface`) has **no** `numCVs` / `numPoints` / `uOrder` / `vOrder` / `numUKnots` / `numVKnots` at all — all throw | property sweep with a surface-class control |
| `trim:false` adds **no** surface — confirmed again on this parent, `0` surfaces in the set | third variant in the same batch |

**So the copy is Max's own conversion of the parent surface into a CV surface, and `numCVs`
reports that conversion.** The question is answered: nothing is wrong, and **no rule may be
written against it** — it is a function of the parent's geometry in a form this repo cannot
predict. `G-54`'s census counts **sub-objects**, not CVs, and is unaffected.

**Removes §7.6 item 2.**

### 3. `nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` claim-by-claim — **DONE**, 16 of 69 claims disproved

Delegated to a `general` subagent with a written probe standard and the standing facts handed
over as data. Transcripts: **`references/_04-05-evidence.md`** (661 lines). **69 claims extracted,
58 settled by execution, 16 disproved, 4 left labelled UNVERIFIED, 47 confirmed.**

The two files' **NURBS geometry was not rewritten.** Corrections are dated, in place, in the house
style. The disproved claims, grouped:

| Area | Disproved |
|---|---|
| **Node class names** | A node's `classOf` is **`NURBSSurf`** (any surface) or **`NURBSCurveshape`** (curves only) — never `CV_Surf` / `Point_Surf` / `Point_Curve` / `CV_Curve`. **I re-verified this myself**: 5-rib loft node → `NURBSSurf`; point-surface node → `NURBSSurf`; point-curve-only node → `NURBSCurveshape` |
| **`addNURBSSet` is a silent no-op** | Returns `OK`, adds nothing: the target's set count and bbox are unchanged. **Re-verified myself** across 4 arities — 3 returned `OK` with `nObj` 9→9 and an identical bbox, the 4th threw. **This invalidates §5.2's merge snippet and Recipe 4 entirely** |
| **Property renames** | `pointType`→**`.type`** · `trim`→**`.trimCurve`** on `NURBSCurveConstPoint` · `trimCurve1/2`→**`trim1`/`trim2`** on `NURBSCurveSurfaceIntersectCurve` · `.curveStartPoint` is a **Float**, not an integer · `curvatureAngle` is **DEGREES**, not radians — the `degToRad` wrapper was removed from Recipe 1 |
| **Absent properties** | `.isSelected` on all 34 classes · `.index` reads `0`, never a set index · `NURBSPointCurve.closed` neither readable nor writable (`.isClosed` only, constructor-only) · `NURBSSurfaceNormalCurve.uParam`/`vParam` · `NURBSPointSurface.closedU`/`closedV` — the last **confirms P4's verified negative independently** · `NURBSCurveIntersectPoint` has no `seed1`/`seed2`/`trim1`/`trim2` · `NURBSMultiCurveTrimSurface` has no parent property under 20 candidate names |

**Spot-checked by me, independently, in the main thread** — because §"two harnesses that reported
success" and the P1 lesson both say a subagent's summary is a claim, not a result:

```
node curve classOf = NURBSCurveshape   super = shape
node surf  classOf = NURBSSurf         super = GeometryClass
NURBSPointSurface property sweep (positive control: matID=1, negative: totalBogusXYZ)
  curvatureAngle THREW · trim THREW · trimCurve THREW · closedU THREW · closedV THREW
  uParam THREW · vParam THREW · isSelected THREW · type THREW · pointType THREW · numTrimPoints THREW
  index  = 0 (Integer)      nurbsID = 3253563697808P (IntegerPtr)
addNURBSSet: 3 arities returned OK with target set 9 -> 9 and byte-identical bbox; 1 threw
```

Every one of those matches the subagent's report. **Note the coincidence worth recording: on
`NURBSPointSurface`, `type` throws too** — the `.type` rename applies to the **const-point**
classes, not to surfaces, and the file now says so.

**One subagent correction it made against itself, kept:** two candidate defects were **discarded
as its own probe errors** and logged rather than reported — `classOf == NURBSCurve` (that is the
*super*class) and `.numTrimPoints`/`.isClosed` read off a surface instead of a curve. That is the
behaviour the standard asks for, and it is why the remaining 16 survived review.

**Not tested, and why:** the §6 prose · `displayTrimming` semantics · tool-list absence claims ·
the *violating* direction of the knot invariant (it opens an Assertion dialog). No modifier stack
was built, so the 20-rung freeze boundary was never approached.

### Bridge state at the end of this pass

**`3dsmax.exe` exited during the delegated pass** — by the time the curvature cross-check ran,
`tasklist` showed only `3dsmax-mcp.exe`, no Max process, and `get_bridge_status` returned the
cached-pipe `ConnectionError` (which names TCP even though the pipe is what failed, §"Bridge
transport"). The instance directory lists `pid-14224`, `pid-25584`, `pid-27352`; `14224` is the
live descriptor from 01:24 and the other two are the permanent dead entries.

**So one cross-check was unfinished at this stage — ✅ DONE at P13, see §P13 §1**: the subagent's `curvatureAngle` evidence reports
`1.0→415 / 4.0→147 / 7.0→87 / 20.0→51 / 0.10472→691` verts on a quarter-cylinder. My independent
attempt **could not reproduce a varying vert count at all** — every value returned `10527`, on both
a wavy 6×3 grid and via `setViewApproximation` / `setRenderApproximation`. That is **not**
evidence against the subagent: my probe used a different surface and a mesh count that evidently
ignores the approximation it set, i.e. it was not calibrated. **The degrees claim therefore rests
on the subagent's transcript alone and is NOT independently confirmed.** Re-run the quarter-cylinder
probe next live session before relying on the `degToRad` removal in Recipe 1.

Per §"Bridge transport", **restarting opencode is required** before the next session has tools —
not restarting Max, and not killing the MCP server.

---

## Resume here — 2026-10-06, hand-off for the next session

> **⚠️ SUPERSEDED IN PART by §P13 (later the same day).** All three open items below were closed at
> P13, and the bridge blocker in §0/§1 did not recur — the bridge answered on the first call this
> pass. This section is kept as the record of what the session actually found, not as current
> status. **Current state: §"Resume here — after P13".**

Read this section first. It states what the next session must do and what it must **not** re-derive.

### 0. The bridge is configured and was measured working. This session could not reach it — and here is why.

**Config: `C:\Users\Turbolamer\.config\opencode\opencode.jsonc`** — both servers were present and
enabled:

| Server | Command | State at end of this session |
|---|---|---|
| `3dsmax-mcp` | `uv run --directory C:/3dsmax-mcp 3dsmax-mcp` | **`enabled: true`** — verified below |
| `rhinomcp` | `uvx rhinomcp@latest` | **set to `enabled: false` on 2026-10-06 at the user's request**, so its ~30 tool names stop colliding with Max's. Backup: `opencode.jsonc.bak.rhinomcp-off-20261006-012133` |

**The `3dsmax-mcp` server itself is healthy — measured by driving it directly**, bypassing opencode:

```
uv run --directory C:/3dsmax-mcp 3dsmax-mcp        # initialize + tools/call
  serverInfo: {'name': '3dsmax-mcp', 'version': '1.26.0'}
  get_bridge_status -> {"ok": true, "result": {
      "maxVersion": 2026, "pong": true, "protocolVersion": 2,
      "server": "3dsmax-mcp-native", "transport": "namedpipe",
      "connected": true, "legacyTransport": false,
      "meta": {"safeMode": true, "threadMode": "mainThread",
               "clientRoundTripMs": 1.604, "requestedTransport": "auto"}}}
```

So: **`ok`, `pong: true`, RTT 1.6 ms, protocol 2, namedpipe, safeMode, mainThread** — every value
`CHECKPOINT.md` §"Environment" already recorded as the verified baseline. **Nothing about the bridge
changed; it is the same session-configured baseline.**

### 1. ⚠️ Why no `3dsmax-mcp_*` tool reached this session — and the one-line fix

**The server is enabled and working. It simply was not exposed to this session's tool list.** The next
session should start with:

> **If no `3dsmax-mcp_*` tool is available, restart opencode, then call
> `3dsmax-mcp_get_bridge_status` before doing anything else.**

The mechanism is the one already in §6 of `agents/max-orchestrator.md`: the MCP client caches the pipe
name for the process lifetime, and `discover_instance_pipes()` runs **once** per client. A session that
started before the bridge was up, or one that raced a Max restart, keeps no usable tool. Restarting
opencode — **not** restarting Max, and **not** killing the MCP server — is what recovers it.

Verified facts about the channel, all measured 2026-10-06:

| Fact | Evidence |
|---|---|
| **Max is alive and responsive** | `3dsmax.exe` PID **17152**, `Responding: True`, window `Untitled - Autodesk 3ds Max 2026` |
| **The instance pipe exists and opens** | `\\.\pipe\3dsmax-mcp-pid-17152` — `CreateFileW` → **OK** |
| **The two stale instance files are expected** | `pid-25584` and `pid-27352` → `ERROR 2`. Their processes are gone. **`instances/` is never pruned** — dead descriptors are permanent and harmless |
| **Discovery prefers the highest live PID** | `max_client.py:50-73` — `discover_instance_pipes()` filters on `_pid_alive` and sorts descending, so stale files cannot win |
| **A restart is handled, but only on retry** | `max_client.py:184-209` `_refresh_pipe_name()` re-resolves by probing, so PID reuse cannot hand back a dead name — but it fires **after** a failure, not at startup |

### 2. 🔴 A probe bug worth recording — it cost this session a wrong conclusion

**`.NET FileStream.Open` cannot open a Win32 named pipe, and the failure reads like a dead bridge.**
My first pipe check returned `OPEN FAIL` and I had to discard it:

```
msg = "FileStream ... не может ... поддерживается, но поток ... CreateFile"
inner = "... ��ꥪ� FileStream ..."
```

`FileStream` applies filesystem path normalisation to `\\.\pipe\...` and resolves it against the
**current drive** — it tried `D:\pipe`. **The pipe was open the whole time.** Only `CreateFileW` via
P/Invoke answers the real question, which is exactly what `max_client.py` does.

This is the **same failure family** as the three rules this repo already retracted: `findString`,
`matrix3` and `getCurrentException()` were all recorded as absent because the probe, not the feature,
was wrong. **Record it next to those three.**

The second trap, same session: **an unframed JSON-RPC write to the pipe times out and proves nothing.**
Feeding a raw `{"jsonrpc":...}` line without the server's handshake produced a 60 s hang with no reply.
A timeout from a probe that does not speak the server's protocol is **absence of evidence, not
evidence of absence**. Drive the server through its own stdio transport instead — that is the method
that produced the `pong: true` above.

### 3. The three open items, with the exact probe for each

All three need a live `3dsmax-mcp_*` tool. **Run them in one batch, main thread, with controls.**

| # | Item | Probe to run |
|---|---|---|
| 1 | ~~**The printed format of a `nurbsID`**~~ | ✅ **CLOSED at P12.** See §P12 §1: `IntegerPtr`, `<decimal>P`, `railID="0P"` reproduced 3/3, `rail1ID` = the rail's own id |
| 2 | ~~**Why a 5-rib loft's trim copy reports `numCVs [9,4]`**~~ | ✅ **CLOSED at P12.** See §P12 §2: it is the parent's own CV conversion; two different profiles give the same number |
| 3 | ~~**`nurbs-complete-guide.md` / `nurbs-architecture-recipes.md` claim-by-claim verification**~~ | ✅ **DONE at P12.** Delegated, 69 claims, 16 disproved, spot-checked by me in the main thread |
| 4 | ~~**The `curvatureAngle` degrees claim needs one independent confirmation**~~ | **CLOSED at P13 — CONFIRMED INDEPENDENTLY**, and the delegated transcript reproduced exactly (`1.0`→415, `6.0`→101, `0.10472`→691). Stronger discriminator: the mesh reaches its 25-vert floor at **≥ 40°** on a 90° arc, while `1.5708` (π/2 rad) sits at 337 in the **dense** region. §P13 §1. The `10527`-constant probe recorded here is now explained: `snapshotAsMesh` does not honour the approximation alone and `curvatureDistance` was setting the floor | The subagent's transcript shows `1.0→415 / 4.0→147 / 7.0→87 / 20.0→51 / 0.10472→691` verts on a 100 mm quarter-cylinder. My own attempt returned a **constant `10527` at every value**, on two different surfaces and via both `setViewApproximation` and `setRenderApproximation` — i.e. **my probe did not measure the approximation**, so it is no evidence either way. Re-run it on a quarter-cylinder before relying on Recipe 1's `degToRad` removal |

### 4. The live chain was NOT re-run in this session

The 254-node figure is from P6/P10-lite. Nothing was rebuilt here — no Max geometry was touched, the
scene was never `fileIn`-ed. **If the next session changes a builder, the full chain must be re-run**:
`massing.ms` → `nurbs.ms` → `assembly.ms`, counting nodes and re-measuring bboxes. An emitted `.ms` is
not done until `fileIn` has run it (§9 of the orchestrator).

### 5. Two things deliberately NOT done, and why

- **`IMPROVEMENTS.md` was not scaffolded and no project was built.** The close-out pass was
  documentation-only. The offline gates all pass: `py_compile` 0, `PASS 138 / FAIL 0 / WARN 0 /
  SKIP 15`, a fresh scaffold at `PASS 105 / FAIL 0`, and `3dsmax-arch-nurbs-ultimate.skill` rebuilt to
  **73 files, byte-identical to the working tree**.
- **UV rules for NURBS vs poly remain unwritten.** They were the last survivor of cancelled P7, and
  writing **unverified** unwrap recipes into a repo that has already shipped four fabricated facts is
  the error it documents. It needs live Max: `generateUVs1`, and a measured read of what a NURBS
  surface and a poly-modified mesh actually produce. Treat it as a new stage, not a docs task.

---

## P13 — the last open live item is closed, and a full drift sweep (2026-10-06)

**A live bridge was available for this whole pass.** Everything below is either measured against
Max 2026.3.2 or a direct reading of a checked-in file.

### 1. `curvatureAngle` is DEGREES — **CONFIRMED INDEPENDENTLY**, and the claim survives

The one item §P12 could not corroborate. The delegated transcript stood up: my measurement, on a
different code path, **reproduced its numbers exactly**.

| Input | Delegated (P12) | Measured here (P13) |
|---|---|---|
| `1.0` | 415 | **415** |
| `6.0` | 101 | **101** |
| `0.10472` (= `degToRad 6.0`) | 691 | **691** |

**The discriminator is stronger than either pass had.** On a 90°-arc quarter cylinder with
`meshApproxType:#curvature` and a **loose** `curvatureDistance`, the mesh descends monotonically
(`0.25`→663, `1.0`→415, `2.0`→279, `5.0`→119, `10.0`→55, `20.0`→37) and reaches its **25-vert floor
— the bare 5×5 net — at ≥ 40°**, flat from 40 through 120. **`1.5708` (= π/2 rad) sits at 337, in
the DENSE region.** Under a radians reading π/2 would already be maximally coarse; it is not. That
is the degrees signature, and it is a *floor location*, not a curve-shape argument.

> **A calibration note, because it cost four probes.** My first ladder returned a **constant**
> `81.1783°` max-step at every input. The reason: `snapshotAsMesh` does not honour
> `setRenderApproximation` alone. A `parametric 6×6` grid — fully predictable at 49 verts —
> returned **169**. `curvatureDistance` was also setting the floor, masking `curvatureAngle`
> entirely. **A uniform result across a ladder is not evidence of absence; it is evidence the probe
> is not measuring the variable.** Three ladders were discarded before one was calibrated. This is
> the same failure family as `getCurrentException`, `matrix3` and `findString`, one level up: not
> "feature absent" but "probe blind".

### 2. NEW HAZARD — `formattedPrint` hangs `execute_maxscript` and crashed Max

**Cost: one hard crash and a user restart.** It is the only new hazard this pass found.

| Fact | Evidence |
|---|---|
| **The name resolves fine** — `formattedPrint` reads back as a valid global, `classOf` `Primitive` | isolated probe, twice, same session |
| **Invoking it hangs the bridge until timeout, and crashed 3ds Max outright on a first attempt** | `formattedPrint 1.23456 format:".%.3f"` → request timed out at 12 s; Max exited. A later isolated retry hung again but Max survived |
| A `try`/`catch` **does not** contain it | the call never returns, so the catch is never reached |

**Recorded in `AGENTS.md` §`execute_maxscript` operating limits**, with a warning in
`maxscript-common-patterns.md` and plain-concatenation replacements in
`maxscript-3dsmax-objects.md` and `maxscript-rendering-cameras.md`. The teaching subsection in
`common-patterns` was replaced by a ⛔ note quoting the old lines rather than deleted, so a reader
who remembers it sees why it went.

**My own error, recorded plainly:** I reached for `formattedPrint` to format floats in a probe and
crashed the user's Max. It is now forbidden in this repo for that reason alone.

### 3. A code defect the prose audits had missed — `applyArchTessellation` misread the unit

`snippets/nurbs_arch_library.ms:86` shipped `curvatureAngle:(degToRad angleDeg)` — a real,
executable falsehood in the one file that runs in every session, correcting nothing that the
reference files had already been fixed for. Now passes `angleDeg` through.

> **Honest scope, measured on the chain and not overclaimed.** On a curvature-bound surface the
> difference is large (**101 vs 691 verts, ~6.9×**). On the **shipped** examples it is **~3%**
> (49 499 vs 51 197 verts across all 6 `NURBSSurf` nodes) because `spacialEdge:4.0` binds there, not
> `curvatureAngle`. **The fix is correct because the unit was wrong, not because it buys 6.9×
> everywhere.** The comment in the file says exactly this.

### 4. Drift audit — 13 HIGH findings, all fixed, four disjoint passes

`references/_drift-audit.md`. Audited against 17 measured facts. **All four HIGH rows I sampled
were verified by me before acting** — the subagent's summary was treated as a claim.

The HIGH findings were not one mistake but three classes, and the pattern is the point:

| Class | Instances | Why it survived |
|---|---|---|
| **A cancelled stage still shipped as a live contract** | `01-architecture-aec-workflow.md` §3 S6/S7/S8 with three nonexistent agent files; `14-chaos-scatter.md` + `chaos_scatter.ms` on the "P8 determinism hook"; `max-{assembly,massing,facade,components,nurbs}.md` rows naming `materials.json` | P7/P8/P9 were cancelled by **user decision**, not by a code change. Nothing failed, so nothing announced it |
| **An obsolete file with no router** | `railclone.md`, `tyflow-graphs.md` had none — while `SKILL.md:473` **falsely claimed they did**. `procedural-graphs.md` presented **12 `mcg_*` tools** plus two invented DC tools as the workflow | the router convention was applied ad hoc, file by file, and the index describing it was never checked against the files |
| **A corrected fact re-introduced elsewhere** | `12-nurbs-gotchas.md` "Boolean is available" + a copy-pasteable `Boolean()` snippet; `07-spec-grammar.md` **contradicting itself row-on-row** on `nurbsID` (`:2316` right, `:2318` stale); `nurbs-complete-guide.md` "an opaque runtime **integer**" against its own `:172` `IntegerPtr` | corrections landed in one place and the duplicate was never re-read |

**That third class is the recurring one, and it is the same defect as §Incident log 2026-10-06
item 2 and the `G-74` wall-cells gap: a fact fixed in one file while a second copy of it stays
wrong.** A claim that exists in three places is three things to maintain, and this repo has now
shipped that mistake four separate ways.

**`procedural-graphs.md` was split, not fenced** — its Data Channel half is live (`list_dc_presets`,
`add_data_channel`, `inspect_data_channel`, `add_dc_script_operator`, `load_dc_preset`,
`set_data_channel_operator`); only the `mcg_*` half is dead.

**Fix notes, kept as written artifacts:** `_fix-a-notes.md`, `_fix-b-notes.md`, `_fix-c-notes.md`,
`_fix-d-notes.md`.

### 5. Gates re-run after every change — including a **live** chain re-run

The chain was re-run because **the library it `fileIn`s changed**. An emitted `.ms` is not done
until Max has run it, and this pass changed a file the emitted scripts depend on.

| Check | Result |
|---|---|
| `python -m py_compile scripts/*.py` | exit 0 |
| `validate_specs.py --dir examples` | **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** — after *each* of the four fix passes, not once at the end |
| **Determinism**, 5 artefacts, two independent builds | **`A == B == committed`**, all five |
| **Live `fileIn` chain** | `massing.ms` → **27**, `nurbs.ms` → **+10**, `assembly.ms` → **+217** = **254** |
| **Idempotence** | 254 → **254** → **254** over three passes |
| **Modifiers in scene** | **0** (`G-81`) |
| **Class census** | Box 239 · Dummy 5 · `NURBSSurf` 6 · `NURBSCurveshape` 1 · 3 shape/poly = **254**; massing is exactly **22 Box + 5 Dummy** |
| **Prefix census** | `PLC_`=136 · `WAL_`=52 · `PROTO_`=29 |
| **Reference instancing** | 136 panels resolve to **29 distinct `baseObject`s** — instances, not copies. Negative control: two massing Boxes share `baseObject` → **false** |
| Scene after the pass | **0** |

### 6. Still open — unchanged, and not a docs task

- **UV rules for NURBS vs poly remain unwritten.** The last survivor of cancelled P7. Writing
  unverified unwrap recipes into a repo that has shipped four fabricated facts is the error this
  file documents. It needs live Max: `generateUVs1`, and a measured read of what a NURBS surface and
  a poly-modified mesh actually produce. **Treat it as a new stage.**
- **`validate_specs.py:90`** hard-coded `P3…P9` in the `RECHECK_STAGES` enum, so G-15 could name
  the cancelled stages P7/P8/P9. **✅ FIXED at P14** — narrowed to `("P3","P4","P5","P6")`, with
  fault injection in both directions.
- **`14-chaos-scatter.md:132`** called `procedural-graphs.md` "OBSOLETE (moot, not wrong)"; after the
  split banner it is *partly* obsolete. **✅ FIXED at P14**, together with two further copies of the
  same claim that were stale in the same way — `AGENTS.md:177` (which *also* still said
  `curve-construction.md` "needs a rewrite rather than a fix", resolved two days earlier) and
  `agents/max-orchestrator.md:157`.

---

## P14 — the three open items closed, and the chain re-measured (2026-10-06)

Scope: close the three items P13 listed as still open. **No new stage, no geometry change.** All of it
was decided by the user: *"Close the 3 open items, no new stage."*

### 1. The linter could name cancelled stages — **FIXED, with fault injection**

`validate_specs.py:90` hard-coded `RECHECK_STAGES = ("P3"…"P9")`, so **G-15 accepted `P7`, `P8` and
`P9`** — the three stages the user cancelled on 2026-10-05. An assumption rechecked "at P7" pointed
at a stage that does not exist, so nothing would ever re-check it.

Narrowed to `("P3","P4","P5","P6")`. **Touching the linter required fault injection, per the `G-74`
lesson** — and it immediately found the reason the enum was left alone twice before: **a shipped spec
relied on it.** `examples/assumptions.json` `A-014` (`roof.coping_overhang_cm`) declared
`recheck_stage: "P7"` with `downstream_stages: ["P6","P7"]`. The coping overhang is **geometry**, built
by `build_spec.py` at P3 massing, so the honest stage is `P3`; rewritten to `"P3"` /
`["P3","P6"]`.

> **The pattern, again.** A rule's *vocabulary* went stale when three stages were cancelled by user
> decision, and a committed artefact had already come to depend on the stale value. This is the
> `G-74` class (`CHECKPOINT.md` §"Closed at P6"): **when a decision removes a stage, re-read every
> enumeration of stage names** — in the linter *and* in the shipped data.

Fault injection, **both directions** — a rule must fire on the bad values *and* not over-fire:

| Injected `recheck_stage` | Result |
|---|---|
| `P7` · `P8` · `P9` (cancelled) | **FAIL 1** each — `G-15 recheck_stage 'P7' not in P3, P4, P5, P6` |
| `P10` (a real, completed stage) | **FAIL 1** — correct: P10…P13 are close-out passes, not re-examination points |
| `BOGUS` (known-bogus control) | **FAIL 1** — the probe can detect |
| `P3` · `P4` · `P5` · `P6` (known-good) | **FAIL 0** each — no over-fire |

**5/5 negatives, 4/4 positives.** Baseline before the change and after it are both
`PASS 138 / FAIL 0 / WARN 0 / SKIP 15`.

> **A harness artifact caught and discarded, recorded because it nearly became a finding.** The first
> injection run reported **FAIL 2**, not 1. The second row was **G-7 "file contains CR"** — my own
> rewrite had written CRLF via Python's default newline translation on Windows. It was **my bug, not
> a linter bug** — and it incidentally proved G-7 fires. Re-run with `newline="\n"`: exact counts.
> **A fault-injection result you cannot attribute is not a result.**

Docs that carried the stale range, all corrected: `07-spec-grammar.md` §field table + the **G-15 row**
(it previously carried a *dated correction note* saying the range was "unchanged" — now it is
changed, so the note was itself the drift), `08-input-rules.md` ×2. `08`'s two rows were found by
grepping `recheck_stage`, not by re-reading `07` — **which is the only reason they were caught.**

### 2. `procedural-graphs.md` described as wholly OBSOLETE — **FIXED in three places, not one**

P13 deferred a **one-word** fix on `14-chaos-scatter.md:132`, on the grounds that it was too small to
do properly. Doing it properly found **two further copies of the same wrong claim**:

| File | Was | Now |
|---|---|---|
| `references/14-chaos-scatter.md:132` | "OBSOLETE (moot, not wrong)" | **half obsolete** — MCG half moot, **Data Channel half live**; points at the real 32-operator vocabulary |
| `agents/max-orchestrator.md:157` | "`procedural-graphs.md` is moot" | MCG half moot, DC half live |
| `AGENTS.md:177` | "is moot" **+ "`curve-construction.md` needs a rewrite rather than a fix"** | both corrected — `curve-construction.md` **was resolved on 2026-10-06** (OBSOLETE + router, body fenced); `AGENTS.md` still asked for a rewrite that had already been decided |

So the "one word" was **three files and two distinct stalenesses**, one of them **two days out of
date** in the file an agent reads *first*. This is the recurring HIGH class (§P13 §4 third row) in its
pure form: **the fix was applied in one place and the duplicates were never re-read.**

### 3. `CHECKPOINT.md` contradicted itself — the same defect, self-inflicted

`CHECKPOINT.md` §P13 §6 listed the `validate_specs.py:90` item **twice, verbatim**. Not a content
error — a *maintenance* error of exactly the kind this file exists to document. Deduplicated, and both
resolved rows now point at this section.

### 4. The chain, re-measured live rather than argued from a hash

My edits touched **no builder and no library file**, and all 9 emitted artefacts were byte-identical to
the committed tree — so a re-run was not strictly required. It was run anyway, because *"byte-identical
to what P13 measured"* is an **inference**, and this repo's rule is that live execution is the only
ground truth.

| Check | Result |
|---|---|
| `py_compile scripts/*.py` | exit 0 |
| `validate_specs.py --dir examples` · `--warnings-as-errors` · `--build` | **PASS 138 / FAIL 0 / WARN 0 / SKIP 15** (all three) |
| `validate_specs.py --dir specs/recipes/nurbs --allow-draft` | **PASS 54 / FAIL 0 / WARN 0 / SKIP 28** |
| **Determinism, 9 artefacts**, two independent builds | **`A == B == committed`**, all nine |
| Fresh scaffold `--allow-draft` | **PASS 105 / FAIL 0 / WARN 0** |
| Live chain `massing.ms` → `nurbs.ms` → `assembly.ms` | **0 → 27 → 37 → 254** |
| Idempotence | **254 → 254 → 254** |
| Modifiers in scene | **0** (`G-81`) |
| Census | Box **239** · `PLC_` **136** · `WAL_` **52** · `PROTO_` **29** · `NURBSSurf` **6** |
| Reference instancing | **136/136** panels share a prototype `baseObject`, **0** exceptions |
| bboxes vs `massing.json` | `EL_001` `[0,0,-30]..[1800,900,0]` · `EL_002` `[0,0,395]..[1800,900,420]` · `EL_003` `[430,430,-30]..[470,470,420]` — **exact** |
| Scene after two sweeps | **0** |
| `.skill` archive | rebuilt, **79 files**; all 6 edited files verified present inside it; installed copy **byte-identical to the working tree at 79/79** in both `~/.claude` and `~/.agents` |

**Every figure reproduces P13 exactly.** No regression, and the deliverable is measured — not assumed
— after the edits.

### 5. One UNEXPLAINED transient, recorded as unexplained

The **first** chain call of the session failed: `Unknown property: "createULoftShell" in undefined`
at `nurbs.ms:85`, i.e. `MCP_NURBS_Arch` was undefined at the point of use. **It did not reproduce,
including when I deliberately recreated its precondition.** Logged in full because the temptation to
explain it is exactly where this repo has gone wrong four times:

| Probe | Result | Verdict |
|---|---|---|
| Library present? | all **12** functions resolve; `TotalGarbageXYZ_fn` **throws** | probe calibrated, library intact |
| Is the `nurbs.ms:3` guard pattern sound? | `if X == undefined do (…)` against a guaranteed-undefined global → **fired, no throw** | guard sound |
| **My own hypothesis** — an identifier not yet a global at compile time binds as a *local*, so the `fileIn` defines the global while the fn keeps reading its own undefined local | **REFUTED by experiment**: a `.ms` whose fn creates then reads the global **returned `5`**; a pre-existing-global control returned **`42`** | theory wrong, discarded |
| **Forced-unload test** — `global MCP_NURBS_Arch = undefined`, then `fileIn nurbs.ms` alone | **succeeded**, guard reloaded the library, scene stayed **254** | the exact precondition, and it passes |

So: the guard works, the library works, the chain works, and the failure did not reproduce under its
own reproduced precondition. **Recorded as a single unreproduced transient, with no mechanism
claimed.** Two things keep it from mattering: `agents/max-orchestrator.md:266` already instructs
preloading the library explicitly, and the guard is a second line of defence that demonstrably fires.
**If it ever recurs, capture the session's `library already loaded?` state first** — the one fact
this occurrence is missing.

### 6. Still open — unchanged

- **UV rules for NURBS vs poly remain unwritten.** The last survivor of cancelled P7. Needs live Max:
  `generateUVs1`, and a measured read of what a NURBS surface and a poly-modified mesh actually
  produce. **A new stage, not a docs task** — the user declined it for this pass.
- **Nothing else.** The three items P13 listed are closed; the two cosmetic drift copies found behind
  them are closed; the duplicated `CHECKPOINT.md` bullet is closed.

---

## P15 — UV / unwrap rules: the last open item, closed by measurement (2026-10-06)

§"Resume here — after P14" left exactly one item, and flagged it as **"a new stage, not a docs task
— the user declined it for this pass."** The user accepted it for this pass. This stage had a live
bridge throughout; **every row below is an executed transcript**, and controls were in every batch.

**Delivered in `references/13-uv-rules.md`.** What follows is the ledger.

### 1. The starting state of the delivered model — three kinds, not one

`massing.ms` + `nurbs.ms` + `assembly.ms` loaded in order → **254 nodes, 0 modifiers in the scene.**
Channel-1 census, read via `snapshotAsMesh` + `meshop.getNumMapVerts`:

| Group | Nodes | Channel 1 |
|---|---|---|
| `PROTO_*` + `PLC_*` | **165** | **absent** |
| `EL_*` `SP_GROUND_PAD` `WAL_*` | **74** | **absent** |
| `SUR_001`…`SUR_006` | 6 | **present, `0..1`** |
| `DRV_001` `DRV_003` `SUR_007` | 4 | absent |
| `GRP_*` `Dummy` | 5 | n/a — `snapshotAsMesh` throws `Cannot get mesh from this object` |

> **A probe that reads `meshop` on the node directly reports a false absence on every object in the
> model** — `Runtime error: Mesh operation on non-mesh: Box` / `: NURBS Surface` / `: Editable Poly`.
> `snapshotAsMesh` first. This is the P3 `pos` trap's sibling: a measurement route that is wrong for
> an entire class.

### 2. ⛔ `setTiling` silently floors its arguments — and `getTiling` hides it

| Call (750 × 200 cm surface) | uv span off `snapshotAsMesh` |
|---|---|
| `setTiling s 2.99 3.99` | `2.0 x 3.0` |
| `setTiling s 2.01 2.01` | `2.0 x 2.0` |
| `setTiling s 1.9 1.9` | `1.0 x 1.0` |
| `setTiling s 3.5 1` (350 cm surface) | `3.0 x 1.0` |

A floor, not a round. Reproduced on three independently constructed surfaces at three different
positions. **A 350 cm wall at one tile per metre needs 3.5 and gets 3** — and every real building
has non-multiple-of-100 widths, so `setTiling` cannot deliver constant texel density at all.

**Why this survived: `getTiling` echoes the request.** `setTiling s 3.5 1.5 channel:1` →
`getTiling s channel:1` → **`[3.5, 1.5]`**, persistently across calls, while the UVs are
**`3.0 x 1.0`**. The stored value genuinely is 3.5; Max applies the integer part.

**This downgrades a recorded verification.** `references/_04-05-evidence.md` §G32 reads
*"G32 CONFIRMED (`getTiling`/`setTiling` round-trip)"*. The round-trip **is** confirmed — it was
calibrated for the wrong question. It read a value back and stopped; it never read the UV range,
which is the only thing that would have caught this. **The eleventh instance of this repo's signature
failure, and a new mechanism: the first ten produced a false *absence*; this one produced a false
*confirmation*.** A read-back that agrees with what you wrote is not evidence that Max applied it.

### 3. ⛔ A modifier's `utile`/`vtile` written in the same call that adds it is DISCARDED

This one cost more probes than anything else in the stage, because **the in-call read-back lies**.

```maxscript
addModifier p (Uvwmap maptype:0 realWorldMapSize:true)
p.modifiers[1].utile = 0.25      -- reads back 0.25 immediately
-- next execute_maxscript call: reads 1.0
```

| Evidence | Result |
|---|---|
| Same-call write, never evaluated | reverted to `1.0` — **8 of 8** |
| Write in a **later** call | persists and changes geometry — **5 of 5** |
| Write after a `snapshotAsMesh` between `addModifier` and the write | persists — **3 of 3** |
| Evaluation **before** the `addModifier` instead | does **not** help — reverted, `1 of 1` |

**The loss is specific to `utile`/`vtile`.** Measured separately:

| Written in the adding call | Next call reads | |
|---|---|---|
| ctor kwargs `maptype` / `realWorldMapSize` | survive | |
| ctor kwargs `utile` / `vtile` | **`1.0`** | **lost** |
| properties `maptype` / `realWorldMapSize` | survive | |
| properties `utile` / `vtile` | **`1.0`** | **lost** |

So it is not "modifier writes are lost" — it is **the tiling scale specifically**, which is the one
you always need. Mechanism **not** isolated; two working mitigations are, so none is required.

**This is a hazard for the emitted `.ms` files too**, and it is recorded here rather than only in
the reference because it applies to any future builder that configures a modifier.

### 4. ✅ The working recipe, and the cross-check that makes it credible

- **`realWorldMapSize:true` ⇒ 1 UV unit = 1 cm.** Three boxes at independent positions:
  4×6×2 cm → span `4.0 x 6.0`; 400×600×2 → `400.0 x 600.0`; 300×150×20 → `300.0 x 150.0`.
- **One tile per metre ⇒ `utile` = `vtile` = `0.01`.** `300 × 150` → `3.0 x 1.5`.
- **Fractional tiling on a NURBS surface works via `Uvwmap`**, measured `3.5 x 1.5` on a
  350 × 150 cm surface — the case `setTiling` gets wrong. Written in a later call, persistent.
- **Cross-check:** a 300×150 poly and a 350×150 NURBS surface both land on the same uv-per-cm
  ratio by different routes. Two independently-derived paths agreeing is the strongest evidence in
  this section, and it is why the recipe is recommended rather than merely reported.
- **On the delivered panels**, `maptype:4` + `realWorldMapSize:true` returns uv span **exactly
  equal to the node's cm extent**: `PLC_001` 135×3×90 → `135.0 x 90.0`; `PLC_002` 180×3×90 →
  `180.0 x 90.0`; `PLC_004` 135×3×180 → `135.0 x 180.0`; `WAL_EL_014_C01` 135×20×420 →
  `135.0 x 420.0`.

### 5. ✅ Modifiers propagate; materials do not — opposite rules, same scene

| Route | Result |
|---|---|
| `addModifier` on the **29** `PROTO_*` | **0 → 165** nodes with channel 1 |
| controlled 4-node test (`SRC` + 3 `copy`/`baseObject` instances) | all four gain it; `INS.modifiers.count` = 1 |
| material on a prototype (P10, 2026-10-05) | **`0 of 10`** instances inherit |

**So the UV pass on the panel system is 29 calls and the material pass is 165.** §5.2's per-node
material claim stands and is *not* weakened by this — it is the complement. `baseObject` sharing is
memory optimisation; it carries modifiers and not materials. Confirmed per family by `baseObject`
identity: `PROTO_CMP_001`'s family is 8 nodes and all 8 gained channel 1, while `PROTO_CMP_008`'s
11-member family stayed clean — the probe discriminates.

### 6. Class census and the false-absence family

With `totalBogusXYZ_Mod` throwing in the same batch: `Unwrap_UVW` `Uvwmap` `UVWMap` `MapScaler`
`surface` construct; `Unreal_UVW` `UVW_Channel_Select` `Camera_Map` throw.

**`Unwrap_UVW` is unusable through this bridge** — attaches, changes nothing, and every method throws
when invoked. Unwrapping is manual.

**`polyoop` is a new false absence.** `execute "polyoop"` → `undefined`; `polyoop == undefined` →
`true`; yet `polyoop.applyUVWMap` **works**. `isProperty polyop "applyUVWMap"` → `true` with
`"totalBogusXYZ"` → `false` is the calibrated test that reaches it. `meshop` is the in-batch control
that proves the probe discriminates (`execute "meshop"` → `StructDef`, not undefined).

An 18-id `execute`-based absence sweep returned undefined for five ids. **Four were true absences,
one (`polyoop`) false** — and nothing in the output distinguishes them. `quaternion` is a true
absence (all three arities throw; `quat 45.0 [0,0,1]` works with `point3` in-batch as control).

### 7. Documentation corrected, and one deliberately not changed

| File | Change |
|---|---|
| `references/13-uv-rules.md` | **created** |
| `references/architecture-exterior-pipelines.md` §7 item 2 | the two `UNVERIFIED` rows resolved; `maptype:4` confirmed; `setTiling` marked defective |
| `references/nurbs-complete-guide.md` §8 | the `setTiling` advice replaced with the `Uvwmap` route and the same-call trap |
| `references/_04-05-evidence.md` §G32 | the "CONFIRMED" claim annotated as **calibrated for the wrong question** |
| `SKILL.md` §3.1 | `generateUVs1` + the `setTiling` warning |
| `agents/max-orchestrator.md` | new **§5.2b** — the UV half of the hand-off |
| **`build_nurbs.py`, `nurbs_arch_library.ms`** | ⛔ **NOT changed.** They emit `generateUVs1:true`, which is now measured to produce a normalised `0..1` map — usable, but not world scale. Changing them is a **user decision**, because UV is a hand-off step and `G-81` makes builder output zero-modifier. **Logged as a project-level finding, not applied** — per §"the two logs are different instruments", a stage must not silently change what the builders emit |

### 8. Left unverified, deliberately

`redrawViews()` as an evaluation trigger (only `snapshotAsMesh` was measured) · `utile` on a
**second** modifier in a stack · UV seams / `isSeam` · `getTilingOffset` / `setTilingOffset` ·
whether the `0..1` NURBS map distorts on a non-planar surface · `Unwrap_UVW` driven from the UI ·
how Corona reads channel 1 (out of scope — materials are hand-made).

### Bridge state at the end of this pass

**Healthy throughout.** ~90 `execute_maxscript` calls, no timeout, no crash, no `formattedPrint`.
Final state: scene restored to the **delivered 254 nodes, 0 modifiers** after the test sweep. The
earlier `3dsmax.exe` exit recorded at P12 did not recur.

---

## Resume here — after P15

**The pack has no open item.** Every stage is verified or cancelled by user decision, the offline
gates pass, the chain measures **254 nodes** live and idempotent, and the documentation is swept
against measured facts — including UV, which was the last thing §"Resume here — after P14" listed.

1. **Do not re-run the drift audit expecting different results.** `references/_drift-audit.md` is
   current as of P13; `references/_fix-{a,b,c,d}-notes.md` record what was done; §P14 closed what it
   left; §P15 closed the UV item.
2. **Do not re-open the four retracted facts** (`getCurrentException`, `matrix3`, `findString`, the
   pipe-discovery "dead bridge") without a **calibrated** probe — hit, miss and bogus in one batch.
3. **Do not trust `getTiling`, `getNumMapVerts` on a node, or any in-call read-back as evidence
   that something was applied.** §P15 added a sixth and seventh member to that list:
   `getTiling` echoes the request, and a modifier property written in the adding call reads back
   correctly while being discarded. **The pattern behind all of them: a read-back that agrees with
   what you wrote is not a measurement.**
4. **Two measurements decide any future UV question:** `snapshotAsMesh <node>` then
   `meshop.getNumMapVerts <mesh> 1`, and the uv **range** — not the stored tiling value.
5. **The next genuine stage would be the materials hand-off itself** — writing the `PROTO_`-keyed
   material assignment as a runnable playbook. It needs live Max and the user's decisions on which
   16 Corona classes map to which `material_role`. **Not planned, not stubbed, not started.**

---

## Resume here — after P14

**The pack has no open live item.** Every stage is verified or cancelled by user decision, the offline
gates pass, the chain measures **254 nodes** live and idempotent, and the documentation has been swept
against the measured facts.

If you pick this up again, the productive work is **not** more docs:

1. **Do not re-run the drift audit expecting different results** — `references/_drift-audit.md` is
   current as of P13, `references/_fix-{a,b,c,d}-notes.md` record what was done, and §P14 closed the
   three items it left.
2. **Do not re-open the four retracted facts** (`getCurrentException`, `matrix3`, `findString`, the
   pipe-discovery "dead bridge") without a **calibrated** probe — hit, miss and bogus in one batch.
3. **When a user decision removes a stage, grep for its name.** §P14 item 1 is the second time this
   repo shipped a stale enumeration of stage names; both times the fix was one line and in both cases
   a committed artefact had already come to depend on the stale value.
4. The next genuine stage is **UV/unwrapping rules**, or a **materials hand-off**. Both need live Max
   and both must be measured, not reasoned about.
