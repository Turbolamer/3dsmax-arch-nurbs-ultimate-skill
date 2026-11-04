"""Create new harmless controls only; never call Max or overwrite prior evidence."""

from __future__ import annotations

import hashlib
import json

from pair_filein import HERE, inspect_pair, render_lock_probe, render_wrapper, write_new_owned


def main() -> None:
    manifest = HERE / "control_pair.json"
    script = HERE / "control_pair.ms"
    expected_manifest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    expected_script = hashlib.sha256(script.read_bytes()).hexdigest()
    manifest, script = inspect_pair(manifest, script, expected_manifest, expected_script)
    payloads = {
        "control_wrapper.ms": render_wrapper(manifest, script, expected_manifest, expected_script),
        "control_malformed_hash_wrapper.ms": render_wrapper(
            manifest, script, expected_manifest, "not-a-sha256", _malformed_control=True
        ),
        "control_mismatch_hash_wrapper.ms": render_wrapper(
            manifest, script, expected_manifest, "0" * 64
        ),
        "control_lock_probe.ms": render_lock_probe(script),
    }
    record_path = HERE / "controls.json"
    for name in (*payloads, record_path.name):
        if (HERE / name).exists():
            raise FileExistsError(f"refusing any prior control/evidence overwrite: {HERE / name}")
    outputs = {}
    for name, text in payloads.items():
        path = write_new_owned(HERE / name, text)
        outputs[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    record = {
        "status": "OFFLINE_GENERATED_UNEXECUTED_IN_MAX",
        "manifest": {"path": str(manifest), "sha256": expected_manifest},
        "script": {"path": str(script), "sha256": expected_script},
        "outputs": outputs,
        "expected_live_only": {
            "control_wrapper.ms": "actual fileIn result 4, both read handles cleaned",
            "control_malformed_hash_wrapper.ms": "exception P16 malformed script SHA-256; no source open/fileIn",
            "control_mismatch_hash_wrapper.ms": "exception P16 script SHA-256 mismatch; handles cleaned; no fileIn",
            "control_lock_probe.ms": "P16_LOCK_PROBE_OBSERVED tuple; compatible read, denied WRITE-open diagnostic, CanRead=false, exclusive READ reopen",
        },
        "qualification": "All MAXScript/.NET enum binding, lock, SHA256, fileIn-sharing and closure behavior unverified until main executes the exact files.",
    }
    write_new_owned(record_path, json.dumps(record, indent=2) + "\n")
    print(json.dumps({"controls": str(record_path), "status": record["status"]}))


if __name__ == "__main__":
    main()
