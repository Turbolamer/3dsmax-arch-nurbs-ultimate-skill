"""Assess main's retained real calibration plus an explicit mutated negative.

Reads the one exact main evidence file; creates only the one new owned verdict
file with exclusive mode. No Max access or emitter/runtime imports.
"""

from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "_phase16-p3-measurement-calibration-2026-11-02e.json"
OUTPUT = HERE / "actual-calibration-verdict-2026-11-02e.json"
CALIBRATION = HERE / "calibration.py"


def main():
    raw_bytes = SOURCE.read_bytes()
    source_hash = sha256(raw_bytes).hexdigest()
    document = json.loads(raw_bytes)
    capture = document["capture"]
    original_capture = deepcopy(capture)
    spec = importlib.util.spec_from_file_location("owned_snapshot_calibration", CALIBRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    positive = module.assess_snapshot_calibration(capture)

    # Deliberately reproduce the original bad measurement line on the ACTUAL
    # observed snapshot vertices, with a separate scalar row-vector multiply.
    negative_capture = deepcopy(capture)
    matrix = capture["object_transform"]
    negative_capture["snapshot_vertices_world"] = [
        [p[0]*matrix[0][axis] + p[1]*matrix[1][axis] + p[2]*matrix[2][axis] + matrix[3][axis]
         for axis in range(3)]
        for p in capture["snapshot_vertices_world"]
    ]
    negative = module.assess_snapshot_calibration(negative_capture)
    if capture != original_capture:
        raise AssertionError("assessment mutated actual capture")
    after_hash = sha256(SOURCE.read_bytes()).hexdigest()
    if source_hash != after_hash:
        raise AssertionError("main evidence source bytes changed")
    if positive["status"] != "PASS" or not all(positive["checks"].values()):
        raise AssertionError("actual calibration did not pass: " + repr(positive))
    if not positive["translation_exercised"] or not positive["rotation_exercised"]:
        raise AssertionError("actual calibration did not exercise both motions")
    if negative["status"] != "FAIL" or negative["checks"]["SNAPSHOT_ALREADY_WORLD"] or negative["checks"]["SNAPSHOT_NOT_DOUBLE_TRANSFORMED"]:
        raise AssertionError("double-transform negative did not discriminate: " + repr(negative))
    verdict = {
        "schema_version": "p3-actual-calibration-verdict-1",
        "status": "PASS_BOUNDED_CALIBRATION",
        "source_path": str(SOURCE), "source_sha256_before": source_hash,
        "source_sha256_after": after_hash,
        "assessment_source_sha256": sha256(CALIBRATION.read_bytes()).hexdigest(),
        "epsilon_scene_units": 1e-4,
        "actual_capture_assessment": positive,
        "deliberate_double_transform_negative": negative,
        "negative_mutation": "actual snapshot_vertices_world multiplied by actual object_transform a second time; all other actual fields retained",
        "negative_snapshot_vertices_world": negative_capture["snapshot_vertices_world"],
        "main_recorded_bridge": {key: document.get(key) for key in (
            "main_executed", "request_id", "bridge_ok", "bridge_error", "bridge_warnings",
            "round_trip_ms", "elapsed_ms", "objects_after")},
        "scope": "Independent offline assessment of main's retained actual translated+rotated one-quad capture. Negative is a deliberate data mutation, not a second live test. No F01/other API/geometry acceptance implied.",
    }
    with OUTPUT.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(verdict, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print("actual=PASS; double_transform_negative=FAIL (both coordinate gates); main source unchanged")
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
