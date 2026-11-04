#!/usr/bin/env python3
"""Independently validate and build the three historical legacy pipelines.

All generated files and any replacement assembly are confined to temporary
copies.  This is offline regression evidence, not a Max/runtime acceptance.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PROJECTS = {
    "examples": ROOT / "examples",
    "stepped-tower": ROOT / "specs/fixtures/stepped-tower",
    "form-precision": ROOT / "specs/fixtures/form-precision/specs/pipeline",
}
RELEVANT = ("place_components.py", "validate_specs.py", "scene_units.py",
            "curve_gen.py", "wall_cell_coverage.py")
BASELINE = "6c0f27b"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(directory: Path) -> dict[str, str]:
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in directory.rglob("*") if p.is_file()}


class ThreeLegacyProjects(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_hashes = {n: digest(SCRIPTS / n) for n in RELEVANT}
        cls.fixture_hashes = {name: tree_hashes(path) for name, path in PROJECTS.items()}
        print("source hashes: " + ", ".join(f"{n}={h[:16]}" for n, h in cls.source_hashes.items()),
              file=sys.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        actual = {n: digest(SCRIPTS / n) for n in RELEVANT}
        if actual != cls.source_hashes:
            raise AssertionError("source changed during run; repeat on a settled tree")
        actual_fixtures = {name: tree_hashes(path) for name, path in PROJECTS.items()}
        if actual_fixtures != cls.fixture_hashes:
            raise AssertionError("a source fixture changed during the offline tests")

    def setUp(self) -> None:
        parent = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        owner = tempfile.TemporaryDirectory(prefix="phase16-three-legacy-",
                                            dir=parent if os.name == "nt" and parent.is_dir() else None)
        self.addCleanup(owner.cleanup)
        self.temp = Path(owner.name)

    def command(self, script: Path, *args: object) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([sys.executable, "-B", str(script), *(str(x) for x in args)],
                                cwd=self.temp, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                                                        PYTHONIOENCODING="utf-8"),
                                text=True, encoding="utf-8", errors="replace",
                                capture_output=True, timeout=120, check=False)
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        return result

    def validate(self, pipeline: Path, *flags: str) -> dict:
        result = self.command(SCRIPTS / "validate_specs.py", "--dir", pipeline, "--json", *flags)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout[:3000])
        report = json.loads(result.stdout)
        self.assertEqual(report["exit_code"], result.returncode)
        self.assertEqual(report["summary"]["FAIL"], 0)
        self.assertEqual(report["summary"]["WARN"], 0)
        for rule in ("G-76", "G-77", "G-82", "G-83"):
            rows = [row for row in report["findings"] if row["rule"] == rule]
            self.assertTrue(any(row["severity"] == "PASS" for row in rows), (rule, rows))
            self.assertFalse(any(row["severity"] in ("FAIL", "WARN") for row in rows), (rule, rows))
        self.assertTrue(any(row["rule"] == "G-81" and row["severity"] == "SKIP"
                            for row in report["findings"]))
        return report

    def test_each_project_lint_strict_build_and_emitter(self) -> None:
        for name, source in PROJECTS.items():
            with self.subTest(project=name):
                work = self.temp / name
                pipeline = work / "pipeline"
                shutil.copytree(source, pipeline)
                self.assertFalse((pipeline / "walls.json").exists())
                self.assertNotIn("wall_technique", json.loads((pipeline / "assembly.json").read_text("utf-8")))
                for flags in ((), ("--warnings-as-errors",), ("--build",)):
                    with self.subTest(project=name, validation=flags or ("lint",)):
                        report = self.validate(pipeline, *flags)
                        print(f"{name} {flags or ('lint',)} summary={report['summary']}", file=sys.stderr)
                        if not flags:
                            for row in report["findings"]:
                                if row["severity"] == "SKIP":
                                    print(f"  SKIP {row['rule']} {row['location']}: "
                                          f"{row['detail'][:120]}", file=sys.stderr)
                for suffix, flags in (("normal", ()), ("build", ("--build",))):
                    with self.subTest(project=name, emitter=suffix):
                        out = work / ("output-" + suffix)
                        result = self.command(SCRIPTS / "place_components.py", "--in", pipeline,
                                              "--out", out, "--json", *flags)
                        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                        for filename in ("assembly.json", "assembly.ms"):
                            self.assertTrue((out / filename).is_file(), filename)
                for filename in ("assembly.json", "assembly.ms"):
                    self.assertEqual((work / "output-normal" / filename).read_bytes(),
                                     (work / "output-build" / filename).read_bytes())
                # Only a temp copy is modified; lint the actually generated pair.
                shutil.copy2(work / "output-build" / "assembly.json", pipeline / "assembly.json")
                shutil.copy2(work / "output-build" / "assembly.ms", pipeline / "assembly.ms")
                self.validate(pipeline, "--build")

    def test_each_emitter_matches_pre_p2_baseline(self) -> None:
        old = self.temp / "old"
        old.mkdir()
        for filename in ("place_components.py", "scene_units.py"):
            result = subprocess.run(["git", "show", f"{BASELINE}:scripts/{filename}"], cwd=ROOT,
                                    capture_output=True, timeout=30, check=False)
            if result.returncode:
                self.skipTest(f"git baseline unavailable: {result.stderr.decode(errors='replace')}")
            (old / filename).write_bytes(result.stdout)
        for name, source in PROJECTS.items():
            with self.subTest(project=name):
                work = self.temp / name
                pipeline = work / "pipeline"
                shutil.copytree(source, pipeline)
                outputs = []
                for label, script in (("old", old / "place_components.py"),
                                      ("current", SCRIPTS / "place_components.py")):
                    out = work / ("output-" + label)
                    result = self.command(script, "--in", pipeline, "--out", out, "--json")
                    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                    outputs.append(out)
                for filename in ("assembly.json", "assembly.ms"):
                    self.assertEqual((outputs[0] / filename).read_bytes(),
                                     (outputs[1] / filename).read_bytes(), (name, filename))


if __name__ == "__main__":
    unittest.main(verbosity=2)
