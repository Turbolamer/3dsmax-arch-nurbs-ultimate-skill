#!/usr/bin/env python3
"""Record a settled P3 offline test run; NEVER decide P3 acceptance.

Usage: python -B Audit/run_phase16_p3_settled.py --out NEW_DIRECTORY

Only direct Audit/test_phase16_p3*.py files are executed, in filename order,
using this interpreter and -B. No P2 suite, Max, installer or Git write is
invoked by this recorder. Tests are trusted local programs, not sandboxed.
Stop authors before invoking: before/after hashes cannot detect change/revert.
"""
from __future__ import annotations

import argparse
import atexit
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "Audit"
SELF = Path(__file__).resolve()
FIXTURE = AUDIT / "phase16-p3-f01-input-2026-11-02e"
P2_MANIFEST = AUDIT / "phase16-p2-final-2026-11-02d/hashes-before.json"
PRESERVATION = AUDIT / "_phase16-p3-preservation-2026-11-02e.json"
P3_SOURCES = (
    "scripts/build_wall_surface.py", "scripts/wall_surface_inputs.py",
    "scripts/wall_surface_runtime.py", "scripts/wall_surface_publish.py",
    "Audit/phase16_p3_oracle.py",
)
# Hash-only supporting tools/fixtures. In particular, main-build is recursive so
# a pair published by main's preparation runner is frozen without executing it.
TOOL_TREES = tuple(AUDIT / name for name in (
    "phase16-p3-preflight-2026-11-02e", "phase16-p3-measurement-2026-11-02e",
    "phase16-p3-execution-2026-11-02e", "phase16-p3-live-controls-2026-11-02e",
    "phase16-p3-runtime-probes-2026-11-02e", "phase16-p3-state-probes-2026-11-02e",
    "phase16-p3-main-build-2026-11-02e",
))
PAIR_NAMES = ("wall_surface.json", "wall_surface.ms")
# Explicit offline filename checklist, not an acceptance/coverage oracle. Other
# direct P3-prefixed tests are ALSO run; no generic unittest/recursive discovery.
REQUIRED_SUITES = {
    "test_phase16_p3_builder.py": "public CLI/coordinator boundary",
    "test_phase16_p3_inputs.py": "input admission adapter",
    "test_phase16_p3_publication.py": "new-directory publication",
    "test_phase16_p3_runtime.py": "offline runtime/emission checks (not live Max)",
    "test_phase16_p3_oracle.py": "independent geometry oracle controls",
    "test_phase16_p3_independent.py": "independent public-boundary adversarial checks",
}
# Main's reported counts are a review baseline, never an asserted executed fact.
# The independent author was still pending when this baseline was supplied.
REPORTED_TEST_COUNTS = {
    "test_phase16_p3_publication.py": 39, "test_phase16_p3_inputs.py": 31,
    "test_phase16_p3_runtime.py": 40, "test_phase16_p3_builder.py": 34,
    "test_phase16_p3_oracle.py": 65, "test_phase16_p3_independent.py": None,
}
P2_ACCEPTED = {
    "scripts/init_project.py": "42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88",
    "scripts/place_components.py": "4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac",
    "scripts/validate_specs.py": "616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f",
    "scripts/wall_cell_coverage.py": "d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e",
}
PACKAGE = "3dsmax-arch-nurbs-ultimate.skill"
PACKAGE_PRESERVED_SHA = "dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a"
FIXED_INPUTS = (
    "AGENTS.md", "CHECKPOINT.md", "PLAN.md", "references/07-spec-grammar.md",
    "Audit/_phase16-p3-main-brief-2026-11-02e.md",
    "Audit/_phase16-p3-contract-2026-11-02e.md",
    "Audit/_phase16-p3-recorder-2026-11-02e.md",
    "Audit/AGENT_PLAN_poly_surface_shell.md", "Audit/EVIDENCE_2026-10-27.md",
    "Audit/run_phase16_settled.py",
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def label(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def within(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def linkish(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400)  # Windows reparse point


def fingerprint(path: Path) -> dict:
    """Never follow an input link; failures are recorded, not silently omitted."""
    try:
        if linkish(path):
            return {"state": "REFUSED_LINK_OR_REPARSE_POINT"}
        if not path.is_file():
            return {"state": "NOT_A_REGULAR_FILE"}
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            while True:
                raw = stream.read(1024 * 1024)
                if not raw:
                    break
                digest.update(raw)
                size += len(raw)
        return {"state": "FILE", "sha256": digest.hexdigest(), "size": size}
    except FileNotFoundError:
        return {"state": "NOT_AVAILABLE"}
    except OSError as exc:
        return {"state": "READ_ERROR", "error": repr(exc)}


def tree_files(directory: Path, errors: list) -> set[Path]:
    """Deterministic, bytecode-free inventory without traversing linked dirs."""
    paths: set[Path] = set()
    if not directory.exists():
        errors.append({"path": label(directory), "error": "directory NOT_AVAILABLE"})
        return paths
    if linkish(directory):
        paths.add(directory)
        return paths

    def onerror(exc: OSError) -> None:
        errors.append({"path": str(exc.filename), "error": repr(exc)})

    for base, dirs, files in os.walk(directory, followlinks=False, onerror=onerror):
        dirs.sort()
        files.sort()
        for name in list(dirs):
            path = Path(base) / name
            if name in ("__pycache__", ".git"):
                dirs.remove(name)
            elif linkish(path):
                dirs.remove(name)
                paths.add(path)
        paths.update(Path(base) / name for name in files
                     if not name.endswith((".pyc", ".pyo")))
    return paths


def suites() -> list[Path]:
    return sorted((p for p in AUDIT.glob("test_phase16_p3*.py") if p.is_file()),
                  key=lambda p: p.name)


def suite_command(script: Path) -> list[str]:
    # All six reviewed public suite entrypoints accept -v. Unknown future P3
    # scripts get no guessed CLI flags; their raw output is still retained.
    return [sys.executable, "-B", str(script), *(["-v"] if script.name in REQUIRED_SUITES else [])]


def git_head() -> dict:
    command = ["git", "rev-parse", "--verify", "HEAD"]
    started = utc()
    try:
        process = subprocess.run(command, cwd=ROOT, capture_output=True, check=False,
                                 timeout=15, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
        return {"command": command, "started_utc": started,
                "returncode": process.returncode,
                "stdout": process.stdout.decode("utf-8", errors="replace"),
                "stderr": process.stderr.decode("utf-8", errors="replace"),
                "head": process.stdout.decode("ascii", errors="replace").strip()
                if process.returncode == 0 else None}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "started_utc": started,
                "returncode": None, "head": None, "error": repr(exc)}


def read_object(path: Path) -> dict:
    # This reads evidence only. It does not import/validate/repair domain inputs.
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key " + repr(key))
            result[key] = value
        return result

    if linkish(path) or not path.is_file():
        raise ValueError("not a regular unlinked evidence file: " + str(path))
    value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("expected JSON object: " + str(path))
    return value


def legacy_reference() -> dict[str, str]:
    reference = read_object(P2_MANIFEST)
    selected = {name: sha for name, sha in reference.items()
                if name.startswith(("examples/", "specs/fixtures/"))}
    if len(selected) != 49 or any(
            not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)
            or Path(name).is_absolute() or ".." in Path(name).parts
            for name, sha in selected.items()):
        raise ValueError("accepted P2 manifest does not identify exactly 49 safe legacy paths")
    if any(reference.get(name) != sha for name, sha in P2_ACCEPTED.items()):
        raise ValueError("accepted P2 evidence disagrees with the explicit four-source baseline")
    return selected


def authority_sources(errors: list) -> set[Path]:
    """Hash record and actual cited source candidates, not guessed direction truth.

    The F01 README currently specifies repository-relative source_file. Relative
    records used by public-boundary tests may instead be record-relative. Retain
    both candidates if both exist; ambiguity is an evidence problem, not a pass.
    """
    sources: set[Path] = set()
    authority = FIXTURE / "direction-authority.json"
    sources.add(authority)
    try:
        record = read_object(authority)
        name = record.get("source_file")
        if not isinstance(name, str) or not name or "\x00" in name:
            raise ValueError("source_file is not a nonempty path string")
        source = Path(name)
        candidates = [source] if source.is_absolute() else [ROOT / source, authority.parent / source]
        # Keep missing candidates too: a later creation is observable drift.
        candidates = sorted(set(Path(os.path.abspath(p)) for p in candidates))
        sources.update(candidates)
        available = [p for p in candidates if p.is_file()]
        if len(available) != 1:
            errors.append({"path": label(authority), "error":
                           "cited source is NOT_AVAILABLE or ambiguous",
                           "candidates": [label(p) for p in candidates]})
        elif fingerprint(available[0]).get("sha256") != record.get("source_sha256"):
            errors.append({"path": label(available[0]), "error":
                           "cited source bytes do not match authority source_sha256"})
        if fingerprint(FIXTURE / "project/walls.json").get("sha256") != record.get("walls_sha256"):
            errors.append({"path": label(authority), "error":
                           "fixture wall bytes do not match authority walls_sha256"})
    except (OSError, ValueError) as exc:
        errors.append({"path": label(authority), "error": repr(exc)})
    return sources


def snapshot(legacy: dict[str, str], artifact_dirs: tuple[Path, ...] = ()) -> dict:
    errors: list = []
    paths = {SELF, P2_MANIFEST, PRESERVATION, ROOT / PACKAGE}
    paths.update(ROOT / name for name in (*FIXED_INPUTS, *P3_SOURCES, *P2_ACCEPTED, *legacy))
    paths.update((ROOT / "scripts").glob("*.py"))  # includes runtime/import dependencies
    paths.update(AUDIT.glob("test_phase16*.py"))  # P2 helpers locked, NOT executed
    paths.update(AUDIT.glob("phase16_p3*.py"))
    # Include current contract/review documents and operational MS/JSON evidence
    # directly under Audit, not just the initial contract/brief filenames.
    paths.update(p for p in AUDIT.glob("_phase16-p3-*") if p.is_file())
    paths.update(ROOT.glob("*.skill"))
    for directory in (ROOT / "examples", ROOT / "specs/fixtures", FIXTURE,
                      *TOOL_TREES, *artifact_dirs):
        paths.update(tree_files(directory, errors))
    pair_dirs = {p.parent for p in paths if p.name in PAIR_NAMES}
    pair_dirs.update(artifact_dirs)
    for directory in pair_dirs:
        paths.update(directory / name for name in PAIR_NAMES)
    paths.update(authority_sources(errors))
    files = {label(p): fingerprint(p) for p in sorted(paths, key=label)}
    for name, record in files.items():
        if record["state"] not in ("FILE", "NOT_AVAILABLE"):
            errors.append({"path": name, "error": record["state"]})
    pairs = []
    for directory in sorted(pair_dirs, key=label):
        pair = {name: files[label(directory / name)] for name in PAIR_NAMES}
        complete = all(record["state"] == "FILE" for record in pair.values())
        pairs.append({"directory": label(directory), "files": pair,
                      "status": "PAIR_BYTES_HASHED_NOT_ACCEPTED" if complete else "INCOMPLETE_PAIR"})
        if not complete:
            errors.append({"path": label(directory), "error": "generated pair INCOMPLETE"})
    return {"captured_utc": utc(), "files": files, "git": git_head(),
            "frozen_generated_pairs": pairs,
            "discovered_p3_suites": [label(p) for p in suites()], "inventory_errors": errors}


def drift(before: dict, after: dict) -> list[str]:
    old, new = before["files"], after["files"]
    changed = [name for name in old.keys() | new.keys() if old.get(name) != new.get(name)]
    if before["git"].get("head") != after["git"].get("head"):
        changed.append("GIT_HEAD")
    if before["discovered_p3_suites"] != after["discovered_p3_suites"]:
        changed.append("P3_SUITE_DISCOVERY")
    return sorted(changed)


def baseline_problems(state: dict, legacy: dict[str, str]) -> list[dict]:
    problems = list(state["inventory_errors"])
    if not state["git"].get("head") or state["git"].get("returncode") != 0:
        problems.append({"path": "GIT_HEAD", "error": "HEAD read NOT_AVAILABLE"})
    for name, expected in {**P2_ACCEPTED, **legacy, PACKAGE: PACKAGE_PRESERVED_SHA}.items():
        record = state["files"].get(name, {})
        if record.get("sha256") != expected:
            problems.append({"path": name, "error": "protected baseline mismatch",
                             "expected_sha256": expected, "observed": record})
    return problems


def availability(discovered: list[Path], state: dict) -> list[dict]:
    names = {p.name for p in discovered}
    result = [{"kind": "offline_suite", "path": "Audit/" + name, "role": role,
               "status": "AVAILABLE" if name in names else "NOT_AVAILABLE",
               "presence_is_execution": False,
               "main_reported_prior_test_count_not_current_evidence": REPORTED_TEST_COUNTS[name]}
              for name, role in sorted(REQUIRED_SUITES.items())]
    for name in P3_SOURCES:
        result.append({"kind": "source_or_oracle", "path": name,
                       "status": "AVAILABLE" if state["files"].get(name, {}).get("state") == "FILE"
                        else "NOT_AVAILABLE"})
    result.append({"kind": "frozen_generated_pair", "status": "HASHED_NOT_ACCEPTED"
                   if state["frozen_generated_pairs"] else "NOT_AVAILABLE",
                   "blocks_offline_recorder": False,
                   "role": "Optional existing main-preparation/artifact pair; absence is not fabricated.",
                   "pairs": state["frozen_generated_pairs"]})
    result.append({"kind": "scope", "status": "NOT_ASSESSED", "role":
                   "Authentic F01 fileIn/captures, physical checks, unit mismatches, three actual "
                   "no-op replays and live edit/collision/cleanup controls require main's evidence. "
                   "Offline script names, mocks, supplied captures and exit codes do not supply it."})
    return result


def write_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def write_raw(path: Path, raw: bytes) -> dict:
    with path.open("xb") as stream:
        stream.write(raw)
    return {"path": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def observations(stdout: bytes, stderr: bytes) -> dict:
    """Literal, stream/line-addressable observations; counts are never added up."""
    qualifiers, summaries, tests, counts = [], [], [], []
    qualifier = re.compile(
        r"\b(?:skip(?:ped|s)?|xfail(?:ed|s)?|expected failures?|unexpected success(?:es)?|"
        r"NOT[_ ]AVAILABLE|NOT[_ ]RUN|INCOMPLETE|NOT[_ ]APPLICABLE|REVIEW)\b", re.I)
    patterns = {
        "unittest_ran": r"^Ran (\d+) tests?\b",
        "skipped": r"\bskipped=(\d+)",
        "expected_failures": r"\bexpected failures=(\d+)",
        "unexpected_successes": r"\bunexpected successes=(\d+)",
        "failures": r"(?<!expected )\bfailures=(\d+)",
        "errors": r"\berrors=(\d+)",
    }
    for stream, raw in (("stdout", stdout), ("stderr", stderr)):
        for number, text in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
            row = {"stream": stream, "line": number, "text": text}
            if qualifier.search(text):
                qualifiers.append(row)
            if (text.startswith(("Ran ", "OK", "FAILED", "SOURCE_DRIFT"))
                    or re.search(r"\b[A-Z][A-Z0-9_]*(?:RESULT|DRIFT)\b", text)):
                summaries.append(row)
            if re.match(r"test\S*\s.*\.\.\.", text) or "::test_" in text:
                tests.append(row)
            for kind, pattern in patterns.items():
                counts.extend({"stream": stream, "line": number, "kind": kind,
                               "value": int(match.group(1))}
                              for match in re.finditer(pattern, text))
    return {"summary_lines": summaries, "qualifier_lines": qualifiers,
            "test_lines": tests, "observed_counts_not_totals": counts,
            "interpretation": "Literal observations only; no assertion/coverage/acceptance inference."}


def validate_output(raw: Path, artifact_dirs: tuple[Path, ...] = ()) -> Path:
    # Check lexical ancestors BEFORE resolve: do not hide a symlink/junction.
    raw = Path(os.path.abspath(raw))
    for path in (raw, *raw.parents):
        if path.exists() or path.is_symlink():
            if linkish(path):
                raise ValueError("output has a linked/reparse-point ancestor: " + str(path))
    out = raw.resolve()
    if out.exists():
        raise ValueError("--out must be a new, nonexistent directory: " + str(out))
    if within(out, ROOT) and not within(out, AUDIT):
        raise ValueError("repository output is permitted only below Audit, never source/spec trees")
    protected = [ROOT / "scripts", ROOT / "examples", ROOT / "specs", ROOT / ".git", FIXTURE,
                 *TOOL_TREES, *artifact_dirs]
    # Protect future explicitly named P3 input projects too, without recursively
    # treating old result directories as new executable suites or input fixtures.
    protected.extend(p for p in AUDIT.glob("phase16-p3*")
                     if p.is_dir() and "input" in p.name.lower())
    for directory in protected:
        if within(out, directory.resolve()) or within(directory.resolve(), out):
            raise ValueError("output overlaps a protected input/source directory: " + str(directory))
    return out


def reserve_output(raw: Path, unique: bool, artifact_dirs: tuple[Path, ...]) -> Path:
    """Reserve one fresh directory; opt-in suffixes never replace an old report."""
    for number in range(10001):
        candidate = raw if number == 0 else raw.with_name(raw.name + "-" + str(number).zfill(3))
        if candidate.exists() or candidate.is_symlink():
            if not unique:
                raise ValueError("--out already exists; select a new path or use --unique-out: " + str(candidate))
            continue
        out = validate_output(candidate, artifact_dirs)
        try:
            out.mkdir(parents=True, exist_ok=False)
            return out
        except FileExistsError:
            if not unique:
                raise
    raise ValueError("no free unique --out suffix in 10000 attempts")


def validate_artifacts(raw_paths: list[Path]) -> tuple[Path, ...]:
    result = set()
    for raw in raw_paths:
        path = Path(os.path.abspath(raw))
        for ancestor in (path, *path.parents):
            if ancestor.exists() or ancestor.is_symlink():
                if linkish(ancestor):
                    raise ValueError("--artifact-dir has a linked/reparse ancestor: " + str(ancestor))
        if not path.is_dir():
            raise ValueError("--artifact-dir must already exist: " + str(path))
        for name in PAIR_NAMES:
            if fingerprint(path / name)["state"] != "FILE":
                raise ValueError("--artifact-dir lacks a regular generated pair member: " + str(path / name))
        result.add(path.resolve())
    return tuple(sorted(result, key=label))


def required_execution(discovered: list[Path], results: list[dict]) -> list[dict]:
    """Missing/not-run/zero-test evidence cannot become a completed suite."""
    names = {p.name for p in discovered}
    by_name = {Path(row["test"]).name: row for row in results}
    rows = []
    for name in sorted(REQUIRED_SUITES):
        result = by_name.get(name)
        observed = [] if result is None else [row["value"] for row in
                    result["observations"]["observed_counts_not_totals"]
                    if row["kind"] == "unittest_ran"]
        expected = REPORTED_TEST_COUNTS[name]
        if name not in names:
            status = "NOT_AVAILABLE"
        elif result is None:
            status = "NOT_RUN"
        elif result["returncode"] != 0:
            status = "EXECUTION_FAILED"
        elif not observed or not all(count > 0 for count in observed):
            status = "NO_POSITIVE_TEST_COUNT_OBSERVED"
        elif expected is not None and any(count < expected for count in observed):
            status = "REPORTED_TEST_COUNT_SHORTFALL"
        else:
            status = "EXECUTED_REQUIRES_REVIEW"
        rows.append({"test": "Audit/" + name, "status": status,
                     "observed_unittest_counts_not_totals": observed,
                     "main_reported_prior_test_count_not_current_evidence": expected,
                     "acceptance": "NOT_ASSESSED"})
    return rows


def positive_seconds(value: str) -> float:
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be a finite positive number of seconds")
    return seconds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New report directory; never overwritten")
    parser.add_argument("--unique-out", action="store_true",
                        help="If --out exists, atomically reserve a new -001/-002/... sibling")
    parser.add_argument("--artifact-dir", type=Path, action="append", default=[],
                        help="Optional existing generated-pair directory to hash only; repeatable")
    parser.add_argument("--timeout", type=positive_seconds, default=1800.0,
                        help="Seconds per test process (default: 1800)")
    options = parser.parse_args()
    try:
        if not __debug__:
            raise ValueError("Python optimization is forbidden: test assertions must be enabled")
        temp = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/opencode"
        if not temp.is_dir() or linkish(temp):
            raise ValueError("approved, real OpenCode temporary directory is absent: " + str(temp))
        artifact_dirs = validate_artifacts(options.artifact_dir)
        legacy = legacy_reference()
        out = reserve_output(options.out, options.unique_out, artifact_dirs)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    completion = {"normal_end": False}
    print(json.dumps({"recorder_output_directory": str(out), "acceptance": "NOT_ASSESSED"}), flush=True)
    before = snapshot(legacy, artifact_dirs)
    write_json(out / "hashes-before.json", before)

    def exit_evidence() -> None:
        try:
            last = snapshot(legacy, artifact_dirs)
            last_drift = drift(before, last)
            last_problems = baseline_problems(last, legacy)
            write_json(out / "hashes-at-process-exit.json", last)
            write_json(out / "process-exit.json", {
                "normal_end": completion["normal_end"], "captured_utc": utc(),
                "recording_status": "FAILED" if last_drift or last_problems
                or not completion["normal_end"] else "EXIT_SNAPSHOT_RECORDED_REQUIRES_REVIEW",
                "source_drift": last_drift, "baseline_problems": last_problems,
                "acceptance": "NOT_ASSESSED",
                "note": "Best-effort atexit evidence only; no kill/crash durability guarantee. "
                        "This later snapshot can invalidate the earlier verdict; inspect both. "
                        "The Python returncode has already been selected before atexit."})
        except Exception as exc:
            print("could not retain process-exit evidence: " + repr(exc), file=sys.stderr)

    atexit.register(exit_evidence)
    discovered = suites()
    available = availability(discovered, before)
    write_json(out / "availability.json", available)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                       TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    environment.pop("PYTHONOPTIMIZE", None)
    write_json(out / "run.json", {
        "schema_version": "phase16-p3-test-recorder-1", "started_utc": utc(),
        "root": str(ROOT), "out": str(out), "python": sys.version, "executable": sys.executable,
        "requested_out": str(options.out), "unique_out_enabled": options.unique_out,
        "hash_only_tool_trees": [label(path) for path in TOOL_TREES],
        "additional_hash_only_artifact_dirs": [str(path) for path in artifact_dirs],
        "main_reported_prior_test_counts_not_current_evidence": REPORTED_TEST_COUNTS,
        "recorder_command": [sys.executable, *sys.argv], "suite_timeout_seconds": options.timeout,
        "discovery": "Direct regular Audit/test_phase16_p3*.py files, exact filename sort; no imports",
        "planned_commands": [suite_command(p) for p in discovered],
        "child_environment_overrides": {key: environment[key] for key in
                                        ("PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "TEMP", "TMP", "TMPDIR")},
        "python_optimization_removed": True, "legacy_fixture_count": len(legacy),
        "protected_p2_source_sha256": P2_ACCEPTED, "preserved_package_sha256": PACKAGE_PRESERVED_SHA,
        "hash_scope": "All scripts/*.py; all Audit/test_phase16*.py (P2 helpers hash-only); "
                      "Audit/phase16_p3*.py; this recorder; F01 input tree/authority/source candidates; "
                      "all examples/specs/fixtures bytes including accepted 49; all root *.skill; "
                      "explicit contracts/source evidence and P2/preservation manifests; "
                      "P3 tool trees/fixtures, main-build tree including any frozen generated pair, "
                      "explicit --artifact-dir trees and direct _phase16-p3-* evidence; Git HEAD.",
        "acceptance": "NOT_ASSESSED", "complete_phase16_or_p3": False,
        "limitations": ["Tests are trusted, not sandboxed; they may use owned temporary directories.",
                        "Hash snapshots cannot exclude change-and-revert or arbitrary races.",
                        "Missing filename checklist entries remain NOT_AVAILABLE, not SKIP/PASS.",
                        "No test filename, zero exit, mock or synthetic capture proves live geometry."]})
    results = []
    observed_drift: set[str] = set()
    problems = baseline_problems(before, legacy)
    stop_reason = "PROTECTED_BASELINE_OR_INVENTORY_FAILURE" if problems else None
    for index, script in enumerate(discovered, 1):
        if stop_reason:
            break
        directory = out / (str(index).zfill(3) + "-" + script.stem)
        directory.mkdir(exist_ok=False)
        suite_before = snapshot(legacy, artifact_dirs)
        write_json(directory / "hashes-before.json", suite_before)
        prior_drift = drift(before, suite_before)
        observed_drift.update(prior_drift)
        prior_problems = baseline_problems(suite_before, legacy)
        if prior_drift or prior_problems:
            problems.extend(prior_problems)
            stop_reason = "SOURCE_DRIFT_BEFORE_SUITE"
            write_json(directory / "not-run.json", {"test": label(script), "status": "NOT_RUN",
                                                   "reason": stop_reason, "source_drift": prior_drift})
            break
        command = suite_command(script)
        write_json(directory / "command.json", {"argv": command, "cwd": str(ROOT), "shell": False})
        started_utc, started = utc(), time.monotonic()
        code, execution_error = None, None
        try:
            process = subprocess.run(command, cwd=ROOT, env=environment, stdin=subprocess.DEVNULL,
                                     capture_output=True, timeout=options.timeout, check=False)
            stdout, stderr, code = process.stdout, process.stderr, process.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b"", exc.stderr or b""
            execution_error = "TIMEOUT: " + repr(exc)
            # run() kills/waits for the direct child, not arbitrary grandchildren.
            stop_reason = "TIMEOUT_DESCENDANT_STATE_UNKNOWN"
        except OSError as exc:
            stdout, stderr = b"", b""
            execution_error = repr(exc)
        seconds, ended_utc = round(time.monotonic() - started, 6), utc()
        stdout_record = write_raw(directory / "stdout.log", stdout)
        stderr_record = write_raw(directory / "stderr.log", stderr)
        suite_after = snapshot(legacy, artifact_dirs)
        write_json(directory / "hashes-after.json", suite_after)
        suite_drift = drift(suite_before, suite_after)
        observed_drift.update(drift(before, suite_after))
        after_problems = baseline_problems(suite_after, legacy)
        problems.extend(after_problems)
        observation = observations(stdout, stderr)
        result = {"test": label(script), "command": command, "cwd": str(ROOT),
                  "started_utc": started_utc, "ended_utc": ended_utc, "seconds": seconds,
                  "returncode": code, "execution_error": execution_error,
                  "stdout": stdout_record, "stderr": stderr_record, "source_drift": suite_drift,
                  "baseline_problems": after_problems, "observations": observation,
                  "disposition": "QUALIFIERS_REQUIRE_REVIEW" if observation["qualifier_lines"]
                  else "EXECUTED_REQUIRES_REVIEW", "acceptance": "NOT_ASSESSED"}
        results.append(result)
        write_json(directory / "result.json", result)
        print(json.dumps({"test": label(script), "returncode": code, "seconds": seconds,
                          "qualifier_lines": len(observation["qualifier_lines"]),
                          "source_drift": suite_drift}), flush=True)
        if suite_drift or after_problems:
            stop_reason = "SOURCE_DRIFT_OR_BASELINE_FAILURE_AFTER_SUITE"

    after = snapshot(legacy, artifact_dirs)
    write_json(out / "hashes-after.json", after)
    observed_drift.update(drift(before, after))
    problems.extend(baseline_problems(after, legacy))
    executed = {r["test"] for r in results}
    not_run = [{"test": label(p), "status": "NOT_RUN", "reason": stop_reason or "UNEXPLAINED"}
               for p in discovered if label(p) not in executed]
    unavailable = [row for row in available if row["status"] == "NOT_AVAILABLE"
                   and row.get("blocks_offline_recorder", True)]
    required = required_execution(discovered, results)
    coverage_qualifications = [row for row in required if row["status"] != "EXECUTED_REQUIRES_REVIEW"]
    nonzero = [r["test"] for r in results if r["returncode"] != 0]
    failed = bool(observed_drift or problems or nonzero or not_run or not discovered)
    exit_code = 1 if failed else 2 if unavailable or coverage_qualifications else 0
    verdict = {
        "timestamp_utc": utc(), "recording_status": "FAILED" if failed else
        "RECORDED_WITH_NOT_AVAILABLE" if unavailable else "RECORDED_WITH_COVERAGE_QUALIFICATIONS"
        if coverage_qualifications else "RECORDED_REQUIRES_REVIEW",
        "recorder_exit_code": exit_code, "acceptance": "NOT_ASSESSED", "complete_phase16_or_p3": False,
        "output_directory": str(out),
        "expected_discovered_scripts": len(discovered), "executed_scripts": len(results),
        "all_discovered_executed": not not_run and bool(discovered), "not_run": not_run,
        "required_not_available": unavailable, "nonzero_or_unexecuted_returncodes": nonzero,
        "required_suite_execution": required,
        "required_suite_coverage_qualifications": coverage_qualifications,
        "all_required_suite_sources_present": all(Path(row["test"]).name in
                {p.name for p in discovered} for row in required),
        "all_required_suites_have_positive_execution_evidence": not coverage_qualifications,
        "frozen_generated_pairs": after["frozen_generated_pairs"],
        "source_drift": sorted(observed_drift), "baseline_problems": problems,
        "git_head_before": before["git"].get("head"), "git_head_after": after["git"].get("head"),
        "note": "Zero is recorder health only, NEVER acceptance. Review raw logs and every "
                "SKIP/xfail/observation; no live/produced-poly evidence is inferred. "
                "P2 suites are not rerun. A changed tree stops the batch and fails it."}
    write_json(out / "results.json", results)
    write_json(out / "snapshot-verdict.json", verdict)
    print(json.dumps(verdict), flush=True)
    completion["normal_end"] = True
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
