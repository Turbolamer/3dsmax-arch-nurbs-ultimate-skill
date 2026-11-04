#!/usr/bin/env python3
"""Actual CLI clean/contradictory authority control, OFFLINE ONLY; no Max import."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_controls import HERE, ROOT, digest, encode, strict_json


def inventory(project: Path, authority: Path):
    paths = sorted(set(project.rglob("*.json")) | {authority} |
                   set((ROOT / "scripts").glob("*.py")) |
                   {ROOT / "Audit" / "AGENT_PLAN_poly_surface_shell.md",
                    ROOT / "Audit" / "_phase16-p3-contract-2026-11-02e.md"})
    return {str(p): digest(p.read_bytes()) for p in paths}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    p.add_argument("--authority", required=True)
    p.add_argument("--out", required=True, help="new direct child of this audit directory")
    a = p.parse_args(argv)
    try:
        project = Path(a.project).resolve()
        authority = Path(a.authority).resolve()
        out = Path(a.out).absolute()
        if out.exists() or out.parent.resolve() != HERE:
            raise ValueError("--out must be a NEW direct child of this owned audit directory")
        record = strict_json(authority.read_bytes())
        before = inventory(project, authority)
        out.mkdir()
        wrong = dict(record)
        wrong["outward"] = [-x for x in record["outward"]]
        bad_authority = out / "NEGATIVE_ONLY_wrong_authority.json"
        bad_authority.write_bytes(encode(wrong))
        commands = []
        for case, auth in (("clean", authority), ("wrong_authority", bad_authority)):
            destination = out / case
            cmd = [sys.executable, "-B", str(ROOT / "scripts" / "build_wall_surface.py"),
                   "--in", str(project), "--out", str(destination), "--namespace", "AuditAuthorityControl",
                   "--system-type", "millimeters", "--system-scale", "1",
                   "--direction-authority", str(auth)]
            run = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=45)
            (out / (case + ".stdout.txt")).write_bytes(run.stdout)
            (out / (case + ".stderr.txt")).write_bytes(run.stderr)
            commands.append({"case": case, "command": cmd, "returncode": run.returncode,
                             "output_exists": destination.exists()})
            if case == "clean":
                if run.returncode != 0 or not (destination / "wall_surface.ms").is_file():
                    raise ValueError("actual clean public CLI control did not emit; later authority negative NOT RUN")
            elif (run.returncode == 0 or destination.exists() or
                  b"direction authority outward conflicts" not in run.stdout + run.stderr):
                raise ValueError("wrong source authority not refused at targeted public authority boundary")
        after = inventory(project, authority)
        result = {"status": "OFFLINE_CONTROL_DISCRIMINATES" if after == before else "FAIL_SOURCE_DRIFT",
                  "commands": commands, "before": before, "after": after,
                  "scope": "actual CLI byte snapshot, no Max execution; clean output offline unverified"}
        (out / "result.json").write_bytes(encode(result))
        print(json.dumps({"status": result["status"], "out": str(out)}))
        return 0 if before == after else 1
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print("INCOMPLETE: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
