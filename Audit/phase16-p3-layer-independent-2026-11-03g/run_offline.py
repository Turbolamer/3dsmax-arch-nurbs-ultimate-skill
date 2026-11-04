"""Run only the three bounded Python audit suites; exclusively create logs.

Never starts Max, never connects to MCP, and never writes outside this directory.
The before/after hashes are sequential observations, not a filesystem lock.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUTS = [
    "Audit/phase16-p3-layer-reader-2026-11-03f/layer_reader.ms",
    "Audit/phase16-p3-layer-reader-2026-11-03f/layer_reader_p31_offline.ms",
    "Audit/phase16-p3-layer-reader-2026-11-03f/emitter_fragment.py",
    "Audit/phase16-p3-layer-reader-2026-11-03f/test_candidate.py",
    "Audit/phase16-p3-layer-reader-2026-11-03f/test_p31_offline.py",
    "Audit/phase16-p3-layer-reader-2026-11-03f/README_p31_offline.md",
    "Audit/phase16-p3-layer-reader-2026-11-03f/REPORT.md",
    "Audit/phase16-p3-layer-reader-2026-11-03f/REPORT_p31_offline.md",
    "Audit/_phase16-p3-contract-2026-11-02e.md",
    "Audit/_phase16-p3-resume-2026-11-03f.md",
    "Audit/_phase16-p3-layer-calibration-brief-2026-11-03f.md",
    "Audit/_phase16-p3-layer-readonly-2026-11-03f.json",
    "Audit/phase16-p3-main-probes-2026-11-03f/layer-owned.ms",
    "Audit/phase16-p3-main-probes-2026-11-03f/layer-owned-result.json",
    "Audit/phase16-p3-main-probes-2026-11-03f/layer-membership.ms",
    "Audit/phase16-p3-main-probes-2026-11-03f/layer-membership-result.json",
    "scripts/wall_surface_runtime.py",
    "Audit/phase16-p3-layer-independent-2026-11-03g/test_independent.py",
    "Audit/phase16-p3-layer-independent-2026-11-03g/run_offline.py",
]
SUITES = [
    ("candidate.log", "Audit/phase16-p3-layer-reader-2026-11-03f/test_candidate.py", 14),
    ("p31.log", "Audit/phase16-p3-layer-reader-2026-11-03f/test_p31_offline.py", 14),
    ("independent.log", "Audit/phase16-p3-layer-independent-2026-11-03g/test_independent.py", 17),
]


def hashes() -> dict[str, str]:
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in INPUTS}


def write_new(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def main() -> int:
    outputs = [HERE / item[0] for item in SUITES] + [HERE / "run.json"]
    for output in outputs:
        if output.exists():
            raise FileExistsError(f"refusing to overwrite audit output: {output}")

    before = hashes()
    results = []
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for log_name, script, expected in SUITES:
        args = [sys.executable, "-B", script, "-v"]
        completed = subprocess.run(
            args, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", check=False,
        )
        log = completed.stdout
        write_new(HERE / log_name, log)
        count_match = re.search(r"(?m)^Ran (\d+) tests? in [^\r\n]+$", log)
        count = int(count_match.group(1)) if count_match else None
        ok = (
            completed.returncode == 0
            and count == expected
            and re.search(r"(?m)^OK\s*$", log) is not None
            and " skipped=" not in log
            and "expected failures=" not in log
            and "unexpected successes=" not in log
        )
        results.append({
            "command": args,
            "exit_code": completed.returncode,
            "tests_run": count,
            "expected_tests": expected,
            "summary_exact_ok_no_qualifiers": bool(ok),
            "log": log_name,
            "log_sha256": hashlib.sha256((HERE / log_name).read_bytes()).hexdigest(),
        })

    after = hashes()
    unchanged = before == after
    report = {
        "scope": "Python structural/model checks only; no MAXScript parse/fileIn or Max/MCP calls",
        "python": sys.version,
        "platform": platform.platform(),
        "cwd": str(ROOT),
        "hash_before": before,
        "hash_after": after,
        "unchanged": unchanged,
        "results": results,
    }
    write_new(HERE / "run.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "unchanged": unchanged,
        "results": [{key: item[key] for key in ("log", "exit_code", "tests_run", "summary_exact_ok_no_qualifiers")} for item in results],
        "manifest": str(HERE / "run.json"),
    }, indent=2))
    return 0 if unchanged and all(item["summary_exact_ok_no_qualifiers"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
