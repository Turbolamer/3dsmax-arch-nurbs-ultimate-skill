# 01 — Pipeline Workflow: Stage Map & Contracts (S0 → S7)

> **Updated 2026-10-10 (Form Precision & Staged Unit Pipeline):**
> The active architecture pipeline runs **S0 → S5 (geometry)**, verified by **S7 (QA gate)**,
> followed by **manual material assignment hand-off**.
> - **S5 (`scripts/place_components.py`) is the FINAL geometry builder.** It emits zero modifiers (`G-81`) and applies Mechanism A host wall hiding (`host_node.isHidden = true`).
> - **S7 (`scripts/qa_check.py`) is the automated QA verification gate.** It evaluates coverage, census, analytical form precision oracle, wall host hiding, modifier stack, and replay idempotency.
> - **S6 / P7 (materials + UVs) and S8 / P9 (export) remain cancelled by user decision.** Materials and UVs are applied by hand; the deliverable is a verified live 3ds Max scene.

---

## 1. Scope & Document Responsibilities

| Question | Owning Document |
|---|---|
| Spec grammar and JSON schema (`G-1`…`G-90`) | [`references/07-spec-grammar.md`](07-spec-grammar.md) |
| Stage procedures, live gates, anti-patterns | `agents/max-<stage>.md` |
| End-to-end orchestration and execution runbook | [`agents/max-orchestrator.md`](../agents/max-orchestrator.md) |
| Verified tool inventory and MCP routing | [`references/02-mcp-live-orchestration.md`](02-mcp-live-orchestration.md) |
| Live status board, verified measurements, incident logs | [`CHECKPOINT.md`](../CHECKPOINT.md) |

### 1.1 Tools that ALWAYS fail — never call at any stage

Absent plugins on this installation (forestPack, forestLite, tyFlow, railClone, phoenixFD):
- `3dsmax-mcp_scatter_forest_pack` (substitute **Chaos Scatter** via `execute_maxscript`)
- All 14 `3dsmax-mcp_tyflow_*` tools (substitute Chaos Scatter for static distribution; Max particles / keyframes for motion)
- `3dsmax-mcp_get_railclone_style_graph` (substitute `clone_objects` with `mode: "instance"`)
- All `mcg_*` tools and `curve_model` (Max Creation Graph undrivable from bridge)
- All Rhino-server collision tools (`loft`, `pipe`, `sweep1`, `extrude_curve`, `boolean_*`, `gh_*`)

---

## 2. Spec Chain & Data Flow

All stages communicate exclusively through locked JSON specs in `specs/pipeline/` and emitted `.ms` scripts:

```
brief
 └─ S1  dimensions.json ─┬─ assumptions.json ─┬─ conflicts_resolved.json      [hand-authored, locked]
                         │
                         ├─> S2  build_spec.py ────> massing.json + massing.ms ──> 27 nodes
                         │
                         ├─> S3  build_nurbs.py ───> nurbs.json  + nurbs.ms     ──> 10 nodes
                         │      (analytical curve expansion via curve_gen.py / expand_curves.py)
                         │
                         └─> S4  facade_tables.py > facade_grids.json
                                            └────> components_registry.json
                                                     facade_table.csv
                                                     world_table.csv         ──> 136 panels / 29 blocks
                                                              │
                            S2 massing.json ──────────────────-┤
                            S1 dimensions.json ────────────────┤
                                                              ▼
                               S5  place_components.py ─> assembly.json + assembly.ms ──> 244/254 nodes
                               [LAST GEOMETRY BUILDER]                  │
                               (Mechanism A host hiding, 0 modifiers)   │
                                                                        ▼
                                                   S7  qa_check.py  (--emit -> MCP collect -> --assess)
                                                   [QA VERIFICATION GATE: coverage, census, form, walls]
                                                                        │
                                                                        ▼
                                                       Manual Material Assignment Hand-off
```

### Spec File Registry

| # | Spec File | Owner Stage | Reads | Writes |
|---|---|---|---|---|
| 1 | `dimensions.json` | **S1** (`agents/max-input.md`) | Brief, drawings, images | Dimensional parameters & constraints |
| 2 | `conflicts_resolved.json` | **S1** (`agents/max-input.md`) | Input contradictions | Conflict resolution audit records |
| 3 | `assumptions.json` | **S1** (`agents/max-input.md`) | Input silences | Recorded architectural defaults (`A-nnn`) |
| 4 | `massing.json` | **S2** (`agents/max-massing.md`) | S1 specs | Prismatic massing solids, storeys, grouping |
| 5 | `nurbs.json` | **S3** (`agents/max-nurbs.md`) | S1, S2 specs | Relational NURBS curves, surfaces, approximations |
| 6 | `facade_grids.json` | **S4a** (`agents/max-facade.md`) | S1, S2 specs | Elevation bay grids, mullions, panel types |
| 7 | `components_registry.json` | **S4b** (`agents/max-components.md`) | S4a specs | Parametric block definitions, geometry profiles |
| 8 | `assembly.json` | **S5** (`agents/max-assembly.md`) | S1, S2, S4 specs, CSVs | Instance placements, tiled walls (`wall_cells`), scatter declarations |
| 9 | `qa.json` | **S7** (`agents/max-qa.md`) | S1..S5 specs | Verification check plan, targets, tolerances, limits (`G-87`..`G-90`) |
| 10 | ~~`materials.json`~~ | Reserved stub | — | Manual hand-off; stage cancelled by user decision |
| 11 | ~~`export.json`~~ | Reserved stub | — | Manual hand-off; stage cancelled by user decision |

---

## 3. Stage Contracts & Pipeline Boundaries

### S0 — Dispatch & Environment (`agents/max-orchestrator.md`)
- **Reads:** `AGENTS.md`, `PLAN.md`, `CHECKPOINT.md`, project brief.
- **Gate:** `python scripts/env_preflight.py --results results.json` exits 0 (all 9 checks PASS).
- **Refuses when:** Transport is not `namedpipe`, Max major version is not 2026, or absent plugins resolve.

### S1 — Input Extraction & Normalisation (`agents/max-input.md`)
- **Reads:** Architectural brief, raster drawings, reference imagery.
- **Gate:** `python scripts/validate_specs.py --dir specs/pipeline --build` exits 0; all three files `status: "locked"`.
- **Refuses when:** Dimensions contain unspecified default inventions, or open conflict records exist.
- **Tools:** Zero MCP calls. Pure offline stage.

### S2 — Prismatic Massing (`agents/max-massing.md`)
- **Reads:** `dimensions.json` (locked).
- **Builder:** `python scripts/build_spec.py --stage massing --in <specs> --out <specs>`.
- **Gate:** `fileIn massing.ms` produces 27 nodes (22 `Box` + 5 `Dummy`), idempotent over 3 runs, 9/9 bboxes exact to $0.000000\text{ cm}$.

### S3 — NURBS Mathematical Surfaces (`agents/max-nurbs.md`)
- **Reads:** `nurbs.json` (hand-authored or expanded via `scripts/expand_curves.py`), `dimensions.json`, `massing.json`.
- **Builder:** `python scripts/build_nurbs.py --in <specs> --out <specs>`.
- **Gate:** `fileIn nurbs.ms` builds relational surfaces (10 nodes in pavilion example, up to 37 nodes in fixtures), idempotent over 3 runs.
- **Precision Discipline:** Evaluated station count ladder. 8-micron precision verified on `point_grid` ($0.000824\text{ cm}$) vs `u_loft` B-spline fit error ($\approx 2.14\text{ cm}$).

### S4a / S4b — Facade Grids & Component Registry (`agents/max-facade.md`, `agents/max-components.md`)
- **Reads:** `dimensions.json`, `massing.json`.
- **Builder:** `python scripts/facade_tables.py --stage all --in <specs> --out <specs>`.
- **Outputs:** `facade_grids.json`, `components_registry.json`, `facade_table.csv`, `world_table.csv`.
- **Gate:** MAXScript reads 136 CSV rows; places 136 reference instances referencing 29 component prototypes; `objects.count` == 165.

### S5 — Assembly & Wall Tiling (FINAL Geometry Builder) (`agents/max-assembly.md`)
- **Reads:** `dimensions.json`, `massing.json`, `components_registry.json`, `world_table.csv`.
- **Builder:** `python scripts/place_components.py --stage assembly --in <specs> --out <specs>`.
- **Outputs:** `assembly.json`, `assembly.ms`.
- **Gate:**
  - `fileIn massing.ms` then `fileIn assembly.ms` ×3 → `objects.count` == 244 (254 with NURBS), strictly idempotent.
  - **Zero modifiers (`G-81`):** `addModifier` count in emitted script is exactly 0.
  - **Mechanism A host hiding:** Massing host walls (`EL_014`..`EL_021`) deactivated via `host_node.isHidden = true`, preventing active collisions with opening apertures and discrete `WAL_` solid cells.
  - **$B_{\text{total}}$ Volume Budget:** G-82 volume propagation error budget verified in $\text{cm}^3$ ($|\text{cell\_volume} - \text{expected}| \le B_{\text{total}}$).

### S7 — QA Verification Gate (`agents/max-qa.md`, `scripts/qa_check.py`)
- **Reads:** All pipeline specs, `qa.json` (`G-87`..`G-90`), live Max scene.
- **Role:** Strictly read-only verification gate. Emits zero geometry.
- **Workflow:**
  1. **Emit:** `python scripts/qa_check.py --in <specs> --emit <run_dir> --run-id <run_id> [--calibration-cert <cert>]`. Generates canonical `qa-request.json`, `qa-run-context.json`, and sequential query batch files (`batch_001.ms`, etc.). Exit 0 = `READY`.
  2. **MCP Collect:** Execute query batches sequentially via `3dsmax-mcp_execute_maxscript`, saving wire stdout to `<run_dir>/results.json`.
  3. **Assess:** `python scripts/qa_check.py --in <specs> --request <run_dir>/qa-request.json --results <run_dir>/results.json --out <run_dir>`.
- **Verification Families:**
  - `QA-V1-COVERAGE`: all target solids and surfaces observed.
  - `QA-V1-CENSUS` & `QA-V1-NURBS-CENSUS`: massing and NURBS object counts match spec.
  - `QA-V1-PLACEMENT`: placed component positions match predicted coordinates.
  - `QA-V1-WALLS`: Mechanism A verified (`host_node.isHidden == true` prevents opening occlusion).
  - `QA-V1-FORM`: surface deviation evaluated by analytical geometry oracle against exact mathematical formulas.
  - `QA-V1-STACK`: zero-modifier invariant verified across all nodes.
  - `QA-V1-REPLAY`: idempotency across repeated runs.
- **Gate:** Exit 0 on complete PASS only; exit 1 on FAIL/ERROR/INCOMPLETE.

---

## 4. Manual Materials & UV Hand-Off

Because S6 (materials) and S8 (export) were cancelled by user decision, the deliverable is handed off to the user:

1. **Geometry is Verified:** S5 produced a zero-modifier model, and S7 confirmed exact census, positions, wall apertures, and form precision.
2. **Material Assignment:**
   - User opens the scene in 3ds Max.
   - `PROTO_` nodes (29 prototypes) share `baseObject` with their instances as a memory optimization, but materials do not propagate across shared base objects.
   - Materials are assigned in the Material Editor per node (`node.material = m`) or using Multi-Materials across component families.
3. **UV Modifiers:**
   - Per `references/13-uv-rules.md`, applying UV modifiers to the **29 prototypes only** automatically equips all 136 `PLC_` instances.
   - Massing nodes and wall cells receive individual UV modifiers if textured.
4. **Layer Assignment:**
   - Applied manually in the 3ds Max Layer dialog following `assembly.json.layer_map`.
