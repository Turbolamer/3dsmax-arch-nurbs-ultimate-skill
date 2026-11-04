"""Run original hash-verified suites against the requested d9 snapshot only."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
MIRROR = HERE / "d9-fixture"
manifest = json.loads((HERE / "d9-fixture-manifest.json").read_text(encoding="utf-8"))


def hashes():
    return {p: hashlib.sha256((MIRROR / p).read_bytes()).hexdigest() for p in manifest}


def save(name, data):
    with (HERE / name).open("xb") as stream:
        stream.write(data)


def main():
    before = hashes()
    if before != manifest:
        raise SystemExit("fixture differs from verified manifest")
    results = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for label, name in (("runtime", "Audit/test_phase16_p3_runtime.py"),
                        ("protection", "Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py")):
        args = [sys.executable, "-B", str(MIRROR / name)]
        result = subprocess.run(args, cwd=MIRROR, env=env, capture_output=True, check=False)
        save("d9-" + label + ".stdout.log", result.stdout)
        save("d9-" + label + ".stderr.log", result.stderr)
        results.append({"suite": name, "argv": args, "exit_code": result.returncode,
                        "stdout": "d9-" + label + ".stdout.log",
                        "stderr": "d9-" + label + ".stderr.log"})
    after = hashes()
    record = {"scope": "offline Python/source checks; no Max or MAXScript execution",
              "finished_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
              "cwd": str(MIRROR), "before": before, "after": after,
              "inputs_stable": before == after, "results": results}
    save("d9-results.json", (json.dumps(record, indent=2) + "\n").encode())
    print(json.dumps(record, indent=2))
    return 0 if before == after and all(r["exit_code"] == 0 for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
