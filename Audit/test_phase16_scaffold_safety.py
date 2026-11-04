#!/usr/bin/env python3
"""Temp-only regressions for bounded P2 initializer safety, not P2 acceptance.

Run: python -B Audit/test_phase16_scaffold_safety.py -v
Freezes initializer and validator + imports, verifies no source drift. No Max,
installer, real project mutation or manufactured production output is involved.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
WALL_FIXTURE = ROOT / "specs" / "fixtures" / "poly-shell-input" / "walls.json"
SOURCES = (ROOT / "scripts" / "init_project.py", ROOT / "scripts" / "validate_specs.py",
           ROOT / "scripts" / "curve_gen.py", ROOT / "scripts" / "wall_cell_coverage.py")
SEED_FILES = ("dimensions.json", "assumptions.json", "conflicts_resolved.json", "massing.json",
              "nurbs.json", "facade_grids.json", "components_registry.json", "assembly.json")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, doc) -> None:
    path.write_bytes((json.dumps(doc, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))


def tree(root: Path) -> dict[str, tuple[str, bytes]]:
    if not root.exists():
        return {}
    result = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[name] = ("symlink", os.fsencode(os.readlink(path)))
        elif path.is_file():
            result[name] = ("file", path.read_bytes())
        elif path.is_dir():
            result[name] = ("directory", b"")
        else:
            raise AssertionError(f"unexpected entry {path}")
    return result


class ScaffoldSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        approved = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "opencode"
        parent = str(approved) if os.name == "nt" and approved.is_dir() else None
        cls.owner = tempfile.TemporaryDirectory(prefix="phase16-scaffold-safety-", dir=parent)
        cls.addClassCleanup(cls.owner.cleanup)
        cls.root = Path(cls.owner.name)
        cls.scripts = cls.root / "frozen-scripts"
        cls.scripts.mkdir()
        files = (*SOURCES, WALL_FIXTURE, *sorted(p for p in EXAMPLES.rglob("*") if p.is_file()))
        cls.snapshot = {path: path.read_bytes() for path in files}
        for path in SOURCES:
            ast.parse(cls.snapshot[path].decode("utf-8"), filename=str(path))
            (cls.scripts / path.name).write_bytes(cls.snapshot[path])
        cls.initializer = cls.scripts / "init_project.py"
        cls.validator = cls.scripts / "validate_specs.py"
        print("\nFrozen source SHA-256: " + ", ".join(
            f"{p.name}={digest(cls.snapshot[p])}" for p in SOURCES), file=sys.stderr, flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        drift = [str(p.relative_to(ROOT)) for p, data in cls.snapshot.items()
                 if not p.is_file() or p.read_bytes() != data]
        if drift:
            raise AssertionError(f"source or fixture changed during test; repeat on a stable tree: {drift}")

    def setUp(self) -> None:
        self.owner = tempfile.TemporaryDirectory(prefix="case-", dir=self.root)
        self.addCleanup(self.owner.cleanup)
        self.temp = Path(self.owner.name)
        self.n = 0

    def cli(self, project: str, *args: object) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        env.pop("PYTHONPATH", None)
        return subprocess.run([sys.executable, "-B", str(self.initializer), "--project", project,
                               "--dir", str(self.temp), *map(str, args)], cwd=self.temp,
                              env=env, text=True, encoding="utf-8", errors="replace",
                              capture_output=True, timeout=60, check=False)

    def make_seed(self, *, explicit: bool = True) -> Path:
        self.n += 1
        seed = self.temp / f"seed-{self.n}"
        seed.mkdir()
        for path, data in self.snapshot.items():
            if path.is_relative_to(EXAMPLES):
                target = seed / path.relative_to(EXAMPLES)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        if explicit:
            (seed / "walls.json").write_bytes(self.snapshot[WALL_FIXTURE])
            assembly = read_json(seed / "assembly.json")
            assembly["status"] = "draft"
            assembly["source"]["reference"] = "components_registry.json; synthetic empty placeholder only"
            for key in ("origin_inputs", "placements", "scatter"):
                assembly[key] = []
            for key in ("origins", "defaults", "layer_map"):
                assembly[key] = {}
            assembly.pop("wall_cells")
            assembly.pop("opening_cuts")
            assembly["wall_technique"] = "poly_surface_shell_v1"
            assembly["wall_ref"] = "wall_surface.json"
            write_json(seed / "assembly.json", assembly)
        return seed

    def create_fresh(self, name: str) -> Path:
        result = self.cli(name)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.temp / name

    def seed_control(self, seed: Path, name: str) -> Path:
        result = self.cli(name, "--from", seed)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.temp / name

    def assert_refused_unchanged(self, result, root: Path, before, message: str) -> None:
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(message.lower(), result.stderr.lower())
        self.assertEqual(tree(root), before)

    def validator_numeric(self, token: str) -> bool:
        """Observe validator parser policy separately from stricter init policy."""
        code = ("import sys, validate_specs as v\n"
                "try: v.strict_json_loads('{\"value\":' + sys.argv[1] + '}')\n"
                "except (ValueError, OverflowError): sys.exit(1)\n")
        # The source is static and the token is an argv value, never interpolated.
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONPATH", None)
        result = subprocess.run([sys.executable, "-B", "-c", code, token], cwd=self.scripts,
                                env=env, capture_output=True, text=True, timeout=60, check=False)
        if result.returncode not in (0, 1) or "Traceback" in result.stderr:
            self.fail(f"frozen validator comparator crashed: {result.stderr}")
        return result.returncode == 0

    def test_explicit_seed_same_project_preserves_every_source_object(self) -> None:
        seed = self.make_seed()
        for i, filename in enumerate((*SEED_FILES, "walls.json")):
            doc = read_json(seed / filename)
            doc["source"]["reference"] = f"test-only original citation {i} for {filename}"
            write_json(seed / filename, doc)
        out = self.seed_control(seed, "same-source") / "specs" / "pipeline"
        for filename in (*SEED_FILES, "walls.json"):
            with self.subTest(filename=filename):
                original, rewritten = read_json(seed / filename), read_json(out / filename)
                self.assertEqual(original["source"], rewritten["source"])
                self.assertEqual(rewritten["project"], "same-source")
        self.assertFalse((out / "wall_surface.json").exists())
        self.assertEqual(read_json(out / "assembly.json")["status"], "draft")

    def test_each_source_identity_mismatch_refused_without_any_output(self) -> None:
        for i, filename in enumerate((*SEED_FILES, "walls.json")):
            with self.subTest(filename=filename):
                seed = self.make_seed()
                self.seed_control(seed, f"identity-control-{i}")
                doc = read_json(seed / filename)
                doc["project"] = "other-project"
                write_json(seed / filename, doc)
                target = self.temp / f"identity-bad-{i}"
                result = self.cli(target.name, "--from", seed)
                self.assert_refused_unchanged(result, target, {}, "project identities differ")
                self.assertFalse(target.exists())

    def test_missing_invalid_or_duplicate_project_refused(self) -> None:
        for index, kind in enumerate(("missing", "null", "blank", "invalid", "duplicate")):
            with self.subTest(kind=kind):
                seed = self.make_seed()
                self.seed_control(seed, f"valid-{index}")
                path = seed / "nurbs.json"
                doc = read_json(path)
                if kind == "missing":
                    del doc["project"]
                elif kind == "null":
                    doc["project"] = None
                elif kind == "blank":
                    doc["project"] = ""
                elif kind == "invalid":
                    doc["project"] = "UPPER CASE"
                if kind != "duplicate":
                    write_json(path, doc)
                else:
                    text = path.read_text(encoding="utf-8")
                    needle = '"project": "pavilion-01"'
                    self.assertEqual(text.count(needle), 1)
                    path.write_bytes(text.replace(needle, '"project": "other", ' + needle, 1).encode("utf-8"))
                target = self.temp / f"invalid-project-{index}"
                result = self.cli(target.name, "--from", seed)
                self.assert_refused_unchanged(result, target, {}, "duplicate" if kind == "duplicate" else "project identity")
                self.assertFalse(target.exists())

    def test_mismatch_with_force_preserves_existing_project_and_sentinels(self) -> None:
        seed = self.make_seed()
        project = self.seed_control(seed, "protected")
        sentinel = project / "notes.txt"
        sentinel.write_bytes(b"USER DATA - KEEP\n")
        before = tree(project)
        doc = read_json(seed / "walls.json")
        doc["project"] = "other-project"
        write_json(seed / "walls.json", doc)
        self.assert_refused_unchanged(self.cli("protected", "--from", seed, "--force"),
                                     project, before, "project identities differ")

    def test_legacy_no_selector_seed_unchanged(self) -> None:
        seed = self.make_seed(explicit=False)
        project = self.seed_control(seed, "legacy-control")
        out = project / "specs" / "pipeline"
        original, rewritten = read_json(seed / "assembly.json"), read_json(out / "assembly.json")
        self.assertFalse((out / "walls.json").exists())
        self.assertNotIn("wall_technique", rewritten)
        self.assertNotIn("wall_ref", rewritten)
        for key in ("placements", "opening_cuts", "wall_cells", "scatter", "origins", "origin_inputs"):
            self.assertEqual(original[key], rewritten[key], key)
        self.assertIn("worked example pavilion-01", read_json(out / "dimensions.json")["source"]["reference"])
        self.assertNotIn("unmodified_wall_scaffold_sha256", read_json(project / "project.json"))

    def test_explicit_seed_numeric_policy_and_documented_validator_difference(self) -> None:
        samples = {
            # (initializer acceptance, validator parser acceptance). A parser
            # acceptance is not geometry or G-82 range acceptance.
            "0.001": (True, True), "1e-3": (True, True), "0.1000": (True, True),
            "5e-324": (True, True), "9007199254740991": (True, True),
            "10000000000000001.9": (False, False), "1e-400": (False, False),
            "1e999": (False, False), "9007199254740992": (False, False),
            "9007199254740992.0": (False, True), "12345678901234567": (False, False),
            "1e20": (False, True),
        }
        for i, (token, (allowed, validator_allowed)) in enumerate(samples.items()):
            with self.subTest(token=token):
                self.assertEqual(self.validator_numeric(token), validator_allowed, token)
                seed = self.make_seed()
                self.seed_control(seed, f"numeric-control-{i}")
                # Inject into walls or a transitive seed. Source bytes are never
                # parsed and rewritten by this test after the token substitution.
                filename = "walls.json" if i % 2 else "dimensions.json"
                path = seed / filename
                doc = read_json(path)
                doc["source"]["reference"] = "numeric token control"
                doc["synthetic_numeric_probe"] = 123456789
                write_json(path, doc)
                text = path.read_text(encoding="utf-8")
                anchor = '"synthetic_numeric_probe": 123456789'
                self.assertEqual(text.count(anchor), 1)
                # walls has a closed schema, so put its probe in an existing
                # numerical field instead of inventing a top-level key.
                if filename == "walls.json":
                    del doc["synthetic_numeric_probe"]
                    write_json(path, doc)
                    text = path.read_text(encoding="utf-8")
                    anchor = '"numeric_epsilon_cm": 0.001'
                    self.assertEqual(text.count(anchor), 1)
                    replacement = f'"numeric_epsilon_cm": {token}'
                else:
                    replacement = f'"synthetic_numeric_probe": {token}'
                path.write_bytes(text.replace(anchor, replacement, 1).encode("utf-8"))
                target = self.temp / f"numeric-{i}"
                result = self.cli(target.name, "--from", seed)
                if allowed:
                    self.assertEqual(result.returncode, 0, result.stderr)
                else:
                    self.assert_refused_unchanged(result, target, {}, "json")
                    self.assertFalse(target.exists())

    def test_lossy_numeric_token_in_each_seed_is_refused_before_write(self) -> None:
        self.assertFalse(self.validator_numeric("1e-400"))
        for index, filename in enumerate((*SEED_FILES, "walls.json")):
            with self.subTest(filename=filename):
                seed = self.make_seed()
                self.seed_control(seed, f"all-input-control-{index}")
                path = seed / filename
                doc = read_json(path)
                doc["numeric_probe_for_test"] = 123456789
                write_json(path, doc)
                text = path.read_text(encoding="utf-8")
                anchor = '"numeric_probe_for_test": 123456789'
                self.assertEqual(text.count(anchor), 1)
                path.write_bytes(text.replace(anchor, '"numeric_probe_for_test": 1e-400', 1).encode("utf-8"))
                target = self.temp / f"all-input-bad-{index}"
                result = self.cli(target.name, "--from", seed)
                self.assert_refused_unchanged(result, target, {}, "loses decimal precision")
                self.assertFalse(target.exists())

    def test_unchanged_wall_scaffold_force_is_allowed_but_no_force_is_refused(self) -> None:
        project = self.create_fresh("fresh")
        before = tree(project)
        self.assert_refused_unchanged(self.cli("fresh"), project, before, "refusing to overwrite")
        self.assertEqual(self.cli("fresh", "--force").returncode, 0)
        walls = read_json(project / "specs" / "pipeline" / "walls.json")
        self.assertEqual((walls["status"], walls["wall_runs"]), ("draft", []))
        self.assertFalse((project / "specs" / "pipeline" / "wall_surface.ms").exists())

    def test_force_refuses_changed_or_unverifiable_walls(self) -> None:
        for mode in ("locked", "edited-draft", "unrecorded", "forged-hash", "missing-hash"):
            with self.subTest(mode=mode):
                project = self.create_fresh(mode)
                wall_path = project / "specs" / "pipeline" / "walls.json"
                manifest_path = project / "project.json"
                doc, manifest = read_json(wall_path), read_json(manifest_path)
                if mode == "locked":
                    doc["status"] = "locked"
                    doc["source"]["reference"] = "USER DATA - KEEP"
                    doc["wall_runs"] = [{"sentinel": "authored"}]
                    write_json(wall_path, doc)
                elif mode in ("edited-draft", "forged-hash"):
                    doc["source"]["reference"] = "USER DATA - KEEP"
                    write_json(wall_path, doc)
                elif mode == "unrecorded":
                    manifest["files"].remove("specs/pipeline/walls.json")
                    write_json(manifest_path, manifest)
                else:
                    del manifest["unmodified_wall_scaffold_sha256"]
                    write_json(manifest_path, manifest)
                if mode == "forged-hash":
                    manifest["unmodified_wall_scaffold_sha256"]["specs/pipeline/walls.json"] = digest(wall_path.read_bytes())
                    write_json(manifest_path, manifest)
                (project / "user-sentinel.txt").write_bytes(b"DO NOT TOUCH\n")
                before = tree(project)
                result = self.cli(mode, "--force")
                self.assert_refused_unchanged(result, project, before, "refusing to overwrite")

    def test_force_refuses_seeded_wall_even_if_its_manifest_lists_it(self) -> None:
        seed = self.make_seed()
        project = self.seed_control(seed, "seeded-wall")
        self.assertIn("specs/pipeline/walls.json", read_json(project / "project.json")["files"])
        before = tree(project)
        result = self.cli("seeded-wall", "--from", seed, "--force")
        self.assert_refused_unchanged(result, project, before, "unchanged recorded fresh draft")

    def test_force_never_switches_routes_or_removes_stale_artifacts(self) -> None:
        for index, artifact in enumerate((None, "specs/pipeline/assembly.ms", "specs/assembly.ms",
                                          "specs/pipeline/wall_surface.ms", "wall_surface.ms",
                                          "specs/pipeline/wall_surface.json")):
            with self.subTest(artifact=artifact):
                name = f"route-{index}"
                seed = self.make_seed(explicit=False)
                project = self.seed_control(seed, name)
                if artifact:
                    path = project / artifact
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"STALE USER ARTIFACT - KEEP\n")
                (project / "sentinel.txt").write_bytes(b"KEEP\n")
                before = tree(project)
                result = self.cli(name, "--force")
                self.assert_refused_unchanged(result, project, before,
                                              "wall manifest" if artifact and artifact.endswith(".json") else "route switch")

        poly = self.create_fresh("poly-to-legacy")
        marker = poly / "wall_surface.ms"
        marker.write_bytes(b"KEEP POLY SCRIPT\n")
        before = tree(poly)
        result = self.cli("poly-to-legacy", "--from", self.make_seed(explicit=False), "--force")
        self.assert_refused_unchanged(result, poly, before, "legacy seed")

    def test_existing_output_blocks_same_route_or_orphan_scaffold(self) -> None:
        for index, (existing_project, artifact) in enumerate((
            (True, "specs/pipeline/assembly.ms"),
            (True, "wall_surface.ms"),
            (False, "assembly.ms"),
            (False, "specs/pipeline/wall_surface.ms"),
            (False, "wall_surface.json"),
        )):
            with self.subTest(existing_project=existing_project, artifact=artifact):
                name = f"same-route-{index}"
                project = self.create_fresh(name) if existing_project else self.temp / name
                path = project / artifact
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"EXISTING USER OUTPUT - KEEP\n")
                before = tree(project)
                result = self.cli(name, "--force" if existing_project else "--dry-run")
                self.assert_refused_unchanged(result, project, before, "existing output")

    def test_partial_io_failure_reports_preserved_files_not_false_force_recovery(self) -> None:
        spec = importlib.util.spec_from_file_location("frozen_scaffold_safety", self.initializer)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        destination = self.temp / "partial" / "specs" / "pipeline" / "nurbs.json"
        real_replace = module.os.replace

        def fail_commit(source, target):
            if Path(target) == destination:
                raise PermissionError(13, "injected test failure", str(target))
            return real_replace(source, target)

        error = io.StringIO()
        with patch.object(module.os, "replace", fail_commit), redirect_stdout(io.StringIO()), redirect_stderr(error):
            status = module.main(["--project", "partial", "--dir", str(self.temp)])
        project = self.temp / "partial"
        self.assertEqual(status, 2)
        self.assertTrue((project / "specs" / "pipeline" / "dimensions.json").is_file())
        self.assertFalse((project / "project.json").exists())
        self.assertIn("preserve and inspect", error.getvalue().lower())
        self.assertIn("may be refused", error.getvalue().lower())
        self.assertNotIn("re-run with --force to continue", error.getvalue().lower())
        before = tree(project)
        self.assert_refused_unchanged(self.cli("partial", "--force"), project, before, "refusing to overwrite")


if __name__ == "__main__":
    unittest.main(verbosity=2)
