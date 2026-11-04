#!/usr/bin/env python3
"""Exercise recorder behavior in a wholly disposable, owned fake repository.

No production P3 suite is run. All created files stay below --out, a new child
of this script's directory. Raw controls and reports are intentionally retained.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
RECORDER = HERE / "recorder.py"
spec = importlib.util.spec_from_file_location("next_recorder_selftest", RECORDER)
recorder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(recorder)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def put(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def suite_source(kind: str) -> bytes:
    bodies = {
        "pass": "        self.assertEqual(2 + 2, 4)",
        "fail": "        self.assertEqual(2 + 2, 5)",
        "skip": "        self.skipTest('deliberate skip control')",
        "xfail": "        self.assertEqual(2 + 2, 5)",
        "unexpected": "        self.assertEqual(2 + 2, 4)",
        "mutate": "        pathlib.Path('scripts/runtime.py').write_text('mutated', encoding='utf8')",
        "policy_drift": "        pathlib.Path('policy.ms').write_text('mutated policy', encoding='utf8')",
    }
    if kind == "empty":
        return b"import unittest\nunittest.main()\n"
    decorator = "    @unittest.expectedFailure\n" if kind in ("xfail", "unexpected") else ""
    return ("import pathlib, unittest\nclass Control(unittest.TestCase):\n" + decorator +
            "    def test_control(self):\n" + bodies[kind] + "\nunittest.main()\n").encode()


def make_fake(root: Path, kind: str) -> None:
    (root / "Audit").mkdir(parents=True)
    put(root / "scripts/runtime.py", b"unmutated")
    put(root / "policy.ms", b"explicit policy baseline")
    put(root / "fixture.dat", b"legacy fixture bytes")
    put(root / "package.skill", b"preserved package bytes")
    put(root / "prior.json", b"old manifest bytes")
    put(root / "f01/project/walls.json", b"input wall bytes")
    put(root / "source.md", b"authority source bytes")
    authority = {"source_file": "source.md", "source_sha256": sha(b"authority source bytes"),
                 "walls_sha256": sha(b"input wall bytes")}
    put(root / "f01/direction-authority.json", json.dumps(authority).encode())
    for name in ("examples", "specs/fixtures", "old-run-one", "old-run-two"):
        (root / name).mkdir(parents=True)
    put(root / "old-run-one/evidence.json", b"prior failure")
    put(root / "old-run-two/evidence.json", b"prior success")
    put(root / "Audit/control_suite.py", suite_source(kind))
    put(root / "Audit/following_suite.py", suite_source("pass"))


def configure_fake(root: Path) -> None:
    recorder.ROOT = root
    recorder.AUDIT = root / "Audit"
    recorder.F01 = root / "f01"
    recorder.SELF = RECORDER
    recorder.P2_MANIFEST = root / "prior.json"
    recorder.P2_MANIFEST_SHA = sha(b"old manifest bytes")
    recorder.PACKAGE = "package.skill"
    recorder.PRESERVED_PACKAGE_SHA = sha(b"preserved package bytes")
    recorder.P2_SOURCES = {"scripts/runtime.py": sha(b"unmutated")}
    recorder.P3_SOURCES = ()
    recorder.MAIN03 = {}
    recorder.PRIOR_MANIFESTS = {}
    recorder.FIXED = ()
    recorder.F01_REQUIRED = ()
    recorder.TOOL_TREES = ()
    recorder.PRIOR_TREES = (root / "old-run-one", root / "old-run-two")
    recorder.REQUIRED_SUITES = {"control_suite.py": 1}
    recorder.OPTIONAL_INDEPENDENT = ()
    recorder.legacy_reference = lambda: {"fixture.dat": sha(b"legacy fixture bytes")}
    recorder.git_head = lambda: {"command": ["fake_git_control"], "returncode": 0,
                                 "head": "a" * 40, "stderr": ""}


def verify_raw(run: Path, expected: int, expected_summary: str) -> dict:
    verdict = json.loads((run / "snapshot-verdict.json").read_text(encoding="utf8"))
    assert verdict["recorder_exit_code"] == expected, verdict
    assert verdict["acceptance"] == "NOT_ASSESSED"
    result = json.loads((run / "results.json").read_text(encoding="utf8"))[0]
    entry = next(p for p in run.iterdir() if p.is_dir())
    for stream in ("stdout", "stderr"):
        data = (entry / (stream + ".log")).read_bytes()
        assert result[stream]["sha256"] == sha(data)
        assert result[stream]["bytes"] == len(data)
    assert expected_summary in (entry / "stderr.log").read_text(encoding="utf8")
    assert (run / "hashes-before.json").is_file()
    assert (entry / "hashes-before.json").is_file()
    assert (entry / "hashes-after.json").is_file()
    assert (run / "hashes-after.json").is_file()
    assert (run / "hashes-at-process-exit.json").is_file()
    assert json.loads((run / "process-exit.json").read_text())["normal_end"] is True
    initial = json.loads((run / "hashes-before.json").read_text())
    assert "policy.ms" in initial["files"]
    assert not any("/Audit/record/" in x or x.startswith("Audit/record/") for x in initial["files"])
    return verdict


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    options = parser.parse_args()
    out = Path(os.path.abspath(options.out))
    if out.parent != HERE:
        parser.error("self-test --out must be a new direct child of " + str(HERE))
    recorder.no_link_ancestors(out)
    out.mkdir(exist_ok=False)
    real_cwd = Path.cwd()
    controls = [("pass", 0, "OK"), ("fail", 1, "FAILED"), ("skip", 1, "skipped=1"),
                ("xfail", 1, "expected failures=1"), ("unexpected", 1, "unexpected successes=1"),
                ("empty", 1, "Ran 0 tests"), ("mutate", 1, "OK"), ("policy_drift", 1, "OK")]
    outcomes = []
    try:
        for kind, expected, summary in controls:
            root = out / kind
            make_fake(root, kind)
            configure_fake(root)
            os.chdir(root)
            capture_out, capture_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(capture_out), contextlib.redirect_stderr(capture_err):
                exit_code = recorder.main(["--out", "Audit/record", "--input", "policy.ms",
                                           "--suite", "Audit/control_suite.py",
                                           "--suite", "Audit/following_suite.py"])
            run = root / "Audit/record"
            put(root / "driver-stdout.txt", capture_out.getvalue().encode())
            put(root / "driver-stderr.txt", capture_err.getvalue().encode())
            assert exit_code == expected, (kind, exit_code, expected)
            verdict = verify_raw(run, expected, summary)
            if kind == "mutate":
                assert "scripts/runtime.py" in verdict["source_drift"]
            if kind == "policy_drift":
                assert "policy.ms" in verdict["source_drift"]
            if kind in ("mutate", "policy_drift"):
                assert verdict["executed_suites"] == 1 and len(verdict["not_run"]) == 1
            else:
                # Failure and qualifiers are retained without suppressing the second suite.
                assert verdict["executed_suites"] == 2 and not verdict["not_run"]
            # A prior recorder result must never be replaced.
            protected = (run / "snapshot-verdict.json").read_bytes()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try:
                    recorder.main(["--out", "Audit/record", "--input", "policy.ms",
                                   "--suite", "Audit/control_suite.py",
                                   "--suite", "Audit/following_suite.py"])
                except SystemExit as exc:
                    assert exc.code == 2
                else:
                    raise AssertionError("existing output was not refused")
            assert (run / "snapshot-verdict.json").read_bytes() == protected
            assert (root / "old-run-one/evidence.json").read_bytes() == b"prior failure"
            assert (root / "old-run-two/evidence.json").read_bytes() == b"prior success"
            outcomes.append({"control": kind, "expected_exit": expected,
                             "actual_exit": exit_code, "status": "observed as expected"})

        # Calibrate non-unittest marker handling without running a real suite.
        for qualifier in ("1 skipped", "2 xfailed", "XFAIL reason", "XPASS reason", "test_a ... skipped 'x'"):
            assert recorder.observations(b"", ("Ran 1 test in 0.001s\nOK\n" + qualifier).encode())["issues"]
        assert not recorder.observations(b"", b'Ran 1 test in 0.001s\nOK\n{"skips": 0}\n')["issues"]
        # Discovery-prefix output names and an input ancestor must fail before mkdir.
        for forbidden in (root / "Audit/_phase16-p3-evidence", root / "Audit/phase16_p3_output"):
            try:
                recorder.reserve_output(forbidden, (), ())
            except ValueError:
                assert not forbidden.exists()
            else:
                raise AssertionError("discovery-colliding output was accepted")
        try:
            recorder.reserve_output(root / "Audit/overlapping", (root / "Audit",), ())
        except ValueError:
            assert not (root / "Audit/overlapping").exists()
        else:
            raise AssertionError("output inside an explicit input was accepted")
        put(out / "selftest-results.json", (json.dumps({"controls": outcomes,
            "additional_checks": ["raw log hashes", "per-suite/end snapshots", "explicit input hash",
                                  "no output self-hashing", "no-clobber", "old evidence preserved",
                                  "skip/xfail marker parser", "zero-skip metadata", "output prefix refusal",
                                  "output/input ancestor overlap refusal", "continue after test failure",
                                  "stop and NOT_RUN after observed source/policy drift"]}, indent=2) + "\n").encode())
        print(json.dumps({"selftest": "passed", "controls": len(outcomes), "directory": str(out)}))
    finally:
        os.chdir(real_cwd)


if __name__ == "__main__":
    main()
