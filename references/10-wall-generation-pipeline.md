# 10 - Wall Generation Pipeline: Production Architecture & Route Separation

> **Status:** Accepted production architecture specification (Plan v4, Phase 5).
> **Target:** `closed_inner_contour_shell_v2` (Schema 2.0).
> **Packaged Reference:** Completely autonomous and self-contained; zero runtime or normative dependencies on `Audit/` or `experiments/`.

---

## 1. Overview & Architectural Hierarchy

The wall generation pipeline translates floor-level boundary polygons and rough opening schedules into verified 3D wall geometry in Autodesk 3ds Max 2026.

### Architectural Routes

| Route | Status | Schema | Key Artifacts | Geometry Description |
|---|---|---|---|---|
| **`closed_inner_contour_shell_v2`** | **Accepted Production Architecture** | `walls.json` v2.0 (`storeys[]`) | `wall_surface.ms`, `_InnerSpline`, `WS_<id>` | Continuous single `Editable_Poly` perimeter per floor; shared vertex indices at corner seams; rough openings cut prior to thickness; exactly 1 outward `Shell` modifier (`straightenCorners=true`); preserved guide spline. |
| **`legacy_cells_v1`** | **Preserved Legacy Route** | `assembly.json` (`wall_cells[]`) | `assembly.ms`, `WAL_<id>` | Prismatic solid `Box` nodes tiling each facade band around rectangular openings. Zero modifiers (`G-81`). Host massing walls deactivated via Mechanism A (`host_node.isHidden = true`). |
| **`poly_surface_shell_v1`** | **Preserved Prototype Route** | `walls.json` v1.0 (`wall_runs[]`) | `wall_surface.ms`, `WS_<id>` | Independent straight wall runs stitched with returns. |

### Strict Non-Fallback Invariant
- Every project declaring walls specifies `wall_technique` in `walls.json` and echoes it in `assembly.json`.
- **Fail-Closed:** Any unknown, conflicting, invalid, or missing selector causes an immediate build failure.
- **No Silent Fallback:** Under no circumstance does an invalid or failing `closed_inner_contour_shell_v2` build silently fall back to `legacy_cells_v1` or vice-versa.

---

## 2. Production Architecture: `closed_inner_contour_shell_v2`

The accepted production architecture executes at stage **S4w** (between S4 facade tables and S5 component assembly):

```text
S1: dimensions.json (storeys, footprints, levels)
  │
  ├─► S2: massing.ms (slabs, columns, roofs; host walls hidden under Mechanism A)
  │
  ├─► S4w: build_wall_v2.py ──► wall_surface.json + wall_surface.ms
  │        (closed inner contour, opening excision, outward Shell modifier)
  │
  ├─► S5: place_components.py ──► assembly.json + assembly.ms
  │       (reads S4w opening manifest, mounts frames, 0 modifiers)
  │
  └─► S7: qa_check.py (independent analytical oracle, watertightness, tolerances)
```

### 2.1 Construction Contract
1. **Preserved Reference Guide Spline (`_InnerSpline`):**
   - Emitted as an unrendered, non-interfering `SplineShape` node (e.g. `WS_storey_1_InnerSpline`).
   - Represents the exact CCW floor footprint boundary. Preserved hidden for user guidance and downstream inspection.
2. **Perimeter Surface Topology:**
   - Generated as a single continuous vertical `Editable_Poly` ribbon spanning the entire perimeter.
   - **Corner Seams:** Vertices on adjacent perimeter segments at corner miters share identical vertex indices (no duplicate coincident vertices, corner valence = 2).
   - **Station Grid:** Horizontal division along segment boundaries and opening edges ($s$-intervals); vertical division at sill, head, base, and storey elevations.
3. **Opening Excision Prior to Shell:**
   - Polygon faces corresponding to rough opening bounding boxes are deleted from the base poly before applying thickness.
   - Eliminates Boolean operations, slice modifiers, and mesh intersections.
4. **Single Outward Shell Modifier:**
   - Exactly **one** `Shell` modifier is applied to the perimeter poly:
     - `innerAmount = 0.0`
     - `outerAmount = wall_thickness_cm` (converted to native scene units)
     - `straightenCorners = true` (guarantees uniform wall thickness at mitered corners)
     - `segments = 1`
   - Verified 100% solid, manifold, and watertight: **`openEdges == 0`**.

### 2.2 S5 Component Integration & Manifest Mount
- S4w generates an **Opening Manifest** embedding the exact local coordinate frames for each rough opening:
  $$\vec{T} = \text{tangent along facade},\quad \vec{N}_{\text{outward}} = \text{outward wall normal},\quad \vec{Z}_{\text{up}} = [0, 0, 1]$$
- S5 reads the manifest and places window/door component assemblies with specified clearances (e.g. 10 mm top/sides, 0 mm flush sill) and outer reveal depths.
- **Mechanism A Host Hiding:** Host facade walls in massing (`EL_...`) are deactivated via `host_node.isHidden = true`, preventing opening occlusion while preserving volume accounting.

### 2.3 Independent S7 Analytical Oracle
The S7 verification gate assesses wall geometry against an independent analytical formula:
$$V_{\text{oracle}} = (A_{\text{outer}} - A_{\text{inner}}) \times H - \sum_{i} (w_i \times h_i \times t)$$
- **Watertight Gate (`QA-V1-SOLID`):** Evaluates signed tetrahedral mesh volume ($V_{\text{scene}} > 0$) and asserts strictly zero open edges (`openEdges == 0`). Volume deviation $|V_{\text{scene}} - V_{\text{oracle}}| \le \text{tolerance}$.
- **Topology Gate (`QA-V1-TOPOLOGY`):** Asserts base object class `Editable_Poly`, modifier stack count strictly equal to 1 (`Shell`), 0 duplicate vertices, and valid seam valence.
- **Surface Gate (`QA-V1-SURFACE`):** Asserts base poly inner vertices lie on the reference spline within linear tolerance ($\le 0.5\text{ cm}$).

---

## 3. Preserved Legacy Route: `legacy_cells_v1`

When `wall_technique: "legacy_cells_v1"` is selected:
1. `assembly.json` contains `wall_cells[]` tiling each host wall band around openings.
2. S5 `place_components.py` emits discrete solid `Box` nodes (`WAL_<host>_C<col>_R<row>`).
3. Zero modifiers attached (`G-81`).
4. Host facade walls are hidden under Mechanism A (`host_node.isHidden = true`).
5. Verified by volume conservation budget ($B_{\text{total}}$ under `G-82`).

---

## 4. Preserved Prototype Route: `poly_surface_shell_v1`

When `wall_technique: "poly_surface_shell_v1"` is selected:
1. `walls.json` schema 1.0 defines independent `wall_runs[]`, `openings[]`, and `upper_returns[]`.
2. Each run is generated as a planar polygonal strip with returns.
3. Used for backward compatibility with isolated straight-run fixtures.

---

## 5. Normative Cross-References

- Complete specification schema and operational invariants: [`references/20-closed-contour-shell-v2-contract.md`](20-closed-contour-shell-v2-contract.md).
- Spec grammar and invariant definitions (`G-1` through `G-98`): [`references/07-spec-grammar.md`](07-spec-grammar.md).
- End-to-end pipeline execution and MCP orchestration: [`references/01-pipeline-workflow.md`](01-pipeline-workflow.md) and [`references/02-mcp-live-orchestration.md`](02-mcp-live-orchestration.md).
