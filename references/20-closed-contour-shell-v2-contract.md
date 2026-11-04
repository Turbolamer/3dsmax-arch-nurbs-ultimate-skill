# 20 — Closed-contour Shell v2 Contract

Normative specification for the **`closed_inner_contour_shell_v2`** wall architecture.
This document is packaged into the skill archive under `references/` and is fully self-contained:
it has **no runtime dependency on `Audit/` or `experiments/`**.

---

## 1. Overview and Target Architecture

The **`closed_inner_contour_shell_v2`** architecture models prismatic floor-level walls as:
1. A **closed inner contour** per storey, preserved as a non-rendering reference `SplineShape` (`_InnerSpline`).
2. A single vertical **`Editable_Poly`** surface for the entire floor perimeter, with **shared vertex indices** at corner seams and a whole-floor Z-level grid.
3. Faces corresponding to rough openings deleted before applying thickness.
4. Exactly **one `Shell` modifier** outward on the perimeter surface:
   - `innerAmount = 0.0`
   - `outerAmount = wall_thickness_cm` (converted to native scene units)
   - `straightenCorners = true`
   - `segments = 1`

Legacy `legacy_cells_v1` and the prototype `poly_surface_shell_v1` remain supported as distinct, explicit routes.
No silent fallback is permitted between routes.

---

## 2. Specification Schema (`walls.json` v2.0)

For `closed_inner_contour_shell_v2`, `walls.json` carries `schema_version: "2.0"` and `wall_technique: "closed_inner_contour_shell_v2"`.

### 2.1 Top-Level Object

The JSON object is closed. Envelope keys appear first, in exact order:

| Key | Type | Constraint / Meaning |
|---|---|---|
| `schema_version` | string | Exactly `"2.0"`. |
| `spec` | string | Exactly `"walls"`. |
| `project` | string | Matches project ID across all pipeline specs. |
| `units` | object | Exactly `{"length": "cm", "angle": "deg"}`. |
| `source` | object | Provenance envelope (`kind`, `reference`, `recorded_at`). |
| `status` | string | `"draft"`, `"locked"`, or `"superseded"`. |
| `tolerances` | object | `linear_cm`, `area_m2`, `angle_deg` copied from `dimensions.json`. |
| `origin_inputs` | array of strings | Upstream paths read (e.g. `facades[...]`, `levels[...]`). |
| `origins` | object | Flat map covering all domain leaves under G-9/G-10. |
| `wall_technique` | string | Exactly `"closed_inner_contour_shell_v2"`. |
| `reference_face` | string | `"inner"` or `"outer"`. |
| `numeric_epsilon_cm` | number | Finite positive number: `0 < numeric_epsilon_cm <= 0.01` cm. |
| `numeric_unit_epsilon` | number | Finite positive number: `0 < numeric_unit_epsilon <= 0.001`. |
| `storeys` | array of objects | One or more closed storey contour declarations. |

---

### 2.2 Storey Object (`storeys[]`)

Each storey represents an independent floor boundary:

```json
{
  "id": "storey_1",
  "name": "Ground Floor",
  "base_z_cm": 0.0,
  "top_z_cm": 300.0,
  "wall_thickness_cm": 30.0,
  "reference_face": "inner",
  "vertices_cm": [
    [0.0, 0.0],
    [600.0, 0.0],
    [600.0, 400.0],
    [0.0, 400.0]
  ],
  "segments": [
    {"id": "seg_1", "start_vertex_index": 0, "end_vertex_index": 1, "facade_ref": "dimensions.json:facades:F-S"},
    {"id": "seg_2", "start_vertex_index": 1, "end_vertex_index": 2, "facade_ref": "dimensions.json:facades:F-E"},
    {"id": "seg_3", "start_vertex_index": 2, "end_vertex_index": 3, "facade_ref": "dimensions.json:facades:F-N"},
    {"id": "seg_4", "start_vertex_index": 3, "end_vertex_index": 0, "facade_ref": "dimensions.json:facades:F-W"}
  ],
  "openings": [
    {
      "id": "OP-001",
      "segment_id": "seg_1",
      "kind": "door",
      "s_range_cm": [100.0, 200.0],
      "sill_cm": 0.0,
      "head_cm": 210.0,
      "component_ref": "components_registry.json:components:DOOR-01"
    }
  ],
  "topology_budget": {
    "max_grid_polygons": 128,
    "max_base_active_polygons": 128,
    "max_evaluated_triangles": 1024
  }
}
```

#### Fields and Constraints
- `id`: unique non-empty string identifier.
- `base_z_cm`, `top_z_cm`: finite numbers with `base_z_cm < top_z_cm`. Height $H = \text{top\_z\_cm} - \text{base\_z\_cm} > 0$.
- `wall_thickness_cm`: finite positive number ($> 0$).
- `reference_face`: `"inner"` or `"outer"` (inherits top-level `reference_face` if omitted).
- `vertices_cm`: array of $\ge 3$ distinct 2D coordinate pairs $[x, y]$ in cm.
  - Must define a **simple, non-self-intersecting** polygon.
  - Consecutive vertices must be distinct ($|p_{i+1} - p_i| > \varepsilon_{\text{linear}}$).
  - Closing duplicate $p_{N-1} == p_0$ is automatically detected and stripped without creating a zero-length segment.
- `segments`: array of segment objects in contour order ($N$ segments for $N$ vertices):
  - `id`: unique segment identifier within the storey.
  - `facade_ref`: optional qualified reference to `dimensions.json:facades:<id>`.
  - `start_vertex_index`, `end_vertex_index`: indices into `vertices_cm`.
- `openings`: array of zero or more rough opening specifications:
  - `id`: unique opening identifier within the storey.
  - `segment_id`: resolves to a declared `segments[].id`.
  - `kind`: `"window"` or `"door"`.
  - `s_range_cm`: $[s_{\min}, s_{\max}]$ with $0 \le s_{\min} < s_{\max} \le L_{\text{segment}}$.
  - `sill_cm`, `head_cm`: vertical bounds from floor base: $0 \le \text{sill\_cm} < \text{head\_cm} \le H$.
  - Non-overlapping: distinct openings on the same segment must not overlap in $s$.
- `topology_budget`: explicit operational ceilings:
  - `max_grid_polygons`: non-negative integer.
  - `max_base_active_polygons`: non-negative integer.
  - `max_evaluated_triangles`: non-negative integer.

---

## 3. Thickness and Provenance Law

1. **Strict Provenance Requirement**:
   `wall_thickness_cm` must have explicit provenance in `origins`.
   - `given`: directly provided in a user brief or architectural dimension spec.
   - `derived`: computed by a documented formula from upstream references.
   - `assumed`: derived from an unstated value, which **must bind to a recorded ledger entry** in `assumptions.json` (e.g. `A-026`).
2. **Builder Prohibition**:
   A builder or adapter **never invents a thickness default**. If `wall_thickness_cm` is absent in `walls.json`, the loader checks `assumptions.json`. If no assumption claims the path, the builder **refuses with an explicit error**.

---

## 4. CCW Normalization & Stable ID Preservation

### 4.1 Orientation Rule
In the 2D Cartesian plane (X right, Y up):
- Signed polygon area:
  $$A = \frac{1}{2} \sum_{i=0}^{N-1} (x_i y_{i+1} - x_{i+1} y_i)$$
- $A > 0$: Counter-Clockwise (CCW).
- $A < 0$: Clockwise (CW).
- $|A| \le \varepsilon_{\text{area}}$: Degenerate polygon (rejected).

For a CCW contour:
- Tangent unit vector: $\vec{T} = \frac{p_{i+1} - p_i}{|p_{i+1} - p_i|} = (t_x, t_y, 0)$.
- Outward unit normal: $\vec{N} = (t_y, -t_x, 0) = \vec{T} \times \vec{Z}_{\text{up}}$.
- Up unit vector: $\vec{Z}_{\text{up}} = (0, 0, 1)$.
- $(\vec{T}, \vec{N}, \vec{Z}_{\text{up}})$ forms a standard right-handed orthonormal basis.

### 4.2 Normalization Algorithm
If $A < 0$ (CW), vertices are reversed to achieve CCW orientation:
1. Vertex sequence $V_0, V_1, \dots, V_{N-1}$ becomes $V'_0, V'_1, \dots, V'_{N-1}$ where $V'_j = V_{(N-j)\%N}$.
2. Each segment $S_k$ formerly directed from $V_k \to V_{k+1}$ is now traversed from $V_{k+1} \to V_k$:
   - Segment ID $S_k$ is preserved.
   - Direction reverses: $\vec{T}' = -\vec{T}$.
3. For any opening on $S_k$ with station interval $[s_{\min}, s_{\max}]$ measured from $V_k$:
   - The opening remains attached to segment $S_k$.
   - The station interval is flipped to match the reversed edge:
     $$s'_{\min} = L_k - s_{\max}, \quad s'_{\max} = L_k - s_{\min}$$
4. Closing knot duplicate ($V_{N-1} == V_0$) is stripped prior to area calculation so no zero-length edge is generated.

---

## 5. Safe Contour Offset & Verification Gates

The prototype offset formula (`probe.py:22–36`) is a simple miter calculation without safety verification.
For production v2, derivation of an inner contour from an outer reference (or verification of an outward shell) must pass **six mathematical safety gates**:

### 5.1 Bisector & Miter Calculation
For each vertex $i$ between incoming unit normal $\vec{N}_{i-1}$ and outgoing unit normal $\vec{N}_i$:
$$\text{denom} = 1 + \vec{N}_{i-1} \cdot \vec{N}_i = 1 + \cos(\theta_i)$$
Miter vector:
$$\vec{M}_i = \frac{\vec{N}_{i-1} + \vec{N}_i}{1 + \vec{N}_{i-1} \cdot \vec{N}_i}$$

### 5.2 Six Safety Gates

1. **Simplicity and Planarity of Input**:
   - No non-adjacent edge intersections.
   - Distinct, finite coordinates.
   - Failure: `POLYGON_SELF_INTERSECTION` or `DEGENERATE_POLYGON`.

2. **Excessive Miter / Acute Corner Gate**:
   - Interior corner angle $\alpha_i$ must be $\ge 30^\circ$ (turn angle $\theta_i \le 150^\circ$).
   - $\text{denom} \ge 0.13397$ and $|\vec{M}_i| \le 4.0$.
   - Failure: `EXCESSIVE_MITER: corner angle < 30 deg exceeds miter threshold`.

3. **Inset Collapse Gate (Area Check)**:
   - For inward offset by $-t$:
     $$0 < A_{\text{inner}} < A_{\text{outer}}$$
   - If $A_{\text{inner}} \le 0$, the wall thickness exceeds the room geometry, causing geometric collapse.
   - Failure: `INSET_COLLAPSE: inner contour area <= 0`.

4. **Edge Direction Preservation (No Local Inversion)**:
   - For every edge $i$:
     $$\vec{E}_i \cdot \vec{E}'_i > 0$$
   - Edge length $|\vec{E}'_i| > \varepsilon_{\text{linear}}$.
   - Failure: `EDGE_COLLAPSE: edge i collapsed or inverted direction`.

5. **Offset Self-Intersection Gate (Global Non-Overlap)**:
   - The offset polygon must be simple: no non-adjacent offset edges $(e'_j, e'_k)$ may intersect.
   - Catches hourglass pinching, narrow neck collapse, and opposing walls crossing.
   - Failure: `OFFSET_SELF_INTERSECTION: offset edges intersect`.

6. **Narrow Notch / Proximity Clearance Gate**:
   - Minimum clearance between any offset vertex $p'_i$ and any non-incident original edge $e_k$ ($k \notin \{i-1, i\}$):
     $$\text{dist}(p'_i, e_k) \ge t - \varepsilon_{\text{linear}}$$
   - Failure: `NARROW_NOTCH: neck width < 2 * thickness`.

If any gate fails, the system **refuses with a structured error**. It never silently clips, never silently modifies wall thickness, and never silently falls back to another route.

---

## 6. S4w → S5 → QA Opening Manifest Contract

The opening manifest is the authoritative geometric contract connecting S4w (wall shell emitter), S5 (component placement), and S7 (QA verification).

### 6.1 Manifest Record Structure

Each opening produces a manifest record:

```json
{
  "manifest_version": "2.0",
  "project_id": "pavilion-01",
  "storey_id": "storey_1",
  "contour_id": "contour_1",
  "segment_id": "seg_1",
  "opening_id": "OP-001",
  "kind": "door",
  "component_type_id": "DOOR-01",
  "mount_reference": "inner_face",
  "local_frame": {
    "origin_cm": [100.0, 0.0, 0.0],
    "tangent": [1.0, 0.0, 0.0],
    "outward": [0.0, -1.0, 0.0],
    "up": [0.0, 0.0, 1.0],
    "basis_matrix": [
      [1.0, 0.0, 0.0, 100.0],
      [0.0, -1.0, 0.0, 0.0],
      [0.0, 0.0, 1.0, 0.0]
    ]
  },
  "station_along_segment": {
    "s_min_cm": 100.0,
    "s_max_cm": 200.0,
    "width_cm": 100.0
  },
  "vertical_bounds": {
    "sill_z_cm": 0.0,
    "head_z_cm": 210.0,
    "height_cm": 210.0
  },
  "rough_opening": {
    "width_cm": 100.0,
    "height_cm": 210.0,
    "depth_cm": 30.0
  },
  "wall_thickness_cm": 30.0,
  "mounting_parameters": {
    "recess_cm": 10.0,
    "frame_depth_cm": 12.0,
    "clearance_sides_cm": 1.0,
    "clearance_top_cm": 1.0,
    "clearance_bottom_cm": 0.0,
    "overlap_cm": 1.5
  },
  "provenance": {
    "source_file": "walls.json",
    "source_path": "storeys[0].openings[0]"
  }
}
```

### 6.2 Local Frame & Mounting Semantics
- `origin_cm`: 3D position in project space at $[s_{\min}, \text{base\_z\_cm} + \text{sill\_cm}]$ on the mount reference face.
- `tangent`: unit vector along the wall segment ($+U$ direction of rough opening).
- `outward`: unit vector perpendicular to wall pointing outward ($+V$ direction, away from building interior).
- `up`: unit vector $[0, 0, 1]$ ($+W$ direction, vertical).
- `basis_matrix`: $3 \times 4$ affine transform matrix $[\vec{T} \mid \vec{N} \mid \vec{Z}_{\text{up}} \mid \vec{P}_{\text{origin}}]$.
- `mount_reference`:
  - `"inner_face"`: origin sits on the inner wall surface.
  - `"outer_face"`: origin sits on the outer wall surface.
  - `"wall_center"`: origin sits on the wall centerline ($t/2$).
- `recess_cm`: signed displacement along $\vec{N}$ (or $-\vec{N}$ if referenced to outer face) from mount reference face to frame front.
- `frame_depth_cm`: physical thickness of the window/door frame along the wall normal.
- `clearance_sides_cm`, `clearance_top_cm`, `clearance_bottom_cm`: installation gap between rough opening edges and component outer boundary.
- `overlap_cm`: exterior casing/trim overlap over the rough opening edge.

---

## 7. Units and Scaling Contract

1. **Specifications**: All dimensions in `walls.json` and `opening_manifest.json` are in canonical **centimetres** (`cm`), angles in **degrees** (`deg`).
2. **3ds Max Execution**: Native scene units are queried via `scene_units.py` (`units.decodeValue "1cm"`). Lengths are scaled by the unit scale factor; areas by $\text{scale}^2$; volumes by $\text{scale}^3$.
3. **No Unit Tampering**: User system unit and display unit settings are never modified.

---

## 8. Exclusivity and Route Separation

1. `assembly.json` must echo `wall_technique: "closed_inner_contour_shell_v2"`.
2. When `closed_inner_contour_shell_v2` is active:
   - `wall_ref` in `assembly.json` must be `"wall_surface.json"`.
   - `opening_cuts` and `wall_cells` must be absent from `assembly.json`.
   - S5 does not generate tiled box cells.
   - S4w generates the single floor poly shell with one `Shell` modifier.
   - S5 adds zero modifiers to placed instances or existing nodes.
