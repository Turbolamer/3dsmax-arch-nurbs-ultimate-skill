"""Independent, offline Phase 16 P3 straight-wall oracle (stdlib only).

This is NOT a wall emitter or a replacement for validate_specs.py. No emitter,
manifest prediction, MAXScript, installed skill, or live Max API is imported.
See _phase16-p3-oracle-2026-11-02e.md for the audit-local authority/capture APIs.
All coordinates below are physical cm, indices are explicitly zero- or one-based.
PASS means only that the supplied evidence passes these bounded checks; dictionary
contents cannot establish source authenticity, actual live observation or ownership.
"""

from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import json
import math


class OracleProblem(ValueError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def source_digest(document):
    """Canonical semantic JSON hash, NOT a hash of original source file bytes."""
    try:
        raw = json.dumps(document, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise OracleProblem("FAIL", "source is not finite serializable JSON") from exc
    return sha256(raw).hexdigest()


def verify_authority_source(physical, source_bytes, *, locator):
    """Verify reviewed authority's locator/hash against separately read bytes.

    This does NOT parse the source or certify the human's interpretation. The F01
    test independently inspects the plan's actual coordinate/direction sentences.
    Callers of arbitrary sources still need that explicit semantic review.
    """
    evidence = _need(physical, "evidence", "physical authority")
    if not isinstance(source_bytes, bytes):
        raise OracleProblem("INCOMPLETE", "authority source bytes not supplied")
    if evidence.get("locator") != locator or evidence.get("sha256") != sha256(source_bytes).hexdigest():
        raise OracleProblem("FAIL", "reviewed authority source locator/hash mismatch")
    return True


def physical_from_f01_authority(walls, dimensions, authority, *, walls_bytes,
                                source_bytes, reviewer):
    """Explicit adapter for the closed P3 direction record and actual F01 plan.

    Only this named, source-inspected F01 case is interpreted automatically. The
    physical thickness and opening rectangles are literal separate plan values,
    NOT copied from the wall or generated manifest. Other projects should provide
    an independently reviewed `physical` record to predict(), not misuse F01.
    This adapter raises OracleProblem on unavailable/contradictory evidence.
    """
    keys = {"schema_version", "project", "wall_run_id", "walls_sha256", "source_file",
            "source_sha256", "source_location", "inner_start_cm", "inner_end_cm",
            "base_z_cm", "top_z_cm", "outward"}
    if not isinstance(authority, dict) or set(authority) != keys:
        raise OracleProblem("FAIL", "not the closed P3 direction authority object")
    if authority["schema_version"] != "p3-direction-authority-1":
        raise OracleProblem("FAIL", "unsupported direction authority schema")
    if not isinstance(walls_bytes, bytes) or not isinstance(source_bytes, bytes):
        raise OracleProblem("INCOMPLETE", "actual wall/authority source bytes are required")
    if (authority["walls_sha256"] != sha256(walls_bytes).hexdigest()
            or authority["source_sha256"] != sha256(source_bytes).hexdigest()):
        raise OracleProblem("FAIL", "wall/source authority byte hash mismatch")

    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise OracleProblem("FAIL", "duplicate key in authority-bound wall bytes")
            result[key] = value
        return result

    try:
        decoded = json.loads(walls_bytes.decode("utf-8"), object_pairs_hook=pairs,
                             parse_constant=lambda value: (_ for _ in ()).throw(
                                 OracleProblem("FAIL", "nonfinite wall JSON")))
    except (UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, OracleProblem):
            raise
        raise OracleProblem("FAIL", "unreadable wall JSON bytes") from exc
    if source_digest(decoded) != source_digest(walls):
        raise OracleProblem("FAIL", "authority-bound wall bytes differ from supplied source dict")
    if (not isinstance(authority["source_file"], str)
            or authority["source_file"].replace("\\", "/") != "Audit/AGENT_PLAN_poly_surface_shell.md"):
        raise OracleProblem("INCOMPLETE", "F01 source adapter supports only the actual analytical plan")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise OracleProblem("INCOMPLETE", "independent reviewer identity is required")
    if not isinstance(authority["source_location"], str) or not authority["source_location"]:
        raise OracleProblem("INCOMPLETE", "source location is missing")
    try:
        text = source_bytes.decode("utf-8")
        section = text.split("### G.1 Численный эталон F01", 1)[1].split("### G.2", 1)[0]
    except (UnicodeError, IndexError) as exc:
        raise OracleProblem("INCOMPLETE", "actual analytical F01 source section is missing") from exc
    for sentence in (
            "Стена в сантиметрах: `u = 0…400`, `Y = 0`, `Z = 0…300`, наружу `(0,−1,0)`, толщина **30**.",
            "Дверь: `u = 50…150`, `Z = 0…210`. Окно: `u = 230…330`, `Z = 90…210`.",
            "Станции: `u = [0, 50, 150, 230, 330, 400]`, `Z = [0, 90, 210, 300]`."):
        if sentence not in section:
            raise OracleProblem("INCOMPLETE", "F01 source differs; fresh independent semantic review required")
    runs = _need(walls, "wall_runs", "walls")
    if not isinstance(runs, list) or len(runs) != 1 or not isinstance(runs[0], dict):
        raise OracleProblem("INCOMPLETE", "F01 authority needs exactly one source run")
    run_id = _need(runs[0], "id", "run")
    if authority["project"] != walls.get("project") or authority["wall_run_id"] != run_id:
        raise OracleProblem("FAIL", "direction authority project/run mismatch")
    if (_vec(authority["inner_start_cm"], 2) != (0, 0)
            or _vec(authority["inner_end_cm"], 2) != (400, 0)
            or _num(authority["base_z_cm"]) != 0 or _num(authority["top_z_cm"]) != 300
            or _vec(authority["outward"], 2) != (0, -1)):
        raise OracleProblem("FAIL", "direction authority contradicts independently read F01 plan")
    ops = _need(walls, "openings", "walls")
    if not isinstance(ops, list):
        raise OracleProblem("FAIL", "wall openings is not an array")
    by_kind = {kind: [op for op in ops if isinstance(op, dict) and op.get("kind") == kind]
               for kind in ("door", "window")}
    if len(ops) != 2 or any(len(group) != 1 for group in by_kind.values()):
        raise OracleProblem("FAIL", "F01 needs exactly one door and one window")
    # IDs are identity bindings only; physical numerical rectangles come from G.1.
    door_id = _need(by_kind["door"][0], "id", "door")
    window_id = _need(by_kind["window"][0], "id", "window")
    return {"project": walls["project"], "wall_run_id": run_id, "reference_face": "inner",
            "source_hashes": {"walls": source_digest(walls), "dimensions": source_digest(dimensions)},
            "start_cm": [0, 0], "end_cm": [400, 0], "base_z_cm": 0, "top_z_cm": 300,
            "thickness_cm": 30, "outward": [0, -1],
            "openings": [{"id": door_id, "kind": "door", "u_range_cm": [50, 150], "sill_cm": 0, "head_cm": 210},
                         {"id": window_id, "kind": "window", "u_range_cm": [230, 330], "sill_cm": 90, "head_cm": 210}],
            "evidence": {"locator": authority["source_file"]+"#"+authority["source_location"],
                         "sha256": sha256(source_bytes).hexdigest(), "reviewer": reviewer, "reviewed": True}}


def _need(obj, key, context):
    if not isinstance(obj, dict) or key not in obj:
        raise OracleProblem("INCOMPLETE", context + ": missing " + key)
    return obj[key]


def _num(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise OracleProblem("FAIL", "non-numeric/boolean coordinate or tolerance")
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise OracleProblem("FAIL", "number overflows binary64") from exc
    if not math.isfinite(result) or (isinstance(value, int) and int(result) != value):
        raise OracleProblem("FAIL", "nonfinite or lossy integer number")
    return result


def _vec(value, count):
    if not isinstance(value, (list, tuple)) or len(value) != count:
        raise OracleProblem("FAIL", "wrong vector shape")
    return tuple(_num(x) for x in value)


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _mul(a, k):
    return tuple(x * k for x in a)


def _dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _norm(a):
    return math.hypot(*a)


def _cycle_key(face):
    face = tuple(face)
    variants = []
    for values in (face, tuple(reversed(face))):
        variants.extend(values[i:] + values[:i] for i in range(len(values)))
    return min(variants)


def _check(checks, name, condition, detail):
    checks.append({"check": name, "status": "PASS" if condition else "FAIL",
                   "detail": detail})


def _status(checks):
    states = {x["status"] for x in checks}
    return "FAIL" if "FAIL" in states else "INCOMPLETE" if "INCOMPLETE" in states else "PASS"


def _problem(checks, name, exc):
    checks.append({"check": name, "status": exc.status, "detail": str(exc)})


def _components(adjacency):
    remaining = set(adjacency)
    count = 0
    while remaining:
        count += 1
        queue = [remaining.pop()]
        while queue:
            for other in adjacency[queue.pop()]:
                if other in remaining:
                    remaining.remove(other)
                    queue.append(other)
    return count


def topology(vertex_count, faces):
    """Recompute edges, components, orientation, duplicate faces and vertex links.

    faces use zero-based IDs. Isolated retained vertices are counted separately;
    Euler characteristic uses active vertices, not dead/retained isolated elements.
    A boundary component is NOT a connected component of the surface.
    """
    edges = defaultdict(list)
    links = defaultdict(list)
    face_graph = {i: set() for i in range(len(faces))}
    canonical = Counter()
    for fid, face in enumerate(faces):
        if len(face) < 3 or len(set(face)) != len(face):
            raise OracleProblem("FAIL", "repeated vertex or undersized face")
        if any(type(i) is not int or i < 0 or i >= vertex_count for i in face):
            raise OracleProblem("FAIL", "face index is invalid")
        canonical[_cycle_key(face)] += 1
        for i, a in enumerate(face):
            b = face[(i+1) % len(face)]
            edges[tuple(sorted((a, b)))].append((fid, a, b))
            links[a].append((face[i-1], b))
    boundary = {e: uses for e, uses in edges.items() if len(uses) == 1}
    boundary_graph = defaultdict(set)
    for a, b in boundary:
        boundary_graph[a].add(b)
        boundary_graph[b].add(a)
    for uses in edges.values():
        for fid, _, _ in uses:
            face_graph[fid].update(x[0] for x in uses if x[0] != fid)
    bad_links = []
    for vertex, pairs in links.items():
        graph = defaultdict(set)
        degree = Counter()
        for a, b in pairs:
            graph[a].add(b)
            graph[b].add(a)
            degree[a] += 1
            degree[b] += 1
        degrees = sorted(degree.values())
        valid_degrees = (all(x == 2 for x in degrees) if vertex not in boundary_graph
                         else degrees.count(1) == 2 and all(x in (1, 2) for x in degrees))
        if _components(graph) != 1 or not valid_degrees:
            bad_links.append(vertex)
    nonmanifold = sum(len(x) > 2 for x in edges.values())
    inconsistent = sum(len(x) == 2 and x[0][1:] != tuple(reversed(x[1][1:]))
                       for x in edges.values())
    return {
        "vertices": vertex_count, "active_vertices": len(links),
        "isolated_vertices": vertex_count-len(links), "edges": len(edges),
        "faces": len(faces), "boundary_edges": len(boundary),
        "interior_edges": sum(len(x) == 2 for x in edges.values()),
        "boundary_components": _components(boundary_graph),
        "surface_components": _components(face_graph),
        "euler": len(links)-len(edges)+len(faces),
        "retained_euler": vertex_count-len(edges)+len(faces),
        "nonmanifold_edges": nonmanifold, "inconsistent_edges": inconsistent,
        "duplicate_faces": sum(x-1 for x in canonical.values()),
        "bad_vertex_links": len(bad_links),
        "boundary_cycles": all(len(x) == 2 for x in boundary_graph.values()),
    }


def _openings(values, run_id, length, height):
    if not isinstance(values, list):
        raise OracleProblem("FAIL", "openings must be an array")
    result = []
    ids = set()
    for item in values:
        if not isinstance(item, dict):
            raise OracleProblem("FAIL", "opening is not an object")
        if item.get("wall_run_id", run_id) != run_id:
            raise OracleProblem("INCOMPLETE", "opening belongs to unsupported additional run")
        ident = _need(item, "id", "opening")
        if not isinstance(ident, str) or not ident or ident in ids:
            raise OracleProblem("FAIL", "empty/duplicate opening id")
        ids.add(ident)
        kind = _need(item, "kind", "opening")
        if kind not in ("window", "door"):
            raise OracleProblem("FAIL", "unknown opening kind")
        lo, hi = _vec(_need(item, "u_range_cm", "opening"), 2)
        sill = _num(_need(item, "sill_cm", "opening"))
        head = _num(_need(item, "head_cm", "opening"))
        if not (0 <= lo < hi <= length and 0 <= sill < head <= height):
            raise OracleProblem("FAIL", "opening outside run or degenerate")
        if lo == 0 or hi == length or head == height:
            raise OracleProblem("INCOMPLETE", "P3.1 excludes end/top-touching openings")
        result.append({"id": ident, "kind": kind, "u_range_cm": [lo, hi],
                       "sill_cm": sill, "head_cm": head})
    result.sort(key=lambda x: (x["u_range_cm"][0], x["id"]))
    for first, second in zip(result, result[1:]):
        if first["u_range_cm"][1] > second["u_range_cm"][0]:
            raise OracleProblem("FAIL", "opening u-intervals overlap")
        if first["u_range_cm"][1] == second["u_range_cm"][0]:
            raise OracleProblem("INCOMPLETE", "P3.1 requires strictly separated opening u intervals")
    return result


def _frame(record, unit_epsilon):
    start = _vec(_need(record, "start_cm", "physical record/run"), 2)
    end = _vec(_need(record, "end_cm", "physical record/run"), 2)
    base = _num(_need(record, "base_z_cm", "physical record/run"))
    top = _num(_need(record, "top_z_cm", "physical record/run"))
    thick = _num(_need(record, "thickness_cm", "physical record/run"))
    outward = _vec(_need(record, "outward", "physical record/run"), 2)
    delta = _sub(end, start)
    length = _norm(delta)
    if not math.isfinite(length) or not math.isfinite(top-base):
        raise OracleProblem("FAIL", "wall extent arithmetic overflows")
    if length <= 0 or top <= base or thick <= 0:
        raise OracleProblem("FAIL", "nonpositive wall geometry")
    tangent = _mul(delta, 1/length)
    if abs(_norm(outward)-1) > unit_epsilon or abs(_dot(tangent, outward)) > unit_epsilon:
        raise OracleProblem("FAIL", "outward must be unit and perpendicular")
    # Shell's geometric normal is exactly perpendicular, not the slightly skew
    # near-unit supplied vector. Use the independently sourced vector for its sign.
    geometric = (tangent[1], -tangent[0])
    outward = geometric if _dot(geometric, outward) > 0 else _mul(geometric, -1)
    return start, end, base, top, thick, outward, tangent, length


def _geometry(record, openings, eps, unit_eps, max_cells):
    start, end, base, top, thick, normal, tangent, length = _frame(record, unit_eps)
    height = top-base
    us = sorted({0.0, length} | {u for op in openings for u in op["u_range_cm"]})
    vs = sorted({0.0, height} | {v for op in openings for v in (op["sill_cm"], op["head_cm"])})
    if any(b-a <= 2*eps for stations in (us, vs) for a, b in zip(stations, stations[1:])):
        raise OracleProblem("INCOMPLETE", "station separation cannot be matched unambiguously")
    if (len(us)-1)*(len(vs)-1) > max_cells:
        raise OracleProblem("INCOMPLETE", "oracle operational cell limit exceeded")
    if thick <= 2*eps:
        raise OracleProblem("INCOMPLETE", "thickness layers cannot be matched unambiguously")
    nx = len(us)
    points = [(start[0]+tangent[0]*u, start[1]+tangent[1]*u, base+v)
              for v in vs for u in us]
    if any(not all(math.isfinite(x) for x in p) for p in points):
        raise OracleProblem("FAIL", "world coordinate overflow")
    # Standard (u,v) has normal t cross +Z. Authority determines sign, NOT walls.outward.
    reverse = _dot(_cross((tangent[0], tangent[1], 0), (0, 0, 1)),
                   (normal[0], normal[1], 0)) < 0
    grid, active, removed_labels = [], [], []
    for j in range(len(vs)-1):
        for i in range(len(us)-1):
            face = (j*nx+i, j*nx+i+1, (j+1)*nx+i+1, (j+1)*nx+i)
            if reverse:
                face = tuple(reversed(face))
            grid.append(face)
            removed = any(op["u_range_cm"][0] <= us[i] and us[i+1] <= op["u_range_cm"][1]
                          and op["sill_cm"] <= vs[j] and vs[j+1] <= op["head_cm"]
                          for op in openings)
            if removed:
                removed_labels.append(j*(nx-1)+i+1)
            else:
                active.append(face)
    base_topology = topology(len(points), active)
    if not active:
        raise OracleProblem("FAIL", "no remaining wall surface")
    if base_topology["bad_vertex_links"] or not base_topology["boundary_cycles"]:
        raise OracleProblem("INCOMPLETE", "singular/touching opening boundary is unsupported")
    if base_topology["isolated_vertices"]:
        raise OracleProblem("INCOMPLETE", "Shell handling of retained isolated vertices is not established")
    edge_uses = defaultdict(list)
    for face in active:
        for i, a in enumerate(face):
            b = face[(i+1) % len(face)]
            edge_uses[tuple(sorted((a, b)))].append((a, b))
    boundary = [uses[0] for uses in edge_uses.values() if len(uses) == 1]
    count = len(points)
    n3 = (normal[0], normal[1], 0)
    shell_points = points + [_add(p, _mul(n3, thick)) for p in points]
    shell_faces = [tuple(reversed(face)) for face in active]
    shell_faces += [tuple(i+count for i in face) for face in active]
    shell_faces += [(a, b, b+count, a+count) for a, b in boundary]
    shell_topology = topology(len(shell_points), shell_faces)
    area = length*height-math.fsum((op["u_range_cm"][1]-op["u_range_cm"][0]) *
                                 (op["head_cm"]-op["sill_cm"]) for op in openings)
    volume = area*thick
    if not math.isfinite(volume) or volume <= 0:
        raise OracleProblem("FAIL", "area/volume overflow or nonpositive result")
    return {"u_stations_cm": us, "v_stations_cm": vs,
            "removed_row_major_labels": removed_labels,
            "source_area_cm2": area, "volume_cm3": volume,
            "physical_outward": list(n3), "thickness_cm": thick,
            "bounds_cm": {"min": [min(p[k] for p in shell_points) for k in range(3)],
                          "max": [max(p[k] for p in shell_points) for k in range(3)]},
            "grid_topology": topology(len(points), grid), "base_topology": base_topology,
            "shell_topology": shell_topology, "evaluated_triangles": 2*len(shell_faces),
            "grid_vertices_cm": points, "grid_faces": grid, "base_faces": active,
            "shell_vertices_cm": shell_points, "shell_faces": shell_faces,
            "openings": openings}


def predict(walls, dimensions, physical, *, max_cells=10000):
    """Predict from locked sources and separately authoritative physical values.

    `physical` is an audit-local reviewed authority record, never a wall manifest.
    Missing evidence returns INCOMPLETE; contradictory available evidence FAIL.
    The function does not mutate inputs or implement the full G-1..G-100 validator.
    """
    checks = []
    result = {"status": "INCOMPLETE", "checks": checks, "prediction": None}
    try:
        if type(max_cells) is not int or not 1 <= max_cells <= 100000:
            raise OracleProblem("FAIL", "invalid oracle max_cells limit")
        for document, name, spec in ((walls, "walls", "walls"), (dimensions, "dimensions", "dimensions")):
            if _need(document, "status", name) != "locked":
                raise OracleProblem("INCOMPLETE", name + " is not locked")
            if _need(document, "spec", name) != spec:
                raise OracleProblem("FAIL", "wrong source spec")
            if _need(document, "units", name) != {"length": "cm", "angle": "deg"}:
                raise OracleProblem("FAIL", "source units are not cm/deg")
        project = _need(walls, "project", "walls")
        if dimensions.get("project") != project:
            raise OracleProblem("FAIL", "source project mismatch")
        if walls.get("schema_version") != "1.1" or dimensions.get("schema_version") not in ("1.0", "1.1"):
            raise OracleProblem("FAIL", "unsupported schema")
        if walls.get("wall_technique") != "poly_surface_shell_v1" or walls.get("reference_face") != "inner":
            raise OracleProblem("INCOMPLETE", "unsupported wall route/reference face")
        runs = _need(walls, "wall_runs", "walls")
        if not isinstance(runs, list) or len(runs) != 1 or walls.get("upper_returns") != []:
            raise OracleProblem("INCOMPLETE", "oracle supports exactly one standalone run and no returns")
        run = runs[0]
        ident = _need(run, "id", "run")
        eps = _num(_need(walls, "numeric_epsilon_cm", "walls"))
        unit_eps = _num(_need(walls, "numeric_unit_epsilon", "walls"))
        if not 0 < eps <= 0.01 or not 0 < unit_eps <= 0.001:
            raise OracleProblem("FAIL", "numeric epsilon outside grammar bounds")
        tolerances = _need(walls, "tolerances", "walls")
        if tolerances != _need(dimensions, "tolerances", "dimensions"):
            raise OracleProblem("FAIL", "inherited tolerances differ")
        linear = _num(_need(tolerances, "linear_cm", "tolerances"))
        if linear <= 0:
            raise OracleProblem("FAIL", "linear tolerance must be positive")
        wf = _frame(run, unit_eps)
        source_openings = _openings(_need(walls, "openings", "walls"), ident, wf[7], wf[3]-wf[2])
        blocks = _need(walls, "blocks", "walls")
        if not isinstance(blocks, list) or len(blocks) != 1:
            raise OracleProblem("INCOMPLETE", "P3.1 requires exactly one block")
        matches = [x for x in blocks if isinstance(x, dict) and x.get("id") == run.get("block_id")]
        if len(matches) != 1:
            raise OracleProblem("FAIL", "block does not resolve uniquely")
        zlo, zhi = _vec(_need(matches[0], "z_range_cm", "block"), 2)
        if not zlo <= wf[2] < wf[3] <= zhi:
            raise OracleProblem("FAIL", "run outside block z interval")
        ref = _need(run, "contour_ref", "run")
        prefix = "dimensions.json:facades:"
        if not isinstance(ref, str) or not ref.startswith(prefix) or not ref[len(prefix):]:
            raise OracleProblem("FAIL", "unsupported facade selector")
        facades = _need(dimensions, "facades", "dimensions")
        if not isinstance(facades, list):
            raise OracleProblem("FAIL", "facades is not an array")
        selected = [x for x in facades if isinstance(x, dict) and x.get("id") == ref[len(prefix):]]
        if len(selected) != 1:
            raise OracleProblem("FAIL", "facade selector does not resolve uniquely")
        fs = _vec(_need(selected[0], "start_corner_cm", "facade"), 2)
        fe = _vec(_need(selected[0], "end_corner_cm", "facade"), 2)
        fl = _norm(_sub(fe, fs))
        if fl <= 0:
            raise OracleProblem("FAIL", "facade has zero length")
        ft = _mul(_sub(fe, fs), 1/fl)
        along = [_dot(_sub(p, fs), ft) for p in wf[:2]]
        offsets = [_norm(_sub(_sub(p, fs), _mul(ft, u))) for p, u in zip(wf[:2], along)]
        _check(checks, "SOURCE_CONTOUR", max(offsets) <= linear and along[0] >= -linear
               and along[1] <= fl+linear and along[1] > along[0], "directed facade subsegment")
        digests = {"walls": source_digest(walls), "dimensions": source_digest(dimensions)}
        result.update({"project": project, "wall_run_id": ident, "source_hashes": digests,
                       "epsilon_cm": eps, "unit_epsilon": unit_eps})
        if not isinstance(physical, dict):
            raise OracleProblem("INCOMPLETE", "independent physical authority is missing")
        if physical.get("project") != project or physical.get("wall_run_id") != ident:
            raise OracleProblem("FAIL", "physical authority project/run mismatch")
        if _need(physical, "source_hashes", "physical authority") != digests:
            raise OracleProblem("FAIL", "physical authority is not bound to these source dicts")
        evidence = _need(physical, "evidence", "physical authority")
        for field in ("locator", "sha256", "reviewer"):
            value = _need(evidence, field, "physical authority evidence")
            if not isinstance(value, str) or not value.strip():
                raise OracleProblem("INCOMPLETE", "physical evidence field is empty: " + field)
        if (len(evidence["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in evidence["sha256"])):
            raise OracleProblem("FAIL", "physical source hash is not SHA-256")
        if evidence.get("reviewed") is not True:
            raise OracleProblem("INCOMPLETE", "physical source has not been independently reviewed")
        if physical.get("reference_face") != "inner":
            raise OracleProblem("INCOMPLETE", "authority does not establish inner reference face")
        pf = _frame(physical, unit_eps)
        physical_openings = _openings(_need(physical, "openings", "physical authority"), ident,
                                      pf[7], pf[3]-pf[2])
        _check(checks, "SOURCE_PHYSICAL_GEOMETRY", all(_norm(_sub(a, b)) <= eps for a, b in zip(wf[:2], pf[:2]))
               and all(abs(wf[i]-pf[i]) <= eps for i in (2, 3, 4)),
               "run endpoints, base/top and thickness versus independent authority")
        _check(checks, "SOURCE_PHYSICAL_DIRECTION", _norm(_sub(wf[5], pf[5])) <= unit_eps,
               "declared outward versus independently established physical outside")
        _check(checks, "SOURCE_OPENINGS", source_openings == physical_openings,
               "rough opening identities, kind and rectangles versus independent authority; no implicit dimensions opening join")
        prediction = _geometry(physical, physical_openings, eps, unit_eps, max_cells)
        result["prediction"] = prediction
        prediction["authority_supplied_outward"] = list(_vec(physical["outward"], 2))
        prediction["wall_supplied_outward"] = list(_vec(run["outward"], 2))
        if (prediction["grid_topology"]["faces"] > 32 or prediction["grid_topology"]["vertices"] > 64
                or prediction["evaluated_triangles"] > 256 or len(physical_openings) > 6):
            raise OracleProblem("INCOMPLETE", "exceeds initial P3.1 absolute planning caps (not live admission)")
        result["authority_evidence"] = deepcopy(evidence)
        budget = _need(run, "topology_budget", "run")
        expected_budget = {"max_grid_polygons", "max_base_active_polygons", "max_evaluated_triangles"}
        if not isinstance(budget, dict) or set(budget) != expected_budget:
            raise OracleProblem("FAIL", "topology budget is not the closed three-ceiling object")
        for key, value in budget.items():
            if type(value) is not int or value < 0:
                raise OracleProblem("FAIL", "budget is not a nonnegative integer")
        result["budget"] = deepcopy(budget)
        counts = (prediction["grid_topology"]["faces"], prediction["base_topology"]["faces"], prediction["evaluated_triangles"])
        for key, count in zip(("max_grid_polygons", "max_base_active_polygons", "max_evaluated_triangles"), counts):
            _check(checks, "PREDICTED_"+key.upper(), count <= budget[key], str(count)+" <= "+str(budget[key]))
    except OracleProblem as exc:
        _problem(checks, "PREDICTION_INPUT", exc)
    result["status"] = _status(checks)
    return result


def adapt_capture(capture, *, cm_per_scene_unit, index_base):
    """Small separate adapter: raw audit-local capture -> normalized cm payload.

    Raw stage keys: grid/base/evaluated, vertices, faces; evaluated also triangles.
    No missing arrays are manufactured. Evidence is passed through, not certified.
    Unknown actual emitter/runtime wire formats must get their own explicit adapter.
    """
    factor = _num(cm_per_scene_unit)
    if factor <= 0 or type(index_base) is not int or index_base not in (0, 1):
        raise OracleProblem("FAIL", "invalid explicit capture scale/index base")
    output = {"evidence": deepcopy(capture.get("evidence"))}
    for name in ("grid", "base", "evaluated"):
        if name not in capture:
            continue
        stage = deepcopy(capture[name])
        vertices = _need(stage, "vertices", "raw "+name)
        stage["vertices_cm"] = [list(_mul(_vec(v, 3), factor)) for v in vertices]
        del stage["vertices"]
        stage["index_base"] = index_base
        output[name] = stage
    return output


def adapt_independent_measurement(raw, evidence, *, grid_raw=None):
    """Normalize the prepared measure.ms full JSON, without scene transformations.

    Schema is p3-independent-measurement-1. This is separate from emitter wire
    formats. The snapshotAsMesh channel is already WORLD space: divide by the
    measured units-per-cm exactly once, never multiply by target.object_transform.
    Reported summary counts, areas, normals, volumes or bounds are NOT substituted
    for actual arrays. Missing grid and polygon loops remain genuinely absent.
    The measurement owner's separate adapter.py is compatibility-tested, not
    imported here; either adapter's normalized geometry works with the core.
    """
    if _need(raw, "schema_version", "full independent capture") != "p3-independent-measurement-1":
        raise OracleProblem("FAIL", "unknown independent measurement schema")
    if raw.get("status") != "CAPTURED_NOT_ACCEPTED" or raw.get("stage") != "final":
        raise OracleProblem("INCOMPLETE", "full final observation required, not a grid/error/path envelope")
    units = _need(raw, "units", "full independent capture")
    factor = _num(_need(units, "scene_units_per_cm", "captured units"))
    if factor <= 0:
        raise OracleProblem("FAIL", "measured scene_units_per_cm must be positive")
    if not isinstance(evidence, dict):
        raise OracleProblem("INCOMPLETE", "explicit independent evidence binding is required")
    output = {"evidence": deepcopy(evidence)}

    def stage(value):
        if _need(value, "index_base", "raw stage") != 1 or type(value["index_base"]) is not int:
            raise OracleProblem("FAIL", "independent capture stage must be explicitly one-based")
        if _need(value, "coordinate_space", "raw stage") != "world":
            raise OracleProblem("FAIL", "independent capture must contain world-space positions")
        adapted = adapt_capture({"base": value}, cm_per_scene_unit=1/factor, index_base=1)["base"]
        return adapted

    for name in ("base", "evaluated"):
        if name in raw:
            output[name] = stage(raw[name])
    if grid_raw is not None:
        if (_need(grid_raw, "schema_version", "grid capture") != raw["schema_version"]
                or grid_raw.get("status") != "CAPTURED_NOT_ACCEPTED" or grid_raw.get("stage") != "grid"):
            raise OracleProblem("INCOMPLETE", "separate actual predeletion grid capture is required")
        if _need(grid_raw, "units", "grid capture") != units:
            raise OracleProblem("FAIL", "grid/final captured unit pairs differ")
        final_target = _need(raw, "target", "final capture")
        grid_target = _need(grid_raw, "target", "grid capture")
        for key in ("anim_handle", "node_handle", "base_anim_handle", "object_transform"):
            if _need(final_target, key, "final target") != _need(grid_target, key, "grid target"):
                raise OracleProblem("FAIL", "grid/final measured identity differs: "+key)
        output["grid"] = stage(_need(grid_raw, "grid", "grid capture"))
    return output


def check_independent_capture(predicted, raw, evidence, *, grid_raw=None, expected_units=None):
    """Assess full measure.ms JSON with explicit source/artifact binding.

    Returns all available geometry checks even if unrelated property-read issues
    or missing stage/polygon evidence keep acceptance INCOMPLETE. expected_units
    is the independently locked exact {system_type,system_scale,scene_units_per_cm}
    triple; its absence is INCOMPLETE, never an inferred equal-factor PASS.
    """
    try:
        normalized = adapt_independent_measurement(raw, evidence, grid_raw=grid_raw)
    except OracleProblem as exc:
        checks = deepcopy(predicted.get("checks", []))
        _problem(checks, "INDEPENDENT_CAPTURE_ADAPTER", exc)
        return {"status": _status(checks), "checks": checks, "measured": {},
                "evidence_scope": "unestablished"}
    result = check_measurements(predicted, normalized)
    checks = result["checks"]
    try:
        for key, expected in (("evidence_origin", "independent_read_only_scene_queries"),
                              ("length_unit", "scene_unit"), ("index_base", 1)):
            observed = _need(raw, key, "full raw capture")
            _check(checks, "INDEPENDENT_CAPTURE_"+key.upper(), observed == expected and type(observed) is type(expected),
                   "full raw capture header versus the inspected measurement schema")
    except OracleProblem as exc:
        _problem(checks, "INDEPENDENT_CAPTURE_HEADERS", exc)
    try:
        issues = _need(raw, "issues", "independent capture")
        if not isinstance(issues, list):
            raise OracleProblem("FAIL", "capture issues is not an array")
        if issues:
            raise OracleProblem("INCOMPLETE", "capture reports unresolved property/measurement issues: "+str(issues))
        _check(checks, "INDEPENDENT_CAPTURE_ISSUES", True, "full raw capture reports no unresolved issues")
    except OracleProblem as exc:
        _problem(checks, "INDEPENDENT_CAPTURE_ISSUES", exc)
    try:
        if not isinstance(expected_units, dict):
            raise OracleProblem("INCOMPLETE", "independently locked expected unit triple is missing")
        keys = {"system_type", "system_scale", "scene_units_per_cm"}
        if set(expected_units) != keys:
            raise OracleProblem("FAIL", "expected unit triple has wrong keys")
        units = _need(raw, "units", "independent capture")
        observed = {key: _need(units, key, "captured units") for key in keys}
        for values in (expected_units, observed):
            if not isinstance(values["system_type"], str) or not values["system_type"]:
                raise OracleProblem("FAIL", "invalid captured/expected system type")
            if _num(values["system_scale"]) <= 0 or _num(values["scene_units_per_cm"]) <= 0:
                raise OracleProblem("FAIL", "invalid captured/expected numeric units")
        _check(checks, "INDEPENDENT_CAPTURE_UNITS", observed == expected_units,
               "exact measured system type, scale AND units-per-cm versus independent locked triple")
    except OracleProblem as exc:
        _problem(checks, "INDEPENDENT_CAPTURE_UNITS", exc)
    result["status"] = _status(checks)
    return result


def _read_vertices(stage):
    vertices = _need(stage, "vertices_cm", "capture mesh")
    if not isinstance(vertices, list):
        raise OracleProblem("FAIL", "vertices must be an array")
    if len(vertices) > 10000:
        raise OracleProblem("INCOMPLETE", "offline measurement vertex cap exceeded")
    return [_vec(v, 3) for v in vertices]


def _measurement_profiles(checks):
    """Scoped status summaries, never a waiver of the full evidence requirement."""
    required = {
        "base": {"BASE_INTEGRITY", "BASE_TOPOLOGY", "BASE_COVERAGE", "BASE_NORMALS", "BASE_SOURCE_AREA"},
        "evaluated_triangles": {"EVALUATED_PHYSICAL_DIRECTION", "EVALUATED_BOUNDS", "TRIANGLE_CLOSED_MANIFOLD",
                                "TRIANGLE_COUNT", "TRIANGLE_TOPOLOGY", "TRIANGLE_VOLUME",
                                "TRIANGLE_VOID_AND_SOLID_COVERAGE", "TRIANGLE_NORMALS"},
    }
    profiles = {}
    for name, names in required.items():
        relevant = [c for c in checks if c["check"] in names]
        present = {c["check"] for c in relevant}
        failures = [c["check"] for c in checks if c["status"] == "FAIL" and
                    (c["check"] in names or (name == "base" and c["check"] == "BASE_CAPTURE") or
                     (name == "evaluated_triangles" and c["check"] == "TRIANGLE_CAPTURE"))]
        missing = sorted(names-present)
        status = "FAIL" if failures else "INCOMPLETE" if missing or _status(relevant) != "PASS" else "PASS"
        profiles[name] = {"status": status, "missing_checks": missing, "failed_checks": failures,
                          "scope": "target_geometry_only_not_source_or_capture_authentication"}
    return profiles


def _read_mesh(stage, *, triangles=False):
    vertices = _read_vertices(stage)
    index_base = _need(stage, "index_base", "capture mesh")
    if type(index_base) is not int or index_base not in (0, 1):
        raise OracleProblem("FAIL", "index_base must be explicitly 0 or 1")
    key = "triangles" if triangles else "faces"
    raw = _need(stage, key, "capture mesh")
    if not isinstance(raw, list):
        raise OracleProblem("FAIL", key+" must be an array")
    if len(raw) > 20000:
        raise OracleProblem("INCOMPLETE", "offline measurement face cap exceeded")
    faces = []
    for face in raw:
        if not isinstance(face, (list, tuple)) or any(type(i) is not int for i in face):
            raise OracleProblem("FAIL", "noninteger mesh index")
        if len(face) != (3 if triangles else 4):
            raise OracleProblem("FAIL", "bounded capture requires triangles/quads respectively")
        faces.append(tuple(i-index_base for i in face))
    stats = topology(len(vertices), faces)
    return vertices, faces, stats


def _match_vertices(actual, expected, eps):
    if len(actual) != len(expected):
        raise OracleProblem("FAIL", "actual vertex count differs from analytical surface")
    # Spatial buckets do NOT weld/quantize points: every candidate must pass actual
    # distance and a one-to-one assignment. Adjacent buckets are explicitly searched.
    cell_size = 2*eps
    buckets = defaultdict(list)
    for i, point in enumerate(expected):
        cell = tuple(math.floor(x/cell_size) for x in point)
        buckets[cell].append(i)
    result, used = [], set()
    for point in actual:
        cell = tuple(math.floor(x/cell_size) for x in point)
        found = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for i in buckets.get((cell[0]+dx, cell[1]+dy, cell[2]+dz), ()):
                        if _norm(_sub(point, expected[i])) <= eps:
                            found.append(i)
        if len(found) != 1 or found[0] in used:
            raise OracleProblem("FAIL", "unmatched/ambiguous/duplicate actual vertex")
        used.add(found[0])
        result.append(found[0])
    return result


def _face_vector(vertices, face):
    origin = vertices[face[0]]
    vectors = [_cross(_sub(vertices[face[i]], origin), _sub(vertices[face[i+1]], origin))
               for i in range(1, len(face)-1)]
    return tuple(math.fsum(x[k] for x in vectors)/2 for k in range(3))


def _area(vertices, faces):
    return math.fsum(_norm(_face_vector(vertices, face)) for face in faces)


def _measure_stage(checks, name, stage, expected_vertices, expected_faces, eps, unit_eps):
    vertices, faces, stats = _read_mesh(stage)
    _check(checks, name+"_INTEGRITY", all(stats[k] == 0 for k in
           ("isolated_vertices", "nonmanifold_edges", "inconsistent_edges", "duplicate_faces", "bad_vertex_links"))
           and stats["boundary_cycles"], str(stats))
    expected_stats = topology(len(expected_vertices), expected_faces)
    _check(checks, name+"_TOPOLOGY", stats == expected_stats, "recomputed active and retained topology")
    mapping = _match_vertices(vertices, expected_vertices, eps)
    mapped = [tuple(mapping[i] for i in face) for face in faces]
    actual_keys = Counter(_cycle_key(f) for f in mapped)
    expected_keys = Counter(_cycle_key(f) for f in expected_faces)
    _check(checks, name+"_COVERAGE", actual_keys == expected_keys,
           "one-to-one analytical patches; detects missing/filled openings and equal-volume substitutions")
    expected_by_key = {_cycle_key(f): f for f in expected_faces}
    normal_ok = True
    for face, indices in zip(mapped, faces):
        reference = expected_by_key.get(_cycle_key(face))
        if reference is None:
            normal_ok = False
            continue
        av = _face_vector(vertices, indices)
        ev = _face_vector(expected_vertices, reference)
        if _norm(av) <= 0 or _norm(ev) <= 0:
            normal_ok = False
        elif _dot(av, ev)/(_norm(av)*_norm(ev)) < 1-unit_eps:
            normal_ok = False
    _check(checks, name+"_NORMALS", normal_ok, "all face normals versus physical analytical patch normals")
    return vertices, faces, stats, mapping


def check_measurements(predicted, measurements):
    """Assess normalized actual geometry, separately from source predictions.

    All three actual stages (grid/base/evaluated) and their full arrays are needed
    for PASS. Aggregate echoed counts/volume/bbox never substitute for arrays.
    """
    checks = list(deepcopy(predicted.get("checks", [])))
    result = {"status": "INCOMPLETE", "checks": checks, "measured": {},
              "evidence_scope": "unestablished"}
    p = predicted.get("prediction")
    if p is None:
        checks.append({"check": "MEASUREMENT_PREREQUISITE", "status": "INCOMPLETE",
                       "detail": "no complete analytical prediction"})
        result["status"] = _status(checks)
        return result
    if not isinstance(measurements, dict):
        measurements = {}
    try:
        evidence = _need(measurements, "evidence", "measurements")
        scope = _need(evidence, "kind", "capture evidence")
        if scope not in ("scene_capture", "synthetic_test"):
            raise OracleProblem("INCOMPLETE", "unknown observation evidence scope")
        result["evidence_scope"] = scope
        for key in ("capture_id", "artifact_sha256"):
            value = _need(evidence, key, "capture evidence")
            if not isinstance(value, str) or not value:
                raise OracleProblem("INCOMPLETE", "empty capture evidence field: "+key)
        if len(evidence["artifact_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in evidence["artifact_sha256"]):
            raise OracleProblem("FAIL", "artifact_sha256 is not SHA-256")
        captured_hashes = _need(evidence, "source_hashes", "capture evidence")
        captured_project = _need(evidence, "project", "capture evidence")
        captured_run = _need(evidence, "wall_run_id", "capture evidence")
        captured_unit = _need(evidence, "length_unit", "capture evidence")
        _check(checks, "CAPTURE_BINDING", captured_hashes == predicted["source_hashes"]
               and captured_project == predicted["project"] and captured_run == predicted["wall_run_id"]
               and captured_unit == "cm", "capture/source/project/run/physical unit binding")
    except OracleProblem as exc:
        _problem(checks, "CAPTURE_EVIDENCE", exc)
    eps, unit_eps = predicted["epsilon_cm"], predicted["unit_epsilon"]
    outputs = {}
    for name, expected_vertices, expected_faces in (
            ("grid", p["grid_vertices_cm"], p["grid_faces"]),
            ("base", p["grid_vertices_cm"], p["base_faces"]),
            ("evaluated", p["shell_vertices_cm"], p["shell_faces"])):
        try:
            stage = _need(measurements, name, "measurements")
            # Direction comes directly from actual positions, BEFORE correspondence:
            # a reversed shell with the same volume must still get a named FAIL.
            if name == "evaluated":
                raw_vertices = _read_vertices(stage)
                origin = p["grid_vertices_cm"][0]
                distances = [_dot(_sub(v, origin), p["physical_outward"]) for v in raw_vertices]
                _check(checks, "EVALUATED_PHYSICAL_DIRECTION", bool(distances)
                       and abs(min(distances)) <= eps and abs(max(distances)-p["thickness_cm"]) <= eps
                       and all(min(abs(d), abs(d-p["thickness_cm"])) <= eps for d in distances),
                       "actual signed displacement is [0,+physical thickness], with inner face unchanged")
                if raw_vertices:
                    bounds = {"min": [min(v[k] for v in raw_vertices) for k in range(3)],
                              "max": [max(v[k] for v in raw_vertices) for k in range(3)]}
                    _check(checks, "EVALUATED_BOUNDS", all(abs(bounds[side][k]-p["bounds_cm"][side][k]) <= eps
                           for side in ("min", "max") for k in range(3)), "bounds versus independent authority")
                    result["measured"]["bounds_cm"] = bounds
            # Retain actual counts/budget evidence even if correspondence later fails.
            _, _, captured_stats = _read_mesh(stage)
            result["measured"][name+"_topology"] = captured_stats
            output = _measure_stage(checks, name.upper(), stage, expected_vertices, expected_faces, eps, unit_eps)
            outputs[name] = output
            result["measured"][name+"_topology"] = output[2]
            if name == "base":
                area = _area(output[0], output[1])
                # Coordinate uncertainty bound, not a physical design tolerance.
                area_limit = math.fsum(2*eps*(_norm(_sub(output[0][f[1]], output[0][f[0]])) +
                                             _norm(_sub(output[0][f[3]], output[0][f[0]]))) + 4*eps*eps for f in output[1])
                _check(checks, "BASE_SOURCE_AREA", abs(area-p["source_area_cm2"]) <= area_limit,
                       "actual polygon area versus authority rectangle-minus-openings")
                result["measured"]["source_area_cm2"] = area
        except (OracleProblem, OverflowError, ValueError) as exc:
            if not isinstance(exc, OracleProblem):
                exc = OracleProblem("INCOMPLETE", "coordinate matching exceeds numeric capability")
            _problem(checks, name.upper()+"_CAPTURE", exc)
    # Actual evaluated triangle mesh is assessed even when outward correspondence
    # failed, retaining the equal-volume/reversed-direction counterexample.
    try:
        stage = _need(measurements, "evaluated", "measurements")
        vertices, triangles, stats = _read_mesh(stage, triangles=True)
        result["measured"]["triangle_topology"] = stats
        _check(checks, "TRIANGLE_CLOSED_MANIFOLD", bool(triangles) and stats["boundary_edges"] == 0
               and all(stats[k] == 0 for k in ("isolated_vertices", "nonmanifold_edges", "inconsistent_edges",
                                             "duplicate_faces", "bad_vertex_links")),
               "closed oriented edge incidence AND vertex links, no duplicates or isolated vertices")
        _check(checks, "TRIANGLE_COUNT", len(triangles) == p["evaluated_triangles"], "actual evaluated triangles")
        expected_triangles = [tri for quad in p["shell_faces"]
                              for tri in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3]))]
        expected_triangle_topology = topology(len(p["shell_vertices_cm"]), expected_triangles)
        _check(checks, "TRIANGLE_TOPOLOGY", stats == expected_triangle_topology,
               "actual triangle V/E/F, components, Euler, boundary, orientation and vertex links")
        reference = vertices[0] if vertices else (0, 0, 0)
        contributions = [_dot(_sub(vertices[f[0]], reference),
                              _cross(_sub(vertices[f[1]], reference), _sub(vertices[f[2]], reference)))/6
                         for f in triangles]
        volume = math.fsum(contributions)
        # Conservative positional uncertainty: sweep each analytical surface by eps.
        volume_limit = 4*eps*_area(p["shell_vertices_cm"], p["shell_faces"])
        _check(checks, "TRIANGLE_VOLUME", volume > 0 and abs(volume-p["volume_cm3"]) <= volume_limit,
               "signed actual triangle volume versus independent source area x thickness")
        result["measured"]["signed_volume_cm3"] = volume
        result["measured"]["absolute_volume_cm3"] = abs(volume)
        mapping = _match_vertices(vertices, p["shell_vertices_cm"], eps)
        mapped = [tuple(mapping[i] for i in f) for f in triangles]
        # Each rectangle must contain exactly two actual triangles, with its four
        # boundary edges once and exactly one shared diagonal twice. No ray-cast or
        # "no open edges" shortcut substitutes for void/solid coverage.
        patches = defaultdict(list)
        membership = defaultdict(list)
        for i, f in enumerate(p["shell_faces"]):
            for vertex in f:
                membership[vertex].append(i)
        for tri, actual_tri in zip(mapped, triangles):
            options = set(membership[tri[0]]) & set(membership[tri[1]]) & set(membership[tri[2]])
            if len(options) != 1:
                raise OracleProblem("FAIL", "triangle crosses or fills an analytical opening/patch")
            patches[options.pop()].append((tri, actual_tri))
        coverage = True
        triangle_normals = True
        for i, quad in enumerate(p["shell_faces"]):
            pair = [entry[0] for entry in patches[i]]
            actual_edges = Counter(tuple(sorted((f[k], f[(k+1) % 3]))) for f in pair for k in range(3))
            quad_edges = {tuple(sorted((quad[k], quad[(k+1) % 4]))) for k in range(4)}
            coverage &= (len(pair) == 2 and all(actual_edges[e] == 1 for e in quad_edges)
                         and sorted(actual_edges.values()) == [1, 1, 1, 1, 2])
            ev = _face_vector(p["shell_vertices_cm"], quad)
            for _, actual_tri in patches[i]:
                av = _face_vector(vertices, actual_tri)
                triangle_normals &= (_norm(av) > 0 and
                                     _dot(av, ev)/(_norm(av)*_norm(ev)) >= 1-unit_eps)
        _check(checks, "TRIANGLE_VOID_AND_SOLID_COVERAGE", coverage,
               "exact two-triangle coverage of every authority skin and reveal rectangle; no door threshold")
        _check(checks, "TRIANGLE_NORMALS", triangle_normals,
               "each actual triangle orientation agrees with its independent physical patch")
    except (OracleProblem, OverflowError, ValueError) as exc:
        if not isinstance(exc, OracleProblem):
            exc = OracleProblem("INCOMPLETE", "numeric triangle capability exceeded")
        _problem(checks, "TRIANGLE_CAPTURE", exc)
    budget = predicted.get("budget")
    if budget is not None:
        for name, key, label in (("grid", "max_grid_polygons", "faces"),
                                 ("base", "max_base_active_polygons", "faces"),
                                 ("triangle", "max_evaluated_triangles", "faces")):
            stats = result["measured"].get(name+"_topology")
            if stats is not None:
                _check(checks, "ACTUAL_"+key.upper(), stats[label] <= budget[key], "actual count versus declared ceiling")
    result["status"] = _status(checks)
    result["profiles"] = _measurement_profiles(checks)
    return result


def assess(walls, dimensions, physical, measurements, *, max_cells=10000):
    """Convenience composition; core prediction and capture checks remain separate."""
    return check_measurements(predict(walls, dimensions, physical, max_cells=max_cells), measurements)
