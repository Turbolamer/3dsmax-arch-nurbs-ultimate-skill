"""Re-run the current existing offline suites with hash-checked inputs."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = ("scripts/wall_surface_runtime.py", "scripts/scene_units.py",
         "Audit/test_phase16_p3_runtime.py",
         "Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py",
         "Audit/phase16-p3-runtime-hardening-2026-11-03f/wall_surface_runtime.pre-edit.py.bin",
         "Audit/phase16-p3-runtime-hardening-2026-11-03f/wall_surface_runtime.pre-precreate-gate.py.bin")
EXPECTED = ("3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf",
            "19360d8f54ce667e692d2c30ce6be7ea28e5fad1a82d3b79d8fbd95195d7919d")


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in FILES}


def write(name, value):
    with (HERE / name).open("xb") as out:
        out.write(value)


def main():
    before = hashes()
    if (before[FILES[0]], before[FILES[3]]) != EXPECTED:
        raise SystemExit("current runtime/test changed, do not run")
    results = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for label, suite in (("runtime", FILES[2]), ("protection", FILES[3])):
        argv = [sys.executable, "-B", str(ROOT / suite)]
        proc = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, check=False)
        write("latest-" + label + ".stdout.log", proc.stdout)
        write("latest-" + label + ".stderr.log", proc.stderr)
        results.append({"suite": suite, "argv": argv, "exit_code": proc.returncode,
                        "stdout": "latest-" + label + ".stdout.log",
                        "stderr": "latest-" + label + ".stderr.log"})
    after = hashes()
    data = {"scope": "offline Python/source tests; no Max or MAXScript execution",
            "finished_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
            "cwd": str(ROOT), "before": before, "after": after,
            "inputs_stable": before == after, "results": results}
    write("latest-results.json", (json.dumps(data, indent=2) + "\n").encode())
    print(json.dumps(data, indent=2))
    return 0 if before == after and all(r["exit_code"] == 0 for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
