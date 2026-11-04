#!/usr/bin/env python3
"""Assess actual full reversed runtime output; no Max call and no echo geometry.

Input capture is the raw console string (UTF-8 text), not its surrounding wire
JSON. Main retains wire evidence and checks its ok/error/markers independently.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from prepare_controls import digest, strict_json


def parse_capture(text: str):
    stages = {}
    counts = {}
    pattern = re.compile(r"P3_CONTROL_(CAPTURE|VERTEX|FACE|TRIANGLE)\|([^\r\n]+)")
    for match in pattern.finditer(text):
        kind, value = match.groups()
        parts = value.split("|")
        if kind == "CAPTURE":
            if len(parts) != 4 or not parts[0].startswith("stage="):
                raise ValueError("malformed capture header")
            stage = parts[0][6:]
            if stage not in ("grid", "base", "evaluated") or stage in stages:
                raise ValueError("duplicate/unknown actual stage")
            counts[stage] = {p.split("=")[0]: int(p.split("=")[1]) for p in parts[1:]}
            stages[stage] = {"vertices": [], "faces": [], "triangles": []}
        else:
            if len(parts) != 3 or parts[0] not in stages:
                raise ValueError("capture data before stage/invalid line")
            stage, index, raw = parts
            key = {"VERTEX": "vertices", "FACE": "faces", "TRIANGLE": "triangles"}[kind]
            array = strict_json(raw.encode())
            if int(index) != len(stages[stage][key]) + 1 or not isinstance(array, list):
                raise ValueError("nonsequential/duplicate actual ID or bad capture payload")
            stages[stage][key].append(array)
    if set(stages) != {"grid", "base", "evaluated"}:
        raise ValueError("full three-stage actual runtime capture required")
    for stage, arrays in stages.items():
        if any(len(arrays[k]) != counts[stage].get(k) for k in arrays):
            raise ValueError("truncated actual capture stage " + stage)
    return stages


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--controls", required=True)
    p.add_argument("--capture", required=True)
    p.add_argument("--walls", required=True)
    p.add_argument("--dimensions", required=True)
    p.add_argument("--authority", required=True)
    p.add_argument("--source", default=str(ROOT / "Audit" / "AGENT_PLAN_poly_surface_shell.md"))
    p.add_argument("--reviewer", required=True)
    a = p.parse_args(argv)
    try:
        controls = Path(a.controls).resolve()
        index = strict_json((controls / "control-index.json").read_bytes())
        variants = [v for v in index["variants"] if v["kind"] == "reverse_winding"]
        if len(variants) != 1:
            raise ValueError("missing exact reversed test artifact identity")
        v = variants[0]
        if digest((controls / v["script"]).read_bytes()) != v["sha256"]:
            raise ValueError("altered test bytes changed since preparation")
        text = Path(a.capture).read_text(encoding="utf-8")
        if ("P3_CREATED|identity=" + v["identity"]) not in text:
            raise ValueError("full altered runtime did not commit; no winding-control success")
        if any(marker in text for marker in ("__MCP_MS_ERR__", "P3_REFUSED|", "P3_INCOMPLETE_RESIDUAL|")):
            raise ValueError("runtime error/refusal in capture; incomplete winding control")
        stages = parse_capture(text)
        oracle_path = ROOT / "Audit" / "phase16_p3_oracle.py"
        spec = importlib.util.spec_from_file_location("p3_independent_winding_oracle", oracle_path)
        oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(oracle)
        wb = Path(a.walls).read_bytes()
        walls = strict_json(wb)
        dimensions = strict_json(Path(a.dimensions).read_bytes())
        authority = strict_json(Path(a.authority).read_bytes())
        physical = oracle.physical_from_f01_authority(walls, dimensions, authority,
                     walls_bytes=wb, source_bytes=Path(a.source).read_bytes(), reviewer=a.reviewer)
        prediction = oracle.predict(walls, dimensions, physical)
        if prediction["status"] != "PASS":
            raise ValueError("clean independent source prediction did not pass")
        # Grid/base/evaluated emitted arrays are actual API readback, not copied
        # predictions. Oracle requires evaluated QUADS separately from triangles;
        # current runtime capture only provides actual evaluated triangles. Supply
        # no fabricated quads: the full oracle remains INCOMPLETE for that channel.
        # This narrower check independently measures winding and scalar volume.
        grid = stages["grid"]
        base = stages["base"]
        evaluated = stages["evaluated"]
        scale = 0.1  # actual scene is mm/1, checked by main harness, never inferred from bad expected pair
        verts = [[x * scale for x in point] for point in evaluated["vertices"]]
        triangles = [[int(i) - 1 for i in face] for face in evaluated["triangles"]]
        if (not verts or not triangles or any(len(t) != 3 or any(i < 0 or i >= len(verts) for i in t) for t in triangles)):
            raise ValueError("invalid actual evaluated triangle arrays")
        import math
        volume = math.fsum(oracle._dot(verts[t[0]], oracle._cross(verts[t[1]], verts[t[2]])) / 6 for t in triangles)
        expected_volume = prediction["prediction"]["volume_cm3"]
        normal = prediction["prediction"]["physical_outward"]
        origin = prediction["prediction"]["grid_vertices_cm"][0]
        distances = [oracle._dot(oracle._sub(vv, origin), normal) for vv in verts]
        eps = prediction["epsilon_cm"]
        thickness = prediction["prediction"]["thickness_cm"]
        desired_direction = abs(min(distances)) <= eps and abs(max(distances) - thickness) <= eps
        reversed_direction = abs(min(distances) + thickness) <= eps and abs(max(distances)) <= eps
        topology = oracle.topology(len(verts), triangles)
        normals = []
        for stage in (grid, base):
            vv = [[x * scale for x in point] for point in stage["vertices"]]
            dots = [oracle._dot(oracle._face_vector(vv, [i-1 for i in f]), normal) for f in stage["faces"]]
            normals.append(bool(dots) and all(x < 0 for x in dots))
        unchanged_volume = abs(abs(volume) - expected_volume) <= max(1e-5, expected_volume * 1e-7)
        protective = (not desired_direction and reversed_direction and all(normals) and unchanged_volume
                      and topology["boundary_edges"] == 0 and topology["nonmanifold_edges"] == 0
                      and topology["inconsistent_edges"] == 0)
        result = {"status": "CONTROL_DISCRIMINATES" if protective else "FAIL",
                  "scope": "actual reversed full-runtime arrays, narrow direction+volume check; NOT production acceptance",
                  "physical_direction_check": "FAIL" if not desired_direction else "PASS",
                  "actual_signed_displacement_cm": [min(distances), max(distances)],
                  "grid_and_base_normals_reversed": normals, "absolute_volume_cm3": abs(volume),
                  "independent_expected_volume_cm3": expected_volume, "volume_unchanged": unchanged_volume,
                  "triangle_topology": topology, "test_script_sha256": v["sha256"],
                  "capture_sha256": digest(Path(a.capture).read_bytes()),
                  "oracle_sha256": digest(oracle_path.read_bytes()),
                  "evaluated_quad_capture": "INCOMPLETE; no synthetic quads supplied"}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if protective else 1
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        print("INCOMPLETE: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
