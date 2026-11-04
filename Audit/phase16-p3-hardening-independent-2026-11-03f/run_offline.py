"""Record the two existing offline suites without modifying their sources."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = (
    "scripts/wall_surface_runtime.py",
    "scripts/scene_units.py",
    "Audit/test_phase16_p3_runtime.py",
    "Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py",
    "Audit/phase16-p3-runtime-hardening-2026-11-03f/wall_surface_runtime.pre-edit.py.bin",
    "Audit/phase16-p3-runtime-hardening-2026-11-03f/REPORT.md",
    "Audit/phase16-p3-runtime-review-2026-11-03/review.md",
    "Audit/_phase16-p3-contract-2026-11-02e.md",
)
SUITES = (
    ("runtime", INPUTS[2]),
    ("protection", INPUTS[3]),
)


def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in INPUTS}


def write_new(name, data):
    with (HERE / name).open("xb") as stream:
        stream.write(data)


def main():
    before = hashes()
    started = datetime.now(timezone.utc).isoformat()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    results = []
    for label, suite in SUITES:
        args = [sys.executable, "-B", str(ROOT / suite)]
        completed = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, check=False)
        write_new(label + ".stdout.log", completed.stdout)
        write_new(label + ".stderr.log", completed.stderr)
        results.append({"suite": suite, "argv": args, "exit_code": completed.returncode,
                        "stdout": label + ".stdout.log", "stderr": label + ".stderr.log"})
    after = hashes()
    result = {"scope": "Offline Python/source checks only; no Max or MAXScript execution",
              "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "cwd": str(ROOT), "before": before, "after": after,
              "inputs_stable": before == after, "results": results}
    write_new("results.json", (json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(result, indent=2))
    return 0 if before == after and all(item["exit_code"] == 0 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
