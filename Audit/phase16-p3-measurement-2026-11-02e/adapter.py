"""Lossless explicit measurement-to-oracle adapter; no generator imports or I/O.

No provenance/binding is inferred: main supplies an independently verified evidence
dictionary. Missing grid and evaluated polygons stay missing. Retains the raw
measurement separately and never promotes CAPTURED_NOT_ACCEPTED to acceptance.
"""

from copy import deepcopy
import math


def oracle_capture(raw, evidence, *, grid_raw=None):
    """Return normalized cm stages for phase16_p3_oracle.assess_measurements.

    `evidence` is explicit coordinator-bound metadata, NOT fields copied from any
    emitter prediction. Optional `grid_raw` must be an actual earlier #grid capture
    of the same exact node/base in the same Max session, observed by main. This
    adapter checks the reported identity/unit pair, not historical authenticity.
    Evaluated triangle indexes are retained as triangles, never merged to polygons.
    """
    if not isinstance(raw, dict) or raw.get("schema_version") != "p3-independent-measurement-1":
        raise ValueError("unknown measurement schema")
    if raw.get("status") != "CAPTURED_NOT_ACCEPTED" or raw.get("stage") != "final":
        raise ValueError("a complete final capture, not an error/grid envelope, is required")
    unit = raw.get("units", {})
    scale = unit.get("scene_units_per_cm")
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale <= 0:
        raise ValueError("invalid measured scene_units_per_cm")
    if not isinstance(evidence, dict) or evidence.get("kind") not in {"scene_capture", "synthetic_test"}:
        raise ValueError("explicit coordinator evidence binding required")
    if evidence.get("length_unit") != "cm":
        raise ValueError("bound oracle output must explicitly declare length_unit=cm")

    def stage(value, *, triangles=False):
        if not isinstance(value, dict) or type(value.get("index_base")) is not int or value["index_base"] != 1 or value.get("coordinate_space") != "world":
            raise ValueError("expected one-based measured world-space stage")
        result = {"index_base": 1}
        points = value.get("vertices")
        if not isinstance(points, list):
            raise ValueError("measured vertices missing")
        converted = []
        for point in points:
            if not isinstance(point, list) or len(point) != 3:
                raise ValueError("bad measured vertex")
            if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in point):
                raise ValueError("nonfinite/nonnumeric measured vertex")
            converted.append([x / scale for x in point])
        result["vertices_cm"] = converted
        keys = ("faces", "triangles") if triangles else ("faces",)
        for key in keys:
            if key not in value:
                continue
            rows = value[key]
            if not isinstance(rows, list) or any(not isinstance(row, list) or any(type(i) is not int for i in row) for row in rows):
                raise ValueError("invalid measured index arrays")
            result[key] = deepcopy(rows)
        if triangles and "triangles" not in result:
            raise ValueError("evaluated actual triangles missing")
        if not triangles and "faces" not in result:
            raise ValueError("base/grid actual faces missing")
        return result

    result = {"evidence": deepcopy(evidence), "base": stage(raw.get("base")),
              "evaluated": stage(raw.get("evaluated"), triangles=True)}
    if grid_raw is not None:
        if not isinstance(grid_raw, dict) or grid_raw.get("schema_version") != raw["schema_version"]:
            raise ValueError("unknown grid measurement schema")
        if grid_raw.get("status") != "CAPTURED_NOT_ACCEPTED" or grid_raw.get("stage") != "grid":
            raise ValueError("a real earlier #grid capture is required")
        if grid_raw.get("units") != raw.get("units"):
            raise ValueError("grid/final measured unit pairs differ")
        for key in ("anim_handle", "node_handle", "base_anim_handle", "object_transform"):
            if key not in raw.get("target", {}) or key not in grid_raw.get("target", {}):
                raise ValueError("grid/final reported identity missing: " + key)
            if grid_raw.get("target", {}).get(key) != raw.get("target", {}).get(key):
                raise ValueError("grid/final reported identities differ: " + key)
        result["grid"] = stage(grid_raw.get("grid"))
    return result
