"""Record final offline test results without touching pre-existing paths.

Exits nonzero if any suite fails. Output directory files use exclusive creation.
Does not invoke 3ds Max and makes no claim about emitted MAXScript behavior.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRACKED = [ROOT / "scripts/wall_surface_runtime.py",
           HERE / "test_protection.py",
           HERE / "run_offline.py",
           ROOT / "Audit/test_phase16_p3_runtime.py",
           HERE / "wall_surface_runtime.pre-edit.py.bin",
           HERE / "wall_surface_runtime.pre-precreate-gate.py.bin"]
SUITES = [HERE / "test_protection.py", ROOT / "Audit/test_phase16_p3_runtime.py"]


def hashes():
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in TRACKED}


def write_new(path, data):
    with path.open("xb") as out:
        out.write(data)


def main():
    prefix = sys.argv[1] if len(sys.argv) == 2 else "final"
    if not prefix.isascii() or not prefix.replace('-', '').isalnum():
        raise ValueError("result prefix must be an ASCII alphanumeric/hyphen token")
    before = hashes()
    results = []
    for i, suite in enumerate(SUITES, 1):
        proc = subprocess.run([sys.executable, "-B", str(suite)], cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        out = f"{prefix}-{i}.stdout.log"
        err = f"{prefix}-{i}.stderr.log"
        write_new(HERE / out, proc.stdout)
        write_new(HERE / err, proc.stderr)
        results.append({"suite": str(suite.relative_to(ROOT)).replace('\\', '/'),
                        "exit_code": proc.returncode, "stdout": out, "stderr": err})
    after = hashes()
    result = {"scope": "offline Python/source tests only; no MAXScript execution",
              "before": before, "after": after, "stable": before == after,
              "results": results}
    write_new(HERE / f"{prefix}-results.json", (json.dumps(result, indent=2) + "\n").encode())
    print(json.dumps(result, indent=2))
    return 0 if before == after and all(r["exit_code"] == 0 for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
