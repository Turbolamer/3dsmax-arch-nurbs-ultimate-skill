"""Independent nonidentity coordinate-channel calibration; no emitter imports.

Input is JSON actually returned by calibrate_snapshot.ms, or explicitly synthetic
test data. No transformed snapshot correction: bad world coordinates must FAIL.
"""

import math


def _points(value, count):
    if not isinstance(value, list) or len(value) != count:
        raise ValueError("wrong coordinate-array size")
    result = []
    for row in value:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError("wrong point shape")
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in row):
            raise ValueError("nonfinite/nonnumeric coordinate")
        result.append(tuple(row))
    return result


def transform_once(points, rows):
    """MAXScript row-vector affine convention, computed from scalar raw values."""
    return [tuple(sum(p[i] * rows[i][axis] for i in range(3)) + rows[3][axis]
                  for axis in range(3)) for p in points]


def assess_snapshot_calibration(raw, *, epsilon_scene_units=1e-4):
    """Check translated/rotated one-quad capture, without trusting reported PASS.

    A single capture may discriminate translation, rotation or both. Main should
    retain separate translated and rotated calibration captures; each returns
    motion flags. Rigid transform only (scale/shear rejected), no identity admission.
    This validates supplied observations, not their scene authenticity.
    """
    if not isinstance(raw, dict) or raw.get("schema_version") != "p3-snapshot-calibration-1" or raw.get("status") != "CAPTURED_NOT_ACCEPTED":
        raise ValueError("complete calibration capture required")
    if type(raw.get("index_base")) is not int or raw["index_base"] != 1:
        raise ValueError("explicit one-based indexes required")
    eps = epsilon_scene_units
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) or not math.isfinite(eps) or eps <= 0:
        raise ValueError("invalid positive epsilon")
    local = _points(raw.get("base_vertices_local"), 4)
    matrix = _points(raw.get("object_transform"), 4)
    observed = _points(raw.get("snapshot_vertices_world"), 4)
    base_world = _points(raw.get("base_vertices_world_once"), 4)
    bbox = _points(raw.get("node_bounds_world"), 2)
    translated = math.dist(matrix[3], (0, 0, 0)) > eps
    rotated = any(math.dist(matrix[i], tuple(int(i == j) for j in range(3))) > eps for i in range(3))
    if not translated and not rotated:
        raise ValueError("identity placement cannot discriminate this fault")
    for i in range(3):
        for j in range(3):
            if abs(sum(matrix[i][k]*matrix[j][k] for k in range(3)) - int(i == j)) > eps:
                raise ValueError("calibration requires a rigid transform, not scale/shear")
    determinant = (matrix[0][0]*(matrix[1][1]*matrix[2][2]-matrix[1][2]*matrix[2][1])
                   - matrix[0][1]*(matrix[1][0]*matrix[2][2]-matrix[1][2]*matrix[2][0])
                   + matrix[0][2]*(matrix[1][0]*matrix[2][1]-matrix[1][1]*matrix[2][0]))
    if abs(determinant - 1) > eps:
        raise ValueError("calibration requires proper rotation, not a mirror")
    if raw.get("base_faces") is None or len(raw["base_faces"]) != 1 or sorted(raw["base_faces"][0]) != [1, 2, 3, 4]:
        raise ValueError("actual one-quad base face required")
    triangles = raw.get("snapshot_triangles")
    if not isinstance(triangles, list) or len(triangles) != 2 or any(not isinstance(t, list) or len(t) != 3 or len(set(t)) != 3 or any(type(i) is not int or i < 1 or i > 4 for i in t) for t in triangles):
        raise ValueError("actual two-triangle snapshot required")
    expected = transform_once(local, matrix)
    double_transformed = transform_once(expected, matrix)

    def set_matches(actual, wanted):
        remaining = list(wanted)
        for p in actual:
            matches = [i for i, q in enumerate(remaining) if math.dist(p, q) <= eps]
            if len(matches) != 1:
                return False
            remaining.pop(matches[0])
        return not remaining

    expected_bbox = [tuple(min(p[axis] for p in expected) for axis in range(3)),
                     tuple(max(p[axis] for p in expected) for axis in range(3))]
    discriminates = not set_matches(expected, double_transformed)
    checks = {
        "NONIDENTITY_DISCRIMINATES_DOUBLE_TRANSFORM": discriminates,
        "BASE_LOCAL_TIMES_MATRIX_ONCE": set_matches(base_world, expected),
        "SNAPSHOT_ALREADY_WORLD": set_matches(observed, expected),
        "SNAPSHOT_NOT_DOUBLE_TRANSFORMED": not set_matches(observed, double_transformed),
        "NODE_WORLD_BBOX": all(math.dist(a, b) <= eps for a, b in zip(bbox, expected_bbox)),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "translation_exercised": translated, "rotation_exercised": rotated,
            "scope": "supplied calibration observations, not live authenticity"}
