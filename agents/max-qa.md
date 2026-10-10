# max-qa — S7: QA configuration, offline emit, read-only collect, and offline assessment

> **Purpose:** S7 is the quality assurance and analytical verification stage (historical P8 gate).
> It reads the locked pipeline specifications, generates deterministic read-only batch inspection scripts,
> collects ground-truth scene measurements from live 3ds Max via the orchestrator, and performs offline
> numerical and topological verification against declared tolerances.
>
> **Core Invariant:** **S7 is strictly READ-ONLY.**
> S7 never creates, mutates, or deletes scene geometry, never executes destructive MAXScript, and
> **never alters upstream design specs (`dimensions.json`, `massing.json`, `nurbs.json`, etc.) or `qa.json`
> to force a pass.** If a check fails, the failure is reported verbatim as a finding; tolerances and
> precision targets are immutable contracts, not tuning knobs.

---

## 1. Mission and stage position

| Property | Value |
|---|---|
| Stage · Input | **S7** (QA & form verification) · Pipeline specs (`dimensions.json`, `massing.json`, `nurbs.json`, `facade_grids.json`, `components_registry.json`, `assembly.json`, `world_table.csv`, `qa.json`) + evidence-bound `calibration-cert.json` |
| Execution mode | Decoupled 3-phase loop: **Offline emit** → **Read-only collect** (orchestrator) → **Offline assess** |
| Max mutations | **Zero.** Strictly read-only queries (`getNodeByName`, `classOf`, `evalPos`, `node.pos`, `node.rotation`, `node.modifiers.count`, etc.). No geometry creation, deletion, or modifier additions |
| Spec mutations | **Zero.** Upstream specs and `qa.json` remain bit-identical. No relaxing tolerances, no deleting targets |
| Orchestrator call | Sequential execution of emitted batch scripts (`batch_001.ms`...) via `3dsmax-mcp_execute_maxscript`. Exact raw string results captured into `results.json` |
| Precondition | S1 through S5 complete and locked (`07` §9 invariants `G-1`…`G-90` PASS; scene nodes fully constructed in 3ds Max) |
| Output artifacts | `qa-request.json`, `qa-run-context.json`, batch scripts (`batch_*.ms`), `results.json`, and final `qa-results.json` |
| Pass criterion | `qa-results.json` overall verdict `PASS` (exit code 0); every mandatory check complete and passing within certified bounds |

---

## 2. The 3-Step execution loop

QA execution separates script generation, live Max communication, and numerical evaluation into three
isolated steps. This guarantees determinism, prevents script timeout crashes on Max's main thread, and ensures
that numerical evaluation runs in certified Python arithmetic rather than Max's single-precision environment.

```
       [Step 1: Offline Emit]
       python scripts/qa_check.py --emit <run_dir> --calibration-cert <cert>
                   │
                   ▼  emits qa-request.json + batch_001.ms ... batch_NNN.ms
       [Step 2: Read-Only Collect]
       Orchestrator runs batch_*.ms sequentially via 3dsmax-mcp_execute_maxscript
                   │
                   ▼  saves raw strings into results.json
       [Step 3: Offline Assess]
       python scripts/qa_check.py --assess --request ... --results ... --out <run_dir>
                   │
                   ▼  emits qa-results.json (Exit 0 = PASS; Exit 1 = FAIL/ERROR/INCOMPLETE)
```

### Step 1: Offline emit

The QA CLI reads the pipeline specifications and calibration certificate, validates all bindings, and
slices the query plan into bounded, read-only batch scripts.

```bash
python scripts/qa_check.py \
  --in <pipeline_dir> \
  --emit <run_dir> \
  --run-id <run_token> \
  --calibration-cert <calibration_cert_path>
```

- **Inputs required:** Locked pipeline specs (`dimensions.json`, `massing.json`, `nurbs.json`, `facade_grids.json`,
  `components_registry.json`, `assembly.json`, `world_table.csv`, `qa.json`) and a valid `calibration-cert.json`.
- **Pre-flight verification:**
  - Verifies `calibration-cert.json` state is `CALIBRATED`.
  - Asserts `library_sha256` matches the active `snippets/nurbs_arch_library.ms`.
  - Verifies `methods.arithmetic_proof_sha256` and numerical bounds.
- **Outputs generated in `<run_dir>`:**
  - `qa-request.json`: Immutable execution request containing query metadata, target descriptors, and certificate digests.
  - `qa-run-context.json`: Run context tracking run ID, timestamps, and parameters.
  - `batch_001.ms`, `batch_002.ms`, ...: Bounded MAXScript inspection scripts (≤ `max_rows_per_batch` queries per script).
- **Exit code:** `0` = Ready for collect; `1` = Not ready / validation failure; `2` = Usage error.

### Step 2: Read-only collect (Orchestrator)

The orchestrator executes the generated batch scripts sequentially against the live 3ds Max instance.
Subagents do not call Max directly.

- **Transport:** Sequential calls to `3dsmax-mcp_execute_maxscript`.
- **Thread constraint:** Max executes scripts on its main UI thread. Long queries freeze Max. Each batch is
  budgeted strictly under `max_batch_seconds` (≤ 2.0 s).
- **Output format:** Batches return structured JSON or delimited wire rows prefixed by `QA_ROW:`.
- **Storage:** The orchestrator writes all raw string outputs directly into `<results.json>` mapping batch index
  or query ID to the unparsed response string. No string manipulation or formatting is performed during collection.

### Step 3: Offline assess

The QA CLI ingests the raw execution results, parses values using certified invariant decimal deserialization,
and evaluates every check against the declared mathematical tolerances.

```bash
python scripts/qa_check.py \
  --in <pipeline_dir> \
  --request <run_dir>/qa-request.json \
  --results <results.json> \
  --out <run_dir>
```

- **Processing:**
  - Deserializes coordinates, bounding boxes, counts, and sampled points.
  - Evaluates form deviation against analytical formulas (e.g., semi-elliptical cylinder reference models).
  - Evaluates topological census, assembly instance sharing, and opening volume identities.
- **Outputs generated in `<run_dir>`:**
  - `qa-results.json`: Full report detailing per-check status, measured values, deviations, tolerances, and overall verdict.
- **Exit code:**
  - `0`: Complete `PASS` — every mandatory check passed within tolerances.
  - `1`: `FAIL` (tolerance exceeded), `ERROR` (binding / syntax failure), or `INCOMPLETE` (unresolved targets / missing results).
  - `2`: CLI usage or file read error.

---

## 3. The 8 Check families

Every check declared in `qa.json:check_plan` belongs to one of eight closed check families:

| Check Family | Target Kind | Purpose and Verification Scope |
|---|---|---|
| `QA-V1-COVERAGE` | `project` | Whole-scene node census. Scans all active objects in Max, compares names against pipeline node registries, and asserts that no extra, untracked, or orphan nodes exist in the scene. |
| `QA-V1-CENSUS` | `massing_element` | Massing node verification. Validates existence, node names, object class (`Box`, `Dummy`), and layer assignment for all massing elements and group pivots. |
| `QA-V1-NURBS-CENSUS` | `nurbs_surface` | NURBS structure verification. Inspects `NURBSSet` / `NURBSNode` objects, validating sub-object counts, committed surface classes (`NURBSPointSurface`, `NURBSCVSurface`, etc.), and derivative meshes/splines. |
| `QA-V1-PLACEMENT` | `placement` | Assembly component verification. Reads placed panel instances, checking world position `(x, y, z)`, Z-axis orientation quaternion, prototype sharing (`baseObject == prototype.baseObject`), and correspondence to `world_table.csv`. |
| `QA-V1-WALLS` | `wall_host` / `wall_cell` | Tiled wall openings verification. Validates bounding box dimensions and coordinates of opening cells (`WAL_`), verifying that host volume minus opening cell volume satisfies the zero-modifier volume conservation identity (`G-82`). |
| `QA-V1-FORM` | `nurbs_surface` | Analytical surface precision. Samples a `(grid_u × grid_v)` lattice on the committed design surface via `evalPos`, comparing actual points against analytical reference geometry (`form_references[]` in `dimensions.json`). Checks surface deviation, longitudinal extent, and barrel landmarks. |
| `QA-V1-STACK` | `project` / `node` | Modifier stack health. Confirms that all nodes maintain clean stacks (0 modifiers for zero-modifier pipeline elements like `assembly.ms`), stack depth is ≤ 5, and no unattachable/crashing modifiers (`Extrude`, `Bevel`) are present. |
| `QA-V1-REPLAY` | `project` | Deterministic replay. Re-executes targeted queries across successive calls to prove measurement stability, idempotency, and absence of floating-point or state drift. |

---

## 4. Tolerances and numerical policies

Tolerances in `qa.json` are strictly separated into arithmetic, analytical form, numerical wire bounds,
and volume conservation:

### 4.1 Linear, area, and angular tolerances

- `tolerances.linear_cm`: Global linear tolerance for placement coordinates and bounding box extents (standard: `0.5 cm`).
- `tolerances.area_m2`: Area discrepancy tolerance for floor plates and footprints (standard: `0.05 m²`).
- `tolerances.angle_deg`: Angular tolerance for rotations and orientations (standard: `0.01 deg`).

### 4.2 Analytical form tolerances (`tolerances.form`)

Required when profile is `form_precision_v1`:
- `surface_deviation_cm`: Maximum allowable perpendicular or radial distance between sampled surface points and the analytical reference surface (e.g., `0.5 cm`).
- `longitudinal_extent_cm`: Maximum allowable deviation along the sweep / extrusion axis of the form (e.g., `0.5 cm`).
- `landmark_deviation_cm`: Maximum allowable discrepancy at critical geometric landmarks (springline, apex, boundary endpoints) (e.g., `0.5 cm`).

### 4.3 Numerical wire and solver bounds (`tolerances.numerical`)

Certified numerical bounds enforcing `separate_bounds_v1`:
- `solver_distance_cm`: Solver search bracket for nonlinear inversion (standard: `0.001 cm`).
- `wire_length_cm`: Maximum precision loss in string decimal formatting / parsing of distances (standard: `0.0001 cm`).
- `wire_angle_deg`: Precision bound for serialized angles (standard: `0.001 deg`).
- `unit_factor_relative`: Relative scaling tolerance across unit conversions (standard: `1e-06`).
- `volume_roundoff_cm3`: Roundoff tolerance for aggregate volume integrals (standard: `0.01 cm³`).

### 4.4 Volume conservation policy (`tolerances.volume`)

- `policy`: `box_endpoint_propagation_v1`.
- `endpoint_tolerance_ref`: References `tolerances.linear_cm`.
- Asserts that solid host volume equals the sum of cell partition volumes without requiring destructive CSG Booleans.

---

## 5. Operational limits and query batching

To protect Max from UI thread freezes and memory exhaustion, `qa.json:limits` enforces hard caps on
every execution run:

| Limit Key | Default Cap | Operational Protection |
|---|---|---|
| `max_rows_per_batch` | `25` | Caps queries per `.ms` script so execution finishes in ~30 ms, well below the 2 s hang threshold. |
| `max_targets` | `50` | Prevents runaway query expansion across massive scenes. |
| `max_samples` | `200` | Limits total surface lattice evaluations (`grid_u × grid_v`) per surface target. |
| `max_calls` | `50` | Maximum number of batch calls the orchestrator may execute in a single QA run. |
| `max_batch_seconds` | `2.0 s` | Max thread timeout ceiling; batches taking longer indicate scene lockup. |
| `max_total_seconds` | `60.0 s` | Total wall-clock time limit for the entire collection pass. |
| `max_solver_iterations` | `100` | Iteration ceiling for offline nonlinear point-to-surface projection solvers. |
| `max_response_bytes` | `1048576` (1 MB) | Maximum string buffer size returned by an individual `execute_maxscript` call. |

---

## 6. Strict rules and anti-patterns

### ⛔ Never alter specs or tolerances to force a pass

- If `CHK_FORM_01` fails with a deviation of `0.82 cm` against a tolerance of `0.5 cm`, **do NOT edit `tolerances.form.surface_deviation_cm` to `1.0 cm`**.
- Do NOT delete targets from `scope.targets` or checks from `check_plan`.
- Do NOT delete entries from `dimensions.json:precision_targets`.
- A QA failure is evidence that upstream geometry generation drifted from design intent. Report the deviation,
  identify the upstream stage responsible (S2 massing, S3 NURBS, or S5 assembly), and log the finding.

### ⛔ Never mutate the scene during QA

- Do NOT execute `delete <node>`, `addModifier <node>`, `move <node>`, or `convertToPoly <node>` in QA scripts.
- Inspection scripts must be pure accessors.
- Wrap all property reads in individual `try ( ) catch ( )` blocks so missing nodes return structured error records
  rather than aborting the batch script.

### ⛔ Never use `formattedPrint`

- `formattedPrint` is fatal in this bridge: it freezes `execute_maxscript` and crashes 3ds Max outright.
- Always use plain string concatenation `+` and `((val) as string)`.
- For fixed-width small integers, use literal `"0"` prefixing.

### ⛔ Never rely on introspection tools for QA ground truth

- Do NOT use `introspect_class` or `discover_plugin_classes` to verify node existence.
- Ground truth is live query execution:
  ```maxscript
  local nd = getNodeByName "SUR_001_Vault"
  if nd != undefined then (
      print ("FOUND:" + (classOf nd as string))
  ) else (
      print "MISSING"
  )
  ```
