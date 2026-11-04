"""Bounded offline TriMesh-group diagnostics, never native-polygon acceptance.

Input is an extracted JSON result from triangle_view_capture.ms, not the MCP
response wrapper. Every result remains INCOMPLETE: local files/handles and these
queries cannot establish live provenance, native MNMesh faces, or history.
"""
from collections import Counter
from hashlib import sha256
import argparse
import json
import math
from pathlib import Path
import sys


class Incomplete(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Incomplete(message)


def finite_number(value):
    return (type(value) in (int, float) and math.isfinite(value))


def matrix(value):
    return (isinstance(value, list) and len(value) == 4 and
            all(isinstance(row, list) and len(row) == 3 and
                all(finite_number(x) for x in row) for row in value))


def same_json(left, right):
    """JSON numeric 1 == 1.0, but never let booleans impersonate numbers."""
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_json(a, b) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same_json(left[k], right[k]) for k in left)
    if type(left) in (int, float) and type(right) in (int, float):
        return finite_number(left) and finite_number(right) and left == right
    return type(left) is type(right) and left == right


def group_boundary(triangles, group):
    """Derive oriented boundary from actual indexed triangles, not an oracle.

    Refuse anything except one edge-connected, consistently oriented simple
    cycle; this deliberately does not support holes, singularities, or n-gons
    with multiple boundaries. Indices and direction remain from the snapshot.
    """
    edges = {}
    for fid in group:
        face = triangles[fid - 1]
        for i, a in enumerate(face):
            b = face[(i + 1) % 3]
            edges.setdefault(tuple(sorted((a, b))), []).append((fid, a, b))
    require(all(len(uses) in (1, 2) for uses in edges.values()), "nonmanifold group edge")
    adjacent = {fid: set() for fid in group}
    boundary = []
    for uses in edges.values():
        if len(uses) == 1:
            boundary.append(uses[0][1:])
        else:
            left, right = uses
            require(left[1:] == tuple(reversed(right[1:])), "inconsistent interior orientation")
            adjacent[left[0]].add(right[0])
            adjacent[right[0]].add(left[0])
    reached = set()
    pending = [group[0]]
    while pending:
        face = pending.pop()
        if face not in reached:
            reached.add(face)
            pending.extend(adjacent[face] - reached)
    require(reached == set(group), "group is not edge-connected")
    require(len(boundary) >= 3, "group has no simple exterior boundary")
    successor = {}
    predecessors = Counter()
    for a, b in boundary:
        require(a not in successor, "branching boundary")
        successor[a] = b
        predecessors[b] += 1
    require(set(successor) == set(predecessors) and all(x == 1 for x in predecessors.values()),
            "boundary is not one-to-one")
    start = min(successor)
    loop = [start]
    current = start
    for _ in range(len(boundary)):
        current = successor[current]
        if current == start:
            break
        require(current not in loop, "boundary revisits a vertex")
        loop.append(current)
    require(current == start and len(loop) == len(boundary), "multiple or unclosed boundary cycles")
    return loop


def diagnose(raw):
    require(isinstance(raw, dict), "capture is not an object")
    require(raw.get("schema_version") == "p3-triangle-view-1" and
            raw.get("status") == "CAPTURED_NOT_ACCEPTED" and
            raw.get("observation") == "snapshot_triangle_groups_not_native_polygons", "wrong capture header")
    require(type(raw.get("index_base")) is int and raw["index_base"] == 1 and
            raw.get("coordinate_space") == "world", "wrong index base or coordinate space")
    require(raw.get("group_api") == "meshop.getPolysUsingFace" and
            raw.get("ignore_visible_edges") is False and
            type(raw.get("threshold_degrees")) in (int, float) and raw["threshold_degrees"] == 45,
            "unknown grouping method or threshold")
    require(raw.get("native_evaluated_polygon_status") == "INCOMPLETE" and
            raw.get("historical_predelete_grid_status") == "INCOMPLETE", "missing explicit evidence limitations")
    target = raw.get("target")
    require(isinstance(target, dict) and matrix(target.get("object_transform")), "target transform missing")
    for key in ("node_handle", "anim_handle", "base_anim_handle", "modifier_anim_handle"):
        require(isinstance(target.get(key), str) and target[key], "target identity missing: " + key)
    units = raw.get("units")
    require(isinstance(units, dict) and isinstance(units.get("system_type"), str) and
            units["system_type"] and all(finite_number(units.get(k)) and units[k] > 0
                                          for k in ("system_scale", "scene_units_per_cm")), "invalid units")
    verts, tris = raw.get("vertices"), raw.get("triangles")
    require(isinstance(verts, list) and 1 <= len(verts) <= 64 and
            all(isinstance(v, list) and len(v) == 3 and all(finite_number(x) for x in v)
                for v in verts), "invalid vertices or F01 ceiling")
    require(isinstance(tris, list) and 1 <= len(tris) <= 96 and
            all(isinstance(f, list) and len(f) == 3 and
                all(type(i) is int and 1 <= i <= len(verts) for i in f) and len(set(f)) == 3 for f in tris),
            "invalid triangle indices or F01 ceiling")
    visibility, rows = raw.get("triangle_edge_visibility"), raw.get("groups_for_each_triangle")
    require(isinstance(visibility, list) and len(visibility) == len(tris) and
            all(isinstance(row, list) and len(row) == 3 and all(type(v) is bool for v in row)
                for row in visibility), "edge visibility unavailable or malformed")
    require(isinstance(rows, list) and len(rows) == len(tris), "one group query per triangle required")
    canonical = []
    for index, row in enumerate(rows, 1):
        require(isinstance(row, list) and 1 <= len(row) <= len(tris) and
                all(type(x) is int and 1 <= x <= len(tris) for x in row), "invalid group ID")
        require(len(set(row)) == len(row) and index in row, "duplicate or missing self in group")
        canonical.append(tuple(sorted(row)))
    for group in canonical:
        require(all(canonical[fid - 1] == group for fid in group), "group queries are not a partition")
    unique = sorted(set(canonical), key=lambda group: group[0])
    require(sum(len(group) for group in unique) == len(tris), "overlapping or missing groups")
    summaries = []
    for group in unique:
        summaries.append({"triangle_ids": list(group),
                          "derived_boundary_vertex_ids": group_boundary(tris, group)})
    counts = raw.get("mesh_equivalent_node_counts")
    require(isinstance(counts, list) and len(counts) == 2 and
            all(type(x) is int and x >= 0 for x in counts), "invalid separate node counts")
    return {
        "status": "INCOMPLETE",
        "observation_scope": "unverified_input_arrays_not_authenticated_live",
        "triangle_count": len(tris),
        "vertex_count": len(verts),
        "visibility_angle_group_count_not_native_polygon_count": len(unique),
        "derived_group_boundaries_not_native_polygon_loops": summaries,
        "mesh_equivalent_node_counts_face_vertex": counts,
        "limitations": ["group boundaries are derived from the supplied triangle partition",
                        "edge-visibility semantics and grouping require main's live positive and negative calibration",
                        "native evaluated polygon loops and count are unobserved",
                        "historical pre-deletion grid is unobserved",
                        "no live provenance, artifact, timing, or absence-of-intervening-edit authentication"]}


def compare_measurement(raw, measurement):
    """Check two separately supplied channels, without merging or promoting them."""
    diagnose(raw)
    require(isinstance(measurement, dict) and
            measurement.get("schema_version") == "p3-independent-measurement-1" and
            measurement.get("status") == "CAPTURED_NOT_ACCEPTED" and
            measurement.get("stage") == "final", "not a complete final measurement")
    target = measurement.get("target")
    require(isinstance(target, dict), "measurement target missing")
    for key in ("node_handle", "anim_handle", "base_anim_handle", "object_transform"):
        require(same_json(raw["target"][key], target.get(key)), "reported identity/transform mismatch: " + key)
    stack = measurement.get("stack")
    require(isinstance(stack, list) and len(stack) == 1 and isinstance(stack[0], dict) and
            stack[0].get("class") == "Shell" and
            same_json(raw["target"]["modifier_anim_handle"], stack[0].get("anim_handle")),
            "reported Shell identity or stack mismatch")
    require(same_json(raw["units"], measurement.get("units")), "measured unit triple mismatch")
    stage = measurement.get("evaluated")
    require(isinstance(stage, dict) and stage.get("coordinate_space") == "world" and
            type(stage.get("index_base")) is int and stage["index_base"] == 1, "missing final triangle stage")
    require(same_json(raw["vertices"], stage.get("vertices")) and same_json(raw["triangles"], stage.get("triangles")) and
            all(type(i) is int for face in stage["triangles"] for i in face),
            "snapshot array mismatch or reindexing; no substitution")
    require(measurement.get("issues") == [], "measurement has missing or unresolved issues")
    return {"status": "INCOMPLETE", "matched_reported_identity_units_and_indexed_arrays": True,
            "scope": "same supplied values only; not authenticated same object/session or no intervening edits"}


def read_json(path):
    data = Path(path).read_bytes()
    require(len(data) <= 2 * 1024 * 1024, "input exceeds 2 MiB")
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    decoded = json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs,
                         parse_constant=lambda value: (_ for _ in ()).throw(Incomplete("nonfinite JSON")))
    return decoded, sha256(data).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", help="extracted p3-triangle-view-1 JSON, not an MCP wrapper")
    parser.add_argument("--measurement", help="optional full final independent-measurement JSON")
    args = parser.parse_args(argv)
    try:
        raw, digest = read_json(args.capture)
        result = diagnose(raw)
        result["input_sha256"] = digest
        if args.measurement:
            measurement, digest = read_json(args.measurement)
            result["comparison"] = compare_measurement(raw, measurement)
            result["comparison_input_sha256"] = digest
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0  # successful diagnostic execution is NOT evidence acceptance
    except (Incomplete, OSError, UnicodeError, ValueError, RecursionError, OverflowError) as exc:
        print(json.dumps({"status": "INCOMPLETE", "diagnostic_error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
