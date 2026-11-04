#!/usr/bin/env python3
"""Run all Phase 16 offline checks, retaining logs and exact snapshot hashes.

Does not install, invoke Max, or alter project inputs. Test-owned disposable
directories use the approved OpenCode temp parent. A zero subprocess exit with
SKIP/xfail is recorded, never promoted into complete Phase 16 acceptance.
"""
from __future__ import annotations

import argparse
import atexit
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def snapshot() -> dict[str, str]:
    files = {ROOT / "PLAN.md", ROOT / "references/07-spec-grammar.md", Path(__file__).resolve()}
    files.update((ROOT / "scripts").glob("*.py"))
    files.update((ROOT / "Audit").glob("test_phase16*.py"))
    for directory in ("examples", "specs/fixtures"):
        files.update(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files) if p.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path,
                        help="New, nonexistent report directory")
    options = parser.parse_args()
    out = options.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = snapshot()
    (out / "hashes-before.json").write_text(json.dumps(before, indent=2) + "\n", encoding="utf-8")
    completion = {"normal_end": False}

    def exit_evidence() -> None:
        """Retain an honest interruption marker even if the suite loop aborts."""
        try:
            last = snapshot()
            marker = dict(normal_end=completion["normal_end"],
                          changed=sorted(k for k in before.keys() | last.keys()
                                         if before.get(k) != last.get(k)),
                          note="No crash/kill durability guarantee; inspect missing final verdict.")
            (out / "hashes-at-process-exit.json").write_text(
                json.dumps(last, indent=2) + "\n", encoding="utf-8")
            (out / "process-exit.json").write_text(
                json.dumps(marker, indent=2) + "\n", encoding="utf-8")
        except Exception as exc:
            print("could not retain exit evidence: " + repr(exc), file=sys.stderr)

    atexit.register(exit_evidence)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()
    environment = dict(python=sys.version, executable=sys.executable, git_head=head,
                       started_utc=datetime.now(timezone.utc).isoformat())
    (out / "environment.json").write_text(json.dumps(environment, indent=2) + "\n", encoding="utf-8")
    temp = Path(os.environ["LOCALAPPDATA"]) / "Temp/opencode"
    if not temp.is_dir():
        raise RuntimeError("approved OpenCode temporary directory is absent")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
               TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    env.pop("PYTHONOPTIMIZE", None)
    if not __debug__:
        raise RuntimeError("run the evidence recorder without Python optimization")
    scripts = sorted((ROOT / "Audit").glob("test_phase16*.py"))
    results = []
    observed_drift = set()
    for script in scripts:
        suite_before = snapshot()
        observed_drift.update(k for k in before.keys() | suite_before.keys()
                              if before.get(k) != suite_before.get(k))
        flags = [] if script.stem in ("test_phase16_strict_upstream",
                                     "test_phase16_scaffold_independent") else ["-v"]
        if script.stem == "test_phase16_p2":
            flags.insert(0, "--require-p2")
        command = [sys.executable, "-B", str(script), *flags]
        started = time.monotonic()
        try:
            process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                     timeout=1800, check=False)
            stdout, stderr, code = process.stdout, process.stderr, process.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b"", exc.stderr or b"", None
            # Do not launch subsequent tests while timed-out grandchildren may
            # still be alive. No broad process termination is attempted here.
        except OSError as exc:
            stdout, stderr, code = b"", repr(exc).encode("utf-8"), None
        (out / (script.stem + ".stdout.log")).write_bytes(stdout)
        (out / (script.stem + ".stderr.log")).write_bytes(stderr)
        text = (stdout + b"\n" + stderr).decode("utf-8", errors="replace")
        qualifiers = [line for line in text.splitlines()
                      if any(term in line.lower() for term in
                             ("skip", "expected failure", "unexpected success", "xfail"))]
        summary = [line for line in text.splitlines()
                   if line.startswith(("Ran ", "OK", "FAILED", "SOURCE_DRIFT"))]
        observed_counts = {
            key: [int(n) for n in re.findall(pattern, text)]
            for key, pattern in (
                ("ran", r"(?m)^Ran (\d+) tests?"),
                ("skipped", r"skipped=(\d+)"),
                ("expected_failures", r"expected failures=(\d+)"),
                ("failures", r"(?<!expected )failures=(\d+)"),
                ("errors", r"errors=(\d+)"),
            )
        }
        observation = script.stem in ("test_phase16_scaffold_independent",
                                      "test_phase16_scaffold_review_d")
        suite_after = snapshot()
        suite_drift = sorted(k for k in suite_before.keys() | suite_after.keys()
                             if suite_before.get(k) != suite_after.get(k))
        observed_drift.update(suite_drift)
        result = dict(test=script.name, command=command, exit_code=code,
                      seconds=round(time.monotonic() - started, 3),
                      summary=summary, qualifiers=qualifiers, observed_counts=observed_counts,
                      source_drift=suite_drift,
                      disposition="OBSERVATION_REQUIRES_REVIEW" if observation else
                                  "QUALIFIERS_REQUIRE_REVIEW" if qualifiers else "EXECUTED")
        results.append(result)
        print(json.dumps({k: result[k] for k in ("test", "exit_code", "seconds", "summary")}),
              flush=True)
        (out / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        if code is None:
            break
        if suite_drift:
            # A moving source invalidates this evidence batch. Retain the logs,
            # stop instead of accumulating apparently comparable results.
            break
    after = snapshot()
    observed_drift.update(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    drift = sorted(observed_drift)
    (out / "hashes-after.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    head_after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True, check=True).stdout.strip()
    verdict = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   source_drift=drift, nonzero=[r["test"] for r in results if r["exit_code"] != 0],
                   git_head_changed=head != head_after, expected_scripts=len(scripts),
                   executed_scripts=len(results), acceptance="NOT_ASSESSED",
                   note="SKIP/xfail and passing fault observations require manual disposition; "
                        "endpoint hashes cannot exclude change-and-revert; "
                        "no live or produced poly evidence")
    (out / "snapshot-verdict.json").write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verdict), flush=True)
    completion["normal_end"] = True
    return 1 if drift or verdict["nonzero"] or head != head_after else 0


if __name__ == "__main__":
    raise SystemExit(main())
