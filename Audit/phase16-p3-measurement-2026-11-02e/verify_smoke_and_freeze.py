"""Read main's exact smoke capture and freeze finalized owned source hashes.

No Max calls, main evidence writes or generator imports. Exclusive new result.
"""

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "_phase16-p3-measurement-smoke-capture-2026-11-02e.json"
OUTPUT = HERE / "final-source-hashes-and-smoke-2026-11-02e.json"
EXPECTED_SHA = "81b69fc1de39a9fcd410b9158cac6d317030d2f2bcd10bde4cd32afdf12c364a"
OWNED_SOURCE_NAMES = (
    "measure.ms", "calibrate_snapshot.ms", "calibrate_writer.ms", "adapter.py",
    "calibration.py", "test_offline.py", "verify_actual_calibration.py",
    "verify_smoke_and_freeze.py", "README.md",
)


def main():
    before = SOURCE.read_bytes()
    digest = sha256(before).hexdigest()
    if digest != EXPECTED_SHA or len(before) != 3516:
        raise AssertionError("main smoke hash/byte count mismatch")
    capture = json.loads(before)
    if capture["status"] != "CAPTURED_NOT_ACCEPTED" or capture["stage"] != "final":
        raise AssertionError("unexpected capture status/stage")
    actual = {
        "base_active_counts": capture["base"]["active_counts"],
        "evaluated_vertices": len(capture["evaluated"]["vertices"]),
        "evaluated_triangles": len(capture["evaluated"]["triangles"]),
        "scene_count": capture["scene_count"], "issues": capture["issues"],
    }
    if actual != {"base_active_counts": [4, 4, 1], "evaluated_vertices": 8,
                  "evaluated_triangles": 12, "scene_count": 1, "issues": []}:
        raise AssertionError("main smoke reported counts differ from actual file")
    hashes = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in OWNED_SOURCE_NAMES}
    after = sha256(SOURCE.read_bytes()).hexdigest()
    if after != digest:
        raise AssertionError("main evidence changed during verification")
    result = {
        "schema_version": "p3-measurement-final-source-freeze-1",
        "capture_verdict": "PARSED_HASH_AND_COUNTS_VERIFIED_BOUNDED_CALIBRATION",
        "main_capture": {"path": str(SOURCE), "sha256_before": digest,
                         "sha256_after": after, "bytes": len(before), "actual": actual},
        "finalized_owned_source_sha256": hashes,
        "current_envelope_runtime_status": "UNVERIFIED_AFTER_INTEGER64_SUFFIX_CORRECTION",
        "qualification": "Main's old compact envelope was invalid JSON (3516L). Existing actual full capture is valid JSON and unchanged. Not F01/geometry/replay/scene cleanup acceptance; cleanup is main-reported. No live calls by this verifier.",
    }
    with OUTPUT.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print("main_capture=PARSED_HASH_AND_COUNTS_VERIFIED; envelope_fix=UNVERIFIED")
    for name in ("measure.ms", "calibrate_writer.ms"):
        print(name + " sha256=" + hashes[name])
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
