#!/usr/bin/env python3
"""Closed-contour Shell v2 — Geometric contract, validation, offset, and manifest module.

Normative implementation of closed_inner_contour_shell_v2:
- Polygon validation, closure, and CCW normalization with stable ID & opening preservation.
- Safe inward/outward contour offset with 6 mathematical safety gates:
  1. Input simplicity & non-degeneracy
  2. Miter limit & acute corner gate (interior angle >= 30 deg, miter <= 4.0)
  3. Inset collapse gate (0 < area_inner < area_outer)
  4. Edge direction preservation (E_i . E'_i > 0)
  5. Offset polygon simplicity & non-self-intersection
  6. Narrow notch / proximity clearance (dist(p'_i, e_k) >= thickness - eps)
- S4w -> S5 -> QA Opening Manifest generation with orthonormal 3D local frames.
- Sourced thickness and provenance verification (no builder-invented defaults).

Self-contained: no runtime dependencies on Audit/ or experiments/.
Packaged in the .skill archive under scripts/.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence, Tuple, Union

Point2D = Tuple[float, float]
Vector2D = Tuple[float, float]
Vector3D = Tuple[float, float, float]
Matrix3x4 = Tuple[Tuple[float, float, float, float],
                  Tuple[float, float, float, float],
                  Tuple[float, float, float, float]]

# Geometric thresholds
DEFAULT_LINEAR_EPS_CM = 0.001
DEFAULT_UNIT_EPS = 0.0001
DEFAULT_MITER_LIMIT = 4.0  # corresponds to corner interior angle >= 28.95 deg (approx 30 deg)
MIN_INTERIOR_ANGLE_DEG = 30.0


class ContourError(ValueError):
    """Base error for contour validation and offset failures."""
    def __init__(self, code: str, message: str, *, details: Optional[Mapping[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = dict(details) if details else {}


class ContourOffsetError(ContourError):
    """Refusal during inward/outward contour offset."""


# --------------------------------------------------------------------------- #
# 1. 2D Vector & Primitive Math
# --------------------------------------------------------------------------- #

def dot2d(u: Vector2D, v: Vector2D) -> float:
    return u[0] * v[0] + u[1] * v[1]


def cross2d(u: Vector2D, v: Vector2D) -> float:
    return u[0] * v[1] - u[1] * v[0]


def norm2d(v: Vector2D) -> float:
    return math.hypot(v[0], v[1])


def dist2d(p1: Point2D, p2: Point2D) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def normalize2d(v: Vector2D, eps: float = DEFAULT_UNIT_EPS) -> Vector2D:
    length = math.hypot(v[0], v[1])
    if length <= eps or not math.isfinite(length):
        raise ContourError("ZERO_VECTOR", f"Cannot normalize zero or non-finite vector: {v}")
    return (v[0] / length, v[1] / length)


def segments_intersect_2d(
    p1: Point2D, p2: Point2D,
    p3: Point2D, p4: Point2D,
    eps: float = DEFAULT_LINEAR_EPS_CM
) -> bool:
    """True if segments p1-p2 and p3-p4 intersect strictly in their relative interiors or overlap."""
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    cross = cross2d(d1, d2)
    diff = (p3[0] - p1[0], p3[1] - p1[1])

    if abs(cross) <= 1e-12:
        # Segments are parallel
        if abs(cross2d(diff, d1)) > eps:
            return False  # parallel and non-collinear
        # Collinear: check interval overlap
        l1_sq = dot2d(d1, d1)
        if l1_sq <= eps * eps:
            return False
        t0 = dot2d(diff, d1) / l1_sq
        t1 = dot2d((p4[0] - p1[0], p4[1] - p1[1]), d1) / l1_sq
        t_min, t_max = min(t0, t1), max(t0, t1)
        # Strict interior overlap
        return (t_max > eps) and (t_min < 1.0 - eps)

    t1 = cross2d(diff, d2) / cross
    t2 = cross2d(diff, d1) / cross
    # Strict interior intersection (with numerical boundary margin)
    return (eps < t1 < 1.0 - eps) and (eps < t2 < 1.0 - eps)


def point_to_segment_dist_2d(p: Point2D, a: Point2D, b: Point2D) -> float:
    """Distance from point p to finite segment a-b."""
    ab = (b[0] - a[0], b[1] - a[1])
    l2 = dot2d(ab, ab)
    if l2 <= 1e-12:
        return dist2d(p, a)
    t = dot2d((p[0] - a[0], p[1] - a[1]), ab) / l2
    t_clamped = max(0.0, min(1.0, t))
    proj = (a[0] + t_clamped * ab[0], a[1] + t_clamped * ab[1])
    return dist2d(p, proj)


# --------------------------------------------------------------------------- #
# 2. Polygon Geometry Analysis
# --------------------------------------------------------------------------- #

def polygon_signed_area_2d(vertices: Sequence[Point2D]) -> float:
    """Signed Shoelace area. Positive = CCW, Negative = CW."""
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1] - vertices[j][0] * vertices[i][1]
    return area / 2.0


def deduplicate_closing_vertex(vertices: Sequence[Point2D], eps: float = DEFAULT_LINEAR_EPS_CM) -> list[Point2D]:
    """Detects and removes closing duplicate vertex p[n-1] == p[0] without creating a zero-edge."""
    verts = [tuple(p) for p in vertices]
    if len(verts) >= 4 and dist2d(verts[0], verts[-1]) <= eps:
        verts = verts[:-1]
    return list(verts)


def validate_polygon_simplicity(vertices: Sequence[Point2D], eps: float = DEFAULT_LINEAR_EPS_CM) -> None:
    """Ensures vertices form a valid, finite, simple (non-self-intersecting) 2D polygon."""
    n = len(vertices)
    if n < 3:
        raise ContourError("DEGENERATE_POLYGON", f"Polygon requires at least 3 vertices, got {n}")

    # Check finite coordinates
    for i, p in enumerate(vertices):
        if len(p) != 2 or not math.isfinite(p[0]) or not math.isfinite(p[1]):
            raise ContourError("NON_FINITE_COORDINATE", f"Vertex {i} has non-finite coordinate: {p}")

    # Check non-zero consecutive edges
    for i in range(n):
        j = (i + 1) % n
        edge_len = dist2d(vertices[i], vertices[j])
        if edge_len <= eps:
            raise ContourError(
                "ZERO_LENGTH_EDGE",
                f"Edge {i}->{j} has zero or near-zero length {edge_len:g} cm <= {eps:g}"
            )

    # Check simplicity: no non-adjacent edge intersections
    for i in range(n):
        p1, p2 = vertices[i], vertices[(i + 1) % n]
        for j in range(i + 2, n):
            if (i == 0 and j == n - 1):
                continue  # adjacent at cyclic boundary
            p3, p4 = vertices[j], vertices[(j + 1) % n]
            if segments_intersect_2d(p1, p2, p3, p4, eps=eps):
                raise ContourError(
                    "POLYGON_SELF_INTERSECTION",
                    f"Polygon self-intersects between edge {i} ({p1}->{p2}) and edge {j} ({p3}->{p4})"
                )


# --------------------------------------------------------------------------- #
# 3. CCW Normalization with Stable ID & Openings Mapping
# --------------------------------------------------------------------------- #

@dataclass
class NormalizedContour:
    vertices: list[Point2D]
    segments: list[dict[str, Any]]
    openings: list[dict[str, Any]]
    signed_area: float
    is_ccw: bool
    was_reversed: bool
    closing_knot_stripped: bool


def normalize_contour_ccw(
    raw_vertices: Sequence[Sequence[float]],
    segments: Optional[Sequence[Mapping[str, Any]]] = None,
    openings: Optional[Sequence[Mapping[str, Any]]] = None,
    eps: float = DEFAULT_LINEAR_EPS_CM
) -> NormalizedContour:
    """Normalize contour vertices to CCW orientation.

    If CW, reverses vertices and edge traversal while:
    - Retaining stable segment IDs.
    - Flipping opening s-ranges: s'_min = L - s_max, s'_max = L - s_min.
    - Preserving stable opening IDs.
    - Stripping closing duplicate vertex cleanly.
    """
    pts = [(float(p[0]), float(p[1])) for p in raw_vertices]
    orig_count = len(pts)
    pts = deduplicate_closing_vertex(pts, eps=eps)
    stripped = len(pts) < orig_count

    validate_polygon_simplicity(pts, eps=eps)
    area = polygon_signed_area_2d(pts)
    if abs(area) <= eps * eps:
        raise ContourError("ZERO_AREA_POLYGON", f"Polygon area is near zero: {area:g} cm2")

    n = len(pts)
    was_reversed = False

    # Default segment generation if not provided
    seg_list: list[dict[str, Any]] = []
    if segments is None or len(segments) == 0:
        for i in range(n):
            seg_list.append({
                "id": f"seg_{i + 1}",
                "start_vertex_index": i,
                "end_vertex_index": (i + 1) % n,
            })
    else:
        if len(segments) != n:
            raise ContourError(
                "SEGMENT_COUNT_MISMATCH",
                f"Contour has {n} vertices but {len(segments)} segments were supplied"
            )
        for s in segments:
            seg_list.append(dict(s))

    op_list: list[dict[str, Any]] = [dict(op) for op in (openings or [])]

    if area < 0:
        # Polygon is CW -> reverse to CCW
        was_reversed = True
        # Reversing vertices: new_pts[j] = pts[(n - j) % n]
        # In this mapping, edge i (pts[i]->pts[i+1]) becomes edge running pts[i+1]->pts[i]
        rev_pts = [pts[(n - j) % n] for j in range(n)]

        # Map segment lengths before reversal
        seg_lengths: dict[str, float] = {}
        for seg in seg_list:
            s_idx = seg.get("start_vertex_index")
            e_idx = seg.get("end_vertex_index")
            if s_idx is not None and e_idx is not None:
                L = dist2d(pts[s_idx], pts[e_idx])
            else:
                L = 0.0
            seg_lengths[str(seg.get("id"))] = L

        # Update segments: vertices indices in rev_pts
        rev_segs: list[dict[str, Any]] = []
        for i, seg in enumerate(seg_list):
            s_id = str(seg.get("id"))
            old_s = seg.get("start_vertex_index", i)
            old_e = seg.get("end_vertex_index", (i + 1) % n)
            # Find indices in rev_pts
            new_s = (n - old_e) % n
            new_e = (n - old_s) % n
            new_seg = dict(seg)
            new_seg["start_vertex_index"] = new_s
            new_seg["end_vertex_index"] = new_e
            new_seg["is_reversed"] = True
            rev_segs.append(new_seg)

        # Update openings on reversed segments
        rev_ops: list[dict[str, Any]] = []
        for op in op_list:
            seg_id = str(op.get("segment_id"))
            L = seg_lengths.get(seg_id, 0.0)
            s_range = op.get("s_range_cm")
            new_op = dict(op)
            if s_range and len(s_range) == 2 and L > 0:
                s_min, s_max = float(s_range[0]), float(s_range[1])
                new_s_min = max(0.0, round(L - s_max, 6))
                new_s_max = min(L, round(L - s_min, 6))
                new_op["s_range_cm"] = [new_s_min, new_s_max]
            rev_ops.append(new_op)

        return NormalizedContour(
            vertices=rev_pts,
            segments=rev_segs,
            openings=rev_ops,
            signed_area=-area,
            is_ccw=True,
            was_reversed=True,
            closing_knot_stripped=stripped
        )

    return NormalizedContour(
        vertices=pts,
        segments=seg_list,
        openings=op_list,
        signed_area=area,
        is_ccw=True,
        was_reversed=False,
        closing_knot_stripped=stripped
    )


# --------------------------------------------------------------------------- #
# 4. Safe Contour Offset & 6 Verification Gates
# --------------------------------------------------------------------------- #

@dataclass
class OffsetResult:
    inner_vertices: list[Point2D]
    outer_vertices: list[Point2D]
    distance_cm: float
    inner_area: float
    outer_area: float
    reference_face: str
    verified: bool = True


def safe_contour_offset(
    vertices: Sequence[Point2D],
    distance_cm: float,
    *,
    reference_face: str = "outer",
    miter_limit: float = DEFAULT_MITER_LIMIT,
    eps: float = DEFAULT_LINEAR_EPS_CM
) -> OffsetResult:
    """Derive inner contour from outer (or outward shell from inner) safely.

    Parameters:
    - vertices: CCW simple polygon vertices.
    - distance_cm: positive wall thickness in cm.
    - reference_face: "outer" (inward offset to get inner) or "inner" (outward offset to get outer).
    - miter_limit: maximum allowable miter ratio (default 4.0, ~30 deg min corner angle).
    - eps: numerical linear tolerance.

    Enforces 6 mathematical safety gates. Refuses explicitly if any gate fails.
    """
    if distance_cm <= 0 or not math.isfinite(distance_cm):
        raise ContourOffsetError("INVALID_THICKNESS", f"Thickness must be positive and finite: {distance_cm}")

    pts = [(float(p[0]), float(p[1])) for p in vertices]
    pts = deduplicate_closing_vertex(pts, eps=eps)

    # Gate 1: Simplicity & Non-degeneracy of input polygon
    validate_polygon_simplicity(pts, eps=eps)
    orig_area = polygon_signed_area_2d(pts)
    if orig_area <= 0:
        raise ContourOffsetError("NON_CCW_INPUT", f"Contour must be normalized CCW (area={orig_area:g})")

    n = len(pts)

    # Compute unit normals for each edge
    # In CCW, edge tangent T = (dx/L, dy/L). Outward normal N = (T.y, -T.x)
    normals: list[Vector2D] = []
    edge_vectors: list[Vector2D] = []
    edge_lengths: list[float] = []
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length <= eps:
            raise ContourOffsetError("ZERO_LENGTH_EDGE", f"Edge {i} length <= {eps}")
        edge_vectors.append((dx, dy))
        edge_lengths.append(length)
        normals.append((dy / length, -dx / length))

    # Gate 2: Compute bisector miter vectors & enforce Miter Limit / Acute Corner Gate
    miter_vectors: list[Vector2D] = []
    for i in range(n):
        n_prev = normals[(i - 1) % n]
        n_curr = normals[i]
        denom = 1.0 + dot2d(n_prev, n_curr)

        # Check turn angle / acute corner
        # denom = 1 + cos(turn_angle). For interior angle alpha, turn_angle = 180 - alpha.
        # cos(turn_angle) = -cos(alpha). So denom = 1 - cos(alpha).
        # For alpha = 30 deg, 1 - cos(30 deg) = 1 - 0.8660 = 0.13397.
        # If denom < 0.13397, alpha < 30 deg!
        min_denom = 1.0 - math.cos(math.radians(MIN_INTERIOR_ANGLE_DEG))
        if denom < min_denom:
            raise ContourOffsetError(
                "EXCESSIVE_MITER",
                f"Vertex {i} interior angle is acute (< {MIN_INTERIOR_ANGLE_DEG} deg); denom={denom:g} < {min_denom:g}"
            )

        mx = (n_prev[0] + n_curr[0]) / denom
        my = (n_prev[1] + n_curr[1]) / denom
        m_len = math.hypot(mx, my)

        if m_len > miter_limit:
            raise ContourOffsetError(
                "EXCESSIVE_MITER",
                f"Vertex {i} miter ratio {m_len:g} exceeds limit {miter_limit:g}"
            )
        miter_vectors.append((mx, my))

    # Direction:
    # If reference_face == "outer", we move INWARD by -distance_cm to obtain the inner contour.
    # If reference_face == "inner", we move OUTWARD by +distance_cm to obtain the outer contour.
    sign = -1.0 if reference_face == "outer" else 1.0

    offset_pts: list[Point2D] = []
    for i, p in enumerate(pts):
        ox = p[0] + sign * distance_cm * miter_vectors[i][0]
        oy = p[1] + sign * distance_cm * miter_vectors[i][1]
        offset_pts.append((ox, oy))

    # Gate 3: Inset Collapse Gate (Area Check)
    offset_area = polygon_signed_area_2d(offset_pts)
    if reference_face == "outer":
        # Inward offset: inner area must be strictly positive and strictly less than outer area
        if offset_area <= eps * eps:
            raise ContourOffsetError(
                "INSET_COLLAPSE",
                f"Inner contour collapsed: area {offset_area:g} cm2 <= 0 (thickness {distance_cm} cm exceeds room geometry)"
            )
        if offset_area >= orig_area:
            raise ContourOffsetError(
                "INSET_COLLAPSE",
                f"Inner contour area {offset_area:g} >= outer area {orig_area:g}; geometric inversion detected"
            )
    else:
        # Outward offset: outer area must be strictly greater than inner area
        if offset_area <= orig_area:
            raise ContourOffsetError(
                "INSET_COLLAPSE",
                f"Outer contour area {offset_area:g} <= inner area {orig_area:g}"
            )

    # Gate 4: Edge Direction Preservation (No Local Inversion)
    for i in range(n):
        oa = offset_pts[i]
        ob = offset_pts[(i + 1) % n]
        odx, ody = ob[0] - oa[0], ob[1] - oa[1]
        olen = math.hypot(odx, ody)
        if olen <= eps:
            raise ContourOffsetError(
                "EDGE_COLLAPSE",
                f"Offset edge {i} collapsed to zero length: {olen:g} cm <= {eps:g}"
            )
        edot = dot2d((odx, ody), edge_vectors[i])
        if edot <= 0:
            raise ContourOffsetError(
                "EDGE_COLLAPSE",
                f"Offset edge {i} reversed direction (dot product {edot:g} <= 0); local edge collapse detected"
            )

    # Gate 5: Offset Self-Intersection Gate
    validate_polygon_simplicity(offset_pts, eps=eps)

    # Gate 6: Narrow Notch / Proximity Clearance Gate
    # Any vertex of the inner polygon must not pierce or sit too close to non-incident outer edges
    inner_poly = offset_pts if reference_face == "outer" else pts
    outer_poly = pts if reference_face == "outer" else offset_pts

    for i, iv in enumerate(inner_poly):
        for k in range(n):
            if k == i or k == (i - 1) % n:
                continue  # incident edges
            oa = outer_poly[k]
            ob = outer_poly[(k + 1) % n]
            d = point_to_segment_dist_2d(iv, oa, ob)
            if d < (distance_cm - eps):
                raise ContourOffsetError(
                    "NARROW_NOTCH",
                    f"Inner vertex {i} clearance {d:g} cm to outer edge {k} is below wall thickness {distance_cm:g} cm"
                )

    if reference_face == "outer":
        return OffsetResult(
            inner_vertices=offset_pts,
            outer_vertices=pts,
            distance_cm=distance_cm,
            inner_area=offset_area,
            outer_area=orig_area,
            reference_face="outer"
        )
    else:
        return OffsetResult(
            inner_vertices=pts,
            outer_vertices=offset_pts,
            distance_cm=distance_cm,
            inner_area=orig_area,
            outer_area=offset_area,
            reference_face="inner"
        )


# --------------------------------------------------------------------------- #
# 5. Opening Manifest Contract Builder (S4w -> S5 -> QA)
# --------------------------------------------------------------------------- #

def build_opening_manifest(
    project_id: str,
    storey_id: str,
    contour_id: str,
    normalized_contour: NormalizedContour,
    wall_thickness_cm: float,
    *,
    base_z_cm: float = 0.0,
    top_z_cm: float = 300.0,
    mount_reference: str = "inner_face",
    mount_defaults: Optional[Mapping[str, Any]] = None
) -> list[dict[str, Any]]:
    """Generates the authoritative Opening Manifest records for S4w -> S5 -> QA.

    Calculates exact right-handed orthonormal local frames (T, Outward, Up),
    3x4 transformation matrices, s-ranges, rough openings, clearances, and recess.
    """
    defaults = {
        "recess_cm": 10.0,
        "frame_depth_cm": 12.0,
        "clearance_sides_cm": 1.0,
        "clearance_top_cm": 1.0,
        "clearance_bottom_cm": 0.0,
        "overlap_cm": 1.5,
    }
    if mount_defaults:
        defaults.update(mount_defaults)

    records: list[dict[str, Any]] = []
    verts = normalized_contour.vertices
    n = len(verts)

    # Index segments by id
    seg_by_id: dict[str, dict[str, Any]] = {
        str(s.get("id")): dict(s) for s in normalized_contour.segments
    }

    storey_height = top_z_cm - base_z_cm

    for op in normalized_contour.openings:
        op_id = str(op.get("id"))
        seg_id = str(op.get("segment_id"))
        if seg_id not in seg_by_id:
            raise ContourError("UNRESOLVED_SEGMENT_REF", f"Opening {op_id} references unknown segment {seg_id}")

        seg = seg_by_id[seg_id]
        s_idx = seg.get("start_vertex_index", 0)
        e_idx = seg.get("end_vertex_index", (s_idx + 1) % n)

        va = verts[s_idx]
        vb = verts[e_idx]
        dx, dy = vb[0] - va[0], vb[1] - va[1]
        length = math.hypot(dx, dy)
        if length <= 1e-6:
            raise ContourError("ZERO_LENGTH_SEGMENT", f"Segment {seg_id} has zero length")

        # Orthonormal basis
        tx, ty = dx / length, dy / length
        nx, ny = ty, -tx  # Outward normal (T x Z_up)
        tangent: Vector3D = (tx, ty, 0.0)
        outward: Vector3D = (nx, ny, 0.0)
        up: Vector3D = (0.0, 0.0, 1.0)

        # S-range bounds
        s_range = op.get("s_range_cm", [0.0, 0.0])
        s_min = float(s_range[0])
        s_max = float(s_range[1])
        width_cm = s_max - s_min

        if s_min < 0 or s_max > length or s_min >= s_max:
            raise ContourError(
                "OPENING_OUT_OF_BOUNDS",
                f"Opening {op_id} s_range [{s_min}, {s_max}] outside segment length {length:g}"
            )

        sill_cm = float(op.get("sill_cm", 0.0))
        head_cm = float(op.get("head_cm", storey_height))
        height_cm = head_cm - sill_cm

        if sill_cm < 0 or head_cm > storey_height or sill_cm >= head_cm:
            raise ContourError(
                "OPENING_VERTICAL_BOUNDS",
                f"Opening {op_id} vertical bounds [{sill_cm}, {head_cm}] outside storey height {storey_height:g}"
            )

        # Local Origin in project coordinates
        # At s_min along segment, at sill_z_cm vertically
        sill_z_cm = base_z_cm + sill_cm
        head_z_cm = base_z_cm + head_cm

        # Base origin on the inner face
        p_inner_x = va[0] + tx * s_min
        p_inner_y = va[1] + ty * s_min
        p_inner_z = sill_z_cm

        if mount_reference == "inner_face":
            orig_x, orig_y, orig_z = p_inner_x, p_inner_y, p_inner_z
        elif mount_reference == "outer_face":
            orig_x = p_inner_x + nx * wall_thickness_cm
            orig_y = p_inner_y + ny * wall_thickness_cm
            orig_z = p_inner_z
        elif mount_reference == "wall_center":
            orig_x = p_inner_x + nx * (wall_thickness_cm / 2.0)
            orig_y = p_inner_y + ny * (wall_thickness_cm / 2.0)
            orig_z = p_inner_z
        else:
            raise ContourError("INVALID_MOUNT_REFERENCE", f"Unknown mount reference: {mount_reference}")

        # 3x4 Affine basis matrix [T | N | Up | Origin]
        basis_matrix: Matrix3x4 = (
            (round(tx, 7), round(nx, 7), 0.0, round(orig_x, 5)),
            (round(ty, 7), round(ny, 7), 0.0, round(orig_y, 5)),
            (0.0, 0.0, 1.0, round(orig_z, 5))
        )

        kind = str(op.get("kind", "window"))
        clearance_bottom = 0.0 if kind == "door" else float(defaults["clearance_bottom_cm"])

        record = {
            "manifest_version": "2.0",
            "project_id": project_id,
            "storey_id": storey_id,
            "contour_id": contour_id,
            "segment_id": seg_id,
            "opening_id": op_id,
            "kind": kind,
            "component_type_id": op.get("component_ref", f"COMP_{kind.upper()}"),
            "mount_reference": mount_reference,
            "local_frame": {
                "origin_cm": [round(orig_x, 5), round(orig_y, 5), round(orig_z, 5)],
                "tangent": [round(tx, 7), round(ty, 7), 0.0],
                "outward": [round(nx, 7), round(ny, 7), 0.0],
                "up": [0.0, 0.0, 1.0],
                "basis_matrix": basis_matrix
            },
            "station_along_segment": {
                "s_min_cm": round(s_min, 5),
                "s_max_cm": round(s_max, 5),
                "width_cm": round(width_cm, 5)
            },
            "vertical_bounds": {
                "sill_z_cm": round(sill_z_cm, 5),
                "head_z_cm": round(head_z_cm, 5),
                "height_cm": round(height_cm, 5)
            },
            "rough_opening": {
                "width_cm": round(width_cm, 5),
                "height_cm": round(height_cm, 5),
                "depth_cm": round(wall_thickness_cm, 5)
            },
            "wall_thickness_cm": round(wall_thickness_cm, 5),
            "mounting_parameters": {
                "recess_cm": float(op.get("recess_cm", defaults["recess_cm"])),
                "frame_depth_cm": float(op.get("frame_depth_cm", defaults["frame_depth_cm"])),
                "clearance_sides_cm": float(defaults["clearance_sides_cm"]),
                "clearance_top_cm": float(defaults["clearance_top_cm"]),
                "clearance_bottom_cm": clearance_bottom,
                "overlap_cm": float(defaults["overlap_cm"])
            },
            "provenance": {
                "source_file": "walls.json",
                "source_path": f"{storey_id}.openings[{op_id}]"
            }
        }
        records.append(record)

    return records


# --------------------------------------------------------------------------- #
# 6. Sourced Thickness & Document Validator
# --------------------------------------------------------------------------- #

def validate_walls_v2_document(
    doc: Mapping[str, Any],
    *,
    dimensions_doc: Optional[Mapping[str, Any]] = None,
    assumptions_doc: Optional[Mapping[str, Any]] = None
) -> list[str]:
    """Validate a walls.json document against the closed_inner_contour_shell_v2 contract."""
    errors: list[str] = []

    # 1. Envelope validation
    envelope_keys = ["schema_version", "spec", "project", "units", "source", "status"]
    doc_keys = list(doc.keys())
    for i, k in enumerate(envelope_keys):
        if i >= len(doc_keys) or doc_keys[i] != k:
            errors.append(f"Envelope key {k!r} missing or out of order at position {i}")

    if doc.get("spec") != "walls":
        errors.append(f"spec must be 'walls', got {doc.get('spec')!r}")
    if doc.get("schema_version") != "2.0":
        errors.append(f"schema_version must be '2.0', got {doc.get('schema_version')!r}")

    # 2. Route validation
    route = doc.get("wall_technique")
    if route != "closed_inner_contour_shell_v2":
        errors.append(f"wall_technique must be 'closed_inner_contour_shell_v2', got {route!r}")

    ref_face = doc.get("reference_face")
    if ref_face not in ("inner", "outer"):
        errors.append(f"reference_face must be 'inner' or 'outer', got {ref_face!r}")

    # 3. Storeys validation
    storeys = doc.get("storeys")
    if not isinstance(storeys, list) or len(storeys) == 0:
        errors.append("storeys must be a non-empty array of storey objects")
        return errors

    origins = doc.get("origins")
    if not isinstance(origins, dict):
        errors.append("origins must be an object")
        origins = {}

    for s_idx, storey in enumerate(storeys):
        spath = f"storeys[{s_idx}]"
        if not isinstance(storey, dict):
            errors.append(f"{spath} must be an object")
            continue

        s_id = storey.get("id")
        if not isinstance(s_id, str) or not s_id.strip():
            errors.append(f"{spath}.id must be a non-empty string")

        base_z = storey.get("base_z_cm")
        top_z = storey.get("top_z_cm")
        if base_z is None or top_z is None or not (isinstance(base_z, (int, float)) and isinstance(top_z, (int, float))):
            errors.append(f"{spath} base_z_cm and top_z_cm must be finite numbers")
        elif top_z <= base_z:
            errors.append(f"{spath} top_z_cm ({top_z}) must be strictly greater than base_z_cm ({base_z})")

        # Thickness validation and provenance rule:
        # Missing thickness MUST only come from recorded assumption, builder NEVER invents.
        thickness = storey.get("wall_thickness_cm")
        thickness_path = f"{spath}.wall_thickness_cm"
        top_thickness_path = "wall_thickness_cm"

        if thickness is None:
            # Check assumptions ledger
            found_assumption = False
            if assumptions_doc and isinstance(assumptions_doc.get("assumptions"), list):
                for asm in assumptions_doc["assumptions"]:
                    if isinstance(asm, dict) and asm.get("field_path") in (thickness_path, top_thickness_path, f"walls.json:{thickness_path}"):
                        val = asm.get("value")
                        if isinstance(val, (int, float)) and val > 0:
                            thickness = float(val)
                            found_assumption = True
                            break
            if not found_assumption:
                errors.append(
                    f"{spath}.wall_thickness_cm is missing and not declared in assumptions.json; builder cannot invent thickness"
                )
        elif not isinstance(thickness, (int, float)) or thickness <= 0:
            errors.append(f"{spath}.wall_thickness_cm must be a finite positive number")
        else:
            # Check provenance coverage
            has_prov = (
                thickness_path in origins or
                top_thickness_path in origins or
                f"storeys[{s_idx}]" in origins
            )
            if not has_prov and doc.get("status") == "locked":
                errors.append(f"Missing origins provenance for {thickness_path}")

        # Contour geometry validation
        verts = storey.get("vertices_cm")
        if not isinstance(verts, list) or len(verts) < 3:
            errors.append(f"{spath}.vertices_cm must contain at least 3 vertices")
            continue

        s_face = storey.get("reference_face", ref_face)
        try:
            norm_contour = normalize_contour_ccw(
                verts,
                segments=storey.get("segments"),
                openings=storey.get("openings")
            )
            # If outer, run safe offset check
            if s_face == "outer" and thickness and thickness > 0:
                safe_contour_offset(norm_contour.vertices, thickness, reference_face="outer")
        except ContourError as ce:
            errors.append(f"{spath} geometry error: [{ce.code}] {ce.message}")

        # Openings bounds validation
        ops = storey.get("openings", [])
        if isinstance(ops, list):
            seg_intervals: dict[str, list[tuple[float, float, str]]] = {}
            for op_i, op in enumerate(ops):
                opath = f"{spath}.openings[{op_i}]"
                if not isinstance(op, dict):
                    continue
                seg_ref = op.get("segment_id")
                s_range = op.get("s_range_cm")
                if isinstance(s_range, list) and len(s_range) == 2:
                    lo, hi = float(s_range[0]), float(s_range[1])
                    if lo < 0 or lo >= hi:
                        errors.append(f"{opath}.s_range_cm requires 0 <= lo < hi")
                    else:
                        seg_intervals.setdefault(str(seg_ref), []).append((lo, hi, opath))

            # Non-overlapping check
            for seg_k, intervals in seg_intervals.items():
                intervals.sort()
                for left, right in zip(intervals, intervals[1:]):
                    if right[0] < left[1]:
                        errors.append(f"{right[2]} overlaps {left[2]} on segment {seg_k!r}")

    return errors
