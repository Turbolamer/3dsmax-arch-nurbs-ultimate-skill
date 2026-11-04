#!/usr/bin/env python3
"""Record, but do not accept, the next frozen P3.1 offline suite.

Stop all authors first.  From the repository root, supply --out NEW_DIRECTORY;
repeat --input for each additional policy/probe file or directory and --suite
for independently authored test scripts outside Audit/test_phase16_p3*.py.
See README.md.  This program does not invoke Max or an installer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "Audit"
SELF = Path(__file__).resolve()
F01 = AUDIT / "phase16-p3-f01-input-2026-11-02e"
P2_MANIFEST = AUDIT / "phase16-p2-final-2026-11-02d/hashes-before.json"
P2_MANIFEST_SHA = "089c6744e176198c547eba6300ef181c05bb64850eaae209d89c73b4becbdf72"
PACKAGE = "3dsmax-arch-nurbs-ultimate.skill"
PRESERVED_PACKAGE_SHA = "dbd0e28003a6f87cafc7215f63fec10df5f576f54b1e66fa131d8b1c9234491a"
P2_SOURCES = {
    "scripts/init_project.py": "42401725a42271b1c45dbeabed22bb76b73587e7b85e9fe970801b606092eb88",
    "scripts/place_components.py": "4f9735ffbf9d59f6e858bed5d6390342db8230b50a036e462d894c00d07b91ac",
    "scripts/validate_specs.py": "616050417380f587fb210e30761df6e025bb5433a2210576018953e67dd9716f",
    "scripts/wall_cell_coverage.py": "d8d1e930808465f3340e2ed2e4cc04e45b46d033cc14ebc57ecb66a61b6ece4e",
}
P3_SOURCES = (
    "scripts/build_wall_surface.py", "scripts/wall_surface_inputs.py",
    "scripts/wall_surface_runtime.py", "scripts/wall_surface_publish.py",
)
# Actual FINAL2 top-level test counts: lower counts require a new reviewed policy,
# not an automatic claim that fewer tests are equivalent.
REQUIRED_SUITES = {
    "test_phase16_p3_builder.py": 34,
    "test_phase16_p3_existing_output_review.py": 7,
    "test_phase16_p3_independent.py": 22,
    "test_phase16_p3_inputs.py": 38,
    "test_phase16_p3_oracle.py": 65,
    "test_phase16_p3_publication.py": 42,
    "test_phase16_p3_runtime.py": 42,
}
# Identified independent suites outside the direct-discovery directory.  Include
# only if present, and never infer that other arbitrary audit scripts are safe.
OPTIONAL_INDEPENDENT = (
    "Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py",
)
MAIN03 = {
    "Audit/phase16-p3-main-build-2026-11-02e/Main03/published/wall_surface.json":
        "59aa9741db9a40a8c593623e898fa956a4d061781bc695d30b5306b0b3e6565b",
    "Audit/phase16-p3-main-build-2026-11-02e/Main03/published/wall_surface.ms":
        "91274ffbb1cb9491c6b5fd511ceb238346f45434e56c2d6b467753a7cbdaaf28",
    "Audit/phase16-p3-main-build-2026-11-02e/Main03/main_only_arm.ms":
        "825707e3bec8ec3efa48b971a442bd2941379ea5b1121c1871572182aabb6a61",
    "Audit/phase16-p3-main-build-2026-11-02e/Main03/held_pair_filein.ms":
        "c09d122744cb2475fd8c5679e7797026b9a5e905a44e6e3a8fafddc23324597c",
}
FIXED = (
    "AGENTS.md", "CHECKPOINT.md", "PLAN.md", "references/07-spec-grammar.md",
    "Audit/phase16_p3_oracle.py", "Audit/AGENT_PLAN_poly_surface_shell.md",
    "Audit/EVIDENCE_2026-10-27.md", "Audit/_phase16-p3-contract-2026-11-02e.md",
    "Audit/_phase16-p3-resume-2026-11-02e.md", "Audit/_phase16-p3-final-run-review-2026-11-02e.md",
    "Audit/run_phase16_p3_settled.py", "Audit/_phase16-p3-preservation-2026-11-02e.json",
)
F01_REQUIRED = tuple("Audit/phase16-p3-f01-input-2026-11-02e/" + n for n in (
    "direction-authority.json", "input-lock.json", "project/assumptions.json",
    "project/conflicts_resolved.json", "project/dimensions.json", "project/walls.json",
))
TOOL_TREES = tuple(AUDIT / name for name in (
    "phase16-p3-preflight-2026-11-02e", "phase16-p3-measurement-2026-11-02e",
    "phase16-p3-execution-2026-11-02e", "phase16-p3-live-controls-2026-11-02e",
    "phase16-p3-runtime-probes-2026-11-02e", "phase16-p3-state-probes-2026-11-02e",
    "phase16-p3-main-build-2026-11-02e",
))
PRIOR_TREES = tuple(AUDIT / name for name in (
    "phase16-p3-final-2026-11-02e", "phase16-p3-final2-2026-11-02e",
))
PRIOR_MANIFESTS = {
    "Audit/phase16-p3-final-2026-11-02e/snapshot-verdict.json":
        "db0e90797081e5e1040f17346046b7df1896fe961024176c8c9f7bf6d68ad21a",
    "Audit/phase16-p3-final2-2026-11-02e/results.json":
        "2369b63e65dcd4f253ba7ce07c7eb396ecbaa90fa0c42d8b4900c83ae1db74a2",
    "Audit/phase16-p3-final2-2026-11-02e/hashes-before.json":
        "a70b949d488fb92f4afd45a16f670b963ea056c35eb4d54115abbefcd66cd16a",
    "Audit/phase16-p3-final2-2026-11-02e/hashes-after.json":
        "a9986f5b505b4a861a739ad42279a205c82f9a2e4d3a27bbb98eed7748b64192",
    "Audit/phase16-p3-final2-2026-11-02e/hashes-at-process-exit.json":
        "287a93d4ac59b47e08bd592af900787ee0acf2185c3d647d9f50664ddc58b89f",
    "Audit/phase16-p3-final2-2026-11-02e/snapshot-verdict.json":
        "237c81051af007d6d71f075c90383389e671e67927bf33d5ec07920a00cde32b",
    "Audit/phase16-p3-final2-2026-11-02e/process-exit.json":
        "5b45eeb4e83e66c3ff6c24ad4b902d86deb190cbcdbf6adbdacfec505a616bcb",
}
TIMEOUT = 1800.0


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def label(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def within(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def linkish(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def no_link_ancestors(path: Path) -> None:
    for part in (path, *path.parents):
        try:
            if linkish(part):
                raise ValueError("linked/reparse path refused: " + str(part))
        except FileNotFoundError:
            continue


def fingerprint(path: Path) -> dict:
    try:
        no_link_ancestors(path)
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            return {"state": "NOT_REGULAR"}
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            while True:
                data = stream.read(1024 * 1024)
                if not data:
                    break
                digest.update(data)
                size += len(data)
        return {"state": "FILE", "sha256": digest.hexdigest(), "size": size}
    except FileNotFoundError:
        return {"state": "NOT_AVAILABLE"}
    except (OSError, ValueError) as exc:
        return {"state": "READ_ERROR", "error": repr(exc)}


def tree_files(directory: Path, errors: list[dict]) -> set[Path]:
    """Inventory file bytes without silently following links, even in subtrees."""
    paths: set[Path] = set()
    try:
        no_link_ancestors(directory)
        if not directory.is_dir():
            raise ValueError("not an available directory")

        def onerror(exc: OSError) -> None:
            errors.append({"path": str(exc.filename), "error": repr(exc)})

        for base, dirs, files in os.walk(directory, followlinks=False, onerror=onerror):
            dirs.sort()
            for name in list(dirs):
                path = Path(base) / name
                if name == "__pycache__":
                    dirs.remove(name)
                elif linkish(path):
                    dirs.remove(name)
                    errors.append({"path": label(path), "error": "linked directory refused"})
            for name in sorted(files):
                if not name.endswith((".pyc", ".pyo")):
                    paths.add(Path(base) / name)
    except (OSError, ValueError) as exc:
        errors.append({"path": label(directory), "error": repr(exc)})
    return paths


def read_object(path: Path) -> dict:
    no_link_ancestors(path)

    def unique(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError("duplicate key: " + repr(key))
            data[key] = value
        return data

    data = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise ValueError("expected JSON object: " + str(path))
    return data


def legacy_reference() -> dict[str, str]:
    if fingerprint(P2_MANIFEST).get("sha256") != P2_MANIFEST_SHA:
        raise ValueError("accepted P2 manifest does not match retained bytes")
    value = read_object(P2_MANIFEST)
    selected = {name: sha for name, sha in value.items()
                if name.startswith(("examples/", "specs/fixtures/"))}
    if len(selected) != 49 or any(
        Path(name).is_absolute() or ".." in Path(name).parts or "\\" in name
        or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)
        for name, sha in selected.items()
    ):
        raise ValueError("accepted manifest must contain exactly 49 safe fixture paths")
    if any(value.get(name) != sha for name, sha in P2_SOURCES.items()):
        raise ValueError("accepted manifest disagrees with four accepted P2 sources")
    return selected


def authority_source(errors: list[dict]) -> set[Path]:
    paths = {F01 / "direction-authority.json"}
    try:
        record = read_object(F01 / "direction-authority.json")
        raw = record.get("source_file")
        if not isinstance(raw, str) or not raw or "\0" in raw:
            raise ValueError("invalid authority source_file")
        token = Path(raw)
        # This fixture's reviewed convention is process-CWD relative, with no fallback.
        if token.is_absolute() or ".." in token.parts:
            raise ValueError("F01 authority must be repository-relative without traversal")
        source = absolute(ROOT / token)
        paths.add(source)
        if fingerprint(source).get("sha256") != record.get("source_sha256"):
            raise ValueError("authority source hash does not match actual source bytes")
        if fingerprint(F01 / "project/walls.json").get("sha256") != record.get("walls_sha256"):
            raise ValueError("authority walls hash does not match actual wall bytes")
    except (OSError, ValueError, TypeError) as exc:
        errors.append({"path": label(F01 / "direction-authority.json"), "error": repr(exc)})
    return paths


def discovered_suites(explicit: tuple[Path, ...]) -> list[Path]:
    direct = {absolute(p) for p in AUDIT.glob("test_phase16_p3*.py")
              if p.is_file() or p.is_symlink()}
    known_extra = {ROOT / name for name in OPTIONAL_INDEPENDENT
                   if (ROOT / name).is_file() or (ROOT / name).is_symlink()}
    return sorted(direct | known_extra | set(explicit),
                  key=label)


def git_head() -> dict:
    command = ["git", "rev-parse", "--verify", "HEAD"]
    try:
        proc = subprocess.run(command, cwd=ROOT, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"),
                              stdin=subprocess.DEVNULL, capture_output=True, timeout=15, check=False)
        text = proc.stdout.decode("ascii", errors="replace").strip()
        return {"command": command, "returncode": proc.returncode, "head": text,
                "stderr": proc.stderr.decode("utf-8", errors="replace")}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "returncode": None, "head": None, "error": repr(exc)}


def snapshot(legacy: dict[str, str], inputs: tuple[Path, ...], extra_suites: tuple[Path, ...]) -> dict:
    errors: list[dict] = []
    paths = {SELF, P2_MANIFEST, ROOT / PACKAGE}
    paths.update(ROOT / name for name in (*FIXED, *F01_REQUIRED, *P3_SOURCES,
                                          *P2_SOURCES, *MAIN03, *legacy))
    paths.update((ROOT / "scripts").glob("*.py"))
    for pattern in ("test_phase16*.py", "phase16_p3*.py", "_phase16-p3-*"):
        paths.update(p for p in AUDIT.glob(pattern) if p.is_file() or p.is_symlink())
    paths.update(ROOT.glob("*.skill"))
    suites = discovered_suites(extra_suites)
    paths.update(suites)
    for directory in (ROOT / "examples", ROOT / "specs/fixtures", F01, *TOOL_TREES, *PRIOR_TREES):
        paths.update(tree_files(directory, errors))
    for path in inputs:
        if path.is_dir() and not linkish(path):
            paths.update(tree_files(path, errors))
        else:
            paths.add(path)
    paths.update(authority_source(errors))
    files = {label(path): fingerprint(path) for path in sorted(paths, key=label)}
    errors.extend({"path": name, "error": item["state"]} for name, item in files.items()
                  if item["state"] != "FILE")
    return {"captured_utc": now(), "files": files, "git": git_head(),
            "discovered_suites": [label(path) for path in suites], "inventory_errors": errors}


def drift(first: dict, second: dict) -> list[str]:
    old, new = first["files"], second["files"]
    changes = [name for name in old.keys() | new.keys() if old.get(name) != new.get(name)]
    if first["git"].get("head") != second["git"].get("head"):
        changes.append("GIT_HEAD")
    if first["discovered_suites"] != second["discovered_suites"]:
        changes.append("P3_SUITE_DISCOVERY")
    return sorted(changes)


def baseline_problems(state: dict, legacy: dict[str, str]) -> list[dict]:
    problems = list(state["inventory_errors"])
    head = state["git"]
    if head.get("returncode") != 0 or not re.fullmatch(r"[0-9a-f]{40,64}", head.get("head") or ""):
        problems.append({"path": "GIT_HEAD", "error": "unavailable or invalid"})
    expected = {**P2_SOURCES, **legacy, **MAIN03, **PRIOR_MANIFESTS, PACKAGE: PRESERVED_PACKAGE_SHA,
                label(P2_MANIFEST): P2_MANIFEST_SHA}
    for name, sha in expected.items():
        observed = state["files"].get(name, {})
        if observed.get("sha256") != sha:
            problems.append({"path": name, "error": "protected baseline mismatch",
                             "expected_sha256": sha, "observed": observed})
    names = {label(AUDIT / name) for name in REQUIRED_SUITES}
    for name in sorted(names - set(state["discovered_suites"])):
        problems.append({"path": name, "error": "required suite missing"})
    return problems


def validate_inputs(raw_inputs: list[Path], raw_suites: list[Path]) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    inputs, suites = set(), set()
    for raw, target, suite in [(p, inputs, False) for p in raw_inputs] + [(p, suites, True) for p in raw_suites]:
        path = absolute(raw)
        no_link_ancestors(path)
        if suite:
            if path.suffix.lower() != ".py" or fingerprint(path)["state"] != "FILE":
                raise ValueError("--suite must identify an existing regular .py file: " + str(path))
        elif not (path.is_dir() or fingerprint(path)["state"] == "FILE"):
            raise ValueError("--input must identify an existing regular file or directory: " + str(path))
        target.add(path)
    return tuple(sorted(inputs, key=label)), tuple(sorted(suites, key=label))


def reserve_output(raw: Path, inputs: tuple[Path, ...], suites: tuple[Path, ...]) -> Path:
    out = absolute(raw)
    no_link_ancestors(out)
    # Direct child only: no previous recorder or input tree can become a parent.
    if out.parent != AUDIT:
        raise ValueError("--out must be a NEW direct child of " + str(AUDIT))
    if out.name.lower().startswith(("_phase16-p3-", "test_phase16", "phase16_p3")):
        raise ValueError("--out name collides with an automatic input discovery pattern")
    for path in (*inputs, *suites, SELF, F01, *TOOL_TREES, *PRIOR_TREES):
        if within(out, path) or within(path, out):
            raise ValueError("output overlaps an input or protected tree: " + str(path))
    out.mkdir(exist_ok=False)
    return out


def write_json(path: Path, data) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def write_raw(path: Path, data: bytes) -> dict:
    with path.open("xb") as stream:
        stream.write(data)
    return {"path": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def observations(stdout: bytes, stderr: bytes, minimum: int = 1) -> dict:
    """Conservative unittest evidence parser. Raw output remains authoritative."""
    lines = [(name, number, line) for name, raw in (("stdout", stdout), ("stderr", stderr))
             for number, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1)]
    ran, oks, bad, metadata = [], [], [], []
    outcome = re.compile(r"(?i)(?:\.\.\.\s*|^\s*)(?:SKIP(?:PED)?|XFAIL(?:ED)?|XPASS(?:ED)?|"
                         r"EXPECTED FAILURE|UNEXPECTED SUCCESS)(?:\b|\s*\[)")
    numeric = re.compile(r'(?i)["\']?(skipped|skips|xfails?|xpasses?|expected[_ ]failures?|'
                         r'unexpected[_ ]success(?:es)?)["\']?\s*[:=]\s*(\d+)')
    reverse_numeric = re.compile(r"(?i)\b([1-9]\d*)\s+(?:skipped|xfailed|xpassed|"
                                 r"expected failures?|unexpected successes)\b")
    failed_line = re.compile(r"(?i)^\s*(?:FAILED|ERROR|FAIL|NOT[_ ]RUN|NOT[_ ]AVAILABLE)\b")
    for stream, number, line in lines:
        row = {"stream": stream, "line": number, "text": line}
        match = re.fullmatch(r"Ran (\d+) tests? in [^\r\n]+", line)
        if match:
            ran.append({**row, "count": int(match.group(1))})
        if re.fullmatch(r"OK(?: \([^\r\n]*\))?", line):
            oks.append(row)
        if outcome.search(line) or failed_line.search(line) or reverse_numeric.search(line):
            bad.append(row)
        for item in numeric.finditer(line):
            record = {**row, "kind": item.group(1), "count": int(item.group(2))}
            metadata.append(record)
            if record["count"] != 0:
                bad.append(record)
        # An OK qualifier not matching a numeric zero marker is ambiguous.
        if line.startswith("OK (") and not re.fullmatch(
            r"OK \((?:\s*(?:skipped|expected failures?|unexpected successes|xfails?)=0\s*,?)+\)",
            line, re.I,
        ):
            bad.append({**row, "reason": "unrecognized unittest OK qualifier"})
    issues = []
    if len(ran) != 1 or ran[0]["count"] < minimum:
        issues.append("expected exactly one positive unittest Ran count >= " + str(minimum))
    if len(oks) != 1:
        issues.append("expected exactly one unittest OK summary")
    if bad:
        issues.append("skip/xfail/unexpected-success/failure or ambiguous outcome observed")
    return {"ran": ran, "ok_summaries": oks, "prohibited_or_failed": bad,
            "qualifier_metadata": metadata, "issues": issues,
            "status": "REFUSED" if issues else "UNQUALIFIED_OUTPUT_REQUIRES_REVIEW"}


def run_suite(script: Path, directory: Path, environment: dict, minimum: int) -> tuple[dict, bool]:
    command = [sys.executable, "-B", str(script)]
    # Reviewed original entrypoints accept -v. Unknown suites receive no guessed flags.
    if script.name in REQUIRED_SUITES and script.parent == AUDIT:
        command.append("-v")
    write_json(directory / "command.json", {"argv": command, "cwd": str(ROOT), "shell": False})
    started, started_utc = time.monotonic(), now()
    code, error, timed_out = None, None, False
    try:
        proc = subprocess.run(command, cwd=ROOT, env=environment, stdin=subprocess.DEVNULL,
                              capture_output=True, timeout=TIMEOUT, check=False)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
        error, timed_out = repr(exc), True
    except OSError as exc:
        stdout, stderr, error = b"", b"", repr(exc)
    result = {"test": label(script), "command": command, "started_utc": started_utc,
              "ended_utc": now(), "seconds": round(time.monotonic() - started, 6),
              "returncode": code, "execution_error": error,
              "stdout": write_raw(directory / "stdout.log", stdout),
              "stderr": write_raw(directory / "stderr.log", stderr),
              "observations": observations(stdout, stderr, minimum), "acceptance": "NOT_ASSESSED"}
    return result, timed_out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="new direct child of Audit; no clobber")
    parser.add_argument("--input", type=Path, action="append", default=[],
                        help="additional existing policy/probe/source file or tree to hash; repeatable")
    parser.add_argument("--suite", type=Path, action="append", default=[],
                        help="additional explicit unittest .py entrypoint to execute; repeatable")
    options = parser.parse_args(argv)
    try:
        if not __debug__:
            raise ValueError("optimized Python is forbidden")
        if absolute(Path.cwd()) != ROOT:
            raise ValueError("invoke from repository root: " + str(ROOT))
        temp = Path(os.environ["LOCALAPPDATA"]) / "Temp/opencode"
        no_link_ancestors(temp)
        if not temp.is_dir():
            raise ValueError("approved OpenCode temporary directory is unavailable")
        inputs, extra_suites = validate_inputs(options.input, options.suite)
        legacy = legacy_reference()
        out = reserve_output(options.out, inputs, extra_suites)
    except (KeyError, OSError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps({"recorder_output_directory": str(out), "acceptance": "NOT_ASSESSED"}), flush=True)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                       TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    environment.pop("PYTHONOPTIMIZE", None)
    before = snapshot(legacy, inputs, extra_suites)
    write_json(out / "hashes-before.json", before)
    suites = discovered_suites(extra_suites)
    write_json(out / "run.json", {
        "schema": "phase16-p3-next-frozen-recorder-1", "started_utc": now(),
        "argv": [sys.executable, *sys.argv], "root": str(ROOT), "out": str(out),
        "python": sys.version, "timeout_seconds_per_suite": TIMEOUT,
        "additional_explicit_inputs": [str(p) for p in inputs],
        "additional_explicit_suites": [str(p) for p in extra_suites],
        "suite_plan": [label(p) for p in suites], "required_final2_test_count_floors": REQUIRED_SUITES,
        "legacy_fixture_count": len(legacy), "accepted_p2_sources": P2_SOURCES,
        "prior_main03_sha256": MAIN03, "acceptance": "NOT_ASSESSED",
        "complete_phase16_or_p3": False,
        "limitations": ["Tests are trusted executable programs, not sandboxed.",
                        "Snapshots cannot detect change/revert or arbitrary concurrent races.",
                        "Supply every new non-discovered test and runtime policy/probe source explicitly.",
                        "Output is not a live Max, F01, replay or stage-acceptance assessment."],
    })
    results, observed_drift = [], set()
    problems = baseline_problems(before, legacy)
    stop = "BASELINE_OR_INVENTORY" if problems else None
    for index, script in enumerate(suites, 1):
        if stop:
            break
        directory = out / (str(index).zfill(3) + "-" + script.stem)
        directory.mkdir(exist_ok=False)
        suite_before = snapshot(legacy, inputs, extra_suites)
        write_json(directory / "hashes-before.json", suite_before)
        changes, current_problems = drift(before, suite_before), baseline_problems(suite_before, legacy)
        observed_drift.update(changes)
        problems.extend(current_problems)
        if changes or current_problems:
            stop = "DRIFT_OR_BASELINE_BEFORE_SUITE"
            write_json(directory / "not-run.json", {"test": label(script), "reason": stop,
                                                    "source_drift": changes})
            break
        floor = REQUIRED_SUITES.get(script.name, 1) if script.parent == AUDIT else 1
        result, timed_out = run_suite(script, directory, environment, floor)
        suite_after = snapshot(legacy, inputs, extra_suites)
        write_json(directory / "hashes-after.json", suite_after)
        changes = drift(suite_before, suite_after)
        observed_drift.update(drift(before, suite_after))
        current_problems = baseline_problems(suite_after, legacy)
        problems.extend(current_problems)
        result["source_drift"] = changes
        result["baseline_problems"] = current_problems
        results.append(result)
        write_json(directory / "result.json", result)
        print(json.dumps({"test": result["test"], "returncode": result["returncode"],
                          "observation_status": result["observations"]["status"],
                          "source_drift": changes}), flush=True)
        if timed_out:
            stop = "TIMEOUT_DESCENDANT_STATE_UNKNOWN"
        elif changes or current_problems:
            stop = "DRIFT_OR_BASELINE_AFTER_SUITE"

    after = snapshot(legacy, inputs, extra_suites)
    write_json(out / "hashes-after.json", after)
    observed_drift.update(drift(before, after))
    problems.extend(baseline_problems(after, legacy))
    executed = {row["test"] for row in results}
    not_run = [{"test": label(p), "reason": stop or "UNEXPLAINED"}
               for p in suites if label(p) not in executed]
    failed_suites = [row["test"] for row in results if row["returncode"] != 0
                     or row["execution_error"] or row["observations"]["issues"]]
    # Take another explicit exit-boundary snapshot before selecting the exit code.
    final = snapshot(legacy, inputs, extra_suites)
    write_json(out / "hashes-at-process-exit.json", final)
    observed_drift.update(drift(before, final))
    problems.extend(baseline_problems(final, legacy))
    failed = bool(problems or observed_drift or failed_suites or not_run or not suites)
    verdict = {"recording_status": "FAILED" if failed else "RECORDED_REQUIRES_REVIEW",
               "recorder_exit_code": 1 if failed else 0, "acceptance": "NOT_ASSESSED",
               "complete_phase16_or_p3": False, "expected_suites": len(suites),
               "executed_suites": len(results), "not_run": not_run, "failed_suites": failed_suites,
               "source_drift": sorted(observed_drift), "baseline_problems": problems,
               "head_before": before["git"].get("head"), "head_at_exit": final["git"].get("head"),
               "note": "Inspect raw logs and all snapshots; zero means recorder health only. "
                       "Exit snapshot is before process exit, not a lock or crash-durability guarantee."}
    write_json(out / "results.json", results)
    write_json(out / "snapshot-verdict.json", verdict)
    write_json(out / "process-exit.json", {"normal_end": True, "captured_utc": now(),
                                           "acceptance": "NOT_ASSESSED",
                                           "note": "Written immediately before return; abnormal exits may lack this file."})
    print(json.dumps(verdict), flush=True)
    return verdict["recorder_exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
