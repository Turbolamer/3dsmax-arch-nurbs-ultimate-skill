#!/usr/bin/env python3
"""Independent existing-artifact refusal regression for the actual P3 CLI.

Run: python -B Audit/test_phase16_p3_existing_output_review.py -v
Add --all-boundaries for the optional project/parent/pipeline 21-CLI matrix.
Uses frozen, unmodified copies of actual scripts and the authentic F01 INPUTS.
No fabricated produced fixture, source repair, Max, installer or preexisting edit.
Late injection calls the real script generator first, then adds only owned files.
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


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "Audit/phase16-p3-f01-input-2026-11-02e"
CONTRACT = ROOT / "Audit/_phase16-p3-contract-2026-11-02e.md"
LAYOUTS = ("project",)  # Quick default: seven actual CLI calls.
SENTINEL = b"INDEPENDENT EXISTING-OUTPUT REVIEW: USER BYTES\x00\xff\r\n"
PAYLOADS = {
    "json_alone": {"wall_surface.json": SENTINEL + b"{ invalid JSON\n"},
    "ms_alone": {"wall_surface.ms": SENTINEL + b"resetMaxFile #noPrompt\n"},
    "contradictory_pair": {
        "wall_surface.json": b'{"project":"FOREIGN","route":"legacy_cells_v1","schema_version":"bogus"}\n',
        "wall_surface.ms": SENTINEL + b"-- FOREIGN CONTRADICTORY SCRIPT; NEVER EXECUTED\n",
    },
}
LATE_MARKER = "INDEPENDENT_AFTER_REAL_GENERATE:"
LATE_RUNNER = r'''
import hashlib, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import build_wall_surface as builder
import wall_surface_runtime as runtime
real_generate = runtime.generate_script
artifact_dir = pathlib.Path(sys.argv[2])
payloads = json.loads(sys.argv[3])
calls = 0
def generate_then_add(*args, **kwargs):
    global calls
    result = real_generate(*args, **kwargs)
    calls += 1
    if calls != 1:
        raise RuntimeError("independent late injection requires exactly one real generation")
    raw = result.encode("utf-8") if isinstance(result, str) else result
    if not raw or b"polyop.createPolygon" not in raw:
        raise RuntimeError("actual geometry script generation was not reached")
    print("INDEPENDENT_AFTER_REAL_GENERATE:" + hashlib.sha256(raw).hexdigest(), file=sys.stderr)
    for name, encoded in payloads.items():
        with (artifact_dir / name).open("xb") as stream:
            stream.write(bytes.fromhex(encoded))
    return result
runtime.generate_script = generate_then_add
raise SystemExit(builder.main(sys.argv[4:]))
'''


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def files_below(directory: Path) -> dict[str, bytes]:
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


class ExistingOutputReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.name != "nt":
            raise RuntimeError("NOT RUN: requires the real Windows no-replace publisher")
        approved = Path(os.environ["LOCALAPPDATA"]) / "Temp/opencode"
        if not approved.is_dir():
            raise RuntimeError("NOT RUN: approved temporary directory unavailable")
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        required = {"build_wall_surface.py", "wall_surface_inputs.py",
                    "wall_surface_runtime.py", "wall_surface_publish.py"}
        if not required.issubset({p.name for p in scripts}):
            raise RuntimeError("NOT RUN: actual P3 source modules missing")
        fixture_paths = sorted((FIXTURE / "project").glob("*.json"))
        if not {"walls.json", "dimensions.json"}.issubset({p.name for p in fixture_paths}):
            raise RuntimeError("NOT RUN: authentic F01 input project missing")
        authority_path = FIXTURE / "direction-authority.json"
        cls.authority_raw = authority_path.read_bytes()
        cls.authority = json.loads(cls.authority_raw)
        source = Path(cls.authority["source_file"])
        if not source.is_absolute():
            source = ROOT / source  # Explicit root-CWD convention of authentic seed.
        cls.authority_source = source.read_bytes()
        if digest(cls.authority_source) != cls.authority["source_sha256"]:
            raise RuntimeError("NOT RUN: authentic analytical source lock is stale")
        captured = {p: p.read_bytes() for p in (*scripts, CONTRACT, *fixture_paths, authority_path, source)}
        cls.before = {str(p): digest(raw) for p, raw in captured.items()}
        cls.captured_paths = tuple(captured)
        print("EXISTING_OUTPUT_REVIEW_SOURCE " + json.dumps(cls.before, sort_keys=True), flush=True)
        owner = tempfile.TemporaryDirectory(prefix="p3-existing-output-review-", dir=approved)
        cls.addClassCleanup(owner.cleanup)  # Only this call's new disposable tree.
        cls.temp = Path(owner.name)
        cls.source = cls.temp / "frozen/scripts"
        cls.source.mkdir(parents=True)
        for p in scripts:
            (cls.source / p.name).write_bytes(captured[p])
        contract_copy = cls.temp / "frozen/Audit" / CONTRACT.name
        contract_copy.parent.mkdir()
        contract_copy.write_bytes(captured[CONTRACT])
        cls.fixture_bytes = {p.name: captured[p] for p in fixture_paths}

    @classmethod
    def tearDownClass(cls) -> None:
        after = {str(p): digest(p.read_bytes()) for p in cls.captured_paths}
        drift = [p for p in cls.before if cls.before[p] != after[p]]
        print("EXISTING_OUTPUT_REVIEW_DRIFT " + json.dumps(drift), flush=True)
        if drift:
            raise AssertionError("source/input drift during frozen-copy review; result is provisional")

    def request(self, label: str, layout: str) -> tuple[Path, Path, Path, Path, Path]:
        home = self.temp / (label + "-" + layout)
        home.mkdir()
        boundary = home / "project"
        project = boundary / "pipeline" if layout == "pipeline_parent" else boundary
        project.mkdir(parents=True)
        for name, raw in self.fixture_bytes.items():
            (project / name).write_bytes(raw)
        artifact_dir = boundary if layout == "pipeline_parent" else project
        if layout == "pipeline_child":
            artifact_dir = project / "pipeline"
            artifact_dir.mkdir()
        (boundary / "unrelated-sentinel.bin").write_bytes(SENTINEL)
        source = home / "analytical-source.md"
        source.write_bytes(self.authority_source)
        authority = dict(self.authority)
        authority["source_file"] = str(source)  # Same authentic source bytes, explicit private location.
        authority_path = home / "authority.json"
        authority_path.write_bytes((json.dumps(authority, sort_keys=True) + "\n").encode("utf-8"))
        return project, artifact_dir, authority_path, home / "new-run", boundary

    def cli(self, project: Path, artifact_dir: Path, authority: Path, out: Path,
            late: dict[str, bytes] | None = None) -> subprocess.CompletedProcess[str]:
        args = ["--in", str(project), "--out", str(out), "--namespace", "ExistingOutputReview",
                "--system-type", "millimeters", "--system-scale", "1",
                "--direction-authority", str(authority)]
        if late is None:
            command = [sys.executable, "-B", str(self.source / "build_wall_surface.py"), *args]
        else:
            command = [sys.executable, "-B", "-c", LATE_RUNNER, str(self.source), str(artifact_dir),
                       json.dumps({name: raw.hex() for name, raw in late.items()}), *args]
        return subprocess.run(command, cwd=out.parent, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=8,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))

    def test_clean_positive_actual_cli_each_boundary_and_late_hook(self) -> None:
        for layout in LAYOUTS:
            with self.subTest(layout=layout):
                project, artifacts, authority, out, boundary = self.request("positive", layout)
                before = files_below(boundary)
                result = self.cli(project, artifacts, authority, out, late={})
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(LATE_MARKER, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual({p.name for p in out.iterdir()}, {"wall_surface.json", "wall_surface.ms"})
                manifest = json.loads((out / "wall_surface.json").read_bytes())
                script = (out / "wall_surface.ms").read_bytes()
                self.assertEqual(manifest["status"], "produced_offline_unverified")
                self.assertEqual(manifest["script"]["sha256"], digest(script))
                self.assertIn(b"polyop.createPolygon", script)
                self.assertEqual(manifest["predictions"]["values"]["volume_cm3"], 2610000)
                self.assertEqual(before, files_below(boundary))
                self.assertFalse(list(out.parent.glob(".wall-surface-stage-*")))

    def refusal_cases(self, case: str, *, late: bool) -> None:
        payloads = PAYLOADS[case]
        for layout in LAYOUTS:
            with self.subTest(layout=layout):
                label = ("late-" if late else "initial-") + case
                project, artifacts, authority, out, boundary = self.request(label, layout)
                expected = files_below(boundary)
                for name, raw in payloads.items():
                    key = (artifacts / name).relative_to(boundary).as_posix()
                    expected[key] = raw
                    if not late:
                        (artifacts / name).write_bytes(raw)
                result = self.cli(project, artifacts, authority, out, late=payloads if late else None)
                if late:
                    self.assertIn(LATE_MARKER, result.stderr, "must reach actual script before addition")
                # Preserve sentinel/injected bytes even if the source is currently red.
                self.assertEqual(expected, files_below(boundary), "refusal changed old/injected bytes")
                self.assertNotIn("Traceback", result.stderr, "unhandled exception is not clean refusal")
                self.assertEqual(result.returncode, 1, "existing artifact accepted: " + result.stdout + result.stderr)
                self.assertIn("REFUSED:", result.stderr)
                self.assertRegex(result.stderr, r"(?i)(wall_surface|wall.surface|artifact|preexisting|existing)")
                self.assertFalse(out.exists(), "refusal published a partial or complete new pair")
                self.assertFalse(list(out.parent.glob(".wall-surface-stage-*")), "recoverable refusal leaked stage")

    def test_initial_json_alone(self) -> None:
        self.refusal_cases("json_alone", late=False)

    def test_initial_ms_alone(self) -> None:
        self.refusal_cases("ms_alone", late=False)

    def test_initial_contradictory_pair(self) -> None:
        self.refusal_cases("contradictory_pair", late=False)

    def test_late_json_alone_after_real_generation(self) -> None:
        self.refusal_cases("json_alone", late=True)

    def test_late_ms_alone_after_real_generation(self) -> None:
        self.refusal_cases("ms_alone", late=True)

    def test_late_contradictory_pair_after_real_generation(self) -> None:
        self.refusal_cases("contradictory_pair", late=True)


if __name__ == "__main__":
    if "--all-boundaries" in sys.argv:
        sys.argv.remove("--all-boundaries")
        LAYOUTS = ("project", "pipeline_parent", "pipeline_child")
    unittest.main(verbosity=2)
