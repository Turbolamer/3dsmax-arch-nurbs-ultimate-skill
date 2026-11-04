#!/usr/bin/env python3
"""Closed-contour Shell v2 — Production Wall Builder (Stage S4w).

Implements the normative closed_inner_contour_shell_v2 wall generation contract:
- Validates walls.json against schema 2.0 and closed_inner_contour_shell_v2 route.
- Enforces strict thickness provenance (reads assumptions.json on silence, never invents defaults).
- Emits per-storey:
  1. Hidden guide SplineShape (<prefix>_<storey_id>_InnerSpline) tracing closed inner contour.
  2. Single Editable_Poly wall surface with conforming corner indices and whole-floor Z-grid.
  3. Rough opening deletions via polyop.deleteFaces with delIsoVerts:true.
  4. Exactly one outward Shell modifier with straightenCorners:true and certified matIDs.
- Targeted rebuild: deletes strictly owned nodes from the ownership manifest;
  never touches foreign objects or sentinels (e.g. WS_FOREIGN_SENTINEL).
- Zero banned tokens: no formattedPrint, no stopCreating, no bare global fn.
- Emits wall_surface.json (ownership manifest, opening manifest, topology budget, analytical volume/bbox)
  and wall_surface.ms (self-contained MAXScript rebuild script).
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Optional, Sequence, Union

try:
    from . import scene_units
    from . import wall_contour_v2 as wc
except ImportError:
    import scene_units
    import wall_contour_v2 as wc


class BuildRefusal(ValueError):
    """Exception raised when wall geometry cannot be safely planned, validated or emitted."""


def _fmt_float(val: float) -> str:
    """Format float cleanly for MAXScript code output, ensuring decimal point."""
    s = f"{val:.4f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    return s


def _validate_namespace(namespace: str) -> str:
    """Validate MAXScript-safe namespace identifier."""
    if not isinstance(namespace, str) or not re.match(r"^[A-Za-z][A-Za-z0-9_]{0,39}$", namespace):
        raise BuildRefusal(f"Invalid namespace {namespace!r}; must match [A-Za-z][A-Za-z0-9_]{{0,39}}")
    return namespace


def resolve_storey_thickness(
    storey: Mapping[str, Any],
    storey_index: int,
    walls_doc: Mapping[str, Any],
    assumptions_doc: Optional[Mapping[str, Any]] = None,
) -> float:
    """Resolve wall thickness for a storey following the strict provenance law.

    If wall_thickness_cm is absent in the storey and top-level doc, assumptions.json
    must explicitly declare it. The builder never invents defaults.
    """
    # 1. Storey-level declaration
    t = storey.get("wall_thickness_cm")
    if isinstance(t, (int, float)) and not isinstance(t, bool) and t > 0 and math.isfinite(t):
        return float(t)

    # 2. Top-level walls.json declaration
    t = walls_doc.get("wall_thickness_cm")
    if isinstance(t, (int, float)) and not isinstance(t, bool) and t > 0 and math.isfinite(t):
        return float(t)

    # 3. Ledger lookup in assumptions.json
    s_id = str(storey.get("id", f"storey_{storey_index + 1}"))
    candidate_paths = {
        f"storeys[{storey_index}].wall_thickness_cm",
        f"storeys[{storey_index}]",
        f"{s_id}.wall_thickness_cm",
        "wall_thickness_cm",
        f"walls.json:storeys[{storey_index}].wall_thickness_cm",
        f"walls.json:storeys[{storey_index}]",
        f"walls.json:{s_id}.wall_thickness_cm",
        "walls.json:wall_thickness_cm",
    }

    if assumptions_doc and isinstance(assumptions_doc.get("assumptions"), list):
        for asm in assumptions_doc["assumptions"]:
            if isinstance(asm, dict):
                f_path = str(asm.get("field_path", ""))
                if f_path in candidate_paths:
                    val = asm.get("value")
                    if isinstance(val, (int, float)) and not isinstance(val, bool) and val > 0 and math.isfinite(val):
                        return float(val)

    raise BuildRefusal(
        f"wall_thickness_cm is missing for storey {s_id!r} (index {storey_index}) "
        f"and not declared in assumptions.json; builder cannot invent defaults"
    )


def prepare_storey_geometry(
    storey: Mapping[str, Any],
    storey_index: int,
    walls_doc: Mapping[str, Any],
    assumptions_doc: Optional[Mapping[str, Any]],
    namespace: str = "WS",
) -> dict[str, Any]:
    """Analyze and generate geometry structures for a single storey."""
    s_id = str(storey.get("id", f"storey_{storey_index + 1}"))
    base_z = float(storey.get("base_z_cm", 0.0))
    top_z = float(storey.get("top_z_cm", 300.0))
    height = top_z - base_z
    if height <= 0:
        raise BuildRefusal(f"Storey {s_id} has invalid height {height:g} cm (top_z <= base_z)")

    thickness_cm = resolve_storey_thickness(storey, storey_index, walls_doc, assumptions_doc)
    ref_face = str(storey.get("reference_face", walls_doc.get("reference_face", "inner")))
    eps_cm = float(walls_doc.get("numeric_epsilon_cm", wc.DEFAULT_LINEAR_EPS_CM))

    raw_verts = storey.get("vertices_cm")
    if not isinstance(raw_verts, list) or len(raw_verts) < 3:
        raise BuildRefusal(f"Storey {s_id} vertices_cm must contain >= 3 vertices")

    try:
        norm = wc.normalize_contour_ccw(
            raw_verts,
            segments=storey.get("segments"),
            openings=storey.get("openings"),
            eps=eps_cm,
        )
    except wc.ContourError as exc:
        raise BuildRefusal(f"Contour normalization error in storey {s_id}: [{exc.code}] {exc.message}") from exc

    # Offset to determine inner and outer contours
    try:
        if ref_face == "outer":
            offset_res = wc.safe_contour_offset(
                norm.vertices,
                thickness_cm,
                reference_face="outer",
                eps=eps_cm,
            )
            inner_points = offset_res.inner_vertices
            outer_points = offset_res.outer_vertices
        else:
            offset_res = wc.safe_contour_offset(
                norm.vertices,
                thickness_cm,
                reference_face="inner",
                eps=eps_cm,
            )
            inner_points = offset_res.inner_vertices
            outer_points = offset_res.outer_vertices
    except wc.ContourError as exc:
        raise BuildRefusal(f"Safe contour offset refusal in storey {s_id}: [{exc.code}] {exc.message}") from exc

    # Analytical areas
    area_inner = wc.polygon_signed_area_2d(inner_points)
    area_outer = wc.polygon_signed_area_2d(outer_points)
    solid_volume = (area_outer - area_inner) * height

    # Opening manifest generation (S4w -> S5 -> QA)
    project_id = str(walls_doc.get("project", "unnamed_project"))
    contour_id = f"{s_id}_contour"
    opening_records = wc.build_opening_manifest(
        project_id,
        s_id,
        contour_id,
        norm,
        thickness_cm,
        base_z_cm=base_z,
        top_z_cm=top_z,
        mount_reference="inner_face",
    )

    # Deduct opening volumes
    openings_deduction = 0.0
    for op in norm.openings:
        s_rng = op.get("s_range_cm", [0.0, 0.0])
        w = float(s_rng[1]) - float(s_rng[0])
        sill = float(op.get("sill_cm", 0.0))
        head = float(op.get("head_cm", height))
        h = head - sill
        openings_deduction += w * h * thickness_cm

    analytical_volume = solid_volume - openings_deduction

    # Bounding box
    all_x = [p[0] for p in outer_points] + [p[0] for p in inner_points]
    all_y = [p[1] for p in outer_points] + [p[1] for p in inner_points]
    bounds_cm = [
        round(min(all_x), 4),
        round(min(all_y), 4),
        round(base_z, 4),
        round(max(all_x), 4),
        round(max(all_y), 4),
        round(top_z, 4),
    ]

    # Whole-floor Z-grid union
    z_set = {round(base_z, 4), round(top_z, 4)}
    for op in norm.openings:
        sill_z = base_z + float(op.get("sill_cm", 0.0))
        head_z = base_z + float(op.get("head_cm", height))
        z_set.add(round(sill_z, 4))
        z_set.add(round(head_z, 4))
    zlevels = sorted(z_set)

    # Columns and stations along CCW perimeter
    n_pts = len(inner_points)
    seg_by_start = {int(seg.get("start_vertex_index", i)): seg for i, seg in enumerate(norm.segments)}

    cols: list[dict[str, Any]] = []
    for i in range(n_pts):
        seg = seg_by_start.get(i)
        if seg is None:
            # Fallback to index-based segment
            seg = norm.segments[i]
        seg_id = str(seg.get("id", f"seg_{i + 1}"))
        va = inner_points[i]
        vb = inner_points[(i + 1) % n_pts]
        edge_len = wc.dist2d(va, vb)

        seg_ops = [op for op in norm.openings if str(op.get("segment_id")) == seg_id]
        cuts = {0.0, edge_len}
        for op in seg_ops:
            s_rng = op.get("s_range_cm", [0.0, 0.0])
            cuts.add(float(s_rng[0]))
            cuts.add(float(s_rng[1]))
        sorted_cuts = sorted(cuts)

        for lo, hi in zip(sorted_cuts, sorted_cuts[1:]):
            ratio = lo / edge_len if edge_len > 0 else 0.0
            px = va[0] + (vb[0] - va[0]) * ratio
            py = va[1] + (vb[1] - va[1]) * ratio
            cols.append({
                "point": (px, py),
                "segment_id": seg_id,
                "s_min": lo,
                "s_max": hi,
            })

    # 3D Mesh vertices: (row, col) ordered
    wall_vertices: list[list[float]] = []
    for z in zlevels:
        for c in cols:
            wall_vertices.append([round(c["point"][0], 4), round(c["point"][1], 4), round(z, 4)])

    # Guide spline vertices: closed loop at base_z
    guide_vertices: list[list[float]] = []
    for c in cols:
        guide_vertices.append([round(c["point"][0], 4), round(c["point"][1], 4), round(base_z, 4)])

    # Mesh faces and opening face deletions
    count = len(cols)
    faces: list[list[int]] = []
    deleted_faces: list[int] = []

    for row, (z0, z1) in enumerate(zip(zlevels, zlevels[1:])):
        for col_idx, col in enumerate(cols):
            nxt = (col_idx + 1) % count
            v_bl = row * count + col_idx + 1
            v_br = row * count + nxt + 1
            v_tr = (row + 1) * count + nxt + 1
            v_tl = (row + 1) * count + col_idx + 1
            faces.append([v_bl, v_br, v_tr, v_tl])
            face_idx = len(faces)

            # Check if this face falls strictly inside an opening
            for op in norm.openings:
                if str(op.get("segment_id")) != col["segment_id"]:
                    continue
                s_rng = op.get("s_range_cm", [0.0, 0.0])
                op_lo, op_hi = float(s_rng[0]), float(s_rng[1])
                op_sill_z = base_z + float(op.get("sill_cm", 0.0))
                op_head_z = base_z + float(op.get("head_cm", height))

                if (op_lo <= col["s_min"] + eps_cm and col["s_max"] <= op_hi + eps_cm and
                        op_sill_z <= z0 + eps_cm and z1 <= op_head_z + eps_cm):
                    deleted_faces.append(face_idx)
                    break

    # Topology budget verification
    grid_polygons = len(faces)
    active_polygons = grid_polygons - len(deleted_faces)
    eval_triangles = active_polygons * 2

    budget = storey.get("topology_budget")
    if isinstance(budget, dict):
        max_grid = budget.get("max_grid_polygons")
        if max_grid is not None and grid_polygons > int(max_grid):
            raise BuildRefusal(f"Storey {s_id} grid_polygons ({grid_polygons}) exceeds budget ({max_grid})")
        max_base = budget.get("max_base_active_polygons")
        if max_base is not None and active_polygons > int(max_base):
            raise BuildRefusal(f"Storey {s_id} base_active_polygons ({active_polygons}) exceeds budget ({max_base})")
        max_eval = budget.get("max_evaluated_triangles")
        if max_eval is not None and eval_triangles > int(max_eval):
            raise BuildRefusal(f"Storey {s_id} evaluated_triangles ({eval_triangles}) exceeds budget ({max_eval})")

    guide_name = f"{namespace}_{s_id}_InnerSpline"
    wall_name = f"{namespace}_{s_id}"

    return {
        "storey_id": s_id,
        "base_z_cm": base_z,
        "top_z_cm": top_z,
        "wall_thickness_cm": thickness_cm,
        "reference_face": ref_face,
        "guide_name": guide_name,
        "wall_name": wall_name,
        "inner_points": inner_points,
        "outer_points": outer_points,
        "guide_vertices": guide_vertices,
        "wall_vertices": wall_vertices,
        "faces": faces,
        "deleted_faces": deleted_faces,
        "opening_records": opening_records,
        "analytical_volume_cm3": analytical_volume,
        "bounds_cm": bounds_cm,
        "topology": {
            "grid_polygons": grid_polygons,
            "deleted_faces": len(deleted_faces),
            "base_active_polygons": active_polygons,
            "evaluated_triangles": eval_triangles,
        },
    }


def generate_maxscript(
    project_id: str,
    namespace: str,
    storeys_data: Sequence[Mapping[str, Any]],
    owned_nodes: Sequence[str],
) -> str:
    """Generate self-contained MAXScript script for targeted creation/rebuild.

    Guarantees:
    - Only deletes explicitly owned nodes matching owned_nodes.
    - Foreign objects and sentinels (e.g. WS_FOREIGN_SENTINEL) are never touched.
    - Zero banned tokens (no formattedPrint, no stopCreating, no bare global fn).
    - Shell modifier outward with straightenCorners:true and certified matIDs.
    - SplineShape inner guide hidden.
    """
    lines: list[str] = [
        "(",
        "-- ============================================================================",
        "-- Wall Surface Builder v2 (closed_inner_contour_shell_v2)",
        "-- Emitted by scripts/build_wall_v2.py",
        f"-- Project: {project_id}",
        f"-- Namespace: {namespace}",
        "-- Targeted rebuild: deletes strictly owned nodes from ownership manifest.",
        "-- Preserves all foreign nodes and sentinels.",
        "-- ============================================================================",
        "",
        "local ownedNodeNames = #(",
    ]

    for name in owned_nodes:
        lines.append(f'    "{name}",')
    if lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]
    lines.append(")")
    lines.append("")

    lines.extend([
        "for nm in ownedNodeNames do (",
        "    local nd = getNodeByName nm",
        "    if nd != undefined and isValidNode nd do (",
        "        delete nd",
        "    )",
        ")",
        "",
        'local factor = units.decodeValue "1cm"',
        "",
    ])

    for s_data in storeys_data:
        s_id = s_data["storey_id"]
        guide_name = s_data["guide_name"]
        wall_name = s_data["wall_name"]
        thickness = s_data["wall_thickness_cm"]
        guide_verts = s_data["guide_vertices"]
        wall_verts = s_data["wall_vertices"]
        faces = s_data["faces"]
        deleted = s_data["deleted_faces"]

        lines.append(f"-- Storey: {s_id}")
        lines.append("(")

        # Guide Spline
        lines.append("    local guideVerts = #(")
        g_chunks = []
        for v in guide_verts:
            g_chunks.append(f"[{_fmt_float(v[0])},{_fmt_float(v[1])},{_fmt_float(v[2])}]")
        for chunk_idx in range(0, len(g_chunks), 5):
            chunk = ", ".join(g_chunks[chunk_idx:chunk_idx + 5])
            comma = "," if chunk_idx + 5 < len(g_chunks) else ""
            lines.append(f"        {chunk}{comma}")
        lines.append("    )")
        lines.append(f'    local guide = SplineShape name:"{guide_name}"')
        lines.append("    addNewSpline guide")
        lines.append("    for p in guideVerts do addKnot guide 1 #corner #line (p * factor)")
        lines.append("    close guide 1")
        lines.append("    updateShape guide")
        lines.append("    guide.isHidden = true")
        lines.append("")

        # Wall Editable_Poly
        lines.append("    local wallVerts = #(")
        w_chunks = []
        for v in wall_verts:
            w_chunks.append(f"[{_fmt_float(v[0])},{_fmt_float(v[1])},{_fmt_float(v[2])}]")
        for chunk_idx in range(0, len(w_chunks), 5):
            chunk = ", ".join(w_chunks[chunk_idx:chunk_idx + 5])
            comma = "," if chunk_idx + 5 < len(w_chunks) else ""
            lines.append(f"        {chunk}{comma}")
        lines.append("    )")
        lines.append("")

        lines.append("    local wallPolygons = #(")
        f_chunks = []
        for f in faces:
            f_chunks.append(f"#({f[0]},{f[1]},{f[2]},{f[3]})")
        for chunk_idx in range(0, len(f_chunks), 5):
            chunk = ", ".join(f_chunks[chunk_idx:chunk_idx + 5])
            comma = "," if chunk_idx + 5 < len(f_chunks) else ""
            lines.append(f"        {chunk}{comma}")
        lines.append("    )")
        lines.append("")

        del_str = ",".join(str(idx) for idx in deleted)
        lines.append(f'    local wall = Editable_mesh name:"{wall_name}"')
        lines.append("    convertTo wall Editable_Poly")
        lines.append("    for p in wallVerts do polyop.createVert wall (p * factor)")
        lines.append("    for indices in wallPolygons do (")
        lines.append("        polyop.createPolygon wall indices")
        lines.append("    )")
        lines.append(f"    local delFaces = #{{{del_str}}}")
        lines.append("    if delFaces.numberSet > 0 do (")
        lines.append("        polyop.deleteFaces wall delFaces delIsoVerts:true")
        lines.append("    )")
        lines.append("    polyop.setFaceSmoothGroup wall #all 0")
        lines.append("")
        lines.append(
            f"    local sh = Shell innerAmount:0.0 outerAmount:({_fmt_float(thickness)} * factor) "
            "straightenCorners:true segments:1 autoSmooth:false overrideMatID:true matID:3 "
            "overrideInnerMatID:true matInnerID:1 overrideOuterMatID:true matOuterID:2"
        )
        lines.append("    addModifier wall sh")
        lines.append(")")
        lines.append("")

    lines.append("OK")
    lines.append(")")
    lines.append("")
    return "\n".join(lines)


def build_walls_v2(
    project_dir: Union[str, Path],
    out_dir: Optional[Union[str, Path]] = None,
    *,
    namespace: str = "WS",
    system_type: str = "Centimeters",
    system_scale: float = 1.0,
) -> dict[str, Any]:
    """Production builder for closed_inner_contour_shell_v2 wall architecture.

    Parameters:
    - project_dir: path to directory containing walls.json (and optional assumptions.json).
    - out_dir: directory to write wall_surface.json and wall_surface.ms (defaults to project_dir).
    - namespace: prefix for scene nodes (default "WS").
    - system_type: native 3ds Max units.SystemType (e.g. "Centimeters", "Millimeters").
    - system_scale: native 3ds Max units.SystemScale (default 1.0).

    Returns:
    - dict: complete wall_surface ownership manifest and geometry summary.
    """
    proj_path = Path(project_dir).resolve()
    if not proj_path.is_dir():
        raise BuildRefusal(f"project_dir does not exist or is not a directory: {proj_path}")

    target_out = Path(out_dir).resolve() if out_dir is not None else proj_path
    target_out.mkdir(parents=True, exist_ok=True)

    clean_namespace = _validate_namespace(namespace)

    # Unit factor verification
    try:
        scene_units.unit_factor(system_type, system_scale)
    except ValueError as exc:
        raise BuildRefusal(f"Invalid unit configuration: {exc}") from exc

    # Load walls.json
    walls_file = proj_path / "walls.json"
    if not walls_file.is_file():
        raise BuildRefusal(f"walls.json not found in {proj_path}")

    try:
        with open(walls_file, "r", encoding="utf-8") as f:
            walls_doc = json.load(f)
    except Exception as exc:
        raise BuildRefusal(f"Failed to parse {walls_file}: {exc}") from exc

    # Load assumptions.json if present
    assumptions_doc: Optional[dict[str, Any]] = None
    assumptions_file = proj_path / "assumptions.json"
    if assumptions_file.is_file():
        try:
            with open(assumptions_file, "r", encoding="utf-8") as f:
                assumptions_doc = json.load(f)
        except Exception:
            assumptions_doc = None

    # Contract checks
    if walls_doc.get("spec") != "walls":
        raise BuildRefusal(f"spec must be 'walls', got {walls_doc.get('spec')!r}")
    if walls_doc.get("schema_version") != "2.0":
        raise BuildRefusal(f"schema_version must be '2.0', got {walls_doc.get('schema_version')!r}")
    if walls_doc.get("wall_technique") != "closed_inner_contour_shell_v2":
        raise BuildRefusal(
            f"wall_technique must be 'closed_inner_contour_shell_v2', got {walls_doc.get('wall_technique')!r}"
        )

    # Validate document with wall_contour_v2
    validation_errors = wc.validate_walls_v2_document(
        walls_doc,
        assumptions_doc=assumptions_doc,
    )
    if validation_errors:
        raise BuildRefusal(f"walls.json validation errors: {'; '.join(validation_errors)}")

    storeys = walls_doc.get("storeys", [])
    if not isinstance(storeys, list) or len(storeys) == 0:
        raise BuildRefusal("walls.json contains no storeys")

    project_id = str(walls_doc.get("project", "unnamed_project"))

    storeys_data: list[dict[str, Any]] = []
    nodes_manifest: list[dict[str, Any]] = []
    owned_nodes: list[str] = []
    all_openings: list[dict[str, Any]] = []

    total_volume_cm3 = 0.0
    overall_bounds = [float("inf"), float("inf"), float("inf"), float("-inf"), float("-inf"), float("-inf")]

    total_grid_polys = 0
    total_deleted = 0
    total_base_active = 0

    for s_idx, storey in enumerate(storeys):
        s_data = prepare_storey_geometry(
            storey,
            s_idx,
            walls_doc,
            assumptions_doc,
            namespace=clean_namespace,
        )
        storeys_data.append(s_data)

        wall_node_name = s_data["wall_name"]
        guide_node_name = s_data["guide_name"]

        owned_nodes.extend([wall_node_name, guide_node_name])
        nodes_manifest.append({
            "name": wall_node_name,
            "role": "wall_shell",
            "storey_id": s_data["storey_id"],
            "class": "Editable_Poly",
        })
        nodes_manifest.append({
            "name": guide_node_name,
            "role": "inner_guide_spline",
            "storey_id": s_data["storey_id"],
            "class": "SplineShape",
        })

        all_openings.extend(s_data["opening_records"])
        total_volume_cm3 += s_data["analytical_volume_cm3"]

        sb = s_data["bounds_cm"]
        overall_bounds[0] = min(overall_bounds[0], sb[0])
        overall_bounds[1] = min(overall_bounds[1], sb[1])
        overall_bounds[2] = min(overall_bounds[2], sb[2])
        overall_bounds[3] = max(overall_bounds[3], sb[3])
        overall_bounds[4] = max(overall_bounds[4], sb[4])
        overall_bounds[5] = max(overall_bounds[5], sb[5])

        topo = s_data["topology"]
        total_grid_polys += topo["grid_polygons"]
        total_deleted += topo["deleted_faces"]
        total_base_active += topo["base_active_polygons"]

    analytical_bbox = [round(c, 4) for c in overall_bounds]

    # Build wall_surface.json
    wall_surface_doc: dict[str, Any] = {
        "schema_version": "2.0",
        "spec": "wall_surface",
        "project": project_id,
        "units": {"length": "cm", "angle": "deg"},
        "source": {
            "kind": "derived",
            "reference": "walls.json",
            "recorded_at": "2026-11-04T00:00:00Z",
        },
        "status": "locked",
        "wall_technique": "closed_inner_contour_shell_v2",
        "namespace": clean_namespace,
        "nodes": nodes_manifest,
        "owned_nodes": owned_nodes,
        "openings": all_openings,
        "analytical_volume_cm3": round(total_volume_cm3, 4),
        "volume_cm3": round(total_volume_cm3, 4),
        "analytical_bbox_cm": analytical_bbox,
        "bounds_cm": analytical_bbox,
        "topology_budget": {
            "total_grid_polygons": total_grid_polys,
            "total_deleted_faces": total_deleted,
            "total_base_active_polygons": total_base_active,
            "total_evaluated_triangles": total_base_active * 2,
        },
        "storeys": [
            {
                "id": sd["storey_id"],
                "base_z_cm": sd["base_z_cm"],
                "top_z_cm": sd["top_z_cm"],
                "wall_thickness_cm": sd["wall_thickness_cm"],
                "analytical_volume_cm3": round(sd["analytical_volume_cm3"], 4),
                "bounds_cm": sd["bounds_cm"],
                "topology": sd["topology"],
            }
            for sd in storeys_data
        ],
    }

    # Generate MAXScript
    maxscript_content = generate_maxscript(
        project_id,
        clean_namespace,
        storeys_data,
        owned_nodes,
    )

    # Write files
    json_path = target_out / "wall_surface.json"
    ms_path = target_out / "wall_surface.ms"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(wall_surface_doc, f, indent=2)
        f.write("\n")

    with open(ms_path, "w", encoding="utf-8") as f:
        f.write(maxscript_content)

    result = dict(wall_surface_doc)
    result["artifacts"] = {
        "wall_surface_json": str(json_path),
        "wall_surface_ms": str(ms_path),
    }
    result["wall_surface_json_path"] = str(json_path)
    result["wall_surface_ms_path"] = str(ms_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Closed-contour Shell v2 Wall Builder")
    parser.add_argument("--in", "-i", dest="project_dir", required=True, help="Project specs directory")
    parser.add_argument("--out", "-o", dest="out_dir", default=None, help="Output directory")
    parser.add_argument("--namespace", default="WS", help="Node prefix namespace (default: WS)")
    parser.add_argument("--system-type", default="Centimeters", help="3ds Max SystemType (default: Centimeters)")
    parser.add_argument("--system-scale", type=float, default=1.0, help="3ds Max SystemScale (default: 1.0)")

    args = parser.parse_args()
    try:
        res = build_walls_v2(
            args.project_dir,
            out_dir=args.out_dir,
            namespace=args.namespace,
            system_type=args.system_type,
            system_scale=args.system_scale,
        )
        print(f"PASS: Built wall_surface for {res.get('project')} ({len(res.get('nodes', []))} nodes)")
        print(f"Emitted: {res['artifacts']['wall_surface_json']}")
        print(f"Emitted: {res['artifacts']['wall_surface_ms']}")
        return 0
    except BuildRefusal as exc:
        print(f"REFUSAL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
